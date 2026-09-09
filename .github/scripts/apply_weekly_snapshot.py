#!/usr/bin/env python3
"""Apply the 2026-09-09 Steam snapshot onto index.html and regenerate backups."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "index.html"
CSV_PATH = ROOT / "backup/progression_packageids.csv"
TXT_PATH = ROOT / "backup/progression_collections_categorized.txt"
MODPACK_PATH = ROOT / "backup/progression_modpack_mods.txt"

SNAPSHOT_LABEL = "9 September 2026 (Europe/London)"
SNAPSHOT_ISO = "2026-09-09"
STEAMDB_HITS = 1015
KNOWN_PKG = 1469

ADDED = [
    {
        "t": "StarFix - Continued",
        "c": "Gameplay tweaks",
        "core": True,
        "content": False,
        "cosmetics": False,
        "id": "3798550797",
        "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3798550797",
        "p": "",
    },
    {
        "t": "Better Vomit - Continued",
        "c": "Medical, needs & hygiene",
        "core": True,
        "content": False,
        "cosmetics": False,
        "id": "3798550391",
        "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3798550391",
        "p": "",
    },
    {
        "t": "Skunks - Continued",
        "c": "Animals",
        "core": False,
        "content": True,
        "cosmetics": False,
        "id": "3798549519",
        "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3798549519",
        "p": "",
    },
]

UNAVAILABLE_IDS = [
    "2164584341",
    "2768240773",
    "2792624577",
    "2920418046",
    "3015087560",
    "3226502149",
    "3309016770",
    "3626568203",
    "3626568306",
    "3628433732",
    "3680510302",
    "3712465624",
    "3775906812",
    "3778487830",
]


def load_data(html: str) -> tuple[dict, int, int]:
    m = re.search(r"const DATA = (\{.*?\});\s*\n", html, re.S)
    if not m:
        raise SystemExit("DATA block not found")
    return json.loads(m.group(1)), m.start(), m.end()


def apply_items(data: dict) -> dict:
    by_id = {str(it["id"]): it for it in data["items"]}
    for pid in UNAVAILABLE_IDS:
        it = by_id.get(pid)
        if not it:
            continue
        it["t"] = f"(unavailable {pid})"
        it["gone"] = True
    for it in ADDED:
        if it["id"] not in by_id:
            data["items"].append(dict(it))
            by_id[it["id"]] = data["items"][-1]
    groups: dict[str, list] = {c: [] for c in data["cats"]}
    extra: list = []
    for it in data["items"]:
        if it["c"] in groups:
            groups[it["c"]].append(it)
        else:
            extra.append(it)
    data["items"] = [it for c in data["cats"] for it in groups[c]] + extra
    return data


def update_html(html: str, data: dict) -> str:
    total = len(data["items"])
    html = re.sub(
        r'<div class="updated">.*?</div>',
        f'<div class="updated">Steam snapshot: <time datetime="{SNAPSHOT_ISO}">{SNAPSHOT_LABEL}</time></div>',
        html,
        count=1,
        flags=re.S,
    )
    footer_old = re.search(r"<footer>.*?</footer>", html, re.S)
    if footer_old:
        footer = """<footer>
  Sources:
  <a href="https://steamcommunity.com/workshop/filedetails/?id=3521297585">The Progression Modpack [1.6]</a> ·
  <a href="https://steamcommunity.com/workshop/filedetails/?id=3521319712">The Progression Content (2/3)</a> ·
  <a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3637541646">The Progression Cosmetics (3/3)</a>.
  Unofficial helper — not an official Progression site.
  Categories are a best-effort grouping from titles (revised 8 September 2026); search is the reliable way to check if a mod is in the pack.
  Steam snapshot: 9 September 2026 (Europe/London).
  packageId from RimSort steamDB: %s of %s.
  Known packageIds (RimSort + previous overlay): %s of %s.
</footer>""" % (STEAMDB_HITS, total, KNOWN_PKG, total)
        html = html[: footer_old.start()] + footer + html[footer_old.end() :]
    data_line = "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    html = re.sub(r"const DATA = \{.*?\};\s*\n", data_line, html, count=1, flags=re.S)
    return html


def write_csv(data: dict) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(
            [
                "title",
                "workshop_id",
                "packageId",
                "collection_core",
                "collection_content",
                "collection_cosmetics",
                "category",
                "steam_url",
            ]
        )
        for it in sorted(data["items"], key=lambda x: (x["t"].lower(), x["id"])):
            w.writerow(
                [
                    it["t"],
                    it["id"],
                    it.get("p", ""),
                    int(bool(it["core"])),
                    int(bool(it["content"])),
                    int(bool(it["cosmetics"])),
                    it["c"],
                    it["u"],
                ]
            )


def write_txt(data: dict) -> None:
    lines = [
        "The Progression — categorized catalog",
        f"Steam snapshot: {SNAPSHOT_LABEL}",
        "Categories revised: 8 September 2026",
        "",
    ]
    for c in data["cats"]:
        arr = [it for it in data["items"] if it["c"] == c]
        if not arr:
            continue
        lines.append("=" * 72)
        lines.append(f"{c}  ({len(arr)})")
        lines.append("=" * 72)
        for it in arr:
            tags = []
            if it["core"]:
                tags.append("1/3 Core")
            if it["content"]:
                tags.append("2/3 Content")
            if it["cosmetics"]:
                tags.append("3/3 Cosmetics")
            extra = "  [unavailable]" if it.get("gone") else ""
            lines.append(f"  - {it['t']}{extra}")
            lines.append(f"    [{' · '.join(tags)}]  {it['u']}")
        lines.append("")
    TXT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_modpack(data: dict) -> None:
    core = [it for it in data["items"] if it["core"]]
    lines = [
        "The Progression Modpack [1.6]",
        "https://steamcommunity.com/workshop/filedetails/?id=3521297585",
        f"Total items: {len(core)}",
        "",
    ]
    for n, it in enumerate(core, 1):
        lines.append(f"   {n}. {it['t']}")
        lines.append(f"     {it['u']}")
    MODPACK_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_xlsx(data: dict) -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        print("openpyxl missing; skip xlsx")
        return

    items = data["items"]
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    head_font = Font(name="Arial", bold=True, size=11, color="E8F5EF")
    body_font = Font(name="Arial", size=10)
    header_fill = PatternFill("solid", fgColor="1B3A2E")
    ws["A1"] = "The Progression collections — categorized workshop list"
    ws["A1"].font = Font(name="Arial", bold=True, size=14)
    ws.merge_cells("A1:D1")
    ws["A2"] = (
        "Source: Steam ISteamRemoteStorage GetCollectionDetails + GetPublishedFileDetails. "
        "Unofficial helper; not an official Progression site. Collection pages omitted."
    )
    ws.merge_cells("A2:D2")
    ws["A2"].alignment = Alignment(wrap_text=True)
    ws["A3"] = f"Steam snapshot: {SNAPSHOT_LABEL}"
    ws["A4"] = (
        f"Unique mods: {len(items)}   packageId from RimSort steamDB: {STEAMDB_HITS} of {len(items)}   "
        f"known packageIds: {KNOWN_PKG} of {len(items)}"
    )
    ws["A6"] = "Collection"
    ws["B6"] = "Workshop ID"
    ws["C6"] = "Steam page"
    ws["D6"] = "Items in collection"
    for col in range(1, 5):
        ws.cell(6, col).font = head_font
        ws.cell(6, col).fill = header_fill
    rows = [
        (
            "1/3 Core pack — The Progression Modpack [1.6]",
            "3521297585",
            "https://steamcommunity.com/workshop/filedetails/?id=3521297585",
            sum(1 for i in items if i["core"]),
        ),
        (
            "2/3 Content — The Progression Content",
            "3521319712",
            "https://steamcommunity.com/workshop/filedetails/?id=3521319712",
            sum(1 for i in items if i["content"]),
        ),
        (
            "3/3 Cosmetics — The Progression Cosmetics",
            "3637541646",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=3637541646",
            sum(1 for i in items if i["cosmetics"]),
        ),
    ]
    for i, row in enumerate(rows, 7):
        for j, val in enumerate(row, 1):
            cell = ws.cell(i, j, val)
            cell.font = body_font
    ws["A11"] = "Category"
    ws["B11"] = "Count"
    ws["A11"].font = head_font
    ws["B11"].font = head_font
    ws["A11"].fill = header_fill
    ws["B11"].fill = header_fill
    r = 12
    for c in data["cats"]:
        ws.cell(r, 1, c).font = body_font
        ws.cell(r, 2, sum(1 for i in items if i["c"] == c)).font = body_font
        r += 1
    ws.cell(r, 1, "Unique total").font = Font(name="Arial", bold=True)
    ws.cell(r, 2, len(items)).font = Font(name="Arial", bold=True)
    ws.column_dimensions["A"].width = 62
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 70
    ws.column_dimensions["D"].width = 22

    ws2 = wb.create_sheet("All mods")
    headers2 = [
        "Category",
        "Mod title",
        "Collections",
        "Core 1/3",
        "Content 2/3",
        "Cosmetics 3/3",
        "Workshop ID",
        "Steam URL",
        "packageId",
        "Unavailable",
    ]
    ws2.append(headers2)
    for col in range(1, len(headers2) + 1):
        cell = ws2.cell(1, col)
        cell.font = head_font
        cell.fill = header_fill
    for it in items:
        tags = []
        if it["core"]:
            tags.append("1/3 Core pack")
        if it["content"]:
            tags.append("2/3 Content")
        if it["cosmetics"]:
            tags.append("3/3 Cosmetics")
        ws2.append(
            [
                it["c"],
                it["t"],
                " · ".join(tags),
                "Yes" if it["core"] else None,
                "Yes" if it["content"] else None,
                "Yes" if it["cosmetics"] else None,
                it["id"],
                it["u"],
                it.get("p") or None,
                "Yes" if it.get("gone") else None,
            ]
        )
    for col, width in enumerate([36, 55, 28, 12, 14, 16, 16, 62, 36, 14], 1):
        ws2.column_dimensions[get_column_letter(col)].width = width
    ws2.auto_filter.ref = f"A1:J{ws2.max_row}"
    ws2.freeze_panes = "A2"

    ws3 = wb.create_sheet("Grouped list")
    ws3["A1"] = "Mods grouped by category"
    ws3["A1"].font = Font(name="Arial", bold=True, size=14)
    ws3.append(["Title", "Collection(s)", "Workshop ID", "URL"])
    for col in range(1, 5):
        ws3.cell(2, col).font = head_font
        ws3.cell(2, col).fill = header_fill
    for c in data["cats"]:
        arr = [it for it in items if it["c"] == c]
        if not arr:
            continue
        ws3.append([f"{c}  ({len(arr)})", None, None, None])
        ws3.cell(ws3.max_row, 1).font = Font(name="Arial", bold=True, size=11)
        for it in arr:
            tags = []
            if it["core"]:
                tags.append("1/3 Core pack")
            if it["content"]:
                tags.append("2/3 Content")
            if it["cosmetics"]:
                tags.append("3/3 Cosmetics")
            ws3.append([it["t"], " · ".join(tags), it["id"], it["u"]])
    ws3.column_dimensions["A"].width = 62
    ws3.column_dimensions["B"].width = 28
    ws3.column_dimensions["C"].width = 16
    ws3.column_dimensions["D"].width = 70
    out = ROOT / "backup/progression_collections_categorized.xlsx"
    wb.save(out)
    print("wrote", out)


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    data, _, _ = load_data(html)
    data = apply_items(data)
    HTML.write_text(update_html(html, data), encoding="utf-8")
    write_csv(data)
    write_txt(data)
    write_modpack(data)
    write_xlsx(data)
    counts = Counter()
    for it in data["items"]:
        if it["core"]:
            counts["core"] += 1
        if it["content"]:
            counts["content"] += 1
        if it["cosmetics"]:
            counts["cosmetics"] += 1
    print(
        f"applied snapshot {SNAPSHOT_ISO}: {len(data['items'])} unique "
        f"(core {counts['core']}, content {counts['content']}, cosmetics {counts['cosmetics']})"
    )


if __name__ == "__main__":
    main()
