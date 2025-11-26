"""
Vector-Native Optimization Framework

Unified framework that uses model_provider abstraction, extends SmartValidationFramework
with model switching and optimization capabilities.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Import model provider abstraction
from .model_provider import ModelProvider, ModelProviderConfig, create_model_provider
from .vn_config import VNConfig
from .convergence_adapter import (
    create_vn_evaluator,
    generate_search_space,
    create_convergence_config,
    CONVERGENCE_AVAILABLE,
)
from .optimizer import optimize_for_model
from .config_registry import ConfigRegistry

# Import existing smart validation framework
sys.path.insert(0, str(Path(__file__).parent.parent))
from smart_validation.framework import SmartValidationFramework
from smart_validation.scenario_selector import load_and_select_scenarios


class VNOptimizationFramework(SmartValidationFramework):
    """
    Unified VN optimization framework that extends SmartValidationFramework
    with model/provider abstraction and optimization capabilities.
    
    Supports:
    - Multiple models/providers (Azure, OpenAI, Gemini)
    - Model switching without code changes
    - VN configuration optimization (Phase 2+)
    """
    
    def __init__(
        self,
        provider: str = "openai",
        model_id: str = "gpt-4o-mini",
        temperature: float = 0.0,
        target_scenarios: int = 15,
        trials_per_config: int = 2,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        vn_config: Optional[VNConfig] = None,
    ):
        """
        Initialize optimization framework.
        
        Args:
            provider: Provider name ("openai", "azure", "gemini", "grok")
            model_id: Model identifier (e.g., "gpt-4o-mini", "gpt-4.1-nano")
            temperature: Temperature for deterministic results (default: 0.0)
            target_scenarios: Number of scenarios to select (default: 15)
            trials_per_config: Number of trials per configuration (default: 2)
            api_key: Optional API key (uses env vars if not provided)
            endpoint: Optional endpoint (for Azure)
            vn_config: Optional VNConfig (defaults to strict variant if not provided)
        """
        # Create model provider
        self.model_provider = create_model_provider(
            provider=provider,
            model_id=model_id,
            api_key=api_key,
            endpoint=endpoint,
            temperature=temperature,
        )
        
        # Initialize VN config (default to strict if not provided)
        self.vn_config = vn_config or VNConfig(prompt_variant="strict")
        
        # Initialize parent with model_id (for scenario selection)
        # Parent will use our model_provider.client instead of hardcoded OpenAI
        super().__init__(
            model=model_id,
            temperature=temperature,
            target_scenarios=target_scenarios,
            trials_per_config=trials_per_config,
        )
        
        # Override client with model provider client
        self.client = self.model_provider.client
        
        # Initialize config registry
        self.config_registry = ConfigRegistry()
    
    def switch_model(
        self,
        provider: str,
        model_id: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        """
        Switch to a different model/provider.
        
        Args:
            provider: Provider name ("openai", "azure", "gemini", "grok")
            model_id: Model identifier
            api_key: Optional API key
            endpoint: Optional endpoint (for Azure)
        """
        self.model_provider = create_model_provider(
            provider=provider,
            model_id=model_id,
            api_key=api_key,
            endpoint=endpoint,
            temperature=self.temperature,
        )
        self.client = self.model_provider.client
        self.model = model_id
        
        # Reload scenarios for new model (if needed)
        self.scenarios = load_and_select_scenarios(
            target_count=self.target_scenarios,
            model=model_id
        )
    
    def set_vn_config(self, vn_config: VNConfig) -> None:
        """
        Set VN configuration.
        
        Args:
            vn_config: VNConfig instance
        """
        # Validate config
        is_valid, error = vn_config.validate()
        if not is_valid:
            raise ValueError(f"Invalid VN config: {error}")
        
        self.vn_config = vn_config
    
    async def optimize_vn_config(
        self,
        scenarios: Optional[List[Dict[str, Any]]] = None,
        search_space_config: Optional[Dict[str, Dict[str, Any]]] = None,
        generations: int = 10,
        population: int = 20,
        compliance_weight: float = 0.7,
        token_reduction_weight: float = 0.3,
    ) -> tuple[VNConfig, Dict[str, float]]:
        """
        Optimize VN config using the-convergence.
        
        Args:
            scenarios: Optional list of scenarios (uses self.scenarios if not provided)
            search_space_config: Optional custom search space
            generations: Number of optimization generations
            population: Population size per generation
            compliance_weight: Weight for compliance metric
            token_reduction_weight: Weight for token reduction metric
        
        Returns:
            Tuple of (best VNConfig, best_metrics)
        """
        if not CONVERGENCE_AVAILABLE:
            raise ImportError("the-convergence not available. Install with: pip install the-convergence")
        
        from convergence.sdk import run_optimization
        
        # Use provided scenarios or self.scenarios
        test_scenarios = scenarios or self.scenarios
        
        # Convert scenarios to test cases format
        test_cases = [
            {"input": {"prompt": s.get("prompt", s.get("text", ""))}, "expected": {}}
            for s in test_scenarios
        ]
        
        # Create evaluator
        evaluator = create_vn_evaluator(
            model_provider=self.model_provider,
            scenarios=test_scenarios,
            temperature=self.temperature,
        )
        
        # Create convergence config
        config = create_convergence_config(
            model_name=self.model,
            scenarios=test_scenarios,
            search_space_config=search_space_config,
            generations=generations,
            population=population,
            compliance_weight=compliance_weight,
            token_reduction_weight=token_reduction_weight,
        )
        
        # Run optimization
        result = await run_optimization(
            config=config,
            evaluator=evaluator,
            test_cases=test_cases,
            logging_mode="summary",
        )
        
        # Convert best config to VNConfig
        best_config_dict = result.best_config
        best_vn_config = VNConfig.from_dict(best_config_dict)
        
        # Extract metrics from result
        best_metrics = {
            "compliance": result.best_score.get("compliance", 0.0),
            "token_reduction": result.best_score.get("token_reduction", 0.0),
        }
        
        return best_vn_config, best_metrics
    
    async def run_optimization_workflow(
        self,
        scenarios: Optional[List[Dict[str, Any]]] = None,
        search_space_config: Optional[Dict[str, Dict[str, Any]]] = None,
        generations: int = 10,
        population: int = 20,
        compliance_weight: float = 0.7,
        token_reduction_weight: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Run complete optimization workflow.
        
        (1) Validates baseline (VN vs JSON/NL)
        (2) Optimizes VN configs per model
        (3) Compares best configs across models
        (4) Returns optimization report
        
        Args:
            scenarios: Optional list of scenarios (uses self.scenarios if not provided)
            search_space_config: Optional custom search space
            generations: Number of optimization generations
            population: Population size per generation
            compliance_weight: Weight for compliance metric
            token_reduction_weight: Weight for token reduction metric
        
        Returns:
            Optimization report dict
        """
        test_scenarios = scenarios or self.scenarios
        
        # Phase 1: Validate baseline (VN vs JSON/NL)
        print("\n[Phase 1] Validating baseline (VN vs JSON/NL)...")
        baseline_results = self.run_phase1(dry_run=False)
        
        # Phase 2: Optimize VN config
        print("\n[Phase 2] Optimizing VN config...")
        best_config, best_metrics = await self.optimize_vn_config(
            scenarios=test_scenarios,
            search_space_config=search_space_config,
            generations=generations,
            population=population,
            compliance_weight=compliance_weight,
            token_reduction_weight=token_reduction_weight,
        )
        
        # Phase 3: Compare best config with baseline
        print("\n[Phase 3] Comparing optimized config with baseline...")
        comparison = self.compare_vn_configs(
            config_a=self.vn_config,
            config_b=best_config,
            scenarios=test_scenarios,
        )
        
        # Store configs in registry
        baseline_config_id = self.config_registry.store_config(
            model=self.model,
            provider=self.model_provider.config.provider,
            vn_config=self.vn_config,
            metrics=baseline_results.get("summary", {}).get("metrics", {}),
            metadata={"type": "baseline"},
        )
        
        optimized_config_id = self.config_registry.store_config(
            model=self.model,
            provider=self.model_provider.config.provider,
            vn_config=best_config,
            metrics=best_metrics,
            metadata={"type": "optimized"},
        )
        
        # Build report
        report = {
            "baseline": {
                "config_id": baseline_config_id,
                "config": self.vn_config.to_searchable_dict(),
                "results": baseline_results,
            },
            "optimized": {
                "config_id": optimized_config_id,
                "config": best_config.to_searchable_dict(),
                "metrics": best_metrics,
            },
            "comparison": comparison,
            "model": self.model,
            "provider": self.model_provider.config.provider,
            "registry": {
                "best_config": self.config_registry.get_best_config(self.model),
                "evolution": self.config_registry.get_evolution(self.model),
                "improvements": self.config_registry.get_improvements(self.model),
            },
        }
        
        return report
    
    def compare_vn_configs(
        self,
        config_a: VNConfig,
        config_b: VNConfig,
        scenarios: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Compare two VN configs against each other (not just vs JSON/NL).
        
        Args:
            config_a: First VN config
            config_b: Second VN config
            scenarios: Optional list of scenarios (uses self.scenarios if not provided)
        
        Returns:
            Comparison results dict
        """
        test_scenarios = scenarios or self.scenarios
        
        results_a = []
        results_b = []
        
        for scenario in test_scenarios:
            prompt = scenario.get("prompt", scenario.get("text", ""))
            
            # Test config A
            system_prompt_a = config_a.generate_system_prompt()
            response_a = self.model_provider.create_completion(
                messages=[
                    {"role": "system", "content": system_prompt_a},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
            )
            
            # Test config B
            system_prompt_b = config_b.generate_system_prompt()
            response_b = self.model_provider.create_completion(
                messages=[
                    {"role": "system", "content": system_prompt_b},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
            )
            
            # Parse responses
            from vector_native import parse_with_fallback
            parsed_a = parse_with_fallback(response_a.choices[0].message.content, hybrid=True)
            parsed_b = parse_with_fallback(response_b.choices[0].message.content, hybrid=True)
            
            # Calculate metrics
            compliance_a = 1.0 if parsed_a["format"] == "vector_native" else 0.0
            compliance_b = 1.0 if parsed_b["format"] == "vector_native" else 0.0
            
            from vector_native import count_tokens
            tokens_a = count_tokens(response_a.choices[0].message.content)
            tokens_b = count_tokens(response_b.choices[0].message.content)
            
            results_a.append({
                "compliance": compliance_a,
                "tokens": tokens_a,
            })
            results_b.append({
                "compliance": compliance_b,
                "tokens": tokens_b,
            })
        
        # Calculate averages
        avg_compliance_a = sum(r["compliance"] for r in results_a) / len(results_a) if results_a else 0.0
        avg_compliance_b = sum(r["compliance"] for r in results_b) / len(results_b) if results_b else 0.0
        avg_tokens_a = sum(r["tokens"] for r in results_a) / len(results_a) if results_a else 0.0
        avg_tokens_b = sum(r["tokens"] for r in results_b) / len(results_b) if results_b else 0.0
        
        return {
            "config_a": {
                "compliance": avg_compliance_a,
                "avg_tokens": avg_tokens_a,
            },
            "config_b": {
                "compliance": avg_compliance_b,
                "avg_tokens": avg_tokens_b,
            },
            "improvement": {
                "compliance_delta": avg_compliance_b - avg_compliance_a,
                "token_delta": avg_tokens_a - avg_tokens_b,  # Positive = reduction
            },
        }

