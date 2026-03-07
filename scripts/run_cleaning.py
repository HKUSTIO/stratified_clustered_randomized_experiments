import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.stratified_clustered import (
    assign_treatment_clustered,
    assign_treatment_stratified,
    compute_n1_by_stratum,
    generate_potential_outcomes_clustered,
    generate_potential_outcomes_stratified,
)


def main() -> None:
    config = json.loads((ROOT / "config" / "assignment.json").read_text(encoding="utf-8"))
    cleaned_dir = ROOT / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    stratified_cfg = config["stratified"]
    clustered_cfg = config["clustered"]

    n1_by_stratum = compute_n1_by_stratum(
        n_total=int(stratified_cfg["n_total"]),
        stratum_weights={str(k): float(v) for k, v in stratified_cfg["stratum_weights"].items()},
        treat_propensity_by_stratum={str(k): float(v) for k, v in stratified_cfg["treat_propensity_by_stratum"].items()},
    )

    potential_strat = generate_potential_outcomes_stratified(config)
    observed_strat = assign_treatment_stratified(
        potential=potential_strat,
        n1_by_stratum=n1_by_stratum,
        seed=int(config["seed_stratified_assignment"]),
    )

    potential_cluster = generate_potential_outcomes_clustered(config)
    g1 = int(round(float(clustered_cfg["treated_cluster_share"]) * int(clustered_cfg["g_total"])))
    observed_cluster = assign_treatment_clustered(
        potential=potential_cluster,
        g1=g1,
        seed=int(config["seed_clustered_assignment"]),
    )

    potential_strat.to_csv(cleaned_dir / "potential_outcomes_stratified.csv", index=False)
    observed_strat.to_csv(cleaned_dir / "observed_data_stratified.csv", index=False)
    potential_cluster.to_csv(cleaned_dir / "potential_outcomes_clustered.csv", index=False)
    observed_cluster.to_csv(cleaned_dir / "observed_data_clustered.csv", index=False)


if __name__ == "__main__":
    main()
