import sys
import os

# 添加项目根目录到Python路径  
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from web_server import app
    
    # Vercel需要的应用实例
    application = app
    
    # 备用导出
    def handler(request, context=None):
        return app
        
except ImportError as e:
    # 如果导入失败，创建一个简单的错误响应
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    fallback_app = FastAPI()
    
    @fallback_app.get("/")
    async def error_handler():
        return JSONResponse(
            status_code=500,
            content={
                "error": "Import failed", 
                "details": str(e),
                "project_root": project_root
            }
        )
    
    application = fallback_app
