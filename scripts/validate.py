"""
Sanity validation for the Moroccan Muhammadi dataset.

Run after any modification of data/*.json:

    python scripts/validate.py

Exits 0 on success, 1 on failure. Prints what was checked.
"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA = os.path.join(ROOT, 'data')

def load(name):
    return json.load(open(os.path.join(DATA, name), encoding='utf-8'))

errors = []
def check(cond, msg):
    if not cond:
        errors.append(msg)
        print(f'  FAIL  {msg}')
    else:
        print(f'  ok    {msg}')

print('Loading data files…')
verses  = load('quran_muhammadi.json')
eighths = load('eighths.json')
surahs  = load('surahs.json')
hizbs   = load('hizbs.json')
juzs    = load('juzs.json')
audio   = load('audio_sources.json')
version = load('VERSION.json')

# -------- Counts --------
print('\n[counts]')
check(len(verses)  == 6214, f'verses == 6214 (got {len(verses)})')
check(len(eighths) == 480,  f'eighths == 480 (got {len(eighths)})')
check(len(surahs)  == 114,  f'surahs == 114 (got {len(surahs)})')
check(len(hizbs)   == 60,   f'hizbs == 60 (got {len(hizbs)})')
check(len(juzs)    == 30,   f'juzs == 30 (got {len(juzs)})')

# -------- Verses --------
print('\n[verses]')
gids = [v['gid'] for v in verses]
check(gids == list(range(1, 6215)), 'gid is contiguous 1..6214')
check(all('text' in v and v['text'] for v in verses), 'every verse has non-empty text')
check(all('text_simple' in v for v in verses), 'every verse has text_simple')
check(all(1 <= v['hizb'] <= 60 for v in verses), 'hizb in 1..60')
check(all(1 <= v['juz'] <= 30 for v in verses), 'juz in 1..30')
check(all(1 <= v['eighth_id'] <= 480 for v in verses), 'eighth_id in 1..480')
check(all(3 <= v['page_mushafma'] <= 640 for v in verses), 'page_mushafma in 3..640')
check(all(v['word_count'] > 0 for v in verses), 'word_count > 0')
check(sum(1 for v in verses if v['is_sajda']) == 11,
      'exactly 11 sajda verses (Maliki / Maghreb)')

# Sajda set
expected_sajdas = {(7,206),(13,16),(16,50),(17,108),(19,58),(22,18),
                   (25,60),(27,26),(32,15),(38,23),(41,36)}
got = {(v['sura'], v['aya']) for v in verses if v['is_sajda']}
check(got == expected_sajdas, 'sajda set matches the 11 Maliki verses')

# -------- Eighths --------
print('\n[eighths]')
for i, e in enumerate(eighths, start=1):
    check(e['eighth_id'] == i, f'eighths[{i-1}].eighth_id == {i}') if i <= 3 or i == 480 else None
check(all(1 <= e['hizb'] <= 60 for e in eighths), 'hizb in 1..60')
check(all(1 <= e['pos_in_hizb'] <= 8 for e in eighths), 'pos_in_hizb in 1..8')
check(all(1 <= e['juz'] <= 30 for e in eighths), 'juz in 1..30')
check(all('start' in e and 'end' in e for e in eighths), 'every eighth has start + end')
check(all(e['end'].get('inclusive') is True for e in eighths), 'every end is inclusive')
check(all(e['verse_count'] >= 1 for e in eighths), 'verse_count >= 1')
check(all(e['word_count']  >= 1 for e in eighths), 'word_count >= 1')

# Per-hizb: 8 eighths, pos 1..8 in order
for h in range(1, 61):
    h_e = [e for e in eighths if e['hizb'] == h]
    check(len(h_e) == 8 and [e['pos_in_hizb'] for e in h_e] == list(range(1, 9)),
          f'hizb {h}: 8 eighths in order') if h in (1, 30, 60) else None

# -------- Cross-references --------
print('\n[cross-refs]')
gid_set = set(gids)
all_eighth_verses = set()
for e in eighths:
    for vc in e['verses_covered']:
        # No gid stored in verses_covered, so look up by (sura,aya)
        pass
verse_keys = {(v['sura'], v['aya']) for v in verses}
covered = set()
for e in eighths:
    for vc in e['verses_covered']:
        covered.add((vc['sura'], vc['aya']))
check(covered == verse_keys,
      f'every verse referenced in eighths matches a real verse '
      f'(missing={len(verse_keys - covered)}, extra={len(covered - verse_keys)})')

# -------- Aggregates --------
print('\n[aggregates]')
total_verses_in_surahs = sum(s['verse_count'] for s in surahs)
check(total_verses_in_surahs == 6214, f'sum(surahs.verse_count) == 6214 (got {total_verses_in_surahs})')

total_words_v = sum(v['word_count'] for v in verses)
total_words_s = sum(s['word_count'] for s in surahs)
check(total_words_v == total_words_s,
      f'sum verses.word_count ({total_words_v}) == sum surahs.word_count ({total_words_s})')

# Hizb -> juz consistency
for h in hizbs:
    expected_juz = (h['number'] + 1) // 2
    check(h['juz'] == expected_juz, f"hizb {h['number']} -> juz {expected_juz}") if h['number'] in (1, 30, 60) else None

# -------- VERSION --------
print('\n[version]')
check(version['verses'] == 6214, f"VERSION.verses == 6214")
check(version['eighths'] == 480, f"VERSION.eighths == 480")
check(version['sajda_verses'] == 11, f"VERSION.sajda_verses == 11")
check(version['riwaya'].lower().startswith('warsh'), 'VERSION.riwaya starts with Warsh')

# -------- Audio --------
print('\n[audio]')
ws = audio['warsh_per_surah']['reciters']
check(len(ws) >= 10, f'>= 10 Warsh reciters listed (got {len(ws)})')
check(all(r.get('server', '').startswith('http') for r in ws), 'every reciter has http(s) server')
check(all(r.get('tariq', '').startswith('Warsh') for r in ws), 'every reciter is Warsh')

# -------- Result --------
print()
if errors:
    print(f'FAIL — {len(errors)} error(s):')
    for e in errors:
        print(f'  - {e}')
    sys.exit(1)
print('OK — all checks passed.')
