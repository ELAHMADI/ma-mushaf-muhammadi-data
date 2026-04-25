"""
Apply manual_picks.json (from review.html) to the merged quran_muhammadi.json.

Usage:
  1. Open build/review.html in a browser.
  2. For each of the flagged verses, click Lawh or Mauri based on the image.
  3. Click the download button -> saves manual_picks.json.
  4. Put manual_picks.json in data-foundation/raw/.
  5. Run this script to apply picks to quran_muhammadi.json.
"""
import io, os, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'raw')
BUILD = os.path.join(ROOT, 'build')

picks_path = os.path.join(RAW, 'manual_picks.json')
if not os.path.exists(picks_path):
    print(f'ERROR: {picks_path} not found.')
    print('Open build/review.html, make your picks, then download the JSON to raw/.')
    sys.exit(1)

picks = json.load(open(picks_path, encoding='utf-8'))
print(f'Loaded {len(picks)} manual picks')

merged = json.load(open(os.path.join(BUILD, 'quran_muhammadi.json'), encoding='utf-8'))
lawh = json.load(open(os.path.join(RAW, 'lawh_verses.json'), encoding='utf-8'))
mauri = json.load(open(os.path.join(RAW, 'mauri_verses.json'), encoding='utf-8'))
lawh_map = {(v['sura_idx'], v['aya']): v for v in lawh}
mauri_map = {(v['sura_idx'], v['aya']): v for v in mauri}
merged_map = {(v['sura'], v['aya']): v for v in merged}

applied = 0
for p in picks:
    key = (p['sura'], p['aya'])
    if key not in merged_map:
        print(f'  WARN: {key} not in merged')
        continue
    v = merged_map[key]
    if p['choice'] == 'lawh':
        v['text'] = lawh_map[key]['text_full'].strip().lstrip('_').strip()
        v['source_decision'] = 'manual_pick_lawh'
    elif p['choice'] == 'mauri':
        v['text'] = mauri_map[key]['text_vocalized'].strip()
        v['source_decision'] = 'manual_pick_mauri'
    applied += 1

with open(os.path.join(BUILD, 'quran_muhammadi.json'), 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False)

still_flagged = [v for v in merged if 'FLAG' in v.get('source_decision', '')]
print(f'Applied {applied} picks')
print(f'Still flagged: {len(still_flagged)}')
