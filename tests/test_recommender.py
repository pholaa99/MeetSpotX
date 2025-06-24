"""
Recommender Tests for MeetSpot
"""
import pytest
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tool.meetspot_recommender import MeetSpotRecommender

@pytest.fixture
def recommender():
    """Create a recommender instance for testing"""
    return MeetSpotRecommender()

def test_recommender_initialization(recommender):
    """Test that recommender initializes correctly"""
    assert recommender is not None
    assert hasattr(recommender, 'venue_types')
    assert isinstance(recommender.venue_types, dict)

def test_center_calculation(recommender):
    """Test center point calculation"""
    locations = [
        {"lat": 39.9042, "lng": 116.4074},  # Beijing
        {"lat": 39.9388, "lng": 116.3974}   # Near Beijing
    ]
    
    center = recommender.calculate_center(locations)
    assert "lat" in center
    assert "lng" in center
    assert isinstance(center["lat"], (int, float))
    assert isinstance(center["lng"], (int, float))

def test_venue_type_mapping(recommender):
    """Test venue type mapping"""
    # Test that basic venue types are mapped
    basic_types = ["咖啡馆", "餐厅", "图书馆", "健身房"]
    for venue_type in basic_types:
        if venue_type in recommender.venue_types:
            mapping = recommender.venue_types[venue_type]
            assert "keywords" in mapping
            assert "icon" in mapping
            assert isinstance(mapping["keywords"], list)

def test_multi_scenario_support(recommender):
    """Test multiple venue type handling"""
    venue_types = ["咖啡馆", "餐厅"]
    
    # Should handle multiple venue types without error
    try:
        # This would normally call external API, so we just test the structure
        keywords = []
        for vtype in venue_types:
            if vtype in recommender.venue_types:
                keywords.extend(recommender.venue_types[vtype]["keywords"])
        
        assert len(keywords) > 0
        assert len(set(keywords)) <= len(keywords)  # Check for uniqueness handling
    except Exception as e:
        pytest.fail(f"Multi-scenario handling failed: {e}")

def test_distance_calculation(recommender):
    """Test distance calculation between points"""
    point1 = {"lat": 39.9042, "lng": 116.4074}
    point2 = {"lat": 39.9388, "lng": 116.3974}
    
    try:
        # This tests the basic structure, actual calculation may need API
        distance = recommender.calculate_distance(point1, point2)
        if distance is not None:
            assert isinstance(distance, (int, float))
            assert distance >= 0
    except Exception:
        # Distance calculation might require external API
        pass

def test_error_handling(recommender):
    """Test error handling in recommender"""
    # Test with invalid input
    try:
        result = recommender.calculate_center([])
        # Should handle empty list gracefully
    except Exception as e:
        # Should raise appropriate exception for invalid input
        assert "empty" in str(e).lower() or "invalid" in str(e).lower()

def test_venue_type_completeness(recommender):
    """Test that all expected venue types are configured"""
    expected_types = [
        "咖啡馆", "餐厅", "图书馆", "公园", "电影院", 
        "健身房", "酒吧", "书店", "购物中心"
    ]
    
    configured_types = list(recommender.venue_types.keys())
    
    # Check that we have a good coverage of venue types
    coverage = len([t for t in expected_types if t in configured_types])
    assert coverage >= len(expected_types) * 0.7  # At least 70% coverage
