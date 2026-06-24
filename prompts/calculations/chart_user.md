---
description: User prompt for daily horoscope generation
role: user
temperature: 1.0
---

Only respond in a few sentences. Based on the following astrological chart data: First give a single sentence summarizing the day as what today's vibe will be like. Then recommend activities in this exact markdown format:

✅ Do:

- item 1
- item 2
- item 3

❌ Don't:

- item 1
- item 2
- item 3

Please also recommend a beverage to drink given today's vibe:

Sun: {sun_sign}, Moon: {moon_sign}, Ascendant: {ascendant_sign}

Planets in Houses:
{planets_in_houses}

Current Planets status:
{current_planets}
