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
    job_description: str, cover_letter_points: List[Dict]
) -> tuple:
    """
    Select the best cover letter point based on keyword matching.
    Returns a tuple of (best_point, default_point).
    The best_point has the most keyword matches, default_point is always included.
    """
    job_desc_lower = job_description.lower()
    best_point = None
    max_matches = 0
    default_point = None

    for point in cover_letter_points:
        # Track the default point
        if point.get("default", False):
            default_point = point

        # Count keyword matches (skip default point from keyword matching)
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
    filename = f"{company_name}_{job_title}_Resume.json"
    filepath = os.path.join(output_dir, filename)
    save_json(filepath, resume_json)
    return filepath


def save_cover_letter(
    output_dir: str, cover_letter_text: str, job_title: str, company_name: str
) -> str:
    """Save the cover letter to the output directory as both TXT and PDF."""
    # Save as TXT
    txt_filename = f"{company_name}_{job_title}_CoverLetter.txt"
    txt_filepath = os.path.join(output_dir, txt_filename)

    with open(txt_filepath, "w", encoding="utf-8") as f:
        f.write(cover_letter_text)

    # Save as PDF
    pdf_filename = f"{company_name}_{job_title}_CoverLetter.pdf"
    pdf_filepath = os.path.join(output_dir, pdf_filename)

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT
    from html import escape

    # Create PDF
    doc = SimpleDocTemplate(
        pdf_filepath,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=12,
    )

    # Split text into paragraphs and add to PDF
    paragraphs = cover_letter_text.split("\n\n")
    for para_text in paragraphs:
        if para_text.strip():
            # Escape special characters for reportlab using html.escape
            para_text = escape(para_text)
            # Replace single newlines with <br/> tags for reportlab
            para_text = para_text.replace("\n", "<br/>")
            para = Paragraph(para_text, normal_style)
            elements.append(para)
            elements.append(Spacer(1, 0.1 * inch))

    # Build PDF
    doc.build(elements)

    return pdf_filepath


def save_latex_resume(
    output_dir: str, latex_text: str, job_title: str, company_name: str
) -> str:
    """Save the LaTeX resume to the output directory."""
    filename = f"{company_name}_{job_title}_Resume.tex"
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
            if "Resume" in filename:
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
