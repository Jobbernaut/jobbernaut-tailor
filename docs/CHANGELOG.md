# Changelog

All notable changes to Jobbernaut Tailor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.1.0] - 2025-10-22

### Added

#### Intelligence Gathering System
- **Three-stage intelligence pipeline** before content generation:
  - Job Resonance Analysis: Extracts emotional keywords, cultural values, hidden requirements
  - Company Research: Gathers company mission, values, tech stack
  - Storytelling Arc: Creates narrative framework for cover letters
- **Model specialization**: Different AI models for different intelligence tasks
- **Quality validation**: Ensures intelligence outputs meet minimum thresholds

#### Enhanced Validation System
- **Progressive error feedback**: Top-injection of validation errors for better model attention
- **Incident logging**: Track validation failures in `learnings.yaml` for continuous improvement
- **Quality thresholds**: Minimum content length, array sizes, meaningful content checks
- **Fail-fast input validation**: Reject invalid inputs immediately with clear error messages

#### Referral Document Generation
- **Optional referral PDFs**: Generate separate documents with referrer's contact info
- **Graceful fallback**: Automatically skips if referral contact not configured
- **Validation**: Ensures referral contact info is valid before generation

#### Humanization Feature
- **Three-level humanization** (low, medium, high) for natural-sounding text
- **Selective application**: Choose which document types to humanize
- **Configurable**: Enable/disable via `config.json`

#### Reasoning Trace Removal
- **Configurable cleanup**: Remove AI model reasoning traces from responses
- **Token efficiency**: Reduces downstream token consumption
- **Debug mode**: Option to keep traces for troubleshooting

### Changed

#### Pipeline Architecture
- **12-step process**: Restructured from 6-step to 12-step pipeline with intelligence phase
- **Retry logic improvements**: Better error feedback and recovery
- **Model configuration**: Per-step model selection with custom parameters
- **Intelligence-first approach**: Gather context before generating content

#### Validation Improvements
- **Phone format standardization**: Automatic formatting to `(XXX) XXX-XXXX`
- **Character sanitization**: Remove ATS-incompatible characters automatically
- **Pydantic validators**: More comprehensive field-level validation
- **Error messages**: Clearer, more actionable validation errors

#### Template System
- **Enhanced LaTeX templates**: Better formatting and structure
- **PDF metadata**: Rich metadata for improved searchability
- **Jinja2 improvements**: Cleaner variable interpolation and escaping

### Fixed
- **Phone validation**: Handles various input formats correctly
- **Bullet point length**: Consistent 118-character enforcement
- **JSON extraction**: Better handling of markdown code blocks
- **LaTeX compilation**: More robust error handling

### Performance
- **Success rate**: >99.5% after retry logic (up from ~85%)
- **Processing time**: 60-90 seconds per job (down from 120+ seconds)
- **First-attempt success**: ~90% (up from ~60%)

---

## [4.0.0] - 2025-10-15

### Added

#### Core Features
- **ATS Optimization Engine**: Character-limit enforcement for ATS compatibility
- **Pydantic Validation**: Strict schema validation for resume structure
- **LaTeX Template System**: Professional PDF generation with Jinja2 templates
- **Multi-model AI Support**: Poe API integration with model selection
- **Automated Pipeline**: End-to-end resume and cover letter generation

#### Validation System
- **Character limits**: Bullet points ≤118 chars, skills ≤90 chars, categories ≤30 chars
- **Format validation**: Phone numbers, dates, URLs
- **Schema enforcement**: Pydantic models for type safety
- **Illegal character removal**: ATS-incompatible character sanitization

#### Template Features
- **Resume template**: Clean, ATS-friendly LaTeX layout
- **Cover letter template**: Professional letter format
- **Custom LaTeX classes**: `resume.cls` and `coverletter.cls`
- **Jinja2 integration**: Dynamic content injection

#### Configuration
- **Model selection**: Configure AI models per task
- **API parameters**: Thinking budget, temperature, web search
- **File paths**: Configurable input/output paths
- **Validation rules**: Adjustable constraints

### Changed
- **Architecture**: Modular design with separation of concerns
- **Error handling**: Comprehensive exception handling and logging
- **Output organization**: Structured output directories with debug files

### Breaking Changes
- **Python 3.9+ required**: Uses modern Python features
- **Poe API key required**: API authentication mandatory
- **LaTeX installation required**: PDF generation dependency
- **Config structure**: New `config.json` format

---

## [3.x] - Legacy Versions

### Notable Features (Pre-4.0)
- Basic resume tailoring functionality
- Simple prompt-based generation
- Manual validation and fixes
- Limited error recovery

### Limitations
- High failure rate (~40%)
- Manual intervention often required
- No structured validation
- No intelligence gathering phase
- Generic cover letters

---

## Migration Guides

### Migrating from 3.x to 4.0

#### Breaking Changes

1. **Configuration Format**
   ```json
   // Old (3.x)
   {
     "model": "gpt-4",
     "temperature": 0.7
   }
   
   // New (4.0)
   {
     "resume_generation": {
       "bot_name": "Gemini-2.5-Pro",
       "parameters": {
         "temperature": 0.7,
         "thinking_budget": 2048
       }
     }
   }
   ```

2. **Resume Structure**
   ```json
   // Old (3.x)
   {
     "education": [{
       "end_date": "June 2020"  // ❌ Wrong
     }]
   }
   
   // New (4.0)
   {
     "education": [{
       "graduation_date": "June 2020"  // ✅ Correct
     }]
   }
   ```

3. **Professional Summary**
   ```json
   // Old (3.x)
   {
     "professional_summaries": "Experienced engineer..."  // ❌
   }
   
   // New (4.0)
   {
     "professional_summaries": ""  // ✅ Must be empty
   }
   ```

#### Migration Steps

1. **Update configuration**:
   ```bash
   cp config.json config.json.backup
   # Update to new format (see config.json.example)
   ```

2. **Update master resume**:
   ```bash
   cp profile/master_resume.json profile/master_resume.json.backup
   # Fix field names: end_date → graduation_date
   # Clear professional_summaries
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **Test migration**:
   ```bash
   python src/main.py
   # Verify output PDFs look correct
   ```

### Migrating from 4.0 to 4.1

#### New Features
- Intelligence gathering phase (backward compatible)
- Humanization (opt-in)
- Referral documents (opt-in)
- Reasoning trace removal (opt-in)

#### Configuration Updates

```json
// Add to config.json
{
  "intelligence_steps": {
    "job_resonance_analysis": {
      "bot_name": "Claude-Haiku-4.5",
      "parameters": {"thinking_budget": 0}
    },
    "company_research": {
      "bot_name": "Claude-Sonnet-4-Search",
      "parameters": {"web_search": true}
    },
    "storytelling_arc": {
      "bot_name": "Claude-Haiku-4.5",
      "parameters": {"thinking_budget": 0}
    }
  },
  "humanization": {
    "enabled": false,
    "level": "low",
    "apply_to": ["resume", "cover_letter"]
  },
  "reasoning_trace": false
}
```

#### Optional: Add Referral Contact

```bash
# Create profile/referral_contact.json
{
  "email": "referrer@example.com",
  "phone": "(555) 123-4567"
}
```

#### No Breaking Changes
- Existing configs work without modification
- New features are opt-in
- Default behavior unchanged

---

## Version History Summary

| Version | Release Date | Key Features | Status |
|---------|--------------|--------------|--------|
| **4.1.0** | 2025-10-22 | Intelligence gathering, humanization, referral docs | ✅ Current |
| **4.0.0** | 2025-10-15 | ATS optimization, Pydantic validation, LaTeX templates | ⚠️ Deprecated |
| **3.x** | 2025-09-xx | Basic tailoring | ❌ Unsupported |

---

## Deprecation Notices

### Deprecated in 4.1
- None

### Removed in 4.1
- None

### Planned for 5.0
- **Python 3.8 support**: Will be dropped (3.9+ required)
- **Old config format**: 3.x config format will not be supported
- **Manual validation**: All validation will be automatic

---

## Future Roadmap

### Version 5.0 (Planned)
- **Automated testing**: Comprehensive test suite
- **CI/CD pipeline**: Automated testing and deployment
- **Multi-language support**: Generate resumes in multiple languages
- **Custom templates**: User-defined LaTeX templates
- **Analytics dashboard**: Track application outcomes
- **Batch processing**: Process multiple jobs in parallel

### Version 5.1 (Planned)
- **Web interface**: Browser-based UI
- **Cloud deployment**: Hosted version
- **Team features**: Shared profiles and templates
- **Version control**: Track changes to resumes over time

### Long-term Vision
- **ML-powered optimization**: Learn from application outcomes
- **ATS scoring**: Predict ATS compatibility score
- **Interview prep**: AI-generated interview questions
- **Application tracking**: Full job search management system

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing changes.

### How to Report Issues

When reporting issues, please include:
- Version number (check with `git describe --tags`)
- Error messages (full traceback)
- Configuration (sanitize API keys)
- Steps to reproduce

### How to Request Features

Feature requests should include:
- Use case description
- Expected behavior
- Alternative solutions considered
- Willingness to contribute implementation

---

## Acknowledgments

### Contributors
- Project maintainers and contributors (see GitHub contributors page)

### Inspiration
- ATS research and best practices from job search communities
- LaTeX resume templates from various open-source projects
- AI-powered content generation research

### Technologies
- **Pydantic**: Data validation library
- **Jinja2**: Template engine
- **LaTeX**: Document preparation system
- **Poe API**: AI model access
- **Python**: Programming language

---

## Release Notes Template

For future releases, use this template:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed

### Removed
- Features that were removed

### Fixed
- Bug fixes

### Security
- Security fixes

### Performance
- Performance improvements

### Breaking Changes
- Incompatible changes

### Migration Guide
- Steps to migrate from previous version
```

---

*For detailed documentation, see:*
- [README.md](../README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines

*Last Updated: October 2025*
