"""
Configuration and constants for the astrology application
"""
import logging

# Load environment variables from a .env file (if present) before anything
# else reads them (e.g. ai_service.py reading ANTHROPIC_TOKEN at import time).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional; env vars can still be set in the shell.
    pass

from flatlib import const

# Configure logging
# Logging configuration is handled in main.py
logger = logging.getLogger(__name__)

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