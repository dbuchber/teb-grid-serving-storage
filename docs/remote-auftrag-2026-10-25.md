# Auftrag für die Remote-Session auf hetzner (25.10.2026)

Kontext: TEB AI Hackathon, Challenge „Grid-Serving Storage“. Abgabe heute **11:30**, Pitch ab 12:00.
Steyr ist nur unsere gewählte Testregion. Live-Demo: https://teb-hackathon.bbger.at (Präsentation unter `/`, ausführlich unter `/details`).

Material in diesem Ordner:
- `docs/challenge/challenge-grid-serving-storage.txt` – Aufgabentext
- `docs/challenge/submission-template.txt` – was die Jury bei der Abgabe sehen will
- `docs/context/profil-v2.md` – Interoperabilitätsprofil v2 (Akteure, P1–P10, Grenzen, PKI, LoRaWAN)
- `docs/context/site/index.html` (Präsentation) und `docs/context/site/details.html` (ausführliche Seite)
- `docs/research/`, `docs/ems-konzept.md`, `docs/anforderungen.md`, `gridsim/` (Simulation), `apps/insight-harbor/` (Lovable-App)

## Fragen des Owners

1. **Großspeicher integrieren:** Die Challenge nennt Speicher „von kleinen Haushaltsspeichern bis zu großen Speichern an Gewerbestandorten“.
   Wie bauen wir Gewerbe- und Großspeicher ein, (a) ins Interoperabilitätsprofil (Akteure, Prozesse, Schnittstellen,
   Unterschiede zur Box im Haushalt, z. B. Anschluss an Mittelspannung, eigene Leittechnik, Vermarktung, Regeln in AT),
   (b) in die Simulation (`gridsim`, Daten in Steyr: welche offenen Quellen für Gewerbestandorte/Großspeicher),
   (c) in Präsentation und Webseite? Mit Aufwand je Schritt.
2. **Lückenanalyse für die Abgabe:** Was fehlt noch, um Challenge und Submission-Template zu erfüllen?
   Jedes Feld des Templates (Projekt, Problem, Lösung, AI, Security, Daten, Tech-Stack, Links, Notes) mit Status und Textvorschlag.
   Priorisiert nach dem, was bis 11:30 machbar ist.

## Ergebnis

- `docs/grossspeicher-integration.md` und `docs/abgabe-lueckenanalyse.md` (Deutsch), Textvorschläge für die Abgabe auf Englisch.
- Quellen nennen; Online-Quellen zusätzlich als Markdown unter `docs/research/` ablegen.

## Grenzen

- Nicht committen, nicht pushen, nichts deployen, keine laufenden Container ändern (`teb-hackathon-web-1`, `gridsim-api`, Caddy).
- Nur in diesem Ordner schreiben. Rechnen auf diesem Server ist erlaubt.
