# Anti-Fragile Pipeline Architecture (V4)

## Overview

The Jobbernaut V4 pipeline features robust validation, self-healing retry logic, and deterministic error handling across all 13 pipeline steps. The intelligence gathering phase introduces three new validation models with quality thresholds that go beyond schema compliance to ensure meaningful, actionable content.

## Key Features

### 1. Input Validation (`_validate_job_inputs`)

**Location**: `src/main.py` lines 194-241

**Purpose**: Validates all job inputs before processing begins

**Validations**:
- `job_id`: Non-empty string
- `job_title`: 3-200 characters
- `company_name`: 2-100 characters  
- `job_description`: 100-50,000 characters

**Behavior**: Fails fast with clear error messages if inputs are invalid

### 2. Output Quality Validation (`_validate_intelligence_output`)

**Location**: `src/main.py` lines 243-333

**Purpose**: Ensures intelligence outputs meet quality thresholds beyond Pydantic schema validation

**Quality Thresholds**:

#### JobResonanceAnalysis
- `key_requirements`: 3-15 items, each 10-200 characters, no generic content
- `nice_to_have_skills`: 2-10 items, each 10-150 characters, no generic content
- `cultural_indicators`: 2-8 items, each 10-150 characters, no generic content
- `experience_level`: 10-100 characters, meaningful content
- `technical_stack`: 3-20 items, each 2-50 characters
- `soft_skills_emphasis`: 2-8 items, each 10-100 characters, no generic content

#### CompanyResearch
- `company_mission`: 20-300 characters, specific and meaningful
- `company_values`: 3-8 items, each 10-100 characters, no generic values
- `recent_news`: 2-6 items, each 20-200 characters, recent and specific
- `industry_position`: 20-200 characters, concrete positioning
- `work_culture_indicators`: 3-10 items, each 10-150 characters, specific signals
- `growth_stage`: 10-100 characters, clear assessment

#### StorytellingArc
- `opening_hook`: 50-400 characters, compelling and specific
- `background_bridge`: 100-500 characters, meaningful connection
- `value_proposition`: 100-500 characters, concrete value
- `cultural_alignment`: 50-400 characters, authentic alignment
- `closing_vision`: 50-400 characters, forward-looking and specific

### 3. Self-Healing Retry Wrapper (`_call_intelligence_step_with_retry`)

**Location**: `src/main.py` lines 335-425

**Purpose**: Generic retry wrapper for all intelligence steps with progressive error feedback

**Retry Logic** (3 attempts per step):

1. **Attempt 1**: Execute with base prompt
2. **JSON Extraction Failure**: Append JSON parsing error feedback, retry
3. **Pydantic Validation Failure**: Append detailed field-level error feedback, retry
4. **Quality Validation Failure**: Append quality threshold error feedback, retry
5. **Final Failure**: Raise ValueError with detailed error context

**Error Feedback Types**:
- JSON parsing errors with format guidance
- Pydantic validation errors with field-specific fixes
- Quality threshold errors with content improvement guidance

### 4. Refactored Intelligence Methods

All three intelligence methods now use the retry wrapper:

#### `analyze_job_resonance` (lines 427-565)
- Uses `_call_intelligence_step_with_retry`
- Validates with `JobResonanceAnalysis` model
- 3 retry attempts with progressive feedback

#### `research_company` (lines 567-598)
- Uses `_call_intelligence_step_with_retry`
- Validates with `CompanyResearch` model
- 3 retry attempts with progressive feedback

#### `generate_storytelling_arc` (lines 600-637)
- Uses `_call_intelligence_step_with_retry`
- Validates with `StorytellingArc` model
- 3 retry attempts with progressive feedback

### 5. V4 Pipeline Execution Flow (13 Steps)

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: LOAD MASTER RESUME                                  │
│    - Load profile/master_resume.json                        │
│    - Parse candidate's complete background                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: INPUT VALIDATION (V4)                               │
│    - Validate job_id, job_title, company_name               │
│    - Validate job_description (100-50,000 chars)            │
│    - Fail fast if invalid                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: JOB RESONANCE ANALYSIS (V4 Intelligence)            │
│    ├─ Attempt 1: Base prompt                               │
│    ├─ Attempt 2: + JSON error feedback (if needed)         │
│    ├─ Attempt 3: + Pydantic/quality feedback (if needed)   │
│    └─ Validate: JobResonanceAnalysis model + quality        │
│                                                             │
│    Extracts:                                                │
│    - key_requirements (3-15 items)                          │
│    - nice_to_have_skills (2-10 items)                       │
│    - cultural_indicators (2-8 items)                        │
│    - experience_level                                       │
│    - technical_stack (3-20 items)                           │
│    - soft_skills_emphasis (2-8 items)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: COMPANY RESEARCH (V4 Intelligence)                  │
│    ├─ Attempt 1: Base prompt                               │
│    ├─ Attempt 2: + JSON error feedback (if needed)         │
│    ├─ Attempt 3: + Pydantic/quality feedback (if needed)   │
│    └─ Validate: CompanyResearch model + quality             │
│                                                             │
│    Extracts:                                                │
│    - company_mission (20-300 chars)                         │
│    - company_values (3-8 items)                             │
│    - recent_news (2-6 items)                                │
│    - industry_position (20-200 chars)                       │
│    - work_culture_indicators (3-10 items)                   │
│    - growth_stage (10-100 chars)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: STORYTELLING ARC GENERATION (V4 Intelligence)       │
│    ├─ Attempt 1: Base prompt                               │
│    ├─ Attempt 2: + JSON error feedback (if needed)         │
│    ├─ Attempt 3: + Pydantic/quality feedback (if needed)   │
│    └─ Validate: StorytellingArc model + quality             │
│                                                             │
│    Creates:                                                 │
│    - opening_hook (50-400 chars)                            │
│    - background_bridge (100-500 chars)                      │
│    - value_proposition (100-500 chars)                      │
│    - cultural_alignment (50-400 chars)                      │
│    - closing_vision (50-400 chars)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: RESUME GENERATION (V4 Enhanced)                     │
│    - Inject job resonance analysis context                  │
│    - 3 retry attempts with TailoredResume validation        │
│    - Progressive error feedback on failures                 │
│    - Validates all resume fields and constraints            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: RESUME VALIDATION (V4)                              │
│    - Pydantic schema validation (TailoredResume)            │
│    - Character limit validation                             │
│    - Array size validation                                  │
│    - Required field validation                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: COVER LETTER GENERATION (V4 Enhanced)               │
│    - Inject storytelling arc + company research             │
│    - Inject job resonance analysis                          │
│    - 3 retry attempts with CoverLetter validation           │
│    - Progressive error feedback on failures                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 9: COVER LETTER VALIDATION (V4)                        │
│    - Pydantic schema validation (CoverLetter)               │
│    - Paragraph structure validation                         │
│    - Character limit validation                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 10: RESUME LATEX RENDERING                             │
│    - Render resume.jinja2 template                          │
│    - Generate LaTeX source                                  │
│    - Save to output directory                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 11: COVER LETTER LATEX RENDERING                       │
│    - Render cover_letter.jinja2 template                    │
│    - Generate LaTeX source                                  │
│    - Save to output directory                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 12: RESUME PDF COMPILATION                             │
│    - Compile LaTeX to PDF (pdflatex)                        │
│    - Generate standard and referral versions                │
│    - Handle compilation errors                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 13: COVER LETTER PDF COMPILATION                       │
│    - Compile LaTeX to PDF (pdflatex)                        │
│    - Generate standard and referral versions                │
│    - Handle compilation errors                              │
└─────────────────────────────────────────────────────────────┘
```

## Anti-Fragile Design Principles

### 1. Fail Fast
- Input validation happens immediately before any processing
- Invalid inputs are rejected with clear error messages
- No wasted API calls on bad data

### 2. Progressive Error Feedback
- Each retry includes detailed feedback about what went wrong
- Feedback is specific to the error type (JSON, Pydantic, quality)
- AI model learns from mistakes and self-corrects

### 3. Deterministic Validation
- All validation rules are explicit and measurable
- No subjective quality checks
- Clear pass/fail criteria at every stage

### 4. Self-Healing
- Automatic retry with corrective guidance
- No manual intervention needed for common errors
- Pipeline continues if one step fails (with error logging)

### 5. Separation of Concerns
- Input validation separate from processing
- Output validation separate from generation
- Retry logic abstracted into reusable wrapper

### 6. Comprehensive Logging
- Every attempt is logged with attempt number
- Raw responses saved for debugging
- Clear success/failure indicators at each stage

## Error Handling Strategy

### Recoverable Errors (Auto-Retry)
1. **JSON Parsing Errors**: Retry with format guidance
2. **Pydantic Validation Errors**: Retry with field-specific fixes
3. **Quality Threshold Errors**: Retry with content improvement guidance

### Non-Recoverable Errors (Fail Fast)
1. **Invalid Job Inputs**: Reject immediately, no processing
2. **API Connection Failures**: Retry at API level (3 attempts)
3. **All Retries Exhausted**: Fail with detailed error context

## V4 Validation Layers

```
Layer 1: Input Validation (Step 2)
├─ Type checking (string, int, etc.)
├─ Length constraints (job_title: 3-200, company_name: 2-100, etc.)
├─ Required field presence (job_id, job_title, company_name, job_description)
└─ Character limits (job_description: 100-50,000 characters)

Layer 2: Pydantic Schema Validation (Steps 3-9)
├─ Field types match schema (string, array, etc.)
├─ Required fields present in all models
├─ Nested object structure correct
├─ Array size constraints (min/max items)
└─ Character limits per field

Layer 3: Quality Threshold Validation (Steps 3-5)
├─ Minimum content length (no trivial content)
├─ Array size constraints (meaningful number of items)
├─ No empty strings in arrays
├─ No generic phrases (e.g., "good communication skills")
└─ Meaningful, specific, actionable content

Layer 4: Content Quality Validation (V4 Intelligence Models)
├─ JobResonanceAnalysis: Specific requirements, not generic
├─ CompanyResearch: Recent, verifiable information
└─ StorytellingArc: Compelling narrative, not boilerplate
```

## Benefits

### Robustness
- Pipeline handles errors gracefully
- Self-corrects common mistakes
- Continues processing other jobs if one fails

### Determinism
- Same inputs produce same validation results
- Clear, measurable quality criteria
- No ambiguous "good enough" checks

### Maintainability
- Validation logic centralized
- Retry logic reusable across steps
- Easy to add new validation rules

### Debuggability
- All attempts saved to disk
- Clear error messages with context
- Progressive feedback shows what was tried

## Configuration

All validation thresholds are hardcoded in `_validate_intelligence_output` for determinism. To modify:

1. Edit threshold values in `src/main.py` lines 243-333
2. Update this documentation
3. Test with sample jobs to ensure thresholds are reasonable

## Testing Recommendations

1. **Valid Inputs**: Ensure pipeline completes successfully
2. **Invalid Inputs**: Verify fail-fast behavior
3. **Malformed JSON**: Confirm retry with JSON feedback
4. **Schema Violations**: Confirm retry with Pydantic feedback
5. **Low Quality Output**: Confirm retry with quality feedback
6. **All Retries Fail**: Verify graceful failure with error context

## Future Enhancements (Not Implemented)

These were considered but deemed over-engineering:

- ❌ Cryptographic hashing of outputs
- ❌ Blockchain-style audit trails
- ❌ Machine learning-based quality prediction
- ❌ Automatic prompt optimization
- ❌ Distributed retry queues

The current implementation provides practical robustness without unnecessary complexity.
