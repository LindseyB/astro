# Astro Chart Calculator

A web-based astrological chart calculator built with Flask and Flatlib.

## Features

- 🌟 Calculate natal charts with Sun, Moon, and Ascendant signs
- � Display planets in all 12 houses
- 📡 Check current Mercury retrograde status
- 🌐 Web interface for easy input and viewing
- 📱 Responsive design

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask app:
```bash
python run.py
```

3. Open your browser to: http://localhost:5000

## Usage

1. Enter your birth information:
   - Birth date and time
   - Timezone offset (include daylight savings)
   - Latitude and longitude of birth location

2. Click "Generate Chart" to see your natal chart

3. View your:
   - Main signs (Sun, Moon, Ascendant)
   - Planets in houses
   - Current Mercury retrograde status

## Location Format Examples

- **New York City:** 40n42, 74w00, -05:00 (EST) / -04:00 (EDT)
- **Los Angeles:** 34n03, 118w15, -08:00 (PST) / -07:00 (PDT)
- **London:** 51n30, 0w10, +00:00 (GMT) / +01:00 (BST)
- **Paris:** 48n52, 2e20, +01:00 (CET) / +02:00 (CEST)

## Development

The app uses:
- **Flask** for the web framework
- **Flatlib** for astrological calculations