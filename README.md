# Brisbane River Water-Quality Analysis (Colmslie Monitoring Buoy)

Exploratory time-series analysis of physicochemical water-quality parameters
and in-situ flow readings collected at 30-minute intervals from the Brisbane
River monitoring buoy at **Colmslie**, spanning **August 2023 – June 2024**
(~11 months, ~30,600 usable records).

Data source: [Queensland Government Open Data Portal](https://www.data.qld.gov.au/dataset/brisbane-river-colmslie-site-water-quality-monitoring-buoy/resource/0ec4dacc-8e78-4c2a-aa70-d7865ec098e2).

---

## Repository structure

```
.
├── data/
│   ├── brisbane_water_quality.csv   # raw dataset (unmodified)
│   └── README.md                    # data dictionary + provenance
├── src/
│   └── analysis.py                  # cleaning, stats, and figure generation
├── figures/                         # generated plots (produced by analysis.py)
├── reports/
│   ├── findings.md                  # detailed write-up
│   └── summary_statistics.csv       # generated summary table
├── requirements.txt
├── LICENSE
└── README.md
```

## Reproduce

```bash
pip install -r requirements.txt
python src/analysis.py
```

This regenerates every figure in `figures/` and the summary table in
`reports/`.

---

## Dataset at a glance

| Property | Value |
|---|---|
| Period | 2023-08-04 → 2024-06-27 |
| Interval | 30 minutes |
| Usable records | ~30,600 |
| Parameters | water speed & direction, temperature, dissolved oxygen (mg/L & % sat), pH, salinity, specific conductance, chlorophyll, turbidity |

Missingness varies by sensor — dissolved-oxygen and temperature channels have
the largest gaps (13–19%), while flow and pH are near-complete (<4%). Each
measurement ships with a paired `[quality]` flag column.

---

## Key findings

### 1. Strong seasonal cycle driven by the sub-tropical climate
Temperature swings from ~18.6 °C (June, austral winter) to ~28.3 °C (February,
austral summer). Dissolved oxygen moves in the opposite direction, exactly as
expected from oxygen solubility physics.

![Time series](Users/madhu/repo/figures/01_timeseries.png)

### 2. Dissolved oxygen is inversely tied to temperature
Across the record, temperature and dissolved oxygen correlate at **r = −0.38**
(and pH vs temperature at **−0.58**). Warmer water holds less oxygen, so the
warm months carry a lower baseline DO — a standing stress factor for aquatic
life during summer.

![Correlation](figures/03_correlation.png)

### 3. The wet season freshens and muddies the river
Salinity sits near ~35 PSU through winter/spring, then drops to **~28 PSU in
Jan–Feb** as summer rainfall and catchment runoff dilute the estuary.
Turbidity climbs in the same window and peaks in **May (~10.7 NTU)**,
consistent with runoff-driven sediment loads.

![Monthly means](figures/02_monthly_means.png)

### 4. A textbook daily photosynthesis/respiration cycle
Dissolved oxygen reaches its **minimum just before dawn (~06:00)** and its
**maximum in mid-afternoon (~16:00)** — the signature of daytime
photosynthesis adding oxygen and night-time respiration removing it.
Chlorophyll peaks a few hours later, in the early evening.

![Diurnal cycle](figures/04_diurnal.png)

### 5. Flow is tidal, along a dominant flood/ebb axis
Water direction is strongly bimodal rather than uniform, reflecting the
twice-daily tidal reversal of an estuarine channel rather than a steady
downstream current.

![Flow rose](figures/05_flow_rose.png)

### 6. Salinity and specific conductance are redundant
The two correlate at **r = 1.00** — they encode the same information. Keep only
one when modelling to avoid multicollinearity.

---

## Implications

- **Ecological risk windows.** The combination of high summer temperature and
  its associated low-DO baseline marks the period of greatest hypoxic stress
  for fish and benthic life. Monitoring and any interventions should be
  weighted toward the warm months.
- **Rainfall is the master variable.** The salinity drop and turbidity spike in
  the wet season show the estuary responds sharply to runoff. Pairing this
  buoy with rainfall/discharge data would likely explain much of the
  short-term variance and is the natural next dataset to join.
- **Sample timing matters.** Because DO swings by ~0.8 mg/L over a single day,
  any manual spot-sample or compliance threshold must account for time of day;
  a pre-dawn reading and an afternoon reading tell very different stories.
- **Modelling guidance.** For any predictive model: drop specific conductance
  (redundant with salinity), treat DO and temperature as coupled, and include
  hour-of-day and month (or rainfall) as features to capture the two dominant
  cycles.
- **Data-quality caveats.** DO and temperature gaps of 13–19% mean seasonal
  means for those channels rest on uneven coverage; use the `[quality]` flag
  columns before drawing firm conclusions, and consider gap-aware
  interpolation for time-series modelling.

See [`reports/findings.md`](reports/findings.md) for the full write-up.

---

## License & attribution

Analysis code is released under the MIT License (see `LICENSE`). The underlying
data is © State of Queensland and provided under the terms of the Queensland
Government Open Data Portal; please retain the source attribution above.
