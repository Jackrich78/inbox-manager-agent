import os
import logging
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
import json, csv

# set up logging
logging.basicConfig(filename='email_parsing_errors.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

load_dotenv(find_dotenv())

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def parse_email(email_thread):

    system_prompt = """
    You are an expert of convert raw email thread into original message / reply pairs. 
    You are given a raw email thread between Jack and others, your goal is to convert it into original message / reply pairs. 
    In some cases Jack may be the sender, if this is the case identify the entire message as 'jack_reply'.
    - orignal_message: the last message sent to Jack, if it is a long email thread, only take the last message
    - jack_reply: Jack's reply to the original message

    if there is only one message in the thread, that should be jack_reply

    The exported format should look something like 
    {
        "original_message": "xxxx",
        "jack_reply": "xxxx"
    }
    """

    response = client.chat.completions.create(  # updated to newer API version
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": email_thread}
        ],
        max_tokens=600
    )

    return response.choices[0].message.content

def process_csv(input_csv_path, output_csv_path):
    with open(input_csv_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        processed_data = []

        for row in csv_reader:
            text = row['Body']  # Get the text from the 'body' column
            try: # to review
                json_string = parse_email(text)
                print(json_string)
                json_data = json.loads(json_string)  # Convert JSON string to dictionary
                original_message = json_data.get('original_message', '')
                jack_reply = json_data.get('jack_reply', '')
                # Append original row data and new columns to processed_data
                processed_data.append([original_message, jack_reply])
                # logging successful categorisation
                logging.info(f"Successfully parsed email: {text[:200]}")
            except json.JSONDecodeError:
                # log parse failure
                logging.error(f"Failed to parse JSON for the email: {text[:200]}")
                continue  # skip this email or log the error for later review
            except Exception as e:
                # log any unexpected errors
                logging.error(f"Unexpected error {e} for email: {text[:200]}")
                continue

    # Write processed data to a new CSV file
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        csv_writer.writerow(['original_message', 'jack_reply'])
        # Write data rows
        csv_writer.writerows(processed_data)

if __name__ == "__main__":
    # Paths to your input and output CSV files
    input_csv_path = 'data/preprocess_clean_test.csv'
    output_csv_path = 'data/email_pairs.csv'

    # Call the function to process the CSV file
    process_csv(input_csv_path, output_csv_path)
