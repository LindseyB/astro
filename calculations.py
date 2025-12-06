"""
Chart calculation business logic
"""
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
from config import PLANET_CONSTANTS, HOUSE_NAMES, logger
from chart_data import create_charts, get_main_positions, get_planets_in_houses, get_current_planets
from formatters import prepare_music_genre_text, format_planets_for_api
from ai_service import call_ai_api


def calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre="any"):
    """
    Calculate daily horoscope with current transits

    Args:
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset
        latitude (float): Latitude
        longitude (float): Longitude
        music_genre (str): Music genre preference (default "any")

    Returns:
        dict: Chart data with sun, moon, ascendant, mercury_retrograde, and astrology_analysis
    """
    # Setup charts
    chart, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)

    # Calculate main positions
    sun, moon, ascendant = get_main_positions(chart)

    # Get planets in houses
    planets_in_houses = get_planets_in_houses(chart)

    # Get current planet statuses
    current_planets = get_current_planets(today_chart)

    # Generate AI analysis with error handling
    # Build the user prompt (music will be loaded separately via async call)
    user_prompt = "Only respond in a few sentences. Based on the following astrological chart data: First give a single sentence summarizing the day for the person getting the horoscope as a title for the horoscope and then please recommend some activities to do or not to do ideally in bullet format the first sentence in your response should be what today's vibe will be like please also recommend a beverage to drink given today's vibe:\n\n" + \
                  f"Sun: {sun.sign}, Moon: {moon.sign}, Ascendant: {ascendant.sign}\n\n" + \
                  "Planets in Houses:\n" + \
                  "\n".join([f"{HOUSE_NAMES[house_number]}: " + ", ".join([f"{p['name']} in {p['sign']}" for p in data['planets']]) for house_number, data in planets_in_houses.items()]) + "\n\n" + \
                  "Current Planets status:\n" + \
                  format_planets_for_api(current_planets)

    # Log the prompt to console
    logger.debug("=== USER PROMPT ===")
    logger.debug(user_prompt)
    logger.debug("=== END PROMPT ===")

    system_content = "You are a cool astrologer who uses lots of emojis and is very casual. You are also very concise and to the point. You are an expert in astrology and can analyze charts quickly. Never use any mdashes in your responses those just aren't cool."

    astrology_analysis = call_ai_api(system_content, user_prompt)
    if astrology_analysis is None:
        astrology_analysis = f"**Cosmic Note:** The AI astrologer is taking a cosmic tea break. ☕ Trust your intuition today! 🔮"

    return {
        'sun': sun.sign,
        'moon': moon.sign,
        'ascendant': ascendant.sign,
        'mercury_retrograde': current_planets.get('Mercury', {}).get('retrograde', False),
        'astrology_analysis': astrology_analysis
    }


def calculate_live_mas(birth_date, birth_time, timezone_offset, latitude, longitude):
    """
    Calculate Taco Bell order based on astrological data

    Args:
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset
        latitude (float): Latitude
        longitude (float): Longitude

    Returns:
        dict: Chart data with sun, moon, ascendant, mercury_retrograde, and taco_bell_order
    """
    # Setup charts
    chart, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)

    # Calculate main positions
    sun, moon, ascendant = get_main_positions(chart)

    # Get planets in houses
    planets_in_houses = get_planets_in_houses(chart)

    # Get current planet statuses
    current_planets = get_current_planets(today_chart)

    # Generate Taco Bell order with AI
    # Build the Taco Bell user prompt
    user_prompt = (
        "You are a cosmic Taco Bell expert! Based on this person's astrological chart, "
        "create a personalized Taco Bell order that matches their cosmic energy. "
        "Be creative, fun, and use lots of emojis! Be concise and use a bulleted list.:\n\n"
        f"Sun: {sun.sign}, Moon: {moon.sign}, Ascendant: {ascendant.sign}\n\n"
        "Planets in Houses:\n" +
        "\n".join([f"{HOUSE_NAMES[house_number]}: " + ", ".join([f"{p['name']} in {p['sign']}" for p in data['planets']]) for house_number, data in planets_in_houses.items()]) + "\n\n" +
        "Current Planets status:\n" +
        format_planets_for_api(current_planets)
    )

    system_content = "You are a cool astrologer who uses lots of emojis and is very casual. You are also very concise and to the point. You are an expert in astrology and can analyze charts and the taco bell menu quickly. Never use any mdashes in your responses those just aren't cool."

    taco_bell_order = call_ai_api(system_content, user_prompt, temperature=1)
    if taco_bell_order is None:
        taco_bell_order = "🌮 **Cosmic Note:** The cosmic Taco Bell oracle is taking a nacho break! ☕ Try a Crunchwrap Supreme - it's universally delicious! 🔔✨"

    return {
        'sun': sun.sign,
        'moon': moon.sign,
        'ascendant': ascendant.sign,
        'mercury_retrograde': current_planets.get('Mercury', {}).get('retrograde', False),
        'taco_bell_order': taco_bell_order
    }


def calculate_full_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre="any"):
    """
    Calculate comprehensive natal chart data

    Args:
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset
        latitude (float): Latitude
        longitude (float): Longitude
        music_genre (str): Music genre preference (default "any")

    Returns:
        dict: Comprehensive chart data with planets, houses, and astrology_analysis
    """
    # Setup chart
    dt = Datetime(birth_date, birth_time, timezone_offset)
    pos = GeoPos(latitude, longitude)
    chart = Chart(dt, pos, IDs=const.LIST_OBJECTS)

    # Calculate main positions
    sun = chart.get('Sun')
    moon = chart.get('Moon')
    ascendant = chart.get('House1')

    # Get all planets with detailed information
    planets = {}

    for planet_name, planet_const in PLANET_CONSTANTS.items():
        try:
            planet_obj = chart.get(planet_const)
            if planet_obj and hasattr(planet_obj, 'sign') and hasattr(planet_obj, 'signlon'):
                planets[planet_name] = {
                    'sign': planet_obj.sign,
                    'degree': float(planet_obj.signlon),
                    'house': None  # Will be filled below
                }
        except Exception as e:
            logger.warning(f"Could not get data for {planet_name}: {e}")
            continue

    # Get all houses and their objects
    houses = chart.houses
    house_data = {}

    for house in houses:
        house_number = int(house.id.replace('House', ''))
        house_data[house_number] = {
            'sign': house.sign,
            'degree': float(house.signlon),
            'planets': []
        }

        # Get all objects in this house
        objects_in_house = chart.objects.getObjectsInHouse(house)

        for obj in objects_in_house:
            if obj.id in planets:
                planets[obj.id]['house'] = house_number
                house_data[house_number]['planets'].append({
                    'name': obj.id,
                    'sign': obj.sign,
                    'degree': float(obj.signlon)
                })

    # Build the user prompt for the full chart (music will be loaded separately via async call)
    user_prompt = (
        "Only respond in a few sentences. Based on the following natal chart data, "
        "please give a concise, emoji-filled summary of this person's personality and life themes. "
        "Highlight any unique planetary placements or house patterns. "
        "Format your response in bullet points:\n\n"
        f"Sun: {sun.sign}, Moon: {moon.sign}, Ascendant: {ascendant.sign}\n\n"
        "Planets:\n" +
        "\n".join([
            f"- {name}: {data['sign']} at {data['degree']:.2f}° in House {data['house'] or 'N/A'}"
            for name, data in planets.items()
        ]) +
        "\n\nHouses:\n" +
        "\n".join([
            f"- House {num} ({house_data[num]['sign']} {house_data[num]['degree']:.2f}°): " +
            ", ".join([f"{p['name']} in {p['sign']} ({p['degree']:.2f}°)" for p in house_data[num]['planets']]) or "No major planets"
            for num in sorted(house_data.keys())
        ])
    )

    system_content = "You are a cool astrologer who uses lots of emojis and is very casual. You are also very concise and to the point. You are an expert in astrology and can analyze charts quickly. Never use any mdashes in your responses those just aren't cool."

    astrology_analysis = call_ai_api(system_content, user_prompt)
    if astrology_analysis is None:
        astrology_analysis = f"**Cosmic Note:** The AI astrologer is taking a cosmic tea break. ☕ You're as special and unique as the stars! 🔮"

    return {
        'sun': sun.sign,
        'moon': moon.sign,
        'ascendant': ascendant.sign,
        'planets': planets,
        'houses': house_data,
        'astrology_analysis': astrology_analysis
    }
