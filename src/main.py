"""
Main pipeline for automating resume and cover letter generation.
"""

import os
import json
from dotenv import load_dotenv
import fastapi_poe as fp

from utils import (
    load_yaml,
    load_json,
    find_pending_job,
    update_job_status,
    create_output_directory,
    save_resume,
    save_cover_letter,
    save_latex_resume,
    save_latex_cover_letter,
    load_prompt_template,
)


class ResumeOptimizationPipeline:
    """Main pipeline for processing job applications."""

    def __init__(self):
        """Initialize the pipeline with configuration."""
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("POE_API_KEY")

        if not self.api_key:
            raise ValueError("POE_API_KEY not found in environment variables")

        # Load configuration
        self.config = load_json("config.json")

        # Get defaults
        defaults = self.config.get("defaults", {})

        # Resume generation config
        self.resume_config = self.config.get("resume_generation", {})
        self.resume_bot = self.resume_config.get("bot_name") or defaults.get("resume_bot")
        self.resume_thinking_budget = self.resume_config.get("thinking_budget") or defaults.get("resume_thinking_budget")
        self.resume_web_search = self.resume_config.get("web_search", True)

        # LaTeX conversion config
        self.latex_config = self.config.get("latex_conversion", {})
        self.latex_bot = self.latex_config.get("bot_name") or defaults.get("latex_bot")
        self.latex_thinking_budget = self.latex_config.get("thinking_budget") or defaults.get("latex_thinking_budget")
        self.latex_web_search = self.latex_config.get("web_search", False)

        # LaTeX verification config
        self.latex_verification_config = self.config.get("latex_verification", {})
        self.latex_verification_bot = self.latex_verification_config.get("bot_name")
        self.latex_verification_thinking_budget = self.latex_verification_config.get(
            "thinking_budget"
        )
        self.latex_verification_web_search = self.latex_verification_config.get(
            "web_search"
        )

        # LaTeX fix config
        self.latex_fix_config = self.config.get("latex_fix", {})
        self.latex_fix_bot = self.latex_fix_config.get("bot_name")
        self.latex_fix_thinking_budget = self.latex_fix_config.get("thinking_budget")
        self.latex_fix_web_search = self.latex_fix_config.get("web_search")
        self.latex_fix_max_retries = self.latex_fix_config.get("max_retries", 5)

        # Cover letter generation config
        self.cover_letter_config = self.config.get("cover_letter_generation", {})
        self.cover_letter_bot = self.cover_letter_config.get("bot_name") or defaults.get("cover_letter_bot")
        self.cover_letter_thinking_budget = self.cover_letter_config.get("thinking_budget") or defaults.get("cover_letter_thinking_budget")
        self.cover_letter_web_search = self.cover_letter_config.get("web_search", False)

        # Referral resume config
        self.referral_config = self.config.get("referral_resume", {})
        self.referral_email = self.referral_config.get("email", "srmanda.compsci@gmail.com")
        self.referral_phone = self.referral_config.get("phone", "+1 919-526-0631")

        # Global settings
        self.reasoning_trace = self.config.get("reasoning_trace", False)

        # Load master profile data
        self.master_resume = load_json("profile/master_resume.json")

        # Load prompt templates
        self.resume_prompt_template = load_prompt_template("generate_resume.txt")
        self.cover_letter_prompt_template = load_prompt_template(
            "generate_cover_letter.txt"
        )
        self.latex_conversion_prompt_template = load_prompt_template(
            "convert_resume_to_latex.txt"
        )
        self.cover_letter_latex_prompt_template = load_prompt_template(
            "convert_cover_letter_to_latex.txt"
        )
        self.latex_verification_prompt_template = load_prompt_template(
            "verify_latex_resume.txt"
        )
        self.latex_fix_prompt_template = load_prompt_template(
            "fix_latex_resume.txt"
        )

    async def call_poe_api(
        self, prompt: str, bot_name: str, max_retries: int = 3
    ) -> str:
        """Call the Poe API with retry logic and exponential backoff."""
        import asyncio

        for attempt in range(max_retries):
            try:
                print(
                    f"🔍 Calling {bot_name} API (attempt {attempt + 1}/{max_retries})..."
                )

                response_text = ""
                async for partial in fp.get_bot_response(
                    messages=[fp.ProtocolMessage(role="user", content=prompt)],
                    bot_name=bot_name,
                    api_key=self.api_key,
                ):
                    response_text += partial.text

                return response_text

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ API call failed after {max_retries} attempts: {e}")
                    raise
                wait_time = 2**attempt
                print(f"⚠️  API error: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        return ""

    def build_resume_prompt(self, job_description: str, company_name: str) -> str:
        """Build the prompt for resume generation."""
        prompt = self.resume_prompt_template

        # Replace placeholders - use master resume directly (no modifications needed)
        prompt = prompt.replace("[JOB_DESCRIPTION]", f"```\n{job_description}\n```")
        prompt = prompt.replace(
            "[MASTER_RESUME_JSON]",
            f"```json\n{json.dumps(self.master_resume, indent=2)}\n```",
        )
        prompt = prompt.replace("[COMPANY_NAME]", company_name)

        return prompt

    def build_cover_letter_prompt(
        self,
        tailored_resume_json: dict,
        job_description: str,
        company_name: str,
    ) -> str:
        """Build the prompt for cover letter generation."""
        prompt = self.cover_letter_prompt_template

        # Replace placeholders
        prompt = prompt.replace(
            "[TAILORED_RESUME_JSON]",
            f"```json\n{json.dumps(tailored_resume_json, indent=2)}\n```",
        )
        prompt = prompt.replace("[JOB_DESCRIPTION]", f"```\n{job_description}\n```")
        prompt = prompt.replace("[COMPANY_NAME]", company_name)

        return prompt

    def build_latex_conversion_prompt(self, tailored_resume_json: dict) -> str:
        """Build the prompt for converting resume JSON to LaTeX."""
        prompt = self.latex_conversion_prompt_template

        # Replace placeholder with the tailored resume JSON
        prompt = prompt.replace(
            "[TAILORED_RESUME_JSON]",
            f"```json\n{json.dumps(tailored_resume_json, indent=2)}\n```",
        )

        return prompt

    def build_cover_letter_latex_prompt(self, contact_info: dict, cover_letter_text: str) -> str:
        """Build the prompt for converting cover letter text to LaTeX."""
        prompt = self.cover_letter_latex_prompt_template

        # Replace placeholders
        prompt = prompt.replace(
            "[CONTACT_INFO_JSON]",
            f"```json\n{json.dumps(contact_info, indent=2)}\n```",
        )
        prompt = prompt.replace("[COVER_LETTER_TEXT]", cover_letter_text)

        return prompt

    def build_latex_verification_prompt(self, latex_text: str, tailored_resume_json: dict) -> str:
        """Build the prompt for verifying LaTeX resume against tailored resume."""
        prompt = self.latex_verification_prompt_template

        # Replace placeholders - use TAILORED resume instead of master resume
        prompt = prompt.replace(
            "[MASTER_RESUME_JSON]",
            f"```json\n{json.dumps(tailored_resume_json, indent=2)}\n```",
        )
        prompt = prompt.replace(
            "[LATEX_RESUME]",
            f"```latex\n{latex_text}\n```",
        )

        return prompt

    def build_latex_fix_prompt(
        self, tailored_resume_json: dict, failed_latex: str, issues: list
    ) -> str:
        """Build the prompt for fixing LaTeX resume based on verification issues."""
        prompt = self.latex_fix_prompt_template

        # Filter to only include major and critical issues
        major_critical_issues = [
            issue
            for issue in issues
            if issue.get("severity") in ["major", "critical"]
        ]

        # Format issues for the prompt
        issues_text = ""
        if major_critical_issues:
            for i, issue in enumerate(major_critical_issues, 1):
                severity = issue.get("severity", "unknown")
                category = issue.get("category", "unknown")
                description = issue.get("description", "No description")
                location = issue.get("location", "Unknown location")

                issues_text += f"{i}. [{severity.upper()}] {category}\n"
                issues_text += f"   Description: {description}\n"
                issues_text += f"   Location: {location}\n\n"
        else:
            issues_text = "No major or critical issues found."

        # Replace placeholders
        prompt = prompt.replace(
            "[TAILORED_RESUME_JSON]",
            f"```json\n{json.dumps(tailored_resume_json, indent=2)}\n```",
        )
        prompt = prompt.replace(
            "[FAILED_LATEX]", f"```latex\n{failed_latex}\n```"
        )
        prompt = prompt.replace("[VERIFICATION_ISSUES]", issues_text)

        return prompt

    async def verify_and_fix_latex_resume(
        self, tailored_resume_json: dict, initial_latex_text: str
    ) -> tuple:
        """
        Verify LaTeX resume and attempt to fix issues if verification fails.
        Retries up to max_retries times.
        Returns (final_latex_text: str, verification_passed: bool, verification_result: dict)
        """
        latex_text = initial_latex_text
        max_retries = self.latex_fix_max_retries

        for attempt in range(1, max_retries + 1):
            # Verify the LaTeX
            verification_passed, verification_result = await self.verify_latex_resume(
                latex_text, tailored_resume_json
            )

            if verification_passed:
                print(f"✓ Verification passed on attempt {attempt}!")
                return latex_text, verification_passed, verification_result

            # Verification failed
            issues = verification_result.get("issues", [])

            # Check if there are any major/critical issues
            major_critical_issues = [
                issue
                for issue in issues
                if issue.get("severity") in ["major", "critical"]
            ]

            if not major_critical_issues:
                print(
                    f"✓ Only minor issues found on attempt {attempt}. Accepting LaTeX."
                )
                return latex_text, True, verification_result

            # We have major/critical issues and haven't exhausted retries
            if attempt < max_retries:
                print(
                    f"\n🔧 Attempt {attempt}/{max_retries}: Found {len(major_critical_issues)} major/critical issues. Attempting to fix..."
                )

                # Build fix prompt
                fix_prompt = self.build_latex_fix_prompt(
                    tailored_resume_json, latex_text, issues
                )

                # Call API to fix the LaTeX
                print(f"🔍 Calling {self.latex_fix_bot} to fix LaTeX issues...")
                fix_response = await self.call_poe_api(fix_prompt, self.latex_fix_bot)

                # Extract fixed LaTeX using the helper method
                latex_text = self.extract_latex_from_response(fix_response)

                print(f"✓ Fixed LaTeX received. Verifying again...")
            else:
                # Exhausted all retries
                print(
                    f"\n❌ Failed to fix LaTeX after {max_retries} attempts. {len(major_critical_issues)} major/critical issues remain."
                )
                return latex_text, False, verification_result

        # Should not reach here, but return the last state
        return latex_text, False, verification_result

    async def verify_latex_resume(self, latex_text: str, tailored_resume_json: dict) -> tuple:
        """
        Verify the LaTeX resume against the tailored resume.
        Returns (verification_passed: bool, verification_result: dict)
        """
        print(
            f"\n🔍 Step 4c: Verifying LaTeX resume using {self.latex_verification_bot}..."
        )

        verification_prompt = self.build_latex_verification_prompt(latex_text, tailored_resume_json)
        verification_response = await self.call_poe_api(
            verification_prompt, self.latex_verification_bot
        )

        # Extract verification result JSON
        verification_result = self.extract_json_from_response(verification_response)

        # Check if verification passed
        verification_passed = verification_result.get("verification_passed", False)
        quality_score = verification_result.get("quality_score", 0)
        issues = verification_result.get("issues", [])
        summary = verification_result.get("summary", "No summary provided")

        print(f"\n{'='*60}")
        print(f"VERIFICATION RESULTS")
        print(f"{'='*60}")
        print(f"Status: {'✓ PASSED' if verification_passed else '✗ FAILED'}")
        print(f"Quality Score: {quality_score}/100")
        print(f"Summary: {summary}")

        if issues:
            print(f"\nIssues Found ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                severity = issue.get("severity", "unknown")
                category = issue.get("category", "unknown")
                description = issue.get("description", "No description")
                location = issue.get("location", "Unknown location")

                severity_emoji = {"critical": "🔴", "major": "🟡", "minor": "🟢"}.get(
                    severity, "⚪"
                )

                print(f"\n{i}. {severity_emoji} [{severity.upper()}] {category}")
                print(f"   Description: {description}")
                print(f"   Location: {location}")
        else:
            print("\nNo issues found!")

        print(f"{'='*60}\n")

        return verification_passed, verification_result

    def validate_resume_json(self, resume: dict) -> bool:
        """Validate resume has required fields."""
        required_keys = [
            "contact_info",
            "work_experience",
            "skills",
        ]
        missing_keys = [key for key in required_keys if key not in resume]

        if missing_keys:
            print(f"⚠️  Warning: Resume JSON missing required fields: {missing_keys}")
            return False
        return True

    def extract_json_from_response(self, response: str) -> dict:
        """Extract JSON from the API response."""
        # Try to find JSON in code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
        else:
            # Assume the entire response is JSON
            json_str = response.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            print(f"Response: {response[:500]}...")
            raise

    def extract_latex_from_response(self, response: str) -> str:
        """
        Extract LaTeX code from the API response, filtering out reasoning traces.
        Handles responses with markdown code blocks and reasoning traces.
        """
        # First, try to extract from code blocks
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
        
        # If no code blocks found, try to find \documentclass directly
        if "\\documentclass" not in latex_text:
            # Look for \documentclass in the original response
            doc_start = response.find("\\documentclass")
            if doc_start != -1:
                latex_text = response[doc_start:].strip()
        
        # Now filter out reasoning traces if reasoning_trace is disabled
        if not self.reasoning_trace and latex_text:
            # Find the start of actual LaTeX content
            doc_start = latex_text.find("\\documentclass")
            
            if doc_start != -1:
                # Extract everything from \documentclass onwards
                latex_text = latex_text[doc_start:].strip()
            else:
                # If no \documentclass found, filter line by line
                lines = latex_text.split("\n")
                filtered_lines = []
                
                for line in lines:
                    # Skip lines that are clearly thinking traces
                    if line.strip().startswith(">"):
                        continue
                    if "**Thinking" in line or "*Thinking*" in line or "Thinking..." in line:
                        continue
                    if line.strip().startswith("**") and "**" in line[2:]:
                        # Skip markdown headers that are part of thinking
                        continue
                    
                    filtered_lines.append(line)
                
                if filtered_lines:
                    latex_text = "\n".join(filtered_lines)
        
        return latex_text.strip()

    async def process_job(self, job: dict) -> None:
        """Process a single job application."""
        job_id = job.get("job_id")
        job_title = job.get("job_title")
        company_name = job.get("company_name")
        job_description = job.get("job_description")

        print(f"\n{'='*60}")
        print(f"📋 Processing: {job_title} at {company_name}")
        print(f"🆔 Job ID: {job_id}")
        print(f"{'='*60}\n")

        # Step 1: Generate tailored resume
        print(f"\n📝 Step 1: Generating tailored resume using {self.resume_bot}...")
        resume_prompt = self.build_resume_prompt(job_description, company_name)
        resume_response = await self.call_poe_api(resume_prompt, self.resume_bot)
        tailored_resume = self.extract_json_from_response(resume_response)

        # Validate the resume JSON
        if self.validate_resume_json(tailored_resume):
            print("✓ Resume generated successfully!")
        else:
            print("⚠️  Resume generated but may be incomplete")

        # Step 2: Generate cover letter
        print(f"\n✉️  Step 2: Generating cover letter using {self.cover_letter_bot}...")
        cover_letter_prompt = self.build_cover_letter_prompt(
            tailored_resume, job_description, company_name
        )
        cover_letter_response = await self.call_poe_api(
            cover_letter_prompt, self.cover_letter_bot
        )

        # Filter reasoning traces if disabled
        cover_letter_text = cover_letter_response.strip()
        if not self.reasoning_trace:
            # Remove lines starting with ">" (reasoning traces) and "*Thinking...*"
            lines = cover_letter_text.split("\n")
            filtered_lines = [
                line
                for line in lines
                if not line.strip().startswith(">")
                and "*Thinking*" not in line
                and "Thinking..." not in line
            ]
            cover_letter_text = "\n".join(filtered_lines).strip()

        print("✓ Cover letter generated successfully!")

        # Step 3: Create output directory and save files
        print("\n📁 Step 3: Creating output directory and saving initial files...")
        output_dir = create_output_directory(job_id, job_title, company_name)
        print(f"Output directory: {output_dir}")

        resume_path = save_resume(output_dir, tailored_resume, job_title, company_name)
        print(f"✓ Resume JSON saved: {resume_path}")

        cover_letter_path = save_cover_letter(
            output_dir,
            cover_letter_text,
            job_title,
            company_name,
        )
        print(f"✓ Cover letter TXT saved: {cover_letter_path}")

        # Step 4: Convert resume JSON to LaTeX
        print(f"\n📄 Step 4: Converting resume to LaTeX using {self.latex_bot}...")
        latex_prompt = self.build_latex_conversion_prompt(tailored_resume)
        latex_response = await self.call_poe_api(latex_prompt, self.latex_bot)

        # Extract LaTeX from response using the helper method
        latex_text = self.extract_latex_from_response(latex_response)

        # Step 5: Verify and fix LaTeX resume (with retry loop)
        print(f"\n🔍 Step 5: Verifying LaTeX resume (with auto-fix retry)...")
        latex_text, verification_passed, verification_result = await self.verify_and_fix_latex_resume(
            tailored_resume, latex_text
        )

        if not verification_passed:
            print("\n" + "=" * 60)
            print("❌ VERIFICATION FAILED AFTER ALL RETRIES")
            print("=" * 60)
            print(
                "The LaTeX resume still contains major/critical issues after all fix attempts."
            )
            print("The process has been halted. Please review the issues above.")
            print("=" * 60 + "\n")
            raise ValueError(
                "LaTeX verification failed after all retry attempts. Resume contains critical issues that must be addressed."
            )

        # Verification passed - save the LaTeX file
        latex_path = save_latex_resume(output_dir, latex_text, job_title, company_name)
        print(f"✓ LaTeX resume saved: {latex_path}")

        # Step 6: Compile LaTeX to PDF (Regular Resume)
        print(f"\n📄 Step 6: Compiling resume LaTeX to PDF...")
        try:
            from utils import compile_latex_to_pdf

            resume_pdf_path = compile_latex_to_pdf(latex_path, output_dir)
            print(f"✓ Resume PDF generated: {resume_pdf_path}")
        except Exception as e:
            print(f"\n❌ Resume LaTeX compilation failed: {e}")
            print(
                "The process has been halted. Please fix the LaTeX errors and try again."
            )
            raise

        # Step 7: Convert cover letter to LaTeX
        print(f"\n📄 Step 7: Converting cover letter to LaTeX using {self.latex_bot}...")
        contact_info = tailored_resume.get("contact_info", {})
        cover_letter_latex_prompt = self.build_cover_letter_latex_prompt(
            contact_info, cover_letter_text
        )
        cover_letter_latex_response = await self.call_poe_api(
            cover_letter_latex_prompt, self.latex_bot
        )

        # Extract LaTeX from response
        cover_letter_latex = self.extract_latex_from_response(cover_letter_latex_response)

        # Save cover letter LaTeX
        cover_letter_latex_path = save_latex_cover_letter(
            output_dir, cover_letter_latex, job_title, company_name
        )
        print(f"✓ Cover letter LaTeX saved: {cover_letter_latex_path}")

        # Step 8: Compile cover letter LaTeX to PDF
        print(f"\n📄 Step 8: Compiling cover letter LaTeX to PDF...")
        try:
            from utils import compile_latex_to_pdf
            import shutil

            # Ensure resume.cls is available in output directory for cover letter compilation
            resume_cls_source = "resume.cls"
            resume_cls_dest = os.path.join(output_dir, "resume.cls")
            
            if not os.path.exists(resume_cls_dest):
                if not os.path.exists(resume_cls_source):
                    raise FileNotFoundError(
                        f"resume.cls not found in the project root. "
                        f"Please ensure resume.cls exists at: {resume_cls_source}"
                    )
                shutil.copy2(resume_cls_source, resume_cls_dest)
                print("✓ resume.cls copied to output directory")

            cover_letter_pdf_path = compile_latex_to_pdf(
                cover_letter_latex_path, output_dir
            )
            print(f"✓ Cover letter PDF generated: {cover_letter_pdf_path}")
        except Exception as e:
            print(f"\n❌ Cover letter LaTeX compilation failed: {e}")
            print(
                "The process has been halted. Please fix the LaTeX errors and try again."
            )
            raise

        # Step 9: Generate Referral Resume Version
        print(f"\n📄 Step 9: Generating Referral Resume Version...")
        try:
            from utils import create_referral_latex, save_referral_latex_resume, compile_latex_to_pdf

            # Create referral resume LaTeX using configured contact information
            referral_resume_latex = create_referral_latex(
                latex_text, self.referral_email, self.referral_phone, "resume"
            )

            # Save referral resume LaTeX using the utility function
            referral_resume_latex_path = save_referral_latex_resume(
                output_dir, referral_resume_latex, job_title, company_name
            )
            print(f"✓ Referral resume LaTeX saved: {referral_resume_latex_path}")

            # Compile referral resume LaTeX to PDF
            referral_resume_pdf_path = compile_latex_to_pdf(referral_resume_latex_path, output_dir)
            print(f"✓ Referral Resume PDF generated: {referral_resume_pdf_path}")

        except Exception as e:
            print(f"\n❌ Referral resume generation failed: {e}")
            print("Continuing without referral resume...")

        # Step 10: Generate Referral Cover Letter Version
        print(f"\n📄 Step 10: Generating Referral Cover Letter Version...")
        try:
            from utils import create_referral_latex, save_referral_latex_cover_letter, compile_latex_to_pdf

            # Create referral cover letter LaTeX using configured contact information
            referral_cover_letter_latex = create_referral_latex(
                cover_letter_latex, self.referral_email, self.referral_phone, "cover_letter"
            )

            # Save referral cover letter LaTeX using the utility function
            referral_cover_letter_latex_path = save_referral_latex_cover_letter(
                output_dir, referral_cover_letter_latex, job_title, company_name
            )
            print(f"✓ Referral cover letter LaTeX saved: {referral_cover_letter_latex_path}")

            # Compile referral cover letter LaTeX to PDF
            referral_cover_letter_pdf_path = compile_latex_to_pdf(
                referral_cover_letter_latex_path, output_dir
            )
            print(f"✓ Referral Cover Letter PDF generated: {referral_cover_letter_pdf_path}")

        except Exception as e:
            print(f"\n❌ Referral cover letter generation failed: {e}")
            print("Continuing without referral cover letter...")

        # Step 11: Organize files and rename with proper convention
        print(f"\n📁 Step 11: Organizing output files...")
        try:
            from utils import organize_output_files

            first_name = tailored_resume["contact_info"]["first_name"]
            last_name = tailored_resume["contact_info"]["last_name"]
            organize_output_files(
                output_dir, first_name, last_name, company_name, job_id
            )
            print(f"✓ Files organized successfully!")
        except Exception as e:
            print(f"\n⚠️  File organization failed: {e}")
            print("Files were generated but may not be in the expected structure.")

        # Step 12: Update job status
        print("\n📝 Step 12: Updating job status...")
        update_job_status("applications.yaml", job_id, "processed")
        print("Job status updated to 'processed'")

        print(f"\n{'='*60}")
        print(f"✓ Successfully processed: {job_title} at {company_name}")
        print(f"{'='*60}\n")

    async def run(self) -> None:
        """Run the pipeline to process pending jobs."""
        print("\n" + "=" * 60)
        print("RESUME OPTIMIZATION PIPELINE")
        print("=" * 60 + "\n")

        # Load applications
        applications = load_yaml("applications.yaml")

        # Find pending job
        pending_job = find_pending_job(applications)

        if not pending_job:
            print("No pending jobs found. All jobs are processed!")
            return

        # Process the pending job
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
