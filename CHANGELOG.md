# Changelog

All notable changes to this dataset will be documented here.
Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] — 2026-04-21

### Added — initial release

**Data**
- `data/quran_muhammadi.json` — 6,214 verses in Madani / Maghrebi numbering (Moroccan Muhammadi)
  - Fields: `text` (vocalized), `text_simple`, `sura`, `aya`, `gid`, `page_mushafma`, `page_mauri`, `word_count`, `char_count`, `hizb`, `juz`, `eighth_id`, `is_sajda`, `source_decision`
- `data/eighths.json` — 480 eighth boundaries (60 hizbs × 8)
  - Inclusive `start` and `end` with `partial_verse` flag for mid-verse cuts
  - `verses_covered`, `verse_count`, `word_count`, `name_ar`, `juz`, `is_surah_start`
- `data/surahs.json` — 114 surahs with Arabic name, transliteration, revelation (makki/madani), first/last eighth, first/last page
- `data/hizbs.json` — 60 hizbs with start/end, pages, word count
- `data/juzs.json` — 30 juzs aggregated
- `data/audio_sources.json` — 19 Warsh 'an Nafi' reciters (16 per-surah streams + 3 per-verse catalogs), verified 2026-04-21
- `data/VERSION.json` — dataset metadata
- `raw/muhammadi-pages/` — 638 printed mushaf.ma page PNGs
- `raw/lawh_verses.json`, `raw/mauri_verses.json` — candidate source texts

**Tooling**
- `scripts/fetch_pages.py` — downloads mushaf.ma page images
- `scripts/majority_merge.py` — merges Lawh + Mauri into authoritative text
- `scripts/build_eighths_final.py` — extracts 477 ۞ + 3 implicit boundaries
- `scripts/build_eighths_ranges.py` — computes inclusive start/end ranges
- `scripts/build_metadata.py` — builds surahs/hizbs/juzs + enriches verses & eighths
- `scripts/build_eighth_viewer.py` — generates HTML viewer for visual QA

**Documentation**
- `README.md` (ar + en), `docs/SCHEMA.md`, `docs/SOURCES.md`, `docs/SAJDA.md`

**Validation**
- 6,209 verses: both Lawh and Mauri agree
- 4 verses: spelling preference (use Lawh)
- 1 verse: Lawh artifact fix (use Mauri for 58:13)
- 0 verses: flagged / unresolved
- 11/11 sajda verses (Maliki / Maghreb tradition) verified at their Moroccan positions:
  7:206, 13:16, 16:50, 17:108, 19:58, 22:18, 25:60, 27:26, 32:15, 38:23, 41:36
- Sanity: 83,646 words total, 755,215 characters (Amiri vocalized)

### Stats

- Verses: 6,214
- Eighths: 480
- Hizbs: 60, Juzs: 30, Surahs: 114
- Pages: 638 (mushaf.ma p3–p640)
- Total size (data/ only): ~4.6 MB
