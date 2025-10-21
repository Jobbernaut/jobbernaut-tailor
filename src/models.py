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
            if len(clean_bullet) > 110:
                raise ValueError(
                    f"Bullet point {i+1} exceeds 110 characters ({len(clean_bullet)} chars): {clean_bullet[:50]}..."
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
        if len(joined) > 95:
            raise ValueError(
                f"Technologies exceed 95 characters when joined ({len(joined)} chars): {joined}"
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
            if len(clean_bullet) > 110:
                raise ValueError(
                    f"Bullet point {i+1} exceeds 110 characters ({len(clean_bullet)} chars): {clean_bullet[:50]}..."
                )
            sanitized.append(clean_bullet)
        return sanitized


class TailoredResume(BaseModel):
    """Complete tailored resume model."""
    contact_info: ContactInfo
    professional_summaries: str = ""  # Should be empty string
    work_authorization: Optional[str] = None
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
            if len(clean_skills) > 95:
                raise ValueError(
                    f"Skills in category '{clean_category}' exceed 95 characters ({len(clean_skills)} chars): {clean_skills[:50]}..."
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
