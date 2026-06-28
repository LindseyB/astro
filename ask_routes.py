"""Ask Anything routes."""

import json
from collections.abc import Iterator
from typing import Any

from flask import Blueprint, Response, jsonify, render_template, request, stream_with_context
from flask.typing import ResponseReturnValue

from calculations import stream_calculate_ask_anything
from config import logger
from personality import DEFAULT_PERSONALITY, normalize_personality
from route_helpers import _require_ai_client
from validation import _format_birth_date_for_calculations, _normalize_birth_inputs


ask_bp = Blueprint('ask', __name__)


@ask_bp.route('/ask-anything', methods=['POST'])
def ask_anything() -> ResponseReturnValue:
    """Render Ask Anything placeholder page immediately."""
    question = request.form.get('question_prompt', '').strip()
    birth_date_html = request.form.get('birth_date', '').strip()
    birth_time = request.form.get('birth_time', '').strip()
    timezone_offset = request.form.get('timezone_offset', '').strip()
    latitude = request.form.get('latitude', '').strip()
    longitude = request.form.get('longitude', '').strip()
    personality = normalize_personality(request.form.get('personality', DEFAULT_PERSONALITY))

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
        'personality': personality,
    }
    return render_template('ask_anything.html', question=question, form_data=form_data, streaming=True)


@ask_bp.route('/stream-ask-anything', methods=['POST'])
def stream_ask_anything() -> ResponseReturnValue:
    """Stream free-form Ask Anything responses."""
    try:
        data = request.get_json() or {}
        question = (data.get('question') or '').strip()

        def _norm(value: Any) -> Any:
            return value.strip() if isinstance(value, str) else value

        birth_date = _norm(data.get('birth_date'))
        birth_time = _norm(data.get('birth_time'))
        timezone_offset = _norm(data.get('timezone_offset'))
        latitude = _norm(data.get('latitude'))
        longitude = _norm(data.get('longitude'))
        personality = normalize_personality(_norm(data.get('personality')))

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

        ai_client_error = _require_ai_client()
        if ai_client_error:
            return ai_client_error

        logger.info("Streaming ask-anything response")

        def generate() -> Iterator[str]:
            try:
                for chunk in stream_calculate_ask_anything(
                    question,
                    birth_date,
                    birth_time,
                    timezone_offset,
                    latitude,
                    longitude,
                    personality,
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
