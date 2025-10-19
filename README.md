# Jobbernaut Job Automation Pipeline

This project is the tailoring backend of Jobbernaut, automating the tedious process of creating tailored resumes and cover letters for job applications. It is designed as a robust pipeline that uses a single master file as its database, processes jobs one by one, and leverages AI to generate high-quality, personalized application materials. Project currently pulled from Jobbernaut's deployment due to misuse concerns.

## Core Philosophy

The design of this project is guided by three core principles:

1.  **A Single Source of Truth:** All job application data, including the raw job descriptions, lives in one master file: `applications.yaml`. This eliminates the need to manage separate input files for each job, creating a scalable and maintainable database of all your prospects.
2.  **Hassle-Free Data Entry:** Using the YAML format allows for raw, multi-line text blocks (`job_description: |`). You can copy and paste a job description directly from a website without any manual formatting or escaping of special characters.
3.  **Intelligent Automation, Not Just Generation:** The system doesn't just generate generic documents. It intelligently selects the most relevant personal story for each cover letter by analyzing the job description for keywords. This provides strategic personalization without requiring manual intervention for each job.

## Features

- **Queue-Based Processing:** The script automatically finds the next job with `status: "pending"` and processes it.
- **Persistent Job Archive:** Stores the full, original job description for every application, protecting you from postings being taken down.
- **Automated Cover Letter Personalization:** Intelligently selects from a bank of your personal stories (`master_cover_letter_points.json`) based on keyword matching against the job description.
- **Multiple Output Formats:** Generates JSON, LaTeX, and PDF versions of your tailored resume, plus PDF cover letters.
- **LaTeX Verification:** Automatically verifies LaTeX resumes against your master resume to prevent factual misrepresentations before PDF generation.
- **Professional PDF Generation:** Compiles LaTeX resumes to PDF using pdflatex with automatic package installation.
- **Organized File Structure:** Automatically organizes output files with standardized naming and separates debug files.
- **Configurable AI Models:** Use different AI models (via Poe API) for resume generation, LaTeX conversion, verification, and cover letter writing.
- **YAML Database:** A human-readable and easy-to-edit master file for all your jobs.
- **Idempotent:** Once a job is `processed`, the script will ignore it on subsequent runs, allowing you to safely re-run the pipeline at any time.

## File Structure

```
.
├── .gitignore
├── applications.yaml              # <-- YOUR MASTER JOB DATABASE. This is the main file you will edit.
├── config.json                    # <-- Configuration for AI models and pipeline settings
├── requirements.txt
├── resume.cls                     # <-- LaTeX resume class file for professional formatting
├── profile/
│   ├── master_resume.json         # <-- Your master resume data in JSON format
│   └── master_cover_letter_points.json  # <-- Your personal story bank with keywords
├── prompts/
│   ├── generate_resume.txt        # <-- Prompt template for generating tailored resumes
│   ├── generate_cover_letter.txt  # <-- Prompt template for generating cover letters
│   ├── convert_resume_to_latex.txt # <-- Prompt template for LaTeX conversion
│   └── verify_latex_resume.txt    # <-- Prompt template for LaTeX verification
├── src/
│   ├── main.py                    # <-- The main pipeline script
│   └── utils.py                   # <-- Helper functions for file I/O and processing
└── output/                        # <-- Generated resumes and cover letters (auto-created)
    └── [Company]_[JobTitle]_[JobID]/
        ├── [FirstName]_[LastName]_[Company]_[JobID]_Resume.pdf
        ├── [FirstName]_[LastName]_[Company]_[JobID]_Cover_Letter.pdf
        └── debug/
            ├── [Company]_[JobTitle]_Resume.json
            ├── [Company]_[JobTitle]_Resume.tex
            └── [Company]_[JobTitle]_CoverLetter.txt
```

## Setup and Installation

### Prerequisites

- **Python 3.8+**
- **MiKTeX** (Windows) or **TeX Live** (Linux/Mac) for PDF generation
  - Download MiKTeX: https://miktex.org/download
  - Download TeX Live: https://www.tug.org/texlive/

### Installation Steps

1.  **Clone the Repository:**

    ```bash
    git clone <your-repo-url>
    cd resume-optimization
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    This will install all required libraries including `PyYAML`, `fastapi_poe`, `python-dotenv`, `reportlab`, and others.

4.  **Install LaTeX Distribution:**

    **For Windows (MiKTeX):**

    - Download and install MiKTeX from https://miktex.org/download
    - During installation, choose "Install missing packages on-the-fly: Yes"
    - Restart your terminal/IDE after installation

    **For Linux:**

    ```bash
    sudo apt-get install texlive-latex-base texlive-latex-extra
    ```

    **For macOS:**

    ```bash
    brew install --cask mactex
    ```

    Verify installation:

    ```bash
    pdflatex --version
    ```

5.  **Set Up API Keys:**

    Create a `.env` file in the root directory (and make sure `.env` is in your `.gitignore` file):

    ```
    # .env
    POE_API_KEY="your_poe_api_key_here"
    ```

    The pipeline uses the Poe API to access various AI models. You can get an API key from [Poe](https://poe.com/).

6.  **Configure Your Profile:**

    - Edit `profile/master_resume.json` with your complete resume data
    - Edit `profile/master_cover_letter_points.json` with your personal stories and keywords
    - Optionally customize `config.json` to change AI models or settings

## Configuration

The `config.json` file allows you to customize the AI models and settings for each stage of the pipeline:

```json
{
  "resume_generation": {
    "bot_name": "Gemini-2.5-Pro",
    "thinking_budget": "8192",
    "web_search": true
  },
  "latex_conversion": {
    "bot_name": "Gemini-2.5-Pro",
    "thinking_budget": "8192",
    "web_search": false
  },
  "latex_verification": {
    "bot_name": "Gemini-2.5-Pro",
    "thinking_budget": "4096",
    "web_search": false
  },
  "cover_letter_generation": {
    "bot_name": "Gemini-2.5-Pro",
    "thinking_budget": "8192",
    "web_search": false
  },
  "reasoning_trace": false,
  "dry_run": false
}
```

### Configuration Options:

- **bot_name:** The Poe AI model to use (e.g., "Gemini-2.5-Pro", "Claude-3.7-Sonnet", "GPT-4o")
- **thinking_budget:** Token budget for model reasoning
- **web_search:** Enable/disable web search capabilities for the model
- **reasoning_trace:** Show/hide AI reasoning traces in cover letters
- **dry_run:** Test mode (not fully implemented)

### Pipeline Stages:

1. **resume_generation:** Tailors your master resume to the job description
2. **latex_conversion:** Converts the tailored resume JSON to professional LaTeX format
3. **latex_verification:** Verifies the LaTeX resume for factual accuracy and quality
4. **cover_letter_generation:** Creates a personalized cover letter

## Daily Workflow

Your entire workflow consists of just two simple steps: adding a job and running the script.

### Step 1: Add a New Job to `applications.yaml`

Open `applications.yaml` and add a new entry at the top of the list.

- Set the `status` to `"pending"`.
- Fill in the `job_id`, `job_title`, and `company_name`.
- Copy the entire job description from the website and paste it directly under `job_description: |`. **Ensure the pasted text is indented correctly.**

**Example of adding a new job:**

```yaml
- job_id: "some-new-unique-id"
  job_title: "Senior DevOps Engineer"
  company_name: "Cyberdyne Systems"
  status: "pending"
  job_description: |
    As a Senior DevOps Engineer at Cyberdyne Systems, you will be responsible for building and maintaining the infrastructure that powers our global defense network.

    We are looking for an engineer with a strong sense of ownership and a proactive mindset. You will be expected to improve our CI/CD pipelines, automate deployments, and enhance system reliability.

- job_id: "AMZ26535.1"
  job_title: "Software Dev Engineer II"
  company_name: "Amazon Web Services"
  status: "processed" # This job will be skipped by the script
  job_description: |
    Description Employer: Amazon Web Services, Inc...
```

### Step 2: Run the Pipeline

Execute the main script from your terminal:

```bash
python src/main.py
```

### What Happens Next

The script will:

1.  **Find the pending job:** Locate the first job in `applications.yaml` with `status: "pending"`.
2.  **Select cover letter story:** Automatically choose the best personal story from `profile/master_cover_letter_points.json` by matching keywords.
3.  **Generate tailored resume:** Call the Poe API to create a tailored resume in JSON format using your master resume data.
4.  **Generate cover letter:** Create a personalized cover letter as a PDF document.
5.  **Convert to LaTeX:** Transform the tailored resume JSON to professional LaTeX format.
6.  **Verify LaTeX resume:** Check the LaTeX resume against your master resume for:
    - Factual accuracy (no blatant lies or major misrepresentations)
    - Quality issues (spacing, formatting, completeness)
    - Professional standards
7.  **Compile to PDF:** If verification passes, compile the LaTeX file to a professional PDF using pdflatex.
8.  **Organize files:** Automatically organize output files with standardized naming:
    - Move intermediate files (.tex, .json, .txt) to a `debug/` subdirectory
    - Rename PDFs with format: `FirstName_LastName_Company_JobID_Resume.pdf`
9.  **Update status:** Change the job's status from `pending` to `processed` in `applications.yaml`.

**Important:** If verification fails, the process halts and displays the issues found. You'll need to review and fix any problems before the PDF is generated.

## Output Files

For each processed job, the pipeline creates a directory under `output/` with the following structure:

```
output/
└── [Company]_[JobTitle]_[JobID]/
    ├── [FirstName]_[LastName]_[Company]_[JobID]_Resume.pdf
    ├── [FirstName]_[LastName]_[Company]_[JobID]_Cover_Letter.pdf
    └── debug/
        ├── [Company]_[JobTitle]_Resume.json
        ├── [Company]_[JobTitle]_Resume.tex
        └── [Company]_[JobTitle]_CoverLetter.txt
```

**Example:**

```
output/
└── Amazon_Web_Services_Software_Dev_Engineer_II_AMZ26535.1/
    ├── Snehashish_Reddy_Manda_Amazon_Web_Services_AMZ26535.1_Resume.pdf
    ├── Snehashish_Reddy_Manda_Amazon_Web_Services_AMZ26535.1_Cover_Letter.pdf
    └── debug/
        ├── Amazon Web Services_Software Dev Engineer II_Resume.json
        ├── Amazon Web Services_Software Dev Engineer II_Resume.tex
        └── Amazon Web Services_Software Dev Engineer II_CoverLetter.txt
```

### File Descriptions:

- **Resume PDF:** Professional LaTeX-compiled resume ready to submit
- **Cover Letter PDF:** Personalized cover letter ready to submit
- **debug/Resume.json:** Tailored resume data in JSON format (for reference)
- **debug/Resume.tex:** LaTeX source file (for manual editing if needed)
- **debug/CoverLetter.txt:** Plain text version of cover letter

## LaTeX Verification

The pipeline includes an intelligent verification step that checks your LaTeX resume before PDF generation:

### What Gets Verified:

1. **Factual Accuracy:**

   - Compares LaTeX content against your master resume
   - Detects blatant lies or major misrepresentations
   - Allows minor embellishments but flags significant discrepancies

2. **Quality Checks:**

   - Identifies spacing and formatting issues
   - Ensures professional presentation
   - Validates completeness of sections

3. **Severity Levels:**
   - **Critical:** Major factual errors or lies (fails verification)
   - **Major:** Significant quality issues (fails verification)
   - **Minor:** Small improvements suggested (passes with warnings)

### Verification Output:

```
============================================================
VERIFICATION RESULTS
============================================================
Status: ✓ PASSED
Quality Score: 92/100
Summary: Resume is accurate and well-formatted with minor suggestions.

Issues Found (2):
1. 🟢 [MINOR] formatting
   Description: Consider adding more whitespace between sections
   Location: Work Experience section
============================================================
```

If verification fails, the process halts and you'll see detailed error messages. Fix the issues in your master resume or prompts, then run the pipeline again.

## Customizing Your Narrative

To make the automation more effective, you can customize your personal story bank in `profile/master_cover_letter_points.json`.

- **`point_text`**: The actual story or statement you want to include in your cover letter.
- **`keywords`**: A list of words that, if found in a job description, make this story relevant. The script will pick the story with the most keyword matches.
- **`default`**: Set `true` for one (and only one) point. This will be the fallback option if no keywords are matched, and will always be included in every cover letter.

```json
{
  "cover_letter_points": [
    {
      "id": "ownership_mentality_story",
      "point_text": "I thrive in environments where I can take ownership...",
      "keywords": [
        "ownership",
        "proactive",
        "automation",
        "efficiency",
        "build"
      ],
      "default": false
    },
    {
      "id": "work_authorization_detailed",
      "point_text": "I am authorized for full-time employment in the U.S...",
      "keywords": [],
      "default": true
    }
  ]
}
```

## Master Resume Format

Your `profile/master_resume.json` should contain your complete resume data in a structured JSON format. The pipeline will use this to generate tailored versions for each job. Key sections include:

- `contact_info`: Your name, email, phone, location, LinkedIn, GitHub, etc.
  - **Important:** Must include `first_name` and `last_name` for PDF naming
- `professional_summaries`: Different summary statements for various roles
- `work_experience`: All your work history with detailed accomplishments
- `skills`: Technical skills, tools, frameworks, etc.
- `education`: Degrees and certifications
- `projects`: Personal or academic projects (optional)

The AI will intelligently select and tailor content from this master file based on the job description.

## Troubleshooting

### Common Issues:

- **No pending jobs found:** All jobs in `applications.yaml` have `status: "processed"`. Add a new job with `status: "pending"`.

- **API errors:** Check that your `POE_API_KEY` is correctly set in the `.env` file and that you have API credits.

- **JSON parsing errors:** The AI response may not be properly formatted. Try adjusting the `bot_name` in `config.json` or check the prompt templates.

- **LaTeX compilation timeout:**

  - Ensure MiKTeX is properly installed and in your PATH
  - Configure MiKTeX to auto-install packages:
    1. Open MiKTeX Console
    2. Go to Settings → General
    3. Set "Install missing packages on-the-fly" to "Yes"
  - Restart your terminal/IDE after configuration

- **Verification failures:**

  - Review the detailed error messages in the console
  - Check your master resume for accuracy
  - Adjust the verification prompt if needed
  - Consider using a different AI model for verification

- **Missing output files:** Check the console output for errors during the pipeline execution.

- **PDF not generated:** Verify that `pdflatex` is installed and accessible:
  ```bash
  pdflatex --version
  ```

### Debug Mode:

If you encounter issues, check the `debug/` folder in your output directory for:

- The raw JSON resume data
- The LaTeX source file (you can manually compile this to identify LaTeX errors)
- The plain text cover letter

## Advanced Usage

### Customizing Prompts

You can modify the prompt templates in the `prompts/` directory to change how the AI generates content:

- `generate_resume.txt` - Controls how resumes are tailored
- `generate_cover_letter.txt` - Controls cover letter generation
- `convert_resume_to_latex.txt` - Controls LaTeX formatting
- `verify_latex_resume.txt` - Controls verification criteria and strictness

### Using Different AI Models

Edit `config.json` to use different Poe AI models for different tasks. For example:

- Use `Claude-3.7-Sonnet` for cover letters (better at creative writing)
- Use `Gemini-2.5-Pro` for resume generation (better at structured data)
- Use `GPT-4o` for LaTeX conversion (better at formatting)
- Use `Gemini-2.5-Pro` for verification (good at fact-checking)

### Manual LaTeX Editing

If you need to manually edit the LaTeX file:

1. Find the `.tex` file in the `debug/` subdirectory
2. Edit it with your preferred LaTeX editor
3. Compile manually:
   ```bash
   cd output/[job_directory]
   cp ../../resume.cls .
   pdflatex debug/[Company]_[JobTitle]_Resume.tex
   ```

### Adjusting Verification Strictness

Edit `prompts/verify_latex_resume.txt` to adjust:

- What constitutes a "blatant lie" vs. acceptable embellishment
- Quality standards for formatting and spacing
- Minimum quality score threshold

## Pipeline Architecture

The pipeline follows a sequential processing model:

```
1. Load Configuration & Master Data
   ↓
2. Find Pending Job
   ↓
3. Select Best Cover Letter Point (keyword matching)
   ↓
4. Generate Tailored Resume (AI)
   ↓
5. Generate Cover Letter (AI)
   ↓
6. Convert Resume to LaTeX (AI)
   ↓
7. Verify LaTeX Resume (AI)
   ↓ (if verification passes)
8. Compile LaTeX to PDF (pdflatex)
   ↓
9. Organize Output Files
   ↓
10. Update Job Status to "processed"
```

If any step fails, the pipeline halts and displays an error message. This ensures you never submit incorrect or low-quality materials.

## License

This project is for personal use. Modify and extend as needed for your job search automation.

## Contributing

Feel free to fork this repository and customize it for your needs. Some ideas for enhancements:

- Add support for multiple resume formats (HTML, Markdown, etc.)
- Implement batch processing for multiple jobs
- Add email integration to automatically send applications
- Create a web interface for easier job entry
- Add analytics to track application success rates
