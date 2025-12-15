"""
Financial Data Fetch Skill Implementation

复用 core/data_fetcher.py 的逻辑，提供 Skill 标准接口。
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.base_skill import BaseSkill
from core.data_fetcher import fetch_stock_daily, fetch_etf_daily


class FinancialDataFetchSkill(BaseSkill):
    """
    Financial Data Fetch Skill
    
    提供股票和ETF数据获取功能。
    """
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        返回工具定义
        
        Returns:
            List[Dict]: 包含 fetch_stock_data 和 fetch_etf_data 两个工具
        """
        return [
            {
                "name": "fetch_stock_data",
                "description": "获取A股历史数据（日K线）。参数：symbol（股票代码，6位数字），days（天数，默认30）。返回包含日期、开盘、收盘、最高、最低、成交量等字段的DataFrame。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码（6位数字，如 '000001' 表示平安银行）"
                        },
                        "days": {
                            "type": "integer",
                            "description": "数据天数，默认30天，最大365天",
                            "default": 30
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "fetch_etf_data",
                "description": "获取ETF历史数据（日K线）。参数：symbol（ETF代码，6位数字），days（天数，默认30）。返回包含日期、开盘、收盘、最高、最低、成交量等字段的DataFrame。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "ETF代码（6位数字，如 '510300' 表示沪深300ETF）"
                        },
                        "days": {
                            "type": "integer",
                            "description": "数据天数，默认30天，最大365天",
                            "default": 30
                        }
                    },
                    "required": ["symbol"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称（fetch_stock_data 或 fetch_etf_data）
            tool_input: 工具参数（symbol, days）
        
        Returns:
            Dict: 包含 success, data, message 的结果字典
        
        Raises:
            ValueError: 如果工具名称不存在
        """
        if tool_name == "fetch_stock_data":
            return self._fetch_stock(tool_input)
        
        elif tool_name == "fetch_etf_data":
            return self._fetch_etf(tool_input)
        
        else:
            raise ValueError(
                f"Unknown tool: {tool_name}. "
                f"Available tools: fetch_stock_data, fetch_etf_data"
            )
    
    def _fetch_stock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取股票数据（内部方法）
        
        Args:
            params: 包含 symbol 和可选的 days
        
        Returns:
            Dict: 执行结果
        """
        symbol = params.get("symbol")
        days = params.get("days", 30)
        
        # 参数验证
        if not symbol:
            return {
                "success": False,
                "error": "缺少必需参数: symbol",
                "data": None
            }
        
        if not isinstance(symbol, str) or len(symbol) != 6 or not symbol.isdigit():
            return {
                "success": False,
                "error": f"股票代码格式错误: {symbol}（必须为6位数字）",
                "data": None
            }
        
        if not isinstance(days, int) or days < 1 or days > 365:
            return {
                "success": False,
                "error": f"天数参数错误: {days}（范围: [1, 365]）",
                "data": None
            }
        
        try:
            # 调用 core/data_fetcher.py 的函数（使用正确的函数名）
            from datetime import datetime, timedelta
            
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            
            df = fetch_stock_daily(symbol, start_date, end_date, adjust="qfq")
            
            if df is None or df.empty:
                return {
                    "success": False,
                    "error": f"未获取到数据（股票代码: {symbol}）。可能原因：代码错误、已退市或停牌",
                    "data": None
                }
            
            return {
                "success": True,
                "data": df,
                "rows": len(df),
                "symbol": symbol,
                "days": days,
                "message": f"成功获取股票 {symbol} 的 {len(df)} 条数据"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"获取股票数据失败: {str(e)}",
                "data": None
            }
    
    def _fetch_etf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取ETF数据（内部方法）
        
        Args:
            params: 包含 symbol 和可选的 days
        
        Returns:
            Dict: 执行结果
        """
        symbol = params.get("symbol")
        days = params.get("days", 30)
        
        # 参数验证
        if not symbol:
            return {
                "success": False,
                "error": "缺少必需参数: symbol",
                "data": None
            }
        
        if not isinstance(symbol, str) or len(symbol) != 6 or not symbol.isdigit():
            return {
                "success": False,
                "error": f"ETF代码格式错误: {symbol}（必须为6位数字）",
                "data": None
            }
        
        if not isinstance(days, int) or days < 1 or days > 365:
            return {
                "success": False,
                "error": f"天数参数错误: {days}（范围: [1, 365]）",
                "data": None
            }
        
        try:
            # 调用 core/data_fetcher.py 的函数（使用正确的函数名）
            from datetime import datetime, timedelta
            
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            
            df = fetch_etf_daily(symbol, start_date, end_date, adjust="qfq")
            
            if df is None or df.empty:
                return {
                    "success": False,
                    "error": f"未获取到数据（ETF代码: {symbol}）。可能原因：代码错误、已退市或停牌",
                    "data": None
                }
            
            return {
                "success": True,
                "data": df,
                "rows": len(df),
                "symbol": symbol,
                "days": days,
                "message": f"成功获取ETF {symbol} 的 {len(df)} 条数据"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"获取ETF数据失败: {str(e)}",
                "data": None
            }
