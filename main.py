from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

# ---- User Input ----
birth_date = '1990/01/01'
birth_time = '8:00'  # in 'HH:MM' 24h format
timezone_offset = '-05:00'  # e.g. '-05:00' for EST (New York standard time)
latitude = '40n42'  # New York City (40°42'N)
longitude = '74w00' # New York City (74°00'W)

# ---- Setup ----
dt = Datetime(birth_date, birth_time, timezone_offset)
pos = GeoPos(latitude, longitude)
chart = Chart(dt, pos)

# ---- Calculate Positions ----
sun = chart.get('Sun')
moon = chart.get('Moon')
ascendant = chart.get('Asc')

# ---- Output Results ----
print (f"☀️ {sun.sign}")
print (f"🌙 {moon.sign}")
print (f"⬆️ {ascendant.sign}")
