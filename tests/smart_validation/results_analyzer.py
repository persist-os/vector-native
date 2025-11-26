"""
Results Analyzer for Smart Validation Framework

Generates comprehensive validation report with all metrics, statistical analysis,
and go/no-go decision for further validation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .metrics_calculator import calculate_all_metrics
from .adaptive_tester import evaluate_phase1_results, generate_go_no_go_decision


def generate_validation_report(
    phase1_results: List[Dict[str, Any]],
    phase2_results: Optional[List[Dict[str, Any]]] = None,
    total_calls: int = 0,
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    scenarios_tested: int = 0
) -> Dict[str, Any]:
    """
    Generate comprehensive validation report.
    
    Args:
        phase1_results: Phase 1 comparison results
        phase2_results: Optional Phase 2 symbol effects results
        total_calls: Total API calls made
        model: Model used
        temperature: Temperature used
        scenarios_tested: Number of scenarios tested
    
    Returns:
        Complete validation report dict
    """
    # Calculate Phase 1 metrics
    phase1_metrics = calculate_all_metrics(phase1_results)
    
    # Evaluate Phase 1
    phase1_evaluation = evaluate_phase1_results(phase1_results)
    go_no_go = generate_go_no_go_decision(phase1_evaluation)
    
    # Phase 2 metrics (if available)
    phase2_metrics = None
    if phase2_results:
        bullet_compliances = [r["symbol_bullet"]["compliance"] for r in phase2_results]
        star_compliances = [r["symbol_star"]["compliance"] for r in phase2_results]
        
        from .metrics_calculator import calculate_p_value, calculate_effect_size, calculate_confidence_interval
        
        phase2_metrics = {
            "bullet_compliance": sum(bullet_compliances) / len(bullet_compliances) if bullet_compliances else 0.0,
            "star_compliance": sum(star_compliances) / len(star_compliances) if star_compliances else 0.0,
            "p_value": calculate_p_value(bullet_compliances, star_compliances),
            "effect_size": calculate_effect_size(bullet_compliances, star_compliances),
            "bullet_ci": calculate_confidence_interval(bullet_compliances),
            "star_ci": calculate_confidence_interval(star_compliances),
        }
        phase2_metrics["significant"] = phase2_metrics["p_value"] < 0.05
    
    # Build report
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "temperature": temperature,
            "scenarios_tested": scenarios_tested,
            "total_api_calls": total_calls,
            "call_limit": 100,
            "call_efficiency": f"{(100 - total_calls) / 100 * 100:.1f}% under limit" if total_calls <= 100 else "EXCEEDED",
        },
        "phase1": {
            "results_count": len(phase1_results),
            "metrics": phase1_metrics,
            "evaluation": phase1_evaluation,
            "go_no_go": go_no_go,
        },
        "phase2": {
            "executed": phase2_results is not None,
            "results_count": len(phase2_results) if phase2_results else 0,
            "metrics": phase2_metrics,
        } if phase2_results else {
            "executed": False,
            "reason": go_no_go.get("recommendation", "Phase 1 not promising"),
        },
        "summary": {
            "vn_compliance": phase1_metrics.get("compliance_rates", {}).get("vector_native", 0.0),
            "vn_token_reduction": phase1_metrics.get("token_reduction", {}).get("mean_vs_nl", 0.0),
            "statistical_significance": phase1_metrics.get("statistical_significance", {}).get("vn_vs_nl_tokens", False),
            "decision": go_no_go.get("decision", "unknown"),
            "recommendation": go_no_go.get("recommendation", ""),
        },
        "conclusions": {
            "format_comparison": _format_comparison_conclusion(phase1_metrics),
            "symbol_effects": _symbol_effects_conclusion(phase2_metrics) if phase2_metrics else "Not tested (Phase 1 not promising)",
            "next_steps": go_no_go.get("next_steps", []),
        }
    }
    
    return report


def _format_comparison_conclusion(metrics: Dict[str, Any]) -> str:
    """Generate conclusion for format comparison."""
    vn_compliance = metrics.get("compliance_rates", {}).get("vector_native", 0.0)
    json_compliance = metrics.get("compliance_rates", {}).get("json", 0.0)
    reduction = metrics.get("token_reduction", {}).get("mean_vs_nl", 0.0)
    p_value = metrics.get("p_values", {}).get("vn_vs_nl_tokens", 1.0)
    significant = metrics.get("statistical_significance", {}).get("vn_vs_nl_tokens", False)
    
    if vn_compliance > 0.85 and reduction > 40.0 and significant:
        return (
            f"Vector-Native significantly outperforms JSON and Natural Language: "
            f"{vn_compliance:.1%} compliance (vs {json_compliance:.1%} for JSON), "
            f"{reduction:.1f}% token reduction (p={p_value:.4f})."
        )
    elif vn_compliance > json_compliance and reduction > 0:
        return (
            f"Vector-Native shows improvement: {vn_compliance:.1%} compliance (vs {json_compliance:.1%} for JSON), "
            f"{reduction:.1f}% token reduction, but not statistically significant (p={p_value:.4f})."
        )
    else:
        return (
            f"Vector-Native does not show clear advantage: {vn_compliance:.1%} compliance (vs {json_compliance:.1%} for JSON), "
            f"{reduction:.1f}% token reduction. Results not statistically significant (p={p_value:.4f})."
        )


def _symbol_effects_conclusion(metrics: Dict[str, Any]) -> str:
    """Generate conclusion for symbol effects."""
    bullet_compliance = metrics.get("bullet_compliance", 0.0)
    star_compliance = metrics.get("star_compliance", 0.0)
    p_value = metrics.get("p_value", 1.0)
    significant = metrics.get("significant", False)
    
    if significant and bullet_compliance > star_compliance:
        return (
            f"● symbol significantly outperforms * symbol: "
            f"{bullet_compliance:.1%} vs {star_compliance:.1%} compliance (p={p_value:.4f})."
        )
    elif bullet_compliance > star_compliance:
        return (
            f"● symbol shows improvement over * symbol: "
            f"{bullet_compliance:.1%} vs {star_compliance:.1%} compliance, but not statistically significant (p={p_value:.4f})."
        )
    else:
        return (
            f"Symbol choice does not significantly affect compliance: "
            f"● {bullet_compliance:.1%} vs * {star_compliance:.1%} (p={p_value:.4f})."
        )


def save_report(
    report: Dict[str, Any],
    output_dir: Optional[Path] = None,
    filename: Optional[str] = None
) -> Path:
    """
    Save validation report to JSON file.
    
    Args:
        report: Validation report dict
        output_dir: Output directory (default: test_results/)
        filename: Output filename (default: auto-generated with timestamp)
    
    Returns:
        Path to saved file
    """
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "test_results"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model = report["metadata"]["model"]
        total_calls = report["metadata"]["total_api_calls"]
        vn_compliance = report["summary"]["vn_compliance"]
        decision = report["summary"]["decision"]
        
        filename = (
            f"smart_validation_"
            f"{timestamp}_"
            f"model-{model}_"
            f"calls-{total_calls}_"
            f"compliance-{vn_compliance:.0f}pct_"
            f"decision-{decision}.json"
        )
    
    output_path = output_dir / filename
    
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    return output_path


def print_report_summary(report: Dict[str, Any]) -> None:
    """Print human-readable summary of validation report."""
    metadata = report["metadata"]
    summary = report["summary"]
    phase1 = report["phase1"]
    
    print(f"\n{'='*80}")
    print("VALIDATION REPORT SUMMARY")
    print(f"{'='*80}")
    print(f"Model: {metadata['model']}")
    print(f"Temperature: {metadata['temperature']}")
    print(f"Scenarios Tested: {metadata['scenarios_tested']}")
    print(f"Total API Calls: {metadata['total_api_calls']} / {metadata['call_limit']}")
    print(f"Call Efficiency: {metadata['call_efficiency']}")
    
    print(f"\nPhase 1 Results:")
    print(f"  VN Compliance: {summary['vn_compliance']:.1%}")
    print(f"  Token Reduction: {summary['vn_token_reduction']:.1f}%")
    print(f"  Statistical Significance: {summary['statistical_significance']}")
    print(f"  Decision: {summary['decision'].upper()}")
    
    print(f"\nConclusions:")
    print(f"  Format Comparison: {report['conclusions']['format_comparison']}")
    print(f"  Symbol Effects: {report['conclusions']['symbol_effects']}")
    
    print(f"\nNext Steps:")
    for step in report['conclusions']['next_steps']:
        print(f"  - {step}")
    
    print(f"\n{'='*80}")

