import pytest

from ai.evaluation import compare_rankings, compare_scores, classification_metrics


def test_compare_scores_reports_real_input_agreement():
    result = compare_scores([80, 60, 40], [80, 55, 40])
    assert result == {
        "sample_count": 3,
        "exact_agreement_rate": pytest.approx(2 / 3),
        "mean_absolute_error": pytest.approx(5 / 3),
    }


def test_compare_scores_rejects_empty_or_mismatched_inputs():
    with pytest.raises(ValueError):
        compare_scores([], [])
    with pytest.raises(ValueError):
        compare_scores([1], [])


def test_compare_rankings_measures_pairwise_agreement():
    result = compare_rankings(["a", "b", "c"], ["a", "c", "b"])
    assert result["pair_count"] == 3
    assert result["pairwise_agreement_rate"] == pytest.approx(2 / 3)


def test_compare_rankings_requires_same_unique_candidates():
    with pytest.raises(ValueError):
        compare_rankings(["a", "a"], ["a", "b"])


def test_classification_metrics_expose_false_positive_and_negative_counts():
    result = classification_metrics(
        {"a": True, "b": False, "c": True, "d": False},
        {"a": True, "b": True, "c": False, "d": False},
    )
    assert result["true_positive"] == 1
    assert result["false_positive"] == 1
    assert result["false_negative"] == 1
    assert result["true_negative"] == 1
    assert result["precision"] == pytest.approx(0.5)
    assert result["recall"] == pytest.approx(0.5)
