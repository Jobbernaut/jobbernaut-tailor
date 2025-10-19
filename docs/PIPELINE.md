# Pipeline Architecture

## Overview

Jobbernaut Tailor implements a sequential 10-step pipeline that transforms a job description and master resume into tailored application materials. This document provides a comprehensive breakdown of each step, including inputs, outputs, error handling, and design rationale.

## Pipeline Flow

The pipeline is orchestrated by the `ResumeOptimizationPipeline` class in `src/main.py`. Each step is executed sequentially, with the output of one step serving as input to the next.

```
Job Description + Master Resume
         ↓
    Configuration Loading
         ↓
    Resume Generation (AI)
         ↓
    Pydantic Validation
         ↓
    Humanization (Optional)
         ↓
    Template Rendering
         ↓
    Cover Letter Generation (AI)
         ↓
    Pydantic Validation
         ↓
    Humanization (Optional)
         ↓
    Template Rendering + PDF Compilation
```

---

## Step 1: Configuration Loading

### Purpose
Initialize the pipeline with all necessary configuration data, including API credentials, model settings, and user preferences.

### Process
The system loads configuration from multiple sources in hierarchical order:

1. **Environment Variables**: API keys and sensitive credentials
2. **config.json**: System-wide settings and preferences
3. **master_resume.json**: User's complete professional profile
4. **Prompt Templates**: Text files containing AI instructions

### Configuration Hierarchy
Later sources override earlier ones, allowing for flexible configuration management:
- Environment variables take highest precedence
- config.json overrides defaults
- Command-line arguments override config.json

### Key Configuration Elements

#### API Configuration
- Model selection (Claude, GPT-4, etc.)
- API endpoints and credentials
- Timeout and retry settings
- Rate limiting parameters

#### Generation Settings
- Resume generation enabled/disabled
- Cover letter generation enabled/disabled
- Humanization level (none, low, medium, high)
- Maximum retry attempts for validation failures

#### Output Settings
- Output directory path
- File naming conventions
- Format preferences (JSON, LaTeX, PDF)
- Cleanup behavior

### Error Handling
- Missing configuration files trigger clear error messages
- Invalid JSON syntax is caught and reported
- Missing required fields are identified
- Default values are applied where appropriate

### Design Rationale
Separating configuration from code allows users to customize behavior without modifying source files. The hierarchical approach provides flexibility while maintaining sensible defaults.

---

## Step 2: Resume Generation

### Purpose
Generate a tailored resume JSON structure that highlights relevant experiences and skills for the specific job description.

### Input
- Job description text
- Master resume JSON (complete professional history)
- Resume generation prompt template
- Configuration settings

### Process

#### Prompt Construction
The system constructs a detailed prompt that includes:
- Instructions for tailoring content
- Job description context
- Master resume data
- Expected JSON schema
- Validation rules and constraints

#### AI Interaction
The AI model analyzes the job description and selects the most relevant:
- Work experiences
- Projects
- Skills
- Education details
- Certifications

#### Content Tailoring
For each selected element, the AI:
- Rewrites descriptions to emphasize relevant aspects
- Adjusts technical terminology to match job requirements
- Highlights transferable skills
- Maintains factual accuracy from master resume

#### Output Structure
The AI generates a JSON object conforming to the TailoredResume schema:
- Contact information
- Professional summary
- Work experience array
- Education array
- Skills array
- Projects array (optional)
- Certifications array (optional)

### Error Handling

#### Retry Logic
If the AI generates invalid JSON or fails to follow instructions:
1. System captures the error
2. Constructs detailed error feedback
3. Sends feedback to AI with retry request
4. Maximum retry attempts prevent infinite loops

#### Common Failure Modes
- Malformed JSON syntax
- Missing required fields
- Exceeding character limits
- Including hallucinated information

### Design Rationale
Separating content generation from formatting allows the AI to focus on semantic understanding and relevance matching. The structured JSON output enables validation before rendering.

---

## Step 3: Resume Validation

### Purpose
Ensure the AI-generated resume JSON conforms to the expected schema and meets all validation constraints.

### Process

#### Pydantic Model Validation
The JSON is parsed into Pydantic models that enforce:
- Type correctness (strings, arrays, objects)
- Required field presence
- Character length limits
- Array size constraints
- Custom validation rules

#### Validation Layers

**ContactInfo Model:**
- Name, email, phone, location, LinkedIn, GitHub
- Email format validation
- Phone number format validation
- URL format validation for links

**WorkExperience Model:**
- Company, position, dates, location, description
- Description character limit (600 characters)
- Bullet points array (2-5 items)
- Each bullet point limited to 200 characters

**Education Model:**
- Institution, degree, field, dates, GPA, location
- GPA range validation (0.0-4.0)
- Date format consistency

**Project Model:**
- Name, description, technologies, dates
- Description character limit (400 characters)
- Technologies array (1-10 items)

**TailoredResume Model:**
- Aggregates all sub-models
- Validates overall structure
- Ensures required sections present

#### Error Feedback Construction
When validation fails, the system:
1. Captures all validation errors
2. Formats them into human-readable messages
3. Constructs feedback for the AI
4. Includes the original prompt and failed output
5. Requests specific corrections

### Error Handling

#### Validation Failure Response
If validation fails:
1. Error details are logged
2. Feedback is constructed with specific issues
3. AI is prompted to regenerate with corrections
4. Process repeats up to maximum retry attempts

#### Maximum Retry Limit
After exhausting retries:
- System logs the failure
- Provides detailed error report
- Exits gracefully with error code

### Design Rationale
Proactive validation catches errors before rendering, preventing invalid LaTeX generation. Detailed error feedback helps the AI correct specific issues rather than regenerating blindly.

---

## Step 4: Resume Humanization (Optional)

### Purpose
Apply natural language transformations to make AI-generated content sound less robotic and more human.

### Conditional Execution
This step only executes if:
- Humanization is enabled in configuration
- Humanization level is set to low, medium, or high
- Resume generation was successful

### Process

#### Humanization Levels

**Low Humanization:**
- Minimal changes to preserve technical accuracy
- Slight variation in sentence structure
- Maintains formal professional tone
- Focuses on readability improvements

**Medium Humanization:**
- Balanced approach between natural and professional
- More varied sentence structures
- Occasional conversational elements
- Maintains credibility while improving flow

**High Humanization:**
- Maximum naturalness and conversational tone
- Varied sentence lengths and structures
- More personal voice
- Still maintains professionalism

#### Prompt Construction
The system loads the appropriate humanization prompt template based on the configured level and includes:
- Current resume JSON
- Humanization guidelines
- Tone and style instructions
- Constraints to maintain accuracy

#### AI Interaction
The AI receives the validated resume JSON and applies transformations:
- Rewrites bullet points for naturalness
- Varies sentence structure
- Adjusts tone based on humanization level
- Maintains all factual information

#### Re-validation
After humanization, the output is validated again to ensure:
- Structure remains intact
- Character limits still respected
- No information was lost or added
- JSON remains valid

### Error Handling

#### Humanization Failure
If humanization produces invalid output:
1. System logs the error
2. Falls back to pre-humanization version
3. Continues pipeline with original validated content
4. User is notified of fallback

### Design Rationale
Separating humanization from content generation allows independent optimization of each concern. Making it optional and configurable gives users control over the trade-off between naturalness and formality.

---

## Step 5: Resume Template Rendering

### Purpose
Convert the validated JSON resume into properly formatted LaTeX code using Jinja2 templates.

### Input
- Validated resume JSON (humanized or original)
- Resume Jinja2 template
- Template renderer with custom filters

### Process

#### Template Loading
The TemplateRenderer class loads the resume template with:
- Custom delimiters to avoid LaTeX conflicts
- Custom filters for LaTeX escaping
- Custom filters for date formatting
- Custom filters for phone formatting

#### Custom Filters

**latex_escape:**
- Escapes special LaTeX characters
- Handles ampersands, percent signs, underscores
- Preserves intentional LaTeX commands
- Prevents compilation errors

**format_date:**
- Converts date strings to consistent format
- Handles various input formats
- Provides fallback for invalid dates
- Supports "Present" for current positions

**format_phone:**
- Formats phone numbers consistently
- Handles various input formats
- Adds appropriate separators
- Maintains international format support

#### Rendering Process
The template engine:
1. Iterates through resume sections
2. Applies formatting rules
3. Escapes special characters
4. Generates valid LaTeX code
5. Maintains consistent styling

#### Output
Clean, valid LaTeX code ready for compilation, including:
- Document class and packages
- Formatted contact information
- Professional summary
- Work experience section
- Education section
- Skills section
- Projects section (if present)

### Error Handling

#### Template Errors
If rendering fails:
- Jinja2 provides detailed error messages
- Line numbers indicate problem location
- Variable names show missing data
- System logs full error context

#### Missing Data
If required template variables are missing:
- Template uses default values where possible
- Conditional blocks handle optional sections
- Error is logged for debugging
- Rendering continues with available data

### Design Rationale
Template-based rendering ensures consistent formatting and eliminates LaTeX syntax errors from AI generation. Custom filters handle edge cases and maintain code quality.

---

## Step 6: Cover Letter Generation

### Purpose
Generate a tailored cover letter that complements the resume and addresses the specific job opportunity.

### Input
- Job description text
- Validated resume JSON
- Master resume JSON
- Cover letter generation prompt template
- Configuration settings

### Process

#### Prompt Construction
The system constructs a prompt that includes:
- Job description context
- Tailored resume content (for consistency)
- Master resume (for additional context)
- Cover letter writing guidelines
- Expected JSON schema

#### AI Interaction
The AI generates a cover letter that:
- References specific job requirements
- Highlights relevant experiences from resume
- Demonstrates enthusiasm and fit
- Maintains professional tone
- Follows standard business letter format

#### Content Structure
The generated JSON includes:
- Recipient information (if available)
- Opening paragraph (introduction)
- Body paragraphs (2-3 paragraphs)
- Closing paragraph
- Signature block

#### Consistency Check
The AI ensures the cover letter:
- Aligns with resume content
- Doesn't contradict resume information
- Uses consistent terminology
- Maintains the same professional voice

### Error Handling

#### Generation Failures
Similar to resume generation:
- Retry logic for invalid JSON
- Error feedback construction
- Maximum retry attempts
- Detailed error logging

#### Content Quality Issues
If the AI generates generic or low-quality content:
- System can detect certain patterns
- Retry with enhanced instructions
- User can review and regenerate manually

### Design Rationale
Generating the cover letter after the resume ensures consistency between documents. Providing the tailored resume as context helps the AI reference specific experiences accurately.

---

## Step 7: Cover Letter Validation

### Purpose
Ensure the AI-generated cover letter JSON conforms to the expected schema and meets validation constraints.

### Process

#### Pydantic Model Validation
Similar to resume validation, but with cover letter-specific models:
- Recipient information validation
- Paragraph structure validation
- Character limit enforcement
- Required field checking

#### Validation Rules

**Opening Paragraph:**
- Character limit (500 characters)
- Must introduce candidate and position
- Should establish enthusiasm

**Body Paragraphs:**
- Array of 2-3 paragraphs
- Each limited to 600 characters
- Must reference specific qualifications
- Should connect to job requirements

**Closing Paragraph:**
- Character limit (400 characters)
- Must include call to action
- Should express availability

#### Error Feedback
When validation fails:
- Specific paragraph issues identified
- Character count violations reported
- Missing required elements highlighted
- AI receives detailed correction instructions

### Error Handling

#### Validation Failure Response
Identical to resume validation:
- Error logging
- Feedback construction
- Retry with corrections
- Maximum retry limit

### Design Rationale
Consistent validation approach across resume and cover letter simplifies maintenance and ensures uniform quality standards.

---

## Step 8: Cover Letter Humanization (Optional)

### Purpose
Apply natural language transformations to the cover letter to enhance authenticity and engagement.

### Conditional Execution
Executes under the same conditions as resume humanization:
- Humanization enabled in configuration
- Level set to low, medium, or high
- Cover letter generation successful

### Process

#### Humanization Application
Uses the same level-based approach as resume humanization:
- Loads appropriate prompt template
- Applies transformations to paragraphs
- Maintains professional business letter tone
- Preserves key information and structure

#### Cover Letter Specific Considerations
Humanization for cover letters focuses on:
- Varying sentence openings
- Adding transitional phrases
- Enhancing enthusiasm expression
- Improving flow between paragraphs
- Maintaining appropriate formality

#### Re-validation
After humanization:
- Validates against cover letter schema
- Ensures character limits maintained
- Verifies structure integrity
- Confirms no information loss

### Error Handling

#### Humanization Failure
Same fallback strategy as resume:
- Logs error
- Reverts to pre-humanization version
- Continues pipeline
- Notifies user

### Design Rationale
Cover letters benefit more from humanization than resumes, as they require a more personal, engaging tone. The same configurable approach maintains consistency across documents.

---

## Step 9: Cover Letter Template Rendering

### Purpose
Convert the validated cover letter JSON into properly formatted LaTeX code.

### Input
- Validated cover letter JSON (humanized or original)
- Cover letter Jinja2 template
- Template renderer with custom filters

### Process

#### Template Structure
The cover letter template includes:
- Business letter formatting
- Recipient address block
- Date formatting
- Salutation
- Body paragraphs
- Closing and signature

#### Rendering Process
Similar to resume rendering:
1. Loads template with custom delimiters
2. Applies custom filters
3. Iterates through paragraphs
4. Formats according to business letter standards
5. Generates valid LaTeX code

#### Special Formatting
Cover letter templates handle:
- Conditional recipient information
- Date formatting
- Paragraph spacing
- Signature block positioning
- Professional closing phrases

### Error Handling

#### Template Errors
Same error handling as resume rendering:
- Detailed Jinja2 error messages
- Line number identification
- Variable name reporting
- Full error context logging

### Design Rationale
Separate templates for resume and cover letter allow independent formatting control while maintaining consistent rendering approach.

---

## Step 10: PDF Compilation and Cleanup

### Purpose
Compile LaTeX files into PDFs and perform cleanup operations.

### Process

#### LaTeX Compilation
For each document (resume and cover letter):
1. Write LaTeX content to file
2. Invoke pdflatex compiler
3. Run twice for proper reference resolution
4. Capture compilation output
5. Check for errors

#### Compilation Settings
- Output directory specified
- Interaction mode set to non-stop
- Auxiliary files managed
- Error logs captured

#### Referral Resume Generation
If configured:
1. Modify contact information
2. Use referral-specific details
3. Render separate template
4. Compile additional PDF

#### Cleanup Operations
After successful compilation:
- Remove auxiliary files (.aux, .log, .out)
- Organize output files
- Preserve only PDFs and source files
- Create application-specific directory

#### Output Organization
Final directory structure:
```
output/
  company_name_position/
    resume.pdf
    resume.tex
    cover_letter.pdf
    cover_letter.tex
    resume.json
    cover_letter.json
    referral_resume.pdf (if configured)
```

### Error Handling

#### Compilation Failures
If LaTeX compilation fails:
- Capture full error output
- Identify problematic lines
- Log error details
- Preserve intermediate files for debugging
- Provide actionable error messages

#### Cleanup Failures
If cleanup operations fail:
- Log warnings
- Continue with available files
- Don't block pipeline completion
- Notify user of incomplete cleanup

### Design Rationale
Separating compilation from generation allows for independent troubleshooting. Preserving source files enables manual debugging and customization.

---

## Error Handling Strategy

### Retry Logic
The pipeline implements intelligent retry logic at multiple levels:

#### Generation Retries
- Maximum attempts configurable
- Exponential backoff between retries
- Detailed error feedback to AI
- Context preservation across retries

#### Validation Retries
- Automatic retry on validation failure
- Specific error messages guide corrections
- Retry count tracked per step
- Graceful failure after max attempts

### Error Propagation
Errors are handled at the appropriate level:
- Validation errors trigger retries
- Template errors stop pipeline
- Compilation errors preserve intermediate files
- Configuration errors fail fast

### Logging
Comprehensive logging throughout pipeline:
- Step entry and exit logged
- Error details captured
- Timing information recorded
- Debug information available

---

## Performance Characteristics

### Timing Breakdown
Typical execution times for each step:

1. Configuration Loading: < 1 second
2. Resume Generation: 10-30 seconds (AI dependent)
3. Resume Validation: < 1 second
4. Resume Humanization: 5-15 seconds (if enabled)
5. Resume Rendering: < 1 second
6. Cover Letter Generation: 10-30 seconds (AI dependent)
7. Cover Letter Validation: < 1 second
8. Cover Letter Humanization: 5-15 seconds (if enabled)
9. Cover Letter Rendering: < 1 second
10. PDF Compilation: 2-5 seconds

**Total Time:** 30-90 seconds depending on configuration

### Optimization Opportunities
- Parallel generation of resume and cover letter (future)
- Caching of template compilation
- Batch processing of multiple applications
- Async AI API calls

---

## Extension Points

### Adding New Steps
The pipeline architecture supports adding new steps:
- Insert between existing steps
- Maintain sequential flow
- Implement error handling
- Update logging

### Custom Validation Rules
Pydantic models can be extended with:
- Additional field validators
- Custom validation logic
- Cross-field validation
- Business rule enforcement

### Alternative Output Formats
New templates can be added for:
- Different resume styles
- Alternative document formats
- Multi-language support
- Industry-specific layouts

---

## Best Practices

### Configuration Management
- Use environment variables for secrets
- Version control config.json
- Document configuration options
- Provide sensible defaults

### Error Handling
- Fail fast on configuration errors
- Retry on transient failures
- Preserve context for debugging
- Provide actionable error messages

### Testing
- Unit test individual steps
- Integration test full pipeline
- Validate with various inputs
- Test error conditions

### Monitoring
- Log all pipeline executions
- Track success/failure rates
- Monitor execution times
- Alert on anomalies

---

## Conclusion

The 10-step pipeline provides a robust, maintainable architecture for generating tailored application materials. The sequential design with comprehensive error handling ensures reliability while the modular structure enables easy extension and customization.
