"""
Data Fetcher Module for Financial Assistant

This module encapsulates AKShare APIs for fetching stock and ETF data.
Handles data retrieval, error handling, and data standardization.
"""

import akshare as ak
import pandas as pd
import logging
from typing import Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# 0. Stock/ETF Name Fetching (Metadata)
# ============================================================================


def get_stock_name(symbol: str) -> Optional[str]:
    """
    Fetch stock name from AKShare.

    Args:
        symbol: Stock code (e.g., "600519")

    Returns:
        Stock name (e.g., "贵州茅台") or None if fetch fails

    Example:
        >>> name = get_stock_name("600519")
        >>> print(name)  # "贵州茅台"
    """
    try:
        logger.info(f"Fetching stock name for: {symbol}")
        info = ak.stock_individual_info_em(symbol=symbol)

        # Find the row with '股票简称' or '股票名称'
        name_row = info[info["item"].isin(["股票简称", "股票名称"])]

        if not name_row.empty:
            name = name_row.iloc[0]["value"]
            logger.info(f"Stock name found: {name}")
            return name
        else:
            logger.warning(f"Stock name not found for {symbol}")
            return None

    except Exception as e:
        logger.error(f"Error fetching stock name for {symbol}: {e}")
        return None


def get_etf_name(symbol: str) -> Optional[str]:
    """
    Fetch ETF name from AKShare.

    Args:
        symbol: ETF code (e.g., "510300")

    Returns:
        ETF name (e.g., "沪深300ETF") or None if fetch fails

    Example:
        >>> name = get_etf_name("510300")
        >>> print(name)  # "沪深300ETF" or similar
    """
    try:
        logger.info(f"Fetching ETF name for: {symbol}")

        # Get ETF spot data which includes name
        df = ak.fund_etf_spot_em()

        # Find the ETF by code
        etf_row = df[df["代码"] == symbol]

        if not etf_row.empty:
            name = etf_row.iloc[0]["名称"]
            logger.info(f"ETF name found: {name}")
            return name
        else:
            logger.warning(f"ETF name not found for {symbol}")
            return None

    except Exception as e:
        logger.error(f"Error fetching ETF name for {symbol}: {e}")
        return None


# ============================================================================
# 1. Stock Data Fetching (A-shares)
# ============================================================================


def fetch_stock_daily(
    symbol: str, start_date: str, end_date: str, adjust: str = "qfq"
) -> Optional[pd.DataFrame]:
    """
    Fetch A-share daily historical data using AKShare.

    Args:
        symbol: Stock code (e.g., "600519" for 贵州茅台)
        start_date: Start date in format "YYYYMMDD"
        end_date: End date in format "YYYYMMDD"
        adjust: Adjustment type - "" (no adjust), "qfq" (forward), "hfq" (backward)

    Returns:
        DataFrame with columns: date, open, close, high, low, volume, amount
        Returns None if fetch fails

    Example:
        >>> df = fetch_stock_daily("600519", "20231001", "20231101", adjust="qfq")
        >>> print(df.head())
    """
    try:
        logger.info(f"Fetching stock data: {symbol} from {start_date} to {end_date}")

        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )

        if df.empty:
            logger.warning(f"Empty dataframe returned for symbol {symbol}")
            return None

        # Standardize column names to English
        df = df.rename(
            columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "涨跌幅": "change_pct",
                "涨跌额": "change_amount",
                "换手率": "turnover",
            }
        )

        # Convert date to datetime
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        logger.info(f"Successfully fetched {len(df)} records")
        return df

    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return None


# ============================================================================
# 2. ETF Data Fetching
# ============================================================================


def fetch_etf_daily(
    symbol: str, start_date: str, end_date: str, adjust: str = "qfq"
) -> Optional[pd.DataFrame]:
    """
    Fetch ETF daily historical data using AKShare (East Money source).

    Args:
        symbol: ETF code (e.g., "510300" for 沪深300ETF)
        start_date: Start date in format "YYYYMMDD"
        end_date: End date in format "YYYYMMDD"
        adjust: Adjustment type - "" (no adjust), "qfq" (forward), "hfq" (backward)

    Returns:
        DataFrame with columns: date, open, close, high, low, volume, amount
        Returns None if fetch fails

    Example:
        >>> df = fetch_etf_daily("510300", "20231001", "20231101")
        >>> print(df.head())
    """
    try:
        logger.info(f"Fetching ETF data: {symbol} from {start_date} to {end_date}")

        df = ak.fund_etf_hist_em(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )

        if df.empty:
            logger.warning(f"Empty dataframe returned for ETF {symbol}")
            return None

        # Standardize column names to English
        df = df.rename(
            columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "涨跌幅": "change_pct",
                "涨跌额": "change_amount",
                "换手率": "turnover",
            }
        )

        # Convert date to datetime
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        logger.info(f"Successfully fetched {len(df)} records")
        return df

    except Exception as e:
        logger.error(f"Error fetching ETF data for {symbol}: {e}")
        return None


# ============================================================================
# 3. ETF Real-time Spot Data
# ============================================================================


def fetch_etf_realtime() -> Optional[pd.DataFrame]:
    """
    Fetch real-time spot data for all ETFs in the market.

    Returns:
        DataFrame with ETF real-time quotes
        Returns None if fetch fails

    Example:
        >>> df_realtime = fetch_etf_realtime()
        >>> print(df_realtime[['代码', '名称', '最新价', '涨跌幅']].head())
    """
    try:
        logger.info("Fetching real-time ETF spot data")
        df = ak.fund_etf_spot_em()

        if df.empty:
            logger.warning("Empty dataframe returned for ETF real-time data")
            return None

        logger.info(f"Successfully fetched {len(df)} ETF records")
        return df

    except Exception as e:
        logger.error(f"Error fetching ETF real-time data: {e}")
        return None


# ============================================================================
# 4. Unified Data Fetcher (Auto-detect type)
# ============================================================================


def fetch_data(
    symbol: str,
    start_date: str,
    end_date: str,
    data_type: str = "auto",
    adjust: str = "qfq",
) -> Optional[pd.DataFrame]:
    """
    Unified data fetcher that automatically detects data type.

    Args:
        symbol: Stock/ETF code
        start_date: Start date "YYYYMMDD"
        end_date: End date "YYYYMMDD"
        data_type: "stock", "etf", or "auto" (auto-detect based on code)
        adjust: Adjustment type

    Returns:
        Standardized DataFrame or None if fetch fails

    Example:
        >>> df = fetch_data("600519", "20231001", "20231101")  # Stock
        >>> df = fetch_data("510300", "20231001", "20231101")  # ETF
    """
    # Auto-detect data type based on code pattern
    if data_type == "auto":
        # ETF codes typically start with 5 (510xxx, 159xxx)
        if symbol.startswith("5") or symbol.startswith("15"):
            data_type = "etf"
        else:
            data_type = "stock"

    if data_type == "stock":
        return fetch_stock_daily(symbol, start_date, end_date, adjust)
    elif data_type == "etf":
        return fetch_etf_daily(symbol, start_date, end_date, adjust)
    else:
        logger.error(f"Invalid data_type: {data_type}. Use 'stock', 'etf', or 'auto'")
        return None


# ============================================================================
# 5. Utility Functions
# ============================================================================


def get_trading_days(start_date: str, end_date: str) -> list:
    """
    Get all trading days between start_date and end_date.

    Args:
        start_date: Start date "YYYYMMDD"
        end_date: End date "YYYYMMDD"

    Returns:
        List of trading days
    """
    try:
        df = ak.tool_trade_date_hist_sina()
        df["trade_date"] = pd.to_datetime(df["trade_date"])

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        trading_days = df[(df["trade_date"] >= start) & (df["trade_date"] <= end)]
        return trading_days["trade_date"].tolist()

    except Exception as e:
        logger.error(f"Error fetching trading days: {e}")
        return []


if __name__ == "__main__":
    # Test code
    print("Testing data fetcher...")

    # Test stock data
    df_stock = fetch_stock_daily("600519", "20231001", "20231101")
    if df_stock is not None:
        print("\n✅ Stock data fetched successfully:")
        print(df_stock.head())

    # Test ETF data
    df_etf = fetch_etf_daily("510300", "20231001", "20231101")
    if df_etf is not None:
        print("\n✅ ETF data fetched successfully:")
        print(df_etf.head())

    # Test unified fetcher
    df_auto = fetch_data("510300", "20231001", "20231101", data_type="auto")
    if df_auto is not None:
        print("\n✅ Auto-detect fetcher works!")
