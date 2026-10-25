# Grid-Serving Storage – Arbeitsstand

Stand: 24.10.2026 · Online-Doc: https://claude.ai/artifact/1Guc2DxDeUFdGFACU7kRvN

Finanzierung, EMS-Konzept, gestufte Förderung, Schadlosstellung und Speicherbedarf sind ausgearbeitet; infra-kg liefert jetzt Globalstrahlung. Nichts ist committet.

## Ergebnisse

Das Konzept ist für den Kunden durchgehend schadlos und für den VNB über die Netzentgelte finanziert.

| Thema | Ergebnis | Status |
| --- | --- | --- |
| Finanzierung Betrieb | VNB zahlt Betrieb und Abrufe über die Netzentgelte (§ 139 Abs. 4 ElWG) | festgelegt |
| Kostenvergleich | Box-Lösung ca. halb so teuer wie ein Netzspeicher am Trafo; gegenüber VPP-Cloud nicht billiger, aber zuverlässiger und sicherer (Schätzung) | Annahmen offen |
| EMS / Home Assistant | Box ist zugleich EMS; Home Assistant nur über eigenen Kanal, nur lesend plus feste Parameterliste | festgelegt |
| Parameter und Vorrang | 8 Nutzerparameter, 6 Überschreibungsquellen, 10 Szenarien (A–J); Notstrom-Reserve nie überschreibbar | Vorschlag |
| Tarife | Tarifformel pro Kunde, täglicher Preisvektor für alle, signiert von einer Preisstelle der E-Control (eigene PKI-Rolle) | festgelegt |
| Förderung | Stufen 0–3 nach Steuerbarkeit; Auszahlung in Tranchen nach gemessener Netzdienlichkeit; Stufe 3 bis zur Freischaltung der Einspeisung auch ohne Entladen ins Netz | Prinzip festgelegt, Prozentsätze Platzhalter |
| Notstrom-Reserve | Bemessen aus Smart-Meter-Daten (Bestand) bzw. Erfahrungswerten (Neubau), nach 12 Monaten nachgeschärft; Wärmepumpe zählt nicht zur Grundreserve | festgelegt |
| Schadlosstellung | Ersatz = Ist minus Referenz ohne Eingriff + Verschleißpauschale, dazu Vergütung; Kunde netto nie im Minus | festgelegt, Verfahren Vorschlag |
| Speicherbedarf | Rechenweg je Segment; installiert ca. das Dreifache des Netto-Bedarfs | Vorschlag, Rechnung offen |
| Degradation | Heimspeicher altern vor allem kalendarisch (2–3 Prozentpunkte pro Jahr); Verschleißpauschale 5 ct/kWh, Obergrenze ca. 11 ct/kWh | Vorschlag |
| Wetterdaten | Globalstrahlung in infra-kg ergänzt (GeoSphere NWP und TAWES, Open-Meteo); alle Tests grün (1695 bestanden) | umgesetzt, nicht committet |
| Demo | Region Steyr / Steyr-Land; Demo und Daten baut Session infra-kg-austria-51 | festgelegt |

## Offene Entscheidungen

Fünf Punkte sind offen; die ersten beiden sind schnell zu treffen.

- [ ] Globalstrahlung in infra-kg committen?
- [ ] Bedarfsrechnung je Segment mit den SimBench-Netzen für Steyr durch Session infra-kg-austria-51?
- [ ] Platzhalter festlegen: Förder-Prozentsätze, Größe und Deckel der Grundreserve, Vergütung für Abruf und Vorhaltung
- [ ] Preisstelle bei der E-Control: Rechtsgrundlage und Lizenz der EPEX-Spotdaten klären
- [ ] Mit Smart Grids Austria abstimmen: maximale Dauer und Häufigkeit von Abrufen und Testabrufen

## Zuständigkeiten

Drei Sessions arbeiten im Repo teb-grid-serving-storage; niemand committet ohne Freigabe des Owners.

| Session | Betreut |
| --- | --- |
| EMS/Tarife | ems-konzept.md, ems-konzept-kurzfassung.md, arbeitsstand.md; Globalstrahlung in infra-kg |
| infra-kg-austria-90 (Recherche/Hardware) | research/\*, hardware-konzept.md |
| infra-kg-austria-51 (Demo/Daten) | Demo, SimBench-Netze, PV-Erkennung aus Orthofotos um Steyr |
| gemeinsam | anforderungen.md (nur kleine, gezielte Änderungen) |
