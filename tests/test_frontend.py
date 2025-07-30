import unittest
import os
import sys

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
        
        with patch('main.calculate_chart') as mock_calc:
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
            with open(sparkles_path, 'r') as f:
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
