"""
LLM Judge - Evaluates VN outputs using LLM reasoning instead of brittle metrics.

Features:
- YAML-based prompt templates for flexibility
- VN-aware evaluation (understands quality vs compression tradeoffs)
- Unbiased scoring (uses different model by default)
- Batch evaluation support
"""

import logging
from typing import List, Optional

from .llm_client import LLMClient
from .models import EvaluationScore, VNExperimentConfig, ParsedVNHypothesis

# Handle both package import and direct import
try:
    from prompts.loader import get_prompt_loader
    from utils.json_parser import parse_json_with_retry
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from prompts.loader import get_prompt_loader
    from utils.json_parser import parse_json_with_retry

logger = logging.getLogger(__name__)


class LLMJudge:
    """
    Evaluates VN outputs using LLM-as-judge methodology.
    
    Self-aware: Understands its role as measurement instrument in scientific
    experiments. Maintains rigorous consistency and objectivity.
    
    Unbiased: Uses different model than executor by default to prevent
    model-specific biases from affecting evaluation.
    
    VN-aware: Evaluates semantic preservation and information density,
    not just surface-level similarity.
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        judge_model: str = "gpt-4o",  # Default to OpenAI (use different model than executor)
        executor_model: str = "gpt-4o-mini"
    ):
        """
        Initialize the LLM Judge.
        
        Args:
            llm_client: LLM client instance (created if not provided)
            judge_model: Model to use for judging (should differ from executor)
            executor_model: Model used by executor (for bias warning)
        """
        self.llm = llm_client or LLMClient()
        self.judge_model = judge_model
        self.executor_model = executor_model
        self.prompt_loader = get_prompt_loader()
        
        # Ensure judge and executor use different models for unbiased evaluation
        if self.judge_model.lower() == self.executor_model.lower():
            logger.warning(
                f"Judge and executor using same model ({self.judge_model}). "
                "This may introduce bias. Consider using different models."
            )
    
    def evaluate(
        self,
        output: str,
        task: str,
        criteria: Optional[List[str]] = None
    ) -> EvaluationScore:
        """
        Evaluate a single output against task criteria.
        
        Args:
            output: The output to evaluate
            task: Task description for context
            criteria: Evaluation criteria (defaults to VN quality criteria)
            
        Returns:
            EvaluationScore with scores and reasoning
        """
        if criteria is None:
            criteria = [
                "Semantic preservation - Does output retain all original meaning?",
                "Information density - Is content efficiently conveyed?",
                "Structural clarity - Is output well-organized?",
                "Completeness - Is all required information present?"
            ]
        
        criteria_list = "\n".join([f"- {c}" for c in criteria])
        
        # Build prompt from YAML template
        prompt = self.prompt_loader.build_prompt(
            prompt_name="evaluation/judge",
            template_key="simple_evaluation_template",
            task=task,
            output=output,
            criteria_list=criteria_list
        )
        
        # Get configuration
        temperature = self.prompt_loader.get_config("evaluation/judge", "temperature", 0.2)
        max_tokens = self.prompt_loader.get_config("evaluation/judge", "max_tokens", 1500)
        system_context = self.prompt_loader.get_system_context("evaluation/judge")
        
        try:
            response = self.llm.call(
                prompt,
                model=self.judge_model,
                temperature=temperature,
                max_tokens=max_tokens,
                system=system_context
            )
        except Exception as e:
            raise ValueError(f"Failed to call LLM judge: {e}")
        
        # Parse JSON response
        try:
            eval_data = parse_json_with_retry(response)
            
            return EvaluationScore(
                overall_score=eval_data["overall_score"],
                criterion_scores=eval_data.get("criterion_scores", {}),
                reasoning=eval_data["reasoning"],
                output_text=output
            )
        except Exception as e:
            raise ValueError(f"Failed to parse evaluation: {e}\nResponse: {response[:500]}...")
    
    def evaluate_vn_quality(
        self,
        original_content: str,
        vn_output: str
    ) -> EvaluationScore:
        """
        Evaluate a VN output against its original content.
        
        Specialized evaluation for VN translation quality.
        
        Args:
            original_content: The original content that was translated to VN
            vn_output: The VN-formatted output
            
        Returns:
            EvaluationScore with VN-specific criteria
        """
        # Build prompt from YAML template
        prompt = self.prompt_loader.build_prompt(
            prompt_name="evaluation/judge",
            template_key="vn_quality_evaluation_template",
            original_content=original_content,
            vn_output=vn_output
        )
        
        # Get configuration
        temperature = self.prompt_loader.get_config("evaluation/judge", "temperature", 0.2)
        max_tokens = self.prompt_loader.get_config("evaluation/judge", "max_tokens", 1500)
        system_context = self.prompt_loader.get_system_context("evaluation/judge")
        
        try:
            response = self.llm.call(
                prompt,
                model=self.judge_model,
                temperature=temperature,
                max_tokens=max_tokens,
                system=system_context
            )
        except Exception as e:
            raise ValueError(f"Failed to call LLM judge for VN quality: {e}")
        
        # Parse JSON response
        try:
            eval_data = parse_json_with_retry(response)
            
            # Include VN-specific issues in reasoning
            reasoning = eval_data["reasoning"]
            if eval_data.get("semantic_issues"):
                reasoning += f" Semantic issues: {eval_data['semantic_issues']}"
            if eval_data.get("missing_information"):
                reasoning += f" Missing: {eval_data['missing_information']}"
            
            return EvaluationScore(
                overall_score=eval_data["overall_score"],
                criterion_scores=eval_data.get("criterion_scores", {}),
                reasoning=reasoning,
                output_text=vn_output
            )
        except Exception as e:
            raise ValueError(f"Failed to parse VN evaluation: {e}\nResponse: {response[:500]}...")
    
    def evaluate_batch(
        self,
        outputs: List[str],
        task: str,
        criteria: Optional[List[str]] = None,
        verbose: bool = True
    ) -> List[EvaluationScore]:
        """
        Evaluate multiple outputs.
        
        Args:
            outputs: List of outputs to evaluate
            task: Task description for context
            criteria: Evaluation criteria
            verbose: Print progress
            
        Returns:
            List of EvaluationScores
        """
        scores = []
        for i, output in enumerate(outputs):
            if verbose:
                print(f"  Evaluating output {i+1}/{len(outputs)}...")
            score = self.evaluate(output, task, criteria)
            scores.append(score)
        return scores
    
    def evaluate_roundtrip(
        self,
        original_content: str,
        vn_intermediate: str,
        reconstructed_content: str
    ) -> EvaluationScore:
        """
        Evaluate a VN roundtrip (Original → VN → English reconstruction).
        
        Tests whether VN can faithfully encode and decode information.
        
        Args:
            original_content: Original English content
            vn_intermediate: VN-encoded intermediate
            reconstructed_content: English reconstructed from VN
            
        Returns:
            EvaluationScore with roundtrip fidelity metrics
        """
        prompt = self.prompt_loader.build_prompt(
            prompt_name="evaluation/judge",
            template_key="roundtrip_evaluation_template",
            original_content=original_content,
            vn_intermediate=vn_intermediate,
            reconstructed_content=reconstructed_content
        )
        
        temperature = self.prompt_loader.get_config("evaluation/judge", "temperature", 0.2)
        max_tokens = self.prompt_loader.get_config("evaluation/judge", "max_tokens", 1500)
        system_context = self.prompt_loader.get_system_context("evaluation/judge")
        
        try:
            response = self.llm.call(
                prompt,
                model=self.judge_model,
                temperature=temperature,
                max_tokens=max_tokens,
                system=system_context
            )
        except Exception as e:
            raise ValueError(f"Failed to call LLM judge for roundtrip: {e}")
        
        try:
            eval_data = parse_json_with_retry(response)
            
            reasoning = eval_data["reasoning"]
            if eval_data.get("information_lost"):
                reasoning += f" Lost: {eval_data['information_lost']}"
            if eval_data.get("information_added"):
                reasoning += f" Added: {eval_data['information_added']}"
            
            return EvaluationScore(
                overall_score=eval_data["overall_score"],
                criterion_scores={
                    "fidelity": eval_data.get("fidelity_score", eval_data["overall_score"]),
                    "structural_match": eval_data.get("structural_match_score", 0)
                },
                reasoning=reasoning,
                output_text=reconstructed_content
            )
        except Exception as e:
            raise ValueError(f"Failed to parse roundtrip evaluation: {e}\nResponse: {response[:500]}...")
    
    def generate_comparison_summary(
        self,
        n_baseline: int,
        n_treatment: int,
        baseline_mean: float,
        treatment_mean: float,
        improvement_percent: float,
        p_value: float,
        effect_size: float,
        effect_interpretation: str,
        baseline_tokens: int = 0,
        treatment_tokens: int = 0,
        token_savings_percent: float = 0.0
    ) -> str:
        """
        Generate a comparison summary of baseline vs treatment results.
        
        Provides qualitative analysis of quantitative results.
        
        Returns:
            Summary string with analysis and recommendation
        """
        prompt = self.prompt_loader.build_prompt(
            prompt_name="evaluation/judge",
            template_key="comparison_summary_template",
            n_baseline=n_baseline,
            n_treatment=n_treatment,
            baseline_mean=baseline_mean,
            treatment_mean=treatment_mean,
            improvement_percent=improvement_percent,
            p_value=p_value,
            effect_size=effect_size,
            effect_interpretation=effect_interpretation,
            baseline_tokens=baseline_tokens,
            treatment_tokens=treatment_tokens,
            token_savings_percent=token_savings_percent
        )
        
        temperature = self.prompt_loader.get_config("evaluation/judge", "temperature", 0.2)
        max_tokens = self.prompt_loader.get_config("evaluation/judge", "max_tokens", 1500)
        
        try:
            response = self.llm.call(
                prompt,
                model=self.judge_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to generate comparison summary: {e}")
            return "Unable to generate comparison summary."

