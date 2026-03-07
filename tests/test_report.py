import json
from pathlib import Path


def test_output_files_exist_after_run():
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "cleaned" / "potential_outcomes_stratified.csv",
        root / "cleaned" / "observed_data_stratified.csv",
        root / "cleaned" / "potential_outcomes_clustered.csv",
        root / "cleaned" / "observed_data_clustered.csv",
        root / "output" / "results.json",
    ]
    for path in required:
        assert path.exists(), f"Missing file: {path}"


def test_results_json_keys():
    root = Path(__file__).resolve().parents[1]
    results = json.loads((root / "output" / "results.json").read_text(encoding="utf-8"))
    required = {
        "fisher_stratified_diff_pvalue",
        "fisher_stratified_weighted_pvalue",
        "fisher_cluster_unit_diff_pvalue",
        "fisher_cluster_average_pvalue",
        "neyman_stratified_weighted",
        "neyman_cluster_average",
    }
    assert required.issubset(results.keys())


def test_rendered_html_exists_and_contains_sections():
    root = Path(__file__).resolve().parents[1]
    html_path = root / "report" / "solution.html"
    assert html_path.exists(), "Missing report/solution.html."
    html = html_path.read_text(encoding="utf-8")
    required_strings = [
        "Fisher randomization inference",
        "Neyman inference",
        "stratified_diff_in_means",
        "clustered_cluster_average",
    ]
    for token in required_strings:
        assert token in html
import json
from pathlib import Path


def test_output_files_exist_after_run():
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "cleaned" / "potential_outcomes_stratified.csv",
        root / "cleaned" / "observed_data_stratified.csv",
        root / "cleaned" / "potential_outcomes_clustered.csv",
        root / "cleaned" / "observed_data_clustered.csv",
        root / "output" / "results.json",
    ]
    for path in required:
        assert path.exists(), f"Missing file: {path}"


def test_results_json_keys():
    root = Path(__file__).resolve().parents[1]
    results = json.loads((root / "output" / "results.json").read_text(encoding="utf-8"))
    required = {
        "fisher_stratified_diff_pvalue",
        "fisher_stratified_weighted_pvalue",
        "fisher_cluster_unit_diff_pvalue",
        "fisher_cluster_average_pvalue",
        "neyman_stratified_weighted",
        "neyman_cluster_average",
    }
    assert required.issubset(results.keys())


def test_rendered_html_exists_and_contains_sections():
    root = Path(__file__).resolve().parents[1]
    html_path = root / "report" / "solution.html"
    assert html_path.exists(), "Missing report/solution.html."
    html = html_path.read_text(encoding="utf-8")
    required_strings = [
        "Fisher randomization inference",
        "Neyman inference",
        "stratified_diff_in_means",
        "clustered_cluster_average",
    ]
    for token in required_strings:
        assert token in html
