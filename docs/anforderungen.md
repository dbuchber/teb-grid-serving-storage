# Anforderungen: Grid-Serving Storage

Stand: 23.10.2026. **[E]** = vom Team festgelegt, **[V]** = Vorschlag,
**[O]** = offen bzw. beim Kickoff zu klären.

## 1. Pflichtergebnis Challenge (Smart Grids Austria)

Quelle: [challenge-grid-serving-storage.txt](challenge/challenge-grid-serving-storage.txt)

- [E] Grobes **Interoperabilitätsprofil** „Grid-Serving Storage“ nach der
  **IES-Methode** (Integrating the Energy System)
- [E] Beschreibt Prozesse und Schnittstellen zur einfachen Integration von Geräten
  und Systemen; konkret und wiederverwendbar
- [E] Keine vollständige Profildefinition, keine technischen Details
- [E] Ausgangslage: Der Anlagenbetreiber bestimmt den Speicherbetrieb. Der
  Netzbetreiber darf ihn nur in Ausnahmesituationen und zeitlich begrenzt für viele
  Speicher eines Netzsegments beeinflussen. Ziel ist, Abregelung von Erzeugern und
  Verbrauchern möglichst zu vermeiden.
- [O] Gibt es eine IES-Vorlage bzw. Gliederung für das Profil?
- [O] Bewertungskriterien und Pitchformat dieser Challenge

## 2. Pflichtangaben TEB-Abgabe

Quelle: [submission-template.txt](challenge/submission-template.txt)

- [E] **Deadline So 25.10.2026, 11:30**, Pitches ab 12:00
- [E] Projekttitel, Pitch in einer Zeile, Team, Kontakt, Track
- [E] Texte: Problem, Lösung, **Einsatz von KI** (was echt, was gemockt),
  **Security & Resilienz**, Daten, Tech-Stack
- [E] Links: **Code-Repo**, **Demo** (Live-URL oder Video ≤ 5 min), **README**
  (lokaler Start, Architektur, was funktioniert bzw. gemockt ist); optional
  Pitch-Deck und weitere Links (dort das IES-Profil)
- [E] Daten nur synthetisch, öffentlich oder vom Partner; **nichts gegen
  Live-Infrastruktur**, das Venue-Netz oder fremde Systeme testen
- [E] Code entsteht im Hacking-Fenster (ab Fr 23.10.); Bibliotheken und vorhandene
  Tools ausgenommen
- [O] Gilt infra-kg als „vorhandenes Tool“? Beim Kickoff klären.

## 3. Lösungsidee

- [E] Netzbetreiber und Stromanbieter arbeiten zusammen
- [E] Steuerung in **beide Richtungen**: abregeln bzw. laden bei Überschuss,
  einspeisen bzw. entladen bei Last
- [E] Kommunikationsmodul am Wechselrichter bzw. Speicher; Smart Meter misst die
  tatsächliche Reaktion
- [E] **Regelmäßige Testabrufe** ermitteln je Gerät bzw. Typ Reaktionszeit und
  Zuverlässigkeit
- [E] Security: Schlüssel am Gerät; Befehle signiert
- [E] Position: **standardisierte Steuerschnittstelle als Pflicht** für Wechselrichter und Speicher
- [E] Geltungsbereich: System **EU-weit einsetzbar**; **Pilotprojekt in Österreich**
- [V] Vertrauensstruktur entsprechend gestuft: EU-weite Root (gemeinsame
  Spezifikation und Wurzelzertifikat), darunter nationale bzw. akkreditierte
  Trusted Authorities, die Module signieren. Im Pilot: eine österreichische
  Authority (z. B. akkreditierte Prüfstelle, Rolle der E-Control zu klären)
- [E] **Hardware beim Endkunden: hochmodulare, standardisierte Box**, um die
  Kosten gering zu halten
  - zentrales **Kernmodul** mit der Haupt-Firmware
  - **Kommunikationsslots 1–4** im gleichen Format; Standardbestückung
    **LoRa-Modul**, optional Ethernet, Mobilfunk, …
  - auch alle übrigen Hardwaremodule im selben Prinzip (Netzteil, M-Bus, Modbus,
    RS485, Ethernet, …)
  - jedes Modul hat **signierte Firmware** und kommuniziert nur authentifiziert
    über den Bus mit dem Kernmodul
  - Module dürfen **nicht ohne Weiteres getauscht** werden; Vorbild:
    vernetzte Steuergeräte im Automobil (Komponentenschutz, SecOC)
  - **jeder Hersteller darf Module bauen**; signieren dürfen sie nur
    **Trusted Authorities**
- [V] Details zur Hardware: [hardware-konzept.md](hardware-konzept.md)
- [E] **Die Box ist zugleich EMS für den Haushalt** (zusätzlicher Nutzen für Kunden)
  - in **Home Assistant integrierbar**, aber **nur über ein eigenes
    Kommunikationsmodul**; kein direkter Weg von Home Assistant zum Kernmodul oder zum
    Netzbetreiberkanal (quasi airgapped)
  - der Nutzer steuert **bestimmte Parameter** selbst, z. B. bei günstigem Tarif
    laden und bei hohem Tarif einspeisen
  - das System darf **bestimmte Parameter überschreiben**
- [V] Umsetzung EMS / Home Assistant:
  - Home Assistant über einen eigenen Kanal des Ethernet-Moduls `ETH`, nur lokal
    (kein Routing in andere Kanäle oder ins Internet), galvanisch getrennt;
    siehe [hardware-konzept.md](hardware-konzept.md) § 3.3
  - Telemetrie nach außen nur lesend (SoC, Leistung, Status, aktiver Abruf)
  - nach innen nur eine **feste Liste von Parametern mit Wertebereich**, die das
    Kernmodul prüft und begrenzt; keine freien Befehle
  - Vorrang im Kernmodul: (1) Sicherheit und Fallback → (2) signierter Abruf des
    Netzbetreibers → (3) Mindestreserve für Abrufe → (4) Parameter des Nutzers →
    (5) Eigenverbrauchsoptimierung
  - Überschreibungen werden dem Nutzer angezeigt (Grund, Dauer, Quelle)
- [E] Preise kommen **signiert über die Box**, nicht über Home Assistant
- [V] Parameter, Überschreibungen, Szenarien und Tarifmodell:
  [ems-konzept.md](ems-konzept.md)
- [O] Preisgesteuertes Laden vieler Speicher gleichzeitig kann selbst einen Engpass
  erzeugen; das Profil muss das über Vorrang (2) und (3) abfangen
- [O] Wer liefert und montiert die Box (Netzbetreiber oder Installateur)?
- [O] Kommunikationskanal (LoRaWAN, LTE/NB-IoT, Internet). Entscheidung nach
  Recherche ([docs/research/](research/))
- [E] **Anreiz für Endkunden über die Förderung:** Volle Förderung für PV/Speicher
  nur mit standardisierter Steuerschnittstelle und Teilnahme an den Testabrufen;
  ohne diese nur Teilförderung
- [E] **Förderung gestaffelt nach Steuerbarkeit** (Owner, 24.10.2026): je mehr
  Steuerbarkeit der Kunde zulässt, desto höher die Förderung; die volle Förderung
  wird erst ausgezahlt, wenn möglichst viel Steuerbarkeit gegeben ist. Stufen und
  Auszahlung in Tranchen: [ems-konzept.md](ems-konzept.md) § 5
- [E] **Schadlosstellung:** Der Kunde wird durch Eingriffe des Netzbetreibers nie
  schlechter gestellt (entgangene bessere Vermarktung, teurer Nachkauf nach einem
  Entlade-Abruf); Ersatz plus Vergütung: [ems-konzept.md](ems-konzept.md) § 6
- [E] Die Förderung deckt auch die **Installationskosten** der Box
- [E] **Speicherförderungen werden ausdrücklich daran geknüpft:** Ein Speicher
  bekommt die volle Förderung nur, wenn er über die Schnittstelle in **beide
  Richtungen** (laden und entladen) ansteuerbar ist und an den Testabrufen teilnimmt
- [V] Anschluss an die bestehende Regulierung in AT (siehe
  [01-regulierung-finanzierung.md](research/01-regulierung-finanzierung.md)):
  § 76 ElWG verlangt die Steuerschnittstelle seit 1.6.2026 nur für Erzeugung; die
  Förderbedingung schließt diese Lücke für Speicher. Die Netzentgeltbefreiung für
  systemdienliche Speicher (SNE-G-V ab 1.1.2027) gilt laut Querprüfung nur für
  Speicher, die **ausschließlich zur Wiedereinspeisung** betrieben werden, also
  nicht ohne Weiteres für PV-Heimspeicher zur Eigenverbrauchsoptimierung. Für
  Heimspeicher ist die Förderung daher der wichtigere Anreiz.
- [V] Rahmen TOR Typ A V1.4 (seit 1.6.2026): OpenADR-Schnittstelle, Sollwert am
  Netzanschlusspunkt in 1 min, keine Drittsysteme im Pfad, aber **kein
  Speicher-Sollwert**. LoRaWAN als Befehlskanal ergänzt die TOR und weicht von ihr ab;
  das muss im Profil begründet werden.
- [V] Aktives Entladen bleibt freiwillig und wird vergütet; die Förderung
  verlangt die **Fähigkeit**, nicht eine Pflicht zur Entladung
- [V] Mögliche Vorbilder (zu prüfen): EU-Ausschluss von Hochrisiko-Wechselrichtern
  aus EU-geförderten Projekten ab 04/2027 (siehe [04-security.md](research/04-security.md));
  DE Solarspitzengesetz 2025 (Einspeisegrenze für nicht steuerbare Neuanlagen)
  [unbestätigt]; AT EAG-Investitionszuschuss als möglicher Hebel [unbestätigt]
- [O] Weitere Finanzierungsbausteine (Netzentgelt, Verfügbarkeit, Abruf).
  Entscheidung nach Recherche

## 4. Demo

- [E] Demo und Demo-Daten baut Session infra-kg-austria-51 (Owner, 23.10.2026)
- [E] **Demo-Region: Steyr bzw. Steyr-Land** (inkl. Umland wie Kronstorf);
  Entscheidung des Owners am 23.10.2026. Gründe: aktuellstes Orthofoto (BEV-Operat
  Steyr 2025) für die PV-Erkennung, Umspannwerke im BEV-DLM, Mischung aus Stadt,
  EFH-Siedlungen und ländlichen Ortsnetzen
- [V] Umspannwerke der Region laut BEV-DLM (objectid, Name, Betreiber): 66311 Steyr
  (Netz OÖ), 66312 Steyr Nord (Netz OÖ), 18217 Steyr (Sonstige), 18213 ohne Name
  (Sonstige), 18219 Rosenau (Sonstige), 75655 ohne Name (Sonstige), 75701 ohne Name
  (APG), 18047 Ernsthofen (APG), 75642 ohne Name (Sonstige), 18159 Haag (Netz NÖ)
- [V] **Annahme:** Ein UW „Kronstorf“ gibt es im DLM nicht; **75701 (APG, ohne Name)
  dient als Kronstorf-Anker**
- [E] Lizenzen der Demo-Daten: BEV DOP und DLM CC BY 4.0, SimBench ODbL
  (Namensnennung, Share-alike für abgeleitete Datenbank), PV-Modelle CC BY 4.0 bzw. MIT.
  Ultralytics-Laufzeit ist AGPL-3.0: nur vorab berechnete Ergebnisse zeigen, keinen
  öffentlichen Erkennungsdienst anbieten
- [V] 3–5 Ortsnetz-Segmente als Netze aus SimBench (synthetisch), je eines pro Typ
  (Stadt / EFH-Siedlung / ländlich); Engpass und Abruf vor allem in EFH- und
  ländlichen Segmenten
- [E] Der **Netzzustand** (Auslastung, Engpässe) kommt aus den **Simulationen**
  (SimBench/pandapower), nicht aus realen Netzdaten
- [O] **Erkennungsgebiet der PV-Modelle** (Orthofoto → PV-Anlagen): Radius bzw.
  Sektoren um Steyr; derzeit 3×3 km um UW 75701 (Kronstorf-Anker)
- [E] **Kartenbasiert**: Netzsegmente, Umspannwerke/Trafos und Speicherstandorte
  auf einer Karte; Zustand (Engpass, Abruf, Reaktion) sichtbar
- [E] **Tabellarisch**: Geräteliste mit Typ, Leistung, Kapazität, Zuverlässigkeit,
  Reaktionszeit und Status
- [E] **Diagramme**: z. B. Last bzw. Einspeisung am Trafo vor/nach dem Abruf,
  Reaktionsverlauf der Speicher, Zuverlässigkeit je Hersteller bzw. Typ
- [V] Ablauf der Demo entlang des IES-Profils: Engpass entsteht → Abruf an das
  Segment → Geräte reagieren → Smart Meter verifiziert → Zuverlässigkeitswerte
  werden aktualisiert
- [V] KI-Anteil: Prognose der Zuverlässigkeit je Gerät aus den Testabrufen und
  Auswahl der abzurufenden Speicher
- [V] Geräte- und Messdaten synthetisch, klar gekennzeichnet
- [O] Tech-Stack der Demo

## 5. Anbindung an infra-kg

- [E] Später in infra-kg (`../infra-kg-austria`) integrierbar
- [E] Datenquellen und Infrastrukturinformationen (z. B. Umspannwerke,
  Netzgebiete, PV-Anlagen, Last) **jetzt schon** so aufbauen, dass infra-kg sie
  übernehmen kann
- [V] Gemeinsame Kennungen und Formate mit infra-kg verwenden, statt eigene zu erfinden
- [O] **Lizenzen:** infra-kg enthält auch Quellen, die nur privat genutzt werden
  dürfen. In die öffentliche Demo kommen nur offen lizenzierte, öffentliche oder
  synthetische Daten; abgeleitete AGGM-Geometrie wird nicht versioniert.
- [O] Welche infra-kg-Datenbestände genau übernommen werden
