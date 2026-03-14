import streamlit as st
import requests
import pandas as pd

# The URL where your FastAPI server is running locally
API_BASE_URL = "https://market-intelligence-platform-gbg9.onrender.com/"

# Set up the page layout
st.set_page_config(page_title="Market Intelligence Platform", layout="wide")
st.title("📈 Market Intelligence Platform")

# --- SIDEBAR: Data Ingestion ---
st.sidebar.header("Ingest New Data")
st.sidebar.write("Add a new company to the database.")
new_ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., MSFT, TSLA, AMZN)").upper()

if st.sidebar.button("Fetch & Store Data"):
    if new_ticker:
        with st.spinner(f"Fetching data for {new_ticker}..."):
            response = requests.post(f"{API_BASE_URL}/ingestion/company/{new_ticker}")
            if response.status_code == 200:
                st.sidebar.success(f"✅ Successfully ingested {new_ticker}!")
            else:
                st.sidebar.error(f"❌ Failed. Check if '{new_ticker}' is valid.")

# --- MAIN DASHBOARD: Analytics & Charts ---
st.header("Company Analytics")

try:
    # 1. Fetch the list of companies you've already ingested
    companies_response = requests.get(f"{API_BASE_URL}/companies")
    
    if companies_response.status_code == 200:
        companies_data = companies_response.json().get("ingested_companies", [])
        
        if not companies_data:
            st.info("No companies found in the database. Use the sidebar to ingest some data!")
        else:
            # Create a dropdown menu using the tickers
            tickers = [c["ticker"] for c in companies_data]
            selected_ticker = st.selectbox("Select a company to analyze", tickers)

            if selected_ticker:
                st.markdown("---")
                
                # 2. Fetch and display the Pandas Analytics Metrics
                st.subheader(f"Key Metrics for {selected_ticker}")
                analytics_res = requests.get(f"{API_BASE_URL}/companies/{selected_ticker}/analytics")
                
                if analytics_res.status_code == 200:
                    metrics = analytics_res.json().get("metrics", {})
                    
                    # Streamlit's built-in metric columns look great for dashboards
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Latest Close", f"${metrics.get('latest_close_price', 0)}")
                    col2.metric("Total Return", f"{metrics.get('total_return_percent', 0)}%")
                    col3.metric("Annualized Volatility", f"{metrics.get('annualized_volatility_percent', 0)}%")
                    col4.metric("50-Day Moving Avg", f"${metrics.get('latest_50_day_ma', 0)}")
                else:
                    st.error("Could not load analytics.")

                st.markdown("---")
                
                # 3. Fetch Historical Data and plot the interactive chart
                st.subheader("Historical Stock Price")
                company_res = requests.get(f"{API_BASE_URL}/companies/{selected_ticker}")
                
                if company_res.status_code == 200:
                    history = company_res.json().get("historical_prices", [])
                    if history:
                        df = pd.DataFrame(history)
                        df['date'] = pd.to_datetime(df['date'])
                        df = df.set_index('date')
                        df = df.sort_index() # Sort from oldest to newest for the chart
                        
                        # Draw the line chart
                        st.line_chart(df['close'])
                        
    else:
         st.error("Failed to connect to the backend API. Did it return a 200?")
except requests.exceptions.ConnectionError:
    st.error("🚨 Could not connect to the backend. Make sure your FastAPI server is running!")