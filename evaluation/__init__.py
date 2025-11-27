"""VN Quality Evaluation Framework.

Provides LLM-as-judge evaluation for Vector-Native outputs.
"""

from .models import (
    EvaluationScore,
    StatisticalAnalysis,
    VNExperimentConfig,
    VNEvaluationResult,
    ParsedVNHypothesis
)
from .llm_client import LLMClient
from .stats import StatisticalAnalyzer
from .judge import LLMJudge

__all__ = [
    # Models
    "EvaluationScore",
    "StatisticalAnalysis",
    "VNExperimentConfig",
    "VNEvaluationResult",
    "ParsedVNHypothesis",
    # Classes
    "LLMClient",
    "StatisticalAnalyzer",
    "LLMJudge",
]

