---
title: Home
hide:
  - toc
  - navigation
  - feedback
  - social
  - navigation.tabs
---

# MkDocs All Plugins Template

Development site that exercises every MkDocs plugin in the 06-apps stack.

## Plugin checklist

| Plugin | Status | Notes |
|--------|--------|-------|
| `search` | enabled | Material built-in |
| `blog` | enabled | posts in `docs/en/blog/posts/` |
| `mkdocs_pivot_table` | enabled | interactive tables with hide/show, swap, sort |
| `mkdocs_raw_markdown` | enabled | `.md` raw source endpoint |
| `multirepo` | enabled | imports `thuis` |
| `blanky` | enabled | external links `target=_blank` |
| `section-index` | enabled | auto section indexes |

## Quick start

```bash
cd ~/dev/06-apps-mkdocs-template
source ~/dev/06-apps-aldo-f-github-io/venv/bin/activate
mkdocs serve -f mkdocs.en.yml --dev-addr=0.0.0.0:8001
```
