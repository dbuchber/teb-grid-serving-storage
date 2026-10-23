# 05 – Gerätebestand & Schnittstellen

Stand: 23.10.2026 · Block 5 des Rechercheplans (`00-rechercheplan.md`)

**Belegstufen in diesem Dokument**

- **[H]**: Herstellerdokument (Datenblatt, Handbuch, Schnittstellenbeschreibung) oder Regulierer-/Normtext, selbst eingesehen.
- **[S]**: Sekundärquelle. Das ist meist die Open-Source-Implementierung *evcc*: Ihre Gerätetemplates zeigen, welche Register in der Praxis für die Speichersteuerung beschrieben werden (Stand Commit `fab6fad`, 23.10.2026). Dazu kommen Integrator-Dokus (TapHome, Eniris, Reduxi, openHAB), Fachpresse und Foren.
- **[unbestätigt]**: Die Aussage stammt nur aus Snippets oder Foren, oder sie war nicht im Original prüfbar.

---

## Kernaussagen

1. **Der Markt ist asiatisch dominiert und zersplittert.** Bei Heimspeichern in DE lag 2025 BYD mit ca. 16,5 % vorn, dahinter Sungrow (9,0 %) und Huawei (7,8 %). Die Top 5 kommen zusammen nur noch auf knapp über 45 % [Q1]. EU-weit stellen BYD und Huawei laut EUPD 2025 zusammen mehr als 30 % der Nachfrage im Heimsegment [Q3]. Bei Wechselrichtern lieferten Huawei und Sungrow 2024 zusammen 55 % der weltweiten Leistung [Q4]. Eine Pflichtschnittstelle muss deshalb chinesische *und* europäische Hersteller erfassen. Ein nationaler Alleingang mit einer Steuerbox erreicht nur den Neubestand.
2. **Technisch lässt sich fast jeder aktuelle Hybrid-Wechselrichter von außen steuern, aber jeder anders.** Lokal per Modbus TCP/RTU lassen sich bei SMA, Fronius, Huawei, SolarEdge, Sungrow, GoodWe, Kostal, SolaX, Deye, Victron und Fox ESS sowohl die Wirkleistung als auch die Lade- und Entladeleistung des Speichers beeinflussen [H/S, Tabelle]. Nur Fronius nutzt dafür ein *Standard*-Modell (SunSpec 124) [Q10]. Alle anderen verwenden proprietäre Register und eine eigene Semantik:
   - absolute Sollwerte: Kostal, SMA, Victron
   - Prozentfenster: Fronius
   - Modus plus Kommando: Sungrow 0xAA/0xBB, Huawei „forcible charge“ mit Dauer
   - Umweg über Zeitplan/TOU-Slots: Growatt, Deye
3. **Watchdogs und Fallbacks sind uneinheitlich.** Fronius hat einen Reversion-Timer von 0–28 800 s, der bei 0 dauerhaft gilt [Q10]. Kostal fällt nach 30–10 800 s auf Fallback-Limits zurück [Q11]. Victron muss alle 60 s neu beschrieben werden, sonst geht das Gerät in Passthru [Q14]. Bei SMA und SolarEdge baut evcc einen eigenen Software-Watchdog [S]. Ein sicheres Rückfallverhalten ist heute **kein** gemeinsames Merkmal der Geräte, ein Pflichtprofil müsste es vorschreiben. In AT schreibt TOR Typ A V1.4 (Kap. 5.4.1.2) einen Fallback bereits vor, allerdings nur für die netzwirksame Leistung am Netzanschlusspunkt und nur in Einspeiserichtung (vertraglicher Wert bzw. 70 % kWp bei PV) (korr. lt. 06).
4. **Die lokale Modbus-Schnittstelle taugt nicht direkt als Netzbetreiber-Schnittstelle.** Sie ist ab Werk meist deaktiviert und muss vom Installateur freigeschaltet werden. Fronius nennt Modbus TCP selbst eine „ungesicherte Schnittstelle“ [Q12]. SolarEdge erlaubt nur einen Modbus-Client gleichzeitig [S, Q8]. Für das Team-Konzept heißt das: Nötig ist ein Kommunikationsmodul mit Signaturprüfung als Sicherheitsgrenze, darunter eine standardisierte lokale Geräteschnittstelle.
5. **Verpflichtend sind heute ein Kontakteingang und in AT zusätzlich ein OpenADR-Sollwert am Netzanschlusspunkt, aber kein Speicher-Sollwert.** TOR Erzeuger Typ A V1.4 (gültig ab 01.06.2026; Umsetzung der RfG 2016/631) verlangt in Kap. 5.4.1.1 einen „Eingangsport“, über den die Wirkleistungsabgabe innerhalb von **5 s** beendet werden kann; potentialfreie Kontakte am Rundsteuerempfänger oder Gateway nur, **falls im Netzanschlussvertrag vorgesehen** (Kap. 6.2.1, S. 40). Neu in V1.4 ist Kap. 5.4.1.2: standardisierte digitale Schnittstelle (**OpenADR**, keine Drittsysteme), Sollwert der netzwirksamen Leistung am Netzanschlusspunkt **in 1 min**, Fallback nur in Einspeiserichtung (korr. lt. 06) [Q20]. DE verlangt vier Stufen per Rundsteuerempfänger [Q22] bzw. die FNN-Steuerbox mit EEBUS LPC/LPP oder Relais [Q23]. **Keine** dieser Vorgaben sieht einen Lade- oder Entladesollwert für Speicher vor. Die TOR Typ A geht in Fall 1 (auch in V1.4, S. 38) sogar davon aus, dass Speicher „nicht ins Netz rückspeisen“ [Q20] (korr. lt. 06).
6. **Australien zeigt, dass eine Pflicht wirkt.** Nach der SA-Regulierung waren über 95 % der Geräte (nach Marktanteil) Flexible-Exports-fähig. Die Wahl der flexiblen Option stieg von 36 % auf über 85 % [Q30]. Australien zeigt aber auch die Kosten:
   - Cloud-Betriebskosten bei den Herstellern
   - Abhängigkeit vom Internet (Fallback 1,5 kW je Phase (korr. lt. 06))
   - Onboarding-Chaos bei fünf Netzbetreibern in VIC
   - anfängliche Compliance-Quote von nur 16,5 % der Solarhändler über 90 % [Q30][Q33]

   Kalifornien hat IEEE 2030.5 zum Default gemacht. Die Pflicht ist aber über Aggregator- und Gateway-Pfade erfüllbar, das Gerät selbst muss 2030.5 nicht sprechen [Q36].
7. **Auf EU-Ebene ist das Fenster offen.** Der Entwurf der RfG 2.0 (Delegierte Verordnung, 08.07.2026) bezieht Speicher ein. Die Konsultation endete am 25.08.2026 mit 117 Stellungnahmen, die Annahme ist für Q4 2026 geplant. Für die V2G-Datenschnittstelle wird **kein** Protokoll benannt [Q40][Q41][Q42]. Ecodesign für „PV-Module, Wechselrichter und Systeme“ steht im Arbeitsplan 2025–2030 als „act in preparation“ [Q43]. Beide Instrumente wären Vehikel für eine Pflichtschnittstelle, keines enthält sie bisher [unbestätigt für RfG-Annex-Details].

---

## Marktanteile

| Segment / Region | Jahr | Hersteller-Anteile | Methode | Quelle |
|---|---|---|---|---|
| Heimspeicher DE (nach Kapazität) | 2025 | BYD ~16,5 %, Sungrow ~9,0 %, Huawei ~7,8 %, Anker 6,9 %, Fox ESS 5,4 %, E3/DC 4,3 %, sonnen 3,3 %. Top 5 knapp > 45 % (2024: knapp 55 %) | MaStR, Auswertung P3/ISEA RWTH (Battery Charts); nicht zuordenbare Einheiten anteilig verteilt | [Q1] |
| Heimspeicher DE | 2024 | BYD 21,6 %, Huawei 12,4 %, Sungrow 11,5 %, LG 3,4 %, Growatt 2,3 % (asiatische Top 5: 51,2 %); sonnen 4,7 %, E3/DC 4,3 %, Fenecon 2,8 %, Varta 1,3 %, Senec 1,2 % (deutsche Top 5: 14,3 %) | wie oben, Datenstand 01.04.2025 | [Q2] |
| Heimspeicher Europa | 2025 | BYD + Huawei zusammen > 30 % der Nachfrage. Sungrow und Fox ESS „führende Marken“. H1 2026: Fox ESS, Huawei, BYD, Sigenergy größte Anteile (ohne Zahlen) | EUPD-Schätzung (Lieferdaten, Hersteller, Installateure) | [Q3] |
| Speichermarkt Europa gesamt | 2025/26 | 32 GWh (2025), Prognose 57 GWh (2026). Heimsegment ~11 → 15 GWh. Größte Heimmärkte DE > IT > NL > UK > AT | EUPD | [Q3] |
| Speichermarkt EU, Segmente | 2024 | Heimspeicher ~50 % der Kapazität trotz −11 % Nachfrage; DE, IT, UK > 2/3 der Nachfrage. Top-4-Heimmärkte 2025: DE, IT, UK, AT | SolarPower Europe | [Q5] |
| Wechselrichter global (alle Segmente) | 2024 | 589 GWac Lieferungen. Huawei + Sungrow = 55 %, dahinter Ginlong Solis, Growatt, Sineng. Europa: Lieferungen „sharp double-digit“ rückläufig (Lager NL/DE) | Wood Mackenzie | [Q4] |
| Wechselrichter-Ranking global | H1 2025 | 1 Huawei, 2 Sungrow, 3 SMA, 4 Fronius, 5 Solis, 6 GoodWe, 7 TMEIC/SolarEdge, 9 Solplanet, 10 Enphase. Top 10 = 71 % Marktanteil. **Achtung:** Score aus 8 Kriterien, kein reiner Mengenanteil | Wood Mackenzie | [Q6] |

**Lücke:** Frei zugängliche **herstellerscharfe Wechselrichter-Anteile für den europäischen Residential-Markt** (DE/AT/IT/NL/ES/FR) habe ich nicht gefunden. Wood Mackenzie und S&P stehen hinter der Paywall. Das MaStR erfasst bei PV-Einheiten nach meinem Kenntnisstand keinen Wechselrichter-Hersteller **[unbestätigt]**. Als Annäherung dienen die Heimspeicher-Anteile, weil der Hybrid-WR meist vom selben Hersteller stammt (Huawei, Sungrow, Fox ESS, E3/DC, sonnen). Bei BYD trifft das nicht zu: BYD liefert nur die DC-Batterie, gesteuert wird über den Fremd-WR (Fronius, GoodWe, Kostal u. a.) [Q19].

---

## Hersteller-Schnittstellen-Tabelle

Legende: **L** = lokal steuerbar (Modbus/REST im LAN), **C** = nur über Hersteller-Cloud, **K** = nur Kontakt-/Stufeneingang, **–** = nicht gefunden.

| Hersteller | Modell (aktuell) | Schnittstellen | SunSpec | EEBUS / IEEE 2030.5 | Digitaler Eingang / RSE | Wirkleistung steuerbar | Speicher-Sollwert steuerbar | Fallback / Watchdog | Quellen |
|---|---|---|---|---|---|---|---|---|---|
| **SMA** | Sunny Boy Smart Energy (SBSE), Sunny Tripower Smart Energy (STP SE), Tripower X / Storage X | Modbus TCP (SMA-Profil + SunSpec-Profil), Speedwire | ja, SunSpec-Modbus-Profil [H] | EEBUS über Sunny Home Manager 2.0 ↔ §14a-Steuerbox (ab FW 2.16.4.R) [H]; Data Manager M: EEBUS (1 Gerät) [S] | I/O-Modul / Relais an SHM; DRM0 (AU) bei STP 110-60 [H] | **L** (SMA-Modbus) | **L**, proprietäre BMS-Register (`CmpBMS.OpMod` 40236, `BatChaMaxW` 40795, `BatDschMaxW` 40799, `GridWSpt` 40801) [S] | kein dokumentierter Geräte-Timeout gefunden; evcc mit Software-Watchdog [S] | [Q7][Q24][Q25][S-sma] |
| **Fronius** | Primo/Symo GEN24 Plus, Verto | Modbus TCP (Port 502/1502), Modbus RTU, LAN/WLAN, Solar API | **ja, schreibbar**: Model 123 (WMaxLimPct, Conn, PF, VAr), **Model 124 Basic Storage Control** (InWRte/OutWRte, StorCtl_Mod, MinRsvPct, ChaGriSet). 7xx-Modelle nur Primo GEN24 208–240 (US) [H] | IEEE 2030.5/CSIP-AUS über **Cloud**-Integration (AU) [H, Q30]; EEBUS im Handbuch nicht erwähnt | I/O-Klemmen (DRM-Belegung), „I/O-Leistungsmanagement“ mit 1–4 Relais, RSE mit mehreren WR [H] | **L** (SunSpec 123) | **L** (SunSpec 124, Prozent von WChaMax) | `RvrtTms` 0–28 800 s, Timer bei jeder Modbus-Nachricht neu; 0 = kein Fallback [H] | [Q10][Q12][Q13] |
| **Huawei** | SUN2000-5…12K-MAP0 + LUNA2000-S0/S1; EMMA | RS485; WLAN/FE bzw. 4G über Smart Dongle; Modbus TCP über Dongle (Installateur-Freigabe, IP-Whitelist möglich) [H/S] | – (proprietäre „Modbus Interface Definitions“) | – (nicht gefunden) | **„Ripple receiver control: Yes“** [H] | **L** (evcc: „curtail“, „dim“) [S] | **L**: Max. Lade-/Entladeleistung 47075/47077, „forcible charge“ 47247 + Dauer 47083 [S]; Huawei-Doku nennt 47100/47246/47247 [S] | Zwangsladung mit Dauer = implizites Timeout [S] | [Q15][Q16][S-hua] |
| **SolarEdge** | Home Hub (einphasig/dreiphasig) + Home Battery | Modbus TCP (ab Werk aus, **nur 1 Modbus-Leader**), RS485 | SunSpec nur für **Monitoring** („SunSpec Logging“) [H, Titel] | CSIP-AUS: SolarEdge-Software als erste für Flexible Exports zugelassen [S, Titel, Q9b] | **RRCR am PRI-Stecker**, 4 Relais, Standard 0/30/60/100 %, bis 16 Zustände [H via Snippet] | **L** (Power-Control-Register) | **L**, proprietär: `StorageConf_CtrlMode` 0xE004 = 4 „Remote“, `StorageRemoteCtrl_CommandMode` 0xE00D, Lade-/Entladelimit 0xE00E/0xE010 [S] | evcc-Watchdog [S]; Herstellerdoku „Power Control Protocol“ nur über Support [S] | [Q8][Q9][S-se] |
| **Sungrow** | SH5.0–10RT (-V112) | WLAN/LAN über WiNet-S, RS485, CAN, **4 × DI**, 1 × DO; Modbus TCP über WiNet-S mit Whitelist [S] | – (eigenes „Communication Protocol of Residential Hybrid Inverter“ V1.0.23/V1.1.15) | CSIP-AUS über **iSolarCloud-API** (SAPN) [S, Q18b] **[unbestätigt]** | „Contact ripple control receiver: yes“ [S, Händlerdatenblatt] | **L** | **L**: EMS-Modus 13049 (0 Eigenverbrauch / 2 Zwang / 3 extern), Kommando 13050 (0xAA laden / 0xBB entladen / 0xCC stop), Leistung 33046/33047 [S]. Foren berichten Rücksprung des Modus nach ~10 s [unbestätigt] | – | [Q17][Q18][S-sun] |
| **GoodWe** | ET Plus+ / ET G2 | Modbus RTU über RS485-EMS-Port (ohne Zusatzhardware); Modbus TCP nur mit LAN-Modul (Port 502, ID 247) [S] | – | – | DI1 „Remote Shutdown / NS Protection“ (ET G2) [H]; DRED-Anschluss (andere Serien) [S] | **L** (evcc: „curtail“) [S] | **L**: `EMSPowerMode` 47511, `EMSPowerSet` 47512 [S] | – | [Q26][Q27][S-gw] |
| **Growatt** | MOD/MIN TL-XH (Hybrid) | Modbus RTU/TCP (Datalogger) | – | – | – (nicht geprüft) | – (nicht geprüft) | **nur indirekt**: „Battery first“ + „AC charge“ über **ersten Zeitslot**, einmalige Freischaltung der Register 1100–1102 nötig [S] | – | [S-grw] |
| **Enphase** | IQ8 + IQ Battery 5P, IQ Gateway | IQ Gateway: lokale API (Token, 1 Jahr gültig) [H/S]; Modbus nur „curtail“ [S] | SunSpec Modbus „under development“ (undatiert) [S] | **IEEE 2030.5/CSIP zertifiziert (CS-000096), Gateway als Client** [S] | – | **L** (Modbus, evcc „curtail“) [S] | **C** / – (evcc ohne lokale Batteriesteuerung) **[unbestätigt]** | – | [Q28][S-enp] |
| **Kostal** | PLENTICORE G3 / PLENTICORE BI G3 / MP G3 | Modbus TCP (Port 1502, Unit-ID 71) + SunSpec | Modelle 1, 103, 113, 120, **123 (Immediate Controls)**, 160, 802 (Battery Base). **Speicher-Sollwert nicht über SunSpec** [H] | – (Forenhinweis EEBUS [unbestätigt]) | „Externes Batteriemanagement via digital I/O“ als Modus; RSE + PT1-Einschwingzeit konfigurierbar [H] | **L** (SunSpec 123, RSE) | **L**, proprietär: Lade-/Entlade-Sollwert AC/DC absolut/relativ (1026–1036), Limits 1038/1040, SoC-Grenzen [H] | **ja**: Fallback-Limits 1284/1286 nach 30–10 800 s (Reg. 1288); Register müssen zyklisch geschrieben werden [H] | [Q11][Q29] |
| **SolaX** | X1/X3-Hybrid G4 | Modbus TCP über WiFi/LAN-3.0-Dongle (Port 502, ID 1), RTU (Baudrate je nach Quelle 9600/19200/115200) [S] | – | – | – (nicht geprüft) | – (nicht geprüft) | **L**: `SolarChargeUseMode` 0x1F = 3 manuell, „Manual mode“ 0x20 laden/entladen [S] | – | [S-sx] |
| **Deye** | SUN-…-SG04LP3 / SG01HP3 (3-phasig) | Modbus RTU (RS485), meist mit Solarman-Logger [unbestätigt] | – | – | – | **L** (evcc „curtail“) [S] | **indirekt**: über TOU-Programm-SoC (166–168) und Netzladestrom in A [S] | – | [S-dey] |
| **Fox ESS** | H3 / H3 Smart | Modbus | – | – | – | – | **L** (evcc „battery-control“) [S] | – | [S-fox] |
| **BYD** | Battery-Box Premium HVS/HVM | nur Batterie-BMS ↔ Wechselrichter | – | – | – | – (über WR) | **nur über den kompatiblen WR** (Fronius, GoodWe, Kostal, SMA u. a.) [H] | über WR | [Q19] |
| **Tesla** | Powerwall 3 | Keine lokale REST-API wie bei PW2. TEDAPI/LAN-Zugang nur inoffiziell [S] | – | – | – | – | **C**: kostenpflichtige Fleet API (Backup-Reserve, Betriebsmodus, Netzladen/-export), **kein W-Sollwert** [S] | – | [S-tes] |
| **sonnen** | sonnenBatterie 10 / eco | lokale REST-API v2 mit Token („Write-API“ in der Weboberfläche aktivieren) [S] | – | – | – | – | **L**: `/api/v2/setpoint/charge/{W}` und `/discharge/{W}` (Manual-Modus) [S] | – | [S-son] |
| **E3/DC** | S10 E / S10 X | Modbus TCP (vorwiegend lesend), **RSCP** (proprietär, lokal) [S] | – | – | – | **[unbestätigt]** | **L über RSCP** (überschreibt Smart-Power-Einstellungen) [S] | – | [S-e3] |
| **Victron** | MultiPlus-II + GX (Venus OS) | Modbus TCP (offen dokumentierte Registerliste), MQTT lokal/Cloud | – | EEBUS LPP „noch nicht“ (Forum) [unbestätigt] | – | **L** | **L**: ESS Mode 2 Netzsollwert (Reg. 2716, Unit 100); Mode 3 AC-Sollwert je Phase (Reg. 37/40/41) [H] | **ja**: Mode 3 muss alle 60 s geschrieben werden, sonst Passthru [H] | [Q14] |

**Auswertung:**

- **Wirkleistung UND Speicher-Sollwert lokal setzbar:** SMA, Fronius, Huawei, SolarEdge, Sungrow, GoodWe, Kostal, SolaX, Victron, sonnen, E3/DC, Fox ESS (12 von 17). Belegt ist das aber meist nur durch **eine** Open-Source-Implementierung [S], nicht durch frei verfügbare Herstellerdoku. Frei verfügbar und vollständig dokumentiert sind nur Fronius, Kostal und Victron [H].
- **Nur indirekt steuerbar:** Growatt und Deye, über Zeitplan- bzw. TOU-Umwege. Ein netzdienlicher Abruf in Echtzeit ist damit schwierig.
- **Nur über die Cloud:** Tesla Powerwall 3; Enphase vermutlich ebenfalls **[unbestätigt]**.
- **Standardisiert:** Nur SunSpec 123 (Wirkleistungslimit) ist bei mehreren Herstellern vorhanden (Fronius, Kostal; SMA mit SunSpec-Profil). Ein Speicher-Sollwert über SunSpec gibt es nur bei Fronius (Model 124). Kostal implementiert Model 802 nur lesend.
- **EEBUS** findet sich bei Wechselrichtern bisher eher im HEMS (SMA Sunny Home Manager) als im Gerät selbst. Das Gros der deutschen Steuerbox-Anbindung läuft weiter über **Relais** oder EEBUS-Relais-Konverter (z. B. Weidmüller/PPC, Auslieferung ab Mitte 2026) [S, Q23].

---

## Reaktionszeiten und Rampen

| Quelle | Anforderung / Angabe | Wert | Beleg |
|---|---|---|---|
| **TOR Erzeuger Typ A V1.4** (AT, gültig ab 01.06.2026; V1.3 galt 01.07.2024–31.05.2026), Kap. 5.4.1.1 (korr. lt. 06) | „fernwirktechnische Schnittstelle (Eingangsport)“, um die Wirkleistungsabgabe zu beenden | **innerhalb 5 s** nach Eingang der Anweisung | [H, Q20; V1.4 S. 34 (korr. lt. 06)] |
| **TOR Typ A V1.4, Kap. 5.4.1.2** (neu) (korr. lt. 06) | Standardisierte digitale Schnittstelle (OpenADR, keine Drittsysteme); Sollwert der netzwirksamen Leistung am Netzanschlusspunkt; Fallback bei Kommunikationsausfall nur in Einspeiserichtung | **innerhalb 1 min** | [TOR V1.4 S. 34–35, laut 06] |
| TOR Typ A, Kap. 6.2.1 | Ausführung der Schnittstelle | **potentialfreie Kontakte** am Fernwirkgerät des Netzbetreibers (z. B. Funkrundsteuerempfänger, Gateway), **nur falls im Netzanschlussvertrag vorgesehen** (korr. lt. 06) | [H, Q20; V1.4 S. 40 (korr. lt. 06)] |
| TOR Typ A, Kap. 5.4.1 | Rollenteilung | Der Netzbetreiber „greift nicht in die Steuerung ein“, er ist nur für die Signalgebung verantwortlich; die Umsetzung liegt „in Eigenverantwortung des Anlagenbetreibers“ | [H, Q20 S. 34] |
| TOR Typ A, Wiederzuschaltung | Wartezeit einstellbar 0–300 s (Empfehlung 60 s bzw. 300 s nach Schutzauslösung); Gradient nach Störung | **≤ 10 % Pmax/min** | [H, Q20] |
| TOR Typ A, Kap. 6.2.3 | Einstellungen gegen Veränderung durch den Nutzer schützen (Passwort darf dem Nutzer nicht mitgeteilt werden) | – | [H, Q20 S. 38] |
| RfG (EU) 2016/631, Art. 13(6) | Eingangsport, um die Wirkleistung innerhalb 5 s zu beenden. Die TOR setzt die RfG um; Wortlaut im Original nicht geprüft | 5 s | **[unbestätigt]**, via [Q20] |
| **VDE-AR-N 4105:2018** (DE), umgesetzt in Netzbetreiber-TAB | Reduzierung in **vier diskreten Stufen** über RSE (vier Relais, Grundstellung 100 %); Quittierungsmeldungen | Zeitvorgabe „unverzüglich“; Sekundenwert nicht gefunden **[unbestätigt]** | [H, Q22] |
| EN 50549-1:2019, Abschn. 4.11.1 | Beenden der Wirkleistung über digitalen Eingangsport | Wert nicht im Original geprüft **[unbestätigt]** | [S, Victron-Zertifikat] |
| **IEEE 1547-2018** (USA) | Lokale DER-Kommunikationsschnittstelle mit mindestens einem Protokoll aus **SunSpec Modbus, IEEE 2030.5, IEEE 1815 (DNP3)** | Lese-Antwortzeit ≤ 30 s (Sekundärquelle) **[unbestätigt]** | [S, Q38] |
| RfG-2.0-Entwurf (V2G, Klasse EV2) | Wirkleistung auf Anweisung modulieren | 30-%-Sollwertsprung **in 0,5 s** | [S, Q41] |
| SMA (ennexOS-TI) | physikalische Reaktionszeit auf Modbus-Sollwert; Schreib-Antwortzeit ~1 s pro Parameter; Übertragungsintervall ≥ 1 s, ≤ 5 Parameter gleichzeitig | **~1 s** | [H, Q7] |
| Fronius GEN24 | `WinTms` 0–300 s (zufälliges Startfenster), `RmpTms` (Rampe), Requests nur sequentiell, Timeout ≥ 1 s | konfigurierbar | [H, Q10] |
| Kostal Plenticore | Einschwingverhalten „Standard / PT1 (s) / Leistungsgradient“ bei externer Wirkleistungsvorgabe über RSE oder Modbus | konfigurierbar | [H, Q29] |
| Kostal Plenticore, AT | Speicher-Sollwert-Register wegen Gradientenbegrenzung „in Austria for the gradient case (10 minutes)“ nicht dauerhaft zugänglich | **AT-Gradientenvorgabe kollidiert mit Speichersteuerung** | [H, Q11 Fußnote 7] |
| Victron ESS | fest einprogrammierte Rampe in der Inverter-Firmware (ab ESS v162) | **400 W/s** | [H, Q14] |
| Sungrow WiNet-S | Aktualisierungsrate der Daten | 10 s | [S, Q18] |

**Folgerung für das Profil:**

- Normativ gefordert ist in AT/EU ein **Abschalten in 5 s**, in AT zusätzlich der Sollwert der netzwirksamen Leistung am Netzanschlusspunkt **in 1 min** (TOR V1.4, 5.4.1.2) (korr. lt. 06). Für speicherspezifische Lade-/Entlade-Sollwerte gibt es **keine** normierte Reaktionszeit. Das Testabruf-Konzept des Teams (Reaktionszeit je Gerät messen) schließt genau diese Lücke.
- Die Herstellerwerte (~1 s bei SMA, 400 W/s bei Victron) zeigen: Für Engpassmanagement in Minuten ist die Geräteseite schnell genug. Der Engpass liegt im Kommunikationsweg.
- **Konflikt AT:** Der 10-%/min-Gradient der TOR beim Wiederhochfahren beschränkt, wie schnell ein Speicher nach einem Abruf wieder auf volle Leistung gehen darf. Kostal sperrt das Register im AT-Gradientenfall sogar [Q11]. Das sollte das Profil explizit regeln.

---

## Pflichtschnittstellen-Vorbilder

| Region | Instrument / seit | Pflichtinhalt | Kommunikationsweg | Ergebnis | Probleme | Quellen |
|---|---|---|---|---|---|---|
| **AU national** | AS/NZS 4777.2:2020, verbindlich für Neuinstallationen ab 18.12.2021 | Regionale Settings; Demand Response Modes (DRM 0–8) über DRED-Schnittstelle | Kontakt-/DRED-Klemmen (Fronius: DRM-Interface, SMA: DRM0) | breite Basisfähigkeit | Welche DRMs Pflicht sind, ist nicht im Original geprüft **[unbestätigt]** | [Q34][Q35] |
| **AU-SA** | „Smarter Homes“ ab **28.09.2020**; Flexible Exports als Standard ab **01.07.2023** | Relevant Agent für Fernabschaltung; alle Neu- und Upgrade-Anlagen müssen Flexible-Exports-fähig sein | **IEEE 2030.5 / CSIP-AUS** (SA HB 218): direkt, über Gateway (SwitchDin Droplet) oder Hersteller-Cloud (Fronius) | **> 95 %** der Geräte (nach Marktanteil) fähig; flexible Option **36 % → > 85 %**; Export bei 10 kW bzw. Anlagengröße in **99,4 %** der Zeit | Fallback **1,5 kW** bei Kommunikationsausfall; Cloud-Datenkosten der OEMs (Fronius/Azure); Compliance-Quote zunächst nur **16,5 %** der Händler > 90 % (08/2023: 84 %) | [Q30][Q31] |
| **AU-VIC** | Emergency Backstop: > 200 kVA ab 25.10.2023, **≤ 200 kVA ab 01.10.2024** | CSIP-AUS-Wechselrichter von der CEC-Liste, „connected to the internet at all times“; OEMs müssen die Verbindung zum Utility Server halten | CSIP-AUS (Cloud oder direkt) bzw. GMND | – | 5 Netzbetreiber mit eigenem Onboarding; Netzanschlüsse monatelang „on hold“; Netzbetreiber-Server offline; wiederholte Vor-Ort-Tests; Ausnahme ohne Internet → fester Export ≤ 1,5 kW | [Q32][Q33] |
| **AU-QLD** | Generation Signalling Device (GSD) ab **06.02.2023** für ≥ 10 kVA | Hardware-Abschaltgerät | Funk/Relais (Ein/Aus) | – | ~70 AUD Großhandel, 300–1000 AUD installiert; Einzellieferant; SMA, Fronius, GoodWe, Enphase, Growatt fordern ergebnisorientierte statt gerätespezifischer Regeln | [Q37] |
| **AU-WA** | Emergency Solar Management ab **14.02.2022** (≤ 5 kVA, neu/Upgrade) | Fernab- und -wiederzuschaltbar | Hersteller-Cloud (Synergy löst aus) | – | – | [Q39] |
| **AU-NSW** | Backstop gestaffelt **ab Ende 2026** (≤ 200 kW) | CSIP-AUS; Registrierung am Utility Server des Netzbetreibers | CSIP-AUS | – | – | [Q32b] |
| **US-CA** | Rule 21: Phase 1 (UL 1741 SA) ab 09/2017; **Phase 2 Kommunikation ab 22.06.2020** | IEEE 2030.5/CSIP als Default-Protokoll; Phase-3-Funktionen (Monitoring, Connect/Disconnect, Wirkleistungslimit, Scheduling …) gestaffelt | 3 Pfade: direkt (SMCU im WR oder Gateway), GFEMS, **Aggregator** | Breite Zertifizierungsinfrastruktur (SunSpec CSIP, CALSSA-Pfad) | Resolution E-5036: **WR selbst braucht kein 2030.5** → Gateway-/Cloud-Lösungen dominieren; SunSpec fand 2023 Kommunikationsdefekte bei UL-1741-SB-zertifizierten Geräten (inkonsistente Register, fehlender Broadcast) | [Q36][Q38] |
| **DE** | §9 EEG (Solarspitzengesetz, ab 25.02.2025); §14a EnWG + BNetzA-Festlegung BK6-22-300 (Stromspeicher als steuVE, > 4,2 kW) | Netzbetreiber muss Ist-Einspeisung abrufen und Einspeisung „stufenweise oder stufenlos ferngesteuert regeln“ können; bis zum iMSys: ≥ 100 kW Fernreduzierung, < 100 kW mit EEG-Vergütung **60-%-Begrenzung** | **SMGW + FNN-Steuerbox**, Anbindung per Relais oder **EEBUS LPC/LPP** | Pflicht wirkt auf den Neubestand | „EEBUS-fähig“ hieß nicht kompatibel → dreistufige EEBUS-Zertifizierung ab 2026; Relais erlauben nur 4 Stufen statt 16 | [Q21][Q23][Q24] |
| **AT** | § 76 ElWG + TOR Erzeuger Typ A V1.4 (ab 01.06.2026, bestätigt; V1.3 galt 01.07.2024–31.05.2026) (korr. lt. 06) | 5.4.1.1: Eingangsport, 5 s Abschalten; potentialfreie Kontakte, **falls im Netzanschlussvertrag vorgesehen**. 5.4.1.2: digitale Schnittstelle, Sollwert netzwirksame Leistung am Netzanschlusspunkt in 1 min, Fallback nur Einspeiserichtung (korr. lt. 06) | Rundsteuer / Gateway des Netzbetreibers; **OpenADR (IEC 62746-10-1) über Kundeninternet, keine Drittsysteme**, AT-Profil bis 31.10.2026 (korr. lt. 06) | – | kein Speicher-Sollwert, Speicher-Rückspeisung nicht vorgesehen (Fall 1, S. 38) | [Q20; TOR V1.4 laut 06] |
| **BE-Flandern** | TRDE-Änderung (27.03.2026) | **Telecontrol für Batterien ≥ 250 kVA** (Konsultation: 100 kVA); kleinere: „technische Flexibilität“ aktivierbar | Netzbetreiber-Fernsteuerung | – | Heimspeicher nicht erfasst | [Q44] |
| **NL** | Netcode: Realtime-Schnittstelle Pflicht ab 1 MW (Stand 2024); NEN entwickelt NTAs für „slimme net-intensieve apparaten“ (12/2025) | Heimgeräte: keine Pflicht gefunden | – | – | – | [Q45][Q46] |
| **LT** | Elektrizitätsgesetz Art. 73³ (11/2024) | **Verbot des Fernzugriffs** von Unternehmen aus Risikostaaten (China) auf PV, Wind und Speicher > 100 kW; Neuanlagen ab 01.05.2025 | – | Netzbetreiber dürfen nicht konforme Anlagen nicht anschließen | sicherheitspolitisch motiviert, kein Interop-Standard | [Q47] |
| **EU** | RfG 2016/631; **RfG-2.0-Entwurf 08.07.2026** (Ersatz der VO, Annahme Q4 2026 geplant); Ecodesign PV-WR „act in preparation“ | heute nur Eingangsport; Entwurf: Speicher im Anwendungsbereich, grid-forming, V2G-Klassen | Protokoll **nicht benannt** (OCA forderte IEC 63584/OCPP für V2G) | – | Fristen laufen ab Inkrafttreten: allgemeine Anforderungen ca. 2 Jahre, also etwa Ende 2028 | [Q40][Q41][Q42][Q43] |

### Lessons learned

1. **Ein nationaler Profilstandard ist entscheidend.** Australien hat CSIP-AUS als Handbuch (SA HB 218) vor dem Rollout festgelegt. Laut SAPN-Bericht schafft ein „nationally consistent framework“ technische und finanzielle Sicherheit für die OEMs [Q30]. SwitchDin warnt dagegen vor inkompatiblen Netzbetreiber-Servern, die mehrere Testprozeduren und mehrere Whitelists nach sich ziehen [Q31]. Genau das ist in VIC mit fünf Netzbetreibern eingetreten [Q33].
2. **Die Pflicht hebt die Gerätebasis schnell.** In SA stieg die Abdeckung von „limitierter Verfügbarkeit“ auf über 95 % nach Marktanteil [Q30].
3. **Der Cloud-Pfad ist am schnellsten umgesetzt, kostet aber dauerhaft und bindet an Hersteller und Internet.** Fronius beziffert kleine Entwicklungskosten, aber laufende Azure-Kosten, die mit der Flotte wachsen. Die direkte Gerät-zu-Utility-Anbindung vermeidet diese Kosten [Q30]. Fällt das Internet aus, greift der Fallback (1,5 kW) [Q30]. Dass Internetverbindungen gerade bei Netznotfällen unsicher sind, ist ein Einwand der Branche **[unbestätigt, nur Sekundär-Snippet]**.
4. **Pflichten nach Ergebnis statt nach Gerät.** QLD (GSD, Einzellieferant) erntete Widerstand von SMA, Fronius, GoodWe, Enphase und Growatt. Sie forderten „outcomes … rather than equipment“ [Q37].
5. **Zertifizierung allein reicht nicht.** SunSpec fand Defekte bei UL-1741-SB-zertifizierten Geräten [Q38]. EEBUS führte eine dreistufige Zertifizierung ein, weil „EEBUS-fähig“ nicht „kompatibel“ bedeutete [Q23]. Daraus folgt: Es braucht **laufende Funktionsnachweise im Feld**. Das ist das Argument für Testabrufe mit Smart-Meter-Verifikation.
6. **Compliance muss man aktiv managen.** SA führte ein Händler-Rating ein. Damit stieg der Anteil der Solarhändler mit über 90 % Compliance in Monaten von 16,5 % auf 84 % [Q30]. Gemessen wurde mit AMI-Smart-Meter-Daten plus Gerätedaten. Das entspricht fast 1:1 der Team-Idee „Smart Meter verifiziert“.
7. **„Interface in, Logik out“ (Kalifornien) führt zu Gateway-Wildwuchs.** Rule 21 schreibt nur die Schnittstelle zur Utility vor. Die Strecke Gateway → Gerät bleibt proprietär, das Gerät muss 2030.5 nicht können [Q36]. Für eine EU-Pflicht hieße das: Die **lokale** Geräteschnittstelle sollte mitstandardisiert werden, sonst bleibt die Herstellerabhängigkeit bestehen.

---

## Argumente für und gegen eine EU-Pflichtschnittstelle

### Dafür

- **Bestand ist steuerbar, aber nicht interoperabel.** 12 von 17 betrachteten Herstellern erlauben lokal Wirkleistungs- *und* Speichersollwerte, aber jeder über ein eigenes Register- und Semantikmodell (siehe Tabelle). Eine Pflicht kodifiziert vorhandene Fähigkeiten und erfordert keine neue Hardware-Kategorie.
- **Das Australien-Vorbild:** Die Pflicht hob die Gerätebasis auf > 95 % und die Teilnahme auf > 85 %. Netzseitig wurden höhere Exportlimits möglich (99,4 % der Zeit 10 kW) [Q30].
- **Es gibt ein passendes Gesetzgebungsfenster.** RfG 2.0 wird gerade finalisiert (Q4 2026), Ecodesign für PV-Wechselrichter ist in Vorbereitung. Beide sind EU-weite Produkt- bzw. Anschlussvorgaben und vermeiden 27 nationale Steuerbox-Varianten [Q40][Q43].
- **Weniger Abhängigkeit von Hersteller-Clouds:** Huawei und Sungrow stellen 55 % der globalen WR-Lieferungen [Q4]. Litauen verbietet bereits Fernzugriff aus China auf Anlagen > 100 kW [Q47]. Eine standardisierte lokale Schnittstelle erlaubt netzdienliche Steuerung **ohne** Hersteller-Cloud.
- **Bidirektional statt nur „Aus“:** Heute ist normativ das Abschalten Pflicht (TOR/RfG 5 s), in AT zusätzlich ein Sollwert am Netzanschlusspunkt (TOR V1.4, 1 min) (korr. lt. 06). Für die Challenge („laden bei Überschuss, entladen bei Last“) fehlt der **Speicher-Sollwert** im Pflichtenheft komplett [Q20].
- **Sicheres Fallback als Pflichtmerkmal:** Watchdog und Fallback existieren bei Fronius, Kostal und Victron, bei anderen nicht [Q10][Q11][Q14]. Eine Pflicht kann ein definiertes Rückfallverhalten erzwingen, ein Kernanliegen der Security.

### Dagegen bzw. Risiken

- **Kosten pro Gerät und Zertifizierungsaufwand.** QLD-GSD: 300–1000 AUD installiert [Q37]. Hinzu kommen Cloud-Betriebskosten bei OEMs [Q30].
- **Protokollstreit:** EEBUS (DE), IEEE 2030.5/CSIP (AU/US), SunSpec Modbus, S2/EN 50491-12-2, OCPP für V2G. Die EU hat im RfG-2.0-Entwurf bewusst **kein** Protokoll benannt [Q41].
- **Nur Neubestand:** Alle Vorbilder erfassen nur neue bzw. aufgerüstete Anlagen (z. B. DE §9 EEG ab 25.02.2025, VIC ab 01.10.2024). Der installierte Bestand bleibt über Jahre auf Kontakt- oder Herstellerlösungen angewiesen.
- **Onboarding-Komplexität bei vielen Netzbetreibern:** VIC zeigt die Probleme bei fünf Netzbetreibern [Q33]. AT hat über 120 Netzbetreiber **[unbestätigt]**.
- **Wechselwirkung mit Normvorgaben:** z. B. der AT-Gradient von 10 %/min beim Wiederhochfahren [Q11][Q20]. Eine Pflichtschnittstelle muss mit TOR und EN 50549 konsistent sein.
- **Angriffsfläche:** Eine einheitliche, breit ausgerollte Steuerschnittstelle erhöht das Massenschalt-Risiko. Modbus TCP ist ungesichert [Q12]. Signatur, Grenzwerte und Randomisierung (Fronius `WinTms` 0–300 s [Q10]) wären daher Pflicht (siehe Block 4).
- **Marktdesign:** Den Speicherbetrieb bestimmt laut Challenge der Anlagenbetreiber. Eine Pflichtschnittstelle darf nicht zur Daueransteuerung werden. Rechtsgrundlage und Vergütung behandelt Block 1.

---

## Offene Fragen an Smart Grids Austria

1. Soll das Profil **nur die Schnittstelle Netzbetreiber → Kommunikationsmodul** festlegen (wie Rule 21) oder **auch die lokale Geräteschnittstelle** (z. B. SunSpec 123/124 bzw. 7xx/802)? Lesson 7 spricht für beides.
2. Wie soll der **10-%-Pmax/min-Gradient** der TOR Typ A beim Wiederhochfahren für Speicher-Entlade-Abrufe gelten? Hersteller wie Kostal sperren deshalb in AT Sollwert-Register [Q11].
3. Gilt ein netzdienliches **Entladen ins Netz** für AC-gekoppelte einphasige Speicher als zulässig? TOR Typ A Fall 1 geht auch in V1.4 (S. 38) von „keiner Rückspeisung“ aus [Q20] (korr. lt. 06).
4. Welche **Reaktionszeit und Genauigkeit** braucht das Engpassmanagement im Verteilnetz wirklich? Normativ gibt es „5 s Aus“ und in AT 1 min für den Sollwert am Netzanschlusspunkt (TOR V1.4, 5.4.1.2); speicherspezifisch gibt es nichts (korr. lt. 06).
5. Ist ein **Kontakt-/RSE-Pfad** als Rückfallebene gewünscht (z. B. 0/30/60/100 % plus „Laden erlaubt/gesperrt“), oder nur digital?
6. Wie wird mit dem **Bestand** umgegangen: Nachrüst-Gateway (SwitchDin-Modell) oder Hersteller-Cloud (Fronius-AU-Modell)?
7. Soll ein **Fallback-Verhalten** (Timeout plus Grenzwerte, wie Kostal 1284–1288) verpflichtend im Profil stehen?
8. Gibt es in AT schon eine Position zu **RfG 2.0** und zur EEBUS-/CSIP-Frage, z. B. von E-Control oder Oesterreichs Energie?
9. Kann die **Smart-Meter-Kundenschnittstelle** in AT (15-min-/Sekundenwerte?) die Verifikation leisten, wie AMI-Daten in SA [Q30]? Das ist abzustimmen mit Block 3.

---

## Quellenliste

**Marktanteile**

- [Q1] pv magazine DE, 26.06.2026: Strukturwandel im Heimspeichermarkt 2025 (MaStR, P3/ISEA RWTH). https://www.pv-magazine.de/2026/06/26/strukturwandel-im-heimspeichermarkt-2025-marktanteile-der-hersteller-zeigen-hohe-dynamik/
- [Q2] pv magazine DE, 05.05.2025: 5,1 GWh Heimspeicher in 2024, asiatische Hersteller > 50 %. https://www.pv-magazine.de/2025/05/05/51-gigawattstunden-heimspeicher-in-2024-asiatische-hersteller-mit-ueber-50-prozent-marktanteil/
- [Q3] pv magazine, 08.09.2026: Europe's storage market to hit 57 GWh in 2026, says EUPD Research. https://www.pv-magazine.com/2026/09/08/europes-storage-market-to-hit-57-gwh-in-2026-says-eupd-research/
- [Q4] pv magazine Australia, 14.07.2025: Huawei leads global inverter market as shipments hit 589 GW in 2024 (Wood Mackenzie). https://www.pv-magazine-australia.com/?p=13986
- [Q5] SolarPower Europe: European Market Outlook for Battery Storage 2025–2029. https://www.solarpowereurope.org/insights/outlooks/european-market-outlook-for-battery-storage-2025-2029 · Zusammenfassung: https://www.ees-europe.com/news/european-market-outlook-for-battery-storage-2025-2029 · Residential Outlook: https://reglobal.org/european-market-outlook-for-residential-battery-storage/
- [Q6] pv magazine USA, 05.01.2026: Huawei, Sungrow lead Wood Mackenzie's inverter market ranking (H1 2025). https://pv-magazine-usa.com/2026/01/05/huawei-sungrow-lead-wood-mackenzies-inverter-market-ranking/

**Herstellerdokumente**

- [Q7] SMA: Technical Information „SMA Modbus Interface ennexOS“ (SMAModbus-ennexOS-TI-en-12), Kap. 3.6 Data Processing and Time Behavior [H]. https://files.sma.de/downloads/SMAModbus-ennexOS-TI-en-12.pdf · SMA/SunSpec Modbus allgemein: https://files.sma.de/downloads/SMA-Modbus-general-TI-en-10.pdf
- [Q8] SolarEdge: Technical Note „SunSpec Logging“ v3.3 (10/2026) [H, nur Titel/Snippet, 403 beim Abruf]. https://knowledge-center.solaredge.com/sites/kc/files/sunspec-implementation-technical-note.pdf
- [Q9] SolarEdge: Application Note „Power Reduction Control“ v4 bzw. „Power Control Options“ (RRCR) [H, nur Snippet]. https://knowledge-center.solaredge.com/sites/kc/files/power-reduction-control-application-note.pdf · https://knowledge-center.solaredge.com/sites/kc/files/application_note_power_control_configuration.pdf
- [Q10] Fronius: GEN24 – Modbus TCP and RTU Operating Instructions (Model 123/124, RvrtTms, Response times) [H]. https://manuals.fronius.com/html/4204102649/en-US.html
- [Q11] KOSTAL: PIKO IQ / PLENTICORE – Interface description MODBUS (TCP) & SunSpec, Rev. 2.7, 20.11.2025, Kap. 3.4/3.5/4.2 [H]. Gespiegelt unter https://taphome.com/compatibility/devices/plentycoreinverter/manufacturer/kostal-modbus-interface.pdf · Original-Downloadbereich: https://www.kostal-solar-electric.com/en/download/page/213
- [Q12] Fronius: Symo GEN24 6–10 kW Plus, Bedienungsanleitung (Datenkommunikations-Bereich, I/O-Leistungsmanagement, „Modbus TCP/IP ist eine ungesicherte Schnittstelle“) [H]. https://manuals.fronius.com/html/4204260315/de.html
- [Q13] Pionierkraft: Vorab-Hinweise Fronius GEN24 (Modbus ab Werk deaktiviert, Steuerung freischalten) [S]. https://info.pionierkraft.de/hubfs/Dokumente%20PARTNER-Helpdesk/Vorab-Hinweise%20Fronius%20Verto%20_%20Tauro%20_%20GEN24%20_%20Primo%20GEN24%20_%20Symo%20GEN24.pdf
- [Q14] Victron Energy: ESS mode 2 and 3 (Register 2716, 37/40/41, 60-s-Regel, 400 W/s) [H]. https://www.victronenergy.com/live/ess:ess_mode_2_and_3
- [Q15] Huawei: Datenblatt SUN2000-5/6/8/10/12K-MAP0, Version 02-202406 (Communication, „Ripple receiver control: Yes“, Netzanschlussnormen inkl. EN 50549-1, VDE 4105, TOR Erzeuger, CEI 0-21) [H]. https://solar.huawei.com/admin/asset/v1/pro/view/1895ef0ef0a64bd5ae353e422fbd4af4.pdf
- [Q16] Huawei: Solar Inverter Modbus Interface Definitions (SUN2000MA, Issue 08, 2024-07-04) [H, nur Snippet]. https://support.huawei.com/enterprise/de/doc/EDOC1100387581
- [Q17] Krannich-Shop: Sungrow SH5.0RT-V112 (4 × DI, „Contact ripple control receiver: yes“) [S]. https://shop.krannich-solar.com/en-de/SH5.0RT-V112/0152286
- [Q18] Sungrow: Compatibility Factsheet (WiNet-S2, 10 s) [H, Snippet]. https://ger.sungrowpower.com/upload/file/20240410/EN_FS_Compatibility_Factsheet.pdf · openHAB Sungrow Binding (Protokoll V1.0.23/V1.1.15, Whitelist): https://www.openhab.org/addons/bindings/modbus.sungrow/
- [Q9b] RenewEconomy: SolarEdge software first to get approval for rooftop solar flexible export plan [S, nur Titel]. https://reneweconomy.com.au/solaredge-software-first-to-get-approval-for-rooftop-solar-flexible-export-plan/
- [Q18b] pv magazine Australia, 05.09.2025: South Australia commercial BESS projects first to face CSIP-AUS testing (Sungrow/iSolarCloud) [S, nur Snippet]. https://www.pv-magazine-australia.com/2025/09/05/south-australia-commercial-bess-projects-first-to-face-csip-aus-testing
- [Q19] BYD: Battery-Box Premium HVS&HVM Compatible Inverter List (V2.10, 2023; V2.21, 2025-08-20) [H]. https://bydbatterybox.com/uploads/downloads/BYD%20Battery-Box%20Premium%20HVS&HVM%20Compatible%20Inverter%20List-V2.10-63d76b3b31b89.pdf
- [Q24] SMA: Technische Information „§14a EnWG“ (EnWG14a-TI-de-10): SHM 2.0 ab FW 2.16.4.R, EEBus zur Steuerbox, Failsafe-Grenze [H]. https://files.sma.de/downloads/EnWG14a-TI-de-10.pdf
- [Q25] SMA: Data Manager M Bedienungsanleitung (SunSpec Modbus, EEBUS 1 Gerät) [H, Snippet]. https://files.sma.de/downloads/EDMM-10A-BE-de-10.pdf · SMA DRM0 (AS/NZS 4777.2): https://files.sma.de/assets/279168.pdf
- [Q26] GoodWe: ET G2 Quick Installation Guide (DI1 Remote Shutdown) [H, Snippet]. https://en.goodwe.com/Ftp/EN/Downloads/User%20Manual/GW_ET-G2_Quick-Installation-Guide-POLY.pdf
- [Q27] TapHome: GoodWe ET Plus+ (Modbus RTU/TCP, Port 502, ID 247) [S]. https://taphome.com/en/compatibility/goodwe-et-plus-inverters/
- [Q28] SunSpec: Mitgliedseintrag Enphase (2030.5 CSIP CS-000096) [S]. https://sunspec.org/contributing-members/enphase-energy/ · Enphase IEEE 1547-2018: https://enphase.com/installers/resources/ieee-1547-2018 · Enphase Local API Token: https://enphase.com/download/accessing-iq-gateway-local-apis-or-local-ui-token-based-authentication
- [Q29] KOSTAL: PLENTICORE BI G3 Handbuch, „Settling time“ [H]. https://documents.kostal.com/PLENTICORE-BI-G3/en-GB/473287819.html

**Open-Source-Implementierung evcc** (Commit fab6fad, 23.10.2026) [S]

Basis: `https://github.com/evcc-io/evcc/blob/fab6fad7bdb80691e80de848c4e1bc41a3eab8a7/templates/definition/meter/`

| Kürzel | Template-Datei(en) |
|---|---|
| [S-sma] | `sma-hybrid.yaml` |
| [S-hua] | `huawei-sun2000-hybrid.yaml` |
| [S-se] | `solaredge-hybrid.yaml` |
| [S-sun] | `sungrow-hybrid.yaml` |
| [S-gw] | `goodwe-hybrid.yaml` |
| [S-grw] | `growatt-hybrid.yaml` |
| [S-enp] | `enphase.yaml`, `enphase-modbus.yaml` |
| [S-sx] | `solax.yaml` |
| [S-dey] | `deye-hybrid-3p.yaml` |
| [S-fox] | `fox-ess-h3.yaml` |
| [S-tes] | `tesla-powerwall.yaml`, `tesla-powerwall-fleet.yaml` |
| [S-son] | `sonnenbatterie.yaml` |
| [S-e3] | `e3dc-rscp.yaml` |

Ergänzende Quellen zu einzelnen Kürzeln:

- [S-se] evcc-Doku: https://docs.evcc.io/en/meters/solaredge-hybrid-inverter
- [S-son] openHAB sonnen Binding: https://www.openhab.org/addons/bindings/sonnen
- [S-tes] Powerwall 3 lokal: https://github.com/jasonacox/pypowerwall

**Normen und Regulierung**

- [Q20] E-Control / Wiener Netze: TOR Stromerzeugungsanlagen Typ A, Version 1.3, gültig ab 01.07.2024. Kap. 2.4, 5.4.1 (S. 33–34), 6.2.1–6.2.3 (S. 38), Unsymmetrie/Speicher-Fälle (S. 36) [H]. **Abgelöst durch V1.4 (gültig ab 01.06.2026): 5.4.1 S. 34–35, Fall 1 S. 38, 6.2.1 S. 40**, https://www.e-control.at/documents/1785851/1811582/TOR+Stromerzeugungsanlagen+Typ+A+Version+1.4+(7).pdf/093752f5-e220-0731-b8a8-bfa85ccb7287?t=1780897058735 (korr. lt. 06). V1.3: https://wienernetze.at/o/document/tor_stromerzeugungsanlagen_typ_a_version_1-3_juli24 · V1.2: https://www.e-control.at/documents/1785851/1811582/TOR+Erzeuger+Typ+A+V1.2.pdf
- [Q21] § 9 EEG [H]. https://www.gesetze-im-internet.de/eeg_2014/__9.html · § 14a EnWG [H]: https://www.gesetze-im-internet.de/enwg_2005/__14a.html
- [Q22] Stromnetz Berlin: Technische Mindestanforderungen Netzsicherheitsmanagement, Ausgabe 08/2025 (vier Stufen nach VDE-AR-N 4105, RSE mit 4 Relais, Quittierung) [H]. https://www.stromnetz.berlin/files/globalassets/dokumente/technische-anschlussbedingungen/ta-netzsicherheitsmanagement/Technische-Mindestanforderungen-Netzsicherheitsmanagement_2025-08.pdf
- [Q23] evcc: FNN-Steuerbox via EEBus LPC&LPP (§14a EnWG, §9 EEG) [S]. https://docs.evcc.io/en/external-limit/fnn-steuerbox-via-eebus-lpcandlpp-ss-14a-enwg-ss-9-eeg · innobu, EEBUS-Zertifizierung 2026 [S]: https://www.innobu.com/de/artikel/eebus-iec-63380-han-hems-2026.html · ZfK, EEBUS-Zertifizierung [S]: https://www.zfk.de/digitalisierung/it/eebus-zertifizierung-steuersignal-sucht-kompatibles-geraet · PPC-Blog 2026 (EEBUS-Relais-Konverter) [S]: https://www.ppc-ag.de/en/blog/2026/page/2/
- [Q30] SA Power Networks / ARENA: Flexible Exports for Solar PV Trial – Final Report, v1.3, 19.10.2023 (S. 2–4, 51–52, Compliance-Rating) [H]. https://arena.gov.au/assets/2024/01/SA-Power-Networks-Flexible-Exports-for-Solar-PV-Trial-Final-Report.pdf
- [Q31] SwitchDin: Submission to Victoria's Emergency Backstop Mechanism Consultation [S]. https://www.switchdin.com/s/SwitchDin-submission-to-Victorias-Emergency-Backstop-Mechanism-Consultation-Paperdocx.pdf
- [Q32] DEECA Victoria: Emergency backstop industry guidance (06/2024) [H, Snippet]. https://www.energy.vic.gov.au/__data/assets/pdf_file/0022/701905/Emergency-backstop-industry-guidance-June-2024.pdf · Jemena: https://www.jemena.com.au/electricity/solar-connections/victoria-emergency-backstop-mechanism/ · AusNet, Anforderungen an Hersteller ab 01.10.2024 [H]: https://www.ausnetservices.com.au/renewables/industry-solar/solar-manufacturers
- [Q32b] NSW Climate and Energy Action: Emergency backstop mechanism [H]. https://www.energy.nsw.gov.au/emergency-backstop-mechanism
- [Q33] SolarQuotes, 18.02.2025: Problems With Victoria's Emergency Backstop For Solar Drag On [S]. https://www.solarquotes.com.au/blog/vic-vebm-solar-problems-mb3119/
- [Q34] AEMO: AS/NZS 4777.2 – Inverter Requirements standard [H]. https://www.aemo.com.au/en/initiatives/major-programs/nem-distributed-energy-resources-der-program/standards-and-connections/as-nzs-4777-2-inverter-requirements-standard
- [Q35] GSES: AS/NZS 4777.2:2020 Updates (DRM-Tabelle) [S]. https://www.gses.com.au/wp-content/uploads/2021/08/GCB_AU2-3_Updates-for-Website.pdf
- [Q36] QualityLogic: CA Rule 21 Communications Requirements and Certifications for Smart Inverters, v1.4, 02/2020 [S]. https://www.qualitylogic.com/wp-content/uploads/2020/12/CA-Rule-21-Communications-Requirements-and-Certifications-for-Smart-Inverters-White-Paper-12-20-compressed.pdf · SunSpec: Rule 21 Phase 2 [S, 403]: https://sunspec.org/california-rule-21-phase-2-goes-into-effect-this-month · CPUC: https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M321/K596/321596742.PDF
- [Q37] SolarQuotes, 09.11.2022: Inverter Manufacturers Hit Back On QLD Emergency Backstop [S]. https://solarquotes.com.au/blog/qld-emergency-backstop-submission-mb2708 · pv magazine, 03.12.2024 (AEMO, Backstop in allen Festlandstaaten) [S]: https://www.pv-magazine.com/2024/12/03/australian-regulator-makes-case-for-rooftop-solar-control-mechanism/
- [Q38] SunSpec: Communication Interface Defects Revealed in UL 1741 SB Certified Inverters (2023) [S, Snippet, 403]. https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ · NRECA, IEEE 1547-2018 (30 s) [S]: https://www.cooperative.com/programs-services/bts/Documents/Emerging%20Priorities%20for%20Energy%20Research%20Day%20-%20Oct%202018/IEEE%201547-2018%20-%20Vartanian%20(NRECA-APA-ResearchDay-20181031).pdf
- [Q39] AEMO WA: Emergency Solar Management [H]. https://aemo.com.au/initiatives/major-programs/wa-der-program/emergency-solar-management · Western Power: https://www.westernpower.com.au/news/solar-industry-changes-with-introduction-of-emergency-solar-management/
- [Q40] Energy Storage Europe, 27.08.2026: Revision of Network Code on Requirements for Grid Connection of Generators [S]. https://energystorageeurope.eu/news/revision-of-network-code-on-requirements-for-grid-connection-of-generators/ · ACER Recommendation 03/2023 [H]: https://www.acer.europa.eu/sites/default/files/documents/Recommendations/ACER_Recommendation_03-2023_NC_RfG_DC.pdf
- [Q41] Plugchoice: RfG 2.0 Draft – V2G EVSE classes; RfG 2.0 consultation closed, 117 responses, adoption Q4 2026 [S]. https://plugchoice.com/en/news/eu-rfg-2-0-draft-v2g-grid-code · https://plugchoice.com/en/news/rfg-2-0-consultation-closed-117-responses
- [Q42] UFE: Feedback on the revision of the RfG [S]. https://ufe-electricite.fr/en/ufe-reply-european-commission-consultation-rfg-2/
- [Q43] Rat der EU, ST-8225-2025-ADD-1 (SWD zum ESPR/Energy-Labelling-Arbeitsplan 2025–2030): „Photovoltaic modules, inverters and systems – New product – Act in preparation“ [H]. https://data.consilium.europa.eu/doc/document/ST-8225-2025-ADD-1/en/pdf · ESIA-Folien 2023 („standardised interconnectivity for inverters“) [S]: https://esmc.solar/wp-content/uploads/2023/11/2023-0914-ESIA_Ecodesign-and-labelling.pdf
- [Q44] Solar Magazine NL, 27.03.2026: Vlaanderen verplicht telecontrole batterijen definitief vanaf 250 kVA [S]. https://solarmagazine.nl/nieuws-zonne-energie/i43325/vlaanderen-verplicht-telecontrole-batterijen-definitief-vanaf-250-kilovoltampere
- [Q45] Solar Magazine NL, 08/2024: Netbeheerders vragen ACM ondersteuning voor uitrol realtime interface [S]. https://solarmagazine.nl/nieuws-zonne-energie/i38226/netbeheerders-vragen-acm-ondersteuning-voor-uitrol-realtime-interface
- [Q46] Solar Magazine NL, 18.12.2025: ElaadNL – slimme net-intensieve apparaten (NEN-NTAs) [S]. https://solarmagazine.nl/nieuws-zonne-energie/i42486/elaadnl-slimme-net-intensieve-apparaten-moeten-vanaf-2027-naadloos-met-elkaar-samenwerken
- [Q47] ESMC: Lithuanian parliament bans remote access of companies from China to solar, wind and storage devices [S]. https://esmc.solar/lithuanian-parliament-bans-remote-access-of-companies-from-china-to-lithuanian-solar-wind-and-storage-devices/ · pv tech: https://pv-tech.org/lithuania-to-block-chinese-inverters-with-cybersecurity-legislation
