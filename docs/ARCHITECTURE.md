# 🏗️ 项目架构文档

> 金融数据分析助手的代码架构说明

## 📦 架构风格

本项目采用 **函数式架构**（而非面向对象），核心模块以独立函数的形式提供功能。

### 为什么选择函数式？

1. **简洁性**: 金融分析流程多为线性管道（数据获取 → 指标计算 → 可视化），函数式更直观
2. **可测试性**: 纯函数易于单元测试，无需 mock 复杂的对象状态
3. **组合性**: 函数可以灵活组合，支持不同的分析场景
4. **性能**: 避免对象创建开销，适合高频数据处理

---

## 📂 核心模块结构

```
core/
├── __init__.py              # 导出所有公共函数
├── data_fetcher.py          # 数据获取模块
├── indicators.py            # 技术指标计算
├── visualization.py         # 图表生成
├── llm_client.py            # LLM 客户端
├── safe_parsing.py          # 安全解析工具
├── ui_utils.py              # UI 工具函数
└── result_display.py        # 结果展示
```

---

## 🔌 公共 API（可导入函数）

### 1. 数据获取模块 (`core.data_fetcher`)

```python
from core.data_fetcher import (
    fetch_stock_daily,      # 获取股票日线数据
    fetch_etf_daily,        # 获取 ETF 日线数据
    fetch_data,             # 通用数据获取（自动识别类型）
    get_trading_days        # 获取交易日历
)
```

**使用示例**:
```python
# 获取贵州茅台 60 天数据
df = fetch_stock_daily("600519", "20231001", "20231130")

# 获取最近 N 个交易日
trading_days = get_trading_days(60)
```

---

### 2. 技术指标模块 (`core.indicators`)

```python
from core.indicators import (
    add_all_indicators,           # 一键计算所有指标
    calculate_ma,                 # 移动平均线
    calculate_macd,               # MACD 指标
    calculate_rsi,                # RSI 相对强弱指标
    calculate_bollinger_bands     # 布林带
)
```

**使用示例**:
```python
# 方式 1: 一键计算所有指标
df_with_indicators = add_all_indicators(df)

# 方式 2: 单独计算指标
df = calculate_ma(df, [5, 10, 20, 60])
df = calculate_macd(df)
df = calculate_rsi(df)
```

**返回列名**:
- MA: `ma_5`, `ma_10`, `ma_20`, `ma_60`
- MACD: `macd`, `macd_signal`, `macd_hist`
- RSI: `rsi`
- Bollinger Bands: `bb_upper`, `bb_middle`, `bb_lower`

---

### 3. 可视化模块 (`core.visualization`)

```python
from core.visualization import (
    plot_kline_basic,           # 基础 K 线图
    plot_kline_with_ma,         # K 线 + 均线
    plot_kline_with_macd,       # K 线 + MACD
    plot_comprehensive_chart,   # 综合图表（推荐）
    plot_auto                   # 自动选择图表类型
)
```

**使用示例**:
```python
# 绘制综合图表（K线 + MA + MACD + 成交量）
plot_comprehensive_chart(
    df_with_indicators,
    title="贵州茅台技术分析",
    save_path="chart.png"
)

# 自动模式（根据列名自动选择）
plot_auto(df_with_indicators, title="自动分析")
```

**图表面板结构**:
- **Panel 0**: K 线 + MA 均线
- **Panel 1**: 成交量（自动配色：红涨绿跌）
- **Panel 2**: MACD（如果存在 `macd` 列）
- **Panel 3**: RSI（如果存在 `rsi` 列）

---

### 4. LLM 客户端 (`core.llm_client`)

```python
from core.llm_client import get_llm_response

# 获取 LLM 分析
response = get_llm_response(
    prompt="分析贵州茅台的技术面",
    conversation_history=[...]
)
```

---

## 🔒 内部函数（不建议外部调用）

### 命名规范
- **前缀 `_`**: 表示内部函数，不应被外部导入
- **未在 `__init__.py` 导出**: 即使无 `_` 前缀，未导出的也视为内部函数

### 示例（`core.visualization` 内部函数）

```python
# ❌ 不推荐外部调用
from core.visualization import _configure_chinese_font  # 内部字体配置
from core.visualization import _prepare_plot_data       # 内部数据预处理

# ✅ 应该使用公共函数
from core.visualization import plot_comprehensive_chart
```

### 为什么要区分？

1. **API 稳定性**: 内部函数可能在版本迭代中修改/删除
2. **依赖管理**: 内部函数依赖其他内部状态，单独调用可能报错
3. **测试覆盖**: 公共函数有测试保障，内部函数仅通过集成测试验证

---

## 📋 导入最佳实践

### ✅ 推荐方式

```python
# 方式 1: 从子模块导入（明确来源）
from core.data_fetcher import fetch_stock_daily
from core.indicators import add_all_indicators
from core.visualization import plot_comprehensive_chart

# 方式 2: 从 core 导入（简洁，适合频繁使用）
from core import (
    fetch_stock_daily,
    add_all_indicators,
    plot_comprehensive_chart
)
```

### ❌ 不推荐方式

```python
# 错误 1: 尝试导入类（本项目无类）
from core import DataFetcher  # ❌ 不存在

# 错误 2: 导入内部函数
from core.visualization import _configure_chinese_font  # ⚠️ 内部函数

# 错误 3: 通配符导入（难以追踪来源）
from core import *  # 😱 不推荐
```

---

## 🧪 测试架构

### 单元测试（未来规划）

```python
# tests/test_indicators.py
def test_calculate_ma():
    df = pd.DataFrame({'close': [10, 11, 12, 13, 14]})
    result = calculate_ma(df, [3])
    assert 'ma_3' in result.columns
    assert result['ma_3'].iloc[-1] == 13.0  # (12+13+14)/3
```

### 集成测试（Notebook 验证）

当前通过 Notebook 进行集成测试：
- `optimization/optimize_visualization.ipynb` - 可视化功能验证
- 后续添加 `tests/integration_test.ipynb`

---

## 🔄 架构演进记录

### v1.0.0 - 初始架构
- 功能分散在单个 `agent_logic.py` 中
- 缺少模块化设计

### v1.1.0 - 模块化重构
- ✅ 拆分为 `core/` 模块
- ✅ 函数式设计
- ✅ 统一导出接口

### v1.1.1 - 架构文档化
- ✅ 创建本文档
- ✅ 规范导入约定
- ✅ 区分公共/内部函数

---

## 📚 相关文档

- [README.md](../README.md) - 项目总览
- [docs/docs.md](./docs.md) - 技术文档
- [docs/spec.md](./spec.md) - 功能规格说明
- [docs/PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - 项目总结
- [optimization/README.md](../optimization/README.md) - 优化框架

---

## 🤝 贡献指南

### 添加新函数

1. **编写函数** - 在对应模块中实现
2. **导出函数** - 在 `core/__init__.py` 中添加导出
3. **编写文档** - 在本文件更新 API 说明
4. **添加测试** - 创建单元测试（未来）
5. **更新示例** - 在 Notebook 中展示用法

### 修改内部函数

- ⚠️ 内部函数修改不需要更新本文档
- ✅ 但需要确保公共函数的行为不变
- 🧪 通过集成测试验证兼容性

---

**Last Updated**: 2025-12-14
**Version**: v1.1.1
