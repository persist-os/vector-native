"""
Parallel Provider Test Suite

Runs token reduction tests on both OpenAI and Gemini in parallel.
Tests the same scenarios across both providers for comparison.
"""

import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from vector_native import (
    get_vector_native_system_prompt,
    count_tokens,
    calculate_reduction,
    parse_with_fallback,
    create_openai_client,
    create_gemini_client,
)

# Load environment variables
load_dotenv()

# Load test scenarios from JSON file
_scenarios_file = Path(__file__).parent / "test_cases" / "scenarios.json"
with open(_scenarios_file, "r") as f:
    TEST_SCENARIOS = json.load(f)


def get_openai_response(client, prompt: str, system_prompt: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Get response from OpenAI.
    
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
            {"role": "system", "content": system_prompt},
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


def get_gemini_response(genai_module, prompt: str, system_prompt: str, model: str = "gemini-1.5-flash") -> Dict[str, Any]:
    """
    Get response from Gemini.
    
    Note: Gemini combines system + user prompt in a single message.
    
    Returns:
        {
            "response": str,
            "tokens_used": int,  # Estimated from response length
            "prompt_tokens": int,  # Estimated
            "completion_tokens": int,  # Estimated
        }
    """
    # Combine system prompt and user prompt for Gemini
    full_prompt = f"{system_prompt}\n\nUser: {prompt}"
    
    model_instance = genai_module.GenerativeModel(model)
    response = model_instance.generate_content(full_prompt)
    
    content = response.text
    
    # Estimate tokens (Gemini doesn't provide exact token counts in free tier)
    # Use simple estimation: ~0.75 tokens per word
    prompt_words = len(full_prompt.split())
    response_words = len(content.split())
    prompt_tokens_est = int(prompt_words * 0.75)
    completion_tokens_est = int(response_words * 0.75)
    total_tokens_est = prompt_tokens_est + completion_tokens_est
    
    return {
        "response": content,
        "tokens_used": total_tokens_est,
        "prompt_tokens": prompt_tokens_est,
        "completion_tokens": completion_tokens_est,
    }


def test_provider_scenario(
    provider: str,
    scenario: Dict[str, Any],
    prompt_variant: str,
    model: str,
    english_response: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Test a single scenario for a single provider.
    
    Args:
        provider: "openai" or "gemini"
        scenario: Test scenario dict
        prompt_variant: Prompt variant ("strict", "balanced", "minimal")
        model: Model name
        english_response: Optional cached English response
    
    Returns:
        Test result dict
    """
    prompt = scenario["prompt"].strip()
    
    try:
        # Get English baseline (if not cached)
        if english_response is None:
            if provider == "openai":
                client = create_openai_client()
                english_response = get_openai_response(
                    client,
                    prompt,
                    "You are a helpful assistant. Respond in natural English with detailed explanations.",
                    model
                )
            else:  # gemini
                genai_module = create_gemini_client()
                english_response = get_gemini_response(
                    genai_module,
                    prompt,
                    "You are a helpful assistant. Respond in natural English with detailed explanations.",
                    model
                )
        
        # Get vector-native response
        vn_system_prompt = get_vector_native_system_prompt(prompt_variant)
        
        if provider == "openai":
            client = create_openai_client()
            vn_response = get_openai_response(client, prompt, vn_system_prompt, model)
        else:  # gemini
            genai_module = create_gemini_client()
            vn_response = get_gemini_response(genai_module, prompt, vn_system_prompt, model)
        
        # Parse vector-native response
        parsed_result = parse_with_fallback(vn_response["response"], hybrid=True)
        
        # Calculate reduction
        reduction_data = calculate_reduction(
            english_response["response"],
            vn_response["response"],
            model
        )
        
        # Calculate total reduction
        english_total = english_response["tokens_used"]
        vn_total = vn_response["tokens_used"]
        total_reduction_pct = (
            (english_total - vn_total) / english_total * 100
            if english_total > 0
            else 0
        )
        
        return {
            "provider": provider,
            "scenario_name": scenario["name"],
            "prompt_variant": prompt_variant,
            "model": model,
            "success": parsed_result["format"] == "vector_native",
            "english": {
                "response": english_response["response"],
                "total_tokens": english_total,
                "completion_tokens": english_response["completion_tokens"],
            },
            "vector_native": {
                "response": vn_response["response"],
                "total_tokens": vn_total,
                "format": parsed_result["format"],
            },
            "reduction": {
                "completion_reduction_pct": reduction_data["reduction"],
                "completion_reduction_tokens": reduction_data["reduction_tokens"],
                "total_reduction_pct": round(total_reduction_pct, 1),
                "total_reduction_tokens": english_total - vn_total,
            },
        }
    except Exception as e:
        return {
            "provider": provider,
            "scenario_name": scenario["name"],
            "prompt_variant": prompt_variant,
            "model": model,
            "success": False,
            "error": str(e),
        }


def run_parallel_tests(
    prompt_variants: List[str] = None,
    providers: List[str] = None,
    max_workers: int = 4,
) -> Dict[str, Any]:
    """
    Run tests in parallel across multiple providers.
    
    Args:
        prompt_variants: List of prompt variants to test. Default: ["strict"]
        providers: List of providers to test. Default: ["openai", "gemini"]
        max_workers: Max concurrent workers. Default: 4
    
    Returns:
        Test results dict
    """
    if prompt_variants is None:
        prompt_variants = ["strict"]
    
    if providers is None:
        providers = []
        if os.getenv("OPENAI_API_KEY"):
            providers.append("openai")
        if os.getenv("GEMINI_API_KEY"):
            providers.append("gemini")
        
        if not providers:
            raise ValueError(
                "No API keys found. Set OPENAI_API_KEY and/or GEMINI_API_KEY env vars."
            )
    
    print("=" * 80)
    print("Parallel Provider Test Suite")
    print(f"Providers: {', '.join(providers)}")
    print(f"Prompt variants: {', '.join(prompt_variants)}")
    print(f"Max workers: {max_workers}")
    print("=" * 80)
    
    # Model mapping
    model_map = {
        "openai": "gpt-4o-mini",
        "gemini": "gemini-1.5-flash",
    }
    
    all_results = []
    provider_summaries = {}
    
    # Create tasks for parallel execution
    tasks = []
    for provider in providers:
        for variant in prompt_variants:
            for scenario in TEST_SCENARIOS:
                tasks.append({
                    "provider": provider,
                    "variant": variant,
                    "scenario": scenario,
                    "model": model_map[provider],
                })
    
    print(f"\n📋 Total tasks: {len(tasks)}")
    print(f"🚀 Running in parallel (max {max_workers} workers)...\n")
    
    # Execute tasks in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_task = {}
        for task in tasks:
            future = executor.submit(
                test_provider_scenario,
                provider=task["provider"],
                scenario=task["scenario"],
                prompt_variant=task["variant"],
                model=task["model"],
            )
            future_to_task[future] = task
        
        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            completed += 1
            
            try:
                result = future.result()
                all_results.append(result)
                
                # Print progress
                status = "✅" if result.get("success", False) else "❌"
                print(
                    f"[{completed}/{len(tasks)}] {status} {task['provider']:6s} | "
                    f"{task['variant']:8s} | {task['scenario']['name']:30s} | "
                    f"Reduction: {result.get('reduction', {}).get('completion_reduction_pct', 0):.1f}%"
                )
            except Exception as e:
                print(
                    f"[{completed}/{len(tasks)}] ❌ {task['provider']:6s} | "
                    f"{task['variant']:8s} | {task['scenario']['name']:30s} | "
                    f"Error: {str(e)[:50]}"
                )
                all_results.append({
                    "provider": task["provider"],
                    "scenario_name": task["scenario"]["name"],
                    "prompt_variant": task["variant"],
                    "model": task["model"],
                    "success": False,
                    "error": str(e),
                })
    
    # Calculate summaries per provider
    for provider in providers:
        provider_results = [r for r in all_results if r.get("provider") == provider]
        successful = [r for r in provider_results if r.get("success", False)]
        
        if successful:
            avg_reduction = sum(
                r.get("reduction", {}).get("completion_reduction_pct", 0)
                for r in successful
            ) / len(successful)
            
            provider_summaries[provider] = {
                "total_tests": len(provider_results),
                "successful_tests": len(successful),
                "success_rate": round(len(successful) / len(provider_results) * 100, 1),
                "avg_reduction_pct": round(avg_reduction, 1),
                "min_reduction_pct": round(min(
                    r.get("reduction", {}).get("completion_reduction_pct", 0)
                    for r in successful
                ), 1),
                "max_reduction_pct": round(max(
                    r.get("reduction", {}).get("completion_reduction_pct", 0)
                    for r in successful
                ), 1),
            }
        else:
            provider_summaries[provider] = {
                "total_tests": len(provider_results),
                "successful_tests": 0,
                "success_rate": 0,
                "avg_reduction_pct": 0,
            }
    
    # Print summaries
    print("\n" + "=" * 80)
    print("📊 PROVIDER COMPARISON")
    print("=" * 80)
    for provider, summary in provider_summaries.items():
        print(f"\n{provider.upper()}:")
        print(f"  Tests: {summary['total_tests']} ({summary['successful_tests']} successful)")
        print(f"  Success rate: {summary['success_rate']:.1f}%")
        if summary['successful_tests'] > 0:
            print(f"  Avg reduction: {summary['avg_reduction_pct']:.1f}%")
            if 'min_reduction_pct' in summary:
                print(f"  Range: {summary['min_reduction_pct']:.1f}% - {summary['max_reduction_pct']:.1f}%")
    
    # Metadata
    metadata = {
        "test_run_timestamp": datetime.now().isoformat(),
        "providers": providers,
        "prompt_variants": prompt_variants,
        "models": {p: model_map[p] for p in providers},
        "total_scenarios": len(TEST_SCENARIOS),
        "total_tests": len(all_results),
        "max_workers": max_workers,
    }
    
    return {
        "metadata": metadata,
        "provider_summaries": provider_summaries,
        "all_results": all_results,
    }


if __name__ == "__main__":
    # Run parallel tests
    prompt_variants = ["strict"]  # Can add "balanced", "minimal" if needed
    providers = None  # Auto-detect from env vars
    max_workers = 4  # Adjust based on API rate limits
    
    test_results = run_parallel_tests(
        prompt_variants=prompt_variants,
        providers=providers,
        max_workers=max_workers,
    )
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    providers_str = "_".join(test_results["metadata"]["providers"])
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "test_results")
    os.makedirs(results_dir, exist_ok=True)
    
    filename = f"parallel_providers_{timestamp}_{providers_str}.json"
    output_file = os.path.join(results_dir, filename)
    
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("✅ Parallel test suite complete!")

