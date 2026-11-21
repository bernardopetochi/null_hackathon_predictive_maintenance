# ULT freezer monitoring: competitor scan (21 Nov 2026, ~20 min desk research)

Legend: **V** = verified on the vendor's own page or a dated news item. **M** = marketing claim, no method or accuracy published. **?** = not checked / not found.

| Vendor / product | What it actually does | Signals | Any brand? | Price | Prediction status |
|---|---|---|---|---|---|
| **PHC (PHCbi)** LabSVIFT, LabAlert | IoT dashboards, real-time alerts, Part 11 reporting ([page](https://www.phchd.com/us/biomedical/lab-equipment-monitoring)) | Not specified on page (?) | Not stated (?) | Quote only | "Predictive analytics" appears only in a July 2026 webinar, no method ([webinar](https://www.phchd.com/us/biomedical/how-predictive-analytics-can-help-lower-the-cost-of-your-ult-freezers)) (M) |
| **Thermo Fisher** Smart Connected Services (TSX) | Human technical experts review data, give "condition-based maintenance recommendations", business hours, US only ([page](https://www.thermofisher.com/ca/en/home/digital-solutions/connected-equipment.html)) | 37 alarm types, 26 parameters: ambient/cabinet temp, power, battery, door, filter (V) ([CAP Today, Dec 2020](https://www.captodayonline.com/thermo-fisher-monitoring-service-for-ult-freezers/?print=pdf)) | **TSX only**, bundled with service plan (V) | In warranty/service plan | Expert review, not a model (V). Separate DeviceLink kit + "InSight Analytics" claims "equipment health assessment" on compatible freezers, no method (M) |
| **Stirling Ultracold** VAULT100 | Onboard "predictive analytics", green/yellow/red, launched Jan 2025 ([PR](https://prnewswire.com/news-releases/stirling-ultracold-advances-signature-technology-with-release-of-new-high-performance-ultra-low-freezer-302353469.html)) | Internal engine data: engine power, piston, heat rejection, thermosiphon ([Lab Manager, sponsored](https://www.labmanager.com/predictive-by-design-staying-ahead-of-ult-freezer-failure-33850)) | **Own Stirling engine only** (V) | Included with freezer | Closest real predictive product, but no accuracy or lead time published (M) |
| **Eppendorf** VisioNize | Cloud alerts: temp limit, door open, mains failure ([page](https://eppendorf.com/pl-pl/lab-academy/lab-solutions/digital-lab-solutions/your-lab/smart-storage-with-the-cryocube-f740hi)) | Temp, door; "sense" add-on probe for non-Eppendorf ([page](https://www.eppendorf.com/us-en/Products/Digital-Lab-Management/Device-Management-Software/VisioNize-sense-p-PF-944965)) | Built-in Eppendorf; probe any brand | ? | None claimed (V) |
| **XiltriX** (independent) | Monitoring + staffed "SafetyNet" call service | Temp, door, **compressor current transducer**, run/rest trending ([page](https://xiltrixusa.squarespace.com/resources/power-consumption-monitoring)) | Retrofit, brands not listed | ? | Heuristic trending + humans; "forecasting" case study is a person reading a temp graph ([page](https://xiltrixusa.squarespace.com/resources/forecasting-failures-through-ult-freezer-monitoring)) (M) |
| **Elemental Machines** (independent, Cambridge MA) | Cloud sensors, "AI-powered" alerts ([2019](https://www.news-medical.net/news/20190403/AI-powered-platform-gives-labs-247-monitoring-and-real-time-data.aspx)) | Temp, light, humidity, compressor cycle stats | Retrofit | ? | Patent [US11561037](https://patents.justia.com/patent/11561037) predicts **defrost timing** from cycling, not failure (V) |
| **Monnit** (independent) | Wireless sensors, threshold alerts, "no monthly subscriptions" ([page](https://www.monnit.com/applications/laboratory-pharmaceutical-monitoring)) | Temp, door, **AC current meter** | Retrofit | ? | Says rising power "can tell you" of impending failure, but alerts are thresholds only (M) |
| **ELPRO** (independent) | GxP loggers, alarms ([page](https://www.elpro.com/en/equipment-monitoring/freezer-monitoring-systems)) | Temp, RH, 4-20 mA | Retrofit | ? | None (V) |

Not checked in this pass: Rees Scientific, SmartSense, Vaisala viewLinc, TandD, Helmer, B Medical. General commercial-refrigeration PdM (Copeland/Emerson, Carrier) exists but targets supermarkets, not lab ULTs.

Others found: NIH says it "is currently researching predictive monitoring systems" and wants to compare each freezer to an average same-age freezer in same conditions ([NIH NEMS](https://nems.nih.gov/sustain/Pages/ULT-Freezer-Predictive-Monitoring.aspx), undated). Lab Design News (Mar 2026, likely) describes clamp-on current-transducer PdM as generic practice but names no vendor ([article](https://www.labdesignnews.com/content/predictive-maintenance-listening-to-freezer-motors)).

## White space (blunt)

- **Hardware is not white space.** Clamp-on current sensing on any brand already exists (XiltriX, Monnit). A sensor pitch alone is me-too.
- **Real failure prediction is OEM-locked.** The only products with genuine predictive features (Stirling, Thermo TSX) work only on their own freezers. Labs run mixed, ageing fleets.
- **Independents alarm and trend, but publish no model, lead time or accuracy.** Prediction is humans reading graphs or fixed thresholds.
- **Nobody publishes how they validate**, and real labelled failure data is tiny (Danish biobank: 42 faults / 53 freezers).
- So the defensible gap is narrow but real: a **brand-agnostic failure-prediction model** (which fault, how many days ahead, with stated accuracy), trained on simulated failures and checked against the real dataset, that runs on signals existing independents already collect. Caveat: this was a 20-minute scan; a stealth startup or an unpublished feature in Rees/SmartSense could exist.

## Who buys or partners

- **Most plausible partners:** independent monitoring vendors that already have current data but no model (XiltriX, Monnit, Elemental Machines). Sell them the model as a software layer.
- **Service orgs** that maintain mixed fleets (third-party freezer service, Thermo Unity Lab Services for non-TSX) as buyers of a "which freezer next" list.
- **Factbird:** factory production monitoring; lab freezers are off its core. A channel at most, unlikely data buyer (unverified that they'd want it).
- Simulated failure data itself is a weak product to sell alone; it's the validated model that has value.

## Q&A lines

1. "Freezer makers like Stirling and Thermo do predict failures, but only on their own freezers. Labs run mixed fleets of 10-year-old units from five brands."
2. "Independent monitors like XiltriX and Monnit already clip on current sensors, but they alarm on thresholds or have a person read the graph. Nobody publishes which fault, how far ahead, or how accurate."
3. "Real failure data is too scarce to train on, so we simulate it and validate against the one open labelled dataset. That's the piece we'd license to monitoring vendors."
