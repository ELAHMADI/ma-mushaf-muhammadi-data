"""
Rebuild eighths.json with explicit INCLUSIVE start and end ranges.

Each eighth is defined by:
  - start: where it BEGINS (sura, aya, char_offset_start) - INCLUSIVE
  - end:   where it ENDS   (sura, aya, char_offset_end)  - INCLUSIVE

The end position is the position of the LAST character included in the eighth,
which is one char before the next eighth's start (if same verse) or the end
of the last covered verse (if the next eighth begins at a new verse).

Examples (inclusive convention):
  eighth 460 = start (74:31, off 0)
                 end   (74:55, end of verse)        # covers 74:31..74:55 fully
  eighth 461 = start (75:1,  off 0)
                 end   (75:40, end of verse)        # covers 75:1..75:40 (all of sura 75)
  eighth 462 = start (76:1,  off 0)
                 end   (76:18, end of verse)        # covers 76:1..76:18

When an eighth ends MID-VERSE (e.g., at a ۞ inside a verse):
  end.char_offset points to the last char of the eighth, aya is the verse
  containing the mid-cut, partial_verse = true.

Also includes word_count and verses_covered.
"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'raw')
BUILD = os.path.join(ROOT, 'build')

mauri = json.load(open(os.path.join(RAW, 'mauri_verses.json'), encoding='utf-8'))
old_eighths = json.load(open(os.path.join(BUILD, 'eighths.json'), encoding='utf-8'))

gid_map = {(v['sura_idx'], v['aya']): v['gid'] for v in mauri}
verse_map = {v['gid']: v for v in mauri}
by_key = {(v['sura_idx'], v['aya']): v for v in mauri}
last_gid = max(v['gid'] for v in mauri)  # 6214

def word_count_range_inclusive(start_s, start_a, start_off, end_s, end_a, end_char_inclusive):
    """Count words from (start_s, start_a, start_off) INCLUSIVE
    to (end_s, end_a, end_char_inclusive) INCLUSIVE."""
    g1 = gid_map[(start_s, start_a)]
    g2 = gid_map[(end_s, end_a)]
    if g1 == g2:
        v = by_key[(start_s, start_a)]
        seg = v['text_vocalized'][start_off:end_char_inclusive + 1]
        return len(seg.split())
    total = 0
    v1 = by_key[(start_s, start_a)]
    total += len(v1['text_vocalized'][start_off:].split())
    for g in range(g1 + 1, g2):
        total += len(verse_map[g]['text_vocalized'].split())
    v2 = by_key[(end_s, end_a)]
    total += len(v2['text_vocalized'][:end_char_inclusive + 1].split())
    return total

def verses_in_range_inclusive(start_s, start_a, end_s, end_a):
    """List of (sura, aya) from start to end, INCLUSIVE of both endpoints."""
    g1 = gid_map[(start_s, start_a)]
    g2 = gid_map[(end_s, end_a)]
    return [(verse_map[g]['sura_idx'], verse_map[g]['aya']) for g in range(g1, g2 + 1)]

# Use old eighths as anchor points (support both legacy flat and nested format)
anchors = []
for e in old_eighths:
    if 'start' in e:
        anchors.append({
            'eighth_id': e['eighth_id'],
            'hizb': e['hizb'],
            'pos_in_hizb': e['pos_in_hizb'],
            'sura': e['start']['sura'],
            'aya': e['start']['aya'],
            'char_offset': e['start']['char_offset'],
            'implicit': e.get('implicit_start', False),
        })
    else:
        anchors.append({
            'eighth_id': e['eighth_id'],
            'hizb': e['hizb'],
            'pos_in_hizb': e['pos_in_hizb'],
            'sura': e['sura'],
            'aya': e['aya'],
            'char_offset': e['char_offset'],
            'implicit': e.get('implicit', False),
        })

# Build ranges: eighth N's end = one char before eighth N+1's start.
# If eighth N+1 starts at offset 0 of a new verse, eighth N ends at the last
# char of the PREVIOUS verse. Otherwise eighth N ends at (next_start_off - 1)
# within the same verse.
result = []
for i, e in enumerate(anchors):
    if i < len(anchors) - 1:
        nxt = anchors[i + 1]
        nxt_s, nxt_a, nxt_off = nxt['sura'], nxt['aya'], nxt['char_offset']
        if nxt_off == 0:
            # End of eighth = last char of verse BEFORE (nxt_s, nxt_a)
            nxt_gid = gid_map[(nxt_s, nxt_a)]
            prev_v = verse_map[nxt_gid - 1]
            end_s = prev_v['sura_idx']
            end_a = prev_v['aya']
            end_char = len(prev_v['text_vocalized']) - 1
            end_partial = False
        else:
            # End mid-verse at (nxt_s, nxt_a, nxt_off - 1)
            end_s, end_a = nxt_s, nxt_a
            end_char = nxt_off - 1
            end_partial = True
    else:
        # Last eighth — ends at the last char of the last verse (114:6)
        last_v = by_key[(114, 6)]
        end_s, end_a = 114, 6
        end_char = len(last_v['text_vocalized']) - 1
        end_partial = False

    words = word_count_range_inclusive(e['sura'], e['aya'], e['char_offset'],
                                        end_s, end_a, end_char)
    covered = verses_in_range_inclusive(e['sura'], e['aya'], end_s, end_a)

    v_start = by_key[(e['sura'], e['aya'])]
    start_page = v_start['page'] + 1  # mushaf.ma page
    v_end = by_key[(end_s, end_a)]
    end_page = v_end['page'] + 1

    start_partial = e['char_offset'] > 0

    text_preview = v_start['text_vocalized'][e['char_offset']:e['char_offset']+50].replace('۞','').strip()

    result.append({
        'eighth_id': e['eighth_id'],
        'hizb': e['hizb'],
        'pos_in_hizb': e['pos_in_hizb'],
        'start': {
            'sura': e['sura'],
            'aya': e['aya'],
            'char_offset': e['char_offset'],
            'partial_verse': start_partial,
            'mushafma_page': start_page,
        },
        'end': {
            'sura': end_s,
            'aya': end_a,
            'char_offset': end_char,
            'inclusive': True,
            'partial_verse': end_partial,
            'mushafma_page': end_page,
        },
        'verses_covered': [{'sura': s, 'aya': a} for s, a in covered],
        'verse_count': len(covered),
        'word_count': words,
        'implicit_start': e['implicit'],
        'text_preview': text_preview[:60],
    })

with open(os.path.join(BUILD, 'eighths.json'), 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Wrote {len(result)} eighths with start/end ranges')
print()
# Show an example: eighth 459, 460, 461, 462 (the gap area)
for e in result:
    if e['eighth_id'] in (459, 460, 461, 462):
        s = e['start']
        nd = e['end']
        print(f"Eighth #{e['eighth_id']}  (hizb {e['hizb']}, pos {e['pos_in_hizb']})")
        print(f"  START: {s['sura']}:{s['aya']} @off {s['char_offset']}"
              f" (page {s['mushafma_page']})"
              f" {'[MID-VERSE]' if s['partial_verse'] else ''}"
              f" {'[IMPLICIT]' if e['implicit_start'] else ''}")
        print(f"  END  : {nd['sura']}:{nd['aya']} @off {nd['char_offset']}"
              f" (page {nd['mushafma_page']}) INCLUSIVE"
              f" {'[mid-verse cut]' if nd['partial_verse'] else '(whole last verse)'}")
        vc = e['verses_covered']
        print(f"  Verses covered: {e['verse_count']} ({vc[0]['sura']}:{vc[0]['aya']} ... {vc[-1]['sura']}:{vc[-1]['aya']})")
        print(f"  Words: {e['word_count']}")
        print(f"  Preview: {e['text_preview']}")
        print()
