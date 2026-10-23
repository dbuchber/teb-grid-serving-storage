# 4. Security & Zertifizierung

Stand: 23.10.2026. Blickwinkel: defensiv (Bedrohungsmodell und Schutzmaßnahmen), keine Exploit-Details.
Kennzeichnung: **[unbestätigt]** = nur Sekundärquelle, widersprüchlich oder nicht im Primärtext geprüft.
Hinweis zur Methode: EUR-Lex war während der Recherche hinter einer WAF-Abfrage nicht abrufbar. Daten zu CRA und RED stammen deshalb von den Kommissionsseiten, Daten zu NIS2 und NCCS aus Sekundärquellen. Vor dem Pitch gegen EUR-Lex prüfen.

---

## Kernaussagen

1. **Die Gefahr liegt im Aggregat, nicht im Einzelgerät.** Laut der DNV-Studie für SolarPower Europe kann eine gezielte Kompromittierung von **3 GW** Erzeugung „significant implications“ für das europäische Netz haben. Mehr als ein Dutzend Hersteller steuern heute deutlich mehr als 3 GW installierte Wechselrichterleistung ([SPE, 29.4.2025](https://www.solarpowereurope.org/press-releases/new-report-solar-sector-proposes-solutions-to-mitigate-critical-cybersecurity-risks)). Ein bidirektionaler Steuerkanal (laden/entladen) vergrößert diese Hebelwirkung, weil ein Angreifer Last- und Erzeugungssprünge kombinieren könnte.
2. **Die größte heutige Angriffsfläche sind die Hersteller-Clouds, nicht die Netzbetreiber-Kanäle.** Bitdefender fand 2024 Schwachstellen in der Solarman-Plattform, die eine Kontoübernahme ermöglicht hätten; eine tatsächliche Kompromittierung ist nicht berichtet. Solarman und Deye zusammen stehen für rund **195 GW** (> 2 Mio. Anlagen, ca. 20 % der weltweiten Solarerzeugung); gemeldet am 22.5.2024, gepatcht bis Juli 2024 (korr. lt. 06) ([SecurityWeek](https://www.securityweek.com/vulnerabilities-exposed-widely-used-solar-power-systems-to-hacking-disruption/)). Forescout fand 2025 46 neue Schwachstellen bei Sungrow, Growatt und SMA, ausnutzbar auch über die Cloud ([Forescout, 27.3.2025](https://www.forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure)). Ein netzbetreiberseitiger Steuerkanal muss deshalb **unabhängig von der Hersteller-Cloud** funktionieren und darf sie nicht als Vertrauensanker brauchen.
3. **Bestehende Rundsteuer- und Funkkanäle sind teils unauthentifiziert.** Das EFR-Funkrundsteuersystem (> 1,3 Mio. Empfänger in DE, AT, CZ, HU, SK) arbeitet nach dem 38C3-Vortrag mit „completely unencrypted and unauthenticated“ Protokollen ([38C3 BlinkenCity](https://events.ccc.de/congress/2024/hub/event/blinkencity-radio-controlling-street-lamps-and-power-plants/)). **Signierte Befehle sind also eine echte Verbesserung gegenüber dem Status quo in AT**, keine Kür.
4. **Die Regulatorik ist 2026 in Bewegung, sie ist aber nicht gerätespezifisch.** Die CRA-Meldepflichten gelten seit 11.9.2026, die vollen Pflichten ab 11.12.2027 ([EU-Kommission](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)). RED DA 2022/30 gilt seit August 2025 für Funkgeräte, also auch für Wechselrichter mit WLAN/LTE. NIS2 trifft Netzbetreiber und Aggregatoren (AT: NISG 2026 ab 1.10.2026). **Es fehlen verbindliche, energiespezifische Anforderungen an einen Steuerbefehl** (Signatur, Grenzen, Ablaufzeit). Genau diese Lücke kann unser Profil füllen.
5. **Die Drittstaaten-Debatte wird zum Marktzugangsthema.** Litauen verbietet seit 1.5.2025 den Fernzugriff aus „Bedrohungsstaaten“ auf Anlagen > 100 kW ([LRT](https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems)). Die Kommission schließt Hochrisiko-Wechselrichter schrittweise aus EU-finanzierten Projekten aus und plant eine Liste von Hochrisiko-Lieferanten im neuen Cybersecurity Act ([Euronews, 4.5.2026](https://www.euronews.com/my-europe/2026/05/04/eu-moves-to-ban-high-risk-inverters-from-china-over-cybersecurity-threats); [pv magazine, 21.1.2026](https://www.pv-magazine-india.com/2026/01/21/eu-to-ban-chinese-inverters-commission-proposal-in-cybersecurity-mulls-high-risk-vendors-list)). Eine **herstellerunabhängige, lokal verifizierende Steuerschnittstelle** entschärft das Problem unabhängig vom Herkunftsland.
6. **Für Geräteidentität gibt es erprobte Vorbilder:** die SMGW-PKI des BSI (Root-CA beim BSI, TR-03109-4), die IEEE-2030.5-PKI für CSIP-AUS (SERCA → MICA/MCA → Gerätezertifikat) und EEBus SHIP (TLS mit Geräte-SKI, Pairing). Für ein EU-Profil am nächsten liegt eine **hierarchische PKI mit Herstellerzwischen-CA und ab Werk eingebrachtem Schlüssel im Secure Element**.
7. **LoRaWAN-Multicast braucht eine eigene Signatur auf Anwendungsebene.** Alle Geräte einer Multicast-Gruppe teilen einen symmetrischen Sicherheitskontext. Ein kompromittiertes Gerät könnte dann Befehle an die ganze Gruppe senden ([TTN-Folien zu TS005](https://www.thethingsnetwork.org/forum/uploads/default/original/3X/7/a/7af5e0849f922f7ee00a7fd843b7d12e9d0909fa.pdf)). Wir brauchen deshalb eine **asymmetrische Signatur des Netzbetreibers**, unabhängig vom Kanal.
8. **Die Verifikation über den Smart Meter ist zugleich ein Sicherheitsmechanismus.** Sie ist ein unabhängiger Messpfad, der manipulierte oder nicht ausgeführte Befehle erkennt. Mit regelmäßigen Testabrufen entsteht eine Basislinie je Gerät, gegen die Anomalien auffallen (eigene Ableitung). Einschränkung: Unabhängig sind nur die Backend-Werte des Netzbetreibers, und die liegen in AT erst am Folgetag vor (Wien: einmal täglich). Die Kundenschnittstelle (1–5 s) ist gegenüber dem Kunden nicht manipulationssicher, weil er den Schlüssel kennt (siehe 03) (korr. lt. 06).

---

## Bedrohungsmodell

### Schutzziele

| Schutzziel | Bedeutung für Grid-Serving Storage |
|---|---|
| Integrität und Authentizität von Befehlen | Nur der berechtigte Netzbetreiber bzw. Lieferant darf in seinem Segment steuern |
| Verfügbarkeit | Im Engpassfall müssen Befehle ankommen. Fällt der Kanal aus, darf das Netz nicht schlechter dastehen als ohne Steuerung |
| Begrenzung der Wirkung | Kein einzelner Schlüssel und kein einzelner Kanal darf mehr als einen definierten Leistungsblock bewegen |
| Nachvollziehbarkeit | Jeder Befehl und jede Reaktion ist beweisbar protokolliert (Abrechnung, Streitfälle, Forensik) |
| Vertraulichkeit/Datenschutz | Messwerte und Standortdaten zeigen Anwesenheit und Gewohnheiten (DSGVO) |

### Akteure

| Akteur | Motiv | Fähigkeit | Bezug |
|---|---|---|---|
| Staatlicher Akteur | Destabilisierung, Erpressungspotenzial im Konfliktfall | Hoch, auch Lieferkette/Firmware | Reuters-Bericht zu undokumentierten Funkbauteilen ([pv magazine, 14.5.2025](https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/)) [unbestätigt, anonyme Quellen] |
| Hersteller bzw. dessen Cloud (gewollt oder kompromittiert) | Lizenz-/Garantiedurchsetzung, staatlicher Druck, Fehler | Direkter Zugriff auf Firmware und Konfiguration | Deye-Abschaltungen USA 11/2024 ([heise](https://heise.de/-10183716)); Deye bestreitet Fernsteuerung |
| Kriminelle | Erpressung, Marktmanipulation (Preisspitzen), Botnetze | Mittel, nutzt bekannte Schwachstellen | DDoS-Missbrauch von Wechselrichtern laut RDI-Test NL ([Gaslicht](https://www.gaslicht.com/nieuws/omvormers-zonnepanelen-gevoelig-voor-storingen-en-hacks)) |
| Innentäter (Netzbetreiber, Aggregator, Installateur) | Sabotage, Fehlbedienung | Legitime Zugänge | Grund für Mehr-Augen-Freigabe |
| Kunde/Anlagenbetreiber | Vergütung ohne Leistung, Steuerung umgehen | Lokaler Gerätezugriff | Grund für Smart-Meter-Verifikation |
| Forscher/Hobbyisten | Aufmerksamkeit, Demonstration | Mittel | 38C3-Funkrundsteuer-Demo |

### Angriffsziele (Wirkung)

- **Massenschalten:** gleichzeitiges Ändern von Erzeugung oder Last zur Frequenz- oder Spannungsstörung. MadIoT zeigt das in Simulation für Lasten ([Soltan et al., USENIX Security 2018](https://www.usenix.org/conference/usenixsecurity18/presentation/soltan)). Forescout zitiert „previous research“: rund 4,5 GW Kontrollverlust würden genügen, um die Frequenz auf 49 Hz zu senken (Lastabwurf), das seien < 2 % von rund 270 GW PV in Europa ([Forescout-Blog](https://www.forescout.com/blog/grid-security-new-vulnerabilities-in-solar-power-systems-exposed/)) **[unbestätigt, Originalstudie nicht genannt]**.
- **Bidirektionaler Hebel (eigene Ableitung):** Ein Speicher, der von Laden auf Entladen springt, bewirkt etwa den doppelten Leistungssprung seiner Nennleistung. Darum sind Rampen- und Sprunggrenzen wichtiger als bei reiner Abregelung.
- **Lokaler Netzschaden:** gezielte Überlastung eines Strangs oder Transformators durch synchrones Laden bzw. Einspeisen in einem Segment.
- **Marktmanipulation:** künstliche Engpässe, Flex-Abrufe zu falschen Preisen, Fake-Verfügbarkeit.
- **Betrug:** Gerät meldet Reaktion, liefert aber keine.
- **Datenabfluss:** Profile, Standorte, Anlagenregister ([Bitdefender laut SecurityWeek](https://www.securityweek.com/vulnerabilities-exposed-widely-used-solar-power-systems-to-hacking-disruption/)).

### Angriffsflächen

| Fläche | Typische Schwäche (belegt) | Relevanz für unser Profil |
|---|---|---|
| Hersteller-Cloud/Portal | IDOR, fest codierte Zugangsdaten, Kontoübernahme ([Forescout](https://www.forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure); [CISA ICSA-25-105-04 Growatt](https://www.cisa.gov/news-events/ics-advisories/icsa-25-105-04)) | Darf nicht im Vertrauenspfad des Netzbefehls liegen |
| Lokales Web-/Management-Interface | Rund 35.000 im Internet exponierte Solar-Geräte, über 3/4 davon in Europa ([Forescout, 3.6.2025](https://www.forescout.com/blog/the-security-risks-of-internet-exposed-solar-power-systems/)) | Kommunikationsmodul ohne eingehende Internet-Ports |
| Gateway/Dongle (WLAN/LTE) | Enphase IQ Gateway: 6 CVEs, volle Übernahme bei Erreichbarkeit aus nicht vertrauenswürdigem Netz ([DIVD-2024-00011](https://csirt.divd.nl/cases/DIVD-2024-00011/)) | Modul fällt unter RED DA/EN 18031 und den CRA |
| Firmware-Update-Kanal | Hersteller kann Verhalten nachträglich ändern ([ESMC, 30.4.2025](https://esmc.solar/restrict-remote-access-of-pv-inverters-from-high-risk-vendors/)) | Grenzen für Netzbefehle unabhängig von der Firmware machen (Sicherheitsmodul/Policy) |
| Funkrundsteuerung (Langwelle) | Unverschlüsselt, unauthentifiziert ([38C3](https://events.ccc.de/congress/2024/hub/event/blinkencity-radio-controlling-street-lamps-and-power-plants/)) | Ablösung bzw. Ergänzung durch signierte Befehle |
| LoRaWAN-Multicast | Gemeinsamer symmetrischer Gruppenschlüssel ([TTN/TS005](https://www.thethingsnetwork.org/forum/uploads/default/original/3X/7/a/7af5e0849f922f7ee00a7fd843b7d12e9d0909fa.pdf); [LoRa Alliance TS005](https://resources.lora-alliance.org/document/ts005-2-0-0-remote-multicast-setup)) | Signatur auf Anwendungsebene nötig |
| Kundeninternet | Verfügbarkeit nicht garantiert, Heimnetz unsicher | Nur als einer von mehreren Kanälen, Fail-safe nötig |
| Backend des Netzbetreibers/Aggregators | Zentraler Single Point of Failure, Innentäter | Mehr-Augen-Freigabe, HSM, Segmentgrenzen |
| Lieferkette/Hardware | Undokumentierte Funkmodule [unbestätigt] ([pv magazine](https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/)) | Offenlegung der Kommunikationsbauteile (SBOM/HBOM) |

---

## Geräteidentität und Schlüsselverwaltung

| Vorbild | Aufbau | Was wir übernehmen können | Quelle |
|---|---|---|---|
| **SMGW-PKI (DE, BSI)** | Root-CA beim BSI (gesetzlich, §28 GDE bzw. MsbG [unbestätigt welcher Paragraph aktuell]), Sub-CAs registrierter Betreiber, Endnutzerzertifikate für Gateway und externe Marktteilnehmer. TR-03109-4 definiert Zertifikats- und Sperrlistenprofile | Staatlich verankerter Vertrauensanker, Sperrlisten, Rollen für Marktteilnehmer | [BSI TR-03109-4](https://bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Smart-metering/Smart-Meterin-PKI/TechnRichtlinie/tr_03109-4_node.html); [Telesec ChangeLog Root (TR-03109-4 v1.2.1, CP v1.1.2)](https://www.telesec.de/assets/downloads/Smart-Metering-PKI/ChangeLog_Root.pdf) |
| **IEEE 2030.5 / CSIP-AUS** | SERCA (offline) → MCA/MICA (Hersteller, Netzbetreiber) → Gerätezertifikat, direkt auf das Gerät gebracht. Australien nutzt eine Interim-PKI bis zur „National Energy PKI“ | Herstellerzwischen-CA, Gerätezertifikat ab Werk, getrennte Test- und Produktions-PKI | [SunSpec Certificate Policy](https://sunspec.org/wp-content/uploads/2025/01/SunSpecCertificatePolicy-V1.0-2019-02-13-1.pdf); [SwitchDin Interim-PKI](https://support.switchdin.com/hc/en-us/articles/48546542623129-What-is-the-purpose-of-our-Public-Key-Infrastructure-PKI-service) [unbestätigt, Hierarchietiefe 3 vs. 4 Ebenen widersprüchlich] |
| **EEBus SHIP** | TLS mit Gerätezertifikat; Vertrauen über SKI (Subject Key Identifier) und Pairing (Nutzerbestätigung bzw. Auto-Accept) | Gut für die lokale Kopplung (EMS ↔ Wechselrichter), **nicht** als Vertrauensanker für Netzbefehle, da kein zentraler Widerruf | [enbility/ship-go](https://github.com/enbility/ship-go) [unbestätigt, Spezifikationstext nicht geprüft] |
| **CRA Anhang IV** | Smart Meter Gateways und „other devices for advanced security purposes“ sind *kritische* Produkte, für sie ist künftig eine Zertifizierung vorgesehen | Ein Kommunikationsmodul mit Sicherheitsfunktion könnte in diese Klasse fallen, das ist zu klären | [Springlex, Anhang IV CRA](https://www.springlex.eu/en/packages/cra/cra-regulation/annex-4/); [CEN-CENELEC Webinar SMGW, 2/2026](https://www.cencenelec.eu/media/CEN-CENELEC/Events/Webinars/2026/2026-02-23_cra-standards-unlocked-cybersecurity-requirements-for-smgw_final.pdf) [unbestätigt, Einstufung eines Steuermoduls offen] |

**Empfehlung zur Lebenszyklusverwaltung (eigene Ableitung aus den Vorbildern):**
- **Provisionierung ab Werk:** Das Schlüsselpaar wird im Secure Element/TPM erzeugt, der private Schlüssel ist nicht exportierbar. Die Hersteller-CA signiert das Gerätezertifikat in der Fertigung. Die Seriennummer ist im Zertifikat gebunden.
- **Inbetriebnahme:** Der Netzbetreiber bindet Gerätezertifikat, Zählpunkt und Netzsegment (z. B. über Installateur-Prozess oder Netzanschlussmeldung). Erst danach nimmt das Gerät Befehle des Netzbetreibers an.
- **Vertrauensanker im Gerät:** öffentliche Schlüssel bzw. Zertifikate der berechtigten Befehlsgeber (Netzbetreiber-CA, ggf. Lieferant), nur über signiertes Update austauschbar.
- **Rotation:** kurzlebige Befehlssignierschlüssel im HSM des Netzbetreibers, langlebige Wurzeln offline.
- **Widerruf:** kompakte Sperrliste bzw. Sperr-Broadcast, auch über LoRaWAN verteilbar. Alternativ kurze Zertifikatslaufzeiten für Befehlsgeber, damit Widerruf im Gerät selten nötig ist.
- **Krypto-Agilität:** Algorithmuswechsel muss per Update möglich sein (Post-Quanten-Migration). ECDSA P-256 (64-Byte-Signatur) passt in LoRaWAN-Nutzlasten erst ab DR3 (115 Byte), nicht bei DR0–2 (51 Byte) (laut 03; korr. lt. 06). Gruppenbefehle müssen kompakt kodiert werden.

---

## Regulatorik (Stand 23.10.2026)

| Regel | Gilt für | Frist/Status | Bezug zum Profil | Quelle |
|---|---|---|---|---|
| **Cyber Resilience Act** (VO (EU) 2024/2847) | Hersteller, Importeure, Händler aller Produkte mit digitalen Elementen (Wechselrichter, Speicher-BMS, Kommunikationsmodule) | In Kraft 10.12.2024; **Meldepflichten seit 11.9.2026** (24 h Frühwarnung, 72 h Meldung); **volle Pflichten ab 11.12.2027** | Security by Design, Schwachstellenmanagement, Updates, SBOM. Smart Meter Gateways sind *kritisch* (Anhang IV) | [EU-Kommission](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act); [Jones Day zu Meldepflichten](https://www.jonesday.com/en/insights/2026/07/eu-cyber-resilience-act-24hour-reporting-duties-start-september-11-2026); [Anhang IV](https://www.springlex.eu/en/packages/cra/cra-regulation/annex-4/) |
| **CRA-Durchführungsverordnung (EU) 2025/2392** | Technische Beschreibung wichtiger und kritischer Produkte | Veröffentlicht ABl. 1.12.2025 | Prüfen, ob unser Steuermodul „important“ oder „critical“ ist [unbestätigt] | [Springlex 2025/2392](https://www.springlex.eu/en/packages/cra/tdpc-regulation/annex-2/) |
| **RED Delegierte VO (EU) 2022/30** + **EN 18031-1/-2/-3:2024** | Mit dem Internet verbundene Funkgeräte (WLAN-/LTE-Dongles von Wechselrichtern, Speicher mit Funk) | Gilt **seit 1.8.2025**. EN 18031 im ABl. mit Einschränkungen gelistet (Beschluss (EU) 2025/138), bei Abweichung ist eine benannte Stelle nötig. **Aufhebung durch DelVO (EU) 2026/339 mit Wirkung 11.12.2027** (dann gilt der CRA) | Übergangsregime bis Ende 2027. Die NL-Behörde RDI kann nicht konforme Wechselrichter vom Markt nehmen | [EU-Kommission RED](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en); [TÜV SÜD](https://www.tuvsud.com/en-gb/resource-centre/blogs/uk/testing-and-certification-blog/red-cyber-standards-oj-citation); [Solar Magazine NL](https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al) |
| **NIS2** (RL (EU) 2022/2555) | Anhang I Energie: u. a. Verteilnetzbetreiber, Versorger, Marktteilnehmer mit **Aggregierung, Laststeuerung oder Speicherdiensten** | Umsetzungsfrist 17.10.2024 (verbreitet verspätet) | Netzbetreiber-Backend und Aggregatoren unterliegen Risikomanagement- und Meldepflichten | [Advisera, Anhang I](https://advisera.com/nis2/sectors-of-high-criticality/) [unbestätigt, nicht gegen EUR-Lex geprüft] |
| **NIS2 – AT: NISG 2026** | Rund 4.000 Einrichtungen in 18 Sektoren; Behörde: Bundesamt für Cybersicherheit (BMI) | Kundgemacht BGBl. I Nr. 94/2025, **gilt ab 1.10.2026**; Registrierung binnen 3 Monaten | Österreichische VNB und Aggregatoren sind ab jetzt verpflichtet | [KPMG AT](https://kpmg.com/at/de/insights/2025/12/nisg-2026.html); [Deloitte Infoblatt](https://www.deloitte.com/content/dam/assets-zone2/at/de/docs/studien/2026/infoblatt-nisg.pdf); [WKO](https://www.wko.at/stmk/information-consulting/unternehmensberatung-buchhaltung-informationstechnologie/nisg-2026-beschlossen-unternehmen-muessen-handeln); Datum im RIS bestätigt (Inkrafttretensdatum 01.10.2026, [RIS](https://ris.bka.gv.at/Dokumente/Bundesnormen/NOR40277627/NOR40277627.pdf)) (korr. lt. 06) |
| **NIS2 – DE: NIS2UmsuCG** | Rund 29.500 Unternehmen | In Kraft **6.12.2025**, BSI-Registrierung bis 6.3.2026 | Vergleich für AT | [usd AG](https://www.usd.de/nis2umsucg-offiziell-in-kraft/) |
| **Network Code on Cybersecurity** (DelVO (EU) 2024/1366) | Grenzüberschreitende Stromflüsse; nur als „high-impact“ bzw. „critical-impact“ eingestufte Einrichtungen (über den ECII-Index) | In Kraft seit 13.6.2024; gestaffelte Risikobewertungen, Einstufung und Pflichten laut Sekundärquellen 2027/2028 [unbestätigt] | **Aggregierte Kleinanlagen** könnten über Aggregatoren oder VNB in den Anwendungsbereich fallen. SPE schlägt vor, Fernsteuerung aggregierter DER über den NCCS zu regeln | [EUR-Lex (ELI)](https://eur-lex.europa.eu/eli/reg_del/2024/1366/oj); [ACER](https://www.acer.europa.eu/electricity/cybersecurity-network-code); [InnoBu](https://www.innobu.com/en/articles/nccs-network-code-cybersecurity-obligations-2026.html) [unbestätigt] |
| **BSI TR-03109** (DE, Familie) | Smart Meter Gateway, SM-PKI (-4), CLS-Kanal zur Steuerbox | Gültig (TR-03109-4 v1.2.1 laut ChangeLog 08/2024, ggf. neuer) | Referenz für „Steuerung nur über zertifiziertes Gateway“. Laut BNetzA (2023) sollen energiewirtschaftlich relevante Steuerdaten nur über SMGW fließen | [BSI TR-03109-4](https://bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Smart-metering/Smart-Meterin-PKI/TechnRichtlinie/tr_03109-4_node.html); [ZfK](https://www.zfk.de/digitalisierung/smart-city-energy/bsi-sicherheitsbedenken-gegen-pv-wechselrichter-das-sagt-die-branche) |
| **DE: § 94 EEG (Solarspitzengesetz)** | Verordnungsermächtigung für weitere Berechtigte zur Fernregelung | Umsetzung offen | BSI warnt vor einer Steuerung über Hersteller-Backends, die SMGW und Steuerbox umgehen würde | [pv magazine DE, 30.12.2025](https://www.pv-magazine.de/2025/12/30/cybersicherheit-von-photovoltaikanlagen-reale-risiken-falsche-loesungen-moegliche-wege/) |
| **Litauen: Elektrizitätsgesetz Art. 73³** | Erzeugungsanlagen und Speicher > 100 kW | Beschluss 12.11.2024; in Kraft **1.5.2025**; Bestandsanlagen bis **1.5.2026** | Fernzugriff aus Staaten, die die Sicherheitsstrategie als Bedrohung nennt (u. a. China), ist verboten; Netzanschluss nur bei konformer Steuerung | [LRT](https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems); [pv magazine](https://www.pv-magazine.com/?p=39019) |
| **EU-Kommission: Förderausschluss Hochrisiko-Wechselrichter** | Alle EU-Förderinstrumente (inkl. EIB, EBRD) | Ankündigung 4.5.2026; fortgeschrittene Projekte bis 1.11.2026; volle Anwendung ab April 2027 | Nicht für Privatanlagen. Signal für die Richtung | [Euronews](https://www.euronews.com/my-europe/2026/05/04/eu-moves-to-ban-high-risk-inverters-from-china-over-cybersecurity-threats) |
| **Revision Cybersecurity Act (Vorschlag)** | IKT-Lieferketten, Liste von Hochrisiko-Lieferanten per Durchführungsrechtsakt | Vorschlag Januar 2026, im Gesetzgebungsverfahren | Könnte Wechselrichter erfassen; laut Berichten Rückruf bzw. Ausphasen bestehender Produkte möglich [unbestätigt] | [pv magazine](https://www.pv-magazine-india.com/2026/01/21/eu-to-ban-chinese-inverters-commission-proposal-in-cybersecurity-mulls-high-risk-vendors-list); [techUK](https://www.techuk.org/insights/news/eu-commission-publishes-cybersecurity-act-revision-proposal); [SPE-Statement](https://www.solarpowereurope.org/press-releases/statement-european-commission-publish-draft-revision-of-the-cybersecurity-act) |
| **UK Smart Charge Points Regulations 2021, Reg. 11** (Vorbild außerhalb EU) | Ladepunkte | In Kraft seit 2022 | **Zufällige Verzögerung bis 600 s (Standard)**, Maximum bis 1800 s fernkonfigurierbar. Direktes Vorbild für Randomisierung | [legislation.gov.uk](https://www.legislation.gov.uk/uksi/2021/1467/regulation/11) |

---

## Vorfälle und Studien

| Jahr | Ereignis / Studie | Kernbefund | Art | Quelle |
|---|---|---|---|---|
| 2018 | **MadIoT / BlackIoT** (Princeton, USENIX Security) | Botnetz aus Hochleistungsgeräten kann in Simulation lokale Ausfälle bis großflächige Blackouts verursachen | Studie | [USENIX](https://www.usenix.org/conference/usenixsecurity18/presentation/soltan) |
| 2023 | **RDI-Test (NL)** | Keiner von 9 getesteten Wechselrichtern erfüllte die angelegte Cybersecurity-Norm; 5 von 9 störten Funk | Behördliche Marktprüfung | [Gaslicht](https://www.gaslicht.com/nieuws/omvormers-zonnepanelen-gevoelig-voor-storingen-en-hacks); [Bright](https://www.bright.nl/nieuws/1136602/omvormer-zonnepanelen-omvormers-zonnepanelen-storing-hacken-veilig.html) [Sekundär] |
| 2024 (Apr–Aug) | **DIVD-2024-00011 Enphase IQ Gateway** | 6 CVEs (CVE-2024-21876…21881), Kombination erlaubt volle Übernahme ohne Authentifizierung, wenn das Gerät aus einem nicht vertrauenswürdigen Netz erreichbar ist. Rund 4 Mio. Systeme [Sekundär]. Gepatcht ab v8.2.4225 | Schwachstelle | [DIVD](https://csirt.divd.nl/cases/DIVD-2024-00011/); [pv magazine](https://www.pv-magazine.com/?p=38158) |
| 2024 (Aug) | **Bitdefender: Solarman/Deye-Cloud** | Schwachstellen gefunden: Kontoübernahme und Änderung von Wechselrichtereinstellungen wären möglich gewesen; kein Einbruch berichtet. Solarman- und Deye-Plattformen zusammen rund **195 GW** (> 2 Mio. Anlagen); fest codiertes Konto bei Deye; gemeldet 22.5.2024, gepatcht bis Juli 2024 (korr. lt. 06) | Schwachstelle (Cloud) | [SecurityWeek](https://www.securityweek.com/vulnerabilities-exposed-widely-used-solar-power-systems-to-hacking-disruption/); [Dark Reading](https://www.darkreading.com/ics-ot-security/solar-power-installations-worldwide-open-to-cloud-api-bugs) |
| 2024 (Nov) | **Deye-Geräte in USA/UK/Pakistan deaktiviert** | Ferndeaktivierung bzw. Autorisierungsprüfung im Feld. Deye bestreitet Fernsteuerung und verweist auf nicht zugelassene Graumarktgeräte | Vorfall (Herstellerkontrolle) | [heise](https://heise.de/-10183716); [Borncity](https://borncity.com/win/2024/11/28/deye-deactivates-solar-inverters-in-usa-uk-and-pakistan/) [Ursache unbestätigt] |
| 2024 (Dez) | **38C3 „BlinkenCity“** (Bräunlein, Melette) | EFR-Funkrundsteuerung: > 1,3 Mio. Empfänger in DE/AT/CZ/HU/SK, Protokolle Versacom/Semagyr unverschlüsselt und unauthentifiziert. Laut pv magazine rund 40 GW Erzeugung plus 20 GW Verbraucher steuerbar (Schätzung der Forscher); EFR bestreitet die Praxistauglichkeit | Studie/Demo | [CCC](https://events.ccc.de/congress/2024/hub/event/blinkencity-radio-controlling-street-lamps-and-power-plants/); [pv magazine DE](https://www.pv-magazine.de/2025/12/30/cybersicherheit-von-photovoltaikanlagen-reale-risiken-falsche-loesungen-moegliche-wege/) [GW-Zahl unbestätigt] |
| 2025 (Mär) | **Forescout SUN:DOWN** | 46 neue Schwachstellen bei Sungrow, Growatt, SMA. Von 93 bekannten Solar-Schwachstellen sind 80 % hoch/kritisch, rund 30 % CVSS 9,8–10. Ausnutzbar über Hersteller-Cloud; alle gepatcht | Schwachstellen | [Forescout PR](https://www.forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure); [Research-Seite](https://www.forescout.com/research-labs/sun-down-a-dark-side-to-solar-energy-grids/) |
| 2025 (Apr) | **CISA ICSA-25-105-04 Growatt Cloud** | Autorisierungsfehler (CWE-639) u. a. CVE-2025-27938, -30257, -30514, -31941 | Advisory | [CISA](https://www.cisa.gov/news-events/ics-advisories/icsa-25-105-04) [Details über SentinelOne, CISA-Text nicht geöffnet] |
| 2025 (29.4.) | **DNV/SolarPower Europe „Solutions for PV Cyber Risks to Grid Stability“** | 14 Risikobereiche: 3 kritisch, 6 hoch, 5 mittel. **3 GW** gezielt kompromittiert = erhebliche Netzwirkung. Empfehlung: verpflichtende sektorspezifische Kontrollen, Fernsteuerung aus Nicht-EU-Regionen begrenzen | Studie (Branche) | [SPE](https://www.solarpowereurope.org/press-releases/new-report-solar-sector-proposes-solutions-to-mitigate-critical-cybersecurity-risks) |
| 2025 (30.4.) | **ESMC-Positionspapier** | Huawei und Sungrow kontrollieren laut DNV-Bericht S. 40 den Fernzugriff auf **168 GW** PV in Europa; > 200 GW PV hängen an Wechselrichtern aus China; 70 % der 2023 installierten Wechselrichter stammen von chinesischen Herstellern. Forderung: „Inverter Security Toolbox“ | Lobby-Position | [ESMC](https://esmc.solar/restrict-remote-access-of-pv-inverters-from-high-risk-vendors/) [interessengeleitet, DNV-Original nicht geprüft] |
| 2025 (14./15.5.) | **Reuters: undokumentierte Kommunikationsbauteile** | US-Experten fanden in einigen chinesischen Wechselrichtern und Batterien nicht dokumentierte Kommunikationsgeräte (u. a. Mobilfunk); Umfang unbekannt | Medienbericht (anonyme Quellen) | [pv magazine](https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/); [Facilities Dive](https://www.facilitiesdive.com/news/rogue-communication-devices-found-on-chinese-made-solar-power-inverters/748237/) **[unbestätigt]** |
| 2025 (Jun) | **Forescout: exponierte Solargeräte** | Rund 35.000 Geräte von 42 Herstellern mit offenem Management-Interface; > 75 % in Europa; DE und GR je 20 % | Messung (Shodan, 9.5.2025) | [Forescout](https://www.forescout.com/blog/the-security-risks-of-internet-exposed-solar-power-systems/) |
| 2025 | **DERSec „Public History of Solar Energy Cyber Attacks and Vulnerabilities“** | 50 Offenlegungsereignisse und 4 öffentlich berichtete Angriffe auf PV. Rund 45 % der weltweiten Solarerzeugung (> 1 TW) gelten als „exposed“ | Studie (Branche) | [Solar Builder](https://solarbuildermag.com/news/report-nearly-50-of-global-solar-power-exposed-to-cyber-exploitation/) [Sekundär] |
| 2025 | **DIVD-2025-00015 SolaX Cloud** | Mehrere Schwachstellen in der Cloud-Plattform | Schwachstelle | [DIVD](https://csirt.divd.nl/cases/DIVD-2025-00015/) [Inhalt nicht geprüft] |
| 2025 (28.4.) | Iberischer Blackout | ENTSO-E-Abschlussbericht (März 2026): mehrere Ursachen (Spannung, Blindleistung, Kaskaden). **Kein Cyber-Bezug belegt**; nur als Kontext für Kaskadenrisiken | Netzereignis | [ENTSO-E](https://entsoe.eu/publications/blackout/28-april-2025-iberian-blackout) |

**Zur Einordnung:** Bestätigte *Angriffe* auf PV sind selten (DERSec: 4). Die Schwachstellenlage ist dagegen schlecht und die Konzentration hoch. SEIA betont den geringen Anteil an Energiesektor-Angriffen ([SEIA](https://seia.org/media/16958/)). Für den Pitch heißt das: Wir argumentieren mit **systemischem Risiko und Vorsorge**, nicht mit „es passiert ständig“.

---

## Schutzmaßnahmen

### A. Am Gerät (Kommunikationsmodul bzw. Wechselrichter)

| Maßnahme | Wirkung | Vorbild/Beleg |
|---|---|---|
| **Signierte Befehle (asymmetrisch, Ende-zu-Ende vom Netzbetreiber-HSM bis ins Gerät)**, unabhängig von der Transportverschlüsselung | Kanal (LoRaWAN, LTE, Internet) und Hersteller-Cloud sind nicht vertrauenswürdig nötig | TLS/Zertifikate bei IEEE 2030.5 in Kalifornien/Südaustralien ([pv magazine DE](https://www.pv-magazine.de/2025/12/30/cybersicherheit-von-photovoltaikanlagen-reale-risiken-falsche-loesungen-moegliche-wege/)); Multicast-Schwäche ([TTN/TS005](https://www.thethingsnetwork.org/forum/uploads/default/original/3X/7/a/7af5e0849f922f7ee00a7fd843b7d12e9d0909fa.pdf)) |
| **Befehl enthält Grenzen:** Segment-ID, Gerätegruppe, max. Leistung (Laden/Entladen), max. Dauer, **Ablaufzeit (notAfter)**, Sequenznummer/Nonce | Replay- und Ausweitungsschutz; ein abgefangener Befehl wirkt nur kurz und lokal | Eigene Ableitung; CSIP-AUS-Steuerobjekte sind zeitbegrenzt [unbestätigt, mit Block 3 prüfen] |
| **Lokale Plausibilisierung (Policy im Gerät, nicht änderbar durch Netzbefehl):** Befehl liegt im vertraglich bzw. normativ zulässigen Band (SoC-Grenzen, Netzanschlussleistung, Sprung-/Rampenlimit, Befehlsrate) | Selbst ein gültig signierter, aber unsinniger Befehl wird gekappt | Eigene Ableitung |
| **Fail-safe:** bei Kanalverlust oder Ablauf Rückkehr in den Kundenbetrieb bzw. eine sichere Default-Kennlinie (z. B. P(U), Frequenzverhalten nach EN 50549-1) mit randomisierter Rückkehr | Kein „eingefrorener“ Zustand nach Ausfall; kein Rebound-Peak | UK Reg. 11 (Randomisierung) ([legislation.gov.uk](https://www.legislation.gov.uk/uksi/2021/1467/regulation/11)) |
| **Randomisierung** von Start und Ende (Sekunden bis Minuten, je nach Anwendungsfall) | Glättet Sprünge auch bei legitimen Befehlen; erschwert synchrone Massenschaltung | UK: bis 600 s Standard, 1800 s max. ([legislation.gov.uk](https://www.legislation.gov.uk/uksi/2021/1467/regulation/11)); gestaffelte 50,2-Hz-Abschaltung in DE ([pv magazine DE](https://www.pv-magazine.de/2025/12/30/cybersicherheit-von-photovoltaikanlagen-reale-risiken-falsche-loesungen-moegliche-wege/)) |
| **Keine eingehenden Internet-Ports**, nur ausgehende, authentifizierte Verbindungen | Vermeidet den Shodan-Expositionspfad | [Forescout Exposure](https://www.forescout.com/blog/the-security-risks-of-internet-exposed-solar-power-systems/); [DIVD-Empfehlung](https://csirt.divd.nl/cases/DIVD-2024-00011/); BSI: lokal betreiben, Fernzugriff nur per VPN ([aroundhome zu BSI](https://www.aroundhome.de/neuigkeiten/cybersicherheit-fuer-solaranlagen-bsi-empfiehlt-schutz-vor-hackerangriffen/)) |
| **Trennung Netzsteuerpfad vs. Hersteller-Service-Pfad**; Hersteller-Updates dürfen die Netz-Policy (Grenzen, Vertrauensanker) nicht ändern ohne signierte Freigabe des Policy-Eigners | Hersteller- oder Cloud-Kompromittierung kann Netzbefehle nicht fälschen oder aushebeln | BNetzA-Linie in DE: Steuerdaten über SMGW, Service über 2. WAN ([ZfK](https://www.zfk.de/digitalisierung/smart-city-energy/bsi-sicherheitsbedenken-gegen-pv-wechselrichter-das-sagt-die-branche)) |
| **Secure Boot, signierte Firmware, Secure Element** für Schlüssel | Schutz vor Firmware-Manipulation und Schlüsseldiebstahl | CRA Anhang I (allgemein); TTN/TS005: Hardware-Sicherheitsmodul empfohlen |
| **Offenlegung aller Kommunikationsschnittstellen (HBOM/SBOM)** | Adressiert undokumentierte Funkbauteile | Reuters-Bericht [unbestätigt]; NL: verbotene versteckte Abschaltfunktionen ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al)) |

### B. Im Backend (Netzbetreiber, Lieferant, Aggregator)

| Maßnahme | Wirkung |
|---|---|
| **Signierschlüssel im HSM**, je Rolle und Segment getrennt | Ein kompromittierter Schlüssel wirkt nur auf sein Segment |
| **Segment-Leistungsgrenzen (Blast-Radius-Budget):** max. steuerbare Leistung je Signierschlüssel bzw. Befehl, z. B. je Trafostation/Netzgebiet. Zielgröße: deutlich unter Schwellen mit Systemwirkung (Größenordnung 3 GW laut DNV gilt für Europa; pro VNB-Segment eher MW) | Begrenzt systemische Wirkung auch bei Innentäter oder Backend-Kompromittierung |
| **Mehr-Augen-Freigabe** für Befehle über einer Schwelle (Leistung, Anzahl Segmente) und für Änderungen an Grenzen, Vertrauensankern, Sperrlisten | Schutz gegen Innentäter und Fehlbedienung |
| **Rollen- und Vorrangmodell** Netzbetreiber vor Lieferant (Ampel); Konfliktauflösung im Gerät deterministisch | Verhindert, dass Markt- und Netzbefehle sich hochschaukeln |
| **NIS2-konformes Betriebsumfeld:** Zwei-Faktor-Authentifizierung, keine generischen Passwörter, Logging, Meldeprozess | Grundhygiene, ohnehin Pflicht (NISG 2026) |
| **Unveränderliches Befehls- und Reaktionsprotokoll** (signiert, zeitgestempelt) | Abrechnung, Streitfälle, Forensik, CRA- und NIS2-Meldungen |

### C. Überwachung (Testabrufe + Smart Meter)

| Maßnahme | Wirkung |
|---|---|
| **Unabhängige Verifikation am Smart Meter** (Lastgang am Netzanschlusspunkt) | Erkennt nicht ausgeführte, falsch ausgeführte oder *nicht beauftragte* Leistungsänderungen (z. B. Hersteller-Cloud schaltet ohne Netzbefehl) |
| **Regelmäßige Testabrufe** (kleine, randomisierte Abrufe) → Basislinie je Gerät/Typ für Reaktionszeit, Genauigkeit, Erreichbarkeit | Anomalien fallen auf: plötzliche Verhaltensänderung nach Firmware-Update, ganze Gerätetypen reagieren anders, Geräte reagieren auf Befehle, die nie gesendet wurden |
| **Typ-/Firmware-Cluster-Analyse** | Frühwarnung bei kompromittierten Herstellerflotten. Ein Gerätetyp, der plötzlich abweicht, wird gesperrt bzw. aus der Flex-Planung genommen |
| **Gegenmaßnahme bei Anomalie:** Gerätezertifikat sperren, Typ aus dem Abruf nehmen, Meldung an CSIRT/Hersteller (CRA-Meldekette) | Schließt den Kreis zur Regulierung |

*Grenze:* Smart-Meter-Daten in AT sind meist 15-min-Werte, die Kundenschnittstelle liefert höhere Auflösung. Laut Block 3 ist die Kundenschnittstelle (1–5 s) aber gegenüber dem Kunden nicht manipulationssicher; unabhängig sind nur die Backend-Werte (Folgetag). Echtzeit und Unabhängigkeit gibt es mit heutiger AT-Infrastruktur nicht zugleich (korr. lt. 06).

---

## Minimal-Sicherheitsprofil für unser Interoperabilitätsprofil

Ziel: herstellerunabhängig, kanalunabhängig, und es schadet nicht, wenn ein Teil kompromittiert ist. Formuliert als Anforderungen auf IES-Ebene, ohne technische Detailfestlegung.

| Nr. | Anforderung | Begründung |
|---|---|---|
| S1 | **Geräteidentität:** Jedes steuerbare Gerät bzw. Kommunikationsmodul hat ein eindeutiges, ab Werk eingebrachtes Schlüsselpaar in einem Secure Element/TPM und ein Zertifikat einer anerkannten Hersteller-CA unter einer gemeinsamen Energie-PKI-Wurzel | Vorbilder SMGW-PKI, CSIP-AUS |
| S2 | **Befehlsauthentizität Ende-zu-Ende:** Netz- und Lieferantenbefehle sind asymmetrisch signiert; das Gerät prüft die Signatur selbst. Transportverschlüsselung (LoRaWAN, TLS) ist zusätzlich, nicht stattdessen | Multicast-Gruppenschlüssel, Cloud-Kompromittierungen |
| S3 | **Begrenzte Befehle:** Jeder Befehl trägt Geltungsbereich (Segment/Gruppe), Leistungsgrenze, Dauer, Ablaufzeit und Sequenznummer; abgelaufene oder wiederholte Befehle werden verworfen | Replay- und Ausweitungsschutz |
| S4 | **Lokale Sicherheits-Policy:** Das Gerät setzt harte Grenzen (Leistung, Rampe, Rate, SoC, Anschlussleistung) durch, die weder Netzbefehl noch Hersteller-Cloud allein ändern können | Schutz gegen gültig signierte Fehlbefehle |
| S5 | **Fail-safe und Randomisierung:** definierter Rückfall bei Kanalverlust oder Ablauf; randomisierter Beginn und Rückkehr in einem konfigurierbaren Fenster | UK Reg. 11, Rebound-Schutz |
| S6 | **Pfadtrennung:** Netzsteuerpfad ist logisch getrennt vom Hersteller-Service-Pfad; das Gerät funktioniert für Netzbefehle auch ohne Hersteller-Cloud | BSI- und BNetzA-Linie, Drittstaaten-Debatte |
| S7 | **Backend-Kontrollen:** HSM, Segment-Leistungsbudget je Schlüssel, Mehr-Augen-Freigabe oberhalb einer Schwelle, NIS2-Hygiene | Innentäter, Single Point of Failure |
| S8 | **Unabhängige Verifikation:** Reaktion wird über den Smart Meter gemessen; regelmäßige Testabrufe erzeugen eine Basislinie; Abweichungen lösen Sperr- und Meldeprozesse aus | Betrug und Kompromittierung erkennen |
| S9 | **Lebenszyklus:** Widerruf (Sperrliste/Broadcast), Schlüsselrotation, signierte Updates, Krypto-Agilität; Schwachstellenmanagement und Meldung nach CRA | CRA ab 2026/2027 |
| S10 | **Transparenz:** vollständige Offenlegung der Kommunikationsschnittstellen (HBOM/SBOM); Konformität mit RED DA/EN 18031 bis 12/2027, danach CRA | Undokumentierte Funkbauteile, Marktaufsicht |

**Pitch-Satz:** „Wir vertrauen weder dem Kanal noch der Hersteller-Cloud, sondern nur der Signatur, den Grenzen im Gerät und der Messung am Zähler.“

---

## Offene Fragen an Smart Grids Austria

1. Gibt es in AT eine Initiative für eine **Energie-PKI** (analog SM-PKI des BSI oder NEPKI in Australien)? Wer könnte Root-CA sein (E-Control, Bundesamt für Cybersicherheit, Branchenverband)?
2. Wie bewerten österreichische VNB die **Funkrundsteuerung (EFR)** nach dem 38C3-Vortrag? Gibt es Migrationspläne zu authentifizierten Kanälen?
3. Sind österreichische VNB und Aggregatoren bereits als **NCCS „high/critical-impact“** vorgesehen? Wie werden aggregierte Kleinanlagen dabei gezählt?
4. Soll die Steuerung in AT **über den Smart Meter** laufen (wie DE: SMGW/CLS), oder ist ein **direkter, signierter Kanal zum Gerät** akzeptabel, wenn der Smart Meter nur verifiziert?
5. Welche **Segment-Leistungsgrenzen** wären aus Netzsicht je Befehl bzw. Schlüssel vertretbar (kW/MW je Trafostation, Netzgebiet)?
6. Gibt es eine österreichische Position zur **Drittstaaten-Fernsteuerung** (analog Litauen) oder zum Cybersecurity-Act-Vorschlag?
7. Welche Reaktionszeit ist für die Randomisierung tolerierbar (Sekunden vs. Minuten), ohne den Engpassnutzen zu verlieren?
8. Sind **Testabrufe** mit Kundenvergütung und Datenschutz (DSGVO, ElWG) vereinbar? Wer darf die Messdaten zur Anomalieerkennung auswerten?
9. Sehen die Partner ein Steuermodul als **CRA-„kritisches“ Produkt** (Nähe zu Smart Meter Gateways)? Das hätte Folgen für Zertifizierungsaufwand und Kosten.

---

## Quellenliste

**Regulatorik (Primär/Behörden)**
- EU-Kommission, Cyber Resilience Act: https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act
- EU-Kommission, Radio Equipment Directive (inkl. Aufhebung 2022/30 durch 2026/339): https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en
- EUR-Lex, DelVO (EU) 2024/1366 (NCCS): https://eur-lex.europa.eu/eli/reg_del/2024/1366/oj
- ACER, Cybersecurity Network Code: https://www.acer.europa.eu/electricity/cybersecurity-network-code
- BSI, TR-03109-4 Smart Metering PKI: https://bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Smart-metering/Smart-Meterin-PKI/TechnRichtlinie/tr_03109-4_node.html
- Telesec (im Auftrag BSI), ChangeLog SM-Root-CA: https://www.telesec.de/assets/downloads/Smart-Metering-PKI/ChangeLog_Root.pdf
- UK, Electric Vehicles (Smart Charge Points) Regulations 2021, Reg. 11: https://www.legislation.gov.uk/uksi/2021/1467/regulation/11
- CISA ICSA-25-105-04 Growatt Cloud Applications: https://www.cisa.gov/news-events/ics-advisories/icsa-25-105-04
- DIVD-2024-00011 (Enphase): https://csirt.divd.nl/cases/DIVD-2024-00011/
- DIVD-2025-00015 (SolaX Cloud): https://csirt.divd.nl/cases/DIVD-2025-00015/
- ENTSO-E, Blackout 28.4.2025: https://entsoe.eu/publications/blackout/28-april-2025-iberian-blackout

**Regulatorik (Sekundär)**
- Jones Day, CRA-Meldepflichten: https://www.jonesday.com/en/insights/2026/07/eu-cyber-resilience-act-24hour-reporting-duties-start-september-11-2026
- Springlex, CRA Anhang IV: https://www.springlex.eu/en/packages/cra/cra-regulation/annex-4/
- Springlex, DVO 2025/2392: https://www.springlex.eu/en/packages/cra/tdpc-regulation/annex-2/
- CEN-CENELEC Webinar SMGW (2/2026): https://www.cencenelec.eu/media/CEN-CENELEC/Events/Webinars/2026/2026-02-23_cra-standards-unlocked-cybersecurity-requirements-for-smgw_final.pdf
- TÜV SÜD, EN 18031 im ABl.: https://www.tuvsud.com/en-gb/resource-centre/blogs/uk/testing-and-certification-blog/red-cyber-standards-oj-citation
- Advisera, NIS2 Anhang I: https://advisera.com/nis2/sectors-of-high-criticality/
- KPMG AT, NISG 2026: https://kpmg.com/at/de/insights/2025/12/nisg-2026.html
- Deloitte AT, Infoblatt NISG: https://www.deloitte.com/content/dam/assets-zone2/at/de/docs/studien/2026/infoblatt-nisg.pdf
- WKO, NISG 2026 beschlossen: https://www.wko.at/stmk/information-consulting/unternehmensberatung-buchhaltung-informationstechnologie/nisg-2026-beschlossen-unternehmen-muessen-handeln
- usd AG, NIS2UmsuCG in Kraft: https://www.usd.de/nis2umsucg-offiziell-in-kraft/
- InnoBu, NCCS-Zeitplan: https://www.innobu.com/en/articles/nccs-network-code-cybersecurity-obligations-2026.html
- LRT, Litauen-Gesetz: https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems
- pv magazine, Litauen: https://www.pv-magazine.com/?p=39019
- Euronews, Förderausschluss 4.5.2026: https://www.euronews.com/my-europe/2026/05/04/eu-moves-to-ban-high-risk-inverters-from-china-over-cybersecurity-threats
- pv magazine, Cybersecurity-Act-Revision: https://www.pv-magazine-india.com/2026/01/21/eu-to-ban-chinese-inverters-commission-proposal-in-cybersecurity-mulls-high-risk-vendors-list
- techUK, CSA-Revision: https://www.techuk.org/insights/news/eu-commission-publishes-cybersecurity-act-revision-proposal
- SolarPower Europe, Statement CSA-Revision: https://www.solarpowereurope.org/press-releases/statement-european-commission-publish-draft-revision-of-the-cybersecurity-act
- Solar Magazine NL, Aufsicht Wechselrichter: https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al
- ZfK, BSI-Bedenken: https://www.zfk.de/digitalisierung/smart-city-energy/bsi-sicherheitsbedenken-gegen-pv-wechselrichter-das-sagt-die-branche
- pv magazine DE, 30.12.2025: https://www.pv-magazine.de/2025/12/30/cybersicherheit-von-photovoltaikanlagen-reale-risiken-falsche-loesungen-moegliche-wege/
- aroundhome, BSI-Empfehlung: https://www.aroundhome.de/neuigkeiten/cybersicherheit-fuer-solaranlagen-bsi-empfiehlt-schutz-vor-hackerangriffen/

**Geräteidentität/Protokolle**
- SunSpec Certificate Policy: https://sunspec.org/wp-content/uploads/2025/01/SunSpecCertificatePolicy-V1.0-2019-02-13-1.pdf
- SwitchDin, Interim-PKI CSIP-AUS: https://support.switchdin.com/hc/en-us/articles/48546542623129-What-is-the-purpose-of-our-Public-Key-Infrastructure-PKI-service
- enbility ship-go (EEBus SHIP): https://github.com/enbility/ship-go
- LoRa Alliance TS005 Remote Multicast Setup: https://resources.lora-alliance.org/document/ts005-2-0-0-remote-multicast-setup
- TTN-Folien Multicast/FUOTA-Sicherheit: https://www.thethingsnetwork.org/forum/uploads/default/original/3X/7/a/7af5e0849f922f7ee00a7fd843b7d12e9d0909fa.pdf

**Vorfälle/Studien**
- Soltan, Mittal, Poor: BlackIoT/MadIoT, USENIX Security 2018: https://www.usenix.org/conference/usenixsecurity18/presentation/soltan
- Forescout SUN:DOWN Pressemitteilung: https://www.forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure
- Forescout SUN:DOWN Research: https://www.forescout.com/research-labs/sun-down-a-dark-side-to-solar-energy-grids/
- Forescout Blog (4,5 GW/49 Hz): https://www.forescout.com/blog/grid-security-new-vulnerabilities-in-solar-power-systems-exposed/
- Forescout exponierte Geräte: https://www.forescout.com/blog/the-security-risks-of-internet-exposed-solar-power-systems/
- SolarPower Europe/DNV: https://www.solarpowereurope.org/press-releases/new-report-solar-sector-proposes-solutions-to-mitigate-critical-cybersecurity-risks
- ESMC: https://esmc.solar/restrict-remote-access-of-pv-inverters-from-high-risk-vendors/
- pv magazine, Reuters-Bericht: https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/
- Facilities Dive, Reuters-Bericht: https://www.facilitiesdive.com/news/rogue-communication-devices-found-on-chinese-made-solar-power-inverters/748237/
- SecurityWeek, Bitdefender Solarman/Deye: https://www.securityweek.com/vulnerabilities-exposed-widely-used-solar-power-systems-to-hacking-disruption/
- Dark Reading, Bitdefender: https://www.darkreading.com/ics-ot-security/solar-power-installations-worldwide-open-to-cloud-api-bugs
- heise, Deye-Abschaltungen: https://heise.de/-10183716
- Borncity, Deye: https://borncity.com/win/2024/11/28/deye-deactivates-solar-inverters-in-usa-uk-and-pakistan/
- CCC 38C3 BlinkenCity: https://events.ccc.de/congress/2024/hub/event/blinkencity-radio-controlling-street-lamps-and-power-plants/
- pv magazine, DIVD/Enphase: https://www.pv-magazine.com/?p=38158
- Solar Builder, DERSec-Report: https://solarbuildermag.com/news/report-nearly-50-of-global-solar-power-exposed-to-cyber-exploitation/
- SEIA: https://seia.org/media/16958/
- Gaslicht, RDI-Test: https://www.gaslicht.com/nieuws/omvormers-zonnepanelen-gevoelig-voor-storingen-en-hacks
- Bright, RDI-Test: https://www.bright.nl/nieuws/1136602/omvormer-zonnepanelen-omvormers-zonnepanelen-storing-hacken-veilig.html
