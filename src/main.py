"""
Main pipeline for automating resume and cover letter generation.
Follows a strict 12-step process with no retries.
"""

import os
import json
import shutil
from dotenv import load_dotenv
import fastapi_poe as fp
from pydantic import ValidationError

from utils import (
    load_yaml,
    load_json,
    save_json,
    find_pending_job,
    update_job_status,
    create_output_directory,
    load_prompt_template,
    compile_latex_to_pdf,
    cleanup_output_directory,
)
from template_renderer import TemplateRenderer
from models import TailoredResume


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

        # Referral contact info
        referral_config = self.config.get("referral_resume", {})
        self.referral_email = referral_config.get("email", "srmanda.compsci@gmail.com")
        self.referral_phone = referral_config.get("phone", "+1 919-526-0631")

        # Load master resume
        self.master_resume = load_json("profile/master_resume.json")

        # Load prompt templates
        self.resume_prompt_template = load_prompt_template("generate_resume.txt")
        self.cover_letter_prompt_template = load_prompt_template("generate_cover_letter.txt")
        
        # Initialize template renderer
        self.renderer = TemplateRenderer()

    async def call_poe_api(self, prompt: str, bot_name: str, max_retries: int = 3) -> str:
        """
        Call the Poe API with retry logic.
        
        Args:
            prompt: The prompt to send to the API
            bot_name: The name of the bot to use
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            The API response text
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"  API Call Attempt {attempt}/{max_retries} to {bot_name}...")
                response_text = ""
                async for partial in fp.get_bot_response(
                    messages=[fp.ProtocolMessage(role="user", content=prompt)],
                    bot_name=bot_name,
                    api_key=self.api_key,
                ):
                    response_text += partial.text
                
                print(f"  ✓ API call successful on attempt {attempt}")
                print(f"  Response length: {len(response_text)} characters")
                return response_text
                
            except Exception as e:
                last_error = e
                print(f"  ✗ API call failed on attempt {attempt}/{max_retries}")
                print(f"  Error type: {type(e).__name__}")
                print(f"  Error message: {str(e)}")
                
                if attempt < max_retries:
                    print(f"  Retrying API call...")
                else:
                    print(f"\n{'='*60}")
                    print(f"❌ API CALL FAILED AFTER {max_retries} ATTEMPTS")
                    print(f"{'='*60}")
                    print(f"Bot: {bot_name}")
                    print(f"Final error: {str(last_error)}")
                    print(f"{'='*60}\n")
                    raise Exception(f"API call failed after {max_retries} attempts: {str(last_error)}")
        
        # Should never reach here, but just in case
        raise Exception(f"API call failed after {max_retries} attempts: {str(last_error)}")

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

    def _build_error_feedback(self, validation_error: ValidationError) -> str:
        """
        Build detailed error feedback section to append to prompt.
        
        Args:
            validation_error: The Pydantic ValidationError from the previous attempt
            
        Returns:
            A formatted string with detailed error information and guidance
        """
        error_lines = [
            "\n" + "="*80,
            "# POSSIBLE POINTS OF FAILURE",
            "="*80,
            "",
            "⚠️  The previous attempt FAILED Pydantic validation with the following errors:",
            ""
        ]
        
        # Group errors by type for better organization
        field_errors = []
        type_errors = []
        missing_errors = []
        
        for error in validation_error.errors():
            field_path = " -> ".join(str(loc) for loc in error['loc'])
            error_msg = error['msg']
            error_type = error['type']
            
            error_detail = f"❌ Field: '{field_path}'\n   Error: {error_msg}\n   Type: {error_type}"
            
            # Add specific guidance based on common error patterns
            if 'graduation_date' in field_path and 'required' in error_msg.lower():
                error_detail += "\n   💡 FIX: Use 'graduation_date' NOT 'end_date' in education entries"
                missing_errors.append(error_detail)
            elif 'technologies' in field_path and ('list' in error_msg.lower() or 'array' in error_msg.lower()):
                error_detail += '\n   💡 FIX: Format as array: ["Tech1", "Tech2", "Tech3"] NOT "Tech1, Tech2, Tech3"'
                error_detail += '\n   💡 EXAMPLE: "technologies": ["Python", "PyTorch", "Scikit-learn"]'
                type_errors.append(error_detail)
            elif 'required' in error_msg.lower():
                error_detail += f"\n   💡 FIX: This field is REQUIRED and cannot be omitted"
                missing_errors.append(error_detail)
            elif 'type' in error_msg.lower() or 'valid' in error_msg.lower():
                error_detail += f"\n   💡 FIX: Check the data type - ensure it matches the schema"
                type_errors.append(error_detail)
            else:
                field_errors.append(error_detail)
        
        # Add errors in organized sections
        if missing_errors:
            error_lines.append("📋 MISSING REQUIRED FIELDS:")
            error_lines.append("")
            for err in missing_errors:
                error_lines.append(err)
                error_lines.append("")
        
        if type_errors:
            error_lines.append("🔧 TYPE/FORMAT ERRORS:")
            error_lines.append("")
            for err in type_errors:
                error_lines.append(err)
                error_lines.append("")
        
        if field_errors:
            error_lines.append("⚠️  OTHER VALIDATION ERRORS:")
            error_lines.append("")
            for err in field_errors:
                error_lines.append(err)
                error_lines.append("")
        
        # Add critical reminders
        error_lines.extend([
            "="*80,
            "🚨 CRITICAL REMINDERS FOR THIS RETRY:",
            "="*80,
            "",
            "1. Education entries MUST use 'graduation_date' (NOT 'end_date')",
            "2. Project 'technologies' MUST be an array: [\"Tech1\", \"Tech2\"]",
            "3. All required fields MUST be present (check schema in docs/expected_json_schema.md)",
            "4. Ensure data types match exactly (strings, arrays, objects)",
            "5. Do NOT invent new field names - use ONLY the fields defined in the schema",
            "",
            "="*80,
            "🎯 ACTION REQUIRED: Fix ALL errors listed above in your next response.",
            "="*80,
            ""
        ])
        
        return "\n".join(error_lines)

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
        
        # Retry loop for resume generation with Pydantic validation
        max_validation_retries = 3
        tailored_resume = None
        last_validation_error = None
        current_prompt = resume_prompt
        
        for validation_attempt in range(1, max_validation_retries + 1):
            print(f"\n{'='*60}")
            print(f"VALIDATION ATTEMPT {validation_attempt}/{max_validation_retries}")
            print(f"{'='*60}\n")
            
            # Generate resume (use modified prompt on retries)
            if validation_attempt == 1:
                print("  Generating resume JSON (initial attempt)...")
            else:
                print(f"  Regenerating resume JSON with error feedback (retry {validation_attempt - 1})...")
            
            resume_response = await self.call_poe_api(current_prompt, self.resume_bot)
            
            # Save raw response for debugging
            raw_response_path = os.path.join(output_dir, f"Resume_Response_Attempt_{validation_attempt}.txt")
            with open(raw_response_path, "w", encoding="utf-8") as f:
                f.write(resume_response)
            print(f"  Raw response saved to: Resume_Response_Attempt_{validation_attempt}.txt")
            
            # Extract JSON
            try:
                tailored_resume_raw = self.extract_json_from_response(resume_response)
                print(f"  ✓ JSON extraction successful")
            except json.JSONDecodeError as e:
                print(f"  ✗ JSON extraction failed: {str(e)}")
                if validation_attempt < max_validation_retries:
                    print(f"  Retrying with error feedback...")
                    error_feedback = f"\n\n{'='*80}\n# JSON PARSING ERROR\n{'='*80}\n\nThe previous response was not valid JSON.\nError: {str(e)}\n\nPlease ensure your response contains ONLY valid JSON with no additional text.\n{'='*80}\n"
                    current_prompt = resume_prompt + error_feedback
                    continue
                else:
                    print(f"\n{'='*60}")
                    print(f"❌ JSON EXTRACTION FAILED AFTER {max_validation_retries} ATTEMPTS")
                    print(f"{'='*60}\n")
                    raise ValueError(f"Failed to extract valid JSON after {max_validation_retries} attempts")
            
            # Save extracted JSON for debugging
            json_attempt_path = os.path.join(output_dir, f"Resume_JSON_Attempt_{validation_attempt}.json")
            save_json(json_attempt_path, tailored_resume_raw)
            print(f"  Extracted JSON saved to: Resume_JSON_Attempt_{validation_attempt}.json")
            
            # Validate with Pydantic
            print(f"  Validating JSON structure with Pydantic...")
            try:
                validated_resume = TailoredResume(**tailored_resume_raw)
                tailored_resume = validated_resume.model_dump()
                print(f"\n{'='*60}")
                print(f"✅ PYDANTIC VALIDATION PASSED ON ATTEMPT {validation_attempt}")
                print(f"{'='*60}\n")
                break  # Success! Exit retry loop
                
            except ValidationError as e:
                last_validation_error = e
                error_count = len(e.errors())
                
                print(f"\n{'='*60}")
                print(f"❌ PYDANTIC VALIDATION FAILED (Attempt {validation_attempt}/{max_validation_retries})")
                print(f"{'='*60}")
                print(f"Found {error_count} validation error(s):\n")
                
                # Display errors in detail
                for i, error in enumerate(e.errors(), 1):
                    field_path = " -> ".join(str(loc) for loc in error['loc'])
                    print(f"{i}. Field: '{field_path}'")
                    print(f"   Error: {error['msg']}")
                    print(f"   Type: {error['type']}\n")
                
                # Save invalid JSON for debugging
                invalid_json_path = os.path.join(output_dir, f"Resume_INVALID_Attempt_{validation_attempt}.json")
                save_json(invalid_json_path, tailored_resume_raw)
                print(f"Invalid JSON saved to: Resume_INVALID_Attempt_{validation_attempt}.json")
                
                if validation_attempt < max_validation_retries:
                    # Build error feedback and retry
                    print(f"\n{'='*60}")
                    print(f"PREPARING RETRY WITH ERROR FEEDBACK")
                    print(f"{'='*60}\n")
                    
                    error_feedback = self._build_error_feedback(e)
                    current_prompt = resume_prompt + error_feedback
                    
                    print(f"Error feedback appended to prompt ({len(error_feedback)} characters)")
                    print(f"Retrying generation with corrective guidance...\n")
                else:
                    # Final failure after all retries
                    print(f"\n{'='*60}")
                    print(f"❌ PYDANTIC VALIDATION FAILED AFTER {max_validation_retries} ATTEMPTS")
                    print(f"{'='*60}")
                    print(f"Total validation errors in final attempt: {error_count}")
                    print(f"\nAll invalid JSON attempts saved to output directory for debugging.")
                    print(f"Pipeline halted. Review the errors and update the prompt or model.")
                    print(f"{'='*60}\n")
                    raise ValueError(f"Pydantic validation failed after {max_validation_retries} attempts with {error_count} error(s).")
        
        # Ensure we have a valid resume before continuing
        if tailored_resume is None:
            raise ValueError("Resume validation failed - no valid resume generated")
        
        # Save validated resume JSON
        resume_json_path = os.path.join(output_dir, "Resume.json")
        save_json(resume_json_path, tailored_resume)
        print(f"✓ Resume JSON saved (Pydantic validation passed)\n")

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

        # STEP 3: Render Resume LaTeX using Jinja2 template
        print("STEP 3: Rendering resume LaTeX from template...")
        resume_latex = self.renderer.render_resume(tailored_resume)
        
        # Save resume LaTeX
        resume_tex_path = os.path.join(output_dir, "Resume.tex")
        with open(resume_tex_path, "w", encoding="utf-8") as f:
            f.write(resume_latex)
        print(f"✓ Resume LaTeX rendered and saved\n")

        # STEP 4: Render Cover Letter LaTeX using Jinja2 template
        print("STEP 4: Rendering cover letter LaTeX from template...")
        contact_info = tailored_resume.get("contact_info", {})
        cover_letter_latex = self.renderer.render_cover_letter(contact_info, cover_letter_text)
        
        # Save cover letter LaTeX
        cover_letter_tex_path = os.path.join(output_dir, "CoverLetter.tex")
        with open(cover_letter_tex_path, "w", encoding="utf-8") as f:
            f.write(cover_letter_latex)
        print(f"✓ Cover letter LaTeX rendered and saved\n")

        # Get name for final PDFs
        first_name = tailored_resume["contact_info"]["first_name"]
        last_name = tailored_resume["contact_info"]["last_name"]
        safe_first = first_name.replace(" ", "_")
        safe_last = last_name.replace(" ", "_")
        safe_company = company_name.replace(" ", "_")

        # STEP 5: Compile Resume PDF
        print("STEP 5: Compiling resume PDF...")
        resume_pdf = compile_latex_to_pdf(resume_tex_path, output_dir, "resume")
        
        # Rename to final name
        final_resume_name = f"{safe_first}_{safe_last}_{safe_company}_{job_id}_Resume.pdf"
        final_resume_path = os.path.join(output_dir, final_resume_name)
        shutil.move(resume_pdf, final_resume_path)
        print(f"✓ Resume PDF: {final_resume_name}\n")

        # STEP 6: Compile Cover Letter PDF
        print("STEP 6: Compiling cover letter PDF...")
        cover_letter_pdf = compile_latex_to_pdf(cover_letter_tex_path, output_dir, "cover_letter")
        
        # Rename to final name
        final_cover_letter_name = f"{safe_first}_{safe_last}_{safe_company}_{job_id}_Cover_Letter.pdf"
        final_cover_letter_path = os.path.join(output_dir, final_cover_letter_name)
        shutil.move(cover_letter_pdf, final_cover_letter_path)
        print(f"✓ Cover Letter PDF: {final_cover_letter_name}\n")

        # STEP 7: Create Referral LaTeX files
        print("STEP 7: Creating referral LaTeX files...")
        
        # Build referral contact info (same name, but referral email/phone)
        referral_contact = {
            "first_name": contact_info.get("first_name"),
            "last_name": contact_info.get("last_name"),
            "phone": self.referral_phone,
            "email": self.referral_email,
            "location": contact_info.get("location"),
            "linkedin_url": contact_info.get("linkedin_url"),
            "github_url": contact_info.get("github_url"),
            "portfolio_url": contact_info.get("portfolio_url")
        }
        
        # Render referral resume LaTeX
        referral_resume_latex = self.renderer.render_resume_with_referral(tailored_resume, referral_contact)
        referral_resume_tex_path = os.path.join(output_dir, "Referral_Resume.tex")
        with open(referral_resume_tex_path, "w", encoding="utf-8") as f:
            f.write(referral_resume_latex)
        
        # Render referral cover letter LaTeX
        referral_cover_letter_latex = self.renderer.render_cover_letter_with_referral(cover_letter_text, referral_contact)
        referral_cover_letter_tex_path = os.path.join(output_dir, "Referral_CoverLetter.tex")
        with open(referral_cover_letter_tex_path, "w", encoding="utf-8") as f:
            f.write(referral_cover_letter_latex)
        
        print(f"✓ Referral LaTeX files created\n")

        # STEP 8: Compile Referral Resume PDF
        print("STEP 8: Compiling referral resume PDF...")
        referral_resume_pdf = compile_latex_to_pdf(referral_resume_tex_path, output_dir, "resume")
        
        # Rename to final name
        final_referral_resume_name = f"Referral_{safe_first}_{safe_last}_{safe_company}_{job_id}_Resume.pdf"
        final_referral_resume_path = os.path.join(output_dir, final_referral_resume_name)
        shutil.move(referral_resume_pdf, final_referral_resume_path)
        print(f"✓ Referral Resume PDF: {final_referral_resume_name}\n")

        # STEP 9: Compile Referral Cover Letter PDF
        print("STEP 9: Compiling referral cover letter PDF...")
        referral_cover_letter_pdf = compile_latex_to_pdf(referral_cover_letter_tex_path, output_dir, "cover_letter")
        
        # Rename to final name
        final_referral_cover_letter_name = f"Referral_{safe_first}_{safe_last}_{safe_company}_{job_id}_Cover_Letter.pdf"
        final_referral_cover_letter_path = os.path.join(output_dir, final_referral_cover_letter_name)
        shutil.move(referral_cover_letter_pdf, final_referral_cover_letter_path)
        print(f"✓ Referral Cover Letter PDF: {final_referral_cover_letter_name}\n")

        # STEP 10: Clean up - move everything except 4 PDFs to debug/
        print("STEP 10: Cleaning up output directory...")
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
