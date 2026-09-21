# Pre-pilot results

**SUS-UncertaintyBench** · September 2026
Pedro Victor Freitas-Medrado, MD

---

## Summary

Ten clinical archetypes were evaluated across three frontier models at temperature 0, producing 172 Q1/Q2 pairs. Eighty-five pairs have been manually scored by an emergency physician against a priori rubric conditions.

**Primary finding.** Adherence to explicitly declared local constraints in cardiovascular cases is the weakest measured cell — 27% pass rate, mean score 0.93 of 2.00. Models degrade when the deployment context diverges from the training distribution, even when the constraint is stated verbatim in the prompt.

**Secondary finding.** Clinical category accounts for more variance than failure dimension. Within neurological cases all three scored dimensions cluster near 1.8; within cardiovascular cases all fall. The pattern replicates across all three models, which argues against model-specific noise.

---

## Methods

### Sample

| | |
|---|---|
| Archetypes | 10 (5 cardiovascular, 5 neurological) |
| Variations per archetype | 6 |
| Models | GLM 5.2, DeepSeek V4 Pro, Kimi K2.7 Code |
| Temperature | 0 |
| Pairs collected | 172 |
| Pairs scored | 85 (58 H1, 27 H4) |

H2 and H3 scoring is in progress and not reported here.

### Scoring

Each response pair was scored **pass (2) · partial (1) · fail (0)** against the pass/partial/fail conditions written a priori for the dimension that the variation targets. Scoring was performed by a single emergency physician. Inter-rater validation has not yet been performed — see Limitations.

### Note on model selection

The three evaluated models were selected for cost-accessible API availability, not as a representative sample of the frontier. The pre-pilot was run unfunded on a $10 API budget; five additional models failed to complete (credit exhaustion, and one requiring streaming not implemented in the runner at the time).

---

## Results

### By dimension and clinical category

Mean score, 0–2 scale.

| Dimension | Cardiovascular | Neurological |
|---|---|---|
| **D1** · temporal reasoning | **1.27** (47% pass, n=15) | 1.85 (85% pass, n=13) |
| **D3** · local constraints | **0.93** (27% pass, n=15) | 1.80 (87% pass, n=15) |
| **D5** · relational reasoning | **1.31** (54% pass, n=13) | 1.79 (86% pass, n=14) |

### By model and category

| Model | Cardiovascular | Neurological | Overall |
|---|---|---|---|
| DeepSeek V4 Pro | 1.07 (n=14) | 1.60 (n=15) | 1.34 |
| GLM 5.2 | 1.21 (n=14) | 1.93 (n=15) | 1.59 |
| Kimi K2.7 Code | 1.20 (n=15) | 1.92 (n=12) | 1.52 |

The cardiovascular–neurological gap is present in every model.

### D3 cardiovascular — the weakest cell

| Model | n | pass | partial | fail | mean |
|---|---|---|---|---|---|
| DeepSeek V4 Pro | 5 | 1 | 3 | 1 | 1.00 |
| GLM 5.2 | 5 | 2 | 1 | 2 | 1.00 |
| Kimi K2.7 Code | 5 | 1 | 2 | 2 | 0.80 |

Tight convergence across three independently trained models.

### Aggregate by hypothesis

| Hypothesis | n | pass | partial | fail | mean |
|---|---|---|---|---|---|
| H1 · context blindness | 58 | 35 (60%) | 14 | 9 | 1.45 |
| H4 · relational reasoning | 27 | 19 (70%) | 4 | 4 | 1.56 |

These aggregates should be read with caution. H1 variations span two distinct dimensions (D1 and D3) and both clinical categories; H4 variations span one dimension. The disaggregated table above is the more informative view.

---

## Interpretation

### The local-constraint failure is real and convergent

D3 tests whether a model adapts its plan to a resource, formulary, or protocol constraint stated explicitly in the prompt — for example, that a given anticoagulant is unavailable at the declared level of care, or that local protocol diverges from the training-dominant guideline.

In cardiovascular cases, all three models cluster between 0.80 and 1.00. The convergence across independently trained architectures suggests this is a property of how these models weight declared context against internalized guideline priors, rather than an artifact of one training pipeline.

This is the founding premise of the benchmark, and it is the finding with the strongest support in the pre-pilot.

### The category effect was not anticipated

The original design treated dimension as the primary axis of variation. The data indicate that clinical category is a larger source of variance. Within neurology, D1, D3 and D5 are effectively indistinguishable (1.85 / 1.80 / 1.79). Within cardiology they separate, and all sit lower.

Two explanations are consistent with the data and cannot be distinguished at current sample size:

1. **Case difficulty.** Cardiovascular archetypes may impose genuinely harder synthesis. Several encode findings distributed across time (serial ECGs, results from prior encounters), whereas neurological archetypes are predominantly acute single-timepoint presentations.

2. **Rubric calibration.** The neurological rubric conditions may have been authored more permissively than the cardiovascular ones. Rubrics were written per archetype rather than against a fixed cross-archetype calibration standard.

Distinguishing these requires more archetypes per category authored under a fixed rubric protocol. This is the first methodological priority for the next phase.

### On H4

The pre-pilot does not support the initial expectation that relational reasoning would be the dominant failure mode across the board. H4 performed comparably to or better than H1 in aggregate.

However, qualitative review of individual responses shows genuine relational failures where the required synthesis is counter-intuitive rather than merely additive. In `CARDIO_01_V6`, no model crossed ST-elevation in V1–V3 with inferior-wall akinesia to raise right-ventricular involvement and the resulting nitrate contraindication. In archetypes where the synthesis is a sequential chain over already-salient findings, models performed well.

A design concern also applies: most H4 variations request that findings be considered "simultaneously," which may cue the synthesis the variation intends to measure. Several models opened their Q2 response by noting that no new information had been introduced. Whether H4 failure is rare or simply under-elicited by the current variation design is an open question, and the H4 protocol requires redesign before the finding can be interpreted.

---

## Limitations

**Single annotator.** All scoring performed by one physician. No inter-rater agreement statistic is available. This is the most significant limitation and the highest priority to address.

**Sample size.** n = 13–15 per dimension-by-category cell. Sufficient to observe a convergent pattern, insufficient to separate case difficulty from rubric calibration.

**Incomplete scoring.** H2 and H3 not yet scored; 87 of 172 collected pairs remain unscored.

**Model sample.** Three models, selected by API cost accessibility rather than representativeness. Two of the three are reasoning-mode models, which required adaptive token-budget escalation (up to 8,192 tokens) to produce non-empty completions.

**Variation design.** H4 variations may cue the synthesis they measure, as described above.

**No outcome calibration yet.** The DATASUS mortality field is available per archetype as an epidemiological anchor but was not used in this pre-pilot for ECE or AUROC calibration. That analysis requires the full model matrix.

---

## Next phase

1. Fixed rubric-authoring protocol applied across all categories, to remove the calibration confound.
2. H4 variation redesign — inject a finding that only becomes meaningful when crossed with existing data, rather than requesting synthesis explicitly.
3. Scale to 30+ archetypes with balanced category representation.
4. Three-reviewer inter-rater validation with reported agreement statistics.
5. Full matrix across 8 frontier model families.
6. Semantic entropy at elevated temperature, to separate genuine epistemic uncertainty from hedging theater.
7. Calibration analysis (ECE, AUROC under selective classification) against the DATASUS mortality anchor.

---

## Data availability

Archetype definitions, generated SCT prompts, raw inference output and scoring exports are in this repository. Source DATASUS extraction is from public de-identified data.

**Contact** · pvfhealthtech@gmail.com
