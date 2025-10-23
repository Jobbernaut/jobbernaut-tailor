# Configuration Guide

## Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/Jobbernaut/jobbernaut-tailor.git
cd jobbernaut-tailor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Add your POE_API_KEY to .env

# 4. Run system
python src/main.py
```

## Core Configuration

### config.json
```json
{
  "intelligence_steps": {
    "job_resonance_analysis": {
      "bot_name": "Gemini-2.5-Pro",
      "thinking_budget": "4096",
      "temperature": 0.7
    },
    "company_research": {
      "bot_name": "Claude-3",
      "thinking_budget": "2048",
      "temperature": 0.5
    }
  },
  "validation": {
    "retry_attempts": 2,
    "quality_threshold": 0.85
  },
  "output": {
    "pdf_quality": "production",
    "debug_mode": false
  }
}
```

## Intelligence Models

### Model Selection
```json
{
  "available_models": {
    "Gemini-2.5-Pro": {
      "strengths": ["technical analysis", "pattern matching"],
      "use_case": "job resonance analysis"
    },
    "Claude-3": {
      "strengths": ["research", "synthesis"],
      "use_case": "company research"
    },
    "GPT-4": {
      "strengths": ["storytelling", "creativity"],
      "use_case": "cover letter generation"
    }
  }
}
```

## Validation Rules

### Character Limits
```python
LIMITS = {
    'bullet_point': 118,
    'skills_category': 30,
    'skills_list': 85,
    'project_tech': 65,
    'summary': 425
}
```

### Quality Thresholds
```python
THRESHOLDS = {
    'min_bullets': 4,
    'max_bullets': 4,
    'min_skills': 3,
    'max_skills': 6
}
```

## Template Customization

### LaTeX Templates
- `templates/resume.jinja2`
- `templates/cover_letter.jinja2`

### Style Configuration
```latex
% In latex/resume.cls
\geometry{
    paper=letterpaper,
    top=0.5in,
    bottom=0.5in,
    left=0.5in,
    right=0.5in
}
```

## Advanced Options

### Debug Mode
```json
{
  "debug": {
    "save_intermediate": true,
    "verbose_logging": true,
    "validation_details": true
  }
}
```

### Error Recovery
```json
{
  "error_handling": {
    "max_retries": 2,
    "backoff_factor": 1.5,
    "preserve_context": true
  }
}
```

### Performance Tuning
```json
{
  "performance": {
    "parallel_validation": true,
    "cache_templates": true,
    "optimize_latex": true
  }
}
```

## Environment Variables

```bash
POE_API_KEY=your_api_key_here
DEBUG_MODE=false
LATEX_QUALITY=production
OUTPUT_DIR=./output
```

## Customization Examples

### 1. Custom Validation Rules
```python
# In src/models.py
class CustomValidator(BaseModel):
    @validator('bullet_points')
    def validate_bullet_length(cls, v):
        if any(len(bullet) > 118 for bullet in v):
            raise ValueError("Bullet point exceeds ATS limit")
        return v
```

### 2. New Intelligence Step
```python
# In src/main_intelligence_methods.py
async def custom_analysis(job_description: str) -> Dict:
    # Your custom analysis logic
    return results
```

For implementation details and architecture overview, see [ARCHITECTURE.md](ARCHITECTURE.md).
