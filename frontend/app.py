import streamlit as st
import requests
import pandas as pd
import os

# This tells Streamlit: "Use the live URL if it exists in the environment, otherwise default to localhost"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Set up the page layout
st.set_page_config(page_title="Market Intelligence Platform", layout="wide")
st.title("📈 Market Intelligence Platform")

# --- NEW: Documentation & Glossary Expander ---
with st.expander("📖 Project Documentation & Financial Glossary"):
    st.markdown("""
    ### 🏗️ System Architecture
    * **Backend:** A high-performance REST API built with **FastAPI** and Python.
    * **Database:** **MongoDB Atlas** (NoSQL) using an `upsert` strategy to keep data fresh without duplicates.
    * **Frontend:** Interactive dashboard built with **Streamlit**.
    * **Analytics Engine:** Powered by **Pandas**, utilizing vectorized operations to process time-series data without slow `for` loops.

    ### 📊 Financial Metrics Explained
    * **Total Return:** The total percentage gained or lost over the entire available history of the stock.
    * **Annualized Volatility:** A measure of risk. It calculates the standard deviation of daily returns, annualized to show how wildly the stock price swings.
    * **50-Day Moving Average (MA):** The average closing price over the last 50 days. Used to smooth out daily noise and identify the overall trend.
    * **14-Day RSI (Relative Strength Index):** A momentum oscillator that measures the speed of price movements on a scale of 0 to 100. 
        * **Overbought (>70):** The stock may be overvalued and due for a pullback.
        * **Oversold (<30):** The stock may be undervalued and due for a bounce.

    ### ⚙️ The Algorithmic Backtester
    This engine simulates a systematic trading strategy over the entire history of the stock. 
    * **The Strategy:** It buys the stock when the RSI drops below 30 (Oversold) and sells/moves to cash when the RSI goes above 70 (Overbought).
    * **The Tech:** Instead of looping through days one-by-one, it uses **Pandas vectorization** (`.shift()`, `.where()`) to calculate thousands of simulated trades in milliseconds, completely eliminating look-ahead bias and maximizing execution speed.
    """)

# --- SIDEBAR: Data Ingestion & Search ---
st.sidebar.header("🔍 Search & Ingest")
st.sidebar.write("Search for a company by name to add it to the database.")

search_query = st.sidebar.text_input("Company Name (e.g., Apple, Tesla)")

if st.sidebar.button("Search"):
    if search_query:
        with st.spinner("Searching..."):
            res = requests.get(f"{API_BASE_URL}/search/{search_query}")
            if res.status_code == 200:
                results = res.json().get("results", [])
                if results:
                    # Store the results in Streamlit's session state so they don't disappear
                    st.session_state['search_results'] = results
                else:
                    st.sidebar.warning("No companies found with that name.")
            else:
                st.sidebar.error("Search failed.")

# If we have search results, show a dropdown to let the user pick the right one
if 'search_results' in st.session_state and st.session_state['search_results']:
    results = st.session_state['search_results']
    # Create a dictionary of "Company Name (Ticker)" -> "Ticker"
    options = {f"{c['name']} ({c['symbol']})": c['symbol'] for c in results}
    
    selected_name = st.sidebar.selectbox("Select the correct company:", list(options.keys()))
    selected_ticker = options[selected_name]

    if st.sidebar.button(f"Ingest {selected_ticker}"):
        with st.spinner(f"Fetching and storing data for {selected_ticker}..."):
            response = requests.post(f"{API_BASE_URL}/ingestion/company/{selected_ticker}")
            if response.status_code == 200:
                st.sidebar.success(f"✅ Successfully ingested {selected_ticker}!")
                # Clear the search results so the sidebar resets
                del st.session_state['search_results']
            else:
                st.sidebar.error(f"❌ Failed to ingest {selected_ticker}.")

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
                    
                    # Streamlit's built-in metric columns
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Latest Close", f"${metrics.get('latest_close_price', 0)}")
                    col2.metric("Total Return", f"{metrics.get('total_return_percent', 0)}%")
                    col3.metric("Volatility", f"{metrics.get('annualized_volatility_percent', 0)}%")
                    col4.metric("50-Day MA", f"${metrics.get('latest_50_day_ma', 0)}")
                    
                    # Add RSI logic (RSI > 70 is considered Overbought, < 30 is Oversold)
                    rsi_value = metrics.get('latest_rsi', 0)
                    rsi_delta = "Overbought" if rsi_value > 70 else "Oversold" if rsi_value < 30 else "Neutral"
                    col5.metric("14-Day RSI", f"{rsi_value}", delta=rsi_delta, delta_color="off")
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

                        # ... (Your existing single-company chart code ends here) ...

                        # --- NEW: Algorithmic Backtester Section ---
                        st.markdown("---")
                        st.subheader("⚙️ Algorithmic Backtesting Engine")
                        st.write(f"Simulate a Vectorized RSI Trading Strategy for {selected_ticker} using historical data.")
                        
                        # 1. Add the dynamic number input
                        starting_capital = st.number_input("Enter Starting Capital ($)", min_value=100, max_value=10000000, value=10000, step=1000)
                        
                        if st.button("Run RSI Backtest Simulation"):
                            with st.spinner("Executing vectorized trades..."):
                                # 2. Pass the dynamic capital to the API using a query parameter
                                backtest_res = requests.get(f"{API_BASE_URL}/companies/{selected_ticker}/backtest?capital={starting_capital}")
                                
                                if backtest_res.status_code == 200:
                                    b_data = backtest_res.json().get("results", {})
                                    
                                    st.success("Simulation Complete!")
                                    
                                    b_col1, b_col2, b_col3 = st.columns(3)
                                    # Formatting the numbers with commas so they look like real money!
                                    b_col1.metric("Starting Capital", f"${b_data.get('initial_capital', 0):,.2f}")
                                    b_col2.metric("Buy & Hold Final Equity", f"${b_data.get('final_buy_and_hold', 0):,.2f}")
                                    b_col3.metric("RSI Strategy Final", f"${b_data.get('final_strategy', 0):,.2f}", 
                                                delta=f"{b_data.get('outperformance_percent', 0)}% vs Buy & Hold")
                                    
                                    chart_data = b_data.get("chart_data", [])
                                    if chart_data:
                                        b_df = pd.DataFrame(chart_data)
                                        b_df['date'] = pd.to_datetime(b_df['date'])
                                        b_df.set_index('date', inplace=True)
                                        
                                        st.write("**Equity Curve Comparison**")
                                        st.line_chart(b_df[['buy_and_hold_equity', 'strategy_equity']])
                                else:
                                    st.error("Backtest failed to run.")

                        # --- NEW: Multi-Company Comparison Section ---
                        st.markdown("---")
                        st.subheader("📊 Compare Stock Performance")
                        st.write("Select multiple companies to compare their historical closing prices.")
                        
                        # Use a multiselect box (defaulting to the first two companies if available)
                        default_compare = tickers[:2] if len(tickers) > 1 else tickers
                        compare_tickers = st.multiselect("Select companies to compare:", tickers, default=default_compare)
                        
                        if compare_tickers:
                            combined_df = pd.DataFrame()
                            
                            # Loop through the selected tickers, fetch their data, and add to the combined DataFrame
                            with st.spinner("Crunching comparison data..."):
                                for t in compare_tickers:
                                    res = requests.get(f"{API_BASE_URL}/companies/{t}")
                                    if res.status_code == 200:
                                        history = res.json().get("historical_prices", [])
                                        if history:
                                            df_temp = pd.DataFrame(history)
                                            df_temp['date'] = pd.to_datetime(df_temp['date'])
                                            df_temp = df_temp.set_index('date')
                                            df_temp = df_temp.sort_index()
                                            
                                            # Add this company's 'close' column to our master DataFrame, named after the ticker
                                            combined_df[t] = df_temp['close']
                            
                            # If we successfully built the dataframe, draw the multi-line chart!
                            if not combined_df.empty:
                                st.line_chart(combined_df)
                            else:
                                st.warning("Not enough data to compare.")
                        
    else:
         st.error("Failed to connect to the backend API. Did it return a 200?")
except requests.exceptions.ConnectionError:
    st.error("🚨 Could not connect to the backend. Make sure your FastAPI server is running!")