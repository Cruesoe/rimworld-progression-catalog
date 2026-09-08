#!/usr/bin/env python3
"""Merge backup/packageids_overlay.json into index.html, CSV, and README."""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "backup/packageids_overlay.json"
HTML = ROOT / "index.html"
CSV_PATH = ROOT / "backup/progression_packageids.csv"
README = ROOT / "README.md"


def main() -> None:
    mapping = {str(k): str(v) for k, v in json.loads(OVERLAY.read_text()).items() if v}
    text = HTML.read_text(encoding="utf-8")
    lines = text.splitlines()
    data_idx = next(i for i, l in enumerate(lines) if l.startswith("const DATA = "))
    raw = lines[data_idx][len("const DATA = ") :].rstrip(";")
    data = json.loads(raw)
    for it in data["items"]:
        if it.get("p"):
            continue
        pid = mapping.get(str(it["id"]))
        if pid:
            it["p"] = pid
    have = sum(1 for it in data["items"] if it.get("p"))
    total = len(data["items"])
    lines[data_idx] = "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
    new_text = "\n".join(lines) + "\n"
    if re.search(r"\(\d+ of \d+\)", new_text):
        new_text = re.sub(r"\(\d+ of \d+\)", f"({have} of {total})", new_text, count=1)
    HTML.write_text(new_text, encoding="utf-8")

    if CSV_PATH.exists():
        with CSV_PATH.open(encoding="utf-8", newline="") as f:
            header = next(csv.reader(f))
        with CSV_PATH.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            wid = str(row.get("workshop_id", "")).strip()
            if not (row.get("packageId") or "").strip() and wid in mapping:
                row["packageId"] = mapping[wid]
        with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)

    if README.exists():
        rtxt = README.read_text(encoding="utf-8")
        cov = f"**packageId coverage: {have} of {total}**"
        if re.search(r"\*\*packageId coverage:", rtxt):
            rtxt = re.sub(r"\*\*packageId coverage:.*", cov, rtxt, count=1)
        else:
            rtxt = re.sub(
                r"(\*\*Steam snapshot date: [^\n]+\*\*\n)",
                r"\1\n" + cov + "\n",
                rtxt,
                count=1,
            )
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        note = f"- packageIds filled {day} Europe/London"
        if "packageIds filled" in rtxt:
            rtxt = re.sub(r"- packageIds filled.*", note, rtxt, count=1)
        else:
            rtxt = rtxt.rstrip() + "\n\n## Snapshot notes\n\n" + note + "\n"
        README.write_text(rtxt, encoding="utf-8")
    print(f"merged {len(mapping)} overlay ids -> {have}/{total}")


if __name__ == "__main__":
    main()
