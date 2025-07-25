from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

# ---- User Input ----
birth_date = '1986/06/25'
birth_time = '8:00'  # in 'HH:MM' 24h format
# daylight savings time :sob:
timezone_offset = '-04:00'  # e.g. '-05:00' for EST (New York standard time)
latitude = '40n42'  # New York City (40°42'N)
longitude = '74w00' # New York City (74°00'W)

# Filter for planets only (exclude house cusps, angles, etc.)
PLANET_NAMES = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

# ---- Setup ----
dt = Datetime(birth_date, birth_time, timezone_offset)
pos = GeoPos(latitude, longitude)
chart = Chart(dt, pos)

# ---- Calculate Positions ----
sun = chart.get('Sun')
moon = chart.get('Moon')
ascendant = chart.get('House1')  # Ascendant is the first house

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


# ---- Output Results ----
print("🌟 MAIN SIGNS:")
print(f"☀️ Sun: {sun.sign}")
print(f"🌙 Moon: {moon.sign}")
print(f"⬆️ Ascendant: {ascendant.sign}")


# ---- Planets in Houses ----
print("\n🏠 HOUSES AND PLANETS:")
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

for house_num in range(1, 13):
    house_data = planets_in_houses[house_num]
    house = house_data['house_obj']
    print(f"\n{house_names[house_num]}:")
    print(f"  Sign: {house.sign}")

    if house_data['planets']:
        print("  Planets:")
        for planet_info in house_data['planets']:
            print(f"    • {planet_info['name']}: {planet_info['sign']}")
    else:
        print("  Planets: None")

