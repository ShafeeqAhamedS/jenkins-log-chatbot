## Execute these commands

```sh
cd frontend
npm i
npm start
```

```sh
cd backend
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### ENV File
```
LOGS_DATA_FILE="Data_FILE"
GEMINI_API_KEY="API_KEY"
GEMINI_MODEL_NAME="modelVersion:generationMethod"
```
