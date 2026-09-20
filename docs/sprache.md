# Sprache und Begriffe im Heimabend-Baukasten

Stand: **20.09.2026 – die fünf Entscheidungen sind getroffen** (siehe Abschnitt 0).
Zahlenstand der Erhebung: 09.09.2026 · Grundlage: `data/elemente.json` (1037 Elemente, selbst nachgezählt),
`docs/heimabend-definition.md`, das DPB-Probenbuch (die 28 Elemente mit dem id-Präfix `pb-`),
`data/SCHEMA.md` und `docs/pruefung-2026-09/begriffe.csv`.

## 0. Was am 20.09.2026 entschieden wurde

Die fünf Fragen aus Abschnitt 2 sind beantwortet. Die Begründungen stehen dort, die
Umsetzung in `data/sprache.json`. Kurzfassung:

| | Frage | Entscheidung vom 20.09.2026 |
|---|---|---|
| (a) | Sippe oder Horte/Gilde? | **Horte/Gilde – überall**, auch in fremden Texten. Im neutralen Spieltext steht die Paarform „Horte/Gilde“, weil „Horte“ allein für eine Mädchengruppe falsch wäre und das Probenbuch die beiden selbst als Paar schreibt. |
| (b) | Spielleitung oder Gruppenführer? | **„Spielleitung“ bleibt** – die 203 Elemente werden nicht angefasst. Nur die Fremdwörter „Betreuer“ und „Gruppenleiter“ werden auf die Spielleitung gezogen. („Teamer“ kommt in den Daten 0× vor.) |
| (c) | Welche Genderschreibweise? | **Paarform bzw. Schrägstrich wie im Probenbuch.** Doppelpunkt, Sternchen und Unterstrich werden beim Anzeigen aufgelöst. |
| (d) | Tonfall? | **Bleibt, wie die Quelle ihn schreibt.** Es wird nicht umformuliert. |
| (e) | Fremdtexte ändern? | **Nur, wo ein Wort für den DPB sachlich falsch ist**, nicht aus Stilgründen – mit Änderungshinweis in der App. |

Dazu gehören zwei Festlegungen, die nicht zur Debatte standen:

- **Das DPB-Probenbuch (28 Elemente, Präfix `pb-`) wird nicht angefasst.** Es ist der Maßstab,
  aus dem die Wörter kommen; außerdem liegen die Rechte beim Bund und nicht bei einer CC-Lizenz.
  In `data/sprache.json` steht es unter `meta.ausser_praefixe`.
- **Die Ersetzung passiert beim Anzeigen, nicht in den Daten** – Weg B aus Abschnitt 4, in der
  App „die Brille“ genannt. In `data/elemente.json` steht weiter „Sippe“, die App zeigt
  „Horte/Gilde“. Nimmt man die Brille ab, ist das Original wieder da.

---

## 1. Wozu dieses Dokument da ist

Die Sammlung stammt aus fünf Quellen und aus fremden Bünden, deshalb stehen unterschiedliche
Wörter für dieselbe Sache nebeneinander: „Sippe" neben „Horte/Gilde", „Spielleitung" neben
„Gruppenführer", drei verschiedene Genderschreibweisen, „Gruppenstunde" neben „Heimabend".
Dieses Dokument sammelt an einer Stelle, welche Wörter betroffen sind, wie oft sie vorkommen und
was das Probenbuch dazu sagt. Es hat fünf Entscheidungen so vorgelegt, dass sie in wenigen Minuten
zu treffen waren; seit dem 20.09.2026 sind sie getroffen (Abschnitt 0). Jetzt ist es das
Wörterbuch, gegen das man `data/sprache.json` prüfen kann. Es ist bewusst kein Stilhandbuch –
nur die Fragen, an denen viele Elemente hängen.

> **An den Daten hat sich nichts geändert.** Dieses Dokument ändert keine Datei in `data/`, und
> `data/elemente.json` ist von den Entscheidungen unberührt geblieben: die Ersetzung passiert
> beim Anzeigen (Abschnitt 4, Weg B). Geändert hat sich die Anzeige – und dafür ist
> `data/sprache.json` dazugekommen.

### Wie die Zahlen entstanden sind

Alle Zahlen in diesem Dokument sind selbst aus `data/elemente.json` gezählt, nicht aus
`begriffe.csv` übernommen. Gesucht wurde in den Feldern `titel`, `kurz`, `beschreibung`, `tipps`
sowie in den Listen `tags`, `themen` und `material` – also in allem, was die App als Text anzeigt.

- **El.** = Zahl der Elemente, in denen der Begriff mindestens einmal vorkommt.
- **Tr.** = Zahl aller Fundstellen (ein Element kann mehrere haben).
- Ein *Muster* (auch: regulärer Ausdruck) ist eine Suchregel, die auch Wortformen findet –
  „Sipp" findet Sippe, Sippen, Sippling und Sippenführer.

Nicht mitgezählt sind die Felder, die am 08./09.09.2026 neu dazugekommen sind (`varianten` mit
seinem Textfeld `aenderung`, dazu `kern`, `platz`, `uebt`, `naehe`, `hosensackspiel`). Sobald in
`varianten.aenderung` eigene Sätze stehen, gehören sie in die nächste Zählung. Die Zahl der
Elemente war zum Zeitpunkt der Zählung unverändert 1037; falls die Kernsammlung (`kern: false`)
später Elemente ausblendet, sinken alle Zahlen unten entsprechend.

Wo meine Zahl von der aus `begriffe.csv` abweicht, stehen unten **beide** Zahlen. Die Abweichungen
kommen daher, dass die Prüfung teils breiter oder enger gesucht hat als ich; welche Zahl stimmt,
hängt daran, was man mitzählen will. Bei den fünf Grundsatzfragen stimmen meine Zahlen mit der CSV
überein – dort ist die Grundlage also unstrittig.

### Was ich am Probenbuch nachgeprüft habe

Maßstab für „unser Wort" ist das DPB-Probenbuch, das selbst in der Sammlung steht (28 Elemente,
id-Präfix `pb-`). Ich habe die Liste aus dem Prüfdokument nicht geglaubt, sondern nachgezählt.

**Bestätigt** (Zahl = Elemente von 28 / Fundstellen):

| Wort | pb-El. | Tr. | Beispiel-Element |
|---|---:|---:|---|
| Heimabend | 28 | 47 | in **allen** 28 Proben |
| Probe | 28 | 148 | in allen 28 Proben |
| Kohte | 5 | 45 | `pb-zeltbau` |
| Kluft | 8 | 35 | `pb-unsere-kluft` |
| Wölfling | 8 | 34 | `pb-staendeaufbau-des-dpb` |
| Halstuch | 5 | 22 | `pb-unsere-kluft` |
| Jungenschaft | 5 | 21 | `pb-organisatorischer-aufbau` |
| Versprechen | 6 | 20 | `pb-pfadfindergruss-und-pfadfinderversprechen` |
| Horte | 6 | 14 | `pb-organisatorischer-aufbau` |
| Stamm (als Einheit) | 5 | 13 | `pb-organisatorischer-aufbau` |
| Jurte | 3 | 11 | `pb-knoten-und-buende` |
| Gau | 4 | 10 | `pb-staendeaufbau-des-dpb` |
| Späher | 4 | 8 | `pb-staendeaufbau-des-dpb` |
| Trupp | 2 | 6 | `pb-organisatorischer-aufbau` |
| Gilde | 2 | 6 | `pb-organisatorischer-aufbau` |
| Knappe | 2 | 5 | `pb-staendeaufbau-des-dpb` |
| Neuling | 2 | 3 | `pb-staendeaufbau-des-dpb` |
| Kornett | 1 | 3 | `pb-aufgaben-in-der-gruppe` |
| Gildin | 2 | 3 | `pb-pfadfindergruss-und-pfadfinderversprechen` |
| Mädelschaft | 2 | 3 | `pb-organisatorischer-aufbau` |
| „Allzeit bereit" | 1 | 3 | `pb-pfadfindergruss-und-pfadfinderversprechen` |
| Wildling | 1 | 2 | `pb-staendeaufbau-des-dpb` |
| Jungwolf | 2 | 2 | `pb-staendeaufbau-des-dpb` |
| Jungpfadfinderin | 2 | 2 | `pb-staendeaufbau-des-dpb` |
| Gildenmädchen | 2 | 2 | `pb-staendeaufbau-des-dpb` |
| Pfadfinderring | 1 | 1 | `pb-organisatorischer-aufbau` |
| Hag | 1 | 1 | `pb-organisatorischer-aufbau` |
| Landesmark | 1 | 1 | `pb-organisatorischer-aufbau` |

Alle 28 Begriffe aus dem Prüfdokument sind damit **bestätigt**. Drei kommen allerdings nur ein
einziges Mal vor, und zwar alle drei in derselben Probe `pb-organisatorischer-aufbau`: Hag,
Pfadfinderring und Landesmark. Sie sind belegt, aber nicht eingeführt – wer nur die App liest,
begegnet ihnen genau einmal.

**Nicht belegt – also im Probenbuch null Fundstellen:** Sippe (0), Meute (0), Gruppenstunde (0),
Spielleitung (0), Gruppenführer (0), Jungschar (0), „Gut Pfad" (0), Gendersternchen/-doppelpunkt/
-unterstrich (0). „Sippe" kommt im Probenbuch tatsächlich kein einziges Mal vor – das bestätigt die
Angabe im Prüfdokument.

**Was ich zusätzlich gefunden habe und was das Prüfdokument nicht sagt:**

- Das Probenbuch benutzt für die Rolle **„Führer" / „Führerin"** (6 Elemente, 18 Fundstellen),
  nicht „Gruppenführer". Wörtlich in `pb-organisatorischer-aufbau`: „Fünf Mädchen und eine
  Führerin oder fünf Jungen und ein Führer."
- Das Probenbuch gendert mit **Paarform und Schrägstrich** („Horten/Gilden", „Jungen/Mädchen",
  „Führer/Führerin"), nie mit Sonderzeichen. Für Frage (c) ist das die einzige belegte Hausform.
- „Horte" und „Gilde" sind **nicht** dasselbe Wort in zwei Schreibweisen: Horte = Jungengruppe,
  Gilde = Mädchengruppe, beide ab 5 Mitgliedern. Ein Skript darf „Sippe" also nicht einfach durch
  „Horte" ersetzen.
- „Tracht" (2 Elemente) und „Uniform" (2 Elemente) stehen im Probenbuch **erklärend und in
  Abgrenzung**: „Die Kluft ist keine Uniform und will uns auch nicht uniformieren."
  Eine mechanische Ersetzung „Uniform" → „Kluft" würde diesen Satz zerstören.

---

## 2. Die fünf Entscheidungen

### (a) Heißt die kleine Gruppe „Sippe" oder „Horte/Gilde"?

**Die Frage in einem Satz:** Wie nennen wir in der App die kleinste Einheit – so wie deine eigene
Sammlung sie heute nennt („Sippe") oder so wie das Probenbuch sie nennt („Horte" für Jungen,
„Gilde" für Mädchen)?

**Was das Probenbuch sagt:** „Sippe" kommt in den 28 pb-Elementen **null** Mal vor. „Horte" steht
in 6 Elementen (14 Fundstellen), „Gilde" in 2 (6 Fundstellen), beide ab 5 Mitgliedern. Das
Probenbuch schreibt sie durchgängig als Paar: „Horten/Gilden".

**Was die Sammlung heute tut:** 88 Elemente enthalten „Sipp…", mit 227 Fundstellen. Meine Zahl
stimmt mit `begriffe.csv` überein (88 / 227). Aufteilung: **79 Inspirator** (CC BY-NC 4.0),
**9 eigene** (CC BY-SA 4.0). In **11 Titeln** steht das Wort, davon 6 aus dem Inspirator und
**5 eigene**: `eig-sippenwimpel-gestalten`, `eig-eigenes-sippenlied-dichten`, `eig-sippenvertrag-unsere-regeln`,
`eig-kooperationsaufgaben-die-sippe-als-team`, `eig-die-gruppe-uebernimmt-heimabend-von-der-sippe`.
Dem stehen 9 Elemente mit „Horte/Gilde" gegenüber (26 Fundstellen; CSV: 24) – 8 davon aus dem
Probenbuch, 1 aus dem Spielewiki. Zusätzlich steckt in 17 Inspirator-Elementen das Wort
„Sippling" für das einzelne Kind – dafür hat das Probenbuch überhaupt kein Wort.

**Möglichkeiten:**

| | Möglichkeit | Folgen |
|---|---|---|
| 1 | **„Sippe" bleibt.** Horte/Gilde nur dort, wo das Probenbuch zitiert wird. | 0 Elemente anzufassen. Eigene Titel bleiben. Widerspruch zum Probenbuch bleibt sichtbar (die App sagt „Sippe", die Probe daneben sagt „Horte"). Späterer Wechsel kostet dann 88 Elemente. |
| 2 | **„Horte/Gilde" ist unser Wort, aber nur eigene Texte werden umgeschrieben.** Fremde Texte bleiben wörtlich. | 9 Elemente + 5 Titel anzufassen, alle eigene (CC BY-SA, kein Lizenzproblem, kein Änderungshinweis nötig, weil du selbst der Urheber bist). 79 Inspirator-Elemente sagen weiter „Sippe" – zwei Wörter in einer App, aber der Widerspruch ist erklärbar („so steht es in der Quelle"). Späterer voller Wechsel kostet noch 79 Elemente. |
| 3 | **„Horte/Gilde" überall, auch in fremden Texten.** | 88 Elemente, 227 Fundstellen. Bei 79 davon (Inspirator, CC BY-NC) ist ein Änderungshinweis Pflicht (siehe (e)). Keine mechanische Ersetzung möglich: „Sippe" → „Horte" wäre für Mädchengruppen falsch, „Sippenführer" → „Hortenführer/Gildenführerin", „Sippling" hat gar keine Entsprechung. Realistisch von Hand. Ein späterer Rückwechsel ist teuer, weil der Originalwortlaut dann nur noch bei der Quelle steht. |

**Meine Empfehlung: Möglichkeit 2.** Begründung: Das Probenbuch ist der Maßstab, und es kennt
„Sippe" nicht – aber deine eigene Sammlung benutzt das Wort bis in Titel hinein, das ist ein
ernstzunehmender Hinweis auf euren Alltag. Möglichkeit 2 löst genau den Teil, den du kostenlos und
ohne Lizenzfrage lösen kannst (9 eigene Elemente), und lässt die 79 Fremdtexte in Ruhe, bis die
Frage „was sagt ihr im Heim wirklich?" beantwortet ist. Der Preis ist gering und der Weg zu
Möglichkeit 3 bleibt offen; der Weg von 3 zurück bliebe es nicht.

**Zusatz, egal wie du entscheidest:** „Sippe" sollte in der Suche ein Synonym von „Horte" und
„Gilde" bleiben, sonst findet jemand, der „Sippe" tippt, die Probenbuch-Elemente nicht mehr.

☐ Sippe bleibt · ☐ Horte/Gilde, nur eigene Texte · **☑ Horte/Gilde überall** · Entschieden am: **20.09.2026**

**Umgesetzt** in `data/sprache.json`, Regel „Horte und Gilde statt Sippe“: 31 Wortpaare, 224
Ersetzungen in 88 Elementen. Im Spieltext steht die Paarform „Horte/Gilde“ (Mehrzahl
„Horten/Gilden“, Zusammensetzungen „Horten-/Gildenwimpel“) – „Horte“ allein wäre für eine
Mädchengruppe falsch, und das Probenbuch schreibt die beiden selbst als Paar
(`pb-organisatorischer-aufbau`: „Horte / Gilde – mindestens 5“, „Horten/Gilden und Trupps“;
`pb-zeltbau`: „in der wir zur Horte/Gilde … zusammenwachsen“). Für „Sippling“ (36 Fundstellen)
hat das Probenbuch kein Wort; angezeigt wird „Pfadfinder“ – das Wort, das das Probenbuch
durchgängig für ein Mitglied des Bundes benutzt, und das in allen Fällen und Zahlen passt.
Ausnahme: `insp-digitales-tabu`, dort ist „Sippe“ ein zu erratendes Wort in einer Wortliste.
Der Zusatz gilt weiter: Die Suche findet beide Schreibweisen (siehe Abschnitt 4).

---

### (b) Heißt die Rolle im Spieltext „Spielleitung" oder „Gruppenführer"?

**Die Frage in einem Satz:** Wenn ein Spieltext sagt „die Spielleitung ruft ein Kommando" – soll da
„Gruppenführer" stehen, auch wenn diese Rolle manchmal ein Kind übernimmt?

**Was das Probenbuch sagt:** Weder noch. „Spielleit…" kommt in den 28 pb-Elementen null Mal vor,
„Gruppenführer" ebenfalls null Mal. Das Probenbuch sagt für die Führungsrolle „Führer" bzw.
„Führerin" (6 Elemente, 18 Fundstellen) und daneben „Führung" (22 Fundstellen). Für die Rolle im
Spiel gibt es also gar kein Probenbuch-Wort – das Probenbuch beschreibt keine Spiele.

**Was die Sammlung heute tut:** 203 Elemente, 328 Fundstellen (Zahl deckt sich mit `begriffe.csv`).
Quellen: Spielewiki 167, pfadfinder-spiele 28, Inspirator 6, eigene 2. Lizenzen: 169 CC BY-SA,
28 CC BY-NC-SA, 6 CC BY-NC. Die Formen im Text sind uneinheitlich: „Spielleiter" 227×,
„Spielleitung" 89×, „Spielleitern" 8×, „Spielleitertisch" 2×, „Spielleiterinnen" 1×,
„Spielleitende" 1×. In den Daten steht „Gruppenführer" heute genau 2× (beides Inspirator).
Daneben liegen 15 Elemente mit den Fremdwörtern „Gruppenleiter", „Teamer", „Betreuer",
„Leiter:in" (37 Fundstellen; Spielewiki 12, Inspirator 2, pfadfinder-spiele 1).
**Wichtig:** In mindestens 8 Spielewiki-Elementen übernimmt ausdrücklich ein Kind die Rolle
(z. B. `sw-bello-dein-knochen-ist-weg`: „Ein Spieler wird von den Spielleitern …";
`sw-au-ja`: „Ein Spieler (zu Beginn meist noch der Spielleiter) …"). Das ist ein
Bedeutungsunterschied, keine Wortwahl: dort wäre „Gruppenführer" schlicht falsch.

**Möglichkeiten:**

| | Möglichkeit | Folgen |
|---|---|---|
| 1 | **„Spielleitung" bleibt das Wort im Spieltext.** „Gruppenführer" nur in den eigenen Texten der App (Startseite, Planer, Hilfe). | 0 Elemente anzufassen. Die 15 Fremdwort-Elemente (Teamer/Betreuer/Gruppenleiter) werden separat auf „Spielleitung" gezogen – das sind 15 Elemente, 37 Fundstellen. Kein Lizenzhinweis nötig, solange die eigenen Texte gemeint sind. |
| 2 | **Überall „Gruppenführer".** | 203 + 15 = 218 Elemente. In mindestens 8 wird die Aussage sachlich falsch (dort leitet ein Kind). Änderungshinweis bei allen 203 nötig. Grammatik ändert sich mit („die Spielleitung ruft" → „der Gruppenführer ruft", plus Genderfrage aus (c)). |
| 3 | **Je nach Stelle.** „Gruppenführer" dort, wo eindeutig der Erwachsene/Ältere gemeint ist, sonst „Spielleitung". | Erfordert, dass jemand 328 Fundstellen einzeln liest. Kein Skript kann das. Ergebnis wäre am genauesten, kostet aber die meiste Zeit von allen Entscheidungen in diesem Dokument. |

**Meine Empfehlung: Möglichkeit 1.** Begründung: „Spielleitung" ist keine fremde Bundessprache,
sondern eine Funktionsbeschreibung – und sie ist in mindestens 8 belegten Fällen sachlich richtiger
als „Gruppenführer", weil dort ein Kind leitet. Das ist die größte Zahl im ganzen Dokument (203
Elemente) mit dem geringsten Gewinn. Umgekehrt sind „Teamer" und „Betreuer" echte
Fremdwörter aus der allgemeinen Jugendarbeit – die 15 Elemente lohnen sich und sind billig.

**☑ Spielleitung bleibt (+ Fremdwörter angleichen)** · ☐ überall Gruppenführer · ☐ je nach Stelle
· Entschieden am: **20.09.2026**

**Umgesetzt** in `data/sprache.json`, Regel „Spielleitung statt Betreuer und Gruppenleiter“:
37 Ersetzungen in 15 Elementen. Die 203 Elemente mit „Spielleitung/Spielleiter“ bleiben
unangetastet. „Teamer“ kommt in den Daten **0×** vor; betroffen sind „Betreuer“ (12 Elemente)
und „Gruppenleiter“ (4). Angezeigt wird „Spielleiter“ und nicht „Spielleitung“, weil in genau
diesen Sätzen männliche Fürwörter zurückverweisen („Der Betreuer wird wieder in den Raum
geholt. **Er** riecht …“, `sw-sesselriechen`) und weil die Mehrzahl erhalten bleiben muss
(„Die Betreuer **einigen** sich“, `sw-laufdiktat`). Mit „die Spielleitung“ müsste man die Sätze
umschreiben – das verbietet Entscheidung (d). „Spielleiter“ ist außerdem das Wort, das in den
203 nicht angefassten Elementen ohnehin steht. Beim Team passt die Spielleitung:
„das Betreuerteam“ wird „das Spielleitungsteam“.

**Nicht ersetzt wird das bloße „Leiter“** (19 Elemente). Es steht nicht in der Entscheidung,
und es ist zweideutig: in `insp-eigenes-brettspiel-bauen-entwickeln` steht „Schlangen und
Leitern“ – das Brettspiel. Wer es ersetzen will, muss die 19 Fundstellen einzeln lesen.

---

### (c) Welche Genderschreibweise gilt in der ganzen App?

**Die Frage in einem Satz:** Schreiben wir „Gruppenführer", „Gruppenführerinnen und
Gruppenführer" oder „Gruppenführer*innen" – und zwar überall gleich?

**Was das Probenbuch sagt:** Kein einziges Sonderzeichen (0× Sternchen, 0× Doppelpunkt, 0×
Unterstrich in 28 Elementen). Stattdessen Paarform und Schrägstrich: „Führer/Führerin",
„Horten/Gilden", „Jungen/Mädchen", „Jungwolf/Jungpfadfinderin", „Knappe/Gildenmädchen",
„Späher/Gildin". Zehn der 28 Proben nennen Jungen und Mädchen ausdrücklich beide.

**Was die Sammlung heute tut:** Drei Schreibweisen nebeneinander, insgesamt **97 Elemente**
(nicht 98 – ein Element enthält Sternchen und Doppelpunkt):

| Form | El. | Tr. | Quelle | Lizenz |
|---|---:|---:|---|---|
| Doppelpunkt `:in` | 77 | 263 | ausschließlich pfadfinder-spiele.de | CC BY-NC-SA 4.0 |
| Sternchen `*in` | 16 | 42 | Inspirator 14, pfadfinder-spiele 2 | CC BY-NC 4.0 / CC BY-NC-SA 4.0 |
| Unterstrich `_in` | 5 | 8 | ausschließlich Inspirator | CC BY-NC 4.0 |

Alle drei Zahlen decken sich mit `begriffe.csv`. Dazu kommen 82 Elemente, die die Paarform
ausschreiben („… und Spielerinnen"), verteilt über alle fünf Quellen (Spielewiki 55, Inspirator 10,
pfadfinder-spiele 8, Probenbuch 6, eigene 3). Deine eigene Doku ist uneinheitlich: `README.md`
schreibt „Gruppenführer*innen", `docs/heimabend-definition.md` und `CLAUDE.md` schreiben
„Gruppenführer" bzw. „Gruppenführer*innen" gemischt.

**Möglichkeiten:**

| | Möglichkeit | Folgen |
|---|---|---|
| 1 | **Paarform/Schrägstrich wie im Probenbuch.** Eigene Texte und Oberfläche: „Gruppenführer und Gruppenführerinnen" bzw. „Führer/Führerin". Fremde Texte bleiben. | 0 Elemente. Anzupassen sind `README.md`, `CLAUDE.md` und die Texte in `web/index.html`. Deckt sich mit dem Maßstab. Die 97 Elemente behalten drei Formen – sichtbar, aber als Zitat erklärbar. |
| 2 | **Eine Sonderzeichenform überall,** z. B. Doppelpunkt. | 97 Elemente, 313 Fundstellen. **Nicht mechanisch machbar:** aus „Spieler:in" wird nicht durch Zeichentausch „Spielerin oder Spieler"; Artikel, Plural und Fälle ändern sich mit („der:die Spielleiter:in"). Änderungshinweis bei allen 97 nötig. Betrifft nur zwei der fünf Quellen – die 622 Spielewiki-Texte hätten weiter ihre eigene Form. |
| 3 | **Generisches Maskulinum überall** („Gruppenführer", gemeint sind alle). | Wie 2, gleiche 97 Elemente und dieselbe Grammatikarbeit. Im DPB mit getrennten Jungen- und Mädchengruppen (Horte/Gilde) verliert man damit die Unterscheidung, die das Probenbuch bewusst macht. |

**Meine Empfehlung: Möglichkeit 1.** Begründung: Es ist die einzige Form, die im Probenbuch belegt
ist, sie kostet null Elemente, und sie macht die Doku sofort einheitlich – heute widersprechen sich
README und Definition. Alle Alternativen kosten 97 Elemente Handarbeit für ein rein sprachliches
Ergebnis, und keine davon würde die Sammlung wirklich vereinheitlichen, weil die größte Quelle
(Spielewiki, 622 Elemente) ohnehin ihre eigene Paarform benutzt.

**Zusatzentscheidung, die dazugehört:** In welcher Reihenfolge? Das Probenbuch schreibt teils
„Jungen/Mädchen", teils „Fünf Mädchen und eine Führerin oder fünf Jungen und ein Führer" – also
beides. Wenn du Möglichkeit 1 wählst, leg eine Reihenfolge fest, sonst wird die App wieder uneinheitlich.

**☑ Paarform/Schrägstrich** · ☐ Doppelpunkt überall · ☐ Sternchen überall · ☐ generisches Maskulinum
· Entschieden am: **20.09.2026**

**Umgesetzt** in `data/sprache.json`, zwei Regeln („Wortgruppen“ und „einzelne Wörter“):
408 Ersetzungen in 109 Elementen. In den Daten stehen 130 verschiedene Formen mit Doppelpunkt,
Sternchen oder Unterstrich – sie stehen **alle einzeln ausgeschrieben** in der Liste, keine
davon wird geraten. Die Regel dahinter:

- **Einzahl bekommt den Schrägstrich** wie „Führer/Führerin“ im Probenbuch:
  „Spieler:in“ → „Spieler/Spielerin“, „Jede:r“ → „Jeder/Jede“, „er:sie“ → „er/sie“.
- **Mehrzahl bekommt die ausgeschriebene Paarform:** „Spieler:innen“ → „Spieler und
  Spielerinnen“. Im Satz liest sich das ohne Umbau, der Schrägstrich in der Einzahl auch –
  „Ein Spieler oder eine Spielerin“ dagegen verlangt einen neuen Satzbau.
- **Steht ein Artikel davor, beugt er sich mit.** Deshalb stehen 90 Wortgruppen als ganzes Paar
  in der Liste: „eine:n Dirigent:in“ → „einen Dirigenten/eine Dirigentin“, „Der/die
  Spielleiter:in“ → „Der Spielleiter/die Spielleiterin“. Die längere Regel gewinnt gegen die
  kürzere, sonst käme „Der/die Spielleiter/Spielleiterin“ heraus.
- **Unregelmäßige Wörter stehen ausgeschrieben da:** „Biolog*in“ wird „Biologe/Biologin“ (nicht
  „Biolog/Biologin“), „Pirat*innen“ wird „Piraten und Piratinnen“, „Nachbar:innen“ wird
  „Nachbarn und Nachbarinnen“.
- **Im Wortinneren gibt es keine Paarform.** „Pfadfinder*innengeschichte“ wird
  „Pfadfindergeschichte“, „Pfadfinder*innen-Memory“ wird „Pfadfinder-Memory“.

**Reihenfolge (die Zusatzfrage):** erst die männliche, dann die weibliche Form – so wie das
Probenbuch „Führer/Führerin“, „Horten/Gilden“, „Knappe/Gildenmädchen“ schreibt.

**Es blieb keine Form übrig** – alle 130 ließen sich sauber in den Satz setzen.
Zwei Stellen sehen nach der Auflösung holprig aus, weil sie es schon vorher waren:
`insp-digitaler-sippencontest` („Der Hortenführer/die Gildenführerin / Roversprecher/
Roversprecherin“) und `insp-upcycling-reisespiele-basteln` („mit deiner Meute/Horte/Gilde“).
Umschreiben wäre nach (d) nicht erlaubt.

Zwei Zeichenketten sehen nur aus wie Genderformen und bleiben stehen: „filetype:ppt“ und
„filetype:pdf“ in `sw-powerpoint-karaoke` sind Suchbefehle. Weil die Liste ausgeschriebene
Formen enthält und keine allgemeine Regel, laufen sie von selbst nicht mit.

---

### (d) Neutrale Beschreibung oder Ansprache an den Gruppenführer?

**Die Frage in einem Satz:** Steht in der App „Ein Kind steht in der Mitte" oder „Stell ein Kind in
die Mitte" bzw. „Ihr braucht dafür einen Ball"?

**Was das Probenbuch sagt:** Es spricht an, aber nicht dich – es spricht **das Kind** an, das die
Probe ablegt: „Lasst euch diese Probe von euren Führern ausführlich erklären, bevor ihr sie
ablegt." (`pb-der-deutsche-pfadfinderbund`). 7 der 28 Proben enthalten diese Anrede,
22 der 28 enthalten überhaupt „ihr/euch/eure". Als Vorbild für den Ton der App taugt das Probenbuch
also nur bedingt: es redet mit einer anderen Person als die App.

**Was die Sammlung heute tut:** Zwei Tonfälle liegen nebeneinander.

| Messung | El. | Tr. | Verteilung |
|---|---:|---:|---|
| enge Anrede: „ihr müsst / sollt / könnt / dürft / braucht" | 95 | 113 | Inspirator 86, Probenbuch 7, Spielewiki 1, pfadfinder-spiele 1 |
| jede Anrede: „ihr", „euch", „eure…" | 280 | – | Inspirator 191, Spielewiki 52, Probenbuch 22, pfadfinder-spiele 13, eigene 2 |

Die enge Zahl (95 Elemente) deckt sich mit `begriffe.csv`; bei den Fundstellen zähle ich 113 statt
116, und die Quellenaufteilung weicht leicht ab (ich finde 86 Inspirator statt 88 und 7 Probenbuch
statt 5). Die zweite Zeile ist die wichtigere: **191 von 211 Inspirator-Elementen (90 %)** reden die
Gruppe an, aber nur **52 von 622 Spielewiki-Elementen (8 %)**. Der Tonfall folgt der Quelle,
nicht dem Zufall. Und der Inspirator spricht meist **die Gruppe** an („Ihr könnt selber eine
frische Butter herstellen"), nicht den Gruppenführer – wer auf „Ansprache an den Gruppenführer"
umstellt, muss dort also nicht nur den Modus, sondern auch den Adressaten ändern.

**Möglichkeiten:**

| | Möglichkeit | Folgen |
|---|---|---|
| 1 | **Neutrale Beschreibung als Hausform.** Gilt für die Oberfläche, die eigenen Elemente und alles, was neu dazukommt. Fremdtexte bleiben, wie sie sind. | 0 Elemente. Nur 2 eigene Elemente enthalten überhaupt eine Anrede. Zwei Tonfälle bleiben sichtbar, sind aber jeweils an die Quelle gebunden und dadurch erklärbar. |
| 2 | **Ansprache als Hausform,** Fremdtexte bleiben. | 0 Elemente, aber die 622 Spielewiki-Texte (die Mehrheit der Sammlung) stehen dann quer zur Hausform – die App wirkt insgesamt neutral, obwohl sie Ansprache verspricht. |
| 3 | **Einen Ton wirklich durchsetzen.** | Neutral überall: 280 Elemente umschreiben, davon 191 Inspirator. Ansprache überall: über 600 Spielewiki-Texte umschreiben. Beides ist keine Begriffsersetzung mehr, sondern Neuschreiben der Quelle – mit Änderungshinweis bei jedem Element, und beim Probenbuch mit der Rechtefrage aus (e). |

**Meine Empfehlung: Möglichkeit 1.** Begründung: Neutral ist der Ton der größten Quelle (622 von
1037 Elementen sind Spielewiki) und der Ton, in dem die Feldnamen und die Oberfläche ohnehin
geschrieben sind. Für die Ansprache müsstest du die Mehrheit der Sammlung neu schreiben; für
neutral immerhin 280 Elemente. Beides ist Arbeit ohne Gewinn für den Gruppenführer im Heim, der
eine Regel lesen will. Die Hausform kostet nichts und wirkt auf alles Neue.

**☑ Tonfall bleibt, wie die Quelle ihn schreibt** (= Möglichkeit 1, neutrale Beschreibung als
Hausform für Neues) · ☐ Ansprache · ☐ einen Ton wirklich durchsetzen
· Entschieden am: **20.09.2026**

**Umgesetzt:** 0 Elemente. Es wird nicht umformuliert. Diese Entscheidung ist die Leitplanke
für alle anderen: Eine Regel in `data/sprache.json` darf ein Wort tauschen und den Artikel
mitbeugen – sie darf keinen Satz umbauen. Daran ist die Wahl „Spielleiter“ statt
„Spielleitung“ in (b) gebunden, und daran, dass „Meute“ stehen bleibt.

---

### (e) Dürfen Texte fremder Quellen sprachlich umgeschrieben werden?

**Die Frage in einem Satz:** Darf in einem Spielewiki- oder Inspirator-Text ein Wort geändert
werden, oder bleiben Fremdtexte wörtlich stehen und nur eigene Elemente werden angepasst?

**Was das Probenbuch sagt:** Dazu sagt es nichts – aber es ist selbst der schwierigste Fall, siehe
unten.

**Was die Lizenzen sagen** (nachgesehen in `data/SCHEMA.md`, Abschnitt „Lizenz-Regeln", und
`docs/datenquellen.md`, Abschnitt „Lizenz-Konsequenzen"; die Lizenz steht je Element in
`quelle.lizenz`):

| Lizenz | Elemente | Bearbeitung erlaubt? | Auflagen |
|---|---:|---|---|
| CC BY-SA 4.0 | 683 (Spielewiki 622 + eigene 61) | ja | Namensnennung, **Hinweis, dass geändert wurde**, Bearbeitung wieder unter CC BY-SA |
| CC BY-NC 4.0 | 211 (Inspirator) | ja | Namensnennung, **Änderungshinweis**, nicht-kommerziell |
| CC BY-NC-SA 4.0 | 115 (pfadfinder-spiele.de) | ja | Namensnennung, **Änderungshinweis**, nicht-kommerziell, Bearbeitung wieder unter derselben Lizenz |
| „DPB-Probenbuch – Nutzung mit Erlaubnis des Rechteinhabers" | 28 | **keine CC-Lizenz** | Bearbeitung ist keine Lizenzfrage, sondern eine Frage an den Rechteinhaber |

Alle drei CC-Lizenzen erlauben also die Bearbeitung; alle drei verlangen einen Hinweis darauf
(CC 4.0, Abschnitt 3.a.1.B: es ist anzugeben, ob das Material verändert wurde). Was sie **nicht**
erlauben, ist das Mischen: CC BY-SA und CC BY-NC-SA bleiben unverträglich – ein geänderter Text
darf keine Formulierung aus einer anders lizenzierten Quelle übernehmen. Das steht schon in
`data/SCHEMA.md` und `CLAUDE.md` und ändert sich hier nicht. Der Sonderfall sind die 28
Probenbuch-Elemente: `docs/datenquellen.md` führt sie als „Rechte beim Projektinhaber". Sprachliche
Änderungen daran solltest du nicht über eine Lizenz begründen, sondern kurz mit dem Bund klären –
zumal das Probenbuch der Maßstab ist und deshalb am wenigsten Änderung braucht.

**Wie ein Änderungshinweis in der App aussehen müsste.** Die App zeigt Quelle und Lizenz heute an
zwei Stellen, beide in `web/index.html`: im Kasten „Quelle" der Detailansicht (ab Zeile 1722) und
im Plan-Text zum Teilen (ab Zeile 2124, Zeile „Quelle: … · Lizenz: … · URL"). An beiden Stellen
müsste der Hinweis mit:

- Detailansicht, Kasten „Quelle", eine Zeile unter der Lizenz:
  `Text geändert: Begriffe an die Sprache des DPB angepasst. Der Originaltext steht unter der oben verlinkten Quelle.`
- Plan-Text zum Teilen, in der bestehenden Quellenzeile:
  `Quelle: Spielewiki · CC BY-SA 4.0 · sprachlich geändert · <url>`
- Wenn ein Titel geändert wurde, zusätzlich: `Titel geändert, im Original: „<alter Titel>"`.
  Für den Titel gibt es das Verfahren schon: `scripts/build.py` setzt bei jedem Eintrag unter
  `umbenannt` das Feld `titel_geaendert: true` (in `wende_redaktion_an`) – nur zeigt die App es noch nicht an.

**Möglichkeiten:**

| | Möglichkeit | Folgen |
|---|---|---|
| 1 | **Fremdtexte bleiben wörtlich.** Nur die 61 eigenen Elemente werden angepasst. | Kein Änderungshinweis nötig, keine Lizenzfrage, kein Risiko. Die App bleibt sprachlich gemischt. Für die Entscheidungen (a)–(d) heißt das jeweils die kleinste Möglichkeit. |
| 2 | **Fremdtexte dürfen geändert werden, aber nur wo ein Wort sachlich falsch ist** (fremde Bundesstruktur, fremder Gruß, fremde Stufe), nicht aus Stilgründen. | Betrifft nach heutiger Zählung eine kleine, aufzählbare Menge: „Gut Pfad" (1), „Pfadi" (5), „Gruppenstunde" (19), fremde Stufen (Rover 6, Meute 10), „Teamer/Betreuer" (15). Änderungshinweis nötig, technisch je Element ein Merkmal. Die 28 Probenbuch-Elemente bleiben ausgenommen, bis die Rechtefrage geklärt ist. |
| 3 | **Fremdtexte dürfen frei umgeschrieben werden**, auch für Tonfall und Genderform. | Bis zu 97 (Gender) + 280 (Tonfall) + 88 (Sippe) + 203 (Spielleitung) Elemente. Jedes geänderte Element braucht den Hinweis. Der Wert der Quellenangabe sinkt: Wer nachschlägt, findet einen anderen Text vor. |

**Meine Empfehlung: Möglichkeit 2.** Begründung: Die Lizenzen erlauben mehr, als hier nötig ist.
Ein Änderungshinweis ist billig, wenn er wenige Dutzend Elemente betrifft, und unangenehm, wenn er
unter zwei Dritteln der Sammlung steht. Die Trennlinie „sachlich falsch, nicht bloß anders"
ist außerdem die einzige, die man später noch nachvollziehen kann. Für das Probenbuch: erst fragen,
dann ändern – dort sind ohnehin nur „Tracht"/„Uniform" strittig, und die stehen dort mit Absicht.

☐ Fremdtexte bleiben wörtlich · **☑ nur wo sachlich falsch (mit Hinweis)** · ☐ frei umschreibbar
· Entschieden am: **20.09.2026**

**Umgesetzt:** 710 Ersetzungen in 214 von 1075 Elementen. Das Probenbuch bleibt ganz außen vor.
Der Änderungshinweis steht in der App an zwei Stellen und **nur dort, wo wirklich etwas
ersetzt wurde** (`web/index.html`):

- **Detailansicht, Kasten „Quelle“**, eine Zeile unter der Lizenz – ohne das Wort „Lizenz“,
  weil der Gruppenführer im Heim damit nichts anfangen kann:
  > Wir haben in diesem Text einzelne Wörter ausgetauscht, damit sie zu unserem Bund passen:
  > „Sippe“ → „Horte/Gilde“, „Sippenwimpel“ → „Horten-/Gildenwimpel“. Sonst steht alles so da,
  > wie die Quelle es geschrieben hat.

  Darunter der Knopf **„Original anzeigen“**: er klappt den unveränderten Wortlaut aller
  betroffenen Felder auf. Damit ist die Auflage aus CC 4.0 3.a.1.B erfüllt, ohne dass irgendwo
  ein Lizenzvortrag stehen muss.
- **Plan-Text zum Teilen**, in der bestehenden Quellenzeile:
  `Quelle: Spielewiki · CC BY-SA 4.0 · sprachlich angepasst · <url>`

Titeländerungen aus `data/redaktion.json` (`titel_geaendert`) sind davon unberührt – das ist
Weg A und bleibt Sache von `scripts/build.py`.

---

## 3. Das Wörterbuch

Alle Begriffe aus `docs/pruefung-2026-09/begriffe.csv`, sortiert nach Zahl der betroffenen Elemente.

**Spaltenerklärung.** *Unser Wort* = was laut Probenbuch bzw. `heimabend-definition.md` bei euch
gilt; „–" heißt: dafür gibt es kein Probenbuch-Wort. *Fremdes Wort* = was heute in den Daten steht.
*El. (Tr.)* = meine eigene Zählung aus `data/elemente.json`; wo `begriffe.csv` abweicht, steht die
CSV-Zahl in der Spalte daneben. *Stand* = seit wann unser Wort gilt – solange nicht entschieden ist,
steht dort „offen". *Entsch.* = offen / getroffen.

| # | Unser Wort | Fremdes Wort | El. (Tr.) | laut CSV | Quellen | Stand | Vorschlag | Entsch. |
|---:|---|---|---:|---|---|---|---|---|
| 1 | Spielleitung | Spielleiter, Spielleitung | 203 (328) | gleich | sw 167, ps 28, insp 6, eig 2 | 20.09.2026 | **belassen** – nicht angefasst, siehe (b) | ☑ |
| 2 | – (Hausform) | „ihr müsst/sollt/könnt" | 95 (113) | 95 (116) | insp 86, pb 7, sw 1, ps 1 | 20.09.2026 | **belassen**, Hausform neutral, siehe (d) | ☑ |
| 3 | Horte/Gilde | Sippe, Sippling, Sippenführer | 88 (227) | gleich | insp 79, eig 9 | 20.09.2026 | **ersetzt**: 224 Ersetzungen in 88 El., 31 Wortpaare, 11 Titel | ☑ |
| 4 | Paarform | Doppelpunkt `:in` | 77 (263) | gleich | ps 77 | 20.09.2026 | **beim Anzeigen aufgelöst**, siehe (c) | ☑ |
| 5 | – | Corona, online, digital | 37 (73) | **73 (113)** | insp 22, ps 7, sw 7, pb 1 | offen | kein Sprach-, sondern Inhaltsthema → Frage 40 der Arbeitsliste | ☐ |
| 6 | Stamm / Hag | (belegt) | 31 (59) | 31 (53) | insp 18, eig 7, pb 5, sw 1 | belegt | belassen; nur 17 der 31 meinen die Einheit, der Rest ist Baumstamm/Stammbaum | ☐ |
| 7 | Wölfling | Wö, Altwolf | 25 (75) | gleich | insp 15, pb 8, sw 2 | belegt | belassen | ☐ |
| 8 | Halstuch | Tuch | 27 (62) | **24 (45)** | sw 10, insp 9, pb 5, eig 2, ps 1 | belegt | belassen; im Feld `material` „Tuch" zulassen | ☐ |
| 9 | Heimabend | Gruppenstunde | 19 (33) | gleich | insp 12, sw 4, ps 2, eig 1 | 20.09.2026 | **ersetzt**: 32 Ersetzungen in 18 El., 1 Ausnahme (`insp-digitales-tabu`) | ☑ |
| 10 | Kohte / Jurte | (belegt) | 19 (112) | gleich | insp 11, pb 5, eig 2, sw 1 | belegt | belassen | ☐ |
| 11 | Kluft | Tracht, Uniform | 16 (49) | 16 (48) | pb 9, insp 7 | belegt | **nicht** mechanisch ersetzen, siehe Bedeutungsliste | ☐ |
| 12 | Paarform | Sternchen `*in` | 16 (42) | gleich | insp 14, ps 2 | 20.09.2026 | **beim Anzeigen aufgelöst**, siehe (c) | ☑ |
| 13 | – | Kindergeburtstag, Party, Fasching | 13 (31) | **16 (45)** | sw 12, ps 1 | offen | Inhaltsthema → Frage 27/48 | ☐ |
| 14 | Spielleitung | Gruppenleiter, Betreuer | 15 (37) | gleich | sw 12, insp 2, ps 1 | 20.09.2026 | **ersetzt**: 37 Ersetzungen in 15 El.; „Teamer" kommt 0× vor; bloßes „Leiter" bleibt | ☑ |
| 15 | Heimabend, Gruppe | Schule, Klasse, Unterricht | 11 (13) | **15 (23)** | sw 6, pb 3, eig 1, insp 1 | offen | einzeln ansehen, sehr kleine Menge | ☐ |
| 16 | Versprechen, Aufnahme | Gelöbnis | 18 (45) | **14 (37)** | insp 10, pb 8 | belegt | belassen; „Gelöbnis" nur 1× (`pb-pfadfindergruss-und-pfadfinderversprechen`) | ☐ |
| 17 | – | Lagerfeuer, Singerunde, Singewettstreit | 13 (20) | gleich | insp 4, pb 3, eig 3, sw 2, ps 1 | offen | dein Wort fehlt noch – bitte eintragen: ____________ | ☐ |
| 18 | – (es gibt keins) | Meute | 10 (11) | gleich | insp 9, eig 1 | 20.09.2026 | **bleibt stehen** – andere Altersstufe, siehe unten | ☑ |
| 19 | Horte/Gilde | – | 9 (26) | 9 (24) | pb 8, sw 1 | 20.09.2026 | Zielwort für (a), jetzt in 88 weiteren El. | ☑ |
| 20 | DPB | DPSG, VCP, BdP, DPBM | 7 (20) | **8 (26)** | pb 3, insp 2, sw 1, ps 1 | offen | stehen lassen, wo Geschichte erzählt wird | ☐ |
| 21 | – | Alkohol, Trinkspiel | 4 (10) | **8 (38)** | insp 3, pb 1 | offen | Inhaltsthema → Frage 26; meine engere Zählung ohne „Schnapsen" | ☐ |
| 22 | Knappe / Späher, Gildenmädchen / Gildin | Rover, Ranger, Caravelle | 6 (11) | gleich | insp 4, ps 1, pb 1 | belegt | **Bedeutungsunterschied**, siehe unten; „Ranger"/„Caravelle" kommen 0× vor | ☐ |
| 23 | Trupp | Truppstunde | 6 (14) | gleich | insp 2, sw 2, pb 2 | belegt | „Trupp" belassen; „Truppstunde" kommt 0× vor | ☐ |
| 24 | Pfadfinder | Pfadi, Pfadis | 5 (9) | gleich | insp 3, ps 1, sw 1 | 20.09.2026 | **ersetzt**: 8 Ersetzungen in 3 El., 2 Ausnahmen (`sw-hugo`, `ps-grenze`) | ☑ |
| 25 | Jungenschaft / Mädelschaft | Jungschar | 5 (24) | 5 (26) | pb 5 | belegt | nichts zu tun, „Jungschar" kommt 0× vor | ☐ |
| 26 | Paarform | Unterstrich `_in` | 5 (8) | gleich | insp 5 | 20.09.2026 | **beim Anzeigen aufgelöst**, siehe (c) | ☑ |
| 27 | Horte | Horde | 4 (5) | gleich | insp 2, pb 1, eig 1 | belegt | nichts zu tun: alle 5 Fundstellen sind „Hordentopf" (Kochgeschirr) | ☐ |
| 28 | Wildling, Neuling, Wölfling … | Wichtel, Biber | 2 (9) | **3 (10)** | sw 2 | belegt | nichts zu tun: beide Treffer sind „Wichteln" (Geschenkspiel), „Biber" kommt 0× vor | ☐ |
| 29 | Kornett | – | 1 (3) | gleich | pb 1 | belegt | belassen, in der App einmal erklären | ☐ |
| 30 | Allzeit bereit | Gut Pfad | 1 (3) | gleich | insp 1, eig 1 | 20.09.2026 | **ersetzt**: 1 Ersetzung (`eig-schlussgruss`); die 2 Treffer in `insp-digitales-tabu` sind Ratewörter | ☑ |

Abkürzungen der Quellen: `sw` Spielewiki · `insp` Heimabend-Inspirator (DPBM) ·
`ps` pfadfinder-spiele.de · `eig` eigene Sammlung · `pb` DPB-Probenbuch.

### Wo meine Zahl von `begriffe.csv` abweicht

Sieben Zeilen weichen ab. In allen sieben Fällen liegt es an der Suchregel, nicht an den Daten:

| Begriff | ich | CSV | Erklärung |
|---|---:|---:|---|
| Corona / online / digital | 37 | 73 | Ich habe nur nach „corona", „online", „digital" gesucht. Die CSV zählt offenbar weitere Wörter mit (virtuell, Video, Zoom o. ä.) – mit diesen Zusätzen komme ich auf 83. Die Differenz steckt fast vollständig im Spielewiki (7 statt 46). |
| Halstuch | 27 | 24 | Ich zähle jedes Vorkommen inklusive `material`-Listen; die CSV zählt drei Elemente weniger. |
| Kindergeburtstag / Party / Fasching | 13 | 16 | Ich habe „Party" nur als eigenes Wort gesucht; mit „Geburtstag" allgemein komme ich auf 21. |
| Schule / Klasse / Unterricht | 11 | 15 | Ich habe auf ganze Wörter eingeschränkt, sonst treffen „Schulhof", „Vorschule" und das Adjektiv „klasse!" mit (dann 56). |
| Versprechen / Gelöbnis / Aufnahme | 18 | 14 | Ich zähle „Aufnahme" auch dort mit, wo Fotoaufnahmen gemeint sind – das sind vermutlich die 4 Elemente Unterschied. |
| Alkohol / Trinkspiel | 4 | 8 | Die CSV zählt die Kartenspiele „Schnapsen", „Bauernschnapsen", „Dreierschnapsen" mit. Das ist ein Falschtreffer: mit Alkohol haben sie nichts zu tun. Mit ihnen komme ich auf 9 Elemente / 72 Fundstellen. |
| Fremde Stufen (Wichtel, Biber) | 2 | 3 | Und beide Treffer sind falsch, siehe unten. |

**Praktische Folge:** Bei den fünf Grundsatzentscheidungen (Sippe 88, Spielleitung 203, Gender
77/16/5, Anrede 95, Lizenzen) stimmen meine Zahlen mit der CSV überein. Die Abweichungen liegen
alle bei Inhaltsfragen, die in Block 4 der Arbeitsliste gehören, nicht in dieses Dokument.

### Begriffe mit echtem Bedeutungsunterschied

Diese Begriffe sind **keine** bloße Wortwahl. Wer sie mechanisch ersetzt, macht Aussagen falsch.
Für ein späteres Skript gilt: Hände weg, ohne dass ein Mensch die Fundstelle gelesen hat.

- **Horte ≠ Gilde.** Horte = Jungengruppe, Gilde = Mädchengruppe, beide ab 5 Mitgliedern
  (`pb-organisatorischer-aufbau`). „Sippe" → „Horte" wäre für eine Mädchengruppe falsch. Richtig
  wäre je nach Gruppe „Horte" oder „Gilde", oder die Paarform „Horte/Gilde".
- **Meute ≠ Sippe.** „Meute" ist bei DPSG und DPBM die **Wölflingsgruppe** (7–11 Jahre), „Sippe"
  die Gruppe der älteren Kinder. In den Daten steht das ausdrücklich so: `insp-marionette`
  „Der Meutenführer gibt Kommandos und alle blinden Wölflinge …", `insp-finde-die-entfuehrte-person`
  „ein/eine Meutenhelfer\*in … Die Wölflinge sollen …". Zwei Elemente stellen beide Wörter
  nebeneinander („mit deiner Meute/Sippe"). Eine Ersetzung „Meute" → „Sippe" würde also die
  Altersangabe verfälschen. Das Probenbuch hat für die Wölflingsgruppe kein eigenes Wort.
  **Entschieden am 20.09.2026: „Meute" bleibt stehen** und steht in keiner Regel von
  `data/sprache.json`. Begründung: Entscheidung (e) erlaubt nur zu ersetzen, was für den DPB
  sachlich falsch ist – „Meute" ist aber nicht das falsche Wort für dieselbe Sache, sondern das
  richtige Wort für eine **andere** Sache (die Gruppe der 7- bis 11-Jährigen). Aus „Meute" eine
  „Horte/Gilde" zu machen hieße, in `insp-marionette` und `insp-finde-die-entfuehrte-person` eine
  Altersangabe zu verfälschen; und für die Wölflingsgruppe hätten wir kein Wort anzubieten. Die
  Folge ist an zwei Stellen sichtbar: aus „mit deiner Meute/Sippe" wird „mit deiner
  Meute/Horte/Gilde". Das ist holprig, aber richtig – und es verschwindet in dem Moment, in dem
  euer Wort für die Wölflingsgruppe feststeht.
- **Trupp ≠ Truppstunde.** „Trupp" ist im DPB eine Einheit ab 10 Mitgliedern (belegt in
  `pb-organisatorischer-aufbau`), „Truppstunde" wäre DPSG-Sprache für den Heimabend. Praktisch ist
  die Frage erledigt: „Truppstunde" kommt in den Daten **0×** vor.
- **Rover ≠ Ältere allgemein.** „Rover" ist die Stufe fremder Bünde; im DPB heißen die Älteren
  Knappe/Späher (Jungen) bzw. Gildenmädchen/Gildin (Mädchen) – belegt in `pb-staendeaufbau-des-dpb`.
  In `insp-nur-fuer-rover-feuerfestigkeit-testen` steht es im Titel und meint eine Altersangabe;
  in `ps-grenze` steht „Rover+Leiter mit Pfadis+Juffis" und meint einen Altersunterschied, nicht
  eine Gruppe. Beide brauchen einen Menschen.
- **Stamm ≠ Baumstamm.** 31 Elemente enthalten „Stamm…", aber nur **17** meinen die Einheit; der
  Rest sind Baumstamm, Stammbaum, „stammt aus", Stammdurchmesser. Eine Regel „Stamm" darf nie
  ohne Wortliste laufen.
- **Horde ≠ Horte.** Alle 5 Fundstellen von „Horde" sind „Hordentopf"/„Hordentöpfe" – das
  Kochgeschirr, und das ist richtig geschrieben. Es gibt **keine** Stelle, an der „Horde" als
  Gruppe steht. Frage 27 des Prüfdokuments ist damit beantwortet: nichts zu tun.
- **Wichteln ≠ Wichtel.** Die beiden Treffer (`sw-schrottwichteln`, `sw-engerl-und-bengerl`) sind
  das Geschenkspiel, nicht die VCP-Stufe „Wichtel". „Biber" kommt 0× vor. Eine Ersetzung würde
  aus „Schrottwichteln" Unsinn machen.
- **Uniform ≠ Kluft.** Im Probenbuch steht der Satz „Die Kluft ist keine Uniform und will uns auch
  nicht uniformieren" (`pb-unsere-kluft`) und die historische Angabe „nach Ablösung der Uniform
  durch die Kluft" (`pb-die-lilie`). „Tracht" steht in `pb-geschichte-der-pfadfinder` und
  `pb-geschichte-der-buendischen-jugend` als historischer Begriff (Wandervogel-Trachten). Alle
  fünf Stellen wären nach einer Ersetzung falsch.
- **Spielleitung ≠ Gruppenführer.** In mindestens 8 Spielewiki-Elementen übernimmt ein Kind die
  Rolle (`sw-anna`, `sw-au-ja`, `sw-bello-dein-knochen-ist-weg`, `sw-boogaloo`, `sw-hangman`,
  `sw-taler-taler-du-musst-wandern`, `sw-umzug-neubau-erdbeben`, `sw-wildschwein`).
- **Pfadi als Eigenname.** In `sw-hugo` stehen „Pfadi Heidegg" und „Pfadi Reiden" – Namen von
  Schweizer Gruppen. Die dürfen nicht ersetzt werden.

---

## 4. Wie die Ersetzung läuft

Das war Frage 55 der Arbeitsliste. Es gibt zwei Wege, und sie schließen sich nicht aus.
**Am 20.09.2026 entschieden: Weg B als Regelfall.**

### Weg A – Änderung im Element speichern

Die Änderung wird in `data/redaktion.json` unter `korrekturen` eingetragen; `scripts/build.py`
wendet sie beim nächsten Lauf an und schreibt das Ergebnis nach `data/elemente.json`.

So funktioniert das heute (nachgesehen in `scripts/build.py`, Funktion `wende_redaktion_an`): ein Eintrag unter
`korrekturen` kann `titel` setzen (dann wird zusätzlich `titel_geaendert: true` gesetzt), Felder
über `felder` **vollständig überschreiben** und über `hinweis` einen Satz vorn an `tipps` hängen.
Von den 26 heutigen Einträgen benutzen die meisten nur `hinweis`.

- **Vorteil:** eine einzige Wahrheit. Alles, was `elemente.json` liest – die Web-App, der Plan-Text
  zum Teilen, die Suche, später die Flutter-App – sieht denselben Text, ohne eigene Regeln.
- **Vorteil:** die Entscheidung ist dokumentiert, mit `grund` je Eintrag, wie es der Vertrag verlangt.
- **Nachteil:** es gibt heute **keine** Wort-für-Wort-Ersetzung. `felder` überschreibt ein ganzes
  Feld. Ein einziges geändertes Wort in einer 3000 Zeichen langen Beschreibung heißt: die komplette
  Beschreibung noch einmal in `redaktion.json`. Bei 88 Sippen-Elementen wäre die Redaktionsdatei
  vielfach größer als heute (17 KB) und würde die Quelltexte doppelt führen.
- **Nachteil:** der Änderungshinweis wird Pflicht (siehe (e)), und der Originalwortlaut steht dann
  nur noch bei der Quelle. Eine Entscheidung zurückzunehmen heißt, die Texte neu zu holen.

### Weg B – erst beim Anzeigen ersetzen

Die Quelldaten bleiben unangetastet; eine Regelliste wird beim Laden der App angewendet.

- **Vorteil:** umkehrbar. Eine Zeile in der Regeldatei ändern, und die App sagt wieder „Sippe".
  Genau das braucht Entscheidung (a), die sich erfahrungsgemäß noch einmal dreht.
- **Vorteil:** `elemente.json` bleibt exakt das, was in der Quelle steht – die Quellenangabe stimmt
  weiter, und ein Vergleich mit der Quelle bleibt möglich.
- **Vorteil in dieser App konkret:** `web/index.html` baut den Suchtext einmalig beim Start auf
  (Funktion `starte()`, Zeilen 2545–2557). Wenn die Ersetzung direkt davor über die geladenen
  Elemente läuft, sind Kacheln, Detailansicht, Suche und Plan-Text automatisch mit erfasst – **eine**
  Stelle, nicht fünf.
- **Nachteil:** jede spätere Ausgabe muss durch die Ersetzung laufen. In dieser App sind das die
  Kachelvorschau (Zeile 1636), die Detailansicht (1671), der Quellenkasten (1722) und vor allem der
  **Plan-Text zum Teilen** (2110–2135) – wer den in einen Messenger kopiert, verschickt Text, den
  die Datei nie enthalten hat.
- **Nachteil:** die Regeln existieren dann in der Web-App. Die geplante Flutter-App müsste sie
  noch einmal umsetzen – oder die Regeldatei mitlesen.
- **Nachteil:** ein Änderungshinweis ist trotzdem nötig. Der Nutzer sieht einen geänderten Text;
  dass die Datei im Hintergrund unverändert ist, ändert daran nichts.

### Entscheidung vom 20.09.2026

**Weg B als Regelfall, Weg A für die Ausnahmen.**

- Weg B für alles, was reine Wortwahl ist (Sippe/Horte, Gruppenstunde/Heimabend, Pfadi/Pfadfinder,
  Teamer/Spielleitung). Umkehrbar, eine Datei, kein Datenverlust.
- Weg A für alles, was **kein** Wortersatz ist: Titeländerungen (dafür gibt es `umbenannt` schon),
  sachliche Korrekturen und Sicherheitshinweise (dafür gibt es `korrekturen`/`hinweis` schon) und
  Elemente, die ganz raus sollen (`gesperrt`). Da ist die dauerhafte Speicherung richtig, weil die
  Entscheidung inhaltlich ist und nicht sprachlich.
- Der Änderungshinweis gehört in beiden Fällen in die Anzeige, mit dem Wortlaut aus Abschnitt (e).

### Das Datenformat – so sieht `data/sprache.json` aus (seit 20.09.2026)

Die Datei liegt neben `redaktion.json`. Die Skizze aus der Fassung vom 09.09. hat getragen, mit
**einer** Abweichung: `von` und `zu` sind keine zwei gleich langen Listen mehr, sondern eine Liste
von Paaren. Bei 281 Wortpaaren wären zwei parallele Listen nicht zu pflegen – eine Zeile
eingeschoben, und ab da steht neben jedem Wort das falsche Gegenstück, ohne dass es jemand merkt.
Ein Paar `{"von": …, "zu": …}` kann nicht verrutschen. Sonst ist alles wie skizziert.

```jsonc
{
  "meta": {
    "name": "Sprachregeln für die Anzeige („die Brille“)",
    "stand": "2026-09-20",
    "felder": ["titel", "kurz", "beschreibung", "tipps", "tags", "themen", "material", "varianten"],
    "ausser_praefixe": ["pb-", "mein-"]      // Probenbuch und selbst erfasste Ideen
  },
  "regeln": [
    {
      "name": "Heimabend statt Gruppenstunde",
      "woerter": [
        { "von": "Gruppenstunde",     "zu": "Heimabend" },
        { "von": "Gruppenstunden",    "zu": "Heimabende" },
        { "von": "zur Gruppenstunde", "zu": "zum Heimabend" }
      ],
      "ausser": ["insp-digitales-tabu"],
      "ausser_grund": "Tabu-Wortliste: das Wort ist dort der Spielgegenstand.",
      "hinweis_noetig": true,
      "grund": "„Heimabend“ steht in allen 28 Proben des Probenbuchs …",
      "seit": "2026-09-20"
    }
  ]
}
```

Sechs Dinge sind an dieser Form wichtig:

1. **Beugungsformen werden aufgezählt, nicht geraten.** Ein Skript, das aus „Gruppenstunde“ selbst
   „Gruppenstunden“ ableiten will, produziert irgendwann „Heimabendn“.
2. **Ändert sich mit dem Wort der Artikel, steht die ganze Wortgruppe als Paar da.**
   „die Gruppenstunde“ ist weiblich, „der Heimabend“ männlich – deshalb
   `"zur Gruppenstunde" → "zum Heimabend"`. Genauso bei den Genderformen:
   `"eine:n Dirigent:in" → "einen Dirigenten/eine Dirigentin"`.
3. **`ausser` ist eine Liste von Element-ids,** jede mit einem `ausser_grund` daneben. Ohne sie
   gibt es keine sicheren Regeln – „Sippe“ und „Gut Pfad“ sind in `insp-digitales-tabu` die zu
   erratenden Wörter eines Ratespiels, „Pfadi Heidegg“ in `sw-hugo` ist ein Gruppenname.
4. **`meta.ausser_praefixe` hält ganze Quellen heraus.** Das Probenbuch (`pb-`) ist von keiner
   Regel betroffen, ohne dass man es in jede einzeln schreiben muss. Selbst erfasste Ideen
   (`mein-`) auch nicht: Wer seine eigene Idee aufschreibt, soll sie so wiederfinden, wie er sie
   getippt hat.
5. **`meta.felder` sagt, wo die Brille hinschaut.** Alles, was die App als Text ausgibt: Titel,
   Kurztext, Beschreibung, Tipps, Stichworte, Themen, Material und die Variantenliste. Ob ein Feld
   ein Text oder eine Liste ist, sieht die App am Wert – die Wortliste muss nichts über den Aufbau
   der Elemente wissen.
6. **`hinweis_noetig` steuert den Änderungshinweis,** es ist kein Kommentar. Steht es auf `true`,
   nennt die App bei jedem betroffenen Element, dass Wörter getauscht wurden. Eine spätere Regel,
   die nur einen Tippfehler geradezieht, käme mit `false` aus. Heute steht es bei allen sieben
   Regeln auf `true`.

**Nur ganze Wörter.** Links und rechts vom Treffer darf kein Buchstabe stehen, sonst würde aus
„Hordentopf“ ein „Horten-/Gildentopf“. Das längere Paar gewinnt gegen das kürzere, sonst käme aus
„zur Gruppenstunde“ ein „zur Heimabend“ heraus.

> **Ein Fallstrick, der beim Bauen aufgefallen ist.** Der naheliegende Weg – alle Wörter in ein
> großes Suchmuster packen und einmal ersetzen lassen – geht schief. In „Kindergeburtstage o**der
> Gruppenstunde**n“ greift die Regel `der Gruppenstunde` mitten im Wort „oder“, wird wegen der
> Wortgrenze verworfen – und die Suche läuft hinter der verworfenen Stelle weiter, also **an
> „Gruppenstunden“ vorbei**. Der Satz bliebe unverändert, ohne Fehlermeldung. Die App läuft
> deshalb Zeichen für Zeichen durch den Text und probiert an jeder Stelle die längste passende
> Regel (`durchDieBrille()` in `web/index.html`). Der Rauchtest prüft genau diesen Fall.

### Wie man die Wortliste pflegt

Die Liste ist für Menschen gemacht, nicht für ein Skript. Sie enthält keine regulären Ausdrücke,
nur ausgeschriebene Wörter – wer Deutsch kann, kann sie lesen und ändern.

**Ein Wort dazunehmen, in fünf Schritten:**

1. **Erst zählen, dann entscheiden.** Wie oft kommt das Wort vor, und in welchen Elementen? Im
   Zweifel mindestens fünf Fundstellen im Zusammenhang ansehen. Zusammengesetzte Wörter und
   Wörter mit zweiter Bedeutung sind die Falle: „Horde“ ist hier immer der Hordentopf, „Stamm“ in
   der Hälfte der Fälle ein Baumstamm, „Wichteln“ ein Geschenkspiel, „Leiter“ manchmal die
   Leiter. Die Liste in Abschnitt „Begriffe mit echtem Bedeutungsunterschied“ ist die Warnliste.
2. **Alle Beugungsformen aufschreiben,** Einzahl und Mehrzahl, und jede Zusammensetzung, die
   wirklich vorkommt – nicht die, die vorkommen könnte. `Sippenwimpel` steht in der Liste,
   `Sippenbeutel` nicht, weil es das Wort in den Daten nicht gibt.
3. **Jede Form im Satz prüfen,** nicht nur im Nominativ. Ändert sich der Artikel mit, kommt die
   Wortgruppe in die Liste. Verweist ein Fürwort im nächsten Satz auf das Wort zurück („… **Er**
   riecht an den Stühlen“), muss das Geschlecht erhalten bleiben – sonst wird der Satz falsch,
   und umschreiben ist nach Entscheidung (d) nicht erlaubt.
4. **Ausnahmen eintragen,** mit `ausser` und `ausser_grund`. Wortlisten von Ratespielen,
   Eigennamen und Zitate sind die häufigsten.
5. **`grund` und `seit` ausfüllen.** Jeder Eintrag sagt, warum er da ist – so verlangt es der
   Vertrag, und in einem halben Jahr weiß es sonst niemand mehr.

**Danach, immer in dieser Reihenfolge:**

- `web/sprache.js` mitziehen. Die Datei enthält dieselbe Liste als `window.SPRACHE = …;` und ist
  nur dafür da, dass die App **auch per Doppelklick** läuft – genau wie `web/elemente.js` neben
  `data/elemente.json`. Wer die eine ändert und die andere vergisst, sieht auf GitHub Pages etwas
  anderes als auf dem eigenen Rechner.
- `scripts/rauchtest.js` im Browser laufen lassen. Er prüft unter anderem, dass „Sippe“ in der
  Anzeige nicht mehr vorkommt, dass die Suche beide Schreibweisen findet, dass die
  Probenbuch-Elemente unverändert sind und dass der Änderungshinweis nur dort steht, wo wirklich
  ersetzt wurde.
- Die Zahlen in diesem Dokument nachziehen.

**Eine Regel wieder loswerden** heißt: die Zeile löschen. `data/elemente.json` ist nie angefasst
worden, also steht sofort wieder der Originalwortlaut da. Wer die ganze Brille abnehmen will,
benennt `data/sprache.json` und `web/sprache.js` um – die App läuft dann ohne sie weiter und zeigt
überall die Quelle im Original. Das ist der Grund, warum Weg B gewählt wurde.

---

## 5. Was ein Skript ohne Rückfrage ersetzen darf – und was nicht

### 5.1 Unstrittig: nichts zu tun

Fünf Begriffe aus dem Prüfdokument kommen in `data/elemente.json` **kein einziges Mal** vor. Die
zugehörigen Fragen sind damit beantwortet, ohne dass du etwas entscheiden musst:

| Begriff | Fundstellen | Frage in der Arbeitsliste |
|---|---:|---|
| Truppstunde | 0 | 44, 23 |
| Stufenstunde | 0 | 44 |
| Jungschar | 0 | 25 |
| Ranger, Caravelle | 0 | 22 |
| „Horde" als Gruppe | 0 (nur „Hordentopf", 4 Elemente) | 27 |
| „Wichtel" als Stufe, „Biber" | 0 (nur „Wichteln" = Geschenkspiel, 2 Elemente) | 28 |

### 5.2 Unstrittig: darf ein Skript ersetzen

Drei Regeln sind sicher – **jede mit einer Ausnahmeliste.** Zusammen betreffen sie 23 Elemente.
**Seit dem 20.09.2026 sind alle drei in `data/sprache.json` umgesetzt.** Eine Korrektur an der
Tabelle: „Gut Pfad" kommt 3× vor, nicht 2× – zweimal in der Tabu-Wortliste von
`insp-digitales-tabu` (Ausnahme) und einmal als echter Gruß in `eig-schlussgruss`. Ersetzt wird
also genau eine Stelle.

| Regel | El. | Tr. | Ausnahmen, die drin bleiben müssen | Warum unstrittig |
|---|---:|---:|---|---|
| Gruppenstunde → Heimabend | 19 | 33 | `insp-digitales-tabu` (Wortliste eines Ratespiels – das Wort ist dort der Spielgegenstand) | „Heimabend" steht in allen 28 Probenbuch-Elementen und in `heimabend-definition.md`; es ist dieselbe Sache unter anderem Namen |
| Pfadi / Pfadis → Pfadfinder | 5 | 9 | `sw-hugo` („Pfadi Heidegg", „Pfadi Reiden" sind Namen Schweizer Gruppen); `ps-grenze` („Pfadis+Juffis" meint Altersstufen fremder Bünde) | Umgangssprache, im Probenbuch nicht belegt; in den 3 übrigen Elementen ist schlicht „Pfadfinder" gemeint |
| Gut Pfad → Allzeit bereit | 1 | 2 | keine | Euer Gruß laut `heimabend-definition.md` und `pb-pfadfindergruss-und-pfadfinderversprechen`; „Gut Pfad" ist der Gruß anderer Bünde |

Der Wunsch, vor dem ersten Lauf alle Fundstellen mit Umgebung zu sehen, hat sich mit Weg B
erledigt: Es wird nichts geschrieben. Wer eine neue Regel prüfen will, trägt sie ein, lädt die
App neu und liest nach – und nimmt sie wieder heraus, wenn sie Unsinn macht. Für neue Importe
bleibt der Rauchtest die Kontrolle: Er sagt, wenn „Sippe" plötzlich wieder in der Anzeige steht.

### 5.3 Braucht eine Entscheidung von dir

Die fünf Grundsatzfragen aus Abschnitt 2 sind **seit dem 20.09.2026 beantwortet** und stehen
nicht mehr hier. Was offen blieb:

Aus dem Wörterbuch, sortiert nach Aufwand:

- **Meute** (10) – ~~offen~~ **entschieden 20.09.2026: bleibt stehen.** Es fehlt weiter euer Wort
  für die Wölflingsgruppe; solange es keins gibt, wäre jede Ersetzung eine Altersverfälschung.
- **Rover** (6) – „Ältere", „Knappen/Späher" oder Stelle streichen? Bedeutungsunterschied.
- **Stamm** (31, davon 17 relevant) – die 17 Fundstellen einmal ansehen; die übrigen 14 sind
  Baumstämme.
- **Lagerfeuer/Singerunde** (13) – hier fehlt schlicht euer Wort; ohne das geht keine Regel.
- **Halstuch** (27) – im Fließtext richtig, im Feld `material` wäre „Tuch" praktischer.
- ~~**Teamer/Betreuer/Gruppenleiter** (15)~~ – **erledigt 20.09.2026**, siehe (b). Offen bleibt
  das bloße „Leiter" (19 Elemente), das zweideutig ist („Schlangen und Leitern").
- **Kluft/Tracht/Uniform** (16) – **nicht** mechanisch; die 5 relevanten Stellen sind Sätze über
  den Unterschied.
- **Kornett** (1) – keine Ersetzung, sondern eine Erklärung in der App.
- **Fremde Bünde** (7) – stehen lassen, wo sie Geschichte erzählen; „Orden St. Georg" ist DPB-eigen.

**Nicht in dieses Dokument, sondern in Block 4 der Arbeitsliste** (das sind Inhaltsfragen, keine
Sprachfragen): Corona/online/digital (37), Kindergeburtstag/Party (13), Alkohol/Trinkspiel (4),
Schule/Klasse (11).

---

## 6. Was seit dem 20.09.2026 gilt

Erledigt:

1. Die Kreuze in Abschnitt 2 sind gesetzt, die Spalte „Entsch." des Wörterbuchs steht bei den
   betroffenen Zeilen auf ☑, mit Datum in der Spalte „Stand".
2. Die Entscheidungen stehen mit Begründung in `data/sprache.json` – jede Regelgruppe trägt
   `grund` und `seit`, so verlangt es der Vertrag.
3. Die App legt die Liste beim Laden über die Texte; `scripts/rauchtest.js` prüft das Ergebnis.
   `data/elemente.json` ist unverändert geblieben, `scripts/build.py` musste nicht laufen.

Was dabei **nicht** entschieden wurde und weiter offen ist:

- **„Meute"** (10 Elemente) bleibt stehen – aber euer Wort für die Wölflingsgruppe fehlt weiter.
  Sobald es eins gibt, ist das eine Regel von drei Zeilen.
- **„Rover"** (6), **„Stamm"** (17 relevante von 31), **„Lagerfeuer/Singerunde"** (13),
  **„Halstuch/Tuch" im Feld `material`** (27), **„Kluft/Tracht/Uniform"** (16) und
  **„Kornett"** (1) stehen unverändert in Abschnitt 5.3. Keines davon ist eine reine Wortwahl.
- **Das bloße „Leiter"** (19 Elemente) – siehe (b).
- Die Inhaltsfragen (Corona, Kindergeburtstag, Alkohol, Schule) gehören weiter in Block 4 der
  Arbeitsliste, nicht hierher.
