"""Music suggestion routes."""

import json

from flask import Blueprint, Response, jsonify, request, stream_with_context

import ai_service
from chart_data import create_charts, get_current_planets, get_main_positions, get_planets_in_houses
from config import HOUSE_NAMES, logger
from formatters import format_planets_for_api, format_planets_in_houses_for_prompt, prepare_music_genre_text
from lastfm_service import LASTFM_API_KEY, format_tracks_for_prompt, get_top_tracks_by_genre
from prompt_templates import load_prompt_template, load_prompt_text
from route_helpers import _require_ai_client
from validation import _format_birth_date_for_calculations, find_missing_fields


music_bp = Blueprint('music', __name__)


@music_bp.route('/music-suggestion', methods=['POST'])
def music_suggestion():
    """Handle async music suggestion request with streaming."""
    try:
        ai_client_error = _require_ai_client()
        if ai_client_error:
            return ai_client_error

        data = request.get_json()
        missing_fields = find_missing_fields(data, ['birth_date', 'birth_time', 'timezone_offset', 'latitude', 'longitude'])
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        timezone_offset = data.get('timezone_offset')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        music_genre = data.get('music_genre', 'any')
        chart_type = data.get('chart_type', 'daily')

        if music_genre == 'other':
            music_genre = 'any'

        logger.info("Generating music suggestion for chart type: %s, genre: %s", chart_type, music_genre)

        try:
            birth_date = _format_birth_date_for_calculations(birth_date)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        chart, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)
        sun, moon, ascendant = get_main_positions(chart)
        planets_in_houses = get_planets_in_houses(chart)
        current_planets = get_current_planets(today_chart)

        genre_text = prepare_music_genre_text(music_genre, chart_type)
        song_request = f" {genre_text}" if genre_text else " any genre"

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
                f"{tracks_context}\\n\\n"
                "You may choose from these popular tracks or suggest other songs in the same genre that match the astrological vibe.\\n\\n"
            )

        current_planets_block = ""
        if chart_type == 'daily':
            current_planets_block = "Current Planets status:\n" + format_planets_for_api(current_planets)

        user_template = load_prompt_template('routes/music_suggestion_user.md')
        user_prompt = user_template.render(
            song_request=song_request,
            tracks_block=tracks_block,
            sun_sign=sun.sign,
            moon_sign=moon.sign,
            ascendant_sign=ascendant.sign,
            planets_in_houses=format_planets_in_houses_for_prompt(planets_in_houses, HOUSE_NAMES),
            current_planets_block=current_planets_block,
        )

        system_content = load_prompt_text('routes/music_suggestion_system.md')

        logger.debug("=== MUSIC SUGGESTION PROMPT ===")
        logger.debug(user_prompt)
        logger.debug("=== END PROMPT ===")

        def generate():
            try:
                for chunk in ai_service.stream_ai_api(
                    system_content,
                    user_prompt,
                    temperature=user_template.metadata.get('temperature', 1.0),
                ):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error("Error streaming music suggestion: %s", e)
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        response = Response(stream_with_context(generate()), mimetype='text/event-stream')
        response.headers['X-Lastfm-Status'] = lastfm_status
        response.headers['X-Lastfm-Tracks-Count'] = str(len(lastfm_tracks))
        return response

    except Exception as e:
        logger.error("ERROR in /music-suggestion route: %s: %s", type(e).__name__, str(e))
        return jsonify({'error': 'Failed to generate music suggestion'}), 500
