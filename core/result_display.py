"""
Result Display Module

This module provides functions to display analysis results beautifully in Jupyter Notebooks.
Encapsulates all visualization logic for agent execution results.
"""

from typing import Dict, Any
from IPython.display import HTML, display
from .ui_utils import print_html


def display_analysis_result(result: Dict[str, Any], show_details: bool = True) -> None:
    """
    Display the complete analysis result with beautiful formatting.

    Args:
        result: Analysis result dictionary from run_agent or analyze_stock
        show_details: Whether to show technical indicators and trading signals

    Example:
        >>> result = analyze_stock("600519", days=45)
        >>> display_analysis_result(result)
    """
    if not result.get("success"):
        print(f"\n❌ 分析失败: {result.get('error', '未知错误')}")
        return

    print("\n" + "=" * 60)
    print("📊 分析结果展示")
    print("=" * 60)

    # 1. Display AI analysis report with Markdown rendering
    print_html(result["final_answer"], title="🤖 AI 分析报告", is_markdown=True)

    if not show_details:
        return

    # 2. Find and display chart and technical indicators
    for step in result.get("history", []):
        if step.get("action") == "analyze_and_plot":
            tool_result = step.get("result", {})

            if tool_result.get("status") == "success" and tool_result.get("chart_path"):
                chart_path = tool_result["chart_path"]

                # Display chart using optimized print_html (with beautiful card-style UI)
                print_html(chart_path, title="📈 技术分析图表", is_image=True)

                # Display technical indicators summary
                if tool_result.get("indicators_summary"):
                    _display_indicators_table(tool_result["indicators_summary"])

                # Display trading signals
                if tool_result.get("trading_signals"):
                    _display_trading_signals(tool_result["trading_signals"])

                print("\n✅ 分析完成！")
                break


def _display_indicators_table(indicators: Dict[str, Any]) -> None:
    """
    Display technical indicators in a beautiful gradient table.

    Args:
        indicators: Dictionary of indicator names and values
    """
    html_table = """
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; color: white; margin: 10px 0;'>
        <h3 style='margin-top: 0;'>📊 技术指标概览</h3>
        <table style='width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.1); 
                      border-radius: 5px; overflow: hidden;'>
            <thead>
                <tr style='background: rgba(0,0,0,0.2);'>
                    <th style='padding: 10px; text-align: left; border-bottom: 2px solid rgba(255,255,255,0.3);'>指标</th>
                    <th style='padding: 10px; text-align: right; border-bottom: 2px solid rgba(255,255,255,0.3);'>数值</th>
                </tr>
            </thead>
            <tbody>
    """

    for key, value in indicators.items():
        # Filter out None and NaN values
        if value is not None and not (isinstance(value, float) and value != value):
            display_name = key.replace("_", " ").upper()

            if isinstance(value, (int, float)):
                display_value = f"{value:.2f}"
            else:
                display_value = str(value)

            html_table += f"""
                <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>
                    <td style='padding: 8px;'>{display_name}</td>
                    <td style='padding: 8px; text-align: right; font-weight: bold;'>{display_value}</td>
                </tr>
            """

    html_table += """
            </tbody>
        </table>
    </div>
    """

    display(HTML(html_table))


def _display_trading_signals(signals: Dict[str, str]) -> None:
    """
    Display trading signals in a beautiful grid layout.

    Args:
        signals: Dictionary of signal types and values
    """
    signal_html = """
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 20px; border-radius: 10px; color: white; margin: 10px 0;'>
        <h3 style='margin-top: 0;'>🎯 交易信号</h3>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>
    """

    signal_icons = {"买入": "🟢", "卖出": "🔴", "持有": "🟡", "观望": "⚪"}

    for signal_type, signal_value in signals.items():
        icon = signal_icons.get(signal_value, "📌")
        signal_html += f"""
            <div style='background: rgba(255,255,255,0.2); padding: 15px; 
                        border-radius: 8px; text-align: center;'>
                <div style='font-size: 2em; margin-bottom: 5px;'>{icon}</div>
                <div style='font-size: 0.9em; opacity: 0.9;'>{signal_type}</div>
                <div style='font-size: 1.2em; font-weight: bold; margin-top: 5px;'>{signal_value}</div>
            </div>
        """

    signal_html += """
        </div>
    </div>
    """

    display(HTML(signal_html))


def display_execution_summary(result: Dict[str, Any]) -> None:
    """
    Display a brief summary of the agent execution.

    Args:
        result: Analysis result dictionary from run_agent or analyze_stock

    Example:
        >>> result = analyze_stock("600519", days=45)
        >>> display_execution_summary(result)
    """
    print("\n" + "=" * 60)
    print("📝 执行摘要")
    print("=" * 60)

    if not result.get("success"):
        print(f"❌ 状态: 失败")
        print(f"❌ 错误: {result.get('error', '未知错误')}")
        return

    print(f"✅ 状态: 成功")

    history = result.get("history", [])
    tool_calls = [step for step in history if step.get("type") == "tool_call"]

    print(f"🔄 总迭代次数: {len(history)}")
    print(f"🔧 工具调用次数: {len(tool_calls)}")

    print("\n工具调用详情:")
    for i, step in enumerate(tool_calls, 1):
        action = step.get("action")
        status = step.get("result", {}).get("status", "unknown")
        status_icon = "✅" if status == "success" else "❌"
        print(f"  {i}. {action}: {status_icon} {status}")


def display_batch_results(
    results: Dict[str, Dict[str, Any]], show_charts: bool = False
) -> None:
    """
    Display results from batch analysis of multiple stocks.

    Args:
        results: Dictionary mapping stock symbols to analysis results
        show_charts: Whether to display charts (can be overwhelming for many stocks)

    Example:
        >>> stocks = ["600519", "000858", "600036"]
        >>> results = {s: analyze_stock(s, verbose=False) for s in stocks}
        >>> display_batch_results(results)
    """
    print("\n" + "=" * 60)
    print("📊 批量分析结果")
    print("=" * 60)

    successful = sum(1 for r in results.values() if r.get("success"))
    total = len(results)

    print(f"\n✅ 成功: {successful}/{total}")
    print(f"❌ 失败: {total - successful}/{total}")

    print("\n详细结果:")

    for symbol, result in results.items():
        print(f"\n{'─'*60}")
        print(f"股票代码: {symbol}")

        if result.get("success"):
            print(f"✅ 状态: 成功")

            if show_charts:
                display_analysis_result(result, show_details=True)
            else:
                # Just show the final answer
                print_html(result["final_answer"], title=f"📈 {symbol} 分析报告")
        else:
            print(f"❌ 状态: 失败")
            print(f"   错误: {result.get('error', '未知错误')}")
