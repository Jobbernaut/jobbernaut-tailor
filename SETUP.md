# Jobbernaut Tailor - Setup Guide

Welcome to Jobbernaut Tailor! This guide will help you get the system up and running.

## System Status: ✅ MOSTLY READY

Your system has been revived and is **8/9 checks passing**. Only the `.env` file configuration remains.

---

## Quick Start (3 Steps)

### 1. Configure Environment Variables

Copy the example file and add your POE API key:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your_poe_api_key_here` with your actual API key from [poe.com/api_key](https://poe.com/api_key).

### 2. Run Health Check

Verify everything is working:

```bash
source .venv/bin/activate
python health_check.py
```

You should see **9/9 checks passed** ✅

### 3. Run the Pipeline

Process your pending jobs:

```bash
source .venv/bin/activate
python src/main.py
```

---

## System Overview

### What's Been Done ✅

- ✅ Python 3.14.2 virtual environment activated
- ✅ All dependencies installed (including missing `rich` module)
- ✅ All 8 core modules importing successfully
- ✅ Directory structure validated
- ✅ All required files present
- ✅ LaTeX (pdflatex) installed and working
- ✅ config.json validated
- ✅ profile/master_resume.json validated
- ✅ profile/referral_contact.json configured
- ✅ Comprehensive health check script created

### What Needs Configuration ⚠️

- ⚠️ **`.env` file with POE_API_KEY** - Required to run the pipeline

---

## Project Structure

```
Tailor/
├── .venv/                    # Python virtual environment (activated)
├── .env.example              # Environment template (created)
├── health_check.py           # Health check script (new!)
├── config.json               # Main configuration
├── requirements.txt          # Python dependencies
├── src/                      # Source code
│   ├── main.py              # Main pipeline
│   ├── models.py            # Pydantic models
│   ├── utils.py             # Utility functions
│   ├── template_renderer.py # Jinja2 LaTeX rendering
│   ├── progress_tracker.py  # Progress tracking
│   ├── system_check.py      # System validation
│   ├── fact_extractor.py    # Fact extraction
│   └── fact_verifier.py     # Fact verification
├── profile/                  # Your personal data
│   ├── master_resume.json   # Master resume (validated ✓)
│   └── referral_contact.json # Referral info (validated ✓)
├── data/                     # Job applications
│   ├── applications.yaml    # Job queue
│   └── application_template.yaml
├── prompts/                  # AI prompts
├── templates/                # LaTeX templates
├── latex/                    # LaTeX classes
└── docs/                     # Documentation
```

---

## Health Check Script

The new `health_check.py` script validates:

1. ✅ Python version (3.10+)
2. ✅ All Python dependencies
3. ✅ All module imports
4. ✅ Directory structure
5. ✅ Required files
6. ⚠️ Environment configuration (.env + POE_API_KEY)
7. ✅ LaTeX installation
8. ✅ config.json structure
9. ✅ Profile data (master_resume.json, referral_contact.json)

Run it anytime with:
```bash
source .venv/bin/activate
python health_check.py
```

---

## Configuration Files

### .env (Required)
```bash
# Get your API key from: https://poe.com/api_key
POE_API_KEY=your_actual_api_key_here
```

### config.json (Already Configured ✓)
Controls bot selection, parameters, file paths, humanization levels, etc.

### profile/master_resume.json (Already Configured ✓)
Your complete resume data - source of truth for all generations.

### profile/referral_contact.json (Already Configured ✓)
Referral contact info - generates alternate versions with referral details.

### data/applications.yaml (Ready for Jobs)
Add jobs here with status: "pending" to process them.

---

## Running the Pipeline

### Activate Virtual Environment
```bash
source .venv/bin/activate
```

### Process Jobs
```bash
python -m src.main
```

The pipeline will:
1. Find all jobs with `status: pending` in `applications.yaml`
2. Run 12-step intelligence-driven pipeline for each job
3. Generate tailored resumes and cover letters
4. Compile PDFs (including referral versions)
5. Update job status to `processed`

---

## Dependencies Installed

All required packages are installed in `.venv/`:

- ✅ `rich` - Terminal UI and progress tracking
- ✅ `pydantic` - Data validation
- ✅ `fastapi_poe` - POE API client
- ✅ `jinja2` - Template rendering
- ✅ `pyyaml` - YAML parsing
- ✅ `python-dotenv` - Environment variables
- ✅ All supporting libraries

---

## Troubleshooting

### Health Check Fails

Run the health check to identify issues:
```bash
source .venv/bin/activate
python health_check.py
```

### Missing POE_API_KEY

1. Get your key: [poe.com/api_key](https://poe.com/api_key)
2. Create `.env`: `cp .env.example .env`
3. Edit `.env` and add your key

### Import Errors

Ensure virtual environment is activated:
```bash
source .venv/bin/activate
```

Then verify:
```bash
python -c "import sys; sys.path.insert(0, 'src'); import main; print('✓ Success')"
```

### LaTeX Compilation Errors

Verify pdflatex is installed:
```bash
which pdflatex
```

If missing, install:
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra
```

---

## Next Steps

1. **Configure `.env`** with your POE_API_KEY
2. **Run health check** to verify: `python health_check.py`
3. **Add jobs** to `data/applications.yaml`
4. **Run pipeline**: `python -m src.main`
5. **Check outputs** in generated directories

---

## Git Branch

You're currently on: **v4.3.0**

This is the production version with all features including fact verification and humanization.

---

## Support

- **Documentation**: See `docs/` for architecture, configuration, and guides
- **FAQ**: See `FAQ.md` for common questions
- **Issues**: Use GitHub issues or `/reportbug` in your IDE

---

## System Requirements Summary

| Component | Status | Details |
|-----------|--------|---------|
| Python | ✅ 3.14.2 | Compatible (3.10+ required) |
| Virtual Env | ✅ Active | `.venv/` activated |
| Dependencies | ✅ Installed | All packages ready |
| LaTeX | ✅ Installed | `/usr/bin/pdflatex` |
| Master Resume | ✅ Valid | All required sections present |
| Referral Info | ✅ Valid | Email and phone configured |
| Config File | ✅ Valid | All sections present |
| .env File | ⚠️ Missing | **Configure with POE_API_KEY** |

---

**🎉 Your project is back to life! Just add your POE_API_KEY and you're ready to go!**
