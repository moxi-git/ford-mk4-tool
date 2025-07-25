#!/usr/bin/env fish
# env-setup.fish - Set up and activate a virtual environment

python -m venv .venv

if not test -f .venv/bin/activate.fish
    echo "Virtual environment activation script for Fish not found."
    echo "Did Python create a Fish-compatible venv?"
    exit 1
end

source .venv/bin/activate.fish

pip install --upgrade pip
pip install -r requirements.txt
