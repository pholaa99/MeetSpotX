#!/bin/bash

# MeetSpot 快速部署脚本
# 适用于 Linux/macOS 系统

echo "🚀 MeetSpot 智能会面点推荐系统 - 快速部署脚本"
echo "=================================================="

# 检查 Python 版本
echo "📋 检查环境..."
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 1 ]]; then
    echo "✅ Python 版本: $(python3 --version)"
else
    echo "❌ 需要 Python 3.11 或更高版本，当前版本: $(python3 --version)"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip3 install -r requirements.txt

# 检查配置文件
echo "⚙️  检查配置..."
if [ ! -f "config/config.toml" ]; then
    echo "📄 创建配置文件..."
    cp config/config.toml.example config/config.toml
    echo "⚠️  请编辑 config/config.toml 文件添加高德地图 API 密钥"
fi

# 运行测试
echo "🧪 运行测试..."
python3 -m pytest tests/ -v

if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过"
else
    echo "⚠️  部分测试失败，但可以继续部署"
fi

# 启动服务
echo "🚀 启动服务..."
echo "服务将在 http://localhost:8000 启动"
echo "按 Ctrl+C 停止服务"
echo "=================================================="

python3 web_server.py
