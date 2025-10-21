"""
Template rendering module for generating LaTeX documents from JSON data using Jinja2.
"""

from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any, Union


class TemplateRenderer:
    """Handles rendering of Jinja2 templates for resume and cover letter generation."""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the template renderer.
        
        Args:
            templates_dir: Directory containing Jinja2 templates
        """
        self.templates_dir = templates_dir
        # Use custom delimiters to avoid conflicts with LaTeX syntax
        # Based on: https://13rac1.com/articles/2015/11/latex-templates-python-and-jinja2-generate-pdfs/
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            block_start_string='\\BLOCK{',
            block_end_string='}',
            variable_start_string='\\VAR{',
            variable_end_string='}',
            comment_start_string='\\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False  # Don't autoescape for LaTeX
        )
        
        # Register custom filters
        self.env.filters['latex_escape'] = self.latex_escape
        self.env.filters['format_date'] = self.format_date
        self.env.filters['format_phone'] = self.format_phone
    
    @staticmethod
    def latex_escape(text: Union[str, Any]) -> str:
        """
        Escape special LaTeX characters in text.
        
        Args:
            text: Input text to escape
            
        Returns:
            Text with LaTeX special characters escaped
        """
        if not isinstance(text, str):
            text = str(text)
        
        # IMPORTANT: Escape backslash FIRST to avoid double-escaping
        text = text.replace('\\', r'\textbackslash{}')
        
        # Then escape other special characters
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        
        # Apply replacements
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """
        Format date from YYYY-MM to 'MMM YYYY' format.
        Handles 'Present' and other special cases.
        
        Args:
            date_str: Date string in YYYY-MM format or special value like 'Present'
            
        Returns:
            Formatted date string
        """
        if not date_str:
            return ""
        
        # Handle special cases
        if date_str.lower() in ['present', 'current', 'now']:
            return 'Present'
        
        try:
            # Parse YYYY-MM format
            date_obj = datetime.strptime(date_str, '%Y-%m')
            # Format as 'MMM YYYY'
            return date_obj.strftime('%b %Y')
        except ValueError:
            # If parsing fails, return original string
            return date_str
    
    @staticmethod
    def format_phone(phone_str: str) -> str:
        """
        Format a phone number to ATS-compatible format: (XXX) XXX-XXXX
        
        Args:
            phone_str: Phone number string in any format (e.g., "+1 919-672-2226", "919-672-2226", "(919) 672-2226")
        
        Returns:
            Formatted phone number as (XXX) XXX-XXXX (e.g., "(919) 672-2226"). If input is not valid, returns the original string.
        
        Examples:
            >>> format_phone("+1 919-672-2226")
            '(919) 672-2226'
            >>> format_phone("919-672-2226")
            '(919) 672-2226'
            >>> format_phone("(919) 672-2226")
            '(919) 672-2226'
        """
        if not phone_str:
            return ""
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_str))
        
        # If it starts with 1 (country code), remove it
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        
        # Return ATS-compatible format: (XXX) XXX-XXXX
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        
        # If not 10 digits, return original
        return phone_str
    
    def render_resume(self, resume_data: Dict[str, Any]) -> str:
        """
        Render resume LaTeX from JSON data.
        
        Args:
            resume_data: Dictionary containing resume data with keys:
                - contact_info: dict with name, phone, email, linkedin, github
                - education: list of education entries
                - skills: dict with category names as keys
                - work_experience: list of work experience entries
                - projects: list of project entries
                
        Returns:
            Rendered LaTeX document as string
        """
        # Sort education by graduation_date (descending - most recent first)
        if 'education' in resume_data and len(resume_data['education']) > 1:
            resume_data['education'] = sorted(
                resume_data['education'],
                key=lambda x: x.get('graduation_date', ''),
                reverse=True
            )
        
        # Sort work experience by start_date (descending - most recent first)
        # Handle "Present" as a special case (treat as future date for sorting)
        if 'work_experience' in resume_data and len(resume_data['work_experience']) > 1:
            def get_sort_key(exp: Dict[str, Any]) -> str:
                start_date = exp.get('start_date', '')
                return "9999-99" if start_date.lower() == "present" else start_date
            
            resume_data['work_experience'] = sorted(
                resume_data['work_experience'],
                key=get_sort_key,
                reverse=True
            )
        
        template = self.env.get_template('resume.jinja2')
        return template.render(**resume_data)
    
    def render_cover_letter(self, contact_info: Dict[str, str], cover_letter_text: str) -> str:
        """
        Render cover letter LaTeX from contact info and cover letter text.
        
        Args:
            contact_info: Dictionary with name, phone, email, linkedin, github
            cover_letter_text: The main body text of the cover letter
            
        Returns:
            Rendered LaTeX document as string
        """
        template = self.env.get_template('cover_letter.jinja2')
        return template.render(
            contact_info=contact_info,
            cover_letter_text=cover_letter_text
        )
    
    def render_resume_with_referral(self, resume_data: Dict[str, Any], 
                                   referral_contact: Dict[str, str]) -> str:
        """
        Render resume with referral contact information.
        
        Args:
            resume_data: Dictionary containing resume data
            referral_contact: Dictionary with referral contact info (name, phone, email, linkedin, github)
            
        Returns:
            Rendered LaTeX document as string with referral contact info
        """
        # Create a copy of resume data and replace contact info
        resume_with_referral = resume_data.copy()
        resume_with_referral['contact_info'] = referral_contact
        
        return self.render_resume(resume_with_referral)
    
    def render_cover_letter_with_referral(self, cover_letter_text: str,
                                         referral_contact: Dict[str, str]) -> str:
        """
        Render cover letter with referral contact information.
        
        Args:
            cover_letter_text: The main body text of the cover letter
            referral_contact: Dictionary with referral contact info
            
        Returns:
            Rendered LaTeX document as string with referral contact info
        """
        return self.render_cover_letter(referral_contact, cover_letter_text)
