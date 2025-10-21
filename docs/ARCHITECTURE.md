# Jobbernaut Tailor - System Architecture

## Overview

Jobbernaut Tailor is an AI-powered job application automation pipeline designed to generate tailored resumes and cover letters at scale. The system follows a strict sequential processing model with robust error handling, type validation, and professional PDF generation.

## Core Design Principles

### 1. Single Source of Truth
All job application data resides in one master YAML file (`applications.yaml`). This eliminates the complexity of managing separate input files for each job application, creating a scalable and maintainable database of all job prospects.

**Rationale**: Centralized data management reduces errors, simplifies version control, and enables easy auditing of application history.

### 2. Hassle-Free Data Entry
The YAML format supports raw, multi-line text blocks (`job_description: |`), allowing users to copy-paste job descriptions directly from websites without manual formatting or character escaping.

**Rationale**: Minimizes friction in the data entry process, reducing the time from finding a job to generating application materials from hours to minutes.

### 3. Type Safety Through Validation
Pydantic models enforce strict schema validation before any document generation, ensuring data integrity and preventing malformed outputs.

**Rationale**: Catching errors early in the pipeline prevents wasted API calls and ensures consistent, high-quality outputs.

### 4. Template-Based Rendering
Jinja2 templates separate content from presentation, enabling consistent formatting while maintaining flexibility for customization.

**Rationale**: Decoupling data from presentation logic makes the system more maintainable and allows non-technical users to customize document appearance.

### 5. Idempotent Operations
Once a job is marked as "processed," the pipeline ignores it on subsequent runs, allowing safe re-execution without duplicate processing.

**Rationale**: Enables recovery from failures and supports iterative development without risk of data corruption.

## System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  - applications.yaml (Job Database)                          │
│  - config.json (Configuration)                               │
│  - CLI Execution (python src/main.py)                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Pipeline Orchestration                     │
│  - ResumeOptimizationPipeline (main.py)                     │
│  - Sequential 13-step processing (V4)                        │
│  - Intelligence gathering phase                              │
│  - Error handling and retry logic                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Core Processing Layer                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   AI Layer   │  │ Validation   │  │  Rendering   │      │
│  │              │  │   Layer      │  │    Layer     │      │
│  │ - Poe API    │  │ - Pydantic   │  │ - Jinja2     │      │
│  │ - Prompts    │  │ - Models     │  │ - Templates  │      │
│  │ - Retry      │  │ - Schema     │  │ - Filters    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Output Generation Layer                   │
│  - LaTeX Compilation (pdflatex)                              │
│  - File Organization (cleanup_output_directory)              │
│  - Referral Document Generation                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Persistence Layer                       │
│  - output/ directory (Generated PDFs)                        │
│  - debug/ subdirectories (Intermediate files)                │
│  - applications.yaml updates (Status tracking)               │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Pipeline Orchestrator (`main.py`)

**Responsibility**: Coordinates the entire document generation workflow.

**Key Classes**:
- `ResumeOptimizationPipeline`: Main orchestration class that manages the 13-step pipeline (V4)

**Key Methods**:
- `__init__()`: Initializes configuration, loads master resume, sets up API clients
- `process_job()`: Executes the complete pipeline for a single job
- `run()`: Entry point that finds pending jobs and processes them
- `call_poe_api()`: Handles AI API calls with retry logic
- `_validate_job_inputs()`: Validates job inputs before processing (V4)
- `_call_intelligence_step_with_retry()`: Generic retry wrapper for intelligence steps (V4)
- `_validate_intelligence_output()`: Validates intelligence output quality (V4)
- `analyze_job_resonance()`: Intelligence Step 1 - analyzes job resonance (V4)
- `research_company()`: Intelligence Step 2 - researches company (V4)
- `generate_storytelling_arc()`: Intelligence Step 3 - generates storytelling arc (V4)
- `_build_error_feedback()`: Generates detailed error messages for validation failures
- `_apply_humanization()`: Conditionally applies humanization prompts

**Design Pattern**: Template Method Pattern - defines the skeleton of the pipeline algorithm, with specific steps implemented as separate methods.

### 2. Validation Layer (`models.py`)

**Responsibility**: Enforces type safety and data integrity through Pydantic models.

**Key Models**:
- `ContactInfo`: Personal contact information
- `Education`: Educational background entries
- `WorkExperience`: Professional experience entries
- `Project`: Project portfolio entries
- `TailoredResume`: Complete resume structure
- `JobResonanceAnalysis`: Job resonance intelligence data (V4)
- `CompanyResearch`: Company research intelligence data (V4)
- `StorytellingArc`: Cover letter storytelling arc data (V4)

**Validation Rules**:
- Character limits (bullet points ≤ 100 chars, skills ≤ 100 chars, technologies ≤ 100 chars)
- Array length constraints (exactly 4 bullet points, exactly 3 work experiences)
- Required vs optional fields
- Field name enforcement (e.g., `graduation_date` not `end_date`)

**Design Pattern**: Builder Pattern - constructs complex resume objects with validation at each step.

### 3. Template Rendering Layer (`template_renderer.py`)

**Responsibility**: Transforms validated JSON data into professional LaTeX documents.

**Key Class**:
- `TemplateRenderer`: Manages Jinja2 template rendering with custom filters

**Custom Filters**:
- `latex_escape()`: Escapes special LaTeX characters to prevent compilation errors
- `format_date()`: Converts YYYY-MM dates to "MMM YYYY" format
- `format_phone()`: Normalizes phone numbers to 10-digit format

**Template Variables**:
- Custom delimiters to avoid LaTeX syntax conflicts:
  - `\VAR{variable}` instead of `{{ variable }}`
  - `\BLOCK{...}` instead of `{% ... %}`

**Design Pattern**: Strategy Pattern - different rendering strategies for resume vs cover letter.

### 4. Utility Layer (`utils.py`)

**Responsibility**: Provides reusable helper functions for file I/O, compilation, and data management.

**Key Functions**:
- `load_yaml()` / `save_yaml()`: YAML file operations
- `load_json()` / `save_json()`: JSON file operations
- `find_pending_job()`: Locates next job to process
- `update_job_status()`: Updates job status in applications.yaml
- `compile_latex_to_pdf()`: Compiles LaTeX to PDF using pdflatex
- `cleanup_output_directory()`: Organizes output files

**Design Pattern**: Utility/Helper Pattern - stateless functions for common operations.

## Data Flow

### Complete Pipeline Flow (V4 - 13 Steps)

```
1. User adds job to applications.yaml with status: "pending"
                    ↓
2. Pipeline finds first pending job
                    ↓
3. Load master resume from profile/master_resume.json
                    ↓
4. Validate job inputs (V4)
   - Check required fields (company_name, job_title, job_description)
   - Verify data types and non-empty values
   - Halt pipeline if validation fails
                    ↓
5. INTELLIGENCE STEP 1: Analyze Job Resonance (V4)
   - Call analyze_job_resonance() with retry wrapper
   - Validate output with JobResonanceAnalysis model
   - Check quality: character counts, array sizes, meaningful content
   - Retry up to 3 times with progressive error feedback
   - Save validated output to job data
                    ↓
6. INTELLIGENCE STEP 2: Research Company (V4)
   - Call research_company() with retry wrapper
   - Validate output with CompanyResearch model
   - Check quality: character counts, array sizes, meaningful content
   - Retry up to 3 times with progressive error feedback
   - Save validated output to job data
                    ↓
7. INTELLIGENCE STEP 3: Generate Storytelling Arc (V4)
   - Call generate_storytelling_arc() with retry wrapper
   - Validate output with StorytellingArc model
   - Check quality: character counts, array sizes, meaningful content
   - Retry up to 3 times with progressive error feedback
   - Save validated output to job data
                    ↓
8. Generate tailored resume JSON via AI
   - Use intelligence context from previous steps
   - Retry up to 3 times on validation failure
   - Build error feedback for AI on each retry
                    ↓
9. Validate resume JSON with TailoredResume Pydantic model
   - Enforce schema compliance
   - Check character limits (bullets ≤100, skills ≤100, tech ≤100)
   - Verify required fields and array lengths
                    ↓
10. Generate cover letter text via AI
    - Use storytelling arc from intelligence phase
    - Apply humanization if enabled
                    ↓
11. Render documents to LaTeX
    - Render resume LaTeX from Jinja2 template
    - Render cover letter LaTeX from Jinja2 template
    - Apply custom filters and escape special characters
                    ↓
12. Compile PDFs with pdflatex
    - Compile resume PDF
    - Compile cover letter PDF
    - Generate referral versions (alternate contact info)
      * Render referral resume LaTeX
      * Render referral cover letter LaTeX
      * Compile referral resume PDF
      * Compile referral cover letter PDF
                    ↓
13. Finalize and cleanup
    - Organize output files (4 final PDFs in main directory)
    - Move intermediate files to debug/ subdirectory
    - Update job status to "processed" in applications.yaml
```

**V4 Key Changes**:
- Added input validation step (Step 4)
- Added 3-step intelligence gathering phase (Steps 5-7)
- Intelligence steps use generic retry wrapper with quality validation
- Resume generation (Step 8) now uses intelligence context
- Cover letter generation (Step 10) uses storytelling arc
- Total pipeline expanded from 10 to 13 steps

## Technology Stack

### Core Technologies
- **Python 3.8+**: Primary programming language
- **Pydantic**: Data validation and settings management
- **Jinja2**: Template engine for LaTeX generation
- **PyYAML**: YAML parsing and serialization
- **fastapi_poe**: Poe API client for AI model access
- **pdflatex**: LaTeX to PDF compilation

### AI Integration
- **Poe API**: Provides access to multiple AI models (Claude, GPT, Gemini)
- **Configurable Models**: Different models for different tasks (resume generation, cover letter writing)

### Document Generation
- **LaTeX**: Professional typesetting system
- **Custom .cls files**: Resume and cover letter class files for consistent formatting
- **Jinja2 Templates**: Separation of content and presentation

## Configuration System

### Configuration Hierarchy

```
1. Environment Variables (.env)
   - POE_API_KEY: API authentication

2. Configuration File (config.json)
   - resume_generation: Bot selection and settings
   - cover_letter_generation: Bot selection and settings
   - humanization: Enable/disable and level settings
   - referral_resume: Alternate contact information
   - defaults: Fallback bot selections

3. Master Data (profile/master_resume.json)
   - Complete resume data
   - Source of truth for all content

4. Prompt Templates (prompts/*.txt)
   - generate_resume.txt: Resume generation instructions
   - generate_cover_letter.txt: Cover letter generation instructions
   - humanization_*.txt: Humanization level prompts
```

## Error Handling Strategy

### Validation Error Handling
1. **Detection**: Pydantic catches schema violations
2. **Categorization**: Errors grouped by type (missing fields, type errors, format errors)
3. **Feedback Generation**: Detailed, actionable error messages created
4. **Retry with Context**: Error feedback appended to prompt for AI correction
5. **Maximum Retries**: Up to 3 attempts before pipeline halt

### API Error Handling
1. **Retry Logic**: Up to 3 attempts per API call
2. **Exponential Backoff**: Implicit through sequential retries
3. **Error Logging**: Detailed error messages with attempt numbers
4. **Graceful Failure**: Pipeline halts with clear error message

### LaTeX Compilation Error Handling
1. **Prerequisite Check**: Verify pdflatex availability
2. **Timeout Protection**: 120-second timeout per compilation
3. **Log Analysis**: Parse .log files for error details
4. **Cleanup**: Remove auxiliary files (.aux, .log, .out)

## Security Considerations

### API Key Management
- Environment variables for sensitive credentials
- .env file excluded from version control
- No hardcoded API keys in source code

### Input Validation
- Pydantic models prevent injection attacks
- LaTeX escaping prevents command injection
- File path sanitization prevents directory traversal

### Output Isolation
- All outputs contained in output/ directory
- Debug files separated from final PDFs
- No overwriting of source files

## Performance Characteristics

### Time Complexity
- **Per Job**: O(1) - constant time per job (dominated by AI API calls)
- **Total Pipeline**: O(n) - linear with number of pending jobs

### Space Complexity
- **Memory**: O(1) - processes one job at a time
- **Disk**: O(n) - grows linearly with number of processed jobs

### Bottlenecks
1. **AI API Calls**: 2-3 seconds per call (4 calls per job)
2. **LaTeX Compilation**: 5-10 seconds per PDF (4 PDFs per job)
3. **Network Latency**: Variable based on API response time

### Optimization Strategies
- Sequential processing prevents API rate limiting
- Retry logic minimizes wasted API calls
- Template caching reduces rendering overhead
- Cleanup operations reduce disk usage

## Extensibility Points

### Adding New AI Models
1. Update `config.json` with new bot name
2. No code changes required

### Adding New Validation Rules
1. Modify Pydantic models in `models.py`
2. Add field validators as needed

### Customizing Templates
1. Edit Jinja2 templates in `templates/`
2. Add custom filters to `template_renderer.py`

### Adding New Output Formats
1. Create new template file
2. Add rendering method to `TemplateRenderer`
3. Update pipeline to call new renderer

## Monitoring and Observability

### Logging Strategy
- Console output for real-time progress
- Step-by-step status updates
- Detailed error messages with context
- Validation attempt tracking

### Debug Artifacts
- Raw API responses saved to debug/
- Invalid JSON saved for troubleshooting
- LaTeX source files preserved
- Plain text cover letters retained

### Status Tracking
- Job status in applications.yaml
- Output directory structure
- File naming conventions indicate completion

## Deployment Considerations

### Prerequisites
- Python 3.8+ runtime
- LaTeX distribution (MiKTeX or TeX Live)
- Internet connection for API access
- Sufficient disk space for outputs

### Environment Setup
1. Virtual environment recommended
2. Dependencies installed via requirements.txt
3. LaTeX packages auto-installed on first run
4. API keys configured in .env

### Operational Requirements
- Manual execution per job batch
- User reviews applications.yaml before running
- Pipeline halts on errors for user intervention
- No background processing or scheduling
