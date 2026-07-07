---
description: User prompt for freeform astrology question answering
role: user
temperature: 0.6
---

Give a short, punchy astrological answer. Blend the natal chart with current transits: one key placement, one relevant transit, done. Be direct and witty. No hedging, no padding.

Question: {question}

NATAL CHART (who they are):
Sun: {sun_sign}, Moon: {moon_sign}, Ascendant: {ascendant_sign}

Planets in Houses:
{planets_in_houses}

CURRENT SKY (transits happening now):
{current_planets}
