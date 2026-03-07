# Stratified and Clustered Randomized Experiments Exercise

This assignment asks you to implement inference and estimation for stratified and clustered randomized experiments in one reproducible pipeline.

## Learning goals

You will implement finite-population simulation and random assignment procedures for stratified and clustered designs, compute Fisher randomization p-values under multiple statistics, and construct Neyman-style confidence intervals for weighted stratified and cluster-average estimators.

## Project structure

```text
stratified_clustered_randomized_experiments/
├── .github/workflows/classroom.yml
├── config/assignment.json
├── input/
├── cleaned/
├── output/
├── report/solution.qmd
├── scripts/
│   ├── run_cleaning.py
│   ├── run_analysis.py
│   ├── run_pipeline.py
│   └── run_assignment.py
├── src/
│   ├── __init__.py
│   └── stratified_clustered.py
├── pyproject.toml
└── README.md
```

## Role of scripts

The `scripts` directory defines how the assignment pipeline is executed, while `src/stratified_clustered.py` contains the functions you must implement. `scripts/run_cleaning.py` loads the configuration, calls your `src` functions for data generation and treatment assignment, and writes intermediate datasets to `cleaned/`. `scripts/run_analysis.py` loads those cleaned datasets, calls your `src` inference functions, and writes Fisher and Neyman outputs to `output/results.json`. `scripts/run_pipeline.py` is the orchestrator that runs cleaning first and analysis second. `scripts/run_assignment.py` is a thin entrypoint that calls `run_pipeline.py`, so running either script executes the same end-to-end workflow.

## Your tasks

All parameters and hyperparameters are defined in `config/assignment.json`. Use this file as the single source of truth and do not hard-code constants in `src/` or `scripts/`.

The mathematical setting follows the original reference documents for stratified and clustered randomized experiments.

The mapping between mathematical symbols and config keys is:

| Symbol or quantity | `config/assignment.json` key | Notes |
|---|---|---|
| $N$ | `stratified.n_total` | Total units in stratified design |
| $g \in \{A,B\}$ | `stratified.strata` | For this assignment: `["A", "B"]` |
| $q_g$ | `stratified.stratum_weights[g]` | Stratum share |
| $e_g$ | `stratified.treat_propensity_by_stratum[g]` | Stratum treatment propensity |
| $N_{1g}$ | computed from `N * q_g * e_g` | Implemented by `compute_n1_by_stratum` |
| $\tau_g$ (stratified) | `stratified.tau_by_stratum[g]` | Mean shift in treated potential outcomes |
| $\sigma_{0g}$ | `stratified.sd_y0_by_stratum[g]` | SD for `Y_i(0)` in stratum `g` |
| $\sigma_{1g}$ | `stratified.sd_y1_by_stratum[g]` | SD for `Y_i(1)` in stratum `g` |
| $\lambda_g$ | `stratified.lambda_by_stratum[g]` | Weight in weighted stratified estimator |
| $s_{\mathrm{str,pop}}$ | `seed_stratified_population` | RNG seed for stratified potential outcomes |
| $s_{\mathrm{str,assign}}$ | `seed_stratified_assignment` | RNG seed for stratified treatment assignment |
| $G$ | `clustered.g_total` | Number of clusters |
| $\lambda_N$ | `clustered.cluster_size_poisson_lambda` | Poisson parameter for cluster sizes |
| $\pi_G$ | `clustered.treated_cluster_share` | Share used to compute treated cluster count |
| $G_1$ | computed as `round(G * clustered.treated_cluster_share)` | Treated cluster count |
| $\sigma_{\tau}$ (clustered scale) | `clustered.tau_cluster_abs_normal_scale` | Scale for `abs(N(0, scale^2))` |
| $\sigma_0$ | `clustered.sd_y0` | SD for clustered `Y_{ig}(0)` |
| $\sigma_1$ | `clustered.sd_y1` | SD for clustered `Y_{ig}(1)` |
| $s_{\mathrm{clu,pop}}$ | `seed_clustered_population` | RNG seed for clustered potential outcomes |
| $s_{\mathrm{clu,assign}}$ | `seed_clustered_assignment` | RNG seed for clustered treatment assignment |
| $R$ | `fisher_replications` | Number of rerandomization draws |
| $\alpha$ | `alpha` | Significance level for confidence intervals |

In the stratified design, there are two strata indexed by `g` in `{A, B}`. Let `N` be total sample size, let `q_g` be stratum share with shares summing to one, and let `e_g` be stratum-specific treatment propensity. The treated count in stratum `g` is
$$
N_{1g} = N q_g e_g.
$$
For each unit `i` in stratum `g`, potential outcomes satisfy
$$
Y_i(0) \sim \mathcal{N}(0, \sigma_{0g}^2),
$$
$$
Y_i(1) \sim \mathcal{N}(\tau_g, \sigma_{1g}^2).
$$
Observed outcomes are
$$
Y_i = Z_i Y_i(1) + (1-Z_i)Y_i(0).
$$
The weighted stratified estimand and estimator use
$$
\tau_{str} = \sum_g \lambda_g \tau_g,
$$
$$
\hat{\tau}_{str} = \sum_g \lambda_g \left(\bar{Y}_{1g} - \bar{Y}_{0g}\right),
$$
where the reference setup uses weights proportional to
$$
q_g e_g(1-e_g).
$$

For Fisher randomization inference in the stratified design, define a statistic `T(Z, Y)` and compute the two-sided p-value by rerandomization:
$$
p = \frac{1}{R}\sum_{r=1}^{R}\mathbf{1}\left\{\left|T^{(r)}\right|\ge \left|T^{obs}\right|\right\}.
$$

In the clustered design, there are `G` clusters indexed by `g = 1, ..., G` with random cluster sizes
$$
N_g \sim \text{Poisson}(\lambda_N) + 1,
$$
and total units
$$
N=\sum_{g=1}^{G}N_g.
$$
Treatment is assigned at the cluster level with `G_1` treated clusters and `G_0 = G - G_1` controls. Cluster-level treatment effects satisfy
$$
\tau_g \sim |\mathcal{N}(0, \sigma_{\tau}^2)|.
$$
Potential outcomes for unit `i` in cluster `g` satisfy
$$
Y_{ig}(0)\sim \mathcal{N}(0,\sigma_0^2),
$$
$$
Y_{ig}(1)\sim \mathcal{N}(\tau_g,\sigma_1^2).
$$
Two benchmark population quantities are
$$
\tau = \sum_{g=1}^{G}\tau_g\frac{N_g}{N},
$$
$$
\tau_c = \frac{1}{G}\sum_{g=1}^{G}\tau_g.
$$
The cluster-average estimator compares cluster mean outcomes between treated and control clusters:
$$
\hat{\tau}_c = \frac{1}{G_1}\sum_{g:Z_g=1}\bar{Y}_g - \frac{1}{G_0}\sum_{g:Z_g=0}\bar{Y}_g.
$$
Its Neyman-style standard error uses cluster-level sample variances:
$$
\widehat{SE}(\hat{\tau}_c)=\sqrt{\frac{s_1^2}{G_1}+\frac{s_0^2}{G_0}}.
$$

Implement all required functions in `src/stratified_clustered.py` with the exact signatures below.

```python
def compute_n1_by_stratum(n_total: int, stratum_weights: dict[str, float], treat_propensity_by_stratum: dict[str, float]) -> dict[str, int]: ...
def generate_potential_outcomes_stratified(config: dict) -> pd.DataFrame: ...
def assign_treatment_stratified(potential: pd.DataFrame, n1_by_stratum: dict[str, int], seed: int) -> pd.DataFrame: ...
def generate_potential_outcomes_clustered(config: dict) -> pd.DataFrame: ...
def assign_treatment_clustered(potential: pd.DataFrame, g1: int, seed: int) -> pd.DataFrame: ...
def stat_diff_in_means(data: pd.DataFrame) -> float: ...
def stat_stratified_weighted(data: pd.DataFrame, lambda_by_stratum: dict[str, float]) -> float: ...
def stat_cluster_average(data: pd.DataFrame) -> float: ...
def fisher_pvalue(data: pd.DataFrame, stat_fn: Callable[[pd.DataFrame], float], rerandomize_fn: Callable[[pd.DataFrame, int], pd.DataFrame], r: int, seed: int) -> float: ...
def estimate_stratified_ate_and_ci(data: pd.DataFrame, lambda_by_stratum: dict[str, float], alpha: float) -> dict[str, float]: ...
def estimate_cluster_ate_and_ci(data: pd.DataFrame, alpha: float) -> dict[str, float]: ...
```

Start with `compute_n1_by_stratum`, which must translate total sample size, stratum shares, and stratum treatment propensities into exact treated counts by stratum. These counts must be used for stratified assignment.

Then implement `generate_potential_outcomes_stratified` and `assign_treatment_stratified`. The generator must return exactly the columns `unit_id`, `g`, `y0`, `y1`, and the assignment function must return exactly `unit_id`, `g`, `z`, `y`.

Next implement `generate_potential_outcomes_clustered` and `assign_treatment_clustered`. The generator must return exactly `unit_id`, `cluster_id`, `y0`, `y1`, and the assignment function must randomize treatment at the cluster level and return exactly `unit_id`, `cluster_id`, `z`, `y`.

After data generation and assignment, implement the statistics `stat_diff_in_means`, `stat_stratified_weighted`, and `stat_cluster_average`, and then implement `fisher_pvalue` so that it computes a two-sided randomization p-value based on absolute statistics under repeated rerandomization.

Finally implement `estimate_stratified_ate_and_ci` and `estimate_cluster_ate_and_ci` so each function returns a dictionary with keys `tau_hat`, `se_hat`, `ci_lower`, and `ci_upper`.

For observed outcomes use
$$
y_i = z_i y_i(1) + (1-z_i)y_i(0).
$$
For the weighted stratified estimator use
$$
\hat{\tau}_{str} = \sum_g \lambda_g \left(\bar{y}_{1g} - \bar{y}_{0g}\right).
$$
For Fisher inference use a two-sided randomization p-value based on absolute statistics. For Neyman inference report
$$
\hat{\tau} \pm z_{1-\alpha/2}\hat{SE}.
$$

After implementing all functions, run `scripts/run_pipeline.py` and complete `report/solution.qmd` using values from `output/results.json`.

## Workflow

Step 1 is to accept the assignment link on GitHub Classroom, which creates your private repository under the course organization.

Step 2 is to clone your repository locally.

```bash
git clone https://github.com/HKUSTIO/<your-repo-name>.git
cd <your-repo-name>
```

Step 3 is to install dependencies with `uv`.

```bash
uv sync
```

Step 4 is to implement all required functions in `src/stratified_clustered.py`.

Step 5 is to run the pipeline and render the report.

```bash
uv run python scripts/run_pipeline.py
uv run quarto render report/solution.qmd
```

The pipeline has two stages. `scripts/run_cleaning.py` maps `input` to `cleaned`, and `scripts/run_analysis.py` maps `cleaned` to `output`. `scripts/run_pipeline.py` runs these two stages in sequence.

Step 6 is to commit and push your submission.

```bash
git add -A
git commit -m "your message"
git push
```

Step 7 is to check scores. Every push to `main` triggers the `Autograding Tests` workflow on GitHub Actions. Open the latest run in the Actions tab to see component scores and total points, and check the GitHub Classroom dashboard for the recorded score.

You can resubmit before the deadline by pushing again. The latest score is recorded, and there is no penalty for multiple submissions.

## Grading policy

Grading is based on two components that can be improved by resubmission. The first component checks correctness of your implementation in `src/stratified_clustered.py`, including formulas, output shapes, and reproducibility under configured seeds. The second component checks pipeline and report completeness, including required files in `cleaned` and `output`, successful rendering of `report/solution.html`, and presence of required result entries in `output/results.json`. Commit-message style and other immutable history details are not grading targets.
