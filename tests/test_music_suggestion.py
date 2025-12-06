"""
Tests for the async music suggestion endpoint
"""
import pytest
from routes import app
import json


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_music_suggestion_endpoint_exists(client):
    """Test that the music suggestion endpoint exists and accepts POST requests"""
    response = client.post('/music-suggestion', 
                          json={
                              'birth_date': '1990/01/01',
                              'birth_time': '12:00',
                              'timezone_offset': '+00:00',
                              'latitude': 0.0,
                              'longitude': 0.0,
                              'music_genre': 'any',
                              'chart_type': 'daily'
                          })
    
    # Should return 200 OK (streaming response)
    assert response.status_code == 200
    assert response.mimetype == 'text/event-stream'


def test_music_suggestion_missing_data(client):
    """Test that the endpoint handles missing data gracefully"""
    response = client.post('/music-suggestion', json={})
    
    # Should return error
    assert response.status_code == 500


def test_music_suggestion_invalid_method(client):
    """Test that the endpoint only accepts POST requests"""
    response = client.get('/music-suggestion')
    
    # Should return 405 Method Not Allowed
    assert response.status_code == 405
