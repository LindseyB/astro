---
description: User prompt for chart-based music suggestions
role: user
temperature: 0.4
---

Based on this astrological chart, recommend ONE perfect song of the following genre: {song_request}. Try to provide _ONLY_ the song title and artist in this exact format:
🎶 [Title] by [Artist]

If you're having a hard time providing a song, recommend an artist instead in this format:

Artist: [Artist Name]

Provide a single sentence justification for your recommendation. It should be concise, short, and to the point, while maintaining a casual, vibey tone.

{tracks_block}Chart Data:
Sun: {sun_sign}, Moon: {moon_sign}, Ascendant: {ascendant_sign}

Planets in Houses:
{planets_in_houses}

{current_planets_block}
