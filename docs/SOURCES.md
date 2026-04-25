# Sources & provenance

## Ground truth

**Printed Muhammadi mushaf** — المصحف المحمدي, published by the Ministry of Habous and Islamic Affairs of the Kingdom of Morocco. Digital page images at [mushaf.ma](https://mushaf.ma/fahres/page/images/muhammadi/).

- 638 PNG pages (p3–p640 of the printed edition) → `raw/muhammadi-pages/`
- Downloaded 2026-04-21 via `scripts/fetch_pages.py`

Every one of the 480 eighth boundaries in `data/eighths.json` was cross-checked against its corresponding page image.

---

## Text candidates (merged)

### Source A — Al-Lawh Almahfoudh (اللوح المحفوظ)

- Android app distributed in Morocco, contains a verse-level Warsh text honoring Maghrebi numbering.
- Text extracted from the APK's `assets/coran.txt` (plain encoded).
- Parsed to `raw/lawh_verses.json` (6,214 entries).
- **Known issue:** 435 verses (~7%) are incorrectly split at ۞ markers — i.e. the text *up to* a ۞ is stored as one verse and the text *after* ۞ as another. This was identified during merge and corrected by always preferring Mauri for these cases.

### Source B — Zizwar/mushaf-mauri (MIT)

- Open-source web mushaf project: [github.com/zizwar/mushaf-mauri](https://github.com/zizwar/mushaf-mauri)
- Vocalized Warsh text in `src/data/textWarsh.js`, Muhammadi pagination in `src/data/indexMuhammadi.js`.
- Parsed to `raw/mauri_verses.json` (6,214 entries with full tashkil).
- Used as the **primary text source** after majority merge.
- 477 `۞` markers preserved at their exact positions (can appear mid-verse).
- Licensed MIT — redistributed here under our CC-BY-4.0 data license with attribution.

---

## Merge rules (`scripts/majority_merge.py`)

| Rule | Cases | Decision |
|---|---|---|
| Both sources agree on vocalized text | 6,209 | Use Mauri (richer, has ۞ markers) |
| Mauri has Basmala bundled into aya 1 | 112 | Strip Basmala, use result |
| Lawh has underscore artifact (58:13) | 1 | Use Mauri |
| Spelling variants `النبيين` / `النبين` | 4 | Prefer Lawh (standard spelling) |
| Lawh truncated verse at ۞ marker | 13 | Use Mauri (Lawh is wrong) |

Full decision log in `reports/divergences.md`.

**Result:** 6,214 verses, 0 flagged for manual review.

---

## Eighth boundaries (`scripts/build_eighths_final.py` + `build_eighths_ranges.py`)

- 477 `۞` markers extracted from Mauri text.
- 3 implicit boundaries added:
  1. Sura 1:1 at offset 0 — start of Al-Fatiha (no printed ۞ at surah opening)
  2. Sura 75:1 — Al-Qiyamah surah header
  3. Sura 76:1 — Al-Insan surah header
- Total: **480 eighths** (60 hizbs × 8), matching the canonical count.
- Word-count gap analysis confirmed the 3 missing markers are exactly at surah boundaries (545-word gap between 74:31 and 76:19 vs expected ~175).

Inclusive `start`/`end` ranges are computed so that consecutive eighths tile the Quran with no gaps and no overlaps:
- If eighth N+1 starts at `aya:1 offset:0`, eighth N ends at the last char of the preceding verse.
- Otherwise eighth N ends at `(next_start_offset - 1)` in the same verse.

---

## Audio reciters (`data/audio_sources.json`)

Sourced from public mp3quran.net API v3 (`language=ar`), filtered for `ورش عن نافع` riwaya. All 16 per-surah reciters verified via HTTP range request on 2026-04-21 — all return HTTP 206.

Per-surah audio (`{server}/{001..114}.mp3`) is fully aligned with the Moroccan numbering used by this dataset.

---

## Licensing summary

| Asset | License | Source |
|---|---|---|
| Text (`data/quran_muhammadi.json`, `data/text_simple`) | CC-BY-4.0 | Compiled from Lawh + Mauri (MIT) |
| Eighth boundaries | CC-BY-4.0 | Extracted from Mauri ۞ markers |
| Metadata (surahs/hizbs/juzs) | CC-BY-4.0 | Derived |
| Audio URLs (`audio_sources.json`) | CC-BY-4.0 (catalog) | mp3quran.net + everyayah.com (audio files themselves remain property of their reciters/publishers) |
| Page images (`raw/muhammadi-pages/`) | © Ministry of Habous | Distributed for educational use |
| Python/HTML code | MIT | Original |
