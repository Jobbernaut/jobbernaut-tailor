# Pydantic Models and Validation

## Overview

Jobbernaut Tailor uses Pydantic for type-safe data validation throughout the pipeline. This document explains the model architecture, validation rules, error handling, and design rationale behind the validation system.

## Why Pydantic?

### Type Safety
Pydantic provides compile-time type checking that catches errors before they reach the rendering stage. This prevents entire classes of runtime errors.

### Automatic Validation
Models automatically validate data when instantiated. No need for manual validation logic scattered throughout the codebase.

### Clear Error Messages
When validation fails, Pydantic provides detailed, structured error messages that pinpoint exactly what went wrong and where.

### JSON Schema Generation
Pydantic models can automatically generate JSON schemas, which are used to instruct the AI on the expected output format.

### Performance
Pydantic is built on top of Python's type hints and uses Rust-based validation for performance-critical operations.

---

## Model Hierarchy

The validation system is organized into a hierarchical structure of models, each responsible for validating a specific aspect of the resume or cover letter.

```
TailoredResume
├── ContactInfo
├── Education (array)
├── WorkExperience (array)
├── Project (array, optional)
└── Skills (array)

CoverLetter
├── ContactInfo
├── RecipientInfo (optional)
├── Opening (string)
├── Body (array of strings)
└── Closing (string)
```

---

## ContactInfo Model

### Purpose
Validates contact information for both resumes and cover letters, ensuring all required fields are present and properly formatted.

### Fields

#### name (required)
- Type: String
- Validation: Non-empty string
- Purpose: Candidate's full name
- Example: "John Smith"

#### email (required)
- Type: String
- Validation: Valid email format
- Purpose: Primary contact email
- Example: "john.smith@email.com"

#### phone (required)
- Type: String
- Validation: Phone number format
- Purpose: Contact phone number
- Example: "+1 (555) 123-4567"

#### location (required)
- Type: String
- Validation: Non-empty string
- Purpose: City and state/country
- Example: "San Francisco, CA"

#### linkedin (optional)
- Type: String or None
- Validation: Valid URL format if provided
- Purpose: LinkedIn profile URL
- Example: "linkedin.com/in/johnsmith"

#### github (optional)
- Type: String or None
- Validation: Valid URL format if provided
- Purpose: GitHub profile URL
- Example: "github.com/johnsmith"

#### website (optional)
- Type: String or None
- Validation: Valid URL format if provided
- Purpose: Personal website or portfolio
- Example: "johnsmith.dev"

### Validation Rules

#### Email Format
Uses regex pattern to validate email structure:
- Must contain @ symbol
- Must have domain extension
- Allows common email formats

#### Phone Format
Flexible phone number validation:
- Accepts various formats
- Handles international numbers
- Allows parentheses and dashes

#### URL Format
Validates URL structure for social links:
- Checks for valid domain
- Allows http/https protocols
- Accepts URLs without protocol prefix

### Design Rationale
Contact information is critical for application success. Strict validation ensures this information is always present and correctly formatted.

---

## Education Model

### Purpose
Validates educational background entries, ensuring all required academic information is present and properly structured.

### Fields

#### institution (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 100 characters
- Purpose: Name of educational institution
- Example: "Stanford University"

#### degree (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 100 characters
- Purpose: Degree type and level
- Example: "Bachelor of Science"

#### field (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 100 characters
- Purpose: Field of study or major
- Example: "Computer Science"

#### start_date (required)
- Type: String
- Validation: Date format
- Purpose: When studies began
- Example: "September 2018"

#### end_date (required)
- Type: String
- Validation: Date format or "Present"
- Purpose: When studies ended or expected to end
- Example: "May 2022" or "Present"

#### gpa (optional)
- Type: Float or None
- Validation: Range 0.0 to 4.0
- Purpose: Grade point average
- Example: 3.85

#### location (optional)
- Type: String or None
- Validation: Non-empty if provided
- Purpose: Institution location
- Example: "Stanford, CA"

#### honors (optional)
- Type: Array of strings or None
- Validation: Each honor limited to 100 characters
- Purpose: Academic honors and awards
- Example: ["Summa Cum Laude", "Dean's List"]

### Validation Rules

#### GPA Range
If GPA is provided, it must be between 0.0 and 4.0:
- Validates against common US GPA scale
- Rejects negative values
- Rejects values above 4.0

#### Date Consistency
Start date should precede end date:
- Validates chronological order
- Allows "Present" for ongoing education
- Handles various date formats

#### Character Limits
Prevents excessively long text:
- Institution name: 100 characters
- Degree: 100 characters
- Field: 100 characters
- Each honor: 100 characters

### Design Rationale
Education information must be concise yet complete. Character limits ensure content fits within resume formatting constraints while validation ensures accuracy.

---

## WorkExperience Model

### Purpose
Validates work experience entries, ensuring job descriptions are properly structured and within character limits.

### Fields

#### company (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 100 characters
- Purpose: Employer name
- Example: "Google"

#### position (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 100 characters
- Purpose: Job title
- Example: "Senior Software Engineer"

#### start_date (required)
- Type: String
- Validation: Date format
- Purpose: Employment start date
- Example: "January 2020"

#### end_date (required)
- Type: String
- Validation: Date format or "Present"
- Purpose: Employment end date
- Example: "December 2023" or "Present"

#### location (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 100 characters
- Purpose: Job location
- Example: "Mountain View, CA"

#### description (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 600 characters
- Purpose: Brief role overview
- Example: "Led development of cloud infrastructure..."

#### bullet_points (required)
- Type: Array of strings
- Validation: 2-5 items, each max 200 characters
- Purpose: Key achievements and responsibilities
- Example: ["Designed scalable API...", "Reduced latency by 40%..."]

### Validation Rules

#### Bullet Points Array
Strict constraints on bullet points:
- Minimum: 2 bullet points
- Maximum: 5 bullet points
- Each bullet point: max 200 characters
- All must be non-empty strings

#### Description Length
The description field is limited to 600 characters:
- Ensures concise overview
- Prevents overly verbose descriptions
- Maintains resume readability

#### Date Validation
Similar to education:
- Start date before end date
- "Present" allowed for current positions
- Consistent date formatting

### Design Rationale
Work experience is the most critical resume section. Strict validation ensures content is impactful yet concise, fitting within standard resume formatting.

---

## Project Model

### Purpose
Validates project entries, ensuring technical projects are properly documented with relevant details.

### Fields

#### name (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 100 characters
- Purpose: Project name
- Example: "E-commerce Platform"

#### description (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 400 characters
- Purpose: Project overview and impact
- Example: "Built full-stack web application..."

#### technologies (required)
- Type: Array of strings
- Validation: 1-10 items, each max 50 characters
- Purpose: Technologies and tools used
- Example: ["React", "Node.js", "PostgreSQL"]

#### start_date (optional)
- Type: String or None
- Validation: Date format if provided
- Purpose: When project began
- Example: "June 2023"

#### end_date (optional)
- Type: String or None
- Validation: Date format or "Present"
- Purpose: When project completed
- Example: "August 2023" or "Present"

#### url (optional)
- Type: String or None
- Validation: Valid URL format if provided
- Purpose: Project link (GitHub, demo, etc.)
- Example: "github.com/user/project"

### Validation Rules

#### Technologies Array
Constraints on technology list:
- Minimum: 1 technology
- Maximum: 10 technologies
- Each technology: max 50 characters
- Prevents overly long lists

#### Description Length
Limited to 400 characters:
- More concise than work experience
- Focuses on key achievements
- Maintains resume balance

### Design Rationale
Projects demonstrate practical skills. Validation ensures they're presented concisely with relevant technical details without overwhelming the resume.

---

## TailoredResume Model

### Purpose
Top-level model that aggregates all resume components and validates the complete resume structure.

### Fields

#### contact_info (required)
- Type: ContactInfo model
- Validation: All ContactInfo rules apply
- Purpose: Candidate contact details

#### summary (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 500 characters
- Purpose: Professional summary or objective

#### education (required)
- Type: Array of Education models
- Validation: At least 1 entry, max 5 entries
- Purpose: Academic background

#### work_experience (required)
- Type: Array of WorkExperience models
- Validation: At least 1 entry, max 10 entries
- Purpose: Professional experience

#### skills (required)
- Type: Array of strings
- Validation: At least 3 skills, max 30 skills
- Purpose: Technical and soft skills
- Each skill: max 50 characters

#### projects (optional)
- Type: Array of Project models or None
- Validation: Max 5 projects if provided
- Purpose: Personal or academic projects

#### certifications (optional)
- Type: Array of strings or None
- Validation: Max 10 certifications if provided
- Purpose: Professional certifications
- Each certification: max 100 characters

### Validation Rules

#### Array Size Constraints
Prevents resumes from being too sparse or too dense:
- Education: 1-5 entries
- Work Experience: 1-10 entries
- Skills: 3-30 items
- Projects: 0-5 entries
- Certifications: 0-10 entries

#### Summary Length
Professional summary limited to 500 characters:
- Ensures conciseness
- Maintains resume focus
- Prevents verbose introductions

### Design Rationale
The top-level model ensures the complete resume is balanced and comprehensive. Array constraints prevent both sparse and overwhelming resumes.

---

## CoverLetter Model

### Purpose
Validates cover letter structure, ensuring proper business letter format and appropriate content length.

### Fields

#### contact_info (required)
- Type: ContactInfo model
- Validation: All ContactInfo rules apply
- Purpose: Candidate contact details

#### recipient_info (optional)
- Type: RecipientInfo model or None
- Validation: RecipientInfo rules if provided
- Purpose: Hiring manager details

#### date (required)
- Type: String
- Validation: Date format
- Purpose: Letter date
- Example: "October 19, 2025"

#### opening (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 500 characters
- Purpose: Introduction paragraph

#### body (required)
- Type: Array of strings
- Validation: 2-3 paragraphs, each max 600 characters
- Purpose: Main content paragraphs

#### closing (required)
- Type: String
- Validation: Non-empty string
- Character Limit: 400 characters
- Purpose: Closing paragraph

#### signature (required)
- Type: String
- Validation: Non-empty string
- Purpose: Closing salutation
- Example: "Best regards"

### Validation Rules

#### Paragraph Structure
Cover letter must have proper structure:
- Opening: 1 paragraph, max 500 characters
- Body: 2-3 paragraphs, each max 600 characters
- Closing: 1 paragraph, max 400 characters

#### Total Length
Combined character limits ensure:
- Cover letter fits on one page
- Content is concise and impactful
- Maintains reader engagement

### Design Rationale
Cover letters must follow business letter conventions. Validation ensures proper structure and appropriate length for professional correspondence.

---

## Validation Error Handling

### Error Detection
When validation fails, Pydantic captures:
- Field name where error occurred
- Type of validation error
- Expected vs actual value
- Location in nested structure

### Error Feedback Construction
The system transforms Pydantic errors into AI-friendly feedback:

#### Error Message Format
```
Validation Error in [field_name]:
- Issue: [description]
- Expected: [requirement]
- Received: [actual_value]
- Fix: [suggested correction]
```

#### Multiple Errors
When multiple validation errors occur:
- All errors are collected
- Grouped by model/section
- Prioritized by severity
- Presented in logical order

### Retry Mechanism

#### Automatic Retry
When validation fails:
1. Capture all validation errors
2. Format errors into feedback message
3. Include original prompt and failed output
4. Request AI to regenerate with corrections
5. Validate new output
6. Repeat up to maximum retry attempts

#### Error Context Preservation
Each retry includes:
- Original job description
- Master resume data
- Previous failed attempt
- Specific validation errors
- Correction instructions

### Maximum Retry Limit
After exhausting retries:
- Log complete error history
- Provide detailed failure report
- Exit with error code
- Preserve failed output for debugging

---

## Custom Validators

### Field Validators
Pydantic allows custom validation logic for specific fields:

#### Character Limit Validator
Ensures text fields don't exceed maximum length:
```
Validates that field length <= max_length
Provides clear error message with current and max length
```

#### Array Length Validator
Ensures arrays have appropriate number of items:
```
Validates min_items <= array_length <= max_items
Reports current count and valid range
```

#### Date Format Validator
Ensures dates follow expected format:
```
Accepts various date formats
Allows "Present" for current positions
Validates chronological consistency
```

#### URL Validator
Ensures URLs are properly formatted:
```
Validates URL structure
Allows with or without protocol
Checks domain validity
```

### Model Validators
Cross-field validation at model level:

#### Date Consistency
Ensures start_date precedes end_date:
```
Compares date fields
Allows "Present" for end_date
Reports chronological violations
```

#### Required Field Groups
Ensures related fields are present together:
```
If field A is present, field B must be present
Validates logical dependencies
Reports missing required companions
```

---

## Schema Generation

### JSON Schema Export
Pydantic models can generate JSON schemas:

#### Purpose
- Document expected structure for AI
- Provide validation reference
- Enable schema-based tooling
- Support API documentation

#### Schema Contents
Generated schemas include:
- Field names and types
- Required vs optional fields
- Validation constraints
- Character limits
- Array size constraints
- Format requirements

### Schema Usage in Prompts
The generated schema is included in AI prompts:
- Provides clear structure expectations
- Reduces validation failures
- Improves AI output quality
- Enables self-correction

---

## Performance Considerations

### Validation Speed
Pydantic validation is fast:
- Rust-based core for performance
- Compiled validation logic
- Minimal overhead
- Sub-millisecond validation for typical resumes

### Memory Efficiency
Models are memory-efficient:
- Lazy validation where possible
- Efficient data structures
- Minimal object overhead
- Garbage collection friendly

### Optimization Strategies
For large-scale processing:
- Reuse model instances
- Cache compiled validators
- Batch validation when possible
- Profile validation bottlenecks

---

## Extension and Customization

### Adding New Fields
To add fields to existing models:
1. Define field with type annotation
2. Add validation constraints
3. Update JSON schema
4. Modify templates to use new field
5. Update prompts to generate field

### Creating New Models
To add new model types:
1. Define Pydantic model class
2. Implement field validators
3. Add model validators if needed
4. Generate JSON schema
5. Integrate into pipeline

### Custom Validation Logic
To add custom validators:
1. Define validator function
2. Decorate with @validator
3. Specify field(s) to validate
4. Return validated value or raise error
5. Provide clear error messages

---

## Best Practices

### Model Design
- Keep models focused and cohesive
- Use composition over inheritance
- Validate at appropriate level
- Provide clear field names

### Validation Rules
- Make constraints explicit
- Provide helpful error messages
- Validate early and often
- Fail fast on critical errors

### Error Handling
- Capture all validation errors
- Provide actionable feedback
- Log errors for debugging
- Preserve context for retries

### Testing
- Test valid inputs
- Test boundary conditions
- Test invalid inputs
- Test error messages

---

## Common Validation Scenarios

### Character Limit Exceeded
**Error:** Field exceeds maximum character limit
**Cause:** AI generated overly verbose content
**Solution:** Retry with explicit length constraint in feedback

### Missing Required Field
**Error:** Required field not present in output
**Cause:** AI omitted field from JSON
**Solution:** Retry with emphasis on required fields

### Invalid Array Length
**Error:** Array has too few or too many items
**Cause:** AI didn't respect array constraints
**Solution:** Retry with specific array size requirements

### Type Mismatch
**Error:** Field has wrong type
**Cause:** AI used string instead of array, etc.
**Solution:** Retry with explicit type requirements

### Invalid Date Format
**Error:** Date doesn't match expected format
**Cause:** AI used inconsistent date formatting
**Solution:** Retry with date format examples

---

## Debugging Validation Issues

### Enable Detailed Logging
Configure logging to capture:
- Full validation error details
- Input data that failed validation
- Stack traces for debugging
- Retry attempt history

### Inspect Failed Output
When validation fails:
- Examine the AI-generated JSON
- Compare against schema
- Identify specific violations
- Understand root cause

### Test Validation Rules
Validate rules independently:
- Create test cases for each validator
- Test boundary conditions
- Verify error messages
- Ensure consistent behavior

---

## Future Enhancements

### Potential Improvements
- Dynamic validation rules based on job type
- Machine learning for optimal character limits
- Context-aware validation
- Validation rule versioning
- Schema evolution support

### Extensibility
The validation system is designed for extension:
- New models can be added easily
- Validation rules can be customized
- Error handling can be enhanced
- Integration with other systems is straightforward

---

## Conclusion

The Pydantic validation system provides robust, type-safe data validation that catches errors early and provides clear feedback for correction. This proactive approach ensures high-quality output while maintaining flexibility for customization and extension.
