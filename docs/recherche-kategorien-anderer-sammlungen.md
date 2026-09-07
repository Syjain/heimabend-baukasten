# Recherche, Teil 2: Welche Einteilungen andere Sammlungen wirklich benutzen

Stand: 07.09.2026. Fortsetzung von `recherche-spiele-apps-und-quellen.md`. Dort ging es
um den Überblick; hier wurden die Kategoriesysteme selbst ausgelesen – Infobox-Felder,
Filterlisten, Inhaltsverzeichnisse – und gegen unsere 1038 Elemente gehalten.
Kategorien sind keine Texte: Wir dürfen von jeder Sammlung *lernen, wie sie ordnet*,
auch wenn wir ihre Spiele nicht übernehmen dürfen.

Kurzfazit: Sechs Ideen sind neu und lohnen sich, drei davon speziell für Pfadfinder
(Abschnitt 3). Die Zahlen in Abschnitt 3 sagen, wie viele unserer 795 Spiele sich
heute schon automatisch zuordnen ließen.

---

## 1. Was die Sammlungen im Einzelnen benutzen

### 1.1 Scoutopedia (fr.scoutwiki.org, 399 Spiele, CC BY-SA 3.0)

Per MediaWiki-API alle 399 Seiten geholt und die Infobox `{{Infobox jeu}}` ausgezählt.

| Feld | Vorkommen | Werte (häufigste) | Für uns |
|---|---|---|---|
| `type` … `type 5` | 372 / 319 / 111 / 20 / 4 | jeu d'extérieur 146 · d'intérieur 76 · de veillée 59 · pour faire connaissance · grand jeu · aquatique · de coopération · de technique · d'adresse · de nuit · de réflexion · sensoriel · de ballon · d'observation · de prise · de relais | **Bis zu fünf Typen je Spiel** – genau unser Schluss, dass eine Kategorie nicht reicht. „Jeu de veillée" (Lagerfeuer-/Abendspiel, 99 Spiele) und „Jeu de technique" (Spiel übt Pfaditechnik, 31) haben wir nicht. |
| `équipes` | 289 | individuel 79 · 2 · plusieurs · possibles · coopératif | = unsere `sozialform`, bestätigt |
| `type terrain` | 285 | plat 58 · plat, herbu · coin veillée 12 · boisé · forêt · urbain · intérieur | Geländeart – für Heimabende nachrangig |
| `taille terrain` | 252 | petit 24 · 10–20 m · 20–30 m · grand · terrain de foot · pièce classique | **Platzbedarf** als eigenes Feld (siehe 3.3) |
| `ennui` („wird langweilig nach …") | 258, davon 115 gefüllt | au bout de quelques tours 20 · rapidement 8 · presque jamais 3 · selon la résistance physique | Originelle Idee: **Haltbarkeit** eines Spiels. Als Feld schwer objektiv; als Hinweis im Tipps-Text brauchbar. |
| Kategorien `Badge …`, `Bûchette …` | 61 / 52 / 50 / 9 | Badge louveteau bon joueur, Badge jeux, Bûchette environnement, Bûchette sécurité | **Spiele sind Abzeichen zugeordnet** – das Pendant zu unseren Proben (siehe 3.1). |

### 1.2 Spielewiki (623 unserer Spiele) – was wir noch nicht auswerten

Die Infobox `{{Spiel}}` hat sieben Pflichtfelder; wir nutzen `Art`, `AnzahlSpieler`,
`Material`, `Dauer`, `Vorbereitung`. Zwei Dinge liegen brach:

- **`Ort` (632 Werte)** ist kein drinnen/draußen, sondern Platzbedarf: „überall" 188 ·
  „beliebig" 51 · „kleine Spielfläche" 33 · **„am Tisch" 30** · „Spielfläche" 20 ·
  „kleines Spielfeld" 18 · „Spielfeld" 12 · „Sitzkreis"/„Sesselkreis"/„im Kreis" 30 ·
  „kurze Laufstrecke" 8. Daraus lässt sich ein Feld `platz` direkt ableiten.
- **`Dauer` „pro Runde" (53) und „beliebig" (146)**: Das Spiel ist rundenweise
  dehnbar – ein Lückenfüller (siehe 3.4).
- 48 verschiedene `Art`-Vorlagen, meist mehrere je Spiel (bis zu vier). Sieben Spiele
  hatten nur Vorlagen, die unser Mapping nicht kannte (Koordinations-, Entspannungs-,
  Würfel-, Darstellungs-, Partyspiel) – mit diesem Stand ergänzt, außer „Partyspiel"
  (Flaschendrehen, Kartenkuss – gehören nicht in ein Kinderwerkzeug).

### 1.3 Robert Aehnelt, Spielpädagogisches Inventar (132 Spiele, CC BY-NC-ND)

Das durchdachteste deutsche System. Drei Ebenen:

1. **Drei Kapitel = Energieverlauf**: „Volle Kraft und Action" (50) → „Ruhe durch
   Bewegung" (46, *aus der Bewegung zur Ruhe kommen*) → „Konzentration und Vertrauen"
   (45). Das ist die Anstrengungsachse, aber als *Kurve* gedacht: Mit Kapitel 2 holt
   man eine aufgedrehte Gruppe runter. Für den Planer eine schöne Regel: nach einem
   Action-Spiel ein „Ruhe durch Bewegung"-Spiel, dann erst die Probe.
2. **Drei Anforderungsskalen je Spiel** (jeweils 1–3): körperlich (Koordination, Kraft,
   Ausdauer, Gleichgewicht, Reaktion, Beweglichkeit), sozial (anfassen / sich anfassen
   lassen, Kontakt aufnehmen, sich einfügen, sich anvertrauen, sich behaupten,
   gemeinsam lösen), geistig (Konzentration, Kombination, Kreativität, Problemlösen,
   Geduld, Fantasie, Logik, Wahrnehmung). Unsere `anforderung` deckt körperlich und
   geistig ab; **die soziale Anforderung fehlt uns** (siehe 3.2).
3. **24 Index-Klassen** (Mehrfachzuordnung): Kennenlern · Ball · **Spiele mit
   verbundenen Augen** · Konzentrations-/Denk-/Logik · Warm-up/Energizer · Gelände ·
   Kreis · Kooperation · Mannschafts-/Wettkampf · **Spiele ohne Material** · Spiele mit
   Musik · New Games · Abwerf-/Abschlag-/Fang · **Spiele für die Großgruppe** ·
   Gleichgewichts-/Geschicklichkeit · Kommunikative · Kreative · Kraft-/Kampf-/Rauf ·
   Partnerspiele · **Berührungsintensive und Vertrauensspiele** · Spiele mit Seilen ·
   Schnelligkeits-/Reaktion · Strategie · Sinnes-/Wahrnehmung.

Je Spiel außerdem: Aufwand, Spielerzahl, Platzbedarf, Mindestzeit, drinnen/draußen,
Material, „zu beachten". Der Anhang „Ideenbasar" listet **Methoden zur
Gruppeneinteilung** (abzählen, nach Geburtsmonat, nach Kleidungsfarbe …) und
**Auswertungsmethoden** (Stimmungsbarometer, Streichholz-Runde, Wetterkarte) – beides
Bausteintypen, die uns fehlen (siehe 3.6).

### 1.4 anschuggerle.com (125 Beiträge, alle Rechte vorbehalten – nur lernen)

Ordnet ausschließlich nach **Zielsetzung**, und zwar persönlichkeitsbezogen:
Spaß 57 · Kooperation 34 · Wettbewerb 30 · Kommunikation 26 · Motivation 21 ·
Konzentration 19 · **Selbstvertrauen 18 · Mut 14** · Kennenlernen 12 · Erleben 11 ·
**Sensibilität 7** · Rollenbildung 4 · Aggressionsabbau 2 · Gruppeneinteilung.
Schlagwörter, die wir nicht haben: **Lückenfüller**, **laute / unruhige Gruppen**,
Nachtgeländespiel, Blind/Augenbinden, Partnerübung, Abendprogramm.

### 1.5 Methodenkartei Oldenburg (202 Methoden, CC BY)

Nur zwei Facetten, aber sauber: **Phase** (Einstieg 46 · Erarbeitung 48 · Sicherung
32 – Mehrfachnennung) und **Hashtags** (Aktivierung 29 · Kooperativ 23 · Sprechen 21 ·
Vorwissen 17 · Kreativität 17 · Textarbeit 15 · Spielerisch 15 · Feedback 10 ·
Methoden mit Arbeitsmaterial 7 · Warm-up 4). Interessanter ist die **Seitenstruktur**:
Beschreibung · **Variation** · **Differenzierung** (Anpassung an leistungsstärkere/
-schwächere) · Tipps · Material · Literatur. „Variation" und „Differenzierung" als
eigene Felder wären für uns wertvoll: 260 unserer Spiele haben Varianten im Fließtext
vergraben.

### 1.6 Verbands-Datenbanken

| Quelle | Ordnung | Neu für uns |
|---|---|---|
| **jubla.netz** (Jungwacht Blauring CH; Seite vom Server aus nicht erreichbar, Angaben aus der Anleitung) | *Blockart*: Ausbildungsblock · Lagersport · Lageraktivität · Lagerprogramm · spirituelle Animation · Gruppenstunde · **Hosensackspiel**; Tags: Grundsätze, Jahresthema | „Hosensackspiel" = Spiel aus der Hosentasche, kein Material, jederzeit. Als Begriff besser als „lazy rating". |
| **pfadi.swiss Spielesammlung** (PDF) | Kreisspiel · Drinnen · Draussen · **Nacht** · **Lagerfeuer** · **Pfaditechnik** · Sportlich | Dieselben drei Lücken wie bei Scoutopedia: Nacht, Lagerfeuer/Abend, Technik-Spiel. |
| **Jungschar Wien, Modellsuche** | Spiele · Lager · Messmodelle · Ausflüge · Basteltipps · nach Schlagworten; dazu eine eigene App „Kooperative Spiele" (>170) | Bestätigt unsere Bereiche. Keine Lizenz → nur verlinken. |
| **Scouts UK, playmeo** | (aus Teil 1) Section, Time, Cost, Setting, Type, Outcomes; playmeo: Typ, 20 Outcomes, Gruppengröße Solo–30+, Setting inkl. **Seated**, Props, Anstrengung, Facilitator Effort | „Seated" = im Sitzen spielbar – unser Platz-Feld deckt das ab. |
| **spielekartei.net** (53 Spiele) | Alter in drei Stufen · **thematische Anpassbarkeit** (anpassbar / „nur" Spaß / bringt Thema mit) · Thema (Gewaltprävention, Kooperation …) · Material ja/nein · Schlagwörter (Wachmacher, Ort kennenlernen, Ringen und raufen) | „Ort kennenlernen" (neues Heim, Lagerplatz) ist eine Wirkung, die wir nicht haben. |
| **praxis-jugendarbeit.de** | Spielart · Ort (drinnen/draußen/**im Bus**) · Material (Luftballon-, Bierdeckel-, Würfel-Spiele …) · **Anlass** (Weihnachten, Fasching, Ostern, Halloween) · **Motto** (Indianer, Ritter, Piraten, Steinzeit) · Funktion (Eisbrecher, ohne Sieger, Entspannung, Vertrauen) · Sketche/Pantomime | Anlass und Motto als Tags (siehe 3.5). |
| **gruppenspiele-hits.de** | Kennenlern · Kreis · Vertrauen · Kooperation · ohne Verlierer · Wort-/Sprachspiele · Staffel · Wasser · Wald/Gelände · Motto · Materialindex | Nichts Neues. |

### 1.7 Theorie, kurz

- **Caillois** (1958): Agon (Wettkampf) · Alea (Glück) · Mimicry (Rolle, Darstellen) ·
  Ilinx (Rausch: drehen, fallen, toben). Unser `modus` kennt nur Agon vs. Kooperation.
  Alea und Mimicry stecken bei uns in `unterkategorie` (Spielewiki: Glücksspiel 8,
  Darstellen), Ilinx nirgends – das sind die „Austoben"-Spiele, also `wirkung`.
- **Gilsdorf/Kistner, Kooperative Abenteuerspiele**: feste Reihenfolge Kennenlernen →
  Warming-up → Wahrnehmung → **Vertrauen → Kooperation → Abenteuer** → Reflexion.
  Kernaussage: Vertrauensspiele setzen eine Gruppe voraus, die schon Kooperation
  geübt hat. Das ist eine Achse **Gruppenreife** (siehe 3.2).
- **Döbler, Kleine Spiele**: Spielidee (unveränderlich) vs. Spielform (anpassbar) –
  entspricht Beschreibung vs. Variation.
- **Baden-Powell 1908** ordnet Spiele nicht nach Spielart, sondern **nach dem
  Kapitel, dessen Fertigkeit sie üben** (Tracking, Woodcraft, Camp Life, Pathfinding,
  First Aid). Genau die Idee „Spiel übt Probe".

---

## 2. Bestandsaufnahme: Welche Ideen fehlen uns wirklich?

Abgleich der oben gefundenen Achsen mit unserem Schema (Bereich, Umfang, Kategorie,
Unterkategorie, Slots, fünf Spielachsen, Alter, Dauer, Ort, Gruppe, Material,
Vorbereitung):

| Idee | Wer benutzt sie | Bei uns |
|---|---|---|
| Spiel übt eine Pfadfinder-Fertigkeit | Scoutopedia (Badges, „jeu de technique"), pfadi.swiss, Baden-Powell | **fehlt** |
| Soziale Anforderung / Gruppenreife / Körperkontakt | Aehnelt, Gilsdorf-Kistner, anschuggerle (Mut, Selbstvertrauen) | **fehlt** |
| Platzbedarf (Tisch · Zimmer · Saal/Wiese · Gelände) | Aehnelt, Scoutopedia, Spielewiki-Feld `Ort`, playmeo „Seated" | **fehlt**, Rohdaten vorhanden |
| Lückenfüller / Hosensackspiel / rundenweise dehnbar | jubla, anschuggerle, Spielewiki „pro Runde", playmeo | **fehlt**, ableitbar |
| Anlass und Motto | praxis-jugendarbeit, Aehnelt Ideenbasar | **fehlt** |
| Gruppeneinteilung, Auswertungsmethoden als Bausteine | Aehnelt, anschuggerle, Methodenkartei (Feedback), Gilsdorf-Kistner | **fehlt** (1 bzw. 2 Elemente) |
| Variation / Differenzierung als Feld | Methodenkartei, Döbler | im Fließtext vergraben |
| Nacht / im Dunkeln · Abend-/Lagerfeuerspiel | Scoutopedia, pfadi.swiss, julei, EJW | fehlt (aus Teil 1 bekannt) |
| Anstrengung als Kurve | Aehnelt, playmeo, julei | fehlt (aus Teil 1 bekannt) |
| Ziel-Kompetenzen (20 Outcomes, SPICES) | playmeo, Verbände | bewusst nicht (zu fein für Ehrenamt) |
| Kosten, Geländeart, Haltbarkeit | Scouts UK, Scoutopedia | nachrangig für Heimabende |

---

## 3. Vorschläge, mit Zahlen aus unseren Daten

Die Zählungen sind einfache Stichwortsuchen über Titel, Text, Tags und Material der
795 Spiele – sie zeigen die Größenordnung, nicht die endgültige Zuordnung.

### 3.1 `uebt` – Spiel übt eine Probe (Pfadfinder-spezifisch, höchster Wert)

**Frage:** Welche Fertigkeit aus dem Probenbuch trainiert das Spiel nebenbei?
**Werte:** dieselben wie `kategorie` bei `pfadfindertechnik` (knoten, karte_kompass,
feuer, erste_hilfe, zelte_bauten, natur, bundeskunde, fahrtentechnik), Liste.
**Ableitbar:** 76 Spiele nennen Knoten, Kompass, Karte, Morsen, Erste Hilfe, Feuer,
Zelt, Spuren oder Natur (z. B. Anschleichen üben, Kimspiele, Morse-Staffeln).
**Nutzen:** Im Planer neben einer Probe „Spiele, die das üben" anbieten. Das kann keine
der allgemeinen Spiele-Apps – nur ein Pfadfinder-Werkzeug. Scoutopedias 31 „jeux de
technique" wären bei einem Import hier zu Hause.

### 3.2 `naehe` – Wie viel Vertrauen und Körperkontakt verlangt das Spiel?

**Frage:** Kann ich das mit einer neuen Gruppe spielen, oder braucht es eine Sippe,
die sich kennt? (Gilsdorf/Kistner-Sequenz, Aehnelts „soziale Anforderung",
anschuggerles Mut/Selbstvertrauen.)
**Werte:** `keine` (kein Kontakt, kein Sich-Zeigen) · `leicht` (Hände halten, Namen
rufen, sich vorstellen) · `hoch` (Augen verbunden, getragen werden, sich anvertrauen,
Massagen, vor der Gruppe allein etwas tun).
**Ableitbar:** 66 Spiele mit verbundenen Augen, grob 190 mit Berührungswörtern
(anfassen, umarmen, huckepack, tragen, Schoß) – die Regex ist noch zu weit, aber die
Menge stimmt. Bestehende `wirkung: vertrauen` ist der Kern von `hoch`.
**Nutzen:** Der wichtigste Filter für Gruppenführer mit einer frischen Sippe oder mit
Pubertierenden. Kein deutsches Tool bietet ihn.

### 3.3 `platz` – Wie viel Platz braucht es?

**Werte:** `tisch` (im Sitzen, am Tisch, Stuhlkreis) · `zimmer` (kleine Spielfläche,
Gruppenraum) · `saal_wiese` (Laufstrecke, Spielfeld, Turnhalle, Wiese) · `gelaende`
(Wald, Stadt, großes Gebiet).
**Ableitbar:** Spielewiki liefert das Feld `Ort` für 632 Spiele fertig („am Tisch" 30,
Sitzkreis 30, „kleine Spielfläche" 33, „Spielfeld" 30, „überall/beliebig" 239 = tisch
oder zimmer); Text nennt Gelände/Wald/Spielfeld bei 138. pfadfinder-spiele.de hat ein
Feld „Umgebung".
**Nutzen:** Heime sind oft klein. „Was geht bei Regen in unserem Raum?" ist die
häufigste Frage im Winter und unser `ort: drinnen` beantwortet sie nicht – ein
Fangspiel „drinnen" braucht eine Turnhalle.

### 3.4 `hosensackspiel` – Lückenfüller (jubla-Begriff)

**Regel:** kein Material, keine Vorbereitung, `dauer_min` ≤ 10 **oder** rundenweise
dehnbar (Spielewiki-Dauer „pro Runde"/„beliebig").
**Ableitbar:** 77 Spiele erfüllen die harte Regel heute, 53 weitere sind „pro Runde",
146 „beliebig".
**Nutzen:** Planer-Knopf „5 Minuten übrig" und der Abschnitt „ohne alles" auf der
Startseite. Ersetzt das vorgeschlagene `faulheit` (Kennzahl) durch ein klares Ja/Nein
mit deutschem Namen.

### 3.5 `anlass[]` – Jahreszeit, Fest, Motto

**Werte:** weihnachten · fasching · ostern · halloween · sommer_wasser · winter_schnee ·
Motto-Tags (piraten, ritter, indianer, detektiv, zirkus, weltraum …).
**Ableitbar:** 19 Spiele mit Festen, 30 mit Motto, 7 echte Wasserspiele; Inspirator-
Themen und eigene „Themenabende" liefern mehr. Klein, aber bei einer Scoutopedia-
Übernahme (99 Lagerfeuerspiele) und den Inspirator-Themenabenden wächst es.
**Nutzen:** „Was machen wir am letzten Heimabend vor Weihnachten?" – ein Filter, keine
Navigation.

### 3.6 Zwei neue Bausteintypen für `gemeinschaft` (34 Elemente, unser dünnster Bereich)

- **Gruppeneinteilung**: bei uns 1 Element, bei Aehnelt und anschuggerle eigene
  Klasse. Zehn Methoden (abzählen, Geburtsmonat, Kleidungsfarbe, Silbenzahl, Bonbons)
  lassen sich als eigene Sammlung schreiben – gemeinfreie Allgemeingüter.
- **Auswertung/Reflexion**: bei uns 2 Elemente; Aehnelts Ideenbasar, die Methodenkartei
  (CC BY, Hashtag Feedback 10) und Gilsdorf/Kistner nennen ein Dutzend
  (Stimmungsbarometer, Blitzlicht, Wetterkarte, Daumen, Fünf-Finger). Passt in den
  Slot `abschluss` und in den Schlusskreis.

Für `gemeinschaft` ergäbe das erstmals eine `kategorie`: gespraech · reflexion ·
einteilung · beteiligung · gute_tat.

### 3.7 Felder statt Achsen: `variation` und `differenzierung`

260 Spiele haben „Variante/Abwandlung" im Fließtext. Ein eigenes Feld `varianten`
(wie `tipps`) macht das sichtbar; `differenzierung` („für Wölflinge einfacher: …",
„für Ältere schwerer: …") ist die Methodenkartei-Idee, die wir bei eigenen Ideen
gleich mitschreiben sollten.

### 3.8 Aus Teil 1 weiter gültig

`anstrengung` (Aehnelt zeigt, dass sie als *Kurve* im Planer wirkt: Action → Ruhe
durch Bewegung → Konzentration), `im_dunkeln` (41 Treffer), `sprache_noetig` (107
Sing-, Klatsch- und Darstellungsspiele als „wenig"). Dazu neu aus Scoutopedia/pfadi.swiss
ein Wert `wirkung: lagerfeuer` (Abendspiel im Sitzen, „jeu de veillée").

---

## 4. Reihenfolge, wenn wir bauen

1. **`platz`** – Rohdaten liegen fertig im Spielewiki-Feld `Ort`, eine Stunde Arbeit,
   sofort spürbar im Heim.
2. **`hosensackspiel`** – reine Regel über vorhandene Felder, Planer-Knopf.
3. **`uebt`** – Stichwortsuche plus Korrekturliste; Pfadfinder-Alleinstellungsmerkmal.
4. **`naehe`** – braucht eine sorgfältige Stichprobe (Regex zu weit), lohnt aber am
   meisten für neue Gruppen.
5. `anstrengung`, `im_dunkeln`, `sprache_noetig`, `anlass` – wie in Teil 1 beschrieben.
6. Gemeinschaft-Kategorie mit eigenen Bausteinen für Einteilung und Auswertung.

Alle Achsen laufen nach dem bewährten Muster: Tags → Text → `redaktion.json`.

---

## 5. Quellen dieser Runde

- Scoutopedia: https://fr.scoutwiki.org/Catégorie:Jeu (API-Auszählung 07.09.2026)
- Spielewiki-Rohdaten: `data/quellen/spielewiki/raw/seiten.json`
- Robert Aehnelt, Spielpädagogisches Inventar Vol. 3 (2011), PDF, CC BY-NC-ND
- anschuggerle.com (Paul Beck), WordPress-API: 125 Beiträge, 24 Kategorien; Impressum: alle Rechte vorbehalten
- Methodenkartei Oldenburg/Vechta: https://www.methodenkartei.uni-oldenburg.de/methoden/
- jubla.netz: Anleitung (Atlassian-Wiki), pfadi-toolbox.ch
- pfadi.swiss, Spielesammlung internationale Kursinhalte (Download-Seite)
- Jungschar Wien: https://wien.jungschar.at/modellsuche
- spielekartei.net, praxis-jugendarbeit.de, gruppenspiele-hits.de (nur Gliederung)
- Baden-Powell, Scouting for Boys (1908), Gutenberg #65993
- Caillois, Les jeux et les hommes (1958); Gilsdorf/Kistner, Kooperative Abenteuerspiele 1; Döbler/Döbler, Kleine Spiele
- Nicht erreichbar vom Arbeitsrechner: pfadispiele.ch, julei-app.de, jugendleiter-blog.de, spiele.wien.jungschar.at, ludologie.de
