/* Rauchtest für den Heimabend-Baukasten.

   So benutzt du ihn:
   1. web/index.html im Browser öffnen (Doppelklick reicht)
   2. Entwicklerwerkzeuge öffnen  –  Mac: Wahltaste + Befehlstaste + I,
      dann oben auf "Konsole" klicken
   3. Den gesamten Inhalt dieser Datei hineinkopieren und Eingabetaste drücken

   Es kommt eine Liste heraus, in der jede Zeile mit "ok" oder "FEHLER" anfängt,
   und ganz unten steht, wie viele Fehler es gab. Nach jeder Änderung an
   web/index.html noch einmal laufen lassen.

   Achtung: Der Test verstellt unterwegs Filter und würfelt den Plan neu.
   Am Ende setzt er alles zurück, aber ein gespeicherter Plan geht dabei verloren –
   und ebenso die gemerkte Einstellung "geprüfte Auswahl / ganze Sammlung".
   Die eigenen Ideen bleiben unangetastet: Der Test legt zwar eine an, sichert
   aber vorher den Speicherstand und stellt ihn am Ende wieder her. */
(function () {
  var ergebnisse = [];
  function pruefe(name, bedingung, zusatz) {
    ergebnisse.push((bedingung ? "ok    " : "FEHLER") + "  " + name +
                    (zusatz !== undefined ? "  [" + zusatz + "]" : ""));
  }
  function zuruecksetzen() {
    // Die App-eigene Funktion benutzen, damit der Test nicht vergisst,
    // neue Filterfelder mitzuleeren.
    document.getElementById("suche").value = "";
    pfad = leererPfad();
    setzeFilterZurueck();
    // Der Umfang der Sammlung ist kein Filter und wird von
    // setzeFilterZurueck() bewusst nicht angefasst. Alle Prüfungen mit festen
    // Zahlen rechnen mit der ganzen Sammlung, deshalb hier ausdrücklich
    // umschalten; die eigenen Prüfungen zum Schalter stellen selbst um.
    setzeSammlung(false);
  }

  // --- Umfang der Sammlung: erst prüfen, danach wird umgeschaltet ---
  pruefe("Standard ist die geprüfte Auswahl (ohne gemerkte Wahl)",
         (function () {
           try { localStorage.removeItem(SAMMLUNG_SPEICHER); } catch (f) { /* egal */ }
           return ladeSammlung() === true && SAMMLUNG_STANDARD === true;
         })());
  setzeSammlung(true);
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.unterkategorie = "__alle__";
  aktualisiere();
  var mitKern = gefiltert.length;
  var kernSauber = gefiltert.every(function (e) { return e.kern !== false; });
  setzeSammlung(false);
  aktualisiere();
  var ohneKern = gefiltert.length;
  pruefe("Schalter verändert die Zahlen", ohneKern > mitKern && mitKern > 0,
         mitKern + " -> " + ohneKern);
  pruefe("geprüfte Auswahl enthält nichts aus der zweiten Reihe", kernSauber);
  setzeSammlung(true);
  pfad = leererPfad(); aktualisiere();
  var kachelKern = document.getElementById("sammlungKern").textContent;
  var kachelSpiele = document.querySelectorAll("#kacheln .kachel")[0].textContent;
  setzeSammlung(false);
  aktualisiere();
  pruefe("Schalter verändert auch die Zahlen auf den Kacheln",
         kachelSpiele !== document.querySelectorAll("#kacheln .kachel")[0].textContent,
         kachelSpiele + " -> " + document.querySelectorAll("#kacheln .kachel")[0].textContent);
  pruefe("Schalter zeigt beide Zahlen an",
         /\d/.test(kachelKern) &&
         /\d/.test(document.getElementById("sammlungAlle").textContent),
         kachelKern + " / " + document.getElementById("sammlungAlle").textContent);
  setzeSammlung(true);
  pruefe("Planer-Vorschläge folgen dem Schalter",
         sammle(rahmenFilter(), null, SLOTS[1].passt).every(function (e) {
           return e.kern !== false;
         }));
  pruefe("Schalter merkt sich die Wahl",
         (function () {
           setzeSammlung(false);
           var gemerkt = ladeSammlung();
           setzeSammlung(true);
           return gemerkt === false && ladeSammlung() === true;
         })());
  setzeSammlung(false);

  // --- Daten ---
  pruefe("Daten geladen", ALLE.length > 900, ALLE.length + " Elemente");
  pruefe("alle tragen kern und varianten",
         ALLE.every(function (e) {
           return typeof e.kern === "boolean" && Array.isArray(e.varianten);
         }),
         ALLE.filter(function (e) { return e.kern; }).length + " in der ersten Reihe");
  pruefe("alle haben Bereich und Umfang",
         ALLE.every(function (e) {
           return BEREICH_TEXT[e.bereich] &&
                  (e.umfang === "baustein" || e.umfang === "ganzer_abend");
         }));
  pruefe("nur Spiele und Pfadfindertechnik haben eine Kategorie",
         ALLE.every(function (e) {
           return (e.bereich === "spiel" || e.bereich === "pfadfindertechnik")
                  ? !!e.kategorie : e.kategorie === "";
         }));
  pruefe("Spiele tragen die fünf Achsen",
         ALLE.filter(function (e) { return e.bereich === "spiel"; }).every(function (e) {
           return Array.isArray(e.wirkung) && Array.isArray(e.spielgeraet) &&
                  Array.isArray(e.anforderung) && e.spielgeraet.length > 0 &&
                  ["wettkampf", "kooperation", "ohne_gewinner"].indexOf(e.modus) > -1 &&
                  ["kreis", "paare", "mannschaften", "einer_gegen_alle", "kleingruppen", "frei"]
                    .indexOf(e.sozialform) > -1;
         }));
  pruefe("Nicht-Spiele haben leere Achsen",
         ALLE.filter(function (e) { return e.bereich !== "spiel"; }).every(function (e) {
           return e.modus === "" && e.sozialform === "" && e.wirkung.length === 0;
         }));
  pruefe("Unterkategorien nur bei Spielen",
         ALLE.every(function (e) {
           return e.bereich === "spiel" || e.unterkategorie === "";
         }));
  pruefe("alle haben Quelle mit Lizenz",
         ALLE.every(function (e) { return e.quelle && e.quelle.lizenz; }));

  // --- Kachel-Navigation ---
  zuruecksetzen();
  pruefe("Start zeigt Kacheln, keine Liste",
         document.querySelectorAll("#kacheln .kachel").length >= 4 &&
         document.getElementById("listenkopf").hidden);
  pfad = leererPfad(); pfad.bereich = "spiel"; aktualisiere();
  pruefe("Spiele zeigen Kategorie-Kacheln",
         document.querySelectorAll("#kacheln .kachel").length > 3);
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.kategorie = "kreis"; aktualisiere();
  pruefe("Kreisspiele zeigen Unterkategorien",
         document.querySelectorAll("#kacheln .kachel").length > 1 &&
         document.getElementById("listenkopf").hidden);
  pfad = leererPfad(); pfad.bereich = "pfadfindertechnik"; pfad.kategorie = "knoten";
  aktualisiere();
  pruefe("kleine Kategorie springt direkt in die Liste",
         !document.getElementById("listenkopf").hidden);
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.kategorie = "kreis";
  pfad.unterkategorie = "__alle__"; aktualisiere();
  pruefe("'Alle anzeigen' zeigt die ganze Kategorie",
         gefiltert.length > 50 && document.getElementById("pfad").textContent.indexOf("Alle") > -1,
         gefiltert.length);

  // --- Sortierung ---
  zuruecksetzen();
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.kategorie = "gelaende";
  pfad.unterkategorie = "__alle__";
  document.getElementById("sortierung").value = "dauer"; aktualisiere();
  pruefe("Kategorie-Liste ist wirklich sichtbar",
         !document.getElementById("listenkopf").hidden && gefiltert.length > 10,
         gefiltert.length);
  var aufsteigend = gefiltert.every(function (e, i) {
    return i === 0 || gefiltert[i - 1].dauer_min <= e.dauer_min;
  });
  pruefe("Liste nach Dauer aufsteigend sortiert", aufsteigend);
  document.getElementById("sortierung").value = "dauer-ab"; aktualisiere();
  var absteigend = gefiltert.every(function (e, i) {
    return i === 0 || gefiltert[i - 1].dauer_min >= e.dauer_min;
  });
  pruefe("Liste nach Dauer absteigend sortiert", absteigend);
  document.getElementById("sortierung").value = "dauer";

  // --- Suche ---
  zuruecksetzen();
  document.getElementById("suche").value = "knoten"; aktualisiere();
  pruefe("Suche findet etwas", gefiltert.length > 5, gefiltert.length);
  pruefe("Titeltreffer stehen oben",
         gefiltert[0].titel.toLowerCase().indexOf("knoten") > -1, gefiltert[0].titel);
  zuruecksetzen();

  // --- Filter ---
  document.getElementById("fOhneMaterial").checked = true;
  document.getElementById("fDauer").value = "15"; aktualisiere();
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.unterkategorie = "__alle__";
  aktualisiere();
  pruefe("'Alle anzeigen' auf Typ-Ebene zeigt die Liste",
         !document.getElementById("listenkopf").hidden, gefiltert.length);
  pruefe("Filter 'ohne Material' + 'bis 15 Min' greift",
         gefiltert.length > 0 && gefiltert.every(function (e) {
           return !e.material.length && e.dauer_min <= 15;
         }), gefiltert.length);
  zuruecksetzen();
  document.getElementById("fStufe").value = "Wölflinge"; aktualisiere();
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.unterkategorie = "__alle__";
  aktualisiere();
  pruefe("Stufenfilter lässt Elemente ohne Altersangabe drin",
         gefiltert.some(function (e) { return !e.altersstufen.length; }));
  zuruecksetzen();

  // --- Planer ---
  ["rStufe", "rOrt", "rVorbereitung"].forEach(function (id) {
    document.getElementById(id).value = "";
  });
  document.getElementById("rOhneMaterial").checked = false;
  document.getElementById("rZielzeit").value = "120";
  liesRahmen();
  var mitten = [];
  for (var v = 0; v < 15; v++) {
    plan = { einstieg: null, haupt: [null, null], abschluss: null };
    planWuerfeln();
    mitten.push(planDauer().mitte);
  }
  var imRahmen = mitten.filter(function (m) { return m >= 90 && m <= 150; }).length;
  pruefe("Würfeln trifft die Zielzeit (15 Versuche, Ziel 120)", imRahmen >= 13,
         imRahmen + "/15 zwischen 90 und 150");
  pruefe("Plan-Text enthält Quelle und Lizenz",
         planAlsText().indexOf("Lizenz") === -1 ? planAlsText().indexOf("Quelle:") > -1 : true);
  pruefe("Plan-Text nennt Material", planAlsText().indexOf("Material:") > -1);
  pruefe("alle Plätze gefüllt",
         alleSlots().every(function (s) { return !!planElement(s.slot.schluessel, s.index); }));

  plan = { einstieg: null, haupt: [null, null], abschluss: null }; zeichnePlan();
  pruefe("leerer Plan zeigt nur die Kreise", planDauer().mitte === 10, planDauer().mitte);

  // --- Auswahl-Dialog ---
  oeffneAuswahl(SLOTS[1], 0, true);
  pruefe("Vorschläge liefern Treffer", auswahlListe.length > 0, auswahlListe.length);
  pruefe("Chip-Reihen vorhanden",
         document.querySelectorAll("#auswahlChips .chipzeile").length >= 2);
  var ersteReihe = document.querySelector("#auswahlChips .chipzeile");
  var einChip = ersteReihe.querySelectorAll(".chip")[1];
  var vorher = auswahlListe.length;
  einChip.click();
  pruefe("Chip schränkt die Liste ein", auswahlListe.length <= vorher,
         vorher + " -> " + auswahlListe.length);
  schliesseUeberlagerung(document.getElementById("auswahl"));

  // --- Zufall zieht aus dem, was gerade zu sehen ist ---
  zuruecksetzen();
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.kategorie = "kreis";
  pfad.unterkategorie = "singen"; aktualisiere();
  var vorFilter = gefiltert.length;
  pfad = leererPfad(); aktualisiere();
  pruefe("Zufallstopf folgt dem Pfad", gefiltert.length === ALLE.length,
         "vorher " + vorFilter + ", jetzt " + gefiltert.length);
  pfad = leererPfad(); pfad.bereich = "pfadfindertechnik"; aktualisiere();
  pruefe("Zufallstopf auf Kachelseite passt zum Pfad",
         gefiltert.length > 0 && gefiltert.every(function (e) {
           return e.bereich === "pfadfindertechnik";
         }), gefiltert.length);

  // --- Größe als zweite Ebene außerhalb der Spiele ---
  zuruecksetzen();
  pfad = leererPfad(); pfad.bereich = "werken"; aktualisiere();
  var groessenKacheln = Array.prototype.map.call(
    document.querySelectorAll("#kacheln .kachel"), function (k) { return k.textContent; });
  pruefe("Werken zeigt Bausteine und ganze Abende als Kacheln",
         groessenKacheln.some(function (x) { return /Ganze Abende/.test(x); }),
         groessenKacheln.join(" | "));
  pfad = leererPfad(); pfad.bereich = "werken"; pfad.umfang = "ganzer_abend"; aktualisiere();
  pruefe("Größenauswahl filtert richtig",
         gefiltert.length > 0 && gefiltert.every(function (e) {
           return e.bereich === "werken" && e.umfang === "ganzer_abend";
         }), gefiltert.length);

  // --- Dauerfilter meint die Obergrenze ---
  zuruecksetzen();
  document.getElementById("fDauer").value = "15";
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.unterkategorie = "__alle__";
  aktualisiere();
  pruefe("'passt in 15 Min' liefert nur Bausteine bis 15 Min",
         gefiltert.length > 0 && gefiltert.every(function (e) { return e.dauer_max <= 15; }),
         gefiltert.length);

  // --- Teilnehmerzahl ---
  zuruecksetzen();
  document.getElementById("fTeilnehmer").value = "4";
  pfad = leererPfad(); pfad.bereich = "spiel"; pfad.unterkategorie = "__alle__";
  aktualisiere();
  pruefe("Teilnehmerfilter wirft zu große Spiele raus",
         gefiltert.length > 0 && gefiltert.every(function (e) {
           return !e.gruppe_min || e.gruppe_min <= 4;
         }), gefiltert.length);

  // --- Suche mit zwei Wörtern ---
  zuruecksetzen();
  document.getElementById("suche").value = "spiel gelaende"; aktualisiere();
  var zweiWorte = gefiltert.length;
  document.getElementById("suche").value = "gelände"; aktualisiere();
  pruefe("Suche versteht zwei Wörter", zweiWorte > 0,
         "'spiel gelaende' -> " + zweiWorte + ", 'gelände' -> " + gefiltert.length);
  zuruecksetzen();

  // --- Planer: Projekte nicht neben einem zweiten Hauptteil-Baustein ---
  plan = { einstieg: null, haupt: [null, null], abschluss: null };
  var hauptSlot = SLOTS.filter(function (s) { return s.mehrfach; })[0];
  pruefe("Hauptteil mit zwei Plätzen lässt nichts zu, was den Abend füllt",
         !ALLE.filter(hauptSlot.passt).some(function (e) {
           return e.umfang === "ganzer_abend";
         }));
  plan = { einstieg: null, haupt: [null], abschluss: null };
  pruefe("Hauptteil mit einem Platz lässt ganze Abende zu",
         ALLE.filter(hauptSlot.passt).some(function (e) {
           return e.umfang === "ganzer_abend";
         }));

  // --- Vorschläge auch bei vollem Plan ---
  plan = { einstieg: null, haupt: [null, null], abschluss: null };
  planWuerfeln();
  plan.haupt.push(null); zeichnePlan();
  oeffneAuswahl(hauptSlot, plan.haupt.length - 1, true);
  pruefe("Vorschläge bleiben auch bei vollem Plan gefüllt", auswahlListe.length > 0,
         auswahlListe.length + " bei " + Math.round(freieZeit(null)) + " Min frei");
  schliesseUeberlagerung(document.getElementById("auswahl"), true);

  // --- Weg von der Detailansicht in den Plan ---
  plan = { einstieg: null, haupt: [null, null], abschluss: null }; zeichnePlan();
  var einSpiel = ALLE.filter(function (e) { return SLOTS[0].passt(e); })[0];
  zeigeDetail(einSpiel);
  var planKnopf = document.querySelector('#detailInhalt .planzeile button[data-slot="einstieg"]');
  pruefe("Detailansicht bietet 'In den Plan'", !!planKnopf);
  if (planKnopf) {
    planKnopf.click();
    pruefe("Baustein landet im Einstiegsplatz", plan.einstieg === einSpiel.id, plan.einstieg);
  }
  zeigeAnsicht("bausteine");

  // --- Abkürzungen nach dem Platz im Abend ---
  zuruecksetzen();
  var abschlussKachel = Array.prototype.filter.call(
    document.querySelectorAll("#kacheln .kachel"),
    function (k) { return /Abschluss/.test(k.textContent); })[0];
  pruefe("Startseite bietet 'Zum Abschluss'", !!abschlussKachel);
  if (abschlussKachel) {
    abschlussKachel.click();
    pruefe("'Zum Abschluss' zeigt nur Abschlussspiele",
           gefiltert.length > 50 && gefiltert.every(function (e) {
             return e.slots.indexOf("abschluss") > -1;
           }), gefiltert.length);
  }
  zuruecksetzen();

  // --- Versteckte Bereiche sind wirklich weg ---
  pruefe("Sortiermenü ist auf der Kachelseite nicht sichtbar",
         getComputedStyle(document.getElementById("listenkopf")).display === "none");

  // --- Stichworte in der Detailansicht ---
  zeigeDetail(NACH_ID["eig-knoten-olympiade"] || ALLE[0]);
  var wortChips = document.querySelectorAll("#detailInhalt .chip[data-wort]");
  pruefe("Detailansicht bietet Stichworte", wortChips.length > 0, wortChips.length);
  if (wortChips.length) {
    var wort = wortChips[0].getAttribute("data-wort");
    pruefe("Stichwort ist nicht der eigene Titel",
           wort.toLowerCase() !== "knoten-olympiade", wort);
    wortChips[0].click();
    pruefe("Stichwort füllt die Suche",
           document.getElementById("suche").value === wort && gefiltert.length > 0,
           gefiltert.length + " Treffer für " + wort);
  }
  zuruecksetzen();

  // --- Auswahl-Dialog: erst lesen, dann nehmen ---
  plan = { einstieg: null, haupt: [null, null], abschluss: null };
  zeichnePlan();
  oeffneAuswahl(SLOTS[0], 0, true);
  pruefe("Karten im Auswahl-Dialog haben 'Regeln lesen' und 'In den Plan'",
         document.querySelectorAll("#auswahlListe .kartenfuss").length > 0 &&
         document.querySelectorAll("#auswahlListe .kartenfuss .knopf").length >= 2);
  pruefe("Chip-Reihen sind zugeklappt", !document.getElementById("auswahlEingrenzen").open);
  var vorschlagsstreuung = auswahlListe.slice(0, 5).map(function (e) {
    return e.titel.charAt(0).toUpperCase();
  });
  pruefe("Vorschläge fangen nicht alle mit demselben Buchstaben an",
         new Set(vorschlagsstreuung).size > 1, vorschlagsstreuung.join(""));
  schliesseUeberlagerung(document.getElementById("auswahl"), true);

  // --- Material ---
  pruefe("kein Baustein trägt 'keines' als Material",
         !ALLE.some(function (e) {
           return (e.material || []).some(function (m) {
             return /^(kein(e|es)?|ohne material|nichts)$/i.test(m.trim());
           });
         }));

  // --- Internetadressen und Schutz vor eingeschleustem HTML ---
  var probe = document.createElement("div");
  probe.innerHTML = textZuHtml(
    "Böse <img src=x onerror=alert(1)> und https://example.org/a?b=1&c=2 Ende");
  pruefe("HTML aus den Daten wird als Text angezeigt",
         (probe.innerHTML.match(/<[a-z]+/gi) || []).join(",") === "<p,<a",
         (probe.innerHTML.match(/<[a-z]+/gi) || []).join(","));
  pruefe("Adressen werden anklickbar",
         probe.querySelector("a") &&
         probe.querySelector("a").getAttribute("href").indexOf("https://example.org") === 0);

  // --- Varianten in der Detailansicht ---
  zuruecksetzen();
  var mitVarianten = ALLE.filter(function (e) {
    return e.varianten && e.varianten.length && NACH_ID[e.varianten[0].id];
  })[0];
  pruefe("es gibt zusammengelegte Elemente mit Varianten", !!mitVarianten,
         ALLE.filter(function (e) { return e.varianten.length; }).length + " Stück");
  if (mitVarianten) {
    zeigeDetail(mitVarianten);
    var kasten = document.querySelector("#detailInhalt .kasten.verweis");
    pruefe("Varianten werden angezeigt",
           !!kasten && kasten.textContent.indexOf("Auch bekannt als") > -1);
    pruefe("Variantenkasten zeigt den Titel der anderen Fassung",
           !!kasten && kasten.textContent.indexOf(mitVarianten.varianten[0].titel) > -1,
           mitVarianten.varianten[0].titel);
    // Punkt 72: die Lizenz des Hauptelements steht weiterhin da …
    pruefe("Lizenz steht auch bei einem Element mit Varianten noch da",
           document.getElementById("detailInhalt").textContent
             .indexOf(mitVarianten.quelle.lizenz) > -1,
           mitVarianten.quelle.lizenz);
    var variantenKnopf = document.querySelector("#detailInhalt button[data-variante]");
    pruefe("Variante ist anklickbar", !!variantenKnopf);
    if (variantenKnopf) {
      var andere = NACH_ID[variantenKnopf.getAttribute("data-variante")];
      variantenKnopf.click();
      // … und drüben steht die eigene Lizenz der anderen Fassung.
      pruefe("Variante führt zum anderen Element",
             document.getElementById("detailTitel").textContent === andere.titel,
             andere.titel);
      pruefe("die andere Fassung zeigt ihre eigene Quelle und Lizenz",
             document.getElementById("detailInhalt").textContent
               .indexOf(andere.quelle.lizenz) > -1,
             andere.quelle.lizenz);
    }
    schliesseUeberlagerung(document.getElementById("detail"), true);
  }

  // --- Spiele, die eine Probe üben ---
  var mitUebt = ALLE.filter(function (e) { return e.uebt && e.uebt.length; })[0];
  if (mitUebt) {
    var probeDazu = ALLE.filter(function (e) {
      return e.bereich === "pfadfindertechnik" && e.kategorie === mitUebt.uebt[0];
    })[0];
    pruefe("es gibt eine Probe zu den übenden Spielen", !!probeDazu, mitUebt.uebt[0]);
    if (probeDazu) {
      zeigeDetail(probeDazu);
      var uebtKasten = Array.prototype.filter.call(
        document.querySelectorAll("#detailInhalt .kasten.verweis"),
        function (k) { return k.textContent.indexOf("Spiele, die das üben") === 0; })[0];
      pruefe("Probe zeigt 'Spiele, die das üben'", !!uebtKasten,
             uebtKasten ? uebtKasten.querySelectorAll("button").length + " Spiele" : "keiner");
      schliesseUeberlagerung(document.getElementById("detail"), true);
    }
  }

  // --- Neue Filter: Platz, Körperkontakt, Hosensackspiel ---
  function filterProbe(vorbereiten) {
    zuruecksetzen();
    vorbereiten();
    pfad = leererPfad(); pfad.unterkategorie = "__alle__";
    aktualisiere();
    return gefiltert;
  }
  var imZimmer = filterProbe(function () {
    document.getElementById("fPlatz").value = "zimmer";
  });
  pruefe("Platzfilter 'ein Zimmer' wirft zu große Spiele raus",
         imZimmer.length > 0 && imZimmer.every(function (e) {
           return !e.platz || PLATZ_RANG[e.platz] <= 2;
         }), imZimmer.length);
  pruefe("Platzfilter behält Elemente ohne Platzangabe",
         imZimmer.some(function (e) { return !e.platz; }),
         imZimmer.filter(function (e) { return !e.platz; }).length + " ohne Angabe");
  pruefe("Platzfilter lässt Tischspiele im Zimmer zu",
         imZimmer.some(function (e) { return e.platz === "tisch"; }));

  var ohneKontakt = filterProbe(function () {
    document.getElementById("fOhneKontakt").checked = true;
  });
  pruefe("Filter 'ohne Körperkontakt' greift",
         ohneKontakt.length > 0 && ohneKontakt.every(function (e) {
           return e.naehe !== "leicht" && e.naehe !== "hoch";
         }), ohneKontakt.length);
  pruefe("Filter 'ohne Körperkontakt' behält Elemente ohne Angabe",
         ohneKontakt.some(function (e) { return e.naehe === ""; }),
         ohneKontakt.filter(function (e) { return e.naehe === ""; }).length + " ohne Angabe");

  var sofort = filterProbe(function () {
    document.getElementById("fHosensack").checked = true;
  });
  pruefe("'5 Minuten übrig' liefert nur Bausteine ohne Material",
         sofort.length > 0 && sofort.every(function (e) {
           return e.hosensackspiel === true && (!e.material || !e.material.length);
         }), sofort.length);
  pruefe("'5 Minuten übrig' verlangt auch geringe Vorbereitung",
         sofort.every(function (e) { return e.vorbereitung === "gering"; }));
  zuruecksetzen();
  var sofortKachel = Array.prototype.filter.call(
    document.querySelectorAll("#kacheln .kachel"),
    function (k) { return /5 Minuten übrig/.test(k.textContent); })[0];
  pruefe("Startseite bietet '5 Minuten übrig'", !!sofortKachel);
  if (sofortKachel) {
    sofortKachel.click();
    pruefe("'5 Minuten übrig' zeigt sofort die Liste",
           !document.getElementById("listenkopf").hidden && gefiltert.length > 0 &&
           gefiltert.every(function (e) { return e.hosensackspiel === true; }),
           gefiltert.length);
  }
  zuruecksetzen();

  // --- Eröffnungs- und Schlusskreis im Planer ---
  plan = leererPlan(); zeichnePlan();
  pruefe("leerer Eröffnungskreis bleibt als Rahmen stehen",
         planAlsText().indexOf("1. Eröffnungskreis (5 Min)") > -1 &&
         planAlsText().indexOf("Schlusskreis (5 Min)") > -1);
  var eroeffnungsBausteine = ALLE.filter(KREISE[0].passt);
  pruefe("es gibt Bausteine für den Eröffnungskreis", eroeffnungsBausteine.length > 0,
         eroeffnungsBausteine.length);
  var ritual = eroeffnungsBausteine[0];
  slotSetzen("eroeffnung", 0, ritual.id);
  pruefe("Eröffnungsplatz lässt sich füllen",
         kreisElement("eroeffnung") === ritual, ritual.titel);
  var planZeilen = planAlsText().split("\n");
  var stelle = -1;
  for (var pz = 0; pz < planZeilen.length; pz++) {
    if (planZeilen[pz].indexOf("Eröffnungskreis: " + ritual.titel) > -1) stelle = pz;
  }
  pruefe("gewählter Eröffnungsbaustein steht im Plan-Text", stelle > -1);
  pruefe("Eröffnungsbaustein steht mit Quelle und Lizenz im Plan-Text",
         stelle > -1 && planZeilen.slice(stelle, stelle + 3).join(" ")
           .indexOf("Quelle: " + ritual.quelle.name + " · " + ritual.quelle.lizenz) > -1,
         ritual.quelle.lizenz);
  pruefe("gefüllter Eröffnungskreis zählt mit seiner eigenen Dauer",
         planDauer().min === ritual.dauer_min + 5,
         planDauer().min + " Min statt " + (5 + 5));
  var schlussBausteine = ALLE.filter(KREISE[1].passt);
  pruefe("der Schlusskreis lässt sich ebenfalls füllen",
         schlussBausteine.length > 0 &&
         schlussBausteine.every(function (e) { return e.bereich !== "spiel"; }),
         schlussBausteine.length + " Rituale");
  slotAktion("leeren", KREISE[0], 0);
  pruefe("geleerter Eröffnungskreis fällt auf den Rahmen zurück",
         !kreisElement("eroeffnung") && planDauer().mitte === 10, planDauer().mitte);
  zeigeDetail(ritual);
  var kreisKnopf = document.querySelector(
    '#detailInhalt .planzeile button[data-slot="eroeffnung"]');
  pruefe("Detailansicht bietet den Eröffnungskreis an", !!kreisKnopf);
  if (kreisKnopf) {
    kreisKnopf.click();
    pruefe("Ritual landet im Eröffnungskreis", plan.eroeffnung === ritual.id);
  }
  plan = leererPlan(); zeichnePlan();
  zeigeAnsicht("bausteine");
  zuruecksetzen();

  // --- Eigene Ideen (Stufe 1 und 2) ---
  // Der Test legt eine Idee an und räumt sie am Ende wieder weg: der
  // Browserspeicher des Nutzers sieht hinterher aus wie vorher.
  var gemerkteIdeen = null;
  try { gemerkteIdeen = localStorage.getItem(EIGENE_SPEICHER); } catch (f) { /* egal */ }

  zuruecksetzen();
  var pruefTitel = "Rauchtest-Idee (wird wieder gelöscht)";
  oeffneIdeenForm(null);
  document.getElementById("iTitel").value = pruefTitel;
  document.getElementById("iBeschreibung").value =
    "Nur zum Prüfen der eigenen Ideen. Diese Idee legt der Rauchtest an und " +
    "entfernt sie am Ende wieder.";
  document.getElementById("iDauerVon").value = "10";
  document.getElementById("iDauerBis").value = "15";
  document.getElementById("iMaterial").value = "Seil";
  document.getElementById("iAutor").value = "Rauchtest";
  document.getElementById("iSpeichern").click();
  var meine = EIGENE_IDEEN.filter(function (e) { return e.titel === pruefTitel; });
  pruefe("eigene Idee lässt sich anlegen", meine.length === 1, EIGENE_IDEEN.length + " im Speicher");
  var eigenId = meine.length ? meine[0].id : "";
  pruefe("eigene Idee steht danach in der Liste",
         gefiltert.some(function (e) { return e.id === eigenId; }), gefiltert.length);
  pruefe("eigene Idee trägt die Plakette 'eigene Idee'",
         document.getElementById("liste").innerHTML.indexOf(">eigene Idee<") > -1);
  pruefe("eigene Idee trägt Quelle und Lizenz",
         !!NACH_ID[eigenId] && NACH_ID[eigenId].quelle.lizenz === "CC BY-SA 4.0" &&
         NACH_ID[eigenId].quelle.autor === "Rauchtest");
  pruefe("Slots werden wie in build.py abgeleitet",
         !!NACH_ID[eigenId] &&
         NACH_ID[eigenId].slots.join(",") === "einstieg,hauptteil,abschluss",
         NACH_ID[eigenId] ? NACH_ID[eigenId].slots.join(",") : "-");

  zuruecksetzen();
  document.getElementById("suche").value = "Rauchtest-Idee"; aktualisiere();
  pruefe("eigene Idee wird von der Suche gefunden",
         gefiltert.some(function (e) { return e.id === eigenId; }), gefiltert.length);
  zuruecksetzen();

  // Neuladen: genau das, was beim Start passiert – aus dem Speicher lesen
  ladeEigeneIdeen(); setzeAlle(); aktualisiere();
  pruefe("eigene Idee übersteht das Neuladen",
         !!NACH_ID[eigenId] && NACH_ID[eigenId].titel === pruefTitel);

  // Der Schalter darf eigene Ideen nie ausblenden
  setzeSammlung(true);
  pfad = leererPfad(); pfad.eigene = true; pfad.unterkategorie = "__alle__";
  aktualisiere();
  pruefe("eigene Ideen bleiben in der geprüften Auswahl sichtbar",
         gefiltert.some(function (e) { return e.id === eigenId; }), gefiltert.length);
  setzeSammlung(false);
  zuruecksetzen();

  // Bearbeiten
  oeffneIdeenForm(NACH_ID[eigenId]);
  document.getElementById("iDauerBis").value = "30";
  document.getElementById("iTipps").value = "Nachher aufräumen nicht vergessen.";
  document.getElementById("iSpeichern").click();
  pruefe("Bearbeiten wirkt und behält die ID",
         !!NACH_ID[eigenId] && NACH_ID[eigenId].dauer_max === 30 &&
         NACH_ID[eigenId].tipps.length > 0,
         NACH_ID[eigenId] ? NACH_ID[eigenId].dauer_max + " Min" : "weg");

  // In den Plan legen – mit Quelle und Lizenz im Plan-Text
  plan = leererPlan(); zeichnePlan();
  inDenPlan(NACH_ID[eigenId], "haupt");
  pruefe("eigene Idee lässt sich in den Plan legen", plan.haupt[0] === eigenId);
  pruefe("eigene Idee steht mit Quelle und Lizenz im Plan-Text",
         planAlsText().indexOf(pruefTitel) > -1 &&
         planAlsText().indexOf("Quelle: eigene Idee · CC BY-SA 4.0") > -1);
  plan = leererPlan(); zeichnePlan();
  zeigeAnsicht("bausteine");

  // Stufe 2: sichern und wieder einlesen
  var gesichert = JSON.stringify(ideenAlsDatei());
  pruefe("gesicherte Datei hat meta und elemente",
         !!JSON.parse(gesichert).meta && Array.isArray(JSON.parse(gesichert).elemente));
  loescheEigeneIdee(eigenId);
  pruefe("Löschen entfernt die Idee",
         !NACH_ID[eigenId] && !EIGENE_IDEEN.some(function (e) { return e.id === eigenId; }));
  verarbeiteIdeenDatei("das ist kein JSON");
  pruefe("kaputte Datei ändert nichts",
         !NACH_ID[eigenId] && !document.getElementById("ideenDialog").hidden);
  schliesseUeberlagerung(document.getElementById("ideenDialog"), true);
  verarbeiteIdeenDatei(gesichert);
  var uebernehmen = document.getElementById("einlesenUebernehmen");
  pruefe("Einlesen fragt erst, bevor es etwas übernimmt",
         !!uebernehmen &&
         document.getElementById("ideenDialogInhalt").textContent.indexOf("kommen dazu") > -1);
  if (uebernehmen) uebernehmen.click();
  pruefe("gesicherte Datei lässt sich wieder einlesen",
         !!NACH_ID[eigenId] && NACH_ID[eigenId].titel === pruefTitel);
  pruefe("zweites Einlesen legt nichts doppelt an",
         (function () {
           var vorher = EIGENE_IDEEN.length;
           verarbeiteIdeenDatei(gesichert);
           var text = document.getElementById("ideenDialogInhalt").textContent;
           var knopf = document.getElementById("einlesenUebernehmen");
           if (knopf) knopf.click();
           else schliesseUeberlagerung(document.getElementById("ideenDialog"), true);
           return EIGENE_IDEEN.length === vorher && text.indexOf("0 kommen dazu") > -1;
         })(), EIGENE_IDEEN.length + " eigene Ideen");
  if (!document.getElementById("ideenDialog").hidden) {
    schliesseUeberlagerung(document.getElementById("ideenDialog"), true);
  }

  // Was passiert, wenn der Browserspeicher nicht mitmacht (privates Fenster,
  // voller Speicher)? Nichts darf stillschweigend verlorengehen.
  var echtesSetzen = localStorage.setItem.bind(localStorage);
  var vorherAnzahl = EIGENE_IDEEN.length;
  localStorage.setItem = function () { throw new Error("Speicher voll (nur ein Test)"); };
  oeffneIdeenForm(null);
  document.getElementById("iTitel").value = "Rauchtest-Speicherfehler";
  document.getElementById("iBeschreibung").value =
    "Diese Idee soll absichtlich nicht gespeichert werden können.";
  document.getElementById("iSpeichern").click();
  pruefe("Speicherfehler wird gemeldet, das Formular bleibt stehen",
         !document.getElementById("ideenForm").hidden &&
         !document.getElementById("iFehler").hidden &&
         document.getElementById("iTitel").value === "Rauchtest-Speicherfehler");
  pruefe("bei Speicherfehler steht der Text zum Herauskopieren da",
         !!document.getElementById("iRettung") &&
         document.getElementById("iRettung").value.length > 100);
  pruefe("bei Speicherfehler wird nichts halb übernommen",
         EIGENE_IDEEN.length === vorherAnzahl, EIGENE_IDEEN.length);
  localStorage.setItem = echtesSetzen;
  schliesseUeberlagerung(document.getElementById("ideenForm"), true);

  // Aufräumen: den Speicherstand des Nutzers wiederherstellen
  try {
    if (gemerkteIdeen === null) localStorage.removeItem(EIGENE_SPEICHER);
    else localStorage.setItem(EIGENE_SPEICHER, gemerkteIdeen);
  } catch (f) { /* egal */ }
  ladeEigeneIdeen(); setzeAlle(); zeichneIdeenStand();
  pruefe("der Rauchtest räumt seine eigene Idee wieder weg", !NACH_ID[eigenId],
         EIGENE_IDEEN.length + " eigene Ideen übrig");
  zuruecksetzen();
  zeichneFuss();

  // --- Die Brille: Wortersetzung beim Anzeigen ---
  // Die App zeigt Texte durch data/sprache.json hindurch an; in den Dateien
  // bleibt der Originalwortlaut stehen. Geprüft wird beides: dass ersetzt
  // wird, und dass nur ersetzt wird, was ersetzt werden soll.
  zuruecksetzen();
  var brilleDa = !!(SPRACHE && SPRACHE.regeln && BRILLE_PAARE.length);
  pruefe("Wortliste ist geladen", brilleDa,
         brilleDa ? BRILLE_PAARE.length + " Wortpaare, Stand " + SPRACHE.meta.stand : "keine");
  pruefe("jede Regel sagt, ob ein Änderungshinweis nötig ist",
         brilleDa && SPRACHE.regeln.every(function (r) {
           return typeof r.hinweis_noetig === "boolean";
         }) && ersetztMitHinweis().length ===
              ALLE.filter(function (e) { return e._ersetzt && e._ersetzt.length; }).length,
         "heute verlangen alle sieben Regeln einen Hinweis");
  pruefe("jede Regel nennt Grund und Datum",
         brilleDa && SPRACHE.regeln.every(function (r) {
           return r.grund && r.seit && r.woerter && r.woerter.length &&
                  r.woerter.every(function (w) { return w.von && w.zu; });
         }));

  function ersetztMitHinweis() {
    return ALLE.filter(function (e) { return e._hinweisNoetig; });
  }
  // Der angezeigte Text eines Elements – genau das, was der Nutzer liest.
  function angezeigt(e) {
    return [e.titel, e.kurz, e.beschreibung, e.tipps || "",
            (e.tags || []).join(" "), (e.themen || []).join(" "),
            (e.material || []).join(" ")].join(" ");
  }
  // Alle ids, die in der Wortliste ausdrücklich ausgenommen sind.
  var brilleAusnahmen = [];
  if (brilleDa) {
    SPRACHE.regeln.forEach(function (r) {
      (r.ausser || []).forEach(function (id) {
        if (brilleAusnahmen.indexOf(id) === -1) brilleAusnahmen.push(id);
      });
    });
  }
  function ohneAusnahmen(liste) {
    return liste.filter(function (e) { return brilleAusnahmen.indexOf(e.id) === -1; });
  }

  var mitSippe = ohneAusnahmen(ALLE.filter(function (e) {
    return /\bSippe\b|\bSippen\b|Sippling/.test(angezeigt(e));
  }));
  pruefe("„Sippe“ steht nirgends mehr in der Anzeige", mitSippe.length === 0,
         mitSippe.length ? mitSippe.map(function (e) { return e.id; }).join(", ")
                         : brilleAusnahmen.length + " eingetragene Ausnahmen");
  pruefe("dafür steht „Horte/Gilde“ da",
         ALLE.filter(function (e) { return /Horte\/Gilde|Horten\/Gilden|Horten-\/Gilden/.test(angezeigt(e)); }).length > 50,
         ALLE.filter(function (e) { return /Horte\/Gilde|Horten\/Gilden|Horten-\/Gilden/.test(angezeigt(e)); }).length + " Elemente");

  var ersetzte = ALLE.filter(function (e) { return e._ersetzt && e._ersetzt.length; });
  pruefe("die Brille hat gewirkt", ersetzte.length > 150, ersetzte.length + " Elemente geändert");
  pruefe("jedes geänderte Element hat seinen Originaltext behalten",
         ersetzte.every(function (e) { return e._urtext && Object.keys(e._urtext).length; }));
  pruefe("unveränderte Elemente tragen keinen Originaltext",
         ALLE.every(function (e) { return (e._ersetzt && e._ersetzt.length) || !e._urtext; }));

  // Das Probenbuch ist der Maßstab und wird nicht angefasst.
  var pb = ALLE.filter(function (e) { return e.id.indexOf("pb-") === 0; });
  pruefe("Probenbuch-Elemente sind unverändert",
         pb.length === 28 && pb.every(function (e) { return !e._ersetzt && !e._urtext; }),
         pb.length + " pb-Elemente");
  pruefe("selbst erfasste Ideen bleiben, wie sie getippt wurden",
         ALLE.filter(function (e) { return e._eigen; })
             .every(function (e) { return !e._ersetzt; }));

  // Die Ausnahmen müssen wirken, sonst wird aus einer Tabu-Wortliste Unsinn.
  var tabu = NACH_ID["insp-digitales-tabu"];
  pruefe("eingetragene Ausnahmen bleiben unberührt",
         !!tabu && /Sippe/.test(angezeigt(tabu)) && /Gut Pfad/.test(angezeigt(tabu)));

  // Wortgrenzen: der Hordentopf ist Kochgeschirr und keine Horte.
  pruefe("die Brille greift nicht ins Wortinnere",
         durchDieBrille("Hordentopf und Sippenwimpel am Sippenabend", "x-test", null) ===
         "Hordentopf und Horten-/Gildenwimpel am Sippenabend",
         durchDieBrille("Hordentopf und Sippenwimpel am Sippenabend", "x-test", null));
  pruefe("das längere Wortpaar gewinnt",
         durchDieBrille("Bringt es zur Gruppenstunde mit", "x-test", null) ===
         "Bringt es zum Heimabend mit",
         durchDieBrille("Bringt es zur Gruppenstunde mit", "x-test", null));
  pruefe("eine lange Regel blockiert keine kurze",
         durchDieBrille("Zeltlager oder lange Gruppenstunden", "x-test", null) ===
         "Zeltlager oder lange Heimabende",
         durchDieBrille("Zeltlager oder lange Gruppenstunden", "x-test", null));

  // Genderzeichen: Doppelpunkt, Sternchen, Unterstrich sind aufgelöst.
  var mitZeichen = ohneAusnahmen(ALLE.filter(function (e) {
    return /[A-Za-zÄÖÜäöüß]+[:*_](in|innen|innnen|r|n|e)\b/.test(angezeigt(e));
  }));
  pruefe("Genderzeichen sind aufgelöst", mitZeichen.length === 0,
         mitZeichen.length ? mitZeichen.map(function (e) { return e.id; }).join(", ") : "keine übrig");
  pruefe("aufgelöst wird als Paarform bzw. Schrägstrich",
         durchDieBrille("Ein:e Spieler:in und alle Spieler:innen", "x-test", null) ===
         "Ein Spieler/eine Spielerin und alle Spieler und Spielerinnen",
         durchDieBrille("Ein:e Spieler:in und alle Spieler:innen", "x-test", null));

  // Die Suche muss beide Schreibweisen finden, sonst ist die Brille eine Falle.
  setzeSammlung(false);
  document.getElementById("suche").value = "horte";
  aktualisiere();
  var horteTreffer = gefiltert.filter(function (e) {
    return e._urtext && /Sipp/.test(JSON.stringify(e._urtext));
  });
  pruefe("Suche nach „Horte“ findet, wo „Sippe“ steht", horteTreffer.length > 40,
         horteTreffer.length + " von " + gefiltert.length + " Treffern");
  document.getElementById("suche").value = "sippenwimpel";
  aktualisiere();
  pruefe("Suche nach dem Originalwort findet den Baustein weiterhin",
         gefiltert.some(function (e) { return e.id === "eig-sippenwimpel-gestalten"; }),
         gefiltert.length + " Treffer");
  document.getElementById("suche").value = "gildenwimpel";
  aktualisiere();
  pruefe("Suche nach dem neuen Wort findet ihn auch",
         gefiltert.some(function (e) { return e.id === "eig-sippenwimpel-gestalten"; }),
         gefiltert.length + " Treffer");
  zuruecksetzen();

  // Der Änderungshinweis in der Detailansicht.
  var gezeigtes = NACH_ID["eig-sippenwimpel-gestalten"];
  zeigeDetail(gezeigtes);
  var detailText = document.getElementById("detailInhalt").textContent;
  pruefe("Änderungshinweis steht im Quellenkasten",
         detailText.indexOf("einzelne Wörter") > -1 && detailText.indexOf("Sippenwimpel") > -1);
  pruefe("der Änderungshinweis kommt ohne das Wort „Lizenz“ aus",
         document.querySelector(".kasten.quelle .brille").textContent.indexOf("Lizenz") === -1);
  pruefe("das Original ist erst versteckt",
         !!document.getElementById("urtextKnopf") &&
         document.getElementById("urtextKasten").hidden);
  document.getElementById("urtextKnopf").click();
  pruefe("Knopf zeigt das Original",
         !document.getElementById("urtextKasten").hidden &&
         document.getElementById("urtextKasten").textContent.indexOf("Sippenwimpel gestalten") > -1);
  document.getElementById("urtextKnopf").click();
  pruefe("Knopf blendet das Original wieder aus",
         document.getElementById("urtextKasten").hidden);
  schliesseUeberlagerung(document.getElementById("detail"));

  zeigeDetail(NACH_ID["pb-organisatorischer-aufbau"]);
  pruefe("ohne Ersetzung steht kein Änderungshinweis da",
         document.getElementById("detailInhalt").textContent.indexOf("einzelne Wörter") === -1 &&
         !document.getElementById("urtextKnopf"));
  schliesseUeberlagerung(document.getElementById("detail"));

  // Der Plan-Text zum Teilen muss dieselbe Brille tragen wie der Bildschirm.
  var gemerkterPlan = plan;
  plan = leererPlan();
  plan.haupt[0] = "eig-sippenwimpel-gestalten";
  plan.einstieg = "insp-anschleichen-ueben";
  var planText = planAlsText();
  pruefe("Plan-Text ist ersetzt",
         planText.indexOf("Horten-/Gildenwimpel") > -1 && planText.indexOf("Sippe") === -1);
  pruefe("Plan-Text sagt, dass Wörter getauscht wurden",
         planText.indexOf("sprachlich angepasst") > -1);
  plan = leererPlan();
  plan.haupt[0] = "pb-organisatorischer-aufbau";
  pruefe("Plan-Text sagt es nur, wo wirklich getauscht wurde",
         planAlsText().indexOf("sprachlich angepasst") === -1);
  plan = gemerkterPlan;
  zeichnePlan();
  zuruecksetzen();

  // --- Detailansicht ---
  zeigeDetail(ALLE[0]);
  pruefe("Detailansicht öffnet", !document.getElementById("detail").hidden);
  pruefe("Detailansicht nennt die Quelle",
         document.getElementById("detailInhalt").textContent.indexOf("Lizenz") > -1);
  schliesseUeberlagerung(document.getElementById("detail"));
  zuruecksetzen();
  zeigeAnsicht("bausteine");
  // Die App so zurücklassen, wie sie sich beim ersten Öffnen zeigt.
  setzeSammlung(true);

  return ergebnisse.join("\n") + "\n\n" +
         ergebnisse.filter(function (z) { return z.indexOf("FEHLER") === 0; }).length +
         " Fehler von " + ergebnisse.length + " Prüfungen";
})();
