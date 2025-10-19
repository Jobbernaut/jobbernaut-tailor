"""
Pydantic models for validating resume JSON structure.
Ensures type safety and correct field names before template rendering.
"""

from typing import List, Dict, Optional
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


class Education(BaseModel):
    """Education entry model."""
    institution: str
    degree: str
    start_date: str
    graduation_date: str  # CRITICAL: Must be 'graduation_date', not 'end_date'
    gpa: str = ""  # Optional, should be empty string as GPA is in degree field


class WorkExperience(BaseModel):
    """Work experience entry model."""
    job_title: str
    company: str
    start_date: str
    end_date: str
    location: Optional[str] = None
    bullet_points: List[str] = Field(..., min_length=4, max_length=4)
    
    @field_validator('bullet_points')
    @classmethod
    def validate_bullet_length(cls, v: List[str]) -> List[str]:
        """Ensure each bullet point is <= 110 characters."""
        for i, bullet in enumerate(v):
            if len(bullet) > 110:
                raise ValueError(
                    f"Bullet point {i+1} exceeds 110 characters ({len(bullet)} chars): {bullet[:50]}..."
                )
        return v


class Project(BaseModel):
    """Project entry model."""
    project_name: str
    technologies: List[str] = Field(default_factory=list)  # Array of technology strings
    project_url: str
    description: Optional[str] = None
    bullet_points: List[str] = Field(..., min_length=4, max_length=4)
    
    @field_validator('bullet_points')
    @classmethod
    def validate_bullet_length(cls, v: List[str]) -> List[str]:
        """Ensure each bullet point is <= 110 characters."""
        for i, bullet in enumerate(v):
            if len(bullet) > 110:
                raise ValueError(
                    f"Bullet point {i+1} exceeds 110 characters ({len(bullet)} chars): {bullet[:50]}..."
                )
        return v
    
    @field_validator('technologies')
    @classmethod
    def validate_technologies_length(cls, v: List[str]) -> List[str]:
        """Ensure technologies joined with ', ' is <= 90 characters."""
        joined = ", ".join(v)
        if len(joined) > 90:
            raise ValueError(
                f"Technologies exceed 90 characters when joined ({len(joined)} chars): {joined}"
            )
        return v


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
        """Ensure each skill category value is <= 90 characters."""
        for category, skills_str in v.items():
            if len(skills_str) > 90:
                raise ValueError(
                    f"Skills in category '{category}' exceed 90 characters ({len(skills_str)} chars): {skills_str[:50]}..."
                )
        return v
    
    @field_validator('professional_summaries')
    @classmethod
    def validate_empty_summary(cls, v: str) -> str:
        """Ensure professional_summaries is empty string."""
        if v and v.strip():
            raise ValueError("professional_summaries must be empty string to maximize content space")
        return ""
