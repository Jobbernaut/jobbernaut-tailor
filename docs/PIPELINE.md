# Pipeline Architecture

## Overview

Jobbernaut Tailor implements a sequential 13-step pipeline (V4) that transforms a job description and master resume into tailored application materials. The V4 architecture introduces an intelligence gathering phase that precedes document generation, providing contextual analysis to enhance the quality and relevance of generated materials.

This document provides a comprehensive breakdown of each step, including inputs, outputs, error handling, and design rationale.

## Pipeline Flow (V4)

The pipeline is orchestrated by the `ResumeOptimizationPipeline` class in `src/main.py`. Each step is executed sequentially, with the output of one step serving as input to the next.

```
Job Description + Master Resume
         ↓
    Configuration Loading
         ↓
    Input Validation (V4)
         ↓
    INTELLIGENCE PHASE (V4)
    ├── Job Resonance Analysis
    ├── Company Research
    └── Storytelling Arc Generation
         ↓
    Resume Generation (AI)
         ↓
    Pydantic Validation
         ↓
    Cover Letter Generation (AI)
         ↓
    Template Rendering
         ↓
    PDF Compilation + Cleanup
```

**V4 Key Changes:**
- Added input validation step before processing
- Introduced 3-step intelligence gathering phase
- Intelligence outputs feed into resume and cover letter generation
- Removed separate humanization steps (integrated into generation)
- Consolidated rendering and compilation steps
- Total pipeline: 13 steps (up from 10)

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
- Intelligence bot configuration (V4)

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

## Step 2: Input Validation (V4)

### Purpose
Validate job inputs before processing to ensure all required data is present and properly formatted, preventing wasted API calls and providing early error detection.

### Input
- Job data from applications.yaml
- Required fields: company_name, job_title, job_description

### Process

#### Validation Checks
The `_validate_job_inputs()` method performs:
1. **Required Field Presence**: Ensures company_name, job_title, and job_description exist
2. **Type Validation**: Confirms all fields are strings
3. **Non-Empty Validation**: Verifies fields contain actual content (not just whitespace)
4. **Data Integrity**: Checks for None values or missing keys

#### Validation Logic
```python
- Check if company_name exists and is non-empty string
- Check if job_title exists and is non-empty string  
- Check if job_description exists and is non-empty string
- Raise ValueError with specific field name if validation fails
```

### Error Handling

#### Validation Failure
If any required field is missing or invalid:
- Raises ValueError with descriptive message
- Specifies which field failed validation
- Pipeline halts immediately
- No API calls are made
- User receives clear error message

#### Success Path
If all validations pass:
- Pipeline proceeds to intelligence gathering phase
- Job data is confirmed ready for processing
- Logging confirms successful validation

### Design Rationale
Early validation prevents wasted API calls and provides immediate feedback to users about data quality issues. This fail-fast approach saves time and API costs while improving user experience.

---

## Step 3: Job Resonance Analysis (V4 Intelligence Step 1)

### Purpose
Analyze the job description to identify key requirements, skills, and qualifications that should be emphasized in the tailored resume and cover letter.

### Input
- Job description text
- Job title
- Company name
- Master resume JSON

### Process

#### Prompt Construction
The system loads the `analyze_job_resonance.txt` prompt template and includes:
- Job description for analysis
- Job title and company context
- Master resume for matching capabilities
- Instructions for structured analysis

#### AI Analysis
The AI performs deep analysis to extract:
- **Key Requirements**: Must-have skills and qualifications
- **Nice-to-Have Skills**: Preferred but not required capabilities
- **Cultural Indicators**: Company values and work environment signals
- **Experience Level**: Seniority expectations and career stage
- **Technical Stack**: Technologies, tools, and methodologies mentioned
- **Soft Skills**: Communication, leadership, teamwork requirements

#### Output Structure
The AI generates a JSON object conforming to the JobResonanceAnalysis schema:
```json
{
  "key_requirements": ["req1", "req2", ...],
  "nice_to_have_skills": ["skill1", "skill2", ...],
  "cultural_indicators": ["indicator1", "indicator2", ...],
  "experience_level": "description",
  "technical_stack": ["tech1", "tech2", ...],
  "soft_skills_emphasis": ["skill1", "skill2", ...]
}
```

#### Validation
The output is validated using:
1. **Pydantic Model**: JobResonanceAnalysis enforces schema compliance
2. **Quality Checks**: `_validate_intelligence_output()` ensures:
   - Each array has 3-10 items
   - Each item is 10-200 characters
   - experience_level is 50-500 characters
   - No empty or trivial content

#### Retry Logic
Uses `_call_intelligence_step_with_retry()` wrapper:
- Maximum 3 attempts
- Progressive error feedback on failures
- Detailed validation error messages
- Context preservation across retries

### Error Handling

#### Validation Failures
If output fails validation:
1. Specific errors identified (array size, character limits, etc.)
2. Error feedback constructed with examples
3. AI receives feedback with retry request
4. Process repeats up to 3 times

#### Maximum Retry Exhaustion
After 3 failed attempts:
- Pipeline halts with detailed error report
- Last attempt's output preserved for debugging
- User notified of specific validation failures

### Design Rationale
Job resonance analysis provides structured context that guides all subsequent generation steps. By identifying what matters most in the job description, the system can make informed decisions about which experiences and skills to emphasize.

---

## Step 4: Company Research (V4 Intelligence Step 2)

### Purpose
Research the company to understand its mission, values, culture, and recent developments, enabling more personalized and informed application materials.

### Input
- Company name
- Job description (for additional context)
- Job title

### Process

#### Prompt Construction
The system loads the `research_company.txt` prompt template and includes:
- Company name for research
- Job description context
- Instructions for structured research output

#### AI Research
The AI analyzes available information to extract:
- **Company Mission**: Core purpose and objectives
- **Company Values**: Stated principles and cultural priorities
- **Recent News**: Notable developments, achievements, or changes
- **Industry Position**: Market standing and competitive landscape
- **Work Culture**: Environment, practices, and employee experience indicators
- **Growth Stage**: Startup, scale-up, established, enterprise

#### Output Structure
The AI generates a JSON object conforming to the CompanyResearch schema:
```json
{
  "company_mission": "mission statement",
  "company_values": ["value1", "value2", ...],
  "recent_news": ["news1", "news2", ...],
  "industry_position": "description",
  "work_culture_indicators": ["indicator1", "indicator2", ...],
  "growth_stage": "stage description"
}
```

#### Validation
The output is validated using:
1. **Pydantic Model**: CompanyResearch enforces schema compliance
2. **Quality Checks**: `_validate_intelligence_output()` ensures:
   - company_mission is 50-500 characters
   - company_values array has 3-8 items (10-100 chars each)
   - recent_news array has 2-6 items (20-300 chars each)
   - industry_position is 50-500 characters
   - work_culture_indicators array has 3-10 items (10-200 chars each)
   - growth_stage is 20-200 characters

#### Retry Logic
Uses `_call_intelligence_step_with_retry()` wrapper:
- Maximum 3 attempts
- Progressive error feedback on failures
- Detailed validation error messages
- Context preservation across retries

### Error Handling

#### Validation Failures
If output fails validation:
1. Specific errors identified (character limits, array sizes, etc.)
2. Error feedback constructed with actionable guidance
3. AI receives feedback with retry request
4. Process repeats up to 3 times

#### Maximum Retry Exhaustion
After 3 failed attempts:
- Pipeline halts with detailed error report
- Last attempt's output preserved for debugging
- User notified of specific validation failures

### Design Rationale
Company research enables personalized application materials that demonstrate genuine interest and cultural fit. Understanding the company's mission, values, and current state allows for more authentic and compelling narratives in both resume and cover letter.

---

## Step 5: Storytelling Arc Generation (V4 Intelligence Step 3)

### Purpose
Generate a narrative structure for the cover letter that connects the candidate's background to the job opportunity in a compelling, coherent way.

### Input
- Job resonance analysis output
- Company research output
- Master resume JSON
- Job description
- Job title
- Company name

### Process

#### Prompt Construction
The system loads the `generate_storytelling_arc.txt` prompt template and includes:
- Job resonance analysis for context
- Company research for personalization
- Master resume for candidate background
- Job description and details
- Instructions for narrative structure

#### AI Narrative Design
The AI creates a storytelling framework with:
- **Opening Hook**: Attention-grabbing introduction that establishes connection
- **Background Bridge**: How candidate's experience relates to opportunity
- **Value Proposition**: Specific ways candidate can contribute
- **Cultural Alignment**: Connection to company values and mission
- **Closing Vision**: Forward-looking statement about potential impact

#### Output Structure
The AI generates a JSON object conforming to the StorytellingArc schema:
```json
{
  "opening_hook": "compelling introduction",
  "background_bridge": "experience connection",
  "value_proposition": "specific contributions",
  "cultural_alignment": "values connection",
  "closing_vision": "future impact statement"
}
```

#### Validation
The output is validated using:
1. **Pydantic Model**: StorytellingArc enforces schema compliance
2. **Quality Checks**: `_validate_intelligence_output()` ensures:
   - opening_hook is 100-400 characters
   - background_bridge is 150-600 characters
   - value_proposition is 150-600 characters
   - cultural_alignment is 100-400 characters
   - closing_vision is 100-400 characters
   - No generic or template-like content

#### Retry Logic
Uses `_call_intelligence_step_with_retry()` wrapper:
- Maximum 3 attempts
- Progressive error feedback on failures
- Detailed validation error messages
- Context preservation across retries

### Error Handling

#### Validation Failures
If output fails validation:
1. Specific errors identified (character limits, generic content, etc.)
2. Error feedback constructed with examples of good vs. bad content
3. AI receives feedback with retry request
4. Process repeats up to 3 times

#### Maximum Retry Exhaustion
After 3 failed attempts:
- Pipeline halts with detailed error report
- Last attempt's output preserved for debugging
- User notified of specific validation failures

### Design Rationale
The storytelling arc provides a coherent narrative structure that guides cover letter generation. By planning the narrative before writing, the system ensures the cover letter tells a compelling, logical story rather than a disconnected list of qualifications.

---

## Step 6: Resume Generation (V4 Enhanced)

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
Separating content generation from formatting allows the AI to focus on semantic understanding and relevance matching. The structured JSON output enables validation before rendering. In V4, resume generation is enhanced by intelligence context from previous steps.

---

## Step 7: Resume Validation (V4)

### Purpose
Ensure the AI-generated resume JSON conforms to the TailoredResume schema and meets all validation constraints.

### Process
Uses the same Pydantic validation approach as previous versions, enforcing:
- Type correctness and required field presence
- Character length limits (bullets ≤100, skills ≤100, tech ≤100)
- Array size constraints (exactly 4 bullets, exactly 3 work experiences)
- Field name enforcement

### Error Handling
- Validation failures trigger retry with detailed error feedback
- Maximum 3 retry attempts
- Progressive error messages guide AI corrections
- Pipeline halts after exhausting retries

### Design Rationale
Proactive validation catches errors before rendering, preventing invalid LaTeX generation and wasted compilation time.

---

## Step 8: Cover Letter Generation (V4 Enhanced)

### Purpose
Generate a tailored cover letter using the storytelling arc from the intelligence phase to create a compelling narrative.

### Input
- Storytelling arc (from Step 5)
- Job resonance analysis (from Step 3)
- Company research (from Step 4)
- Validated resume JSON
- Job description and details

### Process
The AI uses the pre-planned storytelling arc to generate a coherent cover letter that:
- Follows the narrative structure from the storytelling arc
- References specific job requirements identified in resonance analysis
- Demonstrates cultural fit using company research insights
- Maintains consistency with resume content
- Delivers a compelling, personalized message

### Design Rationale
Using the storytelling arc ensures the cover letter tells a coherent story rather than a disconnected list of qualifications. The intelligence context enables more authentic and compelling narratives.

---

## Step 9-13: Rendering and Compilation (V4)

The remaining steps handle template rendering and PDF compilation:

**Step 9-10: Template Rendering**
- Resume LaTeX rendering using Jinja2 templates
- Cover letter LaTeX rendering with custom filters
- LaTeX character escaping and formatting

**Step 11-12: PDF Compilation**
- Resume PDF compilation with pdflatex
- Cover letter PDF compilation
- Referral versions if configured

**Step 13: Cleanup and Finalization**
- Organize output files
- Move intermediate files to debug directory
- Update job status to "processed"
- Preserve source files for debugging

These steps remain largely unchanged from previous versions, maintaining the robust rendering and compilation pipeline.

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

### Timing Breakdown (V4)
Typical execution times for each step:

1. Configuration Loading: < 1 second
2. Input Validation: < 1 second
3. Job Resonance Analysis: 10-30 seconds (AI dependent)
4. Company Research: 10-30 seconds (AI dependent)
5. Storytelling Arc Generation: 10-30 seconds (AI dependent)
6. Resume Generation: 10-30 seconds (AI dependent)
7. Resume Validation: < 1 second
8. Cover Letter Generation: 10-30 seconds (AI dependent)
9-13. Rendering & Compilation: 5-10 seconds

**Total Time:** 60-150 seconds depending on configuration and API response times

**V4 Impact:** Intelligence gathering adds 30-90 seconds but significantly improves output quality

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

---

## Conclusion

The V4 13-step pipeline provides a robust, intelligence-driven architecture for generating highly tailored application materials. The addition of the intelligence gathering phase (job resonance analysis, company research, and storytelling arc generation) enables contextual understanding that significantly enhances the quality and relevance of generated resumes and cover letters.

**Key V4 Improvements:**
- **Intelligence-First Approach**: Three dedicated analysis steps before generation
- **Quality Validation**: Multi-layered validation beyond schema compliance
- **Generic Retry System**: Unified error handling across intelligence steps
- **Input Validation**: Early detection of data quality issues
- **Contextual Generation**: Resume and cover letter generation informed by intelligence

The sequential design with comprehensive error handling ensures reliability, while the modular structure enables easy extension and customization. The V4 architecture represents a significant evolution toward more intelligent, context-aware document generation.
