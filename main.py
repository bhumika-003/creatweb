from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from supabase import create_client, Client

# --- Environment Variables & API Clients ---
NLP_CLOUD_API_KEY = os.environ.get("NLP_CLOUD_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FastAPI App Initialization ---
app = FastAPI()

# Mount static files and configure CORS
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Review(BaseModel):
    product_name: str
    review_text: str
    rating: int

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.get("/summary")
async def read_summary_page():
    return FileResponse('static/summary.html')

@app.post("/submit-review")
async def submit_review(review: Review):
    """
    Accepts a review, stores it, and returns sentiment analysis.
    """
    try:
        # 1. Store the review in Supabase
        response = supabase.table('reviews').insert({
            "product_name": review.product_name,
            "review_text": review.review_text,
            "rating": review.rating
        }).execute()

        # 2. Perform sentiment analysis
        headers = {"Authorization": f"Token {NLP_CLOUD_API_KEY}"}
        payload = {"text": review.review_text}
        api_url = "https://api.nlpcloud.io/v1/distilbert-base-uncased-finetuned-sst-2-english/sentiment"
        
        sentiment_response = requests.post(api_url, headers=headers, json=payload)
        sentiment_response.raise_for_status()
        
        return sentiment_response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize/{product_name}")
async def summarize_product_reviews(product_name: str):
    """
    Summarizes all reviews for a given product and stores the summary.
    """
    try:
        # 1. Get all reviews for the product
        response = supabase.table('reviews').select('review_text').eq('product_name', product_name).execute()
        reviews = [item['review_text'] for item in response.data]

        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this product.")

        # 2. Summarize the reviews
        text_to_summarize = ". ".join(reviews)
        headers = {"Authorization": f"Token {NLP_CLOUD_API_KEY}"}
        payload = {"text": text_to_summarize}
        api_url = "https://api.nlpcloud.io/v1/bart-large-cnn/summarization"

        summary_response = requests.post(api_url, headers=headers, json=payload)
        summary_response.raise_for_status()
        summary_text = summary_response.json().get('summary_text')

        # 3. Store the summary in Supabase (upsert to create or update)
        supabase.table('summaries').upsert({
            "product_name": product_name,
            "summary_text": summary_text
        }, on_conflict='product_name').execute()

        return {"product_name": product_name, "summary": summary_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products")
async def get_products():
    """
    Returns a list of distinct product names from the reviews table using RPC function.
    """
    try:
        response = supabase.rpc('get_distinct_products', {}).execute()
        products = [item['product_name'] for item in response.data]
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary/{product_name}")
async def get_summary(product_name: str):
    """
    Retrieves the stored summary for a given product.
    """
    try:
        response = supabase.table('summaries').select('summary_text').eq('product_name', product_name).limit(1).single().execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Summary not found.")

