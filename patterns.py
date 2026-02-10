import pandas as pd
import numpy as np

def detect_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects candlestick patterns: Doji, Hammer, Engulfing.
    Adds boolean columns to the dataframe:
    - 'Pattern_Doji'
    - 'Pattern_Hammer'
    - 'Pattern_Bullish_Engulfing'
    - 'Pattern_Bearish_Engulfing'
    """
    df = df.copy()

    # Calculate absolute body size and shadow sizes
    df['Body'] = abs(df['Close'] - df['Open'])
    df['Upper_Shadow'] = df['High'] - df[['Open', 'Close']].max(axis=1)
    df['Lower_Shadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']
    df['Total_Range'] = df['High'] - df['Low']
    
    # Avoid division by zero
    avg_body_size = df['Body'].mean()
    
    # 1. Doji
    # Definition: Body is very small relative to total range (e.g., < 10% of range or very small absolute value)
    df['Pattern_Doji'] = df['Body'] <= (0.1 * df['Total_Range'])

    # 2. Hammer
    # Definition: Small body, Long lower shadow (>= 2x body), Short upper shadow
    # Bullish signal if it appears in a downtrend (we will just identify the shape here)
    condition_hammer_body = df['Body'] < (0.3 * df['Total_Range']) # Small body
    condition_long_lower = df['Lower_Shadow'] >= (2.0 * df['Body']) # Long lower wick
    condition_short_upper = df['Upper_Shadow'] <= (1.0 * df['Body']) # Short upper wick
    
    df['Pattern_Hammer'] = condition_hammer_body & condition_long_lower & condition_short_upper

    # 3. Engulfing
    # Definition: 
    # Bullish: Previous Red, Current Green, Current Body > Previous Body, Current Open < Prev Close, Current Close > Prev Open
    # Bearish: Previous Green, Current Red, Current Body > Previous Body, Current Open > Prev Close, Current Close < Prev Open
    
    # Vectorized comparison with shifted values
    prev_open = df['Open'].shift(1)
    prev_close = df['Close'].shift(1)
    prev_body = df['Body'].shift(1)
    
    is_prev_red = prev_close < prev_open
    is_prev_green = prev_close > prev_open
    
    is_curr_green = df['Close'] > df['Open']
    is_curr_red = df['Close'] < df['Open']
    
    # Simplified Engulfing (Just body engulfing body for robustness, strict definition matches open/close exactly)
    # Using loose definition: Current body fully engulfs previous body
    
    # Bullish Engulfing
    df['Pattern_Bullish_Engulfing'] = (
        is_prev_red & 
        is_curr_green & 
        (df['Open'] <= prev_close) & 
        (df['Close'] >= prev_open)
    )

    # Bearish Engulfing
    df['Pattern_Bearish_Engulfing'] = (
        is_prev_green & 
        is_curr_red & 
        (df['Open'] >= prev_close) & 
        (df['Close'] <= prev_open)
    )
    
    # Cleanup temporary columns
    df.drop(columns=['Body', 'Upper_Shadow', 'Lower_Shadow', 'Total_Range'], inplace=True)
    
    return df
