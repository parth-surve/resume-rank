"""Metrics for evaluating predictions against human-labeled cases."""

from collections.abc import Iterable, Mapping


def compare_scores(
    labeled_scores: Iterable[float], predicted_scores: Iterable[float]
) -> dict:
    """Return agreement statistics; inputs must come from real labeled runs."""
    actual = list(labeled_scores)
    predicted = list(predicted_scores)
    if len(actual) != len(predicted):
        raise ValueError("Labeled and predicted scores must have equal length")
    if not actual:
        raise ValueError("At least one labeled score is required")

    absolute_errors = [abs(a - p) for a, p in zip(actual, predicted)]
    return {
        "sample_count": len(actual),
        "exact_agreement_rate": sum(error == 0 for error in absolute_errors)
        / len(actual),
        "mean_absolute_error": sum(absolute_errors) / len(actual),
    }


def compare_rankings(
    labeled_order: Iterable[str], predicted_order: Iterable[str]
) -> dict:
    """Compute pairwise ranking agreement for the same candidate set."""
    actual = list(labeled_order)
    predicted = list(predicted_order)
    if len(actual) != len(predicted) or set(actual) != set(predicted):
        raise ValueError("Rankings must contain the same unique candidates")
    if len(actual) < 2:
        raise ValueError("At least two candidates are required")

    actual_position = {candidate: i for i, candidate in enumerate(actual)}
    predicted_position = {candidate: i for i, candidate in enumerate(predicted)}
    pairs = [
        (left, right)
        for i, left in enumerate(actual)
        for right in actual[i + 1 :]
    ]
    concordant = sum(
        predicted_position[left] < predicted_position[right]
        for left, right in pairs
    )
    return {
        "candidate_count": len(actual),
        "pair_count": len(pairs),
        "pairwise_agreement_rate": concordant / len(pairs),
    }


def classification_metrics(
    labels: Mapping[str, bool], predictions: Mapping[str, bool]
) -> dict:
    """Compute confusion counts and precision/recall only with binary labels."""
    if not labels or set(labels) != set(predictions):
        raise ValueError("Labels and predictions must have the same nonempty keys")
    tp = sum(labels[key] and predictions[key] for key in labels)
    fp = sum(not labels[key] and predictions[key] for key in labels)
    fn = sum(labels[key] and not predictions[key] for key in labels)
    tn = len(labels) - tp - fp - fn
    return {
        "sample_count": len(labels),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
    }
