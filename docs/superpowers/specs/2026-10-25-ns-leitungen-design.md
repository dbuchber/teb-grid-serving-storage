# Design: Niederspannungsleitungen im Steyr-Modell (gridsim)

Stand 25.10.2026, Entwurf. Grundlage: [Recherche NS-Leitungen](../../research/2026-10-25-ns-leitungen-steyr.md).
„Owner“ = Auftraggeber dieses Projekts; „meine Entscheidung“ = vom Autor gesetzt, vom Owner noch nicht bestätigt.

## 1. Warum

Beim Pitch der TEB-Demo (Challenge Grid-Serving Storage) wandten Jury und Netzbetreiber ein: „Nicht nur die Trafos
haben ein Limit, auch die verlegten Leitungen.“ gridsim, das Modell hinter der Live-Demo, vergleicht je
Ortsnetzstation nur die Summe aller Gebäude mit der Trafo-Nennleistung. Leitungen kommen nicht vor.

Die älteren pandapower-Läufe (infra-kg `scripts/steyr_sim_variant_a.py`, `build_net_roads`) haben zwar Leitungen,
taugen aber nicht als Antwort: Schon im heutigen Winter sind dort bei 40–50 von 257 Stationen Kabel über 100 %
(bis 400–600 %) bei nur 6–11 Trafos. Ursache laut Recherche: Die Stränge sind etwa doppelt so lang wie real, und die
Querschnitte sind pauschal (Stadt NAYY 4x150, Land Al 95) statt nach Last bemessen.

**Erfolg:** gridsim kann für jede Station, jedes Wetterjahr und Szenario sagen, ob zuerst der Trafo oder ein
Leitungsabschnitt an die Grenze kommt, und ob ein netzdienlicher Speicher am Ort des Engpasses hilft. Der heutige
Zustand ist dabei plausibel (höchstens einzelne Abschnitte knapp über 100 %).

## 2. Ziele, Nicht-Ziele, Anti-Ziele

**Ziele**

1. Synthetisches NS-Netz je Station mit plausibler Struktur: Stranglängen, Abgangszahl und Kabelanteil im Bereich der
   Referenzwerte (Recherche Abschnitt 4–6).
2. Querschnitte je Leitungsabschnitt nach Planungsregeln bemessen (so wie reale Netze gebaut wurden).
3. Thermische Auslastung jedes Abschnitts für alle 8 760 Stunden und alle Seeds in gridsim, neben der Trafo-Auslastung.
4. Kennzahlen „Leitung vor Trafo“ je Station und Region; Kosten der Leitungsverstärkung neben Trafo und Speicher.
5. Wirkung von Speicher und Steuerung auf Leitungen: nur der Speicher hinter dem Engpass entlastet den Abschnitt.
6. **Steuerung kennt die Leitungsgrenzen** (Owner, 25.10.2026): gesteuertes Laden, V2G und Speicherabrufe halten
   Trafo **und** jeden Abschnitt ein (Abruf je Abgang).
7. **Netzdienlicher Speicher am Leitungsengpass** (Owner, 25.10.2026): neues Speichermodell an einem Abschnitt mit
   eigener Einsatzlogik und Bemessung, vergleichbar mit Leitungsverstärkung und Trafotausch.

**Nicht-Ziele**

- Keine belastbare Spannungsaussage. Spannung höchstens als grober Hinweis (siehe 4.4), klar gekennzeichnet.
- Keine echten Netzdaten; keine Leitungsauskunft des Netzbetreibers (Nutzungsbedingungen).
- Keine Änderung der bisherigen vorbereiteten Daten; Zusatzstationen nur in der neuen Variante (siehe 5.1).
- Kein Lastfluss mit pandapower im Live-Modell.

**Anti-Ziele (wäre ein Fehlschlag, auch wenn es technisch läuft)**

- Ein Ergebnis, das heute viele überlastete Leitungen zeigt. Das widerspricht realen Netzen und würde den
  Netzbetreiber in der Jury bestätigen, dass wir das Netz nicht verstehen.
- Querschnitte so nachjustiert, dass „heute“ passt, ohne nachvollziehbare Regel (Kurvenanpassung).
- Zahlen ohne Kennzeichnung synthetisch / angenommen auf der Demo-Seite.

## 3. Ausgangslage im Code

- **gridsim** (Repo `teb-grid-serving-storage`, Standard-Branch `feat/gridsim`):
  - `gridsim/prepare.py` ruft die eingefrorenen Skripte in `gridsim/legacy/` auf (`build_members` ohne Straßen,
    also Zuordnung Gebäude → nächste Station in Luftlinie ≤ 600 m) und schreibt Knoten-Arrays je Wetterjahr
    (`nodes_station`, `nodes_hh`, `nodes_kwp_bins`, …) und `stations.json` (u. a. `kva`).
  - `gridsim/run.py`: `flows()` liefert je Seed den Fluss **je Station** (ohne E-Auto, E-Auto-Last, Endfluss).
  - `gridsim/metrics.py`: Kennzahlen nach ems-konzept § 7.2 je Station, `trafo_steps`, Kosten.
  - `gridsim/legacy/` ist eingefroren (SHA256SUMS), darf nicht geändert werden.
- **Straßenführung** existiert nur in infra-kg (`scripts/steyr_lv_roads.py`, `build_net_roads` in
  `steyr_sim_variant_a.py`), Eingang `osm_roads.json` im Arbeitsordner auf hetzner.
- **Lastfluss-Ergebnisse** der alten Netze: hetzner `/data/infra-kg-austria/work/steyr-gutachten-2026-10-25/`.

## 4. Lösung

### 4.1 Gebietstyp je Station

Drei Typen nach Recherche Abschnitt 6, bestimmt aus dem mittleren Abstand jedes Wohngebäudes zu seinen vier
nächsten Nachbarn (Verfahren nach Lindner/Aigner und Gust):

| Typ | Kriterium (Startwerte, meine Entscheidung) | Kabelanteil NS | Grenze längster Strang |
|---|---|---|---|
| Stadt | Median-Nachbarabstand < 30 m | 100 % | 500 m |
| Ort | 30–80 m | 80 % | 700 m |
| Streusiedlung | > 80 m | 50 % (Rest Freileitung) | 1 000 m |

Ziel: Regionsmittel des Kabelanteils nahe 79 % (Netz OÖ 2025). Schwellen werden einmal gegen dieses Ziel kalibriert
und dann fest dokumentiert, nicht je Ergebnis nachgestellt.

### 4.2 Topologie

- Gebäude bleiben ihrer Station zugeordnet wie heute in gridsim (Luftlinie, `build_members`), damit Trafo-Ergebnisse
  unverändert bleiben.
- Leitungsweg entlang der Straßen (`steyr_lv_roads`), wie `build_net_roads`; ohne Straße im Umkreis Luftlinie.
- **Strangbegrenzung:** Abgänge werden an Abzweigen geteilt, bis jeder Abgang höchstens etwa 30 Gebäude hat und
  die Grenze aus 4.1 einhält; geteilte Abgänge liegen als eigene Kabel im selben Graben. Abgang mit Gebäude jenseits
  der Grenze, der sich nicht teilen lässt: markieren („bräuchte eigene Station“), nicht stillschweigend verlängern.
- Anlagen ab 30 kWp an eigenem Abgang (wie bisher, Beleg K1).
- **Prüfziele** (Regionswerte, in einem Bericht ausgegeben): NS-Leitung je Station im Mittel nahe 2,7 km
  (ohne Hausanschlüsse; Netz OÖ), 3,4–3,8 Abgänge je Station, Stranglängen Stadt meist 150–500 m, Land 200–500 m.
  Abweichungen werden berichtet und begründet, nicht weggerechnet.

### 4.3 Querschnitte nach Planungsregel

Je Abschnitt (vom Blatt zur Station) wird der kleinste Typ aus einer festen Liste gewählt, der zwei Bedingungen
im **Auslegungsfall „heute“** erfüllt:

1. Strom ≤ 100 % Grenzstrom bei der Auslegungslast;
2. Spannungsfall vom Trafo bis zum entferntesten Gebäude des Abgangs ≤ 5 %, vereinfacht mit R·P + X·Q
   (Verschiebungsfaktor 0,97).

Auslegungslast eines Abschnitts mit n nachgelagerten Haushalten: n · P_HH · g(n) mit
g(n) = g∞ + (1 − g∞)·n^(−3/4), g∞ = 0,07, P_HH-Spitze aus Arnold 2019 / Weisenstein 2022 (Startwert 2,0 kW je
Haushalt für große Kollektive, Faktor aus g(n) für kleine). Dazu bestehende PV (Einspeisefall, 3 % Anhebung) und
die Wärmepumpen und E-Autos des Szenarios **heute**. Größere Lasten künftiger Szenarien fließen bewusst nicht ein:
So entsteht das Netz, wie es heute gebaut wäre.

Typliste (Grenzströme aus Weisenstein 2022, Tab. 10; R/X aus pandapower-Standardtypen bzw. Herstellerdaten):
Kabel NAYY 4x50, 4x95, 4x150, 4x240; Freileitung Al 4x35, 4x70, 4x95 (Streusiedlung). Reicht 4x240 nicht: zwei
parallele 4x240; reicht auch das nicht, Abschnitt markieren. Hausanschlüsse: NAYY 4x35 (Kabel) bzw. Al 4x25.

### 4.4 Bewertung in gridsim

- **Neuer Vorbereitungsschritt** `gridsim prepare-feeders` (neues Modul, nicht in `legacy/`): baut je Station das
  Netz nach 4.1–4.3 und speichert je Station
  - die Abschnitte (Typ, Länge, Grenzstrom, Abgang, Geometrie für die Karte),
  - eine dünn besetzte Matrix „Abschnitt × Knoten“ (1, wenn der Knoten hinter dem Abschnitt liegt).
- **Lauf:** Aus den Knotenflüssen eines Seeds wird je Station Abschnittsfluss = Matrix · Knotenfluss (Stunde für
  Stunde, radial, ohne Verluste). Strom = |P| / (√3 · 400 V · cos φ) mit cos φ 0,97 bei Bezug, 1,0 bei Einspeisung.
  Dafür muss `flows()` die Knotenflüsse je Station in Blöcken liefern statt nur die Summe; Speicherbedarf beachten
  (Knoten × 8 760 Stunden nicht für alle Stationen gleichzeitig halten).
- **Kennzahlen je Station:** höchste Abschnittsauslastung, Überlaststunden je Abgang, Länge der überlasteten
  Abschnitte, „Engpass zuerst“: Trafo / Leitung / beide / keiner, je Richtung (Bezug, Einspeisung).
- **Region:** Anzahl Stationen mit Leitungsengpass neben der mit Trafoengpass, als Band über die Seeds wie bisher.
- **Spannung:** optional als Hinweis (linearer Spannungsfall je Abgang), nur in der Detailansicht, mit dem Vermerk
  „synthetisches Netz, nicht belastbar“. Nicht in Regionskennzahlen.

### 4.5 Steuerung mit Leitungsgrenzen

Heute arbeiten `control.controlled()`, `v2g_with_recharge()` und `engpass_signal()` nur auf der Stationssumme gegen
`kva`; Knotenflüsse nach der Steuerung gibt es nicht. Neu:

- **Grenzmodus** als Parameter in `RunParams`: `trafo` (heutiges Verhalten, Ergebnisse bitgleich) und
  `trafo+leitung` (neu). So bleiben alte Läufe reproduzierbar und beide Modi vergleichbar (meine Entscheidung).
- Im Modus `trafo+leitung` gilt je Stunde für jede gesteuerte Größe (Ladeleistung eines Autos, V2G-Entladung,
  Abrufleistung eines Speichers): Die Summe aller Knotenflüsse darf an keinem Abschnitt auf dem Weg zur Station und
  nicht am Trafo die Grenze überschreiten. Freier Raum je Abschnitt = Grenze − ungesteuerter Fluss; ein Knoten
  bekommt höchstens das Minimum des freien Raums aller Abschnitte auf seinem Weg. Verteilung unter mehreren Knoten
  hinter demselben Abschnitt anteilig nach Bedarf (meine Entscheidung; der Umsetzer darf ein gleichwertiges,
  dokumentiertes Verfahren wählen).
- Im Modus `trafo` werden die Stationsentscheidungen anteilig nach Bedarf auf die Knoten verteilt, damit auch dort
  Abschnittsflüsse entstehen.
- Was nicht geladen werden kann, geht wie heute in `unmet` (ungeladene Energie) ein, jetzt auch durch Leitungsgrenzen.
- Speicherabrufe (Heimspeicher, Strategien `forecast`/`room`) wirken im Modus `trafo+leitung` je Abgang: Ein
  Abschnittsengpass ruft nur die Speicher hinter diesem Abschnitt ab. Für das Interoperabilitätsprofil heißt das:
  Abruf je Abgang statt je Segment (P4/P9 sehen den Abgang als Ziel schon vor); der Profiltext wird nachgezogen.
- Zusätzliche Auswertung: Anteil der Leitungsüberlast, der hinter Knoten mit Heimspeicher liegt.

### 4.6 Netzspeicher am Leitungsengpass

Neues Element „Netzspeicher“ (vom Netzbetreiber, nicht vom Kunden):

- **Ort:** an dem Knoten unmittelbar hinter dem am stärksten überlasteten Abschnitt eines Abgangs (Ort mit der
  größten Wirkung für diesen und alle vorgelagerten Abschnitte). Je Abgang höchstens ein Netzspeicher.
- **Bemessung** wie ems-konzept § 7.2, aber auf den Abschnittsfluss statt auf den Trafofluss: Energie aus den
  Engpassereignissen des Abschnitts (Ereignisse mit < 8 h Abstand zusammengefasst), Leistung aus der höchsten
  Überlast; Bemessung im Auslegungslauf (siehe 5.2), dann fest für alle Seeds.
- **Einsatz:** mit perfekter Tagesprognose wie die Strategie `forecast`: lädt, wenn der Abschnitt bei Einspeisung über
  der Grenze liegt, entlädt, wenn er bei Bezug über der Grenze liegt; außerhalb von Engpässen Rückkehr auf einen
  mittleren Ladezustand, sodass beide Richtungen möglich bleiben. Wirkungsgrad wie die Heimspeicher (0,95 je Richtung).
- **Schalter** in `RunParams` (aus / an), damit Läufe mit und ohne Netzspeicher vergleichbar sind.
- **Kennzahlen:** Zahl und Größe der Netzspeicher, verbleibende Überlast, Vollzyklen; Kosten neben Leitungsverstärkung
  und Trafotausch (Kostensätze als Platzhalter, siehe 4.7).

### 4.7 Kosten

Leitungsverstärkung als Länge der überlasteten Abschnitte × Kostensatz je Meter (Kabeltausch inkl. Tiefbau,
Stadt / Land getrennt). Die Kostensätze sind Platzhalter, bis eine Quelle gefunden ist; `metrics.costs` meldet
Platzhalter wie bisher, statt mit ihnen zu rechnen.

### 4.8 Darstellung

- Dashboard: Stationsfarbe nach „Engpass zuerst“; Abgänge auf der Karte nach Auslastung eingefärbt (die
  NS-Geometrie gibt es schon als Kartenebene).
- Präsentation und Detailseite: ein Satz und eine Zahl „Leitungen vor Trafo“ je Szenario, mit Kennzeichnung
  synthetisch; Annahmen und Quellen auf der Detailseite. Text erst nach Abnahme der Zahlen.

## 5. Entscheidungen

1. **Zusatzstationen, wo Abgänge zu lang sind** (Owner, 25.10.2026; ersetzt „Stationen fest“). Erster Lauf auf
   echten Daten: 215 von 257 Stationen (84 %) mit zu langen oder nicht bemessbaren Abgängen, 7,1 Abgänge und
   4,0 km Trasse je Station (Ziel 3,4–3,8 und ca. 2,7 km). Ursache: zu wenige Stationen. Lösung: synthetische
   Zusatzstationen in den betroffenen Gebieten, gekennzeichnet wie die bisherigen synthetischen Stationen; Trafo
   nach derselben Regel wie die übrigen (`trafo_kva`). Das ergibt eine **neue Variante** der vorbereiteten Daten
   (`prepared-ns/`); die bisherige Variante und alle bisherigen Trafo-Ergebnisse bleiben unverändert erhalten.
   Trafo-Ergebnisse der neuen Variante unterscheiden sich und werden im Abnahmebericht gegenübergestellt.
2. **Nur thermisch bewerten**, Spannung nur als Hinweis (meine Entscheidung; Begründung: Winter-Lastfluss mit
   165 von 257 Stationen über 5 % heute).
3. **Auslegung nach „heute“** (meine Entscheidung): Querschnitte aus der heutigen Last, damit das Netz wie gebaut
   ist und künftige Engpässe sichtbar werden.
4. **Ohne pandapower im Lauf** (meine Entscheidung): radiale Summation ist für die thermische Frage ausreichend und
   schnell genug für 8 760 Stunden × 20 Seeds.

**Ergänzt nach der Umsetzer-Prüfung (alle meine Entscheidung):**

5. **Auslegungslast „heute“ ohne Zufallsbelegung, ein Netz für alle Wetterjahre.** Wärmepumpen und E-Autos gehen mit
   ihrem Erwartungswert ein (Anteil des Szenarios „heute“ × Knoten), nicht mit der Belegung eines Seeds. Die
   Wärmepumpenleistung wird bei der kältesten Stunde des Wetterjahrs **2012** (Kältewelle) angesetzt. Das Netz wird
   einmal gebaut und gilt für alle Wetterjahre und Seeds; so bleiben Jahre und Szenarien vergleichbar.
6. **Abnahmegrenze „heute“, festgelegt vor der Rechnung:** Szenario heute, PV-Faktor 1,0, Speicher `base`,
   ungesteuertes Laden, Grenzmodus `trafo`, alle drei Wetterjahre; über die 20 Seeds das P90 der höchsten
   Abschnittsauslastung je Station. Bestanden, wenn höchstens 5 von 257 Stationen über 100 % liegen und keine über
   120 %. Wird die Grenze verfehlt, wird die Bemessungsregel geprüft und begründet geändert, nicht die Grenze.
7. **Markierte Abgänge** („bräuchte eigene Station“) werden trotzdem mit dem stärksten zulässigen Typ (2 × 4x240)
   bemessen und bewertet; sie werden in allen Kennzahlen getrennt ausgewiesen. Sind mehr als 10 % der Stationen
   betroffen, legt der Umsetzer dem Owner Entscheidung 1 (Stationen fest) erneut vor, bevor er weiterbaut.
8. **Haushaltslast auf Abschnittsebene mit Spitzenzuschlag.** Das H0-Profil ist für große Kollektive geglättet und
   würde kleine Abschnitte unterschätzen. In der Bewertung wird die Haushaltslast je Abschnitt mit
   f(n) = g(n) · n · P_HH / (n · Spitze des H0-Profils) skaliert (n = Haushalte hinter dem Abschnitt), damit
   Bemessung und Bewertung dieselbe Spitze verwenden; die Form über den Tag bleibt die des H0-Profils. Der Trafo
   wird wie bisher ohne Zuschlag bewertet (Trafo-Kennzahlen bleiben identisch).
9. **„Engpass zuerst“** wird je Lauf als Zustand angegeben (Trafo / Leitung / beide / keiner, je Richtung). Welches
   Element in der Kette heute → 2030 → 2040 zuerst überlastet ist, wird im Abnahmebericht und auf der Detailseite
   aus mehreren Läufen abgeleitet; API und Dashboard bekommen dafür kein eigenes Feld.

## 6. Abnahme

- Tests für die Bemessung (kleines Beispielnetz mit bekannter Lösung), für die Matrix (Summe der Abgangsflüsse =
  Stationsfluss), für die Steuerung mit Leitungsgrenzen (kein Abschnitt über der Grenze, solange steuerbar), für den
  Netzspeicher (Energiebilanz, Ladezustand in Grenzen) und für die Kennzahlen; bestehende Tests bleiben grün.
- Im Grenzmodus `trafo` ohne Netzspeicher sind die Trafo-Kennzahlen bitgleich zur heutigen Version (gleiche Seeds,
  gleiche Eingaben).
- Plausibilitätsbericht `docs/gridsim-leitungen-abnahme.md`: Längen, Abgänge, Kabelanteil, Typverteilung gegen die
  Referenzwerte; Anteil markierter Abgänge; Abnahmegrenze „heute“ nach Entscheidung 6; Vergleich der Modi
  `trafo` / `trafo+leitung` und mit / ohne Netzspeicher für 2030 und 2040.
- Stichprobe: drei Stationen je Gebietstyp mit Karte und Abschnittstabelle, von Hand geprüft.
- Vergleich mit pandapower-Lastfluss für dieselben Stationen in einigen Stunden (Abweichung der Abschnittsauslastung
  berichten); nur zur Prüfung, nicht im Lauf.

## 7. Dem Umsetzer überlassen

Datenformat der Abschnitte, Blockgröße für den Speicher, genaue R/X-Werte je Typ (mit Quelle), Aufteilung in
Module, Wiederverwendung von `steyr_lv_roads` (Kopie nach gridsim mit Herkunftsvermerk oder Import), Reihenfolge
der Schritte. Rechnen auf hetzner, nicht am Mac.

## 8. Stand nach Umsetzung (26.10.2026)

Nachtrag nach dem Branch-Review von `feat/ns-leitungen`. Der Entwurf oben bleibt als historisches Dokument stehen;
maßgeblich für den umgesetzten Stand sind der Abnahmebericht [`docs/gridsim-leitungen-abnahme.md`](../../gridsim-leitungen-abnahme.md)
(abgenommener Stand `prepared-ns-fix4`, `MODEL_VERSION` 2026-10-26.5, Cache `cache-fix4`) und das Ledger des
Controllers (`.superpowers/sdd/2026-10-25-ns-leitungen/progress.md`). Abweichungen vom Entwurf:

- **4.1 Gebietsschwellen:** einmal kalibriert auf stadt < 35 m, ort 35–85 m, streu > 85 m (Startwerte 30/80 m
  ergaben 68,6 % Kabel; +5 m ist die kleinste Verschiebung ins Band 74–84 %), danach fest. Kabelanteil nach
  Trassenlänge im Endstand 74,4 % (Kalibrierlauf 75,3 %). Kabelanteile je Typ und Stranggrenzen wie im Entwurf.
- **4.2 Prüfziele:** 4,61 Abgänge und 2,22 km Trasse je Station statt 3,4–3,8 und ca. 2,7 km; im Bericht
  ausgewiesen, Zielwerte gelten als Orientierung (Ruling). Ausläufer mit weniger als 6 Wohngebäuden bekommen keine
  Zusatzstation und zählen nicht zur 10-%-Grenze; Direktabgang ab mehr als 30 kWp.
- **4.3 Typliste:** umgesetzt sind Kabel NAYY 4x50, 4x150, 4x240 und Freileitung Al 4x70, Al 4x95 (Grenzströme
  Weisenstein et al. 2022, Tab. 10, wie in den Global Constraints). **NAYY 4x95 und Al 4x35 aus der Liste oben gibt
  es nicht**, weil die Quelle für sie keinen Grenzstrom nennt. Hausanschlüsse NAYY 4x35 bzw. Al 4x25 werden nicht
  bemessen, aber bewertet. Seit Fix-Runde 2 Mindestquerschnitt im Strang in stadt/ort: NAYY 4x150 bzw. Al 4x95
  (Owner „Ist-Abgleich“; übliche Praxis, kein Steyr-Beleg).
- **4.3 / Entscheidung 5 Auslegungslast:** nicht mehr Erwartungswert und nicht n · P_HH · g(n), sondern (Rulings
  Fix-Runden 1 und 3): Haushalte n · max(P_HH · g(n), H0-Spitze); Wärmepumpen die k größten vollen Leistungen
  mit k = P90 Binomial(m, p_wp); E-Autos k · p_ev(k) mit k = P90 Binomial(n, ev_share). Auslegungsjahr 2012,
  ein Netz für alle Wetterjahre bleibt. Grund: Mit Erwartungswerten verfehlte das Netz die Abnahmegrenze „heute“.
- **Szenario „heute“** nutzt seit Fix-Runde 2 Ist-Anteile für Oberösterreich (WP 0,23 je berechtigtem Gebäude,
  E-Autos 0,076 je Haushalt, Owner „Ist-Abgleich“); die Trafo-Kennzahlen „heute“ sind damit nicht mehr bitgleich zur
  Pitch-Fassung, alle anderen Szenarien schon.
- **Entscheidung 1 (Zusatzstationen):** umgesetzt als eigene Variante; Endstand `prepared-ns-fix4` mit 432
  Stationen (257 + 175). Die Pitch-Fassung mit 257 Trafos bleibt unverändert und wird neben dem Leitungsnachtrag
  gezeigt (Owner: „beide Netze nebeneinander“, Leitungsteil als „Nachtrag nach dem Pitch“ gekennzeichnet).
- **Entscheidung 6 (Abnahmegrenze):** „höchstens 5 von 257“ gilt als „höchstens 5 Stationen der Variante“, gleich
  wie viele Stationen sie hat (Controller: 5 von 465 im ersten Lauf, 5 von 487 in Fix-Runde 1, im Endstand 5 von 432), dazu 20 Seeds je
  Wetterjahr. Bestanden auf `prepared-ns-fix4`: 0 Stationen über 100 %, Maximum 88,9 %.
- **Entscheidung 7 (markierte Abgänge):** Abgänge, die nur am Spannungsfall scheitern, zählen nicht zur 10-%-Grenze
  (Owner, Fix-Runde 4; Spannung wird nach Entscheidung 2 nicht bewertet), werden aber getrennt berichtet
  (122 Abgänge an 93 Stationen). Markiert im Endstand: 41 von 432 Stationen (9,5 %).
- **4.4 Spannung als Hinweis in der Detailansicht:** nicht umgesetzt (im Entwurf optional).
- **4.5 Steuerung:** Grenzmodus `trafo` / `trafo+leitung` wie geplant. **Heimspeicher werden nicht abgerufen**
  (Ruling: gridsim hat keine Abruflogik für Heimspeicher), Abrufe je Abgang macht nur der Netzspeicher.
  V2G-Nachladen ist im Leitungsmodus je Knoten begrenzt. **Die Auswertung „Anteil der Leitungsüberlast hinter
  Knoten mit Heimspeicher“ ist nicht umgesetzt** und steht als offene Abweichung im Abnahmebericht; sie wäre
  unabhängig von den Abrufen möglich, bräuchte aber eine Neurechnung.
- **4.6 Netzspeicher:** wie geplant, aber vor der E-Auto-Steuerung eingesetzt; er sieht bei gesteuertem Laden nur den
  Grundfluss. An Tagen ohne Engpass fährt er auf den Startwert desselben Tages (bereitet einen Engpass früh am
  Folgetag nicht vor).
- **4.7 Kosten:** ein einziger Platzhalter `line_eur_per_m` (keine getrennten Sätze Stadt/Land), solange ohne
  Quelle nicht gerechnet. Netzspeicher werden mit dem Heimspeicher-Satz `storage_eur_per_kwh` (600 €/kWh) bewertet.
- **Szenario 2040r** (50 % Wärmepumpen, 0,60 E-Autos) ist nach Owner-Entscheidung das Hauptergebnis 2040 für die
  Leitungen; 2040 (70 %) heißt dort Stresstest.
- **„Engpass zuerst“** vergleicht den Trafo mit cos φ 1,0 (kW/kVA, bitgleich) und die Leitung mit cos φ 0,97;
  Grenzfälle fallen dadurch eher in die Klasse „Leitung“ (im Bericht unter „Grenzen der Aussage“).
- **Dashboard-Tagesansicht** rechnet weiter nur mit Trafo-Grenze und ohne Netzspeicher und sagt das bei Läufen mit
  Leitungsgrenzen oder Netzspeicher (Ruling, finales Review).
