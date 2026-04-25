"""Find the 3 gaps in the 477 markers by looking for large jumps."""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'raw')
BUILD = os.path.join(ROOT, 'build')

mauri = json.load(open(os.path.join(RAW, 'mauri_verses.json'), encoding='utf-8'))
markers = json.load(open(os.path.join(BUILD, 'markers_raw.json'), encoding='utf-8'))
gid_map = {(v['sura_idx'], v['aya']): v['gid'] for v in mauri}

# Sort markers
m_sorted = sorted(markers, key=lambda m: (gid_map[(m['sura'], m['aya'])], m['char_offset']))
# Prepend Fatiha
pts = [{'sura': 1, 'aya': 1, 'off': 0}] + [{'sura': m['sura'], 'aya': m['aya'], 'off': m['char_offset']} for m in m_sorted]

# Compute gap between consecutive markers in global-verse-id units
print(f'{len(pts)} total points (including Fatiha)')
print()

# Compute word count between consecutive boundaries
def word_count_between(p1, p2):
    """Count words in text between two boundary points."""
    total = 0
    # same verse
    if (p1['sura'], p1['aya']) == (p2['sura'], p2['aya']):
        v = next(v for v in mauri if v['sura_idx']==p1['sura'] and v['aya']==p1['aya'])
        segment = v['text_vocalized'][p1['off']:p2['off']]
        return len(segment.split())
    # different verses
    v1 = next(v for v in mauri if v['sura_idx']==p1['sura'] and v['aya']==p1['aya'])
    total += len(v1['text_vocalized'][p1['off']:].split())
    g1 = gid_map[(p1['sura'], p1['aya'])]
    g2 = gid_map[(p2['sura'], p2['aya'])]
    for g in range(g1+1, g2):
        vm = next(v for v in mauri if v['gid']==g)
        total += len(vm['text_vocalized'].split())
    v2 = next(v for v in mauri if v['sura_idx']==p2['sura'] and v['aya']==p2['aya'])
    total += len(v2['text_vocalized'][:p2['off']].split())
    return total

# Compute word counts for first 100 gaps and entire list
gaps = []
for i in range(len(pts)-1):
    w = word_count_between(pts[i], pts[i+1])
    gaps.append(w)

# Total words in corpus
total_words = sum(len(v['text_vocalized'].split()) for v in mauri)
print(f'Total words (Mauri): {total_words}')
print(f'Expected words per eighth: {total_words/480:.0f}')
print(f'Expected words per hizb: {total_words/60:.0f}')
print()

# Show abnormally large gaps (> 2× expected)
expected_per_eighth = total_words / 480
print(f'Gaps > 2x expected ({expected_per_eighth:.0f}):')
large_gaps = [(i, g) for i, g in enumerate(gaps) if g > 2 * expected_per_eighth]
for i, g in large_gaps[:30]:
    p1, p2 = pts[i], pts[i+1]
    print(f'  gap[{i}] = {g} words  from {p1["sura"]}:{p1["aya"]}@{p1["off"]} -> {p2["sura"]}:{p2["aya"]}@{p2["off"]}')

# Show smallest gaps too (extraneous markers)
print(f'\nSmallest gaps:')
small = sorted([(i,g) for i,g in enumerate(gaps)], key=lambda x: x[1])[:5]
for i,g in small:
    p1, p2 = pts[i], pts[i+1]
    print(f'  gap[{i}] = {g} words  from {p1["sura"]}:{p1["aya"]}@{p1["off"]} -> {p2["sura"]}:{p2["aya"]}@{p2["off"]}')

# Mean, std
mean = sum(gaps)/len(gaps)
var = sum((g-mean)**2 for g in gaps)/len(gaps)
print(f'\nStats: mean={mean:.1f}, stddev={var**0.5:.1f}, min={min(gaps)}, max={max(gaps)}')
