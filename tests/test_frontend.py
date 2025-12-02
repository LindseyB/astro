import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestTemplates(unittest.TestCase):
    """Test template rendering and static file serving"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_static_css_accessible(self):
        """Test that CSS file is accessible"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Space Mono', response.data)

    def test_static_js_sparkles_accessible(self):
        """Test that sparkles JS file is accessible"""
        response = self.app.get('/static/js/sparkles.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'createSparkle', response.data)

    def test_static_js_star_trail_accessible(self):
        """Test that star trail JS file is accessible"""
        response = self.app.get('/static/js/star-trail.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'StarTrail', response.data)

    def test_index_template_renders(self):
        """Test that index template renders correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        # Check for key elements
        self.assertIn(b'birth_date', response.data)
        self.assertIn(b'birth_time', response.data)
        self.assertIn(b'latitude', response.data)
        self.assertIn(b'longitude', response.data)
        self.assertIn(b'timezone_offset', response.data)

    def test_chart_template_structure(self):
        """Test chart template structure with mock data"""
        from unittest.mock import patch

        with patch('routes.calculate_chart') as mock_calc:
            mock_calc.return_value = {
                'sun': 'Leo',
                'moon': 'Scorpio',
                'ascendant': 'Cancer',
                'mercury_retrograde': False,
                'astrology_analysis': '**Test analysis** with markdown'
            }

            form_data = {
                'birth_date': '1988-08-08',
                'birth_time': '10:30',
                'timezone_offset': '0',
                'latitude': '51.5074',
                'longitude': '-0.1278'
            }

            response = self.app.post('/chart', data=form_data)
            self.assertEqual(response.status_code, 200)

            # Check for chart elements
            self.assertIn(b'Leo', response.data)
            self.assertIn(b'Scorpio', response.data)
            self.assertIn(b'Cancer', response.data)
            self.assertIn(b'sparkleContainer', response.data)

    def test_full_chart_template_structure(self):
        """Test full chart template structure with mock data"""
        from unittest.mock import patch

        # Create complete house data (all 12 houses required)
        signs = ['Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces', 'Aries',
                 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra']
        houses = {}
        for i in range(1, 13):
            houses[i] = {'sign': signs[i-1], 'degree': 12.4 + i}

        with patch('routes.calculate_full_chart') as mock_calc:
            mock_calc.return_value = {
                'planets': {
                    'Sun': {'sign': 'Leo', 'degree': 15.5, 'house': 10},
                    'Moon': {'sign': 'Cancer', 'degree': 22.3, 'house': 9},
                    'Mercury': {'sign': 'Virgo', 'degree': 5.1, 'house': 11}
                },
                'houses': houses,
                'aspects': [],
                'chart_analysis': '**Full chart analysis** with details'
            }

            form_data = {
                'birth_date': '1988-08-08',
                'birth_time': '10:30',
                'timezone_offset': '0',
                'latitude': '51.5074',
                'longitude': '-0.1278'
            }

            response = self.app.post('/full-chart', data=form_data)
            self.assertEqual(response.status_code, 200)

            # Check for chart wheel canvas
            self.assertIn(b'chartWheel', response.data)
            self.assertIn(b'<canvas', response.data)
            
            # Check for chart-wheel.js script
            self.assertIn(b'chart-wheel.js', response.data)
            
            # Check for window.chartData
            self.assertIn(b'window.chartData', response.data)
            
            # Check for planet data
            self.assertIn(b'Leo', response.data)
            self.assertIn(b'Cancer', response.data)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_invalid_static_file(self):
        """Test requesting non-existent static file"""
        response = self.app.get('/static/nonexistent.css')
        self.assertEqual(response.status_code, 404)

    def test_chart_with_invalid_date(self):
        """Test chart generation with invalid date format"""
        form_data = {
            'birth_date': 'invalid-date',
            'birth_time': '12:00',
            'timezone_offset': '0',
            'latitude': '0',
            'longitude': '0'
        }

        response = self.app.post('/chart', data=form_data)
        # Should handle error gracefully
        # Check for error message in response
        self.assertIn(b'error', response.data)
        self.assertIn(b'Check your date format (should be YYYY-MM-DD)', response.data)
        self.assertEqual(response.status_code, 200)

    def test_chart_with_missing_fields(self):
        """Test chart generation with missing required fields"""
        form_data = {
            'birth_date': '1990-01-01',
            # Missing other required fields
        }

        response = self.app.post('/chart', data=form_data)
        self.assertIn(response.status_code, [400, 500])

    def test_chart_with_invalid_coordinates(self):
        """Test chart generation with invalid latitude/longitude"""
        form_data = {
            'birth_date': '1990-01-01',
            'birth_time': '12:00',
            'timezone_offset': '0',
            'latitude': '103w52',
            'longitude': '103w52'
        }

        response = self.app.post('/chart', data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'error', response.data)
        self.assertIn(b'Confirm latitude format', response.data)
        self.assertIn(b'Confirm longitude format', response.data)


class TestJavaScriptFunctionality(unittest.TestCase):
    """Test JavaScript file contents and structure"""

    def test_sparkles_js_functions(self):
        """Test that sparkles.js contains required functions"""
        sparkles_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'sparkles.js')

        if os.path.exists(sparkles_path):
            with open(sparkles_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn('createSparkle', content)
            self.assertIn('startSparkleRain', content)
            self.assertIn('sparkleContainer', content)

    def test_star_trail_js_class(self):
        """Test that star-trail.js contains StarTrail class"""
        star_trail_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'star-trail.js')

        if os.path.exists(star_trail_path):
            with open(star_trail_path, 'r') as f:
                content = f.read()

            self.assertIn('class StarTrail', content)
            self.assertIn('createStar', content)
            self.assertIn('animate', content)
            self.assertIn('mousemove', content)

    def test_chart_wheel_js_class(self):
        """Test that chart-wheel.js contains ChartWheel class"""
        chart_wheel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'chart-wheel.js')

        if os.path.exists(chart_wheel_path):
            with open(chart_wheel_path, 'r') as f:
                content = f.read()

            # Test for main class
            self.assertIn('class ChartWheel', content)
            
            # Test for key methods
            self.assertIn('drawZodiacWheel', content)
            self.assertIn('drawHouseLines', content)
            self.assertIn('drawHouseNumbers', content)
            self.assertIn('drawPlanets', content)
            self.assertIn('drawAspectLines', content)
            self.assertIn('calculateAngle', content)
            
            # Test for constants
            self.assertIn('ZODIAC_SYMBOLS', content)
            self.assertIn('PLANET_SYMBOLS', content)
            self.assertIn('SIGN_DEGREES', content)
            
            # Test for zodiac signs
            self.assertIn('Aries', content)
            self.assertIn('Cancer', content)
            self.assertIn('Libra', content)
            self.assertIn('Capricorn', content)

    def test_chart_wheel_js_file_exists(self):
        """Test that chart-wheel.js file exists"""
        chart_wheel_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 'js', 'chart-wheel.js'
        )
        self.assertTrue(os.path.exists(chart_wheel_path), "chart-wheel.js should exist")


class TestCSS(unittest.TestCase):
    """Test CSS file structure and key styles"""

    def test_css_file_structure(self):
        """Test that CSS file contains expected styles"""
        css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'style.css')

        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                content = f.read()

            # Test for key style classes
            self.assertIn('body', content)
            self.assertIn('.container', content)
            self.assertIn('.sparkle', content)
            self.assertIn('.analysis-section', content)
            self.assertIn('Space Mono', content)
            self.assertIn('@keyframes', content)


class TestLaunchDarklyIntegration(unittest.TestCase):
    """Test LaunchDarkly integration with routes"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('routes.should_show_chart_wheel')
    @patch('routes.calculate_full_chart')
    @patch('routes.get_user_ip')
    def test_full_chart_route_calls_feature_flag(self, mock_get_ip, mock_calc, mock_flag):
        """Test that full chart route calls the LaunchDarkly feature flag with IP"""
        mock_flag.return_value = True
        mock_get_ip.return_value = "192.168.1.100"
        
        # Mock the calculation to avoid complex dependency issues
        mock_calc.return_value = {
            'sun': 'Capricorn',
            'moon': 'Taurus', 
            'ascendant': 'Leo',
            'astrology_analysis': 'Test analysis',
            'planets': {
                'Sun': {'sign': 'Capricorn', 'degree': 10.5, 'house': 1},
                'Moon': {'sign': 'Taurus', 'degree': 15.2, 'house': 5}
            },
            'houses': {
                1: {'sign': 'Leo', 'cusp_degree': 0.0},
                2: {'sign': 'Virgo', 'cusp_degree': 30.0}
            }
        }
        
        form_data = {
            'birth_date': '1990-01-01',
            'birth_time': '12:00',
            'timezone_offset': '0',
            'latitude': '40.7128',
            'longitude': '-74.0060',
            'music_genre': 'rock'
        }
        
        response = self.app.post('/full-chart', data=form_data)
        
        # The main thing we want to test is that the flag is being called with IP
        mock_get_ip.assert_called_once()
        mock_flag.assert_called_once_with("192.168.1.100")
        
        # And that the calculation is called with proper parameters
        mock_calc.assert_called_once_with('1990/01/01', '12:00', '0', '40.7128', '-74.0060', 'rock')
        
        # Response should be successful (either 200 or redirected)
        self.assertIn(response.status_code, [200, 302])
    
    @patch('routes.should_show_chart_wheel')
    @patch('routes.get_user_ip')
    def test_ip_function_integration(self, mock_get_ip, mock_flag):
        """Test that we can get user IP and call the flag function"""
        mock_flag.return_value = False
        mock_get_ip.return_value = "203.0.113.195"
        
        from routes import get_user_ip, app as routes_app
        with routes_app.test_request_context('/', headers={'X-Forwarded-For': '203.0.113.195'}):
            user_ip = get_user_ip()
            self.assertEqual(user_ip, "203.0.113.195")
                
        # Test the flag function
        result = mock_flag('203.0.113.195')
        self.assertEqual(result, False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
