# RimWorld Progression collections catalog

Searchable, filterable list of workshop items from:

- [The Progression Modpack [1.6]](https://steamcommunity.com/workshop/filedetails/?id=3521297585) (1/3 Core)
- [The Progression Content (2/3)](https://steamcommunity.com/workshop/filedetails/?id=3521319712)
- [The Progression Cosmetics (3/3)](https://steamcommunity.com/sharedfiles/filedetails/?id=3637541646)

[Site patch notes](CHANGELOG.md)

**Steam snapshot date: 11 October 2026**

**packageId from RimSort steamDB: 1012 of 1493**

**Known packageIds (RimSort + previous overlay): 1457 of 1493**

**Unique mods: 1493** — Core 870 · Content 430 · Cosmetics 193 (3 collection pages omitted from the item list)

This is an unofficial helper, not an official Progression site. Categories are inferred from titles and which collection an item sits in.

## This snapshot vs previous catalog

### Added (5)
- Door Direction (One-Way Doors, Mod Doors Supported) — 3814657467
- Jettison Corpses — 3816431081
- VPE Shrunk Psycast Tooltip Fix — 3795310579
- Custom Base Framework — 3813689040
- Shipcracker Warcasket — 3814428597

### Removed (1)
- Vanilla Base Generation Expanded — 3209927822

### Renamed (1)
- Helpful Raccoons | Fork by [ETF] → Helpful Raccoons [Forked] — 3457315303

### Newly unavailable (0)
- None

## Open the catalog

- Live site (GitHub Pages): https://cruesoe.github.io/rimworld-progression-catalog/
- Or open `index.html` from this repo.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Searchable catalog |
| `backup/progression_collections_categorized.xlsx` | Spreadsheet backup |
| `backup/progression_collections_categorized.txt` | Plain-text grouped list |
| `backup/progression_modpack_mods.txt` | Core pack numbered list |
| `backup/progression_packageids.csv` | Title / workshop ID / packageId table |

## Enable GitHub Pages (if the live URL 404s)

Repo **Settings → Pages → Build and deployment**

- Source: **Deploy from a branch**
- Branch: `main` / `/ (root)`

## Snapshot notes

- Steam Web API snapshot 2026-09-13
- packageId from RimSort steamDB.json; existing overlay/catalog packageIds kept when RimSort has no row
- New workshop IDs without a RimSort row are left blank (packageId unknown)
- Did not download workshop mods via SteamCMD
