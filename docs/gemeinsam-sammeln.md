# Gemeinsam Heimabende sammeln: Konten, Datenbank, Keycloak

Stand: 07.09.2026 · Vorschlag zur Entscheidung, noch nichts gebaut.

## Der Vorschlag

Aus dem Bund kam die Idee: Supabase als Datenbank mit Konten anbinden, die
Anmeldung über das Keycloak des DPB laufen lassen, und dann gemeinsam
Heimabende sammeln. Die App bleibt dabei, was sie ist (eine statische Seite auf
GitHub Pages); dazu kommt ein Dienst, in den angemeldete Leute schreiben können.

## Was das ändert

Heute: 1038 Bausteine, erzeugt von `scripts/build.py`, ausgeliefert als eine
2,4 MB große Datei. Niemand kann von außen etwas hinzufügen, es gibt keine
Anmeldung, nichts kann kaputtgehen.

Morgen: Die 1038 Bausteine bleiben genau so (statisch, kostenlos, offline
lesbar). **Nur das Neue** liegt in Supabase: eigene Ideen, Korrekturen, Bewertungen.
Die App lädt beim Start zusätzlich die freigegebenen Beiträge aus Supabase und
mischt sie unter die Kacheln. Wer sich anmeldet, kann Beiträge einreichen und
seine eigenen bearbeiten.

Warum nicht alles in die Datenbank? Wegen der Zahlen unten (Egress) und weil
die Lizenzpflichten der fünf Quellen weiter über `build.py` laufen sollen.

## Zahlen zu Supabase (Free-Tarif, Stand 09/2026)

| Grenze | Free | Was das für uns heißt |
|---|---:|---|
| Datenbankgröße | 500 MB | Ein Baustein ist im Schnitt 2,4 KB. Platz für über 100.000 Beiträge. |
| Aktive Nutzer/Monat | 50.000 | Der ganze DPB passt viele Male hinein. |
| Datenverkehr (Egress) | 5 GB/Monat | Würde die App ihre 2,2 MB Grunddaten aus Supabase laden, wären das nur ~2.300 Aufrufe im Monat. Deshalb Grunddaten weiter von GitHub Pages, aus Supabase nur die kleinen Beiträge. |
| Projekte | 2 | Reicht: eins für uns. |
| Pause bei Inaktivität | nach 7 Tagen ohne Datenbankzugriff | Wird das Projekt eine Woche nicht benutzt, schläft es ein und die App zeigt keine Beiträge, bis jemand es im Dashboard weckt. Gegenmittel: ein täglicher Ping (GitHub Action, kostenlos) oder Pro. |
| Pro-Tarif | 25 $/Monat | Keine Pause, 8 GB, 250 GB Egress. Erst nötig, wenn es wirklich viele nutzen. |
| Region | Frankfurt wählbar | Daten bleiben in der EU (DSGVO). |

Quelle: https://supabase.com/pricing und https://supabase.com/docs/guides/platform/free-project-pausing

## Drei Wege

**A) Supabase + DPB-Keycloak (der Vorschlag aus dem Bund).**
Anmeldung mit dem DPB-Konto, keine neuen Passwörter. Supabase kennt Keycloak
als Anmeldedienst von Haus aus. Voraussetzung: jemand mit Admin-Rechten im
Keycloak legt einen Client an (Checkliste unten). Solange das nicht passiert
ist, kann sich niemand anmelden. Wer nicht im DPB ist, bleibt draußen.

**B) Supabase mit eigener Anmeldung (Magic Link per E-Mail), Keycloak später.**
Gleiche Datenbank, gleiches Schema, nur die Anmeldung läuft zunächst über einen
E-Mail-Link, den Supabase selbst verschickt. Braucht niemanden vom Bund, geht
sofort. Keycloak lässt sich danach als zweiter Anmeldeweg dazuschalten, ohne
dass sich an der Datenbank etwas ändert. Nachteil: E-Mail-Versand im Free-Tarif
ist auf wenige Mails pro Stunde begrenzt, für den Start reicht das.

**C) Ohne Dienst: Beiträge über GitHub.**
Ein Formular in der App erzeugt einen fertigen GitHub-Issue, `build.py` liest
freigegebene Issues ein. Null Infrastruktur, null Kosten, keine Pause. Aber jede
beitragende Person braucht ein GitHub-Konto, und Bearbeiten ist umständlich.
Für Gruppenführer am Handy im Heim ist das eine echte Hürde.

**Empfehlung: B, mit A als Ziel.** Die Datenbank wird so gebaut, dass Keycloak
jederzeit dazukommt. Das Sammeln kann in dieser Woche losgehen, statt auf einen
Termin mit der DPB-IT zu warten.

## Was gesammelt wird (Datenmodell)

Eine Tabelle `beitraege`. Jeder Beitrag ist ein Baustein im Schema aus
`data/SCHEMA.md`, gespeichert als JSON-Feld, dazu Verwaltungsfelder:

| Feld | Bedeutung |
|---|---|
| `id` | Kennung, in der App mit Präfix `db-` |
| `autor_id` | wer es eingereicht hat (Konto-Kennung, keine E-Mail) |
| `autor_name` | Anzeigename, frei wählbar |
| `status` | `entwurf` → `eingereicht` → `freigegeben` (oder `abgelehnt`) |
| `lizenz` | fest `CC BY-SA 4.0`; Häkchen beim Einreichen |
| `element` | der Baustein selbst (JSON, gleiche Felder wie `elemente.json`) |
| `erstellt`, `geaendert` | Zeitstempel |

Dazu eine kleine Tabelle `profile` (Anzeigename, Rolle `mitglied` oder
`redaktion`). Die Redaktion gibt Beiträge frei, wie heute die Einträge in
`data/redaktion.json`.

Zugriffsregeln (in Supabase „Row Level Security", liegen in `supabase/schema.sql`):
- Jeder, auch ohne Konto, liest `freigegeben`.
- Angemeldete sehen und bearbeiten ihre eigenen Beiträge in jedem Status.
- Redaktion sieht alles und setzt den Status.

Warum ein JSON-Feld statt 30 Spalten: Das Schema hat sich in zwei Wochen zweimal
geändert (`element_typ` weg, fünf Spiel-Achsen dazu). Eine Spalte pro Feld hieße
jedes Mal eine Datenbank-Migration. Das JSON-Feld nimmt das Schema so, wie
`build.py` es liefert, und die App prüft es beim Anzeigen wie alles andere.

## Was beim Datenschutz zu beachten ist

- Keycloak liefert Name und E-Mail. Gespeichert wird nur die Konto-Kennung und
  ein selbst gewählter Anzeigename. E-Mail bleibt bei Supabase Auth, nicht in
  unseren Tabellen.
- Region Frankfurt. Supabase bietet einen AV-Vertrag im Dashboard an; für einen
  Verein sollte das jemand vom Bund einmal abnicken.
- Beiträge sind öffentlich (CC BY-SA), das muss beim Einreichen klar stehen.

## Checkliste für den Keycloak-Admin des DPB

Ohne diese vier Angaben kann Weg A nicht starten. Sie kommen vom Admin des Keycloak:

1. Im Realm einen neuen Client anlegen, Typ **OpenID Connect**, Zugriff
   **confidential** (Client Authentication an).
2. Als gültige Redirect-URI eintragen:
   `https://<projekt-kennung>.supabase.co/auth/v1/callback`
   (die Projekt-Kennung steht im Supabase-Dashboard, sobald das Projekt existiert)
3. Uns geben: **Client-ID**, **Client-Secret** und die **Issuer-URL** des Realms
   (steht unter `<keycloak>/realms/<realm>/.well-known/openid-configuration`).
4. Der Scope `openid` muss erlaubt sein (Pflicht ab Keycloak 22).

Quelle: https://supabase.com/docs/guides/auth/social-login/auth-keycloak

## Was du selbst tun musst (kann Claude nicht)

1. Konto auf https://supabase.com anlegen (GitHub-Login geht) und ein Projekt
   erstellen, Region **Frankfurt (eu-central-1)**.
2. Im Dashboard unter *SQL Editor* die Datei `supabase/schema.sql` einfügen und
   ausführen.
3. Unter *Project Settings → API* zwei Werte kopieren: **Project URL** und
   **anon key**. Beide dürfen öffentlich in der App stehen, die Zugriffsregeln
   schützen die Daten.
4. Für Weg A: die Checkliste oben an den Keycloak-Admin, danach unter
   *Authentication → Providers → Keycloak* eintragen.

Sobald URL und anon key da sind, baue ich die App-Seite: Anmelden, Formular
„Idee einreichen" (Entwurf liegt in `docs/eigene-ideen-erfassen.md`), Beiträge
in den Kacheln, Redaktionsansicht.

## Was das für die App bedeutet

- Die Supabase-Bibliothek (ca. 100 KB) kommt als Datei nach `web/lib/`, nicht
  von einem fremden Server, damit der Doppelklick auf `index.html` weiter geht.
- Ohne Netz oder bei schlafendem Projekt läuft die App wie heute, nur ohne
  Beiträge. Ein Fehler beim Laden darf nie die 1038 Grundbausteine blockieren.
- Die spätere Flutter-App spricht dieselbe Supabase-Tabelle an, das Schema bleibt.
