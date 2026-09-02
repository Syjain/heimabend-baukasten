# Einheitliches Datenmodell: „Element“

Jeder Baustein (Spiel, Probe, Aktivität, Projekt) wird zu einem **Element** mit denselben Feldern.
Alle Quellen werden auf dieses Schema gemappt und in `data/elemente.json` zusammengeführt.

```jsonc
{
  "id": "ps-kotzendes-kaenguru",          // eindeutig, Präfix = Quelle: eig- (eigene), insp- (Inspirator), ps- (pfadfinder-spiele.de), sw- (Spielewiki), sr- (Spielereader)
  "titel": "Kotzendes Känguru",
  "element_typ": "spiel",                 // spiel | probe | aktivitaet | projekt
  "kategorie": "kreis",                   // siehe Kategorien unten
  "slots": ["einstieg", "abschluss"],     // wo im Heimabend passt es: eroeffnung | einstieg | hauptteil | aktivitaet | abschluss
  "altersstufen": ["Wölflinge", "Pfadfinder"],   // Wölflinge (ca. 7–11) | Pfadfinder (ca. 11–16) | Ältere (16+)
  "alter_ab": 6,                          // optional, Mindestalter in Jahren
  "dauer_min": 10,                        // Minuten
  "dauer_max": 20,
  "ort": "beides",                        // drinnen | draussen | beides
  "gruppe_min": 6,                        // optional
  "gruppe_max": 25,                       // optional
  "material": ["Nichts"],                 // Liste, leer = kein Material
  "vorbereitung": "gering",               // gering | mittel | hoch
  "kurz": "Kreisspiel mit Kommandos und Gesten …",   // 1–2 Sätze
  "beschreibung": "…",                    // Ablauf/Regeln als Text (Markdown erlaubt)
  "tipps": "…",                           // optional
  "tags": ["Warm-up", "ohne Material"],
  "themen": ["Knoten"],                   // nur für probe/projekt: Pfadfinderwissen-Themen
  "quelle": {
    "name": "pfadfinder-spiele.de",
    "url": "https://pfadfinder-spiele.de/kotzendes-kaenguru/",
    "autor": "Dorothea Schümann",
    "lizenz": "CC BY-NC-SA 4.0"           // exakt, wird in der App angezeigt
  }
}
```

## Element-Typen und Kategorien

**spiel** – ein einzelnes Spiel, 5–45 Minuten
- `ankommen` – Kennenlernen, Namen, Warm-up
- `bewegung_drinnen` – Toben im Heim
- `bewegung_draussen` – Lauf-, Fang-, Ballspiele draußen
- `gelaende` – Geländespiele, Fahnenraub, Postenläufe (meist länger)
- `kreis` – Kreisspiele, Reaktion, Konzentration
- `ruhig` – Rätsel, Kim-Spiele, Erzählspiele, Denkspiele
- `kooperation` – Team- und Vertrauensaufgaben
- `abschluss` – kurze, ruhige Spiele zum Ausklang

**probe** – Pfadfinderwissen aus dem Probenbuch, 20–60 Minuten
- Kategorie = Thema: `knoten`, `karte_kompass`, `feuer`, `erste_hilfe`, `zelte_bauten`, `natur`, `bundeskunde` (Geschichte, Symbolik, Versprechen, Lieder), `fahrtentechnik` (Packen, Kochen, Haik), `sonstiges`

**aktivitaet** – Gemeinschaftsaktivität, 30–90 Minuten
- `draussen` (Wald, Spaziergang, Mikroabenteuer), `kreativ` (Basteln, Werken), `kochen`, `musisch` (Singen, Theater), `soziales` (gute Tat, Gespräch)

**projekt** – füllt einen ganzen Heimabend (hier landen die Inspirator-Ideen und die meisten eigenen Themenabende)
- Kategorie = Hauptthema (frei, aus `themen`)

## Lizenz-Regeln (wichtig!)

- Jedes Element trägt seine Lizenz in `quelle.lizenz`. Die App zeigt Quelle + Lizenz bei jedem Element an.
- CC BY-SA und CC BY-NC-SA sind **nicht kompatibel**: Texte verschiedener Quellen nie zu einem Element mischen.
- Sobald NC-Inhalte (Inspirator, pfadfinder-spiele.de) enthalten sind, bleibt das Tool **nicht-kommerziell** (kein Verkauf, keine Werbung).
- ShareAlike: die eigene Sammlung wird unter CC BY-SA 4.0 (eigene Inhalte) bzw. je Element unter der Quell-Lizenz veröffentlicht.

## Mapping der Quellen

| Quelle | element_typ | Mapping-Hinweise |
|---|---|---|
| eigene (`data/eigene/heimabend-ideen.json`) | je nach Kategorie: Spiel & Action mit dauer ≤45 → `spiel`; Pfadfindertechnik → `probe`; Draußen/Kreativ/Kochen/Musisch/Gruppe → `aktivitaet`; Themenabende und alles ≥90 min → `projekt` | Felder passen fast 1:1 |
| Inspirator (`data/quellen/inspirator/inspirator-ideen.json`) | `projekt` (Ausnahme: `arten` = nur „Spiel“ und dauer <30 → `spiel`) | `stufen`: Rover → Ältere; `orte`: Drinnen/Draußen/Wald/Garten/Ausflug → ort; `dauer_min/max` vorhanden; `themen` übernehmen; `vorbereitung`: keine/5 → gering, 30 → mittel, 60/>60 → hoch |
| pfadfinder-spiele.de (REST-API, ACF-Felder) | `spiel` | `spielart` → kategorie (Warm up/Kennenlernspiel → ankommen, Kreisspiel → kreis, Bewegungsspiel + Draußen → bewegung_draussen, Konzentrationsspiel/Denkspiel → ruhig, Kooperationsspiel → kooperation); `umgebung` → ort; `alter` → alter_ab; `ungefahre_dauer` → dauer_min/max; `gruppengrose` → gruppe_min/max |
| Spielewiki (XML-Export, Infobox) | `spiel` | Infobox-Felder Art, Spieleranzahl, Ort, Material, Dauer, Vorbereitung; Alter fehlt → altersstufen leer lassen (= „alle“) |
