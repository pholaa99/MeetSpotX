import asyncio
import os
import sys
import time
from pathlib import Path
from typing import List
from urllib.parse import parse_qs, urlparse

import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.agent.manus import Manus
from app.logger import logger
from app.tool.meetspot_recommender import CafeRecommender

app = FastAPI(
    title="OpenManus Web", 
    description="OpenManus会面点推荐Web服务",
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

# 挂载静态文件
app.mount("/workspace", StaticFiles(directory="workspace"), name="workspace")

# 创建工作目录
os.makedirs("workspace/js_src", exist_ok=True)

# 创建Manus代理
agent = Manus()

# 请求计数器和性能监控
request_count = 0
performance_stats = {
    "total_requests": 0,
    "total_response_time": 0.0,
    "average_response_time": 0.0,
    "last_reset": time.time()
}

class CafeRequest(BaseModel):
    locations: List[str]
    keywords: str = "咖啡馆"
    user_requirements: str = ""

# 性能监控中间件
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """性能监控中间件"""
    start_time = time.time()
    
    # 记录请求信息
    global request_count
    request_count += 1
    logger.info(f"处理请求 #{request_count}: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # 计算响应时间
        process_time = time.time() - start_time
        
        # 更新性能统计
        performance_stats["total_requests"] += 1
        performance_stats["total_response_time"] += process_time
        performance_stats["average_response_time"] = (
            performance_stats["total_response_time"] / performance_stats["total_requests"]
        )
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = str(request_count)
        
        logger.info(f"请求 #{request_count} 完成，耗时: {process_time:.3f}秒")
        return response
        
    except Exception as e:
        logger.error(f"请求 #{request_count} 处理异常: {str(e)}")
        # 即使异常也要记录时间
        process_time = time.time() - start_time
        performance_stats["total_requests"] += 1
        performance_stats["total_response_time"] += process_time
        performance_stats["average_response_time"] = (
            performance_stats["total_response_time"] / performance_stats["total_requests"]
        )
        raise

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - performance_stats["last_reset"],
        "performance": performance_stats
    }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """主页处理，检测query参数并调用代理处理"""
    # 解析URL获取查询参数
    query_params = parse_qs(urlparse(str(request.url)).query)

    if "query" in query_params and query_params["query"]:
        # 获取查询参数
        query = query_params["query"][0]

        try:
            # 执行查询，增加超时处理
            logger.info(f"处理查询: {query}")
            
            # 使用asyncio.wait_for设置超时
            result = await asyncio.wait_for(
                agent.run(user_query=query),
                timeout=120.0  # 2分钟超时
            )

            # 构建HTML显示结果
            # 使用replace处理换行符
            formatted_result = result.replace('\n', '<br>')

            html_content = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>OpenManus - 咖啡馆查找结果</title>
                <style>
                    body {{
                        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                        color: #333;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }}
                    .container {{
                        max-width: 1000px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    header {{
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        color: #2c3e50;
                        padding: 20px;
                        text-align: center;
                        margin-bottom: 30px;
                        border-radius: 15px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    }}
                    .content-section {{
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        border-radius: 15px;
                        padding: 30px;
                        margin-bottom: 30px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.18);
                    }}
                    .result-content {{
                        font-size: 16px;
                        line-height: 1.8;
                    }}
                    .back-link {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 12px 24px;
                        background: linear-gradient(45deg, #667eea, #764ba2);
                        color: white;
                        text-decoration: none;
                        border-radius: 25px;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                    }}
                    .back-link:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
                    }}
                    .loading {{
                        text-align: center;
                        color: #666;
                        font-style: italic;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <header>
                        <h1>🤖 OpenManus AI 会面点推荐</h1>
                        <p>智能分析，精准推荐</p>
                    </header>
                    <div class="content-section">
                        <div class="result-content">
                            {formatted_result}
                        </div>
                        <a href="/workspace/meetspot_finder.html" class="back-link">← 返回查找页面</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
            
        except asyncio.TimeoutError:
            # 超时处理
            error_message = "请求处理超时，请稍后重试或简化您的查询"
            logger.warning(f"查询超时: {query}")
            
        except Exception as e:
            # 其他错误处理
            error_message = f"处理查询时出错: {str(e)}"
            logger.error(f"查询处理异常: {query}, 错误: {str(e)}")

        # 统一错误页面
        error_html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>处理错误 - OpenManus</title>
            <style>
                body {{
                    font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
                    background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0;
                    padding: 20px;
                }}
                .error-container {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 40px;
                    max-width: 500px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }}
                .error-icon {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                .error-title {{
                    color: #e74c3c;
                    margin-bottom: 15px;
                    font-size: 24px;
                }}
                .error-message {{
                    color: #666;
                    margin-bottom: 30px;
                    line-height: 1.6;
                }}
                .retry-link {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    text-decoration: none;
                    border-radius: 25px;
                    transition: all 0.3s ease;
                }}
                .retry-link:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h1 class="error-title">处理请求时出错</h1>
                <p class="error-message">{error_message}</p>
                <a href="/workspace/meetspot_finder.html" class="retry-link">返回查找页面</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)

    # 如果没有查询参数，重定向到会面点查找页面
    return RedirectResponse(url="/workspace/meetspot_finder.html")

@app.post("/api/find_meetspot")
async def find_meetspot(request: CafeRequest):
    """会面点查找API端点，带优化的错误处理和性能监控"""
    start_time = time.time()
    request_id = f"req_{int(time.time() * 1000)}"
    
    try:
        logger.info(f"[{request_id}] API请求开始: locations={request.locations}, keywords={request.keywords}")
        
        # 输入验证
        if not request.locations or len(request.locations) < 2:
            raise HTTPException(
                status_code=400, 
                detail="至少需要提供2个地点才能进行会面点推荐"
            )
        
        if len(request.locations) > 10:
            raise HTTPException(
                status_code=400, 
                detail="同时支持的地点数量不能超过10个"
            )
        
        # 创建推荐器实例
        recommender = CafeRecommender()

        # 执行推荐，设置超时
        result = await asyncio.wait_for(
            recommender.execute(
                locations=request.locations,
                keywords=request.keywords,
                user_requirements=request.user_requirements
            ),
            timeout=60.0  # 1分钟超时
        )

        # 从结果中提取HTML文件路径
        output_text = result.output
        html_path = None

        for line in output_text.split('\n'):
            if "HTML页面:" in line:
                html_path = line.split("HTML页面:")[1].strip()
                # 清理路径中的引号
                html_path = html_path.replace('"', '').replace("'", '')
                break

        if not html_path:
            logger.warning(f"[{request_id}] 无法生成HTML页面")
            raise HTTPException(
                status_code=500,
                detail="无法生成推荐结果页面，请检查输入的地点是否有效"
            )

        # 验证HTML文件是否存在
        full_html_path = os.path.join("workspace", "js_src", html_path)
        if not os.path.exists(full_html_path):
            logger.error(f"[{request_id}] HTML文件不存在: {full_html_path}")
            raise HTTPException(
                status_code=500,
                detail="推荐结果页面生成失败"
            )

        # 计算处理时间
        processing_time = time.time() - start_time
        logger.info(f"[{request_id}] API请求完成，耗时: {processing_time:.2f}秒")
        
        # 返回结果，包含元数据
        return JSONResponse(
            content={
                "success": True,
                "html_url": f"/workspace/js_src/{html_path}",
                "processing_time": processing_time,
                "request_id": request_id,
                "locations_count": len(request.locations),
                "keywords": request.keywords
            },
            headers={
                "X-Processing-Time": str(processing_time),
                "X-Request-ID": request_id
            }
        )
        
    except asyncio.TimeoutError:
        logger.error(f"[{request_id}] API请求超时")
        raise HTTPException(
            status_code=408,
            detail="请求处理超时，请检查网络连接或简化查询条件"
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
        
    except Exception as e:
        # 其他异常的统一处理
        processing_time = time.time() - start_time
        logger.error(f"[{request_id}] API请求异常: {str(e)}, 耗时: {processing_time:.2f}秒")
        
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)[:100]}..."  # 限制错误消息长度
        )

# 性能统计端点
@app.get("/api/stats")
async def get_performance_stats():
    """获取性能统计信息"""
    return {
        "performance": performance_stats,
        "current_time": time.time(),
        "uptime_seconds": time.time() - performance_stats["last_reset"],
        "requests_per_second": (
            performance_stats["total_requests"] / 
            (time.time() - performance_stats["last_reset"])
            if time.time() - performance_stats["last_reset"] > 0 else 0
        )
    }

if __name__ == "__main__":
    # 启动Web服务器
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)
