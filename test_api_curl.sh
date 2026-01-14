#!/bin/bash

# EDX Plugin API 接口测试脚本
# 用于测试所有API端点

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 初始化计数器
success_count=0
failure_count=0

# 函数：打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# 打印格式化后的响应体的前N行
print_body_lines() {
    local body="$1"
    local max_lines="${2:-10}"
    
    # 尝试格式化JSON，如果失败则按原样处理
    if echo "$body" | jq . >/dev/null 2>&1; then
        # 格式化JSON并取前N行
        formatted_body=$(echo "$body" | jq . 2>/dev/null)
        local line_count=$(echo "$formatted_body" | wc -l)
        
        if [ $line_count -gt $max_lines ]; then
            echo "$formatted_body" | head -n $max_lines
            print_warning "... (仅显示格式化JSON的前${max_lines}行，共${line_count}行)"
        else
            echo "$formatted_body"
        fi
    else
        # 如果不是有效的JSON，则按原样处理
        local line_count=$(echo "$body" | wc -l)
        
        if [ $line_count -gt $max_lines ]; then
            echo "$body" | head -n $max_lines
            print_warning "... (仅显示前${max_lines}行，共${line_count}行)"
        else
            echo "$body"
        fi
    fi
}

# 创建临时网表文件用于测试
create_test_netlist() {
    local netlist_path="$1"
    cat > "$netlist_path" << 'EOF'
// 测试网表文件
module test(input clk, input rst, output reg [7:0] q);
    always @(posedge clk or posedge rst) begin
        if (rst)
            q <= 8'b0;
        else
            q <= q + 1;
    end
endmodule
EOF
}

# 测试主页面
test_home() {
    print_header "测试 1: 主页面接口"
    print_info "GET http://localhost:5000/"
    
    response=$(curl -s -w "\n%{http_code}" http://localhost:5000/)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        print_success "主页面接口测试成功，状态码: $http_code"
        print_body_lines "$body" 10
        ((success_count++))
    else
        print_error "主页面接口测试失败，状态码: $http_code"
        print_body_lines "$body" 10
        ((failure_count++))
    fi
    echo
}

# 测试加载网表
test_load_netlist() {
    print_header "测试 2: 加载网表接口"
    
    # 创建临时网表文件
    local temp_netlist="/tmp/test_netlist.v"
    create_test_netlist "$temp_netlist"
    
    print_info "POST http://localhost:5000/leapr/load_netlist"
    print_info "上传网表文件: $temp_netlist"
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST http://localhost:5000/leapr/load_netlist \
        -H "Content-Type: application/json" \
        -d "{\"file_path\": \"$temp_netlist\"}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        print_success "加载网表接口测试成功，状态码: $http_code"
        print_body_lines "$body" 10
        ((success_count++))
    else
        print_error "加载网表接口测试失败，状态码: $http_code"
        print_body_lines "$body" 10
        ((failure_count++))
    fi
    
    # 清理临时文件
    rm -f "$temp_netlist"
    echo
}

# 测试获取时序信息（无参数）
test_get_timing_default() {
    print_header "测试 3.1: 获取时序信息接口（默认参数）"
    print_info "GET http://localhost:5000/leapr/get_timing"
    
    response=$(curl -s -w "\n%{http_code}" http://localhost:5000/leapr/get_timing)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        print_success "获取时序信息接口测试成功（默认参数），状态码: $http_code"
        print_body_lines "$body" 10
        ((success_count++))
    else
        print_error "获取时序信息接口测试失败（默认参数），状态码: $http_code"
        print_body_lines "$body" 10
        ((failure_count++))
    fi
    echo
}

# 测试获取时序信息（topn参数为1）
test_get_timing_with_topn_1() {
    print_header "测试 3.2: 获取时序信息接口（topn=1参数）"
    print_info "GET http://localhost:5000/leapr/get_timing?topn=1"
    
    response=$(curl -s -w "\n%{http_code}" http://localhost:5000/leapr/get_timing?topn=1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        print_success "获取时序信息接口测试成功（topn=1），状态码: $http_code"
        print_body_lines "$body" 10
        ((success_count++))
    else
        print_error "获取时序信息接口测试失败（topn=1），状态码: $http_code"
        print_body_lines "$body" 10
        ((failure_count++))
    fi
    echo
}

# 测试获取时序信息（topn参数为3）
test_get_timing_with_topn_3() {
    print_header "测试 3.3: 获取时序信息接口（topn=3参数）"
    print_info "GET http://localhost:5000/leapr/get_timing?topn=3"
    
    response=$(curl -s -w "\n%{http_code}" http://localhost:5000/leapr/get_timing?topn=3)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        print_success "获取时序信息接口测试成功（topn=3），状态码: $http_code"
        print_body_lines "$body" 10
        ((success_count++))
    else
        print_error "获取时序信息接口测试失败（topn=3），状态码: $http_code"
        print_body_lines "$body" 10
        ((failure_count++))
    fi
    echo
}

# 测试执行TCL命令
test_execute_tcl() {
    print_header "测试 4: 执行TCL命令接口"
    print_info "POST http://localhost:5000/leapr/execute_tcl"
    print_info "请求体: {\"command\": \"[puts test_tcl]\"}}"

    response=$(curl -s -w "\n%{http_code}" \
        -X POST http://localhost:5000/leapr/execute_tcl \
        -H "Content-Type: application/json" \
        -d '{"commands": ["puts test_tcl"]}')
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        print_success "执行TCL命令接口测试成功，状态码: $http_code"
        print_body_lines "$body" 10
        ((success_count++))
    else
        print_error "执行TCL命令接口测试失败，状态码: $http_code"
        print_body_lines "$body" 10
        ((failure_count++))
    fi
    echo
}

# 测试执行cell摆放
test_place_cells() {
    print_header "测试 5: 执行cell摆放接口"
    print_info "POST http://localhost:5000/leapr/place_cells"
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST http://localhost:5000/leapr/place_cells \
        -H "Content-Type: application/json" \
        -d '[{"cell_name": "u_macc_top/macc[0].u_macc/lc_drvi15_n119", "x": 10.67, "y": 11.12, "width": 10.0, "height": 12.0, "orient": "R0", "place_status": "PLACED"}]')
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        print_success "执行cell摆放接口测试成功，状态码: $http_code"
        print_body_lines "$body" 10
        ((success_count++))
    else
        print_error "执行cell摆放接口测试失败，状态码: $http_code"
        print_body_lines "$body" 10
        ((failure_count++))
    fi
    echo
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖项..."
    
    if ! command -v curl &> /dev/null; then
        print_error "curl 未安装，请先安装 curl"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        print_warning "jq 未安装，将无法格式化JSON输出"
    fi
    
    print_success "依赖检查完成"
    echo
}

# 检查服务是否运行
check_service() {
    print_info "检查服务是否运行在 http://localhost:5000..."
    
    if timeout 10 bash -c "until curl -s -o /dev/null http://localhost:5000/; do sleep 0.5; done"; then
        print_success "服务正在运行"
        echo
        return 0
    else
        print_error "服务未在 http://localhost:5000 运行"
        print_info "请先启动服务: ./run_server.py 或 python main.py"
        exit 1
    fi
}

# 显示测试结果统计
print_test_summary() {
    local total_tests=$((success_count + failure_count))
    print_header "========================================="
    print_header "          测试结果统计"
    print_header "========================================="
    echo
    print_info "总测试用例数: $total_tests"
    print_success "成功: $success_count"
    if [ $failure_count -gt 0 ]; then
        print_error "失败: $failure_count"
    else
        print_success "失败: $failure_count"
    fi
    echo
    
    if [ $total_tests -gt 0 ]; then
        local success_rate=$((success_count * 100 / total_tests))
        print_info "成功率: ${success_rate}%"
    fi
}

# 显示使用说明
show_usage() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  --help     显示此帮助信息"
    echo "  --host     指定服务器主机 (默认: localhost)"
    echo "  --port     指定服务器端口 (默认: 5000)"
    echo
    echo "示例:"
    echo "  $0                           # 使用默认设置测试"
    echo "  $0 --host 192.168.1.100     # 测试指定主机"
    echo "  $0 --port 8080              # 测试指定端口"
}

# 解析命令行参数
HOST="localhost"
PORT="5000"

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "未知参数: $1"
            show_usage
            exit 1
            ;;
    esac
done

# 更新API_BASE_URL
API_BASE_URL="http://$HOST:$PORT"

# 显示标题
print_header "========================================="
print_header "  EDX Plugin API 接口测试脚本"
print_header "========================================="
echo

# 检查依赖
check_dependencies

# 检查服务
check_service

# 运行测试
print_info "开始测试 EDX Plugin API 接口..."
echo

test_home
test_load_netlist
test_get_timing_default
test_get_timing_with_topn_1
test_get_timing_with_topn_3
test_execute_tcl
test_place_cells

# 打印测试结果统计
print_test_summary

print_success "所有API测试完成！"
print_info "如果某些测试失败，请检查服务是否正常运行以及请求参数是否正确。"