"""
Technical Indicators - Phase D
RSI, EMA, ATR, Body/Wick ratio, Momentum
"""

import pandas as pd
import numpy as np
from typing import Tuple


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index)
    
    Args:
        series: Price series (usually close)
        period: RSI period (default 14)
    
    Returns:
        RSI series
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate EMA (Exponential Moving Average)
    
    Args:
        series: Price series (usually close)
        period: EMA period
    
    Returns:
        EMA series
    """
    return series.ewm(span=period, adjust=False).mean()


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate ATR (Average True Range)
    
    Args:
        df: DataFrame with high, low, close columns
        period: ATR period (default 14)
    
    Returns:
        ATR series
    """
    high = df["high"]
    low = df["low"]
    close = df["close"]
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=period).mean()
    
    return atr


def calculate_macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        series: Price series (usually close)
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line period (default 9)
    
    Returns:
        (macd_line, signal_line, histogram)
    """
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_body_wick_ratio(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate candle body size, upper wick, lower wick
    
    Args:
        df: DataFrame with open, high, low, close columns
    
    Returns:
        (body_size, upper_wick, lower_wick)
    """
    body_size = abs(df["close"] - df["open"])
    
    upper_wick = df["high"] - df[["open", "close"]].max(axis=1)
    lower_wick = df[["open", "close"]].min(axis=1) - df["low"]
    
    return body_size, upper_wick, lower_wick


def calculate_momentum(series: pd.Series, period: int = 3) -> pd.Series:
    """
    Calculate momentum (price change over period)
    
    Args:
        series: Price series (usually close)
        period: Momentum period (default 3)
    
    Returns:
        Momentum series
    """
    return series.diff(period)


def detect_trend(df: pd.DataFrame, ema_period: int = 50) -> str:
    """
    Detect trend using EMA
    
    Args:
        df: DataFrame with close column
        ema_period: EMA period for trend detection (default 50)
    
    Returns:
        "uptrend", "downtrend", or "range"
    """
    close = df["close"]
    ema = calculate_ema(close, ema_period)
    
    # Check last 10 candles
    last_10_close = close.iloc[-10:]
    last_10_ema = ema.iloc[-10:]
    
    above_count = (last_10_close > last_10_ema).sum()
    below_count = (last_10_close < last_10_ema).sum()
    
    if above_count >= 7:
        return "uptrend"
    elif below_count >= 7:
        return "downtrend"
    else:
        return "range"


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all indicators and add to DataFrame
    
    Args:
        df: DataFrame with OHLCV columns
    
    Returns:
        DataFrame with all indicators added
    """
    df = df.copy()
    
    # RSI
    df["rsi"] = calculate_rsi(df["close"], period=14)
    
    # EMA
    df["ema9"] = calculate_ema(df["close"], period=9)
    df["ema21"] = calculate_ema(df["close"], period=21)
    df["ema50"] = calculate_ema(df["close"], period=50)
    df["ema200"] = calculate_ema(df["close"], period=200)
    
    # ATR
    df["atr"] = calculate_atr(df, period=14)
    
    # MACD
    df["macd"], df["macd_signal"], df["macd_hist"] = calculate_macd(df["close"])
    
    # Body/Wick
    df["body_size"], df["upper_wick"], df["lower_wick"] = calculate_body_wick_ratio(df)
    
    # Momentum
    df["momentum_3"] = calculate_momentum(df["close"], period=3)
    
    # Average body size (for comparison)
    df["avg_body_size"] = df["body_size"].rolling(window=20, min_periods=20).mean()
    
    return df


def get_last_candle_features(df: pd.DataFrame) -> dict:
    """
    Extract features from last candle
    
    Args:
        df: DataFrame with all indicators
    
    Returns:
        Dict of features
    """
    last = df.iloc[-1]
    
    # Trend detection
    trend = detect_trend(df, ema_period=50)
    
    # EMA alignment
    ema9 = last["ema9"]
    ema21 = last["ema21"]
    ema50 = last["ema50"]
    close = last["close"]
    
    ema_aligned_up = (ema9 > ema21) and (ema21 > ema50)
    ema_aligned_down = (ema9 < ema21) and (ema21 < ema50)
    
    # Body strength
    body_size = last["body_size"]
    avg_body_size = last["avg_body_size"]
    body_strength = body_size / avg_body_size if avg_body_size > 0 else 1.0
    
    # Wick ratio
    upper_wick = last["upper_wick"]
    lower_wick = last["lower_wick"]
    total_range = last["high"] - last["low"]
    
    upper_wick_ratio = upper_wick / total_range if total_range > 0 else 0
    lower_wick_ratio = lower_wick / total_range if total_range > 0 else 0
    
    # ATR spike
    atr = last["atr"]
    avg_atr = df["atr"].iloc[-20:].mean()
    atr_spike = atr / avg_atr if avg_atr > 0 else 1.0
    
    return {
        "close": close,
        "open": last["open"],
        "high": last["high"],
        "low": last["low"],
        "rsi": last["rsi"],
        "ema9": ema9,
        "ema21": ema21,
        "ema50": ema50,
        "ema200": last["ema200"],
        "atr": atr,
        "atr_spike": atr_spike,
        "macd": last["macd"],
        "macd_signal": last["macd_signal"],
        "macd_hist": last["macd_hist"],
        "body_size": body_size,
        "avg_body_size": avg_body_size,
        "body_strength": body_strength,
        "upper_wick": upper_wick,
        "lower_wick": lower_wick,
        "upper_wick_ratio": upper_wick_ratio,
        "lower_wick_ratio": lower_wick_ratio,
        "momentum_3": last["momentum_3"],
        "trend": trend,
        "ema_aligned_up": ema_aligned_up,
        "ema_aligned_down": ema_aligned_down,
    }
