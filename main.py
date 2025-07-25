from skyfield.api import load, Topos
from datetime import datetime
import pytz

def get_zodiac_sign(ecliptic_longitude_degrees):
    """Convert ecliptic longitude to zodiac sign"""
    # Normalize to 0-360 degrees
    longitude = ecliptic_longitude_degrees % 360

    zodiac_signs = [
        (0, "Aries"), (30, "Taurus"), (60, "Gemini"), (90, "Cancer"),
        (120, "Leo"), (150, "Virgo"), (180, "Libra"), (210, "Scorpio"),
        (240, "Sagittarius"), (270, "Capricorn"), (300, "Aquarius"), (330, "Pisces")
    ]

    for i, (start_degree, sign) in enumerate(zodiac_signs):
        next_degree = zodiac_signs[(i + 1) % 12][0] if i < 11 else 360
        if start_degree <= longitude < next_degree:
            degree_in_sign = longitude - start_degree
            return f"{sign} {degree_in_sign:.1f}°"

    return "Unknown"

# 1. Set birth data
birth_date = '1986-06-25'
birth_time = '12:00'  # 24-hour format
timezone = 'America/New_York'
latitude = 40.7128
longitude = -74.0060

# 2. Parse datetime with timezone
dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
dt_local = pytz.timezone(timezone).localize(dt)
dt_utc = dt_local.astimezone(pytz.utc)

# 3. Load ephemeris and timescale
eph = load('de421.bsp')
ts = load.timescale()
t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute)

# 4. Observer location
observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

# 5. Compute planetary positions
planets = [
    ('Sun', eph['sun']),
    ('Moon', eph['moon']),
    ('Mercury', eph['mercury']),
    ('Venus', eph['venus']),
    ('Mars', eph['mars']),
    ('Jupiter', eph['jupiter barycenter']),
    ('Saturn', eph['saturn barycenter']),
    ('Uranus', eph['uranus barycenter']),
    ('Neptune', eph['neptune barycenter']),
    ('Pluto', eph['pluto barycenter'])
]

for name, planet in planets:
    astrometric = eph['earth'] + observer
    apparent = astrometric.at(t).observe(planet).apparent()
    ra, dec, distance = apparent.radec()

    # Get ecliptic coordinates for zodiac calculation
    ecliptic_lat, ecliptic_lon, ecliptic_distance = apparent.ecliptic_latlon()
    zodiac = get_zodiac_sign(ecliptic_lon.degrees)

    print(f"{name}: RA={ra.hours:.2f}h, Dec={dec.degrees:.2f}°, "
          f"Distance={distance.au:.2f} AU, Zodiac: {zodiac}")

# Special focus on Sun's zodiac sign (main zodiac sign)
sun_astrometric = eph['earth'] + observer
sun_apparent = sun_astrometric.at(t).observe(eph['sun']).apparent()
sun_ecliptic_lat, sun_ecliptic_lon, sun_ecliptic_distance = sun_apparent.ecliptic_latlon()
main_zodiac_sign = get_zodiac_sign(sun_ecliptic_lon.degrees)

print(f"\n🌟 Main Zodiac Sign (Sun): {main_zodiac_sign}")
print(f"   Ecliptic Longitude: {sun_ecliptic_lon.degrees:.2f}°")