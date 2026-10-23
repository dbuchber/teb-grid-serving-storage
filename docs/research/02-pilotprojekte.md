# 2. Pilotprojekte & Flex-Märkte

Stand: 23.10.2026. Block 2 des Rechercheplans (`00-rechercheplan.md`).
Methode: Web-Recherche, Projektberichte/Deliverables bevorzugt. Wo nur Presse oder
Suchmaschinen-Snippets verfügbar waren, ist das vermerkt. **[unbestätigt]** = nicht
gegen eine Primärquelle geprüft. Seitenangaben beziehen sich auf die PDF-Seite.

---

## Kernaussagen

1. **Aktives Entladen von Heimspeichern fürs Verteilnetz ist erprobt, aber nur in
   wenigen Feldversuchen.** Die klarsten Belege kommen aus Australien:
   Project Symphony (WA) hat Batterien zur Spitzenlastsenkung am Netzstrang in die
   Netze entladen lassen, Project EDGE (VIC) hat Netzdienstleistungen mit „demand
   decrease“ und „demand increase“ über einen lokalen Marktplatz abgerufen. In Europa
   gab es aktive Lade-/Entladeabrufe von Heimspeichern bisher vor allem für den
   ÜNB (TenneT/sonnen, Redispatch) und für Regelenergie (Flex+, AT). Kein
   europäisches Projekt mit belastbaren Zahlen zu Heimspeicher-**Entladung** für
   einen **VNB-Engpass** gefunden.
   ([Symphony, S. 96](https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf), [EDGE Final Report, S. 154](https://arena.gov.au/assets/2023/10/AEMO-Project-EDGE-Final-Report.pdf), [pv magazine 2019](https://www.pv-magazine.de/2019/05/08/tennet-und-sonnen-sehen-grosses-potenzial-fuer-blockchain-vernetzte-photovoltaik-heimspeicher/))
2. **Die Erreichbarkeit der Geräte war in allen Projekten das größte Problem, nicht
   der Markt.** Bei Symphony wurden nur 714 von 911 rekrutierten Geräten tatsächlich
   gesteuert (der Bericht nennt auf PDF-S. 43 selbst 715, ist also inkonsistent; korr. lt. 06). 32 Wechselrichtermodelle von 7 Herstellern brauchten ein Gateway,
   Firmware-Patches, teils neue Wechselrichter und mehrere Hausbesuche. Bei Flex+ (AT)
   blieben von 10 Testanlagen 4 übrig. AEMO erhielt im VPP-Programm je Teilnehmer nur
   70–98 % der Telemetrie.
   ([Symphony, S. 59–60](https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf), [Flex+ Endbericht, S. 40](https://www.ait.ac.at/fileadmin/user_upload/20220729_Publizierbarer_Endbericht_Final.pdf), [AEMO VPP Report 4, S. 9](https://aemo.com.au/-/media/files/initiatives/der/2021/vpp-demonstrations-knowledge-sharing-report-4.pdf?la=en))
3. **Die Zuverlässigkeit von Abrufen war messbar mäßig.** Bei Symphony waren 26,6 %
   der 5-Minuten-Intervalle in 8 Netzdienst-Abrufen nicht konform. Bei EDGE wichen
   Aggregatoren in Engpasszeiten in rund 14 % von den Netz-Betriebsgrenzen (DOE) ab.
   Typische Ursachen: leere Batterie (SoC), Kommunikationsausfall, Firmware-Updates,
   die Einstellungen verstellt haben.
   ([Symphony, S. 53](https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf), [EDGE, S. 20](https://arena.gov.au/assets/2023/10/AEMO-Project-EDGE-Final-Report.pdf), [AEMO VPP Report 4, S. 5 und 31](https://aemo.com.au/-/media/files/initiatives/der/2021/vpp-demonstrations-knowledge-sharing-report-4.pdf?la=en))
4. **Unabhängige Verifikation über den Smart Meter wurde praktisch erprobt und ist
   unser stärkster Prior-Art-Beleg.** Bei EDGE hat der VNB die Erbringung bewusst mit
   eigenen Smart-Meter-Daten (5-min-PQ und 30-min-Energie) statt mit der Telemetrie
   der Aggregatoren geprüft, weil das eine unabhängige Prüfung ist. Grenze: Die
   Blindleistungs-Kennlinie (Volt-VAr) am Wechselrichter ließ sich so nicht
   eindeutig nachweisen.
   ([EDGE, S. 154 und 160](https://arena.gov.au/assets/2023/10/AEMO-Project-EDGE-Final-Report.pdf))
5. **Aus fehlender Standardschnittstelle wurde eine Pflichtforderung.** Symphony
   empfiehlt ausdrücklich, CSIP-AUS (IEEE 2030.5) für **alle neuen**
   Wechselrichter-DER in WA verpflichtend zu machen. SAPN/Tesla hat seine
   Netz-API von Anfang an auf IEEE 2030.5 ausgerichtet. Das stützt unsere Position
   zur Pflicht-Steuerschnittstelle direkt.
   ([Symphony, Empfehlung 1.1, S. 60](https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf), [SAPN Final Report, S. 3 ff.](https://arena.gov.au/assets/2021/05/advanced-vpp-grid-integration-final-report.pdf))
6. **Ein definiertes Verhalten bei Verbindungsverlust war Pflichtbestandteil.**
   SAPN testete im Advanced-VPP-Projekt mit Tesla (2019–2021) den Rückfall auf 5 kW
   Standard-Exportgrenze Ende-zu-Ende; nicht zu verwechseln mit SAPN Flexible Exports
   (2023, 1,5 kW je Phase, siehe 03/05) (korr. lt. 06). EDGE testete
   48 h ohne Netzbetriebsgrenzen (DOE) und Aggregatoren mit teilweisem bzw. vollem
   Kontaktverlust zur Flotte. Die Aggregatoren hielten den Rückfall dabei **nicht
   immer** ein. Lokale Fail-safes am Gerät sind deshalb nötig.
   ([SAPN, S. 4 und 27](https://arena.gov.au/assets/2021/05/advanced-vpp-grid-integration-final-report.pdf), [EDGE, S. 111–112](https://arena.gov.au/assets/2023/10/AEMO-Project-EDGE-Final-Report.pdf))
7. **Europäische Flex-Märkte (GOPACS, enera, NODES/sthlmflex, Piclo) sind in der
   Praxis Märkte für größere Anlagen.** Heimspeicher kommen nur über Aggregatoren
   hinein. Lokale Märkte im Verteilnetz leiden strukturell unter geringer Liquidität,
   weil nur wenige Anlagen hinter einem Engpass liegen (enera-Analyse). UKPN meldet
   zwar über 100.000 registrierte Assets (2 GW), eine Aufschlüsselung nach
   Heimspeichern fehlt aber.
   ([UDE/Jacobs-Arbeitspapier enera, S. 6–9](https://www.ewl.wiwi.uni-due.de/fileadmin/fileupload/BWL-ENERGIE/Arbeitspapiere/RePEc/pdf/wp2001_OEkonomischeUndRegulatorischeFragestellungenZumEnera-FlexMarkt.pdf), [UKPN-Meldung via Electrical Review](https://electricalreview.co.uk/2025/01/10/uk-power-networks-dso-reaches-2gw-flexibility-milestone/))
8. **Baselines verzerren die Messung bei Haushalten stark.** Im UK Demand Flexibility
   Service 2022/23 führte die Tagesanpassung der Baseline bei 77 % der
   Kunden-Ereignisse zu einer abgesenkten Baseline. Nur 52 % der Teilnehmenden
   zeigten messbar eine Reduktion. Für Geräte mit direkter Steuerung ist ein
   **Soll-Ist-Vergleich gegen den Befehl** sauberer als eine statistische Baseline.
   ([DFS Smart Meter Evaluation, S. 3–5](https://www.neso.energy/document/371411/download))

---

## Übersichtstabelle

| Projekt | Land | Zeitraum | Geräte / Größe | Kanal / Protokoll | Vergütung | Ergebnis (Zahl) |
|---|---|---|---|---|---|---|
| **Project Symphony** | AU (WA) | 2022–2024 (Pilot ca. 2 J.) | 514 Kunden, 911 DER (PV, 150 Batterien, Klima, Warmwasser); 714 tatsächlich gesteuert | Aggregator-Cloud → Gateway vor Ort → Wechselrichter; Empfehlung CSIP-AUS/IEEE 2030.5 | ~50 % Zuschuss zur Batterie oder ~150 AUD je Gerät; Netzdienst-Vertrag (fest: Verfügbarkeit + Pönale; flexibel: nur Abruf) | 26,6 % nicht konforme Intervalle (8 Abrufe); 32 WR-Modelle / 7 Hersteller |
| **Project EDGE** | AU (VIC) | Feldtest 333 Tage, 2022–2023 | >320 Haushalte/Gewerbe, >400 DER, >3,5 MW | Aggregator ↔ VNB (AusNet) ↔ AEMO über Data Hub; DOE im CSIP-AUS-Schema | Netzdienst über Local Services Exchange; Zahlung für Verfügbarkeit + Teilnahme, Rückforderung bei Nichterbringung | DOE-Abweichung ~14 % in Engpasszeiten; Telemetrie 90–95 % vollständig (1-min); Nachweis per Smart Meter |
| **SAPN Advanced VPP Grid Integration** | AU (SA) | 2019–2021 (18 Mon. Feldtest) | 1.000 Haushalte, Tesla Powerwall 2 (5 MW) | SAPN-API (auf IEEE 2030.5 hin entwickelt) → Tesla-Cloud → Powerwall-Firmware | keine eigene Netzvergütung; Nutzen über höhere Exportgrenze, Gewinne gleich verteilt | Exportkapazität 5 MW → 6–8 MW in Solarstunden; Fail-safe 5 kW getestet |
| **SA VPP (Energy Locals/Tesla) im AEMO-VPP-Programm** | AU (SA) | ab 2019 | AEMO-Programm gesamt ~7.150 Kunden, 31 MW (davon 27 MW in SA) | Hersteller-Cloud, WLAN/3G/4G | FCAS-Erlöse (Frequenzhaltung) | Telemetrie 70–98 %; Unterlieferung wegen Firmware-Einstellungen; bis 10 % Überbuchung als Puffer |
| **enera Flexmarkt** | DE | 2017–2020 (SINTEG) | Erzeuger, Speicher, P2X, Industrie; >360 MW eingebunden [unbestätigt] | EPEX-SPOT-Orderbuch mit lokalen Marktgebieten; Baseline an Nachweisplattform | pay-as-bid | 24 MW größter Abruf innerhalb 1 h (04/2020); 9 Teilnehmer, 23 Marktgebiete (Ende 2019) |
| **TenneT / sonnen** | DE | 2017–2019 | vernetzte sonnen-Heimspeicher (Anzahl nicht genannt) | sonnen-Cloud; Messwerte in IBM-Hyperledger-Blockchain, jede kWh signiert | nicht veröffentlicht | Redispatch durch gleichzeitiges Laden (Überschussregion) und Entladen (Mangelregion) technisch gezeigt; keine Zahlen |
| **GOPACS** | NL | seit 2019 | v. a. Großkunden; Wärmepumpen, E-Boiler, Kühlhäuser, Batterien, Kraftwerke | Gebote über angebundene Handelsplattformen (IDCONS), Congestion Service Provider (CSP) | marktbasiert (Spread) + Kapazitätsverträge (CSC/CBC) | 288.571 MWh (2021), 363.917 MWh (2022), 228.461 MWh (2023) |
| **Piclo Flex / UKPN** | UK | seit 2019 | alle Größen; 2020 vor allem Speicher (80,1 von 123 MW) | Piclo-Plattform; UKPN-Day-Ahead über Localflex (EPEX) | Verfügbarkeit + Abruf je Zone | UKPN: >100.000 Assets / 2 GW registriert; 7,8 GWh abgerufen 2023/24 |
| **UK Demand Flexibility Service** (ÜNB, nicht VNB) | UK | Winter 2022/23 | >1,6 Mio. Haushalte/Betriebe, 31 Anbieter | Lieferant/Aggregator → Kunde (App/E-Mail); Nachweis über Smart Meter | 3.000 £/MWh (Test), Ø 4.559 £/MWh (live) | ~3.300 MWh, 22 Events, 11,1 Mio. £; 52 % reduzierten messbar |
| **Flex+** | AT | 2018–2022 | Batteriepool: 10 geplant, 4 im Betrieb (Fronius) | Cloud → MQTT → Raspberry Pi → Wechselrichter (mangels nativer Fernsteuerung) | Regelenergie (SRL), Day-Ahead/Intraday | SRL-Abruf 6,0 kW gefordert, 4,73 kW geliefert; Datenlücken |
| **LEAFS** | AT | 2015–2018 | Heimspeicher in Köstendorf und Eberstalzell, Zentralspeicher in Heimschuh | Building Energy Agent mit VNB-Signal (Köstendorf); App-Bonus (Eberstalzell) | Tarif-/Bonusmodelle | Wirtschaftlichkeit 2019: Heimspeicher je nach Strategie 1,9× zu teuer bis knapp wirtschaftlich |
| **InterFlex** | EU (FR, DE, NL, CZ, SE) | 2017–2020 | DSM, Speicher, E-Mobilität | je Demo unterschiedlich | je Demo | Rebound 25–50 % der abgeregelten Leistung (Enedis-Folie) |
| **sthlmflex (NODES)** | SE | seit 2019/20 | v. a. größere Lasten (z. B. 10 MW Wärmepumpen Stockholm Exergi) | NODES-Marktplattform | Abruf- und Verfügbarkeitsprodukte (Woche/Saison) | Mindestgebot 0,5 MW (vorläufig) |
| **IntraFlex** | UK | 10/2019–11/2021 | DNO-Flexibilität kurzfristig | NODES Day-Ahead/Intraday, automatisches Rebalancing | Abruf | >50 MW in zwei Monaten beschafft [unbestätigt] |

---

## Detailabschnitte

### Project Symphony (Western Australia), Western Power / Synergy / AEMO

- **Akteure:** Western Power als VNB („DSO“), Synergy als Aggregator, AEMO als
  „Distributed Market Operator“. Pilotgebiet Southern River (Perth), dort haben über
  50 % der Haushalte PV.
  ([ARENA Knowledge Bank](https://arena.gov.au/knowledge-bank/western-power-project-symphony-pilot-results-and-recommendations), [Final Report](https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf))
- **Geräte:** 514 Kunden und 911 DER-Geräte (PV, Batterien, Klimaanlagen,
  Warmwasser). Dazu 218 Klimaanlagen, davon 119 steuerbar (Ziel 280), und 150
  neu angeschaffte Heimbatterien. Netzdienst laut Bericht ausdrücklich auch durch
  „discharging of battery energy storage into the network at peak time“.
  (Final Report, S. 96)
- **Kommunikation:** Aggregator-Plattform → **eigenes Gateway je Haushalt** →
  Wechselrichter. Teils waren Firmware-Patches oder neue Wechselrichter nötig, teils
  mehrere Hausbesuche (S. 60).
- **Vergütung:** Im Pilot gab es ~50 % Zuschuss zur Batterie oder ~150 AUD je
  Gerät, dazu eine Vorab-Zahlung für die Steuerung. Der Bericht sagt selbst, dass
  das nicht dem realen Wert der Leistung entspricht (S. 99). Für den Netzdienst gibt
  es zwei Formen: **fest** mit Verfügbarkeitszahlung und Pönalen als Alternative
  zum Netzausbau, **flexibel** mit reiner Abrufzahlung ohne Pönale (S. 51).
- **Ergebnisse:**
  - 714 von 911 Geräten wurden tatsächlich gesteuert. Grund für die Lücke:
    unzuverlässige Kommunikation und mangelnde Interoperabilität (S. 59). Auf PDF-S. 43
    nennt der Bericht „assets orchestrated (715)“; die Inkonsistenz steckt in der Quelle
    (korr. lt. 06).
  - 26,6 % der 5-Minuten-Intervalle waren bei 8 Netzdienst-Abrufen nicht konform
    (Schwelle: ≥ 95 % des Sollwerts) (S. 53).
  - Nur 35 % der Bewerber hatten Klimaanlagen, die den Demand-Response-Standard
    AS4755 erfüllen (S. 115).
- **Lessons learned:** Der Ladezustand (SoC) ist kritisch, denn mit leerer Batterie
  gibt es keinen Netzdienst. Andere Tests hatten Batterien vor einem Abruf entleert
  (S. 52–53). Einige Interessierte wurden ausgeschlossen, weil sie im falschen
  Netzgebiet lagen oder zu wenig Wert erwarten ließen. Das führte zu Frust (S. 108). **Empfehlung 1.1:** CSIP-AUS/AS5385 für alle neuen
  Wechselrichter-DER verpflichtend, PKI-gesicherte Registrierung (S. 60–61).
  **Empfehlung 4.5:** AS4755 bei Herstellern durchsetzen.

### Project EDGE (Victoria), AEMO / AusNet / Mondo / Aggregatoren

- **Akteure:** AEMO, VNB AusNet Services. Aktiv im Feld: Discover Energy (Versorger)
  sowie Rheem und Combined Energy Technologies (Aggregatoren hinter dem Zähler).
  ([AEMO Projektseite](https://aemo.com.au/initiatives/major-programs/nem-distributed-energy-resources-der-program/der-demonstrations/project-edge))
- **Geräte:** Feldtest rund um die Uhr über 333 Tage mit über 320 Wohn- und
  Gewerbeteilnehmern, über 3,5 MW flexibler Leistung und über 400 DER (PV,
  Batterien, gesteuertes Warmwasser, andere Lasten)
  ([Final Report, S. 36](https://arena.gov.au/assets/2023/10/AEMO-Project-EDGE-Final-Report.pdf)).
- **Kommunikation:** Datenaustausch über einen zentralen „DER Data Hub“ statt
  Punkt-zu-Punkt-Verbindungen. Die Netzbetriebsgrenzen (DOE) folgen dem
  CSIP-AUS-Datenschema. Dabei fiel eine Inkompatibilität auf: Import- und
  Exportgrenzen mussten positiv sein (Final Report, S. 116, Abb. 82).
- **Netzdienste (Local Services Exchange, LSE):** Es gab Dienste mit hoher und
  niedriger Verbindlichkeit („Firmness“) für Leistungsanhebung und
  -absenkung sowie Spannungsstützung über Volt-VAr-Kennlinien. Bei hoher
  Verbindlichkeit kam 24 h vorher ein „Arming Signal“. Danach lieferte der
  Aggregator eine Rückmeldung (ACK/NAK) mit Kapazitätsprüfung und
  Baseline-Qualität (S. 153). Zur Vorbereitung einer Leistungsanhebung entleerten
  Aggregatoren die Batterien vorher. Das fiel Kunden auf, sie mussten informiert
  werden (S. 154).
- **Vergütung:** Bezahlt wurden Verfügbarkeit und Teilnahme, nicht die gelieferten
  kW. Bei Nichterbringung griff eine Rückforderungsklausel (S. 154, Fn. 320).
- **Verifikation:** Der VNB nutzte **Smart-Meter-Daten** (5-min-PQ und
  30-min-Energie) „because it provided an independent verification“ (S. 154). Für
  die Volt-VAr-Spannungsstützung reichte das nicht. Dafür wäre Telemetrie vom
  Wechselrichter oder ein DER-Register nötig (S. 159–160).
- **Ergebnisse (Zahlen):**
  - ~14 % Abweichung von den DOE in Engpasszeiten (S. 20).
  - Telemetrie bei 1-min-Takt zu 90–95 % vollständig, bei manchen Architekturen
    98–100 %. 5-s-Takt technisch machbar (S. 20).
  - 90-%-Compliance-Metrik: Schon ein einzelner Messwert außerhalb galt als
    Fehlschlag. Aggregatoren mussten deshalb einen Puffer überliefern (S. 160).
  - CBA (Deloitte): Data Hub 9 Mio. AUD günstiger als Punkt-zu-Punkt.
    Zusatznutzen der LSE über 20 Jahre 0,08–0,51 Mrd. AUD, nur aus vermiedener
    Exportabregelung gerechnet
    ([CBA Executive Summary, PDF-S. 19–20](https://arena.gov.au/assets/2024/01/AEMO-Project-Edge-Executive-Summary-Revised.pdf)).
- **Kommunikationsausfall-Tests:** Getestet wurden (1) Aggregator ohne Kontakt zu
  Teilen der bzw. zur ganzen Flotte, (2) Aggregator ohne Verbindung zu AEMO und (3)
  48 h ohne DOE. In allen drei Fällen hielten Aggregatoren die Rückfallregeln
  „nicht immer“ ein. Zwischen Marktaustritt und passivem Geräteverhalten gab es eine
  Verzögerung. Empfehlung: zusätzliche Fail-safe-Geräte, die einen Cloud-Ausfall
  erkennen und auf Standard-DOE zurückfallen (S. 111–112). In ländlichen Gebieten
  ist die Kommunikation weniger zuverlässig. Aggregatoren könnten Kunden deshalb
  nach Verbindungsqualität vorqualifizieren (S. 161).

### SA Power Networks: Advanced VPP Grid Integration (South Australia)

- **Akteure / Geräte:** SAPN (VNB) und Tesla mit 1.000 Haushalten der Phase 2 des
  SA VPP, Powerwall 2 mit insgesamt 5 MW
  ([Final Report, S. 3](https://arena.gov.au/assets/2021/05/advanced-vpp-grid-integration-final-report.pdf)).
- **Kommunikation:** Gemeinsam entwickelte Web-API. In der Konsultation wurde
  IEEE 2030.5 als geeignetster Standard identifiziert. Die API mündete in die
  australische IEEE-2030.5-Implementierung (CSIP-AUS). Tesla änderte die globale
  Powerwall-Firmware, um statt der statischen 5-kW-Grenze dynamische Grenzen
  zuzulassen (S. 3 und Kap. 2.2).
- **Ergebnis:** Exportkapazität des VPP in Solarstunden von 5 MW auf 6–8 MW
  gesteigert, ohne die Versorgungsqualität zu verletzen. Netzbetreiber konnten
  Grenzen bei Wartung und Störungen manuell übersteuern (S. 3–4).
- **Fail-safe:** Ende-zu-Ende-Tests für den Rückfall auf 5 kW Standardgrenze bei
  Kommunikationsverlust. Neue Anlagen starten mit 5-kW-Grenze (S. 27).
- **Relevanz für uns:** Das ist kein aktives Entladen auf Netzbefehl, sondern eine
  Betriebshüllkurve. Es ist aber der beste Beleg für eine VNB-Schnittstelle, die
  über eine Hersteller-Cloud bis zu 1.000 Heimspeichern sicher funktioniert.

### SA VPP (Tesla/Energy Locals) und AEMO VPP Demonstrations

- **Umfang:** AEMO-Programm ab 2019 mit 8 VPP-Portfolios, ~7.150 Kunden und
  31 MW, davon 27 MW in Südaustralien
  ([Knowledge Sharing Report 4, S. 4 und 8](https://aemo.com.au/-/media/files/initiatives/der/2021/vpp-demonstrations-knowledge-sharing-report-4.pdf?la=en)).
- **Unterlieferung:** Beim Netztrennungsereignis am 16.11.2019 hatten weniger
  Systeme als erwartet die Frequenzstützung aktiv. Ursache war ein
  Firmware-Update. Abhilfe: **tägliche Prüfung aller Systeme auf korrekte
  Konfiguration** (Report 4, Tab. 3, S. 31). Laut Sekundärquelle standen statt
  1 MW nur 828 kW zur Verfügung **[unbestätigt, Report 1 nicht selbst geprüft]**
  ([SolarQuotes](https://solarquotes.com.au/blog/aemo-report-vpp)).
- **Puffer:** VPPs hielten bis zu 10 % zusätzliche Flottenleistung vor (S. 5).
- **Telemetrie:** AEMO erhielt je Teilnehmer 70–98 % der Daten. Ursache waren
  Ausfälle zwischen Haus und VPP-Cloud über WLAN/3G (S. 9).
- **Messvorgaben (Prequalifikation):** Alle 8 Portfolios wählten 1-s-Messwerte je
  Zählpunkt plus einen Hochgeschwindigkeitszähler (≤ 50 ms) je Region. Verweis auf
  UK FFR und NL FCR mit 100-ms-Daten im Prequalifikationstest und 1–4-s-Daten im
  laufenden Betrieb (S. 24).
- **SAPN-Spannungsstützung parallel zu FCAS:** Im SA VPP lief Spannungsstützung
  parallel zu FCAS. Bei Vorrang für das Netz sank die FCAS-Kapazität (S. 7).

### enera Flexmarkt (Deutschland, SINTEG)

- **Akteure:** EWE NETZ, Avacon Netz, TenneT als alleinige Nachfrager und EPEX
  SPOT als Börse. Das Konsortium hatte 33 Partner
  ([EPEX-Meldung erster Handel](https://epexspot.com/en/news/first-trade-flexibility-platform-enera-completed-successfully)).
- **Marktdesign:** Lokale Orderbücher je „Marktgebiet“ (engpassfreie Netzregion
  mit gleicher Sensitivität). Flexibilität ist definiert als Abweichung von einer
  gemeldeten Baseline. Baseline und Ist-Fahrplan gehen laufend an eine
  Nachweisplattform. Vergütung pay-as-bid, der Anbieter gleicht seinen Bilanzkreis
  selbst aus
  ([UDE/Jacobs, S. 4–5](https://www.ewl.wiwi.uni-due.de/fileadmin/fileupload/BWL-ENERGIE/Arbeitspapiere/RePEc/pdf/wp2001_OEkonomischeUndRegulatorischeFragestellungenZumEnera-FlexMarkt.pdf)).
- **Zahlen:** Ende 2019 waren 9 Marktteilnehmer in 23 Marktgebieten aktiv
  ([EPEX Jahresmeldung 2019](https://www.epexspot.com/sites/default/files/download_center_files/200113_EPEX%20SPOT_2019_Annual%20Press%20Release_.pdf)).
  Größter koordinierter Abruf: 24 MW innerhalb einer Stunde (April 2020)
  ([EPEX/EWE Pressemitteilung](https://www.epexspot.com/sites/default/files/download_center_files/200415_EPEX_EWE_ENERA_Pressemitteilung_DE.pdf), Inhalt per Suchsnippet). Über 360 MW Anlagen
  eingebunden **[unbestätigt, Zeitpunkt unklar]**
  ([ZfK](https://www.zfk.de/energie/strom/360-mw-in-enera-flexmarkt-eingebunden)).
- **Lessons learned:** Engpässe im **Verteilnetz** haben kleine Engpassregionen. Nur
  wenige Anlagen haben dort Wirkung, deshalb ist die Liquidität gering und
  Marktmacht sowie strategisches Bieten (Inc-Dec-Gaming) werden zum Risiko
  (UDE/Jacobs, Kap. 2 und 3). Heimspeicher-Beteiligung ist nicht dokumentiert.

### TenneT / sonnen: Redispatch mit Heimspeichern (Deutschland, ÜNB)

- 2017–2019: Vernetzte sonnen-Heimspeicher luden in Regionen mit
  Windstromüberschuss und entluden zeitgleich in Mangelregionen. sonnen meldete
  TenneT laufend die verfügbare Redispatch-Kapazität. Jede kWh wurde in einer
  IBM-Hyperledger-Blockchain dokumentiert und **kryptografisch signiert**
  ([pv magazine, 08.05.2019](https://www.pv-magazine.de/2019/05/08/tennet-und-sonnen-sehen-grosses-potenzial-fuer-blockchain-vernetzte-photovoltaik-heimspeicher/), [Solarserver](https://www.solarserver.de/2019/05/08/hausspeicher-stabilisieren-das-stromnetz/)).
- Ergebnis laut Partnern: „technischer Nachweis“. Anzahl der Speicher, Mengen und
  Vergütung wurden nicht veröffentlicht. TenneT forderte einen weiterentwickelten
  Regulierungsrahmen und Anreize.
- **Relevanz:** Das ist der klarste europäische Fall von **bidirektionalem**
  Heimspeicher-Abruf für einen Netzengpass, allerdings im Übertragungsnetz und über
  eine einzelne Hersteller-Cloud. Signierte Messwerte sind Prior Art für unsere
  Verifikationsidee.

### GOPACS (Niederlande)

- **Akteure:** Plattform aller niederländischen Netzbetreiber (Coteq, Enexis,
  Liander, Rendo, Stedin, TenneT, Westland Infra), betrieben von GOPACS B.V.
  ([gopacs.eu](https://www.gopacs.eu/)).
- **Ablauf:** Der Netzbetreiber meldet einen Engpass mit Zeitraum, Leistung und
  Gebiet. Marktteilnehmer bieten über angebundene Handelsplattformen mit
  Leistung, Richtung, EAN-Gebiet und Preis. Zur Wahrung der Systembilanz wird ein
  Gegengebot außerhalb des Engpassgebiets kombiniert (Spread)
  ([ETPA Knowledge Hub](https://www.etpa.nl/knowledge-hub/gopacs)). Seit Februar 2025
  werden die Orderbücher mehrerer Plattformen virtuell zusammengeführt
  ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i39815/gopacs-bundelt-per-direct-flexbiedingen-van-meerdere-handelsplatformen)).
- **Produkte heute:** Neben dem Redispatch-Markt Kapazitätssteuerungsverträge
  (CSC-A/CSC-T), Begrenzungsverträge (CBC), zeitabhängige Transportrechte (TDTR)
  und Bietpflichtverträge. Ab 01.11.2026 sind „Cross Operator“-Abrufe möglich
  ([gopacs.eu](https://www.gopacs.eu/)).
- **Volumen:** 288.571 MWh (2021), 363.917 MWh (2022), 228.461 MWh (2023) (ETPA).
- **Kleinanlagen:** GOPACS richtet sich an Großkunden und Congestion Service
  Provider (CSP). Für Heimspeicher gibt es in NL erst Arbeitsgruppen und Piloten.
  Netzbetreiber sehen Heimspeicher „überwiegend positiv“ für die Netzauslastung,
  erwarten aber in bis zu 5 % der Zeit höhere Spitzen im Niederspannungsnetz.
  Ein „Sprintteam“ für netzdienliche Steuerung wurde eingerichtet, Alliander
  testet Heimspeicher-Piloten
  ([Solar Magazine, 18.11.2024](https://solarmagazine.nl/nieuws-zonne-energie/i39053/thuisbatterij-heeft-merendeel-van-de-tijd-positief-effect-op-netcongestie)).
  Verwandter Pilot „netbewust thuisladen“ (Liander/Enexis, E-Autos): 330 Kunden,
  bis zu 68 % weniger Leistung in der Abendspitze. Netzbetreiber bevorzugen
  zunächst **statische** Profile
  ([Liander-Bericht 04/2025](https://www.liander.nl/-/media/files/nieuws/250408---rapport-pilot-netbewust-thuisladen.pdf)).

### Piclo Flex / UK-Verteilnetzbetreiber (UKPN u. a.)

- **Plattform:** Piclo meldete im August 2024 über 300.000 registrierte Assets
  (über 22 GW), 74 Mio. £ vergebene Verträge und über 2,6 GW beschafft. Kunden
  sind u. a. UKPN, SP Energy Networks, ENWL, E-REDES (PT) und ESO (LT)
  ([Piclo-Pressemitteilung](https://www.piclo.energy/press-releases/edp-invests-in-piclo-to-unlock-new-opportunities-in-flexibility-markets)).
- **UKPN-Ausschreibung 2020:** 14 Mio. £ insgesamt, davon 11,4 Mio. £ für
  Speicher (80,1 von 123 MW)
  ([Current News](https://current-news.co.uk/storage-dominates-in-ukpns-most-recent-flexibility-procurement-piclo-says)).
- **UKPN heute:** Über 100.000 Assets mit 2 GW auf Localflex (Betrieb EPEX SPOT),
  von Wallboxen bis zu Energiemanagementsystemen in Haushalten. 7,8 GWh abgerufen
  2023/24, 91 Mio. £ Nutzen für Verbraucher laut UKPN
  ([Electrical Review, 10.01.2025](https://electricalreview.co.uk/2025/01/10/uk-power-networks-dso-reaches-2gw-flexibility-milestone/)).
  Day-Ahead-Markt seit Frühjahr 2024: 4,4 GWh im ersten Jahr, über 40 Zonen
  ([pv magazine, 23.04.2025](https://www.pv-magazine.com/2025/04/23/ai-helps-uk-dso-deliver-4-4-gwh-of-day-ahead-flexibility-in-one-year/)).
  Später meldete UKPN 11 GWh **[unbestätigt, Originalseite 403]**.
- **Heimspeicher-Entladung:** UKPN kontrahierte das VPP von Social Energy
  (Heimbatterien mit PV), das per Entladung Flexibilität liefert (2,1 MW über zwei
  Anbieter, bis 2023/24) **[unbestätigt, nur Suchsnippet]**
  ([Current News](https://current-news.co.uk/ukpn-to-use-virtual-power-plant-for-flexibility-services)).
- **Lücke:** Wie viel davon auf Heimspeicher entfällt und wie zuverlässig sie
  geliefert haben, wird nirgends öffentlich aufgeschlüsselt.

### UK Demand Flexibility Service 2022/23 (ÜNB-Dienst, aber relevant für Messmethodik)

- Über 1,6 Mio. Haushalte und Betriebe bei 31 Anbietern, 22 Events (20 Tests,
  2 Live-Events). Rund 3.300 MWh Reduktion, Live-Events 20 % höher als Tests.
  3.000 £/MWh (Test) bzw. Ø 4.559 £/MWh (live), insgesamt 11,1 Mio. £
  ([NESO Winter Review, S. 3–4 und 9](https://neso.energy/document/287006/download)).
- Baseline nach BSC P376 mit Tagesanpassung. Smart-Meter-Auswertung von ~139.000
  Haushalten: 52 % reduzierten gegenüber der Baseline, im Schnitt 0,39 kWh je
  aktivem Teilnehmer und Event. 77 % der Kunden-Ereignisse hatten eine
  abgesenkte Baseline, weil Kunden schon vor dem Event sparten. Die Tagesanpassung
  wurde danach abgeschafft
  ([DFS Smart Meter Evaluation, S. 3–5](https://www.neso.energy/document/371411/download)).
- **Testabrufe:** Die 20 Testevents dienten ausdrücklich der
  Bereitschaftsprüfung. Sie sind ein Beispiel für regelmäßige Testabrufe im
  Massenmarkt, allerdings mit Verhaltensänderung statt Gerätesteuerung.

### Österreich: Flex+ und LEAFS (Klima- und Energiefonds)

**Flex+** (AIT u. a. mit Fronius, iDM, Austria Email, neoom; 05/2018–04/2022)
([Publizierbarer Endbericht](https://www.ait.ac.at/fileadmin/user_upload/20220729_Publizierbarer_Endbericht_Final.pdf)):
- Batteriepool nur aus Anlagen von Fronius-Mitarbeitenden. Von 10 Anlagen waren
  anfangs 5, dann **nur 4** in den Demowochen nutzbar. Gründe: alternative
  Komponenten, Smart-Home-Lasten unter Drittanbieter-Steuerung, ein
  Batteriedefekt (S. 40).
- Die Fronius-Wechselrichter hatten **noch keine native Fernsteuerung**. Deshalb
  wurde je Haushalt ein Raspberry Pi installiert, angebunden per MQTT an die Cloud
  und mit 2-s-Messwerten als Nachweis gegenüber APG (S. 41).
- Probleme: Offline-Geräte wurden aus der Optimierung ausgenommen. Batterien
  reagierten wegen gerätinterner Vorrangfunktionen (Mindest-SoC,
  Kalibrierladung) teils nicht. Aktivierungen wurden gesendet, aber nicht
  umgesetzt, und Daten fehlten (S. 43–45). Bei einem SRL-Abruf waren 6,0 kW
  gefordert und 4,73 kW wurden geliefert. Ursache war eine fiktive
  Leistungsbegrenzung im Algorithmus (S. 46–47).
- APG-Prequalifikation verlangt u. a. Angaben zu Protokollen, Verfügbarkeit,
  Verzögerungen, Messgenauigkeit und eine gemeinsame Funktionskontrolle. Ein Pool
  mit gleichartigen Geräten bekommt ein vereinfachtes Verfahren, und ein
  Netzbetreibervertrag ist nötig (S. 114–115).
- Kundenbefragung: 4 Fokusgruppen, Online-Umfrage mit n = 850 (S. 93).

**LEAFS** (AIT, Fronius, Siemens, Salzburg Netz, Netz OÖ, Energienetze
Steiermark u. a.; 11/2015–10/2018)
([AIT Projektseite](https://www.ait.ac.at/en/leafs)):
- Feldtests: Köstendorf (Heimspeicher, Building Energy Agent mit
  Netzbetreibersignal), Eberstalzell (App-„Sonnenbonus“ für Verbrauch bei hoher
  lokaler PV-Erzeugung) und Heimschuh (zentraler Speicher)
  ([Solarserver 2018](https://www.solarserver.de/2018/05/08/probelauf-fuer-die-flexible-energiezukunft/)).
- Wirtschaftlichkeit (Kosten 2019): Ein 4,8-kWh-Heimspeicher ist bei maximalem
  Eigenverbrauch noch 1,9-mal zu teuer. In der Strategie „minimaler Leistungsbezug“
  mit 40 €/kW/a Leistungspreis wird er knapp wirtschaftlich (ca. +80 €/a)
  ([Prüggler, IEWT 2019](https://iewt2019.eeg.tuwien.ac.at/download/contribution/presentation/112/112_presentation_20190215_102253.pdf)).
- Gemessene Feldergebnisse (Anzahl Speicher, Reaktionsquoten) **nicht gefunden**.
  Der publizierbare Endbericht war über den Download-Link nicht abrufbar.

**Kontext AT:** 2024 gab es rund 2,2 GWh nutzbare Heimspeicherkapazität. Die
AIT-Prognose für 2040 liegt bei ~1,28 Mio. Heimspeichern mit 17,3 GWh
([Hasanagic et al., EnInnov 2026, S. 1–2](https://www.tugraz.at/fileadmin/user_upload/Events/Eninnov/EnInnov2026/files/lf/544_LF_Hasanagic.pdf)).
Ein österreichisches VNB-Pilotprojekt mit aktivem Heimspeicher-**Entladen** und
veröffentlichten Ergebnissen wurde **nicht gefunden**. Das ältere Projekt
hybrid-VPP4DSO (2014–2017) beschrieb ein Ampelkonzept mit VNB-Vorrang
([TU Graz EnInnov 2016](https://www.tugraz.at/fileadmin/user_upload/Events/Eninnov2016/files/kf/Session_E1/KF_Spreitzhofer.pdf)).

### EU-Horizon-Projekte: InterFlex, EUniversal, OneNet

- **InterFlex** (2017–02/2020, ca. 23 Mio. €, Koordination Enedis, VNB Avacon, ČEZ,
  Enedis, Enexis, E.ON). Die Eindhoven-Demo integrierte lokale Batteriespeicher
  ([Sympower](https://sympower.net/sympower-officially-kicks-off-the-european-smart-grid-project-interflex/), [ČEZ](https://www.cez.cz/nextcez/cs/pro-media/tiskove-zpravy/cez-distribuce-uspesne-dokoncila-smart-grid-projekt-interflex-81467)).
  Eine Enedis-Folie meldet für die französischen Demos 25–50 % Rebound der
  abgeregelten Leistung und 95 % Nachholen der Energie. Für Entlastung im
  Niederspannungsnetz waren viele Teilnehmende nötig, und der Wert für den VNB ist
  lokal und zeitlich begrenzt
  ([Enedis/EPRG, S. 8](https://www.jbs.cam.ac.uk/wp-content/uploads/2024/01/eprg-A.-Phelizon_Enedis-Smart-Grids-MIT-Sorbonne.pdf);
  ob alle Punkte genau InterFlex zuzuordnen sind: **[unbestätigt]**).
- **EUniversal** (bis 11/2023, ~10 Mio. €). Ergebnis ist die quelloffene
  Schnittstelle UMEI zwischen VNB und Flex-Märkten. In der deutschen Demo (Mitnetz)
  war die Beobachtbarkeit im Niederspannungsnetz „quite low“
  ([E.DSO](https://www.edsoforsmartgrids.eu/euniversal), [arXiv 2311.12227](https://arxiv.org/pdf/2311.12227)).
  Haushaltsergebnisse nicht gefunden.
- **OneNet** (2020–2023). Ein Deliverable bewertet Baseline-Methoden und
  Prequalifikation aus den Demos
  ([EUI Cadmus](https://cadmus.eui.eu/handle/1814/76110)). Inhalte wurden
  nicht geprüft **[unbestätigt]**.

### NODES / sthlmflex / NorFlex / IntraFlex

- **sthlmflex:** Svenska kraftnät mit Vattenfall Eldistribution und Ellevio, NODES
  als Marktbetreiber. Produkte sind Abrufe, Wochen- und Saisonverfügbarkeit.
  Vorläufig galten 0,5 MW Mindestgebot, 0,1 MW Schrittweite und eine
  durchschnittliche Lieferzeit von 60 min
  ([HPT Case Study](https://heatpumpingtechnologies.org/project57/case-studies/sthlmflex-creating-and-testing-a-flexibility-market-in-stockholm/), Werte per Suchsnippet aus
  [Svk-Infomaterial](https://www.svk.se/siteassets/2.utveckling-av-kraftsystemet/forskning-och-utveckling/sthlmflex/sthlmflex-information-20200828-status.pdf) **[unbestätigt]**).
- **NorFlex** (2019–2023, Leitung Agder Energi, mit Statnett, Glitre, Mørenett):
  lokale Flexibilität einschließlich Batterien, Wallboxen und Haushaltsgeräten,
  Überschuss für mFRR. Endbericht mit Zahlen nicht gefunden
  ([Statnett](https://www.statnett.no/en/about-statnett/research-and-development/our-prioritised-projects/norflex/), [Nordic Energy Research 2025](https://pub.norden.org/nordicenergyresearch2025-03/in-depth-case-studies-of-flexibility-initiatives.html)).
- **IntraFlex** (WPD, 10/2019–11/2021, 1,281 Mio. £): kurzfristige DNO-Flexibilität
  über NODES Day-Ahead/Intraday mit automatischem Bilanzausgleich für Lieferanten
  ([WPD-Projektseite](https://www.westernpower.co.uk/projects/intraflex) per Suchsnippet,
  [The Energyst](https://theenergyst.com/wpd-and-nord-pool-combine-on-broader-flexibility-market-trial/)).
  Abschlussbericht nicht gefunden.

---

## Projekte mit Testabrufen / Prequalifikation / Messung je Gerät

| Projekt | Was wurde gemessen? | Granularität |
|---|---|---|
| AEMO VPP Demonstrations | 1-s-Daten je Zählpunkt plus 50-ms-Referenzzähler je Region; tägliche Konfigurationschecks nach Firmware-Problemen | je Zählpunkt (Haushalt) |
| Project EDGE | Smart-Meter-Daten des VNB (5-min-PQ, 30-min-Energie); ACK/NAK mit Kapazitätsprüfung; Tests für Kommunikationsausfall | Portfolio, für Volt-VAr je Zählpunkt |
| Project Symphony | Anteil der 5-min-Intervalle ≥ 95 % des Sollwerts | Portfolio am Netzstrang/Trafo |
| SAPN Advanced VPP (Tesla, 2019–2021) (korr. lt. 06) | Ende-zu-Ende-Fail-safe-Test auf 5 kW bei Inbetriebnahme | je Gerät |
| UK DFS | 20 Testevents zur Bereitschaftsprüfung; Baseline P376 | je Zählpunkt (MPAN) |
| Flex+ / APG | Prequalifikation mit Funktionskontrolle, 2-s-Messwerte | Pool, vereinfacht bei gleichartigen Geräten |

**Befund:** Kein gefundenes Projekt bildet systematisch eine **Reaktionszeit- und
Zuverlässigkeitsstatistik je Gerätetyp oder Firmware** aus wiederkehrenden
Testabrufen. Am nächsten kommen AEMO (tägliche Checks) und EDGE/Symphony
(Konformität je Abruf). Diese Lücke kann unser Profil füllen.

---

## Lessons learned für unser Profil

1. **Pflicht-Schnittstelle ist durch Praxisprobleme belegt.** Symphony (Gateway,
   Firmware-Patches, ausgetauschte Wechselrichter, Hausbesuche) und Flex+
   (Raspberry Pi statt nativer Steuerung) zeigen, was der Status quo kostet.
   Symphony fordert selbst die Pflicht (CSIP-AUS). → Im Profil: herstellerunabhängige
   Steuer- und Rückmeldefunktion als Pflicht für Neugeräte, keine Nachrüstpflicht.
2. **Verifikation unabhängig vom Aggregator.** EDGE zeigt, dass der VNB-eigene Smart
   Meter Wirkleistungsdienste prüfen kann. → Im Profil: Smart Meter als
   unabhängige Instanz für die Wirkleistung. Blindleistung braucht zusätzlich
   Daten vom Wechselrichter.
3. **Testabrufe gegen Konfigurationsdrift.** Firmware-Updates haben Einstellungen
   still verändert (SA VPP). → Regelmäßige, randomisierte Testabrufe je Gerät
   und Gerätetyp sowie ein Abgleich der Konfiguration nach jedem Firmware-Update.
4. **SoC-Management ist Teil der Dienstdefinition.** Leere Batterien konnten nicht
   liefern (Symphony), Batterien wurden zur Vorbereitung entleert (EDGE). →
   Ankündigung mit Vorlauf („Arming“, bei EDGE 24 h), SoC-Reserve als
   Vertragsparameter, Rückmeldung der verfügbaren Energie vor dem Abruf.
5. **Fail-safe lokal am Gerät, nicht in der Cloud.** Aggregatoren hielten
   Rückfallregeln nicht immer ein (EDGE). SAPN (Advanced VPP mit Tesla) hat 5-kW-Fallback (korr. lt. 06) und
   Ende-zu-Ende-Test bei Inbetriebnahme. → Gerät fällt bei Kommunikations- oder
   Signaturverlust selbstständig auf sichere Standardwerte zurück, mit Zeitlimit
   für jeden Befehl.
6. **Erreichbarkeit einplanen: 70–98 % statt 100 %.** Bei Heim-WLAN/Mobilfunk
   (AEMO) und auf dem Land (EDGE) fällt die Verbindung aus. → Überbuchung bzw.
   Puffer (VPPs bis 10 %), Statusmeldungen, Kanalredundanz (hier passt der
   LoRaWAN-/Mobilfunk-Ansatz des Teams).
7. **Compliance-Metriken realistisch wählen.** Eine harte 90-%-Instantanregel
   erzwingt Überlieferung (EDGE). → Energie- und Intervallmetriken mit Toleranz,
   ein Profil-Parameter statt Einzelfall-Vertrag.
8. **Kleine Engpassregionen bedeuten wenige Anbieter.** Lokale Märkte im
   Verteilnetz sind illiquide (enera). Für Heimspeicher ist ein regulierter
   Abrufmechanismus mit fester Vergütung (Ausnahmefall, zeitlich begrenzt, wie in
   der Challenge beschrieben) wahrscheinlich robuster als ein lokaler Markt.
9. **Akzeptanz:** Ausschlüsse frustrieren (Symphony). Ungewöhnliches
   Batterieverhalten fällt Kunden auf (EDGE). Kunden wollen Transparenz zum Ertrag
   (AEMO VPP Report 4). → App- bzw. Kundenschnittstelle mit Abrufprotokoll ist Teil
   des Profils.
10. **Rebound beachten.** 25–50 % Rebound nach Abregelung (Enedis/InterFlex). Nach dem
    Ende eines Abrufs braucht es eine gestaffelte Rückkehr, keine
    Gleichzeitigkeit.

---

## Offene Fragen an Smart Grids Austria

1. Gibt es in Österreich (z. B. Netz OÖ, Salzburg Netz, Energienetze Steiermark)
   **unveröffentlichte Feldergebnisse** zu Heimspeicher-Abrufen, etwa aus LEAFS
   (Köstendorf) oder späteren Projekten: Reaktionsquote, Erreichbarkeit, Kosten je
   Teilnehmer?
2. Ist das **Entladen** von Kundenspeichern auf VNB-Anforderung in AT überhaupt
   vorgesehen, oder nur Laden/Abregeln? Wie wird die Einspeisung bilanziell
   behandelt (Lieferant, Bilanzgruppe)?
3. Welche **Smart-Meter-Daten** (15-min-Werte, Kundenschnittstelle) dürfen VNB in AT
   für eine Erbringungsprüfung nutzen, und wie schnell liegen sie vor?
4. Welche **Compliance-Toleranz** hält ein VNB für akzeptabel (vgl. EDGE 90 %,
   Symphony ≥ 95 % je Intervall)?
5. Welche **Reaktionszeit** braucht der VNB für Engpässe in Nieder- und
   Mittelspannung realistisch: Minuten oder Viertelstunde? Davon hängen
   Kanalwahl und Testabrufdesign ab.
6. Wie oft dürfen **Testabrufe** stattfinden, ohne den Kunden zu stören, und
   wer bezahlt sie?
7. Gibt es Positionen der österreichischen VNB zu **Pflicht-Schnittstellen**
   (analog CSIP-AUS-Mandat) oder zum Fail-safe-Standardverhalten bei
   Kommunikationsverlust?
8. Wird ein **Ampelmodell mit VNB-Vorrang** (vgl. hybrid-VPP4DSO) für den
   ElWG-Rahmen angestrebt?

---

## Quellenliste

**Australien**
- AEMO (2023): Project EDGE Final Report. https://arena.gov.au/assets/2023/10/AEMO-Project-EDGE-Final-Report.pdf
- Deloitte Access Economics (2023): Project EDGE CBA Executive Summary (revised). https://arena.gov.au/assets/2024/01/AEMO-Project-Edge-Executive-Summary-Revised.pdf
- AEMO: Project EDGE Projektseite. https://aemo.com.au/initiatives/major-programs/nem-distributed-energy-resources-der-program/der-demonstrations/project-edge
- Western Power / Synergy / AEMO (2024): Project Symphony – Pilot Results and Recommendations. https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf
- ARENA Knowledge Bank Project Symphony. https://arena.gov.au/knowledge-bank/western-power-project-symphony-pilot-results-and-recommendations
- SA Power Networks (2021): Advanced VPP Grid Integration – Final Report. https://arena.gov.au/assets/2021/05/advanced-vpp-grid-integration-final-report.pdf
- AEMO (2021): NEM Virtual Power Plant Demonstrations – Knowledge Sharing Report #4. https://aemo.com.au/-/media/files/initiatives/der/2021/vpp-demonstrations-knowledge-sharing-report-4.pdf?la=en
- SolarQuotes: AEMO report VPP (Sekundärquelle zu Report 1). https://solarquotes.com.au/blog/aemo-report-vpp

**Deutschland**
- Jacobs University Bremen / Universität Duisburg-Essen (2020): Ökonomische und regulatorische Fragestellungen zum enera-Flexmarkt. https://www.ewl.wiwi.uni-due.de/fileadmin/fileupload/BWL-ENERGIE/Arbeitspapiere/RePEc/pdf/wp2001_OEkonomischeUndRegulatorischeFragestellungenZumEnera-FlexMarkt.pdf
- EPEX SPOT (2020): Annual Press Release 2019. https://www.epexspot.com/sites/default/files/download_center_files/200113_EPEX%20SPOT_2019_Annual%20Press%20Release_.pdf
- EPEX SPOT / EWE (2020): Pressemitteilung größter Abruf enera. https://www.epexspot.com/sites/default/files/download_center_files/200415_EPEX_EWE_ENERA_Pressemitteilung_DE.pdf
- EPEX SPOT: First trade on flexibility platform enera. https://epexspot.com/en/news/first-trade-flexibility-platform-enera-completed-successfully
- ZfK: 360 MW in enera-Flexmarkt eingebunden. https://www.zfk.de/energie/strom/360-mw-in-enera-flexmarkt-eingebunden
- pv magazine (08.05.2019): TenneT und Sonnen … Blockchain-vernetzte Heimspeicher. https://www.pv-magazine.de/2019/05/08/tennet-und-sonnen-sehen-grosses-potenzial-fuer-blockchain-vernetzte-photovoltaik-heimspeicher/
- Solarserver (08.05.2019): Hausspeicher stabilisieren das Stromnetz. https://www.solarserver.de/2019/05/08/hausspeicher-stabilisieren-das-stromnetz/

**Niederlande**
- GOPACS. https://www.gopacs.eu/
- ETPA: GOPACS Knowledge Hub. https://www.etpa.nl/knowledge-hub/gopacs
- Solar Magazine: GOPACS bundelt flexbiedingen. https://solarmagazine.nl/nieuws-zonne-energie/i39815/gopacs-bundelt-per-direct-flexbiedingen-van-meerdere-handelsplatformen
- Solar Magazine (18.11.2024): Thuisbatterij heeft merendeel van de tijd positief effect op netcongestie. https://solarmagazine.nl/nieuws-zonne-energie/i39053/thuisbatterij-heeft-merendeel-van-de-tijd-positief-effect-op-netcongestie
- Liander (2025): Rapport pilot netbewust thuisladen. https://www.liander.nl/-/media/files/nieuws/250408---rapport-pilot-netbewust-thuisladen.pdf

**Vereinigtes Königreich**
- NESO (2023): Demand Flexibility Service – Winter 2022/23 review. https://neso.energy/document/287006/download
- ERM/CSE für NESO: DFS Smart Meter Data Evaluation Winter 2022/23. https://www.neso.energy/document/371411/download
- Piclo (20.08.2024): EDP invests in Piclo. https://www.piclo.energy/press-releases/edp-invests-in-piclo-to-unlock-new-opportunities-in-flexibility-markets
- Current News: Storage dominates in UKPN's flexibility procurement. https://current-news.co.uk/storage-dominates-in-ukpns-most-recent-flexibility-procurement-piclo-says
- Current News: UKPN to use virtual power plant for flexibility services. https://current-news.co.uk/ukpn-to-use-virtual-power-plant-for-flexibility-services
- Electrical Review (10.01.2025): UKPN DSO reaches 2GW flexibility milestone. https://electricalreview.co.uk/2025/01/10/uk-power-networks-dso-reaches-2gw-flexibility-milestone/
- pv magazine (23.04.2025): UK DSO delivers 4.4 GWh of day-ahead flexibility. https://www.pv-magazine.com/2025/04/23/ai-helps-uk-dso-deliver-4-4-gwh-of-day-ahead-flexibility-in-one-year/
- WPD: IntraFlex. https://www.westernpower.co.uk/projects/intraflex
- The Energyst: WPD and Nord Pool flexibility market trial. https://theenergyst.com/wpd-and-nord-pool-combine-on-broader-flexibility-market-trial/

**Österreich**
- AIT et al. (2022): Flex+ – Publizierbarer Endbericht. https://www.ait.ac.at/fileadmin/user_upload/20220729_Publizierbarer_Endbericht_Final.pdf
- AIT: LEAFS Projektseite. https://www.ait.ac.at/en/leafs
- Solarserver (08.05.2018): Probelauf für die flexible Energiezukunft (LEAFS). https://www.solarserver.de/2018/05/08/probelauf-fuer-die-flexible-energiezukunft/
- Prüggler (2019): Heimspeichersysteme und zentrale Batteriespeicher, IEWT 2019. https://iewt2019.eeg.tuwien.ac.at/download/contribution/presentation/112/112_presentation_20190215_102253.pdf
- Hasanagic et al. (2026): Regionalisierte Prognose der PV-Heimspeicher in Österreich bis 2040, EnInnov 2026. https://www.tugraz.at/fileadmin/user_upload/Events/Eninnov/EnInnov2026/files/lf/544_LF_Hasanagic.pdf
- Spreitzhofer et al. (2016): hybrid-VPP4DSO, EnInnov 2016. https://www.tugraz.at/fileadmin/user_upload/Events/Eninnov2016/files/kf/Session_E1/KF_Spreitzhofer.pdf

**EU / Nordics**
- Enedis (Phelizon): Smart Grids, EPRG-Präsentation (InterFlex-Ergebnisse). https://www.jbs.cam.ac.uk/wp-content/uploads/2024/01/eprg-A.-Phelizon_Enedis-Smart-Grids-MIT-Sorbonne.pdf
- ČEZ Distribuce: InterFlex abgeschlossen. https://www.cez.cz/nextcez/cs/pro-media/tiskove-zpravy/cez-distribuce-uspesne-dokoncila-smart-grid-projekt-interflex-81467
- Sympower: InterFlex Kick-off. https://sympower.net/sympower-officially-kicks-off-the-european-smart-grid-project-interflex/
- E.DSO: EUniversal. https://www.edsoforsmartgrids.eu/euniversal
- Stochastic flexibility needs assessment: learnings from EUniversal's German demonstration. https://arxiv.org/pdf/2311.12227
- OneNet: Regulatory and demo assessment (EUI Cadmus). https://cadmus.eui.eu/handle/1814/76110
- Heat Pumping Technologies: sthlmflex Case Study. https://heatpumpingtechnologies.org/project57/case-studies/sthlmflex-creating-and-testing-a-flexibility-market-in-stockholm/
- Svenska kraftnät: sthlmflex Status 2020. https://www.svk.se/siteassets/2.utveckling-av-kraftsystemet/forskning-och-utveckling/sthlmflex/sthlmflex-information-20200828-status.pdf
- Statnett: NorFlex. https://www.statnett.no/en/about-statnett/research-and-development/our-prioritised-projects/norflex/
- Nordic Energy Research (2025): In-depth case studies of flexibility initiatives. https://pub.norden.org/nordicenergyresearch2025-03/in-depth-case-studies-of-flexibility-initiatives.html
