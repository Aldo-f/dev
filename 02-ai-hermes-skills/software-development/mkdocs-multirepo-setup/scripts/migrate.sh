#!/bin/bash
set -euo pipefail

echo "Starting migration of Jekyll to MkDocs with multirepo plugin..."

# Repository Setup
if [ -d "Aldo-f.github.io" ]; then
    rm -rf Aldo-f.github.io
fi

gh repo clone Aldo-f/Aldo-f.github.io
cd Aldo-f.github.io

# Jekyll Cleanup
rm -rf _includes _layouts _posts pages
rm -f _config.yml Gemfile Gemfile.lock

# Move index.md to docs/
mkdir -p docs
if [ -f index.md ]; then
    mv index.md docs/index.md
else
    echo "Warning: index.md not found. Creating placeholder."
    touch docs/index.md
fi

# Generate files
cat > requirements.txt << 'EOF'
mkdocs
mkdocs-material
mkdocs-multirepo-plugin
EOF

cat > mkdocs.yml << 'EOF'
site_name: Aldo Fieuw Documentation
site_url: https://aldo-f.github.io
repo_url: https://github.com/Aldo-f/Aldo-f.github.io
repo_name: Aldo-f/Aldo-f.github.io
theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
    - scheme: slate
      primary: indigo
      accent: indigo
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.top
    - search.highlight
    - search.share
    - navigation.indexes
    - toc.integrate
    - navigation.sections
    - toc.follow
plugins:
  - search
  - multirepo:
      nav_repos:
        - name: thuis
          url: https://github.com/Aldo-f/thuis
        - name: infra
          url: https://github.com/AldO-f/01-core-infra
nav:
  - Home: docs/index.md
  - Thuis: !import [thuis]
  - Core Infra: !import [infra]
extra:
  social:
    - icon: fontawesome/all
EOF

cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy MkDocs site to GitHub Pages

on:
  push:
    branches:
      - master

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Build site
        run: mkdocs build
      - name: Upload artifact
        uses: actions/upload-pages-artifact
        with:
          path: site
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages
EOF

# Commit and push
git add .
git commit -m "Migrate Jekyll to MkDocs with multirepo plugin"
git push origin master

echo "Migration completed successfully!"
EOF
