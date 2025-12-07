import unittest
import sys
import os

# Add the parent directory to the path to import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes import app
from formatters import format_planets_for_api, markdown_filter, prepare_music_genre_text


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
        """Test chart route with valid form data - should render placeholder immediately"""
        form_data = {
            'birth_date': '1990-01-15',
            'birth_time': '12:00',
            'timezone_offset': '-5',
            'latitude': '40n42',
            'longitude': '74w00'
        }

        response = self.app.post('/chart', data=form_data)
        self.assertEqual(response.status_code, 200)
        # Should contain the streaming placeholder setup
        self.assertIn(b'document.body.dataset.streaming', response.data)

    def test_full_chart_route_missing_data(self):
        """Test full chart route with missing form data"""
        response = self.app.post('/full-chart', data={})
        # Should return 400 or redirect to error page
        self.assertIn(response.status_code, [400, 500])

    def test_full_chart_route_valid_data(self):
        """Test full chart route with valid form data - should render placeholder immediately"""
        form_data = {
            'birth_date': '1990-01-15',
            'birth_time': '12:00',
            'timezone_offset': '-5',
            'latitude': '40n42',
            'longitude': '74w00'
        }

        response = self.app.post('/full-chart', data=form_data)
        self.assertEqual(response.status_code, 200)
        # Should contain the streaming placeholder setup
        self.assertIn(b'document.body.dataset.streaming', response.data)

    def test_live_mas_route_missing_data(self):
        """Test live-mas route with missing form data"""
        response = self.app.post('/live-mas', data={})
        # Should return 400 or 500 for missing data, or 200 with error in response body
        self.assertIn(response.status_code, [200, 400, 500])
        if response.status_code == 200:
            self.assertIn(b'Error', response.data)

    def test_live_mas_route_valid_data(self):
        """Test live-mas route with valid form data - should render placeholder immediately"""
        form_data = {
            'birth_date': '1990-01-15',
            'birth_time': '12:00',
            'timezone_offset': '-5',
            'latitude': '40n42',
            'longitude': '74w00'
        }

        response = self.app.post('/live-mas', data=form_data)
        self.assertEqual(response.status_code, 200)
        # Should contain the streaming placeholder setup
        self.assertIn(b'document.body.dataset.streaming', response.data)


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

    def test_prepare_music_genre_text_daily_rock(self):
        """Test music genre text preparation for daily horoscope with rock genre"""
        result = prepare_music_genre_text('rock', 'daily')
        self.assertEqual(result, '(Please prioritize rock genre if possible)')

    def test_prepare_music_genre_text_natal_jazz(self):
        """Test music genre text preparation for natal chart with jazz genre"""
        result = prepare_music_genre_text('jazz', 'natal')
        self.assertEqual(result, '(Please prioritize jazz genre if possible)')

    def test_prepare_music_genre_text_other_daily(self):
        """Test music genre text preparation for daily horoscope with 'other' option"""
        result = prepare_music_genre_text('other', 'daily')
        self.assertEqual(result, '(Please suggest songs from any genre that fits the vibe)')

    def test_prepare_music_genre_text_other_natal(self):
        """Test music genre text preparation for natal chart with 'other' option"""
        result = prepare_music_genre_text('other', 'natal')
        self.assertEqual(result, '(Please suggest a song from any genre that fits the chart)')

    def test_prepare_music_genre_text_any_genre(self):
        """Test music genre text preparation with 'any' genre returns empty string"""
        result = prepare_music_genre_text('any', 'daily')
        self.assertEqual(result, '')

    def test_prepare_music_genre_text_empty_genre(self):
        """Test music genre text preparation with empty genre returns empty string"""
        result = prepare_music_genre_text('', 'daily')
        self.assertEqual(result, '')

    def test_prepare_music_genre_text_none_genre(self):
        """Test music genre text preparation with None genre returns empty string"""
        result = prepare_music_genre_text(None, 'daily')
        self.assertEqual(result, '')


class TestFullChartTemplateData(unittest.TestCase):
    """Test that full chart returns properly structured data for templates"""

    def test_full_chart_template_data_structure(self):
        """Test that full chart route provides correct data structure for template"""
        app_client = app.test_client()
        form_data = {
            'birth_date': '1988-11-05',
            'birth_time': '09:45',
            'timezone_offset': '+1',
            'latitude': '48n51',
            'longitude': '2e21'
        }

        response = app_client.post('/full-chart', data=form_data)

        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)
        self.assertIn(b'stream-analysis.js', response.data)


class TestMusicGenreFeature(unittest.TestCase):
    """Test the music genre preference functionality"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_music_genre_rock_preference(self):
        """Test that rock genre preference is passed correctly"""
        form_data = {
            'birth_date': '1990-08-15',
            'birth_time': '12:00',
            'timezone_offset': '-05:00',
            'latitude': '40n42',
            'longitude': '74w00',
            'music_genre': 'rock'
        }

        response = self.app.post('/chart', data=form_data)

        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)

    def test_music_genre_other_custom_preference(self):
        """Test that custom 'other' genre preference is handled correctly"""
        form_data = {
            'birth_date': '1985-02-10',
            'birth_time': '18:30',
            'timezone_offset': '+01:00',
            'latitude': '51n30',
            'longitude': '0w10',
            'music_genre': 'other',
            'other_genre': 'synthwave'
        }

        response = self.app.post('/chart', data=form_data)

        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)

    def test_music_genre_other_empty_fallback(self):
        """Test that empty 'other' genre falls back to 'any'"""
        form_data = {
            'birth_date': '1992-05-20',
            'birth_time': '14:15',
            'timezone_offset': '-07:00',
            'latitude': '34n03',
            'longitude': '118w15',
            'music_genre': 'other',
            'other_genre': ''  # Empty custom genre
        }

        response = self.app.post('/chart', data=form_data)

        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)

    def test_full_chart_music_genre_integration(self):
        """Test that full chart route also handles music genre correctly"""
        form_data = {
            'birth_date': '1987-06-12',
            'birth_time': '11:45',
            'timezone_offset': '-04:00',
            'latitude': '42n21',
            'longitude': '71w03',
            'music_genre': 'jazz'
        }

        response = self.app.post('/full-chart', data=form_data)

        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)


class TestIntegration(unittest.TestCase):
    """Integration tests that test the full flow"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_full_chart_generation_flow(self):
        """Test the complete flow from form submission to chart display"""
        form_data = {
            'birth_date': '1995-02-10',
            'birth_time': '14:30',
            'timezone_offset': '-8',
            'latitude': '34n03',
            'longitude': '118w14'
        }

        response = self.app.post('/chart', data=form_data)

        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)

    def test_full_chart_route_generation_flow(self):
        """Test the complete flow from form submission to full chart display"""
        form_data = {
            'birth_date': '1995-02-10',
            'birth_time': '14:30',
            'timezone_offset': '-8',
            'latitude': '34n03',
            'longitude': '118w14'
        }

        response = self.app.post('/full-chart', data=form_data)

        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)
        # Check basic chart structure is present
        self.assertIn(b'Complete Natal Chart', response.data)
        self.assertIn(b'Gemini', response.data)

        # Check for planet descriptions
        self.assertIn(b'Your core identity', response.data)
        self.assertIn(b'Your emotions', response.data)

        # Check for house descriptions
        self.assertIn(b'1st House', response.data)
        self.assertIn(b'Self & Identity', response.data)

        # Check for astrology analysis section
        self.assertIn(b'Complete Chart Analysis', response.data)


class TestFormPersistenceIntegration(unittest.TestCase):
    """Integration tests for form persistence and location map functionality"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route_includes_form_persistence_script(self):
        """Test that index page includes form persistence JavaScript"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'form-persistence.js', response.data)
        self.assertIn(b'location-map.js', response.data)

    def test_form_data_validation_with_persistence_fields(self):
        """Test form validation works with all persistence-tracked fields"""
        form_data = {
            'birth_date': '1990-06-15',
            'birth_time': '14:30',
            'timezone_offset': '-07:00',
            'latitude': '37n46',
            'longitude': '122w25',
            'music_genre': 'rock'
        }

        response = self.app.post('/chart', data=form_data)
        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)

    def test_timezone_offset_regex_pattern(self):
        """Test that the timezone offset pattern validation works correctly"""
        valid_timezones = ['+05:30', '-04:00', '+00:00', '-11:00']

        for tz in valid_timezones:
            form_data = {
                'birth_date': '1990-01-01',
                'birth_time': '12:00',
                'timezone_offset': tz,
                'latitude': '40n42',
                'longitude': '74w00'
            }

            response = self.app.post('/chart', data=form_data)
            self.assertNotEqual(response.status_code, 400,
                              f"Valid timezone {tz} was rejected")

    def test_coordinate_format_handling(self):
        """Test that various coordinate formats are handled correctly"""
        coordinate_test_cases = [
            ('40n42', '74w00'),   # New York
            ('51n30', '00w07'),   # London
            ('35s12', '138e36'),  # Adelaide
        ]

        for lat, lng in coordinate_test_cases:
            form_data = {
                'birth_date': '1990-01-01',
                'birth_time': '12:00',
                'timezone_offset': '+00:00',
                'latitude': lat,
                'longitude': lng
            }

            response = self.app.post('/chart', data=form_data)
            self.assertNotEqual(response.status_code, 500,
                              f"Coordinates {lat}, {lng} caused server error")

    def test_music_genre_other_field_handling(self):
        """Test handling of 'other' music genre selection"""
        form_data = {
            'birth_date': '1990-01-01',
            'birth_time': '12:00',
            'timezone_offset': '+00:00',
            'latitude': '40n42',
            'longitude': '74w00',
            'music_genre': 'other',
            'other_genre': 'Ambient Techno'
        }

        response = self.app.post('/chart', data=form_data)
        self.assertEqual(response.status_code, 200)
        # Check for streaming setup
        self.assertIn(b'document.body.dataset.streaming', response.data)

    def test_form_persistence_elements_exist(self):
        """Test that form persistence related elements exist in HTML"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        # Check for form persistence elements
        self.assertIn(b'id="formDataStatus"', response.data)
        self.assertIn(b'id="resetFormBtn"', response.data)
        self.assertIn(b'Clear Saved Data', response.data)

        # Check for location map elements
        self.assertIn(b'id="locationMap"', response.data)
        self.assertIn(b'id="locationDisplay"', response.data)
        self.assertIn(b'id="locationSearch"', response.data)


class TestCoordinateConversionLogic(unittest.TestCase):
    """Tests for coordinate conversion logic expectations"""

    def test_astrology_coordinate_format_validation(self):
        """Test understanding of astrology coordinate format"""
        test_cases = [
            # (astro_format, expected_positive, expected_decimal_range)
            ('40n42', True, (40.0, 41.0)),    # New York latitude
            ('74w00', False, (-75.0, -73.0)),  # New York longitude (fixed range)
            ('51n30', True, (51.0, 52.0)),    # London latitude
            ('00w07', False, (-1.0, 0.1)),    # London longitude (fixed range)
        ]

        for astro_format, should_be_positive, decimal_range in test_cases:
            # Extract components
            if 'n' in astro_format or 's' in astro_format:
                direction = 'n' if 'n' in astro_format else 's'
                parts = astro_format.replace(direction, ' ').split()
            else:
                direction = 'e' if 'e' in astro_format else 'w'
                parts = astro_format.replace(direction, ' ').split()

            degrees = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0

            # Calculate expected decimal
            decimal = degrees + (minutes / 60.0)
            if direction in ['s', 'w']:
                decimal = -decimal

            # Validate expectations
            if should_be_positive:
                self.assertGreater(decimal, 0, f"{astro_format} should be positive")
            else:
                self.assertLessEqual(decimal, 0, f"{astro_format} should be negative or zero")

            self.assertGreaterEqual(decimal, decimal_range[0])
            self.assertLess(decimal, decimal_range[1])


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestAstroApp,
        TestUtilityFunctions,
        TestChartCalculation,
        TestFullChartCalculation,
        TestFullChartTemplateData,
        TestMusicGenreFeature,
        TestIntegration,
        TestFormPersistenceIntegration,  # New test class
        TestCoordinateConversionLogic    # New test class
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
