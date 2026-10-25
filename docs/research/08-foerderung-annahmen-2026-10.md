# 08 – Speicherförderung und Modellannahmen (Nachrecherche)

Stand: 25.10.2026. Nachrecherche zu Fragen aus der Demo-Durchsicht (Session 1f).
Konvention wie in `01`: Jede Aussage hat eine Quelle (Kürzel in eckigen Klammern, Liste am Ende).
Sekundärquellen (Händler, Portale, Presse) sind als solche markiert; was nicht gegen eine Primärquelle
geprüft ist, steht als **[unbestätigt]** da.

---

## 1. Speicherförderung in Österreich (Stand Oktober 2026)

1. **Bund, EAG-Investitionszuschuss 2026:** Stromspeicher bis 50 kWh mit fixem Satz **150 €/kWh**, nur
   zusammen mit einer neu errichteten oder erweiterten PV-Anlage; Zuschlag „Made in Europe“ bis 30 % [WKO].
   Drei Fördercalls 2026, der dritte vom 8. bis 22.10.2026 [WKO; Prosolis]. Reine Nachrüstung eines
   Speichers ist in der Bundesförderung nicht vorgesehen [BAM].
2. **Andrang:** Beim zweiten Call 2026 knapp 28.000 Anträge, rund 3.000 Bewilligungen, Topf nach etwa
   36 Sekunden erschöpft; dritter Call rund 8 Mio. € [Enercab] **[unbestätigt, Sekundärquelle]**.
3. **Klima- und Energiefonds:** Förderte 2020–2024 PV-Batteriespeicher für Heimanwender [Klien-TB];
   im Jahresprogramm 2025 keine weiteren Speicherförderungen, Mittel über das EAG gebündelt [Standard-2025].
4. **Land Oberösterreich:** Förderung „Nachrüstung von systemdienlichen Solarstromspeichern“ eingestellt,
   Mittel ausgeschöpft; Anträge bis 30.06.2026 werden noch bearbeitet [OÖ]. Für Steyr gibt es damit derzeit
   keine Förderung für die Nachrüstung eines Speichers.
5. **Umsatzsteuer:** Der Nullsteuersatz für PV endete am 31.03.2025, seither 20 % [oesterreich.gv.at].
6. **Reform ab 2027 (angekündigt August 2026):** Schwerpunkt Speicher und Energiemanagementsysteme statt
   kleiner PV-Anlagen; Nachrüstung von Speichern bei bestehender PV wird gefördert; eigenes Programm für
   Energiemanagementsysteme; Windhundprinzip fällt, Antrag nach Installation und Rechnung; Bonus für
   europäische Komponenten [Standard-2026; Elektrobranche; Leadersnet]. Eine Förderrichtlinie liegt noch
   nicht vor.

**Bezug zum Profil:** Die angekündigte Reform fördert „intelligente Speicher mit Energiemanagement“. Unsere
Förderstufen nach Steuerbarkeit (Kapitel 5 der Demo, `ems-konzept.md`) sind eine mögliche Ausgestaltung
dieser Reform, kein geltendes Recht.

## 2. Wärmepumpen-Anteil 2040 (Szenario „2040 moderate“)

1. Wärmepumpen-Kapazität im UBA-Szenario „mit zusätzlichen Maßnahmen“ von knapp 10 % (2021) auf über 25 %
   (2040), inklusive Wärmepumpen für Fernwärme [BMK-WP].
2. TU Wien „Wärmezukunft 2050“: etwa ein Drittel der beheizten Gebäudefläche mit Wärmepumpe [TUW-2050].
3. Holz deckt 34 % der Raumwärme der Haushalte 2023/24, mit Biomasse-Fernwärme über 43 % [topagrar]
   **[unbestätigt, Sekundärquelle zu Statistik Austria]**.
4. Absatz Heizungs-Wärmepumpen 2023 in Österreich etwa 32.100 [Statista].
5. Im Neubau 2022–2024: 55 % Fernwärme, 27 % Wärmepumpe [Exploreal] **[unbestätigt, Sekundärquelle]**.
6. Die Ausstiegsregeln des Erneuerbare-Wärme-Gesetzes für Bestandsgebäude wurden nicht beschlossen [G2000].

Folgerung für das Modell: 70 % Wärmepumpen 2040 ist ein Stressfall; `2040m` (35 %) liegt näher an den
Szenarien. Abschätzung, nicht belegt: Beim heutigen Absatz kämen bis 2040 grob 10–15 Prozentpunkte dazu.

## 3. Laden von E-Autos: wo und wie viel

1. Prognose Deutschland 2030: 76–88 % private Ladevorgänge (Wohnort und Arbeitgeber), 12–24 % öffentlich
   [RLI/NOW via ZfK].
2. Umfrage unter 200 deutschen Fahrern: 53 % zu Hause, 15 % Arbeit, 32 % öffentlich (Ladevorgänge) [gridX-2025].
3. Schweiz: vier von fünf laden am Wohnort, Mietende deutlich seltener [TCS].
4. 44 % der Fahrer in sechs europäischen Ländern ohne eigenen Ladepunkt (2023) [DJS].
5. Modellwerte Österreich 2021 für E-Pkw: rund 13.100 km im Jahr, 21 kWh/100 km [UBA-EKZ].

Folgerung: gridsim lädt 100 % zu Hause mit 12.000 km und 0,17 kWh/km (rund 2.300–2.500 kWh aus dem Netz je
Auto und Jahr). Mit 13.100 km, 0,21 kWh/km und 55–85 % Heimladen ergäben sich etwa 1.650–2.550 kWh.
Die Energie liegt damit im oberen Bereich; die Abendspitze ist eher etwas zu hoch, in Mehrparteienhaus-Vierteln
deutlich. Eigene Abschätzung, nicht belegt.

## 4. Parkplätze als Lade- und Entladekapazität (Ideensammlung)

1. Ab 2027 müssen neue und erneuerte Ladepunkte ISO 15118-20 unterstützen (AFIR, Delegierter Rechtsakt
   2025/656); eine Ergänzung der Norm deckt bidirektionales AC-Laden ab [AMPECO-05; AMPECO-07].
2. EPBD: Vorverkabelung von Stellplätzen in neuen und stark sanierten Gebäuden; die Kommission hat 2026
   Vertragsverletzungsverfahren gegen alle Mitgliedstaaten wegen der Umsetzungsfrist eröffnet [AMPECO-07; AVERE].
3. Utrecht: öffentliche Stellplätze für bidirektionale Ladepunkte mit Carsharing-Fahrzeugen [FullyCharged].
4. Österreich: Post, EVN und Netz NÖ testen V2G mit fünf E-Transportern; bidirektionales Laden „ab Anfang
   2027“ je nach Regulierung [electrive; leadersnet-Post]. FFG-Netzwerk für bidirektionales Laden [Solarserver].
5. 2025 konnten nur etwa 5 % der batterieelektrischen Autos bidirektional laden [ElectronicDesign]
   **[unbestätigt]**.

Folgerung: Teuer ist der Umrichter, nicht das Kabel. Bei CCS (DC) sitzt er in der Ladestation, bei
bidirektionalem AC-Laden im Auto. Arbeitsplatz-Parkplätze könnten mittags PV aufnehmen, helfen aber nicht
gegen die winterliche Abendspitze an Wohn-Trafos.

---

## Quellen

- [WKO] WKO: EAG-Investitionszuschuss 2026 für Photovoltaik und Stromspeicher. https://www.wko.at/foerderungen/eag-investitionszuschuss-2026-photovoltaik-stromspeicher
- [Prosolis] Prosolis: Photovoltaik Förderung 2026 – die EAG-Fördercalls (Händler). https://prosolis.at/photovoltaik-foerderung-2026-oesterreich-eag/
- [BAM] bam-magazin: Stromspeicher-Förderung in Österreich 2026. https://bam-magazin.at/finanzen-oesterreich/stromspeicher-foerderung/
- [Enercab] enercab: PV- & Speicher-Förderungen in Österreich (Händler). https://www.enercab.eu/foerderungen.html
- [Klien-TB] Klima- und Energiefonds: Technologiebeschreibung Speicher 2026. https://www.klimafonds.gv.at/wp-content/uploads/2026/08/02_TB_Speicher-2026_RZ_Bar.pdf
- [Standard-2025] derStandard: Regierung will Offensive bei Batteriespeichern, doch ein Fördertopf soll versiegen. https://www.derstandard.at/story/3000000279125/regierung-will-offensive-bei-batteriespeichern-doch-ein-foerdertopf-soll-versiegen
- [OÖ] Land Oberösterreich: Förderung eingestellt – Nachrüstung von systemdienlichen Solarstromspeichern. https://www.land-oberoesterreich.gv.at/554598.htm
- [oesterreich.gv.at] Photovoltaik-Förderaktionen und weitere Umweltförderungen. https://www.oesterreich.gv.at/themen/umwelt_und_klima/energie_und_ressourcen_sparen/1/Seite.2430320.html
- [Standard-2026] derStandard: Photovoltaik-Förderung künftig für Speicher statt kleine PV-Anlagen. https://www.derstandard.at/story/3000000336398/photovoltaik-foerderung-kuenftig-fuer-speicher-statt-kleine-pv-anlagen
- [Elektrobranche] ELEKTRObranche.at: Ministerium plant PV-Förderreform 2027 (20.08.2026). https://elektrobranche.at/artikel/ministerium-plant-pv-foerderreform-2027/
- [Leadersnet] Leadersnet: Hattmannsdorfer macht Stromspeicher zum Schwerpunkt der Energiepolitik. https://www.leadersnet.at/news/102968,hattmannsdorfer-macht-stromspeicher-zum-schwerpunkt-der.html
- [BMK-WP] BMK: Der Beitrag von Wärmepumpen zur Wärmewende. https://www.bmk.gv.at/dam/jcr:dbb6b843-401a-4ebb-a382-3c4a4e1a5d49/BMK_Der%20Beitrag%20von%20W%C3%A4rmepumpen%20zur%20W%C3%A4rmewende%20-%20Unterlage%20zum%20Branchentreff.pdf
- [TUW-2050] TU Wien: Wärmezukunft 2050 (Kurzfassung). https://www.propellets.at/assets/upload/Presseaussendungen/2018.01.24%20TU%20Studie%20Energiewendeszenario/Studie_Waermezukunft2050_Kurzfassung.pdf
- [topagrar] topagrar: Holz ist klare Nummer eins bei Österreichs Haushalten. https://www.topagrar.com/energie/news/holz-ist-klare-nummer-eins-bei-osterreichs-haushalten-20014562.html
- [Statista] Statista: Absatz von Heizungs-Wärmepumpen in Österreich. https://de.statista.com/statistik/daten/studie/939112/umfrage/absatz-von-heizungs-waermepumpen-in-oesterreich
- [Exploreal] ImmoScout24/Exploreal: Heizungsart im Neubau. https://www.immobilienscout24.de/content/dam/is24at/dokumente/Unternehmen/2025/Presse/250918_PA_IS24_Heizungsart_Exploreal.pdf
- [G2000] Global 2000: Wärmewende-Check. https://global2000.at/sites/global/files/g2_report_warmewende-check_125-web.pdf
- [RLI/NOW via ZfK] ZfK: Neue Studie ermittelt Bedarf an öffentlichen Ladesäulen bis 2030. https://www.zfk.de/mobilitaet/e-mobilitaet/neue-studie-ermittelt-bedarf-an-oeffentlichen-ladesaeulen-bis-2030
- [gridX-2025] Renewable Energy Magazine: gridX report 2025. https://renewableenergymagazine.com/electric_hybrid_vehicles/new-gridx-report-finds-the-netherlands-leading-20250414
- [TCS] TCS: Wie lädt die Schweiz. https://www.tcs.ch/de/der-tcs/presse/medienmitteilungen-2025/wie-laedt-die-schweiz.php
- [DJS] DJS Research: 44 % of EV drivers do not have a charge point at home. https://www.djsresearch.co.uk/AutomotiveMarketResearchInsightsAndFindings/article/44percent-of-EV-drivers-do-not-have-a-charge-point-at-home-finds-survey-05390
- [UBA-EKZ] Umweltbundesamt: Emissionskennzahlen Verkehrsmittel, Dokumentation. https://www.umweltbundesamt.at/fileadmin/site/themen/mobilitaet/daten/ekz_doku_verkehrsmittel.pdf
- [AMPECO-05] AMPECO: May 2026 EV charging policy update. https://www.ampeco.com/blog/may-2026-ev-charging-policy-update/
- [AMPECO-07] AMPECO: July 2026 EV charging policy update. https://www.ampeco.com/blog/july-2026-ev-charging-policy-update/
- [AVERE] AVERE: EPBD guide. https://www.avere.org/l/library/download/urn:uuid:88bbd8b2-4497-4915-8bd4-3179c54ff4a0/avere_epdb+guide.pdf
- [FullyCharged] Fully Charged: Utrecht's Renault 5 powered supergrid. https://fullycharged.show/episodes/vehicle-to-grid-the-evs-making-money-right-now-unveiling-utrechts-renault-5-powered-supergrid/
- [electrive] electrive: Österreichische Post testet V2G-Laden mit fünf E-Transportern. https://www.electrive.net/2026/03/10/oesterreichische-post-testet-v2g-laden-mit-fuenf-e-transportern/
- [leadersnet-Post] leadersnet: Post und Netzbetreiber machen E-Flotte zum mobilen Speicher. https://www.leadersnet.at/news/98208,post-und-netzbetreiber-machen-e-flotte-zum-mobilen.html
- [Solarserver] Solarserver: Österreich gründet Innovationsnetzwerk für bidirektionales Laden. https://www.solarserver.de/2024/11/15/oesterreich-gruendet-innovationsnetzwerk-fuer-bidirektionales-laden
- [ElectronicDesign] Electronic Design: A big bet on bidirectional EV charging. https://www.electronicdesign.com/markets/automotive/article/21134047/a-big-bet-on-bidirectional-ev-charging
