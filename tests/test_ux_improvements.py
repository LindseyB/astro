import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestTimezoneDropdown(unittest.TestCase):
    """Test timezone dropdown functionality"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_timezone_is_select_element(self):
        """Test that timezone field is rendered as a select dropdown"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for select element instead of text input
        self.assertIn(b'<select id="timezone_offset"', response.data)
        self.assertIn(b'class="timezone-select"', response.data)

    def test_timezone_has_common_us_timezones(self):
        """Test that timezone dropdown includes common US timezones"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for common US timezone options
        self.assertIn(b'Eastern Standard Time (EST)', response.data)
        self.assertIn(b'Pacific Standard Time (PST)', response.data)
        self.assertIn(b'Central Standard Time (CST)', response.data)
        self.assertIn(b'Mountain Standard Time (MST)', response.data)

    def test_timezone_has_international_timezones(self):
        """Test that timezone dropdown includes international timezones"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for international timezone options
        self.assertIn(b'Greenwich Mean Time (GMT)', response.data)
        self.assertIn(b'Central European Time (CET)', response.data)
        self.assertIn(b'India Standard Time (IST)', response.data)
        self.assertIn(b'Japan Standard Time (JST)', response.data)

    def test_timezone_has_utc_offsets(self):
        """Test that timezone dropdown includes UTC offset options"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for UTC offset options
        self.assertIn(b'UTC-05:00', response.data)
        self.assertIn(b'UTC+00:00', response.data)
        self.assertIn(b'UTC+09:00', response.data)

    def test_timezone_has_optgroups(self):
        """Test that timezone options are organized in optgroups"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for optgroup labels
        self.assertIn(b'<optgroup label="Common US Timezones">', response.data)
        self.assertIn(b'<optgroup label="Europe">', response.data)
        self.assertIn(b'<optgroup label="Asia">', response.data)
        self.assertIn(b'<optgroup label="All UTC Offsets">', response.data)

    def test_timezone_select2_script_loaded(self):
        """Test that Select2 library is loaded for timezone dropdown"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for Select2 CSS and JS
        self.assertIn(b'select2.min.css', response.data)
        self.assertIn(b'select2.min.js', response.data)

    def test_timezone_select_js_accessible(self):
        """Test that timezone-select.js file is accessible"""
        response = self.app.get('/static/js/timezone-select.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'select2', response.data)
        self.assertIn(b'timezone_offset', response.data)

    def test_timezone_form_submission_with_dropdown(self):
        """Test that form submission works with timezone dropdown"""
        form_data = {
            'birth_date': '1990-01-01',
            'birth_time': '12:00',
            'timezone_offset': '-05:00',
            'latitude': '40n42',
            'longitude': '74w00'
        }

        response = self.app.post('/chart', data=form_data)
        self.assertEqual(response.status_code, 200)
        # Should successfully generate chart with timezone data
        self.assertIn(b'timezoneoffset', response.data.lower())


class TestHiddenCoordinateFields(unittest.TestCase):
    """Test that latitude and longitude fields are hidden"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_latitude_field_is_hidden(self):
        """Test that latitude field is hidden with display:none"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check that latitude field has display:none
        response_text = response.data.decode('utf-8')
        # Find the div containing latitude field
        self.assertIn('style="display: none;"', response_text)
        self.assertIn('id="latitude"', response_text)

    def test_longitude_field_is_hidden(self):
        """Test that longitude field is hidden with display:none"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check that longitude field has display:none
        response_text = response.data.decode('utf-8')
        # Find the div containing longitude field
        self.assertIn('style="display: none;"', response_text)
        self.assertIn('id="longitude"', response_text)

    def test_coordinate_fields_still_exist_in_dom(self):
        """Test that coordinate fields exist in DOM (just hidden)"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Fields should still be present for form submission
        self.assertIn(b'name="latitude"', response.data)
        self.assertIn(b'name="longitude"', response.data)
        self.assertIn(b'required', response.data)


class TestMapDarkMode(unittest.TestCase):
    """Test dark mode functionality for Leaflet map"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_location_map_js_has_dark_mode_support(self):
        """Test that location-map.js includes dark mode functionality"""
        response = self.app.get('/static/js/location-map.js')
        self.assertEqual(response.status_code, 200)
        
        # Check for dark mode related code
        self.assertIn(b'updateMapTiles', response.data)
        self.assertIn(b'dark-mode', response.data)
        self.assertIn(b'MutationObserver', response.data)

    def test_location_map_js_has_dark_tiles(self):
        """Test that location-map.js includes dark tile provider"""
        response = self.app.get('/static/js/location-map.js')
        self.assertEqual(response.status_code, 200)
        
        # Check for CartoDB dark tiles
        self.assertIn(b'cartocdn.com/dark_all', response.data)

    def test_location_map_js_has_light_tiles(self):
        """Test that location-map.js includes light tile provider"""
        response = self.app.get('/static/js/location-map.js')
        self.assertEqual(response.status_code, 200)
        
        # Check for OpenStreetMap tiles
        self.assertIn(b'tile.openstreetmap.org', response.data)

    def test_location_map_js_observes_html_element(self):
        """Test that location-map.js observes document.documentElement"""
        response = self.app.get('/static/js/location-map.js')
        self.assertEqual(response.status_code, 200)
        
        # Check that it observes documentElement (not body)
        self.assertIn(b'document.documentElement', response.data)


class TestSparklesUpdate(unittest.TestCase):
    """Test sparkles.js updates for star characters and colors"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_sparkles_uses_star_characters(self):
        """Test that sparkles.js uses star characters instead of emoji"""
        response = self.app.get('/static/js/sparkles.js')
        self.assertEqual(response.status_code, 200)
        
        # Check for star characters (UTF-8 encoded)
        self.assertIn('✦'.encode('utf-8'), response.data)
        self.assertIn('✧'.encode('utf-8'), response.data)
        self.assertIn('⋆'.encode('utf-8'), response.data)
        
        # Should not have old emoji
        self.assertNotIn('🌟'.encode('utf-8'), response.data)
        self.assertNotIn('✨'.encode('utf-8'), response.data)

    def test_sparkles_has_color_array(self):
        """Test that sparkles.js includes color definitions"""
        response = self.app.get('/static/js/sparkles.js')
        self.assertEqual(response.status_code, 200)
        
        # Check for color array
        self.assertIn(b'#FFD700', response.data)  # Gold
        self.assertIn(b'#FFA500', response.data)  # Orange
        self.assertIn(b'#FF69B4', response.data)  # Hot pink
        self.assertIn(b'#9370DB', response.data)  # Purple

    def test_sparkles_has_text_shadow(self):
        """Test that sparkles.js applies text shadow for glow effect"""
        response = self.app.get('/static/js/sparkles.js')
        self.assertEqual(response.status_code, 200)
        
        # Check for textShadow property
        self.assertIn(b'textShadow', response.data)

    def test_sparkles_maintains_animation_logic(self):
        """Test that sparkles.js maintains core animation functionality"""
        response = self.app.get('/static/js/sparkles.js')
        self.assertEqual(response.status_code, 200)
        
        # Core functions should still exist
        self.assertIn(b'createSparkle', response.data)
        self.assertIn(b'startSparkleRain', response.data)


class TestSearchButtonStyling(unittest.TestCase):
    """Test search button styling matches main buttons"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_search_button_has_gradient(self):
        """Test that search button has gradient background"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        # Check for gradient in location-search button
        css_content = response.data.decode('utf-8')
        self.assertIn('.location-search button', css_content)
        self.assertIn('linear-gradient(135deg, #667eea 0%, #764ba2 100%)', css_content)

    def test_search_button_has_rounded_corners(self):
        """Test that search button has rounded pill shape"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        # Should have border-radius similar to main buttons
        self.assertIn('border-radius: 25px', css_content)

    def test_search_button_has_hover_effects(self):
        """Test that search button has hover transform effect"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        self.assertIn('.location-search button:hover', css_content)
        self.assertIn('translateY(-2px)', css_content)


class TestFormInputStyling(unittest.TestCase):
    """Test consistent styling across form inputs"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_all_inputs_have_space_mono_font(self):
        """Test that all inputs use Space Mono font"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        # Base input and select styling should include font
        self.assertIn("input, select", css_content)
        self.assertIn("'Space Mono', monospace", css_content)

    def test_location_search_input_consistent_styling(self):
        """Test that location search input matches other inputs"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        self.assertIn('.location-search input', css_content)
        self.assertIn('border-radius: 8px', css_content)
        self.assertIn('font-size: 16px', css_content)

    def test_other_genre_input_consistent_styling(self):
        """Test that other genre input matches standard inputs"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        self.assertIn('.other-genre-input input', css_content)
        self.assertIn('border-radius: 8px', css_content)
        self.assertIn('font-size: 16px', css_content)

    def test_inputs_have_focus_styling(self):
        """Test that inputs have consistent focus styling"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        self.assertIn('input:focus', css_content)
        self.assertIn('border-color: #667eea', css_content)


class TestSelect2Styling(unittest.TestCase):
    """Test Select2 custom styling for timezone dropdown"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_select2_container_styling(self):
        """Test that Select2 container has custom styling"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        self.assertIn('.select2-container--default .select2-selection--single', css_content)
        self.assertIn('border-radius: 8px', css_content)

    def test_select2_dark_mode_styling(self):
        """Test that Select2 has dark mode styling"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        self.assertIn('.dark-mode .select2', css_content)

    def test_select2_uses_css_variables(self):
        """Test that Select2 styling uses CSS variables for theme support"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        # Should use CSS variables for colors
        self.assertIn('var(--input-bg)', css_content)
        self.assertIn('var(--text-color)', css_content)
        self.assertIn('var(--border-color)', css_content)


class TestLocationHelp(unittest.TestCase):
    """Test location help button styling"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_location_help_button_has_emoji(self):
        """Test that location help button uses ❓ emoji"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for question mark emoji
        self.assertIn('❓'.encode('utf-8'), response.data)
        self.assertIn(b'id="locationHelpBtn"', response.data)


class TestJQueryDependency(unittest.TestCase):
    """Test jQuery dependency for Select2"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_jquery_loaded_before_select2(self):
        """Test that jQuery is loaded before Select2"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        response_text = response.data.decode('utf-8')
        jquery_pos = response_text.find('jquery-3.6.0.min.js')
        select2_pos = response_text.find('select2.min.js')
        
        # jQuery should be loaded before Select2
        self.assertGreater(jquery_pos, 0)
        self.assertGreater(select2_pos, 0)
        self.assertLess(jquery_pos, select2_pos)


if __name__ == '__main__':
    unittest.main()
