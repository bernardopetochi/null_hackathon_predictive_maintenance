# Next devices for the simulate-then-predict approach (as of 2026-11-21)

Ranked for: cost of failure, open data available, closeness to the -80 freezer model.

| # | Device | Why it matters (sourced) | Open data | Similarity to -80 freezer |
|---|---|---|---|---|
| 1 | Vaccine / pharmacy / blood-bank fridges | CDC study: 318 storage incidents in 8 weeks (Jul-Sep 2009) across 45 US immunisation programs wasted $1.17M of public vaccine; authors extrapolate ~$11.5M/yr US. Most waste in combination fridge/freezer units. [CDC poster](https://cdc.confex.com/recording/cdc/nic2010/pdf/free/4db77adf5df9fff0d3caf5cafe28f496/paper22506_1.pdf) | Synthetic only: 27 simulated fridges, 1-min, 6 degradation types, Zenodo 10.5281/zenodo.22076228 ([arXiv 2609.22229](https://arxiv.org/pdf/2609.22229)). No real fault set found. | Very high: same vapor-compression cycle, warmer setpoint. |
| 2 | Liquid nitrogen cryo tanks (IVF, biobanks) | 2018: ~3,500 eggs/embryos lost in San Francisco; >4,000 in Ohio (~950 patients), where the tank alarm had been turned off. Jury awarded ~$15M; tank maker Chart 90% liable for a defective LN2-level controller. [NBC](https://www.nbcnews.com/news/us-news/15m-awarded-five-people-who-lost-eggs-embryos-fertility-clinic-n1270439), [Moutos et al. 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6603075) | None found. | Low on hardware (no compressor; vacuum jacket, LN2 level sensor, controller). Physics is simple to simulate (boil-off rises as vacuum degrades). |
| 3 | Supermarket / commercial refrigeration | (cost not verified in this pass) | Real lab rig: ORNL transcritical CO2 system, 6 faults (door open, coil icing, expansion valve, fan motor, condenser and evaporator blockage), 1-3 s sampling, figshare, CC BY 4.0. [Sci Data 2021](https://www.nature.com/articles/s41597-021-00927-6) | High: same components (compressor, valves, fans, coils). |
| 4 | HVAC: AHU, rooftop units, chillers | (cost not verified in this pass) | LBNL FDD datasets: RTU, AHU, VAV, fan coil, chiller, boiler; mostly simulated, RTU/AHU partly lab and field. [LBNL](https://faultdetection.lbl.gov/data) | Medium-high (chillers, RTUs share vapor compression). |
| 5 | CO2 incubators | CO2 sensor drift and contamination are the known issues; no cost figure verified. [Lab Manager](https://www.labmanager.com/co2-incubators-how-to-control-culture-conditions-prevent-contamination-and-maximize-cell-viability-35263) | None found. | Low (heater, gas sensor, humidity; no refrigeration). |

Considered, not ranked: MRI cold heads/compressors (high downtime cost, figures not verified); centrifuges (no device-specific dataset found).

Notes
- "None found" means a short search found nothing, not proof none exists.
- Prior art: the Sherbrooke synthetic fridge dataset (Sept 2026) already does simulated fridge degradation. Our angle has to be calibration against real fault data (Danish biobank, ORNL rig), not simulation alone.
