import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestStreamingEndpointValidation(unittest.TestCase):
    """Test input validation for streaming endpoints"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Valid test data
        self.valid_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51.5',
            'longitude': '-0.1',
            'music_genre': 'any'
        }

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_missing_birth_date(self, mock_get_client):
        """Test /stream-chart-analysis with missing birth_date"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['birth_date']
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('birth_date', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_missing_birth_time(self, mock_get_client):
        """Test /stream-chart-analysis with missing birth_time"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['birth_time']
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('birth_time', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_missing_timezone_offset(self, mock_get_client):
        """Test /stream-chart-analysis with missing timezone_offset"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['timezone_offset']
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('timezone_offset', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_missing_latitude(self, mock_get_client):
        """Test /stream-chart-analysis with missing latitude"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['latitude']
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('latitude', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_missing_longitude(self, mock_get_client):
        """Test /stream-chart-analysis with missing longitude"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['longitude']
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('longitude', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_multiple_missing_fields(self, mock_get_client):
        """Test /stream-chart-analysis with multiple missing fields"""
        mock_get_client.return_value = MagicMock()
        
        data = {
            'birth_date': '1988-08-08',
            'music_genre': 'any'
        }
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        # Should mention at least some of the missing fields
        error_msg = response_data['error']
        self.assertTrue(
            'birth_time' in error_msg or 
            'timezone_offset' in error_msg or 
            'latitude' in error_msg or 
            'longitude' in error_msg
        )

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_empty_string_fields(self, mock_get_client):
        """Test /stream-chart-analysis with empty string values"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        data['birth_date'] = ''
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('birth_date', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_null_fields(self, mock_get_client):
        """Test /stream-chart-analysis with null values"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        data['latitude'] = None
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('latitude', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_chart_analysis_zero_values_allowed(self, mock_get_client):
        """Test /stream-chart-analysis allows 0 values for numeric fields"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        data['timezone_offset'] = '0'
        data['latitude'] = '0'
        data['longitude'] = '0'
        
        response = self.app.post('/stream-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        # Should not get 400 error for zero values
        self.assertNotEqual(response.status_code, 400)

    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_missing_birth_date(self, mock_get_client):
        """Test /stream-full-chart-analysis with missing birth_date"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['birth_date']
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('birth_date', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_missing_birth_time(self, mock_get_client):
        """Test /stream-full-chart-analysis with missing birth_time"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['birth_time']
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('birth_time', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_missing_timezone_offset(self, mock_get_client):
        """Test /stream-full-chart-analysis with missing timezone_offset"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['timezone_offset']
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('timezone_offset', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_missing_latitude(self, mock_get_client):
        """Test /stream-full-chart-analysis with missing latitude"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['latitude']
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('latitude', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_missing_longitude(self, mock_get_client):
        """Test /stream-full-chart-analysis with missing longitude"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['longitude']
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('longitude', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_full_chart_analysis_empty_string_fields(self, mock_get_client):
        """Test /stream-full-chart-analysis with empty string values"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        data['birth_time'] = ''
        
        response = self.app.post('/stream-full-chart-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('birth_time', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_missing_birth_date(self, mock_get_client):
        """Test /stream-live-mas-analysis with missing birth_date"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['birth_date']
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('birth_date', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_missing_birth_time(self, mock_get_client):
        """Test /stream-live-mas-analysis with missing birth_time"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['birth_time']
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('birth_time', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_missing_timezone_offset(self, mock_get_client):
        """Test /stream-live-mas-analysis with missing timezone_offset"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['timezone_offset']
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('timezone_offset', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_missing_latitude(self, mock_get_client):
        """Test /stream-live-mas-analysis with missing latitude"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['latitude']
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('latitude', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_missing_longitude(self, mock_get_client):
        """Test /stream-live-mas-analysis with missing longitude"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        del data['longitude']
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('longitude', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_empty_string_fields(self, mock_get_client):
        """Test /stream-live-mas-analysis with empty string values"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        data['longitude'] = ''
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('longitude', response_data['error'])

    @patch('ai_service.get_client')
    def test_stream_live_mas_analysis_null_fields(self, mock_get_client):
        """Test /stream-live-mas-analysis with null values"""
        mock_get_client.return_value = MagicMock()
        
        data = self.valid_data.copy()
        data['timezone_offset'] = None
        
        response = self.app.post('/stream-live-mas-analysis',
                                data=json.dumps(data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('timezone_offset', response_data['error'])




if __name__ == '__main__':
    unittest.main()
