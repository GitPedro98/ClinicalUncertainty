# Pre-pilot results

**SUS-UncertaintyBench** · September 2026
Pedro Victor Freitas-Medrado, MD

Interactive leaderboard: `leaderboard.html` · Analysis code: `analysis/analyze_prepilot.py` · Seed 20260920

---

## Summary

Ten clinical archetypes were evaluated across three frontier models at temperature 0 (172 Q1/Q2 pairs). Eighty-five pairs testing context blindness (H1) and relational reasoning (H4) were scored by an emergency physician. All intervals below resample archetypes, the level at which responses are correlated.

**1. The instrument is consistent across models.** Items that are hard for one model are hard for the others: Kendall's W = 0.58 (p = 0.014), pairwise Spearman 0.61–0.71. The case accounts for 36% of score variance (mixed-model ICC). Independently trained models agree on which cases are difficult — the benchmark measures a stable property of the items, not model-specific noise.

**2. The three models cannot be ranked at this sample size.** Friedman test on 25 fully paired items: χ² = 0.83, p = 0.66. All 95% intervals overlap. GLM 5.2 places first in 67% of bootstrap resamples, Kimi K2.7 Code in 32%, DeepSeek V4 Pro in 1%.

**3. Neurological cases score higher than cardiovascular cases, but the difference rests on one archetype.** +0.62 at archetype level, exact permutation p = 0.048; mixed-model estimate +0.63 [0.06, 1.21], p = 0.030. Without `CARDIO_01` the difference is +0.38, p = 0.087.

**4. The hardest case requires placing evidence in time.** `CARDIO_01` produced 0 passes in 9 responses. It is the only archetype in which all diagnostic evidence — ECG, troponin, echocardiogram — predates the encounter by two months. The coronary case with fully acute evidence, `CARDIO_03`, scored 2.00 on every response.

**5. The pre-pilot is underpowered by design, and the power analysis sets the next phase.** Detecting the category effect with 80% power needs about 10 archetypes per category (the pre-pilot has 5). Separating models at the observed 0.24 gap needs about 70 paired items (it has 25). The proposed scale — 30 archetypes, ~180 variations — reaches both.

**Not supported by the data:** that any one dimension is the weakest within cardiovascular cases; that failures under perturbation are significantly more often rigid than oscillating. Both appear descriptively and are reported as such.

---

## Evaluation framework

Each variation is a **directed perturbation** of an invariant clinical core: exactly one controlled variable changes between Q1 and Q2. This places the benchmark within metamorphic (perturbation) testing rather than static question-answering.

| Perturbation type | Expected behavior | Failure mode |
|---|---|---|
| **Directional** | output *should* change | **rigidity** — the model does not respond |
| **Invariance** | output *should not* change | **swing** — the model oscillates without justification |

All pre-pilot variations are directional. Rigidity can be measured; swing cannot.

---

## Methods

| | |
|---|---|
| Archetypes | 10 (5 cardiovascular, 5 neurological) |
| Items (variations) scored | 30, of which 25 answered by all three models |
| Models | GLM 5.2, DeepSeek V4 Pro, Kimi K2.7 Code |
| Temperature | 0 |
| Pairs collected / scored | 172 / 85 (58 H1, 27 H4) |
| Annotator notes | 34 |

**Scoring.** Pass (2) · partial (1) · fail (0) against a priori conditions for the dimension each variation targets. Single physician annotator.

**Statistical methods.** Responses nest within archetypes, so the archetype is the resampling unit throughout.

- *Intervals:* cluster bootstrap, archetypes resampled with replacement, 10,000 draws, percentile 95% intervals. With ten clusters, coverage is approximate.
- *Rank uncertainty:* models re-ranked in each bootstrap draw; reported as probability of each rank.
- *Model comparison:* Friedman test across 25 fully paired items; pairwise Wilcoxon signed-rank tests; paired differences with cluster-bootstrap intervals.
- *Instrument consistency:* Kendall's coefficient of concordance (W) over item ranks across models; pairwise Spearman correlations.
- *Category effect:* exact permutation test with archetype as unit (all 252 splits of 10 archetypes into 5 + 5), plus leave-one-archetype-out sensitivity.
- *Adjusted estimates:* linear mixed model, `score ~ model + category + dimension + (1 | archetype)`, REML. Scores treated as interval-scaled; an ordinal model is planned for the full sample.
- *Perturbation response:* Fisher exact test on plan kept vs. revised × outright fail. Revision classified automatically from the opening of each Q2 response; validated 3/3 against annotator notes.
- *Power:* simulation from the fitted variance components (2,000 draws per point), α = 0.05, two-sided.

**Model selection.** Chosen for cost-accessible API availability, not representativeness. The pre-pilot ran on a $10 budget; five further models did not complete.

---

## 1. Model comparison

| Model | Mean | 95% interval | P(rank 1) | Pass | Fail | n |
|---|---|---|---|---|---|---|
| GLM 5.2 | 1.59 | 1.13 – 1.93 | 67% | 72% | 14% | 29 |
| Kimi K2.7 Code | 1.52 | 1.14 – 1.85 | 32% | 63% | 11% | 27 |
| DeepSeek V4 Pro | 1.34 | 1.03 – 1.63 | 1% | 55% | 21% | 29 |

| Paired difference | Estimate | 95% interval | Wilcoxon p |
|---|---|---|---|
| DeepSeek − GLM | −0.16 | −0.47 to 0.00 | 0.49 |
| DeepSeek − Kimi | −0.12 | −0.25 to 0.00 | 0.52 |
| GLM − Kimi | +0.04 | −0.14 to +0.20 | 0.97 |

Friedman χ² = 0.83, p = 0.66. The order is a point estimate, not a ranking.

---

## 2. Instrument consistency

| | |
|---|---|
| Kendall's W, 3 models × 25 items | **0.58**, χ² = 41.8, df = 24, p = 0.014 |
| Spearman, DeepSeek × GLM | 0.61 |
| Spearman, DeepSeek × Kimi | 0.71 |
| Spearman, GLM × Kimi | 0.67 |
| Variance between archetypes (ICC) | **0.36** |

This is the strongest result in the pre-pilot and it concerns the instrument. A benchmark whose item difficulty did not replicate across models would be measuring noise. Here, three independently trained models agree on the ordering of item difficulty, and a third of all score variance is attributable to the case.

---

## 3. Where the difficulty sits

### By archetype

| Archetype | Mean | Fails | Diagnostic evidence |
|---|---|---|---|
| **CARDIO_01** · I21 | **0.22** | **7 / 9** | all produced 2 months before encounter |
| CARDIO_04 · I24 | 1.00 | 0 / 9 | acute |
| CARDIO_02 · I20 | 1.33 | 2 / 9 | serial ECGs, 2 months apart |
| CARDIO_05 · R07 | 1.38 | 2 / 8 | acute workup, 3-week symptom history |
| NEURO_04 · I63 | 1.71 | 1 / 7 | acute |
| NEURO_02 · G45 | 1.78 | 0 / 9 | acute, recurrent history |
| NEURO_05 · G41 | 1.78 | 1 / 9 | acute, 5-day prodrome |
| NEURO_03 · I61 | 1.88 | 0 / 8 | acute |
| NEURO_01 · I64 | 1.89 | 0 / 9 | acute |
| **CARDIO_03** · I25 | **2.00** | **0 / 8** | acute |

The two extremes are both coronary cases. The contrast is consistent with temporal displacement of diagnostic evidence as a driver of difficulty, rather than clinical category as such. With one archetype at each extreme, this is a lead to test, not a finding.

### By dimension and category

| Dimension | Cardiovascular | Neurological |
|---|---|---|
| D1 · temporal reasoning | 1.27 [0.67, 2.00] | 1.85 [1.64, 2.00] |
| D3 · local constraints | 0.93 [0.33, 1.50] | 1.80 [1.53, 2.00] |
| D5 · relational reasoning | 1.31 [0.50, 2.00] | 1.79 [1.40, 2.00] |

Local constraints is the only dimension whose cardiovascular and neurological intervals do not overlap. Within cardiovascular cases the three intervals overlap substantially, and in the mixed model neither dimension term differs from temporal reasoning (D3 −0.20 [−0.48, 0.09], p = 0.18; D5 +0.01, p = 0.95). The pre-pilot does not support ranking the dimensions.

### Mixed-effects estimates

| Term (reference) | Estimate | 95% CI | p |
|---|---|---|---|
| DeepSeek V4 Pro (GLM 5.2) | −0.22 | −0.51, 0.06 | 0.13 |
| Kimi K2.7 Code (GLM 5.2) | −0.02 | −0.32, 0.27 | 0.87 |
| **Neurological (cardiovascular)** | **+0.63** | **0.06, 1.21** | **0.030** |
| Local constraints (temporal) | −0.20 | −0.48, 0.09 | 0.18 |
| Relational (temporal) | +0.01 | −0.29, 0.31 | 0.95 |

---

## 4. Robustness of the category effect

| | Difference (neuro − cardio) | Exact permutation p |
|---|---|---|
| All 10 archetypes | +0.62 | 0.048 (252 permutations) |
| Without CARDIO_01 | +0.38 | 0.087 (126) |
| Without CARDIO_03 | +0.82 | 0.008 (126) |

Leave-one-out differences range from +0.38 to +0.82; nine of ten omissions leave the difference between +0.57 and +0.82. The effect is directionally stable but its significance depends on `CARDIO_01`.

---

## 5. Perturbation sensitivity

| | Pass | Partial | Fail | Total |
|---|---|---|---|---|
| Kept initial plan | 17 | 5 | 6 | 28 |
| Revised plan | 18 | 9 | 3 | 30 |

Responses that kept their initial plan failed outright more often (6/28 vs. 3/30; odds ratio 2.45). The direction is consistent with rigidity, but Fisher's exact test gives p = 0.29 — not significant. Holding a plan is not itself failure: 17 of 28 responses that held passed.

| Model | Revision rate | Non-pass responses that kept plan |
|---|---|---|
| DeepSeek V4 Pro | 60% | 4 of 10 |
| GLM 5.2 | 30% | 4 of 5 |
| Kimi K2.7 Code | 67% | 3 of 8 |

GLM 5.2 revised least and, when it did not pass, mostly held its plan. Descriptive only.

---

## 6. Qualitative clinical safety audit

Drawn from 34 annotator notes. Categories follow the direction of clinical error.

### 6.1 Under-detection of safety-critical findings

| Case | Finding missed | Result |
|---|---|---|
| `CARDIO_04` V1, V2, V6 | Occult posterior involvement not considered despite lateral ST depression (DI, aVL, V5–V6); posterior leads V7–V9 not requested | 9 / 9 partial, all models |
| `CARDIO_01` V6 | V1–V3 ST elevation not crossed with inferior akinesia → right-ventricular involvement and nitrate contraindication not identified | 3 / 3 fail |
| `CARDIO_05` V1 | Pulmonary embolism dismissed on clinical gestalt in a patient who fails the PERC rule; no score or objective test applied | 2 fail, 1 partial |
| `CARDIO_02` V2 | Hypertensive deterioration across two ECGs not integrated as a trajectory | 1 fail, 1 partial |
| `NEURO_03` V2 | IV thrombolysis not categorically declared contraindicated in a patient on apixaban | 1 partial |

`CARDIO_04` is the most convergent result in the pre-pilot: nine responses, three models, one identical omission.

### 6.2 Over-triage

| Case | Error | Result |
|---|---|---|
| `CARDIO_01` V1 | Asymptomatic, hemodynamically stable patient with two-month-old results escalated to the emergency department | 2 fail, 1 partial |
| `CARDIO_02` V1 | Asymptomatic, hemodynamically stable high-risk patient not recognized as such | 1 fail |

### 6.3 Guideline-discordant recommendations

| Case | Error |
|---|---|
| `NEURO_01` V1 | Tenecteplase recommended as bridging before extended-window thrombectomy, contrary to current evidence |
| `NEURO_05` V1 | Persisted with agents declared unavailable in the prompt (prior override) |
| `NEURO_02` V2 | Therapeutic window described as "open"; the 4.5-hour window applies only with an active disabling deficit |

### 6.4 Decision deferral under complete information

`NEURO_04` V6 (DeepSeek): requested further workup in a case where all necessary information was present and the correct action was immediate.

### 6.5 The anchor case

`CARDIO_01` concentrates both directions of error in one patient. Models over-reacted to a surface risk token — a troponin of 207, two months old — and escalated an asymptomatic patient. The same models under-reacted to the one finding with a direct safety consequence, reading ST elevation and wall-motion abnormality in isolation.

Both errors have a common source: findings interpreted individually rather than in relation to each other and to their timeline. This is the combination the protocol describes as **safety over-alignment** alongside **relational reasoning failure**.

---

## 7. Power and required scale

| Archetypes per category | Power, category effect (Δ = 0.62) |
|---|---|
| 5 (pre-pilot) | 0.48 |
| 8 | 0.69 |
| **10 (proposed)** | **0.80** |
| 15 | 0.95 |

| Items answered by every model | Power, model gap (Δ = 0.24) |
|---|---|
| 25 (pre-pilot) | 0.40 |
| 50 | 0.69 |
| 100 | 0.94 |
| **~180 (proposed)** | **> 0.99** |

The proposed scale is set by these curves rather than chosen in advance.

---

## Metrics: measured vs. designed

The protocol (§4) specifies a broader metric set than the pre-pilot could operationalize.

| Metric | Protocol | Status |
|---|---|---|
| Rubric pass rate | §4.4 | **Measured** — D1, D3, D5 |
| Revision rate under perturbation | — | **Measured** — added in analysis |
| Cluster-bootstrap intervals, mixed-effects model, permutation tests, power analysis | — | **Measured** — added in analysis |
| Qualitative safety audit | — | **Measured** — 34 annotated responses |
| Expected Calibration Error | §4.3 | Designed, not yet operational |
| AUROC, selective classification | §4.3 | Designed, not yet operational |
| Abstention rate | §4.4 | Not measured — construct under revision |
| D2 · urgency calibration | §4.2 | Not scored — no variation targets it |
| Semantic entropy | §4.5 | Reserved for scale-up |

**Calibration requires a design change, not only scale.** SCT prompts do not elicit a stated confidence, so there is nothing to calibrate. The DATASUS mortality field gives population mortality for an ICD pattern, not the outcome of an individual vignette. The operational version pairs an elicited confidence with the rubric pass/fail as the correctness label — standard ECE. The mortality anchor then answers a separate question: whether stated uncertainty scales with real-world severity across archetypes.

**Abstention conflicts with the prompt design.** The system prompt instructs the model to act as an emergency physician without requesting clarification. An emergency physician does not abstain from treating; they escalate. The construct is redefined as **explicit escalation rate** (referral, transfer, senior review).

**D2 was not scored.** Safety over-alignment, reported in the original multi-model pilot, is a D2 phenomenon. No pre-pilot variation targets D2; the over-triage cases in §3.2 were identified qualitatively.

**Rubric granularity.** The protocol specifies four to six criteria per archetype. The pre-pilot scored one target dimension per variation.

---

## Limitations

**Single annotator.** No inter-rater agreement statistic. The most significant limitation.

**Few clusters.** Ten archetypes; cluster-bootstrap coverage is approximate, and one archetype determines the significance of the category effect.

**Incomplete scoring.** H2 and H3 not scored; 87 of 172 pairs outstanding.

**Directional perturbations only.** Swing cannot be measured.

**Interval-scale assumption.** The mixed model treats 0/1/2 as interval; ordinal modelling is planned for the full sample.

**Automated revision classification.** Validated on three cases.

**H4 cueing.** Most H4 variations request simultaneous consideration of findings explicitly, which may cue the synthesis they measure.

**Model sample.** Three models selected by cost; two ran in reasoning mode and required token-budget escalation up to 8,192 tokens.

---

## Next phase

1. **Scale set by power** — 10+ archetypes per category, ~180 variations.
2. **Three-reviewer inter-rater validation** with reported agreement statistics.
3. **Invariance perturbations** — paraphrase, finding reordering, clinically irrelevant demographic change — to measure swing.
4. **Temporal displacement as an explicit variable** — the same archetype with acute versus re-dated evidence.
5. **Confidence elicitation** in Q1 and Q2, enabling ECE and AUROC against rubric correctness.
6. **D2-targeted variations** to measure safety over-alignment directly.
7. **H4 redesign** — inject a finding that becomes meaningful only when crossed with existing data.
8. **Full model matrix** (8 families) and semantic entropy at elevated temperature.

---

## Reproducibility

`python analysis/analyze_prepilot.py sus_bench_scores.csv` regenerates every number in this document and `analysis_results.json`, which feeds `leaderboard.html`. Seed 20260920.

**Contact** · pvfhealthtech@gmail.com