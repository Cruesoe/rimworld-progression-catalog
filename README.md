# RimWorld Progression collections catalog

Searchable, filterable list of workshop items from:

- [The Progression Modpack [1.6]](https://steamcommunity.com/workshop/filedetails/?id=3521297585) (1/3 Core)
- [The Progression Content (2/3)](https://steamcommunity.com/workshop/filedetails/?id=3521319712)
- [The Progression Cosmetics (3/3)](https://steamcommunity.com/sharedfiles/filedetails/?id=3637541646)

**Steam snapshot date: 9 September 2026 (Europe/London)**

**packageId from RimSort steamDB: 1015 of 1474**

**Known packageIds (RimSort + previous overlay): 1469 of 1474**

**Unique mods: 1474** — Core 860 · Content 424 · Cosmetics 190 (3 collection pages omitted from the item list)

This is an unofficial helper, not an official Progression site. Categories are inferred from titles and which collection an item sits in.

## This snapshot vs previous catalog

Added (3):

- StarFix - Continued — 3798550797 (1/3 Core)
- Better Vomit - Continued — 3798550391 (1/3 Core)
- Skunks - Continued — 3798549519 (2/3 Content)

Removed: none

Renamed (still available): none

Now listed as unavailable (14): already-deleted workshop files now titled `(unavailable {id})` per catalog rules. Predecessor pages for the three new Continued mods are among them.

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

- Steam Web API snapshot 2026-09-09 (Europe/London)
- packageId from RimSort steamDB.json; existing overlay/catalog packageIds kept when RimSort has no row
- New workshop IDs without a RimSort row are left blank (packageId unknown)
- Did not download workshop mods via SteamCMD
