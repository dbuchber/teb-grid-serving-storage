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
