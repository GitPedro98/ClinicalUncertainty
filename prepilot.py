#!/usr/bin/env python3
import json, re, itertools, sys
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

SEED, B = 20260920, 10_000
rng = np.random.default_rng(SEED)
SCORES = sys.argv[1] if len(sys.argv) > 1 else "sus_bench_scores.csv"
JSONL = "together_prepilot_together_8models_20260720_v2__{}.jsonl"
MODELS = ["deepseek_v4_pro", "glm_5_2", "kimi_k2_7_code"]
LABEL = {"deepseek_v4_pro": "DeepSeek V4 Pro", "glm_5_2": "GLM 5.2", "kimi_k2_7_code": "Kimi K2.7 Code"}

df = pd.read_csv(SCORES)
df = df[df.score_value.notna()].copy()
df["score"] = df.score_value.astype(int)
df["category"] = np.where(df.archetype.str.startswith("CARDIO"), "cardiovascular", "neurological")
archs = sorted(df.archetype.unique())
out = {"n_scored": len(df), "n_items": df.variation.nunique(), "n_archetypes": len(archs),
       "bootstrap_draws": B, "seed": SEED}

def ci(x): return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]

def cluster_boot(fn):
    """Resample archetypes; fn(dataframe) -> dict of scalars."""
    by = {a: df[df.archetype == a] for a in archs}
    draws = []
    for _ in range(B):
        pick = rng.choice(archs, size=len(archs), replace=True)
        draws.append(fn(pd.concat([by[a] for a in pick], ignore_index=True)))
    return pd.DataFrame(draws)

# ---------------------------------------------------------------- 1. leaderboard
def model_means(d): return {m: d[d.model == m].score.mean() for m in MODELS}
bm = cluster_boot(model_means)
ranks = bm[MODELS].rank(axis=1, ascending=False, method="first")
board = []
for m in MODELS:
    s = df[df.model == m].score
    board.append({"model": m, "label": LABEL[m], "n": int(len(s)), "mean": float(s.mean()),
                  "ci": ci(bm[m]), "pass_rate": float((s == 2).mean()),
                  "fail_rate": float((s == 0).mean()),
                  "p_rank1": float((ranks[m] == 1).mean()),
                  "rank_dist": [float((ranks[m] == k).mean()) for k in (1, 2, 3)]})
board.sort(key=lambda r: -r["mean"])
out["leaderboard"] = board

# -------------------------------------------- 2. paired model differences
wide = df.pivot_table(index="variation", columns="model", values="score").dropna()
fr = stats.friedmanchisquare(*[wide[m] for m in MODELS])
out["friedman"] = {"n_items_complete": int(len(wide)), "chi2": float(fr.statistic), "p": float(fr.pvalue)}
pairs = []
for a, b in itertools.combinations(MODELS, 2):
    def diff(d, a=a, b=b):
        w = d.pivot_table(index="variation", columns="model", values="score").dropna(subset=[a, b])
        return {"d": (w[a] - w[b]).mean()}
    bd = cluster_boot(diff)
    obs = (wide[a] - wide[b]).mean()
    pairs.append({"a": LABEL[a], "b": LABEL[b], "diff": float(obs), "ci": ci(bd.d),
                  "wilcoxon_p": float(stats.wilcoxon(wide[a], wide[b], zero_method="zsplit").pvalue)})
out["pairwise"] = pairs

# ------------------------------------ 3. item difficulty consistency (Kendall W)
R = wide[MODELS].rank(axis=0).values          # rank items within each model
k, n = R.shape[1], R.shape[0]
S = ((R.sum(axis=1) - R.sum(axis=1).mean()) ** 2).sum()
W = 12 * S / (k ** 2 * (n ** 3 - n))
chi = k * (n - 1) * W
out["kendall_w"] = {"W": float(W), "chi2": float(chi), "df": n - 1,
                    "p": float(stats.chi2.sf(chi, n - 1)), "n_items": n}
sp = {f"{LABEL[a]} × {LABEL[b]}": float(stats.spearmanr(wide[a], wide[b]).statistic)
      for a, b in itertools.combinations(MODELS, 2)}
out["item_spearman"] = sp

# ----------------------- 4. category effect: exact permutation, archetype = unit
amean = df.groupby("archetype").score.mean()
acat = df.groupby("archetype").category.first()
card = amean[acat == "cardiovascular"].values
neur = amean[acat == "neurological"].values
obs = neur.mean() - card.mean()
allv = amean.values
perm = [allv[list(g)].mean() - np.delete(allv, list(g)).mean()
        for g in itertools.combinations(range(len(allv)), len(neur))]
perm = np.array(perm)
p_exact = float((np.abs(perm) >= abs(obs) - 1e-12).mean())
loo = {}
for a in archs:
    sub = amean.drop(a); sc = acat.drop(a)
    loo[a] = float(sub[sc == "neurological"].mean() - sub[sc == "cardiovascular"].mean())
out["category"] = {"diff_neuro_minus_cardio": float(obs), "p_exact_permutation": p_exact,
                   "n_permutations": int(len(perm)),
                   "archetype_means": {a: float(v) for a, v in amean.items()},
                   "leave_one_out": loo,
                   "mannwhitney_p": float(stats.mannwhitneyu(neur, card, alternative="two-sided").pvalue)}

# ------------------------------------------------ 5. mixed-effects model
mm = smf.mixedlm("score ~ C(model, Treatment('glm_5_2')) + C(category) + C(dimension)",
                 df, groups=df["archetype"]).fit(reml=True)
fe = []
for name, est in mm.fe_params.items():
    lo, hi = mm.conf_int().loc[name]
    fe.append({"term": name, "est": float(est), "ci": [float(lo), float(hi)], "p": float(mm.pvalues[name])})
var_arch = float(mm.cov_re.iloc[0, 0]); var_res = float(mm.scale)
out["mixed_model"] = {"formula": "score ~ model + category + dimension + (1 | archetype)",
                      "fixed_effects": fe, "var_archetype": var_arch, "var_residual": var_res,
                      "icc_archetype": var_arch / (var_arch + var_res)}

# ----------------------------------------------- 6. dimension × category cells
cells = []
for dim in sorted(df.dimension.unique()):
    for cat in ["cardiovascular", "neurological"]:
        s = df[(df.dimension == dim) & (df.category == cat)]
        if not len(s): continue
        boots = cluster_boot(lambda d, dim=dim, cat=cat:
                             {"m": d[(d.dimension == dim) & (d.category == cat)].score.mean()})
        cells.append({"dimension": dim, "category": cat, "n": int(len(s)), "mean": float(s.score.mean()),
                      "ci": ci(boots.m.dropna()), "pass_rate": float((s.score == 2).mean())})
out["cells"] = cells

# ------------------------------------- 7. perturbation rigidity (H1 only)
HOLD = re.compile(r"(does not (change|alter)|do not (change|revise)|doesn.t change|remains? (unchanged|the same)|"
                  r"no (new|substantive|meaningful) (information|data|change|clinical)|plan (is |remains )?unchanged|"
                  r"I (would )?not (revise|change)|nothing (changes|in my)|my (plan|assessment) (stands|remains))", re.I)
q2 = {}
for m in MODELS:
    try:
        for line in open(JSONL.format(m)):
            r = json.loads(line)
            if r.get("phase") == "Q2" and r.get("success"):
                q2[(m, r["variation_id"])] = r.get("response_text") or ""
    except FileNotFoundError:
        pass
h1 = df[df.hypothesis == "H1"].copy()
h1["kept"] = [bool(HOLD.search(q2.get((m, v), "")[:900])) for m, v in zip(h1.model, h1.variation)]
tab = pd.crosstab(h1.kept, h1.score == 0)
odds, fp = stats.fisher_exact(tab.values)
out["rigidity"] = {"table": {"kept_fail": int(tab.loc[True, True]), "kept_nonfail": int(tab.loc[True, False]),
                             "revised_fail": int(tab.loc[False, True]), "revised_nonfail": int(tab.loc[False, False])},
                   "odds_ratio": float(odds), "fisher_p": float(fp),
                   "revision_rate_by_model": {LABEL[m]: float((~h1[h1.model == m].kept).mean()) for m in MODELS},
                   "by_score": {lbl: {"kept": int(((h1.score == v) & h1.kept).sum()),
                                      "revised": int(((h1.score == v) & ~h1.kept).sum())}
                                for lbl, v in [("pass", 2), ("partial", 1), ("fail", 0)]}}

# ------------------------------------------------ 8. power / sample size
sd_a = np.sqrt(var_arch); sd_e = np.sqrt(var_res)
def power_category(n_per, delta, sims=2000, items_per_arch=8.5):
    hits = 0
    for _ in range(sims):
        c = rng.normal(0, sd_a, n_per) + rng.normal(0, sd_e / np.sqrt(items_per_arch), n_per)
        nn = rng.normal(delta, sd_a, n_per) + rng.normal(0, sd_e / np.sqrt(items_per_arch), n_per)
        hits += stats.ttest_ind(nn, c).pvalue < 0.05
    return hits / sims
def power_models(n_items, delta, sims=2000):
    sd_d = float(np.std(wide["glm_5_2"] - wide["deepseek_v4_pro"], ddof=1))
    return float(np.mean([stats.ttest_1samp(rng.normal(delta, sd_d, n_items), 0).pvalue < 0.05
                          for _ in range(sims)])), sd_d
obs_model_gap = max(r["mean"] for r in board) - min(r["mean"] for r in board)
curve_cat = [{"archetypes_per_category": n, "power": power_category(n, obs)} for n in (5, 8, 10, 15, 20, 30)]
pm = [(n, *power_models(n, obs_model_gap)) for n in (25, 50, 100, 150, 200, 300)]
out["power"] = {"category_effect_size": float(obs), "model_gap": float(obs_model_gap),
                "category_curve": curve_cat,
                "model_curve": [{"paired_items": n, "power": p} for n, p, _ in pm],
                "sd_paired_diff": pm[0][2]}

json.dump(out, open("analysis_results.json", "w"), indent=2)

# ------------------------------------------------------------- summary
print(f"n={out['n_scored']} scores | {out['n_items']} items | {out['n_archetypes']} archetypes\n")
print("LEADERBOARD (cluster-bootstrap 95% CI)")
for r in board:
    print(f"  {r['label']:16} {r['mean']:.2f} [{r['ci'][0]:.2f}, {r['ci'][1]:.2f}]  P(rank 1)={r['p_rank1']:.0%}")
print(f"\nFriedman (n={len(wide)} complete items): chi2={fr.statistic:.2f}, p={fr.pvalue:.3f}")
for p in pairs:
    print(f"  {p['a']} − {p['b']}: {p['diff']:+.2f} [{p['ci'][0]:+.2f}, {p['ci'][1]:+.2f}]  Wilcoxon p={p['wilcoxon_p']:.3f}")
print(f"\nKendall W (item difficulty agreement across models) = {W:.2f}, p={out['kendall_w']['p']:.2g}")
for k_, v in sp.items(): print(f"  Spearman {k_}: {v:.2f}")
c = out["category"]
print(f"\nCategory neuro − cardio (archetype-level) = {c['diff_neuro_minus_cardio']:+.2f}, "
      f"exact permutation p={c['p_exact_permutation']:.3f} ({c['n_permutations']} perms)")
print("  leave-one-out:", {k_: round(v, 2) for k_, v in c["leave_one_out"].items()})
print(f"\nMixed model  ICC(archetype) = {out['mixed_model']['icc_archetype']:.2f}")
for f in fe: print(f"  {f['term']:55} {f['est']:+.2f} [{f['ci'][0]:+.2f}, {f['ci'][1]:+.2f}] p={f['p']:.3f}")
rg = out["rigidity"]
print(f"\nRigidity (H1): OR={rg['odds_ratio']:.2f}, Fisher p={rg['fisher_p']:.3f}  {rg['table']}")
print("\nPower — category effect:", [(d['archetypes_per_category'], round(d['power'], 2)) for d in curve_cat])
print("Power — model gap %.2f:" % obs_model_gap, [(d['paired_items'], round(d['power'], 2)) for d in out['power']['model_curve']])