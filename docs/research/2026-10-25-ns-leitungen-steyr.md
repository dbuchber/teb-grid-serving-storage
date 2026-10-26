# Niederspannungsleitungen im Steyr-Modell: Befunde und Recherche (Zwischenstand)

Stand 25.10.2026, nachmittags. Anlass: Beim Pitch der TEB-Demo kam von Jury und Netzbetreiber der Einwand,
dass nicht nur die Trafos ein Limit haben, sondern auch die verlegten Leitungen. Dieses Dokument sammelt,
was unsere Rechnungen dazu schon zeigen, welche Daten wir haben und was die Online-Recherche ergab.
Die Quellen aus Abschnitt 4 bis 6 haben Recherche-Agenten zusammengetragen. Zahlen und Zitate sind dort
übernommen und noch nicht von Hand gegen die Originale geprüft. Eigene Folgerungen sind als solche markiert.

## 1. Kurzfassung

- Unsere synthetischen NS-Netze zeigen im **heutigen** Winter bei 40–50 von 257 Stationen ein Kabel über
  100 % (bis 400–600 %), aber nur 6–11 Trafos über 100 %. Mit realen Netzen ist das nicht vereinbar.
- Ursache laut Recherche: Die Stränge sind etwa doppelt so lang wie in realen Netzen (längster Abgang im
  Median 930–1190 m statt typisch 150–500 m), und die Querschnitte sind pauschal statt nach Last bemessen.
- Die Richtung des Einwands stimmt trotzdem: In realen städtischen Netzen sind bei Vollelektrifizierung
  Leitungen häufiger überlastet als Trafos (München 2050: 84 % gegenüber 53 % der Netze).
- Öffentliche Daten zu realen NS-Leitungen in Steyr gibt es nicht. Brauchbar sind Kennzahlen der Netz OÖ
  (79 % Kabel, ca. 2,7 km NS-Leitung und ca. 383 kVA je Station) und Referenzwerte aus der Literatur.
- Vorschlag: synthetisches Netz nach Planungsregeln neu auslegen (Stranglänge begrenzen, Querschnitt
  nach Strom und Spannungsfall bemessen, Gleichzeitigkeit je Abschnitt), dann Leitungen neben Trafos in
  gridsim bewerten. Entwurf folgt separat.

## 2. Was unsere Rechnungen schon zeigen

Lastfluss mit pandapower auf den synthetischen Straßennetzen (K13), jeweils nur die 24 stärksten Stunden
je Station, nicht das ganze Jahr.

**Sommer, Rückspeisung** ([Variante-A-Bericht](../reports/2026-10-24-steyr-variante-a.md), Abschnitt
„Spannung und Kabel“): Kabel über 100 % nur bei 2 von 257 Stationen, beide in der Klasse über 250 kWp.

**Winter, Bezug** (Läufe der [Nachrechnung](../reports/2026-10-24-nachrechnung-gutachten.md), hetzner
`/data/infra-kg-austria/work/steyr-gutachten-2026-10-25/output-need-g-<jahr>-<szenario>/`, Dateien
`speicherbedarf_summary.json` und `lastfluss_bezug.csv`, ausgewertet am 25.10.2026):

| Wetterjahr | Szenario | Kabel > 100 % | Trafo > 100 % | nicht konvergiert | Kabelauslastung Median / P90 / Max |
|---|---|---|---|---|---|
| 2023 | heute | 40 | 6 | 19 | 46 / 136 / 422 % |
| 2023 | 2030 | 76 | 77 | 47 | 73 / 183 / 418 % |
| 2023 | 2040 | 113 | 155 | 102 | 116 / 266 / 493 % |
| 2017 | heute | 45 | 6 | 24 | 49 / 142 / 389 % |
| 2017 | 2030 | 75 | 87 | 53 | 76 / 186 / 476 % |
| 2017 | 2040 | 109 | 151 | 110 | 114 / 268 / 595 % |
| 2012 | heute | 50 | 11 | 27 | 50 / 154 / 449 % |
| 2012 | 2030 | 87 | 114 | 68 | 79 / 207 / 478 % |
| 2012 | 2040 | 102 | 138 | 125 | 121 / 258 / 551 % |

Lesart:

- Stationen, deren Lastfluss nicht konvergiert, fehlen in der Auslastungsstatistik. Das sind
  vermutlich die schwächsten Netze; die Werte sind also eher zu niedrig.
- Leitungstypen im Modell: Stadt NAYY 4x150, Land Al 95 (Freileitung), Hausanschluss NAYY 4x50
  ([Belegregister](2026-10-24-netzmodell-belege.md), K3, K13).
- Spannung: schon heute 165–169 Stationen über 5 % Spannungsfall oder nicht konvergiert; bei Abgängen
  unter 500 m kein Fall über 5 %.

## 3. Eigene Datenbestände (infra-kg, hetzner)

| Quelle | Inhalt | Für NS-Leitungen |
|---|---|---|
| BEV DLM, `BAU_2700_STROMLEITUNG_L`, `BAU_2800_STROMMAST_P` (Stand 2023-01-25) | nur 110–380 kV; im Raum Steyr 37 Leitungen, 1014 Masten (APG, Netz OÖ, Netz NÖ, ÖBB) | nein |
| BEV ALS, `raw/bev-als-20250915` (538 GB) | Höhenraster 1 m, EPSG:3035, Kacheln 50 × 50 km | kaum, Holzmasten und Seile bei 1 m nicht zuverlässig |
| BEV Orthofotos, `raw/bev-dop-2026-10-19` (856 GB, 2022–2025) | 20 cm, für Steyr schon für die PV-Erkennung genutzt | eventuell, Masten und Trassen am Land |
| Katalog `infra_kg` (ca. 74 000 Datensätze), Stichwortsuche | Treffer nur aus Wien, Tirol, Vorarlberg; OÖ-„Straßeneinbauten“ sind Zäune und Leistensteine | nein |
| OSM, Overpass-Auszug 25.10.2026 | siehe unten | fast nur HS und MS |

OSM-Auszug (Ausschnitt 47,92–48,17° N, 14,20–14,635° O wie die übrigen Steyr-Eingänge), abgelegt mit
Abfrage, Zeitstempel und SHA256 auf hetzner unter
`/data/infra-kg-austria/work/steyr-leitungen-2026-10-25/osm/` (ODbL):

| Objekt | Umfang | Einordnung |
|---|---|---|
| `power=line` 110–380 kV | 560 km, 968 Masten | Hochspannung |
| `power=cable` | 7 km | überwiegend 110 kV |
| `minor_line`, 3 Leiter | 226 km | Mittelspannung (Energie AG) |
| `minor_line`, 20/30 kV angegeben | 22 km | Mittelspannung |
| `minor_line`, 400 V angegeben | 7 km | Niederspannung |
| `minor_line` ohne Angaben | 172 km | unklar |
| `pole` | 5402, davon 5 mit 400 V | überwiegend MS |
| `cable_distribution_cabinet` | 1 | NS-Kabel nicht kartiert |

Die DLM-Auszüge liegen daneben unter `.../steyr-leitungen-2026-10-25/dlm/`.

## 4. Netzbetreiber, Ausbau, Kennzahlen

### Netzbetreiber

Netz Oberösterreich GmbH (Energie AG) für Steyr und Steyr-Land; Behamberg (NÖ) nicht geprüft.
Spannungsebenen 400 V, 30 kV und teils 10 kV, 110 kV, dazu eine Sonderebene **3 kV in Steyr**.
Versorgung von Steyr über die Umspannwerke Steyr Fischhub, Steyr Ost und Steyr Nord.

- Netz OÖ, Netzentwicklungsplan 2026 (V-NEP 2026), Juli 2026, S. 5:
  https://www.ebutilities.at/documents/2026/07/V-NEP_2026_Netz_Ober%C3%B6sterreich.pdf
- EUROPTEN, Projekt 110-kV Steyr Nord – Steyr Ost (Bau 1940/41, Maste 2024 ersetzt):
  https://www.europten.com/en/whats-new/project-detail/default-71a432041bf27c47f3c4dc9fcc88de85

### Kennzahlen Netz OÖ (V-NEP 2026, Tab. 1 und 2)

| | 2019 | 2025 |
|---|---|---|
| NS Freileitung (km) | 6 050 | 5 139 |
| NS Kabel (km) | 17 425 | 19 519 |
| MS Freileitung (km) | 5 247 | 5 080 |
| MS Kabel (km) | 2 730 | 3 145 |
| Trafostationen MS/NS | 8 770 | 9 193 |
| Leistung MS/NS (MVA) | 2 982 | 3 448 |

Eigene Folgerungen: NS-Kabelanteil 74 % (2019) → 79 % (2025; Energie AG GB 2024/25 nennt 79,0 %);
ca. 383 kVA je Trafo; ca. 2,7 km NS-Leitung je Station; ca. 58 Kundenanlagen je Station.
Österreich gesamt 2025: 185 606 km NS, davon 86 % Kabel (Oesterreichs Energie, Stromstatistik 2026).

Verkabelte NS-Freileitung der Netz OÖ: 135 km (2022/23), 177 km (2023/24), 113 km (2024/25)
(Energie AG Geschäftsberichte, z. B. GB 2025 S. 236:
https://berichte.energieag.at/2025/geschaeftsbericht/_assets/downloads/gesamt-energieag-gb2025.pdf).

Planung der NS bei Netz OÖ „im Regelfall auf Erfahrungswerte und/oder die abgerechnete Energieabgabe
und -einspeisung in Kombination mit synthetischen Lastprofilen“ (V-NEP 2026, S. 30).

### Geplanter Ausbau und Engpässe in der Region

- Einspeisekapazität NE 4 (V-NEP 2026, Tab. 6): **UW Steyr Nord 0 MVA verfügbar** in allen Quartalen
  Q3/2024–Q2/2026; UW Bad Hall 0 MVA; UW Steyr 51 → 61 MVA.
- Projekte: UW Großraming +30 MVA (2028), UW Bad Hall +10 MVA (2028), 110 kV Steyr Nord – Kremsmünster
  neues Seil (2033), UW Molln Neubau (> 2036) zur Entlastung von Steyr Fischhub wegen langer
  30-kV-Leitungen und Spannungsanhebung (V-NEP 2026, S. 48, 68, 79, 85).
- Für NE 6 und 7 keine Einzelprojekte: „überwiegend durch Kundenprojekte getrieben“ (V-NEP 2026, S. 98).
- PV-Einspeisestopp Dezember 2023 an sieben UW, darunter Steyr-Nord (Tips, 05.12.2023:
  https://www.tips.at/nachrichten/ooe/wirtschaft-politik/628429-photovoltaik-einspeisestopp-in-sieben-regionen-in-oberoesterreich).
- Netz OÖ: „Beschränkende Faktoren für die Einspeisung von PV-Strom sind in erster Linie die Mittel- und
  Niederspannungsnetze“ (Tips Gmunden, 03.08.2023:
  https://www.tips.at/nachrichten/gmunden/wirtschaft-politik/614203-umspannwerke-am-traunfall-und-in-ohlsdorf-wurden-ausgebaut).
- Land OÖ, PK 06.10.2023, S. 4: NS-Baumaßnahmen der Netz OÖ „von 750 auf 912“ in einem halben Jahr
  (https://land-oberoesterreich.gv.at/Mediendateien/LK/PKLRAchleitner_06102023_Internet.pdf).
- WKO OÖ, Monitoringbericht Dezember 2025, S. 4: UW-Auslastung „Steyr 32 %“, „Steyr-Land 90 %“
  (https://www.wko.at/ooe/news/folder-energieinfra-netze-speicher-6-seiter-251128-v1.pdf).

### Baugeschichte (dünne Quellenlage)

Belegt sind nur Eckpunkte: 110-kV-Leitungen aus den 1920er bis 1940er Jahren; Papierkabel in
Verteilnetzen „bis in die 1990er-Jahre“ verlegt (VDE FNN Infoblatt 2017, deutsche Quelle); NS-Kabelanteil
in Österreich 2017 rund 81,5 % (eigene Rechnung aus vienna.at, 10.01.2019, nach Oesterreichs Energie).
Nicht gefunden: Einführungsjahre von NAYY/NA2XY in Österreich, Querschnittsentwicklung, Altersstruktur
der NS der Netz OÖ, Abschluss der ländlichen Elektrifizierung in OÖ.

## 5. Fachliteratur: Referenzwerte realer NS-Netze

### Netzstruktur

| Größe | Wert | Quelle |
|---|---|---|
| Abgänge je Station | ca. 3,4 (Netz OÖ und Salzburg Netz: 11 000 Netze, 37 000 Abgänge) | Bletterie, Kadam, Abart, Priewasser, EnInnov 2016, S. 2 |
| Abgänge je Station | ca. 3,75 (14 400 Netze, 54 000 Abgänge, zwei AT-VNB) | Kadam, Diss. TU Wien 2018, S. 40, https://repositum.tuwien.at/handle/20.500.12708/7709 |
| Stranglänge Stadt | Stich 70 %, 150–300 m; 2 Abzweige 25 %, 200–350 m; 3 Abzweige 5 %, 300–500 m | Consentec 2013 nach Kadam 2018, S. 25 |
| Stranglänge Land | Stich 30 %, 200–400 m; 2 Abzweige 50 %, 300–500 m | ebd. |
| Hauptstrahl, Modalwert | ca. 150 m in allen Siedlungsklassen; 0,5–1 km nur bei Weiler und Streusiedlung | Gust, Masterarbeit KIT 2014, S. 38–41, https://publikationen.bibliothek.kit.edu/1000045150 |
| mittlere Stranglänge je Siedlungstyp | Streusiedlung 500–600 m, Dorf 270–450 m, Altstadt 166 m | Weisenstein et al., TU Kaiserslautern 2022, Tab. 4, https://kluedo.ub.rptu.de/frontdoor/index/index/docId/6755 |
| Gebäude je Strang | 18–60 | ebd., Tab. 5 |
| Einzelanschluss-Abgänge | 11–17 % der Abgänge | Kadam 2018, S. 41 |

### Grenzströme (Weisenstein et al. 2022, Tab. 10)

NAYY 4x35 123 A, 4x50 144 A, 4x150 275 A, 4x240 313 A; Freileitung Al 4x25 135 A, 4x70 255 A, 4x95 320 A.
Das Datenblatt von Faber Kabel nennt für 4x240 bis 364 A; die Quellen weichen dort ab.

### Planungsregeln und Gleichzeitigkeit

- Auslegung auf 100 % Grenzstrom (Patzack et al., FGH, EnInnov 2016, S. 3) und 5 % Spannungsfall im
  Lastfall, 3 % Anhebung bei Einspeisung (Weisenstein et al. 2022, S. 9–11). Erst thermisch prüfen,
  dann Spannung; sonst nächster Querschnitt oder Parallelkabel.
- Gleichzeitigkeit Haushalte: g(n) = g∞ + (1 − g∞)·n^(−3/4), g∞ ≈ 0,06–0,07 für Haushalte ohne
  elektrische Heizung (Arnold, Diss. TU Kaiserslautern 2019, S. 33–35, nach Kaufmann 1995).
  Spitzenlast für große Kollektive ca. 2 kW je Wohnung, konservative VNB 3,5 kW (Weisenstein 2022).
- Luft-Wasser-Wärmepumpen: Gleichzeitigkeit im Kollektiv „rund 1,1“ auf die Nennleistung bei A-7/W55
  (Fraunhofer IEE/ISE für SWM, 16.04.2026, https://idw-online.de/de/news869300).
- E-Autos: +1,1 kW je Fahrzeug bei 10 Fahrzeugen, +0,53 kW bei 224 (99-%-Quantil, Smart-Meter-Daten
  Salzburg Netz; Maier, Groiß, EnInnov 2026).

### Was zuerst begrenzt

- PV allein, Netz OÖ (überwiegend ländlich): ca. 90 % der Abgänge spannungsbegrenzt, die Hälfte davon
  unter 37 % Strom-Auslastung; städtischerer VNB: 77 % Spannung, 21 % Strom (Bletterie et al. 2016, S. 4–5).
- Vollelektrifizierung 2050, 4 198 reale Münchner Netze: Leitung überlastet in ca. 84 %, Trafo in
  ca. 53 %, Unterspannung in ca. 59 % der Netze; Spannungsverletzungen fast nur zusammen mit
  Leitungsüberlastung (Niederle et al., EnInnov 2026, Tab. 1,
  https://www.tugraz.at/fileadmin/user_upload/Events/Eninnov/EnInnov2026/files/lf/262_LF_Niederle.pdf).
- Ungesteuertes Laden bei voller E-Mobilität im Land Salzburg: ca. 30 % der Trafostationen über 100 %
  (Maier, Groiß 2026).

### Synthetische Netze: bekannte Fehler

- Open-Data-Synthese in drei NÖ-Gemeinden: tendenziell **weniger Trafos** als real, damit längere Stränge
  (Seiler, Diplomarbeit TU Wien 2025, DOI 10.34726/hss.2025.129705).
- Klassifizierung über den mittleren Hausabstand; Direktanschlüsse als eigene Klasse
  (Lindner, Aigner, TUM, EnInnov 2016; Gust 2014).
- Auch reale GIS-Exporte sind fehlerhaft: nur 84 % bestehen den Kurzschlussimpedanz-Test (Kadam 2018).

## 6. Zeitungsarchive und Gemeindeschriften

Ergiebigste Quelle ist das **Amtsblatt der Stadt Steyr**, 1958 bis heute mit Volltext im Stadtarchiv-System
SAIS (https://sais.steyr.gv.at). ANNO lieferte nur Suchausschnitte, die Volltextseiten sind hinter einem
Captcha; die Steyrer Zeitung ist dort nur 1876–1890 durchsuchbar. Gemeindezeitungen waren wenig ergiebig.

### Bauphasen, historisch

- **1894:** Stromversorgung Steyr nimmt den Betrieb auf, „75 Abnehmer mit 626 angeschlossenen Lampen“;
  1914 Zweiteinspeisung über die Umspannstation Sarning; im Ersten Weltkrieg Umbau des Verteilnetzes von
  Gleich- auf Drehstrom (Amtsblatt Steyr, März 1969, S. 4–5,
  https://sais.steyr.gv.at/index.php/amtsblatt-jg-12-nr-3-marz-1969).
- **1969:** „rund 16.700 Stromkunden“, Leitungsnetz „289.630 m“ Hoch- und Niederspannung; OKA seit 1964
  Rechtsnachfolgerin der „Elektrizitätswerke in Steyr GesmbH“, seither „rund 34 Millionen Schilling“ in die
  Modernisierung, „zum modernsten Ortsnetz im Bereich der Gesellschaft“ (ebd.).
- **1963:** Gemeinderat stimmt dem Verkauf des Heimfallsrechts am E-Werk Steyr an die OKA zu, „Mindestkaufpreis
  … 16 Mill. S“ (Amtsblatt Februar 1963, S. 2). Konzessionsvertrag von 1916 lief bis 31.12.1962
  (https://steyr.dahoam.net/wp-flippingbooks/Elektrizitaetswerke/1919/).
- **1958–1976:** zahlreiche Baubewilligungen für Trafostationen in Steyr, meist mit dem Wohnbau, teils im
  Keller von Hochhäusern („Die Stromversorgung erfolgt über eine im Keller untergebrachte eigene
  Trafostation“, Amtsblatt August 1959, S. 8); Tabor 1966, Koloman-Wallisch-Straße 1973, Kegelprielstraße
  1976 (SAIS, Suchbegriff „Trafostation“).
- **1962–1985:** Ausbau der Umspannwerke Fischhub, Sarning und Steyr Ost (Amtsblätter 1962, 1969, 1983–1985).
- **1951/52:** Elektrifizierung Maria Neustift, Transformatoren „in der Walleiten, in Moosgraben, Neustift und
  Sulzbach“ (Linzer Volksblatt, 27.04.1951, S. 4, http://data.onb.ac.at/ANNO/lvb19510427?seite=4);
  „Lichtfeier“ zur Fertigstellung (OÖN, 29.01.1952, S. 4). Weyer, Ortschaft Pichl, Lichtfeier zur
  Fertigstellung des Stromnetzes (OÖN, 30.10.1951, S. 4).

### Verkabelung und Verstärkung seit 1990

- **2010:** 110-kV-Ringschluss Steyr-West als Erdkabel vom UW Gleink durch Resthof, Tabor, Schlüsselhof und
  Fischhub (Amtsblatt März 2010, S. 9); Ring 2024 fertig, „durchgehende Verbindung zwischen den drei
  Umspannwerken“ (Tips Steyr, 14.06.2024,
  https://www.tips.at/nachrichten/steyr/wirtschaft-politik/649433-110-kv-ringleitung-in-steyr-ist-fertig).
- **2020, Steyr Nord:** „ein Mittelspannungs-Erdkabel mit 30.000 Volt angebohrt“ (MeinBezirk, 06.04.2020).
- **2019, Laussa/Ennstal:** 3,7 km MS-Erdkabel zwischen den UW Pyhrn und Großraming, „43 Trafostationen
  können … doppelt versorgt werden“, über 60 km in der Region bereits verkabelt (MeinBezirk, 17.12.2019).
- **2023, Sierning/Bad Hall/Schiedlberg:** Seilwechsel an der 30-kV-Freileitung „Hilbern – Thanstetten“
  (3,706 km), Neubau der „30 kV-Masttrafostation ‚Hilbern‘“, „Leistungserhöhung“ der Masttrafostation
  „Kamberg“ (Kundmachung Amt der OÖ Landesregierung, AUWR-2023-145649/5, 03.05.2023,
  https://www.land-oberoesterreich.gv.at/Mediendateien/Formulare/Dokumente%20UWD%20Abt_AUWR/Kundmachung_2023-145649_5_Sign.pdf).
- **2026, Laussa:** Netz OÖ kündigt Erdkabelarbeiten an (Amtsblatt Laussa, ca. April 2026, S. 2).

### Engpässe und Störungen

- Einspeisestopp UW Steyr-Nord, Dezember 2023; betroffen „nicht nur der Norden der Stadt Steyr sondern auch
  die Umlandgemeinden Dietach, Wolfern, Aschach und Sierning“ (MeinBezirk, 14.12.2023); Petitionen in Steyr,
  Dietach, Sierning, Aschach, Losenstein, Großraming und Reichraming (Tips Steyr, 21.12.2023).
- Störungen an 30-kV-Freileitungen durch Bäume, Schnee und Sturm: Aschach 2022, Laussa bis Gaflenz 2021,
  St. Ulrich/Kleinraming 2023 (ca. 500 Haushalte), Schiedlberg 2026 (MeinBezirk; ooe.ORF.at, 23.09.2026).

### Was das für das synthetische Netz heißt (eigene Folgerung)

- **Kernstadt Steyr:** Kabelnetz überwiegend aus der Erneuerung ab 1964 und der Verdichtung 1958–1976, viele
  Stationen, teils in Gebäuden; MS im Stadtnorden als Kabel belegt.
- **Alpenvorland** (Sierning, Bad Hall, Schiedlberg, Aschach, vermutlich Wolfern, Dietach, St. Ulrich):
  30-kV-Freileitung mit **Masttrafostationen**, also kleine Trafos und vermutlich teils NS-Freileitung;
  verstärkt wird über Trafo-Leistungserhöhung und Seilwechsel.
- **Ennstal und Voralpen** (Laussa, Großraming, Maria Neustift, Gaflenz, Weyer): spät elektrifiziert
  (1950–52), MS inzwischen weitgehend verkabelt; NS in Streusiedlungen vermutlich lange, schwache Abgänge.
- Ein kommunaler Netzbetreiber existierte in Steyr nie (privat bis 1963/64, dann OKA bzw. Energie AG / Netz OÖ),
  im Modell also einheitliche Standards eines Betreibers.

## 7. Offen

- ANNO-Volltexte (Captcha), Amtsblatt Steyr 2016 und 2022 (verschlüsselte PDFs), Gemeinde-Webseiten von
  Losenstein, Weyer, St. Ulrich und Rohr (nicht erreichbar); Gemeindezeitungen von Sierning, Garsten, Wolfern,
  Ternberg und Adlwang nicht systematisch durchsucht.
- Nicht abrufbar waren u. a. SimBench (Energies 13, 3290), Weiß et al. 2024 (Energies 17, 4433), die
  Kerber-Dissertation, der Volltext des Rechnungshofberichts „Transformation der Stromverteilernetze“ und
  netzooe.at „Kennzahlen Stromnetz“. Perzentile der Stranglänge (P90) fehlen noch.
- Direkte Anfrage bei der Netz OÖ nach NS-Kabeltypen je Baujahrsklasse und Trafoverteilung in Steyr-Land.
- Die 172 km OSM-`minor_line` ohne Spannungsangabe lassen sich eventuell über Masthöhe und Mastabstand
  (ALS-Raster) einordnen; ungeprüft.

## 8. Folgerungen für das Modell (eigene Folgerung, Entwurf folgt)

1. Stränge begrenzen: längster Abgang etwa 400–600 m in der Stadt, etwa 800 m am Land; längere Stränge
   teilen oder eine zusätzliche Station setzen.
2. Querschnitt je Abschnitt nach Last bemessen: zuerst Grenzstrom, dann 5 % Spannungsfall, sonst
   nächster Querschnitt (Verfahren nach Weisenstein et al. 2022).
3. Last je Leitungsabschnitt mit Gleichzeitigkeit nach Zahl der nachgelagerten Kunden; Wärmepumpen
   praktisch ohne Durchmischung.
4. Plausibilitätsziele: ca. 2,7 km NS-Leitung je Station im Mittel, 3,4–3,8 Abgänge, ca. 79 % Kabel
   nach Siedlungstyp gestaffelt (Kernstadt fast vollständig Kabel, Alpenvorland mit Masttrafos und teils
   Freileitung, Streusiedlungen im Ennstal lange, schwache Abgänge); heute höchstens einzelne Abgänge
   knapp über 100 %.
5. Erst danach Leitungen neben Trafos in gridsim bewerten und mit den Grenzen von MS und Umspannwerk
   spiegeln (UW Steyr Nord ohne freie Einspeisekapazität).
