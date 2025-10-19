# Template Architecture

## Overview

Jobbernaut Tailor uses Jinja2 templates to convert validated JSON data into properly formatted LaTeX documents. This document explains the template system architecture, custom delimiters, filters, design patterns, and best practices.

## Why Jinja2?

### Separation of Concerns
Templates separate presentation logic from business logic. Content generation happens in Python, formatting happens in templates.

### Deterministic Output
Unlike AI-generated LaTeX, templates produce identical output for identical input. This predictability is crucial for production systems.

### Maintainability
Changing document formatting requires editing templates, not modifying code or retraining AI models. Non-programmers can make formatting changes.

### Reusability
Template components can be reused across different document types. Common patterns are defined once and used everywhere.

### Performance
Template rendering is orders of magnitude faster than AI-based LaTeX generation, with no API costs.

---

## Custom Delimiters

### The LaTeX Conflict Problem

Standard Jinja2 uses curly braces for delimiters:
- Variables: `{{ variable }}`
- Blocks: `{% for item in items %}`
- Comments: `{# comment #}`

LaTeX also uses curly braces extensively:
- Commands: `\textbf{bold text}`
- Environments: `\begin{itemize}`
- Groups: `{\large text}`

This creates conflicts where Jinja2 tries to interpret LaTeX syntax as template code.

### Custom Delimiter Solution

Jobbernaut Tailor uses backslash-based delimiters that integrate naturally with LaTeX:

#### Variable Delimiter
- **Syntax:** `\VAR{variable_name}`
- **Purpose:** Insert variable values
- **Example:** `\VAR{contact_info.name}`

#### Block Delimiter
- **Syntax:** `\BLOCK{statement}`
- **Purpose:** Control flow (loops, conditionals)
- **Example:** `\BLOCK{for exp in work_experience}`

#### Comment Delimiter
- **Syntax:** `\#{comment text}`
- **Purpose:** Template comments (not rendered)
- **Example:** `\#{This is a template comment}`

### Benefits of Custom Delimiters

#### No Escaping Required
LaTeX code can be written naturally without escaping curly braces. This makes templates more readable and maintainable.

#### Visual Clarity
The backslash prefix clearly distinguishes template code from LaTeX code, improving template readability.

#### LaTeX Integration
The delimiter style matches LaTeX command syntax, making templates feel like natural LaTeX extensions.

---

## Template Structure

### Resume Template

The resume template is organized into logical sections that mirror the resume structure:

#### Document Preamble
```
Document class declaration
Package imports
Custom command definitions
Page layout settings
```

#### Contact Information Section
```
Name (large, bold)
Contact details (email, phone, location)
Social links (LinkedIn, GitHub, website)
Horizontal rule separator
```

#### Professional Summary Section
```
Section heading
Summary text with proper formatting
Spacing after section
```

#### Work Experience Section
```
Section heading
For each work experience:
  - Company and position (bold)
  - Dates and location (italic)
  - Description paragraph
  - Bullet points list
  - Spacing between entries
```

#### Education Section
```
Section heading
For each education entry:
  - Institution and degree (bold)
  - Dates and location (italic)
  - GPA (if present)
  - Honors (if present)
  - Spacing between entries
```

#### Skills Section
```
Section heading
Skills formatted as comma-separated list
Proper line breaking for long lists
```

#### Projects Section (Optional)
```
Section heading (if projects exist)
For each project:
  - Project name (bold)
  - Technologies used
  - Description
  - URL (if present)
  - Spacing between entries
```

#### Certifications Section (Optional)
```
Section heading (if certifications exist)
Certifications as formatted list
Proper spacing
```

### Cover Letter Template

The cover letter template follows business letter format:

#### Document Preamble
```
Document class declaration
Package imports
Letter-specific settings
Date formatting
```

#### Sender Information
```
Candidate name
Contact information
Date
```

#### Recipient Information (Optional)
```
Hiring manager name (if known)
Company name
Company address
```

#### Salutation
```
Greeting (personalized if recipient known)
Default to "Dear Hiring Manager"
```

#### Letter Body
```
Opening paragraph
Body paragraphs (2-3)
Closing paragraph
```

#### Signature Block
```
Closing phrase ("Best regards")
Candidate name
```

---

## Custom Filters

Jinja2 filters transform variable values during rendering. Jobbernaut Tailor implements several custom filters for LaTeX-specific needs.

### latex_escape Filter

#### Purpose
Escape special LaTeX characters to prevent compilation errors.

#### Special Characters Handled
- Ampersand: `&` → `\&`
- Percent: `%` → `\%`
- Dollar: `$` → `\$`
- Hash: `#` → `\#`
- Underscore: `_` → `\_`
- Curly braces: `{` → `\{`, `}` → `\}`
- Tilde: `~` → `\textasciitilde{}`
- Caret: `^` → `\textasciicircum{}`
- Backslash: `\` → `\textbackslash{}`

#### Usage
```
\VAR{description|latex_escape}
```

#### Design Rationale
AI-generated content may include special characters that break LaTeX compilation. This filter ensures all text is properly escaped.

### format_date Filter

#### Purpose
Convert various date formats into consistent, professional format.

#### Input Formats Accepted
- "January 2020"
- "Jan 2020"
- "2020-01"
- "01/2020"
- "Present"

#### Output Format
- "January 2020" (full month name, year)
- "Present" (unchanged for current positions)

#### Usage
```
\VAR{start_date|format_date} -- \VAR{end_date|format_date}
```

#### Design Rationale
Consistent date formatting across all resume sections improves professional appearance. The filter handles various input formats from AI.

### format_phone Filter

#### Purpose
Format phone numbers consistently and professionally.

#### Input Formats Accepted
- "+1 555-123-4567"
- "(555) 123-4567"
- "555.123.4567"
- "5551234567"

#### Output Format
- "+1 (555) 123-4567" (international format with parentheses)

#### Usage
```
\VAR{contact_info.phone|format_phone}
```

#### Design Rationale
Professional phone number formatting improves resume appearance and ensures international compatibility.

---

## Template Patterns

### Conditional Sections

#### Optional Fields
```
\BLOCK{if contact_info.linkedin}
LinkedIn: \VAR{contact_info.linkedin}
\BLOCK{endif}
```

#### Optional Sections
```
\BLOCK{if projects}
\section*{Projects}
\BLOCK{for project in projects}
...
\BLOCK{endfor}
\BLOCK{endif}
```

### Iteration Patterns

#### Work Experience Loop
```
\BLOCK{for exp in work_experience}
\textbf{\VAR{exp.company}} -- \VAR{exp.position}
\BLOCK{for bullet in exp.bullet_points}
\item \VAR{bullet|latex_escape}
\BLOCK{endfor}
\BLOCK{endfor}
```

#### Skills List
```
\BLOCK{for skill in skills}
\VAR{skill}\BLOCK{if not loop.last}, \BLOCK{endif}
\BLOCK{endfor}
```

### Spacing and Layout

#### Section Spacing
```
\vspace{0.2cm}  % Space after section
```

#### Entry Spacing
```
\vspace{0.15cm}  % Space between entries
```

#### Paragraph Spacing
```
\setlength{\parskip}{0.1cm}
```

---

## LaTeX Packages and Configuration

### Essential Packages

#### geometry
```
Purpose: Page layout and margins
Configuration: 1-inch margins all around
```

#### hyperref
```
Purpose: Clickable links for email, LinkedIn, GitHub
Configuration: Colored links, no borders
```

#### enumitem
```
Purpose: Customized bullet point lists
Configuration: Reduced spacing, custom bullets
```

#### fontenc and inputenc
```
Purpose: Character encoding and font support
Configuration: UTF-8 input, T1 font encoding
```

### Document Class

#### article
```
Purpose: Standard document class for resumes
Configuration: 11pt font, letter paper
```

### Custom Commands

#### Section Formatting
```
Custom section command for consistent styling
Bold, larger font for section headings
Horizontal rule under headings
```

#### Contact Information
```
Custom command for contact details
Icon support (optional)
Consistent spacing
```

---

## Template Rendering Process

### Initialization

#### Template Loader
```
1. Create Jinja2 environment
2. Set custom delimiters
3. Register custom filters
4. Load template files
```

#### Environment Configuration
```
- Auto-escape disabled (LaTeX handles escaping)
- Trim blocks enabled (cleaner output)
- Strip blocks enabled (remove extra whitespace)
```

### Rendering Steps

#### Data Preparation
```
1. Receive validated JSON data
2. Convert to Python dictionary
3. Prepare template context
```

#### Template Execution
```
1. Load appropriate template
2. Pass context to template
3. Execute template logic
4. Apply filters to variables
5. Generate LaTeX output
```

#### Post-Processing
```
1. Validate LaTeX syntax (basic check)
2. Write to output file
3. Log rendering completion
```

---

## Error Handling

### Template Errors

#### Undefined Variable
```
Error: Variable not found in context
Cause: Template references non-existent field
Solution: Use conditional checks or provide default
```

#### Filter Error
```
Error: Filter raises exception
Cause: Invalid input to filter
Solution: Add error handling in filter
```

#### Syntax Error
```
Error: Invalid template syntax
Cause: Malformed template code
Solution: Fix template syntax, validate with linter
```

### LaTeX Compilation Errors

#### Missing Package
```
Error: LaTeX package not found
Cause: Required package not installed
Solution: Install missing package or remove dependency
```

#### Syntax Error
```
Error: LaTeX compilation fails
Cause: Invalid LaTeX code in template
Solution: Fix template LaTeX syntax
```

---

## Best Practices

### Template Design

#### Keep Templates Simple
- Avoid complex logic in templates
- Move complexity to Python code
- Use filters for transformations

#### Use Consistent Formatting
- Define spacing constants
- Use consistent command names
- Maintain uniform style

#### Comment Complex Sections
- Explain non-obvious template logic
- Document custom commands
- Note LaTeX-specific requirements

### Variable Naming

#### Use Descriptive Names
- `contact_info.email` not `ci.e`
- `work_experience` not `we`
- `bullet_points` not `bp`

#### Follow Conventions
- Snake_case for variables
- Lowercase for fields
- Consistent naming across templates

### Filter Usage

#### Apply Filters Consistently
- Always escape user-generated content
- Format dates uniformly
- Use filters for all transformations

#### Chain Filters When Needed
```
\VAR{description|latex_escape|truncate(100)}
```

---

## Template Customization

### Styling Changes

#### Fonts
```
Modify font family in preamble
Change font sizes for sections
Adjust font weights
```

#### Colors
```
Define color scheme
Apply to section headings
Use for links and accents
```

#### Spacing
```
Adjust margins
Modify section spacing
Change line spacing
```

### Layout Modifications

#### Two-Column Layout
```
Use multicol package
Split sections across columns
Balance column heights
```

#### Alternative Section Order
```
Reorder template sections
Prioritize different content
Customize for specific roles
```

#### Custom Sections
```
Add new sections
Define custom formatting
Integrate with existing layout
```

---

## Template Variants

### Industry-Specific Templates

#### Technical Resume
```
Emphasis on skills and projects
Detailed technical descriptions
GitHub and portfolio links prominent
```

#### Academic Resume
```
Focus on education and research
Publications section
Teaching experience highlighted
```

#### Creative Resume
```
Portfolio links emphasized
Visual design elements
Project showcases
```

### Format Variations

#### One-Page Resume
```
Condensed formatting
Reduced spacing
Selective content inclusion
```

#### Two-Page Resume
```
Expanded descriptions
Additional sections
More detailed experience
```

#### ATS-Optimized Resume
```
Simple formatting
No complex tables
Standard section names
Plain text friendly
```

---

## Testing Templates

### Visual Testing

#### Compile and Review
```
1. Render template with sample data
2. Compile to PDF
3. Review visual appearance
4. Check for formatting issues
```

#### Cross-Platform Testing
```
Test on different LaTeX distributions
Verify package compatibility
Check font rendering
```

### Automated Testing

#### Syntax Validation
```
Validate template syntax
Check for undefined variables
Verify filter usage
```

#### Regression Testing
```
Compare output with baseline
Detect unintended changes
Validate against test cases
```

---

## Performance Optimization

### Template Caching

#### Compiled Templates
```
Cache compiled templates
Reuse across multiple renders
Reduce compilation overhead
```

#### Template Fragments
```
Cache reusable fragments
Share across templates
Reduce duplication
```

### Rendering Optimization

#### Minimize Filter Calls
```
Apply filters once
Cache filter results
Avoid redundant transformations
```

#### Efficient Loops
```
Minimize loop iterations
Use efficient data structures
Avoid nested loops where possible
```

---

## Debugging Templates

### Enable Debug Mode

#### Verbose Output
```
Enable Jinja2 debug mode
Print variable values
Show template execution flow
```

#### Error Messages
```
Capture detailed error messages
Show line numbers
Display variable context
```

### Common Issues

#### Missing Variables
```
Check variable names
Verify data structure
Use conditional checks
```

#### Formatting Problems
```
Review LaTeX syntax
Check spacing and alignment
Validate package usage
```

#### Compilation Failures
```
Isolate problematic sections
Test incrementally
Review LaTeX logs
```

---

## Future Enhancements

### Potential Improvements

#### Template Library
```
Multiple template styles
Industry-specific variants
Customizable themes
```

#### Dynamic Layouts
```
Adaptive section ordering
Content-based formatting
Responsive design
```

#### Advanced Features
```
Multi-language support
Custom fonts and styling
Interactive elements
```

### Extensibility

#### Plugin System
```
Custom filter plugins
Template extensions
Third-party integrations
```

#### Template Inheritance
```
Base templates
Template composition
Reusable components
```

---

## Conclusion

The Jinja2 template system provides a robust, maintainable approach to document generation. Custom delimiters enable seamless LaTeX integration, while custom filters ensure proper formatting. The template-based architecture separates content from presentation, making the system flexible and easy to customize.
