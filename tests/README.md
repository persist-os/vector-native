# Tests README

## Overview

This is a very rudimentary testing setup for the vector-native project. It's designed to get started quickly but is far from comprehensive or sophisticated. The goal is to validate core functionality, particularly token reduction and compliance across different prompt variants and models.

Contributors are **strongly encouraged** to experiment with and propose new structures, frameworks, or approaches to make testing more robust, scalable, and automated. Feel free to refactor, add fixtures, integration tests, or even migrate to a full testing suite like pytest with more advanced features!

## Current Structure

- **`test_cases/`**: Contains test scenarios in JSON format (`scenarios.json`). Each scenario defines:
  - Input prompts or texts to process.
  - Expected outcomes (e.g., token reduction targets, compliance checks).
  - Variants (e.g., balanced, minimal, strict prompts).

- **`test_token_reduction.py`**: Main test script that:
  - Loads scenarios from `test_cases/scenarios.json`.
  - Runs token reduction tests using different prompt variants and models (e.g., GPT-4o-mini).
  - Measures reduction percentage and compliance.
  - Outputs results to `test_results/` as JSON files with timestamps.

- **`test_parallel_providers.py`**: A simple script for testing parallel execution across LLM providers (if applicable).

- **`test_results/`**: Auto-generated folder for test outputs. Each run produces a JSON file like `token_reduction_test_YYYYMMDD_HHMMSS_*.json` with metrics such as:
  - Reduction percentage.
  - Compliance rate.
  - Per-scenario details.

- **`test_parser_hybrid.py`**: Experimental tests for hybrid parsing logic.

## How to Add New Tests

1. **Add Scenarios**:
   - Edit `test_cases/scenarios.json` to include new test cases.
   - Each scenario should have:
     ```json
     {
       "id": "unique_id",
       "input": "Your test prompt or text here",
       "expected_reduction": 0.8,  // Target reduction (0-1)
       "expected_compliance": 0.9, // Target compliance (0-1)
       "variants": ["balanced", "minimal", "strict"]  // Optional: prompt variants to test
     }
     ```
   - Add as many scenarios as needed—focus on edge cases, real-world prompts, and varying lengths.

2. **Run Existing Tests**:
   - Install dependencies: `pip install -r requirements.txt`
   - Execute: `python -m pytest tests/` or run individual files like `python tests/test_token_reduction.py`.
   - Results will appear in `test_results/`. Compare against expectations.

3. **Create New Test Files**:
   - Add a new Python file in `tests/` (e.g., `test_new_feature.py`).
   - Use simple assertions or integrate with pytest if installed.
   - Example structure:
     ```python
     import pytest
     from vector_native import some_function

     def test_example():
         result = some_function("input")
         assert result.tokens_reduced > 0.5
     ```
   - Run with `pytest tests/test_new_feature.py -v`.

4. **Advanced Testing**:
   - For parallel provider tests: Modify `test_parallel_providers.py` to include new LLMs.
   - Generate results: Tests auto-save JSON outputs for review.

## Improving the Setup

This setup is basic—no fixtures, no CI integration, no coverage reports. Ideas for enhancements:
- Migrate to pytest with fixtures for reusable setups.
- Add unit tests for individual modules (e.g., parser, tokenizer).
- Integrate with CI/CD (GitHub Actions) for automated runs.
- Add visual reports (e.g., using matplotlib for token reduction charts).
- Expand `scenarios.json` schema for more complex tests (e.g., error handling, performance benchmarks).

If you have ideas or implement improvements, please:
- Open a PR with your changes.
- Update this README to reflect the new structure.
- Share in discussions for feedback.

Happy testing—and let's make this better together!
