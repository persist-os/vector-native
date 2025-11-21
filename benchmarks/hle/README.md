# HLE Benchmark: Vector-Native Reasoning Accuracy

## Overview

This benchmark tests whether Vector-Native (VN) improves reasoning accuracy compared to Natural Language (NL) by reducing translation overhead.

**Hypothesis:** VN → Higher accuracy due to reduced translation overhead

## Structure

- `config.py` - Configuration management
- `dataset_loader.py` - Loads cais/hle dataset from HuggingFace
- `prompt_templates.py` - Generates NL and VN prompts
- `evaluator.py` - Extracts answers and validates predictions
- `metrics.py` - Calculates accuracy and token metrics
- `runner.py` - Orchestrates complete benchmark execution

## Setup

1. Install dependencies:
```bash
pip install datasets anthropic python-dotenv
```

2. Set environment variables:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

3. Optional configuration:
```bash
export HLE_MODEL=claude-sonnet-4-20250514
export HLE_TEMPERATURE=0.0
export HLE_SAMPLE_SIZE=10  # Test with first 10 examples
```

## Usage

### Run with sample (10 examples):
```bash
cd benchmarks/hle
python runner.py
```

### Run full dataset:
```bash
export FULL_DATASET=true
python runner.py
```

### Programmatic usage:
```python
from benchmarks.hle.runner import run_benchmark
from benchmarks.hle.config import BenchmarkConfig

config = BenchmarkConfig(
    sample_size=10,
    model="claude-sonnet-4-20250514",
    temperature=0.0,
)

results = run_benchmark(config)
```

## Output

Results are saved to `benchmarks/hle/results/`:

- `predictions_nl.json` - NL predictions and evaluations
- `predictions_vn.json` - VN predictions and evaluations
- `comparison.json` - Complete comparison with metrics
- `metrics.json` - Calculated metrics summary

## Metrics

**Primary Metric:** Accuracy (exact_match)

**Secondary Metric:** Token reduction

**Validation Modes:**
- `exact_match` - Exact letter match (A/B/C/D/E)
- `flexible` - Case-insensitive, whitespace-tolerant
- `multiple_choice` - Normalized to single letter

## Critical Requirements

**VN Prompts MUST:**
- Emphasize NO english reasoning
- Require ONLY vn symbols
- Use ultra_strict variant by default
- Inject global.mdc if available

## Flow

1. **Load** - Load cais/hle test split
2. **Prompt NL** - Generate natural language prompts
3. **Prompt VN** - Generate vector-native prompts (ultra_strict)
4. **Extract Answers** - NL: `ANSWER: A` regex, VN: `●answer|value:A` pattern
5. **Validate** - Compare against correct answers
6. **Calculate Metrics** - Accuracy, tokens, delta, reduction percentage

## Expected Results

- **Accuracy:** VN should match or exceed NL accuracy
- **Tokens:** VN should show significant token reduction (80-95%)
- **Delta:** Positive delta indicates VN improvement

