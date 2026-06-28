"""Shared helpers for Flask route handlers."""

from flask import Response, jsonify

import ai_service
from config import logger


def _require_ai_client() -> tuple[Response, int] | None:
    """Return None when the AI client is available; otherwise return a (JSON response, 503) tuple."""
    try:
        ai_service.get_client()
    except ValueError as e:
        logger.error("AI service not available: %s", e)
        return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503
    return None
