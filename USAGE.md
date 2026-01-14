# EDX Plugin 启动脚本使用说明

## Linux/Mac 启动脚本

### 文件名
- `start_server.sh` - Linux/Mac 启动脚本

### 权限设置
首次使用前需要给脚本赋予执行权限：
```bash
chmod +x start_server.sh
```

### 基本用法
```bash
./start_server.sh
```

### 参数说明
- `-h, --host HOST` - 指定服务器监听的主机地址，默认为 `0.0.0.0`
- `-p, --port PORT` - 指定服务器监听的端口，默认为 `5000`
- `-d, --debug` - 启用调试模式
- `--help` - 显示帮助信息

### 使用示例

1. 启动默认服务：
   ```bash
   ./start_server.sh
   ```

2. 指定主机和端口：
   ```bash
   ./start_server.sh --host 127.0.0.1 --port 8080
   ```

3. 启用调试模式：
   ```bash
   ./start_server.sh --debug
   ```

4. 组合参数：
   ```bash
   ./start_server.sh --host 0.0.0.0 --port 9000 --debug
   ```

## Windows 启动脚本

### 文件名
- `start_server.bat` - Windows 批处理脚本

### 基本用法
双击运行 `start_server.bat` 或在命令行中执行：
```cmd
start_server.bat
```

### 参数说明
Windows 脚本目前使用默认参数启动，如需自定义参数，请直接运行：
```cmd
python run_server.py --host 0.0.0.0 --port 5000 --debug
```

## 脚本功能特点

1. **自动环境检测** - 自动检测系统中的 Python 版本
2. **依赖管理** - 自动安装所需的依赖包
3. **虚拟环境** - 自动创建和管理 Python 虚拟环境
4. **彩色日志** - 使用彩色输出显示不同类型的信息
5. **错误处理** - 包含完善的错误处理和提示信息
6. **优雅退出** - 支持使用 Ctrl+C 优雅地停止服务

## 服务访问

服务启动后，默认可以通过以下地址访问：
- API 文档: `http://localhost:5000/`
- 各功能端点: `http://localhost:5000/<tool_name>/<endpoint>`

## 日志文件

服务运行过程中会生成以下日志文件：
- `edx_plugin.log` - 主要服务日志
- `server_startup.log` - 服务启动日志

## 故障排除

如果遇到问题，请检查：
1. Python 3.7+ 是否已正确安装
2. `requirements.txt` 中的依赖是否已安装
3. 端口是否被其他服务占用
4. 日志文件中的错误信息