# 06 – Querprüfung

Stand: 23.10.2026. Ich habe zehn Kernaussagen aus 01–05 gegen die Primärquellen geprüft und die Dateien
auf Widersprüche untereinander gelesen. Die Dateien 01–05 sind unverändert.

Ablage der geprüften Quelltexte:
`/private/tmp/claude-501/-Users-dbuchber-Desktop-tmp-nosync-vscode-infra-kg-austria/3e7ea6fb-32e5-4771-b73a-bb11d20cb91c/scratchpad/reg/`
(TOR 1.4, ElWG, SNE-G-V, Verteilernetzstudie) und `.../scratchpad/check/` (Symphony, SAPN Flexible Exports,
NISG-RIS-Auszug, Netz-OÖ-Folien zu OpenADR).

Urteile: **BESTÄTIGT** = stimmt mit der Primärquelle überein. **TEILWEISE** = Kern stimmt, aber
Einschränkung oder Präzisierung fehlt. **FALSCH** = widerspricht der Quelle. **NICHT PRÜFBAR** = Primärquelle
nicht zugänglich.

---

## Urteilstabelle

| Nr. | Aussage (Datei) | Urteil | Fundstelle | Korrektur / Präzisierung |
|---|---|---|---|---|
| 1a | § 76 ElWG: neue Erzeugungsanlagen ab 3,68 kW ab 1.6.2026 mit Steuereinrichtung und standardisierter Schnittstelle (01) | **BESTÄTIGT** | BGBl. I 91/2025, § 76 Abs. 1–3, S. 60–61 von 149 | § 76 nennt **kein Protokoll**. Es verweist für die Schnittstelle auf die TOR. |
| 1b | TOR Typ A v1.4: OpenADR (IEC 62746-10-1) über Kundeninternet, Sollwert in 1 min, Fallback 70 % (01) | **BESTÄTIGT** | TOR SEA Typ A V1.4, Kap. 5.4.1.2, S. 34–35, Fn. 24–25 | Der Fallback begrenzt nur die **Einspeiserichtung**, auf den vertraglichen Wert bzw. bei PV auf 70 % der Modulspitzenleistung (§ 101 Abs. 2 ElWG). Er gilt für Netzbenutzer mit dynamischem Sollwert. |
| 1c | TOR Typ A verlangt nur potentialfreie Kontakte (5 s), keinen Speicher-Sollwert (05) | **TEILWEISE** (veraltet) | V1.3 galt vom 1.7.2024 bis 31.5.2026. V1.4 gilt ab 1.6.2026 (Versionstabelle, S. 2) | V1.4 behält Kap. 5.4.1.1 (Eingangsport, 5 s) und 6.2.1 (potentialfreie Kontakte, **nur falls im Netzanschlussvertrag vorgesehen**, S. 40). Neu ist Kap. 5.4.1.2 mit der digitalen OpenADR-Schnittstelle. Ein speicherspezifischer Lade-/Entlade-Sollwert fehlt weiterhin. |
| 1d | OpenADR-AT-Profil bis 31.10.2026 spezifizieren, bis 31.12.2026 veröffentlichen (01) | **BESTÄTIGT** | TOR V1.4, Fn. 25, S. 35 | Eine Veröffentlichung haben wir bis 23.10.2026 nicht gefunden. Netz OÖ arbeitet mit **OpenADR 3.1** (Folien vom 4.3.2026). IEC 62746-10-1 beruht aber auf OpenADR 2.0b. Siehe Detail 1. |
| 2 | SNE-G-V: Befreiung systemdienlicher Speicher bei unentgeltlicher Einschränkung in beide Richtungen; Bündelung ab 10 kW zu ≥ 1 MW; Deckel 5 GW; flexible Entnahme ab 4 kW, 2 × 2 h, ab 1.10.2027 (01) | **TEILWEISE** | BGBl. II 299/2026: § 10 (S. 6), §§ 23–24 (S. 11), § 26 (S. 12), §§ 32–33 (S. 13) | Alle Zahlen stimmen. Es fehlt aber eine Bedingung: Befreit ist nur ein Speicher, der „**ausschließlich zur Wiedereinspeisung** betrieben wird“ (§ 23). Ein Heimspeicher zur Eigenverbrauchsoptimierung erfüllt das nicht ohne Weiteres. Außerdem gilt: Standort an einem UW der NE 4 mit PV-Verhältnisleistung > 0,3 MW/MVA **oder** Wind > 0,85 MW/MVA **und** Rückspeisedauer > 2 500 h. Die Verordnung gilt ab 1.1.2027 (§ 32 Abs. 1), Tarifgrundlage also nicht „seit 12.10.2026“. |
| 3 | § 14a EnWG: Dimmen auf 4,2 kW; Modul 1 110–190 €/a; Modul 2 Arbeitspreis auf 40 %; Speicher nur beim Netzbezug (01) | **BESTÄTIGT** | BNetzA, Steuerbare Verbrauchseinrichtungen | Wortlaut: „temporär auf bis zu 4,2 kW“. Modul 1: „Stand 2023“. Modul 2 ist nicht mit Modul 1 kombinierbar. Einspeisung: „allein Regelungen für die Stromentnahme … nicht für die Einspeisung“. |
| 4 | ACM-Codebesluit capaciteitssturingscontract 11.12.2025, Nutzung entgegen der Engpassrichtung gegen Vergütung (01) | **BESTÄTIGT** | ACM/25/196733, Beschluss 11.12.2025, veröffentlicht 12.12.2025, https://www.acm.nl/nl/node/28583 | Wortlaut: „in de tegengestelde richting van de congestie“, Rückspeisung aus Erzeugung oder Batterie „tegen een vergoeding“. Ob Kleinverbraucher erfasst sind, sagt die Seite nicht. |
| 5 | BMWi-Verteilernetzstudie 2014: 3 % Abregelung → > 40 % weniger Netzausbau (01) | **BESTÄTIGT** | Zusammenfassung, PDF-S. 12 | Präzisierung: 3 % der Jahresenergie **von Wind- und PV-Anlagen in Netzen mit Ausbaubedarf**, nicht der gesamten EE-Jahresenergie. 1 % → ca. 30 % stimmt ebenfalls. |
| 6 | Symphony: 26,6 % nicht konforme 5-min-Intervalle; 714 von 911 Geräten; 32 WR-Modelle von 7 Herstellern (02) | **BESTÄTIGT** | Final Report: 26,6 % PDF-S. 53; 714/911 PDF-S. 59; 32 Modelle/7 Hersteller PDF-S. 60 | Der Bericht nennt auf PDF-S. 43 selbst **715** statt 714. 26,6 % bezieht sich auf „NSS intervals“ aus 8 Abrufen, Konformität = ≥ 95 % des Signals. |
| 7 | SAPN Flexible Exports: 89,3 % Erreichbarkeit bei Tageslicht; > 99,97 % Einhaltung; Fallback 1,5 kW; > 95 % steuerfähig nach Pflicht (03/05) | **BESTÄTIGT** | Final Report v1.3: 95 %/36→85 % S. 4 (PDF 5); 1,5 kW S. 11 (PDF 12); 89,3 % S. 45 (PDF 46); 99,97 % PDF 47 | 1,5 kW gilt **je Phase**. 89,3 % bezieht sich auf die Tageslicht-Betriebszeit der Constraint Engine. 99,97 % stammt aus **Gerätemonitoring**, nicht aus Zählerdaten. Der Feldversuch war freiwillig. Die Pflicht (Dynamic Exports Regulations) kam danach. |
| 8 | DNV/SPE 2025: gezielte Kompromittierung von 3 GW mit „significant implications“; Solarman 195 GW (Bitdefender 2024) (04) | **BESTÄTIGT** | SPE-Pressemitteilung 29.4.2025; SecurityWeek 8.8.2024 | 3 GW: wörtlich. „Over a dozen … manufacturers control significantly more than 3 GW“. 195 GW: laut SecurityWeek für die Plattformen von Solarman **und** Deye, „roughly 20 % of the global solar power production“. Bitdefender meldete die Schwachstellen am 22.5.2024, gepatcht bis Juli 2024. Gefunden wurden Schwachstellen. Ein Einbruch („kam in die Plattform“) ist nicht belegt. |
| 9a | NISG 2026 gilt ab 1.10.2026 (04) | **BESTÄTIGT** | RIS, NISG 2026, BGBl. I 94/2025, Inkrafttretensdatum 01.10.2026 | „1.1.2026“ steht in keiner der Dateien und wäre falsch. |
| 9b | CRA: Meldepflichten ab 11.9.2026, volle Pflichten ab 11.12.2027 (04) | **BESTÄTIGT** | EU-Kommission, CRA-Seite | In Kraft seit 10.12.2024. |
| 9c | RED DA 2022/30: Aufhebung durch DelVO 2026/339 mit Wirkung 11.12.2027 (04) | **BESTÄTIGT** | EU-Kommission, RED-Seite | Annahme 16.2.2026, ABl. 29.4.2026, Wirkung ab 11.12.2027. |
| 10 | LoRaWAN EU868: Unterband 869,4–869,65 MHz mit 10 % Duty Cycle und 500 mW; Nutzlast DR0–2 51 Byte, DR3 115 Byte (03) | **BESTÄTIGT** (mit Hinweis) | TTN „Regional limitations of RF use“ (Unterband P); TTN EU868 Regional Parameters (Tabelle M/N) | 500 mW ist ERP nach ETSI/ERC für das Unterband. Der LoRaWAN-Default für EU868 ist Max. EIRP +16 dBm. 51/115 Byte sind die Anwendungsnutzlast N (ohne FOpts). |

---

## Details

### 1. TOR Typ A: Welche Version gilt, was steht wo

**Versionen** (TOR SEA Typ A V1.4, Versionstabelle S. 2):

- V1.3: veröffentlicht 10.6.2024, gültig ab 1.7.2024.
- V1.4: veröffentlicht 1.6.2026, gültig ab 1.6.2026.
- Änderungsvermerk zu V1.4: „Anpassung des Kapitels 5.4 bezüglich der Ansteuerbarkeit von
  Stromerzeugungsanlagen gemäß § 76 ElWG“.

Heute gilt **V1.4**. 05 stützt sich auf die abgelöste V1.3 [Q20]. Die V1.4 markiert 05 als
[unbestätigt], sie ist aber bestätigt.

**V1.4 enthält beide Anforderungen nebeneinander:**

- **5.4.1.1 Fähigkeit zur Wirkleistungsbeendigung** (S. 34): Eingangsport, „die Wirkleistungsabgabe innerhalb
  von 5 Sekunden zu beenden“. „Der Netzbetreiber greift nicht in die Steuerung … ein.“ Nach Kap. 6.2.1 (S. 40)
  ist der Eingangsport „falls vom relevanten Netzbetreiber im Netzanschlussvertrag vorgesehen, in Form von
  potentialfreien Kontakten zu realisieren“ (z. B. Funkrundsteuerempfänger, Gateway).
- **5.4.1.2 Signalgebung der netzwirksamen Leistung am Netzanschlusspunkt** (S. 34–35), neu in V1.4:
  - „Für die Ansteuerbarkeit … gemäß § 76 Abs. 1 ElWG muss die Stromerzeugungsanlage … über eine
    standardisierte, digitale Schnittstelle verfügen.“
  - Voraussetzungen: Internetanbindung sowie Mess- und Regeleinrichtung am Netzanschlusspunkt.
  - Protokoll: „Protokoll des Kommunikationsstandards OpenADR. Eine Kommunikation über Drittsysteme ist nicht
    vorgesehen.“
  - Sollwert „innerhalb von einer Minute zu erreichen“.
  - Fall-Back: „bei einem Kommunikationsausfall eine begrenzte netzwirksame Leistung in Einspeiserichtung
    (vertraglich vereinbart bzw. bei Photovoltaik 70 % der Modulspitzenleistung gemäß § 101 Abs. 2 ElWG)“.
  - Das Protokoll wird „auf Basis des IEC Standards (IEC 62746-10-1) in Hinblick auf die österreichischen
    Anforderungen durch die Netzbetreiber standardisiert“.
  - Fn. 25: „bis spätestens zum 31.10.2026 zu spezifizieren, sowie der E-Control vorzulegen. Das OpenADR
    Protokoll wird bis zum 31.12.2026 veröffentlicht.“
- **Speicher, Fall 1** (S. 38) steht unverändert in V1.4: „wird bei derzeitigem Stand davon ausgegangen, dass
  die Speicher nicht ins Netz rückspeisen“.

**Auflösung des Widerspruchs:** 01 und 05 beschreiben jeweils einen Teil derselben TOR. Die Aussage in 05
„einzige verpflichtende Schnittstelle ist ein Kontakteingang“ stimmt seit 1.6.2026 nicht mehr. Die Aussage
„kein Lade-/Entlade-Sollwert für Speicher“ bleibt richtig. Der OpenADR-Sollwert gilt für die netzwirksame
Leistung am Netzanschlusspunkt, nicht für den Speicher. Der Fallback betrifft nur die Einspeiserichtung.

**§ 76 ElWG** (BGBl. I 91/2025, S. 60–61):

- **Abs. 1:** „Betreiber von neuen und wesentlich geänderten Stromerzeugungsanlagen mit einer netzwirksamen
  Leistung ab 3,68 kW sind ab dem 1. Juni 2026 verpflichtet, ihre Anlagen mit einer technischen Einrichtung
  zur Steuerbarkeit auszustatten. Die technische Einrichtung hat über eine in den [TOR] näher zu definierende
  standardisierte Schnittstelle zu verfügen.“ Die Kosten trägt der Betreiber.
- **Abs. 2:** Fristen für den VNB:
  - 1.6.2028 für > 25 kW
  - 1.6.2029 für > 3,68–25 kW
  - 1.1.2030 für > 0,8–3,68 kW auf Verlangen

  „nachweislich im Betrieb erreichen und erfolgreich Steuerbefehle umsetzen“. Pönale 100 € je angefangenem
  Verzugsjahr, kostenmindernd nach § 134.
- **Abs. 3:** Der VNB gibt die netzwirksame Leistung am Anschlusspunkt vor. „Einbindung von Speichern hinter
  dem Zählpunkt“ ist davon nicht betroffen.

Die Angaben in 01 stimmen. § 76 selbst nennt kein Protokoll, OpenADR kommt erst aus der TOR.

**Neuer Hinweis zur OpenADR-Version:** Netz Oberösterreich hat am 4.3.2026 beim OpenADR-Workshop in Arnhem
„Digital Customer Interface Austria – OpenADR 3.1“ vorgestellt
(https://www.openadr.org/assets/14_Austria%20NetzOOE_gridoo%20openADR%20Workshop%20Arnhem%2005_03_2026.pdf).
Die Folien nennen als Ziele dynamische Exportgrenzen, flexible Netzanschlüsse und dynamische
Betriebshüllkurven. Die Marktkommunikation ist „under discussion“. Als nächster Schritt steht dort
„Standardizing OpenADR 3.1 for Austrian Use Cases“. Die TOR verweist dagegen auf IEC 62746-10-1, und diese
Norm beruht auf OpenADR 2.0b. Laut 03 unterscheiden sich 2.0b und 3.x deutlich in der Security: 2.0b nutzt
X.509 mit TLS 1.2, 3.0 nutzt OAuth2 mit TLS. Welche Version das AT-Profil nutzt, ist eine **offene Frage an
Smart Grids Austria**. Eine veröffentlichte AT-Spezifikation haben wir bis 23.10.2026 nicht gefunden.

### 2. SNE-G-V (BGBl. II 299/2026, ausgegeben 12.10.2026)

- **§ 10 Abs. 2 Z 2** (S. 6):
  - Wortlaut: „die netzwirksame Leistung gänzlich oder zu einem vereinbarten Anteil, der zumindest 4 kW
    beträgt, um bis zu 100 % einzuschränken“.
  - NE 1–5: dynamisch bis 6 Uhr des Vortags, zwei Zeiträume von „jeweils **bis zu** zwei Stunden“.
  - NE 6–7: statisch oder (auf Verlangen, wenn technisch unterstützt) dynamisch, „zwei Zeiträume von jeweils
    zwei Stunden täglich“.
  - NE 7: Es verbleiben mindestens 4 kW.
  - Abs. 3: Viertelstundenleistungswerte. Abs. 5: zehn Jahre.
- **§ 32 Abs. 5** (S. 13): Netzbetreiber schließen Vereinbarungen nach § 10 Abs. 2 Z 2 „umgehend und
  spätestens ab 1. Oktober 2027“ ab. Bestätigt.
- **§ 23** (S. 11): Befreiung „wenn die Energiespeicheranlage als systemdienlicher Speicher gemäß den §§ 24 bis
  26 und **ausschließlich zur Wiedereinspeisung** betrieben wird“. Diese Bedingung fehlt in 01.
- **§ 24 Abs. 1** (S. 11), Voraussetzungen:
  - Z 1: Der Netzbetreiber erhält „vertraglich das Recht und die technische Möglichkeit …, den zulässigen
    Betriebsbereich in beide Energierichtungen innerhalb definierter Grenzen … unentgeltlich einzuschränken“.
    Bestätigt.
  - Z 2: UW der NE 4 mit PV-Verhältnisleistung > 0,3 MW/MVA **oder** Wind > 0,85 MW/MVA, **und**
    Rückspeisedauer > 2 500 h.
  - Z 3: Nutzung der Anschlusskapazitäten nach § 99 Abs. 3 ElWG.
  - Z 4: ≥ 1 MW.
- **§ 24 Abs. 3:** Bündelung von Anlagen mit „zumindest jeweils 10 kW“, „messtechnisch geeignet erfasst“, am
  selben UW, durch „technische Aggregation“. Bestätigt. Die Verordnung spricht von Energiespeicheranlagen,
  nicht ausdrücklich von Heimspeichern.
- **§ 26** (S. 12): Abs. 1: Einschränkungsrahmen stündlich je Monat für fünf Jahre, Vorgabe täglich bis 6 Uhr
  des Vortags. Abs. 3: 5 GW für ganz Österreich. Abs. 8: höchstens 20 Jahre. Bestätigt.
- **§ 32 Abs. 1:** in Kraft 1.1.2027. **§ 33 Abs. 1:** §§ 23–26 treten mit Ablauf des 31.12.2030 außer Kraft
  und gelten für vorher in Betrieb genommene Speicher weiter. Bestätigt.

Folge für den Pitch: Der „systemdienliche Speicher“ ist auf netzgekoppelte Speicher zugeschnitten, die nur
aus dem Netz laden und wieder einspeisen. Für den typischen PV-Heimspeicher hinter dem Zähler ist die
Befreiung so nicht nutzbar. Das ist eher ein Argument für eine **eigene Kategorie „Heimspeicher
netzdienlich“** als ein fertiges Vorbild.

### 3. § 14a EnWG (BNetzA)

- Quelle: https://www.bundesnetzagentur.de/DE/Vportal/Energie/SteuerbareVBE/start.html
- Dimmen: „auf bis zu 4,2 kW“, Mindestleistung 4,2 kW.
- Speicher: „hinsichtlich der Strombezugsrichtung ebenfalls … steuerbare Verbrauchseinrichtungen“.
- Einspeisung: „allein Regelungen für die Stromentnahme aus dem Netz und nicht für die Einspeisung“.
- Modul 1: „zwischen 110 und 190 Euro im Jahr (Stand 2023)“.
- Modul 2: Arbeitspreis „auf 40 Prozent“, eigener Zähler, nicht mit Modul 1 kombinierbar.
- Modul 3: nur zusammen mit Modul 1.

Die Angaben in 01 stimmen. Nicht geprüft: die Sonderregel für Mindestleistungen größerer Wärmepumpen bzw.
Klimaanlagen bei EMS-Steuerung in der Festlegung BK6-22-300.

### 4. ACM capaciteitssturingscontract

- Quelle: ACM/25/196733, „ACM publiceert codebesluit capaciteitssturingscontract“. Beschluss 11.12.2025,
  Publikation 12.12.2025.
- Netzbetreiber können mit Anschlussnehmern vereinbaren, das Netz „in de tegengestelde richting van de
  congestie“ zu nutzen. Beispiel: Rückspeisung aus eigener Erzeugung oder Batterie bei Verbrauchsengpass,
  „tegen een vergoeding“.
- Kein Inkrafttretensdatum und keine Angabe zu Kleinverbrauchern auf der Seite. Der Vermerk [unbestätigt] in
  01 zu Haushalten bleibt richtig.

### 5. BMWi-Verteilernetzstudie

PDF-S. 12, Zusammenfassung: „Es reicht eine Abregelung der jährlichen Einspeisung dieser EE-Anlagen von 1 %
aus, um den Netzausbaubedarf um ca. 30 % zu senken. Eine Abregelung von 3 % der Jahresenergie würde
ausreichen, um mehr als 40 % des Netzausbaus einzusparen.“ „Dieser EE-Anlagen“ meint Wind und PV, und nur in
Netzen mit Ausbaubedarf. Außerdem: Die Gesamtkosten sinken um mindestens 15 %.

### 6. Project Symphony

Final Report (https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf):

- PDF-S. 53: „From a small sample size of 8 NSS calls, data from testing highlights that non-compliance was
  experienced in 26.6% of NSS intervals.“ Konform heißt „within 95% of the NSS deployment signal“.
- PDF-S. 59: „Of the 911 assets recruited, 714 were orchestrated“. Auf PDF-S. 43 heißt es dagegen „assets
  orchestrated (715)“, der Bericht ist also selbst inkonsistent.
- PDF-S. 60: „32 different rooftop solar PV and battery storage inverter models across 7 manufacturers“. Je
  Kunde wurde ein Gateway installiert, dazu kamen Firmware-Patches, teils neue Wechselrichter und mehrere
  Hausbesuche.

### 7. SAPN Flexible Exports (Final Report v1.3, 19.10.2023)

- S. 4: „more than 95% of equipment by market share being Flexible Exports capable“ nach „new regulations in
  South Australia“. Wahl der flexiblen Option von 36 % (Trial) auf über 85 % (BAU).
- S. 11: „Any flexible export system will fall back to the 1.5kW export limit in the event of a communication
  outage“. An anderer Stelle: 1,5 kW je Phase.
- S. 45: Constraint Engine 99,6 % Verfügbarkeit bei Tageslicht, Utility Server 97,8 %, Wechselrichter
  „able to communicate 89.3% of the time“, bezogen auf die Tageslicht-Betriebszeit der Constraint Engine.
- PDF-S. 47: „Analysis of device monitoring data indicated that flexible export limits were adhered to for more
  than 99.97% of 5-minute intervals.“ Rund 15 % der Anlagen hatten Überschreitungen > 250 W, laut SAPN
  Messartefakte.

### 8. DNV/SPE und Bitdefender

- SPE, 29.4.2025: „a targeted compromise of 3 GW of generation capacity can have significant implications for
  Europe's power grid“. „Over a dozen Western and non-Western manufacturers control significantly more than
  3 GW“. Risikobereiche: 3 kritisch, 6 hoch, 5 mittel.
- SecurityWeek, 8.8.2024: Solarman- und Deye-Plattformen betreiben „millions of solar installations
  worldwide, generating 195 GW, or roughly 20% of the global solar power production“. Weitere Berichte:
  Solarman-Plattform mit > 2 Mio. Anlagen. Meldung an die Hersteller am 22.5.2024, gepatcht bis Juli 2024.
- Präzisierung zu 04 („kam in die Solarman-Plattform“): Bitdefender fand Schwachstellen, die eine
  Kontoübernahme ermöglicht hätten. Eine tatsächliche Kompromittierung wurde nicht berichtet.

### 9. NISG 2026, CRA, RED DA

- NISG 2026: RIS-Kopf „Inkrafttretensdatum 01.10.2026“, BGBl. I Nr. 94/2025. 1.10.2026 ist richtig. Der
  Vermerk „[unbestätigt, Datum im RIS prüfen]“ in 04 kann entfallen.
- CRA (EU-Kommission): „entered into force on 10 December 2024“, „reporting obligations to apply as of
  11 September 2026“, „main obligations … will apply from 11 December 2027“.
- RED (EU-Kommission): DelVO 2022/30 „entered into application in August 2025“. Am 16.2.2026 wurde die
  Aufhebung angenommen (DelVO (EU) 2026/339, ABl. 29.4.2026), „effective as of 11 December 2027“.

### 10. LoRaWAN EU868

- TTN „Regional limitations of RF use“: „P (869.4 MHz – 869.65 MHz): 10%, 500 mW ERP“. Die übrigen Unterbänder
  haben 0,1–1 % bei 25 mW.
- TTN EU868 Regional Parameters: N = 51 Byte (DR0–2), 115 Byte (DR3), 222 Byte (DR4–7). RX2-Default
  869,525 MHz mit DR0. Max. EIRP +16 dBm.
- Hinweis: 500 mW ist der regulatorische Rahmen des Unterbands. Ob ein Gateway ihn ausschöpft, hängt von
  Gerät und Netzbetreiber ab. Den Unterband-P-Downlink teilen sich alle RX2-Antworten (Join-Accept, ACKs)
  eines Gateways.

---

## Weitere Widersprüche zwischen 01–05

1. **05 Kernaussage 3 vs. TOR 1.4 (01):** 05 schreibt, ein sicheres Rückfallverhalten sei „kein gemeinsames
   Merkmal, ein Pflichtprofil müsste es vorschreiben“. In AT schreibt TOR V1.4 einen Fallback bereits vor,
   allerdings nur am Netzanschlusspunkt und nur in Einspeiserichtung. Das gehört in 05 ergänzt.
2. **05 „Reaktionszeiten“ und Offene Frage 4 vs. 01:** 05 schreibt „normativ gibt es nur 5 s Aus, für Sollwerte
   gibt es nichts“. TOR 1.4 verlangt den Sollwert der netzwirksamen Leistung in 1 Minute. Speicherspezifisch
   gibt es tatsächlich nichts.
3. **03 Empfehlung vs. TOR 1.4 (01):** 03 empfiehlt LoRaWAN-Multicast als Primärkanal und als Alternative
   REST „an Standort oder Hersteller-Cloud“. TOR 1.4 legt OpenADR über das Kundeninternet fest, „eine
   Kommunikation über Drittsysteme ist nicht vorgesehen“. Ein Cloud-Pfad wäre in AT nicht TOR-konform. LoRaWAN
   wäre ein zusätzlicher Kanal neben OpenADR. 03 sollte das als Abweichung bzw. Ergänzung zur TOR
   kennzeichnen.
4. **03 Offene Frage 8 vs. 01:** 03 fragt, ob das ElWG eine Pflicht-Steuerschnittstelle vorschreiben soll.
   Laut 01 tut § 76 das schon für Erzeugungsanlagen. Offen ist nur die Ausweitung auf Speicher mit Sollwert.
5. **03 Kernaussage 3 vs. 05/Quelle:** 03 nennt den SAPN-Feldversuch ein „Pflichtprofil über das
   Kundeninternet“. Der Feldversuch war freiwillig (36 % wählten die flexible Option), die Pflicht kam erst
   danach. 05 stellt das richtig dar.
6. **SAPN-Fallback 5 kW (02) vs. 1,5 kW (03/05):** Das ist kein Sachwiderspruch, es sind zwei Projekte. 02
   beschreibt das Advanced-VPP-Projekt mit Tesla (2019–2021, 5 kW), 03/05 beschreiben Flexible Exports (2023,
   1,5 kW je Phase). Im Pitch immer das Projekt nennen.
7. **SAPN 99,4 % (05) vs. > 99,97 % (03):** Beide Zahlen stimmen, messen aber Verschiedenes. 99,4 % ist der
   Zeitanteil, in dem 10 kW bzw. Anlagenleistung exportiert werden konnten. 99,97 % ist der Anteil der
   5-min-Intervalle, in denen die Grenze eingehalten wurde.
8. **Smart-Meter-Verifikation „in Echtzeit“ (01, 04) vs. 03:**
   - 01 sieht den Mehrwert in „feinerer Auflösung und Echtzeit-Prüfung“.
   - 04 Kernaussage 8 nennt die Smart-Meter-Verifikation einen unabhängigen Sicherheitsmechanismus.
   - 03 zeigt: Die Kundenschnittstelle (1–5 s) ist gegenüber dem Kunden nicht manipulationssicher, weil er den
     Schlüssel kennt. Unabhängig sind nur die Backend-Werte, und die kommen in Wien einmal täglich.

   Echtzeit und Unabhängigkeit gibt es mit heutiger AT-Infrastruktur also nicht gleichzeitig. 01 und 04 sollten
   das einschränken.
9. **03 Kernaussage 5 vs. Kernaussage 6:** Die Durchsatzrechnung (≈ 1 000 Befehle/h, SF9, ~40–53 Byte) enthält
   keine Signatur. Kernaussage 6 verlangt aber 64 Byte Signatur. Ein signierter Befehl mit ca. 104 Byte
   Nutzlast plus 13 Byte LoRaWAN-Overhead dauert bei SF9/125 kHz rund 0,64 s. Das ergibt etwa **560 Befehle/h**
   im 10-%-Unterband [eigene Rechnung, Semtech-Formel, CR 4/5]. 03 sollte die Zahl anpassen.
10. **04 Krypto-Annahme vs. 03:** 04 lässt offen, ob ECDSA P-256 in LoRaWAN-Nutzlasten passt. 03 beantwortet
    das: erst ab DR3 (115 Byte), nicht bei DR0–2. 04 kann den Vermerk auflösen.
11. **01 Kernaussage 3 intern:** „seit 12.10.2026 eine Tarifgrundlage“ passt nicht zu „gilt ab 1.1.2027“.
    Richtig ist: kundgemacht am 12.10.2026, wirksam ab 1.1.2027.
12. **01 SNE-G-V „Heimspeicher ab 10 kW bündelbar“ vs. Grundannahme in 02/05:** 02 und 05 gehen vom
    PV-Heimspeicher zur Eigenverbrauchsoptimierung aus. § 23 SNE-G-V verlangt aber „ausschließlich zur
    Wiedereinspeisung“. 01 Bedeutung Nr. 5 und Nr. 7 stellen die Befreiung deshalb zu breit als Kundenanreiz
    dar.
13. **03 vs. 05 zur Rundsteuerung in AT:** 03 fragt, ob Rundsteuerempfänger in den TOR gefordert sind. 05 hat die
    Antwort: TOR Kap. 6.2.1 verlangt potentialfreie Kontakte am Fernwirkgerät, z. B. einem
    Funkrundsteuerempfänger, „falls im Netzanschlussvertrag vorgesehen“. Eine generelle Pflicht ist das nicht.
14. **02 Symphony 714 vs. Quelle 715:** Die Inkonsistenz steckt in der Quelle selbst (PDF-S. 43 vs. 59). 714 ist
    korrekt zitiert, die Abweichung sollte vermerkt werden.
15. **OpenADR-Version (01/03) vs. Netz OÖ:** Die TOR verweist auf IEC 62746-10-1, also OpenADR 2.0b. Netz OÖ
    arbeitet mit OpenADR 3.1. In 01 und 03 fehlt dieser Hinweis. Das gehört als offene Frage zu Smart Grids
    Austria.

---

## Nötige Korrekturen in 01–05 (Kurzliste)

- **01**
  - Kernaussage 3: „seit 12.10.2026 kundgemacht, gilt ab 1.1.2027“.
  - SNE-G-V-Abschnitt und Bedeutung Nr. 5/7: Bedingung „ausschließlich zur Wiedereinspeisung“ (§ 23)
    ergänzen; Standortkriterium um „oder Wind > 0,85 MW/MVA“ ergänzen; Befreiung als Anreiz für Heimspeicher
    relativieren.
  - TOR-Abschnitt: Fallback „nur Einspeiserichtung“. Hinweis OpenADR 2.0b (IEC 62746-10-1) vs. 3.1 (Netz OÖ)
    als offene Frage.
  - BMWi-Zeile: „3 % der Jahresenergie von Wind/PV in Netzen mit Ausbaubedarf“.
  - Bedeutung Nr. 2: „Echtzeit-Prüfung“ einschränken (siehe 03).
- **02**
  - Symphony: Hinweis, dass der Bericht auch 715 nennt.
  - SAPN: Fallback 5 kW klar dem Advanced-VPP-Projekt zuordnen.
- **03**
  - Kernaussage 3: „Feldversuch (freiwillig), Pflicht erst danach“; Fallback „1,5 kW je Phase“; 99,97 % aus
    Gerätemonitoring.
  - Kernaussage 5 und Durchsatzrechnung: mit Signatur ca. 560 statt ca. 1 000 Befehle/h.
  - Empfehlung: Abweichung von TOR 1.4 kennzeichnen (OpenADR, keine Drittsysteme).
  - Offene Frage 8 umformulieren: Ausweitung von § 76 auf Speicher.
  - Bei 500 mW den Zusatz „ERP nach ETSI, LoRaWAN-Default 16 dBm EIRP“.
- **04**
  - Bitdefender: „fand Schwachstellen in der Solarman-Plattform (mit Deye ca. 195 GW, > 2 Mio. Anlagen)“ statt
    „kam in die Plattform“.
  - NISG-Vermerk [unbestätigt] streichen, Datum ist im RIS bestätigt.
  - Kernaussage 8: Unabhängigkeit gilt nur für Backend-Werte, die erst am Folgetag vorliegen.
  - Krypto-Vermerk: „passt ab DR3“.
- **05**
  - Kernaussage 5, Reaktionszeit-Tabelle, Pflichtschnittstellen-Tabelle Zeile AT und Offene Fragen 3/4 auf TOR
    V1.4 umstellen: 5.4.1.1 (5 s, Kontakte nur falls vertraglich vorgesehen) **plus** 5.4.1.2 (OpenADR,
    Sollwert am Netzanschlusspunkt in 1 min, Fallback Einspeisung).
  - Seitenzahlen nach V1.4: 5.4.1 S. 34, Fall 1 S. 38, 6.2.1 S. 40.
  - „V1.4 ab 01.06.2026 [unbestätigt]“ → bestätigt.
  - Kernaussage 3: auf die AT-Fallback-Pflicht hinweisen.
  - Weiter richtig: kein speicherspezifischer Lade-/Entlade-Sollwert; Fall 1 „keine Rückspeisung“ gilt auch in
    V1.4.

## Quellen der Querprüfung

- TOR Stromerzeugungsanlagen Typ A V1.4 (E-Control), Link wie in 01 [TOR-A-1.4]
- ElWG, BGBl. I 91/2025: https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2025_I_91/BGBLA_2025_I_91.pdf
- SNE-G-V, BGBl. II 299/2026: https://www.ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2026_II_299/BGBLA_2026_II_299.pdf
- Netz OÖ, Digital Customer Interface Austria – OpenADR 3.1 (4.3.2026): https://www.openadr.org/assets/14_Austria%20NetzOOE_gridoo%20openADR%20Workshop%20Arnhem%2005_03_2026.pdf
- BNetzA § 14a: https://www.bundesnetzagentur.de/DE/Vportal/Energie/SteuerbareVBE/start.html
- ACM/25/196733: https://www.acm.nl/nl/node/28583
- BMWi-Verteilernetzstudie: https://www.offis.de/fileadmin/content/files/download_tools/roadmaps_und_studien/BMWi_Verteilernetzstudie.pdf
- Project Symphony Final Report: https://arena.gov.au/assets/2024/06/Western-Power-Project-Symphony-Pilot-Results-and-Recommendations.pdf
- SAPN Flexible Exports Final Report: https://arena.gov.au/assets/2024/01/SA-Power-Networks-Flexible-Exports-for-Solar-PV-Trial-Final-Report.pdf
- SolarPower Europe, 29.4.2025: https://www.solarpowereurope.org/press-releases/new-report-solar-sector-proposes-solutions-to-mitigate-critical-cybersecurity-risks
- SecurityWeek, 8.8.2024: https://www.securityweek.com/vulnerabilities-exposed-widely-used-solar-power-systems-to-hacking-disruption/
- RIS NISG 2026: https://ris.bka.gv.at/Dokumente/Bundesnormen/NOR40277627/NOR40277627.pdf
- EU-Kommission CRA: https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act
- EU-Kommission RED: https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en
- TTN Regional limitations: https://www.thethingsnetwork.org/docs/lorawan/regional-limitations-of-rf-use/
- TTN EU868: https://www.thethingsnetwork.org/docs/lorawan/regional-parameters/eu868/
