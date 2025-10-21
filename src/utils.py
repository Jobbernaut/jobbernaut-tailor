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
    """Save data to a YAML file, preserving literal block scalars (|) for multiline strings."""
    
    class LiteralString(str):
        """String subclass to mark strings that should use literal block scalar style."""
        pass
    
    def literal_presenter(dumper, data):
        """Present strings as literal block scalars if they contain newlines."""
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    # Create a custom dumper
    yaml.add_representer(str, literal_presenter)
    
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


def load_prompt_template(prompt_file: str) -> str:
    """Load a prompt template from the prompts directory."""
    filepath = os.path.join("prompts", prompt_file)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def compile_latex_to_pdf(
    tex_file_path: str,
    output_dir: str,
    document_type: str = "resume"
) -> str:
    """
    Compile LaTeX file to PDF using pdflatex.
    
    Args:
        tex_file_path: Path to the .tex file to compile
        output_dir: Directory where the PDF should be generated
        document_type: Type of document ("resume" or "cover_letter")
    
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

    # Determine which .cls file to use based on document type
    if document_type == "cover_letter":
        cls_source = "coverletter.cls"
    else:
        cls_source = "resume.cls"

    # Copy the .cls file to the output directory
    cls_dest = os.path.join(output_dir, os.path.basename(cls_source))
    if not os.path.exists(cls_source):
        raise FileNotFoundError(
            f"{cls_source} not found in the project root. "
            f"Please ensure {cls_source} exists."
        )
    shutil.copy2(cls_source, cls_dest)

    # Get the base name without extension
    tex_basename = os.path.basename(tex_file_path)
    tex_name_no_ext = os.path.splitext(tex_basename)[0]

    # Set environment variables for MiKTeX to auto-install packages
    env = os.environ.copy()
    env["MIKTEX_AUTOINSTALL"] = "1"
    env["MIKTEX_ENABLEINSTALLER"] = "t"

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
                timeout=120,
                env=env,
            )

            # Check if PDF was generated (more reliable than return code)
            # pdflatex can return non-zero even when PDF is successfully created
            pdf_path_check = os.path.join(output_dir, f"{tex_name_no_ext}.pdf")
            
            if result.returncode != 0 and not os.path.exists(pdf_path_check):
                log_file = os.path.join(output_dir, f"{tex_name_no_ext}.log")
                error_msg = "LaTeX compilation failed."

                if os.path.exists(log_file):
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        log_content = f.read()
                        # Look for actual errors (not warnings)
                        error_lines = [
                            line
                            for line in log_content.split("\n")
                            if line.startswith("!") and "Error" in line
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
    Create a referral version of the LaTeX document by replacing contact information.

    Args:
        latex_text: Original LaTeX content
        referral_email: Email address for referral version
        referral_phone: Phone number for referral version

    Returns:
        Modified LaTeX with referral contact information
    """
    import re

    referral_latex = latex_text

    # Replace phone number - handle various phone formats
    phone_patterns = [
        r"\+1\s*919-672-2226",
        r"919-672-2226",
        r"\(919\)\s*672-2226",
    ]
    
    for pattern in phone_patterns:
        referral_latex = re.sub(pattern, referral_phone, referral_latex)

    # Replace email
    email_pattern = r"srmanda\.cs@gmail\.com"
    referral_latex = re.sub(email_pattern, referral_email, referral_latex)

    return referral_latex


def cleanup_output_directory(output_dir: str, first_name: str, last_name: str, company_name: str, job_id: str) -> None:
    """
    Clean up output directory by moving all non-PDF files to debug/ folder.
    Keep only the 4 final PDFs in the main directory.
    """
    import shutil

    # Create debug directory
    debug_dir = os.path.join(output_dir, "debug")
    os.makedirs(debug_dir, exist_ok=True)

    # Sanitize names for filenames
    safe_first = first_name.replace(" ", "_")
    safe_last = last_name.replace(" ", "_")
    safe_company = company_name.replace(" ", "_")

    # Define the 4 PDFs that should stay in main directory
    final_pdfs = {
        f"{safe_first}_{safe_last}_{safe_company}_{job_id}_Resume.pdf",
        f"{safe_first}_{safe_last}_{safe_company}_{job_id}_Cover_Letter.pdf",
        f"Referral_{safe_first}_{safe_last}_{safe_company}_{job_id}_Resume.pdf",
        f"Referral_{safe_first}_{safe_last}_{safe_company}_{job_id}_Cover_Letter.pdf",
    }

    # Move everything else to debug/
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)

        # Skip if it's the debug directory itself
        if filename == "debug":
            continue

        # Skip if it's a directory
        if os.path.isdir(filepath):
            continue

        # Keep final PDFs, move everything else
        if filename not in final_pdfs:
            dest_path = os.path.join(debug_dir, filename)
            shutil.move(filepath, dest_path)
            print(f"  Moved {filename} to debug/")
