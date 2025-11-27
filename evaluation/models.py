"""
Data models for VN quality evaluation.

Uses Pydantic for validation and type safety.
Adapted from cognitive-substrate - simplified for VN testing.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class EvaluationScore(BaseModel):
    """Score from LLM judge for a single output."""
    
    overall_score: float = Field(..., ge=0, le=10, description="Overall quality score (0-10)")
    criterion_scores: Dict[str, float] = Field(default_factory=dict, description="Scores per criterion")
    reasoning: str = Field(..., description="Judge's reasoning for the score")
    output_text: str = Field(..., description="The output that was evaluated")
    

class StatisticalAnalysis(BaseModel):
    """Statistical analysis of baseline vs treatment."""
    
    baseline_mean: float
    treatment_mean: float
    baseline_std: float
    treatment_std: float
    improvement_percent: float
    p_value: float
    effect_size: float  # Cohen's d
    confidence_interval_95: tuple[float, float]
    sample_size: int


class VNExperimentConfig(BaseModel):
    """Configuration for a VN translation quality experiment."""
    
    task: str = Field(..., description="Concrete task to test on")
    baseline_prompt: str = Field(..., description="Control condition prompt (standard English)")
    treatment_prompt: str = Field(..., description="Treatment condition prompt (VN format)")
    evaluation_criteria: List[str] = Field(..., description="Criteria for judging quality")
    vn_variant: str = Field(default="standard", description="VN prompt variant used")
    

class VNEvaluationResult(BaseModel):
    """Result of a VN quality evaluation."""
    
    task: str = Field(..., description="Task that was tested")
    validated: bool = Field(..., description="Whether VN quality was validated")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in result (0-1)")
    
    experiment_config: VNExperimentConfig
    statistical_analysis: StatisticalAnalysis
    
    baseline_scores: List[EvaluationScore]
    treatment_scores: List[EvaluationScore]
    
    # Token metrics
    baseline_tokens: int = Field(..., description="Average tokens in baseline outputs")
    treatment_tokens: int = Field(..., description="Average tokens in treatment outputs")
    token_savings_percent: float = Field(..., description="Token reduction percentage")
    
    recommendation: str = Field(..., description="Action recommendation based on results")
    
    # Sample outputs for inspection
    best_baseline_output: str
    best_treatment_output: str
    
    # Metadata
    timestamp: str
    iterations: int
    models_used: Dict[str, str]  # role -> model name
    
    class Config:
        json_schema_extra = {
            "example": {
                "task": "Summarize meeting notes",
                "validated": True,
                "confidence": 0.92,
                "token_savings_percent": 45.3,
                "recommendation": "Deploy VN format - quality maintained with significant token savings",
            }
        }


class ParsedVNHypothesis(BaseModel):
    """Structured representation of a VN quality hypothesis."""
    
    original_text: str
    independent_variable: str = Field(..., description="What changes between conditions (e.g., 'VN format')")
    dependent_variable: str = Field(..., description="What we measure (e.g., 'output quality')")
    expected_direction: Literal["increase", "decrease", "no_change", "maintain"] = Field(
        ..., description="Expected change direction"
    )
    testable: bool = Field(default=True, description="Whether this can be tested")
    reasoning: str = Field(..., description="Why this parsing makes sense")

