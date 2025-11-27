#!/bin/bash
# Script to download Swiss Ephemeris data files

EPHE_DIR="${SE_EPHE_PATH:-/workspaces/astro/swisseph}"

echo "Creating ephemeris directory: $EPHE_DIR"
mkdir -p "$EPHE_DIR"

cd "$EPHE_DIR"

echo "Downloading Swiss Ephemeris files... Because everything is terrible! 😭"

# Download essential ephemeris files from GitHub
# These files contain planetary position data
wget -q --show-progress https://github.com/aloistr/swisseph/raw/refs/heads/master/ephe/seas_18.se1
if [ $? -ne 0 ]; then
    echo "Failed to download seas_18.se1"
    exit 1
fi
wget -q --show-progress https://github.com/aloistr/swisseph/raw/refs/heads/master/ephe/semo_18.se1
if [ $? -ne 0 ]; then
    echo "Failed to download semo_18.se1"
    exit 1
fi
wget -q --show-progress https://github.com/aloistr/swisseph/raw/refs/heads/master/ephe/sepl_18.se1
if [ $? -ne 0 ]; then
    echo "Failed to download sepl_18.se1"
    exit 1
fi

# Verify that all files exist
for f in seas_18.se1 semo_18.se1 sepl_18.se1; do
    if [ ! -f "$f" ]; then
        echo "File $f is missing after download!"
        exit 1
    fi
done
echo "Download complete! You can verify the files below:"
echo "Ephemeris files are in: $EPHE_DIR"
ls -lh "$EPHE_DIR"

echo "Happy hacking! 🖤"