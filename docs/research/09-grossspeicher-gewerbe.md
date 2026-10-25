# 09 – Gewerbe- und Großspeicher (100 kW bis >10 MW): Regeln, Akteure, Daten Steyr/OÖ

Stand: 25.10.2026 (Schnellrecherche, ca. 30 min). Alle Webquellen am 25.10.2026 abgerufen.
"unbestätigt" heißt: nicht in einer Primärquelle (Gesetzestext, APG-/E-Control-/Netz-OÖ-Dokument) geprüft, sondern aus Sekundärquellen oder Fachwissen.

---

## 1. Regeln in Österreich

### 1.1 Netzebenen und Anschluss (Faustregeln)

| Leistung (grob) | Typische Netzebene | Anmerkung |
|---|---|---|
| bis ca. 100–400 kW | NE 7 (Niederspannung 0,4 kV) bzw. NE 6 (Trafo-Sammelschiene) | Ab ca. 100 kW oft eigener Trafoabgang. Ob NE 7 oder NE 6, entscheidet der VNB im Einzelfall (unbestätigt) |
| ca. 0,4–10 MW | NE 5 (Mittelspannung, 30 kV / 10–20 kV) bzw. NE 4 (UW-Sammelschiene MS) | Eigene Übergabestation, Schutz und Fernwirktechnik nötig (unbestätigt für Netz OÖ) |
| > ca. 10–20 MW | NE 4 / NE 3 (110 kV) | Anschluss im Umspannwerk |

- Die freien Einspeisekapazitäten je Umspannwerk (NE 4) veröffentlichen die VNB gemeinsam, gemäß § 20 ElWOG. Die Karte und eine Tabelle liegen auf **ebUtilities** und werden quartalsweise aktualisiert. Sie gibt nur eine erste Orientierung und ersetzt kein Anschlussbegehren. Quelle: Oesterreichs Energie PA 04.08.2023, https://oesterreichsenergie.at/fileadmin/user_upload/20230804_PA_Netzkapazit%C3%A4ten.pdf. WKO OÖ zeigt die Auslastung der OÖ-Umspannwerke (Stand 10/2025, Daten von ebutilities.at): https://www.wko.at/ooe/umwelt-energie/energieinfrastruktur-oberoesterreich
- Eine eigene „Netzkapazitätskarte“-Seite von Netz OÖ wurde nicht gefunden. Die Daten für OÖ laufen über ebUtilities (unbestätigt, ob Netz OÖ zusätzlich eine eigene Seite hat).

### 1.2 TOR Erzeuger und RfG-Typen (gelten auch für Speicher im Einspeisebetrieb)

- **Typ A:** 0,8 kW bis < 250 kW. **Typ B:** 250 kW bis < 35 MW. **Typ C:** 35 bis < 50 MW. **Typ D:** ≥ 50 MW oder Anschluss ≥ 110 kV.
- Rechtsgrundlage ist die RfG-Schwellenwert-V, BGBl. II Nr. 96/2024 (ursprünglich BGBl. II 55/2019). Die TOR erlässt E-Control, die Fassung auf der E-Control-Seite ist die authentische.
- Die **TOR Erzeuger Typ B V1.4** (gültig ab 01.06.2026 laut Versionstabelle) enthält einen Abschnitt „Anwendung auf Speicher“. Wie die Speicherleistung auf die Schwellen angerechnet wird, ist nicht geprüft (unbestätigt). Für die meisten Gewerbespeicher von 250 kW bis 10 MW gilt damit **Typ B**.
- Bei Speichern ist zusätzlich der Bezug als Verbraucher zu regeln, dafür gelten die Netzbetreiber-TAB bzw. TOR Verbraucher (unbestätigt).
- Quellen:
  - OE-Erläuterungsdokument NC RfG: https://oesterreichsenergie.at/fileadmin/user_upload/Oesterreichs_Energie/Publikationsdatenbank/Diverses/2022/20220113_Erl%C3%A4uterungsdokument_NC_RfG_TOR_Erzeuger_OE_design.pdf
  - E-Control TOR Typ A: https://www.e-control.at/documents/1785851/1811582/TOR+Erzeuger+Typ+A+V1.2.pdf
  - TOR Typ B (Vorarlberg Netz): https://www.vorarlbergnetz.at/media/TOR-Erzeuger-Typ-B-V1.2.pdf
  - BGBl. II 55/2019: https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2019_II_55/BGBLA_2019_II_55.pdf

### 1.3 Netzzugang und Anschlussprozess (Kurzfassung)

1. Anschlussanfrage oder -begehren beim VNB (Netz OÖ, im Stadtgebiet Steyr ggf. Stadtbetriebe Steyr; die Zuständigkeit je Adresse ist nicht geprüft).
2. Netzverträglichkeitsprüfung, danach das Angebot mit Anschlusspunkt und Netzebene.
3. Netzzugangs- und Netzanschlussvertrag, Netzbereitstellungs- bzw. Anschlussentgelt.
4. Errichtung, Schutzprüfung, TOR-Konformitätsnachweis (Typ B: Anlagenzertifikat/Einheitenzertifikate, unbestätigt), Inbetriebnahme.
5. Zählpunkte für Bezug und Einspeisung, Zuordnung zu Bilanzgruppe(n).

Unter dem **ElWG** wird das einmalige Netzanschlussentgelt in EUR/kW netzwirksamer Leistung bemessen (Quelle: Seminarfolien Energie NÖ, siehe 1.4).

### 1.4 ElWG (Elektrizitätswirtschaftsgesetz) – Stand

- Der **Nationalrat hat das ElWG im Dezember 2025 beschlossen**, zusammen mit dem EnDG und einer Novelle des E-Control-Gesetzes. Die Regierungsvorlage wurde vorher noch abgeändert, u. a. bei den Netzentgelten für Einspeiser. Quelle: https://mailman3.wu.ac.at/hyperkitty/list/friendsofenergy@wu.ac.at/thread/AKGD2ZGBCR6GBHCSZUCC344RKGYFKUOM/ . Bundesrats-Dokument: https://www.parlament.gv.at/dokument/BR/I-BR/11183/fname_1520866.pdf
- **Speicher-Definition:** Energiespeicheranlagen gelten als Einspeiser **und** Entnehmer (Quelle: Energie-NÖ-Seminarfolien 18.12.2025, https://www.energie-noe.at/download/20251218_ElWG_Online%20Seminar%20Gemeinde.pdf).
- **Flexibler Netzzugang:** Das Recht auf Netzanschluss bleibt bestehen. Als Übergangslösung kann im Verteilnetz ein flexibler Netzzugang gewährt werden. Dabei wird die netzwirksame Leistung je nach Netzebene für **12, 18 oder 24 Monate** beschränkt, wenn das Netz überlastet zu werden droht. Für die **Bezugsseite gibt es keinen temporären flexiblen Netzzugang**. Quelle: wie oben (Energie NÖ, auch https://www.energie-noe.at/download/20251218_ElWG_Online%20Seminar%20WKNOE_Installationsbetriebe.pdf).
- **Systemdienliches Verhalten** soll mit reduzierten Netzentgelten belohnt werden. Das gilt für Erzeugungs-, Verbrauchs- und Speicheranlagen.
- **Inkrafttreten:** Die meisten Bestimmungen gelten ab dem Tag nach Kundmachung. Die Bestimmungen zu den **Systemnutzungsentgelten gelten erst ab 31.12.2026**, die Bürgerenergie-Regeln ab 01.10.2026 (Energie-NÖ-Folien). Die genauen Paragraphen sind nicht im Gesetzestext geprüft (unbestätigt).
- **Netzentgelte für Speicher:** Oesterreichs Energie begrüßte schon zum Entwurf die „Befreiung der Speicher von doppelten Netzentgelten“. Unklar blieb, wann das Kriterium erfüllt ist und was mit Bestandsanlagen passiert. Die AK warnte vor Kosten von ca. 350 Mio. EUR/a. Die **Endfassung für Speicher-Netzentgelte im beschlossenen ElWG ist nicht geprüft (unbestätigt)**, ebenso die Details der künftigen SNE-VO durch E-Control.
  - OE-Presseinfo 24.07.2025: https://oesterreichsenergie.at/fileadmin/user_upload/Oesterreichs_Energie/Presseinformationen/2025/20250724_Presseinformation_OE_zu_ElWG.pdf
  - Stellungnahmen: https://www.parlament.gv.at/dokument/XXVIII/SNME/1357/imfname_1707480.pdf
  - E-Control-Präsentation (Haber, 03/2026): https://www.igwindkraft.at/assets/downloads/260324_prasentationen-23.-branchenplattform/260324_econtrol_alfons-haber.pdf
- **Bisherige Rechtslage nach ElWOG 2010 / EAG** (unbestätigt, aus Fachwissen): Seit EAG 2021 ist für Pumpspeicher und Stromspeicher > 1 MW im Netzebenen-relevanten Bezug **befristet kein Netznutzungs- und Netzverlustentgelt** für eingespeicherte und rückgespeiste Energie vorgesehen (§ 111 Abs. 3 ElWOG idF EAG-Paket). Das muss am Gesetzestext geprüft werden.
- **Abgrenzung DE:** In DE gilt § 118 Abs. 6 EnWG (Befreiung für Inbetriebnahme bis 2029, seit 11/2025 auch Teilbefreiung). Das ist **nicht** auf AT übertragbar. Quelle: https://www.roedl.com/insights/stromspeicherrecht-2025/

### 1.5 Regelreserve bei APG

| Produkt | Mindestgebot | Schrittweite | Max. (unteilbar) | Volumen AT |
|---|---|---|---|---|
| FCR (Primärregelung) | ±1 MW | 1 MW | ±25 MW | ±65 MW (2025), ±75 MW (2026) |
| aFRR (Sekundär) | 1 MW | 1 MW | bis präqual. Leistung | – |
| mFRR (Tertiär) | 1 MW | 1 MW | bis präqual. Leistung | +255 / −195 MW ab 01.05.2026 |

- FCR-Gebote laufen typischerweise ab 7 Tage vor Lieferung bis D−1, 08:00. Der Zuschlag erfolgt nach Merit Order.
- Pooling: Mehrere technische Einheiten können über einen präqualifizierten Regelreserveanbieter als Pool angeboten werden. Präqualifiziert wird je technischer Einheit bzw. Pool, die Unterlagen „Technische Präqualifikation“ liegen auf markt.apg.at. Die Pool-Details für Batterien (z. B. LER-Kriterien/Energiereservoir bei FCR) sind **unbestätigt**.
- Praxisbeispiel OÖ: Der Energie-AG-Speicher Timelkam (5 MW / 14,5 MWh) wird am Regelleistungsmarkt eingesetzt (siehe Abschnitt 3.4).
- Quellen:
  - https://markt.apg.at/en/power-grid/balancing/primary-control/
  - https://markt.apg.at/en/power-grid/balancing/secondary-control/
  - https://markt.apg.at/en/power-grid/balancing/tertiary-control/
  - https://pb1-medien.apg.at/im/dl/pboxx-pixelboxx-19645/RR_Ausschreibungsdetails_1.2_PICASSO.pdf

### 1.6 Redispatch und Flexibilitätsmärkte in AT

- Netzreserve und Redispatch laufen bei APG (§ 23 ElWOG). Heute werden überwiegend Großkraftwerke vertraglich eingesetzt. Die Teilnahme von Speichern am Redispatch über Aggregatoren ist im ElWG als Marktöffnung angelegt (unbestätigt).
- Ein lokaler Flexibilitätsmarkt für VNB ist in AT nur in Pilotprojekten umgesetzt, nicht im Regelbetrieb. Siehe Doku 02-pilotprojekte.md. Ob das ElWG die VNB zur marktbasierten Flexbeschaffung verpflichtet, ist unbestätigt.
- Flexible Netzanschlussverträge (1.4) und systemdienliche Netzentgelte sind derzeit die realistischsten Hebel für „Grid-Serving Storage“ am VNB-Netz.

### 1.7 Steuerbarkeit und Fernwirktechnik

- Für **Netz OÖ wurde keine öffentliche Fernwirk-Spezifikation gefunden** (unbestätigt). Die Vorgaben stehen voraussichtlich in den TAB bzw. im Anschlussangebot.
- Die TOR Typ B fordert eine Schnittstelle zur Wirkleistungsreduktion bzw. -steuerung durch den Netzbetreiber. Bei Typ B/C kommen Blindleistungsvorgaben (Q(U), cos φ) und Fernwirkanbindung hinzu (unbestätigt im Detail).
- Typischer Standard bei deutschen VNB für Erzeuger und Speicher **ab 100 kW**: **IEC 60870-5-104** über ein Netzbetreiber-Gateway, mit Datenpunktlisten nach VDE-AR-N 4110. Beispiele:
  - EWE Netz V4.2 01/2026: https://www.ewe-netz.de/-/media/ewe-netz/downloads/barrierefrei/2026_01_01_anforderung_fernwirktechnik_erzeugungsanlagen_ab_100kw.pdf
  - Pfalzwerke 2026: https://www.pfalzwerke-netz.de/pfalzwerke-netz/downloads/netz-anschliessen/spezifikation_fernwirkkommunikation_2026.pdf
  - RheinNetz: https://www.rheinnetz.de/spezifikation-fernwirktechnische-anbindung-von-kundenuebergabestationen.pdfx
- In AT ist dasselbe Muster plausibel, nämlich 104er Fernwirkung an der Übergabestation (unbestätigt).
- IEC 61850 wird eher stationsintern bzw. zwischen UW und Leitstelle eingesetzt. Für DER gibt es IEC 61850-7-420.

### 1.8 Energiegemeinschaften (kurz)

- EEG (lokal/regional, NE 7–4, reduzierte Netzentgelte bei lokaler Nutzung) und BEG (bundesweit, keine Netzentgeltreduktion), nach EAG und künftig ElWG. Die ElWG-Bürgerenergie-Regeln gelten ab 01.10.2026. Ein Gewerbespeicher kann als Teilnehmer einer EEG eingebunden werden, die Detailregeln sind unbestätigt. Siehe 01-regulierung-finanzierung.md.

---

## 2. Akteure, Rollen und Schnittstellen

| Rolle | Beispiel AT/OÖ | Aufgabe |
|---|---|---|
| Anlagenbetreiber | Gewerbebetrieb (z. B. SKF, ZF in Steyr), Energie AG, Projektierer (NGEN) | Eigentum/Betrieb, Eigenverbrauchsoptimierung, Peak Shaving |
| Direktvermarkter / Aggregator / VPP | z. B. Next Kraftwerke AT, Energie AG, Verbund, oekostrom (unbestätigt je Produkt) | Bündelt Flexibilität, handelt am Day-Ahead/Intraday, bietet Regelreserve über einen präqualifizierten Pool |
| Regelreserveanbieter | präqualifiziert bei APG | Gebot und Erbringung von FCR/aFRR/mFRR |
| BKV / Bilanzgruppe | Lieferant oder Aggregator | Fahrplan, Ausgleichsenergie (APCS ist Bilanzgruppenkoordinator Regelzone APG) |
| ÜNB | APG | Regelreserve, Redispatch, Systemführung |
| VNB | Netz OÖ, ggf. Stadtbetriebe Steyr | Anschluss, TOR/TAB, Fernwirkung, Netzengpässe, flexibler Netzzugang |
| EMS/Leittechnik | Siemens, ABB/Hitachi, Sprecher Automation (Linz), Fronius/Intilion-Integratoren (unbestätigt) | Standort-EMS, RTU, Fernwirkgateway |

**Schnittstellen** (Details in 03-protokolle-kommunikation.md und 05-geraete-schnittstellen.md):
- **VNB ↔ Anlage:** IEC 60870-5-104 (Fernwirkung) und IEC 61850 / 61850-7-420 (DER-Modell).
- **Aggregator ↔ Anlage:** Proprietäre APIs, Modbus TCP/SunSpec, VHPready (DE-Industriestandard für VPP) und OpenADR 3.0 (REST/JSON, Preis- und Lastsignale).
- **Haushalt (nicht Gewerbe-Fokus):** EEBus.
- **Vergleich DE:** Steuerung über das Smart-Meter-Gateway mit CLS-Kanal (§ 14a EnWG, Steuerbox). In AT gibt es kein SMGW-Äquivalent, die Smart Meter nach IMA-VO haben keine CLS-Steuerfunktion.

---

## 3. Offene Datenquellen Steyr/OÖ

### 3.1 OpenStreetMap (Overpass)

Relevante Tags: `landuse=industrial|commercial|retail`, `building=industrial|commercial|warehouse|retail|manufacture`, `power=substation` (+`voltage`, `operator`), `power=plant`+`plant:storage=*`, `power=generator`+`generator:source=battery` bzw. `generator:method=lithium-ion`, `generator:source=solar`.

### 3.2 Testabfrage Steyr (ausgeführt am 25.10.2026, overpass-api.de)

Bounding-Box: S 48.00, W 14.36, N 48.08, E 14.48.

```overpassql
[out:json][timeout:90];
(way["landuse"="industrial"](48.00,14.36,48.08,14.48);relation["landuse"="industrial"](48.00,14.36,48.08,14.48);)->.ind;
(way["landuse"="commercial"](48.00,14.36,48.08,14.48);relation["landuse"="commercial"](48.00,14.36,48.08,14.48);)->.com;
(way["landuse"="retail"](48.00,14.36,48.08,14.48);relation["landuse"="retail"](48.00,14.36,48.08,14.48);)->.ret;
(way["building"~"^(industrial|commercial|warehouse|retail|manufacture)$"](48.00,14.36,48.08,14.48);)->.bld;
(nwr["generator:source"="battery"](48.00,14.36,48.08,14.48);nwr["plant:storage"](48.00,14.36,48.08,14.48);
 nwr["generator:method"="lithium-ion"](48.00,14.36,48.08,14.48);nwr["power"="storage"](48.00,14.36,48.08,14.48);)->.bat;
(nwr["power"="substation"](48.00,14.36,48.08,14.48);)->.sub;
(nwr["generator:source"="solar"](48.00,14.36,48.08,14.48);)->.pv;
.ind out count;.com out count;.ret out count;.bld out count;.bat out count;.sub out count;.pv out count;
```

Hinweis: overpass-api.de antwortet ohne User-Agent-Header mit HTTP 406. Mit `curl -A "<name>"` funktioniert die Abfrage.

**Ergebnis:**

| Objektklasse | Anzahl |
|---|---|
| `landuse=industrial` (Ways) | **35** |
| `landuse=commercial` (Ways) | **91** |
| `landuse=retail` (Ways) | **2** |
| Gebäude industrial/commercial/warehouse/retail/manufacture | **147** (commercial 51, retail 37, industrial 28, manufacture 26, warehouse 5). Zusätzlich tragen 52 der Substation-Objekte selbst ein `building`-Tag (service 30, transformer_tower 15, yes 5, transformer 2) und zählen nicht zu den 147 |
| Batteriespeicher (`generator:source=battery`, `plant:storage`, `power=storage`, `lithium-ion`) | **0** |
| `power=substation` | **70** (13 Nodes, 57 Ways) |
| `generator:source=solar` | **409** (403 Nodes, 6 Ways) |

- **110-kV-Umspannwerke (Netz OÖ) in OSM:** UW Steyr-Nord (way 33066376), UW Steyr-Fischhub (way 33066588), UW Steyr-Ost (way 94159103) sowie ein unbenanntes 110-kV-UW (way 259327225). Die Ortsnetzstationen tragen überwiegend den Operator „Netz Oberösterreich“/„Netz OÖ“. In der Box ist damit **kein Hinweis auf die Stadtbetriebe Steyr als Stromnetzbetreiber**; ob dort ein Teilnetz existiert, ist unbestätigt.
- **Benannte Gewerbe-/Industriegebäude**, Kandidaten für Gewerbespeicher: SKF Kugellager Werk, ZF Steyr, Steyr Automotive (Objekte 21/22/25/47), Steyr Motors, GFM, Eckelt Glas, NKE Austria, ISCAR Austria, Sommerhuber, Brau Union Lager, Fachmarktzentrum Steyr, Taborland, City Point, Bauhaus, OBI.
- **Fazit:** In Steyr sind in OSM keine Batteriespeicher getaggt. Die Speicherstandorte im Demo müssen als synthetisch/angenommen gekennzeichnet werden.
- Hinweis: Das BMW-Motorenwerk liegt v. a. im Stadtteil Hinterberg und reicht teilweise außerhalb der Box. Ob es in OSM als `landuse=industrial` erfasst ist, wurde nicht einzeln geprüft (unbestätigt).

### 3.3 Weitere Datenquellen

- **data.gv.at / Land OÖ DORIS:** Flächenwidmungspläne der Gemeinden (Widmungskategorien B-Betriebsbaugebiet, I-Industriegebiet, G-Gewerbegebiet) sind im DORIS-Viewer einsehbar. Ein Teil ist als WMS/Download verfügbar, Lizenz und Abdeckung für Steyr sind nicht geprüft (unbestätigt). Einstieg: https://www.doris.at bzw. https://www.data.gv.at (Suche „Flächenwidmung Oberösterreich“).
- **Speicher-Register:** Österreich hat **kein öffentliches Marktstammdatenregister** wie DE.
  - Das E-Control-Anlagenregister bzw. der Herkunftsnachweis-Register enthält Erzeuger, ist aber nicht standortgenau öffentlich (unbestätigt).
  - Die OeMAG kennt nur geförderte Anlagen und veröffentlicht keine Standortdaten.
  - Die Speicher-Marktstatistik (BMK/TU Wien „Innovative Energietechnologien – Marktentwicklung“, PV Austria) liefert nur aggregierte Zahlen je Bundesland.
- **Netzkapazitäten:** Verfügbar über ebUtilities (Karte der NE-4-Umspannwerke, § 20 ElWOG, quartalsweise), siehe 1.1.
- **Statistik Austria:** Leistungs- und Strukturstatistik sowie Unternehmensdemografie liegen aggregiert je Bezirk/ÖNACE vor, nicht pro Betrieb. Betriebsliste: WKO-Firmen-A-Z (nicht als Open Data).
- **Typische Lastprofile:**
  - APCS veröffentlicht die österreichischen synthetischen Standardlastprofile (G0–G6, L0–L2, H0), die auf den VDEW/BDEW-Profilen basieren. Download unter https://www.apcs.at (Rubrik Standardlastprofile, Link nicht im Detail geprüft).
  - Die BDEW-G-Profile (G0 allgemein, G1 werktags 8–18, G2 Abendverbrauch, G3 durchlaufend, G4 Läden, G5 Bäckerei, G6 Wochenende) sind gut dokumentiert.
  - Für Industrie über 100.000 kWh/a gilt Lastgangzählung (¼-h), dafür gibt es keine SLP.

### 3.4 Bekannte Großspeicher OÖ (und Referenz)

| Projekt | Ort | Größe | Status | Quelle |
|---|---|---|---|---|
| Energie AG, Kraftwerkspark Timelkam (mit Intilion) | Timelkam (Bez. Vöcklabruck) | ca. 5 MW / 14,5 MWh, ca. 4 Mio. EUR, ohne Förderung, Regelleistungsmarkt | in Betrieb (Meldung 07/2026) | https://www.leadersnet.at/news/102093,groesster-batteriespeicher-oberoesterreichs-ist-ans-netz-gegangen.html ; https://www.tips.at/nachrichten/voecklabruck/wirtschaft-politik/729800-groesster-batteriespeicher-oberoesterreichs-in-timelkam-in-betrieb |
| NGEN Austria, Wagenham | Pischelsdorf am Engelbach (Bez. Braunau) | „Österreichs größte systemdienliche Energiespeicheranlage“; MW/MWh nicht gefunden (unbestätigt) | im Bau, IBN 2026 geplant | https://www.news.at/corporate/ngen-startet-grossprojekt-in-wagenham-eine-der-groessten-energiespeicheranlagen-europas-entsteht-in-oberoesterreich ; https://www.trendingtopics.eu/ngen-baut-in-oberoesterreich-eine-der-groessten-energiespeicheranlagen-europas/ |
| Referenz NÖ: EVN Theiß | Theiß (NÖ) | 70 MW / 140 MWh | Bau/Planung 2026 | https://www.noe.gv.at/noe/Oesterreichs_groesster_Batteriespeicher_wird_von_EVN_in_T.html |

- **Steyr:** Für BMW Steyr, SKF Steyr, Steyr Automotive und ZF wurden **keine öffentlich dokumentierten Batteriespeicher (> 1 MW) gefunden** (unbestätigt, Recherche kurz).
- Ein WKO-OÖ-Folder zu Energieinfrastruktur/Netzen/Speichern (11/2025) fordert den Speicherausbau: https://www.wko.at/ooe/news/folder-energieinfra-netze-speicher-6-seiter-251128-v1.pdf

---

## 4. Konsequenzen für den Hackathon-Prototyp (kurz)

- Gewerbespeicher von 250 kW bis 10 MW sind **RfG-Typ B**, hängen an NE 5/NE 6 und brauchen Fernwirkung (vermutlich IEC 104). Das Demo sollte eine 104/61850-Datenpunktschicht für den VNB andeuten und für den Aggregator eine OpenADR-3- bzw. Modbus-Schicht.
- Der Mehrwert für den VNB liegt im **flexiblen Netzzugang nach ElWG** (zeitweise Leistungsbegrenzung) und in systemdienlichen Netzentgelten. Für den Betreiber kommen Erlöse aus FCR/aFRR (ab 1 MW, poolbar) dazu.
- Als Datenbasis dienen OSM-Gewerbeflächen (35 Industrie- und 91 Gewerbeflächen, 147 Gewerbegebäude), die 110-kV-UW Steyr-Nord, -Ost und -Fischhub sowie die SLP G0–G6. Speicherstandorte sind synthetisch, weil in OSM 0 getaggt sind.

---

## Quellen (alle abgerufen 25.10.2026)

- APG FCR/aFRR/mFRR: https://markt.apg.at/en/power-grid/balancing/primary-control/ · …/secondary-control/ · …/tertiary-control/ · https://pb1-medien.apg.at/im/dl/pboxx-pixelboxx-19645/RR_Ausschreibungsdetails_1.2_PICASSO.pdf
- ElWG-Beschluss: https://mailman3.wu.ac.at/hyperkitty/list/friendsofenergy@wu.ac.at/thread/AKGD2ZGBCR6GBHCSZUCC344RKGYFKUOM/ · https://www.parlament.gv.at/dokument/BR/I-BR/11183/fname_1520866.pdf
- ElWG-Inhalte: https://www.energie-noe.at/download/20251218_ElWG_Online%20Seminar%20Gemeinde.pdf · https://www.energie-noe.at/download/20251218_ElWG_Online%20Seminar%20WKNOE_Installationsbetriebe.pdf · https://www.wko.at/ooe/news/strommarktgesetze
- ElWG-Stellungnahmen/Speicher: https://oesterreichsenergie.at/fileadmin/user_upload/Oesterreichs_Energie/Presseinformationen/2025/20250724_Presseinformation_OE_zu_ElWG.pdf · https://www.parlament.gv.at/dokument/XXVIII/SNME/1357/imfname_1707480.pdf · https://www.igwindkraft.at/assets/downloads/260324_prasentationen-23.-branchenplattform/260324_econtrol_alfons-haber.pdf
- TOR/RfG: https://oesterreichsenergie.at/fileadmin/user_upload/Oesterreichs_Energie/Publikationsdatenbank/Diverses/2022/20220113_Erl%C3%A4uterungsdokument_NC_RfG_TOR_Erzeuger_OE_design.pdf · https://www.e-control.at/documents/1785851/1811582/TOR+Erzeuger+Typ+A+V1.2.pdf · https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2019_II_55/BGBLA_2019_II_55.pdf
- Netzkapazitäten: https://oesterreichsenergie.at/fileadmin/user_upload/20230804_PA_Netzkapazit%C3%A4ten.pdf · https://www.wko.at/ooe/umwelt-energie/energieinfrastruktur-oberoesterreich
- Fernwirk-Referenzen DE: EWE Netz, Pfalzwerke Netz, RheinNetz (URLs in 1.7)
- DE-Vergleich Speicherentgelte: https://www.roedl.com/insights/stromspeicherrecht-2025/
- Großspeicher OÖ: Leadersnet, Tips, news.at, trendingtopics, noe.gv.at, WKO OÖ (URLs in 3.4)
- OSM/Overpass: https://overpass-api.de/api/interpreter (Abfrage siehe 3.2), Daten © OpenStreetMap-Mitwirkende, ODbL
