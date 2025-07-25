#!/usr/bin/env fish
# clean.fish - Remove PyInstaller or setuptools build artifacts

echo "Cleaning build artifacts..."
rm -rf build dist *.spec __pycache__ *.pyc *.pyo
echo "Clean complete."
