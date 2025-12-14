# 🛠️ 金融数据分析助手 - 技术规格说明书

## 1. 系统角色 (System Role)
你是一名专业的**量化金融分析师助手**。你的任务是协助用户获取金融数据，通过计算技术指标和绘制图表来分析市场趋势。你的回答应当客观、数据驱动，并优先展示可视化的分析结果。

## 2. 架构设计 (Architecture)

### 2.1 交互流程 (Workflow)
```
用户输入 (自然语言)
    ↓
意图识别 (LLM Router)
    ↓
工具调用 (Tool Execution)
    ├─ fetch_stock_data/fetch_etf_data
    ├─ analyze_and_plot
    └─ 数据存储 (Memory DB)
    ↓
分析生成 (LLM Analysis)
    ├─ 结合数据摘要
    └─ 生成文字报告
    ↓
最终输出
    ├─ AI 报告 (Markdown 渲染)
    ├─ 技术指标表格
    ├─ 交易信号
    └─ 图表 (中文支持)
```

### 2.2 ReAct 循环
```python
while not finished and iterations < max_iterations:
    # Thought: LLM 分析当前状态
    thought = llm.think(user_query, history)
    
    # Action: 选择并执行工具
    action, params = parse_action(thought)
    result = execute_tool(action, params)
    
    # Observation: 记录结果
    history.append({"action": action, "result": result})
    
    # Check: 是否完成
    if has_answer(history):
        final_answer = llm.summarize(history)
        break
```

## 3. 工具定义 (Tools Definition)

### 3.1 数据获取工具

#### `fetch_stock_data`
```python
def tool_fetch_stock_data(symbol: str, days: int = 90) -> dict:
    """
    获取 A 股历史数据
    
    Args:
        symbol: 股票代码 (e.g., "600519")
        days: 获取天数 (default: 90)
    
    Returns:
        {
            "status": "success",
            "data_id": "stock_600519_20231001_20231231",
            "summary": {
                "symbol": "600519",
                "rows": 60,
                "date_range": ["2023-10-01", "2023-12-31"],
                "latest_close": 1450.50
            }
        }
    """
```

#### `fetch_etf_data`
```python
def tool_fetch_etf_data(symbol: str, days: int = 90) -> dict:
    """
    获取 ETF 历史数据
    
    Args:
        symbol: ETF 代码 (e.g., "510300")
        days: 获取天数 (default: 90)
    
    Returns:
        同 fetch_stock_data
    """
```

### 3.2 分析与绘图工具

#### `analyze_and_plot`
```python
def tool_analyze_and_plot(
    data_id: str,
    chart_type: str = "comprehensive"
) -> dict:
    """
    分析数据并生成图表
    
    Args:
        data_id: 数据 ID（从 fetch_* 工具返回）
        chart_type: 图表类型
            - "comprehensive": 综合技术分析图（默认）
            - "basic": 基础 K 线图
            - "ma": K 线 + 均线
    
    Returns:
        {
            "status": "success",
            "chart_path": "outputs/chart_20231214_120530.png",
            "indicators": {
                "ma_5": 1420.30,
                "ma_20": 1395.80,
                "rsi_14": 65.3,
                "macd": 12.5
            },
            "signals": {
                "ma_signal": "持有",
                "rsi_signal": "中性",
                "macd_signal": "持有"
            }
        }
    """
```

## 4. 数据结构 (Data Schema)

### 4.1 DataFrame 列名规范
确保各模块兼容的标准化列名：

```python
{
    # 基础 OHLCV
    "date": datetime (Index),
    "open": float,
    "high": float,
    "low": float,
    "close": float,
    "volume": float,
    
    # 移动平均线
    "ma_5": float,
    "ma_10": float,
    "ma_20": float,
    "ma_60": float,
    
    # MACD
    "macd": float,
    "macd_signal": float,
    "macd_hist": float,
    
    # RSI
    "rsi_14": float,
    
    # 布林带
    "bb_upper": float,
    "bb_middle": float,
    "bb_lower": float,
    
    # 成交量均线
    "volume_ma_5": float,
    "volume_ma_10": float
}
```

### 4.2 工具返回格式

#### 成功响应
```python
{
    "status": "success",
    "data_id": str,          # 数据标识符
    "chart_path": str,       # 图表路径（如有）
    "summary": dict,         # 数据摘要
    "indicators": dict,      # 技术指标（如有）
    "signals": dict          # 交易信号（如有）
}
```

#### 错误响应
```python
{
    "status": "error",
    "error": str,            # 错误信息
    "details": str           # 详细说明（可选）
}
```

## 5. UI 组件规范

### 5.1 Markdown 渲染
- **使用库**: Python `markdown` 库（v3.5+）
- **扩展**: `nl2br` (换行转 `<br>`)、`sane_lists` (列表处理)
- **缩进规范化**: 自动将 2-3 空格缩进转换为 4 空格
- **CSS 作用域**: `.pretty-card .markdown-content`

### 5.2 中文字体配置
```python
# 平台优先级
macOS:   ['PingFang SC', 'Heiti SC', 'STHeiti']
Windows: ['Microsoft YaHei', 'SimHei', 'KaiTi']
Linux:   ['WenQuanYi Micro Hei', 'Noto Sans CJK SC']

# matplotlib 配置
plt.rcParams['font.sans-serif'] = [selected_font, 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# mplfinance 传递
style = mpf.make_mpf_style(
    ...,
    rc={
        'font.sans-serif': [selected_font, 'DejaVu Sans'],
        'axes.unicode_minus': False
    }
)
```

## 6. 依赖库版本 (Requirements)

```text
# 核心依赖
python>=3.9

# LLM 客户端
openai>=1.0.0
anthropic>=0.18.0

# 金融数据
akshare>=1.13.0

# 数据处理
pandas>=2.0.0
numpy>=1.24.0

# 可视化
mplfinance>=0.12.9
matplotlib>=3.7.0

# Markdown 渲染
markdown>=3.5

# 配置管理
python-dotenv>=1.0.0

# Jupyter 支持
jupyter>=1.0.0
ipython>=8.12.0
```

## 7. 测试与验证

### 7.1 单元测试
每个核心模块包含测试代码：
```bash
python core/data_fetcher.py      # 测试数据获取
python core/indicators.py        # 测试指标计算
python core/visualization.py     # 测试图表生成（含中文）
python core/ui_utils.py          # 测试 Markdown 渲染
python agent_logic.py            # 测试 Agent 逻辑
```

### 7.2 集成测试
在 `financial_agent_demo.ipynb` 中：
- 测试完整的 ReAct 循环
- 验证 Markdown 嵌套列表渲染
- 验证中文字体显示
- 验证批量分析功能

## 8. 性能优化

### 8.1 缓存策略
- 数据存储在内存数据库 `DATA_STORAGE`
- 使用 `data_id` 避免重复获取

### 8.2 渲染优化
- Markdown 使用标准库（比自定义解析器快 10x）
- 图表使用非交互式后端 `matplotlib.use('Agg')`
- 自动清理旧图表文件（可选）

## 9. 安全性

- ✅ 环境变量隔离（`.env` 不提交）
- ✅ 防御性 JSON 解析（`safe_parsing.py`）
- ✅ 异常处理和日志记录
- ✅ 输入验证（股票代码、日期范围）
