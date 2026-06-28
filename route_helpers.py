"""Shared helpers for Flask route handlers."""

from flask import jsonify

import ai_service
from config import logger


def _require_ai_client():
    """Return a 503 JSON response when the AI client is unavailable."""
    try:
        ai_service.get_client()
    except ValueError as e:
        logger.error("AI service not available: %s", e)
        return jsonify({'error': 'AI service is currently unavailable. Please try again later.'}), 503
    return None
