# AKShare API 文档摘要

> 本文档摘录 AKShare 金融数据接口的核心功能和使用方法

## 简介

**AKShare** 是一个开源的金融数据接口库，提供中国股票、期货、基金、债券等市场数据。

- 官网: https://akshare.akfamily.xyz/
- GitHub: https://github.com/akfamily/akshare
- 数据来源: 新浪财经、东方财富、腾讯财经等

## 核心接口

### 1. 股票历史数据

```python
import akshare as ak

# 获取股票日K线数据
stock_zh_a_hist(
    symbol="000001",           # 股票代码
    period="daily",            # 周期：daily, weekly, monthly
    start_date="20240101",     # 开始日期
    end_date="20241215",       # 结束日期
    adjust="qfq"               # 复权类型：qfq(前复权), hfq(后复权), ""(不复权)
)
```

**返回字段**:
- 日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率

### 2. ETF 数据

```python
# 获取ETF日线数据
fund_etf_hist_sina(
    symbol="510300",           # ETF代码
    period="daily",            # 周期
    start_date="20240101",     # 开始日期
    end_date="20241215"        # 结束日期
)
```

**返回字段**:
- 日期、开盘、最高、最低、收盘、成交量、成交额

## 数据特点

### 1. 更新频率
- **实时数据**: 交易日盘中更新（有15分钟延迟）
- **历史数据**: 每日收盘后更新

### 2. 数据范围
- **股票**: 支持沪深A股（1990年至今）
- **ETF**: 支持场内ETF（上市日至今）

### 3. 数据质量
- ✅ 自动处理停牌、退市等特殊情况
- ✅ 自动填充缺失数据
- ✅ 自动处理复权因子

## 使用限制

1. **请求频率**: 建议间隔 > 1秒（避免IP被封）
2. **数据量**: 单次查询最多返回10年数据
3. **并发**: 不支持多线程并发

## 错误处理

### 常见错误

1. **股票代码不存在**
```python
# 返回空 DataFrame 或抛出异常
```

2. **网络超时**
```python
# 需要重试机制（建议3次）
```

3. **数据为空**
```python
# 查询时间范围内无交易数据（停牌、退市等）
```

## 最佳实践

1. **添加重试机制**
```python
for i in range(3):
    try:
        df = ak.stock_zh_a_hist(symbol="000001")
        break
    except Exception as e:
        time.sleep(2)
```

2. **参数验证**
```python
assert len(symbol) == 6, "股票代码必须为6位数字"
assert days > 0 and days <= 365, "天数范围 [1, 365]"
```

3. **缓存数据**
```python
# 避免重复查询相同数据，考虑使用本地缓存
```

## 参考链接

- AKShare 官方文档: https://akshare.akfamily.xyz/data/stock/stock.html
- AKShare 数据字典: https://akshare.akfamily.xyz/data/data.html
