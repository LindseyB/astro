"""
Chart calculation business logic
"""
from collections.abc import Iterator, Mapping
from typing import Any, cast

from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
from chart_data import FullChartHouseInfo, FullChartPlanetInfo, PlanetsInHouse
from config import PLANET_CONSTANTS, HOUSE_NAMES, logger
from chart_data import create_charts, get_main_positions, get_planets_in_houses, get_current_planets
from formatters import format_planets_for_api, format_planets_in_houses_for_prompt
from personality import apply_personality_to_system_prompt, normalize_personality
from prompt_templates import load_prompt_template, load_prompt_text
from ai_service import stream_ai_api


def _prompt_temperature(metadata: Mapping[str, object]) -> float:
    value = metadata.get("temperature", 1.0)
    if isinstance(value, bool):
        return 1.0
    return float(value) if isinstance(value, (int, float)) else 1.0


def _format_planets_in_houses(planets_in_houses: dict[int, PlanetsInHouse]) -> str:
    return format_planets_in_houses_for_prompt(planets_in_houses, HOUSE_NAMES)


def _format_full_chart_planets(planets: dict[str, FullChartPlanetInfo]) -> str:
    return "\n".join(
        f"- {name}: {data['sign']} at {data['degree']:.2f}° in House {data['house'] or 'N/A'}"
        for name, data in planets.items()
    )


def _format_full_chart_houses(house_data: dict[int, FullChartHouseInfo]) -> str:
    house_lines = []

    for house_number in sorted(house_data.keys()):
        planet_text = ", ".join(
            f"{planet['name']} in {planet['sign']} ({planet['degree']:.2f}°)"
            for planet in house_data[house_number]['planets']
        )

        house_lines.append(
            f"- House {house_number} ({house_data[house_number]['sign']} "
            f"{house_data[house_number]['degree']:.2f}°): {planet_text}"
        )

    return "\n".join(house_lines)


def stream_calculate_chart(
    birth_date: str,
    birth_time: str,
    timezone_offset: str,
    latitude: str,
    longitude: str,
    music_genre: str = "any",
    personality: str = "default",
) -> Iterator[str]:
    """
    Calculate daily horoscope with current transits, yielding streaming chunks

    Args:
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset
        latitude (float): Latitude
        longitude (float): Longitude
        music_genre (str): Music genre preference (default "any")

    Yields:
        str: Text chunks from AI streaming response
    """
    # Setup charts
    chart, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)

    # Calculate main positions
    sun, moon, ascendant = get_main_positions(chart)

    # Get planets in houses
    planets_in_houses = get_planets_in_houses(chart)

    # Get current planet statuses
    current_planets = get_current_planets(today_chart)

    user_template = load_prompt_template("calculations/chart_user.md")
    user_prompt = user_template.render(
        sun_sign=sun.sign,
        moon_sign=moon.sign,
        ascendant_sign=ascendant.sign,
        planets_in_houses=_format_planets_in_houses(planets_in_houses),
        current_planets=format_planets_for_api(current_planets),
    )

    # Log the prompt to console
    logger.debug("=== USER PROMPT ===")
    logger.debug(user_prompt)
    logger.debug("=== END PROMPT ===")

    system_content = apply_personality_to_system_prompt(
        load_prompt_text("calculations/shared_astrologer_system.md"),
        normalize_personality(personality),
    )

    # Stream AI response
    try:
        for chunk in stream_ai_api(system_content, user_prompt, temperature=_prompt_temperature(user_template.metadata)):
            yield chunk
    except Exception as e:
        logger.error(f"Error streaming chart calculation: {e}")
        yield f"**Cosmic Note:** The AI astrologer is taking a cosmic tea break. ☕ Trust your intuition today! 🔮"


def stream_calculate_live_mas(
    birth_date: str,
    birth_time: str,
    timezone_offset: str,
    latitude: str,
    longitude: str,
    personality: str = "default",
) -> Iterator[str]:
    """
    Calculate Taco Bell order based on astrological data, yielding streaming chunks

    Args:
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset
        latitude (float): Latitude
        longitude (float): Longitude

    Yields:
        str: Text chunks from AI streaming response
    """
    # Setup charts
    chart, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)

    # Calculate main positions
    sun, moon, ascendant = get_main_positions(chart)

    # Get planets in houses
    planets_in_houses = get_planets_in_houses(chart)

    # Get current planet statuses
    current_planets = get_current_planets(today_chart)

    user_template = load_prompt_template("calculations/live_mas_user.md")
    user_prompt = user_template.render(
        sun_sign=sun.sign,
        moon_sign=moon.sign,
        ascendant_sign=ascendant.sign,
        planets_in_houses=_format_planets_in_houses(planets_in_houses),
        current_planets=format_planets_for_api(current_planets),
    )

    system_content = apply_personality_to_system_prompt(
        load_prompt_text("calculations/live_mas_system.md"),
        normalize_personality(personality),
    )

    # Stream AI response
    try:
        for chunk in stream_ai_api(system_content, user_prompt, temperature=_prompt_temperature(user_template.metadata)):
            yield chunk
    except Exception as e:
        logger.error(f"Error streaming live mas calculation: {e}")
        yield "🌮 **Cosmic Note:** The cosmic Taco Bell oracle is taking a nacho break! ☕ Try a Crunchwrap Supreme - it's universally delicious! 🔔✨"


def stream_calculate_full_chart(
    birth_date: str,
    birth_time: str,
    timezone_offset: str,
    latitude: str,
    longitude: str,
    music_genre: str = "any",
    personality: str = "default",
) -> Iterator[str]:
    """
    Calculate comprehensive natal chart data, yielding streaming chunks

    Args:
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset
        latitude (float): Latitude
        longitude (float): Longitude
        music_genre (str): Music genre preference (default "any")

    Yields:
        str: Text chunks from AI streaming response
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
    planets: dict[str, FullChartPlanetInfo] = {}

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
    house_data: dict[int, FullChartHouseInfo] = {}

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

    user_template = load_prompt_template("calculations/full_chart_user.md")
    user_prompt = user_template.render(
        sun_sign=sun.sign,
        moon_sign=moon.sign,
        ascendant_sign=ascendant.sign,
        planets=_format_full_chart_planets(planets),
        houses=_format_full_chart_houses(house_data),
    )

    system_content = apply_personality_to_system_prompt(
        load_prompt_text("calculations/shared_astrologer_system.md"),
        normalize_personality(personality),
    )

    # Stream AI response
    try:
        for chunk in stream_ai_api(system_content, user_prompt, temperature=_prompt_temperature(user_template.metadata)):
            yield chunk
    except Exception as e:
        logger.error(f"Error streaming full chart calculation: {e}")
        yield f"**Cosmic Note:** The AI astrologer is taking a cosmic tea break. ☕ You're as special and unique as the stars! 🔮"


def stream_calculate_ask_anything(
    question: str,
    birth_date: str,
    birth_time: str,
    timezone_offset: str,
    latitude: str,
    longitude: str,
    personality: str = "default",
) -> Iterator[str]:
    """
    Stream a general purpose answer for free-form questions with astrological context.

    Args:
        question (str): User's free-form question
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset
        latitude (str): Latitude in flatlib format (e.g., 40n42)
        longitude (str): Longitude in flatlib format (e.g., 74w00)

    Yields:
        str: Text chunks from AI streaming response
    """
    chart, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)
    sun, moon, ascendant = get_main_positions(chart)
    planets_in_houses = get_planets_in_houses(chart)
    current_planets = get_current_planets(today_chart)

    user_template = load_prompt_template("calculations/ask_anything_user.md")
    user_prompt = user_template.render(
        question=question,
        sun_sign=sun.sign,
        moon_sign=moon.sign,
        ascendant_sign=ascendant.sign,
        planets_in_houses=_format_planets_in_houses(planets_in_houses),
        current_planets=format_planets_for_api(current_planets),
    )

    system_content = apply_personality_to_system_prompt(
        load_prompt_text("calculations/ask_anything_system.md"),
        normalize_personality(personality),
    )

    try:
        for chunk in stream_ai_api(system_content, user_prompt, temperature=_prompt_temperature(user_template.metadata)):
            yield chunk
    except Exception as e:
        logger.error(f"Error streaming ask-anything response: {e}")
        yield "**Cosmic Note:** The AI astrologer is taking a cosmic tea break. ☕ Trust your intuition today! 🔮"
