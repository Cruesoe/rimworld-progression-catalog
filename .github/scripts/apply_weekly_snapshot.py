#!/usr/bin/env python3
"""Apply the 2026-09-13 Steam snapshot onto index.html and regenerate backups."""
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
README = ROOT / "README.md"

SNAPSHOT_LABEL = "13 September 2026 (Europe/London)"
SNAPSHOT_ISO = "2026-09-13"
STEAMDB_HITS = 1012
KNOWN_PKG = 1464

ADDED = [
    {"t": "Faster Game Loading - Continued", "c": "Performance & tools", "core": True, "content": False, "cosmetics": False, "id": "3652938473", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3652938473", "p": ""},
    {"t": "Psycasts²", "c": "Vanilla Expanded", "core": True, "content": False, "cosmetics": False, "id": "3761869362", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3761869362", "p": ""},
    {"t": "Gravship Fleet", "c": "Vehicles, gravships & mechs", "core": True, "content": False, "cosmetics": False, "id": "3787239201", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3787239201", "p": ""},
    {"t": "[DR] Build Outline（占地描边）", "c": "UI & information", "core": True, "content": False, "cosmetics": False, "id": "3796610291", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3796610291", "p": ""},
    {"t": "Progression: Arsenal", "c": "Research, storytellers & progression", "core": True, "content": False, "cosmetics": False, "id": "3798837810", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3798837810", "p": ""},
    {"t": "Progression: Ammunition", "c": "Research, storytellers & progression", "core": True, "content": False, "cosmetics": False, "id": "3798845290", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3798845290", "p": ""},
    {"t": "Female Apparel Variants Continued", "c": "Apparel, styles & cosmetics", "core": True, "content": False, "cosmetics": False, "id": "3799726535", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3799726535", "p": ""},
    {"t": "Vanilla Gravship Expanded - Chapter 2", "c": "Vanilla Expanded", "core": True, "content": False, "cosmetics": False, "id": "3799737423", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3799737423", "p": ""},
    {"t": "Photo Mode", "c": "UI & information", "core": False, "content": False, "cosmetics": True, "id": "3799924005", "u": "https://steamcommunity.com/sharedfiles/filedetails/?id=3799924005", "p": ""},
]
REMOVED_IDS = ["3234422589", "3422293321", "3511966169", "3699245205", "3787398983"]
RENAMES = {
    "3654021202": "Fluffy Breakdowns Continued",
    "3786620127": "Gas Giant",
}
UNAVAILABLE_IDS = [
    "2164584341", "2768240773", "2792624577", "2920418046", "3015087560",
    "3226502149", "3309016770", "3626568203", "3626568306", "3628433732",
    "3680510302", "3712465624", "3775906812", "3778487830",
    "3798549519", "3798550391", "3798550797",
]


def load_data(html: str) -> dict:
    m = re.search(r"const DATA = (\{.*?\});\s*\n", html, re.S)
    if not m:
        raise SystemExit("DATA block not found")
    return json.loads(m.group(1))


def apply_items(data: dict) -> dict:
    by_id = {str(it["id"]): it for it in data["items"]}
    for pid in REMOVED_IDS:
        if pid in by_id:
            data["items"] = [it for it in data["items"] if str(it["id"]) != pid]
            by_id.pop(pid, None)
    for pid, title in RENAMES.items():
        if pid in by_id:
            by_id[pid]["t"] = title
            by_id[pid].pop("gone", None)
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
    groups = {c: [] for c in data["cats"]}
    extra = []
    for it in data["items"]:
        (groups[it["c"]] if it["c"] in groups else extra).append(it)
    data["items"] = [it for c in data["cats"] for it in groups[c]] + extra
    return data


def update_html(html: str, data: dict) -> str:
    total = len(data["items"])
    html = re.sub(
        r'<div class="updated">.*?</div>',
        f'<div class="updated">Steam snapshot: <time datetime="{SNAPSHOT_ISO}">{SNAPSHOT_LABEL}</time></div>',
        html, count=1, flags=re.S,
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
  Steam snapshot: 13 September 2026 (Europe/London).
  packageId from RimSort steamDB: %s of %s.
  Known packageIds (RimSort + previous overlay): %s of %s.
</footer>""" % (STEAMDB_HITS, total, KNOWN_PKG, total)
        html = html[: footer_old.start()] + footer + html[footer_old.end() :]
    data_line = "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    html = re.sub(r"const DATA = \{.*?\};\s*\n", data_line, html, count=1, flags=re.S)
    return html


def write_csv(data: dict) -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["title","workshop_id","packageId","collection_core","collection_content","collection_cosmetics","category","steam_url"])
        for it in sorted(data["items"], key=lambda x: (x["t"].lower(), x["id"])):
            w.writerow([it["t"], it["id"], it.get("p", ""), int(bool(it["core"])), int(bool(it["content"])), int(bool(it["cosmetics"])), it["c"], it["u"]])


def write_txt(data: dict) -> None:
    lines = ["The Progression — categorized catalog", f"Steam snapshot: {SNAPSHOT_LABEL}", "Categories revised: 8 September 2026", ""]
    for c in data["cats"]:
        arr = [it for it in data["items"] if it["c"] == c]
        if not arr:
            continue
        lines += ["=" * 72, f"{c}  ({len(arr)})", "=" * 72]
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
    lines = ["The Progression Modpack [1.6]", "https://steamcommunity.com/workshop/filedetails/?id=3521297585", f"Total items: {len(core)}", ""]
    for n, it in enumerate(core, 1):
        lines += [f"   {n}. {it['t']}", f"     {it['u']}"]
    MODPACK_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_xlsx(data: dict) -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        print("openpyxl missing; skip xlsx")
        return
    items = data["items"]
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    head = Font(name="Arial", bold=True, size=11, color="E8F5EF")
    fill = PatternFill("solid", fgColor="1B3A2E")
    ws["A1"] = "The Progression collections — categorized workshop list"
    ws["A3"] = f"Steam snapshot: {SNAPSHOT_LABEL}"
    ws["A4"] = f"Unique mods: {len(items)}   packageId from RimSort steamDB: {STEAMDB_HITS} of {len(items)}   known packageIds: {KNOWN_PKG} of {len(items)}"
    ws2 = wb.create_sheet("All mods")
    ws2.append(["Category","Mod title","Collections","Core 1/3","Content 2/3","Cosmetics 3/3","Workshop ID","Steam URL","packageId","Unavailable"])
    for col in range(1, 11):
        ws2.cell(1, col).font = head
        ws2.cell(1, col).fill = fill
    for it in items:
        tags = []
        if it["core"]:
            tags.append("1/3 Core pack")
        if it["content"]:
            tags.append("2/3 Content")
        if it["cosmetics"]:
            tags.append("3/3 Cosmetics")
        ws2.append([it["c"], it["t"], " · ".join(tags), "Yes" if it["core"] else None, "Yes" if it["content"] else None, "Yes" if it["cosmetics"] else None, it["id"], it["u"], it.get("p") or None, "Yes" if it.get("gone") else None])
    for col, width in enumerate([36, 55, 28, 12, 14, 16, 16, 62, 36, 14], 1):
        ws2.column_dimensions[get_column_letter(col)].width = width
    wb.save(ROOT / "backup/progression_collections_categorized.xlsx")
    print("wrote xlsx")


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    data = apply_items(load_data(html))
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
    print(f"applied snapshot {SNAPSHOT_ISO}: {len(data['items'])} unique (core {counts['core']}, content {counts['content']}, cosmetics {counts['cosmetics']})")


if __name__ == "__main__":
    main()
