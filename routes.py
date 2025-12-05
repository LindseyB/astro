"""
Flask application and route handlers
"""

from flask import Flask, render_template, request
from config import logger
from formatters import markdown_filter
from calculations import calculate_chart, calculate_full_chart, calculate_live_mas
from launchdarkly_service import should_show_chart_wheel

app = Flask(__name__)

# Add markdown filter to convert markdown to HTML
app.template_filter('markdown')(markdown_filter)

def get_user_ip():
    """Get the user's IP address for feature flag evaluation"""
    # Check for X-Forwarded-For header (load balancer/proxy)
    if request.headers.get('X-Forwarded-For'):
        # Get the first IP in case of multiple proxies
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    # Check for X-Real-IP header (nginx)
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    # Fallback to remote_addr
    else:
        return request.remote_addr or '127.0.0.1'


@app.route('/')
def index():
    """Render home page"""
    return render_template('index.html')


@app.route('/chart', methods=['POST'])
def chart():
    """Handle daily horoscope request"""
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    music_genre = request.form.get('music_genre', 'any')

    # Handle "other" genre option
    if music_genre == 'other':
        other_genre = request.form.get('other_genre', '').strip()
        if other_genre:
            music_genre = other_genre
        else:
            music_genre = 'any'

    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')

    try:
        logger.info(f"Calculating chart for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        # Calculate chart
        chart_data = calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre)
        return render_template('chart.html', chart_data=chart_data, form_data=request.form)
    except Exception as e:
        logger.error(f"ERROR in /chart route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your chart. Please check your birth information and try again.")


@app.route('/full-chart', methods=['POST'])
def full_chart():
    """Handle full natal chart request"""
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    music_genre = request.form.get('music_genre', 'any')

    # Handle "other" genre option
    if music_genre == 'other':
        other_genre = request.form.get('other_genre', '').strip()
        if other_genre:
            music_genre = other_genre
        else:
            music_genre = 'any'

    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')
    
    # Get user IP and check feature flag
    user_ip = get_user_ip()
    show_chart_wheel = True #should_show_chart_wheel(user_ip)

    try:
        logger.info(f"Calculating full chart for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        logger.info(f"Chart wheel display flag for IP {user_ip}: {show_chart_wheel}")
        
        # Calculate full chart
        full_chart_data = calculate_full_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre)
        return render_template('full_chart.html', chart_data=full_chart_data, show_chart_wheel=show_chart_wheel)
    except Exception as e:
        logger.error(f"ERROR in /full-chart route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your full chart. Please check your birth information and try again.")


@app.route('/live-mas', methods=['POST'])
def live_mas():
    """Handle Taco Bell order request"""
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')

    try:
        logger.info(f"Calculating Live Más order for: {birth_date} {birth_time} {timezone_offset} {latitude} {longitude}")
        # Calculate Live Más order
        live_mas_data = calculate_live_mas(birth_date, birth_time, timezone_offset, latitude, longitude)
        return render_template('live_mas.html', chart_data=live_mas_data, form_data=request.form)
    except Exception as e:
        logger.error(f"ERROR in /live-mas route: {type(e).__name__}: {str(e)}")
        if app.debug:
            import traceback
            traceback.print_exc()
            return f"<h1>Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500
        else:
            return render_template('error.html', error="Something went wrong while calculating your Taco Bell order. Please check your birth information and try again.")
