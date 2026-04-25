"""
Build the 480-entry eighth boundary index for the Moroccan Muhammadi mushaf.

Strategy:
  - Mauri has 477 ۞ markers in its Warsh text = almost all eighth boundaries.
  - Eighth 1 of Hizb 1 is implicitly at 1:1 (Fatiha start, no ۞).
  - Expected 480 - 1 (implicit Fatiha) = 479 ۞ markers.
  - We have 477, so 2 hizb-start markers are missing from Mauri data.
  - These are likely hizbs that start at a surah boundary (where the surah header replaces the marker).

We ORDER all markers by Quranic sequence then try to SEGMENT them into 60 hizbs of 8 eighths each.
The 60 hizb starts are a standard reference (same in Kufi and Moroccan numbering since they are
positional, not tied to verse counting).

Outputs:
  build/eighths.json  - [{eighth_id, hizb, pos_in_hizb, sura, aya, char_offset, text_preview}, ...]
  reports/eighths_report.md  - validation summary
"""
import io, os, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'raw')
BUILD = os.path.join(ROOT, 'build')
REPORTS = os.path.join(ROOT, 'reports')

mauri = json.load(open(os.path.join(RAW, 'mauri_verses.json'), encoding='utf-8'))
markers = json.load(open(os.path.join(BUILD, 'markers_raw.json'), encoding='utf-8'))

# Build gid map
gid_map = {(v['sura_idx'], v['aya']): v['gid'] for v in mauri}
verse_map = {(v['sura_idx'], v['aya']): v for v in mauri}

# Sort markers by (gid, char_offset)
def key(m):
    return (gid_map[(m['sura'], m['aya'])], m['char_offset'])
markers_sorted = sorted(markers, key=key)
print(f'Sorted {len(markers_sorted)} markers')

# Prepend the implicit Fatiha start
fatiha_start = {
    'sura': 1, 'aya': 1, 'char_offset': 0, 'at_verse_start': True,
    'implicit': True,
}

# Use standard hizb boundaries (fixed canonical positions).
# These are the 60 hizb starts in Moroccan numbering.
# Source: widely documented, confirmed with Mauri's HizbQaurter entries 1, 5, 9, ...
HIZB_STARTS_KUFI = [
    (1,1),    (2,75),   (2,142),  (2,203),  (2,253),  (3,15),   (3,93),   (3,171),
    (4,24),   (4,74),   (4,127),  (5,27),   (5,83),   (6,74),   (6,147),  (7,88),
    (7,171),  (8,41),   (9,34),   (9,94),   (10,26),  (10,72),  (11,41),  (11,108),
    (12,53),  (13,19),  (14,53),  (16,51),  (17,1),   (17,88),  (18,75),  (19,99),
    (21,29),  (22,19),  (23,36),  (24,22),  (25,55),  (26,181), (27,56),  (28,51),
    (29,46),  (31,22),  (33,31),  (34,24),  (36,28),  (37,145), (39,32),  (40,41),
    (41,47),  (43,24),  (45,37),  (47,20),  (51,31),  (54,9),   (57,16),  (59,11),
    (62,9),   (69,1),   (75,1),   (83,7),
]

# Kufi->Moroccan aya offset mapping for boundaries. For surahs where counts differ,
# we need to adjust. The boundaries are POSITIONAL (at specific Arabic words), so they
# fall at the same sentence. The verse number may shift if Moroccan merges some verses.

# Given Mauri uses Moroccan numbering AND appears to have markers at hizb-start positions,
# the simplest approach: find the SORTED marker closest to each Kufi hizb start and
# verify it's within 2 verses.

# First, compute per-hizb-start the nearest marker
# But safer: just accept Mauri's 477 markers + Fatiha, order them, and chunk into 8s per hizb.

# Total eighths expected: 480
# We have 477 ۞ + 1 implicit Fatiha = 478. Missing 2.
# The 2 missing = hizb starts that coincide with surah starts (where header replaces ۞).
#
# Looking at HIZB_STARTS_KUFI, boundaries like (17,1), (69,1), (75,1) are at surah starts.
# These are likely places where Mauri didn't put a ۞.

# Check: how many hizb starts are at verse 1 of a surah?
surah_start_hizbs = [(s,a) for s,a in HIZB_STARTS_KUFI if a == 1]
print(f'Hizb starts at surah:1 = {len(surah_start_hizbs)}')
for s,a in surah_start_hizbs:
    print(f'  surah {s} verse {a}')

# Check for each surah:1 hizb start whether Mauri has a marker there
marker_keys = set((m['sura'], m['aya']) for m in markers_sorted)
missing_at_surah_start = []
for s,a in surah_start_hizbs:
    if (s,a) not in marker_keys:
        missing_at_surah_start.append((s,a))
print(f'Surah-start hizbs without ۞: {len(missing_at_surah_start)}')
for s,a in missing_at_surah_start:
    print(f'  {s}:{a}')

# Expected math: 60 hizbs, 8 eighths each = 480
# Explicit ۞ in Mauri: 477
# Implicit at Fatiha 1:1 (hizb 1 eighth 1): 1
# Missing hizb starts at surah boundaries: ?
# We need explicit 479 ۞ total (fatiha is the only implicit one)
# 479 - 477 = 2 missing
# These 2 should be in missing_at_surah_start

# Now build the complete list
all_boundaries = [fatiha_start] + list(markers_sorted)
# Gap analysis shows 545-word gap between 74:31 and 76:19 = ~3 missing eighths
# (normal gap = 175 words). Mauri's text is missing 2 markers in sura 75/76.
# Best guess: surah starts (75:1, 76:1) coincide with eighth boundaries.
# User should verify visually against pages p606-p608.
IMPLICIT_BOUNDARIES = [
    (75, 1),   # Hizb 59 start (canonical) / surah Al-Qiyamah start
    (76, 1),   # Eighth 3 of hizb 59 area / surah Al-Insan start
]
for s, a in IMPLICIT_BOUNDARIES:
    all_boundaries.append({
        'sura': s, 'aya': a, 'char_offset': 0, 'at_verse_start': True,
        'implicit': True, 'reason': 'fills_large_gap_needs_visual_verify',
    })

# Resort
all_boundaries_sorted = sorted(all_boundaries, key=key)
print(f'\nTotal boundaries: {len(all_boundaries_sorted)} (expected 480)')

# Validate: exactly 480?
if len(all_boundaries_sorted) != 480:
    print(f'  WARNING: count mismatch. Expected 480, got {len(all_boundaries_sorted)}')

# Step: assign eighth_id (1..480) and derive hizb (1..60) and pos_in_hizb (1..8)
result = []
for i, b in enumerate(all_boundaries_sorted):
    eighth_id = i + 1
    hizb = (i // 8) + 1
    pos_in_hizb = (i % 8) + 1
    v = verse_map.get((b['sura'], b['aya']))
    text_preview = ''
    if v:
        start = b['char_offset']
        text_preview = v['text_vocalized'][start:start+40]
    result.append({
        'eighth_id': eighth_id,
        'hizb': hizb,
        'pos_in_hizb': pos_in_hizb,
        'sura': b['sura'],
        'aya': b['aya'],
        'char_offset': b['char_offset'],
        'at_verse_start': b.get('at_verse_start', False),
        'implicit': b.get('implicit', False),
        'text_preview': text_preview.replace('۞','').strip()[:40],
    })

# Write output
with open(os.path.join(BUILD, 'eighths.json'), 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)
print(f'Wrote build/eighths.json ({len(result)} eighths)')

# Validate hizb starts match the canonical list
report = ['# Eighth Index Report\n', f'Total eighths: {len(result)}\n']
report.append('\n## Hizb starts vs canonical\n')
report.append('| Hizb | Expected (canonical) | Got (Mauri) | Match |')
report.append('|------|----------------------|-------------|-------|')
for i in range(60):
    expected = HIZB_STARTS_KUFI[i]
    # hizb i+1 starts at eighth_id = i*8+1 = pos_in_hizb 1
    got = result[i*8]
    match = '✅' if (got['sura'], got['aya']) == expected else '⚠️'
    report.append(f"| {i+1} | {expected[0]}:{expected[1]} | {got['sura']}:{got['aya']} (off={got['char_offset']}) | {match} |")

with open(os.path.join(REPORTS, 'eighths_report.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))
print(f'Wrote reports/eighths_report.md')

# Summary
matches = sum(1 for i in range(60) if (result[i*8]['sura'], result[i*8]['aya']) == HIZB_STARTS_KUFI[i])
print(f'\nHizb starts matching canonical: {matches}/60')
