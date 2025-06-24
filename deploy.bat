@echo off
chcp 65001 > nul

echo 🚀 MeetSpot 智能会面点推荐系统 - 快速部署脚本
echo ==================================================

echo 📋 检查环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.11 或更高版本
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python 版本: %python_version%

echo 📦 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ⚙️ 检查配置...
if not exist "config\config.toml" (
    echo 📄 创建配置文件...
    copy "config\config.toml.example" "config\config.toml"
    echo ⚠️ 请编辑 config\config.toml 文件添加高德地图 API 密钥
)

echo 🧪 运行测试...
python -m pytest tests\ -v
if errorlevel 1 (
    echo ⚠️ 部分测试失败，但可以继续部署
)

echo 🚀 启动服务...
echo 服务将在 http://localhost:8000 启动
echo 按 Ctrl+C 停止服务
echo ==================================================

python web_server.py
pause
