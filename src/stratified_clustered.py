from __future__ import annotations

from typing import Callable

import pandas as pd


def compute_n1_by_stratum(n_total: int, stratum_weights: dict[str, float], treat_propensity_by_stratum: dict[str, float]) -> dict[str, int]:
    """
    Return exact treated counts by stratum.
    """
    raise NotImplementedError("Implement compute_n1_by_stratum().")


def generate_potential_outcomes_stratified(config: dict) -> pd.DataFrame:
    """
    Return columns: unit_id, g, y0, y1.
    """
    raise NotImplementedError("Implement generate_potential_outcomes_stratified().")


def assign_treatment_stratified(potential: pd.DataFrame, n1_by_stratum: dict[str, int], seed: int) -> pd.DataFrame:
    """
    Return columns: unit_id, g, z, y.
    """
    raise NotImplementedError("Implement assign_treatment_stratified().")


def generate_potential_outcomes_clustered(config: dict) -> pd.DataFrame:
    """
    Return columns: unit_id, cluster_id, y0, y1.
    """
    raise NotImplementedError("Implement generate_potential_outcomes_clustered().")


def assign_treatment_clustered(potential: pd.DataFrame, g1: int, seed: int) -> pd.DataFrame:
    """
    Return columns: unit_id, cluster_id, z, y.
    """
    raise NotImplementedError("Implement assign_treatment_clustered().")


def stat_diff_in_means(data: pd.DataFrame) -> float:
    """
    Return mean(y|z=1) - mean(y|z=0).
    """
    raise NotImplementedError("Implement stat_diff_in_means().")


def stat_stratified_weighted(data: pd.DataFrame, lambda_by_stratum: dict[str, float]) -> float:
    """
    Return weighted stratified mean difference.
    """
    raise NotImplementedError("Implement stat_stratified_weighted().")


def stat_cluster_average(data: pd.DataFrame) -> float:
    """
    Return difference in means using cluster-level averages.
    """
    raise NotImplementedError("Implement stat_cluster_average().")


def fisher_pvalue(
    data: pd.DataFrame,
    stat_fn: Callable[[pd.DataFrame], float],
    rerandomize_fn: Callable[[pd.DataFrame, int], pd.DataFrame],
    r: int,
    seed: int,
) -> float:
    """
    Return two-sided Fisher randomization p-value.
    """
    raise NotImplementedError("Implement fisher_pvalue().")


def estimate_stratified_ate_and_ci(data: pd.DataFrame, lambda_by_stratum: dict[str, float], alpha: float) -> dict[str, float]:
    """
    Return tau_hat, se_hat, ci_lower, ci_upper for weighted stratified estimator.
    """
    raise NotImplementedError("Implement estimate_stratified_ate_and_ci().")


def estimate_cluster_ate_and_ci(data: pd.DataFrame, alpha: float) -> dict[str, float]:
    """
    Return tau_hat, se_hat, ci_lower, ci_upper for cluster-average estimator.
    """
    raise NotImplementedError("Implement estimate_cluster_ate_and_ci().")
