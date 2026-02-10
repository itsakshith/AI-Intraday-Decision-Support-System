"""
Module: Data Fetcher
Project: AI-Based Intraday Market Decision Support System
Description: Fetches intraday stock market data as described in the project documentation.
"""

import yfinance as yf
import pandas as pd

def fetch_market_data(ticker: str, period: str = "1d", interval: str = "5m") -> pd.DataFrame:
    """
    Fetches intraday market data from Yahoo Finance.

    Args:
        ticker (str): The stock ticker symbol (e.g., '^NSEI', 'RELIANCE.NS').
        period (str): The data period to download (valid: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
        interval (str): The data interval (valid: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).

    Returns:
        pd.DataFrame: DataFrame containing Open, High, Low, Close, Volume data.
                      Returns empty DataFrame if no data found.
    """
    try:
        # Fetch data
        df = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
        df.index = pd.to_datetime(df.index)
        if df.index.tz is None:
    # If timezone-naive, assume UTC then convert
           df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
        else:
    # If already timezone-aware, just convert
           df.index = df.index.tz_convert("Asia/Kolkata")

        if df.empty:
            print(f"No data found for {ticker}")
            return pd.DataFrame()

        # Flatten MultiIndex columns if present (common in new yfinance versions)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Standardize columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df[required_cols] # Keep only OHLCV
        
        # Drop rows with missing values
        df.dropna(inplace=True)

        return df

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()
