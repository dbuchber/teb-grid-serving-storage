# Gewerbe- und Großspeicher integrieren: Profil, Simulation, Webseite

Stand: 25.10.2026, Remote-Session auf hetzner. Arbeitsvorschlag, nicht abgenommen.
Grundlagen: `docs/context/profil-v2.md`, `gridsim/`, `docs/context/site/`, Recherche `docs/research/09-grossspeicher-gewerbe.md` (heute, mit Quellen-URLs).
Kennzeichnung wie im Profil: **[extern]** = externe Tatsache mit Quelle, **unbestätigt** = nicht am Primärtext geprüft.

## 0. Kurzfassung

- **Die Challenge verlangt es ausdrücklich** („from small household storage to large storage systems at commercial sites“). Heute deckt das Projekt Gewerbe nur mit einem Satz auf der Präsentation ab („The same call works … at a business site“). Profil v2 und Simulation kennen nur den Haushalt.
- **Kernidee:** Dieselben Prozesse P1–P10 und dieselbe Abrufnachricht gelten für alle Größen. Was sich mit der Größe ändert, sind **Kanal, Vertrag, Verifikation und Netzebene**. Wir führen drei Klassen ein: **H** (Haushalt, NE 7), **G** (Gewerbe hinter dem Zähler, ca. 30–250 kW, NE 7/6) und **M** (Großspeicher ≥ 250 kW, RfG-Typ B, NE 6/5 an der Mittelspannung).
- **Wichtigste Einsicht für den Pitch:** Ein Großspeicher an der Mittelspannung entlastet **nicht** die überlasteten Ortsnetztrafos (unser Hauptbefund: 193 von 257 im Winter 2040), sondern das Mittelspannungsnetz und das Umspannwerk. Haushalts- und Gewerbespeicher wirken im Ortsnetz, Großspeicher eine Ebene höher. Beides ergänzt sich. Beleg in den offenen Daten: Für das **UW Steyr Nord** ist die freie Einspeisekapazität **0** (UW Steyr: 61,96), siehe Abschnitt B1.
- **Gewerbespeicher im Ortsnetz sind ein kleiner Hebel für Winter-Engpässe:** In gridsim liegen 200 PV-Anlagen über 30 kWp (11,7 MWp) an 71 von 257 Stationen. Mit 0,5 kWh je kWp wären das 5,8 MWh Speicher. Sie stehen an 15 von 37 Engpass-Stationen (2030) bzw. 53 von 192 (2040) und decken dort rechnerisch höchstens 0,7 von 7,7 MWh (2030) bzw. 2,7 von 352 MWh (2040) Netto-Bedarf. Im Sommer (Einspeisung) helfen sie mehr: Alle 3 Stationen mit Einspeiseengpass haben eine Gewerbe-PV.
- **Bis 11:30 machbar:** nur Text (Profil-Ergänzung als Tabelle, ein Absatz auf der Webseite, ein Satz im Formular). Simulation und Karte sind Arbeit für nach der Abgabe.

## A. Interoperabilitätsprofil

### A1. Drei Speicherklassen – Vorschlag(v2.1)

| Merkmal | H Haushalt | G Gewerbe hinter dem Zähler | M Großspeicher |
|---|---|---|---|
| Leistung (Richtwert) | bis 30 kW | 30–250 kW | ab 250 kW (bis ca. 10–20 MW im Verteilnetz) |
| RfG-Typ (Einspeisung) **[extern]** | Typ A | Typ A | Typ B (250 kW bis < 35 MW); Typ C/D erst ab 35 bzw. 50 MW |
| Netzebene **[extern, Faustregel, unbestätigt für Netz OÖ]** | NE 7 | NE 7, ab ca. 100 kW eigener Abgang oder NE 6 | NE 6/5 (eigene Übergabestation), große Anlagen NE 4 |
| Wirkt auf | Ortsnetztrafo und Abgang | Ortsnetztrafo und Abgang | MS-Abgang, Umspannwerk, vorgelagertes Netz |
| Steuerung heute | keine (Profil: Box) | wie H; oft Gebäude-EMS | Fernwirkung des VNB an der Übergabestation, i. d. R. IEC 60870-5-104 **[unbestätigt für AT]** |
| Leittechnik | Box ist das EMS | Gebäude-/Standort-EMS, ggf. Box | eigenes Anlagen-EMS / Parkregler, RTU, oft Leitwarte des Betreibers oder Vermarkters |
| Messung | Smart Meter (15 min, Opt-in) | Smart Meter bzw. Lastgangzähler | Lastgangzähler (¼-h) ist Standard; Echtzeitwerte über Fernwirkung |
| Vermarktung | Eigenverbrauch, dynamischer Tarif | Eigenverbrauch, Spitzenlastkappung (Leistungspreis!), selten Pool | Regelreserve (FCR/aFRR/mFRR ab 1 MW, poolbar **[extern]**), Intraday, Arbitrage |
| Vertrag mit dem VNB | Fördervertrag (Stufen 0–3) | Fördervertrag oder einfacher Flexvertrag | Netzzugangsvertrag mit **flexiblem Netzzugang** (ElWG) **[extern]**, bilateraler Flexvertrag |
| Anzahl im Segment | viele (10–100) | wenige (0–3) | einzelne |

### A2. Akteure – Ergänzung zu Profil v2 Abschnitt 1

| Akteur | Rolle bei G/M | Neu oder geändert |
|---|---|---|
| Anlagenbetreiber Gewerbe (z. B. Industriebetrieb) | bestimmt den Betrieb wie der Haushalt, hat aber Leistungspreis- und Produktionsinteressen | Präferenzen werden zu einem **Fahrplan bzw. Flexibilitätsband** (A3, P11) |
| Betreiber bzw. Leitwarte des Großspeichers | nimmt Abrufe entgegen, quittiert, liefert Echtzeitwerte | neu; ersetzt die Box als „digitale Schnittstelle in der Kundenanlage“ |
| Direktvermarkter / Aggregator | bei M fast immer vorhanden (Regelreserve, Intraday) | P8 wird für M der Regelfall, nicht die Ausnahme |
| ÜNB (APG) | präqualifiziert Regelreserve-Pools; betroffen, wenn der VNB einen präqualifizierten Speicher abruft | Koordination nach P8 wird verbindlich (A4) |
| EMS-/Leittechnik-Hersteller | liefert Parkregler und RTU | muss das Abrufobjekt und die harten Grenzen abbilden (A5) |

### A3. Prozesse – was sich je Klasse ändert

Die Ziele von P1–P10 bleiben. Änderungen für G und M:

| Prozess | G Gewerbe | M Großspeicher |
|---|---|---|
| P1 Inbetriebnahme | wie H, Box oder zertifiziertes Gebäude-EMS | Teil des Netzanschlussverfahrens (TOR Typ B, Konformitätsnachweis, Datenpunktliste Fernwirkung) |
| P2 Tagespreise | wie H | entfällt im Profil; Preise kommen über den Markt |
| P3 Testabruf | wie H | einmal bei Inbetriebnahme, danach selten; Quittung und Messung in Echtzeit ersetzen die Statistik |
| P4 Engpassabruf | wie H, Broadcast an das Segment | **Unicast mit Quittung** (Annahme / Ablehnung mit Grund / Teilannahme mit verfügbarer Leistung). Keine Zufallsverzögerung nötig (einzelne Anlage), aber Rampe nach TOR |
| P5 Verifikation | Smart Meter + Referenz-EMS wie H | **Baseline = gemeldeter Fahrplan** (P11) statt kontrafaktischem EMS; Messung aus Lastgangzähler und Fernwirkung |
| P6 Fallback | wie H | Rückfallwert der Fernwirkung (vereinbarter Wert, analog TOR 70 %-Regel) |
| P7 Bilanzgruppe | wie H | Speicher hat oft eigene Bilanzgruppe oder die des Vermarkters; Korrektur direkt mit diesem |
| P8 Drittvermarktung | selten | **Pflichtprozess**: Sperrfenster day-ahead vor Gate Closure der Regelreserve; Entschädigung für entgangene Markterlöse |
| P9 Segmentzuordnung | wie H | Zuordnung zu MS-Abgang und UW statt Ortsnetzstation |
| P10 Schlüssel | wie H | Schlüssel je Anlage, Widerruf über IP-Kanal sofort; IEC 62351 für die Fernwirkung **[unbestätigt]** |

Neu für G und M:

**P11 Flexibilitätsmeldung (day-ahead) – Vorschlag(v2.1)**

| Feld | Inhalt |
|---|---|
| Ziel | Der VNB weiß am Vortag, wie viel Leistung ein Speicher je Viertelstunde in welche Richtung verschieben könnte, und hat eine Baseline für die Verifikation |
| Auslöser | täglich, vor der Fahrplanfrist |
| Akteure | Betreiber bzw. Vermarkter, VNB |
| Ablauf | 1. Betreiber meldet den geplanten Fahrplan und je Viertelstunde ein Band [P_min, P_max] sowie den Energieinhalt. 2. VNB rechnet seine Netzprognose und meldet Sperrfenster (P8) bzw. reserviert Leistung. 3. Bei Engpass: Abruf nach P4 innerhalb des Bandes |
| Vergütung | Leistungspreis für reservierte Viertelstunden + Arbeitspreis für abgerufene Energie + Ersatz entgangener Markterlöse (kostenbasiert, wie Redispatch) |
| Fehlerfälle | Keine Meldung → kein Abruf, keine Reservierung. Abweichung vom Fahrplan ohne Abruf → keine Vergütung für diese Viertelstunde |

**P12 Flexibler Netzzugang – Vorschlag(v2.1)**

Für **neue** Großspeicher dort, wo das Netz voll ist (z. B. UW Steyr Nord): Der VNB gewährt den Anschluss vor dem Netzausbau, wenn der Speicher in Engpasszeiten nicht gegen das Netz fährt. Das ElWG sieht im Verteilnetz einen flexiblen Netzzugang mit zeitlich begrenzter Leistungsbeschränkung (12, 18 oder 24 Monate je Netzebene, nur Einspeiseseite) vor **[extern, Energie NÖ 18.12.2025, unbestätigt am Gesetzestext]**. Im Profil: Die Grenze kommt als signierter Dauer-Abruf (P4 mit langer Gültigkeit) bzw. als vereinbarter Fernwirk-Sollwert. Systemdienliches Verhalten soll laut ElWG mit niedrigeren Netzentgelten belohnt werden **[extern, Details ab 31.12.2026, unbestätigt]**; das wäre der Anreiz ohne Förderung.

### A4. Vorrang und Vermarktung

- Grundsatz bleibt: Der Betreiber bestimmt den Betrieb, der VNB greift nur in Ausnahmen und zeitlich begrenzt ein (Challenge-Text).
- Für M gilt die Reihenfolge: Sicherheit → **bereits präqualifizierte und bezuschlagte Regelreserve** → VNB-Abruf → Markt. Begründung: Regelreserve sichert das Gesamtsystem; der VNB vermeidet Konflikte über die Sperrfenster in P8/P11. Abweichung von der Box-Kette für H (dort VNB vor Aggregator), weil ein einzelner MW-Speicher einen messbaren Anteil am Regelreserve-Pool haben kann. **offen**, mit APG zu klären.
- Kein Abrufrecht ohne Entschädigung. Für M ist die Schadlosstellung **kostenbasiert** (entgangener Markterlös laut Fahrplan) statt über das Referenz-EMS.

### A5. Schnittstellen

| Strecke | H | G | M |
|---|---|---|---|
| VNB → Anlage | OpenADR (TOR Typ A) und LoRaWAN-Broadcast über die Box | wie H, alternativ OpenADR direkt an zertifiziertes Gebäude-EMS | **Fernwirkung IEC 60870-5-104** an der Übergabestation (in DE ab 100 kW Standard, in AT plausibel **[unbestätigt]**) **oder** OpenADR 3 (VEN im Anlagen-EMS); IP-Kanal, kein LoRa nötig |
| Anlage intern | SunSpec / EEBUS / IEEE 2030.5 | SunSpec Modbus TCP | IEC 61850-7-420 (DER-Modell) bzw. herstellerspezifisch hinter dem Parkregler |
| Vermarkter → Anlage | über Box-Modul | über EMS | Vermarkter-API, Modbus/SunSpec, VHPready (DE), OpenADR 3 **[extern, Recherche 09]** |
| Verifikation | Smart Meter | Smart Meter / Lastgang | Lastgangzähler + Fernwirkwerte |

**Gleiches Abrufobjekt für alle Klassen:** Die 31-Byte-Abrufnachricht aus Profil v2 Abschnitt 6.4 (Segment, Sequenz, Start, Dauer, Richtung, Zielleistung, Rampe, SOC-Grenzen, Grundcode) wird für M als Datenpunktliste in IEC 104 bzw. als OpenADR-Event abgebildet, mit derselben Signatur der Rolle VNB. Neu nur: Quittung (Annahme/Ablehnung/Teilannahme) und Echtzeit-Rückmeldung (P, SOC, verfügbare Leistung).

**Harte Grenzen für M** (analog Profil v2 Abschnitt 3, im Parkregler statt in der Box):

| Grenze | H (Profil v2) | M (Vorschlag) | Warum anders |
|---|---|---|---|
| Abrufe je Tag | 3 | vertraglich, z. B. 4 | Einzelanlage, quittiert |
| Dauer je Abruf | 3 h | bis 4 h bzw. Energieinhalt | Großspeicher haben oft 1–2 h, teils 4 h |
| Rampe | ≤ 10 % P_n/min | nach TOR Typ B / Netzbetreiber-Vorgabe **[unbestätigt]** | Spannungshaltung im MS-Netz |
| Zufallsverzögerung | 60–300 s | keine | eine Anlage, kein Gleichzeitigkeitsproblem |
| Nachrichten je Stunde | 6 | höher (Unicast, quittiert), aber Rate-Limit bleibt | Angriff über gestohlenen Schlüssel bleibt begrenzt |

### A6. Sicherheit – was sich ändert

- **Risiko kippt von „viele kleine“ zu „ein großer“:** Ein gestohlener Schlüssel wirkt bei H auf viele Boxen, aber gestreut und gedrosselt. Bei M wirkt ein einzelner Befehl sofort mit mehreren MW. Gegenmittel: Schlüssel je Anlage, Quittung mit Plausibilitätsprüfung im Parkregler (passt der Abruf zum gemeldeten Band aus P11?), Vier-Augen-Freigabe in der VNB-Leitstelle ab einer Leistungsschwelle, IEC 62351 bzw. VPN für IEC 104.
- Großspeicher-Betreiber und Vermarkter können unter NIS2 fallen **[unbestätigt]**; Bedrohungsanalyse nach IEC 62443 wie im Profil für die Pilotphase.

### A7. Regeln in Österreich (Kurzliste mit Quellen)

| Thema | Stand | Quelle |
|---|---|---|
| RfG-Typen A–D | A 0,8 – < 250 kW; B 250 kW – < 35 MW; C 35 – < 50 MW; D ≥ 50 MW oder ≥ 110 kV | RfG-Schwellenwert-V (BGBl. II 96/2024), Recherche 09 Abschn. 1.2 |
| TOR Typ B V1.4 | gültig ab 01.06.2026, eigener Abschnitt „Anwendung auf Speicher“ | Recherche 09 Abschn. 1.2 (Inhalt unbestätigt) |
| ElWG | Dez. 2025 beschlossen; Speicher = Einspeiser und Entnehmer; flexibler Netzzugang 12/18/24 Monate; systemdienliche Netzentgelte; Entgeltregeln ab 31.12.2026 | Recherche 09 Abschn. 1.4 (unbestätigt am Gesetzestext) |
| Netzentgelte Speicher | Befreiung von „doppelten Netzentgelten“ diskutiert; Endfassung **unbestätigt**; Altregel § 111 Abs. 3 ElWOG idF EAG **unbestätigt** | Recherche 09 Abschn. 1.4 |
| Regelreserve APG | FCR, aFRR, mFRR je 1 MW Mindestgebot, poolbar | Recherche 09 Abschn. 1.5 |
| Netzkapazitäten | freie Kapazität je UW (NE 4) gemeinsam über ebUtilities, quartalsweise | Recherche 09 Abschn. 1.1 |
| Fernwirkung | keine öffentliche Spezifikation von Netz OÖ gefunden; DE-Muster IEC 104 ab 100 kW | Recherche 09 Abschn. 1.7 |
| VNB Steyr | Netz OÖ (OSM, Netzkapazitätsdaten); ob Stadtbetriebe Steyr Stromnetz betreiben: **unbestätigt** | Recherche 09 Abschn. 3.2 |

### A8. Aufwand Profil

| Schritt | Inhalt | Aufwand |
|---|---|---|
| A-1 | Tabelle A1 und Absatz A4 als neuer Abschnitt „1a Speicherklassen“ in `profil-v2.md` | 20 min (heute machbar) |
| A-2 | P11 und P12 als Prozesstabellen, Änderungstabelle A3 | 30 min |
| A-3 | Schnittstellen A5 und Grenzen für M | 30 min |
| A-4 | Abgleich mit TOR Typ B V1.4 (Speicherabschnitt) und ElWG-Text, „unbestätigt“ auflösen | 2–3 h |
| A-5 | Abstimmung mit Smart Grids Austria / Netz OÖ: Vorrang Regelreserve vs. VNB, Fernwirk-Datenpunkte | nach dem Hackathon |

## B. Simulation (`gridsim`)

### B1. Was die Daten schon hergeben

Alles liegt bereits in den Eingangsdaten unter `/data/infra-kg-austria/work/steyr-pv-2026-10-24/input/` (heute ausgewertet):

| Quelle | Inhalt für Gewerbe / Großspeicher | Befund |
|---|---|---|
| `pv_steyr_bbox.geojson` (BOKU-PV-Karte) | PV je Anlage mit Leistung | 4 420 Anlagen in der Box: 4 207 bis 30 kWp (27,5 MWp), **205 mit 30–250 kWp (12,0 MWp)**, **8 über 250 kWp (4,5 MWp)**. Die 8 großen Anlagen sind heute **nicht** im Modell (gelten als MS-Anschluss) |
| `gebaeude_bbox.csv` (BEV-Adressregister, Feld `EIGENSCHAFT`) | Gebäudenutzung je Adresse | 12 913 × „01“, 6 566 × „02“ (Wohnen), **900 × „08“, 303 × „06“, 278 × „05“**, 311 × „09“, 132 × „04“. Nach der BEV-Codeliste vermutlich 05 Büro, 06 Groß-/Einzelhandel, 08 Industrie und Lager **[Zuordnung unbestätigt, Codeliste prüfen]** |
| `apcs/synthload2026.csv` | APCS-Standardlastprofile 2026 je Viertelstunde | enthält **G0–G6** (Typnummern 2–8), L0–L2, G7, B1 – Gewerbelasten sind ohne neue Quelle möglich |
| `powerstations.json` (Netzkapazitäten der VNB) | gebuchte und freie Kapazität je UW | **UW Steyr: gebucht 13,77, frei 61,96; UW Steyr Nord: gebucht 28,44, frei 0** (Einheit vermutlich MW, unbestätigt; Netz OÖ, Link `netto.netzooe.at`) |
| OSM (Overpass, heute) | Flächen und Großspeicher | 35 Industrie-, 91 Gewerbeflächen, 147 Gewerbe-/Industriegebäude, 3 benannte 110-kV-UW (Steyr-Nord, -Ost, -Fischhub), **0 getaggte Batteriespeicher** (Recherche 09 Abschn. 3.2) |

Ergebnis: Kein bekannter Großspeicher > 1 MW in Steyr (Recherche 09 Abschn. 3.4). Standorte für Großspeicher sind im Demo **synthetisch** und als solche zu kennzeichnen; Kandidaten: Industrieflächen mit Gebäudecode 08 und PV > 250 kWp, Nähe zu UW Steyr Nord.

### B2. Was gridsim heute macht

- `legacy/steyr_sim_variant_a.py` hat schon einen Schalter für Gewerbespeicher: `STORAGE_SHARE_LARGE` (Anteil der Anlagen 30–250 kWp mit Speicher, `--large-share`) und `STORAGE_KWH_PER_KWP_LARGE = 0,5`. `gridsim/prepare.py` setzt den Anteil fest auf 0.
- Knoten ohne Haushalt (`nodes_hh == 0`, „Halle/Stall“) haben **keine Last**, nur PV. Gewerbelasten fehlen im Modell; die Trafogröße wird aus Wohngebäuden, Haushalten und PV geschätzt. Das unterschätzt die Last an gemischten Stationen und sollte als Grenze in Notes und README stehen.
- Keine Mittelspannung: Stationen sind einem UW zugeordnet (`st_uw` in `build_members`), es gibt aber keine Kennzahl je UW.

### B3. Schnellrechnung von heute (Wetter 2023, Seed 0, ungesteuert, Speicher „base“)

| Kennzahl | 2030 | 2040 |
|---|---|---|
| Stationen mit Lastengpass | 37 | 192 |
| davon mit Gewerbe-PV > 30 kWp | 15 | 53 |
| Stationen mit Einspeiseengpass / davon mit Gewerbe-PV | 3 / 3 | 2 / 2 |
| Netto-Bedarf E_netto (Summe größtes Ereignis je Station) | 7,7 MWh | 352 MWh |
| davon rechnerisch durch Gewerbespeicher (0,5 kWh/kWp) an diesen Stationen deckbar, Obergrenze | 0,7 MWh | 2,7 MWh |
| Gewerbespeicher gesamt bei 100 % Ausstattung | 5,8 MWh | 5,8 MWh |

Lesart: Im Winter sind die Engpässe lang und energiereich; Gewerbespeicher in der Größe der Gewerbe-PV decken nur einen kleinen Teil. Sie sind vor allem im Sommer gegen Einspeisespitzen nützlich und dort, wo sie zufällig an einer kritischen Station stehen. Modellwerte, ein Seed, ohne Gewerbelasten. Rechnung: `load_prepared(…/prepared, 2023)`, `run.flows`, `metrics.station_rows`, Knoten mit `kwp > 30`.

### B4. Vorschlag: drei Ausbaustufen

| Schritt | Inhalt | Dateien | Aufwand |
|---|---|---|---|
| B-1 | **Gewerbespeicher hinter dem Zähler (Klasse G):** `RunParams.large_share` (0 / 0,5 / 1,0); in `prepare.py` Speichergröße für Knoten 30–250 kWp mit eigenem Zufallsstrom vorbereiten (`nodes_kwh_large`), in `control.storage_flow` mitsimulieren. MODEL_VERSION erhöhen; Tests ergänzen; Dashboard-Schalter | `prepare.py`, `run.py`, `control.py`, `data.py`, `api/app.py`, `web/gridsim/dashboard.js`, `tests/` | 3–4 h inkl. neuem `prepare` und Cache |
| B-2 | **Gewerbelasten:** Knoten mit Gebäudecode 05/06/08 in Stationsnähe erhalten Jahresverbrauch (Annahme je m² bzw. je Gebäude aus LoD1-Fläche) und G-Profil (G1 Büro, G4 Handel, G3 bzw. G0 Industrie). Ohne B-2 sind die Ergebnisse für Gewerbe zu optimistisch | `prepare.py`, `profiles.py`, Legacy-Zuordnung Gebäude → Station | 4–6 h, Annahmen dokumentieren |
| B-3 | **Großspeicher an der Mittelspannung (Klasse M):** Stationsflüsse je UW summieren (`st_uw`), freie Kapazität aus `powerstations.json` als Grenze der Einspeisung, 1–2 synthetische Großspeicher (z. B. 2 MW / 4 MWh) je UW mit Strategie „Peak Shaving am UW“ bzw. Fahrplan + Abruf. Kennzahl: Stunden über der UW-Grenze, verschobene Energie. Die 8 PV-Anlagen > 250 kWp hier aufnehmen | neues `gridsim/mv.py`, `metrics.py`, Dashboard-Kachel | 1 Tag; Lastfluss MS nicht enthalten |
| B-4 | Optional: Overpass-Gewerbeflächen und DORIS-Widmung (B/I/G) als Kandidatenstandorte; Lizenz DORIS **unbestätigt** | `prepare.py` | 2–3 h |

Datenquellen für B-1 bis B-4 sind offen: BOKU-PV, BEV-Adressregister, APCS-SLP, VNB-Netzkapazitäten (ebUtilities), OSM. Ein öffentliches Speicher-Register wie das deutsche Marktstammdatenregister gibt es in Österreich nicht **[extern, Recherche 09 Abschn. 3.3]**.

## C. Präsentation und Webseite

| Schritt | Wo | Inhalt | Aufwand |
|---|---|---|---|
| C-1 | `index.html`, Abschnitt „Who exchanges what“ | Den vorhandenen Satz durch zwei ersetzen (Text unten). Kein neues Kapitel | 10 min (heute machbar) |
| C-2 | `details.html`, Kapitel 5 | Unterabschnitt „Business and large storage“ mit Tabelle A1 (gekürzt auf 6 Zeilen), P11/P12 in je einem Satz, Hinweis auf UW Steyr Nord | 30–45 min |
| C-3 | `details.html`, Kapitel 7 Datenquellen | Gebäudecodes, PV > 30 kWp, Netzkapazitäten, APCS G-Profile ergänzen; Grenze „keine Gewerbelasten im Modell“ | 15 min |
| C-4 | Dashboard-Karte | Layer: Gewerbe-PV > 30 kWp, Industriegebäude, UW mit freier Kapazität | 1–2 h, setzt Daten aus B voraus |
| C-5 | Pitch (mündlich) | Ein Satz: „Home and business batteries relieve the local transformer; large storage at medium voltage relieves the substation – same signed call, different channel.“ | 0 min |

Textvorschlag C-1 (Englisch):

> **From basement to business park.** The same signed call and the same limits work for every size. Home and business batteries behind the meter relieve the local transformer; large storage from 250 kW upwards sits on the medium-voltage grid, gets the call via the grid operator's telecontrol link with an acknowledgement, and relieves the substation – in our region one substation already has no free feed-in capacity left.

Satz für das Abgabeformular (Notes oder Solution):

> Business and large storage use the same processes and call; they differ in channel (telecontrol or OpenADR with acknowledgement instead of radio broadcast), contract (flexible grid connection under the new Austrian electricity act instead of subsidies) and verification (declared schedule as baseline). Simulating them is a next step.

## D. Empfehlung und Reihenfolge

1. **Vor 11:30:** C-1 (Webseite, 10 min) und der Formularsatz; optional A-1 ins Profil. Nur wenn die P0-Punkte der Lückenanalyse (Repo- und Demo-Zugang, README) erledigt sind.
2. **Für den Pitch:** C-5 mündlich, mit der UW-Steyr-Nord-Zahl.
3. **Nach der Abgabe:** A-2/A-3, dann B-1 + B-2 zusammen (sonst schönt B-1 die Gewerbe-Ergebnisse), dann B-3 und C-2 bis C-4.

## Quellen

- Recherche heute mit allen URLs: `docs/research/09-grossspeicher-gewerbe.md` (TOR/RfG, ElWG, APG, ebUtilities, Großspeicher OÖ, Overpass-Abfrage).
- Profil v2: `docs/context/profil-v2.md`.
- Eingangsdaten gridsim: `/data/infra-kg-austria/work/steyr-pv-2026-10-24/input/` (`pv_steyr_bbox.geojson`, `gebaeude_bbox.csv`, `apcs/synthload2026.csv`, `apcs/Kategorien.csv`, `powerstations.json`), ausgewertet 25.10.2026.
- Vorbereitete Simulation: `/data/infra-kg-austria/work/gridsim/prepared/2023`, Code `gridsim/` (HEAD `232691f`).
