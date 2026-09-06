# DPB-Probenbuch (3. Auflage)

Zwei Dateien, eine Quelle:

- `proben-dpb.json` – **Rohtext**. 30 Proben, am 02.09.2026 automatisch aus der
  PDF-Druckvorlage (ca. 2003, 95 Seiten) extrahiert. Wird nicht mehr von Hand geändert.
- `proben-dpb-redigiert.json` – **redigierte Fassung** (06.09.2026), 28 Proben.
  Das ist die Datei, die `scripts/build.py` in die App übernimmt. Fehlt sie, fällt der
  Build auf den Rohtext zurück.

## Rechte

Die Rechte am Probenbuch liegen beim Projektinhaber (Auskunft vom 02.09.2026).
Die Elemente tragen deshalb in der App:

    quelle.name   = "DPB-Probenbuch (3. Auflage)"
    quelle.autor  = "Deutscher Pfadfinderbund"
    quelle.lizenz = "DPB-Probenbuch – Nutzung mit Erlaubnis des Rechteinhabers"

Zu ändern in `scripts/build.py`, Konstante `PROBENBUCH_QUELLE`.

## Was in der redigierten Fassung steckt

Je Probe:

| Feld | Inhalt | Herkunft |
|---|---|---|
| `wissen` | der Inhalt der Probe als lesbares Markdown | Probenbuch, redigiert |
| `prueft` | was zum Ablegen der Probe verlangt wird | Probenbuch, zusammengefasst |
| `heimabend` | Vorschlag, wie man die Probe in ~30–120 Minuten vermittelt (Ablauf mit Minuten) | Redaktion |
| `kurz` | ein bis zwei Sätze für die Kartenansicht | Redaktion |
| `kategorie`, `umfang`, `dauer_min/max`, `altersstufen`, `ort`, `material`, `vorbereitung` | Metadaten fürs Schema | Redaktion (Einschätzung) |
| `tipps` | Hinweise für die Führung: Sicherheit, Material, fehlende Abbildungen | Redaktion |
| `veraltet` | was gegenüber 2003 zu prüfen ist, sonst `null` | Redaktion |
| `bilder_noetig` | `true`, wenn die Zeichnungen des gedruckten Buchs gebraucht werden | Redaktion |
| `tags` | Suchbegriffe | Redaktion |

`build.py` setzt daraus `beschreibung` zusammen: Wissen → „Was zur Probe gehört“ →
„So bringst du es in den Heimabend“. `veraltet` und `tipps` landen in `tipps`.

Was beim Redigieren passiert ist: Zeilenumbrüche der PDF-Extraktion entfernt; zerfallene
Tabellen (Bundeseinheiten, Stände, Windrose, Sonnenstand, drei Zeittafeln) als Listen
rekonstruiert; Tippfehler der Vorlage behoben; ein Rechenfehler korrigiert (Probe 22:
Viertelkreis = 90°, nicht 45°). Der Inhalt folgt sonst dem Original – auch wo er 2003
atmet. Genau dafür gibt es `veraltet`.

Die Rückseite des Probenbuchs (Bestätigungstabellen, erforderliche Proben je Stand,
Impressum) steht in `meta`, nicht mehr im Text von Probe 30.

## Ergebnis im Build

28 Elemente, alle `bereich: pfadfindertechnik`:

- **18 Bausteine** (20–90 Minuten)
- **10 ganze Abende** (75–120 Minuten): Zeltbau, Feuerstellen, Kochen, Basteln und
  Ausbessern, Orientieren, Karte und Kompass, Erste Hilfe und die drei
  Geschichtskapitel (Nr. 27–29)

Kategorien: bundeskunde 11 · karte_kompass 5 · fahrtentechnik 3 · zelte_bauten 2 ·
natur 2 · erste_hilfe 2 · knoten 1 · feuer 1 · sonstiges 1.

## Bekannte Einschränkungen

- **Nr. 1 „Unser Bundeslied“ und Nr. 2 „Drei Lieder“ fehlen.** Es sind Liednoten, aus
  denen sich kein Text extrahieren ließ.
- **Alle Abbildungen fehlen.** Bei 15 Proben steht `bilder_noetig: true`; der Text sagt
  dort, was aus dem gedruckten Buch mitzubringen ist.
- **Stand 2003.** Erste Hilfe (Nr. 25/26) ist an aktuelle Leitlinien anzupassen – die
  wichtigsten Abweichungen stehen in `tipps`; Aufbau des Bundes, Stände, Kompass-
  Missweisung, Bünde-Landschaft und Bundesvögte (Nr. 4, 5, 20, 28, 29, 30) sind auf den
  heutigen Stand zu prüfen. Alles in `veraltet` markiert.
- **Altersstufen** je Probe sind Einschätzungen – das Probenbuch macht dazu keine Angabe,
  es nennt nur, wie viele Proben je Stand nötig sind (`meta.erforderliche_proben`).
- **Zeittafeln** (Nr. 27, 28, 29): Die Zuordnung der Ereignisse zu den Jahreszahlen wurde
  aus der zerfallenen Tabelle rekonstruiert; bei Zweifeln im gedruckten Buch nachsehen.

## Herkunft

`proben-dpb.json` wurde aus `probenbuch.pdf` außerhalb dieses Repositories erzeugt.
`proben-dpb-redigiert.json` wurde am 06.09.2026 daraus redigiert (Claude, Cowork-Sitzung).
Änderungen an den Proben gehören in die redigierte Datei; die Rohfassung bleibt als Beleg.
