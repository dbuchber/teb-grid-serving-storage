# Interoperabilitätsprofil „Grid-Serving Storage“ v2 – Entwurf für einen VNB-Pilot

Stand: 24.10.2026, ergänzt 26.10.2026 (Abruf je Abgang, Netzspeicher; Grundlage: [gridsim-leitungen-abnahme.md](../gridsim-leitungen-abnahme.md)). Arbeitsentwurf, nicht abgenommen.
Grundlage: Profil v1 (Kapitel 5 der ausführlichen Seite, [site/details.html](../../site/details.html#proposal))
und ein internes technisches Gutachten vom 24.10.2026 (nicht im Repository), Findings F-15 bis F-18 sowie Teil 2 E, F, G.

**Status je Punkt:**
**entschieden(v1)** = im Profil v1 vom Team entschieden und übernommen,
**Vorschlag(v2)** = neu in diesem Entwurf, zur Diskussion mit dem VNB,
**offen** = noch zu klären.
**[extern]** = externe Tatsache, auf die sich der Entwurf stützt;
**[extern, geprüft]** = am Quelltext geprüft; **zu prüfen** = nicht verifiziert.

## 0. Was v1 festgelegt hat und was v2 ändert

Übernommen aus v1 (entschieden(v1)):

- Jede Rolle hat ein eigenes Zertifikat und signiert nur ihre eigenen Dokumente (T1–T5, Abrufe, Modulzulassung).
- Preise und Abrufe erreichen den Speicher nur signiert und nur über die Box. Kein Herstellerportal im Befehlspfad.
- Prioritätskette in der Box: Sicherheit/Fallback > signierter Abruf > Mindestreserve für Abrufe > Präferenzen des Haushalts > Eigenverbrauch. Die Notstromreserve wird nie übersteuert.
- Der Kunde wird nie schlechter gestellt. Die Förderung steigt mit der Steuerbarkeit (Stufen 0–3), die Box ist ab Stufe 1 voll gefördert.
- Home Assistant hat einen eigenen Kanal ohne Weg zum Kernmodul oder zum Kanal des Netzbetreibers. Module laufen mit signierter Software.
- Prozesse P1–P6 (Inbetriebnahme, Tagespreise, Testabruf, Engpassabruf, Verifikation und Vergütung, Fallback).

Neu in v2: zusätzliche Akteure (Abschnitt 1), P4 mit Endrampe und P7–P10 (Abschnitt 2), harte Grenzen in der Box (3), Mindestprofil für den Wechselrichter (4), PKI (5), LoRaWAN-Kapazitätsrechnung (6), Verifikation v2 (7), regulatorischer Pfad (8), Pilotplan Steyr (9).

**Neue Randbedingung aus der TOR [extern, geprüft]:** TOR Stromerzeugungsanlagen Typ A V1.4 (gültig ab 01.06.2026), Kap. 5.4.1, S. 35–36:
Die Ansteuerung erfolgt über eine Kommunikationsleitung des Netzbetreibers zu einer digitalen Schnittstelle in der Kundenanlage mit **OpenADR** (Profil auf Basis IEC 62746-10-1; Spezifikation bis 31.10.2026, Veröffentlichung bis 31.12.2026). „Eine Kommunikation über Drittsysteme ist nicht vorgesehen.“ Der Sollwert muss **innerhalb einer Minute** erreicht sein. Bei Kommunikationsverlust wird die Einspeisung auf den vereinbarten Wert bzw. **70 % der Modulspitzenleistung** begrenzt (§ 101 Abs. 2 ElWG). Nach § 76 Abs. 3 ElWG liegt die Signalübertragung hinter dem Netzanschlusspunkt beim Netzbenutzer. Standard-Blindleistung: cos φ = 1; empfohlene Q(U)-Stützpunkte 0,92/0,96/1,05/1,08 U_n.

Folgen für v2 (Vorschlag(v2)): Die Box **ist** die digitale Schnittstelle in der Kundenanlage. Sie implementiert den OpenADR-Endpunkt (VEN) für die PV nach TOR und den LoRaWAN-Broadcast für Speicherabrufe als zusätzlichen Kanal. Beide enden im selben Kernmodul, keiner führt über ein Drittsystem. Der TOR-Fallback (70 %-Begrenzung der PV) gilt unverändert neben dem Speicher-Fallback P6.

---

## 1. Akteure (Ergänzung zu v1)

| Akteur | Rolle im Profil | Signiert | Empfängt | Status |
|---|---|---|---|---|
| Verteilernetzbetreiber (VNB) | Engpasserkennung je Segment, Abrufe, Testabrufe, Segmentzuordnung, Vergütung | Abrufe, Testabrufe, T3, Segmentzuordnung (P9), Widerrufe der VNB-Schlüssel (P10) | 15-min-Werte, Abrufprotokolle, Wechselrichter-Rückmeldungen (aggregiert) | entschieden(v1), Erweiterung Vorschlag(v2) |
| Messstellenbetreiber / Smart-Meter-Backend | Liefert die geeichten 15-min-Werte für Verifikation und Vergütung. In Österreich i. d. R. der VNB selbst **[extern, zu prüfen für den Pilot-VNB]** | Messwerte im bestehenden Marktprozess (keine neue Signatur in der Box) | Liste der Pilot-Zählpunkte, Zustimmung des Kunden zu 15-min-Werten | Vorschlag(v2) |
| Bilanzgruppenverantwortlicher (BGV) des Lieferanten | Trägt die Ausgleichsenergie, die ein Abruf gegenüber dem Fahrplan verursacht | Bestätigung des Empfangs (P7) | Vorankündigung und Nachmeldung der verschobenen Energie je Bilanzgruppe | Vorschlag(v2) |
| Lieferant (als betroffene Partei) | Verkauft dem Haushalt Strom. Ist betroffen, weil sich Bezug und Einspeisung verschieben | T1, T5 (wie v1) | Monatliche Summe der Abrufenergie je Zählpunkt (P7) | entschieden(v1) Rolle; Vorschlag(v2) Betroffenheit |
| Aggregator / Flexibilitätsanbieter (z. B. aFRR-Pool, Intraday-Vermarkter) | Vermarktet denselben Speicher Dritten. Nur über ein zugelassenes Modul der Box | Eigene Fahrpläne an die Box (Rolle „Aggregator“), Meldung der Poolzugehörigkeit (P8) | Sperrzeiten je Segment (P8), Abrufprotokoll der Box für seine Zählpunkte | Vorschlag(v2) |
| Übertragungsnetzbetreiber (ÜNB, APG) und vorgelagerter VNB | Koordination, wenn Abrufe in Summe MS-Netz oder Umspannwerk berühren oder Regelreserve-Pools betreffen | nichts in der Box | Tägliche Summe der geplanten Abrufleistung je Umspannwerk (Vorschlag), Information bei Konflikt mit aFRR (P8) | Vorschlag(v2); Verfahren offen |
| EDA (energiewirtschaftlicher Datenaustausch, ebUtilities) | **Kanal**, kein Akteur: transportiert Marktnachrichten zwischen VNB, Lieferant, BGV | – (Transport- und Signaturregeln von EDA) | – | Vorschlag(v2); ob ein passender Prozess existiert: **zu prüfen** |
| Trust-Anchor-Betreiber (Root-CA) | Betreibt die Root-CA offline und signiert die Sub-CAs je Rolle | Sub-CA-Zertifikate, Epochenwechsel der Root | – | offen (wer: Behörde, Branchenverein oder Prüfstelle) |

Grundsatz (Vorschlag(v2)): Der Aggregator erhält **keinen** Schlüssel, der Abrufe des VNB übersteuern kann. Er ist in der Box eine Rolle unterhalb von „Mindestreserve für Abrufe“ und oberhalb der Haushaltspräferenzen, aber nur mit Zustimmung des Haushalts.

### 1a. Speicherklassen: Haushalt, Gewerbe, Großspeicher – Vorschlag(v2.1)

Die Challenge umfasst Speicher vom Haushalt bis zum Gewerbestandort. Prozesse P1–P10 und die Abrufnachricht (Abschn. 6.4) gelten für alle Klassen; es ändern sich Kanal, Vertrag, Verifikation und Netzebene. Ausarbeitung mit Quellen: [grossspeicher-integration.md](../grossspeicher-integration.md).

| Merkmal | H Haushalt | G Gewerbe hinter dem Zähler | M Großspeicher |
|---|---|---|---|
| Leistung | bis 30 kW | 30–250 kW | ab 250 kW (RfG-Typ B) |
| Wirkt auf | Ortsnetztrafo, Abgang | Ortsnetztrafo, Abgang | MS-Abgang, Umspannwerk |
| Abruf über | Box: OpenADR (TOR) bzw. LoRaWAN-Broadcast | Box oder zertifiziertes Gebäude-EMS | Fernwirkung IEC 60870-5-104 oder OpenADR 3, Unicast mit Quittung **[unbestätigt für AT]** |
| Verifikation | Smart Meter + Referenz-EMS (Abschn. 7) | Smart Meter bzw. Lastgangzähler | gemeldeter Fahrplan als Baseline (P11) |
| Vertrag | Förderstufen 0–3 | Förderung oder einfacher Flexvertrag | flexibler Netzzugang nach ElWG (P12), kostenbasierte Entschädigung |
| Hauptrisiko | viele Geräte gleichzeitig | wie H | ein gestohlener Schlüssel bewegt mehrere MW: Schlüssel je Anlage, Quittung mit Plausibilitätsprüfung, Vier-Augen-Freigabe |

Neu für G und M: **P11 Flexibilitätsmeldung** (day-ahead: Fahrplan und Band [P_min, P_max] je Viertelstunde, Baseline für die Verifikation) und **P12 Flexibler Netzzugang** (Anschluss vor dem Netzausbau gegen Einspeisebegrenzung in Engpasszeiten). Details: grossspeicher-integration.md A3–A6. Gewerbe- und Großspeicher sind in der Simulation noch nicht abgebildet (offen).

**Netzspeicher des VNB – Vorschlag(v2.1):** Ein Speicher im Eigentum des VNB an einem Leitungsabschnitt (Knoten hinter dem am stärksten überlasteten Abschnitt eines Abgangs, höchstens einer je Abgang). Er ist ein Betriebsmittel des VNB wie Trafo oder Kabel, kein Kundenspeicher: keine Box, keine Förderstufe, keine Vergütung nach P5; Ansteuerung aus der Netzleittechnik des VNB. Ergebnis der Simulation (synthetisches NS-Netz, 432 Stationen, 2040 mit 50 % Wärmepumpen, Wetter 2012, ungesteuertes Laden): 170 Netzspeicher mit zusammen 24,8 MWh (im Mittel 146 kWh) senken die Stationen mit Leitungsüberlast von 101 auf 88 und die überlastete Leitungslänge von 11,0 auf 8,3 km; am Trafo ändern sie fast nichts (298 → 296 überlastete Trafos). Mit leitungsbewusst gesteuertem Laden entsteht kein Bedarf (0 Netzspeicher). Lesart: Brücke für wenige ungesteuerte Fälle, kein Ersatz für Steuerung oder Trafotausch; Kostensätze sind Platzhalter (offen). Grenzen: Ort und Größe der Netzspeicher stammen aus einem Auslegungslauf (ein Seed) mit perfekter Tagesprognose; das Netz ist synthetisch, bewertet wird nur thermisch (keine Spannung).

### 1b. Informationsaustausch (IES-Sicht) – Vorschlag(v2)

Kern des Profils: jeder Austausch zwischen zwei Akteuren mit Informationsobjekt, Prozess und Standard bzw. Kanal.

| Von → an | Informationsobjekt | Prozess | Standard / Kanal | Status |
|---|---|---|---|---|
| Trusted Authority → Box | Modulzertifikate, Firmware-Freigabe | P1, P10 | X.509, lokaler Servicekanal | Vorschlag(v2) |
| Installateur → VNB | Zählpunkt, Box-ID, Modulliste | P1, P9 | Inbetriebnahmeportal des VNB | offen |
| VNB → Box | Signierte Segmentzuweisung | P9 | LoRaWAN-Unicast (TS005-Gruppe) | Vorschlag(v2) |
| Lieferant, Einspeiseabnehmer → Box | Tarifformeln T1, T2, Abgaben T5 | P2 | signiert, bei Vertragsbeginn | entschieden(v1) |
| Price Authority → alle Boxen | Preisliste T4 (96 Viertelstunden) | P2 | LoRaWAN-Multicast, TS004-Fragmente | Vorschlag(v2) |
| VNB → Boxen eines Segments | Testabruf / Engpassabruf (Felder Abschn. 6.4) | P3, P4 | OpenADR-Event (TOR) oder LoRaWAN-Multicast | Vorschlag(v2) |
| Box → Wechselrichter | S1–S5 (Sollwert, Grenzen, Rampe, Rückfall) | P4, P6 | SunSpec Modbus, EEBUS LPC/LPP, IEEE 2030.5 (Abschn. 4) | Vorschlag(v2) |
| Wechselrichter → Box | R1–R5 (Leistung, SOC, Zustand, Typschild) | P3–P5 | wie oben | Vorschlag(v2) |
| Smart-Meter-Backend → VNB | 15-min-Werte | P3, P5 | bestehender Messprozess, Opt-in | Vorschlag(v2) |
| Box → VNB | Präferenzen, SOC-Verlauf (signiert) | P5 | IP-Modul oder Servicekontakt | Vorschlag(v2) |
| VNB → Haushalt | Vergütungsnachweis, Gutschrift | P5 | Netzrechnung, Portal | Vorschlag(v2) |
| VNB → BGV, Lieferant | Vor- und Nachmeldung je Bilanzgruppe und Viertelstunde | P7 | EDA oder bilateral | offen |
| Aggregator ↔ VNB | Poolzugehörigkeit ↔ Sperrfenster je Segment | P8 | nicht festgelegt | offen |
| Sub-CA → alle Boxen | Epochen- und Widerrufsnachricht | P10 | LoRaWAN-Multicast, 3× in 24 h | Vorschlag(v2) |
| VNB → Großspeicher | Abruf mit Quittung | P4, P11 | IEC 60870-5-104 oder OpenADR 3 | Vorschlag(v2.1), unbestätigt |

Ablauf P4 und P5:

```mermaid
sequenceDiagram
    participant VNB
    participant BGV as BGV / Aggregator
    participant Box as Box (je Haushalt)
    participant WR as Wechselrichter
    participant SM as Smart-Meter-Backend
    VNB->>VNB: Engpass am Trafo erkannt, Abruf im HSM signiert
    VNB->>BGV: Vorankündigung (P7), Sperrfenster (P8)
    VNB-->>Box: Abruf je Segment (Multicast, zweimal)
    Box->>Box: Signatur, Rolle, Segment, Sequenz, Ablauf, harte Grenzen prüfen
    Box->>WR: nach Zufallsverzögerung Rampe auf Sollwert (S1)
    WR-->>Box: Leistung, SOC (R1, R2)
    Box->>WR: Ende: Endversatz, Rampe zurück in den Eigenverbrauch
    SM->>VNB: 15-min-Werte (D+1)
    VNB->>VNB: Referenz-EMS rechnet Kontrafaktum, Vergleichsgruppe
    VNB->>Box: (Haushalt) monatliche Gutschrift
    VNB->>BGV: Nachmeldung der gemessenen Verschiebung (P7)
```

**Konformität** (Vorschlag(v2)): Box und VNB-Systeme werden an einem gemeinsamen Testtag gegen veröffentlichte Testnachrichten geprüft (gültig, abgelaufen, wiederholt, falsches Segment, falsche Rolle, über den Grenzen); nur die gültige Nachricht darf wirken. Wechselrichter-Schnittstellen werden gegen S1–S5 und R1–R5 (Abschn. 4.1) getestet.

---

## 2. Prozesse (IEC-62559-2-Stil, verkürzt)

Die Tabellen sind Kurzfassungen. Sequenzdiagramme und die vollständige Vorlage nach IEC 62559-2 **[extern]** folgen im Pilotdokument (offen).

### P4 Engpassabruf, erweitert um Endrampe – Vorschlag(v2)

| Feld | Inhalt |
|---|---|
| Ziel | Last bzw. Einspeisung im Segment für eine begrenzte Zeit verschieben, ohne neue Spitzen beim Start **oder Ende** |
| Auslöser | Prognostizierter oder gemessener Engpass am Ortsnetztrafo bzw. Abgang |
| Akteure | VNB (signiert), Box, Wechselrichter, BGV (P7), Aggregator (P8) |
| Vorbedingungen | Box im Segment registriert (P9), gültiger VNB-Schlüssel (P10), Uhr synchron (Abschn. 5.5), Tagesgrenzen nicht erschöpft (Abschn. 3) |
| Ablauf | 1. VNB erzeugt eine Abrufnachricht je Segment (Abschn. 6.4) im HSM. 2. Vorankündigung an BGV (P7) und Sperre an Aggregatoren (P8). 3. LoRaWAN-Multicast an die Segmentgruppe, zweimal gesendet. 4. Box prüft Signatur, Rolle, Segment, Sequenz, Ablauf, Grenzen. 5. Start nach Zufallsverzögerung U(0, Startfenster), Rampe ≤ Rampenrate. 6. Halten des Sollwerts im Rahmen der SOC-Grenzen. 7. **Ende:** jede Box zieht einen Endversatz U(0, Endfenster) und fährt mit derselben Rampenrate auf den Eigenverbrauchs-Sollwert zurück. 8. Box protokolliert lokal. |
| Nachbedingung | Segment wieder im Eigenverbrauch, gestaffelt über das Endfenster. Abruf im Protokoll |
| Fehlerfälle | Signatur ungültig → ignorieren, Zähler „verworfen“ erhöhen. Nachricht verloren → Box handelt nicht (kein Schaden). Ablauf während des Abrufs → Endrampe wie Schritt 7. SOC-Grenze erreicht → Box hält die Grenze, fährt mit Rampe weg. Tagesgrenze erreicht → Abruf abgelehnt |

**Abruf je Abgang – Vorschlag(v2.1):** Ein Segment ist entweder ein Ortsnetztrafo oder ein Abgang dieses Trafos. Liegt der Engpass an einem Leitungsabschnitt, ruft der VNB nur die Speicher hinter diesem Abschnitt ab (Segment-ID des Abgangs); liegt er am Trafo, alle Speicher des Trafos. Die Abrufnachricht (Abschn. 6.4) bleibt gleich, nur die Segment-ID zeigt auf den Abgang. Grundlage aus gridsim (synthetisches NS-Netz, 432 Stationen, Modellwerte; gesteuert wird dort das Laden der E-Autos, nicht Heimspeicher): Der erste Engpass ist fast überall der Trafo (2040 mit 50 % Wärmepumpen, ungesteuert, Wetter 2012: Trafo zuerst 214, Leitung zuerst 11, beide 89 von 432 Stationen). Gesteuertes Laden der E-Autos, das nur den Trafo kennt, lässt 40 Stationen mit Leitungsüberlast; leitungsbewusst gesteuert (Trafo **und** jeder Abschnitt) sind es 0, bei gleicher ungeladener Energie (280 MWh). Abrufe und Steuerung müssen daher den Abgang adressieren können, auch wenn der Trafo der häufigere Engpass ist. Abrufe von Heimspeichern je Abgang sind daraus abgeleitet, nicht simuliert (gridsim hat keine Abruflogik für Heimspeicher). Grenzen der Zahlen: Trafo-Bemessungsleistungen kommen aus einer Faustregel (2–3 kVA je Wohnung), ein Trafo eine Stufe größer verschiebt Stationen von „Trafo zuerst“ zu „Leitung zuerst“; die Spannung ist nicht bewertet (an 93 von 432 Stationen, 21,5 %, halten Abgänge nur die Spannungsgrenze nicht ein); ungesteuertes Laden mit 11 kW ist eine Obergrenze.

### P7 Information der Bilanzgruppe, Fahrplankorrektur und Ausgleich – Vorschlag(v2)

| Feld | Inhalt |
|---|---|
| Ziel | Ausgleichsenergie, die Abrufe verursachen, dem richtigen BGV zuordnen und finanziell neutralisieren |
| Auslöser | Geplanter Abruf (Vorankündigung) und Abschluss der Verifikation (Nachmeldung) |
| Akteure | VNB, BGV, Lieferant, EDA als Kanal, Bilanzgruppenkoordinator (APCS) **[extern, zu prüfen, ob beteiligt]** |
| Vorbedingungen | Zuordnung Zählpunkt → Lieferant → Bilanzgruppe beim VNB vorhanden (Stammdaten) |
| Ablauf | 1. Day-ahead-Abrufe: VNB meldet bis zur Fahrplanfrist geplante Energie je Bilanzgruppe und Viertelstunde (Summenprofil, keine Einzelkunden). 2. Kurzfristige Abrufe: Meldung sobald gesendet. 3. Nach Verifikation (P5, D+1 bis D+3): Nachmeldung der gemessenen Verschiebung je Bilanzgruppe. 4. Monatlich: Ausgleichszahlung VNB → BGV nach Ausgleichsenergiepreis für die gemessene Abweichung, oder Gutschrift in Energie. |
| Nachbedingung | BGV ist für Abrufe finanziell neutral. Lieferant kennt die Abrufenergie je Zählpunkt |
| Fehlerfälle | Lieferantenwechsel im Monat → Zuordnung nach Stichtag der Viertelstunde. Meldung verspätet → Ausgleich nur nach Nachmeldung. Streit über Menge → Smart-Meter-Wert und Referenzalgorithmus (Abschn. 7) entscheiden |

Offen: ob die Ausgleichszahlung über EDA, bilateral oder über eine Korrektur im Clearing läuft. Im Pilot genügt bilaterale Abrechnung mit einem teilnehmenden Lieferanten.

### P8 Konfliktauflösung mit Drittvermarktung (Aggregator) – Vorschlag(v2)

| Feld | Inhalt |
|---|---|
| Ziel | Verhindern, dass ein VNB-Abruf und ein Regelreserve- oder Intraday-Fahrplan gegeneinander arbeiten |
| Auslöser | Ein Speicher ist bei einem Aggregator angemeldet, oder ein VNB-Abruf kollidiert mit einem Aggregator-Fahrplan |
| Akteure | VNB, Aggregator, Box, ÜNB (bei aFRR) |
| Vorbedingungen | Haushalt hat dem Aggregator-Modul zugestimmt. Aggregator meldet Poolzugehörigkeit je Zählpunkt beim VNB (Register) |
| Ablauf | 1. Day-ahead: VNB veröffentlicht je Segment „Sperrfenster“ (Ampel gelb/rot) bis zur Gate-Closure der Regelreserve. 2. Aggregator plant in roten Fenstern keine Leistung in Gegenrichtung des Engpasses. 3. Kurzfristiger Abruf in einem nicht angekündigten Fenster: Box folgt dem VNB (Priorität), meldet lokal den Konflikt; der VNB informiert Aggregator und ÜNB. 4. Der Aggregator wird für nachweislich entgangene Leistung nicht pönalisiert (Regel mit ÜNB: **offen**). |
| Nachbedingung | Kein Gegeneinander-Fahren im Segment. Konflikte sind protokolliert |
| Fehlerfälle | Aggregator ignoriert Sperrfenster → Box verweigert den Aggregator-Fahrplan in roten Fenstern lokal. Gleiche Richtung (beide wollen laden) → kein Konflikt, beide werden bedient, Vergütung nur einmal (Abschn. 7) |

### P9 Segmentzuordnung und Umschaltung – Vorschlag(v2)

| Feld | Inhalt |
|---|---|
| Ziel | Jede Box weiß, zu welchem Segment sie gehört, und reagiert nur auf Abrufe dieses Segments |
| Auslöser | Inbetriebnahme (P1), dauerhafte Netzänderung, vorübergehende Umschaltung |
| Akteure | VNB (GIS/Netzleitsystem), Box, LoRaWAN-Netzserver |
| Vorbedingungen | Zählpunkt der Box bekannt; Segment-ID im GIS des VNB |
| Ablauf | 1. Inbetriebnahme: Installateur erfasst Zählpunktnummer, VNB ermittelt das Segment aus Zählpunkt → Abgang → Trafo (nicht aus Koordinaten); die Box erhält die Segment-ID ihres Trafos **und** ihres Abgangs (Abruf je Abgang, siehe P4; **offen:** Gruppenzahl je Box, d. h. zwei Multicast-Gruppen nach TS005 und ihre Wirkung auf die LoRaWAN-Kapazität, Abschn. 6). 2. VNB signiert eine **Segmentzuweisung** (Box-ID, Segment-ID, gültig ab, Sequenz) und fügt die Box der Multicast-Gruppe des Segments hinzu (TS005, unicast, einmalig). 3. Dauerhafte Änderung: neue Zuweisung, alte Gruppe verlassen. 4. **Vorübergehende Umschaltung** (Störung, Wartung): Box behält die Zuordnung. VNB sendet an das betroffene Segment eine signierte **Segmentsperre** (keine Abrufe bis Zeitpunkt X) bzw. adressiert die Abrufe an das neue Speisesegment über eine signierte **Alias-Nachricht** (Segment A gilt bis X als Teil von B). |
| Nachbedingung | Box handelt nur auf Abrufe mit eigener Segment-ID (Trafo oder Abgang) oder gültigem Alias |
| Fehlerfälle | Zuordnung im GIS falsch → erkannt über Testabruf (P3): Trafomessung reagiert nicht wie erwartet. Box ohne Zuweisung → nur Eigenverbrauch und Tagespreise |

Auch bei falscher Zuordnung bleiben die harten Grenzen (Abschn. 3) wirksam, der Schaden ist begrenzt.

### P10 Zertifikatswiderruf, Schlüsselwechsel, Außerbetriebnahme und Tausch – Vorschlag(v2)

| Feld | Inhalt |
|---|---|
| Ziel | Kompromittierte Schlüssel schnell unwirksam machen, Schlüssel planmäßig wechseln, Boxen sauber ab- und anmelden |
| Auslöser | Verdacht auf Kompromittierung; planmäßiger Wechsel (jährlich); Defekt, Umzug, Kündigung |
| Akteure | Sub-CA der Rolle, VNB, Trusted Authority, Box, Installateur, Förderstelle |
| Vorbedingungen | Box kennt die Widerrufsschlüssel der Sub-CAs (bei Herstellung eingebracht) |
| Ablauf | **Widerruf:** Sub-CA signiert mit dem eigenen Widerrufsschlüssel eine Epochennachricht (Rolle, neue Mindestepoche, optional Liste von Schlüssel-IDs); Broadcast an alle Gruppen, dreimal über 24 h. **Wechsel:** neuer öffentlicher Schlüssel mit Epoche, von der Sub-CA signiert, vorab verteilt; Umschaltung zu einem signierten Zeitpunkt. **Außerbetriebnahme:** VNB widerruft die Segmentzuweisung, Box löscht Gruppenschlüssel, Förderstelle wird informiert. **Tausch:** neue Box durchläuft P1 und P9; der Zählpunkt bleibt, Vergütungs- und Förderhistorie hängen am Zählpunkt, nicht an der Box |
| Nachbedingung | Nachrichten älterer Epochen werden verworfen. Ausgebaute Box kann nichts mehr auslösen |
| Fehlerfälle | Box verpasst den Widerruf → nächste Nachricht trägt die Epoche im Kopf, die Box lernt sie beim nächsten Empfang. Root kompromittiert → nur Neuprovisionierung vor Ort (Restrisiko, offen) |

---

## 3. Harte Grenzen in der Box (durch keine Signatur aufhebbar)

Die Werte stehen in der zugelassenen Firmware und sind nur über ein Firmware-Update der Trusted Authority änderbar, nicht über Nachrichten. Ziel: Auch ein gestohlener VNB-Schlüssel kann nur eine begrenzte, langsame und zeitlich gestreute Wirkung erzeugen (F-15). Alle Werte Vorschlag(v2).

| Grenze | Vorschlagswert | Begründung |
|---|---|---|
| Max. Abrufe je Tag (inkl. Testabruf) | 3 | Mittags-Einspeisespitze plus Abendspitze plus Reserve; mehr deutet auf Fehler oder Missbrauch |
| Max. Testabrufe | 1 je 7 Tage, Dauer ≤ 15 min | v1 sieht monatlich vor; wöchentlich reicht für die Statistik im Pilot |
| Max. Dauer je Abruf | 3 h | Ein 10-kWh-Speicher mit 3–5 kW ist nach 2–3 h voll bzw. leer |
| Max. Abrufdauer je Tag | 4 h | Deckt die PV-Spitze ca. 11–15 Uhr ab |
| Mindestabstand zwischen Abrufen | 30 min | Verhindert Pendeln zwischen Laden und Entladen |
| Max. verschobene Energie je Tag | 1 Vollzyklus der Nennkapazität | Begrenzt Verschleiß und Vergütungsrisiko |
| Rampenrate (Start, Ende, Fallback) | ≤ 10 % P_n/min | Größenordnung der Wiederzuschaltrampe in EN 50549-1 **[extern, zu prüfen]**; 10 min für einen vollen Wechsel |
| Startverzögerung | U(0, s) mit 60 s ≤ s ≤ 300 s | Streut den Start über mehrere Minuten. Gilt nur für Speicherabrufe; PV-Sollwerte nach TOR (1 min) setzt die Box ohne Verzögerung um |
| Endversatz | U(0, e), e ≥ 300 s, Standard 900 s | Verteilt den Rücksprung in den Eigenverbrauch über eine Viertelstunde (E5) |
| Fallback-Eintritt (P6) | Zustand halten bis Abrufende bzw. 15 min, dann Endrampe | Kein Sprung bei Ausfall des Kanals |
| Gestaffelte Rückkehr in Eigenverbrauch | Slot = Hash(Box-ID) mod 15 min + U(0, 120 s) | Deterministisch verteilt, auch wenn alle Boxen gleichzeitig ausfallen |
| Max. Zielleistung | ≤ P_n Wechselrichter, SOC-Grenzen 10–95 % | Herstellergrenzen bleiben maßgeblich |
| Notstromreserve | nie unterschritten | entschieden(v1) |
| Max. Nachrichten mit gültiger Signatur je Stunde | 6 | Wiederholungen und Sperren eingeschlossen; mehr gilt als Angriff und wird bis zur nächsten Epoche protokolliert und ignoriert |
| Plausibilitätsfenster Preise | −50 … +100 ct/kWh | entschieden(v1) |

---

## 4. Mindestprofil der Wechselrichter-Schnittstelle

Die Box spricht den Wechselrichter lokal (RS-485 oder Ethernet) an. Ein Hersteller-Cloudpfad ist nicht zulässig (entschieden(v1); passt zu „keine Drittsysteme“ in der TOR). Pflicht ist **eine** der drei Optionen; SunSpec Modbus ist Vorschlag(v2) als Referenz für die Zertifizierung.

### 4.1 Pflichtwerte

| Nr. | Funktion | Art | Pflicht |
|---|---|---|---|
| S1 | Wirkleistungs-Sollwert Speicher (Laden/Entladen, W, mit Vorzeichen) | Sollwert | ja |
| S2 | Begrenzung Einspeisung am Netzanschluss (W) | Sollwert | ja |
| S3 | Begrenzung Bezug am Netzanschluss (W) | Sollwert | ja (Stufe 2+) |
| S4 | Rampenrate (%P_n/min) | Sollwert | ja, sonst rampt die Box selbst in ≤ 10-s-Schritten |
| S5 | Rückfallwert und Timeout bei Kommunikationsverlust | Sollwert | ja |
| R1 | Wirkleistung AC, Blindleistung, Spannung | Rückmeldung | ja |
| R2 | Ladezustand (SOC), nutzbare Energie, max. Lade-/Entladeleistung | Rückmeldung | ja |
| R3 | Betriebszustand, Fehlercodes, aktiver Steuermodus | Rückmeldung | ja |
| R4 | Typschild: Hersteller, Modell, Seriennummer, Firmware, P_n, E_n | Rückmeldung | ja |
| R5 | Q(U)/cos φ-Einstellung | Rückmeldung | ja, nur lesend (TOR: cos φ = 1 Standard) |

### 4.2 Abbildung auf Standards

| Pflichtwert | SunSpec Modbus | EEBUS | IEEE 2030.5 |
|---|---|---|---|
| R4 Typschild | Modell 1 (Common) | Geräteklassifikation (Device Diagnosis) **zu prüfen** | DeviceInformation, DERSettings |
| R1 Messwerte | Modell 701 (DER AC Measurement) | MPC (Monitoring of Power Consumption), MGCP (Monitoring of Grid Connection Point) | DERStatus / MirrorUsagePoint **zu prüfen** |
| R2 Speicherwerte | Modell 713 (DER Storage Capacity); Altmodell 124 (Basic Storage Controls); Batteriemodell 802 | kein passender Pflicht-Use-Case bekannt **zu prüfen** | DERStatus.stateOfChargeStatus, DERCapability |
| S1 Speicher-Sollwert | Modell 704 (DER AC Controls) bzw. 124 (Lade-/Entladeraten) | keine direkte Abbildung; Ersatz über S2/S3 | DERControl opModTargetW / opModFixedW **zu prüfen** |
| S2 Einspeisegrenze | Modell 704 (Wirkleistungsbegrenzung) | LPP (Limitation of Power Production) | DERControl opModExpLimW **zu prüfen** |
| S3 Bezugsgrenze | **zu prüfen** (in 704 nicht eindeutig) | LPC (Limitation of Power Consumption) | opModImpLimW **zu prüfen** |
| S4 Rampe | Modell 704 / 703 (Enter Service, Rampe beim Zuschalten) **zu prüfen** | – | setGradW **zu prüfen** |
| S5 Rückfall | Timeout-Felder in 704 **zu prüfen**; LPC/LPP kennen Failsafe-Werte | LPC/LPP Failsafe | DefaultDERControl |
| Planung | Modell 715 (DER Control) **zu prüfen** | – | DERProgram, Ereignisse mit Zeit |

Hinweis: EEBUS LPC/LPP begrenzen Leistungen am Netzanschluss, setzen aber keinen Speicher-Sollwert. Ein Ladeabruf lässt sich nur indirekt abbilden (Einspeisegrenze nahe null zwingt das EMS zum Laden). Für Stufe 2 und 3 reicht EEBUS allein daher nicht; Vorschlag(v2): EEBUS nur für Stufe 1 zulassen. Alle Modell- und Feldnummern sind vor der Zertifizierung gegen die aktuellen SunSpec-Modelldateien bzw. die EEBUS- und 2030.5-Spezifikation zu prüfen.

---

## 5. PKI und Gerätesicherheit

### 5.1 Hierarchie – Vorschlag(v2)

| Ebene | Inhaber | Signiert | Aufbewahrung | Laufzeit |
|---|---|---|---|---|
| Root-CA | Trust-Anchor-Betreiber (offen) | Sub-CAs, Root-Epochen | offline, HSM, 2-aus-3-Zeremonie | 20 Jahre |
| Sub-CA VNB (je VNB) | VNB | Abruf-, Segment- und Sperrschlüssel des VNB | HSM | 8 Jahre |
| Sub-CA Preis | Price Authority (E-Control, offen) | T4-Schlüssel | HSM | 8 Jahre |
| Sub-CA Markt | Branchen-CA | Schlüssel von Lieferant (T1, T5), Einspeiseabnehmer (T2), Aggregator | HSM | 8 Jahre |
| Sub-CA Gerät | Trusted Authority | Hersteller-CAs → Box-Identität, Modulzertifikate | HSM | 10 Jahre |
| Sub-CA Firmware | Trusted Authority | Firmware-Signaturschlüssel je Hersteller | HSM, offline | 10 Jahre |
| Betriebsschlüssel (Abruf, Preis, T1–T3) | jeweilige Rolle | Nachrichten | HSM (VNB: Pflicht, FIPS 140-3 Level 3 oder CC EAL4+ als Richtwert) | 1 Jahr, Wechsel nach P10 |
| Widerrufsschlüssel je Sub-CA | Sub-CA | nur Epochen- und Widerrufsnachrichten | eigenes HSM, getrennt vom Betriebsschlüssel | wie Sub-CA |
| Box-Identität | Box (Secure Element) | Inbetriebnahmedaten, lokale Protokolle | Secure Element, nicht exportierbar | Lebensdauer der Box (15 Jahre) |

Autorisierung pro Segment: Das Zertifikat eines VNB-Betriebsschlüssels enthält die Netzbereichs-ID. Die Box akzeptiert Abrufe nur, wenn ihr Segment in diesem Netzbereich liegt (schließt Lücke aus F).

### 5.2 Schlüsseltypen

| Verwendung | Algorithmus | Signaturgröße | Status |
|---|---|---|---|
| Broadcast-Nachrichten (Abruf, Preis, Widerruf) | ECDSA P-256, Signatur roh r‖s | 64 B | Vorschlag(v2): Pflicht, weil verbreitete Secure Elements und HSMs P-256 unterstützen |
| Alternativ | Ed25519 | 64 B | offen; Unterstützung im gewählten Secure Element zu prüfen |
| Zertifikate in der Box | X.509 bei Inbetriebnahme über lokalen Kanal; über LoRa nur Schlüssel-ID (2 B) und Epoche | – | Vorschlag(v2) |

Über LoRa werden keine Zertifikate übertragen. Die Box kennt die öffentlichen Schlüssel ihrer Rollen aus der Inbetriebnahme oder aus signierten Schlüsselwechsel-Nachrichten (öffentlicher Schlüssel komprimiert 33 B + Schlüssel-ID 2 B + Epoche 2 B + Gültigkeit 4 B + Signatur 64 B ≈ 105 B, drei Fragmente bei SF12).

### 5.3 Widerruf über einen schmalbandigen Kanal

Keine CRL über LoRa. Stattdessen (Vorschlag(v2)):

1. **Epochenzähler je Rolle** (16 bit). Jede Nachricht trägt Schlüssel-ID und Epoche. Eine Epochennachricht des Widerrufsschlüssels hebt die Mindestepoche an; ältere Schlüssel sind sofort ungültig.
2. **Kurze Widerrufsliste**: signierte Nachricht mit bis zu 8 Schlüssel-IDs (2 B je ID) für Einzelschlüssel, z. B. eines Aggregators.
3. **Wiederholung**: Epochennachrichten werden dreimal in 24 h und danach wöchentlich gesendet. Die Box speichert die höchste gesehene Epoche persistent.

### 5.4 Replay-Schutz

- Sequenzzähler 32 bit je (Schlüssel-ID, Segment), streng monoton.
- Die Box schreibt den Zähler **vor** der Ausführung persistent (Monotonic Counter im Secure Element oder Flash mit Wear-Leveling).
- Nachrichten mit Sequenz ≤ gespeichertem Wert werden verworfen. Mit neuer Schlüssel-ID beginnt die Sequenz neu.

### 5.5 Zeitbasis

| Quelle | Einsatz | Status |
|---|---|---|
| LoRaWAN DeviceTimeReq (MAC-Befehl ab LoRaWAN 1.0.3 **[extern]**) | täglich, mit Uplink | Vorschlag(v2) Standard |
| Class-B-Beacon (GPS-Zeit) | wenn Netz Class B betreibt | Alternative |
| Application Layer Clock Sync (TS003 **[extern, zu prüfen]**) | Alternative zu DeviceTimeReq | zu prüfen |
| Signierter Zeitstempel in Abruf und Preisliste | Plausibilitätsprüfung | Vorschlag(v2) |

Regeln: Toleranz für Ablauf und Start ±60 s. Korrekturen über das Netz sind nur um ±120 s je Tag zulässig, außer bei signiertem Zeitstempel. Rückwärtssprünge über 120 s werden nicht übernommen. Der Netzserver authentifiziert DeviceTimeAns nur per MIC; die Zeit ist deshalb nicht Ende-zu-Ende gesichert, die harten Grenzen (Abschn. 3) begrenzen den Schaden.

### 5.6 Firmware

| Thema | Vorschlag(v2) |
|---|---|
| Secure Boot | ROM → Bootloader → Anwendung, jede Stufe prüft die Signatur der nächsten |
| Signierte Updates | Signatur durch Hersteller-Firmwareschlüssel **und** Freigabe der Trusted Authority (zwei Signaturen) |
| Rollback-Schutz | Versionszähler in eFuse bzw. Monotonic Counter; A/B-Partitionen mit automatischem Rückfall bei Startfehler |
| Update-Kanal | LTE- oder Ethernet-Modul, sonst Servicetermin vor Ort. **Nicht über LoRa:** ein 256-kB-Image braucht bei SF9 ca. 2 341 Fragmente bzw. 0,44 h reine Sendezeit, bei SF12 ca. 5 462 Fragmente bzw. 4,2 h; mit 10 % Duty Cycle sind das 4,4 h bzw. 42 h Sperre des Downlinks je Gateway, ohne Redundanz |
| Grenzen aus Abschn. 3 | nur durch Update änderbar, Änderungen öffentlich dokumentiert |

Bedrohungsanalyse nach IEC 62443 bzw. im NIS2-Kontext des VNB **[extern]**: offen, Pflicht vor Phase 2 des Pilots.

---

## 6. LoRaWAN-Kapazität (EU868)

### 6.1 Formel

Semtech-Formel für die Sendezeit (Time on Air) **[extern, Semtech SX127x-Datenblatt / AN1200.13]**:

```
T_sym      = 2^SF / BW
T_preamble = (n_preamble + 4,25) · T_sym
n_payload  = 8 + max( ceil( (8·PL − 4·SF + 28 + 16·CRC − 20·IH) / (4·(SF − 2·DE)) ) · (CR + 4), 0 )
T_air      = T_preamble + n_payload · T_sym
```

Parameter: BW = 125 kHz, CR = 1 (4/5), n_preamble = 8, expliziter Header (IH = 0), CRC = 1, DE = 1 bei SF11/12 (Low Data Rate Optimisation), sonst 0.
PL ist die PHY-Nutzlast. LoRaWAN fügt zur Anwendungsnutzlast 13 B hinzu (MHDR 1 + FHDR 7 ohne FOpts + FPort 1 + MIC 4).
Hinweis: LoRaWAN-Downlinks werden ohne Nutzlast-CRC gesendet. Für die hier gerechneten Größen ändert das wegen der Aufrundung nichts (geprüft).

Maximale Anwendungsnutzlast EU868 **[extern, RP002]**: SF12 (DR0) 51 B, SF9 (DR3) 115 B, SF7 (DR5) 222 B.

### 6.2 Ergebnisse (mit Python gerechnet)

| Fall | PL (PHY) | T_sym | Symbole Nutzlast | T_air |
|---|---|---|---|---|
| 51 B bei SF12, PL = 51 (wie vorgegeben) | 51 B | 32,768 ms | 63 | **2 465,8 ms** |
| 51 B Anwendung + 13 B LoRaWAN, SF12 | 64 B | 32,768 ms | 73 | **2 793,5 ms** |
| 222 B bei SF7, PL = 222 | 222 B | 1,024 ms | 328 | **348,4 ms** |
| 222 B Anwendung + 13 B, SF7 | 235 B | 1,024 ms | 348 | **368,9 ms** |
| 115 B Anwendung + 13 B, SF9 | 128 B | 4,096 ms | 153 | 676,9 ms |

### 6.3 Preisliste T4 (~180 B inkl. 64 B Signatur)

Fragmentierung nach TS004 (Fragmented Data Block Transport) **[extern]**, 3 B Kopf je Fragment: Nutzdaten je Fragment 48 B (SF12) bzw. 112 B (SF9).

| SF | Fragmente | T_air je volles Fragment | Gesamt ohne Redundanz | mit +50 % FEC-Fragmenten |
|---|---|---|---|---|
| SF12 | 4 (3 × 48 B + 36 B) | 2,79 s | **10,85 s** | 6 Fragmente, ≈ 16,8 s |
| SF9 | 2 (112 B + 68 B) | 0,68 s | **1,15 s** | 3 Fragmente, ≈ 2,0 s |

Ob 96 Viertelstundenwerte in ~116 B passen (≈ 9,7 bit je Wert), hängt von Delta-Codierung und Quantisierung ab; bleibt **offen** und ist im Pilot mit realen EPEX-Reihen zu prüfen.

### 6.4 Abrufnachricht je Segment

| Feld | Bytes |
|---|---|
| Nachrichtentyp und Version | 1 |
| Segment-ID | 4 |
| Sequenznummer | 4 |
| Schlüssel-ID und Epoche | 2 |
| Startzeit (Unix-Sekunden) | 4 |
| Max. Dauer (min) | 2 |
| Ablauf relativ zum Start (min) | 2 |
| Richtung und Modus | 1 |
| Zielleistung je Box (‰ von P_n oder W) | 2 |
| Startfenster (s) | 2 |
| Endfenster (s) | 2 |
| Rampenrate (%P_n/min) | 1 |
| SOC-Grenzen min/max | 2 |
| Grundcode | 1 |
| Flags (Test, vergütet, Wiederholung) | 1 |
| **Summe Inhalt** | **31** |
| Signatur ECDSA P-256 | 64 |
| **Gesamt** | **95** |

| SF | Rahmen | T_air |
|---|---|---|
| SF12 | 2 Fragmente (48 + 47 B Daten) | 5,59 s |
| SF9 | 1 Rahmen (95 ≤ 115 B) | 0,59 s |
| SF7 | 1 Rahmen | 0,18 s |

### 6.5 Duty Cycle und Nachrichten je Gateway und Stunde

Downlinks im Unterband 869,4–869,65 MHz (869,525 MHz, RX2-Standardfrequenz) dürfen 10 % der Zeit senden, im Unterband g1 (868,0–868,6 MHz) 1 % **[extern, ETSI EN 300 220 / ERC REC 70-03, zu prüfen im Detail]**. Das ergibt 360 s bzw. 36 s Sendezeit je Stunde.

| Nachricht | SF | T_air | max./h bei 10 % | max./h bei 1 % |
|---|---|---|---|---|
| Abruf (95 B) | SF12 | 5,59 s | **64** | 6 |
| Abruf (95 B) | SF9 | 0,59 s | **605** | 60 |
| Preisliste (180 B) | SF12 | 10,85 s | **33** | 3 |
| Preisliste (180 B) | SF9 | 1,15 s | **313** | 31 |
| Leere Quittung (ACK, 13 B PHY) | SF12 | 1,16 s | 311 | 31 |

Lesart: Ein Gateway, das 20 Segmente versorgt, braucht für einen Abruf in allen Segmenten mit zweifacher Wiederholung bei SF12 20 × 2 × 5,59 s ≈ 224 s, also 62 % des Stundenbudgets. Das geht für Broadcast. Eine Quittung je Box ginge bei 311 ACKs je Stunde nicht: Ein Segment mit 60 Boxen braucht für Quittungen allein ein Fünftel des Budgets, und während des Sendens empfängt das Gateway nicht (Halbduplex).

### 6.6 Schluss: LoRa nur für Broadcast – Vorschlag(v2)

| Aufgabe | Kanal | Begründung |
|---|---|---|
| Abrufe, Preise, Epochen, Sperren | LoRaWAN Class-C-Multicast (TS005) | Ein Rahmen pro Segment, skaliert mit Segmenten statt Boxen |
| Quittungen einzelner Boxen | keine | Downlink-Budget und Halbduplex (Tabelle 6.5) |
| Messwerte für Verifikation und Vergütung | Smart-Meter-Backend des VNB (15-min-Werte, D+1) | Geeicht, vorhanden, kein Funkbudget, keine Box als Partei |
| Lebenszeichen | optional ein unbestätigter Uplink ≤ 11 B je Tag | Erreichbarkeit für die Förderraten (v1) |
| Firmware, Zertifikate, Diagnose | lokaler Service oder LTE/Ethernet-Modul | Volumen (Abschn. 5.6) |

Ein signierter Messwert-Uplink (ca. 20 B + 64 B Signatur) braucht bei SF12 zwei Rahmen, 5,6 s. Bei reinem ALOHA (max. ca. 18 % Kanalauslastung) und 3 Kanälen schafft ein Gateway rechnerisch ≈ 350 solcher Uplinks je Stunde, ohne Wiederholungen. Für einige tausend Boxen nach jedem Abruf reicht das nicht. Dazu kommt, dass der eigene Zähler der Box ohne MID-/MEG-Konformität **[extern]** nicht abrechnungsrelevant ist.

---

## 7. Verifikation und Vergütung v2

Prinzip entschieden(v1): Kunde nie schlechter gestellt; Vergütung = max(0, Mehrkosten Bezug − Mehrerlös Einspeisung) + Verschleißpauschale × verschobene Energie + Abrufentgelt. Neu (F-18): Die Box ist nicht mehr allein für das Kontrafaktum zuständig.

| Baustein | Inhalt | Status |
|---|---|---|
| Referenz-EMS | Deterministischer, offengelegter Algorithmus (Quelltext und Testvektoren veröffentlicht), Eingaben: Präferenzen, Preise T1–T5, SOC zu Abrufbeginn, 15-min-Smart-Meter-Werte. Gleiche Eingaben → gleiches Ergebnis in Box und Backend | Vorschlag(v2) |
| Berechnung | Backend des VNB rechnet das Kontrafaktum selbst. Die Box liefert nur Eingaben (Präferenzen, SOC-Verlauf), signiert mit Box-Identität, beim nächsten Servicekontakt oder über das optionale IP-Modul | Vorschlag(v2) |
| Plausibilisierung | (a) Smart-Meter-Saldo vor/während/nach dem Abruf; (b) Vergleichsgruppe: Boxen desselben Segments bzw. ähnlicher Segmente ohne Abruf an diesem Tag (z. B. per Los ausgeschlossene 10 %); (c) Trafomessung im Segment | Vorschlag(v2) |
| Grenzen für Präferenzen | Präferenzen von vor 24 h (v1). Zusätzlich: höchstens 2 Änderungen je Woche gehen in die Vergütung ein; Preisschwellen nur im Bereich ±50 % des Monatsmittels; Vergütung höchstens das 1,5-Fache des Medians der Vergleichsgruppe, darüber manuelle Prüfung | Vorschlag(v2) |
| Verschleißpauschale | 5 ct/kWh (v1 Vorschlag). Begründung: 500 €/kWh über 6 000 Zyklen ≈ 8 ct/kWh je Zyklus brutto, Abrufe verursachen nur einen Teil zusätzlicher Zyklen | Vorschlag(v2) |
| Doppelvergütung | Vergütet ein Aggregator dieselbe Energie (P8, gleiche Richtung), zahlt der VNB nur die Mehrkosten, kein Abrufentgelt | Vorschlag(v2) |
| Abrufentgelt | Höhe | offen |
| Streitfall | 1. Kunde sieht Berechnung im Portal (Eingaben, Ergebnis, Referenzversion). 2. Einspruch binnen 60 Tagen. 3. VNB rechnet mit Referenz-EMS nach und begründet schriftlich. 4. Danach Schlichtung bei E-Control **[extern, Zuständigkeit für diesen Vertragstyp zu prüfen]** | Vorschlag(v2) |

---

## 8. Regulatorischer Pfad

| Mechanismus | Heute gedeckt? | Grundlage / was fehlt | Status |
|---|---|---|---|
| Steuerbarkeit von PV (Erzeugungsanlagen) | ja, für Anlagen ab 1.6.2026 | § 76 ElWG; TOR Typ A V1.4 Kap. 5.4.1: OpenADR (IEC 62746-10-1), keine Drittsysteme, Sollwert in 1 min, Rückfall 70 % (§ 101 Abs. 2 ElWG) **[extern, geprüft]**. Leistungsschwelle (Sekundärquellen: 7 kW) **zu prüfen** | entschieden(v1) als Basis |
| Steuerbarkeit von Heimspeichern | nein (nicht als Speicher) | Weg über Fördervertrag (zivilrechtlich). Ob ein Speicher in einer PV-Anlage unter § 76 ElWG fällt, **zu prüfen** | entschieden(v1) Förderbedingung |
| Signalweg hinter dem Anschlusspunkt | ja | § 76 Abs. 3 ElWG: Pflicht des Netzbenutzers **[extern, geprüft]**; Box erfüllt das in der Kundenanlage | Vorschlag(v2) |
| LoRaWAN als zusätzlicher Kanal | nicht geregelt | TOR sieht OpenADR vor; LoRa nur für Speicher und nur ergänzend. Abstimmung mit dem VNB, ob der OpenADR-Kanal selbst auch über die Box laufen darf | offen |
| 15-min-Werte für Verifikation | ja, mit Zustimmung | Opt-in des Kunden für Viertelstundenwerte **[extern, Paragraph im ElWG zu prüfen]**; Zustimmung als Förderbedingung | Vorschlag(v2) |
| Ausgleich gegenüber BGV | teilweise | bilateraler Vertrag möglich; Abbildung in EDA-Prozessen **zu prüfen** | Vorschlag(v2) |
| Segmentspezifischer Netztarif (T3d) | nein | Netzentgelte je Netzebene und Netzbereich per SNE-VO; räumliche Differenzierung je Ortsnetzstation braucht Verordnungsänderung, Gleichbehandlung zu klären. Im Pilot nur als Gutschrift aus dem Pilotvertrag | offen |
| E-Control als Price Authority | nein | Mandat fehlt; Weitergabe von EPEX-Preisen braucht Lizenz. Im Pilot: VNB oder Lieferant mit eigener EPEX-Lizenz signiert T4 | offen |
| Entladung des Speichers ins Netz (Stufe 3) | nein, nicht abrechenbar | Messung muss gespeicherte PV-Energie von Netzstrom trennen; Regeln für Speicher-Einspeisung **zu prüfen** | offen |
| Abrechnungsrelevanter Box-Zähler | nein | MID/MEG-Konformität nötig; v2 verzichtet darauf und nutzt den Smart Meter | Vorschlag(v2) |
| Regelreserve-Konflikt | nein | Regel mit APG zu Pönalen bei VNB-Abruf fehlt | offen |
| Netz-Cybersicherheit | teilweise | NIS2-Umsetzung beim VNB **[extern, Stand zu prüfen]** | offen |

---

## 9. Pilotplan Steyr – Vorschlag(v2)

Netzbetreiber im Pilotgebiet: **zu prüfen** (Netz OÖ bzw. lokaler Netzbetreiber). Segmentauswahl nach Messdaten des VNB, nicht nach dem synthetischen Modell der Demo.

### 9.1 Phasen

| Phase | Dauer | Inhalt | Exit-Kriterium |
|---|---|---|---|
| 0 Vorbereitung | 4 Monate | Segmentauswahl (2–3 Segmente mit gemessener Einspeisespitze), Verträge (Kunden, ein Lieferant/BGV, ggf. ein Aggregator), PKI-Test-Root, Labortest Box ↔ 2 Wechselrichterfamilien (SunSpec und EEBUS), Bedrohungsanalyse | Labortest aller Prozesse, inkl. P6 und P10 |
| 1 Inbetriebnahme | 2 Monate | 30–60 Boxen, P1, P9; Trafomessung in jedem Segment; Vergleichsgruppe per Los | ≥ 90 % der Boxen registriert und erreichbar |
| 2 Testabrufe | 3 Monate (Frühjahr) | wöchentliche Testabrufe P3, Kalibrierung der Rampen und Fenster, Widerruf und Schlüsselwechsel einmal real durchspielen | Antwortzuverlässigkeit ≥ 80 % |
| 3 Engpassabrufe mit Vergütung | 5 Monate (Mai–September) | P4, P5, P7, P8 im Echtbetrieb, monatliche Gutschrift | KPIs in 9.2 |
| 4 Auswertung | 2 Monate | Bericht, Kosten je kW gegen Netzausbau und Abregelung, Profil v3 | – |

Gesamtdauer: ca. 16 Monate, davon eine volle PV-Saison.

### 9.2 Erfolgskennzahlen

| KPI | Definition | Ziel |
|---|---|---|
| Antwortzuverlässigkeit | Anteil der Boxen, die einen gültigen Abruf binnen Startfenster + 10 min erkennbar umsetzen (Smart Meter) | ≥ 90 % |
| Gelieferte gegen angeforderte Leistung | Mittelwert geliefert/angefordert je Abruf am Trafo, bereinigt um Vergleichsgruppe | ≥ 80 %, Streuung berichtet |
| Rebound | Max. Leistungsanstieg am Trafo in 30 min nach Abrufende gegenüber Vergleichsgruppe | ≤ 10 % der verschobenen Leistung |
| Kostenneutralität der Kunden | Anteil der Kunden, deren Rechnung inkl. Gutschrift nicht über dem Kontrafaktum liegt | 100 %, Streitfälle ≤ 5 % |
| Ausgleichsenergie | gemeldete gegen gemessene Abrufenergie je Bilanzgruppe | Abweichung ≤ 10 % |
| Sicherheit | erfolgreiche Annahme ungültiger, abgelaufener oder wiederholter Nachrichten im Test | 0 |
| Funk | Anteil der Abrufe, die alle Boxen eines Segments erreichen (aus Lebenszeichen und Smart Meter geschätzt) | ≥ 95 % |
| Kosten | € je kW verlässlicher Flexibilität und Jahr gegen Trafotausch und Abregelung | berichtet, kein Zielwert |

---

## 10. Offene Punkte (Kurzliste)

1. Betreiber der Root-CA und der Price Authority.
2. Höhe des Abrufentgelts; Förderträger und Budget.
3. Regel mit APG für Aggregatoren bei VNB-Abruf.
4. Codierung der Preisliste in ~116 B.
5. Ob OpenADR nach TOR und LoRa-Broadcast im selben Kernmodul zugelassen werden.
6. Alle mit **zu prüfen** markierten Modellnummern und Paragraphen.

## Quellen

- TOR Stromerzeugungsanlagen Typ A V1.4, Kap. 5.4.1, S. 35–36 **[extern, geprüft]**; Arbeitskopie auf dem Server: `/data/infra-kg-austria/work/netzmodell-recherche-2026-10-24/tor_typ_a.txt`.
- Internes technisches Gutachten vom 24.10.2026 (nicht im Repository).
- Nicht im Rahmen dieses Entwurfs geprüft, aus Fachwissen: LoRaWAN Regional Parameters RP002, TS003, TS004, TS005; Semtech-Formel zur Sendezeit; ETSI EN 300 220; SunSpec-Modelle 1, 124, 701–705, 713, 715, 802; EEBUS LPC, LPP, MPC, MGCP; IEEE 2030.5; IEC 62559-2; IEC 62443; EN 50549-1; MID/MEG; SNE-VO.
