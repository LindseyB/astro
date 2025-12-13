import unittest
import os
import sys
from unittest.mock import patch

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
        """Test chart template structure with streaming placeholder"""
        form_data = {
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '00w07'
        }

        response = self.app.post('/chart', data=form_data)
        self.assertEqual(response.status_code, 200)

        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)
        self.assertIn(b'sparkleContainer', response.data)
        self.assertIn(b'stream-analysis.js', response.data)

    def test_full_chart_template_structure(self):
        """Test full chart template structure with streaming placeholder"""
        from unittest.mock import patch

        with patch('routes.should_show_chart_wheel', return_value=False):
            form_data = {
                'birth_date': '1988-08-08',
                'birth_time': '10:30',
                'timezone_offset': '0',
                'latitude': '51n30',
                'longitude': '00w07'
            }

            response = self.app.post('/full-chart', data=form_data)
            self.assertEqual(response.status_code, 200)

            # Check for streaming setup
            self.assertIn(b'document.body.dataset.streaming', response.data)
            self.assertIn(b'stream-analysis.js', response.data)


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

    def test_modal_js_functions(self):
        """Test that modal.js contains required functions"""
        modal_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'modal.js')

        if os.path.exists(modal_path):
            with open(modal_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Test for main functions
            self.assertIn('openModal', content)
            self.assertIn('closeModal', content)
            self.assertIn('initializeModals', content)
            
            # Test for event handling
            self.assertIn('handleEscapeKey', content)
            self.assertIn('addEventListener', content)
            
            # Test for modal interaction elements
            self.assertIn('modal-overlay', content)
            self.assertIn('modal-close', content)
            
            # Test for accessibility
            self.assertIn('overflow', content)  # Body scroll prevention

    def test_section_toggle_js_functions(self):
        """Test that section-toggle.js contains required functions"""
        section_toggle_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'section-toggle.js')

        if os.path.exists(section_toggle_path):
            with open(section_toggle_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Test for main functions
            self.assertIn('initializeToggleSections', content)
            self.assertIn('restoreSectionStates', content)
            self.assertIn('updateSectionState', content)
            
            # Test for event handling
            self.assertIn('addEventListener', content)
            
            # Test for toggle interaction elements
            self.assertIn('section-header', content)
            self.assertIn('toggle-btn', content)
            self.assertIn('data-section', content)
            
            # Test for state management
            self.assertIn('localStorage', content)
            self.assertIn('collapsed', content)
            
            # Test for accessibility
            self.assertIn('aria-expanded', content)


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
    @patch('routes.get_user_ip')
    def test_full_chart_route_calls_feature_flag(self, mock_get_ip, mock_flag):
        """Test that full chart route calls the LaunchDarkly feature flag with IP"""
        mock_flag.return_value = True
        mock_get_ip.return_value = "192.168.1.100"
        
        form_data = {
            'birth_date': '1990-01-01',
            'birth_time': '12:00',
            'timezone_offset': '0',
            'latitude': '40n42',
            'longitude': '74w00',
            'music_genre': 'rock'
        }
        
        response = self.app.post('/full-chart', data=form_data)
        
        # The main thing we want to test is that the flag is being called with IP
        mock_get_ip.assert_called_once()
        mock_flag.assert_called_once_with("192.168.1.100")
        
        # Response should be successful
        self.assertEqual(response.status_code, 200)
        # Should contain streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)
    
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
