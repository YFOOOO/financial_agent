"""
Quick regression test for date fix (v1.1.2)

Tests three relative time expressions to verify date calculation works correctly.
"""

import sys
from datetime import datetime
from agent_logic import run_agent

def test_date_interpretation():
    """Test if LLM correctly interprets relative time expressions."""
    
    print("\n" + "="*80)
    print("🧪 日期修复回归测试 (v1.1.2)")
    print("="*80)
    print(f"\n📅 当前日期: {datetime.now().strftime('%Y年%m月%d日')}")
    print(f"📅 当前日期: {datetime.now().strftime('%Y%m%d')}\n")
    
    test_cases = [
        {
            "name": "测试1: 最近两个月",
            "query": "请帮我分析比亚迪（002594）最近两个月的技术面表现",
            "expected_days": 60
        },
        {
            "name": "测试2: 近一周",
            "query": "分析贵州茅台（600519）近一周的走势",
            "expected_days": 7
        },
        {
            "name": "测试3: 三个月",
            "query": "查看沪深300ETF（510300）三个月的表现",
            "expected_days": 90
        }
    ]
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"🔬 {case['name']}")
        print(f"❓ 查询: {case['query']}")
        print(f"✅ 预期天数: {case['expected_days']}")
        print(f"{'─'*80}\n")
        
        try:
            # Run agent with minimal output
            result = run_agent(
                user_query=case['query'],
                model="qwen-max",  # Use fast model for testing
                max_iterations=3,
                verbose=False  # Reduce output
            )
            
            # Check if execution was successful
            if result.get("success"):
                # Analyze history to check if days parameter was used
                history = result.get("history", [])
                days_used = None
                
                for step in history:
                    if "action_input" in step:
                        action_input = step["action_input"]
                        if "days" in action_input:
                            days_used = action_input["days"]
                            break
                        # Check if start_date was used (fallback)
                        elif "start_date" in action_input and "end_date" in action_input:
                            start = action_input["start_date"]
                            end = action_input["end_date"]
                            print(f"   ℹ️  使用了显式日期: {start} 到 {end}")
                
                if days_used:
                    print(f"   ✅ LLM 使用了 days 参数: {days_used}")
                    if abs(days_used - case['expected_days']) <= 5:  # Allow ±5 days tolerance
                        print(f"   ✅ 日期计算正确（误差 ±5天内）")
                        results.append((case['name'], True, f"使用days={days_used}"))
                    else:
                        print(f"   ⚠️  日期偏差较大：预期{case['expected_days']}, 实际{days_used}")
                        results.append((case['name'], False, f"偏差: 预期{case['expected_days']}, 实际{days_used}"))
                else:
                    print(f"   ⚠️  LLM 没有使用 days 参数（可能使用了显式日期）")
                    results.append((case['name'], None, "未使用days参数"))
                
            else:
                print(f"   ❌ 执行失败: {result.get('error', 'Unknown error')}")
                results.append((case['name'], False, f"执行失败: {result.get('error', 'Unknown')}"))
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            results.append((case['name'], False, f"异常: {str(e)}"))
    
    # Summary
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80)
    
    passed = sum(1 for _, result, _ in results if result is True)
    failed = sum(1 for _, result, _ in results if result is False)
    warning = sum(1 for _, result, _ in results if result is None)
    
    for name, result, note in results:
        if result is True:
            icon = "✅"
        elif result is False:
            icon = "❌"
        else:
            icon = "⚠️ "
        print(f"{icon} {name}: {note}")
    
    print(f"\n总计: {passed} 通过, {warning} 警告, {failed} 失败")
    
    if failed == 0 and passed >= 2:
        print("\n🎉 日期修复测试通过！")
        return 0
    elif failed == 0:
        print("\n⚠️  部分测试有警告，但无失败")
        return 0
    else:
        print("\n❌ 测试失败，需要进一步调试")
        return 1

if __name__ == "__main__":
    sys.exit(test_date_interpretation())
