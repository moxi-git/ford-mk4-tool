#!/bin/bash
# clean.sh - Remove PyInstaller or setuptools build artifacts

echo "Cleaning build artifacts..."
rm -rf build/ dist/ *.spec __pycache__/ *.pyc *.pyo
echo "Clean complete."

