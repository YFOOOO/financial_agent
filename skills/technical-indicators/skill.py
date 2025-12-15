"""
Technical Indicators Skill Implementation

复用 core/indicators.py 的逻辑，提供 Skill 标准接口。
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.base_skill import BaseSkill
from core.indicators import (
    calculate_ma,
    calculate_macd,
    calculate_rsi,
    calculate_bollinger_bands,
    add_all_indicators
)


class TechnicalIndicatorsSkill(BaseSkill):
    """
    Technical Indicators Skill
    
    提供技术指标计算功能。
    """
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        返回工具定义
        
        Returns:
            List[Dict]: 包含 MA, MACD, RSI, BOLL, 批量计算 五个工具
        """
        return [
            {
                "name": "calculate_ma",
                "description": "计算移动平均线（MA）。参数：data（包含'收盘'列的DataFrame），periods（周期列表，默认[5,10,20,60]）。返回新增MA列的DataFrame。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "包含'收盘'列的DataFrame数据"
                        },
                        "periods": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "MA周期列表（如[5,10,20]）",
                            "default": [5, 10, 20, 60]
                        }
                    },
                    "required": ["data"]
                }
            },
            {
                "name": "calculate_macd",
                "description": "计算MACD指标。参数：data（包含'收盘'列的DataFrame），fast_period（快线周期，默认12），slow_period（慢线周期，默认26），signal_period（信号线周期，默认9）。返回新增MACD_DIF、MACD_DEA、MACD_BAR列的DataFrame。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "包含'收盘'列的DataFrame数据"
                        },
                        "fast_period": {
                            "type": "integer",
                            "description": "快线周期",
                            "default": 12
                        },
                        "slow_period": {
                            "type": "integer",
                            "description": "慢线周期",
                            "default": 26
                        },
                        "signal_period": {
                            "type": "integer",
                            "description": "信号线周期",
                            "default": 9
                        }
                    },
                    "required": ["data"]
                }
            },
            {
                "name": "calculate_rsi",
                "description": "计算RSI指标。参数：data（包含'收盘'列的DataFrame），period（周期，默认14）。返回新增RSI列的DataFrame。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "包含'收盘'列的DataFrame数据"
                        },
                        "period": {
                            "type": "integer",
                            "description": "RSI周期",
                            "default": 14
                        }
                    },
                    "required": ["data"]
                }
            },
            {
                "name": "calculate_boll",
                "description": "计算布林带（BOLL）指标。参数：data（包含'收盘'列的DataFrame），period（周期，默认20），std_dev（标准差倍数，默认2.0）。返回新增BOLL_MIDDLE、BOLL_UPPER、BOLL_LOWER列的DataFrame。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "包含'收盘'列的DataFrame数据"
                        },
                        "period": {
                            "type": "integer",
                            "description": "MA周期",
                            "default": 20
                        },
                        "std_dev": {
                            "type": "number",
                            "description": "标准差倍数",
                            "default": 2.0
                        }
                    },
                    "required": ["data"]
                }
            },
            {
                "name": "calculate_all_indicators",
                "description": "批量计算所有技术指标（MA、MACD、RSI、BOLL）。参数：data（包含OHLCV列的DataFrame）。返回新增所有指标列的DataFrame。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "包含'开盘'、'最高'、'最低'、'收盘'、'成交量'列的DataFrame数据"
                        }
                    },
                    "required": ["data"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称
            tool_input: 工具参数
        
        Returns:
            Dict: 执行结果
        
        Raises:
            ValueError: 如果工具名称不存在
        """
        tool_map = {
            "calculate_ma": self._calculate_ma,
            "calculate_macd": self._calculate_macd,
            "calculate_rsi": self._calculate_rsi,
            "calculate_boll": self._calculate_boll,
            "calculate_all_indicators": self._calculate_all
        }
        
        handler = tool_map.get(tool_name)
        if handler is None:
            raise ValueError(
                f"Unknown tool: {tool_name}. "
                f"Available tools: {list(tool_map.keys())}"
            )
        
        return handler(tool_input)
    
    def _validate_dataframe(self, df: Any, required_columns: List[str]) -> Dict[str, Any]:
        """
        验证 DataFrame 输入
        
        Args:
            df: 输入数据
            required_columns: 必需列名列表
        
        Returns:
            Dict: 验证结果，包含 success 和 error
        """
        if not isinstance(df, pd.DataFrame):
            return {
                "success": False,
                "error": "输入数据必须为 pandas DataFrame"
            }
        
        if df.empty:
            return {
                "success": False,
                "error": "DataFrame 为空，无法计算指标"
            }
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return {
                "success": False,
                "error": f"DataFrame 缺少必需列: {missing_cols}"
            }
        
        return {"success": True}
    
    def _calculate_ma(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """计算 MA"""
        df = params.get("data")
        periods = params.get("periods", [5, 10, 20, 60])
        
        # 验证输入
        validation = self._validate_dataframe(df, ["收盘"])
        if not validation["success"]:
            return {"success": False, "error": validation["error"], "data": None}
        
        try:
            # 调用 core/indicators.py（需要列名为'close'）
            df_copy = df.copy()
            df_copy['close'] = df_copy['收盘']
            
            result = calculate_ma(df_copy, periods=periods)
            
            # 将列名映射回中文
            for period in periods:
                result[f'MA{period}'] = result[f'ma_{period}']
                result.drop(f'ma_{period}', axis=1, inplace=True)
            
            result.drop('close', axis=1, inplace=True, errors='ignore')
            
            return {
                "success": True,
                "data": result,
                "message": f"成功计算 MA 指标（周期: {periods}）"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"MA 计算失败: {str(e)}",
                "data": None
            }
    
    def _calculate_macd(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """计算 MACD"""
        df = params.get("data")
        fast = params.get("fast_period", 12)
        slow = params.get("slow_period", 26)
        signal = params.get("signal_period", 9)
        
        validation = self._validate_dataframe(df, ["收盘"])
        if not validation["success"]:
            return {"success": False, "error": validation["error"], "data": None}
        
        try:
            df_copy = df.copy()
            df_copy['close'] = df_copy['收盘']
            
            result = calculate_macd(df_copy, fast_period=fast, slow_period=slow, signal_period=signal)
            
            # 映射列名
            result['MACD_DIF'] = result['macd']
            result['MACD_DEA'] = result['macd_signal']
            result['MACD_BAR'] = result['macd_hist']
            result.drop(['macd', 'macd_signal', 'macd_hist', 'close'], axis=1, inplace=True, errors='ignore')
            
            return {
                "success": True,
                "data": result,
                "message": f"成功计算 MACD 指标（{fast}-{slow}-{signal}）"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"MACD 计算失败: {str(e)}",
                "data": None
            }
    
    def _calculate_rsi(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """计算 RSI"""
        df = params.get("data")
        period = params.get("period", 14)
        
        validation = self._validate_dataframe(df, ["收盘"])
        if not validation["success"]:
            return {"success": False, "error": validation["error"], "data": None}
        
        try:
            df_copy = df.copy()
            df_copy['close'] = df_copy['收盘']
            
            result = calculate_rsi(df_copy, period=period)
            
            result['RSI'] = result['rsi']
            result.drop(['rsi', 'close'], axis=1, inplace=True, errors='ignore')
            
            return {
                "success": True,
                "data": result,
                "message": f"成功计算 RSI 指标（周期: {period}）"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"RSI 计算失败: {str(e)}",
                "data": None
            }
    
    def _calculate_boll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """计算 BOLL"""
        df = params.get("data")
        period = params.get("period", 20)
        std_dev = params.get("std_dev", 2.0)
        
        validation = self._validate_dataframe(df, ["收盘"])
        if not validation["success"]:
            return {"success": False, "error": validation["error"], "data": None}
        
        try:
            df_copy = df.copy()
            df_copy['close'] = df_copy['收盘']
            
            result = calculate_bollinger_bands(df_copy, period=period, std_dev=std_dev)
            
            result['BOLL_MIDDLE'] = result['bb_middle']
            result['BOLL_UPPER'] = result['bb_upper']
            result['BOLL_LOWER'] = result['bb_lower']
            result.drop(['bb_middle', 'bb_upper', 'bb_lower', 'close'], axis=1, inplace=True, errors='ignore')
            
            return {
                "success": True,
                "data": result,
                "message": f"成功计算 BOLL 指标（周期: {period}, 标准差: {std_dev}）"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"BOLL 计算失败: {str(e)}",
                "data": None
            }
    
    def _calculate_all(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """批量计算所有指标"""
        df = params.get("data")
        
        required = ["开盘", "最高", "最低", "收盘", "成交量"]
        validation = self._validate_dataframe(df, required)
        if not validation["success"]:
            return {"success": False, "error": validation["error"], "data": None}
        
        try:
            df_copy = df.copy()
            # 列名映射
            df_copy['open'] = df_copy['开盘']
            df_copy['high'] = df_copy['最高']
            df_copy['low'] = df_copy['最低']
            df_copy['close'] = df_copy['收盘']
            df_copy['volume'] = df_copy['成交量']
            
            result = add_all_indicators(df_copy)
            
            # 映射列名回中文（仅保留中文列和指标列）
            result.drop(['open', 'high', 'low', 'close', 'volume'], axis=1, inplace=True, errors='ignore')
            
            return {
                "success": True,
                "data": result,
                "message": "成功计算所有技术指标（MA、MACD、RSI、BOLL）"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"批量计算失败: {str(e)}",
                "data": None
            }
