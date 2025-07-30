#!/usr/bin/env python3
"""
Astro Chart Calculator - Flask Web Application
Run this script to start the web server
"""

if __name__ == '__main__':
    from main import app
    import os

    port = int(os.environ.get("PORT", 8080))

    print("🌟 Starting Astro Horoscope...")
    print(f"📍 Open your browser to: http://localhost:{port}")
    print("⏹️  Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=port, debug=True)
