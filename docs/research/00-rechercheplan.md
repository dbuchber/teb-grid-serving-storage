# Rechercheplan: Grid-Serving Storage

Stand: 23.10.2026. Ziel: Faktenbasis für ein IES-Interoperabilitätsprofil und den Pitch.

## Arbeitsthese

Netzbetreiber und Stromanbieter nutzen Kundenspeicher und PV-Wechselrichter
**in beide Richtungen**: abregeln bzw. laden bei Überschuss, einspeisen bzw.
entladen bei Last. Ein Kommunikationsmodul am Gerät nimmt signierte Befehle an.
Der Smart Meter verifiziert die Reaktion unabhängig. Regelmäßige Testabrufe
ermitteln je Gerät/Typ Reaktionszeit und Zuverlässigkeit.

**Position:** Wechselrichter und Speicher müssen eine **standardisierte
Steuerschnittstelle** anbieten (Pflicht, herstellerunabhängig).

## Geltungsbereich

- EU-Rahmen als Basis
- Länder: **DE, FR, IT, ES, NL** (je kurz), plus **AT** als Bezug zum
  Challenge-Partner Smart Grids Austria
- Prior art außerhalb der EU nur, wenn direkt übertragbar (z. B. Australien, Kalifornien)

## Themenblöcke

### 1. Regulierung & Finanzierung → `01-regulierung-finanzierung.md`
- Was erlaubt bzw. verlangt der EU-Rahmen? (Strommarktdesign-Reform 2024,
  Network Code Demand Response, Art. 32 Elektrizitätsrichtlinie: Flexibilität für Netzbetreiber)
- Nationale Modelle zur Steuerbarkeit gegen Vergütung: §14a EnWG (DE), ElWG (AT),
  Pendants in FR/IT/ES/NL
- Vergütungsformen: Netzentgeltreduktion, Verfügbarkeit, Abruf, Flex-Märkte
- Darf der Netzbetreiber Flexibilität als Netzkosten verrechnen? (Opex vs. Capex)
- Konflikt Markt vs. Netz: Ampelmodell, Vorrangregeln
- Größenordnung: Kosten Netzausbau vs. Kosten Flexibilität (Zahlen mit Quelle)

### 2. Pilotprojekte & Flex-Märkte → `02-pilotprojekte.md`
- GOPACS (NL), Piclo Flex (UK), enera (DE), NODES, IntraFlex, Project EDGE (AU)
- Je Projekt: Akteure, Geräte, Kommunikationsweg, Vergütung, Ergebnis, Probleme
- Gab es Projekte mit **aktivem Entladen** aus Heimspeichern für das Verteilnetz?
- Was hat bei Kleinanlagen nicht funktioniert (Erreichbarkeit, Akzeptanz, Kosten)?

### 3. Protokolle & Kommunikation → `03-protokolle-kommunikation.md`
- Steuerprotokolle: IEEE 2030.5 / CSIP-AUS, OpenADR 2.0/3.0, EEBus, IEC 61850-7-420,
  SunSpec Modbus, S2 (EN 50491-12-2)
- Deutscher Weg: Smart Meter Gateway + CLS-Kanal + Steuerbox
- Österreich: Smart-Meter-Kundenschnittstelle (nur lesend?), Rundsteuertechnik
- Übertragungswege: LoRaWAN (Class C, Multicast, Duty-Cycle EU868), NB-IoT/LTE-M,
  Kundeninternet, PLC; Latenz und Verfügbarkeit
- Welche Latenz braucht Engpassmanagement im Verteilnetz wirklich?

### 4. Security & Zertifizierung → `04-security.md`
- Geräteidentität: Secure Element, PKI, Schlüsselverwaltung, Widerruf
- Pflichten: Cyber Resilience Act, NIS2, RED Delegated Act (seit 08/2025),
  NC Cybersecurity, BSI-Vorgaben (SMGW)
- Vorfälle und Studien: Schwachstellen in Wechselrichtern und Hersteller-Clouds,
  Berichte zu Kommunikationsbauteilen (2025), Massenschalt-Szenarien
- Schutzmaßnahmen: signierte Befehle mit Grenzen, lokale Plausibilisierung,
  Fail-safe, Randomisierung, Segmentgrenzen

### 5. Gerätebestand & Schnittstellen → `05-geraete-schnittstellen.md`
- Marktanteile Wechselrichter und Heimspeicher in der EU (Huawei, SMA, Fronius,
  SolarEdge, Sungrow, GoodWe, Growatt, Enphase, Kostal, BYD, Tesla u. a.)
- **Datenblätter**: welche Schnittstellen haben die Geräte tatsächlich (Modbus TCP/RTU,
  SunSpec, EEBus, Hersteller-Cloud-API, digitale Eingänge/Rundsteuerempfänger)?
- Wie lässt sich ein Gerät heute von außen steuern: lokal, über die Cloud, gar nicht?
- Reaktionszeiten und Rampen laut Datenblatt bzw. Normen (EN 50549-1, VDE-AR-N 4105)
- Vorbilder für eine **Pflichtschnittstelle**: CSIP-AUS (Australien), CA Rule 21 /
  IEEE 1547-2018, §14a-Steuerbox
- Ergebnis: Tabelle Hersteller × Schnittstelle × steuerbar (ja/nein/über Cloud) × Quelle

## Methode

- Ein Recherche-Agent pro Block, alle fünf parallel
- Jede Aussage mit Quellenlink. Primärquellen (Gesetzestexte, Normen, Datenblätter)
  vor Sekundärquellen
- Unsicheres als **[unbestätigt]** markieren, nichts aus dem Gedächtnis als Fakt
- Danach Querprüfung: ein Agent prüft die 10 wichtigsten Zahlen und Aussagen gegen ihre Quellen
- Synthese in `06-synthese.md`: Kernaussagen für Profil und Pitch, offene Fragen
  an Smart Grids Austria

## Aufwand

ca. 1–2 h Laufzeit, 6–7 Agenten (5 Blöcke + Querprüfung + Synthese).
