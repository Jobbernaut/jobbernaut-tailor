#!/usr/bin/env python3
"""
Comprehensive health check script for Jobbernaut Tailor
Tests all critical components and dependencies
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

def print_header(text):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def check_python_version():
    """Check Python version compatibility"""
    print_header("1. PYTHON VERSION CHECK")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}.{version.micro}")
        return False

def check_dependencies():
    """Check all required Python packages"""
    print_header("2. DEPENDENCY CHECK")
    
    required_packages = [
        'yaml',
        'jinja2',
        'pydantic',
        'dotenv',
        'fastapi_poe',
        'rich',
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            all_ok = False
    
    return all_ok

def check_module_imports():
    """Check if all custom modules can be imported"""
    print_header("3. MODULE IMPORT CHECK")
    
    modules = [
        'models',
        'utils',
        'template_renderer',
        'progress_tracker',
        'system_check',
        'fact_extractor',
        'fact_verifier',
        'main'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print_success(f"{module} imported successfully")
        except Exception as e:
            print_error(f"{module} failed to import: {str(e)}")
            all_ok = False
    
    return all_ok

def check_directory_structure():
    """Check if all required directories exist"""
    print_header("4. DIRECTORY STRUCTURE CHECK")
    
    required_dirs = [
        'src',
        'data',
        'profile',
        'prompts',
        'templates',
        'latex',
        'docs'
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        if Path(dir_name).is_dir():
            print_success(f"{dir_name}/ exists")
        else:
            print_error(f"{dir_name}/ is missing")
            all_ok = False
    
    return all_ok

def check_required_files():
    """Check if all required configuration files exist"""
    print_header("5. REQUIRED FILES CHECK")
    
    required_files = {
        'config.json': 'Configuration file',
        'requirements.txt': 'Python dependencies',
        'profile/master_resume.json': 'Master resume data',
        'data/applications.yaml': 'Job applications data (optional)',
        'prompts/generate_resume.txt': 'Resume generation prompt',
        'prompts/generate_cover_letter.txt': 'Cover letter generation prompt',
        'prompts/analyze_job_resonance.txt': 'Job resonance analysis prompt',
        'prompts/research_company.txt': 'Company research prompt',
        'prompts/generate_storytelling_arc.txt': 'Storytelling arc prompt',
        'templates/resume.jinja2': 'Resume LaTeX template',
        'templates/cover_letter.jinja2': 'Cover letter LaTeX template',
    }
    
    all_ok = True
    for file_path, description in required_files.items():
        if Path(file_path).is_file():
            print_success(f"{file_path} - {description}")
        else:
            if 'applications.yaml' in file_path:
                print_warning(f"{file_path} - {description} (will be created on first run)")
            else:
                print_error(f"{file_path} - {description} is missing")
                all_ok = False
    
    return all_ok

def check_env_configuration():
    """Check environment configuration"""
    print_header("6. ENVIRONMENT CONFIGURATION CHECK")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    env_ok = True
    
    # Check for .env file
    if Path('.env').is_file():
        print_success(".env file exists")
    else:
        print_warning(".env file not found (use .env.example as template)")
        env_ok = False
    
    # Check for POE_API_KEY
    api_key = os.getenv("POE_API_KEY")
    if api_key and api_key != "your_poe_api_key_here":
        print_success("POE_API_KEY is configured")
    else:
        print_warning("POE_API_KEY not configured in .env")
        env_ok = False
    
    return env_ok

def check_latex_installation():
    """Check if LaTeX is installed"""
    print_header("7. LaTeX INSTALLATION CHECK")
    
    import shutil
    
    pdflatex = shutil.which('pdflatex')
    if pdflatex:
        print_success(f"pdflatex found at: {pdflatex}")
        return True
    else:
        print_error("pdflatex not found in PATH")
        print("  Install LaTeX: sudo apt-get install texlive-latex-base texlive-latex-extra")
        return False

def check_config_file():
    """Validate config.json structure"""
    print_header("8. CONFIG.JSON VALIDATION")
    
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['defaults', 'resume_generation', 'cover_letter_generation', 'file_paths']
        
        all_ok = True
        for key in required_keys:
            if key in config:
                print_success(f"config.json has '{key}' section")
            else:
                print_error(f"config.json missing '{key}' section")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_error(f"Failed to load config.json: {str(e)}")
        return False

def check_profile_data():
    """Validate profile data files"""
    print_header("9. PROFILE DATA VALIDATION")
    
    import json
    all_ok = True
    
    # Check master_resume.json
    try:
        with open('profile/master_resume.json', 'r') as f:
            master_resume = json.load(f)
        
        required_sections = ['contact_info', 'work_experience', 'education', 'skills', 'projects']
        for section in required_sections:
            if section in master_resume:
                print_success(f"master_resume.json has '{section}' section")
            else:
                print_error(f"master_resume.json missing '{section}' section")
                all_ok = False
    except Exception as e:
        print_error(f"Failed to load master_resume.json: {str(e)}")
        all_ok = False
    
    # Check referral_contact.json (optional)
    try:
        with open('profile/referral_contact.json', 'r') as f:
            referral = json.load(f)
        
        if 'email' in referral and 'phone' in referral:
            print_success("referral_contact.json is configured (referral docs will be generated)")
        else:
            print_warning("referral_contact.json incomplete (referral docs will be skipped)")
    except Exception as e:
        print_warning(f"referral_contact.json not available: {str(e)}")
    
    return all_ok

def main():
    """Run all health checks"""
    print("\n" + "="*60)
    print("JOBBERNAUT TAILOR - COMPREHENSIVE HEALTH CHECK")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Module Imports", check_module_imports),
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_required_files),
        ("Environment Config", check_env_configuration),
        ("LaTeX Installation", check_latex_installation),
        ("Config File", check_config_file),
        ("Profile Data", check_profile_data),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Check '{name}' crashed: {str(e)}")
            results[name] = False
    
    # Summary
    print_header("HEALTH CHECK SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        status_str = "✓ PASS" if status else "✗ FAIL"
        print(f"{status_str:<10} {name}")
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n" + "="*60)
        print("🎉 ALL CHECKS PASSED - SYSTEM READY!")
        print("="*60)
        print("\nNext steps:")
        print("1. Configure your .env file with POE_API_KEY")
        print("2. Add jobs to data/applications.yaml")
        print("3. Run: python src/main.py")
        print("="*60 + "\n")
        return 0
    else:
        print("\n" + "="*60)
        print("⚠️  SOME CHECKS FAILED - REVIEW ABOVE")
        print("="*60)
        print(f"\n{total - passed} issue(s) need to be resolved before running the pipeline.")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
