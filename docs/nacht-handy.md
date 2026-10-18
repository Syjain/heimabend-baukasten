# Handy-Durchgang – was ein Gruppenführer am Handy erlebt und was geändert wurde

Gemessen bei 375 x 812 (und gegengeprüft bei 320 px), dunkel und hell, im Browser
verifiziert. Leitlinie: nichts Neues, nur Reibung abbauen. Es kam **kein** neuer
Filter, kein neues Feld, kein neuer Reiter dazu. Rauchtest: 194 → 207 Prüfungen,
0 Fehler.

Ausgangspunkt war `main` mit „Heute sind wir“, Reiter „Vorbereiten“ und dem
Filterkasten mit „Mehr Optionen“ (der Worktree stand noch davor und wurde
vorgespult).

## Befunde und Änderungen

| # | Befund | Vorher | Nachher |
|---|---|---|---|
| 1 | **Fehler:** „Mehr Optionen“ im Filterkasten, aufgeklappt, stand Titelzeile und Inhalt nebeneinander statt untereinander (die Klasse `mehr` war schon für „Weitere anzeigen“ vergeben: flex, zentriert). Vorbereitung und Platz saßen halb breit und eingerückt. | kaputt | Block, untereinander |
| 2 | **Detailansicht:** der erste Satz der Regeln lag mehr als eine Bildschirmhöhe weit unten (erst Plan-Knöpfe, „Nächste Woche“, Datenblatt mit 9 Zeilen). | Text ab 863 px | Text ab 144 px; Plan-Knöpfe und Datenblatt folgen danach |
| 3 | Kurztext stand doppelt über der Beschreibung, weil der Vergleich an `**fett**` scheiterte. | bei 1008 von 1075 | bei 438 (nur noch, wo er wirklich etwas anderes sagt) |
| 4 | Datenblatt: Zeile „Umfang: einzelner Baustein“ sagt bei fast allen nichts. | immer | nur bei „füllt einen ganzen Heimabend“ |
| 5 | „Heute sind wir **egal**“ liest sich wie eine Antwort auf die Frage. | egal | „? Kinder“ |
| 6 | „25+ Kinder“ wurde im Auswahlfeld abgeschnitten (Monospace, 96 px). | abgeschnitten | Systemschrift, 114 px, einzeilig bei 375 px |
| 7 | Kleinschrift: Beschriftungen 10,9 px, Zahlen/Hinweise 11,8 px, Plaketten 10,9 px. | 10,9–11,8 px | 12–12,8 px (nichts mehr unter 12 px; Ausnahme: „Heute sind wir“ bei unter 360 px) |
| 8 | Plus/Minus bei „Heute sind wir“ nur 42 px breit. | 42 px | 44 px |
| 9 | Nach Änderung 7 brach „299 Bausteine“ in den Kacheln um. | – | Kachelrand schmaler, kein Umbruch ab 360 px |
| 10 | Leerzustand: „Nichts gefunden. [Filter zurücksetzen]“ – auch wenn keine Filter gesetzt waren, und ohne zu sagen, ob das hilft. Ein Wort, das nur in der zweiten Reihe steht, wirkte wie „gibt es nicht“. | – | Zeigt „Gesucht mit: Wort · Filter · Anzahl“ und je einen Weg **mit Trefferzahl**: „Auch die zweite Reihe durchsuchen (1)“, „Filter zurücksetzen (39)“, „Anzahl nicht beachten (n)“, „Überall suchen (n)“. Hilft nichts, steht ein Tipp zum Suchwort. Dasselbe im Auswahl-Dialog („Suchwort löschen“, „Auch Längeres zeigen“). |
| 11 | Über dem Leerzustand standen „0 Bausteine“ und das Sortierfeld. | ja | ausgeblendet |
| 12 | Karten: jede trug „drinnen & draußen“ und bei zwei Dritteln „Alter offen“ – 5 Plaketten, die nichts sagen. | 4–6 Plaketten | „drinnen/draußen“ nur bei Einschränkung, „Alter offen“ nur, wenn eine Altersstufe gewählt ist (dann steht es auch in der Trefferzeile) |
| 13 | Plan: der gewählte Baustein ist antippbar (öffnet die Regeln), sieht aber aus wie Text. Dazu „ · Heimabend-Inspirator“ mit losem Trennpunkt. | kein Hinweis | Pfeil „›“ hinter dem Titel, Trennpunkt nur, wo zwei Angaben da sind |
| 14 | „+“ neben „Zufall“ sagt nicht, wofür es steht. | „+“ | „+ Idee“ ab 360 px (darunter bleibt „+“) |
| 15 | Fehlerkasten im Ideenformular war für Screenreader unsichtbar; Quell-Link in der Detailansicht nur 34 px hoch. | – | `role="alert"`; Link 45 px |

## Geprüft und in Ordnung (nicht angefasst)

- **Kein horizontales Scrollen** in Start, Liste, Detail, Plan, Vorbereiten, Ideenformular bei 375 und 320 px.
- **Kontrast** (WCAG AA) hell und dunkel: keine Stelle unter 4,5 : 1 (die Messung „3,3 : 1“ in der Planer-Leiste war ein Messfehler durch die Transparenz; gerechnet 5,8 : 1).
- **Tippflächen**: alle Knöpfe, Felder, Reiter, Kacheln, Schalter mindestens 44 px hoch (Ausnahme: Plus/Minus bei unter 360 px, 38 px breit).
- **Geschwindigkeit**: Liste mit 1075 Elementen, Suche pro Tastendruck 12–18 ms, „Weitere anzeigen“ unter 1 ms, Seitenaufbau 55 ms; `elemente.json` 2,6 MB (auf GitHub Pages gezippt, ein Bruchteil davon).
- **Tastatur/Screenreader**: alle Felder haben Beschriftungen, die Dialoge setzen den Fokus hinein, Esc schließt, der Fokus kehrt zurück, der Hintergrund ist gesperrt.
- **Dunkelmodus** ist vorhanden und folgt dem Gerät.

## Bewusst nicht geändert

- **Sammlungsschalter im Filterkasten** (geprüfte Auswahl / ganze Sammlung): bleibt, wo Yannick ihn hingelegt hat. Die Kopfzeile des Kastens meldet „ganze Sammlung“, und der Leerzustand bietet die zweite Reihe jetzt ausdrücklich an – damit filtert nichts unbemerkt.
- **„Würfeln“ (ganzer Plan) und „Zufall“ (ein Platz)** sowie **„Entfernen“ und „Platz löschen“** im Planer: sehen ähnlich aus, tun aber Verschiedenes. Zusammenlegen ändert das Verhalten, nicht nur die Beschriftung – siehe Fragen.
- **Karten mit 3 Plaketten** (Art, Kategorie, Unterkategorie): Kategorie und Unterkategorie wiederholen sich oft sinngemäß („Ankommen & Kennenlernen · Namen & Kennenlernen“). Das ist ein Datenthema, nicht Oberfläche.
- **Daten** (`data/`) nicht berührt.

## Fragen an Yannick

1. **Planer: „Entfernen“ und „Platz löschen“** stehen bei einem gefüllten zweiten Hauptteil nebeneinander. Soll „Entfernen“ dort den ganzen Platz wegnehmen, wenn es mehr als einen Hauptteil gibt? Dann entfällt ein Knopf.
2. **„Würfeln“ unten und „Zufall“ je Platz:** soll es nur noch „Würfeln“ geben (Platz antippen → „Tauschen“)? Weniger Knöpfe, aber ein Weg weniger zum schnellen Einzeltausch.
3. **Detailansicht:** soll „In den Plan“ ganz nach unten (nach dem Datenblatt) oder bleibt es unter den Regeln? Jetzt steht es unter den Regeln, damit man es ohne langes Scrollen findet.
4. **Zweite Plakettenreihe auf Karten** (Kategorie plus Unterkategorie): eine von beiden weglassen?
5. **2,6 MB beim ersten Öffnen** über Mobilfunk im Gruppenheim: soll die Datei verkleinert werden (z. B. Beschreibungstexte erst beim Öffnen nachladen)? Das ist eine größere Änderung an Daten und Ladeweg, deshalb nicht in dieser Nacht.
