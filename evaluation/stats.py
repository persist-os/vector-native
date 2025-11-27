"""
Statistical Analysis - Rigorous statistical comparison of baseline vs treatment.

Uses scipy for t-tests, effect size calculations, and confidence intervals.
"""

import numpy as np
from scipy import stats
from typing import List
from .models import EvaluationScore, StatisticalAnalysis


class StatisticalAnalyzer:
    """Performs statistical analysis on experiment results."""
    
    @staticmethod
    def analyze(
        baseline_scores: List[EvaluationScore],
        treatment_scores: List[EvaluationScore],
        alpha: float = 0.05
    ) -> StatisticalAnalysis:
        """
        Perform statistical analysis comparing baseline and treatment.
        
        Args:
            baseline_scores: Scores from baseline condition
            treatment_scores: Scores from treatment condition
            alpha: Significance level (default 0.05)
            
        Returns:
            StatisticalAnalysis with all metrics
        """
        # Extract overall scores
        baseline_values = np.array([s.overall_score for s in baseline_scores])
        treatment_values = np.array([s.overall_score for s in treatment_scores])
        
        # Basic statistics
        baseline_mean = float(np.mean(baseline_values))
        treatment_mean = float(np.mean(treatment_values))
        baseline_std = float(np.std(baseline_values, ddof=1)) if len(baseline_values) > 1 else 0.0
        treatment_std = float(np.std(treatment_values, ddof=1)) if len(treatment_values) > 1 else 0.0
        
        # Improvement percentage
        if baseline_mean > 0:
            improvement_percent = ((treatment_mean - baseline_mean) / baseline_mean) * 100
        else:
            improvement_percent = 0.0
        
        # T-test (independent samples)
        if len(baseline_values) > 1 and len(treatment_values) > 1:
            t_stat, p_value = stats.ttest_ind(baseline_values, treatment_values)
            p_value = float(p_value)
        else:
            p_value = 1.0  # Not enough samples for t-test
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt((baseline_std**2 + treatment_std**2) / 2)
        if pooled_std > 0:
            effect_size = (treatment_mean - baseline_mean) / pooled_std
        else:
            effect_size = 0.0
        
        # 95% Confidence interval for treatment mean
        if len(treatment_values) > 1:
            ci = stats.t.interval(
                0.95,
                len(treatment_values) - 1,
                loc=treatment_mean,
                scale=stats.sem(treatment_values)
            )
            confidence_interval_95 = (float(ci[0]), float(ci[1]))
        else:
            confidence_interval_95 = (treatment_mean, treatment_mean)
        
        return StatisticalAnalysis(
            baseline_mean=baseline_mean,
            treatment_mean=treatment_mean,
            baseline_std=baseline_std,
            treatment_std=treatment_std,
            improvement_percent=improvement_percent,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval_95=confidence_interval_95,
            sample_size=len(treatment_values)
        )
    
    @staticmethod
    def interpret_effect_size(effect_size: float) -> str:
        """
        Interpret Cohen's d effect size.
        
        Args:
            effect_size: Cohen's d value
            
        Returns:
            Human-readable interpretation
        """
        abs_effect = abs(effect_size)
        if abs_effect < 0.2:
            return "negligible"
        elif abs_effect < 0.5:
            return "small"
        elif abs_effect < 0.8:
            return "medium"
        else:
            return "large"
    
    @staticmethod
    def is_significant(p_value: float, alpha: float = 0.05) -> bool:
        """Check if result is statistically significant."""
        return p_value < alpha
    
    @staticmethod
    def generate_recommendation(
        validated: bool,
        effect_size: float,
        improvement_percent: float,
        confidence: float,
        token_savings_percent: float = 0.0
    ) -> str:
        """
        Generate actionable recommendation based on VN evaluation results.
        
        Args:
            validated: Whether quality was maintained
            effect_size: Cohen's d effect size
            improvement_percent: Quality improvement percentage (negative = quality loss)
            confidence: Confidence level (0-1)
            token_savings_percent: Token savings from VN format
            
        Returns:
            Recommendation string
        """
        effect_interpretation = StatisticalAnalyzer.interpret_effect_size(effect_size)
        
        # VN-specific: Quality maintenance is the goal, not improvement
        # Small negative effect is acceptable if token savings are significant
        
        if not validated and improvement_percent < -10:
            return (
                f"DO NOT DEPLOY VN: Significant quality loss detected "
                f"({improvement_percent:.1f}% quality reduction). "
                f"Token savings ({token_savings_percent:.1f}%) do not justify quality loss. "
                f"Consider refining VN prompts or using standard format."
            )
        
        if validated and token_savings_percent > 30:
            if abs(improvement_percent) < 5:
                return (
                    f"DEPLOY VN: Quality maintained (within 5% of baseline) with "
                    f"{token_savings_percent:.1f}% token savings. "
                    f"Effect size is {effect_interpretation}. "
                    f"VN format recommended for this use case."
                )
            elif improvement_percent > 0:
                return (
                    f"STRONGLY DEPLOY VN: Quality improved by {improvement_percent:.1f}% "
                    f"with {token_savings_percent:.1f}% token savings. "
                    f"Effect size is {effect_interpretation}. "
                    f"VN format outperforms baseline."
                )
            else:
                return (
                    f"DEPLOY WITH MONITORING: Minor quality reduction ({improvement_percent:.1f}%) "
                    f"offset by {token_savings_percent:.1f}% token savings. "
                    f"Effect size is {effect_interpretation}. "
                    f"Monitor quality metrics in production."
                )
        
        if token_savings_percent < 20:
            return (
                f"INSUFFICIENT SAVINGS: Token savings ({token_savings_percent:.1f}%) "
                f"are below the 20% threshold for VN benefit. "
                f"Quality change: {improvement_percent:.1f}%. "
                f"Consider refining VN prompts for better compression."
            )
        
        return (
            f"FURTHER TESTING NEEDED: Results inconclusive. "
            f"Quality change: {improvement_percent:.1f}%, token savings: {token_savings_percent:.1f}%. "
            f"Run additional iterations to confirm results."
        )
    
    @staticmethod
    def calculate_quality_confidence(
        p_value: float,
        effect_size: float,
        sample_size: int
    ) -> float:
        """
        Calculate overall confidence in quality assessment.
        
        Args:
            p_value: Statistical significance p-value
            effect_size: Cohen's d effect size
            sample_size: Number of samples
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence from p-value (inverted - lower p = higher confidence)
        p_confidence = max(0, 1 - p_value)
        
        # Penalty for small sample sizes
        sample_penalty = min(1, sample_size / 10)  # Full confidence at n=10+
        
        # Adjust for effect size (small effects need more samples)
        effect_factor = 1.0
        if abs(effect_size) < 0.2 and sample_size < 20:
            effect_factor = 0.8  # Reduce confidence for small effects with few samples
        
        return min(1.0, p_confidence * sample_penalty * effect_factor)

