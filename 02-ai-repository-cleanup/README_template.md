# README Template with Ko-fi Integration
# Place this in your repo's README.md

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/J2Z126OL9C)

# aldo-f.github.io

Personal documentation hub for Aldo Fieuw's projects and home-lab services.

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/usful)
[![GitHub Pages Deploy](https://github.com/Aldo-f/Aldo-f.github.io/actions/workflows/deploy.yml/badge.svg)](https://github.com/Aldo-f/Aldo-f.github.io/actions/workflows/deploy.yml)
[![GitHub Pages Status](https://img.shields.io/github/actions/workflow/status/Aldo-f/Aldo-f.github.io/deploy.yml?branch=main&label=pages%20deploy)](https://aldo-f.github.io)
[![MkDocs Material](https://img.shields.io/badge/mkdocs-material-9.5.31-blue)](https://squidfunk.github.io/mkdocs-material/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Last Updated](https://img.shields.io/github/last-commit/Aldo-f/Aldo-f.github.io/main)](https://github.com/Aldo-f/Aldo-f.github.io/commits/main)

## What's here

Documentation collected from multiple repositories and served via [GitHub Pages](https://aldo-f.github.io):

## Structure

```
06-apps-aldo-f-github-io/
├── docs/en/          # English documentation
├── docs/nl/          # Dutch documentation
├── .github/workflows/deploy.yml    # GitHub Pages deployment
├── mkdocs.yml                # Site configuration
└── requirements.txt          # Python dependencies
```

## Local development

```bash
# Install dependencies
pip install -r requirements.txt

# Start dev server (English)
mkdocs serve -f mkdocs.en.yml

# Start dev server (Dutch)
mkdocs serve -f mkdocs.nl.yml

# Build both sites
mkdocs build --strict -f mkdocs.en.yml
mkdocs build --strict -f mkdocs.nl.yml
```

## Deployment

Pushes to `main` trigger automatic GitHub Pages deployment via the [deploy.yml](.github/workflows/deploy.yml) workflow.

- English site → `https://aldo-f.github.io/`
- Dutch site → `https://aldo-f.github.io/nl/`

## Support the Project

If this project has helped you, please consider showing your support! A small donation helps me dedicate more time to projects like this. Thank you!

Patreon | PayPal | Ko-fi Thanks for trying it and let me know how you like it!