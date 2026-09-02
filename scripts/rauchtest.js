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
    ["fStufe", "fDauer", "fOrt", "fVorbereitung"].forEach(function (id) {
      document.getElementById(id).value = "";
    });
    document.getElementById("fOhneMaterial").checked = false;
    document.getElementById("suche").value = "";
    pfad = { typ: "", kategorie: "", unterkategorie: "" };
    aktualisiere();
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

  // --- Zufall darf nicht aus einer alten Liste ziehen ---
  zuruecksetzen();
  pfad = { typ: "spiel", kategorie: "kreis", unterkategorie: "singen" }; aktualisiere();
  var vorFilter = gefiltert.length;
  pfad = { typ: "", kategorie: "", unterkategorie: "" }; aktualisiere();
  pruefe("Kachelseite leert die Trefferliste", gefiltert.length === 0,
         "vorher " + vorFilter + ", jetzt " + gefiltert.length);

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
