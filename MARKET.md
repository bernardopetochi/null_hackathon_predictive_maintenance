# Market notes (as of 21 Nov 2026)

Short desk research done during a hackathon. Research-firm market sizes vary a lot between firms and are not audited. Treat them as rough context, not facts. We did not find any published figure for spending on lab-freezer *monitoring* or *predictive maintenance* specifically.

## Sourced reference figures (research-firm estimates)

| Market | Figure | Source | What it does and doesn't measure |
|---|---|---|---|
| Ultra-low-temperature (ULT) freezers | USD 813.4 M (2025) → USD 1.5 B (2035) | Global Market Insights (GM Insights) | Sales of the freezers themselves, not monitoring or maintenance spend |
| Predictive maintenance (all industries) | USD 13.89 B (2026) → USD 23.79 B (2031) | MarketsandMarkets | Software and services across industries; lab freezers are a small slice |
| HVAC services | USD 72.5 B (2025) → USD 97.9 B (2030) | MarketsandMarkets | Roadmap context: the same vapor-compression components as freezers |

## Cost of failure (sourced, from `research/next-devices.md`)
- **Vaccine storage:** a CDC study found 318 storage incidents in 8 weeks (Jul–Sep 2009) across 45 US immunisation programs, wasting USD 1.17 M of public vaccine. The authors extrapolate about USD 11.5 M/year for the US.
- **Liquid-nitrogen cryo tanks (IVF):** in 2018 about 3,500 eggs/embryos were lost in San Francisco and more than 4,000 in Ohio (~950 patients). A jury awarded about USD 15 M, with the tank maker found 90% liable.
- **ULT freezers:** a −80 °C freezer can warm to −60 °C in about five hours after failure, and samples start to degrade at −60 °C ([Boston University, 2024](https://www.bu.edu/oehs/files/2024/10/Optimizing-Risk-Management-for-ULT-Freezers.pdf), citing NIH). In the Danish biobank data, a single 54-second door opening pushed the chamber to about −60 °C (Huang et al. 2023). One failure can affect years of irreplaceable samples. The financial value at risk per freezer is not quantified here.

## Team's own bottom-up estimate (illustrative, every input is an assumption)

Business model: license the prediction model as a software layer to independent monitoring vendors, or sell directly to labs. Price it per monitored freezer per year.

| Input | Value used | Status |
|---|---|---|
| ULT freezers installed worldwide (N) | 500,000 – 1,000,000 | **Assumption, no source found.** Needs checking: freezer sales (~USD 0.8 B/yr) ÷ an assumed ~USD 10–15 k unit price gives roughly 55–80 k new units/yr. With a 10–15-year life ([Boston University, 2024](https://www.bu.edu/oehs/files/2024/10/Optimizing-Risk-Management-for-ULT-Freezers.pdf)), that is roughly 0.5–1.2 M installed. |
| Share that is already networked / monitored (m) | 30% – 50% | Assumption |
| Price per freezer per year (p) | USD 100 – 300 | Assumption (software add-on, below the cost of one service visit) |

- **TAM** (all ULT freezers, software price): N × p = 0.5 M × 100 to 1.0 M × 300 → **USD 50 M – 300 M / year**
- **SAM** (already monitored, so the model can run on existing sensor data): TAM × m → **USD 15 M – 150 M / year**
- **SOM** (illustrative early target: 1% of SAM) → **USD 0.15 M – 1.5 M / year**

These are the team's own order-of-magnitude numbers, not research. The biggest unknown is N.

Expansion (from `research/next-devices.md`): vaccine/pharmacy/blood-bank fridges, commercial refrigeration and HVAC all use the same vapor-compression components. That is the route from a niche (lab freezers) to the multi-billion predictive-maintenance and HVAC-services markets above.

## Who pays (from `research/competitors.md`)
- Real failure prediction today exists only from freezer makers, and only on their own units (Stirling Ultracold, Thermo Fisher TSX).
- Independent any-brand monitors (XiltriX, Monnit, Elemental Machines, ELPRO) alarm on thresholds. They are the most plausible licensees for a brand-agnostic model.
