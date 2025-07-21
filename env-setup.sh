#!/bin/bash
# env-setup.sh - Set up and activate a virtual environment

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
