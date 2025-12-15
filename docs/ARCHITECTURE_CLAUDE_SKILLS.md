# 🧩 Claude Skills 架构 - 金融数据分析助手适配方案

> 基于 Anthropic 官方 Skills 规范的实现指南  
> 参考: [Claude Skills Repository](https://github.com/Claude-Skills-Org/skills-main)

---

## 1. 核心概念 (Core Concepts)

### 1.1 什么是 Skill？

**Skill (技能)** 是一个文件夹，包含指令、脚本和资源，使 Claude 能够动态加载并在特定任务上表现更好。每个 Skill 通过 `SKILL.md` 文件定义，该文件包含：

- **YAML Frontmatter**: 元数据（name, description）
- **Markdown Body**: 使用说明、工作流程、最佳实践
- **Bundled Resources** (可选):
  - `scripts/` - 可执行代码（Python/Bash 等）
  - `references/` - 参考文档（加载到上下文中）
  - `assets/` - 输出资源（模板、图像、字体等）

### 1.2 Skill 的三层加载机制

Claude Skills 使用**渐进式披露 (Progressive Disclosure)** 设计：

1. **元数据层** (name + description) - 始终在上下文中 (~100 词)
2. **SKILL.md 主体** - 技能触发时加载 (<5k 词)
3. **捆绑资源** - 按需由 Claude 加载（脚本可不读取直接执行）

### 1.3 关键设计原则

- **简洁为王**: 保持 SKILL.md 精简，复杂内容拆分到 references/
- **适度自由度**: 根据任务脆弱性调整指令具体程度
- **可重用性**: 脚本、模板应在不同场景下可复用
- **向后兼容**: 保持现有 API 稳定，Skill 作为底层增强

---

## 2. 官方 Skill 规范 (Agent Skills Spec v1.0)

### 2.1 标准文件结构

```
skill-name/                    # 技能目录（hyphen-case）
├── SKILL.md                   # 必需：技能入口
│   ├── YAML Frontmatter       # 必需：元数据
│   │   ├── name: skill-name   # 必需：与目录名完全一致
│   │   ├── description: ...   # 必需：触发描述（关键！）
│   │   ├── license: ...       # 可选：许可证
│   │   ├── allowed-tools: []  # 可选：预批准工具列表
│   │   └── metadata: {}       # 可选：自定义键值对
│   └── Markdown Body          # 必需：使用说明
├── scripts/                   # 可选：可执行代码
│   ├── fetch_data.py          # 示例：数据获取脚本
│   └── calculate_ma.py        # 示例：指标计算脚本
├── references/                # 可选：参考文档
│   ├── api_docs.md            # 示例：API 文档
│   └── indicators.md          # 示例：指标说明
└── assets/                    # 可选：输出资源
    ├── chart_template.html    # 示例：图表模板
    └── logo.png               # 示例：品牌资源
```

### 2.2 SKILL.md 编写要点

#### Frontmatter 规范
- **name**: 小写字母 + 连字符，与目录名完全一致
- **description**: **最关键字段** - 这是触发机制！
  - 必须包含"做什么"和"何时使用"
  - 示例: `"获取A股和ETF数据，计算技术指标，生成K线图表。适用于：(1) 股票数据查询，(2) 技术分析需求，(3) 图表生成任务"`

#### Body 编写原则
- 使用**祈使语气**（Do this, not "You should do this"）
- 保持 < 500 行（超出则拆分到 references/）
- 包含具体示例和决策树（如适用）
- 引用 scripts/references 时清晰说明何时使用

---

## 3. 金融分析助手的 Skills 实现方案

### 3.1 渐进式重构策略（推荐）

**Phase 1: 保持兼容的包装层**
```
项目结构（v1.4.0）：
├── core/                      # 保留：现有核心模块
│   ├── data_fetcher.py        # 保留不变
│   ├── indicators.py          # 保留不变
│   └── visualization.py       # 保留不变
├── skills/                    # 新增：Skill 包装层
│   ├── __init__.py            # Skill 注册和加载
│   ├── financial-data-fetch/  # Skill #1
│   ├── technical-indicators/  # Skill #2
│   └── chart-generation/      # Skill #3
└── agent_logic.py             # 更新：使用 SkillOrchestrator
```

**优势**:
- ✅ 向后兼容 - 现有代码继续工作
- ✅ 渐进迁移 - 逐个 Skill 测试和优化
- ✅ 低风险 - 出问题可快速回滚
- ✅ 学习曲线 - 团队逐步适应新架构

### 3.2 三个核心 Skill 设计

#### Skill #1: Financial Data Fetch

**目标**: 统一的股票和 ETF 数据获取

```markdown
skills/financial-data-fetch/
├── SKILL.md
│   name: financial-data-fetch
│   description: 获取中国A股和ETF市场数据。使用场景：(1) 查询股票历史数据
│                (2) 获取ETF净值走势 (3) 指定时间范围的数据提取
├── scripts/
│   ├── fetch_stock.py         # 复用 core/data_fetcher.py 逻辑
│   └── fetch_etf.py            # 复用 core/data_fetcher.py 逻辑
└── references/
    ├── akshare_api.md          # AKShare API 文档摘要
    └── data_schema.md          # 返回数据格式说明
```

**SKILL.md 结构**:
```markdown
# Financial Data Fetch

## Overview
统一的金融数据获取接口，支持 A股 和 ETF。

## Quick Start
1. 确定数据类型（股票 or ETF）
2. 提取股票代码和时间范围
3. 调用对应脚本
4. 返回标准化 DataFrame

## Data Types
### Stock Data (A股)
- Script: `scripts/fetch_stock.py`
- Parameters: symbol (6位代码), days (天数)
- Returns: OHLCV + 复权数据

### ETF Data
- Script: `scripts/fetch_etf.py`  
- Parameters: symbol (6位代码), days (天数)
- Returns: 净值 + 成交量

## Error Handling
- 代码不存在 → 返回明确错误信息
- 网络超时 → 重试 3 次
- 数据为空 → 提示用户调整参数

## References
详细 API 文档见 [references/akshare_api.md](references/akshare_api.md)
```

#### Skill #2: Technical Indicators

**目标**: 计算常用技术指标

```markdown
skills/technical-indicators/
├── SKILL.md
│   name: technical-indicators
│   description: 计算股票技术指标（MA, MACD, RSI, BOLL等）。适用于技术分析、
│                量化回测、趋势判断等场景
├── scripts/
│   ├── calculate_ma.py         # 移动平均线
│   ├── calculate_macd.py       # MACD 指标
│   └── calculate_all.py        # 批量计算
└── references/
    ├── indicators_formula.md   # 指标公式详解
    └── interpretation.md       # 指标解读指南
```

#### Skill #3: Chart Generation

**目标**: 生成专业金融图表

```markdown
skills/chart-generation/
├── SKILL.md
│   name: chart-generation
│   description: 生成K线图、技术指标图表。支持多种图表类型（basic, comprehensive）
│                和自定义样式
├── scripts/
│   ├── plot_candlestick.py    # K线图生成
│   └── plot_indicators.py     # 指标叠加图
├── assets/
│   └── chart_styles/           # 预定义样式
│       ├── dark_theme.json
│       └── light_theme.json
└── references/
    └── mplfinance_guide.md     # mplfinance 使用指南
```

### 3.3 Skill Orchestrator (编排器)

创建 `skills/orchestrator.py` 统一管理 Skills：

```python
"""
Skill Orchestrator - 技能编排器

负责加载、注册和调度 Skills
"""

class SkillOrchestrator:
    def __init__(self):
        self.skills = {}
        self.load_skills()
    
    def load_skills(self):
        """加载所有 Skills"""
        self.skills['data'] = DataFetchSkill()
        self.skills['indicators'] = TechnicalIndicatorsSkill()
        self.skills['chart'] = ChartGenerationSkill()
    
    def get_skill(self, skill_name: str):
        """获取指定 Skill"""
        return self.skills.get(skill_name)
    
    def execute_workflow(self, user_query: str):
        """
        根据用户查询，编排 Skills 执行工作流
        
        典型流程：
        1. Data Fetch Skill → 获取数据
        2. Technical Indicators Skill → 计算指标
        3. Chart Generation Skill → 生成图表
        """
        pass
```

### 3.4 与现有代码集成

**agent_logic.py 更新**:
```python
from skills.orchestrator import SkillOrchestrator

# 初始化 Skill 编排器
orchestrator = SkillOrchestrator()

# 在 run_agent() 中使用
def run_agent(query, model="gpt-4o-mini", verbose=False):
    # ... 现有逻辑保持不变 ...
    
    # 工具定义现在由 Skills 提供
    tools = orchestrator.get_all_tool_definitions()
    
    # 工具执行由 Orchestrator 分发
    result = orchestrator.execute_tool(tool_name, tool_input)
    
    return result
```

---

## 4. 实施路线图

### Phase 1: 基础设施搭建 (1-2天)

**目标**: 建立 Skill 加载和编排机制

**任务**:
- [ ] 创建 `skills/` 目录结构
- [ ] 实现 `SkillOrchestrator` 基类
- [ ] 实现 `BaseSkill` 抽象类
- [ ] 编写 Skill 加载器

**输出**:
```python
# skills/__init__.py
# skills/base_skill.py
# skills/orchestrator.py
```

### Phase 2: 第一个 Skill (0.5天)

**目标**: 完成 Financial Data Fetch Skill

**任务**:
- [ ] 创建 `skills/financial-data-fetch/`
- [ ] 编写 `SKILL.md`（符合官方规范）
- [ ] 复用 `core/data_fetcher.py` 为 scripts
- [ ] 编写 `references/akshare_api.md`
- [ ] 集成到 `agent_logic.py`
- [ ] 端到端测试

### Phase 3: 第二和第三个 Skill (1天)

**目标**: 完成 Technical Indicators 和 Chart Generation Skills

**任务**:
- [ ] 创建剩余两个 Skill 目录
- [ ] 编写各自的 `SKILL.md`
- [ ] 复用现有 core 模块为 scripts
- [ ] 编写 references 文档
- [ ] 全流程集成测试

### Phase 4: 优化与文档 (0.5天)

**目标**: 性能优化和文档完善

**任务**:
- [ ] 性能基准测试
- [ ] 更新 `docs/ARCHITECTURE.md`
- [ ] 编写 Skills 使用示例
- [ ] 更新 README.md

---

## 5. 成功标准

### 功能标准
- ✅ 所有现有功能正常工作
- ✅ Skills 可被 Claude 正确识别和触发
- ✅ Skill 间可协同工作（数据 → 指标 → 图表）
- ✅ 向后兼容（`agent_logic.py` API 不变）

### 性能标准
- ✅ 端到端性能不低于 v1.3.0
- ✅ Skill 加载时间 < 100ms
- ✅ 内存使用增长 < 10%

### 代码质量标准
- ✅ 所有 SKILL.md 符合官方规范
- ✅ Scripts 有完整的错误处理
- ✅ References 文档清晰完整
- ✅ 通过所有现有测试

---

## 6. 技术细节

### 6.1 BaseSkill 抽象类

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseSkill(ABC):
    """Skill 基类"""
    
    def __init__(self, skill_dir: str):
        self.skill_dir = skill_dir
        self.metadata = self.load_metadata()
        self.instructions = self.load_instructions()
    
    @abstractmethod
    def get_tool_definitions(self) -> List[Dict]:
        """返回该 Skill 提供的工具定义"""
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """执行工具调用"""
        pass
    
    def load_metadata(self) -> Dict:
        """从 SKILL.md 加载 YAML frontmatter"""
        pass
    
    def load_instructions(self) -> str:
        """加载 SKILL.md markdown body"""
        pass
```

### 6.2 Skill 发现和加载

```python
import os
from pathlib import Path

def discover_skills(skills_dir: str) -> List[str]:
    """发现所有 Skill 目录"""
    skills = []
    for item in Path(skills_dir).iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append(item.name)
    return skills

def load_skill(skill_path: str) -> BaseSkill:
    """加载单个 Skill"""
    # 根据 skill_path 动态导入对应的 Skill 类
    pass
```

---

## 7. 与官方 Skills 的差异

### 7.1 我们保留的特性
- ✅ `core/` 模块作为底层实现（不暴露给 Claude）
- ✅ ReAct Agent 主循环
- ✅ 现有工具调用机制

### 7.2 我们采纳的特性
- ✅ `SKILL.md` 标准格式
- ✅ `scripts/`, `references/`, `assets/` 结构
- ✅ 渐进式披露设计
- ✅ YAML frontmatter 作为触发机制

### 7.3 暂不实现的特性
- ❌ `.skill` 打包格式（暂无分发需求）
- ❌ 动态安装/卸载（项目内置 Skills）
- ❌ Skill Marketplace 集成

---

## 8. 参考资源

- [Anthropic Skills Repository](https://github.com/Claude-Skills-Org/skills-main)
- [Agent Skills Spec v1.0](https://github.com/Claude-Skills-Org/skills-main/blob/main/agent_skills_spec.md)
- [Skill Creator Guide](https://github.com/Claude-Skills-Org/skills-main/tree/main/skill-creator)
- [Claude Skills 官方文档](https://support.claude.com/en/articles/12512176-what-are-skills)

---

**最后更新**: 2025-12-15  
**适用版本**: v1.4.0  
**维护者**: YFOOOO
