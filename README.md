# Job Application Automation Pipeline

This project automates the tedious process of creating tailored resumes and cover letters for job applications. It is designed as a robust pipeline that uses a single master file as its database, processes jobs one by one, and leverages AI to generate high-quality, personalized application materials.

## Core Philosophy

The design of this project is guided by three core principles:

1.  **A Single Source of Truth:** All job application data, including the raw job descriptions, lives in one master file: `applications.yml`. This eliminates the need to manage separate input files for each job, creating a scalable and maintainable database of all your prospects.
2.  **Hassle-Free Data Entry:** Using the YAML format allows for raw, multi-line text blocks (`job_description: |`). You can copy and paste a job description directly from a website without any manual formatting or escaping of special characters.
3.  **Intelligent Automation, Not Just Generation:** The system doesn't just generate generic documents. It intelligently selects the most relevant personal story for each cover letter by analyzing the job description for keywords. This provides strategic personalization without requiring manual intervention for each job.

## Features

- **Queue-Based Processing:** The script automatically finds the next job with `status: "pending"` and processes it.
- **Persistent Job Archive:** Stores the full, original job description for every application, protecting you from postings being taken down.
- **Automated Cover Letter Personalization:** Intelligently selects from a bank of your personal stories (`cover_letter_points.json`) based on keyword matching against the job description.
- **YAML Database:** A human-readable and easy-to-edit master file for all your jobs.
- **Idempotent:** Once a job is `processed`, the script will ignore it on subsequent runs, allowing you to safely re-run the pipeline at any time.

## File Structure

```
.
├── .gitignore
├── applications.yml              # <-- YOUR MASTER JOB DATABASE. This is the main file you will edit.
├── profile/
│   └── cover_letter_points.json  # <-- Your personal story bank with keywords.
├── prompts/
│   ├── generate_cover_letter.txt # <-- Prompt for generating the cover letter.
│   └── tailor_resume.txt         # <-- Prompt for tailoring the resume.
├── requirements.txt
└── src/
    └── main.py                   # <-- The main script that runs the pipeline.
```

## Setup and Installation

1.  **Clone the Repository:**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
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

    This will install `PyYAML` and any other required libraries (e.g., `openai`).

4.  **Set Up API Keys:**
    It is highly recommended to use environment variables for your API keys. Create a `.env` file in the root directory (and make sure `.env` is in your `.gitignore` file).
    ```
    # .env
    OPENAI_API_KEY="your_api_key_here"
    ```
    Your Python script (`main.py`) should be configured to load this key.

## Daily Workflow

Your entire workflow consists of just two simple steps: adding a job and running the script.

### Step 1: Add a New Job to `applications.yml`

Open `applications.yml` and add a new entry at the top of the list.

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

- job_id: "add58865-8b9f-4cf7-9720-2908ba5f4d80"
  job_title: "Software Engineer, Infrastructure, Early Career"
  company_name: "Notion"
  status: "processed" # This job will be skipped by the script
  job_description: |
    About Us:
    Notion helps you build beautiful tools for your life’s work...
```

### Step 2: Run the Pipeline

Execute the main script from your terminal:

```bash
python src/main.py
```

### What Happens Next

The script will:

1.  Find the first job in `applications.yml` with `status: "pending"` (the Cyberdyne Systems job in our example).
2.  Read its job description and automatically select the best personal story from `profile/cover_letter_points.json` by matching keywords.
3.  Call the AI API to generate the tailored resume and cover letter.
4.  Save the output files to an `output/` directory, named with the `job_id`.
5.  **Crucially, it will then update `applications.yml` in-place, changing the job's status from `pending` to `processed`.**

The next time you run the script, it will skip the Cyberdyne job and look for the next `pending` one.

## Customizing Your Narrative

To make the automation more effective, you can customize your personal story bank in `profile/cover_letter_points.json`.

- **`point_text`**: The actual story or statement you want to include in your cover letter.
- **`keywords`**: A list of words that, if found in a job description, make this story relevant. The script will pick the story with the most keyword matches.
- **`default`**: Set `true` for one (and only one) point. This will be the fallback option if no keywords are matched.

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
