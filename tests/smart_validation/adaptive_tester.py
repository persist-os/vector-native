"""
Adaptive Tester for Smart Validation Framework

Evaluates Phase 1 results and determines if Phase 2 (symbol effects) should proceed.
Implements go/no-go decision logic per innovation proposal.
"""

from typing import Dict, List, Any, Optional
from .metrics_calculator import calculate_all_metrics


def evaluate_phase1_results(
    phase1_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluate Phase 1 results and determine if Phase 2 should proceed.
    
    Success Criteria (ALL must be met):
    - VN compliance >85%
    - VN token reduction >40% on average
    - Statistical significance (p < 0.05)
    
    Args:
        phase1_results: List of Phase 1 comparison results
    
    Returns:
        {
            "should_proceed": bool,
            "reason": str,
            "metrics": {...},
            "criteria_met": {
                "compliance": bool,
                "token_reduction": bool,
                "statistical_significance": bool,
            }
        }
    """
    if not phase1_results:
        return {
            "should_proceed": False,
            "reason": "No Phase 1 results available",
            "metrics": {},
            "criteria_met": {
                "compliance": False,
                "token_reduction": False,
                "statistical_significance": False,
            }
        }
    
    # Calculate metrics
    metrics = calculate_all_metrics(phase1_results)
    
    # Check criteria
    vn_compliance = metrics.get("compliance_rates", {}).get("vector_native", 0.0)
    mean_reduction = metrics.get("token_reduction", {}).get("mean_vs_nl", 0.0)
    p_value = metrics.get("p_values", {}).get("vn_vs_nl_tokens", 1.0)
    is_significant = metrics.get("statistical_significance", {}).get("vn_vs_nl_tokens", False)
    
    criteria_met = {
        "compliance": vn_compliance > 0.85,
        "token_reduction": mean_reduction > 40.0,
        "statistical_significance": p_value < 0.05 and is_significant,
    }
    
    all_met = all(criteria_met.values())
    
    if all_met:
        reason = (
            f"All criteria met: VN compliance {vn_compliance:.1%}, "
            f"token reduction {mean_reduction:.1f}%, p-value {p_value:.4f}"
        )
    else:
        failed = [k for k, v in criteria_met.items() if not v]
        reason = f"Criteria not met: {', '.join(failed)}"
    
    return {
        "should_proceed": all_met,
        "reason": reason,
        "metrics": metrics,
        "criteria_met": criteria_met,
        "thresholds": {
            "compliance_required": 0.85,
            "compliance_actual": vn_compliance,
            "reduction_required": 40.0,
            "reduction_actual": mean_reduction,
            "p_value_required": 0.05,
            "p_value_actual": p_value,
        }
    }


def generate_go_no_go_decision(
    phase1_evaluation: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate go/no-go decision with recommendations.
    
    Args:
        phase1_evaluation: Result from evaluate_phase1_results()
    
    Returns:
        {
            "decision": "go" or "no_go",
            "recommendation": str,
            "next_steps": List[str],
            "expansion_plan": Optional[Dict] (if go)
        }
    """
    should_proceed = phase1_evaluation.get("should_proceed", False)
    metrics = phase1_evaluation.get("metrics", {})
    criteria_met = phase1_evaluation.get("criteria_met", {})
    
    if should_proceed:
        decision = "go"
        recommendation = (
            "Phase 1 results are promising. Proceed with Phase 2 (symbol effects test). "
            "Consider expanding to 360 calls (20 scenarios × 3 formats × 2 models × 1 temp × 3 trials) "
            "for comprehensive validation."
        )
        next_steps = [
            "Execute Phase 2: Symbol effects test (10 calls)",
            "If Phase 2 successful, consider expanded validation (360 calls)",
            "Generate final validation report",
        ]
        expansion_plan = {
            "scenarios": 20,
            "formats": 3,
            "models": 2,
            "temperature": 1,
            "trials": 3,
            "total_calls": 360,
        }
    else:
        decision = "no_go"
        recommendation = (
            "Phase 1 results do not meet success criteria. "
            "Do not proceed with Phase 2. "
            "Consider refining system prompts or adjusting validation approach."
        )
        next_steps = [
            "Analyze failure modes in Phase 1 results",
            "Refine Vector-Native system prompts",
            "Re-run Phase 1 with improved prompts",
            "Document findings and adjust claims if necessary",
        ]
        expansion_plan = None
    
    return {
        "decision": decision,
        "recommendation": recommendation,
        "next_steps": next_steps,
        "expansion_plan": expansion_plan,
        "phase1_summary": {
            "compliance": metrics.get("compliance_rates", {}).get("vector_native", 0.0),
            "token_reduction": metrics.get("token_reduction", {}).get("mean_vs_nl", 0.0),
            "p_value": metrics.get("p_values", {}).get("vn_vs_nl_tokens", 1.0),
            "criteria_met": criteria_met,
        }
    }

