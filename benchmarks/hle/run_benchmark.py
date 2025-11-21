#!/usr/bin/env python3
"""
Quick start script for HLE benchmark
Can be run directly: python benchmarks/hle/run_benchmark.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
benchmark_dir = Path(__file__).parent
project_root = benchmark_dir.parent.parent
sys.path.insert(0, str(project_root))

from benchmarks.hle.runner import run_benchmark
from benchmarks.hle.config import load_config

if __name__ == "__main__":
    config = load_config()
    
    # Test with sample first
    if config.sample_size:
        print(f"Running with sample size: {config.sample_size}")
        results = run_benchmark(config)
        
        # Check if full dataset should run
        import os
        if os.getenv("FULL_DATASET", "").lower() == "true":
            config.sample_size = None
            print("\nRunning full dataset...")
            results = run_benchmark(config)
    else:
        # Run full dataset
        results = run_benchmark(config)

