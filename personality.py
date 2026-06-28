"""Personality selection helpers for astrology prompt styling."""

from typing import Final

DEFAULT_PERSONALITY: Final[str] = "default"
WITCHY_PERSONALITY: Final[str] = "witchy"
GOTH_PERSONALITY: Final[str] = "goth"

PERSONALITY_OPTIONS: Final[tuple[str, ...]] = (
    DEFAULT_PERSONALITY,
    WITCHY_PERSONALITY,
    GOTH_PERSONALITY,
)

PERSONALITY_LABELS: Final[dict[str, str]] = {
    DEFAULT_PERSONALITY: "Default",
    WITCHY_PERSONALITY: "Witchy",
    GOTH_PERSONALITY: "Goth",
}

PERSONALITY_PROMPT_APPENDIX: Final[dict[str, str]] = {
    WITCHY_PERSONALITY: (
        "Adopt a witchy mystical voice. Focus your language on crystals, moon phases, candle work, "
        "tarot symbolism, and elemental currents. Keep the tone enchanting but still practical. "
        "Favor emojis like 🔮, 🌙, ✨, 🕯️, 🃏, and 🌊."
    ),
    GOTH_PERSONALITY: (
        "Adopt a dark goth voice that is moody, atmospheric, and poetic. Emphasize ravens, black attire, "
        "gothic music references, and nocturnal energy. Keep the style brooding but helpful. "
        "Use only black emojis, specifically 🖤 and ⚫."
    ),
}


def normalize_personality(personality: str | None) -> str:
    """Return a supported personality key, defaulting for unknown values."""
    value = (personality or DEFAULT_PERSONALITY).strip().lower()
    return value if value in PERSONALITY_OPTIONS else DEFAULT_PERSONALITY


def apply_personality_to_system_prompt(system_prompt: str, personality: str | None) -> str:
    """Append personality-specific system instructions to the base system prompt."""
    normalized = normalize_personality(personality)
    appendix = PERSONALITY_PROMPT_APPENDIX.get(normalized)
    if not appendix:
        return system_prompt
    return f"{system_prompt}\n\n{appendix}"


def get_personality_choices() -> tuple[tuple[str, str], ...]:
    """Return ordered (value, label) choices for UI rendering."""
    return tuple((value, PERSONALITY_LABELS[value]) for value in PERSONALITY_OPTIONS)
