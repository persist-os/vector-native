"""
Metrics Calculator for Smart Validation Framework

Calculates compliance rates, token reduction, statistical significance,
confidence intervals, and effect sizes for format comparison.
"""

import math
from typing import Dict, List, Any, Tuple, Optional

# Try to import scipy for advanced statistics, fall back to basic if not available
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Use Python's built-in statistics module
import statistics


def calculate_compliance_rate(results: List[Dict[str, Any]], format_type: str) -> float:
    """
    Calculate compliance rate for a format.
    
    Args:
        results: List of comparison results
        format_type: "natural_language", "json", or "vector_native"
    
    Returns:
        Compliance rate (0.0 to 1.0)
    """
    if not results:
        return 0.0
    
    compliant = sum(
        1 for r in results
        if r.get("comparison", {}).get(f"{format_type.split('_')[0]}_compliance", 0) == 1.0
    )
    
    return compliant / len(results)


def calculate_mean_token_reduction(
    results: List[Dict[str, Any]],
    baseline: str = "natural_language",
    target: str = "vector_native"
) -> float:
    """
    Calculate mean token reduction percentage.
    
    Args:
        results: List of comparison results
        baseline: Baseline format ("natural_language" or "json")
        target: Target format (usually "vector_native")
    
    Returns:
        Mean reduction percentage
    """
    if not results:
        return 0.0
    
    reductions = []
    for r in results:
        comparison = r.get("comparison", {})
        if baseline == "natural_language":
            reduction = comparison.get("vn_reduction_vs_nl", 0)
        else:
            reduction = comparison.get("vn_reduction_vs_json", 0)
        reductions.append(reduction)
    
    return statistics.mean(reductions) if reductions else 0.0


def calculate_confidence_interval(
    data: List[float],
    confidence: float = 0.95
) -> Tuple[float, float, float]:
    """
    Calculate confidence interval for mean.
    
    Args:
        data: List of values
        confidence: Confidence level (default: 0.95 for 95% CI)
    
    Returns:
        (mean, lower_bound, upper_bound)
    """
    if not data or len(data) < 2:
        mean = statistics.mean(data) if data else 0.0
        return (mean, mean, mean)
    
    mean = statistics.mean(data)
    stdev = statistics.stdev(data) if len(data) > 1 else 0.0
    n = len(data)
    
    # Use t-distribution for small samples, normal for large
    if HAS_SCIPY and n < 30:
        # t-distribution for small samples
        alpha = 1 - confidence
        t_critical = stats.t.ppf(1 - alpha / 2, df=n - 1)
        margin = t_critical * (stdev / math.sqrt(n))
    else:
        # Normal distribution approximation
        z_critical = 1.96 if confidence == 0.95 else 2.576 if confidence == 0.99 else 1.645
        margin = z_critical * (stdev / math.sqrt(n))
    
    return (mean, mean - margin, mean + margin)


def calculate_effect_size(
    group1: List[float],
    group2: List[float]
) -> float:
    """
    Calculate Cohen's d effect size.
    
    Args:
        group1: First group values
        group2: Second group values
    
    Returns:
        Cohen's d (effect size)
    """
    if not group1 or not group2:
        return 0.0
    
    mean1 = statistics.mean(group1)
    mean2 = statistics.mean(group2)
    
    # Pooled standard deviation
    if len(group1) > 1 and len(group2) > 1:
        var1 = statistics.variance(group1)
        var2 = statistics.variance(group2)
        pooled_std = math.sqrt((var1 + var2) / 2)
    elif len(group1) > 1:
        pooled_std = statistics.stdev(group1)
    elif len(group2) > 1:
        pooled_std = statistics.stdev(group2)
    else:
        return 0.0
    
    if pooled_std == 0:
        return 0.0
    
    return (mean1 - mean2) / pooled_std


def calculate_p_value(
    group1: List[float],
    group2: List[float],
    test_type: str = "two_sample_t"
) -> float:
    """
    Calculate p-value for difference between two groups.
    
    Args:
        group1: First group values
        group2: Second group values
        test_type: "two_sample_t" or "mannwhitney" (default: "two_sample_t")
    
    Returns:
        p-value
    """
    if not group1 or not group2:
        return 1.0
    
    if HAS_SCIPY:
        if test_type == "two_sample_t":
            # Two-sample t-test
            t_stat, p_value = stats.ttest_ind(group1, group2)
            return p_value
        elif test_type == "mannwhitney":
            # Mann-Whitney U test (non-parametric)
            u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            return p_value
    
    # Fallback: Simple t-test approximation
    mean1 = statistics.mean(group1)
    mean2 = statistics.mean(group2)
    
    if len(group1) > 1 and len(group2) > 1:
        var1 = statistics.variance(group1)
        var2 = statistics.variance(group2)
        pooled_std = math.sqrt((var1 + var2) / 2)
        se = pooled_std * math.sqrt(1/len(group1) + 1/len(group2))
    else:
        return 1.0
    
    if se == 0:
        return 1.0
    
    t_stat = (mean1 - mean2) / se
    # Approximate p-value (two-tailed)
    # For small samples, this is rough approximation
    p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(t_stat) / math.sqrt(2))))
    return min(p_value, 1.0)


def bootstrap_confidence_interval(
    data: List[float],
    confidence: float = 0.95,
    n_bootstrap: int = 1000
) -> Tuple[float, float, float]:
    """
    Calculate confidence interval using bootstrap sampling.
    
    Args:
        data: List of values
        confidence: Confidence level
        n_bootstrap: Number of bootstrap samples
    
    Returns:
        (mean, lower_bound, upper_bound)
    """
    if not data:
        return (0.0, 0.0, 0.0)
    
    import random
    
    n = len(data)
    bootstrap_means = []
    
    for _ in range(n_bootstrap):
        sample = random.choices(data, k=n)
        bootstrap_means.append(statistics.mean(sample))
    
    bootstrap_means.sort()
    mean = statistics.mean(data)
    
    alpha = 1 - confidence
    lower_idx = int(n_bootstrap * (alpha / 2))
    upper_idx = int(n_bootstrap * (1 - alpha / 2))
    
    lower_bound = bootstrap_means[lower_idx] if lower_idx < len(bootstrap_means) else bootstrap_means[0]
    upper_bound = bootstrap_means[upper_idx] if upper_idx < len(bootstrap_means) else bootstrap_means[-1]
    
    return (mean, lower_bound, upper_bound)


def calculate_all_metrics(
    results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate all metrics for format comparison.
    
    Args:
        results: List of comparison results
    
    Returns:
        Comprehensive metrics dict
    """
    if not results:
        return {
            "error": "No results provided"
        }
    
    # Compliance rates
    nl_compliance = calculate_compliance_rate(results, "natural_language")
    json_compliance = calculate_compliance_rate(results, "json")
    vn_compliance = calculate_compliance_rate(results, "vector_native")
    
    # Token reductions
    vn_reductions_vs_nl = [
        r["comparison"]["vn_reduction_vs_nl"]
        for r in results
        if "comparison" in r
    ]
    vn_reductions_vs_json = [
        r["comparison"]["vn_reduction_vs_json"]
        for r in results
        if "comparison" in r
    ]
    
    mean_reduction_vs_nl = statistics.mean(vn_reductions_vs_nl) if vn_reductions_vs_nl else 0.0
    mean_reduction_vs_json = statistics.mean(vn_reductions_vs_json) if vn_reductions_vs_json else 0.0
    
    # Confidence intervals
    ci_reduction_nl = calculate_confidence_interval(vn_reductions_vs_nl)
    ci_reduction_json = calculate_confidence_interval(vn_reductions_vs_json)
    
    # Effect sizes
    nl_tokens = [r["comparison"]["nl_tokens"] for r in results if "comparison" in r]
    json_tokens = [r["comparison"]["json_tokens"] for r in results if "comparison" in r]
    vn_tokens = [r["comparison"]["vn_tokens"] for r in results if "comparison" in r]
    
    effect_vn_vs_nl = calculate_effect_size(vn_tokens, nl_tokens) if vn_tokens and nl_tokens else 0.0
    effect_vn_vs_json = calculate_effect_size(vn_tokens, json_tokens) if vn_tokens and json_tokens else 0.0
    
    # P-values
    p_value_vn_vs_nl = calculate_p_value(vn_tokens, nl_tokens) if vn_tokens and nl_tokens else 1.0
    p_value_vn_vs_json = calculate_p_value(vn_tokens, json_tokens) if vn_tokens and json_tokens else 1.0
    p_value_compliance = calculate_p_value(
        [r["comparison"]["vn_compliance"] for r in results if "comparison" in r],
        [r["comparison"]["json_compliance"] for r in results if "comparison" in r]
    )
    
    return {
        "compliance_rates": {
            "natural_language": nl_compliance,
            "json": json_compliance,
            "vector_native": vn_compliance,
        },
        "token_reduction": {
            "mean_vs_nl": mean_reduction_vs_nl,
            "mean_vs_json": mean_reduction_vs_json,
            "ci_vs_nl": {
                "mean": ci_reduction_nl[0],
                "lower": ci_reduction_nl[1],
                "upper": ci_reduction_nl[2],
            },
            "ci_vs_json": {
                "mean": ci_reduction_json[0],
                "lower": ci_reduction_json[1],
                "upper": ci_reduction_json[2],
            },
        },
        "effect_sizes": {
            "vn_vs_nl": effect_vn_vs_nl,
            "vn_vs_json": effect_vn_vs_json,
        },
        "p_values": {
            "vn_vs_nl_tokens": p_value_vn_vs_nl,
            "vn_vs_json_tokens": p_value_vn_vs_json,
            "vn_vs_json_compliance": p_value_compliance,
        },
        "statistical_significance": {
            "vn_vs_nl_tokens": p_value_vn_vs_nl < 0.05,
            "vn_vs_json_tokens": p_value_vn_vs_json < 0.05,
            "vn_vs_json_compliance": p_value_compliance < 0.05,
        },
        "sample_size": len(results),
    }

