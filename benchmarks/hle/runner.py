"""
Main Runner for HLE Benchmark
Orchestrates the complete benchmark execution
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from .config import BenchmarkConfig, load_config
from .dataset_loader import load_hle_dataset, get_example_prompt
from .prompt_templates import (
    get_nl_system_prompt,
    get_vn_system_prompt,
    format_question_prompt,
    format_question_prompt_vn,
)
from .evaluator import evaluate_response
from .metrics import calculate_all_metrics

# LLM client imports
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None


def call_claude_api(
    client: Any,
    system_prompt: str,
    user_prompt: str,
    model: str = "claude-sonnet-4-20250514",
    temperature: float = 0.0
) -> Dict[str, Any]:
    """
    Call Claude API with system and user prompts.
    
    Args:
        client: Anthropic client instance
        system_prompt: System prompt
        user_prompt: User prompt
        model: Model name
        temperature: Temperature setting
    
    Returns:
        {
            "response": str,
            "tokens_used": int,
            "prompt_tokens": int,
            "completion_tokens": int,
        }
    """
    if not ANTHROPIC_AVAILABLE:
        raise ImportError("anthropic package not installed. Install with: pip install anthropic")
    
    try:
        message = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        response_text = message.content[0].text if message.content else ""
        
        # Extract token usage if available
        tokens_used = getattr(message, "usage", None)
        prompt_tokens = tokens_used.input_tokens if tokens_used else None
        completion_tokens = tokens_used.output_tokens if tokens_used else None
        total_tokens = (prompt_tokens + completion_tokens) if (prompt_tokens and completion_tokens) else None
        
        return {
            "response": response_text,
            "tokens_used": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }
    
    except Exception as e:
        raise Exception(f"Claude API call failed: {e}")


def run_nl_evaluation(
    client: Any,
    examples: List[Dict[str, Any]],
    config: BenchmarkConfig
) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Run natural language evaluation.
    
    Args:
        client: LLM client
        examples: List of dataset examples
        config: Benchmark configuration
    
    Returns:
        (evaluation_results, response_texts)
    """
    print("\n" + "="*80)
    print("Running Natural Language Evaluation")
    print("="*80)
    
    system_prompt = get_nl_system_prompt()
    results = []
    responses = []
    
    for i, example in enumerate(examples):
        print(f"\n[{i+1}/{len(examples)}] Processing example {example.get('id', i)}...")
        
        # Format prompt
        user_prompt = format_question_prompt(
            example["question"],
            example.get("options", [])
        )
        
        # Call API
        try:
            api_result = call_claude_api(
                client,
                system_prompt,
                user_prompt,
                config.model,
                config.temperature
            )
            
            response_text = api_result["response"]
            responses.append(response_text)
            
            # Evaluate
            eval_result = evaluate_response(
                response_text,
                example["answer"],
                "nl",
                config.nl_answer_pattern,
                config.validation_modes
            )
            
            eval_result["example_id"] = example.get("id", f"example_{i}")
            eval_result["response_tokens"] = api_result.get("completion_tokens")
            results.append(eval_result)
            
            print(f"  Extracted: {eval_result['extracted_answer']}")
            print(f"  Correct: {example['answer']}")
            print(f"  Correct: {eval_result['is_correct'].get('exact_match', False)}")
        
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "example_id": example.get("id", f"example_{i}"),
                "error": str(e),
                "extraction_success": False,
            })
            responses.append("")
    
    return results, responses


def run_vn_evaluation(
    client: Any,
    examples: List[Dict[str, Any]],
    config: BenchmarkConfig
) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Run vector-native evaluation.
    
    Args:
        client: LLM client
        examples: List of dataset examples
        config: Benchmark configuration
    
    Returns:
        (evaluation_results, response_texts)
    """
    print("\n" + "="*80)
    print("Running Vector-Native Evaluation")
    print("="*80)
    
    system_prompt = get_vn_system_prompt(
        config.vn_prompt_variant,
        config.global_mdc_path
    )
    results = []
    responses = []
    
    for i, example in enumerate(examples):
        print(f"\n[{i+1}/{len(examples)}] Processing example {example.get('id', i)}...")
        
        # Format prompt (VN style)
        user_prompt = format_question_prompt_vn(
            example["question"],
            example.get("options", [])
        )
        
        # Call API
        try:
            api_result = call_claude_api(
                client,
                system_prompt,
                user_prompt,
                config.model,
                config.temperature
            )
            
            response_text = api_result["response"]
            responses.append(response_text)
            
            # Evaluate
            eval_result = evaluate_response(
                response_text,
                example["answer"],
                "vn",
                config.vn_answer_pattern,
                config.validation_modes
            )
            
            eval_result["example_id"] = example.get("id", f"example_{i}")
            eval_result["response_tokens"] = api_result.get("completion_tokens")
            results.append(eval_result)
            
            print(f"  Extracted: {eval_result['extracted_answer']}")
            print(f"  Correct: {example['answer']}")
            print(f"  Correct: {eval_result['is_correct'].get('exact_match', False)}")
            print(f"  Response preview: {response_text[:100]}...")
        
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "example_id": example.get("id", f"example_{i}"),
                "error": str(e),
                "extraction_success": False,
            })
            responses.append("")
    
    return results, responses


def save_results(
    nl_results: List[Dict[str, Any]],
    vn_results: List[Dict[str, Any]],
    nl_responses: List[str],
    vn_responses: List[str],
    metrics: Dict[str, Any],
    config: BenchmarkConfig
) -> Dict[str, Path]:
    """
    Save all results to JSON files.
    
    Args:
        nl_results: NL evaluation results
        vn_results: VN evaluation results
        nl_responses: NL response texts
        vn_responses: VN response texts
        metrics: Calculated metrics
        config: Benchmark configuration
    
    Returns:
        Dict mapping result type to file path
    """
    output_paths = config.get_output_paths()
    
    # Save predictions
    predictions_nl = [
        {
            "example_id": r.get("example_id"),
            "extracted_answer": r.get("extracted_answer"),
            "correct_answer": r.get("correct_answer"),
            "is_correct": r.get("is_correct", {}),
            "response": nl_responses[i] if i < len(nl_responses) else "",
        }
        for i, r in enumerate(nl_results)
    ]
    
    predictions_vn = [
        {
            "example_id": r.get("example_id"),
            "extracted_answer": r.get("extracted_answer"),
            "correct_answer": r.get("correct_answer"),
            "is_correct": r.get("is_correct", {}),
            "response": vn_responses[i] if i < len(vn_responses) else "",
        }
        for i, r in enumerate(vn_results)
    ]
    
    # Save files
    with open(output_paths["predictions_nl"], "w") as f:
        json.dump(predictions_nl, f, indent=2)
    
    with open(output_paths["predictions_vn"], "w") as f:
        json.dump(predictions_vn, f, indent=2)
    
    # Save comparison
    comparison = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "model": config.model,
            "temperature": config.temperature,
            "dataset": config.dataset_name,
            "split": config.dataset_split,
            "vn_variant": config.vn_prompt_variant,
            "num_examples": len(nl_results),
        },
        "metrics": metrics,
        "nl_results": nl_results,
        "vn_results": vn_results,
    }
    
    with open(output_paths["comparison"], "w") as f:
        json.dump(comparison, f, indent=2)
    
    # Save metrics separately
    with open(output_paths["metrics"], "w") as f:
        json.dump(metrics, f, indent=2)
    
    return output_paths


def print_summary(metrics: Dict[str, Any], config: BenchmarkConfig):
    """Print benchmark summary."""
    print("\n" + "="*80)
    print("BENCHMARK SUMMARY")
    print("="*80)
    
    primary = metrics["primary_metric"]
    print(f"\nPrimary Metric ({primary['mode']}):")
    print(f"  NL Accuracy: {primary['accuracy_nl']:.2f}%")
    print(f"  VN Accuracy: {primary['accuracy_vn']:.2f}%")
    print(f"  Delta: {primary['delta']:+.2f} percentage points")
    print(f"  Improvement: {'✅ YES' if primary['improvement'] else '❌ NO'}")
    print(f"  Parity: {'✅ YES' if primary['parity'] else '❌ NO'}")
    
    token_metrics = metrics["tokens"]
    print(f"\nToken Metrics:")
    print(f"  NL Tokens: {token_metrics['tokens_nl']:,}")
    print(f"  VN Tokens: {token_metrics['tokens_vn']:,}")
    print(f"  Reduction: {token_metrics['reduction_percentage']:.2f}%")
    print(f"  Avg NL: {token_metrics['avg_tokens_nl']:.2f} tokens/example")
    print(f"  Avg VN: {token_metrics['avg_tokens_vn']:.2f} tokens/example")
    
    summary = metrics["summary"]
    print(f"\nSummary:")
    print(f"  Total Examples: {summary['total_examples']}")
    print(f"  NL Correct: {summary['nl_correct']}")
    print(f"  VN Correct: {summary['vn_correct']}")
    print(f"  Token Reduction: {summary['token_reduction_pct']:.2f}%")
    print(f"  Accuracy Improvement: {'✅ YES' if summary['accuracy_improvement'] else '❌ NO'}")


def run_benchmark(config: Optional[BenchmarkConfig] = None) -> Dict[str, Any]:
    """
    Run the complete HLE benchmark.
    
    Args:
        config: Optional benchmark configuration (uses defaults if None)
    
    Returns:
        Complete benchmark results
    """
    # Load configuration
    if config is None:
        config = load_config()
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment. Please set it in .env file."
        )
    
    # Initialize client
    if not ANTHROPIC_AVAILABLE:
        raise ImportError("anthropic package not installed. Install with: pip install anthropic")
    
    client = Anthropic(api_key=api_key)
    
    print("="*80)
    print("HLE BENCHMARK: Vector-Native vs Natural Language")
    print("="*80)
    print(f"Model: {config.model}")
    print(f"Temperature: {config.temperature}")
    print(f"Dataset: {config.dataset_name} ({config.dataset_split})")
    print(f"VN Variant: {config.vn_prompt_variant}")
    print(f"Sample Size: {config.sample_size or 'Full dataset'}")
    
    # Load dataset
    examples = load_hle_dataset(
        config.dataset_name,
        config.dataset_split,
        config.sample_size
    )
    
    if not examples:
        raise ValueError("No examples loaded from dataset")
    
    print(f"\nLoaded {len(examples)} examples")
    
    # Run NL evaluation
    nl_results, nl_responses = run_nl_evaluation(client, examples, config)
    
    # Run VN evaluation
    vn_results, vn_responses = run_vn_evaluation(client, examples, config)
    
    # Calculate metrics
    print("\n" + "="*80)
    print("Calculating Metrics")
    print("="*80)
    
    metrics = calculate_all_metrics(
        nl_results,
        vn_results,
        nl_responses,
        vn_responses,
        config.model,
        config.validation_modes
    )
    
    # Save results
    output_paths = save_results(
        nl_results,
        vn_results,
        nl_responses,
        vn_responses,
        metrics,
        config
    )
    
    # Print summary
    print_summary(metrics, config)
    
    print(f"\n💾 Results saved to:")
    for result_type, path in output_paths.items():
        print(f"  {result_type}: {path}")
    
    return {
        "config": config,
        "nl_results": nl_results,
        "vn_results": vn_results,
        "metrics": metrics,
        "output_paths": output_paths,
    }


if __name__ == "__main__":
    # Run benchmark
    config = load_config()
    
    # Test with sample first
    if config.sample_size:
        print(f"Running with sample size: {config.sample_size}")
        results = run_benchmark(config)
        
        # Ask user if they want to run full dataset
        if config.full_dataset_after_validation:
            print("\n" + "="*80)
            print("Sample run complete. Run full dataset? (y/n)")
            print("="*80)
            # For automated runs, set FULL_DATASET=true in env
            if os.getenv("FULL_DATASET", "").lower() == "true":
                config.sample_size = None
                print("Running full dataset...")
                results = run_benchmark(config)
    else:
        # Run full dataset
        results = run_benchmark(config)

