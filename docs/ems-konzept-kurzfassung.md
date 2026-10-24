# EMS-Konzept Grid-Serving Storage (Kurzfassung)

Stand: 24.10.2026 · Online-Doc: https://claude.ai/artifact/K3vL6DYdzFtVMxTKS473PT ·
Ausführliche Fassung: [ems-konzept.md](ems-konzept.md)

Die Box steuert den Heimspeicher für den Haushalt und gibt ihn dem Netzbetreiber nur in Engpässen frei; der Kunde verliert dabei nie Geld, und mehr Steuerbarkeit bringt mehr Förderung. Werte mit „Beispiel“ oder „Platzhalter“ sind noch nicht festgelegt.

## Festgelegt

Zwölf Grundsatzentscheidungen des Owners (23.–24.10.2026) tragen das Konzept.

1. Die Box ist zugleich EMS für den Haushalt.
2. Home Assistant ist nur über einen eigenen Kanal angebunden, ohne Weg zum Kernmodul oder Netzbetreiberkanal.
3. Der Nutzer setzt bestimmte Parameter selbst; das System darf bestimmte Parameter überschreiben.
4. Preise kommen signiert über die Box, nicht über Home Assistant.
5. Den täglichen Preisvektor signiert eine gemeinsame Preisstelle für alle Lieferanten, betrieben von der E-Control, als eigene PKI-Rolle.
6. Die Förderung deckt auch die Installation der Box.
7. Die Förderhöhe steigt mit der zugelassenen Steuerbarkeit; voll ausgezahlt wird erst bei möglichst viel Steuerbarkeit.
8. Solange Einspeisung aus dem Speicher nicht freigeschaltet ist, ist die höchste Stufe auch ohne Entladen ins Netz erreichbar.
9. Die geschützte Notstrom-Reserve wird aus Verbrauchsdaten bemessen und nach einem Jahr nachgeschärft.
10. Die Wärmepumpe zählt nicht zur geschützten Grundreserve.
11. Der Kunde wird durch Eingriffe des Netzbetreibers nie schlechter gestellt.
12. Der tatsächliche Speicherbedarf je Segment wird ermittelt, unter Berücksichtigung der Degradation.

## Parameter und Vorrang

Der Nutzer stellt acht Parameter ein; sechs Quellen dürfen sie zeitlich begrenzt überschreiben, die Notstrom-Reserve N3 nie.

Vorrang im Kernmodul:

1. Sicherheit und Fallback
2. Signierter Abruf des Netzbetreibers
3. Mindestreserve für Abrufe
4. Parameter des Nutzers
5. Eigenverbrauchsoptimierung

| ID | Nutzerparameter | Beispiel | Grenze im Kernmodul |
| --- | --- | --- | --- |
| N1 | Ladepreis-Schwelle: aus dem Netz laden, wenn Bezugspreis darunter | 8 ct/kWh | nur mit N5 = ja |
| N2 | Einspeisepreis-Schwelle: ins Netz entladen, wenn Einspeisepreis darüber | 25 ct/kWh | nur mit N6 = ja |
| N3 | Notstrom-Reserve | 2 kWh | künftig in kWh, siehe Förderung |
| N4 | Max. Lade-/Entladeleistung | 5 kW | ≤ Gerätegrenze |
| N5 | Laden aus dem Netz erlaubt | ja/nein | – |
| N6 | Entladen ins Netz (Arbitrage) erlaubt | ja/nein | – |
| N7 | Mindest-Spread für Arbitrage | 8 ct/kWh | deckt Wirkungsgrad und Verschleiß |
| N8 | Teilnahme an vergüteten Entlade-Abrufen | ja/nein | freiwillig |

| Quelle | Darf überschreiben | Dauer |
| --- | --- | --- |
| S1 Sicherheit (BMS, Temperatur) | alles | solange der Zustand anhält |
| S2 Signierter Abruf des VNB | N1, N2, N4–N7; Entladen ins Netz nur mit N8 | Abrufdauer, max. 4 h (Beispiel) |
| S3 Vorhaltung (Ankündigung am Vortag) | N1, N5 | angekündigtes Fenster |
| S4 Testabruf | N1, N2, N4–N7 | max. 15 min, 1× pro Monat (Beispiel) |
| S5 Staffelung im Segment | N4 | einzelne Viertelstunden |
| S6 Keine gültigen Preise | N1, N2, N6 pausieren | bis gültige Preise vorliegen |

Jede Überschreibung erscheint in Home Assistant mit Quelle, Grund, Beginn und Ende; danach gelten wieder die Nutzerwerte.

## Szenarien

Zehn Szenarien zeigen, wann das System eingreift und was der Nutzer sieht.

| Szenario | Lage | Was das System tut |
| --- | --- | --- |
| A Billiger Nachttarif | 40 Speicher laden gleichzeitig; im SimBench-Test steigt die Leitungsauslastung von 34 % auf 90 % (vorläufig) | Staffelung S5: geringere Ladeleistung, versetzte Starts; Speicher trotzdem voll |
| B Sonniger Mittag | Einspeiseengpass 11–14 Uhr erwartet | Vorhaltung S3: nachts nur bis 40 % laden, mittags PV-Überschuss aufnehmen |
| C Abendspitze | Lastengpass 18 Uhr, Nutzer will Notstrom behalten | Entladen bis zur Reserve N3, dann Stopp; ohne N8 nur Eigenversorgung aus dem Speicher |
| D Testabruf | monatlich, 15 min | Box folgt dem Sollwert; Smart Meter und eigene Messung bewerten Reaktion |
| E Preise fehlen | Preisvektor bis 18 Uhr nicht angekommen | Arbitrage pausiert, nur Eigenverbrauch |
| F Manipulierter Preis | Angreifer meldet −50 ct über Home Assistant | wirkungslos, Preise nur signiert über die Box |
| G Negative Preise | Speicher voll, PV erzeugt weiter | Einspeisung begrenzen, wenn der Einspeisetarif null oder negativ ist |
| H Unplausible Werte | Nutzer setzt 15 kW bei 5-kW-Gerät | Kernmodul begrenzt und meldet den Wert zurück |
| I Teurer Nachkauf | Abruf entlädt 5 kWh, Haushalt kauft abends zu 32 ct nach | Ersatz 1,25 € plus Vergütung 1,00 € (Beispiel) |
| J Entgangener Verkauf | Vorhaltung verhindert Arbitrage 6 → 28 ct | Ersatz 0,59 € plus Vorhaltevergütung (Beispiel) |

## Tarife: signiert über die Box

Die Box berechnet den Preis aus signierten Teilen; nur ein Dokument (der Preisvektor) geht täglich an alle Boxen.

```latex
\begin{aligned}
\text{Bezugspreis}(t) &= a \cdot \text{Spot}(t) + b + \text{Netzentgelt}(t) + \text{Abgaben} \\
\text{Einspeisepreis}(t) &= c \cdot \text{Spot}(t) + d
\end{aligned}
```

Bei Fixpreis ist a = 0; für negative Preise gilt eine eigene Regel.

| Dokument | Signiert von | Inhalt | Übertragung |
| --- | --- | --- | --- |
| T1 Tarifformel Bezug | Lieferant | Typ, a, b, Zeitfenster, Gültigkeit | bei Vertragsänderung, an einen Kunden |
| T2 Tarifformel Einspeisung | Abnahmestelle | Typ, c, d, Regel bei negativem Preis | wie T1 |
| T3 Netzentgelt-Tabelle | VNB des Anschlusses | Zeitfenster, Preise je Netzebene | selten, Multicast je Netzbereich |
| T4 Preisvektor | Preisstelle der E-Control | 96 Viertelstundenwerte für morgen | täglich nach der Day-Ahead-Auktion, Multicast an alle |
| T5 Abgaben/Steuern | Lieferant | fixe Bestandteile | selten |

- **Größe:** T4 umfasst ca. 180 Byte inklusive Signatur und passt fragmentiert in LoRaWAN-Multicast.
- **Prüfung:** Jede Rolle darf nur ihre Dokumente signieren; Gültigkeit und Sequenznummer verhindern alte Preise; Werte außerhalb von −50 bis +100 ct/kWh werden verworfen.
- **Demo-Region Steyr:** Zwei VNB (Netz OÖ und vermutlich ein lokaler VNB); jede Box nimmt T3 nur von ihrem eigenen VNB laut Verbauliste.

### Dynamisches Netzentgelt je Segment (T3d)

Österreich bekommt ab 2027 zeitvariable, aber statische Netzentgelte: SNAP (Sommer, 10–16 Uhr, ca. −20 %), WiNAP (Winter, 23–5 Uhr, ab Oktober 2027), Leistungspreis nach der höchsten Viertelstunde im Monat und die flexible Entnahme nach § 10 SNE-G-V. Ein Netzentgelt nach dem Zustand eines Segments ist nicht vorgesehen; nur Deutschland hat dazu ein Pilotprojekt.

- **Problem:** Feste Fenster lassen alle gleichzeitig starten, wie der Rebound nach den DE-Sperrzeiten (plus 25–33 % Abendspitze). Der Leistungspreis wirkt auf den Haushalt, nicht auf das Segment.
- **Vorschlag:** Der VNB signiert an Tagen mit Engpassprognose ein Segmentsignal T3d je Ortsnetzstation: 96 Viertelstundenwerte, nur Rabatt, ca. 180 Byte wie T4.
- **Wirkung:** Mittags Rabatt bei Einspeiseengpass; nachts gestaffelte Rabattfenster bei Lastengpass, damit der Ladebeginn sich verteilt.
- **Reihenfolge:** Erst das freiwillige Signal (ohne Schadlosstellung), dann signierte Abrufe mit Schadlosstellung, wenn die Prognose weiter einen Engpass zeigt.
- **Offen:** Rechtlich wohl nur als Flexibilitätsvergütung (§ 139) oder Abschlag (§ 128) möglich; Abrechnung braucht Viertelstundenwerte, die die Box-Messung liefert.

## Förderung nach Steuerbarkeit

Volle Förderung gibt es nur in Stufe 3; ausgezahlt wird zur Hälfte bei Inbetriebnahme, der Rest nach gemessener Netzdienlichkeit.

| Stufe | Was der Kunde zulässt | Förderung (Platzhalter) |
| --- | --- | --- |
| 0 | keine Steuerschnittstelle | 40 %, Box nicht gefördert |
| 1 | steuerbar nur in Laderichtung, Testabrufe | 60 % |
| 2 | steuerbar in beide Richtungen, Testabrufe | 80 % |
| 3 | Stufe 2 plus Entladen ins Netz (N8) und Vorhaltung (S3); bis zur Freischaltung der Einspeisung ohne N8 | 100 % |

- **Box samt Installation:** ab Stufe 1 voll gefördert.
- **Auszahlung:** 50 % nach dem ersten erfolgreichen Testabruf; Rest in Jahrestranchen (z. B. 5 Jahre) nach Erreichbarkeit, Zuverlässigkeit in Testabrufen und Stufe im Jahresmittel.
- **Nachweis:** Die Box erstellt ihn signiert aus eigener Messung; der VNB leitet ihn an die Förderstelle.
- **Stufe senken:** jederzeit möglich; künftige Tranchen sinken, Ausgezahltes wird nicht zurückgefordert.

### Notstrom-Reserve

Eine geschützte Grundreserve zählt nicht gegen die Stufe; nur Reserve darüber verringert die freigegebene Kapazität.

- **Einheit:** kWh statt Prozent, weil 20 % bei 5 kWh nur 1 kWh sind, bei 15 kWh aber 3 kWh.
- **Nur bei notstromfähiger Anlage;** sonst gilt das technische Minimum des BMS.
- **Bemessung:** Bestand aus Smart-Meter-Daten (Grundlast im Winter × 24 h), Neubau aus Erfahrungswerten, nach 12 Monaten aus der eigenen Messung der Box nachgeschärft. In Österreich haben 96,9 % der Zählpunkte ein Smart Meter, aber nur 12,6 % übertragen Viertelstundenwerte (Ende 2024).
- **Wärmepumpe** zählt nicht zur Grundreserve.
- **Deckel:** höchstens 30 % der Nutzkapazität (Platzhalter); Stufe 3 ab 80 % freigegebener Kapazität, Stufe 2 ab 60 % (Platzhalter).
- Die Reserve ist **nie überschreibbar**, auch nicht im Krisenfall.

## Schadlosstellung

Nach jedem Eingriff ersetzt der VNB den Nachteil gegenüber einer Referenz ohne Eingriff und zahlt zusätzlich eine Vergütung; der Kunde steht netto nie im Minus.

```latex
\text{Ersatz} = \max\bigl(0,\ \Delta\text{Bezugskosten} - \Delta\text{Einspeiseerlös}\bigr) + \text{Verschleißpauschale} \cdot \Delta E
```

1. **Referenz:** Der signierte, deterministische EMS-Algorithmus rechnet nach, was er ohne Eingriff getan hätte, mit tatsächlicher PV und Last, signierten Preisen und Nutzerparametern. Der VNB kann die Rechnung nachvollziehen.
2. **Ist:** signierte eigene Messung von Bezug und Einspeisung.
3. **Zeitraum:** vom Eingriff, bis der Speicher wieder dem Referenzverlauf folgt, höchstens 48 h.
4. **Vergütung** für Abruf bzw. Vorhaltung kommt immer dazu.
5. **Abrechnung:** monatlich als Gutschrift auf der Netzrechnung; die Kosten sind als Flex-Kosten in den Netzentgelten anerkennbar (§ 139 Abs. 4 ElWG).
6. **Anzeige:** pro Eingriff Zeitraum, Grund, Mehrkosten, Ersatz und Vergütung.

**Missbrauch:** Für die Referenz gelten die Parameter von 24 h vor dem Eingriff. Testabrufe werden genauso abgerechnet. Fixpreis-Kunden bekommen den Nachkauf zum Fixpreis abzüglich Einspeiseerlös plus Pauschale.

## Speicherbedarf und Degradation

Je Segment muss etwa das Dreifache des Netto-Bedarfs installiert sein; zusätzliche Netzabrufe kosten den Speicher wenig, weil Heimspeicher vor allem mit der Zeit altern.

### Bedarf je Segment

1. **Überlast** je Viertelstunde aus der Simulation (SimBench, Steyr), getrennt für Last- und Einspeiseengpass.
2. **Je Ereignis** Energie und Spitzenleistung der Überlast.
3. **Netto-Bedarf** = größtes Ereignis im Jahr; Ereignisse ohne Pause zum Nachladen zusammengerechnet. Bei ca. 5 kW je Gerät kann die Leistung die engere Grenze sein.
4. **Installiert** = Netto-Bedarf / (Verfügbarkeit 0,6 × Zuverlässigkeit 0,85 × freigegebener Anteil 0,8 × Restkapazität am Lebensende 0,8) ≈ Netto-Bedarf / 0,33 (Platzhalter; Flex+ lieferte 79 % der geforderten Leistung).
5. **Ergebnis** je Segment: Engpass-Stunden pro Jahr, Netto- und installierter Bedarf, Anzahl Speicher; direkt vergleichbar mit dem Netzausbau.

### Ergebnisse

Heute hat Steyr praktisch keinen Engpass (1–3 von 257 Ortsnetzstationen); bei mehr PV entstehen Einspeiseengpässe, die Heimspeicher allein nicht lösen. Stationszahlen nach gridsim (24.10.), übrige Spalten aus der früheren Einzelrechnung.

| Steyr, PV-Stand | Stationen mit Engpass | Engpass-h/a (Median) | E_inst Summe | Speicher à 10 kWh (Summe) | Netz-Vollzyklen/a (Median) | Trafo-Verstärkungen ohne Speicher |
| --- | --- | --- | --- | --- | --- | --- |
| heute | 3 | 21 | 0,45 MWh | 46 | 1,2 | 2 |
| PV × 1,5 | 19 | 285 | 39,2 MWh | 3.933 | 7,9 | 21 |
| PV × 2 | 34 | 674 | 128,2 MWh | 12.839 | 17,4 | 31 |

- **Energie begrenzt, nicht Leistung:** Mittagsspitzen dauern Stunden (Steyr und SimBench).
- **Engpässe kommen über die Spannung:** In SimBench begrenzt der Spannungsanstieg (≤ 3 %) vor dem Trafo; in Steyr sind es PV-lastige Stationen mit Gewerbe- und Agrar-PV (30–250 kWp).
- **Heimspeicher allein reichen nicht:** SimBench-EFH-Netz semiurb4 braucht bei Faktor 3 146 Speicher für 41 Anschlüsse. Nötig ist eine Kombination aus Speicher, Kappung am Netzanschlusspunkt, Gewerbespeichern und gezieltem Ausbau.
- **Degradation klein:** 0,3–19 Netz-Vollzyklen pro Jahr gegenüber 190–240 PV-Zyklen.
- **Lastengpässe** (Wärmepumpe, E-Auto) gibt es in SimBench ohne die deutschen Sperrzeiten bis Faktor 4 gar nicht; die wenigen dort entstehen nur durch den Rebound nach der Sperre (+25–33 % Abendspitze); in Steyr kommen sie mit Wärmepumpen und E-Autos früher (Tabelle unten).

Lastengpass am Winterabend in Steyr (gridsim, 20 Zufallsläufe je Einstellung, Median und Band 10–90 %, ungesteuertes Laden, ohne Sperrzeiten, INCA-Temperatur je Station):

| Wetterjahr | Stationen mit Engpass heute / 2030 / 2040 | Speicher à 10 kWh nötig 2030 / 2040 |
| --- | --- | --- |
| 2023 | 1 / 44 (39–49) / 193 (190–197) | 2.765 / 108.609 |
| 2017 | 2 / 56 (50–63) / 199 (195–202) | 3.885 / 342.085 |
| 2012 (Kältewelle, −20,6 °C) | 4 / 100 (95–104) / 208 (206–210) | 19.815 / 1,15 Mio. |

Steuerlogiken im Vergleich (Stationen mit Lastengpass von 257, Median über 20 Zufallsläufe):

| Fall | ungesteuert | WiNAP ab 23 Uhr | T3d je Segment | gesteuertes Laden | gesteuert + V2G |
| --- | --- | --- | --- | --- | --- |
| mild (2023), 2030 | 44 | 80 | 13 | 7 | 0 |
| Kältewelle (2012), 2030 | 100 | 141 | 56 | 30 | 8 |
| mild (2023), 2040 | 193 | 216 | 176 | 103 | 19 |
| Kältewelle (2012), 2040 | 208 | 222 | 201 | 166 | 103 |

- **Feste Fenster schaden:** WiNAP ab 23 Uhr verdoppelt 2030 fast die Zahl der überlasteten Trafos (44 → 80).
- **T3d wirkt ohne Eingriff:** Das gestaffelte Segmentsignal senkt sie 2030 auf 13 bzw. 56, freiwillig und ohne Schadlosstellung.
- **2040 reicht Steuerung nicht:** Der Winterengpass kommt aus der Wärmepumpe; selbst mit gesteuertem Laden und V2G bleiben bei Kälte 103 Stationen, dort hilft nur Netzausbau. Gesteuertes Laden lässt 2012/2040 rund 1,7 GWh E-Auto-Energie bis 7 Uhr ungeladen.
- **Einzelwerte schwanken stark:** Die frühere Einzelrechnung (2012/2030: 116 MWh Engpass-Energie) lag am oberen Rand; das Band über 20 Zufallsläufe ist 51–93 MWh ([Abnahme](gridsim-abnahme.md)).

### V2G-Demo: drei Lösungen am Winterabend

Gesteuertes Laden löst den Lastengpass fast immer allein; V2G ist die Reserve für Gleichzeitigkeit und Kältewellen.

| Fall (Wetterjahr 2012) | Trafo-Auslastung | Gesteuertes Laden | V2G-Autos nötig |
| --- | --- | --- | --- |
| 2030 schwaches Segment (250 kVA, ländlich), ungesteuert | 0,80 | kein Engpass | – |
| 2030 schwaches Segment, alle laden um 18 Uhr | 1,21 | 5 Wallboxen pausiert, löst | 7 von 19 |
| 2030 typische Station (400 kVA, Stadt), alle um 18 Uhr | 1,64 | 24 Wallboxen pausiert, löst | 34 von 50 |
| 2040 schwaches Segment, ungesteuert | 1,57 | 13 Wallboxen gedrosselt, löst | 40 von 69 |
| 2040 schwaches Segment, alle um 18 Uhr | 3,40 | löst nicht ganz: ca. 5 kWh je Auto ungeladen | 82 von 69: mehr als vorhanden |
| 2040 typische Station, ungesteuert | 1,37 | 14 Wallboxen, löst | 32 von 105 |
| 2040 typische Station, alle um 18 Uhr | 3,11 | 77 Wallboxen, löst | 110 von 105: mehr als vorhanden |

- **Ohne Sperrzeiten kommt der Lastengpass erst 2040** oder durch Gleichzeitigkeit; das deckt sich mit SimBench.
- **Reihenfolge der Eingriffe:** Wallbox drosseln → Heimspeicher → V2G; bei angekündigter Kälte Ziel-SoC am Vortag.
- **Annahmen:** V2G 11 kW und 15 kWh je Abend, 70 % der Autos angesteckt; gesteuertes Laden holt bis 7 Uhr nach.

Modellwerte (Session infra-kg-austria-18): Steyr stündlich, Netz und Trafo-Größen synthetisch (mindestens 2 kVA je Haushalt), reale OSM-Stationen in der V2G-Demo; SimBench Szenario 2, 15 min, Jahr 2016. Details: [ems-konzept.md](ems-konzept.md) § 7.2.

### Degradation

| Kennzahl | Wert | Quelle |
| --- | --- | --- |
| Zyklenfestigkeit LFP bis 80 % | 6.000–10.000 Vollzyklen | [42watt](https://42watt.de/magazin/lebensdauer-stromspeicher) (Herstellerangaben) |
| Vollzyklen im PV-Betrieb | 190–240 pro Jahr (> 3.000 Anlagen) | [42watt](https://42watt.de/magazin/lebensdauer-stromspeicher) |
| Kapazitätsverlust im Feld | 2–3 Prozentpunkte pro Jahr | [Figgener et al., Nature Energy 2024](https://www.ess-news.com/2024/09/18/most-home-battery-storage-systems-meet-warranty-claims-new-research-finds/) |

- **Zyklenreserve:** 15 Jahre × 240 Zyklen = 3.600, deutlich unter 6.000; Netzabrufe (geschätzt 10–50 Vollzyklen pro Jahr) nutzen vor allem diese Reserve.
- **Verschleißpauschale:** Obergrenze 600 €/kWh / (6.000 × 0,9) ≈ 11 ct/kWh; Vorschlag 5 ct/kWh, später aus gemessenen SoH-Verläufen nachschärfen.
- **Ladezustand:** Langer hoher SoC beschleunigt die Alterung; Vorhaltung (teilweise leer) schont, ein hoher Winter-Ziel-SoC belastet.
- **Betrieb:** Die Box meldet den SoH; Testabrufe messen die lieferbare Energie. Beides steuert, welche Speicher abgerufen werden.

## Offene Punkte

- [ ] Preisstelle bei der E-Control: Rechtsgrundlage und Lizenz der EPEX-Spotdaten
- [ ] Höhe der Vergütung für Abruf und Vorhaltung
- [ ] Förderstelle und Rechtsgrundlage für gestufte Förderung mit Tranchen; Prozentsätze festlegen
- [ ] Verschleißpauschale festlegen (Vorschlag 5 ct/kWh)
- [ ] Bedarfsrechnung mit den SimBench-Segmenten der Demo-Region
- [ ] Maximale Dauer und Häufigkeit von Abrufen und Testabrufen mit Smart Grids Austria
- [ ] Notstrom-Reserve: Größe der Grundreserve, Deckel, Stufen-Schwellen
- [ ] Segmentsignal T3d: Rechtsgrundlage, Höhe des Rabatts, Demo-Rechnung WiNAP gegen gestaffelt

## Quellen

- [E-Control: Smart-Meter-Monitoringbericht](https://www.e-control.at/smart-meter-monitoringbericht-2024); Zahlen Ende 2024 laut [ORF](https://orf.at/stories/3412054/)
- [42watt: Lebensdauer Stromspeicher](https://42watt.de/magazin/lebensdauer-stromspeicher)
- [ess-news: Figgener et al., Feldstudie Heimspeicher](https://www.ess-news.com/2024/09/18/most-home-battery-storage-systems-meet-warranty-claims-new-research-finds/)
- [AIT: Flex+ Endbericht](https://www.ait.ac.at/fileadmin/user_upload/20220729_Publizierbarer_Endbericht_Final.pdf)
- [E-Control: Neue Regeln für die Energiewende](https://www.ots.at/presseaussendung/OTS_20261012_OTS0085/e-control-neue-regeln-fuer-die-energiewende); [i-magazin: Netzentgelte-Reform 2027](https://i-magazin.com/e-control-netzentgelte-reform-2027/)
- [TenneT: Pilotprojekt dynamische Netzentgelte](https://www.tennet.eu/de/news/pilotprojekt-zeigt-dynamische-netzentgelte-entlasten-stromnetze-und-reduzieren-kosten-fuer-endkundinnen)
- Rechtsgrundlagen (ElWG, SNE-G-V, TOR Typ A) und Pilotprojekte: [research/](research/)
