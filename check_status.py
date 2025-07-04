#!/usr/bin/env python3
import requests
import json
import time

print("等待 Vercel 部署完成...")
time.sleep(45)

try:
    print("🔍 检查 Vercel 状态...")
    response = requests.get("https://meetspotagent.vercel.app/vercel-status", timeout=10)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 详细状态:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ 检查失败: {e}")
    
    # 尝试主页
    try:
        print("\n🔍 检查主页...")
        response = requests.get("https://meetspotagent.vercel.app/", timeout=10)
        print(f"主页状态码: {response.status_code}")
        if "错误" in response.text or "error" in response.text.lower():
            print("⚠️ 主页显示错误信息")
        else:
            print("✅ 主页正常加载")
    except Exception as e2:
        print(f"❌ 主页检查失败: {e2}")
