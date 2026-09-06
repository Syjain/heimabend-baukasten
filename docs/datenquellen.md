# Datenquellen (Recherche-Stand 02.09.2026)

## Import-Basis (Lizenz erlaubt Übernahme)

| Quelle | Umfang | Lizenz | Zugriff |
|---|---|---|---|
| Spielewiki https://www.spielewiki.org/ | ~632 Spiele, Infobox (Art, Spieleranzahl, Ort, Material, Dauer, Vorbereitung), **kein Altersfeld** | CC BY-SA 4.0 | MediaWiki: XML-Export https://www.spielewiki.org/wiki/Spezial:Exportieren (Kategorie `SpieleWiki:Spiel`) oder API `https://www.spielewiki.org/w/api.php` |
| pfadfinder-spiele.de | ~105 dt. Spiele (115 Posts inkl. EN) | CC BY-NC-SA 4.0 | WP-REST-API `https://pfadfinder-spiele.de/wp-json/wp/v2/posts?per_page=100&page=1` (2 Seiten). ACF-Felder: `spielart[]`, `umgebung[]`, `material[]`, `alter` (int), `ungefahre_dauer` (min), `gruppengrose[]`, `gruppenzusammensetzung[]`, `bekannt_als`. Kategorien: „Gruppenspiele" vs. „Blogbeiträge" (nur Gruppenspiele importieren) |
| Spielereader https://github.com/oliverklee/spielereader | PDF/LaTeX, 7 Kapitel | CC BY-SA 3.0 DE | selektiv, manuell taggen |
| Heimabend-Inspirator (DPBM) | 211 Ideen in `data/quellen/inspirator/` | CC BY-NC 4.0 | liegt bereits im Repo, siehe README dort |
| eigene Ideen | 61 in `data/eigene/` | eigene (Vorschlag CC BY-SA 4.0) | liegt im Repo |
| Scoutopedia https://fr.scoutwiki.org/Catégorie:Jeu | 399 Spiele, 17 Unterkategorien, **französisch** | CC BY-SA 3.0 (+ GFDL) | MediaWiki-API; nur mit Übersetzung sinnvoll, Dubletten mit Spielewiki prüfen – siehe `docs/recherche-spiele-apps-und-quellen.md` |
| Methodenkartei Uni Oldenburg https://www.methodenkartei.uni-oldenburg.de/methoden/ | 202 Schul-/Gruppenmethoden, davon ~50 für Gemeinschaft/Reflexion brauchbar | CC BY (OER-Standard; auf der Einzelseite prüfen) | Webseite, kein Export |
| Baden-Powell, *Scouting for Boys* (1908), Teil VI | ~50 historische Spiele, englisch | gemeinfrei | https://www.gutenberg.org/ebooks/65993 – kuratierte Auswahl mit eigener Übersetzung |
| DPB-Probenbuch, 3. Auflage | 30 Proben (28 mit Text), Stand ca. 2003, ohne Abbildungen | Rechte beim Projektinhaber | `data/quellen/probenbuch/proben-dpb.json`, aus dem PDF extrahiert; siehe README dort |

## Nur mit Erlaubnis (anfragen)
- ejb.vernetzt Spielekatalog https://ejb-vernetzt.de/spielekatalog/ – ~160 Spiele, offene API `https://ejb-vernetzt.de/wp-json/wc/store/v1/products?per_page=100`, keine Lizenzangabe
- Jungschar Wien https://spiele.wien.jungschar.at/ – 300+ Spiele, keine Lizenzangabe
- Scout-o-wiki https://www.scout-o-wiki.de/index.php/Kategorie:Spiel – 40 Spiele, keine Lizenz
- Deutsche Wanderjugend, Spielesammlung (PDF, ~80 Spiele, 2019) – „alle Rechte vorbehalten“
- Jugendverbände München, Spielesammlung von Jugendleitern (PDF, ~38 Spiele, 2016) – keine Lizenzangabe

## Nur verlinken (Übernahme untersagt)
Robert Aehnelt „Spielpädagogisches Inventar“ (CC BY-NC-**ND**, keine Bearbeitung erlaubt), EJW Spielebox, julei-app.de, Fun-for-Groups-App, Pfadiwiki/en.scoutwiki (GFDL, nicht CC-kompatibel), praxis-jugendarbeit.de, gruppenspiele-hits.de, jugendleiter-blog.de, labbe.de/spielotti, super-sozi.de, spielekartei.net, pfadispiele.ch, thepulse.org, groupsenz.org, spielefuerviele.de, jugendarbeit.online, ultimatecampresource.com, youthgroupgames.com.au, scouts.org.uk, playmeo.com

## Lizenz-Konsequenzen
- Pro Element `quelle.lizenz`, `quelle.url`, `quelle.autor` pflegen und in der App anzeigen.
- CC BY-SA und CC BY-NC-SA nicht mischen (nie Texte zweier Quellen in einem Element).
- Mit NC-Inhalten bleibt das Tool nicht-kommerziell.
- Kontakt DPBM: inspirator@dpbm.de
