"""
Fact extraction utilities for verifying resume content against master resume.
Extracts verifiable facts (companies, dates, skills, etc.) for static validation.
"""

from typing import Dict, List, Set, Tuple
import re
from datetime import datetime


class FactExtractor:
    """Extracts verifiable facts from resume data structures."""
    
    def __init__(self):
        """Initialize fact extractor."""
        pass
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison (lowercase, strip whitespace)."""
        if not text:
            return ""
        return text.lower().strip()
    
    def normalize_company_name(self, company: str) -> str:
        """
        Normalize company name for matching.
        Handles variations like "UNC Chapel Hill" vs "UNC-Chapel Hill".
        """
        normalized = self.normalize_text(company)
        # Remove common suffixes/prefixes
        normalized = re.sub(r'\b(inc|llc|ltd|corp|corporation|company|co)\b\.?', '', normalized)
        # Normalize punctuation
        normalized = re.sub(r'[-_\s]+', ' ', normalized)
        return normalized.strip()
    
    def normalize_institution_name(self, institution: str) -> str:
        """
        Normalize institution name for matching.
        Handles variations like "UNC Chapel Hill" vs "University of North Carolina at Chapel Hill".
        """
        normalized = self.normalize_text(institution)
        # Common university abbreviations
        normalized = re.sub(r'\buniversity of north carolina at chapel hill\b', 'unc chapel hill', normalized)
        normalized = re.sub(r'\buniversity of north carolina\b', 'unc', normalized)
        # Remove common suffixes
        normalized = re.sub(r'\b(university|college|institute|school)\b', '', normalized)
        # Normalize punctuation
        normalized = re.sub(r'[-_\s]+', ' ', normalized)
        return normalized.strip()
    
    def parse_date(self, date_str: str) -> Tuple[int, int]:
        """
        Parse date string to (year, month) tuple.
        Handles formats: "2024-08", "2024-05", "Present", "present".
        Returns: (year, month) or (9999, 12) for "Present"
        """
        if not date_str:
            return (0, 0)
        
        date_str = date_str.strip()
        
        # Handle "Present" case
        if date_str.lower() == "present":
            return (9999, 12)
        
        # Try YYYY-MM format
        match = re.match(r'(\d{4})-(\d{2})', date_str)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            return (year, month)
        
        # Try YYYY format
        match = re.match(r'(\d{4})', date_str)
        if match:
            year = int(match.group(1))
            return (year, 1)  # Default to January
        
        return (0, 0)
    
    def extract_work_experience_facts(self, work_exp: List[Dict]) -> Dict[str, Set]:
        """
        Extract facts from work experience.
        Returns: {
            'companies': set of normalized company names,
            'job_titles': set of normalized job titles,
            'date_ranges': set of (company, start_date, end_date) tuples
        }
        """
        companies = set()
        job_titles = set()
        date_ranges = set()
        
        for job in work_exp:
            company = job.get('company', '')
            job_title = job.get('job_title', '')
            start_date = job.get('start_date', '')
            end_date = job.get('end_date', '')
            
            if company:
                companies.add(self.normalize_company_name(company))
            
            if job_title:
                job_titles.add(self.normalize_text(job_title))
            
            if company and start_date and end_date:
                date_ranges.add((
                    self.normalize_company_name(company),
                    start_date,
                    end_date
                ))
        
        return {
            'companies': companies,
            'job_titles': job_titles,
            'date_ranges': date_ranges
        }
    
    def extract_education_facts(self, education: List[Dict]) -> Dict[str, Set]:
        """
        Extract facts from education.
        Returns: {
            'institutions': set of normalized institution names,
            'degrees': set of normalized degree names,
            'graduation_dates': set of (institution, graduation_date) tuples
        }
        """
        institutions = set()
        degrees = set()
        graduation_dates = set()
        
        for edu in education:
            institution = edu.get('institution', '')
            degree = edu.get('degree', '')
            grad_date = edu.get('graduation_date', '')
            
            if institution:
                institutions.add(self.normalize_institution_name(institution))
            
            if degree:
                # Extract degree type (BS, MS, PhD, etc.)
                degree_normalized = self.normalize_text(degree)
                degrees.add(degree_normalized)
            
            if institution and grad_date:
                graduation_dates.add((
                    self.normalize_institution_name(institution),
                    grad_date
                ))
        
        return {
            'institutions': institutions,
            'degrees': degrees,
            'graduation_dates': graduation_dates
        }
    
    def extract_skills(self, skills: Dict[str, str]) -> Set[str]:
        """
        Extract individual skills from skills dictionary.
        Skills dict format: {"Category": "skill1, skill2, skill3"}
        Returns: set of normalized individual skills
        """
        all_skills = set()
        
        for category, skills_str in skills.items():
            if not skills_str:
                continue
            
            # Split by comma and normalize each skill
            skill_list = [s.strip() for s in skills_str.split(',')]
            for skill in skill_list:
                if skill:
                    all_skills.add(self.normalize_text(skill))
        
        return all_skills
    
    def extract_project_facts(self, projects: List[Dict]) -> Dict[str, Set]:
        """
        Extract facts from projects.
        Returns: {
            'project_names': set of normalized project names,
            'technologies': set of normalized technologies
        }
        """
        project_names = set()
        technologies = set()
        
        for project in projects:
            project_name = project.get('project_name', '')
            tech_list = project.get('technologies', [])
            
            if project_name:
                project_names.add(self.normalize_text(project_name))
            
            if tech_list:
                for tech in tech_list:
                    if tech:
                        technologies.add(self.normalize_text(tech))
        
        return {
            'project_names': project_names,
            'technologies': technologies
        }
    
    def extract_all_facts(self, resume: Dict) -> Dict[str, any]:
        """
        Extract all verifiable facts from a resume.
        Returns comprehensive fact dictionary for verification.
        """
        work_exp = resume.get('work_experience', [])
        education = resume.get('education', [])
        skills = resume.get('skills', {})
        projects = resume.get('projects', [])
        
        work_facts = self.extract_work_experience_facts(work_exp)
        edu_facts = self.extract_education_facts(education)
        skill_facts = self.extract_skills(skills)
        project_facts = self.extract_project_facts(projects)
        
        return {
            'companies': work_facts['companies'],
            'job_titles': work_facts['job_titles'],
            'date_ranges': work_facts['date_ranges'],
            'institutions': edu_facts['institutions'],
            'degrees': edu_facts['degrees'],
            'graduation_dates': edu_facts['graduation_dates'],
            'skills': skill_facts,
            'project_names': project_facts['project_names'],
            'technologies': project_facts['technologies']
        }
    
    def extract_facts_from_cover_letter(self, cover_letter_text: str) -> Dict[str, Set]:
        """
        Extract factual claims from cover letter text.
        This is a simple extraction - looks for company names, skills, etc.
        Returns: {
            'mentioned_companies': set of company-like terms,
            'mentioned_skills': set of skill-like terms
        }
        """
        # This is a basic implementation
        # In practice, you might want more sophisticated NLP
        
        text_lower = cover_letter_text.lower()
        
        # Extract potential company mentions (capitalized words/phrases)
        # This is simplified - you might want to use NER or more sophisticated matching
        
        return {
            'mentioned_companies': set(),  # Simplified for now
            'mentioned_skills': set()  # Simplified for now
        }
