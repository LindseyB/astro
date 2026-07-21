# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Overview

**Astro Horoscope** is a Flask web app that generates AI-powered astrological horoscopes using the Claude API (Anthropic SDK). It calculates natal charts via the Swiss Ephemeris (`swisseph`) library and serves a responsive bento-grid UI.

## Stack

- **Backend**: Python / Flask (`main.py`, `run.py`)
- **AI**: Anthropic Claude API via `ai_service.py`
- **Astrology engine**: Swiss Ephemeris (`swisseph/`)
- **Feature flags**: LaunchDarkly (`launchdarkly_service.py`)
- **Music data**: Last.fm API (`lastfm_service.py`)
- **Templates**: Jinja2 (`templates/`)
- **Static assets**: Vanilla JS web components (`static/js/components/`), CSS
- **Tests**: pytest (`tests/`)

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Flask app factory and startup |
| `run.py` | Dev server entrypoint |
| `routes.py` | Primary route handlers |
| `ai_service.py` | Claude API calls, streaming |
| `calculations.py` | Ephemeris / chart math |
| `prompt_templates.py` | Shared prompt loader |
| `prompts/` | Markdown prompt files with frontmatter |
| `static/js/components/` | Web components (see README) |
| `config.py` | App config and env vars |
| `validation.py` | Input validation helpers |

## Development Commands

```bash
make test            # run full test suite
make test-unit       # unit tests only
make test-frontend   # frontend tests only
make test-coverage   # tests with coverage report
python run.py        # start dev server (port 8080)
```

## Prompt System

Prompts live in `prompts/` as Markdown files with YAML frontmatter (`description`, `role`, `temperature`, `max_tokens`). Bodies use `{placeholder}` syntax for Python `str.format()`. Load them through `prompt_templates.py` — do not inline prompts in Python files.

## Web Components

Frontend behavior is componentized under `static/js/components/` and registered in `static/js/components/index.js`. Add new interactive UI as a custom element there. The legacy adapters (`button-loading.js`, `section-toggle.js`, `copy-analysis.js`) are deprecated — do not extend them.

## Feature Flags

Feature flags use LaunchDarkly (`launchdarkly_service.py`). See `LAUNCHDARKLY.md` for setup details. Always provide a safe boolean default when evaluating a flag — assume the SDK may be absent in dev environments.

## Design System

Follow `DESIGN_SYSTEM.md` for colors, typography, spacing, and component styling. Key tokens:
- Primary accent: `#00CED1` (cyan)
- Secondary accent: `#9333ea` (purple)
- Fonts: Space Grotesk (display), DM Sans (body), JetBrains Mono (mono)

## Testing Conventions

- Tests live in `tests/`; use pytest
- Do not mock the database or external APIs unless unavoidable — prefer real service calls or fixtures
- Run the full suite before opening a PR

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | Yes | Flask session secret |
| `ANTHROPIC_TOKEN` | Yes | Claude API key |
| `LAUNCHDARKLY_SDK_KEY` | No | Feature flags (falls back to defaults) |
| `LAST_FM_API_KEY` | No | Real song recommendations |

Copy `.env.example` to `.env` for local development. The app auto-loads `.env` on startup.
