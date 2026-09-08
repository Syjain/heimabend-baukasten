# Einheitliches Datenmodell: „Element“

Jeder Baustein (Spiel, Pfadfindertechnik, Werken, Kochen …) wird zu einem **Element**
mit denselben Feldern. Alle Quellen werden auf dieses Schema gemappt und in
`data/elemente.json` zusammengeführt.

```jsonc
{
  "id": "ps-kotzendes-kaenguru",          // eindeutig, Präfix = Quelle: eig- (eigene), mein- (in der App selbst erfasst), insp- (Inspirator), ps- (pfadfinder-spiele.de), sw- (Spielewiki), pb- (Probenbuch)
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
  "platz": "zimmer",                      // nur Spiele: tisch | zimmer | saal_wiese | gelaende | ""
  "hosensackspiel": true,                 // nur Spiele: ohne alles, jederzeit spielbar
  "uebt": [],                             // nur Spiele: welche Probe das Spiel nebenbei übt
  "naehe": "keine",                       // nur Spiele: keine | leicht | hoch
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
  "kern": true,                           // erste Reihe (true) oder zweite Reihe (false)
  "varianten": [                          // von Hand zusammengelegte Fassungen desselben Spiels
    {"titel": "Kotzendes Känguru", "id": "sw-kotzendes-kaenguru", "aenderung": ""}
  ],
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

Seit dem 08.09.2026 kommen vier weitere Achsen dazu (`platz`, `hosensackspiel`, `uebt`,
`naehe`) – siehe den nächsten Abschnitt.

Leere Listen bzw. `frei`/`ohne_gewinner` heißen: aus der Quelle nicht erkennbar – nicht
„trifft nicht zu". Bei Nicht-Spielen sind die Felder leer. Die Ableitung wird bewusst
**nicht** an die Planer-Slots gekoppelt (jedes kurze Spiel ist dort „einstieg"), das
würde die Achse entwerten. Grenzfälle korrigiert `data/redaktion.json` unter `achsen`
(`{"id": …, "felder": {"modus": "kooperation"}}`).

## Vier weitere Achsen für Spiele (seit 08.09.2026)

Die Recherche `docs/recherche-kategorien-anderer-sammlungen.md` hat vier Fragen gefunden,
die andere Sammlungen beantworten und wir bisher nicht. Sie werden wie die fünf Achsen
oben abgeleitet: **Quellfeld → Tags → Text → `data/redaktion.json` unter `achsen`**.

| Feld | Frage | Werte | Ableitungsregel | Stand |
|---|---|---|---|---|
| `platz` | Wieviel Platz braucht es? | `tisch` · `zimmer` · `saal_wiese` · `gelaende` · `""` | Zuerst das Spielewiki-Infoboxfeld **`Ort`** (632 Seiten; das ist kein drinnen/draußen, sondern der Platzbedarf: „am Tisch“, „kleine Spielfläche“, „Spielfeld“, „überall“). Danach `unterkategorie` `gelaende`/`tisch` bzw. der Tag „Geländespiel“. Zuletzt der Text (Wald, Turnhalle, Stuhlkreis, Gruppenraum). | 08.09.2026 |
| `hosensackspiel` | Geht es aus der Hosentasche? | `true` · `false` | Kein Material **und** Vorbereitung `gering` **und** (`dauer_max` ≤ 10 **oder** die Spielewiki-Dauer sagt „pro Runde“/„beliebig“, ist also rundenweise dehnbar). Begriff von jubla.netz. | 08.09.2026 |
| `uebt` | Welche Probe übt es nebenbei? | Liste aus `knoten` · `karte_kompass` · `feuer` · `erste_hilfe` · `zelte_bauten` · `natur` · `bundeskunde` · `fahrtentechnik` | Enge Wendungen in Titel, Tags, Themen, Beschreibung, Tipps und Material („Knoten knüpfen“, „Erste Hilfe“, „Waldläuferzeichen“). Wortlisten-Spiele (Tabu, Quiz, Memory, Montagsmaler) sind ganz ausgeschlossen, ebenso Zufallstreffer wie „Feuer, Wasser, Sturm“, „Gordischer Knoten“, Spielkarten und Zeltstangen. | 08.09.2026 |
| `naehe` | Wieviel Körperkontakt und Vertrauen verlangt es? | `keine` · `leicht` · `hoch` · `""` | `hoch`: `wirkung: vertrauen` bzw. Tag Vertrauensspiel, verbundene Augen, huckepack/getragen werden, Massage, sich fallen lassen, allein vor der Gruppe. `leicht`: Hände halten, Namen rufen, sich vorstellen, unterhaken, Namens- und Kennenlernspiele. Sonst `keine`. | 08.09.2026 |

Bei Nicht-Spielen sind alle vier leer (`""`, `[]`, `false`).

**Warum die Muster so eng sind.** Die naheliegende Regex auf Berührungswörter (anfassen,
umarmen, huckepack, tragen, Schoß) trifft rund 190 Spiele – weil in jedem Fangspiel steht
„wer berührt wird, ist gefangen“ und „vorstellen“ meistens „sich etwas vorstellen“ heißt.
Deshalb stehen in `naehe` nur ausformulierte Wendungen, keine einzelnen Wortstämme.
Dasselbe bei `uebt`: die lose Suche nach Knoten/Kompass/Karte/Feuer/Zelt/Spur/Natur trifft
97 Spiele, von denen fast keines wirklich eine Probe übt (Kartenspiele, „Feuer, Wasser,
Sturm“, „Gordischer Knoten“, die Mordkarte bei Werwolf).

**Bewusst offen:** Kimspiele üben Beobachten und Merken, aber keine der acht Proben. Sie
bekommen deshalb kein `uebt`; eine eigene Achse „Wahrnehmung“ wäre ehrlicher, als sie
unter `natur` zu verstecken.

Grenzfälle korrigiert `data/redaktion.json` unter `achsen`, genau wie bei den fünf Achsen:
`{"id": "sw-ha-ha-ha", "felder": {"naehe": "hoch"}, "grund": "…"}`.

## Zwei Reihen statt Löschen: `kern`

Mit 1037 Elementen ist die Sammlung vollständig, aber unübersichtlich – und in vielen
Unterkategorien liegen dieselben drei Spielideen zehnmal. Trotzdem wird **nichts gelöscht**:

| Feld | Werte | Ableitungsregel | Stand |
|---|---|---|---|
| `kern` | `true` (erste Reihe) · `false` (zweite Reihe) | Nicht-Spiele immer `true`. Spiele: Punktbewertung (eigene Sammlung, Länge der Beschreibung, Altersstufe, Tipps, Dauer, Material, Vorbereitung, Gruppengröße, Corona/Alkohol/Party-Abzug) und dann je `unterkategorie` eine Quote, Ziel 300 Kern-Spiele. Zusammengelegte Varianten und zweite Fassungen einer Dublette sind nie Kern. `data/redaktion.json` unter `kern` schlägt beides – in beide Richtungen. | 08.09.2026 |
| `varianten` | Liste aus `{"titel", "id", "aenderung"}` | Aus `data/redaktion.json` unter `zusammengelegt`. Das Hauptelement bekommt die Liste, die Varianten bleiben als eigene Elemente erhalten und bekommen `kern: false`. | 08.09.2026 |

**Warum das umkehrbar ist.** `kern: false` ist keine Löschung, sondern ein Filter: Das
Element steht mit allen Feldern, seiner Quelle und seiner Lizenz weiter in
`data/elemente.json`. Die App zeigt standardmäßig die erste Reihe und blendet die zweite
auf Wunsch dazu. Wer eine Entscheidung anders sieht, schreibt eine Zeile mit Begründung in
`data/redaktion.json` – der nächste `python3 scripts/build.py` dreht sie um. Ein gelöschtes
Element wäre dagegen beim nächsten Importlauf entweder ganz weg oder unbemerkt wieder da,
weil die Import-Skripte idempotent sind.

Die Punkte und die Quotenrechnung stehen auf Modulebene in `scripts/build.py`
(`kern_punkte`, `kern_quoten`) und sind aus `scripts/analyse.py`, Teil C, übernommen, damit
Prüfung und Build dasselbe rechnen. Die Zuteilung ist stabil: sortiert wird nach
(−Punkte, entschärfter Titel, id), die Unterkategorien in der Reihenfolge (−Anzahl, Name).
Gleiche Eingabe, gleiches Ergebnis – kein Zufall.

**Lizenzregel beim Zusammenlegen (wichtig!).** Stehen in einem Cluster CC BY-SA und
CC BY-NC(-SA) nebeneinander, trägt der Redaktionseintrag `"lizenzen_unvertraeglich": true`.
Dann stehen in `varianten` nur **Titel und id** der anderen Fassung, `aenderung` bleibt
leer. Es wandert kein Text der anderen Quelle in das Element. Ein `aenderung`-Text ist
immer ein selbst geschriebener Satz, nie ein Zitat.

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

## Selbst erfasste Ideen (seit 09.09.2026)

Die App kann eigene Ideen aufnehmen (Knopf „+ Idee"). Sie liegen zunächst nur im
Browser (`localStorage`), tragen den Präfix `mein-` und sind vollständige Elemente
nach diesem Schema. „Meine Ideen sichern" schreibt sie als Datei im selben Aufbau
wie `data/eigene/rahmen-und-methoden.json`; kommt die Datei nach
`data/eigene/meine-ideen.json`, liest `build.py` sie beim nächsten Lauf mit ein.

Zwei Besonderheiten:

- Selbst erfasste Ideen sind **immer** `kern: true`. Wer eine Idee aufschreibt,
  will sie wiederfinden und nicht hinter dem Schalter suchen; sie stammen auch aus
  keiner Quelle, die man verdichten müsste.
- Ihre `slots` bleiben stehen, statt neu berechnet zu werden – die App leitet sie
  beim Erfassen mit derselben Regel ab wie `slots_fuer()` und lässt sie von Hand
  ändern. Dasselbe gilt für `rahmen-und-methoden.json`.

Die neun Spiel-Achsen fragt das Formular nicht ab: Ein Formular kann sie nicht
ehrlich beantworten. Sie bleiben leer („nicht erkennbar") und werden beim
nächsten `build.py`-Lauf aus dem Text abgeleitet wie bei jeder anderen Quelle.

## Redaktion

`data/redaktion.json` hält fest, was aus den Quellen herausfällt (`gesperrt`),
umbenannt wird (`umbenannt`), an Feldern korrigiert wird (`korrekturen`), welchem
Bereich es zugeordnet wird (`bereiche`) und welche Dubletten zusammen- bzw. nicht
zusammengehören (`auch_dublette`, `keine_dublette`). Jeder Eintrag hat eine
Begründung. Ohne diese Datei holt der nächste Importlauf alles wieder herein,
weil die Import-Skripte idempotent sind.

Die Schlüssel im Überblick:

| Schlüssel | Wirkung |
|---|---|
| `gesperrt` | Element fällt ganz heraus |
| `umbenannt` | neuer Titel |
| `korrekturen` | einzelne Felder setzen, Hinweis in `tipps` voranstellen |
| `bereiche` | Bereich/Kategorie von Hand, schlägt die Automatik |
| `achsen` | einzelne Achsen von Hand: `{"id": …, "felder": {"platz": "zimmer"}, "grund": "…"}` – nimmt jeden Feldnamen, auch `hosensackspiel`, `uebt`, `naehe` |
| `auch_dublette` / `keine_dublette` | Dublettengruppen verbinden bzw. wieder lösen |
| `zusammengelegt` | `{"haupt": "sw-x", "varianten": ["ps-y"], "lizenzen_unvertraeglich": true, "aenderungen": {"ps-y": "eigener Satz"}, "grund": "…"}` – setzt `varianten` beim Hauptelement, `kern: false` bei den Varianten |
| `kern` | `{"id": "sw-x", "kern": false, "grund": "…"}` – Handentscheidung, schlägt die Punkte in beide Richtungen |

Alle Schlüssel sind freiwillig: Fehlt einer, läuft `scripts/build.py` sauber durch.
