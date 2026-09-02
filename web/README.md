# Web-App

Alles steckt in `index.html`: HTML, CSS und JavaScript in einer Datei.
Kein Framework, kein Build-Schritt, keine Inhalte von fremden Servern.

## Öffnen

**Per Doppelklick** auf `index.html` – funktioniert ohne alles.

**Oder mit einem kleinen Webserver**, näher an GitHub Pages:

    cd heimabend-baukasten
    python3 -m http.server 8000

Dann im Browser `http://localhost:8000/web/index.html` aufrufen.
(Beenden mit Strg + C.)

## Woher die Daten kommen

Die App versucht zuerst `../data/elemente.json` per `fetch` zu laden – das ist der
Weg auf GitHub Pages. Beim Doppelklick auf die Datei sperrt der Browser `fetch`
aus Sicherheitsgründen; **nur dann** lädt die App `elemente.js` nach, das dieselben
Daten als `window.ELEMENTE` enthält. So werden die knapp 2 MB nie doppelt übertragen.

Beide Dateien erzeugt `python3 scripts/build.py`. `elemente.js` wird also nicht
von Hand bearbeitet.

## Was die App kann

**Bausteine** – Volltextsuche über Titel, Kurztext, Tags und Beschreibung
(Titeltreffer stehen oben), Filter nach Art, Kategorie, Altersstufe, Dauer, Ort,
Vorbereitung und „nur ohne Material", ein Zufallsvorschlag sowie eine Detailansicht
mit Ablauf, Hinweisen, Quelle und Lizenz. Bausteine, die es in mehreren Quellen
gibt, verweisen aufeinander.

**Heimabend planen** – Eröffnungskreis → Einstiegsspiel → Hauptteil (beliebig viele
Plätze) → Abschlussspiel → Schlusskreis. Die Gesamtdauer wird laufend summiert,
Ziel sind etwa 120 Minuten. „Würfeln" füllt alle leeren Plätze und achtet dabei auf
das Zeitbudget: Einstieg und Abschluss bleiben kurz, die restliche Zeit wird auf die
Plätze im Hauptteil verteilt. Der fertige Plan lässt sich als Text kopieren oder
teilen – mit Kurzbeschreibung, Quelle, Lizenz und einer Materialliste für den ganzen
Abend. Der zuletzt bearbeitete Plan bleibt im Browser gespeichert.

Die eingestellten Filter gelten auch beim Auswählen und Würfeln. Wer also oben
„draußen" und „ohne Material" einstellt, bekommt auch einen entsprechenden Abend.

## Altersstufen

Elemente ohne Altersangabe (vor allem die aus dem Spielewiki, das kein Altersfeld
hat) gelten für alle Stufen und werden bei keiner Altersauswahl herausgefiltert.

## Veröffentlichen

Für GitHub Pages reicht es, das Repository als Quelle einzustellen; die App liegt
dann unter `…/web/index.html` und findet `data/elemente.json` über den relativen
Pfad. Beide Ordner (`web/` und `data/`) müssen dafür veröffentlicht sein.
