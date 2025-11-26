"""
Vector-Native Optimization Framework

Unified framework for VN validation + optimization, eliminating hardcoded configs
and enabling systematic VN improvement across models.
"""

from .model_provider import ModelProvider, create_model_provider
from .vn_config import VNConfig
from .framework import VNOptimizationFramework
from .convergence_adapter import (
    create_vn_evaluator,
    generate_search_space,
    create_convergence_config,
)
from .optimizer import optimize_for_model
from .config_registry import ConfigRegistry

__all__ = [
    "ModelProvider",
    "create_model_provider",
    "VNConfig",
    "VNOptimizationFramework",
    "create_vn_evaluator",
    "generate_search_space",
    "create_convergence_config",
    "optimize_for_model",
    "ConfigRegistry",
]

