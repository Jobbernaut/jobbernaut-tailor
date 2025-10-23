# API Reference

Complete reference for all classes, methods, and functions in Jobbernaut Tailor v4.x.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Data Models](#data-models)
3. [Utility Functions](#utility-functions)
4. [Template Renderer](#template-renderer)
5. [Configuration Schema](#configuration-schema)

## Core Classes

### ResumeOptimizationPipeline

Main pipeline orchestrator for resume and cover letter generation.

**Location**: `src/main.py`

#### Constructor

```python
def __init__(self)
```

Initializes the pipeline with configuration from `config.json` and environment variables.

**Raises**:
- `ValueError`: If `POE_API_KEY` is not found in environment variables

**Side Effects**:
- Loads configuration from `config.json`
- Loads master resume from `profile/master_resume.json`
- Loads prompt templates from `prompts/` directory
- Loads referral contact info if available
- Initializes template renderer

**Example**:
```python
from dotenv import load_dotenv
load_dotenv()

pipeline = ResumeOptimizationPipeline()
await pipeline.run()
```

#### Methods

##### run()

```python
async def run(self) -> None
```

Main entry point. Processes all pending jobs from `applications.yaml`.

**Behavior**:
- Finds all jobs with `status: "pending"`
- Processes each job sequentially
- Updates job status to `"processed"` on success
- Continues to next job on failure (doesn't stop pipeline)
- Prints summary statistics at end

**Example**:
```python
pipeline = ResumeOptimizationPipeline()
await pipeline.run()
```

##### process_job()

```python
async def process_job(self, job: dict) -> None
```

Processes a single job application through the complete 12-step pipeline.

**Parameters**:
- `job` (dict): Job dictionary with keys:
  - `job_id` (str): Unique job identifier
  - `job_title` (str): Job title
  - `company_name` (str): Company name
  - `job_description` (str): Full job description text

**Raises**:
- `ValueError`: If job inputs fail validation
- `Exception`: If any pipeline step fails after retries

**Pipeline Steps**:
1. Validate job inputs
2. Create output directory
3. Intelligence gathering phase:
   - Job resonance analysis
   - Company research
4. Generate tailored resume JSON
5. Generate storytelling arc
6. Generate cover letter text
7. Render resume LaTeX
8. Render cover letter LaTeX
9. Compile resume PDF
10. Compile cover letter PDF
11. (Optional) Create and compile referral documents
12. Clean up output directory

**Example**:
```python
job = {
    "job_id": "job_123",
    "job_title": "Senior Software Engineer",
    "company_name": "Example Corp",
    "job_description": "Full job description..."
}
await pipeline.process_job(job)
```

##### call_poe_api()

```python
async def call_poe_api(
    self,
    prompt: str,
    bot_name: str,
    parameters: dict = None,
    max_retries: int = 2
) -> str
```

Calls the Poe API with retry logic and optional reasoning trace removal.

**Parameters**:
- `prompt` (str): The prompt to send to the API
- `bot_name` (str): Name of the bot to use (e.g., "Gemini-2.5-Pro")
- `parameters` (dict, optional): API parameters:
  - `web_search` (bool): Enable web search
  - `thinking_budget` (int): Thinking tokens budget
  - `temperature` (float): Response randomness (0.0-1.0)
- `max_retries` (int): Maximum retry attempts (default: 2)

**Returns**:
- `str`: API response text (with reasoning traces removed if configured)

**Raises**:
- `Exception`: If all retry attempts fail

**Example**:
```python
response = await pipeline.call_poe_api(
    prompt="What is Python?",
    bot_name="Claude-Sonnet-4.5",
    parameters={"thinking_budget": 1024}
)
```

##### extract_json_from_response()

```python
def extract_json_from_response(self, response: str) -> dict
```

Extracts JSON from API response, handling markdown code blocks.

**Parameters**:
- `response` (str): Raw API response text

**Returns**:
- `dict`: Parsed JSON object

**Raises**:
- `json.JSONDecodeError`: If response is not valid JSON

**Supported Formats**:
```python
# Format 1: Markdown JSON code block
response = '''
```json
{"key": "value"}
```
'''

# Format 2: Markdown code block without language
response = '''
```
{"key": "value"}
```
'''

# Format 3: Raw JSON
response = '{"key": "value"}'
```

##### analyze_job_resonance()

```python
async def analyze_job_resonance(
    self,
    job_description: str,
    company_name: str,
    job_id: str,
    output_dir: str
) -> dict
```

**Intelligence Step 1**: Analyzes job description for emotional keywords and cultural signals.

**Parameters**:
- `job_description` (str): Full job description text
- `company_name` (str): Company name
- `job_id` (str): Job ID for logging
- `output_dir` (str): Directory to save analysis results

**Returns**:
- `dict`: JobResonanceAnalysis data:
  - `emotional_keywords` (List[str]): 3-15 emotional words
  - `cultural_values` (List[str]): 2+ culture signals
  - `hidden_requirements` (List[str]): 2+ implicit needs
  - `power_verbs` (List[str]): 3+ action words
  - `technical_keywords` (List[str]): 3+ technical terms

**Raises**:
- `ValueError`: If validation fails after max retries

**Output Files**:
- `Job_Resonance_Analysis.json`: Validated analysis
- `Job_Resonance_Analysis_Raw_Attempt_*.txt`: Raw AI responses

##### research_company()

```python
async def research_company(
    self,
    job_description: str,
    company_name: str,
    job_id: str,
    output_dir: str
) -> dict
```

**Intelligence Step 2**: Researches company for authentic connection building.

**Parameters**:
- `job_description` (str): Full job description text
- `company_name` (str): Company name
- `job_id` (str): Job ID for logging
- `output_dir` (str): Directory to save research results

**Returns**:
- `dict`: CompanyResearch data:
  - `company_name` (str): Company name
  - `mission_statement` (str): Mission (20+ chars)
  - `core_values` (List[str]): 2-10 values
  - `tech_stack` (List[str]): Technologies
  - `culture_keywords` (List[str]): Culture descriptors
  - `recent_news` (str): Recent achievements
  - `mission_keywords` (List[str]): Mission-critical keywords
  - `domain_context` (str): Industry context

**Raises**:
- `ValueError`: If validation fails after max retries

**Output Files**:
- `Company_Research.json`: Validated research
- `Company_Research_Raw_Attempt_*.txt`: Raw AI responses

##### generate_storytelling_arc()

```python
async def generate_storytelling_arc(
    self,
    job_description: str,
    company_research: dict,
    job_resonance: dict,
    tailored_resume: dict,
    job_id: str,
    company_name: str,
    output_dir: str
) -> dict
```

**Intelligence Step 3**: Generates storytelling arc for cover letter narrative.

**Parameters**:
- `job_description` (str): Full job description text
- `company_research` (dict): CompanyResearch data
- `job_resonance` (dict): JobResonanceAnalysis data
- `tailored_resume` (dict): Generated tailored resume
- `job_id` (str): Job ID for logging
- `company_name` (str): Company name
- `output_dir` (str): Directory to save storytelling arc

**Returns**:
- `dict`: StorytellingArc data:
  - `hook` (str): Opening sentence (50+ chars)
  - `bridge` (str): Transition (50+ chars)
  - `proof_points` (List[str]): 2-3 stories (each 30+ chars)
  - `vision` (str): Forward-looking statement (50+ chars)
  - `call_to_action` (str): Closing invitation (20+ chars)

**Raises**:
- `ValueError`: If validation fails after max retries

**Output Files**:
- `Storytelling_Arc.json`: Validated storytelling arc
- `Storytelling_Arc_Raw_Attempt_*.txt`: Raw AI responses

#### Private Methods

##### _validate_job_inputs()

```python
def _validate_job_inputs(self, job: dict) -> None
```

Validates job inputs before processing.

**Validation Rules**:
- `job_id`: Non-empty string
- `job_title`: 3-200 characters
- `company_name`: 2-100 characters
- `job_description`: 100-50,000 characters

**Raises**:
- `ValueError`: If any validation fails

##### _validate_intelligence_output()

```python
def _validate_intelligence_output(
    self,
    data: dict,
    step_name: str,
    model_class
) -> None
```

Validates intelligence output meets quality thresholds.

**Quality Checks**:
- Array sizes (minimum/maximum items)
- String lengths (minimum characters)
- No empty strings in arrays
- Meaningful content (not generic)

**Raises**:
- `ValueError`: If output doesn't meet quality thresholds

##### _build_simple_error_feedback()

```python
def _build_simple_error_feedback(
    self,
    validation_error: ValidationError,
    step_name: str
) -> str
```

Builds concise error feedback for retry attempts.

**Returns**:
- `str`: Formatted error feedback with:
  - Error count
  - Field-level errors
  - Corrective guidance

**Format**:
```
===============================================================================
⚠️  VALIDATION ERRORS TO FIX
===============================================================================

The previous [step_name] attempt had X validation error(s):

  • field.path: Error message
  • field.path: Error message

Fix these issues and regenerate the complete JSON output.
===============================================================================
```

##### _log_validation_failure()

```python
def _log_validation_failure(
    self,
    step_name: str,
    validation_error: ValidationError,
    job_id: str,
    company_name: str,
    attempt: int
) -> None
```

Logs validation failure to `learnings.yaml` for incident tracking.

**Purpose**: Track common failure patterns to improve prompts and validation rules.

**Output**: Appends to `learnings.yaml`:
```yaml
incidents:
  - timestamp: "2025-10-23T10:30:45"
    step_name: "Resume Generation"
    job_id: "job_123"
    company_name: "Example Corp"
    attempt: 2
    error_count: 3
    errors:
      - field: "work_experience.0.bullet_points.0"
        message: "Bullet point 1 exceeds 118 characters"
        type: "value_error"
```

##### _call_intelligence_step_with_retry()

```python
async def _call_intelligence_step_with_retry(
    self,
    prompt_template_name: str,
    replacements: dict,
    model_class,
    step_name: str,
    output_dir: str,
    output_filename_prefix: str,
    bot_name: str,
    parameters: dict = None,
    max_retries: int = 2
) -> dict
```

Generic retry wrapper for intelligence steps with validation and self-healing.

**Parameters**:
- `prompt_template_name` (str): Prompt template filename
- `replacements` (dict): Placeholder -> value mappings
- `model_class`: Pydantic model class for validation
- `step_name` (str): Human-readable step name
- `output_dir` (str): Output directory path
- `output_filename_prefix` (str): Output file prefix
- `bot_name` (str): AI model name
- `parameters` (dict, optional): API parameters
- `max_retries` (int): Maximum retry attempts

**Returns**:
- `dict`: Validated model data

**Raises**:
- `ValueError`: If all retries fail

**Retry Logic**:
1. Load and fill prompt template
2. Call AI API
3. Extract JSON
4. Validate with Pydantic
5. Validate quality thresholds
6. On failure: Build error feedback and retry
7. On success: Save validated JSON

##### _load_referral_contact()

```python
def _load_referral_contact(self) -> None
```

Loads referral contact information from `profile/referral_contact.json`.

**Behavior**:
- Gracefully handles missing, empty, or invalid files
- Validates email and phone format
- Sets `self.has_referral_contact` flag
- Prints status messages

**Side Effects**:
- Sets `self.referral_email`
- Sets `self.referral_phone`
- Sets `self.has_referral_contact`

##### _load_humanization_prompt()

```python
def _load_humanization_prompt(self, level: str) -> str
```

Loads humanization prompt for the specified level.

**Parameters**:
- `level` (str): Humanization level ("low", "medium", "high")

**Returns**:
- `str`: Humanization prompt text or None if file not found

##### _apply_humanization()

```python
def _apply_humanization(self, prompt: str, target: str) -> str
```

Applies humanization instructions to a prompt if enabled and applicable.

**Parameters**:
- `prompt` (str): Base prompt to enhance
- `target` (str): Target type ("resume" or "cover_letter")

**Returns**:
- `str`: Prompt with humanization appended (if applicable)

**Format**:
```
[Original Prompt]

================================================================================
[Humanization Instructions]
================================================================================
```

## Data Models

All models defined in `src/models.py` using Pydantic.

### ContactInfo

Contact information model with ATS-compatible validation.

**Fields**:
- `first_name` (str): First name (sanitized)
- `last_name` (str): Last name (sanitized)
- `phone` (str): Phone number in format `(XXX) XXX-XXXX`
- `email` (str): Email address
- `location` (str): Location (City, State or City, Country)
- `linkedin_url` (str): LinkedIn profile URL
- `github_url` (str): GitHub profile URL
- `portfolio_url` (str): Portfolio website URL

**Validators**:
- `sanitize_name()`: Removes illegal characters `<>[]{}\|~^`
- `validate_phone_format()`: Standardizes to `(XXX) XXX-XXXX`
- `sanitize_location()`: Removes illegal characters

**Example**:
```python
contact = ContactInfo(
    first_name="John",
    last_name="Doe",
    phone="919-672-2226",  # Will be formatted to (919) 672-2226
    email="john.doe@example.com",
    location="San Francisco, CA",
    linkedin_url="https://linkedin.com/in/johndoe",
    github_url="https://github.com/johndoe",
    portfolio_url="https://johndoe.com"
)
```

### Education

Education entry model.

**Fields**:
- `institution` (str): School name
- `degree` (str): Degree and major (e.g., "B.S. Computer Science, GPA: 3.9/4.0")
- `start_date` (str): Start date (e.g., "September 2016")
- `graduation_date` (str): Graduation date (NOT "end_date"!)
- `gpa` (str): Should be empty string (GPA goes in degree field)

**Validators**:
- `sanitize_text()`: Removes illegal characters from institution and degree

**Example**:
```python
edu = Education(
    institution="Stanford University",
    degree="B.S. Computer Science, GPA: 3.9/4.0",
    start_date="September 2016",
    graduation_date="June 2020",
    gpa=""  # Empty - GPA is in degree field
)
```

### WorkExperience

Work experience entry model with strict bullet point validation.

**Fields**:
- `job_title` (str): Job title
- `company` (str): Company name
- `start_date` (str): Start date (e.g., "January 2020")
- `end_date` (str): End date or "Present"
- `location` (Optional[str]): Location (City, State)
- `bullet_points` (List[str]): Exactly 4 bullets, each ≤118 chars

**Validators**:
- `sanitize_text()`: Removes illegal characters from title and company
- `sanitize_location()`: Removes illegal characters from location
- `validate_bullet_length()`: Enforces 4 bullets, each ≤118 chars

**Constraints**:
- Must have exactly 4 bullet points
- Each bullet point ≤118 characters (ATS limit)

**Example**:
```python
exp = WorkExperience(
    job_title="Senior Software Engineer",
    company="Tech Corp",
    start_date="January 2020",
    end_date="Present",
    location="San Francisco, CA",
    bullet_points=[
        "Led team of 5 engineers to deliver critical features on time",
        "Reduced API latency by 40% through optimization",
        "Implemented CI/CD pipeline reducing deploy time by 60%",
        "Mentored junior engineers on best practices"
    ]
)
```

### Project

Project entry model with technology stack validation.

**Fields**:
- `project_name` (str): Project name
- `technologies` (List[str]): Technology array (joined ≤70 chars)
- `project_url` (str): Project URL
- `description` (Optional[str]): Short description
- `bullet_points` (List[str]): Exactly 4 bullets, each ≤118 chars

**Validators**:
- `sanitize_project_name()`: Removes illegal characters
- `validate_technologies_length()`: Ensures joined string ≤70 chars
- `validate_bullet_length()`: Enforces 4 bullets, each ≤118 chars

**Constraints**:
- Must have exactly 4 bullet points
- Each bullet point ≤118 characters
- Technologies joined with ", " ≤70 characters

**Example**:
```python
project = Project(
    project_name="E-Commerce Platform",
    technologies=["Python", "Django", "PostgreSQL", "Redis"],
    project_url="https://github.com/user/project",
    description="Scalable e-commerce platform",
    bullet_points=[
        "Built RESTful API serving 10K requests/second",
        "Implemented caching layer reducing DB load by 70%",
        "Designed scalable microservices architecture",
        "Achieved 99.9% uptime through monitoring"
    ]
)
```

### TailoredResume

Complete tailored resume model (root model).

**Fields**:
- `contact_info` (ContactInfo): Contact information
- `professional_summaries` (str): Must be empty string
- `education` (List[Education]): Minimum 1 entry
- `skills` (Dict[str, str]): Category name -> skills string
- `work_experience` (List[WorkExperience]): Exactly 3 entries
- `projects` (List[Project]): Exactly 3 entries

**Validators**:
- `validate_skills_length()`: Category ≤30 chars, skills ≤90 chars
- `validate_empty_summary()`: Ensures professional_summaries is empty

**Constraints**:
- professional_summaries must be empty string (to maximize content space)
- Exactly 3 work experience entries
- Exactly 3 project entries
- Skills category names ≤30 characters
- Skills values ≤90 characters

**Example**:
```python
resume = TailoredResume(
    contact_info=ContactInfo(...),
    professional_summaries="",  # Must be empty!
    education=[Education(...)],
    skills={
        "Languages": "Python, Java, JavaScript, TypeScript, Go",
        "Frameworks": "Django, Flask, React, Node.js, Spring Boot",
        "Tools": "Docker, Kubernetes, AWS, PostgreSQL, Redis"
    },
    work_experience=[
        WorkExperience(...),
        WorkExperience(...),
        WorkExperience(...)
    ],
    projects=[
        Project(...),
        Project(...),
        Project(...)
    ]
)
```

### JobResonanceAnalysis

Intelligence model for job description analysis.

**Fields**:
- `emotional_keywords` (List[str]): 3-15 emotional words
- `cultural_values` (List[str]): 2+ culture signals
- `hidden_requirements` (List[str]): 2+ implicit needs
- `power_verbs` (List[str]): 3+ action words
- `technical_keywords` (List[str]): 3+ technical terms

**Validators**:
- `validate_non_empty_lists()`: Ensures all lists have ≥1 item

**Quality Thresholds**:
- emotional_keywords: 3-15 items
- cultural_values: ≥2 items
- hidden_requirements: ≥2 items
- power_verbs: ≥3 items
- technical_keywords: ≥3 items

**Example**:
```python
analysis = JobResonanceAnalysis(
    emotional_keywords=["passionate", "innovative", "ownership", "impact"],
    cultural_values=["collaborative", "data-driven", "customer-focused"],
    hidden_requirements=["startup mentality", "comfort with ambiguity"],
    power_verbs=["architected", "spearheaded", "optimized", "delivered"],
    technical_keywords=["Python", "AWS", "microservices", "CI/CD"]
)
```

### CompanyResearch

Intelligence model for company information.

**Fields**:
- `company_name` (str): Company name
- `mission_statement` (str): Mission (20+ chars)
- `core_values` (List[str]): 2-10 company values
- `tech_stack` (List[str]): Technologies used
- `culture_keywords` (List[str]): Culture descriptors
- `recent_news` (str): Recent achievements (optional)
- `mission_keywords` (List[str]): Mission-critical keywords
- `domain_context` (str): Industry context

**Validators**:
- `validate_core_values()`: Ensures ≥1 value

**Quality Thresholds**:
- mission_statement: ≥20 characters
- core_values: 2-10 items

**Example**:
```python
research = CompanyResearch(
    company_name="Example Corp",
    mission_statement="Empowering businesses through innovative technology solutions",
    core_values=["customer obsession", "innovation", "integrity"],
    tech_stack=["Python", "React", "AWS", "Kubernetes"],
    culture_keywords=["collaborative", "fast-paced", "learning-focused"],
    recent_news="Raised $50M Series B, expanded to Europe",
    mission_keywords=["innovation", "technology", "empowerment"],
    domain_context="Enterprise SaaS"
)
```

### StorytellingArc

Intelligence model for cover letter narrative structure.

**Fields**:
- `hook` (str): Opening sentence (50+ chars)
- `bridge` (str): Transition (50+ chars)
- `proof_points` (List[str]): 2-3 stories (each 30+ chars)
- `vision` (str): Forward-looking statement (50+ chars)
- `call_to_action` (str): Closing invitation (20+ chars)

**Validators**:
- `validate_non_empty_strings()`: Ensures all strings are non-empty

**Quality Thresholds**:
- hook: ≥50 characters
- bridge: ≥50 characters
- vision: ≥50 characters
- call_to_action: ≥20 characters
- proof_points: 2-3 items, each ≥30 characters

**Example**:
```python
arc = StorytellingArc(
    hook="When I read about Example Corp's mission to democratize AI, it resonated deeply with my passion for accessible technology.",
    bridge="Throughout my career, I've consistently worked at the intersection of cutting-edge technology and user experience.",
    proof_points=[
        "At Tech Corp, I led the development of an API that reduced latency by 40%, directly improving user experience for 100K+ customers.",
        "I architected a microservices platform that scaled to handle 1M requests/day while maintaining 99.9% uptime.",
        "My work on CI/CD automation reduced deployment time from hours to minutes, enabling rapid iteration."
    ],
    vision="I'm excited about the opportunity to bring this experience to Example Corp, where I can contribute to building scalable, user-centric solutions that align with your mission.",
    call_to_action="I'd love to discuss how my background in distributed systems and API design can support Example Corp's growth objectives."
)
```

## Utility Functions

All utility functions defined in `src/utils.py`.

### load_yaml()

```python
def load_yaml(file_path: str) -> list | dict
```

Loads YAML file and returns parsed content.

**Parameters**:
- `file_path` (str): Path to YAML file

**Returns**:
- `list | dict`: Parsed YAML content

**Raises**:
- `FileNotFoundError`: If file doesn't exist
- `yaml.YAMLError`: If YAML is invalid

### load_json()

```python
def load_json(file_path: str) -> dict
```

Loads JSON file and returns parsed content.

**Parameters**:
- `file_path` (str): Path to JSON file

**Returns**:
- `dict`: Parsed JSON content

**Raises**:
- `FileNotFoundError`: If file doesn't exist
- `json.JSONDecodeError`: If JSON is invalid

### save_json()

```python
def save_json(file_path: str, data: dict) -> None
```

Saves dictionary to JSON file with pretty formatting.

**Parameters**:
- `file_path` (str): Path to save JSON file
- `data` (dict): Data to save

**Format**: 2-space indentation, sorted keys, UTF-8 encoding

### find_pending_job()

```python
def find_pending_job(applications: list) -> dict | None
```

Finds the first pending job in applications list.

**Parameters**:
- `applications` (list): List of job dictionaries

**Returns**:
- `dict | None`: First job with `status: "pending"` or None

### update_job_status()

```python
def update_job_status(
    applications_path: str,
    job_id: str,
    new_status: str
) -> None
```

Updates job status in applications YAML file.

**Parameters**:
- `applications_path` (str): Path to applications.yaml
- `job_id` (str): Job ID to update
- `new_status` (str): New status value (e.g., "processed", "skipped")

### create_output_directory()

```python
def create_output_directory(
    job_id: str,
    job_title: str,
    company_name: str
) -> str
```

Creates output directory for job application.

**Parameters**:
- `job_id` (str): Job ID
- `job_title` (str): Job title
- `company_name` (str): Company name

**Returns**:
- `str`: Path to created directory

**Format**: `output/{job_id}_{company_name}/`

### load_prompt_template()

```python
def load_prompt_template(template_name: str) -> str
```

Loads prompt template from prompts directory.

**Parameters**:
- `template_name` (str): Template filename (e.g., "generate_resume.txt")

**Returns**:
- `str`: Template content

**Raises**:
- `FileNotFoundError`: If template doesn't exist

### compile_latex_to_pdf()

```python
def compile_latex_to_pdf(
    tex_file: str,
    output_dir: str,
    doc_type: str
) -> str
```

Compiles LaTeX file to PDF using pdflatex.

**Parameters**:
- `tex_file` (str): Path to .tex file
- `output_dir` (str): Output directory
- `doc_type` (str): Document type ("resume" or "cover_letter")

**Returns**:
- `str`: Path to generated PDF

**Raises**:
- `Exception`: If compilation fails

**Compilation Options**:
- `-interaction=nonstopmode`: Don't stop on errors
- `-output-directory`: Specify output directory
- Run twice for proper formatting

### cleanup_output_directory()

```python
def cleanup_output_directory(
    output_dir: str,
    first_name: str,
    last_name: str,
    company_name: str,
    job_id: str
) -> None
```

Moves non-PDF files to debug subdirectory.

**Parameters**:
- `output_dir` (str): Output directory path
- `first_name` (str): First name for final PDFs
- `last_name` (str): Last name for final PDFs
- `company_name` (str): Company name for final PDFs
- `job_id` (str): Job ID for final PDFs

**Behavior**:
- Creates `debug/` subdirectory
- Moves all non-PDF files to debug/
- Keeps only final PDFs in main directory

**Files Moved**:
- `.json` - JSON data files
- `.txt` - Text files
- `.tex` - LaTeX source files
- `.log` - LaTeX log files
- `.aux` - LaTeX auxiliary files

### remove_reasoning_traces()

```python
def remove_reasoning_traces(
    text: str,
    remove: bool
) -> str
```

Removes reasoning traces from AI model responses.

**Parameters**:
- `text` (str): Response text
- `remove` (bool): Whether to remove traces

**Returns**:
- `str`: Text with reasoning traces removed (if remove=True)

**Patterns Removed**:
- `<thinking>...</thinking>`
- `<reasoning>...</reasoning>`
- Any similar XML-style thinking blocks

## Template Renderer

Template rendering system defined in `src/template_renderer.py`.

### TemplateRenderer

Handles Jinja2 template rendering for LaTeX generation.

#### Constructor

```python
def __init__(self)
```

Initializes Jinja2 environment with LaTeX-compatible syntax.

**Configuration**:
- Block delimiters: `\BLOCK{...}`
- Variable delimiters: `\VAR{...}`
- Comment delimiters: `\#{...}`
- Autoescape: Disabled (manual LaTeX escaping)
- Template directory: `templates/`

#### Methods

##### render_resume()

```python
def render_resume(self, resume_data: dict) -> str
```

Renders resume LaTeX from template and data.

**Parameters**:
- `resume_data` (dict): Validated TailoredResume data

**Returns**:
- `str`: Complete LaTeX document

**Template**: `templates/resume.jinja2`

**Example**:
```python
renderer = TemplateRenderer()
resume_latex = renderer.render_resume(validated_resume)
```

##### render_cover_letter()

```python
def render_cover_letter(
    self,
    contact_info: dict,
    cover_letter_text: str
) -> str
```

Renders cover letter LaTeX from template and data.

**Parameters**:
- `contact_info` (dict): ContactInfo data
- `cover_letter_text` (str): Generated cover letter text

**Returns**:
- `str`: Complete LaTeX document

**Template**: `templates/cover_letter.jinja2`

**Example**:
```python
renderer = TemplateRenderer()
cover_letter_latex = renderer.render_cover_letter(
    contact_info,
    cover_letter_text
)
```

##### render_resume_with_referral()

```python
def render_resume_with_referral(
    self,
    resume_data: dict,
    referral_contact: dict
) -> str
```

Renders resume with referral contact information.

**Parameters**:
- `resume_data` (dict): Validated TailoredResume data
- `referral_contact` (dict): Referral ContactInfo data

**Returns**:
- `str`: Complete LaTeX document with referral contact

**Behavior**: Same as `render_resume()` but replaces contact info with referral contact.

##### render_cover_letter_with_referral()

```python
def render_cover_letter_with_referral(
    self,
    cover_letter_text: str,
    referral_contact: dict
) -> str
```

Renders cover letter with referral contact information.

**Parameters**:
- `cover_letter_text` (str): Generated cover letter text
- `referral_contact` (dict): Referral ContactInfo data

**Returns**:
- `str`: Complete LaTeX document with referral contact

**Behavior**: Same as `render_cover_letter()` but uses referral contact info.

##### latex_escape()

```python
def latex_escape(self, text: str) -> str
```

Escapes special LaTeX characters in text.

**Parameters**:
- `text` (str): Text to escape

**Returns**:
- `str`: LaTeX-safe text

**Escaped Characters**:
```python
{
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}'
}
```

**Note**: Backslash `\` requires special handling for LaTeX commands.

## Configuration Schema

Configuration structure for `config.json`.

### Root Schema

```json
{
  "resume_generation": {...},
  "cover_letter_generation": {...},
  "intelligence_steps": {...},
  "humanization": {...},
  "defaults": {...},
  "reasoning_trace": bool,
  "file_paths": {...}
}
```

### resume_generation

```json
{
  "bot_name": "Gemini-2.5-Pro",
  "parameters": {
    "web_search": false,
    "thinking_budget": 2048,
    "temperature": 0.7
  }
}
```

**Fields**:
- `bot_name` (str): AI model name for resume generation
- `parameters` (dict): API parameters
  - `web_search` (bool): Enable web search
  - `thinking_budget` (int): Thinking tokens budget
  - `temperature` (float): Response randomness (0.0-1.0)

### cover_letter_generation

```json
{
  "bot_name": "Claude-Haiku-4.5",
  "parameters": {
    "thinking_budget": 0
  }
}
```

**Fields**: Same as `resume_generation`

### intelligence_steps

```json
{
  "job_resonance_analysis": {
    "bot_name": "Claude-Haiku-4.5",
    "parameters": {
      "thinking_budget": 0
    }
  },
  "company_research": {
    "bot_name": "Claude-Sonnet-4-Search",
    "parameters": {
      "web_search": true,
      "thinking_budget": 0
    }
  },
  "storytelling_arc": {
    "bot_name": "Claude-Haiku-4.5",
    "parameters": {
      "thinking_budget": 0
    }
  }
}
```

**Fields**: Per-step model configuration with same structure as `resume_generation`

### humanization

```json
{
  "enabled": false,
  "level": "low",
  "apply_to": ["resume", "cover_letter"]
}
```

**Fields**:
- `enabled` (bool): Enable humanization feature
- `level` (str): Humanization level ("low", "medium", "high")
- `apply_to` (List[str]): Document types to humanize

### defaults

```json
{
  "resume_bot": "Claude-Sonnet-4.5",
  "cover_letter_bot": "Claude-Sonnet-4.5"
}
```

**Fields**:
- `resume_bot` (str): Default model for resume tasks
- `cover_letter_bot` (str): Default model for cover letter tasks

### reasoning_trace

```json
"reasoning_trace": false
```

**Type**: `bool`

**Behavior**:
- `false`: Remove reasoning traces from responses (default)
- `true`: Keep reasoning traces (for debugging)

### file_paths

```json
{
  "applications": "data/applications.yaml",
  "application_template": "data/application_template.yaml",
  "master_resume": "profile/master_resume.json"
}
```

**Fields**:
- `applications` (str): Path to applications YAML
- `application_template` (str): Path to application template
- `master_resume` (str): Path to master resume JSON

---

## Error Classes

### ValidationError

Pydantic validation error raised when model validation fails.

**Attributes**:
- `errors()`: List of error dictionaries
  - `loc` (Tuple): Field path (e.g., ("work_experience", 0, "bullet_points", 0))
  - `msg` (str): Error message
  - `type` (str): Error type (e.g., "value_error")

**Example**:
```python
try:
    resume = TailoredResume(**data)
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {'.'.join(str(loc) for loc in error['loc'])}")
        print(f"Error: {error['msg']}")
```

---

## Constants

### ATS Character Limits

Defined in validation logic:

```python
BULLET_POINT_MAX_LENGTH = 118  # Characters
SKILLS_CATEGORY_MAX_LENGTH = 30  # Characters
SKILLS_VALUE_MAX_LENGTH = 90  # Characters
TECHNOLOGIES_MAX_LENGTH = 70  # Characters (joined)
```

### File Extensions

```python
LATEX_EXTENSIONS = ['.tex', '.aux', '.log', '.out']
DEBUG_EXTENSIONS = ['.json', '.txt', '.tex', '.log', '.aux']
PDF_EXTENSION = '.pdf'
```

### Status Values

```python
JOB_STATUS_PENDING = "pending"
JOB_STATUS_PROCESSED = "processed"
JOB_STATUS_SKIPPED = "skipped"
```

---

*Last Updated: October 2025*
*Version: 4.1*
