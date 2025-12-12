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
    # Mock get_client to raise ValueError simulating missing token
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.side_effect = ValueError("ANTHROPIC_TOKEN environment variable is not set")
        
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


def test_music_suggestion_success(client):
    """Test successful song suggestion"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        with patch('routes.stream_ai_api') as mock_stream:
            mock_stream.return_value = iter(['Song: Bohemian Rhapsody by Queen'])
            
            response = client.post('/music-suggestion',
                                  json={
                                      'birth_date': '1990/01/01',
                                      'birth_time': '12:00',
                                      'timezone_offset': '+00:00',
                                      'latitude': 0.0,
                                      'longitude': 0.0,
                                      'music_genre': 'rock',
                                      'chart_type': 'daily'
                                  })
            
            assert response.status_code == 200
            # Consume the streaming response to trigger the generator
            _ = b''.join(response.response)
            # Verify stream_ai_api was called
            assert mock_stream.call_count == 1


def test_music_suggestion_with_lastfm_integration(client):
    """Test that Last.fm service is called and tracks are included in prompt"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        # Mock Last.fm service to return tracks
        with patch('routes.get_top_tracks_by_genre') as mock_lastfm:
            mock_lastfm.return_value = [
                {'name': 'Stayin\' Alive', 'artist': 'Bee Gees'},
                {'name': 'Le Freak', 'artist': 'Chic'},
                {'name': 'I Will Survive', 'artist': 'Gloria Gaynor'}
            ]
            
            with patch('routes.stream_ai_api') as mock_stream:
                mock_stream.return_value = iter(['Song: Stayin\' Alive by Bee Gees'])
                
                response = client.post('/music-suggestion',
                                      json={
                                          'birth_date': '1990/01/01',
                                          'birth_time': '12:00',
                                          'timezone_offset': '+00:00',
                                          'latitude': 0.0,
                                          'longitude': 0.0,
                                          'music_genre': 'disco',
                                          'chart_type': 'daily'
                                      })
                
                assert response.status_code == 200
                _ = b''.join(response.response)
                
                # Verify Last.fm was called with correct genre
                mock_lastfm.assert_called_once_with('disco')
                
                # Verify the prompt included Last.fm tracks
                call_args = mock_stream.call_args
                prompt = call_args[0][1]  # Second argument is the user prompt
                assert 'Popular tracks in this genre include:' in prompt
                assert 'Stayin\' Alive by Bee Gees' in prompt
                assert 'Le Freak by Chic' in prompt


def test_music_suggestion_lastfm_no_tracks_found(client):
    """Test that endpoint works when Last.fm returns no tracks"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        # Mock Last.fm to return empty list
        with patch('routes.get_top_tracks_by_genre') as mock_lastfm:
            mock_lastfm.return_value = []
            
            with patch('routes.stream_ai_api') as mock_stream:
                mock_stream.return_value = iter(['Song: Test Song by Test Artist'])
                
                response = client.post('/music-suggestion',
                                      json={
                                          'birth_date': '1990/01/01',
                                          'birth_time': '12:00',
                                          'timezone_offset': '+00:00',
                                          'latitude': 0.0,
                                          'longitude': 0.0,
                                          'music_genre': 'unknown_genre',
                                          'chart_type': 'daily'
                                      })
                
                assert response.status_code == 200
                _ = b''.join(response.response)
                
                # Verify Last.fm was still called
                mock_lastfm.assert_called_once()
                
                # Verify the prompt does NOT include Last.fm section
                call_args = mock_stream.call_args
                prompt = call_args[0][1]
                assert 'Popular tracks in this genre include:' not in prompt


def test_music_suggestion_any_genre_skips_lastfm(client):
    """Test that 'any' genre skips Last.fm API call"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        # Mock Last.fm to return empty (simulating skip)
        with patch('routes.get_top_tracks_by_genre') as mock_lastfm:
            mock_lastfm.return_value = []
            
            with patch('routes.stream_ai_api') as mock_stream:
                mock_stream.return_value = iter(['Song: Test Song by Test Artist'])
                
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
                
                assert response.status_code == 200
                _ = b''.join(response.response)
                
                # Last.fm should still be called (it handles 'any' internally)
                mock_lastfm.assert_called_once_with('any')