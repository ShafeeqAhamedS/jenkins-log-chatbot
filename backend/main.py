from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import logging
import datetime
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict

from utils.general import (
    read_data_from_file,
    write_data_to_file,
    generate_random_identifier,
    search_logs
)
from utils.gemini import (
    extract_gemini_response,
    send_to_gemini_api,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

# Data model for uploading log data
class LogData(BaseModel):
    job_name: str
    build_number: str
    log: str

class ChatPrompt(BaseModel):
    prompt: str

class APIResponse(BaseModel):
    status_code: int
    response: str
    job_name: str | None = None
    build_number: str | None = None
    unique_key: str | None = None

class SearchResponse(BaseModel):
    results: dict[str, dict]

class HistoryResponse(BaseModel):
    status_code: int
    history: Optional[Dict[str, Dict[str, str]]]
    job_name: Optional[str]
    build_number: Optional[str]
    unique_key: Optional[str]

@app.get("/")
def read_root():
    """
    Root endpoint for the Jenkins Log Analysis Chatbot.
    """
    logging.info("Root endpoint accessed.")
    return {"message": "Welcome to the Jenkins Log Analysis Chatbot!"}

@app.get("/chat")
def get_chat_data():
    """
    Get the history of all Builds uploaded. Returns a dictionary of unique keys, Job Name and build numbers.
    """
    logging.info("Fetching history of all builds.")
    try:
        logs_data = read_data_from_file()
        if not logs_data:
            logging.info("No build history found.")
            return {"message": "No build history found."}
        
        result = []
        for job_id, job_data in logs_data.items():
            latest_time = max(job_data.get("history", {}).keys(), default=None)
            result.append({
                "uniqueKey": job_id,
                "job_name": job_data.get("job_name"),
                "build_number": job_data.get("build_number"),
                "latest_time": latest_time
            })
        return result
    except FileNotFoundError:
        logging.error("Log file not found.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Log file not found.")
    except Exception as e:
        logging.error(f"Error fetching build history: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching build history.")

@app.post("/chatbot", response_model=APIResponse)
def chatbot_general(chat_prompt: ChatPrompt):
    """
    General chatbot endpoint for non-log-related interactions (now via POST).
    """
    logging.info("General chatbot endpoint accessed.")
    logs_data = read_data_from_file()
    unique_key = generate_random_identifier(chat_prompt.prompt)
    combined_text = f"query={chat_prompt.prompt}"

    try:
        gemini_response = send_to_gemini_api(combined_text)
        if gemini_response["status_code"] != 200:
            raise HTTPException(status_code=gemini_response["status_code"], detail=gemini_response["response"])
        processed_text = gemini_response["response"]
        history_key = str(int(datetime.datetime.now().timestamp()))
        logs_data[unique_key] = {
            "job_name": "Query",
            "build_number": datetime.datetime.now().strftime("%d-%m-%Y - %I:%M %p"),
            "log": None,
            "memory": f"User: {chat_prompt.prompt}\nGemini: {processed_text}",
            "history": {
                history_key: {
                    "user": chat_prompt.prompt,
                    "gemini": processed_text
                }
            }
        }
        write_data_to_file(logs_data)
    except Exception as e:
        logging.error(f"Error in general chatbot endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return APIResponse(status_code=status.HTTP_200_OK, response=processed_text, unique_key=unique_key)

@app.post("/chatbot/load", response_model=APIResponse)
def load_log(data: LogData):
    """
    Upload log data and create a unique encrypted identifier for accessing it.
    """
    logging.info(f"Loading log data for job: {data.job_name}, build: {data.build_number}")
    logs_data = read_data_from_file()
    unique_key = generate_random_identifier(f"{data.job_name}_{data.build_number}")

    logs_data[unique_key] = {
        "job_name": data.job_name,
        "build_number": data.build_number,
        "log": data.log,
    }

    write_data_to_file(logs_data)

    route_url = f"/chatbot/{unique_key}"
    logging.info(f"Log uploaded successfully. Access it via {route_url}")
    return APIResponse(status_code=status.HTTP_201_CREATED, response=f"Log uploaded successfully. Access it via {route_url}", job_name=data.job_name, build_number=data.build_number, unique_key=unique_key)

@app.post("/chatbot/{unique_key}", response_model=APIResponse)
def chatbot_specific_log(unique_key: str, chat_prompt: ChatPrompt):
    """
    Access the chatbot with a specific log, include user prompt, and integrate with GEMINI.
    """
    logging.info(f"Accessing chatbot for specific log with key: {unique_key}")
    logs_data = read_data_from_file()
    log_data = logs_data.get(unique_key)
    if not log_data:
        logging.error(f"Log not found for key: {unique_key}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    memory = log_data.get("memory", "")
    if not memory:
        combined_text = f"log={log_data['log']}\nquery={chat_prompt.prompt}"
        log_data["memory"] = log_data['log']
    else:
        combined_text = f"memory={memory}\nquery={chat_prompt.prompt}"

    try:
        gemini_response = send_to_gemini_api(combined_text)
        if gemini_response["status_code"] != 200:
            raise HTTPException(status_code=gemini_response["status_code"], detail=gemini_response["response"])
        processed_text = gemini_response["response"]
        log_data["memory"] += f"\nUser: {chat_prompt.prompt}\nGemini: {processed_text}"
        history_key = str(int(datetime.datetime.now().timestamp()))
        log_data["history"][history_key] = {
            "user": chat_prompt.prompt,
            "gemini": processed_text
        }
        logs_data[unique_key] = log_data
        write_data_to_file(logs_data)
    except Exception as e:
        logging.error(f"Error in specific log chatbot endpoint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return APIResponse(status_code=status.HTTP_200_OK, response=processed_text, job_name=log_data["job_name"], build_number=log_data["build_number"])

@app.get("/logs/{job_name}/{build_number}", response_model=APIResponse)
def get_log_by_job_and_build(job_name: str, build_number: str):
    """
    Get the log for a specific job and build number.
    """
    logging.info(f"Fetching log for job: {job_name}, build: {build_number}")
    logs_data = read_data_from_file()
    for key, log_data in logs_data.items():
        if log_data["job_name"] == job_name and log_data["build_number"] == build_number:
            return APIResponse(status_code=status.HTTP_200_OK, response=log_data["log"], job_name=job_name, build_number=build_number)
    logging.error(f"Log not found for job: {job_name}, build: {build_number}")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

@app.get("/search", response_model=SearchResponse)
def search_logs_endpoint(keyword: str):
    """
    Search logs by keyword or phrase to locate specific data.
    """
    logging.info(f"Search endpoint accessed with keyword: {keyword}")
    try:
        results = search_logs(keyword)
        if not results:
            return SearchResponse(results={})
        return SearchResponse(results=results)
    except Exception as e:
        logging.error(f"Error during search: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while searching logs.")

@app.get("/history/{unique_key}", response_model=HistoryResponse)
def get_history(unique_key: str):
    """
    Retrieve the chat history for a given unique key.
    """
    logging.info(f"Retrieving history for unique_key: {unique_key}")
    try:
        logs_data = read_data_from_file()
        log_entry = logs_data.get(unique_key)
        if not log_entry:
            logging.warning(f"No log found for unique_key: {unique_key}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found for the provided unique key.")
        
        history = log_entry.get("history", {})
        if not history:
            logging.info(f"No history available for unique_key: {unique_key}")
            return HistoryResponse(
                status_code=status.HTTP_200_OK,
                history={},
                job_name=log_entry.get("job_name"),
                build_number=log_entry.get("build_number"),
                unique_key=unique_key
            )
        
        logging.info(f"History retrieved successfully for unique_key: {unique_key}")
        return HistoryResponse(
            status_code=status.HTTP_200_OK,
            history=history,
            job_name=log_entry.get("job_name"),
            build_number=log_entry.get("build_number"),
            unique_key=unique_key
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Error retrieving history for unique_key {unique_key}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving the history.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)