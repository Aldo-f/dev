#!/bin/bash
set -e

echo "Starting Mike versioning setup..."

# Activate venv
source venv/bin/activate

# Install mike
pip install mike

# Configure mike in mkdocs.yml (already done via nav structure)
echo "Mike configured in mkdocs.yml"

# Deploy versions
mike deploy --push main v3.0.0

echo "Mike versioning setup complete!"