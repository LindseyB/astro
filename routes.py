"""
Flask application and route handlers
"""

from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from config import logger, HOUSE_NAMES
from formatters import markdown_filter, prepare_music_genre_text, format_planets_for_api
from calculations import stream_calculate_chart, stream_calculate_full_chart, stream_calculate_live_mas
from launchdarkly_service import should_show_chart_wheel
from chart_data import create_charts, get_main_positions, get_planets_in_houses, get_current_planets, get_full_chart_structure
from ai_service import stream_ai_api, verify_song_exists
from lastfm_service import get_top_tracks_by_genre, format_tracks_for_prompt
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
        
        return render_template('chart.html', chart_data=chart_data, form_data=form_data, streaming=True)
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
    
    # Get user IP and check feature flag
    user_ip = get_user_ip()
    show_chart_wheel = should_show_chart_wheel(user_ip)

    try:
        logger.info(f"Rendering full chart placeholder for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        logger.info(f"Chart wheel display flag for IP {user_ip}: {show_chart_wheel}")
        
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
        
        return render_template('full_chart.html', chart_data=full_chart_data, show_chart_wheel=show_chart_wheel, form_data=form_data, streaming=True)
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


@app.route('/music-suggestion', methods=['POST'])
def music_suggestion():
    """Handle async music suggestion request with streaming and verification"""
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

        # Get top tracks from Last.fm for the genre
        lastfm_tracks = get_top_tracks_by_genre(music_genre)
        tracks_context = format_tracks_for_prompt(lastfm_tracks)
        
        # Build the user prompt
        user_prompt = (
            f"Based on this astrological chart, recommend ONE perfect song of the following genre: {song_request}. "
            f"Try to provide *ONLY* the song title and artist in this exact format:\n"
            f"🎶 [Title] by [Artist]\n\n"
            f"If you're having a hard time providing a song recommend an artist instead in this format:\n\n"
            f"Artist: [Artist Name]\n\n"
            f"Provide a single sentence justification for your recommendation it should be concise short and to the point while maintaining a casual vibey tone.\n\n"
            f"Make sure it's a REAL song that actually exists. Double-check your recommendation. Most importantly it should match the genre it does not need to be well-known\n\n"
        )
        
        # Add Last.fm tracks as examples if available
        if tracks_context:
            user_prompt += f"{tracks_context}\n\nYou may choose from these popular tracks or suggest other songs in the same genre that match the astrological vibe.\n\n"
        
        user_prompt += (
            f"Chart Data:\n"
            f"Sun: {sun.sign}, Moon: {moon.sign}, Ascendant: {ascendant.sign}\n\n"
            "Planets in Houses:\n" +
            "\n".join([f"{HOUSE_NAMES[house_number]}: " + ", ".join([f"{p['name']} in {p['sign']}" for p in house_data['planets']]) 
                      for house_number, house_data in planets_in_houses.items()]) + "\n\n"
        )

        if chart_type == 'daily':
            user_prompt += "Current Planets status:\n" + format_planets_for_api(current_planets)

        system_content = "You are a music expert and astrologer. You are a cool astrologer who uses lots of emojis and is very casual. You are also VERY concise and to the point. You are an expert in astrology and can analyze charts quickly. Never use any mdashes in your responses those just aren't cool. You recommend REAL songs that exist. Be precise with song titles and artists. The songs should match the vibe of the astrological chart data provided."

        logger.debug("=== MUSIC SUGGESTION PROMPT ===")
        logger.debug(user_prompt)
        logger.debug("=== END PROMPT ===")

        def generate():
            """Generator function for streaming response with verification"""
            max_attempts = 3
            
            for attempt in range(max_attempts):
                full_response = ""
                
                # Build prompt based on attempt number
                if attempt == 0:
                    current_prompt = user_prompt
                    yield f"data: {json.dumps({'type': 'attempt', 'attempt': attempt + 1})}\n\n"
                else:
                    # For retries, emphasize that it must be a real song
                    current_prompt = (
                        f"{user_prompt}\n\n"
                        f"IMPORTANT: Previous suggestion(s) couldn't be verified as real songs. "
                        f"Please recommend a song that DEFINITELY EXISTS. Verify the song title and artist are correct."
                    )
                    yield f"data: {json.dumps({'type': 'retry', 'content': f'Attempt {attempt + 1}: Getting alternative suggestion...', 'attempt': attempt + 1})}\n\n"
                
                # Stream the suggestion
                for chunk in stream_ai_api(system_content, current_prompt, temperature=0.4):
                    if chunk is None:
                        logger.error(f"Attempt {attempt + 1}: Failed to generate music suggestion")
                        break
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # Check if we got any response
                if not full_response:
                    logger.warning(f"Attempt {attempt + 1}: No response received from AI")
                    continue
                
                # Verify the song exists
                logger.info(f"Attempt {attempt + 1}: Verifying song: {full_response}")
                yield f"data: {json.dumps({'type': 'verifying', 'content': 'Verifying song exists...'})}\n\n"
                
                verification = verify_song_exists(full_response)
                
                if verification['is_real']:
                    # Success! Return the verified song
                    yield f"data: {json.dumps({'type': 'verified', 'content': full_response, 'verified': True, 'attempt': attempt + 1})}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return
                else:
                    # Song verification failed
                    logger.warning(f"Attempt {attempt + 1}: Song verification failed: {verification['explanation']}")
                    
                    # If this was the last attempt, return empty string
                    if attempt == max_attempts - 1:
                        logger.error(f"All {max_attempts} attempts failed. Returning empty string.")
                        yield f"data: {json.dumps({'type': 'verified', 'content': '', 'verified': False, 'note': 'All attempts failed to find a verifiable song'})}\n\n"
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        return
            
            # Fallback (should not reach here, but just in case)
            yield f"data: {json.dumps({'type': 'verified', 'content': '', 'verified': False})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        logger.error(f"ERROR in /music-suggestion route: {type(e).__name__}: {str(e)}")
        return jsonify({'error': 'Failed to generate music suggestion'}), 500
