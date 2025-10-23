# Development Guide

This guide explains the engineering decisions, design patterns, and development workflow for Jobbernaut Tailor v4.x.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Design Decisions](#design-decisions)
3. [Pipeline Flow](#pipeline-flow)
4. [Data Models](#data-models)
5. [Validation System](#validation-system)
6. [Error Handling](#error-handling)
7. [Template System](#template-system)
8. [Intelligence Gathering](#intelligence-gathering)
9. [Development Workflow](#development-workflow)
10. [Testing Strategy](#testing-strategy)

## System Architecture

### Core Components

The system is built around three main pillars:

#### 1. Intelligence Pipeline
The intelligence pipeline gathers contextual information before generating content:
- **Job Resonance Analysis**: Extracts emotional keywords, cultural signals, and hidden requirements
- **Company Research**: Gathers company mission, values, and tech stack information
- **Storytelling Arc**: Creates narrative structure for cover letters

**Design Rationale**: By gathering intelligence first, the content generation models have rich context to create highly tailored outputs that resonate with the specific job and company culture.

#### 2. Content Generation Engine
Generates tailored resumes and cover letters using AI models:
- **Resume Generation**: Tailors master resume data to job requirements
- **Cover Letter Generation**: Creates compelling narratives using storytelling framework

**Design Rationale**: Separating intelligence gathering from content generation allows for model specialization. Fast models can analyze, while creative models focus on generation.

#### 3. Validation & Compilation System
Ensures ATS compatibility and produces final PDFs:
- **Pydantic Validation**: Enforces strict schema compliance
- **ATS Rules Engine**: Character limits, format standards, sanitization
- **LaTeX Compilation**: Professional PDF generation with metadata

**Design Rationale**: Multi-stage validation catches errors early, and self-healing capabilities reduce manual intervention.

## Design Decisions

### Why Pydantic for Validation?

**Problem**: AI models occasionally generate JSON with missing fields, wrong types, or invalid values.

**Solution**: Pydantic provides:
- Compile-time type checking via type hints
- Runtime validation with clear error messages
- Custom validators for ATS-specific rules
- Automatic sanitization of illegal characters

**Alternative Considered**: Manual JSON validation with dictionaries.
**Why Not**: Error-prone, no type safety, harder to maintain.

**Code Location**: `src/models.py`

### Why Character Limits?

**Problem**: ATS systems have parsing limits. Exceeding them causes content truncation or rejection.

**Research Findings**:
- Bullet points > 118 chars often get truncated
- Skills strings > 90 chars cause layout issues
- Category names > 30 chars break column alignment

**Solution**: Strict Pydantic validators enforce limits with clear error messages.

**Code Location**: 
- `src/models.py` - validators
- `docs/ARCHITECTURE.md` - limit specifications

### Why Intelligence Gathering Phase?

**Problem**: Generic resume tailoring produces shallow, obvious modifications.

**Solution**: Three-stage intelligence gathering:
1. **Job Resonance**: Identifies emotional language and cultural signals
2. **Company Research**: Adds authentic company-specific context
3. **Storytelling Arc**: Creates narrative framework for cover letters

**Impact**: Cover letters feel personal rather than templated, increasing response rates.

**Code Location**: 
- `src/main.py` - `analyze_job_resonance()`, `research_company()`, `generate_storytelling_arc()`
- `prompts/` - intelligence gathering prompts

### Why Multiple AI Models?

**Problem**: No single AI model excels at all tasks.

**Solution**: Model specialization via `config.json`:
- **Gemini-2.5-Pro**: Resume generation (technical accuracy, JSON structure)
- **Claude-Sonnet-4-Search**: Company research (web search, synthesis)
- **Claude-Haiku-4.5**: Fast intelligence tasks (cost-effective)

**Benefits**:
- Performance optimization (fast models for simple tasks)
- Cost optimization (expensive models only where needed)
- Quality optimization (best model for each task)

**Configuration**: `config.json` - `intelligence_steps`, `resume_generation`, `cover_letter_generation`

### Why Retry Logic with Error Feedback?

**Problem**: AI models sometimes fail validation on first attempt.

**Solution**: Progressive error feedback system:
1. **Attempt 1**: Clean prompt
2. **Validation Failure**: Extract Pydantic errors
3. **Attempt 2**: Original prompt + error feedback at top
4. **Success**: Save validated output

**Design Pattern**: Top-injection of errors (not appending) for better model attention.

**Success Rate**: >99.5% after 2 attempts.

**Code Location**: 
- `src/main.py` - `_call_intelligence_step_with_retry()`, `_build_simple_error_feedback()`
- `src/main.py` - Resume generation retry loop (lines 855-955)

### Why LaTeX Instead of HTML/Word?

**Problem**: Need professional, ATS-compatible PDFs with precise formatting.

**Comparison**:
| Feature | LaTeX | HTML/CSS | Word |
|---------|-------|----------|------|
| Precise spacing | ✅ | ❌ | ❌ |
| Professional typography | ✅ | ⚠️ | ⚠️ |
| Version control | ✅ | ✅ | ❌ |
| Programmatic generation | ✅ | ✅ | ❌ |
| ATS compatibility | ✅ | ⚠️ | ⚠️ |
| Rich metadata | ✅ | ⚠️ | ❌ |

**Solution**: LaTeX with Jinja2 templates provides:
- Pixel-perfect layout control
- Professional typography (Helvetica font family)
- Rich PDF metadata for searchability
- Clean version control (text files)
- Repeatable builds

**Code Location**:
- `templates/*.jinja2` - Template definitions
- `latex/*.cls` - LaTeX class files
- `src/template_renderer.py` - Rendering logic

### Why Humanization as Optional Feature?

**Problem**: AI-generated text can sound robotic or overly formal.

**Solution**: Optional humanization with three levels (low, medium, high):
- Modular: Enable/disable per document type
- Configurable: Adjust tone intensity
- Transparent: Clearly separated in prompts

**Design Rationale**: Not all use cases need humanization. Some industries prefer formal tone. Making it optional provides flexibility.

**Configuration**: `config.json` - `humanization` section

**Code Location**:
- `src/main.py` - `_apply_humanization()`
- `prompts/humanization_*.txt` - Humanization instructions

### Why Reasoning Trace Removal?

**Problem**: Some AI models include internal reasoning in output (`<thinking>...</thinking>` blocks).

**Solution**: Configurable post-processing to strip reasoning traces:
- Preserves clean JSON for validation
- Reduces token consumption in downstream processing
- Optional: Keep traces for debugging

**Configuration**: `config.json` - `reasoning_trace: false`

**Code Location**: 
- `src/utils.py` - `remove_reasoning_traces()`
- `src/main.py` - Applied in `call_poe_api()`

### Why Referral Document Generation?

**Problem**: Referrals often require different contact information.

**Solution**: Optional referral documents with separate contact info:
- Main PDFs: Personal contact info
- Referral PDFs: Referrer's contact info for internal routing

**Use Case**: When a friend/colleague submits your resume internally, HR contacts them first, then you.

**Configuration**: `profile/referral_contact.json` (optional file)

**Code Location**: 
- `src/main.py` - `_load_referral_contact()`, referral PDF generation (lines 1096-1158)
- `src/template_renderer.py` - `render_resume_with_referral()`, `render_cover_letter_with_referral()`

## Pipeline Flow

### Complete 12-Step Process

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT VALIDATION                          │
│  - Job title length (3-200 chars)                           │
│  - Company name length (2-100 chars)                        │
│  - Job description length (100-50K chars)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              INTELLIGENCE GATHERING PHASE                    │
│                                                              │
│  Step 1: Job Resonance Analysis                             │
│  ├── Extract emotional keywords (3-15 items)                │
│  ├── Identify cultural values (2+ items)                    │
│  ├── Find hidden requirements (2+ items)                    │
│  ├── List power verbs (3+ items)                            │
│  └── Extract technical keywords (3+ items)                  │
│                                                              │
│  Step 2: Company Research                                   │
│  ├── Mission statement (20+ chars)                          │
│  ├── Core values (2-10 items)                               │
│  ├── Tech stack                                             │
│  ├── Culture keywords                                       │
│  └── Domain context                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 RESUME GENERATION                            │
│                                                              │
│  Step 3: Generate Resume JSON                               │
│  ├── Call AI with job resonance context                     │
│  ├── Extract JSON from response                             │
│  ├── Validate with Pydantic (TailoredResume)               │
│  │   ├── Contact info format validation                     │
│  │   ├── Education fields (graduation_date, not end_date)   │
│  │   ├── Work experience (3 entries, 4 bullets each)        │
│  │   ├── Projects (3 entries, 4 bullets each)               │
│  │   ├── Skills (category ≤30, values ≤90 chars)           │
│  │   └── Bullet points (≤118 chars each)                   │
│  ├── On failure: Inject error feedback and retry (max 2)    │
│  └── Save validated Resume.json                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            STORYTELLING ARC GENERATION                       │
│                                                              │
│  Step 4: Generate Storytelling Arc                          │
│  ├── Synthesize intelligence + tailored resume              │
│  ├── Create narrative structure:                            │
│  │   ├── Hook (50+ chars)                                   │
│  │   ├── Bridge (50+ chars)                                 │
│  │   ├── Proof points (2-3, each 30+ chars)                │
│  │   ├── Vision (50+ chars)                                 │
│  │   └── Call to action (20+ chars)                         │
│  └── Validate and save Storytelling_Arc.json                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│             COVER LETTER GENERATION                          │
│                                                              │
│  Step 5: Generate Cover Letter Text                         │
│  ├── Call AI with all intelligence context                  │
│  ├── Quality validation (≥200 chars)                        │
│  ├── On failure: Inject feedback and retry (max 2)          │
│  └── Save CoverLetter.txt                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 LATEX RENDERING                              │
│                                                              │
│  Step 6: Render Resume LaTeX                                │
│  ├── Load Jinja2 template (templates/resume.jinja2)        │
│  ├── Inject validated resume data                           │
│  ├── Apply LaTeX escaping for special characters            │
│  └── Save Resume.tex                                         │
│                                                              │
│  Step 7: Render Cover Letter LaTeX                          │
│  ├── Load Jinja2 template (templates/cover_letter.jinja2)  │
│  ├── Inject contact info + cover letter text                │
│  ├── Apply LaTeX escaping                                   │
│  └── Save CoverLetter.tex                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  PDF COMPILATION                             │
│                                                              │
│  Step 8: Compile Resume PDF                                 │
│  ├── pdflatex Resume.tex                                    │
│  ├── Inject PDF metadata (author, title, keywords)          │
│  └── Rename to: FirstName_LastName_Company_JobID_Resume.pdf │
│                                                              │
│  Step 9: Compile Cover Letter PDF                           │
│  ├── pdflatex CoverLetter.tex                               │
│  ├── Inject PDF metadata                                    │
│  └── Rename to: FirstName_LastName_Company_JobID_CoverLetter.pdf │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          REFERRAL DOCUMENTS (Optional)                       │
│                                                              │
│  Step 10: Create Referral LaTeX Files                       │
│  ├── Check if referral_contact.json exists                  │
│  ├── If yes: Render with referral contact info              │
│  └── Save Referral_Resume.tex, Referral_CoverLetter.tex    │
│                                                              │
│  Step 11: Compile Referral Resume PDF                       │
│  └── Save: Referral_FirstName_LastName_Company_JobID_Resume.pdf │
│                                                              │
│  Step 12: Compile Referral Cover Letter PDF                 │
│  └── Save: Referral_FirstName_LastName_Company_JobID_CoverLetter.pdf │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      CLEANUP                                 │
│                                                              │
│  Step 13: Organize Output Directory                         │
│  ├── Keep: *.pdf files in main directory                    │
│  ├── Move to debug/: *.json, *.txt, *.tex, *.log, *.aux    │
│  └── Update job status to "processed"                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ✅ COMPLETE
```

### Data Flow Diagram

```
┌──────────────┐
│ applications │
│   .yaml      │──────┐
└──────────────┘      │
                      │
┌──────────────┐      │     ┌─────────────────────┐
│master_resume │      ├────→│ResumeOptimization   │
│    .json     │──────┘     │    Pipeline         │
└──────────────┘            └─────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │Job Resonance │  │   Company    │  │ Storytelling │
          │   Analysis   │  │   Research   │  │     Arc      │
          └──────────────┘  └──────────────┘  └──────────────┘
                    │                 │                 │
                    └────────┬────────┴────────┬────────┘
                             ↓                 ↓
                    ┌──────────────┐  ┌──────────────┐
                    │   Resume     │  │Cover Letter  │
                    │  Generation  │  │  Generation  │
                    └──────────────┘  └──────────────┘
                             │                 │
                             ↓                 ↓
                    ┌──────────────┐  ┌──────────────┐
                    │    LaTeX     │  │    LaTeX     │
                    │   Rendering  │  │   Rendering  │
                    └──────────────┘  └──────────────┘
                             │                 │
                             ↓                 ↓
                    ┌──────────────┐  ┌──────────────┐
                    │     PDF      │  │     PDF      │
                    │ Compilation  │  │ Compilation  │
                    └──────────────┘  └──────────────┘
                             │                 │
                             └────────┬────────┘
                                      ↓
                             ┌──────────────┐
                             │Final Output  │
                             │  Directory   │
                             └──────────────┘
```

## Data Models

### Model Hierarchy

```
TailoredResume (Root Model)
├── contact_info: ContactInfo
│   ├── first_name: str
│   ├── last_name: str
│   ├── phone: str (validated format: (XXX) XXX-XXXX)
│   ├── email: str
│   ├── location: str
│   ├── linkedin_url: str
│   ├── github_url: str
│   └── portfolio_url: str
├── professional_summaries: str (must be empty)
├── education: List[Education] (min 1 entry)
│   └── Education
│       ├── institution: str
│       ├── degree: str
│       ├── start_date: str
│       ├── graduation_date: str (NOT end_date!)
│       └── gpa: str (should be empty)
├── skills: Dict[str, str] (category -> skills)
│   └── Validation: category ≤30 chars, skills ≤90 chars
├── work_experience: List[WorkExperience] (exactly 3)
│   └── WorkExperience
│       ├── job_title: str
│       ├── company: str
│       ├── start_date: str
│       ├── end_date: str
│       ├── location: Optional[str]
│       └── bullet_points: List[str] (exactly 4, each ≤118 chars)
└── projects: List[Project] (exactly 3)
    └── Project
        ├── project_name: str
        ├── technologies: List[str] (joined ≤70 chars)
        ├── project_url: str
        ├── description: Optional[str]
        └── bullet_points: List[str] (exactly 4, each ≤118 chars)

JobResonanceAnalysis
├── emotional_keywords: List[str] (3-15 items)
├── cultural_values: List[str] (2+ items)
├── hidden_requirements: List[str] (2+ items)
├── power_verbs: List[str] (3+ items)
└── technical_keywords: List[str] (3+ items)

CompanyResearch
├── company_name: str
├── mission_statement: str (20+ chars)
├── core_values: List[str] (2-10 items)
├── tech_stack: List[str]
├── culture_keywords: List[str]
├── recent_news: str
├── mission_keywords: List[str]
└── domain_context: str

StorytellingArc
├── hook: str (50+ chars)
├── bridge: str (50+ chars)
├── proof_points: List[str] (2-3 items, each 30+ chars)
├── vision: str (50+ chars)
└── call_to_action: str (20+ chars)
```

### Field Validators

All models use Pydantic validators for:
1. **Type Safety**: Ensures correct Python types
2. **Length Constraints**: Enforces character limits
3. **Format Validation**: Phone numbers, dates, URLs
4. **Sanitization**: Removes ATS-incompatible characters
5. **Business Rules**: e.g., professional_summaries must be empty

**Code Location**: `src/models.py`

## Validation System

### Three-Layer Validation Architecture

#### Layer 1: Pydantic Schema Validation
- **When**: Immediately after JSON parsing
- **What**: Type checking, required fields, basic constraints
- **Errors**: Clear field-level error messages

#### Layer 2: Custom Field Validators
- **When**: During Pydantic validation
- **What**: ATS character limits, format standards, sanitization
- **Errors**: Specific validation rules (e.g., "Bullet point 1 exceeds 118 characters")

#### Layer 3: Quality Thresholds
- **When**: After Pydantic validation passes
- **What**: Minimum array sizes, meaningful content checks
- **Errors**: High-level quality requirements

### ATS Compatibility Rules

The validation system enforces strict ATS compatibility:

#### Character Sanitization
```python
# Removed characters: <>[]{}\|~^
illegal_chars = r'[<>\[\]{}\\|~^]'
cleaned = re.sub(illegal_chars, '', text)
```

**Rationale**: These characters break LaTeX compilation and confuse ATS parsers.

#### Phone Number Standardization
```python
# Input: Various formats (919-672-2226, (919) 672-2226, 9196722226)
# Output: (919) 672-2226 (ATS-preferred)
```

**Rationale**: Consistent formatting improves ATS parsing accuracy.

#### Date Format
```python
# Format: "Month YYYY" or "Month YYYY - Month YYYY"
# Example: "January 2020 - Present"
```

**Rationale**: Human-readable format preferred by recruiters, parsed correctly by ATS.

### Retry Logic

When validation fails:

1. **Extract Errors**: Parse Pydantic ValidationError
2. **Build Feedback**: Create concise error summary
3. **Inject at Top**: Prepend errors to original prompt
4. **Retry**: Call AI model again with corrective guidance
5. **Max Attempts**: 2 retries (total 3 attempts)

**Success Rate**: 99.5%+ after retries

**Code Location**: 
- `src/main.py` - `_call_intelligence_step_with_retry()` (lines 542-657)
- `src/main.py` - `_build_simple_error_feedback()` (lines 457-488)

## Error Handling

### Incident Logging System

All validation failures are logged to `learnings.yaml`:

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

**Purpose**: Track common failure patterns to improve prompts and validation rules.

**Code Location**: `src/main.py` - `_log_validation_failure()` (lines 490-540)

### Error Recovery Strategies

#### JSON Parsing Errors
- **Cause**: AI includes text outside JSON block
- **Recovery**: Extract JSON from markdown code blocks (````json ... ````)
- **Feedback**: "Please ensure your response contains ONLY valid JSON"

#### Pydantic Validation Errors
- **Cause**: Missing fields, wrong types, constraint violations
- **Recovery**: Inject field-level errors into prompt
- **Feedback**: Structured error list with field paths

#### Quality Threshold Errors
- **Cause**: Content too short, arrays too small
- **Recovery**: Request more detailed content
- **Feedback**: "Field X is too short (min Y chars, got Z chars)"

#### LaTeX Compilation Errors
- **Cause**: Special characters, malformed LaTeX syntax
- **Prevention**: Character sanitization in validators
- **Fallback**: Save .log file for debugging

## Template System

### Jinja2 Template Architecture

#### Resume Template (`templates/resume.jinja2`)

**Structure**:
```latex
\documentclass{resume}  % Custom LaTeX class
\usepackage[...]{geometry}  % Page margins
\usepackage[...]{hyperref}  % PDF metadata

\begin{document}

% Contact Header
\VAR{contact_info.first_name} \VAR{contact_info.last_name}
\href{mailto:\VAR{contact_info.email}}{\VAR{contact_info.email}}

% Education Section
\BLOCK{for edu in education}
  \VAR{edu.institution} | \VAR{edu.degree}
  \VAR{edu.start_date} - \VAR{edu.graduation_date}
\BLOCK{endfor}

% Skills Section
\BLOCK{for category, skills in skills.items()}
  \textbf{\VAR{category}}: \VAR{skills}
\BLOCK{endfor}

% Work Experience Section
\BLOCK{for exp in work_experience}
  \textbf{\VAR{exp.job_title}} | \VAR{exp.company}
  \VAR{exp.start_date} - \VAR{exp.end_date}
  \BLOCK{for bullet in exp.bullet_points}
    \item \VAR{bullet}
  \BLOCK{endfor}
\BLOCK{endfor}

% Projects Section (similar structure)

\end{document}
```

**Key Features**:
- `\VAR{...}`: Variable interpolation with automatic LaTeX escaping
- `\BLOCK{...}`: Control flow (loops, conditionals)
- Custom filters: `|latex_escape`, `|join(', ')`

#### Cover Letter Template (`templates/cover_letter.jinja2`)

**Structure**:
```latex
\documentclass{coverletter}

% Contact header (same as resume)
% Current date
% Hiring manager info

\begin{letter}

\VAR{cover_letter_text}  % Free-form text generated by AI

\closing{Sincerely,\\
\VAR{contact_info.first_name} \VAR{contact_info.last_name}}

\end{letter}
```

### LaTeX Class Files

#### Resume Class (`latex/resume.cls`)

**Key Definitions**:
```latex
% Section formatting
\newcommand{\rSection}[1]{
  \section*{\MakeUppercase{#1}}
  \hrule
}

% Experience entry
\newcommand{\rExperience}[4]{
  \textbf{#1} \hfill #2\\
  \textit{#3} \hfill #4
}

% Bullet list spacing
\newcommand{\rBulletList}{
  \begin{itemize}
  \itemsep -3pt {}  % Tight spacing for ATS
}
```

**Design Rationale**: Consistent formatting across all resumes, easy to modify globally.

#### Cover Letter Class (`latex/coverletter.cls`)

**Key Definitions**:
```latex
% Letter environment
\newenvironment{letter}{
  % Setup
}{
  % Cleanup
}

% Closing signature
\newcommand{\closing}[1]{
  \vspace{1em}
  #1
}
```

### Rendering Process

1. **Load Template**: Read Jinja2 template file
2. **Create Environment**: Configure Jinja2 with LaTeX syntax
3. **Inject Data**: Pass validated dictionary to template
4. **Escape Characters**: Automatic LaTeX escaping for special characters
5. **Render**: Generate complete LaTeX document
6. **Save**: Write .tex file to output directory

**Code Location**: `src/template_renderer.py`

## Intelligence Gathering

### Why Three Stages?

Traditional resume tailoring focuses on keyword matching. The intelligence gathering phase goes deeper:

#### Stage 1: Job Resonance Analysis
**Purpose**: Understand the *emotional* and *cultural* signals in the job description.

**Extracts**:
- Emotional keywords: "passionate", "innovative", "ownership"
- Cultural values: "collaborative", "fast-paced", "data-driven"
- Hidden requirements: "startup mentality", "ambiguity tolerance"
- Power verbs: "architected", "spearheaded", "optimized"
- Technical keywords: For ATS optimization

**Why It Matters**: Companies don't just want skills—they want culture fit. This analysis ensures the resume resonates emotionally.

**Code Location**: `src/main.py` - `analyze_job_resonance()` (lines 659-696)

#### Stage 2: Company Research
**Purpose**: Build authentic connection with the company's mission and values.

**Extracts**:
- Mission statement
- Core values
- Tech stack
- Culture keywords
- Domain context

**Why It Matters**: Generic cover letters get rejected. Company-specific details demonstrate genuine interest.

**Code Location**: `src/main.py` - `research_company()` (lines 698-733)

#### Stage 3: Storytelling Arc
**Purpose**: Create a compelling narrative structure for the cover letter.

**Structure**:
1. **Hook**: Opening that creates emotional connection
2. **Bridge**: Transition to candidate's story
3. **Proof Points**: 2-3 specific stories demonstrating fit
4. **Vision**: Forward-looking statement about impact
5. **Call to Action**: Invitation to conversation

**Why It Matters**: Story-driven cover letters are memorable. Data-driven proof points build credibility.

**Code Location**: `src/main.py` - `generate_storytelling_arc()` (lines 735-778)

### Model Specialization Strategy

Different intelligence tasks require different model capabilities:

| Task | Model | Rationale |
|------|-------|-----------|
| Job Resonance | Claude-Haiku-4.5 | Fast, cost-effective for simple extraction |
| Company Research | Claude-Sonnet-4-Search | Web search capability for real-time data |
| Storytelling Arc | Claude-Haiku-4.5 | Creative narrative generation |
| Resume Generation | Gemini-2.5-Pro | Technical accuracy, structured JSON output |
| Cover Letter | Claude-Haiku-4.5 | Natural language generation |

**Configuration**: `config.json` allows per-task model selection with custom parameters.

## Development Workflow

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone https://github.com/Jobbernaut/jobbernaut-tailor.git
cd jobbernaut-tailor

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your POE_API_KEY

# 5. Prepare profile data
# Edit profile/master_resume.json with your information
# (Optional) Edit profile/referral_contact.json for referral documents

# 6. Configure pipeline
# Edit config.json to select AI models and parameters

# 7. Add job applications
# Edit data/applications.yaml with job details

# 8. Run pipeline
python src/main.py
```

### Project Structure

```
jobbernaut-tailor/
├── config.json              # Pipeline configuration
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (API keys)
├── .gitignore              # Git ignore patterns
├── README.md               # Project overview
├── data/
│   ├── applications.yaml    # Job applications queue
│   └── application_template.yaml  # Template for new jobs
├── profile/
│   ├── master_resume.json   # Your complete resume data
│   └── referral_contact.json  # Optional referral contact info
├── prompts/
│   ├── analyze_job_resonance.txt     # Job analysis prompt
│   ├── research_company.txt          # Company research prompt
│   ├── generate_storytelling_arc.txt # Storytelling prompt
│   ├── generate_resume.txt           # Resume generation prompt
│   ├── generate_cover_letter.txt     # Cover letter prompt
│   └── humanization_*.txt            # Humanization prompts
├── templates/
│   ├── resume.jinja2        # Resume LaTeX template
│   └── cover_letter.jinja2  # Cover letter LaTeX template
├── latex/
│   ├── resume.cls           # Resume LaTeX class
│   └── coverletter.cls      # Cover letter LaTeX class
├── src/
│   ├── main.py              # Main pipeline orchestration
│   ├── models.py            # Pydantic data models
│   ├── utils.py             # Helper functions
│   ├── template_renderer.py # Jinja2 template rendering
│   └── main_intelligence_methods.py  # Intelligence methods reference
├── docs/
│   ├── ARCHITECTURE.md      # System architecture documentation
│   ├── CONFIGURATION.md     # Configuration guide
│   └── DEVELOPMENT.md       # Development guide (this file)
└── output/
    └── {job_id}_{company}/  # Generated PDFs and debug files
```

### Adding a New Job

1. Open `data/applications.yaml`
2. Add new job entry:

```yaml
- job_id: "job_123"
  status: "pending"  # pending | processed | skipped
  job_title: "Senior Software Engineer"
  company_name: "Example Corp"
  job_description: |
    Full job description text here...
    Multiple lines supported.
```

3. Run pipeline: `python src/main.py`
4. Check output in `output/job_123_Example_Corp/`

### Customizing Prompts

All prompts support placeholder substitution:

**Example**: `prompts/generate_resume.txt`
```
You are an expert resume writer...

Job Description:
[JOB_DESCRIPTION]

Master Resume:
[MASTER_RESUME_JSON]

Company: [COMPANY_NAME]

Job Resonance Analysis:
[JOB_RESONANCE_ANALYSIS]

Instructions: ...
```

**Available Placeholders**:
- `[JOB_DESCRIPTION]`: Full job description text
- `[COMPANY_NAME]`: Company name
- `[MASTER_RESUME_JSON]`: Your master resume data
- `[JOB_RESONANCE_ANALYSIS]`: Job resonance analysis results
- `[COMPANY_RESEARCH]`: Company research results
- `[STORYTELLING_ARC]`: Storytelling arc structure
- `[TAILORED_RESUME_JSON]`: Generated tailored resume

### Modifying Templates

#### To change resume layout:

Edit `templates/resume.jinja2`:
```latex
% Add new section
\begin{rSection}{CERTIFICATIONS}
\BLOCK{for cert in certifications}
  \textbf{\VAR{cert.name}} | \VAR{cert.issuer} | \VAR{cert.date}
\BLOCK{endfor}
\end{rSection}
```

#### To change global styling:

Edit `latex/resume.cls`:
```latex
% Change font
\renewcommand{\familydefault}{\rmdefault}  % Serif font

% Change margins
\geometry{left=0.6in, right=0.6in, top=0.6in, bottom=0.6in}

% Change section header style
\renewcommand{\rSection}[1]{
  \section*{\textsc{#1}}  % Small caps instead of uppercase
}
```

### Debugging

#### Enable Debug Mode

In `config.json`:
```json
{
  "debug": {
    "save_intermediate": true,
    "verbose_logging": true
  }
}
```

#### Debug File Locations

After running pipeline, check `output/{job_id}_{company}/debug/`:
- `*_Raw_Attempt_*.txt`: Raw AI responses
- `*_Attempt_*.json`: Extracted JSON (before validation)
- `*_INVALID_*.json`: Failed validation attempts
- `Resume.tex`, `CoverLetter.tex`: Generated LaTeX
- `*.log`: LaTeX compilation logs

#### Common Issues

**Issue**: "Phone number must be 10 digits"
- **Cause**: Invalid phone format in master_resume.json
- **Fix**: Use format: `(XXX) XXX-XXXX` or `XXX-XXX-XXXX`

**Issue**: "Bullet point exceeds 118 characters"
- **Cause**: AI generated bullet point too long
- **Fix**: Automatic retry with error feedback (no action needed)
- **If persists**: Adjust prompt to emphasize character limits

**Issue**: "Failed to compile PDF"
- **Cause**: Special characters in content, LaTeX syntax errors
- **Fix**: Check `*.log` file in debug/ directory
- **Prevention**: Validators should catch this—report as bug

**Issue**: "Pydantic validation failed after 2 attempts"
- **Cause**: AI model not following schema
- **Fix**: Check `Resume_INVALID_Attempt_*.json` for patterns
- **Action**: Improve prompt clarity or try different model

## Testing Strategy

### Manual Testing

The system currently relies on manual testing:

1. **Unit Tests**: Run pipeline with sample job
2. **Validation Tests**: Verify Pydantic models catch errors
3. **Template Tests**: Check LaTeX rendering with various data
4. **Integration Tests**: End-to-end pipeline execution

### Future Automated Testing

Proposed test structure:

```
tests/
├── test_models.py           # Pydantic model validation tests
├── test_utils.py            # Utility function tests
├── test_template_renderer.py  # Template rendering tests
├── test_pipeline.py         # Pipeline orchestration tests
└── fixtures/
    ├── sample_resume.json
    ├── sample_job.yaml
    └── expected_outputs/
```

### Test Cases to Implement

#### Model Validation Tests
- Valid resume passes validation
- Invalid phone number rejected
- Bullet point exceeds 118 chars rejected
- Skills category exceeds 30 chars rejected
- Empty professional_summaries accepted
- Non-empty professional_summaries rejected

#### Template Rendering Tests
- LaTeX special characters escaped correctly
- All template variables interpolated
- Loops generate correct number of sections
- Conditional sections work (e.g., optional description)

#### Pipeline Tests
- Input validation catches invalid jobs
- Retry logic recovers from validation failures
- Intelligence gathering produces valid models
- PDF compilation succeeds with sample data
- Cleanup moves non-PDF files correctly

#### Integration Tests
- Full pipeline execution with sample job
- Multiple jobs processed in sequence
- Referral documents generated when config present
- Humanization applied when enabled

### Running Tests (Future)

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_phone_validation
```

## Contributing

### Code Style

- **Python**: Follow PEP 8
- **Line Length**: 100 characters (except long strings)
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Required for all function signatures

### Commit Message Convention

```
type(scope): Short description

Longer explanation if needed.

Fixes #issue_number
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Add or update tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(validation): Add character limit validator for skills

Adds custom Pydantic validator to enforce 90-character limit
on skills string values for ATS compatibility.

Fixes #45

---

docs(architecture): Document LaTeX compilation process

Adds detailed explanation of PDF generation pipeline and
metadata injection in ARCHITECTURE.md.
```

### Pull Request Process

1. Create feature branch: `git checkout -b feat/your-feature`
2. Make changes and commit: `git commit -m "feat: description"`
3. Push branch: `git push origin feat/your-feature`
4. Open pull request on GitHub
5. Address review feedback
6. Merge after approval

### Adding New Features

#### Example: Add Certifications Section

1. **Update Models** (`src/models.py`):
```python
class Certification(BaseModel):
    name: str
    issuer: str
    date: str
    url: Optional[str] = None

class TailoredResume(BaseModel):
    # ... existing fields ...
    certifications: List[Certification] = Field(default_factory=list)
```

2. **Update Master Resume** (`profile/master_resume.json`):
```json
{
  "certifications": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon Web Services",
      "date": "January 2023",
      "url": "https://..."
    }
  ]
}
```

3. **Update Template** (`templates/resume.jinja2`):
```latex
\BLOCK{if certifications}
\begin{rSection}{CERTIFICATIONS}
\BLOCK{for cert in certifications}
  \textbf{\VAR{cert.name}} | \VAR{cert.issuer} | \VAR{cert.date}
  \BLOCK{if cert.url}
    | \href{\VAR{cert.url}}{\VAR{cert.url|replace('https://', '')}}
  \BLOCK{endif}
\BLOCK{endfor}
\end{rSection}
\BLOCK{endif}
```

4. **Update Prompt** (`prompts/generate_resume.txt`):
```
... existing instructions ...

Certifications Section (if applicable):
- Include relevant certifications
- Format: name, issuer, date
- Optional: URL to credential
```

5. **Test**:
- Add certification to master_resume.json
- Run pipeline with test job
- Verify certification appears in PDF
- Check LaTeX escaping of special characters

## Performance Optimization

### Current Performance Metrics

- **Average Processing Time**: 60-90 seconds per job
- **Validation Success Rate**: >99.5% after retries
- **API Calls**: 6-8 per job (intelligence + generation + retries)
- **Token Consumption**: ~15K tokens per job (varies by model)

### Optimization Opportunities

#### 1. Parallel Intelligence Gathering
**Current**: Sequential execution (job resonance → company research → storytelling)
**Opportunity**: Run job resonance and company research in parallel
**Savings**: ~15-20 seconds per job

#### 2. Response Caching
**Current**: Every job makes fresh API calls
**Opportunity**: Cache company research by company name
**Savings**: Significant for repeat applications to same company

#### 3. Model Selection
**Current**: High-capability models for all tasks
**Opportunity**: Use faster/cheaper models for simple tasks
**Savings**: 30-50% cost reduction, 20-30% time reduction

#### 4. Prompt Optimization
**Current**: Long, detailed prompts
**Opportunity**: Optimize prompt length while maintaining quality
**Savings**: 10-20% token reduction

### Monitoring

Track these metrics to measure optimization impact:
- Processing time per job
- API call count per job
- Token consumption per job
- Validation success rate
- First-attempt success rate (no retries needed)

## Troubleshooting Guide

### Problem: Pipeline crashes with "POE_API_KEY not found"

**Cause**: Missing or invalid API key

**Solution**:
1. Create `.env` file: `cp .env.example .env`
2. Add your key: `POE_API_KEY=your_key_here`
3. Verify: `cat .env` (should show your key)

### Problem: "Failed to compile PDF"

**Cause**: LaTeX installation missing or incomplete

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra

# macOS
brew install mactex

# Windows
# Download and install MiKTeX from miktex.org
```

**Verify**:
```bash
pdflatex --version  # Should show version info
```

### Problem: Bullet points consistently exceed 118 characters

**Cause**: AI model not respecting character limits

**Solution**:
1. Edit `prompts/generate_resume.txt`
2. Emphasize character limits:
```
CRITICAL: Each bullet point MUST be ≤118 characters.
Use a character counter to verify BEFORE generating JSON.
```
3. Try different model (e.g., switch to Claude-Sonnet-4.5)

### Problem: Cover letter sounds generic

**Cause**: Insufficient intelligence gathering or model selection

**Solution**:
1. Enable web search for company research:
```json
{
  "intelligence_steps": {
    "company_research": {
      "bot_name": "Claude-Sonnet-4-Search",
      "parameters": {
        "web_search": true
      }
    }
  }
}
```
2. Increase thinking budget for storytelling arc:
```json
{
  "intelligence_steps": {
    "storytelling_arc": {
      "parameters": {
        "thinking_budget": 2048
      }
    }
  }
}
```

### Problem: "graduation_date" field error

**Cause**: Model generated "end_date" instead of "graduation_date"

**Solution**: Automatic retry should fix this. If persists:
1. Check `prompts/generate_resume.txt`
2. Verify it says "graduation_date" not "end_date"
3. Update prompt if incorrect

### Problem: Processing hangs/times out

**Cause**: Network issues, API rate limiting, or model overload

**Solution**:
1. Check internet connection
2. Verify API key is valid: `echo $POE_API_KEY`
3. Check Poe API status
4. Retry with different model
5. Increase retry attempts in code (if needed)

## Next Steps

### Recommended Learning Path

1. **Understand Data Flow**: Trace a job through the pipeline
2. **Experiment with Prompts**: Modify prompts and observe output changes
3. **Customize Templates**: Adjust LaTeX layout to your preference
4. **Add Features**: Implement certifications, publications, etc.
5. **Optimize Performance**: Profile and optimize bottlenecks
6. **Contribute**: Submit improvements back to the project

### Advanced Topics

- **Custom Validators**: Create domain-specific validation rules
- **Prompt Engineering**: Improve prompt quality and reduce retries
- **Template Theming**: Create multiple resume styles
- **Multi-language Support**: Generate resumes in different languages
- **Analytics Dashboard**: Track application outcomes and optimize
- **CI/CD Integration**: Automate testing and deployment

---

## Appendix

### Useful Commands

```bash
# View job queue
cat data/applications.yaml

# Check output directory
ls -la output/

# View last generated resume
ls -t output/*/debug/*.pdf | head -1 | xargs open  # macOS
ls -t output/*/debug/*.pdf | head -1 | xargs xdg-open  # Linux

# Clean all output directories
rm -rf output/*/

# Reset job statuses to pending
sed -i 's/status: processed/status: pending/g' data/applications.yaml

# Check LaTeX installation
pdflatex --version
```

### References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [LaTeX Documentation](https://www.latex-project.org/help/documentation/)
- [Poe API Documentation](https://developer.poe.com/)
- [ATS Best Practices](https://www.jobscan.co/blog/8-things-you-need-to-know-about-applicant-tracking-systems/)

### Glossary

- **ATS**: Applicant Tracking System - Software used by companies to filter and rank resumes
- **Pydantic**: Python data validation library using type hints
- **LaTeX**: Document preparation system for high-quality typesetting
- **Jinja2**: Template engine for Python
- **Intelligence Gathering**: Pre-generation analysis phase to understand job context
- **Storytelling Arc**: Narrative structure for cover letters
- **Validation Layer**: Schema, field, and quality validation stages
- **Self-Healing**: Automatic error recovery through retry with feedback

---

*Last Updated: October 2025*
*Version: 4.1*
