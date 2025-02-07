#Location - /var/lib/jenkins/jobs
import requests
import json
import argparse
import re

def summarize_console_output(console_output, api_key, api_url):
    """
    Send console output to Gemini API for summarization and return the response.
    """
    # Construct the prompt content
    prompt_content = (
        f"Analyze the following console output, identify the error type, and summarize it in the following format: "
        f"Error type: [error type - The major error only] Summary: [summary of the error]. \\n{console_output}"
    )

    # Construct the payload with the correct structure
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_content}
                ]
            }
        ]
    }

    # Set headers for the API request
    headers = {
        "Content-Type": "application/json",
    }

    # Send the request to the Gemini API
    response = requests.post(f"{api_url}?key={api_key}", headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        summary_text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Improved regex to handle potential extra spaces or line breaks
        match = re.search(r"Error type:\s*(.*?)\s*Summary:\s*(.*?)\s*(?=\n|$)", summary_text)

        if match:
            error_type = match.group(1).strip()
            summary = match.group(2).strip()

            # Create the JSON structure
            json_response = {
                "errorType": error_type,
                "summary": summary.replace("\\", "").replace("\\\\", "")
            }

            # Print the JSON response
            return (json.dumps(json_response, indent=4))
        else:
            print("No match found for Error type and Summary.")
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Summarize console output using Gemini API.")
    parser.add_argument("--value", required=True, help="Console output to summarize")
    parser.add_argument("--api_key", required=True, help="API key for the Gemini API")
    parser.add_argument("--api_url", required=True, help="URL for the Gemini API endpoint")

    # Parse arguments
    args = parser.parse_args()

    # Extract arguments
    console_output = args.value
    api_key = args.api_key
    api_url = args.api_url

    # Call the summarize function
    try:
        summary = summarize_console_output(console_output, api_key, api_url)
        print(summary)
    except Exception as e:
        print(f"Error: {e}")
