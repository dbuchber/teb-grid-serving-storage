# Bedrohungsmodell „Grid-Serving Storage“ (eine Seite)

Stand 25.10.2026. Grundlage: [Profil v2](context/profil-v2.md) §3 (harte Grenzen), §5 (PKI, Widerruf, Replay, Zeit, Firmware), §6 (LoRaWAN) und [Recherche Security](research/04-security.md).
Status je Maßnahme: **entschieden(v1)** = im Profil v1 festgelegt · **Vorschlag(v2)** = im Profil v2 vorgeschlagen · **Vorschlag** = neu in diesem Dokument, noch nicht im Profil · **offen** = ungeklärt.
Nichts davon ist implementiert oder gegen echte Geräte getestet. Eine formale Analyse nach IEC 62443 bzw. im NIS2-Kontext des VNB ist **offen** (Pflicht vor Pilotphase 2).

## Werte (Assets)

| Wert | Warum schützenswert |
|---|---|
| Netzstabilität im Segment (Trafo, Spannung) | Viele Speicher gleichzeitig können den Engpass verschärfen statt lindern |
| VNB-Betriebs- und Widerrufsschlüssel (HSM) | Wer sie hat, kann gültige Abrufe bzw. Widerrufe senden |
| Harte Grenzen und Vertrauensanker in der Box-Firmware | Letzte Verteidigungslinie gegen gültig signierte Fehlbefehle |
| Notstromreserve und Batterielebensdauer des Haushalts | Kundennutzen, Vertrauen, Haftung |
| Mess- und Vergütungsdaten (Smart Meter, Box-Protokoll) | Grundlage für Verifikation (P5) und Abrechnung |
| Verfügbarkeit des Broadcast-Kanals (LoRaWAN) | Ohne Kanal kein Abruf, nur Fallback P6 |

## Angreifer, Wirkung und Gegenmittel

| Angreifer | Was er **innerhalb der harten Grenzen** erreichen kann | Erkennung | Eindämmung | Wiederherstellung | Restrisiko |
|---|---|---|---|---|---|
| **Gestohlener VNB-Betriebsschlüssel** | Alle Speicher eines Segments gleichzeitig *gegen* den Engpass fahren (z. B. Entladen bei Einspeisespitze, Laden bei Abendspitze): bis 3 h je Abruf, 4 h und 3 Abrufe je Tag, Rampe ≤ 10 % P_n/min (voller Wechsel in 10 min), Startstreuung 1–5 min. Notstromreserve und SOC 10–95 % bleiben (entschieden(v1) bzw. Vorschlag(v2)). | Anomalie-Erkennung: Trafomessung und Smart-Meter-Lastgang gegen erwartete Wirkung des Abrufs (Vorschlag); Abrufprotokoll im Backend gegen Freigaben abgleichen (Vorschlag) | Zertifikat an Netzbereichs-ID gebunden, Box nimmt nur Abrufe für das eigene Segment an (Vorschlag(v2)); Vier-Augen-Freigabe im HSM (Vorschlag, aus 04-security S7); max. 6 signierte Nachrichten/h (Vorschlag(v2)); **lokale Plausibilitätsprüfung in der Box: Richtung des Abrufs gegen eigene Messung am Netzanschluss** (Vorschlag) | Epochen-Widerruf über LoRa, Rollout innerhalb von Stunden, Wiederholung 3× in 24 h (Vorschlag(v2)); neuer Schlüssel nach P10 | **Hoch für ein Segment, begrenzt im System.** Bis zum Widerruf ist die volle Wirkung eines Tages (4 h) möglich. Die Plausibilitätsprüfung in der Box ist der wirksamste offene Hebel. |
| **Kompromittierte Hersteller-Cloud** | Über den Herstellerpfad Wechselrichter umkonfigurieren oder abschalten (siehe Solarman/Deye 2024, SUN:DOWN 2025). Netzabrufe fälschen kann sie nicht. | Smart Meter zeigt Leistungsänderung ohne Netzbefehl (Vorschlag(v2), 04-security C) | Kein Cloudpfad im Netzsteuerpfad, Box spricht Wechselrichter lokal an (entschieden(v1)); Hersteller-Updates ändern Grenzen und Vertrauensanker nicht ohne zweite Signatur der Trusted Authority (Vorschlag(v2)) | Hersteller-CA sperren (Kurzliste, P10); Cloud vom Gerät trennen | Mittel: Der Wechselrichter selbst bleibt angreifbar, solange er online ist. Liegt außerhalb des Profils. |
| **LoRa-Jammer / -Spoofer** | Jamming: keine Abrufe, keine Widerrufe im betroffenen Gebiet. Spoofing: gefälschte Nachrichten scheitern an der Signatur; alte Nachrichten am Replay-Zähler (Vorschlag(v2)). DeviceTimeAns ist nur per MIC gesichert, **Zeit nicht Ende-zu-Ende gesichert** (Vorschlag(v2) benennt das selbst). | Gateway-Rauschpegel, fehlende Quittungen über IP-Modul bzw. Testabrufe (Vorschlag) | Fallback P6: Zustand bis Abrufende bzw. 15 min halten, dann gestreute Rückkehr in den Eigenverbrauch (Vorschlag(v2)); Zeitkorrektur max. ±120 s/Tag, keine Rückwärtssprünge > 120 s (Vorschlag(v2)); signierter Zeitstempel im Abruf (Vorschlag(v2)) | Störquelle orten (Fernmeldebehörde); Abruf über OpenADR/IP-Modul, wo vorhanden (offen) | Jamming: **kein Schaden, aber kein Dienst**. Zeitmanipulation verschiebt Abrufe höchstens um Minuten. Eine signierte Zeitquelle ist offen. |
| **Kompromittiertes Home Assistant / Heimnetz** | Gefälschte Preise oder Befehle ins Heimnetz einspielen; Komfortfunktionen stören | Box ignoriert unsignierte Netz- und Preisnachrichten, Protokoll | Eigener Kanal ohne Weg zum Kernmodul oder zum VNB-Kanal (Vorschlag(v2)); Preise nur signiert über die Box, Plausibilitätsfenster −50 … +100 ct/kWh (entschieden(v1)) | Heimnetz neu aufsetzen; keine Netzwirkung | Gering für das Netz, Komfortverlust für den Haushalt. |
| **Innentäter beim VNB** | Wie gestohlener Schlüssel, aber mit legitimem Zugang und Wissen über Engpässe | Protokoll aller Abrufe mit Bearbeiter, Abgleich mit Leitstellen-Freigabe (Vorschlag) | Vier-Augen-Freigabe im HSM über einer Schwelle und für Änderungen an Grenzen und Sperrlisten (Vorschlag, aus 04-security S7); Leistungsbudget je Schlüssel und Segment (Vorschlag) | Widerruf, Rollen neu vergeben | Mittel: Zwei kollaborierende Innentäter umgehen die Freigabe. Die harten Grenzen bleiben. |
| **Kompromittiertes Box-Modul / Firmware** | Zugelassenes Zusatzmodul (z. B. Aggregator) sendet eigene Fahrpläne; manipulierte Firmware könnte Grenzen entfernen | Smart Meter gegen Box-Protokoll; Testabrufe P3 | Module laufen mit signierter Software, ohne Zugriff auf Netzschlüssel (Vorschlag(v2)); Secure Boot, zwei Signaturen für Updates, Rollback-Schutz (Vorschlag(v2)); kein Firmware-Update über LoRa (Vorschlag(v2)) | Modulzertifikat sperren; A/B-Rückfall; Servicetermin | Mittel bis hoch bei Lieferkettenangriff auf den Firmwareschlüssel eines Herstellers, darum die zweite Signatur der Trusted Authority. Betreiber der Trusted Authority und Root-CA: offen. |

## Was bewusst nicht abgedeckt ist

- Angriffe auf den Smart-Meter-Pfad selbst und auf Leitstellen-IT des VNB (gehören zur NIS2-Pflicht des VNB).
- Physische Manipulation einzelner Boxen (Wirkung auf ein Haus begrenzt).
- Systemweite Wirkung über viele Segmente: Leistungsbudget je Schlüssel deutlich unter der Systemschwelle (Größenordnung 3 GW laut DNV, 04-security) ist **offen** zu dimensionieren.

## Text for the submission field “Security and resilience”

> The box verifies every command itself (signature, role, network-area binding, expiry, replay counter) and enforces hard firmware limits no message can lift: at most 3 calls and 4 h per day, 3 h per call, 10 %/min ramps, randomised start and staggered return, backup reserve never touched; keys are revoked over the radio via epochs within hours, and LoRa jamming only triggers a safe fallback to self-consumption. We state the residual risk openly: a stolen grid-operator key could still drive all batteries of one segment against the bottleneck for up to 4 h per day, so we propose two-person release in the HSM, a local plausibility check of call direction against the box's own measurement, and anomaly detection via transformer and smart-meter data. This is a concept only: nothing is implemented or tested against live infrastructure, and a formal IEC 62443 / NIS2 analysis is still open.
