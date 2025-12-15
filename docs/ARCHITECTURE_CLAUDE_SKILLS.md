# 🧩 Claude Modular Skills & Financial Analyst Architecture

> 基于 Claude Quickstarts (Financial Data Analyst) 的模块化技能架构参考

## 1. 核心概念 (Core Concepts)

Claude 的 "Skills" (技能) 架构强调将 Agent 的能力封装为独立、可复用的模块。在金融分析场景中，这意味着将数据获取、指标计算、图表绘制等功能解耦，并通过高质量的 Prompt 和 Tool Definitions 提供给 LLM。

### 1.1 关键组件

- **Skills (技能模块)**: 
  - 独立的 Python 函数或类，封装特定领域的逻辑。
  - 例如：`StockDataSkill`, `TechnicalAnalysisSkill`, `ChartingSkill`。
  - 每个 Skill 包含：
    - **Implementation**: 实际的 Python 代码。
    - **Tool Definition**: 符合 OpenAI/Anthropic 标准的 JSON Schema 描述。
    - **System Prompt**: 指导 LLM 如何使用该技能的微调指令。

- **Client-side Tools (客户端工具)**:
  - Agent 不直接在服务器运行所有代码，而是通过调用定义好的工具，由客户端（或沙箱环境）执行并返回结果。
  - 这种模式特别适合需要生成交互式 UI (Artifacts) 的场景。

- **Artifacts (交互式产物)**:
  - Claude 特有的 UI 呈现方式。在金融分析中，生成的不仅仅是静态图片，而是可以是交互式的 React 组件或 HTML/JS 图表（如使用 Recharts 或 Plotly）。

## 2. 架构图示 (Architecture Diagram)

```mermaid
graph LR
    User[用户] -->|自然语言查询| Agent[Claude Agent]
    
    subgraph Skills [技能库 (Modular Skills)]
        direction TB
        DataSkill[数据技能]
        CalcSkill[计算技能]
        VizSkill[可视化技能]
    end
    
    Agent -->|Tool Call| DataSkill
    Agent -->|Tool Call| CalcSkill
    Agent -->|Tool Call| VizSkill
    
    DataSkill -->|JSON Data| Agent
    CalcSkill -->|Indicators| Agent
    VizSkill -->|Chart Config| Agent
    
    Agent -->|生成 Artifact| UI[交互式前端]
    UI -->|渲染图表| User
```

## 3. 在金融分析助手中的应用

### 3.1 技能模块化 (Modularization)

建议将现有的 `core/` 目录进一步重构为基于技能的结构：

```
skills/
├── market_data/           # 数据技能
│   ├── __init__.py
│   ├── tools.py          # 工具定义 (JSON Schema)
│   └── implementation.py # 实际逻辑 (AKShare 调用)
├── technical_analysis/    # 分析技能
│   ├── __init__.py
│   ├── tools.py
│   └── implementation.py # Pandas/TA-Lib 计算
└── visualization/         # 可视化技能
    ├── __init__.py
    ├── tools.py
    └── implementation.py # 生成 Plotly 配置或 React 组件代码
```

### 3.2 交互式可视化 (Interactive Visualization)

参考 Claude Financial Analyst Demo，Agent 不应只返回静态图片路径，而应返回**图表配置数据**。

- **当前模式**: Python 生成 `.png` -> 保存磁盘 -> 返回路径。
- **优化模式 (Claude Style)**: Agent 生成 JSON 配置 -> 前端解析 -> 渲染交互式图表。

**示例响应**:
```json
{
  "type": "chart",
  "data": {
    "symbol": "600519",
    "dates": ["2023-01-01", ...],
    "prices": [1800.5, ...],
    "indicators": {
      "ma5": [...]
    }
  },
  "viz_type": "candlestick_with_ma"
}
```

## 4. 优势与权衡

### 优势
1.  **高内聚低耦合**: 每个 Skill 独立开发测试，易于维护。
2.  **复用性**: 相同的 Skill 可以被不同的 Agent (如 LangGraph 中的不同 Worker) 复用。
3.  **用户体验**: 支持生成更现代、交互性更强的 UI。

### 权衡
1.  **前端依赖**: 需要更强的前端配合来渲染 Artifacts (如果只在 Notebook 中运行，可以使用 `ipywidgets` 或 `plotly`)。
2.  **上下文管理**: 需要精心设计 System Prompt，确保 LLM 知道有哪些 Skill 可用。

## 5. 总结

Claude 的 Skills 模式侧重于**能力的封装与表达**。它是构建高质量 Agent 的基石。无论是否使用多 Agent 架构，首先将单体 Agent 的能力模块化为高质量的 Skills 都是必经之路。
