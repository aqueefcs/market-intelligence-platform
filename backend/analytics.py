import pandas as pd

def calculate_financial_metrics(historical_prices):
    if not historical_prices:
        return {"error": "No historical data available to process"}

    # 1. Load the raw JSON data into a Pandas DataFrame
    df = pd.DataFrame(historical_prices)
    
    # 2. Data Cleaning: Ensure 'date' is a proper datetime object and sort from oldest to newest
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 3. Calculate Daily Returns (Percentage change from the previous day)
    df['daily_return'] = df['close'].pct_change()
    
    # 4. Calculate Annualized Volatility 
    # (Standard deviation of daily returns multiplied by the square root of 252 trading days in a year)
    daily_volatility = df['daily_return'].std()
    annualized_volatility = daily_volatility * (252 ** 0.5)
    
    # 5. Calculate 50-Day Moving Average
    df['50_MA'] = df['close'].rolling(window=50).mean()
    latest_50_ma = df['50_MA'].iloc[-1]
    
    # 6. Calculate Total Return over the period
    last_close = df['close'].iloc[-1]
    first_close = df['close'].iloc[0]
    total_return = (last_close - first_close) / first_close
    
    # Return the metrics as a clean dictionary
    return {
        "latest_close_price": round(last_close, 2),
        "total_return_percent": round(total_return * 100, 2),
        "annualized_volatility_percent": round(annualized_volatility * 100, 2),
        "latest_50_day_ma": round(latest_50_ma, 2)
    }