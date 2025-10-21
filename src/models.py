"""
Pydantic models for validating resume JSON structure.
Ensures type safety and correct field names before template rendering.
"""

from typing import List, Dict, Optional
import re
from pydantic import BaseModel, Field, field_validator


class ContactInfo(BaseModel):
    """Contact information model."""
    first_name: str
    last_name: str
    phone: str
    email: str
    location: str
    linkedin_url: str
    github_url: str
    portfolio_url: str
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Remove ATS-incompatible characters from names."""
        if not v:
            return v
        # Remove illegal characters: <>[]{}\|~^
        illegal_chars = r'[<>\[\]{}\\|~^]'
        v = re.sub(illegal_chars, '', v)
        return v.strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        """
        Validate and format phone number for ATS compatibility.
        Accepts formats like: 919-672-2226, (919) 672-2226, 9196722226
        Returns format: (919) 672-2226 (ATS-preferred format)
        """
        if not v:
            return v
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, v))
        
        # Remove country code if present (assumes US +1)
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        
        # Validate 10-digit phone number
        if len(digits) != 10:
            raise ValueError(
                f"Phone number must be 10 digits (found {len(digits)}). "
                f"Format should be: (XXX) XXX-XXXX or XXX-XXX-XXXX"
            )
        
        # Format as (XXX) XXX-XXXX for ATS compatibility
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    @field_validator('location')
    @classmethod
    def sanitize_location(cls, v: str) -> str:
        """Remove ATS-incompatible characters from location."""
        if not v:
            return v
        illegal_chars = r'[<>\[\]{}\\|~^]'
        v = re.sub(illegal_chars, '', v)
        return v.strip()


class Education(BaseModel):
    """Education entry model."""
    institution: str
    degree: str
    start_date: str
    graduation_date: str  # CRITICAL: Must be 'graduation_date', not 'end_date'
    gpa: str = ""  # Optional, should be empty string as GPA is in degree field
    
    @field_validator('institution', 'degree')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Remove ATS-incompatible characters from text fields."""
        if not v:
            return v
        # Remove illegal characters: <>[]{}\|~^
        illegal_chars = r'[<>\[\]{}\\|~^]'
        v = re.sub(illegal_chars, '', v)
        return v.strip()


class WorkExperience(BaseModel):
    """Work experience entry model."""
    job_title: str
    company: str
    start_date: str
    end_date: str
    location: Optional[str] = None
    bullet_points: List[str] = Field(..., min_length=4, max_length=4)
    
    @field_validator('job_title', 'company')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Remove ATS-incompatible characters from text fields."""
        if not v:
            return v
        # Remove illegal characters: <>[]{}\|~^
        illegal_chars = r'[<>\[\]{}\\|~^]'
        v = re.sub(illegal_chars, '', v)
        return v.strip()
    
    @field_validator('location')
    @classmethod
    def sanitize_location(cls, v: Optional[str]) -> Optional[str]:
        """Remove ATS-incompatible characters from location."""
        if not v:
            return v
        illegal_chars = r'[<>\[\]{}\\|~^]'
        v = re.sub(illegal_chars, '', v)
        return v.strip()
    
    @field_validator('bullet_points')
    @classmethod
    def validate_bullet_length(cls, v: List[str]) -> List[str]:
        """Ensure each bullet point is <= 110 characters and sanitize ATS-incompatible characters."""
        sanitized = []
        # Remove illegal characters: <>[]{}\|~^
        illegal_chars = r'[<>\[\]{}\\|~^]'
        
        for i, bullet in enumerate(v):
            # Sanitize the bullet
            clean_bullet = re.sub(illegal_chars, '', bullet).strip()
            
            # Check length after sanitization
            if len(clean_bullet) > 115:
                raise ValueError(
                    f"Bullet point {i+1} exceeds 115 characters ({len(clean_bullet)} chars): {clean_bullet[:50]}..."
                )
            sanitized.append(clean_bullet)
        return sanitized


class Project(BaseModel):
    """Project entry model."""
    project_name: str
    technologies: List[str] = Field(default_factory=list)  # Array of technology strings
    project_url: str
    description: Optional[str] = None
    bullet_points: List[str] = Field(..., min_length=4, max_length=4)
    
    @field_validator('project_name')
    @classmethod
    def sanitize_project_name(cls, v: str) -> str:
        """Remove ATS-incompatible characters from project name."""
        if not v:
            return v
        # Remove illegal characters: <>[]{}\|~^
        illegal_chars = r'[<>\[\]{}\\|~^]'
        v = re.sub(illegal_chars, '', v)
        return v.strip()
    
    @field_validator('technologies')
    @classmethod
    def validate_technologies_length(cls, v: List[str]) -> List[str]:
        """Ensure technologies joined with ', ' is <= 95 characters and sanitize ATS-incompatible characters."""
        # Remove illegal characters from each technology
        illegal_chars = r'[<>\[\]{}\\|~^]'
        sanitized = [re.sub(illegal_chars, '', tech).strip() for tech in v]
        
        # Check length constraint
        joined = ", ".join(sanitized)
        if len(joined) > 100:
            raise ValueError(
                f"Technologies exceed 100 characters when joined ({len(joined)} chars): {joined}"
            )
        return sanitized
    
    @field_validator('bullet_points')
    @classmethod
    def validate_bullet_length(cls, v: List[str]) -> List[str]:
        """Ensure each bullet point is <= 110 characters and sanitize ATS-incompatible characters."""
        sanitized: List[str] = []
        # Remove illegal characters: <>[]{}\|~^
        illegal_chars = r'[<>\[\]{}\\|~^]'
        
        for i, bullet in enumerate(v):
            # Sanitize the bullet
            clean_bullet = re.sub(illegal_chars, '', bullet).strip()
            
            # Check length after sanitization
            if len(clean_bullet) > 115:
                raise ValueError(
                    f"Bullet point {i+1} exceeds 115 characters ({len(clean_bullet)} chars): {clean_bullet[:50]}..."
                )
            sanitized.append(clean_bullet)
        return sanitized


class TailoredResume(BaseModel):
    """Complete tailored resume model."""
    contact_info: ContactInfo
    professional_summaries: str = ""  # Should be empty string
    education: List[Education] = Field(..., min_length=1)
    skills: Dict[str, str] = Field(...)  # Category name -> comma-separated skills string
    work_experience: List[WorkExperience] = Field(..., min_length=3, max_length=3)
    projects: List[Project] = Field(..., min_length=3, max_length=3)
    
    @field_validator('skills')
    @classmethod
    def validate_skills_length(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Ensure each skill category value is <= 95 characters and sanitize ATS-incompatible characters."""
        # Remove illegal characters: <>[]{}\|~^
        illegal_chars = r'[<>\[\]{}\\|~^]'
        sanitized_skills: Dict[str, str] = {}
        
        for category, skills_str in v.items():
            # Sanitize category name
            clean_category = re.sub(illegal_chars, '', category).strip()
            
            # Sanitize skills string
            clean_skills = re.sub(illegal_chars, '', skills_str).strip()
            
            # Check length constraint
            if len(clean_skills) > 100:
                raise ValueError(
                    f"Skills in category '{clean_category}' exceed 100 characters ({len(clean_skills)} chars): {clean_skills[:50]}..."
                )
            
            sanitized_skills[clean_category] = clean_skills
        
        return sanitized_skills
    
    @field_validator('professional_summaries')
    @classmethod
    def validate_empty_summary(cls, v: str) -> str:
        """Ensure professional_summaries is empty string."""
        if v and v.strip():
            raise ValueError("professional_summaries must be empty string to maximize content space")
        return ""


class JobResonanceAnalysis(BaseModel):
    """
    Intelligence gathering model for deep job description analysis.
    Extracts emotional keywords, cultural values, and hidden requirements.
    """
    emotional_keywords: List[str] = Field(
        ..., 
        description="Emotionally charged words from JD (e.g., 'passionate', 'innovative', 'ownership')"
    )
    cultural_values: List[str] = Field(
        ..., 
        description="Company culture signals (e.g., 'collaborative', 'fast-paced', 'data-driven')"
    )
    hidden_requirements: List[str] = Field(
        ..., 
        description="Implicit requirements not in bullet points (e.g., 'startup mentality', 'ambiguity tolerance')"
    )
    power_verbs: List[str] = Field(
        ..., 
        description="Action verbs from JD to mirror in resume (e.g., 'architected', 'spearheaded', 'optimized')"
    )
    technical_keywords: List[str] = Field(
        ..., 
        description="Technical skills and tools mentioned in JD for ATS optimization"
    )
    
    @field_validator('emotional_keywords', 'cultural_values', 'hidden_requirements', 'power_verbs', 'technical_keywords')
    @classmethod
    def validate_non_empty_lists(cls, v: List[str]) -> List[str]:
        """Ensure all lists have at least one item."""
        if not v or len(v) == 0:
            raise ValueError("List must contain at least one item")
        return v


class CompanyResearch(BaseModel):
    """
    Company intelligence model for authentic connection building.
    Stores company mission, values, tech stack, and culture keywords.
    """
    company_name: str = Field(..., description="Company name from job posting")
    mission_statement: str = Field(
        ..., 
        description="Company mission or 'about us' summary (1-2 sentences)"
    )
    core_values: List[str] = Field(
        ..., 
        description="Company values (e.g., 'customer obsession', 'innovation', 'integrity')"
    )
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Known technologies used by company (optional)"
    )
    culture_keywords: List[str] = Field(
        default_factory=list,
        description="Culture descriptors from company website/reviews (optional)"
    )
    recent_news: str = Field(
        default="",
        description="Recent company news or achievements (optional, 1 sentence)"
    )
    
    @field_validator('core_values')
    @classmethod
    def validate_core_values(cls, v: List[str]) -> List[str]:
        """Ensure core values list has at least one item."""
        if not v or len(v) == 0:
            raise ValueError("core_values must contain at least one item")
        return v


class StorytellingArc(BaseModel):
    """
    Narrative structure model for cover letter storytelling.
    Creates emotional connection through structured story arc.
    """
    hook: str = Field(
        ..., 
        description="Opening sentence that creates emotional connection (1 sentence)"
    )
    bridge: str = Field(
        ..., 
        description="Transition from hook to candidate's story (1-2 sentences)"
    )
    proof_points: List[str] = Field(
        ..., 
        min_length=2,
        max_length=3,
        description="2-3 specific stories demonstrating fit (each 2-3 sentences)"
    )
    vision: str = Field(
        ..., 
        description="Forward-looking statement about impact at company (1-2 sentences)"
    )
    call_to_action: str = Field(
        ..., 
        description="Closing sentence inviting conversation (1 sentence)"
    )
    
    @field_validator('hook', 'bridge', 'vision', 'call_to_action')
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Ensure all string fields are non-empty."""
        if not v or not v.strip():
            raise ValueError("Field must be a non-empty string")
        return v.strip()
