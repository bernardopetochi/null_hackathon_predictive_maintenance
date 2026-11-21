# Real-data backtest: Revco freezer 806278 (Danish National Biobank)

Data: `806278_temp.parquet` (1-min, 2013-01 → 2023-04) from the dataset of Huang et al., Scientific Data 2023 (not redistributed here). Fault label: refrigerant leakage at stage 1, service registered **2022-04-19** (labels are service dates and lag true onset).
Sensor mapping (from the parquet column names): chamber = `RTD`, 1st-stage suction = `1st Suc.`, interstage HX = `H.E.`, evaporator outlet = `Evap. Out`, 2nd-stage sump = `2nd Sump`, compressor on-time from `State` bit 0.

## What the real leak looked like (daily means)
- ~18 Mar 2022: 2nd-stage sump dips from ~32 °C to ~30 °C.
- 25 Mar → 15 Apr: 1st-stage suction climbs steadily from −31 °C to +11 °C while the chamber holds at −79.7 °C.
- Compressor on-time drifts slightly down (23.7 → ~22 min), not up.
- 16 Apr 22:00: chamber hourly mean first above −70 °C (a conventional alarm). Chamber reaches ~−55 °C by 19 Apr.

## Results
| | Model v3 (simulator guesses) | Model v4 (leak shape + noise recalibrated on this freezer) |
|---|---|---|
| First alarm | 17 Apr 2022, 1.7 days before service, **after** the −70 °C alarm | **29 Mar 2022, 20.8 days before service, ~18 days before the −70 °C alarm** |
| Fault named | stage-1 leak (correct) | stage-1 leak (correct) |
| False alarms, 26 fault-free 125-day stretches of the same freezer (2013–2022) | 12 / 26 | 6 / 26 |

**Caveats (important):**
- v4 was recalibrated on this same freezer's leak, so the 20.8-day result is **in-sample**. An independent check needs another leak freezer (e.g. 806274, leak 2017-03-07).
- "Fault-free" stretches only mean no service report; some alarms may reflect real unlogged events (setpoint changes in 2013, defrosts, data gaps). Still, 6/26 is too many for a product.
- One freezer, one fault. This is a first real-data check, not validation.

Real healthy hourly noise measured (Jun 2021–Feb 2022) and now used in the simulator: chamber 0.05 °C, on-time 2.3 min, 1st suction 0.37 °C, HX 0.19 °C, evap out 0.17 °C, 2nd sump 0.66 °C; lag-1 autocorrelation 0.4–0.7.
Reproduce: `python3 analysis/real_freezer_backtest.py --temp 806278_temp.parquet --faults fault_summary.xlsx`.
