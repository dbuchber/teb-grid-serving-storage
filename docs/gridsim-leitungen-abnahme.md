# Abnahme NS-Leitungen in gridsim (25.10.2026)

Abnahmelauf nach Spec `docs/superpowers/specs/2026-10-25-ns-leitungen-design.md` § 6 auf hetzner, Stand
`feat/ns-leitungen`, `MODEL_VERSION` `2026-10-26.5` (Fix-Runde 4: reine Spannungsfälle zählen nicht zur 10-%-Grenze; dazu
Wärmepumpen als k größte Leistungen, Ist-Abgleich „heute“ und Mindestquerschnitt aus den Fix-Runden 1–3).
Die Läufe der Fix-Runden 3, 2 und 1 und der erste Lauf sind verworfen und stehen am Ende als eigene Abschnitte. Alle Zahlen sind
Modellwerte aus einem **synthetischen** Niederspannungsnetz, keine Messungen.

## Kurzfassung (Fix-Runde 4)

- **Die Abnahmegrenze „heute“ ist bestanden.** Auf `prepared-ns-fix4` (432 Stationen) liegt im P90 über
  20 Seeds in keinem der drei Wetterjahre eine Station über 100 % (Maximum 88,9 %). Regel: höchstens 5 von 432 über
  100 %, keine über 120 %.
- **Markierte Abgänge:** 41 von 432 Stationen (9,5 %), innerhalb der 10-%-Grenze. Abgänge, die nur am
  Spannungsfall scheitern, zählen nach Owner-Entscheidung nicht mehr mit. Es sind 122 Abgänge an 93 Stationen
  (21,5 %; stadt 12, ort 41, streu 40); dort müsste ein realer Netzbetreiber wegen der Spannung handeln.
- **2040 (Hauptergebnis 2040r, 50 % Wärmepumpen), ungesteuert:** An 298 (2012) bzw. 250 (2023) von 432 Stationen
  ist der Trafo überlastet, Leitungen an 101 bzw. 49. „Engpass zuerst“: Trafo 214 / Leitung 11 / beide 89 (2012).
  **Der Trafo ist der erste Engpass**, Leitungen kippen nur an wenigen Stationen vorher (11–17).
  2040 als Stresstest (70 %): 324 bzw. 289 Trafos, 160 bzw. 80 Stationen mit Leitungsüberlast.
- **2030, ungesteuert:** 127 (2012) bzw. 52 (2023) Trafos überlastet, Leitungen nur an 9 bzw. 4 Stationen.
- **Gesteuertes Laden:**
  - Es senkt die Trafo-Engpässe stark: 2040r/2012 von 298 auf 122, mit V2G auf 33.
  - Im Modus `trafo+leitung` bleibt keine Leitungsüberlast (40 → 0 Stationen in 2040r).
  - Die ungeladene Energie bleibt dabei gleich (280 MWh); die Leitungsgrenze kostet hier also keine Ladung.
- **Netzspeicher:** Sie sind jetzt klein und wirken nur ungesteuert. 2040r/2012: 170 Speicher mit zusammen
  24,8 MWh (Mittel 146 kWh), die Stationen mit Leitungsüberlast sinken von 101 auf 88, die Überlastlänge von
  11,0 auf 8,3 km. Mit leitungsbewusster Steuerung entsteht kein Bedarf (0 Speicher).
- **pandapower:** gridsim liegt im Median 2,5 % (heute) bzw. 3,9 % (2040r) unter dem Lastfluss, im P95 um 2,1
  bzw. 4,5 Prozentpunkte.
- **Dashboard:** zeigt 432 Stationen, keine Fehler in der Konsole.

## Szenarioannahmen

Die Anteile der Szenarien wurden gegen veröffentlichte Quellen geprüft (Recherche
`docs/research/2026-10-25-szenarioanteile-wp-ev.md` im Repo infra-kg-austria, Stand 25.10.2026):

| Szenario | Wärmepumpen (Haushalte) | E-Autos je Haushalt | Befund der Recherche |
|---|---|---|---|
| heute | 23 % je Gebäude (21,4 % der Haushalte) | 0,076 | aus dem Ist-Abgleich, plausibel (Stichprobenfehler WP ±2,3 Pp) |
| 2030 | 35 % | 0,25 | WP plausibel, aber ambitioniert. AIT/Oesterreichs Energie 2024 nennt 31–40 %, der Trend OÖ etwa 29 %. E-Autos auf der oberen Seite (AIT 0,24, Trend 0,19) |
| **2040r** (Hauptergebnis) | **50 %** | 0,60 | WP innerhalb der Quellen: AIT 48–57 %; Obergrenze aus dem OÖ-Heizungsmix etwa 50 %. E-Autos plausibel (AIT 0,60) |
| 2040 (**Stresstest**) | 70 % | 0,60 | WP durch keine gefundene Quelle gedeckt. Für 70 % müssten über 20 Pp der Holz- und Fernwärme-Haushalte wechseln |
| 2040m | 35 % | 0,60 | unverändert, im Dashboard wählbar |

`2040r` ist als Override in `gridsim/profiles.SCENARIOS` angelegt (wie 2040m), Test `test_scenario_2040r_realistic`;
2040 bleibt unverändert. Der Cache-Schlüssel bestehender Einstellungen ändert sich dadurch nicht, daher kein neuer
`MODEL_VERSION`.

## Ist-Abgleich „heute“ (Owner-Entscheidung, Fix-Runde 2)

Die realen Kabel tragen die heutige Last; deshalb muss das Modell für „heute“ halten. Geprüft wurden die
Anteile von E-Autos und Wärmepumpen, die gridsim für „heute“ zieht (`profiles.assign`). Der frühere Stand
`legacy/steyr_wp_ev.SCENARIOS['heute']` = 15 % WP, 0,08 E-Autos je Haushalt bleibt unverändert (SHA256SUMS); die
neuen Werte stehen als Override in `gridsim/profiles.SCENARIOS['heute']`. 2030, 2040 und 2040m sind unverändert.

| Größe | Quelle (Abruf 25.10.2026) | Stand | Wert | Modell |
|---|---|---|---|---|
| Elektro-Pkw OÖ | Statistik Austria, „Kfz-Bestand nach Bundesland und Kraftstoffart bzw. Energiequelle 2025“, https://www.statistik.at/fileadmin/pages/75/Kfz-BestandKraftfahrzeugBundeslandKraftstoffartEnergiequelle2025.ods (Zeile Oberösterreich / Personenkraftwagen Klasse M1, Spalte Elektro) | 31.12.2025 | 51 343 von 1 000 719 Pkw (5,1 %) | – |
| Pkw Stadt Steyr / Steyr-Land | Statistik Austria, „Kfz-Bestand 2025“, Tabelle 7, https://www.statistik.at/fileadmin/pages/75/kfz-bestand_2025.ods | 31.12.2025 | 22 694 / 42 880 Pkw; Elektro je Bezirk nicht veröffentlicht (nur STATcube) | – |
| Privathaushalte OÖ | Statistik Austria, Haushaltsprognose, wiedergegeben von WKÖ, https://www.wko.at/statistik/bundesland/PrivathaushPrognose.pdf; Mikrozensus 2024: 672 976 (https://www.wko.at/statistik/bundesland/Privathaush.pdf) | 2025 | 672 647 | – |
| **E-Autos je Haushalt** | eigene Rechnung: 51 343 / 672 647 | 2025 | **0,076** | `ev_share` 0,076 (bisher 0,08) |
| Heizsystem Hauptwohnsitze OÖ | Statistik Austria, „Primäres Heizsystem nach überwiegend eingesetztem Energieträger und Art der Heizung 2003 bis 2024“, Blatt Oberösterreich, https://www.statistik.at/fileadmin/pages/100/08Heizungen2003Bis2024NachBundeslaendernUndVerwendetemEnergietraeger.ods (MZ Energieeinsatz der Haushalte 2023/2024, erstellt 14.05.2025) | Winter 2023/24 | „Solar, Wärmepumpen“ 142 397 von 666 900 Wohnungen = **21,4 %**; Fernwärme 223 656 (33,5 %) | `wp_share` 0,23 (bisher 0,15) |
| Anteil 11-kW-Wallboxen | keine Quelle gefunden | – | – | unverändert 0,7 |

Umrechnung und Annahmen:

- **E-Autos:** Bezirkswerte für Elektro-Pkw veröffentlicht Statistik Austria nur in STATcube, nicht als Datei;
  der Katalog auf hetzner (data.gv.at-Spiegel, `infra-kg-db-1`) hat für Steyr keinen Kfz-Bestand nach
  Antrieb. Daher gilt der OÖ-Wert. Gegenprobe:
  - Mit dem OÖ-Anteil von 5,1 % an den Pkw in Stadt Steyr und Steyr-Land (65 574 Pkw) ergeben sich etwa
    3 360 Elektro-Pkw. Im Modell sind es 0,076 × 42 210 Haushalte ≈ 3 210; das modellierte Gebiet ist kleiner
    als beide Bezirke.
  - Die Stadt Steyr hat weniger Pkw je Einwohner als OÖ (598 gegen 651 je 1 000; Tabelle 6). Der Wert ist eher
    eine Obergrenze für die Stadt.
  - Bestand und Haushalte stammen aus verschiedenen Quellen (Kfz-Statistik 31.12.2025, Haushaltsprognose 2025).
- **Wärmepumpen:**
  - Die Kategorie der Statistik heißt „Solar, Wärmepumpen“; Solarthermie als primäres Heizsystem ist selten.
  - gridsim zieht Wärmepumpen je Wohngebäude, ohne Fernwärme-Gebäude (`p_wp = wp_share / (1 − Fernwärmeanteil
    der Gebäude)`), und kann damit Haushalte in Mehrfamilienhäusern nur gemeinsam treffen.
  - Im Modellgebiet (42 210 Haushalte, 12,4 % mit Fernwärme) ergibt `wp_share` 0,23 einen erwarteten Anteil von
    21,4 % der Haushalte mit Wärmepumpe (0,15 ergab 14,0 %).
  - Der OÖ-Wert enthält Linz mit viel Fernwärme. Unter den Haushalten ohne Fernwärme wären es in OÖ 32 %, im
    Modell jetzt 24 %. Gewählt ist der Anteil an allen Haushalten, wie die Statistik ihn ausweist.
- **Wallboxen:** Ohne Quelle bleibt der Anteil 11 kW bei 70 % (legacy `EV_FAST_SHARE`). Die Bemessung rechnet
  ohnehin mit 11 kW je Auto (p_ev(1)).

Wirkung auf die Trafo-Kennzahlen heute (`prepared-ns-fix2`, ungesteuert, 20 Seeds, Median mit Band 10–90 %):

| Wetterjahr | Trafo-Engpass, alte Anteile (0,15 / 0,08) | Trafo-Engpass, Ist-Abgleich (0,23 / 0,076) | E_netto MWh alt → neu | Trafo +1 alt → neu |
|---|---|---|---|---|
| 2012 | 2 (1–5) | **11** (7–17) | 0,06 → 0,95 | 2 → 10 |
| 2017 | 0,5 (0–1) | **3** (1–5) | 0,00 → 0,07 | 0,5 → 3 |
| 2023 | 0 (0–1) | **1,5** (0–4) | 0,00 → 0,03 | 0 → 1 |

Die alten Werte sind ohne Cache mit den legacy-Anteilen gerechnet (`out/heute-old-shares-fix2.json` auf hetzner).
Das sind immer noch wenige Trafos (2 % der 508 Stationen im Kältejahr). Mit 11 überlasteten Trafos in 2012 liegt
das Modell aber deutlich über dem Bild „heute praktisch kein Trafo überlastet“.

## Mindestquerschnitt (Fix-Runde 2)

In den Gebietstypen stadt und ort bekommt jeder Strangabschnitt mindestens NAYY 4x150 (Kabel) bzw. Al 4x95
(Freileitung); streu und Hausanschlüsse sind unverändert. Höhere Last oder Spannungsfall setzen den Abschnitt
weiter hoch wie bisher. Umsetzung: `gridsim/feeders/sizing.py` (`MIN_TRUNK`), Tests
`test_minimum_trunk_section_in_stadt_and_ort` und `test_minimum_section_still_upgrades_for_load`. Das entspricht
üblicher Praxis für neue Ortsnetze, ist aber nicht aus Steyr-Daten belegt (siehe „Grenzen der Aussage“).

## Bemessungsregel (Fix-Runden 1 und 3, Rulings des Controllers, 25.10.2026)

Ersetzt die Auslegungslast aus Spec 4.3 / Entscheidung 5; die Abnahmegrenze bleibt unverändert. Umsetzung in
`gridsim/feeders/sizing.py::design_flows` und `gridsim/feeders/prepare.py::design_loads`. Je Abschnitt mit n
Haushalten und m WP-berechtigten Gebäuden dahinter:

- **Haushalte:** n · max(P_HH · g(n), H0-Spitze). Die H0-Spitze kommt aus gridsims eigenem H0-Profil
  (`p.h0 · KWH_PER_HH`), als größerer Wert aus „H0 in der kältesten Stunde 2012“ und „Jahresspitze des H0-Profils“
  (die Abendspitze im Winter, die die Bewertung trifft). Das ergibt 0,79 kW je Haushalt; der Wert ist nicht im
  Code festgeschrieben.
- **Wärmepumpen:** k = P90 Binomial(m, p_wp) ganze Geräte (`scipy.stats.binom.ppf(0.9, m, p_wp)`). p_wp ist wie in
  `profiles.assign` der Anteil „heute“ (seit Fix-Runde 2: 23 %) geteilt durch den Anteil der Wohngebäude ohne Fernwärme, gezogen je
  berechtigtem Gebäude. Gerechnet wird seit Fix-Runde 3 die Summe der k größten vollen elektrischen Leistungen der
  berechtigten Knoten dahinter (vorher: k × mittlere Leistung), jeweils in der kältesten Stunde ihrer Zelle
  (`profiles.heat_pump_kw`, Versatz 0). Test `test_heat_pumps_k_largest_powers`: k = 2 bei [3, 3, 20, 25] kW
  ergibt 45 kW, nicht 2 × 12,75 kW. Alle laufen gleichzeitig, so wie gridsim die
  kälteste Stunde ohne Versatz rechnet.
- **E-Autos:** k = P90 Binomial(n, ev_share). ev_share ist der Anteil „heute“ je Haushalt (seit Fix-Runde 2: 0,076), wie `profiles.assign` ihn zieht. Gerechnet
  wird k · p_ev(k): volle Wallbox-Leistung 11 kW bei k = 1, darüber der Gleichzeitigkeitsfaktor nach Maier/Groiß.
- Einspeisung und Planungsgrenzen sind unverändert.
- Tests:
  - `test_household_term_at_least_h0_peak`
  - `test_devices_binomial_p90`
  - `test_design_flows_without_homes_or_devices`
  - `test_design_loads_heute` (angepasst)

## Netzbau (`prepared-ns-fix4`)

`gridsim prepare-feeders --input …/steyr-pv-2026-10-24/input --prepared prepared --extra-stations --out
prepared-ns-fix4`. Neu gebaut, weil die Markierung bestimmt, wo Zusatzstationen entstehen: Abgänge, die nur am
Spannungsfall scheitern, lösen keine Zusatzstation mehr aus. Ein Durchgang reichte (53,3 % → 9,5 %): 194 geplant,
19 kleine wieder aufgelöst, 175 behalten, 432 Stationen.

| Kennzahl | Fix-Runde 4 | Ziel |
|---|---|---|
| Stationen | 432 | – |
| Kabelanteil nach Trassenlänge (Abnahmegröße) | 74,4 % | 79 % (Band 74–84 %) |
| Kabelanteil nach Kabellänge | 69,6 % | nur Information |
| NS-Trasse je Station | 2,22 km | ca. 2,7 km |
| NS-Kabellänge je Station (Systeme einzeln) | 3,86 km | ca. 2,7 km |
| Abgänge je Station (Mittel / Median) | 4,61 / 3 | 3,4–3,8 |
| Wohngebäude je Station (Mittel) | 41,8 | ca. 58 |
| Trasse je Wohngebäude | 53,1 m | ca. 46 m |
| **Stationen mit markiertem Abgang (zählt)** | **41 (9,5 %)** | ≤ 10 % |
| davon zu lang / Strom zu hoch (Abgänge) | 100 / 1 | – |
| **nur Spannung (zählt nicht)** | **122 Abgänge an 93 Stationen (21,5 %)** | – |
| nur Spannung nach Gebietstyp (Stationen) | stadt 12, ort 41, streu 40 | – |
| Ausläufer | 406 Abgänge an 202 Stationen (Reichweite Median 841 m) | – |
| Gebietstypen stadt / ort / streu | 136 / 203 / 93 | – |

Die reinen Spannungsfälle sind mit dem stärksten Typ bemessen (2 × NAYY 4x240 bzw. 2 × Al 4x95) und stehen
getrennt in `report.json` (`voltage_only`), `index.json` (`marked_voltage`), der API (`/api/stations`) und im
lines-report. Das Dashboard zeigt keine Markierungen und braucht dafür keine Änderung.

| Typ | km | Anteil |
|---|---|---|
| NAYY 4x50 | 40,9 | 2,5 % |
| NAYY 4x150 | 691,1 | 41,4 % |
| NAYY 4x240 | 429,3 | 25,7 % |
| Al 4x70 | 53,1 | 3,2 % |
| Al 4x95 | 454,0 | 27,2 % |
| NAYY 4x35 (Hausanschluss) | 263,3 | 87,1 % |
| Al 4x25 (Hausanschluss) | 39,0 | 12,9 % |

## Abnahmegrenze „heute“ (Fix-Runde 4)

Heute (Anteile aus dem Ist-Abgleich), PV 1,0, Speicher base, ungesteuert, `trafo`, ohne Netzspeicher, 20 Seeds;
8 Worker, je Wetterjahr etwa 87 s; Cache `cache-fix4/`.

| Wetterjahr | Seeds | Stationen > 100 % | Stationen > 120 % | Median P90 | Max P90 |
|---|---|---|---|---|---|
| 2012 | 20 | 0 | 0 | 48,9 % | 87,0 % |
| 2017 | 20 | 0 | 0 | 43,3 % | 88,9 % |
| 2023 | 20 | 0 | 0 | 40,8 % | 85,1 % |
| alle (Maximum je Station) | 20 | **0** | **0** | 48,9 % | 88,9 % |

**Ergebnis: bestanden** (Regel: höchstens 5 von 432 über 100 %, keine über 120 %).

Trafos heute (Median, Band 10–90 %): 11 (7–18) in 2012, 3,5 (2–5) in 2017, 2 (0–5) in 2023 von 432. Zur
Lesart siehe „Grenzen der Aussage“.

## Vergleich der Modi 2030 und 2040 (2040r als Hauptergebnis, 2040 als Stresstest)

`prepared-ns-fix4`, PV 1,0, Speicher base, 20 Seeds je Einstellung, Median über die Seeds. Gerechnet wurden
2012, 2023 × 2030, 2040r, 2040 × ungesteuert (`trafo`, Netzspeicher aus/an) sowie gesteuert und V2G × `trafo` /
`trafo+leitung` × Netzspeicher aus/an. Spalten wie im ersten Lauf; die letzte Spalte zeigt „Engpass zuerst“ in
Bezugsrichtung je Station.

### Kernaussagen

| Wetter | Szenario | Trafo / Leitung / beide / keiner (ungesteuert) | Trafo-Engpass: ungesteuert → gesteuert → V2G | Leitung Bezug: gesteuert `trafo` → `trafo+leitung` | ungeladen MWh (gesteuert / V2G) | Netzspeicher ungesteuert: Leitung aus → an, Anzahl, MWh |
|---|---|---|---|---|---|---|
| 2012 | 2030 | 126 / 6 / 1 / 299 | 127 → 36 → 10 | 7 → 0 | 8,8 / 24,1 | 9 → 9, 7, 0,4 |
| 2023 | 2030 | 46 / 5 / 0 / 381 | 52 → 6 → 0 | 4 → 0 | 0,0 / 0,3 | 4 → 4, 6, 0,4 |
| 2012 | **2040r** | 214 / 11 / 89 / 118 | 298 → 122 → 33 | 40 → 0 | 280 / 508 | 101 → 88, 170, 24,8 |
| 2023 | **2040r** | 227 / 17 / 26 / 162 | 250 → 38 → 2 | 34 → 0 | 6 / 13 | 49 → 44, 73, 11,4 |
| 2012 | 2040 (Stresstest) | 169 / 11 / 157 / 95 | 324 → 226 → 132 | 52 → 14 | 1 092 / 2 207 | 160 → 136, 277, 63,6 |
| 2023 | 2040 (Stresstest) | 226 / 11 / 64 / 131 | 289 → 136 → 20 | 36 → 0 | 57 / 120 | 80 → 71, 127, 18,2 |

- **Trafo vor Leitung.** Mit dem neuen Netz ist der Trafo fast überall der erste Engpass. 2030 sind Leitungen nur
  an 4–9 Stationen überlastet; in 2040r an 49–101 Stationen, aber nur an 11–17 vor dem Trafo. Der erste Lauf
  hatte das Gegenteil gezeigt („Leitung zuerst“ an über 100 Stationen 2030); das lag am zu schwach bemessenen Netz.
- **Gesteuertes Laden wirkt am Trafo:**
  - 2040r/2012: 298 → 122 Trafo-Engpässe, mit V2G 33; 2023 sinkt es auf 38 bzw. 2.
  - Der Preis ist ungeladene Energie in der Kältewelle (280 MWh gesteuert, 508 MWh V2G in 2040r/2012; 2023 nur
    6 bzw. 13 MWh).
  - Im Stresstest 2040 (2012) bleiben 226 Trafo-Engpässe mit 1,1 GWh ungeladen.
- **Leitungsbewusste Steuerung** (`trafo+leitung`):
  - Sie beseitigt die verbleibende Leitungsüberlast fast vollständig (2040r: 40 → 0; Stresstest 2012: 52 → 14).
  - Ungeladene Energie und Trafo-Kennzahlen bleiben dabei gleich: Wo der Trafo ohnehin drosselt, kostet die
    Leitungsgrenze kaum zusätzlich.
  - Die Rest-Leitungsüberlast bei gesteuertem Laden im Modus `trafo` (34–40 Stationen in 2040r) entsteht, weil die
    Trafo-Steuerung die Ladeleistung ohne Blick auf die Abgänge verteilt.
- **V2G gegen Leitung:** Im Modus `trafo` ändert V2G an den Leitungen nichts (39 Stationen), erst `trafo+leitung`
  bringt sie auf 0.
- **Einspeisung:** keine Leitungsüberlast bei PV 1,0.

### Reihenfolge heute → 2030 → 2040r bzw. 2040

Je Station das erste Szenario mit Engpass (ungesteuert, Grenzmodus `trafo`, beide Richtungen, häufigste Klasse
über die Seeds):

| Wetter (letztes Glied) | zuerst Trafo | zuerst Leitung | beide zugleich | nie | davon schon heute (T / L / b) |
|---|---|---|---|---|---|
| 2012 bis 2040r | 252 | 14 | 50 | 116 | 4/0/0 |
| 2023 bis 2040r | 234 | 19 | 21 | 158 | 4/0/0 |
| 2012 | 241 | 14 | 84 | 93 | 4/0/0 |
| 2023 | 236 | 13 | 56 | 127 | 4/0/0 |

„beide zugleich“ heißt: Im ersten Szenario mit Engpass sind Trafo und Leitung überlastet. Heute gibt es keine
Station mit Leitungsengpass (Abnahmegrenze bestanden); die 4 Stationen „heute“ sind Trafo-Engpässe.

### Netzspeicher, neu bewertet

Bemessung unverändert (§ 7.2 auf den Abschnittsfluss, Auslegungslauf Seed 0). Mit dem neuen Netz:

- **Ungesteuert, 2040r:** 170 (2012) bzw. 73 (2023) Speicher mit zusammen 24,8 bzw. 11,4 MWh, im Mittel 146 bzw.
  156 kWh je Speicher. Die Stationen mit Leitungsüberlast sinken um 10–13 % (101 → 88, 49 → 44), die Länge der
  überlasteten Abschnitte um 25–28 % (11,0 → 8,3 km, 6,5 → 4,7 km). Am Trafo ändern sie fast nichts (298 → 296).
- **Stresstest 2040 (2012):** 277 Speicher mit 63,6 MWh (230 kWh im Mittel); Leitung 160 → 136 Stationen.
- **2030:** 6–7 Speicher mit zusammen 0,4 MWh, ohne Wirkung auf die Zahl der Stationen.
- **Gesteuertes Laden / V2G im Modus `trafo+leitung`:** kein Bedarf (0 Speicher). Im Modus `trafo` gleiche Wirkung
  wie ungesteuert, weil der Netzspeicher dort nur den Grundfluss sieht (Ruling).
- Lesart: Die Größen sind jetzt plausibel (Größenordnung 100–250 kWh je Abgang; erster Lauf: bis 11 GWh in Summe).
  Als Mittel gegen Leitungsengpässe sind sie eine Brücke für die wenigen ungesteuerten Fälle; leitungsbewusstes
  Laden löst dieselben Engpässe ohne Speicher. Den Trafo entlasten sie nicht. Kostensätze bleiben Platzhalter.

### Alle Einstellungen

| Wetter | Szenario | Laden | Grenzen | Netzspeicher | Seeds | Trafo-Engpass | Leitung Bezug | Leitung Einsp. | nur Leitung | Überlast km | ungeladen MWh | NS Anzahl | NS kWh | Bezug: Trafo / Leitung / beide / keiner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2012 | heute | uncontrolled | trafo | aus | 20 | 11 | 0 | 0 | 0 | 0,0 | 0,0 | – | – | 2 / 0 / 0 / 430 |
| 2012 | 2030 | uncontrolled | trafo | aus | 20 | 127 | 9 | 0 | 6 | 0,8 | 0,0 | – | – | 126 / 6 / 1 / 299 |
| 2012 | 2030 | uncontrolled | trafo | an | 20 | 127 | 9 | 0 | 6 | 0,6 | 0,0 | 7 | 415 | 126 / 5 / 1 / 300 |
| 2012 | 2030 | controlled | trafo | aus | 20 | 36 | 7 | 0 | 7 | 0,7 | 8,8 | – | – | 29 / 6 / 0 / 397 |
| 2012 | 2030 | controlled | trafo | an | 20 | 36 | 7 | 0 | 7 | 0,7 | 8,8 | 7 | 391 | 29 / 6 / 0 / 397 |
| 2012 | 2030 | controlled | trafo+leitung | aus | 20 | 36 | 0 | 0 | 0 | 0,0 | 8,8 | – | – | 29 / 0 / 0 / 403 |
| 2012 | 2030 | controlled | trafo+leitung | an | 20 | 36 | 0 | 0 | 0 | 0,0 | 8,8 | 0 | 0 | 29 / 0 / 0 / 403 |
| 2012 | 2030 | v2g | trafo | aus | 20 | 10 | 7 | 0 | 7 | 0,7 | 24,1 | – | – | 2 / 6 / 0 / 424 |
| 2012 | 2030 | v2g | trafo | an | 20 | 10 | 7 | 0 | 7 | 0,7 | 24,1 | 7 | 391 | 2 / 6 / 0 / 424 |
| 2012 | 2030 | v2g | trafo+leitung | aus | 20 | 10 | 0 | 0 | 0 | 0,0 | 24,1 | – | – | 2 / 0 / 0 / 430 |
| 2012 | 2030 | v2g | trafo+leitung | an | 20 | 10 | 0 | 0 | 0 | 0,0 | 24,1 | 0 | 0 | 2 / 0 / 0 / 430 |
| 2012 | 2040r | uncontrolled | trafo | aus | 20 | 298 | 101 | 0 | 12 | 11,0 | 0,0 | – | – | 214 / 11 / 89 / 118 |
| 2012 | 2040r | uncontrolled | trafo | an | 20 | 296 | 88 | 0 | 13 | 8,3 | 0,0 | 170 | 24817 | 231 / 11 / 71 / 119 |
| 2012 | 2040r | controlled | trafo | aus | 20 | 122 | 40 | 0 | 37 | 5,0 | 280,2 | – | – | 124 / 36 / 1 / 271 |
| 2012 | 2040r | controlled | trafo | an | 20 | 122 | 40 | 0 | 37 | 5,0 | 280,2 | 60 | 10626 | 124 / 36 / 1 / 271 |
| 2012 | 2040r | controlled | trafo+leitung | aus | 20 | 122 | 0 | 0 | 0 | 0,0 | 280,2 | – | – | 125 / 0 / 0 / 307 |
| 2012 | 2040r | controlled | trafo+leitung | an | 20 | 122 | 0 | 0 | 0 | 0,0 | 280,2 | 0 | 0 | 125 / 0 / 0 / 307 |
| 2012 | 2040r | v2g | trafo | aus | 20 | 33 | 39 | 0 | 39 | 5,0 | 508,3 | – | – | 27 / 37 / 0 / 368 |
| 2012 | 2040r | v2g | trafo | an | 20 | 33 | 39 | 0 | 39 | 5,0 | 508,3 | 60 | 10626 | 27 / 37 / 0 / 368 |
| 2012 | 2040r | v2g | trafo+leitung | aus | 20 | 33 | 0 | 0 | 0 | 0,0 | 508,4 | – | – | 27 / 0 / 0 / 405 |
| 2012 | 2040r | v2g | trafo+leitung | an | 20 | 33 | 0 | 0 | 0 | 0,0 | 508,4 | 0 | 0 | 27 / 0 / 0 / 405 |
| 2012 | 2040 | uncontrolled | trafo | aus | 20 | 324 | 160 | 0 | 11 | 18,9 | 0,0 | – | – | 169 / 11 / 157 / 95 |
| 2012 | 2040 | uncontrolled | trafo | an | 20 | 322 | 136 | 0 | 11 | 13,7 | 0,0 | 277 | 63552 | 203 / 10 / 123 / 96 |
| 2012 | 2040 | controlled | trafo | aus | 20 | 226 | 52 | 0 | 32 | 5,6 | 1091,6 | – | – | 222 / 31 / 12 / 167 |
| 2012 | 2040 | controlled | trafo | an | 20 | 226 | 51 | 0 | 32 | 5,6 | 1091,6 | 75 | 14611 | 224 / 31 / 10 / 167 |
| 2012 | 2040 | controlled | trafo+leitung | aus | 20 | 226 | 14 | 0 | 1 | 0,5 | 1092,8 | – | – | 226 / 1 / 6 / 199 |
| 2012 | 2040 | controlled | trafo+leitung | an | 20 | 226 | 12 | 0 | 2 | 0,4 | 1092,9 | 10 | 1764 | 228 / 1 / 4 / 199 |
| 2012 | 2040 | v2g | trafo | aus | 20 | 132 | 50 | 0 | 42 | 5,6 | 2207,3 | – | – | 130 / 40 / 3 / 259 |
| 2012 | 2040 | v2g | trafo | an | 20 | 132 | 49 | 0 | 42 | 5,5 | 2207,2 | 73 | 14252 | 132 / 40 / 1 / 259 |
| 2012 | 2040 | v2g | trafo+leitung | aus | 20 | 132 | 7 | 0 | 0 | 0,2 | 2209,9 | – | – | 130 / 0 / 3 / 299 |
| 2012 | 2040 | v2g | trafo+leitung | an | 20 | 132 | 6 | 0 | 0 | 0,2 | 2209,9 | 6 | 1240 | 132 / 0 / 1 / 299 |
| 2017 | heute | uncontrolled | trafo | aus | 20 | 4 | 0 | 0 | 0 | 0,0 | 0,0 | – | – | 0 / 0 / 0 / 432 |
| 2023 | heute | uncontrolled | trafo | aus | 20 | 2 | 0 | 0 | 0 | 0,0 | 0,0 | – | – | 0 / 0 / 0 / 432 |
| 2023 | 2030 | uncontrolled | trafo | aus | 20 | 52 | 4 | 0 | 4 | 0,6 | 0,0 | – | – | 46 / 5 / 0 / 381 |
| 2023 | 2030 | uncontrolled | trafo | an | 20 | 52 | 4 | 0 | 4 | 0,4 | 0,0 | 6 | 384 | 46 / 4 / 0 / 382 |
| 2023 | 2030 | controlled | trafo | aus | 20 | 6 | 4 | 0 | 4 | 0,5 | 0,0 | – | – | 0 / 5 / 0 / 427 |
| 2023 | 2030 | controlled | trafo | an | 20 | 6 | 4 | 0 | 4 | 0,5 | 0,0 | 5 | 376 | 0 / 5 / 0 / 427 |
| 2023 | 2030 | controlled | trafo+leitung | aus | 20 | 6 | 0 | 0 | 0 | 0,0 | 0,0 | – | – | 0 / 0 / 0 / 432 |
| 2023 | 2030 | controlled | trafo+leitung | an | 20 | 6 | 0 | 0 | 0 | 0,0 | 0,0 | 0 | 0 | 0 / 0 / 0 / 432 |
| 2023 | 2030 | v2g | trafo | aus | 20 | 0 | 4 | 0 | 4 | 0,5 | 0,3 | – | – | 0 / 5 / 0 / 427 |
| 2023 | 2030 | v2g | trafo | an | 20 | 0 | 4 | 0 | 4 | 0,5 | 0,3 | 5 | 376 | 0 / 5 / 0 / 427 |
| 2023 | 2030 | v2g | trafo+leitung | aus | 20 | 0 | 0 | 0 | 0 | 0,0 | 0,3 | – | – | 0 / 0 / 0 / 432 |
| 2023 | 2030 | v2g | trafo+leitung | an | 20 | 0 | 0 | 0 | 0 | 0,0 | 0,3 | 0 | 0 | 0 / 0 / 0 / 432 |
| 2023 | 2040r | uncontrolled | trafo | aus | 20 | 250 | 49 | 0 | 18 | 6,5 | 0,0 | – | – | 227 / 17 / 26 / 162 |
| 2023 | 2040r | uncontrolled | trafo | an | 20 | 248 | 44 | 0 | 16 | 4,7 | 0,0 | 73 | 11369 | 228 / 16 / 24 / 164 |
| 2023 | 2040r | controlled | trafo | aus | 20 | 38 | 34 | 0 | 33 | 4,1 | 6,0 | – | – | 33 / 30 / 0 / 369 |
| 2023 | 2040r | controlled | trafo | an | 20 | 38 | 34 | 0 | 33 | 4,1 | 6,0 | 46 | 7362 | 33 / 30 / 0 / 369 |
| 2023 | 2040r | controlled | trafo+leitung | aus | 20 | 38 | 0 | 0 | 0 | 0,0 | 6,0 | – | – | 33 / 0 / 0 / 399 |
| 2023 | 2040r | controlled | trafo+leitung | an | 20 | 38 | 0 | 0 | 0 | 0,0 | 6,0 | 0 | 0 | 33 / 0 / 0 / 399 |
| 2023 | 2040r | v2g | trafo | aus | 20 | 2 | 34 | 0 | 34 | 4,1 | 13,0 | – | – | 0 / 30 / 0 / 402 |
| 2023 | 2040r | v2g | trafo | an | 20 | 2 | 34 | 0 | 34 | 4,1 | 13,0 | 46 | 7362 | 0 / 30 / 0 / 402 |
| 2023 | 2040r | v2g | trafo+leitung | aus | 20 | 2 | 0 | 0 | 0 | 0,0 | 13,0 | – | – | 0 / 0 / 0 / 432 |
| 2023 | 2040r | v2g | trafo+leitung | an | 20 | 2 | 0 | 0 | 0 | 0,0 | 13,0 | 0 | 0 | 0 / 0 / 0 / 432 |
| 2023 | 2040 | uncontrolled | trafo | aus | 20 | 289 | 80 | 0 | 12 | 8,8 | 0,0 | – | – | 226 / 11 / 64 / 131 |
| 2023 | 2040 | uncontrolled | trafo | an | 20 | 288 | 71 | 0 | 12 | 6,6 | 0,0 | 127 | 18223 | 241 / 10 / 48 / 133 |
| 2023 | 2040 | controlled | trafo | aus | 20 | 136 | 36 | 0 | 35 | 4,6 | 57,4 | – | – | 138 / 31 / 1 / 262 |
| 2023 | 2040 | controlled | trafo | an | 20 | 136 | 36 | 0 | 35 | 4,6 | 57,4 | 51 | 8306 | 138 / 31 / 1 / 262 |
| 2023 | 2040 | controlled | trafo+leitung | aus | 20 | 136 | 0 | 0 | 0 | 0,0 | 57,4 | – | – | 140 / 0 / 0 / 292 |
| 2023 | 2040 | controlled | trafo+leitung | an | 20 | 136 | 0 | 0 | 0 | 0,0 | 57,4 | 0 | 0 | 140 / 0 / 0 / 292 |
| 2023 | 2040 | v2g | trafo | aus | 20 | 20 | 36 | 0 | 36 | 4,6 | 120,1 | – | – | 17 / 32 / 0 / 383 |
| 2023 | 2040 | v2g | trafo | an | 20 | 20 | 36 | 0 | 36 | 4,6 | 120,1 | 51 | 8306 | 17 / 32 / 0 / 383 |
| 2023 | 2040 | v2g | trafo+leitung | aus | 20 | 20 | 0 | 0 | 0 | 0,0 | 120,1 | – | – | 17 / 0 / 0 / 415 |
| 2023 | 2040 | v2g | trafo+leitung | an | 20 | 20 | 0 | 0 | 0 | 0,0 | 120,1 | 0 | 0 | 17 / 0 / 0 / 415 |

Wandzeiten der Matrix (je Wetterjahr parallel, 4 Worker, 20 Seeds je Einstellung, 2030 und 2040/2040r zusammen):

| Einstellung | Wandzeit |
|---|---|
| ungesteuert | 194–332 s |
| gesteuert, `trafo` | 192–306 s |
| gesteuert, `trafo+leitung` | 354–520 s |
| V2G, `trafo` | 205–323 s |
| V2G, `trafo+leitung` | 362–683 s |
| gesamte Matrix 2030/2040 | ca. 2 h |
| 2040r | ca. 1 h |

## Stichprobe und pandapower-Vergleich (Fix-Runde 4)

Je Gebietstyp drei Stationen nach dem P90 der Abnahmegrenze: höchster Wert, Median, unteres Viertel.
Abschnittstabelle aus heute, 2012, Seed 0. Kartenskizzen liegen in `docs/abnahme-screens/fix4-stichprobe-*.svg`:
grün < 80 %, orange 80–100 %, rot > 100 %, gestrichelt = Freileitung.

| Station | Gebiet | Gebäude | Abgänge | Abschnitte | Ausläufer | P90 Abnahme | km je Typ (Systeme) |
|---|---|---|---|---|---|---|---|
| 333 | stadt | 97 | 7 | 184 | 1 | 88,9 % | NAYY 4x150 2,91, NAYY 4x35 1,77, NAYY 4x240 0,13 |
| 3 | stadt | 20 | 2 | 40 | 0 | 60,0 % | NAYY 4x150 0,78, NAYY 4x35 0,38 |
| 329 | stadt | 35 | 4 | 58 | 0 | 49,0 % | NAYY 4x240 1,02, NAYY 4x35 0,69, NAYY 4x150 0,62 |
| 262 | ort | 47 | 3 | 94 | 0 | 81,8 % | NAYY 4x240 1,26, NAYY 4x150 1,15, NAYY 4x35 0,69 |
| 209 | ort | 59 | 4 | 125 | 1 | 46,4 % | NAYY 4x240 2,10, Al 4x95 1,75, NAYY 4x150 1,07, NAYY 4x35 0,85, Al 4x25 0,04 |
| 365 | ort | 17 | 7 | 33 | 1 | 35,3 % | NAYY 4x240 1,39, Al 4x95 0,78, NAYY 4x150 0,51, Al 4x25 0,15, NAYY 4x35 0,13 |
| 27 | streu | 12 | 3 | 26 | 1 | 77,9 % | Al 4x95 2,40, NAYY 4x240 1,05, Al 4x70 0,41, NAYY 4x150 0,25, Al 4x25 0,22, NAYY 4x35 0,04 |
| 243 | streu | 17 | 7 | 43 | 5 | 39,5 % | Al 4x95 2,52, Al 4x70 2,42, NAYY 4x150 1,68, NAYY 4x240 1,13, NAYY 4x50 0,73, NAYY 4x35 0,29, Al 4x25 0,05 |
| 186 | streu | 7 | 4 | 18 | 2 | 30,8 % | Al 4x95 5,16, NAYY 4x150 1,64, NAYY 4x240 1,24, Al 4x70 0,28, NAYY 4x35 0,05, Al 4x25 0,04, NAYY 4x50 0,03 |

Je Station die drei am stärksten ausgelasteten Abschnitte (Auslegung nach Regel, Grenze bei cos φ 0,97):

| Station | Abschnitt | Typ | Länge m | Knoten dahinter | Auslegung kW | Grenze kW | höchste Auslastung | Stunden > 100 % |
|---|---|---|---|---|---|---|---|---|
| 333 | 5 | NAYY 4x150 | 64,6 | 30 | 130,0 | 184,8 | 75,0 % | 0 |
| 333 | 7 | NAYY 4x150 | 20,6 | 29 | 125,6 | 184,8 | 72,9 % | 0 |
| 333 | 9 | NAYY 4x150 | 20,6 | 28 | 121,6 | 184,8 | 70,2 % | 0 |
| 3 | 1 | NAYY 4x150 | 21,2 | 19 | 86,8 | 184,8 | 60,0 % | 0 |
| 3 | 3 | NAYY 4x150 | 10,9 | 12 | 57,6 | 184,8 | 39,2 % | 0 |
| 3 | 6 | NAYY 4x150 | 22,8 | 11 | 53,6 | 184,8 | 37,1 % | 0 |
| 329 | 23 | NAYY 4x35 (HA) | 37,7 | 1 | 41,9 | 82,7 | 49,2 % | 0 |
| 329 | 12 | NAYY 4x150 | 87,5 | 8 | 100,8 | 184,8 | 39,3 % | 0 |
| 329 | 28 | NAYY 4x35 (HA) | 9,7 | 1 | 24,8 | 82,7 | 28,5 % | 0 |
| 262 | 23 | NAYY 4x150 | 30,1 | 7 | 176,7 | 184,8 | 80,5 % | 0 |
| 262 | 72 | NAYY 4x35 (HA) | 16,4 | 1 | 80,1 | 82,7 | 80,5 % | 0 |
| 262 | 2 | NAYY 4x240 ×2 | 99,1 | 27 | 455,0 | 420,7 | 57,9 % | 0 |
| 209 | 86 | NAYY 4x35 (HA) | 14,2 | 1 | 24,8 | 82,7 | 37,5 % | 0 |
| 209 | 0 | NAYY 4x150 | 50,6 | 10 | 71,5 | 184,8 | 34,6 % | 0 |
| 209 | 111 | NAYY 4x35 (HA) | 9,4 | 1 | 18,7 | 82,7 | 20,8 % | 0 |
| 365 | 31 | Al 4x25 (HA) | 13,8 | 1 | 7,6 | 90,7 | 22,0 % | 0 |
| 365 | 21 | NAYY 4x35 (HA) | 13,1 | 1 | 26,3 | 82,7 | 15,7 % | 0 |
| 365 | 16 | NAYY 4x150 | 80,9 | 1 | 22,2 | 184,8 | 14,6 % | 0 |
| 27 | 17 | NAYY 4x35 (HA) | 15,3 | 1 | 46,8 | 82,7 | 55,4 % | 0 |
| 27 | 10 | NAYY 4x240 | 1054,6 | 1 | 46,8 | 210,3 | 21,8 % | 0 |
| 27 | 24 | Al 4x25 (HA) | 12,7 | 1 | 0,0 | 90,7 | 17,8 % | 0 |
| 243 | 42 | NAYY 4x35 (HA) | 61,8 | 1 | 0,0 | 82,7 | 21,7 % | 0 |
| 243 | 28 | NAYY 4x35 (HA) | 28,8 | 1 | 18,2 | 82,7 | 20,5 % | 0 |
| 243 | 3 | NAYY 4x50 | 16,6 | 3 | 45,0 | 96,8 | 19,8 % | 0 |
| 186 | 17 | Al 4x25 (HA) | 14,5 | 1 | 27,8 | 90,7 | 17,4 % | 0 |
| 186 | 12 | NAYY 4x35 (HA) | 14,6 | 1 | 27,8 | 82,7 | 14,7 % | 0 |
| 186 | 16 | Al 4x25 (HA) | 14,5 | 1 | 8,8 | 90,7 | 14,3 % | 0 |

Von Hand geprüft:

- In stadt und ort ist der Strang nirgends schwächer als NAYY 4x150 bzw. Al 4x95 (Mindestquerschnitt).
- Die höchsten Auslastungen heute liegen bei 75–81 % (Stationen 333, 262) an Strangabschnitten mit 10–20 Gebäuden.
- Hausanschlüsse (NAYY 4x35) sind oft der am stärksten ausgelastete Abschnitt kleiner Stationen. Bei Station 27
  liegen 55 % auf einem Anschluss mit 47 kW Auslegung (großes Mehrfamilienhaus).
- Station 27, Abschnitt 10: 1 055 m NAYY 4x240 zu einem einzelnen Knoten, ein langer Stich in Streulage. Der
  Querschnitt ist durch den Spannungsfall bestimmt; ein realer Betreiber würde hier eher eine Station setzen
  (siehe reine Spannungsfälle).

pandapower-Vergleich: gleiches Verfahren wie im ersten Lauf, in den 24 stärksten Stunden, heute und 2040r (2012,
Seed 0). Alle Lastflüsse konvergierten.

| Station | heute: gridsim max | pandapower max | Abw. Mittel (Pp) | Abw. P95 (Pp) | Abw. rel. Median | U min (pu) | 2040r: gridsim max | pandapower max | Abw. Mittel (Pp) | Abw. P95 (Pp) | Abw. rel. Median | U min (pu) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 333 | 75,0 % | 77,4 % | 0,9 | 2,2 | 3,0 % | 0,96 | 163,6 % | 177,0 % | 2,4 | 10,1 | 6,1 % | 0,90 |
| 3 | 60,0 % | 60,8 % | 0,3 | 0,6 | 1,4 % | 0,98 | 112,2 % | 115,2 % | 0,7 | 1,9 | 2,0 % | 0,96 |
| 329 | 48,8 % | 50,7 % | 0,8 | 1,6 | 3,2 % | 0,96 | 55,0 % | 58,0 % | 0,8 | 2,1 | 4,3 % | 0,95 |
| 262 | 80,5 % | 83,0 % | 0,7 | 2,0 | 2,1 % | 0,96 | 109,3 % | 116,1 % | 1,3 | 3,4 | 3,9 % | 0,93 |
| 209 | 37,5 % | 37,8 % | 0,1 | 0,2 | 1,0 % | 0,99 | 71,1 % | 74,8 % | 0,8 | 2,2 | 2,5 % | 0,94 |
| 365 | 22,7 % | 22,6 % | -0,0 | 0,1 | -0,2 % | 1,00 | 30,8 % | 31,9 % | 0,5 | 0,8 | 3,1 % | 0,96 |
| 27 | 54,8 % | 57,7 % | 1,4 | 2,6 | 4,5 % | 0,95 | 78,2 % | 80,8 % | 0,9 | 2,2 | 3,6 % | 0,94 |
| 243 | 21,7 % | 21,2 % | -0,1 | 0,4 | -1,3 % | 0,96 | 53,1 % | 56,4 % | 0,7 | 1,8 | 2,5 % | 0,92 |
| 186 | 17,4 % | 18,4 % | 0,9 | 1,0 | 5,4 % | 0,94 | 44,7 % | 47,5 % | 1,1 | 2,8 | 4,6 % | 0,84 |

Über alle Abschnittsstunden ab 10 % Auslastung:

| Fall | Abschnittsstunden | Abweichung Mittel | Abweichung P95 | Abweichung Max | relativ Median | relativ P95 | Überlast uneinig |
|---|---|---|---|---|---|---|---|
| heute | 2 571 | +0,7 Pp | 2,1 Pp | 2,9 Pp | +2,5 % | +4,1 % | 0 |
| 2040r | 6 452 | +1,4 Pp | 4,5 Pp | 13,5 Pp | +3,9 % | +8,9 % | 23 von 234 |

Mit dem stärkeren Netz sind die Spannungen höher (U min 0,84–1,00 pu) und die Abweichung kleiner als im ersten
Lauf. Die radiale Summation liegt weiter leicht unter dem Lastfluss.

## Dashboard-Prüfung (Fix-Runde 4)

API aus dem Arbeitsordner auf hetzner (`127.0.0.1:17099`, `GRIDSIM_PREPARED=prepared-ns-fix4`,
`GRIDSIM_CACHE=cache-fix4`, 1 Worker), Seite `site/` mit dem aktuellen `web/gridsim/`, SSH-Tunnel, Playwright
(Chromium, 1440 × 900). Läufe heute und 2030 (2012, ungesteuert, 20 Seeds aus dem Cache, 8,1 s), Leitungsebene
ein, Schalter „Control limits“ und „Grid storage“ umgestellt.

- Überschrift „Regional simulation: all 432 transformers in the Steyr area“, Kachel „Transformers overloaded“
  „11 of 432“ (heute) bzw. „127 of 432“ (2030). Die feste 257 ist weg.
- Konsole: keine Fehler und keine Warnungen aus Seite oder MapLibre; alle Kartenkacheln geladen.
- Karte 2030: fast nur „Transformer first“ (blau), wenige „Line first“ im Zentrum von Steyr. Das passt zur Matrix.
- Screenshots (ersetzen die des ersten Laufs): `docs/abnahme-screens/dashboard-1-start.png`,
  `dashboard-2-run-heute.png`, `dashboard-2-run-2030.png`, `dashboard-3-lines-heute.png`,
  `dashboard-3-lines-2030.png`, `dashboard-4-switches.png`.
- Szenario `2040r` ist im Dashboard als „2040 (50 % heat pumps)“ wählbar.

## Abweichungen und Entscheidungen

Fix-Runde 4 (Owner, 25./26.10.2026):

- **Reine Spannungsfälle zählen nicht zur 10-%-Grenze:** Abgänge, die thermisch reichen, aber den Spannungsfall
  bzw. die -anhebung auch mit dem stärksten Typ nicht einhalten, stehen unter eigenem Grund
  (`SizedGrid.marked_voltage`). Sie lösen keine Zusatzstation aus und werden getrennt berichtet. Zu lange Abgänge
  und Stromüberschreitung zählen weiter. Begründung: Die Spannung wird nicht bewertet (Entscheidung 2).
- **Szenario 2040r** (50 % WP, 0,60 E-Autos) als Hauptergebnis 2040; 2040 (70 %) als Stresstest.
- **`MODEL_VERSION` 2026-10-26.5**, neue Variante `prepared-ns-fix4`. Abnahmegrenze bestanden, Matrix gerechnet.

Fix-Runde 3 (Controller, 25.10.2026):

- **Wärmepumpen in der Bemessung:** Summe der k größten vollen Leistungen statt k × Mittel; k bleibt das P90.
- **`MODEL_VERSION` 2026-10-26.4**, neue Variante `prepared-ns-fix3`.
- **Halt bei markierten Abgängen über 10 %:** keine Abnahmegrenze, keine Matrix.

Fix-Runde 2 (Owner „Ist-Abgleich“, 25.10.2026):

- **heute aus realen Daten:** WP 0,23 (21,4 % der Haushalte), E-Autos 0,076 je Haushalt, Override in
  `profiles.SCENARIOS`; legacy unverändert.
- **Mindestquerschnitt** im Strang in stadt/ort: NAYY 4x150 bzw. Al 4x95.
- **`MODEL_VERSION` 2026-10-26.3.**
- Neue Variante `prepared-ns-fix2`; fix1 bleibt erhalten. Matrix nur bei bestandener Grenze.

Fix-Runde 1 (Controller, 25.10.2026):

- **Neue Bemessungsregel** (siehe oben): Haushalte nicht unter der H0-Spitze, ganze Geräte als P90 der
  Binomialverteilung.
- **Abnahmeregel:** 5 von n Stationen (465 im ersten Lauf, 487 in Fix-Runde 1), nicht 5 von 257.
- **Matrix nur bei bestandener Grenze;** keine weiteren Regeländerungen durch den Umsetzer.
- **Netzspeicher-Bemessung** bleibt unverändert.
- **`MODEL_VERSION` erhöht.** Der Grund sind veraltete Caches mit `trafo+leitung` und die Regeländerung.

Aus dem Ledger:

Aus dem Ledger des Controllers (`progress.md`, „Ruling“) und dem Brief; für die Lesart der Zahlen wichtig:

- **Heimspeicher nicht abrufbar:** Heimspeicher-Strategien (base, forecast, room) bleiben unverändert; gridsim
  hat keine Abruflogik für Heimspeicher (Spec 4.5 setzt sie voraus). Abrufe je Abgang macht nur der Netzspeicher.
- **V2G-Nachladen im Leitungsmodus je Knoten begrenzt** (im Trafo-Modus je Station), nur im neuen Modus.
- **Netzspeicher sieht bei gesteuertem Laden und V2G nur den Grundfluss** (Reihenfolge Speicher vor
  E-Auto-Steuerung); er kann daher für E-Auto-Spitzen zu klein bemessen sein.
- **Ausläufer:** Ferne Abgangsenden mit weniger als 6 Wohngebäuden bekommen keine eigene Station, bleiben an ihrer
  Station, werden mit dem nötigen Typ bemessen und zählen nicht zur 10-%-Grenze.
- **Zusatzstationen:** Gruppen bis 105 Gebäude (3,5 Abgänge × 30) mit Radiusbedingung; nur Gebäude der markierten
  Abgänge wechseln die Station; 2 Durchgänge; kleine Zusatzstationen werden aufgelöst.
- **Kabelanteil nach Trassenlänge** (gemeinsame Gräben und Parallelsysteme einmal) als Abnahmegröße, Kabellänge
  zusätzlich berichtet.
- **Kalibrierung der Gebietsschwellen:** stadt 35 m, ort 85 m (Startwerte 30/80 m ergaben 68,6 % Kabel; +5 m ist
  die kleinste Verschiebung ins Band), danach fest.
- Weitere: Direktabgang ab mehr als 30 kWp; markierte Abgänge = zu lang ODER Bemessung scheitert; Grenzstrom
  `i_max_a` enthält die Parallelführung; Hausanschlüsse werden nicht bemessen, aber bewertet; Stationsfarbe =
  häufigste Engpassklasse über die Seeds (Gleichstand: schwerere).

### Im Zuge der Abnahme behoben

Im Grenzmodus `trafo+leitung` füllten gesteuertes Laden, Nachladen und V2G den Trafo-Raum exakt bis `kva`; durch
Rundung lag der Stationsfluss bis 10⁻⁶ kW über `kva`, und die Trafo-Kennzahl zählte das als Engpass (2040, 2023,
Seed 0: 151 statt 129 Stationen bei gesteuertem Laden, 82 statt etwa 20 bei V2G). Echte Überlast war gleich. Fix:
Abstand 1 µW am Trafo (`control_lines._TRAFO_EPS_KW`), Test `test_trafo_never_above_kva_by_rounding`, Commit
`66ca7b7`. Der Modus `trafo` ist nicht betroffen (bitgleich). Alle Läufe mit `trafo+leitung` in diesem Bericht
sind mit dem Fix gerechnet.

## Grenzen der Aussage

- **Synthetisches Netz:** Lage, Länge und Querschnitt der NS-Leitungen sind aus Straßen, Gebäuden und einer
  Planungsregel abgeleitet, nicht aus Netzdaten des Betreibers. Einzelne Stationen können stark abweichen; belastbar
  sind nur Größenordnung und Richtung über die Region. Die Abnahmegrenze ist verfehlt: Das synthetische Netz ist
  heute schon schwächer als ein real betriebenes, die Leitungszahlen für 2030/2040 sind deshalb zu hoch.
- **Kein Spannungsurteil:** Bewertet wird nur thermisch (Strom gegen Grenzstrom). Spannungsfall und -anhebung
  sind in keiner Kennzahl; der pandapower-Vergleich zeigt in 2040 Spannungen bis 0,69 pu, die im realen Netz
  längst zu Maßnahmen geführt hätten. Wo die Spannung zuerst begrenzt (laut Literatur häufig in ländlichen
  Netzen), unterschätzt die thermische Sicht den Bedarf.
- **Radiale Summation:** ohne Verluste und bei 400 V; gegenüber dem Lastfluss 4 % (heute) bis 12 % (2040) zu
  niedrig, bei tiefen Spannungen mehr.
- **Trafo-Bemessung:** Trafos der Zusatzstationen und der bisherigen Stationen kommen aus `trafo_kva`
  (2–3 kVA je Wohnung, auf Normgrößen gerundet), nicht aus Betreiberdaten. Die Trafo-Kennzahlen hängen direkt
  daran; ein Trafo eine Stufe größer verschiebt „Trafo zuerst“ zu „Leitung zuerst“.
- **Reine Spannungsfälle aus der 10-%-Grenze genommen:** 122 Abgänge an 93 Stationen (21,5 %; vor allem ort und
  streu) halten den Spannungsfall bzw. die -anhebung auch mit 2 × 4x240 nicht ein. Sie zählen nach
  Owner-Entscheidung nicht zur 10-%-Grenze und lösen keine Zusatzstation aus. Das markiert die Stellen, an denen
  reale Netzbetreiber wegen der Spannung handeln müssten (eigene Station, Spannungsregelung, Blindleistung). Ihre
  thermischen Ergebnisse sind gerechnet; der Spannungsfall dort ist im Modell nicht eingehalten.
- **Ungesteuertes Laden mit 11 kW ist konservativ:** Die Simulation lässt E-Autos nach der Ankunft am Abend mit
  voller Wallbox-Leistung laden. Salzburg Netz misst an großen Trafostationen eine spezifische Zusatzlast von etwa
  0,5 kW je Fahrzeug (99-%-Quantil, Maier/Groiß, EnInnov 2026). Die E-Auto-Engpässe sind daher eine Obergrenze.
- **Mindestquerschnitt ist übliche Praxis, kein Steyr-Beleg:** NAYY 4x150 bzw. Al 4x95 als kleinster
  Strangquerschnitt in stadt und ort entspricht verbreiteter Planungspraxis für neue Ortsnetze. Für das reale
  Netz in Steyr gibt es dafür keinen Beleg; ältere Netzteile können schwächer sein. Das Netz ist damit eher stärker
  als das reale, und Leitungsengpässe der Zukunftsszenarien werden eher unterschätzt.
- **Trafo-Überlast „heute“ trotz realer Last:** Mit den Anteilen aus dem Ist-Abgleich sind im Kältejahr 2012
  „heute“ im Median 11 von 432 Trafos überlastet (Fix-Runde 4; 2017: 3,5, 2023: 2; dritter Lauf: 11 von 508). Die realen Trafos tragen die
  heutige Last; das Modell überschätzt also entweder die Last am Trafo oder unterschätzt seine Belastbarkeit.
  Diagnose aus den Seeds 2012 des dritten Laufs: Die am häufigsten überlasteten Trafos haben 125 kVA (einzelne 160/250 kVA) bei
  2,0–2,2 kVA je Haushalt, am unteren Rand der Regel `trafo_kva` (2–3 kVA je Wohnung, Median aller Stationen
  3,0). Die meisten sind synthetische Stationen; die Überlast dauert nur 0–1 Stunde im Jahr. Mögliche Ursachen:
  - **Trafo-Leistungen nicht aus Daten:** Bemessungsleistungen kommen aus der Regel, nicht vom Netzbetreiber
    (OSM hat keine Leistungsangaben). Reale Stationen dürften oft größer sein (Netz OÖ im Mittel ca. 383 kVA je
    Station), und für die Zusatzstationen gibt es gar keine Vorlage.
  - **Wärmepumpenanteil je Gebäude:** gridsim zieht Wärmepumpen je Wohngebäude. Für 21,4 % der Haushalte braucht
    es einen Gebäudeanteil von 23 %, und dabei bekommen auch Mehrfamilienhäuser mit derselben Wahrscheinlichkeit
    eine Wärmepumpe für das ganze Haus. Real stehen Wärmepumpen überwiegend in Einfamilienhäusern; die Last in
    dichten Gebieten ist damit eher zu hoch.
  - **Wärmepumpen ohne Rückhalt:** Alle laufen in der Kältewelle ohne Versatz der Heizgrenze darüber hinaus, ohne
    Zweitheizung (Holz, vorhandener Kessel) und ohne EVU-Sperrzeiten.
  - **Stundengrenze 100 % kva:** Ölgekühlte Trafos vertragen kurze Überlast (Stunden) ohne Schaden; das Modell
    zählt jede Stunde über `kva` als Engpass.
  - **Haushaltslast:** einheitlich 3 000 kWh je Haushalt mit H0-Profil, ohne Abweichung je Gebiet.
- **Ist-Abgleich mit Landeswerten:** E-Autos und Wärmepumpen „heute“ kommen aus Werten für ganz OÖ
  (Bezirkswerte nicht veröffentlicht); der Wärmepumpenanteil stammt aus dem Winter 2023/24.
- **P90-Bemessung überdimensioniert eher:** Ganze Geräte als P90 der Binomialverteilung je Abschnitt bemessen
  jeden Abschnitt für ein Zehntel-Ereignis, und zwar alle Abschnitte zugleich. Ein Abschnitt mit einem
  Haushalt bekommt schon eine volle Wärmepumpe (P(keine WP) = 85 % < 90 %). Über die Region entsteht so ein
  stärkeres Netz als der Erwartungswert verlangt: mehr 4x150/4x240, mehr scheiternde Bemessung, mehr markierte
  Abgänge. Leitungsengpässe in Zukunftsszenarien werden damit eher unterschätzt.
- **Zufall und Seeds:** Wärmepumpen und E-Autos sind je Seed zufällig verteilt; alle Einstellungen haben
  20 Seeds, berichtet ist der Median. Bänder siehe `region.csv` je Einstellung im Cache.
- **Netzspeicher:** Ort und Größe aus einem Auslegungslauf (Seed 0) je Einstellung, mit perfekter Tagesprognose;
  Kostensätze für Leitungen sind Platzhalter.

## Vierter Lauf, verworfen (Fix-Runde 3, `MODEL_VERSION` 2026-10-26.4)

Kernzahlen: 525 Stationen, 61 Stationen (11,6 %) mit markiertem Abgang, fast alle nur wegen des Spannungsfalls (57 Stationen, ort/streu). Halt vor der Abnahmegrenze, keine Abnahmezahlen. Daraufhin hat der Owner reine Spannungsfälle aus der 10-%-Grenze genommen (Fix-Runde 4).

#### Kurzfassung des vierten Laufs

- **Angehalten vor der Abnahmegrenze:** Mit der vervollständigten Regel für Wärmepumpen (Summe der k größten
  Leistungen) haben auf `prepared-ns-fix3` (525 Stationen) **61 Stationen (11,6 %) einen markierten Abgang**,
  über der 10-%-Grenze (Spec Entscheidung 7, Global Constraints). Nach Vorgabe wurde die Abnahmegrenze nicht
  gerechnet. Es gibt keine Matrix und keine Dashboard-Prüfung.
- **Ursache:** 57 der 61 Stationen sind markiert, weil die Bemessung am **Spannungsfall** scheitert (alle 71
  betroffenen Abgänge; thermisch reicht 2 × 4x240 überall). Sie liegen in ort (26) und streu (29), kaum in stadt (2).
  - Die Auslegungslasten dort sind moderat (Median 44 kW je Abgang, Grenze 2 × 4x240 bei 421 kW).
  - Die Abgänge sind aber lang. Mit den schwereren Wärmepumpen hält ein Teil auch mit dem stärksten Typ die 5 %
    im Bezug bzw. 3 % bei Einspeisung nicht.
  - Nur 8 Stationen sind wegen zu langer Abgänge mit Weilern markiert.
- Netzbau sonst: Kabelanteil nach Trassenlänge 75,0 %. NAYY 4x50 3 % des Strangs, 4x150 43 %, 4x240 24 %,
  Al 4x95 27 %.
- Ist-Abgleich und Mindestquerschnitt aus Fix-Runde 2 gelten unverändert. Der letzte Lauf mit Abnahmezahlen ist
  der dritte (verworfen): 6 Stationen über 100 %, keine über 120 % bei 508 Stationen.
- Zu entscheiden (Controller/Owner, nicht umgesetzt):
  - Die 10-%-Grenze für Abgänge, die nur am Spannungsfall scheitern, gesondert behandeln. Die Spannung wird
    ohnehin nicht bewertet (Entscheidung 2); diese Abgänge wären mit 2 × 4x240 thermisch ausreichend.
  - Oder einen dritten Durchgang Zusatzstationen zulassen.

### Vierter Lauf: Netzbau (`prepared-ns-fix3`)

`gridsim prepare-feeders --input …/steyr-pv-2026-10-24/input --prepared prepared --extra-stations --out
prepared-ns-fix3` (27 s; fix2 unverändert erhalten).

| Kennzahl | Fix-Runde 3 | Fix-Runde 2 (verworfen) | Ziel |
|---|---|---|---|
| Stationen | 525 | 508 | – |
| Stationen mit markiertem Abgang | **61 (11,6 %)** | 50 (9,8 %) | ≤ 10 % |
| davon zu lang / Bemessung scheitert (Stationen) | 8 / 57 | 9 / 45 | – |
| markierte Abgänge | 87 | 79 | – |
| Kabelanteil nach Trassenlänge | 75,0 % | 75,0 % | 79 % (Band 74–84 %) |
| NS-Trasse je Station | 1,83 km | 1,90 km | ca. 2,7 km |
| Abgänge je Station (Mittel) | 4,05 | 4,14 | 3,4–3,8 |
| Gebietstypen stadt / ort / streu | 157 / 257 / 111 | – | – |
| Ausläufer (Abgänge an Stationen) | 360 an 190 | – | – |

| Typ | km | Anteil |
|---|---|---|
| NAYY 4x50 | 44,9 | 2,9 % |
| NAYY 4x150 | 673,0 | 42,8 % |
| NAYY 4x240 | 377,0 | 24,0 % |
| Al 4x70 | 49,6 | 3,2 % |
| Al 4x95 | 428,7 | 27,3 % |
| NAYY 4x35 (Hausanschluss) | 269,3 | 89,0 % |
| Al 4x25 (Hausanschluss) | 33,2 | 11,0 % |

Zusatzstationen: 305 geplant, 36 kleine wieder aufgelöst, 269 behalten (525). Der Anteil der Stationen mit
markiertem Abgang sank von 68,9 % (Ausgangsnetz) über 23,9 % (Durchgang 1) auf 11,6 % (Durchgang 2). Zwei
Durchgänge sind das Maximum der Regel.

## Dritter Lauf, verworfen (Fix-Runde 2, `MODEL_VERSION` 2026-10-26.3)

Kernzahlen: 508 Stationen, Abnahmegrenze 6 Stationen über 100 % und keine über 120 % (nicht bestanden, nur Wetterjahr 2012), markierte Abgänge 9,8 %, Kabelanteil 75,0 %, NAYY 4x150 47 % des Strangs. Regel wie heute, aber Wärmepumpen als k × mittlere Leistung. Ist-Abgleich und Mindestquerschnitt wie heute.

#### Kurzfassung des dritten Laufs

- **Die Abnahmegrenze „heute“ ist knapp nicht bestanden:** Auf `prepared-ns-fix2` (508 Stationen) liegen im P90
  über 20 Seeds **6 Stationen über 100 %** und **keine über 120 %**. Die Regel erlaubt höchstens 5 von 508. Alle 6
  liegen nur im Kältejahr 2012 darüber (P90 100,0–108,4 %); 2017 und 2023 liegt keine Station über 100 %. Nach
  Vorgabe keine eigene Regeländerung, keine Vergleichsmatrix, keine neue Dashboard-Prüfung.
- **Markierte Abgänge:** 50 von 508 Stationen (9,8 %), innerhalb der 10-%-Grenze.
- **Ist-Abgleich „heute“:**
  - E-Autos: 0,076 je Haushalt. Statistik Austria zählt 51 343 Elektro-Pkw in OÖ (31.12.2025), dem stehen
    672 647 Privathaushalte gegenüber. Bisher galten 0,08 aus legacy.
  - Wärmepumpen: 21,4 % der Hauptwohnsitze in OÖ heizen mit „Solar, Wärmepumpen“ (Statistik Austria,
    MZ Energieeinsatz der Haushalte 2023/24). Bisher galten 15 %; im Modell steht jetzt `wp_share` 0,23, was
    haushaltsgewichtet 21,4 % ergibt.
  - Eine Quelle für den Anteil der 11-kW-Wallboxen gibt es nicht; es bleibt bei 70 %.
- **Trafo-Kennzahlen heute,** Stationen mit Trafo-Engpass (Median) auf `prepared-ns-fix2`, alte Anteile → neue:
  2012: 2 → 11, 2017: 0,5 → 3, 2023: 0 → 1,5.
- **Mindestquerschnitt** im Strang in stadt und ort: NAYY 4x150 bzw. Al 4x95. NAYY 4x50 sinkt auf 3 % des
  Strangs, NAYY 4x150 steigt auf 47 %.
- **Rest-Ursache:** Die 6 Stationen (5 stadt, 1 ort) sind an einem Strang-Abschnitt NAYY 4x150 (4) bzw. 4x240 (2)
  mit 13–27 Gebäuden überlastet, im Median 3 Stunden im Jahr, an Abenden im Februar 2012.
  - Anteile im Median: Wärmepumpen 135 kW, Haushalte 52 kW, E-Autos 11 kW; zusammen 196 kW.
  - Auslegung 181 kW, Grenze 185 kW.
  - Ausschlaggebend sind die Wärmepumpen in der Kältewelle: 9 Knoten mit WP gegen k ganze WP × mittlere Leistung
    in der Auslegung.

### Dritter Lauf: Plausibilität des Netzbaus (`prepared-ns-fix2`)

`gridsim prepare-feeders --input …/steyr-pv-2026-10-24/input --prepared prepared --extra-stations --out
prepared-ns-fix2` (fix1 bleibt unverändert erhalten).

| Kennzahl | Fix-Runde 2 | Fix-Runde 1 (verworfen) | erster Lauf (verworfen) | Ziel |
|---|---|---|---|---|
| Stationen | 508 | 487 | 465 | – |
| Kabelanteil nach Trassenlänge (Abnahmegröße) | 75,0 % | 74,7 % | 74,3 % | 79 % (Band 74–84 %) |
| NS-Trasse je Station | 1,90 km | 1,98 km | 2,06 km | ca. 2,7 km |
| NS-Kabellänge je Station (Systeme einzeln) | 3,02 km | 3,25 km | 3,10 km | ca. 2,7 km |
| Abgänge je Station (Mittel) | 4,14 | 4,28 | 4,36 | 3,4–3,8 |
| Stationen mit markiertem Abgang | **50 (9,8 %)** | 51 (10,5 %) | 29 (6,2 %) | ≤ 10 % |
| davon zu lang / Bemessung scheitert (Stationen) | 9 / 45 | 13 / 42 | 11 / 20 | – |

Typverteilung (km, parallele Systeme einzeln; Anteil am Strang bzw. an den Hausanschlüssen):

| Typ | Fix-Runde 2 km | Anteil | Fix-Runde 1 Anteil | erster Lauf Anteil |
|---|---|---|---|---|
| NAYY 4x50 | 45,7 | 3,0 % | 29,2 % | 46,0 % |
| NAYY 4x150 | 718,0 | 46,9 % | 17,6 % | 12,2 % |
| NAYY 4x240 | 301,7 | 19,7 % | 23,2 % | 13,9 % |
| Al 4x70 | 53,2 | 3,5 % | 7,5 % | 13,2 % |
| Al 4x95 | 414,4 | 27,0 % | 22,4 % | 14,6 % |
| NAYY 4x35 (Hausanschluss) | 269,8 | 89,2 % | 88,4 % | 87,3 % |
| Al 4x25 (Hausanschluss) | 32,8 | 10,8 % | 11,6 % | 12,7 % |

Zusatzstationen: 284 geplant, 32 kleine wieder aufgelöst, 252 behalten (508). Der Anteil der Stationen mit
markiertem Abgang sank von 66,9 % (Ausgangsnetz) über 21,3 % (Durchgang 1) auf 9,8 % (Durchgang 2).

### Dritter Lauf: Abnahmegrenze „heute“ (Fix-Runde 2)

Gleiche Einstellung wie zuvor (heute mit den Anteilen aus dem Ist-Abgleich, PV 1,0, Speicher base, ungesteuert,
`trafo`, ohne Netzspeicher), 2012/2017/2023, je 20 Seeds. 8 Worker, je Wetterjahr etwa 93 s; Cache `cache-fix2/`.

| Wetterjahr | Seeds | Stationen > 100 % | Stationen > 120 % | Median P90 | Max P90 |
|---|---|---|---|---|---|
| 2012 | 20 | 6 | 0 | 48,8 % | 108,4 % |
| 2017 | 20 | 0 | 0 | 43,2 % | 98,7 % |
| 2023 | 20 | 0 | 0 | 40,5 % | 88,7 % |
| alle (Maximum je Station) | 20 | **6** | **0** | 48,9 % | 108,4 % |

**Ergebnis: nicht bestanden** (Regel: höchstens 5 von 508 über 100 %, keine über 120 %). Die Grenze ist um eine
Station verfehlt. Zwei der sechs liegen gerade an der Grenze (Station 102: P90 100,0 %, Station 261: 100,5 %).

#### Diagnose (Wetter 2012, je Station der Seed am nächsten am P90)

| Station | Gebiet | P90 | schlimmster Abschnitt | Länge | Gebäude dahinter | Überlaststunden im Seed |
|---|---|---|---|---|---|---|
| 10 | stadt | 108,4 % | NAYY 4x150 | 35 m | 25 | 15 |
| 343 | stadt | 108,3 % | NAYY 4x240 | 24 m | 24 | 12 |
| 14 | stadt | 104,6 % | NAYY 4x150 | 24 m | 25 | 4 |
| 50 | stadt | 102,6 % | NAYY 4x150 | 29 m | 27 | 2 |
| 261 | ort | 100,5 % | NAYY 4x150 | 34 m | 13 | 1 |
| 102 | stadt | 100,0 % | NAYY 4x240 | 53 m | 26 | 0 |

- Immer Strang, einfach geführt, nicht im Ausläufer, nicht markiert, Richtung Bezug. Zeitpunkt: Abende im
  Februar 2012 (Kältewelle).
- Alle überlasteten Abschnitte zusammen: 0,22 km (Fix-Runde 1: 0,8 km; erster Lauf: 8,5 km).
- Zerlegung des schlimmsten Abschnitts in der Spitzenstunde, Median über die 6 Stationen:

| Anteil | kW |
|---|---|
| Wärmepumpen (9 Knoten mit WP) | 135 |
| Haushalte | 52 |
| E-Autos | 11 |
| **Summe** | **196** |
| Auslegung | 181 |
| Grenze (meist NAYY 4x150) | 185 |

- Die Lücke kommt aus den Wärmepumpen in der Kältewelle. Die Regel rechnet k ganze Wärmepumpen × mittlere
  Leistung der berechtigten Knoten; ein Seed, der viele Wärmepumpen auf große Mehrfamilienhäuser setzt, liegt
  darüber (wie schon in Fix-Runde 1 beschrieben). E-Autos spielen hier kaum eine Rolle.
- Mögliche nächste Schritte (Entscheidung beim Controller/Owner, nicht umgesetzt): die k größten WP-Leistungen
  hinter dem Abschnitt statt k × Mittel; oder die Abnahmegrenze für 2012 als Extremjahr gesondert betrachten.
  Die Grenze selbst bleibt nach Vorgabe unverändert.

#### Nicht gerechnet

Vergleichsmatrix 2030/2040, erneute Dashboard-Prüfung und Neubewertung der Netzspeicher-Bemessung nur bei
bestandener Grenze (Vorgabe). Die Zahlen dazu stehen beim ersten Lauf und gelten für dessen Netz. Die
Netzspeicher-Bemessung ist unverändert.

## Zweiter Lauf, verworfen (Fix-Runde 1, `MODEL_VERSION` 2026-10-26.2)

Kernzahlen: 487 Stationen, Abnahmegrenze 29 Stationen über 100 % und 5 über 120 % (nicht bestanden), markierte Abgänge 10,5 % (über der Grenze), Kabelanteil 74,7 %, NAYY 4x50 29 % des Strangs. Bemessungsregel wie heute (H0-Spitze, ganze Geräte P90), aber mit den legacy-Anteilen heute (15 % WP, 0,08 E-Autos) und ohne Mindestquerschnitt.

#### Kurzfassung des zweiten Laufs

- **Die Abnahmegrenze „heute“ ist auch mit der neuen Bemessungsregel nicht bestanden**, aber deutlich näher:
  Auf der neu gebauten Variante `prepared-ns-fix1` (487 Stationen) liegen im P90 über 20 Seeds **29 Stationen über
  100 %** und **5 über 120 %** (Regel: höchstens 5 von 487 über 100 %, keine über 120 %). Erster Lauf: 105 und 63.
  Keine weitere Regeländerung durch den Umsetzer; die Vergleichsmatrix wurde nach Vorgabe nicht neu gerechnet.
- **Markierte Abgänge überschreiten die 10-%-Grenze:** 51 von 487 Stationen (10,5 %) haben einen markierten
  Abgang, davon 42 mit scheiternder Bemessung (die schwerere Auslegungslast reicht auch für 2 × NAYY 4x240 nicht).
  Nach Spec Entscheidung 7 und den Global Constraints ist das ein Haltepunkt mit Rückfrage an den Owner.
- **Rest-Ursache:** 25 der 29 Stationen liegen im Gebietstyp stadt, 4 in ort. Am schlimmsten Abschnitt liegen im
  Median 106 kW an, ausgelegt sind 91 kW, die Grenze ist 97 kW; meist nur 2 Überlaststunden im Jahr. Der
  Haushaltsteil passt jetzt (53 kW gegen 54,5 kW Auslegung). Zu niedrig bleiben die E-Autos und die Wärmepumpen:
  - E-Autos: 32 kW in der Bewertung gegen etwa 11 kW Auslegung. p_ev(k) aus Smart-Meter-Daten setzt viel weniger
    Gleichzeitigkeit an als gridsims ungesteuertes Laden mit 11 kW nach der Ankunft am Abend.
  - Wärmepumpen: 48 kW gegen etwa 26 kW Auslegung. Die Regel rechnet mit der mittleren WP-Leistung der
    berechtigten Knoten, ein Seed trifft oft große Wärmepumpen in Mehrfamilienhäusern.
- Netzbau: Kabelanteil nach Trassenlänge 74,7 % (Band 74–84 %). NAYY 4x50 im Strang sinkt von 46 % auf 29 %,
  4x150 und 4x240 steigen auf 18 % und 23 %.
- Die Zusatzstationen wurden mit der neuen Regel neu bestimmt, weil die schwerere Auslegung mehr Abgänge markiert:
  266 geplant, 231 behalten, 487 statt 465 Stationen.
- Nebenbei behoben: Die Abnahmeregel im Bericht ist „5 von n Stationen“ (nicht 5 von 257); das Dashboard nimmt die
  Stationszahl aus der API (Überschrift und Kachel „Transformers overloaded“).

### Zweiter Lauf: Plausibilität des Netzbaus (`prepared-ns-fix1`)

`gridsim prepare-feeders --input …/steyr-pv-2026-10-24/input --prepared prepared --extra-stations --out
prepared-ns-fix1`, ausgeführt wie beim ersten Lauf (30 s auf hetzner). `prepared/` (ohne Zusatzstationen) wurde
nicht neu gebaut: Diese Variante hat über 50 % markierte Abgänge und ist kein Abnahmekandidat.

| Kennzahl | Fix-Runde 1 | erster Lauf | Ziel |
|---|---|---|---|
| Stationen | 487 | 465 | – |
| Kabelanteil nach Trassenlänge (Abnahmegröße) | 74,7 % | 74,3 % | 79 % (Band 74–84 %) |
| Kabelanteil nach Kabellänge | 70,0 % | 72,2 % | nur Information |
| NS-Trasse je Station | 1,98 km | 2,06 km | ca. 2,7 km |
| NS-Kabellänge je Station (Systeme einzeln) | 3,25 km | 3,10 km | ca. 2,7 km |
| Abgänge je Station (Mittel / Median) | 4,28 / 3 | 4,36 / 3 | 3,4–3,8 |
| Wohngebäude je Station (Mittel) | 37,1 | 38,8 | ca. 58 |
| Trasse je Wohngebäude | 53,3 m | 52,9 m | ca. 46 m |
| Stationen mit markiertem Abgang | **51 (10,5 %)** | 29 (6,2 %) | ≤ 10 % |
| davon zu lang / Bemessung scheitert (Stationen) | 13 / 42 | 11 / 20 | – |
| Ausläufer (Abgänge an Stationen) | 376 an 194 | 398 an 203 | – |
| Gebietstypen stadt / ort / streu | 145 / 239 / 103 | 142 / 227 / 96 | – |

Typverteilung (km, parallele Systeme einzeln; Anteil am Strang bzw. an den Hausanschlüssen):

| Typ | Fix-Runde 1 km | Anteil | erster Lauf km | Anteil |
|---|---|---|---|---|
| NAYY 4x50 | 462,9 | 29,2 % | 663,2 | 46,0 % |
| NAYY 4x150 | 279,0 | 17,6 % | 175,7 | 12,2 % |
| NAYY 4x240 | 367,2 | 23,2 % | 200,5 | 13,9 % |
| Al 4x70 | 119,3 | 7,5 % | 190,7 | 13,2 % |
| Al 4x95 | 355,3 | 22,4 % | 210,1 | 14,6 % |
| NAYY 4x35 (Hausanschluss) | 267,4 | 88,4 % | 263,9 | 87,3 % |
| Al 4x25 (Hausanschluss) | 35,1 | 11,6 % | 38,4 | 12,7 % |

Zusatzstationen: 266 geplant, 35 kleine wieder aufgelöst, 231 behalten. Der Anteil der Stationen mit markiertem
Abgang sank von 65,0 % (Ausgangsnetz mit neuer Regel) über 19,0 % (Durchgang 1) auf 10,5 % (Durchgang 2); zwei
Durchgänge sind das Maximum der Regel. Der Rest geht vor allem auf scheiternde Bemessung zurück (42 Stationen):
Einzelne Abschnitte nahe der Station tragen mit der schwereren Auslegungslast auch 2 × 4x240 nicht.

### Zweiter Lauf: Abnahmegrenze „heute“ (Fix-Runde 1)

Gleiche Einstellung wie im ersten Lauf: heute, PV 1,0, Speicher base, ungesteuert, `trafo`, ohne Netzspeicher,
2012/2017/2023, je 20 Seeds. 8 Worker, je Wetterjahr etwa 90 s; Cache `cache-fix1/`.

| Wetterjahr | Seeds | Stationen > 100 % | Stationen > 120 % | Median P90 | Max P90 |
|---|---|---|---|---|---|
| 2012 | 20 | 29 | 4 | 60,6 % | 137,0 % |
| 2017 | 20 | 9 | 5 | 55,8 % | 132,5 % |
| 2023 | 20 | 8 | 3 | 52,4 % | 130,6 % |
| alle (Maximum je Station) | 20 | **29** | **5** | 60,6 % | 137,0 % |

**Ergebnis: nicht bestanden.** Regel: höchstens 5 von 487 Stationen über 100 %, keine über 120 %. Über 120 % liegen
die Stationen 3, 60, 181, 337 und 344, alle im Gebietstyp stadt (P90 121–137 %). Der Median aller Werte je Station
sinkt nur wenig (69 % → 61 %), die Spitzen aber stark (Max 203 % → 137 %). Die Trafo-Seite bleibt fast frei:
0–2 Stationen mit Engpass.

#### Diagnose (Wetter 2012, je Station der Seed am nächsten am P90)

- Gebietstyp: stadt 25, ort 4, streu 0.
- Schlimmster Abschnitt: NAYY 4x50 23-mal, NAYY 4x150 5-mal, NAYY 4x240 1-mal. Immer Strang, einfach geführt,
  nicht im Ausläufer, nicht markiert, Richtung Bezug; hinter dem Abschnitt meist 10 oder mehr Gebäude.
- Überlaststunden am schlimmsten Abschnitt: Median **2 im Jahr** (erster Lauf: 27). Die Überlast ist knapp und
  selten, aber im P90 vorhanden. Alle überlasteten Abschnitte zusammen: 0,8 km (erster Lauf: 8,5 km).
- Zeitpunkt: meist Winterabend 18–20 Uhr (23 von 29), sonst um die Mittagszeit; November bis Februar.

Zerlegung des schlimmsten Abschnitts in seiner Spitzenstunde (Median über die 29 Stationen):

| Anteil | Bewertung (gridsim) | Auslegung (neue Regel, Näherung für den Median-Abschnitt) |
|---|---|---|
| Haushalt (69 Haushalte) | 52,9 kW | 54,5 kW (69 · 0,79 kW) |
| Wärmepumpen | 48,4 kW (4 Knoten mit WP) | ca. 26 kW (k ganze WP × mittlere Leistung) |
| E-Autos | 31,6 kW (5 Knoten mit Auto) | ca. 11 kW (k = 9, 9 · p_ev(9) = 10,7 kW) |
| Summe | **106,0 kW** | **91,2 kW** |
| Grenze (meist NAYY 4x50) | 96,8 kW | 96,8 kW |

Die Auslegung liegt nie über der Grenze, die Bewertung in 26 von 29 Fällen. Was bleibt:

1. **E-Autos:** p_ev(k) (Maier/Groiß 2026, 99-%-Quantil aus Smart-Meter-Daten) gibt bei 9 Autos 1,2 kW je Auto.
   gridsims ungesteuertes Laden lässt Autos am Abend mit 11 kW (70 %) bzw. 3,7 kW ankommen und laden. Bei 9 Autos
   laden in der Spitzenstunde oft 3 gleichzeitig, also rund 32 kW. Modell und Gleichzeitigkeitsfaktor
   widersprechen sich.
2. **Wärmepumpen:** Die Regel rechnet k × mittlere Leistung der berechtigten Knoten. Die Leistung hängt am
   Wärmebedarf des Gebäudes, und Mehrfamilienhäuser haben große Wärmepumpen. Ein Seed, der 4 Wärmepumpen auf
   große Gebäude setzt, liegt deutlich über k × Mittel.
3. Der Haushaltsteil ist mit der H0-Untergrenze getroffen.

Mögliche nächste Schritte (Entscheidung beim Controller, nicht umgesetzt):

- E-Autos: p_ev(k) durch einen Gleichzeitigkeitsfaktor ersetzen, der zu gridsims Ladeereignissen passt (aus den
  Seeds geschätzt), oder k · 11 kW · Anteil gleichzeitig ladender Autos aus gridsims Ankunftsverteilung.
- Wärmepumpen: die k größten Leistungen hinter dem Abschnitt statt k × Mittel.
- Zusätzlich zur Abnahme die 10-%-Grenze der markierten Abgänge klären (Owner). Strengere Lasten erhöhen sie
  weiter.

#### Nicht gerechnet

Vorgabe: Vergleichsmatrix 2030/2040, Stichprobe, pandapower-Vergleich und Trafo-Gegenüberstellung nur bei
bestandener Grenze. Die Zahlen dazu stehen unten beim ersten Lauf und gelten für dessen (zu schwaches) Netz.
Netzspeicher-Bemessung: unverändert (Ruling 8). Neu bewertet wird sie erst mit neuen Matrixzahlen; der Befund
des ersten Laufs (sehr große Speicher im Winter, kleine Wirkung) bleibt die einzige Grundlage.

## Erster Lauf, verworfen (Bemessung nach Spec 4.3, `MODEL_VERSION` 2026-10-26.1)

Kernzahlen: 465 Stationen, Abnahmegrenze 105 Stationen über 100 % und 63 über 120 % (nicht bestanden), markierte Abgänge 6,2 %, NAYY 4x50 46 % des Strangs. Die Regel n · 2,0 kW · g(n) plus Erwartungswerte unterschätzte die Last am Winterabend um mehr als die Hälfte (Median 56 kW Auslegung gegen 121 kW Bewertung). Alle folgenden Zahlen gelten für dieses verworfene Netz.

#### Kurzfassung des ersten Laufs

- **Die Abnahmegrenze „heute“ ist nicht bestanden.** Auf `prepared-ns` (465 Stationen) liegen im P90 über
  20 Seeds **105 Stationen über 100 %** und **63 über 120 %** (Regel: höchstens 5 von 465 über 100 %, keine
  über 120 %). Daraufhin hat der Controller die Bemessungsregel geändert (Fix-Runde 1).
- **Ursache:** Alle 105 Stationen scheitern an einem Strang-Abschnitt **NAYY 4x50** in Bezugsrichtung an einem
  Winterabend (18–19 Uhr), 71 in Gebietstyp stadt, 34 in ort, keine in streu. In der Spitzenstunde liegt der
  Abschnittsfluss im Median bei 121 kW, die Auslegung bei 56 kW, die Grenze bei 97 kW. Zwei Teile der
  Auslegungsregel unterschätzen die Last, die gridsim danach bewertet: der Haushaltsanteil
  (n · 2,0 kW · g(n) geht für große n gegen 0,14 kW je Haushalt, das H0-Profil von gridsim hat 0,79 kW Spitze je
  Haushalt) und Wärmepumpen/E-Autos als Erwartungswert, während ein Seed ganze
  Geräte an einzelne Knoten setzt (Szenario heute: rund 15 % Wärmepumpen, 8 % E-Autos je Haushalt).
- Netzbau plausibel: Kabelanteil nach Trassenlänge 74,3 % (Band 74–84 %), markierte Abgänge an 6,2 % der
  Stationen (Grenze 10 %). Abgänge je Station 4,36 (Ziel 3,4–3,8) und Trasse je Station 2,06 km (Ziel ca. 2,7 km)
  liegen daneben, weil es mit 465 statt 257 Stationen mehr, aber kleinere Netze gibt.
- 2030 ist an mehr Stationen nur die Leitung als nur der Trafo überlastet (Wetter 2012: 114 gegen 32 von 465),
  2040 meist beide (285). Leitungsbewusste Steuerung senkt die Stationen mit Leitungsüberlast 2030 um 44–61 %
  (gesteuert) bzw. 73–91 % (V2G), auf Kosten ungeladener E-Auto-Energie; Netzspeicher wirken wenig (−8 bis −10 %)
  und werden unrealistisch groß (2040, 2012: 11 GWh). Wegen der verfehlten
  Abnahmegrenze sind die Leitungszahlen zu hoch (das Netz ist heute schon zu schwach bemessen); sie zeigen die
  Richtung, nicht die Größe.
- pandapower-Vergleich: Die radiale Summation unterschätzt den Strom gegenüber dem Lastfluss im Mittel um 1,4
  Prozentpunkte (heute) bzw. 6,4 Prozentpunkte (2040), relativ im Median um 4 % bzw. 12 %; die Abweichung wächst mit
  dem Spannungsfall.
- Im Zuge der Abnahme gefunden und behoben: Scheinüberlast am Trafo durch Rundung im Grenzmodus `trafo+leitung`
  (Commit `66ca7b7`, siehe unten).

### Erster Lauf: Was gerechnet wurde

Arbeitsordner `/data/infra-kg-austria/work/gridsim-leitungen/` (Code per rsync aus dem Worktree, eigene Caches
`cache-ns/` und `cache-orig/`; der Live-Ordner `work/gridsim` wurde nicht berührt). Höchstens 8 Worker,
`OMP_NUM_THREADS=1`.

| Lauf | Daten | Einstellungen | Seeds |
|---|---|---|---|
| Abnahmegrenze | `prepared-ns` | heute, PV 1,0, Speicher base, ungesteuert, `trafo`, ohne Netzspeicher; 2012, 2017, 2023 | 20 |
| Abnahmegrenze und Trafo-Vergleich | `prepared` (257 Stationen, Netze nach Freileitungs-Korrektur) | wie oben, dazu 2030/2040 ungesteuert 2012/2023 | 20 |
| Modusvergleich | `prepared-ns` | 2012, 2023 × 2030, 2040 × ungesteuert (`trafo`, Netzspeicher aus/an) | 20 |
| Modusvergleich | `prepared-ns` | 2012, 2023 × 2030, 2040 × gesteuert, V2G × `trafo`, `trafo+leitung` × Netzspeicher aus/an | 20 |
| Stichprobe, pandapower | `prepared-ns` | 9 Stationen, heute und 2040 (2012, ungesteuert, Seed 0), 24 stärkste Stunden | 1 |

`trafo+leitung` entfällt für ungesteuertes Laden (gleiche Rechnung wie `trafo`). Befehle:

```sh
uv run python -m gridsim batch --prepared prepared-ns --cache cache-ns --years 2012 2017 2023 --scenarios heute \
  --charging uncontrolled --seeds 20 --workers 8
uv run python -m gridsim batch --prepared prepared-ns --cache cache-ns --years 2012 --scenarios 2030 2040 \
  --charging controlled v2g --limits trafo trafo+leitung --netzspeicher off on --seeds 20 --workers 4   # je Wetterjahr parallel
uv run python -m gridsim lines-report --prepared prepared-ns --cache cache-ns --report out/lines-report-ns.md
uv run python tools/pp_compare.py export --prepared prepared-ns --year 2012 --scenario heute --seed 0 \
  --stations 63 109 259 261 352 441 167 117 433 --out out/pp/heute --svg out/svg
py.sh gridsim-ppcompare/pp_compare.py compare --in gridsim-ppcompare/heute --out gridsim-ppcompare/heute.json
```

Die Matrix lief zuerst mit 10 Seeds und wurde dann auf 20 aufgefüllt (die ersten 10 aus dem Cache); alle
Einstellungen in diesem Bericht haben 20 Seeds.

#### Laufzeiten

Ein Seed, ein Prozess, Wetter 2023, 465 Stationen (hetzner, geteilt mit anderen Projekten, Last 20–40):

| Einstellung | Plan Netzspeicher | Seed |
|---|---|---|
| heute, ungesteuert | – | 9,8 s |
| 2040, ungesteuert | – | 14,6 s |
| 2040, gesteuert, `trafo` | – | 21,7 s |
| 2040, gesteuert, `trafo+leitung` | – | 64,0 s |
| 2040, V2G, `trafo` | – | 22,1 s |
| 2040, V2G, `trafo+leitung` | – | 113,3 s |
| 2040, ungesteuert, Netzspeicher an | 56,6 s | 100,9 s |
| 2040, gesteuert, `trafo+leitung`, Netzspeicher an | 139,5 s | 73,1 s |

Batch mit 8 Workern: 20 Seeds heute in 105–111 s je Wetterjahr (465 Stationen) bzw. 95–113 s (257 Stationen);
2030/2040 ungesteuert mit 4 Workern 222–254 s. Mehr Worker bringen wenig, weil die Speicherbandbreite sättigt
(ein Seed braucht mit 8 Workern 40–60 s statt 10–15 s). Weitere Wandzeiten der Matrix im Abschnitt
„Vergleich der Modi“.

### Erster Lauf: Plausibilität des Netzbaus (`prepared-ns`)

| Kennzahl | Wert | Ziel | im Ziel |
|---|---|---|---|
| Kabelanteil nach Trassenlänge (Abnahmegröße) | 74,3 % | 79 % (Band 74–84 %) | ja |
| Kabelanteil nach Kabellänge | 72,2 % | nur Information | – |
| NS-Trasse je Station | 2,06 km | ca. 2,7 km | – |
| NS-Kabellänge je Station (Systeme einzeln) | 3,10 km | ca. 2,7 km | – |
| Abgänge je Station (Mittel / Median) | 4,36 / 3 | 3,4–3,8 | nein |
| Wohngebäude je Station (Mittel) | 38,8 | ca. 58 | – |
| Trasse je Wohngebäude | 52,9 m | ca. 46 m | – |

Referenzwerte: Netz OÖ / V-NEP 2026 (79 % Kabel, ca. 2,7 km NS-Leitung und ca. 58 Kundenanlagen je Station),
Bletterie et al. 2016 und Kadam 2018 (3,4 bzw. 3,75 Abgänge je Station), siehe
`docs/research/2026-10-25-ns-leitungen-steyr.md`. Die Werte je Station sind nur Orientierung (Controller): Mit
465 Stationen werden die Netze kleiner (weniger Gebäude und Trasse je Station); je Gebäude liegt die Trasse mit
52,9 m nahe am Netz-OÖ-Mittel von 46 m, das ländlicher geprägt ist als die Region Steyr. Mehr Abgänge als das
Ziel kommen aus der Regel „höchstens 30 Gebäude je Abgang“ und den eigenen Abgängen für Anlagen über 30 kWp.

Typverteilung (km, parallele Systeme einzeln; Anteil am Strang bzw. an den Hausanschlüssen):

| Typ | km | Anteil |
|---|---|---|
| NAYY 4x50 | 663,2 | 46,0 % |
| Al 4x95 | 210,1 | 14,6 % |
| NAYY 4x240 | 200,5 | 13,9 % |
| Al 4x70 | 190,7 | 13,2 % |
| NAYY 4x150 | 175,7 | 12,2 % |
| NAYY 4x35 (Hausanschluss) | 263,9 | 87,3 % |
| Al 4x25 (Hausanschluss) | 38,4 | 12,7 % |

Für die Typverteilung gibt es keinen Referenzwert in der Recherche; auffällig ist der hohe Anteil des kleinsten
Kabels (46 %), der zur verfehlten Abnahmegrenze passt.

Markierte Abgänge („bräuchte eigene Station“, Entscheidung 7): 59 Abgänge an **29 von 465 Stationen (6,2 %)**,
Grenze 10 % eingehalten; davon 29 zu lang (ab 6 Wohngebäuden jenseits der Grenze), 32 mit scheiternder Bemessung
(auch 2 × 4x240 reicht nicht). Ausläufer (nicht markiert, Controller-Regel): 398 Abgänge an 203 Stationen,
Reichweite Median 789 m, P90 1 495 m. Gebietstypen: stadt 142, ort 227, streu 96 Stationen.

Zusatzstationen (Owner-Entscheidung 1): 245 geplant, 36 kleine wieder aufgelöst, 209 behalten (465 statt 257);
der Anteil der Stationen mit markiertem Abgang sank von 57,6 % über 13,5 % (Durchgang 1) auf 6,2 % (Durchgang 2).

### Erster Lauf: Abnahmegrenze „heute“ (Entscheidung 6)

Szenario heute, PV 1,0, Speicher base, ungesteuert, Grenzmodus `trafo`, ohne Netzspeicher; je Station und
Wetterjahr das P90 über 20 Seeds der höchsten Abschnittsauslastung (beide Richtungen, mit Spitzenzuschlag),
zusammengefasst als Maximum über die drei Jahre.

| Wetterjahr | Seeds | Stationen > 100 % | Stationen > 120 % | Median P90 | Max P90 |
|---|---|---|---|---|---|
| 2012 | 20 | 105 | 61 | 68,8 % | 202,8 % |
| 2017 | 20 | 81 | 46 | 63,4 % | 188,2 % |
| 2023 | 20 | 72 | 33 | 59,7 % | 179,6 % |
| alle (Maximum je Station) | 20 | **105** | **63** | 69,0 % | 202,8 % |

**Ergebnis: nicht bestanden** (Regel: ≤ 5 von 465 über 100 %, keine über 120 %).
Zum Vergleich die Variante ohne Zusatzstationen (`prepared`, 257 Stationen): 73 über 100 %, 41 über 120 % —
ebenfalls nicht bestanden. Die Trafo-Seite ist dagegen heute fast frei (Median 0–2 Stationen mit Engpass).

#### Diagnose

Für jede der 105 Stationen (Wetter 2012) der Seed mit dem Wert am nächsten am P90 und darin der Abschnitt mit
der höchsten Auslastung (`gridsim/feeders/report.py::segment_table`):

- Gebietstyp: stadt 71, ort 34, streu 0 (stadt: 71 von 142 Stationen = 50 %; ort 34 von 227; streu 0 von 96).
- Abschnitt: immer **NAYY 4x50**, immer Strang (nie Hausanschluss), einfach geführt, 102 von 105 nicht im
  Ausläufer, keiner in einem markierten Abgang; Richtung immer Bezug; hinter dem Abschnitt 8–30 Gebäude (Median 23), Länge 6–123 m (Median 22 m).
- Alle überlasteten Abschnitte dieser Stationen: NAYY 4x50 347, NAYY 4x150 7, NAYY 4x240 1; zusammen 8,5 km.
- Zeitpunkt: 18–19 Uhr (89 von 105), fast immer Dezember bis Februar; im Median 27 Überlaststunden je Jahr am schlimmsten
  Abschnitt.

Zerlegung des schlimmsten Abschnitts in seiner Spitzenstunde (Median über die 105 Stationen):

| Anteil | Bewertung (gridsim) | Auslegung (Regel) |
|---|---|---|
| Haushalt (66 Haushalte) | 43,7 kW | ca. 14,5 kW (66 · 2,0 kW · g(66), g = 0,11) |
| Wärmepumpen | 47,8 kW (5 Knoten mit WP) | zusammen ca. 41 kW (Erwartungswert, 15 % je Knoten, kälteste Stunde 2012) |
| E-Autos | 30,8 kW (5 Knoten mit Auto) | (8 % je Haushalt, n · p_ev(n)) |
| Summe | **121,2 kW** | **55,7 kW** |
| Grenze NAYY 4x50 (144 A, cos φ 0,97) | 96,8 kW | 96,8 kW |

Die Auslegung liegt in keinem Fall über der Grenze (Regel richtig umgesetzt), die Bewertung in 103 von 105 Fällen
darüber. Die Regel selbst passt nicht zur Bewertung:

1. **Haushalt:** n · P_HH · g(n) mit P_HH = 2,0 kW und g∞ = 0,07 ergibt für große Kollektive 0,14 kW je Haushalt.
   Das H0-Profil in gridsim hat eine Spitze von 0,79 kW je Haushalt (3 000 kWh). Der Spitzenzuschlag nach
   Entscheidung 8 greift nur, wenn g(n) · 2,0 kW über 0,79 kW liegt, also nur bis n ≈ 2. Die Aussage „Bemessung und
   Bewertung verwenden dieselbe Spitze“ gilt damit nur für sehr kleine Abschnitte.
2. **Wärmepumpen und E-Autos:** Der Erwartungswert verteilt rund 0,15 WP und 0,08 Autos je Haushalt gleichmäßig; ein
   Seed setzt ganze Geräte (ca. 10 kW WP-Leistung an einem kalten Abend, 11 kW Laden) an einzelne Knoten. Für
   einen Abschnitt mit 20 Knoten erwartet die Regel 3 Wärmepumpen, ein Seed hat oft 5 und mehr.
3. **Keine Reserve:** Der kleinste passende Typ wird bis 100 % Grenzstrom gewählt; 4x50 ist schon bei 79,7 kW
   Auslegung (82 %) genommen (Station 63).

Mögliche Regeländerungen (Entscheidung beim Controller, nicht umgesetzt): Haushaltslast je Abschnitt mindestens
n · H0-Spitze (oder P_HH so wählen, dass g∞ · P_HH zur H0-Spitze passt); Wärmepumpen und E-Autos mit einem
Quantil der Binomialverteilung je Abschnitt statt mit dem Erwartungswert; oder ein Mindestquerschnitt im Strang
(etwa NAYY 4x150; dafür fehlt noch eine Quelle). Mit dem Median oben bräuchte es beide
der ersten zwei Änderungen: H0-Spitze allein hebt die Auslegung auf ca. 93 kW, immer noch unter 121 kW.

### Erster Lauf: Trafo-Kennzahlen: `prepared` gegen `prepared-ns`

Ungesteuert, PV 1,0, Speicher base, Grenzmodus `trafo`, 20 Seeds, Median (Band 10–90 % siehe
`out/trafo-cmp.json` auf hetzner). Die Zusatzstationen haben eigene Trafos nach `trafo_kva`; die Stationsliste
der bisherigen Variante bleibt unverändert erhalten (Entscheidung 1).

| Wetter | Szenario | Stationen | Trafo-Engpass Bezug | E_netto MWh | Speicher-Einheiten | Trafo +1 | Trafo +2 und mehr | über 1000 kVA | Engpass Einspeisung |
|---|---|---|---|---|---|---|---|---|---|
| 2012 | heute | 257 / 465 | 3,5 / 2 | 0,22 / 0,06 | 68 / 17 | 1 / 2 | 0 / 0 | 2 / 0 | 1 / 2 |
| 2017 | heute | 257 / 465 | 1,5 / 1 | 0,10 / 0,00 | 33 / 1 | 0 / 1 | 0 / 0 | 1 / 0 | 2 / 2 |
| 2023 | heute | 257 / 465 | 1 / 0 | 0,07 / 0,00 | 22 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 3 / 4 |
| 2012 | 2030 | 257 / 465 | 100 / 124 | 64,5 / 33,5 | 19 815 / 10 329 | 66,5 / 105 | 10,5 / 16 | 23 / 5 | 1 / 2 |
| 2023 | 2030 | 257 / 465 | 44 / 48,5 | 8,9 / 3,0 | 2 765 / 939 | 27 / 45 | 2 / 3 | 15 / 1 | 3 / 4 |
| 2012 | 2040 | 257 / 465 | 208 / 334 | 3 737 / 2 247 | 1 145 013 / 688 615 | 37 / 102 | 107 / 198 | 64 / 36 | 1 / 1 |
| 2023 | 2040 | 257 / 465 | 193 / 296,5 | 354 / 196 | 108 609 / 60 312 | 74 / 157,5 | 70 / 118 | 49 / 21 | 2 / 3 |

Lesart: Mehr, aber kleinere Trafos. Die Zahl der Stationen mit Trafo-Engpass steigt mit der Stationszahl (2040
absolut von 193–208 auf 297–334 gestiegen, als Anteil von 75–81 % auf 64–72 % gesunken); die Energie über der Grenze und die
Stationen über 1000 kVA sinken deutlich, weil große Stationen entlastet wurden. Für Aussagen „Anteil der Trafos
mit Engpass“ ist die Stationszahl mitzunennen.

### Erster Lauf: Vergleich der Modi 2030 und 2040

`prepared-ns`, PV 1,0, Speicher base, 20 Seeds je Einstellung, Median über die Seeds. Spalten: Trafo-Engpass =
Stationen mit Trafo über `kva` (Bezug); Leitung Bezug / Einsp. = Stationen mit mindestens einem Abschnitt über
100 %; nur Leitung = Stationen, an denen in einer Richtung nur die Leitung überlastet ist; Überlast km = Länge der
überlasteten Abschnitte; ungeladen = E-Auto-Energie, die bis 7 Uhr nicht geladen werden konnte; NS = Netzspeicher
(Anzahl, Summe der Kapazität); letzte Spalte = „Engpass zuerst“ in Bezugsrichtung je Station als häufigste
Klasse über die Seeds (Stationen, Summe 465).

#### Kernaussagen

| Wetter | Szenario | Stationen Trafo / Leitung / beide / keiner (ungesteuert) | Leitung Bezug: gesteuert `trafo` → `trafo+leitung` | dabei ungeladen MWh | Leitung Bezug: V2G `trafo` → `trafo+leitung` | dabei ungeladen MWh | Netzspeicher (ungesteuert): Leitung Bezug aus → an, Anzahl, MWh |
|---|---|---|---|---|---|---|---|
| 2012 | 2030 | 32 / 114 / 91 / 228 | 188 → 105 | 8 → 98 | 188 → 51 | 23 → 257 | 200 → 182, 369, 935 |
| 2023 | 2030 | 18 / 139 / 18 / 290 | 154 → 60 | 0 → 10 | 154 → 14 | 0 → 36 | 157 → 141, 275, 114 |
| 2012 | 2040 | 52 / 19 / 285 / 109 | 275 → 228 | 1 037 → 2 181 | 273 → 184 | 2 090 → 4 392 | 303 → 286, 698, 11 012 |
| 2023 | 2040 | 45 / 23 / 253 / 144 | 252 → 171 | 52 → 729 | 250 → 70 | 112 → 1 333 | 278 → 258, 612, 1 399 |

- **Trafo oder Leitung (ungesteuert):** 2030 ist an mehr Stationen nur die Leitung überlastet als nur der Trafo
  (2012: 114 gegen 32, 2023: 139 gegen 18); 2040 sind an den meisten Stationen beide überlastet (253–285 von 465).
  Weil schon „heute“ 42–58 Stationen „Leitung zuerst“ zeigen (Abnahmegrenze verfehlt), ist der Leitungsanteil
  überzeichnet.
- **Leitungsbewusste Steuerung** (`trafo+leitung`) senkt die Zahl der Stationen mit Leitungsüberlast deutlich
  (gesteuertes Laden 2030: um 44–61 %, 2040: um 17–32 %; V2G stärker, weil die Rückspeisung Abschnitte entlastet).
  Der Preis ist ungeladene E-Auto-Energie: Was der Abschnitt nicht trägt, wird nicht geladen (2040, 2012: 2,2 GWh
  statt 1,0 GWh). Die verbleibende Leitungsüberlast kommt aus dem Grundfluss (Haushalt, Wärmepumpe), den die
  Steuerung nicht verschiebt. Die Trafo-Kennzahlen sind in beiden Modi gleich (34/34, 230/230, 132/132 Stationen) —
  nach dem Fix unten.
- **V2G gegen Trafo:** Im Modus `trafo` senkt V2G die Stationen mit Trafo-Engpass stark (2040, 2023: 132 → 18
  gegenüber gesteuertem Laden), ändert an den Leitungen aber fast nichts; erst `trafo+leitung` bringt die
  Rückspeisung an die Abschnitte, die sie brauchen.
- **Netzspeicher** wirken wenig und werden sehr groß: ungesteuert 2030 (2012) 8–10 % weniger Stationen mit
  Leitungsüberlast bei 369 Speichern mit zusammen 935 MWh; 2040 (2012) 698 Speicher mit 11 GWh. Die Bemessung nach
  § 7.2 fasst die langen Winterabend-Ereignisse einer Kältewelle zusammen und ergibt Energien, die kein
  Netzbetreiber an einen NS-Abgang stellen würde. Mit gesteuertem Laden im Leitungsmodus erhöhen sie die
  ungeladene Energie (2012/2030: 98 → 158 MWh), weil ihr Nachladen in der Nacht Leitungsraum belegt (Ruling: der
  Netzspeicher sieht dort nur den Grundfluss). Als Mittel gegen die Leitungsengpässe dieses Netzes taugen sie
  nach diesen Zahlen nicht; gegen kurze Spitzen (2023) ist die Größe kleiner (114 MWh in 2030), die Wirkung aber
  ebenso gering.
- **Einspeisung:** Bei PV 1,0 gibt es praktisch keine Leitungsüberlast in Einspeiserichtung (0–5 Stationen).

#### Reihenfolge heute → 2030 → 2040

Je Station das erste Szenario mit Engpass (ungesteuert, Grenzmodus `trafo`, beide Richtungen, häufigste Klasse
über die Seeds) und welches Element dort überlastet ist (Entscheidung 9):

| Wetter | zuerst Trafo | zuerst Leitung | beide zugleich | nie bis 2040 | davon schon heute (T / L / b) |
|---|---|---|---|---|---|
| 2012 | 80 | 139 | 139 | 107 | 2/58/0 |
| 2023 | 62 | 147 | 115 | 141 | 4/42/0 |

„beide zugleich“ heißt: Im ersten Szenario mit Engpass sind Trafo und Leitung überlastet. Ohne die verfehlte
Abnahmegrenze würden die 42–58 Stationen mit „Leitung schon heute“ später kippen; die Reihenfolge ist daher nur
als Tendenz zu lesen: Leitungen kippen bei diesem Netz meist vor oder mit dem Trafo.

#### Alle Einstellungen

| Wetter | Szenario | Laden | Grenzen | Netzspeicher | Seeds | Trafo-Engpass | Leitung Bezug | Leitung Einsp. | nur Leitung | Überlast km | ungeladen MWh | NS Anzahl | NS kWh | Bezug: Trafo / Leitung / beide / keiner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2012 | heute | uncontrolled | trafo | aus | 20 | 2 | 62 | 0 | 62 | 5,2 | 0,0 | – | – | 0 / 58 / 0 / 407 |
| 2012 | 2030 | uncontrolled | trafo | aus | 20 | 124 | 200 | 0 | 114 | 34,6 | 0,0 | – | – | 32 / 114 / 91 / 228 |
| 2012 | 2030 | uncontrolled | trafo | an | 20 | 108 | 182 | 0 | 118 | 28,2 | 0,0 | 369 | 934923 | 36 / 124 / 62 / 243 |
| 2012 | 2030 | controlled | trafo | aus | 20 | 34 | 188 | 0 | 170 | 31,6 | 8,3 | – | – | 14 / 173 / 15 / 263 |
| 2012 | 2030 | controlled | trafo | an | 20 | 32 | 188 | 0 | 172 | 31,5 | 7,8 | 346 | 934730 | 14 / 180 / 7 / 264 |
| 2012 | 2030 | controlled | trafo+leitung | aus | 20 | 34 | 105 | 0 | 88 | 9,4 | 98,1 | – | – | 15 / 85 / 10 / 355 |
| 2012 | 2030 | controlled | trafo+leitung | an | 20 | 32 | 92 | 0 | 77 | 7,7 | 158,0 | 152 | 671396 | 15 / 76 / 7 / 367 |
| 2012 | 2030 | v2g | trafo | aus | 20 | 9 | 188 | 0 | 182 | 31,6 | 22,6 | – | – | 1 / 189 / 0 / 275 |
| 2012 | 2030 | v2g | trafo | an | 20 | 9 | 188 | 0 | 182 | 31,4 | 21,2 | 346 | 932299 | 1 / 189 / 0 / 275 |
| 2012 | 2030 | v2g | trafo+leitung | aus | 20 | 10 | 51 | 0 | 46 | 4,7 | 257,1 | – | – | 1 / 42 / 1 / 421 |
| 2012 | 2030 | v2g | trafo+leitung | an | 20 | 10 | 48 | 0 | 43 | 4,4 | 278,3 | 59 | 321159 | 1 / 40 / 1 / 423 |
| 2012 | 2040 | uncontrolled | trafo | aus | 20 | 334 | 303 | 0 | 23 | 121,8 | 0,0 | – | – | 52 / 19 / 285 / 109 |
| 2012 | 2040 | uncontrolled | trafo | an | 20 | 318 | 286 | 0 | 32 | 107,3 | 0,0 | 698 | 11011942 | 60 / 25 / 264 / 116 |
| 2012 | 2040 | controlled | trafo | aus | 20 | 230 | 275 | 0 | 88 | 75,7 | 1037,2 | – | – | 42 / 83 / 196 / 144 |
| 2012 | 2040 | controlled | trafo | an | 20 | 201 | 270 | 0 | 118 | 77,1 | 793,4 | 587 | 9984805 | 48 / 115 / 158 / 144 |
| 2012 | 2040 | controlled | trafo+leitung | aus | 20 | 230 | 228 | 0 | 52 | 44,0 | 2180,9 | – | – | 55 / 50 / 183 / 177 |
| 2012 | 2040 | controlled | trafo+leitung | an | 20 | 206 | 202 | 0 | 61 | 36,0 | 3204,2 | 442 | 7795200 | 66 / 58 / 146 / 195 |
| 2012 | 2040 | v2g | trafo | aus | 20 | 130 | 273 | 0 | 164 | 74,7 | 2090,1 | – | – | 15 / 157 / 117 / 176 |
| 2012 | 2040 | v2g | trafo | an | 20 | 104 | 270 | 5 | 192 | 76,4 | 1547,5 | 584 | 8857952 | 19 / 182 / 89 / 175 |
| 2012 | 2040 | v2g | trafo+leitung | aus | 20 | 144 | 184 | 0 | 65 | 35,3 | 4392,2 | – | – | 18 / 59 / 130 / 258 |
| 2012 | 2040 | v2g | trafo+leitung | an | 20 | 136 | 173 | 0 | 66 | 32,3 | 4681,3 | 340 | 3068256 | 25 / 59 / 116 / 265 |
| 2017 | heute | uncontrolled | trafo | aus | 20 | 1 | 54 | 0 | 54 | 4,4 | 0,0 | – | – | 0 / 53 / 0 / 412 |
| 2023 | heute | uncontrolled | trafo | aus | 20 | 0 | 44 | 0 | 44 | 3,7 | 0,0 | – | – | 0 / 42 / 0 / 423 |
| 2023 | 2030 | uncontrolled | trafo | aus | 20 | 48 | 157 | 0 | 131 | 22,1 | 0,0 | – | – | 18 / 139 / 18 / 290 |
| 2023 | 2030 | uncontrolled | trafo | an | 20 | 44 | 141 | 0 | 122 | 17,6 | 0,0 | 275 | 113754 | 19 / 129 / 12 / 305 |
| 2023 | 2030 | controlled | trafo | aus | 20 | 6 | 154 | 0 | 151 | 21,4 | 0,0 | – | – | 0 / 155 / 0 / 310 |
| 2023 | 2030 | controlled | trafo | an | 20 | 6 | 154 | 0 | 152 | 21,2 | 0,0 | 269 | 112347 | 0 / 155 / 0 / 310 |
| 2023 | 2030 | controlled | trafo+leitung | aus | 20 | 6 | 60 | 0 | 58 | 3,9 | 10,2 | – | – | 0 / 54 / 0 / 411 |
| 2023 | 2030 | controlled | trafo+leitung | an | 20 | 6 | 52 | 0 | 51 | 3,1 | 23,5 | 74 | 48275 | 0 / 43 / 0 / 422 |
| 2023 | 2030 | v2g | trafo | aus | 20 | 0 | 154 | 0 | 154 | 21,4 | 0,3 | – | – | 0 / 155 / 0 / 310 |
| 2023 | 2030 | v2g | trafo | an | 20 | 0 | 154 | 0 | 154 | 21,2 | 0,3 | 269 | 112339 | 0 / 155 / 0 / 310 |
| 2023 | 2030 | v2g | trafo+leitung | aus | 20 | 1 | 14 | 0 | 14 | 0,9 | 35,5 | – | – | 0 / 10 / 0 / 455 |
| 2023 | 2030 | v2g | trafo+leitung | an | 20 | 1 | 14 | 0 | 14 | 0,9 | 40,5 | 15 | 16263 | 0 / 10 / 0 / 455 |
| 2023 | 2040 | uncontrolled | trafo | aus | 20 | 296 | 278 | 0 | 30 | 88,6 | 0,0 | – | – | 45 / 23 / 253 / 144 |
| 2023 | 2040 | uncontrolled | trafo | an | 20 | 262 | 258 | 0 | 56 | 75,0 | 0,0 | 612 | 1399303 | 57 / 54 / 206 / 148 |
| 2023 | 2040 | controlled | trafo | aus | 20 | 132 | 252 | 0 | 147 | 65,3 | 52,0 | – | – | 26 / 140 / 114 / 185 |
| 2023 | 2040 | controlled | trafo | an | 20 | 102 | 251 | 0 | 178 | 66,0 | 47,1 | 547 | 1312416 | 28 / 175 / 77 / 185 |
| 2023 | 2040 | controlled | trafo+leitung | aus | 20 | 132 | 171 | 0 | 81 | 21,5 | 729,1 | – | – | 41 / 78 / 99 / 247 |
| 2023 | 2040 | controlled | trafo+leitung | an | 20 | 109 | 147 | 0 | 88 | 17,0 | 1128,6 | 302 | 719771 | 49 / 90 / 65 / 261 |
| 2023 | 2040 | v2g | trafo | aus | 20 | 18 | 250 | 0 | 238 | 64,6 | 111,6 | – | – | 5 / 239 / 12 / 209 |
| 2023 | 2040 | v2g | trafo | an | 20 | 16 | 250 | 0 | 240 | 65,6 | 91,7 | 541 | 1264616 | 6 / 241 / 8 / 210 |
| 2023 | 2040 | v2g | trafo+leitung | aus | 20 | 22 | 70 | 0 | 57 | 8,1 | 1333,2 | – | – | 5 / 54 / 15 / 391 |
| 2023 | 2040 | v2g | trafo+leitung | an | 20 | 20 | 66 | 0 | 54 | 7,0 | 1414,4 | 94 | 220465 | 7 / 54 / 10 / 394 |

Wandzeiten der Matrix (je Wetterjahr parallel, 4 Worker): 20 Seeds ungesteuert 222–254 s, mit Netzspeicher
130–183 s (für die zweiten 10 Seeds; Plan einmal 57–140 s); gesteuert/V2G `trafo` 100–175 s je 10 Seeds,
`trafo+leitung` 186–485 s je 10 Seeds. Gesamte Matrix etwa 2,5 Stunden.

### Erster Lauf: Stichprobe: drei Stationen je Gebietstyp

Auswahl je Gebietstyp nach dem P90 der Abnahmegrenze: höchster Wert, Median, unteres Viertel. Abschnittstabelle
aus `tools/pp_compare.py export` (heute, 2012, Seed 0), Kartenskizzen in `docs/abnahme-screens/stichprobe-*.svg`
(Abschnitte nach höchster Auslastung des Seeds: grün < 80 %, orange 80–100 %, rot > 100 %; gestrichelt =
Freileitung; schwarzes Quadrat = Station).

| Station | Gebiet | Gebäude | Abgänge | Abschnitte | Ausläufer | P90 Abnahme | km je Typ (Systeme) |
|---|---|---|---|---|---|---|---|
| 63 | stadt | 40 | 4 | 82 | 1 | 202,8 % | NAYY 4x50 1,96, NAYY 4x35 0,53, NAYY 4x150 0,27 |
| 109 | stadt | 94 | 7 | 177 | 2 | 100,2 % | NAYY 4x50 3,39, NAYY 4x35 1,73, NAYY 4x150 0,62 |
| 259 | stadt | 35 | 3 | 62 | 0 | 77,1 % | NAYY 4x50 0,79, NAYY 4x35 0,46 |
| 261 | ort | 47 | 3 | 94 | 0 | 185,0 % | NAYY 4x50 1,38, NAYY 4x35 0,69, NAYY 4x240 0,37, NAYY 4x150 0,08 |
| 352 | ort | 22 | 3 | 41 | 0 | 68,4 % | NAYY 4x50 0,62, NAYY 4x35 0,35, Al 4x70 0,15, Al 4x25 0,11 |
| 441 | ort | 8 | 3 | 15 | 0 | 48,0 % | NAYY 4x50 0,25, NAYY 4x35 0,16 |
| 167 | streu | 41 | 4 | 98 | 1 | 79,9 % | Al 4x95 2,50, NAYY 4x50 1,23, Al 4x70 1,15, NAYY 4x240 1,05, Al 4x25 0,34, NAYY 4x35 0,31, NAYY 4x150 0,17 |
| 117 | streu | 20 | 3 | 44 | 0 | 39,3 % | Al 4x70 2,37, Al 4x95 0,54, NAYY 4x150 0,43, NAYY 4x50 0,31, Al 4x25 0,26, NAYY 4x35 0,02 |
| 433 | streu | 9 | 3 | 20 | 1 | 30,1 % | Al 4x95 1,09, NAYY 4x50 0,89, NAYY 4x150 0,21, NAYY 4x35 0,13, Al 4x25 0,03, Al 4x70 0,03 |

Je Station die drei am stärksten ausgelasteten Abschnitte (Auslegung = Auslegungsbezug nach Regel, Grenze =
Grenzstrom bei cos φ 0,97; HA = Hausanschluss):

| Station | Abschnitt | Typ | Länge m | Knoten dahinter | Auslegung kW | Grenze kW | höchste Auslastung | Stunden > 100 % |
|---|---|---|---|---|---|---|---|---|
| 63 | 3 | NAYY 4x50 | 15,9 | 18 | 79,7 | 96,8 | 133,6 % | 70 |
| 63 | 13 | NAYY 4x50 | 37,2 | 11 | 54,6 | 96,8 | 75,7 % | 0 |
| 63 | 18 | NAYY 4x50 | 23,3 | 10 | 51,4 | 96,8 | 71,7 % | 0 |
| 109 | 3 | NAYY 4x50 | 17,0 | 25 | 45,5 | 96,8 | 91,1 % | 0 |
| 109 | 8 | NAYY 4x50 | 2,7 | 24 | 43,9 | 96,8 | 88,3 % | 0 |
| 109 | 9 | NAYY 4x50 | 8,1 | 29 | 48,8 | 96,8 | 82,1 % | 0 |
| 259 | 2 | NAYY 4x50 | 57,4 | 12 | 32,7 | 96,8 | 72,5 % | 0 |
| 259 | 1 | NAYY 4x50 | 16,1 | 22 | 51,8 | 96,8 | 66,9 % | 0 |
| 259 | 5 | NAYY 4x50 | 23,6 | 11 | 31,4 | 96,8 | 62,1 % | 0 |
| 261 | 16 | NAYY 4x50 | 34,2 | 13 | 75,1 | 96,8 | 151,7 % | 156 |
| 261 | 23 | NAYY 4x50 | 30,1 | 7 | 47,9 | 96,8 | 119,6 % | 61 |
| 261 | 3 | NAYY 4x50 | 1,0 | 17 | 70,9 | 96,8 | 100,4 % | 1 |
| 352 | 2 | NAYY 4x50 | 24,2 | 14 | 35,5 | 96,8 | 54,1 % | 0 |
| 352 | 5 | NAYY 4x50 | 24,2 | 13 | 34,2 | 96,8 | 53,4 % | 0 |
| 352 | 8 | NAYY 4x50 | 49,2 | 6 | 26,0 | 96,8 | 37,6 % | 0 |
| 441 | 7 | NAYY 4x35 (HA) | 21,7 | 1 | 9,5 | 82,7 | 51,5 % | 0 |
| 441 | 1 | NAYY 4x50 | 45,5 | 3 | 13,7 | 96,8 | 47,2 % | 0 |
| 441 | 3 | NAYY 4x50 | 29,3 | 2 | 11,5 | 96,8 | 47,1 % | 0 |
| 167 | 6 | NAYY 4x50 | 18,7 | 17 | 42,3 | 96,8 | 62,2 % | 0 |
| 167 | 23 | NAYY 4x50 | 13,7 | 7 | 29,4 | 96,8 | 42,4 % | 0 |
| 167 | 28 | NAYY 4x50 | 42,2 | 6 | 28,0 | 96,8 | 41,8 % | 0 |
| 117 | 0 | Al 4x70 | 45,9 | 17 | 41,0 | 171,4 | 25,8 % | 0 |
| 117 | 24 | NAYY 4x150 | 429,6 | 1 | 0,0 | 184,8 | 23,9 % | 0 |
| 117 | 25 | Al 4x25 (HA) | 35,2 | 1 | 10,6 | 90,7 | 22,2 % | 0 |
| 433 | 2 | NAYY 4x50 | 41,8 | 3 | 19,7 | 96,8 | 20,2 % | 0 |
| 433 | 15 | NAYY 4x35 (HA) | 17,6 | 1 | 9,8 | 82,7 | 18,0 % | 0 |
| 433 | 4 | NAYY 4x50 | 410,3 | 2 | 12,0 | 96,8 | 16,2 % | 0 |

Von Hand geprüft:

- Topologie und Typen passen zum Gebietstyp: stadt nur Kabel; ort überwiegend Kabel mit einzelnen
  Freileitungsabgängen (352); streu mit hohem Freileitungsanteil und langen Strängen (117, 167, 433).
- Querschnitte steigen zur Station hin (261: 4x240 am Abgangsanfang mit 27 Knoten, 4x150 dahinter, 4x50 am Ende);
  das Bemessungsverfahren arbeitet wie beschrieben.
- Station 117, Abschnitt 24: 430 m NAYY 4x150 zu einem einzelnen Knoten ohne Bezugslast — ein eigener Abgang für
  eine PV-Anlage über 30 kWp, nach Einspeisung und 3 % Spannungsanhebung bemessen. Plausibel.
- Station 433, Abschnitte 4 und 6: 410 m und 228 m NAYY 4x50 zu ein bis zwei Gebäuden — lange Stichleitungen in
  Streusiedlung, wie in der Recherche (0,5–1 km bei Weilern und Einzelgehöften), thermisch unkritisch.
- Die überlasteten Abschnitte (63, 261) sind kurze 4x50-Abschnitte nahe der Abzweigung mit 13–18 Gebäuden
  dahinter, deren Auslegung schon bei 78–82 % der Grenze lag; genau das Muster der Diagnose.

### Erster Lauf: pandapower-Vergleich

`tools/pp_compare.py` exportiert je Station Netz und Knotenflüsse (ohne Spitzenzuschlag, der am Abschnitt und
nicht am Knoten hängt) der 24 Stunden mit der höchsten Abschnittsauslastung und rechnet im pandapower-Container
(`steyr-gutachten-2026-10-25/py.sh`, pandapower 3.2.1, eigener Unterordner `gridsim-ppcompare/`) je Stunde einen
Lastfluss: Sammelschiene ideal 1,0 pu, Trafo nicht modelliert, Lasten mit cos φ 0,97 bei Bezug und 1,0 bei
Einspeisung, R/X der Abschnitte wie in gridsim. Verglichen wird der Strom je Abschnitt als Anteil am Grenzstrom,
nur Abschnittsstunden ab 10 % Auslastung. Alle Lastflüsse konvergierten.

| Station | heute: gridsim max | pandapower max | Abw. Mittel (Pp) | Abw. P95 (Pp) | Abw. relativ Median | U min (pu) | 2040: gridsim max | pandapower max | Abw. Mittel (Pp) | Abw. P95 (Pp) | Abw. relativ Median | U min (pu) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 63 | 133,6 % | 142,5 % | 1,8 | 4,7 | 4,6 % | 0,92 | 361,6 % | 431,4 % | 9,0 | 36,5 | 12,1 % | 0,76 |
| 109 | 91,1 % | 96,8 % | 1,2 | 3,5 | 4,2 % | 0,93 | 203,4 % | 246,9 % | 5,9 | 19,5 | 12,4 % | 0,80 |
| 259 | 72,5 % | 75,1 % | 1,1 | 2,2 | 3,8 % | 0,95 | 175,1 % | 190,1 % | 3,6 | 8,4 | 7,4 % | 0,88 |
| 261 | 151,7 % | 164,6 % | 2,8 | 7,6 | 6,5 % | 0,92 | 406,0 % | 545,6 % | 12,4 | 43,6 | 17,2 % | 0,69 |
| 352 | 54,1 % | 55,2 % | 0,5 | 1,1 | 2,1 % | 0,96 | 120,4 % | 125,8 % | 1,3 | 4,6 | 3,8 % | 0,89 |
| 441 | 50,9 % | 51,9 % | 0,5 | 0,9 | 1,4 % | 0,98 | 60,0 % | 61,6 % | 0,6 | 1,0 | 1,7 % | 0,97 |
| 167 | 62,2 % | 64,8 % | 1,0 | 2,0 | 4,8 % | 0,93 | 171,6 % | 194,0 % | 4,0 | 10,3 | 12,0 % | 0,78 |
| 117 | 25,8 % | 26,8 % | 0,0 | 0,7 | −1,7 % | 0,96 | 110,8 % | 129,2 % | 3,1 | 8,4 | 12,5 % | 0,82 |
| 433 | 20,2 % | 21,3 % | 0,9 | 1,1 | 5,9 % | 0,94 | 60,8 % | 68,3 % | 1,7 | 4,6 | 5,9 % | 0,85 |
| **alle** | | | **1,4** | **4,4** | **4,2 %** | | | | **6,4** | **23,9** | **11,6 %** | |

Abw. = pandapower − gridsim in Prozentpunkten (Pp) der Auslastung. Überlast (> 100 %) in Abschnittsstunden:
heute gridsim 65, pandapower 71, uneinig 6 (von 4 754); 2040 gridsim 969, pandapower 1 191, uneinig 222
(von 9 174).

Lesart: Die radiale Summation ohne Verluste rechnet den Strom bei 400 V. Bei Konstantleistungslasten steigt der
Strom, wenn die Spannung sinkt; daher liegt gridsim systematisch **unter** dem Lastfluss, um etwa den
Kehrwert der Spannung (heute U min 0,92–0,98 pu → 2–7 %, 2040 U min 0,69–0,97 pu → bis 17 %, Spitzen bis 140 Pp
bei Station 261). Für die thermische Frage heute ist die Abweichung klein; in 2040 sind die gridsim-Werte als
Untergrenze zu lesen. Die Spannungen selbst sind kein Ergebnis (synthetisches Netz, ideale Sammelschiene).

### Erster Lauf: Dashboard-Prüfung

API aus dem Arbeitsordner auf hetzner (`127.0.0.1:17099`, `GRIDSIM_PREPARED=prepared-ns`, `GRIDSIM_CACHE=cache-ns`,
1 Worker), dazu die Seite `site/` mit dem aktuellen `web/gridsim/` unter demselben Ursprung, SSH-Tunnel vom Mac,
Playwright (Chromium, 1440 × 900). Geprüft: Lauf heute und 2030 (2012, ungesteuert, 20 Seeds aus dem Cache in
8,2 s), Leitungsebene ein, Schalter „Control limits“ und „Grid storage“ umgestellt.

- Screenshots: `docs/abnahme-screens/dashboard-1-start.png`, `dashboard-2-run-heute.png`,
  `dashboard-2-run-2030.png`, `dashboard-3-lines-heute.png`, `dashboard-3-lines-2030.png`,
  `dashboard-4-switches.png`.
- Konsole: keine Fehler und keine Warnungen aus Seite oder MapLibre (kein Fehler durch leere Literal-Ausdrücke);
  nur Chromium-Hinweise „GPU stall due to ReadPixels“. In einem ersten Durchgang liefen Kacheln von basemap.at
  in eine Zeitüberschreitung (Netz, nicht Code); im zweiten Durchgang luden alle.
- Leitungsebene lädt (465 Stationsnetze) und färbt Stationen nach „Engpass zuerst“; Kacheln für Leitung, Kennzahl
  „Line limits before transformer“ und Leitungslänge über Grenzstrom erscheinen.
- Befund im ersten Durchgang: Überschrift „all 257 transformers“ und die Einheit „of 257“ der Kachel
  „Transformers overloaded“ waren fest im Code. In Fix-Runde 1 behoben: Die Überschrift nimmt die Zahl aus
  `/api/stations`, die Kachel `region.n_stations` des Laufs (`regionTitle`, `tileUnit` in `web/gridsim/charts.js`,
  Node-Test). Die Screenshots dieses Durchgangs sind durch die der Fix-Runde 4 ersetzt.
