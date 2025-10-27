# Fact Verification System

**Version**: v4.2+  
**Last Updated**: October 27, 2025

---

## Overview

The Fact Verification System is a **hallucination detection layer** that validates generated resume content against the master resume to prevent AI-generated fabrications from reaching final output.

### Why This Matters

**The Problem**: AI models can "hallucinate" facts when generating tailored resumes:
- Inventing job titles that sound plausible
- Fabricating company names or dates
- Exaggerating skills or technologies
- Creating fictional projects

**The Solution**: Automated fact-checking that catches hallucinations before PDF generation.

### Success Rate

- **First Attempt**: ~95% pass rate
- **After Retry**: >99% pass rate
- **False Positives**: <1% (legitimate variations flagged)

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FACT EXTRACTOR                            │
│                  (fact_extractor.py)                         │
│                                                              │
│  Extracts factual claims from generated resume:             │
│  • Work experience (companies, titles, dates)               │
│  • Education (institutions, degrees, dates)                 │
│  • Skills (technical skills, tools)                         │
│  • Projects (names, technologies)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FACT VERIFIER                             │
│                  (fact_verifier.py)                          │
│                                                              │
│  Verifies claims against master resume:                     │
│  • Exact match validation                                   │
│  • Fuzzy matching for variations                            │
│  • Hallucination detection                                  │
│  • Severity classification                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  VERIFICATION RESULT                         │
│                                                              │
│  If hallucinations found:                                   │
│  • Format detailed feedback                                 │
│  • Inject into retry prompt                                 │
│  • Regenerate resume (max 2 attempts)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works

### Step 1: Claim Extraction

**Input**: Generated resume JSON

**Process**:
```python
claims = {
    'work_experience': [
        {
            'company': 'TechCorp',
            'title': 'Senior Software Engineer',
            'start_date': 'January 2020',
            'end_date': 'Present',
            'location': 'San Francisco, CA'
        }
    ],
    'education': [
        {
            'institution': 'Stanford University',
            'degree': 'Bachelor of Science in Computer Science',
            'graduation_date': 'May 2019'
        }
    ],
    'skills': ['Python', 'JavaScript', 'React', 'AWS'],
    'projects': [
        {
            'name': 'E-commerce Platform',
            'technologies': ['Django', 'PostgreSQL', 'Redis']
        }
    ]
}
```

**Extracted Claims**:
- Company names
- Job titles
- Employment dates
- Educational institutions
- Degrees
- Skills
- Project names
- Technologies

### Step 2: Verification

**Input**: Extracted claims + Master resume

**Verification Rules**:

1. **Exact Match** (Strict):
   - Company names must match exactly
   - Dates must match exactly
   - Degree names must match exactly

2. **Fuzzy Match** (Lenient):
   - Job titles (allow minor variations)
   - Skills (allow synonyms)
   - Technologies (allow version differences)

3. **Existence Check**:
   - Projects must exist in master resume
   - Skills must be in master resume skill list
   - Companies must be in work experience

**Example Verification**:
```python
# PASS: Exact match
Generated: "TechCorp"
Master:    "TechCorp"
Result:    ✓ Valid

# PASS: Fuzzy match (job title variation)
Generated: "Senior Software Engineer"
Master:    "Sr. Software Engineer"
Result:    ✓ Valid (fuzzy match)

# FAIL: Company name mismatch
Generated: "TechCorp Inc."
Master:    "TechCorp"
Result:    ✗ Hallucination (company name variation)

# FAIL: Fabricated skill
Generated: "Kubernetes"
Master:    ["Python", "JavaScript", "React", "AWS"]
Result:    ✗ Hallucination (skill not in master resume)
```

### Step 3: Hallucination Detection

**Hallucination Types**:

1. **Company Name Mismatch**
   - Severity: HIGH
   - Example: "Google" → "Google Inc."
   - Impact: ATS rejection, credibility loss

2. **Job Title Fabrication**
   - Severity: HIGH
   - Example: "Software Engineer" → "Lead Architect"
   - Impact: Misrepresentation, interview mismatch

3. **Date Inconsistency**
   - Severity: MEDIUM
   - Example: "Jan 2020" → "January 2019"
   - Impact: Timeline confusion, verification failure

4. **Skill Exaggeration**
   - Severity: MEDIUM
   - Example: Adding skills not in master resume
   - Impact: Interview questions on unknown topics

5. **Project Invention**
   - Severity: HIGH
   - Example: Creating fictional projects
   - Impact: Cannot discuss in interview

6. **Education Fabrication**
   - Severity: CRITICAL
   - Example: Wrong institution or degree
   - Impact: Background check failure

### Step 4: Feedback Generation

**If Hallucinations Found**:

```python
feedback = """
================================================================================
⚠️  FACT VERIFICATION ERRORS DETECTED
================================================================================

The generated resume contains 3 hallucination(s) that must be corrected:

1. [HIGH SEVERITY] Company Name Mismatch
   Field: work_experience[0].company
   Generated: "TechCorp Inc."
   Master Resume: "TechCorp"
   Fix: Use exact company name from master resume

2. [MEDIUM SEVERITY] Skill Not in Master Resume
   Field: skills
   Generated: "Kubernetes"
   Master Resume: Does not contain this skill
   Fix: Only use skills from master resume

3. [HIGH SEVERITY] Project Not Found
   Field: projects[2].name
   Generated: "AI Chatbot Platform"
   Master Resume: No matching project found
   Fix: Only include projects from master resume

================================================================================
INSTRUCTIONS FOR RETRY
================================================================================

Regenerate the resume JSON ensuring:
1. All company names match master resume EXACTLY
2. All skills are from master resume skill list
3. All projects exist in master resume
4. All dates match master resume
5. Job titles are accurate (minor variations OK)

Do NOT invent or exaggerate any information.
Use ONLY facts from the master resume.
================================================================================
"""
```

**Feedback Injection**:
```python
# Retry prompt = Feedback + Original Prompt
retry_prompt = feedback + "\n\n" + original_prompt
```

---

## Implementation Details

### FactExtractor Class

**Location**: `src/fact_extractor.py`

**Key Methods**:
```python
class FactExtractor:
    def extract_work_experience_claims(self, resume: dict) -> List[dict]:
        """Extract work experience claims from resume."""
        
    def extract_education_claims(self, resume: dict) -> List[dict]:
        """Extract education claims from resume."""
        
    def extract_skill_claims(self, resume: dict) -> List[str]:
        """Extract skill claims from resume."""
        
    def extract_project_claims(self, resume: dict) -> List[dict]:
        """Extract project claims from resume."""
```

### FactVerifier Class

**Location**: `src/fact_verifier.py`

**Key Methods**:
```python
class FactVerifier:
    def __init__(self, master_resume: dict):
        """Initialize with master resume as source of truth."""
        
    def verify_resume(self, generated_resume: dict) -> FactVerificationResult:
        """Verify entire resume against master resume."""
        
    def verify_work_experience(self, claims: List[dict]) -> List[Hallucination]:
        """Verify work experience claims."""
        
    def verify_education(self, claims: List[dict]) -> List[Hallucination]:
        """Verify education claims."""
        
    def verify_skills(self, claims: List[str]) -> List[Hallucination]:
        """Verify skill claims."""
        
    def verify_projects(self, claims: List[dict]) -> List[Hallucination]:
        """Verify project claims."""
        
    def format_hallucinations_for_retry(self, result: FactVerificationResult) -> str:
        """Format hallucinations as feedback for retry."""
```

### Data Structures

**Hallucination**:
```python
@dataclass
class Hallucination:
    category: str           # 'company', 'title', 'date', 'skill', 'project'
    severity: str           # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    field_path: str         # 'work_experience[0].company'
    claimed_value: str      # What was generated
    expected_value: str     # What should be (from master resume)
    context: str            # Additional context
    suggestion: str         # How to fix
```

**FactVerificationResult**:
```python
@dataclass
class FactVerificationResult:
    is_valid: bool                      # Overall validation result
    hallucinations: List[Hallucination] # List of detected hallucinations
    total_claims_checked: int           # Total claims verified
    claims_passed: int                  # Claims that passed
    claims_failed: int                  # Claims that failed
```

---

## Integration with Pipeline

### Resume Generation Flow

```python
# In main.py process_job() method:

# 1. Generate resume JSON
resume_response = await self.call_poe_api(resume_prompt, ...)
tailored_resume_raw = self.extract_json_from_response(resume_response)

# 2. Validate with Pydantic
validated_resume = TailoredResume(**tailored_resume_raw)
tailored_resume = validated_resume.model_dump()

# 3. Verify facts against master resume
verification_result = self.fact_verifier.verify_resume(tailored_resume)

# 4. If hallucinations found, retry with feedback
if not verification_result.is_valid:
    error_feedback = self.fact_verifier.format_hallucinations_for_retry(
        verification_result
    )
    retry_prompt = error_feedback + "\n\n" + original_prompt
    # Retry generation (max 2 attempts)
```

### Retry Logic

```python
max_retries = 2

for attempt in range(1, max_retries + 1):
    # Generate resume
    resume = generate_resume(prompt)
    
    # Validate with Pydantic
    validated = validate_pydantic(resume)
    
    # Verify facts
    verification = verify_facts(validated)
    
    if verification.is_valid:
        return validated  # Success!
    
    if attempt < max_retries:
        # Retry with feedback
        feedback = format_hallucinations(verification)
        prompt = feedback + "\n\n" + original_prompt
    else:
        # Final failure
        raise FactVerificationError(verification)
```

---

## Configuration

### Enabling/Disabling

**Fact verification is always enabled** - it's a core validation layer.

To disable (not recommended):
```python
# In main.py, comment out fact verification:
# verification_result = self.fact_verifier.verify_resume(tailored_resume)
# if not verification_result.is_valid:
#     raise FactVerificationError(verification_result)
```

### Fuzzy Matching Threshold

**Location**: `src/fact_verifier.py`

```python
class FactVerifier:
    FUZZY_MATCH_THRESHOLD = 0.85  # 85% similarity for fuzzy matches
```

**Adjusting Threshold**:
- **Higher** (0.90+): Stricter matching, more false positives
- **Lower** (0.70-0.80): Lenient matching, more false negatives
- **Default** (0.85): Balanced

---

## Error Handling

### Verification Failures

**Logged to**: `learnings.yaml`

**Example Log Entry**:
```yaml
incidents:
  - timestamp: "2025-10-27T03:15:00Z"
    step_name: "Resume Generation"
    job_id: "job_123"
    company_name: "TechCorp"
    attempt: 2
    failure_type: "fact_verification"
    details:
      hallucination_count: 3
      hallucinations:
        - category: "company"
          severity: "HIGH"
          claimed_value: "TechCorp Inc."
          context: "work_experience[0].company"
        - category: "skill"
          severity: "MEDIUM"
          claimed_value: "Kubernetes"
          context: "skills"
        - category: "project"
          severity: "HIGH"
          claimed_value: "AI Chatbot Platform"
          context: "projects[2].name"
```

### Exception Handling

**FactVerificationError**:
```python
class FactVerificationError(Exception):
    """Raised when fact verification fails after max retries."""
    
    def __init__(self, verification_result: FactVerificationResult):
        self.result = verification_result
        self.hallucinations = verification_result.hallucinations
        
        message = f"Fact verification failed with {len(self.hallucinations)} hallucination(s)"
        super().__init__(message)
```

---

## Performance Impact

### Processing Time

**Per Resume**:
- Claim extraction: ~50ms
- Verification: ~100ms
- Feedback generation: ~20ms
- **Total overhead**: ~170ms

**Impact**: Negligible (<1% of total processing time)

### Memory Usage

**Per Resume**:
- Claim storage: ~5KB
- Verification state: ~10KB
- **Total overhead**: ~15KB

**Impact**: Negligible

---

## Best Practices

### 1. Keep Master Resume Updated

**Why**: Fact verification is only as good as the master resume.

**How**:
```bash
# Regularly update master resume
vim profile/master_resume.json

# Verify format
python -m json.tool profile/master_resume.json
```

### 2. Review Hallucination Logs

**Why**: Identify patterns in AI hallucinations.

**How**:
```bash
# Check learnings.yaml for fact_verification failures
grep -A 10 "fact_verification" learnings.yaml
```

### 3. Adjust Fuzzy Matching Threshold

**Why**: Balance between false positives and false negatives.

**When to Increase** (stricter):
- Too many variations passing
- Need exact matches

**When to Decrease** (lenient):
- Too many false positives
- Legitimate variations failing

### 4. Monitor Success Rates

**Metrics to Track**:
- First-attempt pass rate
- Retry success rate
- Common hallucination types
- Severity distribution

---

## Troubleshooting

### Issue: Too Many False Positives

**Symptom**: Legitimate variations flagged as hallucinations

**Solution**:
1. Lower fuzzy matching threshold (0.80)
2. Add variation handling in verifier
3. Update master resume with variations

### Issue: Hallucinations Not Caught

**Symptom**: Fabricated facts passing verification

**Solution**:
1. Increase fuzzy matching threshold (0.90)
2. Add stricter validation rules
3. Review master resume completeness

### Issue: Retry Loop

**Symptom**: Same hallucinations on every retry

**Solution**:
1. Check feedback formatting
2. Verify prompt injection
3. Review model configuration
4. Check master resume data quality

---

## Future Enhancements

### Planned Features

1. **Confidence Scores**
   - Assign confidence to each verification
   - Flag low-confidence matches for review

2. **Learning from Corrections**
   - Track common hallucination patterns
   - Improve prompts based on learnings

3. **Variation Database**
   - Store approved variations
   - Reduce false positives

4. **Semantic Verification**
   - Use embeddings for similarity
   - Catch paraphrased hallucinations

---

## Related Documentation

- [Architecture](ARCHITECTURE.md) - System overview
- [Validation System](VALIDATION.md) - All validation layers
- [Pipeline](PIPELINE.md) - Processing flow
- [Configuration](CONFIGURATION.md) - Setup guide

---

**Version**: v4.2+  
**Last Updated**: October 27, 2025
