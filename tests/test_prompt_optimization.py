"""
手动验证 Prompt 优化效果

快速测试不同版本的 Prompt，对比实际表现

测试目的：
1. 验证 v1 精简版（Token 最少）的实际准确性
2. 验证 v3 CoT版（理论上更稳健）的实际表现
3. 基于真实数据决策采纳哪个版本

运行方式：
    python3 tests/test_prompt_optimization.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_logic import run_agent
from datetime import datetime
import time

# ============================================================================
# 优化后的 Prompt 版本
# ============================================================================

def get_v1_prompt():
    """v1 精简版 - Token 最少"""
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


def get_v3_prompt():
    """v3 CoT引导版 - 预期准确率最高"""
    base = get_v1_prompt()
    cot_guide = """
**思维链步骤**（必须在 thought 中体现）：
1. 意图识别 → 2. 参数提取 → 3. 工具选择 → 4. 执行

示例thought格式: "意图:分析茅台走势 | 参数:600519,60天 | 工具:fetch_stock_data"
"""
    return base + cot_guide


# ============================================================================
# 测试函数
# ============================================================================

def test_prompt_version(prompt_func, version_name, test_query, model="gpt-4o-mini"):
    """
    测试指定版本的 Prompt
    """
    print(f"\n{'='*60}")
    print(f"🧪 测试版本: {version_name}")
    print(f"📝 查询: {test_query}")
    print(f"{'='*60}\n")
    
    # 临时替换 Prompt（通过猴子补丁）
    import agent_logic
    original_get_prompt = agent_logic._get_system_prompt
    agent_logic._get_system_prompt = prompt_func
    
    try:
        start = time.time()
        result = run_agent(test_query, model=model, verbose=True)
        end = time.time()
        
        # 分析结果
        print(f"\n📊 测试结果:")
        print(f"  ⏱️  耗时: {end - start:.2f}s")
        print(f"  ✅ 成功: {result.get('success')}")
        print(f"  🎫 Token: {result.get('total_tokens', 'N/A')}")
        print(f"  📈 生成图表: {'是' if result.get('chart_path') else '否'}")
        
        final_answer = result.get('final_answer', '')
        if final_answer:
            print(f"\n📝 分析摘要:")
            print(f"  {final_answer[:200]}{'...' if len(final_answer) > 200 else ''}")
            
            # 质量检查
            has_trend = any(word in final_answer for word in ["上涨", "下跌", "震荡", "趋势"])
            has_indicator = any(word in final_answer for word in ["MA", "MACD", "RSI", "金叉", "死叉"])
            
            print(f"\n✅ 质量评分:")
            print(f"  趋势分析: {'✅' if has_trend else '❌'}")
            print(f"  指标分析: {'✅' if has_indicator else '❌'}")
        else:
            print(f"  ❌ 未返回分析结果")
        
        return {
            "version": version_name,
            "duration": end - start,
            "success": result.get('success'),
            "tokens": result.get('total_tokens'),
            "has_chart": bool(result.get('chart_path')),
            "has_trend": has_trend if final_answer else False,
            "has_indicator": has_indicator if final_answer else False,
        }
        
    except Exception as e:
        print(f"  ❌ 测试失败: {str(e)}")
        return {
            "version": version_name,
            "error": str(e)
        }
    finally:
        # 恢复原始 Prompt
        agent_logic._get_system_prompt = original_get_prompt


# ============================================================================
# 主测试流程
# ============================================================================

if __name__ == "__main__":
    print("🚀 开始 Prompt 优化效果验证")
    print("="*60)
    
    # 测试用例
    TEST_QUERY = "分析茅台最近两个月的走势"
    MODEL = "qwen3-max"  # 使用项目标准模型
    
    print(f"📋 测试配置:")
    print(f"  模型: {MODEL}")
    print(f"  查询: {TEST_QUERY}")
    print(f"  版本: v1 精简版 vs v3 CoT版")
    
    # 运行测试
    results = []
    
    # 测试 v1
    result_v1 = test_prompt_version(
        get_v1_prompt,
        "v1 精简版",
        TEST_QUERY,
        MODEL
    )
    results.append(result_v1)
    
    print("\n" + "="*60)
    input("⏸️  按 Enter 继续测试 v3 版本...")
    
    # 测试 v3
    result_v3 = test_prompt_version(
        get_v3_prompt,
        "v3 CoT版",
        TEST_QUERY,
        MODEL
    )
    results.append(result_v3)
    
    # 对比总结
    print("\n" + "="*60)
    print("📊 对比总结")
    print("="*60)
    
    for r in results:
        if "error" not in r:
            print(f"\n{r['version']}:")
            print(f"  耗时: {r['duration']:.2f}s")
            print(f"  Token: {r['tokens']}")
            print(f"  图表: {'✅' if r['has_chart'] else '❌'}")
            print(f"  趋势分析: {'✅' if r['has_trend'] else '❌'}")
            print(f"  指标分析: {'✅' if r['has_indicator'] else '❌'}")
    
    print("\n💡 决策建议:")
    print("  - 如果两个版本质量相当，选择 Token 更少的 v1")
    print("  - 如果 v3 明显更准确，选择 v3")
    print("  - 记录实际 Token 数，更新实验报告")
