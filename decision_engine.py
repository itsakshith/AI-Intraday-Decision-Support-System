import pandas as pd

def generate_signals(df):
    """
    Generates independent Buy/Sell signals based on available technical indicators.
    
    Args:
        df (pd.DataFrame): DataFrame containing OHLCV data and potential indicators.
        
    Returns:
        pd.DataFrame: DataFrame with added signal columns (e.g., 'Signal_EMA', 'Signal_RSI')
                      Logic: 1 (Buy), -1 (Sell), 0 (Hold)
    """
    
    # 1. EMA Signal
    # BUY if Close > EMA
    # SELL if Close < EMA
    if 'EMA' in df.columns:
        df['Signal_EMA'] = 0
        df.loc[df['Close'] > df['EMA'], 'Signal_EMA'] = 1
        df.loc[df['Close'] < df['EMA'], 'Signal_EMA'] = -1

    # 2. RSI Signal
    # BUY if RSI < 30
    # SELL if RSI > 70
    if 'RSI' in df.columns:
        df['Signal_RSI'] = 0
        df.loc[df['RSI'] < 30, 'Signal_RSI'] = 1
        df.loc[df['RSI'] > 70, 'Signal_RSI'] = -1

    # 3. MACD Signal
    # BUY if MACD > Signal
    # SELL if MACD < Signal
    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        df['Signal_MACD'] = 0
        df.loc[df['MACD'] > df['MACD_Signal'], 'Signal_MACD'] = 1
        df.loc[df['MACD'] < df['MACD_Signal'], 'Signal_MACD'] = -1

    # 4. Bollinger Bands Signal
    # BUY if Close < Lower Band
    # SELL if Close > Upper Band
    if 'BB_Lower' in df.columns and 'BB_Upper' in df.columns:
        df['Signal_BB'] = 0
        df.loc[df['Close'] < df['BB_Lower'], 'Signal_BB'] = 1
        df.loc[df['Close'] > df['BB_Upper'], 'Signal_BB'] = -1

    return df
