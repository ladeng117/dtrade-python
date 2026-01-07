#!/usr/bin/env python3
"""
实时行情调试脚本 - 全面测试市场和交易模块所有函数
用于调试和验证API功能，验证异常处理和中文提示
"""

import sys
import time
import traceback
from datetime import datetime

# 添加 dtrade 包路径
sys.path.append('g:\\BaiduNetdiskDownload\\a股日内\\fengzhuangbao\\absolute\\path\\to\\dtrade')

from dtrade import DTraderClient
from dtrade.models import OrderState
from dtrade.exceptions import ValidationError, TradingError

# 测试股票代码
TEST_STOCKS = [
    "000001", "000002", "600000", "600858", # 常用
    "600519", "300750", "002594", "601127", "300059" # 热门
]

def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"【{title}】")
    print(f"{'='*60}")

def print_error(func_name, error):
    """统一错误打印格式"""
    print(f"❌ {func_name} 失败: {error}")
    print(f"   错误类型: {type(error).__name__}")
    if hasattr(error, 'error_code'):
        print(f"   错误代码: {error.error_code}")

def debug_raw_response(client, url):
    """调试辅助函数：打印原始API响应"""
    print(f"   🔍 [DEBUG] 请求原始数据: {url}")
    try:
        response = client.get(url)
        data = response.get("data")
        print(f"   🔍 [DEBUG] Data 类型: {type(data)}")
        if isinstance(data, list):
            print(f"   🔍 [DEBUG] 列表长度: {len(data)}")
            if data:
                print(f"   🔍 [DEBUG] 第一项类型: {type(data[0])}")
                print(f"   🔍 [DEBUG] 第一项内容: {data[0]}")
            else:
                print(f"   🔍 [DEBUG] 列表为空")
        else:
            print(f"   🔍 [DEBUG] Data 内容: {data}")
    except Exception as e:
        print(f"   ❌ [DEBUG] 获取原始数据失败: {e}")

def test_market_functions(client):
    """测试市场数据模块所有函数"""
    print_section("市场数据模块测试")
    
    # 1. get_snapshot (单只股票)
    print("\n1. 测试 get_snapshot() - 单只股票...")
    for code in TEST_STOCKS[:2]:
        try:
            snapshots = client.market.get_snapshot(code)
            if snapshots:
                snapshot = snapshots[0]
                print(f"✅ {code}: 当前价 {snapshot.price:.2f}, 涨跌幅 {snapshot.change_percent:.2f}%")
            else:
                print(f"⚠️ {code}: 未获取到快照数据")
        except Exception as e:
            print_error(f"get_snapshot({code})", e)
    
    # 2. get_snapshot (批量)
    print("\n2. 测试 get_snapshot() - 批量获取...")
    try:
        snapshots = client.market.get_snapshot(TEST_STOCKS[:3])
        print(f"✅ 成功获取 {len(snapshots)} 个股票快照")
    except Exception as e:
        print_error("get_snapshot(batch)", e)
    
    # 3. get_kline_data (通用K线)
    print("\n3. 测试 get_kline_data()...")
    try:
        klines = client.market.get_kline_data("000001", "1d", 5)
        print(f"✅ 获取到 {len(klines)} 条日K线数据")
        if klines:
            print(f"   最新: {klines[-1].timestamp} 收盘: {klines[-1].close}")
    except Exception as e:
        print_error("get_kline_data", e)

    # 4. get_today_kline (今日K线)
    print("\n4. 测试 get_today_kline()...")
    try:
        klines = client.market.get_today_kline("000001")
        print(f"✅ 获取到 {len(klines)} 条今日分钟线")
        if klines:
            print(f"   最新: {klines[-1].timestamp} 收盘: {klines[-1].close}")
    except Exception as e:
        print_error("get_today_kline", e)

    # 5. get_recent_kline (近期K线)
    print("\n5. 测试 get_recent_kline()...")
    try:
        klines = client.market.get_recent_kline("000001", days=10)
        print(f"✅ 获取到 {len(klines)} 条近期日K线")
    except Exception as e:
        print_error("get_recent_kline", e)

    # 6. validate_stock_code (验证代码)
    print("\n6. 测试 validate_stock_code()...")
    valid_code = "000001"
    invalid_code = "abc"
    print(f"   验证 {valid_code}: {client.market.validate_stock_code(valid_code)}")
    print(f"   验证 {invalid_code}: {client.market.validate_stock_code(invalid_code)}")
    if client.market.validate_stock_code(valid_code) and not client.market.validate_stock_code(invalid_code):
        print("✅ 股票代码验证逻辑正确")
    else:
        print("❌ 股票代码验证逻辑异常")

    # 7. get_stock_with_retry (重试机制)
    print("\n7. 测试 get_stock_with_retry()...")
    try:
        snap = client.market.get_stock_with_retry("000001", max_retries=2)
        if snap:
            print(f"✅ 重试获取成功: {snap.price}")
        else:
            print("⚠️ 重试获取返回 None")
    except Exception as e:
        print_error("get_stock_with_retry", e)

    # 8. 测试新实现的榜单和基础接口
    print("\n8. 测试榜单和基础接口...")
    
    def run_subtest(name, func, *args, **kwargs):
        print(f"   测试 {name}...")
        try:
            result = func(*args, **kwargs)
            if isinstance(result, (list, dict)):
                count = len(result)
                print(f"   ✅ 获取到 {count} 条数据")
            else:
                print(f"   ✅ 获取成功: {result}")
        except Exception as e:
            print(f"   ⚠️ 获取失败: {e}")

    # 8.1 热门行业
    run_subtest("热门行业 (get_hot_industry)", client.market.get_hot_industry)
    
    # 8.2 热门概念
    run_subtest("热门概念 (get_hot_concept)", client.market.get_hot_concept)
    
    # 8.3 热门ETF
    run_subtest("热门ETF (get_hot_etf)", client.market.get_hot_etf)
    
    # 8.4 股票数量
    run_subtest("股票数量 (get_stock_count)", client.market.get_stock_count, "sz")
    
    # 8.5 股票列表
    run_subtest("股票列表 (get_stock_list)", client.market.get_stock_list, "sz", start=0)

    # 8.6 指数实时行情
    run_subtest("指数实时行情 (get_index_data) - 上证指数", client.market.get_index_data, "sh000001")

    # 8.9 指数K线
    run_subtest("指数K线 (get_index_kline) - 上证指数", client.market.get_index_kline, "sh000001")

    # 8.10 市场指数列表
    run_subtest("市场指数列表 (get_market_indices)", client.market.get_market_indices)

    # 8.11 分时数据 (今日 + 历史)
    run_subtest("分时数据 (今日) - 000001", client.market.get_minute_data, "000001")
    debug_raw_response(client, "/hq/minute/000001") # DEBUG
    
    run_subtest("分时数据 (历史 20240816) - 000001", client.market.get_minute_data, "000001", date="20240816")

    # 8.12 Tick数据 (今日 + 历史)
    run_subtest("Tick数据 (今日) - 000001", client.market.get_tick_data, "000001", 100)
    debug_raw_response(client, "/hq/tick/000001/100") # DEBUG
    
    run_subtest("Tick数据 (历史 20240806) - 000001", client.market.get_tick_data, "000001", 100, date="20240806")

    # 8.13 财务信息
    run_subtest("财务信息 (get_finance_info) - 000001", client.market.get_finance_info, "000001")

    # 8.14 分红信息
    run_subtest("分红信息 (get_dividend_info) - 000001", client.market.get_dividend_info, "000001")

    # 8.15 涨停分析
    run_subtest("涨停分析 (get_limit_up_info)", client.market.get_limit_up_info)

    # 8.16 个股热度
    run_subtest("个股热度 (get_hot_stock)", client.market.get_hot_stock)
    debug_raw_response(client, "/hq/ranking/hot-stock") # DEBUG

    # 8.17 同花顺热点代码
    run_subtest("同花顺热点代码 (get_ths_hot_code)", client.market.get_ths_hot_code)

    # 8.18 强势股
    run_subtest("强势股 (get_force_rising)", client.market.get_force_rising)
    debug_raw_response(client, "/hq/ranking/forse-rasing") # DEBUG

    # 8.19 异动股
    run_subtest("异动股 (get_stock_fluctuation)", client.market.get_stock_fluctuation)
    debug_raw_response(client, "/hq/ranking/stock-fluctuation") # DEBUG

    # 8.20 主力试盘
    run_subtest("主力试盘 (get_main_testing)", client.market.get_main_testing)

    # 8.21 强弱分析
    run_subtest("强弱分析 (get_weak_strong)", client.market.get_weak_strong)
    debug_raw_response(client, "/hq/ranking/weak-strong") # DEBUG

    # 8.22 智能买入
    run_subtest("智能买入 (get_smart_buy)", client.market.get_smart_buy)
    debug_raw_response(client, "/hq/ranking/smart-buy") # DEBUG
    
    # 8.23 热点事件
    run_subtest("热点事件 (get_hot_event)", client.market.get_hot_event)

    # 9. 异常测试：无效股票代码
    print("\n9. 异常测试 - 无效股票代码...")
    try:
        client.market.get_snapshot("")
    except ValidationError as e:
        print(f"✅ 捕获预期异常: {e}")
    except Exception as e:
        print_error("异常测试(无效代码)", e)

def test_trading_functions(client):
    """测试交易模块所有函数"""
    print_section("交易模块测试")
    
    # 1. 获取所有委托单
    print("\n1. 测试 get_all_orders()...")
    try:
        all_orders = client.trading.get_all_orders()
        print(f"✅ 获取到 {len(all_orders)} 个委托单")
    except Exception as e:
        print_error("get_all_orders", e)
    
    # 2. 按状态获取委托单
    print("\n2. 测试 get_all_orders() 按状态过滤...")
    for status in [OrderState.SUBMITTED, OrderState.FILLED, OrderState.CANCELLED]:
        try:
            orders = client.trading.get_all_orders(status=status.value)
            print(f"   ✅ {status.value}状态委托单: {len(orders)}个")
        except Exception as e:
            print_error(f"get_all_orders({status.value})", e)
    
    # 3. 获取账户信息
    print("\n3. 测试 get_account_info()...")
    try:
        account_info = client.trading.get_account_info()
        print(f"✅ 账户信息: 总资产 {account_info.total_assets}, 可用 {account_info.available_cash}")
    except Exception as e:
        print_error("get_account_info", e)
        
    # 3.1 测试 get_balance() (新增)
    print("\n3.1 测试 get_balance()...")
    try:
        balance = client.trading.get_balance()
        print(f"✅ 余额信息: {balance}")
    except Exception as e:
        print_error("get_balance", e)
    
    # 4. 获取持仓列表
    print("\n4. 测试 get_positions()...")
    try:
        positions = client.trading.get_positions()
        print(f"✅ 获取到 {len(positions)} 个持仓")
        for pos in positions[:2]:
            print(f"   {pos.stock_code}: {pos.volume}股, 盈亏 {pos.profit_loss}")
            
        # 4.1 测试 get_position() (新增)
        if positions:
            target_code = positions[0].stock_code
            print(f"\n4.1 测试 get_position({target_code})...")
            pos = client.trading.get_position(target_code)
            if pos:
                print(f"✅ 获取特定持仓成功: {pos.stock_code}, {pos.volume}股")
            else:
                print(f"❌ 获取特定持仓失败: {target_code}")
                
    except Exception as e:
        print_error("get_positions", e)
    
    # 5. 异常测试：买入参数验证
    print("\n5. 异常测试 - 买入参数验证...")
    try:
        client.trading.buy("000001", -10.0, 100)
    except ValidationError as e:
        print(f"✅ 捕获预期异常(价格负数): {e}")
    except Exception as e:
        print_error("异常测试(无效价格)", e)
        
    try:
        client.trading.buy("000001", 10.0, 50)
    except ValidationError as e:
        print(f"✅ 捕获预期异常(非100倍数): {e}")
    except Exception as e:
        print_error("异常测试(无效数量)", e)

def test_full_trade_flow(client, stock_code, volume):
    """测试完整交易流程：下单 -> 查询 -> 撤单"""
    print_section(f"完整交易流程测试: {stock_code}")
    
    # 1. 获取行情
    print(f"\n1. 获取 {stock_code} 行情...")
    buy_price = 0.0
    try:
        snapshots = client.market.get_snapshot(stock_code)
        if snapshots:
            snap = snapshots[0]
            if snap.ask_prices:
                buy_price = snap.ask_prices[0] # 卖一价
                print(f"   使用卖一价: {buy_price}")
            else:
                buy_price = snap.price
                print(f"   使用当前价: {buy_price}")
        else:
            print("⚠️ 未获取到行情")
    except Exception as e:
        print_error("获取行情", e)
    
    if buy_price == 0:
        buy_price = 10.0
        print(f"   使用默认价格: {buy_price}")
        
    # 2. 下单买入
    print(f"\n2. 下单买入 {stock_code}, 价格 {buy_price}, 数量 {volume}...")
    order_id = None
    try:
        result = client.trading.buy(stock_code, buy_price, volume)
        if result.success:
            order_id = result.order_id
            print(f"✅ 下单成功: {order_id}")
        else:
            print(f"❌ 下单失败: {result.message}")
            return
    except Exception as e:
        print_error("下单买入", e)
        return
        
    # 3. 查询订单
    print(f"\n3. 查询订单状态...")
    time.sleep(1)
    try:
        order = client.trading.get_order(order_id)
        if order:
            print(f"✅ 查询成功: {order.order_id} - {order.order_state.value}")
        else:
            # 尝试从列表查询
            all_orders = client.trading.get_all_orders()
            found = False
            for o in all_orders:
                if str(o.order_id) == str(order_id):
                    print(f"✅ 在列表中找到: {o.order_id} - {o.order_state.value}")
                    found = True
                    order = o
                    break
            if not found:
                print("❌ 未查询到订单")
    except Exception as e:
        print_error("查询订单", e)
        
    # 4. 撤单 (如果未成交)
    if order and order.order_state in [OrderState.SUBMITTED, OrderState.PARTIALLY_FILLED]:
        print(f"\n4. 撤销订单 {order_id}...")
        try:
            result = client.trading.cancel_order(order_id)
            if result.success:
                print("✅ 撤单请求发送成功")
            else:
                print(f"❌ 撤单失败: {result.message}")
        except Exception as e:
            print_error("撤销订单", e)
    else:
        print(f"\n4. 订单状态为 {order.order_state.value if order else 'None'}，跳过撤单")
        
    # 5. 测试单笔卖出 (如果有持仓)
    print("\n5. 测试单笔卖出 (尝试卖出 600858)...")
    try:
        # 使用极高价格卖出，确保只挂单不成交
        result = client.trading.sell("600858", 999.0, 100)
        if result.success:
            print(f"✅ 卖出挂单成功: {result.order_id}")
            # 立即撤单
            time.sleep(1)
            client.trading.cancel_order(result.order_id)
            print(f"✅ 卖出挂单已撤销: {result.order_id}")
        else:
            print(f"❌ 卖出失败: {result.message}")
    except Exception as e:
        print_error("单笔卖出", e)

def test_batch_trading(client):
    """测试批量交易功能"""
    print_section("批量交易功能测试")
    
    # 构造批量买单
    # 注意：使用较低的价格以避免成交（除非是测试目的），这里使用 600858 和 600000
    batch_orders = [
        {"stock_code": "600858", "price": 1.0, "volume": 100}, # 极低价格，应该挂单成功但不成交
        {"stock_code": "600000", "price": 1.0, "volume": 100},
        {"stock_code": "000001", "price": 1.0, "volume": 100}
    ]
    
    print(f"\n1. 批量买入 {len(batch_orders)} 笔订单...")
    try:
        results = client.trading.batch_buy(batch_orders)
        success_count = 0
        order_ids = []
        
        for i, res in enumerate(results):
            code = batch_orders[i]["stock_code"]
            if res.success:
                print(f"   ✅ {code}: 下单成功, ID: {res.order_id}")
                success_count += 1
                order_ids.append(res.order_id)
            else:
                print(f"   ❌ {code}: 下单失败, 原因: {res.message}")
        
        print(f"   成功 {success_count}/{len(batch_orders)}")
        
        # 清理批量订单
        if order_ids:
            print(f"\n2. 清理批量订单 (撤单)...")
            time.sleep(1) # 等待订单入库
            for oid in order_ids:
                try:
                    client.trading.cancel_order(oid)
                    print(f"   ✅ 撤单请求已发送: {oid}")
                except Exception as e:
                    print(f"   ❌ 撤单失败 {oid}: {e}")
                    
    except Exception as e:
        print_error("批量买入", e)

    # 批量卖出测试
    print(f"\n3. 批量卖出测试 (尝试高价卖出)...")
    batch_sell_orders = [
        {"stock_code": "600858", "price": 999.0, "volume": 100},
        {"stock_code": "603679", "price": 999.0, "volume": 100} # 假设有持仓
    ]
    try:
        results = client.trading.batch_sell(batch_sell_orders)
        order_ids = []
        for i, res in enumerate(results):
            code = batch_sell_orders[i]["stock_code"]
            if res.success:
                print(f"   ✅ {code}: 卖出挂单成功, ID: {res.order_id}")
                order_ids.append(res.order_id)
            else:
                print(f"   ❌ {code}: 卖出失败, 原因: {res.message}")
        
        # 清理
        if order_ids:
            print(f"   清理批量卖出订单...")
            time.sleep(1)
            for oid in order_ids:
                client.trading.cancel_order(oid)
                print(f"   ✅ 撤单: {oid}")
    except Exception as e:
        print_error("批量卖出", e)

def main():
    """主函数"""
    print("=== DTrader API 全面测试脚本 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 初始化客户端
    print("\n【初始化客户端】")
    try:
        client = DTraderClient(
            host="127.0.0.1",
            port=6756,
            api_key="4131991",
            timeout=30
        )
        print(f"✅ 客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        return
    
    try:
        # 2. 测试市场模块
        test_market_functions(client)
        
        # 3. 测试交易模块
        test_trading_functions(client)
        
        # 4. 测试完整交易流程 (使用 600858)
        test_full_trade_flow(client, "600858", 100)
        
        # 5. 测试批量交易
        test_batch_trading(client)
        
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中出现意外错误: {e}")
        traceback.print_exc()
    finally:
        client.close()
        print(f"\n【测试完成】")

if __name__ == "__main__":
    main()
