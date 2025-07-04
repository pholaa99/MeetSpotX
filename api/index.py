import sys
import os
import asyncio
import time
from pathlib import Path
from typing import List
from urllib.parse import parse_qs, urlparse

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 设置项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")
os.chdir(str(project_root))

# 创建 FastAPI 应用
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

# 尝试挂载静态文件
try:
    if os.path.exists("workspace"):
        app.mount("/workspace", StaticFiles(directory="workspace"), name="workspace")
        print("✅ Mounted /workspace static files")
    else:
        print("⚠️ workspace directory not found")
except Exception as e:
    print(f"⚠️ Static files mount failed: {e}")

# 创建简化的数据模型
class CafeRequest(BaseModel):
    locations: List[str]
    keywords: str = "咖啡馆"
    user_requirements: str = ""
    theme: str = ""

# 请求计数器
request_count = 0
performance_stats = {
    "total_requests": 0,
    "total_response_time": 0.0,
    "average_response_time": 0.0,
    "last_reset": time.time()
}

# 性能监控中间件
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """性能监控中间件"""
    start_time = time.time()
    global request_count
    request_count += 1
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    performance_stats["total_requests"] += 1
    performance_stats["total_response_time"] += process_time
    performance_stats["average_response_time"] = (
        performance_stats["total_response_time"] / performance_stats["total_requests"]
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = str(request_count)
    
    return response

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """主页处理"""
    query_params = parse_qs(urlparse(str(request.url)).query)

    if "query" in query_params and query_params["query"]:
        query = query_params["query"][0]
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MeetSpot - 查询结果</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       margin: 0; padding: 20px; min-height: 100vh; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; 
                             border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>查询处理中...</h1>
                <p>查询内容：{query}</p>
                <p>系统正在处理您的请求，完整功能正在加载中。</p>
                <a href="/">← 返回首页</a>
            </div>
        </body>
        </html>
        """)
    else:
        # 返回主页
        try:
            meetspot_html_path = "workspace/meetspot_finder.html"
            if os.path.exists(meetspot_html_path):
                return FileResponse(meetspot_html_path)
        except Exception as e:
            print(f"无法加载 meetspot_finder.html: {e}")
        
        # Fallback 主页
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MeetSpot - 智能会面点推荐</title>
            <style>
                body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       margin: 0; padding: 20px; min-height: 100vh; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; 
                             border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }
                h1 { color: #333; margin-bottom: 20px; }
                .feature { background: #f8f9ff; padding: 20px; margin: 20px 0; border-radius: 10px; }
                .btn { background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                       padding: 15px 30px; border: none; border-radius: 8px; 
                       text-decoration: none; display: inline-block; margin: 10px; }
                .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>�️ MeetSpot</h1>
                <h2>智能会面点推荐系统</h2>
                
                <div class="status">
                    ✅ 服务运行正常<br>
                    已成功部署到 Vercel
                </div>
                
                <div class="feature">
                    <h3>📍 多地点计算</h3>
                    <p>支持输入多个参与者地点，智能计算最佳会面位置</p>
                </div>
                <div class="feature">
                    <h3>🎯 场景推荐</h3>
                    <p>根据场景类型（咖啡馆、餐厅、图书馆等）推荐合适地点</p>
                </div>
                <div class="feature">
                    <h3>🎨 个性化需求</h3>
                    <p>支持自定义筛选条件和特殊需求</p>
                </div>
                
                <h3>API端点</h3>
                <p><a href="/health" style="color: #667eea;">/health</a> - 健康检查</p>
                <p><a href="/api/status" style="color: #667eea;">/api/status</a> - API状态</p>
                <p><a href="/docs" style="color: #667eea;">/docs</a> - API文档</p>
                
                <a href="/workspace/meetspot_finder.html" class="btn">开始使用完整版</a>
                <a href="/api/find_meetspot" class="btn">API 接口</a>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "MeetSpot",
        "version": "1.0.0",
        "timestamp": time.time(),
        "uptime": time.time() - performance_stats["last_reset"],
        "performance": performance_stats,
        "mode": "production"
    }

@app.get("/api/status")
async def api_status():
    """API状态端点"""
    return {
        "api": "MeetSpot API",
        "status": "online",
        "endpoints": [
            "/health - 健康检查",
            "/api/status - API状态", 
            "/api/find_meetspot - 会面点推荐",
            "/docs - API文档"
        ]
    }

@app.post("/api/find_meetspot")
async def find_meetspot(request: CafeRequest):
    """会面点推荐 API"""
    try:
        # 简化版推荐逻辑
        result = {
            "status": "success",
            "query": {
                "locations": request.locations,
                "keywords": request.keywords,
                "requirements": request.user_requirements,
                "theme": request.theme
            },
            "message": "API 正常运行，完整推荐功能正在加载中",
            "recommendations": [
                {
                    "name": "示例咖啡馆",
                    "address": "示例地址",
                    "score": 4.5,
                    "note": "这是一个示例推荐，完整功能正在开发中"
                }
            ]
        }
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel 函数处理器
def handler(event, context):
    """Vercel 函数处理器"""
    return app
