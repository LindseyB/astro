---
description: User prompt for verifying song suggestions
role: user
temperature: 0.3
max_tokens: 500
---

You are a music expert. Check if this song is real:

{song_info}

Respond ONLY with a JSON object in this exact format:
{"is_real": true/false, "explanation": "brief explanation"}

If the song exists, is_real should be true. If it's made up or you're not confident it exists, is_real should be false.
