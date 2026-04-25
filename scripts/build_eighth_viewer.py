"""Build HTML viewer showing every eighth boundary next to its mushaf.ma page.

Organized as 60 hizbs × 8 eighths. For each eighth:
- eighth_id, hizb/position
- text preview (where the ۞ falls)
- link to mushaf.ma page image

User can visually confirm each boundary matches a printed marker.
"""
import io, os, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUILD = os.path.join(ROOT, 'build')
RAW = os.path.join(ROOT, 'raw')

eighths = json.load(open(os.path.join(BUILD, 'eighths.json'), encoding='utf-8'))
mauri = json.load(open(os.path.join(RAW, 'mauri_verses.json'), encoding='utf-8'))
verse_map = {(v['sura_idx'], v['aya']): v for v in mauri}

# Group by hizb
hizbs = [[] for _ in range(60)]
for e in eighths:
    hizbs[e['hizb']-1].append(e)

html = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8">
<title>Eighths Validation - 480 boundaries</title>
<style>
  body { font-family: 'Amiri Quran','Traditional Arabic',serif; margin:0; background:#f5f5f0; }
  header { background:#1a6b3a; color:white; padding:12px 20px; position:sticky; top:0; z-index:10; }
  header h1 { margin:0; font-size:16px; }
  .sub { font-size:12px; opacity:0.85; }
  .hizb-nav { padding:8px; background:#234; color:#cde; position:sticky; top:40px; z-index:9; font-size:12px; overflow-x:auto; white-space:nowrap; }
  .hizb-nav a { color:#cde; margin-right:8px; text-decoration:none; padding:2px 6px; border-radius:4px; background:rgba(255,255,255,0.1); }
  .hizb-nav a:hover { background:rgba(255,255,255,0.3); }
  .hizb { margin:20px; background:white; border-radius:8px; padding:14px; box-shadow:0 1px 4px rgba(0,0,0,0.1); }
  .hizb h2 { margin:0 0 10px; color:#1a6b3a; font-size:17px; }
  .eighth { display:grid; grid-template-columns: 60px 1fr 340px; gap:12px; padding:8px; border-bottom:1px solid #eee; align-items:center; }
  .eighth:last-child { border-bottom:none; }
  .eid { font-weight:bold; color:#555; font-family:monospace; font-size:13px; }
  .eid .pos { display:block; font-size:11px; color:#999; }
  .eid.implicit { color:#c62; }
  .text-snip { font-size:17px; line-height:1.9; }
  .text-snip .marker-word { background:#fffab0; padding:0 3px; border-radius:3px; }
  .meta { font-size:12px; color:#666; }
  .meta a { color:#1a6b3a; }
  .page-thumb img { max-width:320px; border:1px solid #ccc; border-radius:4px; }
  details summary { cursor:pointer; color:#1a6b3a; font-size:13px; }
  .implicit-tag { background:#fdd; color:#c33; font-size:10px; padding:1px 5px; border-radius:3px; margin-right:4px; }
</style>
</head>
<body>
<header>
  <h1>تحقق من الأثمان - 480 eighths</h1>
  <div class="sub">لكل ثُمْن: تحقق أن الموضع موافق للعلامة ۞ في الصفحة المحمدية</div>
</header>
<div class="hizb-nav">
"""
for h in range(1, 61):
    html += f'<a href="#hizb{h}">حزب {h}</a>'
html += '</div>\n'

for h_idx, eighths_in_h in enumerate(hizbs):
    h_num = h_idx + 1
    first = eighths_in_h[0]
    fs = first['start']
    html += f'<div class="hizb" id="hizb{h_num}"><h2>الحزب {h_num} — يبدأ عند {fs["sura"]}:{fs["aya"]}</h2>'
    for e in eighths_in_h:
        s = e['start']
        end = e['end']
        v = verse_map.get((s['sura'], s['aya']))
        text_around = ''
        if v:
            before = v['text_vocalized'][max(0,s['char_offset']-40):s['char_offset']]
            at_mark = v['text_vocalized'][s['char_offset']:s['char_offset']+50]
            text_around = (
                f'<span style="color:#888">...{before}</span>'
                f'<span class="marker-word">۞{at_mark}</span>...'
            )
        mushafma_page = s['mushafma_page']
        implicit_tag = '<span class="implicit-tag">ضِمْني</span>' if e.get('implicit_start') else ''
        html += f"""
<div class="eighth">
  <div class="eid{' implicit' if e.get('implicit_start') else ''}">#{e['eighth_id']}<span class="pos">ح{e['hizb']}.ث{e['pos_in_hizb']}</span></div>
  <div>
    <div class="text-snip">{implicit_tag}{text_around}</div>
    <div class="meta">
      <b>بداية:</b> {s['sura']}:{s['aya']} @{s['char_offset']}
      {'<span style="color:#c62">(آية مجزأة)</span>' if s.get('partial_verse') else ''}
      &nbsp;<b>نهاية:</b> {end['sura']}:{end['aya']} @{end['char_offset']} (شاملة)
      {'<span style="color:#c62">(آية مجزأة)</span>' if end.get('partial_verse') else ''}
      <br>{e['verse_count']} آية، {e['word_count']} كلمة &nbsp;
      <a href="../raw/muhammadi-pages/page{mushafma_page:03d}.png" target="_blank">📄 صفحة {mushafma_page:03d}</a>
    </div>
  </div>
  <div class="page-thumb">
    <details><summary>معاينة الصفحة</summary>
    <img src="../raw/muhammadi-pages/page{mushafma_page:03d}.png" loading="lazy">
    </details>
  </div>
</div>"""
    html += '</div>'

html += '</body></html>'

out = os.path.join(BUILD, 'eighths_viewer.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Wrote: {out}')
print(f'Open: file:///{out.replace(os.sep, "/")}')
