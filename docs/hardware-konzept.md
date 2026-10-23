# Hardware-Konzept: modulare Steuerbox

Stand: 23.10.2026. **[E]** = vom Team festgelegt, **[V]** = Vorschlag,
**[O]** = offen. Produktnamen und Kernaussagen am 23.10.2026 gegen Hersteller-
und Händlerseiten geprüft; Preise und Lieferzeiten ändern sich, vor einer
Bestellung erneut prüfen.

## 1. Festgelegt [E]

- Hochmodular und standardisiert, damit die Kosten niedrig bleiben
- Ein zentrales Kernmodul trägt die Haupt-Firmware
- **Jedes Modul hat einen Mikrocontroller, auch das Kernmodul.** Das Kernmodul
  nutzt einen leistungsstärkeren Mikrocontroller (kein Linux-Prozessor); Auswahl
  in § 4.4
- **EMS-Optimierung läuft lokal** im optionalen Linux-Modul `APP`, nicht im
  Kernmodul (§ 2.1)
- Kommunikationsslots 1–4 im gleichen Format; ab Werk ein LoRa-Modul, optional
  Ethernet, Mobilfunk, …
- **Ein Ethernet-Modul `ETH`** mit einem Anschluss im Heim-LAN für Backend,
  Home Assistant und IP-Geräte (§ 2.1)
- Dasselbe Prinzip für alle übrigen Module: Netzteil, M-Bus, Modbus/RS485, Ethernet, …
- Jedes Modul hat signierte Firmware und spricht nur authentifiziert mit dem Kernmodul
- Module lassen sich nicht ohne Weiteres tauschen (Vorbild: Steuergeräte im Automobil)
- **Offenes Ökosystem:** Jeder Hersteller darf Module bauen. **Signieren** dürfen
  Module und Firmware aber nur **Trusted Authorities**. Ein Hersteller kann sein
  Modul also nicht selbst in Verkehr bringen, sondern erst nach Prüfung und
  Signatur durch eine solche Stelle.
- **Zwei Phasen:** Der Prototyp wird aus Off-the-shelf-Komponenten aufgebaut
  (§ 4.1). Eigene Hardware (eigene Platinen in Tragschienengehäusen) folgt erst
  für die Serie (§ 4.2).

## 2. Aufbau [V]

```
 Tragschiene (Zählerplatz, plombierbare Abdeckung)
 ┌──────┬────────┬──────┬──────┬──────┬──────┬───────┬───────┬───────┐
 │Netz- │ Kern-  │Slot 1│Slot 2│Slot 3│Slot 4│ MTR   │FLD-IO │ frei  │
 │teil  │ modul  │ LoRa │(LTE) │(ETH) │(APP) │ Zähler│Basis- │(MEAS, │
 │      │        │      │      │      │      │       │IO     │ …)    │
 └──┬───┴───┬────┴──┬───┴──┬───┴──┬───┴──┬───┴───┬───┴───┬───┴───┬───┘
 ═══╧═══════╧═══════╧══════╧══════╧══════╧═══════╧═══════╧═══════╧═══
     Tragschienen-Busverbinder: 24 V + CAN FD Bus K und Bus F (authentifiziert)
```

- **Bauform:** Jedes Modul ist ein schmales Tragschienengehäuse (17,5–22,5 mm).
  Gehäuse und Tragschienen-Busverbinder gibt es fertig zu kaufen (z. B. Phoenix
  Contact ME-/ICS-Gehäuse mit TBUS). Nur die Platine ist eigenentwickelt.
- **Alle Slots sind mechanisch und elektrisch gleich.** Was in einem Slot steckt,
  erkennt das Kernmodul über das Zertifikat des Moduls, nicht über die Position.
- **Modulbus: CAN FD.** Er ist robust, multidrop-fähig, billig und das direkte
  Vorbild aus dem Automobil. Die Befehle sind klein (unter 200 Byte), dafür
  reichen 2–5 Mbit/s. Später möglich: 10BASE-T1S (Ethernet mit mehreren
  Teilnehmern an einer Leitung, ebenfalls aus dem Automobil).
- **Abschaltbare Slots:** Das Kernmodul kann jeden Slot einzeln stromlos schalten
  und so ein nicht freigegebenes Modul isolieren.

### 2.1 Architektur der Module [V]

```
      Netzbetreiber / Stromanbieter (Backend)      Heim-LAN: Router, Home Assistant,
        │ LoRaWAN       │ LTE-M                   │ Wallbox, Wechselrichter, Wärmepumpe
  ┌─────▼─────┐   ┌─────▼─────┐             ┌─────▼──────────┐   ┌──────────────┐
  │ COM-LORA  │   │ COM-LTE   │             │ ETH  1 × RJ45  │   │ APP (Linux)  │
  │ MCU       │   │ MCU       │             │ MCU, Kanäle:   │   │ i.MX 93      │
  └─────┬─────┘   └─────┬─────┘             │ Backend · HA · │   │ EMS-Optim.   │
        │               │                   │ Geräte (IP)    │   └──────┬───────┘
        │               │                   └─────┬──────────┘          │
 Bus K ═╧═══════════════╧═════════════════════════╧═════════════════════╧════════╗
 (CAN FD, SecOC)    Kommunikation + EMS: Befehle, Vorschläge, Transport          ║
                                                                                 ║
                        ┌─────────────────────────────────────┐                  ║
   230 V ──► PSU ─24 V──┤ KRN   STM32H573 + Secure Element    ├══════════════════╝
             (Puffer)   │ Signatur prüfen · Grenzen · Vorrang │
                        │ Fail-safe · Verbauliste · Slots aus │
                        │ einziger Erzeuger von Sollwerten    │
                        └──────────────────┬──────────────────┘
                                           ║
 Bus F ═╤═══════════════╤══════════════════╩═╤═══════════════════╤══════
 (CAN FD, SecOC)    Feld: erhält nur geprüfte Sollwerte vom Kern
  ┌─────┴─────┐   ┌─────┴──────────┐   ┌─────┴─────┐       ┌─────┴─────┐
  │ MTR       │   │ FLD-IO         │   │ MEAS      │       │ frei für  │
  │ MCU       │   │ MCU            │   │ MCU       │       │ weitere   │
  └─────┬─────┘   │ RS485 · 4 Rel. │   └─────┬─────┘       │ Module    │
        │         │ 4 DI · 2×0–10 V│         │             └───────────┘
        │         └─────┬──────────┘         │
   Smart Meter    Wechselrichter RS485,   Stromwandler,
   (M-Bus / IR)   Altgerät, SG-Ready,     Netzmessung U/f
                  Heizstab, Rundsteuer-
                  empfänger, Notstrom
```

- **Zwei getrennte Busse:** Bus K (Kommunikation und EMS) und Bus F (Feld). Nur
  der Kern verbindet beide.
- **Nur der Kern erzeugt Sollwerte.** Module an Bus K liefern Befehle oder
  Vorschläge an den Kern. `ETH` transportiert die vom Kern erzeugten Sollwerte an
  IP-Geräte (Wallbox, Wechselrichter mit Modbus TCP, Wärmepumpe), erzeugt aber
  selbst keine.
- **Ein Ethernet-Anschluss im Heim-LAN** für Backend, Home Assistant und
  IP-Geräte. Ein getrenntes Feld-LAN brächte keine Sicherheit, solange die
  Geräte ohnehin im Heim-LAN hängen; Modbus TCP hat keine Authentifizierung.
- **Module nach elektrischer Schnittstelle, nicht nach Gerät:** Ob an `FLD-IO`
  ein alter Wechselrichter, eine Wärmepumpe oder ein Heizstab hängt, legt ein
  signiertes Geräteprofil fest, keine eigene Hardware.
- **Kern = MCU, EMS = Linux-Modul `APP`:** Die Optimierung läuft lokal auf
  Linux, schickt dem Kern aber nur Vorschläge aus der festen Parameterliste. Fällt
  `APP` aus oder wird angegriffen, läuft die Box sicher weiter.
- Vorbild Automobil: sicherheitskritisches Steuergerät getrennt vom
  Infotainment-Rechner.

## 3. Moduldefinitionen [V]

### 3.1 Gemeinsamer Modulvertrag

Jedes Modul erfüllt denselben Vertrag, egal von welchem Hersteller. Das macht
die Slots austauschbar und die Prüfung durch die Trusted Authority wiederholbar.

| Punkt | Festlegung |
|---|---|
| Gehäuse | Tragschienengehäuse 35 mm, Breite 17,5 mm (1 TE) oder 22,5 mm, plombierbar |
| Busanschluss | Tragschienen-Busverbinder mit 24 V DC und CAN FD (2–5 Mbit/s) |
| Modul-MCU | MCU mit FDCAN, Secure Boot, gesperrtem Debug-Port und eigenem, nicht exportierbarem Schlüssel; das Kernmodul nutzt eine leistungsstärkere MCU (§ 4.4) |
| Identität | Modulzertifikat mit Hersteller, Modultyp, Hardware-Revision, Seriennummer; signiert von einer Trusted Authority |
| Firmware | zwei Signaturen: Hersteller **und** Betreiber-Freigabe; Update nur über das Kernmodul |
| Buskommunikation | jede Nachricht mit MAC und Zähler (SecOC-Prinzip), Sitzungsschlüssel je Modul |
| Nachrichtenklassen | `CMD` (Sollwert vom Kern), `CFG` (Parameter), `TEL` (Messwerte), `EVT` (Alarm, Manipulation), `HB` (Lebenszeichen) |
| Fähigkeiten | Das Modul meldet Fähigkeiten statt eines festen Typs, z. B. „Sollwert Wirkleistung“, „Schaltausgang“, „Analogausgang“, „Digitaleingang“, „Messwert“. So nutzt der Kern ein neues Modul mit einem signierten Profil, ohne Kern-Update |
| Galvanische Trennung | jede Feldschnittstelle (Zähler, Wechselrichter, LAN) ist vom Modulbus getrennt |
| Fail-safe | bleibt `HB` vom Kern länger als die Frist aus, fällt das Modul in seinen definierten Ruhezustand (je Modul unten) |
| Anzeige | eine Status-LED (Betrieb, nicht freigegeben, Fehler) |
| Umgebung | −25 … +60 °C, Zählerplatz im Innenbereich |
| Leistungsklasse | A: < 0,5 W · B: < 2 W · C: < 5 W Mittelwert (Spitzen puffert das Modul selbst) |

### 3.2 Modulübersicht

| Kürzel | Modul | Pflicht | Slot | Breite | Leistung *[Schätzung]* |
|---|---|---|---|---|---|
| `PSU` | Netzteil | ja | fest, ganz links | 17,5–35 mm | liefert 15–30 W |
| `KRN` | Kernmodul | ja | fest | 35–45 mm | B (ca. 1 W) |
| `COM-LORA` | LoRaWAN Class C | ja (Standard) | Kommunikationsslot 1–4 | 17,5 mm | A |
| `COM-LTE` | LTE-M / NB-IoT | optional | Kommunikationsslot 1–4 | 22,5 mm | B (Spitze 2 A gepuffert) |
| `ETH` | Ethernet im Heim-LAN: Backend, Home Assistant, IP-Geräte | optional | Kommunikationsslot 1–4 | 17,5 mm | A |
| `APP` | Linux-Modul für lokale EMS-Optimierung | optional | Bus K | 35–45 mm | C (2–4 W) |
| `MTR` | Zähler-Kundenschnittstelle | ja | Feldslot | 17,5 mm | A |
| `FLD-IO` | Basis-IO: 1 × RS485, 4 Relais, 4 Digitaleingänge, 2 × 0–10 V | ja (Standard); ein zweites bei Bedarf | Feldslot | 22,5 mm | B |
| `MEAS` | eigene, signierte Messung inkl. Netzmessung U/f | optional, für Förderung empfohlen | Feldslot | 22,5–35 mm | A |
| *weitere* | jedes Modul nach Modulvertrag, z. B. Funk-M-Bus, KNX, Batterie-CAN | optional | Feldslot | – | – |

Grundausstattung: `PSU` + `KRN` + `COM-LORA` + `MTR` + `FLD-IO`. Leistung
gesamt im Mittel etwa 5 W, mit allen Modulen etwa 8–10 W (mit `APP` bis 14 W).
Ein 15-W-Netzteil reicht für die Grundausstattung; mit `COM-LTE`, `APP` oder
geschalteten Relais 30 W.

**Warum ein Basis-IO statt einzelner Module** *[Schätzung]*: Jedes Modul kostet
vor seiner eigentlichen Funktion etwa 10–15 € (Gehäuse, Busverbinder, MCU,
Secure Element, isolierte Versorgung, Test), jeder Modultyp zusätzlich 20–50 k€
für Entwicklung, EMV und Prüfung durch die Trusted Authority. `FLD-IO` kostet
etwa 25–35 € Bauteile, drei Einzelmodule (RS485, Relais, Eingänge) etwa
45–60 € und mehr Platz im Zählerkasten. Den Kern spart man trotzdem nicht ein:
Feldkabel und Relaiskontakte bleiben vom Sicherheitskern getrennt.

### 3.3 Die Module im Einzelnen

#### `PSU` – Netzteil

- **Aufgabe:** 230 V AC → 24 V DC für den Busverbinder.
- **Feld:** 230-V-Anschluss (L, N), abgesichert im Zählerplatz.
- **Bus:** keine eigene Logik; optional ein Statuskontakt „24 V ok“.
- **Besonderheit:** Pufferkondensator oder Superkondensator, damit das Kernmodul
  bei Netzausfall noch 1–2 s hat, um den Zustand zu sichern und ein `EVT` zu senden.
- **Ruhezustand:** entfällt.

#### `KRN` – Kernmodul

- **Aufgabe:** Haupt-Firmware: Befehle prüfen (Signatur, Gültigkeit, Grenzen),
  Vorrangregeln aus [anforderungen.md](anforderungen.md) § 3 anwenden,
  Sollwerte an `FLD-IO` bzw. über `ETH` an IP-Geräte geben, Reaktion über `MTR`/`MEAS` messen und melden.
- **Hält:** Secure Element mit Box-Schlüssel, Netzbetreiber-Zertifikate,
  signierte Verbauliste, Ereignisprotokoll, Echtzeituhr.
- **Bus:** Busmaster; schaltet jeden Slot einzeln stromlos.
- **Feld:** Servicezugang nur für den Installateur (USB-C oder NFC mit
  Rollenzertifikat), sonst keine Außenschnittstelle.
- **Gehäusekontakt:** meldet das Öffnen der plombierten Abdeckung als `EVT`.
- **Ruhezustand:** ohne gültigen Befehl Eigenbetrieb; Sollwerte laufen mit ihrer
  Ablaufzeit aus.

#### `COM-LORA` – LoRaWAN (Standard)

- **Aufgabe:** Empfängt signierte Befehle des Netzbetreibers (auch Multicast an
  Gruppen) und sendet kurze Rückmeldungen.
- **Feld:** Antenne (SMA-Buchse, Außenantenne wegen Zählerkasten aus Metall).
- **Funk:** EU868, Class C für sofortigen Empfang.
- **Regel:** Das Modul reicht Befehle nur durch und prüft sie nicht; die Prüfung
  macht ausschließlich das Kernmodul.
- **Ruhezustand:** Funk aus, `EVT` an den Kern.

#### `COM-LTE` – LTE-M / NB-IoT (optional)

- **Aufgabe:** Rückkanal für größere Daten (Testabruf-Auswertung, Firmware) und
  Ausweichweg für Befehle.
- **Feld:** Antenne, Nano-SIM oder eSIM.
- **Besonderheit:** puffert Sendespitzen bis 2 A lokal, damit der Bus stabil bleibt.
- **Ruhezustand:** Modem aus.

#### `ETH` – Ethernet im Heim-LAN (optional)

- **Aufgabe:** ein Anschluss für drei getrennte Kanäle, jeder mit eigenem
  Sitzungsschlüssel zum Kern:
  1. **Backend:** wie `COM-LTE`, über den Internetanschluss des Kunden; nur
     ausgehende, gegenseitig authentifizierte TLS-Verbindung. TLS endet im Kern.
  2. **Home Assistant:** Telemetrie nach außen (SoC, Leistung, Status, aktiver
     Abruf, Überschreibungen) über Modbus TCP und MQTT; nach innen nur die feste
     Parameterliste mit Wertebereich. Der Kern prüft und begrenzt noch einmal.
     Preise kommen nicht über diesen Kanal (siehe [ems-konzept.md](ems-konzept.md)).
  3. **IP-Geräte:** OCPP 2.x zur Wallbox (bei V2G auch Rückspeisen; ISO 15118
     läuft zwischen Auto und Wallbox), SunSpec Modbus TCP zum Wechselrichter,
     EEBus zur Wärmepumpe. Die Sollwerte erzeugt der Kern; `ETH` transportiert sie.
- **Feld:** RJ45, galvanisch getrennt.
- **Regel:** Kein Kanal leitet in einen anderen weiter; das Modul ist kein Router.
- **Ruhezustand:** Kanäle 1 und 3 aus, Kanal 2 nur noch lesend.
- **Folge der Zusammenlegung:** Fällt `ETH` aus, sind Backend über LAN, Home
  Assistant und IP-Geräte gleichzeitig weg. Abrufe kommen weiter über LoRa;
  `FLD-IO` und der Fail-safe laufen unabhängig weiter. Für Anlagen mit eigenem
  Feldnetz (Gewerbe, Wechselrichter mit zwei LAN-Ports) ist ein zweites `ETH`
  möglich.

#### `APP` – lokale EMS-Optimierung (optional, Linux)

- **Aufgabe:** Plant Laden und Entladen nach Tarif, PV-Prognose und Verbrauch;
  bietet die lokale Oberfläche und die Logik für Home Assistant (Anbindung über `ETH`).
- **Hardware:** Linux-Prozessor, z. B. NXP i.MX 93 (EdgeLock Secure Enclave)
  oder STM32MP25, mit eigener MCU-Seite bzw. eigenem Bus-Controller für den
  Modulvertrag.
- **Bus:** nur Bus K. Schickt dem Kern Vorschläge aus der festen Parameterliste
  (`CFG`); der Kern prüft, begrenzt und kann ablehnen. Liest Telemetrie, die der
  Kern freigibt.
- **Regel:** Netzbetreiber-Abrufe und Fail-safe haben immer Vorrang
  (Vorrangregeln in [anforderungen.md](anforderungen.md) § 3).
- **Ruhezustand:** keine Vorschläge; der Kern fällt auf Eigenverbrauchsoptimierung
  ohne Prognose zurück.

#### `MTR` – Zähler-Kundenschnittstelle

- **Aufgabe:** Liest den Smart Meter des Netzbetreibers (Leistung, Energie je
  Richtung), entschlüsselt mit dem Kundenschlüssel und meldet `TEL` an den Kern.
- **Varianten**, weil die österreichischen Netzbetreiber verschiedene
  Schnittstellen haben:
  - `MTR-MBUS`: kabelgebundenes M-Bus über RJ12, 2.400 Baud, DLMS/COSEM (z. B.
    Netz NÖ, Salzburg Netz, E-Netze Steiermark)
  - `MTR-IR`: optischer Lesekopf nach IEC 62056-21 (z. B. Wiener Netze)
  - `MTR-P1`: DSMR P1 (Sagemcom-Zähler einzelner Netzbetreiber)
- **Regel:** Werte dieser Schnittstelle gelten als nicht manipulationssicher;
  für den Nachweis der Reaktion zählt `MEAS`, falls vorhanden.
- **Ruhezustand:** passiv, kein Senden.

#### `FLD-IO` – Basis-IO (Standard)

- **Aufgabe:** alle Kleinsignal-Anschlüsse im Feld in einem Modul. Welches Gerät
  an welchem Anschluss hängt, legt ein signiertes Geräteprofil fest.
- **Feld:**

  | Anschluss | Typische Nutzung |
  |---|---|
  | 1 × RS485, galvanisch getrennt, Abschluss schaltbar | Wechselrichter oder Speicher mit SunSpec Modbus RTU; Wallbox oder Wärmepumpe mit Modbus RTU |
  | 4 Relais, potentialfrei | 0/30/60/100 % für ältere Wechselrichter mit Rundsteuereingang; SG-Ready der Wärmepumpe (2 Kontakte); Heizstab oder Verbraucher ein/aus |
  | 4 Digitaleingänge, potentialfrei | vorhandenen Rundsteuerempfänger mitlesen; Notabschaltung; Status der Notstrom-Umschaltung (im Inselbetrieb nichts einspeisen) |
  | 2 × 0–10 V | Leistungssteller für den Heizstab (PV-Überschuss ins Warmwasser); Sollwert für Geräte mit Analogeingang |

- **Protokoll RS485:** SunSpec Modbus als Standard; herstellerspezifische Profile
  als signierte Profildateien, nicht als freier Code.
- **Zweites `FLD-IO`:** nur wenn die Relais nicht reichen, z. B. alter
  Wechselrichter (4 Relais) **und** Wärmepumpe mit SG-Ready (2 Relais).
- **Ruhezustand:** keine Sollwerte mehr über RS485 (der Wechselrichter fällt nach
  seinem eigenen Timeout in den Eigenbetrieb); alle Relais stromlos = 100 %,
  keine Einschränkung, SG-Ready „Normalbetrieb“; 0–10 V auf 0 V. Ein Ausfall der
  Box regelt also nie dauerhaft ab.

#### `MEAS` – eigene, signierte Messung (optional)

- **Aufgabe:** Misst Wirkleistung am Wechselrichter oder Speicher selbst und
  signiert jeden Messwert im Modul. Damit ist die Reaktion auf einen Abruf auch
  dann nachweisbar, wenn die Zählerdaten fehlen oder manipuliert sind.
- **Feld:** Spannungsabgriff und Stromwandler (1- oder 3-phasig).
- **Netzmessung:** Der Mess-IC misst Spannung und Frequenz ohnehin mit. Damit
  kann die Box später selbst nach Spannung bzw. Frequenz regeln (Q(U), P(f)),
  ohne zusätzliches Modul.
- **Eigenes Modul, weil:** 230-V-Messung braucht eigene Isolationsabstände und
  die Messwerte werden im Modul signiert.
- **Ruhezustand:** misst weiter und puffert Werte, bis der Kern wieder da ist.

### 3.4 Offene Punkte zu den Modulen [O]

- Sind `KRN` und `PSU` getrennt oder ein Gehäuse? Getrennt ist modularer,
  gemeinsam ist billiger.
- Reichen getrennte Kanäle in `ETH`, oder braucht der Home-Assistant-Kanal eine
  zusätzliche Trennung (z. B. eigener Netzwerkcontroller)?
- Reicht der Zuschnitt von `FLD-IO` (1 × RS485, 4 Relais, 4 Eingänge,
  2 × 0–10 V), oder braucht es einen zweiten RS485?
- Wird `MEAS` für die volle Förderung Pflicht?
- Woher bekommt `APP` Wetter- bzw. PV-Prognosen: signiert über das Backend und
  den Kern, oder über einen eigenen Internetzugang über `ETH`?
- Reicht für `MTR` eine Lösung mit wechselbarem Kopf (RJ12 oder IR) in einem
  Modul statt drei Varianten?

## 4. Komponenten

### 4.1 Prototyp aus Off-the-shelf-Komponenten [E: Phase, V: Auswahl]

Ziel: Funktion und Sicherheitskonzept zeigen (Befehl per LoRa, Prüfung,
Ansteuerung des Wechselrichters, signierte Module am CAN-FD-Bus), ohne eine
Platine zu entwickeln. Nicht Ziel: Zielpreis, Zertifizierung, Bauform der Serie.

| Funktion | Prototyp-Komponente | Hinweis |
|---|---|---|
| Kernmodul | **STM32H573I-DK** (Discovery Kit mit der Serien-MCU, [DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32H573I-DK/21382558)) oder günstiger **NUCLEO-H563ZI** (gleiche Familie ohne die Krypto-Extras der H573) | dieselbe MCU wie in der Serie (§ 4.4), damit die Kern-Firmware direkt weiterverwendet wird |
| Modulbus CAN FD | CAN-FD-Transceiver-Board mit TJA1443 oder TCAN1042G an den FDCAN der MCU | |
| Prüfplatz zum Mitlesen | PEAK PCAN-USB FD (IPEH-004022, ca. 230–350 $, SocketCAN) am Laptop | liest den Modulbus mit, auch zum Einspielen manipulierter Nachrichten |
| *nicht mehr Kern* | Revolution Pi Connect 5 (RS485 + CAN FD, ca. 835 €) | Linux-Rechner; passt nicht zur Entscheidung „Kern = MCU“. Höchstens als Backend- oder Gateway-Simulator. Der Connect 4 scheidet aus: Con CAN ist laut Hersteller nicht kompatibel ([Shop](https://revolutionpi.com/shop/en/canbus-module)) |
| Secure Element | Eval-Board NXP SE050 (I²C, per USB-Brücke) | ersetzt das Secure Element im Kern; OPTIGA Trust M hat derzeit ca. 26 Wochen Lieferzeit |
| LoRaWAN Class C | RAK3172 Evaluation Board (RAK3172-E = RAK3372 auf RAK19007) oder Breakout RAK3272S ([Doku](https://docs.rakwireless.com/product-categories/wisduo/rak3172-evaluation-board/overview/)) | gleiches Funkmodul wie für die Serie; [RAK7431](https://docs.rakwireless.com/product-categories/wisnode/rak7431/overview/) als fertige Tragschienen-Bridge nur für Funktionstests, weil dort keine eigene Prüflogik läuft |
| LTE-M (optional) | Quectel-BG95-M3-Evalboard oder USB-Stick | |
| Zähler-Kundenschnittstelle (`MTR`) | **Smart-Meter-Adapter (SMA) von Oesterreichs Energie**: liest IR, DSMR, MEP (UART-Variante) bzw. M-Bus, Funk-M-Bus (M-Bus-Variante), gibt Modbus TCP/MQTT/JSON über WLAN aus ([Datenblatt](https://oesterreichsenergie.at/fileadmin/user_upload/Datenblatt_Smart_Meter_Adapter_V7_20220808__2_.pdf)) | Variante passend zum Netzbetreiber wählen (§ 3.3, `MTR`). Ohne WLAN: M-Bus-Pegelwandler ADFweb HD67022 (RS485) für RJ12-Zähler bzw. IR-Lesekopf nach IEC 62056-21 für Wiener Netze |
| `FLD-IO` | Nucleo-G0B1RE mit isoliertem RS485-Board (z. B. MikroE RS485 Isolator Click), 4-Kanal-Relaisboard, Digitaleingängen und 0–10-V-Ausgang | *Produktnamen ungeprüft* |
| `ETH` | Nucleo mit Ethernet (z. B. NUCLEO-H563ZI) | Wallbox-Test über einen OCPP-Simulator am Laptop |
| Eigene Messung (`MEAS`) | Eastron **SDM120-Modbus MID** (1-phasig) oder SDM630-Modbus MID V3 (3-phasig) | ersetzt den Mess-IC; MID nur mit der Bestellvariante „MID“ |
| Netzteil | Mean Well HDR-15-24 (24 V / 0,63 A, 17,5 mm) | für die Grundausstattung; mit LTE und Relais 30 W wählen |
| **Signierte Module (Emulation)** | 2–3 × STM32 Nucleo-G0B1RE (FDCAN) mit CAN-FD-Transceiver-Board | zeigt Modulzertifikat, SecOC-MAC, Verbauliste und das Isolieren eines Slots (§ 5) |

Die Prototyp-Module sind Nucleo-Boards mit aufgesteckten Click-Boards bzw.
Evalboards. Jedes Prototyp-Modul hat damit wie in der Serie eine eigene MCU am
CAN-FD-Bus.

Grobe Kosten des Prototyps *[Schätzung]*: 600–900 € für einen Aufbau
(Kern-Board 30–100 €, je Modul 30–80 €, SMA, Zähler und PCAN-Adapter je 100–350 €).

**Was der Prototyp beweist:** Ablauf von Befehl und Rückmeldung, Prüflogik und
Grenzen, Fail-safe, Modulfreigabe nach § 5. **Was nicht:** Kosten, EMV,
Zertifizierung, Bauform der Serie.

### 4.2 Eigene Hardware (Serie) [V]

Nach dem Prototyp: eigene Platinen in fertigen Tragschienengehäusen (§ 2) nach dem Modulvertrag (§ 3.1). Die
Firmware und das Sicherheitskonzept aus dem Prototyp werden übernommen, die
Kaufmodule durch die folgenden Bauteile ersetzt.

#### Kernmodul

| Funktion | Kandidaten |
|---|---|
| Mikrocontroller | **STM32H573** (Empfehlung, § 4.4); Alternativen NXP MCX N947, Infineon XMC7200 |
| Secure Element / TPM | NXP SE050 (SE051 mit im Feld aktualisierbaren Applets), Microchip ATECC608C (Nachfolger des 608B), Infineon OPTIGA Trust M (lange Lieferzeit), TPM 2.0 Infineon SLB 9672 |
| CAN-FD-Transceiver | NXP TJA1443 (5 Mbit/s), TI TCAN1042**G**-Varianten (5 Mbit/s; ohne G nur 2 Mbit/s) oder TCAN1044A (8 Mbit/s) |
| Echtzeituhr, Speicher | RTC der MCU mit Pufferkondensator; externer QSPI-NOR-Flash 16–64 MB für Firmware A/B, Modul-Firmware und Ereignisprotokoll |

#### Kommunikationsmodule (Slots 1–4)

| Modul | Kandidaten |
|---|---|
| **LoRaWAN (Standard)** | RAK3172 (STM32WLE5CC, Class A/B/C); Semtech LR1121 bzw. Murata Type 2GT, falls Mehrband (Sub-GHz, 2,4 GHz, Satellit) nötig. Murata Type 1SJ ist abgekündigt |
| LTE-M / NB-IoT | Quectel BG95-M3/BG77, u-blox SARA-R5 (nur -01B, -00B ist abgekündigt) / LEXI-R4, Nordic nRF9151 |
| Ethernet (`ETH`) | MCU mit integriertem MAC + PHY Microchip LAN8742A; WIZnet W5500 (Lieferzeit bis 20 Wochen) |
| WLAN | ESP32-C6-Modul (Wi-Fi 6 nur 2,4 GHz, BLE, Thread/Zigbee) |
| Optional | 450-MHz-Funk, G3-PLC (z. B. ST8500) |

#### Weitere Module

| Modul | Kandidaten |
|---|---|
| Netzteil 230 V → 24 V | Mean Well HDR-15-24 bzw. HDR-30-24 (fertiges Tragschienennetzteil) oder Recom RAC05-K (5-W-Printmodul) auf eigener Platine |
| Zähler-Kundenschnittstelle (`MTR`) | M-Bus-Master-Pegelwandler (RJ12); IR-Lesekopf nach IEC 62056-21; Wireless M-Bus über Würth/Amber oder Radiocrafts *(ungeprüft)* |
| `FLD-IO` RS485 | isolierter Transceiver ADM2561E/ADM2563E (Empfehlung von ADI statt ADM2587E) oder THVD1450 (nicht isoliert) mit Isolator |
| `FLD-IO` Relais, Eingänge, 0–10 V | 4 Relais, 4 Optokoppler-Eingänge, 2 × 0–10 V über DAC bzw. gefilterte PWM mit Ausgangsstufe *(Bauteile noch nicht ausgewählt)* |
| Messung (eigene, signierte) | Energie-Mess-IC, z. B. ADE9153A (Empfehlung von ADI statt ADE7953) oder ATM90E26, beide 1-phasig, mit Stromwandler. Dient zur Verifikation, weil die Daten der Kundenschnittstelle manipulierbar sind (siehe [07-synthese.md](research/07-synthese.md)) |

**Je Modul gleich:** eine kleine MCU mit FDCAN, Secure Boot und eigenem Schlüssel
(z. B. STM32G0B1 mit 2 × FDCAN oder STM32C092 mit 1 × FDCAN, jeweils mit Zusatz-Secure-Element; andere STM32C0 haben kein FDCAN). Mehrkosten pro Modul
grob 2–5 € [Schätzung].

### 4.3 Hackathon-Demo

Für die Hackathon-Demo reicht eine Simulation der Box; der Prototyp nach § 4.1
folgt danach.

### 4.4 Evaluation Kern-MCU [V]

#### Anforderungen an die Kern-MCU

| Anforderung | Warum | Mindestwert |
|---|---|---|
| CAN FD | Modulbus | 2 Controller: Kommunikations- und Feldslots auf getrennten Bussen, damit Home Assistant, `APP` und Funk nie auf demselben Bus wie `FLD-IO` liegen |
| Krypto in Hardware | Befehlssignatur prüfen (ECDSA P-256), SecOC-MAC (AES-CMAC), TRNG | PKA + AES + TRNG |
| Root of Trust | Secure Boot, gesperrtes Debug, Schlüsselschutz | TrustZone oder eigene Security-Einheit; zusätzlich externes Secure Element möglich |
| RAM | TLS-Endpunkt der Box (für `ETH`/`COM-LTE`), Puffer für Modul-Firmware | ≥ 512 KB |
| Flash | Firmware A/B direkt in der MCU, Rest extern | ≥ 1 MB intern |
| Zertifizierung | Nachweis für CRA und RED/EN 18031 | PSA Certified / SESIP Level 3 wünschenswert |
| Verfügbarkeit | Box hängt 15–20 Jahre im Zählerkasten | Langzeit-Liefergarantie ≥ 10 Jahre |
| Software | MCUboot, Zephyr oder FreeRTOS, mbedTLS / PSA Crypto | offizieller Support |

Ethernet in der Kern-MCU ist nicht nötig, weil `ETH` ein eigenes Modul ist.
Die TLS-Verbindung endet aber im Kern, damit Kommunikationsmodule nur Modems
sind und keinen Box-Schlüssel brauchen.

#### Kandidaten

| MCU | Kern | RAM / Flash | CAN FD | Sicherheit | Preis | Bewertung |
|---|---|---|---|---|---|---|
| **ST STM32H573** | Cortex-M33, 250 MHz | 640 KB / 2 MB | 2 *(Anzahl aus Vorwissen, im Datenblatt DS14258 nachprüfen)* | TrustZone, Krypto-Beschleuniger, unveränderliche ST-Root-of-Trust; Ziel PSA Certified L3 und SESIP3 ([ST](https://www.st.com/en/microcontrollers-microprocessors/stm32h573zi.html)) | ca. 5,50 $ bei 1.000 Stück ([DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32H573VIT6/21348909)) | **Empfehlung.** Gleicher Hersteller wie die Modul-MCUs (STM32G0B1, STM32C092): eine Toolchain, ein Secure-Boot-Konzept. Leistung reicht für Prüfung, TLS und Busmaster mit Reserve |
| NXP MCX N947 | 2 × Cortex-M33, 150 MHz | 512 KB / 2 MB | 2 | EdgeLock Secure Enclave (Core Profile), PUF, TrustZone ([NXP](https://www.nxp.com/mcxn)) | Einzelstück ca. 16 $; Board FRDM-MCXN947 ca. 26 $ | Starke Alternative, vor allem zusammen mit dem NXP SE050. PSA-Zertifizierung nicht bestätigt |
| Infineon XMC7200 | 2 × Cortex-M7, 350 MHz + Cortex-M0+ als Security-Kern | bis 1 MB / 8 MB | bis 10 | eSHE und HSM wie im Auto-Steuergerät (Schwester der TRAVEO T2G), bis 125 °C ([Datenblatt](https://www.rutronik.com/fileadmin/rutronik/Supplier/Infineon/2022/XMC7000/XMC7200_Datasheet_.pdf)) | höher, nicht ermittelt | Am nächsten am Automobil-Vorbild. Für unsere Last überdimensioniert, größeres Gehäuse, teurer |
| NXP i.MX RT1180 | Cortex-M7 800 MHz + Cortex-M33 | 1,5 MB / extern | 3 | EdgeLock Secure Enclave, TrustZone, PUF; TSN-Switch, EtherCAT ([NXP](https://www.nxp.com/assets/block-diagram/en/i.MX-RT1180.pdf)) | nicht ermittelt | Nur sinnvoll, falls der Modulbus später auf Ethernet (10BASE-T1S/TSN) wechselt. Kein interner Flash, BGA-Gehäuse |
| Renesas RA8M1 | Cortex-M85, 480 MHz | 1 MB / 2 MB | 2 | TrustZone, Renesas Secure IP; PSA nur „angestrebt“ ([Renesas](https://www.renesas.com/en/products/ra8m1)) | nicht ermittelt | Leistung deutlich über Bedarf, Zertifizierung offen |
| Microchip PIC32CZ CA90 | Cortex-M7, 300 MHz | 1 MB / bis 8 MB | ja | integriertes HSM, Secure Boot ([Microchip](https://www.microchip.com/en-us/products/microcontrollers-and-microprocessors/32-bit-mcus/pic32-32-bit-mcus/pic32cz-ca)) | nicht ermittelt | HSM nur nach NDA nutzbar; passt schlecht zum offenen Modul-Ökosystem |
| ST STM32U585 | Cortex-M33, 160 MHz | 786 KB / 2 MB | 1 | PSA Certified L3 und SESIP3 **erteilt** (2021) ([ST-Blog](https://blog.st.com/psa-and-sesip-level-3-certifications)) | nicht ermittelt | Bereits zertifiziert, aber nur ein CAN-FD-Controller: keine Bustrennung möglich |

Nicht mehr in der Auswahl: NXP i.MX 93 und STM32MP25. Beides sind
Linux-Prozessoren und widersprechen der Entscheidung „Kern = Mikrocontroller“.

#### Empfehlung

1. **Serie:** STM32H573 im LQFP-Gehäuse, dazu ein externes Secure Element
   (NXP SE050 oder Microchip ATECC608C) für den Box-Schlüssel. Das Secure
   Element hält den Schlüssel, auch wenn die MCU angegriffen wird.
2. **Prototyp:** STM32H573I-DK oder NUCLEO-H563ZI (§ 4.1).
3. **Rückfallebene:** NXP MCX N947, falls Lieferzeit oder Zertifizierung des
   STM32H573 nicht passen. Die Firmware bleibt mit Zephyr und MCUboot
   weitgehend übertragbar.

#### Offen [O]

- FDCAN-Anzahl und PKA des STM32H573 im Datenblatt bestätigen
- Ist die PSA-L3-/SESIP3-Zertifizierung des STM32H573 inzwischen erteilt? Im
  [PSA-Certified-Verzeichnis](https://www.psacertified.org/certified-products/) prüfen
- Reicht für die Modul-MCU der STM32G0B1 (ohne TrustZone, Schlüssel nur im
  externen Secure Element), oder lohnt ein Cortex-M33 auch dort?

## 5. Sicherheit am Modulbus [V], nach Vorbild Automobil

| Automobil | Unsere Box |
|---|---|
| HSM / SHE im Steuergerät | Secure Element im Kernmodul, MCU mit Secure Boot in jedem Modul |
| **SecOC** (AUTOSAR): Nachrichten-MAC + Freshness-Zähler auf CAN | Jede Bus-Nachricht trägt einen MAC und einen Zähler; Sitzungsschlüssel je Modul |
| **Komponentenschutz**: Steuergerät ist ans Fahrzeug gebunden, Tausch nur mit Online-Freigabe | Signierte **Verbauliste** im Kernmodul; ein neues Modul arbeitet erst nach Freigabe durch das Backend |
| Werkstatt mit Berechtigung | Zertifizierter Installateur mit Rollenzertifikat |
| UNECE R155/R156, ISO/SAE 21434 | CRA, RED/EN 18031, NC Cybersecurity (siehe [04-security.md](research/04-security.md)) |
| Uptane (sichere OTA-Updates) | Firmware vom Hersteller signiert **und** vom Betreiber freigegeben (zwei Signaturen) |

### Ablauf: Modul hinzufügen oder tauschen

1. Der Installateur steckt das Modul ein. Das Kernmodul hält den Slot zunächst isoliert.
2. Das Kernmodul liest das Modulzertifikat (Hersteller-PKI) und prüft die Firmware-Signatur.
3. Der Installateur meldet sich mit seinem Rollenzertifikat an. Das Kernmodul fragt
   die Freigabe beim Backend an.
4. Das Backend schickt eine signierte, neue Verbauliste. Das Kernmodul vergibt
   einen Sitzungsschlüssel und schaltet den Slot frei.
5. Ohne Freigabe bleibt der Slot stromlos und das Kernmodul meldet einen Alarm.

**Wichtig:** Die Signatur des Netzbetreibers auf jedem **Befehl** (S1–S10 aus
04) bleibt davon unabhängig. Der Modulbus schützt die Box nach innen, die
Befehlssignatur den Weg vom Netzbetreiber zur Box.

## 6. Offen [O]

- Wer liefert und montiert die Box: Netzbetreiber oder Installateur?
- Wer betreibt die PKI für Module und Verbauliste?
- Darf der Kunde selbst ein Kommunikationsmodul ergänzen (z. B. LTE), wenn das
  Backend online zustimmt?
- [V] Gestufte PKI, weil das System EU-weit einsetzbar sein soll und der Pilot in AT
  läuft: EU-weite Root → nationale/akkreditierte Trusted Authorities → Module.
  Ein in einem Land signiertes Modul gilt dann in der ganzen EU.
- Wer genau ist Trusted Authority (z. B. Regulator, akkreditierte Prüfstelle)? Wie sieht die PKI-Hierarchie aus (Root → Authority → Modul)?
  Mögliche Vorbilder [ungeprüft]: SMGW-PKI des BSI, Plug&Charge-PKI (ISO 15118)
  bei E-Autos, CSIP-AUS-PKI
- Was prüft die Authority vor der Signatur (Konformitätstest, Security-Audit,
  Firmware-Review), und wie werden Signaturen widerrufen?
- Rolle **Preisstelle** in der PKI: Der tägliche Preisvektor (T4, siehe
  [ems-konzept.md](ems-konzept.md)) wird von einer gemeinsamen Stelle für alle
  Lieferanten signiert. Offen, wer das ist (EPEX, E-Control oder die Trusted
  Authority der Box-PKI). [V] Eigene Rolle mit eigenem Zwischenzertifikat unter der
  Root, getrennt von Modul-Signatur und VNB-Befehlsschlüssel: Ein kompromittierter
  Preisschlüssel darf weder Steuerbefehle noch Module signieren können.
- Zielpreis der Box in Grundausstattung (Netzteil, Kern, LoRa, M-Bus, Modbus)
