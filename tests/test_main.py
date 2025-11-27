import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the parent directory to the path to import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, calculate_chart, calculate_full_chart, format_planets_for_api, markdown_filter, prepare_music_genre_text, calculate_live_mas


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
    
    def test_full_chart_route_missing_data(self):
        """Test full chart route with missing form data"""
        response = self.app.post('/full-chart', data={})
        # Should return 400 or redirect to error page
        self.assertIn(response.status_code, [400, 500])
    
    def test_full_chart_route_valid_data(self):
        """Test full chart route with valid form data"""
        form_data = {
            'birth_date': '1990-01-15',
            'birth_time': '12:00',
            'timezone_offset': '-5',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        }
        
        with patch('main.calculate_full_chart') as mock_calc:
            mock_calc.return_value = {
                'sun': 'Capricorn',
                'moon': 'Leo',
                'ascendant': 'Virgo',
                'planets': {
                    'Sun': {'sign': 'Capricorn', 'degree': 25.5, 'house': 4},
                    'Moon': {'sign': 'Leo', 'degree': 12.3, 'house': 11},
                    'Mercury': {'sign': 'Sagittarius', 'degree': 8.7, 'house': 3}
                },
                'houses': {
                    1: {'sign': 'Virgo', 'degree': 15.0, 'planets': []},
                    2: {'sign': 'Libra', 'degree': 20.5, 'planets': []}
                }
            }
            
            response = self.app.post('/full-chart', data=form_data)
            self.assertEqual(response.status_code, 200)
            mock_calc.assert_called_once()
    
    def test_live_mas_route_missing_data(self):
        """Test live-mas route with missing form data"""
        response = self.app.post('/live-mas', data={})
        # Should return 400 or 500 for missing data, or 200 with error in response body
        self.assertIn(response.status_code, [200, 400, 500])
        if response.status_code == 200:
            self.assertIn(b'Error', response.data)
    
    def test_live_mas_route_valid_data(self):
        """Test live-mas route with valid form data"""
        form_data = {
            'birth_date': '1990-01-15',
            'birth_time': '12:00',
            'timezone_offset': '-5',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        }
        
        with patch('main.calculate_live_mas') as mock_calc:
            mock_calc.return_value = {
                'sun': 'Capricorn',
                'moon': 'Leo',
                'ascendant': 'Virgo',
                'mercury_retrograde': False,
                'taco_bell_order': '🌮 Test Taco Bell order based on cosmic energy!'
            }
            
            response = self.app.post('/live-mas', data=form_data)
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
        
        # Mock Anthropic client
        with patch('main.client') as mock_client:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Test astrology analysis")]
            mock_client.messages.create.return_value = mock_response
            
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
        mock_client.messages.create.side_effect = Exception("API Error")
        
        result = calculate_chart(
            '1990/01/15', '12:00', '-5', 40.7128, -74.0060
        )
        
        self.assertIn('cosmic coffee break', result['astrology_analysis'])

    @patch('main.datetime')
    @patch('main.Chart')
    @patch('main.client')
    def test_calculate_chart_music_genre_default_any(self, mock_client, mock_chart, mock_dt):
        """Test that calculate_chart defaults to 'any' when no music_genre is specified"""
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
        
        # Mock Anthropic client to capture the prompt
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test astrology analysis")]
        mock_client.messages.create.return_value = mock_response
        
        # Call without music_genre parameter (should default to "any")
        result = calculate_chart(
            '1990/01/15', '12:00', '-5', 40.7128, -74.0060
        )
        
        # Verify the API was called
        self.assertTrue(mock_client.messages.create.called)
        
        # Get the actual prompt that was sent to the API
        call_args = mock_client.messages.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[0]['content']
        
        # Verify the user prompt contains "Music Preference: any"
        self.assertIn('Music Preference: any', user_message)
        
        # Verify result structure
        self.assertEqual(result['sun'], 'Capricorn')
        self.assertEqual(result['moon'], 'Leo')
        self.assertEqual(result['ascendant'], 'Virgo')

    @patch('main.datetime')
    @patch('main.Chart')
    @patch('main.client')
    def test_calculate_chart_music_genre_explicit_any(self, mock_client, mock_chart, mock_dt):
        """Test that calculate_chart handles explicit 'any' music_genre correctly"""
        # Mock datetime
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: {
            '%Y/%m/%d': '2024/01/15',
            '%H:%M': '12:00'
        }[fmt]
        
        # Setup mock chart
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
        
        # Mock Anthropic client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test astrology analysis")]
        mock_client.messages.create.return_value = mock_response
        
        # Call with explicit "any" music_genre
        result = calculate_chart(
            '1990/01/15', '12:00', '-5', 40.7128, -74.0060, music_genre="any"
        )
        
        # Get the actual prompt that was sent to the API
        call_args = mock_client.messages.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[0]['content']
        
        # Verify the user prompt contains "Music Preference: any"
        self.assertIn('Music Preference: any', user_message)

    @patch('main.datetime')
    @patch('main.Chart')
    @patch('main.client')
    def test_calculate_chart_music_genre_specific_genre(self, mock_client, mock_chart, mock_dt):
        """Test that calculate_chart handles specific music genres correctly"""
        # Mock datetime
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: {
            '%Y/%m/%d': '2024/01/15',
            '%H:%M': '12:00'
        }[fmt]
        
        # Setup mock chart
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
        
        # Mock Anthropic client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test astrology analysis")]
        mock_client.messages.create.return_value = mock_response
        
        # Call with specific music genre
        result = calculate_chart(
            '1990/01/15', '12:00', '-5', 40.7128, -74.0060, music_genre="jazz"
        )
        
        # Get the actual prompt that was sent to the API
        call_args = mock_client.messages.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[0]['content']
        
        # Verify the user prompt contains the jazz preference text
        self.assertIn('Music Preference: (Please prioritize jazz genre if possible)', user_message)

    @patch('main.datetime')
    @patch('main.Chart')
    @patch('main.client')
    def test_calculate_chart_music_genre_empty_string(self, mock_client, mock_chart, mock_dt):
        """Test that calculate_chart handles empty string music_genre correctly by falling back to 'any'"""
        # Mock datetime
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: {
            '%Y/%m/%d': '2024/01/15',
            '%H:%M': '12:00'
        }[fmt]
        
        # Setup mock chart
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
        
        # Mock Anthropic client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test astrology analysis")]
        mock_client.messages.create.return_value = mock_response
        
        # Call with empty string music_genre
        result = calculate_chart(
            '1990/01/15', '12:00', '-5', 40.7128, -74.0060, music_genre=""
        )
        
        # Get the actual prompt that was sent to the API
        call_args = mock_client.messages.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[0]['content']
        
        # Verify the user prompt contains "Music Preference: any" (fallback)
        self.assertIn('Music Preference: any', user_message)

    @patch('main.datetime')
    @patch('main.Chart')  
    @patch('main.client')
    def test_calculate_chart_music_genre_other(self, mock_client, mock_chart, mock_dt):
        """Test that calculate_chart handles 'other' music_genre correctly"""
        # Mock datetime
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: {
            '%Y/%m/%d': '2024/01/15',
            '%H:%M': '12:00'
        }[fmt]
        
        # Setup mock chart
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
        
        # Mock Anthropic client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test astrology analysis")]
        mock_client.messages.create.return_value = mock_response
        
        # Call with "other" music_genre
        result = calculate_chart(
            '1990/01/15', '12:00', '-5', 40.7128, -74.0060, music_genre="other"
        )
        
        # Get the actual prompt that was sent to the API
        call_args = mock_client.messages.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[0]['content']
        
        # Verify the user prompt contains the "other" preference text
        self.assertIn('Music Preference: (Please suggest songs from any genre that fits the vibe)', user_message)


class TestFullChartCalculation(unittest.TestCase):
    
    @patch('main.Chart')
    @patch('main.Datetime')
    @patch('main.GeoPos')
    def test_calculate_full_chart_basic(self, mock_geopos, mock_datetime, mock_chart):
        """Test basic full chart calculation with mocked dependencies"""
        # Mock chart objects
        mock_sun = MagicMock()
        mock_sun.sign = 'Capricorn'
        mock_sun.signlon = 25.5
        
        mock_moon = MagicMock()
        mock_moon.sign = 'Leo'
        mock_moon.signlon = 12.3
        
        mock_ascendant = MagicMock()
        mock_ascendant.sign = 'Virgo'
        
        # Mock planet objects
        mock_mercury = MagicMock()
        mock_mercury.sign = 'Sagittarius'
        mock_mercury.signlon = 8.7
        mock_mercury.id = 'Mercury'
        
        mock_venus = MagicMock()
        mock_venus.sign = 'Aquarius'
        mock_venus.signlon = 18.2
        mock_venus.id = 'Venus'
        
        # Mock house objects
        mock_house1 = MagicMock()
        mock_house1.id = 'House1'
        mock_house1.sign = 'Virgo'
        mock_house1.signlon = 15.0
        
        mock_house2 = MagicMock()
        mock_house2.id = 'House2'
        mock_house2.sign = 'Libra'
        mock_house2.signlon = 20.5
        
        # Mock chart instance
        mock_chart_instance = MagicMock()
        mock_chart_instance.get.side_effect = lambda x: {
            'Sun': mock_sun,
            'Moon': mock_moon,
            'House1': mock_ascendant,
            'Mercury': mock_mercury,
            'Venus': mock_venus
        }.get(x)
        
        mock_chart_instance.houses = [mock_house1, mock_house2]
        
        # Mock objects in house
        mock_objects_in_house = MagicMock()
        mock_objects_in_house.getObjectsInHouse.return_value = [mock_mercury]
        mock_chart_instance.objects = mock_objects_in_house
        
        mock_chart.return_value = mock_chart_instance
        
        result = calculate_full_chart(
            '1990/01/15', '12:00', '-5', 40.7128, -74.0060
        )
        
        # Test basic structure
        self.assertEqual(result['sun'], 'Capricorn')
        self.assertEqual(result['moon'], 'Leo')
        self.assertEqual(result['ascendant'], 'Virgo')
        self.assertIn('planets', result)
        self.assertIn('houses', result)
        
        # Test planets data
        self.assertIn('Sun', result['planets'])
        self.assertEqual(result['planets']['Sun']['sign'], 'Capricorn')
        self.assertEqual(result['planets']['Sun']['degree'], 25.5)
        
        # Test houses data
        self.assertIn(1, result['houses'])
        self.assertEqual(result['houses'][1]['sign'], 'Virgo')
        self.assertEqual(result['houses'][1]['degree'], 15.0)
    
    @patch('main.Chart')
    @patch('main.Datetime')
    @patch('main.GeoPos')
    def test_calculate_full_chart_with_planets_in_houses(self, mock_geopos, mock_datetime, mock_chart):
        """Test full chart calculation with planets placed in houses"""
        # Mock basic chart objects
        mock_sun = MagicMock()
        mock_sun.sign = 'Leo'
        mock_moon = MagicMock()
        mock_moon.sign = 'Scorpio'
        mock_ascendant = MagicMock()
        mock_ascendant.sign = 'Gemini'
        
        # Mock planet in house
        mock_jupiter = MagicMock()
        mock_jupiter.sign = 'Pisces'
        mock_jupiter.signlon = 14.8
        mock_jupiter.id = 'Jupiter'
        
        # Mock house
        mock_house5 = MagicMock()
        mock_house5.id = 'House5'
        mock_house5.sign = 'Libra'
        mock_house5.signlon = 10.0
        
        mock_chart_instance = MagicMock()
        mock_chart_instance.get.side_effect = lambda x: {
            'Sun': mock_sun,
            'Moon': mock_moon,
            'House1': mock_ascendant,
            'Jupiter': mock_jupiter
        }.get(x)
        
        mock_chart_instance.houses = [mock_house5]
        
        # Mock planet placement in house
        mock_objects_in_house = MagicMock()
        mock_objects_in_house.getObjectsInHouse.return_value = [mock_jupiter]
        mock_chart_instance.objects = mock_objects_in_house
        
        mock_chart.return_value = mock_chart_instance
        
        result = calculate_full_chart(
            '1985/06/20', '18:30', '+2', 51.5074, -0.1278
        )
        
        # Test that Jupiter is in the houses data
        self.assertIn(5, result['houses'])
        self.assertEqual(len(result['houses'][5]['planets']), 1)
        self.assertEqual(result['houses'][5]['planets'][0]['name'], 'Jupiter')
        self.assertEqual(result['houses'][5]['planets'][0]['sign'], 'Pisces')
        
        # Test that Jupiter has house information
        self.assertIn('Jupiter', result['planets'])
        self.assertEqual(result['planets']['Jupiter']['house'], 5)
    
    @patch('main.Chart')
    def test_calculate_full_chart_error_handling(self, mock_chart):
        """Test full chart calculation handles errors gracefully"""
        # Mock chart that raises an exception for some planets
        mock_chart_instance = MagicMock()
        mock_chart_instance.get.side_effect = lambda x: {
            'Sun': MagicMock(sign='Leo'),
            'Moon': MagicMock(sign='Cancer'),
            'House1': MagicMock(sign='Virgo')
        }.get(x) if x in ['Sun', 'Moon', 'House1'] else None
        
        mock_chart_instance.houses = []
        mock_chart.return_value = mock_chart_instance
        
        # Should not raise an exception
        result = calculate_full_chart(
            '1990/01/01', '00:00', '0', 0, 0
        )
        
        self.assertEqual(result['sun'], 'Leo')
        self.assertEqual(result['moon'], 'Cancer')
        self.assertEqual(result['ascendant'], 'Virgo')


class TestFullChartTemplateData(unittest.TestCase):
    """Test that full chart returns properly structured data for templates"""
    
    @patch('main.calculate_full_chart')
    def test_full_chart_template_data_structure(self, mock_calc):
        """Test that full chart route provides correct data structure for template"""
        # Mock comprehensive chart data
        mock_calc.return_value = {
            'sun': 'Scorpio',
            'moon': 'Taurus',
            'ascendant': 'Cancer',
            'planets': {
                'Sun': {'sign': 'Scorpio', 'degree': 15.5, 'house': 5},
                'Moon': {'sign': 'Taurus', 'degree': 22.3, 'house': 11},
                'Mercury': {'sign': 'Libra', 'degree': 8.7, 'house': 4},
                'Venus': {'sign': 'Virgo', 'degree': 29.1, 'house': 3},
                'Mars': {'sign': 'Capricorn', 'degree': 12.8, 'house': 7},
                'Jupiter': {'sign': 'Pisces', 'degree': 5.4, 'house': 9},
                'Saturn': {'sign': 'Aquarius', 'degree': 18.9, 'house': 8},
                'Uranus': {'sign': 'Taurus', 'degree': 11.2, 'house': 11},
                'Neptune': {'sign': 'Pisces', 'degree': 24.6, 'house': 9},
                'Pluto': {'sign': 'Capricorn', 'degree': 26.3, 'house': 7},
                'Chiron': {'sign': 'Aries', 'degree': 9.7, 'house': 10}
            },
            'houses': {
                i: {
                    'sign': ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'][i-1],
                    'degree': 15.0 + i,
                    'planets': []
                } for i in range(1, 13)
            },
            'astrology_analysis': '✨ **Your Chart Vibes:** This is a powerful and transformative chart! 🔥\n\n• Do: Embrace your intensity\n• Don\'t: Ignore your intuition\n• Song: "Bohemian Rhapsody" by Queen 🎵'
        }
        
        app_client = app.test_client()
        form_data = {
            'birth_date': '1988-11-05',
            'birth_time': '09:45',
            'timezone_offset': '+1',
            'latitude': '48.8566',
            'longitude': '2.3522'
        }
        
        response = app_client.post('/full-chart', data=form_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Check that response contains all expected planets
        planet_names = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                       'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron']
        for planet in planet_names:
            self.assertIn(planet.encode(), response.data)
        
        # Check that all houses are represented
        for i in range(1, 13):
            house_text = f"{i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'} House"
            self.assertIn(house_text.encode(), response.data)
        
        # Check that astrology analysis is present
        self.assertIn(b'Your Chart Vibes', response.data)
        self.assertIn(b'Complete Chart Analysis', response.data)
        self.assertIn(b'copy-analysis.js', response.data)
        
        mock_calc.assert_called_once_with(
            '1988/11/05', '09:45', '+1', '48.8566', '2.3522', 'any'
        )


class TestMusicGenreFeature(unittest.TestCase):
    """Test the music genre preference functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    @patch('main.calculate_chart')
    def test_music_genre_rock_preference(self, mock_calc):
        """Test that rock genre preference is passed correctly"""
        mock_calc.return_value = {
            'sun': 'Leo',
            'moon': 'Virgo',
            'ascendant': 'Scorpio',
            'mercury_retrograde': False,
            'astrology_analysis': '🎸 Rock on! Your Leo sun loves the spotlight like a rockstar! 🌟'
        }
        
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
        mock_calc.assert_called_once_with(
            '1990/08/15', '12:00', '-05:00', '40n42', '74w00', 'rock'
        )

    @patch('main.calculate_chart')
    def test_music_genre_other_custom_preference(self, mock_calc):
        """Test that custom 'other' genre preference is handled correctly"""
        mock_calc.return_value = {
            'sun': 'Aquarius',
            'moon': 'Pisces',
            'ascendant': 'Gemini',
            'mercury_retrograde': True,
            'astrology_analysis': '🎵 Synthwave vibes for your futuristic Aquarius energy! ✨'
        }
        
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
        mock_calc.assert_called_once_with(
            '1985/02/10', '18:30', '+01:00', '51n30', '0w10', 'synthwave'
        )

    @patch('main.calculate_chart')
    def test_music_genre_other_empty_fallback(self, mock_calc):
        """Test that empty 'other' genre falls back to 'any'"""
        mock_calc.return_value = {
            'sun': 'Taurus',
            'moon': 'Cancer',
            'ascendant': 'Virgo',
            'mercury_retrograde': False,
            'astrology_analysis': '🌟 Any genre works for your versatile chart! 🎶'
        }
        
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
        mock_calc.assert_called_once_with(
            '1992/05/20', '14:15', '-07:00', '34n03', '118w15', 'any'
        )

    @patch('main.calculate_full_chart')
    def test_full_chart_music_genre_integration(self, mock_calc):
        """Test that full chart route also handles music genre correctly"""
        mock_calc.return_value = {
            'sun': 'Gemini',
            'moon': 'Sagittarius',
            'ascendant': 'Pisces',
            'planets': {'Sun': {'sign': 'Gemini', 'degree': 15.5, 'house': 4}},
            'houses': {1: {'sign': 'Pisces', 'degree': 0.0, 'planets': []}},
            'astrology_analysis': '🎺 Jazz rhythms match your complex Gemini-Sagittarius energy! 🎷'
        }
        
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
        mock_calc.assert_called_once_with(
            '1987/06/12', '11:45', '-04:00', '42n21', '71w03', 'jazz'
        )


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
    
    @patch('main.calculate_full_chart')
    def test_full_chart_generation_flow(self, mock_calc):
        """Test the complete flow from form submission to full chart display"""
        mock_calc.return_value = {
            'sun': 'Aquarius',
            'moon': 'Pisces', 
            'ascendant': 'Gemini',
            'planets': {
                'Sun': {'sign': 'Aquarius', 'degree': 20.5, 'house': 9},
                'Moon': {'sign': 'Pisces', 'degree': 15.3, 'house': 10},
                'Mercury': {'sign': 'Capricorn', 'degree': 8.7, 'house': 8}
            },
            'houses': {
                1: {'sign': 'Gemini', 'degree': 15.0, 'planets': []},
                2: {'sign': 'Cancer', 'degree': 20.5, 'planets': []},
                3: {'sign': 'Leo', 'degree': 25.0, 'planets': []},
                4: {'sign': 'Virgo', 'degree': 30.0, 'planets': []},
                5: {'sign': 'Libra', 'degree': 35.0, 'planets': []},
                6: {'sign': 'Scorpio', 'degree': 40.0, 'planets': []},
                7: {'sign': 'Sagittarius', 'degree': 45.0, 'planets': []},
                8: {'sign': 'Capricorn', 'degree': 50.0, 'planets': []},
                9: {'sign': 'Aquarius', 'degree': 55.0, 'planets': []},
                10: {'sign': 'Pisces', 'degree': 60.0, 'planets': []},
                11: {'sign': 'Aries', 'degree': 65.0, 'planets': []},
                12: {'sign': 'Taurus', 'degree': 70.0, 'planets': []}
            },
            'astrology_analysis': '🌟 **Your Vibe:** Air sign energy with water moon = dreamy innovator! ✨\n\n• Do: Trust your intuition\n• Don\'t: Overthink everything\n• Song: "Imagine" by John Lennon 🎵'
        }
        
        form_data = {
            'birth_date': '1995-02-10',
            'birth_time': '14:30',
            'timezone_offset': '-8',
            'latitude': '34.0522',
            'longitude': '-118.2437'
        }
        
        response = self.app.post('/full-chart', data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Complete Natal Chart', response.data)
        self.assertIn(b'Aquarius', response.data)
        self.assertIn(b'Pisces', response.data)
        self.assertIn(b'Gemini', response.data)
        
        # Check for planet descriptions
        self.assertIn(b'Your core identity', response.data)
        self.assertIn(b'Your emotions', response.data)
        
        # Check for house descriptions
        self.assertIn(b'1st House', response.data)
        self.assertIn(b'Self & Identity', response.data)
        
        # Check for astrology analysis
        self.assertIn(b'Complete Chart Analysis', response.data)
        self.assertIn(b'dreamy innovator', response.data)
        
        mock_calc.assert_called_once_with(
            '1995/02/10', '14:30', '-8', '34.0522', '-118.2437', 'any'
        )


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
        
        with patch('main.calculate_chart') as mock_calc:
            mock_calc.return_value = {
                'sun': 'Gemini',
                'moon': 'Pisces',
                'ascendant': 'Leo',
                'mercury_retrograde': False,
                'astrology_analysis': 'Test analysis'
            }
            
            response = self.app.post('/chart', data=form_data)
            self.assertEqual(response.status_code, 200)
            mock_calc.assert_called_once()
    
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
            
            with patch('main.calculate_chart') as mock_calc:
                mock_calc.return_value = {
                    'sun': 'Capricorn', 'moon': 'Leo', 'ascendant': 'Virgo',
                    'mercury_retrograde': False, 'astrology_analysis': 'Test'
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
            
            with patch('main.calculate_chart') as mock_calc:
                mock_calc.return_value = {
                    'sun': 'Capricorn', 'moon': 'Leo', 'ascendant': 'Virgo',
                    'mercury_retrograde': False, 'astrology_analysis': 'Test'
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
        
        with patch('main.calculate_chart') as mock_calc:
            mock_calc.return_value = {
                'sun': 'Capricorn', 'moon': 'Leo', 'ascendant': 'Virgo',
                'mercury_retrograde': False, 'astrology_analysis': 'Test with Ambient Techno'
            }
            
            response = self.app.post('/chart', data=form_data)
            self.assertEqual(response.status_code, 200)
            
            # The custom genre should be passed to the calculation
            args, kwargs = mock_calc.call_args
            self.assertEqual(kwargs.get('music_genre') or args[5], 'Ambient Techno')
    
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
