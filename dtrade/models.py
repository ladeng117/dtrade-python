"""
Data models for dtrade-python
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum


class OrderType(Enum):
    """Order type enumeration"""
    BUY = "buy"
    SELL = "sell"
    # 保持向后兼容性
    证券买入 = "buy"
    证券卖出 = "sell"
    
    @classmethod
    def _missing_(cls, value):
        """处理未知值"""
        value_lower = str(value).lower()
        if value_lower == "buy" or "买入" in str(value):
            return cls.BUY
        elif value_lower == "sell" or "卖出" in str(value):
            return cls.SELL
        raise ValueError(f"'{value}' is not a valid OrderType")


class OrderState(Enum):
    """Order state enumeration"""
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    # 保持向后兼容性
    已报 = "submitted"
    部成 = "partially_filled"
    已成 = "filled"
    已撤 = "cancelled"
    废单 = "rejected"
    
    @classmethod
    def _missing_(cls, value):
        """处理未知值"""
        value_str = str(value)
        value_lower = value_str.lower()
        
        # 映射英文值
        if value_lower == "submitted" or "已报" in value_str:
            return cls.SUBMITTED
        elif value_lower == "partially_filled" or "部成" in value_str:
            return cls.PARTIALLY_FILLED
        elif value_lower == "filled" or "已成" in value_str:
            return cls.FILLED
        elif value_lower == "cancelled" or "已撤" in value_str:
            return cls.CANCELLED
        elif value_lower == "rejected" or "废单" in value_str or "无效" in value_str:
            return cls.REJECTED
        
        # 记录未知状态并默认为废单，或者抛出异常？
        # 为了程序的健壮性，对于未知的非成功状态，可以归类为 REJECTED 或 SUBMITTED (视情况而定)
        # 这里我们选择宽容处理，如果包含"无效"、"失败"等词，归为 REJECTED
        if "失败" in value_str:
            return cls.REJECTED
            
        raise ValueError(f"'{value}' is not a valid OrderState")


@dataclass
class Order:
    """Order information"""
    order_id: str
    stock_code: str
    stock_name: str
    order_type: OrderType
    order_price: float
    order_volume: int
    order_state: OrderState
    dealt_price: Optional[float] = None
    dealt_volume: Optional[int] = None
    order_time: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Create Order from API response dictionary"""
        # 处理字段名映射
        order_type_value = data.get("order_type") or data.get("type", "")
        order_state_value = data.get("order_state") or data.get("state", "")
        
        return cls(
            order_id=str(data.get("order_id", "")),
            stock_code=data.get("stock_code") or data.get("code", ""),
            stock_name=data.get("stock_name") or data.get("name", ""),
            order_type=OrderType(order_type_value),
            order_price=float(data.get("order_price") or data.get("price", 0)),
            order_volume=int(data.get("order_volume") or data.get("volume", 0)),
            order_state=OrderState(order_state_value),
            dealt_price=float(data.get("dealt_price", 0)) if data.get("dealt_price") else None,
            dealt_volume=int(data.get("dealt_volume", 0)) if data.get("dealt_volume") else None,
            order_time=datetime.fromisoformat(data["order_time"]) if data.get("order_time") else None
        )


@dataclass
class AccountInfo:
    """Account information"""
    account_id: str
    account_name: str
    total_assets: float
    available_cash: float
    market_value: float
    profit_loss: float
    profit_loss_rate: float
    frozen_cash: float  # 新增属性

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountInfo':
        """Create AccountInfo from API response dictionary"""
        return cls(
            account_id=str(data.get("account_id") or data.get("asset_account", "")),
            account_name=str(data.get("account_name") or data.get("broker", "")),
            total_assets=float(data.get("total_assets") or data.get("total_asset", 0)),
            available_cash=float(data.get("available_cash") or data.get("free_amount", 0)),
            market_value=float(data.get("market_value") or data.get("stock_market_value", 0)),
            profit_loss=float(data.get("profit_loss") or data.get("position_profit", 0)),
            profit_loss_rate=float(data.get("profit_loss_rate", 0)),
            frozen_cash=float(data.get("frozen_cash") or data.get("frozen_capital", 0))
        )


@dataclass
class Position:
    """Position information"""
    stock_code: str
    stock_name: str
    current_price: float
    cost_price: float
    volume: int  # 确保有这个属性
    available_volume: int
    market_value: float
    profit_loss: float
    profit_loss_rate: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        """Create Position from dictionary"""
        # 字段名映射
        field_mapping = {
            "stock_code": ["code", "stock_code"],
            "stock_name": ["name", "stock_name"],
            "current_price": ["current_price", "price", "market_price"],
            "cost_price": ["cost_price", "cost"],
            "volume": ["volume", "current_amount", "vol_actual"],
            "available_volume": ["available_volume", "enable_amount", "vol_remain"],
            "market_value": ["market_value", "value"],
            "profit_loss": ["profit_loss", "profit", "curr_profit"],
            "profit_loss_rate": ["profit_loss_rate", "profit_rate", "profit_ratio"]
        }
        
        mapped_data = {}
        for field, possible_keys in field_mapping.items():
            value = None
            for key in possible_keys:
                if key in data:
                    value = data[key]
                    break
            if value is None:
                value = 0 if field in ["volume", "available_volume"] else 0.0
            mapped_data[field] = value
        
        return cls(**mapped_data)


@dataclass
class MarketSnapshot:
    """Market snapshot (五档行情)"""
    symbol: str
    price: float
    last_close: float
    change: float
    change_percent: float
    volume: int
    amount: float
    bid_prices: List[float]
    ask_prices: List[float]
    bid_volumes: List[int]
    ask_volumes: List[int]
    timestamp: datetime
    
    @property
    def stock_code(self) -> str:
        """Alias for symbol"""
        return self.symbol

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketSnapshot':
        """Create MarketSnapshot from API response dictionary"""
        # 提取买卖盘数据
        bid_prices = []
        bid_volumes = []
        ask_prices = []
        ask_volumes = []
        
        for i in range(1, 6):
            bid_prices.append(float(data.get(f"Bid{i}") or data.get(f"bid{i}", 0)))
            bid_volumes.append(int(data.get(f"BidVol{i}") or data.get(f"bid_vol{i}", 0)))
            ask_prices.append(float(data.get(f"Ask{i}") or data.get(f"ask{i}", 0)))
            ask_volumes.append(int(data.get(f"AskVol{i}") or data.get(f"ask_vol{i}", 0)))

        # 兼容小写和首字母大写的字段名
        price = float(data.get("Price") or data.get("price", 0))
        last_close = float(data.get("LastClose") or data.get("last_close", 0))
        
        # 如果没有 change 字段，尝试计算
        change = float(data.get("Change") or data.get("change", 0))
        if change == 0 and price > 0 and last_close > 0:
            change = price - last_close
            
        return cls(
            symbol=str(data.get("Code") or data.get("code") or data.get("symbol", "")),
            price=price,
            last_close=last_close,
            change=change,
            change_percent=float(data.get("Rate") or data.get("change_percent", 0)),
            volume=int(data.get("Vol") or data.get("volume", 0)),
            amount=float(data.get("Amount") or data.get("amount", 0)),
            bid_prices=bid_prices,
            ask_prices=ask_prices,
            bid_volumes=bid_volumes,
            ask_volumes=ask_volumes,
            timestamp=datetime.now() # 默认当前时间，或者解析 TimeStamp
        )


@dataclass
class TradeResult:
    """Trade result"""
    success: bool
    order_id: Optional[str] = None
    message: Optional[str] = None
    error_code: Optional[int] = None
    stock_code: Optional[str] = None  # 新增
    price: Optional[float] = None     # 新增
    volume: Optional[int] = None      # 新增
    status: Optional[str] = None      # 新增

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeResult":
        """Create TradeResult from dictionary"""
        # 初始化默认值
        order_id = None
        stock_code = None
        price = None
        volume = None
        status = None
        
        # 处理嵌套的 data 字段
        if "data" in data:
            raw_data = data["data"]
            if isinstance(raw_data, dict):
                order_id = raw_data.get("order_id")
                stock_code = raw_data.get("stock_code")
                price = raw_data.get("price")
                volume = raw_data.get("volume")
                status = raw_data.get("status")
            elif isinstance(raw_data, (str, int)):
                # 如果 data 直接是 ID
                order_id = str(raw_data)
        
        # 如果从 data 中没取到，尝试从顶层取
        if order_id is None:
            order_id = data.get("order_id")
        if stock_code is None:
            stock_code = data.get("stock_code")
        if price is None:
            price = data.get("price")
        if volume is None:
            volume = data.get("volume")
        if status is None:
            status = data.get("status")
        
        return cls(
            success=data.get("code", 0) == 0,
            order_id=order_id,
            message=data.get("msg"),
            error_code=data.get("code"),
            stock_code=stock_code,
            price=price,
            volume=volume,
            status=status
        )


@dataclass
class KLineData:
    """K-line data"""
    symbol: str
    period: str
    timestamp: datetime
    open: float
    close: float
    high: float
    low: float
    volume: int
    amount: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KLineData':
        """Create KLineData from API response dictionary"""
        return cls(
            symbol=data.get("symbol", "") or data.get("code", ""),
            period=data.get("period", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            open=float(data.get("open", 0)),
            close=float(data.get("close", 0)),
            high=float(data.get("high", 0)),
            low=float(data.get("low", 0)),
            volume=int(data.get("volume", 0)),
            amount=float(data.get("amount", 0))
        )


@dataclass
class MinuteData:
    """分时数据"""
    timestamp: datetime
    price: float
    volume: int
    amount: float
    avg_price: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], base_date: Optional[str] = None, index: Optional[int] = None) -> 'MinuteData':
        """
        从字典创建分时数据
        
        Args:
            data: 数据字典
            base_date: 基础日期 (YYYYMMDD)
            index: 数据索引 (用于在没有时间字段时推算时间)
        """
        # 兼容不同的时间字段格式
        ts_str = data.get("time") or data.get("timestamp", "")
        timestamp = datetime.now()
        
        # 确定基础日期
        base_dt = datetime.now()
        if base_date:
            try:
                base_dt = datetime.strptime(str(base_date), "%Y%m%d")
            except Exception:
                pass

        if ts_str:
            try:
                if len(str(ts_str)) == 14: # YYYYMMDDHHMMSS
                    timestamp = datetime.strptime(str(ts_str), "%Y%m%d%H%M%S")
                elif "T" in str(ts_str):
                    timestamp = datetime.fromisoformat(str(ts_str))
                else:
                    # 假设是 HH:MM 格式
                    time_part = datetime.strptime(str(ts_str), "%H:%M")
                    timestamp = base_dt.replace(hour=time_part.hour, minute=time_part.minute, second=0, microsecond=0)
            except Exception:
                pass
        elif index is not None:
            # 如果没有时间字段，尝试根据索引推算 (针对A股交易时间)
            # 09:30 - 11:30 (0-120), 13:00 - 15:00 (121-240)
            # 注意：通常第一条是09:30或09:31，这里假设从09:30开始
            try:
                minutes_from_start = index
                start_dt = base_dt.replace(hour=9, minute=30, second=0, microsecond=0)
                
                if minutes_from_start <= 120:
                    delta = timedelta(minutes=minutes_from_start)
                    timestamp = start_dt + delta
                else:
                    # 下午盘，从13:00开始计算
                    # index 121 对应 13:01? 或者 index 120 对应 11:30?
                    # 假设 0-120 是上午 (121个点?), 121-241 是下午
                    # 通常分时数据是240个点 (09:31-11:30, 13:01-15:00)
                    # 或者是 241个点 (包含09:30)
                    
                    # 简化处理：上午 09:30 + index, 如果超过 11:30 则跳到 13:00
                    # 但中间休市 90 分钟
                    if minutes_from_start > 120: 
                         # 减去上午的120分钟，加上中午休市的90分钟 = +90
                         # 实际上：11:30 -> 13:00 是 +90分钟
                         delta = timedelta(minutes=minutes_from_start + 90)
                    else:
                         delta = timedelta(minutes=minutes_from_start)
                    
                    timestamp = start_dt + delta
            except Exception:
                pass
                
        return cls(
            timestamp=timestamp,
            price=float(data.get("price", 0)),
            volume=int(data.get("volume", 0) or data.get("vol", 0)),
            amount=float(data.get("amount", 0) or data.get("money", 0)),
            avg_price=float(data.get("avg_price", 0) or data.get("avg", 0))
        )


@dataclass
class TickData:
    """逐笔交易数据"""
    timestamp: datetime
    price: float
    volume: int
    amount: float
    type: str # B/S/M (Buy/Sell/Neutral)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], base_date: Optional[str] = None) -> 'TickData':
        """
        从字典创建Tick数据
        
        Args:
            data: 数据字典
            base_date: 基础日期 (YYYYMMDD), 用于补全时间
        """
        ts_str = data.get("time") or data.get("timestamp", "")
        timestamp = datetime.now()
        
        # 确定基础日期
        base_dt = datetime.now()
        if base_date:
            try:
                base_dt = datetime.strptime(str(base_date), "%Y%m%d")
            except Exception:
                pass
                
        if ts_str:
            try:
                if len(str(ts_str)) == 14: # YYYYMMDDHHMMSS
                    timestamp = datetime.strptime(str(ts_str), "%Y%m%d%H%M%S")
                elif "T" in str(ts_str):
                    timestamp = datetime.fromisoformat(str(ts_str))
                else:
                    # 假设是 HH:MM:SS 或 HH:MM 格式
                    if len(str(ts_str)) == 5: # HH:MM
                        time_part = datetime.strptime(str(ts_str), "%H:%M")
                    else: # HH:MM:SS
                        time_part = datetime.strptime(str(ts_str), "%H:%M:%S")
                        
                    timestamp = base_dt.replace(hour=time_part.hour, minute=time_part.minute, second=time_part.second, microsecond=0)
            except Exception:
                pass
        
        return cls(
            timestamp=timestamp,
            price=float(data.get("price", 0)),
            volume=int(data.get("volume", 0)),
            amount=float(data.get("amount", 0)),
            type=str(data.get("type", "") or data.get("flag", ""))
        )


@dataclass
class FinanceInfo:
    """财务信息"""
    stock_code: str
    updated_date: Optional[str] = None
    eps: Optional[float] = None # 每股收益
    pe: Optional[float] = None  # 市盈率
    pb: Optional[float] = None  # 市净率
    total_shares: Optional[float] = None # 总股本
    float_shares: Optional[float] = None # 流通股本
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FinanceInfo':
        return cls(
            stock_code=data.get("code", ""),
            updated_date=data.get("updated_date") or data.get("date"),
            eps=float(data.get("eps", 0)) if data.get("eps") else None,
            pe=float(data.get("pe", 0)) if data.get("pe") else None,
            pb=float(data.get("pb", 0)) if data.get("pb") else None,
            total_shares=float(data.get("total_shares", 0)) if data.get("total_shares") else None,
            float_shares=float(data.get("float_shares", 0)) if data.get("float_shares") else None
        )

@dataclass
class RankingItem:
    """通用榜单项"""
    stock_code: str
    stock_name: str
    value: float # 榜单核心值（涨幅、成交额等）
    change_rate: Optional[float] = None # 涨跌幅
    price: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RankingItem':
        # 尝试适配多种榜单格式
        return cls(
            stock_code=data.get("code") or data.get("symbol", ""),
            stock_name=data.get("name") or data.get("stock_name", ""),
            value=float(data.get("value") or data.get("rate") or data.get("amount") or 0),
            change_rate=float(data.get("change_percent") or data.get("rate", 0)),
            price=float(data.get("price") or data.get("current_price", 0))
        )
