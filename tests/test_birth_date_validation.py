import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock swisseph before importing any module that transitively depends on it
if 'swisseph' not in sys.modules:
    sys.modules['swisseph'] = MagicMock()

from main import app


class TestFormatBirthDateForCalculations(unittest.TestCase):
    """Unit tests for the _format_birth_date_for_calculations helper function"""

    def setUp(self):
        from routes import _format_birth_date_for_calculations
        self.format_birth_date = _format_birth_date_for_calculations

    def test_yyyy_mm_dd_format_is_normalized_to_slashes(self):
        """YYYY-MM-DD input should be returned as YYYY/MM/DD"""
        result = self.format_birth_date('1990-07-15')
        self.assertEqual(result, '1990/07/15')

    def test_yyyy_slash_mm_slash_dd_format_is_preserved(self):
        """YYYY/MM/DD input should be returned unchanged as YYYY/MM/DD"""
        result = self.format_birth_date('1990/07/15')
        self.assertEqual(result, '1990/07/15')

    def test_leading_trailing_whitespace_is_stripped(self):
        """Birth date with surrounding whitespace should be normalized correctly"""
        result = self.format_birth_date('  1990-07-15  ')
        self.assertEqual(result, '1990/07/15')

    def test_invalid_format_raises_value_error(self):
        """Unsupported date format should raise ValueError"""
        with self.assertRaises(ValueError):
            self.format_birth_date('15-07-1990')

    def test_dd_mm_yyyy_format_raises_value_error(self):
        """DD/MM/YYYY format should raise ValueError"""
        with self.assertRaises(ValueError):
            self.format_birth_date('15/07/1990')

    def test_mm_dd_yyyy_format_raises_value_error(self):
        """MM/DD/YYYY format should raise ValueError"""
        with self.assertRaises(ValueError):
            self.format_birth_date('07/15/1990')

    def test_empty_string_raises_value_error(self):
        """Empty string should raise ValueError"""
        with self.assertRaises(ValueError):
            self.format_birth_date('')

    def test_non_string_raises_value_error(self):
        """Non-string input should raise ValueError"""
        with self.assertRaises(ValueError):
            self.format_birth_date(None)

    def test_integer_raises_value_error(self):
        """Integer input should raise ValueError"""
        with self.assertRaises(ValueError):
            self.format_birth_date(19900715)

    def test_error_message_mentions_both_supported_formats(self):
        """ValueError message for an unsupported format should mention both formats"""
        with self.assertRaises(ValueError) as ctx:
            self.format_birth_date('not-a-date')
        self.assertIn('YYYY-MM-DD', str(ctx.exception))
        self.assertIn('YYYY/MM/DD', str(ctx.exception))

    def test_non_string_error_message_mentions_both_supported_formats(self):
        """ValueError message for a non-string should mention both formats"""
        with self.assertRaises(ValueError) as ctx:
            self.format_birth_date(None)
        self.assertIn('YYYY-MM-DD', str(ctx.exception))
        self.assertIn('YYYY/MM/DD', str(ctx.exception))


class TestStreamChartAnalysisBirthDateValidation(unittest.TestCase):
    """Test that /stream-chart-analysis returns 400 for invalid birth date formats"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.valid_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51.5',
            'longitude': '-0.1',
        }

    @patch('ai_service.get_client')
    def test_invalid_birth_date_format_returns_400(self, mock_get_client):
        """Unsupported birth date format should return 400, not 500"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '08-08-1988'

        response = self.app.post('/stream-chart-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    @patch('ai_service.get_client')
    def test_slash_format_birth_date_accepted(self, mock_get_client):
        """YYYY/MM/DD birth date format should be accepted"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '1988/08/08'

        response = self.app.post('/stream-chart-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertNotEqual(response.status_code, 400)


class TestStreamFullChartAnalysisBirthDateValidation(unittest.TestCase):
    """Test that /stream-full-chart-analysis returns 400 for invalid birth date formats"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.valid_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51.5',
            'longitude': '-0.1',
        }

    @patch('ai_service.get_client')
    def test_invalid_birth_date_format_returns_400(self, mock_get_client):
        """Unsupported birth date format should return 400, not 500"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '08/08/1988'

        response = self.app.post('/stream-full-chart-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    @patch('ai_service.get_client')
    def test_slash_format_birth_date_accepted(self, mock_get_client):
        """YYYY/MM/DD birth date format should be accepted"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '1988/08/08'

        response = self.app.post('/stream-full-chart-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertNotEqual(response.status_code, 400)


class TestStreamLiveMasAnalysisBirthDateValidation(unittest.TestCase):
    """Test that /stream-live-mas-analysis returns 400 for invalid birth date formats"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.valid_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51.5',
            'longitude': '-0.1',
        }

    @patch('ai_service.get_client')
    def test_invalid_birth_date_format_returns_400(self, mock_get_client):
        """Unsupported birth date format should return 400, not 500"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = 'August 8, 1988'

        response = self.app.post('/stream-live-mas-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    @patch('ai_service.get_client')
    def test_slash_format_birth_date_accepted(self, mock_get_client):
        """YYYY/MM/DD birth date format should be accepted"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '1988/08/08'

        response = self.app.post('/stream-live-mas-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertNotEqual(response.status_code, 400)


class TestStreamAskAnythingBirthDateValidation(unittest.TestCase):
    """Test that /stream-ask-anything returns 400 for invalid birth date formats"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.valid_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51.5',
            'longitude': '-0.1',
            'question': 'What does my chart say?',
        }

    @patch('ai_service.get_client')
    def test_invalid_birth_date_format_returns_400(self, mock_get_client):
        """Unsupported birth date format should return 400, not 500"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '08-08-1988'

        response = self.app.post('/stream-ask-anything',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    @patch('ai_service.get_client')
    def test_slash_format_birth_date_accepted(self, mock_get_client):
        """YYYY/MM/DD birth date format should be accepted"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '1988/08/08'

        response = self.app.post('/stream-ask-anything',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertNotEqual(response.status_code, 400)


class TestMusicSuggestionBirthDateValidation(unittest.TestCase):
    """Test that /music-suggestion returns 400 for invalid birth date formats"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.valid_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51.5',
            'longitude': '-0.1',
        }

    @patch('ai_service.get_client')
    def test_invalid_birth_date_format_returns_400(self, mock_get_client):
        """Unsupported birth date format should return 400, not 500"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '08/08/1988'

        response = self.app.post('/music-suggestion',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    @patch('ai_service.get_client')
    def test_slash_format_birth_date_accepted(self, mock_get_client):
        """YYYY/MM/DD birth date format should be accepted"""
        mock_get_client.return_value = MagicMock()
        data = self.valid_data.copy()
        data['birth_date'] = '1988/08/08'

        response = self.app.post('/music-suggestion',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertNotEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
