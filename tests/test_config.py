# Test configuration and utilities

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Test data constants
SAMPLE_BIRTH_DATA = {
    'date': '1990-07-15',
    'time': '14:30',
    'timezone': '-5',
    'latitude': '40.7589',
    'longitude': '-73.9851'
}

SAMPLE_PLANET_DATA = {
    'Sun': {
        'sign': 'Cancer',
        'degree': 23.45,
        'retrograde': False
    },
    'Moon': {
        'sign': 'Pisces', 
        'degree': 12.67,
        'retrograde': False
    },
    'Mercury': {
        'sign': 'Gemini',
        'degree': 5.23,
        'retrograde': True
    },
    'Venus': {
        'sign': 'Leo',
        'degree': 18.90,
        'retrograde': False
    }
}

SAMPLE_CHART_RESULT = {
    'sun': 'Cancer',
    'moon': 'Pisces',
    'ascendant': 'Libra',
    'mercury_retrograde': True,
    'astrology_analysis': '✨ **Today\'s cosmic vibe** is all about emotional depth and intuition! 🌙\n\n**What to do:**\n• Trust your gut feelings 💫\n• Spend time near water 🌊\n• Journal your dreams 📝\n\n**What to avoid:**\n• Making impulsive decisions 🚫\n• Ignoring your emotions 💔'
}


class AstroTestCase(unittest.TestCase):
    """Base test case with common utilities"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def mock_openai_response(self, content="Test astrology response"):
        """Helper to mock OpenAI API response"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = content
        return mock_response
    
    def mock_chart_objects(self, sun_sign='Leo', moon_sign='Virgo', asc_sign='Gemini'):
        """Helper to mock astrological chart objects"""
        mock_sun = MagicMock()
        mock_sun.sign = sun_sign
        
        mock_moon = MagicMock()
        mock_moon.sign = moon_sign
        
        mock_ascendant = MagicMock()
        mock_ascendant.sign = asc_sign
        
        return mock_sun, mock_moon, mock_ascendant


def create_test_app():
    """Create a test Flask app instance"""
    from main import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    return app.test_client()


# Mock environment variables for testing
TEST_ENV_VARS = {
    'GITHUB_TOKEN': 'test_token_12345'
}


class MockEnvironment:
    """Context manager for mocking environment variables"""
    
    def __init__(self, env_vars):
        self.env_vars = env_vars
        self.original_env = {}
    
    def __enter__(self):
        for key, value in self.env_vars.items():
            self.original_env[key] = os.environ.get(key)
            os.environ[key] = value
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.env_vars:
            if self.original_env[key] is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = self.original_env[key]
