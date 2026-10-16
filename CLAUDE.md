# Fair Weather or Foul for the Philippines? — project brief

**Status: Phase 1 (research), draft of 2026-10-16. The reference paper is proposed and waiting for the user's approval. No data downloaded, no estimates run.**

This study asks what happens to the Philippine economy during an El Niño, and what the 2026–27 super El Niño is likely to do to output, inflation, interest rates and the peso. It replicates the Global Vector Autoregression (GVAR) design of Cashin, Mohaddes and Raissi (2017, *Journal of International Economics* 106: 37–54; working paper IMF WP/15/89), which estimates how an El Niño shock moves real GDP, inflation, interest rates, the exchange rate and world commodity prices in 33 economies, the Philippines among them. The study then extends that design with Philippine data to 2026, adds the sector, regional and policy detail the reference paper lacks, and turns the estimates into a dated, pre-registered scenario for 2026–27 with policy implications for the Bangko Sentral ng Pilipinas (BSP) and the national government.

## Why this reference paper

- It asks the user's exact question at the macroeconomic level: GDP, inflation, the short- and long-term interest rate, real equity prices, the real exchange rate, and oil and non-fuel commodity prices.
- The Philippines is one of its 21 country models (Table 1), so it publishes Philippine numbers to replicate (`replication/cmr2017_targets.csv`).
- Its data are public: the GVAR database, now updated to 1979Q2–2023Q3 (Mohaddes and Raissi 2024; Mendeley DOI 10.17632/kfp5fhgkvf.1).
- Its identification is clean. The Southern Oscillation Index (SOI) enters every country model as weakly exogenous, which means the Philippine economy cannot move El Niño but El Niño can move the economy.
- Its Philippine result is an open puzzle worth testing. The cumulative GDP response after four quarters is +0.21% and not significant, and the authors credit early-warning systems (WP p. 18). Inflation rises by 0.27 percentage points after four quarters (Table 7). The sample ends in 2013Q1, before the strong 2015–16 and 2023–24 events, the Rice Tariffication Law (RA 11203, 2019) and the 2024 rice-tariff cut.
- Its own conclusion names the policy questions this study can answer for the Philippines: tighten only if second-round effects emerge, release food stocks wisely, adjust import policy, invest in irrigation, and set inflation-target bands with El Niño in mind.

Companion references:

- Armas, Asi, Mandap and Moral (2024, BSP Discussion Paper 2024-02) estimate regional-panel local projections on Philippine data, with temperature as the shock and El Niño as a control. Their design is the model for the regional and sectoral extension.
- Callahan and Mankin (2023, *Science* 380: 1064–1069) find that El Niño lowers growth persistently, for years. Their result is the benchmark for testing whether Philippine losses fade or persist.

## Conventions

- `data/raw/` holds untouched downloads only; every file gets an entry in `data/raw/source_log.md` (URL, date pulled, base year, coverage).
- `data/processed/` and `output/` are written by scripts, never by hand.
- `replication/cmr2017_targets.csv` holds the reference paper's coefficients.
- No new-data estimate is reported until the replication gate passes.
- Every specification choice goes in the decisions log below, with the evidence, labelled pre-registered / supplementary / exploratory.
- Documents are rendered from templates; never edit rendered .md/.docx by hand.
- User style: as simple as possible, define every term on first use (words → formula → example), paragraphs over bullets/tables.
- Policy facts (laws, dates, official forecasts) go in `paper/policy_context.md` with a source URL.

## Reference specification (read from IMF WP/15/89; to be checked against the JIE 2017 version)

- **Model.** A GVAR made of 21 country or region VARX\*(p_i, q_i) models. Each links a country's own variables to trade-weighted foreign averages of the same variables and to the global variables. The models are solved together, so a shock in one country spills over to its trade partners. There is a separate commodity block (real oil price and real IMF non-fuel commodity price, endogenous), and the SOI anomaly enters as a dominant, weakly exogenous variable with a univariate AR(1).
- **Domestic variables (non-US models).** These are log real GDP y, inflation π, log real equity prices eq, the short-term rate r^S, the long-term rate r^L and the log real exchange rate ep, depending on availability. The Philippine model has no equity series or long rate in many GVAR vintages, which needs checking.
- **Philippine lag orders.** p = 2 and q = 1, with 2 cointegrating relations (Table 2). Lags were chosen by the Akaike information criterion (AIC) with a maximum of 2.
- **Shock.** A negative one-standard-error shock to SOI anomalies; a falling SOI signals El Niño. In the paper's notation the anomaly is SOI minus its historical mean, and sustained values below −1 indicate El Niño.
- **Sample.** Quarterly, 1979Q2–2013Q1.
- **Reported output.** Median impulse responses at impact and cumulated after 1–4 quarters, in percent. Significance comes from bootstrapped 5–95% (\*\*) and 16–84% (\*) bands.
- **Open.** Exact bootstrap settings; whether the JIE version changed the sample or numbers; whether the Philippine model includes eq and r^L.

## Draft research questions and hypotheses (Phase 1, not yet pre-registered)

**Main question.** How does an El Niño shock move the Philippine economy, and what should policy expect and do in the 2026–27 super El Niño?

- **RQ1, replication and update.** How do real GDP, inflation, the policy rate and the real exchange rate respond to an El Niño shock? This is done first on the reference sample, then extended to 2026.
  - H1a, the reference finding: no significant national growth effect, because agriculture is a small share of GDP (about 14% in 2004–13, lower now) and because of early warning and adaptation.
  - H1b, the alternative: a significant growth loss that the 1979–2013 sample could not detect. It would show up once the 2015–16 and 2023–24 events are added, and in agriculture value added.
- **RQ2, channels.** Which sectors and prices carry the shock? The candidates are agriculture and fisheries value added, food, rice and electricity inflation, and rice imports. This uses regional-panel local projections in the style of Armas et al. (2024).
- **RQ3, size nonlinearity.** Is the response to strong events more than proportional? This matters most for a "super" event. The test is state-dependent local projections (Ramey and Zubairy 2018).
- **RQ4, second-round effects.** Does El Niño inflation spread to core inflation and to inflation expectations?
  - H4a: no spread, so the BSP can "look through" the shock.
  - H4b: it spreads, so tightening is justified. This is the reference paper's own condition for tightening.
- **Policy objective.** Scale the estimated responses to the NOAA and PAGASA forecast path for 2026–27, publish the projected GDP and inflation paths with bands before the peak, and compare them later with outturns. The projections are also compared with BSP's own forecasts and with market scenarios.

**Three objectives.**

- **Objective 1, descriptive:** the 1982–83, 1997–98, 2015–16 and 2023–24 episodes.
- **Objective 2, estimation:** RQ1 to RQ4.
- **Objective 3, policy:** the 2026–27 scenario and what it implies for the policy rate, rice imports and tariffs, buffer stocks and irrigation.

## Decisions log

| # | Date | Decision | Evidence / reason |
| --- | --- | --- | --- |
| D1 | 2026-10-16 | Proposed reference paper: Cashin, Mohaddes and Raissi (2017). **Awaiting user approval.** | Macro scope matches the RQ; the Philippines is in the sample with published coefficients; public GVAR data; exogenous shock. Alternatives considered: Callahan and Mankin (2023), which is annual growth only with no inflation or policy block; Armas et al. (2024), which uses a temperature shock and is a discussion paper; Smith and Ubilava (2017), a cross-country panel without Philippine-specific results. |

## Replication gate (to be pre-registered before any estimate)

- **G1:** reproduce the Philippine cumulative GDP and inflation responses (Tables 3 and 7) on the GVAR data, 1979Q2–2013Q1. The pass band is to be fixed after reading the JIE tables and bootstrap settings.
- **G2:** reproduce the sign pattern of the cross-checks: Indonesia GDP negative and significant, Thailand GDP positive, oil and non-fuel prices rising.
- **G3:** decide whether a full 33-country GVAR is needed. A Philippine VARX\* with foreign variables treated as given is a cheaper approximation.

## Open questions

- [ ] User approval of D1.
- [ ] Obtain the JIE 2017 version (tables may differ from WP/15/89).
- [ ] Download the GVAR database (1979Q2–2023Q3) and check the Philippine variable list.
- [ ] El Niño measure for the extension: SOI (as in the reference) or the Oceanic Niño Index (ONI) / relative ONI that NOAA now uses. Plan: SOI for replication; ONI as a robustness check.
- [ ] Software: implement the GVAR in Python, or use the GVAR Toolbox (MATLAB) for the gate.
- [ ] The pre-registered 2026–27 scenario must be frozen before the December 2026 to March 2027 drought peak.
