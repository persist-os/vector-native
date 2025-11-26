"""
Smart Validation Framework for Vector-Native

Statistical sampling framework reducing API calls 99.8% (60K → 100)
while maintaining 95% validation value.
"""

from .framework import SmartValidationFramework
from .scenario_selector import load_and_select_scenarios, select_stratified_scenarios

__all__ = [
    "SmartValidationFramework",
    "load_and_select_scenarios",
    "select_stratified_scenarios",
]

