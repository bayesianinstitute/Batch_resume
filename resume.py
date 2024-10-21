import os
import argparse
import pandas as pd
import csv
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API key
api_key = os.getenv("MY_GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("Please set the MY_GEMINI_API_KEY environment variable in your .env file.")
genai.configure(api_key=api_key)

# Initialize the Google Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Function to extract text from a TXT file
def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to parse extraction result with error handling for incomplete fields
def parse_extraction_result(response_text):
    details = {}
    for line in response_text.split('\n'):
        if line.startswith("First Name:"):
            details['First Name'] = line.split(":", 1)[1].strip()
        elif line.startswith("Last Name:"):
            details['Last Name'] = line.split(":", 1)[1].strip()
        elif line.startswith("Location:"):
            details['Location'] = line.split(":", 1)[1].strip()
        elif line.startswith("Designation:"):
            details['Designation'] = line.split(":", 1)[1].strip()
        elif line.startswith("Email:"):
            details['Email'] = line.split(":", 1)[1].strip()
        elif line.startswith("Phone:"):
            details['Phone'] = line.split(":", 1)[1].strip()
        elif line.startswith("Recommendation:"):
            if 'Recommendation' in details:
                details['Recommendation'] += " " + line.split(":", 1)[1].strip()
            else:
                details['Recommendation'] = line.split(":", 1)[1].strip()
        elif line.startswith("Score:"):
            score_value = line.split(":", 1)[1].strip()
            if score_value.isdigit():
                details['Score'] = score_value
            else:
                details['Score'] = '45'  # Default to 45 if score is not numeric

    # Set default score to 45 if Score is missing
    if 'Score' not in details:
        print("Warning: Score not found in response. Defaulting to 45.")
        details['Score'] = '45'  # Default to 45 if Score is missing

    return details

# Function to retry model if score is zero
def get_valid_score_response(prompt):
    retry = True
    while retry:
        response = model.generate_content(prompt)
        parsed_result = parse_extraction_result(response.text)

        # Check if the score is zero or missing
        score = parsed_result.get('Score', '0')
        if score.isdigit() and int(score) > 0:
            retry = False  # Exit loop if score is valid and non-zero
        else:
            print("Score is zero, retrying the model...")

        # If retry fails, set to 45 after loop
        if retry == False and int(score) == 0:
            parsed_result['Score'] = '45'

    return parsed_result

# Main function to process resumes and job descriptions
def process_files(resume_folder, job_description_folder, output_csv):
    processed_data = []

    for resume_file in os.listdir(resume_folder):
        if resume_file.endswith('.pdf'):
            resume_path = os.path.join(resume_folder, resume_file)
            resume_text = extract_text_from_pdf(resume_path)

            for jd_file in os.listdir(job_description_folder):
                if jd_file.endswith('.txt'):
                    jd_path = os.path.join(job_description_folder, jd_file)
                    job_text = extract_text_from_txt(jd_path)
                    job_company = job_text.split('\n', 1)[0].strip()

                    # Create the prompt for generating a recommendation and score
                    combined_prompt = (
                        f"Extract and summarize the following details from this resume:\n"
                        f"First Name, Last Name, Location, Designation, Email, Phone\n\n"
                        f"After extracting these details, analyze the resume's relevance to the job description "
                        f"for a position at {job_company}. Provide one concise recommendation based on this analysis, "
                        f"and a suitability score (1-100).\n\n"
                        f"Job Description:\n{job_text}\n\n"
                        f"Resume Content:\n{resume_text}\n\n"
                        "Please respond in the following format:\n"
                        "First Name: <First Name>\n"
                        "Last Name: <Last Name>\n"
                        "Location: <Location>\n"
                        "Designation: <Designation>\n"
                        "Email: <Email>\n"
                        "Phone: <Phone>\n"
                        "Recommendation: <One Recommendation>\n"
                        "Score: <1-100>"
                    )

                    # Retrieve a valid response with non-zero score or default to 45
                    result_entry = get_valid_score_response(combined_prompt)
                    result_entry.update({'Job Company': job_company})
                    processed_data.append(result_entry)

    output_df = pd.DataFrame(processed_data)
    if os.path.isfile(output_csv):
        existing_df = pd.read_csv(output_csv)
        output_df = pd.concat([existing_df, output_df], ignore_index=True)
    output_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Output saved to {output_csv}")

# Set up argument parser for command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process resumes and job descriptions.")
    parser.add_argument("resume_folder", type=str, help="Path to the folder containing resume files.")
    parser.add_argument("job_description_folder", type=str, help="Path to the folder containing job description files.")
    parser.add_argument("-o", "--output", type=str, default="output.csv", help="Output CSV file name (default: output.csv)")

    args = parser.parse_args()

    # Run the process
    process_files(args.resume_folder, args.job_description_folder, args.output)
