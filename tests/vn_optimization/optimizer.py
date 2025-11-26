"""
High-Level Optimization Interface

Optimization workflow that searches VN config space and finds best config per model.
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sys

from .vn_config import VNConfig
from .model_provider import ModelProvider
from .convergence_adapter import (
    create_vn_evaluator,
    generate_search_space,
    create_convergence_config,
    CONVERGENCE_AVAILABLE,
)

# Import validation infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from smart_validation.format_comparator import compare_formats
from smart_validation.metrics_calculator import calculate_all_metrics


async def optimize_for_model(
    model_provider: ModelProvider,
    scenarios: List[Dict[str, Any]],
    search_space_config: Optional[Dict[str, Dict[str, Any]]] = None,
    temperature: float = 0.0,
    generations: int = 10,
    population: int = 20,
    compliance_weight: float = 0.7,
    token_reduction_weight: float = 0.3,
) -> Tuple[VNConfig, Dict[str, float]]:
    """
    Optimize VN config for a specific model.
    
    Args:
        model_provider: ModelProvider instance
        scenarios: List of test scenarios
        search_space_config: Optional custom search space
        temperature: Temperature setting
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
    
    # Convert scenarios to test cases format
    test_cases = [
        {"input": {"prompt": s.get("prompt", s.get("text", ""))}, "expected": {}}
        for s in scenarios
    ]
    
    # Create evaluator
    evaluator = create_vn_evaluator(
        model_provider=model_provider,
        scenarios=scenarios,
        temperature=temperature,
    )
    
    # Create convergence config
    config = create_convergence_config(
        model_name=model_provider.config.model_id,
        scenarios=scenarios,
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

