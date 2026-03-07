import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.stratified_clustered import (
    estimate_cluster_ate_and_ci,
    estimate_stratified_ate_and_ci,
    fisher_pvalue,
    stat_cluster_average,
    stat_diff_in_means,
    stat_stratified_weighted,
)


def build_stratified_rerandomize_fn(n1_by_stratum: dict[str, int]):
    def rerandomize_fn(data: pd.DataFrame, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        out = data.copy()
        out["z"] = 0
        for g, group in out.groupby("g"):
            idx = group.index.to_numpy()
            treated_idx = rng.choice(idx, size=int(n1_by_stratum[g]), replace=False)
            out.loc[treated_idx, "z"] = 1
        return out

    return rerandomize_fn


def build_clustered_rerandomize_fn(g1: int):
    def rerandomize_fn(data: pd.DataFrame, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        out = data.copy()
        clusters = out["cluster_id"].drop_duplicates().to_numpy()
        treated_clusters = set(rng.choice(clusters, size=g1, replace=False).tolist())
        out["z"] = out["cluster_id"].isin(treated_clusters).astype(int)
        return out

    return rerandomize_fn


def main() -> None:
    config = json.loads((ROOT / "config" / "assignment.json").read_text(encoding="utf-8"))
    cleaned_dir = ROOT / "cleaned"
    output_dir = ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    observed_strat = pd.read_csv(cleaned_dir / "observed_data_stratified.csv")
    observed_cluster = pd.read_csv(cleaned_dir / "observed_data_clustered.csv")

    strat_cfg = config["stratified"]
    cluster_cfg = config["clustered"]

    n_total = int(strat_cfg["n_total"])
    n1_by_stratum = {
        g: int(round(n_total * float(strat_cfg["stratum_weights"][g]) * float(strat_cfg["treat_propensity_by_stratum"][g])))
        for g in strat_cfg["strata"]
    }
    lambda_by_stratum = {str(k): float(v) for k, v in strat_cfg["lambda_by_stratum"].items()}
    g1 = int(round(float(cluster_cfg["treated_cluster_share"]) * int(cluster_cfg["g_total"])))

    strat_rerandomize = build_stratified_rerandomize_fn(n1_by_stratum=n1_by_stratum)
    cluster_rerandomize = build_clustered_rerandomize_fn(g1=g1)
    r = int(config["fisher_replications"])

    strat_weighted_stat = lambda df: stat_stratified_weighted(df, lambda_by_stratum)
    p_strat_diff = fisher_pvalue(observed_strat, stat_diff_in_means, strat_rerandomize, r, int(config["seed_stratified_assignment"]))
    p_strat_weighted = fisher_pvalue(observed_strat, strat_weighted_stat, strat_rerandomize, r, int(config["seed_stratified_assignment"]) + 1)
    p_cluster_unit = fisher_pvalue(observed_cluster, stat_diff_in_means, cluster_rerandomize, r, int(config["seed_clustered_assignment"]))
    p_cluster_avg = fisher_pvalue(observed_cluster, stat_cluster_average, cluster_rerandomize, r, int(config["seed_clustered_assignment"]) + 1)

    ci_strat = estimate_stratified_ate_and_ci(observed_strat, lambda_by_stratum=lambda_by_stratum, alpha=float(config["alpha"]))
    ci_cluster = estimate_cluster_ate_and_ci(observed_cluster, alpha=float(config["alpha"]))

    results = {
        "fisher_stratified_diff_pvalue": float(p_strat_diff),
        "fisher_stratified_weighted_pvalue": float(p_strat_weighted),
        "fisher_cluster_unit_diff_pvalue": float(p_cluster_unit),
        "fisher_cluster_average_pvalue": float(p_cluster_avg),
        "neyman_stratified_weighted": ci_strat,
        "neyman_cluster_average": ci_cluster,
    }
    (output_dir / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
