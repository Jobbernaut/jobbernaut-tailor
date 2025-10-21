# Anti-Fragile Pipeline Architecture

## Overview

The Jobbernaut pipeline has been enhanced with robust validation, self-healing retry logic, and deterministic error handling to ensure reliable operation without over-engineering.

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

**Purpose**: Ensures intelligence outputs meet quality thresholds

**Quality Thresholds**:

#### JobResonanceAnalysis
- `emotional_keywords`: 3-15 items, no empty strings
- `cultural_values`: 2+ items, no empty strings
- `hidden_requirements`: 2+ items, no empty strings
- `power_verbs`: 3+ items, no empty strings
- `technical_keywords`: 3+ items, no empty strings

#### CompanyResearch
- `mission_statement`: 20+ characters
- `core_values`: 2-10 items, no empty strings
- `tech_stack`: No empty strings
- `culture_keywords`: No empty strings

#### StorytellingArc
- `hook`: 50+ characters
- `bridge`: 50+ characters
- `vision`: 50+ characters
- `call_to_action`: 20+ characters
- `proof_points`: 2-3 items, each 30+ characters

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

### 5. Pipeline Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. VALIDATE JOB INPUTS                                      │
│    - Check job_id, job_title, company_name, job_description│
│    - Fail fast if invalid                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. INTELLIGENCE GATHERING PHASE                             │
│                                                             │
│    Step 1: Job Resonance Analysis (with retry)             │
│    ├─ Attempt 1: Base prompt                               │
│    ├─ Attempt 2: + JSON error feedback (if needed)         │
│    ├─ Attempt 3: + Pydantic/quality feedback (if needed)   │
│    └─ Validate: Pydantic + Quality thresholds              │
│                                                             │
│    Step 2: Company Research (with retry)                   │
│    ├─ Attempt 1: Base prompt                               │
│    ├─ Attempt 2: + JSON error feedback (if needed)         │
│    ├─ Attempt 3: + Pydantic/quality feedback (if needed)   │
│    └─ Validate: Pydantic + Quality thresholds              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. RESUME GENERATION (with retry)                           │
│    - Inject job resonance analysis                          │
│    - 3 retry attempts with Pydantic validation              │
│    - Progressive error feedback on failures                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. STORYTELLING ARC GENERATION (with retry)                 │
│    - Uses resume + company research + job resonance         │
│    - 3 retry attempts with validation                       │
│    - Progressive error feedback on failures                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. COVER LETTER GENERATION                                  │
│    - Inject storytelling arc + company research + resonance │
│    - Single attempt (text output, no validation needed)     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. LATEX RENDERING & PDF COMPILATION                        │
│    - Resume LaTeX → PDF                                     │
│    - Cover Letter LaTeX → PDF                               │
│    - Referral versions                                      │
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

## Validation Layers

```
Layer 1: Input Validation
├─ Type checking (string, int, etc.)
├─ Length constraints
└─ Required field presence

Layer 2: Pydantic Schema Validation
├─ Field types match schema
├─ Required fields present
└─ Nested object structure correct

Layer 3: Quality Threshold Validation
├─ Minimum content length
├─ Array size constraints
└─ No empty strings in arrays
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
