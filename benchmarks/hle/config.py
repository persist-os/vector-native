"""
Configuration for HLE Benchmark
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class BenchmarkConfig:
    """Configuration for HLE benchmark execution"""
    
    # Dataset configuration
    dataset_name: str = "cais/hle"
    dataset_split: str = "test"
    
    # Model configuration
    model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.0
    
    # VN protocol configuration
    vn_prompt_variant: str = "ultra_strict"  # Emphasizes NO english reasoning
    global_mdc_path: Optional[str] = None  # Will be set if exists
    
    # Extraction patterns
    nl_answer_pattern: str = r"ANSWER:\s*([A-Z])"  # Regex for NL answers
    vn_answer_pattern: str = r"●answer\|value:([A-Z])"  # Pattern for VN answers
    
    # Validation modes
    validation_modes: list[str] = None  # ["exact_match", "flexible", "multiple_choice"]
    
    # Output paths
    output_dir: Path = None
    
    # Test configuration
    sample_size: Optional[int] = 10  # Test with first N examples
    full_dataset_after_validation: bool = True
    
    def __post_init__(self):
        """Initialize default values"""
        if self.validation_modes is None:
            self.validation_modes = ["exact_match", "flexible", "multiple_choice"]
        
        if self.output_dir is None:
            # Default to benchmarks/hle/results/
            benchmark_dir = Path(__file__).parent
            self.output_dir = benchmark_dir / "results"
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to find global.mdc in plansandschemes
        if self.global_mdc_path is None:
            # Check relative path: ../../plansandschemes/.cursor/rules/global.mdc
            current_file = Path(__file__)
            potential_path = current_file.parent.parent.parent.parent / "plansandschemes" / ".cursor" / "rules" / "global.mdc"
            if potential_path.exists():
                self.global_mdc_path = str(potential_path)
    
    def get_output_paths(self) -> dict[str, Path]:
        """Get output file paths"""
        return {
            "predictions_nl": self.output_dir / "predictions_nl.json",
            "predictions_vn": self.output_dir / "predictions_vn.json",
            "comparison": self.output_dir / "comparison.json",
            "metrics": self.output_dir / "metrics.json",
        }


def load_config() -> BenchmarkConfig:
    """Load configuration from environment variables or defaults"""
    config = BenchmarkConfig()
    
    # Override with environment variables if present
    if os.getenv("HLE_DATASET_NAME"):
        config.dataset_name = os.getenv("HLE_DATASET_NAME")
    
    if os.getenv("HLE_MODEL"):
        config.model = os.getenv("HLE_MODEL")
    
    if os.getenv("HLE_TEMPERATURE"):
        config.temperature = float(os.getenv("HLE_TEMPERATURE"))
    
    if os.getenv("HLE_SAMPLE_SIZE"):
        config.sample_size = int(os.getenv("HLE_SAMPLE_SIZE"))
    
    return config

