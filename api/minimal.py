from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import os

# 创建FastAPI应用
app = FastAPI(title="MeetSpot")

@app.get("/")
def read_root():
    """主页"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MeetSpot - 智能会面点推荐</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0; padding: 40px; min-height: 100vh;
                display: flex; align-items: center; justify-content: center;
            }
            .container { 
                background: white; padding: 40px; border-radius: 15px; 
                text-align: center; max-width: 500px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; margin-bottom: 20px; }
            .status { background: #2ecc71; color: white; padding: 15px; border-radius: 8px; margin: 20px 0; }
            .api-info { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ MeetSpot</h1>
            <p>智能会面点推荐系统</p>
            <div class="status">✅ 服务运行正常<br>已成功部署到 Vercel</div>
            <div class="api-info">
                <h3>API端点</h3>
                <p><a href="/health">/health</a> - 健康检查</p>
                <p><a href="/api/status">/api/status</a> - API状态</p>
                <p><a href="/docs">/docs</a> - API文档</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "message": "MeetSpot is running on Vercel"}

@app.get("/api/status")
def api_status():
    """API状态检查"""
    silicon_key = os.getenv("SILICON_API_KEY")
    amap_key = os.getenv("AMAP_API_KEY")
    
    return {
        "status": "running",
        "service": "MeetSpot API",
        "platform": "Vercel",
        "version": "1.0.0",
        "config": {
            "silicon_api_configured": bool(silicon_key),
            "amap_configured": bool(amap_key),
            "silicon_base_url": "https://api.siliconflow.cn/v1"
        }
    }

# Vercel兼容的导出
app_instance = app
