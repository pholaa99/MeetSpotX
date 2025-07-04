from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

# 创建简化的FastAPI应用
app = FastAPI(
    title="MeetSpot", 
    description="智能会面点推荐系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量读取API密钥
SILICON_API_KEY = os.getenv("SILICON_API_KEY")  # 硅基流动API密钥
AMAP_API_KEY = os.getenv("AMAP_API_KEY")        # 高德地图API密钥

# 硅基流动API配置
SILICON_BASE_URL = "https://api.siliconflow.cn/v1"  # 硅基流动API基础URL

# 尝试挂载静态文件（如果目录存在）
try:
    if os.path.exists("workspace"):
        app.mount("/workspace", StaticFiles(directory="workspace"), name="workspace")
    if os.path.exists("docs"):
        app.mount("/docs", StaticFiles(directory="docs"), name="docs")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")

@app.get("/")
async def root():
    """主页"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MeetSpot - 智能会面点推荐</title>
        <style>
            body {
                font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 40px;
                max-width: 600px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            h1 { color: #2c3e50; margin-bottom: 20px; }
            .status { 
                background: #2ecc71; 
                color: white; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ MeetSpot</h1>
            <p>智能会面点推荐系统</p>
            <div class="status">
                <strong>✅ 服务运行正常</strong><br>
                已成功部署到 Vercel
            </div>
            <p>系统正在初始化中，完整功能即将上线...</p>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "MeetSpot is running on Vercel"}

@app.get("/api/status")
async def api_status():
    """API状态检查"""
    return {
        "status": "running",
        "service": "MeetSpot API",
        "platform": "Vercel",
        "version": "1.0.0",
        "config": {
            "silicon_api_configured": bool(SILICON_API_KEY),
            "amap_configured": bool(AMAP_API_KEY),
            "silicon_base_url": SILICON_BASE_URL
        }
    }

@app.get("/api/test-silicon")
async def test_silicon_api():
    """测试硅基流动API连接"""
    if not SILICON_API_KEY:
        return JSONResponse(
            status_code=400,
            content={"error": "Silicon API key not configured"}
        )
    
    try:
        import httpx
        
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {SILICON_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a test message."
                }
            ],
            "max_tokens": 50
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "Silicon API connection successful",
                "api_response": response.json()
            }
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "error": "Silicon API error",
                    "status_code": response.status_code,
                    "response": response.text
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to test Silicon API: {str(e)}"}
        )

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "message": "请求的资源不存在"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "服务器内部错误"}
    )

# Vercel需要的应用实例
app_instance = app

# 为Vercel导出的处理函数
def handler(event, context):
    """Vercel serverless function handler"""
    return app

# 直接导出app供Vercel使用
application = app
