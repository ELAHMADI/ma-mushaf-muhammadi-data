"""
Build an offline HTML viewer for manual verification of the flagged 13 verses.

For each flagged (sura, aya), shows:
  - the mushaf.ma page image
  - Lawh candidate text (left)
  - Mauri candidate text (right)
  - Tanzil Warsh text for context
  - radio buttons to pick which matches the image

Writes build/review.html (standalone, no internet needed).
"""
import io, os, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'raw')
BUILD = os.path.join(ROOT, 'build')

merged = json.load(open(os.path.join(BUILD, 'quran_muhammadi.json'), encoding='utf-8'))
lawh = json.load(open(os.path.join(RAW, 'lawh_verses.json'), encoding='utf-8'))
mauri = json.load(open(os.path.join(RAW, 'mauri_verses.json'), encoding='utf-8'))
lawh_map = {(v['sura_idx'], v['aya']): v for v in lawh}
mauri_map = {(v['sura_idx'], v['aya']): v for v in mauri}

flagged = [v for v in merged if 'FLAG' in v.get('source_decision', '')]

cards = []
for v in flagged:
    s, a = v['sura'], v['aya']
    pg = v['page_mushafma']
    l = lawh_map[(s, a)]
    m = mauri_map[(s, a)]
    img_path = f'../raw/muhammadi-pages/page{pg:03d}.png'
    cards.append({
        'sura': s,
        'aya': a,
        'page': pg,
        'img': img_path,
        'lawh': l['text_full'],
        'mauri': m['text_vocalized'],
    })

html = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8">
<title>Manual Review - {len(cards)} verses</title>
<style>
  body {{ font-family: 'Amiri Quran', 'Traditional Arabic', serif; margin: 0; background: #f5f5f0; }}
  header {{ background: #1a6b3a; color: white; padding: 16px 24px; position: sticky; top: 0; z-index: 10; }}
  header h1 {{ margin: 0; font-size: 20px; }}
  header p {{ margin: 4px 0 0; font-size: 13px; opacity: 0.9; }}
  .card {{
    margin: 24px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    padding: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  }}
  .card h2 {{ grid-column: 1/-1; margin: 0 0 8px; color: #1a6b3a; font-size: 18px; }}
  .card .meta {{ grid-column: 1/-1; font-size: 13px; color: #666; margin-bottom: 12px; }}
  .img-pane img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }}
  .text-pane {{ padding-right: 8px; }}
  .choice {{
    padding: 12px; margin-bottom: 8px; border: 2px solid transparent; border-radius: 8px;
    background: #fafafa; cursor: pointer; transition: all 0.15s;
  }}
  .choice:hover {{ background: #f0f0eb; }}
  .choice.picked-lawh {{ border-color: #1a6b3a; background: #e8f5ec; }}
  .choice.picked-mauri {{ border-color: #d4a017; background: #fdf5e0; }}
  .choice-label {{ font-size: 12px; font-weight: bold; color: #555; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .choice-text {{ font-size: 20px; line-height: 2.2; }}
  .save-btn {{
    position: fixed; bottom: 24px; left: 24px; padding: 14px 28px;
    background: #1a6b3a; color: white; border: none; border-radius: 28px;
    font-size: 15px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }}
  .progress {{
    position: fixed; top: 60px; left: 24px; background: white; padding: 12px 18px;
    border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); font-size: 13px;
  }}
</style>
</head>
<body>
<header>
  <h1>مراجعة يدوية - {len(cards)} آية</h1>
  <p>لكل آية: افتح الصورة، ثم اختر النص المطابق (Lawh = أخضر، Mauri = أصفر)</p>
</header>
<div class="progress">
  <span id="count">0</span> / {len(cards)} مراجَع
</div>
"""

for i, c in enumerate(cards):
    html += f"""
<div class="card" data-idx="{i}" data-sura="{c['sura']}" data-aya="{c['aya']}">
  <h2>{i+1}. السورة {c['sura']} - الآية {c['aya']}</h2>
  <div class="meta">صفحة المصحف المحمدي: {c['page']:03d}</div>
  <div class="img-pane">
    <img src="{c['img']}" alt="page {c['page']}">
  </div>
  <div class="text-pane">
    <div class="choice" onclick="pick({i}, 'lawh', this)">
      <div class="choice-label">Lawh (الافتراضي)</div>
      <div class="choice-text">{c['lawh']}</div>
    </div>
    <div class="choice" onclick="pick({i}, 'mauri', this)">
      <div class="choice-label">Mauri</div>
      <div class="choice-text">{c['mauri']}</div>
    </div>
  </div>
</div>
"""

html += """
<button class="save-btn" onclick="save()">تنزيل الاختيارات (JSON)</button>
<script>
const picks = {};
function pick(idx, src, el) {
  const card = el.closest('.card');
  card.querySelectorAll('.choice').forEach(c => c.classList.remove('picked-lawh', 'picked-mauri'));
  el.classList.add('picked-' + src);
  picks[idx] = { sura: +card.dataset.sura, aya: +card.dataset.aya, choice: src };
  document.getElementById('count').textContent = Object.keys(picks).length;
}
function save() {
  const arr = Object.values(picks);
  const blob = new Blob([JSON.stringify(arr, null, 2)], {type: 'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'manual_picks.json';
  a.click();
}
</script>
</body>
</html>
"""

out = os.path.join(BUILD, 'review.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Wrote: {out}')
print(f'Open in browser: file:///{out.replace(os.sep, "/")}')
print(f'After reviewing, click "تنزيل الاختيارات" to save manual_picks.json')
