"""
MkDocs hook: makes nav sections clickable by giving each one an index page.

Top-level sections become clickable via the terminal theme's
`navigation.side.indexes` feature: an "Index" child page is injected.
Nested sections are flattened into leaf entries that link to an
auto-generated index listing their original children.

If a section already has a bare-path child pointing to an existing file,
that file is used as the section's Index instead of an auto-generated
listing — so hand-written pages like `gear/index.md` are honored.
"""

import os
from pathlib import Path
from mkdocs.structure.files import File


INDEX_TITLE = "Index"
GEN_DIR = "_categories"

_GENERATED: dict[str, str] = {}


def _slug(s: str) -> str:
    return s.lower().replace(" ", "-").replace("/", "-").replace("_", "-")


def _existing_index(children: list, docs_dir: Path) -> str | None:
    for child in children:
        if isinstance(child, str) and (docs_dir / child).exists():
            return child
    return None


def _render_listing(title: str, entries: list[tuple[str, str]], from_path: str) -> str:
    from_dir = os.path.dirname(from_path)
    lines = [f"# {title}", ""]
    for c_title, c_url in entries:
        rel = os.path.relpath(c_url, from_dir) if from_dir else c_url
        lines.append(f"- [{c_title}]({rel})")
    return "\n".join(lines) + "\n"


def on_config(config):
    _GENERATED.clear()
    docs_dir = Path(config["docs_dir"])

    def transform_top(items):
        new_items = []
        for item in items:
            if isinstance(item, dict):
                title, value = next(iter(item.items()))
                if isinstance(value, list):
                    new_items.append({title: _process_top_section(title, value, docs_dir)})
                    continue
            new_items.append(item)
        return new_items

    config["nav"] = transform_top(config.get("nav", []) or [])
    return config


def _process_top_section(title: str, value: list, docs_dir: Path) -> list:
    slug = _slug(title)
    user_index = _existing_index(value, docs_dir)
    top_index_path = user_index or f"{GEN_DIR}/{slug}.md"

    new_children = []
    listing: list[tuple[str, str]] = []

    for child in value:
        if isinstance(child, str):
            continue  # bare path is handled by user_index detection
        if not isinstance(child, dict):
            continue
        c_title, c_val = next(iter(child.items()))

        if isinstance(c_val, list):
            sub_slug = f"{slug}-{_slug(c_title)}"
            sub_user_index = _existing_index(c_val, docs_dir)
            sub_index_path = sub_user_index or f"{GEN_DIR}/{sub_slug}.md"

            if not sub_user_index:
                sub_listing = []
                for sub_child in c_val:
                    if isinstance(sub_child, dict):
                        sc_title, sc_val = next(iter(sub_child.items()))
                        if isinstance(sc_val, str):
                            sub_listing.append((sc_title, sc_val))
                _GENERATED[sub_index_path] = _render_listing(c_title, sub_listing, sub_index_path)

            new_children.append({c_title: sub_index_path})
            listing.append((c_title, sub_index_path))

        elif isinstance(c_val, str):
            new_children.append({c_title: c_val})
            listing.append((c_title, c_val))

    if not user_index:
        _GENERATED[top_index_path] = _render_listing(title, listing, top_index_path)

    return [{INDEX_TITLE: top_index_path}] + new_children


def on_files(files, config):
    for src_path, content in _GENERATED.items():
        files.append(File.generated(config, src_path, content=content))
    return files
