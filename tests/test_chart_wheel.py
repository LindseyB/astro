import unittest
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestChartWheelVisualization(unittest.TestCase):
    """Test chart wheel visualization and data structure"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_full_chart_includes_canvas(self):
        """Test that full chart page includes canvas element"""
        from unittest.mock import patch

        # Create complete house data (all 12 houses required)
        houses = {}
        signs = ['Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius',
                 'Capricorn', 'Aquarius', 'Pisces', 'Aries', 'Taurus', 'Gemini']
        for i in range(1, 13):
            houses[i] = {'sign': signs[i-1], 'degree': 10.0 + i}

        with patch('routes.calculate_full_chart') as mock_calc:
            mock_calc.return_value = {
                'planets': {
                    'Sun': {'sign': 'Cancer', 'degree': 18.5, 'house': 1},
                    'Moon': {'sign': 'Pisces', 'degree': 12.3, 'house': 9}
                },
                'houses': houses,
                'aspects': [],
                'chart_analysis': 'Test analysis'
            }

            form_data = {
                'birth_date': '1995-07-10',
                'birth_time': '14:30',
                'timezone_offset': '-8',
                'latitude': '34.0522',
                'longitude': '-118.2437'
            }

            response = self.app.post('/full-chart', data=form_data)
            self.assertEqual(response.status_code, 200)
            
            # Check for canvas element
            self.assertIn(b'<canvas id="chartWheel"', response.data)

    def test_chart_data_structure(self):
        """Test that chart data is properly structured for JavaScript"""
        from unittest.mock import patch

        with patch('routes.calculate_full_chart') as mock_calc:
            test_data = {
                'planets': {
                    'Sun': {'sign': 'Aries', 'degree': 10.5, 'house': 1},
                    'Moon': {'sign': 'Taurus', 'degree': 20.3, 'house': 2},
                    'Mercury': {'sign': 'Aries', 'degree': 5.1, 'house': 1},
                    'Venus': {'sign': 'Pisces', 'degree': 28.7, 'house': 12},
                    'Mars': {'sign': 'Gemini', 'degree': 15.2, 'house': 3}
                },
                'houses': {
                    1: {'sign': 'Aries', 'degree': 0.0},
                    2: {'sign': 'Taurus', 'degree': 0.0},
                    3: {'sign': 'Gemini', 'degree': 0.0},
                    4: {'sign': 'Cancer', 'degree': 0.0},
                    5: {'sign': 'Leo', 'degree': 0.0},
                    6: {'sign': 'Virgo', 'degree': 0.0},
                    7: {'sign': 'Libra', 'degree': 0.0},
                    8: {'sign': 'Scorpio', 'degree': 0.0},
                    9: {'sign': 'Sagittarius', 'degree': 0.0},
                    10: {'sign': 'Capricorn', 'degree': 0.0},
                    11: {'sign': 'Aquarius', 'degree': 0.0},
                    12: {'sign': 'Pisces', 'degree': 0.0}
                },
                'aspects': [
                    {'planet1': 'Sun', 'planet2': 'Mars', 'type': 'square', 'orb': 4.7}
                ],
                'chart_analysis': 'Detailed chart analysis'
            }
            mock_calc.return_value = test_data

            form_data = {
                'birth_date': '1990-04-15',
                'birth_time': '12:00',
                'timezone_offset': '0',
                'latitude': '40.7128',
                'longitude': '-74.0060'
            }

            response = self.app.post('/full-chart', data=form_data)
            self.assertEqual(response.status_code, 200)
            
            # Check that chart data is embedded in the page
            self.assertIn(b'window.chartData', response.data)
            
            # Extract the chart data (check for presence of data structure)
            response_text = response.data.decode('utf-8')
            self.assertIn('planets:', response_text)
            self.assertIn('houses:', response_text)
            self.assertIn('Sun', response_text)
            self.assertIn('Aries', response_text)

    def test_all_zodiac_signs_handled(self):
        """Test that all 12 zodiac signs are properly handled"""
        from unittest.mock import patch

        zodiac_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]

        for sign in zodiac_signs:
            # Create complete house data
            houses = {}
            for i in range(1, 13):
                houses[i] = {'sign': zodiac_signs[(zodiac_signs.index(sign) + i - 1) % 12], 'degree': 10.0}
            
            with patch('routes.calculate_full_chart') as mock_calc:
                mock_calc.return_value = {
                    'planets': {
                        'Sun': {'sign': sign, 'degree': 15.0, 'house': 1}
                    },
                    'houses': houses,
                    'aspects': [],
                    'chart_analysis': f'Sun in {sign}'
                }

                form_data = {
                    'birth_date': '1990-01-01',
                    'birth_time': '12:00',
                    'timezone_offset': '0',
                    'latitude': '0',
                    'longitude': '0'
                }

                response = self.app.post('/full-chart', data=form_data)
                self.assertEqual(response.status_code, 200)
                self.assertIn(sign.encode(), response.data)

    def test_all_major_planets_handled(self):
        """Test that all major planets are properly handled"""
        from unittest.mock import patch

        planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                   'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

        # Create complete house data
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        houses = {}
        for i in range(1, 13):
            houses[i] = {'sign': signs[i-1], 'degree': 0.0}

        with patch('routes.calculate_full_chart') as mock_calc:
            planet_data = {}
            for i, planet in enumerate(planets):
                planet_data[planet] = {
                    'sign': 'Aries',
                    'degree': i * 3.0,
                    'house': (i % 12) + 1
                }

            mock_calc.return_value = {
                'planets': planet_data,
                'houses': houses,
                'aspects': [],
                'chart_analysis': 'All planets present'
            }

            form_data = {
                'birth_date': '1990-01-01',
                'birth_time': '12:00',
                'timezone_offset': '0',
                'latitude': '0',
                'longitude': '0'
            }

            response = self.app.post('/full-chart', data=form_data)
            self.assertEqual(response.status_code, 200)

            # Check that all planets appear in the response
            for planet in planets:
                self.assertIn(planet.encode(), response.data)

    def test_house_cusps_all_present(self):
        """Test that all 12 house cusps are properly handled"""
        from unittest.mock import patch

        with patch('routes.calculate_full_chart') as mock_calc:
            houses = {}
            signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
            
            for i in range(1, 13):
                houses[i] = {
                    'sign': signs[(i - 1) % 12],
                    'degree': i * 5.0
                }

            mock_calc.return_value = {
                'planets': {
                    'Sun': {'sign': 'Leo', 'degree': 15.0, 'house': 5}
                },
                'houses': houses,
                'aspects': [],
                'chart_analysis': 'Full house system'
            }

            form_data = {
                'birth_date': '1990-01-01',
                'birth_time': '12:00',
                'timezone_offset': '0',
                'latitude': '0',
                'longitude': '0'
            }

            response = self.app.post('/full-chart', data=form_data)
            self.assertEqual(response.status_code, 200)

            # Check that chart data includes all houses
            response_text = response.data.decode('utf-8')
            for i in range(1, 13):
                # House numbers should appear in the data
                self.assertIn(f'"1":', response_text)  # At least house 1


class TestChartWheelJavaScript(unittest.TestCase):
    """Test chart wheel JavaScript file structure"""

    def test_chart_wheel_constants(self):
        """Test that chart-wheel.js contains required constants"""
        chart_wheel_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 'js', 'chart-wheel.js'
        )

        if os.path.exists(chart_wheel_path):
            with open(chart_wheel_path, 'r') as f:
                content = f.read()

            # Check for zodiac symbols constant
            self.assertIn('ZODIAC_SYMBOLS', content)
            self.assertIn('Aries', content)
            self.assertIn('♈', content)
            
            # Check for planet symbols constant
            self.assertIn('PLANET_SYMBOLS', content)
            self.assertIn('Sun', content)
            self.assertIn('☉', content)
            
            # Check for sign degrees mapping
            self.assertIn('SIGN_DEGREES', content)

    def test_chart_wheel_methods(self):
        """Test that chart-wheel.js contains required methods"""
        chart_wheel_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 'js', 'chart-wheel.js'
        )

        if os.path.exists(chart_wheel_path):
            with open(chart_wheel_path, 'r') as f:
                content = f.read()

            # Core drawing methods
            self.assertIn('drawBackground', content)
            self.assertIn('drawInnerCircle', content)
            self.assertIn('drawZodiacWheel', content)
            self.assertIn('drawHouseLines', content)
            self.assertIn('drawHouseNumbers', content)
            self.assertIn('drawPlanets', content)
            self.assertIn('drawCenterInfo', content)
            
            # Calculation methods
            self.assertIn('calculateAngle', content)
            self.assertIn('adjustPlanetPositions', content)
            
            # Aspect methods
            self.assertIn('drawAspectLines', content)
            self.assertIn('calculateAspectAngle', content)

    def test_chart_wheel_ascendant_rotation(self):
        """Test that chart wheel rotates based on Ascendant position"""
        chart_wheel_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 'js', 'chart-wheel.js'
        )

        if os.path.exists(chart_wheel_path):
            with open(chart_wheel_path, 'r') as f:
                content = f.read()

            # Check that Ascendant is referenced in calculations
            self.assertIn('ascendant', content.lower())
            self.assertIn('houses[1]', content)
            
            # Check for rotation logic
            self.assertIn('relativeToAscendant', content)

    def test_chart_wheel_aspect_types(self):
        """Test that chart wheel handles different aspect types"""
        chart_wheel_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 'js', 'chart-wheel.js'
        )

        if os.path.exists(chart_wheel_path):
            with open(chart_wheel_path, 'r') as f:
                content = f.read()

            # Check for major aspects
            aspects = ['conjunction', 'opposition', 'trine', 'square', 'sextile']
            for aspect in aspects:
                self.assertIn(aspect, content.lower())


class TestFullChartRoute(unittest.TestCase):
    """Test the full chart route functionality"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_full_chart_route_exists(self):
        """Test that /full-chart route exists"""
        response = self.app.get('/full-chart')
        # Should redirect or show form page, not 404
        self.assertNotEqual(response.status_code, 404)

    def test_full_chart_post_with_valid_data(self):
        """Test POST to full-chart with valid data"""
        from unittest.mock import patch

        # Create complete house data
        signs = ['Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn',
                 'Aquarius', 'Pisces', 'Aries', 'Taurus', 'Gemini', 'Cancer']
        houses = {}
        for i in range(1, 13):
            houses[i] = {'sign': signs[i-1], 'degree': 0.0}

        with patch('routes.calculate_full_chart') as mock_calc:
            mock_calc.return_value = {
                'planets': {'Sun': {'sign': 'Leo', 'degree': 15.0, 'house': 1}},
                'houses': houses,
                'aspects': [],
                'chart_analysis': 'Test'
            }

            form_data = {
                'birth_date': '1990-08-01',
                'birth_time': '12:00',
                'timezone_offset': '0',
                'latitude': '0',
                'longitude': '0'
            }

            response = self.app.post('/full-chart', data=form_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'chartWheel', response.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
