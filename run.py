#!/usr/bin/env python3
"""
Astro Chart Calculator - Flask Web Application
Run this script to start the web server
"""

if __name__ == '__main__':
    from main import app
    print("🌟 Starting Astro Chart Calculator...")
    print("📍 Open your browser to: http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=8080, debug=True)
