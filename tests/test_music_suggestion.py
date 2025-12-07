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


def test_music_suggestion_first_attempt_success(client):
    """Test successful song suggestion on first attempt"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        with patch('routes.stream_ai_api') as mock_stream:
            mock_stream.return_value = iter(['Song: Bohemian Rhapsody by Queen'])
            
            with patch('routes.verify_song_exists') as mock_verify:
                mock_verify.return_value = {'is_real': True, 'explanation': 'Valid song'}
                
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
                # Verify stream_ai_api was called only once
                assert mock_stream.call_count == 1
                # Verify verify_song_exists was called once
                assert mock_verify.call_count == 1


def test_music_suggestion_retry_on_verification_failure(client):
    """Test that the endpoint retries when song verification fails"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        with patch('routes.stream_ai_api') as mock_stream:
            # First attempt returns fake song, second returns real song
            mock_stream.side_effect = [
                iter(['Song: Fake Song by Fake Artist']),
                iter(['Song: Yesterday by The Beatles'])
            ]
            
            with patch('routes.verify_song_exists') as mock_verify:
                # First verification fails, second succeeds
                mock_verify.side_effect = [
                    {'is_real': False, 'explanation': 'Song not found'},
                    {'is_real': True, 'explanation': 'Valid song'}
                ]
                
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
                # Consume the streaming response to trigger the generator
                _ = b''.join(response.response)
                # Should have called stream_ai_api twice (1 initial + 1 retry)
                assert mock_stream.call_count == 2
                # Should have called verify_song_exists twice
                assert mock_verify.call_count == 2
def test_music_suggestion_max_retries_exceeded(client):
    """Test that the endpoint returns empty string after 3 failed attempts"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        with patch('routes.stream_ai_api') as mock_stream:
            # All attempts return fake songs
            mock_stream.side_effect = [
                iter(['Song: Fake Song 1 by Artist 1']),
                iter(['Song: Fake Song 2 by Artist 2']),
                iter(['Song: Fake Song 3 by Artist 3'])
            ]
            
            with patch('routes.verify_song_exists') as mock_verify:
                # All verifications fail
                mock_verify.return_value = {'is_real': False, 'explanation': 'Song not found'}
                
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
                # Consume the streaming response to trigger the generator
                data = b''.join(response.response).decode('utf-8')
                # Should have called stream_ai_api 3 times (max attempts)
                assert mock_stream.call_count == 3
                # Should have called verify_song_exists 3 times
                assert mock_verify.call_count == 3
                
                # Verify empty content was returned
                assert '"verified": false' in data.lower()
                assert '"content": ""' in data
def test_music_suggestion_no_response_from_ai(client):
    """Test handling when AI returns no response"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        with patch('routes.stream_ai_api') as mock_stream:
            # Return empty responses for all attempts
            mock_stream.side_effect = [
                iter([]),
                iter([]),
                iter([])
            ]
            
            with patch('routes.verify_song_exists') as mock_verify:
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
                # Consume the streaming response to trigger the generator
                _ = b''.join(response.response)
                # Should have tried 3 times
                assert mock_stream.call_count == 3
                # Verify was never called since we got no responses
                assert mock_verify.call_count == 0
def test_music_suggestion_third_attempt_success(client):
    """Test successful song suggestion on third attempt"""
    with patch('ai_service.get_client') as mock_get_client:
        mock_get_client.return_value = MagicMock()
        
        with patch('routes.stream_ai_api') as mock_stream:
            # First two fail, third succeeds
            mock_stream.side_effect = [
                iter(['Song: Fake Song 1 by Artist 1']),
                iter(['Song: Fake Song 2 by Artist 2']),
                iter(['Song: Imagine by John Lennon'])
            ]
            
            with patch('routes.verify_song_exists') as mock_verify:
                # First two verifications fail, third succeeds
                mock_verify.side_effect = [
                    {'is_real': False, 'explanation': 'Not found'},
                    {'is_real': False, 'explanation': 'Not found'},
                    {'is_real': True, 'explanation': 'Valid song'}
                ]
                
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
                # Consume the streaming response to trigger the generator
                _ = b''.join(response.response)
                # Should have called stream_ai_api 3 times
                assert mock_stream.call_count == 3
                # Should have called verify_song_exists 3 times
                assert mock_verify.call_count == 3