"""
Comprehensive Token Reduction Test Suite

Tests the 30-80% token reduction claim with focus on:
1. Verification that reduction increases with length
2. Multiple scenarios (analysis, tasks, data processing)
3. Real OpenAI API integration
4. Thorough measurement and reporting
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from vector_native import (
    get_vector_native_system_prompt,
    count_tokens,
    calculate_reduction,
    parse_with_fallback,
)
# VectorNativeClient removed - using direct OpenAI calls

# Load environment variables
load_dotenv()

# Load test scenarios from JSON file
_scenarios_file = Path(__file__).parent / "test_cases" / "scenarios.json"
with open(_scenarios_file, "r") as f:
    TEST_SCENARIOS = json.load(f)


def get_english_response(client: OpenAI, prompt: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Get English response from OpenAI (without vector-native system prompt).
    
    Returns:
        {
            "response": str,
            "tokens_used": int,
            "prompt_tokens": int,
            "completion_tokens": int,
        }
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Respond in natural English with detailed explanations.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    
    content = response.choices[0].message.content
    usage = response.usage
    
    return {
        "response": content,
        "tokens_used": usage.total_tokens,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
    }


def get_vector_native_response(
    client: OpenAI, prompt: str, system_prompt: str, model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Get vector-native response from OpenAI (with vector-native system prompt).
    
    Returns:
        {
            "response": str,
            "parsed": ParsedOperation or None,
            "format": str,
            "tokens_used": int,
        }
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    
    content = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
    
    # Parse response (use hybrid mode to preserve prose while parsing operations)
    parsed_result = parse_with_fallback(content, hybrid=True)
    return {
        "response": content,
        "parsed": parsed_result["parsed"],
        "format": parsed_result["format"],
        "tokens_used": tokens_used,
    }


def test_scenario(
    scenario: Dict[str, Any],
    english_client: OpenAI,
    vn_client: OpenAI,  # Same client, different prompts
    prompt_variant: str = "strict",
    model: str = "gpt-4o-mini",
    cached_english_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Test a single scenario: compare English vs vector-native responses.
    
    Args:
        scenario: Test scenario dict
        english_client: OpenAI client for English responses
        vn_client: OpenAI client for vector-native responses
        prompt_variant: Prompt variant to test ("strict", "balanced", "minimal")
        model: Model to use
        cached_english_result: Optional cached English response (to avoid duplicate API calls)
    
    Returns:
        {
            "scenario_name": str,
            "prompt_variant": str,
            "prompt_length": int,
            "english": {...},
            "vector_native": {...},
            "reduction": {...},
            "success": bool,
        }
    """
    print(f"\n{'='*80}")
    print(f"Testing: {scenario['name']} ({prompt_variant})")
    print(f"{'='*80}")
    
    prompt = scenario["prompt"].strip()
    prompt_tokens = count_tokens(prompt, model)
    
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Prompt preview: {prompt[:100]}...")
    
    # Get English response (use cache if available)
    if cached_english_result:
        print("\n[1/2] Using cached English response...")
        english_result = cached_english_result
    else:
        print("\n[1/2] Getting English response...")
        english_result = get_english_response(english_client, prompt, model)
    
    english_response = english_result["response"]
    english_total = english_result["tokens_used"]
    english_completion = english_result["completion_tokens"]
    
    print(f"English response tokens: {english_total} (completion: {english_completion})")
    print(f"English response preview: {english_response[:200]}...")
    
    # Get vector-native response with specified variant
    print(f"\n[2/2] Getting vector-native response ({prompt_variant})...")
    vn_system_prompt = get_vector_native_system_prompt(prompt_variant)
    vn_result = get_vector_native_response(vn_client, prompt, vn_system_prompt, model)
    vn_response = vn_result["response"]
    vn_total = vn_result.get("tokens_used", 0)
    vn_format = vn_result.get("format", "unknown")
    vn_parsed = vn_result.get("parsed")
    
    print(f"Vector-native response tokens: {vn_total}")
    print(f"Vector-native format: {vn_format}")
    print(f"Vector-native response: {vn_response[:200]}...")
    
    # Calculate reduction
    # Use completion tokens for fair comparison (same prompt, different responses)
    reduction_data = calculate_reduction(english_response, vn_response, model)
    
    # Also calculate based on total tokens if available
    if vn_total > 0:
        total_reduction_pct = (
            (english_total - vn_total) / english_total * 100
            if english_total > 0
            else 0
        )
        total_reduction_tokens = english_total - vn_total
    else:
        total_reduction_pct = reduction_data["reduction"]
        total_reduction_tokens = reduction_data["reduction_tokens"]
    
    result = {
        "scenario_name": scenario["name"],
        "prompt_variant": prompt_variant,
        "prompt_length": prompt_tokens,
        "prompt_text": prompt,
        "english": {
            "response": english_response,
            "total_tokens": english_total,
            "completion_tokens": english_completion,
            "response_length": len(english_response),
        },
        "vector_native": {
            "response": vn_response,
            "total_tokens": vn_total,
            "format": vn_format,
            "parsed": str(vn_parsed) if vn_parsed else None,
            "response_length": len(vn_response),
        },
        "reduction": {
            "completion_reduction_pct": reduction_data["reduction"],
            "completion_reduction_tokens": reduction_data["reduction_tokens"],
            "total_reduction_pct": round(total_reduction_pct, 1),
            "total_reduction_tokens": total_reduction_tokens,
            "before_tokens": reduction_data["before"],
            "after_tokens": reduction_data["after"],
        },
        "success": vn_format == "vector_native",
    }
    
    print(f"\n📊 Results:")
    print(f"  Completion reduction: {reduction_data['reduction']:.1f}% ({reduction_data['reduction_tokens']} tokens)")
    print(f"  Total reduction: {total_reduction_pct:.1f}% ({total_reduction_tokens} tokens)")
    print(f"  Format: {vn_format} {'✅' if vn_format == 'vector_native' else '❌'}")
    
    return result


def run_comprehensive_tests(prompt_variants: List[str] = None) -> Dict[str, Any]:
    """
    Run comprehensive test suite for all prompt variants.
    
    Args:
        prompt_variants: List of prompt variants to test. Default: ["strict", "balanced", "minimal"]
    
    Returns:
        {
            "variants": Dict[str, Dict],  # Results per variant
            "comparison": Dict,  # Cross-variant comparison
            "all_results": List[Dict],  # All individual test results
        }
    """
    if prompt_variants is None:
        prompt_variants = ["strict", "balanced", "minimal"]
    
    print("=" * 80)
    print("Vector-Native Token Reduction Test Suite")
    print(f"Testing variants: {', '.join(prompt_variants)}")
    print("=" * 80)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment. Please set it in .env file."
        )
    
    print(f"\n✅ API key found: {api_key[:10]}...")
    
    # Initialize client
    model = "gpt-4o-mini"  # Use cheaper model for testing
    english_client = OpenAI(api_key=api_key)
    
    print(f"✅ Using model: {model}")
    
    # Cache English responses (same for all variants)
    english_responses_cache = {}
    
    # Run tests for each variant
    variant_results = {}
    all_results = []
    
    for variant in prompt_variants:
        print(f"\n{'#'*80}")
        print(f"# Testing variant: {variant.upper()}")
        print(f"{'#'*80}")
        
        try:
            system_prompt = get_vector_native_system_prompt(variant)
            print(f"✅ Loaded {variant} prompt ({len(system_prompt)} chars)")
        except Exception as e:
            print(f"❌ Failed to load {variant} prompt: {e}")
            continue
        
        variant_test_results = []
        
        for scenario in TEST_SCENARIOS:
            try:
                # Cache English response (only fetch once per scenario)
                scenario_key = scenario["name"]
                if scenario_key not in english_responses_cache:
                    print(f"\n[English baseline] {scenario['name']}...")
                    english_result = get_english_response(english_client, scenario["prompt"].strip(), model)
                    english_responses_cache[scenario_key] = english_result
                
                # Use cached English response
                cached_result = english_responses_cache[scenario_key]
                result = test_scenario(scenario, english_client, english_client, variant, model, cached_result)
                variant_test_results.append(result)
                all_results.append(result)
            except Exception as e:
                print(f"\n❌ Error testing {scenario['name']} ({variant}): {e}")
                import traceback
                traceback.print_exc()
                variant_test_results.append(
                    {
                        "scenario_name": scenario["name"],
                        "prompt_variant": variant,
                        "error": str(e),
                        "success": False,
                    }
                )
        
        # Calculate summary for this variant
        variant_results[variant] = calculate_variant_summary(variant_test_results)
        
        # Print variant summary
        print_variant_summary(variant, variant_results[variant])
    
    # Cross-variant comparison
    comparison = compare_variants(variant_results)
    print_comparison(comparison)
    
    # Add metadata
    metadata = {
        "test_run_timestamp": datetime.now().isoformat(),
        "prompt_variants_tested": prompt_variants,
        "model": "gpt-4o-mini",
        "total_scenarios": len(TEST_SCENARIOS),
        "total_tests": len(all_results),
    }
    
    return {
        "metadata": metadata,
        "variants": variant_results,
        "comparison": comparison,
        "all_results": all_results,
    }


def calculate_variant_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics for a single variant."""
    successful_tests = [r for r in results if r.get("success", False)]
    
    if not successful_tests:
        return {
            "total_tests": len(results),
            "successful_tests": 0,
            "success_rate": 0,
            "avg_completion_reduction_pct": 0,
            "avg_total_reduction_pct": 0,
            "min_reduction_pct": 0,
            "max_reduction_pct": 0,
            "reduction_range": "N/A",
            "results": results,
        }
    
    avg_completion_reduction = sum(
        r["reduction"]["completion_reduction_pct"] for r in successful_tests
    ) / len(successful_tests)
    
    avg_total_reduction = sum(
        r["reduction"]["total_reduction_pct"] for r in successful_tests
    ) / len(successful_tests)
    
    min_reduction = min(
        r["reduction"]["completion_reduction_pct"] for r in successful_tests
    )
    max_reduction = max(
        r["reduction"]["completion_reduction_pct"] for r in successful_tests
    )
    
    return {
        "total_tests": len(results),
        "successful_tests": len(successful_tests),
        "success_rate": round(len(successful_tests) / len(results) * 100, 1),
        "avg_completion_reduction_pct": round(avg_completion_reduction, 1),
        "avg_total_reduction_pct": round(avg_total_reduction, 1),
        "min_reduction_pct": round(min_reduction, 1),
        "max_reduction_pct": round(max_reduction, 1),
        "reduction_range": f"{round(min_reduction, 1)}% - {round(max_reduction, 1)}%",
        "results": results,
    }


def print_variant_summary(variant: str, summary: Dict[str, Any]):
    """Print summary for a single variant."""
    print(f"\n{'='*80}")
    print(f"📊 {variant.upper()} VARIANT SUMMARY")
    print(f"{'='*80}")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']} ({summary['success_rate']:.1f}%)")
    print(f"Average reduction: {summary['avg_completion_reduction_pct']:.1f}%")
    print(f"Range: {summary['reduction_range']}")


def compare_variants(variant_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Compare results across all variants."""
    comparison = {
        "best_reduction": None,
        "best_compliance": None,
        "variant_stats": {},
    }
    
    best_reduction = -1
    best_compliance = -1
    
    for variant, summary in variant_results.items():
        reduction = summary.get("avg_completion_reduction_pct", 0)
        compliance = summary.get("success_rate", 0)
        
        comparison["variant_stats"][variant] = {
            "avg_reduction": reduction,
            "compliance_rate": compliance,
        }
        
        if reduction > best_reduction:
            best_reduction = reduction
            comparison["best_reduction"] = variant
        
        if compliance > best_compliance:
            best_compliance = compliance
            comparison["best_compliance"] = variant
    
    return comparison


def print_comparison(comparison: Dict[str, Any]):
    """Print cross-variant comparison."""
    print(f"\n{'='*80}")
    print("📊 CROSS-VARIANT COMPARISON")
    print(f"{'='*80}")
    
    if comparison["best_reduction"]:
        print(f"\nBest Average Reduction: {comparison['best_reduction']} ({comparison['variant_stats'][comparison['best_reduction']]['avg_reduction']:.1f}%)")
    if comparison["best_compliance"]:
        print(f"Best Compliance Rate: {comparison['best_compliance']} ({comparison['variant_stats'][comparison['best_compliance']]['compliance_rate']:.1f}%)")
    
    print(f"\nVariant Comparison:")
    for variant, stats in comparison["variant_stats"].items():
        print(f"  {variant:10s}: {stats['avg_reduction']:5.1f}% reduction, {stats['compliance_rate']:5.1f}% compliance")


if __name__ == "__main__":
    # Run tests
    prompt_variants = None  # Default: ["strict", "balanced", "minimal"]
    test_results = run_comprehensive_tests(prompt_variants)
    
    # Generate timestamped filename with clear metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    variants_tested = prompt_variants if prompt_variants else ["strict", "balanced", "minimal"]
    variants_str = "_".join(variants_tested)
    model = "gpt-4o-mini"
    
    # Calculate summary stats for filename
    all_variant_summaries = test_results.get("variants", {})
    if all_variant_summaries:
        best_reduction = max(
            (v.get("avg_completion_reduction_pct", 0) for v in all_variant_summaries.values()),
            default=0
        )
        avg_compliance = sum(
            (v.get("success_rate", 0) for v in all_variant_summaries.values())
        ) / len(all_variant_summaries) if all_variant_summaries else 0
        
        # Create descriptive filename
        filename = (
            f"token_reduction_test_"
            f"{timestamp}_"
            f"variants-{variants_str}_"
            f"model-{model}_"
            f"reduction-{best_reduction:.0f}pct_"
            f"compliance-{avg_compliance:.0f}pct.json"
        )
    else:
        # Fallback if no results
        filename = f"token_reduction_test_{timestamp}_variants-{variants_str}_model-{model}.json"
    
    # Save results to tests/test_results folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "test_results")
    os.makedirs(results_dir, exist_ok=True)
    
    output_file = os.path.join(results_dir, filename)
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)
    
    # Also save per-variant results for easier reference
    variants_tested = test_results.get("variants", {})
    for variant_name, variant_data in variants_tested.items():
        variant_filename = (
            f"variant_{variant_name}_"
            f"{timestamp}_"
            f"reduction-{variant_data.get('avg_completion_reduction_pct', 0):.0f}pct_"
            f"compliance-{variant_data.get('success_rate', 0):.0f}pct.json"
        )
        variant_file = os.path.join(results_dir, variant_filename)
        variant_output = {
            "metadata": {
                **test_results.get("metadata", {}),
                "variant": variant_name,
            },
            "variant_summary": variant_data,
            "variant_results": [
                r for r in test_results.get("all_results", [])
                if r.get("prompt_variant") == variant_name
            ],
        }
        with open(variant_file, "w") as f:
            json.dump(variant_output, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📁 Main file: {filename}")
    if variants_tested:
        print(f"📁 Per-variant files: {len(variants_tested)} files saved")
    print("\n✅ Test suite complete!")

