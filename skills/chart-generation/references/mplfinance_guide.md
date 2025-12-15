# mplfinance 使用指南

> 本文档提供 mplfinance 库的核心功能和最佳实践

## 简介

**mplfinance** 是一个基于 matplotlib 的金融图表库，专门用于绘制蜡烛图、OHLC图等金融图表。

- GitHub: https://github.com/matplotlib/mplfinance
- 文档: https://github.com/matplotlib/mplfinance/wiki
- 基于: matplotlib

## 核心功能

### 1. 基础蜡烛图

```python
import mplfinance as mpf

# 数据格式要求
# DataFrame with DatetimeIndex and columns: Open, High, Low, Close, Volume

mpf.plot(
    data,
    type='candle',        # 图表类型：candle, ohlc, line
    volume=True,          # 显示成交量
    style='charles',      # 内置样式
    title='Stock Chart',  # 标题
    savefig='chart.png'   # 保存路径
)
```

### 2. 添加移动平均线

```python
mpf.plot(
    data,
    type='candle',
    volume=True,
    mav=(5, 10, 20),     # 添加5日、10日、20日均线
    style='charles'
)
```

### 3. 自定义样式

```python
# 创建自定义样式
mc = mpf.make_marketcolors(
    up='red',            # 上涨蜡烛颜色
    down='green',        # 下跌蜡烛颜色
    edge='inherit',      # 边框颜色继承
    wick='inherit',      # 影线颜色继承
    volume='in',         # 成交量颜色与蜡烛一致
    alpha=0.9            # 透明度
)

s = mpf.make_mpf_style(
    marketcolors=mc,
    gridstyle='--',      # 网格样式
    gridcolor='gray',    # 网格颜色
    facecolor='black',   # 背景色
    figcolor='black'     # 图形背景色
)

mpf.plot(data, style=s)
```

### 4. 多副图（Panels）

```python
# 添加 MACD 副图
apds = [
    mpf.make_addplot(data['MACD_DIF'], panel=1, color='blue', ylabel='MACD'),
    mpf.make_addplot(data['MACD_DEA'], panel=1, color='orange'),
    mpf.make_addplot(data['MACD_BAR'], panel=1, type='bar', color='gray', alpha=0.5)
]

mpf.plot(
    data,
    type='candle',
    volume=True,
    addplot=apds,        # 添加副图
    panel_ratios=(3,1,1) # 主图:副图1:副图2 = 3:1:1
)
```

## 数据格式要求

### DataFrame 结构

```python
import pandas as pd

# 正确的数据格式
data = pd.DataFrame({
    'Open': [...],
    'High': [...],
    'Low': [...],
    'Close': [...],
    'Volume': [...]
}, index=pd.DatetimeIndex([...]))  # 必须是 DatetimeIndex

# 列名必须是：Open, High, Low, Close, Volume（首字母大写！）
```

### 列名转换

```python
# 如果数据列名是中文，需要转换
data_en = data.rename(columns={
    '日期': 'Date',
    '开盘': 'Open',
    '收盘': 'Close',
    '最高': 'High',
    '最低': 'Low',
    '成交量': 'Volume'
})
data_en.set_index('Date', inplace=True)
```

## 内置样式

mplfinance 提供多种内置样式：

| 样式名 | 说明 | 适用场景 |
|--------|------|----------|
| charles | 经典样式（深色背景） | 专业分析 |
| yahoo | Yahoo Finance 风格 | 网页展示 |
| nightclouds | 夜空云彩（深色） | 现代化 |
| sas | SAS 统计风格 | 报告输出 |
| mike | 清新简洁 | 简报 |

```python
# 使用内置样式
mpf.plot(data, style='nightclouds')
```

## 高级功能

### 1. 图表大小和分辨率

```python
mpf.plot(
    data,
    figsize=(12, 8),     # 图表大小（宽, 高）英寸
    figratio=(16, 9),    # 宽高比
    savefig=dict(
        fname='chart.png',
        dpi=150,         # 分辨率（DPI）
        bbox_inches='tight'  # 紧凑边界
    )
)
```

### 2. 中文显示

```python
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'STHeiti']  # 黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 然后正常绘图
mpf.plot(data, title='股票K线图')
```

### 3. 非交易日处理

```python
# 默认会显示所有日期（包括周末、节假日）
# 如果只想显示交易日，数据自然就是交易日

# 如果需要显示日期间隔
mpf.plot(
    data,
    show_nontrading=False  # 不显示非交易日
)
```

## 性能优化

### 1. 数据量控制

```python
# 大数据量时，只显示最近的数据
data_recent = data.tail(120)  # 最近120条
mpf.plot(data_recent)
```

### 2. 关闭交互模式

```python
# 生成图片时，关闭交互模式提升性能
import matplotlib
matplotlib.use('Agg')  # 非交互后端

mpf.plot(data, savefig='chart.png')
```

## 常见错误

### 1. 列名错误
```
KeyError: 'Open'
```
**解决**: 确保列名首字母大写（Open, High, Low, Close, Volume）

### 2. 索引类型错误
```
TypeError: DatetimeIndex required
```
**解决**: 确保索引是 DatetimeIndex 类型
```python
data.index = pd.to_datetime(data.index)
```

### 3. 数据顺序错误
```
ValueError: High must be >= Low
```
**解决**: 检查数据逻辑，确保 High >= Low, High >= Open, High >= Close

## 最佳实践

### 1. 封装绘图函数

```python
def plot_stock_chart(data, symbol, save_path=None):
    """统一的绘图接口"""
    # 数据预处理
    data_en = prepare_data(data)
    
    # 自定义样式
    style = create_custom_style()
    
    # 绘图
    mpf.plot(
        data_en,
        type='candle',
        volume=True,
        style=style,
        title=f'{symbol} K线图',
        savefig=save_path
    )
```

### 2. 错误处理

```python
try:
    mpf.plot(data, savefig='chart.png')
except Exception as e:
    print(f"图表生成失败: {e}")
    # 记录日志、降级处理等
```

### 3. 样式复用

```python
# 将样式保存为全局变量
DARK_STYLE = mpf.make_mpf_style(...)
LIGHT_STYLE = mpf.make_mpf_style(...)

# 使用时直接引用
mpf.plot(data, style=DARK_STYLE)
```

## 参考链接

- mplfinance GitHub: https://github.com/matplotlib/mplfinance
- mplfinance Wiki: https://github.com/matplotlib/mplfinance/wiki
- 示例代码: https://github.com/matplotlib/mplfinance/tree/master/examples
