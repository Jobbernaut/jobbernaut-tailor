"""
Main pipeline for automating resume and cover letter generation.
Follows a strict 12-step process with no retries.
"""

import os
import json
import shutil
from dotenv import load_dotenv
import fastapi_poe as fp

from utils import (
    load_yaml,
    load_json,
    save_json,
    find_pending_job,
    update_job_status,
    create_output_directory,
    load_prompt_template,
    compile_latex_to_pdf,
    create_referral_latex,
    cleanup_output_directory,
)


class ResumeOptimizationPipeline:
    """Main pipeline for processing job applications."""

    def __init__(self):
        """Initialize the pipeline with configuration."""
        load_dotenv()
        self.api_key = os.getenv("POE_API_KEY")

        if not self.api_key:
            raise ValueError("POE_API_KEY not found in environment variables")

        # Load configuration
        self.config = load_json("config.json")
        defaults = self.config.get("defaults", {})

        # Bot configurations
        self.resume_bot = self.config.get("resume_generation", {}).get("bot_name") or defaults.get("resume_bot")
        self.cover_letter_bot = self.config.get("cover_letter_generation", {}).get("bot_name") or defaults.get("cover_letter_bot")
        self.latex_bot = self.config.get("latex_conversion", {}).get("bot_name") or defaults.get("latex_bot")
        self.verification_bot = self.config.get("latex_verification", {}).get("bot_name")

        # Referral contact info
        referral_config = self.config.get("referral_resume", {})
        self.referral_email = referral_config.get("email", "srmanda.compsci@gmail.com")
        self.referral_phone = referral_config.get("phone", "+1 919-526-0631")

        # Load master resume
        self.master_resume = load_json("profile/master_resume.json")

        # Load prompt templates
        self.resume_prompt_template = load_prompt_template("generate_resume.txt")
        self.cover_letter_prompt_template = load_prompt_template("generate_cover_letter.txt")
        self.latex_conversion_prompt_template = load_prompt_template("convert_resume_to_latex.txt")
        self.cover_letter_latex_prompt_template = load_prompt_template("convert_cover_letter_to_latex.txt")
        self.verification_prompt_template = load_prompt_template("verify_latex_resume.txt")

    async def call_poe_api(self, prompt: str, bot_name: str) -> str:
        """Call the Poe API."""
        print(f"  Calling {bot_name}...")
        response_text = ""
        async for partial in fp.get_bot_response(
            messages=[fp.ProtocolMessage(role="user", content=prompt)],
            bot_name=bot_name,
            api_key=self.api_key,
        ):
            response_text += partial.text
        return response_text

    def extract_json_from_response(self, response: str) -> dict:
        """Extract JSON from API response."""
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
        else:
            json_str = response.strip()

        return json.loads(json_str)

    def extract_latex_from_response(self, response: str) -> str:
        """Extract LaTeX code from API response and sanitize thinking output."""
        latex_text = response.strip()
        
        if "```latex" in latex_text:
            start = latex_text.find("```latex") + 8
            end = latex_text.find("```", start)
            if end != -1:
                latex_text = latex_text[start:end].strip()
        elif "```" in latex_text:
            start = latex_text.find("```") + 3
            end = latex_text.find("```", start)
            if end != -1:
                latex_text = latex_text[start:end].strip()
        
        # Find \documentclass if not in code blocks
        if "\\documentclass" not in latex_text:
            doc_start = response.find("\\documentclass")
            if doc_start != -1:
                latex_text = response[doc_start:].strip()
        
        # Sanitize: Remove thinking output lines (lines starting with > or containing *Thinking*)
        lines = latex_text.split('\n')
        clean_lines = []
        found_documentclass = False
        
        for line in lines:
            stripped = line.strip()
            # Skip thinking output markers
            if stripped.startswith('>') or '*Thinking*' in stripped:
                continue
            # Once we find \documentclass, start collecting lines
            if '\\documentclass' in line:
                found_documentclass = True
            if found_documentclass:
                clean_lines.append(line)
        
        # If we found clean content, use it; otherwise return original
        if clean_lines:
            latex_text = '\n'.join(clean_lines)
        
        return latex_text.strip()

    async def process_job(self, job: dict) -> None:
        """
        Process a single job application following the 12-step pipeline.
        
        Pipeline:
        1. Generate Resume JSON
        2. Generate Cover Letter Text
        3. Convert Resume to LaTeX
        4. Convert Cover Letter to LaTeX
        5. Verify Resume LaTeX (must be >= 95%)
        6. Fail if verification < 95% (no retry)
        7. Compile Resume PDF
        8. Compile Cover Letter PDF
        9. Create Referral LaTeX files
        10. Compile Referral Resume PDF
        11. Compile Referral Cover Letter PDF
        12. Clean up (move non-PDFs to debug/)
        """
        job_id = job.get("job_id")
        job_title = job.get("job_title")
        company_name = job.get("company_name")
        job_description = job.get("job_description")

        print(f"\n{'='*60}")
        print(f"Processing: {job_title} at {company_name}")
        print(f"Job ID: {job_id}")
        print(f"{'='*60}\n")

        # Create output directory
        output_dir = create_output_directory(job_id, job_title, company_name)
        print(f"Output directory: {output_dir}\n")

        # STEP 1: Generate Resume JSON
        print("STEP 1: Generating tailored resume JSON...")
        resume_prompt = self.resume_prompt_template.replace(
            "[JOB_DESCRIPTION]", f"```\n{job_description}\n```"
        ).replace(
            "[MASTER_RESUME_JSON]", f"```json\n{json.dumps(self.master_resume, indent=2)}\n```"
        ).replace(
            "[COMPANY_NAME]", company_name
        )
        
        resume_response = await self.call_poe_api(resume_prompt, self.resume_bot)
        tailored_resume = self.extract_json_from_response(resume_response)
        
        # Save resume JSON
        resume_json_path = os.path.join(output_dir, "Resume.json")
        save_json(resume_json_path, tailored_resume)
        print(f"✓ Resume JSON saved\n")

        # STEP 2: Generate Cover Letter Text
        print("STEP 2: Generating cover letter text...")
        cover_letter_prompt = self.cover_letter_prompt_template.replace(
            "[TAILORED_RESUME_JSON]", f"```json\n{json.dumps(tailored_resume, indent=2)}\n```"
        ).replace(
            "[JOB_DESCRIPTION]", f"```\n{job_description}\n```"
        ).replace(
            "[COMPANY_NAME]", company_name
        )
        
        cover_letter_response = await self.call_poe_api(cover_letter_prompt, self.cover_letter_bot)
        cover_letter_text = cover_letter_response.strip()
        
        # Save cover letter text
        cover_letter_txt_path = os.path.join(output_dir, "CoverLetter.txt")
        with open(cover_letter_txt_path, "w", encoding="utf-8") as f:
            f.write(cover_letter_text)
        print(f"✓ Cover letter text saved\n")

        # STEP 3: Convert Resume to LaTeX
        print("STEP 3: Converting resume to LaTeX...")
        latex_prompt = self.latex_conversion_prompt_template.replace(
            "[TAILORED_RESUME_JSON]", f"```json\n{json.dumps(tailored_resume, indent=2)}\n```"
        )
        
        latex_response = await self.call_poe_api(latex_prompt, self.latex_bot)
        resume_latex = self.extract_latex_from_response(latex_response)
        
        # Save resume LaTeX
        resume_tex_path = os.path.join(output_dir, "Resume.tex")
        with open(resume_tex_path, "w", encoding="utf-8") as f:
            f.write(resume_latex)
        print(f"✓ Resume LaTeX saved\n")

        # STEP 4: Convert Cover Letter to LaTeX
        print("STEP 4: Converting cover letter to LaTeX...")
        contact_info = tailored_resume.get("contact_info", {})
        cover_letter_latex_prompt = self.cover_letter_latex_prompt_template.replace(
            "[CONTACT_INFO_JSON]", f"```json\n{json.dumps(contact_info, indent=2)}\n```"
        ).replace(
            "[COVER_LETTER_TEXT]", cover_letter_text
        )
        
        cover_letter_latex_response = await self.call_poe_api(cover_letter_latex_prompt, self.latex_bot)
        cover_letter_latex = self.extract_latex_from_response(cover_letter_latex_response)
        
        # Save cover letter LaTeX
        cover_letter_tex_path = os.path.join(output_dir, "CoverLetter.tex")
        with open(cover_letter_tex_path, "w", encoding="utf-8") as f:
            f.write(cover_letter_latex)
        print(f"✓ Cover letter LaTeX saved\n")

        # STEP 5 & 6: Verify Resume LaTeX (must be >= 95%, fail if not)
        print("STEP 5-6: Verifying resume LaTeX quality...")
        verification_prompt = self.verification_prompt_template.replace(
            "[MASTER_RESUME_JSON]", f"```json\n{json.dumps(tailored_resume, indent=2)}\n```"
        ).replace(
            "[LATEX_RESUME]", f"```latex\n{resume_latex}\n```"
        )
        
        verification_response = await self.call_poe_api(verification_prompt, self.verification_bot)
        verification_result = self.extract_json_from_response(verification_response)
        
        quality_score = verification_result.get("quality_score", 0)
        print(f"  Quality Score: {quality_score}/100")
        
        if quality_score < 95:
            print(f"\n{'='*60}")
            print("❌ VERIFICATION FAILED")
            print(f"{'='*60}")
            print(f"Quality score {quality_score} is below required 95%")
            print("Pipeline halted. No retry.")
            print(f"{'='*60}\n")
            raise ValueError(f"Resume quality score {quality_score} < 95%. Pipeline failed.")
        
        print(f"✓ Verification passed (>= 95%)\n")

        # Get name for final PDFs
        first_name = tailored_resume["contact_info"]["first_name"]
        last_name = tailored_resume["contact_info"]["last_name"]
        safe_first = first_name.replace(" ", "_")
        safe_last = last_name.replace(" ", "_")
        safe_company = company_name.replace(" ", "_")

        # STEP 7: Compile Resume PDF
        print("STEP 7: Compiling resume PDF...")
        resume_pdf = compile_latex_to_pdf(resume_tex_path, output_dir, "resume")
        
        # Rename to final name
        final_resume_name = f"{safe_first}_{safe_last}_{safe_company}_{job_id}_Resume.pdf"
        final_resume_path = os.path.join(output_dir, final_resume_name)
        shutil.move(resume_pdf, final_resume_path)
        print(f"✓ Resume PDF: {final_resume_name}\n")

        # STEP 8: Compile Cover Letter PDF
        print("STEP 8: Compiling cover letter PDF...")
        cover_letter_pdf = compile_latex_to_pdf(cover_letter_tex_path, output_dir, "cover_letter")
        
        # Rename to final name
        final_cover_letter_name = f"{safe_first}_{safe_last}_{safe_company}_{job_id}_Cover_Letter.pdf"
        final_cover_letter_path = os.path.join(output_dir, final_cover_letter_name)
        shutil.move(cover_letter_pdf, final_cover_letter_path)
        print(f"✓ Cover Letter PDF: {final_cover_letter_name}\n")

        # STEP 9: Create Referral LaTeX files
        print("STEP 9: Creating referral LaTeX files...")
        
        # Create referral resume LaTeX
        referral_resume_latex = create_referral_latex(resume_latex, self.referral_email, self.referral_phone)
        referral_resume_tex_path = os.path.join(output_dir, "Referral_Resume.tex")
        with open(referral_resume_tex_path, "w", encoding="utf-8") as f:
            f.write(referral_resume_latex)
        
        # Create referral cover letter LaTeX
        referral_cover_letter_latex = create_referral_latex(cover_letter_latex, self.referral_email, self.referral_phone)
        referral_cover_letter_tex_path = os.path.join(output_dir, "Referral_CoverLetter.tex")
        with open(referral_cover_letter_tex_path, "w", encoding="utf-8") as f:
            f.write(referral_cover_letter_latex)
        
        print(f"✓ Referral LaTeX files created\n")

        # STEP 10: Compile Referral Resume PDF
        print("STEP 10: Compiling referral resume PDF...")
        referral_resume_pdf = compile_latex_to_pdf(referral_resume_tex_path, output_dir, "resume")
        
        # Rename to final name
        final_referral_resume_name = f"Referral_{safe_first}_{safe_last}_{safe_company}_{job_id}_Resume.pdf"
        final_referral_resume_path = os.path.join(output_dir, final_referral_resume_name)
        shutil.move(referral_resume_pdf, final_referral_resume_path)
        print(f"✓ Referral Resume PDF: {final_referral_resume_name}\n")

        # STEP 11: Compile Referral Cover Letter PDF
        print("STEP 11: Compiling referral cover letter PDF...")
        referral_cover_letter_pdf = compile_latex_to_pdf(referral_cover_letter_tex_path, output_dir, "cover_letter")
        
        # Rename to final name
        final_referral_cover_letter_name = f"Referral_{safe_first}_{safe_last}_{safe_company}_{job_id}_Cover_Letter.pdf"
        final_referral_cover_letter_path = os.path.join(output_dir, final_referral_cover_letter_name)
        shutil.move(referral_cover_letter_pdf, final_referral_cover_letter_path)
        print(f"✓ Referral Cover Letter PDF: {final_referral_cover_letter_name}\n")

        # STEP 12: Clean up - move everything except 4 PDFs to debug/
        print("STEP 12: Cleaning up output directory...")
        cleanup_output_directory(output_dir, first_name, last_name, company_name, job_id)
        print(f"✓ Cleanup complete\n")

        # Update job status
        update_job_status("applications.yaml", job_id, "processed")

        print(f"{'='*60}")
        print(f"✓ Successfully processed: {job_title} at {company_name}")
        print(f"{'='*60}\n")

    async def run(self) -> None:
        """Run the pipeline to process pending jobs."""
        print("\n" + "=" * 60)
        print("RESUME OPTIMIZATION PIPELINE")
        print("=" * 60 + "\n")

        applications = load_yaml("applications.yaml")
        pending_job = find_pending_job(applications)

        if not pending_job:
            print("No pending jobs found. All jobs are processed!")
            return

        await self.process_job(pending_job)

        print("\nPipeline completed successfully!")
        print("Run the script again to process the next pending job.\n")


async def main():
    """Main entry point."""
    pipeline = ResumeOptimizationPipeline()
    await pipeline.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
