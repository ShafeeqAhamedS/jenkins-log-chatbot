import os
import requests
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME")
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}"

def extract_gemini_response(gemini_data: Dict) -> str:
    """
    Extract the text from the Gemini response.
    """
    try:
        logging.info("Extracting text from Gemini response")
        return gemini_data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        logging.error("Failed to extract text from Gemini response.")
        return "No text found in Gemini response."

def send_to_gemini_api(log_text: str) -> Dict[str, Any]:
    """
    Send log text to GEMINI API and return the response.
    """
    prompt_content = f"""
    Consider yourself a DevOps engineer specializing in Jenkins. You have two roles:
    Answer general Jenkins-related questions.
    Analyze Jenkins logs provided and give detailed feedback.
    Rules:
    If logs are provided, only analyze those logs and offer solutions or insights.
    If logs are not provided, answer any Jenkins-related questions directly.
    Keep your responses concise—limit most answers to 50 words. Offer more details only if requested.
    Memory:
    You will receive memory indicating previous conversations. Use it to provide context, but only respond with relevant information based on the logs or query given based on memory.
    User = {log_text}
    """
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_content}
                ]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(f"{api_url}?key={API_KEY}", headers=headers, json=payload)
        if response.status_code == 200:
            logging.info("Successfully received response from GEMINI API.")
            gemini_data = response.json()
            extracted_response = extract_gemini_response(gemini_data)
            return {"status_code": 200, "response": extracted_response}
        else:
            logging.error(f"Request failed with status code {response.status_code}: {response.text}")
            return {"status_code": response.status_code, "response": response.text}
    except Exception as e:
        logging.error(f"Exception occurred while sending request to GEMINI API: {e}")
        return {"status_code": 500, "response": str(e)}