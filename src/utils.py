"""
Utility functions for the resume optimization pipeline.
"""

import json
import os
from typing import Dict, List, Any, Optional
import yaml


def load_yaml(filepath: str) -> Any:
    """Load and parse a YAML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(filepath: str, data: Any) -> None:
    """Save data to a YAML file."""
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )


def load_json(filepath: str) -> Dict:
    """Load and parse a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath: str, data: Dict) -> None:
    """Save data to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_pending_job(applications: List[Dict]) -> Optional[Dict]:
    """Find the first job with status 'pending'."""
    for job in applications:
        if job.get("status") == "pending":
            return job
    return None


def update_job_status(filepath: str, job_id: str, new_status: str) -> None:
    """Update the status of a specific job in the applications YAML file."""
    applications = load_yaml(filepath)

    for job in applications:
        if job.get("job_id") == job_id:
            job["status"] = new_status
            break

    save_yaml(filepath, applications)


def select_best_cover_letter_point(
    job_description: str, cover_letter_points: List[Dict], location: str = ""
) -> tuple:
    """
    Select the best cover letter point based on keyword matching.
    Returns a tuple of (best_point, default_point).
    The best_point has the most keyword matches, default_point is selected based on location.
    
    Args:
        job_description: The job description text
        cover_letter_points: List of cover letter points
        location: Job location (empty = US, otherwise check for US indicators)
    """
    job_desc_lower = job_description.lower()
    best_point = None
    max_matches = 0
    default_point = None
    
    # Determine if this is a US job
    is_us = True
    if location and location.strip():
        location_lower = location.lower()
        us_indicators = ["united states", "usa", "u.s.a", "u.s.", "us"]
        is_us = any(indicator in location_lower for indicator in us_indicators)

    for point in cover_letter_points:
        # Track the appropriate default point based on location
        if point.get("default", False):
            point_location_type = point.get("location_type", "US")
            if is_us and point_location_type == "US":
                default_point = point
            elif not is_us and point_location_type == "International":
                default_point = point

        # Count keyword matches (skip default points from keyword matching)
        if not point.get("default", False):
            keywords = point.get("keywords", [])
            matches = sum(
                1 for keyword in keywords if keyword.lower() in job_desc_lower
            )

            if matches > max_matches:
                max_matches = matches
                best_point = point

    # Return both the best match and the default point
    return (best_point, default_point)


def create_output_directory(job_id: str, job_title: str, company_name: str) -> str:
    """
    Create an output directory for the job application.
    Returns the path to the created directory.
    """
    # Sanitize the directory name
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in job_title
    )
    safe_company = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in company_name
    )

    # Create directory name: company_title_jobid
    dir_name = f"{safe_company}_{safe_title}_{job_id}"
    dir_path = os.path.join("output", dir_name)

    # Create the directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)

    return dir_path


def save_resume(
    output_dir: str, resume_json: Dict, job_title: str, company_name: str
) -> str:
    """Save the tailored resume to the output directory."""
    # Sanitize filename components
    safe_company = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in company_name
    )
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in job_title
    )
    filename = f"{safe_company}_{safe_title}_Resume.json"
    filepath = os.path.join(output_dir, filename)
    save_json(filepath, resume_json)
    return filepath


def save_cover_letter(
    output_dir: str,
    cover_letter_text: str,
    job_title: str,
    company_name: str,
    first_name: str,
    last_name: str,
    contact_info: Dict = None,
) -> str:
    """Save the cover letter to the output directory as both TXT and PDF with professional formatting."""
    # Sanitize filename components
    safe_company = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in company_name
    )
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in job_title
    )
    
    # Save as TXT
    txt_filename = f"{safe_company}_{safe_title}_CoverLetter.txt"
    txt_filepath = os.path.join(output_dir, txt_filename)

    with open(txt_filepath, "w", encoding="utf-8") as f:
        f.write(cover_letter_text)

    # Save as PDF with professional formatting
    pdf_filename = f"{safe_company}_{safe_title}_CoverLetter.pdf"
    pdf_filepath = os.path.join(output_dir, pdf_filename)

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from datetime import datetime
    from html import escape

    # Create PDF with proper metadata
    full_name = f"{first_name} {last_name}"
    doc = SimpleDocTemplate(
        pdf_filepath,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=f"{full_name} Cover Letter",
        author=full_name,
        subject="Cover Letter",
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles using Helvetica
    name_style = ParagraphStyle(
        "NameStyle",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    contact_style = ParagraphStyle(
        "ContactStyle",
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        spaceAfter=16,
    )

    date_style = ParagraphStyle(
        "DateStyle",
        fontName="Helvetica",
        fontSize=11,
        leading=13,
        alignment=TA_LEFT,
        spaceAfter=12,
    )

    recipient_style = ParagraphStyle(
        "RecipientStyle",
        fontName="Helvetica",
        fontSize=11,
        leading=13,
        alignment=TA_LEFT,
        spaceAfter=16,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        fontName="Helvetica",
        fontSize=11,
        leading=14.3,  # 1.3x line spacing
        alignment=TA_LEFT,
        spaceAfter=11,  # Space between paragraphs
    )

    # Add header with name
    name_para = Paragraph(full_name, name_style)
    elements.append(name_para)

    # Add contact information if provided
    if contact_info:
        contact_parts = []
        
        if contact_info.get("phone"):
            contact_parts.append(contact_info["phone"])
        
        if contact_info.get("email"):
            email = contact_info["email"]
            contact_parts.append(f'<a href="mailto:{email}">{email}</a>')
        
        if contact_info.get("linkedin_url"):
            linkedin = contact_info["linkedin_url"]
            # Extract display text (e.g., "linkedin.com/in/username")
            display = linkedin.replace("https://", "").replace("http://", "")
            contact_parts.append(f'<a href="{linkedin}">{display}</a>')
        
        if contact_info.get("github_url"):
            github = contact_info["github_url"]
            display = github.replace("https://", "").replace("http://", "")
            contact_parts.append(f'<a href="{github}">{display}</a>')
        
        if contact_info.get("portfolio_url"):
            portfolio = contact_info["portfolio_url"]
            display = portfolio.replace("https://", "").replace("http://", "")
            contact_parts.append(f'<a href="{portfolio}">{display}</a>')
        
        if contact_parts:
            contact_line = " • ".join(contact_parts)
            contact_para = Paragraph(contact_line, contact_style)
            elements.append(contact_para)
    else:
        # Add spacing if no contact info
        elements.append(Spacer(1, 0.2 * inch))

    # Add date
    current_date = datetime.now().strftime("%B %d, %Y")
    date_para = Paragraph(current_date, date_style)
    elements.append(date_para)

    # Parse the cover letter text to extract greeting and body
    lines = cover_letter_text.strip().split("\n")
    
    # Find the greeting line (starts with "Dear")
    greeting_line = None
    body_start_idx = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith("Dear"):
            greeting_line = line.strip()
            body_start_idx = i + 1
            break
    
    # If no greeting found, assume first line is greeting
    if greeting_line is None and lines:
        greeting_line = lines[0].strip()
        body_start_idx = 1
    
    # Add recipient (extract from greeting or use default)
    if greeting_line:
        # Add the greeting as recipient
        recipient_para = Paragraph(greeting_line.rstrip(","), recipient_style)
        elements.append(recipient_para)
    else:
        # Default recipient
        recipient_text = f"{job_title} Hiring Team<br/>{company_name}"
        recipient_para = Paragraph(recipient_text, recipient_style)
        elements.append(recipient_para)

    # Process the body paragraphs
    current_paragraph = []
    
    for line in lines[body_start_idx:]:
        line = line.strip()
        
        # Skip the greeting if it appears again
        if line.startswith("Dear"):
            continue
            
        # Empty line indicates paragraph break
        if not line:
            if current_paragraph:
                para_text = " ".join(current_paragraph)
                # Escape special characters
                para_text = escape(para_text)
                para = Paragraph(para_text, body_style)
                elements.append(para)
                current_paragraph = []
        else:
            current_paragraph.append(line)
    
    # Add the last paragraph if exists
    if current_paragraph:
        para_text = " ".join(current_paragraph)
        para_text = escape(para_text)
        para = Paragraph(para_text, body_style)
        elements.append(para)

    # Build PDF
    doc.build(elements)

    return pdf_filepath


def save_latex_resume(
    output_dir: str, latex_text: str, job_title: str, company_name: str
) -> str:
    """Save the LaTeX resume to the output directory."""
    # Sanitize filename components
    safe_company = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in company_name
    )
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in job_title
    )
    filename = f"{safe_company}_{safe_title}_Resume.tex"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(latex_text)

    return filepath


def load_prompt_template(prompt_file: str) -> str:
    """Load a prompt template from the prompts directory."""
    filepath = os.path.join("prompts", prompt_file)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def compile_latex_to_pdf(tex_file_path: str, output_dir: str) -> str:
    """
    Compile LaTeX file to PDF using pdflatex.
    Returns the path to the generated PDF file.
    """
    import subprocess
    import shutil

    # Check if pdflatex is available
    if shutil.which("pdflatex") is None:
        raise RuntimeError(
            "pdflatex not found. Please install MiKTeX or TeX Live.\n"
            "Download MiKTeX from: https://miktex.org/download"
        )

    # Copy resume.cls to the output directory (required for compilation)
    resume_cls_source = "resume.cls"
    resume_cls_dest = os.path.join(output_dir, "resume.cls")

    if not os.path.exists(resume_cls_source):
        raise FileNotFoundError(
            f"resume.cls not found in the project root. "
            f"Please ensure resume.cls exists at: {resume_cls_source}"
        )

    shutil.copy2(resume_cls_source, resume_cls_dest)

    # Get the base name without extension
    tex_basename = os.path.basename(tex_file_path)
    tex_name_no_ext = os.path.splitext(tex_basename)[0]

    # Set environment variables for MiKTeX to auto-install packages without prompting
    env = os.environ.copy()
    env["MIKTEX_AUTOINSTALL"] = "1"  # Enable automatic package installation
    env["MIKTEX_ENABLEINSTALLER"] = "t"  # Enable the package installer

    # Run pdflatex twice (standard practice for proper references)
    for run in range(1, 3):
        print(f"  Running pdflatex (pass {run}/2)...")
        try:
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory",
                    output_dir,
                    tex_file_path,
                ],
                capture_output=True,
                text=True,
                timeout=120,  # Increased timeout to allow for package installation
                env=env,  # Pass environment variables
            )

            # Check for errors in the output
            if result.returncode != 0:
                # Extract relevant error information from log
                log_file = os.path.join(output_dir, f"{tex_name_no_ext}.log")
                error_msg = "LaTeX compilation failed."

                if os.path.exists(log_file):
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        log_content = f.read()
                        # Look for error lines
                        error_lines = [
                            line
                            for line in log_content.split("\n")
                            if line.startswith("!")
                        ]
                        if error_lines:
                            error_msg += f"\n\nErrors found:\n" + "\n".join(
                                error_lines[:5]
                            )

                raise RuntimeError(error_msg)

        except subprocess.TimeoutExpired:
            raise RuntimeError("LaTeX compilation timed out after 120 seconds.")

    # Clean up auxiliary files
    aux_extensions = [".aux", ".log", ".out"]
    for ext in aux_extensions:
        aux_file = os.path.join(output_dir, f"{tex_name_no_ext}{ext}")
        if os.path.exists(aux_file):
            os.remove(aux_file)

    # Also remove the copied resume.cls
    if os.path.exists(resume_cls_dest):
        os.remove(resume_cls_dest)

    # Return the path to the generated PDF
    pdf_path = os.path.join(output_dir, f"{tex_name_no_ext}.pdf")

    if not os.path.exists(pdf_path):
        raise RuntimeError(
            f"PDF was not generated. Expected at: {pdf_path}\n"
            "Check the LaTeX file for syntax errors."
        )

    return pdf_path


def create_referral_latex(
    latex_text: str, referral_email: str, referral_phone: str
) -> str:
    """
    Create a referral version of the LaTeX resume by replacing contact information.

    Args:
        latex_text: Original LaTeX content
        referral_email: Email address for referral version
        referral_phone: Phone number for referral version

    Returns:
        Modified LaTeX with referral contact information
    """
    import re

    # Create a copy of the LaTeX text
    referral_latex = latex_text

    # Replace phone number - matches the actual phone format in \address{+1 919-672-2226 \\ Raleigh, NC}
    phone_pattern = r"\+1 919-672-2226"
    referral_latex = re.sub(phone_pattern, referral_phone, referral_latex)

    # Replace email - matches srmanda.cs@gmail.com in both mailto: and display text
    # This will replace both occurrences in: \href{mailto:srmanda.cs@gmail.com}{srmanda.cs@gmail.com}
    email_pattern = r"srmanda\.cs@gmail\.com"
    referral_latex = re.sub(email_pattern, referral_email, referral_latex)

    return referral_latex


def organize_output_files(
    output_dir: str,
    first_name: str,
    last_name: str,
    company_name: str,
    job_id: str,
) -> None:
    """
    Organize output files into final structure:
    - Create debug/ subdirectory
    - Move .tex, .json, .txt files to debug/
    - Rename PDFs with proper naming convention
    """
    import shutil

    # Create debug subdirectory
    debug_dir = os.path.join(output_dir, "debug")
    os.makedirs(debug_dir, exist_ok=True)

    # Sanitize names for filenames (replace spaces with underscores)
    safe_first = first_name.replace(" ", "_")
    safe_last = last_name.replace(" ", "_")
    safe_company = company_name.replace(" ", "_")

    # Find and move files to debug/
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)

        # Skip if it's a directory
        if os.path.isdir(filepath):
            continue

        # Move .tex, .json, .txt files to debug/
        if filename.endswith((".tex", ".json", ".txt")):
            dest_path = os.path.join(debug_dir, filename)
            shutil.move(filepath, dest_path)
            print(f"  Moved {filename} to debug/")

        # Rename PDFs with proper naming convention
        elif filename.endswith(".pdf"):
            if "Referral" in filename and "Resume" in filename:
                # Handle referral resume PDF
                new_name = f"Referral_{safe_first}_{safe_last}_{safe_company}_{job_id}_Resume.pdf"
                new_path = os.path.join(output_dir, new_name)
                shutil.move(filepath, new_path)
                print(f"  Renamed referral resume PDF to: {new_name}")

            elif "Resume" in filename:
                # Handle regular resume PDF
                new_name = (
                    f"{safe_first}_{safe_last}_{safe_company}_{job_id}_Resume.pdf"
                )
                new_path = os.path.join(output_dir, new_name)
                shutil.move(filepath, new_path)
                print(f"  Renamed resume PDF to: {new_name}")

            elif "CoverLetter" in filename or "Cover_Letter" in filename:
                new_name = (
                    f"{safe_first}_{safe_last}_{safe_company}_{job_id}_Cover_Letter.pdf"
                )
                new_path = os.path.join(output_dir, new_name)
                shutil.move(filepath, new_path)
                print(f"  Renamed cover letter PDF to: {new_name}")
