"""Ask Anything routes."""

import json

from flask import Blueprint, Response, jsonify, render_template, request, stream_with_context

import ai_service
from calculations import stream_calculate_ask_anything
from config import logger
from validation import _format_birth_date_for_calculations, _normalize_birth_inputs


ask_bp = Blueprint('ask', __name__)


@ask_bp.route('/ask-anything', methods=['POST'])
def ask_anything():
    """Render Ask Anything placeholder page immediately."""
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


@ask_bp.route('/stream-ask-anything', methods=['POST'])
def stream_ask_anything():
    """Stream free-form Ask Anything responses."""
    try:
        data = request.get_json() or {}
        question = (data.get('question') or '').strip()

        def _norm(value):
            return value.strip() if isinstance(value, str) else value

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
            name
            for name, value in required_fields.items()
            if value is None or (isinstance(value, str) and value == '')
        ]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        try:
            birth_date = _format_birth_date_for_calculations(birth_date)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        try:
            ai_service.get_client()
        except ValueError as e:
            logger.error("AI service not available: %s", e)
            return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503

        logger.info("Streaming ask-anything response")

        def generate():
            try:
                for chunk in stream_calculate_ask_anything(
                    question,
                    birth_date,
                    birth_time,
                    timezone_offset,
                    latitude,
                    longitude,
                ):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error("Error in stream_ask_anything: %s", e)
                yield f"data: {json.dumps({'error': 'Failed to stream response'})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error("ERROR in /stream-ask-anything route: %s: %s", type(e).__name__, str(e))
        return jsonify({'error': 'Failed to stream response'}), 500
