# 📈 金融数据分析助手

> 基于 LLM 的智能金融数据分析工具，支持 A 股和 ETF 的技术分析与可视化

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 功能特性

- **🤖 自然语言交互**: 用自然语言描述分析需求，Agent 自动调用工具完成分析
- **📊 多数据源支持**: 集成 AKShare，支持 A 股、ETF 等金融产品
- **📐 专业技术指标**: 自动计算 MA、MACD、RSI、布林带等常用技术指标
- **📉 精美可视化**: 生成专业 K 线图，支持中文显示和 Markdown 渲染
- **🔧 模块化设计**: Core-Logic 分离，易于扩展和维护
- **🎨 交互式开发**: 基于 Jupyter Notebook 的可视化调试环境

## 📂 项目结构

```
金融数据分析助手/
├── core/                          # 核心基础设施
│   ├── __init__.py
│   ├── llm_client.py             # 统一 LLM 客户端（支持多模型）
│   ├── safe_parsing.py           # 防御性 JSON 解析
│   ├── ui_utils.py               # UI 工具（支持 Markdown 渲染）
│   ├── result_display.py         # 结果显示封装
│   ├── data_fetcher.py           # 数据获取（AKShare）
│   ├── indicators.py             # 技术指标计算
│   └── visualization.py          # 图表生成（支持中文字体）
│
├── agent_logic.py                 # Agent 主逻辑（ReAct 模式）
├── financial_agent_demo.ipynb     # 交互式演示笔记本
│
├── docs.md                        # 项目文档
├── spec.md                        # 技术规格说明
├── requirements.txt               # 依赖清单
├── .env.example                   # 环境变量模板
└── README.md                      # 本文件
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 克隆项目（如果还未克隆）
cd "My Agents/金融数据分析助手"

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Keys
```

### 2. 运行演示笔记本

```bash
# 启动 Jupyter Notebook
jupyter notebook financial_agent_demo.ipynb
```

### 3. 使用 Python 脚本

```python
from agent_logic import analyze_stock

# 分析贵州茅台最近 60 天的走势
result = analyze_stock(
    symbol="600519",
    days=60,
    model="gpt-4o-mini"
)

if result["success"]:
    print(result["final_answer"])
```

## 💡 使用示例

### 示例 1: 快速分析股票

```python
from agent_logic import run_agent

query = "帮我分析一下贵州茅台（600519）最近三个月的走势"
result = run_agent(query, model="gpt-4o-mini", verbose=True)
```

### 示例 2: ETF 技术分析

```python
query = "分析沪深300ETF（510300）的技术指标，重点看 MACD 和 RSI"
result = run_agent(query, model="gpt-4o-mini")
```

### 示例 3: 手动调用工具

```python
from core.data_fetcher import fetch_stock_daily
from core.indicators import add_all_indicators
from core.visualization import plot_comprehensive_chart
from datetime import datetime, timedelta

# 获取数据
end_date = datetime.now().strftime("%Y%m%d")
start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")

df = fetch_stock_daily("600519", start_date, end_date)

# 计算指标
df_with_indicators = add_all_indicators(df)

# 生成图表
chart_path = plot_comprehensive_chart(
    df_with_indicators,
    title="贵州茅台技术分析"
)
```

## 🛠️ 支持的工具

Agent 内置以下工具：

| 工具名称 | 功能 | 参数 |
| :--- | :--- | :--- |
| `fetch_stock_data` | 获取 A 股历史数据 | symbol, start_date, end_date |
| `fetch_etf_data` | 获取 ETF 历史数据 | symbol, start_date, end_date |
| `analyze_and_plot` | 分析数据并生成图表 | data_id, chart_type |

## 📊 支持的技术指标

- **MA (Moving Average)**: 移动平均线（5日、10日、20日、60日）
- **MACD**: 异同移动平均线（快线、慢线、柱状图）
- **RSI**: 相对强弱指标（14日）
- **Bollinger Bands**: 布林带（上轨、中轨、下轨）
- **Volume MA**: 成交量均线

## 🎨 UI 优化特性

- **Markdown 自动渲染**: AI 输出自动识别并美化显示（标题、列表、代码、引用）
- **中文字体支持**: 自动检测系统字体（macOS: STHeiti/PingFang SC）
- **嵌套列表处理**: 智能规范化缩进，完美渲染复杂列表
- **精美卡片样式**: 统一渐变边框，响应式布局

## 🔑 支持的 LLM 模型

本项目通过统一的 `llm_client` 支持多种 LLM：

- **OpenAI**: GPT-4, GPT-4o, GPT-3.5
- **阿里云**: 通义千问（Qwen）
- **智谱 AI**: GLM-4
- **DeepSeek**: DeepSeek-Chat
- **Moonshot AI**: Kimi

只需在 `.env` 文件中配置相应的 API Key 即可。

## 📖 项目文档

## 📖 项目文档

- **`README.md`**: 项目介绍、快速开始、使用示例
- **`docs.md`**: 功能特性、技术栈、开发路线
- **`spec.md`**: 系统角色、工具接口、数据结构
- **`PROJECT_SUMMARY.md`**: 项目搭建完成报告

## 🧪 测试与验证

每个核心模块都包含测试代码，可独立运行：

```bash
# 测试数据获取
python core/data_fetcher.py

# 测试指标计算
python core/indicators.py

# 测试图表生成（含中文字体）
python core/visualization.py

# 测试 Agent 逻辑
python agent_logic.py

# 测试 UI 工具（Markdown 渲染）
python core/ui_utils.py
```

## 🔧 扩展开发

### 添加新的技术指标

在 `core/indicators.py` 中添加计算函数：

```python
def calculate_custom_indicator(df: pd.DataFrame) -> pd.DataFrame:
    # 你的指标计算逻辑
    df['custom_indicator'] = ...
    return df
```

### 注册新的工具

在 `agent_logic.py` 中定义工具函数并注册：

```python
def tool_custom_analysis(**kwargs):
    # 你的工具逻辑
    return result

TOOLS["custom_analysis"] = tool_custom_analysis
```

然后在 `SYSTEM_PROMPT` 中添加工具说明。

## ⚠️ 注意事项

1. **数据仅供参考**: AKShare 数据来源于公开网站，不保证实时性和准确性
2. **非投资建议**: 本工具生成的分析报告仅用于学习研究，不构成投资建议
3. **API 限流**: 部分数据源可能有访问频率限制，请合理使用
4. **环境变量**: 不要将 `.env` 文件提交到版本控制系统
5. **中文显示**: 图表自动配置系统中文字体，若显示异常请检查字体安装

## 🔧 技术亮点

- **智能缩进规范化**: 自动将 LLM 输出的 2-3 空格缩进规范化为标准 4 空格
- **标准 Markdown 库**: 使用 Python `markdown` 库替代自定义解析器，支持完整语法
- **跨平台字体支持**: 自动检测 macOS/Windows/Linux 系统字体
- **mplfinance 字体传递**: 通过 `rc` 参数将字体配置传递给 mplfinance

## 📚 参考资料

- [AKShare 官方文档](https://akshare.akfamily.xyz/)
- [mplfinance 文档](https://github.com/matplotlib/mplfinance)
- [技术指标说明](https://www.investopedia.com/technical-analysis-4689657)
- [ReAct 模式论文](https://arxiv.org/abs/2210.03629)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 开源协议。

---

**Happy Analyzing!** 📈✨
