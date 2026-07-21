# GitHub Copilot Instructions

## Project

**Astro Horoscope** — a Flask/Python web app that generates AI-powered astrological horoscopes using the Claude API. It calculates natal charts via the Swiss Ephemeris library and serves a responsive bento-grid UI with vanilla JS web components.

## Stack

- **Backend**: Python / Flask
- **AI**: Anthropic Claude API (`ai_service.py`)
- **Astrology**: Swiss Ephemeris (`swisseph/`)
- **Feature flags**: LaunchDarkly (`launchdarkly_service.py`)
- **Templates**: Jinja2 (`templates/`)
- **Frontend**: Vanilla JS custom elements (`static/js/components/`)
- **Tests**: pytest

## Code Style

- Python: follow existing style (no type annotations are used in this codebase, keep it consistent)
- Keep Flask route handlers thin — move logic into service/helper modules
- Do not inline prompt text in Python; use the `prompts/` directory and load via `prompt_templates.py`
- New UI behavior belongs in a custom element under `static/js/components/`, not in the deprecated legacy adapters (`button-loading.js`, `section-toggle.js`, `copy-analysis.js`)

## Prompts

Prompts live in `prompts/` as Markdown files with YAML frontmatter:

```markdown
---
description: Short human-readable summary
role: user
temperature: 0.4
max_tokens: 500
---

Prompt body with {placeholder} variables.
```

Use `str.format()` placeholders. Load through `prompt_templates.py`.

## Feature Flags

Always provide a safe boolean default when evaluating a LaunchDarkly flag — the SDK key may be absent in dev. See `LAUNCHDARKLY.md` for flag details.

## Design System

Follow `DESIGN_SYSTEM.md` for all UI work:
- Primary accent: `#00CED1` (cyan)
- Secondary accent: `#9333ea` (purple)
- Fonts: Space Grotesk (display), DM Sans (body), JetBrains Mono (mono/labels)
- Dark/light theme via CSS custom properties (`--primary-accent`, etc.)

## Testing

Run tests with `make test`. Add pytest tests in `tests/` for new backend logic. Do not skip tests or mock away external dependencies without a good reason.

## Environment

Required env vars: `SECRET_KEY`, `ANTHROPIC_TOKEN`. Optional: `LAUNCHDARKLY_SDK_KEY`, `LAST_FM_API_KEY`. Copy `.env.example` → `.env` for local dev.
