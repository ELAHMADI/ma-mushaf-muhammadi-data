"""
Enrich quran_muhammadi.json and eighths.json with app-useful attributes,
and emit aggregate metadata: surahs.json, juzs.json, hizbs.json.

Adds to each VERSE:
  - word_count, char_count (of text_vocalized)
  - juz  (1..30)
  - hizb (1..60)
  - eighth_id (1..480) — the eighth this verse starts in
  - is_sajda (bool)

Adds to each EIGHTH:
  - juz (1..30)
  - is_surah_start (bool) — eighth begins at verse (S, 1) with offset 0
  - name_ar (positional Moroccan label, pos_in_hizb 1..8)

Writes new files:
  - build/surahs.json (114 entries)
  - build/juzs.json   (30 entries)
  - build/hizbs.json  (60 entries)

All aggregate entries carry: number, first_eighth_id, last_eighth_id,
first_page_mushafma, last_page_mushafma, verse_count, word_count.
"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUILD = os.path.join(ROOT, 'build')

verses = json.load(open(os.path.join(BUILD, 'quran_muhammadi.json'), encoding='utf-8'))
eighths = json.load(open(os.path.join(BUILD, 'eighths.json'), encoding='utf-8'))

# --- Positional Moroccan eighth labels (per CLAUDE.md) ---
EIGHTH_NAMES_AR = {
    1: 'الثمن الأول',
    2: 'الربع',
    3: 'ثلاثة أثمان',
    4: 'النصف',
    5: 'خمسة أثمان',
    6: 'ثلاثة أرباع',
    7: 'سبعة أثمان',
    8: 'الثمن الأخير',
}

# --- Moroccan Maliki sajda verses: 11 only (NOT the universal 15) ---
# Followed in Morocco. Verse numbers are Madani Akhir (Moroccan Warsh).
# Excluded vs Hanafi/Shafi'i 15-list:
#   22:76 (second Hajj sajda), 53:61 (An-Najm),
#   84:21 (Al-Inshiqaq),       96:19 (Al-'Alaq)
# Verse-number shifts vs Kufi (due to Madani Akhir boundary differences):
#   13:15 Kufi -> 13:16 Madani   (Ar-Ra'd)
#   17:109 Kufi -> 17:108 Madani (Al-Isra)
#   38:24 Kufi -> 38:23 Madani   (Sad)
#   41:38 Kufi -> 41:36 Madani   (Fussilat)
SAJDA_VERSES = {
    (7, 206),  (13, 16), (16, 50), (17, 108), (19, 58),
    (22, 18),  (25, 60), (27, 26), (32, 15),  (38, 23),
    (41, 36),
}

# --- Surah names (Arabic + Latin transliteration) + revelation place ---
# Madani = revealed in Medina, Makki = revealed in Mecca.
SURAH_META = [
    # (num, name_ar, translit, revelation, kufi_aya_count_for_ref)
    (1, 'الفاتحة', 'Al-Fatiha', 'makki', 7),
    (2, 'البقرة', 'Al-Baqara', 'madani', 286),
    (3, 'آل عمران', "Al-'Imran", 'madani', 200),
    (4, 'النساء', 'An-Nisa', 'madani', 176),
    (5, 'المائدة', "Al-Ma'ida", 'madani', 120),
    (6, 'الأنعام', "Al-An'am", 'makki', 165),
    (7, 'الأعراف', "Al-A'raf", 'makki', 206),
    (8, 'الأنفال', 'Al-Anfal', 'madani', 75),
    (9, 'التوبة', 'At-Tawba', 'madani', 129),
    (10, 'يونس', 'Yunus', 'makki', 109),
    (11, 'هود', 'Hud', 'makki', 123),
    (12, 'يوسف', 'Yusuf', 'makki', 111),
    (13, 'الرعد', "Ar-Ra'd", 'madani', 43),
    (14, 'إبراهيم', 'Ibrahim', 'makki', 52),
    (15, 'الحجر', 'Al-Hijr', 'makki', 99),
    (16, 'النحل', 'An-Nahl', 'makki', 128),
    (17, 'الإسراء', 'Al-Isra', 'makki', 111),
    (18, 'الكهف', 'Al-Kahf', 'makki', 110),
    (19, 'مريم', 'Maryam', 'makki', 98),
    (20, 'طه', 'Ta-Ha', 'makki', 135),
    (21, 'الأنبياء', 'Al-Anbiya', 'makki', 112),
    (22, 'الحج', 'Al-Hajj', 'madani', 78),
    (23, 'المؤمنون', "Al-Mu'minun", 'makki', 118),
    (24, 'النور', 'An-Nur', 'madani', 64),
    (25, 'الفرقان', 'Al-Furqan', 'makki', 77),
    (26, 'الشعراء', "Ash-Shu'ara", 'makki', 227),
    (27, 'النمل', 'An-Naml', 'makki', 93),
    (28, 'القصص', 'Al-Qasas', 'makki', 88),
    (29, 'العنكبوت', "Al-'Ankabut", 'makki', 69),
    (30, 'الروم', 'Ar-Rum', 'makki', 60),
    (31, 'لقمان', 'Luqman', 'makki', 34),
    (32, 'السجدة', 'As-Sajda', 'makki', 30),
    (33, 'الأحزاب', 'Al-Ahzab', 'madani', 73),
    (34, 'سبأ', "Saba'", 'makki', 54),
    (35, 'فاطر', 'Fatir', 'makki', 45),
    (36, 'يس', 'Ya-Sin', 'makki', 83),
    (37, 'الصافات', 'As-Saffat', 'makki', 182),
    (38, 'ص', 'Sad', 'makki', 88),
    (39, 'الزمر', 'Az-Zumar', 'makki', 75),
    (40, 'غافر', 'Ghafir', 'makki', 85),
    (41, 'فصلت', 'Fussilat', 'makki', 54),
    (42, 'الشورى', 'Ash-Shura', 'makki', 53),
    (43, 'الزخرف', 'Az-Zukhruf', 'makki', 89),
    (44, 'الدخان', 'Ad-Dukhan', 'makki', 59),
    (45, 'الجاثية', 'Al-Jathiya', 'makki', 37),
    (46, 'الأحقاف', 'Al-Ahqaf', 'makki', 35),
    (47, 'محمد', 'Muhammad', 'madani', 38),
    (48, 'الفتح', 'Al-Fath', 'madani', 29),
    (49, 'الحجرات', 'Al-Hujurat', 'madani', 18),
    (50, 'ق', 'Qaf', 'makki', 45),
    (51, 'الذاريات', 'Adh-Dhariyat', 'makki', 60),
    (52, 'الطور', 'At-Tur', 'makki', 49),
    (53, 'النجم', 'An-Najm', 'makki', 62),
    (54, 'القمر', 'Al-Qamar', 'makki', 55),
    (55, 'الرحمن', 'Ar-Rahman', 'madani', 78),
    (56, 'الواقعة', "Al-Waqi'a", 'makki', 96),
    (57, 'الحديد', 'Al-Hadid', 'madani', 29),
    (58, 'المجادلة', 'Al-Mujadala', 'madani', 22),
    (59, 'الحشر', 'Al-Hashr', 'madani', 24),
    (60, 'الممتحنة', 'Al-Mumtahana', 'madani', 13),
    (61, 'الصف', 'As-Saff', 'madani', 14),
    (62, 'الجمعة', "Al-Jumu'a", 'madani', 11),
    (63, 'المنافقون', 'Al-Munafiqun', 'madani', 11),
    (64, 'التغابن', 'At-Taghabun', 'madani', 18),
    (65, 'الطلاق', 'At-Talaq', 'madani', 12),
    (66, 'التحريم', 'At-Tahrim', 'madani', 12),
    (67, 'الملك', 'Al-Mulk', 'makki', 30),
    (68, 'القلم', 'Al-Qalam', 'makki', 52),
    (69, 'الحاقة', 'Al-Haqqa', 'makki', 52),
    (70, 'المعارج', "Al-Ma'arij", 'makki', 44),
    (71, 'نوح', 'Nuh', 'makki', 28),
    (72, 'الجن', 'Al-Jinn', 'makki', 28),
    (73, 'المزمل', 'Al-Muzzammil', 'makki', 20),
    (74, 'المدثر', 'Al-Muddaththir', 'makki', 56),
    (75, 'القيامة', 'Al-Qiyama', 'makki', 40),
    (76, 'الإنسان', 'Al-Insan', 'madani', 31),
    (77, 'المرسلات', 'Al-Mursalat', 'makki', 50),
    (78, 'النبأ', "An-Naba'", 'makki', 40),
    (79, 'النازعات', "An-Nazi'at", 'makki', 46),
    (80, 'عبس', "'Abasa", 'makki', 42),
    (81, 'التكوير', 'At-Takwir', 'makki', 29),
    (82, 'الانفطار', 'Al-Infitar', 'makki', 19),
    (83, 'المطففين', 'Al-Mutaffifin', 'makki', 36),
    (84, 'الانشقاق', 'Al-Inshiqaq', 'makki', 25),
    (85, 'البروج', 'Al-Buruj', 'makki', 22),
    (86, 'الطارق', 'At-Tariq', 'makki', 17),
    (87, 'الأعلى', "Al-A'la", 'makki', 19),
    (88, 'الغاشية', 'Al-Ghashiya', 'makki', 26),
    (89, 'الفجر', 'Al-Fajr', 'makki', 30),
    (90, 'البلد', 'Al-Balad', 'makki', 20),
    (91, 'الشمس', 'Ash-Shams', 'makki', 15),
    (92, 'الليل', 'Al-Layl', 'makki', 21),
    (93, 'الضحى', 'Ad-Duha', 'makki', 11),
    (94, 'الشرح', 'Ash-Sharh', 'makki', 8),
    (95, 'التين', 'At-Tin', 'makki', 8),
    (96, 'العلق', "Al-'Alaq", 'makki', 19),
    (97, 'القدر', 'Al-Qadr', 'makki', 5),
    (98, 'البينة', 'Al-Bayyina', 'madani', 8),
    (99, 'الزلزلة', 'Az-Zalzala', 'madani', 8),
    (100, 'العاديات', "Al-'Adiyat", 'makki', 11),
    (101, 'القارعة', "Al-Qari'a", 'makki', 11),
    (102, 'التكاثر', 'At-Takathur', 'makki', 8),
    (103, 'العصر', "Al-'Asr", 'makki', 3),
    (104, 'الهمزة', 'Al-Humaza', 'makki', 9),
    (105, 'الفيل', 'Al-Fil', 'makki', 5),
    (106, 'قريش', 'Quraysh', 'makki', 4),
    (107, 'الماعون', "Al-Ma'un", 'makki', 7),
    (108, 'الكوثر', 'Al-Kawthar', 'makki', 3),
    (109, 'الكافرون', 'Al-Kafirun', 'makki', 6),
    (110, 'النصر', 'An-Nasr', 'madani', 3),
    (111, 'المسد', 'Al-Masad', 'makki', 5),
    (112, 'الإخلاص', 'Al-Ikhlas', 'makki', 4),
    (113, 'الفلق', 'Al-Falaq', 'makki', 5),
    (114, 'الناس', 'An-Nas', 'makki', 6),
]

# =============================================================
# Build per-verse -> eighth_id lookup by walking eighths in order
# =============================================================

# gid lookup
gid_map = {(v['sura'], v['aya']): v['gid'] for v in verses}

# Which eighth does each gid fall into?
# An eighth covers verses from start.(sura,aya) to end.(sura,aya) INCLUSIVE.
# A mid-verse split means the SAME verse belongs to two eighths — we tag the
# verse with the eighth where its FIRST character appears (start of wird).
verse_eighth = {}  # gid -> eighth_id
for e in eighths:
    for vc in e['verses_covered']:
        g = gid_map[(vc['sura'], vc['aya'])]
        if g not in verse_eighth:
            verse_eighth[g] = e['eighth_id']

assert len(verse_eighth) == len(verses), \
    f'verses without eighth: {len(verses) - len(verse_eighth)}'

# =============================================================
# Enrich verses
# =============================================================
for v in verses:
    text = v['text']
    v['word_count'] = len(text.split())
    v['char_count'] = len(text)
    eid = verse_eighth[v['gid']]
    v['eighth_id'] = eid
    # eighth_id 1..8 -> hizb 1; 9..16 -> hizb 2; ...
    v['hizb'] = (eid - 1) // 8 + 1
    v['juz'] = (v['hizb'] + 1) // 2  # juz 1 = hizbs 1,2
    v['is_sajda'] = (v['sura'], v['aya']) in SAJDA_VERSES

# =============================================================
# Enrich eighths
# =============================================================
for e in eighths:
    hizb = e['hizb']
    e['juz'] = (hizb + 1) // 2
    e['name_ar'] = EIGHTH_NAMES_AR[e['pos_in_hizb']]
    s = e['start']
    e['is_surah_start'] = (s['aya'] == 1 and s['char_offset'] == 0)

# =============================================================
# Build aggregate metadata
# =============================================================

# Group verses by (sura) for surahs.json
verses_by_sura = {}
for v in verses:
    verses_by_sura.setdefault(v['sura'], []).append(v)

# Eighths by surah (first eighth that STARTS at or before a surah's first verse;
# last eighth that CONTAINS the surah's last verse).
# Simpler: for each surah, use its verses' eighth_ids.
surahs_out = []
for num, name_ar, translit, rev, _ref_count in SURAH_META:
    vs = verses_by_sura[num]
    eids = sorted({v['eighth_id'] for v in vs})
    # last eighth may continue beyond surah end — we still use these for scope
    first_e = eids[0]
    last_e = eids[-1]
    surahs_out.append({
        'number': num,
        'name_ar': name_ar,
        'name_transliteration': translit,
        'revelation': rev,
        'verse_count': len(vs),
        'word_count': sum(v['word_count'] for v in vs),
        'first_eighth_id': first_e,
        'last_eighth_id': last_e,
        'first_page_mushafma': vs[0]['page_mushafma'],
        'last_page_mushafma': vs[-1]['page_mushafma'],
        'first_verse_gid': vs[0]['gid'],
        'last_verse_gid': vs[-1]['gid'],
        'has_sajda': any(v['is_sajda'] for v in vs),
    })

# Hizbs (60)
hizbs_out = []
for h in range(1, 61):
    h_eighths = [e for e in eighths if e['hizb'] == h]
    h_verse_ids = set()
    for e in h_eighths:
        for vc in e['verses_covered']:
            h_verse_ids.add(gid_map[(vc['sura'], vc['aya'])])
    h_verses = [v for v in verses if v['gid'] in h_verse_ids]
    first_e = h_eighths[0]
    last_e = h_eighths[-1]
    hizbs_out.append({
        'number': h,
        'juz': (h + 1) // 2,
        'first_eighth_id': first_e['eighth_id'],
        'last_eighth_id': last_e['eighth_id'],
        'start': first_e['start'],
        'end': last_e['end'],
        'first_page_mushafma': first_e['start']['mushafma_page'],
        'last_page_mushafma': last_e['end']['mushafma_page'],
        'verse_count': len(h_verses),
        'word_count': sum(v['word_count'] for v in h_verses),
    })

# Juzs (30)
juzs_out = []
for j in range(1, 31):
    j_hizbs = [h for h in hizbs_out if h['juz'] == j]
    j_eighths = [e for e in eighths if e['juz'] == j]
    j_verse_ids = set()
    for e in j_eighths:
        for vc in e['verses_covered']:
            j_verse_ids.add(gid_map[(vc['sura'], vc['aya'])])
    j_verses = [v for v in verses if v['gid'] in j_verse_ids]
    first_e = j_eighths[0]
    last_e = j_eighths[-1]
    juzs_out.append({
        'number': j,
        'first_hizb': j_hizbs[0]['number'],
        'last_hizb': j_hizbs[-1]['number'],
        'first_eighth_id': first_e['eighth_id'],
        'last_eighth_id': last_e['eighth_id'],
        'start': first_e['start'],
        'end': last_e['end'],
        'first_page_mushafma': first_e['start']['mushafma_page'],
        'last_page_mushafma': last_e['end']['mushafma_page'],
        'verse_count': len(j_verses),
        'word_count': sum(v['word_count'] for v in j_verses),
    })

# =============================================================
# Write outputs
# =============================================================
def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

write_json(os.path.join(BUILD, 'quran_muhammadi.json'), verses)
write_json(os.path.join(BUILD, 'eighths.json'), eighths)
write_json(os.path.join(BUILD, 'surahs.json'), surahs_out)
write_json(os.path.join(BUILD, 'hizbs.json'), hizbs_out)
write_json(os.path.join(BUILD, 'juzs.json'), juzs_out)

# Summary
total_words = sum(v['word_count'] for v in verses)
total_chars = sum(v['char_count'] for v in verses)
print(f'Verses:  {len(verses)}  ({total_words} words, {total_chars} chars)')
print(f'Eighths: {len(eighths)}')
print(f'Surahs:  {len(surahs_out)}')
print(f'Hizbs:   {len(hizbs_out)}')
print(f'Juzs:    {len(juzs_out)}')
print(f'Sajda verses: {sum(1 for v in verses if v["is_sajda"])} (expected 11 — Maliki/Moroccan)')
print(f'Is-surah-start eighths: {sum(1 for e in eighths if e["is_surah_start"])}')
