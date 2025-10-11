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
) -> Dict:
    """
    Select the best cover letter point based on keyword matching.
    Returns the point with the most keyword matches, or the default point if no matches.
    """
    job_desc_lower = job_description.lower()
    best_point = None
    max_matches = 0
    default_point = None

    for point in cover_letter_points:
        # Track the default point
        if point.get("default", False):
            default_point = point

        # Count keyword matches
        keywords = point.get("keywords", [])
        matches = sum(1 for keyword in keywords if keyword.lower() in job_desc_lower)

        if matches > max_matches:
            max_matches = matches
            best_point = point

    # Return the best match, or default if no matches found
    return best_point if best_point else default_point


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
    """Save the cover letter to the output directory."""
    filename = f"{company_name}_{job_title}_CoverLetter.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cover_letter_text)

    return filepath


def load_prompt_template(prompt_file: str) -> str:
    """Load a prompt template from the prompts directory."""
    filepath = os.path.join("prompts", prompt_file)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
