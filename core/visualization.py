"""
Visualization Module for Financial Data

This module provides functions to create professional financial charts:
- K-line (Candlestick) charts with technical indicators
- Volume charts
- Indicator subplots (MACD, RSI)
"""

import pandas as pd
import mplfinance as mpf
import matplotlib

matplotlib.use("Agg")  # 使用非交互式后端，避免自动显示图表
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Optional, Tuple
import os
from datetime import datetime
import sys


# ============================================================================
# Configure Chinese Font Support
# ============================================================================


def _configure_chinese_font():
    """
    Configure matplotlib to support Chinese characters.

    This function automatically detects and sets the best available Chinese font
    based on the operating system.

    Returns:
        str: The name of the selected Chinese font, or None if not found
    """
    # Try to find a suitable Chinese font
    chinese_fonts = []

    if sys.platform == "darwin":  # macOS
        # Prefer PingFang SC (Modern macOS default), fallback to others
        preferred_fonts = [
            "PingFang SC",
            "Heiti SC",
            "STHeiti",
            "Hiragino Sans GB",
            "Arial Unicode MS",
        ]
    elif sys.platform == "win32":  # Windows
        preferred_fonts = ["Microsoft YaHei", "SimHei", "KaiTi", "FangSong"]
    else:  # Linux
        preferred_fonts = [
            "WenQuanYi Micro Hei",
            "WenQuanYi Zen Hei",
            "Noto Sans CJK SC",
            "Droid Sans Fallback",
        ]

    # Find available fonts from the system
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    # Select the first available preferred font
    selected_font = None
    for font in preferred_fonts:
        if font in available_fonts:
            selected_font = font
            break

    # Fallback: try to find any font with Chinese keywords
    if not selected_font:
        chinese_keywords = [
            "PingFang",
            "Heiti",
            "STHeiti",
            "SimHei",
            "YaHei",
            "KaiTi",
            "FangSong",
            "Hiragino",
            "WenQuanYi",
            "Noto",
        ]
        for font in available_fonts:
            if any(keyword in font for keyword in chinese_keywords):
                selected_font = font
                break

    # Apply font configuration
    if selected_font:
        plt.rcParams["font.sans-serif"] = [selected_font, "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False  # Fix minus sign display
        print(f"✅ Matplotlib 中文字体已配置: {selected_font}")
    else:
        print("⚠️  未找到合适的中文字体，图表中文可能显示为方块")
        # Even without Chinese font, set unicode_minus to prevent issues
        plt.rcParams["axes.unicode_minus"] = False

    return selected_font


# Initialize Chinese font support when module is imported
_CHINESE_FONT = _configure_chinese_font()


def _create_style_with_chinese_font(**kwargs):
    """
    Create mplfinance style with Chinese font support and professional visual settings.

    Args:
        **kwargs: Additional style parameters for make_mpf_style

    Returns:
        Style object for mplfinance
    """
    # Add font configuration if Chinese font is available
    if _CHINESE_FONT:
        if "rc" not in kwargs:
            kwargs["rc"] = {}
        kwargs["rc"].update(
            {
                "font.sans-serif": [_CHINESE_FONT, "DejaVu Sans"],
                "axes.unicode_minus": False,
                # Professional font settings (similar to Sina Finance)
                "axes.labelsize": 10,  # Axis label font size
                "xtick.labelsize": 9,  # X-axis tick label size
                "ytick.labelsize": 9,  # Y-axis tick label size
                "axes.titlesize": 14,  # Title font size
                "axes.titleweight": "bold",  # Bold title
                # Grid line optimization (light and subtle)
                "grid.color": "#E0E0E0",  # Light gray grid
                "grid.linestyle": "-",  # Solid line
                "grid.linewidth": 0.5,  # Thin lines
                "grid.alpha": 0.3,  # Subtle transparency
            }
        )

    return mpf.make_mpf_style(**kwargs)


# ============================================================================
# 1. Basic K-line Chart
# ============================================================================


def plot_kline_basic(
    df: pd.DataFrame,
    title: str = "Stock Price Chart",
    save_path: Optional[str] = None,
    show: bool = True,
) -> str:
    """
    Plot basic candlestick chart.

    Args:
        df: DataFrame with columns: open, high, low, close, volume (date as index)
        title: Chart title
        save_path: Path to save the chart (if None, auto-generate)
        show: Whether to display the chart

    Returns:
        Path to the saved chart image

    Example:
        >>> chart_path = plot_kline_basic(df, title="贵州茅台 K线图")
    """
    # Auto-generate save path if not provided
    if save_path is None:
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"outputs/kline_{timestamp}.png"

    # Create custom style
    mc = mpf.make_marketcolors(
        up="red",  # Rising candles (red in China)
        down="green",  # Falling candles (green in China)
        edge="inherit",
        wick="inherit",
        volume="in",
        alpha=0.9,
    )

    s = mpf.make_mpf_style(marketcolors=mc, gridstyle="--", y_on_right=False)

    # Plot
    mpf.plot(
        df,
        type="candle",
        style=s,
        title=title,
        ylabel="Price",
        volume=True,
        ylabel_lower="Volume",
        savefig=save_path,
        show_nontrading=False,
    )

    print(f"✅ Chart saved to: {save_path}")
    return save_path


# ============================================================================
# 2. K-line Chart with Moving Averages
# ============================================================================


def plot_kline_with_ma(
    df: pd.DataFrame,
    ma_periods: list = [5, 10, 20, 60],
    title: str = "Stock Price with MA",
    save_path: Optional[str] = None,
    show: bool = True,
) -> str:
    """
    Plot candlestick chart with moving averages overlaid.

    Args:
        df: DataFrame with MA columns (ma_5, ma_10, etc.)
        ma_periods: List of MA periods to plot
        title: Chart title
        save_path: Path to save the chart
        show: Whether to display the chart

    Returns:
        Path to the saved chart image

    Example:
        >>> chart_path = plot_kline_with_ma(df, ma_periods=[5, 20, 60])
    """
    # Auto-generate save path if not provided
    if save_path is None:
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"outputs/kline_ma_{timestamp}.png"

    # Prepare moving average plots
    ma_plots = []
    ma_colors = ["blue", "orange", "purple", "brown"]

    for i, period in enumerate(ma_periods):
        ma_col = f"ma_{period}"
        if ma_col in df.columns:
            ma_plots.append(
                mpf.make_addplot(
                    df[ma_col], color=ma_colors[i % len(ma_colors)], width=1.5
                )
            )

    # Create custom style
    mc = mpf.make_marketcolors(
        up="red", down="green", edge="inherit", wick="inherit", volume="in", alpha=0.9
    )

    s = mpf.make_mpf_style(marketcolors=mc, gridstyle="--", y_on_right=False)

    # Plot
    mpf.plot(
        df,
        type="candle",
        style=s,
        title=title,
        ylabel="Price",
        volume=True,
        ylabel_lower="Volume",
        addplot=ma_plots,
        savefig=save_path,
        show_nontrading=False,
    )

    print(f"✅ Chart with MA saved to: {save_path}")
    return save_path


# ============================================================================
# 3. K-line Chart with MACD
# ============================================================================


def plot_kline_with_macd(
    df: pd.DataFrame,
    title: str = "Stock Price with MACD",
    save_path: Optional[str] = None,
    show: bool = True,
) -> str:
    """
    Plot candlestick chart with MACD indicator in subplot.

    Args:
        df: DataFrame with columns: macd, macd_signal, macd_hist
        title: Chart title
        save_path: Path to save the chart
        show: Whether to display the chart

    Returns:
        Path to the saved chart image

    Example:
        >>> chart_path = plot_kline_with_macd(df)
    """
    # Auto-generate save path if not provided
    if save_path is None:
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"outputs/kline_macd_{timestamp}.png"

    # Prepare MACD plots
    macd_plots = [
        mpf.make_addplot(df["macd"], panel=2, color="blue", width=1.5, ylabel="MACD"),
        mpf.make_addplot(df["macd_signal"], panel=2, color="red", width=1.5),
        mpf.make_addplot(df["macd_hist"], panel=2, type="bar", color="gray", alpha=0.5),
    ]

    # Create custom style
    mc = mpf.make_marketcolors(
        up="red", down="green", edge="inherit", wick="inherit", volume="in", alpha=0.9
    )

    s = mpf.make_mpf_style(marketcolors=mc, gridstyle="--", y_on_right=False)

    # Plot
    mpf.plot(
        df,
        type="candle",
        style=s,
        title=title,
        ylabel="Price",
        volume=True,
        ylabel_lower="Volume",
        addplot=macd_plots,
        savefig=save_path,
        show_nontrading=False,
        panel_ratios=(3, 1, 1),  # Main chart : Volume : MACD
    )

    print(f"✅ Chart with MACD saved to: {save_path}")
    return save_path


# ============================================================================
# 4. Comprehensive Chart (MA + MACD + RSI)
# ============================================================================


def plot_comprehensive_chart(
    df: pd.DataFrame,
    ma_periods: list = [5, 20, 60],
    title: str = "Comprehensive Technical Analysis",
    save_path: Optional[str] = None,
    show: bool = True,
) -> str:
    """
    Plot comprehensive chart with MA, MACD, and RSI indicators.

    Args:
        df: DataFrame with all indicators calculated
        ma_periods: List of MA periods to plot
        title: Chart title
        save_path: Path to save the chart
        show: Whether to display the chart

    Returns:
        Path to the saved chart image

    Example:
        >>> chart_path = plot_comprehensive_chart(df)
    """
    # Auto-generate save path if not provided
    if save_path is None:
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"outputs/comprehensive_{timestamp}.png"

    # Prepare all plots
    addplots = []
    # Professional MA colors (inspired by Sina Finance)
    ma_colors = ["#1E90FF", "#FF69B4", "#FFD700"]  # Blue, Pink, Gold
    panel_count = 1  # Start with 1 (volume is always panel 1)

    # Moving Averages on main chart (panel 0) - Thicker lines for clarity
    for i, period in enumerate(ma_periods):
        ma_col = f"ma_{period}"
        if ma_col in df.columns and not df[ma_col].isna().all():
            addplots.append(
                mpf.make_addplot(
                    df[ma_col],
                    panel=0,
                    color=ma_colors[i % len(ma_colors)],
                    width=2.5,  # Thicker for better visibility
                    alpha=0.85,  # Slight transparency
                )
            )

    # MACD on next panel (if available) - Professional styling
    has_macd = "macd" in df.columns and not df["macd"].isna().all()
    if has_macd:
        panel_count += 1
        addplots.extend(
            [
                mpf.make_addplot(
                    df["macd"],
                    panel=panel_count,
                    color="#1E90FF",  # DodgerBlue
                    width=2.0,
                    ylabel="MACD",
                ),
                mpf.make_addplot(
                    df["macd_signal"],
                    panel=panel_count,
                    color="#FF69B4",  # HotPink
                    width=2.0,
                ),
                mpf.make_addplot(
                    df["macd_hist"],
                    panel=panel_count,
                    type="bar",
                    color="gray",
                    alpha=0.6,  # More visible histogram
                ),
            ]
        )

    # RSI on next panel (if available) - Professional styling
    has_rsi = "rsi_14" in df.columns and not df["rsi_14"].isna().all()
    if has_rsi:
        panel_count += 1
        addplots.append(
            mpf.make_addplot(
                df["rsi_14"],
                panel=panel_count,
                color="#9370DB",  # MediumPurple
                width=2.0,
                ylabel="RSI",
            )
        )
        # Add RSI reference lines (30 and 70) - More subtle
        addplots.extend(
            [
                mpf.make_addplot(
                    [30] * len(df),
                    panel=panel_count,
                    color="#32CD32",  # LimeGreen
                    linestyle="--",
                    width=1.0,
                    alpha=0.6,
                ),
                mpf.make_addplot(
                    [70] * len(df),
                    panel=panel_count,
                    color="#DC143C",  # Crimson
                    linestyle="--",
                    width=1.0,
                    alpha=0.6,
                ),
            ]
        )

    # Create custom style with Chinese font support and professional look
    mc = mpf.make_marketcolors(
        up="red", down="green", edge="inherit", wick="inherit", volume="in", alpha=0.9
    )

    s = _create_style_with_chinese_font(
        marketcolors=mc,
        gridstyle="-",
        y_on_right=False,  # Solid grid lines (handled by rc params)
    )

    # Calculate panel ratios dynamically (inspired by Sina Finance layout)
    # Main chart gets more space, indicators get proportional space
    panel_ratios = [4.5, 1.2]  # Main chart + volume (optimized ratio)
    if has_macd:
        panel_ratios.append(1.0)  # MACD panel
    if has_rsi:
        panel_ratios.append(1.0)  # RSI panel

    # Determine x-axis rotation based on data density
    data_points = len(df)
    xrotation = 0 if data_points <= 40 else 15  # Rotate labels if too dense

    # Plot with professional settings
    mpf.plot(
        df,
        type="candle",
        style=s,
        title=title,
        ylabel="Price",
        volume=True,
        ylabel_lower="Volume",
        addplot=addplots if addplots else None,
        savefig=save_path,
        show_nontrading=False,
        panel_ratios=tuple(panel_ratios),
        figsize=(14, 10),
        xrotation=xrotation,  # Smart label rotation
        datetime_format="%m-%d",  # Simplified date format (month-day)
    )

    print(f"✅ Comprehensive chart saved to: {save_path}")
    return save_path


# ============================================================================
# 5. Utility: Auto-select Chart Type
# ============================================================================


def plot_auto(
    df: pd.DataFrame,
    title: str = "Financial Chart",
    save_path: Optional[str] = None,
    chart_type: str = "auto",
) -> str:
    """
    Automatically select the best chart type based on available data.

    Args:
        df: DataFrame with financial data
        title: Chart title
        save_path: Path to save the chart
        chart_type: "auto", "basic", "ma", "macd", or "comprehensive"

    Returns:
        Path to the saved chart image

    Example:
        >>> chart_path = plot_auto(df, title="贵州茅台分析")
    """
    if chart_type == "auto":
        # Check which indicators are available
        has_ma = any(col.startswith("ma_") for col in df.columns)
        has_macd = "macd" in df.columns
        has_rsi = "rsi_14" in df.columns

        if has_ma and has_macd and has_rsi:
            chart_type = "comprehensive"
        elif has_macd:
            chart_type = "macd"
        elif has_ma:
            chart_type = "ma"
        else:
            chart_type = "basic"

    # Plot based on selected type
    if chart_type == "comprehensive":
        return plot_comprehensive_chart(df, title=title, save_path=save_path)
    elif chart_type == "macd":
        return plot_kline_with_macd(df, title=title, save_path=save_path)
    elif chart_type == "ma":
        return plot_kline_with_ma(df, title=title, save_path=save_path)
    else:
        return plot_kline_basic(df, title=title, save_path=save_path)


if __name__ == "__main__":
    # Test code
    print("Testing visualization module...")

    import numpy as np

    # Create sample data
    dates = pd.date_range("2023-10-01", periods=60, freq="D")
    close_prices = 100 + np.random.randn(60).cumsum()

    df = pd.DataFrame(
        {
            "date": dates,
            "open": close_prices + np.random.randn(60) * 0.5,
            "high": close_prices + abs(np.random.randn(60)) * 1,
            "low": close_prices - abs(np.random.randn(60)) * 1,
            "close": close_prices,
            "volume": np.random.randint(1000000, 10000000, 60),
        }
    )
    df = df.set_index("date")

    # Add some indicators
    df["ma_5"] = df["close"].rolling(5).mean()
    df["ma_20"] = df["close"].rolling(20).mean()

    # Test basic chart
    chart_path = plot_kline_basic(df, title="Test K-line Chart", show=False)
    print(f"✅ Basic chart created: {chart_path}")

    # Test MA chart
    chart_path_ma = plot_kline_with_ma(
        df, ma_periods=[5, 20], title="Test MA Chart", show=False
    )
    print(f"✅ MA chart created: {chart_path_ma}")
