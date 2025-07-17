#!/bin/bash

# MeetSpot 快速验证脚本
echo "🔍 MeetSpot 项目完整性验证"
echo "================================"

# 检查核心文件
echo "📁 检查核心文件..."
files=(
    "README.md"
    "README_EN.md" 
    "LICENSE"
    "CONTRIBUTING.md"
    "SECURITY.md"
    "requirements.txt"
    "setup.py"
    "web_server.py"
    "app/tool/meetspot_recommender.py"
    "workspace/meetspot_finder.html"
)

missing_files=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
        missing_files=$((missing_files + 1))
    fi
done

# 检查文档目录
echo "📸 检查文档图片..."
if [ -d "docs" ]; then
    doc_count=$(find docs -name "*.png" | wc -l)
    echo "✅ 找到 $doc_count 个图片文件"
else
    echo "❌ docs 目录缺失"
    missing_files=$((missing_files + 1))
fi

# 检查 GitHub 配置
echo "⚙️ 检查 GitHub 配置..."
github_files=(
    ".github/workflows/ci.yml"
    ".github/ISSUE_TEMPLATE/bug_report.md"
    ".github/ISSUE_TEMPLATE/feature_request.md"
    ".github/pull_request_template.md"
)

for file in "${github_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
        missing_files=$((missing_files + 1))
    fi
done

# 检查测试文件
echo "🧪 检查测试文件..."
if [ -d "tests" ]; then
    test_count=$(find tests -name "*.py" | wc -l)
    echo "✅ 找到 $test_count 个测试文件"
else
    echo "❌ tests 目录缺失"
    missing_files=$((missing_files + 1))
fi

# 总结
echo "================================"
if [ $missing_files -eq 0 ]; then
    echo "🎉 项目完整性验证通过！"
    echo "📦 项目已准备好发布"
    echo ""
    echo "下一步："
    echo "1. git push origin feature"
    echo "2. 在 GitHub 创建 Pull Request"
    echo "3. 合并到 main 分支"
    echo "4. 创建 Release v1.0.0"
else
    echo "⚠️  发现 $missing_files 个缺失文件"
    echo "请检查并补充缺失的文件"
fi

echo ""
echo "🚀 MeetSpot 智能会面点推荐系统"
echo "Made with ❤️ by JasonRobertDestiny"
