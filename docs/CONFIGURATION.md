# Configuration System

## Overview

Jobbernaut Tailor uses a hierarchical configuration system that allows flexible customization while maintaining sensible defaults. This document explains the configuration architecture, available settings, precedence rules, and best practices.

## Configuration Hierarchy

The system loads configuration from multiple sources in order of precedence:

### Precedence Order (Highest to Lowest)

1. **Command-line Arguments**: Runtime parameters override all other settings
2. **Environment Variables**: System-level configuration for sensitive data
3. **config.json**: User-specific settings and preferences
4. **Default Values**: Built-in fallback values

### Why This Hierarchy?

#### Security
Sensitive credentials stay in environment variables, never committed to version control.

#### Flexibility
Users can override settings without modifying code or configuration files.

#### Portability
Configuration files can be shared across environments while environment variables handle environment-specific values.

#### Maintainability
Default values ensure the system works out of the box with minimal configuration.

---

## Environment Variables

### Purpose
Store sensitive credentials and environment-specific settings that should not be committed to version control.

### Required Variables

#### ANTHROPIC_API_KEY
- **Purpose**: API key for Claude models
- **Format**: String (sk-ant-...)
- **Required**: Yes (if using Claude)
- **Example**: `sk-ant-api03-xxx`

#### OPENAI_API_KEY
- **Purpose**: API key for OpenAI models
- **Format**: String (sk-...)
- **Required**: Yes (if using GPT models)
- **Example**: `sk-xxx`

### Optional Variables

#### OUTPUT_DIR
- **Purpose**: Override default output directory
- **Format**: File path
- **Default**: `./output`
- **Example**: `/home/user/resumes`

#### LOG_LEVEL
- **Purpose**: Control logging verbosity
- **Format**: DEBUG, INFO, WARNING, ERROR
- **Default**: INFO
- **Example**: `DEBUG`

### Setting Environment Variables

#### Windows
```
set ANTHROPIC_API_KEY=sk-ant-xxx
set OPENAI_API_KEY=sk-xxx
```

#### Linux/Mac
```
export ANTHROPIC_API_KEY=sk-ant-xxx
export OPENAI_API_KEY=sk-xxx
```

#### .env File (Development)
```
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
OUTPUT_DIR=./output
LOG_LEVEL=DEBUG
```

---

## config.json

### Purpose
Store user preferences and system settings that can be version controlled and shared across environments.

### File Location
Root directory of the project: `config.json`

### Structure

The configuration file is organized into logical sections:

```
{
  "api": { ... },
  "resume_generation": { ... },
  "cover_letter_generation": { ... },
  "humanization": { ... },
  "referral_resume": { ... },
  "output": { ... }
}
```

---

## API Configuration

### Purpose
Configure AI model selection and API settings.

### Settings

#### model
- **Purpose**: Select AI model for generation
- **Type**: String
- **Options**: "claude-3-5-sonnet-20241022", "gpt-4", "gpt-4-turbo"
- **Default**: "claude-3-5-sonnet-20241022"
- **Example**: `"model": "claude-3-5-sonnet-20241022"`

#### max_tokens
- **Purpose**: Maximum tokens for AI responses
- **Type**: Integer
- **Range**: 1000-8000
- **Default**: 4000
- **Example**: `"max_tokens": 4000`

#### temperature
- **Purpose**: Control AI creativity/randomness
- **Type**: Float
- **Range**: 0.0-1.0
- **Default**: 0.7
- **Example**: `"temperature": 0.7`
- **Note**: Lower = more deterministic, Higher = more creative

#### timeout
- **Purpose**: API request timeout in seconds
- **Type**: Integer
- **Default**: 60
- **Example**: `"timeout": 60`

#### max_retries
- **Purpose**: Maximum retry attempts for failed API calls
- **Type**: Integer
- **Default**: 3
- **Example**: `"max_retries": 3`

### Design Rationale
Separating API configuration allows easy model switching and parameter tuning without code changes.

---

## Resume Generation Configuration

### Purpose
Control resume generation behavior and validation settings.

### Settings

#### enabled
- **Purpose**: Enable/disable resume generation
- **Type**: Boolean
- **Default**: true
- **Example**: `"enabled": true`
- **Use Case**: Disable when only generating cover letters

#### max_validation_retries
- **Purpose**: Maximum attempts to fix validation errors
- **Type**: Integer
- **Default**: 3
- **Example**: `"max_validation_retries": 3`

#### include_projects
- **Purpose**: Include projects section in resume
- **Type**: Boolean
- **Default**: true
- **Example**: `"include_projects": true`

#### include_certifications
- **Purpose**: Include certifications section
- **Type**: Boolean
- **Default**: true
- **Example**: `"include_certifications": true`

#### max_work_experiences
- **Purpose**: Maximum work experiences to include
- **Type**: Integer
- **Default**: 10
- **Example**: `"max_work_experiences": 5`
- **Use Case**: Limit resume length for recent graduates

#### max_skills
- **Purpose**: Maximum skills to list
- **Type**: Integer
- **Default**: 30
- **Example**: `"max_skills": 20`

### Design Rationale
Fine-grained control over resume content allows customization for different career stages and industries.

---

## Cover Letter Generation Configuration

### Purpose
Control cover letter generation and formatting.

### Settings

#### enabled
- **Purpose**: Enable/disable cover letter generation
- **Type**: Boolean
- **Default**: true
- **Example**: `"enabled": true`

#### max_validation_retries
- **Purpose**: Maximum attempts to fix validation errors
- **Type**: Integer
- **Default**: 3
- **Example**: `"max_validation_retries": 3`

#### include_recipient_info
- **Purpose**: Include hiring manager details if available
- **Type**: Boolean
- **Default**: true
- **Example**: `"include_recipient_info": true`

#### tone
- **Purpose**: Overall tone of cover letter
- **Type**: String
- **Options**: "professional", "enthusiastic", "formal"
- **Default**: "professional"
- **Example**: `"tone": "enthusiastic"`

### Design Rationale
Cover letter configuration allows tone adjustment for different company cultures and industries.

---

## Humanization Configuration

### Purpose
Control the humanization process that makes AI-generated content sound more natural.

### Settings

#### enabled
- **Purpose**: Enable/disable humanization
- **Type**: Boolean
- **Default**: true
- **Example**: `"enabled": true`

#### level
- **Purpose**: Intensity of humanization
- **Type**: String
- **Options**: "none", "low", "medium", "high"
- **Default**: "medium"
- **Example**: `"level": "medium"`

#### apply_to_resume
- **Purpose**: Apply humanization to resume
- **Type**: Boolean
- **Default**: true
- **Example**: `"apply_to_resume": true`

#### apply_to_cover_letter
- **Purpose**: Apply humanization to cover letter
- **Type**: Boolean
- **Default**: true
- **Example**: `"apply_to_cover_letter": true`

### Humanization Levels

#### none
- No humanization applied
- AI-generated content used as-is
- Most formal and technical
- Best for: Technical roles, academic positions

#### low
- Minimal changes to preserve accuracy
- Slight sentence structure variation
- Maintains formal professional tone
- Best for: Corporate roles, conservative industries

#### medium
- Balanced natural and professional
- Varied sentence structures
- Occasional conversational elements
- Best for: Most professional roles

#### high
- Maximum naturalness
- Conversational tone
- Varied sentence lengths
- Best for: Startups, creative roles

### Design Rationale
Configurable humanization allows users to balance naturalness with professionalism based on target industry and role.

---

## Referral Resume Configuration

### Purpose
Configure generation of referral-specific resumes with alternative contact information.

### Settings

#### enabled
- **Purpose**: Enable referral resume generation
- **Type**: Boolean
- **Default**: false
- **Example**: `"enabled": true`

#### contact_info
- **Purpose**: Alternative contact information for referrals
- **Type**: Object
- **Fields**: name, email, phone, location
- **Example**:
```json
"contact_info": {
  "name": "John Smith",
  "email": "referral@email.com",
  "phone": "+1 (555) 999-8888",
  "location": "San Francisco, CA"
}
```

### Use Case
When applying through employee referrals, some companies prefer alternative contact information to route applications correctly.

### Design Rationale
Separate referral configuration allows maintaining both standard and referral contact information without manual editing.

---

## Output Configuration

### Purpose
Control output file generation and organization.

### Settings

#### directory
- **Purpose**: Base output directory
- **Type**: String (file path)
- **Default**: "./output"
- **Example**: `"directory": "./output"`

#### create_subdirectories
- **Purpose**: Create company-specific subdirectories
- **Type**: Boolean
- **Default**: true
- **Example**: `"create_subdirectories": true`

#### subdirectory_format
- **Purpose**: Format for subdirectory names
- **Type**: String
- **Options**: "{company}_{position}", "{company}", "{position}"
- **Default**: "{company}_{position}"
- **Example**: `"subdirectory_format": "{company}_{position}"`

#### save_json
- **Purpose**: Save intermediate JSON files
- **Type**: Boolean
- **Default**: true
- **Example**: `"save_json": true`
- **Use Case**: Useful for debugging and manual editing

#### save_latex
- **Purpose**: Save LaTeX source files
- **Type**: Boolean
- **Default**: true
- **Example**: `"save_latex": true`

#### save_pdf
- **Purpose**: Generate PDF files
- **Type**: Boolean
- **Default**: true
- **Example**: `"save_pdf": true`

#### cleanup_auxiliary_files
- **Purpose**: Remove LaTeX auxiliary files after compilation
- **Type**: Boolean
- **Default**: true
- **Example**: `"cleanup_auxiliary_files": true`

### Design Rationale
Flexible output configuration supports different workflows and debugging needs.

---

## master_resume.json

### Purpose
Store complete professional profile that serves as source data for tailored resumes.

### File Location
`profile/master_resume.json`

### Structure

#### contact_info
Complete contact information including all social links.

#### summary
Comprehensive professional summary covering all aspects of career.

#### work_experience
Complete work history with detailed descriptions and achievements.

#### education
All educational background including degrees, certifications, and honors.

#### skills
Comprehensive list of technical and soft skills.

#### projects
All personal and professional projects.

#### certifications
Professional certifications and licenses.

### Best Practices

#### Completeness
Include all experiences, even if not always relevant. The AI will select appropriate content.

#### Detail
Provide detailed descriptions. The AI can condense but cannot expand missing information.

#### Accuracy
Ensure all information is factually accurate. The AI will not fact-check.

#### Updates
Keep master resume current with new experiences and skills.

### Design Rationale
A comprehensive master resume allows the AI to select and tailor the most relevant information for each application.

---

## Prompt Templates

### Purpose
Store AI instruction templates that guide content generation.

### File Locations
- `prompts/generate_resume.txt`
- `prompts/generate_cover_letter.txt`
- `prompts/humanization_low.txt`
- `prompts/humanization_medium.txt`
- `prompts/humanization_high.txt`

### Structure

#### Instructions Section
Clear, specific instructions for the AI on what to generate.

#### Context Section
Job description, master resume, and other relevant context.

#### Schema Section
Expected JSON structure and validation rules.

#### Examples Section (Optional)
Sample outputs to guide the AI.

### Customization

#### Tone Adjustment
Modify instructions to change output tone and style.

#### Content Focus
Emphasize different aspects (technical skills, leadership, etc.).

#### Format Preferences
Specify preferred phrasing and structure.

### Design Rationale
Separate prompt templates allow easy customization of AI behavior without code changes.

---

## Configuration Validation

### Startup Validation
The system validates configuration at startup:

#### Required Fields
- Checks for required configuration fields
- Validates field types
- Ensures valid value ranges

#### File Existence
- Verifies configuration files exist
- Checks template files are present
- Validates master resume file

#### API Credentials
- Confirms API keys are set
- Tests API connectivity (optional)
- Validates key format

### Error Handling

#### Missing Configuration
Clear error messages indicate missing required settings.

#### Invalid Values
Validation errors specify expected vs actual values.

#### File Not Found
Helpful messages indicate which files are missing and where they should be located.

---

## Configuration Best Practices

### Security

#### Never Commit Secrets
- Use environment variables for API keys
- Add .env to .gitignore
- Use separate credentials for different environments

#### Rotate Keys Regularly
- Change API keys periodically
- Use different keys for development and production
- Revoke compromised keys immediately

### Organization

#### Logical Grouping
- Group related settings together
- Use consistent naming conventions
- Document non-obvious settings

#### Version Control
- Commit config.json to version control
- Document configuration changes
- Use separate configs for different environments

### Maintenance

#### Regular Review
- Review configuration periodically
- Remove unused settings
- Update defaults as system evolves

#### Documentation
- Document custom settings
- Explain non-standard values
- Provide examples for complex settings

---

## Environment-Specific Configuration

### Development Environment
```json
{
  "api": {
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.7
  },
  "output": {
    "save_json": true,
    "save_latex": true,
    "cleanup_auxiliary_files": false
  }
}
```

### Production Environment
```json
{
  "api": {
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.5
  },
  "output": {
    "save_json": false,
    "save_latex": false,
    "cleanup_auxiliary_files": true
  }
}
```

### Testing Environment
```json
{
  "api": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 2000,
    "temperature": 0.0
  },
  "resume_generation": {
    "max_validation_retries": 1
  }
}
```

---

## Configuration Migration

### Version Updates
When updating Jobbernaut Tailor:

#### Check Changelog
Review configuration changes in release notes.

#### Backup Current Config
Save current configuration before updating.

#### Merge New Settings
Add new configuration options while preserving customizations.

#### Test Configuration
Validate configuration works with new version.

### Schema Changes
If configuration schema changes:

#### Migration Scripts
Use provided migration scripts to update configuration.

#### Manual Updates
Follow migration guide for manual updates.

#### Validation
Run configuration validation after migration.

---

## Troubleshooting Configuration

### Common Issues

#### API Key Not Found
**Symptom**: Error about missing API key
**Solution**: Set environment variable or check variable name

#### Invalid Configuration Format
**Symptom**: JSON parsing error
**Solution**: Validate JSON syntax, check for trailing commas

#### File Not Found
**Symptom**: Cannot find configuration file
**Solution**: Verify file path and location

#### Invalid Setting Value
**Symptom**: Validation error for configuration value
**Solution**: Check allowed values and types in documentation

### Debugging

#### Enable Debug Logging
Set LOG_LEVEL=DEBUG to see detailed configuration loading.

#### Validate JSON
Use JSON validator to check configuration file syntax.

#### Check Precedence
Verify which configuration source is being used.

---

## Future Enhancements

### Potential Improvements

#### Configuration UI
Web interface for configuration management.

#### Profile Management
Multiple configuration profiles for different use cases.

#### Dynamic Configuration
Runtime configuration updates without restart.

#### Configuration Templates
Pre-built configurations for common scenarios.

### Extensibility

#### Plugin Configuration
Configuration for third-party plugins and extensions.

#### Custom Validators
User-defined configuration validation rules.

#### Configuration Hooks
Callbacks for configuration changes.

---

## Conclusion

The hierarchical configuration system provides flexibility and security while maintaining ease of use. Environment variables protect sensitive data, config.json enables customization, and sensible defaults ensure the system works out of the box. Understanding the configuration hierarchy and available settings allows users to tailor Jobbernaut Tailor to their specific needs.
