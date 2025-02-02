import os
import json
import random
import string
import logging
from typing import Dict
from hashlib import sha256
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
DATA_FILE = os.environ.get("LOGS_DATA_FILE")

def read_data_from_file() -> Dict[str, Dict]:
    """
    Reads logs from a JSON file; returns an empty dict if file doesn't exist or can't be read.
    """
    if not os.path.exists(DATA_FILE):
        logging.warning(f"Data file {DATA_FILE} does not exist.")
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            logging.info(f"Reading data from {DATA_FILE}")
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to read data from {DATA_FILE}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Failed to read data from {DATA_FILE}: {e}")
        return {}

def write_data_to_file(data: Dict[str, Dict]):
    """
    Writes the given data dictionary to a JSON file.
    """
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
            logging.info(f"Data written to {DATA_FILE}")
    except Exception as e:
        logging.error(f"Failed to write data to {DATA_FILE}: {e}")

def generate_random_identifier(data: str) -> str:
    """
    Generate a unique and random identifier, ensuring it doesn't already exist in the JSON file.
    """
    logs_data = read_data_from_file()
    while True:
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed = sha256(f"{data}{random_suffix}".encode()).hexdigest()
        candidate = hashed[:12]
        if candidate not in logs_data:
            logging.info(f"Generated unique identifier: {candidate}")
            return candidate

def search_logs(keyword: str) -> Dict[str, Dict]:
    """
    Search logs for entries containing the given keyword or phrase.
    """
    logs_data = read_data_from_file()
    results = {key: value for key, value in logs_data.items() if keyword.lower() in json.dumps(value).lower()}
    logging.info(f"Search completed for keyword: {keyword}. Found {len(results)} results.")
    return results
