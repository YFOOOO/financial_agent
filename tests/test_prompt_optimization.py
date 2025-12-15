"""
Pytest 格式的 Prompt 优化测试

测试不同版本的 Prompt，验证优化效果

测试目的：
1. 验证 v1 精简版（Token 最少）的实际准确性
2. 验证 v3 CoT版（理论上更稳健）的实际表现
3. 自动化测试确保优化后质量不下降

运行方式：
    pytest tests/test_prompt_optimization.py -v
    pytest tests/test_prompt_optimization.py::test_v1_prompt_quality -v
"""

import sys
from pathlib import Path
import pytest
from datetime import datetime
import time

# 添加项目根目录到 path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_logic import run_agent


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def test_query():
    """测试查询语句"""
    return "分析茅台最近两个月的走势"


@pytest.fixture
def test_model():
    """测试使用的模型"""
    return "gpt-4o-mini"  # 使用快速模型进行测试


@pytest.fixture
def v1_prompt():
    """v1 精简版 Prompt"""
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


@pytest.fixture
def v3_prompt(v1_prompt):
    """v3 CoT引导版 Prompt"""
    cot_guide = """
**思维链步骤**（必须在 thought 中体现）：
1. 意图识别 → 2. 参数提取 → 3. 工具选择 → 4. 执行

示例thought格式: "意图:分析茅台走势 | 参数:600519,60天 | 工具:fetch_stock_data"
"""
    return v1_prompt + cot_guide


# ============================================================================
# 辅助函数
# ============================================================================

def run_with_custom_prompt(prompt, query, model="gpt-4o-mini", verbose=False):
    """使用自定义 Prompt 运行 Agent"""
    import agent_logic
    
    # 临时替换 Prompt
    original_get_prompt = agent_logic._get_system_prompt
    agent_logic._get_system_prompt = lambda: prompt
    
    try:
        start = time.time()
        result = run_agent(query, model=model, verbose=verbose)
        duration = time.time() - start
        
        # 质量检查
        final_answer = result.get('final_answer', '')
        has_trend = any(word in final_answer for word in ["上涨", "下跌", "震荡", "趋势"])
        has_indicator = any(word in final_answer for word in ["MA", "MACD", "RSI", "金叉", "死叉"])
        
        return {
            "success": result.get('success', False),
            "duration": duration,
            "tokens": result.get('total_tokens'),
            "has_chart": bool(result.get('chart_path')),
            "has_trend": has_trend,
            "has_indicator": has_indicator,
            "final_answer": final_answer
        }
    finally:
        # 恢复原始 Prompt
        agent_logic._get_system_prompt = original_get_prompt


# ============================================================================
# 测试用例
# ============================================================================

@pytest.mark.slow
@pytest.mark.skip(reason="需要 LLM API，手动运行: pytest tests/test_prompt_optimization.py -m slow")
def test_v1_prompt_quality(v1_prompt, test_query, test_model):
    """测试 v1 精简版 Prompt 的质量"""
    result = run_with_custom_prompt(v1_prompt, test_query, test_model)
    
    # 基本断言
    assert result["success"], "v1 精简版执行失败"
    assert result["has_chart"], "v1 精简版未生成图表"
    assert result["has_trend"], "v1 精简版缺少趋势分析"
    assert result["has_indicator"], "v1 精简版缺少指标分析"
    
    # 性能断言（允许较大范围）
    assert result["duration"] < 60, f"v1 精简版执行超时: {result['duration']:.2f}s"
    
    print(f"\n✅ v1 精简版测试通过:")
    print(f"  耗时: {result['duration']:.2f}s")
    print(f"  Token: {result['tokens']}")


@pytest.mark.slow
@pytest.mark.skip(reason="需要 LLM API，手动运行: pytest tests/test_prompt_optimization.py -m slow")
def test_v3_prompt_quality(v3_prompt, test_query, test_model):
    """测试 v3 CoT版 Prompt 的质量"""
    result = run_with_custom_prompt(v3_prompt, test_query, test_model)
    
    # 基本断言
    assert result["success"], "v3 CoT版执行失败"
    assert result["has_chart"], "v3 CoT版未生成图表"
    assert result["has_trend"], "v3 CoT版缺少趋势分析"
    assert result["has_indicator"], "v3 CoT版缺少指标分析"
    
    # 性能断言
    assert result["duration"] < 60, f"v3 CoT版执行超时: {result['duration']:.2f}s"
    
    print(f"\n✅ v3 CoT版测试通过:")
    print(f"  耗时: {result['duration']:.2f}s")
    print(f"  Token: {result['tokens']}")


@pytest.mark.parametrize("prompt_version,version_name", [
    ("v1_prompt", "v1 精简版"),
    ("v3_prompt", "v3 CoT版"),
])
@pytest.mark.slow
@pytest.mark.skip(reason="需要 LLM API，手动运行: pytest tests/test_prompt_optimization.py -m slow")
def test_prompt_versions_comparison(prompt_version, version_name, test_query, test_model, request):
    """参数化测试：对比不同版本的 Prompt"""
    prompt = request.getfixturevalue(prompt_version)
    result = run_with_custom_prompt(prompt, test_query, test_model)
    
    # 通用质量检查
    assert result["success"], f"{version_name} 执行失败"
    assert result["has_chart"], f"{version_name} 未生成图表"
    
    print(f"\n📊 {version_name}:")
    print(f"  成功: {result['success']}")
    print(f"  耗时: {result['duration']:.2f}s")
    print(f"  Token: {result['tokens']}")
    print(f"  图表: {'✅' if result['has_chart'] else '❌'}")
    print(f"  趋势分析: {'✅' if result['has_trend'] else '❌'}")
    print(f"  指标分析: {'✅' if result['has_indicator'] else '❌'}")
    
    print("\n💡 决策建议:")
    print("  - 如果两个版本质量相当，选择 Token 更少的 v1")
    print("  - 如果 v3 明显更准确，选择 v3")
    print("  - 记录实际 Token 数，更新实验报告")
