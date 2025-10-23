# Jobbernaut Tailor Architecture

## Intelligence Pipeline Overview

The v4.1 pipeline implements a sophisticated 12-step process with strict validation gates and self-healing capabilities:

1. Job Resonance Analysis
2. Company Research
3. Storytelling Arc Generation
4. Resume JSON Generation
5. Cover Letter Text Generation
6. Resume LaTeX Rendering
7. Cover Letter LaTeX Rendering
8. Resume PDF Compilation
9. Cover Letter PDF Compilation
10. Referral Document Generation (Optional)
11. Quality Validation
12. Output Organization

## Validation Architecture

### ATS Compatibility Engine

The system enforces strict character limits and formatting rules:

```python
# Work Experience Bullet Points
max_length = 118  # ATS parsing threshold
min_bullets = 4   # Optimal content density
max_bullets = 4   # Prevent overflow

# Skills Section
category_length = 30  # Category name limit
skills_length = 85    # Skills string limit

# Project Section
tech_stack_length = 65  # Combined technologies limit
```

### Field-Specific Validators

Custom Pydantic validators ensure ATS compatibility:

1. **Contact Information**
   - Phone format: (XXX) XXX-XXXX
   - Email validation
   - Location sanitization

2. **Work Experience**
   - Date format standardization
   - Location field sanitization
   - Bullet point validation

3. **Projects**
   - Technology stack length checks
   - URL validation
   - Description sanitization

### Intelligence Models

#### 1. JobResonanceAnalysis
```python
class JobResonanceAnalysis(BaseModel):
    emotional_keywords: List[str]  # Emotional resonance
    cultural_values: List[str]     # Company culture
    hidden_requirements: List[str]  # Implicit needs
    power_verbs: List[str]         # Action words
    technical_keywords: List[str]   # Hard skills
```

#### 2. CompanyResearch
```python
class CompanyResearch(BaseModel):
    mission_statement: str
    core_values: List[str]
    tech_stack: List[str]
    culture_keywords: List[str]
    domain_context: str
```

#### 3. StorytellingArc
```python
class StorytellingArc(BaseModel):
    hook: str            # Opening impact
    bridge: str          # Transition
    proof_points: List[str]  # Evidence
    vision: str          # Future impact
    call_to_action: str  # Closing
```

## Anti-Fragile Error Recovery System

The v4.1 pipeline implements sophisticated error handling with progressive feedback:

1. **Validation Retries**
   - Maximum 3 attempts per stage
   - Progressive error feedback injection
   - Context preservation across retries
   - JSON parsing error guidance
   - Field-specific Pydantic fixes
   - Quality threshold feedback

2. **Self-Healing Capabilities**
   - Automatic character sanitization
   - Format standardization (dates, phone numbers)
   - Length adjustment with content preservation
   - Illegal character removal
   - Field-specific validation fixes

3. **Quality Thresholds**
   - Minimum content length requirements
   - Array size constraints (e.g., 4 bullet points)
   - No empty strings or generic content
   - Format verification (LaTeX, JSON)
   - ATS compatibility validation

4. **Fail-Fast Input Validation**
   - Job title: 3-200 characters
   - Company name: 2-100 characters
   - Job description: 100-50,000 characters
   - Immediate rejection of invalid inputs
   - Clear error messages for quick fixes

## Intelligence Pipeline Architecture

The v4.1 system implements a sophisticated 3-stage intelligence gathering phase before content generation:

### 1. Job Resonance Analysis
```python
class JobResonanceAnalysis(BaseModel):
    emotional_keywords: List[str]  # 3-15 items
    cultural_values: List[str]     # 2+ items
    hidden_requirements: List[str]  # 2+ items
    power_verbs: List[str]         # 3+ items
    technical_keywords: List[str]   # 3+ items
```

### 2. Company Research
```python
class CompanyResearch(BaseModel):
    mission_statement: str         # 20+ chars
    core_values: List[str]        # 2-10 items
    tech_stack: List[str]         # No empty strings
    culture_keywords: List[str]    # No empty strings
    domain_context: str           # Meaningful content
```

### 3. Storytelling Arc
```python
class StorytellingArc(BaseModel):
    hook: str                     # 50+ chars
    bridge: str                   # 50+ chars
    vision: str                   # 50+ chars
    call_to_action: str          # 20+ chars
    proof_points: List[str]       # 2-3 items, 30+ chars each
```

## Performance Optimizations

### 1. Processing Architecture
- Parallel validation gates
- Cached template rendering
- Optimized LaTeX compilation
- Configurable AI model selection per step

### 2. Error Prevention
- Pre-validation input checks
- Progressive format standardization
- Intelligent character sanitization
- Quality threshold enforcement

### 3. Quality Assurance
- Multi-stage content verification
- Strict validation thresholds
- Format consistency enforcement
- ATS compatibility validation

## System Components

### 1. Core Engine
- Intelligence gathering
- Content generation
- Validation system

### 2. Template System
- LaTeX rendering
- PDF compilation
- Format standardization

### 3. Storage System
- Job history tracking
- Output organization
- Debug information

## Integration Points

### 1. AI Models
- Poe API integration
- Model-specific parameters
- Response validation

### 2. File System
- Output organization
- Debug information
- Template management

### 3. Configuration
- Model selection
- Validation rules
- Output formatting

## LaTeX Architecture

The system employs a sophisticated LaTeX generation pipeline that ensures consistent, ATS-optimized PDFs:

### 1. Custom LaTeX Classes
```latex
% Professional formatting with ATS-friendly spacing
\documentclass{resume}  % or coverletter
\usepackage[left=0.4in,top=0.4in,right=0.4in,bottom=0.4in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
```

### 2. Jinja2 Template Layer
```jinja2
% Smart variable interpolation
\VAR{contact_info.first_name|latex_escape}

% Conditional formatting
\BLOCK{if project.technologies}
| \VAR{project.technologies|join(', ')|latex_escape}
\BLOCK{endif}
```

### 3. ATS Optimizations
```latex
% Precise spacing for optimal parsing
\itemsep -3pt {}

% Clean URL handling
\href{\VAR{url|latex_escape}}{\VAR{url|replace('https://', '')|latex_escape}}

% Standardized section headers
\begin{rSection}{EXPERIENCE}
```

### 4. Unified Template System
```latex
% Shared configuration across templates
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[left=0.4in,top=0.4in,right=0.4in,bottom=0.4in]{geometry}
```

### 5. PDF Metadata Optimization
```latex
% Rich PDF metadata for improved searchability
\usepackage[pdftex,
    pdfauthor={\VAR{contact_info.first_name} \VAR{contact_info.last_name}},
    pdftitle={...},
    pdfsubject={...},
    pdfkeywords={Software Development Engineer, Resume},
    pdfproducer={LaTeX},
    pdfcreator={pdflatex}
]{hyperref}
```

### 6. Generation Pipeline
1. Template Rendering
   - Jinja2 processes templates
   - LaTeX escaping for special characters
   - URL sanitization and formatting
   - Contact info standardization

2. LaTeX Compilation
   - pdflatex with hyperref support
   - UTF-8 encoding for universal compatibility
   - Rich metadata injection
   - Hyperlinked contact information

3. Quality Validation
   - Character encoding validation
   - Structure verification
   - Format consistency checks
   - Hyperlink validation
   - PDF metadata verification

## Troubleshooting Common Issues

### Validation Failures

**Problem**: Bullet points consistently exceed 118 characters

**Root Cause**: AI model not respecting character limits in prompt

**Solution**:
1. Check `prompts/generate_resume.txt` emphasizes character limits
2. Try different AI model (e.g., switch to Claude-Sonnet-4.5)
3. Increase thinking_budget for better reasoning:
   ```json
   {
     "resume_generation": {
       "parameters": {
         "thinking_budget": 4096
       }
     }
   }
   ```

**Problem**: "graduation_date" field errors

**Root Cause**: Model generating "end_date" instead of "graduation_date"

**Solution**: Automatic retry should fix. If persists, update prompt to emphasize correct field name.

**Problem**: Empty or generic intelligence outputs

**Root Cause**: Insufficient model capability or web search disabled

**Solution**:
1. Enable web search for company research:
   ```json
   {
     "intelligence_steps": {
       "company_research": {
         "parameters": {
           "web_search": true
         }
       }
     }
   }
   ```
2. Use higher-capability model (e.g., Claude-Sonnet-4-Search)

### PDF Compilation Issues

**Problem**: LaTeX compilation fails with special characters

**Root Cause**: Character not properly escaped

**Solution**: Validators should sanitize automatically. If not, check `src/models.py` validators.

**Problem**: PDF layout looks wrong

**Root Cause**: LaTeX class file or template issue

**Solution**:
1. Check `.log` file in debug/ directory for LaTeX errors
2. Verify LaTeX class files are present in `latex/` directory
3. Test LaTeX manually:
   ```bash
   cd output/job_id_company/debug/
   pdflatex Resume.tex
   ```

### Performance Issues

**Problem**: Pipeline takes >5 minutes per job

**Root Cause**: High thinking budgets or slow AI models

**Solution**:
1. Reduce thinking budgets:
   ```json
   {
     "intelligence_steps": {
       "job_resonance_analysis": {
         "parameters": {
           "thinking_budget": 0  // Faster
         }
       }
     }
   }
   ```
2. Use faster models (e.g., Claude-Haiku-4.5 instead of Sonnet)

**Problem**: High API costs

**Root Cause**: Using expensive models for all tasks

**Solution**: Use model specialization strategy (see DEVELOPMENT.md)

## System Limits and Constraints

### Character Limits (ATS Compatibility)

| Field | Limit | Rationale |
|-------|-------|-----------|
| Bullet points | 118 chars | ATS parsing threshold |
| Skills category | 30 chars | Column alignment |
| Skills value | 90 chars | Layout constraints |
| Technologies (joined) | 70 chars | Single line display |
| Professional summary | 0 chars (empty) | Maximize content space |

### Array Size Constraints

| Array | Min | Max | Rationale |
|-------|-----|-----|-----------|
| Work experience | 3 | 3 | Optimal detail level |
| Projects | 3 | 3 | Optimal detail level |
| Bullet points (per entry) | 4 | 4 | Consistent structure |
| Education | 1 | N/A | At least one degree |
| Emotional keywords | 3 | 15 | Meaningful analysis |
| Core values | 2 | 10 | Reasonable range |
| Proof points | 2 | 3 | Cover letter length |

### Processing Constraints

| Resource | Limit | Rationale |
|----------|-------|-----------|
| Max retries | 2 | Balance quality vs. time |
| API timeout | 120 sec | Prevent hanging |
| Job description | 100-50K chars | Reasonable job posting size |
| Job title | 3-200 chars | Valid title range |
| Company name | 2-100 chars | Valid name range |

## Security Considerations

### API Key Management

**Best Practices**:
- Store API keys in `.env` file
- Never commit `.env` to version control
- Use environment variable injection in CI/CD
- Rotate keys periodically

**Implementation**:
```python
# src/main.py
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("POE_API_KEY")
if not api_key:
    raise ValueError("POE_API_KEY not found")
```

### Input Validation

**Threat**: Malicious job descriptions with code injection attempts

**Mitigation**:
- Strict Pydantic validation
- Character sanitization in validators
- LaTeX escaping for special characters
- Length limits on all inputs

**Example**:
```python
# Illegal characters removed
illegal_chars = r'[<>\[\]{}\\|~^]'
cleaned = re.sub(illegal_chars, '', text)
```

### File System Safety

**Threat**: Path traversal attacks in output directories

**Mitigation**:
- Use `os.path.join()` for path construction
- Sanitize job_id and company_name
- Never use user input directly in file paths

**Implementation**:
```python
# Safe path construction
safe_job_id = re.sub(r'[^a-zA-Z0-9_-]', '', job_id)
safe_company = re.sub(r'[^a-zA-Z0-9_-]', '', company_name)
output_dir = os.path.join("output", f"{safe_job_id}_{safe_company}")
```

## Monitoring and Observability

### Logging Strategy

**Log Levels**:
- **INFO**: Pipeline progress, step completion
- **WARNING**: Validation retries, recoverable errors
- **ERROR**: Unrecoverable failures

**Log Outputs**:
- Console: Real-time feedback
- `learnings.yaml`: Validation failure tracking
- Debug files: Detailed API responses

### Key Metrics to Track

**Success Metrics**:
- Validation success rate (target: >99%)
- First-attempt success rate (target: >90%)
- Processing time per job (target: <90 seconds)
- API cost per job

**Failure Metrics**:
- Most common validation errors
- Most problematic fields
- Retry frequency by step
- LaTeX compilation errors

### Example: Monitoring Script

```python
# scripts/analyze_learnings.py
import yaml
from collections import Counter

with open('learnings.yaml') as f:
    learnings = yaml.safe_load(f)

incidents = learnings.get('incidents', [])

# Count errors by field
error_fields = []
for incident in incidents:
    for error in incident['errors']:
        error_fields.append(error['field'])

print("Most common validation errors:")
for field, count in Counter(error_fields).most_common(10):
    print(f"  {field}: {count}")
```

## Scalability Considerations

### Current Limitations

- **Sequential processing**: One job at a time
- **No caching**: Every job makes fresh API calls
- **No load balancing**: Single process

### Scaling Strategies

#### 1. Parallel Processing

```python
# Future implementation
import asyncio

async def process_jobs_parallel(jobs, max_concurrent=3):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_limit(job):
        async with semaphore:
            return await process_job(job)
    
    results = await asyncio.gather(*[
        process_with_limit(job) for job in jobs
    ])
    return results
```

#### 2. Response Caching

```python
# Future implementation
import hashlib
import json

def get_cache_key(company_name):
    return hashlib.sha256(company_name.encode()).hexdigest()

def cached_company_research(company_name):
    cache_key = get_cache_key(company_name)
    cache_file = f"cache/company_{cache_key}.json"
    
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)
    
    # Make API call
    result = await research_company(company_name)
    
    # Cache result
    with open(cache_file, 'w') as f:
        json.dump(result, f)
    
    return result
```

#### 3. Distributed Processing

```python
# Future implementation using Celery
from celery import Celery

app = Celery('jobbernaut', broker='redis://localhost:6379')

@app.task
def process_job_task(job_data):
    pipeline = ResumeOptimizationPipeline()
    return pipeline.process_job(job_data)

# Queue multiple jobs
for job in pending_jobs:
    process_job_task.delay(job)
```

## Future Extensibility

The v4.1 architecture supports:

### 1. Additional Intelligence Models

**Example: Salary Analysis**
```python
class SalaryAnalysis(BaseModel):
    salary_range: str
    equity_mentioned: bool
    benefits_highlights: List[str]
    market_comparison: str

async def analyze_compensation(job_description: str) -> dict:
    # Intelligence gathering for salary negotiation
    pass
```

### 2. Custom Validation Rules

**Example: Industry-Specific Validators**
```python
class TechResumeValidator:
    @field_validator('skills')
    def validate_tech_skills(cls, v):
        # Ensure key technologies are present
        required_tech = ['Python', 'AWS', 'Docker']
        skills_str = str(v.values())
        for tech in required_tech:
            if tech not in skills_str:
                print(f"Warning: {tech} not in skills")
        return v
```

### 3. New Output Formats

**Example: HTML Resume**
```python
def render_resume_html(resume_data: dict) -> str:
    template = env.get_template('resume.html.jinja2')
    return template.render(**resume_data)
```

### 4. Enhanced ATS Optimization

**Example: ATS Scoring**
```python
def calculate_ats_score(resume_data: dict, job_description: str) -> float:
    """Calculate predicted ATS compatibility score."""
    # Analyze keyword density
    # Check formatting compliance
    # Validate field presence
    return score  # 0.0 to 1.0
```

### 5. Template Customization

**Example: Multiple Resume Styles**
```python
TEMPLATES = {
    'modern': 'resume_modern.jinja2',
    'classic': 'resume_classic.jinja2',
    'minimal': 'resume_minimal.jinja2'
}

def render_resume(resume_data: dict, style='modern'):
    template_file = TEMPLATES.get(style, TEMPLATES['modern'])
    return renderer.render(template_file, resume_data)
```

### 6. PDF Metadata Configuration

**Example: Custom Metadata**
```python
def add_pdf_metadata(pdf_path: str, metadata: dict):
    """Add custom metadata to PDF."""
    # Author, Title, Subject, Keywords
    # Creation date, modification date
    # Custom properties
    pass
```

## Related Documentation

For more detailed information, see:
- [DEVELOPMENT.md](DEVELOPMENT.md) - Design decisions and engineering details
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration guide and examples
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history and breaking changes

---

*Last Updated: October 2025*
*Version: 4.1*
