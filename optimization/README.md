# 🔬 优化与评估框架

> 系统化的性能优化和质量评估工作空间

## 🎯 核心理念

- **质量优先**: 准确性和用户体验是第一位
- **快速迭代**: 完成优化即发布，保持敏捷
- **数据驱动**: 每次优化都有基准对比
- **实验记录**: 所有尝试都值得记录

## 📊 评估维度

### 1. 性能评估 (Performance)
- **数据获取速度**: AKShare API 响应时间
- **指标计算效率**: 技术指标计算耗时
- **LLM 响应时间**: 各模型端到端延迟
- **内存占用**: 数据存储和处理内存使用

### 2. 质量评估 (Quality)
- **LLM 输出准确性**: 分析结论的准确性和完整性
- **技术指标正确性**: 与标准库对比验证
- **图表美观度**: 可视化效果评分
- **用户体验**: 交互流畅度和错误处理

### 3. 成本评估 (Cost)
- **LLM API 费用**: Token 使用量和成本
- **数据获取频率**: API 调用次数限制
- **存储成本**: 历史数据和图表存储

## 📁 文件说明

### `eval_framework.ipynb` - 评估框架
**目的**: 建立基准测试和评估体系

**内容**:
- 性能基准测试套件
- 质量评估标准
- 成本计算模型
- 对比分析工具

### `optimize_llm_prompts.ipynb` - Prompt 优化
**目的**: 优化 LLM Prompt，提升输出质量和降低成本

**优化方向**:
- 减少冗余描述，提高 Token 效率
- 优化 Few-shot 示例
- 改进输出格式约束
- 测试不同模型表现

### `optimize_data_fetching.ipynb` - 数据获取优化
**目的**: 提升数据获取速度和可靠性

**优化方向**:
- 实现缓存机制
- 并行获取多只股票
- 错误重试策略
- 数据预加载

### `optimize_indicators.ipynb` - 指标计算优化
**目的**: 提升技术指标计算效率

**优化方向**:
- 向量化计算（NumPy）
- 批量处理优化
- 可选指标按需计算
- 内存优化

### `optimize_visualization.ipynb` - 可视化优化
**目的**: 提升图表生成速度和美观度

**优化方向**:
- 图表模板缓存
- 异步生成
- 样式优化
- 响应式尺寸

## 📈 评估流程

```
1. 运行 eval_framework.ipynb
   ↓ 建立基准数据
   
2. 针对性优化
   ↓ 使用专项优化 Notebook
   
3. 重新评估
   ↓ 对比优化前后数据
   
4. 记录结果
   ↓ 更新 benchmark_results.json
   
5. 版本发布
   ↓ 合并到主分支，打标签
```

## 🎯 优化目标

### v1.2.0 目标
- [ ] LLM 响应时间减少 20%
- [ ] Token 使用量降低 30%
- [ ] 数据获取支持缓存
- [ ] 批量分析性能提升 50%
- [ ] 图表生成速度提升 30%

### v1.3.0 目标
- [ ] 实现实时监控功能
- [ ] 支持自定义指标
- [ ] Web 界面（Streamlit）
- [ ] 回测功能

## 📝 使用说明

### 开始优化前
```bash
# 1. 创建开发分支
git checkout -b dev/optimization

# 2. 运行基准测试
jupyter notebook optimization/eval_framework.ipynb
```

### 优化过程中
```bash
# 针对性运行优化 Notebook
jupyter notebook optimization/optimize_llm_prompts.ipynb
```

### 优化完成后
```bash
# 1. 重新运行评估
jupyter notebook optimization/eval_framework.ipynb

# 2. 提交代码
git add .
git commit -m "⚡ 优化: [描述]"

# 3. 合并到主分支
git checkout main
git merge dev/optimization

# 4. 打版本标签
git tag v1.2.0
git push origin main --tags
```

## 质量保证

### 提交前自动检查

本项目配置了 Git Hook，每次提交前自动运行：

1. ✅ **代码格式检查**: Black/isort 自动格式化
2. ✅ **类型检查**: MyPy 静态类型分析
3. ✅ **单元测试**: 核心模块测试（快速）
4. ✅ **性能回归检测**: 与最新基准对比

如果检查失败，提交将被阻止，需要修复后重新提交。

### 质量标准

每次优化必须满足：
- ✅ 功能完整性（不破坏现有功能）
- ✅ 性能提升或持平（不允许回退）
- ✅ 代码可读性（保持良好风格）
- ✅ 文档同步更新（README、docs、spec）

## �📊 基准数据管理

### 目录结构

```
optimization/benchmarks/
├── v1.1.0_baseline.json       # v1.1.0 基准数据
├── v1.2.0_alpha_1.json        # v1.2.0 第1次优化
├── v1.2.0_alpha_2.json        # v1.2.0 第2次优化
├── v1.2.0_final.json          # v1.2.0 最终数据
└── comparison_report.ipynb    # 自动生成对比报告
```

### 数据格式

```json
{
  "version": "v1.1.0",
  "timestamp": "2025-12-14T17:30:00",
  "performance": {
    "data_fetching_avg": 1.2,
    "indicator_calculation_avg": 0.8,
    "llm_response_avg": 3.5,
    "end_to_end_avg": 6.2
  },
  "quality": {
    "format_correct_rate": 0.95,
    "content_complete_rate": 0.88,
    "has_trend_analysis_rate": 1.0,
    "has_indicator_analysis_rate": 0.92,
    "has_recommendation_rate": 0.85
  },
  "cost": {
    "total_cost_cny": 0.0035,
    "cost_per_1k_queries_cny": 3.5,
    "avg_total_tokens": 2500
  }
}
```

---

**版本**: v1.1.0  
**创建日期**: 2025-12-14  
**维护者**: YFOOOO
