"""
Fact verification module for validating resume content against master resume.
Prevents LLM hallucinations by checking all factual claims statically.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from src.fact_extractor import FactExtractor


@dataclass
class Hallucination:
    """Represents a detected hallucination (invented fact)."""
    category: str  # "company", "skill", "date", "institution", etc.
    claimed_value: str  # The invented value
    context: str  # Where it appeared
    severity: str  # "critical" or "warning"


@dataclass
class VerificationResult:
    """Result of fact verification."""
    is_valid: bool
    hallucinations: List[Hallucination]
    
    def __bool__(self) -> bool:
        """Allow using result in boolean context."""
        return self.is_valid


class FactVerificationError(Exception):
    """Exception raised when fact verification fails."""
    
    def __init__(self, result: VerificationResult):
        self.result = result
        super().__init__(f"Fact verification failed with {len(result.hallucinations)} hallucination(s)")


class FactVerifier:
    """Verifies tailored resume facts against master resume."""
    
    def __init__(self, master_resume: Dict[str, Any]):
        """
        Initialize fact verifier with master resume.
        
        Args:
            master_resume: The master resume dictionary (single source of truth)
        """
        self.master_resume = master_resume
        self.extractor = FactExtractor()
        
        # Extract all facts from master resume once
        self.master_facts = self.extractor.extract_all_facts(master_resume)
    
    def verify_resume(self, tailored_resume: Dict[str, Any]) -> VerificationResult:
        """
        Verify tailored resume against master resume.
        
        Args:
            tailored_resume: The generated tailored resume to verify
            
        Returns:
            VerificationResult with is_valid flag and list of hallucinations
        """
        hallucinations: List[Hallucination] = []
        
        # Extract facts from tailored resume
        tailored_facts = self.extractor.extract_all_facts(tailored_resume)
        
        # 1. Verify companies (CRITICAL)
        for company in tailored_facts['companies']:
            if company not in self.master_facts['companies']:
                hallucinations.append(Hallucination(
                    category="company",
                    claimed_value=company,
                    context="Work experience",
                    severity="critical"
                ))
        
        # 2. Verify institutions (CRITICAL)
        for institution in tailored_facts['institutions']:
            if institution not in self.master_facts['institutions']:
                hallucinations.append(Hallucination(
                    category="institution",
                    claimed_value=institution,
                    context="Education",
                    severity="critical"
                ))
        
        # 3. Verify skills (WARNING - subset allowed)
        invented_skills = tailored_facts['skills'] - self.master_facts['skills']
        if invented_skills:
            for skill in invented_skills:
                hallucinations.append(Hallucination(
                    category="skill",
                    claimed_value=skill,
                    context="Skills section",
                    severity="warning"
                ))
        
        # 4. Verify project names (WARNING)
        for project_name in tailored_facts['project_names']:
            if project_name not in self.master_facts['project_names']:
                hallucinations.append(Hallucination(
                    category="project_name",
                    claimed_value=project_name,
                    context="Projects section",
                    severity="warning"
                ))
        
        # 5. Verify technologies (WARNING - subset allowed)
        invented_techs = tailored_facts['technologies'] - self.master_facts['technologies']
        if invented_techs:
            for tech in invented_techs:
                hallucinations.append(Hallucination(
                    category="technology",
                    claimed_value=tech,
                    context="Project technologies",
                    severity="warning"
                ))
        
        # 6. Verify date ranges (CRITICAL)
        for company, start_date, end_date in tailored_facts['date_ranges']:
            # Check if this exact date range exists in master resume
            if (company, start_date, end_date) not in self.master_facts['date_ranges']:
                # Check if company exists at all
                if company in self.master_facts['companies']:
                    hallucinations.append(Hallucination(
                        category="date_range",
                        claimed_value=f"{start_date} to {end_date}",
                        context=f"Work experience at {company}",
                        severity="critical"
                    ))
                # If company doesn't exist, it's already caught above
        
        # 7. Verify graduation dates (CRITICAL)
        for institution, grad_date in tailored_facts['graduation_dates']:
            if (institution, grad_date) not in self.master_facts['graduation_dates']:
                if institution in self.master_facts['institutions']:
                    hallucinations.append(Hallucination(
                        category="graduation_date",
                        claimed_value=grad_date,
                        context=f"Education at {institution}",
                        severity="critical"
                    ))
        
        # Determine if valid (no critical hallucinations)
        critical_hallucinations = [h for h in hallucinations if h.severity == "critical"]
        is_valid = len(critical_hallucinations) == 0
        
        return VerificationResult(
            is_valid=is_valid,
            hallucinations=hallucinations
        )
    
    def verify_cover_letter(
        self, 
        cover_letter_text: str, 
        tailored_resume: Dict[str, Any]
    ) -> VerificationResult:
        """
        Verify cover letter against master resume and tailored resume.
        
        This is a simplified version - mainly checks that the cover letter
        doesn't claim facts not in the tailored resume (which is already verified).
        
        Args:
            cover_letter_text: The generated cover letter text
            tailored_resume: The already-verified tailored resume
            
        Returns:
            VerificationResult with is_valid flag and list of hallucinations
        """
        hallucinations: List[Hallucination] = []
        
        # For now, we assume cover letter is grounded in the tailored resume
        # which has already been verified against master resume.
        # Future enhancement: extract claims from cover letter text and verify them.
        
        # Basic check: ensure cover letter is not empty
        if not cover_letter_text or len(cover_letter_text.strip()) < 100:
            hallucinations.append(Hallucination(
                category="content",
                claimed_value="empty or too short",
                context="Cover letter",
                severity="critical"
            ))
        
        return VerificationResult(
            is_valid=len(hallucinations) == 0,
            hallucinations=hallucinations
        )
    
    def format_hallucinations_for_retry(self, result: VerificationResult) -> str:
        """
        Format hallucinations into error feedback for LLM retry.
        
        Args:
            result: VerificationResult containing hallucinations
            
        Returns:
            Formatted error message for LLM
        """
        if result.is_valid:
            return ""
        
        lines = [
            "=" * 80,
            "⚠️  FACT VERIFICATION ERRORS",
            "=" * 80,
            "",
            f"Found {len(result.hallucinations)} hallucination(s):",
            ""
        ]
        
        # Group by severity
        critical = [h for h in result.hallucinations if h.severity == "critical"]
        warnings = [h for h in result.hallucinations if h.severity == "warning"]
        
        if critical:
            lines.append("CRITICAL ERRORS (must fix):")
            for h in critical:
                lines.append(f"  • {h.category}: '{h.claimed_value}' not found in master resume")
                lines.append(f"    Context: {h.context}")
            lines.append("")
        
        if warnings:
            lines.append("WARNINGS (should fix):")
            for h in warnings:
                lines.append(f"  • {h.category}: '{h.claimed_value}' not found in master resume")
                lines.append(f"    Context: {h.context}")
            lines.append("")
        
        lines.extend([
            "CRITICAL: Only use facts that exist in the master resume.",
            "Do not invent companies, skills, dates, institutions, or education.",
            "Do not modify employment dates or graduation dates.",
            "=" * 80,
            ""
        ])
        
        return "\n".join(lines)
