# 📈 金融数据分析助手 - 项目文档

## 1. 项目简介
本项目旨在构建一个基于 LLM 的金融数据分析助手，专注于**金融市场数据的获取、清洗、分析与可视化**。
助手能够根据用户指令，快速拉取特定股票或 ETF 的历史行情，计算关键技术指标，并生成专业的图表，辅助用户进行投资决策。

## 2. 核心功能

### 2.1 数据获取 (Data Fetching)
- **数据源**: [AKShare](https://github.com/akfamily/akshare)
- **支持市场**: 
    - A 股 (历史/实时)
    - ETF (交易所交易基金)
- **数据粒度**: 日线 (Daily)

### 2.2 数据分析 (Data Analysis)
- **基础统计**: 涨跌幅、波动率、成交量分析
- **技术指标**:
    - **MA (移动平均线)**: 识别趋势方向 (MA5, MA10, MA20, MA60)
    - **MACD (异同移动平均线)**: 判断买卖时机与动能
    - **RSI (相对强弱指标)**: 评估超买超卖状态
    - **Bollinger Bands (布林带)**: 波动性分析
    - **Volume MA (成交量均线)**: 成交量趋势

### 2.3 可视化 (Visualization)
- **K 线图**: 专业的蜡烛图展示
- **指标叠加**: 在主图叠加均线，副图展示 MACD/RSI
- **中文支持**: 自动配置系统中文字体（macOS: STHeiti/PingFang SC）
- **图表保存**: 自动保存分析图表到 `outputs/` 目录

### 2.4 UI 优化 (User Interface)
- **Markdown 渲染**: AI 输出自动识别并美化（使用标准 `markdown` 库）
- **嵌套列表支持**: 智能规范化 2-3 空格缩进为标准 4 空格
- **精美卡片**: 渐变边框、响应式布局
- **多模态显示**: 支持文本、图片、表格、Markdown

## 3. 技术栈

- **核心语言**: Python 3.9+
- **大模型交互**: OpenAI API / 兼容接口（通义千问、智谱 AI、DeepSeek、Moonshot）
- **数据处理**: Pandas, NumPy
- **数据接口**: AKShare
- **图表库**: mplfinance, matplotlib
- **Markdown 渲染**: Python `markdown` 库（支持 `nl2br`, `sane_lists` 扩展）
- **开发环境**: Jupyter Notebook

## 4. 架构设计

### 4.1 Core-Logic 分离
```
core/              ← 可复用的基础设施
├── llm_client.py     # 统一 LLM 接口
├── safe_parsing.py   # 防御性解析
├── ui_utils.py       # UI 工具（Markdown 渲染）
├── result_display.py # 结果显示封装
├── data_fetcher.py   # 数据获取
├── indicators.py     # 指标计算
└── visualization.py  # 图表生成（中文字体）

agent_logic.py     ← 业务逻辑（ReAct 循环）
```

### 4.2 模块职责
- **core**: 通用工具，无业务逻辑，可跨项目复用
- **agent_logic**: 金融分析特定逻辑，调用 core 工具

## 5. 已完成功能 ✅

- ✅ 封装 AKShare 数据获取工具
- ✅ 实现 MA、MACD、RSI、Bollinger Bands 计算
- ✅ 开发专业 K 线图绘制工具
- ✅ 集成 LLM 进行自然语言交互
- ✅ ReAct 模式 Agent 实现
- ✅ Markdown 自动渲染（使用标准库）
- ✅ 中文字体支持（跨平台）
- ✅ 嵌套列表智能规范化
- ✅ 交互式演示笔记本

## 6. 未来优化方向 🚀

- [ ] 添加更多技术指标（KDJ、OBV、ATR）
- [ ] 支持更多数据源（Tushare、东方财富）
- [ ] 实现回测功能
- [ ] 添加风险评估工具
- [ ] 多股票对比分析
- [ ] 实时行情监控
- [ ] Web 界面（Streamlit/Gradio）
