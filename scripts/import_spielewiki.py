#!/usr/bin/env python3
"""
Importiert die Spiele aus dem Spielewiki (https://www.spielewiki.org) über die
MediaWiki-API und mappt sie auf das Element-Schema aus `data/SCHEMA.md`.

Aufruf:
    python3 scripts/import_spielewiki.py             # holt die Daten aus dem Netz
    python3 scripts/import_spielewiki.py --offline   # nutzt nur die gespeicherten Rohdaten

Was passiert:
- `list=categorymembers` liefert alle Seiten der Kategorie "SpieleWiki:Spiel"
- `prop=revisions` holt den Wikitext, in 50er-Paketen, mit 0,5 s Pause und eigenem User-Agent
- Rohdaten: data/quellen/spielewiki/raw/kategorie-mitglieder.json und raw/seiten.json
- Aus jeder Seite werden die Infobox {{Spiel|Art=|AnzahlSpieler=|Ort=|Material=|Dauer=|
  Vorbereitung=}} und der Regeltext gelesen und ins Element-Schema übersetzt
- Ergebnis: data/quellen/spielewiki/elemente.json (wird bei jedem Lauf überschrieben)

Die Infobox-Werte sind Freitext ("ab etwa 10", "kurz", "überall"), deshalb wird
zusätzlich auf die strukturierten [[Kategorie:...]]-Angaben am Seitenende zurückgegriffen
(z. B. "Spiel für 10-20 Spieler", "Spiel ohne Material").

Lizenz der Inhalte: CC BY-SA 4.0 (Fußzeile des Wikis verweist auf
https://creativecommons.org/licenses/by-sa/4.0/). Als Autor wird die Autorenschaft des
Wikis genannt; einzelne Benutzernamen werden nicht übernommen (siehe CLAUDE.md).
Werbe-Bausteine ({{Amazon}}) und Zählpixel ({{METIS}}) werden entfernt.
"""
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

API = "https://www.spielewiki.org/w/api.php"
SEITEN_URL = "https://www.spielewiki.org/wiki/"
KATEGORIE = "Kategorie:SpieleWiki:Spiel"
USER_AGENT = (
    "heimabend-baukasten/0.1 (nicht-kommerzielles Pfadfinder-Projekt, "
    "Import unter CC BY-SA 4.0; Kontakt über das Projekt-Repository)"
)
PAUSE_SEKUNDEN = 0.5
PAKETGROESSE = 50

WURZEL = Path(__file__).resolve().parent.parent
RAW = WURZEL / "data" / "quellen" / "spielewiki" / "raw"
ROH_MITGLIEDER = RAW / "kategorie-mitglieder.json"
ROH_SEITEN = RAW / "seiten.json"
AUSGABE = WURZEL / "data" / "quellen" / "spielewiki" / "elemente.json"

QUELLE = {
    "name": "Spielewiki",
    "autor": "Spielewiki-Autor*innen",
    "lizenz": "CC BY-SA 4.0",
}

# Trinkspiele passen nicht in ein Werkzeug für Kinder- und Jugendgruppen.
# Auf None setzen, wenn doch alles importiert werden soll.
AUSGESCHLOSSENE_WIKI_KATEGORIEN = {"Trinkspiel"}

# Art-Vorlage -> Schema-Kategorie, in dieser Reihenfolge geprüft (erste passende gewinnt).
KATEGORIE_REIHENFOLGE = [
    ("Geländespiel", "gelaende"),
    ("Namenslernspiel", "ankommen"),
    ("Kennenlernspiel", "ankommen"),
    ("Gruppenfindungsspiel", "ankommen"),
    ("Vertrauensspiel", "kooperation"),
    ("Gruppendynamisches Spiel", "kooperation"),
    ("Kooperationsspiel", "kooperation"),
    ("Kommunikationsspiel", "kooperation"),
    ("Reflexionsmethode", "ruhig"),
    ("Kimspiel", "ruhig"),
    ("Merkspiel", "ruhig"),
    ("Denkspiel", "ruhig"),
    ("Rätsel", "ruhig"),
    ("Quiz", "ruhig"),
    ("Ratespiel", "ruhig"),
    ("Konzentrationsspiel", "ruhig"),
    ("Ruhiges Spiel", "ruhig"),
    ("Kreativspiel", "ruhig"),
    ("Kartenspiel", "ruhig"),
    ("Glücksspiel", "ruhig"),
    ("Spiel mit den Sinnen", "ruhig"),
    ("Sitzkreis", "kreis"),
    ("Kreisspiel", "kreis"),
    ("Klatschspiel", "kreis"),
    ("Singspiel", "kreis"),
    ("Musikspiel", "kreis"),
    ("Tanzspiel", "kreis"),
    ("Reaktionsspiel", "kreis"),
    # Verstecken und Suchen sind keine Geländespiele - "Uhrensuche" ist ein
    # ruhiges Suchspiel im Zimmer. Sie laufen über den Ort in bewegung_*.
    ("Versteckspiel", "bewegung"),
    ("Suchspiel", "bewegung"),
    ("Fangspiel", "bewegung"),
    ("Laufspiel", "bewegung"),
    ("Staffelspiel", "bewegung"),
    ("Ballspiel", "bewegung"),
    ("Abschießspiel", "bewegung"),
    ("Kampfspiel", "bewegung"),
    ("Bewegungsspiel", "bewegung"),
    ("Geschicklichkeitsspiel", "bewegung"),
]

# Vorlagen, die ersatzlos aus dem Text verschwinden (Werbung, Navigation, Zählpixel).
TEMPLATE_ENTFERNEN = {
    "amazon", "metis", "box kategorien", "weitere", "bilderwunsch",
    "hauptartikel", "siehe auch", "toc", "nowiki", "lösung", "loesung",
}
# Abschnitte, die nicht in die Beschreibung gehören (Verweise nach außen).
ABSCHNITT_ENTFERNEN = {
    "ähnliche spiele", "ähnliche reflexionsmethoden", "weblinks", "links",
    "quelle", "quellen", "einzelnachweise", "siehe auch",
}
# Abschnitte, die als Praxistipp separat gespeichert werden.
ABSCHNITT_TIPPS = {"hinweis", "hinweise", "tipp", "tipps", "sicherheit", "anmerkung", "anmerkungen"}

WORT_DAUER = [
    ("sehr kurz", (5, 10)),
    ("wenige minuten", (5, 10)),
    ("kurz", (5, 10)),
    ("einige minuten", (10, 20)),
    ("mehrere minuten", (10, 20)),
    ("beliebig", (10, 30)),
    ("lange", (45, 90)),
    ("länger", (45, 90)),
]

WORT_DRAUSSEN = (
    "freien", "draußen", "draussen", "wald", "wiese", "gelände", "park", "sportplatz",
    "laufstrecke", "rasen", "spielplatz", "see", "wasser", "schnee", "garten", "hof",
)
WORT_DRINNEN = (
    "tisch", "sitzkreis", "sesselkreis", "stuhlkreis", "raum", "saal", "halle", "innen",
    "boden", "zimmer", "gruppenraum", "heim", "turnhalle", "sofa",
)


# --------------------------------------------------------------------------
# Netz
# --------------------------------------------------------------------------
def api(parameter):
    """Ruft die MediaWiki-API auf und gibt die geparste Antwort zurück."""
    parameter = dict(parameter)
    parameter["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(parameter)
    anfrage = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(anfrage, timeout=60) as antwort:
        return json.loads(antwort.read().decode("utf-8"))


def hole_kategorie_mitglieder():
    """Alle Seiten der Kategorie SpieleWiki:Spiel (mit Fortsetzung, 500 je Anfrage)."""
    mitglieder = []
    weiter = {}
    while True:
        parameter = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": KATEGORIE,
            "cmlimit": "500",
        }
        parameter.update(weiter)
        antwort = api(parameter)
        mitglieder.extend(antwort["query"]["categorymembers"])
        print("  {} Seiten gelistet ...".format(len(mitglieder)))
        if "continue" not in antwort:
            return mitglieder
        weiter = antwort["continue"]
        time.sleep(PAUSE_SEKUNDEN)


def hole_wikitexte(titel_liste):
    """Holt den Wikitext in 50er-Paketen; gibt {titel: seiten-objekt} zurück."""
    seiten = {}
    for start in range(0, len(titel_liste), PAKETGROESSE):
        paket = titel_liste[start:start + PAKETGROESSE]
        antwort = api({
            "action": "query",
            "prop": "revisions",
            "rvprop": "content|timestamp",
            "rvslots": "main",
            "titles": "|".join(paket),
        })
        for seite in antwort["query"]["pages"].values():
            if "revisions" in seite:
                seiten[seite["title"]] = seite
        print("  {}/{} Seiten geholt".format(min(start + PAKETGROESSE, len(titel_liste)), len(titel_liste)))
        time.sleep(PAUSE_SEKUNDEN)
    return seiten


# --------------------------------------------------------------------------
# Wikitext lesen
# --------------------------------------------------------------------------
def hole_wikitext(seite):
    """Zieht den Quelltext aus dem API-Objekt einer Seite."""
    try:
        return seite["revisions"][0]["slots"]["main"]["*"]
    except (KeyError, IndexError):
        return ""


def finde_infobox(wikitext):
    """
    Findet die {{Spiel ...}}-Infobox und gibt (felder_dict, resttext) zurück.
    Zählt geschweifte Klammern mit, damit verschachtelte Vorlagen wie
    {{Ohne Material}} nicht zum vorzeitigen Ende führen.
    """
    start = wikitext.find("{{Spiel")
    if start == -1:
        return {}, wikitext
    tiefe = 0
    ende = None
    for pos in range(start, len(wikitext) - 1):
        paar = wikitext[pos:pos + 2]
        if paar == "{{":
            tiefe += 1
        elif paar == "}}":
            tiefe -= 1
            if tiefe == 0:
                ende = pos + 2
                break
    if ende is None:
        return {}, wikitext
    inhalt = wikitext[start + 2:ende - 2]
    inhalt = inhalt.split("\n", 1)[1] if "\n" in inhalt else ""

    felder = {}
    for zeile in re.split(r"\n\s*\|", "\n|" + inhalt):
        if "=" not in zeile:
            continue
        schluessel, wert = zeile.split("=", 1)
        felder[schluessel.strip().lstrip("|").strip()] = wert.strip()
    return felder, wikitext[:start] + wikitext[ende:]


def entferne_vorlagen(text):
    """Wirft Werbe-/Navigationsvorlagen raus und macht aus dem Rest lesbaren Text."""
    def ersetze(treffer):
        inhalt = treffer.group(1)
        name = inhalt.split("|")[0].strip().lower()
        if name in TEMPLATE_ENTFERNEN:
            return ""
        teile = [t for t in inhalt.split("|")[1:]]
        if name == "webseite":
            # {{Webseite|1=url|2=Titel}} -> nur den Titel behalten
            for teil in teile:
                if teil.startswith("2="):
                    return teil[2:]
            return ""
        if not teile:
            return inhalt.strip()  # z. B. {{Ohne Material}} -> "Ohne Material"
        return ""

    vorher = None
    while vorher != text:  # mehrfach, damit auch verschachtelte Vorlagen wegkommen
        vorher = text
        text = re.sub(r"\{\{([^{}]*)\}\}", ersetze, text)
    return text


def wikitext_zu_text(wikitext):
    """
    Wandelt den Artikeltext in leichtes Markdown um (## Überschrift, - Aufzählung).
    Gibt (beschreibung, tipps, wiki_kategorien) zurück.
    """
    text = wikitext
    kategorien = [k.strip() for k in re.findall(r"\[\[Kategorie:([^\]|]+)", text)]

    text = re.sub(r"(?s)<!--.*?-->", "", text)
    text = re.sub(r"(?s)<ref[^>]*>.*?</ref>", "", text)
    text = re.sub(r"(?s)<(gallery|imagemap)[^>]*>.*?</\1>", "", text)
    text = re.sub(r"\[\[Kategorie:[^\]]*\]\]", "", text)
    text = re.sub(r"\[\[(Datei|Bild|File|Image):[^\]]*\]\]", "", text)
    text = re.sub(r"\[\[[a-z]{2,3}:[^\]]*\]\]", "", text)  # Interwiki, z. B. [[en:...]]
    text = entferne_vorlagen(text)

    # Wikitabellen ({| ... |}) auf ihre Zellinhalte eindampfen
    text = re.sub(r"(?m)^\s*\{\|.*$", "", text)
    text = re.sub(r"(?m)^\s*\|[}\-+].*$", "", text)
    text = re.sub(r"(?m)^\s*[|!]\s*", "", text)

    # Links: [[Ziel|Text]] -> Text, [[Ziel]] -> Ziel, [http://... Text] -> Text
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[:?(?:Kategorie:)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\s+([^\]]*)\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\]", "", text)

    text = re.sub(r"<[^>]+>", "", text)
    # Wikitext enthält vereinzelt HTML-Entities (z. B. &nbsp; in Koordinaten)
    text = html.unescape(text)

    # Zeilenweise: Überschriften und Aufzählungen aufbereiten.
    # Achtung: das muss VOR der Fett-Umwandlung passieren, sonst hält die
    # Aufzählungs-Erkennung ein **fettes** Wort am Zeilenanfang für einen Punkt.
    abschnitt = ""          # aktuelle Überschrift (klein geschrieben)
    beschreibung, tipps = [], []
    for zeile in text.split("\n"):
        zeile = zeile.rstrip()
        ueberschrift = re.match(r"^\s*(=+)\s*(.+?)\s*=+\s*$", zeile)
        if ueberschrift:
            titel = ueberschrift.group(2)
            ebene = min(len(ueberschrift.group(1)), 4)
            abschnitt = titel.strip().lower()
            if abschnitt in ABSCHNITT_ENTFERNEN:
                continue
            ziel = tipps if abschnitt in ABSCHNITT_TIPPS else beschreibung
            ziel.append("")
            ziel.append("#" * ebene + " " + titel)
            continue
        if abschnitt in ABSCHNITT_ENTFERNEN:
            continue
        ziel = tipps if abschnitt in ABSCHNITT_TIPPS else beschreibung
        aufzaehlung = re.match(r"^\s*[*#]+\s*(.*)$", zeile)
        begriff = re.match(r"^;\s*(.+?)\s*$", zeile)
        erklaerung = re.match(r"^:\s*(.+?)\s*$", zeile)
        if aufzaehlung:
            ziel.append("- " + aufzaehlung.group(1).strip())
        elif begriff:
            # MediaWiki-Definitionsliste: ";Achtung, Verletzungsgefahr!" wäre
            # sonst als Fließtext mit führendem Semikolon gelandet.
            ziel.append("")
            ziel.append("**" + begriff.group(1).rstrip(":") + "**")
        elif erklaerung:
            ziel.append(erklaerung.group(1))
        else:
            ziel.append(zeile.strip())

    def aufraeumen(zeilen):
        ergebnis = "\n".join(zeilen)
        # Fett/kursiv erst jetzt umwandeln (siehe Hinweis oben)
        ergebnis = re.sub(r"'''''(.+?)'''''", r"**\1**", ergebnis)
        ergebnis = re.sub(r"'''(.+?)'''", r"**\1**", ergebnis)
        ergebnis = re.sub(r"''(.+?)''", r"\1", ergebnis)
        ergebnis = re.sub(r"[ \t]+", " ", ergebnis)
        ergebnis = re.sub(r"\n{3,}", "\n\n", ergebnis)
        # Überschrift ohne Inhalt dahinter wieder entfernen
        ergebnis = re.sub(r"\n#+ [^\n]*(?=\n*$)", "", ergebnis)
        return ergebnis.strip()

    return aufraeumen(beschreibung), aufraeumen(tipps), kategorien


# --------------------------------------------------------------------------
# Mapping auf das Schema
# --------------------------------------------------------------------------
def nur_text(wert):
    """Macht aus einem Infobox-Wert (mit Vorlagen/Links) reinen Text."""
    wert = entferne_vorlagen(wert or "")
    wert = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", wert)
    wert = re.sub(r"\[\[([^\]]*)\]\]", r"\1", wert)
    wert = re.sub(r"'{2,}", "", wert)
    wert = re.sub(r"<[^>]+>", "", wert)
    return re.sub(r"\s+", " ", wert).strip()


def art_vorlagen(wert):
    """Zieht die Spielart-Vorlagen aus dem Art-Feld: "{{Fangspiel}}, {{Ballspiel}}"."""
    arten = [a.strip() for a in re.findall(r"\{\{([^}|]+)\}\}", wert or "")]
    if not arten:
        arten = [a.strip() for a in re.split(r"[,/]", nur_text(wert)) if a.strip()]
    return [a for a in arten if a]


def auf_fuenf(minuten):
    return int(round(minuten / 5.0) * 5)


def map_dauer(wert):
    """Freitext-Dauer -> (dauer_min, dauer_max) in Minuten."""
    text = nur_text(wert).lower()
    pro_runde = "pro runde" in text or "pro durchgang" in text
    minimum = maximum = None

    stunden = re.search(r"(\d+)\s*stunde", text)
    spanne = re.search(r"(\d+)\s*(?:-|–|bis)\s*(\d+)", text)
    ab = re.search(r"ab\s*(?:ca\.?|etwa)?\s*(\d+)", text)
    bis = re.search(r"bis\s*(?:zu\s*)?(?:ca\.?|etwa)?\s*(\d+)", text)
    einzeln = re.search(r"(\d+)", text)

    if stunden:
        minimum = int(stunden.group(1)) * 60
        maximum = minimum + 30
    elif spanne:
        minimum, maximum = int(spanne.group(1)), int(spanne.group(2))
    elif ab:
        minimum = int(ab.group(1))
        maximum = minimum * 2
    elif bis:
        maximum = int(bis.group(1))
        minimum = max(5, maximum // 2)
    elif einzeln:
        wert_min = int(einzeln.group(1))
        minimum, maximum = wert_min * 2 // 3, wert_min * 4 // 3
    else:
        for wort, spanne_wort in WORT_DAUER:
            if wort in text:
                minimum, maximum = spanne_wort
                break
    if minimum is None:
        minimum, maximum = 10, 20
    if pro_runde:  # eine Runde ist kurz, gespielt werden mehrere
        minimum, maximum = minimum * 2, maximum * 2
    minimum = max(5, auf_fuenf(minimum))
    maximum = max(minimum + 5, auf_fuenf(maximum or minimum * 2))
    return min(minimum, 120), min(maximum, 180)


def map_ort(wert):
    """Freitext-Ort -> drinnen | draussen | beides."""
    text = nur_text(wert).lower()
    draussen = any(w in text for w in WORT_DRAUSSEN)
    drinnen = any(w in text for w in WORT_DRINNEN)
    if draussen and not drinnen:
        return "draussen"
    if drinnen and not draussen:
        return "drinnen"
    return "beides"  # "überall", "beliebig", "Spielfeld" oder beides genannt


def entferne_leere_ueberschriften(text):
    """Wirft Überschriften weg, unter denen nichts mehr steht."""
    zeilen = text.split("\n")
    ergebnis = []
    for i, zeile in enumerate(zeilen):
        if re.match(r"^#+ ", zeile):
            rest = [z for z in zeilen[i + 1:] if z.strip()]
            if not rest or re.match(r"^#+ ", rest[0]):
                continue
        ergebnis.append(zeile)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(ergebnis)).strip()


def saeubere_loesung(text):
    """Nimmt der Lösungsseite ihre eigene Überschrift und den Vorspann."""
    text = re.sub(r"(?mi)^#+ *Lösung.*$", "", text)
    text = re.sub(r"(?mi)^Lösung\s*$", "", text)
    text = re.sub(r"(?mi)^Diese Seite beschreibt die Lösung.*$", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def entferne_loesungsverweis(text):
    """
    Entfernt den toten Satz "Die Lösung ... findet sich auf X/Lösung."
    Die Unterseite selbst wird jetzt mitgeholt und angehängt.
    """
    text = re.sub(r"(?m)^.*/Lösung.*$", "", text)
    return entferne_leere_ueberschriften(text)


def trenne_ausserhalb_klammern(text):
    """
    Trennt an Komma, Semikolon, " und ", " oder " und " sowie " – aber nicht
    innerhalb von Klammern. Sonst wird aus "20 Spielkarten (doppeldeutsch oder
    französisch)" ein Eintrag "französisch)".
    """
    teile, aktuell, tiefe = [], [], 0
    i = 0
    while i < len(text):
        zeichen = text[i]
        if zeichen in "([":
            tiefe += 1
        elif zeichen in ")]":
            tiefe = max(0, tiefe - 1)
        if tiefe == 0:
            if zeichen in ",;":
                teile.append("".join(aktuell)); aktuell = []; i += 1; continue
            for wort in (" und ", " oder ", " sowie "):
                if text[i:i + len(wort)].lower() == wort:
                    teile.append("".join(aktuell)); aktuell = []; i += len(wort)
                    break
            else:
                aktuell.append(zeichen); i += 1
                continue
            continue
        aktuell.append(zeichen)
        i += 1
    teile.append("".join(aktuell))
    return [t for t in teile if t.strip()]


def map_material(wert, wiki_kategorien):
    """Material-Feld -> Liste; leere Liste heißt: kein Material nötig."""
    text = nur_text(wert)
    if "Spiel ohne Material" in wiki_kategorien:
        return []
    if not text or re.match(r"^(ohne material|kein(e|es|erlei)?|-{1,2}|nichts)$", text.strip(), re.I):
        return []
    teile = [t.strip(" .;") for t in trenne_ausserhalb_klammern(text) if t.strip(" .;")]
    if not teile:
        return []
    # Sehr lange Fließtext-Angaben nicht zerhacken
    if len(text) > 90 and len(teile) > 4:
        return [text]
    return teile[:8]


def map_vorbereitung(wert):
    """Vorbereitung-Feld -> gering | mittel | hoch."""
    text = nur_text(wert).lower().strip(" .-")
    if not text or text in ("keine", "keines", "keinerlei", "nichts", "nein"):
        return "gering"
    if any(w in text for w in ("aufwändig", "aufwendig", "umfangreich", "viel", "lange")):
        return "hoch"
    return "mittel"


def map_gruppengroesse(wert, wiki_kategorien):
    """AnzahlSpieler (Freitext) + Wiki-Kategorien -> (min, max)."""
    text = nur_text(wert).lower()
    text = text.replace("zwei", "2").replace("drei", "3").replace("vier", "4")
    minimum = maximum = None

    spanne = re.search(r"(\d+)\s*(?:-|–|bis(?:\s*etwa|\s*ca\.?)?)\s*(\d+)", text)
    ab = re.search(r"(?:ab|mindestens|min\.?)\s*(?:etwa|ca\.?)?\s*(\d+)", text)
    bis = re.search(r"(?:bis(?:\s*zu)?|höchstens|max\.?)\s*(?:etwa|ca\.?)?\s*(\d+)", text)
    if spanne:
        minimum, maximum = int(spanne.group(1)), int(spanne.group(2))
    elif ab:
        minimum = int(ab.group(1))
    elif bis:
        maximum = int(bis.group(1))
    else:
        einzeln = re.match(r"^\D*(\d+)\D*$", text)
        if einzeln:
            minimum = maximum = int(einzeln.group(1))

    if minimum is None and maximum is None:
        # Rückfall auf die strukturierten Kategorien am Seitenende
        untergrenzen, obergrenzen, offen = [], [], False
        for kategorie in wiki_kategorien:
            if kategorie == "Spiel für einen Spieler":
                untergrenzen.append(1)
                obergrenzen.append(1)
            elif kategorie == "Spiel für zwei Spieler":
                untergrenzen.append(2)
                obergrenzen.append(2)
            elif kategorie == "Spiel für drei Spieler":
                untergrenzen.append(3)
                obergrenzen.append(3)
            elif kategorie == "Spiel für vier Spieler":
                untergrenzen.append(4)
                obergrenzen.append(4)
            elif kategorie == "Spiel für mehr als 20 Spieler":
                untergrenzen.append(20)
                offen = True
            else:
                treffer = re.match(r"Spiel für (\d+)-(\d+) Spieler", kategorie)
                if treffer:
                    untergrenzen.append(int(treffer.group(1)))
                    obergrenzen.append(int(treffer.group(2)))
        if untergrenzen:
            minimum = min(untergrenzen)
        if obergrenzen and not offen:
            maximum = max(obergrenzen)
    if minimum and maximum and maximum < minimum:
        minimum, maximum = maximum, minimum
    return minimum, maximum


def map_kategorie(arten, ort):
    """Spielart-Vorlagen -> eine Kategorie aus dem Schema."""
    arten_klein = [a.lower() for a in arten]
    for schluessel, kategorie in KATEGORIE_REIHENFOLGE:
        if schluessel.lower() in arten_klein:
            if kategorie == "bewegung":
                return "bewegung_draussen" if ort == "draussen" else "bewegung_drinnen"
            return kategorie
    return "bewegung_draussen" if ort == "draussen" else "bewegung_drinnen"


def map_slots(arten, kategorie, dauer_min):
    """Wo im Heimabend passt das Spiel?"""
    arten_klein = [a.lower() for a in arten]
    slots = []
    if kategorie == "ankommen" or dauer_min <= 10:
        slots.append("einstieg")
    slots.append("hauptteil")  # jedes Spiel kann im Hauptteil vorkommen
    if dauer_min <= 15 and kategorie in ("kreis", "ruhig", "ankommen"):
        slots.append("abschluss")
    if "reflexionsmethode" in arten_klein and "abschluss" not in slots:
        slots.append("abschluss")
    return slots or ["hauptteil"]


def baue_tags(arten, wiki_kategorien, material):
    """Stichworte für Suche und Filter."""
    tags = list(arten)
    for kategorie in wiki_kategorien:
        # Spieleranzahl steckt schon in gruppe_min/max
        if re.match(r"Spiel für (\d|einen|zwei|drei|vier|mehr)", kategorie):
            continue
        if kategorie in ("Spiel ohne Material", "SpieleWiki:Spiel"):
            continue
        tags.append(kategorie)
    if not material:
        tags.append("ohne Material")
    gesehen, ergebnis = set(), []
    for tag in tags:
        if tag.lower() not in gesehen:
            gesehen.add(tag.lower())
            ergebnis.append(tag)
    return ergebnis


def mache_id(titel):
    """Titel -> stabile ID mit Quellpräfix, z. B. "Acid River" -> sw-acid-river."""
    text = unicodedata.normalize("NFKD", titel.lower())
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(alt, neu)
    text = "".join(z for z in text if not unicodedata.combining(z))
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return "sw-" + (text or "spiel")


def seite_zu_element(titel, seite):
    """Baut aus einer Wikiseite ein Element nach data/SCHEMA.md."""
    wikitext = hole_wikitext(seite)
    infobox, rest = finde_infobox(wikitext)
    beschreibung, tipps, wiki_kategorien = wikitext_zu_text(rest)

    arten = art_vorlagen(infobox.get("Art", ""))
    ort = map_ort(infobox.get("Ort", ""))
    material = map_material(infobox.get("Material", ""), wiki_kategorien)
    kategorie = map_kategorie(arten, ort)
    dauer_min, dauer_max = map_dauer(infobox.get("Dauer", ""))
    gruppe_min, gruppe_max = map_gruppengroesse(infobox.get("AnzahlSpieler", ""), wiki_kategorien)

    element = {
        "id": mache_id(titel),
        "titel": titel,
        "element_typ": "spiel",
        "kategorie": kategorie,
        "slots": map_slots(arten, kategorie, dauer_min),
        "altersstufen": [],  # das Spielewiki hat kein Altersfeld -> gilt für alle Stufen
        "dauer_min": dauer_min,
        "dauer_max": dauer_max,
        "ort": ort,
        "material": material,
        "vorbereitung": map_vorbereitung(infobox.get("Vorbereitung", "")),
        "kurz": nur_text(infobox.get("Meta", "")),
        "beschreibung": beschreibung,
        "tipps": tipps,
        "tags": baue_tags(arten, wiki_kategorien, material),
        "themen": [],
        "quelle": {
            "name": QUELLE["name"],
            "url": SEITEN_URL + urllib.parse.quote(titel.replace(" ", "_")),
            "autor": QUELLE["autor"],
            "lizenz": QUELLE["lizenz"],
        },
    }
    if gruppe_min is not None:
        element["gruppe_min"] = gruppe_min
    if gruppe_max is not None:
        element["gruppe_max"] = gruppe_max
    return element, wiki_kategorien


# --------------------------------------------------------------------------
# Ablauf
# --------------------------------------------------------------------------
def main():
    offline = "--offline" in sys.argv

    if offline:
        if not ROH_SEITEN.exists():
            print("Keine Rohdaten unter {}".format(ROH_SEITEN))
            print("Bitte einmal ohne --offline laufen lassen.")
            return 1
        print("Lese Rohdaten aus {}".format(RAW))
        with open(ROH_SEITEN, encoding="utf-8") as datei:
            seiten = json.load(datei)
    else:
        RAW.mkdir(parents=True, exist_ok=True)
        print("Liste die Kategorie {} ...".format(KATEGORIE))
        mitglieder = hole_kategorie_mitglieder()
        with open(ROH_MITGLIEDER, "w", encoding="utf-8") as datei:
            json.dump(mitglieder, datei, ensure_ascii=False, indent=1)
        titel = [m["title"] for m in mitglieder if m.get("ns") == 0]
        print("Hole den Wikitext von {} Seiten ...".format(len(titel)))
        seiten = hole_wikitexte(titel)
        # Bei Rätselspielen steht die Lösung auf einer Unterseite, die selbst
        # nicht in der Kategorie steht. Ohne sie ist das Spiel nicht spielbar.
        loesungen = [t + "/Lösung" for t in titel]
        print("Hole {} mögliche Lösungsseiten ...".format(len(loesungen)))
        for name, seite in hole_wikitexte(loesungen).items():
            seiten[name] = seite
        print("  davon vorhanden: {}".format(
            sum(1 for name in seiten if name.endswith("/Lösung"))))
        with open(ROH_SEITEN, "w", encoding="utf-8") as datei:
            json.dump(seiten, datei, ensure_ascii=False, indent=1)
        print("  Rohdaten gespeichert: {}".format(RAW))

    # Lösungsseiten sind keine eigenen Spiele – sie gehören an ihr Spiel
    loesungen = {}
    for name in list(seiten):
        if name.endswith("/Lösung"):
            loesungen[name[:-len("/Lösung")]] = seiten.pop(name)

    elemente = []
    ausgeschlossen = []
    ohne_beschreibung = []
    for titel in sorted(seiten):
        element, wiki_kategorien = seite_zu_element(titel, seiten[titel])
        element["beschreibung"] = entferne_loesungsverweis(element["beschreibung"])
        if titel in loesungen:
            loesungstext, _, _ = wikitext_zu_text(hole_wikitext(loesungen[titel]))
            loesungstext = saeubere_loesung(loesungstext)
            if loesungstext:
                # Hat die Hauptseite schon einen Lösungsabschnitt, nicht doppelt betiteln
                trenner = "\n\n" if element["beschreibung"].rstrip().endswith("## Lösung") \
                          else "\n\n## Lösung\n"
                element["beschreibung"] = element["beschreibung"].rstrip() + trenner + loesungstext
        if AUSGESCHLOSSENE_WIKI_KATEGORIEN and (
            set(wiki_kategorien) & AUSGESCHLOSSENE_WIKI_KATEGORIEN
        ):
            ausgeschlossen.append(titel)
            continue
        if len(element["beschreibung"]) < 40:
            ohne_beschreibung.append(titel)
            continue
        elemente.append(element)

    AUSGABE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUSGABE, "w", encoding="utf-8") as datei:
        json.dump(
            {
                "meta": {
                    "quelle": QUELLE["name"],
                    "url": "https://www.spielewiki.org/",
                    "autor": QUELLE["autor"],
                    "lizenz": QUELLE["lizenz"],
                    "lizenz_url": "https://creativecommons.org/licenses/by-sa/4.0/",
                    "hinweis": "Erzeugt von scripts/import_spielewiki.py.",
                    "anzahl": len(elemente),
                },
                "elemente": elemente,
            },
            datei,
            ensure_ascii=False,
            indent=1,
        )

    print()
    print("Seiten gesamt:          {}".format(len(seiten)))
    print("ausgeschlossen ({}): {} {}".format(
        ", ".join(sorted(AUSGESCHLOSSENE_WIKI_KATEGORIEN)) or "-",
        len(ausgeschlossen), ausgeschlossen or ""))
    print("ohne Beschreibung raus: {} {}".format(len(ohne_beschreibung), ohne_beschreibung or ""))
    print("Elemente geschrieben:   {}  ->  {}".format(len(elemente), AUSGABE))
    print()
    print("Kategorien:    {}".format(dict(Counter(e["kategorie"] for e in elemente).most_common())))
    print("Orte:          {}".format(dict(Counter(e["ort"] for e in elemente).most_common())))
    print("Slots:         {}".format(dict(Counter(s for e in elemente for s in e["slots"]).most_common())))
    print("Vorbereitung:  {}".format(dict(Counter(e["vorbereitung"] for e in elemente).most_common())))
    print("ohne Material: {}".format(sum(1 for e in elemente if not e["material"])))
    print("mit Gruppengröße: {}".format(sum(1 for e in elemente if "gruppe_min" in e)))
    print("mit Tipps:     {}".format(sum(1 for e in elemente if e["tipps"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
