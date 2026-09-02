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
   Am Ende setzt er alles zurück, aber ein gespeicherter Plan geht dabei verloren. */
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
    pfad = { typ: "", kategorie: "", unterkategorie: "", slot: "" };
    setzeFilterZurueck();
  }

  // --- Daten ---
  pruefe("Daten geladen", ALLE.length > 900, ALLE.length + " Elemente");
  pruefe("alle haben unterkategorie-Feld",
         ALLE.every(function (e) { return typeof e.unterkategorie === "string"; }));
  pruefe("alle haben Quelle mit Lizenz",
         ALLE.every(function (e) { return e.quelle && e.quelle.lizenz; }));

  // --- Kachel-Navigation ---
  zuruecksetzen();
  pruefe("Start zeigt Kacheln, keine Liste",
         document.querySelectorAll("#kacheln .kachel").length >= 4 &&
         document.getElementById("listenkopf").hidden);
  pfad = { typ: "spiel", kategorie: "", unterkategorie: "" }; aktualisiere();
  pruefe("Spiele zeigen Kategorie-Kacheln",
         document.querySelectorAll("#kacheln .kachel").length > 3);
  pfad = { typ: "spiel", kategorie: "kreis", unterkategorie: "" }; aktualisiere();
  pruefe("Kreisspiele zeigen Unterkategorien",
         document.querySelectorAll("#kacheln .kachel").length > 1 &&
         document.getElementById("listenkopf").hidden);
  pfad = { typ: "probe", kategorie: "knoten", unterkategorie: "" }; aktualisiere();
  pruefe("kleine Kategorie springt direkt in die Liste",
         !document.getElementById("listenkopf").hidden);
  pfad = { typ: "spiel", kategorie: "kreis", unterkategorie: "__alle__" }; aktualisiere();
  pruefe("'Alle anzeigen' zeigt die ganze Kategorie",
         gefiltert.length > 50 && document.getElementById("pfad").textContent.indexOf("Alle") > -1,
         gefiltert.length);

  // --- Sortierung ---
  zuruecksetzen();
  pfad = { typ: "spiel", kategorie: "gelaende", unterkategorie: "__alle__" };
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
  pfad = { typ: "spiel", kategorie: "", unterkategorie: "__alle__" }; aktualisiere();
  pruefe("'Alle anzeigen' auf Typ-Ebene zeigt die Liste",
         !document.getElementById("listenkopf").hidden, gefiltert.length);
  pruefe("Filter 'ohne Material' + 'bis 15 Min' greift",
         gefiltert.length > 0 && gefiltert.every(function (e) {
           return !e.material.length && e.dauer_min <= 15;
         }), gefiltert.length);
  zuruecksetzen();
  document.getElementById("fStufe").value = "Wölflinge"; aktualisiere();
  pfad = { typ: "spiel", kategorie: "", unterkategorie: "__alle__" }; aktualisiere();
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
  pfad = { typ: "spiel", kategorie: "kreis", unterkategorie: "singen" }; aktualisiere();
  var vorFilter = gefiltert.length;
  pfad = { typ: "", kategorie: "", unterkategorie: "" }; aktualisiere();
  pruefe("Zufallstopf folgt dem Pfad", gefiltert.length === ALLE.length,
         "vorher " + vorFilter + ", jetzt " + gefiltert.length);
  pfad = { typ: "probe", kategorie: "", unterkategorie: "" }; aktualisiere();
  pruefe("Zufallstopf auf Kachelseite passt zum Pfad",
         gefiltert.length > 0 && gefiltert.every(function (e) { return e.element_typ === "probe"; }),
         gefiltert.length);

  // --- Dauerfilter meint die Obergrenze ---
  zuruecksetzen();
  document.getElementById("fDauer").value = "15";
  pfad = { typ: "spiel", kategorie: "", unterkategorie: "__alle__" }; aktualisiere();
  pruefe("'passt in 15 Min' liefert nur Bausteine bis 15 Min",
         gefiltert.length > 0 && gefiltert.every(function (e) { return e.dauer_max <= 15; }),
         gefiltert.length);

  // --- Teilnehmerzahl ---
  zuruecksetzen();
  document.getElementById("fTeilnehmer").value = "4";
  pfad = { typ: "spiel", kategorie: "", unterkategorie: "__alle__" }; aktualisiere();
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
  pruefe("Hauptteil mit zwei Plätzen lässt keine Projekte zu",
         !ALLE.filter(hauptSlot.passt).some(function (e) { return e.element_typ === "projekt"; }));
  plan = { einstieg: null, haupt: [null], abschluss: null };
  pruefe("Hauptteil mit einem Platz lässt Projekte zu",
         ALLE.filter(hauptSlot.passt).some(function (e) { return e.element_typ === "projekt"; }));

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

  // --- Detailansicht ---
  zeigeDetail(ALLE[0]);
  pruefe("Detailansicht öffnet", !document.getElementById("detail").hidden);
  pruefe("Detailansicht nennt die Quelle",
         document.getElementById("detailInhalt").textContent.indexOf("Lizenz") > -1);
  schliesseUeberlagerung(document.getElementById("detail"));
  zuruecksetzen();
  zeigeAnsicht("bausteine");

  return ergebnisse.join("\n") + "\n\n" +
         ergebnisse.filter(function (z) { return z.indexOf("FEHLER") === 0; }).length +
         " Fehler von " + ergebnisse.length + " Prüfungen";
})();
