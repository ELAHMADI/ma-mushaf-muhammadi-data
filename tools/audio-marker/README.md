# Audio Marker — Kouchi (Warsh Muhammadi)

Outil web mobile-first pour marquer les timestamps verset par verset d'une récitation, aligné avec le mushaf Muhammadi de ce repo.

## Utilisation

1. Choisir la sourate dans le sélecteur
2. **تحميل** — charge l'audio Kouchi (mp3quran.net) + la liste des آيات
3. Lecture (▶) — écouter jusqu'à la fin de la 1ère آية
4. **MARK** — marque `end[1]` (qui devient automatiquement `start[2]`)
5. Continuer pour les آيات suivantes
6. **↶** Undo si erreur · **Nudges** ±100ms / ±1s pour rattraper la précision

L'autosave localStorage tourne en continu — fermer/reprendre OK.

## Export

- **📋 نسخ JSON** — copie dans le presse-papiers (à coller dans GitHub web editor)
- **📤 مشاركة** — Web Share API Android (Drive, Files, Email…)
- **⬇ تنزيل** — fichier `{NNN}.json` à placer dans `data/timings/kouchi/`

## Convention

`end[N] === start[N+1]` (pas de gap, pas d'overlap). `start[0] = 0`, `end[last]` = durée audio.

## Schema (JSON)

```json
{
  "schema_version": 1,
  "surah": 1,
  "surah_name_ar": "الفاتحة",
  "verse_count": 7,
  "reciter": "el_ayoun_el_kouchi",
  "reciter_name": "El-Ayoun El-Kouchi",
  "audio_url": "https://server11.mp3quran.net/koshi/001.mp3",
  "audio_duration": 56.78,
  "marked_at": "2026-05-12T18:00:00.000Z",
  "marks": [4.123, 8.456, 12.789, ...],
  "timings": [
    { "verse": 1, "start": 0, "end": 4.123 },
    { "verse": 2, "start": 4.123, "end": 8.456 },
    ...
  ],
  "complete": true
}
```

## Dépendances data

- `../../data/surahs.json` — métadonnées 114 sourates
- `../../data/quran_muhammadi.json` — versets Muhammadi (filtré au runtime par sourate)

## Raccourcis (bonus desktop)

`Space` play/pause · `M` / `→` mark · `Z` / `←` undo · `↑/↓` ±1s
