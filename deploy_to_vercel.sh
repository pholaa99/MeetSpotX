#!/bin/bash

echo "🚀 MeetSpot Vercel 部署脚本"
echo "================================"

# 检查是否在正确的目录
if [ ! -f "vercel.json" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "📋 检查必需文件..."

# 检查必需文件
required_files=("vercel.json" "api/index.py" "web_server.py" "requirements.txt" "package.json")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ 缺少文件: $file"
        exit 1
    fi
done

echo ""
echo "🧹 清理临时文件..."
# 清理临时文件
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.log" -delete 2>/dev/null

echo "✅ 清理完成"
echo ""

echo "📝 Git 状态检查..."
if ! git status &>/dev/null; then
    echo "❌ 这不是一个Git仓库，请先初始化Git"
    exit 1
fi

# 显示待提交的更改
git status --porcelain

echo ""
echo "🤔 是否要提交并推送更改? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "📤 提交更改..."
    git add .
    git commit -m "🚀 Ready for Vercel deployment

- Add Vercel configuration files
- Create API entry point for serverless functions  
- Clean up dependencies and test files
- Update project structure for production"

    echo "📤 推送到远程仓库..."
    git push

    echo "✅ 代码已推送"
else
    echo "⏭️  跳过Git提交"
fi

echo ""
echo "🌐 Vercel 部署选项:"
echo "1. 访问 https://vercel.com/new 并连接你的GitHub仓库"
echo "2. 或运行: npx vercel --prod"
echo ""
echo "🎉 准备完成！现在可以在Vercel上部署了！"
