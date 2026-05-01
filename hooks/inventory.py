"""
MkDocs hook: replaces {{ inventory_eurorack }} and {{ inventory_gear }} in
inventory.md with markdown tables generated from data/modules.csv.
"""

import csv
from pathlib import Path


EURORACK_COLS = ["Module", "Brand", "Description", "Width", "Depth", "+12V (mA)", "-12V (mA)", "Owned"]
GEAR_COLS     = ["Module", "Brand", "Description", "Owned"]


def _md_table(rows: list[dict], cols: list[str]) -> str:
    header = "| " + " | ".join(cols) + " |"
    sep    = "| " + " | ".join("---" for _ in cols) + " |"
    lines  = [header, sep]
    for row in rows:
        cells = [row.get(c, "") for c in cols]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _load_csv(config) -> list[dict]:
    csv_path = Path(config["config_file_path"]).parent / "data" / "modules.csv"
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def on_page_markdown(markdown, page, config, files):
    if page.file.src_path != "inventory.md":
        return markdown

    rows = _load_csv(config)
    eurorack = [r for r in rows if r.get("Eurorack Module", "").strip() == "Yes"]
    gear     = [r for r in rows if r.get("Eurorack Module", "").strip() == "No"]

    markdown = markdown.replace("{{ inventory_eurorack }}", _md_table(eurorack, EURORACK_COLS))
    markdown = markdown.replace("{{ inventory_gear }}",     _md_table(gear,     GEAR_COLS))
    return markdown
