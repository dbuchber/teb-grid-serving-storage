# Design: Simulationsbibliothek `gridsim` und Live-Dashboard Steyr

Stand: 24.10.2026. Hackathon-Deadline: **So 25.10.2026, 11:30** (TEB AI Hackathon,
Challenge Grid-Serving Storage, Partner Smart Grids Austria).

Kennzeichnung: **[Owner]** = vom Owner entschieden; **[Vorschlag]** = Entscheidung des
Designs (Claude), änderbar; **[Builder]** = bewusst dem Umsetzenden überlassen.

## 1. Zweck und Warum

Die Bedarfsrechnungen für Steyr (Heimspeicher, Wärmepumpen, E-Autos, V2G) liegen heute
als einzelne Skripte `steyr_*.py` im Repo infra-kg-austria und laufen auf hetzner. Der
Owner ist mit vier Dingen unzufrieden [Owner]:

1. **Wartezeit je Lauf:** ein Jahreslauf `steyr_storage_need.py` (2040, Wetter 2023, LoD1-Wärme,
   Fernwärme) dauert 89 s und braucht 6,5 GB RAM; 74 % der Zeit steckt in `ev_kw`
   (Python-Schleife je Auto und Tag, 3,7 Mio. skalare `np.clip`-Aufrufe).
2. **Viele Varianten:** Wetterjahre × Szenarien × PV-Faktoren × Steuerlogik ergeben
   Dutzende Einzelprozesse, die jeweils alle Eingaben neu lesen.
3. **Umständlicher Ablauf:** Start, Ergebnisse holen und Tabellen in die Doku übertragen
   sind Handarbeit.
4. **Unsichere Ergebnisse:** ein Zufallsseed, keine Bandbreite, schwer vergleichbar.

Ziel ist eine **neue Simulationsbibliothek** und darauf eine **Live-Demo** für den Pitch:
Das Publikum sieht echte Rechenläufe in angenehmer Geschwindigkeit, nicht nur
vorberechnete Bilder [Owner].

Kernaussage, die die Demo tragen muss (Ergebnisse Session 18, 24.10.): Einspeiseengpässe
gibt es heute kaum; der Winterengpass 2040 kommt aus der Wärmepumpe und dauert Tage
(dafür braucht es Netzausbau); E-Mobilität ist mit gesteuertem Laden lösbar; V2G und
Heimspeicher sind Reserve bei Gleichzeitigkeit; pauschale Zeitfenster (WiNAP ab 23 Uhr)
erzeugen neue Spitzen, ein gestaffeltes Segmentsignal (T3d) nicht.

## 2. Ziele, Nicht-Ziele, Anti-Ziele

**Ziele**
- Eine Bibliothek ersetzt fachlich alle Steyr-Skripte: Speicher (Variante A), Bedarf je
  Segment (§ 7.2 ems-konzept), Wärmepumpe/E-Auto, V2G-Demo [Owner: „komplett jetzt“].
- Regionen-Dashboard (Variante C) mit Drilldown auf die Tageskurve einer Station [Owner].
- Monte-Carlo-Band statt Einzelwert [Owner].
- Vergleiche: Steuerlogiken, Szenarien, Wetterjahre, Speicher gegen Netzausbau [Owner].

**Nicht-Ziele**
- Keine Lastflussrechnung (pandapower) im Live-Pfad; Spannung bleibt Sache der
  bestehenden Skripte. [Vorschlag]
- Keine Änderung an den bestehenden `steyr_*.py`; sie bleiben für die anderen Sessions
  unverändert, bis die Bibliothek sie ersetzt [Owner: „parallel, alte bleiben“].
- Keine Datenbank; keine Nutzerverwaltung über Keycloak hinaus.

**Anti-Ziele** (wäre ein Fehlschlag, auch wenn es technisch läuft)
- Die Demo hängt oder bricht im Pitch ab (Rechenlauf ohne Rückmeldung, Absturz bei
  zweitem Klick, fehlende Netzverbindung ohne Fallback).
- Zahlen, die den Tabellen von Session 18 in Größenordnung oder Tendenz widersprechen,
  ohne dass der Grund (Modelländerung) sichtbar ist.
- Annahmen (Kosten, Anteile) erscheinen als Messwerte.

## 3. Rahmen

- **Rechnen auf hetzner** (`hetzner-wikidata`, 24 Kerne, ca. 49 GB RAM frei), nicht auf
  dem Mac [Owner, Memory]. Der Uni-Knoten bringt für diese Last nichts (Messung 24.10.).
- **Hosting:** Docker-Container auf hetzner unter **teb-hackathon.bbger.at**; Caddy-Block,
  Container-Härtung und Veröffentlichung macht **Session infra-kg-austria-18** [Owner].
  Die Bibliothek liefert dafür ein Image bzw. Dockerfile, einen Startbefehl und einen Port.
- **Einbettung in die Seite von Session 02** [Owner]: Die Seite gehört **infra-kg-austria-02**
  (Repo infra-kg-austria, `deploy/teb-hackathon/site/`, live `/data/projects/teb-hackathon/site/`,
  Aufbau Problem → Lösung → interaktive Demo → Ergebnisse → Methodik → Daten und Grenzen).
  Das Dashboard wird dort im Abschnitt „interaktive Demo“ eingebettet. Wir liefern
  **Rechen-API + Dashboard-Komponente**, 02 bettet ein und schreibt die Texte.
- **Stack der Seite (von 02 vorgegeben):** statisch ohne Build, `index.html` + ES-Module
  (`js/{app,data,map,flow,chart}.js`), **MapLibre 4.7.1** (CSP-Build, vendored),
  Diagramme als **handgeschriebenes SVG**, CSP `script-src 'self'`,
  `connect-src 'self'` + basemap.at. Die Komponente hält sich daran: keine CDN-Skripte,
  keine Inline-Skripte, keine weitere Karten- oder Chart-Bibliothek.
- **Gleicher Origin:** Die API läuft unter `teb-hackathon.bbger.at/api/` hinter demselben
  Login, damit CSP und Cookies nicht erweitert werden müssen; den Caddy- bzw. nginx-Eintrag
  setzt Session 18.
- **Zugang: Login** [Owner] über das bestehende Gate der Seite: nginx + oauth2-proxy,
  Keycloak-Realm `teb-hackathon`, Gruppe `teb-access`.
- **Code im Repo teb-grid-serving-storage** [Owner], z. B. `gridsim/` (Paket) und
  `demo/` (Backend + Frontend). Bisher enthält das Repo nur Doku.
- **Eingabedaten** liegen auf hetzner unter
  `/data/infra-kg-austria/work/steyr-pv-2026-10-24/input/` (PVGIS je Ausrichtung und
  Wetterjahr 2012/2017/2023, INCA-T2M je Station, APCS-Synthload 2026, OSM-Stationen,
  LoD1-Gebäude, when2heat, Fernwärmegebiete). Abgeleitete AGGM-Geometrie wird nie
  versioniert [Memory]; Eingaben werden in den Container gemountet, nicht ins Image
  kopiert.
- **Git:** nicht committen oder pushen ohne Auftrag; auf dem Default-Branch erst branchen.

## 4. Fachliches Modell [Owner: übernimmt den Stand der Skripte vom 24.10.]

Die Bibliothek übernimmt die Modellannahmen der aktuellen Skripte (Stand hetzner-Kopie
24.10., inkl. Änderungen von Session 18), nicht deren Code-Struktur:

- **Netz/Knoten:** `steyr_sim_variant_a.build_members` (Gebäude → Knoten → Station,
  257 Stationen, Trafo-Bemessung `trafo_kva`, Normgrößen 125–1000 kVA).
- **PV:** PVGIS-Profile je Ausrichtungsklasse (E30, F10, S35, W30) × kWp je Knoten;
  PV-Faktoren × 1 / × 1,5 / × 2.
- **Haushaltslast:** APCS-Synthload H0 × 3 000 kWh je Haushalt.
- **Wärmepumpe:** Wärmebedarf je Gebäude aus LoD1 + TABULA, kalibriert auf Statistik
  Austria (18,8 MWh EFH, 7,1 MWh je MFH-Haushalt); COP nach when2heat; Streuung
  Heizgrenze 14–17 °C, Zeitversatz ± 2 h; Heizstab unter −7 °C; Fernwärme-MFH (Münichholz,
  Ennsleite, Resthof, Tabor) ohne Wärmepumpe; Temperatur je Station aus INCA.
- **E-Auto:** wie `steyr_wp_ev.ev_kw` (Tagesverbrauch nach Temperatur, Ankunftszeit
  werktags/Wochenende, 11 bzw. 3,7 kW, Ladebedarf mit Schwelle), aber vektorisiert.
- **Szenarien:** heute 0,15/0,08, 2030 0,35/0,25, 2040 0,70/0,60 (Anteil WP/E-Auto).
- **Speicher:** `simulate` (Strategien base, fixcap, forecast, room), C-Rate 0,5, η 0,95.
- **Bedarf je Segment:** § 7.2 (`steyr_storage_need.segment_row`): Ereignisse mit
  Mindestpause 8 h, E_inst = E_netto / 0,326, Speicheranzahl nach Energie und Leistung,
  Trafo-Stufen.
- **V2G:** wie `steyr_v2g_demo.py` (gesteuertes Laden mit Frist 7 Uhr, V2G 11 kW /
  15 kWh / 70 % verfügbar, Gleichzeitigkeitsfall 18 Uhr am kältesten Abend).

Neue Steuerlogiken für den Vergleich [Owner: Steuerlogiken vergleichen; Ausgestaltung
Vorschlag]:

| Steuerlogik | Verhalten |
|---|---|
| ungesteuert | E-Autos laden ab Ankunft, Speicher im Eigenverbrauch |
| WiNAP 23 Uhr | im Winter (1.10.–31.3.) starten alle E-Autos, die bis 7 Uhr laden können, um 23 Uhr; Heimspeicher laden netzseitig ab 23 Uhr, wenn der Nutzer das will (Anteil als Parameter) |
| T3d gestaffelt | wie WiNAP, aber das Rabattfenster beginnt je Station gestaffelt (z. B. 3 Gruppen 22/0/2 Uhr) und nur an Tagen mit Engpassprognose (perfekte Prognose als obere Schranke) |
| gesteuertes Laden | Wallboxen gedrosselt, sobald der Trafo voll ist; Nachladen bis 7 Uhr, Rest ungeladen ausgewiesen |
| V2G | gesteuertes Laden + Rückspeisung angesteckter Autos |
| Speicher netzdienlich | `forecast` bzw. `room` aus Variante A |

Siehe ems-konzept.md § 4.5 (T3d) und § 7.2.

Präzisierungen [Vorschlag, Entscheidung des Designs]:

- **Zwei getrennte Auswahlen:** *Ladesteuerung* (ungesteuert, WiNAP 23 Uhr, T3d gestaffelt,
  gesteuertes Laden, V2G) und *Speicherstrategie* (Eigenverbrauch `base`, netzdienlich
  `forecast`, `room`). Standard: Speicher im Eigenverbrauch. Bei WiNAP/T3d laden Heimspeicher
  netzseitig im Rabattfenster nur mit dem Anteil aus dem Parameter (Standard 0).
- **Gesteuertes Laden und V2G drosseln nur Wallboxen**, gegen 100 % Trafo-Bemessung wie
  `steyr_v2g_demo.controlled`. Wärmepumpen bleiben ungesteuert; sonst kippt die Kernaussage
  „Winterengpass aus der Wärmepumpe braucht Netzausbau“. Eine § 14a-artige WP-Drosselung ist
  ein späterer Zusatz, nicht Teil des Hackathons.

## 5. Auflösung [Owner: beides umschaltbar]

- **Jahresläufe stündlich** (8 760 h).
- **Drilldown-Tag in 15 Minuten** (96 Werte): H0 ist nativ viertelstündlich; PV linear
  aus Stundenwerten interpoliert; Wärmepumpe stundenkonstant; E-Auto viertelstündlich
  neu gerechnet. [Vorschlag]

## 6. Unsicherheit [Owner: Monte Carlo mit Band]

- Zufällig je Seed: Zuordnung WP/E-Auto zu Knoten, E-Auto-Verhalten, Streuung der
  Wärmepumpen. Netz, PV und Wetter sind fest je Lauf.
- Standard **20 Seeds** je Einstellung; Anzeige Median und 10–90-%-Band. [Vorschlag]
- Seeds deterministisch aus Basis-Seed + Index, damit ein Lauf reproduzierbar ist.

## 7. Dashboard (Variante C) [Owner]

- **Einstellungen:** Steuerlogik, Szenario, Wetterjahr, PV-Faktor; Lauf-Knopf.
- **Ablauf: Band wächst live** [Owner]. Jeder fertige Seed wird sofort angezeigt;
  Kacheln und Band aktualisieren sich, bis alle 20 Seeds da sind.
- **Kacheln:** Stationen mit Engpass (Last/Einspeisung), Engpass-h (Median), E_netto
  Summe, Speicher Summe, Trafo +1 / +2 und mehr / über 1 000 kVA, ungeladene E-Auto-Energie.
- **Vergleichsansicht:** dieselbe Kennzahl über Steuerlogiken, Szenarien oder Wetterjahre
  nebeneinander (je Säule/Punkt mit Band) [Owner: alle vier Vergleiche].
- **Speicher gegen Netzausbau:** Anzahl und Kosten der Heimspeicher/V2G-Autos gegen
  Trafo-Stufen und Leitungen. **Kosten aus unserer Recherche** [Owner], als Annahmen
  markiert und im Dashboard änderbar. Vorhanden: Speicher 600 €/kWh, Verschleiß 5 ct/kWh
  (ems-konzept § 7.3), Förderstufen § 5.2 (Platzhalter). **Nicht vorhanden:** Kosten je
  Trafo-Stufe und je Leitungsmeter. [Builder: recherchieren, Quelle nennen, sonst als
  Platzhalter kennzeichnen]
  **Nur Trafo-Stufen werden live gerechnet** (aus der Leistungsbilanz). Leitungen erscheinen
  als eigener, deutlich markierter Platzhalter („Leitungsausbau: Lastfluss nicht im
  Live-Modell“); keine Netzgeometrie in `prepare`. [Vorschlag]
- **Karte:** Stationen eingefärbt nach Engpass (Median über Seeds). Klick → **Drilldown:
  Trafo-Kurve des schlimmsten Tages** der Station in 15 min, mit Grenze und Beitrag von
  Haushalt, Wärmepumpe, E-Auto, PV, Speicher [Owner: „Ja, mit Tageskurve“].
- **Kennzeichnung:** jeder Wert mit Hinweis „Modellwert“; Annahmen in einer Legende.

## 8. Technik [Vorschlag, Details Builder]

- **Bibliothek `gridsim/`** in Schichten:
  1. `prepare`: einmal je Wetterjahr Knoten, Stationen, PV-, H0- und Temperaturmatrizen
     als `.npy`/`.npz` (float32, memory-mapped) – kein CSV/WKT-Parsen pro Lauf.
  2. `profiles`: Wärmepumpe und E-Auto vektorisiert (NumPy, ggf. Numba [Builder]).
  3. `strategies`: Steuerlogiken als austauschbare Funktionen auf Stationsmatrizen.
  4. `metrics`: § 7.2-Kennzahlen, V2G, Kosten.
  5. `runner`: Seeds parallel (Prozesspool auf hetzner), Ergebnis-Cache je Parameter-Hash,
     **Manifest** je Lauf (Parameter, Code-Version, Hash der Eingaben, Seeds, Laufzeit).
  CLI für Batchläufe, die die Tabellen nach § 7.2 als CSV/JSON wie heute erzeugt.
- **Zielwerte Laufzeit:** Jahreslauf alle Stationen, 1 Seed, 1 Steuerlogik ≤ 10 s;
  20 Seeds parallel ≤ 30 s bis zum vollen Band; Drilldown-Tag ≤ 1 s. RAM je Worker
  ≤ 2 GB.
- **Backend:** Python-Webdienst (z. B. FastAPI), Ergebnisse je Seed als Stream (SSE oder
  WebSocket). Höchstens ein laufender Rechenauftrag je Einstellung; gleiche Einstellung
  → Ergebnis aus dem Cache. Begrenzung paralleler Aufträge, damit hetzner nicht
  überläuft.
- **Schnittstelle zur Seite von 02** (Vorschlag 02, übernommen):
  - Anker `<div id="region-dashboard"></div>` im Abschnitt „Interactive demo“, oberhalb von
    Karte und Ablauf.
  - Modul `js/gridsim/dashboard.js` mit
    `export function mount(el, { apiBase: "/api/", stations, onSelectStation })`;
    `stations` = bereits geladene FeatureCollection aus `site/data/stations.geojson`
    (IDs `way/…`, `node/…`, `demo:steyr:station-NNN`); `onSelectStation(id)` meldet den
    Klick an Karte und Ablauf von 02.
  - Live-Updates per **SSE oder Polling** über `/api/` (kein WebSocket, sonst müsste die CSP
    `wss:` erlauben). CSP: `script-src 'self'`, `connect-src 'self' https://mapsneu.wien.gv.at`,
    `worker-src 'self'`.
  - Stil über die CSS-Variablen aus `style.css` (`--surface`, `--line`, `--ink2`,
    `--accent`, `--warn`, `--ok`), damit Hell und Dunkel passen.
  - Die API liefert Ergebnisse je Station mit genau diesen IDs (Abbildung aus `osm_id`
    bzw. synthetischen Stationen in `build_members` prüfen).
- **Frontend:** ES-Modul(e) für die Seite von 02 (MapLibre, SVG-Diagramme, siehe § 3);
  Oberfläche **Englisch** [Owner]. Vorhandene vorgerechnete JSON in `site/data/`
  (Session 18: stations/timeseries/v2g_cases/lv_lines; e2: pv_storage/devices) bleiben
  unangetastet; Stations-IDs mit `stations.geojson` abgleichen.
- **Container:** ein Image, Eingaben read-only gemountet, Cache-Verzeichnis beschreibbar,
  lauscht auf 127.0.0.1:<Port>; Übergabe an Session 18 mit Startbefehl und Port.
- **Pitch läuft online am eigenen Laptop** [Owner]. Fallback: vorgerechnete Läufe der
  wichtigsten Einstellungen im Cache („Run“ spielt sie im gleichen Tempo ab, falls hetzner
  langsam ist). Kein Offline-Export. [Vorschlag für den Fallback]
- **Reihenfolge bei Zeitnot:** Der Owner hat alle vier Teile zum Minimum erklärt
  (Steuerlogik-Vergleich, Szenarien + Wetter, Karte + Drilldown, Speicher gegen Netzausbau).
  Abbruchpunkt deshalb nicht bei Funktionen, sondern bei der Breite: zuerst Wetter 2012 und
  2023, Szenarien 2030 und 2040, PV × 1; weitere Werte danach. Live-Rechnen vor
  Kosteneditor. [Vorschlag]

## 9. Abnahme [Owner: „nur plausibel“]

Die Bibliothek gilt, wenn sie die Tabellen von Session 18 (24.10.) in Größenordnung und
Tendenz trifft. Referenz Lastengpass, PV × 1, 257 Stationen (Stationen mit Engpass /
E_netto MWh):

| Wetter | heute | 2030 | 2040 |
|---|---|---|---|
| 2023 mild | 2 / 0,2 | 39 / 12 | 193 / 337 |
| 2017 | 4 / 0,4 | 52 / 28 | 200 / 1 057 |
| 2012 Kältewelle | 5 / 2,3 | 90 / 116 | 210 / 3 573 |

Einspeiseengpässe PV × 1 / × 1,5 / × 2: 1–3 / 19 / 31–34. V2G 2030 schwaches Segment
(250 kVA): ungesteuert 264 kW, 2 Engpass-h; gesteuertes Laden löst es. Abweichungen über
etwa ± 30 % oder umgekehrte Tendenz begründen (z. B. vektorisiertes E-Auto-Modell).

Ergebnisablage von Session 18: hetzner `/data/infra-kg-austria/work/steyr-pv-2026-10-24/
output-need-f-*`, `output-v2g-f-*`.

**Referenzkonfiguration** [Vorschlag]: Die Läufe `need-f-*` liefen als
`steyr_storage_need.py --scenario <s> --weather-year <j> --heat lod1 --district-heating`
(Prozessliste hetzner, 24.10. 11:15), also mit Default `--large-share 0,0`. Maßgeblich für
weitere Details ist der Block `annahmen` in `speicherbedarf_summary.json` je Ausgabeordner.
Vor Beginn friert der Builder die hetzner-Skripte als Kopie mit Prüfsumme ein und vermerkt
den Stand im Manifest. Ändert Session 18 sie später, gilt weiter die eingefrorene Kopie.

## 10. Dem Builder überlassen

Paket- und Modulnamen, Web-Framework des Backends, Stream-Technik,
Cache-Format, Numba ja/nein, genaue Gestaltung der Seite (Wireframe C als Richtschnur:
`.superpowers/brainstorm/…/content/demo-layout.html`), Tests im üblichen Umfang.

## 11. Offen

- Kosten je Trafo-Stufe und Leitung (Quelle fehlt).
- Port und Pfad der API mit Session 18 abstimmen; Einbettung (DOM-Anker, Modulname) mit
  Session 02.
