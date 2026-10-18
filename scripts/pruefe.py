#!/usr/bin/env python3
"""
Prüft in einem Lauf, ob die Daten und Skripte des Heimabend-Baukastens in Ordnung sind.

Aufruf (im Repo-Ordner):
    python3 scripts/pruefe.py              # alles, auch zwei Probeläufe von build.py (ca. 10 s)
    python3 scripts/pruefe.py --schnell    # ohne die Probeläufe (ca. 1 s)

Am Ende steht entweder "OK" oder eine Liste der Probleme. Exit-Code 0 = OK, 1 = Probleme.
"Hinweise" sind Auffälligkeiten, die nichts kaputt machen; sie ändern das Ergebnis nicht.

Was geprüft wird:
  1. Skripte    – Python-3.9-Verträglichkeit (Syntax und typische 3.10-Fallen)
  2. Dateien    – jede JSON-Datei in data/ ist lesbares JSON (mit Zeile und Spalte)
  3. Redaktion  – Form von data/redaktion.json, Verweise auf IDs, die es nicht gibt (Waisen)
  4. Sprache    – data/sprache.json: Form, Ausnahme-IDs, Regeln, die nirgends greifen
  5. Elemente   – data/elemente.json gegen data/SCHEMA.md (Pflichtfelder, Wertebereiche,
                  ID-Eindeutigkeit, Dubletten und Varianten, Lizenzen, Links)
  6. Web-Datei  – web/elemente.js enthält dieselben Elemente wie data/elemente.json
  7. Build      – zwei Probeläufe von build.py in ein Temp-Verzeichnis: gleiches Ergebnis
                  (idempotent) und gleich wie die eingecheckte data/elemente.json

Nur Standardbibliothek, läuft ab Python 3.9.
"""
import argparse
import ast
import contextlib
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

SKRIPTE = Path(__file__).resolve().parent
STANDARD_WURZEL = SKRIPTE.parent
sys.path.insert(0, str(SKRIPTE))

import build  # noqa: E402  (nutzt die Wertebereiche und pruefe() von build.py mit)


# ---------------------------------------------------------------- Meldungen
class Bericht:
    """Sammelt Probleme (fehler) und Auffälligkeiten (hinweise) je Abschnitt."""

    def __init__(self):
        self.abschnitte = []        # (titel, [fehler], [hinweise])
        self._aktuell = None

    def abschnitt(self, titel):
        self._aktuell = (titel, [], [])
        self.abschnitte.append(self._aktuell)

    def fehler(self, text):
        self._aktuell[1].append(text)

    def hinweis(self, text):
        self._aktuell[2].append(text)

    def anzahl_fehler(self):
        return sum(len(a[1]) for a in self.abschnitte)

    def ausgeben(self, ausfuehrlich_ab=25):
        print()
        for titel, fehler, hinweise in self.abschnitte:
            marke = "ok     " if not fehler else "FEHLER "
            zusatz = ""
            if fehler:
                zusatz += "  ({} Problem{})".format(len(fehler), "" if len(fehler) == 1 else "e")
            if hinweise:
                zusatz += "  ({} Hinweis{})".format(len(hinweise), "" if len(hinweise) == 1 else "e")
            print("{} {}{}".format(marke, titel, zusatz))
            for zeile in fehler[:ausfuehrlich_ab]:
                print("    - {}".format(zeile))
            if len(fehler) > ausfuehrlich_ab:
                print("    ... und {} weitere".format(len(fehler) - ausfuehrlich_ab))
            for zeile in hinweise[:10]:
                print("    . {}".format(zeile))
            if len(hinweise) > 10:
                print("    . ... und {} weitere Hinweise".format(len(hinweise) - 10))
        print()
        n = self.anzahl_fehler()
        if n == 0:
            print("OK")
        else:
            print("{} PROBLEM{} gefunden – siehe oben.".format(n, "" if n == 1 else "E"))


def lade(pfad, bericht, pflicht=True):
    """JSON lesen; bei Fehler Meldung im Bericht und None zurück."""
    if not pfad.exists():
        if pflicht:
            bericht.fehler("{}: Datei fehlt.".format(pfad))
        return None
    try:
        return build.lade_json(pfad)
    except build.DatenFehler as fehler:
        bericht.fehler(str(fehler))
        return None


# ---------------------------------------------------------------- 1. Skripte
def pruefe_skripte(bericht):
    bericht.abschnitt("Skripte: Python-3.9-Verträglichkeit")
    for pfad in sorted(SKRIPTE.glob("*.py")):
        quelle = pfad.read_text(encoding="utf-8")
        try:
            baum = ast.parse(quelle, filename=str(pfad), feature_version=(3, 9))
        except SyntaxError as fehler:
            bericht.fehler("{}: Zeile {}: {} (Syntax, die erst ab Python 3.10 geht?)".format(
                pfad.name, fehler.lineno, fehler.msg))
            continue
        mit_future = any(
            isinstance(k, ast.ImportFrom) and k.module == "__future__"
            and any(a.name == "annotations" for a in k.names)
            for k in baum.body)
        for knoten in ast.walk(baum):
            # X | Y in Typangaben wird zur Laufzeit ausgewertet und scheitert vor 3.10 –
            # außer mit "from __future__ import annotations".
            if not mit_future and isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                angaben = [a.annotation for a in knoten.args.args + knoten.args.kwonlyargs
                           if a.annotation is not None]
                if knoten.returns is not None:
                    angaben.append(knoten.returns)
                for angabe in angaben:
                    if any(isinstance(k, ast.BinOp) and isinstance(k.op, ast.BitOr)
                           for k in ast.walk(angabe)):
                        bericht.fehler("{}: Zeile {}: 'X | Y' in einer Typangabe geht erst ab Python 3.10."
                                       .format(pfad.name, knoten.lineno))
            if isinstance(knoten, ast.Call):
                if (isinstance(knoten.func, ast.Name) and knoten.func.id == "zip"
                        and any(k.arg == "strict" for k in knoten.keywords)):
                    bericht.fehler("{}: Zeile {}: zip(strict=...) gibt es erst ab Python 3.10."
                                   .format(pfad.name, knoten.lineno))
                if isinstance(knoten.func, ast.Attribute) and knoten.func.attr in (
                        "bit_count", "pairwise"):
                    bericht.fehler("{}: Zeile {}: .{}() gibt es erst ab Python 3.10."
                                   .format(pfad.name, knoten.lineno, knoten.func.attr))
            if isinstance(knoten, ast.Match if hasattr(ast, "Match") else ()):
                bericht.fehler("{}: Zeile {}: match/case geht erst ab Python 3.10."
                               .format(pfad.name, knoten.lineno))
    if sys.version_info < (3, 9):
        bericht.fehler("Dieser Prüfer läuft ab Python 3.9, gefunden: {}.{}".format(*sys.version_info[:2]))
    bericht.hinweis("geprüft mit Python {}.{}.{} gegen die Sprachversion 3.9".format(*sys.version_info[:3]))


# ---------------------------------------------------------------- 2. Dateien
def pruefe_dateien(bericht, wurzel):
    bericht.abschnitt("Dateien: alles unter data/ ist lesbares JSON")
    n = 0
    for pfad in sorted((wurzel / "data").rglob("*.json")):
        if "raw" in pfad.relative_to(wurzel / "data").parts:
            continue                 # Rohdaten sind groß und gehören nicht ins Repo
        n += 1
        lade(pfad, bericht)
    bericht.hinweis("{} JSON-Dateien gelesen".format(n))


# ---------------------------------------------------------------- Hilfen
def quell_ids():
    """
    Alle IDs, die die Quellen vor der Redaktion liefern (also auch die gesperrten).
    Nutzt die Lader von build.py, ohne deren Ausgabe zu zeigen.
    """
    vergeben = set()
    elemente = []
    with contextlib.redirect_stdout(io.StringIO()):
        elemente += build.lade_eigene(vergeben)
        elemente += build.lade_rahmen(vergeben)
        elemente += build.lade_meine_ideen(vergeben)
        elemente += build.lade_probenbuch(vergeben)
        elemente += build.lade_inspirator(vergeben)
        for pfad in (build.PFADFINDER_SPIELE, build.SPIELEWIKI):
            for element in build.lade_import(pfad):
                if element["id"] in vergeben:
                    element["id"] = build.mache_id(element["id"].split("-")[0], element["titel"], vergeben)
                else:
                    vergeben.add(element["id"])
                elemente.append(element)
    return {e["id"] for e in elemente}


# ---------------------------------------------------------------- 3. Redaktion
def pruefe_redaktion(bericht, wurzel, elemente_ids, quell_id_menge):
    bericht.abschnitt("Redaktion: data/redaktion.json (Form, Waisen)")
    redaktion = lade(wurzel / "data" / "redaktion.json", bericht, pflicht=False)
    if redaktion is None:
        return None
    for text in build.formfehler_redaktion(redaktion):
        bericht.fehler(text)
    if bericht.abschnitte[-1][1]:
        return None                  # bei kaputter Form lässt sich nichts Sinnvolles zählen

    gesperrt = {e["id"] for e in redaktion.get("gesperrt", [])}
    sicher_da = quell_id_menge if quell_id_menge is not None else elemente_ids | gesperrt

    # Waisen: Verweise auf IDs, die es nirgends gibt
    def verweis(schluessel, kennung, wo):
        if kennung in gesperrt and schluessel != "gesperrt":
            bericht.fehler("'{}': {} verweist auf das gesperrte Element {} – der Eintrag greift nie."
                           .format(schluessel, wo, kennung))
        elif kennung not in sicher_da:
            bericht.fehler("'{}': {} verweist auf {}, das es in keiner Quelle gibt (Waise)."
                           .format(schluessel, wo, kennung))

    for e in redaktion.get("gesperrt", []):
        verweis("gesperrt", e["id"], "Eintrag")
        if e["id"] in elemente_ids:
            bericht.fehler("'gesperrt': {} steht trotz Sperre in data/elemente.json – build.py neu laufen lassen."
                           .format(e["id"]))
    for schluessel in ("umbenannt", "korrekturen", "bereiche", "achsen", "kern"):
        for e in redaktion.get(schluessel, []):
            verweis(schluessel, e["id"], "Eintrag")
    for schluessel in ("keine_dublette", "auch_dublette"):
        for e in redaktion.get(schluessel, []):
            if not isinstance(e["ids"], list) or len(e["ids"]) < 2:
                bericht.fehler("'{}': 'ids' braucht eine Liste mit mindestens zwei IDs: {}".format(schluessel, e["ids"]))
                continue
            for kennung in e["ids"]:
                verweis(schluessel, kennung, "Eintrag " + "/".join(e["ids"]))
    for e in redaktion.get("zusammengelegt", []):
        verweis("zusammengelegt", e["haupt"], "Hauptelement")
        if not isinstance(e["varianten"], list) or not e["varianten"]:
            bericht.fehler("'zusammengelegt': {} hat keine Varianten.".format(e["haupt"]))
            continue
        for kennung in e["varianten"]:
            verweis("zusammengelegt", kennung, "Variante von " + e["haupt"])
        if e["haupt"] in e["varianten"]:
            bericht.fehler("'zusammengelegt': {} ist sein eigener Variant.".format(e["haupt"]))
        for kennung in (e.get("aenderungen") or {}):
            if kennung not in e["varianten"]:
                bericht.fehler("'zusammengelegt': aenderungen nennt {}, das keine Variante von {} ist."
                               .format(kennung, e["haupt"]))
        if e.get("lizenzen_unvertraeglich") and any((e.get("aenderungen") or {}).values()):
            bericht.fehler("'zusammengelegt': {} ist als lizenzen_unvertraeglich markiert, hat aber einen "
                           "aenderung-Text – dort darf nichts aus der anderen Quelle stehen.".format(e["haupt"]))

    # doppelte Einträge, Begründungen, Wertebereiche
    for schluessel, feld in (("umbenannt", "id"), ("korrekturen", "id"), ("bereiche", "id"),
                             ("achsen", "id"), ("kern", "id"), ("gesperrt", "id")):
        # (zusammengelegt darf dasselbe Hauptelement mehrfach nennen: build.py führt die Gruppen zusammen)
        zaehler = Counter(e[feld] for e in redaktion.get(schluessel, []))
        for kennung, anzahl in zaehler.items():
            if anzahl > 1:
                bericht.fehler("'{}': {} steht {}-mal drin – der spätere Eintrag überschreibt den früheren."
                               .format(schluessel, kennung, anzahl))
    alle_varianten = Counter(k for e in redaktion.get("zusammengelegt", []) for k in e["varianten"])
    haupt_menge = {e["haupt"] for e in redaktion.get("zusammengelegt", [])}
    for kennung, anzahl in alle_varianten.items():
        if anzahl > 1:
            bericht.fehler("'zusammengelegt': {} ist Variante in {} Gruppen.".format(kennung, anzahl))
        if kennung in haupt_menge:
            bericht.fehler("'zusammengelegt': {} ist zugleich Hauptelement und Variante.".format(kennung))
    for schluessel in ("gesperrt", "umbenannt", "korrekturen", "bereiche", "keine_dublette",
                       "auch_dublette", "zusammengelegt", "kern", "achsen"):
        for e in redaktion.get(schluessel, []):
            if not str(e.get("grund") or "").strip():
                bericht.fehler("'{}': Eintrag {} hat keine Begründung ('grund').".format(
                    schluessel, e.get("id") or e.get("haupt") or e.get("ids")))
    for e in redaktion.get("bereiche", []):
        if e["bereich"] not in build.BEREICHE:
            bericht.fehler("'bereiche': {} hat den unbekannten Bereich '{}'.".format(e["id"], e["bereich"]))
        elif e.get("kategorie") and e["kategorie"] not in build.KATEGORIEN[e["bereich"]]:
            bericht.fehler("'bereiche': {}: Kategorie '{}' passt nicht zum Bereich '{}'.".format(
                e["id"], e["kategorie"], e["bereich"]))
    for e in redaktion.get("kern", []):
        if not isinstance(e["kern"], bool):
            bericht.fehler("'kern': {}: 'kern' muss true oder false sein.".format(e["id"]))
    erlaubt = set(build.PFLICHTFELDER) | {"gruppe_min", "gruppe_max", "alter_ab"}
    for e in redaktion.get("achsen", []):
        if not isinstance(e["felder"], dict):
            bericht.fehler("'achsen': {}: 'felder' muss ein Objekt sein.".format(e["id"]))
            continue
        for feld in e["felder"]:
            if feld not in erlaubt:
                bericht.fehler("'achsen': {}: Feld '{}' gibt es im Schema nicht.".format(e["id"], feld))
    for e in redaktion.get("korrekturen", []):
        felder = e.get("felder") or {}
        if not isinstance(felder, dict):
            bericht.fehler("'korrekturen': {}: 'felder' muss ein Objekt sein.".format(e["id"]))
            continue
        for feld in felder:
            if feld == "element_typ":
                bericht.hinweis("'korrekturen': {} setzt das alte Feld 'element_typ' – build.py wirft es am Ende "
                                "weg, der Eintrag bewirkt nichts.".format(e["id"]))
            elif feld not in erlaubt:
                bericht.fehler("'korrekturen': {}: Feld '{}' gibt es im Schema nicht.".format(e["id"], feld))
    if quell_id_menge is None:
        bericht.hinweis("Quellen konnten nicht gelesen werden; Waisen nur gegen data/elemente.json geprüft")
    n = sum(len(v) for k, v in redaktion.items() if isinstance(v, list))
    bericht.hinweis("{} Einträge in {} Gruppen geprüft".format(
        n, sum(1 for v in redaktion.values() if isinstance(v, list))))
    return redaktion


# ---------------------------------------------------------------- 4. Sprache
BUCHSTABE = "A-Za-zÄÖÜäöüß"


def pruefe_sprache(bericht, pfad, elemente):
    bericht.abschnitt("Sprache: {}".format(pfad.name))
    if not pfad.exists():
        bericht.hinweis("{} fehlt – die App zeigt dann die Originaltexte (erlaubt).".format(pfad))
        return
    daten = lade(pfad, bericht)
    if daten is None:
        return
    if not isinstance(daten, dict) or not isinstance(daten.get("regeln"), list):
        bericht.fehler("oberste Ebene braucht ein Objekt mit der Liste 'regeln'.")
        return
    meta = daten.get("meta") or {}
    ids = {e["id"] for e in elemente}
    felder = meta.get("felder") or ["titel", "kurz", "beschreibung", "tipps", "tags", "themen", "material"]
    praefixe = tuple(meta.get("ausser_praefixe") or ())
    for feld in felder:
        if feld not in build.PFLICHTFELDER and feld not in ("tipps",):
            bericht.fehler("meta.felder nennt '{}', das es im Schema nicht gibt.".format(feld))
    for praefix in praefixe:
        if not praefix.endswith("-"):
            bericht.fehler("meta.ausser_praefixe: '{}' endet nicht auf '-'.".format(praefix))

    def texte(element):
        for feld in felder:
            wert = element.get(feld)
            if feld == "varianten":
                continue
            if isinstance(wert, str):
                yield wert
            elif isinstance(wert, list):
                for x in wert:
                    if isinstance(x, str):
                        yield x
    betroffen = [e for e in elemente if not e["id"].startswith(praefixe)]
    korpus = "\n".join(t for e in betroffen for t in texte(e))
    gesehen_von = {}
    tote = []
    anzahl_regeln = 0
    for nr, regel in enumerate(daten["regeln"], 1):
        name = regel.get("name", "Regel {}".format(nr)) if isinstance(regel, dict) else "Regel {}".format(nr)
        if not isinstance(regel, dict) or not isinstance(regel.get("woerter"), list):
            bericht.fehler("Regel '{}': braucht eine Liste 'woerter'.".format(name))
            continue
        if not isinstance(regel.get("hinweis_noetig"), bool):
            bericht.fehler("Regel '{}': 'hinweis_noetig' muss true oder false sein.".format(name))
        ausnahmen = regel.get("ausser") or []
        if not isinstance(ausnahmen, list):
            bericht.fehler("Regel '{}': 'ausser' muss eine Liste sein.".format(name))
            ausnahmen = []
        for kennung in ausnahmen:
            if kennung not in ids:
                bericht.fehler("Regel '{}': 'ausser' nennt {}, das es nicht gibt (Waise).".format(name, kennung))
        if ausnahmen and not str(regel.get("ausser_grund") or "").strip():
            bericht.fehler("Regel '{}': 'ausser' hat keinen 'ausser_grund'.".format(name))
        for paar in regel["woerter"]:
            anzahl_regeln += 1
            if (not isinstance(paar, dict) or not isinstance(paar.get("von"), str)
                    or not isinstance(paar.get("zu"), str) or not paar["von"].strip()
                    or not paar["zu"].strip()):
                bericht.fehler("Regel '{}': jedes Paar braucht nicht-leere Texte 'von' und 'zu': {}".format(name, paar))
                continue
            von = paar["von"]
            if von == paar["zu"]:
                bericht.fehler("Regel '{}': '{}' wird durch sich selbst ersetzt.".format(name, von))
            if von in gesehen_von and gesehen_von[von] != paar["zu"]:
                bericht.fehler("'{}' hat zwei verschiedene Ersetzungen ('{}' in '{}' und '{}' in '{}')."
                               .format(von, gesehen_von[von], "früher", paar["zu"], name))
            gesehen_von[von] = paar["zu"]
            muster = re.compile(r"(?<![{b}]){v}(?![{b}])".format(b=BUCHSTABE, v=re.escape(von)))
            if not muster.search(korpus):
                tote.append("{} (Regel '{}')".format(von, name))
    for eintrag in tote:
        bericht.hinweis("greift in keinem Element: '{}' – Tippfehler oder überflüssig?".format(eintrag))
    bericht.hinweis("{} Regeln in {} Gruppen geprüft".format(anzahl_regeln, len(daten["regeln"])))


# ---------------------------------------------------------------- 5. Elemente
ID_MUSTER = re.compile(r"^(eig|mein|insp|ps|sw|pb)-[a-z0-9]+(-[a-z0-9]+)*$")
LIZENZ_JE_PRAEFIX = {
    "sw": "CC BY-SA 4.0",
    "ps": "CC BY-NC-SA 4.0",
    "insp": "CC BY-NC 4.0",
    "eig": "CC BY-SA 4.0",
}
URL_PFLICHT = {"sw", "ps", "insp"}
LISTEN_VON_TEXT = ["slots", "altersstufen", "wirkung", "spielgeraet", "anforderung", "uebt",
                   "material", "tags", "themen", "dubletten"]
TEXTFELDER = ["titel", "kurz", "beschreibung", "tipps"]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
NACKTE_URL = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)


def url_fehler(url):
    """Gibt einen Grund zurück, warum die Adresse kaputt ist, sonst None."""
    if not url or url != url.strip():
        return "leer oder mit Leerzeichen am Rand"
    if re.search(r"\s", url):
        return "enthält Leerzeichen"
    if not re.match(r"^https?://", url, re.IGNORECASE):
        return "beginnt nicht mit http:// oder https://"
    rest = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
    wirt = re.split(r"[/?#]", rest, maxsplit=1)[0]
    if "." not in wirt or wirt.startswith(".") or wirt.endswith(".") or ".." in wirt:
        return "Rechnername '{}' sieht kaputt aus".format(wirt)
    if re.search(r"[<>\"{}|\\^`]", url):
        return "enthält unerlaubte Zeichen"
    return None


def pruefe_schema_doku(bericht, schema_text):
    """Jeder Wert, den build.py erlaubt, muss in data/SCHEMA.md vorkommen."""
    mengen = {
        "wirkung": build.WIRKUNGEN, "modus": build.MODI, "sozialform": build.SOZIALFORMEN,
        "spielgeraet": build.SPIELGERAETE, "anforderung": build.ANFORDERUNGEN,
        "platz": build.PLAETZE, "naehe": build.NAEHE_WERTE, "uebt": build.UEBT_WERTE,
        "bereich": build.BEREICHE, "umfang": sorted(build.UMFAENGE),
        "ort": sorted(build.ORTE), "vorbereitung": sorted(build.VORBEREITUNGEN),
        "slots": sorted(build.SLOTS), "altersstufen": sorted(build.ALTERSSTUFEN),
        "kategorie (spiel)": sorted(build.KATEGORIEN_SPIEL),
        "kategorie (pfadfindertechnik)": sorted(build.KATEGORIEN_PROBE),
        "unterkategorie": [k for k, _ in build.UNTERKATEGORIE_SPIEL] + ["sonstiges"],
    }
    for feld, werte in mengen.items():
        for wert in werte:
            if not re.search(r"(?<![\w])" + re.escape(wert) + r"(?![\w])", schema_text):
                bericht.fehler("build.py erlaubt {} = '{}', aber data/SCHEMA.md nennt den Wert nicht."
                               .format(feld, wert))


def pruefe_elemente(bericht, wurzel, elemente, redaktion):
    bericht.abschnitt("Elemente: data/elemente.json gegen data/SCHEMA.md")
    schema = wurzel / "data" / "SCHEMA.md"
    if schema.exists():
        pruefe_schema_doku(bericht, schema.read_text(encoding="utf-8"))
    else:
        bericht.fehler("data/SCHEMA.md fehlt.")

    # 1) Die Prüfung, die build.py selbst vor dem Schreiben macht (Pflichtfelder, Wertebereiche, Dauer ...)
    for text in build.pruefe(elemente):
        bericht.fehler(text)

    ids = Counter(e.get("id") for e in elemente)
    nach_id = {e.get("id"): e for e in elemente}
    unterkategorien = {k for k, _ in build.UNTERKATEGORIE_SPIEL} | {"sonstiges"}   # Rückfallwert
    for e in elemente:
        k = e.get("id", "<ohne id>")
        praefix = k.split("-")[0] if isinstance(k, str) else ""
        if not isinstance(k, str) or not ID_MUSTER.match(k):
            bericht.fehler("{}: ID hat nicht die Form <Quelle>-<kleinbuchstaben-mit-bindestrich>.".format(k))
        quelle = e.get("quelle") if isinstance(e.get("quelle"), dict) else {}
        erwartet = LIZENZ_JE_PRAEFIX.get(praefix)
        if erwartet and quelle.get("lizenz") != erwartet:
            bericht.fehler("{}: Lizenz '{}' passt nicht zum Präfix '{}-' (erwartet '{}')."
                           .format(k, quelle.get("lizenz"), praefix, erwartet))
        if praefix == "pb" and "Erlaubnis" not in str(quelle.get("lizenz")):
            bericht.fehler("{}: Probenbuch-Elemente brauchen den Hinweis auf die Erlaubnis des Rechteinhabers.".format(k))
        url = quelle.get("url", "")
        if praefix in URL_PFLICHT or url:
            grund = url_fehler(url)
            if grund:
                bericht.fehler("{}: quelle.url '{}' ist kaputt: {}.".format(k, url, grund))
        # Listen von Texten
        for feld in LISTEN_VON_TEXT:
            wert = e.get(feld)
            if wert is None:
                continue
            if not isinstance(wert, list) or not all(isinstance(x, str) for x in wert):
                bericht.fehler("{}: '{}' muss eine Liste von Texten sein.".format(k, feld))
            elif feld != "tags" and len(set(wert)) != len(wert):
                bericht.hinweis("{}: '{}' enthält Doppelte.".format(k, feld))
        for feld in TEXTFELDER:
            if not isinstance(e.get(feld), str):
                bericht.fehler("{}: '{}' muss ein Text sein.".format(k, feld))
        # Spiel: Unterkategorie
        if e.get("bereich") == "spiel" and e.get("unterkategorie") not in unterkategorien:
            bericht.fehler("{}: unterkategorie '{}' ist keine der 22 Werte aus SCHEMA.md.".format(
                k, e.get("unterkategorie")))
        if e.get("bereich") != "spiel" and e.get("unterkategorie") not in ("",):
            bericht.fehler("{}: unterkategorie ist nur bei Spielen gefüllt ('{}').".format(k, e.get("unterkategorie")))
        if e.get("bereich") != "spiel":
            for feld in ("wirkung", "spielgeraet", "anforderung"):
                if e.get(feld):
                    bericht.fehler("{}: '{}' ist nur bei Spielen gefüllt.".format(k, feld))
            for feld in ("modus", "sozialform"):
                if e.get(feld) != "":
                    bericht.fehler("{}: '{}' ist nur bei Spielen gefüllt.".format(k, feld))
        # Slots: eroeffnung gibt es nur bei den Rahmen-Elementen
        if "eroeffnung" in (e.get("slots") or []) and praefix not in ("eig", "mein"):
            bericht.fehler("{}: Slot 'eroeffnung' kommt nur bei eigenen Elementen vor.".format(k))
        # Zahlen
        for feld in ("gruppe_min", "gruppe_max", "alter_ab"):
            if feld in e and (not isinstance(e[feld], int) or isinstance(e[feld], bool) or e[feld] < 0):
                bericht.fehler("{}: '{}' muss eine ganze Zahl >= 0 sein ({!r}).".format(k, feld, e[feld]))
        if (isinstance(e.get("gruppe_min"), int) and isinstance(e.get("gruppe_max"), int)
                and e["gruppe_min"] > e["gruppe_max"]):
            bericht.fehler("{}: gruppe_min {} ist größer als gruppe_max {}.".format(k, e["gruppe_min"], e["gruppe_max"]))
        if isinstance(e.get("dauer_max"), int) and e["dauer_max"] > 600:
            bericht.hinweis("{}: dauer_max {} Minuten ist sehr lang.".format(k, e["dauer_max"]))
        if isinstance(e.get("titel"), str) and e["titel"] != e["titel"].strip():
            bericht.fehler("{}: Titel hat Leerzeichen am Rand.".format(k))
        # Personenbezogenes (CLAUDE.md: keine E-Mail-Adressen aus Quellen)
        for feld in TEXTFELDER:
            if isinstance(e.get(feld), str):
                for treffer in EMAIL.findall(e[feld]):
                    bericht.fehler("{}: E-Mail-Adresse im Feld '{}': {} (keine personenbezogenen Daten übernehmen)."
                                   .format(k, feld, treffer))
        # Links in den Texten
        for feld in ("kurz", "beschreibung", "tipps"):
            text = e.get(feld)
            if not isinstance(text, str):
                continue
            for beschriftung, ziel in MD_LINK.findall(text):
                grund = url_fehler(ziel.strip())
                if grund:
                    bericht.fehler("{}: Link [{}]({}) in '{}' ist kaputt: {}.".format(
                        k, beschriftung[:30], ziel[:60], feld, grund))
            ohne_md = MD_LINK.sub("", text)
            for roh in NACKTE_URL.findall(ohne_md):
                url = roh.rstrip(".,;:!?")
                grund = url_fehler(url)
                if grund:
                    bericht.fehler("{}: Adresse '{}' in '{}' ist kaputt: {}.".format(k, url[:60], feld, grund))
        # Dubletten: gegenseitig und vorhanden
        for d in e.get("dubletten") or []:
            if d not in nach_id:
                bericht.fehler("{}: Dublette {} gibt es nicht.".format(k, d))
            elif k not in (nach_id[d].get("dubletten") or []):
                bericht.fehler("{}: Dublette {} verweist nicht zurück.".format(k, d))
            elif d == k:
                bericht.fehler("{}: ist seine eigene Dublette.".format(k))
        # Varianten: vorhanden, nie Kern, Lizenzfamilie
        for v in e.get("varianten") or []:
            vid = v.get("id") if isinstance(v, dict) else None
            ziel = nach_id.get(vid)
            if ziel is None:
                continue                         # meldet build.pruefe() schon
            if ziel.get("kern") is not False:
                bericht.fehler("{}: Variante {} muss kern=false sein.".format(k, vid))
            if lizenzfamilie(ziel) != lizenzfamilie(e) and str(v.get("aenderung") or "").strip():
                bericht.fehler("{}: Variante {} hat eine andere Lizenzfamilie, aber einen 'aenderung'-Text – "
                               "es darf kein Text der anderen Quelle wandern.".format(k, vid))
            if v.get("titel") != ziel.get("titel"):
                bericht.hinweis("{}: Variante {} heißt dort '{}', hier '{}'.".format(
                    k, vid, ziel.get("titel"), v.get("titel")))

    for kennung, anzahl in ids.items():
        if anzahl > 1:
            bericht.fehler("{}: ID {}-mal vergeben.".format(kennung, anzahl))
    # Redaktion wirkt sich aus
    if redaktion:
        for eintrag in redaktion.get("kern", []):
            e = nach_id.get(eintrag["id"])
            if e is not None and e.get("kern") != eintrag["kern"]:
                bericht.fehler("{}: redaktion.json setzt kern={}, in den Daten steht {} – build.py neu laufen lassen."
                               .format(eintrag["id"], eintrag["kern"], e.get("kern")))
        for eintrag in redaktion.get("umbenannt", []):
            e = nach_id.get(eintrag["id"])
            if e is not None and e.get("titel") != eintrag["titel"]:
                bericht.fehler("{}: redaktion.json nennt den Titel '{}', in den Daten steht '{}'."
                               .format(eintrag["id"], eintrag["titel"], e.get("titel")))
    bericht.hinweis("{} Elemente geprüft".format(len(elemente)))


def lizenzfamilie(element):
    lizenz = str((element.get("quelle") or {}).get("lizenz") or "")
    if "NC" in lizenz:
        return "nc"
    if "BY-SA" in lizenz:
        return "sa"
    return "sonst"


# ---------------------------------------------------------------- 6. Web-Datei
def pruefe_webdatei(bericht, wurzel, elemente):
    bericht.abschnitt("Web-Datei: web/elemente.js passt zu data/elemente.json")
    pfad = wurzel / "web" / "elemente.js"
    if not pfad.exists():
        bericht.fehler("{} fehlt – 'python3 scripts/build.py' erzeugt sie.".format(pfad))
        return
    text = pfad.read_text(encoding="utf-8")
    anfang = text.find("window.ELEMENTE = ")
    if anfang < 0:
        bericht.fehler("web/elemente.js beginnt nicht mit 'window.ELEMENTE = '.")
        return
    nutzlast = text[anfang + len("window.ELEMENTE = "):].rstrip()
    if not nutzlast.endswith(";"):
        bericht.fehler("web/elemente.js endet nicht mit ';' (abgeschnitten?).")
        return
    try:
        daten = json.loads(nutzlast[:-1])
    except json.JSONDecodeError as fehler:
        bericht.fehler("web/elemente.js: kein gültiges JSON – Zeile {}, Spalte {}: {}".format(
            fehler.lineno, fehler.colno, fehler.msg))
        return
    if daten != elemente:
        a = {e["id"]: e for e in daten}
        b = {e["id"]: e for e in elemente}
        bericht.fehler("web/elemente.js und data/elemente.json sind verschieden ({} vs. {} Elemente, "
                       "{} unterschiedlich) – 'python3 scripts/build.py' laufen lassen.".format(
                           len(a), len(b), sum(1 for i in b if a.get(i) != b[i])))


def pruefe_spracheweb(bericht, wurzel):
    """web/sprache.js (falls vorhanden) muss dieselben Regeln enthalten wie data/sprache.json."""
    js = wurzel / "web" / "sprache.js"
    quelle = wurzel / "data" / "sprache.json"
    if not js.exists() and not quelle.exists():
        return
    if js.exists() and not quelle.exists():
        bericht.fehler("web/sprache.js gibt es, aber data/sprache.json fehlt.")
        return
    if quelle.exists() and not js.exists():
        bericht.hinweis("web/sprache.js fehlt: Per Doppelklick auf index.html läuft die App dann "
                        "ohne Sprachregeln (über einen Webserver geht fetch() auf data/sprache.json).")
        return
    text = js.read_text(encoding="utf-8")
    anfang = text.find("window.SPRACHE = ")
    if anfang < 0 or not text.rstrip().endswith(";"):
        bericht.fehler("web/sprache.js hat nicht die Form 'window.SPRACHE = {...};'.")
        return
    try:
        daten = json.loads(text[anfang + len("window.SPRACHE = "):].rstrip()[:-1])
        original = build.lade_json(quelle)
    except (json.JSONDecodeError, build.DatenFehler) as fehler:
        bericht.fehler("web/sprache.js oder data/sprache.json nicht lesbar: {}".format(fehler))
        return
    if daten != original:
        bericht.fehler("web/sprache.js und data/sprache.json sind verschieden – build.py neu laufen lassen.")


# ---------------------------------------------------------------- 7. Build
def pruefsumme(pfad):
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def pruefe_build(bericht, wurzel):
    bericht.abschnitt("Build: zwei Probeläufe von build.py sind gleich und passen zu data/elemente.json")
    ergebnisse = []
    with tempfile.TemporaryDirectory(prefix="heimabend-pruefe-") as temp:
        for nr in (1, 2):
            ziel = Path(temp) / "lauf{}".format(nr)
            lauf = subprocess.run(
                [sys.executable, str(SKRIPTE / "build.py"), "--ausgabe", str(ziel)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            if lauf.returncode != 0:
                bericht.fehler("build.py (Probelauf {}) endet mit Fehler:\n        {}".format(
                    nr, "\n        ".join(lauf.stdout.strip().splitlines()[-8:])))
                return
            ergebnisse.append((ziel, lauf.stdout))
        for name in ("elemente.json", "elemente.js"):
            if pruefsumme(ergebnisse[0][0] / name) != pruefsumme(ergebnisse[1][0] / name):
                bericht.fehler("{}: zwei Läufe hintereinander ergeben Verschiedenes (nicht idempotent).".format(name))
        fehlen_rohdaten = "ACHTUNG: " in ergebnisse[0][1] and "fehlt – 'platz'" in ergebnisse[0][1]
        for name, ziel_in_repo in (("elemente.json", wurzel / "data" / "elemente.json"),
                                   ("elemente.js", wurzel / "web" / "elemente.js")):
            if pruefsumme(ergebnisse[0][0] / name) != pruefsumme(ziel_in_repo):
                text = ("{} im Repo ist nicht der Stand, den build.py jetzt erzeugt".format(ziel_in_repo.name))
                if fehlen_rohdaten:
                    bericht.hinweis(text + " – kein Wunder: die Spielewiki-Rohdaten fehlen "
                                    "(data/quellen/spielewiki/raw/, .gitignore), 'platz' und "
                                    "'hosensackspiel' kommen dann nur aus dem Text.")
                else:
                    bericht.fehler(text + " – 'python3 scripts/build.py' laufen lassen und committen.")
        if fehlen_rohdaten:
            bericht.hinweis("Spielewiki-Rohdaten fehlen: 'python3 scripts/import_spielewiki.py' holt sie.")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Prüft Daten und Skripte des Heimabend-Baukastens.")
    ap.add_argument("--schnell", action="store_true", help="ohne die Probeläufe von build.py")
    ap.add_argument("--wurzel", default=str(STANDARD_WURZEL),
                    help="Ordner mit data/ und web/ (Standard: dieses Repo). Quellen und Probeläufe "
                         "werden nur im Standard-Repo geprüft.")
    ap.add_argument("--sprache", default=None, help="Pfad zu sprache.json (Standard: data/sprache.json)")
    args = ap.parse_args()
    wurzel = Path(args.wurzel).resolve()
    eigenes_repo = wurzel == STANDARD_WURZEL

    bericht = Bericht()
    pruefe_skripte(bericht)
    pruefe_dateien(bericht, wurzel)

    bericht.abschnitt("Einlesen")
    roh = lade(wurzel / "data" / "elemente.json", bericht)
    elemente = None
    if roh is not None:
        if not isinstance(roh, dict) or not isinstance(roh.get("elemente"), list):
            bericht.fehler("data/elemente.json: erwartet ein Objekt mit der Liste 'elemente'.")
        elif not all(isinstance(e, dict) and isinstance(e.get("id"), str) for e in roh["elemente"]):
            bericht.fehler("data/elemente.json: jedes Element muss ein Objekt mit Text-'id' sein.")
        else:
            elemente = roh["elemente"]
            anzahl = (roh.get("meta") or {}).get("anzahl")
            if anzahl != len(elemente):
                bericht.fehler("data/elemente.json: meta.anzahl ist {}, es sind aber {} Elemente.".format(
                    anzahl, len(elemente)))

    quell = None
    if eigenes_repo:
        try:
            quell = quell_ids()
        except build.DatenFehler as fehler:
            bericht.fehler("Quellen: {}".format(fehler))
        except (KeyError, TypeError, ValueError) as fehler:
            bericht.fehler("Quellen: eine Quelldatei hat nicht die erwartete Form ({}: {}).".format(
                type(fehler).__name__, fehler))
    ids = {e["id"] for e in elemente} if elemente else set()
    redaktion = pruefe_redaktion(bericht, wurzel, ids, quell)
    sprache = Path(args.sprache) if args.sprache else wurzel / "data" / "sprache.json"
    if elemente is not None:
        pruefe_sprache(bericht, sprache, elemente)
        pruefe_elemente(bericht, wurzel, elemente, redaktion)
        pruefe_webdatei(bericht, wurzel, elemente)
        pruefe_spracheweb(bericht, wurzel)
    if eigenes_repo and not args.schnell:
        pruefe_build(bericht, wurzel)
    bericht.ausgeben()
    return 1 if bericht.anzahl_fehler() else 0


if __name__ == "__main__":
    sys.exit(main())
