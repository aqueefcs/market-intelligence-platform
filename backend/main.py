from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os
import requests
from backend.analytics import calculate_financial_metrics

# Build the exact path to the .env file inside the backend folder
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize the FastAPI app
app = FastAPI(title="Market Intelligence Platform API")

# Fetch the MongoDB URL from the environment variables
MONGO_URL = os.getenv("MONGODB_URL")

try:
    # Connect to the MongoDB cluster
    client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
    
    # Define our database name (MongoDB creates it automatically later)
    db = client["market_intelligence"]
    
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")

# A simple test route
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Market Intelligence API!", 
        "database_status": "Connected"
    }

# --- STEP 3.2: Pydantic Models (Schemas) ---
# These define what our API expects to send and receive
class IngestionResponse(BaseModel):
    message: str
    ticker: str

# --- STEP 3.3: Data Ingestion Endpoint ---
@app.post("/ingestion/company/{ticker}", response_model=IngestionResponse)
def ingest_company_data(ticker: str):
    ticker = ticker.upper()
    api_key = os.getenv("FMP_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="FMP API Key not configured")

    # 1. Fetch Company Profile
    profile_url = f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={api_key}"
    profile_response = requests.get(profile_url)
    
    if profile_response.status_code != 200 or not profile_response.json():
        raise HTTPException(status_code=404, detail=f"Could not fetch profile for {ticker}")
        
    company_data = profile_response.json()[0] # FMP returns a list, grab the first item

    # 2. Fetch Historical Stock Prices (Last 5 years by default)
    history_url = f"https://financialmodelingprep.com/stable/historical-price-eod/full?symbol={ticker}&apikey={api_key}"
    history_response = requests.get(history_url)
    
    historical_data = []
    if history_response.status_code == 200:
        historical_data = history_response.json()

    # 3. Store in MongoDB
    # We create a single document containing both the profile and the stock history
    document = {
        "ticker": ticker,
        "profile": company_data,
        "historical_prices": historical_data
    }
    
    # Update if exists, otherwise insert (Upsert)
    db.companies.update_one(
        {"ticker": ticker},
        {"$set": document},
        upsert=True
    )

    return {"message": "Data successfully ingested and stored in MongoDB", "ticker": ticker}

# --- STEP 3.4: Retrieve Company Data Endpoint ---
@app.get("/companies/{ticker}")
def get_company_data(ticker: str):
    ticker = ticker.upper()
    
    # Search MongoDB for the company
    # We use {"_id": 0} to hide the MongoDB internal ID, because FastAPI 
    # doesn't know how to convert MongoDB ObjectIds to JSON by default.
    company_data = db.companies.find_one({"ticker": ticker}, {"_id": 0})
    
    if not company_data:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}. Did you ingest it first?")
        
    return company_data

# --- STEP 4.2: Analytics Endpoint ---
@app.get("/companies/{ticker}/analytics")
def get_company_analytics(ticker: str):
    ticker = ticker.upper()
    company_data = db.companies.find_one({"ticker": ticker}, {"_id": 0})
    
    if not company_data or "historical_prices" not in company_data:
        raise HTTPException(status_code=404, detail="Data not found. Did you ingest it first?")
        
    metrics = calculate_financial_metrics(company_data["historical_prices"])
    
    return {
        "ticker": ticker,
        "company_name": company_data.get("profile", {}).get("companyName", "Unknown"),
        "metrics": metrics
    }

# --- STEP 4.3: List All Companies Endpoint (For Frontend Dropdown) ---
@app.get("/companies")
def get_all_companies():
    # Fetch only the ticker and name from MongoDB to keep the response fast and light
    companies = list(db.companies.find({}, {"_id": 0, "ticker": 1, "profile.companyName": 1}))
    return {"ingested_companies": companies}