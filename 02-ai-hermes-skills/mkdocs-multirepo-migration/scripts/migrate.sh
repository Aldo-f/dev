#!/bin/bash
set -euo pipefail

# MkDocs Multirepo Migration Script
# Usage: ./migrate.sh [repo-clone-dir]
# 
# This script migrates a Jekyll GitHub Pages site to MkDocs with
# the multirepo plugin for aggregating documentation from multiple repos.

REPO_DIR="${1:-.}"
cd "$REPO_DIR"

echo "=== MkDocs Multirepo Migration ==="
echo "Working directory: $(pwd)"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "ERROR: Not in a git repository. Clone the repo first:"
    echo "  gh repo clone <owner>/<repo>"
    exit 1
fi

# 1. Jekyll Cleanup
echo ""
echo "Step 1: Cleaning Jekyll artifacts..."
rm -rf _includes _layouts _posts pages
rm -f _config.yml Gemfile Gemfile.lock
echo "✓ Jekyll cleanup complete"

# 2. Create docs directory and preserve homepage
echo ""
echo "Step 2: Preserving homepage..."
mkdir -p docs
if [ -f index.md ]; then
    mv index.md docs/index.md
    echo "✓ Moved index.md to docs/index.md"
else
    echo "⚠ No index.md found. Creating empty docs/index.md"
    touch docs/index.md
fi

# 3. Create requirements.txt
echo ""
echo "Step 3: Creating requirements.txt..."
cat > requirements.txt << 'EOF'
mkdocs
mkdocs-material
mkdocs-multirepo-plugin
EOF
echo "✓ requirements.txt created"

# 4. Create mkdocs.yml
echo ""
echo "Step 4: Creating mkdocs.yml..."
cat > mkdocs.yml << 'EOF'
site_name: Documentation Hub
site_url: https://OWNER.github.io
repo_url: https://github.com/OWNER/REPO
repo_name: OWNER/REPO
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
plugins:
  - search
  - multirepo
nav:
  - Home: docs/index.md
  # Add your imports below - remember to quote the !import tag!
  # - 'Section Name: "!import https://github.com/OWNER/REPO?branch=main"'
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/OWNER
markdown_extensions:
  - toc:
      permalink: true
EOF
echo "✓ mkdocs.yml created (EDIT ME - update site_name, repo_url, and nav imports)"

# 5. Create GitHub Actions workflow
echo ""
echo "Step 5: Creating GitHub Actions workflow..."
mkdir -p .github/workflows
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy MkDocs site to GitHub Pages

on:
  push:
    branches:
      - master
      - main

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
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
EOF
echo "✓ GitHub Actions workflow created"

# 6. Update .gitignore
echo ""
echo "Step 6: Updating .gitignore..."
cat > .gitignore << 'EOF'
_site
.sass-cache
.jekyll-metadata
site/
migrate.sh
.venv/
venv/
*.pyc
__pycache__/
EOF
echo "✓ .gitignore updated"

# 7. Git operations
echo ""
echo "Step 7: Git operations..."
git add .
if git diff --cached --quiet; then
    echo "⚠ No changes to commit"
else
    git commit -m "Migrate to MkDocs with multirepo plugin"
    echo "✓ Committed changes"
    
    echo ""
    echo "Push to deploy:"
    echo "  git push origin master"
    echo "  git push origin main"
fi

echo ""
echo "=== Migration Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit mkdocs.yml - update site_name, repo_url, and add your imports"
echo "2. Add content to docs/index.md"
echo "3. Run 'mkdocs build' to test locally"
echo "4. Run 'git push origin master' to deploy"
echo ""
echo "Important: Quote the !import tag in YAML:"
echo "  - 'Section: \"!import https://github.com/OWNER/REPO?branch=main\"'"