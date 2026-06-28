"""Flask application bootstrap and blueprint registration."""

import os
from collections.abc import Mapping

from flask import Flask, request


from ask_routes import ask_bp
from chart_routes import chart_bp
from config import IS_DEVELOPMENT, get_secret_key, logger
from formatters import markdown_filter
from music_routes import music_bp


app = Flask(__name__)
app.config['SECRET_KEY'] = get_secret_key()

SITE_META = {
    'site_name': 'Astro Horoscope',
    'default_title': 'Astro Horoscope',
    'default_social_title': 'Astro Horoscope - Your Cosmic Vibe Check',
    'og_description': "Your cosmic vibe check starts here. See your sun, moon, rising, and today's astrology in one beautiful experience.",
    'twitter_description': 'Cosmic vibe check: sun, moon, rising, and your daily astrology snapshot.',
    'meta_description': 'Get a fun, personalized astrology experience with your birth chart, daily horoscope, and chart-based insights.',
    'keywords': 'astrology app, cosmic vibe check, birth chart, horoscope, zodiac signs, sun moon rising, natal astrology, daily astrology',
    'twitter_image_alt': 'Astro Horoscope - Personalized astrological charts with cosmic animations',
    'author': 'Astro Horoscope',
}


@app.context_processor
def inject_site_meta() -> Mapping[str, dict[str, str]]:
    """Expose shared site copy to all templates to avoid repeated strings."""
    return {'site_meta': SITE_META}


# In development, disable static file caching so CSS/JS edits show on reload.
if IS_DEVELOPMENT:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.template_filter('markdown')(markdown_filter)


app.register_blueprint(chart_bp)
app.register_blueprint(music_bp)
app.register_blueprint(ask_bp)


def get_user_ip() -> str:
    """Get the user's IP address for feature flag evaluation."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr or '127.0.0.1'


__all__ = [
    'app',
    'get_user_ip',
    'logger',
]
