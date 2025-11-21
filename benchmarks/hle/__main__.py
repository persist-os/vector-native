"""
Entry point for HLE benchmark
Allows running as: python -m benchmarks.hle
"""
from .runner import run_benchmark
from .config import load_config

if __name__ == "__main__":
    config = load_config()
    results = run_benchmark(config)

