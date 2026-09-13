"""MkDocs hook: generate 'How the docs are organized' table from nav_repos (SSOT)."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# Canonical mapping from nav_repo name -> (display_name, url, notes)
# This mirrors the nav_repos in mkdocs.en.yml / mkdocs.nl.yml
REPO_META = {
    "thuis": {
        "display": "Thuis main",
        "url": "https://github.com/Aldo-f/thuis",
        "branch": "main",
        "notes": "Current MkDocs-based documentation (EN + NL)",
    },
    "thuis-v3": {
        "display": "Thuis v3",
        "url": "https://github.com/Aldo-f/thuis",
        "branch": "v3.0.0",
        "notes": "Legacy single-file Python version (MkDocs, EN + NL)",
    },
    "thuis-v4": {
        "display": "Thuis v4",
        "url": "https://github.com/Aldo-f/thuis",
        "branch": "v4.1.0",
        "docs_dir": "website/docs/*",
        "notes": "Installation, usage, credentials",
    },
    "thuis-v5": {
        "display": "Thuis v5",
        "url": "https://github.com/Aldo-f/thuis",
        "branch": "v5/main",
        "docs_dir": "website/docs/*",
        "notes": "Getting started, API, architecture",
    },
    "clock": {
        "display": "Clock",
        "url": "https://github.com/Aldo-f/clock",
        "branch": "main",
        "notes": "Special clocks — features & development docs",
    },
    "blanky": {
        "display": "Blanky",
        "url": "https://gitlab.com/Aldo-f/blanky",
        "branch": "main",
        "notes": "External link opener library",
    },
    "blanky-v1": {
        "display": "Blanky v1",
        "url": "https://gitlab.com/Aldo-f/blanky",
        "branch": "v1-docs",
        "notes": "Legacy Blanky version",
    },
    "opencode-multi-model-fallback": {
        "display": "OpenCode Multi-Model Fallback",
        "url": "https://github.com/Aldo-f/opencode-multi-model-fallback",
        "branch": "main",
        "notes": "Auto-switches fallback models on rate limits",
    },
    "vaultwarden-backup": {
        "display": "Vaultwarden Backup",
        "url": "https://github.com/Aldo-f/07-security-vaultwarden-backup",
        "branch": "main",
        "notes": "Automated cloud backup",
    },
}


def _branch_display(repo: dict) -> str:
    """Return a human-readable branch/tag reference."""
    branch = repo.get("branch", "")
    if branch:
        if branch.startswith("v") and "." in branch:
            return f"tag `{branch}`"
        return f"branch `{branch}`"
    return ""


def _build_table(nav_repos: list[dict]) -> str:
    """Build the markdown table from nav_repos config."""
    lines = [
        "## How the docs are organized",
        "",
        "| Section | Source | Notes |",
        "|---------|--------|-------|",
    ]

    for entry in nav_repos:
        name = entry.get("name", "")
        meta = REPO_META.get(name)
        if not meta:
            # Fallback: use raw entry data
            display = name
            url = entry.get("import_url", "")
            notes = "Documentation imported at build time"
        else:
            display = meta["display"]
            url = meta["url"]
            branch_info = _branch_display(meta)
            if branch_info:
                source = f"[{meta['display']}]({url}) ({branch_info})"
            else:
                source = f"[{meta['display']}]({url})"
            notes = meta.get("notes", "Documentation imported at build time")
            lines.append(f"| **{display}** | {source} | {notes} |")
            continue

        # Fallback row for unknown entries
        lines.append(f"| **{display}** | {url} | {notes} |")

    return "\n".join(lines) + "\n"


def _inject_into_about(content: str, table: str) -> str:
    """Replace the 'How the docs are organized' section in about.md."""
    # Pattern: from "## How the docs are organized" to next "## " or end of file
    pattern = r"(## How the docs are organized\n)(.*?)(\n## |\Z)"
    replacement = r"\1\n" + table + r"\3"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return new_content


def on_page_markdown(markdown: str, page, config, files, **kwargs):
    """Inject the generated table into about.md during markdown processing."""
    # Only process the about page
    if page.file.src_path != "about.md":
        return markdown

    # Get nav_repos from multirepo plugin config
    multirepo_plugin = config.plugins.get("multirepo")
    if not multirepo_plugin:
        return markdown

    nav_repos = getattr(multirepo_plugin.config, "nav_repos", [])
    if not nav_repos:
        return markdown

    table = _build_table(nav_repos)
    return _inject_into_about(markdown, table)


# For direct testing
if __name__ == "__main__":
    import sys

    # Test with mkdocs.en.yml nav_repos
    test_nav_repos = [
        {
            "name": "thuis",
            "import_url": "https://github.com/Aldo-f/thuis?branch=main",
            "imports": ["docs"],
        },
        {
            "name": "vaultwarden-backup",
            "import_url": "https://github.com/Aldo-f/07-security-vaultwarden-backup?branch=main",
            "imports": ["docs"],
        },
        {
            "name": "thuis-v3",
            "import_url": "https://github.com/Aldo-f/thuis?branch=v3.0.0",
            "imports": ["docs"],
        },
        {
            "name": "thuis-v4",
            "import_url": "https://github.com/Aldo-f/thuis?branch=v4.1.0&docs_dir=website/docs/*",
            "imports": ["docs"],
        },
        {
            "name": "thuis-v5",
            "import_url": "https://github.com/Aldo-f/thuis?branch=v5/main&docs_dir=website/docs/*",
            "imports": ["docs"],
        },
        {
            "name": "clock",
            "import_url": "https://github.com/Aldo-f/clock?branch=main",
            "imports": ["docs"],
        },
        {
            "name": "blanky",
            "import_url": "https://gitlab.com/Aldo-f/blanky?branch=main",
            "imports": ["docs"],
        },
        {
            "name": "opencode-multi-model-fallback",
            "import_url": "https://github.com/Aldo-f/opencode-multi-model-fallback?branch=main",
            "imports": ["docs"],
        },
        {
            "name": "blanky-v1",
            "import_url": "https://gitlab.com/Aldo-f/blanky?branch=v1-docs",
            "imports": ["docs"],
        },
    ]

    print(_build_table(test_nav_repos))
