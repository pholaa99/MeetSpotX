#!/usr/bin/env python3
"""
测试聚点推荐功能
"""
import asyncio
from app.tool.meetspot_recommender import CafeRecommender

async def test_meetspot():
    """测试聚点推荐功能"""
    print("🚀 开始测试聚点推荐功能...")
    
    # 创建推荐工具实例
    recommender = CafeRecommender()
    
    # 测试数据
    locations = ["北京市朝阳区望京SOHO", "北京市海淀区中关村"]
    keywords = "咖啡馆"
    user_requirements = "环境安静，适合商务会谈"
    
    print(f"📍 地点列表: {locations}")
    print(f"🔍 搜索关键词: {keywords}")
    print(f"📝 用户需求: {user_requirements}")
    print("\n" + "="*50)
    
    try:
        # 执行推荐
        result = await recommender.execute(
            locations=locations,
            keywords=keywords,
            user_requirements=user_requirements
        )
        
        print("✅ 推荐完成!")
        print(f"📄 结果: {result.output}")
        
        if result.artifacts:
            print(f"📎 生成的文件: {list(result.artifacts.keys())}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_meetspot())
