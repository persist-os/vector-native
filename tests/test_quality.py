"""
VN Quality-Focused Test Suite

Tests Vector Native outputs for quality preservation, not just token savings.

Focus areas:
1. Semantic preservation - Does VN retain all original meaning?
2. Information density - Is content efficiently conveyed?
3. Roundtrip fidelity - Can VN be accurately decoded back to English?
4. Judge-evaluated quality scores

Usage:
    python tests/test_quality.py                          # Run all quality tests
    python tests/test_quality.py --test semantic          # Run specific test
    python tests/test_quality.py --judge-model gpt-4o     # Specify judge model
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

# Load environment variables
load_dotenv()

# Paths
TESTS_DIR = Path(__file__).parent
REPO_DIR = TESTS_DIR.parent
PROMPTS_DIR = REPO_DIR / "prompts" / "vn_base"
RESULTS_DIR = TESTS_DIR / "test_results"

# Import evaluation module
try:
    from evaluation import LLMJudge, LLMClient, StatisticalAnalyzer, EvaluationScore
    EVALUATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Evaluation module not available: {e}")
    print("Install dependencies with: pip install scipy anthropic google-generativeai")
    EVALUATION_AVAILABLE = False


# Test scenarios focused on quality (not max savings)
QUALITY_SCENARIOS = [
    {
        "name": "Technical Documentation",
        "description": "Convert technical documentation to VN format",
        "content": """
The authentication system uses JWT tokens with RS256 signing. Tokens expire after 24 hours
and must be refreshed using the /auth/refresh endpoint. The system maintains a blacklist
of revoked tokens in Redis with automatic TTL cleanup. Rate limiting is enforced at 100
requests per minute per user, with burst allowance of 150 for the first 10 seconds.
Failed authentication attempts trigger exponential backoff starting at 1 second.
""",
        "criteria": [
            "All technical details preserved (JWT, RS256, 24h, Redis, 100/min, 150 burst)",
            "Relationships between concepts maintained",
            "No semantic drift or hallucination"
        ]
    },
    {
        "name": "Meeting Notes",
        "description": "Convert meeting notes to VN format",
        "content": """
Q3 Planning Meeting - Product Team
Date: 2024-11-15
Attendees: Sarah (PM), Mike (Tech Lead), Lisa (Design), Tom (QA)

Key Decisions:
1. Mobile app MVP launches January 15th (firm deadline)
2. Desktop redesign pushed to Q2 (resource constraints)
3. API v2 migration starts December 1st (2-week deprecation notice)

Action Items:
- Sarah: Finalize feature list by Nov 20
- Mike: Architecture review by Nov 22
- Lisa: Mockups complete by Nov 25
- Tom: Test plan ready by Nov 28

Blockers:
- Third-party API rate limits (need enterprise plan)
- Design system updates blocking mobile work
""",
        "criteria": [
            "All dates and deadlines preserved",
            "All names and roles correct",
            "All action items and blockers captured"
        ]
    },
    {
        "name": "Research Summary",
        "description": "Convert research findings to VN format",
        "content": """
User Research Summary: Mobile App Onboarding

Sample: 127 users, 18-54 age range, 60% first-time users
Method: Remote usability testing + post-session interviews
Duration: September 2024

Key Findings:
1. 73% of users completed onboarding in under 3 minutes (target: 5 min)
2. Step 3 (permission requests) had highest dropout: 18% abandoned
3. Users strongly prefer progressive disclosure (87% positive sentiment)
4. Tutorial video watched by only 12% - most skipped immediately

Recommendations:
- Defer non-essential permissions to first-use context
- Replace video with interactive walkthrough
- Add skip option for experienced users
- Implement progress indicator

Statistical Notes:
- Confidence level: 95%
- Margin of error: ±8.5%
- Significant correlation between completion rate and age (r=0.42)
""",
        "criteria": [
            "All statistics preserved exactly (73%, 18%, 87%, 12%, etc.)",
            "Sample size and methodology correct",
            "Recommendations complete and accurate"
        ]
    }
]


def load_vn_prompt(variant: str = "standard") -> str:
    """Load VN system prompt from YAML file."""
    prompt_file = PROMPTS_DIR / f"{variant}.yaml"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    with open(prompt_file, "r") as f:
        data = yaml.safe_load(f)
    
    return data.get("instructions", "")


def translate_to_vn(
    client: OpenAI,
    content: str,
    system_prompt: str,
    model: str = "gpt-4o-mini"
) -> str:
    """Translate content to VN format."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate to Vector Native format:\n\n{content}"},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content


def translate_from_vn(
    client: OpenAI,
    vn_content: str,
    model: str = "gpt-4o-mini"
) -> str:
    """Translate VN content back to English."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a translator. Convert Vector Native notation back to "
                    "clear English prose. Preserve all information accurately. "
                    "Do not add or remove any information."
                ),
            },
            {"role": "user", "content": f"Translate to English:\n\n{vn_content}"},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content


def test_semantic_preservation(
    scenario: Dict[str, Any],
    client: OpenAI,
    judge: LLMJudge,
    model: str = "gpt-4o-mini",
    vn_variant: str = "standard"
) -> Dict[str, Any]:
    """
    Test semantic preservation of VN translation.
    
    Translates content to VN and evaluates whether meaning is preserved.
    """
    print(f"\n{'='*60}")
    print(f"Testing: {scenario['name']}")
    print(f"{'='*60}")
    
    # Translate to VN
    print("\n[1/2] Translating to VN...")
    vn_prompt = load_vn_prompt(vn_variant)
    vn_output = translate_to_vn(client, scenario["content"], vn_prompt, model)
    
    print(f"  VN output preview: {vn_output[:200]}...")
    
    # Evaluate VN quality
    print("\n[2/2] Evaluating semantic preservation...")
    score = judge.evaluate_vn_quality(scenario["content"], vn_output)
    
    print(f"\n📊 Results:")
    print(f"  Overall score: {score.overall_score:.1f}/10")
    print(f"  Reasoning: {score.reasoning[:200]}...")
    
    return {
        "scenario_name": scenario["name"],
        "test_type": "semantic_preservation",
        "original_content": scenario["content"],
        "vn_output": vn_output,
        "score": score.overall_score,
        "criterion_scores": score.criterion_scores,
        "reasoning": score.reasoning,
        "passed": score.overall_score >= 7.0  # 7/10 threshold
    }


def test_roundtrip_fidelity(
    scenario: Dict[str, Any],
    client: OpenAI,
    judge: LLMJudge,
    model: str = "gpt-4o-mini",
    vn_variant: str = "standard"
) -> Dict[str, Any]:
    """
    Test roundtrip fidelity: Original → VN → English.
    
    Measures how accurately VN can encode and decode information.
    """
    print(f"\n{'='*60}")
    print(f"Testing Roundtrip: {scenario['name']}")
    print(f"{'='*60}")
    
    # Original → VN
    print("\n[1/3] Translating to VN...")
    vn_prompt = load_vn_prompt(vn_variant)
    vn_output = translate_to_vn(client, scenario["content"], vn_prompt, model)
    
    # VN → English
    print("[2/3] Translating back to English...")
    reconstructed = translate_from_vn(client, vn_output, model)
    
    # Evaluate roundtrip
    print("[3/3] Evaluating roundtrip fidelity...")
    score = judge.evaluate_roundtrip(
        scenario["content"],
        vn_output,
        reconstructed
    )
    
    print(f"\n📊 Results:")
    print(f"  Fidelity score: {score.overall_score:.1f}/10")
    print(f"  Reasoning: {score.reasoning[:200]}...")
    
    return {
        "scenario_name": scenario["name"],
        "test_type": "roundtrip_fidelity",
        "original_content": scenario["content"],
        "vn_intermediate": vn_output,
        "reconstructed_content": reconstructed,
        "score": score.overall_score,
        "criterion_scores": score.criterion_scores,
        "reasoning": score.reasoning,
        "passed": score.overall_score >= 7.0
    }


def test_information_density(
    scenario: Dict[str, Any],
    client: OpenAI,
    model: str = "gpt-4o-mini",
    vn_variant: str = "standard"
) -> Dict[str, Any]:
    """
    Test information density: tokens per meaningful unit.
    
    Measures compression efficiency while preserving content.
    """
    print(f"\n{'='*60}")
    print(f"Testing Information Density: {scenario['name']}")
    print(f"{'='*60}")
    
    # Translate to VN
    print("\n[1/2] Translating to VN...")
    vn_prompt = load_vn_prompt(vn_variant)
    vn_output = translate_to_vn(client, scenario["content"], vn_prompt, model)
    
    # Approximate token counts
    original_tokens = len(scenario["content"]) // 4
    vn_tokens = len(vn_output) // 4
    
    # Count information units (crude: count lines with actual content)
    original_lines = [l for l in scenario["content"].split('\n') if l.strip()]
    vn_lines = [l for l in vn_output.split('\n') if l.strip()]
    
    # Calculate metrics
    compression_ratio = vn_tokens / original_tokens if original_tokens > 0 else 1
    density_improvement = (1 - compression_ratio) * 100
    
    print(f"\n📊 Results:")
    print(f"  Original tokens: ~{original_tokens}")
    print(f"  VN tokens: ~{vn_tokens}")
    print(f"  Compression: {density_improvement:.1f}% reduction")
    print(f"  Original lines: {len(original_lines)}")
    print(f"  VN lines: {len(vn_lines)}")
    
    return {
        "scenario_name": scenario["name"],
        "test_type": "information_density",
        "original_tokens": original_tokens,
        "vn_tokens": vn_tokens,
        "compression_ratio": round(compression_ratio, 3),
        "density_improvement_pct": round(density_improvement, 1),
        "original_lines": len(original_lines),
        "vn_lines": len(vn_lines),
        "passed": density_improvement >= 30  # 30% minimum compression
    }


def run_quality_tests(
    scenarios: Optional[List[Dict]] = None,
    test_type: str = "all",
    model: str = "gpt-4o-mini",
    judge_model: str = "gpt-4o",
    vn_variant: str = "standard"
) -> Dict[str, Any]:
    """
    Run quality-focused test suite.
    
    Args:
        scenarios: Test scenarios (uses defaults if None)
        test_type: "all", "semantic", "roundtrip", or "density"
        model: Model for VN translation
        judge_model: Model for quality evaluation
        vn_variant: VN prompt variant
    
    Returns:
        Complete test results
    """
    if not EVALUATION_AVAILABLE:
        raise RuntimeError(
            "Evaluation module required. Install with:\n"
            "pip install scipy anthropic google-generativeai"
        )
    
    if scenarios is None:
        scenarios = QUALITY_SCENARIOS
    
    print("="*60)
    print("Vector Native Quality Test Suite")
    print("="*60)
    print(f"\nTest type: {test_type}")
    print(f"Scenarios: {len(scenarios)}")
    print(f"Model: {model}")
    print(f"Judge: {judge_model}")
    print(f"VN variant: {vn_variant}")
    
    # Initialize clients
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY required")
    
    client = OpenAI(api_key=api_key)
    llm_client = LLMClient()
    judge = LLMJudge(llm_client=llm_client, judge_model=judge_model, executor_model=model)
    
    # Run tests
    results = []
    
    for scenario in scenarios:
        try:
            if test_type in ["all", "semantic"]:
                result = test_semantic_preservation(scenario, client, judge, model, vn_variant)
                results.append(result)
            
            if test_type in ["all", "roundtrip"]:
                result = test_roundtrip_fidelity(scenario, client, judge, model, vn_variant)
                results.append(result)
            
            if test_type in ["all", "density"]:
                result = test_information_density(scenario, client, model, vn_variant)
                results.append(result)
                
        except Exception as e:
            print(f"\n❌ Error testing {scenario['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    # Calculate summary
    passed = sum(1 for r in results if r.get("passed", False))
    total = len(results)
    
    semantic_results = [r for r in results if r["test_type"] == "semantic_preservation"]
    roundtrip_results = [r for r in results if r["test_type"] == "roundtrip_fidelity"]
    density_results = [r for r in results if r["test_type"] == "information_density"]
    
    summary = {
        "total_tests": total,
        "passed": passed,
        "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        "by_type": {}
    }
    
    if semantic_results:
        avg_score = sum(r["score"] for r in semantic_results) / len(semantic_results)
        summary["by_type"]["semantic_preservation"] = {
            "count": len(semantic_results),
            "avg_score": round(avg_score, 2),
            "passed": sum(1 for r in semantic_results if r["passed"])
        }
    
    if roundtrip_results:
        avg_score = sum(r["score"] for r in roundtrip_results) / len(roundtrip_results)
        summary["by_type"]["roundtrip_fidelity"] = {
            "count": len(roundtrip_results),
            "avg_score": round(avg_score, 2),
            "passed": sum(1 for r in roundtrip_results if r["passed"])
        }
    
    if density_results:
        avg_compression = sum(r["density_improvement_pct"] for r in density_results) / len(density_results)
        summary["by_type"]["information_density"] = {
            "count": len(density_results),
            "avg_compression_pct": round(avg_compression, 1),
            "passed": sum(1 for r in density_results if r["passed"])
        }
    
    # Print summary
    print(f"\n{'='*60}")
    print("QUALITY TEST SUMMARY")
    print(f"{'='*60}")
    print(f"\n✅ Passed: {passed}/{total} ({summary['pass_rate']}%)")
    
    for test_type, metrics in summary["by_type"].items():
        print(f"\n{test_type}:")
        if "avg_score" in metrics:
            print(f"  Average score: {metrics['avg_score']:.1f}/10")
        if "avg_compression_pct" in metrics:
            print(f"  Average compression: {metrics['avg_compression_pct']:.1f}%")
        print(f"  Passed: {metrics['passed']}/{metrics['count']}")
    
    print("="*60)
    
    return {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "test_type": test_type,
            "model": model,
            "judge_model": judge_model,
            "vn_variant": vn_variant,
        },
        "summary": summary,
        "results": results,
    }


def save_results(results: Dict[str, Any], filename: Optional[str] = None) -> str:
    """Save results to JSON file."""
    RESULTS_DIR.mkdir(exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pass_rate = results["summary"]["pass_rate"]
        filename = f"quality_test_{timestamp}_pass-{pass_rate:.0f}pct.json"
    
    filepath = RESULTS_DIR / filename
    
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {filepath}")
    return str(filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Vector Native quality tests")
    parser.add_argument("--test", default="all", choices=["all", "semantic", "roundtrip", "density"],
                        help="Test type to run")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model for VN translation")
    parser.add_argument("--judge-model", default="gpt-4o", help="Model for evaluation")
    parser.add_argument("--variant", default="standard", help="VN prompt variant")
    
    args = parser.parse_args()
    
    results = run_quality_tests(
        test_type=args.test,
        model=args.model,
        judge_model=args.judge_model,
        vn_variant=args.variant,
    )
    
    save_results(results)
    print("\n✅ Quality tests complete!")

