#!/usr/bin/env fish
# build.fish - Activate environment, build with PyInstaller, and archive results

echo "Ford Mondeo Diagnostics Tool - Build Script"
echo "==========================================="

# Check if virtual environment exists
if not test -d .venv
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv
end

echo "Activating virtual environment..."
if not source .venv/bin/activate.fish
    echo "Failed to activate virtual environment"
    echo "Make sure you have a proper Python virtual environment set up"
    exit 1
end

# Install/upgrade required packages
echo "Installing/upgrading build dependencies..."
pip install --upgrade pip
pip install pyinstaller

# Install project dependencies
if test -f requirements.txt
    pip install -r requirements.txt
else
    echo "Installing core dependencies..."
    pip install python-obd pyserial
    # Try GTK for GUI version
    pip install PyGObject 2>/dev/null || echo "Warning: PyGObject not available - GUI may not work"
end

# Clean previous builds
echo "Cleaning previous builds..."
if test -d build
    rm -rf build
end
if test -d dist
    rm -rf dist
end
if test -d __pycache__
    rm -rf __pycache__
end

# Create CLI version filename
set cli_file "main.py"
if test -f "mondeo-cli.py"
    set cli_file "mondeo-cli.py"
end

echo "Building CLI version ($cli_file)..."
if test -f $cli_file
    pyinstaller --onefile --name mondeo-cli $cli_file
    if test $status -ne 0
        echo "Failed to build CLI version"
        exit 1
    end
else
    echo "Warning: CLI file not found, skipping CLI build"
end

echo "Building GUI version (main-gui.py)..."
if test -f main-gui.py
    # For GUI applications, we might want additional options
    pyinstaller --onefile --name mondeo-gui --windowed main-gui.py
    if test $status -ne 0
        echo "Warning: GUI build failed - this is normal if GTK is not available"
    end
else
    echo "Warning: main-gui.py not found, skipping GUI build"
end

echo "Build complete!"

# Check if dist directory was created
if not test -d dist
    echo "No dist/ directory found - builds may have failed"
    exit 1
end

# Move to dist directory
cd dist

echo "Contents of dist directory:"
ls -la

# Create archives if files exist
echo "Creating archives..."

if test -f mondeo-cli
    echo "Creating CLI archive..."
    7z a mondeo-cli.7z mondeo-cli
    if test $status -eq 0
        echo "Cleaning CLI executable..."
        rm -f mondeo-cli
    else
        echo "Warning: 7z not found, keeping executable"
    end
else
    echo "No CLI executable found"
end

if test -f mondeo-gui
    echo "Creating GUI archive..."
    7z a mondeo-gui.7z mondeo-gui
    if test $status -eq 0
        echo "Cleaning GUI executable..."
        rm -f mondeo-gui
    else
        echo "Warning: 7z not found, keeping executable"
    end
else
    echo "No GUI executable found"
end

# Alternative compression if 7z is not available
if not command -v 7z >/dev/null
    echo "7z not found, using tar.gz compression..."

    if test -f mondeo-cli
        tar -czf mondeo-cli.tar.gz mondeo-cli
        rm -f mondeo-cli
    end

    if test -f mondeo-gui
        tar -czf mondeo-gui.tar.gz mondeo-gui
        rm -f mondeo-gui
    end
end

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
echo "  source .venv/bin/activate.fish"
echo "  python $cli_file"
echo ""
echo "Install 7z for better compression:"
echo "  sudo apt install p7zip-full  # Ubuntu/Debian"
echo "  sudo dnf install p7zip       # Fedora"
echo "  sudo pacman -S p7zip         # Arch"
