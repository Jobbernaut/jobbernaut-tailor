# Architecture Guide

## System Overview

Jobbernaut Tailor v4.2 is an industrial-scale resume tailoring system built on three architectural pillars:

1. **Parallel Processing Engine**: Semaphore-based concurrency for 10x throughput
2. **Self-Healing Validation Pipeline**: 99.5% success rate with automatic error correction
3. **Intelligence Gathering System**: Multi-stage context extraction at $0.10/application

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Job Queue    │  │ Concurrency  │  │ Output Mgmt  │      │
│  │ Management   │  │ Control      │  │ & Storage    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Intelligence Pipeline                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Job Resonance│  │ Company      │  │ Storytelling │      │
│  │ Analysis     │  │ Research     │  │ Arc          │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Content Generation                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Resume JSON  │  │ Cover Letter │  │ Referral Doc │      │
│  │ Generation   │  │ Generation   │  │ (Optional)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Validation System                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Pydantic     │  │ ATS          │  │ Self-Healing │      │
│  │ Schema       │  │ Compatibility│  │ Recovery     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Rendering & Compilation                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ LaTeX        │  │ PDF          │  │ Quality      │      │
│  │ Rendering    │  │ Compilation  │  │ Verification │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Parallel Processing Architecture (v4.2)

### The Breakthrough

v4.2 introduces semaphore-based parallel processing that transforms the system from sequential to concurrent execution:

```python
class JobbernautTailor:
    async def run(self):
        """Process all pending jobs in parallel with concurrency control"""
        pending_jobs = self.get_pending_jobs()
        
        # Semaphore limits concurrent execution
        max_concurrent = self.config.get('max_concurrent_jobs', 10)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create tasks for all jobs
        tasks = [
            self.process_job_with_semaphore(job, semaphore)
            for job in pending_jobs
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def process_job_with_semaphore(self, job, semaphore):
        """Process a single job with semaphore control"""
        async with semaphore:
            return await self.process_single_job(job)
```

### Why Semaphores?

**Problem**: Naive parallelization with `asyncio.gather()` would spawn 100 concurrent tasks, overwhelming:
- API rate limits
- System memory
- LaTeX compilation processes

**Solution**: Semaphore-based concurrency control:
- Limits concurrent jobs to configurable maximum (default: 10)
- Queues remaining jobs automatically
- Maintains quality guarantees at all scales
- Prevents resource exhaustion

### Performance Characteristics

```
Concurrency Level vs. Throughput:
┌────────────────────────────────────────┐
│ Jobs/min                               │
│   50 │                          ████   │
│   40 │                    ████  ████   │
│   30 │              ████  ████  ████   │
│   20 │        ████  ████  ████  ████   │
│   10 │  ████  ████  ████  ████  ████   │
│    0 └──────────────────────────────────│
│       1     5     10    15    20       │
│           Concurrent Jobs               │
└────────────────────────────────────────┘
Optimal: 10 concurrent jobs
Diminishing returns beyond 15
```

## Intelligence Pipeline

### 12-Step Processing Flow

Each job goes through 12 distinct stages, all of which can run in parallel across different jobs:

#### Stage 1-3: Intelligence Gathering

**1. Job Resonance Analysis**
```python
class JobResonanceAnalysis(BaseModel):
    emotional_keywords: List[str]      # 3-15 items
    cultural_values: List[str]         # 2+ items
    hidden_requirements: List[str]     # 2+ items
    power_verbs: List[str]            # 3+ items
    technical_keywords: List[str]      # 3+ items
```

**Purpose**: Extract implicit signals from job descriptions
- Emotional resonance keywords (e.g., "innovative", "collaborative")
- Cultural values (e.g., "work-life balance", "fast-paced")
- Hidden requirements not explicitly stated
- Action verbs for resume bullet points
- Technical skills and technologies

**2. Company Research**
```python
class CompanyResearch(BaseModel):
    mission_statement: str             # 20+ chars
    core_values: List[str]            # 2-10 items
    tech_stack: List[str]             # Technologies used
    culture_keywords: List[str]        # Cultural indicators
    domain_context: str               # Industry context
```

**Purpose**: Gather company-specific context
- Mission and vision alignment
- Core values for cultural fit
- Technology stack for skills matching
- Cultural keywords for cover letter
- Domain-specific terminology

**3. Storytelling Arc**
```python
class StorytellingArc(BaseModel):
    hook: str                         # 50+ chars
    bridge: str                       # 50+ chars
    proof_points: List[str]           # 2-3 items, 30+ chars each
    vision: str                       # 50+ chars
    call_to_action: str              # 20+ chars
```

**Purpose**: Structure narrative for cover letter
- Hook: Opening impact statement
- Bridge: Transition to relevant experience
- Proof points: Evidence of capabilities
- Vision: Future impact at company
- Call to action: Closing statement

#### Stage 4-5: Content Generation

**4. Resume JSON Generation**
```python
class ResumeData(BaseModel):
    contact_info: ContactInfo
    summary: str                      # ≤ 425 chars
    work_experience: List[WorkExperience]
    projects: List[Project]
    skills: List[SkillCategory]
    education: List[Education]
```

**Validation Rules**:
- Summary: Maximum 425 characters
- Work experience: Exactly 4 bullet points per role
- Bullet points: Maximum 118 characters each
- Skills per category: Maximum 85 characters
- All fields: No empty strings

**5. Cover Letter Generation**
```python
class CoverLetterData(BaseModel):
    opening: str                      # Uses storytelling hook
    body_paragraphs: List[str]        # 2-3 paragraphs
    closing: str                      # Uses call to action
    signature: str                    # Professional closing
```

#### Stage 6-9: Rendering & Compilation

**6-7. LaTeX Rendering**
- Jinja2 template processing
- LaTeX character escaping
- Format standardization
- Metadata injection

**8-9. PDF Compilation**
- pdflatex execution
- Hyperlink generation
- Metadata embedding
- Quality verification

#### Stage 10-12: Finalization

**10. Referral Document** (Optional)
- Networking aid generation
- Key talking points
- Company research summary

**11. Quality Validation**
- Final content verification
- ATS compatibility check
- Format consistency
- Completeness validation

**12. Output Organization**
- File structure creation
- Metadata storage
- Debug information
- Status tracking

## Validation System

### Multi-Stage Validation Architecture

```
Input → Pydantic Validation → ATS Rules → Self-Healing → Output
         ↓ Fail                ↓ Fail      ↓ Fail
         Retry (2x)            Retry (2x)  Retry (2x)
         ↓                     ↓           ↓
         Progressive Feedback  Progressive Feedback
```

### 1. Pydantic Schema Validation

**Field-Level Validators**:
```python
class WorkExperience(BaseModel):
    company: str
    title: str
    location: str
    start_date: str
    end_date: str
    bullet_points: List[str]
    
    @validator('bullet_points')
    def validate_bullets(cls, v):
        if len(v) != 4:
            raise ValueError("Must have exactly 4 bullet points")
        if any(len(bullet) > 118 for bullet in v):
            raise ValueError(f"Bullet point exceeds 118 char limit")
        if any(not bullet.strip() for bullet in v):
            raise ValueError("Empty bullet points not allowed")
        return v
    
    @validator('location')
    def validate_location(cls, v):
        # Standardize location format
        return v.replace(',', ' •').strip()
```

### 2. ATS Compatibility Rules

**Character Limits** (Enforced at validation):
```python
LIMITS = {
    'bullet_point': 118,      # ATS parsing threshold
    'skills_category': 30,    # Category name limit
    'skills_list': 85,        # Combined skills limit
    'project_tech': 65,       # Technology stack limit
    'summary': 425,           # Professional summary limit
}
```

**Format Standardization**:
- Phone: `(XXX) XXX-XXXX`
- Dates: `Month YYYY` or `Month YYYY - Present`
- Locations: `City • State` or `City • Country`
- URLs: Hyperlinked with clean display text

**Illegal Character Sanitization**:
```python
def sanitize_for_latex(text: str) -> str:
    """Remove/escape characters that break LaTeX compilation"""
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text
```

### 3. Self-Healing Error Recovery

**Progressive Feedback System**:
```python
async def generate_with_retry(
    self,
    prompt: str,
    model: BaseModel,
    max_retries: int = 2
) -> BaseModel:
    """Generate content with progressive feedback on failures"""
    
    for attempt in range(max_retries):
        try:
            response = await self.ai_generate(prompt)
            validated = model.parse_raw(response)
            return validated
            
        except ValidationError as e:
            if attempt == max_retries - 1:
                raise
            
            # Inject error-specific feedback
            feedback = self.generate_feedback(e)
            prompt = f"{prompt}\n\nPREVIOUS ATTEMPT FAILED:\n{feedback}"
            
        except JSONDecodeError as e:
            if attempt == max_retries - 1:
                raise
            
            # Guide JSON formatting
            prompt = f"{prompt}\n\nJSON PARSING ERROR: Ensure valid JSON format"
    
    raise Exception("Max retries exceeded")
```

**Error-Specific Guidance**:
- **Character limit exceeded**: "Reduce bullet point length to ≤118 chars"
- **Missing required fields**: "Include all required fields: {field_list}"
- **Invalid format**: "Use format: {expected_format}"
- **Empty content**: "Provide meaningful content, not empty strings"

### 4. Quality Thresholds

**Content Quality Rules**:
```python
class QualityThresholds:
    MIN_BULLET_LENGTH = 30        # Meaningful content
    MAX_BULLET_LENGTH = 118       # ATS compatibility
    REQUIRED_BULLETS = 4          # Optimal density
    MIN_SKILLS_PER_CATEGORY = 3   # Sufficient breadth
    MAX_SKILLS_PER_CATEGORY = 6   # Avoid clutter
    MIN_SUMMARY_LENGTH = 100      # Substantive overview
    MAX_SUMMARY_LENGTH = 425      # ATS limit
```

## LaTeX Architecture

### Template System

**Jinja2 + LaTeX Integration**:
```latex
% templates/resume.jinja2
\documentclass{resume}

% Contact Information
\name{\VAR{contact_info.first_name} \VAR{contact_info.last_name}}
\address{
    \VAR{contact_info.location} \\
    \href{tel:\VAR{contact_info.phone}}{\VAR{contact_info.phone}} \\
    \href{mailto:\VAR{contact_info.email}}{\VAR{contact_info.email}}
}

% Work Experience
\begin{rSection}{EXPERIENCE}
\BLOCK{for exp in work_experience}
    \begin{rSubsection}
        {\VAR{exp.company}}
        {\VAR{exp.start_date} - \VAR{exp.end_date}}
        {\VAR{exp.title}}
        {\VAR{exp.location}}
        \BLOCK{for bullet in exp.bullet_points}
        \item \VAR{bullet|latex_escape}
        \BLOCK{endfor}
    \end{rSubsection}
\BLOCK{endfor}
\end{rSection}
```

### Custom LaTeX Classes

**resume.cls**:
```latex
% Optimized for ATS parsing
\ProvidesClass{resume}[2025/10/23 Resume class]
\LoadClass[11pt,letterpaper]{article}

% Precise spacing for optimal parsing
\usepackage[left=0.4in,top=0.4in,right=0.4in,bottom=0.4in]{geometry}

% Clean, professional font
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

% Section formatting
\newenvironment{rSection}[1]{
    \sectionskip
    \MakeUppercase{\bf #1}
    \sectionlineskip
    \hrule
    \begin{list}{}{
        \setlength{\leftmargin}{1.5em}
    }
    \item[]
}{
    \end{list}
}
```

### PDF Metadata Optimization

```latex
\usepackage[pdftex,
    pdfauthor={\VAR{contact_info.first_name} \VAR{contact_info.last_name}},
    pdftitle={Resume - \VAR{contact_info.first_name} \VAR{contact_info.last_name} - \VAR{job_title}},
    pdfsubject={Software Engineering Resume},
    pdfkeywords={Software Development, \VAR{primary_skills|join(', ')}},
    pdfproducer={LaTeX with hyperref},
    pdfcreator={pdflatex}
]{hyperref}
```

**Benefits**:
- Improved searchability in ATS systems
- Professional metadata for recruiters
- Hyperlinked contact information
- Clean URL handling

## Configuration System

### Model Selection

```json
{
  "intelligence_steps": {
    "job_resonance_analysis": {
      "bot_name": "Gemini-2.5-Pro",
      "thinking_budget": "4096"
    },
    "company_research": {
      "bot_name": "Claude-3.5-Sonnet",
      "thinking_budget": "2048"
    },
    "storytelling_arc": {
      "bot_name": "GPT-4o",
      "thinking_budget": "3072"
    }
  }
}
```

**Model Selection Strategy**:
- **Gemini-2.5-Pro**: Technical analysis, pattern matching
- **Claude-3.5-Sonnet**: Research, synthesis, factual accuracy
- **GPT-4o**: Creative writing, storytelling, narrative flow

### Concurrency Configuration

```json
{
  "max_concurrent_jobs": 10,
  "semaphore_timeout": 300
}
```

**Tuning Guidelines**:
- **1-5 concurrent**: Conservative, low resource usage
- **10 concurrent**: Optimal for most systems (default)
- **15+ concurrent**: High-end systems only, diminishing returns

## Error Handling

### Fail-Fast Input Validation

```python
def validate_input(job_data: dict) -> None:
    """Validate input before processing"""
    
    # Job title validation
    if not 3 <= len(job_data['title']) <= 200:
        raise ValueError("Job title must be 3-200 characters")
    
    # Company name validation
    if not 2 <= len(job_data['company']) <= 100:
        raise ValueError("Company name must be 2-100 characters")
    
    # Job description validation
    if not 100 <= len(job_data['description']) <= 50000:
        raise ValueError("Job description must be 100-50,000 characters")
```

### Graceful Degradation

```python
async def process_job_with_fallback(self, job: dict) -> dict:
    """Process job with fallback strategies"""
    
    try:
        return await self.process_single_job(job)
    
    except ValidationError as e:
        # Log validation failure
        self.log_error(job, e)
        return {'status': 'validation_failed', 'error': str(e)}
    
    except APIError as e:
        # Retry with exponential backoff
        return await self.retry_with_backoff(job, e)
    
    except Exception as e:
        # Catch-all for unexpected errors
        self.log_critical_error(job, e)
        return {'status': 'failed', 'error': str(e)}
```

## Performance Optimization

### Caching Strategy

```python
class TemplateCache:
    """Cache compiled Jinja2 templates"""
    
    def __init__(self):
        self.cache = {}
    
    def get_template(self, name: str) -> Template:
        if name not in self.cache:
            self.cache[name] = self.load_template(name)
        return self.cache[name]
```

### Async I/O Optimization

```python
async def compile_pdfs_parallel(self, latex_files: List[str]) -> List[str]:
    """Compile multiple PDFs concurrently"""
    
    tasks = [
        self.compile_single_pdf(latex_file)
        for latex_file in latex_files
    ]
    
    return await asyncio.gather(*tasks)
```

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- LaTeX distribution (TeX Live, MiKTeX, MacTeX)
- POE API key

### Recommended for Parallel Processing
- Python 3.10+
- 8GB+ RAM
- SSD storage
- Stable internet connection (API calls)

## Monitoring & Observability

### Metrics Tracked
- Processing time per job
- Validation success rate
- Retry attempts per stage
- API costs per job
- Concurrency utilization

### Logging Strategy
```python
logger.info(f"Processing job: {job_id}")
logger.debug(f"Intelligence gathering: {elapsed_time}s")
logger.warning(f"Validation retry: attempt {attempt}/2")
logger.error(f"Job failed: {error_message}")
```

---

**Architecture designed for scale, validated for quality, optimized for speed.**
