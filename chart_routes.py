"""Chart-related Flask routes and streaming endpoints."""

import json
from collections.abc import Iterator

from flask import Blueprint, Response, current_app, flash, jsonify, render_template, request, stream_with_context
from flask.typing import ResponseReturnValue

from calculations import stream_calculate_chart, stream_calculate_full_chart, stream_calculate_live_mas
from chart_data import create_charts, get_current_planets, get_full_chart_structure, get_main_positions
from config import logger
from route_helpers import _require_ai_client
from validation import _format_birth_date_for_calculations, _is_birthday_today, find_missing_fields


chart_bp = Blueprint('chart', __name__)


@chart_bp.route('/')
def index() -> ResponseReturnValue:
    """Render home page."""
    return render_template('index.html')


@chart_bp.route('/chart', methods=['POST'])
def chart() -> ResponseReturnValue:
    """Handle daily horoscope request and render placeholder page immediately."""
    birth_date_html = request.form['birth_date']
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    music_genre = request.form.get('music_genre', 'any')

    if music_genre == 'other':
        other_genre = request.form.get('other_genre', '').strip()
        music_genre = other_genre if other_genre else 'any'

    try:
        birth_date = _format_birth_date_for_calculations(birth_date_html)
        logger.info(
            "Rendering chart placeholder for: %s %s %s %s %s",
            birth_date,
            birth_time,
            timezone_offset,
            latitude,
            longitude,
        )

        chart_obj, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)
        sun, moon, ascendant = get_main_positions(chart_obj)
        current_planets = get_current_planets(today_chart)

        chart_data = {
            'sun': sun.sign,
            'moon': moon.sign,
            'ascendant': ascendant.sign,
            'mercury_retrograde': current_planets.get('Mercury', {}).get('retrograde', False),
            'astrology_analysis': '',
        }

        form_data = {
            'birth_date': birth_date_html,
            'birth_time': birth_time,
            'timezone_offset': timezone_offset,
            'latitude': latitude,
            'longitude': longitude,
            'music_genre': music_genre,
            'other_genre': request.form.get('other_genre', ''),
        }

        is_birthday = _is_birthday_today(birth_date_html, timezone_offset)
        if is_birthday:
            flash('Happy Birthday!', 'success')

        return render_template(
            'chart.html',
            chart_data=chart_data,
            form_data=form_data,
            streaming=True,
            is_birthday=is_birthday,
        )
    except Exception as e:
        logger.error("ERROR in /chart route: %s: %s", type(e).__name__, str(e))
        if current_app.debug:
            import traceback

            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        return render_template('error.html', error="Something went wrong while calculating your chart. Please check your birth information and try again.")


@chart_bp.route('/stream-chart-analysis', methods=['POST'])
def stream_chart_analysis() -> ResponseReturnValue:
    """Stream daily horoscope analysis."""
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

        try:
            birth_date = _format_birth_date_for_calculations(birth_date)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        logger.info("Streaming chart analysis for: %s %s", birth_date, birth_time)

        def generate() -> Iterator[str]:
            try:
                for chunk in stream_calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error("Error in stream_chart_analysis: %s", e)
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error("ERROR in /stream-chart-analysis route: %s: %s", type(e).__name__, str(e))
        return jsonify({'error': str(e)}), 500


@chart_bp.route('/full-chart', methods=['POST'])
def full_chart() -> ResponseReturnValue:
    """Handle full natal chart request and render placeholder page immediately."""
    birth_date_html = request.form['birth_date']
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    music_genre = request.form.get('music_genre', 'any')

    if music_genre == 'other':
        other_genre = request.form.get('other_genre', '').strip()
        music_genre = other_genre if other_genre else 'any'

    try:
        birth_date = _format_birth_date_for_calculations(birth_date_html)
        logger.info(
            "Rendering full chart placeholder for: %s %s %s %s %s",
            birth_date,
            birth_time,
            timezone_offset,
            latitude,
            longitude,
        )

        full_chart_data = get_full_chart_structure(birth_date, birth_time, timezone_offset, latitude, longitude)
        full_chart_data['astrology_analysis'] = ''

        form_data = {
            'birth_date': birth_date_html,
            'birth_time': birth_time,
            'timezone_offset': timezone_offset,
            'latitude': latitude,
            'longitude': longitude,
            'music_genre': music_genre,
            'other_genre': request.form.get('other_genre', ''),
        }

        return render_template('full_chart.html', chart_data=full_chart_data, form_data=form_data, streaming=True)
    except Exception as e:
        logger.error("ERROR in /full-chart route: %s: %s", type(e).__name__, str(e))
        if current_app.debug:
            import traceback

            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        return render_template('error.html', error="Something went wrong while calculating your full chart. Please check your birth information and try again.")


@chart_bp.route('/stream-full-chart-analysis', methods=['POST'])
def stream_full_chart_analysis() -> ResponseReturnValue:
    """Stream full natal chart analysis."""
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

        try:
            birth_date = _format_birth_date_for_calculations(birth_date)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        logger.info("Streaming full chart analysis for: %s %s", birth_date, birth_time)

        def generate() -> Iterator[str]:
            try:
                for chunk in stream_calculate_full_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error("Error in stream_full_chart_analysis: %s", e)
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error("ERROR in /stream-full-chart-analysis route: %s: %s", type(e).__name__, str(e))
        return jsonify({'error': str(e)}), 500


@chart_bp.route('/live-mas', methods=['POST'])
def live_mas() -> ResponseReturnValue:
    """Handle Taco Bell order request and render placeholder page immediately."""
    birth_date_html = request.form['birth_date']
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    try:
        birth_date = _format_birth_date_for_calculations(birth_date_html)
        logger.info(
            "Rendering Live Mas placeholder for: %s %s %s %s %s",
            birth_date,
            birth_time,
            timezone_offset,
            latitude,
            longitude,
        )

        chart_obj, today_chart = create_charts(birth_date, birth_time, timezone_offset, latitude, longitude)
        sun, moon, ascendant = get_main_positions(chart_obj)
        current_planets = get_current_planets(today_chart)

        live_mas_data = {
            'sun': sun.sign,
            'moon': moon.sign,
            'ascendant': ascendant.sign,
            'mercury_retrograde': current_planets.get('Mercury', {}).get('retrograde', False),
            'taco_bell_order': '',
        }

        form_data = {
            'birth_date': birth_date_html,
            'birth_time': birth_time,
            'timezone_offset': timezone_offset,
            'latitude': latitude,
            'longitude': longitude,
            'music_genre': 'any',
            'other_genre': '',
        }

        return render_template('live_mas.html', chart_data=live_mas_data, form_data=form_data, streaming=True)
    except Exception as e:
        logger.error("ERROR in /live-mas route: %s: %s", type(e).__name__, str(e))
        if current_app.debug:
            import traceback

            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        return render_template('error.html', error="Something went wrong while calculating your Taco Bell order. Please check your birth information and try again.")


@chart_bp.route('/stream-live-mas-analysis', methods=['POST'])
def stream_live_mas_analysis() -> ResponseReturnValue:
    """Stream Taco Bell order analysis."""
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

        try:
            birth_date = _format_birth_date_for_calculations(birth_date)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        logger.info("Streaming live mas analysis for: %s %s", birth_date, birth_time)

        def generate() -> Iterator[str]:
            try:
                for chunk in stream_calculate_live_mas(birth_date, birth_time, timezone_offset, latitude, longitude):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error("Error in stream_live_mas_analysis: %s", e)
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error("ERROR in /stream-live-mas-analysis route: %s: %s", type(e).__name__, str(e))
        return jsonify({'error': str(e)}), 500
