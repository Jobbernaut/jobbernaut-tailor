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
from models import TailoredResume, JobResonanceAnalysis, CompanyResearch, StorytellingArc


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
        
        # Intelligence step bot configurations
        intelligence_config = self.config.get("intelligence_steps", {})
        self.job_resonance_bot = intelligence_config.get("job_resonance_analysis", {}).get("bot_name") or self.resume_bot
        self.company_research_bot = intelligence_config.get("company_research", {}).get("bot_name") or self.resume_bot
        self.storytelling_arc_bot = intelligence_config.get("storytelling_arc", {}).get("bot_name") or self.resume_bot

        # Referral contact info
        referral_config = self.config.get("referral_resume", {})
        self.referral_email = referral_config.get("email", "srmanda.compsci@gmail.com")
        self.referral_phone = referral_config.get("phone", "+1 919-526-0631")

        # Load master resume
        self.master_resume = load_json("profile/master_resume.json")

        # Load prompt templates
        self.resume_prompt_template = load_prompt_template("generate_resume.txt")
        self.cover_letter_prompt_template = load_prompt_template("generate_cover_letter.txt")
        
        # Load humanization configuration
        humanization_config = self.config.get("humanization", {})
        self.humanization_enabled = humanization_config.get("enabled", False)
        self.humanization_level = humanization_config.get("level", "medium")
        self.humanization_targets = humanization_config.get("apply_to", ["resume", "cover_letter"])
        
        # Load humanization prompt if enabled
        self.humanization_prompt = None
        if self.humanization_enabled:
            self.humanization_prompt = self._load_humanization_prompt(self.humanization_level)
            print(f"✓ Humanization enabled: {self.humanization_level} level")
            print(f"  Applying to: {', '.join(self.humanization_targets)}\n")
        
        # Initialize template renderer
        self.renderer = TemplateRenderer()

    def _load_humanization_prompt(self, level: str) -> str:
        """
        Load the humanization prompt for the specified level.
        
        Args:
            level: The humanization level (low, medium, high)
            
        Returns:
            The humanization prompt text
        """
        valid_levels = ["low", "medium", "high"]
        if level not in valid_levels:
            print(f"⚠️  Invalid humanization level '{level}', defaulting to 'medium'")
            level = "medium"
        
        prompt_file = f"humanization_{level}.txt"
        try:
            humanization_prompt = load_prompt_template(prompt_file)
            print(f"  Loaded humanization prompt: {prompt_file}")
            return humanization_prompt
        except FileNotFoundError:
            print(f"⚠️  Humanization prompt file not found: {prompt_file}")
            print(f"  Humanization will be disabled for this run")
            return None
    
    def _apply_humanization(self, prompt: str, target: str) -> str:
        """
        Apply humanization instructions to a prompt if enabled and applicable.
        
        Args:
            prompt: The base prompt to enhance
            target: The target type ('resume' or 'cover_letter')
            
        Returns:
            The prompt with humanization instructions appended (if applicable)
        """
        # Check if humanization is enabled and applies to this target
        if not self.humanization_enabled:
            return prompt
        
        if target not in self.humanization_targets:
            return prompt
        
        if not self.humanization_prompt:
            return prompt
        
        # Append humanization instructions to the prompt
        separator = "\n\n" + "="*80 + "\n"
        humanized_prompt = prompt + separator + self.humanization_prompt + separator
        
        return humanized_prompt
    
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

    def _validate_job_inputs(self, job: dict) -> None:
        """
        Validate job inputs before processing.
        
        Args:
            job: The job dictionary to validate
            
        Raises:
            ValueError: If any input is invalid
        """
        job_id = job.get("job_id")
        job_title = job.get("job_title")
        company_name = job.get("company_name")
        job_description = job.get("job_description")
        
        # Validate job_id
        if not job_id or not isinstance(job_id, str) or len(job_id.strip()) == 0:
            raise ValueError("job_id is required and must be a non-empty string")
        
        # Validate job_title
        if not job_title or not isinstance(job_title, str):
            raise ValueError("job_title is required and must be a string")
        if len(job_title.strip()) < 3:
            raise ValueError(f"job_title must be at least 3 characters, got: '{job_title}'")
        if len(job_title) > 200:
            raise ValueError(f"job_title is too long (max 200 chars), got {len(job_title)} chars")
        
        # Validate company_name
        if not company_name or not isinstance(company_name, str):
            raise ValueError("company_name is required and must be a string")
        if len(company_name.strip()) < 2:
            raise ValueError(f"company_name must be at least 2 characters, got: '{company_name}'")
        if len(company_name) > 100:
            raise ValueError(f"company_name is too long (max 100 chars), got {len(company_name)} chars")
        
        # Validate job_description
        if not job_description or not isinstance(job_description, str):
            raise ValueError("job_description is required and must be a string")
        if len(job_description.strip()) < 100:
            raise ValueError(f"job_description is too short (min 100 chars), got {len(job_description.strip())} chars")
        if len(job_description) > 50000:
            raise ValueError(f"job_description is too long (max 50K chars), got {len(job_description)} chars")
        
        print(f"✓ Job inputs validated successfully")
        print(f"  - Job ID: {job_id}")
        print(f"  - Title: {job_title[:50]}{'...' if len(job_title) > 50 else ''}")
        print(f"  - Company: {company_name}")
        print(f"  - Description: {len(job_description)} characters\n")
    
    def _validate_intelligence_output(self, data: dict, step_name: str, model_class) -> None:
        """
        Validate intelligence output has meaningful content.
        
        Args:
            data: The validated Pydantic model data
            step_name: Name of the intelligence step for logging
            model_class: The Pydantic model class for type checking
            
        Raises:
            ValueError: If output doesn't meet quality thresholds
        """
        if model_class == JobResonanceAnalysis:
            # Validate emotional_keywords
            if len(data.get('emotional_keywords', [])) < 3:
                raise ValueError(f"{step_name}: emotional_keywords must have at least 3 items, got {len(data.get('emotional_keywords', []))}")
            if len(data.get('emotional_keywords', [])) > 15:
                raise ValueError(f"{step_name}: emotional_keywords has too many items (max 15), got {len(data.get('emotional_keywords', []))}")
            
            # Validate cultural_values
            if len(data.get('cultural_values', [])) < 2:
                raise ValueError(f"{step_name}: cultural_values must have at least 2 items, got {len(data.get('cultural_values', []))}")
            
            # Validate hidden_requirements
            if len(data.get('hidden_requirements', [])) < 2:
                raise ValueError(f"{step_name}: hidden_requirements must have at least 2 items, got {len(data.get('hidden_requirements', []))}")
            
            # Validate power_verbs
            if len(data.get('power_verbs', [])) < 3:
                raise ValueError(f"{step_name}: power_verbs must have at least 3 items, got {len(data.get('power_verbs', []))}")
            
            # Validate technical_keywords
            if len(data.get('technical_keywords', [])) < 3:
                raise ValueError(f"{step_name}: technical_keywords must have at least 3 items, got {len(data.get('technical_keywords', []))}")
            
            # Check for empty strings
            for field in ['emotional_keywords', 'cultural_values', 'hidden_requirements', 'power_verbs', 'technical_keywords']:
                if any(not item or not item.strip() for item in data.get(field, [])):
                    raise ValueError(f"{step_name}: {field} contains empty strings")
        
        elif model_class == CompanyResearch:
            # Validate mission_statement
            mission = data.get('mission_statement', '')
            if len(mission.strip()) < 20:
                raise ValueError(f"{step_name}: mission_statement too short (min 20 chars), got {len(mission.strip())} chars")
            
            # Validate core_values
            if len(data.get('core_values', [])) < 2:
                raise ValueError(f"{step_name}: core_values must have at least 2 items, got {len(data.get('core_values', []))}")
            if len(data.get('core_values', [])) > 10:
                raise ValueError(f"{step_name}: core_values has too many items (max 10), got {len(data.get('core_values', []))}")
            
            # Check for empty strings in arrays
            for field in ['core_values', 'tech_stack', 'culture_keywords']:
                if any(not item or not item.strip() for item in data.get(field, [])):
                    raise ValueError(f"{step_name}: {field} contains empty strings")
        
        elif model_class == StorytellingArc:
            # Validate hook
            hook = data.get('hook', '')
            if len(hook.strip()) < 50:
                raise ValueError(f"{step_name}: hook too short (min 50 chars), got {len(hook.strip())} chars")
            
            # Validate bridge
            bridge = data.get('bridge', '')
            if len(bridge.strip()) < 50:
                raise ValueError(f"{step_name}: bridge too short (min 50 chars), got {len(bridge.strip())} chars")
            
            # Validate vision
            vision = data.get('vision', '')
            if len(vision.strip()) < 50:
                raise ValueError(f"{step_name}: vision too short (min 50 chars), got {len(vision.strip())} chars")
            
            # Validate call_to_action
            cta = data.get('call_to_action', '')
            if len(cta.strip()) < 20:
                raise ValueError(f"{step_name}: call_to_action too short (min 20 chars), got {len(cta.strip())} chars")
            
            # Validate proof_points
            proof_points = data.get('proof_points', [])
            if len(proof_points) < 2:
                raise ValueError(f"{step_name}: proof_points must have at least 2 items, got {len(proof_points)}")
            if len(proof_points) > 3:
                raise ValueError(f"{step_name}: proof_points must have at most 3 items, got {len(proof_points)}")
            
            # Check proof_points content
            for i, point in enumerate(proof_points):
                if len(point.strip()) < 30:
                    raise ValueError(f"{step_name}: proof_points[{i}] too short (min 30 chars), got {len(point.strip())} chars")
        
        print(f"  ✓ {step_name} output validation passed")
    
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
            
            # Add specific guidance based on error 'type' codes for robust categorization
            if 'graduation_date' in field_path and error_type == 'value_error.missing':
                error_detail += "\n   💡 FIX: Use 'graduation_date' NOT 'end_date' in education entries"
                missing_errors.append(error_detail)
            elif 'technologies' in field_path and error_type == 'type_error.list':
                error_detail += '\n   💡 FIX: Format as array: ["Tech1", "Tech2", "Tech3"] NOT "Tech1, Tech2, Tech3"'
                error_detail += '\n   💡 EXAMPLE: "technologies": ["Python", "PyTorch", "Scikit-learn"]'
                type_errors.append(error_detail)
            elif error_type == 'value_error.missing':
                error_detail += f"\n   💡 FIX: This field is REQUIRED and cannot be omitted"
                missing_errors.append(error_detail)
            elif error_type.startswith('type_error'):
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

    async def _call_intelligence_step_with_retry(
        self, 
        prompt_template_name: str,
        replacements: dict,
        model_class,
        step_name: str,
        output_dir: str,
        output_filename_prefix: str,
        bot_name: str,
        max_retries: int = 3
    ) -> dict:
        """
        Generic retry wrapper for intelligence steps with validation and self-healing.
        
        Args:
            prompt_template_name: Name of the prompt template file
            replacements: Dictionary of placeholder -> value replacements
            model_class: Pydantic model class for validation
            step_name: Human-readable step name for logging
            output_dir: Directory to save outputs
            output_filename_prefix: Prefix for output files (e.g., "Job_Resonance_Analysis")
            bot_name: Name of the bot to use for API calls
            max_retries: Maximum retry attempts (default: 3)
            
        Returns:
            Validated dictionary from Pydantic model
            
        Raises:
            ValueError: If all retries fail
        """
        # Load prompt template
        prompt_template = load_prompt_template(prompt_template_name)
        base_prompt = prompt_template
        for placeholder, value in replacements.items():
            base_prompt = base_prompt.replace(placeholder, value)
        
        current_prompt = base_prompt
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            print(f"  Attempt {attempt}/{max_retries}...")
            
            try:
                # Call API
                response = await self.call_poe_api(current_prompt, bot_name)
                
                # Save raw response
                raw_path = os.path.join(output_dir, f"{output_filename_prefix}_Raw_Attempt_{attempt}.txt")
                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(response)
                print(f"    Raw response saved: {output_filename_prefix}_Raw_Attempt_{attempt}.txt")
                
                # Extract JSON
                try:
                    data = self.extract_json_from_response(response)
                    print(f"    ✓ JSON extraction successful")
                except json.JSONDecodeError as e:
                    print(f"    ✗ JSON extraction failed: {str(e)}")
                    if attempt < max_retries:
                        error_feedback = f"\n\n{'='*80}\n# JSON PARSING ERROR\n{'='*80}\n\nThe previous response was not valid JSON.\nError: {str(e)}\n\nPlease ensure your response contains ONLY valid JSON with no additional text.\n{'='*80}\n"
                        current_prompt = base_prompt + error_feedback
                        continue
                    else:
                        raise ValueError(f"{step_name} failed: Invalid JSON after {max_retries} attempts")
                
                # Validate with Pydantic
                print(f"    Validating with Pydantic...")
                try:
                    validated_model = model_class(**data)
                    result = validated_model.model_dump()
                    print(f"    ✓ Pydantic validation passed")
                except ValidationError as e:
                    print(f"    ✗ Pydantic validation failed: {len(e.errors())} error(s)")
                    if attempt < max_retries:
                        error_feedback = self._build_error_feedback(e)
                        current_prompt = base_prompt + error_feedback
                        continue
                    else:
                        raise ValueError(f"{step_name} failed: Pydantic validation failed after {max_retries} attempts")
                
                # Validate output quality
                print(f"    Validating output quality...")
                try:
                    self._validate_intelligence_output(result, step_name, model_class)
                except ValueError as e:
                    print(f"    ✗ Quality validation failed: {str(e)}")
                    if attempt < max_retries:
                        error_feedback = f"\n\n{'='*80}\n# OUTPUT QUALITY ERROR\n{'='*80}\n\n{str(e)}\n\nPlease provide more detailed and meaningful content that meets the quality thresholds.\n{'='*80}\n"
                        current_prompt = base_prompt + error_feedback
                        continue
                    else:
                        raise ValueError(f"{step_name} failed: Quality validation failed after {max_retries} attempts")
                
                # Success! Save validated JSON
                json_path = os.path.join(output_dir, f"{output_filename_prefix}.json")
                save_json(json_path, result)
                print(f"    ✓ {step_name} complete (attempt {attempt})")
                
                return result
                
            except Exception as e:
                last_error = e
                print(f"    ✗ Attempt {attempt} failed: {str(e)}")
                if attempt >= max_retries:
                    raise ValueError(f"{step_name} failed after {max_retries} attempts: {str(last_error)}")
        
        # Should never reach here
        raise ValueError(f"{step_name} failed after {max_retries} attempts: {str(last_error)}")

    async def analyze_job_resonance(self, job_description: str, company_name: str, output_dir: str) -> dict:
        """
        INTELLIGENCE STEP 1: Analyze job description for emotional keywords and hidden requirements.
        
        Args:
            job_description: The job description text
            company_name: The company name
            output_dir: Directory to save analysis results
            
        Returns:
            Dictionary containing JobResonanceAnalysis data
        """
        print("INTELLIGENCE STEP 1: Analyzing job resonance...")
        
        result = await self._call_intelligence_step_with_retry(
            prompt_template_name="analyze_job_resonance.txt",
            replacements={
                "[JOB_DESCRIPTION]": job_description,
                "[COMPANY_NAME]": company_name
            },
            model_class=JobResonanceAnalysis,
            step_name="Job Resonance Analysis",
            output_dir=output_dir,
            output_filename_prefix="Job_Resonance_Analysis",
            bot_name=self.job_resonance_bot
        )
        
        print(f"  ✓ Job resonance analysis complete")
        print(f"    - Emotional keywords: {len(result['emotional_keywords'])}")
        print(f"    - Cultural values: {len(result['cultural_values'])}")
        print(f"    - Hidden requirements: {len(result['hidden_requirements'])}")
        print(f"    - Power verbs: {len(result['power_verbs'])}")
        print(f"    - Technical keywords: {len(result['technical_keywords'])}\n")
        
        return result

    async def research_company(self, job_description: str, company_name: str, output_dir: str) -> dict:
        """
        INTELLIGENCE STEP 2: Research company for authentic connection building.
        
        Args:
            job_description: The job description text
            company_name: The company name
            output_dir: Directory to save research results
            
        Returns:
            Dictionary containing CompanyResearch data
        """
        print("INTELLIGENCE STEP 2: Researching company...")
        
        result = await self._call_intelligence_step_with_retry(
            prompt_template_name="research_company.txt",
            replacements={
                "[COMPANY_NAME]": company_name,
                "[JOB_DESCRIPTION]": job_description
            },
            model_class=CompanyResearch,
            step_name="Company Research",
            output_dir=output_dir,
            output_filename_prefix="Company_Research",
            bot_name=self.company_research_bot
        )
        
        print(f"  ✓ Company research complete")
        print(f"    - Mission: {result['mission_statement'][:60]}...")
        print(f"    - Core values: {len(result['core_values'])}")
        print(f"    - Tech stack: {len(result['tech_stack'])} technologies\n")
        
        return result

    async def generate_storytelling_arc(self, job_description: str, company_research: dict, 
                                       job_resonance: dict, tailored_resume: dict, 
                                       output_dir: str) -> dict:
        """
        INTELLIGENCE STEP 3: Generate storytelling arc for cover letter.
        
        Args:
            job_description: The job description text
            company_research: CompanyResearch data
            job_resonance: JobResonanceAnalysis data
            tailored_resume: The tailored resume JSON
            output_dir: Directory to save storytelling arc
            
        Returns:
            Dictionary containing StorytellingArc data
        """
        print("INTELLIGENCE STEP 3: Generating storytelling arc...")
        
        result = await self._call_intelligence_step_with_retry(
            prompt_template_name="generate_storytelling_arc.txt",
            replacements={
                "[JOB_DESCRIPTION]": job_description,
                "[COMPANY_RESEARCH]": json.dumps(company_research, indent=2),
                "[JOB_RESONANCE]": json.dumps(job_resonance, indent=2),
                "[TAILORED_RESUME]": json.dumps(tailored_resume, indent=2)
            },
            model_class=StorytellingArc,
            step_name="Storytelling Arc Generation",
            output_dir=output_dir,
            output_filename_prefix="Storytelling_Arc",
            bot_name=self.storytelling_arc_bot
        )
        
        print(f"  ✓ Storytelling arc generated")
        print(f"    - Hook: {result['hook'][:60]}...")
        print(f"    - Proof points: {len(result['proof_points'])}")
        print(f"    - Vision: {result['vision'][:60]}...\n")
        
        return result

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

        # Validate job inputs before processing
        print("VALIDATING JOB INPUTS...")
        try:
            self._validate_job_inputs(job)
        except ValueError as e:
            print(f"\n{'='*60}")
            print(f"❌ JOB INPUT VALIDATION FAILED")
            print(f"{'='*60}")
            print(f"Error: {str(e)}")
            print(f"{'='*60}\n")
            raise ValueError(f"Invalid job inputs: {str(e)}")

        # Create output directory
        output_dir = create_output_directory(job_id, job_title, company_name)
        print(f"Output directory: {output_dir}\n")

        # INTELLIGENCE GATHERING PHASE (3 steps before resume generation)
        print(f"\n{'='*60}")
        print(f"INTELLIGENCE GATHERING PHASE")
        print(f"{'='*60}\n")
        
        # Intelligence Step 1: Analyze job resonance
        job_resonance = await self.analyze_job_resonance(job_description, company_name, output_dir)
        
        # Intelligence Step 2: Research company
        company_research = await self.research_company(job_description, company_name, output_dir)
        
        print(f"{'='*60}")
        print(f"INTELLIGENCE GATHERING COMPLETE")
        print(f"{'='*60}\n")

        # STEP 1: Generate Resume JSON
        print("STEP 1: Generating tailored resume JSON...")
        resume_prompt = self.resume_prompt_template.replace(
            "[JOB_DESCRIPTION]", f"```\n{job_description}\n```"
        ).replace(
            "[MASTER_RESUME_JSON]", f"```json\n{json.dumps(self.master_resume, indent=2)}\n```"
        ).replace(
            "[COMPANY_NAME]", company_name
        ).replace(
            "[JOB_RESONANCE_ANALYSIS]", f"```json\n{json.dumps(job_resonance, indent=2)}\n```"
        )
        
        # Apply humanization if enabled for resume
        resume_prompt = self._apply_humanization(resume_prompt, "resume")
        
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

        # Intelligence Step 3: Generate storytelling arc (after resume, before cover letter)
        storytelling_arc = await self.generate_storytelling_arc(
            job_description, company_research, job_resonance, tailored_resume, output_dir
        )
        
        print(f"{'='*60}")
        print(f"INTELLIGENCE PHASE COMPLETE - PROCEEDING TO COVER LETTER")
        print(f"{'='*60}\n")

        # STEP 2: Generate Cover Letter Text
        print("STEP 2: Generating cover letter text...")
        cover_letter_prompt = self.cover_letter_prompt_template.replace(
            "[TAILORED_RESUME_JSON]", f"```json\n{json.dumps(tailored_resume, indent=2)}\n```"
        ).replace(
            "[JOB_DESCRIPTION]", f"```\n{job_description}\n```"
        ).replace(
            "[COMPANY_NAME]", company_name
        ).replace(
            "[STORYTELLING_ARC]", f"```json\n{json.dumps(storytelling_arc, indent=2)}\n```"
        ).replace(
            "[COMPANY_RESEARCH]", f"```json\n{json.dumps(company_research, indent=2)}\n```"
        ).replace(
            "[JOB_RESONANCE_ANALYSIS]", f"```json\n{json.dumps(job_resonance, indent=2)}\n```"
        )
        
        # Apply humanization if enabled for cover letter
        cover_letter_prompt = self._apply_humanization(cover_letter_prompt, "cover_letter")
        
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
        """Run the pipeline to process all pending jobs."""
        print("\n" + "=" * 60)
        print("RESUME OPTIMIZATION PIPELINE")
        print("=" * 60 + "\n")

        applications = load_yaml("applications.yaml")
        
        # Find all pending jobs
        pending_jobs = [job for job in applications if job.get("status") == "pending"]
        
        if not pending_jobs:
            print("No pending jobs found. All jobs are processed!")
            return

        print(f"Found {len(pending_jobs)} pending job(s) to process.\n")
        
        # Process each pending job
        processed_count = 0
        failed_count = 0
        
        for idx, pending_job in enumerate(pending_jobs, 1):
            job_title = pending_job.get("job_title", "Unknown")
            company_name = pending_job.get("company_name", "Unknown")
            
            print(f"\n{'='*60}")
            print(f"Processing job {idx}/{len(pending_jobs)}")
            print(f"{'='*60}\n")
            
            try:
                await self.process_job(pending_job)
                processed_count += 1
                print(f"\n✓ Successfully processed job {idx}/{len(pending_jobs)}: {job_title} at {company_name}")
            except Exception as e:
                failed_count += 1
                job_id = pending_job.get("job_id", "Unknown")
                print(f"\n{'='*60}")
                print(f"❌ ERROR processing job {idx}/{len(pending_jobs)}")
                print(f"{'='*60}")
                print(f"Job: {job_title} at {company_name}")
                print(f"Job ID: {job_id}")
                print(f"Error: {str(e)}")
                print(f"{'='*60}\n")
                print(f"Continuing to next job...\n")
                continue

        # Print summary
        print(f"\n{'='*60}")
        print(f"PIPELINE SUMMARY")
        print(f"{'='*60}")
        print(f"Total pending jobs: {len(pending_jobs)}")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed: {failed_count}")
        print(f"{'='*60}\n")
        
        if processed_count > 0:
            print("Pipeline completed successfully!")
        if failed_count > 0:
            print(f"⚠️  {failed_count} job(s) failed. Check the error messages above for details.\n")


async def main():
    """Main entry point."""
    pipeline = ResumeOptimizationPipeline()
    await pipeline.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
