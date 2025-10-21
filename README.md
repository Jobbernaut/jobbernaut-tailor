# Jobbernaut Tailor

**Stop wasting hours customizing resumes. Let AI do it in seconds.**

Jobbernaut Tailor is an intelligent automation system that transforms your master resume into perfectly tailored resumes and cover letters for every job you apply to. Copy-paste a job description, run one command, and get professional PDFs ready to submit.

---

## 🎯 Why This Is a Breakthrough

### The Old Way (Painful)
1. Find a job posting you like
2. Spend 1-2 hours rewriting your resume to match
3. Spend another hour crafting a cover letter
4. Repeat for every single job
5. Lose track of what you sent where
6. Job postings disappear before you can reference them

### The New Way (Effortless)
1. Copy-paste the job description into one file
2. Run `python src/main.py`
3. Get a perfectly tailored resume + cover letter in 60-90 seconds
4. Everything is saved and organized automatically
5. Never lose a job description again

**That's it.** No manual editing. No formatting headaches. No keeping track of dozens of files.

---

## 🚀 What Makes This Special

### 1. **One Master Resume, Infinite Variations**
You maintain ONE complete resume with all your experience. The AI intelligently selects and emphasizes the most relevant parts for each job. No more maintaining 10 different resume versions.

### 2. **Smart, Not Just Automated**
This isn't a simple template filler. The AI:
- Analyzes job descriptions to understand what matters
- Highlights your most relevant experiences
- Adjusts technical depth based on the role
- Creates natural, human-sounding cover letters
- Ensures everything is factually accurate

### 3. **Professional Quality Output**
- Beautiful LaTeX-formatted PDFs (the same system used for academic papers)
- Consistent, professional styling
- ATS-friendly (gets past automated resume screeners)
- Validation ensures no errors or hallucinations

### 4. **Your Personal Job Application Database**
Every job description is saved permanently in one organized file. Never worry about postings being taken down. Always have a record of what you applied for and when.

---

## 🤔 Need Help?

**If anything is confusing, just ask ChatGPT or Claude:**

> "I'm setting up Jobbernaut Tailor. Can you help me [create a .env file / understand the config / fix this error]?"

AI assistants can guide you through any step. This README covers the basics, but they can provide personalized help for your specific situation.

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **LaTeX** - For creating professional PDFs:
  - Windows: [MiKTeX](https://miktex.org/download)
  - Mac: [MacTeX](https://www.tug.org/mactex/)
  - Linux: `sudo apt-get install texlive-latex-extra`
- **AI API Key** - Get one from [Poe](https://poe.com/) (free tier available)

### Installation

1. **Clone and enter the project:**
   ```bash
   git clone https://github.com/Jobbernaut/jobbernaut-tailor.git
   cd jobbernaut-tailor
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create your `.env` file:**
   
   Create a file named `.env` in the project root with your API key:
   ```
   POE_API_KEY=your_api_key_here
   ```
   
   **How to get a Poe API key:**
   - Go to [poe.com](https://poe.com/)
   - Sign up or log in
   - Navigate to Settings → API Keys
   - Create a new key and copy it

4. **Set up your master resume:**
   
   Edit `profile/master_resume.json` with your complete work history, skills, and education. This is your single source of truth - include everything, even if it's not always relevant. The AI will pick what matters for each job.

5. **Verify LaTeX is installed:**
   ```bash
   pdflatex --version
   ```
   
   If this shows a version number, you're ready!

---

## 📝 Daily Workflow

### Step 1: Add a Job

Open `applications.yaml` and add a new entry at the top:

```yaml
- job_id: "unique-id-123"
  job_title: "Senior Software Engineer"
  company_name: "Amazing Tech Co"
  status: "pending"
  job_description: |
    [Paste the entire job description here]
    No formatting needed - just copy and paste!
    
    The system preserves everything exactly as posted.
```

**Tips:**
- `job_id`: Make it unique (company name + date works well)
- `status`: Always set to `"pending"` for new jobs
- `job_description`: Copy-paste the entire posting - no editing needed!

### Step 2: Run the Pipeline

```bash
python src/main.py
```

**What happens:**
1. Finds your pending job
2. Generates a tailored resume (JSON → LaTeX → PDF)
3. Creates a personalized cover letter (PDF)
4. Validates everything for accuracy
5. Organizes files in `output/CompanyName_JobTitle_JobID/`
6. Updates the job status to `"processed"`

**Output files:**
```
output/
└── Amazing_Tech_Co_Senior_Software_Engineer_unique-id-123/
    ├── YourName_Amazing_Tech_Co_unique-id-123_Resume.pdf
    ├── YourName_Amazing_Tech_Co_unique-id-123_Cover_Letter.pdf
    └── debug/
        ├── Resume.json
        ├── Resume.tex
        └── CoverLetter.txt
```

That's it! Your application materials are ready to submit.

---

## ⚙️ Configuration

### Basic Configuration (`config.json`)

The default configuration works great out of the box, but you can customize:

```json
{
  "resume_generation": {
    "bot_name": "Gemini-2.5-Pro",
    "thinking_budget": "8192",
    "web_search": true
  },
  "cover_letter_generation": {
    "bot_name": "Claude-Sonnet-4.5",
    "thinking_budget": "2048",
    "web_search": true
  },
  "intelligence_steps": {
    "job_resonance_analysis": {
      "bot_name": "Gemini-2.5-Pro",
      "thinking_budget": "4096"
    },
    "company_research": {
      "bot_name": "Gemini-2.5-Pro",
      "thinking_budget": "4096"
    },
    "storytelling_arc": {
      "bot_name": "Gemini-2.5-Pro",
      "thinking_budget": "4096"
    }
  },
  "humanization": {
    "enabled": false,
    "level": "low",
    "apply_to": ["resume", "cover_letter"]
  },
  "referral_resume": {
    "email": "alternative@email.com",
    "phone": "555-0123"
  },
  "defaults": {
    "resume_bot": "Gemini-2.5-Pro",
    "cover_letter_bot": "Claude-Sonnet-4.5"
  },
  "reasoning_trace": false
}
```

**Key settings:**
- `bot_name`: Which AI model to use (Gemini, Claude, GPT-4)
- `intelligence_steps`: Configure AI models for job analysis, company research, and storytelling (V4)
- `humanization.enabled`: Make AI writing sound more natural
- `humanization.level`: "low", "medium", or "high" naturalness
- `referral_resume`: Alternative contact info for employee referrals
- `defaults`: Fallback bot configurations
- `reasoning_trace`: Enable detailed debugging output

### Environment Variables (`.env`)

**Required:**
```
POE_API_KEY=your_poe_api_key
```

**Optional:**
```
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

---

## 🎨 Customization

### Humanization Levels

AI-generated content can sound robotic. Humanization makes it more natural:

- **None/Disabled**: Formal, technical, precise
- **Low**: Slightly more natural while staying professional
- **Medium**: Balanced - natural but still professional
- **High**: Conversational and engaging

**When to use:**
- Technical roles: Low or disabled
- Corporate roles: Low to medium
- Startups/Creative: Medium to high

### Referral Resumes

When applying through employee referrals, some companies want alternative contact info:

```json
"referral_resume": {
  "email": "referral@email.com",
  "phone": "555-0123"
}
```

Enable this in your job entry:
```yaml
- job_id: "ref-123"
  referral: true
  # ... rest of job details
```

---

## 🔧 Troubleshooting

### "No pending jobs found"
All jobs in `applications.yaml` are marked as `"processed"`. Add a new job with `status: "pending"`.

### "API key not found"
Check that your `.env` file exists and contains `POE_API_KEY=your_key_here`.

### "pdflatex not found"
LaTeX isn't installed or not in your PATH. Install MiKTeX/MacTeX/TeXLive and restart your terminal.

### "Validation failed"
The AI generated content that doesn't match your master resume. Check the error message for details. The system will prevent submitting inaccurate information.

### JSON parsing errors
The AI response wasn't properly formatted. Try running again or switch to a different model in `config.json`.

### Still stuck?
Ask ChatGPT or Claude! Copy the error message and ask:
> "I'm using Jobbernaut Tailor and got this error: [paste error]. How do I fix it?"

---

## 📚 Technical Documentation

For developers and advanced users, comprehensive technical documentation is available in the `docs/` folder:

- **[Documentation Index](docs/README.md)** - Navigation and overview
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Evolution](docs/EVOLUTION.md)** - Version history (V1 → V2 → V3 → V4)
- **[Pipeline](docs/PIPELINE.md)** - Detailed pipeline steps
- **[Models](docs/MODELS.md)** - Pydantic validation system
- **[Templates](docs/TEMPLATES.md)** - Jinja2 template customization
- **[Configuration](docs/CONFIGURATION.md)** - Advanced configuration options

---

## 🏗️ How It Works (Simple Explanation)

1. **You provide:** Your complete work history (once) + a job description
2. **AI analyzes:** What skills and experiences matter for this specific job
3. **AI tailors:** Selects and emphasizes your most relevant background
4. **Templates format:** Converts to beautiful LaTeX (professional typesetting)
5. **Validation checks:** Ensures accuracy and quality
6. **PDF generation:** Creates submission-ready documents
7. **Organization:** Saves everything with clear naming

**The magic:** The AI understands context. It knows that "led a team of 5" matters more for a leadership role, while "optimized database queries" matters more for a backend position. It makes these decisions automatically.

---

## 🎯 Best Practices

### Master Resume
- Include EVERYTHING - all jobs, skills, projects
- Be detailed - the AI can condense but can't expand
- Keep it updated as you gain new experience
- Don't worry about length - this isn't what you submit

### Job Descriptions
- Copy the entire posting - don't summarize
- Include company info if available
- Paste exactly as posted (formatting doesn't matter)
- The system preserves everything for future reference

### Applications YAML
- Add new jobs at the top (easier to find)
- Use descriptive job_ids (company-date works well)
- Keep processed jobs for your records
- Never delete entries - they're your application history

---

## 🚀 What's Next?

Once you're comfortable with the basics:

1. **Customize templates** - Edit `templates/resume.jinja2` for your preferred style
2. **Adjust prompts** - Modify `prompts/` to change AI behavior
3. **Try different models** - Experiment with Claude, GPT-4, or Gemini
4. **Enable humanization** - Make your applications sound more natural
5. **Explore the docs** - Deep dive into the technical architecture

---

## 📄 License

This project is for personal use. Modify and extend as needed for your job search.

---

## 🙏 Contributing

Found a bug? Have an improvement? Feel free to:
- Open an issue
- Submit a pull request
- Share your customizations

---

## 💡 The Bottom Line

**Job hunting is hard enough.** Let AI handle the tedious parts so you can focus on:
- Finding great opportunities
- Preparing for interviews
- Networking
- Actually getting hired

Stop spending hours on each application. Start applying to more jobs with better materials in less time.

**Questions?** Ask ChatGPT, Claude, or check the [docs](docs/README.md).

**Ready?** Add your first job to `applications.yaml` and run `python src/main.py`. 

Good luck with your job search! 🎉
