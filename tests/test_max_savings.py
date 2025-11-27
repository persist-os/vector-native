"""
Max Savings Token Reduction Test Suite

Tests the maximum token reduction scenarios where Vector Native shows 60-80% savings.
These scenarios force verbose prose in baseline (transitions, justifications, explanations)
while VN format eliminates all filler words.

Proven results:
- Step-by-Step Instructions: 65% savings
- Requirements Specification: 74% savings  
- State Machine Transitions: 80% savings (best)
- Average: 73% savings

Prompt Variants (see prompts/vn_base/):
- minimal: ~40% compliance, ~95% token savings (best for testing)
- standard: ~80% compliance, ~89% token savings (best for production)

Usage:
    python tests/test_max_savings.py                     # Run all scenarios (minimal)
    python tests/test_max_savings.py --variant standard  # Run with standard variant
    python tests/test_max_savings.py --scenario 2        # Run single scenario (State Machine)
    python tests/test_max_savings.py --all-variants      # Test both variants
    python tests/test_max_savings.py --evaluate          # Run with LLM quality evaluation
    python tests/test_max_savings.py --evaluate --judge-model gpt-4o  # Specify judge
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Optional: Quality evaluation imports (only loaded if --evaluate flag is used)
EVALUATION_AVAILABLE = False
try:
    from evaluation import LLMJudge, LLMClient, StatisticalAnalyzer, EvaluationScore
    EVALUATION_AVAILABLE = True
except ImportError:
    pass  # Evaluation module not available, quality scoring disabled

# Load environment variables
load_dotenv()

# Paths
TESTS_DIR = Path(__file__).parent
REPO_DIR = TESTS_DIR.parent
PROMPTS_DIR = REPO_DIR / "prompts" / "vn_base"
SCENARIOS_FILE = TESTS_DIR / "test_cases" / "max_savings_scenarios.json"
RESULTS_DIR = TESTS_DIR / "test_results"

# Available VN prompt variants (see prompts/vn_base/README.md)
VN_PROMPT_FILES = {
    "minimal": PROMPTS_DIR / "minimal.yaml",   # ~40% compliance, ~95% savings
    "standard": PROMPTS_DIR / "standard.yaml", # ~80% compliance, ~89% savings
}


def load_vn_prompt(variant: str = "minimal") -> str:
    """
    Load Vector Native system prompt from YAML file.
    
    Args:
        variant: "minimal" or "standard"
    
    Returns:
        System prompt string
    """
    if variant not in VN_PROMPT_FILES:
        available = ", ".join(VN_PROMPT_FILES.keys())
        raise ValueError(f"Unknown variant '{variant}'. Available: {available}")
    
    prompt_file = VN_PROMPT_FILES[variant]
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    with open(prompt_file, "r") as f:
        data = yaml.safe_load(f)
    
    return data.get("instructions", "")


def count_tokens_approx(text: str) -> int:
    """Approximate token count (1 token ≈ 4 chars for English)."""
    return len(text) // 4


def load_max_savings_scenarios(path: Path = SCENARIOS_FILE) -> List[Dict[str, Any]]:
    """Load max savings scenarios from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def get_baseline_response(
    client: OpenAI, prompt: str, model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Get baseline (verbose prose) response from OpenAI.
    
    Uses a system prompt that encourages detailed, flowing prose.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a detailed technical writer. "
                    "Write in complete sentences with thorough explanations. "
                    "Use transitional phrases and provide context for each point. "
                    "Be comprehensive and professional."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,  # Slightly higher for more natural prose
    )
    
    content = response.choices[0].message.content
    usage = response.usage
    
    return {
        "response": content,
        "tokens_used": usage.total_tokens,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
    }


def get_vn_response(
    client: OpenAI,
    prompt: str,
    system_prompt: str,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Get Vector Native response from OpenAI.
    
    Uses VN system prompt for structured output.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,  # Low for compliance
    )
    
    content = response.choices[0].message.content
    usage = response.usage
    
    # Simple format detection (VN if starts with ● or ⊕)
    is_vn = content.strip().startswith("●") or content.strip().startswith("⊕")
    
    return {
        "response": content,
        "tokens_used": usage.total_tokens,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "format": "vector_native" if is_vn else "natural_language",
    }


def measure_vn_compliance(text: str) -> float:
    """
    Measure VN compliance as percentage of lines starting with ● or ⊕.
    """
    if not text or len(text.strip()) == 0:
        return 0.0
    
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return 0.0
    
    vn_lines = sum(1 for line in lines if line.startswith("●") or line.startswith("⊕"))
    return vn_lines / len(lines)


def test_max_savings_scenario(
    scenario: Dict[str, Any],
    client: OpenAI,
    variant: str = "strict",
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Test a single max savings scenario.
    
    Args:
        scenario: Scenario dict with baseline_prompt and vn_prompt
        client: OpenAI client
        variant: VN prompt variant (strict, balanced, minimal)
        model: Model to use
    
    Returns:
        Test result dict with baseline, treatment, and savings metrics
    """
    print(f"\n{'='*80}")
    print(f"Testing: {scenario['name']} (variant: {variant})")
    print(f"Target savings: {scenario.get('target_savings_pct', 'N/A')}%")
    print(f"{'='*80}")
    
    # Get baseline (verbose prose) response
    print("\n[1/2] Getting baseline (verbose prose) response...")
    baseline_result = get_baseline_response(client, scenario["baseline_prompt"], model)
    baseline_completion = baseline_result["completion_tokens"]
    
    print(f"  Completion tokens: {baseline_completion}")
    print(f"  Response preview: {baseline_result['response'][:200]}...")
    
    # Get VN response
    print(f"\n[2/2] Getting Vector Native response ({variant})...")
    vn_system_prompt = load_vn_prompt(variant)
    vn_result = get_vn_response(client, scenario["vn_prompt"], vn_system_prompt, model)
    vn_completion = vn_result["completion_tokens"]
    
    compliance = measure_vn_compliance(vn_result["response"])
    
    print(f"  Completion tokens: {vn_completion}")
    print(f"  VN Compliance: {compliance:.1%}")
    print(f"  Response preview: {vn_result['response'][:200]}...")
    
    # Calculate savings
    savings_pct = ((baseline_completion - vn_completion) / baseline_completion * 100) if baseline_completion > 0 else 0
    target_savings = scenario.get("target_savings_pct", 50)
    met_target = savings_pct >= target_savings
    
    print(f"\n📊 Results:")
    print(f"  Savings: {savings_pct:.1f}% (target: {target_savings}%) {'✅' if met_target else '⚠️'}")
    print(f"  Compliance: {compliance:.1%} {'✅' if compliance >= 0.8 else '⚠️'}")
    
    return {
        "scenario_name": scenario["name"],
        "description": scenario.get("description", ""),
        "variant": variant,
        "target_savings_pct": target_savings,
        "baseline": {
            "prompt": scenario["baseline_prompt"],
            "response": baseline_result["response"],
            "completion_tokens": baseline_completion,
            "total_tokens": baseline_result["tokens_used"],
        },
        "treatment": {
            "prompt": scenario["vn_prompt"],
            "response": vn_result["response"],
            "completion_tokens": vn_completion,
            "total_tokens": vn_result["tokens_used"],
            "compliance": compliance,
            "format": vn_result["format"],
        },
        "results": {
            "savings_pct": round(savings_pct, 2),
            "met_target": met_target,
            "compliance": compliance,
        },
    }


def evaluate_outputs(
    baseline_response: str,
    vn_response: str,
    task: str,
    judge: "LLMJudge"
) -> Dict[str, Any]:
    """
    Evaluate baseline and VN outputs using LLM-as-judge.
    
    Args:
        baseline_response: Baseline (verbose) response
        vn_response: VN format response
        task: Task description
        judge: LLMJudge instance
    
    Returns:
        Dict with baseline and VN scores
    """
    criteria = [
        "Completeness - Does the output cover all required information?",
        "Clarity - Is the output easy to understand?",
        "Accuracy - Is the information correct and precise?",
        "Usefulness - Would this output be useful for the intended purpose?"
    ]
    
    print("  Evaluating baseline output...")
    baseline_score = judge.evaluate(baseline_response, task, criteria)
    
    print("  Evaluating VN output...")
    vn_score = judge.evaluate(vn_response, task, criteria)
    
    return {
        "baseline_score": baseline_score,
        "vn_score": vn_score,
        "quality_preserved": vn_score.overall_score >= baseline_score.overall_score * 0.9
    }


def run_max_savings_tests(
    scenarios: Optional[List[Dict]] = None,
    variants: List[str] = None,
    model: str = "gpt-4o-mini",
    scenario_index: Optional[int] = None,
    evaluate: bool = False,
    judge_model: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    Run max savings test suite.
    
    Args:
        scenarios: List of scenario dicts (loads from file if None)
        variants: List of variants to test (default: ["minimal"])
        model: Model to use
        scenario_index: Optional specific scenario index to run
        evaluate: If True, run LLM-as-judge quality evaluation
        judge_model: Model to use for quality evaluation
    
    Returns:
        Complete test results dict
    """
    if scenarios is None:
        scenarios = load_max_savings_scenarios()
    
    if variants is None:
        variants = ["minimal"]  # Minimal for max savings, standard for compliance
    
    # Filter to single scenario if specified
    if scenario_index is not None:
        if 0 <= scenario_index < len(scenarios):
            scenarios = [scenarios[scenario_index]]
        else:
            raise ValueError(f"Invalid scenario index: {scenario_index}")
    
    # Initialize judge if evaluation is requested
    judge = None
    if evaluate:
        if not EVALUATION_AVAILABLE:
            print("\n⚠️ Evaluation module not available. Install with:")
            print("   pip install scipy anthropic google-generativeai")
            print("   Continuing without quality evaluation...\n")
            evaluate = False
        else:
            print("\n🔬 Quality evaluation enabled")
            print(f"   Judge model: {judge_model}")
            llm_client = LLMClient()
            judge = LLMJudge(llm_client=llm_client, judge_model=judge_model, executor_model=model)
    
    print("="*80)
    print("Vector Native Max Savings Test Suite")
    print("="*80)
    print(f"\nScenarios: {len(scenarios)}")
    print(f"Variants: {', '.join(variants)}")
    print(f"Model: {model}")
    if evaluate:
        print(f"Quality evaluation: ✅ (judge: {judge_model})")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found. Set it in .env file.")
    
    print(f"\n✅ API key found: {api_key[:10]}...")
    
    # Initialize client
    client = OpenAI(api_key=api_key)
    
    # Run tests
    all_results = []
    
    for variant in variants:
        print(f"\n{'#'*80}")
        print(f"# Variant: {variant.upper()}")
        print(f"{'#'*80}")
        
        for scenario in scenarios:
            try:
                result = test_max_savings_scenario(scenario, client, variant, model)
                
                # Add quality evaluation if enabled
                if evaluate and judge:
                    print("\n  [3/3] Running quality evaluation...")
                    eval_result = evaluate_outputs(
                        result["baseline"]["response"],
                        result["treatment"]["response"],
                        scenario.get("description", scenario["name"]),
                        judge
                    )
                    result["evaluation"] = {
                        "baseline_score": eval_result["baseline_score"].overall_score,
                        "baseline_reasoning": eval_result["baseline_score"].reasoning,
                        "vn_score": eval_result["vn_score"].overall_score,
                        "vn_reasoning": eval_result["vn_score"].reasoning,
                        "quality_preserved": eval_result["quality_preserved"],
                    }
                    result["results"]["quality_preserved"] = eval_result["quality_preserved"]
                    
                    # Print evaluation summary
                    print(f"  📊 Quality scores:")
                    print(f"     Baseline: {eval_result['baseline_score'].overall_score:.1f}/10")
                    print(f"     VN: {eval_result['vn_score'].overall_score:.1f}/10")
                    print(f"     Quality preserved: {'✅' if eval_result['quality_preserved'] else '⚠️'}")
                
                all_results.append(result)
            except Exception as e:
                print(f"\n❌ Error testing {scenario['name']}: {e}")
                import traceback
                traceback.print_exc()
                all_results.append({
                    "scenario_name": scenario["name"],
                    "variant": variant,
                    "error": str(e),
                    "results": {"savings_pct": 0, "met_target": False, "compliance": 0},
                })
    
    # Calculate summary
    successful = [r for r in all_results if "error" not in r]
    
    if successful:
        avg_savings = sum(r["results"]["savings_pct"] for r in successful) / len(successful)
        avg_compliance = sum(r["results"]["compliance"] for r in successful) / len(successful)
        met_targets = sum(1 for r in successful if r["results"]["met_target"])
        best_result = max(successful, key=lambda r: r["results"]["savings_pct"])
        
        # Quality metrics (if evaluation was run)
        evaluated = [r for r in successful if "evaluation" in r]
        if evaluated:
            avg_baseline_quality = sum(r["evaluation"]["baseline_score"] for r in evaluated) / len(evaluated)
            avg_vn_quality = sum(r["evaluation"]["vn_score"] for r in evaluated) / len(evaluated)
            quality_preserved_count = sum(1 for r in evaluated if r["evaluation"]["quality_preserved"])
        else:
            avg_baseline_quality = None
            avg_vn_quality = None
            quality_preserved_count = 0
    else:
        avg_savings = 0
        avg_compliance = 0
        met_targets = 0
        best_result = None
        avg_baseline_quality = None
        avg_vn_quality = None
        quality_preserved_count = 0
        evaluated = []
    
    summary = {
        "total_tests": len(all_results),
        "successful_tests": len(successful),
        "avg_savings_pct": round(avg_savings, 2),
        "avg_compliance": round(avg_compliance, 3),
        "tests_meeting_target": met_targets,
        "best_scenario": best_result["scenario_name"] if best_result else None,
        "best_savings_pct": best_result["results"]["savings_pct"] if best_result else 0,
    }
    
    # Add quality metrics to summary if available
    if evaluated:
        summary["quality_evaluation"] = {
            "tests_evaluated": len(evaluated),
            "avg_baseline_quality": round(avg_baseline_quality, 2) if avg_baseline_quality else None,
            "avg_vn_quality": round(avg_vn_quality, 2) if avg_vn_quality else None,
            "quality_preserved_count": quality_preserved_count,
            "quality_preserved_pct": round(quality_preserved_count / len(evaluated) * 100, 1) if evaluated else 0,
        }
    
    # Print summary
    print(f"\n{'='*80}")
    print("MAX SAVINGS TEST SUMMARY")
    print(f"{'='*80}")
    print(f"\n📊 Token Savings:")
    print(f"  Tests: {len(successful)}/{len(all_results)} successful")
    print(f"  Average savings: {avg_savings:.1f}%")
    print(f"  Average compliance: {avg_compliance:.1%}")
    print(f"  Met targets: {met_targets}/{len(successful)}")
    
    if best_result:
        print(f"\n🏆 Best: {best_result['scenario_name']} ({best_result['results']['savings_pct']:.1f}%)")
    
    # Print quality metrics if available
    if evaluated:
        print(f"\n🔬 Quality Evaluation:")
        print(f"  Tests evaluated: {len(evaluated)}")
        print(f"  Baseline quality: {avg_baseline_quality:.1f}/10")
        print(f"  VN quality: {avg_vn_quality:.1f}/10")
        print(f"  Quality preserved: {quality_preserved_count}/{len(evaluated)} ({quality_preserved_count/len(evaluated)*100:.0f}%)")
        
        quality_diff = avg_vn_quality - avg_baseline_quality if avg_baseline_quality else 0
        if quality_diff >= 0:
            print(f"\n✅ Quality maintained or improved (+{quality_diff:.1f})")
        elif quality_diff >= -0.5:
            print(f"\n⚠️ Minor quality reduction ({quality_diff:.1f})")
        else:
            print(f"\n❌ Significant quality reduction ({quality_diff:.1f})")
    
    # Determine success
    if avg_savings >= 60:
        print(f"\n✅✅✅ SUCCESS: {avg_savings:.1f}% average savings achieved!")
    elif avg_savings >= 50:
        print(f"\n✅ GOOD: {avg_savings:.1f}% average savings (meets 50% target)")
    else:
        print(f"\n⚠️ Below target: {avg_savings:.1f}% average savings")
    
    print("="*80)
    
    return {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "variants_tested": variants,
            "scenarios_count": len(scenarios),
        },
        "summary": summary,
        "results": all_results,
    }


def save_results(results: Dict[str, Any], filename: Optional[str] = None) -> str:
    """Save results to JSON file."""
    RESULTS_DIR.mkdir(exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        savings = results["summary"]["avg_savings_pct"]
        compliance = int(results["summary"]["avg_compliance"] * 100)
        filename = f"max_savings_{timestamp}_savings-{savings:.0f}pct_compliance-{compliance}pct.json"
    
    filepath = RESULTS_DIR / filename
    
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {filepath}")
    return str(filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Vector Native max savings tests")
    parser.add_argument("--variant", default="minimal", help="VN variant (minimal, standard)")
    parser.add_argument("--scenario", type=int, help="Run specific scenario by index (0, 1, 2)")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--all-variants", action="store_true", help="Test all variants")
    parser.add_argument("--evaluate", action="store_true", help="Run LLM quality evaluation")
    parser.add_argument("--judge-model", default="gpt-4o", help="Model for quality evaluation")
    
    args = parser.parse_args()
    
    variants = ["minimal", "standard"] if args.all_variants else [args.variant]
    
    results = run_max_savings_tests(
        variants=variants,
        model=args.model,
        scenario_index=args.scenario,
        evaluate=args.evaluate,
        judge_model=args.judge_model,
    )
    
    save_results(results)
    print("\n✅ Max savings tests complete!")

