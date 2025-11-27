# Codespaces Setup

This repository is configured to work with GitHub Codespaces.

## Quick Start

1. Click the "Code" button on GitHub
2. Select "Codespaces" tab
3. Click "Create codespace on main"

The environment will automatically:
- Install Python 3.10
- Install all dependencies from requirements.txt
- Set up the Flask development environment

## Running the App

Once the Codespace is ready:

```bash
python main.py
```

The app will be available on port 5000, which will be automatically forwarded.

## Environment Variables

You'll need to set your Anthropic API key:

```bash
export ANTHROPIC_TOKEN="your-api-key-here"
```

Or create a `.env` file:

```
ANTHROPIC_TOKEN=your-api-key-here
```

## Running Tests

```bash
pytest tests/
```

## Features

- Python 3.10 (as specified in .python-version)
- All dependencies pre-installed
- Flask app configured with port forwarding
- Python extensions and linting pre-configured
