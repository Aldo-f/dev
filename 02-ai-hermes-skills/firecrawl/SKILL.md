---
name: firecrawl
description: Firecrawl tools for web scraping, searching, and research.
---

# Firecrawl

Firecrawl helps agents search first, scrape clean content, interact with live pages when plain extraction is not enough, parse local documents into markdown, search scientific papers and GitHub history through the research index, monitor pages for changes, and produce finished deliverables from web data.

## Install

The Firecrawl CLI is installed for live web work:

```bash
npx -y firecrawl-cli@latest init --all --browser
```

## Setup

- Ensure `FIRECRAWL_API_KEY` is set in the environment (`~/.firecrawl.env`).
- Verify installation: `firecrawl --status`

## Usage Paths

- Need web data during this session -> Path A (live tools)
- Need to add Firecrawl to app code -> Path B (app integration)
- Need a finished deliverable from web data -> Path C (workflow skills)

See https://www.firecrawl.dev/agent-onboarding/SKILL.md for detailed path instructions.
