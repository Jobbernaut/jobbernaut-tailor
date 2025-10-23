# Contributing to Jobbernaut Tailor

Thank you for your interest in contributing to Jobbernaut Tailor! This guide will help you get started with development, testing, and submitting contributions.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Environment](#development-environment)
4. [Project Structure](#project-structure)
5. [Development Workflow](#development-workflow)
6. [Coding Standards](#coding-standards)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation](#documentation)
9. [Commit Guidelines](#commit-guidelines)
10. [Pull Request Process](#pull-request-process)
11. [Common Tasks](#common-tasks)
12. [Getting Help](#getting-help)

## Code of Conduct

This project values:
- **Respect**: Treat all contributors with respect
- **Collaboration**: Work together to improve the project
- **Quality**: Maintain high code quality standards
- **Learning**: Support each other's growth

## Getting Started

### Prerequisites

- **Python**: 3.9 or higher
- **LaTeX**: Full TeX distribution (TeX Live, MiKTeX, or MacTeX)
- **Git**: Version control
- **Poe API Key**: Required for AI model access

### Quick Setup

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/jobbernaut-tailor.git
cd jobbernaut-tailor

# 3. Add upstream remote
git remote add upstream https://github.com/Jobbernaut/jobbernaut-tailor.git

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Set up environment
cp .env.example .env
# Edit .env and add your POE_API_KEY

# 7. Verify installation
python src/main.py --help  # Should not error
pdflatex --version  # Should show LaTeX version
```

## Development Environment

### Recommended Tools

- **IDE**: VSCode, PyCharm, or similar with Python support
- **Extensions** (VSCode):
  - Python (Microsoft)
  - Pylance
  - Pylint
  - Black Formatter
  - LaTeX Workshop

### Environment Setup

#### Python Environment

```bash
# Create isolated environment
python -m venv venv

# Activate environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install black pylint pytest pytest-cov  # Optional: for linting/testing
```

#### LaTeX Installation

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

**macOS**:
```bash
brew install mactex
# Or download from: http://www.tug.org/mactex/
```

**Windows**:
- Download MiKTeX: https://miktex.org/download
- Run installer and choose "Complete" installation

#### Verify Installation

```bash
# Check Python
python --version  # Should be 3.9+

# Check LaTeX
pdflatex --version  # Should show pdfTeX version

# Check dependencies
pip list | grep pydantic  # Should show pydantic version
```

## Project Structure

```
jobbernaut-tailor/
├── .github/              # GitHub-specific files
├── config.json           # Pipeline configuration
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore patterns
├── README.md            # Project overview
├── data/                # Job applications
│   ├── applications.yaml
│   └── application_template.yaml
├── profile/             # User profile data
│   ├── master_resume.json
│   └── referral_contact.json
├── prompts/             # AI prompts
│   ├── analyze_job_resonance.txt
│   ├── research_company.txt
│   ├── generate_storytelling_arc.txt
│   ├── generate_resume.txt
│   ├── generate_cover_letter.txt
│   └── humanization_*.txt
├── templates/           # Jinja2 LaTeX templates
│   ├── resume.jinja2
│   └── cover_letter.jinja2
├── latex/              # LaTeX class files
│   ├── resume.cls
│   └── coverletter.cls
├── src/                # Source code
│   ├── main.py
│   ├── models.py
│   ├── utils.py
│   ├── template_renderer.py
│   └── main_intelligence_methods.py
├── docs/               # Documentation
│   ├── ARCHITECTURE.md
│   ├── CONFIGURATION.md
│   ├── DEVELOPMENT.md
│   ├── API_REFERENCE.md
│   └── CONTRIBUTING.md (this file)
└── output/             # Generated files (not in git)
    └── {job_id}_{company}/
```

### Key Files

- **config.json**: Configure AI models and pipeline behavior
- **src/main.py**: Main pipeline orchestrator
- **src/models.py**: Pydantic data models and validators
- **src/utils.py**: Helper functions
- **src/template_renderer.py**: Jinja2 template rendering
- **templates/\*.jinja2**: LaTeX templates
- **prompts/\*.txt**: AI prompts

## Development Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/\***: Feature development branches
- **fix/\***: Bug fix branches
- **docs/\***: Documentation branches

### Feature Development

```bash
# 1. Update your fork
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes
# ... edit files ...

# 4. Test changes
python src/main.py  # Run pipeline
# ... verify output ...

# 5. Commit changes
git add .
git commit -m "feat: add your feature description"

# 6. Push to your fork
git push origin feature/your-feature-name

# 7. Create pull request on GitHub
```

### Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream main into your main
git checkout main
git merge upstream/main

# Rebase your feature branch (optional)
git checkout feature/your-feature
git rebase main
```

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

#### Formatting

```python
# Line length: 100 characters (except long strings)
MAX_LINE_LENGTH = 100

# Indentation: 4 spaces
def my_function():
    if condition:
        do_something()

# Blank lines:
# - 2 blank lines between top-level functions/classes
# - 1 blank line between methods in a class
class MyClass:
    
    def method_one(self):
        pass
    
    def method_two(self):
        pass
```

#### Naming Conventions

```python
# Functions and variables: snake_case
def calculate_total(input_value):
    result_value = input_value * 2
    return result_value

# Classes: PascalCase
class ResumeGenerator:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
API_TIMEOUT = 60

# Private methods/variables: leading underscore
class MyClass:
    def _private_method(self):
        self._private_var = 10
```

#### Type Hints

```python
# Required for all function signatures
def process_data(input_text: str, max_length: int = 100) -> dict:
    """Process input text and return results."""
    return {"result": input_text[:max_length]}

# Use typing module for complex types
from typing import List, Dict, Optional, Union

def analyze_data(
    items: List[str],
    config: Dict[str, any],
    optional_param: Optional[int] = None
) -> Union[str, None]:
    """Analyze data with optional configuration."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Short one-line summary of function.
    
    Longer description if needed. Can span multiple lines and explain
    the purpose, behavior, and any important details.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this is raised
        TypeError: Description of when this is raised
        
    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

### LaTeX Style Guide

#### Template Formatting

```latex
% Use descriptive variable names
\VAR{contact_info.first_name}  % Good
\VAR{fi}                        % Bad

% Comment complex sections
% Skills section with category grouping
\BLOCK{for category, skills in skills.items()}
  \textbf{\VAR{category}}: \VAR{skills}
\BLOCK{endfor}

% Use consistent indentation
\begin{rSection}{EXPERIENCE}
  \BLOCK{for exp in work_experience}
    \rExperience
      {\VAR{exp.job_title}}
      {\VAR{exp.start_date} - \VAR{exp.end_date}}
  \BLOCK{endfor}
\end{rSection}
```

### Prompt Engineering Guidelines

#### Prompt Structure

```
# Clear objective statement
You are an expert resume writer...

# Context section
Job Description:
[JOB_DESCRIPTION]

# Clear instructions
Instructions:
1. Analyze the job description
2. Tailor the resume content
3. Ensure ATS compatibility

# Constraints
Constraints:
- Bullet points ≤118 characters
- Exactly 4 bullet points per experience
- Use keywords from job description

# Output format specification
Output Format:
Return ONLY valid JSON in this exact schema:
{
  "field": "value",
  ...
}

# Examples (if helpful)
Example output:
{
  "example_field": "example_value"
}
```

## Testing Guidelines

### Manual Testing

Since automated tests are not yet implemented, follow these manual testing procedures:

#### Unit Testing

Test individual components:

```python
# Test model validation
from src.models import TailoredResume, ContactInfo

# Valid data - should succeed
contact = ContactInfo(
    first_name="John",
    last_name="Doe",
    phone="919-672-2226",
    email="john@example.com",
    location="San Francisco, CA",
    linkedin_url="https://linkedin.com/in/johndoe",
    github_url="https://github.com/johndoe",
    portfolio_url="https://johndoe.com"
)

# Invalid data - should raise ValidationError
try:
    contact = ContactInfo(
        phone="invalid"  # Should fail validation
    )
except ValidationError as e:
    print("Validation failed as expected:", e)
```

#### Integration Testing

Test complete pipeline:

```bash
# 1. Create test job in data/applications.yaml
- job_id: "test_001"
  status: "pending"
  job_title: "Software Engineer"
  company_name: "Test Corp"
  job_description: |
    [Paste a real job description here for realistic testing]

# 2. Run pipeline
python src/main.py

# 3. Verify outputs
ls output/test_001_Test_Corp/
# Should contain:
# - Resume PDF
# - Cover Letter PDF
# - debug/ directory with intermediate files

# 4. Check PDF quality
# Open PDFs and verify:
# - Formatting is correct
# - No LaTeX errors
# - Content is tailored
# - Contact info is correct
```

#### Validation Testing

Test validators with edge cases:

```python
# Test bullet point length validator
from src.models import WorkExperience

# Should succeed (exactly 118 chars)
bullet = "x" * 118
exp = WorkExperience(
    job_title="Engineer",
    company="Corp",
    start_date="Jan 2020",
    end_date="Present",
    bullet_points=[bullet, bullet, bullet, bullet]
)

# Should fail (119 chars)
try:
    bullet_too_long = "x" * 119
    exp = WorkExperience(
        bullet_points=[bullet_too_long, bullet, bullet, bullet]
    )
except ValidationError as e:
    print("Validation correctly rejected too-long bullet")
```

### Test Cases to Cover

When contributing, ensure your changes don't break these test cases:

#### Model Validation
- [ ] Valid resume data passes validation
- [ ] Invalid phone numbers are rejected
- [ ] Bullet points >118 chars are rejected
- [ ] Skills categories >30 chars are rejected
- [ ] Skills values >90 chars are rejected
- [ ] Empty professional_summaries is accepted
- [ ] Non-empty professional_summaries is rejected
- [ ] Illegal characters are sanitized

#### Template Rendering
- [ ] All variables are interpolated correctly
- [ ] LaTeX special characters are escaped
- [ ] Loops generate correct number of sections
- [ ] Optional fields are handled correctly
- [ ] URLs are formatted properly

#### Pipeline Integration
- [ ] Input validation catches invalid jobs
- [ ] Intelligence gathering produces valid models
- [ ] Retry logic recovers from validation failures
- [ ] PDF compilation succeeds with valid data
- [ ] Cleanup moves files to debug/ correctly
- [ ] Job status is updated correctly

#### Error Handling
- [ ] Missing API key is detected
- [ ] Invalid JSON responses trigger retry
- [ ] Pydantic errors trigger retry with feedback
- [ ] LaTeX compilation errors are caught
- [ ] Missing files are handled gracefully

## Documentation

### Code Comments

Add comments for:
- Complex algorithms
- Non-obvious design decisions
- Workarounds for known issues
- Performance-critical sections

```python
# Good comments
def calculate_score(values: List[int]) -> float:
    """Calculate weighted average score."""
    # Use harmonic mean to penalize outliers more heavily
    # This aligns with ATS scoring algorithms observed in research
    total = sum(1/v for v in values if v > 0)
    return len(values) / total if total > 0 else 0.0

# Avoid obvious comments
x = x + 1  # Increment x by 1  (Bad - obvious)
```

### Documentation Files

When adding features, update relevant documentation:

- **README.md**: High-level overview, quick start
- **ARCHITECTURE.md**: System design, component interaction
- **DEVELOPMENT.md**: Design decisions, engineering details
- **API_REFERENCE.md**: API signatures, examples
- **CONFIGURATION.md**: Config options, examples
- **CONTRIBUTING.md** (this file): Contributing guidelines

### Docstring Requirements

All public functions/classes must have docstrings:

```python
def my_function(param: str) -> int:
    """
    Required: One-line summary.
    
    Optional: Extended description.
    
    Args:
        param: Required for functions with parameters
        
    Returns:
        Required for functions that return values
        
    Raises:
        Optional: Document exceptions
    """
    pass
```

## Commit Guidelines

### Commit Message Format

```
type(scope): Short description (≤50 chars)

Longer explanation if needed (wrap at 72 chars).
Explain WHAT changed and WHY, not HOW.

Breaking Changes:
- List any breaking changes

Fixes #123
```

### Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **refactor**: Code refactoring (no behavior change)
- **perf**: Performance improvement
- **test**: Add or update tests
- **chore**: Build process, dependencies, tooling
- **style**: Code style changes (formatting, etc.)

### Scopes

- **models**: Data models (src/models.py)
- **pipeline**: Main pipeline logic
- **validation**: Validation logic
- **templates**: LaTeX templates
- **prompts**: AI prompts
- **utils**: Utility functions
- **config**: Configuration
- **docs**: Documentation

### Examples

```bash
# Good commit messages
feat(models): add certifications section support
fix(validation): correct phone number format validation
docs(api): add examples to API reference
refactor(pipeline): extract intelligence gathering logic
perf(template): optimize LaTeX rendering performance

# Bad commit messages
Fixed stuff
Update file
WIP
Changes
```

### Commit Best Practices

1. **Atomic commits**: One logical change per commit
2. **Working state**: Each commit should leave code in working state
3. **Clear messages**: Explain what and why, not how
4. **Reference issues**: Link to issue numbers when applicable

```bash
# Good: Atomic commits
git commit -m "feat(models): add Certification model"
git commit -m "feat(templates): add certifications section to resume"
git commit -m "docs(api): document Certification model"

# Bad: Everything in one commit
git commit -m "Add certifications feature"
# (Contains model, template, AND documentation changes)
```

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test your changes**:
   ```bash
   python src/main.py
   # Verify output PDFs
   ```

3. **Update documentation**:
   - Add/update docstrings
   - Update relevant .md files
   - Add examples if applicable

4. **Clean commit history**:
   ```bash
   # Squash fixup commits if needed
   git rebase -i HEAD~5
   ```

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- List of changes made
- File-by-file breakdown

## Testing
How was this tested?
- [ ] Manual testing completed
- [ ] Edge cases verified
- [ ] Documentation updated

## Screenshots (if UI changes)
[Attach screenshots]

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts
- [ ] Testing completed

## Related Issues
Fixes #123
Relates to #456
```

### Review Process

1. **Automated checks**: Must pass (if configured)
2. **Code review**: At least one approving review
3. **Discussion**: Address all reviewer comments
4. **Final approval**: Maintainer approval required

### Addressing Feedback

```bash
# Make requested changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Address review feedback: fix validation logic"

# Push to your branch
git push origin feature/your-feature

# PR updates automatically
```

## Common Tasks

### Adding a New AI Model

1. **Update config.json**:
   ```json
   {
     "resume_generation": {
       "bot_name": "New-Model-Name",
       "parameters": {
         "thinking_budget": 2048
       }
     }
   }
   ```

2. **Test with sample job**:
   ```bash
   python src/main.py
   ```

3. **Document in CONFIGURATION.md**:
   ```markdown
   ### New Model Name
   - **Strengths**: ...
   - **Use Cases**: ...
   - **Cost**: ...
   ```

### Adding a New Pydantic Field

1. **Update model in src/models.py**:
   ```python
   class TailoredResume(BaseModel):
       # ... existing fields ...
       certifications: List[Certification] = Field(default_factory=list)
       
       @field_validator('certifications')
       @classmethod
       def validate_certifications(cls, v):
           # Add validation logic
           return v
   ```

2. **Update template**:
   ```latex
   % templates/resume.jinja2
   \BLOCK{if certifications}
   \begin{rSection}{CERTIFICATIONS}
   \BLOCK{for cert in certifications}
     \VAR{cert.name} | \VAR{cert.issuer}
   \BLOCK{endfor}
   \end{rSection}
   \BLOCK{endif}
   ```

3. **Update prompt**:
   ```
   # prompts/generate_resume.txt
   Certifications Section (if applicable):
   - Include relevant certifications
   - Format: name, issuer, date
   ```

4. **Test and document**:
   - Test with sample data
   - Update API_REFERENCE.md
   - Update master_resume.json example

### Modifying Validation Rules

1. **Update validator in src/models.py**:
   ```python
   @field_validator('bullet_points')
   @classmethod
   def validate_bullet_length(cls, v: List[str]) -> List[str]:
       # Modify validation logic
       MAX_LENGTH = 120  # Changed from 118
       for i, bullet in enumerate(v):
           if len(bullet) > MAX_LENGTH:
               raise ValueError(f"Bullet {i+1} exceeds {MAX_LENGTH} chars")
       return v
   ```

2. **Update documentation**:
   - Update ARCHITECTURE.md with new limits
   - Update API_REFERENCE.md
   - Update prompts with new constraints

3. **Test thoroughly**:
   - Test with edge cases (exactly at limit, 1 over, 1 under)
   - Verify error messages are clear

### Improving AI Prompts

1. **Edit prompt file**:
   ```bash
   # Edit prompts/generate_resume.txt
   nano prompts/generate_resume.txt
   ```

2. **Test changes**:
   ```bash
   # Run with test job
   python src/main.py
   
   # Check output quality
   cat output/*/debug/Resume_Response_Attempt_1.txt
   ```

3. **Iterate**:
   - Adjust prompt based on results
   - Test with multiple jobs
   - Document changes in commit message

4. **Document improvements**:
   ```
   docs(prompts): improve resume bullet point generation
   
   - Added emphasis on character limits
   - Clarified action verb usage
   - Added example outputs
   
   Results in 95% first-attempt success rate (up from 85%)
   ```

### Customizing LaTeX Templates

1. **Edit template**:
   ```latex
   % templates/resume.jinja2
   
   % Change section header style
   \begin{rSection}{\textsc{Experience}}  % Small caps
   % Instead of: \begin{rSection}{EXPERIENCE}  % Uppercase
   ```

2. **Test compilation**:
   ```bash
   python src/main.py
   # Check PDF output
   ```

3. **Update .cls file if needed**:
   ```latex
   % latex/resume.cls
   
   % Modify section formatting
   \renewcommand{\rSection}[1]{
     \section*{\textsc{#1}}  % Small caps
     \hrule
   }
   ```

4. **Document changes**:
   - Update ARCHITECTURE.md if significant
   - Add comments in template files

## Getting Help

### Resources

- **Documentation**: Start with docs/ directory
- **Issues**: Check existing issues on GitHub
- **Discussions**: GitHub Discussions for questions
- **Code**: Read through well-commented source

### Asking Questions

When asking for help:

1. **Search first**: Check docs and existing issues
2. **Provide context**: What are you trying to do?
3. **Include details**:
   - Python version
   - LaTeX distribution
   - Error messages (full traceback)
   - Code snippets
   - Configuration

**Good question format**:
```markdown
## What I'm trying to do
Add support for certifications section

## What I've tried
1. Added Certification model to models.py
2. Updated resume template
3. Ran pipeline

## Error I'm getting
```
ValidationError: certifications.0.date
  Field required (type=value_error.missing)
```

## Configuration
- Python 3.10.5
- MacTeX 2023
- Poe API key configured

## Code
```python
class Certification(BaseModel):
    name: str
    issuer: str
    # Missing: date field!
```
```

### Common Issues

**Issue**: "POE_API_KEY not found"
- **Solution**: Create .env file with API key

**Issue**: "pdflatex: command not found"
- **Solution**: Install LaTeX distribution

**Issue**: "ValidationError: bullet_points"
- **Solution**: Check prompt emphasizes 118-char limit

**Issue**: "JSON parsing failed"
- **Solution**: AI response includes extra text, check reasoning_trace setting

## Development Tips

### Debugging

```python
# Add debug prints
print(f"DEBUG: Processing job {job_id}")
print(f"DEBUG: Resume data: {json.dumps(resume_data, indent=2)}")

# Save intermediate outputs
with open("/tmp/debug_output.json", "w") as f:
    json.dump(data, f, indent=2)

# Check debug/ directory after pipeline runs
ls -la output/*/debug/
```

### Performance Profiling

```python
import time

start = time.time()
result = await expensive_operation()
elapsed = time.time() - start
print(f"Operation took {elapsed:.2f} seconds")
```

### LaTeX Debugging

```bash
# Check LaTeX log for errors
cat output/*/debug/*.log | grep -i error

# Compile manually to see errors
cd output/job_123_Company/debug/
pdflatex Resume.tex
# Errors will be shown in console
```

## Security

### API Keys

- **Never commit** API keys to git
- **Use .env** file for secrets
- **Add .env to .gitignore**

### Code Review

When reviewing code, check for:
- [ ] No hardcoded credentials
- [ ] Input validation for user data
- [ ] Safe file operations (no path traversal)
- [ ] Proper error handling

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

## Quick Reference

### Useful Commands

```bash
# Run pipeline
python src/main.py

# Check code style
pylint src/

# Format code
black src/

# View job queue
cat data/applications.yaml

# Clean output
rm -rf output/*/

# Reset job statuses
sed -i 's/processed/pending/g' data/applications.yaml

# Check LaTeX version
pdflatex --version

# Test model validation
python -c "from src.models import TailoredResume; print('Models OK')"
```

### File Locations

```
Documentation:     docs/
Source code:       src/
Templates:         templates/
LaTeX classes:     latex/
Prompts:           prompts/
Configuration:     config.json
Environment:       .env
Job queue:         data/applications.yaml
Master resume:     profile/master_resume.json
```

---

**Thank you for contributing to Jobbernaut Tailor!**

If you have questions, don't hesitate to ask in GitHub Issues or Discussions.

*Last Updated: October 2025*
*Version: 4.1*
