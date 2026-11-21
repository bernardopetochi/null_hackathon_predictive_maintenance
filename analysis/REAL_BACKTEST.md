# Real-data backtests: Revco freezers 806278 and 806274 (Danish National Biobank)

Data: `806278_temp.parquet` (1-min, 2013-01 → 2023-04) from the dataset of Huang et al., Scientific Data 2023 (not redistributed here). Fault label: refrigerant leakage at stage 1, service registered **2022-04-19** (labels are service dates and lag true onset).
Sensor mapping (from the parquet column names): chamber = `RTD`, 1st-stage suction = `1st Suc.`, interstage HX = `H.E.`, evaporator outlet = `Evap. Out`, 2nd-stage sump = `2nd Sump`, compressor on-time from `State` bit 0.

## Running tally: v4 model, unchanged, on real Revco freezers
"Early" means the model alarmed before the chamber first went above −70 °C (a conventional alarm). Fault labels are service dates, which can lag the real failure by weeks.

| Freezer | Label | Model alarm vs −70 °C alarm | Early warning? | Fault named | False alarms (fault-free 125-day stretches) | Note |
|---|---|---|---|---|---|---|
| 806278 | stage-1 leak, 2022-04-19 | ~18 days before | yes | correct | 6/26 | **in-sample** (v4 calibrated on it) |
| 806274 | stage-1 leak, 2017-03-07 | 2 h after | no | correct | 9/27 | out-of-sample |
| 806019 | none (healthy, 2012–2023) | – | – | – | **16/32** (≥16 false alarms in ~11 years, ≈1.5 per freezer-year) | out-of-sample healthy |
<!-- TALLY-END -->

**Out-of-sample so far: 0 of 1 leak freezers warned early; on a real healthy freezer, 16 of 32 fault-free 125-day stretches had a false alarm.** Including in-sample: 1 of 2 leaks. The simulator's 0.4% false-alarm rate does **not** carry over to real freezers: the threshold was set on simulated healthy freezers, and real healthy behaviour (defrosts, setpoint changes, maintenance, slow drifts) is far noisier than our simulation. Setting the threshold on real healthy freezers is the next fix.

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

---

## Out-of-sample test: Revco freezer 806274 (stage-1 leak, service registered 2017-03-07)
The v4 model was run **exactly as calibrated on 806278, with no changes**.

What happened in the data (daily means):
- From ~16 Jan 2017, 1st-stage suction climbs steadily from about −30 °C to −8 °C (2 Feb), then +9 °C (5 Feb). The chamber holds at −79.9 °C and on-time drifts slightly down. This is the same signature as 806278, but slower and spread over three weeks.
- 6 Feb 2017 09:00: chamber hourly mean first above −70 °C. The freezer then failed, with data missing or warm until early March. **The real failure was about 29 days before the service date**, so "days before service" is misleading here, and we compare against the −70 °C alarm instead.

| | Model v4, out-of-sample |
|---|---|
| First alarm | 6 Feb 2017 11:00, **2 hours after** the −70 °C alarm, so **no early warning** |
| Fault named | stage-1 leak (correct) |
| p(healthy) trend | dipped from 0.999 to 0.88–0.95 from 23 Jan and to 0.58–0.65 on 3–4 Feb, but stayed above the 0.5 threshold until 5 Feb. The 6-consecutive-check rule then added about a day. |
| False alarms, 27 fault-free 125-day stretches | 9 / 27 |

Check on the protocol: the default baseline window (starting 45 days before the service date) began on 21 Jan, after the leak had started. Moving the baseline to start 60–120 days before gave the **same** alarm time, so the miss is not caused by a contaminated baseline. This check was done after seeing the result.

**Conclusion:** recalibrating on one leak (806278) did not carry over to a second, slower leak. The model saw the trend, but its threshold is tuned to the faster 806278 shape. Honest current status on real data: **1 early warning out of 2 leaks, and the one that worked is in-sample**. False alarms of 6–9 per ~26 fault-free stretches are too high. The next step is to train on several real leak shapes (variable onset speed) and calibrate the threshold on real healthy freezers, not only simulated ones.

Reproduce: `python3 analysis/real_freezer_backtest.py --temp 806274_temp.parquet --faults fault_summary.xlsx`.
