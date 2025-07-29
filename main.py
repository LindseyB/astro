from flask import Flask, render_template, request, redirect, url_for
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
from datetime import datetime

app = Flask(__name__)

# Filter for planets only (exclude house cusps, angles, etc.)
PLANET_NAMES = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron']

def calculate_chart(birth_date, birth_time, timezone_offset, latitude, longitude):
    """Calculate astrological chart data"""
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

    return {
        'sun': sun.sign,
        'moon': moon.sign,
        'ascendant': ascendant.sign,
        'planets_in_houses': planets_in_houses,
        'house_names': house_names,
        'current_planets': current_planets
    }

@app.route('/')
def index():
    return render_template('index.html')

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
        return render_template('chart.html', chart_data=chart_data)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)