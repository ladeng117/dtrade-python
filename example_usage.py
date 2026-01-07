"""
DTrader API 全面使用示例
演示 dtrade 库的所有功能接口
"""

import sys
import time
from datetime import datetime, timedelta

# 确保能导入 dtrade (如果未安装到 site-packages)
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dtrade import DTraderClient
from dtrade.models import OrderType, OrderState

def print_header(title):
    print(f"\n{'='*20} {title} {'='*20}")

def print_sub_header(title):
    print(f"\n--- {title} ---")

def main():
    print("=== DTrader API 全面功能展示 ===")
    
    # 1. 初始化客户端
    print_header("1. 初始化客户端")
    try:
        client = DTraderClient(
            host="127.0.0.1",
            port=6756,
            api_key="4131991",
            timeout=30
        )
        print(f"✅ 客户端初始化成功: {client}")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        return

    # 定义测试用的股票代码
    TEST_STOCK = "000001"  # 平安银行
    TEST_INDEX = "sh000001" # 上证指数

    # ==========================================
    # 市场模块 (Market API)
    # ==========================================
    print_header("2. 市场模块 (Market API)")

    try:
        # 2.1 基础行情
        print_sub_header("基础行情")
        
        # get_snapshot (单只)
        snapshots = client.market.get_snapshot(TEST_STOCK)
        if snapshots:
            s = snapshots[0]
            print(f"get_snapshot({TEST_STOCK}): 价格 {s.price}, 涨跌幅 {s.change_percent}%, 成交量 {s.volume}")
        
        # get_snapshot (批量)
        snapshots = client.market.get_snapshot(["000001", "000002", "600000"])
        print(f"get_snapshot(批量): 获取到 {len(snapshots)} 个股票快照")
        if snapshots:
            print(f"  最新快照时间: {snapshots[0].timestamp if hasattr(snapshots[0], 'timestamp') else 'N/A'}")

        # 2.2 K线数据
        print_sub_header("K线数据")
        
        # get_kline_data
        klines = client.market.get_kline_data(TEST_STOCK, "1d", 5)
        print(f"get_kline_data(1d): 获取到 {len(klines)} 条日K线")
        if klines:
            print(f"  最新日K: 时间 {klines[-1].timestamp}, 收盘价 {klines[-1].close}")
        
        # get_today_kline
        klines = client.market.get_today_kline(TEST_STOCK)
        print(f"get_today_kline: 获取到 {len(klines)} 条今日分钟线")
        if klines:
            print(f"  最新分钟线: 时间 {klines[-1].timestamp}, 收盘价 {klines[-1].close}")
        
        # get_recent_kline
        klines = client.market.get_recent_kline(TEST_STOCK)
        print(f"get_recent_kline: 获取到 {len(klines)} 条近期K线")
        if klines:
            print(f"  最新K线: 时间 {klines[-1].timestamp}, 收盘价 {klines[-1].close}")

        # 2.3 分时与Tick
        print_sub_header("分时与Tick")
        
        # get_minute_data (今日)
        minutes = client.market.get_minute_data(TEST_STOCK)
        print(f"get_minute_data(今日): {len(minutes)} 条")
        if minutes:
            print(f"  最新分时: 时间 {minutes[-1].timestamp}, 价格 {minutes[-1].price}")
        
        # 计算昨天的日期 (简单处理，不考虑节假日)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        # get_minute_data (历史 - 昨天)
        minutes = client.market.get_minute_data(TEST_STOCK, date=yesterday)
        print(f"get_minute_data(历史-{yesterday}): {len(minutes)} 条")
        if minutes:
            print(f"  最新历史分时: 时间 {minutes[-1].timestamp}, 价格 {minutes[-1].price}")
        
        # get_tick_data (今日)
        ticks = client.market.get_tick_data(TEST_STOCK, count=20)
        print(f"get_tick_data(今日): {len(ticks)} 条")
        if ticks:
            print(f"  最新Tick: 时间 {ticks[-1].timestamp}, 价格 {ticks[-1].price}")
        
        # get_tick_data (历史 - 昨天)
        ticks = client.market.get_tick_data(TEST_STOCK, count=20, date=yesterday)
        print(f"get_tick_data(历史-{yesterday}): {len(ticks)} 条")
        if ticks:
            print(f"  最新历史Tick: 时间 {ticks[-1].timestamp}, 价格 {ticks[-1].price}")

        # 2.4 指数数据
        print_sub_header("指数数据")
        
        # get_index_data
        idx_snap = client.market.get_index_data(TEST_INDEX)
        if idx_snap:
            print(f"get_index_data({TEST_INDEX}): {idx_snap.price} ({idx_snap.change_percent}%)")
            # 指数快照可能没有 timestamp 字段，或者在 extra 中，视具体模型定义而定
            
        # get_index_kline
        idx_klines = client.market.get_index_kline(TEST_INDEX, "1d", 5)
        print(f"get_index_kline: {len(idx_klines)} 条")
        if idx_klines:
            print(f"  最新指数K线: 时间 {idx_klines[-1].timestamp}, 收盘价 {idx_klines[-1].close}")
        
        # get_market_indices
        indices = client.market.get_market_indices()
        print(f"get_market_indices: {len(indices)} 个主要指数")

        # 2.5 榜单数据 (部分可能需要权限)
        print_sub_header("热门榜单")
        
        funcs = [
            ("get_hot_industry", client.market.get_hot_industry),
            ("get_hot_concept", client.market.get_hot_concept),
            ("get_hot_etf", client.market.get_hot_etf),
            ("get_stock_count", lambda: client.market.get_stock_count("sz")),
            ("get_stock_list", lambda: client.market.get_stock_list("sz", start=0)),
        ]
        
        for name, func in funcs:
            try:
                res = func()
                count = len(res) if isinstance(res, (list, dict)) else 1
                print(f"{name}: 获取到 {count} 条数据")
            except Exception as e:
                print(f"{name}: ⚠️ {e}")

        # 2.6 高级分析接口
        print_sub_header("高级分析接口")
        
        adv_funcs = [
            ("get_hot_stock", client.market.get_hot_stock),
            ("get_limit_up_info", client.market.get_limit_up_info),
            ("get_force_rising", client.market.get_force_rising),
            ("get_stock_fluctuation", client.market.get_stock_fluctuation),
            ("get_main_testing", client.market.get_main_testing),
            ("get_weak_strong", client.market.get_weak_strong),
            ("get_smart_buy", client.market.get_smart_buy),
            ("get_hot_event", client.market.get_hot_event),
            ("get_ths_hot_code", client.market.get_ths_hot_code),
        ]
        
        for name, func in adv_funcs:
            try:
                res = func()
                print(f"{name}: {len(res)} 条")
            except Exception as e:
                print(f"{name}: ⚠️ {e}")

        # 2.7 基本面数据
        print_sub_header("基本面数据")
        
        # get_finance_info
        fin = client.market.get_finance_info(TEST_STOCK)
        print(f"get_finance_info: EPS={fin.eps}, PE={fin.pe}")
        
        # get_dividend_info
        divs = client.market.get_dividend_info(TEST_STOCK)
        print(f"get_dividend_info: {len(divs)} 条分红记录")

        # 2.8 辅助功能
        print_sub_header("辅助功能")
        print(f"validate_stock_code('000001'): {client.market.validate_stock_code('000001')}")
        print(f"get_stock_with_retry: {client.market.get_stock_with_retry(TEST_STOCK).price}")

    except Exception as e:
        print(f"❌ 市场模块测试出错: {e}")

    # ==========================================
    # 交易模块 (Trading API)
    # ==========================================
    print_header("3. 交易模块 (Trading API)")
    
    try:
        # 3.1 账户与持仓
        print_sub_header("账户与持仓")
        
        # get_account_info
        acct = client.trading.get_account_info()
        print(f"get_account_info: 总资产 {acct.total_assets}, 可用 {acct.available_cash}")
        
        # get_balance
        bal = client.trading.get_balance()
        print(f"get_balance: {bal}")
        
        # get_positions
        positions = client.trading.get_positions()
        print(f"get_positions: {len(positions)} 个持仓")
        if positions:
            p = positions[0]
            print(f"  首个持仓: {p.stock_code}, {p.volume}股")
            
            # get_position
            p_spec = client.trading.get_position(p.stock_code)
            print(f"get_position({p.stock_code}): 成功" if p_spec else "失败")

        # 3.2 订单查询
        print_sub_header("订单查询")
        
        # get_all_orders
        orders = client.trading.get_all_orders()
        print(f"get_all_orders: {len(orders)} 个订单")
        if orders:
            # get_order
            oid = orders[0].order_id
            o = client.trading.get_order(oid)
            print(f"get_order({oid}): {o.stock_code} {o.order_type.value} {o.order_state.value}")

        # 3.3 交易操作 (示例代码，默认不执行以免误操作)
        print_sub_header("交易操作 (示例)")
        
        print("注意：以下交易代码默认注释，请在确认环境安全后取消注释测试")
        
        # 单笔买入
        res = client.trading.buy("000001", 1.0, 100)
        print(f"buy: {res.success}, msg={res.message}, id={res.order_id}")
        
         #单笔卖出
        #res = client.trading.sell("000001", 15.0, 100)
        #print(f"sell: {res.success}, msg={res.message}, id={res.order_id}")
        
         #撤单
        if orders:
            res = client.trading.cancel_order(orders[0].order_id)
            print(f"cancel_order: {res.success}, msg={res.message}")
        
        # 批量买入
        batch_orders = [
             {"stock_code": "000001", "price": 1.0, "volume": 100},
             {"stock_code": "000002", "price": 1.0, "volume": 100}
         ]
        results = client.trading.batch_buy(batch_orders)
        print(f"batch_buy: 提交 {len(results)} 笔")
        for i, res in enumerate(results):
            code = batch_orders[i]["stock_code"]
            status = "✅" if res.success else "❌"
            msg = f"ID: {res.order_id}" if res.success else f"Error: {res.message}"
            print(f"  {status} [{code}] {msg}")
        
         #批量卖出
        batch_sell_orders = [
            {"stock_code": "000001", "price": 15.0, "volume": 100}
         ]
        results = client.trading.batch_sell(batch_sell_orders)
        print(f"batch_sell: 提交 {len(results)} 笔")
        for i, res in enumerate(results):
            code = batch_sell_orders[i]["stock_code"]
            status = "✅" if res.success else "❌"
            msg = f"ID: {res.order_id}" if res.success else f"Error: {res.message}"
            print(f"  {status} [{code}] {msg}")

    except Exception as e:
        print(f"❌ 交易模块测试出错: {e}")

    # 4. 清理资源
    print_header("4. 清理资源")
    client.close()
    print("✅ 客户端已关闭")

if __name__ == "__main__":
    main()
