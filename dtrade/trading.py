"""
DTrader 交易 API
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import logging

from .models import Order, AccountInfo, Position, TradeResult, OrderType, OrderState
from .exceptions import (
    ValidationError, APIError, AuthenticationError, 
    TradingError, InsufficientFundsError, InvalidOrderError,
    OrderNotFoundError
)

logger = logging.getLogger(__name__)


class TradingAPI:
    """DTrader 交易 API 客户端"""
    
    def __init__(self, client):
        """
        初始化交易 API
        
        参数:
            client: DTrader 客户端实例
        """
        self.client = client
    
    def get_all_orders(self, status: Optional[str] = None) -> List[Order]:
        """
        获取所有委托单
        
        参数:
            status: 按委托单状态过滤（可选）
        
        返回:
            Order 对象列表
        """
        params = {}
        if status:
            params["status"] = status
        
        try:
            response = self.client.get("/orders/all", params=params)
        except Exception as e:
            raise TradingError(f"获取委托单失败: {e}")
        
        orders_data = response.get("data", [])
        
        # 确保 orders_data 是列表
        if orders_data is None:
            orders_data = []
        
        orders = []
        for order_data in orders_data:
            try:
                order = Order.from_dict(order_data)
                orders.append(order)
            except Exception as e:
                logger.warning(f"Failed to parse order data: {e}")
        
        return orders

    def get_order(self, order_id: str) -> Optional[Order]:
        """
        根据 ID 获取特定委托单
        
        参数:
            order_id: 委托单 ID
        
        返回:
            如果找到则返回 Order 对象，否则返回 None
        """
        if not order_id:
            raise ValidationError("委托单ID不能为空")
        
        try:
            response = self.client.get(f"/orders/{order_id}")
        except Exception as e:
            raise TradingError(f"获取委托单失败: {e}")
        
        order_data = response.get("data")
        
        if order_data:
            try:
                return Order.from_dict(order_data)
            except Exception as e:
                logger.error(f"Failed to parse order data: {e}")
                return None
        return None

    def buy(self, stock_code: str, price: float, volume: int) -> TradeResult:
        """
        买入股票
        
        参数:
            stock_code: 股票代码（例如 "000001"）
            price: 委托价格
            volume: 委托数量
        
        返回:
            TradeResult 对象
        """
        self._validate_trade_params(stock_code, price, volume)
        
        params = {
            "code": stock_code,
            "price": price,
            "volume": volume
        }
        
        logger.info(f"Buy order: {stock_code}, price: {price}, volume: {volume}")
        try:
            response = self.client.get("/orders/buy", params=params)
        except Exception as e:
            raise TradingError(f"买入委托失败: {e}")
        
        trade_result = TradeResult.from_dict(response)
        # 手动填充请求参数，因为API返回可能只包含订单ID
        if not trade_result.stock_code:
            trade_result.stock_code = stock_code
        if not trade_result.price:
            trade_result.price = price
        if not trade_result.volume:
            trade_result.volume = volume
        if not trade_result.status:
            trade_result.status = "submitted" # 假设成功提交后状态为 submitted
            
        return trade_result
        logger.info(f"Buy order result: {trade_result}")
        
        return trade_result

    def sell(self, stock_code: str, price: float, volume: int) -> TradeResult:
        """
        卖出股票
        
        参数:
            stock_code: 股票代码（例如 "000001"）
            price: 委托价格
            volume: 委托数量
        
        返回:
            TradeResult 对象
        """
        self._validate_trade_params(stock_code, price, volume)
        
        params = {
            "code": stock_code,
            "price": price,
            "volume": volume
        }
        
        logger.info(f"Sell order: {stock_code}, price: {price}, volume: {volume}")
        try:
            response = self.client.get("/orders/sell", params=params)
        except Exception as e:
            raise TradingError(f"卖出委托失败: {e}")
        
        trade_result = TradeResult.from_dict(response)
        # 手动填充请求参数
        if not trade_result.stock_code:
            trade_result.stock_code = stock_code
        if not trade_result.price:
            trade_result.price = price
        if not trade_result.volume:
            trade_result.volume = volume
        if not trade_result.status:
            trade_result.status = "submitted"
            
        return trade_result
        logger.info(f"Sell order result: {trade_result}")
        
        return trade_result

    def cancel_order(self, order_id: str) -> TradeResult:
        """
        撤销委托单
        
        参数:
            order_id: 要撤销的委托单 ID
        
        返回:
            TradeResult 对象
        """
        if not order_id:
            raise ValidationError("委托单ID不能为空", field="order_id")
        
        logger.info(f"Cancel order: {order_id}")
        try:
            response = self.client.get(f"/orders/cancel/{order_id}")
        except Exception as e:
            raise TradingError(f"撤销委托失败: {e}")
        
        trade_result = TradeResult.from_dict(response)
        logger.info(f"Cancel order result: {trade_result}")
        
        return trade_result

    def batch_buy(self, orders: List[Dict[str, Any]], max_workers: int = 5) -> List[TradeResult]:
        """
        批量买入股票
        
        参数:
            orders: 订单列表，每个订单是一个字典，包含 {"stock_code": str, "price": float, "volume": int}
            max_workers: 最大并发线程数 (默认: 5)
            
        返回:
            TradeResult 对象列表，顺序与输入 orders 一致
        """
        from concurrent.futures import ThreadPoolExecutor
        
        results = [None] * len(orders)
        
        def _execute_buy(index, order):
            try:
                stock_code = order.get("stock_code")
                price = order.get("price")
                volume = order.get("volume")
                
                # 简单参数检查
                if not stock_code or not price or not volume:
                    return TradeResult(
                        success=False, 
                        message=f"订单参数不完整: {order}",
                        stock_code=stock_code
                    )
                    
                return self.buy(stock_code, price, volume)
            except Exception as e:
                return TradeResult(
                    success=False, 
                    message=f"批量买入异常: {e}",
                    stock_code=order.get("stock_code")
                )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, order in enumerate(orders):
                futures.append(executor.submit(_execute_buy, i, order))
            
            # 收集结果，保持顺序（实际上 submit 返回的 future 顺序就是提交顺序，但为了保险起见，我们按顺序获取）
            for i, future in enumerate(futures):
                results[i] = future.result()
                
        return results

    def batch_sell(self, orders: List[Dict[str, Any]], max_workers: int = 5) -> List[TradeResult]:
        """
        批量卖出股票
        
        参数:
            orders: 订单列表，每个订单是一个字典，包含 {"stock_code": str, "price": float, "volume": int}
            max_workers: 最大并发线程数 (默认: 5)
            
        返回:
            TradeResult 对象列表，顺序与输入 orders 一致
        """
        from concurrent.futures import ThreadPoolExecutor
        
        results = [None] * len(orders)
        
        def _execute_sell(index, order):
            try:
                stock_code = order.get("stock_code")
                price = order.get("price")
                volume = order.get("volume")
                
                if not stock_code or not price or not volume:
                    return TradeResult(
                        success=False, 
                        message=f"订单参数不完整: {order}",
                        stock_code=stock_code
                    )
                    
                return self.sell(stock_code, price, volume)
            except Exception as e:
                return TradeResult(
                    success=False, 
                    message=f"批量卖出异常: {e}",
                    stock_code=order.get("stock_code")
                )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, order in enumerate(orders):
                futures.append(executor.submit(_execute_sell, i, order))
            
            for i, future in enumerate(futures):
                results[i] = future.result()
                
        return results


    def get_account_info(self) -> AccountInfo:
        """
        获取账户信息
        
        返回:
            AccountInfo 对象
        """
        try:
            response = self.client.get("/account")
        except Exception as e:
            raise TradingError(f"获取账户信息失败: {e}")
        
        account_data = response.get("data", {})
        
        try:
            return AccountInfo.from_dict(account_data)
        except Exception as e:
            logger.error(f"Failed to parse account info: {e}")
            raise APIError(f"解析账户信息失败: {e}")

    def get_positions(self) -> List[Position]:
        """
        Get all positions
        
        Returns:
            List[Position]: List of positions
        """
        try:
            response = self.client.get("/positions")
        except Exception as e:
            raise TradingError(f"获取持仓失败: {e}")
        
        positions_data = response.get("data", [])
        
        positions = []
        for position_data in positions_data:
            try:
                position = Position.from_dict(position_data)
                positions.append(position)
            except Exception as e:
                logger.warning(f"Failed to parse position data: {e}")
        
        return positions

    def __repr__(self) -> str:
        """返回 TradingAPI 的字符串表示"""
        return f"TradingAPI(client={type(self.client).__name__})"
    
    def get_position(self, stock_code: str) -> Optional[Position]:
        """
        根据股票代码获取特定持仓
        
        参数:
            stock_code: 股票代码
        
        返回:
            如果找到则返回 Position 对象，否则返回 None
        """
        if not stock_code:
            raise ValidationError("股票代码不能为空")
        
        positions = self.get_positions()
        for position in positions:
            if position.stock_code == stock_code:
                return position
        
        return None
    
    def get_balance(self) -> Dict[str, float]:
        """
        获取账户余额
        
        返回:
            包含余额信息的字典
        """
        account_info = self.get_account_info()
        return {
            "total_assets": account_info.total_assets,
            "available_cash": account_info.available_cash,
            "market_value": account_info.market_value,
            "frozen_cash": account_info.frozen_cash
        }
    
    def _validate_trade_params(self, stock_code: str, price: float, volume: int) -> None:
        """
        验证交易参数
        
        参数:
            stock_code: 股票代码
            price: 委托价格
            volume: 委托数量
        
        抛出:
            ValidationError: 如果任何参数无效
        """
        if not stock_code or not isinstance(stock_code, str):
            raise ValidationError("股票代码必须是非空字符串")
        
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValidationError("价格必须是正数")
        
        if not isinstance(volume, int) or volume <= 0:
            raise ValidationError("数量必须是正整数")
        
        # 基于 DTrader 要求的额外验证
        if len(stock_code) != 6:
            raise ValidationError("股票代码必须是6位字符")
        
        if volume % 100 != 0:
            raise ValidationError("数量必须是100的倍数")