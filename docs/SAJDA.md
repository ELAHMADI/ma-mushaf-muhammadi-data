# Sajda verses (آيات السجدة)

This dataset flags **11 sajda verses** — the Maliki / Maghreb tradition followed across Morocco, Algeria, and Tunisia.

This matches the printed Muhammadi mushaf, where exactly 11 verses bear the ۩ sign.

---

## The 11 sajda verses

All verse numbers are in the Moroccan numbering used by this dataset.

| # | Sura | Aya | Surah name | Mushaf page |
|---|---|---|---|---|
| 1 | 7  | 206 | الأعراف — Al-A'raf | 178 |
| 2 | 13 | 16  | الرعد — Ar-Ra'd | 254 |
| 3 | 16 | 50  | النحل — An-Nahl | 276 |
| 4 | 17 | 108 | الإسراء — Al-Isra | 298 |
| 5 | 19 | 58  | مريم — Maryam | 316 |
| 6 | 22 | 18  | الحج — Al-Hajj | 341 |
| 7 | 25 | 60  | الفرقان — Al-Furqan | 374 |
| 8 | 27 | 26  | النمل — An-Naml | 390 |
| 9 | 32 | 15  | السجدة — As-Sajda | 428 |
| 10 | 38 | 23 | ص — Sad | 469 |
| 11 | 41 | 36 | فصلت — Fussilat | 496 |

---

## In code

```js
const sajdas = verses.filter(v => v.is_sajda);
console.log(sajdas.length);  // 11
```

```python
sajdas = [v for v in verses if v["is_sajda"]]
assert len(sajdas) == 11
```

---

## Reference

The `is_sajda` flag in `data/quran_muhammadi.json` is set for these 11 verses, matching the ۩ markers printed in the Muhammadi mushaf.
