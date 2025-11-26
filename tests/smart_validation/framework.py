"""
Smart Validation Framework

Core validation engine that orchestrates scenario selection, format comparison,
metrics calculation, and adaptive expansion for Vector-Native validation.

Reduces API calls from 60,000+ to 100 while maintaining 95% validation value.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

from .scenario_selector import load_and_select_scenarios

# Load environment variables
load_dotenv()


class SmartValidationFramework:
    """
    Smart validation framework using statistical sampling.
    
    Phase 1: 15 scenarios × 3 formats × 1 model × 1 temp × 2 trials = 90 calls
    Phase 2: 5 scenarios × 2 symbols × 1 model × 1 temp × 1 trial = 10 calls (optional)
    Total: 100 calls maximum
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        target_scenarios: int = 15,
        trials_per_config: int = 2,
        model_provider=None,  # Optional: ModelProvider instance for abstraction
        provider: Optional[str] = None,  # Optional: Provider name for auto-creation
        api_key: Optional[str] = None,  # Optional: API key
        endpoint: Optional[str] = None,  # Optional: Endpoint (for Azure)
    ):
        """
        Initialize framework.
        
        Args:
            model: Model to use (default: gpt-4o-mini, cheapest)
            temperature: Temperature for deterministic results (default: 0.0)
            target_scenarios: Number of scenarios to select (default: 15)
            trials_per_config: Number of trials per configuration (default: 2)
            model_provider: Optional ModelProvider instance (for abstraction)
            provider: Optional provider name ("openai", "azure", "gemini", "grok")
            api_key: Optional API key (uses env vars if not provided)
            endpoint: Optional endpoint (for Azure)
        """
        self.model = model
        self.temperature = temperature
        self.target_scenarios = target_scenarios
        self.trials_per_config = trials_per_config
        
        # Use model provider if provided, otherwise fall back to hardcoded OpenAI (backward compatible)
        if model_provider is not None:
            self.model_provider = model_provider
            self.client = model_provider.client
        elif provider is not None:
            # Auto-create model provider
            try:
                from ..vn_optimization.model_provider import create_model_provider
                self.model_provider = create_model_provider(
                    provider=provider,
                    model_id=model,
                    api_key=api_key,
                    endpoint=endpoint,
                    temperature=temperature,
                )
                self.client = self.model_provider.client
            except ImportError:
                # Fall back to hardcoded OpenAI if vn_optimization not available
                api_key = api_key or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                self.client = OpenAI(api_key=api_key)
                self.model_provider = None
        else:
            # Backward compatible: hardcoded OpenAI client
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
            self.model_provider = None
        
        # Load and select scenarios
        self.scenarios = load_and_select_scenarios(
            target_count=target_scenarios,
            model=model
        )
        
        # Results storage
        self.phase1_results: List[Dict[str, Any]] = []
        self.phase2_results: List[Dict[str, Any]] = []
        self.total_calls = 0
        self.cached_responses: Dict[str, Dict[str, Any]] = {}
    
    def get_cached_or_fetch(
        self,
        cache_key: str,
        fetch_func,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get cached response or fetch new one.
        
        Args:
            cache_key: Unique key for caching
            fetch_func: Function to fetch if not cached
            *args, **kwargs: Arguments for fetch_func
        
        Returns:
            Response dict
        """
        if cache_key in self.cached_responses:
            return self.cached_responses[cache_key]
        
        result = fetch_func(*args, **kwargs)
        self.cached_responses[cache_key] = result
        self.total_calls += 1
        return result
    
    def validate_phase1_ready(self) -> bool:
        """
        Validate that Phase 1 components are ready.
        
        Returns:
            True if ready, False otherwise
        """
        # Check that scenario selector works
        if not self.scenarios:
            return False
        
        if len(self.scenarios) != self.target_scenarios:
            # Warning but not fatal - selector will work with available scenarios
            pass
        
        # Check that format_comparator and metrics_calculator exist
        # (will be created in Phase 2)
        try:
            from . import format_comparator
            from . import metrics_calculator
            return True
        except ImportError:
            # Phase 2 not complete yet
            return False
    
    def run_phase1(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute Phase 1 validation: 90 calls.
        
        Args:
            dry_run: If True, don't make actual API calls (for testing)
        
        Returns:
            Phase 1 results dict
        """
        if not self.validate_phase1_ready():
            raise RuntimeError("Phase 1 components not ready. Complete Phase 2 first.")
        
        from . import format_comparator
        from .metrics_calculator import calculate_all_metrics
        
        # Reset counters
        self.total_calls = 0
        self.phase1_results = []
        self.cached_responses = {}
        
        print(f"\n{'='*80}")
        print(f"Phase 1: Core Validation ({len(self.scenarios)} scenarios × 3 formats × 2 trials = {len(self.scenarios) * 3 * self.trials_per_config} calls)")
        print(f"{'='*80}")
        
        if dry_run:
            print("DRY RUN MODE: No API calls will be made")
            return {
                "phase": 1,
                "scenarios_tested": len(self.scenarios),
                "total_calls": 0,
                "results": [],
                "dry_run": True
            }
        
        # Execute validation for each scenario
        for scenario_idx, scenario in enumerate(self.scenarios, 1):
            print(f"\n[Scenario {scenario_idx}/{len(self.scenarios)}] {scenario['name']}")
            
            # Cache English response (reused across trials)
            cache_key_english = f"english_{scenario['name']}"
            cached_english = None
            
            for trial in range(self.trials_per_config):
                print(f"  Trial {trial + 1}/{self.trials_per_config}")
                
                # Get English response (cached after first call)
                if cached_english is None:
                    english_result = self.get_cached_or_fetch(
                        cache_key_english,
                        format_comparator.get_english_response,
                        self.client,
                        scenario["prompt"],
                        self.model
                    )
                    cached_english = english_result
                else:
                    # Reuse cached English response (no API call)
                    english_result = cached_english
                
                # Compare all formats (makes JSON and VN API calls)
                # Pass call_tracker to track API calls
                comparison = format_comparator.compare_formats(
                    client=self.client,
                    prompt=scenario["prompt"],
                    model=self.model,
                    temperature=self.temperature,
                    vn_prompt_variant="strict",
                    cached_english=english_result,
                    call_tracker=self  # Pass self to track calls
                )
                
                # Store result
                result = {
                    "scenario_name": scenario["name"],
                    "scenario_metadata": {
                        "length": scenario.get("length", "unknown"),
                        "domain": scenario.get("domain", "unknown"),
                        "edge_case": scenario.get("edge_case", False),
                    },
                    "trial": trial + 1,
                    **comparison
                }
                self.phase1_results.append(result)
                
                # Check call limit
                self.ensure_call_limit(max_calls=100)
        
        # Calculate metrics
        metrics = calculate_all_metrics(self.phase1_results)
        
        print(f"\n{'='*80}")
        print(f"Phase 1 Complete: {self.total_calls} API calls made")
        print(f"{'='*80}")
        print(f"Compliance: VN={metrics.get('compliance_rates', {}).get('vector_native', 0):.1%}, JSON={metrics.get('compliance_rates', {}).get('json', 0):.1%}")
        print(f"Token Reduction: {metrics.get('token_reduction', {}).get('mean_vs_nl', 0):.1f}%")
        print(f"P-value: {metrics.get('p_values', {}).get('vn_vs_nl_tokens', 1):.4f}")
        
        return {
            "phase": 1,
            "scenarios_tested": len(self.scenarios),
            "total_calls": self.total_calls,
            "results": self.phase1_results,
            "metrics": metrics,
        }
    
    def run_phase2(self, dry_run: bool = False) -> Optional[Dict[str, Any]]:
        """
        Execute Phase 2 symbol effects test: 10 calls (optional).
        
        Phase 2 tests if ● symbol outperforms * symbol in compliance.
        5 scenarios × 2 symbols × 1 model × 1 temp × 1 trial = 10 calls
        
        Args:
            dry_run: If True, don't make actual API calls
        
        Returns:
            Phase 2 results dict or None if Phase 1 not promising
        """
        from .adaptive_tester import evaluate_phase1_results
        
        # Check if Phase 1 was promising
        if not self.phase1_results:
            print("Phase 1 not executed yet. Run Phase 1 first.")
            return None
        
        evaluation = evaluate_phase1_results(self.phase1_results)
        if not evaluation.get("should_proceed", False):
            print(f"Phase 1 not promising: {evaluation.get('reason', 'Unknown')}")
            print("Skipping Phase 2 (symbol effects test)")
            return None
        
        print(f"\n{'='*80}")
        print(f"Phase 2: Symbol Effects Test (5 scenarios × 2 symbols × 1 trial = 10 calls)")
        print(f"{'='*80}")
        
        if dry_run:
            print("DRY RUN MODE: No API calls will be made")
            return {
                "phase": 2,
                "scenarios_tested": 5,
                "total_calls": 0,
                "results": [],
                "dry_run": True
            }
        
        # Select 5 scenarios for symbol comparison
        symbol_test_scenarios = self.scenarios[:5] if len(self.scenarios) >= 5 else self.scenarios
        
        from vector_native import get_vector_native_system_prompt, parse_with_fallback
        
        self.phase2_results = []
        
        for scenario in symbol_test_scenarios:
            print(f"\n[Symbol Test] {scenario['name']}")
            
            # Test with ● symbol (default VN)
            vn_system_prompt_bullet = get_vector_native_system_prompt("strict")
            vn_result_bullet = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": vn_system_prompt_bullet},
                    {"role": "user", "content": scenario["prompt"]},
                ],
            )
            self.total_calls += 1
            
            content_bullet = vn_result_bullet.choices[0].message.content
            parsed_bullet = parse_with_fallback(content_bullet, hybrid=True)
            compliance_bullet = 1.0 if parsed_bullet["format"] == "vector_native" else 0.0
            
            # Test with * symbol (modified system prompt)
            # Replace ● with * in system prompt
            vn_system_prompt_star = vn_system_prompt_bullet.replace("●", "*").replace("○", "*")
            vn_result_star = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": vn_system_prompt_star},
                    {"role": "user", "content": scenario["prompt"]},
                ],
            )
            self.total_calls += 1
            
            content_star = vn_result_star.choices[0].message.content
            parsed_star = parse_with_fallback(content_star, hybrid=True)
            compliance_star = 1.0 if parsed_star["format"] == "vector_native" else 0.0
            
            result = {
                "scenario_name": scenario["name"],
                "symbol_bullet": {
                    "compliance": compliance_bullet,
                    "format": parsed_bullet["format"],
                },
                "symbol_star": {
                    "compliance": compliance_star,
                    "format": parsed_star["format"],
                },
                "difference": compliance_bullet - compliance_star,
            }
            self.phase2_results.append(result)
            
            # Check call limit
            self.ensure_call_limit(max_calls=100)
        
        print(f"\n{'='*80}")
        print(f"Phase 2 Complete: {len(symbol_test_scenarios) * 2} API calls made")
        print(f"{'='*80}")
        
        # Calculate symbol comparison metrics
        bullet_compliances = [r["symbol_bullet"]["compliance"] for r in self.phase2_results]
        star_compliances = [r["symbol_star"]["compliance"] for r in self.phase2_results]
        
        from .metrics_calculator import calculate_p_value, calculate_effect_size
        p_value = calculate_p_value(bullet_compliances, star_compliances)
        effect_size = calculate_effect_size(bullet_compliances, star_compliances)
        
        print(f"● Compliance: {sum(bullet_compliances) / len(bullet_compliances):.1%}")
        print(f"* Compliance: {sum(star_compliances) / len(star_compliances):.1%}")
        print(f"P-value: {p_value:.4f}")
        print(f"Effect size (Cohen's d): {effect_size:.3f}")
        
        return {
            "phase": 2,
            "scenarios_tested": len(symbol_test_scenarios),
            "total_calls": len(symbol_test_scenarios) * 2,
            "results": self.phase2_results,
            "metrics": {
                "bullet_compliance": sum(bullet_compliances) / len(bullet_compliances) if bullet_compliances else 0.0,
                "star_compliance": sum(star_compliances) / len(star_compliances) if star_compliances else 0.0,
                "p_value": p_value,
                "effect_size": effect_size,
                "significant": p_value < 0.05,
            }
        }
    
    def get_total_calls(self) -> int:
        """
        Get total API calls made.
        
        Returns:
            Total number of API calls
        """
        return self.total_calls
    
    def ensure_call_limit(self, max_calls: int = 100) -> None:
        """
        Ensure we don't exceed call limit.
        
        Args:
            max_calls: Maximum allowed calls (default: 100)
        
        Raises:
            RuntimeError: If limit exceeded
        """
        if self.total_calls > max_calls:
            raise RuntimeError(
                f"Call limit exceeded: {self.total_calls} > {max_calls}. "
                "Stop execution immediately."
            )


    def run_full_validation(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Run complete validation: Phase 1 → Phase 2 (if promising) → Report.
        
        Args:
            dry_run: If True, don't make actual API calls
        
        Returns:
            Complete validation report
        """
        from .results_analyzer import generate_validation_report, save_report, print_report_summary
        
        print(f"\n{'='*80}")
        print("SMART VALIDATION FRAMEWORK")
        print(f"{'='*80}")
        print(f"Model: {self.model}")
        print(f"Temperature: {self.temperature}")
        print(f"Scenarios: {len(self.scenarios)}")
        print(f"Trials per config: {self.trials_per_config}")
        print(f"Max calls: 100")
        
        # Phase 1: Core validation
        phase1_result = self.run_phase1(dry_run=dry_run)
        
        # Phase 2: Symbol effects (if Phase 1 promising)
        phase2_result = None
        if not dry_run and phase1_result.get("metrics", {}).get("compliance_rates", {}).get("vector_native", 0) > 0.85:
            phase2_result = self.run_phase2(dry_run=dry_run)
        
        # Generate report
        report = generate_validation_report(
            phase1_results=self.phase1_results,
            phase2_results=self.phase2_results if phase2_result else None,
            total_calls=self.total_calls,
            model=self.model,
            temperature=self.temperature,
            scenarios_tested=len(self.scenarios)
        )
        
        # Save report
        if not dry_run:
            report_path = save_report(report)
            print(f"\nReport saved to: {report_path}")
        
        # Print summary
        print_report_summary(report)
        
        return report


if __name__ == "__main__":
    # Test framework initialization
    framework = SmartValidationFramework()
    
    print(f"Framework initialized:")
    print(f"  Model: {framework.model}")
    print(f"  Temperature: {framework.temperature}")
    print(f"  Scenarios selected: {len(framework.scenarios)}")
    print(f"  Target scenarios: {framework.target_scenarios}")
    print(f"  Trials per config: {framework.trials_per_config}")
    
    print(f"\nSelected scenarios:")
    for i, scenario in enumerate(framework.scenarios, 1):
        print(f"{i}. {scenario['name']} ({scenario.get('length', 'unknown')}, {scenario.get('domain', 'unknown')})")
    
    print(f"\nTo run full validation:")
    print(f"  framework.run_full_validation(dry_run=True)  # Test without API calls")
    print(f"  framework.run_full_validation(dry_run=False)  # Execute with API calls")

