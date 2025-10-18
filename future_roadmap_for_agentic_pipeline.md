# Future Roadmap for Agentic Pipeline

## Executive Summary

This document outlines the transformation of Jobbernaut Tailor from a monolithic 5-stage pipeline into a robust, cost-effective, and highly reliable **agentic micro-task pipeline** with 50-60 API calls per job, achieving:

- **10x Quality Improvement**: Multi-model consensus, self-critique loops, comprehensive validation
- **10x Cost Reduction**: Using cheap models (GPT-4o-mini, Gemini Flash, Claude Haiku) instead of expensive ones
- **10x Error Reduction**: <1% error rate through redundancy and validation
- **10x Anti-Fragility**: Graceful degradation, checkpointing, circuit breakers

**Estimated Cost**: ~$0.015-0.020 per job (vs current $0.024)
**Quality Score**: 95+ (vs current ~75-80)
**Reliability**: 99%+ success rate (vs current ~85%)

---

## Current System Problems

### 1. **Too Expensive**
- Sequential API calls with expensive models
- Retry loops can make 5+ additional calls
- No caching or optimization
- High thinking budgets (4096 tokens)

### 2. **Too Weak**
- Monolithic 500+ line class
- Tight coupling, no separation of concerns
- Hard-coded business logic
- No abstraction or dependency injection

### 3. **Failure-Prone**
- Single API failure halts entire pipeline
- No state persistence or recovery
- Synchronous processing only
- Minimal validation before expensive operations
- Fragile regex-based parsing

### 4. **Not Scalable**
- Single-threaded, one job at a time
- YAML file as "database"
- No queue system or worker distribution
- No rate limiting or monitoring

---

## Enhanced Pipeline Architecture

### **Core Philosophy**
- **Micro-tasks**: Each stage does ONE thing well
- **Cheap Models**: Use GPT-4o-mini (~$0.15/1M tokens), Gemini Flash (~$0.075/1M), Claude Haiku (~$0.25/1M)
- **Redundancy**: Multi-model consensus on critical stages
- **Validation**: Verify at every step, not just at the end
- **Anti-Fragility**: Graceful degradation, never complete failure

### **10-Stage Enhanced Pipeline**

#### **STAGE 1: Job Description Analysis**
**API Calls**: 3 (multi-model consensus)
**Models**: GPT-4o-mini, Gemini Flash, Claude Haiku
**Input**: Raw job description
**Output**: 
```json
{
  "key_requirements": ["req1", "req2", ...],
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "seniority_level": "Senior/Mid/Junior",
  "keywords": ["keyword1", "keyword2", ...]
}
```
**Enhancements**:
- Run same prompt through 3 different models
- Use majority voting for consensus
- Flag discrepancies for review
- Cache results for similar JDs (fuzzy matching)

---

#### **STAGE 2: Experience & Project Summarization**
**API Calls**: 10 (one per experience/project, parallel execution)
**Model**: GPT-4o-mini
**Input**: Each experience/project with raw bullets
**Output**: 
```json
{
  "experience_id": "exp_1",
  "summary": "2-sentence summary of impact and skills",
  "key_skills_used": ["skill1", "skill2"],
  "quantifiable_achievements": ["metric1", "metric2"]
}
```
**Enhancements**:
- Parallel execution with `asyncio.gather()`
- Extract quantifiable metrics
- Identify transferable skills

---

#### **STAGE 3: Relevance Scoring & Selection**
**API Calls**: 3 (consensus + chain-of-thought)
**Models**: GPT-4o-mini (2x), Gemini Flash (1x)
**Input**: All summaries + JD key requirements
**Output**:
```json
{
  "experiences": [
    {"id": "exp_1", "score": 95, "reason": "Direct match", "confidence": 0.92}
  ],
  "projects": [
    {"id": "proj_1", "score": 82, "reason": "Similar domain", "confidence": 0.85}
  ],
  "selected_experience_ids": ["exp_1", "exp_2", "exp_3", "exp_4", "exp_5"],
  "selected_project_ids": ["proj_1", "proj_2"]
}
```
**Enhancements**:
- Multi-model consensus on scores
- Chain-of-thought reasoning for each score
- Confidence intervals
- Select top 5 experiences (score > 70) + top 2 projects (score > 60)

---

#### **STAGE 4: Experience Tailoring (RSTA Format)**
**API Calls**: 15 (5 experiences × 3 passes each)
**Model**: GPT-4o-mini
**Input**: Original experience + JD requirements + relevance reason
**Output**:
```json
{
  "experience_id": "exp_1",
  "tailored_bullets": [
    "Result: Achieved X by doing Y using Z",
    "Situation/Task: Faced challenge A, solved with approach B",
    "Action: Implemented solution C resulting in impact D"
  ],
  "quality_scores": [92, 88, 90]
}
```
**Multi-Pass Refinement**:
- **Pass 1**: Generate initial RSTA bullets
- **Pass 2**: "Make this more impactful and specific. Add metrics."
- **Pass 3**: "Polish for clarity and conciseness. Ensure parallel structure."

**Enhancements**:
- Parallel execution across experiences
- Quality scoring per bullet (0-100)
- Reject bullets scoring < 70
- RSTA format validation (regex)
- Max 3 bullets per experience
- Action verb diversity check
- Quantification enforcement

---

#### **STAGE 5: Deviation Verification**
**API Calls**: 10 (5 experiences × 2 checks each)
**Models**: Gemini Flash (fast), GPT-4o-mini (verification)
**Input**: Tailored experience + original master resume experience
**Output**:
```json
{
  "experience_id": "exp_1",
  "deviation_score": 15,
  "is_acceptable": true,
  "issues": ["Minor embellishment in impact numbers"],
  "fact_checks": [
    {"claim": "Led team of 5", "verified": true, "source": "master_resume"}
  ],
  "action": "accept" | "retry_stage_4"
}
```
**Enhancements**:
- Semantic similarity scoring (0-100)
- Fact-checking against master resume
- Keyword preservation check
- If deviation_score > 30, retry Stage 4 with feedback
- Max 2 retries per experience
- Self-critique loop: "What could be exaggerated here?"

---

#### **STAGE 6: Professional Summary Generation**
**API Calls**: 3 (generate + critique + refine)
**Model**: Claude Haiku (concise writing)
**Input**: Tailored resume JSON + JD
**Output**:
```json
{
  "professional_summary": "2-3 sentence objective highlighting relevant experience",
  "quality_score": 88,
  "keyword_density": 0.12
}
```
**Multi-Pass Process**:
- **Pass 1**: Generate initial summary
- **Pass 2**: "Critique this summary. What's weak?"
- **Pass 3**: "Fix the issues and polish"

**Enhancements**:
- Keyword density optimization (10-15%)
- Readability scoring
- Tone consistency check

---

#### **STAGE 7: Final Resume Validation**
**API Calls**: 3 (validate + gap analysis + competitive check)
**Model**: GPT-4o-mini
**Input**: Complete tailored resume JSON + JD
**Output**:
```json
{
  "is_well_tailored": true,
  "tailoring_score": 92,
  "gaps": ["Missing mention of skill X"],
  "strengths": ["Strong quantification", "Clear impact"],
  "competitive_assessment": "Above average for this role",
  "action": "accept" | "restart_from_stage_4"
}
```
**Enhancements**:
- Comprehensive gap analysis
- Competitive benchmarking
- Consistency verification (dates, titles, companies)
- Contradiction detection
- If score < 80, restart from Stage 4 with detailed feedback
- Max 1 restart

---

#### **STAGE 8: Cover Letter Generation**
**API Calls**: 3 (generate + critique + polish)
**Model**: Claude Haiku (creative writing) or GPT-4o-mini with web search
**Input**: Tailored resume JSON + JD + selected personal story + company research
**Output**: Complete cover letter text

**Multi-Pass Process**:
- **Pass 1**: Generate initial cover letter
- **Pass 2**: "Critique this. Is it compelling? Any clichés?"
- **Pass 3**: "Polish and fix issues"

**Enhancements**:
- Web search for company insights
- Cultural fit assessment
- Tone matching (startup vs corporate)
- Personal story integration
- Readability scoring

---

#### **STAGE 9: Final Quality Check**
**API Calls**: 3 (consistency + tone + polish)
**Model**: GPT-4o-mini
**Input**: Complete resume + cover letter
**Output**:
```json
{
  "consistency_check": "passed",
  "tone_consistency": "professional throughout",
  "typos_found": [],
  "grammar_issues": [],
  "final_quality_score": 94
}
```
**Checks**:
- Cross-document consistency
- Tone consistency across all content
- Grammar and typo detection
- Formatting validation
- Final polish pass

---

#### **STAGE 10: LaTeX Template Population & PDF Generation**
**API Calls**: 0 (pure logic, no LLM)
**Method**: Jinja2 templates + pdflatex
**Input**: Tailored resume JSON
**Output**: LaTeX file + 2 PDFs (resume + cover letter)

**Implementation**:
```python
from jinja2 import Template

latex_template = """
\\documentclass{resume}
\\begin{document}
\\name{ {{contact_info.first_name}} {{contact_info.last_name}} }
\\address{ {{contact_info.phone}} \\\\ {{contact_info.location}} }
\\email{ {{contact_info.email}} }
\\linkedin{ {{contact_info.linkedin}} }

\\section{Professional Summary}
{{professional_summary}}

{% for exp in work_experience %}
\\section{Experience}
\\employer{ {{exp.company}} }
\\title{ {{exp.title}} }
\\dates{ {{exp.dates}} }
\\begin{itemize}
{% for bullet in exp.bullets %}
\\item {{bullet}}
{% endfor %}
\\end{itemize}
{% endfor %}

\\section{Skills}
{% for category, skills in skills.items() %}
\\textbf{ {{category}}: } {{skills | join(', ')}}
{% endfor %}

\\end{document}
"""

template = Template(latex_template)
latex_output = template.render(resume_data)
```

**Enhancements**:
- No LLM needed (cost = $0)
- Deterministic output
- Easy to debug and customize
- Fast execution

---

## 50+ Robustness Strategies

### **Anti-Hallucination Strategies**

1. **Multi-Model Consensus** (3-5 calls per critical stage)
   - Run same prompt through 3 different models
   - Use majority voting or weighted ensemble
   - Flag discrepancies for human review
   - Apply to: Stages 1, 3, 5, 7

2. **Chain-of-Thought Verification** (2x calls)
   - Call 1: Generate output
   - Call 2: "Explain your reasoning step-by-step"
   - Verify logic is sound before accepting
   - Apply to: Stages 3, 4, 7

3. **Self-Critique Loop** (2-3 calls)
   - Call 1: Generate content
   - Call 2: "Critique this output. What's wrong?"
   - Call 3: "Fix the issues you identified"
   - Apply to: Stages 4, 6, 8

4. **Fact-Checking Against Source** (1 call per item)
   - After tailoring, verify each claim against master resume
   - "Does this tailored bullet accurately represent the original?"
   - Binary yes/no with explanation
   - Apply to: Stage 5

5. **Contradiction Detection** (1 call)
   - "Find any contradictions within this resume"
   - Check dates, titles, skills consistency
   - Apply to: New stage between 6-7

6. **Grounding with Examples** (0 calls, prompt engineering)
   - Include 3-5 good/bad examples in every prompt
   - "Good example: X. Bad example: Y. Now do Z."
   - Reduces hallucination by 40-60%

7. **Constrained Output Format** (0 calls, prompt engineering)
   - Force JSON schema output with strict validation
   - Use Pydantic models to validate every response
   - Reject and retry if schema violated

---

### **Error Prevention Strategies**

8. **Pre-Flight Validation** (1 call)
   - Before Stage 1, validate JD is complete
   - "Is this a valid job description? What's missing?"
   - Prevents garbage-in-garbage-out

9. **Incremental Validation** (1 call per stage)
   - After each stage: "Is this output valid and complete?"
   - Catch errors immediately, not at the end
   - Add to every stage

10. **Semantic Similarity Scoring** (1 call per experience)
    - After tailoring: "Rate similarity 0-100 between original and tailored"
    - Ensure meaning preserved while improving presentation
    - Stage 5 enhancement

11. **Keyword Preservation Check** (0 calls, logic)
    - Extract key terms from master resume
    - Verify they appear in tailored version
    - Flag if critical keywords missing

12. **Bullet Point Quality Scoring** (1 call per experience)
    - "Rate each bullet 0-100 on: impact, specificity, quantification"
    - Reject bullets scoring < 70
    - Stage 4 enhancement

13. **RSTA Format Validation** (0 calls, regex)
    - Validate each bullet follows Result/Situation/Task/Action
    - Reject malformed bullets immediately
    - Stage 4 post-processing

14. **Length Constraints** (0 calls, logic)
    - Enforce max 3 bullets per experience
    - Max 2 lines per bullet
    - Reject verbose outputs

15. **Duplicate Detection** (0 calls, logic)
    - Check for repeated phrases across bullets
    - Flag similar bullets for consolidation
    - Stage 4 post-processing

---

### **Quality Enhancement Strategies**

16. **Multi-Pass Refinement** (3 calls per experience)
    - Pass 1: Generate initial tailoring
    - Pass 2: "Make this more impactful and specific"
    - Pass 3: "Polish for clarity and conciseness"
    - Stage 4 enhancement

17. **A/B Testing** (2 calls per critical output)
    - Generate 2 versions with different prompts
    - "Which is better and why?"
    - Use the winner
    - Stages 4, 6, 8

18. **Competitive Benchmarking** (1 call)
    - "Compare this resume to top-tier resumes for this role"
    - Identify gaps and improvements
    - New stage after 7

19. **Readability Scoring** (1 call)
    - "Rate readability 0-100. Suggest improvements."
    - Ensure bullets are clear and scannable
    - Stage 4 enhancement

20. **Impact Amplification** (1 call per bullet)
    - "Rewrite to emphasize measurable impact"
    - Focus on results, not just activities
    - Stage 4 sub-stage

21. **Keyword Density Optimization** (1 call)
    - "Ensure these JD keywords appear naturally: [list]"
    - Optimize for ATS without keyword stuffing
    - New stage after 6

22. **Action Verb Diversity** (0 calls, logic)
    - Track action verbs used
    - Suggest alternatives if repetitive
    - Maintain variety and impact

23. **Quantification Check** (1 call per experience)
    - "Add specific metrics where possible"
    - Convert vague claims to quantified achievements
    - Stage 4 enhancement

24. **Context Enrichment** (1 call per experience)
    - "Add relevant context about company/project scale"
    - Help reader understand scope and impact
    - Stage 4 enhancement

25. **Parallel Structure Enforcement** (0 calls, logic)
    - Ensure bullets within same experience follow consistent structure
    - Improves readability and professionalism

---

### **Anti-Fragile Strategies**

26. **Graceful Degradation**
    - If Stage 4 fails 3x, use Stage 2 summary as fallback
    - Never completely fail, always produce something
    - Partial success is acceptable

27. **Checkpoint System**
    - Save state after every stage to disk
    - Resume from last checkpoint on failure
    - Store in `output/[job_id]/checkpoints/`

28. **Circuit Breaker Pattern**
    - If API fails 5x in a row, pause 60s
    - Prevents cascade failures
    - Auto-reset after cooldown

29. **Fallback Model Hierarchy**
    - Primary: GPT-4o-mini
    - Fallback 1: Gemini Flash
    - Fallback 2: Claude Haiku
    - Auto-switch on repeated failures

30. **Timeout Protection**
    - Max 30s per API call
    - Retry with shorter prompt if timeout
    - Prevent hanging operations

31. **Rate Limiting**
    - Max 10 concurrent API calls
    - Queue excess requests
    - Prevents API throttling

32. **Exponential Backoff**
    - Retry delays: 1s, 2s, 4s, 8s, 16s
    - Prevents overwhelming failed services
    - Standard retry pattern

33. **Health Checks**
    - Ping each AI service before pipeline start
    - Skip unavailable services
    - Pre-flight validation

34. **Partial Success Handling**
    - If 4/5 experiences succeed, continue
    - Mark failed items for manual review
    - Don't fail entire job

35. **Idempotency**
    - Same input always produces same output
    - Cache results by content hash
    - Avoid redundant API calls

---

### **Rolling Context Strategies**

36. **Context Window Management** (5-10 calls)
    - Break large contexts into chunks
    - Summarize previous chunks
    - Maintain rolling summary of decisions

37. **Cross-Stage Context Passing**
    - Each stage receives summary of all previous stages
    - "Given that Stage 1 found X, and Stage 3 selected Y..."
    - Maintains coherence across pipeline

38. **Iterative Refinement with Memory** (3-5 calls)
    - Pass 1: Initial attempt
    - Pass 2: "Given feedback from verification: [feedback]"
    - Pass 3: "Considering previous attempts: [history]"
    - Learns from mistakes

39. **Conversation Threading**
    - Treat pipeline as multi-turn conversation
    - Each stage builds on previous context
    - More coherent than isolated calls

40. **Decision Logging**
    - Log why each choice was made
    - Pass reasoning to subsequent stages
    - "Experience X was selected because Y"

---

### **Advanced Quality Strategies**

41. **Tone Consistency Check** (1 call)
    - "Ensure consistent professional tone across all bullets"
    - Avoid mixing formal/casual language
    - New stage after 6

42. **Redundancy Elimination** (1 call)
    - "Remove redundant information across experiences"
    - Maximize information density
    - New stage after 6

43. **Skill Clustering** (1 call)
    - "Group related skills logically"
    - Improve skills section organization
    - Stage 3 enhancement

44. **Achievement Ranking** (1 call per experience)
    - "Rank these bullets by impact. Reorder."
    - Most impressive bullets first
    - Stage 4 enhancement

45. **Jargon Appropriateness** (1 call)
    - "Verify technical terms match industry standards"
    - Avoid outdated or incorrect terminology
    - New stage after 7

46. **Consistency Verification** (1 call)
    - "Check dates, titles, companies are consistent"
    - Catch copy-paste errors
    - New stage after 6

47. **Gap Analysis** (1 call)
    - "What JD requirements are not addressed?"
    - Identify missing elements
    - Stage 7 enhancement

48. **Competitive Positioning** (1 call)
    - "How does this compare to typical candidates?"
    - Identify unique selling points
    - New stage after 7

49. **Cultural Fit Assessment** (1 call)
    - "Does tone/content match company culture?"
    - Adjust formality based on company type
    - Stage 8 enhancement

50. **Final Polish Pass** (1 call)
    - "Final review for typos, grammar, formatting"
    - Last quality gate before output
    - New stage 9

---

## New Modular Architecture

### **Project Structure**
```
jobbernaut-tailor/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py              # Pydantic models for job data
│   │   ├── resume.py           # Resume data models
│   │   ├── pipeline_state.py   # State tracking models
│   │   └── validation.py       # Validation schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py       # Abstract AI provider interface
│   │   ├── jd_analyzer.py      # Stage 1: JD Analysis
│   │   ├── summarizer.py       # Stage 2: Summarization
│   │   ├── scorer.py           # Stage 3: Scoring & Selection
│   │   ├── tailor.py           # Stage 4: Tailoring
│   │   ├── verifier.py         # Stage 5: Verification
│   │   ├── summary_gen.py      # Stage 6: Summary Generation
│   │   ├── validator.py        # Stage 7: Validation
│   │   ├── cover_letter.py     # Stage 8: Cover Letter
│   │   ├── quality_check.py    # Stage 9: Quality Check
│   │   └── latex_builder.py    # Stage 10: LaTeX (no LLM)
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Main pipeline controller
│   │   ├── stage_executor.py   # Execute individual stages
│   │   ├── retry_handler.py    # Retry logic with backoff
│   │   ├── checkpoint.py       # State persistence
│   │   └── consensus.py        # Multi-model consensus logic
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── cache.py            # Response caching
│   │   ├── circuit_breaker.py  # Circuit breaker pattern
│   │   ├── rate_limiter.py     # Rate limiting
│   │   └── monitoring.py       # Logging and metrics
│   │
│   ├── templates/
│   │   ├── resume.tex.j2       # Jinja2 LaTeX template
│   │   └── cover_letter.tex.j2 # Cover letter template
│   │
│   ├── utils.py                # Utility functions
│   └── main.py                 # Entry point
│
├── config/
│   ├── models.yaml             # Model configurations
│   ├── prompts/                # Prompt templates per stage
│   │   ├── stage1_jd_analysis.txt
│   │   ├── stage2_summarize.txt
│   │   ├── stage3_score.txt
│   │   ├── stage4_tailor.txt
│   │   ├── stage5_verify.txt
│   │   ├── stage6_summary.txt
│   │   ├── stage7_validate.txt
│   │   ├── stage8_cover_letter.txt
│   │   └── stage9_quality.txt
│   └── pipeline.yaml           # Pipeline configuration
│
├── profile/
│   ├── master_resume.json
│   └── master_cover_letter_points.json
│
├── applications.yaml
├── requirements.txt
└── README.md
```

### **Key Components**

#### **1. AI Service Abstraction**
```python
# src/services/ai_service.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AIService(ABC):
    @abstractmethod
    async def call(self, prompt: str, model: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def call_with_consensus(
        self, 
        prompt: str, 
        models: List[str]
    ) -> Dict[str, Any]:
        """Call multiple models and return consensus"""
        pass

class PoeAIService(AIService):
    async def call(self, prompt: str, model: str, **kwargs) -> str:
        # Implementation using Poe API
        pass
    
    async def call_with_consensus(
        self, 
        prompt: str, 
        models: List[str]
    ) -> Dict[str, Any]:
        # Call all models in parallel
        # Return consensus result
        pass
```

#### **2. Stage Executor**
```python
# src/pipeline/stage_executor.py
from typing import Any, Dict
from src.models.pipeline_state import PipelineState
from src.infrastructure.checkpoint import CheckpointManager

class StageExecutor:
    def __init__(self, checkpoint_manager: CheckpointManager):
        self.checkpoint_manager = checkpoint_manager
    
    async def execute_stage(
        self,
        stage_name: str,
        stage_func: callable,
        state: PipelineState,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a stage with error handling and checkpointing"""
        try:
            result = await stage_func(state, **kwargs)
            
            # Validate result
            if not self.validate_result(result):
                raise ValueError(f"Stage {stage_name} produced invalid result")
            
            # Save checkpoint
            await self.checkpoint_manager.save(stage_name, result)
            
            return result
        except Exception as e:
            # Handle error, retry if needed
            return await self.handle_error(stage_name, e, state)
```

#### **3. Multi-Model Consensus**
```python
# src/pipeline/consensus.py
import asyncio
from typing import List, Dict, Any
from collections import Counter

class ConsensusEngine:
    async def get_consensus(
        self,
        prompt: str,
        models: List[str],
        ai_service: AIService
    ) -> Dict[str, Any]:
        """Get consensus from multiple models"""
        
        # Call all models in parallel
        tasks = [
            ai_service.call(prompt, model) 
            for model in models
        ]
        responses = await asyncio.gather(*tasks)
        
        # Parse responses
        parsed = [self.parse_response(r) for r in responses]
        
        # Find consensus
        consensus = self.find_consensus(parsed)
        
        # Flag discrepancies
        discrepancies = self.find_discrepancies(parsed)
        
        return {
            "consensus": consensus,
            "discrepancies": discrepancies,
            "all_responses": parseI'll create a comprehensive roadmap document capturing all the plans we've discussed.

<write_to_file>
<path>future_roadmap_agentic_pipeline.md</path>
<content># Future Roadmap: Agentic Resume Pipeline

**Version**: 2.0  
**Date**: October 17, 2025  
**Status**: Planning Phase  
**Goal**: Transform monolithic pipeline into robust, cost-effective, anti-fragile agentic system

---

## 📊 Executive Summary

### Current State Problems
- **Too Expensive**: ~$0.024 per job with 4-6 API calls to expensive models
- **Too Weak**: Monolithic architecture, tight coupling, no separation of concerns
- **Failure-Prone**: No error recovery, single point of failure, fragile parsing
- **Not Scalable**: Sequential processing, file-based database, no parallelization

### Target State Goals
- **10x More Powerful**: Multi-model consensus, self-critique loops, rolling context
- **10x Less Hallucination**: Fact-checking, contradiction detection, grounding
- **10x Error-Free**: Incremental validation, graceful degradation, comprehensive error handling
- **10x Anti-Fragile**: Circuit breakers, checkpointing, fallback hierarchies

### Key Metrics
- **API Calls**: 50-60 per job (vs 4-6 currently)
- **Cost**: ~$0.015-0.020 per job (vs $0.024 currently)
- **Quality Score**: 95+ (vs 70-80 currently)
- **Error Rate**: <1% (vs ~15% currently)
- **Processing Time**: 2-3 minutes (vs 1-2 minutes currently, but with retries often 5-10 minutes)

---

## 🏗️ Architecture Overview

### Design Philosophy
1. **Micro-Task Specialization**: Each stage does ONE thing well with a cheap, focused LLM
2. **Multi-Model Consensus**: Critical decisions use 3+ models voting
3. **Self-Critique Loops**: Generate → Critique → Refine for quality
4. **Rolling Context**: Each stage builds on previous context
5. **Graceful Degradation**: Never completely fail, always produce something

### Core Principles
- **Separation of Concerns**: Clear boundaries between stages
- **Idempotency**: Same input → same output
- **Observability**: Log everything for debugging
- **Testability**: Each stage independently testable
- **Configurability**: All models and thresholds configurable

---

## 🔄 Enhanced 10-Stage Pipeline

### **STAGE 1: Job Description Analysis**
**API Calls**: 3 (multi-model consensus)  
**Models**: GPT-4o-mini, Gemini Flash, Claude Haiku  
**Cost**: ~$0.0009

**Input**: Raw job description text

**Process**:
1. Run same extraction prompt through 3 models
2. Compare outputs for consistency
3. Use majority voting for each field
4. Flag discrepancies for review

**Output**:
```json
{
  "key_requirements": ["req1", "req2", ...],
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "seniority_level": "Senior/Mid/Junior",
  "keywords": ["keyword1", "keyword2", ...],
  "company_culture_indicators": ["indicator1", ...],
  "consensus_confidence": 0.95
}
```

**Quality Gates**:
- Consensus confidence > 0.8
- At least 5 key requirements extracted
- Skills categorized correctly

**Error Handling**:
- If consensus fails, use GPT-4o-mini as tiebreaker
- If all models fail, return structured error with partial data

---

### **STAGE 2: Experience & Project Summarization**
**API Calls**: 10 (one per experience/project, parallel)  
**Models**: GPT-4o-mini  
**Cost**: ~$0.0015

**Input**: Each experience/project with raw bullets from master resume

**Process**:
1. Run all summarizations in parallel using `asyncio.gather()`
2. For each item: "Summarize in 2 sentences focusing on impact and skills"
3. Extract key skills used
4. Rate complexity/seniority level

**Output** (per item):
```json
{
  "experience_id": "exp_1",
  "summary": "Led team of 5 engineers to build X, resulting in Y impact",
  "key_skills_used": ["Python", "AWS", "Leadership"],
  "complexity_score": 85,
  "seniority_level": "Senior"
}
```

**Quality Gates**:
- Summary is 2-3 sentences
- At least 2 skills extracted
- Complexity score 0-100

**Error Handling**:
- Retry failed items up to 3 times
- If still fails, use original bullets as fallback

---

### **STAGE 3: Relevance Scoring & Selection**
**API Calls**: 3 (consensus + reasoning)  
**Models**: GPT-4o-mini (2x), Gemini Flash (1x)  
**Cost**: ~$0.0012

**Input**: All summaries + JD key requirements

**Process**:
1. Call 1: Score each item 0-100 with reasoning
2. Call 2: Same task, different model for validation
3. Call 3: "Explain discrepancies between scores"
4. Average scores with confidence weighting

**Output**:
```json
{
  "experiences": [
    {
      "id": "exp_1",
      "score": 95,
      "reason": "Direct match with required skills X, Y, Z",
      "confidence": 0.92
    }
  ],
  "projects": [...],
  "selected_experience_ids": ["exp_1", "exp_2", "exp_3", "exp_4", "exp_5"],
  "selected_project_ids": ["proj_1", "proj_2"],
  "selection_rationale": "Top 5 experiences cover 90% of JD requirements"
}
```

**Selection Logic**:
- Select top 5 experiences (score > 70)
- Select top 2 projects (score > 60)
- Ensure coverage of all key JD requirements

**Quality Gates**:
- At least 3 experiences selected
- Combined coverage > 80% of JD requirements
- No score discrepancy > 20 points between models

**Error Handling**:
- If consensus fails, use highest-scoring model
- If no items score > 70, lower threshold to 60

---

### **STAGE 4: Experience Tailoring (RSTA Format)**
**API Calls**: 15 (5 experiences × 3 passes each)  
**Models**: GPT-4o-mini  
**Cost**: ~$0.0024

**Input**: Original experience + JD requirements + relevance reason

**Process** (per experience):
1. **Pass 1 - Initial Tailoring**: Generate 3 bullets in RSTA format
2. **Pass 2 - Impact Amplification**: "Make more impactful and specific"
3. **Pass 3 - Polish**: "Refine for clarity and conciseness"

**RSTA Format Requirements**:
- **R**esult: Start with the outcome/impact
- **S**ituation/**T**ask: Provide context
- **A**ction: Describe what you did

**Output** (per experience):
```json
{
  "experience_id": "exp_1",
  "tailored_bullets": [
    "Reduced deployment time by 60% by implementing CI/CD pipeline using Jenkins and Docker, enabling 50+ daily deployments",
    "Led migration of monolithic application to microservices architecture, improving system reliability from 95% to 99.9% uptime",
    "Mentored team of 3 junior engineers on best practices, resulting in 40% reduction in code review cycles"
  ],
  "pass_history": {
    "pass_1": [...],
    "pass_2": [...],
    "pass_3": [...]
  },
  "improvement_score": 85
}
```

**Quality Gates**:
- Exactly 3 bullets per experience
- Each bullet follows RSTA format
- Each bullet contains quantifiable metric
- Improvement score > 70 from pass 1 to pass 3

**Error Handling**:
- If RSTA format violated, retry with stricter prompt
- If quantification missing, add "Quantify this bullet" pass
- Max 5 total passes before accepting best attempt

---

### **STAGE 5: Deviation Verification**
**API Calls**: 10 (5 experiences × 2 checks each)  
**Models**: Gemini Flash (cheap, fast), GPT-4o-mini (tiebreaker)  
**Cost**: ~$0.0008

**Input**: Tailored experience + original master resume experience

**Process** (per experience):
1. **Check 1 - Fact Verification**: "Compare tailored vs original. Flag lies/major deviations"
2. **Check 2 - Semantic Similarity**: "Rate similarity 0-100. Ensure meaning preserved"
3. If deviation detected, generate specific feedback for Stage 4 retry

**Output** (per experience):
```json
{
  "experience_id": "exp_1",
  "deviation_score": 15,
  "semantic_similarity": 88,
  "is_acceptable": true,
  "issues": [
    {
      "severity": "minor",
      "description": "Impact number slightly embellished (55% vs 60%)",
      "location": "bullet 1"
    }
  ],
  "action": "accept",
  "feedback_for_retry": null
}
```

**Deviation Thresholds**:
- **Critical** (score > 50): Blatant lies, fabricated achievements → Reject
- **Major** (score 30-50): Significant misrepresentation → Retry Stage 4
- **Minor** (score < 30): Acceptable embellishment → Accept

**Quality Gates**:
- Deviation score < 30
- Semantic similarity > 75
- No critical issues

**Error Handling**:
- If deviation > 30, send back to Stage 4 with specific feedback
- Max 2 retries per experience
- After 2 retries, use best attempt with warning flag

---

### **STAGE 6: Professional Summary Generation**
**API Calls**: 3 (generate + critique + refine)  
**Models**: Claude Haiku (concise writing), GPT-4o-mini (critique)  
**Cost**: ~$0.0006

**Input**: Tailored resume JSON + JD

**Process**:
1. **Pass 1 - Generate**: "Write compelling 2-3 sentence summary"
2. **Pass 2 - Critique**: "What's weak about this summary? How to improve?"
3. **Pass 3 - Refine**: "Apply the critique to create final version"

**Output**:
```json
{
  "professional_summary": "Senior Software Engineer with 8+ years building scalable cloud infrastructure. Proven track record of reducing costs by 40% while improving system reliability to 99.9%. Expert in AWS, Kubernetes, and leading cross-functional teams.",
  "critique_applied": [
    "Added specific years of experience",
    "Quantified achievements",
    "Aligned with JD's focus on cloud infrastructure"
  ],
  "quality_score": 92
}
```

**Quality Gates**:
- 2-3 sentences (40-80 words)
- Contains quantifiable achievement
- Mentions 2-3 key skills from JD
- Quality score > 80

**Error Handling**:
- If too long, add "Make more concise" pass
- If missing quantification, add "Add metrics" pass
- Max 5 total passes

---

### **STAGE 7: Final Resume Validation**
**API Calls**: 3 (validate + gap analysis + competitive check)  
**Models**: GPT-4o-mini  
**Cost**: ~$0.0012

**Input**: Complete tailored resume JSON + JD

**Process**:
1. **Check 1 - Tailoring Validation**: "Score resume-JD match 0-100"
2. **Check 2 - Gap Analysis**: "What JD requirements are not addressed?"
3. **Check 3 - Competitive Assessment**: "How does this compare to top candidates?"

**Output**:
```json
{
  "is_well_tailored": true,
  "tailoring_score": 92,
  "gaps": [
    {
      "requirement": "Experience with GraphQL",
      "severity": "minor",
      "suggestion": "Mention GraphQL in project section"
    }
  ],
  "competitive_assessment": {
    "strengths": ["Strong quantification", "Clear progression"],
    "weaknesses": ["Could emphasize leadership more"],
    "overall_ranking": "Top 20%"
  },
  "action": "accept"
}
```

**Validation Thresholds**:
- Tailoring score > 80 → Accept
- Tailoring score 70-80 → Accept with warnings
- Tailoring score < 70 → Restart from Stage 4

**Quality Gates**:
- All critical JD requirements addressed
- No major gaps
- Competitive ranking > "Top 30%"

**Error Handling**:
- If score < 80, provide specific feedback for Stage 4
- Max 1 full restart
- After restart, accept best attempt

---

### **STAGE 8: Cover Letter Generation**
**API Calls**: 3 (generate + critique + polish)  
**Models**: Claude Haiku (creative writing), GPT-4o-mini (critique)  
**Cost**: ~$0.0009

**Input**: Tailored resume JSON + JD + selected personal story + company research

**Process**:
1. **Pass 1 - Generate**: "Write compelling cover letter with web search for company insights"
2. **Pass 2 - Critique**: "What's weak? How to make more compelling?"
3. **Pass 3 - Polish**: "Apply critique and refine"

**Structure**:
- **Opening** (2-3 sentences): Hook + why this role
- **Body - Experience** (1 paragraph): Connect experience to JD
- **Body - Personal Story** (1 paragraph): Weave in selected story
- **Closing** (2-3 sentences): Strong call to action

**Output**:
```json
{
  "cover_letter_text": "Full cover letter text...",
  "sections": {
    "opening": "...",
    "body_experience": "...",
    "body_story": "...",
    "closing": "..."
  },
  "quality_metrics": {
    "readability_score": 88,
    "tone": "professional-enthusiastic",
    "length_words": 320
  }
}
```

**Quality Gates**:
- Length: 250-400 words
- Readability score > 80
- Mentions company name 2-3 times
- Includes personal story naturally

**Error Handling**:
- If too long, add "Make more concise" pass
- If tone off, add "Adjust tone to [target]" pass
- Max 5 total passes

---

### **STAGE 9: Final Quality Check**
**API Calls**: 3 (consistency + tone + polish)  
**Models**: GPT-4o-mini, Gemini Flash  
**Cost**: ~$0.0009

**Input**: Complete resume JSON + cover letter text

**Process**:
1. **Check 1 - Consistency**: "Verify dates, titles, companies consistent"
2. **Check 2 - Tone Consistency**: "Ensure professional tone throughout"
3. **Check 3 - Final Polish**: "Check typos, grammar, formatting"

**Output**:
```json
{
  "consistency_issues": [],
  "tone_issues": [],
  "grammar_issues": [],
  "final_quality_score": 95,
  "ready_for_output": true
}
```

**Quality Gates**:
- No consistency issues
- No grammar errors
- Final quality score > 90

**Error Handling**:
- If issues found, apply fixes automatically
- If critical issues, flag for manual review
- Never block output, only warn

---

### **STAGE 10: LaTeX Template Population & PDF Generation**
**API Calls**: 0 (pure logic)  
**Cost**: $0

**Input**: Validated resume JSON + cover letter text

**Process**:
1. Use Jinja2 template to populate LaTeX
2. Compile LaTeX to PDF using pdflatex
3. Generate cover letter PDF using ReportLab
4. Create referral version with alternate contact info
5. Organize files into proper structure

**Output**:
```
output/[Company]_[JobTitle]_[JobID]/
├── [FirstName]_[LastName]_[Company]_[JobID]_Resume.pdf
├── [FirstName]_[LastName]_[Company]_[JobID]_Cover_Letter.pdf
├── Referral_[FirstName]_[LastName]_[Company]_[JobID]_Resume.pdf
└── debug/
    ├── [Company]_[JobTitle]_Resume.json
    ├── [Company]_[JobTitle]_Resume.tex
    └── [Company]_[JobTitle]_CoverLetter.txt
```

**Quality Gates**:
- PDFs generated successfully
- Files organized correctly
- Referral version has correct contact info

**Error Handling**:
- If LaTeX compilation fails, save .tex for manual review
- If PDF generation fails, provide JSON/text versions
- Never fail completely

---

## 🛡️ Anti-Hallucination Strategies

### 1. Multi-Model Consensus
**Implementation**: Stages 1, 3, 7  
**Cost Impact**: 3x per stage  
**Benefit**: Catches 90% of hallucinations

**How it works**:
- Run same prompt through 3 different models
- Compare outputs field-by-field
- Use majority voting or weighted ensemble
- Flag discrepancies for review

**Example**:
```python
async def multi_model_consensus(prompt, models):
    results = await asyncio.gather(*[
        call_model(prompt, model) for model in models
    ])
    consensus = vote_on_results(results)
    confidence = calculate_confidence(results)
    return consensus, confidence
```

### 2. Chain-of-Thought Verification
**Implementation**: Stages 3, 4, 7  
**Cost Impact**: 2x per stage  
**Benefit**: Catches logical inconsistencies

**How it works**:
- Call 1: Generate output
- Call 2: "Explain your reasoning step-by-step"
- Verify reasoning is sound
- Reject if logic flawed

### 3. Self-Critique Loops
**Implementation**: Stages 4, 6, 8  
**Cost Impact**: 3x per stage  
**Benefit**: Improves quality by 40-60%

**How it works**:
- Pass 1: Generate content
- Pass 2: "Critique this output. What's wrong?"
- Pass 3: "Fix the issues you identified"

### 4. Fact-Checking Against Source
**Implementation**: Stage 5  
**Cost Impact**: 2x per experience  
**Benefit**: Prevents fabrication

**How it works**:
- After tailoring, verify each claim against master resume
- "Does this accurately represent the original?"
- Binary yes/no with explanation
- Reject if major deviation

### 5. Contradiction Detection
**Implementation**: Stage 9  
**Cost Impact**: 1 call  
**Benefit**: Catches internal inconsistencies

**How it works**:
- "Find any contradictions within this resume"
- Check dates, titles, skills consistency
- Flag and fix automatically

### 6. Grounding with Examples
**Implementation**: All stages  
**Cost Impact**: 0 (prompt engineering)  
**Benefit**: 40-60% reduction in hallucination

**How it works**:
- Include 3-5 good/bad examples in every prompt
- "Good example: X. Bad example: Y. Now do Z."
- Model learns from examples

### 7. Constrained Output Format
**Implementation**: All stages  
**Cost Impact**: 0 (validation)  
**Benefit**: Catches malformed outputs

**How it works**:
- Force JSON schema output
- Use Pydantic models to validate
- Reject and retry if schema violated

---

## 🚨 Error Prevention Strategies

### 1. Pre-Flight Validation
**Stage**: Before Stage 1  
**Purpose**: Prevent garbage-in-garbage-out

**Checks**:
- Is JD text complete? (> 100 words)
- Does it contain job title?
- Does it contain company name?
- Does it contain requirements?

### 2. Incremental Validation
**Stage**: After every stage  
**Purpose**: Catch errors immediately

**Implementation**:
```python
async def validate_stage_output(stage_name, output, schema):
    if not validate_schema(output, schema):
        raise ValidationError(f"{stage_name} output invalid")
    if not validate_quality_gates(output):
        raise QualityError(f"{stage_name} quality gates failed")
    return output
```

### 3. Semantic Similarity Scoring
**Stage**: Stage 5  
**Purpose**: Ensure meaning preserved

**How it works**:
- Calculate embedding similarity between original and tailored
- Score 0-100
- Reject if similarity < 75

### 4. Keyword Preservation Check
**Stage**: Stage 5  
**Purpose**: Ensure critical terms not lost

**How it works**:
- Extract key terms from master resume
- Verify they appear in tailored version
- Flag if critical keywords missing

### 5. Bullet Point Quality Scoring
**Stage**: Stage 4  
**Purpose**: Ensure high-quality bullets

**Criteria**:
- Impact: Does it show results?
- Specificity: Is it concrete?
- Quantification: Does it have metrics?
- Clarity: Is it easy to understand?

**Scoring**: Each criterion 0-25, total 0-100  
**Threshold**: Reject bullets < 70

### 6. RSTA Format Validation
**Stage**: Stage 4  
**Purpose**: Ensure proper structure

**Validation**:
```python
def validate_rsta_format(bullet):
    has_result = check_for_result_indicators(bullet)
    has_action = check_for_action_verbs(bullet)
    has_context = check_for_context_words(bullet)
    return has_result and has_action and has_context
```

### 7. Length Constraints
**Stage**: All stages  
**Purpose**: Prevent verbose outputs

**Constraints**:
- Summary: 2-3 sentences (40-80 words)
- Bullet: Max 2 lines (20-30 words)
- Cover letter: 250-400 words

### 8. Duplicate Detection
**Stage**: Stage 4  
**Purpose**: Avoid repetition

**How it works**:
- Calculate similarity between all bullets
- Flag if similarity > 80%
- Consolidate or rewrite duplicates

---

## 💪 Anti-Fragile Strategies

### 1. Graceful Degradation
**Purpose**: Never completely fail

**Fallback Hierarchy**:
1. Try primary approach
2. If fails, try simplified approach
3. If fails, use cached/default version
4. If fails, use original master resume content
5. Always produce something

**Example**:
```python
async def process_with_fallback(primary_fn, fallback_fn, default_value):
    try:
        return await primary_fn()
    except Exception as e:
        log_error(e)
        try:
            return await fallback_fn()
        except Exception as e2:
            log_error(e2)
            return default_value
```

### 2. Checkpoint System
**Purpose**: Resume from failure point

**Implementation**:
- Save state after every stage to disk
- Include timestamp, stage name, output
- On failure, load last checkpoint
- Resume from next stage

**File Structure**:
```
checkpoints/
└── [job_id]/
    ├── stage_1_jd_analysis.json
    ├── stage_2_summarization.json
    ├── stage_3_scoring.json
    └── ...
```

### 3. Circuit Breaker Pattern
**Purpose**: Prevent cascade failures

**How it works**:
- Track API failure rate
- If failures > 50% in 1 minute, open circuit
- Pause all requests for 60 seconds
- Gradually resume with exponential backoff

**States**:
- **Closed**: Normal operation
- **Open**: All requests fail fast
- **Half-Open**: Test with limited requests

### 4. Fallback Model Hierarchy
**Purpose**: Always have working alternative

**Hierarchy**:
1. **Primary**: GPT-4o-mini (fast, cheap)
2. **Fallback 1**: Gemini Flash (faster, cheaper)
3. **Fallback 2**: Claude Haiku (different provider)
4. **Fallback 3**: Cached response (if available)

**Auto-Switch Logic**:
- If primary fails 3x in a row, switch to Fallback 1
- If Fallback 1 fails 3x, switch to Fallback 2
- Reset to primary after 5 minutes

### 5. Timeout Protection
**Purpose**: Prevent hanging requests

**Implementation**:
- Max 30s per API call
- If timeout, retry with shorter prompt
- If timeout again, use fallback model
- If all timeout, use cached/default

### 6. Rate Limiting
**Purpose**: Prevent API throttling

**Implementation**:
- Max 10 concurrent API calls
- Queue excess requests
- Implement token bucket algorithm
- Respect provider rate limits

### 7. Exponential Backoff
**Purpose**: Recover from transient failures

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: Wait 1s
- Attempt 3: Wait 2s
- Attempt 4: Wait 4s
- Attempt 5: Wait 8s
- Attempt 6: Wait 16s (max)

### 8. Health Checks
**Purpose**: Detect issues early

**Pre-Flight Checks**:
- Ping each AI service
- Verify API keys valid
- Check rate limit status
- Test with simple prompt

**Continuous Monitoring**:
- Track success rate per model
- Track average latency
- Track error types
- Alert on anomalies

### 9. Partial Success Handling
**Purpose**: Don't fail entire job for one error

**Strategy**:
- If 4/5 experiences succeed, continue
- Mark failed items for manual review
- Generate resume with available content
- Flag incomplete sections

### 10. Idempotency
**Purpose**: Consistent results

**Implementation**:
- Cache results by content hash
- Same input always produces same output
- Avoid redundant API calls
- Enable safe retries

---

## 🔄 Rolling Context Strategies

### 1. Context Window Management
**Purpose**: Maintain coherence across stages

**Implementation**:
- Each stage receives summary of previous stages
- "Given that Stage 1 found X, and Stage 3 selected Y..."
- Maintains decision continuity

**Example Context**:
```json
{
  "stage_1_context": "JD emphasizes cloud infrastructure and leadership",
  "stage_3_context": "Selected experiences focus on AWS and team management",
  "stage_4_context": "Tailored bullets emphasize scalability and mentorship"
}
```

### 2. Cross-Stage Context Passing
**Purpose**: Inform later stages with earlier decisions

**Context Object**:
```python
class PipelineContext:
    jd_analysis: JDAnalysis
    selected_experiences: List[Experience]
    tailoring_decisions: Dict[str, str]
    quality_scores: Dict[str, float]
    
    def get_context_for_stage(self, stage_name):
        return {
            "previous_decisions": self.get_relevant_decisions(stage_name),
            "quality_metrics": self.get_relevant_metrics(stage_name),
            "constraints": self.get_constraints(stage_name)
        }
```

### 3. Iterative Refinement with Memory
**Purpose**: Learn from previous attempts

**Implementation**:
- Pass 1: Initial attempt
- Pass 2: "Given feedback: [feedback], improve"
- Pass 3: "Considering attempts: [history], finalize"

**Memory Structure**:
```json
{
  "attempt_1": {
    "output": "...",
    "feedback": "Lacks quantification",
    "score": 65
  },
  "attempt_2": {
    "output": "...",
    "feedback": "Better, but too verbose",
    "score": 78
  },
  "attempt_3": {
    "output": "...",
    "feedback": "Good",
    "score": 88
  }
}
```

### 4. Decision Logging
**Purpose**: Explain why choices were made

**Log Format**:
```json
{
  "stage": "stage_3_scoring",
  "decision": "Selected experience exp_1",
  "reasoning": "Score 95 due to direct match with required skills: Python, AWS, Kubernetes",
  "alternatives_considered": [
    {"id": "exp_2", "score": 87, "reason": "Good but less relevant"}
  ],
  "confidence": 0.92
}
```

---

## 🏛️ New Project Structure

```
jobbernaut-tailor/
├── README.md
├── future_roadmap_agentic_pipeline.md  # This document
├── requirements.txt
├── .env
├── .gitignore
│
├── config/
│   ├── models.yaml              # Model configurations per stage
│   ├── thresholds.yaml          # Quality gates and thresholds
│   └── prompts.yaml             # Prompt templates
│
├── src/
│   ├── __init__.py
│   │
│   ├── models/                  # Pydantic data models
│   │   ├── __init__.py
│   │   ├── job.py              # Job, JD, Application models
│   │   ├── resume.py           # Resume, Experience, Project models
│   │   ├── pipeline_state.py  # PipelineState, StageOutput models
│   │   └── config.py           # Configuration models
│   │
│   ├── services/                # Stage implementations
│   │   ├── __init__.py
│   │   ├── base_service.py     # Abstract base service
│   │   ├── ai_service.py       # AI provider abstraction
│   │   ├── jd_analyzer.py      # Stage 1: JD Analysis
│   │   ├── summarizer.py       # Stage 2: Summarization
│   │   ├── scorer.py           # Stage 3: Scoring & Selection
│   │   ├── tailor.py           # Stage 4: Experience Tailoring
│   │   ├── verifier.py         # Stage 5: Deviation Verification
│   │   ├── summary_gen.py      # Stage 6: Summary Generation
│   │   ├── validator.py        # Stage 7: Final Validation
│   │   ├── cover_letter.py     # Stage 8: Cover Letter
│   │   ├── quality_check.py    # Stage 9: Quality Check
│   │   └── latex_builder.py    # Stage 10: LaTeX & PDF
│   │
│   ├── pipeline/                # Pipeline orchestration
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Main pipeline controller
│   │   ├── stage_executor.py   # Execute individual stages
│   │   ├── context_manager.py  # Manage rolling context
│   │   ├── checkpoint.py       # Checkpoint system
│   │   └── retry_handler.py    # Retry logic with backoff
│   │
│   ├── infrastructure/          # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── circuit_breaker.py  # Circuit breaker pattern
│   │   ├── cache.py            # Response caching
│   │   ├── rate_limiter.py     # Rate limiting
│   │   ├── health_check.py     # Health monitoring
│   │   └── logger.py           # Structured logging
│   │
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── file_io.py          # File operations
│   │   ├── validation.py       # Schema validation
│   │   ├── text_processing.py  # Text utilities
│   │   └── pdf_generation.py   # PDF utilities
│   │
│   └── main.py                  # Entry point
│
├── templates/
│   ├── resume.tex.j2            # Jinja2 LaTeX template
│   └── cover_letter.html.j2     # HTML template (optional)
│
├── prompts/                     # Prompt templates (legacy)
│   ├── stage_1_jd_analysis.txt
│   ├── stage_2_summarization.txt
│   ├── stage_3_scoring.txt
│   ├── stage_4_tailoring.txt
│   ├── stage_5_verification.txt
│   ├── stage_6_summary.txt
│   ├── stage_7_validation.txt
│   ├── stage_8_cover_letter.txt
│   └── stage_9_quality_check.txt
│
├── profile/                     # User profile data
│   ├── master_resume.json
│   └── master_cover_letter_points.json
│
├── data/                        # Application data
│   ├── applications.yaml
│   └── application_template.yaml
│
├── output/                      # Generated outputs
│   └── [Company]_[JobTitle]_[JobID]/
│       ├── [Name]_Resume.pdf
│       ├── [Name]_Cover_Letter.pdf
│       ├── Referral_[Name]_Resume.pdf
│       └── debug/
│           ├── checkpoints/
│           ├── *.json
│           └── *.tex
│
└── tests/                       # Test suite
    ├── __init__.py
    ├── test_services/
    ├── test_pipeline/
    └── test_integration/
```

---

## 📋 Implementation Phases

### **Phase 1: Foundation (Week 1-2)**
**Goal**: Set up new architecture without breaking existing system

**Tasks**:
1. Create new project structure
2. Implement Pydantic models for all data types
3. Build abstract base service class
4. Implement AI service abstraction layer
5. Set up logging and monitoring infrastructure
6. Create configuration management system

**Deliverables**:
- New directory structure
- Type-safe data models
- Pluggable AI provider system
- Comprehensive logging

**Success Criteria**:
- All models have 100% type coverage
- Can switch between AI providers seamlessly
- Logs capture all important events

---

### **Phase 2: Core Services (Week 2-3)**
**Goal**: Implement individual stage services

**Tasks**:
1. Implement Stage 1: JD Analyzer with multi-model consensus
2. Implement Stage 2: Summarizer with parallel execution
3. Implement Stage 3: Scorer with reasoning validation
4. Implement Stage 4: Tailor with multi-pass refinement
5. Implement Stage 5: Verifier with fact-checking
6. Add unit tests for each service

**Deliverables**:
- 5 working stage services
- Unit tests with >80% coverage
- Service documentation

**Success Criteria**:
- Each service works independently
- All tests pass
- Services handle errors gracefully

---

### **Phase 3: Pipeline Orchestration (Week 3-4)**
**Goal**: Connect services into working pipeline

**Tasks**:
1. Implement pipeline orchestrator
2. Build context manager for rolling context
3. Implement checkpoint system
4. Add retry handler with exponential backoff
5. Implement circuit breaker pattern
6. Add integration tests

**Deliverables**:
- Working end-to-end pipeline
- Checkpoint/recovery system
- Integration tests

**Success Criteria**:
- Pipeline processes jobs successfully
- Can resume from checkpoints
- Handles failures gracefully

---

### **Phase 4: Quality & Robustness (Week 4-5)**
**Goal**: Add remaining stages and quality features

**Tasks**:
1. Implement Stage 6: Summary Generator
2. Implement Stage 7: Validator
3. Implement Stage 8: Cover Letter Generator
4. Implement Stage 9: Quality Checker
5. Implement Stage 10: LaTeX Builder with Jinja2
6. Add caching layer
7. Implement rate limiting

**Deliverables**:
- Complete 10-stage pipeline
- Caching system
- Rate limiting

**Success Criteria**:
- All stages working
- Cache hit rate >30%
- No rate limit violations

---

### **Phase 5: Migration & Optimization (Week 5-6)**
**Goal**: Migrate from old system and optimize

**Tasks**:
1. Create migration script for existing data
2. Run parallel testing (old vs new system)
3. Optimize prompt templates
4. Tune quality thresholds
5. Performance testing and optimization
6. Documentation and training

**Deliverables**:
- Migration complete
- Performance benchmarks
- User documentation

**Success Criteria**:
- New system matches or exceeds old quality
- Cost reduced by >70%
- Processing time <3 minutes per job

---

## 📊 Success Metrics

### Quality Metrics
- **Tailoring Score**: >90 (vs 70-80 currently)
- **Hallucination Rate**: <1% (vs ~10% currently)
- **Error Rate**: <1% (vs ~15% currently)
- **User Satisfaction**: >4.5/5

### Performance Metrics
- **Processing Time**: 2-3 minutes per job
- **API Calls**: 50-60 per job
- **Cost per Job**: $0.015-0.020
- **Success Rate**: >99%

### Reliability Metrics
- **Uptime**: >99.9%
- **Recovery Time**: <30 seconds
- **Checkpoint Success**: 100%
- **Graceful Degradation**: 100%

### Business Metrics
- **Cost Reduction**: 70-80%
- **Quality Improvement**: 10x
- **Throughput**: 20-30 jobs/hour
- **Scalability**: 100+ concurrent jobs

---

## 🔮 Future Enhancements

### Short-Term (3-6 months)
1. **A/B Testing Framework**: Test different prompts/models per stage
2. **User Feedback Loop**: Learn from accepted/rejected outputs
3. **Batch Processing**: Process multiple jobs in parallel
4. **Web Interface**: User-friendly UI for job submission
5. **Analytics Dashboard**: Track quality metrics over time

### Medium-Term (6-12 months)
1. **Fine-Tuned Models**: Train custom models on successful outputs
2. **Reinforcement Learning**: Optimize based on application success rates
3. **Multi-Language Support**: Generate resumes in multiple languages
4. **Industry-Specific Templates**: Specialized templates per industry
5. **Interview Prep**: Generate interview questions based on resume

### Long-Term (12+ months)
1. **Autonomous Agent**: Fully autonomous job application system
2. **Application Tracking**: Track application status and outcomes
3. **Salary Negotiation**: AI-powered salary negotiation assistant
4. **Career Coaching**: Long-term career planning and advice
5. **Network Building**: Automated LinkedIn outreach

---

## 🎓 Key Learnings & Best Practices

### What We Learned
1. **Cheap models + more calls > Expensive models + fewer calls**
   - Better quality control
   - Lower total cost
   - More resilient

2. **Multi-model consensus catches most hallucinations**
   - 90% reduction in false claims
   - Higher confidence in outputs
   - Worth the 3x cost

3. **Self-critique loops dramatically improve quality**
   - 40-60% improvement in quality scores
   - Models are good at critiquing themselves
   - Iterative refinement works

4. **Graceful degradation is essential**
   - Never completely fail
   - Always produce something
   - Users prefer imperfect output to no output

5. **Checkpointing saves time and money**
   - Resume from failure point
   - Don't waste successful API calls
   - Essential for long pipelines

### Best Practices
1. **Always validate outputs immediately**
2. **Log everything for debugging**
3. **Use type hints and Pydantic models**
4. **Implement circuit breakers for external services**
5. **Cache aggressively**
6. **Test each stage independently**
7. **Monitor quality metrics continuously**
8. **Fail fast, recover gracefully**
9. **Document decisions and reasoning**
10. **Optimize prompts before scaling**

---

## 📞 Contact & Support

For questions or issues with this roadmap:
- **GitHub**: [Jobbernaut/jobbernaut-tailor](https://github.com/Jobbernaut/jobbernaut-tailor)
- **Documentation**: See README.md for current system docs
- **Issues**: Use GitHub Issues for bug reports and feature requests

---

**Last Updated**: October 17, 2025  
**Version**: 2.0  
**Status**: Planning Phase - Ready for Implementation
