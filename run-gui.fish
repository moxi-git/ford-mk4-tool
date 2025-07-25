#!/usr/bin/env fish
# run-gui.fish - Activate virtual environment and run main-gui.py

if not test -f .venv/bin/activate.fish
    echo "Virtual environment not found or not fish-compatible."
    exit 1
end

source .venv/bin/activate.fish

python3 main-gui.py
