# 🚀 开发迭代指南

> 金融数据分析助手 - 快速迭代工作流

## 🎯 核心原则

- **质量优先**: 准确性和用户体验是第一位
- **快速迭代**: 完成优化即发布，保持敏捷
- **数据驱动**: 每次优化都有基准对比
- **实验记录**: 所有尝试都值得记录

---

## 📋 标准迭代流程

### 阶段 1: 准备阶段 🔧

```bash
# 1. 确保在最新的主分支
git checkout main
git pull origin main

# 2. 创建开发分支
git checkout -b dev/optimization

# 3. 运行基准测试（建立性能基线）
jupyter notebook optimization/eval_framework.ipynb
# 运行所有 cell，保存结果到 benchmarks/v1.1.0_baseline.json
```

**输出**: `optimization/benchmarks/v1.1.0_baseline.json`

---

### 阶段 2: 实验阶段 🧪

```bash
# 1. 选择优化方向（4选1）
# - optimization/optimize_llm_prompts.ipynb      # Prompt 优化
# - optimization/optimize_data_fetching.ipynb    # 数据获取优化
# - optimization/optimize_indicators.ipynb       # 指标计算优化
# - optimization/optimize_visualization.ipynb    # 可视化优化

# 2. 在 Notebook 中进行实验
jupyter notebook optimization/optimize_llm_prompts.ipynb

# 3. 记录实验过程
# 编辑 optimization/experiments/experiment_log.md
# 使用提供的模板记录实验详情
```

**输出**: 
- 优化后的代码
- 实验记录（experiment_log.md）

---

### 阶段 3: 评估阶段 📊

```bash
# 1. 将优化代码复制到核心模块
# 例如: 优化后的 Prompt 更新到 agent_logic.py

# 2. 重新运行评估框架
jupyter notebook optimization/eval_framework.ipynb
# 运行所有 cell，保存结果到 benchmarks/v1.2.0_alpha_1.json

# 3. 运行对比分析
jupyter notebook optimization/benchmarks/comparison_report.ipynb
# 生成对比图表和报告
```

**输出**:
- `optimization/benchmarks/v1.2.0_alpha_1.json`
- `optimization/benchmarks/performance_comparison.png`
- `optimization/benchmarks/quality_comparison.png`
- `optimization/benchmarks/cost_comparison.png`
- `optimization/benchmarks/optimization_report.md`

**决策标准**:
- ✅ 性能提升或持平
- ✅ 质量不下降
- ✅ 成本降低或持平
- ✅ 无破坏性变更

---

### 阶段 4: 提交阶段 💾

```bash
# 1. 查看修改
git status
git diff

# 2. 添加修改文件
git add core/llm_client.py agent_logic.py
git add optimization/benchmarks/v1.2.0_alpha_1.json
git add optimization/experiments/experiment_log.md

# 3. 提交（自动触发 pre-commit hook）
git commit -m "⚡ 优化: 减少 LLM Token 使用 30%

- 精简 Prompt 描述
- 优化工具说明格式
- 移除冗余 Few-shot 示例

性能提升:
- Token 使用: -28%
- 响应时间: -20%
- 成本: -28.6%

质量保持:
- 格式正确率: 95% (持平)
- 内容完整率: 90% (+2%)

参考: optimization/experiments/experiment_log.md #001"

# Hook 会自动运行:
# - 代码格式检查
# - 语法检查
# - 导入检查
# - 单元测试（如果有）
```

---

### 阶段 5: 发布阶段 🚀

```bash
# 1. 合并到主分支
git checkout main
git merge dev/optimization

# 2. 更新版本号和文档
# 编辑 README.md, docs.md, spec.md
# 更新版本号为 v1.2.0

# 3. 提交文档更新
git add README.md docs.md spec.md
git commit -m "📝 文档: 更新到 v1.2.0"

# 4. 打版本标签
git tag -a v1.2.0 -m "v1.2.0: Prompt 优化

主要改进:
- Token 使用减少 28%
- 响应时间减少 20%
- 成本降低 28.6%

完整变更: optimization/benchmarks/optimization_report.md"

# 5. 推送到远程
git push origin main
git push origin v1.2.0

# 6. 清理开发分支
git branch -d dev/optimization
```

---

## 🔄 并行实验模式

如果需要同时尝试多个优化方案：

```bash
# 实验 1: Prompt 优化
git checkout -b exp/prompt-optimization
# ... 实验代码 ...
git commit -m "🧪 实验: Prompt 精简"

# 实验 2: 缓存机制
git checkout main
git checkout -b exp/caching
# ... 实验代码 ...
git commit -m "🧪 实验: 数据缓存"

# 对比结果后，选择最优方案合并
git checkout main
git merge exp/prompt-optimization  # 如果这个效果更好
```

---

## 📊 质量门禁

每次提交必须通过以下检查：

### 自动检查（pre-commit hook）
- [x] 代码格式（Black）
- [x] 类型检查（MyPy）
- [x] 语法检查
- [x] 模块导入
- [x] 单元测试（如果有）

### 手动检查
- [ ] 功能完整性（不破坏现有功能）
- [ ] 性能提升或持平（对比基准数据）
- [ ] 代码可读性（保持良好风格）
- [ ] 文档同步更新（README、docs、spec）

---

## 🎨 Commit Message 规范

使用 emoji + 类型 + 描述：

```
⚡ 优化: 减少 LLM Token 使用 30%
🐛 修复: 数据获取超时问题
📝 文档: 更新 README 安装说明
✨ 功能: 添加数据缓存机制
🔧 配置: 更新 requirements.txt
🎨 格式: Black 代码格式化
♻️  重构: 优化 Agent 逻辑结构
🔥 清理: 移除过时的测试代码
✅ 测试: 添加指标计算单元测试
🚀 部署: 推送 v1.2.0 到生产环境
🧪 实验: 尝试向量化计算
```

---

## 📈 版本发布规则

### 语义化版本 (Semantic Versioning)

```
v1.2.3
│ │ │
│ │ └─ 补丁版本（Bug 修复、文档更新）
│ └─── 次版本（新功能、优化改进）
└───── 主版本（破坏性变更、重大重构）
```

### 发布频率

- **补丁版本 (v1.2.x)**: 随时发布（Bug 修复）
- **次版本 (v1.x.0)**: 完成优化即发布（1-3天）
- **主版本 (vx.0.0)**: 重大里程碑（1-2个月）

---

## 🛠️ 常用命令速查

```bash
# 查看当前分支
git branch

# 查看未提交的修改
git status
git diff

# 撤销工作区修改
git checkout -- <file>

# 撤销暂存区修改
git reset HEAD <file>

# 查看提交历史
git log --oneline --graph --decorate

# 查看标签
git tag -l

# 删除本地分支
git branch -d <branch>

# 查看 Git Hook 配置
git config core.hooksPath

# 临时跳过 Hook（不推荐）
git commit --no-verify -m "message"
```

---

## 📚 文件清单

### 核心文件
- `agent_logic.py` - Agent 主逻辑
- `core/*.py` - 核心模块（8个）

### 评估文件
- `optimization/eval_framework.ipynb` - 评估框架
- `optimization/benchmarks/*.json` - 基准数据
- `optimization/benchmarks/comparison_report.ipynb` - 对比分析

### 优化文件
- `optimization/optimize_llm_prompts.ipynb` - Prompt 优化
- `optimization/optimize_data_fetching.ipynb` - 数据优化
- `optimization/optimize_indicators.ipynb` - 指标优化
- `optimization/optimize_visualization.ipynb` - 可视化优化

### 实验文件
- `optimization/experiments/experiment_log.md` - 实验日志

### 文档文件
- `README.md` - 项目介绍
- `docs.md` - 详细文档
- `spec.md` - 技术规格
- `optimization/README.md` - 优化框架说明
- `optimization/ITERATION_GUIDE.md` - 本文件

---

## 🔍 故障排除

### Q: Hook 没有执行？
```bash
# 检查配置
git config core.hooksPath
# 应该输出: .git-hooks

# 重新配置
git config core.hooksPath .git-hooks
```

### Q: Hook 检查失败？
```bash
# 查看详细错误
git commit -m "test"

# 临时跳过（仅用于紧急情况）
git commit --no-verify -m "紧急修复"
```

### Q: 基准数据丢失？
```bash
# 重新运行评估框架
jupyter notebook optimization/eval_framework.ipynb
# 运行所有 cell，保存基准数据
```

### Q: 如何回滚代码？
```bash
# 回滚到上一个提交
git reset --hard HEAD^

# 回滚到指定版本
git reset --hard v1.1.0

# 回滚单个文件
git checkout v1.1.0 -- core/llm_client.py
```

---

## 🎯 快速开始检查清单

第一次使用时，请确认：

- [ ] 已安装依赖: `pip install -r requirements.txt`
- [ ] 已配置环境变量: `.env` 文件
- [ ] 已安装 Git Hook: `git config core.hooksPath .git-hooks`
- [ ] 已建立基准数据: 运行 `eval_framework.ipynb`
- [ ] 已阅读文档: `README.md`, `optimization/README.md`

---

## 📌 当前迭代状态

### v1.4.0 - Skill 模式重构 (进行中)

**开始日期**: 2025-12-15  
**预计完成**: 2025-12-16  
**详细计划**: `optimization/v1.4.0_PLAN.md`

**核心目标**:
1. ✨ Skill 模式架构重构（模块化、可扩展）
2. 🔧 技术债务清理（评估框架、基准数据、文档对齐）
3. ⚡ 性能和可维护性提升

**关键任务**:
- [ ] Phase 1: 架构设计 (0.5天)
- [ ] Phase 2: Skill 重构 (2-3天) 
  - DataFetchSkill, IndicatorSkill, VisualizationSkill
- [ ] Phase 3: 技术债务清理 (1天)
- [ ] Phase 4: 测试与优化 (0.5天)
- [ ] Phase 5: 发布 v1.4.0 (0.5天)

**预计工作量**: 8-10 小时

**参考文档**:
- `docs/ARCHITECTURE_CLAUDE_SKILLS.md` - Skill 模式设计
- `optimization/TECH_DEBT.md` - 技术债务追踪
- `optimization/v1.4.0_PLAN.md` - 详细开发计划

---

### 版本历史

#### v1.3.0 - Prompt 优化 ✅
- **发布日期**: 2025-12-14
- **主要改进**: Token 使用减少 67.6%，成本降低 67.6%
- **提交**: 75800c5

#### v1.2.0 - 可视化优化 ✅
- **发布日期**: 2025-12-13
- **主要改进**: 图表生成速度提升 31.2%

#### v1.1.0 - 基础版本 ✅
- **发布日期**: 2025-12-12
- **核心功能**: ReAct Agent + 数据获取 + 技术指标 + K线图表

---

**Happy Iterating!** 🚀✨

**维护者**: YFOOOO  
**最后更新**: 2025-12-15
