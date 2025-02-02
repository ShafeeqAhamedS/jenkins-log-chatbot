### Start Python Backend
```
uvicorn main:app --reload
```

### Create venv python
```
python3 -m venv venv
```

### Activate venv
```
venv\Scripts\activate
```

### Install requirements
```
pip install -r requirements.txt
```

### Save requirements
```
pip freeze > requirements.txt
```

### ENV File
```
LOGS_DATA_FILE="Data_FILE"
GEMINI_API_KEY="API_KEY"
GEMINI_MODEL_NAME="modelVersion:generationMethod" eg "gemini-1.5-flash:generateContent"
```