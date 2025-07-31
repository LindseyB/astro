from flask import Flask, render_template, request
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
from datetime import datetime
import os
from openai import OpenAI
import markdown

app = Flask(__name__)

# Add markdown filter to convert markdown to HTML
@app.template_filter('markdown')
def markdown_filter(text):
    if not text:
        return ""
    return markdown.markdown(text, extensions=['nl2br'])

# Client setup for OpenAI API
token = os.environ.get("GITHUB_TOKEN") or "default_token"
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

# Filter for planets only (exclude house cusps, angles, etc.)
PLANET_NAMES = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron']

# Planet constants mapping for Flatlib
PLANET_CONSTANTS = {
    'Sun': const.SUN,
    'Moon': const.MOON,
    'Mercury': const.MERCURY,
    'Venus': const.VENUS,
    'Mars': const.MARS,
    'Jupiter': const.JUPITER,
    'Saturn': const.SATURN,
    'Uranus': const.URANUS,
    'Neptune': const.NEPTUNE,
    'Pluto': const.PLUTO,
    'Chiron': const.CHIRON
}

def prepare_music_genre_text(music_genre, chart_type="daily"):
    """
    Prepare music genre preference text for AI prompts
    
    Args:
        music_genre (str): The music genre preference
        chart_type (str): Either "daily" for daily horoscope or "natal" for full chart
    
    Returns:
        str: Formatted genre preference text for AI prompt
    """
    if not music_genre or music_genre.lower() == "any":
        return ""
    
    if music_genre.lower() == "other":
        if chart_type == "natal":
            return " (Please suggest a song from any genre that fits the chart)"
        else:
            return " (Please suggest songs from any genre that fits the vibe)"
    else:
        return f" (Please prioritize {music_genre} genre if possible)"

def extract_form_data(request_form):
    """
    Extract and process form data from Flask request
    
    Args:
        request_form: Flask request.form object
        
    Returns:
        dict: Processed form data with proper formatting
    """
    birth_date_html = request_form['birth_date']
    birth_time = request_form['birth_time']
    timezone_offset = request_form['timezone_offset']
    latitude = request_form['latitude']
    longitude = request_form['longitude']
    music_genre = request_form.get('music_genre', 'any')
    
    # Handle "other" genre option
    if music_genre == 'other':
        other_genre = request_form.get('other_genre', '').strip()
        if other_genre:
            music_genre = other_genre
        else:
            music_genre = 'any'
    
    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')
    
    return {
        'birth_date': birth_date,
        'birth_time': birth_time,
        'timezone_offset': timezone_offset,
        'latitude': latitude,
        'longitude': longitude,
        'music_genre': music_genre
    }

def create_chart(birth_date, birth_time, timezone_offset, latitude, longitude):
    """
    Create a natal chart from birth data
    
    Args:
        birth_date (str): Birth date in YYYY/MM/DD format
        birth_time (str): Birth time in HH:MM format
        timezone_offset (str): Timezone offset (e.g., '-5')
        latitude (str): Latitude 
        longitude (str): Longitude
        
    Returns:
        Chart: Flatlib Chart object
    """
    dt = Datetime(birth_date, birth_time, timezone_offset)
    pos = GeoPos(latitude, longitude)
    return Chart(dt, pos, IDs=const.LIST_OBJECTS)

def get_planet_data(chart, include_houses=False):
    """
    Extract planet data from a chart
    
    Args:
        chart: Flatlib Chart object
        include_houses (bool): Whether to include house information
        
    Returns:
        dict: Planet data with signs, degrees, and optionally houses
    """
    planets = {}
    
    for planet_name, planet_const in PLANET_CONSTANTS.items():
        try:
            planet_obj = chart.get(planet_const)
            if planet_obj and hasattr(planet_obj, 'sign') and hasattr(planet_obj, 'signlon'):
                planet_data = {
                    'sign': planet_obj.sign,
                    'degree': float(planet_obj.signlon)
                }
                if include_houses:
                    planet_data['house'] = None  # Will be filled by caller
                planets[planet_name] = planet_data
        except Exception as e:
            print(f"Warning: Could not get data for {planet_name}: {e}")
            continue
    
    return planets

def get_ai_analysis(user_prompt, chart_type="daily"):
    """
    Get AI analysis with error handling
    
    Args:
        user_prompt (str): The prompt to send to the AI
        chart_type (str): Type of chart analysis
        
    Returns:
        str: AI analysis response or fallback message
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a zoomer astrologer who uses lots of emojis and is very casual. You are also very concise and to the point. You are an expert in astrology and can analyze charts quickly.",
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=1.0,
            top_p=1.0,
            model=model,
            timeout=30  # 30 second timeout
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Handle various API errors gracefully
        error_type = type(e).__name__
        print(f"AI Analysis Error ({error_type}): {str(e)}")
        
        if chart_type == "natal":
            return f"**Cosmic Note:** The AI astrologer is taking a cosmic coffee break. ☕ You're as special and unique as the stars! 🔮"
        else:
            return f"**Cosmic Note:** The AI astrologer is taking a cosmic coffee break. ☕ Trust your intuition today! 🔮"

def format_planets_for_api(current_planets):
    planet_strings = []
    retrograde_planets = []
    
    for planet_name, planet_data in current_planets.items():
        # Format basic position
        position_str = f"{planet_name} in {planet_data['sign']} at {planet_data['degree']:.2f} degrees"
        
        # Add retrograde status
        if planet_data['retrograde']:
            position_str += " (RETROGRADE)"
            retrograde_planets.append(planet_name)
        else:
            position_str += " (direct)"
            
        planet_strings.append(position_str)
    
    # Create the complete string
    result = "CURRENT PLANETARY POSITIONS:\n"
    result += "\n".join(planet_strings)
    
    if retrograde_planets:
        result += f"\n\nRETROGRADE PLANETS: {', '.join(retrograde_planets)}"
    else:
        result += "\n\nNo planets are currently retrograde."
    
    return result

def calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre="any"):
    now = datetime.now()
    current_date = now.strftime('%Y/%m/%d')
    current_time = now.strftime('%H:%M')

    # Setup charts
    chart = create_chart(birth_date, birth_time, timezone_offset, latitude, longitude)
    today_chart = create_chart(current_date, current_time, timezone_offset, latitude, longitude)

    # Calculate main positions
    sun = chart.get('Sun')
    moon = chart.get('Moon')
    ascendant = chart.get('House1')

    # Get all houses and their objects
    houses = chart.houses
    planets_in_houses = {}

    for house in houses:
        house_number = int(house.id.replace('House', ''))
        planets_in_houses[house_number] = {
            'house_obj': house,
            'planets': []
        }

        # Get all objects in this house
        objects_in_house = chart.objects.getObjectsInHouse(house)

        for obj in objects_in_house:
            if obj.id in PLANET_NAMES:
                planets_in_houses[house_number]['planets'].append({
                    'name': obj.id,
                    'sign': obj.sign,
                    'object': obj
                })

    # Get all current planet statuses
    current_planets = {}
    
    for planet_name, planet_const in PLANET_CONSTANTS.items():
        try:
            planet_obj = today_chart.get(planet_const)
            # Check if planet object exists and has the required attributes
            if planet_obj and hasattr(planet_obj, 'sign') and hasattr(planet_obj, 'signlon'):
                retrograde = False
                
                # Sun and Moon don't go retrograde
                if planet_name not in ['Sun', 'Moon']:
                    if hasattr(planet_obj, 'isRetrograde'):
                        try:
                            retrograde = planet_obj.isRetrograde()
                        except:
                            retrograde = False
                
                current_planets[planet_name] = {
                    'sign': planet_obj.sign,
                    'degree': float(planet_obj.signlon),
                    'retrograde': retrograde
                }
        except Exception as e:
            # Skip planets that cause errors but continue with others
            print(f"Warning: Could not get data for {planet_name}: {e}")
            continue

    house_names = {
        1: "1st House (Self/Identity) 🪞",
        2: "2nd House (Money/Values) 💰",
        3: "3rd House (Communication) 💬",
        4: "4th House (Home/Family) 🏡",
        5: "5th House (Creativity/Romance) 🎨",
        6: "6th House (Health/Work) 🧑‍💼",
        7: "7th House (Partnerships) 🤝",
        8: "8th House (Transformation) 🔄",
        9: "9th House (Philosophy/Travel) 🌍",
        10: "10th House (Career/Reputation) 🏆",
        11: "11th House (Friends/Hopes) 👥",
        12: "12th House (Spirituality/Subconscious) 🔮"
    }

    # Prepare music genre preference text
    genre_text = prepare_music_genre_text(music_genre, "daily")
    
    # Build the user prompt
    user_prompt = "Only respond in a few sentences. Based on the following astrological chart data please recommend some activities to do or not to do ideally in bullet format the first sentence in your response should be what today's vibe will be like please also recommend a single song to listen to and recommend a beverage to drink given today's vibe:\n\n" + \
                  f"Sun: {sun.sign}, Moon: {moon.sign}, Ascendant: {ascendant.sign}\n\n" + \
                  "Planets in Houses:\n" + \
                  "\n".join([f"{house_names[house_number]}: " + ", ".join([f"{p['name']} in {p['sign']}" for p in data['planets']]) for house_number, data in planets_in_houses.items()]) + "\n\n" + \
                  "Current Planets status:\n" + \
                  format_planets_for_api(current_planets) + \
                  f"\n\nMusic Preference: {genre_text}" if genre_text else ""
    
    astrology_analysis = get_ai_analysis(user_prompt, "daily")

    return {
        'sun': sun.sign,
        'moon': moon.sign,
        'ascendant': ascendant.sign,
        'mercury_retrograde': current_planets.get('Mercury', {}).get('retrograde', False),
        'astrology_analysis': astrology_analysis
    }

@app.route('/')
def index():
    return render_template('index.html')

def calculate_full_chart(birth_date, birth_time, timezone_offset, latitude, longitude, music_genre="any"):
    """Calculate comprehensive natal chart data"""
    chart = create_chart(birth_date, birth_time, timezone_offset, latitude, longitude)

    sun = chart.get('Sun')
    moon = chart.get('Moon')
    ascendant = chart.get('House1')

    planets = get_planet_data(chart, include_houses=True)

    # Get all houses and their objects
    houses = chart.houses
    house_data = {}
    
    for house in houses:
        house_number = int(house.id.replace('House', ''))
        house_data[house_number] = {
            'sign': house.sign,
            'degree': float(house.signlon),
            'planets': []
        }

        # Get all objects in this house
        objects_in_house = chart.objects.getObjectsInHouse(house)

        for obj in objects_in_house:
            if obj.id in planets:
                planets[obj.id]['house'] = house_number
                house_data[house_number]['planets'].append({
                    'name': obj.id,
                    'sign': obj.sign,
                    'degree': float(obj.signlon)
                })
    genre_text = prepare_music_genre_text(music_genre, "natal")
    
    user_prompt = (
        "Only respond in a few sentences. Based on the following natal chart data, "
        "please give a concise, emoji-filled summary of this person's personality and life themes. "
        "Highlight any unique planetary placements or house patterns. "
        f"Format your response in bullet points. Recommend a single song that fits this chart{genre_text}:\n\n"
        f"Sun: {sun.sign}, Moon: {moon.sign}, Ascendant: {ascendant.sign}\n\n"
        "Planets:\n" +
        "\n".join([
            f"- {name}: {data['sign']} at {data['degree']:.2f}° in House {data['house'] or 'N/A'}"
            for name, data in planets.items()
        ]) +
        "\n\nHouses:\n" +
        "\n".join([
            f"- House {num} ({house_data[num]['sign']} {house_data[num]['degree']:.2f}°): " +
            ", ".join([f"{p['name']} in {p['sign']} ({p['degree']:.2f}°)" for p in house_data[num]['planets']]) or "No major planets"
            for num in sorted(house_data.keys())
        ])
    )

    astrology_analysis = get_ai_analysis(user_prompt, "natal")

    return {
        'sun': sun.sign,
        'moon': moon.sign,
        'ascendant': ascendant.sign,
        'planets': planets,
        'houses': house_data,
        'astrology_analysis': astrology_analysis
    }

@app.route('/chart', methods=['POST'])
def chart():
    try:
        # Extract and process form data
        form_data = extract_form_data(request.form)
        
        # Calculate chart
        chart_data = calculate_chart(
            form_data['birth_date'], 
            form_data['birth_time'], 
            form_data['timezone_offset'], 
            form_data['latitude'], 
            form_data['longitude'], 
            form_data['music_genre']
        )
        return render_template('chart.html', chart_data=chart_data, form_data=request.form)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/full-chart', methods=['POST'])
def full_chart():
    try:
        # Extract and process form data
        form_data = extract_form_data(request.form)
        
        # Calculate full chart
        full_chart_data = calculate_full_chart(
            form_data['birth_date'], 
            form_data['birth_time'], 
            form_data['timezone_offset'], 
            form_data['latitude'], 
            form_data['longitude'], 
            form_data['music_genre']
        )
        return render_template('full_chart.html', chart_data=full_chart_data)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)