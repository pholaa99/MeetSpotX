import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 设置项目根目录
project_root = Path(__file__).parent.parent
os.chdir(str(project_root))

# 创建 FastAPI 应用
app = FastAPI(title="MeetSpot", description="智能会面点推荐系统")

# 添加CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
try:
    if os.path.exists("workspace"):
        app.mount("/workspace", StaticFiles(directory="workspace"), name="workspace")
        print("✅ Mounted workspace static files")
    if os.path.exists("docs"):
        app.mount("/docs", StaticFiles(directory="docs"), name="docs")
        print("✅ Mounted docs static files")
except Exception as e:
    print(f"⚠️ Static files mount failed: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页 - 直接返回前端界面"""
    try:
        # 直接返回 meetspot_finder.html 文件
        meetspot_html_path = "workspace/meetspot_finder.html"
        if os.path.exists(meetspot_html_path):
            with open(meetspot_html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <title>MeetSpot - 文件未找到</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: red; margin: 20px; }}
                </style>
            </head>
            <body>
                <h1>MeetSpot</h1>
                <div class="error">前端文件未找到: {meetspot_html_path}</div>
                <p>当前工作目录: {os.getcwd()}</p>
                <p>文件列表: {os.listdir('workspace') if os.path.exists('workspace') else '无workspace目录'}</p>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>MeetSpot - 错误</title></head>
        <body>
            <h1>加载错误</h1>
            <p>错误信息: {str(e)}</p>
            <p>工作目录: {os.getcwd()}</p>
        </body>
        </html>
        """, status_code=500)

@app.get("/health")
async def health():
    """健康检查"""
    return JSONResponse({
        "status": "healthy",
        "service": "MeetSpot",
        "mode": "frontend"
    })

# Vercel 处理函数
def handler(event, context):
    return app
