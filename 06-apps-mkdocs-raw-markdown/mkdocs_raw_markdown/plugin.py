import logging
import os
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.structure.files import File

log = logging.getLogger("mkdocs.plugins")


class RawMarkdownPlugin(BasePlugin):
    config_scheme = (("suffix", config_options.Type(str, default=".md")),)

    def on_files(self, files, config):
        """Add virtual .md files for each markdown page.

        CHANGED:
        - Use `list(files)` to avoid "dictionary changed size during iteration".
        - Skip `blog/posts/` (handled by the blog plugin).
        - Preserve original `abs_src_path` via `File.generated()` so multirepo
          temp-dir paths are resolved correctly at read-time.
        - Only create virtual files for local (non-imported) docs; for multirepo
          imports, we let the multirepo plugin handle the files instead.
        """
        suffix = self.config["suffix"]
        self._virtual_files = {}  # Maps virtual src_path -> original abs_src_path

        # Collect multirepo repo names to skip them (multirepo handles its own files)
        multirepo_name_set = set()
        multirepo_plugin = config.plugins.get("multirepo")
        if multirepo_plugin and hasattr(multirepo_plugin, "config"):
            mr_config = multirepo_plugin.config
            if hasattr(mr_config, "nav_repos"):
                multirepo_name_set = {e.get("name", "") for e in mr_config.nav_repos}
            elif isinstance(mr_config, dict):
                multirepo_name_set = {
                    e.get("name", "") for e in mr_config.get("nav_repos", [])
                }

        for file in list(files):
            # Skip blog directory — the blog plugin handles its own markdown files
            if file.src_path.endswith(".md") and not file.src_path.startswith(
                "blog/posts/"
            ):
                # For multirepo-imported repos, skip creating virtual files here;
                # the multirepo plugin clones docs to a temp dir and those files are
                # served by the multirepo plugin's own read_source mechanism.
                is_mr = any(
                    name in (file.src_path or "") for name in multirepo_name_set
                )
                if is_mr:
                    continue

                # Create virtual path with suffix (e.g., "index.md" -> "index.md.md")
                virtual_path = file.src_path + suffix

                # Store the original file's absolute source path so we can read it
                # at read-time.
                self._virtual_files[virtual_path] = file.abs_src_path

                # Create new File with virtual path — use File() with the original
                # src_dir/dest_dir so generated files resolve correctly.
                new_file = File(
                    virtual_path,
                    file.src_dir,
                    file.dest_dir,
                    file.use_directory_urls,
                )
                files.append(new_file)
        return files

    def on_page_read_source(self, page, config):
        """Serve raw markdown content for virtual .md files.

        CHANGED:
        - Use `self._virtual_files.get(src_path)` to look up the original
          abs_src_path that was stored in on_files().
        - If the abs_src_path exists on disk, read and return its content.
        - If not (e.g. multirepo temp dir already cleaned), fall back gracefully
          to returning empty string instead of raising FileNotFoundError.
        - Remove the old fallback path-construct logic that assumed local docs_dir.
        """
        suffix = self.config["suffix"]
        src_path = page.file.src_path
        if src_path.endswith(suffix):
            # This is a virtual file, look up the original file's abs_src_path
            abs_src_path = self._virtual_files.get(src_path)
            if abs_src_path and os.path.isfile(abs_src_path):
                try:
                    with open(abs_src_path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    log.error(f"RawMarkdownPlugin: error reading {abs_src_path}: {e}")
                    return ""
            # Fallback: virtual file but abs_src_path not on disk — return empty
            # rather than trying to guess paths that won't match multirepo temp dirs.
            return ""
        return None
