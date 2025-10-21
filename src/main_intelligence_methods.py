"""
Intelligence gathering methods to add to ResumeOptimizationPipeline class.
These methods should be inserted after _build_error_feedback method.
"""

async def analyze_job_resonance(self, job_description: str, company_name: str, output_dir: str) -> dict:
    """
    INTELLIGENCE STEP 1: Analyze job description for emotional keywords and hidden requirements.
    
    Args:
        job_description: The job description text
        company_name: The company name
        output_dir: Directory to save analysis results
        
    Returns:
        Dictionary containing JobResonanceAnalysis data
    """
    print("INTELLIGENCE STEP 1: Analyzing job resonance...")
    
    # Load prompt template
    analysis_prompt_template = load_prompt_template("analyze_job_resonance.txt")
    analysis_prompt = analysis_prompt_template.replace(
        "[JOB_DESCRIPTION]", job_description
    ).replace(
        "[COMPANY_NAME]", company_name
    )
    
    # Call API
    response = await self.call_poe_api(analysis_prompt, self.resume_bot)
    
    # Save raw response
    raw_path = os.path.join(output_dir, "Job_Resonance_Analysis_Raw.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"  Raw response saved: Job_Resonance_Analysis_Raw.txt")
    
    # Extract and validate JSON
    try:
        analysis_data = self.extract_json_from_response(response)
        validated_analysis = JobResonanceAnalysis(**analysis_data)
        result = validated_analysis.model_dump()
        
        # Save validated JSON
        json_path = os.path.join(output_dir, "Job_Resonance_Analysis.json")
        save_json(json_path, result)
        print(f"  ✓ Job resonance analysis complete")
        print(f"    - Emotional keywords: {len(result['emotional_keywords'])}")
        print(f"    - Cultural values: {len(result['cultural_values'])}")
        print(f"    - Hidden requirements: {len(result['hidden_requirements'])}")
        print(f"    - Power verbs: {len(result['power_verbs'])}")
        print(f"    - Technical keywords: {len(result['technical_keywords'])}\n")
        
        return result
        
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"  ✗ Job resonance analysis failed: {str(e)}")
        raise ValueError(f"Failed to analyze job resonance: {str(e)}")


async def research_company(self, job_description: str, company_name: str, output_dir: str) -> dict:
    """
    INTELLIGENCE STEP 2: Research company for authentic connection building.
    
    Args:
        job_description: The job description text
        company_name: The company name
        output_dir: Directory to save research results
        
    Returns:
        Dictionary containing CompanyResearch data
    """
    print("INTELLIGENCE STEP 2: Researching company...")
    
    # Load prompt template
    research_prompt_template = load_prompt_template("research_company.txt")
    research_prompt = research_prompt_template.replace(
        "[COMPANY_NAME]", company_name
    ).replace(
        "[JOB_DESCRIPTION]", job_description
    )
    
    # Call API
    response = await self.call_poe_api(research_prompt, self.resume_bot)
    
    # Save raw response
    raw_path = os.path.join(output_dir, "Company_Research_Raw.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"  Raw response saved: Company_Research_Raw.txt")
    
    # Extract and validate JSON
    try:
        research_data = self.extract_json_from_response(response)
        validated_research = CompanyResearch(**research_data)
        result = validated_research.model_dump()
        
        # Save validated JSON
        json_path = os.path.join(output_dir, "Company_Research.json")
        save_json(json_path, result)
        print(f"  ✓ Company research complete")
        print(f"    - Mission: {result['mission_statement'][:60]}...")
        print(f"    - Core values: {len(result['core_values'])}")
        print(f"    - Tech stack: {len(result['tech_stack'])} technologies\n")
        
        return result
        
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"  ✗ Company research failed: {str(e)}")
        raise ValueError(f"Failed to research company: {str(e)}")


async def generate_storytelling_arc(self, job_description: str, company_research: dict, 
                                   job_resonance: dict, tailored_resume: dict, 
                                   output_dir: str) -> dict:
    """
    INTELLIGENCE STEP 3: Generate storytelling arc for cover letter.
    
    Args:
        job_description: The job description text
        company_research: CompanyResearch data
        job_resonance: JobResonanceAnalysis data
        tailored_resume: The tailored resume JSON
        output_dir: Directory to save storytelling arc
        
    Returns:
        Dictionary containing StorytellingArc data
    """
    print("INTELLIGENCE STEP 3: Generating storytelling arc...")
    
    # Load prompt template
    arc_prompt_template = load_prompt_template("generate_storytelling_arc.txt")
    arc_prompt = arc_prompt_template.replace(
        "[JOB_DESCRIPTION]", job_description
    ).replace(
        "[COMPANY_RESEARCH]", json.dumps(company_research, indent=2)
    ).replace(
        "[JOB_RESONANCE]", json.dumps(job_resonance, indent=2)
    ).replace(
        "[TAILORED_RESUME]", json.dumps(tailored_resume, indent=2)
    )
    
    # Call API
    response = await self.call_poe_api(arc_prompt, self.cover_letter_bot)
    
    # Save raw response
    raw_path = os.path.join(output_dir, "Storytelling_Arc_Raw.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"  Raw response saved: Storytelling_Arc_Raw.txt")
    
    # Extract and validate JSON
    try:
        arc_data = self.extract_json_from_response(response)
        validated_arc = StorytellingArc(**arc_data)
        result = validated_arc.model_dump()
        
        # Save validated JSON
        json_path = os.path.join(output_dir, "Storytelling_Arc.json")
        save_json(json_path, result)
        print(f"  ✓ Storytelling arc generated")
        print(f"    - Hook: {result['hook'][:60]}...")
        print(f"    - Proof points: {len(result['proof_points'])}")
        print(f"    - Vision: {result['vision'][:60]}...\n")
        
        return result
        
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"  ✗ Storytelling arc generation failed: {str(e)}")
        raise ValueError(f"Failed to generate storytelling arc: {str(e)}")
