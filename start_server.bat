@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   EDX Plugin EDA工具REST API服务启动脚本
echo ========================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保已安装Python并添加到PATH环境变量
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖...
if exist requirements.txt (
    echo 安装依赖包...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo 警告: 安装依赖时出现问题，继续尝试启动服务...
    )
) else (
    echo 警告: 未找到requirements.txt文件
)

REM 启动服务器
echo.
echo 正在启动EDX Plugin服务...
echo 访问 http://localhost:5000 查看API服务状态
echo.
echo 按 Ctrl+C 可停止服务
echo.

python run_server.py %*

echo.
echo 服务已停止
pause