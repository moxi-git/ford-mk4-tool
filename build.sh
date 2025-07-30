#!/usr/bin/env bash
# build.sh - Activate environment, build with PyInstaller, and archive results

echo "Ford Mondeo Diagnostics Tool - Build Script"
echo "==========================================="

# Check if virtual environment exists
if [ ! -d .venv ]; then
  echo "Virtual environment not found. Creating..."
  python3 -m venv .venv
fi

echo "Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate || {
  echo "Failed to activate virtual environment"
  echo "Make sure you have a proper Python virtual environment set up"
  exit 1
}

# Install/upgrade required packages
echo "Installing/upgrading build dependencies..."
pip install --upgrade pip
pip install pyinstaller

# Install project dependencies
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "Installing core dependencies..."
  pip install python-obd pyserial
  pip install PyGObject 2>/dev/null || echo "Warning: PyGObject not available - GUI may not work"
fi

# Clean previous builds
echo "Cleaning previous builds..."
[ -d build ] && rm -rf build
[ -d dist ] && rm -rf dist
[ -d __pycache__ ] && rm -rf __pycache__

# Create CLI version filename
cli_file="main.py"
[ -f "mondeo-cli.py" ] && cli_file="mondeo-cli.py"

echo "Building CLI version ($cli_file)..."
if [ -f "$cli_file" ]; then
  pyinstaller --onefile --name mondeo-cli "$cli_file"
  if [ $? -ne 0 ]; then
    echo "Failed to build CLI version"
    exit 1
  fi
else
  echo "Warning: CLI file not found, skipping CLI build"
fi

echo "Building GUI version (main-gui.py)..."
if [ -f main-gui.py ]; then
  pyinstaller --onefile --name mondeo-gui --windowed main-gui.py
  if [ $? -ne 0 ]; then
    echo "Warning: GUI build failed - this is normal if GTK is not available"
  fi
else
  echo "Warning: main-gui.py not found, skipping GUI build"
fi

echo "Build complete!"

# Check if dist directory was created
if [ ! -d dist ]; then
  echo "No dist/ directory found - builds may have failed"
  exit 1
fi

cd dist || exit 1

echo "Contents of dist directory:"
ls -la

# Create archives
echo "Creating archives..."

if [ -f mondeo-cli ]; then
  echo "Creating CLI archive..."
  7z a mondeo-cli.7z mondeo-cli
  if [ $? -eq 0 ]; then
    echo "Cleaning CLI executable..."
    rm -f mondeo-cli
  else
    echo "Warning: 7z not found or failed, keeping executable"
  fi
else
  echo "No CLI executable found"
fi

if [ -f mondeo-gui ]; then
  echo "Creating GUI archive..."
  7z a mondeo-gui.7z mondeo-gui
  if [ $? -eq 0 ]; then
    echo "Cleaning GUI executable..."
    rm -f mondeo-gui
  else
    echo "Warning: 7z not found or failed, keeping executable"
  fi
else
  echo "No GUI executable found"
fi

# Alternative compression if 7z not available
if ! command -v 7z >/dev/null; then
  echo "7z not found, using tar.gz compression..."

  [ -f mondeo-cli ] && tar -czf mondeo-cli.tar.gz mondeo-cli && rm -f mondeo-cli
  [ -f mondeo-gui ] && tar -czf mondeo-gui.tar.gz mondeo-gui && rm -f mondeo-gui
fi

echo ""
echo "Build Summary:"
echo "=============="
echo "Archives created in dist/:"
ls -la

cd ..

echo ""
echo "Build process complete!"
echo ""
echo "To test before building:"
echo "  source .venv/bin/activate"
echo "  python $cli_file"
echo ""
echo "Install 7z for better compression:"
echo "  sudo apt install p7zip-full  # Ubuntu/Debian"
echo "  sudo dnf install p7zip       # Fedora"
echo "  sudo pacman -S p7zip         # Arch"
