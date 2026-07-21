"""Shared helpers for Flask route handlers."""

from flask import Response, jsonify, render_template

import ai_service
from config import logger


def _missing_field_response(route: str, field: str) -> tuple[Response, int]:
    """Return a 400 response for a missing required form field."""
    logger.error("ERROR in %s route — missing field: %s", route, field)
    return render_template(
        'http_error.html',
        code=400,
        message='Bad Request',
        description="Please fill in all required fields and try again.",
    ), 400


def _require_ai_client() -> tuple[Response, int] | None:
    """Return None when the AI client is available; otherwise return a (JSON response, 503) tuple."""
    try:
        ai_service.get_client()
    except ValueError as e:
        logger.error("AI service not available: %s", e)
        return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503
    return None
