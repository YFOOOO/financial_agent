# 📊 Agent 运行时输出目录

此目录存放 Agent 运行时生成的临时文件（图表、数据等）。

## 📋 说明

- **自动生成**: 当运行 `agent_logic.py` 或 `financial_agent_demo.ipynb` 时自动创建
- **临时文件**: 这些文件不会被 Git 追踪（已在 `.gitignore` 中配置）
- **定期清理**: 建议定期清理旧文件以节省空间

## 🔄 与优化目录的区别

| 目录 | 用途 | Git 追踪 |
|------|------|----------|
| `outputs/` | Agent 运行时的临时输出 | ❌ 不追踪 |
| `optimization/outputs/` | 优化实验的对比图表 | ✅ 追踪（用于演示） |

## 🗑️ 清理命令

```bash
# 清理所有图片文件
rm -f outputs/*.png

# 清理所有 CSV 文件
rm -f outputs/*.csv

# 清理所有文件（保留 README）
find outputs/ -type f ! -name 'README.md' -delete
```

## 📝 文件命名规范

Agent 自动生成的文件遵循以下命名规范：

- **K 线图**: `kline_YYYYMMDD_HHMMSS.png`
- **综合图表**: `comprehensive_YYYYMMDD_HHMMSS.png`
- **数据文件**: `stock_data_with_indicators.csv`

---

**提示**: 如果需要保存某个分析结果，请手动复制到其他目录。
