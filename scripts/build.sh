#!/bin/bash
# build.sh - Build the project with PyInstaller

echo "Building main.py..."
pyinstaller --onefile main.py

echo "Building main-gui.py..."
pyinstaller --onefile main-gui.py

echo "Build complete!"
