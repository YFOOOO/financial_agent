## 审核结论

* 目录存在两个输出位置：

  * `notebooks/optimization/outputs/releases/v1.4.0/metrics.json`（包含 baseline 与 current，viz≈0.341s）

  * `optimization/outputs/releases/v1.4.0/metrics.json`（仅 current，viz≈0.333s）

* 结果显示：相对公告的 v1.3.0 基线（viz≈0.241s），当前 v1.4.0 的单次测量在 0.333–0.341s 区间，存在环境与测量差异；需统一输出路径与采样策略（多次测量取中位数）以提升可比性。

## 修复与改进项

* 统一输出路径：Notebook 与脚本将输出到项目根的 `optimization/outputs/releases/vX.Y.Z/`，避免相对路径导致的 `notebooks/optimization/...` 影子目录。

* 稳定测量：

  * 引入多次采样（如 N=5），输出均值/中位数/方差；固定 `matplotlib` 后端、`figsize`、字体配置。

  * 统一数据集：在线 AKShare 优先，失败回退本地 CSV 固定夹具，确保跨设备一致性。

* 指标口径：

  * 可视化耗时：`plot_comprehensive_chart` 測量段固定。

  * Agent 耗时（离线）：以可视化耗时代替或单独记录工具链时间；Token 指标保留估算说明。

## 最小 CI（离线模式）

* 依赖：`nbclient`, `pytest`, `pytest-nbval`, `matplotlib`, `pandas`。

* 执行：

  * 以 `pytest --nbval` 执行 `notebooks/vX.Y.Z_*.ipynb`；在 Notebook 中写入产物到 `optimization/outputs/releases/vX.Y.Z/`。

  * 断言：产物存在（`figures/*.png`、`metrics.json`），指标范围合理（耗时>0，图像尺寸一致）。

* 跳过网络：默认为离线；如需在线测试，要求设置 `ENABLE_ONLINE_TESTS=1` 环境变量。

## 在线测试补充（可选）

* 标记：`pytest -m online` 执行，包含：

  * AKShare 数据接口连通性与基本结构校验（`core/data_fetcher.py`）。

  * LLM 客户端连通性（在 `.env` 配置存在时运行，超时与速率受控）。

  * 基准模型：qwen3-max

* 保护：无环境变量或密钥时自动跳过；记录跳过原因。

## 模板复制与注释

* 新增两类模板：`notebooks/template_release_demo.ipynb`、`notebooks/template_performance_compare.ipynb`。

* 模板特性：

  * 版本参数 `VERSION` 与统一输出根 `PROJECT_ROOT` 初始化单元。

  * 关键单元格补充注释（用途、输入输出、失败回退策略、断言内容）。

* 可选生成脚本：`scripts/generate_version_notebooks.py`，输入版本号生成当次版本 Notebook。

## 提交与同步

* 本地 `main` 领先远端 14 提交（此前审计结果）；建议：

  * 打 `v1.4.1` 标签，包含 Notebook 与文档修正。

  * 同步到远端：`git push origin main --tags`；在 Releases 发布说明中附带指标与产物位置。

  * 提交更改前请求人工审核

* 后续：在 PR/CI 中启用离线 Notebook 执行；在线测试按需开启。

## 实施步骤（确认后执行）

1. 统一 Notebook 输出路径与采样逻辑（更新两个 v1.4.0 Notebook）。
2. 增加 CI 配置与依赖，接入 `pytest --nbval` 离线执行与断言。
3. 添加在线测试用例与跳过机制（`pytest -m online`）。
4. 提交更改，打 `v1.4.1` 标签并推送远端；发布说明指向产物目录与对比结果。

