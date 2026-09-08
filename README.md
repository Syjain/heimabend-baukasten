# Heimabend-Baukasten

**App:** https://syjain.github.io/heimabend-baukasten/web/ · **Code:** https://github.com/Syjain/heimabend-baukasten

Ein Werkzeug für junge Gruppenführer*innen bei den Pfadfindern: Bausteine (Spiele, Proben, Aktivitäten, Projekte),
aus denen sich ein ca. zweistündiger Heimabend zusammenstellen lässt.

- Was ein Heimabend ist und was das Tool soll: `docs/heimabend-definition.md`
- Datenmodell: `data/SCHEMA.md`
- Woher die Daten kommen und was lizenzrechtlich geht: `docs/datenquellen.md`
- Arbeitsanweisung für Claude Code: `PROMPT-fuer-claude-code.md` (Projektkontext in `CLAUDE.md`)

## Stand
`data/elemente.json` enthält 1075 Bausteine aus fünf Quellen (erzeugt von `scripts/build.py`):

| Quelle | Anzahl | Lizenz |
|---|---:|---|
| Spielewiki (`scripts/import_spielewiki.py`) | 622 | CC BY-SA 4.0 |
| DPBM-Heimabend-Inspirator (`data/quellen/inspirator/`) | 211 | CC BY-NC 4.0 |
| pfadfinder-spiele.de (`scripts/import_pfadfinder_spiele.py`) | 115 | CC BY-NC-SA 4.0 |
| eigene Sammlung (`data/eigene/`) | 99 | CC BY-SA 4.0 |
| DPB-Probenbuch (`data/quellen/probenbuch/`) | 28 | Nutzung mit Erlaubnis des Rechteinhabers |

Nach Bereich: 794 Spiele, 77 Pfadfindertechnik, 72 Gemeinschaft, 67 Werken,
30 Natur & Draußen, 23 Kochen, 12 Musisches.

**Zwei Reihen statt löschen.** Seit dem 08.09.2026 trägt jedes Element ein Feld
`kern`. 580 Elemente stehen in der ersten Reihe – das ist die geprüfte Auswahl,
die die App beim Öffnen zeigt, darunter 299 Spiele nach Quoten je Unterkategorie.
Die übrigen 495 (Doppeltes, sehr Langes, sehr Großes, Ideen fürs Netz) bleiben
vollständig in den Daten und sind über einen Schalter erreichbar. Es wird nichts
gelöscht, und jede Zuordnung lässt sich in `data/redaktion.json` unter `kern`
von Hand umdrehen.

`data/redaktion.json` hält fest, was aus den Quellen herausfällt, umbenannt oder
korrigiert wird, welche Fassungen zusammengelegt werden und was in welche Reihe
gehört – mit Begründung je Eintrag. Ohne diese Datei holt der nächste
Importlauf alles wieder herein, weil die Import-Skripte idempotent sind.

Der Befund, aus dem das alles folgt, steht in `docs/pruefung-2026-09/`
(Prüfdokument mit 73 Fragen und vier Tabellen, erzeugt von `scripts/analyse.py`).
Was davon in der Nacht zum 09.09.2026 eingearbeitet wurde und was noch zu
entscheiden ist: `docs/nachtschicht-2026-09-09.md`. Die fünf offenen
Sprachfragen: `docs/sprache.md`.

Neu bauen:

    python3 scripts/import_pfadfinder_spiele.py   # holt die Spiele von pfadfinder-spiele.de
    python3 scripts/import_spielewiki.py          # holt die Spiele aus dem Spielewiki
    python3 scripts/build.py                      # führt alles zu data/elemente.json zusammen

Die beiden Import-Skripte kennen `--offline` und arbeiten dann nur mit den bereits
geholten Rohdaten.

## Die App benutzen

Online unter https://syjain.github.io/heimabend-baukasten/web/ – die Adresse kann man
weitergeben, sie läuft am Handy ohne Installation. Nach jedem `git push` auf `main` baut
GitHub Pages die Seite in etwa einer Minute neu.

Lokal:

`web/index.html` per Doppelklick öffnen – mehr braucht es nicht. Näher an GitHub Pages
ist ein kleiner Webserver:

    python3 -m http.server 8000

Danach `http://localhost:8000/web/index.html` aufrufen. Was die App kann, steht in
`web/README.md`.

Nach Änderungen an der App: `scripts/rauchtest.js` in die Browser-Konsole
kopieren, das prüft 111 Punkte auf einmal (Anleitung oben in der Datei).

## Was noch offen ist
- Fünf Sprachentscheidungen (Sippe oder Horte/Gilde, Spielleitung oder
  Gruppenführer, Genderschreibweise, Tonfall, Umschreiben fremder Texte) –
  Optionen mit Zahlen in `docs/sprache.md`
- Gemeinsam sammeln über Supabase – Entscheidungspapier in
  `docs/gemeinsam-sammeln.md`, wartet auf Zugangsdaten
- Die Abbildungen des Probenbuchs (Knoten, Zeltbau, Karten) fehlen in der
  Textfassung; betroffene Proben tragen einen Hinweis

## Lizenz
Eigene Inhalte: CC BY-SA 4.0 (Vorschlag). Fremde Inhalte je Element unter der angegebenen Quell-Lizenz.
Das Projekt ist nicht-kommerziell.
