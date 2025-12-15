"""
Chart Generation Skill Implementation

复用 core/visualization.py 的逻辑，提供 Skill 标准接口。
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.base_skill import BaseSkill
from core.visualization import plot_basic_chart, plot_comprehensive_chart


class ChartGenerationSkill(BaseSkill):
    """
    Chart Generation Skill
    
    提供金融图表生成功能。
    """
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        返回工具定义
        
        Returns:
            List[Dict]: 包含 generate_candlestick_chart 和 generate_comprehensive_chart 两个工具
        """
        return [
            {
                "name": "generate_candlestick_chart",
                "description": "生成基础K线图（蜡烛图+成交量）。参数：data（包含OHLCV的DataFrame），symbol（股票代码，可选），title（标题，可选），theme（主题dark/light，默认dark），save_path（保存路径，可选）。返回包含success和saved_path的结果。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "包含日期、开盘、收盘、最高、最低、成交量列的DataFrame"
                        },
                        "symbol": {
                            "type": "string",
                            "description": "股票代码（如'000001'），用于标题",
                            "default": ""
                        },
                        "title": {
                            "type": "string",
                            "description": "自定义图表标题",
                            "default": ""
                        },
                        "theme": {
                            "type": "string",
                            "enum": ["dark", "light"],
                            "description": "图表主题（dark深色/light浅色）",
                            "default": "dark"
                        },
                        "save_path": {
                            "type": "string",
                            "description": "保存路径（如'output/chart.png'），不指定则不保存",
                            "default": ""
                        }
                    },
                    "required": ["data"]
                }
            },
            {
                "name": "generate_comprehensive_chart",
                "description": "生成综合技术分析图表（K线+MA+MACD+成交量）。参数：data（包含OHLCV和技术指标的DataFrame），symbol（股票代码，可选），title（标题，可选），theme（主题，默认dark），save_path（保存路径，可选）。返回包含success和saved_path的结果。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "包含OHLCV和技术指标（MA_5/10/20/60, MACD_DIF/DEA/BAR）的DataFrame"
                        },
                        "symbol": {
                            "type": "string",
                            "description": "股票代码",
                            "default": ""
                        },
                        "title": {
                            "type": "string",
                            "description": "自定义图表标题",
                            "default": ""
                        },
                        "theme": {
                            "type": "string",
                            "enum": ["dark", "light"],
                            "description": "图表主题",
                            "default": "dark"
                        },
                        "save_path": {
                            "type": "string",
                            "description": "保存路径",
                            "default": ""
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
        if tool_name == "generate_candlestick_chart":
            return self._generate_basic_chart(tool_input)
        
        elif tool_name == "generate_comprehensive_chart":
            return self._generate_comprehensive_chart(tool_input)
        
        else:
            raise ValueError(
                f"Unknown tool: {tool_name}. "
                f"Available tools: generate_candlestick_chart, generate_comprehensive_chart"
            )
    
    def _generate_basic_chart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成基础K线图（内部方法）
        
        Args:
            params: 包含 data 和可选的 symbol, title, theme, save_path
        
        Returns:
            Dict: 执行结果
        """
        data = params.get("data")
        symbol = params.get("symbol", "")
        title = params.get("title", "")
        theme = params.get("theme", "dark")
        save_path = params.get("save_path", "")
        
        # 数据验证
        validation = self._validate_chart_data(data)
        if not validation["success"]:
            return validation
        
        # 主题验证
        if theme not in ["dark", "light"]:
            return {
                "success": False,
                "error": f"无效的主题: {theme}（必须是 'dark' 或 'light'）",
                "saved_path": None
            }
        
        try:
            # 生成标题
            if not title:
                if symbol:
                    title = f"{symbol} K线图"
                else:
                    title = "K线图"
            
            # 调用 core/visualization.py 的函数
            result_path = plot_basic_chart(
                data=data,
                title=title,
                save_path=save_path if save_path else None
            )
            
            return {
                "success": True,
                "message": f"成功生成K线图: {title}",
                "saved_path": result_path if save_path else None,
                "chart_type": "basic",
                "theme": theme
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"生成K线图失败: {str(e)}",
                "saved_path": None
            }
    
    def _generate_comprehensive_chart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合技术图表（内部方法）
        
        Args:
            params: 包含 data 和可选的 symbol, title, theme, save_path
        
        Returns:
            Dict: 执行结果
        """
        data = params.get("data")
        symbol = params.get("symbol", "")
        title = params.get("title", "")
        theme = params.get("theme", "dark")
        save_path = params.get("save_path", "")
        
        # 数据验证
        validation = self._validate_chart_data(data, check_indicators=True)
        if not validation["success"]:
            return validation
        
        # 主题验证
        if theme not in ["dark", "light"]:
            return {
                "success": False,
                "error": f"无效的主题: {theme}（必须是 'dark' 或 'light'）",
                "saved_path": None
            }
        
        try:
            # 生成标题
            if not title:
                if symbol:
                    rows = len(data)
                    title = f"{symbol} 技术分析（{rows}日）"
                else:
                    title = "技术分析图表"
            
            # 调用 core/visualization.py 的函数
            result_path = plot_comprehensive_chart(
                data=data,
                title=title,
                save_path=save_path if save_path else None
            )
            
            return {
                "success": True,
                "message": f"成功生成综合图表: {title}",
                "saved_path": result_path if save_path else None,
                "chart_type": "comprehensive",
                "theme": theme,
                "rows": len(data)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"生成综合图表失败: {str(e)}",
                "saved_path": None
            }
    
    def _validate_chart_data(
        self, 
        data: Any, 
        check_indicators: bool = False
    ) -> Dict[str, Any]:
        """
        验证图表数据（内部方法）
        
        Args:
            data: DataFrame 数据
            check_indicators: 是否检查技术指标列
        
        Returns:
            Dict: 验证结果
        """
        # 检查是否为 DataFrame
        if not isinstance(data, pd.DataFrame):
            return {
                "success": False,
                "error": f"数据类型错误: 期望 DataFrame，实际 {type(data).__name__}",
                "saved_path": None
            }
        
        # 检查是否为空
        if data.empty:
            return {
                "success": False,
                "error": "数据为空，无法生成图表",
                "saved_path": None
            }
        
        # 检查必需列（OHLCV）
        required_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量']
        
        # 允许日期作为索引或列
        if '日期' not in data.columns and data.index.name != '日期':
            # 检查是否有 DatetimeIndex
            if not isinstance(data.index, pd.DatetimeIndex):
                required_columns_display = ['开盘', '收盘', '最高', '最低', '成交量']
                missing = [col for col in required_columns_display if col not in data.columns]
                
                return {
                    "success": False,
                    "error": f"缺少必需列: {missing}，或缺少 DatetimeIndex",
                    "saved_path": None
                }
        
        # 检查其他必需列
        required_columns_check = ['开盘', '收盘', '最高', '最低', '成交量']
        missing_columns = [col for col in required_columns_check if col not in data.columns]
        
        if missing_columns:
            return {
                "success": False,
                "error": f"缺少必需列: {missing_columns}",
                "saved_path": None
            }
        
        # 如果需要，检查技术指标列
        if check_indicators:
            # 检查是否有至少一个技术指标
            indicator_columns = [
                'MA_5', 'MA_10', 'MA_20', 'MA_60',
                'MACD_DIF', 'MACD_DEA', 'MACD_BAR'
            ]
            
            has_indicators = any(col in data.columns for col in indicator_columns)
            
            if not has_indicators:
                return {
                    "success": False,
                    "error": "综合图表需要技术指标数据（MA、MACD等）。请先调用 technical-indicators Skill 计算指标。",
                    "saved_path": None
                }
        
        # 验证通过
        return {
            "success": True,
            "message": "数据验证通过"
        }
