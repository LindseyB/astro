"""
Flask application and route handlers
"""

from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from config import logger, PLANET_CONSTANTS, HOUSE_NAMES
from formatters import markdown_filter, prepare_music_genre_text, format_planets_for_api
from calculations import calculate_chart, calculate_full_chart, calculate_live_mas
from launchdarkly_service import should_show_chart_wheel
from chart_data import create_charts, get_main_positions, get_planets_in_houses, get_current_planets
from ai_service import stream_ai_api, verify_song_exists
import json

app = Flask(__name__)

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


@app.route('/')
def index():
    """Render home page"""
    return render_template('index.html')


@app.route('/chart', methods=['POST'])
def chart():
    """Handle daily horoscope request"""
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
        logger.info(f"Calculating chart for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        # Calculate chart
        chart_data = calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre)
        return render_template('chart.html', chart_data=chart_data, form_data=request.form)
    except Exception as e:
        logger.error(f"ERROR in /chart route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your chart. Please check your birth information and try again.")


@app.route('/full-chart', methods=['POST'])
def full_chart():
    """Handle full natal chart request"""
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
    
    # Get user IP and check feature flag
    user_ip = get_user_ip()
    show_chart_wheel = should_show_chart_wheel(user_ip)

    try:
        logger.info(f"Calculating full chart for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        logger.info(f"Chart wheel display flag for IP {user_ip}: {show_chart_wheel}")
        
        # Calculate full chart
        full_chart_data = calculate_full_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre)
        return render_template('full_chart.html', chart_data=full_chart_data, show_chart_wheel=show_chart_wheel, form_data=request.form)
    except Exception as e:
        logger.error(f"ERROR in /full-chart route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your full chart. Please check your birth information and try again.")


@app.route('/live-mas', methods=['POST'])
def live_mas():
    """Handle Taco Bell order request"""
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')

    try:
        logger.info(f"Calculating Live Más order for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        # Calculate Live Más order
        live_mas_data = calculate_live_mas(birth_date, birth_time, timezone_offset, latitude, longitude)
        return render_template('live_mas.html', chart_data=live_mas_data, form_data=request.form)
    except Exception as e:
        logger.error(f"ERROR in /live-mas route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your Taco Bell order. Please check your birth information and try again.")


@app.route('/music-suggestion', methods=['POST'])
def music_suggestion():
    """Handle async music suggestion request with streaming and verification"""
    try:
        data = request.get_json()
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

        # Build the user prompt
        user_prompt = (
            f"Based on this astrological chart, recommend ONE perfect song of the following genre: {song_request}. "
            f"Provide *ONLY* the song title and artist in this exact format:\n"
            f"Song: [Title] by [Artist]\n\n"
            f"Provide no additional explanation or text, just the song information.\n\n"
            f"Make sure it's a REAL song that actually exists. Double-check your recommendation.\n\n"
            f"Chart Data:\n"
            f"Sun: {sun.sign}, Moon: {moon.sign}, Ascendant: {ascendant.sign}\n\n"
            "Planets in Houses:\n" +
            "\n".join([f"{HOUSE_NAMES[house_number]}: " + ", ".join([f"{p['name']} in {p['sign']}" for p in data['planets']]) 
                      for house_number, data in planets_in_houses.items()]) + "\n\n"
        )

        if chart_type == 'daily':
            user_prompt += "Current Planets status:\n" + format_planets_for_api(current_planets)

        system_content = "You are a music expert and astrologer. You recommend REAL songs that exist. Be precise with song titles and artists."

        logger.debug("=== MUSIC SUGGESTION PROMPT ===")
        logger.debug(user_prompt)
        logger.debug("=== END PROMPT ===")

        def generate():
            """Generator function for streaming response with verification"""
            full_response = ""
            
            # Stream the initial suggestion
            for chunk in stream_ai_api(system_content, user_prompt, temperature=0.8):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # Now verify the song exists
            logger.info(f"Verifying song: {full_response}")
            yield f"data: {json.dumps({'type': 'verifying', 'content': 'Verifying song exists...'})}\n\n"
            
            verification = verify_song_exists(full_response)
            
            if verification['is_real']:
                yield f"data: {json.dumps({'type': 'verified', 'content': full_response, 'verified': True})}\n\n"
            else:
                # Song is likely hallucinated, ask for a more well-known alternative
                logger.warning(f"Song verification failed: {verification['explanation']}")
                yield f"data: {json.dumps({'type': 'retry', 'content': 'Original suggestion could not be verified. Getting alternative...'})}\n\n"
                
                retry_prompt = (
                    f"{user_prompt}\n\n"
                    f"IMPORTANT: The previous suggestion couldn't be verified. Please recommend a VERY WELL-KNOWN, "
                    f"POPULAR song that definitely exists. Choose a classic or mainstream hit."
                )
                
                retry_response = ""
                for chunk in stream_ai_api(system_content, retry_prompt, temperature=0.5):
                    if chunk:
                        retry_response += chunk
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # Verify retry
                retry_verification = verify_song_exists(retry_response)
                yield f"data: {json.dumps({'type': 'verified', 'content': retry_response, 'verified': retry_verification['is_real'], 'note': 'Alternative suggestion' if not retry_verification['is_real'] else None})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        logger.error(f"ERROR in /music-suggestion route: {type(e).__name__}: {str(e)}")
        return jsonify({'error': 'Failed to generate music suggestion'}), 500
