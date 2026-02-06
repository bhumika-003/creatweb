from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

NLP_CLOUD_API_KEY = os.environ.get("NLP_CLOUD_API_KEY", "YOUR_API_KEY")
NLP_CLOUD_API_URL = "https://api.nlpcloud.io/v1/distilbert-base-uncased-finetuned-sst-2-english/sentiment"

class Feedback(BaseModel):
    text: str

@app.post("/analyze-sentiment")
async def analyze_sentiment(feedback: Feedback):
    headers = {
        "Authorization": f"Token {NLP_CLOUD_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"text": feedback.text}
    
    try:
        response = requests.post(NLP_CLOUD_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')
