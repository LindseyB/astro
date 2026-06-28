#!/usr/bin/env python3
"""
Astro Chart Calculator - Flask Web Application
Run this script to start the web server
"""

import os


def _is_debug_enabled():
    """Return True when runtime should enable Flask debug behavior."""
    return os.environ.get('FLASK_DEBUG', '').strip() == '1'

if __name__ == '__main__':
    try:
        from dotenv import load_dotenv
        project_root = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(dotenv_path=os.path.join(project_root, '.env'), override=False)
    except ImportError:
        # python-dotenv is optional; env vars can still be set in the shell.
        pass

    # Running via this helper implies local development unless explicitly overridden.
    resolved_flask_env = os.environ.get('FLASK_ENV', '').strip().lower()
    if not resolved_flask_env:
        os.environ['FLASK_ENV'] = 'development'
        resolved_flask_env = 'development'
    os.environ.setdefault('FLASK_DEBUG', '1' if resolved_flask_env == 'development' else '0')

    from main import app

    port = int(os.environ.get("PORT", 8080))

    print("🌟 Starting Astro Horoscope...")
    print(f"📍 Open your browser to: http://localhost:{port}")
    print("⏹️  Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=port, debug=_is_debug_enabled())
