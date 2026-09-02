# DPB-Probenbuch (3. Auflage)

`proben-dpb.json` enthält 30 Proben aus dem Probenbuch des Deutschen Pfadfinderbundes,
3. Auflage (Druckvorlage ca. 2003, 95 Seiten). Der Text wurde am 02.09.2026 automatisch
aus dem PDF extrahiert und liegt als Rohtext vor.

## Rechte

Die Rechte am Probenbuch liegen beim Projektinhaber (Auskunft vom 02.09.2026).
Die Elemente tragen deshalb in der App:

    quelle.name   = "DPB-Probenbuch (3. Auflage)"
    quelle.autor  = "Deutscher Pfadfinderbund"
    quelle.lizenz = "DPB-Probenbuch – Nutzung mit Erlaubnis des Rechteinhabers"

Zu ändern in `scripts/build.py`, Konstante `PROBENBUCH_QUELLE`.

## Was daraus wird

`scripts/build.py` macht daraus 28 Elemente:

- **25 Proben** (`element_typ: probe`, 30–60 Minuten) – Waldläuferzeichen, Bundeskunde,
  Fahrtengepäck, Knoten, Zeltbau, Feuerstellen, Lagerbau, Kochen, Orientieren,
  Karte und Kompass, Tierkunde, Erste Hilfe …
- **3 Projekte** (`element_typ: projekt`, Kategorie `wissen`, 90–120 Minuten) –
  die drei Geschichtskapitel (Nr. 27–29). Sie sind mit 12.500 bis 23.500 Zeichen
  zu umfangreich für eine Probe im Hauptteil und füllen einen ganzen Abend.

Die Zuordnung jeder einzelnen Probe (Typ, Kategorie, Ort, Material) steht als
nachprüfbare Tabelle in `scripts/build.py` unter `PROBENBUCH_ZUORDNUNG`.

## Bekannte Einschränkungen

- **Nr. 1 „Unser Bundeslied" und Nr. 2 „Drei Lieder" fehlen.** Es sind Liednoten,
  aus denen sich kein sinnvoller Text extrahieren ließ.
- **Alle Abbildungen fehlen.** Die Extraktion enthält nur Text. Bei Knoten, Zeltbau,
  Feuerstellen, Karte/Kompass, Tierkunde und Wundverbänden stehen deshalb
  Bildunterschriften ohne die zugehörige Zeichnung da (z. B. „Weberknoten: Zum Verbinden
  zweier etwa gleichstarker Seile"). Diese Elemente tragen in `tipps` den Hinweis,
  die Zeichnungen aus dem gedruckten Probenbuch mitzubringen.
- **Stand 2003.** Die Warnungen aus `meta.achtung_veraltet` werden beim Bauen
  automatisch in das Feld `tipps` der betroffenen Elemente übernommen:
  - Erste Hilfe und Wundverbände (Nr. 25/26) sind an aktuelle Leitlinien anzupassen,
  - Organisatorischer Aufbau, Ständeaufbau und „Der DPB" (Nr. 4/5/30) sind auf
    die heutige Struktur des Bundes zu prüfen.

## Herkunft der Datei

Erzeugt aus `probenbuch.pdf` außerhalb dieses Repositories; die Kopie hier ist die
Arbeitsgrundlage für `scripts/build.py`. Beim Neubauen wird sie nur gelesen,
nie verändert.
