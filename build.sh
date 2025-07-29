#!/bin/bash
# Build script for Render deployment

echo "Installing Python packages..."
pip install --upgrade pip setuptools wheel

# Install pyswisseph first (flatlib dependency)
echo "Installing pyswisseph..."
pip install pyswisseph --no-cache-dir

# Install remaining packages
echo "Installing other requirements..."
pip install -r requirements.txt --no-cache-dir

echo "Build complete!"
