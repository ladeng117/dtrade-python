#!/usr/bin/env python3
"""
异常处理调试脚本 - 专门测试各种异常情况
用于验证异常处理机制的正确性
"""

import sys
import time
from datetime import datetime, timedelta

# 添加 dtrade 包路径
sys.path.append('g:\\BaiduNetdiskDownload\\a股日内\\fengzhuangbao\\absolute\\path\\to\\dtrade')

from dtrade import DTraderClient
from dtrade.models import OrderType, OrderState
from dtrade.exceptions import (
    DTraderError, ValidationError, APIError, TradingError, 
    MarketDataError, AuthenticationError, ConnectionError, TimeoutError,
    RateLimitError, InsufficientFundsError, OrderNotFoundError, InvalidOrderError
)

def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"【{title}】")
    print(f"{'='*60}")

def test_exception_hierarchy():
    """测试异常继承层次"""
    print_section("异常继承层次测试")
    
    # 创建各种异常实例
    exceptions = [
        DTraderError("基础错误"),
        ValidationError("验证错误", field="test_field"),
        APIError("API错误", status_code=500, api_code=1001),
        TradingError("交易错误"),
        MarketDataError("市场数据错误"),
        AuthenticationError("认证错误"),
        ConnectionError("连接错误"),
        TimeoutError("超时错误"),
        RateLimitError("速率限制错误"),
        InsufficientFundsError("资金不足错误"),
        OrderNotFoundError("订单未找到错误"),
        InvalidOrderError("无效订单错误")
    ]
    
    print("异常类型和继承关系:")
    for exc in exceptions:
        print(f"✅ {type(exc).__name__}: {exc}")
        if hasattr(exc, 'error_code'):
            print(f"   错误代码: {exc.error_code}")
        if hasattr(exc, 'field') and exc.field:
            print(f"   字段: {exc.field}")
        if hasattr(exc, 'status_code') and exc.status_code:
            print(f"   HTTP状态码: {exc.status_code}")
        if hasattr(exc, 'api_code') and exc.api_code:
            print(f"   API代码: {exc.api_code}")

def test_validation_errors():
    """测试验证错误"""
    print_section("验证错误测试")
    
    # 模拟各种验证错误场景
    test_cases = [
        ("空股票代码", ValidationError("股票代码不能为空", field="stock_code")),
        ("无效价格", ValidationError("价格必须大于0", field="price")),
        ("无效数量", ValidationError("数量必须是100的整数倍", field="volume")),
        ("日期格式错误", ValidationError("日期格式必须为YYYY-MM-DD", field="date")),
    ]
    
    for name, exc in test_cases:
        print(f"✅ {name}: {exc}")
        print(f"   字段: {exc.field}")

def test_api_errors():
    """测试API错误"""
    print_section("API错误测试")
    
    # 模拟各种API错误
    test_cases = [
        ("服务器错误", APIError("Internal server error", status_code=500)),
        ("认证失败", APIError("Authentication failed", status_code=401, api_code=401)),
        ("速率限制", APIError("Rate limit exceeded", status_code=429, api_code=429)),
        ("参数错误", APIError("Invalid parameters", status_code=400, api_code=1001)),
        ("数据不存在", APIError("Data not found", status_code=404, api_code=2001)),
    ]
    
    for name, exc in test_cases:
        print(f"✅ {name}: {exc}")
        if exc.status_code:
            print(f"   HTTP状态码: {exc.status_code}")
        if exc.api_code:
            print(f"   API代码: {exc.api_code}")

def test_trading_errors():
    """测试交易相关错误"""
    print_section("交易错误测试")
    
    # 模拟各种交易错误
    test_cases = [
        ("资金不足", InsufficientFundsError("账户可用资金不足")),
        ("订单未找到", OrderNotFoundError("订单12345不存在")),
        ("无效订单", InvalidOrderError("订单价格超出涨跌停限制")),
        ("交易时间错误", TradingError("非交易时间")),
        ("持仓不足", TradingError("可卖出持仓不足")),
    ]
    
    for name, exc in test_cases:
        print(f"✅ {name}: {exc}")
        if hasattr(exc, 'error_code'):
            print(f"   错误代码: {exc.error_code}")

def test_network_errors():
    """测试网络相关错误"""
    print_section("网络错误测试")
    
    # 模拟各种网络错误
    test_cases = [
        ("连接拒绝", ConnectionError("Connection refused by server")),
        ("连接超时", TimeoutError("Connection timeout after 30 seconds")),
        ("DNS解析失败", ConnectionError("Failed to resolve hostname")),
        ("网络不可达", ConnectionError("Network is unreachable")),
    ]
    
    for name, exc in test_cases:
        print(f"✅ {name}: {exc}")
        print(f"   错误代码: {exc.error_code}")

def test_error_propagation():
    """测试错误传播和包装"""
    print_section("错误传播测试")
    
    # 模拟底层错误被包装的情况
    try:
        try:
            # 模拟底层网络错误
            raise ConnectionError("原始连接错误")
        except ConnectionError as e:
            # 包装为市场数据错误
            raise MarketDataError(f"获取行情数据失败: {e}") from e
    except MarketDataError as e:
        print(f"✅ 错误包装成功: {e}")
        print(f"   原始错误: {e.__cause__}")
    
    # 测试多重包装
    try:
        try:
            raise TimeoutError("请求超时")
        except TimeoutError as e1:
            try:
                raise APIError(f"API调用失败: {e1}") from e1
            except APIError as e2:
                raise TradingError(f"交易操作失败: {e2}") from e2
    except TradingError as e:
        print(f"✅ 多重错误包装: {e}")
        print(f"   错误链: {type(e).__name__} -> {type(e.__cause__).__name__} -> {type(e.__cause__.__cause__).__name__}")

def test_error_formatting():
    """测试错误格式化输出"""
    print_section("错误格式化测试")
    
    # 测试不同错误的字符串表示
    errors = [
        ValidationError("字段验证失败", field="price"),
        APIError("API返回错误", status_code=500, api_code=1001),
        MarketDataError("获取K线数据失败"),
        TradingError("下单失败", error_code="ORDER_FAILED")
    ]
    
    print("不同错误的格式化输出:")
    for exc in errors:
        print(f"✅ {type(exc).__name__}: {exc}")

def test_real_world_exceptions():
    """测试真实环境下的异常触发"""
    print_section("真实环境异常测试")
    
    # 初始化客户端
    client = DTraderClient(
        host="127.0.0.1",
        port=6756,
        api_key="4131991", # 假设这是有效的 Key，如果无效会触发 AuthenticationError
        timeout=5
    )
    
    # 1. 测试无效的股票代码 (Market API)
    print("\n1. 测试无效股票代码 (get_snapshot)...")
    try:
        # 传入空字符串，预期触发 ValidationError
        client.market.get_snapshot("")
        print("❌ 未触发预期异常")
    except ValidationError as e:
        print(f"✅ 捕获 ValidationError: {e}")
    except Exception as e:
        print(f"⚠️ 捕获非预期异常: {type(e).__name__}: {e}")

    # 2. 测试无效的参数类型 (Market API)
    print("\n2. 测试无效参数类型 (get_kline_data)...")
    try:
        # 传入非法周期
        client.market.get_kline_data("000001", period="invalid_period")
        # 注意：如果服务端不校验，这里可能不会报错。取决于 SDK 是否做了本地校验。
        # 假设 SDK 没做严格本地校验，这里可能由服务端返回错误
        print("⚠️ 未触发异常 (可能 SDK 未在本地校验此参数)")
    except Exception as e:
        print(f"✅ 捕获异常: {type(e).__name__}: {e}")

    # 3. 测试交易参数验证 (Trading API)
    print("\n3. 测试交易参数验证 (buy)...")
    try:
        # 价格为负
        client.trading.buy("000001", -10.0, 100)
        print("❌ 未触发预期异常")
    except ValidationError as e:
        print(f"✅ 捕获 ValidationError (负价格): {e}")
    except Exception as e:
        print(f"⚠️ 捕获非预期异常: {type(e).__name__}: {e}")
        
    try:
        # 数量非 100 倍数
        client.trading.buy("000001", 10.0, 50)
        print("❌ 未触发预期异常")
    except ValidationError as e:
        print(f"✅ 捕获 ValidationError (非整手): {e}")
    except Exception as e:
        print(f"⚠️ 捕获非预期异常: {type(e).__name__}: {e}")

    # 4. 测试错误的 API Key (模拟)
    print("\n4. 测试错误的 API Key (需要重新初始化客户端)...")
    bad_client = DTraderClient(
        host="127.0.0.1",
        port=6756,
        api_key="wrong_key",
        timeout=5
    )
    try:
        # 尝试一个需要认证的操作，如查询账户
        bad_client.trading.get_account_info()
        print("⚠️ 未触发认证错误 (可能服务端未开启严格校验)")
    except AuthenticationError as e:
        print(f"✅ 捕获 AuthenticationError: {e}")
    except APIError as e:
        print(f"✅ 捕获 APIError (可能是认证失败): {e}")
        print(f"   Status: {e.status_code}, Code: {e.api_code}")
    except Exception as e:
        print(f"⚠️ 捕获其他异常: {type(e).__name__}: {e}")
    finally:
        bad_client.close()

    # 5. 测试连接超时 (连接到一个不可达的 IP，或者设置极短超时)
    print("\n5. 测试连接超时...")
    # 注意：连接不可达 IP 可能会很慢，这里尝试连接本地未开放端口
    bad_conn_client = DTraderClient(
        host="127.0.0.1",
        port=12345, # 假设此端口未开放
        api_key="test",
        timeout=1
    )
    try:
        bad_conn_client.market.get_snapshot("000001")
        print("❌ 未触发连接错误")
    except ConnectionError as e:
        print(f"✅ 捕获 ConnectionError: {e}")
    except Exception as e:
        print(f"✅ 捕获异常 (可能是底层 ConnectionRefusedError): {type(e).__name__}: {e}")
    finally:
        bad_conn_client.close()

    client.close()

def test_model_parsing_exceptions():
    """测试数据模型解析异常"""
    print_section("数据模型解析异常测试")
    
    from dtrade.models import MinuteData
    
    print("\n1. 测试 MinuteData 解析脏数据...")
    dirty_data = {"price": "invalid_float", "vol": 100}
    try:
        MinuteData.from_dict(dirty_data)
        print("❌ 未触发解析异常")
    except ValueError as e:
        print(f"✅ 捕获 ValueError: {e}")
    except Exception as e:
        print(f"✅ 捕获异常: {type(e).__name__}: {e}")

def main():
    """主函数"""
    print("=== DTrader 异常处理调试脚本 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 测试异常继承层次
        test_exception_hierarchy()
        
        # 2. 测试验证错误
        test_validation_errors()
        
        # 3. 测试API错误
        test_api_errors()
        
        # 4. 测试交易错误
        test_trading_errors()
        
        # 5. 测试网络错误
        test_network_errors()
        
        # 6. 测试错误传播
        test_error_propagation()
        
        # 7. 测试错误格式化
        test_error_formatting()
        
        # 8. 测试客户端错误处理 (模拟连接错误)
        # test_client_error_handling() # 已被集成到 test_real_world_exceptions 中
        
        # 9. 测试真实环境异常 (新增)
        test_real_world_exceptions()
        
        # 10. 测试模型解析异常 (新增)
        test_model_parsing_exceptions()
        
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中出现意外错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n【测试完成】")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()