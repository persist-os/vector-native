"""
Metrics Calculation for HLE Benchmark
"""
from typing import List, Dict, Any
from vector_native import count_tokens


def calculate_accuracy(
    results: List[Dict[str, Any]],
    validation_mode: str = "exact_match"
) -> float:
    """
    Calculate accuracy from evaluation results.
    
    Args:
        results: List of evaluation results, each with "is_correct" dict
        validation_mode: Which validation mode to use for accuracy
    
    Returns:
        Accuracy percentage (0.0 to 100.0)
    """
    if not results:
        return 0.0
    
    correct = sum(
        1 for r in results
        if r.get("is_correct", {}).get(validation_mode, False)
    )
    
    total = len(results)
    return (correct / total * 100.0) if total > 0 else 0.0


def calculate_token_metrics(
    nl_responses: List[str],
    vn_responses: List[str],
    model: str = "claude-sonnet-4-20250514"
) -> Dict[str, Any]:
    """
    Calculate token usage metrics.
    
    Args:
        nl_responses: List of natural language response texts
        vn_responses: List of vector-native response texts
        model: Model name for token counting
    
    Returns:
        {
            "tokens_nl": int,
            "tokens_vn": int,
            "reduction_tokens": int,
            "reduction_percentage": float,
            "avg_tokens_nl": float,
            "avg_tokens_vn": float,
        }
    """
    # Count tokens for each response
    nl_tokens = [count_tokens(r, model) for r in nl_responses]
    vn_tokens = [count_tokens(r, model) for r in vn_responses]
    
    total_nl = sum(nl_tokens)
    total_vn = sum(vn_tokens)
    
    reduction_tokens = total_nl - total_vn
    reduction_pct = (reduction_tokens / total_nl * 100.0) if total_nl > 0 else 0.0
    
    return {
        "tokens_nl": total_nl,
        "tokens_vn": total_vn,
        "reduction_tokens": reduction_tokens,
        "reduction_percentage": round(reduction_pct, 2),
        "avg_tokens_nl": round(total_nl / len(nl_tokens), 2) if nl_tokens else 0.0,
        "avg_tokens_vn": round(total_vn / len(vn_tokens), 2) if vn_tokens else 0.0,
        "per_example": [
            {
                "nl_tokens": nl_tokens[i],
                "vn_tokens": vn_tokens[i],
                "reduction": nl_tokens[i] - vn_tokens[i],
                "reduction_pct": round((nl_tokens[i] - vn_tokens[i]) / nl_tokens[i] * 100, 2) if nl_tokens[i] > 0 else 0.0,
            }
            for i in range(len(nl_tokens))
        ],
    }


def calculate_delta_metrics(
    nl_results: List[Dict[str, Any]],
    vn_results: List[Dict[str, Any]],
    validation_mode: str = "exact_match"
) -> Dict[str, Any]:
    """
    Calculate delta (improvement) metrics between NL and VN.
    
    Args:
        nl_results: Natural language evaluation results
        vn_results: Vector-native evaluation results
        validation_mode: Which validation mode to use
    
    Returns:
        {
            "accuracy_nl": float,
            "accuracy_vn": float,
            "delta": float,  # VN - NL (positive = improvement)
            "delta_percentage": float,  # Percentage point improvement
            "improvement": bool,  # True if VN > NL
        }
    """
    accuracy_nl = calculate_accuracy(nl_results, validation_mode)
    accuracy_vn = calculate_accuracy(vn_results, validation_mode)
    
    delta = accuracy_vn - accuracy_nl
    delta_pct = delta  # Percentage points
    
    return {
        "accuracy_nl": round(accuracy_nl, 2),
        "accuracy_vn": round(accuracy_vn, 2),
        "delta": round(delta, 2),
        "delta_percentage": round(delta_pct, 2),
        "improvement": delta > 0,
        "parity": abs(delta) < 1.0,  # Within 1 percentage point
    }


def calculate_all_metrics(
    nl_results: List[Dict[str, Any]],
    vn_results: List[Dict[str, Any]],
    nl_responses: List[str],
    vn_responses: List[str],
    model: str = "claude-sonnet-4-20250514",
    validation_modes: List[str] = None
) -> Dict[str, Any]:
    """
    Calculate all metrics for the benchmark.
    
    Args:
        nl_results: Natural language evaluation results
        vn_results: Vector-native evaluation results
        nl_responses: Natural language response texts
        vn_responses: Vector-native response texts
        model: Model name for token counting
        validation_modes: List of validation modes to calculate metrics for
    
    Returns:
        Comprehensive metrics dictionary
    """
    if validation_modes is None:
        validation_modes = ["exact_match"]
    
    # Token metrics
    token_metrics = calculate_token_metrics(nl_responses, vn_responses, model)
    
    # Accuracy metrics per validation mode
    accuracy_metrics = {}
    delta_metrics = {}
    
    for mode in validation_modes:
        accuracy_metrics[mode] = {
            "nl": calculate_accuracy(nl_results, mode),
            "vn": calculate_accuracy(vn_results, mode),
        }
        delta_metrics[mode] = calculate_delta_metrics(nl_results, vn_results, mode)
    
    # Primary metric (exact_match)
    primary_mode = validation_modes[0]
    primary_delta = delta_metrics[primary_mode]
    
    return {
        "primary_metric": {
            "mode": primary_mode,
            "accuracy_nl": primary_delta["accuracy_nl"],
            "accuracy_vn": primary_delta["accuracy_vn"],
            "delta": primary_delta["delta"],
            "improvement": primary_delta["improvement"],
            "parity": primary_delta["parity"],
        },
        "accuracy": accuracy_metrics,
        "delta": delta_metrics,
        "tokens": token_metrics,
        "summary": {
            "total_examples": len(nl_results),
            "nl_correct": sum(
                1 for r in nl_results
                if r.get("is_correct", {}).get(primary_mode, False)
            ),
            "vn_correct": sum(
                1 for r in vn_results
                if r.get("is_correct", {}).get(primary_mode, False)
            ),
            "token_reduction_pct": token_metrics["reduction_percentage"],
            "accuracy_improvement": primary_delta["improvement"],
        },
    }

