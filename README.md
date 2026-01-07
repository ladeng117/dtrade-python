# DTrader Python SDK 接口文档

`dtrade` 是一个用于连接 DTrader 交易柜台的 Python SDK，提供了全面的 A 股实时行情获取和程序化交易功能。

## 目录

- [安装与配置](#安装与配置)
- [快速开始](#快速开始)
- [客户端初始化](#客户端初始化)
- [数据模型 (Models)](#数据模型-models)
- [行情模块 (Market API)](#行情模块-market-api)
  - [基础行情](#基础行情)
    - [get_snapshot](#get_snapshot)
    - [get_index_data](#get_index_data)
    - [get_market_indices](#get_market_indices)
  - [K线与历史数据](#k线与历史数据)
    - [get_kline_data](#get_kline_data)
    - [get_today_kline](#get_today_kline)
    - [get_recent_kline](#get_recent_kline)
    - [get_index_kline](#get_index_kline)
    - [get_minute_data](#get_minute_data)
    - [get_tick_data](#get_tick_data)
  - [榜单与统计](#榜单与统计)
    - [get_hot_industry](#get_hot_industry)
    - [get_hot_concept](#get_hot_concept)
    - [get_hot_etf](#get_hot_etf)
    - [get_stock_count](#get_stock_count)
    - [get_stock_list](#get_stock_list)
  - [高级分析](#高级分析)
    - [get_hot_stock](#get_hot_stock)
    - [get_limit_up_info](#get_limit_up_info)
    - [get_force_rising](#get_force_rising)
    - [get_stock_fluctuation](#get_stock_fluctuation)
    - [get_main_testing](#get_main_testing)
    - [get_weak_strong](#get_weak_strong)
    - [get_smart_buy](#get_smart_buy)
    - [get_hot_event](#get_hot_event)
    - [get_ths_hot_code](#get_ths_hot_code)
  - [基本面与辅助](#基本面与辅助)
    - [get_finance_info](#get_finance_info)
    - [get_dividend_info](#get_dividend_info)
    - [validate_stock_code](#validate_stock_code)
    - [get_stock_with_retry](#get_stock_with_retry)
- [交易模块 (Trading API)](#交易模块-trading-api)
  - [账户与持仓](#账户与持仓)
    - [get_account_info](#get_account_info)
    - [get_balance](#get_balance)
    - [get_positions](#get_positions)
    - [get_position](#get_position)
  - [订单管理](#订单管理)
    - [get_all_orders](#get_all_orders)
    - [get_order](#get_order)
  - [交易操作](#交易操作)
    - [buy](#buy)
    - [sell](#sell)
    - [cancel_order](#cancel_order)
    - [batch_buy](#batch_buy)
    - [batch_sell](#batch_sell)
- [异常处理](#异常处理)

---

## 安装与配置

请确保已安装 `requests` 库：

```bash
pip install requests
```

将 `dtrade` 包文件夹放置在您的项目目录中。

## 快速开始

```python
from dtrade import DTraderClient

# 1. 初始化客户端
client = DTraderClient(
    host="127.0.0.1", 
    port=6756, 
    api_key="your_api_key"
)

# 2. 获取行情
snapshot = client.market.get_snapshot("000001")[0]
print(f"平安银行: {snapshot.price}")

# 3. 查询资产
account = client.trading.get_account_info()
print(f"可用资金: {account.available_cash}")

# 4. 下单买入 (示例)
# result = client.trading.buy("000001", 10.5, 100)
# print(f"下单结果: {result.success}, 订单ID: {result.order_id}")
```

## 客户端初始化

### `DTraderClient`

主客户端类，用于管理连接和访问子模块。

```python
client = DTraderClient(
    host="127.0.0.1",  # 服务器地址
    port=6756,         # 服务器端口
    api_key="your_api_key", # API Key
    timeout=30         # 请求超时时间(秒)
)
```

# DTrader 客户端配置文件
{
    "host":"127.0.0.1",
    "port":"6756",
    "token":"需要付费购买",
    "api_key":"your_api_key"
}



**属性:**
- `client.market`: 访问行情模块 (`MarketAPI`)
- `client.trading`: 访问交易模块 (`TradingAPI`)

**方法:**
- `client.close()`: 关闭连接会话

---

## 数据模型 (Models)

SDK 返回的数据通常封装在以下对象中，而非原始字典：

- **MarketSnapshot**: 实时五档快照 (price, volume, ask_prices, bid_volumes...)
- **KLineData**: K线数据 (timestamp, open, close, high, low, volume...)
- **MinuteData**: 分时数据 (timestamp, price, volume, avg_price...)
- **TickData**: 逐笔成交 (timestamp, price, volume, type...)
- **Order**: 订单信息 (order_id, stock_code, price, volume, state...)
- **Position**: 持仓信息 (stock_code, volume, cost_price, profit_loss...)
- **AccountInfo**: 账户资金 (total_assets, available_cash...)
- **RankingItem**: 榜单项 (code, name, value, change_rate...)
- **FinanceInfo**: 财务信息 (pe, eps, revenue...)

---

## 行情模块 (Market API)

通过 `client.market` 访问。

### 基础行情

#### `get_snapshot`
获取一只或多只股票的实时五档快照。

- **参数**:
  - `stock_codes` (str | List[str]): 股票代码（如 "000001"）或代码列表。
- **返回**: `List[MarketSnapshot]`
- **示例**:
  ```python
  # 单只
  snaps = client.market.get_snapshot("000001")
  # 批量
  snaps = client.market.get_snapshot(["000001", "600519"])
  ```

#### `get_index_data`
获取指数实时行情。

- **参数**:
  - `index_code` (str): 指数代码 (e.g., "sh000001")。
- **返回**: `Optional[MarketSnapshot]` (如果未找到返回 None)
- **示例**:
  ```python
  index = client.market.get_index_data("sh000001")
  if index:
      print(f"上证指数: {index.price}")
  ```

#### `get_market_indices`
获取主要市场指数列表。

- **参数**: 无
- **返回**: `List[Dict[str, Any]]` (包含指数代码、名称、价格等)
- **示例**:
  ```python
  indices = client.market.get_market_indices()
  ```

### K线与历史数据

#### `get_kline_data`
获取通用K线数据。

- **参数**:
  - `stock_code` (str): 股票代码
  - `period` (str): 周期 ("1m", "5m", "15m", "30m", "1h", "1d", "1w", "1M")
  - `count` (int): 数量，默认 100
  - `start_date` / `end_date`: (预留参数，暂不支持)
- **返回**: `List[KLineData]`
- **示例**:
  ```python
  klines = client.market.get_kline_data("000001", "1d", 20)
  ```

#### `get_today_kline`
获取今日分钟线（快捷方法）。

- **参数**:
  - `stock_code` (str): 股票代码
  - `period` (str): 默认 "1m"
  - `count` (int): 默认 100
- **返回**: `List[KLineData]`

#### `get_recent_kline`
获取近期日K线（快捷方法）。

- **参数**:
  - `stock_code` (str): 股票代码
  - `period` (str): 默认 "1d"
  - `days` (int): 天数（默认30，实际受 count 限制）
- **返回**: `List[KLineData]`

#### `get_index_kline`
获取指数K线数据。

- **参数**:
  - `index_code` (str): 指数代码
  - `period` (str): 周期
  - `count` (int): 数量
- **返回**: `List[KLineData]`

#### `get_minute_data`
获取分时数据（当日或历史）。

- **参数**:
  - `stock_code` (str): 股票代码
  - `date` (Optional[str]): 历史日期字符串 "YYYYMMDD" (e.g., "20240816")。不填则为今日。
- **返回**: `List[MinuteData]`
- **示例**:
  ```python
  # 今日分时
  mins = client.market.get_minute_data("000001")
  # 历史分时
  hist_mins = client.market.get_minute_data("000001", date="20240816")
  ```

#### `get_tick_data`
获取逐笔成交数据。

- **参数**:
  - `stock_code` (str): 股票代码
  - `count` (int): 数量
  - `date` (Optional[str]): 历史日期 "YYYYMMDD"
- **返回**: `List[TickData]`
- **示例**:
  ```python
  ticks = client.market.get_tick_data("000001", 100)
  ```

### 榜单与统计

#### `get_hot_industry`
获取热门行业榜单。

- **返回**: `List[Dict]`
- **示例**:
  ```python
  industries = client.market.get_hot_industry()
  ```

#### `get_hot_concept`
获取热门概念榜单。

- **返回**: `List[Dict]`

#### `get_hot_etf`
获取热门 ETF 榜单。

- **返回**: `List[Dict]`

#### `get_stock_count`
获取某市场的股票总数。

- **参数**: `market` (str): "sh" 或 "sz"
- **返回**: `int` (或包含 count 的字典)

#### `get_stock_list`
获取某市场的股票列表（分页）。

- **参数**:
  - `market` (str): "sh" 或 "sz"
  - `start` (int): 起始索引
- **返回**: `List[str]` (股票代码列表)

### 高级分析

以下接口返回 `List[RankingItem]`，每个 Item 包含股票代码、名称及特定的数值（如热度值、涨幅等）。

#### `get_hot_stock`
获取个股热度排行榜。

- **返回**: `List[RankingItem]`

#### `get_limit_up_info`
获取涨停股分析信息。

- **返回**: `List[RankingItem]`

#### `get_force_rising`
获取强势股列表。

- **返回**: `List[RankingItem]`

#### `get_stock_fluctuation`
获取异动股列表。

- **返回**: `List[RankingItem]`

#### `get_main_testing`
获取主力试盘股列表。

- **返回**: `List[RankingItem]`

#### `get_weak_strong`
获取强弱分析列表。

- **返回**: `List[RankingItem]`

#### `get_smart_buy`
获取智能买入推荐列表。

- **返回**: `List[RankingItem]`

#### `get_hot_event`
获取热点事件相关股票。

- **返回**: `List[RankingItem]`

#### `get_ths_hot_code`
获取同花顺热榜代码。

- **返回**: `List[RankingItem]`

### 基本面与辅助

#### `get_finance_info`
获取个股财务信息。

- **参数**: `stock_code` (str)
- **返回**: `FinanceInfo` (包含 pe, eps, bvps, revenue 等)
- **示例**:
  ```python
  fin = client.market.get_finance_info("000001")
  print(f"市盈率: {fin.pe}")
  ```

#### `get_dividend_info`
获取分红配送记录。

- **参数**: `stock_code` (str)
- **返回**: `List[Dict]`

#### `validate_stock_code`
验证股票代码格式是否正确（简单正则校验）。

- **参数**: `stock_code` (str)
- **返回**: `bool`

#### `get_stock_with_retry`
带重试机制的行情获取。在网络不稳定时很有用。

- **参数**:
  - `stock_code` (str)
  - `max_retries` (int): 最大重试次数，默认3
  - `delay` (float): 重试间隔秒数，默认1.0
- **返回**: `Optional[MarketSnapshot]`

---

## 交易模块 (Trading API)

通过 `client.trading` 访问。

### 账户与持仓

#### `get_account_info`
获取详细账户资金信息。

- **参数**: 无
- **返回**: `AccountInfo`
  - `total_assets`: 总资产
  - `available_cash`: 可用资金
  - `market_value`: 持仓市值
  - `profit_loss`: 总盈亏
- **示例**:
  ```python
  acct = client.trading.get_account_info()
  ```

#### `get_balance`
获取简要资金字典。

- **参数**: 无
- **返回**: `Dict` (包含 total_assets, available_cash 等)

#### `get_positions`
获取所有持仓列表。

- **参数**: 无
- **返回**: `List[Position]`
  - `stock_code`: 股票代码
  - `volume`: 持仓数量
  - `available_volume`: 可用数量
  - `cost_price`: 成本价
  - `current_price`: 现价
  - `profit_loss`: 浮动盈亏

#### `get_position`
获取指定股票的持仓信息。

- **参数**: `stock_code` (str)
- **返回**: `Optional[Position]` (如果无持仓则返回 None)
- **示例**:
  ```python
  pos = client.trading.get_position("000001")
  if pos:
      print(f"持仓 {pos.volume} 股")
  ```

### 订单管理

#### `get_all_orders`
获取所有委托单。

- **参数**:
  - `status` (Optional[str]): 按状态过滤。可选值见 `OrderState` 枚举 (e.g., "submitted", "filled", "cancelled", "rejected")。
- **返回**: `List[Order]`
- **示例**:
  ```python
  # 获取所有
  orders = client.trading.get_all_orders()
  # 获取已成交
  filled = client.trading.get_all_orders(status="filled")
  ```

#### `get_order`
查询指定订单详情。

- **参数**: `order_id` (str)
- **返回**: `Order`
- **示例**:
  ```python
  order = client.trading.get_order("123456")
  ```

### 交易操作

#### `buy`
限价买入。

- **参数**:
  - `stock_code` (str): 股票代码
  - `price` (float): 买入价格
  - `volume` (int): 买入数量 (通常为100的整数倍)
- **返回**: `TradeResult`
  - `success` (bool): 是否成功
  - `order_id` (str): 委托编号 (成功时)
  - `message` (str): 错误信息 (失败时)
- **示例**:
  ```python
  res = client.trading.buy("000001", 10.0, 100)
  ```

#### `sell`
限价卖出。

- **参数**:
  - `stock_code` (str): 股票代码
  - `price` (float): 卖出价格
  - `volume` (int): 卖出数量
- **返回**: `TradeResult`

#### `cancel_order`
撤销委托。

- **参数**: `order_id` (str)
- **返回**: `TradeResult`
- **示例**:
  ```python
  client.trading.cancel_order("123456")
  ```

#### `batch_buy`
批量买入。

- **参数**: `orders` (List[Dict])
  - 字典结构: `{"stock_code": str, "price": float, "volume": int}`
- **返回**: `List[TradeResult]`
- **示例**:
  ```python
  orders = [
      {"stock_code": "000001", "price": 10.0, "volume": 100},
      {"stock_code": "600000", "price": 8.5, "volume": 200}
  ]
  results = client.trading.batch_buy(orders)
  ```

#### `batch_sell`
批量卖出。

- **参数**: `orders` (List[Dict])
  - 字典结构: `{"stock_code": str, "price": float, "volume": int}`
- **返回**: `List[TradeResult]`

---

## 异常处理

SDK 定义了以下异常类型 (在 `dtrade.exceptions` 中)：

- **DTraderError**: 所有异常的基类
- **APIError**: 服务器返回错误代码 (e.g., 账户未登录, 参数错误)
- **ValidationError**: 本地参数验证错误 (e.g., 价格为负, 代码格式错误)
- **AuthenticationError**: API Key 无效
- **MarketDataError**: 行情获取失败
- **TradingError**: 交易操作失败 (如资金不足, 持仓不足)
- **ConnectionError**: 网络连接失败
- **TimeoutError**: 请求超时

建议在代码中使用 `try-except` 块包裹 API 调用，以提高程序的健壮性：

```python
from dtrade.exceptions import TradingError, MarketDataError

try:
    client.trading.buy("000001", 10.0, 100)
except TradingError as e:
    print(f"交易错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```
