# Einheitliches Datenmodell: „Element“

Jeder Baustein (Spiel, Pfadfindertechnik, Werken, Kochen …) wird zu einem **Element**
mit denselben Feldern. Alle Quellen werden auf dieses Schema gemappt und in
`data/elemente.json` zusammengeführt.

```jsonc
{
  "id": "ps-kotzendes-kaenguru",          // eindeutig, Präfix = Quelle: eig- (eigene), insp- (Inspirator), ps- (pfadfinder-spiele.de), sw- (Spielewiki), pb- (Probenbuch)
  "titel": "Kotzendes Känguru",
  "bereich": "spiel",                     // WORUM geht es – sieben Werte, siehe unten
  "umfang": "baustein",                   // WIE GROSS – baustein | ganzer_abend
  "kategorie": "kreis",                   // zweite Ebene, nur bei spiel und pfadfindertechnik
  "unterkategorie": "konzentration",      // dritte Ebene, nur bei spiel
  "slots": ["einstieg", "hauptteil"],     // wo im Heimabend: eroeffnung | einstieg | hauptteil | abschluss
  "wirkung": ["ankommen", "konzentration"],   // nur Spiele: wozu setze ich es ein (mehrere)
  "modus": "ohne_gewinner",               // nur Spiele: wettkampf | kooperation | ohne_gewinner
  "sozialform": "kreis",                  // nur Spiele: kreis | paare | mannschaften | einer_gegen_alle | kleingruppen | frei
  "spielgeraet": ["nichts"],              // nur Spiele, aus Material: ball | seil | tuch | stuehle | papier_stift | karten_wuerfel | musik | nichts | sonstiges
  "anforderung": ["bewegung", "konzentration"],   // nur Spiele: bewegung | geschick | denken | merken | konzentration | sprache | rhythmus
  "altersstufen": ["Wölflinge", "Pfadfinder"],   // Wölflinge (ca. 7–11) | Pfadfinder (ca. 11–16) | Ältere (16+); leer = keine Angabe
  "alter_ab": 6,                          // optional, Mindestalter in Jahren
  "dauer_min": 10,
  "dauer_max": 20,
  "ort": "beides",                        // drinnen | draussen | beides
  "gruppe_min": 6,                        // optional
  "gruppe_max": 25,                       // optional
  "material": [],                         // leere Liste = kein Material nötig
  "vorbereitung": "gering",               // gering | mittel | hoch
  "kurz": "Kreisspiel mit Kommandos und Gesten …",
  "beschreibung": "…",                    // Ablauf/Regeln, leichtes Markdown (## Überschrift, - Punkt, **fett**)
  "tipps": "…",                           // Hinweise für die Spielleitung, auch Sicherheitshinweise
  "tags": ["Konzentrationsspiel", "Kreisspiel", "ohne Material"],
  "themen": [],                           // feine Themen der Quelle
  "dubletten": ["sw-toasterspiel"],       // optional: dasselbe Spiel in einer anderen Quelle
  "quelle": {
    "name": "pfadfinder-spiele.de",
    "url": "https://pfadfinder-spiele.de/kotzendes-kaenguru/",
    "autor": "Dorothea Schümann",
    "lizenz": "CC BY-NC-SA 4.0"           // exakt, wird in der App angezeigt
  }
}
```

## Zwei Achsen statt einer

Bis 03.09.2026 gab es ein Feld `element_typ` mit den Werten `spiel`, `probe`,
`aktivitaet` und `projekt`. Das hat **zwei unabhängige Fragen vermischt**:

- *Worum geht es?* (ein Spiel, Pfadfinderwissen, etwas herstellen)
- *Wie groß ist es?* (ein Baustein im Abend oder ein ganzer Abend)

Die Folge: „Armbänder knüpfen“ (60–90 min) war eine **Aktivität**, „Speckstein-Werkstatt“
(90–120 min) ein **Projekt** – obwohl beides Basteln ist. Und die Projekt-Kategorie
`wissen` wurde zum Sammeleimer, in dem „Kohte blind aufbauen“ neben „Gitarrenkurs“ lag.

Deshalb jetzt zwei Felder:

### `bereich` – worum geht es (sieben Werte)

| Wert | Bedeutung |
|---|---|
| `spiel` | ein Spiel |
| `pfadfindertechnik` | Pfadfinderwissen: Knoten, Karte und Kompass, Feuer, Erste Hilfe, Zelte und Bauten, Naturkunde, Bundeskunde, Fahrtentechnik |
| `natur_draussen` | rausgehen, beobachten, Umwelt |
| `werken` | etwas herstellen: basteln, bauen, schnitzen, nähen, gestalten |
| `kochen` | kochen und backen |
| `musisch` | singen, Musik, Theater, Geschichten, Schreiben |
| `gemeinschaft` | die Gruppe selbst: Gespräch, Reflexion, Beteiligung, gute Tat, Gesellschaft |

Die Einteilung folgt der eigenen Sammlung des Projekts und deckt sich mit der im
Pfadfinderwesen üblichen Gliederung der Pfaditechnik (Pioniertechnik, Orientierung,
Natur, Sicherheit, Bundeskunde, unterwegs sein).

### `umfang` – wie groß ist es

| Wert | Bedeutung |
|---|---|
| `baustein` | passt in einen Platz des Heimabends |
| `ganzer_abend` | füllt den Abend (ab 60 Minuten Mindestdauer bzw. 75 Minuten Regeldauer) |

Der Planer nutzt das: Sind mehrere Plätze im Hauptteil offen, kommen nur Bausteine
in Frage; ein einzelner Platz darf auch mit einem ganzen Abend gefüllt werden.

## Zweite und dritte Ebene

Nur zwei Bereiche haben eine `kategorie`; bei den übrigen ist der Bereich selbst
schon das Thema, und die Navigation geht über den `umfang` weiter.

**`bereich: "spiel"`** – Kategorie:
`ankommen` · `bewegung_drinnen` · `bewegung_draussen` · `gelaende` · `kreis` ·
`ruhig` · `kooperation` · `abschluss`

und `unterkategorie` (22 Werte, aus den Spielarten der Quellen abgeleitet):
`fangen` · `ball` · `geschick` · `kampf` · `wettkampf` · `toben` · `verstecken` ·
`gelaende` · `reaktion` · `konzentration` · `denken` · `merken` · `namen` ·
`vertrauen` · `team` · `reflexion` · `singen` · `darstellen` · `tisch` · `ruhig` ·
`warmup` · `sonstiges`

**`bereich: "pfadfindertechnik"`** – Kategorie:
`knoten` · `karte_kompass` · `feuer` · `erste_hilfe` · `zelte_bauten` · `natur` ·
`bundeskunde` · `fahrtentechnik` · `sonstiges`

Alle anderen Bereiche: `kategorie` und `unterkategorie` sind leer (`""`).

## Fünf Achsen für Spiele (seit 04.09.2026)

Die Spiel-`kategorie` (ankommen, kreis, ruhig, kooperation, bewegung_*, gelaende) mischt
vier Fragen in einem Feld – deshalb war sie nicht trennscharf: 64 Spiele unter
„ruhig/kreis/ankommen/kooperation", in denen gerannt wird. Sie **bleibt als Navigation**
erhalten; daneben beantwortet jede der folgenden Achsen genau eine Frage:

| Feld | Frage | Werte | Herkunft |
|---|---|---|---|
| `wirkung` (mehrere) | Wozu setze ich es ein? | ankommen, kennenlernen, austoben, beruhigen, konzentration, vertrauen, zusammenarbeit, abschluss | Tags der Quellen, dann Text |
| `modus` | Gegeneinander oder miteinander? | wettkampf, kooperation, ohne_gewinner | Text (Gewinner/Punkte vs. Kooperationsaufgabe), Tags |
| `sozialform` | Wie ist die Gruppe aufgestellt? | kreis, paare, mannschaften, einer_gegen_alle, kleingruppen, frei | Text, Tags |
| `spielgeraet` (mehrere) | Was brauche ich in der Hand? | ball, seil, tuch, stuehle, papier_stift, karten_wuerfel, musik, nichts, sonstiges | Feld `material` |
| `anforderung` (mehrere) | Was fordert es von den Kindern? | bewegung, geschick, denken, merken, konzentration, sprache, rhythmus | Tags, dann Text |

Leere Listen bzw. `frei`/`ohne_gewinner` heißen: aus der Quelle nicht erkennbar – nicht
„trifft nicht zu". Bei Nicht-Spielen sind die Felder leer. Die Ableitung wird bewusst
**nicht** an die Planer-Slots gekoppelt (jedes kurze Spiel ist dort „einstieg"), das
würde die Achse entwerten. Grenzfälle korrigiert `data/redaktion.json` unter `achsen`
(`{"id": …, "felder": {"modus": "kooperation"}}`).

## Wie der Bereich bestimmt wird

`scripts/build.py` geht von exakt nach ungefähr vor:

1. **Spielewiki und pfadfinder-spiele.de** liefern ausschließlich Spiele → `spiel`.
2. **Probenbuch** → immer `pfadfindertechnik`, Kategorie aus `PROBENBUCH_ZUORDNUNG`.
3. **Eigene Sammlung** → über die neun eigenen Kategorien (`EIGENE_BEREICH`).
   Ausnahme „Themenabende“, inhaltlich gemischt → Stichworte.
4. **Inspirator** → Abstimmung über sein geschlossenes Themen-Vokabular
   (30 Werte, Tabelle `THEMA_BEREICH`). Gleichstand entscheidet `BEREICH_RANG`.
   Themen, die die Spielform beschreiben („Bewegung“, „Kim-Spiel“, „Detektiv“),
   stimmen nicht mit ab.
5. **Rückfall** → Stichworte in Titel und Tags, zuletzt `gemeinschaft`.

Grenzfälle wurden von Hand durchgesehen; die Entscheidungen stehen mit Begründung
in `data/redaktion.json` unter `bereiche` und schlagen die Automatik.

## Lizenz-Regeln (wichtig!)

- Jedes Element trägt seine Lizenz in `quelle.lizenz`. Die App zeigt Quelle + Lizenz an.
- CC BY-SA und CC BY-NC-SA sind **nicht kompatibel**: Texte verschiedener Quellen
  nie zu einem Element mischen.
- Sobald NC-Inhalte (Inspirator, pfadfinder-spiele.de) enthalten sind, bleibt das
  Tool **nicht-kommerziell** (kein Verkauf, keine Werbung).
- Keine E-Mail-Adressen oder anderen personenbezogenen Daten aus Quellen übernehmen.

## Redaktion

`data/redaktion.json` hält fest, was aus den Quellen herausfällt (`gesperrt`),
umbenannt wird (`umbenannt`), an Feldern korrigiert wird (`korrekturen`), welchem
Bereich es zugeordnet wird (`bereiche`) und welche Dubletten zusammen- bzw. nicht
zusammengehören (`auch_dublette`, `keine_dublette`). Jeder Eintrag hat eine
Begründung. Ohne diese Datei holt der nächste Importlauf alles wieder herein,
weil die Import-Skripte idempotent sind.
