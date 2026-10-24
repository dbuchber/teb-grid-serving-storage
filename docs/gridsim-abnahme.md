# Abnahme gridsim gegen Session 18 (2026-10-24)

Ungesteuert, Speicher Eigenverbrauch, PV × 1, 20 Seeds je Einstellung (Median, Band 10–90 %).
Referenz: Tabellen von Session 18 vom 24.10.2026 (`steyr_storage_need.py --heat lod1 --district-heating`).
Toleranz ± 30 %, bei kleinen Werten absolut (3 Stationen, 1 MWh). Alle Werte sind Modellwerte.

| Wetter | Szenario | Kennzahl | gridsim Median | Band 10–90 % | Referenz | Verhältnis | ok |
|---|---|---|---|---|---|---|---|
| 2023 | heute | stations_load_congestion | 1 | 1–2 | 2 | 0.50 | ja |
| 2023 | heute | e_net_mwh | 0.07 | 0.0161–0.1392 | 0.2 | 0.35 | ja |
| 2023 | 2030 | stations_load_congestion | 44 | 38.8–49 | 39 | 1.13 | ja |
| 2023 | 2030 | e_net_mwh | 8.943 | 7.5456–10.1591 | 12 | 0.75 | ja |
| 2023 | 2040 | stations_load_congestion | 193 | 190–197 | 193 | 1.00 | ja |
| 2023 | 2040 | e_net_mwh | 354.18 | 339.692–366.177 | 337 | 1.05 | ja |
| 2017 | heute | stations_load_congestion | 1.5 | 1–3 | 4 | 0.38 | ja |
| 2017 | heute | e_net_mwh | 0.104 | 0.0246–0.1865 | 0.4 | 0.26 | ja |
| 2017 | 2030 | stations_load_congestion | 56 | 49.8–63 | 52 | 1.08 | ja |
| 2017 | 2030 | e_net_mwh | 12.588 | 10.2576–17.3083 | 28 | 0.45 | nein |
| 2017 | 2040 | stations_load_congestion | 198.5 | 194.9–202.1 | 200 | 0.99 | ja |
| 2017 | 2040 | e_net_mwh | 1116.26 | 1059.16–1177.47 | 1057 | 1.06 | ja |
| 2012 | heute | stations_load_congestion | 3.5 | 2–5 | 5 | 0.70 | ja |
| 2012 | heute | e_net_mwh | 0.2165 | 0.0897–0.5285 | 2.3 | 0.09 | nein |
| 2012 | 2030 | stations_load_congestion | 100 | 94.9–103.8 | 90 | 1.11 | ja |
| 2012 | 2030 | e_net_mwh | 64.491 | 50.5216–93.2828 | 116 | 0.56 | nein |
| 2012 | 2040 | stations_load_congestion | 208 | 205.9–210.1 | 210 | 0.99 | ja |
| 2012 | 2040 | e_net_mwh | 3736.98 | 3567.31–3903.13 | 3573 | 1.05 | ja |

Tendenz (heute < 2030 < 2040, 2023 < 2017 < 2012): ja

| PV-Faktor | Stationen mit Einspeiseengpass (Median, Band) | Referenz |
|---|---|---|
| × 1 | 3 (3–3) | 1–3 |
| × 1.5 | 19 (19–19) | 19–19 |
| × 2 | 34 (34–34) | 31–34 |

## Gründe für Abweichungen

- E-Auto-Zuteilung und Ladeverhalten vektorisiert: andere Zufallsfolge als `steyr_wp_ev`, 20 Seeds statt 1.
- Heimspeicher entladen nicht ins E-Auto (wie `steyr_v2g_demo`); `steyr_storage_need` nimmt E-Autos in die Speicherlast.
- Wärmepumpe in float32 (Abweichung < 1e-4 gegen die alte Formel).

## Nachprüfung der Abweichungen bei E_netto (2030, heute)

Stationszahlen, 2040 und Einspeiseengpässe treffen die Referenz. Bei E_netto liegt gridsim in den knappen
Szenarien unter der Referenz, z. B. 2012/2030 Median 64 MWh (Band 51–93) gegen 116 MWh. Nachprüfung auf
hetzner am 24.10.2026:

| Lauf (2012, 2030, ungesteuert) | Stationen | E_netto MWh | größte Station MWh |
|---|---|---|---|
| eingefrorenes `steyr_storage_need.py` (Seed von Session 18) | 90 | 115,6 | – |
| gridsim-Speicher + alte WP/E-Auto-Lasten | 91 | 115,6 | – |
| alte WP-Zuteilung, Seed 0 (= Session 18) | 92 | 115,5 | 40,7 |
| alte WP-Zuteilung, Seed 1 | 99 | 50,9 | 12,0 |
| alte WP-Zuteilung, Seed 2 | 108 | 79,4 | 14,6 |
| alte WP-Zuteilung, Seed 3 | 93 | 66,6 | 14,4 |
| alte WP-Zuteilung, Seed 4 | 102 | 72,5 | 18,1 |

**Befund:** Speicher, Wärmepumpenformel und E-Auto-Modell der Bibliothek reproduzieren die alte Rechnung
(Jahresenergie WP 65,3 / 65,6 GWh, E-Auto 26,2 / 26,3 GWh, Summe der Stationsspitzen ± 1 %). Der Unterschied
kommt aus der zufälligen Verteilung der Wärmepumpen: Im Seed von Session 18 hat eine einzelne Station ein
langes Winterereignis mit 40,7 MWh, in anderen Seeds sind es 12–18 MWh. E_netto summiert das größte Ereignis je
Station und reagiert in Szenarien mit wenigen Engpässen stark auf einzelne Stationen. Die Referenzwerte für
2030 und „heute“ sind deshalb Einzelziehungen am oberen Rand; das gridsim-Band (20 Seeds) ist die belastbarere
Angabe. **Abnahme: plausibel.**
