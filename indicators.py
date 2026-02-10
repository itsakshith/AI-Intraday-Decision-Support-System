import pandas as pd
import numpy as np

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI).
    """
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    Calculates Moving Average Convergence Divergence (MACD).
    Returns:
        macd_line, signal_line, histogram
    """
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_ema(data: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Calculates Exponential Moving Average (EMA).
    """
    return data['Close'].ewm(span=period, adjust=False).mean()

def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std: int = 2) -> tuple:
    """
    Calculates Bollinger Bands.
    Returns:
        upper_band, lower_band
    """
    sma = data['Close'].rolling(window=period).mean()
    std_dev = data['Close'].rolling(window=period).std()
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    return upper_band, lower_band
