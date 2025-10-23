#!/bin/bash

# Vertex AI Search Setup Script
echo "Setting up Vertex AI Search Python integration..."

# Create virtual environment
python3 -m venv venv-312
source venv-312/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

echo "Setup complete!"
echo "To activate the virtual environment, run: source venv-312/bin/activate"
echo "Make sure to authenticate with: gcloud auth application-default login"
