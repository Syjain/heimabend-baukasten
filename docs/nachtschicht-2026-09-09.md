# Nachtschicht 08./09.09.2026 – was eingearbeitet wurde und was du entscheiden musst

Grundlage: das Prüfdokument in `docs/pruefung-2026-09/` (73 Fragen), die beiden
Recherchen in `docs/recherche-*.md`, der Entwurf `docs/eigene-ideen-erfassen.md`
und der Vorschlag `docs/gemeinsam-sammeln.md`. Gearbeitet haben sechs Agenten auf
getrennten Dateien; jede Änderung ist committet und einzeln rückgängig zu machen.

**Der Grundsatz der Nacht: Es wurde nichts gelöscht.** Aussortiert wird über das
neue Feld `kern` und über `data/redaktion.json` – beides sind Textzeilen mit
Begründung, die du streichen kannst.

---

## 1. Was sich geändert hat

| | vorher | nachher |
|---|---:|---:|
| Elemente | 1037 | 1075 |
| davon in der ersten Reihe („geprüfte Auswahl") | – | 580 |
| Spiele in der ersten Reihe | – | 299 |
| Bausteine für den Eröffnungskreis | 0 | 8 |
| Methoden zur Gruppeneinteilung | 1 | 11 |
| Bausteine für Auswertung und Reflexion | 2 | 14 |
| Prüfungen im Rauchtest | 54 | 111 |

### Aufgeräumt (Prüfdokument Teil B und C)

- **64 Dubletten-Cluster zusammengelegt.** Das Hauptelement führt die anderen
  Fassungen unter `varianten`; in der App stehen sie als „Auch bekannt als" mit
  anklickbarem Titel. Bei unverträglichen Lizenzen wandert **kein** fremder Text
  ans Hauptelement – nur der Titel, und jede Fassung bleibt bei ihrer eigenen
  Quelle und Lizenz.
- **23 Paare sind Falschtreffer** und stehen jetzt unter `keine_dublette`, damit
  sie nie wieder zusammengeworfen werden. Beispiele: drei verschiedene
  Drachenschwanz-Spiele, zwei Spiele namens „Welle" (Rückenmassage gegen
  Vertrauenslauf), „Katze und Maus" als Raster- und als Kreisspiel.
- **96 Elemente ab 75 Minuten** sind jetzt `umfang: ganzer_abend` statt Baustein.
- **11 Anlässe** vom Kindergeburtstag auf den Heimabend umgedeutet (als Hinweis,
  ohne den Quelltext zu ändern).
- **7 reine Online-Elemente** in die zweite Reihe gestellt.

### Widerlegt

- **Die sechs „Alkohol-/Trinkspiele" gibt es nicht.** Alle Treffer des
  Prüfdokuments sind Wortfehler: „Schnapsen" und „Bauernschnapsen" sind
  Kartenspiele, „Bierbank" und „Bierkiste" sind Möbel, „Bierdeckel" ist
  Wurfmaterial, und der Casino-Heimabend schreibt selbst „Cocktails (ohne
  Alkohol!)". Es wurde nichts gesperrt.
- **Fünf Begriffsfragen sind gegenstandslos.** „Truppstunde", „Stufenstunde",
  „Jungschar", „Ranger" und „Biber" kommen kein einziges Mal vor, „Horde" nur
  als Hordentopf. Die Fragen 23, 25, 27 und 44 der Arbeitsliste erledigen sich.
- **„Uniform" darf nicht durch „Kluft" ersetzt werden.** Im Probenbuch steht:
  die Kluft sei keine Uniform. Ein mechanisches Ersetzen hätte den Satz zerstört.
- **`uebt` trifft 21 Spiele, nicht 76.** Die 76 aus der Recherche waren
  Stichwortfehler: „Feuer, Wasser, Sturm" übt kein Feuer, der Gordische Knoten
  keinen Knoten, die Mordkarte bei Werwolf keine Kartenkunde. Im Bestand gibt es
  schlicht fast keine Knoten- und Feuerspiele – das ist ein Befund, kein Fehler.

### Neu gebaut

- **Feld `kern`** (erste/zweite Reihe) mit Quoten je Unterkategorie; die Zahlen
  des Prüfdokuments werden auf ein Spiel genau getroffen. Ein Eintrag in
  `redaktion.json` unter `kern` schlägt die Automatik in beide Richtungen.
- **Vier neue Achsen für Spiele:** `platz` (Tisch/Zimmer/Saal oder Wiese/Gelände –
  620 von 622 Spielewiki-Spielen, aus Infobox-Feldern, die der Import bisher
  wegwarf), `hosensackspiel` („5 Minuten übrig", 187 Spiele), `uebt` (welche
  Probe ein Spiel nebenbei übt) und `naehe` (wie viel Körperkontakt – der Filter
  für eine neue Gruppe, 77 Spiele „hoch").
- **38 eigene Bausteine** für die Stellen, an denen nichts stand: Eröffnungskreis,
  Schlusskreis, Gruppeneinteilung, Auswertung. Alle in eigenen Worten, ohne
  fremde Texte, ohne Liedtitel, und bewusst so geschrieben, dass sie von deinen
  Sprachentscheidungen unabhängig sind (kein „Sippe", kein „Gruppenstunde").
- **In der App:** Schalter „geprüfte Auswahl / ganze Sammlung", die drei neuen
  Filter, „Spiele, die das üben" an jeder Probe, und Eröffnungs- und Schlusskreis
  als Plätze, die man füllen kann.
- **Eigene Ideen erfassen** (der Entwurf vom 03.09., den du auf später verschoben
  hattest): Knopf „+ Idee", die Idee läuft danach wie jeder andere Baustein durch
  Suche, Filter, Zufall und Planer. „Meine Ideen sichern" schreibt eine Datei, die
  nach `data/eigene/meine-ideen.json` gehört – ab dann steckt die Idee in
  `elemente.json` und ist auf allen Geräten da. Zu tippen sind zwei Zeilen: Titel
  und Beschreibung. Selbst erfasste Ideen stehen immer in der ersten Reihe.

### Zwei Fehler in der Kern-Auswahl behoben

Die Punktzahl aus der Analyse maß, wie vollständig eine Quelle ihre Felder
ausgefüllt hat – nicht, ob ein Spiel taugt. Zwei Folgen davon sind repariert:

1. **Ein Spiel, das mehrere Sammlungen unabhängig voneinander führen, ist ein
   Klassiker.** Das zählte gar nicht. Jetzt gibt es dafür Punkte: von den 64
   zusammengelegten Spielen stehen 47 statt 25 in der ersten Reihe.
2. **Zwölf Klassiker bekamen drei Punkte Abzug**, weil ihre Quelle zusätzlich
   eine Online-Variante nennt – Montagsmaler, Scharade, Wer bin ich,
   Menschenmemory, Ich packe meinen Koffer. Ein Zusatz ist kein Mangel. Der
   Abzug greift jetzt nur noch, wenn das Spiel wirklich ans Netz gebunden ist.

Trotzdem gilt, was schon im Prüfdokument steht: **die Reihenfolge ist ein
Vorschlag, kein Urteil.** Dein Bauchgefühl für ein Spiel, das im Heim immer
funktioniert, schlägt jede Punktzahl – und es umzudrehen kostet eine Zeile.

---

## 2. Was du entscheiden musst

### Sprache – fünf Fragen, alle mit Zahlen und Empfehlung in `docs/sprache.md`

☐ Heißt die kleine Gruppe **Sippe** oder **Horte/Gilde**? (88 Elemente, 227 Fundstellen)
☐ Heißt die Rolle im Spieltext **Spielleitung** oder **Gruppenführer**? (203 Elemente)
☐ Welche **Genderschreibweise** gilt? (Das Probenbuch benutzt die Paarform – die kostet 0 Elemente Änderung.)
☐ **Tonfall**: neutrale Beschreibung oder Ansprache an den Gruppenführer?
☐ Dürfen **fremde Texte** sprachlich umgeschrieben werden? (Lizenzen erlauben es mit Änderungshinweis; das Probenbuch ist der Sonderfall.)

Diese fünf hängen zusammen und blockieren die restliche Sprachaufräumerei.
Alles andere in dieser Nacht wurde so gebaut, dass es von ihnen unabhängig ist.

### Verdichtung

☐ **Zielgröße 300 bestätigen?** Umgesetzt sind 299 Spiele in der ersten Reihe.
☐ **40 Spiele brauchen 15 Personen oder mehr.** Für eine Horte ab 5 unbrauchbar.
   Zweite Reihe, Filter, oder so lassen? (Spitzenreiter brauchen 25 Mitspielende.)
☐ **12 Elemente mit Vorbereitung „hoch"** – für den Wochen-Heimabend realistisch?
   (6 Spiele, 6 Nicht-Spiele; das Prüfdokument zählte nur die Spiele.)
☐ **`insp-behelfs-schutzmasken-naehen`** ist reiner Corona-Zeitbezug, aber kein
   Online-Spiel. Auch in die zweite Reihe?
☐ Die Quoten je Unterkategorie durchsehen: Ist Gelände mit 10 zu knapp,
   sind team mit 39 und namen mit 27 zu großzügig?

### Passung zum Heimabend

☐ **Altersstufen**: bei den drei Stufen bleiben oder auf die DPB-Stände umstellen?
   617 Elemente haben gar keine Angabe – bisher gilt „ohne Angabe = alle Stufen".
☐ **912 Elemente ohne Tipps für die Spielleitung** – wenigstens für die erste
   Reihe nachpflegen?
☐ **51 Elemente setzen Lieder voraus.** Welches Liederbuch benutzt ihr?
☐ Spiele mit **Ausschluss-Mechanik** (wer raus ist, sitzt 10 Minuten am Rand)
   kennzeichnen oder aussortieren?

### Rechte

☐ **Das Probenbuch als PDF liegt in `docs/`, ist aber bewusst nicht committet**
   (`.gitignore`). Das Repo ist öffentlich; ein Scan des Bundes-Probenbuchs dort
   zu veröffentlichen ist eine Entscheidung, die ich nicht für dich treffe. Die
   28 daraus abgeleiteten Elemente sind davon unberührt und tragen ihren
   Rechtevermerk.

### Ausbau (bewusst nicht gemacht)

☐ **Scoutopedia (399 französische Spiele), Baden-Powell (~15 Klassiker),
   Methodenkartei.** Der ganze Befund lautet, dass wir mit 794 Spielen zu viele
   haben und auf 300 verdichten. 399 weitere zu importieren, während wir
   eindampfen, wäre gegenläufig – deshalb heute Nacht nicht angefasst. Sinnvoll
   wird das erst, wenn die Sammlung aufgeräumt ist, und dann gezielt: Nacht- und
   Lagerfeuerspiele, wo wir dünn sind.
☐ **Gemeinsam sammeln (Supabase).** Bleibt blockiert, bis du ein Supabase-Projekt
   in Frankfurt anlegst und Project URL und anon key lieferst. Schema und
   Entscheidungspapier liegen bereit.

---

## 3. Wie du etwas zurückdrehst

Alles Redaktionelle steht in `data/redaktion.json` mit Begründung. Zeile
streichen, `python3 scripts/build.py` laufen lassen, fertig.

| Was | Wo |
|---|---|
| Element gehört doch in die erste Reihe | `kern` → `{"id": "...", "kern": true, "grund": "..."}` |
| Zwei Spiele sind doch nicht dasselbe | Eintrag aus `zusammengelegt` löschen, unter `keine_dublette` eintragen |
| Dauer, Umfang, Ort, Kategorie falsch | `korrekturen` → `felder` |
| Eine neue Achse liegt falsch | `achsen` → `{"id": "...", "felder": {"naehe": "hoch"}}` |

Nach jeder Änderung: `python3 scripts/build.py` (baut `data/elemente.json` und
`web/elemente.js` neu) und danach `scripts/rauchtest.js` in der Browser-Konsole
(111 Prüfungen). Push auf `main` veröffentlicht sofort.
