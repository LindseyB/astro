"""Flask application bootstrap and blueprint registration."""

from typing import Any

from flask import Flask, Response, render_template, request
from werkzeug.exceptions import HTTPException


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
def inject_site_meta() -> dict[str, Any]:
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
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()

    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip

    return request.remote_addr or '127.0.0.1'


@app.errorhandler(404)
def not_found(e):
    try:
        return render_template(
            'http_error.html',
            code=404,
            message=e.name,
            h1='🔭 Lost in Space',
            description="The stars have aligned... but not for this page. Mercury must be in retrograde, because whatever you were looking for has vanished into the cosmic void.",
        ), 404
    except Exception:
        return Response('404 Not Found', status=404, mimetype='text/plain')


@app.errorhandler(HTTPException)
def http_error(e):
    try:
        return render_template('http_error.html', code=e.code, message=e.name, description=e.description), e.code
    except Exception:
        return Response(f'{e.code} {e.name}', status=e.code, mimetype='text/plain')


@app.errorhandler(Exception)
def internal_error(e):
    try:
        return render_template('http_error.html', code=500, message='Internal Server Error'), 500
    except Exception:
        return Response('500 Internal Server Error', status=500, mimetype='text/plain')


__all__ = [
    'app',
    'get_user_ip',
    'logger',
]
