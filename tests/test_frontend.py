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
        app.testing = True
        self.app = app.test_client()

    def test_static_css_accessible(self):
        """Test that CSS file is accessible"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'@keyframes', response.data)

    def test_static_js_datetime_input_accessible(self):
        """Test that datetime input JS file is accessible"""
        response = self.app.get('/static/js/datetime-input.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'normalizeDate', response.data)

    def test_datetime_input_clears_on_focus(self):
        """Test that datetime input JS includes clear-on-focus behaviour"""
        response = self.app.get('/static/js/datetime-input.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'focus', response.data)
        self.assertIn(b"text.value = ''", response.data)

    def test_datetime_input_digits_only(self):
        """Test that datetime input JS restricts input to digits only"""
        response = self.app.get('/static/js/datetime-input.js')
        self.assertEqual(response.status_code, 200)
        # Keydown handler that blocks non-digit keys
        self.assertIn(b'keydown', response.data)
        self.assertIn(b'preventDefault', response.data)
        self.assertIn(b'/^\\d$/', response.data)

    def test_datetime_input_auto_delimiter(self):
        """Test that datetime input JS auto-inserts delimiters while typing"""
        response = self.app.get('/static/js/datetime-input.js')
        self.assertEqual(response.status_code, 200)
        # Formatter functions for date and time
        self.assertIn(b'formatDateDigits', response.data)
        self.assertIn(b'formatTimeDigits', response.data)
        # Input event handler drives auto-formatting
        self.assertIn(b"addEventListener('input'", response.data)

    def test_datetime_input_date_hint_updated(self):
        """Test that the date field hint reflects digits-only input and example formatting"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        self.assertIn('id="birth_date"', response_text)
        self.assertIn('id="birth_date_hint"', response_text)
        self.assertIn('19900715', response_text)
        self.assertIn('1990-07-15', response_text)
    def test_datetime_input_time_hint_updated(self):
        """Test that the time field hint reflects digits-only input and example formatting"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        self.assertIn('id="birth_time"', response_text)
        self.assertIn('id="birth_time_hint"', response_text)
        self.assertIn('0930', response_text)
        self.assertIn('09:30', response_text)
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
        self.assertIn(b'astro-datetime-input', response.data)
        self.assertIn(b'astro-timezone-select', response.data)

    def test_base_loads_web_component_registry(self):
        """Test that base template loads the centralized web component module"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'js/components/index.js', response.data)

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
        self.assertIn(b'chart-page-config', response.data)
        self.assertIn(b'chart-page.js', response.data)
        self.assertIn(b'reading-page', response.data)
        self.assertIn(b'stream-analysis.js', response.data)
        self.assertIn(b'Today, in three breaths', response.data)
        self.assertIn(b'The sky is listening', response.data)

    def test_full_chart_template_structure(self):
        """Test full chart template structure with streaming placeholder"""
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

    def test_ask_anything_template_structure(self):
        """Test ask-anything template structure with streaming placeholder"""
        response = self.app.post('/ask-anything', data={
            'question_prompt': 'How do I focus better?',
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '00w07'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'document.body.dataset.streaming', response.data)
        self.assertIn(b'stream-analysis.js', response.data)
        self.assertIn(b'pageType: \'ask-anything\'', response.data)
        self.assertIn(b'astro-copy-analysis', response.data)
        self.assertIn(b'astro-button', response.data)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        """Set up test client"""
        app.testing = True
        self.app = app.test_client()

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

    def test_chart_wheel_js_class(self):
        """Test that chart-wheel.js contains ChartWheel class"""
        chart_wheel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'chart-wheel.js')

        if os.path.exists(chart_wheel_path):
            with open(chart_wheel_path, 'r', encoding='utf-8', errors='ignore') as f:
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

    def test_web_component_files_exist(self):
        """Test that web component files are present in static/js/components"""
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'components')
        required = [
            'index.js',
            'registry.js',
            'astro-button.js',
            'astro-chart-wheel.js',
            'astro-section-toggle.js',
            'astro-copy-analysis.js',
            'astro-datetime-input.js',
            'astro-timezone-select.js',
        ]

        for filename in required:
            full_path = os.path.join(base_path, filename)
            self.assertTrue(os.path.exists(full_path), f'{filename} should exist')

            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if filename.startswith('astro-'):
                self.assertIn('customElements.define', content, f'{filename} should define a custom element')
    def test_web_component_registry_accessible(self):
        """Test that component registry module is served as a static asset"""
        response = app.test_client().get('/static/js/components/index.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'registerAstroComponents', response.data)

    def test_full_chart_uses_chart_wheel_component(self):
        """Test full chart template uses astro-chart-wheel wrapper"""
        response = app.test_client().post('/full-chart', data={
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '00w07'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'astro-chart-wheel', response.data)


class TestCSS(unittest.TestCase):
    """Test CSS file structure and key styles"""

    def test_css_file_structure(self):
        """Test that CSS file contains expected styles"""
        css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'style.css')

        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                content = f.read()

            # Test for key style classes
            self.assertIn('.spinner', content)
            self.assertIn('@keyframes', content)


class TestAccessibilityRegression(unittest.TestCase):
    """Regression tests for accessibility-critical template and script behavior"""

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_base_has_skip_link_and_theme_toggle_a11y_state_script(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertIn(b'class="skip-link" href="#main-content"', response.data)
        self.assertIn(b"setAttribute('aria-pressed'", response.data)
        self.assertIn(b"setAttribute('aria-label'", response.data)

    def test_key_pages_have_main_landmark_target(self):
        page_responses = [
            self.app.get('/'),
            self.app.post('/chart', data={
                'birth_date': '1988-08-08',
                'birth_time': '10:30',
                'timezone_offset': '0',
                'latitude': '51n30',
                'longitude': '00w07'
            }),
            self.app.post('/full-chart', data={
                'birth_date': '1988-08-08',
                'birth_time': '10:30',
                'timezone_offset': '0',
                'latitude': '51n30',
                'longitude': '00w07'
            }),
            self.app.post('/ask-anything', data={
                'question_prompt': 'How can I stay grounded today?',
                'birth_date': '1988-08-08',
                'birth_time': '10:30',
                'timezone_offset': '0',
                'latitude': '51n30',
                'longitude': '00w07'
            }),
            self.app.post('/live-mas', data={
                'birth_date': '1988-08-08',
                'birth_time': '10:30',
                'timezone_offset': '0',
                'latitude': '51n30',
                'longitude': '00w07',
                'music_genre': 'any',
                'other_genre': ''
            }),
        ]

        for response in page_responses:
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'id="main-content"', response.data)

    def test_index_dialog_semantics_and_trigger_attributes(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertIn(b'id="birthInfoBtn" class="pill-btn" aria-haspopup="dialog"', response.data)
        self.assertIn(b'aria-controls="birthPanel"', response.data)
        self.assertIn(b'aria-expanded="false"', response.data)

        re = __import__('re')
        self.assertRegex(
            response.data.decode('utf-8', errors='ignore'),
            r'<aside[^>]*\bid="birthPanel"[^>]*\brole="dialog"[^>]*\baria-modal="true"[^>]*\baria-labelledby="panelTitle"[^>]*\baria-hidden="true"[^>]*\binert\b'
        )

    def test_index_has_programmatic_labels_for_critical_fields(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertIn(b'<label for="locationSearch">Birth Location</label>', response.data)
        self.assertIn(b'<label class="sr-only" for="latitude">Latitude</label>', response.data)
        self.assertIn(b'<label class="sr-only" for="longitude">Longitude</label>', response.data)
        self.assertIn(b'<label class="sr-only" for="askModalInput">Your question</label>', response.data)

    def test_personality_field_is_optional_and_described_for_screen_readers(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertIn(b'<label for="personality">Personality (optional)</label>', response.data)
        self.assertIn(b'id="personality" name="personality" aria-describedby="personality_hint"', response.data)
        self.assertIn(b'id="personality_hint" class="field-hint">Optional voice style for responses.', response.data)

    def test_analysis_regions_expose_live_status(self):
        chart_response = self.app.post('/chart', data={
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '00w07'
        })
        ask_response = self.app.post('/ask-anything', data={
            'question_prompt': 'What should I focus on?',
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '00w07'
        })
        full_response = self.app.post('/full-chart', data={
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '00w07'
        })
        live_mas_response = self.app.post('/live-mas', data={
            'birth_date': '1988-08-08',
            'birth_time': '10:30',
            'timezone_offset': '0',
            'latitude': '51n30',
            'longitude': '00w07',
            'music_genre': 'any',
            'other_genre': ''
        })

        for response in [chart_response, ask_response, full_response, live_mas_response]:
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'id="analysisContent"', response.data)
            self.assertIn(b'role="status"', response.data)
            self.assertIn(b'aria-live="polite"', response.data)
            self.assertIn(b'aria-busy="false"', response.data)
            self.assertIn(b'id="analysisStreamContent"', response.data)
            self.assertIn(b'id="analysisStreamIndicator"', response.data)
            self.assertIn(b'streaming-indicator__icon', response.data)

    def test_streaming_script_sets_and_clears_aria_busy(self):
        response = self.app.get('/static/js/stream-analysis.js')
        self.assertEqual(response.status_code, 200)

        self.assertIn(b"setAttribute('aria-busy', 'true')", response.data)
        self.assertIn(b"setAttribute('aria-busy', 'false')", response.data)
        self.assertIn(b'analysisStreamContent', response.data)
        self.assertIn('✦'.encode('utf-8'), response.data)
        self.assertIn(b'sr-only', response.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
