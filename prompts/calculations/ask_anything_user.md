---
description: User prompt for freeform astrology question answering
role: user
temperature: 0.6
---

Answer the question using the natal chart and current transits together. Keep the response short and direct: 2-3 sentences max. No hedging, no padding. You don't need to explain your astrological reasoning; just give the answer.

Question: {question}

NATAL CHART (who they are):
Sun: {sun_sign}, Moon: {moon_sign}, Ascendant: {ascendant_sign}

Planets in Houses:
{planets_in_houses}

CURRENT SKY (transits happening now):
{current_planets}
