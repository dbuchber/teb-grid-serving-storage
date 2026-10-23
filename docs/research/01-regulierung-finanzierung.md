# 01 – Regulierung & Finanzierung

Stand: 23.10.2026. Block 1 des Rechercheplans (`00-rechercheplan.md`).
Konvention: Jede Aussage hat eine Quelle (Kürzel in eckigen Klammern, Liste am Ende).
Was nicht gegen eine Primärquelle geprüft ist, steht als **[unbestätigt]** da.

---

## Kernaussagen

1. **Österreich hat die Pflicht-Steuerschnittstelle schon, aber nur für Erzeugung und nur am Netzanschlusspunkt.**
   § 76 ElWG: Neue oder wesentlich geänderte Erzeugungsanlagen ab 3,68 kW müssen seit **1.6.2026**
   eine „technische Einrichtung zur Steuerbarkeit“ mit **standardisierter Schnittstelle** haben. Die
   TOR Typ A v1.4 legt dafür **OpenADR (IEC 62746-10-1)** über das Kundeninternet fest, mit 1 Minute
   Sollwert-Reaktionszeit und Fallback nur in Einspeiserichtung (vertraglicher Wert bzw. 70 % kWp bei PV)
   (korr. lt. 06). § 76 selbst nennt kein Protokoll, OpenADR kommt aus der TOR (korr. lt. 06). Das österreichische OpenADR-Profil ist erst **bis 31.10.2026**
   zu spezifizieren und bis 31.12.2026 zu veröffentlichen [ElWG; TOR-A-1.4]. Speicher und bidirektionale
   Wallboxen sind darin laut Konsultation **nicht geklärt** [TOR-Stn].
2. **Der VNB in Österreich gibt nur die netzwirksame Leistung am Anschlusspunkt vor. Alles hinter dem Zähler
   bleibt Sache des Betreibers** (§ 76 Abs. 3 ElWG). Unser Profil muss deshalb mit einem Sollwert am
   Netzanschlusspunkt arbeiten, nicht mit Gerätebefehlen. Der Smart Meter am Anschlusspunkt ist die
   natürliche Prüfinstanz.
3. **Die beidseitige Nutzung von Speichern hat in AT eine Tarifgrundlage, kundgemacht am 12.10.2026, wirksam
   ab 1.1.2027 (korr. lt. 06).** Die SNE-G-V
   (BGBl. II 299/2026) befreit „systemdienliche Speicher“ vom Netznutzungs- und
   Netzverlustentgelt. Bedingung: Der VNB darf den Betrieb **in beide Energierichtungen** unentgeltlich
   einschränken, und der Speicher wird „**ausschließlich zur Wiedereinspeisung**“ betrieben (§ 23); ein
   Heimspeicher zur Eigenverbrauchsoptimierung erfüllt das nicht ohne Weiteres (korr. lt. 06).
   Speicheranlagen ab **10 kW** dürfen zu **≥ 1 MW** gebündelt werden („technische Aggregation“; die
   Verordnung spricht von Energiespeicheranlagen, nicht ausdrücklich von Heimspeichern) (korr. lt. 06).
   Deckel: 5 GW österreichweit [SNE-G-V §§ 23–26]. Dazu kommt ein §14a-ähnlicher Tarif für „flexible
   Entnahme“ (≥ 4 kW, bis 100 % einschränkbar, 2 × 2 h/Tag). Ihn müssen VNB spätestens ab 1.10.2027
   anbieten [SNE-G-V § 10, § 32].
4. **EU-Recht verlangt marktbasierte Flex-Beschaffung durch VNB und die Anerkennung ihrer Kosten in den
   Netzentgelten, einschließlich IKT.** Art. 32 RL 2019/944 regelt das. Seit der Reform 2024 sollen
   Tarifmethoden Capex **und** Opex berücksichtigen und Flexibilität sowie flexible Anschlüsse fördern
   (Art. 18 VO 2019/943 i.d.F. 2024/1747) [RL944; VO1747]. Österreich hat das in § 139 Abs. 4 ElWG
   übernommen [ElWG].
5. **Der EU Network Code Demand Response ist noch nicht in Kraft.** ACER hat ihn am 7.3.2025 vorgeschlagen,
   die Kommission hat Anfang 2026 die Konsultationsantworten veröffentlicht. Eine Verabschiedung bis
   Oktober 2026 haben wir nicht gefunden [ACER-NCDR; EC-NC; Electron]. Bis dahin gelten nationale Regeln.
6. **Deutschland (§ 14a EnWG) erfasst Speicher nur beim Netzbezug.** Der VNB darf den Bezug auf 4,2 kW
   dimmen, eine Einspeisung kann er nicht anordnen. Entlastung: Modul 1 pauschal **110–190 €/a**, Modul 2:
   Arbeitspreis auf 40 %, Modul 3: zeitvariabel [BNetzA-14a]. Für unser Konzept fehlt dort die Richtung
   „entladen bei Last“.
7. **Ein beidseitiger Abruf existiert in NL als Vertragsform.** Das ACM-Codebesluit
   „capaciteitssturingscontract“ vom 11.12.2025 erlaubt es, Netzgebrauch zu begrenzen **oder entgegen
   der Engpassrichtung** zu nutzen, z. B. Batterie-Rückspeisung bei Lastengpass, gegen Vergütung [ACM-CSC].
   FR und IT beschaffen lokale Flex über Ausschreibungen. Die Größenordnung ist klein: z. B. 11 MW bei
   E-Distribuzione 2026 [EDGE-2026].
8. **Flexibilität ist erheblich billiger als Netzausbau, nach mehreren Studien.** BMWi-Verteilernetzstudie:
   3 % Abregelung der Jahresenergie von Wind- und PV-Anlagen in Netzen mit Ausbaubedarf spart **> 40 %** des
   Netzausbaus (korr. lt. 06) [BMWi-VNS]. DNV/smartEn: EU-weit
   **11,1–29,1 Mrd. €/a** vermiedene Verteilnetzinvestitionen 2030 [DNV]. Zum Vergleich der Bedarf:
   Eurelectric nennt 67 Mrd. €/a Verteilnetzinvestitionen in der EU (2025–2050), Österreich rund
   44 Mrd. € Verteilnetz bis 2040 [Eurelectric; FINGREEN].

---

## 1. EU-Rahmen

### 1.1 Art. 32 RL (EU) 2019/944: Flexibilität im Verteilnetz
- Die Mitgliedstaaten müssen einen Rahmen schaffen, der VNB **erlaubt und Anreize gibt**, Flexibilitätsleistungen
  einschließlich Engpassmanagement zu beschaffen, „from providers of distributed generation, demand response or
  energy storage“. Voraussetzung ist, dass das den Netzausbau kosteneffizient ersetzt. Die Beschaffung ist
  **transparent, diskriminierungsfrei, marktbasiert**, außer der Regulator stellt fest, dass das nicht effizient
  ist oder den Markt verzerrt (Abs. 1) [RL944].
- Die Produktspezifikationen legt der VNB fest (mit Genehmigung des Regulators) oder der Regulator selbst,
  „at least at national level“ (Abs. 2) [RL944].
- **Kostenanerkennung:** „Distribution system operators shall be adequately remunerated for the procurement of
  such services to allow them to recover at least their reasonable corresponding costs, including the necessary
  information and communication technology expenses and infrastructure costs.“ (Abs. 2) [RL944]
- Der Netzentwicklungsplan muss Flex-Bedarf und Flex als Alternative zum Ausbau ausweisen (Abs. 3) [RL944].

### 1.2 Strommarktdesign-Reform 2024
**VO (EU) 2024/1747** (ändert VO 2019/943) [VO1747]:
- **Art. 18 Abs. 2 (neu):** Tarifmethoden „shall consider both capital and operational expenditure“, sollen
  „support the use of flexibility services and enable the use of flexible connections“ und „facilitate energy
  storage, demand response“. Erwägungsgrund 23 spricht von einer „efficient combination of both“, also einem
  TOTEX-ähnlichen Ansatz, ohne das Wort zu verwenden.
- **Art. 18 Abs. 8 (neu):** Die Regulatoren erkennen die relevanten Kosten an und führen ggf. Leistungsziele ein,
  u. a. für „the use of flexibility services and the development of smart grids“.
- **Art. 19e:** Flexibilitätsbedarfsanalyse durch den Regulator, alle 2 Jahre für 5–10 Jahre, auf Basis von
  ÜNB- und VNB-Daten. **Art. 19f:** indikatives nationales Ziel für nicht-fossile Flexibilität.
  **Art. 19g/19h:** Förderregelungen für nicht-fossile Flexibilität (Kapazitätszahlungen, nur Neuinvestitionen).
- **Art. 7b „Dedicated measurement device“:** ÜNB, VNB und Aggregatoren dürfen mit Zustimmung des Kunden Daten
  aus geräteeigenen Messeinrichtungen für Beobachtbarkeit und **Abrechnung** von Flex nutzen, „including from
  energy storage facilities“. Liefert der Smart Meter die nötigen Daten nicht, **müssen** sie diese Daten
  akzeptieren. Die Mitgliedstaaten regeln die Datenvalidierung. Das ist für unsere Verifikationslogik relevant:
  Smart Meter und Gerätemessung können sich ergänzen.
- **Art. 7a Peak-shaving product:** nur bei einer ausgerufenen Preiskrise. Für das Verteilnetz-Engpassmanagement
  ist es nicht einschlägig.

**RL (EU) 2024/1711** (ändert RL 2019/944) [RL1711]:
- **Art. 6a „Flexible connection agreements“:** Der Regulator schafft einen Rahmen für flexible Anschlüsse in
  Gebieten mit knapper Kapazität. Auch dauerhafte Lösungen „including for energy storage“ sind möglich. Der
  Netzbenutzer muss „a power control system that is certified by an authorised certifier“ installieren. Das ist
  ein EU-Hebel für eine **zertifizierte Steuereinrichtung**.
- Umsetzungsfrist: 17.1.2025, für einzelne Punkte 17.7.2026 [RL1711, Art. 3].

### 1.3 Network Code on Demand Response (NC DR)
- Die gemeinsame Vorlage von EU DSO Entity und ENTSO-E kam im Mai 2024, der ACER-Vorschlag an die Kommission
  am **7.3.2025** [ACER-NCDR].
- Inhalt laut ACER: vereinfachte Präqualifikation und Produktverifikation, nationales Register,
  **marktbasierte Beschaffung** von Engpass- und Spannungsdiensten durch VNB/ÜNB (Ausnahmen müssen begründet
  werden), TSO-DSO-Koordination. Er ändert auch die EB GL, SO GL und den NC DCC [ACER-NCDR].
- Die Kommissionskonsultation lief vom 14.7. bis 12.9.2025, die Antworten wurden am 8.1.2026 veröffentlicht.
  Laut Stand 6.8.2026 ist der Code nicht verabschiedet [Electron]. Die Kommissionsseite sagt, man „is developing“
  den NC DR, und nennt eine Studie zu lokalen Flexibilitätsmärkten (März 2026) [EC-NC].
  **Eine Annahme bis Oktober 2026 haben wir nicht gefunden.** Üblich wäre danach eine Umsetzungsfrist von etwa
  2 Jahren **[unbestätigt]** [Electron].

---

## 2. Nationale Modelle

### 2.1 Deutschland: § 14a EnWG (BNetzA BK6-22-300 / BK8-22/010-A)
Quelle, wenn nicht anders angegeben: [BNetzA-14a].
- **Erfasst:** Wallboxen (nicht öffentlich), Wärmepumpen, Klimaanlagen und **Stromspeicher, nur hinsichtlich
  Netzbezug** (Einspeicherung), jeweils > 4,2 kW. Ein Speicher fällt auch dann darunter, wenn er nur PV-geladen
  programmiert ist, sofern er netzbezugsfähig ist.
- **Eingriff:** Der VNB darf den Bezug „temporär auf bis zu 4,2 kW reduzieren“. Das ist nur bei tatsächlicher
  oder drohender Überlastung erlaubt, präventiv nur auf Basis der Netzplanungsdaten. **Einspeisung ist nicht
  betroffen. Speicher müssen bei Steuerung nicht einspeisen.** Eine aktive Entladung zur Netzstützung gibt es
  im § 14a nicht.
- **Entlastung:**
  - Modul 1: pauschale Netzentgeltreduktion **110–190 €/a** (Stand 2023, je VNB). Beispiele 2026:
    111,25 €/a (Netze ODR), 131,82 €/a u. a. [Preisblätter 2026, siehe Quellen].
  - Modul 2: Arbeitspreis auf **40 %**, eigener Zählpunkt nötig.
  - Modul 3: zeitvariables Netzentgelt (HT/ST/NT), Pflichtangebot seit **1.4.2025**, nur mit Modul 1
    kombinierbar, iMSys nötig.
- Übergang: Bestandsanlagen vor 2024 bleiben ohne Vereinbarung dauerhaft ausgenommen. Steuereingriffe sind
  seit 1.3.2025 auf einer gemeinsamen Plattform zu veröffentlichen.
- **Solarspitzengesetz (Feb. 2025):** Neue PV-Anlagen bis 25 kW ohne Smart Meter und Steuerbox dürfen nur
  60 % einspeisen. Die Grenze entfällt nach Einbau und **bestandenem Fernsteuertest des Netzbetreibers**. Bei
  negativen Preisen gibt es keine Vergütung (für Neuanlagen) [BSW-Solar via pv-magazine].
  Die genaue Schwellen-Systematik ist **[unbestätigt gegen Gesetzestext]**.
- **§ 14c EnWG:** Marktgestützte Flex-Beschaffung durch VNB. Die BNetzA kann Ausnahmen festlegen (Abs. 4)
  [§14c]. Ob und in welchem Umfang sie das getan hat, ist **[unbestätigt]**.
- **§ 13k EnWG „Nutzen statt Abregeln“:** zuschaltbare Lasten in Entlastungsregionen, ÜNB-Ebene, seit
  1.10.2024. Das Umsetzungskonzept v2.0 stammt vom 1.4.2026 [§13k; ÜNB-13k].
- **AgNes (Netzentgeltreform):** Der Festlegungsentwurf vom 6.8.2026 sieht für Erzeuger und Speicher einen
  Leistungspreis von etwa **4–7 €/kW/a** vor, ohne Arbeitspreis. **Heimspeicher in NS bis 30 kW sind
  ausgenommen.** Start 1.1.2029, Konzept für dynamische Netzentgelte 2027, Leitlinien für Flexible Connection
  Agreements ab 2027 [Rödl-AgNes]. Endgültige Festlegung Ende 2026 geplant.
- **Regulierungsrahmen ab 2029 (NEST/RAMEN Strom, Festlegung 10.12.2025):** ersetzt ARegV/StromNEV. Geplant
  sind eine Trennung von Opex/Capex im Erlösobergrenzen-Modell und ein OPEX-Anpassungsfaktor (diskutiert
  ca. 2–2,4 %) [VKU-NEST; Noerr; BDEW-Stn]. Eine explizite Flex-Kostenregel haben wir nicht gefunden
  **[unbestätigt]**.

### 2.2 Österreich: ElWG (BGBl. I Nr. 91/2025) und Verordnungen
Das ElWG wurde am 11.12.2025 im Nationalrat beschlossen, am 23.12.2025 kundgemacht und trat am 24.12.2025 in
Kraft. Es ersetzt das ElWOG 2010 [RIS-ElWG].

| Regelung | Inhalt | Bedeutung für uns |
|---|---|---|
| **§ 63** Last- und Einspeisesteuerung | Endkunden dürfen Last- und Einspeisesteuerung, „wobei auch Energiespeicheranlagen genutzt werden können“, allein oder über Aggregatoren an allen Märkten anbieten. Aggregatoren brauchen keine Zustimmung anderer Marktteilnehmer. E-Control kann einen Ausgleich an Lieferanten/BGV regeln. | Marktseite (Aggregator) ist legal verankert. |
| **§ 76** Ansteuerbarkeit | **Ab 1.6.2026** Pflicht für neue Erzeugungsanlagen **≥ 3,68 kW**: Steuereinrichtung mit **standardisierter Schnittstelle** (Details in den TOR), Kosten trägt der Betreiber. Der VNB muss die Ansteuerbarkeit herstellen: > 25 kW bis 1.6.2028, 3,68–25 kW bis 1.6.2029, 0,8–3,68 kW auf Verlangen bis 1.1.2030. „Ansteuerbarkeit ist gegeben, wenn der Netzbetreiber die Anlage nachweislich im Betrieb erreichen und erfolgreich Steuerbefehle umsetzen kann.“ Pönale für den VNB: 100 € je Verzugsjahr. Abs. 3: Der VNB gibt nur die **netzwirksame Leistung am Anschlusspunkt** vor; Eigenverbrauchsoptimierung und Speicher hinter dem Zähler bleiben unberührt. | Das ist unsere Position, in AT schon Gesetz. „Nachweislich erreichen und umsetzen“ verlangt einen **Testabruf**. |
| **§ 101** Spitzenkappung | PV (neu/geändert): Der VNB darf die netzwirksame Leistung dauerhaft statisch oder dynamisch begrenzen, **nicht unter 70 % der Modulspitzenleistung**. Wind ab 1.1.2027: ≤ 1 % Jahresenergie, ≤ 15 % Leistung. **Ausnahme: vereinbarte netzwirksame Leistung ≤ 7 kW.** Benachrichtigung maschinenlesbar, bei Meldung nach 9:00 Uhr des Vortags trägt der VNB die Ausgleichsenergiekosten. Veröffentlichung binnen 24 h. **Keine Entschädigung.** | Begrenzung nur in eine Richtung (Einspeisung), unvergütet. |
| **§ 103** Flexibler Netzzugang VN | Statische oder dynamische Leistungsvorgabe vertraglich möglich, befristet (NE 6–7: 12 Monate, NE 4–5: 18, NE 3: 24), auf Wunsch auch dauerhaft für Erzeugung, Verbrauch **und Speicher**. | Umsetzung von Art. 6a RL. |
| **§ 127 Abs. 3** | Speicher sind 20 Jahre ab Inbetriebnahme beim Bezug für die Speicherung von Netznutzungs- und Netzverlustentgelt freigestellt, „unter Berücksichtigung des systemdienlichen Betriebs“. | Konkretisiert in SNE-G-V §§ 23–26. |
| **§ 128 Abs. 3–4** | Zeitvariable Netznutzungsentgelte auf Verlangen; Leistung kann als **unterbrechbar und/oder regelbar** vereinbart werden, dafür gibt es einen **Abschlag**. | AT-Pendant zu § 14a. |
| **§ 139** Flex-Beschaffung | VNB beschaffen Flex marktgestützt, wenn das günstiger als Netzausbau ist. Gemeinsamer VNB-Vorschlag für Produkte und Verfahren binnen 9 Monaten. E-Control legt die Modalitäten per Verordnung fest. **Abs. 4: Die angemessenen Kosten einschließlich IKT werden in den Systemnutzungsentgelten anerkannt.** | Rechtsgrundlage für die Finanzierung aus Netzentgelten. |
| **§ 142** Flexibilitätsplattform | ÜNB und VNB betreiben gemeinsam eine digitale Infrastruktur mit Web-Schnittstelle zur Koordination von Flex-Bedarf, -Angebot und -Einsatz. | Andockpunkt für unser Profil (Markt ↔ Netz). |

**TOR Stromerzeugungsanlagen Typ A, Version 1.4 (gültig ab 1.6.2026)** [TOR-A-1.4]:
- Kap. 5.4.1.2: „standardisierte, digitale Schnittstelle“. Voraussetzungen sind Internetanbindung sowie Mess-
  und Regeleinrichtung am Netzanschlusspunkt. „Die Signalgebung vom Netzbetreiber erfolgt über die
  Internetverbindung des Netzbenutzers mittels standardisiertem Kommunikationsprotokoll.“
- Protokoll: **OpenADR auf Basis IEC 62746-10-1**, von den Netzbetreibern für AT zu profilieren.
  „Eine Kommunikation über Drittsysteme ist nicht vorgesehen“, also keine Hersteller-Cloud im Pfad.
- Sollwert innerhalb **1 Minute**. Bei Kommunikationsausfall greift ein **Fallback** auf die vertraglich
  vereinbarte Einspeiseleistung bzw. 70 % kWp. Er begrenzt **nur die Einspeiserichtung** und gilt für
  Netzbenutzer mit dynamischem Sollwert (korr. lt. 06).
- OpenADR-Version offen: IEC 62746-10-1 beruht auf OpenADR 2.0b, Netz OÖ hat am 4.3.2026 dagegen „Digital
  Customer Interface Austria – OpenADR 3.1“ vorgestellt. Welche Version das AT-Profil nutzt, ist eine offene
  Frage (korr. lt. 06).
- Cybersicherheit ausdrücklich gefordert: CRA (VO 2024/2847), NIS2/NISG 2026, CER/RKEG, NC CS (DelVO 2024/1366).
- Fußnote 25: Das OpenADR-Protokoll ist „bis spätestens zum 31.10.2026 zu spezifizieren“ und der E-Control
  vorzulegen, Veröffentlichung bis 31.12.2026.
- Konsultationskritik [TOR-Stn]: Version und Use Cases sind unklar. „Es ist unklar, wie und in welcher Art
  zukünftig bidirektionale Wallboxen und Speicher gesteuert werden.“ Speicher werden je nach Netzwirkung als
  Erzeugung oder Verbrauch behandelt. Gefordert werden ein verbindliches nationales Profil und eine
  Übergangsfrist (z. B. 12 Monate).

**SNE-G-V, BGBl. II Nr. 299/2026 (kundgemacht 12.10.2026, in Kraft 1.1.2027)** [SNE-G-V]:
- **§ 10 Flexible Entnahme:** Der Netzbenutzer verpflichtet sich, die netzwirksame Leistung ganz oder zu einem
  Anteil von **mindestens 4 kW um bis zu 100 %** einzuschränken. NE 6–7: statisch oder (auf Wunsch, wenn
  technisch unterstützt) dynamisch bis 6 Uhr des Vortags, **2 Zeiträume à 2 h täglich**. Auf NE 7 bleiben
  mindestens 4 kW. Voraussetzung: Der VNB darf die **Viertelstundenwerte des Zählers** zur Vertragserfüllung
  verarbeiten. Laufzeit 10 Jahre. Auf NE 6–7 besteht ein Anspruch auf Kundenwunsch, verpflichtend spätestens
  ab **1.10.2027**. Gesonderter Leistungspreis, die Höhe kommt in der Tarifverordnung (noch offen). Wer gegen
  die Vereinbarung bezieht, zahlt eine Überschreitungspönale, außer der VNB hat eine technische
  Einschränkungsmöglichkeit.
- **§ 11:** Ein eigenes Netznutzungsentgelt für Mehrbezug durch Regelreserve oder Flex-Erbringung verhindert
  Doppelbelastung (NE 5–7 nach Präqualifikation).
- **§§ 23–26 Systemdienliche Speicher:** Befreiung von Netznutzungs- und Netzverlustentgelt, wenn (u. a.) der
  VNB „vertraglich das Recht und die technische Möglichkeit erhält, den zulässigen Betriebsbereich **in beide
  Energierichtungen** innerhalb definierter Grenzen … **unentgeltlich** einzuschränken“. Weitere Bedingungen:
  Betrieb „**ausschließlich zur Wiedereinspeisung**“ (§ 23) (korr. lt. 06); Standort an einem UW der NE 4 mit
  PV-Verhältnisleistung > 0,3 MW/MVA **oder Wind > 0,85 MW/MVA** (korr. lt. 06) und Rückspeisedauer > 2 500 h, ≥ 1 MW.
  **Bündelung von Speichern ≥ 10 kW**, „messtechnisch geeignet erfasst“, am selben UW per „technischer
  Aggregation“ ist zulässig. Einschränkungsrahmen stündlich je Monat für 5 Jahre, tatsächliche Vorgabe täglich
  bis 6 Uhr des Vortags. Deckel 5 GW für ganz AT. Gilt für Speicher, die bis 31.12.2030 in Betrieb gehen.
- Weitere Tarifbausteine: **Sommer-Nieder-Arbeitspreis** (1.4.–30.9., 10–16 Uhr, NE 7) seit 1.4.2026 mit rund
  20 % Abschlag [SNE-V-Nov-2025; WKO-ElWG].
  Beispiel Wiener Netze: 5,58 statt 6,98 ct/kWh netto, gilt für temporäre Anlagen [WN-SNE].

**Regulierung (Opex/Capex):** Die 5. Regulierungsperiode für Strom-VNB läuft vom 1.1.2024 bis 31.12.2028
[CEER-RFR25]. Wie Flex-Kosten darin behandelt werden, ist **[unbestätigt]**. Die gesetzliche Grundlage ist
§ 139 Abs. 4 ElWG.

### 2.3 Niederlande
- **Codebesluit congestiemanagement** (ACM, in Kraft seit 2022): neues Produkt „capaciteitsbeperkingscontract“
  (CBC) und Pflicht zur Prüfung marktbasierter Engpasslösungen [ACM-QA].
- **Capaciteitssturingscontract** (ACM/25/196733, 11.12.2025): Netzbetreiber und Anschlussnehmer vereinbaren,
  den Netzgebrauch zu begrenzen **oder in Gegenrichtung zum Engpass** zu nutzen, z. B. Rückspeisung aus eigener
  Erzeugung oder Batterie bei Lastengpass, „for a fee“ [ACM-CSC]. **Das ist das nächste Vorbild für unseren
  bidirektionalen Abruf.** Ob Haushalte erfasst sind, ist **[unbestätigt]**.
- Alternative Transportrechte: non-firm ATO, zeitdauer- und zeitblockgebundene Transportrechte (z. B. ATR85).
  Die Rabatthöhen sind **[unbestätigt]** [ACM-ATR].
- **GOPACS**: gemeinsame Plattform von TenneT und VNB. Der VNB bezahlt die Spread zwischen Kauf- und
  Verkaufsgebot (IDCONS). Seit 2025 sind alle drei NEMOs angebunden, Nord Pool ab 2026 [Solarmagazine-GOPACS].
  Jahreskosten haben wir nicht gefunden.
- **Zeitvariable Netzentgelte für Kleinverbraucher (≤ 3×80 A):** Vorschlag der Netzbetreiber von Mai 2026 mit
  Start 1.1.2029, gut 2/3 des Transporttarifs volumen- und zeitabhängig. Die ACM-Entscheidung steht aus
  [Solarmagazine-TAN].

### 2.4 Frankreich
- **Enedis-Flex-Ausschreibungen** seit 2020. Die Runde S1 2026 hatte **101 Lose** in 17 Regionen
  (44 Lastsenkung, 57 Lasterhöhung), ohne Kapazitätsreservierung, mit Vergütung der variablen Komponente in
  €/MWh und Vertragslaufzeit bis 31.7.2029 [Enedis-S1-2026]. Ältere Runden hatten einen Festpreis in €/Monat
  plus Aktivierungspreis in €/MWh [Enedis-S2-2025]. Vergütungshöhen haben wir nicht gefunden. Gewinner waren
  wiederholt Aggregatoren für Heizungen und Warmwasser (Voltalis) [Voltalis].
- **Portail Flexibilités** (RTE + Enedis, gemeinsamer Zugang): CRE-Delib. 2026-161 vom 22.7.2026, zweijähriges
  Experiment in 10 Départements im Südwesten [CRE-2026-161].
- **TURPE 7 / Heures creuses:** Die Schwachlastzeiten verlagern sich teilweise auf den Tag (max. 3 h zwischen
  11 und 17 Uhr), Rollout ab Nov. 2025 bis Ende 2027 **[unbestätigt in CRE-Primärtext]** [HelloWatt; Kelwatt].

### 2.5 Italien
- **UVAM** (Terna, ÜNB-Ebene): gemischte virtuelle Einheiten, Vergütung fix in €/MW/a plus €/MWh. Im Pilot
  2019 lagen die Preise nahe der Obergrenze von ca. **30 000 €/MW/a** [QualEnergia].
  Ob UVAM inzwischen durch den TIDE abgelöst ist, ist **[unbestätigt]**.
- **VNB-Pilote nach ARERA 352/2021**, z. B. **EDGE (E-Distribuzione)**, verlängert für 2026 (Delib. 508/2025).
  Bedarf 2026: ca. **11 MW** Lastsenkung, ca. 6 000 h Verfügbarkeit in Bari und Macerata, 200–900 kW je
  Perimeter. Zweiteilige Vergütung (Verfügbarkeit €/kW·h + Nutzung €/kWh), **Preisobergrenze Nutzung
  200 €/MWh**, Abwicklung über **Piclo Flex** [EDGE-2026].

### 2.6 Spanien
- **CNMC Circular 1/2024** und **Resolución 31.7.2026** (BOE 11.8.2026, in Kraft 1.9.2026): **flexible
  Netzzugangsrechte** für Verbrauch und **Speicher** an Engpassknoten (Anschluss ohne Garantie für alle Stunden)
  [PwC-CNMC; Osborne Clarke].
- Die Circular verlangt von den VNB einen Vorschlag für ein „procedimiento de operación de distribución“ zum
  Engpassmanagement [PwC-CNMC].
  Lokale Flex-Märkte oder ein § 14a-Pendant haben wir **nicht gefunden [unbestätigt]**.

---

## 3. Vergütungsformen und typische Höhen

| Form | Beispiel | Höhe | Quelle |
|---|---|---|---|
| Pauschale Netzentgeltreduktion | DE § 14a Modul 1 | 110–190 €/a je Marktlokation | [BNetzA-14a] |
| Reduzierter Arbeitspreis | DE § 14a Modul 2 | 40 % des NS-Arbeitspreises | [BNetzA-14a] |
| Zeitvariables Netzentgelt | DE Modul 3; AT SNAP; NL ab 2029 | z. B. DE NT 1,95 / HT 7,70–11,32 ct/kWh; AT ca. −20 % im Sommerfenster | [Wemag; SWBS; WKO-ElWG] |
| Leistungspreis-Abschlag für einschränkbare Leistung | AT § 10 SNE-G-V „flexible Entnahme“ | Höhe offen (Tarif-VO) | [SNE-G-V] |
| Befreiung Netznutzungs- und Verlustentgelt gegen bidirektionale Einschränkung | AT systemdienliche Speicher | volle Befreiung beim Speicherbezug, Deckel 5 GW | [SNE-G-V] |
| Verfügbarkeit + Abruf (Ausschreibung) | IT EDGE; FR Enedis | IT: Abruf ≤ 200 €/MWh; FR: €/Monat + €/MWh (Höhe n. v.) | [EDGE-2026; Enedis] |
| Verfügbarkeit (ÜNB) | IT UVAM | bis ca. 30 000 €/MW/a (2019) | [QualEnergia] |
| Spread-basierter Abruf | NL GOPACS/IDCONS | Marktpreis-Spread | [Solarmagazine-GOPACS] |
| Unvergütete Pflicht | AT § 101 Spitzenkappung; DE Solarspitzen 60 % | 0 € | [ElWG; pv-magazine] |
| Kosten des Steuergeräts | AT § 76; DE Steuerbox | AT: trägt der Betreiber. DE: Preisobergrenze Steuerbox 50 €/a (Angabe BSW/Finanztip **[unbestätigt]**) | [ElWG; pv-magazine] |

Zum Vergleich der Netzentgelte für Speicher ab 2029 (DE, Entwurf): 4–7 €/kW/a Leistungspreis, Heimspeicher
≤ 30 kW befreit [Rödl-AgNes].

---

## 4. Regulatorische Anerkennung von Flex-Kosten (Opex vs. Capex)

- **Problem:** In klassischer Anreizregulierung wird Capex verzinst, Opex (Flex-Einkauf) unterliegt Effizienz-
  druck. Das begünstigt Kupfer gegenüber Flexibilität. Die EU reagiert darauf mit Art. 18 Abs. 2 lit. a und
  Abs. 8 VO 2019/943 n. F. („consider both capital and operational expenditure“, „recognise relevant costs as
  eligible“, Leistungsziele für Flex-Nutzung) und Erwägungsgrund 23 („efficient combination of both“) [VO1747].
- **Art. 32 Abs. 2 RL 2019/944:** Mindestens die angemessenen Flex-Kosten inklusive IKT sind zu erstatten [RL944].
- **AT:** § 139 Abs. 4 ElWG übernimmt das wörtlich. Erlöse aus der Beschaffung werden gegengerechnet [ElWG].
  Die Pönale nach § 76 Abs. 2 (100 €/Jahr Verzug) ist „kostenmindernd“ in der Kostenbasis anzusetzen: ein
  Anreiz, die Ansteuerbarkeit herzustellen.
- **DE:** RAMEN Strom ab 2029 sieht eine Opex/Capex-Trennung und einen OPEX-Aufschlag vor [VKU-NEST; Noerr;
  BDEW-Stn]. Ob Flex-Kosten als dauerhaft nicht beeinflussbar gelten, ist **[unbestätigt]**.
- **Vorbild TOTEX:** Ofgem RIIO (UK) ist bekannt als TOTEX-Ansatz **[unbestätigt, nicht geprüft; außerhalb
  Geltungsbereich]**.

---

## 5. Konflikt Markt vs. Netz

- **BDEW-Ampel (2015, konkretisiert 2017):** Grün bedeutet Marktphase ohne Einschränkung. Gelb heißt, ein Engpass
  droht im Netzsegment und der VNB ruft Flex vertraglich bzw. marktlich ab (vergütet). Rot bedeutet Gefährdung
  der Netzstabilität, dann greift der VNB direkt ein. Die 2017er Konkretisierung behandelt u. a. die
  **Priorisierung bei Mehrfachvermarktung** [BDEW-2015; BDEW-2017].
  VDE FNN (2022) trennt Gelb (präventiv, Prognose) zeitlich klar von Rot (kurativ) [VDE-Flex].
- **Rechtliche Abbildung:**
  - DE § 14a: Eingriff nur bei Gefährdung (rot-nah), Mindestleistung garantiert [BNetzA-14a].
  - AT: § 101/§ 103/SNE-G-V legen Vorgaben bis 6 Uhr bzw. 9 Uhr am Vortag fest. Damit kann der Markt (Lieferant,
    BGV, Aggregator) den Fahrplan anpassen. Spätere Eingriffe gehen kostenmäßig zulasten des VNB (§ 101 Abs. 5)
    [ElWG; SNE-G-V]. Die Meldung geht automatisch auch an den Lieferanten des Zählpunkts.
  - AT § 140: Engpässe im ÜN behandelt der Regelzonenführer kaskadiert: erst Flex-Verträge über die Plattform,
    dann Anordnung, Regelarbeitsgebote, Intraday. Vorrang für EE, Entschädigung nach Art. 13 VO 2019/943 [ElWG].
- **Aggregatoren:** In AT haben sie ein Recht auf Marktzugang ohne Zustimmung des Lieferanten. Ein finanzieller
  Ausgleich an Lieferanten ist möglich, darf den Marktzutritt aber nicht behindern (§ 63) [ElWG]. Die EU will mit
  dem NC DR die Präqualifikation harmonisieren [ACER-NCDR].
- **Doppelvermarktung:** Laut § 11 SNE-G-V zahlt man keine doppelten Netzentgelte auf Flex-bedingten Mehrbezug
  [SNE-G-V]. Eine Rangfolge zwischen VNB-Abruf und Marktvermarktung desselben Speichers regeln wir im Profil
  (Vorschlag: Netzsignal mit Vortagesfrist hat Vorrang, kurzfristige Abrufe nur im „Rot“-Fall).

---

## 6. Zahlen: Netzausbau vs. Flexibilität

| Aussage | Zahl | Quelle | Qualität |
|---|---|---|---|
| DE Verteilnetz-Zusatzinvestitionen bis 2032 | 23–49 Mrd. € je Szenario | [BMWi-VNS] | Primär, 2014 |
| **Abregelung 3 % der Jahresenergie von Wind/PV in Netzen mit Ausbaubedarf, in der Planung** (korr. lt. 06) | **spart > 40 % des Netzausbaus** (1 % → ca. 30 %) | [BMWi-VNS] | Primär |
| Kombination aus Erzeugungsmanagement + rONT | Investitionsbedarf ca. −60 %, jährliche Kosten ca. −20 % | [BMWi-VNS] | Primär |
| **EU: vermiedene Verteilnetzinvestitionen durch Demand-side Flex 2030** | **11,1–29,1 Mrd. €/a** | [DNV] | Studie, gesponsert (Eaton, Enel X, EDF, Voltalis) |
| EU: Verteilnetzinvestitionsbedarf | 33 → 67 Mrd. €/a (2025–2050). Mit vorausschauenden Strategien und Flex ca. 55 Mrd. €/a (−18 %) | [Eurelectric] | Verband; −18 % nur Sekundärquelle |
| EU Netzinvestitionen dieses Jahrzehnts | 584 Mrd. € | [EC-GAP] | Kommission |
| AT Verteilnetz bis 2040 | 44,4 Mrd. € (AIT 2024), gesamt Netz ca. 53 Mrd. € | [FINGREEN; OE-Netzentgelte] | Sekundärzitat der AIT-Studie |
| DE Haushaltsflex 2035 (EV, WP, Heimspeicher) | 100 TWh flexibilisierbar, 4,8 Mrd. €/a Systemeinsparung (nicht nur Netz) | [Agora] | Thinktank |
| BW: Spitzenkappung reduziert Ausbaubedarf | 19 % | [BW-VNS] | Landesstudie |

---

## Ländertabelle

| Land | Steuerpflicht/-recht für Kleinanlagen | Speicher erfasst? | Richtung | Vergütung | Schnittstelle/Protokoll | Flex-Markt VNB |
|---|---|---|---|---|---|---|
| **EU** | Kein Gerätezwang. Flexible Anschlüsse erfordern zertifiziertes „power control system“ (Art. 6a RL) | ja (Art. 32, 6a, 7b) | offen | Kostenanerkennung beim VNB (Art. 32, 18) | nicht festgelegt; NC DR ausstehend | Pflicht marktbasiert, mit Ausnahmen |
| **AT** | § 76 ElWG: Pflicht ab 3,68 kW (Erzeugung) seit 1.6.2026; § 101 Spitzenkappung PV ≥ 70 % kWp (Ausnahme ≤ 7 kW) | Speicher: SNE-G-V §§ 23–26 (≥ 10 kW bündelbar, nur bei Betrieb ausschließlich zur Wiedereinspeisung (korr. lt. 06)), § 10 flexible Entnahme | **beide** (systemdienliche Speicher); sonst Einspeisung (§ 101) bzw. Bezug (§ 10) | Entgeltbefreiung, Leistungspreis-Abschlag (Höhe offen); Spitzenkappung unvergütet | **OpenADR / IEC 62746-10-1** über Kundeninternet, Profil bis 31.10.2026 | § 139 + Plattform § 142 (in Aufbau) |
| **DE** | § 14a (Bezug > 4,2 kW); Solarspitzen 60 % ohne Steuerbox | nur Bezug | nur Bezug dimmen | Modul 1–3 (110–190 €/a usw.) | SMGW + CLS + Steuerbox (siehe Block 3) | § 14c; § 13k (ÜNB) |
| **NL** | vertraglich (CBC, capaciteitssturingscontract) | ja (Batterie explizit) | **beide** (capaciteitssturing) | Vertragsvergütung; IDCONS-Spread | GOPACS (Plattform) | ja, GOPACS |
| **FR** | keine Gerätepflicht gefunden | über Aggregatoren | Senkung und Erhöhung (Lose) | €/Monat + €/MWh Ausschreibung | n. v. | Enedis-Ausschreibungen, Portail Flexibilités |
| **IT** | keine Gerätepflicht gefunden **[unbestätigt]** | über BSP/Aggregatoren | in EDGE nur „a scendere“ | Verfügbarkeit + Nutzung ≤ 200 €/MWh | Piclo Flex | Pilote (352/2021) |
| **ES** | keine gefunden | flexible Zugangsrechte für Speicher | n. v. | n. v. | n. v. | Betriebsverfahren VNB in Arbeit **[unbestätigt]** |

---

## Bedeutung für unser Profil/Pitch

1. **„Pflicht-Steuerschnittstelle“ ist in AT keine Utopie, sondern seit 1.6.2026 geltendes Recht, allerdings
   unvollständig.** Pitch-Formel: *„Österreich hat mit § 76 ElWG die Pflicht geschaffen. Wir liefern das
   fehlende Stück: den Speicher in beide Richtungen, die unabhängige Verifikation und den Testabruf.“*
2. **Das Profil auf den Netzanschlusspunkt-Sollwert ausrichten** (§ 76 Abs. 3 ElWG, TOR 5.4.1.2), nicht auf
   Gerätebefehle. Die Geräte- bzw. EMS-Ebene hinter dem Zähler bleibt beim Betreiber. Das passt zu „Smart Meter
   verifiziert die Reaktion“, denn der Zähler misst genau am Anschlusspunkt. Die SNE-G-V verlangt für die
   flexible Entnahme ausdrücklich Zugriff auf die **Viertelstundenwerte**. Unser Mehrwert wäre eine feinere
   Auflösung und Echtzeit-Prüfung. Einschränkung: Mit heutiger AT-Infrastruktur gibt es Echtzeit und
   Unabhängigkeit nicht zugleich. Die Kundenschnittstelle (1–5 s) ist gegenüber dem Kunden nicht
   manipulationssicher, unabhängig sind nur die Backend-Werte, und die kommen z. B. in Wien einmal täglich
   (siehe 03) (korr. lt. 06).
3. **Den Testabruf juristisch verankern:** „nachweislich im Betrieb erreichen und erfolgreich Steuerbefehle
   umsetzen“ (§ 76 Abs. 2). Regelmäßige Testabrufe sind der Nachweis. In DE ist der „bestandene
   Fernsteuertest“ Voraussetzung für die Aufhebung der 60 %-Grenze.
4. **Signierte Befehle mit Grenzen und Fallback:** Die TOR verlangt einen Fallback bei Kommunikationsausfall und
   Cybersicherheit nach CRA/NIS2. Die RL 2024/1711 verlangt zertifizierte Leistungsregelsysteme bei flexiblen
   Anschlüssen. Beides stützt unser Sicherheitsdesign (siehe Block 4).
5. **Finanzierung:** Kosten für Flex und IKT sind netzentgeltfähig (EU Art. 32, AT § 139 Abs. 4). Kunden-
   anreize gibt es über die Entgeltbefreiung systemdienlicher Speicher (Bündelung ab 10 kW; gilt aber nur für
   Speicher „ausschließlich zur Wiedereinspeisung“, für PV-Heimspeicher zur Eigenverbrauchsoptimierung also
   nicht ohne Weiteres (korr. lt. 06)), den
   Leistungspreis-Abschlag für flexible Entnahme und ggf. marktbasierte Abrufe über die Plattform nach § 142.
   Die Argumentation lautet: Flex ist billiger als Kupfer (3 % Wind/PV-Jahresenergie in Netzen mit
   Ausbaubedarf → > 40 % (korr. lt. 06), BMWi-VNS; 11–29 Mrd. €/a EU, DNV).
6. **Lücke, die wir schließen:** Speicher fallen in den TOR je nach Netzwirkung unter Erzeugung oder Verbrauch.
   Für bidirektionale Steuerung fehlt ein Use Case [TOR-Stn]. Unser Profil kann genau diesen Use Case
   („Grid-Serving Storage“) für das OpenADR-AT-Profil vorschlagen.
7. **Vorsicht im Pitch:** keine Zwangsentladung ohne Vergütung fordern. In AT ist die bidirektionale Einschränkung
   unentgeltlich, aber freiwillig gegen Entgeltbefreiung, und diese Befreiung erreicht PV-Heimspeicher zur
   Eigenverbrauchsoptimierung wegen § 23 („ausschließlich zur Wiedereinspeisung“) nicht ohne Weiteres
   (korr. lt. 06). In NL ist Gegenrichtungs-Nutzung vergütet. Unsere
   Position: **Pflicht zur Schnittstelle, Freiwilligkeit plus Vergütung für aktives Entladen.**

---

## Offene Fragen an Smart Grids Austria

1. Wie weit ist das **OpenADR-AT-Profil** (Frist 31.10.2026 an die E-Control)? Enthält es Use Cases für
   **Speicher in beiden Richtungen** und bidirektionale Wallboxen? Beruht es auf OpenADR 2.0b (IEC 62746-10-1,
   so die TOR) oder auf OpenADR 3.1 (so Netz OÖ, 4.3.2026)? (korr. lt. 06)
2. Wird die Steuerschnittstelle nach § 76 auch für **neue Speicher** verpflichtend (z. B. über die TOR für
   Verbrauchsanlagen oder Speicher), oder bleibt es bei Erzeugungsanlagen?
3. Wie stellen die VNB die „Ansteuerbarkeit“ nach § 76 Abs. 2 nachweisbar her? Gibt es schon ein Konzept für
   **regelmäßige Testabrufe** und eine Dokumentation je Anlage?
4. Wie wird die „technische Aggregation“ nach § 24 Abs. 3 SNE-G-V praktisch umgesetzt? Wer ist Aggregator, und
   wie wird die Einhaltung „messtechnisch geeignet“ geprüft? Reicht der Smart Meter (15 min), oder braucht es
   eine Gerätemessung (vgl. EU Art. 7b)?
5. Welche Höhe wird der **Leistungspreis für flexible Entnahme** (§ 10 SNE-G-V) in der SNE-V 2027 haben?
6. Status des gemeinsamen VNB-Vorschlags nach § 139 Abs. 2 ElWG (Frist 9 Monate ab Inkrafttreten, also etwa
   Herbst 2026) und der **Flexibilitätsplattform § 142**: Sind Kleinspeicher als Anbieter vorgesehen?
7. Wie wird der Vorrang zwischen VNB-Vorgabe (Vortag 6:00/9:00) und Aggregator-Vermarktung (Regelreserve,
   Intraday) operativ gelöst? Gibt es eine Ampel-Logik?
8. Welche Latenz brauchen die VNB wirklich? Die TOR verlangt 1 Minute bis zum Sollwert. Reicht das für das
   kurative Engpassmanagement im Ortsnetz?

---

## Quellen

**EU (Primär)**
- [RL944] Richtlinie (EU) 2019/944, Art. 32. https://eur-lex.europa.eu/eli/dir/2019/944/oj (abgerufen als PDF über http://publications.europa.eu/resource/celex/32019L0944)
- [VO1747] Verordnung (EU) 2024/1747 (ändert VO 2019/943), Art. 2 Nr. 72–79, Art. 7a, 7b, 18, 19e–19h, ErwG 23. https://eur-lex.europa.eu/eli/reg/2024/1747/oj
- [RL1711] Richtlinie (EU) 2024/1711 (ändert RL 2019/944), Art. 6a, Art. 3. https://eur-lex.europa.eu/eli/dir/2024/1711/oj
- [ACER-NCDR] ACER, „New network code on demand response…“, 11.3.2025. https://www.acer.europa.eu/news/new-network-code-demand-response-will-further-advance-energy-transition
- [EC-NC] EU-Kommission, Electricity network codes and guidelines. https://energy.ec.europa.eu/topics/markets-and-consumers/wholesale-energy-market/electricity-network-codes-and-guidelines_en
- [EC-Kons] EU-Kommission, Targeted consultation NC DR. https://energy.ec.europa.eu/consultations/targeted-consultation-support-establishment-new-network-code-demand-response_en
- [Electron] Electron, „Your guide to the proposed EU network code on demand response“ (Stand 6.8.2026). https://electron.net/your-guide-to-the-eu-draft-network-code-on-demand-response/
- [EC-GAP] EU Action Plan for Grids, Factsheet. https://ec.europa.eu/commission/presscorner/api/files/attachment/876888/Factsheet_EU%20Action%20Plan%20for%20Grids.pdf

**Österreich (Primär)**
- [ElWG]/[RIS-ElWG] Elektrizitätswirtschaftsgesetz, BGBl. I Nr. 91/2025 (§§ 63, 76, 101, 103, 127, 128, 139, 140, 142). https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2025_I_91/BGBLA_2025_I_91.pdf
- [TOR-A-1.4] E-Control, TOR Stromerzeugungsanlagen Typ A, Version 1.4, gültig ab 1.6.2026, Kap. 5.4. https://www.e-control.at/documents/1785851/1811582/TOR+Stromerzeugungsanlagen+Typ+A+Version+1.4+(7).pdf/093752f5-e220-0731-b8a8-bfa85ccb7287?t=1780897058735
- [TOR-Stn] E-Control, Stellungnahmen zur Konsultation der TOR SEA V1.4. https://www.e-control.at/documents/1785851/1811582/Stellungnahmen+zur+Konsultation+der+TOR+SEA+V1.4.pdf/c86a9b93-0132-77bb-eebc-735ef2ff0e21?t=1780376483452
- [SNE-G-V] Systemnutzungsentgelte-Grundsatzverordnung, BGBl. II Nr. 299/2026 (12.10.2026), §§ 10, 11, 23–26, 32–33. https://www.ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2026_II_299/BGBLA_2026_II_299.pdf
- [SNE-V-Nov-2025] SNE-V-Novelle, BGBl. II Nr. 305/2025. https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2025_II_305/BGBLA_2025_II_305.rtf
- [WKO-ElWG] WKO, Präsentation Stromnetz-Rahmen ElWG (März 2026). https://www.wko.at/oe/news/praesentation-stromnetz-rahmen-elwg-fuerst.pdf
- [WN-SNE] Wiener Netze, Systemnutzungsentgelte temporäre Anlagen NE 7 2026. https://www.wienernetze.at/o/document/systemnutzungsentgelte-fuer-temporaere-anlagen-in-der-netzebene-7_2026_bf
- [CEER-RFR25] CEER Regulatory Frameworks Report 2025, Annex 5. https://www.ceer.eu/wp-content/uploads/2026/01/RFR25-Annex-5.pdf

**Österreich (Sekundär)**
- [Freshfields] Freshfields, „Austria's new Electricity Act…“ (16.12.2025). https://www.freshfields.com/en/our-thinking/blogs/sustainability/austrias-new-electricity-act-navigating-the-grid-of-tomorrow-key-changes-for-gr-102ly58
- [Energiezukunft-AT] energiezukunft.eu, „Strommarktreform in Österreich beschlossene Sache“. https://www.energiezukunft.eu/politik/strommarktreform-in-oesterreich-beschlossene-sache
- [FINGREEN] FINGREEN-Studie für AK Wien (7/2025), zitiert AIT 2024. https://wien.arbeiterkammer.at/interessenvertretung/wirtschaft/klimadialog/FINGREEN_Studie_20250708.pdf
- [OE-Netzentgelte] Oesterreichs Energie, Kurzstudie Entwicklung Netzentgelte (6/2025). https://oesterreichsenergie.at/fileadmin/user_upload/Kurzstudie_Entwicklung_Netzentgelte_%C3%96sterreich_Juni-2025_final__002_.pdf

**Deutschland**
- [BNetzA-14a] Bundesnetzagentur, Steuerbare Verbrauchseinrichtungen (§ 14a EnWG). https://www.bundesnetzagentur.de/DE/Vportal/Energie/SteuerbareVBE/start.html
- Preisblätter 2026 (Beispiele Modul 1–3): Netze ODR https://www.netze-odr.de/fileadmin/Netze-ODR/Dokumente/Unternehmen/Veroeffentlichungen/Netzentgelte/Netzentgelte_Strom_2026.pdf · [Wemag] https://www.wemag-netz.de/media/506/download · [SWBS] https://www.stwbs.de/fileadmin/Dokumente/Netz/Strom/LRV_Strom/SW_BS_vorl._Preisblatt_NN_Strom_2026.pdf · ENERGIE https://die-energie.de/fileadmin/netz/Netzinfo/Marktpartner/Preisinformationen/Strom/ENERGIE_Strom_Preisblatt_2026_endg%C3%BCltig_20251215.pdf
- [§14c] § 14c EnWG. https://www.gesetze-im-internet.de/enwg_2005/__14c.html
- [§13k] § 13k EnWG. https://www.gesetze-im-internet.de/enwg_2005/__13k.html · [ÜNB-13k] Umsetzungskonzept 2.0 (1.4.2026). https://www.netztransparenz.de/cdn/files/37bd9764-d02a-46de-fce9-08de8bf3161c/2026-04-01%20%C3%BCnb%20umsetzungskonzept%20%C2%A713k%20enwg.pdf
- [pv-magazine] BSW-Solar-Merkblatt Solarspitzengesetz (18.2.2025). https://www.pv-magazine.de/2025/02/18/bsw-solar-veroeffentlicht-merkblatt-zum-solarspitzen-gesetz/
- [Rödl-AgNes] Rödl & Partner, AgNes-Zwischenstand (1.9.2026). https://www.roedl.com/insights/netzentgelte-strom-agnes-zwischenstand/ · Festlegungsentwurf (19.8.2026) https://www.roedl.com/insights/agnes-festlegungsentwurf-netzentgelte-ab-2029/
- [VKU-NEST] VKU Anwendungshilfe NEST (21.1.2026). https://www.vku.de/fileadmin/user_upload/Energiewirtschaft/Dokumente/260121_VKU_Anwendungshilfe-NEST.pdf · [Noerr] https://www.noerr.com/de/insights/nest-beschlusse-bringen-dynamik-in-die-netzentgeltregulierung-fur-strom-und-gas · [BDEW-Stn] https://www.lobbyregister.bundestag.de/media/2f/5c/624014/Stellungnahme-Gutachten-SG2509300247.pdf
- [BDEW-2015] BDEW, Smart-Grids-Ampelkonzept (10.3.2015). https://www.bdew.de/media/documents/Stn_20150310_Smart-Grids-Ampelkonzept.pdf · [BDEW-2017] Konkretisierung Ampelkonzept. https://www.bdew.de/media/documents/20170210_Konkretisierung-Ampelkonzept-Smart-Grids.pdf
- [VDE-Flex] VDE FNN, Flexibilität im Verteilnetz. https://www.vde.com/flexibilitaet-im-verteilnetz
- [BMWi-VNS] E-Bridge/IAEW/OFFIS, „Moderne Verteilernetze für Deutschland“, BMWi, 12.9.2014. https://www.offis.de/fileadmin/content/files/download_tools/roadmaps_und_studien/BMWi_Verteilernetzstudie.pdf
- [BW-VNS] Verteilnetzstudie Baden-Württemberg (Pressemitteilung). https://www.baden-wuerttemberg.de/de/service/presse/pressemitteilung/pid/verteilnetzstudie-fuer-baden-wuerttemberg-veroeffentlicht-1
- [Agora] Agora Energiewende, „Haushaltsnahe Flexibilitäten nutzen“ (2023). https://www.agora-energiewende.de/fileadmin/Projekte/2023/2023-14_DE_Flex_heben/A-EW_315_Flex_heben_WEB.pdf

**Niederlande**
- [ACM-CSC] ACM, Codebesluit capaciteitssturingscontract (ACM/25/196733, 11.12.2025). https://www.acm.nl/nl/node/28583
- [ACM-QA] Solarmagazine zur ACM-Q&A Congestiemanagement. https://solarmagazine.nl/nieuws-zonne-energie/i28218/acm-presenteert-q-a-over-congestiemanagement-nieuwe-regels-per-25-november-van-kracht
- [ACM-ATR] Factsheet alternatieve transportrechten (2024). https://uploads-ssl.webflow.com/5bd6c7165d02ac3a1604bf29/660d6a6c5dbd6ef51cb608c5_240402%20Factsheet%20alternatieve%20transportrechten%20(versie%201.0).pdf
- [Solarmagazine-GOPACS] https://solarmagazine.nl/nieuws-zonne-energie/i41946/gopacs-en-nord-pool-bundelen-krachten-voor-congestiemanagement-stroomnet
- [Solarmagazine-TAN] https://solarmagazine.nl/nieuws-zonne-energie/i43666/tijdsafhankelijke-nettarieven-consumenten-in-2029-van-start-prijs-verschilt-per-seizoen

**Frankreich**
- [Enedis-S1-2026] Enedis, AO Flexibilités S1 2026. https://www.enedis.fr/media/5115/download · Ergebnisse RFQ-2601 https://www.enedis.fr/media/5334/download
- [Enedis-S2-2025] Enedis, Ergebnisse S2 2025. https://www.enedis.fr/media/5006/download
- [CRE-2026-161] CRE, Délibération 2026-161 (22.7.2026), Portail Flexibilités. https://www.cre.fr/fileadmin/Documents/Deliberations/2026/260722_2026-161_Avis_Regles_Portail_Flexibilites.pdf
- [Voltalis] Voltalis, AO Enedis 2025. https://group.voltalis.com/wp-content/uploads/2026/08/AO-Enedis-2025-1.pdf
- [HelloWatt] https://www.hellowatt.fr/blog/heures-creuses-creneau-11h-14h-debloque/ · [Kelwatt] https://www.kelwatt.fr/actu/rte-enedis-portail-flexibilites-locales-2026

**Italien**
- [EDGE-2026] E-Distribuzione, Progetto EDGE – Relazione tecnica 2026. https://www.e-distribuzione.it/content/dam/e-distribuzione/04_progetti-e-innovazioni/edge/2026/relazione-tecnica.pdf
- [QualEnergia] QualEnergia zu UVAM-Auktionen 2019. https://www.qualenergia.it/pro/articoli-pro/uvam-terna-assegna-1006-mw-per-marzo/

**Spanien**
- [PwC-CNMC] PwC, Resolución CNMC permisos de acceso flexibles. https://periscopiofiscalylegal.pwc.es/resolucion-de-la-cnmc-por-la-que-se-establecen-los-permisos-de-acceso-flexibles-de-la-demanda-a-las-redes-de-transporte-y-distribucion-en-desarrollo-de-la-circular-1-2024/
- [Osborne Clarke] https://www.osborneclarke.com/es/insights/la-cnmc-aprueba-la-regulacion-por-la-que-se-establecen-los-permisos-de-acceso-flexible-de

**EU-Studien**
- [DNV] DNV/smartEn, „Demand-side flexibility: Quantification of benefits in the EU“ (9/2022). https://www.dnv.com/publications/demand-side-flexibility-quantification-of-benefits-in-the-eu-232342
- [Eurelectric] Eurelectric/EY, „Grids for Speed“ (2024). https://www.tos.lth.se/fileadmin/tos/docs/Grids-for-Speed_Report.pdf · Zusammenfassung https://www.pveurope.eu/markets/eurelectric-double-investments-power-distribution-or-lose-race-net-zero
