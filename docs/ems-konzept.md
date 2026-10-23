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
| **T4 Preisvektor** | **gemeinsame Preisstelle** [E]; wer das ist, ist offen | 96 Viertelstundenwerte für morgen | **alle** Boxen | täglich nach der Day-Ahead-Auktion, Multicast |
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
  die gemeinsame Preisstelle darf T4 signieren; keine Rolle darf Dokumente einer anderen Rolle
  ausstellen.
- **Gültigkeit** (von/bis) und **Sequenznummer** gegen Wiedereinspielen alter Preise.
- **Plausibilität:** Werte außerhalb eines Bandes (z. B. −50 … +100 ct/kWh)
  verwerfen und melden.
- Ohne gültiges T4 für den aktuellen Tag: Szenario E (nur Eigenverbrauch).
  Statische Tarife (T1 ohne Spot-Anteil) bleiben bis zum Ablauf gültig.
- Home Assistant bekommt die **berechneten Preise nur lesend**, damit der Nutzer
  seine Schwellen N1/N2 sinnvoll setzen kann.

## 5. Offen [O]

- Wer ist die gemeinsame Preisstelle für T4: Börse (EPEX), Regulator (E-Control)
  oder eine Trusted Authority der Box-PKI?
- Wird die Vorhaltung (S3) vergütet, und wie wird die Testabruf-Energie (S4)
  gutgeschrieben?
- Maximale Dauer und Häufigkeit von S2 und S4 mit Smart Grids Austria abstimmen.
- Darf N3 (Notstrom-Reserve) im Krisenfall (Blackout-Vorsorge) doch überschrieben
  werden, oder bleibt sie absolut?
