#!/usr/bin/env fish
# build.fish - Activate environment, build with PyInstaller, and archive results

echo "Activating virtual environment..."
if not source .venv/bin/activate
    echo "Failed to activate virtual environment"
    exit 1
end

echo "Building main.py..."
pyinstaller --onefile main.py

echo "Building main-gui.py..."
pyinstaller --onefile main-gui.py

echo "Build complete!"

if not cd dist
    echo "dist/ directory not found"
    exit 1
end

echo "Creating 7z archives..."
7z a main.7z main
7z a main-gui.7z main-gui

echo "clean executables"
rm -rf main main-gui

echo "7z archives created in dist/"
