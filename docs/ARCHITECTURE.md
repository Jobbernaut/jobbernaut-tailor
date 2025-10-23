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

## Future Extensibility

The v4.1 architecture supports:
1. Additional intelligence models
2. Custom validation rules
3. New output formats
4. Enhanced ATS optimization
5. Template customization
6. PDF metadata configuration

For configuration details and customization options, see [CONFIGURATION.md](CONFIGURATION.md).
