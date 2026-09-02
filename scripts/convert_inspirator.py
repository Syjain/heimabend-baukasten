#!/usr/bin/env python3
"""
Wandelt die Django-Fixtures des DPBM-Heimabend-Inspirators (Repo RobertBagdahn/inspi,
Basis von gruppenstunde.de) in eine saubere, lesbare JSON-Datei um.

Aufruf:
    python3 scripts/convert_inspirator.py <pfad-zum-inspi-repo> [ausgabe.json]

Beispiel:
    git clone https://github.com/RobertBagdahn/inspi /tmp/inspi
    python3 scripts/convert_inspirator.py /tmp/inspi data/quellen/inspirator/inspirator-ideen.json

Was passiert:
- IDs für Stufe, Art, Ort, Jahreszeit, Themen werden zu Klartext aufgelöst
- Dubletten (gleicher Titel, v.a. Testdatensätze) werden entfernt
- E-Mail-Adressen der Autor*innen werden NICHT übernommen (Datenschutz)
- Materiallisten werden angehängt
- Die HTML-Beschreibung bleibt erhalten, zusätzlich gibt es eine Nur-Text-Fassung

Lizenz der Inhalte laut Impressum gruppenstunde.de: CC BY-NC 4.0
(Namensnennung: Heimabend-Inspirator / DPBM + Autor*in). Nicht-kommerziell!
"""
import html
import json
import re
import sys
from pathlib import Path

EXECUTION_TIME = {0: "<30 min", 1: "30 min", 2: "60 min", 3: "90 min", 4: ">90 min"}
EXECUTION_MINUTES = {0: (10, 30), 1: (30, 45), 2: (45, 75), 3: (75, 105), 4: (105, 150)}
DIFFICULTY = {0: "Einfach", 1: "Mittel", 2: "Schwer"}
COSTS = {0: "0 €", 1: "0,50 €", 2: "1,00 €", 3: "2,00 €", 4: ">2,00 €"}
PREPARATION = {0: "keine", 1: "5 min", 2: "30 min", 3: "60 min", 4: ">60 min"}
STATUS = {"1": "Entwurf", "2": "Veröffentlicht", "3": "Archiviert", "4": "Review"}


def load_fixture(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def id_to_name(fixture):
    return {row["pk"]: row["fields"]["name"] for row in fixture}


def html_to_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|li|h\d|div)>", "\n", s, flags=re.I)
    s = re.sub(r"<li[^>]*>", "- ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def main(repo: Path, out: Path):
    md = repo / "data" / "activity" / "master-data"
    td = repo / "data" / "activity" / "test-data"

    topics = id_to_name(load_fixture(md / "1_topic.json"))
    types = id_to_name(load_fixture(md / "2_activity_type_choice.json"))
    levels = id_to_name(load_fixture(md / "3_scout_level_choice.json"))
    units = id_to_name(load_fixture(md / "4_material_unit.json"))
    locations = id_to_name(load_fixture(md / "5_location_choice.json"))
    times = id_to_name(load_fixture(md / "6_time_choice.json"))

    material_names = id_to_name(load_fixture(td / "1_material_name.json"))
    material_items = {}
    for row in load_fixture(td / "4_materialitem.json"):
        f = row["fields"]
        material_items.setdefault(f["activity_id"], []).append(
            {
                "name": material_names.get(f["material_name_id"], "?"),
                "menge": f.get("quantity"),
                "einheit": units.get(f.get("material_unit_id"), ""),
                "pro_teilnehmer": f.get("number_of_participants", 0),
            }
        )

    seen_titles = set()
    ideen = []
    for row in load_fixture(td / "3_activity.json"):
        f = row["fields"]
        title = f["title"].strip()
        if title in seen_titles:
            continue
        seen_titles.add(title)
        ex = int(f.get("execution_time", 0))
        ideen.append(
            {
                "inspirator_id": f["id"],
                "url": f"https://gruppenstunde.de/activity/details/{f['id']}",
                "titel": title,
                "kurz": html_to_text(f.get("summary", "")),
                "beschreibung_html": f.get("description", ""),
                "beschreibung_text": html_to_text(f.get("description", "")),
                "stufen": [levels[i] for i in f.get("scout_levels", []) if i in levels],
                "arten": [types[i] for i in f.get("activity_types", []) if i in types],
                "orte": [locations[i] for i in f.get("locations", []) if i in locations],
                "zeiten": [times[i] for i in f.get("times", []) if i in times],
                "themen": [topics[i] for i in f.get("topics", []) if i in topics],
                "dauer": EXECUTION_TIME.get(ex, "?"),
                "dauer_min": EXECUTION_MINUTES.get(ex, (None, None))[0],
                "dauer_max": EXECUTION_MINUTES.get(ex, (None, None))[1],
                "vorbereitung": PREPARATION.get(int(f.get("preparation_time") or 0), "?"),
                "schwierigkeit": DIFFICULTY.get(int(f.get("difficulty", 0)), "?"),
                "kosten": COSTS.get(int(f.get("costs_rating", 0)), "?"),
                "material": material_items.get(f["id"], []),
                "autor": (f.get("created_by_name") or "").strip() or None,
                "status": STATUS.get(str(f.get("status")), "?"),
                "erstellt": (f.get("created_at") or "")[:10],
                "geaendert": (f.get("updated_at") or "")[:10],
            }
        )

    ideen.sort(key=lambda x: x["inspirator_id"])
    result = {
        "meta": {
            "quelle": "Heimabend-Inspirator (Deutscher Pfadfinder*innenbund Mosaik), heute gruppenstunde.de",
            "quelle_url": "https://gruppenstunde.de/activity/",
            "repo": "https://github.com/RobertBagdahn/inspi (data/activity/test-data/3_activity.json)",
            "lizenz": "CC BY-NC 4.0 (laut Impressum gruppenstunde.de) – nicht-kommerziell, Namensnennung: Heimabend-Inspirator/DPBM + Autor*in",
            "hinweis": "Vor Veröffentlichung in einem eigenen Tool beim DPBM anfragen: inspirator@dpbm.de",
            "anzahl": len(ideen),
            "felder": {
                "stufen": sorted(set(levels.values())),
                "arten": sorted(set(types.values())),
                "orte": sorted(set(locations.values())),
                "zeiten": sorted(set(times.values())),
                "themen": sorted(set(topics.values())),
                "dauer": list(EXECUTION_TIME.values()),
                "vorbereitung": list(PREPARATION.values()),
                "schwierigkeit": list(DIFFICULTY.values()),
                "kosten": list(COSTS.values()),
            },
        },
        "ideen": ideen,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"{len(ideen)} Ideen nach {out} geschrieben")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    repo = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/quellen/inspirator/inspirator-ideen.json")
    main(repo, out)
