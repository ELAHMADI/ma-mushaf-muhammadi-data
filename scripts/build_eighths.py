"""
Extract eighth (ثُمْن) boundaries from Mauri's ۞ markers in the Warsh text.

In the Moroccan Muhammadi mushaf:
- 60 hizb × 8 eighths = 480 total eighths (global ids 1..480)
- Each eighth boundary is marked in the printed mushaf by a ۞ symbol
- ۞ can appear at the start of a verse OR mid-verse (after N characters)
- The first eighth of Fatiha and some hizb starts may not have an inline ۞
  (implied by hizb margin marker instead)

This script:
  1. Scans Mauri's textWarsh.js for every ۞ marker
  2. Records (sura, aya, char_offset_in_verse) for each
  3. Compares count to 480, fills gaps using quarter-boundary data from
     mushaf-mauri's QuranData.HizbQuarter (240 quarter boundaries =
     4 per hizb × 60 hizbs) + known first-eighth rules
  4. Writes build/eighths.json with 480 entries

Output format:
  [
    { "eighth_id": 1, "hizb": 1, "pos_in_hizb": 1,
      "sura": 1, "aya": 1, "char_offset": 0 },
    ...
    { "eighth_id": 480, "hizb": 60, "pos_in_hizb": 8,
      "sura": 114, "aya": 1, "char_offset": 0 }
  ]
"""
import io, os, sys, json, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'raw')
BUILD = os.path.join(ROOT, 'build')
os.makedirs(BUILD, exist_ok=True)

mauri = json.load(open(os.path.join(RAW, 'mauri_verses.json'), encoding='utf-8'))

# Step 1: find every ۞ marker in every verse
markers = []  # list of {sura, aya, char_offset, text_before, text_after}
for v in mauri:
    text = v['text_vocalized']
    for m in re.finditer('۞', text):
        off = m.start()
        markers.append({
            'sura': v['sura_idx'],
            'aya': v['aya'],
            'char_offset': off,
            'at_verse_start': off == 0 or text[:off].strip() == '',
        })

print(f'Total ۞ markers found in Mauri: {len(markers)}')
# group by (sura, aya) to see if any verse has multiple
from collections import Counter
per_verse = Counter((m['sura'], m['aya']) for m in markers)
multi = {k: c for k, c in per_verse.items() if c > 1}
print(f'Verses with multiple markers: {len(multi)}')
for k, c in list(multi.items())[:5]:
    print(f'  {k}: {c} markers')

# Step 2: sort markers by Quranic order (sura, aya, char_offset)
def mauri_gid(v):
    return v['gid']
gid_map = {(v['sura_idx'], v['aya']): v['gid'] for v in mauri}

markers_sorted = sorted(markers, key=lambda m: (gid_map[(m['sura'], m['aya'])], m['char_offset']))

# Step 3: count expected
# Fatiha has no ۞ (Fatiha = 1st eighth of hizb 1, implied)
# Each hizb after that starts with an eighth, which may or may not have ۞ marker.
# 60 hizbs × 8 eighths = 480 total.
# If 477 markers: probably missing 3 (e.g. Fatiha + 2 others where hizb boundary = surah start)

# Use QuranData.Hizb (60 entries) as ground truth for hizb starts
# Extract from quranData.js

QURAN_DATA_JS = r'C:\Users\elahmano\AppData\Local\Temp\mushaf-mauri\src\data\quranData.js'
if not os.path.exists(QURAN_DATA_JS):
    print(f'ERROR: quranData.js not found at {QURAN_DATA_JS}')
    sys.exit(1)

with open(QURAN_DATA_JS, encoding='utf-8') as f:
    qd = f.read()

# Extract HizbQaurter [note: typo in source — "HizbQaurter"] — 240 quarter entries
m = re.search(r'QuranData\.HizbQaurter\s*=\s*\[(.*?)\n\];', qd, re.DOTALL)
if not m:
    print('Could not find HizbQaurter block')
    sys.exit(1)
block = m.group(1)
# entries like [1, 1]
quarter_entries = re.findall(r'\[\s*(\d+)\s*,\s*(\d+)\s*\]', block)
quarters = [(int(s), int(a)) for s, a in quarter_entries]
print(f'HizbQuarter entries: {len(quarters)}')

# Extract Juz data too (30 entries)
m = re.search(r'QuranData\.Juz\s*=\s*\[(.*?)\n\];', qd, re.DOTALL)
juz = []
if m:
    juz_entries = re.findall(r'\[\s*(\d+)\s*,\s*(\d+)\s*\]', m.group(1))
    juz = [(int(s), int(a)) for s, a in juz_entries]
print(f'Juz entries: {len(juz)}')

# Step 4: The HizbQuarter list (240) is at quarter boundaries (0, 1/4, 2/4, 3/4 of each hizb).
# We need eighth boundaries (0, 1/8, 2/8, ..., 7/8 of each hizb).
# Markers from Mauri: 477 ۞ markers — exactly between quarter boundaries.
# So total = 240 quarter boundaries + 477 eighth-only markers = 717 potential boundaries.
# But we only want 480 eighth boundaries TOTAL.
#
# Logic: in printed Muhammadi mushaf, the markers are:
#   - ۞ in text = Thumn (ربع الحزب / ثُمْن) = eighth boundary INSIDE text
#   - Hizb number in margin = START of a new hizb (= first eighth of that hizb)
#   - Rub' / Nisf / Thalatha Arba' in margin = quarter boundaries (visual)
#
# Actually let's verify: 477 ۞ + 60 hizb starts (implied) = 537, still not 480.
# OR: 477 ۞ are ALL 477 non-hizb-start eighths. Missing 3 of (480-60)=420? Math doesn't work.
#
# Let me look at this differently. 477 markers + how many gaps?

# Check: for each of the 60 hizb starts, is there a ۞ at (sura, aya, offset)=hizb_start?
# If yes, ۞ count = 480 - implicit = something.

# Collect marker (sura, aya) pairs
marker_keys = set((m['sura'], m['aya']) for m in markers)
print(f'Unique (sura,aya) with ۞ marker: {len(marker_keys)}')

# Print a few markers to inspect
print('\nFirst 10 markers:')
for m in markers_sorted[:10]:
    v = next(x for x in mauri if x['sura_idx']==m['sura'] and x['aya']==m['aya'])
    before = v['text_vocalized'][:m['char_offset']]
    after = v['text_vocalized'][m['char_offset']:m['char_offset']+40]
    print(f"  s{m['sura']}:a{m['aya']}  off={m['char_offset']}  start={m['at_verse_start']}")
    print(f"    before: ...{before[-30:]}")
    print(f"    after : {after}...")

# Save for inspection
with open(os.path.join(BUILD, 'markers_raw.json'), 'w', encoding='utf-8') as f:
    json.dump(markers_sorted, f, ensure_ascii=False)
print(f'\nSaved {len(markers_sorted)} markers to build/markers_raw.json')
