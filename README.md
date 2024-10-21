# Resume and Job Description Processing Script

## Overview

This script processes resumes and job descriptions by extracting key information from the resumes and analyzing them against specific job descriptions to generate a recommendation and suitability score. The output is saved in a CSV file.

## Features

- Extracts personal details from resumes (First Name, Last Name, Location, Designation, Email, Phone).
- Compares resumes against job descriptions and provides a recommendation along with a suitability score (1-100).
- Handles both PDF resumes and text-based job descriptions.
- Automatically retries for a valid score, defaulting to 45 if no valid score is generated.
- Outputs results into a CSV file with options for appending data if the file already exists.

## Prerequisites

Before running the script, ensure that the following Python packages are installed:

- `PyPDF2`
- `dotenv`
- `google.generativeai`
- `pandas`
- `argparse`

To install the required dependencies, run:

```bash
pip install PyPDF2 python-dotenv google-generativeai pandas argparse
```

You will also need a Google Gemini API key. Store the key in a `.env` file in the project directory with the following format:

```
MY_GEMINI_API_KEY=your_google_gemini_api_key
```

## Usage

### Command Line Arguments

The script accepts the following command-line arguments:

- `resume_folder`: Path to the folder containing resume files (PDF format).
- `job_description_folder`: Path to the folder containing job description files (TXT format).
- `-o`, `--output`: (Optional) The output CSV file name. Defaults to `output.csv`.

### Example Command

```bash
python script_name.py /path/to/resumes /path/to/job_descriptions -o output.csv
```

This command processes resumes in the `/path/to/resumes` folder and job descriptions in the `/path/to/job_descriptions` folder, saving the results to `output.csv`.

## Workflow

1. The script loads environment variables, including the API key for Google Gemini.
2. It initializes the `gemini-1.5-flash` model using the provided API key.
3. The script extracts text from PDF resumes and text files containing job descriptions.
4. It generates a combined prompt to compare the resume with the job description and obtain a recommendation and score.
5. The output is saved as a CSV file containing the extracted details and analysis.

## Output

The output CSV file will contain the following fields:

- First Name
- Last Name
- Location
- Designation
- Email
- Phone
- Recommendation
- Score
- Job Company

## Notes

- Ensure your `.env` file is correctly set up with the API key.
- The script will retry generating a score if the initial response returns a score of 0. The default score is set to 45 if no valid score is obtained.
- Existing output CSV files are automatically appended with new data.
