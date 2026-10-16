# Fair Weather or Foul for the Philippines? — project brief

**Status (2026-10-16): Phases 1–2 done. Phase 3 replication gate run: FAIL (Philippine-only approximation misses the global-demand/oil channel). Waiting for the user's decision on the full GVAR. No estimates on new data.**

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
| D1 | 2026-10-16 | Reference paper: Cashin, Mohaddes and Raissi (2017, JIE; IMF WP/15/89). **Approved by the user** ("Philippine model only first"). Pre-registered. | Macro scope matches the RQ; the Philippines is in the sample with published coefficients; public data; exogenous shock. Alternatives considered: Callahan and Mankin (2023), Armas et al. (2024), Smith and Ubilava (2017). |
| D2 | 2026-10-16 | **Philippine-only model**, not the 33-country GVAR (user's instruction). The rest of the world is a *foreign block*: the Philippines' trade-weighted foreign variables plus world oil and non-fuel prices, modelled as a VARX that responds to El Niño but not to Philippine shocks (block exogeneity). Pre-registered. | The Philippines is a small open economy, so its feedback on the world is negligible. In the full GVAR, x\* responds to El Niño through other countries' models; here a reduced-form foreign block carries that response. This is an approximation and the gate tests it. |
| D3 | 2026-10-16 | Data: **GVAR 2013 Vintage** (1979Q1–2013Q1) for the replication, the vintage CMR used; **2023 Vintage** (Mohaddes and Raissi 2024) for the update. Pre-registered. | CMR p. 15 cite the GVAR website and Smith and Galesi (2014); the 2013 Vintage is the one shipped with GVAR Toolbox 2.0. |
| D4 | 2026-10-16 | Transformations as in the GVAR Toolbox: y = ln RGDP; Dp = Δln CPI (quarterly); eq = ln(EQ/CPI); ep = ln(E) − ln(CPI); r = 0.25 ln(1+R/100). The Philippines has no long rate, so 5 domestic variables. Pre-registered. | Rebuilt series are **identical** to the 2023 Vintage's own Philippine series over 1979Q3–2013Q1 (correlation 1.0000, mean abs. diff. 0; `output/tables/data_checks.csv`). |
| D5 | 2026-10-16 | Non-fuel commodity price = **World Bank Pink Sheet non-energy index** (quarterly mean) deflated by the US CPI; real oil = GVAR Brent (USD) / US CPI. Both enter the home model as weakly exogenous global variables. Pre-registered. | CMR use the IMF non-fuel index, which in the current IMF release starts only in 1992. Over 1992Q2–2013Q1 the quarterly log changes of the two correlate at **0.92** (0.91 to 2026). CMR's text does not state how commodity prices enter country models; weak exogeneity is the GVAR convention for global variables. |
| D6 | 2026-10-16 | Foreign variables: trade weights averaged over 2009–2011 (CMR eq. 3), 20 partner units with one Europe region of 13 countries aggregated by 2009–2011 PPP-GDP weights (CMR p. 13). Where a partner lacks a variable, weights are renormalised over partners that have it. Coverage of the Philippines' trade: y\*, Dp\* 100%; r\* 97%; eq\* 80%; lr\* 55%. Pre-registered. | Largest Philippine partners: Japan 0.175, USA 0.157, China 0.130, Singapore 0.122, Europe 0.119 (`output/tables/trade_weights_2013v.json`). Rebuilt Δy\*, Dp\*, Δeq\*, Δr\*, Δlr\* correlate 0.985–0.999 with the 2023 Vintage's own star series, which use other weights. |
| D7 | 2026-10-16 | El Niño measure: NOAA CPC SOI ("anomaly" block), quarterly mean of monthly values; AR(1) marginal model; shock = **−1 standard error** of the AR(1) residual. Pre-registered. | CMR pp. 7, 16–17. The IRF is invariant to rescaling the SOI, so the anomaly and standardised blocks (correlation 0.9998) give the same result. SOI and ONI correlate at −0.84 (1979–2023). |
| D8 | 2026-10-16 | Home block: **VECMX\*(2,1) with r = 2** cointegrating relations, unrestricted intercept and restricted trend (case IV), estimated by reduced-rank regression; this is CMR Table 2 for the Philippines. Secondary: unrestricted levels VARX\*(2,1) with trend. Foreign block: levels VARX(p_f) with trend and SOI_t, SOI_{t−1}; p_f chosen by AIC with maximum 2 (CMR's rule). Pre-registered. | Simulation tests (`tests/test_varx.py`) show the estimator recovers known IRFs and the long-run matrix, and that the full-rank VECM equals the levels VARX. |
| D9 | 2026-10-16 | Reported statistics: **bootstrap median** IRF from 1,000 recursive residual-bootstrap replications (all blocks re-estimated each time), with 5–95% and 16–84% bands, as in CMR. GDP: response of 100·y at quarter h (= cumulated growth, Table 3). Inflation: response of 100·Dp at quarter h (primary reading of Table 7; the GVAR Toolbox reports Dp itself, and CMR's text speaks of inflation "in the fourth quarter"); the running sum is reported as secondary. Pre-registered. | Table 7's label "cumulated" is ambiguous for inflation. The primary reading is fixed now, before results. |
| D10 | 2026-10-16 | Estimation window: data 1979Q2–2013Q1 (Dp starts 1979Q2); first usable observation after two lags is 1979Q4. Pre-registered. | CMR p. 15. |
| D11 | 2026-10-16 | Targets file corrected: significance stars re-read from the rendered PDF tables (text extraction had dropped them) and all horizons recorded for the Philippines, Indonesia, Thailand and commodity prices. **Logged after the gate was run.** G3a was written on the wrong belief that Indonesia's h = 4 GDP effect is significant; it is not. The gate verdict does not change, because G2b and G4 fail regardless. Labelled supplementary. | Rendered WP/15/89 pp. 17, 22, 24. |

## Replication gate (pre-registered 2026-10-16, before any estimate on real data)

Targets: `replication/cmr2017_targets.csv` (IMF WP/15/89 Tables 3, 6, 7). Model and data: D2–D10. Script: `scripts/04_replicate.py` → `output/tables/replication_gate.csv`.

- **G1, Philippine GDP (Table 3; target +0.21 at h = 4, not significant).** (a) The 16–84% band contains zero at every h = 0…4; and (b) the bootstrap median at h = 4 lies in [−0.29, 0.71] (target ± 0.5).
- **G2, Philippine inflation (Table 7; target +0.27 at h = 4, +0.11 on impact).** (a) The median at h = 0 is positive; and (b) the median at h = 4 lies in [0.02, 0.52] (target ± 0.25 pp).
- **G3, method cross-check on Indonesia (same code; VECMX\*(2,1), r = 3 per Table 2; Indonesia has no equity series).** (a) The GDP median at h = 4 is negative and its 16–84% band excludes zero (target −1.01, significant); and (b) the inflation median at h = 4 is positive (target +0.91).
- **G4, commodity prices in the Philippine system (Table 6).** The medians of real oil and real non-fuel prices at h = 4 are both positive (targets +13.87% and +5.31%).

**Pass rule.** The gate passes only if G1–G4 all pass. If any fails, stop: re-read the specification, fix the code, and say what changed. No pass range may be loosened after seeing results.

**Indicative only (not part of the gate):** Thailand (VECMX\*(1,1), r = 1), whose GDP median at h = 4 should be positive (target +1.81); and the levels VARX\* version of every check.

**Result (run 2026-10-16, `scripts/04_replicate.py`, 1,000 bootstrap replications): FAIL.** G1a, G1b, G2a and G3b pass; G2b, G3a and G4 fail (`output/tables/replication_gate.csv`; every target cell against the estimate in `output/tables/replication_comparison.csv`).

- G1 (GDP) passes. The Philippine GDP response is small and insignificant at every horizon (median +0.04 at h = 4, 16–84% band [−0.11, 0.19]), as in CMR.
- G2b fails. Philippine inflation at h = 4 is +0.01 pp (target +0.27).
- G3a fails as written, but the criterion rests on a transcription error (D11). The rendered Table 3 shows Indonesia's h = 4 effect (−1.01) is *not* significant. Our Indonesia GDP path has the right sign and shape: −0.54 on impact (CMR −0.35\*\*), then −0.33, −0.48, −0.29, −0.14.
- G4 fails, and this is the substantive gap. Oil rises 1.8% on impact but turns negative by h = 2 (−1.50% at h = 4; CMR +13.87%\*\*). Non-fuel prices rise but much less (+0.91% against +5.31%\*\*). The world-output response in the foreign block is almost zero (+0.06% at h = 4). CMR attribute their oil rise to El Niño *raising* growth in the US, Europe and China (+0.55, +0.69, +0.56 at h = 4), which then lifts world oil demand (WP p. 22). A reduced-form foreign block built from the Philippines' trade-weighted aggregates does not reproduce that global-demand channel.

**Diagnosis (after re-reading the specification).** The simulation tests pass, so this is not a coding error. The failure comes from the D2 approximation. Our responses are consistently smaller and less persistent than CMR's wherever world dynamics matter: oil, non-fuel prices, Thai GDP (+0.19 against +1.81\*\*), and Philippine inflation, which CMR say is driven by commodity prices. The full 33-country GVAR is the remedy. The decision is the user's (open question 1).

**Post-hoc observation (exploratory, not applied to the gate).** In Table 7, the inflation paths of most countries rise steadily and level off (Korea 0.01 → 0.44, Thailand 0.01 → 0.55, New Zealand −0.06 → −0.61). That shape fits a *running sum* of quarterly inflation responses better than the quarter-by-quarter reading pre-registered in D9. Under the running-sum reading, Philippine inflation at h = 4 is +0.08 pp (inside the G2b range), but G4 still fails, so the gate would still fail. Any later use of the running-sum reading must be labelled conditional on this post-hoc change.

## Open questions

- [ ] **User decision: build the full 33-country GVAR** (CMR's own design, all 21 country VECMX\* models plus the commodity block, solved jointly) to restore the global-demand and oil channel, or keep the Philippine-only model as a documented simplification without claiming to replicate CMR.
- [ ] Obtain the JIE 2017 version (tables may differ from WP/15/89).
- [ ] El Niño measure for the extension: SOI (as in the reference) or the Oceanic Niño Index (ONI) / relative ONI that NOAA now uses. Plan: SOI for replication; ONI as a robustness check.
- [ ] After the gate: the full 33-country GVAR remains an option if the Philippine-only approximation fails or a referee asks.
- [ ] The pre-registered 2026–27 scenario must be frozen before the December 2026 to March 2027 drought peak.
