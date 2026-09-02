# Prompt für Claude Code

So startest du: Terminal öffnen, in den Projektordner wechseln und Claude Code starten:

```bash
cd ~/Documents/Programmieren/heimabend-baukasten   # in den Projektordner wechseln
claude                                             # Claude Code starten
```

Dann diesen Text einfügen (alles zwischen den Linien):

---

Lies zuerst CLAUDE.md, docs/heimabend-definition.md, docs/datenquellen.md und data/SCHEMA.md vollständig, bevor du irgendetwas baust. Ich bin Programmier-Einsteiger – erkläre mir bei jedem Befehl, den ich selbst ausführen soll, in einer Zeile, was er tut, und frag nach, bevor du größere Architekturentscheidungen triffst.

Wir bauen den Heimabend-Baukasten in vier Schritten. Mach nach jedem Schritt einen Git-Commit und zeig mir kurz, was entstanden ist.

**Schritt 1 – Import pfadfinder-spiele.de.** Schreib `scripts/import_pfadfinder_spiele.py`: Ruft die WordPress-REST-API ab (`https://pfadfinder-spiele.de/wp-json/wp/v2/posts?per_page=100&page=N`, bis alle 115 Posts da sind), speichert die Rohantwort unter `data/quellen/pfadfinder-spiele/raw/posts.json`, nimmt nur Posts der Kategorie „Gruppenspiele“, wandelt das HTML in Text um und mappt die ACF-Felder (`spielart`, `umgebung`, `material`, `alter`, `ungefahre_dauer`, `gruppengrose`) nach der Tabelle in `data/SCHEMA.md` auf unser Element-Schema. Ausgabe: `data/quellen/pfadfinder-spiele/elemente.json`. Lizenz jedes Elements: „CC BY-NC-SA 4.0“, Autor „Dorothea Schümann“, URL = Post-Link. Englische Spiele weglassen, wenn es eine deutsche Version desselben Spiels gibt.

**Schritt 2 – Import Spielewiki.** Schreib `scripts/import_spielewiki.py`: Holt über die MediaWiki-API (`https://www.spielewiki.org/w/api.php`, `list=categorymembers`, Kategorie `SpieleWiki:Spiel`, dann `action=parse` oder `prop=revisions` für den Wikitext) alle Spiele, speichert Rohdaten unter `data/quellen/spielewiki/raw/`, parst die Infobox (Art, Spieleranzahl, Ort, Material, Dauer, Vorbereitung) und den Regeltext und mappt ins Schema. Lizenz „CC BY-SA 4.0“, Quelle „Spielewiki“, URL = Wikiseite. Zwischen den Requests kurz warten (0,5 s) und einen User-Agent setzen, der auf unser Projekt hinweist. Ausgabe: `data/quellen/spielewiki/elemente.json`.

**Schritt 3 – Zusammenführen.** Schreib `scripts/build.py`: Liest `data/eigene/heimabend-ideen.json` (Mapping je Kategorie laut SCHEMA.md), `data/quellen/inspirator/inspirator-ideen.json` (→ element_typ „projekt“, Rover → Ältere), und die beiden Import-Ausgaben, vergibt IDs mit Quell-Präfix (eig-, insp-, ps-, sw-), erkennt Dubletten über normalisierte Titel (nur markieren mit `dubletten: [ids]`, nicht löschen), validiert Pflichtfelder und schreibt `data/elemente.json` plus eine Statistik (Anzahl je Typ, Kategorie, Quelle, Lizenz) in der Konsole.

**Schritt 4 – Web-App.** Bau `web/index.html` als eine einzige Datei (HTML + CSS + Vanilla JS, kein Framework, kein Build-Schritt), die `../data/elemente.json` per fetch lädt (beachte: bei Doppelklick auf die Datei blockt der Browser fetch – bau deshalb zusätzlich `scripts/build.py` so, dass es `web/elemente.js` mit `window.ELEMENTE = [...]` erzeugt, das per `<script>` eingebunden wird). Mobile-first, deutsch, schlicht. Funktionen: Filter nach Typ, Kategorie, Altersstufe, Dauer, drinnen/draußen, „ohne Material“, Vorbereitung; Volltextsuche; Zufallsvorschlag; Detailansicht mit Quelle und Lizenz; und ein Modus „Heimabend zusammenstellen“ mit den Slots Eröffnungskreis → Einstiegsspiel → Hauptteil (Spiel / Probe / Aktivität) → Abschlussspiel → Schlusskreis, der die Gesamtdauer summiert (Ziel ca. 120 Minuten) und den Plan als Text zum Kopieren/Teilen ausgibt.

Beginn mit Schritt 1 und zeig mir das Ergebnis, bevor du mit Schritt 2 weitermachst.

---
