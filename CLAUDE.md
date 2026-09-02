# Heimabend-Baukasten – Projektkontext für Claude Code

## Worum es geht
Ein Werkzeug für junge Gruppenführer*innen bei den Pfadfindern (Deutscher Pfadfinderbund, Prinzip „Jugend führt Jugend“).
Ein **Heimabend** ist die wöchentliche, ca. zweistündige Gruppenstunde. Das Tool liefert **Bausteine** (Spiele,
Proben = Pfadfinderwissen, Gemeinschaftsaktivitäten, Projekte), aus denen sich ein Heimabend zusammenstellen lässt.
Bewusst KEIN projektbezogener Ansatz wie der DPBM-Inspirator (gruppenstunde.de), sondern ein Baukasten.
Lies zuerst `docs/heimabend-definition.md` und `data/SCHEMA.md`.

## Typischer Heimabend-Ablauf (Slots)
Eröffnungskreis → Einstiegsspiel → Hauptteil (1–2 Spiele + eine Probe und/oder Aktivität) → Abschlussspiel → Schlusskreis

## Ordnerstruktur
- `docs/` – Definition, Datenquellen-Recherche (mit Lizenzen!)
- `data/SCHEMA.md` – einheitliches Element-Schema, Kategorien, Mapping je Quelle
- `data/eigene/heimabend-ideen.json` – 61 eigene Ideen (lizenzfreier Kern)
- `data/quellen/inspirator/` – 211 Ideen des DPBM-Inspirators (CC BY-NC 4.0), aufbereitet
- `data/quellen/<quelle>/raw/` – Rohdaten der Importe (in .gitignore, werden von Skripten geholt)
- `data/elemente.json` – ZIEL: zusammengeführte Datenbasis für die App (wird von `scripts/build.py` erzeugt)
- `scripts/` – Import-/Konvertierungsskripte (Python 3, nur Standardbibliothek wenn möglich)
- `web/` – statische Web-App (eine `index.html`, Vanilla JS, kein Build-Schritt), liest `data/elemente.json`

## Technische Leitplanken
- Sprache im Code, in Daten und in der Oberfläche: **Deutsch** (Feldnamen deutsch, wie im Schema).
- Python 3.10+, keine Abhängigkeiten außer Standardbibliothek (requests ist ok, wenn nötig – dann `requirements.txt`).
- Web: eine statische Seite ohne Framework und ohne Build-Schritt, muss per Doppelklick auf `web/index.html`
  UND auf GitHub Pages laufen. Mobile-first (Gruppenführer nutzen das am Handy im Heim).
- Skripte müssen idempotent sein (mehrfach ausführbar, überschreiben ihre Ausgabe).
- Später soll eine Flutter-App dieselbe `elemente.json` nutzen → Schema stabil halten, keine UI-Logik in die Daten.
- Der Nutzer ist Programmier-Einsteiger: Befehle, die er ausführen soll, immer mit einer Zeile Erklärung angeben.

## Lizenzen (nicht verhandelbar)
- Jedes Element trägt `quelle.name`, `quelle.url`, `quelle.autor`, `quelle.lizenz`; die App zeigt das an.
- CC BY-SA (Spielewiki) und CC BY-NC-SA (pfadfinder-spiele.de) / CC BY-NC (Inspirator) nie in einem Element mischen.
- Das Tool ist nicht-kommerziell. Keine Inhalte von Seiten übernehmen, die in `docs/datenquellen.md` unter „nur verlinken“ stehen.
- Keine E-Mail-Adressen oder andere personenbezogene Daten aus Quellen übernehmen.

## Nächste Schritte (Reihenfolge)
1. `scripts/import_pfadfinder_spiele.py` – REST-API abrufen, Rohdaten nach `data/quellen/pfadfinder-spiele/raw/`, Mapping ins Schema
2. `scripts/import_spielewiki.py` – MediaWiki-API/XML-Export der Kategorie `SpieleWiki:Spiel`, Infobox parsen, Mapping
3. `scripts/build.py` – alle Quellen (eigene, Inspirator, pfadfinder-spiele, Spielewiki) ins Schema mappen, Dubletten
   (gleicher Titel) markieren, `data/elemente.json` schreiben, Statistik ausgeben
4. `web/index.html` – Filter (Typ, Kategorie, Altersstufe, Dauer, Ort, Material ja/nein, Vorbereitung), Volltextsuche,
   Zufallsvorschlag, und ein „Heimabend zusammenstellen“-Modus: Slots füllen, Gesamtdauer anzeigen, Plan als Text teilen
5. Git: sinnvolle Commits nach jedem Schritt; GitHub Pages aus `web/` + `data/` (relative Pfade!)
