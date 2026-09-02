#!/usr/bin/env python3
"""
Importiert die Gruppenspiele von pfadfinder-spiele.de über die WordPress-REST-API
und mappt sie auf das Element-Schema aus `data/SCHEMA.md`.

Aufruf:
    python3 scripts/import_pfadfinder_spiele.py             # holt die Daten aus dem Netz
    python3 scripts/import_pfadfinder_spiele.py --offline   # nutzt nur die gespeicherten Rohdaten

Was passiert:
- Alle Seiten von https://pfadfinder-spiele.de/wp-json/wp/v2/posts?per_page=100&page=N werden geholt
- Die Rohantwort landet unverändert in data/quellen/pfadfinder-spiele/raw/posts.json
- Nur Posts der Kategorie "Gruppenspiele" werden übernommen (Blogbeiträge fliegen raus)
- Das HTML der Beschreibung wird zu Text (das Sternebewertungs-Widget wird abgeschnitten)
- Die ACF-Felder (spielart, umgebung, material, alter, ungefahre_dauer, gruppengrose)
  werden nach der Mapping-Tabelle in data/SCHEMA.md ins Element-Schema übersetzt
- Ergebnis: data/quellen/pfadfinder-spiele/elemente.json (wird bei jedem Lauf überschrieben)

Lizenz der Inhalte: CC BY-NC-SA 4.0, Autorin: Dorothea Schümann (pfadfinder-spiele.de).
Nicht-kommerziell! Die einzelnen Autor*innennamen der Posts werden bewusst NICHT
übernommen (Datenschutz, siehe CLAUDE.md).
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

API_URL = "https://pfadfinder-spiele.de/wp-json/wp/v2/posts?per_page=100&page={seite}"
KATEGORIE_URL = "https://pfadfinder-spiele.de/wp-json/wp/v2/categories?per_page=100"
USER_AGENT = (
    "heimabend-baukasten/0.1 (nicht-kommerzielles Pfadfinder-Projekt; "
    "Import unter CC BY-NC-SA 4.0)"
)
PAUSE_SEKUNDEN = 0.5

WURZEL = Path(__file__).resolve().parent.parent
ROHDATEN = WURZEL / "data" / "quellen" / "pfadfinder-spiele" / "raw" / "posts.json"
AUSGABE = WURZEL / "data" / "quellen" / "pfadfinder-spiele" / "elemente.json"

QUELLE = {
    "name": "pfadfinder-spiele.de",
    "autor": "Dorothea Schümann",
    "lizenz": "CC BY-NC-SA 4.0",
}

# spielart -> kategorie, in dieser Reihenfolge geprüft (die erste passende gewinnt).
# Die Reihenfolge folgt dem Beispiel in data/SCHEMA.md: "Kotzendes Känguru" hat
# Konzentrationsspiel + Kreisspiel + Warm up und soll die Kategorie "kreis" bekommen.
KATEGORIE_REIHENFOLGE = [
    ("Geländespiel", "gelaende"),
    ("Kennenlernspiel", "ankommen"),
    ("Kreisspiel", "kreis"),
    ("Kooperationsspiel", "kooperation"),
    ("Vertrauensübung", "kooperation"),
    ("Konzentrationsspiel", "ruhig"),
    ("Warm up", "ankommen"),
    ("Renn- & Fangenspiel", "bewegung"),
    ("Bewegungsspiel", "bewegung"),
    ("Mannschaftsspiel", "bewegung"),
]

# Absätze, die so anfangen, wandern nach "tipps" statt in die Beschreibung.
TIPP_ANFANG = re.compile(r"^(Hinweis|Tipp|Anmerkung|Achtung)\b", re.IGNORECASE)

# Grobe Sprachprüfung: überwiegt Englisch deutlich, ist der Post eine englische Fassung.
ENGLISCHE_WOERTER = re.compile(
    r"\b(the|and|with|players|game|they|are|is|of|to|for|each|other|around)\b",
    re.IGNORECASE,
)
DEUTSCHE_WOERTER = re.compile(
    r"\b(der|die|das|und|mit|Spieler|Spiel|ein|eine|sich|wird|werden|nicht|auf|im|den)\b"
)


# --------------------------------------------------------------------------
# Netz
# --------------------------------------------------------------------------
def hole_json(url):
    """Ruft eine URL ab und gibt die geparste JSON-Antwort zurück."""
    anfrage = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(anfrage, timeout=30) as antwort:
        return json.loads(antwort.read().decode("utf-8"))


def hole_alle_posts():
    """Holt Seite für Seite, bis keine weitere mehr kommt."""
    posts = []
    seite = 1
    while True:
        print("  hole Seite {} ...".format(seite))
        try:
            teil = hole_json(API_URL.format(seite=seite))
        except urllib.error.HTTPError as fehler:
            if fehler.code == 400:  # so meldet WordPress "keine weitere Seite"
                break
            raise
        if not teil:
            break
        posts.extend(teil)
        seite += 1
        time.sleep(PAUSE_SEKUNDEN)
    return posts


def hole_kategorien():
    """Gibt {kategorie_id: name} zurück; bei Netzproblemen ein leeres Dict."""
    try:
        return {k["id"]: k["name"] for k in hole_json(KATEGORIE_URL)}
    except (urllib.error.URLError, ValueError, KeyError):
        return {}


# --------------------------------------------------------------------------
# HTML -> Text
# --------------------------------------------------------------------------
def html_zu_text(roh_html):
    """Wandelt das WordPress-HTML in lesbaren Fließtext um."""
    # Das Sternebewertungs-Widget hängt hinten dran und gehört nicht zum Spiel.
    text = (roh_html or "").split('<div class="kk-star-ratings')[0]
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", text)
    text = re.sub(r"(?i)<li[^>]*>", "\n- ", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|li|ul|ol|h[1-6]|tr)>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace(" ", " ")
    text = "\n".join(zeile.strip() for zeile in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def trenne_tipps(text):
    """Trennt Hinweis-/Tipp-Absätze vom eigentlichen Ablauf ab."""
    absaetze = [a.strip() for a in text.split("\n\n") if a.strip()]
    beschreibung = [a for a in absaetze if not TIPP_ANFANG.match(a)]
    tipps = [a for a in absaetze if TIPP_ANFANG.match(a)]
    return "\n\n".join(beschreibung), "\n\n".join(tipps)


def ist_englisch(text):
    """True, wenn der Text deutlich mehr englische als deutsche Funktionswörter hat."""
    englisch = len(ENGLISCHE_WOERTER.findall(text))
    deutsch = len(DEUTSCHE_WOERTER.findall(text))
    return englisch >= 5 and englisch > deutsch * 2


def normalisiere_titel(titel):
    """Vergleichsform eines Titels (für den Sprach-/Dublettenabgleich)."""
    titel = titel.lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        titel = titel.replace(alt, neu)
    return re.sub(r"[^a-z0-9]+", "", titel)


# --------------------------------------------------------------------------
# Mapping der ACF-Felder auf das Schema
# --------------------------------------------------------------------------
def map_ort(umgebung):
    """umgebung[] -> drinnen | draussen | beides"""
    drinnen = "Drinnen" in umgebung
    draussen = "Draußen" in umgebung
    if drinnen and draussen:
        return "beides"
    if drinnen:
        return "drinnen"
    if draussen:
        return "draussen"
    return "beides"  # nur "Online" o. Ä. -> keine Einschränkung


def map_kategorie(spielart, ort):
    """spielart[] -> eine Kategorie aus dem Schema."""
    for schluessel, kategorie in KATEGORIE_REIHENFOLGE:
        if schluessel in spielart:
            if kategorie == "bewegung":
                return "bewegung_draussen" if ort == "draussen" else "bewegung_drinnen"
            return kategorie
    return "bewegung_draussen" if ort == "draussen" else "bewegung_drinnen"


def map_slots(spielart, kategorie, dauer_min):
    """Wo im Heimabend passt das Spiel? (einstieg | hauptteil | abschluss)"""
    slots = []
    if "Warm up" in spielart or "Kennenlernspiel" in spielart or dauer_min <= 10:
        slots.append("einstieg")
    if dauer_min >= 10:
        slots.append("hauptteil")
    if dauer_min <= 15 and kategorie in ("kreis", "ruhig", "ankommen"):
        slots.append("abschluss")
    return slots or ["hauptteil"]


def map_altersstufen(alter_ab):
    """alter (Mindestalter) -> Altersstufen des Bundes."""
    if not alter_ab:
        return []
    stufen = []
    if alter_ab <= 11:
        stufen.append("Wölflinge")
    if alter_ab <= 16:
        stufen.append("Pfadfinder")
    stufen.append("Ältere")
    return stufen


def auf_fuenf(minuten):
    """Rundet auf volle 5 Minuten."""
    return int(round(minuten / 5.0) * 5)


def map_dauer(ungefahre_dauer):
    """Ein einzelner Minutenwert wird zu einer Spanne (+/- ein Drittel)."""
    try:
        dauer = int(ungefahre_dauer)
    except (TypeError, ValueError):
        return 10, 20
    if dauer <= 0:
        return 10, 20
    minimum = max(5, auf_fuenf(dauer * 2 / 3.0))
    maximum = max(minimum + 5, auf_fuenf(dauer * 4 / 3.0))
    return minimum, maximum


def map_gruppengroesse(gruppengrose):
    """gruppengrose[] ("6 - 25 Personen", "25 und mehr Personen") -> min/max."""
    untergrenzen, obergrenzen = [], []
    offen_nach_oben = False
    for eintrag in gruppengrose or []:
        spanne = re.match(r"\s*(\d+)\s*-\s*(\d+)", eintrag)
        if spanne:
            untergrenzen.append(int(spanne.group(1)))
            obergrenzen.append(int(spanne.group(2)))
            continue
        mehr = re.match(r"\s*(\d+)\s*und mehr", eintrag)
        if mehr:
            untergrenzen.append(int(mehr.group(1)))
            offen_nach_oben = True
    minimum = min(untergrenzen) if untergrenzen else None
    maximum = None if offen_nach_oben or not obergrenzen else max(obergrenzen)
    return minimum, maximum


def map_material(material):
    """material[] -> Liste; "Nichts" bedeutet: kein Material (leere Liste)."""
    return [m for m in (material or []) if m and m.strip().lower() != "nichts"]


def map_vorbereitung(material):
    """
    pfadfinder-spiele.de hat kein Vorbereitungsfeld.
    Heuristik: ohne Material = gering, mit Material = mittel.
    """
    return "mittel" if material else "gering"


def baue_tags(spielart, material, umgebung, bekannt_als):
    """Stichworte für Suche und Filter (inkl. anderer Namen des Spiels)."""
    tags = list(spielart)
    if not material:
        tags.append("ohne Material")
    if "Online" in (umgebung or []):
        tags.append("auch online")
    for name in (bekannt_als or "").split(","):
        name = name.strip()
        if name:
            tags.append(name)
    gesehen, ergebnis = set(), []
    for tag in tags:
        if tag.lower() not in gesehen:
            gesehen.add(tag.lower())
            ergebnis.append(tag)
    return ergebnis


def post_zu_element(post):
    """Baut aus einem WordPress-Post ein Element nach data/SCHEMA.md."""
    acf = post.get("acf") or {}
    titel = html_zu_text(post["title"]["rendered"])
    volltext = html_zu_text(post["content"]["rendered"])
    beschreibung, tipps = trenne_tipps(volltext)
    kurz = html_zu_text(post.get("excerpt", {}).get("rendered", ""))

    spielart = acf.get("spielart") or []
    umgebung = acf.get("umgebung") or []
    material = map_material(acf.get("material"))
    ort = map_ort(umgebung)
    kategorie = map_kategorie(spielart, ort)
    dauer_min, dauer_max = map_dauer(acf.get("ungefahre_dauer"))
    gruppe_min, gruppe_max = map_gruppengroesse(acf.get("gruppengrose"))
    alter_ab = acf.get("alter") or None

    element = {
        "id": "ps-" + post["slug"],
        "titel": titel,
        "element_typ": "spiel",
        "kategorie": kategorie,
        "slots": map_slots(spielart, kategorie, dauer_min),
        "altersstufen": map_altersstufen(alter_ab),
        "dauer_min": dauer_min,
        "dauer_max": dauer_max,
        "ort": ort,
        "material": material,
        "vorbereitung": map_vorbereitung(material),
        "kurz": kurz,
        "beschreibung": beschreibung,
        "tipps": tipps,
        "tags": baue_tags(spielart, material, umgebung, acf.get("bekannt_als")),
        "themen": [],
        "quelle": {
            "name": QUELLE["name"],
            "url": post["link"],
            "autor": QUELLE["autor"],
            "lizenz": QUELLE["lizenz"],
        },
    }
    if alter_ab:
        element["alter_ab"] = int(alter_ab)
    if gruppe_min is not None:
        element["gruppe_min"] = gruppe_min
    if gruppe_max is not None:
        element["gruppe_max"] = gruppe_max
    return element


# --------------------------------------------------------------------------
# Ablauf
# --------------------------------------------------------------------------
def main():
    offline = "--offline" in sys.argv

    if offline:
        if not ROHDATEN.exists():
            print("Keine Rohdaten unter {}".format(ROHDATEN))
            print("Bitte einmal ohne --offline laufen lassen.")
            return 1
        print("Lese Rohdaten aus {}".format(ROHDATEN))
        with open(ROHDATEN, encoding="utf-8") as datei:
            posts = json.load(datei)
        kategorien = {}
    else:
        print("Rufe pfadfinder-spiele.de ab ...")
        posts = hole_alle_posts()
        ROHDATEN.parent.mkdir(parents=True, exist_ok=True)
        with open(ROHDATEN, "w", encoding="utf-8") as datei:
            json.dump(posts, datei, ensure_ascii=False, indent=1)
        print("  {} Posts roh gespeichert: {}".format(len(posts), ROHDATEN))
        kategorien = hole_kategorien()

    # Nur Gruppenspiele, keine Blogbeiträge
    gruppenspiel_ids = {kid for kid, name in kategorien.items() if name == "Gruppenspiele"}
    if not gruppenspiel_ids:
        gruppenspiel_ids = {2}  # Stand 09/2026: "Gruppenspiele" = 2, "Blogbeiträge" = 1
    spiele = [p for p in posts if set(p.get("categories") or []) & gruppenspiel_ids]
    verworfen_kategorie = len(posts) - len(spiele)

    elemente = [post_zu_element(p) for p in spiele]

    # Englische Fassungen weglassen, wenn es dasselbe Spiel auf Deutsch gibt.
    deutsche_titel = {
        normalisiere_titel(e["titel"])
        for e in elemente
        if not ist_englisch(e["beschreibung"])
    }
    behalten, verworfen_englisch = [], []
    for element in elemente:
        if ist_englisch(element["beschreibung"]) and normalisiere_titel(element["titel"]) in deutsche_titel:
            verworfen_englisch.append(element["titel"])
        else:
            behalten.append(element)
    elemente = sorted(behalten, key=lambda e: e["titel"].lower())

    AUSGABE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUSGABE, "w", encoding="utf-8") as datei:
        json.dump(
            {
                "meta": {
                    "quelle": QUELLE["name"],
                    "url": "https://pfadfinder-spiele.de/",
                    "autor": QUELLE["autor"],
                    "lizenz": QUELLE["lizenz"],
                    "hinweis": "Nicht-kommerziell. Erzeugt von scripts/import_pfadfinder_spiele.py.",
                    "anzahl": len(elemente),
                },
                "elemente": elemente,
            },
            datei,
            ensure_ascii=False,
            indent=1,
        )

    print()
    print("Posts gesamt:              {}".format(len(posts)))
    print("davon keine Gruppenspiele: {}".format(verworfen_kategorie))
    print("englische Dubletten raus:  {} {}".format(len(verworfen_englisch), verworfen_englisch or ""))
    print("Elemente geschrieben:      {}  ->  {}".format(len(elemente), AUSGABE))
    print()
    print("Kategorien:    {}".format(dict(Counter(e["kategorie"] for e in elemente).most_common())))
    print("Orte:          {}".format(dict(Counter(e["ort"] for e in elemente).most_common())))
    print("Slots:         {}".format(dict(Counter(s for e in elemente for s in e["slots"]).most_common())))
    print("Vorbereitung:  {}".format(dict(Counter(e["vorbereitung"] for e in elemente).most_common())))
    print("ohne Material: {}".format(sum(1 for e in elemente if not e["material"])))
    print("mit Tipps:     {}".format(sum(1 for e in elemente if e["tipps"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
