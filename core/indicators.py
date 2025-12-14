"""
Technical Indicators Calculation Module

This module provides functions to calculate common technical indicators:
- Moving Averages (MA)
- MACD (Moving Average Convergence Divergence)
- RSI (Relative Strength Index)
- Bollinger Bands
"""

import pandas as pd
import numpy as np
from typing import Optional


# ============================================================================
# 1. Moving Averages (MA)
# ============================================================================


def calculate_ma(df: pd.DataFrame, periods: list = [5, 10, 20, 60]) -> pd.DataFrame:
    """
    Calculate Moving Averages for specified periods.

    Args:
        df: DataFrame with 'close' column
        periods: List of MA periods (default: [5, 10, 20, 60])

    Returns:
        DataFrame with additional MA columns (ma_5, ma_10, ma_20, ma_60)

    Example:
        >>> df = calculate_ma(df, periods=[5, 20, 60])
    """
    df = df.copy()

    for period in periods:
        col_name = f"ma_{period}"
        df[col_name] = df["close"].rolling(window=period).mean()

    return df


# ============================================================================
# 2. MACD (Moving Average Convergence Divergence)
# ============================================================================


def calculate_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """
    Calculate MACD indicator.

    MACD = EMA(12) - EMA(26)
    Signal Line = EMA(9) of MACD
    Histogram = MACD - Signal

    Args:
        df: DataFrame with 'close' column
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)

    Returns:
        DataFrame with columns: macd, macd_signal, macd_hist

    Example:
        >>> df = calculate_macd(df)
    """
    df = df.copy()

    # Calculate EMAs
    ema_fast = df["close"].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow_period, adjust=False).mean()

    # MACD line
    df["macd"] = ema_fast - ema_slow

    # Signal line
    df["macd_signal"] = df["macd"].ewm(span=signal_period, adjust=False).mean()

    # Histogram
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    return df


# ============================================================================
# 3. RSI (Relative Strength Index)
# ============================================================================


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate RSI (Relative Strength Index).

    RSI measures the speed and magnitude of price changes.
    Values range from 0-100:
    - RSI > 70: Overbought (potential sell signal)
    - RSI < 30: Oversold (potential buy signal)

    Args:
        df: DataFrame with 'close' column
        period: RSI period (default: 14)

    Returns:
        DataFrame with column: rsi_14 (or rsi_{period})

    Example:
        >>> df = calculate_rsi(df, period=14)
    """
    df = df.copy()

    # Calculate price changes
    delta = df["close"].diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate average gains and losses
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    df[f"rsi_{period}"] = rsi

    return df


# ============================================================================
# 4. Bollinger Bands
# ============================================================================


def calculate_bollinger_bands(
    df: pd.DataFrame, period: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.

    Bollinger Bands consist of:
    - Middle Band: Simple Moving Average (SMA)
    - Upper Band: SMA + (Standard Deviation × num_std)
    - Lower Band: SMA - (Standard Deviation × num_std)

    Args:
        df: DataFrame with 'close' column
        period: Moving average period (default: 20)
        num_std: Number of standard deviations (default: 2.0)

    Returns:
        DataFrame with columns: bb_middle, bb_upper, bb_lower

    Example:
        >>> df = calculate_bollinger_bands(df, period=20, num_std=2.0)
    """
    df = df.copy()

    # Middle band (SMA)
    df["bb_middle"] = df["close"].rolling(window=period).mean()

    # Calculate standard deviation
    std = df["close"].rolling(window=period).std()

    # Upper and lower bands
    df["bb_upper"] = df["bb_middle"] + (std * num_std)
    df["bb_lower"] = df["bb_middle"] - (std * num_std)

    return df


# ============================================================================
# 5. Volume Indicators
# ============================================================================


def calculate_volume_ma(df: pd.DataFrame, periods: list = [5, 10]) -> pd.DataFrame:
    """
    Calculate Volume Moving Averages.

    Args:
        df: DataFrame with 'volume' column
        periods: List of periods (default: [5, 10])

    Returns:
        DataFrame with columns: vol_ma_5, vol_ma_10

    Example:
        >>> df = calculate_volume_ma(df, periods=[5, 10])
    """
    df = df.copy()

    for period in periods:
        col_name = f"vol_ma_{period}"
        df[col_name] = df["volume"].rolling(window=period).mean()

    return df


# ============================================================================
# 6. All-in-One: Add All Technical Indicators
# ============================================================================


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all common technical indicators to the DataFrame.

    Intelligently adapts to data length:
    - < 20 days: Only short-term indicators (MA5, MA10)
    - < 60 days: Medium-term indicators (MA5, MA10, MA20)
    - >= 60 days: All indicators including MA60

    Includes:
    - MA (Moving Averages)
    - MACD (12, 26, 9)
    - RSI (14)
    - Bollinger Bands (20, 2)
    - Volume MA (5, 10)

    Args:
        df: DataFrame with columns: date, open, close, high, low, volume

    Returns:
        DataFrame with all applicable technical indicators added

    Example:
        >>> df_with_indicators = add_all_indicators(df)
    """
    df = df.copy()
    data_len = len(df)

    # Intelligently select MA periods based on data length
    if data_len < 20:
        ma_periods = [5, 10]
    elif data_len < 60:
        ma_periods = [5, 10, 20]
    else:
        ma_periods = [5, 10, 20, 60]

    # Moving Averages
    df = calculate_ma(df, periods=ma_periods)

    # MACD (requires at least 26 days)
    if data_len >= 26:
        df = calculate_macd(df)

    # RSI (requires at least 14 days)
    if data_len >= 14:
        df = calculate_rsi(df, period=14)

    # Bollinger Bands (requires at least 20 days)
    if data_len >= 20:
        df = calculate_bollinger_bands(df, period=20, num_std=2.0)

    # Volume MA
    if data_len >= 10:
        vol_periods = [5, 10] if data_len >= 10 else [5]
        df = calculate_volume_ma(df, periods=vol_periods)

    return df


# ============================================================================
# 7. Signal Generation (Basic)
# ============================================================================


def generate_trading_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate basic trading signals based on technical indicators.

    Signals:
    - MACD cross: MACD line crosses signal line
    - RSI extreme: RSI > 70 (overbought) or RSI < 30 (oversold)
    - MA cross: Price crosses MA(20)

    Args:
        df: DataFrame with technical indicators

    Returns:
        DataFrame with signal columns: macd_signal_flag, rsi_signal, ma_signal

    Example:
        >>> df = generate_trading_signals(df)
    """
    df = df.copy()

    # MACD cross signal
    df["macd_cross"] = np.where(
        (df["macd"] > df["macd_signal"])
        & (df["macd"].shift(1) <= df["macd_signal"].shift(1)),
        "BUY",
        np.where(
            (df["macd"] < df["macd_signal"])
            & (df["macd"].shift(1) >= df["macd_signal"].shift(1)),
            "SELL",
            "HOLD",
        ),
    )

    # RSI signal
    df["rsi_signal"] = np.where(
        df["rsi_14"] > 70,
        "OVERBOUGHT",
        np.where(df["rsi_14"] < 30, "OVERSOLD", "NEUTRAL"),
    )

    # MA(20) cross signal
    df["ma_cross"] = np.where(
        (df["close"] > df["ma_20"]) & (df["close"].shift(1) <= df["ma_20"].shift(1)),
        "BUY",
        np.where(
            (df["close"] < df["ma_20"])
            & (df["close"].shift(1) >= df["ma_20"].shift(1)),
            "SELL",
            "HOLD",
        ),
    )

    return df


# ============================================================================
# 8. Utility: Get Indicator Summary
# ============================================================================


def get_indicator_summary(df: pd.DataFrame) -> dict:
    """
    Get a summary of the latest indicator values.

    Args:
        df: DataFrame with technical indicators

    Returns:
        Dictionary with latest indicator values

    Example:
        >>> summary = get_indicator_summary(df)
        >>> print(summary)
    """
    latest = df.iloc[-1]

    summary = {
        "close_price": latest["close"],
        "ma_5": latest.get("ma_5", None),
        "ma_20": latest.get("ma_20", None),
        "ma_60": latest.get("ma_60", None),
        "macd": latest.get("macd", None),
        "macd_signal": latest.get("macd_signal", None),
        "macd_hist": latest.get("macd_hist", None),
        "rsi_14": latest.get("rsi_14", None),
        "bb_upper": latest.get("bb_upper", None),
        "bb_middle": latest.get("bb_middle", None),
        "bb_lower": latest.get("bb_lower", None),
    }

    return summary


if __name__ == "__main__":
    # Test code
    print("Testing indicators module...")

    # Create sample data
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    close_prices = 100 + np.random.randn(100).cumsum()
    volume = np.random.randint(1000000, 10000000, 100)

    df = pd.DataFrame(
        {
            "date": dates,
            "close": close_prices,
            "volume": volume,
            "open": close_prices + np.random.randn(100) * 0.5,
            "high": close_prices + np.random.randn(100) * 1,
            "low": close_prices - np.random.randn(100) * 1,
        }
    )
    df = df.set_index("date")

    # Add all indicators
    df_with_indicators = add_all_indicators(df)

    print("\n✅ Indicators calculated successfully!")
    print(df_with_indicators[["close", "ma_5", "ma_20", "rsi_14", "macd"]].tail())

    # Get summary
    summary = get_indicator_summary(df_with_indicators)
    print("\n✅ Latest indicator summary:")
    for key, value in summary.items():
        if value is not None:
            print(f"  {key}: {value:.2f}")
