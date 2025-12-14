# 📊 实验产出目录

此目录存放优化实验的产出文件，包括图表、报告等。

## 📁 目录结构

```
outputs/
├── baseline_demo.png       # 基线性能示例图
├── optimized_demo.png      # 优化后性能示例图
└── experiments/            # 各个实验的详细产出
    ├── viz_optimization/   # 可视化优化实验
    ├── llm_optimization/   # LLM 优化实验
    └── data_optimization/  # 数据获取优化实验
```

## 📋 文件管理规范

### ✅ 应保留的文件
- 实验对比图（baseline vs optimized）
- 最终版本的性能报告
- 关键实验的原始数据（CSV/JSON）

### 🗑️ 应清理的文件
- 中间测试图片（test_0.png, test_1.png...）
- 临时数据文件
- 重复的实验记录

### 🔄 定期清理
建议每次 minor 版本发布后（如 v1.2.0）：
1. 归档当前实验产出到 `experiments/<version>/`
2. 清理临时测试文件
3. 保留代表性的对比图表

## 🎯 Git 管理

- **`.gitignore` 配置**: 排除所有 `*.png`，但保留 `outputs/` 目录下的文件
- **提交策略**: 仅提交有对比价值的实验结果图
- **大小限制**: 单个文件不超过 1MB，优先使用压缩格式
