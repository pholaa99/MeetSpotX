"""
API Tests for MeetSpot
"""
import pytest
import httpx
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_server import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_root_redirect():
    """Test that root redirects to the main page"""
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/workspace/meetspot_finder.html"

def test_static_file_serving():
    """Test that static HTML files are served correctly"""
    response = client.get("/workspace/meetspot_finder.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_api_recommend_validation():
    """Test API parameter validation"""
    # Test missing parameters
    response = client.post("/api/recommend", json={})
    assert response.status_code == 422
    
    # Test invalid parameters
    response = client.post("/api/recommend", json={
        "locations": ["invalid"],  # Should be at least 2 locations
        "venue_types": ["咖啡馆"]
    })
    assert response.status_code == 400

def test_api_recommend_basic():
    """Test basic recommendation functionality"""
    response = client.post("/api/recommend", json={
        "locations": ["北京天安门", "北京西站"],
        "venue_types": ["咖啡馆"],
        "special_requirements": []
    })
    
    # Should not crash, even if external API is not available
    assert response.status_code in [200, 500]  # 500 if API key not configured
    
    if response.status_code == 200:
        data = response.json()
        assert "center_point" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

def test_performance_stats():
    """Test that performance stats are included in responses"""
    response = client.post("/api/recommend", json={
        "locations": ["测试地点1", "测试地点2"],
        "venue_types": ["咖啡馆"]
    })
    
    if response.status_code == 200:
        data = response.json()
        assert "performance_stats" in data
        stats = data["performance_stats"]
        assert "request_duration_ms" in stats
        assert "timestamp" in stats
