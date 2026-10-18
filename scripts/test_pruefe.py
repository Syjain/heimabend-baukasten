#!/usr/bin/env python3
"""
Testet den Prüfer scripts/pruefe.py: Er muss saubere Daten durchlassen und jeden
absichtlich eingebauten Fehler finden.

Aufruf:
    python3 scripts/test_pruefe.py

Arbeitet auf einer Kopie von data/ und web/ in einem Temp-Ordner; das Repo bleibt unberührt.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
PRUEFE = WURZEL / "scripts" / "pruefe.py"


class PrueferTest(unittest.TestCase):
    def setUp(self):
        self.temp = Path(tempfile.mkdtemp(prefix="heimabend-test-"))
        (self.temp / "data").mkdir()
        (self.temp / "web").mkdir()
        shutil.copy(WURZEL / "data" / "elemente.json", self.temp / "data" / "elemente.json")
        shutil.copy(WURZEL / "data" / "redaktion.json", self.temp / "data" / "redaktion.json")
        shutil.copy(WURZEL / "data" / "SCHEMA.md", self.temp / "data" / "SCHEMA.md")
        shutil.copy(WURZEL / "web" / "elemente.js", self.temp / "web" / "elemente.js")
        self.elemente = json.loads((self.temp / "data" / "elemente.json").read_text(encoding="utf-8"))
        self.redaktion = json.loads((self.temp / "data" / "redaktion.json").read_text(encoding="utf-8"))

    def tearDown(self):
        shutil.rmtree(self.temp, ignore_errors=True)

    def schreibe_elemente(self, mit_js=True):
        (self.temp / "data" / "elemente.json").write_text(
            json.dumps(self.elemente, ensure_ascii=False, indent=1), encoding="utf-8")
        if mit_js:
            (self.temp / "web" / "elemente.js").write_text(
                "window.ELEMENTE = " + json.dumps(self.elemente["elemente"], ensure_ascii=False) + ";\n",
                encoding="utf-8")

    def schreibe_redaktion(self):
        (self.temp / "data" / "redaktion.json").write_text(
            json.dumps(self.redaktion, ensure_ascii=False, indent=1), encoding="utf-8")

    def pruefe(self):
        lauf = subprocess.run([sys.executable, str(PRUEFE), "--schnell", "--wurzel", str(self.temp)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        return lauf.returncode, lauf.stdout

    def erwarte_fehler(self, teil):
        code, text = self.pruefe()
        self.assertEqual(code, 1, text)
        self.assertIn(teil, text)

    def spiel(self):
        return next(e for e in self.elemente["elemente"] if e["bereich"] == "spiel" and e["id"].startswith("sw-"))

    # ---------------------------------------------------------------- Positiv
    def test_saubere_daten_sind_ok(self):
        code, text = self.pruefe()
        self.assertEqual(code, 0, text)
        self.assertTrue(text.rstrip().endswith("OK"), text)

    # ---------------------------------------------------------------- Dateien
    def test_kaputtes_json_in_redaktion(self):
        pfad = self.temp / "data" / "redaktion.json"
        pfad.write_text(pfad.read_text(encoding="utf-8")[:1500], encoding="utf-8")
        self.erwarte_fehler("kein gültiges JSON")

    def test_redaktion_eintrag_ohne_id(self):
        self.redaktion["umbenannt"].append({"titel": "x", "grund": "y"})
        self.schreibe_redaktion()
        self.erwarte_fehler("Feld 'id' fehlt")

    # ---------------------------------------------------------------- Waisen
    def test_waise_in_redaktion(self):
        self.redaktion["kern"].append({"id": "sw-gibt-es-nicht", "kern": False, "grund": "Test"})
        self.schreibe_redaktion()
        self.erwarte_fehler("sw-gibt-es-nicht")

    def test_waise_in_zusammengelegt(self):
        self.redaktion["zusammengelegt"].append(
            {"haupt": self.spiel()["id"], "varianten": ["ps-gibt-es-nicht"],
             "lizenzen_unvertraeglich": False, "grund": "Test"})
        self.schreibe_redaktion()
        self.erwarte_fehler("ps-gibt-es-nicht")

    def test_waise_in_sprache(self):
        sprache = {"meta": {"felder": ["titel"], "ausser_praefixe": ["pb-"]},
                   "regeln": [{"name": "t", "hinweis_noetig": True, "ausser": ["sw-gibt-es-nicht"],
                               "ausser_grund": "Test", "woerter": [{"von": "Abc", "zu": "Def"}]}]}
        (self.temp / "data" / "sprache.json").write_text(json.dumps(sprache), encoding="utf-8")
        self.erwarte_fehler("sw-gibt-es-nicht")

    # ---------------------------------------------------------------- Schema
    def test_doppelte_id(self):
        self.elemente["elemente"].append(dict(self.spiel()))
        self.elemente["meta"]["anzahl"] = len(self.elemente["elemente"])
        self.schreibe_elemente()
        self.erwarte_fehler("ID doppelt vergeben")

    def test_unbekannter_bereich(self):
        self.spiel()["bereich"] = "zauberei"
        self.schreibe_elemente()
        self.erwarte_fehler("unbekannter Bereich 'zauberei'")

    def test_unbekannter_umfang(self):
        self.spiel()["umfang"] = "riesig"
        self.schreibe_elemente()
        self.erwarte_fehler("unbekannter Umfang 'riesig'")

    def test_unbekannte_achse(self):
        self.spiel()["modus"] = "chaos"
        self.schreibe_elemente()
        self.erwarte_fehler("ungültiger Modus 'chaos'")

    def test_pflichtfeld_fehlt(self):
        del self.spiel()["kurz"]
        self.schreibe_elemente()
        self.erwarte_fehler("Feld 'kurz' fehlt")

    def test_kaputter_link(self):
        self.spiel()["quelle"]["url"] = "htp:/spielewiki"
        self.schreibe_elemente()
        self.erwarte_fehler("quelle.url")

    def test_kaputter_link_im_text(self):
        self.spiel()["tipps"] = "Siehe [hier](www.example.org/seite) dazu."
        self.schreibe_elemente()
        self.erwarte_fehler("ist kaputt")

    def test_email_im_text(self):
        self.spiel()["beschreibung"] += " Fragen an max.mustermann@example.org."
        self.schreibe_elemente()
        self.erwarte_fehler("E-Mail-Adresse")

    def test_falsche_lizenz(self):
        self.spiel()["quelle"]["lizenz"] = "CC BY-NC 4.0"
        self.schreibe_elemente()
        self.erwarte_fehler("passt nicht zum Präfix")

    def test_web_datei_weicht_ab(self):
        self.schreibe_elemente()
        self.elemente["elemente"][0]["titel"] += " geändert"
        self.schreibe_elemente(mit_js=False)
        self.erwarte_fehler("sind verschieden")


if __name__ == "__main__":
    unittest.main(verbosity=2)
