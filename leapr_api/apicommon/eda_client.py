#!/usr/bin/env python3
"""
EDA TCP Client - Python客户端用于向TCL服务器发送命令
这个脚本实现了TCP客户端，可以连接到TCL编写的EDA服务器，
发送TCL命令或脚本，并接收执行结果。
"""

import socket
import sys
import json
import argparse
from typing import Union


class EdaTcpClient:
    def __init__(self, host: str = 'localhost', port: int = 9999):
        """
        初始化EDA TCP客户端
        
        Args:
            host: 服务器主机地址
            port: 服务器端口号
        """
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """连接到TCL服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置连接超时
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            print(f"已连接到EDA服务器 {self.host}:{self.port}")
            
            # 接收欢迎消息
            welcome_msg = self.receive_response()
            if welcome_msg:
                print(f"服务器消息: {welcome_msg}")
                
        except socket.timeout:
            print(f"连接超时: 无法连接到 {self.host}:{self.port}")
            sys.exit(1)
        except ConnectionRefusedError:
            print(f"连接被拒绝: 无法连接到 {self.host}:{self.port}")
            sys.exit(1)
        except Exception as e:
            print(f"连接错误: {e}")
            sys.exit(1)

    def send_command(self, command: str) -> Union[str, tuple]:
        """
        发送TCL命令到服务器并接收响应
        
        Args:
            command: TCL命令或脚本字符串
            
        Returns:
            服务器响应结果
        """
        if not self.socket:
            print("错误: 未建立连接")
            return None

        try:
            # 发送命令
            self.socket.sendall((command + '\n').encode('utf-8'))
            
            # 接收响应
            response = self.receive_response()
            return response
            
        except Exception as e:
            print(f"发送命令时出错: {e}")
            return None

    def receive_response(self) -> str:
        """接收服务器响应"""
        try:
            # 设置接收超时
            self.socket.settimeout(30)
            response = self.socket.recv(4096).decode('utf-8').strip()
            return response
        except socket.timeout:
            print("接收响应超时")
            return None
        except Exception as e:
            print(f"接收响应时出错: {e}")
            return None

    def close(self):
        """关闭连接"""
        if self.socket:
            try:
                self.socket.close()
                print("连接已关闭")
            except Exception as e:
                print(f"关闭连接时出错: {e}")


def parse_server_response(response: str) -> dict:
    """
    解析服务器返回的响应
    
    Args:
        response: 服务器返回的原始响应
        
    Returns:
        解析后的结果字典
    """
    if not response:
        return {"status": "error", "result": "空响应"}

    # 尝试解析为JSON格式
    try:
        parsed = json.loads(response)
        if isinstance(parsed, list) and len(parsed) >= 2:
            status = parsed[0]
            result = parsed[1] if len(parsed) > 1 else ""
            return {"status": status.lower(), "result": result}
        else:
            return {"status": "ok", "result": response}
    except json.JSONDecodeError:
        # 如果不是JSON格式，直接返回原响应
        # This handles cases where the server sends plain text instead of JSON
        return {"status": "ok", "result": response}


def main():
    parser = argparse.ArgumentParser(description='EDA TCP Client - 向TCL服务器发送TCL命令')
    parser.add_argument('--host', default='localhost', help='服务器主机地址 (默认: localhost)')
    parser.add_argument('-p', '--port', type=int, default=9999, help='服务器端口 (默认: 9999)')
    parser.add_argument('command', nargs='?', help='要发送的TCL命令 (如果未提供则进入交互模式)')
    parser.add_argument('-f', '--file', help='包含TCL脚本的文件路径')

    args = parser.parse_args()

    # 创建客户端实例
    client = EdaTcpClient(host=args.host, port=args.port)

    try:
        # 连接到服务器
        client.connect()

        # 确定要发送的命令
        if args.file:
            # 从文件读取TCL脚本
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    command = f.read().strip()
                print(f"从文件 '{args.file}' 读取TCL脚本:")
                print(command[:200] + "..." if len(command) > 200 else command)
                print("-" * 40)
            except FileNotFoundError:
                print(f"错误: 文件 '{args.file}' 不存在")
                sys.exit(1)
            except Exception as e:
                print(f"读取文件时出错: {e}")
                sys.exit(1)
        elif args.command:
            # 使用命令行提供的命令
            command = args.command
        else:
            # 进入交互模式
            print("进入交互模式 (输入 'exit' 或 'quit' 退出)")
            while True:
                try:
                    command = input("\nTCL> ").strip()
                    if command.lower() in ['exit', 'quit']:
                        break
                    
                    if not command:
                        continue
                    
                    print(f"发送命令: {command}")
                    
                    # 发送命令
                    response = client.send_command(command)
                    
                    # 解析并显示响应
                    parsed_response = parse_server_response(response)
                    status = parsed_response.get("status", "unknown")
                    result = parsed_response.get("result", "")
                    
                    print(f"状态: {status}")
                    print(f"结果: {result}")
                    
                except KeyboardInterrupt:
                    print("\n用户中断")
                    break
                except EOFError:
                    print("\n连接结束")
                    break
            client.close()
            return

        # 如果不是交互模式，发送单个命令
        if 'command' in locals() and command:
            print(f"发送命令: {command}")
            
            # 发送命令
            response = client.send_command(command)
            
            # 解析并显示响应
            parsed_response = parse_server_response(response)
            status = parsed_response.get("status", "unknown")
            result = parsed_response.get("result", "")
            
            print(f"状态: {status}")
            print(f"结果: {result}")

    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        client.close()


if __name__ == "__main__":
    main()