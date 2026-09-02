# Heimabend-Baukasten

Ein Werkzeug für junge Gruppenführer*innen bei den Pfadfindern: Bausteine (Spiele, Proben, Aktivitäten, Projekte),
aus denen sich ein ca. zweistündiger Heimabend zusammenstellen lässt.

- Was ein Heimabend ist und was das Tool soll: `docs/heimabend-definition.md`
- Datenmodell: `data/SCHEMA.md`
- Woher die Daten kommen und was lizenzrechtlich geht: `docs/datenquellen.md`
- Arbeitsanweisung für Claude Code: `PROMPT-fuer-claude-code.md` (Projektkontext in `CLAUDE.md`)

## Stand
`data/elemente.json` enthält 1044 Bausteine aus fünf Quellen (erzeugt von `scripts/build.py`):

| Quelle | Anzahl | Lizenz |
|---|---:|---|
| Spielewiki (`scripts/import_spielewiki.py`) | 629 | CC BY-SA 4.0 |
| DPBM-Heimabend-Inspirator (`data/quellen/inspirator/`) | 211 | CC BY-NC 4.0 |
| pfadfinder-spiele.de (`scripts/import_pfadfinder_spiele.py`) | 115 | CC BY-NC-SA 4.0 |
| eigene Ideen (`data/eigene/`) | 61 | CC BY-SA 4.0 |
| DPB-Probenbuch (`data/quellen/probenbuch/`) | 28 | Rechte beim Projektinhaber |

Nach Typ: 753 Spiele, 232 Projekte, 35 Proben, 18 Aktivitäten.

`data/redaktion.json` hält fest, was aus den Quellen herausfällt, umbenannt oder
korrigiert wird – mit Begründung je Eintrag. Ohne diese Datei holt der nächste
Importlauf alles wieder herein, weil die Import-Skripte idempotent sind.

Neu bauen:

    python3 scripts/import_pfadfinder_spiele.py   # holt die Spiele von pfadfinder-spiele.de
    python3 scripts/import_spielewiki.py          # holt die Spiele aus dem Spielewiki
    python3 scripts/build.py                      # führt alles zu data/elemente.json zusammen

Die beiden Import-Skripte kennen `--offline` und arbeiten dann nur mit den bereits
geholten Rohdaten.

## Die App benutzen

`web/index.html` per Doppelklick öffnen – mehr braucht es nicht. Näher an GitHub Pages
ist ein kleiner Webserver:

    python3 -m http.server 8000

Danach `http://localhost:8000/web/index.html` aufrufen. Was die App kann, steht in
`web/README.md`.

Nach Änderungen an der App: `scripts/rauchtest.js` in die Browser-Konsole
kopieren, das prüft 46 Punkte auf einmal (Anleitung oben in der Datei).

## Was noch offen ist
- Eigene Ideen in der App erfassen – Entwurf in `docs/eigene-ideen-erfassen.md`
- Die Abbildungen des Probenbuchs (Knoten, Zeltbau, Karten) fehlen in der
  Textfassung; betroffene Proben tragen einen Hinweis

## Lizenz
Eigene Inhalte: CC BY-SA 4.0 (Vorschlag). Fremde Inhalte je Element unter der angegebenen Quell-Lizenz.
Das Projekt ist nicht-kommerziell.
