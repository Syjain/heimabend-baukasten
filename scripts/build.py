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
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
EIGENE = WURZEL / "data" / "eigene" / "heimabend-ideen.json"
# Eigene Elemente, die schon im fertigen Schema stehen (Rituale für den
# Eröffnungs- und Schlusskreis, Gruppeneinteilung, Auswertung). Sie bringen
# ihre Slots selbst mit - nur hier kommt "eroeffnung" überhaupt vor.
RAHMEN = WURZEL / "data" / "eigene" / "rahmen-und-methoden.json"
PROBENBUCH = WURZEL / "data" / "quellen" / "probenbuch" / "proben-dpb.json"
# Redigierte Fassung (lesbarer Text + Heimabend-Zuschnitt). Ist sie da, gewinnt sie;
# der Rohtext bleibt als Rückfall, damit der Build nie ohne Proben dasteht.
PROBENBUCH_REDIGIERT = WURZEL / "data" / "quellen" / "probenbuch" / "proben-dpb-redigiert.json"
INSPIRATOR = WURZEL / "data" / "quellen" / "inspirator" / "inspirator-ideen.json"
PFADFINDER_SPIELE = WURZEL / "data" / "quellen" / "pfadfinder-spiele" / "elemente.json"
SPIELEWIKI = WURZEL / "data" / "quellen" / "spielewiki" / "elemente.json"
# Rohdaten des Spielewiki-Imports. Sie liegen in .gitignore, sind also nicht
# überall da. Wenn sie fehlen, wird "platz" nur aus dem Text abgeleitet und die
# Statistik sagt das ausdrücklich. Gebraucht werden zwei Infobox-Felder, die der
# Import nicht ins Schema übernimmt: "Ort" (= Platzbedarf) und "Dauer"
# ("beliebig"/"pro Runde" = rundenweise dehnbar).
SPIELEWIKI_ROH = WURZEL / "data" / "quellen" / "spielewiki" / "raw" / "seiten.json"
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
    "platz", "hosensackspiel", "uebt", "naehe",
    "dauer_min", "dauer_max", "ort", "material", "vorbereitung",
    "kurz", "beschreibung", "tags", "themen", "quelle",
    "kern", "varianten",
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


def lade_rahmen(vergeben):
    """
    Mappt data/eigene/rahmen-und-methoden.json auf das Element-Schema.

    Anders als heimabend-ideen.json steht diese Datei schon im fertigen Schema.
    Zwei Dinge bleiben deshalb stehen, statt neu berechnet zu werden:
    die Slots (slots_fuer() kann "eroeffnung" gar nicht vergeben) und der
    Bereich. Fehlt die Datei, läuft der Build ohne sie weiter.
    """
    if not RAHMEN.exists():
        print("  Hinweis: {} fehlt - Rahmen und Methoden fehlen.".format(RAHMEN.name))
        return []
    with open(RAHMEN, encoding="utf-8") as datei:
        daten = json.load(datei)
    elemente = []
    for roh in daten.get("elemente", []):
        element = dict(roh)
        if element["id"] in vergeben:
            element["id"] = mache_id("eig", element["titel"], vergeben)
        else:
            vergeben.add(element["id"])
        element["_bereich"] = element.get("bereich") or "gemeinschaft"
        element["_slots_fest"] = True
        # Eine Quelle, eine Schreibweise: die 61 Ideen aus heimabend-ideen.json
        # tragen denselben Namen, sonst stünden zwei "eigene" Quellen in der App.
        element["quelle"] = {
            "name": "Heimabend-Baukasten (eigene Sammlung)",
            "url": "",
            "autor": "Heimabend-Baukasten",
            "lizenz": (element.get("quelle") or {}).get("lizenz") or "CC BY-SA 4.0",
        }
        elemente.append(element)
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


def lade_probenbuch_redigiert(vergeben):
    """
    Mappt data/quellen/probenbuch/proben-dpb-redigiert.json auf das Element-Schema.

    Die redigierte Fassung bringt ihre Metadaten selbst mit (Kategorie, Umfang, Dauer,
    Altersstufen, Ort, Material, Vorbereitung) – PROBENBUCH_ZUORDNUNG gilt nur noch
    für den Rohtext-Rückfall. Die Beschreibung setzt sich aus drei Teilen zusammen:
    dem Wissen aus dem Probenbuch, dem, was zum Ablegen gehört, und dem Vorschlag
    für den Heimabend.
    """
    with open(PROBENBUCH_REDIGIERT, encoding="utf-8") as datei:
        daten = json.load(datei)

    elemente = []
    for probe in daten.get("proben", []):
        nummer = probe["nummer"]
        teile = [probe["wissen"].strip()]
        if probe.get("prueft"):
            teile.append("## Was zur Probe gehört\n\n" + probe["prueft"].strip())
        if probe.get("heimabend"):
            teile.append("## So bringst du es in den Heimabend\n\n" + probe["heimabend"].strip())
        beschreibung = "\n\n".join(teile)

        hinweise = []
        if probe.get("veraltet"):
            hinweise.append(probe["veraltet"].strip())
        if probe.get("tipps"):
            hinweise.append(probe["tipps"].strip())

        umfang = probe["umfang"]
        kategorie = probe["kategorie"]
        dauer_min = probe["dauer_min"]
        tags = ["Probenbuch", "Pfadfinderwissen", "Probe {}".format(nummer)]
        for tag in probe.get("tags", []):
            if tag not in tags:
                tags.append(tag)

        elemente.append({
            "id": mache_id("pb", probe["titel"], vergeben),
            "titel": probe["titel"],
            "_bereich": "pfadfindertechnik",
            "umfang": umfang,
            "kategorie": kategorie,
            "slots": slots_fuer("pfadfindertechnik", umfang, kategorie, dauer_min),
            "altersstufen": list(probe.get("altersstufen", [])),
            "dauer_min": dauer_min,
            "dauer_max": probe["dauer_max"],
            "ort": probe["ort"],
            "material": list(probe.get("material", [])),
            "vorbereitung": probe["vorbereitung"],
            "kurz": probe["kurz"].strip(),
            "beschreibung": beschreibung,
            "tipps": "\n\n".join(hinweise),
            "tags": tags,
            "themen": [probe["titel"]],
            "quelle": dict(PROBENBUCH_QUELLE),
        })
    return elemente


def lade_probenbuch(vergeben):
    """Mappt das Probenbuch auf das Element-Schema – redigierte Fassung, sonst Rohtext."""
    if PROBENBUCH_REDIGIERT.exists():
        return lade_probenbuch_redigiert(vergeben)
    print("  Hinweis: {} fehlt – Rohtext-Fassung wird verwendet.".format(PROBENBUCH_REDIGIERT.name))
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


def _heu_weit(element):
    """Wie _heu, aber mit Titel, Themen, Tipps und Material - für die Achsen von 09/2026."""
    teile = [" ".join(element.get("tags") or []), " ".join(element.get("themen") or []),
             element.get("titel") or "", element.get("kurz") or "",
             element.get("beschreibung") or "", element.get("tipps") or "",
             " ".join(element.get("material") or [])]
    return " ".join(teile).lower()


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


# --------------------------------------------- Vier weitere Spiel-Achsen (08.09.2026)
# Die Recherche in docs/recherche-kategorien-anderer-sammlungen.md (Abschnitt 3)
# hat vier Fragen gefunden, die andere Sammlungen beantworten und wir bisher nicht.
# Sie laufen nach demselben Muster wie die fünf Achsen oben:
#   Quellfeld (wenn vorhanden) -> Tags -> Text -> data/redaktion.json ("achsen").
#
#   platz           Wieviel Platz braucht es?     tisch | zimmer | saal_wiese | gelaende | ""
#   hosensackspiel  Geht es aus der Hosentasche?  true | false
#   uebt            Welche Probe übt es nebenbei? Liste der Pfadfindertechnik-Kategorien
#   naehe           Wieviel Körperkontakt und Vertrauen? keine | leicht | hoch
#
# "" bzw. die leere Liste heißt immer: aus der Quelle nicht erkennbar - nie
# "trifft nicht zu". Ausnahme ist "naehe": dort ist "keine" die bewusste Aussage
# "kein Körperkontakt erkennbar"; "" gibt es nur über die Redaktion.

PLAETZE = ["tisch", "zimmer", "saal_wiese", "gelaende"]
NAEHE_WERTE = ["keine", "leicht", "hoch"]
# Dieselben acht Werte wie die Kategorie bei bereich "pfadfindertechnik" -
# ohne "sonstiges": eine Probe, die niemand benennen kann, übt auch kein Spiel.
UEBT_WERTE = ["knoten", "karte_kompass", "feuer", "erste_hilfe", "zelte_bauten",
              "natur", "bundeskunde", "fahrtentechnik"]


# ---------------------------------------------------------------- platz
# Das Spielewiki-Feld "Ort" ist kein drinnen/draußen, sondern der Platzbedarf
# (632 Werte, 166 verschiedene Formulierungen). Die Reihenfolge der Muster ist
# wichtig, das erste Muster gewinnt: "kleine Spielfläche" (33x) muss vor
# "Spielfläche" stehen, sonst landet der halbe Gruppenraum auf der Wiese.
PLATZ_ORT_MUSTER = [
    ("gelaende", r"wald|gel[äa]nde|stadt|freie natur|gro[ßs]e[sn]? gebiet|zwischen b[äa]umen|"
                 r"\bsee\b|fluss|nachtgel"),
    ("tisch", r"tisch|sitzkreis|sesselkreis|stuhlkreis|sitzreihe|am boden|im sitzen"),
    ("zimmer", r"kleine spielfl|kleine[rns]? (freie )?(fl[äa]che|raum)|kleine ?\"?tanzfl|"
               r"gruppenraum|zimmer|innenraum|k[üu]che|zwei r[äa]ume|getrennte r[äa]ume"),
    ("saal_wiese", r"spielfeld|spielfl[äa]che|laufstrecke|wegstrecke|turnhalle|turnsaal|\bsaal\b|"
                   r"\bhalle\b|wiese|rasen|sportplatz|im freien|drau[ßs]en|au[ßs]en|garten|\bhof\b|"
                   r"\bnetz\b|gro[ßs]e fl[äa]che|mauer"),
    ("zimmer", r"[üu]berall|beliebig|egal|platz|stehkreis|\bkreis\b|boden|wand|innen|haus|drinnen|"
               r"raum|fl[äa]che|untergrund"),
]
# Rückfall für alle Quellen ohne Ortsfeld (eigene, Inspirator, pfadfinder-spiele.de).
# Das Feld "Umgebung" von pfadfinder-spiele.de sagt nur drinnen/draußen und trägt
# zum Platzbedarf nichts bei - deshalb steht es hier nicht.
PLATZ_TEXT_MUSTER = [
    ("gelaende", [r"\bim wald\b", r"\bgel[äa]ndespiel", r"\bim gel[äa]nde", r"\bdurch den wald",
                  r"\bin der stadt", r"\bwaldst[üu]ck", r"\bschnitzeljagd", r"\bnachtwanderung"]),
    ("saal_wiese", [r"\bturnhalle", r"\bsporthalle", r"\bauf (der|eine[rn]) wiese", r"\bspielfeld",
                    r"\bgro[ßs]er? (raum|saal|fl[äa]che)", r"\bstaffel", r"\blaufstrecke",
                    r"\bviel platz", r"\bsportplatz"]),
    ("tisch", [r"\bam tisch", r"\bum den tisch", r"\bstuhlkreis", r"\bsitzkreis", r"\bsesselkreis",
               r"\bim sitzen", r"\bauf dem boden sitz"]),
    ("zimmer", [r"\bgruppenraum", r"\bim zimmer", r"\bkleine[rn]? raum", r"\bim heim\b",
                r"\bwenig platz"]),
]


def spielewiki_seitentitel(element):
    """Holt den Wikiseiten-Titel aus quelle.url - der überlebt auch ein Umbenennen."""
    url = (element.get("quelle") or {}).get("url") or ""
    if "/wiki/" not in url:
        return ""
    return urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("_", " ")


def lade_spielewiki_infobox():
    """
    Liest "Ort" und "Dauer" aus den Spielewiki-Rohdaten (Wikitext der Infobox).

    Der Import wirft beide Felder weg: "Ort" wird auf drinnen/draussen/beides
    eingedampft, "Dauer" auf Minuten. Für "platz" und "hosensackspiel" brauchen
    wir aber den Originaltext. Fehlt die Rohdatei, kommt ein leeres Verzeichnis
    zurück und die Ableitung läuft nur über den Text.
    """
    if not SPIELEWIKI_ROH.exists():
        return {}
    with open(SPIELEWIKI_ROH, encoding="utf-8") as datei:
        seiten = json.load(datei)
    infobox = {}
    for eintrag in seiten.values():
        try:
            wikitext = eintrag["revisions"][0]["slots"]["main"]["*"]
        except (KeyError, IndexError, TypeError):
            continue
        felder = {}
        for feld in ("Ort", "Dauer"):
            treffer = re.search(r"\|\s*" + feld + r"\s*=([^|}\n]*)", wikitext)
            if treffer:
                felder[feld.lower()] = treffer.group(1).strip()
        if felder:
            infobox[eintrag.get("title") or ""] = felder
    return infobox


def bestimme_platz(element, ort_roh):
    """tisch | zimmer | saal_wiese | gelaende | "" - erst das Quellfeld, dann der Text."""
    if ort_roh:
        text = ort_roh.lower()
        for name, muster in PLATZ_ORT_MUSTER:
            if re.search(muster, text):
                return name
    if element.get("unterkategorie") == "gelaende" or "Geländespiel" in (element.get("tags") or []):
        return "gelaende"
    if element.get("unterkategorie") == "tisch":
        return "tisch"
    heu = _heu(element)
    for name, muster in PLATZ_TEXT_MUSTER:
        if _treffer(heu, muster):
            return name
    return ""


# ------------------------------------------------------- hosensackspiel
# Begriff von jubla.netz (Jungwacht Blauring): ein Spiel, das man "aus der
# Hosentasche" zieht - kein Material, keine Vorbereitung, jederzeit und überall.
# Die Recherche (3.4) nennt die Regel: kein Material UND Vorbereitung gering UND
# (dauer_min <= 10 ODER die Quelle sagt "pro Runde"/"beliebig", also rundenweise
# dehnbar). Rundenweise dehnbare Spiele sind Lückenfüller, auch wenn der Import
# ihnen der Vorsicht halber 20 Minuten gegeben hat.
DEHNBAR_MUSTER = re.compile(r"pro runde|beliebig", re.IGNORECASE)


def bestimme_hosensackspiel(element, dauer_roh):
    """
    Abweichung von der Recherche, mit Absicht: dort steht "dauer_min <= 10",
    die genannten 77 Spiele ergeben sich aber nur mit dauer_max <= 10. Mit
    dauer_min wären es 267 von 794 - jedes dritte Spiel, damit taugt der Filter
    "5 Minuten übrig" nichts mehr. Gemeint ist "in zehn Minuten durch", also die
    Obergrenze. Wer es anders will, ändert diese eine Zeile.
    """
    if element.get("material"):
        return False
    if element.get("vorbereitung") != "gering":
        return False
    if 0 < (element.get("dauer_max") or 0) <= 10:
        return True
    return bool(dauer_roh and DEHNBAR_MUSTER.search(dauer_roh))


# ------------------------------------------------------------------ uebt
# "Welche Probe übt das Spiel nebenbei?" - die Pfadfinder-Achse (Recherche 3.1,
# Scoutopedias "jeu de technique", Baden-Powell 1908). Bewusst streng: es zählt
# nur, wo die Fertigkeit wirklich geübt wird.
#
# Deshalb ausgeschlossen:
# - Wortlisten-Spiele (Tabu, Montagsmaler, Quiz, Memory, Stadt-Land-Fluss …).
#   In ihren Begriffslisten steht irgendwann jedes Pfadfinderwort; "Digitales
#   Tabu" traf so sechs von acht Proben, ohne eine einzige zu üben.
# - "Feuer, Wasser, Sturm" und Verwandte: Kommandospiel, kein Feuer.
# - "Gordischer Knoten" / "Menschenknoten": ein Knäuel aus Armen, kein Knoten.
# - "Knoten am Seilende" als Beiwerk eines Wurfspiels.
# - Spielkarten, Karteikarten, gelbe/rote Karte - das ist keine Landkarte.
# - Zeltstangen als Bastelmaterial (Riesen-Mikado) - das ist kein Zeltbau.
# - Erste-Hilfe-Kasten als Gegenstand in einer Rangliste (NASA-Spiel).
# - Kimspiele: sie üben Beobachten und Merken, aber keine der acht Proben.
#   Baden-Powell zählt sie zur Beobachtungsschulung; eine eigene Achse dafür
#   wäre ehrlicher als sie unter "natur" zu verstecken. Bewusst offen gelassen.
# - "Stationenlauf" als Tag: die Einzelspiele einer Olympiade (Dosenwerfen,
#   Seilspringen) üben keine Orientierung, nur der Lauf als Ganzes.
UEBT_WORTLISTE = re.compile(
    r"\btabu\b|montagsmaler|pantomime|scharade|\bquiz\b|stadt[ -]land[ -]fluss|wer bin ich|"
    r"teekesselchen|galgenm|begriffe? erraten|paare finden|p[äa]rchen finden|\bmemory\b|"
    r"\bdalli\b|\bactivity\b|lexikonspiel")
UEBT_AUSSCHLUSS = re.compile(
    r"feuer,? ?wasser,? ?(sturm|blitz|sand|erde)|feuer frei|feuerwehr|lauffeuer|feuer und flamme|"
    r"gordische[rn]? knoten|menschenknoten|knoten im (magen|taschentuch)|knoten am seil\w*|"
    r"kartenspiel|spielkarten|karteikarte|gelbe karte|rote karte|zeltstange\w*|"
    r"erste[- ]hilfe[- ](kasten|set|täschchen)|verbandskasten")
UEBT_MUSTER = [
    ("knoten", [r"\bknoten (kn[üu]pf|binden|machen|[üu]ben|lernen|schlagen)", r"\bknotenkunde",
                r"\bknotenstaffel", r"\bknoten-olympiade", r"\bkreuzknoten", r"\bmastwurf",
                r"\bzimmermannsschlag", r"\bpalstek", r"\bschotstek", r"\bwebeleinstek",
                r"\bbrezelbund|kreuzbund|parallelbund|diagonalbund", r"\bbund (schlagen|binden)",
                r"\bknotenkette"]),
    ("karte_kompass", [r"\bkompass", r"\bhimmelsrichtung", r"\bkarte lesen", r"\bkarte und kompass",
                       r"karte kompass", r"\borientierungslauf", r"\bazimut", r"\bpeilen\b",
                       r"\bmarschzahl", r"\bmorse", r"\bwinkeralphabet", r"\bwaldl[äa]uferzeichen",
                       r"\bgeheimschrift", r"\bkroki", r"\bschatzkarte", r"\bkarte zeichnen",
                       r"\bschritte messen", r"\bentfernung sch[äa]tzen", r"\bschnitzeljagd",
                       r"\bschatzsuche", r"\bfotorallye", r"\bgeocach", r"\bnachtwanderung",
                       r"\blageplan"]),
    ("feuer", [r"\bfeuer (machen|entz[üu]nden|anz[üu]nden|entfachen|sch[üu]ren|aufbauen)",
               r"\blagerfeuer (bauen|entz[üu]nden|aufbauen)", r"\bfeuerstelle", r"\bzunder",
               r"\bfeuerarten", r"\bpyramidenfeuer", r"\bpagodenfeuer", r"\bfunken schlagen",
               r"\bfeuerbohrer"]),
    ("erste_hilfe", [r"\berste[ -]hilfe(?!\w)", r"\bverband (anlegen|wickeln)", r"\bdruckverband",
                     r"\bstabile seitenlage", r"\brettungsgriff", r"\bnotruf\b", r"\bwiederbelebung",
                     r"\bdreiecktuch", r"\btrage (bauen|aus)", r"\bwundversorgung", r"\bsanit[äa]ts",
                     r"\bverletzte[nr]? (versorgen|transportier)"]),
    ("zelte_bauten", [r"\bzelt (aufbauen|aufstellen|bauen)", r"\bzeltbau", r"\bkohte", r"\bjurte",
                      r"\bschwarzzelt", r"\bseilbr[üu]cke", r"\bpioniertechnik", r"\bspierbau",
                      r"\bstangen und seile?", r"\bbiwak", r"\blagerbau"]),
    ("natur", [r"\bbaumart", r"\bb[äa]ume (bestimmen|erkennen)",
               r"\bbl[äa]tter (bestimmen|erkennen|zuordnen)", r"\btierspur",
               r"\bspuren (lesen|deuten|verfolgen)", r"\bkr[äa]uter",
               r"\bpflanzen (bestimmen|erkennen)", r"\bvogelstimme", r"\bsternbild",
               r"\bessbare (pflanzen|beeren|kr[äa]uter)", r"\bnatur-?kim|\bbl[äa]tterkim|\bwaldkim",
               r"\bpilze (bestimmen|erkennen)", r"\banschleich", r"\btarnen\b",
               r"\bnaturmaterial\w* (bestimmen|erkennen|ertasten)"]),
    ("bundeskunde", [r"\bpfadfindergesetz", r"\bwahlspruch", r"\bbaden-powell", r"\bbipi\b",
                     r"\bpfadfindergru[ßs]", r"\bpfadfinderversprechen", r"\bbundesgeschichte",
                     r"\bpfadfindergeschichte", r"\bgilwell", r"\bpfadfindersymbolik",
                     r"pfa\. geschichte", r"unser bund"]),
    ("fahrtentechnik", [r"\brucksack (packen|richtig)", r"\bfahrtenplanung", r"\bfahrtengep[äa]ck",
                        r"\bpackliste", r"\bkochstelle", r"\bhaik\b", r"\bmesserf[üu]hrerschein",
                        r"\bschnitzdiplom", r"\btrampen"]),
]


def bestimme_uebt(element):
    """Liste der Proben, die das Spiel nebenbei übt. Streng - im Zweifel leer."""
    kennzeichen = (element["titel"] + " " + " ".join(element.get("tags") or [])).lower()
    if UEBT_WORTLISTE.search(kennzeichen):
        return []
    heu = UEBT_AUSSCHLUSS.sub(" ", _heu_weit(element))
    return [name for name, muster in UEBT_MUSTER if _treffer(heu, muster)]


# ----------------------------------------------------------------- naehe
# "Kann ich das mit einer neuen Sippe spielen, oder muss die Gruppe sich kennen?"
# (Gilsdorf/Kistner: Kennenlernen -> Warming-up -> Vertrauen -> Kooperation.)
# Die Recherche warnt: die naheliegende Regex auf Berührungswörter (anfassen,
# umarmen, huckepack, tragen, Schoß) trifft rund 190 Spiele - viel zu viele,
# weil "berührt" in jedem Fangspiel steht ("wer berührt wird, ist gefangen") und
# "vorstellen" meistens "sich etwas vorstellen" heißt. Deshalb hier nur enge,
# ausformulierte Wendungen statt einzelner Wortstämme.
# Kern von "hoch" ist die schon vorhandene wirkung "vertrauen".
NAEHE_HOCH_MUSTER = [
    r"\bverbundenen augen", r"\baugen (werden )?verbunden", r"\baugenbinde", r"\baugen zubinden",
    r"\bblind (gef[üu]hrt|f[üu]hren|durch|[üu]ber|zu zweit)", r"\bblindenf[üu]hrung",
    r"\bhuckepack", r"\bauf den r[üu]cken (nehmen|laden)",
    r"\b(auf (den|dem) (arm|armen|r[üu]cken)|von der gruppe|von den anderen) getragen",
    r"\bmassage|\bmassier", r"\bsich (nach hinten )?fallen (lassen|zu lassen)",
    r"\bnach hinten fallen", r"\bauf dem scho[ßs]", r"\bauf den scho[ßs]", r"\bsich anvertrau",
    r"\bpendeln lassen", r"\bvor der (ganzen )?gruppe (etwas )?(vorspiel|vortrag|vorsing|vorf[üu]hr)",
    r"\beinzeln vor die gruppe",
]
NAEHE_LEICHT_MUSTER = [
    r"\bh[äa]nde (halten|fassen|reichen|geben)", r"\bhand (halten|fassen|geben)",
    r"\ban den h[äa]nden (fassen|halten|nehmen)", r"\bh[äa]ndekette", r"\ban der hand (f[üu]hren|nehmen)",
    r"\bnamen (rufen|nennen|sagen|zurufen)", r"\bnamensrunde", r"\bvorstellungsrunde",
    r"\bstellt sich (kurz )?(mit namen )?vor\b", r"\bunterhak|\buntergehakt", r"\barm in arm",
    r"\ban den schultern (fassen|halten)", r"\bauf die schulter (legen|tippen)",
    r"\bk[öo]rperkontakt", r"\bsich (gegenseitig )?ber[üu]hren", r"\bkette bilden",
    r"\bhand auf", r"\br[üu]cken an r[üu]cken",
]


def bestimme_naehe(element):
    """keine | leicht | hoch."""
    tags = set(element.get("tags") or [])
    if "vertrauen" in (element.get("wirkung") or []) or tags & {"Vertrauensspiel", "Vertrauensübung"}:
        return "hoch"
    heu = _heu(element)
    if _treffer(heu, NAEHE_HOCH_MUSTER):
        return "hoch"
    # Namens- und Kennenlernspiele verlangen immer, sich der Gruppe zu zeigen
    if tags & {"Namenslernspiel", "Kennenlernspiel"}:
        return "leicht"
    if _treffer(heu, NAEHE_LEICHT_MUSTER):
        return "leicht"
    return "keine"


def bestimme_weitere_achsen(element, infobox):
    """Die vier Achsen aus der Recherche vom 07.09.2026, nur für Spiele."""
    felder = infobox.get(spielewiki_seitentitel(element)) or {}
    return {
        "platz": bestimme_platz(element, felder.get("ort") or ""),
        "hosensackspiel": bestimme_hosensackspiel(element, felder.get("dauer") or ""),
        "uebt": bestimme_uebt(element),
        "naehe": bestimme_naehe(element),
    }


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


# ----------------------------------------------- Zusammengelegte Dubletten
def wende_zusammenlegung_an(elemente, redaktion):
    """
    Wertet den Redaktions-Schlüssel "zusammengelegt" aus.

    Format in data/redaktion.json:
        {"haupt": "sw-x", "varianten": ["ps-y"], "lizenzen_unvertraeglich": true,
         "grund": "…", "aenderungen": {"ps-y": "eigener Satz"}}

    Wirkung: Das Hauptelement bekommt `varianten` (Liste aus titel, id, aenderung),
    die Varianten bleiben in den Daten, werden aber nie Kern. Gelöscht wird nichts -
    die zweite Reihe ist jederzeit wieder einblendbar.

    LIZENZ: Stehen im Cluster CC BY-SA und CC BY-NC(-SA) nebeneinander
    ("lizenzen_unvertraeglich": true), darf in `varianten` nur Titel und id der
    anderen Fassung stehen. `aenderung` bleibt dann leer - es wandert kein Text
    der anderen Quelle in das Element.

    Fehlt der Schlüssel (der Redaktions-Agent arbeitet noch daran), passiert nichts.
    Gibt (Anzahl Gruppen, Menge der Varianten-IDs, Liste unbekannter IDs) zurück.
    """
    nach_id = {e["id"]: e for e in elemente}
    for element in elemente:
        element.setdefault("varianten", [])

    varianten_ids = set()
    unbekannt = []
    gruppen = 0
    for eintrag in redaktion.get("zusammengelegt", []):
        haupt = nach_id.get(eintrag.get("haupt"))
        if not haupt:
            unbekannt.append(eintrag.get("haupt"))
            continue
        gemischt = bool(eintrag.get("lizenzen_unvertraeglich"))
        aenderungen = eintrag.get("aenderungen") or {}
        liste = []
        for kennung in eintrag.get("varianten") or []:
            variante = nach_id.get(kennung)
            if not variante:
                unbekannt.append(kennung)
                continue
            varianten_ids.add(kennung)
            liste.append({
                "titel": variante["titel"],
                "id": kennung,
                # Bei unverträglichen Lizenzen bleibt das Feld leer.
                "aenderung": "" if gemischt else (aenderungen.get(kennung)
                                                  or eintrag.get("aenderung") or ""),
            })
        if liste:
            # Stabil sortiert und ohne Doppelte, damit mehrfache Läufe dasselbe ergeben
            vorhanden = {v["id"] for v in haupt["varianten"]}
            haupt["varianten"].extend(v for v in liste if v["id"] not in vorhanden)
            haupt["varianten"].sort(key=lambda v: v["id"])
            gruppen += 1
    return gruppen, varianten_ids, unbekannt


# --------------------------------------------------------------- Kernsammlung
# Zwei Reihen statt Löschen: Jedes Element trägt `kern`. Die erste Reihe (true)
# ist die aufgeräumte Sammlung, mit der die App startet; die zweite Reihe (false)
# bleibt vollständig in den Daten und ist über einen Filter erreichbar. Damit ist
# jede Aussortierung umkehrbar - ein Eintrag in data/redaktion.json genügt.
#
# Die Punkte und die Quotenrechnung sind wörtlich aus scripts/analyse.py
# übernommen (dort Teil C, Funktion `punkte` und die Quotenschleifen), damit die
# Prüfung und der Build dasselbe rechnen. Sie stehen hier auf Modulebene, damit
# analyse.py sie später importieren kann statt sie ein zweites Mal zu führen.
ZIEL_KERN = 300          # Zielgröße der Kernsammlung (Prüfdokument Teil C.4)
KERN_MINDESTZAHL = 4     # so viele Spiele behält jede Unterkategorie mindestens
DUENN_ZEICHEN = 300      # Beschreibung kürzer -> "dünn beschrieben"
LANG_SPIEL_MIN = 45      # Spiel dauert länger -> passt schlecht als Baustein

KERN_CORONA = re.compile(r"corona|lockdown|pandemi|videokonferenz|\bzoom\b|\bonline\b", re.IGNORECASE)
KERN_TRINKSPIEL = re.compile(r"trinkspiel|\balkohol|\bbier\b|schnaps|\bwodka\b|betrunken", re.IGNORECASE)
KERN_PARTY = re.compile(r"kindergeburtstag|geburtstagsfeier|\bparty\b|silvester|fasching|karneval",
                        re.IGNORECASE)


def kern_volltext(element):
    """Titel, Kurz, Beschreibung, Tipps, Tags, Themen, Material - wie in analyse.py."""
    teile = [element.get("titel", ""), element.get("kurz", ""), element.get("beschreibung", ""),
             element.get("tipps", "")]
    for feld in ("tags", "themen", "material"):
        wert = element.get(feld) or []
        if isinstance(wert, list):
            teile.extend(str(x) for x in wert)
    return "\n".join(str(t) for t in teile if t)


def kern_punkte(element, in_dublette):
    """
    Was spricht dafür, ein Spiel in die erste Reihe zu nehmen? (aus analyse.py)

    Gibt (Punkte, Begründungen) zurück. Rein aus vorhandenen Feldern gerechnet -
    kein Zufall, keine Reihenfolgeabhängigkeit.
    """
    punkte, warum = 0, []
    kennung = element["id"]
    text = kern_volltext(element)
    if kennung.startswith("eig-"):
        punkte += 3
        warum.append("eigene Sammlung")
    if kennung in in_dublette:
        punkte -= 6
        warum.append("Dublette")
    laenge = len(element.get("beschreibung") or "")
    if laenge >= 700:
        punkte += 2
        warum.append("ausführlich beschrieben")
    elif laenge < DUENN_ZEICHEN:
        punkte -= 2
        warum.append("dünn beschrieben")
    if element.get("altersstufen"):
        punkte += 2
        warum.append("Altersstufe da")
    if (element.get("tipps") or "").strip():
        punkte += 1
        warum.append("Tipps da")
    dauer = element.get("dauer_max") or element.get("dauer_min") or 0
    if 0 < dauer <= 20:
        punkte += 2
        warum.append("kurz genug für einen Slot")
    elif dauer >= LANG_SPIEL_MIN:
        punkte -= 2
        warum.append("zu lang für einen Baustein")
    if not (element.get("material") or []):
        punkte += 2
        warum.append("kein Material")
    elif len(element.get("material") or []) >= 4:
        punkte -= 1
        warum.append("viel Material")
    if element.get("vorbereitung") == "gering":
        punkte += 1
    elif element.get("vorbereitung") == "hoch":
        punkte -= 2
        warum.append("viel Vorbereitung")
    if (element.get("gruppe_min") or 0) >= 15:
        punkte -= 2
        warum.append("braucht große Gruppe")
    if KERN_CORONA.search(text):
        punkte -= 3
        warum.append("Corona/Online")
    if KERN_TRINKSPIEL.search(text) or KERN_PARTY.search(text):
        punkte -= 4
        warum.append("Anlass passt nicht")
    if element.get("ort") == "beides":
        punkte += 1
    if len(element.get("wirkung") or []) >= 1:
        punkte += 1
    return punkte, warum


def kern_quoten(ist, ziel=ZIEL_KERN):
    """
    Verteilt `ziel` Plätze proportional auf die Unterkategorien (aus analyse.py).

    Jede Unterkategorie behält mindestens KERN_MINDESTZAHL Spiele, damit auch
    kleine Spielarten (Reflexion, Verstecken) nicht ganz verschwinden. Danach wird
    so lange feinjustiert, bis die Summe das Ziel trifft: weggenommen wird dort,
    wo der Anteil am größten ist, dazugegeben dort, wo er am kleinsten ist.
    `ist` muss ein Verzeichnis Unterkategorie -> Anzahl in stabiler Reihenfolge sein.
    """
    quote = dict((k, int(max(KERN_MINDESTZAHL, min(v, round(v * ziel / max(1, sum(ist.values())))))))
                 for k, v in ist.items())
    schutz = 0
    while sum(quote.values()) > ziel and schutz < 10000:
        schutz += 1
        kandidat = [x for x in quote if quote[x] > KERN_MINDESTZAHL]
        if not kandidat:
            break
        schluessel = max(kandidat, key=lambda x: (quote[x] / max(1, ist[x]), quote[x]))
        quote[schluessel] -= 1
    schutz = 0
    while sum(quote.values()) < ziel and schutz < 10000:
        schutz += 1
        kandidat = [x for x in quote if quote[x] < ist[x]]
        if not kandidat:
            break
        schluessel = min(kandidat, key=lambda x: (quote[x] / max(1, ist[x]), -ist[x]))
        quote[schluessel] += 1
    return quote


def bestimme_kern(elemente, redaktion, varianten_ids):
    """
    Setzt `kern` für jedes Element.

    - Nicht-Spiele sind immer Kern: davon gibt es so wenige, dass jede Aussortierung
      ein Loch in den Heimabend reißt (Pfadfindertechnik: 77, Musisches: 12).
    - Spiele: Punkte nach kern_punkte, dann je Unterkategorie die besten n laut
      kern_quoten. Sortiert wird nach (-Punkte, entschärfter Titel, id) - bei
      Punktgleichstand entscheidet also der Titel, nie der Zufall oder die
      Lesereihenfolge der Quellen.
    - Zusammengelegte Varianten sind nie Kern.
    - data/redaktion.json ("kern") schlägt alles: {"id": …, "kern": false} nimmt
      ein Spiel heraus, {"id": …, "kern": true} holt es herein, auch gegen die Punkte.

    Gibt (Bericht, unbekannte IDs) zurück.
    """
    nach_id = {e["id"]: e for e in elemente}
    von_hand = {}
    unbekannt = []
    for eintrag in redaktion.get("kern", []):
        if eintrag.get("id") in nach_id:
            von_hand[eintrag["id"]] = bool(eintrag.get("kern"))
        else:
            unbekannt.append(eintrag.get("id"))

    spiele = [e for e in elemente if e["bereich"] == "spiel"]
    # Auch titelgleiche Dubletten zählen als zweite Fassung: die erste Fassung ist
    # die mit der ausführlicheren Beschreibung (eigene Sammlung zuerst).
    in_dublette = set(varianten_ids)
    for gruppe in sorted({tuple(sorted([e["id"]] + list(e.get("dubletten") or [])))
                          for e in elemente if e.get("dubletten")}):
        vorhanden = [i for i in gruppe if i in nach_id]

        def rang(kennung):
            element = nach_id[kennung]
            return (0 if kennung.startswith("eig-") else 1,
                    -len(element.get("beschreibung") or ""),
                    0 if element.get("altersstufen") else 1,
                    0 if (element.get("tipps") or "").strip() else 1,
                    kennung)
        for kennung in sorted(vorhanden, key=rang)[1:]:
            in_dublette.add(kennung)

    bewertet = {}
    for element in spiele:
        bewertet[element["id"]] = kern_punkte(element, in_dublette)[0]

    # Stabile Reihenfolge der Unterkategorien: erst die größte, bei Gleichstand
    # alphabetisch. Damit hängt die Quote nicht an der Lesereihenfolge der Quellen.
    roh = Counter(e.get("unterkategorie") or "(leer)" for e in spiele)
    ist = dict()
    for schluessel in sorted(roh, key=lambda x: (-roh[x], x)):
        ist[schluessel] = roh[schluessel]
    quote = kern_quoten(ist)

    nach_unterkategorie = defaultdict(list)
    for element in spiele:
        nach_unterkategorie[element.get("unterkategorie") or "(leer)"].append(element)

    kern_ids = set()
    for schluessel, liste in nach_unterkategorie.items():
        liste.sort(key=lambda e: (-bewertet[e["id"]], entschaerfe(e["titel"]), e["id"]))
        genommen = 0
        for element in liste:
            if element["id"] in in_dublette:
                continue          # zweite Fassung desselben Spiels: nie Kern
            if genommen >= quote.get(schluessel, 0):
                break
            kern_ids.add(element["id"])
            genommen += 1

    automatisch_spiele = len(kern_ids)
    for element in elemente:
        if element["bereich"] != "spiel":
            element["kern"] = True
        else:
            element["kern"] = element["id"] in kern_ids
        # Handentscheidung schlägt die Automatik - in beide Richtungen
        if element["id"] in von_hand:
            element["kern"] = von_hand[element["id"]]

    bericht = {
        "quote": quote,
        "ist": ist,
        "automatisch_spiele": automatisch_spiele,
        "von_hand": len(von_hand),
        "in_dublette": len(in_dublette),
        "kern_spiele": sum(1 for e in elemente if e["bereich"] == "spiel" and e["kern"]),
        "kern_gesamt": sum(1 for e in elemente if e["kern"]),
    }
    return bericht, unbekannt


# ---------------------------------------------------------------- Prüfung
def pruefe(elemente):
    """Prüft Pflichtfelder und Wertebereiche. Gibt die Liste der Fehler zurück."""
    fehler = []
    gesehen = set()
    gesehen_alle = {e.get("id") for e in elemente}
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
            # Die vier Achsen von 09/2026. Leer heißt "nicht erkennbar" und ist erlaubt.
            if element.get("platz") not in set(PLAETZE) | {""}:
                fehler.append("{}: ungültiger Platz '{}'".format(kennung, element.get("platz")))
            if not isinstance(element.get("hosensackspiel"), bool):
                fehler.append("{}: hosensackspiel ist kein Ja/Nein".format(kennung))
            if not isinstance(element.get("uebt"), list) or set(element.get("uebt") or []) - set(UEBT_WERTE):
                fehler.append("{}: ungültiges uebt {}".format(kennung, element.get("uebt")))
            if element.get("naehe") not in set(NAEHE_WERTE) | {""}:
                fehler.append("{}: ungültige Nähe '{}'".format(kennung, element.get("naehe")))
        else:
            # Listenfelder und Achsen gibt es nur bei Spielen - sonst leer
            for feld in ("platz", "naehe"):
                if element.get(feld) != "":
                    fehler.append("{}: '{}' ist nur bei Spielen gefüllt".format(kennung, feld))
            if element.get("uebt"):
                fehler.append("{}: 'uebt' ist nur bei Spielen gefüllt".format(kennung))
            if element.get("hosensackspiel") is not False:
                fehler.append("{}: 'hosensackspiel' ist nur bei Spielen wahr".format(kennung))
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
        if not isinstance(element.get("kern"), bool):
            fehler.append("{}: kern ist kein Ja/Nein".format(kennung))
        varianten = element.get("varianten")
        if not isinstance(varianten, list):
            fehler.append("{}: varianten ist keine Liste".format(kennung))
        else:
            for variante in varianten:
                if not isinstance(variante, dict) or set(variante) != {"titel", "id", "aenderung"}:
                    fehler.append("{}: Variante hat nicht genau titel/id/aenderung: {}".format(
                        kennung, variante))
                elif variante["id"] not in gesehen_alle:
                    fehler.append("{}: Variante '{}' gibt es nicht".format(kennung, variante["id"]))
        quelle = element.get("quelle") or {}
        for feld in ("name", "autor", "lizenz"):
            if not (quelle.get(feld) or "").strip():
                fehler.append("{}: quelle.{} fehlt".format(kennung, feld))
        if "url" not in quelle:
            fehler.append("{}: quelle.url fehlt".format(kennung))
    return fehler


# ---------------------------------------------------------------- Ausgabe
def statistik(elemente, kern_bericht=None, zusammengelegt=0):
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

    # --- die vier Achsen von 09/2026
    zeige("Spiele nach Platzbedarf:", Counter(
        e["platz"] or "(nicht erkennbar)" for e in spiele))
    zeige("Hosensackspiel (ohne alles, jederzeit):", Counter(
        "ja" if e["hosensackspiel"] else "nein" for e in spiele))
    zeige("Spiele nach geübter Probe (mehrfach):", Counter(
        [u for e in spiele for u in e["uebt"]] or []))
    print("  {:<14}  {:>4}".format("(keine)", sum(1 for e in spiele if not e["uebt"])))
    zeige("Spiele nach Nähe/Körperkontakt:", Counter(
        e["naehe"] or "(nicht erkennbar)" for e in spiele))
    print("\nSpiele ohne erkannte Wirkung: {}, ohne Anforderung: {}".format(
        sum(1 for e in spiele if not e["wirkung"]), sum(1 for e in spiele if not e["anforderung"])))
    zeige("nach Ort:", Counter(e["ort"] for e in elemente))
    zeige("nach Vorbereitung:", Counter(e["vorbereitung"] for e in elemente))
    zeige("nach Slot:", Counter(s for e in elemente for s in e["slots"]))
    zeige("nach Altersstufe:", Counter(
        s for e in elemente for s in (e["altersstufen"] or ["(alle / keine Angabe)"])))
    print("\nohne Material: {}".format(sum(1 for e in elemente if not e["material"])))

    # --- Kernsammlung (erste Reihe) und zusammengelegte Varianten
    kern = [e for e in elemente if e["kern"]]
    print("\n" + "-" * 58)
    print("KERNSAMMLUNG (erste Reihe)  –  {} von {} Elementen".format(len(kern), len(elemente)))
    print("-" * 58)
    zeige("Kern nach Bereich:", Counter(e["bereich"] for e in kern))
    zeige("Kern-Spiele nach Unterkategorie:", Counter(
        e["unterkategorie"] or "(leer)" for e in kern if e["bereich"] == "spiel"))
    print("\nzweite Reihe (kern: false): {} Elemente – bleiben in den Daten"
          .format(len(elemente) - len(kern)))
    print("zusammengelegt: {} Gruppen, {} Varianten (bei {} Hauptelementen als 'varianten')".format(
        zusammengelegt,
        sum(len(e["varianten"]) for e in elemente),
        sum(1 for e in elemente if e["varianten"])))
    if kern_bericht:
        print("davon von Hand entschieden (redaktion.json 'kern'): {}"
              .format(kern_bericht.get("von_hand", 0)))


def main():
    vergeben = set()
    print("Lese Quellen ...")
    elemente = []
    elemente += lade_eigene(vergeben)
    print("  eigene Ideen:        {}".format(len(elemente)))
    vorher = len(elemente)
    elemente += lade_rahmen(vergeben)
    print("  Rahmen und Methoden: {}".format(len(elemente) - vorher))
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

    # Zwei Infobox-Felder des Spielewikis, die der Import nicht ins Schema
    # übernimmt ("Ort" = Platzbedarf, "Dauer" im Originalwortlaut). Fehlen die
    # Rohdaten, bleibt das Verzeichnis leer und "platz" kommt nur aus dem Text.
    infobox = lade_spielewiki_infobox()
    if infobox:
        print("\nSpielewiki-Infobox: Ort/Dauer von {} Seiten gelesen".format(len(infobox)))
    else:
        print("\nHinweis: {} fehlt – 'platz' und 'hosensackspiel' nur aus dem Text."
              .format(SPIELEWIKI_ROH))

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
        # Elemente, die ihre Slots selbst mitbringen (rahmen-und-methoden.json),
        # behalten sie: nur dort steht der Slot "eroeffnung", den slots_fuer()
        # nicht vergeben kann.
        if not element.get("_slots_fest"):
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
                if not element.get("_slots_fest"):
                    element["slots"] = slots_fuer(element["bereich"], element["umfang"],
                                                  element["kategorie"], element["dauer_min"])
            elif eintrag.get("kategorie"):
                element["kategorie"] = eintrag["kategorie"]
        # Die Achsen erst jetzt - nachdem der Bereich endgültig feststeht
        if element["bereich"] == "spiel":
            element.update(bestimme_spielachsen(element))
            element.update(bestimme_weitere_achsen(element, infobox))
        else:
            element.update({"wirkung": [], "modus": "", "sozialform": "",
                            "spielgeraet": [], "anforderung": [],
                            "platz": "", "hosensackspiel": False, "uebt": [], "naehe": ""})
        # Redaktion schlägt die Automatik - auch bei den neuen Achsen. Der
        # vorhandene Mechanismus ("achsen" mit "felder") kann das schon, weil er
        # beliebige Feldnamen durchreicht; er muss nur nach ihnen laufen.
        for feld, wert in bericht.get("achsen", {}).get(element["id"], {}).items():
            element[feld] = wert
        element.pop("element_typ", None)   # ersetzt durch bereich + umfang

    gruppen, getrennt = markiere_dubletten(elemente, redaktion)
    betroffen = sum(1 for e in elemente if e.get("dubletten"))
    print("\nDubletten: {} Gruppen, {} Elemente markiert (nichts gelöscht)"
          .format(gruppen, betroffen))
    if getrennt:
        print("  {} falsche Verknüpfung(en) laut Redaktion wieder gelöst".format(getrennt))

    # Von Hand zusammengelegte Fassungen: das Hauptelement bekommt "varianten",
    # die Varianten bleiben erhalten, kommen aber nie in die erste Reihe.
    gelegt, varianten_ids, unbekannt_zusammen = wende_zusammenlegung_an(elemente, redaktion)
    print("Zusammengelegt (redaktion.json 'zusammengelegt'): {} Gruppen, {} Varianten"
          .format(gelegt, len(varianten_ids)))
    if unbekannt_zusammen:
        print("  ACHTUNG, IDs gibt es nicht (mehr): {}".format(
            ", ".join(str(i) for i in unbekannt_zusammen)))

    # Erste und zweite Reihe festlegen
    kern_bericht, unbekannt_kern = bestimme_kern(elemente, redaktion, varianten_ids)
    print("Kernsammlung: {} Elemente (davon {} Spiele, Ziel {}); zweite Reihe: {}".format(
        kern_bericht["kern_gesamt"], kern_bericht["kern_spiele"], ZIEL_KERN,
        len(elemente) - kern_bericht["kern_gesamt"]))
    if unbekannt_kern:
        print("  ACHTUNG, IDs gibt es nicht (mehr): {}".format(
            ", ".join(str(i) for i in unbekannt_kern)))

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
    # Arbeitsfelder, die nur im Lauf gebraucht werden, gehören nicht in die Ausgabe.
    for element in elemente:
        element.pop("_slots_fest", None)

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

    statistik(elemente, kern_bericht, gelegt)
    print("\nGeschrieben:")
    print("  {}".format(AUSGABE_JSON))
    print("  {}".format(AUSGABE_JS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
