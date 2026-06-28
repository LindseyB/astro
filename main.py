"""
Main entry point for the astrology application.

This module handles the critical Swiss Ephemeris initialization that must occur
before any other astrological libraries are imported, then starts the Flask application.
"""
import os
import logging

try:
    from dotenv import load_dotenv
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, '.env'), override=False)
except ImportError:
    # python-dotenv is optional; env vars can still be set in the shell.
    pass


def _is_debug_enabled():
    """Return True when runtime should enable Flask debug behavior."""
    return os.environ.get('FLASK_DEBUG', '').strip() == '1'

# Ensure direct script execution defaults to local development behavior.
if __name__ == '__main__':
    resolved_flask_env = os.environ.get('FLASK_ENV', '').strip().lower()
    if not resolved_flask_env:
        os.environ['FLASK_ENV'] = 'development'
        resolved_flask_env = 'development'
    os.environ.setdefault('FLASK_DEBUG', '1' if resolved_flask_env == 'development' else '0')

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Problem child pyswisseph logic hack here #
# Set Swiss Ephemeris path BEFORE any other imports

if os.environ.get('SE_EPHE_PATH'):
    ephe_path = os.environ.get('SE_EPHE_PATH')
else:
    # Fallback for local development
    ephe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swisseph')

# Verify path exists
if os.path.exists(ephe_path):
    # Set BOTH environment variables that might be checked
    os.environ['EPHE_PATH'] = ephe_path
    os.environ['SE_EPHE_PATH'] = ephe_path
    logger.info(f"Setting ephemeris path to: {ephe_path}")
    logger.debug(f"Files in directory: {os.listdir(ephe_path)}")
else:
    logger.error(f"Ephemeris path not found: {ephe_path}")

# Import pyswisseph and set path with absolute path
import swisseph as swe
abs_ephe_path = os.path.abspath(ephe_path)
swe.set_ephe_path(abs_ephe_path)
logger.info(f"pyswisseph configured with absolute path: {abs_ephe_path}")

# End problem child pyswisseph logic hack #

# Now import the Flask app from routes module
from routes import app

if __name__ == '__main__':
    app.run(debug=_is_debug_enabled())