# UncertaintyBench

**Measuring frontier LLM reliability under controlled clinical context divergence.**

A benchmark that tests whether large language models maintain calibrated clinical judgment when the deployment context diverges from their training distribution — different drug formularies, different levels of care, different epidemiology.

Built on de-identified admission data from 14 Brazilian federal university hospitals (EBSERH network) via DATASUS.

---

## Why this exists

Clinical LLM benchmarks in current use are built on US or synthetic data. They measure whether a model knows medicine. They do not measure what happens when the model is deployed into a health system whose constraints it was not trained on.

The failure mode that matters in deployment is not missing knowledge. It is **confident output that is locally wrong** — a recommendation that is correct against one guideline and unavailable, unaffordable, or unsafe in the context where it will be acted on.

This benchmark isolates that failure.

---

## Design

### Archetypes

Each archetype is a clinically dense case anchored to a real high-frequency ICD-10 admission/discharge pattern in the source data. It separates:

- **`invariant_clinical_core`** — baseline presentation, vitals, physical exam, workup, care setting. Identical across every variation of that archetype.
- **`manipulable_variables`** — controlled variations, each differing from baseline along **exactly one** dimension.

The single-variable rule is what makes behavioral change attributable to the manipulated variable rather than to case-to-case noise.

All clinical content — presentation and management ground truth — is authored by a licensed emergency physician. See `PROTOCOL.md` §1.4.

### Format

Script Concordance Testing with open-response items:

```
system → emergency physician in the Brazilian public health system (SUS)
Q1     → invariant clinical core + request for initial clinical judgment
         ↓ parametric injection (the variation's `change` field)
Q2     → explicit request to revise or justify not revising
```

### Hypotheses

| | Failure mode |
|---|---|
| **H1** | **Context blindness** — fails to weight contextual variables even when integrated into the prompt |
| **H2** | **Prior override** — resists a declared constraint that conflicts with the training-dominant guideline |
| **H3** | **Absent reasoning spectrum** — produces a single answer without locating itself on the conservative–liberal axis |
| **H4** | **Relational reasoning failure** — cannot integrate simultaneous findings into a higher-order conclusion |

### Scoring dimensions

| | Dimension |
|---|---|
| **D1** | Temporal reasoning |
| **D2** | Urgency calibration |
| **D3** | Local constraints |
| **D4** | Management completeness |
| **D5** | Relational reasoning |

Each scored **pass (2) · partial (1) · fail (0)** against a priori conditions written per archetype. Scoring is performed by licensed physicians, not by models.

---

## Repository structure

```
archetypes/
  cardiovascular/     CARDIO_01..05   (I21, I20, I25, I24, R07)
  neurological/       NEURO_01..05    (I64, G45, I61, I63, G41)
  sepsis_infection/   SEPSIS_01..05   (A41, N39, J18, J15, K65)

scripts/
  build_sct_prompts.py          archetype YAML → SCT prompt JSON
  run_together_sct.py           batch inference, resumable
  validate_together_postrun.py  output integrity checks

sus_bench/
  prompts/    generated SCT prompts
  results/    raw inference output (JSONL)
  scoring/    manual scoring exports

RESULTS.md    pre-pilot findings
PROTOCOL.md   full methodology
```

### Archetype schema

```yaml
archetype_id: "CARDIO_01_I21"
epidemiological_anchor:     # ICD pair, n, mortality %, demographics
invariant_clinical_core:    # presentation, vitals, exam, workup, setting
manipulable_variables:      # hypothesis_tested + controlled variations
rubric_d1_d5:               # pass / partial / fail conditions per dimension
provenance:                 # literature anchors, guidelines, validation date
```

---

## Pre-pilot status

| | |
|---|---|
| Archetypes built | 15 |
| Archetypes evaluated | 10 (cardiovascular + neurological) |
| Models evaluated | 3 (GLM 5.2, DeepSeek V4 Pro, Kimi K2.7 Code) |
| Q1/Q2 pairs collected | 172 (temperature 0) |
| Pairs manually scored | 85 |

Full results and analysis: **[`RESULTS.md`](RESULTS.md)**

---

## Methodological constraints

**Physician-authored ground truth.** No AI system generates archetype clinical content or management ground truth. Parametric variations were drafted with LLM assistance and reviewed and approved by the authoring physician for clinical accuracy; all scoring is human.

**Single-variable manipulation.** A variation may differ from baseline along one controlled dimension only.

**Reporting standard.** Protocol follows TRIPOD-LLM.

---

## Status and roadmap

This is an active research project at pre-pilot stage. Current limitations and the planned design to address them are documented in `RESULTS.md`.

Next: full 15-archetype run across 8 frontier model families, three-reviewer inter-rater validation, and semantic entropy at elevated temperature to separate genuine epistemic uncertainty from hedging theater.

---

## Citation

```
Freitas-Medrado, P. V. (2026). SUS-UncertaintyBench: measuring frontier LLM
reliability under controlled clinical context divergence. Pre-pilot release.
```

**Contact** · pvfhealthtech@gmail.com
