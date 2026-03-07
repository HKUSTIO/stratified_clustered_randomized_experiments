import itertools

import numpy as np
import pandas as pd

from src.stratified_clustered import (
    assign_treatment_clustered,
    assign_treatment_stratified,
    compute_n1_by_stratum,
    estimate_cluster_ate_and_ci,
    estimate_stratified_ate_and_ci,
    fisher_pvalue,
    generate_potential_outcomes_clustered,
    generate_potential_outcomes_stratified,
    stat_cluster_average,
    stat_diff_in_means,
    stat_stratified_weighted,
)


def test_compute_n1_by_stratum():
    n1 = compute_n1_by_stratum(
        n_total=100,
        stratum_weights={"A": 0.6, "B": 0.4},
        treat_propensity_by_stratum={"A": 0.3, "B": 0.7},
    )
    assert n1 == {"A": 18, "B": 28}


def test_generate_potential_outcomes_stratified_columns_and_size():
    config = {
        "seed_stratified_population": 1,
        "stratified": {
            "n_total": 10,
            "strata": ["A", "B"],
            "stratum_weights": {"A": 0.6, "B": 0.4},
            "tau_by_stratum": {"A": 0.2, "B": 0.3},
            "sd_y0_by_stratum": {"A": 1.0, "B": 1.0},
            "sd_y1_by_stratum": {"A": 1.0, "B": 1.0},
        },
    }
    df = generate_potential_outcomes_stratified(config)
    assert list(df.columns) == ["unit_id", "g", "y0", "y1"]
    assert len(df) == 10
    assert (df["g"] == "A").sum() == 6
    assert (df["g"] == "B").sum() == 4


def test_assign_treatment_stratified_counts():
    potential = pd.DataFrame(
        {
            "unit_id": [1, 2, 3, 4, 5, 6],
            "g": ["A", "A", "A", "B", "B", "B"],
            "y0": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "y1": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        }
    )
    observed = assign_treatment_stratified(potential, {"A": 1, "B": 2}, seed=7)
    assert observed.loc[observed["g"] == "A", "z"].sum() == 1
    assert observed.loc[observed["g"] == "B", "z"].sum() == 2
    assert list(observed.columns) == ["unit_id", "g", "z", "y"]


def test_generate_and_assign_clustered():
    config = {
        "seed_clustered_population": 5,
        "clustered": {
            "g_total": 5,
            "cluster_size_poisson_lambda": 3,
            "tau_cluster_abs_normal_scale": 1.0,
            "sd_y0": 1.0,
            "sd_y1": 1.0,
        },
    }
    potential = generate_potential_outcomes_clustered(config)
    assert set(["unit_id", "cluster_id", "y0", "y1"]).issubset(potential.columns)
    observed = assign_treatment_clustered(potential, g1=2, seed=8)
    cluster_treat = observed.groupby("cluster_id")["z"].mean()
    assert (cluster_treat == 1).sum() == 2
    assert (cluster_treat == 0).sum() == 3


def test_statistics_and_ci_on_fixed_data():
    data_str = pd.DataFrame(
        {
            "unit_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "g": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "z": [1, 1, 0, 0, 1, 1, 0, 0],
            "y": [3.0, 5.0, 1.0, 3.0, 4.0, 6.0, 2.0, 4.0],
        }
    )
    assert np.isclose(stat_diff_in_means(data_str), 2.0)
    assert np.isclose(stat_stratified_weighted(data_str, {"A": 0.6, "B": 0.4}), 2.0)
    ci_str = estimate_stratified_ate_and_ci(data_str, {"A": 0.6, "B": 0.4}, alpha=0.05)
    assert ci_str["ci_lower"] < ci_str["tau_hat"] < ci_str["ci_upper"]

    data_cl = pd.DataFrame(
        {
            "unit_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "cluster_id": [1, 1, 2, 2, 3, 3, 4, 4],
            "z": [1, 1, 1, 1, 0, 0, 0, 0],
            "y": [3.0, 5.0, 1.0, 3.0, 4.0, 6.0, 2.0, 4.0],
        }
    )
    assert np.isclose(stat_cluster_average(data_cl), -1.0)
    ci_cl = estimate_cluster_ate_and_ci(data_cl, alpha=0.05)
    assert ci_cl["ci_lower"] < ci_cl["tau_hat"] < ci_cl["ci_upper"]


def test_fisher_pvalue_known_case():
    data = pd.DataFrame(
        {
            "unit_id": [1, 2, 3, 4],
            "g": ["A", "A", "A", "A"],
            "z": [1, 1, 0, 0],
            "y": [1.0, 2.0, 3.0, 4.0],
        }
    )
    assignments = list(itertools.combinations([0, 1, 2, 3], 2))

    def rerandomize_fn(df: pd.DataFrame, seed: int) -> pd.DataFrame:
        treated = assignments[seed % len(assignments)]
        out = df.copy()
        out["z"] = 0
        out.loc[list(treated), "z"] = 1
        return out

    pvalue = fisher_pvalue(data, stat_diff_in_means, rerandomize_fn, r=6, seed=0)
    assert np.isclose(pvalue, 2.0 / 6.0)
import itertools

import numpy as np
import pandas as pd

from src.stratified_clustered import (
    assign_treatment_clustered,
    assign_treatment_stratified,
    compute_n1_by_stratum,
    estimate_cluster_ate_and_ci,
    estimate_stratified_ate_and_ci,
    fisher_pvalue,
    generate_potential_outcomes_clustered,
    generate_potential_outcomes_stratified,
    stat_cluster_average,
    stat_diff_in_means,
    stat_stratified_weighted,
)


def test_compute_n1_by_stratum():
    n1 = compute_n1_by_stratum(
        n_total=100,
        stratum_weights={"A": 0.6, "B": 0.4},
        treat_propensity_by_stratum={"A": 0.3, "B": 0.7},
    )
    assert n1 == {"A": 18, "B": 28}


def test_generate_potential_outcomes_stratified_columns_and_size():
    config = {
        "seed_stratified_population": 1,
        "stratified": {
            "n_total": 10,
            "strata": ["A", "B"],
            "stratum_weights": {"A": 0.6, "B": 0.4},
            "tau_by_stratum": {"A": 0.2, "B": 0.3},
            "sd_y0_by_stratum": {"A": 1.0, "B": 1.0},
            "sd_y1_by_stratum": {"A": 1.0, "B": 1.0},
        },
    }
    df = generate_potential_outcomes_stratified(config)
    assert list(df.columns) == ["unit_id", "g", "y0", "y1"]
    assert len(df) == 10
    assert (df["g"] == "A").sum() == 6
    assert (df["g"] == "B").sum() == 4


def test_assign_treatment_stratified_counts():
    potential = pd.DataFrame(
        {
            "unit_id": [1, 2, 3, 4, 5, 6],
            "g": ["A", "A", "A", "B", "B", "B"],
            "y0": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "y1": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        }
    )
    observed = assign_treatment_stratified(potential, {"A": 1, "B": 2}, seed=7)
    assert observed.loc[observed["g"] == "A", "z"].sum() == 1
    assert observed.loc[observed["g"] == "B", "z"].sum() == 2
    assert list(observed.columns) == ["unit_id", "g", "z", "y"]


def test_generate_and_assign_clustered():
    config = {
        "seed_clustered_population": 5,
        "clustered": {
            "g_total": 5,
            "cluster_size_poisson_lambda": 3,
            "tau_cluster_abs_normal_scale": 1.0,
            "sd_y0": 1.0,
            "sd_y1": 1.0,
        },
    }
    potential = generate_potential_outcomes_clustered(config)
    assert set(["unit_id", "cluster_id", "y0", "y1"]).issubset(potential.columns)
    observed = assign_treatment_clustered(potential, g1=2, seed=8)
    cluster_treat = observed.groupby("cluster_id")["z"].mean()
    assert (cluster_treat == 1).sum() == 2
    assert (cluster_treat == 0).sum() == 3


def test_statistics_and_ci_on_fixed_data():
    data_str = pd.DataFrame(
        {
            "unit_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "g": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "z": [1, 1, 0, 0, 1, 1, 0, 0],
            "y": [3.0, 5.0, 1.0, 3.0, 4.0, 6.0, 2.0, 4.0],
        }
    )
    assert np.isclose(stat_diff_in_means(data_str), 2.0)
    assert np.isclose(stat_stratified_weighted(data_str, {"A": 0.6, "B": 0.4}), 2.0)
    ci_str = estimate_stratified_ate_and_ci(data_str, {"A": 0.6, "B": 0.4}, alpha=0.05)
    assert ci_str["ci_lower"] < ci_str["tau_hat"] < ci_str["ci_upper"]

    data_cl = pd.DataFrame(
        {
            "unit_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "cluster_id": [1, 1, 2, 2, 3, 3, 4, 4],
            "z": [1, 1, 1, 1, 0, 0, 0, 0],
            "y": [3.0, 5.0, 1.0, 3.0, 4.0, 6.0, 2.0, 4.0],
        }
    )
    assert np.isclose(stat_cluster_average(data_cl), -1.0)
    ci_cl = estimate_cluster_ate_and_ci(data_cl, alpha=0.05)
    assert ci_cl["ci_lower"] < ci_cl["tau_hat"] < ci_cl["ci_upper"]


def test_fisher_pvalue_known_case():
    data = pd.DataFrame(
        {
            "unit_id": [1, 2, 3, 4],
            "g": ["A", "A", "A", "A"],
            "z": [1, 1, 0, 0],
            "y": [1.0, 2.0, 3.0, 4.0],
        }
    )
    assignments = list(itertools.combinations([0, 1, 2, 3], 2))

    def rerandomize_fn(df: pd.DataFrame, seed: int) -> pd.DataFrame:
        treated = assignments[seed % len(assignments)]
        out = df.copy()
        out["z"] = 0
        out.loc[list(treated), "z"] = 1
        return out

    pvalue = fisher_pvalue(data, stat_diff_in_means, rerandomize_fn, r=6, seed=0)
    assert np.isclose(pvalue, 2.0 / 6.0)
