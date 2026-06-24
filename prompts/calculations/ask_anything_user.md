---
description: User prompt for freeform astrology question answering
role: user
temperature: 0.6
---

Give this person a confident, direct take on their question by reading their natal chart AGAINST the current sky. Weigh both: what their birth chart reveals about who they are, AND how today's planetary positions and any retrogrades are transiting that chart right now. Reference at least one current transit (a present-day planet position or retrograde) and tie it to a placement in their natal chart. Be witty, fun, and definitive. Use short bullets where useful. Don't hedge or suggest they trust their own intuition instead - give them the astrological answer!

Question: {question}

NATAL CHART (who they are):
Sun: {sun_sign}, Moon: {moon_sign}, Ascendant: {ascendant_sign}

Planets in Houses:
{planets_in_houses}

CURRENT SKY (transits happening now):
{current_planets}
