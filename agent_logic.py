"""
Financial Analysis Agent Logic

This module implements the main agent logic for financial data analysis.
Following the ReAct pattern, it orchestrates data fetching, analysis, and visualization.
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Import core infrastructure
from core.llm_client import get_response
from core.safe_parsing import extract_json_from_markdown, safe_json_parse
from core.data_fetcher import fetch_data, fetch_stock_daily, fetch_etf_daily
from core.indicators import (
    add_all_indicators,
    get_indicator_summary,
    generate_trading_signals,
)
from core.visualization import plot_auto, plot_comprehensive_chart
from core.ui_utils import print_html


# ============================================================================
# 1. System Prompt (Agent Role Definition)
# ============================================================================


def _get_system_prompt() -> str:
    """
    Generate system prompt with current date injected.

    This ensures the LLM knows the current date and won't use its training cutoff date
    when interpreting relative time expressions like "最近两个月" or "近期".
    """
    current_date = datetime.now().strftime("%Y年%m月%d日")

    return f"""你是一名专业的量化金融分析师助手。你的任务是协助用户获取金融市场数据，计算技术指标，并生成可视化图表来分析市场趋势。

**重要时间信息**: 今天是 {current_date}。
当用户提到"最近X天/月"、"近期"、"当前"等相对时间词时，请基于 {current_date} 来计算日期范围。

你的能力包括：
1. 获取 A 股和 ETF 的历史行情数据
2. 计算技术指标（MA、MACD、RSI、布林带等）
3. 生成专业的 K 线图和指标图表
4. 基于技术指标提供客观的市场分析

你的回答应当：
- 数据驱动，基于实际的市场数据
- 客观中立，不做主观预测
- 优先展示可视化分析结果
- 清晰解释技术指标的含义

你可以使用以下工具：

**fetch_stock_data**
获取 A 股历史数据。
参数：
- symbol: 股票代码（例如 "600519" 表示贵州茅台）
- days: 获取最近 N 天的数据（整数，推荐使用此参数）
  * 如果用户说"最近两个月"，请传递 60
  * 如果用户说"近一周"，请传递 7
  * 如果用户说"三个月"，请传递 90
- start_date: 开始日期（格式：YYYYMMDD，可选）
- end_date: 结束日期（格式：YYYYMMDD，可选）

**推荐**：优先使用 `days` 参数，系统会自动计算对应的日期范围（从今天往前推）。

**fetch_etf_data**
获取 ETF 历史数据。
参数：
- symbol: ETF 代码（例如 "510300" 表示沪深300ETF）
- days: 获取最近 N 天的数据（整数，推荐使用此参数）
  * 如果用户说"最近两个月"，请传递 60
  * 如果用户说"近一周"，请传递 7
  * 如果用户说"三个月"，请传递 90
- start_date: 开始日期（格式：YYYYMMDD，可选）
- end_date: 结束日期（格式：YYYYMMDD，可选）

**推荐**：优先使用 `days` 参数，系统会自动计算对应的日期范围（从今天往前推）。

**analyze_and_plot**
分析数据并生成图表。
参数：
- data_id: 数据标识符（由前面的 fetch 工具返回）
- chart_type: 图表类型（"auto", "basic", "ma", "macd", "comprehensive"）

当用户提出请求时，你应该：
1. 解析用户意图，提取股票代码、时间范围等关键信息
2. 将相对时间转换为天数（如"最近两个月" = 60天）
3. 调用相应的工具获取数据（优先使用 `days` 参数）
4. **必须调用 analyze_and_plot 生成分析图表**
5. 图表生成后，基于技术指标提供简短的分析报告

**重要**：你必须实际执行工具调用，而不是描述将要调用什么工具。

请以 JSON 格式返回你的工具调用：
{{
  "thought": "你的思考过程",
  "action": "工具名称",
  "action_input": {{
    "参数名": "参数值"
  }}
}}

**只有在所有工具都已执行完毕后**，才能提供最终的文字分析报告。
在提供最终答案时，不要使用 JSON 格式，直接用自然语言回答即可。
"""


# Legacy constant for backward compatibility
SYSTEM_PROMPT = _get_system_prompt()


# ============================================================================
# 2. Tool Definitions (Function Implementations)
# ============================================================================


class FinancialDataStore:
    """Simple in-memory data store for holding fetched data."""

    def __init__(self):
        self.data = {}
        self.counter = 0

    def store(self, df, metadata: dict) -> str:
        """Store dataframe and return an ID."""
        self.counter += 1
        data_id = f"data_{self.counter}"
        self.data[data_id] = {
            "dataframe": df,
            "metadata": metadata,
            "timestamp": datetime.now(),
        }
        return data_id

    def get(self, data_id: str):
        """Retrieve dataframe by ID."""
        return self.data.get(data_id, {}).get("dataframe")

    def get_metadata(self, data_id: str):
        """Retrieve metadata by ID."""
        return self.data.get(data_id, {}).get("metadata")


# Global data store
data_store = FinancialDataStore()


def tool_fetch_stock_data(
    symbol: str,
    days: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tool: Fetch stock historical data.

    Priority: If `days` is provided, it will be used to calculate date range.
    Otherwise, start_date and end_date will be used.

    Args:
        symbol: Stock code
        days: Number of days to fetch (from today backwards)
        start_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)

    Returns:
        Dictionary with status, data_id, and summary information
    """
    try:
        # Calculate date range from days parameter (recommended)
        if days is not None:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        # Use explicit dates if provided
        elif start_date is None or end_date is None:
            # Default: last 60 days
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

        df = fetch_stock_daily(symbol, start_date, end_date, adjust="qfq")

        if df is None or df.empty:
            return {
                "status": "error",
                "message": f"无法获取股票 {symbol} 的数据，请检查股票代码是否正确。",
            }

        # Fetch stock name (with fallback to symbol if fails)
        from core.data_fetcher import get_stock_name

        stock_name = get_stock_name(symbol)

        # Store data with name
        metadata = {
            "type": "stock",
            "symbol": symbol,
            "name": stock_name or symbol,  # Fallback to symbol if name fetch fails
            "start_date": start_date,
            "end_date": end_date,
        }
        data_id = data_store.store(df, metadata)

        # Generate summary
        latest = df.iloc[-1]
        first = df.iloc[0]
        change_pct = ((latest["close"] - first["close"]) / first["close"]) * 100

        summary = {
            "status": "success",
            "data_id": data_id,
            "symbol": symbol,
            "records": len(df),
            "date_range": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
            "latest_price": round(latest["close"], 2),
            "period_change": f"{change_pct:+.2f}%",
            "price_range": f"{df['low'].min():.2f} - {df['high'].max():.2f}",
        }

        return summary

    except Exception as e:
        return {"status": "error", "message": f"获取数据时出错: {str(e)}"}


def tool_fetch_etf_data(
    symbol: str,
    days: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tool: Fetch ETF historical data.

    Priority: If `days` is provided, it will be used to calculate date range.
    Otherwise, start_date and end_date will be used.

    Args:
        symbol: ETF code
        days: Number of days to fetch (from today backwards)
        start_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)

    Returns:
        Dictionary with status, data_id, and summary information
    """
    try:
        # Calculate date range from days parameter (recommended)
        if days is not None:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        # Use explicit dates if provided
        elif start_date is None or end_date is None:
            # Default: last 60 days
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

        df = fetch_etf_daily(symbol, start_date, end_date, adjust="qfq")

        if df is None or df.empty:
            return {
                "status": "error",
                "message": f"无法获取 ETF {symbol} 的数据，请检查代码是否正确。",
            }

        # Fetch ETF name (with fallback to symbol if fails)
        from core.data_fetcher import get_etf_name

        etf_name = get_etf_name(symbol)

        # Store data with name
        metadata = {
            "type": "etf",
            "symbol": symbol,
            "name": etf_name or symbol,  # Fallback to symbol if name fetch fails
            "start_date": start_date,
            "end_date": end_date,
        }
        data_id = data_store.store(df, metadata)

        # Generate summary
        latest = df.iloc[-1]
        first = df.iloc[0]
        change_pct = ((latest["close"] - first["close"]) / first["close"]) * 100

        summary = {
            "status": "success",
            "data_id": data_id,
            "symbol": symbol,
            "records": len(df),
            "date_range": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
            "latest_price": round(latest["close"], 2),
            "period_change": f"{change_pct:+.2f}%",
            "price_range": f"{df['low'].min():.2f} - {df['high'].max():.2f}",
        }

        return summary

    except Exception as e:
        return {"status": "error", "message": f"获取数据时出错: {str(e)}"}


def tool_analyze_and_plot(data_id: str, chart_type: str = "auto") -> Dict[str, Any]:
    """
    Tool: Analyze data and generate chart.

    Returns:
        Dictionary with chart path and technical analysis summary
    """
    try:
        # Retrieve data
        df = data_store.get(data_id)
        metadata = data_store.get_metadata(data_id)

        if df is None:
            return {"status": "error", "message": f"找不到数据 ID: {data_id}"}

        # Calculate technical indicators
        df_with_indicators = add_all_indicators(df)

        # Generate signals
        df_with_signals = generate_trading_signals(df_with_indicators)

        # Get latest indicator summary
        indicator_summary = get_indicator_summary(df_with_signals)

        # Generate chart with professional title
        symbol = metadata.get("symbol", "Unknown")
        name = metadata.get("name", symbol)  # Get name, fallback to symbol

        # Professional title format: "股票名称(代码) 技术分析"
        if name != symbol:
            title = f"{name}({symbol}) 技术分析"
        else:
            title = f"{symbol} 技术分析"  # Fallback if name not available

        chart_path = plot_auto(df_with_signals, title=title, chart_type=chart_type)

        # Get latest signals
        latest_signals = df_with_signals.iloc[-1]

        result = {
            "status": "success",
            "chart_path": chart_path,
            "symbol": symbol,
            "analysis": {
                "latest_price": round(indicator_summary["close_price"], 2),
                "ma_5": (
                    round(indicator_summary["ma_5"], 2)
                    if indicator_summary["ma_5"]
                    else None
                ),
                "ma_20": (
                    round(indicator_summary["ma_20"], 2)
                    if indicator_summary["ma_20"]
                    else None
                ),
                "ma_60": (
                    round(indicator_summary["ma_60"], 2)
                    if indicator_summary["ma_60"]
                    else None
                ),
                "rsi_14": (
                    round(indicator_summary["rsi_14"], 2)
                    if indicator_summary["rsi_14"]
                    else None
                ),
                "macd": (
                    round(indicator_summary["macd"], 4)
                    if indicator_summary["macd"]
                    else None
                ),
                "macd_signal": (
                    round(indicator_summary["macd_signal"], 4)
                    if indicator_summary["macd_signal"]
                    else None
                ),
            },
            "signals": {
                "macd_cross": latest_signals.get("macd_cross", "HOLD"),
                "rsi_signal": latest_signals.get("rsi_signal", "NEUTRAL"),
                "ma_cross": latest_signals.get("ma_cross", "HOLD"),
            },
        }

        return result

    except Exception as e:
        return {"status": "error", "message": f"分析数据时出错: {str(e)}"}


# Tool registry
TOOLS = {
    "fetch_stock_data": tool_fetch_stock_data,
    "fetch_etf_data": tool_fetch_etf_data,
    "analyze_and_plot": tool_analyze_and_plot,
}


# ============================================================================
# 3. Agent Execution Loop (ReAct Pattern)
# ============================================================================


def parse_agent_response(response: str) -> Optional[Dict]:
    """
    Parse the agent's response to extract tool call.

    Returns:
        Dictionary with thought, action, action_input, or None if no tool call
    """
    # Try to extract JSON from markdown code block
    json_str = extract_json_from_markdown(response)

    if json_str:
        parsed = safe_json_parse(json_str)
        if parsed and "action" in parsed:
            return parsed

    return None


def execute_tool(tool_name: str, tool_input: Dict) -> Any:
    """
    Execute a tool with given input.

    Returns:
        Tool execution result
    """
    if tool_name not in TOOLS:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    tool_func = TOOLS[tool_name]

    try:
        result = tool_func(**tool_input)
        return result
    except Exception as e:
        return {"status": "error", "message": f"Tool execution error: {str(e)}"}


def run_agent(
    user_query: str,
    model: str = "gpt-4o-mini",
    max_iterations: int = 5,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run the financial analysis agent.

    Args:
        user_query: User's question or request
        model: LLM model to use
        max_iterations: Maximum number of tool calls
        verbose: Whether to print intermediate steps

    Returns:
        Dictionary with final response and execution history
    """
    history = []
    # Use dynamic prompt with current date
    system_prompt = _get_system_prompt()
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]

    for iteration in range(max_iterations):
        if verbose:
            print(f"\n{'='*60}")
            print(f"🔄 Iteration {iteration + 1}/{max_iterations}")
            print(f"{'='*60}")

        # Get agent response
        prompt = "\n\n".join([msg["content"] for msg in conversation])
        response = get_response(model, prompt)

        if verbose:
            print(
                f"\n🤖 Agent Response:\n{response[:200]}..."
                if len(response) > 200
                else f"\n🤖 Agent Response:\n{response}"
            )

        # Try to parse tool call
        parsed = parse_agent_response(response)

        if parsed is None:
            # No tool call, this is the final answer
            history.append(
                {
                    "iteration": iteration + 1,
                    "type": "final_answer",
                    "content": response,
                }
            )

            if verbose:
                print(f"\n✅ Agent 完成分析")

            return {"success": True, "final_answer": response, "history": history}

        # Execute tool
        thought = parsed.get("thought", "")
        action = parsed.get("action")
        action_input = parsed.get("action_input", {})

        if verbose:
            print(f"\n💭 Thought: {thought}")
            print(f"🔧 Action: {action}")
            print(f"📥 Input: {json.dumps(action_input, ensure_ascii=False)}")

        tool_result = execute_tool(action, action_input)

        if verbose:
            status_icon = "✅" if tool_result.get("status") == "success" else "❌"
            print(f"{status_icon} Result: {tool_result.get('status', 'unknown')}")
            if tool_result.get("status") != "success":
                print(f"   Error: {tool_result.get('message', 'N/A')}")

        # Record in history
        history.append(
            {
                "iteration": iteration + 1,
                "type": "tool_call",
                "thought": thought,
                "action": action,
                "action_input": action_input,
                "result": tool_result,
            }
        )

        # Add observation to conversation
        observation = (
            f"工具执行结果：\n{json.dumps(tool_result, ensure_ascii=False, indent=2)}"
        )
        conversation.append({"role": "assistant", "content": response})
        conversation.append({"role": "user", "content": observation})

    # Max iterations reached
    if verbose:
        print(f"\n⚠️  达到最大迭代次数")

    return {"success": False, "error": "达到最大迭代次数", "history": history}


# ============================================================================
# 4. Simplified Interface
# ============================================================================


def analyze_stock(
    symbol: str, days: int = 60, model: str = "gpt-4o-mini", verbose: bool = True
) -> Dict[str, Any]:
    """
    Simplified interface to analyze a stock.

    Args:
        symbol: Stock code (e.g., "600519")
        days: Number of days to analyze (default: 60)
        model: LLM model to use
        verbose: Whether to print progress

    Returns:
        Analysis result dictionary

    Example:
        >>> result = analyze_stock("600519", days=90)
    """
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    if verbose:
        print(f"\n{'='*60}")
        print(f"📈 开始分析股票 {symbol}")
        print(f"📅 时间范围: {start_date} 到 {end_date} (最近 {days} 天)")
        print(f"🤖 使用模型: {model}")
        print(f"{'='*60}")

    query = f"请帮我分析股票 {symbol} 最近 {days} 天的走势，时间范围是 {start_date} 到 {end_date}。"

    return run_agent(query, model=model, verbose=verbose)


if __name__ == "__main__":
    # Test code
    print("Testing Financial Analysis Agent...")

    # Test query
    test_query = "帮我分析一下贵州茅台（600519）最近两个月的走势"

    result = run_agent(test_query, model="gpt-4o-mini", verbose=True)

    if result["success"]:
        print("\n" + "=" * 60)
        print("✅ Agent execution successful!")
        print("=" * 60)
        print("\nFinal Answer:")
        print(result["final_answer"])
    else:
        print("\n❌ Agent execution failed:")
        print(result.get("error"))
