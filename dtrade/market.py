"""
Market API for DTrader - 基础行情接口（不含 Level2）
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import logging

from .models import MarketSnapshot, KLineData, MinuteData, TickData, FinanceInfo, RankingItem
from .exceptions import ValidationError, APIError, MarketDataError

logger = logging.getLogger(__name__)


class MarketAPI:
    """Market API client for DTrader - 基础行情接口"""
    
    def __init__(self, client):
        """
        Initialize Market API
        
        Args:
            client: DTrader client instance
        """
        self.client = client
    
    def get_snapshot(self, stock_codes: Union[str, List[str]]) -> List[MarketSnapshot]:
        """
        获取五档快照数据
        
        Args:
            stock_codes: 股票代码或股票代码列表
        
        Returns:
            List of MarketSnapshot objects
        """
        if isinstance(stock_codes, list):
            codes = ",".join(stock_codes)
        else:
            codes = stock_codes
        
        if not codes:
            raise ValidationError("股票代码不能为空", field="stock_codes")
        
        try:
            response = self.client.get(f"/hq/realtime/{codes}")
        except Exception as e:
            raise MarketDataError(f"获取快照数据失败: {e}")
        
        data = response.get("data", {})
        
        snapshots = []
        if isinstance(data, dict):
            # 单个股票的情况
            try:
                snapshot = MarketSnapshot.from_dict(data)
                snapshots.append(snapshot)
            except Exception as e:
                logger.error(f"Failed to parse snapshot data: {e}")
        elif isinstance(data, list):
            # 多个股票的情况
            for item in data:
                try:
                    snapshot = MarketSnapshot.from_dict(item)
                    snapshots.append(snapshot)
                except Exception as e:
                    logger.warning(f"Failed to parse snapshot data: {e}")
        
        return snapshots

    def get_kline_data(
        self, 
        stock_code: str, 
        period: str = "1d", 
        count: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[KLineData]:
        """
        获取K线数据
        
        Args:
            stock_code: 股票代码
            period: K线周期 (1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M)
            count: 数据条数
            start_date: 开始日期 (YYYY-MM-DD) - 目前仅作为预留参数，API暂不支持
            end_date: 结束日期 (YYYY-MM-DD) - 目前仅作为预留参数，API暂不支持
        
        Returns:
            List of KLineData objects
        """
        if not stock_code:
            raise ValidationError("股票代码不能为空", field="stock_code")
        
        # 映射周期参数
        period_mapping = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "1h": "1hour",
            "1d": "daily",
            "1w": "weekly",
            "1M": "monthly"
        }
        api_period = period_mapping.get(period, period)
        
        # 构建路径参数 URL: /hq/kline/{code}/{period}/{count}
        url = f"/hq/kline/{stock_code}/{api_period}/{count}"
        
        params = {}
        # 注意：API文档仅提及 start 参数作为索引，未提及日期过滤
        # 如果需要支持分页，可以使用 params['start'] = 0
        
        try:
            response = self.client.get(url, params=params)
        except Exception as e:
            raise MarketDataError(f"获取K线数据失败: {e}")
        
        data = response.get("data", [])
        
        # 处理可能的嵌套结构 {"count": 100, "list": [...]}
        kline_data = []
        if isinstance(data, dict):
            if "list" in data:
                kline_data = data["list"]
            elif "data" in data: # 有些API可能嵌套 data.data
                kline_data = data["data"]
            else:
                # 尝试直接把 dict 当作列表的一个元素（不太可能，通常是列表）
                pass
        elif isinstance(data, list):
            kline_data = data
            
        klines = []
        for item in kline_data:
            try:
                kline = KLineData.from_dict(item)
                klines.append(kline)
            except Exception as e:
                logger.warning(f"Failed to parse kline data: {e}, item: {item}")
        
        return klines

    def get_today_kline(self, stock_code: str, period: str = "1m", count: int = 100) -> List[KLineData]:
        """
        获取今日K线数据
        
        Args:
            stock_code: 股票代码
            period: K线周期 (默认: 1m)
            count: 数据条数 (默认: 100)
        
        Returns:
            List of KLineData objects
        """
        return self.get_kline_data(stock_code, period, count)
    
    def get_recent_kline(self, stock_code: str, period: str = "1d", days: int = 30) -> List[KLineData]:
        """
        获取近期K线数据
        
        Args:
            stock_code: 股票代码
            period: K线周期 (默认: 1d)
            days: 天数 (默认: 30)
        
        Returns:
            List of KLineData objects
        """
        return self.get_kline_data(stock_code, period, count=100)

    # 以下方法在当前 API 版本中可能不支持，保留占位符或注释掉
            
    def get_hot_industry(self) -> List[Dict[str, Any]]:
        """获取热门行业"""
        try:
            response = self.client.get("/hq/ranking/hot-industry")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取热门行业失败: {e}")
            
    def get_hot_concept(self) -> List[Dict[str, Any]]:
        """获取热门概念"""
        try:
            response = self.client.get("/hq/ranking/hot-concept")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取热门概念失败: {e}")
            
    def get_hot_etf(self) -> List[Dict[str, Any]]:
        """获取热门ETF"""
        try:
            response = self.client.get("/hq/ranking/hot-etf")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取热门ETF失败: {e}")

    def get_index_data(self, index_code: str) -> Optional[MarketSnapshot]:
        """
        获取指数实时行情
        
        Args:
            index_code: 指数代码 (e.g. "sh000001")
            
        Returns:
            MarketSnapshot object
        """
        snapshots = self.get_snapshot(index_code)
        return snapshots[0] if snapshots else None

    def get_index_kline(self, index_code: str, period: str = "1d", count: int = 100) -> List[KLineData]:
        """
        获取指数K线数据
        
        Args:
            index_code: 指数代码
            period: 周期 (1m, 5m, 15m, 30m, 1h, 1d...)
            count: 数量
        """
        # 映射周期参数
        period_mapping = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "1h": "1hour",
            "1d": "daily",
            "1w": "weekly",
            "1M": "monthly"
        }
        api_period = period_mapping.get(period, period)
        
        url = f"/hq/ikline/{index_code}/{api_period}/{count}"
        
        try:
            response = self.client.get(url)
            data = response.get("data", [])
            
            klines = []
            if isinstance(data, list):
                for item in data:
                    try:
                        klines.append(KLineData.from_dict(item))
                    except Exception as e:
                        logger.warning(f"Failed to parse index kline: {e}")
            return klines
        except Exception as e:
            raise MarketDataError(f"获取指数K线失败: {e}")

    def get_market_indices(self) -> List[Dict[str, Any]]:
        """
        获取主要市场指数列表 (尝试探测)
        """
        # 尝试使用 stocklist 接口获取指数，市场代码假设为 "index" 或 "sh" 的前几条
        # 这里硬编码一些常用指数作为备选，或者尝试探测接口
        common_indices = ["sh000001", "sz399001", "sz399006", "sh000300", "sh000905"]
        try:
            snapshots = self.get_snapshot(common_indices)
            return [
                {"code": s.symbol, "name": "", "price": s.price, "change": s.change_percent}
                for s in snapshots
            ]
        except Exception as e:
            raise MarketDataError(f"获取市场指数失败: {e}")

    # 榜单接口保留，但注明可能需要权限
    def get_rising_rate_ranking(self) -> List[Dict[str, Any]]:
        """获取涨幅榜 (可能需要 Level-2 权限)"""
        try:
            response = self.client.get("/hq/ranking/rising-rate")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取涨幅榜失败: {e}")

    def get_falling_rate_ranking(self) -> List[Dict[str, Any]]:
        """获取跌幅榜 (可能需要 Level-2 权限)"""
        try:
            response = self.client.get("/hq/ranking/falling-rate")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取跌幅榜失败: {e}")

    def get_turnover_ranking(self) -> List[Dict[str, Any]]:
        """获取换手率榜 (可能需要 Level-2 权限)"""
        try:
            response = self.client.get("/hq/ranking/rising-turnover")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取换手率榜失败: {e}")
            
    # 其他榜单接口同理...
    
    def get_rising_speed_ranking(self) -> List[Dict[str, Any]]:
        """获取涨速榜"""
        try:
            response = self.client.get("/hq/ranking/rising-speed")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取涨速榜失败: {e}")

    def get_falling_speed_ranking(self) -> List[Dict[str, Any]]:
        """获取跌速榜"""
        try:
            response = self.client.get("/hq/ranking/falling-speed")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取跌速榜失败: {e}")

    def get_main_inflow_ranking(self) -> List[Dict[str, Any]]:
        """获取主力流入榜"""
        try:
            response = self.client.get("/hq/ranking/rising-main")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取主力流入榜失败: {e}")

    def get_main_outflow_ranking(self) -> List[Dict[str, Any]]:
        """获取主力流出榜"""
        try:
            response = self.client.get("/hq/ranking/falling-main")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取主力流出榜失败: {e}")

    def get_minute_data(self, stock_code: str, date: Optional[str] = None) -> List[MinuteData]:
        """
        获取分时数据
        """
        try:
            if date:
                url = f"/hq/minute/{stock_code}/{date}"
            else:
                url = f"/hq/minute/{stock_code}"
            response = self.client.get(url)
            data = response.get("data", [])
            
            # 适配可能返回 dict 的情况
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                # 尝试查找列表字段
                if "data" in data and isinstance(data["data"], list):
                    items = data["data"]
                elif "list" in data and isinstance(data["list"], list):
                    items = data["list"]
                # 某些情况下 data 本身就是包含元数据的字典，无法直接转列表，保持 items 为空
            
            result = []
            for i, item in enumerate(items):
                if isinstance(item, dict):
                    try:
                        result.append(MinuteData.from_dict(item, base_date=date, index=i))
                    except Exception as e:
                        logger.warning(f"Failed to parse minute data item: {e}")
            return result
        except Exception as e:
            raise MarketDataError(f"获取分时数据失败: {e}")

    def get_tick_data(self, stock_code: str, count: int = 100, date: Optional[str] = None) -> List[TickData]:
        """
        获取Tick数据
        
        Args:
            stock_code: 股票代码
            count: 数量
            date: 日期 (YYYYMMDD), 默认为今日
        """
        try:
            if date:
                url = f"/hq/tick/{stock_code}/{count}/{date}"
            else:
                url = f"/hq/tick/{stock_code}/{count}"
            response = self.client.get(url)
            data = response.get("data", [])
            
            # 适配可能返回 dict 的情况
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                if "data" in data and isinstance(data["data"], list):
                    items = data["data"]
                elif "list" in data and isinstance(data["list"], list):
                    items = data["list"]
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    try:
                        result.append(TickData.from_dict(item, base_date=date))
                    except Exception as e:
                        logger.warning(f"Failed to parse tick data item: {e}")
            return result
        except Exception as e:
            raise MarketDataError(f"获取Tick数据失败: {e}")

    def get_finance_info(self, stock_code: str) -> FinanceInfo:
        """获取财务信息"""
        try:
            response = self.client.get(f"/hq/finance/{stock_code}")
            data = response.get("data", {})
            if not isinstance(data, dict):
                data = {}
            return FinanceInfo.from_dict(data)
        except Exception as e:
            raise MarketDataError(f"获取财务信息失败: {e}")

    def get_dividend_info(self, stock_code: str) -> List[Dict[str, Any]]:
        """获取分红信息 (结构较复杂，暂保持字典返回)"""
        try:
            response = self.client.get(f"/hq/dividend/{stock_code}")
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取分红信息失败: {e}")

    def get_limit_up_info(self) -> List[RankingItem]:
        """获取涨停分析"""
        try:
            response = self.client.get("/hq/ranking/limit-up-info")
            data = response.get("data", [])
            
            result = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取涨停分析失败: {e}")

    def get_hot_stock(self) -> List[RankingItem]:
        """获取个股热度"""
        try:
            response = self.client.get("/hq/ranking/hot-stock")
            data = response.get("data", {})
            
            # 适配 {'rankings': [...]} 结构
            if isinstance(data, dict) and "rankings" in data:
                items = data["rankings"]
            elif isinstance(data, list):
                items = data
            else:
                items = []
                
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取个股热度失败: {e}")
            
    def get_ths_hot_code(self) -> List[RankingItem]:
        """获取同花顺热点代码"""
        try:
            response = self.client.get("/hq/ranking/ths-hot-code")
            data = response.get("data", [])
            
            # 这里的 data 通常直接是列表
            items = data if isinstance(data, list) else []
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取同花顺热点代码失败: {e}")

    # 以下接口名称基于 URL 推断，可能需要 Level-2 权限
    def get_force_rising(self) -> List[RankingItem]:
        """获取强势股 (可能需要权限)"""
        try:
            response = self.client.get("/hq/ranking/forse-rasing")
            data = response.get("data", {})
            
            # 适配 {'data': [...]} 结构
            if isinstance(data, dict) and "data" in data:
                items = data["data"]
            elif isinstance(data, list):
                items = data
            else:
                items = []
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取强势股失败: {e}")

    def get_stock_fluctuation(self) -> List[RankingItem]:
        """获取异动股 (可能需要权限)"""
        try:
            response = self.client.get("/hq/ranking/stock-fluctuation")
            data = response.get("data", {})
            
            # 适配 {'rankings': [...]} 结构
            if isinstance(data, dict) and "rankings" in data:
                items = data["rankings"]
            elif isinstance(data, list):
                items = data
            else:
                items = []
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取异动股失败: {e}")
            
    def get_main_testing(self) -> List[RankingItem]:
        """获取主力试盘 (可能需要权限)"""
        try:
            response = self.client.get("/hq/ranking/main-testing")
            data = response.get("data", [])
            
            # 这里的 data 通常直接是列表
            items = data if isinstance(data, list) else []
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取主力试盘失败: {e}")
            
    def get_weak_strong(self) -> List[RankingItem]:
        """获取强弱分析 (可能需要权限)"""
        try:
            response = self.client.get("/hq/ranking/weak-strong")
            data = response.get("data", {})
            
            # 适配 {'weak_strong': [...]} 结构
            if isinstance(data, dict) and "weak_strong" in data:
                items = data["weak_strong"]
            elif isinstance(data, list):
                items = data
            else:
                items = []
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取强弱分析失败: {e}")
            
    def get_smart_buy(self) -> List[RankingItem]:
        """获取智能买入 (可能需要权限)"""
        try:
            response = self.client.get("/hq/ranking/smart-buy")
            data = response.get("data", {})
            
            # 适配 {'smart_buys': [...]} 结构
            if isinstance(data, dict) and "smart_buys" in data:
                items = data["smart_buys"]
            elif isinstance(data, list):
                items = data
            else:
                items = []
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取智能买入失败: {e}")
            
    def get_hot_event(self) -> List[RankingItem]:
        """获取热点事件 (可能需要权限)"""
        try:
            response = self.client.get("/hq/ranking/hot-event")
            data = response.get("data", [])
            
            result = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        result.append(RankingItem.from_dict(item))
            return result
        except Exception as e:
            raise MarketDataError(f"获取热点事件失败: {e}")


    def get_stock_count(self, market: str = "sz") -> Dict[str, Any]:
        """获取股票数量"""
        try:
            response = self.client.get(f"/hq/stockcount/{market}")
            return response.get("data", {})
        except Exception as e:
            raise MarketDataError(f"获取股票数量失败: {e}")
            
    # 热门行业等接口保持不变 (因为它们测试通过了)


    def get_stock_list(self, market: str = "sz", start: int = 0) -> List[Dict[str, Any]]:
        """获取股票列表"""
        try:
            response = self.client.get(f"/hq/stocklist/{market}", params={"start": start})
            return response.get("data", [])
        except Exception as e:
            raise MarketDataError(f"获取股票列表失败: {e}")

    def validate_stock_code(self, stock_code: str) -> bool:
        """
        验证股票代码格式
        
        Args:
            stock_code: 股票代码
        
        Returns:
            True if valid, False otherwise
        """
        if not stock_code:
            return False
        
        # 简单验证：6位数字
        if len(stock_code) != 6:
            return False
        
        if not stock_code.isdigit():
            return False
        
        return True
    
    def get_stock_with_retry(self, stock_code: str, max_retries: int = 3) -> Optional[MarketSnapshot]:
        """
        获取股票快照数据（带重试机制）
        
        Args:
            stock_code: 股票代码
            max_retries: 最大重试次数
        
        Returns:
            MarketSnapshot or None if failed
        """
        for attempt in range(max_retries):
            try:
                snapshots = self.get_snapshot([stock_code])
                if snapshots:
                    return snapshots[0]
                
                logger.warning(f"No snapshot data for {stock_code}, attempt {attempt + 1}/{max_retries}")
                
            except Exception as e:
                logger.error(f"Error getting snapshot for {stock_code}, attempt {attempt + 1}/{max_retries}: {e}")
                
                if attempt == max_retries - 1:
                    raise
                
                import time
                time.sleep(1 * (attempt + 1))
        
        return None
    
    def __repr__(self) -> str:
        """Return string representation of MarketAPI"""
        return f"<MarketAPI client={self.client}>"
