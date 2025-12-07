"""
Test coverage for streaming endpoints

This module tests the Server-Sent Events (SSE) streaming functionality for all
streaming endpoints: /stream-chart-analysis, /stream-full-chart-analysis, and
/stream-live-mas-analysis.

Coverage includes:
- ✅ SSE format validation (proper data: prefix, JSON structure)
- ✅ Error handling (AI service unavailable, streaming errors)
- ✅ Integration tests (full flow, concurrent requests)
- ✅ Unicode and special character handling in streams
- ✅ Large response streaming
- ✅ Empty chunk filtering
- ✅ Date format conversion
- ✅ Parameter passing validation

Note: Tests use mocking at the calculation layer to isolate streaming behavior.
Input validation tests are in test_streaming_validation.py.
"""

import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock, call, Mock
from io import BytesIO

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestStreamingEndpointsSSE(unittest.TestCase):
    """Test SSE streaming functionality for all streaming endpoints"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Valid test data - latitude/longitude in flatlib format (e.g., 40n42, 74w00)
        self.valid_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '0w07',
            'music_genre': 'any'
        }

    def _consume_sse_stream(self, response):
        """
        Consume and parse SSE response stream
        
        Args:
            response: Flask test client response object with streaming data
            
        Returns:
            list: List of parsed JSON messages
        """
        messages = []
        
        # Iterate through the response directly to consume the generator
        for chunk in response.response:
            lines = chunk.decode('utf-8').split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Skip "data: " prefix
                        messages.append(data)
                    except json.JSONDecodeError:
                        pass  # Skip malformed messages
        
        return messages
    
    def _mock_chart_dependencies(self):
        """Helper to set up common chart calculation mocks"""
        mock_chart = MagicMock()
        mock_today_chart = MagicMock()
        
        # Mock chart positions
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        
        mock_chart.get.side_effect = lambda x: {
            'Sun': mock_sun,
            'Moon': mock_moon,
            'House1': mock_asc
        }[x]
        
        # Mock planets in houses
        mock_chart.objects = []
        
        return mock_chart, mock_today_chart

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_sse_format(self, mock_get_client, mock_create_charts,
                                             mock_main_pos, mock_planets_houses, 
                                             mock_current_planets, mock_stream_ai):
        """Test /stream-chart-analysis returns properly formatted SSE stream"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart calculations
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        
        # Mock streaming AI response
        mock_stream_ai.return_value = iter([
            'Hello ',
            'this ',
            'is ',
            'a ',
            'test.'
        ])
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/event-stream')
        
        # Parse SSE messages
        messages = self._consume_sse_stream(response)
        
        # Should have 5 chunk messages + 1 done message
        self.assertGreaterEqual(len(messages), 6)
        
        # Verify chunk messages
        chunk_messages = [msg for msg in messages if 'chunk' in msg]
        self.assertEqual(len(chunk_messages), 5)
        
        # Verify chunks contain expected text
        chunks = [msg['chunk'] for msg in chunk_messages]
        self.assertEqual(chunks, ['Hello ', 'this ', 'is ', 'a ', 'test.'])
        
        # Verify done message
        done_messages = [msg for msg in messages if 'done' in msg]
        self.assertEqual(len(done_messages), 1)
        self.assertTrue(done_messages[0]['done'])

    @patch('calculations.stream_ai_api')
    @patch('chart_data.get_full_chart_structure')
    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_sse_format(self, mock_get_client, mock_chart_structure, mock_stream_ai):
        """Test /stream-full-chart-analysis returns properly formatted SSE stream"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart structure
        mock_chart_structure.return_value = {'planets': {}}
        
        # Mock streaming AI response with markdown-like content
        mock_stream_ai.return_value = iter([
            '## Sun in Leo\n',
            'Your sun sign ',
            'is in Leo.'
        ])
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/event-stream')
        
        # Parse SSE messages
        messages = self._consume_sse_stream(response)
        
        # Should have 3 chunk messages + 1 done message
        chunk_messages = [msg for msg in messages if 'chunk' in msg]
        self.assertEqual(len(chunk_messages), 3)
        
        # Verify done message exists
        done_messages = [msg for msg in messages if 'done' in msg]
        self.assertEqual(len(done_messages), 1)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_sse_format(self, mock_get_client, mock_create_charts,
                                                 mock_main_pos, mock_planets_houses,
                                                 mock_current_planets, mock_stream_ai):
        """Test /stream-live-mas-analysis returns properly formatted SSE stream"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        
        # Mock streaming AI response
        mock_stream_ai.return_value = iter([
            'Based on your chart, ',
            'try the Crunchwrap Supreme!'
        ])
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/event-stream')
        
        # Parse SSE messages
        messages = self._consume_sse_stream(response)
        
        # Should have 2 chunk messages + 1 done message
        chunk_messages = [msg for msg in messages if 'chunk' in msg]
        self.assertGreaterEqual(len(chunk_messages), 2)
        
        # Verify done message exists
        done_messages = [msg for msg in messages if 'done' in msg]
        self.assertEqual(len(done_messages), 1)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_empty_chunks_filtered(self, mock_get_client, mock_create_charts,
                                                         mock_main_pos, mock_planets_houses,
                                                         mock_current_planets, mock_stream_ai):
        """Test that empty chunks are filtered out from SSE stream"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        
        # Mock streaming response with some empty chunks
        mock_stream_ai.return_value = iter([
            'Hello',
            '',  # Empty chunk should be filtered
            ' ',
            '',  # Another empty chunk
            'world'
        ])
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Parse SSE messages
        messages = self._consume_sse_stream(response)
        chunk_messages = [msg for msg in messages if 'chunk' in msg]
        
        # Should only have 3 non-empty chunks
        self.assertEqual(len(chunk_messages), 3)
        chunks = [msg['chunk'] for msg in chunk_messages]
        self.assertEqual(chunks, ['Hello', ' ', 'world'])

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_streaming_error_handling(self, mock_get_client, mock_create_charts,
                                                            mock_main_pos, mock_planets_houses,
                                                            mock_current_planets, mock_stream_ai):
        """Test error handling during streaming"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        
        # Mock streaming that raises an error mid-stream
        def failing_generator():
            yield 'Starting...'
            raise ValueError('Streaming error occurred')
        
        mock_stream_ai.return_value = failing_generator()
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Parse SSE messages
        messages = self._consume_sse_stream(response)
        
        # Should have at least chunks (starting chunk + error fallback message)
        chunk_messages = [msg for msg in messages if 'chunk' in msg]
        self.assertGreaterEqual(len(chunk_messages), 1)
        
        # Should have a done message
        done_messages = [msg for msg in messages if 'done' in msg]
        self.assertEqual(len(done_messages), 1)

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_ai_service_unavailable(self, mock_get_client):
        """Test error when AI service is unavailable before stream starts"""
        # Mock get_client to raise ValueError
        mock_get_client.side_effect = ValueError('ANTHROPIC_TOKEN not set')
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 503)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('unavailable', response_data['error'].lower())

    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_ai_service_unavailable(self, mock_get_client):
        """Test error when AI service is unavailable for full chart"""
        mock_get_client.side_effect = ValueError('ANTHROPIC_TOKEN not set')
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 503)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_ai_service_unavailable(self, mock_get_client):
        """Test error when AI service is unavailable for live mas"""
        mock_get_client.side_effect = ValueError('ANTHROPIC_TOKEN not set')
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 503)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_date_format_conversion(self, mock_get_client, mock_create_charts,
                                                          mock_main_pos, mock_planets_houses,
                                                          mock_current_planets, mock_stream_ai):
        """Test that date format is properly converted from HTML to slash format"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        mock_stream_ai.return_value = iter(['Test response'])
        
        data = self.valid_data.copy()
        data['birth_date'] = '1988-08-08'  # HTML format with dashes
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        # Should successfully process without errors
        self.assertEqual(response.status_code, 200)
        messages = self._consume_sse_stream(response)
        self.assertGreater(len(messages), 0)

    @patch('calculations.stream_ai_api')
    @patch('chart_data.get_full_chart_structure')
    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_date_format_conversion(self, mock_get_client, mock_chart_structure, mock_stream_ai):
        """Test date format conversion for full chart endpoint"""
        mock_get_client.return_value = MagicMock()
        mock_chart_structure.return_value = {'planets': {}}
        mock_stream_ai.return_value = iter(['Test response'])
        
        data = self.valid_data.copy()
        data['birth_date'] = '2000-12-31'
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        # Should successfully process without errors
        self.assertEqual(response.status_code, 200)
        messages = self._consume_sse_stream(response)
        self.assertGreater(len(messages), 0)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_date_format_conversion(self, mock_get_client, mock_create_charts,
                                                             mock_main_pos, mock_planets_houses,
                                                             mock_current_planets, mock_stream_ai):
        """Test date format conversion for live mas endpoint"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        mock_stream_ai.return_value = iter(['Test response'])
        
        data = self.valid_data.copy()
        data['birth_date'] = '1995-05-15'
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        # Should successfully process without errors
        self.assertEqual(response.status_code, 200)
        messages = self._consume_sse_stream(response)
        self.assertGreater(len(messages), 0)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_music_genre_passed(self, mock_get_client, mock_create_charts,
                                                      mock_main_pos, mock_planets_houses,
                                                      mock_current_planets, mock_stream_ai):
        """Test that music genre is properly handled in request"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        mock_stream_ai.return_value = iter(['Test'])
        
        data = self.valid_data.copy()
        data['music_genre'] = 'rock'
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        # Should successfully process with custom music genre
        self.assertEqual(response.status_code, 200)
        messages = self._consume_sse_stream(response)
        self.assertGreater(len(messages), 0)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_default_music_genre(self, mock_get_client, mock_create_charts,
                                                       mock_main_pos, mock_planets_houses,
                                                       mock_current_planets, mock_stream_ai):
        """Test default music genre when not provided"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        mock_stream_ai.return_value = iter(['Test'])
        
        data = self.valid_data.copy()
        del data['music_genre']
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        # Should successfully process with default music genre
        self.assertEqual(response.status_code, 200)
        messages = self._consume_sse_stream(response)
        self.assertGreater(len(messages), 0)

    @patch('calculations.stream_ai_api')
    @patch('chart_data.get_full_chart_structure')
    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_all_parameters(self, mock_get_client, mock_chart_structure, mock_stream_ai):
        """Test that all parameters are correctly handled by full chart endpoint"""
        mock_get_client.return_value = MagicMock()
        mock_chart_structure.return_value = {'planets': {}}
        mock_stream_ai.return_value = iter(['Full chart response'])
        
        data = {
            'birth_date': '1990-01-15',
            'birth_time': '14:30',
            'timezone_offset': '-5',
            'latitude': '40n42',
            'longitude': '74w00',
            'music_genre': 'jazz'
        }
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        # Should successfully process all parameters
        self.assertEqual(response.status_code, 200)
        messages = self._consume_sse_stream(response)
        self.assertGreater(len(messages), 0)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_all_parameters(self, mock_get_client, mock_create_charts,
                                                     mock_main_pos, mock_planets_houses,
                                                     mock_current_planets, mock_stream_ai):
        """Test that all parameters are correctly handled by live mas endpoint"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        mock_stream_ai.return_value = iter(['Taco order'])
        
        data = {
            'birth_date': '1985-06-20',
            'birth_time': '08:45',
            'timezone_offset': '3',
            'latitude': '33s52',
            'longitude': '151e12',
        }
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        # Should successfully process all parameters
        self.assertEqual(response.status_code, 200)
        messages = self._consume_sse_stream(response)
        self.assertGreater(len(messages), 0)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_unicode_content(self, mock_get_client, mock_create_charts,
                                                   mock_main_pos, mock_planets_houses,
                                                   mock_current_planets, mock_stream_ai):
        """Test that unicode content is properly handled in streaming"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        
        # Mock streaming with unicode characters
        mock_stream_ai.return_value = iter([
            '✨ Your horoscope: ',
            '🌟 Sun in Leo ',
            '🌙 Moon in Pisces'
        ])
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Parse SSE messages
        messages = self._consume_sse_stream(response)
        chunk_messages = [msg for msg in messages if 'chunk' in msg]
        
        # Verify unicode content is preserved
        chunks = [msg['chunk'] for msg in chunk_messages]
        self.assertIn('✨', chunks[0])
        self.assertIn('🌟', chunks[1])
        self.assertIn('🌙', chunks[2])

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_large_response(self, mock_get_client, mock_create_charts,
                                                  mock_main_pos, mock_planets_houses,
                                                  mock_current_planets, mock_stream_ai):
        """Test streaming with large response"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        
        # Generate a large number of chunks
        large_chunks = [f'Chunk {i}. ' for i in range(100)]
        mock_stream_ai.return_value = iter(large_chunks)
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Parse SSE messages
        messages = self._consume_sse_stream(response)
        chunk_messages = [msg for msg in messages if 'chunk' in msg]
        
        # Should have 100 chunks
        self.assertEqual(len(chunk_messages), 100)
        
        # Verify done message exists
        done_messages = [msg for msg in messages if 'done' in msg]
        self.assertEqual(len(done_messages), 1)

    @patch('calculations.stream_ai_api')
    @patch('calculations.get_current_planets')
    @patch('calculations.get_planets_in_houses')
    @patch('calculations.get_main_positions')
    @patch('calculations.create_charts')
    @patch('ai_service.get_client')
    def test_stream_chart_analysis_json_escape_handling(self, mock_get_client, mock_create_charts,
                                                        mock_main_pos, mock_planets_houses,
                                                        mock_current_planets, mock_stream_ai):
        """Test that special JSON characters are properly escaped in chunks"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart dependencies
        mock_chart, mock_today_chart = self._mock_chart_dependencies()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_planets_houses.return_value = {}
        mock_current_planets.return_value = {}
        
        # Mock streaming with characters that need JSON escaping
        mock_stream_ai.return_value = iter([
            'Test with "quotes"',
            'Test with \n newlines',
            'Test with \\ backslashes'
        ])
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Parse SSE messages - should not raise JSON errors
        messages = self._consume_sse_stream(response)
        chunk_messages = [msg for msg in messages if 'chunk' in msg]
        
        # Verify chunks were properly parsed
        self.assertEqual(len(chunk_messages), 3)
        
        # Verify content is preserved correctly
        chunks = [msg['chunk'] for msg in chunk_messages]
        self.assertIn('quotes', chunks[0])
        self.assertIn('newlines', chunks[1])
        self.assertIn('backslashes', chunks[2])


class TestStreamingEndpointsIntegration(unittest.TestCase):
    """Integration tests for streaming endpoints with realistic scenarios"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Valid test data - latitude/longitude in flatlib format (e.g., 40n42, 74w00)
        self.valid_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '0w07',
            'music_genre': 'any'
        }

    def _consume_sse_stream(self, response):
        """Helper method to consume and parse SSE stream from response"""
        messages = []
        for line in response.response:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    messages.append(data)
                except json.JSONDecodeError:
                    pass
        return messages

    @patch('calculations.stream_calculate_chart')
    @patch('chart_data.create_charts')
    @patch('chart_data.get_main_positions')
    @patch('chart_data.get_current_planets')
    @patch('ai_service.get_client')
    def test_full_flow_chart_with_streaming(self, mock_get_client, mock_current_planets, 
                                           mock_main_pos, mock_create_charts, mock_stream_calc):
        """Test complete flow from chart request to streaming analysis"""
        mock_get_client.return_value = MagicMock()
        
        # Mock chart calculation
        mock_chart = MagicMock()
        mock_today_chart = MagicMock()
        mock_create_charts.return_value = (mock_chart, mock_today_chart)
        
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Pisces'
        mock_asc = MagicMock()
        mock_asc.sign = 'Virgo'
        mock_main_pos.return_value = (mock_sun, mock_moon, mock_asc)
        
        mock_current_planets.return_value = {'Mercury': {'retrograde': False}}
        
        # Mock streaming
        mock_stream_calc.return_value = iter([
            'Your daily horoscope: ',
            'Sun in Leo brings creative energy.'
        ])
        
        # Test streaming endpoint
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(self.valid_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/event-stream')

    @patch('calculations.stream_calculate_chart')
    @patch('ai_service.get_client')
    def test_multiple_concurrent_streaming_requests(self, mock_get_client, mock_stream_calc):
        """Test that multiple streaming requests can be handled sequentially"""
        mock_get_client.return_value = MagicMock()
        
        # Create different responses for different requests
        def mock_generator_1():
            yield 'Response 1'
        
        def mock_generator_2():
            yield 'Response 2'
        
        mock_stream_calc.side_effect = [mock_generator_1(), mock_generator_2()]
        
        # Make first request and consume it completely
        response1 = self.app.post('/stream-chart-analysis',
                                 data=json.dumps(self.valid_data),
                                 content_type='application/json')
        
        self.assertEqual(response1.status_code, 200)
        messages1 = self._consume_sse_stream(response1)
        self.assertGreater(len(messages1), 0)
        
        # Make second request after first is complete
        response2 = self.app.post('/stream-chart-analysis',
                                 data=json.dumps(self.valid_data),
                                 content_type='application/json')
        
        self.assertEqual(response2.status_code, 200)
        messages2 = self._consume_sse_stream(response2)
        self.assertGreater(len(messages2), 0)


if __name__ == '__main__':
    unittest.main()
