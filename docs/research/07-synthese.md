# 07 – Synthese

Stand: 23.10.2026. Grundlage: 01–05 (nach Einarbeitung der Korrekturen aus 06) und
[anforderungen.md](../anforderungen.md). Zielgruppe: Team für IES-Profil und Pitch.
Nichts hier ist neu recherchiert. Verweise: `01 KA3` = Datei 01, Kernaussage 3; `06 D1` = 06, Detail 1;
`06 W8` = 06, „Weitere Widersprüche“ Nr. 8.

---

## 1. Kernaussagen

| # | Aussage | Verweis |
|---|---|---|
| 1 | **AT hat die Pflicht-Steuerschnittstelle schon, aber nur für Erzeugung und nur am Netzanschlusspunkt.** § 76 ElWG (seit 1.6.2026, ≥ 3,68 kW) plus TOR Typ A V1.4: OpenADR, Sollwert der netzwirksamen Leistung in 1 min, Fallback nur Einspeiserichtung. Ein Lade-/Entlade-Sollwert für Speicher fehlt. Diese Lücke füllt unser Profil. | 01 KA1, 01 § 2.2; 05 KA5; 06 D1 |
| 2 | **Bidirektionale Nutzung gibt es bisher nur als Vertrag oder Tarif, nicht als Geräteprofil.** NL: capaciteitssturingscontract (Gegenrichtung, vergütet). AT: SNE-G-V „systemdienliche Speicher“, aber nur bei Betrieb ausschließlich zur Wiedereinspeisung. DE § 14a: nur Bezug dimmen. | 01 KA3, KA6, KA7; 06 D2 |
| 3 | **Das Hauptproblem in der Praxis ist die Erreichbarkeit, nicht der Markt.** Symphony: 714 von 911 Geräten gesteuert, 26,6 % nicht konforme Intervalle. SAPN: Wechselrichter 89,3 % der Tageslichtzeit erreichbar. AEMO: 70–98 % Telemetrie. Kein Projekt führt eine Zuverlässigkeitsstatistik je Gerätetyp oder Firmware. | 02 KA2, KA3, Befund Testabrufe; 03 KA3 |
| 4 | **Eine Pflicht wirkt schnell, braucht aber vorher ein nationales Profil.** SA: > 95 % der Geräte fähig, flexible Option 36 % → > 85 %. VIC: fünf Netzbetreiber mit eigenem Onboarding führten zu Chaos. Symphony empfiehlt CSIP-AUS als Pflicht. | 05 KA6, Lessons 1–2; 02 KA5 |
| 5 | **Die Geräte sind technisch steuerbar, aber jedes anders.** 12 von 17 Herstellern erlauben lokal Wirkleistungs- und Speicher-Sollwerte, nur Fronius über ein Standardmodell (SunSpec 124). EEBus LPC/LPP und die §14a-Steuerbox können nur begrenzen, nicht entladen. Die lokale Geräteschnittstelle muss mitstandardisiert werden. | 05 KA2, Lesson 7; 03 KA1, KA2 |
| 6 | **Das Sicherheitsrisiko liegt im Aggregat und in den Hersteller-Clouds.** 3 GW gezielt kompromittiert haben laut DNV/SPE erhebliche Netzwirkung. Bitdefender fand Schwachstellen in Solarman (mit Deye ca. 195 GW). Die Funkrundsteuerung ist unauthentifiziert. Daraus folgt: signierte Befehle mit Grenzen, Netzpfad ohne Hersteller-Cloud. | 04 KA1–3, KA7; 06 D8 |
| 7 | **Die Smart-Meter-Verifikation ist erprobt (EDGE), in AT heute aber zweistufig.** Lokal sind 1–5 s möglich, aber gegenüber dem Kunden nicht manipulationssicher. Unabhängig sind nur die 15-min-Backend-Werte, und die kommen am Folgetag. | 02 KA4; 03 KA4; 04 KA8; 06 W8 |
| 8 | **Engpassmanagement braucht Minuten, keine Millisekunden.** Die Trafo-Zeitkonstante liegt bei ca. 180 min, die TOR verlangt 1 min. LoRaWAN-Multicast passt technisch als Zusatzkanal (ca. 560 signierte Befehle/h je Gateway, Signatur ab DR3), weicht aber von der TOR ab (OpenADR, keine Drittsysteme). | 03 KA5–7, Empfehlung; 06 W3, W9 |

---

## 2. Was es schon gibt vs. Lücke, die unser Profil füllt

| Vorbild | Was es leistet | Was fehlt (für Grid-Serving Storage) | Verweis |
|---|---|---|---|
| **AT § 76 ElWG + TOR V1.4 (OpenADR)** | Pflicht-Schnittstelle für neue Erzeugung ≥ 3,68 kW. Sollwert am Netzanschlusspunkt in 1 min, Fallback Einspeisung. „Nachweislich erreichen und umsetzen“ (Abs. 2). AT-OpenADR-Profil bis 31.10.2026 | kein Speicher-Sollwert; Speicher hinter dem Zähler ausdrücklich unberührt (Abs. 3); TOR Fall 1: Speicher speisen nicht zurück; Use Case bidirektional „nicht geklärt“ (Konsultation) | 01 § 2.2, KA1; 05 KA5; 06 D1 |
| **DE § 14a EnWG** | Dimmen des Bezugs auf 4,2 kW, Entlastung über Modul 1–3, SMGW + Steuerbox; Solarspitzengesetz mit Fernsteuertest | nur Bezugsrichtung, kein Entladen; EEBus LPC/LPP nur Begrenzung | 01 § 2.1; 03 Tabelle |
| **NL capaciteitssturingscontract (ACM, 11.12.2025)** | Netznutzung in Gegenrichtung zum Engpass (z. B. Batterie-Rückspeisung), gegen Vergütung | Vertrag, kein Geräteprofil; ob Haushalte erfasst sind, ist offen | 01 KA7, § 2.3; 06 D4 |
| **AU CSIP-AUS (IEEE 2030.5)** | Pflichtprofil mit PKI, dynamischen Exportgrenzen, Fallback (SAPN 1,5 kW je Phase), Compliance-Rating mit Zählerdaten | Standortgrenzen statt Speicher-Sollwert; Cloud-Pfad dominiert; Gerät selbst muss 2030.5 oft nicht sprechen | 03 KA3, Tabelle; 05 Pflichtschnittstellen, Lessons |

**Lücke, die unser Profil füllt:**

| Baustein | Warum neu | Beleg für die Lücke |
|---|---|---|
| **Speicher-Sollwert laden/entladen** (Segmentabruf, zeitlich begrenzt) | Weder TOR, § 14a noch CSIP-AUS sehen ihn vor | 05 KA5; 03 KA2; 01 Bedeutung 6 |
| **Regelmäßige Testabrufe mit Zuverlässigkeitsstatistik je Gerätetyp/Firmware** | Kein Projekt macht das systematisch; Firmware-Updates haben Einstellungen still verändert | 02 Befund Testabrufe, Lesson 3; 05 Lesson 5 |
| **Signierte Befehle mit Grenzen** (Segment, Leistung, Dauer, Ablaufzeit, Sequenznummer) | Es fehlen verbindliche, energiespezifische Anforderungen an einen Steuerbefehl | 04 KA4, S2–S4 |
| **Unabhängige Verifikation am Zähler** als Teil des Profils | In EDGE erprobt, aber nirgends als Profilbestandteil normiert | 02 KA4; 05 Lesson 6 |

Pitch-Formel (01 Bedeutung 1): *„Österreich hat mit § 76 ElWG die Pflicht geschaffen. Wir liefern das
fehlende Stück: den Speicher in beide Richtungen, die unabhängige Verifikation und den Testabruf.“*

---

## 3. Ehrliche Grenzen

- **Verifikation:** In AT gibt es heute Echtzeit und Manipulationssicherheit nicht zugleich. Die Kundenschnittstelle
  kann der Kunde fälschen, weil er den Schlüssel kennt. Die Backend-Werte (15 min) kommen am Folgetag (Wien: einmal täglich).
  Deshalb gilt: Echtzeit nur zur Plausibilisierung, Abrechnung und Statistik nur aus dem Backend (03 KA4; 06 W8).
- **Kanal:** LoRaWAN als Befehlskanal weicht von TOR V1.4 ab (OpenADR über Kundeninternet, „keine Drittsysteme“).
  In AT ist es nur als Zusatzkanal neben OpenADR denkbar. Ein Hersteller-Cloud-Pfad wäre nicht TOR-konform (03 Empfehlung; 06 W3).
- **LoRaWAN-Kapazität:** ca. 560 signierte Befehle/h je Gateway im 10-%-Unterband (eigene Rechnung), Signatur erst ab DR3.
  Multicast hat keine Quittung, die Rückmeldung braucht einen anderen Kanal (03 KA5, KA6).
- **Tarifanreiz:** Die SNE-G-V-Befreiung greift nicht für Eigenverbrauchsspeicher („ausschließlich zur Wiedereinspeisung“,
  § 23, plus Standortkriterien am UW, ≥ 1 MW gebündelt). Für Heimspeicher bleibt die Förderung der Hebel (01 KA3; 06 D2).
- **Rechtsrahmen hinter dem Zähler:** § 76 Abs. 3 lässt den VNB nur die netzwirksame Leistung am Anschlusspunkt vorgeben.
  Der Speicher-Sollwert muss sich deshalb als Vorgabe am Netzanschlusspunkt ausdrücken lassen, die das EMS umsetzt (01 KA2).
- **Rückspeisung:** TOR Fall 1 geht davon aus, dass Speicher nicht zurückspeisen. Der 10-%/min-Gradient beim Wiederhochfahren
  kollidiert mit Speicherabrufen, Kostal sperrt deshalb in AT Sollwert-Register (05 Reaktionszeiten, OF 2–3).
- **Belege für Entladen:** Kein europäisches Projekt mit belastbaren Zahlen zu Heimspeicher-Entladung für einen VNB-Engpass.
  Die Belege kommen aus Australien bzw. vom ÜNB (TenneT/sonnen) (02 KA1).
- **Zuverlässigkeit:** Selbst in Pilotprojekten waren 26,6 % der Intervalle nicht konform. Das Profil muss mit 70–98 %
  Erreichbarkeit planen (Überbuchung, Puffer) (02 KA3, Lesson 6).
- **Bestand:** Alle Pflicht-Vorbilder erfassen nur Neuanlagen (05 „Dagegen“).
- **OpenADR-Version offen:** TOR verweist auf IEC 62746-10-1 (2.0b), Netz OÖ arbeitet mit 3.1 (06 D1).

---

## 4. Bausteine fürs Profil

### 4.1 Akteure

| Akteur | Rolle im Profil | Verweis |
|---|---|---|
| Verteilernetzbetreiber (VNB) | erkennt den Engpass, löst Segmentabruf und Testabruf aus, verifiziert; in AT auch Messstellenbetreiber (Smart Meter) | 01 § 2.2; 03 AT |
| Anlagenbetreiber / Kunde | bestimmt den Normalbetrieb, stimmt zu, erhält Förderung/Vergütung und Abrufprotokoll | Challenge; 02 Lesson 9 |
| Lieferant / Aggregator | vermarktet Flexibilität am Markt; Vorrangregel gegenüber VNB nötig | 01 § 5; § 63 ElWG |
| Hersteller WR/Speicher | stellt die lokale Sollwert-Schnittstelle und das Gerätezertifikat (Hersteller-CA) bereit | 05; 04 S1 |
| Kommunikationsmodul / EMS | prüft die Signatur, setzt die lokale Policy durch, steuert das Gerät, meldet zurück | 04 S2–S6; 05 KA4 |
| PKI-Betreiber | Wurzel der Energie-PKI, Widerruf (Betreiber offen) | 04 OF 1; 03 OF 7 |
| Förderstelle | knüpft die volle Förderung an Schnittstelle und Testabruf-Teilnahme | anforderungen.md § 3 |
| E-Control / Regulator | TOR, Tarife, Anerkennung der Flex- und IKT-Kosten | 01 § 2.2 |
| Flexibilitätsplattform (§ 142 ElWG, ÜNB + VNB) | Koordination von Netz- und Marktabrufen | 01 § 2.2 |

### 4.2 Prozesse

| Prozess | Kern | Anker / Vorbild |
|---|---|---|
| **P1 Registrierung / Onboarding** | Gerätezertifikat, Zählpunkt und Netzsegment binden; Fähigkeiten melden (Pmax laden/entladen, Kapazität, Typ, Firmware); Ende-zu-Ende-Test bei Inbetriebnahme | 04 Lebenszyklus; 02 SAPN-Fail-safe-Test; 05 Lesson 1 |
| **P2 Testabruf** | regelmäßig, klein, randomisiert; Reaktionszeit, Genauigkeit und Erreichbarkeit je Gerät messen und je Typ/Firmware aggregieren; Test auch nach Firmware-Update | § 76 Abs. 2 „nachweislich“; 02 Lesson 3; 04 C |
| **P3 Ereignis-Abruf laden/entladen** | Engpass erkannt → signierter Segmentbefehl (Modus, Sollwert, Start, Dauer, Randomisierung, Ablaufzeit) → Umsetzung ≤ 1 min → gestaffelte Rückkehr; möglichst mit Vorankündigung („Arming“) und SoC-Rückmeldung | 03 Empfehlung; 02 Lessons 4, 10; 01 § 5 |
| **P4 Verifikation** | Stufe 1 lokal (Kundenschnittstelle, Plausibilisierung), Stufe 2 verbindlich (15-min-Backend, Folgetag); Soll-Ist gegen den Befehl statt statistischer Baseline | 03 Verifikation; 02 KA8 |
| **P5 Abrechnung / Förderung** | Vergütung aktiver Abrufe; Nachweis der Testabruf-Teilnahme an die Förderstelle; Anomalie → Gerät oder Typ sperren, Meldung nach CRA; Förderstufen 0–3 mit Auszahlung in Tranchen nach gemessener Netzdienlichkeit; Schadlosstellung des Kunden bei VNB-Eingriffen (Ist minus kontrafaktische Referenz, plus Vergütung) | 01 § 3; 04 C; anforderungen.md; [ems-konzept.md](../ems-konzept.md) §5, §6 |

### 4.3 Schnittstellen

| Nr. | Von → Nach | Zweck | Kandidaten-Standard |
|---|---|---|---|
| I1 | VNB-Backend → Kommunikationsmodul | Abruf- und Testbefehle (signiert) | OpenADR (TOR V1.4; Version offen); IEEE 2030.5/CSIP-Datenmodell als Vorbild; LoRaWAN Class C Multicast (TS005) als Zusatzkanal |
| I2 | Kommunikationsmodul → VNB | Quittung, Ist-Leistung, SoC, Status | OpenADR-Reports bzw. REST über Kundeninternet/LTE-M; LoRaWAN-Uplink nur für kurze Quittungen |
| I3 | Kommunikationsmodul/EMS ↔ WR/Speicher (lokal) | Sollwert laden/entladen, Grenzen, Watchdog | SunSpec Modbus 704/124, S2 (EN 50491-12-2); EEBus LPC/LPP nur für Begrenzung |
| I4 | Smart Meter → Kommunikationsmodul (lokal) | Echtzeit-Plausibilisierung (1–5 s) | Kundenschnittstelle DLMS/COSEM (M-Bus, AES-128) |
| I5 | Smart-Meter-Backend → VNB-Verifikation | verbindliche Erbringungsprüfung, Testabruf-Statistik | 15-min-Lastgang (Folgetag); kein spezieller Standard gefunden |
| I6 | VNB ↔ Lieferant/Aggregator | Vorrang, Vortagesmeldung, Fahrplananpassung | Flexibilitätsplattform § 142 ElWG; Ampellogik (BDEW) |
| I7 | PKI ↔ Modul | Zertifikate, Sperrliste, Rotation | Vorbilder SMGW-PKI (TR-03109-4), CSIP-AUS-PKI |
| I8 | VNB → Förderstelle | Nachweis Schnittstelle und Testabruf-Teilnahme; Jahresnachweis der Netzdienlichkeit für die Förder-Tranchen, gestützt auf die eigene Messung (Modul `MTR`/`MEAS`, siehe [ems-konzept.md](../ems-konzept.md) §5) | kein Standard gefunden **[offen]** |
| I9 | VNB/Modul → Kunde | Abrufprotokoll, Transparenz | App/Portal, kein Standard nötig |

### 4.4 Sicherheitsanforderungen (aus 04, Minimal-Sicherheitsprofil)

| Nr. | Kurz |
|---|---|
| S1 | Geräteidentität: Schlüssel ab Werk im Secure Element, Hersteller-CA unter gemeinsamer Energie-PKI |
| S2 | Befehle Ende-zu-Ende asymmetrisch signiert, das Gerät prüft selbst; Transportverschlüsselung nur zusätzlich |
| S3 | Befehl mit Geltungsbereich, Leistungsgrenze, Dauer, Ablaufzeit, Sequenznummer |
| S4 | Lokale Policy (Leistung, Rampe, Rate, SoC, Anschlussleistung), weder per Netzbefehl noch per Cloud allein änderbar |
| S5 | Fail-safe bei Kanalverlust bzw. Ablauf; randomisierter Start und randomisierte Rückkehr |
| S6 | Netzsteuerpfad getrennt vom Hersteller-Service-Pfad, funktioniert ohne Cloud |
| S7 | Backend: HSM, Leistungsbudget je Schlüssel/Segment, Mehr-Augen-Freigabe, NIS2-Hygiene |
| S8 | Unabhängige Verifikation + Testabruf-Basislinie, Sperr- und Meldeprozess |
| S9 | Lebenszyklus: Widerruf, Rotation, signierte Updates, Krypto-Agilität, CRA-Meldungen |
| S10 | Offenlegung der Kommunikationsschnittstellen (HBOM/SBOM); RED DA/EN 18031 bis 12/2027, danach CRA |

Pitch-Satz (04): *„Wir vertrauen weder dem Kanal noch der Hersteller-Cloud, sondern nur der Signatur, den Grenzen im
Gerät und der Messung am Zähler.“*

---

## 5. Finanzierung

| Baustein | Inhalt / Zahl | Status | Verweis |
|---|---|---|---|
| **Förderbedingung (Team-Entscheidung [E])** | Volle Förderung für PV/Speicher nur mit standardisierter Steuerschnittstelle und Teilnahme an Testabrufen, sonst Teilförderung. **Speicher: volle Förderung nur bei Ansteuerbarkeit in beide Richtungen (laden und entladen) über die Schnittstelle plus Testabrufe.** Verlangt wird die Fähigkeit, keine Entladepflicht | Konzept; Höhe und Förderinstrument offen (EAG-Investitionszuschuss als Hebel **[unbestätigt]**) | anforderungen.md § 3 |
| Kosten des Netzbetreibers für Flex und IKT | sind in den Netzentgelten anzuerkennen (Art. 32 Abs. 2 RL 2019/944; § 139 Abs. 4 ElWG) | geltendes Recht | 01 KA4, § 4 |
| Kosten der Steuereinrichtung | trägt in AT der Anlagenbetreiber (§ 76 Abs. 1) | geltendes Recht | 01 § 2.2 |
| VNB-Anreiz zur Ansteuerbarkeit | Pönale 100 € je Verzugsjahr, kostenmindernd (§ 76 Abs. 2) | geltendes Recht | 01 § 4 |
| Systemdienliche Speicher (SNE-G-V §§ 23–26) | Befreiung von Netznutzungs- und Netzverlustentgelt; ≥ 10 kW bündelbar zu ≥ 1 MW; Deckel 5 GW; ab 1.1.2027; **nicht für Eigenverbrauchsspeicher** | kundgemacht 12.10.2026 | 01 § 2.2; 06 D2 |
| Flexible Entnahme (SNE-G-V § 10) | ≥ 4 kW bis 100 % einschränkbar, 2 × 2 h/Tag; eigener Leistungspreis (Höhe offen); Pflichtangebot spätestens ab 1.10.2027 | kundgemacht, Tarifhöhe offen | 01 § 2.2 |
| Unterbrechbare Leistung (§ 128 Abs. 3–4 ElWG) | Abschlag für unterbrechbar/regelbar vereinbarte Leistung | geltendes Recht, Höhe n. v. | 01 § 2.2 |
| Vergütung aktiver Abrufe (Entladen freiwillig) | Vergleichswerte: IT EDGE Abruf ≤ 200 €/MWh; IT UVAM bis ca. 30 000 €/MW/a (2019); NL Gegenrichtung „tegen een vergoeding“ | Vorbilder | 01 § 3 |
| Vergleich DE § 14a | Modul 1: 110–190 €/a (Stand 2023); Modul 2: Arbeitspreis auf 40 % | geltendes Recht DE | 01 KA6; 06 D3 |
| Argument „Flex statt Kupfer“ | BMWi: 3 % Abregelung der Wind/PV-Jahresenergie (in Netzen mit Ausbaubedarf) → > 40 % weniger Netzausbau. DNV/smartEn: 11,1–29,1 Mrd. €/a vermiedene EU-Verteilnetzinvestitionen 2030. AT: 44,4 Mrd. € Verteilnetz bis 2040 (Sekundärzitat AIT) | Studien | 01 KA8, § 6; 06 D5 |

Schluss für den Pitch: Für PV-Heimspeicher hinter dem Zähler gibt es in AT keinen passenden Tarifanreiz (SNE-G-V greift
nicht). Deshalb ist die **Förderbedingung** der wichtigste Hebel. Aktives Entladen bleibt freiwillig und wird vergütet
(01 Bedeutung 7).

---

## 6. Die 10 stärksten Zahlen für den Pitch

| # | Zahl | Aussage | Quelle |
|---|---|---|---|
| 1 | **1.6.2026 / 3,68 kW** | Seit 1.6.2026 brauchen neue Erzeugungsanlagen ab 3,68 kW in AT eine Steuereinrichtung mit standardisierter Schnittstelle (06: bestätigt) | https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2025_I_91/BGBLA_2025_I_91.pdf |
| 2 | **1 min / 31.10.2026** | TOR V1.4: Sollwert am Netzanschlusspunkt in 1 min über OpenADR; AT-Profil bis 31.10.2026 zu spezifizieren (06: bestätigt) | https://www.e-control.at/documents/1785851/1811582/TOR+Stromerzeugungsanlagen+Typ+A+Version+1.4+(7).pdf/093752f5-e220-0731-b8a8-bfa85ccb7287?t=1780897058735 |
| 3 | **3 % → > 40 %** | 3 % Abregelung der Wind/PV-Jahresenergie in Netzen mit Ausbaubedarf sparen über 40 % Netzausbau (06: bestätigt) | https://www.offis.de/fileadmin/content/files/download_tools/roadmaps_und_studien/BMWi_Verteilernetzstudie.pdf |
| 4 | **11,1–29,1 Mrd. €/a** | vermiedene EU-Verteilnetzinvestitionen durch Demand-side-Flex 2030 (Studie, gesponsert; 01) | https://www.dnv.com/publications/demand-side-flexibility-quantification-of-benefits-in-the-eu-232342 |
| 5 | **26,6 %** | nicht konforme 5-min-Intervalle bei 8 Netzdienst-Abrufen in Symphony (06: bestätigt) | https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf |
| 6 | **714 von 911; 32 Modelle / 7 Hersteller** | Nur 714 von 911 Geräten waren tatsächlich steuerbar (Bericht nennt auch 715); 32 WR-Modelle von 7 Herstellern brauchten Gateway und Patches (06: bestätigt) | https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf |
| 7 | **89,3 %** | Wechselrichter über das Kundeninternet nur 89,3 % der Tageslichtzeit erreichbar (SAPN Flexible Exports; 06: bestätigt) | https://arena.gov.au/assets/2024/01/SA-Power-Networks-Flexible-Exports-for-Solar-PV-Trial-Final-Report.pdf |
| 8 | **> 95 %; 36 % → > 85 %** | Nach der Pflicht in SA sind über 95 % der Geräte (Marktanteil) fähig; die flexible Option stieg von 36 % auf über 85 % (06: bestätigt) | https://arena.gov.au/assets/2024/01/SA-Power-Networks-Flexible-Exports-for-Solar-PV-Trial-Final-Report.pdf |
| 9 | **3 GW** | Eine gezielte Kompromittierung von 3 GW hat „significant implications“ für das europäische Netz; über ein Dutzend Hersteller steuern deutlich mehr (06: bestätigt) | https://www.solarpowereurope.org/press-releases/new-report-solar-sector-proposes-solutions-to-mitigate-critical-cybersecurity-risks |
| 10 | **195 GW (~20 %)** | Solarman- und Deye-Plattformen zusammen, ca. 20 % der weltweiten Solarerzeugung; Bitdefender fand Schwachstellen (kein Einbruch) (06: bestätigt) | https://www.securityweek.com/vulnerabilities-exposed-widely-used-solar-power-systems-to-hacking-disruption/ |

Achtung im Pitch: SAPN 1,5 kW (Flexible Exports, je Phase) und 5 kW (Advanced VPP mit Tesla) sind zwei Projekte.
99,97 % (Grenze eingehalten, Gerätemonitoring) und 99,4 % (Zeitanteil 10-kW-Export) messen Verschiedenes (06 W6, W7).

---

## 7. Offene Fragen an Smart Grids Austria (konsolidiert)

1. **OpenADR-AT-Profil:** Wie weit ist es (Frist 31.10.2026 an die E-Control, Veröffentlichung bis 31.12.2026)? Enthält
   es einen Use Case für Speicher in beiden Richtungen? Kann unser Profil dafür als Vorschlag dienen? (01 OF 1; 01 Bedeutung 6)
2. **OpenADR 2.0b oder 3.1?** Die TOR verweist auf IEC 62746-10-1 (2.0b, X.509/TLS 1.2), Netz OÖ arbeitet mit 3.1 (OAuth2/TLS).
   Welche Version und welches Sicherheitsmodell gelten? (06 D1; 03 OF 9)
3. **Speicher-Sollwert und Rückspeisung:** Wird § 76 bzw. die TOR auf Speicher mit Lade-/Entlade-Sollwert ausgeweitet?
   Ist netzdienliches Entladen trotz TOR Fall 1 zulässig, und wie wird es bilanziell behandelt? (01 OF 2; 02 OF 2; 03 OF 8; 05 OF 3)
4. **Nachweis der Ansteuerbarkeit (§ 76 Abs. 2):** Gibt es ein Konzept für regelmäßige Testabrufe? Wie oft sind sie
   zumutbar, wer zahlt, und wie verhalten sie sich zu Datenschutz und Vergütung? (01 OF 3; 02 OF 6; 04 OF 8)
5. **Messdaten für die Verifikation:** Dürfen VNB die 15-min-Backend-Werte für Verifikation und Testabruf-Statistik nutzen,
   und wie schnell liegen sie vor? Ist eine bidirektionale oder manipulationssichere Kundenschnittstelle geplant? (02 OF 3; 03 OF 1, 6; 05 OF 9)
6. **Kanal:** Ist ein zusätzlicher Kanal neben OpenADR (LoRaWAN, 450 MHz) trotz „keine Drittsysteme“ akzeptabel? Wie geht es
   mit Rundsteuerung und Funkrundsteuerung (EFR) weiter? (03 OF 2–3; 04 OF 2, 4; 06 W3)
7. **Reaktionszeit, Toleranz, Segmente:** Reicht 1 min? Welche Compliance-Toleranz und Segmentgröße (Trafo, Abgang) sind
   sinnvoll? Welches Leistungsbudget je Schlüssel ist vertretbar? Wie gilt der 10-%/min-Gradient für Speicherabrufe? (01 OF 8; 02 OF 4–5; 03 OF 4–5; 04 OF 5, 7; 05 OF 2, 4)
8. **Energie-PKI:** Wer betreibt die Wurzel für signierte Befehle (E-Control, Bundesamt für Cybersicherheit, Branche)?
   Gilt das Steuermodul als CRA-„kritisches“ Produkt? (03 OF 7; 04 OF 1, 9)
9. **Vorrang Netz vs. Markt:** Wie werden VNB-Vorgaben (Vortag 6/9 Uhr) und Aggregator-Vermarktung koordiniert (Ampel)?
   Sind Kleinspeicher auf der Flexibilitätsplattform § 142 vorgesehen? (01 OF 6–7; 02 OF 8)
10. **Tarifanreiz für Heimspeicher:** Ist eine Kategorie für netzdienliche Heimspeicher hinter dem Zähler denkbar, da
    § 23 SNE-G-V nicht greift? Welche Höhe hat der Leistungspreis für flexible Entnahme? (01 OF 4–5; 06 D2)

## 8. Eigene Demo-Befunde (Simulation, keine Feldmessung)

- **Unkoordiniertes Laden erzeugt den Engpass selbst:** Im SimBench-Test
  (SimBench 1.6.3, pandapower, Szenario 2 mit hochskalierter Durchdringung) steigt die
  Leitungsauslastung von **34 % auf 90 %**, wenn alle Speicher gleichzeitig mit
  voller Leistung laden. Das stützt dosierte Vorgaben je Netzsegment statt
  gleicher Befehle an alle (vgl. Gruppenstaffelung S5 in [ems-konzept.md](../ems-konzept.md)).
  Quelle: eigene Simulation, Session infra-kg-austria-51, 23.10.2026.
- SimBench-Netze sind bei der gelieferten Durchdringung nicht überlastet; Engpässe
  entstehen in der Demo erst durch hochskalierte Durchdringung. V2G ist in SimBench
  nicht enthalten und wird gemockt.
