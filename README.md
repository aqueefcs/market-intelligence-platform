# 📈 Market Intelligence Platform

**Live Dashboard:** [Insert Streamlit App URL Here]  
**Live API Docs:** [Insert Render API /docs URL Here]

## Overview

The Market Intelligence Platform is a full-stack, backend-driven analytics system. It ingests real-time financial market data from external APIs, stores structured datasets in a cloud NoSQL database, computes financial metrics using Pandas, and exposes insights through both RESTful APIs and an interactive visualization dashboard.

This project demonstrates end-to-end data pipeline construction, API development, and cloud deployment.

## System Architecture

External Financial API (FMP)
↓
FastAPI Backend (Data Ingestion Endpoint)
↓
MongoDB Atlas (Cloud Database)
↓
FastAPI Backend (Analytics Engine via Pandas)
↓
Streamlit Dashboard (Data Visualization)

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic, Pandas, Requests
- **Database:** MongoDB Atlas (NoSQL)
- **Frontend:** Streamlit
- **Deployment:** Render (Backend), Streamlit Community Cloud (Frontend)

## Core Features

1. **Automated Data Ingestion:** Fetches real-time company profiles and historical stock prices via the Financial Modeling Prep API.
2. **Cloud Data Storage:** Implements an `upsert` architecture in MongoDB to ensure data remains current without duplication.
3. **Analytics Engine:** Utilizes Pandas to calculate financial metrics across time-series data, including:
   - Total Return Percentage
   - Annualized Volatility
   - 50-Day Moving Averages
4. **Interactive Dashboard:** Provides a user-friendly interface to ingest new tickers on the fly and compare historical performance metrics.

## API Endpoints

- `POST /ingestion/company/{ticker}` - Fetches external data and stores it in MongoDB.
- `GET /companies` - Retrieves a list of all currently tracked companies.
- `GET /companies/{ticker}` - Retrieves full profile and historical data.
- `GET /companies/{ticker}/analytics` - Computes and returns financial metrics.
