"""MkDocs hook: injects related posts section into blog posts.

Scans all blog posts, finds those sharing tags or categories,
and adds a "Lees ook" section at the bottom of each post.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import defaultdict


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract frontmatter dict and body from markdown content."""
    if not content.startswith("---"):
        return {}, content
    match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
    if not match:
        return {}, content
    fm_text, body = match.groups()

    fm: dict = {}
    current_key = None
    current_list: list[str] = []

    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if current_key:
                current_list.append(line[2:].strip().strip('"').strip("'"))
        elif ":" in line:
            if current_key and current_list:
                fm[current_key] = current_list
                current_list = []
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            current_key = key
            if value:
                fm[key] = value
                current_key = None

    if current_key and current_list:
        fm[current_key] = current_list

    return fm, body


def _find_blog_posts(docs_dir: Path) -> list[Path]:
    """Find all blog post files."""
    posts_dir = docs_dir / "blog" / "posts"
    if not posts_dir.exists():
        return []
    return sorted(posts_dir.glob("*.md"))


def _build_index(posts: list[Path]) -> tuple[dict, dict]:
    """Build tag and category indexes keyed by resolved file path."""
    tag_index: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    cat_index: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    for post_path in posts:
        content = post_path.read_text(encoding="utf-8")
        fm, _ = _parse_frontmatter(content)
        post_tags = [t.lower() for t in fm.get("tags", [])]
        post_cats = [c.lower() for c in fm.get("categories", [])]
        for tag in post_tags:
            tag_index[tag].append((post_path, fm))
        for cat in post_cats:
            cat_index[cat].append((post_path, fm))
    return dict(tag_index), dict(cat_index)


def _get_related(
    current_path: Path,
    current_tags: list[str],
    current_cats: list[str],
    tag_index: dict,
    cat_index: dict,
    blog_base: Path,
) -> list[tuple[str, str]]:
    """Find related posts by tags or categories."""
    scored: dict[Path, int] = {}
    for tag in current_tags:
        tag = tag.lower()
        if tag in tag_index:
            for path, fm in tag_index[tag]:
                if path.resolve() == current_path.resolve():
                    continue
                score = scored.get(path, 0) + 2
                scored[path] = score
    for cat in current_cats:
        cat = cat.lower()
        if cat in cat_index:
            for path, fm in cat_index[cat]:
                if path.resolve() == current_path.resolve():
                    continue
                score = scored.get(path, 0) + 1
                scored[path] = score

    related = sorted(scored.items(), key=lambda x: -x[1])[:5]
    result = []
    for path, _score in related:
        try:
            # Preserve language folder in URL (e.g., /nl/blog/...)
            rel_url = "/" + path.relative_to(blog_base.parent.parent).as_posix()
        except ValueError:
            rel_url = "/" + path.name
        content = path.read_text(encoding="utf-8")
        fm, _ = _parse_frontmatter(content)
        display_title = fm.get("title", path.stem)
        result.append((display_title, rel_url))
    return result


def on_config(config, **kwargs):
    """Pre-build the blog post index for reuse."""
    docs_dir = Path(config.docs_dir)
    blog_posts = _find_blog_posts(docs_dir)
    if blog_posts:
        tag_index, cat_index = _build_index(blog_posts)
        config._blog_tag_index = tag_index
        config._blog_cat_index = cat_index
        config._blog_posts = blog_posts
        print(f"[RELATED] Found {len(blog_posts)} blog posts", file=sys.stderr)
    return config


def on_page_markdown(markdown: str, page, config, **kwargs):
    """Inject related posts into blog post pages."""
    src_path = getattr(getattr(page, "file", None), "src_path", None)

    # Only process individual blog posts, not indexes or category pages
    if not src_path or (
        "blog/posts/" not in src_path and "blog\\posts\\" not in src_path
    ):
        return markdown

    # Skip if this is an index page (e.g., blog/index.md, category/index.md)
    if src_path.endswith("/index.md") or src_path.endswith("\\index.md"):
        return markdown

    blog_posts = getattr(config, "_blog_posts", None)
    tag_index = getattr(config, "_blog_tag_index", {})
    cat_index = getattr(config, "_blog_cat_index", {})

    if not blog_posts:
        return markdown

    current_path = Path(getattr(page.file, "abs_src_path", "")).resolve()
    current_tags = [t.lower() for t in page.meta.get("tags", [])]
    current_cats = [c.lower() for c in page.meta.get("categories", [])]

    blog_base = Path(config.docs_dir) / "blog" / "posts"

    related = _get_related(
        current_path, current_tags, current_cats, tag_index, cat_index, blog_base
    )

    if not related:
        return markdown

    sections = []
    # Determine language from docs_dir to show translated label
    docs_dir_str = str(config.docs_dir).lower()
    section_label = (
        "See also"
        if "/en/" in docs_dir_str or docs_dir_str.endswith("/en")
        else "Lees ook"
    )

    for title, url in related:
        sections.append(f'<a href="{url}">{title}</a>')

    related_html = f"""
<div class="related-posts md-typeset">
<h2 id="related-posts">{section_label}</h2>
<ul class="related-list">
{"".join(f'<li>{s}</li>' for s in sections)}
</ul>
</div>
"""

    if "<!-- more -->" in markdown:
        markdown = markdown.replace("<!-- more -->", related_html + "\n<!-- more -->")
    else:
        markdown = markdown.rstrip() + "\n\n" + related_html

    print(
        f"[RELATED] Injected {len(related)} related posts into {src_path}",
        file=sys.stderr,
    )
    return markdown


def on_post_page(output: str, page, config, **kwargs):
    """Add CSS for related posts."""
    src_path = getattr(getattr(page, "file", None), "src_path", None)
    if not src_path or (
        "/blog/posts/" not in src_path and "\\blog\\posts\\" not in src_path
    ):
        return output

    css = """
<style>
.related-posts {
  margin: 2rem 0;
  padding: 1.5rem;
  background: var(--md-default-fg-color--lightest);
  border-radius: 4px;
}
.related-posts h2 {
  margin-top: 0;
  font-size: 1.1rem;
  text-transform: uppercase;
  color: var(--md-default-fg-color--medium);
}
.related-list {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0;
}
.related-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--md-default-fg-color--light);
}
.related-list li:last-child {
  border-bottom: none;
}
.related-list a {
  color: var(--md-default-fg-color);
  text-decoration: none;
}
.related-list a:hover {
  color: var(--md-accent-fg-color);
  text-decoration: underline;
}
</style>
"""
    return output + css
