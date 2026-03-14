import pandas as pd
import numpy as np

def calculate_financial_metrics(historical_prices):
    if not historical_prices:
        return {"error": "No historical data available to process"}

    df = pd.DataFrame(historical_prices)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Existing basic metrics
    df['daily_return'] = df['close'].pct_change()
    daily_volatility = df['daily_return'].std()
    annualized_volatility = daily_volatility * (np.sqrt(252))
    df['50_MA'] = df['close'].rolling(window=50).mean()
    
    # --- NEW PANDAS FLEX: 14-Day RSI Calculation ---
    # 1. Calculate the daily price differences
    delta = df['close'].diff()
    
    # 2. Separate the gains (positive deltas) and losses (negative deltas)
    # The .where() function replaces values where the condition is False
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # 3. Calculate the 14-day exponential moving average (EMA) of gains and losses
    avg_gain = gain.ewm(span=14, adjust=False).mean()
    avg_loss = loss.ewm(span=14, adjust=False).mean()
    
    # 4. Calculate the Relative Strength (RS)
    rs = avg_gain / avg_loss
    
    # 5. Calculate the RSI
    # If avg_loss is 0, RSI should be 100 (handling division by zero)
    df['RSI_14'] = np.where(avg_loss == 0, 100, 100 - (100 / (1 + rs)))
    
    # Extract the final values
    last_close = df['close'].iloc[-1]
    first_close = df['close'].iloc[0]
    total_return = (last_close - first_close) / first_close
    latest_rsi = df['RSI_14'].iloc[-1]
    
    return {
        "latest_close_price": round(last_close, 2),
        "total_return_percent": round(total_return * 100, 2),
        "annualized_volatility_percent": round(annualized_volatility * 100, 2),
        "latest_50_day_ma": round(df['50_MA'].iloc[-1], 2),
        "latest_rsi": round(latest_rsi, 2) # Added RSI!
    }

def run_rsi_backtest(historical_prices, initial_capital=10000):
    if not historical_prices:
        return {"error": "No historical data available"}

    # 1. Setup DataFrame
    df = pd.DataFrame(historical_prices)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df.set_index('date', inplace=True)

    # 2. Calculate daily baseline returns
    df['daily_return'] = df['close'].pct_change()

    # 3. Recalculate RSI for the backtest period
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(span=14, adjust=False).mean()
    avg_loss = loss.ewm(span=14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = np.where(avg_loss == 0, 100, 100 - (100 / (1 + rs)))

    # 4. Vectorized Strategy Signals (1 = Hold Stock, 0 = Sit in Cash)
    df['signal'] = np.nan
    df.loc[df['RSI'] < 30, 'signal'] = 1  # Buy condition
    df.loc[df['RSI'] > 70, 'signal'] = 0  # Sell condition
    
    # Forward fill the signals so we hold the position until the next signal
    df['signal'] = df['signal'].ffill().fillna(0)

    # 5. Shift signal by 1 day (We buy at the close of the signal day, so returns start the NEXT day)
    # This completely eliminates look-ahead bias.
    df['strategy_return'] = df['signal'].shift(1) * df['daily_return']

    # 6. Calculate Cumulative Equity 
    df['buy_and_hold_equity'] = initial_capital * (1 + df['daily_return']).cumprod()
    df['strategy_equity'] = initial_capital * (1 + df['strategy_return']).cumprod()

    # Clean up the output data
    result_df = df[['buy_and_hold_equity', 'strategy_equity']].dropna()
    result_df.reset_index(inplace=True)

    final_buy_hold = result_df['buy_and_hold_equity'].iloc[-1]
    final_strategy = result_df['strategy_equity'].iloc[-1]
    outperformance = ((final_strategy - final_buy_hold) / final_buy_hold) * 100

    # Format dates as strings for JSON serialization
    result_df['date'] = result_df['date'].dt.strftime('%Y-%m-%d')

    return {
        "initial_capital": initial_capital,
        "final_buy_and_hold": round(final_buy_hold, 2),
        "final_strategy": round(final_strategy, 2),
        "outperformance_percent": round(outperformance, 2),
        "chart_data": result_df.to_dict(orient="records")
    }