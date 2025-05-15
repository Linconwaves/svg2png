#!/bin/bash

# Exit immediately if a command fails
set -e

mkdir -p server/templates

cd server

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install flask cairosvg flask-cors
pip freeze > requirements.txt

# Deactivate virtual environment
deactivate

# Return to project root
cd ../..

echo "✅ Setup complete."
echo "👉 Placed Django file in: server/templates/index.html"
echo "👉 To run the server:"
echo "   source server/venv/bin/activate"
echo "   python server/app.py"