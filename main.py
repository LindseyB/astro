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
    chart = Chart(dt, pos)
    today_chart = Chart(Datetime(current_date, current_time, timezone_offset), pos)

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

    # Mercury retrograde check
    mercury = today_chart.get(const.MERCURY)
    mercury_retrograde = mercury.isRetrograde()

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
        'mercury': {
            'sign': mercury.sign,
            'degree': mercury.signlon,
            'retrograde': mercury_retrograde
        }
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