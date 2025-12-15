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

# Import Skill Orchestrator (v1.4.0 - Skill Mode Integration)
try:
    from skills import SkillOrchestrator

    orchestrator = SkillOrchestrator()
    USE_SKILLS = True
    print("✅ Skill 模式已启用")
except ImportError as e:
    USE_SKILLS = False
    orchestrator = None
    print(f"⚠️  Skill 模式未启用，使用传统工具模式: {e}")


# ============================================================================
# 1. System Prompt (Agent Role Definition)
# ============================================================================


def _get_system_prompt() -> str:
    """
    Generate system prompt with current date injected (v1.3.0 - Optimized).

    This ensures the LLM knows the current date and won't use its training cutoff date
    when interpreting relative time expressions like "最近两个月" or "近期".

    Optimization (v1.3.0):
    - Reduced token count by 67.6% (1658 → 537 tokens)
    - Simplified expressions while maintaining core functionality
    - Removed redundant descriptions
    - Consolidated tool parameter explanations
    """
    current_date = datetime.now().strftime("%Y年%m月%d日")

    return f"""你是量化金融分析师助手。今天是 {current_date}。

**核心能力**：获取A股/ETF数据，计算技术指标，生成K线图表。

**工具**：

1. **fetch_stock_data**(symbol, days=60) - 获取A股数据
   - symbol: 股票代码（如"600519"）
   - days: 天数（"最近两个月"=60，"近一周"=7）

2. **fetch_etf_data**(symbol, days=60) - 获取ETF数据
   - symbol: ETF代码（如"510300"）
   - days: 同上

3. **analyze_and_plot**(data_id, chart_type="comprehensive") - 生成图表
   - data_id: 前面工具返回的ID
   - chart_type: "auto"/"basic"/"comprehensive"

**执行流程**：
1. 提取股票代码和天数
2. 调用fetch工具（优先用days参数）
3. **必须**调用analyze_and_plot生成图表
4. 基于图表提供简短分析

**响应格式**（JSON）：
{{
  "thought": "分析用户需求",
  "action": "工具名",
  "action_input": {{"参数": "值"}}
}}

完成时输出：{{"final_answer": "分析结论"}}
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
# 2.5. Skill Integration Helper Functions (v1.4.0)
# ============================================================================


def _format_skill_result_for_data_fetch(skill_result: dict) -> dict:
    """
    将 Skill 数据获取结果格式化为传统格式

    Args:
        skill_result: Skill 返回的结果

    Returns:
        dict: 传统工具格式的结果
    """
    if not skill_result.get("success"):
        return {"status": "error", "message": skill_result.get("error", "未知错误")}

    # 存储 DataFrame 到 data_store
    df = skill_result["data"]
    metadata = {
        "type": "stock",  # 或 "etf"，根据工具名判断
        "symbol": skill_result.get("symbol", ""),
        "name": skill_result.get("symbol", ""),
        "start_date": "",
        "end_date": "",
    }
    data_id = data_store.store(df, metadata)

    # 生成摘要信息（与传统格式一致）
    latest = df.iloc[-1]
    first = df.iloc[0]

    # 计算涨跌幅
    if "收盘" in df.columns:
        change_pct = ((latest["收盘"] - first["收盘"]) / first["收盘"]) * 100
        latest_price = round(latest["收盘"], 2)
    elif "close" in df.columns:
        change_pct = ((latest["close"] - first["close"]) / first["close"]) * 100
        latest_price = round(latest["close"], 2)
    else:
        change_pct = 0
        latest_price = 0

    return {
        "status": "success",
        "data_id": data_id,
        "symbol": skill_result.get("symbol", ""),
        "records": skill_result.get("rows", len(df)),
        "date_range": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
        "latest_price": latest_price,
        "period_change": f"{change_pct:+.2f}%",
        "message": skill_result.get("message", "数据获取成功"),
    }


def _try_skill_execution(tool_name: str, tool_input: dict) -> Optional[dict]:
    """
    尝试使用 Skill 执行工具

    Args:
        tool_name: 工具名称
        tool_input: 工具参数

    Returns:
        dict: 执行结果，失败则返回 None
    """
    if not USE_SKILLS or orchestrator is None:
        return None

    try:
        # 工具名映射（传统工具名 → Skill 工具名）
        skill_tool_mapping = {
            "fetch_stock_data": "fetch_stock_data",
            "fetch_etf_data": "fetch_etf_data",
            # analyze_and_plot 暂时不映射，因为需要重构逻辑
        }

        skill_tool_name = skill_tool_mapping.get(tool_name)
        if not skill_tool_name:
            return None  # 不支持的工具，回退到传统模式

        # 执行 Skill 工具
        skill_result = orchestrator.execute_tool(skill_tool_name, tool_input)

        # 格式化结果
        if tool_name in ["fetch_stock_data", "fetch_etf_data"]:
            return _format_skill_result_for_data_fetch(skill_result)

        return skill_result

    except Exception as e:
        print(f"⚠️  Skill 执行失败，回退到传统模式: {e}")
        return None


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

    v1.4.0: 支持混合模式（Skills 优先 + 传统工具 fallback）

    Returns:
        Tool execution result
    """
    # 1. 尝试使用 Skill 模式执行
    skill_result = _try_skill_execution(tool_name, tool_input)
    if skill_result is not None:
        print(f"✅ 使用 Skill 模式执行: {tool_name}")
        return skill_result

    # 2. 回退到传统工具
    print(f"📌 使用传统模式执行: {tool_name}")
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
