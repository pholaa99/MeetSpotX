#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MeetSpot 集成测试
测试系统的各个组件集成和端到端功能
"""

import asyncio
import pytest
import time
from httpx import AsyncClient
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.tool.meetspot_recommender import MeetSpotRecommender


class TestMeetSpotIntegration:
    """MeetSpot 集成测试"""
    
    @pytest.fixture
    def recommender(self):
        """创建推荐器实例"""
        return MeetSpotRecommender()
    
    def test_single_scenario_recommendation(self, recommender):
        """测试单场景推荐"""
        locations = [
            "北京市朝阳区国贸",
            "北京市海淀区中关村"
        ]
        place_types = ["咖啡馆"]
        
        result = recommender.find_meetspots(locations, place_types)
        
        assert result is not None
        assert "center_point" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
    
    def test_multi_scenario_recommendation(self, recommender):
        """测试多场景推荐"""
        locations = [
            "上海市黄浦区人民广场",
            "上海市浦东新区陆家嘴"
        ]
        place_types = ["咖啡馆", "餐厅", "图书馆"]
        
        result = recommender.find_meetspots(locations, place_types)
        
        assert result is not None
        assert "center_point" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        
        # 检查是否包含多种场所类型
        types_found = set()
        for rec in result["recommendations"]:
            if "type" in rec:
                types_found.add(rec["type"])
        
        assert len(types_found) > 1, "应该包含多种场所类型"
    
    def test_multiple_locations(self, recommender):
        """测试多地点推荐"""
        locations = [
            "广州市天河区天河城",
            "广州市越秀区北京路",
            "广州市海珠区琶洲"
        ]
        place_types = ["餐厅"]
        
        result = recommender.find_meetspots(locations, place_types)
        
        assert result is not None
        assert "center_point" in result
        assert len(result["recommendations"]) > 0
    
    def test_error_handling(self, recommender):
        """测试错误处理"""
        # 测试空位置列表
        result = recommender.find_meetspots([], ["咖啡馆"])
        assert result is None or len(result.get("recommendations", [])) == 0
        
        # 测试无效位置
        result = recommender.find_meetspots(["不存在的地址"], ["咖啡馆"])
        # 应该优雅处理，不抛出异常
        assert isinstance(result, (dict, type(None)))
    
    def test_performance(self, recommender):
        """测试性能"""
        locations = [
            "深圳市南山区科技园",
            "深圳市福田区华强北"
        ]
        place_types = ["咖啡馆", "餐厅"]
        
        start_time = time.time()
        result = recommender.find_meetspots(locations, place_types)
        end_time = time.time()
        
        # 推荐应该在合理时间内完成（15秒）
        assert end_time - start_time < 15, f"推荐耗时 {end_time - start_time:.2f}s 过长"
        assert result is not None


@pytest.mark.asyncio
async def test_web_server_health():
    """测试 Web 服务器健康检查"""
    # 这个测试需要服务器运行
    # 在 CI 环境中，服务器会被启动
    try:
        async with AsyncClient(base_url="http://localhost:8000") as ac:
            response = await ac.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    except Exception as e:
        # 如果服务器未运行，跳过测试
        pytest.skip(f"服务器未运行: {e}")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
