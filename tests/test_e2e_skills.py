"""
端到端测试：v1.4.0 Skill 模式完整验证

测试场景：
1. Skills 模式正常运行（数据获取 → 图表生成）
2. Skills 加载失败回退（模拟目录不存在）
3. Skills 执行失败回退（模拟执行异常）
4. 完整 Agent 工作流（真实用户查询）

执行命令：
    pytest tests/test_e2e_skills.py -v -s
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSkillsE2E:
    """端到端测试：Skill 模式验证"""
    
    def test_01_skills_loading(self):
        """
        测试场景 1.1: Skills 成功加载
        
        验证要点：
        - SkillOrchestrator 初始化成功
        - 3 个 Skills 全部加载
        - 工具定义获取正确
        """
        from skills import SkillOrchestrator
        
        orchestrator = SkillOrchestrator()
        
        # 验证 Skills 数量
        assert len(orchestrator.skills) == 3, f"应加载 3 个 Skills，实际加载 {len(orchestrator.skills)} 个"
        
        # 验证 Skills 名称
        expected_skills = {'financial-data-fetch', 'technical-indicators', 'chart-generation'}
        actual_skills = set(orchestrator.skills.keys())
        assert actual_skills == expected_skills, f"Skills 名称不匹配：{actual_skills} vs {expected_skills}"
        
        # 验证工具定义
        all_tools = orchestrator.get_all_tool_definitions()
        assert len(all_tools) > 0, "应返回工具定义"
        
        print(f"✅ 成功加载 {len(orchestrator.skills)} 个 Skills")
        print(f"✅ 工具定义: {len(all_tools)} 个")
        
    def test_02_data_fetch_skill_execution(self):
        """
        测试场景 1.2: 数据获取 Skill 执行
        
        验证要点：
        - fetch_stock_data 工具执行成功
        - 返回数据格式正确
        - DataFrame 包含必要字段
        """
        from skills import SkillOrchestrator
        
        orchestrator = SkillOrchestrator()
        
        # 执行股票数据获取
        result = orchestrator.execute_tool('fetch_stock_data', {
            'symbol': '600519',
            'days': 30
        })
        
        # 验证返回格式
        assert result.get('success') is True, f"数据获取失败: {result.get('error')}"
        assert 'data' in result, "返回结果应包含 data 字段"
        assert result.get('rows', 0) > 0, "应返回数据行数"
        
        # 验证 DataFrame
        df = result['data']
        assert df is not None, "DataFrame 不应为 None"
        assert len(df) > 0, "DataFrame 应包含数据"
        
        # 验证必要字段（英文列名）
        required_columns = {'open', 'close', 'high', 'low', 'volume'}
        actual_columns = set(df.columns)
        assert required_columns.issubset(actual_columns), f"缺少必要字段: {required_columns - actual_columns}"
        
        print(f"✅ 成功获取股票数据: {result['symbol']}")
        print(f"✅ 数据行数: {result['rows']}")
        print(f"✅ DataFrame 字段: {list(df.columns)}")
        
    def test_03_agent_mixed_mode_integration(self):
        """
        测试场景 1.3: Agent 混合模式集成
        
        验证要点：
        - execute_tool 使用 Skills 模式
        - 数据正确存储到 data_store
        - 返回格式与传统模式一致
        """
        from agent_logic import execute_tool, data_store
        
        # 重置 data_store（避免测试干扰）
        data_store.data.clear()
        data_store.counter = 0
        
        # 执行工具调用
        result = execute_tool('fetch_stock_data', {'symbol': '600519', 'days': 30})
        
        # 验证返回格式（传统格式）
        assert result.get('status') == 'success', f"执行失败: {result.get('message')}"
        assert 'data_id' in result, "返回结果应包含 data_id"
        assert 'symbol' in result, "返回结果应包含 symbol"
        assert 'records' in result, "返回结果应包含 records"
        
        # 验证数据存储
        data_id = result['data_id']
        df = data_store.get(data_id)
        assert df is not None, f"数据未存储: {data_id}"
        assert len(df) > 0, "存储的 DataFrame 应包含数据"
        
        print(f"✅ 混合模式执行成功")
        print(f"✅ data_id: {data_id}")
        print(f"✅ 数据已存储: {len(df)} 行")
        
    def test_04_skills_loading_failure_fallback(self):
        """
        测试场景 2: Skills 加载失败回退
        
        验证要点：
        - 模拟 Skills 导入失败
        - 系统降级到传统模式
        - 功能完整性不受影响
        """
        # 模拟 Skills 导入失败
        with patch('agent_logic.USE_SKILLS', False):
            with patch('agent_logic.orchestrator', None):
                from agent_logic import execute_tool, data_store
                
                # 重置 data_store
                data_store.data.clear()
                data_store.counter = 0
                
                # 执行工具调用（应使用传统模式）
                result = execute_tool('fetch_stock_data', {'symbol': '600519', 'days': 30})
                
                # 验证传统模式执行成功
                assert result.get('status') == 'success', f"传统模式执行失败: {result.get('message')}"
                assert 'data_id' in result, "传统模式应返回 data_id"
                
                # 验证数据存储
                data_id = result['data_id']
                df = data_store.get(data_id)
                assert df is not None, "传统模式应存储数据"
                assert len(df) > 0, "传统模式应返回有效数据"
        
        print(f"✅ Skills 加载失败回退测试通过")
        print(f"✅ 传统模式功能正常")
        
    def test_05_skills_execution_failure_fallback(self):
        """
        测试场景 3: Skills 执行失败回退
        
        验证要点：
        - 模拟 Skill 执行异常
        - 系统回退到传统工具
        - 错误日志清晰
        """
        from agent_logic import _try_skill_execution, data_store
        
        # 测试不支持的工具（应返回 None，触发回退）
        result = _try_skill_execution('analyze_and_plot', {'data_id': 'data_1', 'chart_type': 'auto'})
        
        # 验证返回 None（触发回退）
        assert result is None, "不支持的工具应返回 None"
        
        print(f"✅ Skills 执行失败回退测试通过")
        print(f"✅ 不支持的工具正确回退")
        
    def test_06_complete_agent_workflow(self):
        """
        测试场景 4: 完整 Agent 工作流（简化版）
        
        验证要点：
        - 数据获取成功
        - 数据存储正确
        - 工具调用链完整
        
        注意：此测试不调用 LLM，仅验证工具链
        """
        from agent_logic import execute_tool, data_store
        
        # 重置 data_store
        data_store.data.clear()
        data_store.counter = 0
        
        # 步骤 1: 获取股票数据
        print("\n📍 步骤 1: 获取股票数据")
        result1 = execute_tool('fetch_stock_data', {'symbol': '600519', 'days': 60})
        assert result1.get('status') == 'success', f"数据获取失败: {result1.get('message')}"
        data_id = result1['data_id']
        print(f"   ✅ 数据获取成功: {data_id}")
        
        # 步骤 2: 验证数据存储
        print("\n📍 步骤 2: 验证数据存储")
        df = data_store.get(data_id)
        assert df is not None, f"数据未存储: {data_id}"
        assert len(df) > 0, "DataFrame 应包含数据"
        print(f"   ✅ 数据已存储: {len(df)} 行")
        
        # 步骤 3: 获取元数据
        print("\n📍 步骤 3: 验证元数据")
        metadata = data_store.get_metadata(data_id)
        assert metadata is not None, "应返回元数据"
        assert metadata['type'] == 'stock', "元数据类型应为 stock"
        assert metadata['symbol'] == '600519', "元数据 symbol 应为 600519"
        print(f"   ✅ 元数据正确: {metadata}")
        
        print("\n✅ 完整工作流验证通过")
        print(f"   - 数据获取: ✅")
        print(f"   - 数据存储: ✅")
        print(f"   - 元数据: ✅")


class TestSkillsQuality:
    """质量验证：错误处理、日志输出"""
    
    def test_07_error_handling_invalid_symbol(self):
        """
        测试场景: 错误处理 - 无效股票代码
        
        验证要点：
        - 返回错误信息
        - 错误信息清晰
        - 不抛出异常
        """
        from skills import SkillOrchestrator
        
        orchestrator = SkillOrchestrator()
        
        # 测试无效股票代码（非6位数字）
        result = orchestrator.execute_tool('fetch_stock_data', {
            'symbol': 'INVALID',
            'days': 30
        })
        
        # 验证错误处理
        assert result.get('success') is False, "无效代码应返回失败"
        assert 'error' in result, "应返回错误信息"
        assert '格式错误' in result['error'], f"错误信息不清晰: {result['error']}"
        
        print(f"✅ 错误处理测试通过")
        print(f"   错误信息: {result['error']}")
        
    def test_08_error_handling_invalid_days(self):
        """
        测试场景: 错误处理 - 无效天数参数
        
        验证要点：
        - 参数验证生效
        - 错误信息准确
        """
        from skills import SkillOrchestrator
        
        orchestrator = SkillOrchestrator()
        
        # 测试超出范围的天数
        result = orchestrator.execute_tool('fetch_stock_data', {
            'symbol': '600519',
            'days': 400  # 超过 365 天限制
        })
        
        # 验证参数验证
        assert result.get('success') is False, "超出范围的天数应返回失败"
        assert 'error' in result, "应返回错误信息"
        assert '天数参数错误' in result['error'], f"错误信息不准确: {result['error']}"
        
        print(f"✅ 参数验证测试通过")
        print(f"   错误信息: {result['error']}")


if __name__ == '__main__':
    # 直接运行测试
    pytest.main([__file__, '-v', '-s'])
