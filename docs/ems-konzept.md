# EMS-Konzept: Nutzerparameter, Überschreibungen und signierte Tarife

Stand: 23.10.2026. **[E]** = vom Team festgelegt, **[V]** = Vorschlag,
**[O]** = offen. Ergänzt [anforderungen.md](anforderungen.md) § 3 und
[hardware-konzept.md](hardware-konzept.md).

## 1. Festgelegt [E]

- Die Box ist zugleich EMS für den Haushalt und über ein eigenes
  Kommunikationsmodul in Home Assistant integrierbar.
- Der Nutzer setzt bestimmte Parameter selbst; das System darf bestimmte
  Parameter überschreiben.
- **Preise kommen signiert über die Box**, nicht über Home Assistant.
- Den täglichen **Preisvektor T4 signiert eine gemeinsame Stelle** für alle
  Lieferanten (Owner, 23.10.2026); ein Multicast pro Tag für alle Boxen.
- Die Preisstelle betreibt die **E-Control** (Owner, 24.10.2026).

## 2. Parameter [V]

### 2.1 Vom Nutzer gesetzt (über Home Assistant)

| ID | Parameter | Beispiel | Grenzen im Kernmodul |
|---|---|---|---|
| N1 | Ladepreis-Schwelle: aus dem Netz laden, wenn Bezugspreis darunter | 8 ct/kWh | nur wirksam, wenn N5 = ja |
| N2 | Einspeisepreis-Schwelle: entladen ins Netz, wenn Einspeisepreis darüber | 25 ct/kWh | nur wirksam, wenn N6 = ja |
| N3 | Notstrom-Reserve (SoC, den der Haushalt immer behält) | 20 % | 0–50 % |
| N4 | Max. Lade-/Entladeleistung aus Sicht des Nutzers | 5 kW | ≤ Gerätegrenze |
| N5 | Laden aus dem Netz erlaubt | ja/nein | – |
| N6 | Entladen ins Netz (Arbitrage) erlaubt | ja/nein | – |
| N7 | Mindest-Spread: Arbitrage nur, wenn Einspeise- minus Bezugspreis mindestens so groß ist | 8 ct/kWh | deckt Wirkungsgrad und Verschleiß |
| N8 | Teilnahme an vergüteten Entlade-Abrufen des VNB | ja/nein | freiwillig (Entladen bleibt freiwillig, siehe anforderungen.md) |

### 2.2 Vom System überschreibbar

| Quelle | Darf überschreiben | Darf **nicht** überschreiben | Dauer |
|---|---|---|---|
| S1 Sicherheit (BMS, Temperatur, Gerätegrenzen) | alles | – | solange der Zustand anhält |
| S2 Signierter VNB-Abruf („Rot“) | N1, N2, N4, N5, N6, N7 | N3 (Notstrom-Reserve); Entladen ins Netz nur mit N8 = ja | Abrufdauer, max. 4 h am Stück [V] |
| S3 Vorhaltung (Vortagesankündigung des VNB) | N1, N5: freie Kapazität bzw. Füllstand für den Engpass reservieren | N3 | angekündigtes Zeitfenster |
| S4 Testabruf | N1, N2, N4–N7 | N3 | max. 15 min, max. 1× pro Monat [V] |
| S5 Gruppenstaffelung (Ladeleistung im Segment) | N4: Ladeleistung reduzieren bzw. Start zeitlich versetzen | N3 | einzelne Viertelstunden |
| S6 Kommunikationsausfall / keine gültigen Preise | N1, N2, N6: preisgesteuerte Funktionen pausieren | N3 | bis gültige Preise vorliegen |

Jede Überschreibung erscheint in Home Assistant mit **Quelle, Grund, Beginn und
Ende**. Überschriebene Nutzerwerte werden danach automatisch wieder aktiv.

## 3. Szenarien [V]

### A. Billiger Nachttarif, alle laden gleichzeitig

- **Lage:** Dynamischer Tarif, 02:00–04:00 Uhr 5 ct/kWh. 40 Speicher im Segment
  haben N1 = 8 ct und N5 = ja. Zusammen mit Wärmepumpen und E-Autos überlastet
  das den Trafo.
- **Ohne System:** Alle starten um 02:00 mit voller Leistung, und es entsteht ein
  neuer Lastengpass. Erster SimBench-Test (vorläufig, Demo-Daten): Unkoordiniertes
  Laden aller Speicher mit voller Leistung hebt die Leitungsauslastung von **34 %
  auf 90 %**.
- **Mit System (S5):** Der VNB sendet für das Segment eine Ladeobergrenze bzw.
  versetzte Startzeiten. Jede Box lädt im billigen Fenster, nur verteilt.
- **Nutzer sieht:** „Ladeleistung 2 kW statt 5 kW, 02:00–03:30, Grund:
  Netzauslastung Segment“. Der Speicher ist trotzdem bis 04:00 voll.

### B. Sonniger Mittag nach billiger Nacht (Vorhaltung)

- **Lage:** Prognose für morgen: starke PV-Einspeisung, Einspeiseengpass im
  Ortsnetz 11:00–14:00. Der Nutzer hätte nachts aus dem Netz voll geladen (N1, N5).
- **Mit System (S3):** Am Vortag kündigt der VNB an: „bis 11:00 mindestens 60 %
  freie Kapazität“. Die Box lädt nachts nur bis 40 %; mittags nimmt der Speicher
  den PV-Überschuss auf.
- **Ergebnis:** Weniger Abregelung nach § 101 ElWG; der Nutzer verliert nur den
  Arbitragevorteil der Nacht für diesen Tag (Vergütung der Vorhaltung [O]).

### C. Abendspitze mit Lastengpass, Nutzer will Notstrom behalten

- **Lage:** 18:00 Uhr, Lastengpass. Einspeisepreis 30 ct. Nutzer: N2 = 25 ct,
  N3 = 30 %, N8 = ja. Speicher bei 80 %.
- **Mit System (S2):** Der VNB ruft Entladen an. Die Box entlädt bis 30 % und
  stoppt dort, weil N3 nicht überschreibbar ist. Die Vergütung des Abrufs und der
  Einspeisepreis laufen getrennt (Doppelvermarktung regeln, siehe
  [01 § 5](research/01-regulierung-finanzierung.md)).
- **Variante N8 = nein:** Die Box entlädt nicht ins Netz, deckt aber den eigenen
  Haushalt aus dem Speicher (Netzbezug sinkt). Auch das entlastet den Engpass.

### D. Testabruf

- **Lage:** Monatlicher Testabruf, 10:15–10:30, Sollwert „+3 kW laden“.
- **Mit System (S4):** Die Box folgt unabhängig von N1/N5. Das Smart Meter und das
  eigene Messmodul messen Reaktionszeit und Leistung; daraus wird der
  Zuverlässigkeitswert aktualisiert.
- **Nutzer sieht:** „Testabruf 15 min, Energie wird gutgeschrieben“ [V].

### E. Preise fehlen (Funkstörung)

- **Lage:** Der Preisvektor für morgen ist bis 18:00 nicht angekommen.
- **Mit System (S6):** Arbitrage (N1, N2, N6) pausiert. Die Box optimiert nur den
  Eigenverbrauch und bleibt für Netzabrufe erreichbar, soweit möglich. Fallback
  bei Abrufen nach TOR Typ A.
- **Nutzer sieht:** „Keine gültigen Preise für morgen; nur Eigenverbrauch“.

### F. Manipulierter Preis

- **Lage:** Eine Home-Assistant-Integration oder ein Angreifer im Heimnetz meldet
  „Bezugspreis −50 ct“, damit alle Speicher gleichzeitig laden.
- **Mit System:** Die Box nimmt Preise nur signiert über ihren eigenen Kanal an.
  Über den Home-Assistant-Kanal des `ETH`-Moduls kommen nur Werte aus der Parameterliste.
  Ein falscher Preis hat keine Wirkung.
- **Relevanz für den Pitch:** Ein manipulierter Preis würde sonst viele Speicher
  gleichzeitig steuern, also genau das Massenrisiko, das das Profil verhindern soll.

### G. Negative Preise zur Mittagszeit

- **Lage:** Day-Ahead −3 ct/kWh, Speicher bereits voll, PV erzeugt weiter.
- **Mit System:** Der Speicher ist voll, Laden geht nicht mehr. Die Box begrenzt
  die Einspeisung, wenn der Einspeisetarif bei negativen Preisen null oder
  negativ ist (Wechselrichter-Sollwert). Überschreibt nichts, folgt der
  Tarifregel.

### H. Unplausible Nutzerwerte

- **Lage:** Der Nutzer setzt N4 = 15 kW bei einem 5-kW-Gerät oder N3 = 90 %.
- **Mit System:** Das Kernmodul begrenzt auf den zulässigen Bereich (5 kW bzw.
  50 %) und meldet den begrenzten Wert an Home Assistant zurück.

### I. Abendabruf zwingt zu teurem Nachkauf in der Nacht (Schadlosstellung, § 6)

- **Lage:** 18:00–19:00 Lastengpass, VNB ruft 5 kWh Entladen ab. Ohne Abruf hätte
  der Haushalt diese 5 kWh von 19:00–23:00 selbst verbraucht. Dynamischer Tarif:
  19:00–23:00 Bezug 32 ct/kWh.
- **Rechnung der Box:** Referenz (ohne Abruf) 0 € Bezug. Ist: 5 kWh × 32 ct =
  1,60 € Bezug, minus 5 kWh × 12 ct Einspeiseerlös im Abruf = 0,60 €. **Mehrkosten
  1,00 €** + Verschleißpauschale 5 kWh × 5 ct = 0,25 € → **Ersatz 1,25 €**.
- **Dazu** die Abrufvergütung (z. B. Arbeitspreis 20 ct/kWh × 5 kWh = 1,00 €).
- **Nutzer sieht:** „Eingriff 18:00–19:00 · Mehrkosten 1,25 € ersetzt ·
  Vergütung 1,00 € · netto +1,00 €“.

### J. Vorhaltung verhindert bessere Vermarktung

- **Lage:** Wie Szenario B. Der Nutzer hätte nachts für 6 ct geladen und abends
  für 28 ct eingespeist (N6 = ja, N7 erfüllt). Wegen der Vorhaltung lädt die Box
  nachts nur bis 40 %.
- **Rechnung der Box:** Entgangene Arbitrage für die nicht geladene Menge
  (z. B. 3 kWh × (28 − 6) ct × Wirkungsgrad 0,9 ≈ 0,59 €) → **Ersatz 0,59 €**
  plus Vorhaltevergütung.
- Der Mittags-PV-Überschuss, den der Speicher stattdessen aufnimmt, wird in der
  Ist-Rechnung gegengerechnet; der Ersatz ist also nur der echte Nachteil.

## 4. Tarife: signiert über die Box [V]

### 4.1 Tariftypen, die abgebildet werden müssen

| Typ | Beispiel | Änderung | Was die Box braucht |
|---|---|---|---|
| **Fixpreis** | 25 ct/kWh, ganzjährig | selten (Vertragswechsel) | ein Wert; Arbitrage dann sinnlos, nur Eigenverbrauch |
| **Zeitvariabel, statisch** | HT/NT-Fenster; Sommer-Niedrigpreisfenster beim Netzentgelt (siehe [01 § 3](research/01-regulierung-finanzierung.md)) | selten | Zeitfenster-Tabelle mit Gültigkeit |
| **Index/Floater** | Monatspreis nach Börsenindex | monatlich | ein Wert pro Monat |
| **Dynamisch** | Day-Ahead-Spot + Aufschlag, Viertelstunden (15-min-Day-Ahead seit 10/2025 [Vorwissen, prüfen]) | täglich | 96 Werte pro Tag |
| **Einspeisetarif** | fix, Marktpreis monatlich oder dynamisch; ggf. 0 bei negativen Preisen | je Typ | wie oben, eigene Tabelle |

Bezug und Einspeisung können **verschiedene Vertragspartner** haben (Lieferant,
Abnahmestelle). Netzentgelte kommen vom **VNB**.

### 4.2 Aufbau: Formel pro Kunde, Preisvektor für alle

Der Endpreis wird in der Box aus signierten Teilen berechnet:

```
Bezugspreis(t)    = Energiepreis(t) + Netzentgelt(t) + Abgaben/Steuern
Energiepreis(t)   = a × Spot(t) + b          (Fixpreis: a = 0)
Einspeisepreis(t) = c × Spot(t) + d, mit Regel für negative Preise
```

| Dokument | Signiert von | Inhalt | Gilt für | Übertragung |
|---|---|---|---|---|
| **T1 Tarifformel Bezug** | Lieferant | Typ, a, b, Zeitfenster, Gültigkeit | einen Kunden | einmalig/bei Vertragsänderung, Unicast |
| **T2 Tarifformel Einspeisung** | Abnahmestelle | Typ, c, d, Regel negativer Preis | einen Kunden | wie T1 |
| **T3 Netzentgelt-Tabelle** | VNB des Anschlusses | Zeitfenster, Preise je Netzebene; Werte aus der Systemnutzungsentgelte-Verordnung der E-Control für den jeweiligen Netzbereich [V, prüfen] | alle Kunden eines Netzbereichs | selten, Multicast |
| **T4 Preisvektor** | **gemeinsame Preisstelle, betrieben von der E-Control** [E] | 96 Viertelstundenwerte für morgen | **alle** Boxen | täglich nach der Day-Ahead-Auktion, Multicast |
| **T5 Abgaben/Steuern** | Lieferant | fixe Bestandteile | alle | selten |

Dadurch muss nur **ein** Dokument täglich an alle Boxen (T4); alles Kundenspezifische
ändert sich selten.

**Demo-Region Steyr / Steyr-Land:** Dort gibt es voraussichtlich zwei VNB (Netz OÖ
und einen lokalen VNB in der Stadt Steyr [unbestätigt]). Jede Box akzeptiert T3 nur
vom VNB ihres eigenen Anschlusses; welcher das ist, steht in der signierten
Verbauliste. Lieferant und Preisvektor T4 sind davon unabhängig.

### 4.3 Größe über LoRaWAN [V]

- T4: 96 Werte × 1 Byte (Differenz zum Vortageswert in 0,1 ct, Überlauf mit
  Escape-Code) + Kopf ~16 Byte + Signatur 64 Byte (Ed25519) ≈ **180 Byte**.
- Ein LoRaWAN-Downlink fasst in EU868 je nach Datenrate etwa 51–222 Byte
  [Vorwissen, prüfen]. Deshalb **Multicast (Class C) mit Fragmentierung**
  (LoRaWAN Fragmented Data Block Transport) bzw. Aufteilen in 2–4 Pakete.
- Bei Ethernet- oder LTE-Modul entfällt die Grenze; das Format bleibt gleich.

### 4.4 Prüfung in der Box

- Signatur gegen die PKI-Rolle prüfen: Lieferant darf T1/T5, VNB darf T3,
  die gemeinsame Preisstelle darf T4 signieren. Die Preisstelle ist eine **eigene
  PKI-Rolle mit eigenem Zertifikat**, getrennt vom Steuerbefehlsschlüssel des VNB
  und von der Modulsignatur der Trusted Authority [E] (siehe
  [hardware-konzept.md § 6](hardware-konzept.md)); keine Rolle darf Dokumente einer anderen Rolle
  ausstellen.
- **Gültigkeit** (von/bis) und **Sequenznummer** gegen Wiedereinspielen alter Preise.
- **Plausibilität:** Werte außerhalb eines Bandes (z. B. −50 … +100 ct/kWh)
  verwerfen und melden.
- Ohne gültiges T4 für den aktuellen Tag: Szenario E (nur Eigenverbrauch).
  Statische Tarife (T1 ohne Spot-Anteil) bleiben bis zum Ablauf gültig.
- Home Assistant bekommt die **berechneten Preise nur lesend**, damit der Nutzer
  seine Schwellen N1/N2 sinnvoll setzen kann.

### 4.5 Dynamisches Netzentgelt je Segment (T3d) [V]

**Stand Österreich (Oktober 2026):** Ab 2027 gibt es **zeitvariable, aber statische**
Netzentgelte. Die Fenster sind fix und gelten im ganzen Netzbereich gleich.

| Instrument | Inhalt | Ab |
|---|---|---|
| SNAP (Sommer-Niedrigpreisfenster) | 1.4.–30.9., 10–16 Uhr, Arbeitspreis ca. −20 % | 1.4.2026 |
| WiNAP (Winter-Niedrigpreisfenster) | 1.10.–31.3., 23–5 Uhr, Höhe in der Tarifverordnung | 10/2027 |
| Leistungspreis (SNE-G-V, BGBl. II 299/2026) | höchste Viertelstunde im Monat; Anteil steigt in 3 Jahren bis 50:50; NE 7 zweistufig bis/ab 10 kW | 1.1.2027 |
| Flexible Entnahme (§ 10 SNE-G-V) | ab 4 kW, VNB darf in zwei festen Fenstern bis 100 % einschränken; eigener Leistungspreis | 1.10.2027 |
| § 128 ElWG | zeitvariable Entgelte; Abschlag für unterbrechbare/regelbare Leistung | geltend |

Ein Netzentgelt, das sich nach dem **Zustand eines Netzsegments** richtet, ist
nicht vorgesehen; ein österreichisches Pilotprojekt dazu ist nicht bekannt. In
Deutschland hat das Pilotprojekt „Grids & Benefits“ viertelstündliche Netzentgelte
am Vortag veröffentlicht (mehr als 70 % der Ladevorgänge verschoben, Angabe des
Konsortiums); die Bundesnetzagentur plant ein Konzept für 2027 (siehe
[01](research/01-regulierung-finanzierung.md)). Eine Studie im Auftrag von RWE
(Frontier Economics) hält eine Weiterentwicklung des Redispatch für besser.

**Problem statischer Fenster:**

- Beginnt das WiNAP-Fenster um 23 Uhr, starten Wallboxen und Heimspeicher im ganzen
  Netzbereich gleichzeitig (Szenario A). Derselbe Effekt wie der Rebound nach den
  DE-Sperrzeiten in § 7.2: plus 25–33 % Abendspitze.
- Der Leistungspreis belohnt die Spitze des **Haushalts**, nicht die des
  **Segments**. Eine Wärmepumpe um 3 Uhr senkt die eigene Spitze, hilft dem
  Netz aber nur, wenn das Segment um 3 Uhr Reserve hat.

**Vorschlag: T3d als zusätzliches Dokument je Segment**

| Dokument | Signiert von | Inhalt | Gilt für | Übertragung |
|---|---|---|---|---|
| **T3d Segmentsignal** | VNB des Anschlusses (Rolle wie T3) | 96 Viertelstundenwerte ΔNE(t) für morgen, nur **Rabatt** (ΔNE ≤ 0) | alle Boxen einer Ortsnetzstation | täglich, Multicast-Gruppe je Station; nur an Tagen mit Engpassprognose |

```
Bezugspreis(t) = a × Spot(t) + b + Netzentgelt_T3(t) + ΔNE_seg(t) + Abgaben/Steuern
```

- **Format wie T4:** ca. 180 Byte mit Signatur. Die Box kennt ihre Station aus der
  signierten Verbauliste und nimmt T3d nur für diese an.
- **Berechnung beim VNB:** aus der Netzzustandsprognose des Segments für morgen
  (PV aus GeoSphere-NWP-Globalstrahlung, Wärmepumpen aus der Temperatur, Lastprofil).
- **Bei Einspeiseengpass:** Rabatt auf den Bezug zur Mittagszeit; Speicher und
  Wallboxen laden dann aus dem Segment statt aus der Nacht.
- **Bei Lastengpass:** Rabattfenster in der Nacht **je Segment gestaffelt** (z. B.
  ein Teil ab 22 Uhr, ein Teil ab 1 Uhr). So verteilt sich der Ladebeginn, statt
  dass alle um 23 Uhr starten.
- **Nur Rabatt, kein Aufschlag:** Ein Aufschlag in schwachen Segmenten würde
  Kunden je nach Netzlage ungleich behandeln. Ein Bonus für netzdienliches
  Verhalten passt dagegen in die Logik von § 128 ElWG und § 10 SNE-G-V.

**Verhältnis zu Abruf und Förderung:**

1. **Erst das Signal:** T3d lenkt, das EMS optimiert auf den Gesamtpreis (N1/N2
   gelten weiter).
2. **Dann der Abruf:** Zeigt die Prognose am Vortag trotz T3d einen Engpass, folgen
   signierte Vorgaben (S2, S5) mit Schadlosstellung nach § 6. Je mehr T3d
   erreicht, desto seltener und billiger sind diese Eingriffe.
3. **Keine Schadlosstellung für T3d:** Die Reaktion ist freiwillig; der Kunde
   folgt nur, wenn es sich für ihn rechnet.
4. **Auch Stufe 0 wirkt mit:** Kunden ohne Steuerbarkeit (§ 5.2) können auf T3d
   reagieren. Die Förderstufe ändert sich dadurch nicht, weil die Wirkung nicht
   garantiert ist.

**Abrechnung:** Ein Rabatt je Viertelstunde braucht Viertelstundenwerte. Die
übertragen heute nur 12,6 % der Smart Meter (Opt-in, § 5.4). Die signierte Messung
der Box (`MTR`) kann die Lücke schließen.

**Rechtsfrage [O]:** Netzentgelte legt die E-Control per Verordnung je Netzbereich
einheitlich fest [prüfen]. Ein Unterschied je Segment innerhalb eines Netzbereichs
ist daher wahrscheinlich nur als **Flexibilitätsvergütung** nach § 139 Abs. 4
ElWG (Kosten in den Netzentgelten) oder als Abschlag nach § 128 möglich, nicht als
eigenes Netzentgelt. Für die Demo heißt T3d deshalb „Segmentsignal des VNB“.

**Quellen:** [pv magazine: E-Control schlägt zeitvariable Netzentgelte vor](https://www.pv-magazine.de/2025/10/20/e-control-schlaegt-zeitlich-variable-netzentgelte-fuer-oesterreich-vor/),
[i-magazin: Netzentgelte-Reform 2027](https://i-magazin.com/e-control-netzentgelte-reform-2027/),
[E-Control: Neue Regeln für die Energiewende](https://www.ots.at/presseaussendung/OTS_20261012_OTS0085/e-control-neue-regeln-fuer-die-energiewende),
[E-Control: ElWG-Umsetzung (Emberger, 16.3.2026)](https://www.e-control.at/documents/1785851/1811582/20260316-ElWG-Umsetzung-02-Karin-Emberger.pdf/e2797780-a1a6-7d83-beb5-1a9c7f17f9c0?t=1773672562574),
[TenneT: Pilotprojekt dynamische Netzentgelte](https://www.tennet.eu/de/news/pilotprojekt-zeigt-dynamische-netzentgelte-entlasten-stromnetze-und-reduzieren-kosten-fuer-endkundinnen),
[Frontier Economics: Bewertung dynamischer Netzentgelte](https://www.frontier-economics.com/media/gqxjwza4/rpt-frontier-bewertung-dynamischer-netzentgelte-und-weiterentwicklung-des-redispatch-final-2026-04-01_clean-stc.pdf).

## 5. Förderung nach Grad der Steuerbarkeit

### 5.1 Festgelegt [E] (Owner, 24.10.2026)

- Die Förderhöhe richtet sich nach der **Steuerbarkeit, die der Kunde zulässt**:
  mehr Steuerbarkeit → mehr Netzdienlichkeit → höhere Förderung.
- Die **volle Förderung** wird erst ausgezahlt, wenn möglichst viel Steuerbarkeit
  für das Netz gegeben ist.

### 5.2 Förderstufen [V, Prozentsätze illustrativ]

| Stufe | Was der Kunde zulässt | Förderung (Anteil am Höchstsatz) |
|---|---|---|
| 0 | keine Steuerschnittstelle | Basis, z. B. 40 %; Box nicht gefördert |
| 1 | Steuerbar nur in Laderichtung (Einspeiseengpass), Testabrufe, N3 ≤ 50 % | z. B. 60 % |
| 2 | Steuerbar in **beide Richtungen**, Testabrufe, N3 ≤ 30 % | z. B. 80 % |
| 3 | Stufe 2 **plus** Entladen ins Netz bei Abruf (N8 = ja), Vorhaltung (S3) zugelassen, N3 ≤ 20 % | **100 %** |

- [E] Solange Einspeisung aus dem Speicher noch nicht freigeschaltet ist
  (Messkonzept nicht akzeptiert), ist Stufe 3 **ohne** N8 erreichbar; N8 wird
  erst ab der Freischaltung Bedingung (Owner, 24.10.2026).
- Die Grenzen für N3 in der Tabelle sind vorläufig; siehe § 5.4.

- Die Box samt Installation ist ab Stufe 1 voll gefördert ([anforderungen.md](anforderungen.md) § 3).
- Die Stufe ergibt sich direkt aus den Parametern N3 und N8 und der Freigabe
  von S3; der Kunde sieht in Home Assistant, welche Stufe seine Einstellung ergibt.
- Stufe 2 entspricht der bisherigen Bedingung „volle Förderung nur bei
  Ansteuerbarkeit in beide Richtungen“; Stufe 3 macht daraus „volle Förderung nur
  bei möglichst viel Steuerbarkeit“. Entladen ins Netz bleibt freiwillig, wird
  aber belohnt.

### 5.3 Auszahlung nach gemessener Netzdienlichkeit [V]

- **Bei Inbetriebnahme:** 50 % der Förderung der gewählten Stufe, nach dem ersten
  erfolgreichen Testabruf.
- **Rest in jährlichen Tranchen** (z. B. über 5 Jahre), je nach **gemessenem**
  Erfüllungsgrad: Erreichbarkeit der Box, Zuverlässigkeit in Testabrufen, im
  Jahresmittel eingestellte Stufe.
- Den Jahresnachweis erstellt die Box signiert (eigene Messung `MTR`); der VNB
  leitet ihn an die Förderstelle weiter (Schnittstelle I8 in
  [07-synthese.md](research/07-synthese.md)).
- Der Kunde darf die Stufe jederzeit senken. Dann sinken die **künftigen**
  Tranchen; bereits Ausgezahltes wird nicht zurückgefordert (Akzeptanz).
- Wirkung: Wer nur für die Förderung eine hohe Stufe einstellt und sie danach
  senkt, verliert die späteren Tranchen.

### 5.4 Wie weit darf die Notstrom-Reserve (N3) die Stufe begrenzen? [V, offen]

Überlegungen:

- **Die Reserve wirkt nur bei Entlade-Abrufen** (Lastengpass, Winterabend). Bei
  Lade-Abrufen (Einspeiseengpass, Sommermittag) stört sie nicht.
- **Prozent ist ungerecht:** 20 % sind bei 15 kWh 3 kWh, bei 5 kWh nur 1 kWh. Besser
  in **kWh**.
- **Notstrom nur bei notstromfähiger Anlage:** Ohne Umschalteinrichtung bzw.
  Ersatzstromfunktion hat eine Reserve keinen Nutzen für den Haushalt; dann gilt
  nur das technische Minimum des BMS.
- **Krisenvorsorge ist gewollt** (Blackout-Vorsorge). Ein Konzept, das Kunden die
  Reserve abspricht, verliert Akzeptanz.

Vorschlag:

1. N3 wird in **kWh** eingestellt.
2. Eine **geschützte Grundreserve** (Platzhalter: bis 2 kWh, etwa ein Tag
   Grundversorgung mit Kühlschrank, Heizungspumpe, Router und Licht [Schätzung])
   zählt **nicht** gegen die Stufe. Sie gibt es nur bei notstromfähigen Anlagen.
3. Was darüber liegt, verringert die **freigegebene Kapazität**. Die Stufe richtet
   sich nach deren Anteil an der Nutzkapazität: z. B. Stufe 3 ≥ 80 %, Stufe 2
   ≥ 60 % [Platzhalter].
4. Die Reserve bleibt **nie überschreibbar**, auch nicht im Krisenfall.

#### Größe der geschützten Grundreserve

- [E] Die Grundreserve wird **aus Verbrauchsdaten** bemessen, nicht pauschal
  (Owner, 24.10.2026):
  - **Bestehender Haushalt:** Daten des Smart Meters
  - **Neubau mit neuem Netzanschluss:** zunächst Erfahrungswerte
  - **Nach einem Jahr Betrieb:** mit echten Betriebsdaten nachschärfen
- [V] Umsetzung:
  - **Datenlage AT:** Ende 2024 hatten 96,9 % der Zählpunkte ein Smart Meter,
    aber nur 12,6 % übertragen Viertelstundenwerte (Opt-in); Standard sind
    Tageswerte (E-Control-Monitoring, Sekundärquellen [prüfen]). Der Kunde muss der
    Nutzung zustimmen; mit Opt-in wird die Bemessung genauer.
  - **Kennzahl:** Grundlast in den Wintermonaten (z. B. 10-%-Quantil der
    Viertelstundenleistung) × Überbrückungsdauer (z. B. 24 h). Nur mit
    Tageswerten: grober Schätzwert aus dem niedrigsten Tagesverbrauch.
  - **Neubau:** Startwert aus Haushaltsgröße, Wohnfläche und Heizungsart
    (Erfahrungswerte bzw. Standardlastprofil).
  - **Nachschärfen:** nach 12 Monaten und danach jährlich, aus der eigenen
    signierten Messung der Box (`MTR`); ab dann ist kein Opt-in beim Smart Meter
    mehr nötig.
  - **Deckel:** Die geschützte Grundreserve beträgt höchstens z. B. 30 % der
    Nutzkapazität [Platzhalter], damit ein übergroßer Wert die Stufe nicht aushebelt.
  - [E] Die **Wärmepumpe zählt nicht** zur geschützten Grundreserve (Owner,
    24.10.2026). Wer sie im Notfall versorgen will, stellt eine Reserve über der
    Grundreserve ein; dieser Teil zählt normal für die Förderstufe.

## 6. Schadlosstellung: der Kunde verliert durch Eingriffe kein Geld

### 6.1 Festgelegt [E] (Owner, 24.10.2026)

- Der Kunde darf durch Eingriffe des Netzbetreibers **nie schlechter gestellt**
  werden als ohne Eingriff. Das gilt insbesondere, wenn er
  - den Strom anderweitig besser hätte vermarkten können, oder
  - wegen eines Entlade-Abrufs später (z. B. in der Nacht) teuren Strom kaufen muss.

### 6.2 Verfahren [V]

1. **Referenz ohne Eingriff:** Der EMS-Algorithmus in der Box ist deterministisch
   und signiert. Nach einem Eingriff rechnet die Box nach, was sie **ohne** Eingriff
   getan hätte: mit den tatsächlichen Werten für PV und Verbrauch, den signierten
   Preisen (T1–T5) und den Nutzerparametern. Der VNB kann diese Rechnung mit den
   protokollierten Eingangsdaten nachvollziehen.
2. **Ist:** signierte Messung (`MTR`) von Bezug und Einspeisung.
3. **Betrachtungszeitraum:** vom Eingriff bis der Speicher wieder dem
   Referenzverlauf folgt, höchstens 48 h.
4. **Ersatz** = (Bezugskosten Ist − Referenz) − (Einspeiseerlös Ist − Referenz)
   + Verschleißpauschale je zusätzlich bewegter kWh (z. B. 5 ct/kWh [V]).
   Negativer Ersatz (Eingriff war für den Kunden günstig) wird **nicht**
   abgezogen.
5. **Zusätzlich** die Vergütung für Abruf bzw. Vorhaltung. Damit ist der Kunde
   netto immer ≥ 0, im Normalfall im Plus.
6. **Abrechnung:** monatlich, Gutschrift des VNB auf der Netzrechnung. Die Kosten
   sind als Flex-Kosten in den Netzentgelten anerkennbar (§ 139 Abs. 4 ElWG, siehe
   [01-regulierung-finanzierung.md](research/01-regulierung-finanzierung.md)).
7. **Anzeige:** pro Eingriff in Home Assistant bzw. App: Zeitraum, Grund,
   Mehrkosten, Ersatz, Vergütung (Szenarien I und J).

### 6.3 Missbrauch verhindern [V]

- Für die Referenz gelten die Nutzerparameter, die **24 h vor** dem Eingriff bzw.
  bei dessen Ankündigung eingestellt waren. Wer kurz vorher N1/N2 verstellt, um
  einen höheren Ersatz zu erzielen, hat davon nichts.
- Testabrufe (S4) werden genauso abgerechnet; ihre Energie wird also ebenfalls
  ersetzt.
- Bei Fixpreis-Kunden gibt es keine Arbitrage; der Ersatz ist dann nur der
  Nachkauf zum Fixpreis abzüglich Einspeiseerlös plus Verschleißpauschale.

## 7. Benötigte Speicherkapazität und Degradation

### 7.1 Festgelegt [E] (Owner, 24.10.2026)

- Ermittelt wird die **tatsächlich nötige Energiemenge** zur Netzstabilisierung,
  also wie viel Speicherkapazität je Netzsegment wirklich gebraucht wird.
- Die **Degradation der Speicher** wird bei der Nutzung berücksichtigt.

### 7.2 Bedarf je Segment ermitteln [V]

Grundlage: Zeitreihen in Viertelstunden je Segment aus der Simulation
(SimBench/pandapower, Demo-Region Steyr) bzw. später aus Messdaten.

1. **Überlast je Zeitschritt:** P_über(t) = max(0, P(t) − P_grenz), getrennt für
   Bezug (Lastengpass) und Einspeisung (Einspeiseengpass). P_grenz z. B. 100 % der
   Bemessungsleistung von Trafo bzw. Leitung, mit Sicherheitsabstand nach
   Prognosegüte (siehe Wetternutzung).
2. **Je Engpass-Ereignis:** Energie E_ev = Σ P_über · Δt und Spitzenleistung
   P_max = max P_über.
3. **Netto-Bedarf des Segments:** E_netto = größtes E_ev im Jahr; liegen Ereignisse
   ohne ausreichende Pause zum Nachladen hintereinander, zusammen gerechnet.
   Leistungsbedarf = P_max. Bei Heimspeichern (ca. 5 kW je Gerät) kann die
   **Leistung** statt der Energie die engere Grenze sein.
4. **Installierter Bedarf:** E_inst = E_netto / (Verfügbarkeit × Zuverlässigkeit ×
   freigegebener Anteil × SoH am Lebensende).
   Beispiel [Platzhalter]: 0,6 (Speicher hat zur richtigen Zeit Platz bzw. Ladung)
   × 0,85 (Zuverlässigkeit; Flex+ lieferte 79 %, siehe
   [02-pilotprojekte.md](research/02-pilotprojekte.md)) × 0,8 (Stufe 3) × 0,8 (SoH)
   ≈ **0,33**, also rund das **Dreifache** des Netto-Bedarfs.
5. **Anzahl Speicher:** E_inst / mittlere Nutzkapazität je Haushalt; zugleich
   Leistung prüfen: Anzahl ≥ P_max / (Leistung je Gerät × Zuverlässigkeit).
6. **Ergebnis je Segment:** Engpass-Stunden pro Jahr, E_netto, E_inst, Anzahl
   Speicher. Das ist der direkte Vergleich mit dem Netzausbau (Pitch-Zahl).

**Rechnung für Steyr (Session infra-kg-austria-9c, Stand 24.10.2026):**
Simulation mit 257 Ortsnetzstationen (141 aus OSM, 116 synthetisch), BOKU-PV,
BEV-Gebäuden, PVGIS 2023, Lastprofil APCS H0 und 1.049 Heimspeichern
(`scripts/steyr_sim_variant_a.py`, Branch `feat/steyr-pv-quellen` in infra-kg).
Einschränkungen:

- **Stündlich statt Viertelstunde** (PVGIS ist stündlich): E_ev in kWh stimmt,
  P_max ist eher unterschätzt.
- **Segment = Ortsnetzstation (Trafo).** Angenommene Trafo-Bemessung:
  max(1,5 kVA je Haushalt, 0,7 × kWp, 160 kVA), auf Normgröße gerundet.
  Leitungsgrenzen nur in den 24 stärksten Stunden, synthetisches Netz
  (minimaler Spannbaum, NAYY 4x150).
- **Nur Einspeiseengpass:** Wärmepumpen und E-Autos sind noch nicht modelliert,
  Lastengpässe (Winterabend, Szenario C) fehlen also im Ergebnis.
- **Durchdringung:** heute (BOKU 2021–2023) sowie PV × 1,5 und × 2 bei gleichem Trafo.
- **Wärmepumpen und E-Autos:** Modell liegt vor (`scripts/steyr_wp_ev.py` in infra-kg,
  Temperatur aus PVGIS T2m, Szenarien heute / 2030 / 2040); Einbau in die
  Steyr-Rechnung durch Session 9c steht aus.

Ergebnis (nur Einspeiseengpass, Grenze 100 % Trafo, Basisfall Eigenverbrauch,
Bericht `docs/reports/2026-10-24-steyr-variante-a.md` in infra-kg):

| PV-Stand | Stationen mit Engpass (von 257) | Engpass-h/a Median | E_netto Summe / Median | E_inst Summe / Median | Speicher (10 kWh) Summe / Median | Speicher im Modell dort | Netz-Vollzyklen/a Median (P10–P90) | Trafo ohne Speicher: +1 Stufe / ≥ +2 / > 1000 kVA |
|---|---|---|---|---|---|---|---|---|
| heute | 2 | 21 | 0,15 MWh / 73 kWh | 0,45 MWh / 224 kWh | 46 / 23 | 8 | 1,2 (0,6–1,8) | 2 / 0 / 0 |
| PV × 1,5 | 21 | 285 | 12,8 MWh / 378 kWh | 39,2 MWh / 1.158 kWh | 3.933 / 116 | 69 | 7,9 (1,8–15,7) | 13 / 6 / 2 |
| PV × 2 | 31 | 674 | 41,9 MWh / 922 kWh | 128,2 MWh / 2.826 kWh | 12.839 / 283 | 140 | 17,4 (2,6–22,5) | 14 / 8 / 9 |

- Überall begrenzt die Energie, nicht die Leistung.
- Die Engpass-Stationen sind PV-lastig mit wenigen Haushalten (Gewerbe- und
  Agrar-PV 30–250 kWp); der Bedarf ist mehr als zehnmal so groß wie die vorhandenen
  Haushaltsspeicher. Dort gehören Gewerbe- und Agrarspeicher bzw. Abregelung dazu.
- Pitch: Heute hat Steyr praktisch keinen Engpass (2 von 257 Stationen); bei PV × 1,5
  braucht es 21 Trafo-Verstärkungen, die sich vor allem dort vermeiden lassen, wo
  Haushalte dominieren.

**Lastengpass mit Wärmepumpen und E-Autos** (Session infra-kg-austria-18, Stand
24.10.2026, nach Korrektur des Netzmodells K1–K6, Belege in
`docs/research/2026-10-24-netzmodell-belege.md` in infra-kg; Trafo mindestens 2 kVA je
Haushalt; `steyr_wp_ev.py` mit Heizstab unter −7 °C, ohne Sperrzeiten; INCA-Temperatur
1 km je Station; PV × 1). Die früheren Werte 1 / 31 / 170 Stationen sind überholt.

| Wetterjahr | heute: Stationen | 2030: Stationen / Engpass-h Median / E_netto Summe / Speicher Summe | 2040: Stationen / Engpass-h Median / E_netto Summe / Speicher Summe |
|---|---|---|---|
| Referenz (PVGIS 2023, ein Temperaturpunkt) | 1 | 8 / 28 / 4,2 MWh / 1.279 | 159 / 19 / 110 MWh / 33.791 |
| INCA 2023 | 1 | 11 / 2 / 5,7 MWh / 1.757 | 161 / 19 / 128 MWh / 39.418 |
| INCA 2017 | 2 | 14 / 3,5 / 6,9 MWh / 2.107 | 174 / 30 / 164 MWh / 50.212 |
| INCA 2012 (Kältewelle Feb., −20,6 °C) | 2 | 18 / 4,5 / 10,9 MWh / 3.342 | 190 / 40 / 487 MWh / 149.374 |

- **Das Kältejahr bestimmt das Ergebnis,** der Heizstab kaum (+1 Station, +6 % E_netto).
- **Einspeiseengpässe** nach der Korrektur: 1–3 / 19 / 32–34 Stationen bei PV × 1 /
  × 1,5 / × 2 (vorher 2 / 21 / 31).
- **Heimspeicher binden über die Energie:** Eine Kältewelle verbindet mehrere Abende
  zu einem Ereignis; daher die hohen Speicherzahlen 2040. Im Winter setzt die
  Verfügbarkeit 0,6 Netzladung am Vortag voraus (Ziel-SoC), weil Heimspeicher dann
  nach dem PV-Laden meist leer sind.

**V2G-Demo: drei Lösungen für den Lastengpass am Winterabend** (Wetterjahr 2012,
Modellwerte):

- Schwaches Segment: reale OSM-Station way/235746848 (UW Steyr Nord), ländlich,
  250 kVA, 5 Abgänge, längster 714 m, 100 Haushalte.
- Typische Station: node/12794591194 (UW Steyr), Stadt, 400 kVA, 181 Haushalte.
- „Gleichzeitig“ = Stresstest: Am kältesten Abend laden alle E-Autos ab 18 Uhr mit
  voller Wallbox-Leistung.

| Fall | Trafo-Spitze kW (Auslastung) | Engpass-h/a | E_netto kWh | Heimspeicher (Leistung/Energie) | Gesteuertes Laden | V2G-Autos (Leistung/Energie) von vorhandenen |
|---|---|---|---|---|---|---|
| 2030 schwach, ungesteuert (19 E-Autos) | 201 (0,80) | – | – | – | – | – |
| 2030 schwach, gleichzeitig | 302 (1,21) | 1 | 52 | 13/16 | 5 Wallboxen pausiert, löst vollständig | 7/5 von 19 |
| 2030 typisch, ungesteuert (50 E-Autos) | 363 (0,91) | – | – | – | – | – |
| 2030 typisch, gleichzeitig | 655 (1,64) | 1 | 255 | 61/79 | 24 Wallboxen pausiert, löst vollständig | 34/25 von 50 |
| 2040 schwach, ungesteuert (52 WP, 69 E-Autos) | 392 (1,57) | 87 | 419 | 34/129 | 13 Wallboxen gedrosselt, löst vollständig | 19/40 von 69 |
| 2040 schwach, gleichzeitig | 851 (3,40) | 86 | 860 | 142/264 | löst nicht ganz: 321 kWh ungeladen (ca. 5 kWh je Auto in einer Nacht) | 79/82 von 69: mehr als vorhanden |
| 2040 typisch, ungesteuert (105 E-Autos) | 548 (1,37) | 43 | 335 | 35/103 | 14 Wallboxen, löst vollständig | 20/32 von 105 |
| 2040 typisch, gleichzeitig | 1.242 (3,11) | 42 | 1.085 | 199/333 | 77 Wallboxen, löst vollständig | 110/104 von 105: mehr als vorhanden |

Annahmen: V2G 11 kW je Auto, 15 kWh je Abend freigegeben, 70 % der Autos angesteckt;
gesteuertes Laden holt die Energie bis 7 Uhr nach; Heimspeicher laden nicht ins Auto;
V2G-Energie je Ereignis (bei Kältewellen mehrere Abende, also obere Schranke).
Zeitreihen und Abbildungen eines Abends (ungesteuert, gesteuert, V2G):
`output-v2g-{2030,2040}/` auf hetzner (`v2g_abend_{schwach,typisch}.png`).

Pitch-Aussagen:

1. **Ohne Sperrzeiten entsteht der Lastengpass auch in Steyr erst 2040 oder durch
   Gleichzeitigkeit.** 2030 bleibt ungesteuertes Laden unter der Trafo-Grenze
   (0,80 bzw. 0,91); das deckt sich mit SimBench.
2. **Gesteuertes Laden löst fast alles allein,** weil Wärmepumpe plus Haushalt nie über
   der Trafo-Grenze liegen. Ausnahme ist der Stresstest 2040 im schwachen Segment
   (ca. 5 kWh Komfortverlust je Auto in einer Nacht).
3. **V2G ist die Reserve für Gleichzeitigkeit und Kältewellen,** wenn Drosseln den
   Komfort verletzen würde. Ungesteuert bräuchte es 2040 30–60 % der Autos, mit
   gesteuertem Laden davor keines.
4. Für das Profil heißt das: Reihenfolge der Eingriffe **Wallbox drosseln → Heimspeicher
   → V2G**, Ziel-SoC am Vortag bei angekündigter Kälte.

**Ergebnis SimBench (Session infra-kg-austria-4e, 24.10.2026):** SimBench-NS-Netze,
Szenario 2, Jahr 2016 in Viertelstunden, vorhandene Speicher ausgeschaltet. Grenze je
Segment = kleinster Wert aus Trafo-Bemessung, Leitung ≤ 100 %, Spannungsanstieg
≤ 3 % (Einspeisung) bzw. Spannungsfall ≤ 5 % (Bezug), per Lastfluss am kritischsten
Zeitschritt bestimmt und dann als feste Grenze am Trafo angewendet (Näherung).
Faktoren auf PV / Wallboxen / Wärmepumpen: × 2 = 2/2/2, × 3 = 3/3/2, × 4 = 4/4/2.
Nach Einschätzung von 4e entspricht × 3 in Steyr-Land etwa „heute bis bald“
(rural3 × 3 = 6,4 kWp je Anschluss).

| Segment (Anschlüsse, Trafo) | Faktor | Engpass | Grenze kVA | h/a | E_netto kWh | P_max kW | E_inst kWh | Speicher (Leistung/Energie) | Netz-Vollzyklen/a |
|---|---|---|---|---|---|---|---|---|---|
| EFH semiurb4 (41, 400 kVA) | × 2 | Einspeisung | 151 (Spannung) | 11 | 31 | 16 | 94 | 10 (4/10) | 0,7 |
| EFH semiurb4 | × 3 | Einspeisung | 152 | 385 | 474 | 114 | 1.453 | **146** (27/146) | 10,0 |
| EFH semiurb4 | × 4 | Einspeisung | 144 | 811 | 1.100 | 225 | 3.371 | 338 (53/338) | 19,2 |
| EFH semiurb5 (104, 630 kVA) | × 3 | Einspeisung | 246 | 19 | 45 | 30 | 137 | 14 (7/14) | 1,4 |
| EFH semiurb5 | × 4 | Einspeisung | 246 | 288 | 442 | 137 | 1.355 | 136 (33/136) | 9,4 |
| ländlich rural3 (118, 400 kVA) | × 3 | Einspeisung | 363 | 23 | 42 | 40 | 129 | 13 (10/13) | 2,1 |
| ländlich rural3 | × 3 | Bezug | 399 (Trafo) | 0,2 | 4 | 17 | 13 | 4 (4/2) | 0,3 |
| ländlich rural3 | × 4 | Einspeisung | 363 | 302 | 618 | 184 | 1.893 | 190 (44/190) | 10,1 |
| ländlich rural3 | × 4 | Bezug | 399 | 0,5 | 14 | 56 | 43 | 14 (14/5) | 0,4 |
| Stadt urban6 (111, 630 kVA) | × 4 | Einspeisung | 309 (Spannung) | 9 | 53 | 42 | 163 | 17 (10/17) | 0,7 |

Alle übrigen Fälle haben 0 Engpass-Stunden. Folgerungen:

1. **Engpässe entstehen fast nur durch PV-Einspeisung, und zwar über den
   Spannungsanstieg, nicht über den Trafo.**
2. **Bei Einspeiseengpässen begrenzt die Energie, nicht die Leistung:** Die
   Mittagsspitzen dauern Stunden.
3. **Heimspeicher allein reichen bei hoher Durchdringung nicht:** semiurb4 × 3
   braucht 146 Geräte (10 kWh) für 41 Anschlüsse. Dann braucht es zusätzlich
   Kappung bzw. dynamische Vorgabe am Netzanschlusspunkt (TOR Typ A), größere
   Speicher oder Netzausbau. Pitch: **Kombination statt „Speicher statt Ausbau“.**
4. **Netz-Vollzyklen 0,3–19 pro Jahr:** Die Degradation durch Netzabrufe ist klein
   gegenüber 190–240 PV-Zyklen (§ 7.3).
5. **Lastengpässe** treten in SimBench erst bei × 4 und nur kurz auf. Das
   SimBench-Wärmepumpenprofil enthält deutsche EVU-Sperrzeiten (harte Nullstunden um
   8 und 17 Uhr, danach Rebound: rural3 im Jänner 82 kW um 19 Uhr bei ca. 30 kW
   Tagesmittel). Für Österreich passt das temperaturgetriebene Modell
   `steyr_wp_ev.py` besser. Für V2G als Engpassmittel braucht die Demo ein
   schwächeres Netz oder ungesteuertes gleichzeitiges Laden.
6. **Argument gegen pauschale Sperrzeiten:** Der Rebound danach erzeugt selbst
   Lastspitzen. Dosierte, signierte Vorgaben je Segment (S2, S5) vermeiden das.

**Nachrechnung mit `steyr_wp_ev.py` statt SimBench-Profilen (4e, 24.10.2026):**
Temperatur PVGIS 2016 für Steyr; Variante A mit gleicher kWh_el wie SimBench
(rural3 ca. 6.050 kWh_el je Wärmepumpe), Variante B mit Modell-Default (3.948 kWh_el).

| Segment (Grenze kVA) | Faktor | Trafo-Spitze Bezug: SimBench (Sperrzeiten) | Modell A | Modell B |
|---|---|---|---|---|
| Stadt urban6 (630) | × 4 | 347 | 263 | 265 |
| EFH semiurb4 (ca. 320–380, Spannung) | × 4 | 193 | 172 | 188 |
| EFH semiurb5 (ca. 550–630) | × 4 | 323 | 279 | 285 |
| ländlich rural3 (399) | × 2 | 376 | 292 | 246 |
| ländlich rural3 | × 3 | 415: 0,25 h Engpass, 4 Speicher | 325, kein Engpass | 280, kein Engpass |
| ländlich rural3 | × 4 | 455: 0,5 h Engpass, 14 Speicher | 343, kein Engpass | 306, kein Engpass |

- **Ohne Sperrzeiten gibt es in keinem SimBench-NS-Segment bis × 4 einen
  Lastengpass.** Die einzigen Lastengpässe kamen vom Rebound nach den
  DE-Sperrzeiten (Spitze 1.12. um 19:15, direkt nach der 17-Uhr-Sperre): plus
  85–110 kVA bzw. 25–33 % Abendspitze. Ein Teil davon stammt aus der vollen
  Gleichzeitigkeit der k-fach skalierten SimBench-Wallboxprofile.
- **Einspeiseengpässe bleiben praktisch gleich** (± 10 %), sie liegen mittags im Mai.
- **Für die Demo:** Lastengpässe und V2G als Engpassmittel brauchen ein schwächeres
  Segment (160–250-kVA-Trafo, lange Leitung) oder ein Gleichzeitigkeitsszenario
  (alle Autos laden um 18 Uhr nach einem Kältetag).
- Die Steyr-Rechnung (9c) zeigt Lastengpässe früher, weil dort die Trafos mit
  1,5 kVA je Haushalt knapp bemessen sind.

**Simulationsbibliothek gridsim (24.10.2026):** Die Steyr-Rechnung läuft jetzt als Bibliothek mit
20 Zufallsläufen je Einstellung (Repo `gridsim/`, Design `docs/superpowers/specs/2026-10-24-gridsim-live-demo-design.md`)
und trifft die Einzelrechnungen von Session 18 in Stationszahl und 2040-Energie (Abnahme:
[gridsim-abnahme.md](gridsim-abnahme.md)). Stationen mit Lastengpass von 257 (Median):

| Fall | ungesteuert | WiNAP ab 23 Uhr | T3d je Segment (§ 4.5) | gesteuertes Laden | gesteuert + V2G |
|---|---|---|---|---|---|
| 2023, 2030 | 44 | 80 | 13 | 7 | 0 |
| 2012, 2030 | 100 | 141 | 56 | 30 | 8 |
| 2023, 2040 | 193 | 216 | 176 | 103 | 19 |
| 2012, 2040 | 208 | 222 | 201 | 166 | 103 |

T3d: Signal an Tagen, für die der VNB unter WiNAP einen Engpass prognostiziert; Start je Haushalt
gestaffelt (22/0/2 Uhr) innerhalb des Segments. Gesteuertes Laden und V2G drosseln nur Wallboxen,
Wärmepumpen bleiben ungesteuert. Alle Werte sind Modellwerte.

### 7.3 Degradation [V]

Kennzahlen (Hersteller- bzw. Händlerangaben und eine Feldstudie, nicht
unabhängig geprüft):

| Kennzahl | Wert | Quelle |
|---|---|---|
| Zyklenfestigkeit LFP bis 80 % Restkapazität | 6.000–10.000 Vollzyklen | Herstellerangaben laut 42watt |
| Garantie | meist 10 Jahre, 70–80 % Restkapazität | Herstellerangaben laut 42watt |
| Vollzyklen im PV-Betrieb | 190–240 pro Jahr (E3/DC, > 3.000 Anlagen) | 42watt |
| Kapazitätsverlust im Feld | 2–3 Prozentpunkte pro Jahr | Figgener et al., Nature Energy 2024 (21 Systeme, bis 8 Jahre) |

Folgerungen:

- **Heimspeicher altern vor allem mit der Zeit, nicht mit den Zyklen:** 15 Jahre ×
  240 Zyklen = 3.600 Zyklen, also deutlich unter 6.000. Zusätzliche Netzabrufe
  (Schätzung 10–50 Vollzyklen pro Jahr, aus § 7.2 Schritt 6 berechenbar:
  Σ E_ev pro Jahr / E_inst) verbrauchen vor allem **ungenutzte** Zyklenreserve.
- **Verschleißpauschale (§ 6.2):** Obergrenze, wenn die Zyklen der Engpass sind:
  Speicherpreis / (Zyklen × Entladetiefe), z. B. 600 €/kWh / (6.000 × 0,9) ≈
  **11 ct/kWh**. Wo die Alterung über die Zeit überwiegt, sind die echten
  Mehrkosten deutlich niedriger. Vorschlag: Pauschale **5 ct/kWh**, später aus
  den gemessenen SoH-Verläufen nachschärfen.
- **Ladezustand zählt mit:** Langes Verweilen bei hohem SoC beschleunigt die
  Alterung über die Zeit. Vorhaltung (S3, Speicher teilweise leer) schont den
  Speicher; ein hoher Ziel-SoC im Winter belastet ihn. Für Szenarien mit hohem
  Ziel-SoC über Tage gehört das in den Ersatz nach § 6.
- **Planung mit SoH am Lebensende:** E_inst in § 7.2 nutzt den SoH am Ende der
  Laufzeit (z. B. 0,8), nicht die Neukapazität.
- **SoH im Betrieb:** Die Box meldet den SoH des BMS mit; die Testabrufe messen
  die tatsächlich lieferbare Energie und Leistung. Beides fließt in die
  Zuverlässigkeitsprognose und die Auswahl der abzurufenden Speicher ein
  (bevorzugt gesunde Speicher, gleichmäßige Verteilung der Abrufe).

## 8. Offen [O]

- Preisstelle (E-Control): Rechtsgrundlage und Übernahme der Spot-Preise
  (Lizenz der EPEX-Daten) klären.
- Höhe der Vergütung für Abruf und Vorhaltung (S2, S3); der Ersatz nach § 6 kommt
  immer dazu.
- Förderstelle und Rechtsgrundlage für gestufte Förderung mit Tranchen
  (EAG-Investitionszuschuss oder Landesförderung [unbestätigt]); Prozentsätze in
  § 5.2 sind Platzhalter.
- Höhe der Verschleißpauschale: Vorschlag 5 ct/kWh, Obergrenze ca. 11 ct/kWh
  (§ 7.3).
- Bedarfsrechnung nach § 7.2 mit den SimBench-Segmenten der Demo-Region
  durchführen (Demo/Daten: Session infra-kg-austria-51).
- Maximale Dauer und Häufigkeit von S2 und S4 mit Smart Grids Austria abstimmen.
- Notstrom-Reserve N3: Einheit kWh, Größe der geschützten Grundreserve,
  Schwellen der Stufen und Krisenfall (Vorschlag in § 5.4).
- Segmentsignal T3d (§ 4.5): Rechtsgrundlage (§ 128 oder § 139), Höhe des Rabatts,
  Abrechnung über die Box-Messung; Demo-Rechnung Steyr „WiNAP ab 23 Uhr“ gegen
  „T3d gestaffelt“.
