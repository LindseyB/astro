"""
Flask application and route handlers
"""

from flask import Flask, render_template, request, Response, stream_with_context, jsonify, flash
from config import logger, HOUSE_NAMES
from formatters import markdown_filter, prepare_music_genre_text, format_planets_for_api, format_planets_in_houses_for_prompt
from calculations import stream_calculate_chart, stream_calculate_full_chart, stream_calculate_live_mas, stream_calculate_ask_anything
from chart_data import create_charts, get_main_positions, get_planets_in_houses, get_current_planets, get_full_chart_structure
from ai_service import stream_ai_api
from lastfm_service import get_top_tracks_by_genre, format_tracks_for_prompt, LASTFM_API_KEY
from prompt_templates import load_prompt_template, load_prompt_text
import json
import re
import os
from datetime import datetime, timedelta

app = Flask(__name__)
secret_key = os.environ.get('SECRET_KEY', '').strip()
if not secret_key:
    raise RuntimeError('SECRET_KEY environment variable is required at startup.')
app.config['SECRET_KEY'] = secret_key

SITE_META = {
    'site_name': 'Astro Horoscope',
    'default_title': 'Astro Horoscope',
    'default_social_title': 'Astro Horoscope - Your Cosmic Vibe Check',
    'og_description': 'Your cosmic vibe check starts here. See your sun, moon, rising, and today\'s astrology in one beautiful experience.',
    'twitter_description': 'Cosmic vibe check: sun, moon, rising, and your daily astrology snapshot.',
    'meta_description': 'Get a fun, personalized astrology experience with your birth chart, daily horoscope, and chart-based insights.',
    'keywords': 'astrology app, cosmic vibe check, birth chart, horoscope, zodiac signs, sun moon rising, natal astrology, daily astrology',
    'twitter_image_alt': 'Astro Horoscope - Personalized astrological charts with cosmic animations',
    'author': 'Astro Horoscope'
}


@app.context_processor
def inject_site_meta():
    """Expose shared site copy to all templates to avoid repeated strings."""
    return {'site_meta': SITE_META}

# In development, disable static file caching so CSS/JS edits show on reload
if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Add markdown filter to convert markdown to HTML
app.template_filter('markdown')(markdown_filter)

def get_user_ip():
    """Get the user's IP address for feature flag evaluation"""
    # Check for X-Forwarded-For header (load balancer/proxy)
    if request.headers.get('X-Forwarded-For'):
        # Get the first IP in case of multiple proxies
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    # Check for X-Real-IP header (nginx)
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    # Fallback to remote_addr
    else:
        return request.remote_addr or '127.0.0.1'


def _decimal_to_astro_coord(value, is_latitude):
    """Convert decimal coordinates to flatlib astro format (e.g., 40n42, 74w00)."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return value

    direction = 'n' if is_latitude else 'e'
    if numeric < 0:
        direction = 's' if is_latitude else 'w'

    absolute = abs(numeric)
    degrees = int(absolute)
    minutes = int(round((absolute - degrees) * 60))
    if minutes == 60:
        degrees += 1
        minutes = 0

    return f"{degrees}{direction}{minutes:02d}"


def _normalize_birth_inputs(birth_date, timezone_offset, latitude, longitude):
    """Normalize legacy input formats used by older saved form data."""
    if isinstance(birth_date, str):
        birth_date = birth_date.strip()
        if '/' in birth_date:
            birth_date = birth_date.replace('/', '-')

    if isinstance(timezone_offset, str):
        timezone_offset = timezone_offset.strip()
        tz_match = re.fullmatch(r'([+-]?)(\d{1,2})', timezone_offset)
        if tz_match:
            sign, hours = tz_match.groups()
            hour_num = int(hours)
            if sign == '':
                sign = '-' if timezone_offset.startswith('-') else '+'
            timezone_offset = f"{sign}{hour_num:02d}:00"

    if isinstance(latitude, str):
        latitude = latitude.strip().lower()
    if isinstance(longitude, str):
        longitude = longitude.strip().lower()

    lat_pattern = r'^\d+[ns]\d{1,2}$'
    lon_pattern = r'^\d+[we]\d{1,2}$'

    if isinstance(latitude, str) and latitude and not re.fullmatch(lat_pattern, latitude):
        latitude = _decimal_to_astro_coord(latitude, is_latitude=True)
    if isinstance(longitude, str) and longitude and not re.fullmatch(lon_pattern, longitude):
        longitude = _decimal_to_astro_coord(longitude, is_latitude=False)

    return birth_date, timezone_offset, latitude, longitude


def _parse_timezone_offset_minutes(timezone_offset):
    """Parse timezone offsets like -5, +05:00, or +0530 into minutes."""
    if not isinstance(timezone_offset, str):
        return 0

    tz = timezone_offset.strip()
    match = re.fullmatch(r'([+-]?)(\d{1,2})(?::?(\d{2}))?', tz)
    if not match:
        return 0

    sign_token, hours_text, minutes_text = match.groups()
    sign = -1 if sign_token == '-' else 1
    hours = int(hours_text)
    minutes = int(minutes_text or '0')
    return sign * (hours * 60 + minutes)


def _get_user_local_today(timezone_offset):
    """Return today's date using the provided timezone offset."""
    offset_minutes = _parse_timezone_offset_minutes(timezone_offset)
    return (datetime.utcnow() + timedelta(minutes=offset_minutes)).date()


def _is_birthday_today(birth_date_html, timezone_offset):
    """True if the user's birthday (month/day) matches their local date."""
    try:
        birthday = datetime.strptime(birth_date_html, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return False

    local_today = _get_user_local_today(timezone_offset)
    return (birthday.month, birthday.day) == (local_today.month, local_today.day)


@app.route('/')
def index():
    """Render home page"""
    return render_template('index.html')


@app.route('/chart', methods=['POST'])
def chart():
    """Handle daily horoscope request - renders placeholder page immediately"""
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    music_genre = request.form.get('music_genre', 'any')

    # Handle "other" genre option
    if music_genre == 'other':
        other_genre = request.form.get('other_genre', '').strip()
        if other_genre:
            music_genre = other_genre
        else:
            music_genre = 'any'

    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')

    try:
        logger.info(f"Rendering chart placeholder for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        
        # Calculate basic chart data (fast - no AI)
        from chart_data import create_charts, get_main_positions, get_current_planets
        chart_obj, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)
        sun, moon, ascendant = get_main_positions(chart_obj)
        current_planets = get_current_planets(today_chart)
        
        # Build minimal chart_data for placeholder page
        chart_data = {
            'sun': sun.sign,
            'moon': moon.sign,
            'ascendant': ascendant.sign,
            'mercury_retrograde': current_planets.get('Mercury', {}).get('retrograde', False),
            'astrology_analysis': ''  # Will be loaded via streaming
        }
        
        # Prepare form data for template (keep HTML date format for JavaScript)
        form_data = {
            'birth_date': birth_date_html,
            'birth_time': birth_time,
            'timezone_offset': timezone_offset,
            'latitude': latitude,
            'longitude': longitude,
            'music_genre': music_genre,
            'other_genre': request.form.get('other_genre', '')
        }
        
        is_birthday = _is_birthday_today(birth_date_html, timezone_offset)
        if is_birthday:
            flash('Happy Birthday!', 'success')

        return render_template(
            'chart.html',
            chart_data=chart_data,
            form_data=form_data,
            streaming=True,
            is_birthday=is_birthday
        )
    except Exception as e:
        logger.error(f"ERROR in /chart route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your chart. Please check your birth information and try again.")


@app.route('/stream-chart-analysis', methods=['POST'])
def stream_chart_analysis():
    """Stream daily horoscope analysis"""
    try:
        # Validate API token early, before starting stream
        from ai_service import get_client
        try:
            get_client()
        except ValueError as e:
            logger.error(f"AI service not available: {e}")
            return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503
        
        data = request.get_json()
        
        # Validate required fields (check for None or empty string, but allow 0/0.0)
        required_fields = ['birth_date', 'birth_time', 'timezone_offset', 'latitude', 'longitude']
        missing_fields = [field for field in required_fields if field not in data or data.get(field) is None or data.get(field) == '']
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        timezone_offset = data.get('timezone_offset')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        music_genre = data.get('music_genre', 'any')
        
        # Convert date format if needed
        if birth_date and '-' in birth_date:
            birth_date = birth_date.replace('-', '/')
        
        logger.info(f"Streaming chart analysis for: {birth_date} {birth_time}")
        
        def generate():
            try:
                for chunk in stream_calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Error in stream_chart_analysis: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error(f"ERROR in /stream-chart-analysis route: {type(e).__name__}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/full-chart', methods=['POST'])
def full_chart():
    """Handle full natal chart request - renders placeholder page immediately"""
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    music_genre = request.form.get('music_genre', 'any')

    # Handle "other" genre option
    if music_genre == 'other':
        other_genre = request.form.get('other_genre', '').strip()
        if other_genre:
            music_genre = other_genre
        else:
            music_genre = 'any'

    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')

    try:
        logger.info(f"Rendering full chart placeholder for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        
        # Calculate chart structure (fast - no AI)
        full_chart_data = get_full_chart_structure(birth_date, birth_time, timezone_offset, latitude, longitude)
        full_chart_data['astrology_analysis'] = ''  # Will be loaded via streaming
        
        # Prepare form data for template (keep HTML date format for JavaScript)
        form_data = {
            'birth_date': birth_date_html,
            'birth_time': birth_time,
            'timezone_offset': timezone_offset,
            'latitude': latitude,
            'longitude': longitude,
            'music_genre': music_genre,
            'other_genre': request.form.get('other_genre', '')
        }
        
        return render_template('full_chart.html', chart_data=full_chart_data, form_data=form_data, streaming=True)
    except Exception as e:
        logger.error(f"ERROR in /full-chart route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your full chart. Please check your birth information and try again.")


@app.route('/stream-full-chart-analysis', methods=['POST'])
def stream_full_chart_analysis():
    """Stream full natal chart analysis"""
    try:
        # Validate API token early, before starting stream
        from ai_service import get_client
        try:
            get_client()
        except ValueError as e:
            logger.error(f"AI service not available: {e}")
            return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503
        
        data = request.get_json()
        
        # Validate required fields (check for None or empty string, but allow 0/0.0)
        required_fields = ['birth_date', 'birth_time', 'timezone_offset', 'latitude', 'longitude']
        missing_fields = [field for field in required_fields if field not in data or data.get(field) is None or data.get(field) == '']
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        timezone_offset = data.get('timezone_offset')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        music_genre = data.get('music_genre', 'any')
        
        if birth_date and '-' in birth_date:
            birth_date = birth_date.replace('-', '/')
        
        logger.info(f"Streaming full chart analysis for: {birth_date} {birth_time}")
        
        def generate():
            try:
                for chunk in stream_calculate_full_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Error in stream_full_chart_analysis: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error(f"ERROR in /stream-full-chart-analysis route: {type(e).__name__}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/live-mas', methods=['POST'])
def live_mas():
    """Handle Taco Bell order request - renders placeholder page immediately"""
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')

    try:
        logger.info(f"Rendering Live Más placeholder for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        
        # Calculate basic chart data (fast - no AI)
        from chart_data import create_charts, get_main_positions, get_current_planets
        chart_obj, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)
        sun, moon, ascendant = get_main_positions(chart_obj)
        current_planets = get_current_planets(today_chart)
        
        live_mas_data = {
            'sun': sun.sign,
            'moon': moon.sign,
            'ascendant': ascendant.sign,
            'mercury_retrograde': current_planets.get('Mercury', {}).get('retrograde', False),
            'taco_bell_order': ''  # Will be loaded via streaming
        }
        
        # Prepare form data for template (keep HTML date format for JavaScript)
        form_data = {
            'birth_date': birth_date_html,
            'birth_time': birth_time,
            'timezone_offset': timezone_offset,
            'latitude': latitude,
            'longitude': longitude,
            'music_genre': 'any',  # live_mas doesn't use music genre
            'other_genre': ''
        }
        
        return render_template('live_mas.html', chart_data=live_mas_data, form_data=form_data, streaming=True)
    except Exception as e:
        logger.error(f"ERROR in /live-mas route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your Taco Bell order. Please check your birth information and try again.")


@app.route('/ask-anything', methods=['POST'])
def ask_anything():
    """Render Ask Anything placeholder page immediately"""
    question = request.form.get('question_prompt', '').strip()
    birth_date_html = request.form.get('birth_date', '').strip()
    birth_time = request.form.get('birth_time', '').strip()
    timezone_offset = request.form.get('timezone_offset', '').strip()
    latitude = request.form.get('latitude', '').strip()
    longitude = request.form.get('longitude', '').strip()

    birth_date_html, timezone_offset, latitude, longitude = _normalize_birth_inputs(
        birth_date_html, timezone_offset, latitude, longitude
    )

    if not question:
        return render_template('error.html', error="Please enter a question before using Ask Anything mode."), 400

    required_fields = {
        'birth_date': birth_date_html,
        'birth_time': birth_time,
        'timezone_offset': timezone_offset,
        'latitude': latitude,
        'longitude': longitude,
    }
    missing_fields = [name for name, value in required_fields.items() if not value]
    if missing_fields:
        return render_template('error.html', error="Please complete your birth details before using Ask Anything mode."), 400

    form_data = {
        'birth_date': birth_date_html,
        'birth_time': birth_time,
        'timezone_offset': timezone_offset,
        'latitude': latitude,
        'longitude': longitude,
    }

    return render_template('ask_anything.html', question=question, form_data=form_data, streaming=True)


@app.route('/stream-live-mas-analysis', methods=['POST'])
def stream_live_mas_analysis():
    """Stream Taco Bell order analysis"""
    try:
        # Validate API token early, before starting stream
        from ai_service import get_client
        try:
            get_client()
        except ValueError as e:
            logger.error(f"AI service not available: {e}")
            return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503
        
        data = request.get_json()
        
        # Validate required fields (check for None or empty string, but allow 0/0.0)
        required_fields = ['birth_date', 'birth_time', 'timezone_offset', 'latitude', 'longitude']
        missing_fields = [field for field in required_fields if field not in data or data.get(field) is None or data.get(field) == '']
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        timezone_offset = data.get('timezone_offset')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if birth_date and '-' in birth_date:
            birth_date = birth_date.replace('-', '/')
        
        logger.info(f"Streaming live mas analysis for: {birth_date} {birth_time}")
        
        def generate():
            try:
                for chunk in stream_calculate_live_mas(birth_date, birth_time, timezone_offset, latitude, longitude):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Error in stream_live_mas_analysis: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error(f"ERROR in /stream-live-mas-analysis route: {type(e).__name__}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/stream-ask-anything', methods=['POST'])
def stream_ask_anything():
    """Stream free-form Ask Anything responses"""
    try:
        data = request.get_json() or {}
        question = (data.get('question') or '').strip()

        def _norm(v):
            return v.strip() if isinstance(v, str) else v

        birth_date = _norm(data.get('birth_date'))
        birth_time = _norm(data.get('birth_time'))
        timezone_offset = _norm(data.get('timezone_offset'))
        latitude = _norm(data.get('latitude'))
        longitude = _norm(data.get('longitude'))

        birth_date, timezone_offset, latitude, longitude = _normalize_birth_inputs(
            birth_date, timezone_offset, latitude, longitude
        )

        if not question:
            return jsonify({'error': 'Missing required field: question'}), 400

        required_fields = {
            'birth_date': birth_date,
            'birth_time': birth_time,
            'timezone_offset': timezone_offset,
            'latitude': latitude,
            'longitude': longitude,
        }
        missing_fields = [
            name for name, value in required_fields.items()
            if value is None or (isinstance(value, str) and value == '')
        ]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        if birth_date and '-' in birth_date:
            birth_date = birth_date.replace('-', '/')
        from ai_service import get_client
        try:
            get_client()
        except ValueError as e:
            logger.error(f"AI service not available: {e}")
            return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503

        logger.info("Streaming ask-anything response")

        def generate():
            try:
                for chunk in stream_calculate_ask_anything(question, birth_date, birth_time, timezone_offset, latitude, longitude):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Error in stream_ask_anything: {e}")
                yield f"data: {json.dumps({'error': 'Failed to stream response'})}\n\n"
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error(f"ERROR in /stream-ask-anything route: {type(e).__name__}: {str(e)}")
        return jsonify({'error': 'Failed to stream response'}), 500


@app.route('/music-suggestion', methods=['POST'])
def music_suggestion():
    """Handle async music suggestion request with streaming"""
    try:
        # Validate API token early, before starting stream
        from ai_service import get_client
        try:
            get_client()
        except ValueError as e:
            logger.error(f"AI service not available: {e}")
            return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503
        
        data = request.get_json()
        
        # Validate required fields (check for None or empty string, but allow 0/0.0)
        required_fields = ['birth_date', 'birth_time', 'timezone_offset', 'latitude', 'longitude']
        missing_fields = [field for field in required_fields if field not in data or data.get(field) is None or data.get(field) == '']
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        timezone_offset = data.get('timezone_offset')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        music_genre = data.get('music_genre', 'any')
        chart_type = data.get('chart_type', 'daily')  # 'daily' or 'natal'
        
        # Handle edge case where 'other' slips through (should be handled in frontend)
        if music_genre == 'other':
            music_genre = 'any'

        logger.info(f"Generating music suggestion for chart type: {chart_type}, genre: {music_genre}")

        # Convert date format if needed
        if '-' in birth_date:
            birth_date = birth_date.replace('-', '/')

        # Setup charts
        chart, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)

        # Calculate main positions
        sun, moon, ascendant = get_main_positions(chart)

        # Get planets in houses
        planets_in_houses = get_planets_in_houses(chart)

        # Get current planet statuses (for daily horoscope)
        current_planets = get_current_planets(today_chart)

        # Prepare music genre preference text
        genre_text = prepare_music_genre_text(music_genre, chart_type)
        if genre_text:
            song_request = f" {genre_text}"
        else:
            song_request = " any genre"

        # Fetch a larger pool and let formatter pick a varied 30-track mix.
        lastfm_tracks = get_top_tracks_by_genre(music_genre, limit=50)
        tracks_context = format_tracks_for_prompt(lastfm_tracks, limit=30)

        normalized_genre = (music_genre or '').strip().lower() if isinstance(music_genre, str) else ''
        if not normalized_genre or normalized_genre == 'any':
            lastfm_status = 'skipped_any_genre'
        elif not LASTFM_API_KEY:
            lastfm_status = 'skipped_missing_api_key'
        elif lastfm_tracks:
            lastfm_status = 'ok_tracks_found'
        else:
            lastfm_status = 'ok_no_tracks_found'

        logger.info(
            "Last.fm lookup status: %s (genre=%s, tracks=%d)",
            lastfm_status,
            music_genre,
            len(lastfm_tracks),
        )
        
        tracks_block = ""
        if tracks_context:
            tracks_block = (
                f"{tracks_context}\n\n"
                "You may choose from these popular tracks or suggest other songs in the same genre that match the astrological vibe.\n\n"
            )

        current_planets_block = ""
        if chart_type == 'daily':
            current_planets_block = "Current Planets status:\n" + format_planets_for_api(current_planets)

        user_template = load_prompt_template("routes/music_suggestion_user.md")
        user_prompt = user_template.render(
            song_request=song_request,
            tracks_block=tracks_block,
            sun_sign=sun.sign,
            moon_sign=moon.sign,
            ascendant_sign=ascendant.sign,
            planets_in_houses=format_planets_in_houses_for_prompt(planets_in_houses, HOUSE_NAMES),
            current_planets_block=current_planets_block,
        )

        system_content = load_prompt_text("routes/music_suggestion_system.md")

        logger.debug("=== MUSIC SUGGESTION PROMPT ===")
        logger.debug(user_prompt)
        logger.debug("=== END PROMPT ===")

        def generate():
            """Generator function for streaming response"""
            try:
                for chunk in stream_ai_api(system_content, user_prompt, temperature=user_template.metadata.get("temperature", 1.0)):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Error streaming music suggestion: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        response = Response(stream_with_context(generate()), mimetype='text/event-stream')
        response.headers['X-Lastfm-Status'] = lastfm_status
        response.headers['X-Lastfm-Tracks-Count'] = str(len(lastfm_tracks))
        return response

    except Exception as e:
        logger.error(f"ERROR in /music-suggestion route: {type(e).__name__}: {str(e)}")
        return jsonify({'error': 'Failed to generate music suggestion'}), 500
