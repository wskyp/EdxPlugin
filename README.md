# EDX Plugin - EDA工具REST API接口

这是一个用于电子设计自动化(EDA)工具的REST API接口，支持多种EDA工具，提供网表处理、时序分析、TCL命令执行和单元摆放等功能。

## 功能特性

- 📁 **读取网表**: 加载和解析电路网表文件
- ⏱️ **时序分析**: 获取电路的时序信息
- 🔧 **TCL命令执行**: 执行EDA工具的TCL命令
- 📐 **Cell摆放**: 执行单元摆放算法
- 🔄 **多工具支持**: 支持Leapr等多种EDA工具
- 📝 **日志记录**: 详细的日志记录功能，便于问题定位
- 📊 **统一响应格式**: 所有API返回统一的响应格式，包含code、message和data字段

## 支持的EDA工具

- **Leapr**: 物理设计工具，用于布局布线

## 安装与启动

### 环境要求

- Python 3.7+
- pip包管理器

### Linux/Mac安装步骤

1. 克隆或下载此项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 启动服务：
   ```bash
   python main.py
   ```

或者使用启动脚本：
   ```bash
   chmod +x start_server.sh
   ./start_server.sh
   ```

服务器将在 http://localhost:5000 上运行。

### Linux启动脚本使用

我们提供了 `start_server.sh` 脚本来方便Linux用户启动服务：

1. 使脚本可执行：
   ```bash
   chmod +x start_server.sh
   ```

2. 运行脚本：
   ```bash
   ./start_server.sh
   ```

3. 自定义参数：
   ```bash
   # 指定主机和端口
   ./start_server.sh --host 0.0.0.0 --port 8080
   
   # 启用调试模式
   ./start_server.sh --debug
   
   # 同时指定多个参数
   ./start_server.sh --host 127.0.0.1 --port 8080 --debug
   ```

脚本功能：
- 自动检测Python版本
- 自动创建虚拟环境（如果不存在）
- 自动安装依赖
- 彩色输出日志
- 参数化配置

### Windows安装步骤

1. 克隆或下载此项目到本地
2. 安装依赖：
   ```cmd
   pip install -r requirements.txt
   ```
3. 启动服务：
   ```cmd
   python main.py
   ```
   
或者双击 `start_server.bat` 批处理文件。

## 日志功能

系统会自动记录所有操作到 `edx_plugin.log` 文件中，包括：
- 工具初始化信息
- API请求和响应
- 错误和异常信息
- 操作成功和失败的状态

日志格式为：`时间戳 级别 工具名 信息`

## API端点

### 工具列表 (`GET /`)

获取支持的EDA工具列表和API端点信息。

#### 示例请求
```bash
curl -X GET http://localhost:5000/
```

### 1. 读取网表 (`POST /<tool_name>/load_netlist`)

为指定的EDA工具加载电路网表文件到内存中进行后续处理。

#### 支持的工具名称
- `leapr`

#### 请求参数
```json
{
  "file_path": "/path/to/netlist.v"
}
```

#### 示例请求 (Leapr)
```bash
curl -X POST http://localhost:5000/leapr/load_netlist \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/netlist.v"}'
```

#### 响应示例 (Leapr)
```json
{
  "code": 200,
  "message": "Leapr: Successfully loaded netlist: /path/to/netlist.v",
  "data": {
    "name": "test_design",
    "top_module": "top_module",
    "cells": [
      {
        "name": "INV_X1",
        "cell_type": "combinational",
        "area": 1.2,
        "power": 0.003,
        "delay": 0.12,
        "pins": [],
        "properties": {}
      }
    ],
    "nets": [...],
    "ports": [...],
    "clocks": [...],
    "timing_arcs": [...],
    "hierarchy": ["top_module", "sub_module1", "sub_module2"],
    "area": 1200.5,
    "utilization": 75.2,
    "tool_used": "Leapr",
    "properties": {
      "file_path": "/path/to/netlist.v",
      "size": 1024,
      "supported_formats": ["verilog", "lef", "gds", "def", "sdc"]
    }
  }
}
```

### 2. 获取时序信息 (`GET /<tool_name>/get_timing`)

获取指定EDA工具的时序分析结果。

#### 示例请求 (Leapr)
```bash
curl -X GET http://localhost:5000/leapr/get_timing
```

#### 响应示例 (Leapr)
```json
{
  "code": 200,
  "message": "Leapr: Timing analysis completed",
  "data": {
    "tool": "Leapr",
    "setup_slack": -0.123,
    "hold_slack": 0.456,
    "clock_period": 2.0,
    "setup_margin": 0.1,
    "hold_margin": 0.05,
    "min_pulse_width": 0.5,
    "clock_skew": 0.05,
    "power_consumption": {
      "dynamic": 12.5,
      "static": 0.8
    },
    "critical_path": [...],
    "worst_clock": "clk",
    "timing_violations": 2
  }
}
```

### 3. 执行TCL命令 (`POST /<tool_name>/execute_tcl`)

为指定EDA工具执行TCL命令。

#### 请求参数
```json
{
  "command": "place_design"
}
```

#### 示例请求 (Leapr)
```bash
curl -X POST http://localhost:5000/leapr/execute_tcl \
  -H "Content-Type: application/json" \
  -d '{"command": "place_design"}'
```

#### 响应示例
```json
{
  "code": 200,
  "message": "TCL command executed successfully",
  "data": {
    "tool": "Leapr",
    "command": "place_design",
    "mapped_command": "place_design",
    "result": "Leapr executed: place_design",
    "status": "success",
    "command_type": "other"
  }
}
```

### 4. 执行Cell摆放 (`POST /<tool_name>/place_cells`)

为指定EDA工具执行电路单元的摆放算法。

#### 请求参数
```json
{
  "params": {
    "utilization": 0.75,
    "aspect_ratio": 1.0
  }
}
```

#### 示例请求 (Leapr)
```bash
curl -X POST http://localhost:5000/leapr/place_cells \
  -H "Content-Type: application/json" \
  -d '{"params": {"utilization": 0.75, "aspect_ratio": 1.0}}'
```

#### 响应示例 (Leapr)
```json
{
  "code": 200,
  "message": "Leapr: Cell placement completed",
  "data": {
    "tool": "Leapr",
    "placement_status": "completed",
    "utilization": 75.0,
    "aspect_ratio": 1.0,
    "target_density": 85.0,
    "core_area": 2100.3,
    "routing_layers": ["M1", "M2", "M3", "M4", "M5", "M6"],
    "congestion_map": "low",
    "vias_count": 1500,
    "min_distance_constraint": 0.1,
    "power_ring_width": 1.0,
    "placed_cells": [
      {"name": "BUF_X1", "x": 100.5, "y": 200.3, "orientation": "FN", "layer": "M1"},
      {"name": "CLKBUF_X2", "x": 150.2, "y": 250.7, "orientation": "FS", "layer": "M2"},
      {"name": "PHYCELL_X1", "x": 220.8, "y": 180.1, "orientation": "FE", "layer": "M3"}
    ]
  }
}
```

## 错误处理

API会返回适当的HTTP状态码和错误信息：

- `400 Bad Request`: 请求参数错误或不支持的EDA工具
- `500 Internal Server Error`: 服务器内部错误

错误响应格式：
```json
{
  "code": 400,
  "message": "Error message",
  "error": "Detailed error information"
}
```

## 数据模型

系统使用统一的数据模型来表示电路设计信息，主要包含：
- **Design**: 设计的主要容器，包含所有其他元素
- **Cell**: 电路单元（标准单元、宏单元等）
- **Net**: 网络连接
- **Port**: 设计端口
- **Clock**: 时钟定义
- **TimingArc**: 时序弧

## 使用场景

此API适用于：
- 集成多种EDA工具到Web应用
- 自动化IC设计流程
- 电路仿真和验证
- 设计数据可视化
- 远程EDA工具访问
- EDA工具间的协同工作流

## 扩展支持

要添加新的EDA工具支持，请：
1. 创建继承自BaseEDA_Tool的新类
2. 实现load_netlist、get_timing_info、execute_tcl_command和place_cells方法
3. 在eda_tools字典中添加工具实例

## 许可证

请参阅项目许可证文件。