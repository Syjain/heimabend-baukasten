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

## Ansicht „Bausteine"

Über tausend Einträge in einer Liste sind unbrauchbar, deshalb geht es über
**Kacheln in die Tiefe**:

    Art (Spiele, Proben, Aktivitäten, Projekte)
      → Kategorie (Kreisspiele, Geländespiele, Knoten …)
        → Unterkategorie (Singen & Tanzen, Fangen & Laufen …)
          → Liste, nach Dauer sortiert

Die dritte Ebene wird übersprungen, wo sie nicht hilft – bei unter 20 Einträgen
oder wenn es nur eine Unterkategorie gibt. Eine Brotkrume führt zurück, „Alle
anzeigen" überspringt die Ebenen. Auf der Startseite gibt es zusätzlich die
Abkürzungen **„Zum Einstieg"** und **„Zum Abschluss"**, weil man oft genau danach
sucht.

**Suche:** über Titel, Kurztext, Stichworte und Beschreibung. Mehrere Wörter
werden einzeln geprüft („Gelände spiel" findet dasselbe wie „Geländespiel").
Sortiert wird nach Relevanz: Titeltreffer zuerst.

**Filter:** Altersstufe, Dauer, Teilnehmerzahl, Ort, Vorbereitung, „nur ohne
Material" und „nur mit geprüfter Altersangabe". Die Zahlen auf den Kacheln
berücksichtigen die Filter, und der zugeklappte Kasten zeigt, wie viele gesetzt
sind.

**Detailansicht:** Ablauf, Hinweise, Datenblatt, Quelle und Lizenz. Stichworte
sind anklickbar und führen zu verwandten Bausteinen. Bausteine, die es in
mehreren Quellen gibt, verweisen aufeinander. Von hier führt ein Knopf direkt
**in den Plan**.

## Ansicht „Heimabend planen"

Der Ablauf steht als Zeitstrahl:

    Eröffnungskreis → Einstiegsspiel → Hauptteil (beliebig viele Plätze)
    → Abschlussspiel → Schlusskreis

Eröffnungs- und Schlusskreis sind mit je fünf Minuten fest eingeplant.

**Rahmen des Abends** (einklappbar) gilt für alle Vorschläge: Gesamtzeit,
Altersstufe, Teilnehmerzahl, Ort, höchstens welche Vorbereitung, nur ohne
Material.

Jeder leere Platz zeigt, wie viel Zeit noch frei ist, und bietet **Vorschläge**
– zeitlich passend und nach Passung sortiert. Im Auswahl-Dialog lässt sich jeder
Baustein erst lesen und dann übernehmen; Chips grenzen nach Art, Kategorie und
Unterkategorie ein.

**Würfeln** füllt alle leeren Plätze und hält dabei die Zielzeit ein: Einstieg
und Abschluss bleiben kurz, die restliche Zeit verteilt sich auf den Hauptteil.
Gemessen über je 25 Würfe: Ziel 60 → 63 Min, Ziel 90 → 80, Ziel 120 → 110,
Ziel 150 → 135. Kein Baustein kommt zweimal vor.

Der fertige Plan lässt sich als Text teilen oder kopieren – mit Kurzbeschreibung,
Quelle, Lizenz und einer Materialliste für den ganzen Abend. Der zuletzt
bearbeitete Plan und der Rahmen bleiben im Browser gespeichert.

## Altersstufen

654 der Bausteine haben gar keine Altersangabe – vor allem die aus dem
Spielewiki, das kein solches Feld führt. Die App behauptet dafür **nicht**
„alle Stufen", sondern schreibt „keine Angabe – bitte selbst einschätzen" und
setzt auf die Karte eine gestrichelte Plakette „Alter offen". Ist eine
Altersstufe gewählt, stehen geprüfte Bausteine vorn, und die Trefferzeile nennt
die Zahl der ungeprüften. Wer nur Geprüftes sehen will, setzt den Haken
„nur mit geprüfter Altersangabe".

## Prüfen nach Änderungen

`scripts/rauchtest.js` prüft 46 Punkte im Browser – Navigation, Sortierung,
Suche, Filter, Würfeln, Auswahl-Dialog, Detailansicht. Anleitung steht oben in
der Datei. Nach jeder Änderung an `index.html` laufen lassen.

## Veröffentlichen

Für GitHub Pages reicht es, das Repository als Quelle einzustellen; die App liegt
dann unter `…/web/index.html` und findet `data/elemente.json` über den relativen
Pfad. Beide Ordner (`web/` und `data/`) müssen dafür veröffentlicht sein.
