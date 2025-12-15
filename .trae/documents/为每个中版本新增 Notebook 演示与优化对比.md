## 目标

* 为每个次版本（Minor，如 v1.4.0、v1.5.0）提供可运行的 Jupyter Notebook 演示。

* 在 Notebook 中对比本次迭代相对上一稳定版本的优化效果（性能、准确性、可用性）。

* 实际调用项目功能进行端到端测试，输出图表与关键指标，并保留可复验产物。

## Notebook 清单与目录结构

* 新增目录：`notebooks/`

* 每次发布新增 2 个 Notebook：

  * `notebooks/vX.Y.Z_release_demo.ipynb`：端到端功能演示（Skills 混合模式、数据获取、指标计算、图表生成）。

  * `notebooks/vX.Y.Z_performance_compare.ipynb`：与上一稳定版本的关键指标对比（运行时长、Token 使用、渲染耗时）。

* 统一产出目录：`optimization/outputs/releases/vX.Y.Z/`（保存运行日志、图表、指标 JSON、对比报告片段）。

## 演示内容设计（release\_demo）

* 用例选择：

  * 股票：`600519` 最近 `days=60`（验证 v1.1.2 的相对日期修复）。

  * ETF：`510300` 最近 `days=90`（验证名称查询与标题生成）。

* 过程展示：

  * `run_agent()`：自然语言到工具编排的端到端流程（Skills 优先，失败回退）。

  * 技术指标：`add_all_indicators()` 核心指标计算结果预览（MACD、RSI、MA、BOLL）。

  * 可视化：`plot_comprehensive_chart()` 生成图表并保存至 `optimization/outputs/releases/vX.Y.Z/figures/`。

* 关键断言：

  * 数据量、时间范围与 `days` 映射正确。

  * 生成图表文件存在且尺寸合理（元数据/哈希对比）。

  * Skills 混合模式正常（记录路由与回退状态）。

## 对比内容设计（performance\_compare）

* 指标体系：

  * 端到端耗时：`run_agent()` 总时长（含数据获取与绘图）。

  * 可视化耗时：`plot_comprehensive_chart()` 渲染时间（参考 v1.2.0 优化）。

  * Token 使用量：Prompt 优化前后（参考 v1.3.0，如无实时 API，采用本地估算）。

* 基线数据来源：

  * 读取上一稳定版本记录的指标 JSON（位于 `optimization/outputs/`）。

  * 当前版本现场计算同指标，生成对比表与可视化（条形图/雷达图）。

## 数据与可重复性

* 优先在线数据（AKShare）；失败时回退到本地小型数据集（CSV，置于 `tests/data/`）。

* 固定随机种子与环境配置，使用 `matplotlib` 的 `Agg` 后端输出文件，确保跨平台一致性。

* 将 Notebook 输出的关键指标及图表都落盘，便于审阅与回归。

## 验证与自动化

* 本地验证：开发者运行两个 Notebook，检查输出目录中是否生成完整产物（日志、图表、指标 JSON）。

* 半自动化测试：

  * 引入 Notebook 运行器（如 `nbclient` / `papermill` / `pytest --nbval`）在本地或 CI 中执行。

  * 仅校验关键产物存在与指标范围，跳过 LLM 网络依赖；保留离线可运行能力。

## 与现有文档的对齐

* `README.md`：新增“版本演示与优化对比”章节，指向 `notebooks/` 与 `optimization/outputs/releases/`。

* `CHANGELOG.md`：每次次版本在“📚 文档”处说明新增 Notebook 与关键优化对比结论。

## 交付标准（每次次版本）

* 两个 Notebook 可一键运行；核心产物均在 `optimization/outputs/releases/vX.Y.Z/` 下生成。

* 至少一条股票与一条 ETF 用例完整通过（端到端）。

* 对比报告清晰呈现本次优化相对上一版本的提升或回归情况。

## 风险与缓解

* 网络与数据源不稳定：准备本地 CSV 回退路径；在 Notebook 中自动切换。

* LLM API 受限：引入 Token 估算与本地代理；在对比中标注近似值来源。

* 图表快照差异：采用元数据（尺寸、轴、线数）与图像哈希（阈值）双重校验，降低误报。

## 下一步实施（收到确认后）

* 创建 `notebooks/` 目录并为当前版本 `v1.4.0 `提供两份 Notebook 模板与示例用例。

* 补充 `optimization/outputs/releases/v1.4.0/` 的输出文件结构与收敛脚本。

* 在 `README.md` 与 `CHANGELOG.md` 对齐说明；可选增加最小 CI 步骤运行 Notebook（离线模式）。

