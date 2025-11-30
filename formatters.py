"""
Formatting utilities for astrology data
"""
import markdown as md


def markdown_filter(text):
    """Convert markdown text to HTML"""
    if not text:
        return ""
    return md.markdown(text, extensions=['nl2br'])


def prepare_music_genre_text(music_genre, chart_type="daily"):
    """
    Prepare music genre preference text for AI prompts

    Args:
        music_genre (str): The music genre preference
        chart_type (str): Either "daily" for daily horoscope or "natal" for full chart

    Returns:
        str: Formatted genre preference text for AI prompt
    """
    if not music_genre or music_genre.lower() == "any":
        return ""

    if music_genre.lower() == "other":
        if chart_type == "natal":
            return "(Please suggest a song from any genre that fits the chart)"
        else:
            return "(Please suggest songs from any genre that fits the vibe)"
    else:
        return f"(Please prioritize {music_genre} genre if possible)"


def format_planets_for_api(current_planets):
    """
    Format planet positions for AI API consumption

    Args:
        current_planets (dict): Dictionary of planet data with sign, degree, and retrograde status

    Returns:
        str: Formatted string describing current planetary positions
    """
    planet_strings = []
    retrograde_planets = []

    for planet_name, planet_data in current_planets.items():
        # Format basic position
        position_str = f"{planet_name} in {planet_data['sign']} at {planet_data['degree']:.2f} degrees"

        # Add retrograde status
        if planet_data['retrograde']:
            position_str += " (RETROGRADE)"
            retrograde_planets.append(planet_name)
        else:
            position_str += " (direct)"

        planet_strings.append(position_str)

    # Create the complete string
    result = "CURRENT PLANETARY POSITIONS:\n"
    result += "\n".join(planet_strings)

    if retrograde_planets:
        result += f"\n\nRETROGRADE PLANETS: {', '.join(retrograde_planets)}"
    else:
        result += "\n\nNo planets are currently retrograde."

    return result
