@echo off
echo 🚀 MeetSpot Vercel 部署脚本
echo ================================

REM 检查是否在正确的目录
if not exist "vercel.json" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

echo 📋 检查必需文件...

REM 检查必需文件
if exist "vercel.json" (echo ✅ vercel.json) else (echo ❌ 缺少文件: vercel.json & pause & exit /b 1)
if exist "api\index.py" (echo ✅ api\index.py) else (echo ❌ 缺少文件: api\index.py & pause & exit /b 1)
if exist "web_server.py" (echo ✅ web_server.py) else (echo ❌ 缺少文件: web_server.py & pause & exit /b 1)
if exist "requirements.txt" (echo ✅ requirements.txt) else (echo ❌ 缺少文件: requirements.txt & pause & exit /b 1)
if exist "package.json" (echo ✅ package.json) else (echo ❌ 缺少文件: package.json & pause & exit /b 1)

echo.
echo 🧹 清理临时文件...
REM 清理Python缓存文件
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
del /s /q *.log >nul 2>&1

echo ✅ 清理完成
echo.

echo 📝 Git 状态检查...
git status >nul 2>&1
if errorlevel 1 (
    echo ❌ 这不是一个Git仓库，请先初始化Git
    pause
    exit /b 1
)

echo 当前Git状态:
git status --porcelain

echo.
echo 🤔 是否要提交并推送更改? (y/n)
set /p response=

if /i "%response%"=="y" (
    echo 📤 提交更改...
    git add .
    git commit -m "🚀 Ready for Vercel deployment - Add Vercel configuration files - Create API entry point for serverless functions - Clean up dependencies and test files - Update project structure for production"
    
    echo 📤 推送到远程仓库...
    git push
    
    echo ✅ 代码已推送
) else (
    echo ⏭️  跳过Git提交
)

echo.
echo 🌐 Vercel 部署选项:
echo 1. 访问 https://vercel.com/new 并连接你的GitHub仓库
echo 2. 或运行: npx vercel --prod
echo.
echo 🎉 准备完成！现在可以在Vercel上部署了！
echo.
echo 按任意键继续...
pause >nul
