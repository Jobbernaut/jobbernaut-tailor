"""
Test script to verify YAML pipe symbol preservation when updating job status.
"""

from src.utils import load_yaml, save_yaml, update_job_status

def test_yaml_preservation():
    """Test that pipe symbols are preserved when updating YAML."""
    
    print("Testing YAML pipe symbol preservation...")
    print("=" * 60)
    
    # Load the applications
    applications = load_yaml("applications.yaml")
    
    # Find a processed job to check
    processed_jobs = [job for job in applications if job.get("status") == "processed"]
    
    if processed_jobs:
        test_job = processed_jobs[0]
        job_id = test_job.get("job_id")
        job_description = test_job.get("job_description", "")
        
        print(f"\nTest Job ID: {job_id}")
        print(f"Job Description length: {len(job_description)} characters")
        print(f"Contains newlines: {chr(10) in job_description}")
        
        # Save the YAML (this should preserve pipe symbols)
        print("\nSaving YAML file...")
        save_yaml("applications.yaml", applications)
        
        # Reload and verify
        print("Reloading YAML file...")
        reloaded = load_yaml("applications.yaml")
        
        # Find the same job
        reloaded_job = next((job for job in reloaded if job.get("job_id") == job_id), None)
        
        if reloaded_job:
            reloaded_description = reloaded_job.get("job_description", "")
            
            # Check if content is preserved
            if job_description == reloaded_description:
                print("✓ Job description content preserved correctly")
            else:
                print("✗ Job description content changed!")
                print(f"  Original length: {len(job_description)}")
                print(f"  Reloaded length: {len(reloaded_description)}")
            
            # Read the raw YAML file to check for pipe symbols
            with open("applications.yaml", "r", encoding="utf-8") as f:
                yaml_content = f.read()
            
            # Check if pipe symbols are present
            if "job_description: |" in yaml_content or "job_description: |-" in yaml_content:
                print("✓ Pipe symbols (|) preserved in YAML file")
            else:
                print("✗ Pipe symbols NOT found in YAML file")
                # Check what format was used instead
                if f'job_description: "' in yaml_content or f"job_description: '" in yaml_content:
                    print("  ⚠️  Using quoted string format instead")
        
        print("\n" + "=" * 60)
        print("Test completed!")
        
    else:
        print("No processed jobs found to test with")

if __name__ == "__main__":
    test_yaml_preservation()
