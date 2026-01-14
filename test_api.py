import requests
import json
import os
import tempfile
import time

# API基础URL
BASE_URL = "http://localhost:5000"

def test_home():
    """测试主页功能"""
    print("测试主页功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    print("-" * 50)


def test_load_netlist(tool_name, file_path):
    """测试读取网表功能"""
    print(f"测试{tool_name}的读取网表功能...")
    
    try:
        response = requests.post(f"{BASE_URL}/{tool_name}/load_netlist", 
                                json={"file_path": file_path})
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2)}")
        
        # 验证响应格式
        response_data = response.json()
        if 'code' in response_data and 'message' in response_data:
            print("✓ 响应格式正确，包含code和message字段")
        else:
            print("✗ 响应格式不正确")
    except Exception as e:
        print(f"错误: {e}")
    
    print("-" * 50)


def test_get_timing(tool_name):
    """测试获取时序信息功能"""
    print(f"测试{tool_name}的获取时序信息功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/{tool_name}/get_timing")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2)}")
        
        # 验证响应格式
        response_data = response.json()
        if 'code' in response_data and 'message' in response_data:
            print("✓ 响应格式正确，包含code和message字段")
        else:
            print("✗ 响应格式不正确")
    except Exception as e:
        print(f"错误: {e}")
    
    print("-" * 50)


def test_execute_tcl(tool_name, command):
    """测试执行TCL命令功能"""
    print(f"测试{tool_name}的执行TCL命令功能...")
    
    try:
        response = requests.post(f"{BASE_URL}/{tool_name}/execute_tcl", 
                                json={"command": command})
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2)}")
        
        # 验证响应格式
        response_data = response.json()
        if 'code' in response_data and 'message' in response_data:
            print("✓ 响应格式正确，包含code和message字段")
        else:
            print("✗ 响应格式不正确")
    except Exception as e:
        print(f"错误: {e}")
    
    print("-" * 50)


def test_place_cells(tool_name, params=None):
    """测试执行cell摆放功能"""
    print(f"测试{tool_name}的执行cell摆放功能...")
    
    try:
        payload = {"params": params} if params else {}
        response = requests.post(f"{BASE_URL}/{tool_name}/place_cells", 
                                json=payload)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2)}")
        
        # 验证响应格式
        response_data = response.json()
        if 'code' in response_data and 'message' in response_data:
            print("✓ 响应格式正确，包含code和message字段")
        else:
            print("✗ 响应格式不正确")
    except Exception as e:
        print(f"错误: {e}")
    
    print("-" * 50)


def run_comprehensive_tests():
    """运行全面的API测试"""
    print("开始测试EDX Plugin API...")
    print("=" * 50)
    
    # 创建临时网表文件用于测试
    with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as temp_file:
        temp_file.write("// Simple test netlist\nmodule test(input clk, output reg q);\n  always @(posedge clk) begin\n    q <= ~q;\n  end\nendmodule")
        temp_filename = temp_file.name
    
    try:
        # 测试支持的工具
        test_home()
        
        # 测试Leapr
        print("=== 测试Leapr ===")
        test_load_netlist("leapr", temp_filename)
        test_get_timing("leapr")
        test_execute_tcl("leapr", "place_design")
        test_place_cells("leapr", {"utilization": 0.80, "aspect_ratio": 1.0})
        
        # 尝试使用不支持的工具
        print("=== 测试不支持的工具 ===")
        try:
            response = requests.get(f"{BASE_URL}/unsupported_tool/get_timing")
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2)}")
            
            # 验证错误响应格式
            response_data = response.json()
            if 'code' in response_data and 'message' in response_data and 'error' in response_data:
                print("✓ 错误响应格式正确，包含code、message和error字段")
            else:
                print("✗ 错误响应格式不正确")
        except Exception as e:
            print(f"错误: {e}")
    
    finally:
        # 清理临时文件
        os.unlink(temp_filename)
    
    print("API测试完成!")


if __name__ == "__main__":
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    run_comprehensive_tests()