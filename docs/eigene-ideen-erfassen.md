# Eigene Ideen in der App erfassen (Entwurf)

Stand: 03.09.2026 · noch nicht gebaut, erst zur Entscheidung

## Das Problem

Die App ist eine statische Datei ohne Server. Es gibt keine Datenbank, in die
etwas geschrieben werden könnte, und keine Anmeldung. Trotzdem soll man eigene
Heimabend-Ideen erfassen können – und zwar so, dass sie nicht verloren gehen,
wenn der Browser aufgeräumt wird oder das Handy wechselt.

## Vorschlag: zwei Stufen

**Stufe 1 – sofort nutzbar (im Browser).**
Eine neue Idee wird über ein Formular erfasst und in `localStorage` abgelegt.
Sie erscheint ab dann in Suche, Kacheln, Filtern und im Planer wie jeder andere
Baustein, nur mit einer Plakette „eigene Idee". Bearbeiten und Löschen gehen
jederzeit. Das reicht für „mir fällt gerade etwas ein, das will ich nicht
vergessen".

**Stufe 2 – dauerhaft (im Projekt).**
Ein Knopf „Meine Ideen sichern" lädt alle eigenen Ideen als JSON-Datei
herunter. Diese Datei kommt nach `data/eigene/meine-ideen.json`, und
`scripts/build.py` liest sie beim nächsten Lauf mit ein. Danach stecken die
Ideen in `data/elemente.json` und sind auf allen Geräten da – auch auf
GitHub Pages, auch in einer späteren Flutter-App.

Ein Gegenstück „Datei einlesen" holt eine gesicherte Datei zurück in den
Browser, etwa nach einem Gerätewechsel.

Damit ist der Weg: **erfassen → benutzen → sichern → einbauen.**
Ohne Server geht es nicht kürzer, und dieser Weg verliert nichts.

## Das Formular

Pflicht sind nur fünf Angaben, alles andere hat sinnvolle Vorbelegungen –
sonst schreibt niemand etwas ein:

| Feld | Eingabe | Vorbelegung |
|---|---|---|
| Titel | Textzeile | – |
| Art | Auswahl: Spiel / Probe / Aktivität / Projekt | Spiel |
| Kategorie | Auswahl, hängt an der Art | erste der Art |
| Dauer | zwei Zahlen (von/bis) in Minuten | 10 / 20 |
| Beschreibung | mehrzeiliger Text | – |
| Kurztext | Textzeile | erster Satz der Beschreibung |
| Unterkategorie | Auswahl, hängt an der Kategorie | leer |
| Altersstufen | Mehrfachauswahl | keine = alle Stufen |
| Ort | drinnen / draußen / beides | beides |
| Material | Textzeile, mit Komma getrennt | leer = ohne Material |
| Vorbereitung | gering / mittel / hoch | gering |
| Gruppengröße | zwei Zahlen, freiwillig | leer |
| Tipps | mehrzeiliger Text, freiwillig | leer |
| Slots | Mehrfachauswahl: Einstieg / Hauptteil / Abschluss | aus Art und Dauer abgeleitet |

Die Slots kann die App genauso ableiten wie `build.py` es für die importierten
Quellen tut (kurze Spiele → Einstieg und Abschluss, alles → Hauptteil). Wer
mag, korrigiert es von Hand.

## Wie die Daten aussehen

Eigene Ideen benutzen dasselbe Schema wie alles andere (`data/SCHEMA.md`),
damit nichts umgerechnet werden muss:

```jsonc
{
  "id": "mein-knotenstaffel-1757030400000",   // Präfix "mein-" plus Zeitstempel
  "titel": "Knotenstaffel im Dunkeln",
  "element_typ": "spiel",
  "kategorie": "kooperation",
  "unterkategorie": "wettkampf",
  "slots": ["hauptteil"],
  "altersstufen": ["Pfadfinder"],
  "dauer_min": 15, "dauer_max": 25,
  "ort": "drinnen",
  "material": ["Seile", "Stirnlampen"],
  "vorbereitung": "gering",
  "kurz": "Knoten auf Zeit, nur mit Stirnlampe.",
  "beschreibung": "…",
  "tipps": "",
  "tags": ["eigene Idee"],
  "themen": [],
  "quelle": {
    "name": "eigene Idee",
    "url": "",
    "autor": "",                      // bleibt leer, kein Zwang zum Namen
    "lizenz": "CC BY-SA 4.0"
  },
  "erstellt": "2026-09-03",           // nur bei eigenen Ideen
  "geaendert": "2026-09-03"
}
```

Das Präfix `mein-` reiht sich in die bestehenden ein (`eig-`, `insp-`, `ps-`,
`sw-`, `pb-`). Der Zeitstempel in der ID verhindert Zusammenstöße, wenn zwei
Leute unabhängig eine Idee mit demselben Titel anlegen.

## Was in der App dazukommt

- **Knopf „+ Eigene Idee"** in der Baustein-Ansicht, oben neben „Zufall".
- **Formular als Überlagerung**, gleiche Bauart wie die Detailansicht.
- **Eigene Ideen in der Detailansicht** bekommen zwei zusätzliche Knöpfe:
  „Bearbeiten" und „Löschen" (Löschen mit Rückfrage).
- **Kachel „Eigene Ideen (N)"** auf der Startebene, damit man sie schnell findet.
- **Plakette „eigene Idee"** auf der Karte, so wie jetzt der Quellname bei
  Dubletten steht.
- **Im Filter-Klappfeld**: „Meine Ideen sichern" und „Datei einlesen".

## Was schiefgehen kann, und was dagegen hilft

- **Browserdaten werden gelöscht → Ideen weg.** Deshalb Stufe 2. Zusätzlich
  ein Hinweis in der App, sobald mehr als drei eigene Ideen ungesichert sind.
- **`localStorage` ist voll** (meist etwa 5 MB). Bei rund 2 KB je Idee reicht
  das für über tausend, aber der Schreibvorgang muss trotzdem in `try/catch`
  laufen und bei Fehlschlag ehrlich melden: „konnte nicht gespeichert werden".
- **Doppelte Ideen nach dem Einbauen.** Wenn eine Idee über `build.py` in
  `data/elemente.json` gelandet ist, steckt sie auch noch im Browser. Lösung:
  Beim Start prüft die App, ob eine ID aus dem Browser schon in den geladenen
  Daten steckt; wenn ja, gewinnt die Datei und die Kopie im Browser wird
  stillschweigend verworfen. Deshalb ist die stabile ID wichtig.
- **Kaputter Inhalt im Browserspeicher.** Beim Lesen jede Idee gegen die
  Pflichtfelder prüfen und Unbrauchbares überspringen, statt die App abstürzen
  zu lassen.
- **Lizenz.** Eigene Ideen sind eigene Inhalte, Vorschlag CC BY-SA 4.0 wie die
  übrige eigene Sammlung. Wichtig: Beim Erfassen keine Texte aus fremden
  Quellen einfügen, die unter „nur verlinken" in `docs/datenquellen.md` stehen.
  Ein kurzer Hinweis dazu gehört unter das Formular.

## Aufwand

| Schritt | Umfang |
|---|---|
| Formular, Speichern und Lesen im Browser | etwa 200 Zeilen |
| Eigene Ideen in Liste, Kacheln, Filter, Planer einhängen | etwa 40 Zeilen |
| Bearbeiten und Löschen | etwa 60 Zeilen |
| Sichern und Einlesen als Datei | etwa 60 Zeilen |
| `build.py` liest `data/eigene/meine-ideen.json` mit | etwa 30 Zeilen |
| Rauchtest erweitern | etwa 40 Zeilen |

Alles in derselben `web/index.html`, ohne neue Abhängigkeiten.

## Offene Frage für dich

Sollen mehrere Leute in der Gruppenführung Ideen sammeln und zusammenlegen
können? Mit dem Weg oben geht das über die gesicherten Dateien, die jemand
einsammelt und ins Projekt legt. Bequemer wäre es mit einem kleinen Server –
das wäre aber ein anderes Projekt und würde die Regel „eine statische Datei,
kein Build-Schritt" aus `CLAUDE.md` brechen.
