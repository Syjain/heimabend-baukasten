/* Randfälle-Test für den Heimabend-Baukasten – Ergänzung zu rauchtest.js.

   Der Rauchtest prüft, dass die Hauptwege funktionieren. Dieser Test prüft die
   Ränder: leere Filter, null Treffer, eine leere Sammlung, die Zeile
   "Heute sind wir" mit 1 und 40 Kindern, und einen Browser, in dem
   localStorage gar nicht benutzbar ist (privates Fenster).

   So benutzt du ihn (genau wie rauchtest.js):
   1. web/index.html im Browser öffnen
   2. Entwicklerwerkzeuge öffnen (Mac: Wahltaste + Befehlstaste + I), "Konsole"
   3. Den gesamten Inhalt dieser Datei hineinkopieren, Eingabetaste

   Ausgabe: je Prüfung eine Zeile "ok" oder "FEHLER". Zeilen mit "Befund" sind
   keine Fehler, sondern Beobachtungen, über die man entscheiden sollte.
   Prüfungen für Funktionen, die es in der geöffneten Fassung der App nicht gibt,
   erscheinen als "übersprungen".

   Der Test stellt Anzahl, Sammlung, Filter und Pfad am Ende wieder so, wie sie
   vorher waren; gespeicherte Pläne und eigene Ideen rührt er nicht an (bei der
   Prüfung ohne localStorage wird der Zugriff nur vorübergehend gesperrt). */
(function () {
  var ergebnisse = [];
  function pruefe(name, bedingung, zusatz) {
    ergebnisse.push((bedingung ? "ok    " : "FEHLER") + "  " + name +
                    (zusatz !== undefined ? "  [" + zusatz + "]" : ""));
  }
  function befund(text) { ergebnisse.push("Befund  " + text); }
  function uebersprungen(name, grund) {
    ergebnisse.push("übersprungen  " + name + "  [" + grund + "]");
  }
  /* Führt fn aus; wirft sie, ist das ein Fehler. fn gibt true/false oder
     {ok, zusatz} zurück. */
  function sicher(name, fn) {
    try {
      var r = fn();
      if (r && typeof r === "object") pruefe(name, r.ok, r.zusatz);
      else pruefe(name, r !== false);
    } catch (f) {
      ergebnisse.push("FEHLER  " + name + "  [wirft: " + (f && f.message ? f.message : f) + "]");
    }
  }
  function da() {
    for (var i = 0; i < arguments.length; i++) {
      if (typeof window[arguments[i]] === "undefined") return false;
    }
    return true;
  }
  function el(id) { return document.getElementById(id); }
  function zuruecksetzen() {
    el("suche").value = "";
    pfad = leererPfad();
    setzeFilterZurueck();
    setzeSammlung(false);       // wie im Rauchtest: Zahlen beziehen sich auf die ganze Sammlung
  }

  var hatApp = da("ALLE", "aktualisiere", "leererPfad", "setzeFilterZurueck", "setzeSammlung",
                  "gefiltert");
  if (!hatApp) {
    return "FEHLER  Die App ist nicht geladen (ALLE, aktualisiere … fehlen). " +
           "Diesen Test in der Konsole von web/index.html ausführen.";
  }

  var vorherPfad = pfad;
  var vorherKern = typeof nurKern !== "undefined" ? nurKern : true;
  var vorherAnzahl = typeof heuteAnzahl !== "undefined" ? heuteAnzahl : 0;
  var vorherSuche = el("suche").value;

  // ------------------------------------------------------------ 1. Daten
  var nachId = {};
  var doppelt = [];
  ALLE.forEach(function (e) {
    if (nachId[e.id]) doppelt.push(e.id);
    nachId[e.id] = e;
  });
  pruefe("IDs sind eindeutig", doppelt.length === 0, doppelt.slice(0, 3).join(", "));
  pruefe("Dauer: min <= max und beide positiv",
         ALLE.every(function (e) { return e.dauer_min >= 1 && e.dauer_max >= e.dauer_min; }),
         ALLE.filter(function (e) { return !(e.dauer_min >= 1 && e.dauer_max >= e.dauer_min); })
           .map(function (e) { return e.id; }).slice(0, 3).join(", "));
  pruefe("Gruppengröße: min <= max, wo beides steht",
         ALLE.every(function (e) {
           return !(e.gruppe_min && e.gruppe_max) || e.gruppe_min <= e.gruppe_max;
         }));
  pruefe("Titel und Beschreibung sind nie leer",
         ALLE.every(function (e) {
           return typeof e.titel === "string" && e.titel.trim() &&
                  typeof e.beschreibung === "string" && e.beschreibung.trim();
         }));
  pruefe("kein Titel und keine Kurzfassung zeigt 'undefined', 'null' oder 'NaN'",
         ALLE.every(function (e) {
           return !/\b(undefined|null|NaN)\b/.test(e.titel + " " + (e.kurz || ""));
         }),
         ALLE.filter(function (e) { return /\b(undefined|null|NaN)\b/.test(e.titel + " " + (e.kurz || "")); })
           .map(function (e) { return e.id; }).slice(0, 3).join(", "));
  pruefe("in keinem Text steckt ein <script> oder on…=-Attribut",
         ALLE.every(function (e) {
           return !/<\s*script|\son[a-z]+\s*=/i.test([e.titel, e.kurz, e.beschreibung, e.tipps].join("\n"));
         }));
  pruefe("Dubletten verweisen auf vorhandene Elemente und zurück",
         ALLE.every(function (e) {
           return (e.dubletten || []).every(function (d) {
             return nachId[d] && (nachId[d].dubletten || []).indexOf(e.id) > -1;
           });
         }));
  pruefe("Varianten verweisen auf vorhandene Elemente",
         ALLE.every(function (e) {
           return (e.varianten || []).every(function (v) { return !!nachId[v.id]; });
         }));
  pruefe("jedes Element hat mindestens einen Slot",
         ALLE.every(function (e) { return e.slots && e.slots.length > 0; }));

  // ------------------------------------------- 2. Leere Filter, null Treffer
  sicher("alle Filter leer: Sammlung erscheint vollständig", function () {
    zuruecksetzen();
    pfad = leererPfad(); pfad.unterkategorie = "__alle__";
    aktualisiere();
    return { ok: gefiltert.length === ALLE.length, zusatz: gefiltert.length + " von " + ALLE.length };
  });
  sicher("Suche ohne Treffer: leere Liste, Meldung, Zufall gesperrt", function () {
    zuruecksetzen();
    el("suche").value = "qqqxyzzy";
    aktualisiere();
    return { ok: gefiltert.length === 0 && /Nichts gefunden|bleibt nichts übrig/.test(document.body.textContent) &&
                 el("zufallKnopf").disabled === true,
             zusatz: gefiltert.length + " Treffer" };
  });
  sicher("Zufall-Knopf bei null Treffern tut nichts Schlimmes", function () {
    var knopf = el("zufallKnopf");
    knopf.disabled = false;               // ein Klick von Hand oder per Tastatur-Trick
    knopf.click();
    aktualisiere();
    return !el("detail") || el("detail").hidden !== false || gefiltert.length > 0
           ? true : { ok: false, zusatz: "Detailansicht öffnet sich ohne Treffer" };
  });
  sicher("Suche nur aus Leerzeichen zählt als leer", function () {
    zuruecksetzen();
    el("suche").value = "    ";
    pfad = leererPfad(); pfad.unterkategorie = "__alle__";
    aktualisiere();
    return { ok: gefiltert.length === ALLE.length, zusatz: gefiltert.length };
  });
  sicher("Suche mit Sonderzeichen wirft nicht", function () {
    zuruecksetzen();
    var wirft = false;
    ["(", "[", "\\", "*", "?", "<b>", "a|b", "'; drop", "%", "\u0000"].forEach(function (s) {
      try { el("suche").value = s; aktualisiere(); } catch (f) { wirft = s; }
    });
    zuruecksetzen();
    return { ok: wirft === false, zusatz: wirft === false ? "" : "wirft bei " + JSON.stringify(wirft) };
  });
  sicher("sehr lange Suche (5000 Zeichen) wirft nicht", function () {
    zuruecksetzen();
    el("suche").value = new Array(5001).join("a");
    aktualisiere();
    var n = gefiltert.length;
    zuruecksetzen();
    return { ok: n === 0, zusatz: n + " Treffer" };
  });
  sicher("unmögliche Filterkombination: 0 Treffer, Kacheln melden es", function () {
    zuruecksetzen();
    el("fDauer").value = "10";
    el("fOhneMaterial").checked = true;
    el("fStufe").value = "Ältere";
    el("suche").value = "qqqxyzzy";
    pfad = leererPfad();
    aktualisiere();
    var text = document.body.textContent;
    zuruecksetzen();
    return { ok: /Nichts gefunden|bleibt nichts übrig/.test(text) };
  });
  sicher("Filter zurücksetzen holt die ganze Sammlung zurück", function () {
    el("suche").value = "qqqxyzzy"; aktualisiere();
    var knopf = Array.prototype.filter.call(document.querySelectorAll("button[data-weg]"),
      function (b) { return /^Filter zurücksetzen/.test(b.textContent); })[0];
    if (!knopf) return { ok: false, zusatz: "kein Zurücksetzen-Knopf bei 0 Treffern" };
    knopf.click();
    var suchfeld = el("suche").value;
    pfad = leererPfad(); pfad.unterkategorie = "__alle__"; aktualisiere();
    // Behoben 18.10.2026: der Knopf leert auch das Suchfeld (Runde 2).
    return { ok: gefiltert.length > 0 && suchfeld === "",
             zusatz: gefiltert.length + " Treffer, Suchfeld danach: '" + suchfeld + "'" };
  });

  // ------------------------------------------ 3. Heute sind wir: 1 und 40
  if (!da("setzeAnzahl", "ANZAHL_STUFEN", "heuteAnzahl") || !el("heuteAnzahl")) {
    uebersprungen("Zeile 'Heute sind wir'", "diese Fassung der App hat sie nicht");
  } else {
    var gesehen = {};
    [1, 2, 40, 100, 0, -3, "abc", "", null, undefined, NaN, 3, 25, "25", 7.5].forEach(function (z) {
      sicher("setzeAnzahl(" + String(z) + ") wirft nicht und landet auf einer gültigen Stufe", function () {
        zuruecksetzen();
        setzeAnzahl(z);
        var gueltig = ANZAHL_STUFEN.indexOf(heuteAnzahl) > -1;
        var feldPasst = el("heuteAnzahl").value === String(heuteAnzahl);
        var hinweisPasst = (heuteAnzahl === 0) === (el("heuteHinweis").textContent === "");
        gesehen[String(z)] = heuteAnzahl;
        return { ok: gueltig && feldPasst && hinweisPasst,
                 zusatz: "-> " + heuteAnzahl + (gueltig ? "" : ", keine Stufe") +
                         (feldPasst ? "" : ", Feld zeigt " + el("heuteAnzahl").value) +
                         (hinweisPasst ? "" : ", Hinweis passt nicht") };
      });
    });
    if (gesehen["1"] === 0) {
      befund("Anzahl 1 ist keine Stufe (kleinste ist " + ANZAHL_STUFEN[1] + "); " +
             "setzeAnzahl(1) wird stillschweigend zu 'egal'. Im Alltag erreichbar nur über " +
             "gespeicherte Werte, nicht über die Knöpfe.");
    }
    if (gesehen["40"] === 0) {
      befund("Anzahl 40 ist keine Stufe (größte ist " + ANZAHL_STUFEN[ANZAHL_STUFEN.length - 1] +
             "); setzeAnzahl(40) wird stillschweigend zu 'egal'. Eine Gruppe von 40 kann die " +
             "App nicht ausdrücken.");
    }

    // Das Filterverhalten an den Rändern der Stufenleiter
    [ANZAHL_STUFEN[1], ANZAHL_STUFEN[ANZAHL_STUFEN.length - 1]].forEach(function (n) {
      sicher("Anzahl " + n + ": jede Liste folgt der Regel (min <= n <= max, fehlende Angaben bleiben)", function () {
        zuruecksetzen();
        setzeAnzahl(n);
        pfad = leererPfad(); pfad.unterkategorie = "__alle__"; aktualisiere();
        var falsch = gefiltert.filter(function (e) {
          return (e.gruppe_min && e.gruppe_min > n) || (e.gruppe_max && e.gruppe_max < n);
        });
        var rest = ALLE.filter(function (e) {
          return !((e.gruppe_min && e.gruppe_min > n) || (e.gruppe_max && e.gruppe_max < n));
        }).length;
        return { ok: falsch.length === 0 && gefiltert.length === rest,
                 zusatz: gefiltert.length + " Treffer, erwartet " + rest +
                         (falsch.length ? ", falsch: " + falsch[0].id : "") };
      });
    });
    sicher("Knöpfe − und + bleiben an den Enden stehen", function () {
      zuruecksetzen();
      setzeAnzahl(0);
      stelleAnzahl(-1);
      var unten = heuteAnzahl;
      var untenGesperrt = el("heuteWeniger").disabled;
      setzeAnzahl(ANZAHL_STUFEN[ANZAHL_STUFEN.length - 1]);
      stelleAnzahl(+1);
      var oben = heuteAnzahl;
      var obenGesperrt = el("heuteMehr").disabled;
      return { ok: unten === 0 && oben === ANZAHL_STUFEN[ANZAHL_STUFEN.length - 1] &&
                   untenGesperrt && obenGesperrt,
               zusatz: unten + " / " + oben };
    });
    sicher("Anzahl wirkt auch auf die Kacheln (andere Zahl als ohne Anzahl)", function () {
      zuruecksetzen();
      setzeAnzahl(0); pfad = leererPfad(); aktualisiere();
      var ohne = Array.prototype.map.call(document.querySelectorAll("#kacheln .kachel"),
                                          function (k) { return k.textContent; }).join("|");
      setzeAnzahl(ANZAHL_STUFEN[1]); aktualisiere();
      var mit = Array.prototype.map.call(document.querySelectorAll("#kacheln .kachel"),
                                         function (k) { return k.textContent; }).join("|");
      return { ok: ohne !== mit };
    });
    sicher("Hinweis zur Anzahl nennt passende und offene Bausteine in Zahlen", function () {
      zuruecksetzen();
      setzeAnzahl(8);
      var t = el("heuteHinweis").textContent;
      return { ok: /^\d+ Bausteine passen für 8 Kinder – davon \d+ ohne Angabe/.test(t), zusatz: t };
    });
    sicher("Anzahl 25 sagt ehrlich '25 Kinder' (kein 'oder mehr', kein '+')", function () {
      zuruecksetzen();
      setzeAnzahl(25);
      var t = el("heuteHinweis").textContent;
      var wahl = el("heuteAnzahl").options[el("heuteAnzahl").selectedIndex].textContent;
      return { ok: /für 25 Kinder/.test(t) && !/mehr/.test(t) && wahl === "25 Kinder",
               zusatz: t + " / " + wahl };
    });
    // Zustand zurück
    setzeAnzahl(vorherAnzahl);
  }

  // ----------------------------------------------- 4. Leere Sammlung (ALLE = [])
  if (!da("zeichneKacheln") && !da("planWuerfeln")) {
    uebersprungen("leere Sammlung", "benötigte Funktionen fehlen");
  } else {
    var echteAlle = ALLE;
    var echterNachId = typeof NACH_ID !== "undefined" ? NACH_ID : null;
    try {
      ALLE = [];
      if (echterNachId) NACH_ID = {};
      sicher("leere Sammlung: aktualisiere() wirft nicht", function () {
        pfad = leererPfad(); el("suche").value = ""; aktualisiere();
        return { ok: gefiltert.length === 0 };
      });
      sicher("leere Sammlung: Zeile 'Heute sind wir' wirft nicht", function () {
        if (!da("zeichneHeute")) return true;
        zeichneHeute();
        return true;
      });
      if (da("planWuerfeln", "leererPlan", "zeichnePlan", "liesRahmen")) {
        sicher("leere Sammlung: Würfeln im Planer wirft nicht", function () {
          plan = leererPlan();
          liesRahmen();
          planWuerfeln();
          zeichnePlan();
          return true;
        });
        sicher("leere Sammlung: Plan-Text lässt sich bilden", function () {
          return typeof planAlsText() === "string";
        });
      }
      sicher("leere Sammlung: Zufall-Knopf ist gesperrt", function () {
        return el("zufallKnopf").disabled === true;
      });
    } finally {
      ALLE = echteAlle;
      if (echterNachId) NACH_ID = echterNachId;
      if (da("leererPlan")) plan = leererPlan();
      zuruecksetzen();
      if (da("zeichnePlan")) zeichnePlan();
    }
  }

  // ------------------------------------- 5. localStorage nicht benutzbar
  // Privates Fenster oder gesperrte Cookies: schon das Lesen von
  // window.localStorage wirft (SecurityError). Der Test sperrt den Zugriff
  // nur für die Dauer der Prüfung.
  (function () {
    var beschr = Object.getOwnPropertyDescriptor(window, "localStorage");
    if (!beschr || !beschr.configurable) {
      uebersprungen("localStorage gesperrt", "dieser Browser lässt window.localStorage nicht überschreiben");
      return;
    }
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      get: function () { throw new Error("SecurityError (nur ein Test)"); }
    });
    try {
      var kaputt = false;
      try { void window.localStorage; } catch (f) { kaputt = true; }
      pruefe("Sperre greift (Zugriff auf localStorage wirft)", kaputt);
      [["ladeSammlung", []], ["speichereSammlung", []], ["ladeAnzahl", []],
       ["speichereAnzahl", []], ["ladePlan", []], ["speicherePlan", []],
       ["ladeEigeneIdeen", []], ["speichereEigeneIdeen", []]].forEach(function (p) {
        if (!da(p[0])) { uebersprungen(p[0] + " ohne localStorage", "gibt es hier nicht"); return; }
        sicher(p[0] + "() ohne localStorage wirft nicht", function () {
          window[p[0]].apply(null, p[1]);
          return true;
        });
      });
      if (da("setzeSammlung")) {
        sicher("setzeSammlung() ohne localStorage schaltet trotzdem um", function () {
          setzeSammlung(true);
          var kern = (typeof nurKern !== "undefined") ? nurKern : true;
          setzeSammlung(false);
          return { ok: kern === true && (typeof nurKern === "undefined" || nurKern === false) };
        });
      }
      if (da("setzeAnzahl", "ANZAHL_STUFEN")) {
        sicher("setzeAnzahl() ohne localStorage wirkt trotzdem", function () {
          setzeAnzahl(ANZAHL_STUFEN[2]);
          var ok = heuteAnzahl === ANZAHL_STUFEN[2];
          setzeAnzahl(0);
          return { ok: ok };
        });
      }
      if (da("planWuerfeln", "leererPlan")) {
        sicher("Plan würfeln ohne localStorage wirft nicht", function () {
          plan = leererPlan(); liesRahmen(); planWuerfeln(); zeichnePlan();
          return true;
        });
      }
      if (da("oeffneIdeenForm", "EIGENE_IDEEN")) {
        sicher("eigene Idee speichern ohne localStorage: Fehlermeldung statt Absturz", function () {
          var vorher = EIGENE_IDEEN.length;
          oeffneIdeenForm(null);
          el("iTitel").value = "Kantentest ohne Speicher";
          el("iBeschreibung").value = "Diese Idee darf nicht gespeichert werden, wenn der Speicher gesperrt ist.";
          el("iSpeichern").click();
          var ok = EIGENE_IDEEN.length === vorher && !el("iFehler").hidden;
          if (da("schliesseUeberlagerung")) schliesseUeberlagerung(el("ideenForm"), true);
          return { ok: ok, zusatz: EIGENE_IDEEN.length + " eigene Ideen" };
        });
      }
    } finally {
      Object.defineProperty(window, "localStorage", beschr);
    }
  })();

  // ------------------------- Runde 2 (18.10.2026): Gespeichertes und Links
  (function () {
    var schluessel = "heimabend-plan", vorher = null, hatte = true;
    try { vorher = localStorage.getItem(schluessel); } catch (f) { hatte = false; }
    sicher("gespeicherter Plan mit unbekannten IDs: wird still ignoriert, Plätze bleiben offen", function () {
      if (!hatte || !da("ladePlan", "planElement", "zeichnePlan", "NACH_ID")) {
        return { ok: true, zusatz: "übersprungen (kein Speicher oder keine Planfunktionen)" };
      }
      var echte = ALLE[0].id;
      localStorage.setItem(schluessel, JSON.stringify({ plan: {
        eroeffnung: "gibt-es-nicht-1", einstieg: echte, abschluss: "gibt-es-nicht-2",
        schluss: "__proto__", haupt: ["gibt-es-nicht-3", echte, 42, "constructor"] }, rahmen: {} }));
      ladePlan();
      zeichnePlan();
      var ok = plan.eroeffnung === null && plan.abschluss === null && plan.schluss === null &&
               plan.einstieg === echte && plan.haupt.length === 4 && plan.haupt[0] === null &&
               plan.haupt[1] === echte && plan.haupt[2] === null && plan.haupt[3] === null &&
               !planElement("haupt", 0) && !!planElement("einstieg");
      return { ok: ok, zusatz: JSON.stringify(plan.haupt) };
    });
    sicher("Vormerkungen mit unbekannten IDs: nichts bricht, Zähler zählt nur Vorhandenes", function () {
      if (!da("ladeVormerkungen", "vorgemerkteElemente", "zeichneVorbereiten")) {
        return { ok: true, zusatz: "übersprungen" };
      }
      var alt = null; try { alt = localStorage.getItem("heimabend-vormerken"); } catch (f) {}
      var echte = ALLE[0].id;
      localStorage.setItem("heimabend-vormerken", JSON.stringify({ version: 1,
        ids: ["gibt-es-nicht", echte, "constructor", 7] }));
      ladeVormerkungen();
      zeichneVorbereiten();
      var n = vorgemerkteElemente().length;
      if (alt === null) localStorage.removeItem("heimabend-vormerken");
      else localStorage.setItem("heimabend-vormerken", alt);
      ladeVormerkungen();
      return { ok: n === 1, zusatz: n + " vorhanden" };
    });
    if (hatte) {
      try {
        if (vorher === null) localStorage.removeItem(schluessel);
        else localStorage.setItem(schluessel, vorher);
      } catch (f) {}
      if (da("ladePlan")) ladePlan();
    }
    if (da("textZuHtml")) {
      sicher("Adressen im Text: Satzzeichen am Ende gehören nicht in den Link", function () {
        var h = textZuHtml("Siehe https://stellarium-web.org/. Oder https://r9.whiteboardfox.com, " +
                           "(https://a.de/x), https://b.de/y?a=1&b=2; ja!");
        var ziele = [];
        h.replace(/href="([^"]*)"/g, function (m, z) { ziele.push(z); return m; });
        var soll = ["https://stellarium-web.org/", "https://r9.whiteboardfox.com",
                    "https://a.de/x", "https://b.de/y?a=1&amp;b=2"];
        return { ok: JSON.stringify(ziele) === JSON.stringify(soll) &&
                     h.indexOf("</a>.") > -1 && h.indexOf("</a>,") > -1,
                 zusatz: ziele.join(" | ") };
      });
      sicher("Adresse in Liste und mitten im Satz bleibt ganz", function () {
        var h = textZuHtml("- Mehr unter https://example.org/a-b_c.html und weiter");
        return { ok: h.indexOf('href="https://example.org/a-b_c.html"') > -1, zusatz: h };
      });
    }
  })();

  // -------------------------------------------- Zustand wiederherstellen
  zuruecksetzen();
  el("suche").value = vorherSuche;
  pfad = vorherPfad || leererPfad();
  setzeSammlung(vorherKern);
  if (da("setzeAnzahl")) setzeAnzahl(vorherAnzahl);
  if (da("leererPlan", "zeichnePlan")) { plan = leererPlan(); zeichnePlan(); }
  aktualisiere();

  var fehler = ergebnisse.filter(function (z) { return z.indexOf("FEHLER") === 0; }).length;
  var anzahl = ergebnisse.filter(function (z) {
    return z.indexOf("ok") === 0 || z.indexOf("FEHLER") === 0;
  }).length;
  return ergebnisse.join("\n") + "\n\n" + fehler + " Fehler von " + anzahl + " Prüfungen";
})();
