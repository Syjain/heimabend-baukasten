# Datenqualität der ersten Reihe – was geändert wurde und was offen ist

Stand: 18.10.2026 · Arbeitsgrundlage: die 580 Elemente mit `kern: true` aus `data/elemente.json`
(299 Spiele, 281 andere). Geändert wurden nur Daten und `scripts/build.py`; `web/index.html` ist unberührt.
Alle Korrekturen stehen mit Begründung in `data/redaktion.json`, nichts wurde gelöscht, nichts gepusht.
Die Texte der Quellen sind nicht angefasst – `python3 scripts/build.py` setzt die Korrekturen bei jedem Lauf
neu auf die Quellen auf (zweimal gelaufen, die Ausgabe ist beim zweiten Lauf bytegleich).

## 1. Zahlen vorher und nachher

| | vorher | nachher |
|---|---:|---:|
| Elemente insgesamt | 1075 | 1075 |
| erste Reihe | 580 | 575 |
| davon Spiele | 299 | 299 |
| Spiele der ersten Reihe **mit** Tipps für die Spielleitung | 18 | 150 |
| Spiele der ersten Reihe ohne Tipps | 281 | 149 |
| erste Reihe ohne Tipps (alle Bereiche) | 448 | 312 |
| Elemente mit geschütztem Leerzeichen im Text (Rest der Webseiten-Formatierung) | 76 | 0 |
| Material-Platzhalter „Diverses“ | 8 | 0 |
| Spiele mit Gruppengröße „N bis N“ aus „etwa N“ | 15 | 2 (beide sind echt: Liegestütz-Viereck, Alle meine Entlein) |
| Spiele mit Höchstgröße unter 2 | 4 | 0 |
| Spiele mit leerem Material, obwohl die Quelle welches nennt | 11 | 4 (dort ist das Material laut Quelle freiwillig oder „keinerlei“) |
| Material mit abgeschnittenem Eintrag („…“) | 8 | 3 |
| Verweise auf Links, Videos, Downloads, die nicht in den Daten stehen | 8 | 0 |
| Wiki-Überschrift im Feld Tipps | 3 | 0 |
| Erste Reihe mit „Auch bekannt als“ | 47 | 54 |

Der Rauchtest (`scripts/rauchtest.js`) läuft ohne Fehler: **0 Fehler von 111 Prüfungen**. Auf dem Rechner ist
kein Node installiert; der Test lief deshalb in der Browser-Vorschau gegen die frisch gebauten Dateien.

## 2. Was geändert wurde

### 2.1 Tipps für die Spielleitung (137 Spiele)

Kurze, praktische Hinweise, die sich aus Ablauf und Sicherheitsfragen der jeweiligen Beschreibung ergeben:
Spielfeld abgrenzen, Stoppsignal vereinbaren, weicher Ball, nicht auf den Kopf zielen, Allergien bei
Süßigkeiten und Gummibärchen (Gelatine), Einverständnis bei Körperkontakt, Aufsicht beim Hochheben, bei
Augenbinden, bei Feuer und bei Trampolin und Kletterrahmen. Es wurden keine Regeln erfunden; wo die Quelle
selbst warnt (Himmel auf Erden, Hugo mit Vorschlaghammer, Pferdebändiger, Streichholz-Feuerwerk), steht die
Warnung jetzt in den Tipps. Ausgewählt wurden bekannte Klassiker und Spiele mit Sicherheitsaspekt; eine
Nutzungszählung gibt es nicht, die Auswahl ist ein Urteil.

### 2.2 Plausibilität von Dauer, Gruppengröße, Material, Ort

- **Gruppengröße (25 Felder):** Der Import hat Angaben wie „etwa 10“, „beliebig, rund 10“, „6 Personen oder mehr“
  als feste Größe „10 bis 10“ gelesen. Bei 23 Spielen fällt jetzt die Obergrenze weg, bei Baumball (5–20),
  Häschen-Spiel (ab 3) und Zwei Fünfecke (bis 20) steht die Zahl aus der Quelle. Spiele für „zwei Personen
  je Runde“ oder „einer“ (1 2 3, 52 Einsammeln, Seilspringen, Zehnerln, Topfschlagen, Armdrücken, Mumie)
  sind nicht mehr auf 1–2 Personen begrenzt, weil die Quelle mehrere Paare oder ein Publikum vorsieht.
- **Dauer (4):** „wenige Sekunden“ (Schere Stein Papier) und „eine Minute“ (Eine Minute, Minutenweg,
  Liegestütz-Kampf) standen als 10–20 Minuten.
- **Ort und Platz (11 Platz-, 4 Ortsangaben):** „Sitzkreis“ und „am Boden“ waren als „am Tisch“ eingelesen (9 Spiele);
  Fotograf, Flaschenhals, Förderband, Liegestütz-Kampf standen nur als „drinnen“; Himmel auf Erden (Spielplatz)
  als Zimmer.
- **Nähe (5):** Körperteil-Twister und Telefax (Berührung) standen auf „keine“; Topfschlagen,
  Geschmackskim und Fahrbahnen auf „hoch“, nur weil eine Augenbinde vorkommt.
- **Material (28 Elemente):** acht Platzhalter „Diverses“ durch das konkrete Material der Quelle ersetzt,
  acht Spiele ohne Material, obwohl die Quelle welches verlangt (Socken, Karten, Stift, Taler …),
  an Kommas zerrissene Einträge (Schwebende Stange, Bruchenball, „ähnliches“), abgeschnittene Wörter bei
  fünf Inspirator-Elementen. Die Geräteachse (`spielgeraet`) wurde dort von Hand nachgezogen, wo die Automatik
  aus dem neuen Material Unsinn ableitete (zum Beispiel „Papierknäuel“ = Papier und Stift).
- **Kurztexte:** Glockenklang (bestand nur aus Überschriften der Quelle), Sockenkampf (endete auf „Vorbereitung“),
  Verstecken (Wikisatz „Dieser Artikel beschreibt …“).

### 2.3 Tippfehler, abgeschnittene Texte, Reste der Quell-Formatierung

- **Rechtschreibprüfung:** alle Texte der ersten Reihe mit dem deutschen macOS-Wörterbuch geprüft
  (1 265 Auffälligkeiten, danach von Hand durchgesehen). Ersetzt wurden 158 Stellen in rund 100 Elementen:
  „veranstaleten“, „Hilfsmitttel“, „Kovertüre“, „Lautpsrecher“, „Seilten“, „mit mit“, „stehen stehen“ und
  Ähnliches. Zwei Titel mit Tippfehler wurden korrigiert (Kröten ohne Hilfsmittel aufbauen, PC-Lautsprecher
  selber bauen); die App zeigt sie dadurch als „umbenannt“.
- **Tote Verweise:** „Link zum Dokument“, „Download“, „YouTube Video Lulale“, „[Link gekürzt]“ und Ähnliches
  (Insektenhotel, Milchkarton-Portmonnaie, Augenklappe, Waldläuferzeichen-Memory, Pfadi-Stories,
  Digitales Tabu, Drachenbau, Papier-Recycling).
- **Abgebrochene Texte:** Sippenchronik (Schlusspunkt), Namensschilder (letzter Satz brach ab, entfernt),
  Haik-Küche (Rezept bricht mitten im Satz ab – der Text sagt das jetzt offen, siehe Fragen).
- **Quell-Formatierung (fünf Regeln unter `bereinigung`):** 158 geschützte Leerzeichen, 66 Leerzeilen aus
  nichts als Leerzeichen, 15 leere Aufzählungspunkte, 67 mehrfache Leerzeilen, 26 doppelte Leerzeichen.
  Die HTML-Vorlage in der Sippen-Homepage bleibt eingerückt.
- **Unicode:** ein Text (Namensschilder einnähen) hatte „ä“ als a plus Trema; `build.py` bringt jetzt alle
  Texte in die Normalform, sonst findet die App-Suche das Wort nicht.

### 2.4 Beinahe-Dubletten in der ersten Reihe

Neun Paare und Dreiergruppen sind jetzt unter „Auch bekannt als“ zusammengelegt (`zusammengelegt`);
bei unverträglichen Lizenzen wandert wie bisher nur der Titel, nie Text:

| Hauptelement | Variante(n) |
|---|---|
| Sardinli (Spielewiki) | Sardine (pfadfinder-spiele.de) |
| Lärmwand | Das Schreispiel |
| Wer bin ich (Spielewiki) | Wer bin ich? (Inspirator) |
| Papierflieger-Wettkampf | Papierflieger Wettbewerb (Inspirator) |
| Seilbrücke bauen (eigene) | Seilbrücke bauen (Inspirator) |
| Capture the Flag | Capture the Flag im Dunkeln und Fahnenraub im Wald (beide eigene) |
| Verstecken | Versteck-fangen |
| Geschmacks-Kim: Blind-Tasting (eigene) | Geschmackskim |
| Blitzlicht-Runde (eigene) | Blitzlicht-Reflexion |

Der **Gitarrenkurs** besteht nur aus einer Linksammlung ohne die Links und steht jetzt in der zweiten Reihe.
Dadurch rücken sechs Spiele über die Quote je Unterkategorie in die erste Reihe nach (Angeln, Der Kaiser
schickt Soldaten aus, Geisterbahn, Geocaching, Papierknäuel-Reflexion, Tastkim); sie haben Tipps bekommen.
Sechs weitere Spiele würden durch die Material-Korrekturen aus der Punkterechnung fallen (Ameisenkönig,
Rüppel Tüppel, Offen oder geschlossen weitergeben) bzw. nachrücken (Kalaha, Mafia, Zahlensumme); sie sind
unter `kern` von Hand festgehalten, damit sich die Auswahl durch Datenpflege nicht still verschiebt.
Alles ist mit einer Zeile in `redaktion.json` umkehrbar.

### 2.5 Änderungen an `scripts/build.py`

Nötig, damit die Korrekturen redaktionell bleiben: neue Schlüssel `ersetzungen` und `bereinigung`
(beschrieben in `data/SCHEMA.md`), `null` in `felder` entfernt ein optionales Feld, NFC-Normalisierung.
Fehlen die Schlüssel, läuft das Skript wie vorher. Eine nicht gefundene Ersetzung wird beim Bauen gemeldet.

## 3. Was bewusst nicht geändert wurde

- **Sprache.** Die fünf Sprachfragen aus `docs/sprache.md` (Sippe oder Horte/Gilde, Spielleitung oder
  Gruppenführer, Gendern, Tonfall, Umschreiben fremder Texte) sind noch offen; deshalb wurde kein Wort
  ersetzt außer Schreibfehlern. Zum Beispiel steht in „Stufenspiel“ weiter die Anrede „Teilen Sie …“.
- Keine neuen Quellen, keine Abbildungen aus dem Probenbuch, keine Eingriffe in Fremdtexte außer den
  oben genannten Fehlerkorrekturen.

## 4. Offene Fragen für Yannick

1. **Mindestzahlen.** Atomspiel und Gleichstrom Wechselstrom stehen auf „ab 20“, obwohl der Quelltext von
   Gleichstrom ausdrücklich sagt, es sei auch mit weniger spielbar. Soll ich sie auf 10 setzen? (Ich habe es
   nicht getan, weil die Quelle keine Zahl nennt.) Weitere 40 Spiele brauchen 15 oder mehr Personen
   (siehe Nachtschicht 09.09.).
2. **Weitere Beinahe-Dubletten, bewusst nicht zusammengelegt**, weil Umfang oder Zweck verschieden sind:
   Schmuggeln / Schmuggler*innen-Spiel (Wald gegen Dorf, das zweite hat schon eine Variante), Morsen lernen /
   Morse-Abend, Geheimschriften / Geheimschriften und Codes, Sternenhimmel erkunden / Sternenkunde-Abend,
   Stockbrot-Upgrade / Stockbrot und Lagerfeuer, Kochduell (drei Fassungen), Zeltbau (Kohte blind aufbauen,
   Kröten ohne Hilfsmittel, Neue Zeltkonstruktionen, Kohten- und Jurtenbau-Training, Zeltbau), Müllsammeln /
   Müll-Rallye, Halstuchknoten (selber machen / schnitzen), Schatzsuche (vier Fassungen), Daumenprobe /
   Stimmungsrunde mit der Hand, Stille Post mit Telefax, Epidemie und Pantomime. Zusammenlegen oder so lassen?
3. **Inhalt, der dir vielleicht nicht passt** (nichts geändert, nur gemeldet):
   - *Lateral* nennt als Beispiele Tötungs- und Suizidrätsel; der Tipp warnt, die Beispiele stehen weiter im Text.
   - *Funky Chicken* nennt eine Figur „Gay tiger“ und eine „Toilet Diver“.
   - *Liebst du mich* (Antwort „Ja, mein Schatz, ich liebe dich …“) und *Ameisenkönig* (Strafen, Arbeitsdienst,
     45–90 Minuten) für Wölflinge.
   - *Peng* und *Hase und Jäger* zielen mit Fingerpistolen; die Quelle bietet beim Peng eine Alternative (im Tipp genannt).
   - *Kontinentespiel*: „gerade Jungen nicht zu grob“ im Tipp-Text der Quelle.
   - *Drei Chinesen mit dem Kontrabass*, *Murmeln … aber in geil!*: Titel der Quelle.
4. **Unvollständige Quellen.** *Haik-Küche üben*: das Rezept bricht ab (jetzt mit Hinweis). *Pfadi-Stories*:
   das Rätsel hat keine Auflösung mehr (sie stand hinter einem Link). *Gitarrenkurs*: nur Links (zweite Reihe).
   Drei Materiallisten des Inspirators bleiben mit „…“ abgeschnitten (Action Painting, Handcreme, DNA isolieren).
5. **Dauer und Vorbereitung bei Inspirator-Bausteinen.** Die Dauer sind Stufen (10–30, 30–45, 45–75 …), keine
   Messung; *Rollenspielprojekt über mehrere Wochen* steht mit 10–30 Minuten. Alle Inspirator-Bastelideen haben
   Vorbereitung „gering“, auch mit 13 Materialien (Hüttenlicht, Lilien-Kekse, Rotkohl-Farborgel). Pauschal auf
   „mittel“ ab sechs Materialien?
6. **Altersstufen** fehlen bei 243 der 575 Elemente der ersten Reihe (gilt als „alle“). Für *Knieboxen*,
   *Bruchenball*, *Liegestütz-Kampf*, *Pflöckeln* und *Nageln* wäre eine Altersangabe sinnvoll; bisher steht nur
   bei Pflöckeln und Nageln eine.
7. **Zuzwinckern** (pfadfinder-spiele.de) schreibt sich in der Quelle mit „ck“; geändert habe ich es nicht.
8. **Weitere Tipps.** 149 Kern-Spiele und 163 Kern-Bausteine anderer Bereiche haben weiter keine Tipps.
   Soll ich die Bausteine (Basteln, Kochen, Natur) in einem zweiten Durchgang bearbeiten?
