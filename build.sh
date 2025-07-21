#!/bin/bash
# build.sh - Activate environment, build with PyInstaller, and archive results

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate || {
  echo "Failed to activate virtual environment"
  exit 1
}

# Build the Python scripts
echo "Building main.py..."
pyinstaller --onefile main.py

echo "Building main-gui.py..."
pyinstaller --onefile main-gui.py

echo "Build complete!"

# Change to the dist directory
cd dist || {
  echo "dist/ directory not found"
  exit 1
}

# Archive each executable with 7z
echo "Creating 7z archives..."
7z a main.7z main
7z a main-gui.7z main-gui

echo "7z archives created in dist/"
