# Configuration Guide

## Overview

Jobbernaut Tailor uses a combination of environment variables and a JSON configuration file to control its behavior. This document explains all configuration options and how to set them up correctly.

## Configuration Files

### 1. Environment Variables (.env)

The `.env` file stores sensitive credentials that should never be committed to version control.

#### Required Variables

**POE_API_KEY**
- **Purpose**: Authentication for Poe API access
- **How to Get**: 
  1. Visit [poe.com](https://poe.com)
  2. Log in to your account
  3. Go to Settings → API Keys
  4. Generate a new API key
- **Format**: String (typically starts with `poe-`)
- **Example**: `POE_API_KEY=poe-abcdef1234567890`

#### Creating the .env File

Create a file named `.env` in the project root directory:

```bash
# .env file
POE_API_KEY=your_actual_api_key_here
```

**Security Note**: The `.env` file is listed in `.gitignore` to prevent accidental commits. Never share your API key publicly.

---

### 2. Configuration File (config.json)

The `config.json` file controls AI model selection, humanization settings, and referral contact information.

#### Complete Configuration Structure

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
  "humanization": {
    "enabled": false,
    "level": "low",
    "apply_to": ["resume", "cover_letter"]
  },
  "referral_resume": {
    "email": "alternative@email.com",
    "phone": "555-0123"
  }
}
```

---

## Configuration Sections

### resume_generation

Controls the AI model used for generating tailored resume JSON.

#### bot_name
- **Type**: String
- **Purpose**: Specifies which Poe AI bot to use for resume generation
- **Available Options**:
  - `"Claude-Sonnet-4.5"` - Anthropic's Claude Sonnet 4.5 (excellent reasoning)
  - `"Gemini-2.5-Pro"` - Google's Gemini 2.5 Pro (strong technical understanding)
  - `"GPT-4o"` - OpenAI's GPT-4o (balanced performance)
  - `"GPT-4o-Mini"` - OpenAI's GPT-4o Mini (faster, cost-effective)
- **Recommendation**: `"Gemini-2.5-Pro"` for technical resumes
- **Default**: `"Gemini-2.5-Pro"`

#### thinking_budget
- **Type**: String (number as string)
- **Purpose**: Maximum tokens allocated for AI reasoning/thinking
- **Range**: "0" to "32768"
- **Recommendation**: "8192" for complex resume tailoring
- **Default**: "8192"
- **Note**: Higher values allow more thorough analysis but may increase latency

#### web_search
- **Type**: Boolean
- **Purpose**: Enable/disable web search for company research
- **Options**: `true` or `false`
- **Recommendation**: `true` to research company details and industry trends
- **Default**: `true`
- **Note**: Helps AI understand company culture and tailor content accordingly

---

### intelligence_steps (V4)

Controls the AI models used for the three intelligence gathering steps that precede resume generation.

#### job_resonance_analysis
- **Type**: Object
- **Purpose**: Configuration for analyzing job description to extract key requirements
- **bot_name**: Which AI model to use for job analysis
  - **Recommendation**: `"Gemini-2.5-Pro"` for structured extraction
  - **Default**: `"Gemini-2.5-Pro"`
- **thinking_budget**: Tokens allocated for analysis
  - **Recommendation**: `"4096"` for thorough requirement extraction
  - **Default**: `"4096"`

#### company_research
- **Type**: Object
- **Purpose**: Configuration for researching company culture, values, and positioning
- **bot_name**: Which AI model to use for company research
  - **Recommendation**: `"Gemini-2.5-Pro"` with web search capabilities
  - **Default**: `"Gemini-2.5-Pro"`
- **thinking_budget**: Tokens allocated for research
  - **Recommendation**: `"4096"` for comprehensive research
  - **Default**: `"4096"`

#### storytelling_arc
- **Type**: Object
- **Purpose**: Configuration for generating narrative structure for cover letter
- **bot_name**: Which AI model to use for narrative generation
  - **Recommendation**: `"Gemini-2.5-Pro"` for coherent storytelling
  - **Default**: `"Gemini-2.5-Pro"`
- **thinking_budget**: Tokens allocated for narrative creation
  - **Recommendation**: `"4096"` for compelling story development
  - **Default**: `"4096"`

**Note**: These intelligence steps run before resume/cover letter generation, providing context that makes the final documents more targeted and effective.

---

### cover_letter_generation

Controls the AI model used for generating cover letters.

#### bot_name
- **Type**: String
- **Purpose**: Specifies which Poe AI bot to use for cover letter writing
- **Available Options**: Same as resume_generation
- **Recommendation**: `"Claude-Sonnet-4.5"` for natural, persuasive writing
- **Default**: `"Claude-Sonnet-4.5"`
- **Note**: Claude excels at creative writing and persuasive communication

#### thinking_budget
- **Type**: String (number as string)
- **Purpose**: Maximum tokens for AI reasoning when writing cover letters
- **Range**: "0" to "32768"
- **Recommendation**: "2048" (cover letters require less complex reasoning)
- **Default**: "2048"

#### web_search
- **Type**: Boolean
- **Purpose**: Enable/disable web search for company research
- **Options**: `true` or `false`
- **Recommendation**: `true` to personalize cover letters with company details
- **Default**: `true`

---

### humanization

Controls post-processing to make AI-generated content sound more natural.

#### enabled
- **Type**: Boolean
- **Purpose**: Enable/disable humanization processing
- **Options**: `true` or `false`
- **Recommendation**: `false` (AI models are already quite natural)
- **Default**: `false`
- **Note**: When enabled, adds an extra AI pass to "humanize" the content

#### level
- **Type**: String
- **Purpose**: Intensity of humanization when enabled
- **Options**:
  - `"low"` - Minimal changes, subtle improvements
  - `"medium"` - Moderate changes, more conversational tone
  - `"high"` - Significant changes, very casual tone
- **Recommendation**: `"low"` if enabled (maintains professionalism)
- **Default**: `"low"`
- **Note**: Only applies when `enabled: true`

#### apply_to
- **Type**: Array of strings
- **Purpose**: Which documents to humanize
- **Options**: `["resume"]`, `["cover_letter"]`, or `["resume", "cover_letter"]`
- **Recommendation**: `["resume", "cover_letter"]` if humanization is enabled
- **Default**: `["resume", "cover_letter"]`
- **Note**: Only applies when `enabled: true`

---

### defaults

Fallback bot configurations when specific settings aren't provided.

#### resume_bot
- **Type**: String
- **Purpose**: Default bot for resume generation if not specified elsewhere
- **Default**: `"Gemini-2.5-Pro"`

#### cover_letter_bot
- **Type**: String
- **Purpose**: Default bot for cover letter generation if not specified elsewhere
- **Default**: `"Claude-Sonnet-4.5"`

---

### reasoning_trace

Controls whether to output detailed reasoning traces during processing.

- **Type**: Boolean
- **Purpose**: Enable/disable verbose reasoning output for debugging
- **Options**: `true` or `false`
- **Recommendation**: `false` (only enable for debugging)
- **Default**: `false`
- **Note**: When enabled, shows detailed AI reasoning steps in logs

---

### referral_resume

Alternate contact information for referral versions of documents.

#### email
- **Type**: String
- **Purpose**: Alternative email address for referral documents
- **Use Case**: When applying through a referral, you might want to use a different email
- **Example**: `"alternative@email.com"`
- **Default**: `"alternative@email.com"`
- **Note**: Referral PDFs are generated automatically with this contact info

#### phone
- **Type**: String
- **Purpose**: Alternative phone number for referral documents
- **Use Case**: Separate phone number for referral applications
- **Example**: `"555-0123"`
- **Default**: `"555-0123"`
- **Note**: Update this to your actual alternative contact information

---

## Available AI Models (Poe Bots)

### Claude-Sonnet-4.5
- **Provider**: Anthropic
- **Strengths**: Excellent reasoning, natural writing, strong instruction following
- **Best For**: Cover letters, creative content, persuasive writing
- **Speed**: Moderate
- **Cost**: Higher tier

### Gemini-2.5-Pro
- **Provider**: Google
- **Strengths**: Technical understanding, structured output, web search integration
- **Best For**: Resume generation, technical content, research-heavy tasks
- **Speed**: Fast
- **Cost**: Mid tier

### GPT-4o
- **Provider**: OpenAI
- **Strengths**: Balanced performance, versatile, reliable
- **Best For**: General purpose, when you need consistency
- **Speed**: Moderate
- **Cost**: Higher tier

### GPT-4o-Mini
- **Provider**: OpenAI
- **Strengths**: Fast, cost-effective, good for simple tasks
- **Best For**: Quick iterations, testing, budget-conscious usage
- **Speed**: Very fast
- **Cost**: Lower tier

---

## Configuration Examples

### Example 1: High-Quality, Research-Focused

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

**Use Case**: Maximum quality, thorough company research, willing to wait longer for results.

---

### Example 2: Fast, Cost-Effective

```json
{
  "resume_generation": {
    "bot_name": "GPT-4o-Mini",
    "thinking_budget": "2048",
    "web_search": false
  },
  "cover_letter_generation": {
    "bot_name": "GPT-4o-Mini",
    "thinking_budget": "1024",
    "web_search": false
  },
  "intelligence_steps": {
    "job_resonance_analysis": {
      "bot_name": "GPT-4o-Mini",
      "thinking_budget": "2048"
    },
    "company_research": {
      "bot_name": "GPT-4o-Mini",
      "thinking_budget": "2048"
    },
    "storytelling_arc": {
      "bot_name": "GPT-4o-Mini",
      "thinking_budget": "2048"
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
    "resume_bot": "GPT-4o-Mini",
    "cover_letter_bot": "GPT-4o-Mini"
  },
  "reasoning_trace": false
}
```

**Use Case**: Quick iterations, testing, or when applying to many jobs rapidly.

---

### Example 3: Humanized Output

```json
{
  "resume_generation": {
    "bot_name": "Claude-Sonnet-4.5",
    "thinking_budget": "8192",
    "web_search": true
  },
  "cover_letter_generation": {
    "bot_name": "Claude-Sonnet-4.5",
    "thinking_budget": "4096",
    "web_search": true
  },
  "intelligence_steps": {
    "job_resonance_analysis": {
      "bot_name": "Claude-Sonnet-4.5",
      "thinking_budget": "4096"
    },
    "company_research": {
      "bot_name": "Claude-Sonnet-4.5",
      "thinking_budget": "4096"
    },
    "storytelling_arc": {
      "bot_name": "Claude-Sonnet-4.5",
      "thinking_budget": "4096"
    }
  },
  "humanization": {
    "enabled": true,
    "level": "medium",
    "apply_to": ["resume", "cover_letter"]
  },
  "referral_resume": {
    "email": "referral@email.com",
    "phone": "555-7777"
  },
  "defaults": {
    "resume_bot": "Claude-Sonnet-4.5",
    "cover_letter_bot": "Claude-Sonnet-4.5"
  },
  "reasoning_trace": false
}
```

**Use Case**: When you want extra-natural sounding content with a conversational tone.

---

## Troubleshooting

### "POE_API_KEY not found in environment"

**Problem**: The `.env` file is missing or the API key is not set.

**Solution**:
1. Create a `.env` file in the project root
2. Add `POE_API_KEY=your_actual_key_here`
3. Ensure there are no spaces around the `=` sign
4. Restart the application

---

### "Invalid bot name"

**Problem**: The specified bot name doesn't exist or is misspelled.

**Solution**:
1. Check the bot name spelling in `config.json`
2. Ensure it matches one of the available options exactly
3. Bot names are case-sensitive

---

### "Thinking budget must be a string"

**Problem**: The thinking_budget is set as a number instead of a string.

**Solution**:
Change `"thinking_budget": 8192` to `"thinking_budget": "8192"` (with quotes)

---

### Web search not working

**Problem**: Web search is enabled but not providing results.

**Solution**:
1. Verify your Poe API key has web search permissions
2. Check if the selected bot supports web search
3. Try a different bot that explicitly supports web search

---

### Referral documents have wrong contact info

**Problem**: Referral PDFs show default placeholder contact information.

**Solution**:
Update the `referral_resume` section in `config.json` with your actual alternative contact details.

---

## Best Practices

### Model Selection
- **Resume Generation**: Use Gemini-2.5-Pro for technical accuracy
- **Cover Letters**: Use Claude-Sonnet-4.5 for persuasive writing
- **Testing**: Use GPT-4o-Mini for quick iterations

### Thinking Budget
- **Complex Tasks**: 8192+ tokens for thorough analysis
- **Simple Tasks**: 2048 tokens for straightforward generation
- **Balance**: Higher budgets = better quality but slower processing

### Web Search
- **Enable** when applying to specific companies (research culture, values)
- **Disable** for generic applications or when speed is critical

### Humanization
- **Disable** by default (modern AI is already natural)
- **Enable** only if you notice overly formal or robotic language
- **Use "low" level** to maintain professionalism

### Referral Contact Info
- Keep a separate email/phone for referral applications
- Update immediately when you get new contact information
- Test by generating a referral document and verifying the contact details

---

## Configuration Validation

The system validates configuration on startup:
- Checks for required fields
- Validates data types
- Warns about deprecated settings
- Provides helpful error messages

If configuration is invalid, the system will:
1. Display a clear error message
2. Indicate which field is problematic
3. Suggest the correct format
4. Exit before processing any jobs

---

## Security Considerations

### API Key Protection
- Never commit `.env` file to version control
- Don't share your API key in screenshots or logs
- Rotate keys periodically for security
- Use environment-specific keys for different deployments

### Configuration File
- `config.json` can be committed (no sensitive data)
- Review before committing to avoid exposing personal info
- Use placeholder values in shared configurations

---

## Version History

- **v4.0** (October 2025): Current configuration system
  - Intelligence gathering phase configuration
  - Job resonance analysis settings
  - Company research configuration
  - Storytelling arc generation settings
  - Defaults section for fallback bots
  - Reasoning trace debugging option

- **v3.0** (October 2025): Previous configuration system
  - Poe API integration
  - Separate resume/cover letter model selection
  - Humanization controls
  - Referral document support
