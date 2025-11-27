# Vector-Native Test Suite

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run token savings test (fast, no API key needed for dry run)
python tests/test_max_savings.py --variant minimal

# Run with quality evaluation (requires API key)
python tests/test_max_savings.py --evaluate

# Run quality-focused tests
python tests/test_quality.py --test all
```

## Prerequisites

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional (for fallback or alternative models)
export GOOGLE_API_KEY="..."           # For Gemini fallback
export ANTHROPIC_API_KEY="sk-ant-..." # For Claude (if preferred)
```

## Automatic Fallback

The LLM client automatically tries fallback models if the primary model fails:

**Fallback order:** `gpt-4o-mini` → `gemini-1.5-flash` → `gpt-4o`

This means:
- If your primary model (e.g., `gpt-4o`) has rate limits or errors, it will try alternatives
- You only need ONE working API key for tests to succeed
- Fallback is enabled by default (disable with `fallback=False` in code)

---

## Test Suites

### 1. Max Savings Test (`test_max_savings.py`)

**Purpose:** Measures token reduction in scenarios that maximize VN's advantage (verbose prose → structured VN).

**Target:** 60-80% token savings with acceptable quality.

```bash
# Basic usage (uses minimal VN variant)
python tests/test_max_savings.py

# Use standard variant (higher compliance, slightly less savings)
python tests/test_max_savings.py --variant standard

# Run single scenario by index
python tests/test_max_savings.py --scenario 0

# Test both variants
python tests/test_max_savings.py --all-variants

# With quality evaluation (uses LLM-as-judge, defaults to gpt-4o)
python tests/test_max_savings.py --evaluate

# Specify different judge model
python tests/test_max_savings.py --evaluate --judge-model gemini-1.5-pro

# Specify executor model
python tests/test_max_savings.py --model gpt-4o-mini
```

**Output:** Results saved to `test_results/max_savings_*.json`

**Metrics:**
- Token savings % (baseline vs VN)
- VN compliance % (lines starting with ●/⊕)
- Quality scores (if `--evaluate` used)

---

### 2. Quality Test (`test_quality.py`)

**Purpose:** Evaluates VN output quality using LLM-as-judge methodology.

**Focus areas:**
- **Semantic preservation** - Does VN retain all original meaning?
- **Roundtrip fidelity** - Can VN be decoded back to English accurately?
- **Information density** - Is content efficiently compressed?

```bash
# Run all quality tests
python tests/test_quality.py --test all

# Run specific test type
python tests/test_quality.py --test semantic
python tests/test_quality.py --test roundtrip
python tests/test_quality.py --test density

# Specify models
python tests/test_quality.py --model gpt-4o-mini --judge-model gpt-4o

# Use different VN variant
python tests/test_quality.py --variant standard
```

**Output:** Results saved to `test_results/quality_test_*.json`

**Passing criteria:**
- Semantic preservation: ≥7/10
- Roundtrip fidelity: ≥7/10
- Information density: ≥30% compression

---

### 3. Token Reduction Test (`test_token_reduction.py`)

**Purpose:** Original test suite measuring token reduction across scenarios.

```bash
python tests/test_token_reduction.py
```

---

### 4. Parser Test (`test_parser_hybrid.py`)

**Purpose:** Tests VN parsing logic for hybrid notation.

```bash
python tests/test_parser_hybrid.py
```

---

## Test Scenarios

### Location: `test_cases/`

| File | Description |
|------|-------------|
| `max_savings_scenarios.json` | High-compression scenarios (instructions, specs, state machines) |
| `scenarios.json` | General token reduction scenarios |

### Adding New Scenarios

Edit the JSON files:

```json
{
  "name": "My New Scenario",
  "description": "What this tests",
  "baseline_prompt": "Prompt for verbose baseline response",
  "vn_prompt": "Prompt for VN format response",
  "target_savings_pct": 50
}
```

---

## Quality Evaluation Framework

The `evaluation/` module provides LLM-as-judge evaluation:

```python
from evaluation import LLMJudge, LLMClient

# Initialize (with automatic fallback on failure)
client = LLMClient()
judge = LLMJudge(
    llm_client=client,
    judge_model="gpt-4o",        # Different from executor to avoid bias
    executor_model="gpt-4o-mini"
)

# Evaluate VN quality
score = judge.evaluate_vn_quality(
    original_content="Your original content here",
    vn_output="●content|type:vn|..."
)
print(f"Score: {score.overall_score}/10")
print(f"Reasoning: {score.reasoning}")

# Evaluate roundtrip fidelity
score = judge.evaluate_roundtrip(
    original_content="Original",
    vn_intermediate="●vn|...",
    reconstructed_content="Reconstructed from VN"
)
```

### Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Semantic Preservation | 40% | Does VN retain ALL original meaning? |
| Information Density | 25% | Content per token ratio |
| Structural Clarity | 20% | Consistent VN syntax, logical grouping |
| Completeness | 15% | All required information present |

---

## VN Prompt Variants

Located in `prompts/vn_base/`:

| Variant | Compliance | Token Savings | Best For |
|---------|------------|---------------|----------|
| `minimal` | ~40% | ~95% | Maximum compression testing |
| `standard` | ~80% | ~89% | Production use |

---

## Results

All test results are saved to `test_results/`:

```
test_results/
├── max_savings_*.json         # Token savings test results
├── quality_test_*.json        # Quality evaluation results
└── token_reduction_*.json     # Legacy test results
```

### Sample Result Structure

```json
{
  "metadata": {
    "timestamp": "2024-11-27T10:30:00",
    "model": "gpt-4o-mini",
    "judge_model": "gpt-4o"
  },
  "summary": {
    "avg_savings_pct": 73.2,
    "avg_compliance": 0.85,
    "quality_evaluation": {
      "avg_baseline_quality": 7.8,
      "avg_vn_quality": 7.5,
      "quality_preserved_pct": 100.0
    }
  },
  "results": [...]
}
```

---

## Troubleshooting

### "OPENAI_API_KEY not found"
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### "Evaluation module not available"
```bash
pip install scipy anthropic google-generativeai pydantic
```

### Import errors
```bash
# Run from repo root
cd vector-native
python tests/test_max_savings.py
```

---

## Contributing

1. Add scenarios to `test_cases/*.json`
2. Create new test files following the pattern
3. Run tests and verify results
4. Submit PR with test results

Ideas for improvement:
- CI/CD integration (GitHub Actions)
- Visual reports (matplotlib charts)
- Performance benchmarks
- Coverage reports
