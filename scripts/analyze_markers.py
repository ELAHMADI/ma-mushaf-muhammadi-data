"""Compare HizbQuarter list (240) with ۞ markers (477) to derive 480 eighth boundaries."""
import io, os, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'raw')
BUILD = os.path.join(ROOT, 'build')

markers = json.load(open(os.path.join(BUILD, 'markers_raw.json'), encoding='utf-8'))
mauri = json.load(open(os.path.join(RAW, 'mauri_verses.json'), encoding='utf-8'))

QURAN_DATA_JS = r'C:\Users\elahmano\AppData\Local\Temp\mushaf-mauri\src\data\quranData.js'
qd = open(QURAN_DATA_JS, encoding='utf-8').read()

m = re.search(r'QuranData\.HizbQaurter\s*=\s*\[(.*?)\n\];', qd, re.DOTALL)
block = m.group(1)
quarter_entries = re.findall(r'\[\s*(\d+)\s*,\s*(\d+)\s*\]', block)
# First entry looks like placeholder; skip empty
quarters = [(int(s), int(a)) for s, a in quarter_entries]
# strip the outer placeholders
# Actual data: first entry is [1,1], then 240 quarter-starts
print(f'Raw quarter entries: {len(quarters)}')
# The list likely has a leading empty [] placeholder so actual entries = 240

# Build marker-key set
marker_set = set((m['sura'], m['aya']) for m in markers)
print(f'Unique verses with ۞: {len(marker_set)}')

# For each HizbQuarter entry, check if that (sura, aya) has a ۞
quarters_with_marker = 0
quarters_without = []
for s, a in quarters:
    if (s, a) in marker_set:
        quarters_with_marker += 1
    else:
        quarters_without.append((s, a))

print(f'Quarters matching a ۞ marker: {quarters_with_marker}/{len(quarters)}')
print(f'Quarters WITHOUT a ۞ marker: {len(quarters_without)}')
print(f'First 10 without marker:')
for s, a in quarters_without[:10]:
    print(f'  hizb start: {s}:{a}')

# Extract marker positions NOT in HizbQuarter list — these are "mid-eighths"
quarter_set = set(quarters)
markers_only = [m for m in markers if (m['sura'], m['aya']) not in quarter_set]
print(f'\n۞ markers NOT in HizbQuarter list: {len(markers_only)}')
print(f'۞ markers IN HizbQuarter list: {len(markers) - len(markers_only)}')

# Hypothesis: 240 HizbQuarter + 240 "mid-eighths" = 480 eighths
# Count mid-eighths expected: 240
# Count mid-eighths found via ۞: len(markers_only)
