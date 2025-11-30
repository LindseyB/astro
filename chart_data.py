"""
Core chart data extraction functions
"""
from datetime import datetime
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
from config import PLANET_NAMES, PLANET_CONSTANTS, logger


def create_charts(birth_date, birth_time, timezone_offset, latitude, longitude):
    """
    Create natal and current charts

    Args:
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset (e.g., '+00:00')
        latitude (float): Latitude
        longitude (float): Longitude

    Returns:
        tuple: (natal_chart, today_chart)
    """
    now = datetime.now()
    current_date = now.strftime('%Y/%m/%d')
    current_time = now.strftime('%H:%M')

    # Setup charts
    dt = Datetime(birth_date, birth_time, timezone_offset)
    pos = GeoPos(latitude, longitude)
    chart = Chart(dt, pos, IDs=const.LIST_OBJECTS)
    today_chart = Chart(Datetime(current_date, current_time, timezone_offset), pos, IDs=const.LIST_OBJECTS)

    return chart, today_chart


def get_main_positions(chart):
    """
    Get sun, moon, and ascendant from chart

    Args:
        chart: flatlib Chart object

    Returns:
        tuple: (sun, moon, ascendant) objects
    """
    return chart.get('Sun'), chart.get('Moon'), chart.get('House1')


def get_planets_in_houses(chart):
    """
    Get all planets organized by houses

    Args:
        chart: flatlib Chart object

    Returns:
        dict: Dictionary keyed by house number with planet data
    """
    houses = chart.houses
    planets_in_houses = {}

    for house in houses:
        house_number = int(house.id.replace('House', ''))
        planets_in_houses[house_number] = {
            'house_obj': house,
            'planets': []
        }

        # Get all objects in this house
        objects_in_house = chart.objects.getObjectsInHouse(house)

        for obj in objects_in_house:
            if obj.id in PLANET_NAMES:
                planets_in_houses[house_number]['planets'].append({
                    'name': obj.id,
                    'sign': obj.sign,
                    'object': obj
                })

    return planets_in_houses


def get_current_planets(today_chart):
    """
    Get current planet positions and retrograde status

    Args:
        today_chart: flatlib Chart object for current date/time

    Returns:
        dict: Dictionary with planet positions and retrograde status
    """
    current_planets = {}

    for planet_name, planet_const in PLANET_CONSTANTS.items():
        try:
            planet_obj = today_chart.get(planet_const)
            # Check if planet object exists and has the required attributes
            if planet_obj and hasattr(planet_obj, 'sign') and hasattr(planet_obj, 'signlon'):
                retrograde = False

                # Sun and Moon don't go retrograde
                if planet_name not in ['Sun', 'Moon']:
                    if hasattr(planet_obj, 'isRetrograde'):
                        try:
                            retrograde = planet_obj.isRetrograde()
                        except Exception:
                            retrograde = False

                current_planets[planet_name] = {
                    'sign': planet_obj.sign,
                    'degree': float(planet_obj.signlon),
                    'retrograde': retrograde
                }
        except Exception as e:
            # Skip planets that cause errors but continue with others
            logger.warning(f"Could not get data for {planet_name}: {e}")
            continue

    return current_planets
