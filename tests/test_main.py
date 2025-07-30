import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, calculate_chart, format_planets_for_api, markdown_filter


class TestAstroApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_index_route(self):
        """Test the main index page loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Astro Horoscope', response.data)
    
    def test_chart_route_missing_data(self):
        """Test chart route with missing form data"""
        response = self.app.post('/chart', data={})
        # Should return 400 or redirect to error page
        self.assertIn(response.status_code, [400, 500])
    
    def test_chart_route_valid_data(self):
        """Test chart route with valid form data"""
        form_data = {
            'birth_date': '1990-01-15',
            'birth_time': '12:00',
            'timezone_offset': '-5',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        }
        
        with patch('main.calculate_chart') as mock_calc:
            mock_calc.return_value = {
                'sun': 'Capricorn',
                'moon': 'Leo',
                'ascendant': 'Virgo',
                'mercury_retrograde': False,
                'astrology_analysis': 'Test analysis'
            }
            
            response = self.app.post('/chart', data=form_data)
            self.assertEqual(response.status_code, 200)
            mock_calc.assert_called_once()


class TestUtilityFunctions(unittest.TestCase):
    
    def test_markdown_filter_basic(self):
        """Test markdown filter with basic text"""
        result = markdown_filter("**Bold text**")
        self.assertIn('<strong>Bold text</strong>', result)
    
    def test_markdown_filter_empty(self):
        """Test markdown filter with empty input"""
        result = markdown_filter("")
        self.assertEqual(result, "")
    
    def test_markdown_filter_none(self):
        """Test markdown filter with None input"""
        result = markdown_filter(None)
        self.assertEqual(result, "")
    
    def test_format_planets_for_api(self):
        """Test planet formatting function"""
        test_planets = {
            'Mercury': {
                'sign': 'Gemini',
                'degree': 15.5,
                'retrograde': True
            },
            'Venus': {
                'sign': 'Taurus',
                'degree': 22.3,
                'retrograde': False
            }
        }
        
        result = format_planets_for_api(test_planets)
        
        self.assertIn('CURRENT PLANETARY POSITIONS:', result)
        self.assertIn('Mercury in Gemini at 15.50 degrees (RETROGRADE)', result)
        self.assertIn('Venus in Taurus at 22.30 degrees (direct)', result)
        self.assertIn('RETROGRADE PLANETS: Mercury', result)
    
    def test_format_planets_no_retrograde(self):
        """Test planet formatting with no retrograde planets"""
        test_planets = {
            'Sun': {
                'sign': 'Leo',
                'degree': 10.0,
                'retrograde': False
            }
        }
        
        result = format_planets_for_api(test_planets)
        self.assertIn('No planets are currently retrograde.', result)


class TestChartCalculation(unittest.TestCase):
    
    @patch('main.datetime')
    @patch('main.Chart')
    @patch('main.Datetime')
    @patch('main.GeoPos')
    def test_calculate_chart_basic(self, mock_geopos, mock_datetime, mock_chart, mock_dt):
        """Test basic chart calculation with mocked dependencies"""
        # Mock the datetime
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: {
            '%Y/%m/%d': '2024/01/15',
            '%H:%M': '12:00'
        }[fmt]
        
        # Mock chart objects
        mock_sun = MagicMock()
        mock_sun.sign = 'Capricorn'
        mock_moon = MagicMock()
        mock_moon.sign = 'Leo'
        mock_ascendant = MagicMock()
        mock_ascendant.sign = 'Virgo'
        
        mock_chart_instance = MagicMock()
        mock_chart_instance.get.side_effect = lambda x: {
            'Sun': mock_sun,
            'Moon': mock_moon,
            'House1': mock_ascendant
        }[x]
        mock_chart_instance.houses = []
        
        mock_chart.return_value = mock_chart_instance
        
        # Mock OpenAI client
        with patch('main.client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Test astrology analysis"
            mock_client.chat.completions.create.return_value = mock_response
            
            result = calculate_chart(
                '1990/01/15', '12:00', '-5', 40.7128, -74.0060
            )
            
            self.assertEqual(result['sun'], 'Capricorn')
            self.assertEqual(result['moon'], 'Leo')
            self.assertEqual(result['ascendant'], 'Virgo')
            self.assertIn('astrology_analysis', result)
    
    @patch('main.datetime')
    @patch('main.Chart')
    @patch('main.client')
    def test_calculate_chart_api_error(self, mock_client, mock_chart, mock_dt):
        """Test chart calculation when AI API fails"""
        # Mock datetime
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: {
            '%Y/%m/%d': '2024/01/15',
            '%H:%M': '12:00'
        }[fmt]
        
        # Mock chart objects
        mock_sun = MagicMock()
        mock_sun.sign = 'Capricorn'
        mock_moon = MagicMock()
        mock_moon.sign = 'Leo'
        mock_ascendant = MagicMock()
        mock_ascendant.sign = 'Virgo'
        
        mock_chart_instance = MagicMock()
        mock_chart_instance.get.side_effect = lambda x: {
            'Sun': mock_sun,
            'Moon': mock_moon,
            'House1': mock_ascendant
        }[x]
        mock_chart_instance.houses = []
        
        mock_chart.return_value = mock_chart_instance
        
        # Mock API failure
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = calculate_chart(
            '1990/01/15', '12:00', '-5', 40.7128, -74.0060
        )
        
        self.assertIn('cosmic coffee break', result['astrology_analysis'])


class TestIntegration(unittest.TestCase):
    """Integration tests that test the full flow"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('main.calculate_chart')
    def test_full_chart_generation_flow(self, mock_calc):
        """Test the complete flow from form submission to chart display"""
        mock_calc.return_value = {
            'sun': 'Aquarius',
            'moon': 'Pisces',
            'ascendant': 'Gemini',
            'mercury_retrograde': True,
            'astrology_analysis': '✨ **Today\'s Vibe:** Cosmic energy is flowing! 🌟\n\n• Do: Meditate\n• Don\'t: Make big decisions'
        }
        
        form_data = {
            'birth_date': '1995-02-10',
            'birth_time': '14:30',
            'timezone_offset': '-8',
            'latitude': '34.0522',
            'longitude': '-118.2437'
        }
        
        response = self.app.post('/chart', data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aquarius', response.data)
        self.assertIn(b'Pisces', response.data)
        self.assertIn(b'Gemini', response.data)
        mock_calc.assert_called_once_with(
            '1995/02/10', '14:30', '-8', '34.0522', '-118.2437'
        )


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAstroApp,
        TestUtilityFunctions, 
        TestChartCalculation,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
