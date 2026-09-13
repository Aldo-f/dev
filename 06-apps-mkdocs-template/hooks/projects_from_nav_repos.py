"""MkDocs hook: generate 'Projects' index content from nav_repos (SSOT).

Replaces the body of docs/<lang>/projects.md at build time, so there's ONE
source of truth: the nav_repos config in mkdocs.<lang>.yml.

The projects.md source files become stubs (front matter + include marker),
and this hook injects the generated markdown via on_page_markdown.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Canonical metadata per nav_repo name
REPO_META = {
    "thuis": {
        "display": "Thuis",
        "url": "https://github.com/Aldo-f/thuis",
        "versions": [
            ("main", "thuis/docs/index.md", "`main` branch"),
            ("v5", "thuis-v5/website/docs/intro.md", "`v5/main`"),
            ("v4", "thuis-v4/website/docs/intro.md", "tag `v4.1.0`"),
            ("v3", "thuis-v3/docs/index.md", "tag `v3.0.0`"),
        ],
    },
    "clock": {
        "display": "Clock",
        "url": "https://github.com/Aldo-f/clock",
    },
    "blanky": {
        "display": "Blanky",
        "url": "https://gitlab.com/Aldo-f/blanky",
    },
    "blanky-v1": {
        "display": "Blanky v1",
        "url": "https://gitlab.com/Aldo-f/blanky",
    },
    "opencode-multi-model-fallback": {
        "display": "OpenCode Multi-Model Fallback",
        "url": "https://github.com/Aldo-f/opencode-multi-model-fallback",
    },
    "vaultwarden-backup": {
        "display": "Vaultwarden Backup",
        "url": "https://github.com/Aldo-f/07-security-vaultwarden-backup",
    },
}


def _build_projects_md(nav_repos: list[dict]) -> str:
    lines = [
        "# Projects",
        "",
        "A quick index of everything documented on this hub.",
        "",
    ]
    for entry in nav_repos:
        name = entry.get("name", "")
        meta = REPO_META.get(name)
        if not meta:
            continue
        display = meta["display"]
        url = meta.get("url")
        versions = meta.get("versions", [])

        if versions:
            lines.append(f"## {meta['display']}")
            lines.append("")
            # VRT MAX video downloader etc — derive from display
            doc_ref = versions[0][1]
            lines.append(f"- Docs: [{display}]({doc_ref})")
            lines.append("")
            lines.append("|| Version | Docs | Source ref |")
            lines.append("||---------|------|------------|")
            for label, doc_path, ref in versions:
                lines.append(f"|| {label} | [{label}]({doc_path}) | {ref} |")
            if url:
                lines.append("")
                lines.append(f"- Source: [{display}]({url})")
            lines.append("")
        else:
            lines.append(f"## {display}")
            lines.append("")
            if url:
                lines.append(f"- Source: [{display}]({url})")
            lines.append("")

    return "\n".join(lines)


def on_page_markdown(markdown: str, page, config, files, **kwargs):
    """Inject generated content into projects.md."""
    if page.file.src_path != "projects.md":
        return markdown

    multirepo = config.plugins.get("multirepo")
    if not multirepo or not hasattr(multirepo, "config"):
        return markdown

    nav_repos = getattr(multirepo.config, "nav_repos", [])
    if not nav_repos:
        return markdown

    return _build_projects_md(nav_repos)
