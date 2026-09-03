#!/usr/bin/env python3
"""
Führt alle Quellen zur gemeinsamen Datenbasis `data/elemente.json` zusammen.

Aufruf:
    python3 scripts/build.py

Gelesen werden:
    data/eigene/heimabend-ideen.json                    (61 eigene Ideen)
    data/quellen/probenbuch/proben-dpb.json             (30 Proben aus dem DPB-Probenbuch)
    data/quellen/inspirator/inspirator-ideen.json       (211 Ideen, CC BY-NC 4.0)
    data/quellen/pfadfinder-spiele/elemente.json        (Ausgabe von import_pfadfinder_spiele.py)
    data/quellen/spielewiki/elemente.json               (Ausgabe von import_spielewiki.py)

Geschrieben werden:
    data/elemente.json   – alle Elemente nach data/SCHEMA.md, für App und spätere Flutter-App
    web/elemente.js      – dasselbe als `window.ELEMENTE = [...]`, damit die Web-App auch
                           per Doppelklick auf index.html funktioniert (fetch() ist dort gesperrt)

Was passiert:
- Die beiden Rohquellen (eigene, Inspirator) werden nach den Regeln aus data/SCHEMA.md
  auf das Element-Schema gemappt; die beiden Import-Ausgaben sind schon im Schema.
- IDs bekommen ein Quell-Präfix: eig-, insp-, ps-, sw-
- Dubletten werden über normalisierte Titel erkannt und mit `dubletten: [ids]`
  gegenseitig markiert – gelöscht wird nichts (verschiedene Quellen, verschiedene Lizenzen).
- Pflichtfelder und Wertebereiche werden geprüft; Fehler brechen den Lauf ab.
- Zum Schluss gibt es eine Statistik nach Typ, Kategorie, Quelle und Lizenz.

Lizenzhinweis: Jedes Element behält die Lizenz seiner Quelle. Texte verschiedener
Quellen werden nie vermischt (siehe CLAUDE.md).
"""
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
EIGENE = WURZEL / "data" / "eigene" / "heimabend-ideen.json"
PROBENBUCH = WURZEL / "data" / "quellen" / "probenbuch" / "proben-dpb.json"
INSPIRATOR = WURZEL / "data" / "quellen" / "inspirator" / "inspirator-ideen.json"
PFADFINDER_SPIELE = WURZEL / "data" / "quellen" / "pfadfinder-spiele" / "elemente.json"
SPIELEWIKI = WURZEL / "data" / "quellen" / "spielewiki" / "elemente.json"
REDAKTION = WURZEL / "data" / "redaktion.json"
AUSGABE_JSON = WURZEL / "data" / "elemente.json"
AUSGABE_JS = WURZEL / "web" / "elemente.js"

# ---------------------------------------------------------------- Wertebereiche
UMFAENGE = {"baustein", "ganzer_abend"}
ORTE = {"drinnen", "draussen", "beides"}
VORBEREITUNGEN = {"gering", "mittel", "hoch"}
SLOTS = {"eroeffnung", "einstieg", "hauptteil", "abschluss"}
ALTERSSTUFEN = {"Wölflinge", "Pfadfinder", "Ältere"}

KATEGORIEN_SPIEL = {
    "ankommen", "bewegung_drinnen", "bewegung_draussen", "gelaende",
    "kreis", "ruhig", "kooperation", "abschluss",
}
KATEGORIEN_PROBE = {
    "knoten", "karte_kompass", "feuer", "erste_hilfe", "zelte_bauten",
    "natur", "bundeskunde", "fahrtentechnik", "sonstiges",
}
# Nur "spiel" und "pfadfindertechnik" haben eine zweite Ebene. Bei den übrigen
# Bereichen ist der Bereich selbst schon das Thema; dort bleibt die Kategorie
# leer, und die Navigation geht über den Umfang weiter.
KATEGORIEN = {
    "spiel": KATEGORIEN_SPIEL,
    "pfadfindertechnik": KATEGORIEN_PROBE,
    "natur_draussen": {""},
    "werken": {""},
    "kochen": {""},
    "musisch": {""},
    "gemeinschaft": {""},
}
PFLICHTFELDER = [
    "id", "titel", "bereich", "umfang", "kategorie", "unterkategorie", "slots", "altersstufen",
    "wirkung", "modus", "sozialform", "spielgeraet", "anforderung",
    "dauer_min", "dauer_max", "ort", "material", "vorbereitung",
    "kurz", "beschreibung", "tags", "themen", "quelle",
]


# ---------------------------------------------------------------- Hilfsmittel
def entschaerfe(text):
    """Kleinbuchstaben ohne Umlaute/Akzente – Grundlage für ID und Dublettensuche."""
    text = (text or "").lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(alt, neu)
    text = unicodedata.normalize("NFKD", text)
    return "".join(z for z in text if not unicodedata.combining(z))


def mache_id(praefix, titel, vergeben):
    """Baut eine eindeutige ID mit Quell-Präfix, z. B. eig-knoten-olympiade."""
    kern = re.sub(r"[^a-z0-9]+", "-", entschaerfe(titel)).strip("-") or "element"
    kandidat = "{}-{}".format(praefix, kern)
    nummer = 2
    while kandidat in vergeben:
        kandidat = "{}-{}-{}".format(praefix, kern, nummer)
        nummer += 1
    vergeben.add(kandidat)
    return kandidat


def dubletten_schluessel(titel):
    """Vergleichsform für die Dublettensuche: nur Buchstaben und Ziffern."""
    return re.sub(r"[^a-z0-9]+", "", entschaerfe(titel))


def kurzfassung(text, laenge=220):
    """Erzeugt einen Kurztext aus den ersten Sätzen einer Beschreibung."""
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= laenge:
        return text
    schnitt = text[:laenge]
    punkt = max(schnitt.rfind(". "), schnitt.rfind("! "), schnitt.rfind("? "))
    if punkt > 60:
        return schnitt[:punkt + 1]
    return schnitt.rsplit(" ", 1)[0] + " …"


def normalisiere_ort(wert):
    """"draußen"/"Draussen" -> "draussen"."""
    wert = entschaerfe(wert).strip()
    if wert.startswith("drau"):
        return "draussen"
    if wert.startswith("drin"):
        return "drinnen"
    return "beides"


def normalisiere_stufen(stufen):
    """Stufennamen vereinheitlichen; der Inspirator nennt die Älteren "Rover"."""
    ergebnis = []
    for stufe in stufen or []:
        stufe = stufe.strip()
        if stufe.lower() in ("rover", "ältere", "aeltere", "ranger", "ranger/rover"):
            stufe = "Ältere"
        elif stufe.lower().startswith("wölf") or stufe.lower().startswith("woelf"):
            stufe = "Wölflinge"
        elif stufe.lower().startswith("pfadfinder") or stufe.lower().startswith("jungpfad"):
            stufe = "Pfadfinder"
        if stufe in ALTERSSTUFEN and stufe not in ergebnis:
            ergebnis.append(stufe)
    reihenfolge = ["Wölflinge", "Pfadfinder", "Ältere"]
    return sorted(ergebnis, key=reihenfolge.index)


# ---------------------------------------------------------------- eigene Ideen
# Zweite Ebene innerhalb eines Bereichs, soweit vorhanden
EIGENE_AKTIVITAET = {
    "Draußen & Natur": "draussen",
    "Kreativ & Werken": "kreativ",
    "Kochen & Essen": "kochen",
    "Musisch": "musisch",
    "Gruppe & Soziales": "soziales",
    "Denken & Rätsel": "soziales",
}
# ... und -> Kategorie für element_typ "projekt"
EIGENE_PROJEKT = {
    "Themenabende": "themenabend",
    "Draußen & Natur": "draussen",
    "Kreativ & Werken": "kreativ",
    "Kochen & Essen": "kochen",
    "Musisch": "musisch",
    "Gruppe & Soziales": "soziales",
    "Denken & Rätsel": "raetsel",
    "Spiel & Action": "spiel",
    "Pfadfindertechnik": "wissen",
}
# Stichwort im Titel/Tag -> Probenthema (erste Übereinstimmung gewinnt)
PROBEN_THEMEN = [
    ("knoten", "knoten"),
    ("bund", "zelte_bauten"),
    ("seilbrücke", "zelte_bauten"),
    ("kohte", "zelte_bauten"),
    ("jurte", "zelte_bauten"),
    ("zelt", "zelte_bauten"),
    ("erste hilfe", "erste_hilfe"),
    ("feuer", "feuer"),
    ("karte", "karte_kompass"),
    ("kompass", "karte_kompass"),
    ("orientierung", "karte_kompass"),
    ("waldläuferzeichen", "karte_kompass"),
    ("spuren", "natur"),
    ("natur", "natur"),
    ("baum", "natur"),
    ("stern", "natur"),
    ("bipi", "bundeskunde"),
    ("geschichte", "bundeskunde"),
    ("symbolik", "bundeskunde"),
    ("versprechen", "bundeskunde"),
    ("lied", "bundeskunde"),
    ("schnitz", "fahrtentechnik"),
    ("messer", "fahrtentechnik"),
    ("werkzeug", "fahrtentechnik"),
    ("packen", "fahrtentechnik"),
    ("kochen", "fahrtentechnik"),
    ("haik", "fahrtentechnik"),
    ("morse", "sonstiges"),
    ("geheimschrift", "sonstiges"),
]
# Stichwort -> Kategorie, wenn eine eigene Idee ein "spiel" wird
EIGENE_SPIEL_KATEGORIE = [
    ("warm-up", "ankommen"),
    ("kennenlern", "ankommen"),
    ("geländespiel", "gelaende"),
    ("postenlauf", "gelaende"),
    ("stationen", "gelaende"),
    ("kooperation", "kooperation"),
    ("vertrauen", "kooperation"),
    ("rätsel", "ruhig"),
    ("kim-spiel", "ruhig"),
    ("ruhig", "ruhig"),
    ("quiz", "ruhig"),
]


def probenthema(idee):
    """Bestimmt das Probenthema aus Titel und Tags."""
    heuhaufen = entschaerfe(idee["titel"] + " " + " ".join(idee.get("tags", [])))
    for stichwort, thema in PROBEN_THEMEN:
        if entschaerfe(stichwort) in heuhaufen:
            return thema
    return "sonstiges"


def eigene_spielkategorie(idee, ort):
    """Bestimmt die Spielkategorie einer eigenen Idee."""
    heuhaufen = entschaerfe(idee["titel"] + " " + " ".join(idee.get("tags", [])))
    for stichwort, kategorie in EIGENE_SPIEL_KATEGORIE:
        if entschaerfe(stichwort) in heuhaufen:
            return kategorie
    return "bewegung_draussen" if ort == "draussen" else "bewegung_drinnen"


def ist_spielhaft(idee):
    """
    True, wenn eine eigene Idee im Kern ein Spiel ist. Neben den Kategorien
    "Spiel & Action" und "Denken & Rätsel" zählt auch der Tag "Geländespiel"
    dazu – sonst landet z. B. "Fahnenraub im Wald" unter Bastel-Aktivitäten.
    """
    if idee.get("kategorie") in ("Spiel & Action", "Denken & Rätsel"):
        return True
    return any(entschaerfe(t) == "gelaendespiel" for t in idee.get("tags", []))


def eigener_typ(idee):
    """
    Bestimmt den element_typ nach der Mapping-Tabelle in data/SCHEMA.md.

    Reihenfolge (bewusst so gewählt, siehe Commit-Nachricht):
    1. Pfadfindertechnik ist immer eine Probe – auch wenn sie 90 Minuten dauert,
       sonst landet Probenbuch-Wissen unter "Projekt".
    2. Themenabende sind Projekte.
    3. Spielhaftes bis 45 (bzw. höchstens 60) Minuten ist ein Spiel; das Schema
       sieht für "spiel" 5-45 Minuten vor. Längere Spiele füllen den Abend
       und werden deshalb zum Projekt.
    4. Alles Übrige ab 90 Minuten füllt ebenfalls den Abend -> Projekt.
    5. Der Rest ist eine Gemeinschaftsaktivität (laut Schema 30-90 Minuten).
    """
    kategorie = idee.get("kategorie", "")
    dauer_min = idee.get("dauer_min") or 0
    dauer_max = idee.get("dauer_max") or dauer_min
    if kategorie == "Pfadfindertechnik":
        return "probe"
    if kategorie == "Themenabende":
        return "projekt"
    if ist_spielhaft(idee):
        return "spiel" if dauer_min <= 45 and dauer_max <= 60 else "projekt"
    if dauer_min >= 90:
        return "projekt"
    return "aktivitaet"


def slots_fuer(bereich, umfang, kategorie, dauer_min):
    """Wo im Heimabend passt das Element?"""
    if umfang == "ganzer_abend":
        return ["hauptteil"]          # füllt den Abend, kein Einstieg, kein Ausklang
    if bereich != "spiel":
        return ["hauptteil"]
    slots = []
    if kategorie == "ankommen" or dauer_min <= 10:
        slots.append("einstieg")
    slots.append("hauptteil")
    if dauer_min <= 15 and kategorie in ("kreis", "ruhig", "ankommen"):
        slots.append("abschluss")
    return slots


def lade_eigene(vergeben):
    """Mappt data/eigene/heimabend-ideen.json auf das Element-Schema."""
    with open(EIGENE, encoding="utf-8") as datei:
        daten = json.load(datei)
    lizenz = "CC BY-SA 4.0"
    elemente = []
    for idee in daten["ideen"]:
        ort = normalisiere_ort(idee.get("ort", "beides"))
        beschreibung = (idee.get("beschreibung") or "").strip()
        dauer_min = idee.get("dauer_min") or 30
        dauer_max = idee.get("dauer_max") or dauer_min
        # Die neun eigenen Kategorien lassen sich direkt einem Bereich zuordnen;
        # nur "Themenabende" ist inhaltlich gemischt und läuft über die Stichworte.
        bereich = EIGENE_BEREICH.get(idee["kategorie"])
        umfang = "ganzer_abend" if (dauer_min >= 75 or dauer_max >= 120) else "baustein"
        if bereich == "spiel":
            kategorie = eigene_spielkategorie(idee, ort)
        elif bereich == "pfadfindertechnik":
            kategorie = probenthema(idee)
        else:
            kategorie = ""
        elemente.append({
            "id": mache_id("eig", idee["titel"], vergeben),
            "titel": idee["titel"],
            "_bereich": bereich,
            "umfang": umfang,
            "kategorie": kategorie,
            "slots": slots_fuer(bereich or "gemeinschaft", umfang, kategorie, dauer_min),
            "altersstufen": normalisiere_stufen(idee.get("altersstufen")),
            "dauer_min": dauer_min,
            "dauer_max": dauer_max,
            "ort": ort,
            "material": [m for m in idee.get("material", []) if m],
            "vorbereitung": idee.get("vorbereitung", "gering"),
            "kurz": kurzfassung(beschreibung),
            "beschreibung": beschreibung,
            "tipps": (idee.get("tipps") or "").strip(),
            "tags": list(idee.get("tags", [])),
            "themen": list(idee.get("tags", [])),
            "quelle": {
                "name": "Heimabend-Baukasten (eigene Sammlung)",
                "url": "",
                "autor": "Heimabend-Baukasten",
                "lizenz": lizenz,
            },
        })
    return elemente


# ---------------------------------------------------------------- Probenbuch
# Rechte am Probenbuch liegen beim Projektinhaber (Auskunft 02.09.2026).
# Diese Angaben stehen bei jedem Element in der App.
PROBENBUCH_QUELLE = {
    "name": "DPB-Probenbuch (3. Auflage)",
    "url": "",
    "autor": "Deutscher Pfadfinderbund",
    "lizenz": "DPB-Probenbuch – Nutzung mit Erlaubnis des Rechteinhabers",
}

# Zuordnung jeder Probe: Nummer -> (element_typ, kategorie, ort, Material)
# Bewusst als vollständige Tabelle, damit sie nachprüfbar und leicht zu korrigieren ist.
# Die Nummern 1 und 2 (Liednoten) fehlen absichtlich – sie haben keinen Text.
PROBENBUCH_ZUORDNUNG = {
    3:  ("probe", "karte_kompass", "draussen", []),
    4:  ("probe", "bundeskunde", "drinnen", []),
    5:  ("probe", "bundeskunde", "drinnen", []),
    6:  ("probe", "bundeskunde", "drinnen", ["Kluft"]),
    7:  ("probe", "bundeskunde", "drinnen", []),
    8:  ("probe", "bundeskunde", "beides", []),
    9:  ("probe", "bundeskunde", "beides", []),
    10: ("probe", "fahrtentechnik", "drinnen", ["Fahrtenrucksack", "Fahrtengepäck"]),
    11: ("probe", "knoten", "beides", ["Seile/Reepschnüre"]),
    12: ("probe", "zelte_bauten", "draussen", ["Kohte oder Jurte", "Zeltstangen", "Heringe", "Seile"]),
    13: ("probe", "feuer", "draussen", ["Feuerholz", "Streichhölzer", "Löschwasser"]),
    14: ("probe", "zelte_bauten", "draussen", ["Seile", "Stangen"]),
    15: ("probe", "fahrtentechnik", "beides", ["Kochgeschirr", "Zutaten"]),
    16: ("probe", "fahrtentechnik", "drinnen", ["Nadel und Faden", "Werkzeug"]),
    17: ("probe", "sonstiges", "draussen", []),
    18: ("probe", "bundeskunde", "drinnen", []),
    19: ("probe", "karte_kompass", "draussen", ["Karte", "Kompass"]),
    20: ("probe", "karte_kompass", "beides", ["Kompass"]),
    21: ("probe", "karte_kompass", "beides", ["Karte"]),
    22: ("probe", "karte_kompass", "draussen", ["Karte", "Kompass"]),
    23: ("probe", "natur", "draussen", []),
    24: ("probe", "natur", "draussen", []),
    25: ("probe", "erste_hilfe", "beides", ["Verbandsmaterial"]),
    26: ("probe", "erste_hilfe", "beides", ["Verbandsmaterial", "Dreiecktücher"]),
    # Die drei Geschichts-Kapitel füllen einen ganzen Abend (umfang), gehören
    # aber inhaltlich zur Bundeskunde.
    27: ("projekt", "bundeskunde", "drinnen", []),
    28: ("projekt", "bundeskunde", "drinnen", []),
    29: ("projekt", "bundeskunde", "drinnen", []),
    30: ("probe", "bundeskunde", "drinnen", []),
}
# Proben, bei denen die Zeichnungen aus dem gedruckten Buch fehlen und deshalb
# gebraucht werden (die JSON-Extraktion enthält nur den Text).
PROBENBUCH_BRAUCHT_BILDER = {3, 11, 12, 13, 19, 20, 21, 22, 23, 24, 26}


def probenbuch_absaetze(text):
    """
    Fügt den harten Zeilenumbruch der PDF-Extraktion wieder zu Absätzen zusammen.
    Leerzeilen trennen Absätze, Zeilen mit "- " bleiben eigene Aufzählungspunkte.
    """
    absaetze = []
    for absatz in re.split(r"\n\s*\n", text or ""):
        teile = []
        for zeile in (z.strip() for z in absatz.split("\n")):
            if not zeile:
                continue
            if re.match(r"^[-–•*]\s+", zeile):
                teile.append("- " + re.sub(r"^[-–•*]\s+", "", zeile))
            elif teile:
                teile[-1] += " " + zeile
            else:
                teile.append(zeile)
        if teile:
            absaetze.append("\n".join(teile))
    return "\n\n".join(absaetze)


def lade_probenbuch(vergeben):
    """Mappt data/quellen/probenbuch/proben-dpb.json auf das Element-Schema."""
    if not PROBENBUCH.exists():
        print("  ACHTUNG: {} fehlt – Proben werden übersprungen.".format(PROBENBUCH))
        return []
    with open(PROBENBUCH, encoding="utf-8") as datei:
        daten = json.load(datei)

    # Die Warnungen aus meta.achtung_veraltet den betroffenen Proben zuordnen,
    # damit niemand versehentlich Erste Hilfe von 2003 vermittelt.
    warnungen = {}
    for warnung in daten.get("meta", {}).get("achtung_veraltet", []):
        for nummer in re.findall(r"\d+", warnung.split(":")[0]):
            warnungen.setdefault(int(nummer), []).append(warnung.strip())

    elemente, ohne_text, ohne_zuordnung = [], [], []
    for probe in daten.get("proben", []):
        nummer = probe.get("nummer")
        beschreibung = probenbuch_absaetze(probe.get("text_roh"))
        if len(beschreibung) < 40:
            ohne_text.append("{} {}".format(nummer, probe.get("titel")))
            continue
        if nummer not in PROBENBUCH_ZUORDNUNG:
            ohne_zuordnung.append("{} {}".format(nummer, probe.get("titel")))
            continue
        typ, kategorie, ort, material = PROBENBUCH_ZUORDNUNG[nummer]

        hinweise = list(warnungen.get(nummer, []))
        if probe.get("hinweis"):
            hinweise.append(probe["hinweis"].strip())
        if nummer in PROBENBUCH_BRAUCHT_BILDER:
            hinweise.append("Die Zeichnungen aus dem gedruckten Probenbuch fehlen in "
                            "dieser Textfassung – für den Heimabend mitbringen.")

        if typ == "projekt":
            dauer_min, dauer_max = 90, 120
            altersstufen = ["Pfadfinder", "Ältere"]
        else:
            dauer_min, dauer_max = 30, 60
            altersstufen = []  # gilt für alle Stufen
        umfang = "ganzer_abend" if dauer_min >= 75 else "baustein"

        elemente.append({
            "id": mache_id("pb", probe["titel"], vergeben),
            "titel": probe["titel"],
            "_bereich": "pfadfindertechnik",   # das ganze Probenbuch ist Pfadfinderwissen
            "umfang": umfang,
            "kategorie": kategorie,
            "slots": slots_fuer("pfadfindertechnik", umfang, kategorie, dauer_min),
            "altersstufen": altersstufen,
            "dauer_min": dauer_min,
            "dauer_max": dauer_max,
            "ort": ort,
            "material": list(material),
            "vorbereitung": "mittel",  # eine Probe will vorbereitet sein
            "kurz": kurzfassung(beschreibung),
            "beschreibung": beschreibung,
            "tipps": "\n\n".join(hinweise),
            "tags": ["Probenbuch", "Pfadfinderwissen", "Probe {}".format(nummer)],
            "themen": [probe["titel"]],
            "quelle": dict(PROBENBUCH_QUELLE),
        })
    if ohne_text:
        print("    ohne Text übersprungen: {}".format(", ".join(ohne_text)))
    if ohne_zuordnung:
        print("    ohne Zuordnung in PROBENBUCH_ZUORDNUNG: {}".format(", ".join(ohne_zuordnung)))
    return elemente


# ---------------------------------------------------------------- Inspirator
# arten des Inspirators -> Kategorie für element_typ "projekt"
INSPIRATOR_PROJEKT = [
    ("Rezept", "kochen"),
    ("Kreatives", "kreativ"),
    ("Forschen", "entdecken"),
    ("Lernen", "wissen"),
    ("Spiel", "spiel"),
]
INSPIRATOR_VORBEREITUNG = {
    "keine": "gering", "5 min": "gering",
    "30 min": "mittel",
    "60 min": "hoch", ">60 min": "hoch",
}


def inspirator_ort(orte):
    """orte[] (Drinnen, Draußen, Wald, Garten, Ausflug) -> ort."""
    drinnen = "Drinnen" in (orte or [])
    draussen = bool(set(orte or []) & {"Draußen", "Wald", "Garten", "Ausflug"})
    if drinnen and draussen:
        return "beides"
    if draussen:
        return "draussen"
    if drinnen:
        return "drinnen"
    return "beides"


def lade_inspirator(vergeben):
    """Mappt data/quellen/inspirator/inspirator-ideen.json auf das Element-Schema."""
    with open(INSPIRATOR, encoding="utf-8") as datei:
        daten = json.load(datei)
    elemente = []
    for idee in daten["ideen"]:
        arten = idee.get("arten") or []
        dauer_min = idee.get("dauer_min") or 45
        dauer_max = idee.get("dauer_max") or dauer_min
        ort = inspirator_ort(idee.get("orte"))
        umfang = "ganzer_abend" if (dauer_min >= 75 or dauer_max >= 120) else "baustein"
        # Reine Spiele bleiben Spiele; alles andere bekommt seinen Bereich
        # später aus der Themen-Abstimmung (bestimme_bereich).
        if arten == ["Spiel"]:
            bereich = "spiel"
            kategorie = "bewegung_draussen" if ort == "draussen" else "bewegung_drinnen"
        else:
            bereich = None
            kategorie = ""
        material = []
        for eintrag in idee.get("material") or []:
            name = (eintrag.get("name") or "").strip() if isinstance(eintrag, dict) else str(eintrag)
            if name and name not in material:
                material.append(name)
        beschreibung = (idee.get("beschreibung_text") or "").strip()
        elemente.append({
            "id": mache_id("insp", idee["titel"], vergeben),
            "titel": idee["titel"],
            "_bereich": bereich,
            "umfang": umfang,
            "kategorie": kategorie,
            "slots": slots_fuer(bereich or "gemeinschaft", umfang, kategorie, dauer_min),
            "altersstufen": normalisiere_stufen(idee.get("stufen")),
            "dauer_min": dauer_min,
            "dauer_max": dauer_max,
            "ort": ort,
            "material": material,
            "vorbereitung": INSPIRATOR_VORBEREITUNG.get(idee.get("vorbereitung"), "gering"),
            "kurz": kurzfassung(idee.get("kurz") or beschreibung),
            "beschreibung": beschreibung,
            "tipps": "",
            "tags": list(idee.get("themen") or []) + list(arten),
            "themen": list(idee.get("themen") or []),
            "quelle": {
                "name": "Heimabend-Inspirator (DPBM)",
                "url": idee.get("url", ""),
                # Bewusst ohne die Vornamen der Autor*innen: CLAUDE.md untersagt
                # personenbezogene Daten. Die Namensnennung erfolgt über Quelle + URL.
                "autor": "Heimabend-Inspirator (DPBM)",
                "lizenz": "CC BY-NC 4.0",
            },
        })
    return elemente


# ---------------------------------------------------------------- Importe
def lade_import(pfad):
    """Liest eine fertige Import-Ausgabe (schon im Element-Schema)."""
    if not pfad.exists():
        print("  ACHTUNG: {} fehlt – bitte das zugehörige Import-Skript laufen lassen.".format(pfad))
        return []
    with open(pfad, encoding="utf-8") as datei:
        return json.load(datei)["elemente"]


# ------------------------------------------------------------ Redaktion
def lade_redaktion():
    """Liest data/redaktion.json; fehlt die Datei, wird nichts gefiltert."""
    if not REDAKTION.exists():
        print("  Hinweis: {} fehlt – keine redaktionellen Regeln.".format(REDAKTION))
        return {}
    with open(REDAKTION, encoding="utf-8") as datei:
        return json.load(datei)


def wende_redaktion_an(elemente, redaktion):
    """
    Sperrt, benennt um und korrigiert Felder.

    Nötig, weil die Import-Skripte idempotent sind: ohne diesen Schritt holt
    der nächste Lauf zum Beispiel das Bleigießen wieder herein.
    Gibt (elemente, bericht) zurück.
    """
    bericht = {"gesperrt": [], "umbenannt": [], "korrigiert": [], "unbekannt": []}
    nach_id = {e["id"]: e for e in elemente}

    gesperrt = set()
    for eintrag in redaktion.get("gesperrt", []):
        if eintrag["id"] in nach_id:
            gesperrt.add(eintrag["id"])
            bericht["gesperrt"].append("{} ({})".format(nach_id[eintrag["id"]]["titel"], eintrag["id"]))
        else:
            bericht["unbekannt"].append(eintrag["id"])

    for eintrag in redaktion.get("umbenannt", []):
        element = nach_id.get(eintrag["id"])
        if not element:
            bericht["unbekannt"].append(eintrag["id"])
            continue
        bericht["umbenannt"].append("{} -> {}".format(element["titel"], eintrag["titel"]))
        element["titel"] = eintrag["titel"]
        element["titel_geaendert"] = True

    # Bereich, Umfang und Kategorie werden erst nach der Automatik gesetzt -
    # sonst überschreibt die Automatik die redaktionelle Entscheidung wieder.
    bericht["nachtraeglich"] = {}
    for eintrag in redaktion.get("bereiche", []):
        if eintrag["id"] in nach_id:
            bericht["nachtraeglich"][eintrag["id"]] = eintrag
        else:
            bericht["unbekannt"].append(eintrag["id"])
    bericht["achsen"] = {}
    for eintrag in redaktion.get("achsen", []):
        if eintrag["id"] in nach_id:
            bericht["achsen"][eintrag["id"]] = eintrag.get("felder") or {}
        else:
            bericht["unbekannt"].append(eintrag["id"])

    for eintrag in redaktion.get("korrekturen", []):
        element = nach_id.get(eintrag["id"])
        if not element:
            bericht["unbekannt"].append(eintrag["id"])
            continue
        if eintrag.get("titel"):
            bericht["umbenannt"].append("{} -> {}".format(element["titel"], eintrag["titel"]))
            element["titel"] = eintrag["titel"]
            element["titel_geaendert"] = True
        for feld, wert in (eintrag.get("felder") or {}).items():
            element[feld] = wert
        if eintrag.get("hinweis"):
            # Der Hinweis steht vorn, damit er in der App zuerst gelesen wird.
            element["tipps"] = (eintrag["hinweis"] + "\n\n" + (element.get("tipps") or "")).strip()
        bericht["korrigiert"].append("{} ({})".format(element["titel"], eintrag["id"]))

    elemente = [e for e in elemente if e["id"] not in gesperrt]
    return elemente, bericht


# ------------------------------------------------------------- Bereiche
# Die alte Einteilung mischte zwei Fragen: WAS ist es (Spiel, Wissen, etwas
# herstellen) und WIE GROSS ist es (ein Baustein oder ein ganzer Abend).
# Dadurch lagen "Armbänder knüpfen" (60-90 min) und "Speckstein-Werkstatt"
# (90-120 min) in verschiedenen Arten, obwohl beides Basteln ist.
#
# Jetzt sind es zwei Achsen:
#   bereich  – worum geht es (sieben Werte, siehe unten)
#   umfang   – baustein (passt in einen Slot) oder ganzer_abend
#
# Die Bereiche folgen der eigenen Sammlung des Projekts und decken sich mit
# der Gliederung der Pfaditechnik, wie sie im Pfadfinderwesen üblich ist
# (Pioniertechnik, Orientierung, Natur, Sicherheit, Bundeskunde, unterwegs sein).
BEREICHE = [
    "spiel", "pfadfindertechnik", "natur_draussen", "werken",
    "kochen", "musisch", "gemeinschaft",
]
# Bei Gleichstand entscheidet diese Rangfolge: das Speziellere gewinnt.
BEREICH_RANG = ["pfadfindertechnik", "kochen", "werken", "musisch",
                "natur_draussen", "gemeinschaft", "spiel"]

# Das Themen-Vokabular des Inspirators ist geschlossen (30 Werte), deshalb
# eine exakte Tabelle statt Stichwortsuche. Themen ohne Eintrag ("Bewegung",
# "Kim-Spiel", "Detektiv") beschreiben die Spielform, nicht den Bereich,
# und stimmen deshalb nicht mit ab.
THEMA_BEREICH = {
    "Basteln": "werken", "Handwerkliches": "werken", "Schnitzen": "werken",
    "Küche": "kochen", "Backen": "kochen",
    "Haik": "pfadfindertechnik", "Karte Kompass": "pfadfindertechnik",
    "Knoten": "pfadfindertechnik", "Feuer machen": "pfadfindertechnik",
    "Schwarzzelte": "pfadfindertechnik", "Symbolik": "pfadfindertechnik",
    "Unser Bund": "pfadfindertechnik", "Versprechen": "pfadfindertechnik",
    "Pfa. Geschichte": "pfadfindertechnik", "1. Hilfe": "pfadfindertechnik",
    "Pflanzen": "natur_draussen", "Baum": "natur_draussen", "Tier": "natur_draussen",
    "Wasser": "natur_draussen", "Sternenkunde": "natur_draussen",
    "Nachhaltigkeit": "natur_draussen", "Unsere Erde": "natur_draussen",
    "Geschichten": "musisch", "Musisches": "musisch",
    "Gesellschaftliches": "gemeinschaft", "Unsere Sippe": "gemeinschaft",
    "Prävention": "gemeinschaft",
}
# Die neun Kategorien der eigenen Sammlung lassen sich direkt zuordnen.
EIGENE_BEREICH = {
    "Pfadfindertechnik": "pfadfindertechnik",
    "Draußen & Natur": "natur_draussen",
    "Kreativ & Werken": "werken",
    "Kochen & Essen": "kochen",
    "Musisch": "musisch",
    "Gruppe & Soziales": "gemeinschaft",
    "Spiel & Action": "spiel",
    "Denken & Rätsel": "spiel",
    "Themenabende": None,          # inhaltlich verschieden, siehe Stichworte
}
# Nur noch Rückfallebene für die wenigen Elemente ohne verwertbares Thema.
BEREICH_STICHWORTE = [
    ("pfadfindertechnik", ["knoten", "kompass", "karte", "orientier", "feuer",
                           "zelt", "kohte", "jurte", "lager", "erste hilfe",
                           "biwak", "haik", "fahrt", "morse", "waldläuferzeichen",
                           "bipi", "bund", "versprechen", "kluft", "lilie",
                           "probenbuch", "pfadfinderwissen", "wimpel"]),
    ("kochen", ["küche", "kochen", "backen", "rezept", "brot", "kuchen",
                "grillen", "mahlzeit", "stockbrot"]),
    ("werken", ["basteln", "werken", "schnitzen", "nähen", "knüpfen", "malen",
                "gestalten", "upcycling", "speckstein", "holz", "foto"]),
    ("musisch", ["lied", "singen", "musik", "gitarre", "theater", "impro",
                 "sketch", "dichten", "geschichten", "erzählen"]),
    ("natur_draussen", ["natur", "baum", "pflanze", "tier", "wald", "spuren",
                        "stern", "umwelt", "nachhaltig", "müll", "wandern",
                        "mikroabenteuer"]),
    ("gemeinschaft", ["sippe", "gruppe", "gemeinschaft", "reflexion", "gespräch",
                      "diskussion", "beteiligung", "regeln", "gute tat",
                      "zukunft", "beruf", "länder", "kultur", "rückblick"]),
]


def bestimme_bereich(element):
    """
    Ermittelt den Bereich. Exakte Tabellen zuerst, Stichworte nur als Rückfall.
    Der Quellschlüssel steht in "_bereich_quelle", falls das Element schon
    beim Einlesen zugeordnet werden konnte.
    """
    if element.get("_bereich"):
        return element["_bereich"]
    # Die Import-Ausgaben von Spielewiki und pfadfinder-spiele.de enthalten
    # ausschließlich Spiele und liefern das noch im alten Feld element_typ.
    if element.get("element_typ") == "spiel":
        return "spiel"

    # Abstimmung über die Themen (geschlossenes Vokabular)
    stimmen = Counter()
    for thema in element.get("themen") or []:
        ziel = THEMA_BEREICH.get(thema)
        if ziel:
            stimmen[ziel] += 1
    if stimmen:
        hoechste = max(stimmen.values())
        gleichauf = [b for b, n in stimmen.items() if n == hoechste]
        return sorted(gleichauf, key=BEREICH_RANG.index)[0]

    heu = " " + " ".join(
        [element["titel"]] + (element.get("tags") or []) + (element.get("themen") or [])
    ).lower() + " "
    for name, woerter in BEREICH_STICHWORTE:
        for wort in woerter:
            if wort in heu:
                return name
    return "gemeinschaft"


# Themen des Inspirators -> Probenthema, für die zweite Ebene der Pfadfindertechnik
THEMA_TECHNIK = {
    "Knoten": "knoten", "Karte Kompass": "karte_kompass", "Feuer machen": "feuer",
    "1. Hilfe": "erste_hilfe", "Schwarzzelte": "zelte_bauten", "Haik": "fahrtentechnik",
    "Symbolik": "bundeskunde", "Unser Bund": "bundeskunde",
    "Versprechen": "bundeskunde", "Pfa. Geschichte": "bundeskunde",
    "Pflanzen": "natur", "Baum": "natur", "Tier": "natur", "Sternenkunde": "natur",
}


def technik_kategorie(element):
    """Zweite Ebene innerhalb der Pfadfindertechnik (Knoten, Karte & Kompass, ...)."""
    for thema in element.get("themen") or []:
        if thema in THEMA_TECHNIK:
            return THEMA_TECHNIK[thema]
    heuhaufen = entschaerfe(
        element["titel"] + " " + " ".join(element.get("tags") or [])
    )
    for stichwort, thema in PROBEN_THEMEN:
        if entschaerfe(stichwort) in heuhaufen:
            return thema
    return "sonstiges"


def bestimme_umfang(element):
    """Passt es in einen Slot des Abends oder füllt es den Abend?"""
    if element["dauer_min"] >= 75 or element["dauer_max"] >= 120:
        return "ganzer_abend"
    return "baustein"


# ------------------------------------------------------------ Spiel-Achsen
# Die Spiel-Kategorie (ankommen, kreis, ruhig, kooperation, bewegung_*) mischt
# vier Fragen in einem Feld - deshalb ist sie nicht trennscharf. Sie bleibt als
# Navigation erhalten; daneben bekommt jedes Spiel fünf eigenständige Achsen,
# jede beantwortet genau eine Frage:
#   wirkung      wozu setze ich es ein?          (mehrere Werte)
#   modus        gegeneinander oder miteinander?  (ein Wert)
#   sozialform   wie ist die Gruppe aufgestellt?  (ein Wert)
#   spielgeraet  was brauche ich in der Hand?     (mehrere Werte, aus Material)
#   anforderung  was fordert es von den Kindern?  (mehrere Werte)
# Alles wird aus Tags, Material und Text abgeleitet; Grenzfälle korrigiert
# data/redaktion.json ("achsen").

WIRKUNGEN = ["ankommen", "kennenlernen", "austoben", "beruhigen", "konzentration",
             "vertrauen", "zusammenarbeit", "abschluss"]
MODI = ["wettkampf", "kooperation", "ohne_gewinner"]
SOZIALFORMEN = ["kreis", "paare", "mannschaften", "einer_gegen_alle", "kleingruppen", "frei"]
SPIELGERAETE = ["ball", "seil", "tuch", "stuehle", "papier_stift", "karten_wuerfel",
                "musik", "nichts", "sonstiges"]
ANFORDERUNGEN = ["bewegung", "geschick", "denken", "merken", "konzentration",
                 "sprache", "rhythmus"]

# Reihenfolge: zuerst Tags (verlässlich), dann der Text (Wortanfänge, \b)
WIRKUNG_TAGS = {
    "Warm up": "ankommen", "Warm-up": "ankommen", "warmup": "ankommen",
    "Kennenlernspiel": "kennenlernen", "Namenslernspiel": "kennenlernen",
    "Vertrauensspiel": "vertrauen", "Vertrauensübung": "vertrauen",
    "Kooperationsspiel": "zusammenarbeit", "Gruppendynamisches Spiel": "zusammenarbeit",
    "Kommunikationsspiel": "zusammenarbeit", "Konzentrationsspiel": "konzentration",
    "Reflexionsmethode": "abschluss", "ruhiges Spiel": "beruhigen", "Ruhiges Spiel": "beruhigen",
    "Fangspiel": "austoben", "Renn- & Fangenspiel": "austoben", "Laufspiel": "austoben",
    "Bewegungsspiel": "austoben", "Kampfspiel": "austoben",
}
WIRKUNG_TEXT = [
    ("kennenlernen", [r"\bkennenlern", r"\bnamen (lernen|merken|nennen)", r"\bnamensspiel"]),
    ("vertrauen", [r"\bvertrauen", r"\bblind (geführt|führen)", r"\baugen verbunden"]),
    ("zusammenarbeit", [r"\bkooperat", r"\bzusammenarbeit", r"\bgemeinsam(e|es|en)? (ziel|aufgabe|lösung)",
                        r"\bals gruppe (eine|die) aufgabe"]),
    ("konzentration", [r"\bkonzentr", r"\baufmerksam", r"\breaktion"]),
    ("austoben", [r"\brenn", r"\blaufen\b", r"\btoben", r"\bfänger", r"\bfangspiel"]),
    # "ruhig" als Adverb ("ruhig auch draußen") zählt nicht - nur als Spielcharakter
    ("beruhigen", [r"\bruhiges spiel", r"\bzur ruhe", r"\bentspann", r"\bruhige[sr]? (runde|phase|abschluss)"]),
]
SOZIALFORM_TEXT = [
    ("mannschaften", [r"\bmannschaft", r"\bteams?\b", r"\bzwei gruppen", r"\bgruppen gegeneinander",
                      r"\bparteien\b"]),
    ("paare", [r"\bpaar", r"\bzu zweit", r"\bpartner"]),
    ("einer_gegen_alle", [r"\bder fänger", r"\bdie fängerin", r"\bein fänger", r"\bein spieler ist\b",
                          r"\beine person ist\b", r"\bein\(e\) spieler", r"\bein[e]? mitspieler\w* (ist|wird|steht)"]),
    ("kleingruppen", [r"\bkleingruppe", r"\bin gruppen von", r"\bin kleinen gruppen", r"\bdreiergruppe"]),
    ("kreis", [r"\bim kreis", r"\bkreis\b", r"\bsitzkreis", r"\bstuhlkreis", r"\bstehkreis", r"\bsesselkreis"]),
]
WETTKAMPF_TEXT = [r"\bgewinn", r"\bgewonnen", r"\bverlier", r"\bpunkte?\b", r"\bsieger", r"\bwer zuerst",
                  r"\bam schnellsten", r"\bwettkampf", r"\bwettlauf", r"\bwettbewerb", r"\bscheidet aus",
                  r"\bausgeschieden", r"\bwer (als )?letzte"]
# "gemeinsam" allein reicht nicht - sonst wird jedes Singspiel zur Kooperation
KOOPERATION_TEXT = [r"\bkooperat", r"\bzusammenarbeit", r"\bgruppendynamisch",
                    r"\bgemeinsam(e|es|en)? (ziel|aufgabe|lösung)", r"\bals gruppe (eine|die) aufgabe",
                    r"\bdie gruppe muss", r"\balle müssen gemeinsam"]
GERAET_MATERIAL = [
    ("ball", r"\bb[äa]ll|frisbee|luftballon"),
    ("seil", r"seil|schnur|reepschn|band\b|wolle|faden"),
    ("tuch", r"\btuch|tücher|augenbinde|halstuch|decke"),
    ("stuehle", r"stuhl|stühle|sessel|bank\b|bänke"),
    ("papier_stift", r"papier|zettel|stift|flipchart|plakat|kärtchen|karteikarte"),
    ("karten_wuerfel", r"spielkarten|kartenspiel|würfel|kartendeck|\bkarten\b"),
    ("musik", r"musik|lied|gitarre|instrument|lautsprecher"),
]
ANFORDERUNG_TEXT = [
    ("bewegung", [r"\brenn", r"\blaufen\b", r"\btoben", r"\bspringen", r"\bhüpf", r"\bkrabbel",
                  r"\bstaffel", r"\bfänger"]),
    ("geschick", [r"\bgeschick", r"\bbalanc", r"\bzielen", r"\bwerfen", r"\bfangen (den|einen|des) ball",
                  r"\bjonglier", r"\bstapel"]),
    ("denken", [r"\brätsel", r"\braten\b", r"\bdenken", r"\bknobel", r"\blösung", r"\bwissen\b",
                r"\bquiz", r"\bstrategie", r"\büberlegen"]),
    ("merken", [r"\bmerken", r"\bgedächtnis", r"\bkim\b", r"\berinner", r"\beinprägen"]),
    ("konzentration", [r"\bkonzentr", r"\breaktion", r"\baufmerksam", r"\bschnell reagier"]),
    ("sprache", [r"\bsprechen", r"\berzähl", r"\breden\b", r"\bdiskut", r"\bwörter", r"\bfragen stellen",
                 r"\bpantomim", r"\bbegriff (erklär|erraten)", r"\bumschreib"]),
    ("rhythmus", [r"\bsingen", r"\blied", r"\bklatsch", r"\brhythm", r"\btanz", r"\bmusik"]),
]


def _heu(element):
    return (" ".join(element.get("tags") or []) + " " + (element.get("kurz") or "") + " " +
            (element.get("beschreibung") or "")).lower()


def _treffer(text, muster):
    return any(re.search(m, text) for m in muster)


def bestimme_spielachsen(element):
    """Leitet die fünf Spiel-Achsen ab (nur für bereich == "spiel")."""
    heu = _heu(element)
    tags = set(element.get("tags") or [])

    wirkung = []
    for tag, w in WIRKUNG_TAGS.items():
        if tag in tags and w not in wirkung:
            wirkung.append(w)
    for w, muster in WIRKUNG_TEXT:
        if w not in wirkung and _treffer(heu, muster):
            wirkung.append(w)
    # Bewusst NICHT aus den Planer-Slots ableiten: die sind großzügige
    # Heuristiken (jedes kurze Spiel ist "einstieg") und würden die Achse entwerten.
    if "Bewegungsspiel" in tags and "austoben" not in wirkung:
        wirkung.append("austoben")
    if tags & {"Sitzkreis", "ruhiges Spiel", "Ruhiges Spiel", "Kimspiel"} and "beruhigen" not in wirkung:
        wirkung.append("beruhigen")
    wirkung.sort(key=WIRKUNGEN.index)

    wett = _treffer(heu, WETTKAMPF_TEXT) or bool(tags & {"Mannschaftsspiel", "Staffelspiel", "Wettkampf"})
    koop = _treffer(heu, KOOPERATION_TEXT) or bool(
        tags & {"Kooperationsspiel", "Gruppendynamisches Spiel", "Vertrauensspiel"})
    if koop and not wett:
        modus = "kooperation"
    elif wett:
        modus = "wettkampf"
    else:
        modus = "ohne_gewinner"

    sozialform = "frei"
    for form, muster in SOZIALFORM_TEXT:
        if _treffer(heu, muster) or (form == "kreis" and tags & {"Kreisspiel", "Sitzkreis"}) \
                or (form == "mannschaften" and "Mannschaftsspiel" in tags):
            sozialform = form
            break

    material = " ".join(element.get("material") or []).lower()
    geraet = [name for name, rx in GERAET_MATERIAL if re.search(rx, material)]
    if not element.get("material"):
        geraet = ["nichts"]
    elif not geraet:
        geraet = ["sonstiges"]

    anforderung = [name for name, muster in ANFORDERUNG_TEXT if _treffer(heu, muster)]
    if tags & {"Bewegungsspiel", "Fangspiel", "Laufspiel", "Renn- & Fangenspiel", "Staffelspiel"} \
            and "bewegung" not in anforderung:
        anforderung.append("bewegung")
    if tags & {"Singspiel", "Tanzspiel", "Klatschspiel", "Musikspiel"} and "rhythmus" not in anforderung:
        anforderung.append("rhythmus")
    if "Geschicklichkeitsspiel" in tags and "geschick" not in anforderung:
        anforderung.append("geschick")
    if tags & {"Denkspiel", "Rätsel", "Ratespiel", "Quiz"} and "denken" not in anforderung:
        anforderung.append("denken")
    anforderung.sort(key=ANFORDERUNGEN.index)

    return {"wirkung": wirkung, "modus": modus, "sozialform": sozialform,
            "spielgeraet": geraet, "anforderung": anforderung}


# ------------------------------------------------------- Unterkategorien
# Mit 766 Spielen ist die Kategorie allein zu grob: "bewegung_drinnen" hat über
# 200 Einträge. Die Quellen liefern aber Spielarten (pfadfinder-spiele.de:
# spielart, Spielewiki: die Art-Vorlagen) – daraus wird eine zweite Ebene.
# Geprüft wird in dieser Reihenfolge, die erste Übereinstimmung gewinnt;
# deshalb stehen die aussagekräftigen Arten oben und "Bewegungsspiel" ganz unten.
UNTERKATEGORIE_SPIEL = [
    ("gelaende", ["Geländespiel"]),
    ("verstecken", ["Versteckspiel", "Suchspiel"]),
    ("namen", ["Namenslernspiel", "Kennenlernspiel"]),
    ("vertrauen", ["Vertrauensspiel", "Vertrauensübung"]),
    ("team", ["Kooperationsspiel", "Gruppendynamisches Spiel", "Kommunikationsspiel",
              "Gruppenfindungsspiel", "Diskussionsspiel"]),
    ("reflexion", ["Reflexionsmethode"]),
    ("merken", ["Kimspiel", "Merkspiel", "Spiel mit den Sinnen"]),
    ("denken", ["Denkspiel", "Rätsel", "Ratespiel", "Quiz"]),
    ("singen", ["Singspiel", "Musikspiel", "Tanzspiel", "Klatschspiel", "Spiel mit Musik"]),
    ("darstellen", ["Kreativspiel", "Darstellungsspiel", "Pantomime"]),
    ("tisch", ["Kartenspiel", "Glücksspiel", "Spiel am Tisch", "Partyspiel",
               "Spiel mit Münzen", "Würfelspiel"]),
    ("ball", ["Ballspiel", "Abschießspiel", "Spiel mit Frisbees"]),
    ("fangen", ["Fangspiel", "Renn- & Fangenspiel", "Laufspiel"]),
    ("kampf", ["Kampfspiel"]),
    ("wettkampf", ["Staffelspiel", "Mannschaftsspiel", "Spiel für Stationenlauf",
                   "Hindernisparcours"]),
    ("reaktion", ["Reaktionsspiel"]),
    ("konzentration", ["Konzentrationsspiel"]),
    ("geschick", ["Geschicklichkeitsspiel"]),
    ("ruhig", ["ruhiges Spiel", "Ruhiges Spiel", "Sitzkreis"]),
    ("warmup", ["Warm up"]),
    ("toben", ["Bewegungsspiel", "Bewegung"]),
]
# Projekte: 91 der 225 liegen in der Kategorie "kreativ". Die Themen aus dem
# Inspirator und der eigenen Sammlung ergeben auch hier eine zweite Ebene.
UNTERKATEGORIE_PROJEKT = [
    ("pfaditechnik", ["Knoten", "Karte Kompass", "Feuer machen", "Schwarzzelte",
                      "Haik", "Kohte", "Jurte", "Erste Hilfe", "Fahrtenplanung"]),
    ("kochen", ["Küche", "Backen", "Kochen", "Essen"]),
    ("basteln", ["Basteln", "Handwerkliches", "Schnitzen", "Werken", "Upcycling"]),
    ("natur", ["Pflanzen", "Baum", "Tier", "Wasser", "Sternenkunde", "Unsere Erde",
               "Natur", "Sterne"]),
    ("bund", ["Unser Bund", "Symbolik", "Versprechen", "Pfa. Geschichte", "Geschichte",
              "BiPi", "Bundeskunde"]),
    ("nachhaltigkeit", ["Nachhaltigkeit", "Umwelt"]),
    ("gruppe", ["Unsere Sippe", "Gesellschaftliches", "Beteiligung", "Gemeinschaft"]),
    ("musisch", ["Musisches", "Geschichten", "Singen", "Theater", "Musik"]),
    ("spiel", ["Bewegung", "Kim-Spiel", "Detektiv", "Geländespiel", "Wettkampf"]),
]


def bestimme_unterkategorie(element):
    """
    Vergibt die zweite Gliederungsebene aus den Tags bzw. Themen.
    Für Proben und Aktivitäten bleibt sie leer – dort sind es so wenige
    Einträge, dass die Kategorie allein reicht.
    """
    if element["bereich"] == "spiel":
        tabelle, quelle = UNTERKATEGORIE_SPIEL, element.get("tags")
    else:
        # Außerhalb der Spiele ist der Bereich selbst schon das Thema;
        # die feine Gliederung steht im Feld "themen".
        return ""
    vorhanden = set(entschaerfe(t) for t in (quelle or []))
    for schluessel, begriffe in tabelle:
        for begriff in begriffe:
            if entschaerfe(begriff) in vorhanden:
                return schluessel
    return "sonstiges"


# ---------------------------------------------------------------- Dubletten
def markiere_dubletten(elemente, redaktion):
    """
    Markiert Elemente, die dasselbe Spiel meinen, gegenseitig.

    Grundlage ist der normalisierte Titel. Das findet nur Titelgleichheit –
    "Möhren ziehen" und "Karottenziehen" fallen durch. Deshalb kommen aus
    data/redaktion.json zusätzliche Gruppen dazu, und falsch verknüpfte
    Namensgleichheiten werden wieder gelöst.
    """
    nach_id = {e["id"]: e for e in elemente}
    verbunden = defaultdict(set)

    def verbinde(ids):
        vorhanden = [i for i in ids if i in nach_id]
        for eins in vorhanden:
            for zwei in vorhanden:
                if eins != zwei:
                    verbunden[eins].add(zwei)

    nach_titel = defaultdict(list)
    for element in elemente:
        nach_titel[dubletten_schluessel(element["titel"])].append(element["id"])
    for gruppe in nach_titel.values():
        if len(gruppe) > 1:
            verbinde(gruppe)

    for eintrag in redaktion.get("auch_dublette", []):
        verbinde(eintrag["ids"])

    # Gleicher Titel, verschiedenes Spiel: Verbindung wieder auflösen
    getrennt = 0
    for eintrag in redaktion.get("keine_dublette", []):
        ids = [i for i in eintrag["ids"] if i in nach_id]
        for eins in ids:
            for zwei in ids:
                if eins != zwei and zwei in verbunden.get(eins, set()):
                    verbunden[eins].discard(zwei)
                    getrennt += 1

    gruppen = set()
    for element in elemente:
        partner = sorted(verbunden.get(element["id"], set()))
        if partner:
            element["dubletten"] = partner
            gruppen.add(tuple(sorted([element["id"]] + partner)))
        else:
            element.pop("dubletten", None)
    return len(gruppen), getrennt // 2


# ---------------------------------------------------------------- Prüfung
def pruefe(elemente):
    """Prüft Pflichtfelder und Wertebereiche. Gibt die Liste der Fehler zurück."""
    fehler = []
    gesehen = set()
    for element in elemente:
        kennung = element.get("id", "<ohne id>")
        for feld in PFLICHTFELDER:
            if feld not in element:
                fehler.append("{}: Feld '{}' fehlt".format(kennung, feld))
        if kennung in gesehen:
            fehler.append("{}: ID doppelt vergeben".format(kennung))
        gesehen.add(kennung)
        if not (element.get("titel") or "").strip():
            fehler.append("{}: leerer Titel".format(kennung))
        if len((element.get("beschreibung") or "").strip()) < 20:
            fehler.append("{}: Beschreibung fehlt oder ist zu kurz".format(kennung))
        bereich = element.get("bereich")
        if bereich not in KATEGORIEN:
            fehler.append("{}: unbekannter Bereich '{}'".format(kennung, bereich))
        elif element.get("kategorie") not in KATEGORIEN[bereich]:
            fehler.append("{}: Kategorie '{}' passt nicht zum Bereich '{}'".format(
                kennung, element.get("kategorie"), bereich))
        if element.get("bereich") == "spiel":
            if set(element.get("wirkung") or []) - set(WIRKUNGEN):
                fehler.append("{}: ungültige Wirkung {}".format(kennung, element.get("wirkung")))
            if element.get("modus") not in MODI:
                fehler.append("{}: ungültiger Modus '{}'".format(kennung, element.get("modus")))
            if element.get("sozialform") not in SOZIALFORMEN:
                fehler.append("{}: ungültige Sozialform '{}'".format(kennung, element.get("sozialform")))
            if set(element.get("spielgeraet") or []) - set(SPIELGERAETE) or not element.get("spielgeraet"):
                fehler.append("{}: ungültiges Spielgerät {}".format(kennung, element.get("spielgeraet")))
            if set(element.get("anforderung") or []) - set(ANFORDERUNGEN):
                fehler.append("{}: ungültige Anforderung {}".format(kennung, element.get("anforderung")))
        if element.get("umfang") not in UMFAENGE:
            fehler.append("{}: unbekannter Umfang '{}'".format(kennung, element.get("umfang")))
        if not isinstance(element.get("unterkategorie"), str):
            fehler.append("{}: unterkategorie ist kein Text".format(kennung))
        if element.get("ort") not in ORTE:
            fehler.append("{}: unbekannter Ort '{}'".format(kennung, element.get("ort")))
        if element.get("vorbereitung") not in VORBEREITUNGEN:
            fehler.append("{}: unbekannte Vorbereitung '{}'".format(
                kennung, element.get("vorbereitung")))
        if not element.get("slots") or set(element["slots"]) - SLOTS:
            fehler.append("{}: ungültige Slots {}".format(kennung, element.get("slots")))
        if set(element.get("altersstufen") or []) - ALTERSSTUFEN:
            fehler.append("{}: ungültige Altersstufe {}".format(kennung, element["altersstufen"]))
        dauer_min, dauer_max = element.get("dauer_min"), element.get("dauer_max")
        if not isinstance(dauer_min, int) or not isinstance(dauer_max, int):
            fehler.append("{}: Dauer ist keine ganze Zahl".format(kennung))
        elif dauer_min < 1 or dauer_max < dauer_min:
            fehler.append("{}: unplausible Dauer {}-{}".format(kennung, dauer_min, dauer_max))
        quelle = element.get("quelle") or {}
        for feld in ("name", "autor", "lizenz"):
            if not (quelle.get(feld) or "").strip():
                fehler.append("{}: quelle.{} fehlt".format(kennung, feld))
        if "url" not in quelle:
            fehler.append("{}: quelle.url fehlt".format(kennung))
    return fehler


# ---------------------------------------------------------------- Ausgabe
def statistik(elemente):
    """Gibt die Statistik auf der Konsole aus."""
    def zeige(titel, zaehler):
        print("\n{}".format(titel))
        breite = max((len(str(k)) for k in zaehler), default=0)
        for schluessel, anzahl in zaehler.most_common():
            print("  {:<{b}}  {:>4}".format(str(schluessel), anzahl, b=breite))

    print("\n" + "=" * 58)
    print("STATISTIK  –  {} Elemente insgesamt".format(len(elemente)))
    print("=" * 58)
    zeige("nach Bereich:", Counter(e["bereich"] for e in elemente))
    zeige("nach Umfang:", Counter(e["umfang"] for e in elemente))
    zeige("nach Quelle:", Counter(e["quelle"]["name"] for e in elemente))
    zeige("nach Lizenz:", Counter(e["quelle"]["lizenz"] for e in elemente))
    for bereich in BEREICHE:
        teilmenge = [e for e in elemente if e["bereich"] == bereich]
        if not teilmenge:
            continue
        kategorien = Counter(e["kategorie"] for e in teilmenge if e["kategorie"])
        if kategorien:
            zeige("Kategorien ({}, {} Stück):".format(bereich, len(teilmenge)), kategorien)
        unter = Counter(e["unterkategorie"] for e in teilmenge if e["unterkategorie"])
        if unter:
            zeige("Unterkategorien ({}):".format(bereich), unter)
    spiele = [e for e in elemente if e["bereich"] == "spiel"]
    zeige("Spiele nach Wirkung (mehrfach):", Counter(w for e in spiele for w in e["wirkung"]))
    zeige("Spiele nach Modus:", Counter(e["modus"] for e in spiele))
    zeige("Spiele nach Sozialform:", Counter(e["sozialform"] for e in spiele))
    zeige("Spiele nach Spielgerät (mehrfach):", Counter(g for e in spiele for g in e["spielgeraet"]))
    zeige("Spiele nach Anforderung (mehrfach):", Counter(a for e in spiele for a in e["anforderung"]))
    print("\nSpiele ohne erkannte Wirkung: {}, ohne Anforderung: {}".format(
        sum(1 for e in spiele if not e["wirkung"]), sum(1 for e in spiele if not e["anforderung"])))
    zeige("nach Ort:", Counter(e["ort"] for e in elemente))
    zeige("nach Vorbereitung:", Counter(e["vorbereitung"] for e in elemente))
    zeige("nach Slot:", Counter(s for e in elemente for s in e["slots"]))
    zeige("nach Altersstufe:", Counter(
        s for e in elemente for s in (e["altersstufen"] or ["(alle / keine Angabe)"])))
    print("\nohne Material: {}".format(sum(1 for e in elemente if not e["material"])))


def main():
    vergeben = set()
    print("Lese Quellen ...")
    elemente = []
    elemente += lade_eigene(vergeben)
    print("  eigene Ideen:        {}".format(len(elemente)))
    vorher = len(elemente)
    elemente += lade_probenbuch(vergeben)
    print("  DPB-Probenbuch:      {}".format(len(elemente) - vorher))
    vorher = len(elemente)
    elemente += lade_inspirator(vergeben)
    print("  Inspirator:          {}".format(len(elemente) - vorher))
    for pfad, name in ((PFADFINDER_SPIELE, "pfadfinder-spiele.de"), (SPIELEWIKI, "Spielewiki")):
        geladen = lade_import(pfad)
        for element in geladen:
            # ID trotzdem gegen Kollisionen absichern
            if element["id"] in vergeben:
                element["id"] = mache_id(element["id"].split("-")[0], element["titel"], vergeben)
            else:
                vergeben.add(element["id"])
        elemente += geladen
        print("  {:<20} {}".format(name + ":", len(geladen)))

    redaktion = lade_redaktion()
    elemente, bericht = wende_redaktion_an(elemente, redaktion)
    print()
    print("Redaktion (data/redaktion.json):")
    print("  gesperrt:   {}".format(len(bericht["gesperrt"])))
    for zeile in bericht["gesperrt"]:
        print("     - {}".format(zeile))
    print("  umbenannt:  {}".format(len(bericht["umbenannt"])))
    for zeile in bericht["umbenannt"]:
        print("     - {}".format(zeile))
    print("  korrigiert: {}".format(len(bericht["korrigiert"])))
    print("  Bereich von Hand gesetzt: {}".format(len(bericht.get("nachtraeglich", {}))))
    if bericht["unbekannt"]:
        print("  ACHTUNG, IDs gibt es nicht (mehr): {}".format(", ".join(bericht["unbekannt"])))

    # Materialangaben, die "nichts" bedeuten, gehören nicht in die Liste -
    # sonst fallen die Spiele aus dem Filter "nur ohne Material" heraus.
    # Achtung: "Kein Plastik!" ist eine Regel und muss stehen bleiben.
    nichts = re.compile(
        r"^(kein|keine|keines|nichts|ohne)\b\s*(material\w*)?\s*"
        r"(notwendig|n[oö]tig|erforderlich)?\s*(\(.*\))?[.!]*$", re.IGNORECASE)
    bereinigt = []
    for element in elemente:
        vorher = list(element.get("material") or [])
        nachher = [m for m in vorher
                   if not nichts.match(m.strip()) and m.strip().lower() != "zur not ohne"]
        if nachher != vorher:
            element["material"] = nachher
            bereinigt.append("{}: {} -> {}".format(element["id"], vorher, nachher))
    if bereinigt:
        print("\nMaterialangaben bereinigt ({}):".format(len(bereinigt)))
        for zeile in bereinigt:
            print("   {}".format(zeile))

    # Die Materialangaben des Inspirators sind in der Quelldatei hart auf
    # 29 Zeichen abgeschnitten (Feldlänge der Ursprungsdatenbank) - meist
    # mitten im Wort: "Computer/ Endgerät mit Intern". Das lässt sich nicht
    # wiederherstellen, aber es soll wenigstens als abgeschnitten erkennbar sein.
    abgeschnitten = 0
    for element in elemente:
        if not element["id"].startswith("insp-"):
            continue
        neue = []
        for eintrag in element.get("material") or []:
            if len(eintrag) == 29 and not eintrag.endswith(("…", ".", ")")):
                eintrag = eintrag.rstrip() + " …"
                abgeschnitten += 1
            neue.append(eintrag)
        element["material"] = neue
    if abgeschnitten:
        print("\n{} Materialangaben des Inspirators als abgeschnitten markiert"
              .format(abgeschnitten))

    # Bereich und Umfang festlegen. Die Quellen, die ihren Bereich kennen,
    # haben ihn schon in "_bereich" hinterlegt; für den Rest entscheidet
    # die Themen-Abstimmung.
    for element in elemente:
        element["bereich"] = bestimme_bereich(element)
        element.pop("_bereich", None)
        # Die Pfadfindertechnik hat eine zweite Ebene, die übrigen Bereiche nicht
        if element["bereich"] == "pfadfindertechnik" and not element.get("kategorie"):
            element["kategorie"] = technik_kategorie(element)
        elif element["bereich"] not in ("spiel", "pfadfindertechnik"):
            element["kategorie"] = ""
        if not element.get("umfang"):
            element["umfang"] = bestimme_umfang(element)
        # Ein Baustein, der eine Stunde und länger dauert, füllt den Abend
        if element["umfang"] == "baustein" and element["dauer_min"] >= 60:
            element["umfang"] = "ganzer_abend"
        element["slots"] = slots_fuer(element["bereich"], element["umfang"],
                                      element["kategorie"], element["dauer_min"])
        element["unterkategorie"] = bestimme_unterkategorie(element)
        # Redaktionelle Entscheidung schlägt die Automatik
        eintrag = bericht["nachtraeglich"].get(element["id"])
        if eintrag:
            if eintrag.get("bereich"):
                element["bereich"] = eintrag["bereich"]
                if element["bereich"] == "pfadfindertechnik":
                    element["kategorie"] = eintrag.get("kategorie") or technik_kategorie(element)
                elif element["bereich"] == "spiel":
                    element["kategorie"] = eintrag.get("kategorie") or "ruhig"
                    element["unterkategorie"] = bestimme_unterkategorie(element)
                else:
                    element["kategorie"] = ""
                element["slots"] = slots_fuer(element["bereich"], element["umfang"],
                                              element["kategorie"], element["dauer_min"])
            elif eintrag.get("kategorie"):
                element["kategorie"] = eintrag["kategorie"]
        # Die Achsen erst jetzt - nachdem der Bereich endgültig feststeht
        if element["bereich"] == "spiel":
            element.update(bestimme_spielachsen(element))
        else:
            element.update({"wirkung": [], "modus": "", "sozialform": "",
                            "spielgeraet": [], "anforderung": []})
        for feld, wert in bericht.get("achsen", {}).get(element["id"], {}).items():
            element[feld] = wert
        element.pop("element_typ", None)   # ersetzt durch bereich + umfang

    gruppen, getrennt = markiere_dubletten(elemente, redaktion)
    betroffen = sum(1 for e in elemente if e.get("dubletten"))
    print("\nDubletten: {} Gruppen, {} Elemente markiert (nichts gelöscht)"
          .format(gruppen, betroffen))
    if getrennt:
        print("  {} falsche Verknüpfung(en) laut Redaktion wieder gelöst".format(getrennt))

    fehler = pruefe(elemente)
    if fehler:
        print("\n{} FEHLER bei der Prüfung:".format(len(fehler)))
        for eintrag in fehler[:40]:
            print("  - {}".format(eintrag))
        if len(fehler) > 40:
            print("  ... und {} weitere".format(len(fehler) - 40))
        return 1
    print("Prüfung: alle Pflichtfelder und Wertebereiche in Ordnung.")

    elemente.sort(key=lambda e: (BEREICHE.index(e["bereich"]), entschaerfe(e["titel"])))

    AUSGABE_JSON.parent.mkdir(parents=True, exist_ok=True)
    inhalt = {
        "meta": {
            "name": "Heimabend-Baukasten – Elemente",
            "beschreibung": "Zusammengeführte Bausteine für Heimabende. "
                            "Jedes Element trägt die Lizenz seiner Quelle.",
            "anzahl": len(elemente),
            "quellen": sorted({e["quelle"]["name"] for e in elemente}),
            "lizenzen": sorted({e["quelle"]["lizenz"] for e in elemente}),
            "hinweis": "Erzeugt von scripts/build.py – nicht von Hand bearbeiten. "
                       "Das Projekt ist nicht-kommerziell (NC-Inhalte enthalten).",
        },
        "elemente": elemente,
    }
    with open(AUSGABE_JSON, "w", encoding="utf-8") as datei:
        json.dump(inhalt, datei, ensure_ascii=False, indent=1)

    AUSGABE_JS.parent.mkdir(parents=True, exist_ok=True)
    with open(AUSGABE_JS, "w", encoding="utf-8") as datei:
        datei.write("// Erzeugt von scripts/build.py – nicht von Hand bearbeiten.\n")
        datei.write("// Ermöglicht der Web-App, auch per Doppelklick auf index.html zu laufen\n")
        datei.write("// (der Browser sperrt fetch() bei file://-Adressen).\n")
        datei.write("window.ELEMENTE = ")
        # kompakt geschrieben: die Datei liest nur der Browser, und am Handy
        # zählt jedes Kilobyte. Die lesbare Fassung steht in data/elemente.json.
        json.dump(elemente, datei, ensure_ascii=False, separators=(",", ":"))
        datei.write(";\n")

    statistik(elemente)
    print("\nGeschrieben:")
    print("  {}".format(AUSGABE_JSON))
    print("  {}".format(AUSGABE_JS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
