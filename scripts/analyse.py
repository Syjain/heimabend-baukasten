#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heimabend-Baukasten – Prüf-Analyse
==================================

Was das Skript macht
--------------------
Es liest ``data/elemente.json`` (und, wenn vorhanden, ``data/redaktion.json``)
und beantwortet fünf Fragen:

  A  Bestandsaufnahme – wie viele Elemente wo, wo ist es überfüllt, wo dünn
  B  Dubletten        – welche Spiele sind dasselbe Spiel (Cluster)
                        und welche Spiele sind dieselbe Spielidee (Familien)
  C  Verdichtung      – wie käme man von 795 Spielen auf eine Kernsammlung
  D  Begriffe         – welches Pfadfinder-Vokabular fremder Bünde steckt drin
  E  Passung          – was passt nicht zum Heimabend-Ablauf

Es ändert NICHTS an den Daten. Es schreibt nur nach ``--out``:

  dubletten_cluster.csv   cluster_id; id; titel; quelle; lizenz; aehnlichkeit; vorschlag
  familien.csv            familie; id; titel; quelle; kategorie; unterkategorie; …
  begriffe.csv            begriff; treffer; quellen; beispiel_ids; herkunft; vorschlag; frage
  kernsammlung.csv        id; titel; kategorie; unterkategorie; punkte; rang; empfehlung
  analyse_ergebnis.json   alle Zahlen und Listen (Grundlage für das Prüfdokument)

Aufruf (im Repo-Ordner)
-----------------------
    python3 analyse.py                                  # nimmt data/elemente.json
    python3 analyse.py --daten data/elemente.json --out ./pruefung
    python3 analyse.py --ziel 300                       # Zielgröße der Kernsammlung

Abhängigkeiten
--------------
Nur die Python-Standardbibliothek (Python 3.10+). Optional etwas schneller mit

    pip install rapidfuzz

Ohne rapidfuzz nimmt das Skript ``difflib`` – praktisch dasselbe Ergebnis,
ein paar Sekunden langsamer (einzelne Grenzfälle an der Schwelle können
abweichen, im Test 77 statt 78 Cluster).

Erzeugt wird das Prüfdokument aus ``analyse_ergebnis.json`` von
``pruefdokument.js`` (Node, Paket ``docx``):

    node pruefdokument.js analyse_ergebnis.json Pruefdokument_Heimabend-Baukasten.docx
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

try:  # optional, nur Tempo
    from rapidfuzz import fuzz as _rf_fuzz

    def titel_aehnlich(a: str, b: str) -> float:
        return _rf_fuzz.ratio(a, b) / 100.0
except Exception:  # pragma: no cover
    def titel_aehnlich(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()


# --------------------------------------------------------------------------
# Schwellen – hier drehen, wenn zu viel oder zu wenig gefunden wird
# --------------------------------------------------------------------------
S_TITEL_SICHER = 0.88      # Titel fast gleich -> Dublette
S_TITEL_MIT_TEXT = 0.60    # Titel ähnlich UND Text ähnlich -> Dublette
S_TEXT_MIT_TITEL = 0.30
S_TEXT_ALLEIN = 0.52       # Text sehr ähnlich, Titel egal -> Dublette
S_VERWANDT = 0.22          # darunter: nur "verwandt", keine Dublette
DUENN_ZEICHEN = 300        # Beschreibung kürzer -> "dünn"
SEHR_DUENN = 200
LANG_SPIEL_MIN = 45        # Spiel dauert länger -> passt schlecht als Baustein
ZIEL_STANDARD = 300        # Zielgröße der Kernsammlung

ARTIKEL = ("der ", "die ", "das ", "ein ", "eine ", "den ", "dem ", "des ")

STOPP = set("""
und oder aber auch als also am an auf aus bei bin bis bist da damit dann dass
dem den denn der des dem die dies diese diesem diesen dieser dieses doch dort du
ein eine einem einen einer eines er es etwas euch euer fuer haben hat hatte hier
ich ihr ihm ihn ihnen ihre im in ist ja jede jeden jeder jedes kann kein keine
man mit muss nach nicht noch nun nur ob oder ohne schon sein seine sich sie sind
so soll sollte um und uns unser vom von vor war waren was wenn wer werden wie
wieder wir wird wirst wo zu zum zur ueber alle allen alles beim durch gegen
dabei dazu darf mal mehr sehr viel viele wird kann koennen einfach immer
spieler spielerin spielern mitspieler gruppe gruppen kinder person personen
spiel spiele spielt spielen anzahl minuten minute dauer material ort
spielleiter spielleitung teilnehmer teilnehmerinnen jeweils danach nachdem
""".split())


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------
def falte(s: str) -> str:
    """Kleinschreibung, Umlaute auflösen, Sonderzeichen weg."""
    s = s.lower()
    s = (s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
          .replace("ß", "ss").replace("é", "e").replace("è", "e"))
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def norm_titel(t: str) -> str:
    """Titel vergleichbar machen: Klammern raus, Artikel raus, nur a-z0-9."""
    t = falte(t)
    t = re.sub(r"\([^)]*\)", " ", t)          # (Variante), (Kreisspiel) …
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for a in ARTIKEL:
        if t.startswith(a):
            t = t[len(a):]
            break
    return t.strip()


def wortmenge(text: str) -> list[str]:
    w = [x for x in re.split(r"[^a-z0-9]+", falte(text)) if len(x) >= 4]
    return [x for x in w if x not in STOPP]


def volltext(e: dict) -> str:
    teile = [e.get("titel", ""), e.get("kurz", ""), e.get("beschreibung", ""),
             e.get("tipps", "")]
    for f in ("tags", "themen", "material"):
        v = e.get(f) or []
        if isinstance(v, list):
            teile.extend(str(x) for x in v)
    return "\n".join(str(t) for t in teile if t)


KURZNAME = {
    "Spielewiki": "Spielewiki",
    "pfadfinder-spiele.de": "pfadfinder-spiele",
    "Heimabend-Inspirator (DPBM)": "Inspirator (DPBM)",
    "Heimabend-Baukasten (eigene Sammlung)": "eigene",
    "DPB-Probenbuch (3. Auflage)": "Probenbuch",
}


def kurzquelle(e: dict) -> str:
    n = (e.get("quelle") or {}).get("name", "?")
    return KURZNAME.get(n, n)


def kurzlizenz(e: dict) -> str:
    l = (e.get("quelle") or {}).get("lizenz", "?")
    return "DPB-Probenbuch" if l.startswith("DPB-Probenbuch") else l


def lizenzgruppe(e: dict) -> str:
    """SA und NC dürfen nicht in einem Element gemischt werden."""
    l = kurzlizenz(e)
    if l == "CC BY-SA 4.0":
        return "SA"
    if l.startswith("CC BY-NC"):
        return "NC"
    return "eigen"


def blen(e: dict) -> int:
    return len(e.get("beschreibung") or "")


def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else 0


# --------------------------------------------------------------------------
# Union-Find für die Cluster
# --------------------------------------------------------------------------
class UF:
    def __init__(self):
        self.p: dict[str, str] = {}

    def find(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


# --------------------------------------------------------------------------
# TF-IDF (Standardbibliothek, invertierter Index)
# --------------------------------------------------------------------------
def tfidf(docs: dict[str, str]):
    tf = {i: Counter(wortmenge(t)) for i, t in docs.items()}
    df: Counter = Counter()
    for c in tf.values():
        df.update(c.keys())
    n = len(docs)
    vec: dict[str, dict[str, float]] = {}
    index: dict[str, set[str]] = defaultdict(set)
    for i, c in tf.items():
        v: dict[str, float] = {}
        for w, k in c.items():
            if df[w] < 2 or df[w] > 0.20 * n:      # zu selten / zu häufig
                continue
            v[w] = (1 + math.log(k)) * math.log(n / df[w])
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vec[i] = {w: x / norm for w, x in v.items()}
        for w in v:
            index[w].add(i)
    return vec, index


def cosinus_paare(vec, index, min_score: float) -> dict[tuple[str, str], float]:
    """Nur Paare, die mindestens ein aussagekräftiges Wort teilen."""
    acc: dict[tuple[str, str], float] = defaultdict(float)
    for w, ids in index.items():
        if len(ids) > 130:            # Allerweltswort, bringt nichts
            continue
        ids = sorted(ids)
        for a_i in range(len(ids)):
            a = ids[a_i]
            wa = vec[a].get(w, 0.0)
            for b in ids[a_i + 1:]:
                acc[(a, b)] += wa * vec[b].get(w, 0.0)
    return {k: v for k, v in acc.items() if v >= min_score}


# --------------------------------------------------------------------------
# Teil D: Begriffe
# Belege aus dem DPB-Probenbuch (Proben „Organisatorischer Aufbau“ und
# „Ständeaufbau des DPB“), die in dieser Datenbasis stehen:
#   Einheiten   Horte/Gilde (ab 5) · Trupp (ab 10) · Stamm/Hag (ab 20) ·
#               Jungenschaft/Mädelschaft (ab 40) · Pfadfinderring · Gau · Landesmark
#   Stände      Wildling · Neuling · Wölfling · Jungwolf / Jungpfadfinderin ·
#               Knappe / Gildenmädchen · Späher / Gildin
#   Weiteres    Kluft · Halstuch · Kohte/Jurte · Kornett · Führer/Führerin ·
#               Heimabend · Probe · Versprechen · Allzeit bereit
# Alles, was hier NICHT belegt ist, ist eine offene Frage an Yannick.
# --------------------------------------------------------------------------
BEGRIFFE = [
    ("Sippe / Sippling / Sippenführer", r"\bSipp(e|en|ling|linge|lings)\w*\b",
     "DPBM (Inspirator), DPSG, VCP – und die eigene Sammlung",
     "Im DPB-Probenbuch heißt die kleinste Einheit „Horte“ (Jungen) bzw. „Gilde“ (Mädchen); "
     "„Sippe“ kommt dort nicht vor. ACHTUNG: die eigene Sammlung benutzt „Sippe“ trotzdem, "
     "auch in Titeln wie „Sippenwimpel gestalten“.",
     "Heißt die kleine Gruppe bei euch Sippe oder Horte/Gilde? Einmal festlegen – "
     "davon hängen rund 90 Elemente und mehrere eigene Titel ab."),
    ("Meute", r"\bMeute\w*\b", "DPSG/DPBM (Wölflingsstufe)",
     "Im Probenbuch kommt „Meute“ als Einheit nicht vor.",
     "Wie heißt bei euch die Wölflingsgruppe? Ersetzen durch Horte/Gilde – oder streichen?"),
    ("Wölfling / Wö / Altwolf", r"\bWölfling\w*\b|\bWölfi\w*\b|\bAltwolf\w*\b|\bWö\b",
     "alle Bünde, Wortgebrauch verschieden",
     "„Wölfling“ ist im DPB-Probenbuch belegt (8–11 Jahre) – passt vermutlich.",
     "„Wölfling“ so lassen? Und gilt die Altersspanne 8–11 wie im Probenbuch?"),
    ("Jufi / Jungpfadfinder / Jupfi",
     r"\bJufi\w*\b|\bJungpfadfinder\b|\bJungpfadfinders?\b|\bJupfi\w*\b",
     "DPSG, VCP",
     "Im DPB heißt der Stand „Jungwolf“ (Jungen) bzw. „Jungpfadfinderin“ (Mädchen), je ab 12.",
     "Ersetzen durch „Jungwolf/Jungpfadfinderin“ – oder Stufenangabe ganz weglassen?"),
    ("Pfadi", r"\bPfadis?\b", "Schweiz, DPSG-Umgangssprache",
     "Umgangssprache, im Probenbuch nicht belegt.",
     "„Pfadi“ ersetzen durch „Pfadfinder“?"),
    ("Rover / Ranger / Caravelle", r"\bRover\w*\b|\bRanger\w*\b|\bCaravelle\w*\b",
     "DPSG, VCP, BdP",
     "Im DPB heißen die Älteren „Knappe/Späher“ (Jungen) bzw. „Gildenmädchen/Gildin“ (Mädchen).",
     "Womit ersetzen – „Ältere“, „Knappen/Späher“, oder Stelle streichen?"),
    ("Stamm / Hag", r"\bStamm\b|\bStammes\w*\b|\bStämme\w*\b|\bHag\b",
     "DPB und andere Bünde",
     "„Stamm / Hag“ ist im DPB-Probenbuch belegt (ab 20 Mitglieder) – passt vermutlich.",
     "So lassen? Oder die Fundstellen prüfen, wo „Stamm“ eine fremde Struktur meint?"),
    ("Trupp / Truppstunde", r"\bTrupp\w*\b", "DPB (Einheit ab 10) und DPSG (Stufe)",
     "„Trupp“ ist im DPB eine Einheit – „Truppstunde“ dagegen DPSG-Sprache.",
     "„Trupp“ behalten und „Truppstunde“ zu „Heimabend“ ändern?"),
    ("Horte / Gilde", r"\bHort(e|en)\b|\bGild(e|en|in|innen)\b", "DPB",
     "Beides im Probenbuch belegt (Horte = Jungen, Gilde = Mädchen, je ab 5 Mitglieder).",
     "Bestätigen: benutzt ihr im Alltag wirklich Horte/Gilde – und schreiben wir das in alle Texte?"),
    ("Horde (statt Horte)", r"\bHorde\w*\b", "Schreibfehler / anderes Wort",
     "„Hordentopf“ ist Kochgeschirr und richtig; „Horde“ als Gruppe wäre falsch.",
     "Fundstellen durchsehen: überall „Hordentopf“ gemeint, oder irgendwo „Horte“?"),
    ("Kornett", r"\bKornett\w*\b", "DPB (Amt in der Gruppe)",
     "Im Probenbuch als Amt genannt – passt.",
     "Kornett in der App kurz erklären, damit junge Gruppenführer es verstehen?"),
    ("Gruppenleiter / Leiter:in / Teamer / Betreuer",
     r"\bGruppenleit\w*\b|\bJugendleit\w*\b|\bTeamer\w*\b|\bBetreuer\w*\b|\bAnleiter\w*\b|\bLeiterrunde\w*\b",
     "Jugendarbeit allgemein, DPSG",
     "Deine Sprache (docs/heimabend-definition.md): „Gruppenführer“; das Probenbuch sagt „Führer/Führerin“.",
     "Alles auf „Gruppenführer“ ändern – oder je nach Stelle „Führung“?"),
    ("Spielleiter / Spielleitung", r"\bSpielleit\w*\b", "Spielesammlungen allgemein",
     "Neutral, aber der mit Abstand häufigste Rollenbegriff in den Daten.",
     "„Spielleitung“ so lassen, oder überall „Gruppenführer“ – auch wenn ein Kind das Spiel leitet?"),
    ("Gruppenstunde / Truppstunde / Stufenstunde",
     r"\bGruppenstunde\w*\b|\bTruppstunde\w*\b|\bStufenstunde\w*\b",
     "DPSG, VCP, DPBM",
     "Deine Sprache: „Heimabend“. Das Probenbuch benutzt durchgängig „Heimabend“.",
     "Überall zu „Heimabend“ ändern – auch dort, wo es wörtliches Zitat der Quelle ist?"),
    ("Gut Pfad", r"Gut\s*Pfad", "DPSG, VCP, BdP",
     "Euer Gruß laut heimabend-definition.md und Probenbuch: „Allzeit bereit“.",
     "Ersetzen durch „Allzeit bereit“?"),
    ("Kluft / Tracht / Uniform", r"\bKluft\w*\b|\bTracht\b|\bUniform\w*\b", "DPB: „Kluft“",
     "Im Probenbuch heißt es „Kluft“ (Probe „Unsere Kluft“); „Tracht“ steht dort nur erklärend.",
     "„Tracht“ und „Uniform“ überall zu „Kluft“ ändern?"),
    ("Halstuch", r"\bHalstuch\b|\bHalstücher\b|\bHalstuchs?\b", "alle Bünde",
     "Unproblematisch – nur prüfen, wo es reines Spielmaterial ist.",
     "Als Spielmaterial „Halstuch“ schreiben oder neutral „Tuch“ (dann geht auch ein Geschirrtuch)?"),
    ("Kohte / Jurte", r"\bKohte\w*\b|\bJurte\w*\b", "bündisch, auch DPB",
     "Passt zum DPB (Probenbuch: Probe „Zeltbau“).",
     "Bleiben Kohte/Jurte so stehen? Passen die beschriebenen Bauweisen zu euren Planen?"),
    ("Lagerfeuer / Singerunde / Singewettstreit",
     r"\bLagerfeuer\w*\b|\bSingerunde\w*\b|\bSingewettstreit\w*\b|\bSingekreis\w*\b|\bFeuerrunde\w*\b",
     "bündisch, Wortgebrauch verschieden",
     "Im Probenbuch nicht als fester Begriff belegt.",
     "Welchen Begriff benutzt ihr fürs Singen am Feuer – Singerunde, Feuerrunde, etwas anderes?"),
    ("Versprechen / Gelöbnis / Aufnahme",
     r"\bVersprechen\b|\bGelöbnis\w*\b|\bAufnahmefeier\w*\b", "verschieden",
     "Probenbuch: „Pfadfinderversprechen“ und „Aufnahme“ (Wildling/Neuling).",
     "Einheitlich „Versprechen“ und „Aufnahme“ schreiben?"),
    ("Fremde Bünde (DPSG, VCP, BdP, DPBM …)",
     r"\bDPSG\b|\bVCP\b|\bBdP\b|\bBDP\b|\bDPBM\b|\bPSG\b|St\.?\s?Georgs?[- ]?Pfadfinder\w*\b",
     "fremde Bünde",
     "Als geschichtliche Information in Ordnung, als „bei uns“ falsch. "
     "Achtung: „Orden St. Georg“ ist DPB-eigen und darf bleiben.",
     "Nennungen stehen lassen (Geschichte) oder auf den DPB umschreiben?"),
    ("Jungenschaft / Mädelschaft vs. Jungschar",
     r"\bJungenschaft\w*\b|\bMädelschaft\w*\b|\bMädchenschaft\w*\b|\bJungschar\w*\b",
     "DPB („Jungenschaft/Mädelschaft“) vs. kath./ev. „Jungschar“",
     "„Jungenschaft/Mädelschaft“ ist DPB (ab 40). „Jungschar“ ist fremd.",
     "„Jungschar“ ersetzen – wodurch?"),
    ("Fremde Stufenbezeichnungen (Wichtel, Biber …)",
     r"\bWichtel\w*\b|\bBiber\w*\b|\bPfadfinderstufe\w*\b|\bStufenübergang\w*\b",
     "DPSG, VCP, BdP",
     "Kommen in euren Ständen nicht vor (Wildling, Neuling, Wölfling, Jungwolf, "
     "Knappe, Späher, Gildenmädchen, Gildin).",
     "Auf eure Stände umschreiben oder Stufenangabe ganz weglassen?"),
    ("Gendersternchen (*in)", r"\w+\*(in|innen)\b", "DPBM (Inspirator), pfadfinder-spiele.de",
     "Deine Doku schreibt teils „Gruppenführer*innen“ (README), teils „Gruppenführer“ (Definition).",
     "Welche Schreibweise gilt in der App: „Gruppenführer“, „Gruppenführer und -führerinnen“ oder „*innen“?"),
    ("Gender-Unterstrich (_in)", r"\w+_(in|innen)\b", "DPBM (Inspirator)",
     "Uneinheitlich zum Rest der Sammlung.",
     "Vereinheitlichen – auf welche Form?"),
    ("Gender-Doppelpunkt (:in)", r"\w+:(in|innen)\b", "pfadfinder-spiele.de",
     "Betrifft fast jeden Text dieser Quelle – wäre eine Massenänderung. "
     "CC BY-NC-SA erlaubt Bearbeitung, wenn sie gekennzeichnet wird.",
     "Umschreiben (mit Änderungshinweis) oder als Zitat der Quelle so lassen?"),
    ("Corona / online / digital",
     r"\bCorona\b|\bLockdown\b|\bpandemi\w*\b|\bZoom\b|\bVideokonferenz\w*\b|"
     r"\bdigitale?r?\s+Heimabend\w*\b|\bonline\b",
     "Inspirator 2020/21, teils Spielewiki",
     "Zeitgebundene Inhalte aus der Pandemie.",
     "Corona-/Online-Elemente streichen, oder als eigenen Filter „geht auch digital“ behalten?"),
    ("Schule / Klasse / Unterricht",
     r"\bSchule\w*\b|\bKlassenraum\w*\b|\bKlassenzimmer\w*\b|\bUnterricht\w*\b|\bSchüler\w*\b|\bLehrer\w*\b",
     "Spielewiki (Schul- und Jugendarbeitskontext)",
     "Formulierungen aus der Schule wirken im Heim fremd.",
     "Diese Stellen auf Heimabend-Sprache umschreiben?"),
    ("Kindergeburtstag / Party / Fasching",
     r"\bKindergeburtstag\w*\b|\bGeburtstagsfeier\w*\b|\bParty\w*\b|\bSilvester\w*\b|\bFasching\w*\b|\bKarneval\w*\b",
     "Spielewiki",
     "Der Anlass passt nicht zum Heimabend, das Spiel selbst oft schon.",
     "Anlass-Erwähnungen streichen oder ganze Elemente aussortieren?"),
    ("Alkohol / Trinkspiel",
     r"\bTrinkspiel\w*\b|\bAlkohol\w*\b|\bBier\b|\bSchnaps\w*\b|\bWodka\b|\bbetrunken\w*\b",
     "Spielewiki",
     "Geht bei Kindern und Jugendlichen gar nicht.",
     "Diese Elemente ersatzlos streichen (in redaktion.json unter „gesperrt“)?"),
    ("Anrede: „ihr müsst/sollt/könnt“",
     r"\bihr\s+(müsst|sollt|könnt|habt|seid|bekommt)\b",
     "Inspirator (spricht die Gruppe direkt an)",
     "Der Inspirator redet die Gruppe an, Spielewiki beschreibt neutral – zwei Tonfälle in einer App.",
     "Welchen Tonfall soll die App haben: neutrale Beschreibung oder Ansprache an den Gruppenführer?"),
]


# --------------------------------------------------------------------------
# Teil B2: Spielfamilien – Mechanik-Gruppen zum härteren Zusammenfassen
#   (Name, Regex auf den gefalteten TITEL, Regex zusätzlich auf den Volltext)
# --------------------------------------------------------------------------
FAMILIEN = [
    ("Fangen (alle Varianten)",
     r"fangen|faenger|fangspiel|abschlagen|versteinern|kettenfang",
     r"\bfangen\b|\bfaenger\b|\bkettenfangen\b|\bversteinert\b"),
    ("Ball- und Wurfspiele",
     r"ball|baseball|voelkerball|brennball|frisbee|wurf|werfen",
     r"\bvoelkerball\b|\bbrennball\b|\bball\b"),
    ("Namens- und Kennenlernspiele",
     r"namen|name|kennenlern|vorstell|steckbrief",
     r"\bnamensspiel\b|\bkennenlernspiel\b|namen (lernen|merken)"),
    ("Kim-Spiele (Sinne und Merken)",
     r"\bkim|kimspiel|merkspiel|gedaechtnis|memory|memorix",
     r"\bkim-?spiel\b|\bmerkspiel\b|\bgedaechtnisspiel\b"),
    ("Staffel- und Wettlaufspiele",
     r"staffel|wettlauf|lauf|rennen|wettrennen|parcours|hindernis",
     r"\bstaffel\b|\bstaffellauf\b"),
    ("Verstecken, Suchen, Schatzsuche",
     r"versteck|suche|suchen|sucher|schatzsuche|schnitzeljagd|jagd",
     r"\bverstecken\b|\bschatzsuche\b|\bschnitzeljagd\b"),
    ("Werwolf, Mafia, Mörderspiele",
     r"werwolf|mafia|moerder|mordern|krimi|detektiv|spion",
     r"\bwerwolf\b|\bmafia\b|\bmoerderspiel\b|\bdorfbewohner\b"),
    ("Pantomime, Raten, Darstellen",
     r"pantomime|scharade|montagsmaler|tabu|raten|ratespiel|wer bin ich|zeichnen",
     r"\bpantomime\b|\bscharade\b|\bmontagsmaler\b|\bwer bin ich\b"),
    ("Stuhlkreis-Spiele (Reise nach Jerusalem, Obstsalat …)",
     r"stuhl|jerusalem|obstsalat|obstkorb|platzwechsel|alle die",
     r"\bstuhlkreis\b|\breise nach jerusalem\b|\bobstsalat\b|\bplatz(wechsel|tausch)\b"),
    ("Blind- und Vertrauensspiele",
     r"blind|vertrauen|augen verbunden|tast",
     r"\bvertrauensspiel\b|\bverbundenen augen\b|\baugen verbunden\b|\bvertrauensfall\b"),
    ("Luftballon-Spiele", r"luftballon|ballon", r"\bluftballon\w*\b"),
    ("Wäscheklammer-Spiele", r"waescheklammer|klammer", r"\bwaescheklammer\w*\b"),
    ("Zeitungs- und Papierspiele",
     r"zeitung|papier|papierflieger|zettel", r"\bzeitung(spapier|en)?\b|\bpapierflieger\b"),
    ("Seil-, Knoten- und Kooperationsaufgaben",
     r"seil|knoten|gordisch|spinnennetz|turmbau|saeureteich",
     r"\bgordische[rn]? knoten\b|\bspinnennetz\b|\bsaeureteich\b|\bturmbau\b"),
    ("Klatsch-, Rhythmus- und Singspiele",
     r"klatsch|rhythmus|singspiel|lied|singen|melodie|musik",
     r"\bklatschspiel\b|\brhythmusspiel\b|\bsingspiel\b"),
    ("Stille Post und Weitergabespiele",
     r"stille post|post|weitergabe|kette", r"\bstille post\b"),
    ("Papier-und-Stift-Spiele (Stadt-Land-Fluss, Bingo …)",
     r"stadt land fluss|galgenmaennchen|bingo|domino|kreuzwort|buchstaben|woerter|wort",
     r"\bstadt.?land.?fluss\b|\bgalgenmaennchen\b|\bbingo\b"),
    ("Gelände- und Nachtspiele",
     r"gelaendespiel|nachtspiel|nachtgelaende|raeuber|gendarm|capture the flag|schmuggel|grenz",
     r"\bgelaendespiel\b|\bnachtspiel\b|\braeuber und gendarm\b|\bcapture the flag\b|\bschmuggel\w*\b"),
    ("Kraft- und Kampfspiele",
     r"kampf|ringen|tauzieh|hahnenkampf|schwert|ritter",
     r"\bhahnenkampf\b|\btauziehen\b|\bringkampf\b"),
    ("Quiz- und Wissensspiele",
     r"quiz|wissen|frage|raetsel|1 2 oder 3", r"\bquiz\b|\bquizfragen\b|\bwissensfragen\b"),
]


# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Prüf-Analyse für den Heimabend-Baukasten")
    ap.add_argument("--daten", default="data/elemente.json")
    ap.add_argument("--redaktion", default="data/redaktion.json")
    ap.add_argument("--out", default=".")
    ap.add_argument("--ziel", type=int, default=ZIEL_STANDARD,
                    help="Zielgröße der Kernsammlung an Spielen (Standard 300)")
    args = ap.parse_args()

    pfad = Path(args.daten)
    if not pfad.exists():
        sys.exit(f"Nicht gefunden: {pfad} – bitte im Repo-Ordner ausführen oder --daten setzen.")
    roh = json.loads(pfad.read_text(encoding="utf-8"))
    alle: list[dict] = roh["elemente"]
    byid = {e["id"]: e for e in alle}

    red = {}
    rp = Path(args.redaktion)
    if rp.exists():
        red = json.loads(rp.read_text(encoding="utf-8"))
    keine_dublette = {frozenset(x["ids"]) for x in red.get("keine_dublette", [])}
    auch_dublette = [frozenset(x["ids"]) for x in red.get("auch_dublette", [])]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    erg: dict = {"anzahl_gesamt": len(alle), "ziel": args.ziel}

    spiele = [e for e in alle if e.get("bereich") == "spiel"]
    erg["anzahl_spiele"] = len(spiele)
    txt = {e["id"]: volltext(e) for e in alle}
    ftxt = {i: falte(t) for i, t in txt.items()}

    # ==================================================================
    # TEIL A – Bestandsaufnahme
    # ==================================================================
    def zaehl(feld, menge=alle):
        c = Counter()
        for e in menge:
            v = e.get(feld)
            if isinstance(v, list):
                if not v:
                    c["(ohne Angabe)"] += 1
                else:
                    c.update(v)
            else:
                c[v if (v not in ("", None)) else "(ohne Angabe)"] += 1
        return c

    erg["A_bereich"] = zaehl("bereich").most_common()
    erg["A_quelle"] = Counter(kurzquelle(e) for e in alle).most_common()
    erg["A_lizenz"] = Counter(kurzlizenz(e) for e in alle).most_common()
    erg["A_umfang"] = zaehl("umfang").most_common()
    erg["A_kategorie_spiel"] = zaehl("kategorie", spiele).most_common()
    erg["A_unterkategorie_spiel"] = zaehl("unterkategorie", spiele).most_common()
    erg["A_altersstufen"] = zaehl("altersstufen").most_common()
    erg["A_slots"] = zaehl("slots").most_common()
    erg["A_ort"] = zaehl("ort").most_common()
    erg["A_vorbereitung"] = zaehl("vorbereitung").most_common()
    erg["A_modus"] = zaehl("modus", spiele).most_common()
    erg["A_sozialform"] = zaehl("sozialform", spiele).most_common()
    erg["A_wirkung"] = zaehl("wirkung", spiele).most_common()

    qb: dict[str, Counter] = defaultdict(Counter)
    for e in alle:
        qb[kurzquelle(e)][e.get("bereich", "?")] += 1
    erg["A_quelle_bereich"] = {k: dict(v) for k, v in qb.items()}

    kq: dict[str, Counter] = defaultdict(Counter)
    for e in spiele:
        kq[e.get("kategorie") or "(leer)"][kurzquelle(e)] += 1
    erg["A_kategorie_quelle"] = {k: dict(v) for k, v in kq.items()}

    erg["A_luecken"] = {
        "Beschreibung unter 200 Zeichen": sum(1 for e in alle if blen(e) < SEHR_DUENN),
        "Beschreibung unter 300 Zeichen": sum(1 for e in alle if blen(e) < DUENN_ZEICHEN),
        "Beschreibung unter 600 Zeichen": sum(1 for e in alle if blen(e) < 600),
        "ohne Altersstufe": sum(1 for e in alle if not e.get("altersstufen")),
        "ohne alter_ab": sum(1 for e in alle if not e.get("alter_ab")),
        "ohne Dauer (dauer_min fehlt/0)": sum(1 for e in alle if not e.get("dauer_min")),
        "ohne Gruppengröße (min)": sum(1 for e in alle if not e.get("gruppe_min")),
        "ohne Gruppengröße (max)": sum(1 for e in alle if not e.get("gruppe_max")),
        "ohne Material-Angabe (leere Liste)": sum(1 for e in alle if not e.get("material")),
        "ohne Tipps": sum(1 for e in alle if not (e.get("tipps") or "").strip()),
        "ohne Tags": sum(1 for e in alle if not e.get("tags")),
    }
    erg["A_luecken_spiele"] = {
        "Spiele mit Beschreibung unter 300 Zeichen": sum(1 for e in spiele if blen(e) < DUENN_ZEICHEN),
        "Spiele ohne Altersstufe": sum(1 for e in spiele if not e.get("altersstufen")),
        "Spiele ohne Tipps": sum(1 for e in spiele if not (e.get("tipps") or "").strip()),
        "Spiele ohne Wirkung": sum(1 for e in spiele if not e.get("wirkung")),
        "Spiele ohne Gruppengröße (max)": sum(1 for e in spiele if not e.get("gruppe_max")),
    }

    lq: dict[str, list[int]] = defaultdict(list)
    for e in alle:
        lq[kurzquelle(e)].append(blen(e))
    erg["A_laenge_je_quelle"] = {
        k: {"anzahl": len(v), "median_zeichen": median(v),
            "unter_300": sum(1 for x in v if x < DUENN_ZEICHEN)}
        for k, v in sorted(lq.items())
    }

    # ==================================================================
    # TEIL B1 – Dubletten unter den Spielen
    # ==================================================================
    nt = {e["id"]: norm_titel(e["titel"]) for e in spiele}
    ttok = {i: set(t.split()) for i, t in nt.items()}
    vec, index = tfidf({e["id"]: (e.get("kurz", "") + "\n" + e.get("beschreibung", ""))
                        for e in spiele})
    text_paare = cosinus_paare(vec, index, S_VERWANDT)

    kandidaten: dict[tuple[str, str], dict] = {}

    def merke(a, b, ts, ds, grund):
        k = (a, b) if a < b else (b, a)
        alt = kandidaten.get(k)
        score = max(ts, ds)
        if not alt or score > alt["score"]:
            kandidaten[k] = {"titel_sim": round(ts, 3), "text_sim": round(ds, 3),
                             "score": score, "grund": grund}

    gleich: dict[str, list[str]] = defaultdict(list)
    for i, t in nt.items():
        gleich[t].append(i)
    for t, ids in gleich.items():
        if len(ids) > 1:
            for a_i in range(len(ids)):
                for b in ids[a_i + 1:]:
                    merke(ids[a_i], b, 1.0,
                          text_paare.get(tuple(sorted((ids[a_i], b))), 0.0), "gleicher Titel")

    block: dict[str, set[str]] = defaultdict(set)
    for i, toks in ttok.items():
        for w in toks:
            if len(w) >= 4:
                block[w].add(i)
        s = nt[i].replace(" ", "")
        if len(s) >= 4:
            block["#" + s[:4]].add(i)
    gesehen: set[tuple[str, str]] = set()
    for w, ids in block.items():
        if len(ids) > 60:
            continue
        ids = sorted(ids)
        for a_i in range(len(ids)):
            a = ids[a_i]
            for b in ids[a_i + 1:]:
                k = (a, b)
                if k in gesehen:
                    continue
                gesehen.add(k)
                ts = titel_aehnlich(nt[a], nt[b])
                ds = text_paare.get(k, 0.0)
                if ts >= S_TITEL_SICHER:
                    merke(a, b, ts, ds, "Titel fast gleich")
                elif ts >= S_TITEL_MIT_TEXT and ds >= S_TEXT_MIT_TITEL:
                    merke(a, b, ts, ds, "Titel ähnlich + Text ähnlich")

    for (a, b), ds in text_paare.items():
        if ds >= S_TEXT_ALLEIN:
            merke(a, b, titel_aehnlich(nt[a], nt[b]), ds, "Beschreibung sehr ähnlich")

    for e in spiele:
        for d in e.get("dubletten") or []:
            if d in nt:
                k = tuple(sorted((e["id"], d)))
                merke(k[0], k[1], titel_aehnlich(nt[k[0]], nt[k[1]]),
                      text_paare.get(k, 0.0), "in den Daten als Dublette markiert")
    for fs in auch_dublette:
        ids = [i for i in fs if i in nt]
        for a_i in range(len(ids)):
            for b in ids[a_i + 1:]:
                k = tuple(sorted((ids[a_i], b)))
                merke(k[0], k[1], titel_aehnlich(nt[k[0]], nt[k[1]]),
                      text_paare.get(k, 0.0), "redaktion.json: auch_dublette")

    for k in list(kandidaten):
        if frozenset(k) in keine_dublette:
            del kandidaten[k]

    uf = UF()
    for a, b in kandidaten:
        uf.union(a, b)
    cl: dict[str, list[str]] = defaultdict(list)
    for i in nt:
        cl[uf.find(i)].append(i)
    cluster = [sorted(v) for v in cl.values() if len(v) > 1]
    cluster.sort(key=lambda v: (-len(v), byid[v[0]]["titel"]))

    def hauptelement(ids: list[str]) -> str:
        def rang(i):
            e = byid[i]
            return (0 if i.startswith("eig-") else 1,
                    -len(e.get("beschreibung") or ""),
                    0 if e.get("altersstufen") else 1,
                    0 if (e.get("tipps") or "").strip() else 1, i)
        return sorted(ids, key=rang)[0]

    cluster_daten = []
    for n, ids in enumerate(cluster, start=1):
        haupt = hauptelement(ids)
        lg = {lizenzgruppe(byid[i]) for i in ids}
        gemischt = len(lg - {"eigen"}) > 1
        sims = {}
        for i in ids:
            if i == haupt:
                sims[i] = 1.0
            else:
                k = tuple(sorted((i, haupt)))
                v = kandidaten.get(k)
                sims[i] = v["score"] if v else max(titel_aehnlich(nt[i], nt[haupt]),
                                                   text_paare.get(k, 0.0))
        gruende = {kandidaten[k]["grund"] for k in kandidaten if k[0] in ids and k[1] in ids}
        cluster_daten.append({
            "cluster_id": f"C{n:03d}", "haupt": haupt, "ids": ids,
            "titel": [byid[i]["titel"] for i in ids],
            "quellen": sorted({kurzquelle(byid[i]) for i in ids}),
            "lizenzen": sorted({kurzlizenz(byid[i]) for i in ids}),
            "lizenz_gemischt": gemischt,
            "aehnlichkeit": {i: round(sims[i], 2) for i in ids},
            "gruende": sorted(gruende),
        })
    erg["B_cluster_anzahl"] = len(cluster_daten)
    erg["B_betroffene_spiele"] = sum(len(c["ids"]) for c in cluster_daten)
    erg["B_einsparung"] = sum(len(c["ids"]) - 1 for c in cluster_daten)
    erg["B_cluster_gemischte_lizenz"] = sum(1 for c in cluster_daten if c["lizenz_gemischt"])
    erg["B_cluster"] = cluster_daten

    def vorschlag_fuer(c, i):
        e = byid[i]
        if i == c["haupt"]:
            return "behalten (Hauptelement)"
        if c["lizenz_gemischt"] and lizenzgruppe(e) != lizenzgruppe(byid[c["haupt"]]):
            return "als Variante verweisen (Lizenz nicht mischen!)"
        if c["aehnlichkeit"][i] >= 0.85:
            return "streichen (praktisch identisch)"
        return "als Variante zusammenlegen"

    with (out / "dubletten_cluster.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["cluster_id", "id", "titel", "quelle", "lizenz", "aehnlichkeit", "vorschlag"])
        for c in cluster_daten:
            for i in c["ids"]:
                e = byid[i]
                w.writerow([c["cluster_id"], i, e["titel"], kurzquelle(e), kurzlizenz(e),
                            c["aehnlichkeit"][i], vorschlag_fuer(c, i)])

    # ==================================================================
    # TEIL B2 – Spielfamilien (Mechanik-Gruppen)
    # ==================================================================
    in_dublette = {i for c in cluster_daten for i in c["ids"] if i != c["haupt"]}
    familien = []
    schon_familie: set[str] = set()
    for name, pt, ptext in FAMILIEN:
        rt = re.compile(pt, re.I)
        rx = re.compile(ptext, re.I) if ptext else None
        mitglieder = []
        for e in spiele:
            treffer_titel = bool(rt.search(falte(e["titel"])))
            treffer_text = bool(rx and rx.search(ftxt[e["id"]]))
            if treffer_titel or treffer_text:
                mitglieder.append((e["id"], "Titel" if treffer_titel else "Text"))
        if len(mitglieder) < 4:
            continue
        nur_titel = [i for i, w in mitglieder if w == "Titel"]
        familien.append({
            "familie": name,
            "anzahl": len(mitglieder),
            "anzahl_titel": len(nur_titel),
            "ids": [i for i, _ in mitglieder],
            "ids_titel": nur_titel,
            "beispiele": [(i, byid[i]["titel"]) for i in nur_titel[:8]],
            # Vorschlag: pro Familie so viele behalten, dass die Spannweite bleibt
            "behalten_vorschlag": max(2, round(len(nur_titel) ** 0.5) + 1),
        })
        schon_familie.update(nur_titel)
    familien.sort(key=lambda x: -x["anzahl_titel"])
    erg["B_familien"] = familien
    erg["B_familien_abdeckung"] = len(schon_familie)

    with (out / "familien.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["familie", "id", "titel", "quelle", "kategorie", "unterkategorie",
                    "dauer_min", "dauer_max", "vorschlag"])
        for fam in familien:
            for i in fam["ids_titel"]:
                e = byid[i]
                v = ("Dublette – siehe dubletten_cluster.csv" if i in in_dublette
                     else "Familie durchsehen: behalten oder als Variante anhängen")
                w.writerow([fam["familie"], i, e["titel"], kurzquelle(e),
                            e.get("kategorie") or "", e.get("unterkategorie") or "",
                            e.get("dauer_min") or "", e.get("dauer_max") or "", v])

    # ==================================================================
    # TEIL C – Verdichtung / Kernsammlung
    # ==================================================================
    duenn = {e["id"] for e in spiele if blen(e) < DUENN_ZEICHEN}
    sehr_duenn = {e["id"] for e in spiele if blen(e) < SEHR_DUENN}
    lang = {e["id"] for e in spiele
            if (e.get("dauer_min") or 0) >= LANG_SPIEL_MIN or e.get("umfang") == "ganzer_abend"}
    ohne_alter = {e["id"] for e in spiele if not e.get("altersstufen")}
    hohe_vorbereitung = {e["id"] for e in spiele if e.get("vorbereitung") == "hoch"}
    viel_material = {e["id"] for e in spiele if len(e.get("material") or []) >= 4}
    grossgruppe = {e["id"] for e in spiele if (e.get("gruppe_min") or 0) >= 15}
    corona = {e["id"] for e in spiele
              if re.search(r"corona|lockdown|pandemi|videokonferenz|\bzoom\b|\bonline\b",
                           txt[e["id"]], re.I)}
    trinkspiel = {e["id"] for e in spiele
                  if re.search(r"trinkspiel|\balkohol|\bbier\b|schnaps|\bwodka\b|betrunken",
                               txt[e["id"]], re.I)}
    party = {e["id"] for e in spiele
             if re.search(r"kindergeburtstag|geburtstagsfeier|\bparty\b|silvester|fasching|karneval",
                          txt[e["id"]], re.I)}

    kriterien = [
        ("Dubletten – zweite und weitere Fassung desselben Spiels", in_dublette,
         "zusammenlegen; nur das Hauptelement bleibt"),
        ("Spiel gehört zu einer großen Spielfamilie (Fangen, Ball, Kim …)", schon_familie,
         "Familie auf 3–8 Vertreter eindampfen, Rest als Variante anhängen"),
        ("Beschreibung unter 200 Zeichen", sehr_duenn, "nachschreiben oder streichen"),
        ("Beschreibung unter 300 Zeichen", duenn, "prüfen"),
        ("Spiel dauert 45 min oder länger / ganzer Abend", lang,
         "nicht als Baustein führen, sondern als „ganzer Abend“"),
        ("keine Altersstufe hinterlegt", ohne_alter,
         "nachtragen – sonst greift der Altersfilter nicht"),
        ("Vorbereitung „hoch“", hohe_vorbereitung, "für den Wochen-Heimabend meist unrealistisch"),
        ("vier oder mehr Materialien nötig", viel_material, "prüfen: ist das im Heim da?"),
        ("braucht 15 Personen oder mehr", grossgruppe,
         "für eine Horte/Gilde (ab 5) meist zu groß"),
        ("Corona-/Online-Bezug", corona, "streichen oder als Filter „geht auch digital“"),
        ("Alkohol / Trinkspiel", trinkspiel, "streichen, passt nicht zu Kindern"),
        ("Kindergeburtstag / Party / Fasching", party, "Anlass umschreiben oder streichen"),
    ]
    erg["C_kriterien"] = [{"kriterium": k, "anzahl": len(s), "empfehlung": t,
                           "beispiele": [(i, byid[i]["titel"]) for i in sorted(s)[:4]]}
                          for k, s, t in kriterien]

    # --- Kern-Punkte: was spricht dafür, ein Spiel in die Kernsammlung zu nehmen
    def punkte(e: dict) -> tuple[int, list[str]]:
        p, warum = 0, []
        i = e["id"]
        if i.startswith("eig-"):
            p += 3
            warum.append("eigene Sammlung")
        if i in in_dublette:
            p -= 6
            warum.append("Dublette")
        b = blen(e)
        if b >= 700:
            p += 2
            warum.append("ausführlich beschrieben")
        elif b < DUENN_ZEICHEN:
            p -= 2
            warum.append("dünn beschrieben")
        if e.get("altersstufen"):
            p += 2
            warum.append("Altersstufe da")
        if (e.get("tipps") or "").strip():
            p += 1
            warum.append("Tipps da")
        d = e.get("dauer_max") or e.get("dauer_min") or 0
        if 0 < d <= 20:
            p += 2
            warum.append("kurz genug für einen Slot")
        elif d >= LANG_SPIEL_MIN:
            p -= 2
            warum.append("zu lang für einen Baustein")
        if not (e.get("material") or []):
            p += 2
            warum.append("kein Material")
        elif len(e.get("material") or []) >= 4:
            p -= 1
            warum.append("viel Material")
        if e.get("vorbereitung") == "gering":
            p += 1
        elif e.get("vorbereitung") == "hoch":
            p -= 2
            warum.append("viel Vorbereitung")
        if (e.get("gruppe_min") or 0) >= 15:
            p -= 2
            warum.append("braucht große Gruppe")
        if i in corona:
            p -= 3
            warum.append("Corona/Online")
        if i in (trinkspiel | party):
            p -= 4
            warum.append("Anlass passt nicht")
        if e.get("ort") == "beides":
            p += 1
        if len(e.get("wirkung") or []) >= 1:
            p += 1
        return p, warum

    bewertet = []
    for e in spiele:
        p, warum = punkte(e)
        bewertet.append({"id": e["id"], "titel": e["titel"],
                         "kategorie": e.get("kategorie") or "(leer)",
                         "unterkategorie": e.get("unterkategorie") or "(leer)",
                         "punkte": p, "warum": warum})

    # --- Quoten je Unterkategorie: proportional, aber mit Mindestzahl
    uk_ist = Counter(b["unterkategorie"] for b in bewertet)
    n_sp = len(spiele)
    ziel = args.ziel
    quote = {k: int(max(4, min(v, round(v * ziel / n_sp)))) for k, v in uk_ist.items()}
    # feinjustieren, damit die Summe das Ziel trifft
    schutz = 0
    while sum(quote.values()) > ziel and schutz < 10000:
        schutz += 1
        kandidat = [x for x in quote if quote[x] > 4]
        if not kandidat:
            break
        k = max(kandidat, key=lambda x: (quote[x] / max(1, uk_ist[x]), quote[x]))
        quote[k] -= 1
    schutz = 0
    while sum(quote.values()) < ziel and schutz < 10000:
        schutz += 1
        kandidat = [x for x in quote if quote[x] < uk_ist[x]]
        if not kandidat:
            break
        k = min(kandidat, key=lambda x: (quote[x] / max(1, uk_ist[x]), -uk_ist[x]))
        quote[k] += 1

    nach_uk: dict[str, list[dict]] = defaultdict(list)
    for b in bewertet:
        nach_uk[b["unterkategorie"]].append(b)
    kern: set[str] = set()
    for k, liste in nach_uk.items():
        liste.sort(key=lambda b: (-b["punkte"], b["titel"]))
        for n, b in enumerate(liste):
            b["rang"] = n + 1
            b["empfehlung"] = "Kern" if n < quote.get(k, 0) else "Reserve (zweite Reihe)"
            if b["empfehlung"] == "Kern":
                kern.add(b["id"])
    erg["C_kern_anzahl"] = len(kern)
    erg["C_quoten"] = [{"unterkategorie": k, "ist": uk_ist[k], "kern": quote[k],
                        "reserve": uk_ist[k] - quote[k]}
                       for k in sorted(uk_ist, key=lambda x: -uk_ist[x])]

    with (out / "kernsammlung.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "titel", "quelle", "kategorie", "unterkategorie",
                    "punkte", "rang_in_unterkategorie", "empfehlung", "warum"])
        for b in sorted(bewertet, key=lambda x: (x["unterkategorie"], x["rang"])):
            w.writerow([b["id"], b["titel"], kurzquelle(byid[b["id"]]), b["kategorie"],
                        b["unterkategorie"], b["punkte"], b["rang"], b["empfehlung"],
                        ", ".join(b["warum"])])

    # --- stufenweiser Fahrplan (Vereinigung, damit nichts doppelt gezählt wird)
    stufen = []
    rest = {e["id"] for e in spiele}
    for name, menge in [
        ("Dubletten zusammenlegen", in_dublette),
        ("Alkohol-, Party- und Faschingsspiele streichen", trinkspiel | party),
        ("Corona-/Online-Spiele streichen oder umetikettieren", corona),
        ("Spiele ab 45 min als „ganzer Abend“ ausbuchen", lang),
        ("Vorbereitung „hoch“ aussortieren", hohe_vorbereitung),
        ("Spiele mit unter 300 Zeichen Beschreibung nachschreiben oder streichen", duenn),
        ("Spiele, die 15 Personen und mehr brauchen, aussortieren", grossgruppe),
    ]:
        raus = rest & menge
        rest -= raus
        stufen.append({"schritt": name, "entfernt": len(raus), "verbleibend": len(rest)})
    stufen.append({"schritt": f"Spielfamilien eindampfen, Quoten je Unterkategorie (Ziel {ziel})",
                   "entfernt": max(0, len(rest) - ziel), "verbleibend": min(len(rest), ziel)})
    erg["C_fahrplan"] = stufen

    # ==================================================================
    # TEIL D – Begriffe
    # ==================================================================
    begriffe = []
    for name, pat, herkunft, vorschlag, frage in BEGRIFFE:
        flags = 0 if name.startswith("Gender") else re.I
        r = re.compile(pat, flags)
        treffer = []
        for i, t in txt.items():
            m = r.findall(t)
            if m:
                treffer.append((i, len(m)))
        if not treffer:
            continue
        treffer.sort(key=lambda x: -x[1])
        q = Counter(kurzquelle(byid[i]) for i, _ in treffer)
        bsp = []
        for i, _ in treffer[:3]:
            m = r.search(txt[i])
            stelle = ""
            if m:
                a = max(0, m.start() - 55)
                stelle = re.sub(r"\s+", " ", txt[i][a:m.end() + 55]).strip()
            bsp.append({"id": i, "titel": byid[i]["titel"], "stelle": stelle})
        # in wie vielen Titeln steckt der Begriff? (Titel ändern = sichtbarste Änderung)
        im_titel = [i for i, _ in treffer if r.search(byid[i]["titel"])]
        begriffe.append({
            "begriff": name, "elemente": len(treffer), "treffer": sum(n for _, n in treffer),
            "im_titel": len(im_titel), "titel_beispiele": [byid[i]["titel"] for i in im_titel[:4]],
            "quellen": dict(q.most_common()), "herkunft": herkunft,
            "vorschlag": vorschlag, "frage": frage, "beispiele": bsp,
            "beispiel_ids": [i for i, _ in treffer[:3]],
        })
    begriffe.sort(key=lambda x: -x["elemente"])
    erg["D_begriffe"] = begriffe

    with (out / "begriffe.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["begriff", "elemente", "treffer", "im_titel", "quellen",
                    "beispiel_ids", "herkunft", "vorschlag", "frage"])
        for b in begriffe:
            w.writerow([b["begriff"], b["elemente"], b["treffer"], b["im_titel"],
                        ", ".join(f"{k} ({v})" for k, v in b["quellen"].items()),
                        ", ".join(b["beispiel_ids"]), b["herkunft"], b["vorschlag"], b["frage"]])

    # ==================================================================
    # TEIL E – Passung
    # ==================================================================
    def ids_wo(pat, menge=alle):
        r = re.compile(pat, re.I)
        return [e["id"] for e in menge if r.search(txt[e["id"]])]

    fremde_struktur = ids_wo(r"\bSipp\w*\b|\bMeute\w*\b|\bRover\w*\b|\bRanger\w*\b|"
                             r"\bJufi\w*\b|\bDPSG\b|\bVCP\b|\bBdP\b|\bJungschar\w*\b")
    lieder = ids_wo(r"\bLied\b|\bLieder\b|\bLiederbuch\w*\b|\bGitarre\w*\b|\bSingerunde\w*\b")
    projekte_getarnt = [e["id"] for e in alle
                        if e.get("umfang") == "baustein" and (e.get("dauer_max") or 0) >= 75]
    ganzer_abend_spiel = [e["id"] for e in spiele if e.get("umfang") == "ganzer_abend"]
    slot_eroeffnung = [e["id"] for e in alle if "eroeffnung" in (e.get("slots") or [])]
    slot_abschluss = [e["id"] for e in alle if "abschluss" in (e.get("slots") or [])]
    slot_einstieg = [e["id"] for e in alle if "einstieg" in (e.get("slots") or [])]
    nur_hauptteil = [e["id"] for e in alle if (e.get("slots") or []) == ["hauptteil"]]
    ohne_alter_alle = [e["id"] for e in alle if not e.get("altersstufen")]
    aktivitaet_bausteine = [e["id"] for e in alle
                            if e.get("bereich") in ("natur_draussen", "gemeinschaft")
                            and e.get("umfang") == "baustein"]

    erg["E_passung"] = {
        "Elemente mit fremder Bundesstruktur im Text": len(fremde_struktur),
        "Elemente, die Lieder/Gitarre erwähnen (Liedgut prüfen)": len(lieder),
        "als „baustein“ geführt, dauern aber 75 min oder mehr": len(projekte_getarnt),
        "Spiele, die als „ganzer Abend“ geführt werden": len(ganzer_abend_spiel),
        "Elemente für den Slot „Eröffnungskreis“": len(slot_eroeffnung),
        "Elemente für den Slot „Einstieg“": len(slot_einstieg),
        "Elemente für den Slot „Abschluss“": len(slot_abschluss),
        "Elemente nur für den Hauptteil": len(nur_hauptteil),
        "Elemente ohne Altersstufe": len(ohne_alter_alle),
        "Bausteine für Gemeinschaftsaktivität (natur_draussen + gemeinschaft)":
            len(aktivitaet_bausteine),
    }
    erg["E_beispiele"] = {
        "fremde_struktur": [(i, byid[i]["titel"], kurzquelle(byid[i])) for i in fremde_struktur[:10]],
        "projekte_getarnt": [(i, byid[i]["titel"], byid[i].get("dauer_max")) for i in projekte_getarnt[:10]],
        "ganzer_abend_spiel": [(i, byid[i]["titel"]) for i in ganzer_abend_spiel[:10]],
        "lieder": [(i, byid[i]["titel"], kurzquelle(byid[i])) for i in lieder[:10]],
    }
    erg["E_alter_je_quelle"] = {
        q: {"gesamt": sum(1 for e in alle if kurzquelle(e) == q),
            "ohne_altersstufe": sum(1 for e in alle
                                    if kurzquelle(e) == q and not e.get("altersstufen"))}
        for q in sorted({kurzquelle(e) for e in alle})
    }
    erg["E_bereich_umfang"] = {
        b: dict(Counter(e.get("umfang") for e in alle if e.get("bereich") == b))
        for b in sorted({e.get("bereich") for e in alle})
    }

    (out / "analyse_ergebnis.json").write_text(
        json.dumps(erg, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- kurze Ausgabe auf der Konsole -------------------------------
    print(f"Elemente gesamt: {len(alle)}   davon Spiele: {len(spiele)}")
    print(f"Dubletten-Cluster: {len(cluster_daten)}  betroffene Spiele: {erg['B_betroffene_spiele']}"
          f"  Einsparung: {erg['B_einsparung']}  gemischte Lizenz: {erg['B_cluster_gemischte_lizenz']}")
    print(f"Spielfamilien: {len(familien)}  erfasste Spiele (über den Titel): {len(schon_familie)}")
    print("Fahrplan:")
    for s in stufen:
        print(f"  – {s['schritt']}: -{s['entfernt']}  ->  {s['verbleibend']}")
    print(f"Kernsammlung nach Quoten: {len(kern)} Spiele")
    print(f"Begriffe mit Treffern: {len(begriffe)}")
    print(f"Geschrieben nach: {out.resolve()}")


if __name__ == "__main__":
    main()
