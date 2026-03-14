# 📈 Market Intelligence Platform

**Live Dashboard:** [Insert Streamlit App URL Here]  
**Live API Docs:** [Insert Render API /docs URL Here]

## 🎯 Overview

**For the Business / Layperson:**
The Market Intelligence Platform is an automated financial analysis tool. It pulls historical stock market data and company profiles from the internet, stores them securely in a cloud database, and acts like an instant financial analyst. Instead of just showing charts, it calculates complex momentum indicators and instantly simulates trading strategies (like buying when a stock is "oversold") to see exactly how much money that strategy would have made over the last 5 years compared to just holding the stock.

**For the Developer / Engineer:**
This is a decoupled, full-stack analytics system demonstrating external API ingestion, NoSQL document storage, and high-performance data processing. The backend exposes RESTful endpoints via FastAPI to ingest data from the Financial Modeling Prep (FMP) API, managing state via MongoDB Atlas with an `upsert` architecture to prevent data duplication. The analytics engine leverages pure Pandas vectorization to compute financial metrics (RSI, Volatility, Moving Averages) and execute algorithmic backtests in milliseconds, completely bypassing the computational overhead of iterative loops.

---

## 🏗️ System Architecture

````text
[External Data] FMP API
       │
       ▼  (REST GET)
[Backend API] FastAPI Ingestion Route
       │
       ▼  (PyMongo Upsert)
[Database] MongoDB Atlas (Cloud NoSQL)
       │
       ▼  (PyMongo Find)
[Backend API] FastAPI Analytics Engine (Pandas/NumPy)
       │
       ▼  (REST GET)
[Frontend] Streamlit Dashboard (Community Cloud)


Tech Stack
 - Backend: Python 3, FastAPI, Pydantic, Requests

 - Data Engineering & Math: Pandas, NumPy

 - Database: MongoDB Atlas (PyMongo)

 - Frontend: Streamlit

 - Deployment: Render (API Server), Streamlit Community Cloud (UI)


 🚀 Core Features & Technical Deep Dive
1. Automated Data Ingestion & Storage
Fetches live company metadata and multi-year historical price data.

Architecture Note: Uses MongoDB's update_one with upsert=True. This ensures the database is highly available and idempotently handles repeated ingestion requests without creating duplicate records or requiring complex relational migrations.

2. High-Performance Analytics Engine
Calculates standard financial metrics (Total Return, Annualized Volatility, 50-Day Moving Averages, and 14-Day RSI).

Architecture Note: All transformations are handled via Pandas DataFrames. Time-series data is explicitly typed and sorted by datetime indices to guarantee sequential integrity before applying rolling window functions.

3. Vectorized Algorithmic Backtesting
Simulates a systematic mean-reversion trading strategy (Buy when RSI < 30, Sell when RSI > 70).

Architecture Note: This engine avoids O(N) for loops entirely. It uses NumPy where() clauses to generate boolean signal masks and Pandas .shift(1) to forward-fill trade execution. This guarantees O(1) array-level mathematical operations, executing years of simulated daily trades in milliseconds while strictly preventing look-ahead bias.

4. Interactive UI & Market Comparison
A dynamic frontend that allows users to search for companies via an external API proxy, ingest data on the fly, and overlay multi-ticker historical price charts for comparative analysis.


💻 Local Setup & Installation
To run this project locally, you will need Python 3.9+ and free accounts with MongoDB Atlas and Financial Modeling Prep.

1. Clone the repository and set up the environment:

```bash
git clone [https://github.com/](https://github.com/)[YOUR_USERNAME]/market-intelligence-platform.git
cd market-intelligence-platform
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

3. Set up Environment Variables:
Create a .env file inside the backend/ directory:
```text
MONGODB_URL="mongodb+srv://<username>:<password>@cluster0..."
FMP_API_KEY="your_financial_modeling_prep_api_key"

4. Run the Application (Requires Two Terminals):
Terminal 1 (Backend):
```bash
uvicorn backend.main:app --reload

Terminal 2 (Frontend):
```bash
streamlit run frontend/app.py

````
