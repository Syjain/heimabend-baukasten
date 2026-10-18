# Nachtschicht Robustheit und Prüfbarkeit (18.10.2026)

Auftrag: Skripte und Daten prüfbar machen, ohne `web/index.html` anzufassen und ohne die
Daten inhaltlich zu ändern. Alles unten ist auf Python 3.9.6 gelaufen (das ist das
`python3` auf diesem Mac).

## Die drei Befehle

    python3 scripts/pruefe.py            # prüft alles, ca. 10 Sekunden, endet mit "OK" oder Problemliste
    python3 scripts/pruefe.py --schnell  # dasselbe ohne die zwei Probeläufe von build.py (ca. 1 Sekunde)
    python3 scripts/test_pruefe.py       # testet den Prüfer selbst: 16 absichtlich eingebaute Fehler müssen auffallen

Die Tests für die App (im Browser, siehe Abschnitt 4):

    python3 -m http.server 8000          # im Repo-Ordner; dann http://localhost:8000/scripts/rauchtest-seite.html öffnen

## 1. Was gebaut wurde

**`scripts/pruefe.py`** (nur Standardbibliothek) prüft in einem Lauf:

| Abschnitt | Prüft |
|---|---|
| Skripte | alle `scripts/*.py` lassen sich mit der Python-3.9-Grammatik lesen; keine `X \| Y`-Typangaben, kein `match`, kein `zip(strict=)` |
| Dateien | jede JSON-Datei unter `data/` ist lesbar (Fehler mit Zeile und Spalte) |
| Redaktion | Form jedes Eintrags von `data/redaktion.json`; **Waisen** (IDs, die es in keiner Quelle gibt, auch bei gesperrten Elementen); Eintrag zeigt auf ein gesperrtes Element; doppelte Einträge; fehlende Begründung; Bereich/Kategorie/Felder gegen das Schema; Lizenzregel bei `zusammengelegt` |
| Sprache | `data/sprache.json`: Form, Waisen in `ausser`, Paare ohne Text, doppelte `von`, Regeln, die in keinem Element greifen |
| Elemente | alles, was `build.py` schon prüft, plus: ID-Form, Lizenz passend zum Präfix, `quelle.url` kaputt, Links und E-Mail-Adressen in Texten, Dubletten gegenseitig, Varianten nie Kern und Lizenzfamilie, Unterkategorie nur bei Spielen und aus der Liste, jeder Wert, den `build.py` erlaubt, steht auch in `data/SCHEMA.md` |
| Web-Datei | `web/elemente.js` (und `web/sprache.js`, falls vorhanden) enthalten dasselbe wie die JSON-Dateien |
| Build | `build.py` zweimal in ein Temp-Verzeichnis: gleiches Ergebnis (idempotent, per SHA-256) und gleich wie die eingecheckten Dateien |

**`scripts/build.py`** (kleine Änderungen, Ausgabe unverändert):
- `lade_json()`: kaputtes JSON führt zu einer deutschen Meldung mit Datei, Zeile, Spalte und Brechen des Laufs *vor* dem Schreiben ("Es wurde nichts geschrieben."), statt zu einem Traceback.
- `formfehler_redaktion()`: fehlendes `id`, `titel`, `ids`, `haupt` … in `redaktion.json` ergibt eine klare Meldung statt `KeyError` mitten im Lauf.
- `--ausgabe VERZEICHNIS`: schreibt `elemente.json`/`elemente.js` woandershin (für Probeläufe).
- Fehlen die Spielewiki-Rohdaten, steht jetzt ein deutlicher Hinweis mit den Folgen (siehe Befund B1).

**`analyse.py`, `convert_inspirator.py`, `import_*.py`**: kaputtes JSON in den gelesenen Dateien ergibt eine deutsche Meldung.

**`scripts/rauchtest-kanten.js`** (neu, ändert `rauchtest.js` nicht): 56 Prüfungen für die Ränder – siehe Abschnitt 4.

**`scripts/rauchtest-seite.html`**: Rahmenseite, die App und beide Tests lädt und das Ergebnis oben anzeigt.

## 2. Befunde zu Python und Daten

- **B1 (wichtig): Der Build ist ohne Spielewiki-Rohdaten nicht reproduzierbar.** `data/quellen/spielewiki/raw/` steht in `.gitignore`. Ohne diesen Ordner leitet `build.py` `platz` und `hosensackspiel` nur aus dem Text ab: in einem frischen Checkout (oder einem Worktree) ändern sich beim ersten Lauf 616 Zeilen in `data/elemente.json` (ca. 447 × `platz: ""`, 110 Hosensackspiele weniger). Mit Rohdaten ergibt sich **byte-genau** die eingecheckte Datei. Der Build ist mit Rohdaten idempotent (zweiter Lauf: gleiche SHA-256 bei `elemente.json` und `elemente.js`; `analyse.py` und `import_spielewiki.py --offline` ebenso). Gegenmaßnahme: Warnung im Build, Hinweis in `pruefe.py`. Wer nur Code ändert, sollte vor dem Commit der Daten prüfen, dass `raw/` da ist. Offen: ob `raw/` doch ins Repo soll (Größe?) oder `build.py` ohne `raw/` die Ausgabe nicht überschreiben soll.
- **B2: `python3 scripts/import_pfadfinder_spiele.py --offline` ließ sich nicht prüfen**, weil es auch im Hauptordner keine Rohdaten gibt (`raw/posts.json` fehlt). Es endet ohne Rohdaten sauber mit einer Meldung und Exit 1.
- **B3: Fehlt eine Import-Ausgabe (`pfadfinder-spiele/elemente.json`, `spielewiki/elemente.json`), warnt `build.py` nur und baut ohne sie weiter.** Dabei würde `data/elemente.json` kleiner überschrieben. Beabsichtigt dokumentiert, aber riskant; `pruefe.py` fällt dann über die Waisen in der Redaktion auf.
- **B4: CLAUDE.md sagt "Python 3.10+", der Auftrag "3.9".** Alle Skripte laufen auf 3.9.6; `analyse.py` nutzt `from __future__ import annotations` (damit sind `list[dict]` usw. unschädlich). Wenn 3.9 gilt, sollte CLAUDE.md angepasst werden.
- **B5: Die Redaktion ist im Hauptordner weiter als im Git-Stand dieses Worktrees** (`data/redaktion.json` 96 KB statt 72 KB, `data/sprache.json`, `web/sprache.js` und Erzeugung von `sprache.js` in `build.py`, vermutlich nicht eingecheckt). `pruefe.py --wurzel <Hauptordner> --schnell` läuft gegen diesen Stand mit **OK**. Beim Zusammenführen müssen meine `build.py`-Änderungen mit denen im Hauptordner zusammengeführt werden; dort sollte `--ausgabe` auch `sprache.js` umleiten.
- **B6: In `redaktion.json` setzt der Eintrag `insp-typische-1-hilfe-fallbeispiele` unter `korrekturen` das alte Feld `element_typ`.** `build.py` wirft es am Ende weg, der Eintrag bewirkt nichts. Nicht geändert (Daten), als Hinweis in `pruefe.py`.
- **B7: Gleiches `haupt` mehrfach unter `zusammengelegt` ist erlaubt** (`build.py` führt die Gruppen zusammen, 13 Fälle im Hauptordner). Der Prüfer meldet es deshalb nicht.
- **B8: Zwei Texte enthalten Adressen mit Satzzeichen am Ende** (`insp-sternenhimmel-erkunden`: `https://stellarium-web.org/.`, `insp-unser-lagerplatz-in-der-zukunft`: `https://r9.whiteboardfox.com,`). Die App macht das Satzzeichen zum Teil des Links (siehe I2). Die Daten sind unverändert, `pruefe.py` zeigt es als Hinweis.
- **B9: Sprachregel "Ein:e Geschichtenerzähler:in" greift in keinem Element** (nur die kleingeschriebene Fassung kommt vor). Harmlos. In den Daten steht außerdem einmal die Tippfehler-Form `Sippensymbolß`, die die Regeln absichtlich mit abdecken.
- Waisen: **keine** in `redaktion.json` des Git-Stands (gegen alle Quellen geprüft, auch die gesperrten) und keine in `sprache.json`; für den Hauptordner liefen nur die Prüfungen gegen `elemente.json` (die Quellen lassen sich nur im eigenen Repo lesen), auch dort ohne Fund. Die einzige harte Korrektur an den Daten, die der Prüfer hätte vorschlagen können, war also nicht nötig; `data/` ist unverändert.

## 3. Wie die Tests ohne Browser laufen können (Auftragspunkt 3)

Auf diesem Mac ist **Node nicht installiert**. `rauchtest.js` greift auf rund 60 globale Funktionen und Variablen der App und auf `document` zu (`ALLE`, `pfad`, `aktualisiere`, `getComputedStyle`, Klicks auf Knöpfe, Dialoge). Eine Auslagerung der reinen Logik wäre ein Umbau der `index.html` und kommt nicht in Frage, solange parallel daran gearbeitet wird. Was geht:

1. **Datenteil ohne Browser:** `python3 scripts/pruefe.py` deckt alles aus dem Abschnitt "Daten" des Rauchtests ab (und mehr).
2. **Die Tests in einem Rutsch, ohne Konsole kopieren:** `rauchtest-seite.html` (siehe oben). Getestet im Browserfenster von Claude Code: `rauchtest.js` 194 Prüfungen ok (gegen die `index.html` aus dem Hauptordner), `rauchtest-kanten.js` 56 Prüfungen mit einem Fehler und drei Befunden (Abschnitt 4).
3. **Headless-Browser:** Brave liegt unter `/Applications`. Ein Start mit `--headless --dump-dom` auf die Rahmenseite kam hier aber nicht zurück (hing auch bei einer leeren Seite, vermutlich die Sandbox); deshalb nicht eingebaut.
4. **Node später:** Mit `npm install jsdom` lässt sich `index.html` per `new JSDOM(html, { runScripts: "dangerously", resources: "usable", url: "http://localhost/web/" })` laden und der Test mit `dom.window.eval(...)` ausführen. Das ist nicht ausprobiert (kein Node hier); `getComputedStyle`-Prüfungen und Layout-Dinge sind in jsdom nur eingeschränkt verlässlich.

**Hinweis zum Stand:** `scripts/rauchtest.js` im Hauptordner unterscheidet sich von dem im Git-Stand dieses Worktrees. Der Git-Stand fragt noch den Filter `fTeilnehmer` ab, den es in der neuen `index.html` nicht mehr gibt (Anzahl steht jetzt in "Heute sind wir"). Deshalb steht das Neue in einer eigenen Datei, die nichts davon überschreibt.

## 4. `rauchtest-kanten.js`: was geprüft wird

- Daten in der App: IDs eindeutig, Dauer und Gruppengröße plausibel, keine Texte mit `undefined`/`NaN`, kein `<script>`, Dubletten und Varianten verweisen auf Vorhandenes.
- Leere Filter und null Treffer: Suche ohne Treffer, nur Leerzeichen, Sonderzeichen, 5000 Zeichen, unmögliche Filterkombination, Zurücksetzen, Zufall-Knopf gesperrt.
- "Heute sind wir": `setzeAnzahl` mit 1, 2, 40, 100, 0, -3, "abc", leer, null, undefined, NaN, 7.5, 25; Filterregel an beiden Enden (3 und 25); − und + an den Enden; Hinweistext in Zahlen.
- Leere Sammlung (`ALLE = []`): Zeichnen, Würfeln, Plan-Text, Zufall.
- **`localStorage` nicht verfügbar** (Zugriff wirft): Das ist ohne Änderung an der `index.html` testbar, indem der Test `window.localStorage` vorübergehend durch einen werfenden Zugriff ersetzt. Alle Lade- und Speicherfunktionen (Sammlung, Anzahl, Plan, eigene Ideen) laufen durch, `setzeSammlung`/`setzeAnzahl` wirken trotzdem, eine eigene Idee meldet einen Fehler statt zu verschwinden. Ergebnis: **besteht**.

Zeilen, die mit "Befund" anfangen, zählen nicht als Fehler; Prüfungen für Funktionen, die es in der geöffneten App-Fassung nicht gibt, stehen als "übersprungen".

## 5. Befunde zu `web/index.html` (nicht behoben, Stand: Hauptordner mit "Heute sind wir")

- **I1 (Fehler, echt): "Filter zurücksetzen" bei "Nichts gefunden" leert das Suchfeld nicht.** `setzeFilterZurueck()` setzt nur den Filterkasten zurück. Kommt das leere Ergebnis von der Suche (oder von "Heute sind wir" bzw. "geprüfte Auswahl"), tut der Knopf scheinbar nichts. Der Randfälle-Test meldet das als einzigen FEHLER. Die Meldung "Überall suchen" hilft nur, wenn ein Pfad gewählt ist.
- **I2 (Fehler, klein): Adressen im Text werden mit Satzzeichen am Ende verlinkt** (`/(https?:\/\/[^\s<]+)/g`). In den Daten betrifft das heute 2 von 16 Adressen (siehe B8); jede neue Quelle kann es wieder auslösen. Auch ein `&quot;` oder `)` am Ende landet im Link.
- **I3 (Risiko): Gruppen über 25 und unter 3 sind nicht ausdrückbar.** Die Stufen sind `0, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25`. `setzeAnzahl(1)`, `(2)` und `(40)` werden stillschweigend zu "egal". Für 1 bis 2 Kinder ist das vertretbar, für 40 nicht.
- **I4 (Risiko, Wortlaut): "25 Kinder oder mehr" filtert nur mit genau 25.** Bausteine mit `gruppe_max` zwischen 25 und 39 gelten als passend, passen aber nicht zu 40 Kindern (745 Treffer bei 25; für wirklich 40 Kinder bleiben 664). Entweder den Text auf "25 Kinder" ändern oder bei der letzten Stufe `gruppe_max >= 25` statt `== 25` rechnen.
- **I5 (Risiko, klein): Gespeicherte Pläne behalten IDs, die es nach einem Neubau nicht mehr gibt** (z. B. gesperrte Elemente). Der Platz zeigt "noch offen", das Gespeicherte bleibt aber stehen, und ein verfälschter Speicher mit drei `haupt`-Einträgen erzeugt einen dritten Hauptteil-Platz. Probiert mit absichtlich kaputtem Speicherinhalt: kein Absturz, Rahmen und Anzahl werden auf Standardwerte gesetzt. Wunsch: unbekannte IDs beim Laden verwerfen.
- **I6 (Risiko, niedrig): `ladeDaten()` fällt bei jedem Fehler (auch bei kaputtem JSON auf dem Server) stillschweigend auf `elemente.js` zurück.** Sind beide Dateien verschieden alt, sieht man alte Daten ohne Hinweis. `pruefe.py` stellt sicher, dass beide im Repo gleich sind; im Browser merkt man es nicht. Dasselbe bei `sprache.json`/`sprache.js`.
- **Positiv:** Alle `localStorage`-Zugriffe sind abgesichert (auch das Lesen von `window.localStorage` selbst), Text aus den Daten wird maskiert, bevor er in `innerHTML` landet, externe Links tragen `rel="noopener"`, `aktualisiere()` und der Planer überstehen leere Filter, 0 Treffer und eine leere Sammlung ohne Fehler.
