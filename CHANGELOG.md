# 📝 更新日志 (CHANGELOG)

本文件记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.1.1] - 2025-12-14

### 🆕 新增

#### 优化与评估框架
- **性能评估工具** (`optimization/benchmarks/comparison_report.ipynb`)
  - 多版本性能数据自动加载与对比
  - 4 类可视化图表（性能对比、质量评分、成本分析、提升百分比）
  - Markdown 格式报告导出
  
- **实验记录系统** (`optimization/experiments/experiment_log.md`)
  - 3 个预定义实验计划（可视化优化、LLM 优化、数据获取优化）
  - 标准化实验记录模板（目标、方案、数据、结论）
  - 实验索引表与最佳实践指南

- **迭代工作流程** (`optimization/ITERATION_GUIDE.md`)
  - 5 阶段完整工作流（准备 → 实验 → 评估 → 提交 → 发布）
  - 质量标准定义（性能、可维护性、用户体验）
  - 提交信息规范与语义化版本管理
  - 快速参考命令表

#### Git 自动化工具
- **Pre-commit Hook** (`.git-hooks/pre-commit`)
  - 7 项自动质量检查：
    1. 代码格式化（Black）
    2. 类型检查（MyPy）
    3. Python 语法检查
    4. 模块导入验证
    5. 单元测试（可选）
    6. 性能回归检测（可选）
    7. 文档同步检查
  - 自动格式化并重新暂存
  - 仅警告不阻止提交（灵活策略）

#### 架构文档
- **架构设计文档** (`docs/ARCHITECTURE.md`)
  - 函数式架构设计说明
  - 所有公共 API 的完整列表（13 个函数）
  - 内部函数命名规范（`_` 前缀）
  - 导入最佳实践与反模式
  - 模块结构与职责划分
  - 测试架构规划

#### 实验验证
- **可视化优化实验** (`optimization/optimize_visualization.ipynb`)
  - ✅ 性能提升：31.2%（超过目标 30%）
  - ✅ 样式预配置与缓存机制
  - ✅ 动态面板检测（适配有/无 MACD）
  - ✅ 中文字体自动检测（macOS/Windows/Linux）
  - ✅ 完整质量检查清单

### 🔧 优化

#### 模块导入系统
- 修复 `core/__init__.py` 导出缺失问题
- 新增 13 个函数的统一导出接口：
  - 数据获取：`fetch_stock_daily`, `fetch_etf_daily`, `fetch_data`, `get_trading_days`
  - 技术指标：`add_all_indicators`, `calculate_ma`, `calculate_macd`, `calculate_rsi`, `calculate_bollinger_bands`
  - 可视化：`plot_kline_basic`, `plot_kline_with_ma`, `plot_kline_with_macd`, `plot_comprehensive_chart`, `plot_auto`

#### 数据文件管理
- 创建 `optimization/outputs/` 目录存放实验产出
- 更新 `.gitignore` 排除临时文件但保留演示图表
- 添加 `outputs/README.md` 规范文件管理策略

### 📚 文档

#### 更新
- `README.md` - 添加优化框架章节、更新项目结构
- `optimization/README.md` - 框架核心原则与使用指南
- `.git-hooks/README.md` - Git Hook 安装与使用说明

#### 新增
- `CHANGELOG.md` - 本文件，记录所有版本变更
- `docs/ARCHITECTURE.md` - 完整架构设计文档
- `optimization/outputs/README.md` - 实验产出管理规范

### 🐛 修复

- **Git Hook 路径错误** - 修复 `pre-commit` 脚本中的路径拼接问题
- **交互式阻塞** - 移除文档检查的交互式确认，改为仅警告
- **Panel Ratios 错误** - 实现动态面板比例计算，适配不同指标组合
- **导入错误** - 修复 Notebook 中尝试导入不存在的类的问题

### 🔬 实验记录

#### 实验 #000: 可视化性能优化
- **目标**: 图表生成速度提升 30%
- **方案**: 样式预配置与缓存、减少对象创建
- **结果**: ✅ 性能提升 31.2%（0.241s → 0.166s）
- **结论**: 合并到核心代码（v1.2.0 规划）
- **详情**: `optimization/experiments/experiment_log.md` #000

---

## [1.1.0] - 2025-12-13

### 🎉 初始发布

#### 核心功能
- **数据获取模块** (`core/data_fetcher.py`)
  - 支持 A 股和 ETF 日线数据获取
  - 基于 AKShare 数据源
  - 自动处理日期格式

- **技术指标计算** (`core/indicators.py`)
  - MA（5/10/20/60 日均线）
  - MACD（快线、慢线、柱状图）
  - RSI（14 日相对强弱指标）
  - 布林带（上轨、中轨、下轨）

- **可视化系统** (`core/visualization.py`)
  - 基于 mplfinance 的 K 线图
  - 中文字体自动配置
  - 多面板布局（K线 + 指标 + 成交量）
  - 红涨绿跌配色方案

- **LLM 客户端** (`core/llm_client.py`)
  - 支持多家 LLM 提供商（OpenAI、阿里云、智谱AI、DeepSeek、Moonshot）
  - 统一的调用接口
  - 对话历史管理

- **Agent 逻辑** (`agent_logic.py`)
  - ReAct 模式实现
  - 工具调用管理
  - 结果展示与格式化

#### UI 优化
- **Markdown 渲染** (`core/ui_utils.py`)
  - 自动识别并渲染 Markdown 内容
  - 支持标题、列表、代码块、引用
  - 智能缩进规范化（2/3 空格 → 4 空格）
  - 精美卡片样式（渐变边框）

- **中文字体支持**
  - macOS: STHeiti / PingFang SC
  - Windows: Microsoft YaHei
  - Linux: WenQuanYi Zen Hei

#### 文档
- `README.md` - 项目介绍与快速开始
- `docs.md` - 技术文档
- `spec.md` - 功能规格说明
- `requirements.txt` - 依赖清单
- `.env.example` - 环境变量模板

#### Bug 修复
- 修复 Markdown 嵌套列表渲染问题
- 修复 mplfinance 中文字体配置传递问题
- 修复日期范围计算错误

---

## [Unreleased]

### 🚀 规划中

#### v1.2.0 - 视觉优化迭代
- [ ] 图表标签字体加粗
- [ ] 坐标轴标签旋转优化
- [ ] 网格线透明度调整
- [ ] MA 线条颜色区分度优化
- [ ] 图例位置和样式优化

#### v1.3.0 - LLM 优化迭代
- [ ] Token 使用量减少 20%
- [ ] Few-shot 提示词优化
- [ ] 响应时间优化（缓存策略）
- [ ] 上下文压缩

#### v1.4.0 - 数据获取优化
- [ ] Redis 缓存支持
- [ ] 并行数据获取
- [ ] 增量更新机制
- [ ] 缓存命中率 > 80%

#### 长期规划
- [ ] 单元测试覆盖率 > 80%
- [ ] CI/CD 自动化流水线
- [ ] 性能监控面板
- [ ] 多时间粒度支持（分钟、小时、周、月）
- [ ] 更多技术指标（KDJ、CCI、威廉指标等）
- [ ] 自定义策略回测框架

---

## 版本说明

- **主版本号（Major）**: 不兼容的 API 变更
- **次版本号（Minor）**: 向下兼容的功能新增
- **修订号（Patch）**: 向下兼容的问题修复

**当前稳定版本**: v1.1.1  
**开发分支**: main  
**发布标签**: [GitHub Releases](https://github.com/YFOOOO/financial_agent/releases)

---

## 🤝 贡献

感谢所有贡献者！特别感谢：
- **Claude AI** - 架构设计与代码实现协助
- **YuFan** - 项目维护与迭代规划

---

**Last Updated**: 2025-12-14 18:58 CST
