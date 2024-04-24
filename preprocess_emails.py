import csv
import re

def clean_email(text):
    # Define patterns to remove, including specific footer elements
    footer_patterns = [
        r"\n--\n",  # Standard email signature split
        r"\n__\n",  # Another common signature delimiter
        r"\nRegards,",  # Common closing
        r"\nKind regards,",  # Common closing
        r"\nkind regards,",  # Common closing
        r"\nBest,",  # Common closing
        r"\nbest,",  # Common closing
        r"\nAll the best,",  # Common closing
        r"\nThanks,",  # Common closing
        r"\nthanks,",  # Common closing
        r"\nBest regards,",  # Another common closing
        r"\nSincerely,",  # Another common closing
        r"\nThank you,",  # Another common closing
        # Add specific patterns for personalized footers
        r"\nAll the best,\s+Jack\s+--\s+Jack Rich",  # Custom pattern for your signature
        r"Senior Product Manager",  # Titles and positions
        r"Barcelona",  # Location details
        r"Mobile: \+\d{2,3} \d{6,10}",  # Phone numbers, adjust regex according to actual phone number formats
        r"LinkedIn:\s+",  # LinkedIn followed by potential URL or just space
        r"Email:\s+"  # Email keyword followed by space
        # Jack Rich  Senior Product Manager Barcelona  Mobile: +34 623101789 LinkedIn: https://uk.linkedin.com/in/jackrich7 Email: Jackrich78@gmail.com
    ]
    
    # Combine all patterns into a single regex to run once
    combined_pattern = "|".join(footer_patterns)
    text = re.split(combined_pattern, text, 1)[0]
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove email addresses
    text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '', text)
    # Optionally, truncate long emails
    text = text[:2000] if len(text) > 2000 else text
    return text

def preprocess_emails(input_csv_path, output_csv_path):
    with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Cleaned_Body']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            clean_text = clean_email(row['Body'])
            row['Cleaned_Body'] = clean_text
            writer.writerow(row)

if __name__ == "__main__":
    input_csv_path = 'data/past_email_filtered.csv'  # Path to the input CSV file
    output_csv_path = 'data/past_email_preprocessed_raw.csv'  # Path to save the cleaned CSV file
    preprocess_emails(input_csv_path, output_csv_path)
