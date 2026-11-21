# Freezer Watch

**Predicting −80 °C lab freezer failures days ahead, trained on simulated freezers, checked against real data.**
NullHacks Helsinki, 21 Nov 2026. Theme: simulate data for physical AI.

- **Live demo:** open [`index.html`](index.html) in a browser (no install, ~20 s to train in the page). Inject a fault, watch the model warn days before the freezer loses temperature.
- **Pitch deck:** https://claude.ai/artifact/Qjn2mC4PQ5U55GtGvmpddk (may need sharing to open)
- **Market notes:** [`MARKET.md`](MARKET.md) · **Competitors:** [`research/competitors.md`](research/competitors.md) · **Next devices:** [`research/next-devices.md`](research/next-devices.md)
- **Dataset:** [`data/`](data/) (300 simulated freezers, hourly, ground-truth labels)

### Repo map
| Path | What |
|---|---|
| `index.html` | Freezer Watch: simulator, in-browser model training, live dashboard, proof charts |
| `coffee.html`, `coffee_v1_guesses.html` | Same engine on an espresso machine (calibrated v2, and the uncalibrated v1) |
| `analysis/run_robust.js`, `robust_page.js` | Multi-seed, cross-brand, 1,000-healthy-freezer and baseline-rule evaluation (`node analysis/run_robust.js`, needs Playwright) |
| `analysis/real_freezer_backtest.py` | Backtest of the simulator-trained model on the real Danish biobank freezer data (`model.json` = exported weights) |
| `analysis/analyze.py`, `bt.py`, `effects.json` | Hydraulic test-rig calibration (UCI dataset 447) |
| `analysis/export_dataset.js`, `export_model.js` | Regenerate `data/` and `analysis/model.json` |

Third-party data is not redistributed. Get it from the sources: Danish biobank ULT freezer dataset (Huang et al., Sci Data 2023, figshare doi:10.6084/m9.figshare.c.6805332.v1; code lab.compute.dtu.dk/taohu/ult-freezers-labelled-dataset-sci-data) and UCI dataset 447 (hydraulic rig). `coffee.html` embeds per-cycle summary features derived from UCI 447 for the in-browser backtest, with attribution.

---

## Details

Predictive maintenance for **−80 °C lab freezers**, trained on simulated data. Same engine also runs an espresso-machine version, to show it carries over to other machines.

**Run it:** open `index.html` (freezer) or `coffee.html` (espresso) in any modern browser. No install, no server, no internet. Training takes ~20–25 s on load.
`coffee_v1_guesses.html` is the first, uncalibrated espresso version (before/after comparison).

## Freezer version (`index.html`)
- 1 step = 1 hour. 7 signals per freezer, chosen to match what the real Danish National Biobank freezer dataset records: chamber temperature (RTD), compressor on-time per cycle (from the compressor state signal), 1st-stage suction, interstage heat exchanger, evaporator outlet, 2nd-stage compressor sump, pull-down time after door openings.
- 4 faults, in the same proportions as the real Revco service log: refrigerant leak (stage 1), 1st-stage compressor, 2nd-stage compressor, door tightness / insulation. Electrical faults (2nd commonest) are sudden and out of scope.
- Nuisances the model must ignore: door openings in working hours, cooling-water temperature changes, slow healthy ageing of compressor on-time, sensor glitches, slow drift.
- Compared against a conventional −70 °C chamber-temperature alarm on the same simulated freezers.
- Headline numbers: see Robustness checks below (5 seeds). One run in the page gives similar numbers.

### Freezer sources
- Huang, Nøstvik, Bacher, Markussen, Møller, "Labelled dataset for Ultra-Low Temperature Freezer to aid dynamic modelling & fault detection and diagnostics", *Scientific Data* 10 (2023), doi:10.1038/s41597-023-02808-6 (read via PMC10710515). 53 freezers, 1-min data, 42 labelled fault events in 24 Revco freezers; fault labels are service-request dates, which lag true onset. Data on figshare, code at lab.compute.dtu.dk/taohu/ult-freezers-labelled-dataset-sci-data. **Both hosts were blocked from our build environment, so we have not backtested on it yet.** That is the obvious next step.
- Used from the paper: signal list, −80 °C setpoint, fault categories, "2nd-stage leak: sump changes first, chamber RTD last", ice buildup raising duty, door opening (54 s → ~−60 °C, ~1 h recovery), chilled water 10 °C → 20 °C change, on-time drifting over years.
- Our guesses: healthy loop temperature levels, ~35 min on-time baseline, fault lifetimes, the −70 °C alarm level, chamber warming curve. Fault sizes (~1–2σ per loop sensor) reuse the leakage effect sizes measured on the hydraulic rig below.

### Robustness checks (freezer, `analysis/run_robust.js`, results in `analysis/robustness_results.json`)
All on simulated freezers. Every alarm rule gets the same operating point: threshold set so ≤10% of 120 separate healthy validation freezers ever alarm.

| Method | Failures caught | Caught ≥1 day ahead | Median warning | Healthy freezers with a false alarm (1,000 freezers × 125 days) |
|---|---|---|---|---|
| **Our model** (5 seeds) | 100% (all seeds) | 100% | 8.1–8.8 days | 0.4% |
| Any-sensor z-score rule | 96–98% | 79–87% | 2.8–3.6 days | 15% |
| Compressor on-time rule | 15–29% | 12–27% | (few caught) | 13% |
| Conventional −70 °C chamber alarm | 90–92% | 46–50% | 1.0–1.2 days | 0% |

- Fault mix and types match the real Revco service log (`fault_summary.xlsx` from the biobank dataset's repository, not redistributed here; 46 events): refrigerant leak (stage 1) 11, 2nd-stage compressor 7, 1st-stage compressor 5, door/insulation 4. Electrical faults (7 of 46) are sudden and not modelled; "unstable operation", "data missing" and similar (≈15) are not modelled either. So the model addresses roughly 27 of the 46 real service events.
- Fault named correctly when caught: **59–66%** across seeds (4 fault types, chance 25%). Compressor stage 1 vs leak is the main confusion; this is the weakest part.
- **Cross-brand test:** model trained only on fixed-speed (Revco-like) freezers, tested on variable-speed (Haier-like) freezers that log whole degrees and whose compressor on-time reacts half as much: still 100% caught, median 7.7 days, 1/73 false alarms, fault named 65%. Training on Haier-like directly: 8.3 days, 1/73. Both brands are our simulation, so this shows the baseline-relative features survive these particular differences, not that it works on real Haier units.
- Why the model beats a plain threshold: it combines small (~1–2σ) shifts across several loop sensors and their trends against each freezer's own baseline; no single sensor moves enough early on.
- **Big caveat:** detection is easy in our simulator because every simulated fault grows steadily until failure. Real faults include sudden electrical ones and messy, partially repaired leaks. The real-data backtest (below) is what would make these numbers credible.

### Real-data backtest (ready, waiting for data)
`analysis/real_freezer_backtest.py --dir <folder>` takes the biobank's `fault_summary.xlsx` and per-freezer `*_temp.parquet` files, rebuilds the same hourly signals (on-time from the compressor state bit), runs the simulator-trained model (`analysis/model.json`, exported by `analysis/export_model.js`), and reports: days of warning before each service date vs the −70 °C alarm, false alarms on fault-free 125-day stretches, and real noise / autocorrelation / fault sizes vs the simulator's assumptions. Tested only on fake data in the paper's format so far; column mapping follows the paper's Table 2 and is printed for checking.

### Simulated dataset
`data/ult_freezer_sim.csv.gz`: 300 freezers (150 Revco-like, 150 Haier-like), ~585k freezer-hours, ground-truth fault labels and hours-to-failure. See `data/README.md`.

### Where this fits (from `research/competitors.md`, 20-minute scan)
- Real failure prediction exists only from makers on their own freezers (Stirling Ultracold VAULT100, Thermo Fisher TSX connected services).
- Independent any-brand monitors (XiltriX, Monnit, Elemental Machines, ELPRO, Eppendorf VisioNize sense) collect temperature, door and sometimes compressor current, but alarm on thresholds or have people read graphs; none publishes a model, lead time or accuracy.
- Gap: a brand-agnostic model that says which fault and how many days ahead, with stated accuracy, running on signals those vendors already collect. Plausible route: license the model to independent monitoring vendors.

---

## Espresso version (`coffee.html`)

## Pipeline (all in the page)
1. **Simulate** 1,000 virtual espresso machines shot by shot. 7 sensors: pump pressure, boiler temp, shot time, vibration, heat recovery, water flow, pump power. 80% develop one of 4 faults (scale, worn gasket, failing pump, dull burrs) that worsen until breakdown. Non-fault nuisances: barista grind tweaks, daily room-temperature cycle, sensor glitches, slow sensor drift.
2. **Train** a small neural net (21→32→5, written from scratch) on 30-shot windows compared to each machine's own 200-shot baseline: "which fault breaks this machine within 300 shots", plus a shots-left regressor.
3. **Set the alarm threshold** on 120 separate healthy validation machines (≤10% may false-alarm).
4. **Test** on 400 unseen simulated machines.
5. **Reality check:** the same model code is trained and tested on real data from a hydraulic test rig (below).

## Real data used
- **UCI dataset 447, "Condition monitoring of hydraulic systems"** (ZeMA / Saarland University; Helwig, Pignanelli, Schütze, I2MTC 2015, doi:10.1109/I2MTC.2015.7151267). Real test rig, 2,205 one-minute cycles; cooler, valve, pump leakage and accumulator degraded on purpose and labelled. Downloaded from a GitHub mirror (YoverCC/Project-Data-hydraulicsystemuci) because the UCI/Zenodo hosts were blocked from our build environment; row/column counts match the official description.
- **Match to espresso:** loose proxy. Same component types (pump, heat exchanger, valve; pressure, flow, temperature, vibration, motor power), very different machine. Not run-to-failure: conditions are stepped, not gradual.

What we measured and changed (`analysis/analyze.py`, regression of cycle averages on the four conditions, stable cycles n=1,449):
- Severe pump leakage moves each sensor only ~1–1.3σ → pump/gasket fault sizes cut from our guessed ~10–15σ to ~1.5σ.
- Cooler near failure: temperatures +24–29σ → scale (heat-transfer fault) set to +25σ on heat recovery.
- Noise is mostly slow drift (cycle-to-cycle autocorrelation 0.72–1.0) → ~72% of sim noise is now drift, baseline 200 shots.
- Valve lag is invisible in cycle averages and needs the pressure-curve shape → not yet simulated (next step).

## Results (measured in the page, will vary slightly by browser)
| | v1 (guessed physics) | v2 (calibrated) |
|---|---|---|
| Failures caught before breakdown | 100% | 51% |
| Healthy machines with a false alarm | 0% | 7% |
| Caught by fault: scale / pump / gasket / burrs | 100% each | 73% / 72% / 41% / 18% |

Same model on the **real rig** (held-out blocks of cycles): cooler 99%, pump leakage 99%, valve 100% (89% with averages only), accumulator 60% (chance ~39–45%).
Caveat: the rig keeps each condition for long runs, so even blocked splits are probably optimistic.

## Honest caveats
- Lifetimes, wear curves, burr fault, absolute noise levels, 100 shots/day: invented.
- Which espresso sensor moves in which direction is our reasoning; only the *size* of effects is calibrated, and from a different machine.
- One fault at a time; four known fault types.

## Related reading
Nieminen et al., "Synthetic Data for Predictive Maintenance: A Systematic Review and Framework for Industry 4.0 Applications", Journal of Intelligent Manufacturing (2026), doi:10.1007/s10845-026-02795-6. Reviews 86 papers; finds hybrid/physics-informed generation most valued and names validation against real data as a key gap. This project is a small hybrid example: physics-style simulator + effect sizes calibrated on real data.

## Code map (same in both pages)
- `stepMachine` / `FAULTS`: simulator and fault physics (calibration comments inline)
- `features`, `MLP`, `trainAll`, `calibrateThreshold`, `evaluate`: ML pipeline
- `HYD`, `realBacktest`: embedded real rig features and the real-data backtest
- `renderLive` / `tick`: live dashboard
