"""
Configuration and constants for the astrology application
"""
import logging
import os


def is_development_mode():
    """Return True when Flask is running in development/debug mode."""
    flask_env = os.environ.get('FLASK_ENV', '').strip().lower()
    flask_debug = os.environ.get('FLASK_DEBUG', '').strip()
    return flask_env == 'development' or flask_debug == '1'


IS_DEVELOPMENT = is_development_mode()

from flatlib import const

# Configure logging
# Logging configuration is handled in main.py
logger = logging.getLogger(__name__)


def get_secret_key():
    """Return configured Flask secret key or fail fast with a clear error."""
    secret_key = os.environ.get('SECRET_KEY', '').strip()
    if not secret_key:
        raise RuntimeError('SECRET_KEY environment variable is required at startup.')
    return secret_key

# Filter for planets only (exclude house cusps, angles, etc.)
PLANET_NAMES = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron']

# Planet constants mapping
PLANET_CONSTANTS = {
    'Sun': const.SUN,
    'Moon': const.MOON,
    'Mercury': const.MERCURY,
    'Venus': const.VENUS,
    'Mars': const.MARS,
    'Jupiter': const.JUPITER,
    'Saturn': const.SATURN,
    'Uranus': const.URANUS,
    'Neptune': const.NEPTUNE,
    'Pluto': const.PLUTO,
    'Chiron': const.CHIRON
}

# House names mapping
HOUSE_NAMES = {
    1: "1st House (Self/Identity) 🪞",
    2: "2nd House (Money/Values) 💰",
    3: "3rd House (Communication) 💬",
    4: "4th House (Home/Family) 🏡",
    5: "5th House (Creativity/Romance) 🎨",
    6: "6th House (Health/Work) 🧑‍💼",
    7: "7th House (Partnerships) 🤝",
    8: "8th House (Transformation) 🔄",
    9: "9th House (Philosophy/Travel) 🌍",
    10: "10th House (Career/Reputation) 🏆",
    11: "11th House (Friends/Hopes) 👥",
    12: "12th House (Spirituality/Subconscious) 🔮"
}