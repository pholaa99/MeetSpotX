import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_server import app

# Vercel入口点
def handler(request):
    return app

# 直接导出app供Vercel使用
application = app
