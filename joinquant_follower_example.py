"""
JoinQuant 聚宽跟单机器人
用于监听本地跟单系统的信号，并调用 dtrade 自动下单

使用说明:
1. 确保 dtrade 服务已启动。
2. 确保聚宽跟单网页 (localhost:61333) 已运行。
3. **关键步骤**: 打开浏览器 F12 -> Network (网络)，点击网页上的“交易记录”或刷新页面，
   找到返回交易数据的那个请求 URL，填入下方的 `SIGNAL_API_URL`。
"""

import time
import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional

# 尝试导入 dtrade，如果未安装则提示
try:
    from dtrade import DTraderClient
    from dtrade.models import OrderType
    from dtrade.exceptions import TradingError
except ImportError:
    print("❌ 未找到 dtrade 包，请先安装: pip install dtrade-python")
    exit(1)

# ================= 配置区域 (请根据实际情况修改) =================

# 1. DTrader 配置
DTRADE_CONF = {
    "host": "127.0.0.1",
    "port": 6756,
    "api_key": "your_api_key", # 请修改为您的真实 Key
    "timeout": 10
}

# 2. 信号源配置
# 根据最新截图，正确的 API 地址是 /v2/transactions
SIGNAL_API_URL = "http://localhost:61333/v2/transactions" 
# 轮询间隔 (秒)
POLL_INTERVAL = 3

# ===============================================================

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("Follower")

class JoinQuantFollower:
    def __init__(self):
        self.client = None
        self.processed_signals = set() # 记录已处理的信号ID，防止重复
        
    def connect_dtrade(self):
        """连接交易柜台"""
        try:
            self.client = DTraderClient(**DTRADE_CONF)
            # 测试连接
            acct = self.client.trading.get_account_info()
            logger.info(f"✅ DTrader 连接成功! 可用资金: {acct.available_cash}")
            return True
        except Exception as e:
            logger.error(f"❌ DTrader 连接失败: {e}")
            return False

    def get_latest_signals(self) -> List[Dict]:
        """
        从网页接口获取信号
        """
        try:
            # 发送请求
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "http://localhost:61333/joinquant"
            }
            response = requests.get(SIGNAL_API_URL, headers=headers, timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"获取信号失败 HTTP {response.status_code}: {response.text[:100]}")
                return []

            # 解析 JSON
            try:
                data = response.json()
            except Exception:
                logger.warning(f"响应不是有效的 JSON: {response.text[:100]}")
                return []
            
            # === 调试：打印前两条数据，帮助确认字段名 ===
            # (确认数据结构后可注释掉)
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"🔍 收到数据示例 (前1条): {data[0]}")
            elif isinstance(data, dict):
                logger.info(f"🔍 收到数据示例: {str(data)[:200]}")

            # 提取信号列表
            # 常见的结构可能是 list, 或者 {"data": [...], "list": [...]}
            signals = []
            if isinstance(data, list):
                signals = data
            elif isinstance(data, dict):
                if "data" in data and isinstance(data["data"], list):
                    signals = data["data"]
                elif "list" in data and isinstance(data["list"], list):
                    signals = data["list"]
                elif "transactions" in data and isinstance(data["transactions"], list):
                    signals = data["transactions"]
            
            return signals

        except Exception as e:
            logger.error(f"获取/解析信号出错: {e}")
            return []

    def execute_trade(self, signal: Dict):
        """执行交易"""
        try:
            # === 字段映射 (关键) ===
            # 请根据实际信号字段名修改
            sig_id = signal.get("id") or signal.get("trade_id")
            stock_code = signal.get("code") or signal.get("symbol")
            action = signal.get("action") or signal.get("side") # "buy" / "sell"
            price = float(signal.get("price", 0))
            volume = int(signal.get("volume") or signal.get("amount", 0))
            
            if not (sig_id and stock_code and action and volume):
                logger.warning(f"⚠️ 信号字段不完整，跳过: {signal}")
                return

            # 检查是否已处理
            if sig_id in self.processed_signals:
                return

            logger.info(f"🔔 收到新信号: {action} {stock_code} 价格={price} 数量={volume}")

            # 调用 DTrader 下单
            result = None
            if action.lower() in ["buy", "long", "买入"]:
                # 如果价格为0，可能需要用市价或获取当前价，这里演示限价
                if price <= 0:
                    snap = self.client.market.get_snapshot(stock_code)
                    price = snap[0].price if snap else 0
                    logger.info(f"信号价格无效，使用最新价: {price}")

                result = self.client.trading.buy(stock_code, price, volume)

            elif action.lower() in ["sell", "short", "卖出"]:
                if price <= 0:
                    snap = self.client.market.get_snapshot(stock_code)
                    price = snap[0].price if snap else 0
                
                result = self.client.trading.sell(stock_code, price, volume)
            
            else:
                logger.warning(f"未知操作类型: {action}")
                return

            # 处理结果
            if result and result.success:
                logger.info(f"✅ 下单成功! 委托号: {result.order_id}")
                self.processed_signals.add(sig_id)
            else:
                logger.error(f"❌ 下单失败: {result.message if result else '未知错误'}")

        except Exception as e:
            logger.error(f"❌ 执行交易异常: {e}")

    def run(self):
        """主循环"""
        if not self.connect_dtrade():
            return

        logger.info(f"🚀 跟单机器人启动! 监听接口: {SIGNAL_API_URL}")
        logger.info("按 Ctrl+C 停止...")

        while True:
            try:
                signals = self.get_latest_signals()
                
                # 假设返回的是包含所有历史记录的列表
                # 我们只需要处理最新的，或者根据 ID 过滤
                for sig in signals:
                    self.execute_trade(sig)
                
                time.sleep(POLL_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("🛑 用户停止")
                break
            except Exception as e:
                logger.error(f"主循环错误: {e}")
                time.sleep(POLL_INTERVAL)
        
        if self.client:
            self.client.close()

if __name__ == "__main__":
    follower = JoinQuantFollower()
    follower.run()
