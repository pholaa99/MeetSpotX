# MeetSpot Tests

This directory contains the test suite for MeetSpot.

## Test Structure

- `test_api.py` - API endpoint tests
- `test_recommender.py` - Recommendation algorithm tests
- `test_integration.py` - Integration tests

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ -v --cov=app
```

## Test Requirements

Make sure to install test dependencies:

```bash
pip install pytest pytest-asyncio httpx
```
