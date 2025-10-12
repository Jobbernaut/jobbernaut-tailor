# Job Application Automation Pipeline

This project automates the tedious process of creating tailored resumes and cover letters for job applications. It is designed as a robust pipeline that uses a single master file as its database, processes jobs one by one, and leverages AI to generate high-quality, personalized application materials.

## Core Philosophy

The design of this project is guided by three core principles:

1.  **A Single Source of Truth:** All job application data, including the raw job descriptions, lives in one master file: `applications.yaml`. This eliminates the need to manage separate input files for each job, creating a scalable and maintainable database of all your prospects.
2.  **Hassle-Free Data Entry:** Using the YAML format allows for raw, multi-line text blocks (`job_description: |`). You can copy and paste a job description directly from a website without any manual formatting or escaping of special characters.
3.  **Intelligent Automation, Not Just Generation:** The system doesn't just generate generic documents. It intelligently selects the most relevant personal story for each cover letter by analyzing the job description for keywords. This provides strategic personalization without requiring manual intervention for each job.

## Features

- **Queue-Based Processing:** The script automatically finds the next job with `status: "pending"` and processes it.
- **Persistent Job Archive:** Stores the full, original job description for every application, protecting you from postings being taken down.
- **Automated Cover Letter Personalization:** Intelligently selects from a bank of your personal stories (`master_cover_letter_points.json`) based on keyword matching against the job description.
- **Multiple Output Formats:** Generates both JSON and LaTeX versions of your tailored resume, plus PDF cover letters.
- **Configurable AI Models:** Use different AI models (via Poe API) for resume generation, LaTeX conversion, and cover letter writing.
- **YAML Database:** A human-readable and easy-to-edit master file for all your jobs.
- **Idempotent:** Once a job is `processed`, the script will ignore it on subsequent runs, allowing you to safely re-run the pipeline at any time.

## File Structure

```
.
├── .gitignore
├── applications.yaml              # <-- YOUR MASTER JOB DATABASE. This is the main file you will edit.
├── config.json                    # <-- Configuration for AI models and pipeline settings
├── requirements.txt
├── profile/
│   ├── master_resume.json         # <-- Your master resume data in JSON format
│   └── master_cover_letter_points.json  # <-- Your personal story bank with keywords
├── prompts/
│   ├── generate_resume.txt        # <-- Prompt template for generating tailored resumes
│   ├── generate_cover_letter.txt  # <-- Prompt template for generating cover letters
│   └── convert_resume_to_latex.txt # <-- Prompt template for LaTeX conversion
├── src/
│   ├── main.py                    # <-- The main pipeline script
│   └── utils.py                   # <-- Helper functions for file I/O and processing
└── output/                        # <-- Generated resumes and cover letters (auto-created)
    └── [job_id]/
        ├── [Company]_[Title]_Resume.json
        ├── [Company]_[Title]_Resume.tex
        └── [Company]_[Title]_CoverLetter.pdf
```

## Setup and Installation

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

4.  **Set Up API Keys:**

    Create a `.env` file in the root directory (and make sure `.env` is in your `.gitignore` file):

    ```
    # .env
    POE_API_KEY="your_poe_api_key_here"
    ```

    The pipeline uses the Poe API to access various AI models. You can get an API key from [Poe](https://poe.com/).

5.  **Configure Your Profile:**

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
  "cover_letter_generation": {
    "bot_name": "Gemini-2.5-Pro",
    "thinking_budget": "8192",
    "web_search": false
  },
  "reasoning_trace": false,
  "dry_run": false
}
```

- **bot_name:** The Poe AI model to use (e.g., "Gemini-2.5-Pro", "Claude-3.7-Sonnet", "GPT-4o")
- **thinking_budget:** Token budget for model reasoning
- **web_search:** Enable/disable web search capabilities for the model
- **reasoning_trace:** Show/hide AI reasoning traces in cover letters
- **dry_run:** Test mode (not fully implemented)

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

1.  Find the first job in `applications.yaml` with `status: "pending"` (the Cyberdyne Systems job in our example).
2.  Read its job description and automatically select the best personal story from `profile/master_cover_letter_points.json` by matching keywords.
3.  Call the Poe API to generate a tailored resume in JSON format using your master resume data.
4.  Convert the tailored resume JSON to LaTeX format for professional typesetting.
5.  Generate a personalized cover letter as a PDF document.
6.  Save all outputs to the `output/[job_id]/` directory with descriptive filenames.
7.  **Crucially, it will then update `applications.yaml` in-place, changing the job's status from `pending` to `processed`.**

The next time you run the script, it will skip the Cyberdyne job and look for the next `pending` one.

## Output Files

For each processed job, the pipeline creates a directory under `output/` with the following files:

- **`[Company]_[Title]_Resume.json`** - Tailored resume in JSON format
- **`[Company]_[Title]_Resume.tex`** - Tailored resume in LaTeX format (ready to compile)
- **`[Company]_[Title]_CoverLetter.pdf`** - Cover letter as a PDF document

Example: `output/AMZ26535.1/Amazon Web Services_Software Dev Engineer II_Resume.json`

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
- `professional_summaries`: Different summary statements for various roles
- `work_experience`: All your work history with detailed accomplishments
- `skills`: Technical skills, tools, frameworks, etc.
- `education`: Degrees and certifications
- `projects`: Personal or academic projects (optional)

The AI will intelligently select and tailor content from this master file based on the job description.

## Troubleshooting

- **No pending jobs found:** All jobs in `applications.yaml` have `status: "processed"`. Add a new job with `status: "pending"`.
- **API errors:** Check that your `POE_API_KEY` is correctly set in the `.env` file and that you have API credits.
- **JSON parsing errors:** The AI response may not be properly formatted. Try adjusting the `bot_name` in `config.json` or check the prompt templates.
- **Missing output files:** Check the console output for errors during the pipeline execution.

## Advanced Usage

### Customizing Prompts

You can modify the prompt templates in the `prompts/` directory to change how the AI generates content:

- `generate_resume.txt` - Controls how resumes are tailored
- `generate_cover_letter.txt` - Controls cover letter generation
- `convert_resume_to_latex.txt` - Controls LaTeX formatting

### Using Different AI Models

Edit `config.json` to use different Poe AI models for different tasks. For example:

- Use `Claude-3.7-Sonnet` for cover letters (better at creative writing)
- Use `Gemini-2.5-Pro` for resume generation (better at structured data)
- Use `GPT-4o` for LaTeX conversion (better at formatting)

## License

This project is for personal use. Modify and extend as needed for your job search automation.
