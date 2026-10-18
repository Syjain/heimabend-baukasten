# Nacht 18.10.2026, Runde 2: Fehler in web/index.html

Leitlinie: nur Fehler beheben, nichts Neues. Rauchtest 207 Prüfungen, 0 Fehler;
Randfälle-Test 60 Prüfungen (vorher 56), 0 Fehler. Im Browser geprüft.

| # | Befund | Änderung |
|---|---|---|
| 1 | "Filter zurücksetzen" leerte das Suchfeld nicht und fehlte, wenn nur das Suchwort schuld war. | `setzeFilterZurueck()` leert auch die Suche. Der Knopf erscheint bei 0 Treffern auch mit nur einem Suchwort (mit Trefferzahl) und steht jetzt hinter den anderen Wegen. "Heute sind wir" bleibt stehen. |
| 2 | "25 Kinder oder mehr" / "25+" filterte nur mit genau 25 (gruppe_max 25 bis 39 gilt als passend). | Kleinere Änderung: Text ehrlich gemacht, jetzt "25 Kinder". Filter unverändert. |
| 3 | Gespeicherter Plan mit nicht mehr vorhandenen IDs blieb im Speicher stehen. Vormerkungen übergingen sie schon beim Anzeigen. | `ladePlan()` übernimmt nur noch bekannte IDs, der Rest wird zu einem offenen Platz. Test für Plan und Vormerkungen. |
| 4 | Satzzeichen am Ende einer Adresse (. , ; : ! ? ) und maskierte Anführungszeichen) lagen im Link. | Regex nimmt sie aus dem Link heraus. Test mit stellarium-web.org und whiteboardfox.com. Keine Adresse in den Daten endet auf ")", nichts geht verloren. |
| 5 | `elemente.json` und `elemente.js` fallen still aufeinander zurück. | Kein echtes Risiko, nichts geändert: `pruefe.py` stellt sicher, dass beide im Repo gleich sind, und beide kommen aus demselben `build.py`-Lauf. Alt wird nur, wenn jemand nur eine Datei ausliefert; das ist ein Veröffentlichungsfehler, kein App-Fehler. |

Angepasster alter Test in `rauchtest.js`: "ohne jeden Treffer" verlangte "kein Knopf, nur ein Tipp".
Das widerspricht Punkt 1; jetzt: genau ein Weg, und der leert die Suche.
