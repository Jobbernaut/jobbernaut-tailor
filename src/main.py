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
    select_best_cover_letter_point,
    create_output_directory,
    save_resume,
    save_cover_letter,
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

        # Resume generation config
        self.resume_config = self.config.get("resume_generation", {})
        self.resume_bot = self.resume_config.get("bot_name", "Gemini-2.5-Pro")
        self.resume_thinking_budget = self.resume_config.get("thinking_budget", "4096")
        self.resume_web_search = self.resume_config.get("web_search", True)

        # Cover letter generation config
        self.cover_letter_config = self.config.get("cover_letter_generation", {})
        self.cover_letter_bot = self.cover_letter_config.get(
            "bot_name", "Claude-3.7-Sonnet"
        )
        self.cover_letter_thinking_budget = self.cover_letter_config.get(
            "thinking_budget", "2048"
        )
        self.cover_letter_web_search = self.cover_letter_config.get("web_search", False)

        # Global settings
        self.reasoning_trace = self.config.get("reasoning_trace", False)
        self.dry_run = self.config.get("dry_run", False)

        # Load master profile data
        self.master_resume = load_json("profile/master_resume.json")
        self.cover_letter_points_data = load_json(
            "profile/master_cover_letter_points.json"
        )
        self.cover_letter_points = self.cover_letter_points_data.get(
            "cover_letter_points", []
        )

        # Load prompt templates
        self.resume_prompt_template = load_prompt_template("generate_resume.txt")
        self.cover_letter_prompt_template = load_prompt_template(
            "generate_cover_letter.txt"
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

        # Replace placeholders
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
        best_point: dict,
        default_point: dict,
    ) -> str:
        """Build the prompt for cover letter generation."""
        prompt = self.cover_letter_prompt_template

        # Combine both points - default point is mandatory, best point is optional
        personal_notes = []

        if default_point:
            personal_notes.append(default_point.get("point_text", ""))

        if best_point and best_point != default_point:
            personal_notes.append(best_point.get("point_text", ""))

        combined_notes = "\n\n".join(filter(None, personal_notes))

        # Replace placeholders
        prompt = prompt.replace(
            "[TAILORED_RESUME_JSON]",
            f"```json\n{json.dumps(tailored_resume_json, indent=2)}\n```",
        )
        prompt = prompt.replace("[JOB_DESCRIPTION]", f"```\n{job_description}\n```")
        prompt = prompt.replace("[COMPANY_NAME]", company_name)
        prompt = prompt.replace("[HIRING_MANAGER_NAME]", "N/A")
        prompt = prompt.replace("[USER_PERSONAL_NOTE]", combined_notes)

        return prompt

    def validate_resume_json(self, resume: dict) -> bool:
        """Validate resume has required fields."""
        required_keys = [
            "contact_info",
            "professional_summaries",
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

        # Step 1: Select best cover letter point
        print("📌 Step 1: Selecting best cover letter point...")
        best_point, default_point = select_best_cover_letter_point(
            job_description, self.cover_letter_points
        )
        print(f"Best point: {best_point.get('id') if best_point else 'None'}")
        print(f"Default point: {default_point.get('id') if default_point else 'None'}")

        # Step 2: Generate tailored resume
        print(f"\n📝 Step 2: Generating tailored resume using {self.resume_bot}...")
        resume_prompt = self.build_resume_prompt(job_description, company_name)
        resume_response = await self.call_poe_api(resume_prompt, self.resume_bot)
        tailored_resume = self.extract_json_from_response(resume_response)

        # Validate the resume JSON
        if self.validate_resume_json(tailored_resume):
            print("✓ Resume generated successfully!")
        else:
            print("⚠️  Resume generated but may be incomplete")

        # Step 3: Generate cover letter
        print(f"\n✉️  Step 3: Generating cover letter using {self.cover_letter_bot}...")
        cover_letter_prompt = self.build_cover_letter_prompt(
            tailored_resume, job_description, company_name, best_point, default_point
        )
        cover_letter_response = await self.call_poe_api(
            cover_letter_prompt, self.cover_letter_bot
        )

        # Filter reasoning traces if disabled
        cover_letter_text = cover_letter_response.strip()
        if not self.reasoning_trace:
            # Remove lines starting with ">" (reasoning traces)
            lines = cover_letter_text.split("\n")
            filtered_lines = [
                line for line in lines if not line.strip().startswith(">")
            ]
            cover_letter_text = "\n".join(filtered_lines).strip()

        print("Cover letter generated successfully!")

        # Step 4: Create output directory and save files
        print("\nStep 4: Saving outputs...")
        output_dir = create_output_directory(job_id, job_title, company_name)
        print(f"Output directory: {output_dir}")

        resume_path = save_resume(output_dir, tailored_resume, job_title, company_name)
        print(f"Resume saved: {resume_path}")

        cover_letter_path = save_cover_letter(
            output_dir, cover_letter_text, job_title, company_name
        )
        print(f"Cover letter saved: {cover_letter_path}")

        # Step 5: Update job status
        print("\nStep 5: Updating job status...")
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
