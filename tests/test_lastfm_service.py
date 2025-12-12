"""
Tests for the Last.fm service integration
"""

from unittest.mock import patch, MagicMock
from lastfm_service import get_top_tracks_by_genre, format_tracks_for_prompt


class TestGetTopTracksByGenre:
    """Tests for get_top_tracks_by_genre function"""
    
    def test_no_api_key_returns_empty_list(self):
        """Test that missing API key returns empty list"""
        with patch('lastfm_service.LASTFM_API_KEY', None):
            result = get_top_tracks_by_genre('rock')
            assert result == []
    
    def test_any_genre_returns_empty_list(self):
        """Test that 'any' genre returns empty list"""
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            result = get_top_tracks_by_genre('any')
            assert result == []
    
    def test_empty_genre_returns_empty_list(self):
        """Test that empty genre returns empty list"""
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            result = get_top_tracks_by_genre('')
            assert result == []
    
    def test_successful_api_call(self):
        """Test successful API call with valid response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'tracks': {
                'track': [
                    {
                        'name': 'Stayin\' Alive',
                        'artist': {'name': 'Bee Gees'}
                    },
                    {
                        'name': 'Le Freak',
                        'artist': {'name': 'Chic'}
                    },
                    {
                        'name': 'I Will Survive',
                        'artist': {'name': 'Gloria Gaynor'}
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get', return_value=mock_response) as mock_get:
                result = get_top_tracks_by_genre('disco', limit=10)
                
                # Verify API was called correctly
                mock_get.assert_called_once()
                call_args = mock_get.call_args
                assert call_args[1]['params']['method'] == 'tag.gettoptracks'
                assert call_args[1]['params']['tag'] == 'disco'
                assert call_args[1]['params']['api_key'] == 'test_key'
                assert call_args[1]['params']['format'] == 'json'
                assert call_args[1]['params']['limit'] == 10
                
                # Verify response
                assert len(result) == 3
                assert result[0] == {'name': 'Stayin\' Alive', 'artist': 'Bee Gees'}
                assert result[1] == {'name': 'Le Freak', 'artist': 'Chic'}
                assert result[2] == {'name': 'I Will Survive', 'artist': 'Gloria Gaynor'}
    
    def test_api_call_respects_limit(self):
        """Test that limit parameter is enforced"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'tracks': {'track': []}}
        mock_response.raise_for_status = MagicMock()
        
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get', return_value=mock_response) as mock_get:
                get_top_tracks_by_genre('rock', limit=5)
                
                call_args = mock_get.call_args
                assert call_args[1]['params']['limit'] == 5
    
    def test_api_call_max_limit_50(self):
        """Test that limit is capped at 50"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'tracks': {'track': []}}
        mock_response.raise_for_status = MagicMock()
        
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get', return_value=mock_response) as mock_get:
                get_top_tracks_by_genre('rock', limit=100)
                
                call_args = mock_get.call_args
                assert call_args[1]['params']['limit'] == 50
    
    def test_handles_string_artist_format(self):
        """Test handling of artist as string (alternative API format)"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'tracks': {
                'track': [
                    {
                        'name': 'Test Song',
                        'artist': 'Test Artist'  # String format instead of dict
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get', return_value=mock_response):
                result = get_top_tracks_by_genre('rock')
                
                assert len(result) == 1
                assert result[0] == {'name': 'Test Song', 'artist': 'Test Artist'}
    
    def test_filters_incomplete_tracks(self):
        """Test that tracks without name or artist are filtered out"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'tracks': {
                'track': [
                    {'name': 'Complete Song', 'artist': {'name': 'Complete Artist'}},
                    {'name': '', 'artist': {'name': 'Artist Only'}},
                    {'name': 'Song Only', 'artist': {'name': ''}},
                    {'artist': {'name': 'No Name Track'}},
                    {'name': 'Valid Song', 'artist': {'name': 'Valid Artist'}}
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get', return_value=mock_response):
                result = get_top_tracks_by_genre('rock')
                
                assert len(result) == 2
                assert result[0] == {'name': 'Complete Song', 'artist': 'Complete Artist'}
                assert result[1] == {'name': 'Valid Song', 'artist': 'Valid Artist'}
    
    def test_no_tracks_in_response(self):
        """Test handling of response with no tracks"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'tracks': {}}
        mock_response.raise_for_status = MagicMock()
        
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get', return_value=mock_response):
                result = get_top_tracks_by_genre('unknown_genre')
                
                assert result == []
    
    def test_api_timeout(self):
        """Test handling of API timeout"""
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get') as mock_get:
                import requests
                mock_get.side_effect = requests.exceptions.Timeout()
                
                result = get_top_tracks_by_genre('rock')
                
                assert result == []
    
    def test_api_request_error(self):
        """Test handling of request errors"""
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get') as mock_get:
                import requests
                mock_get.side_effect = requests.exceptions.RequestException("Network error")
                
                result = get_top_tracks_by_genre('rock')
                
                assert result == []
    
    def test_invalid_json_response(self):
        """Test handling of invalid JSON response"""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get', return_value=mock_response):
                result = get_top_tracks_by_genre('rock')
                
                assert result == []
    
    def test_genre_sanitization(self):
        """Test that genre is sanitized (stripped and lowercased)"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'tracks': {'track': []}}
        mock_response.raise_for_status = MagicMock()
        
        with patch('lastfm_service.LASTFM_API_KEY', 'test_key'):
            with patch('lastfm_service.requests.get', return_value=mock_response) as mock_get:
                get_top_tracks_by_genre('  Rock Music  ')
                
                call_args = mock_get.call_args
                assert call_args[1]['params']['tag'] == 'rock music'


class TestFormatTracksForPrompt:
    """Tests for format_tracks_for_prompt function"""
    
    def test_empty_tracks_returns_empty_string(self):
        """Test that empty track list returns empty string"""
        result = format_tracks_for_prompt([])
        assert result == ""
    
    def test_formats_single_track(self):
        """Test formatting a single track"""
        tracks = [{'name': 'Test Song', 'artist': 'Test Artist'}]
        result = format_tracks_for_prompt(tracks)
        
        assert 'Popular tracks in this genre include:' in result
        assert '- Test Song by Test Artist' in result
    
    def test_formats_multiple_tracks(self):
        """Test formatting multiple tracks"""
        tracks = [
            {'name': 'Song 1', 'artist': 'Artist 1'},
            {'name': 'Song 2', 'artist': 'Artist 2'},
            {'name': 'Song 3', 'artist': 'Artist 3'}
        ]
        result = format_tracks_for_prompt(tracks)
        
        assert 'Popular tracks in this genre include:' in result
        assert '- Song 1 by Artist 1' in result
        assert '- Song 2 by Artist 2' in result
        assert '- Song 3 by Artist 3' in result
    
    def test_respects_limit_parameter(self):
        """Test that limit parameter restricts number of tracks"""
        tracks = [
            {'name': f'Song {i}', 'artist': f'Artist {i}'}
            for i in range(1, 11)
        ]
        result = format_tracks_for_prompt(tracks, limit=3)
        
        assert '- Song 1 by Artist 1' in result
        assert '- Song 2 by Artist 2' in result
        assert '- Song 3 by Artist 3' in result
        assert '- Song 4 by Artist 4' not in result
    
    def test_default_limit_is_20(self):
        """Test that default limit is 20 tracks"""
        tracks = [
            {'name': f'Song {i}', 'artist': f'Artist {i}'}
            for i in range(1, 25)
        ]
        result = format_tracks_for_prompt(tracks)
        
        # Should include first 20
        assert '- Song 20 by Artist 20' in result
        # Should not include 21st
        assert '- Song 21 by Artist 21' not in result
    
    def test_handles_fewer_tracks_than_limit(self):
        """Test handling when tracks list is smaller than limit"""
        tracks = [
            {'name': 'Song 1', 'artist': 'Artist 1'},
            {'name': 'Song 2', 'artist': 'Artist 2'}
        ]
        result = format_tracks_for_prompt(tracks, limit=5)
        
        assert '- Song 1 by Artist 1' in result
        assert '- Song 2 by Artist 2' in result
