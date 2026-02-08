# Architecture Guide - Jobbernaut Tailor v4.2+

**Last Updated**: October 27, 2025  
**Version**: v4.2+ (with Fact Verification & Humanization)

---

## System Overview

Jobbernaut Tailor is a **validation-first resume automation pipeline** that processes job applications at scale while maintaining quality guarantees through multi-stage validation and self-healing error recovery.

### Core Philosophy

```
Quality > Speed > Cost
```

Every design decision prioritizes **validation and error recovery** over raw performance. The system is built to handle failures gracefully and self-correct without manual intervention.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE ORCHESTRATOR                     │
│                      (main.py)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              INTELLIGENCE GATHERING PHASE                    │
│  1. Job Resonance Analysis (emotional keywords)             │
│  2. Company Research (mission, values, tech stack)          │
│  3. Storytelling Arc (cover letter narrative)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                CONTENT GENERATION PHASE                      │
│  4. Resume Generation (Pydantic validation)                 │
│     └─ Includes Fact Verification (hallucination detection) │
│  5. Cover Letter Generation (quality validation)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  RENDERING & COMPILATION                     │
│  6. Resume LaTeX Rendering (Jinja2)                         │
│  7. Cover Letter LaTeX Rendering (Jinja2)                   │
│  8. Resume PDF Compilation (pdflatex)                       │
│  9. Cover Letter PDF Compilation (pdflatex)                 │
│  10-11. [Optional] Referral Documents                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT ORGANIZATION                       │
│  12. Cleanup (move non-PDFs to debug/)                      │
│      Status update (mark job as processed)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Pipeline Orchestrator (`main.py`)

**Purpose**: Coordinates the entire processing pipeline with error handling and retry logic.

**Key Classes**:
- `ResumeOptimizationPipeline`: Main orchestration class
  - Manages configuration
  - Coordinates API calls
  - Handles validation and retries
  - Tracks progress

**Key Methods**:
```python
async def process_job(job, tracker, live)
    # Main processing pipeline for a single job
    
async def call_poe_api(prompt, bot_name, parameters, max_retries=2)
    # API calls with exponential backoff retry
    
async def _call_intelligence_step_with_retry(...)
    # Generic retry wrapper for intelligence steps
```

### 2. Validation System

**Multi-Layer Defense**:

```
Layer 1: Pydantic Schema Validation
  ↓ (retry with feedback if invalid)
Layer 2: Fact Verification
  ↓ (retry with hallucination feedback)
Layer 3: Quality Thresholds
  ↓ (retry with quality feedback)
Layer 4: LaTeX Compilation
  ↓ (fail if compilation errors)
Output: Validated PDFs
```

**Why Multiple Layers?**
- Each layer catches different error types
- Defense in depth prevents cascading failures
- Self-healing at each layer reduces manual intervention

**Note**: Input validation happens implicitly at the start of `process_job()` through Python type checking and basic validation, but is not a separate numbered step in the pipeline.

### 3. Pydantic Models (`models.py`)

**Purpose**: Define strict schemas for all data structures with custom validators.

**Key Models**:
```python
class TailoredResume(BaseModel):
    # Resume structure with ATS-optimized constraints
    # - Bullet points ≤ 118 chars
    # - Skills per category ≤ 85 chars
    # - Phone number formatting
    # - Date standardization
    
class JobResonanceAnalysis(BaseModel):
    # Job analysis output structure
    
class CompanyResearch(BaseModel):
    # Company research output structure
    
class StorytellingArc(BaseModel):
    # Cover letter narrative structure
```

**Custom Validators**:
- Character limit enforcement
- Format standardization (phone, dates, locations)
- Required field validation
- Type coercion and sanitization

### 4. Fact Verification System

**Components**:
- `fact_extractor.py`: Extracts factual claims from generated resume
- `fact_verifier.py`: Verifies claims against master resume

**Process**:
```python
1. Extract claims from generated resume
   - Work experience (companies, titles, dates)
   - Education (institutions, degrees, dates)
   - Skills (technical skills, tools)
   - Projects (names, technologies)

2. Verify against master resume
   - Exact match validation
   - Fuzzy matching for variations
   - Hallucination detection

3. If hallucinations found:
   - Format detailed feedback
   - Retry generation with corrections
   - Max 2 retry attempts
```

**Hallucination Categories**:
- Company name mismatches
- Job title fabrications
- Date inconsistencies
- Skill exaggerations
- Project inventions

### 5. Template Rendering (`template_renderer.py`)

**Purpose**: Convert JSON data to LaTeX using Jinja2 templates.

**Key Methods**:
```python
def render_resume(resume_data, job_title, company_name)
    # Renders resume.jinja2 template
    
def render_cover_letter(contact_info, cover_letter_text, ...)
    # Renders cover_letter.jinja2 template
    
def render_resume_with_referral(resume_data, referral_contact, ...)
    # Renders resume with referral contact info
```

**Template Features**:
- LaTeX escaping (special characters)
- Conditional sections (optional fields)
- Dynamic formatting (dates, phone numbers)
- ATS-optimized layout

### 6. Progress Tracking (`progress_tracker.py`)

**Purpose**: Real-time progress visualization and failure tracking.

**Features**:
- Rich table display with live updates
- Per-job step tracking (12 steps)
- Shadow failure tracking (retries that succeeded)
- Incident logging to `learnings.yaml`

**Tracked Metrics**:
- Jobs processed / total
- Current step per job
- Retry attempts (API, validation, quality)
- Failure reasons and recovery

### 7. Utility Functions (`utils.py`)

**Purpose**: Common operations used across the pipeline.

**Key Functions**:
```python
def load_yaml(path) / save_yaml(path, data)
def load_json(path) / save_json(path, data)
def load_prompt_template(name)
def compile_latex_to_pdf(tex_path, output_dir, doc_type)
def cleanup_output_directory(output_dir, ...)
def remove_reasoning_traces(text, enabled)
```

---

## Processing Pipeline (Detailed)

### Phase 1: Intelligence Gathering

**Step 1: Job Resonance Analysis**
```python
Input: Job description, company name
Output: JobResonanceAnalysis
  - emotional_keywords (3-15 items)
  - cultural_values (2+ items)
  - hidden_requirements (2+ items)
  - power_verbs (3+ items)
  - technical_keywords (3+ items)

Validation: Pydantic + quality thresholds
Retry: Max 2 attempts with error feedback
Bot: Configurable (default: Gemini-2.5-Pro)
```

**Step 2: Company Research**
```python
Input: Company name, job description
Output: CompanyResearch
  - mission_statement (20+ chars)
  - core_values (2-10 items)
  - tech_stack (array)
  - culture_keywords (array)
  - recent_news (optional)

Validation: Pydantic + quality thresholds
Retry: Max 2 attempts with error feedback
Bot: Configurable (default: Claude-3.5-Sonnet)
```

### Phase 2: Content Generation

**Step 3: Storytelling Arc Generation**
```python
Input: Job description, company research, job resonance, resume
Output: StorytellingArc
  - hook (50+ chars)
  - bridge (50+ chars)
  - proof_points (2-3 items, 30+ chars each)
  - vision (50+ chars)
  - call_to_action (20+ chars)

Validation: Pydantic + quality thresholds
Retry: Max 2 attempts with error feedback
Bot: Configurable (default: claude-haiku-4.5)
```

**Step 4: Resume Generation**
```python
Input: Job description, master resume, job resonance
Output: TailoredResume (Pydantic model)

Process:
1. Generate resume JSON (with humanization if enabled)
2. Extract JSON from response
3. Validate with Pydantic (character limits, formats)
4. Verify facts against master resume
5. If validation fails: retry with error feedback (max 2)

Validation Layers:
- JSON parsing
- Pydantic schema validation
- Fact verification (hallucination detection)
- Character limit enforcement

Bot: Configurable (default: gemini-3-pro)
```

**Note**: Fact verification is integrated into resume generation and runs automatically after Pydantic validation. If hallucinations are detected, the resume generation step is retried with detailed feedback.

**Step 5: Cover Letter Generation**
```python
Input: Resume, job description, storytelling arc, company research
Output: Cover letter text

Process:
1. Generate cover letter (with humanization if enabled)
2. Validate minimum length (200+ chars)
3. If validation fails: retry with quality feedback (max 2)

Validation: Quality thresholds (length, coherence)
Bot: Configurable (default: claude-haiku-4.5)
```

### Phase 3: Rendering & Compilation

**Step 6-7: LaTeX Rendering**
```python
Templates: resume.jinja2, cover_letter.jinja2

Process:
1. Load Jinja2 template
2. Inject resume/cover letter data
3. Apply LaTeX escaping
4. Render to .tex file

Features:
- Special character escaping
- Conditional sections
- Dynamic formatting
- ATS-optimized layout
```

**Step 8-9: PDF Compilation**
```python
Compiler: pdflatex

Process:
1. Run pdflatex on .tex file
2. Check for compilation errors
3. If errors: fail (no retry, check LaTeX log)
4. Rename PDF to final name format

Output Format:
FirstName_LastName_Company_JobID_Resume.pdf
FirstName_LastName_Company_JobID_Cover_Letter.pdf
```

**Step 10-11: Referral Documents (Optional)**
```python
Condition: referral_contact.json exists and valid

Process:
1. Load referral contact info (email, phone)
2. Render resume with referral contact
3. Render cover letter with referral contact
4. Compile referral PDFs

Output Format:
Referral_FirstName_LastName_Company_JobID_Resume.pdf
Referral_FirstName_LastName_Company_JobID_Cover_Letter.pdf

Graceful Degradation: Skips if referral_contact.json missing
```

### Phase 4: Output Organization

**Step 12: Cleanup**
```python
Process:
1. Create debug/ subdirectory
2. Move all non-PDF files to debug/
   - .tex files
   - .json files
   - .txt files
   - .log files
   - .aux files
3. Keep only PDFs in main output directory

Result: Clean output directory with only final PDFs
```

**Note**: Status update happens as part of step 12 cleanup process, marking the job as "processed" in applications.yaml.

---

## Concurrent Execution Model

### Semaphore-Based Concurrency

```python
# Configuration
max_concurrent_jobs = 10  # From config.json

# Implementation
semaphore = asyncio.Semaphore(max_concurrent_jobs)

async def process_with_limit(job):
    async with semaphore:
        return await process_job(job, tracker, live)

# Execute all jobs concurrently
results = await asyncio.gather(
    *[process_with_limit(job) for job in pending_jobs],
    return_exceptions=True
)
```

**How It Works**:
1. Semaphore limits concurrent jobs to configured maximum
2. Each job runs independently (no shared state)
3. Failures in one job don't affect others
4. Progress tracker updates in real-time

**Performance**:
- Sequential (v4.1): 100 jobs × 75s = 125 minutes
- Concurrent (v4.2): 100 jobs ÷ 10 = 12.5 minutes
- **10x speedup** with zero quality compromise

**Why This Works**:
- Each job is independent (no shared state)
- Intelligence gathering is I/O-bound (API calls)
- PDF compilation is CPU-bound but short
- Validation is deterministic (no race conditions)

---

## Error Handling & Recovery

### Retry Strategy

**API Retries** (Exponential Backoff):
```python
Attempt 1: Immediate
Attempt 2: Wait 2 seconds
Max Attempts: 2

Retry Triggers:
- Network errors
- API timeouts
- Rate limiting
- Server errors
```

**Validation Retries** (Progressive Feedback):
```python
Attempt 1: Base prompt
Attempt 2: Base prompt + error feedback
Max Attempts: 2

Retry Triggers:
- JSON parsing errors
- Pydantic validation errors
- Fact verification failures
- Quality threshold failures
```

### Failure Logging

**learnings.yaml Structure**:
```yaml
incidents:
  - timestamp: ISO 8601
    step_name: "Resume Generation"
    job_id: "job_123"
    company_name: "TechCorp"
    attempt: 2
    failure_type: "validation"
    details:
      error_count: 3
      errors:
        - field: "work_experience.0.bullet_points.0"
          message: "String should have at most 118 characters"
          type: "string_too_long"
```

**Failure Types**:
- `input`: Invalid job data
- `json_parsing`: Invalid JSON response
- `validation`: Pydantic validation errors
- `fact_verification`: Hallucination detection
- `quality`: Quality threshold failures
- `latex_compilation`: PDF compilation errors
- `api`: API call failures

### Shadow Failure Tracking

**Purpose**: Track retries that eventually succeeded.

**Metrics**:
- Total retry attempts per job
- Retry reasons (API, validation, quality)
- Recovery success rate
- Time to recovery

**Output**: Detailed report at end of pipeline run

---

## Configuration System

### config.json Structure

```json
{
  "max_concurrent_jobs": 10,
  
  "intelligence_steps": {
    "job_resonance_analysis": {
      "bot_name": "claude-haiku-4.5",
      "parameters": {
        "thinking_budget": 0
      }
    },
    "company_research": {
      "bot_name": "claude-haiku-4.5",
      "parameters": {
        "thinking_budget": 0,
        "web_search": true
      }
    },
    "storytelling_arc": {
      "bot_name": "claude-haiku-4.5",
      "parameters": {
        "thinking_budget": 0
      }
    }
  },
  
  "resume_generation": {
    "bot_name": "gemini-3-pro",
    "parameters": {
      "thinking_level": "low"
    }
  },
  
  "cover_letter_generation": {
    "bot_name": "claude-haiku-4.5",
    "parameters": {
      "thinking_budget": 0
    }
  },
  
  "humanization": {
    "enabled": true,
    "levels": {
      "resume": "medium",
      "cover_letter": "high"
    }
  },
  
  "reasoning_trace": false,
  
  "file_paths": {
    "applications": "data/applications.yaml",
    "master_resume": "profile/master_resume.json"
  }
}
```

### Environment Variables (.env)

```bash
POE_API_KEY=your_api_key_here
DEBUG_MODE=false
LOG_LEVEL=INFO
```

---

## Data Flow

### Input Data

**applications.yaml**:
```yaml
applications:
  - job_id: "job_001"
    job_title: "Senior Software Engineer"
    company_name: "TechCorp"
    job_description: "Full job description..."
    status: "pending"
```

**master_resume.json**:
```json
{
  "contact_info": { ... },
  "work_experience": [ ... ],
  "education": [ ... ],
  "skills": [ ... ],
  "projects": [ ... ]
}
```

### Output Data

**Directory Structure**:
```
output/
└── TechCorp_Senior_Software_Engineer_job_001/
    ├── John_Doe_TechCorp_job_001_Resume.pdf
    ├── John_Doe_TechCorp_job_001_Cover_Letter.pdf
    ├── Referral_John_Doe_TechCorp_job_001_Resume.pdf (optional)
    ├── Referral_John_Doe_TechCorp_job_001_Cover_Letter.pdf (optional)
    └── debug/
        ├── Resume.json
        ├── Resume.tex
        ├── CoverLetter.txt
        ├── CoverLetter.tex
        ├── Job_Resonance_Analysis.json
        ├── Company_Research.json
        └── Storytelling_Arc.json
```

---

## Performance Characteristics

### Processing Time

**Per Job** (average):
- Intelligence gathering: 20-30s
- Content generation: 25-35s
- Rendering & compilation: 10-15s
- **Total**: 60-90s per job

**Concurrent** (10 jobs):
- Wall clock time: ~90s (limited by longest job)
- Throughput: ~10 jobs/minute
- **100 jobs**: ~12.5 minutes

### Resource Usage

**Memory**:
- Base: ~200MB
- Per concurrent job: ~50MB
- **10 concurrent**: ~700MB total

**CPU**:
- Intelligence gathering: Low (I/O-bound)
- PDF compilation: High (CPU-bound, short bursts)
- Average utilization: 30-50%

**Network**:
- API calls: ~5-10 per job
- Bandwidth: Minimal (text-based)
- Rate limiting: Handled by Poe API

---

### Quality Guarantees

### Validation Success Rate

**Overall**: >99.5% after self-healing

**By Layer**:
- Pydantic validation: ~98% first attempt, >99.5% after retry
- Fact verification: ~95% first attempt, >99% after retry
- Quality thresholds: ~97% first attempt, >99.5% after retry
- LaTeX compilation: >99.9% (rare failures)

### ATS Compatibility

**Character Limits** (enforced):
- Bullet points: ≤ 118 chars
- Skills per category: ≤ 85 chars
- Summary: ≤ 425 chars
- Project descriptions: ≤ 200 chars

**Format Standardization**:
- Phone numbers: (XXX) XXX-XXXX
- Dates: Month YYYY
- Locations: City, State

**LaTeX Safety**:
- Special character escaping
- No illegal characters
- ATS-friendly formatting

---

## Extension Points

### Adding New Intelligence Steps

1. Create prompt template in `prompts/`
2. Define Pydantic model in `models.py`
3. Add configuration to `config.json`
4. Call `_call_intelligence_step_with_retry()` in pipeline

### Adding New Validation Rules

1. Add custom validator to Pydantic model
2. Update `_validate_intelligence_output()` for quality checks
3. Add error feedback templates

### Adding New Output Formats

1. Create Jinja2 template in `templates/`
2. Add rendering method to `template_renderer.py`
3. Add compilation logic to pipeline

---

## Related Documentation

- [Pipeline Details](PIPELINE.md) - Step-by-step processing flow
- [Validation System](VALIDATION.md) - All validation layers
- [Fact Verification](FACT_VERIFICATION.md) - Hallucination detection
- [Humanization](HUMANIZATION.md) - Content humanization system
- [Configuration](CONFIGURATION.md) - Setup and customization
- [Templates](TEMPLATES.md) - Jinja2 and LaTeX templates

---

**Architecture Version**: v4.2+ (Fact Verification)  
**Last Updated**: October 27, 2025
