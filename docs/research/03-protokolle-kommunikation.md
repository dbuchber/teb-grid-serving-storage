# 3. Protokolle & Kommunikation

Stand: 23.10.2026. Recherche-Block 3 zum Rechercheplan (`00-rechercheplan.md`).
Jede Aussage hat eine Quelle. Was nicht aus einer Quelle belegt ist, steht als
**[unbestätigt]** oder **[eigene Rechnung]** im Text. Quellen sind mit [Qn]
nummeriert, die Liste steht am Ende.

---

## Kernaussagen

1. **Kein einziges Protokoll deckt die Kette Netzbetreiber → Gerät → Verifikation ab.**
   IEEE 2030.5/CSIP(-AUS) und OpenADR sind Protokolle für den Weg vom Netzbetreiber
   zum Standort (WAN). EEBus (LPC/LPP), S2 und SunSpec Modbus sind lokale Protokolle
   im Gebäude. Das Profil braucht deshalb zwei Ebenen: einen WAN-Befehl
   (Segment/Standort) und eine lokale Pflichtschnittstelle am Gerät [Q9][Q14][Q20][Q24].
2. **Für aktives Laden und Entladen reichen die §14a-Use-Cases nicht.** EEBus LPC/LPP
   und die FNN-Steuerbox *begrenzen* nur Bezug oder Einspeisung [Q15][Q17]. Ein
   Sollwert „entlade jetzt X kW“ braucht ein Modell mit Wirkleistungs-Sollwert:
   SunSpec 704 (DER AC Controls) [Q22], IEEE 2030.5 DERControl [Q11] oder S2, das
   Speicher über den Ladezustand (SoC) modelliert [Q19]. Die genauen Feldnamen und
   Vorzeichen sind **[unbestätigt]**, weil die Spezifikationstexte nicht abrufbar waren.
3. **Australien zeigt, was ein Profil über das Kundeninternet leistet.** Im
   (freiwilligen) Feldversuch von SA Power Networks hielten die Anlagen dynamische Exportgrenzen in
   >99,97 % der 5-Minuten-Intervalle ein (laut Gerätemonitoring, nicht Zählerdaten). Die
   Wechselrichter waren aber nur **89,3 %** der Tageslichtzeit erreichbar. Bei Kommunikationsausfall
   fallen sie auf einen festen Ersatzwert von 1,5 kW je Phase zurück [Q12]. Die Pflicht (Dynamic
   Exports Regulations) kam erst nach dem Feldversuch (korr. lt. 06). Das Kundeninternet reicht also, wenn ein
   lokaler Rückfallwert definiert ist, aber nicht als einziger Kanal für Notfälle.
4. **Der österreichische Smart Meter kann die Reaktion nur lokal fast in Echtzeit zeigen.**
   Die Kundenschnittstelle sendet nur („Push only“), alle 5 s (Salzburg Netz), verschlüsselt
   mit AES-128 und einem Schlüssel vom Netzbetreiber [Q27]. Andere Varianten senden alle
   1 s [Q26]. Über das Backend kommen die Daten in Wien dagegen nur einmal täglich
   [Q29]. Verifikation in Echtzeit heißt also: Das Modul liest die Kundenschnittstelle
   lokal mit. Gerichtsfeste Abrechnung heißt: Viertelstundenwerte am Folgetag.
5. **LoRaWAN-Multicast passt technisch als Befehlskanal für ein Netzsegment.** Der
   Downlink-Unterkanal 869,4–869,65 MHz erlaubt 10 % Duty Cycle und 500 mW ERP (regulatorischer
   Rahmen nach ETSI/ERC; LoRaWAN-Default EU868 ist Max. EIRP +16 dBm) [Q1] (korr. lt. 06).
   TS005 legt Multicast-Gruppen mit eigenen Schlüsseln für Class B/C fest [Q3][Q5].
   Multicast hat aber **keine Quittung**, die Rückmeldung muss also über einen anderen
   Kanal laufen [Q5]. Bei SF9 dauert ein unsignierter Befehl von etwa 40 Byte rund 0,33 s
   Sendezeit (≈ 1.000/h). Mit 64-Byte-Signatur (ca. 104 Byte Nutzlast + 13 Byte Overhead)
   sind es rund 0,64 s, also etwa **560 signierte Segmentbefehle pro Stunde** und Gateway im
   Unterkanal **[eigene Rechnung]** (korr. lt. 06). Den Unterkanal teilen sich alle
   RX2-Antworten (Join-Accept, ACKs) des Gateways (korr. lt. 06).
6. **Signaturen müssen in der Anwendungsschicht liegen.** Bei LoRaWAN-Multicast kennen
   alle Geräte der Gruppe denselben Gruppenschlüssel [Q5]. Ein kompromittiertes Gerät
   könnte also gültige Gruppen-Frames erzeugen **[eigene Ableitung]**. Deshalb braucht
   jeder Befehl eine asymmetrische Signatur des Netzbetreibers (z. B. 64 Byte ECDSA/Ed25519).
   Das passt erst ab DR3 (115 Byte Nutzlast), nicht bei DR0–2 (51 Byte) [Q5][Q4].
7. **Engpassmanagement braucht Minuten, keine Millisekunden.** Die Öl-Zeitkonstante eines
   Ortsnetztrafos liegt nach IEC 60076-7 bei 180 min, gemessen 129–199 min [Q33]. §14a
   erlaubt bis Ende 2028 präventive Zeitfenster bis 2 h/Tag und verlangt ab 2029 eine
   Steuerung nur bei Engpass in Echtzeit [Q31]. SAPN rechnet Hüllkurven im 15-Minuten-Takt
   [Q12]. Ziel für das Profil: Befehl umgesetzt in **≤ 1 min**, verifiziert im nächsten
   Messintervall. Schnelle Spannungshaltung bleibt lokal und autonom (Q(U)/P(U)).

---

## Vergleichstabelle Protokolle

| Protokoll | Zweck / Ebene | Verbreitung | Security | Laden/Entladen-Sollwerte? | Status 2026 |
|---|---|---|---|---|---|
| **IEEE 2030.5 (SEP 2.0) + CSIP / CSIP-AUS** | Netzbetreiber-Server → Gerät, Gateway oder Hersteller-Cloud (WAN). REST über HTTP [Q10]. Drei Integrationsmodelle: direkt, Gateway, Cloud [Q12] | Kalifornien: Rule 21 Phase 2 seit 22.06.2020 Pflicht, Standardprotokoll IEEE 2030.5 [Q13]. Australien: CSIP-AUS (SA HB 218, Tests nach SA TS 5573:2025) bei SAPN und AusNet [Q10][Q12] | Mutual TLS, PKI mit Gerätezertifikaten [Q10]. SAPN betreibt eigene CA (SERCA), Übergang zu nationaler PKI (AEMO) vorgeschlagen [Q12]. TLS-Version laut Quellen uneinheitlich **[unbestätigt]** | Ja: DERControl mit Startzeit, Dauer und Randomisierung [Q11]. CSIP-AUS nutzt Standort-Export-/Importgrenzen statt direkter Gerätesteuerung [Q12]. Explizite Speicher-Sollwerte **[unbestätigt]** | IEEE 2030.5-2023 aktuell, mit EV-Laden und erweitertem DER-Monitoring [Q11] (Sekundärquelle). CSIP-Pflege seit 12/2024 bei SunSpec [Q13] |
| **OpenADR 2.0b / 3.x** | Signal/Preis/Event vom Programmbetreiber (VTN) an Kunden-EMS (VEN), WAN | Weit verbreitet in US-Demand-Response. 3.0 seit 2024 veröffentlicht [Q6][Q7] | 2.0b: X.509v3 für Client und Server, TLS 1.2, PKI über OpenADR-CA [Q8]. 3.0: REST/JSON, OAuth2 Client Credentials plus TLS [Q6] | Eher Events/Preise/Grenzen an ein EMS, nicht ein Gerätemodell für Speicher **[unbestätigt]** | 3.0 in der Spezifikationsliste, 3.0.1 mit Webhooks, 3.1 mit Message Queue geplant [Q6][Q7]. AT: TOR V1.4 verweist auf IEC 62746-10-1 (= OpenADR 2.0b), Netz OÖ arbeitet dagegen mit OpenADR 3.1 (Folien 4.3.2026); Version des AT-Profils offen (korr. lt. 06) |
| **EEBus (SPINE/SHIP), Use Cases LPC/LPP** | Lokal (HAN): Steuerbox/HEMS → Gerät. SHIP = TLS-Transport mit Pairing über TCP/IP, SPINE = Datenmodell [Q14] | DE: Pflicht-Digitalschnittstelle der FNN-Steuerbox (neben Relais und KNX) für §14a [Q16][Q17]. Wechselrichter z. B. Kostal Plenticore G3 mit LPC/LPP [Q15] | SHIP: TLS, Zertifikate über SKI, Pairing [Q14][Q18]. Open-Source-Stacks setzen PIN-Prüfung nur teilweise um [Q18] | **Nur Begrenzung** (LPC: Bezug, LPP: Einspeisung). Bei Heartbeat-Verlust gilt ein Failsafe-Grenzwert [Q15]. Aktives Entladen deckt das nicht ab | SPINE/SHIP 2025 als IEC 63380-2/-3 übernommen [Q14]. LPP-Testspezifikation 1.0.0 vom 30.04.2024 [Q15] |
| **IEC 61850-7-420** | Datenmodell (Logical Nodes) für DER inkl. Speicher und steuerbare Lasten; eher Netzleittechnik und größere Anlagen | Bei Heimspeichern kaum belegt **[unbestätigt]** | Über IEC 62351 **[unbestätigt]** | Modelliert Speicher als DER-Typ [Q23]. Namen der Speicher-LNs nicht verifiziert | Edition 2 (2021) ersetzt Ed. 1 (2009) [Q23] |
| **SunSpec Modbus (700er-Modelle, IEEE 1547-Profil)** | Lokal: Register-Modell am Wechselrichter über Modbus TCP/RTU | 700er-Serie seit 04/2021 freigegeben, Basis für US-Zertifizierung [Q21] | Modbus selbst ohne Authentifizierung **[unbestätigt, Protokollwissen]**. Nur im abgeschotteten LAN oder hinter einem Modul einsetzen | Ja: 704 DER AC Controls (Wirkleistung), 702 Kapazität, 705 Volt-Var [Q22]. Speichermodelle (713/714) **[unbestätigt]** | DER Information Model Spec v1.2, IEEE 1547-2018 Profile v1.1 (2025) [Q22] |
| **S2 (EN 50491-12-2)** | Lokal: CEM ↔ Resource Manager, beschreibt die Flexibilität eines Geräts statt eines Use Cases [Q19][Q20] | Pilotphase, „Henne-Ei-Problem“ bei der Verbreitung [Q20] | Die Norm regelt Security ausdrücklich nicht [Q19] | Ja, generisch: Speicher über SoC und Betriebsmodi (Operation Modes) [Q19] | EN seit 04/2022, IEC-Pendant IEC 63402-2-2 in Arbeit oder erschienen [Q19][Q20] |
| **SMGW + CLS + FNN-Steuerbox (DE, §14a)** | Netzbetreiber → SMGW (WAN, BSI-PKI) → CLS-Kanal (TLS über HAN) → Steuerbox → Relais / EEBus / KNX [Q17][Q34] | Steuerboxen zertifiziert (u. a. Theben, Vivavis, Swistec) [Q34]. Einige Netzbetreiber lassen vorerst nur Direktansteuerung zu [Q16] | BSI TR-03109-5 für CLS-Komponenten, Konformitätsbewertung plus Zertifizierung [Q34] | Nur Begrenzung (Mindestleistung 4,2 kW je Gerät bei Direktsteuerung) [Q31] | Lastenheft 1.5, Testfallspezifikation 1.2 (05/2026) [Q16][Q17]. MsbG verlangt funktionierende Steuerung bis 31.12.2026 [Q34] |

**Folgerung für das Profil:** WAN-seitig ein Modell nach dem Vorbild von IEEE 2030.5/CSIP-AUS
(Standortgrenzen plus Sollwerte, Zeitplan, Randomisierung, Rückfallwert). Lokal am Gerät
eine Pflichtschnittstelle, die *Sollwerte* kann (SunSpec 704 oder S2), nicht nur Grenzen
wie LPC/LPP.

---

## Österreich: Smart Meter und Rundsteuertechnik

**Kundenschnittstelle am Smart Meter**
- Die Schnittstelle ist rechtlich als *unidirektional* angelegt (§ 84 Abs 5 ElWOG 2010,
  § 3 Abs 5 IMA-VO 2011). Das stammt aus einem Forenbeitrag; der Primärtext war nicht
  abrufbar **[unbestätigt]** [Q28].
- Salzburg Netz (Kaifa, Honeywell): RJ12, wired M-Bus, DLMS/COSEM (IDIS), Security Suite 1,
  AES128-CBC mit Global Unicast Encryption Key, CMAC-Authentifizierung, **„Push only“, alle
  5 s**. Sie liefert Spannung, Strom, Wirkleistung ±P und Energiezähler ±A/±R [Q27].
- Österreichs Energie listet sechs verschiedene Security-Varianten (Suite 0, OMS Mode 5,
  Suite 1 mit GUEK, GUEK+GAK, AES-GCM-128 mit GPKs) und Push-Intervalle von 1 s oder 5 s
  [Q26]. Ein Adapter darf „keine Rückwirkungen“ auf den Zähler haben [Q26].
- Kundinnen und Kunden bekommen den Schlüssel vom Netzbetreiber über das Webportal oder per
  E-Mail [Q28][Q30].
- **Folge für die Verifikation:** Die Daten sind authentisch gegenüber Dritten, *nicht* aber
  gegenüber dem Kunden selbst. Der Kunde kennt den symmetrischen Schlüssel und könnte
  Telegramme fälschen **[eigene Ableitung]**. Für unabhängige Verifikation taugen deshalb
  nur die Backend-Werte des Netzbetreibers. Wiener Netze überträgt sie einmal täglich
  (Viertelstundenwerte nur bei Opt-in) [Q29].
- Anbindung der Zähler an das Backend: PLC im Band 9–95 kHz [Q38], G3-PLC z. B. bei
  Netz Burgenland [Q36]. Wiener Netze überträgt laut Sekundärquelle über Mobilfunk [Q29b].

**Rundsteuertechnik**
- Funktionsweise: Ein Tonfrequenzsignal (z. B. 750 Hz, allgemein 100–2.000 Hz) liegt auf der
  Netzspannung; es gibt **keinen Rückkanal** [Q39].
- Latenz: Bei Decabit dauert ein Bit 600 ms (30 Netzperioden) [Q40]. Ein Telegramm aus
  Start, 10 Daten- und Stoppbit dauert damit etwa 7 s **[eigene Rechnung]**.
- Österreich: ElWG erlaubt die Spitzenkappung auf 70 % der Modulleistung [Q41]. Wie verbreitet
  Rundsteuerempfänger bei PV in AT sind, ließ sich nicht belegen **[unbestätigt]**.
- Ein ähnliches Vorbild ohne Rückkanal sind LoRaWAN-Multicast-Befehle mit autonomem
  Weiterbetrieb, z. B. die Gas-Absperrventil-Demo von Senet/Oxit [Q42].

---

## Vergleichstabelle Kanäle

| Kanal | Latenz Befehl | Verfügbarkeit / Abdeckung | Kosten | Richtung | Multicast |
|---|---|---|---|---|---|
| **LoRaWAN Class C** (netzgespeistes Modul) | Sekunden: Empfänger dauernd offen [Q5]. Sendezeit SF9 ≈ 0,33 s pro Frame **[eigene Rechnung]** | AT: öffentliches Netz von Drei/Actility seit 10/2023 [Q37], Abdeckung nicht beziffert. Private Gateways je Trafostation möglich | Gering je Gerät **[unbestätigt]** | Downlink stark (10 % DC im Unterkanal P, 500 mW ERP nach ETSI; LoRaWAN-Default 16 dBm EIRP (korr. lt. 06)) [Q1]. Uplink 1 % DC [Q1] | Ja: TS005 mit Gruppenschlüssel und Gruppen-Frame-Counter [Q3][Q5]. Keine Quittung |
| **LoRaWAN Class B** | Bis 128 s (Beacon-Periode 128 s, Ping-Slot-Periode 0,96·2^p s, p = 0…7) [Q2b] | wie oben, braucht Beacon-fähige Gateways | wie oben | wie oben | Ja, nach Ping-Slot-Periode der Gruppe [Q2b] |
| **NB-IoT** | ~1 s im Normalfall, mehrere Sekunden bei erweiterter Abdeckung [Q35]. Mit PSM/eDRX bis Minuten oder Stunden (eDRX bis ~174 min) [Q36b] | Designziel 164 dB MCL (20 dB besser als GPRS) [Q35b] | SIM-Tarif je Gerät **[unbestätigt]** | bidirektional | Nur SC-PTM in Rel. 14 **[unbestätigt]**, praktisch unicast |
| **LTE-M** | ~100–150 ms im Normalfall [Q35]. eDRX bis ~43 min [Q36b] | gute Gebäudedurchdringung, Netzbetreiber-abhängig | SIM-Tarif **[unbestätigt]** | bidirektional | praktisch unicast |
| **Kundeninternet (WLAN/LAN)** | Sekunden **[unbestätigt]** | SAPN-Feldversuch: Geräte **89,3 %** der Tageslichtzeit erreichbar, Server 97,8 % [Q12] | keine für den Netzbetreiber | bidirektional | nein (Server-Fan-out) |
| **Smart-Meter-PLC (G3/PRIME)** | Netzgröße durch Ende-zu-Ende-Latenz begrenzt, keine Zahl gefunden [Q36] | in AT weit verbreitet [Q36][Q38] | im Zählernetz vorhanden | bidirektional, aber Kapazität für Messwerte vorgesehen | **[unbestätigt]** |
| **450 MHz (LTE450)** | LTE-typisch **[unbestätigt]** | DE: 450connect, ~1.600 Standorte geplant [Q43], SMGW-Anbindung seit 2025 [Q44]. AT: Lizenz bei ArgoNET [Q45]. Energie AG OÖ: 6.000 Stationen von CDMA450 auf LTE450 [Q46] | Netz für kritische Infrastruktur | bidirektional | **[unbestätigt]** |
| **Rundsteuertechnik** | Sekunden pro Telegramm (≈ 7 s Decabit) **[eigene Rechnung]** [Q40] | netzweit über das Stromnetz | vorhandene Sender | **nur Downlink** [Q39] | ja (Broadcast nach Gruppen) |

**LoRaWAN-Details:**
- **Unterkanal:** P = 869,4–869,65 MHz mit 10 %; die übrigen EU868-Unterkanäle haben 0,1–1 %
  [Q1]. RX2 liegt standardmäßig auf 869,525 MHz mit DR0 (SF12), bei TTN mit SF9 [Q2].
  Die vom Team genannte Bezeichnung „g3“ entspricht der älteren ERC-Nomenklatur
  **[unbestätigt]**.
- **Nutzlast:** DR0–2 51 Byte, DR3 115 Byte, DR4–5 222 Byte [Q5][Q4].
- **Durchsatz [eigene Rechnung]:** Formel nach Semtech, CR 4/5, 8 Präambelsymbole.
  - SF9, ~53 Byte PHY-Payload: ≈ 0,33 s Sendezeit → ≈ 1.090 Frames/h im 10-%-Unterkanal.
  - SF12, 51 Byte: ≈ 2,8 s → ≈ 128 Frames/h.
  - SF9, signierter Befehl (~104 Byte Nutzlast + 13 Byte LoRaWAN-Overhead): ≈ 0,64 s →
    ≈ 560 Befehle/h (korr. lt. 06).
- **Sicherheit:**
  - Unicast: AES-128 (AppKey). Die Nutzlast ist mit AppSKey AES-CTR-verschlüsselt, der MIC
    ist AES-CMAC mit NwkSKey über einen 32-bit-Frame-Counter [Q24][Q25].
  - Multicast: Gruppenschlüssel werden über McGroupSetup verteilt, mit einem gerätespezifischen
    Schlüssel verschlüsselt. Min/Max-Frame-Counter begrenzen die Gültigkeit. Bis zu 4 Gruppen
    je Gerät [Q3][Q5].
- **FUOTA:** Bei 1 % Duty Cycle dauert ein Unicast-Update eines einzigen Geräts ca. 17 h. Erst
  Multicast plus Fragmentierung (TS004) macht es praktikabel [Q5].

---

## Latenzanforderung

| Bezug | Zeitskala | Quelle |
|---|---|---|
| Öl-Zeitkonstante Ortsnetztrafo (ONAN) | 180 min (Norm), 129–199 min gemessen an 160/400/800 kVA | IEC 60076-7 nach [Q33] |
| Wicklungs-Zeitkonstante | einige Minuten (~4 min) | **[unbestätigt]**, nicht aus Quelle bestätigt |
| Erdkabel NS | thermisch träge, Stunden | **[unbestätigt]**, nur Methodik belegt [Q47] |
| §14a präventiv (bis Ende 2028) | Zeitfenster, max. 2 h/Tag | [Q31] |
| §14a ab 2029 | nur bei in Echtzeit festgestelltem Engpass, Dauer auf den Engpass begrenzt | [Q31] |
| SAPN Flexible Exports | Hüllkurven alle 15 min für 75.000 Trafos, Einhaltung im 5-min-Raster | [Q12] |
| Vergleich Regelreserve | FCR voll in 30 s, aFRR (Elia) 5 min | [Q48] |

**Bewertung:** Thermische Engpässe im Verteilnetz bauen sich über zehn Minuten bis Stunden auf.
Das Profil sollte daher Folgendes festlegen **[eigene Ableitung]**:
- **Befehl bis Wirkung ≤ 60 s** im Normalfall. Das reicht für Class C sicher; Class B mit p ≤ 5
  (≤ 30 s Ping-Periode) ebenfalls.
- **Verifikation im 15-min-Raster**, also am Abrechnungsintervall.
- Spannungsprobleme (Sekunden) regelt das Gerät **autonom vor Ort** über Kennlinien und nicht
  per Fernbefehl.

Schnellere Anforderungen nach dem FCR-Vorbild sind ein anderer Anwendungsfall (Systemdienstleistung)
und gehören nicht in dieses Profil.

---

## Empfehlung

**Befehl (Netzbetreiber → Segment)**
- **Abweichung von TOR Typ A V1.4 (AT):** Die TOR legt OpenADR über das Kundeninternet fest,
  „eine Kommunikation über Drittsysteme ist nicht vorgesehen“. LoRaWAN wäre in AT ein
  zusätzlicher Kanal neben OpenADR, ein Hersteller-Cloud-Pfad wäre nicht TOR-konform. Das muss
  das Profil als Abweichung bzw. Ergänzung begründen (korr. lt. 06).
- Primär: **LoRaWAN Class C Multicast** je Netzsegment (Trafo- oder Abgangsgruppe). Das Modul
  ist netzgespeist, also ist Class C ohne Batterieproblem möglich. Gruppenverwaltung nach TS005.
  Downlink im 10-%-Unterkanal mit DR3 oder höher, damit eine Signatur passt.
- Inhalt: kompakter, **asymmetrisch signierter** Befehl, z. B. „Segment S, Modus Laden/Entladen,
  Sollwert in % Pmax, Start, Dauer, Randomisierung, Ablaufzeit, Sequenznummer“. Dazu lokale
  Plausibilitätsgrenzen. Bei fehlendem Befehl gilt der Rückfallwert nach dem SAPN-Vorbild [Q12].
- Alternativ, wo kein LoRaWAN vorhanden ist: derselbe signierte Befehl über **IEEE 2030.5-artiges
  REST über Internet/LTE**, unicast an Standort oder Hersteller-Cloud [Q12] (Cloud-Pfad in AT
  nicht TOR-konform, korr. lt. 06). Die Signatur ist
  unabhängig vom Kanal; das ist der Kern der Interoperabilität.

**Rückmeldung (Gerät → Netzbetreiber)**
- **Internet/LTE-M** (Kundeninternet, Rückfall auf LTE-M): Quittung, Ist-Leistung, SoC, Status.
- LoRaWAN-Uplink nur für kurze Quittungen mit Randomisierung. Bei 1 % Duty Cycle und vielen
  Geräten gleichzeitig kommt es sonst zu Kollisionen **[eigene Ableitung]**.

**Verifikation**
- Echtzeit: Das Modul liest die **Smart-Meter-Kundenschnittstelle** (1–5 s Push) mit und
  meldet die Wirkung mit [Q26][Q27]. Das ist nicht manipulationssicher gegenüber dem Kunden.
- Verbindlich: **15-min-Lastgang aus dem Netzbetreiber-Backend** (Folgetag) für Vergütung
  und Testabruf-Statistik [Q29].

**Lokale Pflichtschnittstelle am Gerät**
- Wechselrichter und Speicher bieten einen *Sollwert*-fähigen offenen Standard an, z. B.
  **SunSpec Modbus 704** oder **S2**. EEBus LPC/LPP bleibt zusätzlich für §14a-Begrenzungen
  erhalten. Die Pflicht schreibt Fähigkeiten vor, kein bestimmtes Protokoll, so wie Rule 21 /
  CSIP es mit einem Standardprotokoll plus Ausnahme bei Einvernehmen tut [Q13].

---

## Offene Fragen an Smart Grids Austria

1. Gibt es in AT ein Vorhaben, die Kundenschnittstelle **bidirektional** zu machen oder Steuer-
   funktionen über den Zähler bzw. das Zählernetz (PLC) bereitzustellen? Rechtlich ist sie heute
   unidirektional [Q28].
2. Welche **Verbreitung und Restlaufzeit** hat die Rundsteuertechnik in den österreichischen
   Verteilnetzen? (Zu den TOR: Kap. 6.2.1 verlangt potentialfreie Kontakte am Fernwirkgerät,
   z. B. Funkrundsteuerempfänger, nur „falls im Netzanschlussvertrag vorgesehen“, siehe 05;
   eine generelle Pflicht ist das nicht (korr. lt. 06).)
3. Akzeptieren Netzbetreiber **LoRaWAN (Drei-Netz oder eigene Gateways)** als Kanal für kritische
   Befehle, oder ist **450 MHz (ArgoNET, eigene LTE450-Netze)** gesetzt [Q45][Q46]?
4. Welche **Segmentgröße** ist für Engpassmanagement sinnvoll (Trafo, Abgang, Strang), und wie
   bilden Netzbetreiber Kunden auf Segmente ab?
5. Welche **Reaktionszeit** würden Netzbetreiber vertraglich verlangen (1 min, 5 min, 15 min)?
6. Ist es zulässig, die **15-min-Werte aus dem Backend** für Verifikation und Testabrufe zu nutzen
   (Datenschutz, IMA-VO, Opt-in)?
7. Wer betreibt die **PKI** für signierte Befehle: Netzbetreiber, E-Control oder ein gemeinsamer
   Dienst (Vorbild SAPN → AEMO) [Q12]?
8. § 76 ElWG schreibt die Pflicht-Steuerschnittstelle für Erzeugungsanlagen bereits vor (siehe 01).
   Soll sie auf **Speicher mit Lade-/Entlade-Sollwert** ausgeweitet werden, analog zu Rule 21 und
   CSIP-AUS? (korr. lt. 06)
9. Welche **OpenADR-Version** nutzt das AT-Profil: 2.0b (IEC 62746-10-1, X.509/TLS 1.2) oder 3.1
   (Netz OÖ, OAuth2/TLS)? (korr. lt. 06)

---

## Quellenliste

- [Q1] The Things Network: Regional limitations of RF use (ETSI-Unterkanäle K–Q). https://www.thethingsnetwork.org/docs/lorawan/regional-limitations-of-rf-use/
- [Q2] Actility: LoRaWAN EU863-870 MHz Band Guide (RX2 869,525 MHz, DR0). https://www.actility.com/lorawan-eu863-870-mhz-band/; TTN EU868: https://www.thethingsnetwork.org/docs/lorawan/regional-parameters/eu868/
- [Q2b] Abdelfadeel et al. / Sekundärquellen zu Class B (Beacon 128 s, Ping-Slot 0,96·2^p s): https://arxiv.org/pdf/2409.20408 ; ThingPark-Doku: https://docs.thingpark.com/thingpark-enterprise/7.3/docs/user-guide-tpe/manage-devices/activate-new-devices/supported-classes-of-lora-devices
- [Q3] LoRa Alliance: TS005-2.0.0 Remote Multicast Setup (14.04.2022). https://resources.lora-alliance.org/document/ts005-2-0-0-remote-multicast-setup ; v1.0.0: https://lora-alliance.org/resource_hub/lorawan-remote-multicast-setup-specification-v1-0-0/
- [Q4] AWS Whitepaper LPWAN/LoRaWAN (DR0 51 Byte). https://docs.aws.amazon.com/whitepapers/latest/implementing-lpwan-solutions-with-aws/lorawan.html
- [Q5] Abdelfadeel, Farrell, McDonald, Pesch: How to make Firmware Updates over LoRaWAN Possible (arXiv 2002.08735). Tabelle DR/Nutzlast, Class-C/B-Multicast, McGroupSetup, 17-h-Beispiel. https://arxiv.org/pdf/2002.08735
- [Q6] OpenADR Alliance: Webinar „From 2.0 to 3.0“ (11/2023) und 3.0-Deep-Dive. https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf ; https://www.openadr.org/assets/1_2_1_Deep%20Dive%20in%20OpenADR%203.0.pdf
- [Q7] OpenADR Specification-Seite. https://www.openadr.org/specification ; stadt+werk 16.05.2024: https://stadt-und-werk.de/meldung_43734_Version+3.0+von+OpenADR+erschienen.pdf
- [Q8] OpenADR Alliance: Security Certificates – a brief overview. https://www.openadr.org/assets/openadr%20security%20certificates%20-%20a%20brief%20overview%20-%20v1.pdf ; https://www.openadr.org/assets/security_alliancemeeting_jim.pdf
- [Q9] OpenADR/EEBus-Workshop. https://www.openadr.org/assets/2_2_5_OpenADR%20EEBUS.pdf
- [Q10] Codibly: CSIP Guide (IEEE 2030.5, mTLS, PKI). https://codibly.com/blog/articles/csip-guide-ieee-2030-5-certification ; pv magazine Australia (CSIP-AUS, SAPN über iSolarCloud): https://www.pv-magazine-australia.com/?p=14220
- [Q11] VOLTTRON: IEEE 2030.5 DER Support (DERProgram/DERControl, Randomisierung). https://volttron.readthedocs.io/en/releases-7.x/specifications/ieee2030_5_agent.html ; SunSpec-Blog zu IEEE 2030.5-2023: https://sunspec.org/blog-ieee-2030-5/
- [Q12] SA Power Networks: Flexible Exports for Solar PV Trial – Final Report v1.3 (19.10.2023), ARENA. https://arena.gov.au/assets/2024/01/SA-Power-Networks-Flexible-Exports-for-Solar-PV-Trial-Final-Report.pdf
- [Q13] SunSpec: California Rule 21 Phase 2 Goes Into Effect. https://sunspec.org/california-rule-21-phase-2-goes-into-effect-this-month ; QualityLogic Intro 2030.5: https://www.qualitylogic.com/wp-content/uploads/2020/09/QL-Intro-to-2030.5-Webinar-AU-091420.pdf
- [Q14] innobu: EEBUS / IEC 63380 (2026). https://www.innobu.com/de/artikel/eebus-iec-63380-han-hems-2026.html ; openmuc jEEBus: https://openmuc.org/eebus
- [Q15] Kostal Plenticore G3: Leistungsbegrenzung §14a (LPC/LPP über FNN-Steuerbox). https://documents.kostal.com/PLENTICORE-G3/BA/en-GB/581546763581584779.html ; evcc EEBus HEMS (Failsafe LPP): https://docs.evcc.io/en/external-limit/awatt-electronic-hems-pro-eebus
- [Q16] VDE FNN: Testfallspezifikation Steuerbox 1.2 (12.05.2026). https://www.vde.com/de/fnn/aktuelles/testfallspezifiktion-steuerbox ; LokalWerke Infoblatt §14a (20.10.2025): https://lokalwerke.de/wp-content/uploads/2025/10/11.2.9.4-FB_Informationsblatt-§14a-EnWG.pdf
- [Q17] VDE FNN: Steuerbox fit für die netzorientierte Steuerung (Lastenheft 1.4/1.5, BSI-TR-03109-5). https://www.vde.com/de/fnn/aktuelles/steuerbox-fit-fuer-die-netzorientierte-steuerung ; BayWa r.e./Enphase §14a: https://solar-distribution.baywa-re.de/out/media/225288.DMS_teb-00327-de-de-enwg-14a-compliant-sys.pdf
- [Q18] enbility ship-go (SHIP 1.0.1, Einschränkungen). https://github.com/enbility/ship-go ; evcc EEBus-Konfiguration: https://docs.evcc.io/en/reference/configuration/eebus
- [Q19] S2-Überblick, OpenADR Users Conference 2024. https://www.openadr.org/assets/2_2_3_S2%20overview%20-%20OpenADR%20Users%20Conference.pdf ; NEN-EN 50491-12-2: https://standards.globalspec.com/std/14517744/nen-en-50491-12-2
- [Q20] TNO/ElaadNL: S2 Current state and future developments (02/2026). https://elaad.nl/wp-content/uploads/downloads/S2-Current-state-and-future-developments-Res-Flex-Feb-2026.pdf ; LF Energy: https://lfenergy.org/interoperability-technologies-behind-the-meter-s2-standard/
- [Q21] SunSpec: 700 Series DER Information Models APPROVED. https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/
- [Q22] SunSpec DER Information Model Specification v1.2. https://sunspec.org/wp-content/uploads/2025/01/SunSpec-DER-Information-Model-Specification-V1-2.pdf ; IEEE 1547-2018 Profile v1.1: https://sunspec.org/wp-content/uploads/2025/01/SunSpec-Modbus-IEEE-1547-2018-Profile-Specification-and-Implementation-Guide-v1.1-1.pdf
- [Q23] IEC 61850-7-420:2021 (Ed. 2), Normenseiten. https://webstore.ansi.org/standards/iec/iec61850420ed2021 ; https://genorma.com/en/standards/iec-61850-7-420-2021-ed2
- [Q24] LoRa Alliance: LoRaWAN Security Whitepaper. https://lora-alliance.org/sites/default/files/2019-05/lorawan_security_whitepaper.pdf
- [Q25] TTN: LoRaWAN Security. https://www.thethingsnetwork.org/docs/lorawan/security/index.html
- [Q26] Oesterreichs Energie: Konzept Smart-Meter-Kundenschnittstellen-Adapter (Stand 02/2021). https://oesterreichsenergie.at/fileadmin/user_upload/Smart_Meter-Plattform/20200201_Konzept_Kundenschnittstelle_SM.pdf
- [Q27] Salzburg Netz: Technische Beschreibung Kundenschnittstelle Smart Meter (10/2026). https://www.salzburgnetz.at/content/dam/salzburgnetz/dokumente/stromnetz/Technische-Beschreibung-Kundenschnittstelle.pdf
- [Q28] openHAB-Community: DSMR binding for Austrian Smart Meters (Keys GUEK/GAK, ElWOG/IMA-VO-Verweis). https://community.openhab.org/t/dsmr-binding-for-austrian-smart-meters/90649
- [Q29] Wiener Netze: Factsheet Funktionen des Smart Meters (03/2021). https://wienernetze.at/o/document/wn-sm-factsheet-funktionen
- [Q29b] futurezone: Wiener Netze 800.000 Smart Meter (Übertragung über Mobilfunk). https://futurezone.at/digital-life/wiener-netze-smart-meter-ausbau-800000-installiert/402327078
- [Q30] Eniris: Connect EMS to Austrian Smart Meters (Zählerschlüssel). https://eniris.com/news/how-to-connect-your-eniris-ems-to-austrian-smart-meters
- [Q31] Stadtwerke Homburg: FAQ zu §14a EnWG (Stand 01.04.2024; 4,2 kW, 2 h/Tag bis Ende 2028, Echtzeit ab 2029). https://www.stadtwerke-homburg.de/fileadmin/dokumente/Netze/Netztechnische_Dienste/__14_aEnWG/20240403_FAQ_zu__14a_EnWG_final.pdf
- [Q32] BNetzA: Verfahren BK6-22-300 (§14a). https://www.bundesnetzagentur.de/1107472
- [Q33] Najar et al.: Improving thermal model for oil temperature estimation in power distribution transformers, Applied Thermal Engineering 119 (2017) 73–78, Tab. 1/2 (IEC 60076-7: τo = 180 min). https://www.lias-lab.fr/~eriketien/Files/Other/Improving%20thermal%20model%20for%20oil%20temperature%20estimation%20in%20power.pdf
- [Q34] ZfK: BSI veröffentlicht TR-5; zertifizierte Steuerboxen. https://www.zfk.de/digitalisierung/smart-city-energy/bsi-veroeffentlicht-tr-5 ; https://www.zfk.de/digitalisierung/smart-city-energy/drei-weitere-steuerboxen-fuer-intelligente-messsysteme-zertifiziert ; innobu CLS-Management 2026: https://www.innobu.com/de/artikel/cls-management-aemt-stadtwerke-2026.html
- [Q35] GSMA: Difference in data throughput LTE-M/NB-IoT (Latenzen). https://www.gsma.com/solutions-and-impact/technologies/internet-of-things/gsma_resources/what-is-the-difference-in-data-throughput-between-lte-m-nb-iot-and-3g-or-4g/
- [Q35b] 3GPP TR 45.820 (10-s-Latenzziel, 164 dB MCL) über iTecSpec. https://itecspec.com/3gpp/45.820/s/7a.4.1.2.2
- [Q36] Analog Devices: Mesh networking extends a PLC network (G3-PLC). https://www.analog.com/en/resources/technical-articles/mesh-networking-extends-a-plc-network-to-thousands-of-meters.html ; Renewable Energy World: Landis+Gyr Netz Burgenland: https://www.renewableenergyworld.com/power-grid/smart-grids/landis-gyr-brings-smart-metering-to-austria/
- [Q36b] Onomondo: eDRX und PSM; Telenor eDRX/PSM-Tabelle. https://onomondo.com/blog/edrx-and-psm-for-lte-low-power-iot/ ; https://talkmore.no/-/media/files/bedrift/hvordan-edrx-og-psm-konfigureres-i-telenors-nett.ashx
- [Q37] Actility: Drei Partners with Actility to Operate Austria's Public LoRaWAN Network (25.10.2023). https://www.actility.com/drei-pr/
- [Q38] Oesterreichs Energie: Rechtliches Gutachten PLC (2017). https://oesterreichsenergie.at/fileadmin/user_upload/Oesterreichs_Energie/Publikationsdatenbank/Gutachten/2017/2017.02_rechtliches_Gutachten_PLC.pdf
- [Q39] Energie-Museum: Kommunikationstechnik (Rundsteuerung, kein Rückkanal). https://www.energie-museum.de/fileadmin/Dateien/Kommunikationstechnik.pdf
- [Q40] Protostar Labs: Decabit-Protokoll (600 ms/Bit). https://www.protostarlabs.net/ripple/protocols/decabit.asp
- [Q41] BMWET: ElWG-Factsheet Spitzenkappung. https://www.bmwet.gv.at/dam/jcr:260fda60-c745-4861-bdcb-1c1223a4af58/ElWG-Factsheets_Spitzenkappung_final%20final.pdf
- [Q42] eeNews Europe: Senet/Oxit LoRaWAN-Multicast (Gas). https://www.eenewseurope.com/en/wp-json/wp/v2/posts/398986
- [Q43] winfuture: 450-MHz-Band an Energieversorger. https://winfuture.de/news,119309.html
- [Q44] pv magazine: 450connect und Inexogy (05.08.2025). https://www.pv-magazine.de/2025/08/05/450connect-und-inexogy-starten-mit-anbindung-intelligenter-messsysteme-ueber-450-megahertz-frequenz/
- [Q45] pressetext: Sichere Mobilfunkkommunikation für kritische Infrastruktur (ArgoNET). https://www.pressetext.com/news/sichere-mobilfunkkommunikation-fuer-kritische-infrastruktur.html
- [Q46] Westermo: Energie AG – CDMA to LTE 450 MHz upgrade. https://westermo.com/about-us/success-stories/energie-cdma-to-lte-450-mhz-upgrade
- [Q47] TU Berlin (Trinks): Strombelastbarkeit von Erdkabeln. https://depositonce.tu-berlin.de/items/2d174526-480a-48ea-8a49-efada139a550
- [Q48] Elia: Activation for balancing (FCR 30 s, aFRR 5 min). https://www.elia.be/electricity-market-and-system/system-services/keeping-the-balance/activation-for-balancing

**Methodische Hinweise:**
- Mehrere Primärdokumente waren nicht abrufbar, entweder hinter einer Paywall oder mit
  HTTP 403/404: IEEE 2030.5, SA HB 218, TS005-PDF, RP002, IEC 60076-7, IEC 61850-7-420,
  EN 50491-12-2, BNetzA-Beschlusstext BK6-22-300, IMA-VO.
- Aussagen dazu stützen sich auf Sekundärquellen und sind entsprechend markiert.
- Die Sendezeiten nach Semtech-Formel sind eigene Rechnungen.
