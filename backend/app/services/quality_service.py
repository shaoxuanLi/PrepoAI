def compute_f1(precision: float, recall: float) -> float:
    """Compute F1 score for annotator consensus quality checks."""
    if precision <= 0 or recall <= 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)
