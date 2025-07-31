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

def calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude):
    now = datetime.now()
    current_date = now.strftime('%Y/%m/%d')
    current_time = now.strftime('%H:%M')

    # Setup chart
    dt = Datetime(birth_date, birth_time, timezone_offset)
    pos = GeoPos(latitude, longitude)
    chart = Chart(dt, pos, IDs=const.LIST_OBJECTS)
    today_chart = Chart(Datetime(current_date, current_time, timezone_offset), pos, IDs=const.LIST_OBJECTS)

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
    planet_constants = {
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
    
    for planet_name, planet_const in planet_constants.items():
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

    # Generate AI analysis with error handling
    try:
        # Build the user prompt
        user_prompt = "Only respond in a few sentences. Based on the following astrological chart data please recommend some activities to do or not to do ideally in bullet format the first sentence in your response should be what today's vibe will be like please also recommend a single song to listen to and recommend a beverage to drink given today's vibe:\n\n" + \
                      f"Sun: {sun.sign}, Moon: {moon.sign}, Ascendant: {ascendant.sign}\n\n" + \
                      "Planets in Houses:\n" + \
                      "\n".join([f"{house_names[house_number]}: " + ", ".join([f"{p['name']} in {p['sign']}" for p in data['planets']]) for house_number, data in planets_in_houses.items()]) + "\n\n" + \
                      "Current Planets status:\n" + \
                      format_planets_for_api(current_planets)
        
        # Log the prompt to console
        print("=== USER PROMPT ===")
        print(user_prompt)
        print("=== END PROMPT ===")
        
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
        
        astrology_analysis = response.choices[0].message.content
        
    except Exception as e:
        # Handle various API errors gracefully
        error_type = type(e).__name__
        print(f"AI Analysis Error ({error_type}): {str(e)}")
    
        astrology_analysis = f"**Cosmic Note:** The AI astrologer is taking a cosmic coffee break. ☕ Trust your intuition today! 🔮"


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

def calculate_full_chart(birth_date, birth_time, timezone_offset, latitude, longitude):
    """Calculate comprehensive natal chart data"""
    # Setup chart
    dt = Datetime(birth_date, birth_time, timezone_offset)
    pos = GeoPos(latitude, longitude)
    chart = Chart(dt, pos, IDs=const.LIST_OBJECTS)

    # Calculate main positions
    sun = chart.get('Sun')
    moon = chart.get('Moon')
    ascendant = chart.get('House1')

    # Get all planets with detailed information
    planets = {}
    planet_constants = {
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
    
    for planet_name, planet_const in planet_constants.items():
        try:
            planet_obj = chart.get(planet_const)
            if planet_obj and hasattr(planet_obj, 'sign') and hasattr(planet_obj, 'signlon'):
                planets[planet_name] = {
                    'sign': planet_obj.sign,
                    'degree': float(planet_obj.signlon),
                    'house': None  # Will be filled below
                }
        except Exception as e:
            print(f"Warning: Could not get data for {planet_name}: {e}")
            continue

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

    # Build the user prompt for the full chart
    user_prompt = (
        "Only respond in a few sentences. Based on the following natal chart data, "
        "please give a concise, emoji-filled summary of this person's personality and life themes. "
        "Highlight any unique planetary placements or house patterns. "
        "Format your response in bullet points. Recommend a single song that fits this chart:\n\n"
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

        astrology_analysis = response.choices[0].message.content
    except Exception as e:
        # Handle various API errors gracefully
        error_type = type(e).__name__
        print(f"AI Analysis Error ({error_type}): {str(e)}")

        astrology_analysis = f"**Cosmic Note:** The AI astrologer is taking a cosmic coffee break. ☕ You're as special and unique as the stars! 🔮"

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
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    
    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')
    
    try:
        # Calculate chart
        chart_data = calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude)
        return render_template('chart.html', chart_data=chart_data, form_data=request.form)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/full-chart', methods=['POST'])
def full_chart():
    # Get form data
    birth_date_html = request.form['birth_date']  # HTML date format: YYYY-MM-DD
    birth_time = request.form['birth_time']
    timezone_offset = request.form['timezone_offset']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    
    # Convert date format from YYYY-MM-DD to YYYY/MM/DD
    birth_date = birth_date_html.replace('-', '/')
    
    try:
        # Calculate full chart
        full_chart_data = calculate_full_chart(birth_date, birth_time, timezone_offset, latitude, longitude)
        return render_template('full_chart.html', chart_data=full_chart_data)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)