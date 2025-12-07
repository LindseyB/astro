"""
Tests for the async music suggestion endpoint
"""
import os
import pytest
from routes import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_music_suggestion_endpoint_exists(client):
    """Test that the music suggestion endpoint exists and accepts POST requests"""
    # Mock the get_client function to avoid needing a real token
    with patch('ai_service.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock the stream_ai_api to return some test data
        with patch('ai_service.stream_ai_api') as mock_stream:
            mock_stream.return_value = iter(['Song: Test Song by Test Artist'])
            
            # Mock verify_song_exists to avoid additional API calls
            with patch('ai_service.verify_song_exists') as mock_verify:
                mock_verify.return_value = {'is_real': True, 'explanation': 'Test'}
                
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
    # Mock the get_client function to avoid token validation error
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        response = client.post('/music-suggestion', json={})
        
        # Should return error for missing data (400) not token error (503)
        assert response.status_code == 400


def test_music_suggestion_without_token(client):
    """Test that the endpoint returns 503 when AI token is not available"""
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
    
    # Should return 503 Service Unavailable when token is not set
    assert response.status_code == 503
    data = response.get_json()
    assert 'error' in data
    assert 'unavailable' in data['error'].lower()


def test_music_suggestion_invalid_method(client):
    """Test that the endpoint only accepts POST requests"""
    response = client.get('/music-suggestion')
    
    # Should return 405 Method Not Allowed
    assert response.status_code == 405
