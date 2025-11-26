"""
Convergence Integration Adapter

Bridge VN optimization to the-convergence. Implements evaluator function,
search space generator, and ConvergenceConfig creation.
"""

from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import sys

# Import VN config
from .vn_config import VNConfig

# Import convergence SDK
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "the-convergence"))
try:
    from convergence.types import ConvergenceConfig, ApiConfig, SearchSpaceConfig, RunnerConfig, EvaluationConfig
    from convergence.sdk import run_optimization
    CONVERGENCE_AVAILABLE = True
except ImportError:
    CONVERGENCE_AVAILABLE = False
    ConvergenceConfig = None
    ApiConfig = None
    SearchSpaceConfig = None
    RunnerConfig = None
    EvaluationConfig = None
    run_optimization = None

# Import validation infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from smart_validation.format_comparator import compare_formats
from smart_validation.metrics_calculator import calculate_all_metrics


def create_vn_evaluator(
    model_provider,
    scenarios: List[Dict[str, Any]],
    temperature: float = 0.0,
) -> Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, float]]:
    """
    Create evaluator function for the-convergence.
    
    Args:
        model_provider: ModelProvider instance
        scenarios: List of test scenarios
        temperature: Temperature setting
    
    Returns:
        Evaluator function that takes (test_case, optimization_params) and returns metrics
    """
    def evaluator(test_case: Dict[str, Any], optimization_params: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate VN config using optimization params.
        
        Args:
            test_case: Test case dict (scenario)
            optimization_params: Optimization params from convergence (VN config as dict)
        
        Returns:
            Metrics dict: {"compliance": float, "token_reduction": float}
        """
        # Convert optimization params to VNConfig
        vn_config = VNConfig.from_dict(optimization_params)
        
        # Get scenario from test_case
        scenario = test_case.get("input", test_case)  # Support both formats
        prompt = scenario.get("prompt", scenario.get("text", ""))
        
        if not prompt:
            return {"compliance": 0.0, "token_reduction": 0.0}
        
        # Generate system prompt with symbol substitution
        system_prompt = vn_config.generate_system_prompt()
        
        # Run validation (compare VN vs baseline)
        try:
            # Get VN response
            vn_response = model_provider.create_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
            
            vn_content = vn_response.choices[0].message.content
            
            # Parse VN response
            from vector_native import parse_with_fallback
            parsed = parse_with_fallback(vn_content, hybrid=True)
            
            # Calculate compliance (1.0 if VN format, 0.0 otherwise)
            compliance = 1.0 if parsed["format"] == "vector_native" else 0.0
            
            # Calculate token reduction (simplified - compare to baseline)
            from vector_native import count_tokens
            vn_tokens = count_tokens(vn_content)
            
            # Estimate baseline (English) tokens (heuristic: ~2x VN tokens for similar content)
            # In practice, you'd run actual English baseline, but for optimization we use heuristic
            baseline_tokens = len(prompt.split()) * 1.3  # Rough token estimate
            token_reduction = max(0.0, (baseline_tokens - vn_tokens) / baseline_tokens) if baseline_tokens > 0 else 0.0
            
            return {
                "compliance": compliance,
                "token_reduction": token_reduction,
            }
        except Exception as e:
            # Return zero metrics on error
            return {"compliance": 0.0, "token_reduction": 0.0}
    
    return evaluator


def generate_search_space(
    symbol_options: Optional[Dict[str, List[str]]] = None,
    prompt_variants: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Generate search space for VN config optimization.
    
    Args:
        symbol_options: Dict mapping symbol roles to list of possible symbols
            e.g., {"attention": ["●", "*", "→"], "background": ["○", "·", "-"]}
        prompt_variants: List of prompt variant names
    
    Returns:
        Search space dict for ConvergenceConfig
    """
    if symbol_options is None:
        # Default symbol options
        symbol_options = {
            "attention": ["●", "*", "→"],
            "background": ["○", "·", "-"],
            "connection": ["━", "-", "→"],
        }
    
    if prompt_variants is None:
        # Get available variants
        try:
            from vector_native import list_prompt_variants
            prompt_variants = list_prompt_variants()
        except Exception:
            prompt_variants = ["strict", "balanced", "minimal"]
    
    # Build search space parameters
    parameters = {}
    
    # Symbol parameters (categorical choices)
    for role, symbols in symbol_options.items():
        parameters[f"symbols.{role}"] = {
            "type": "categorical",
            "choices": symbols,
        }
    
    # Prompt variant parameter
    parameters["prompt_variant"] = {
        "type": "categorical",
        "choices": prompt_variants,
    }
    
    # Custom prompt is not searchable initially (can be added later)
    # For now, we only search symbol combinations and prompt variants
    
    return parameters


def create_convergence_config(
    model_name: str,
    scenarios: List[Dict[str, Any]],
    search_space_config: Optional[Dict[str, Dict[str, Any]]] = None,
    generations: int = 10,
    population: int = 20,
    compliance_weight: float = 0.7,
    token_reduction_weight: float = 0.3,
) -> ConvergenceConfig:
    """
    Create ConvergenceConfig for VN optimization.
    
    Args:
        model_name: Model identifier
        scenarios: List of test scenarios
        search_space_config: Optional custom search space (uses default if not provided)
        generations: Number of optimization generations
        population: Population size per generation
        compliance_weight: Weight for compliance metric (default: 0.7)
        token_reduction_weight: Weight for token reduction metric (default: 0.3)
    
    Returns:
        ConvergenceConfig instance
    """
    if not CONVERGENCE_AVAILABLE:
        raise ImportError("the-convergence not available. Install with: pip install the-convergence")
    
    # Generate search space if not provided
    if search_space_config is None:
        search_space_config = generate_search_space()
    
    # Create config
    config = ConvergenceConfig(
        api=ApiConfig(
            name=f"vn_optimization_{model_name}",
            kind="callable",  # We use callable evaluator, not HTTP endpoint
        ),
        search_space=SearchSpaceConfig(
            parameters=search_space_config,
        ),
        runner=RunnerConfig(
            generations=generations,
            population=population,
        ),
        evaluation=EvaluationConfig(
            required_metrics=["compliance", "token_reduction"],
            weights={
                "compliance": compliance_weight,
                "token_reduction": token_reduction_weight,
            },
        ),
    )
    
    return config

