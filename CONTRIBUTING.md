# Contributing to Vector-Native

Thank you for your interest in contributing to Vector-Native. This project is an open-source effort to develop and refine a symbol-based language that optimizes token usage in LLM interactions while maintaining readability. We welcome contributions that advance this goal through empirical testing and iterative improvements.

## Introduction

Vector-Native aims to provide a shared framework for exploring efficient syntax in AI-to-AI communication. Contributions from the community help us test variants, expand applicability, and validate performance across models and use cases. Whether you're experimenting with system prompts, adding test scenarios, or enhancing the core implementation, your input supports a more precise and cost-effective approach to prompting LLMs.

By participating, you join a collaborative space to define patterns that reduce cognitive overhead in prompt engineering and improve operational efficiency.

## Ways to Contribute

### System Prompts
The core of Vector-Native lies in system prompts that guide LLMs in translating natural language to vector-native syntax. Creating or refining these is the most accessible entry point.

- **Develop Variants:** Create prompts similar to `strict.txt`, `balanced.txt`, or `minimal.txt`. Experiment with instruction phrasing, example inclusion, and output delimiters to balance compliance and token reduction.
- **Test Configurations:** Evaluate prompts with different temperatures (e.g., 0.1 for strict compliance, 0.5 for flexibility) or models (e.g., GPT-4o-mini, Claude).
- **Domain-Specific Prompts:** Adapt prompts for specialized areas like code generation or data analysis, documenting how they perform on relevant tasks.
- **Multi-Language Support:** Explore prompts that handle non-English inputs, assessing token efficiency in diverse linguistic contexts.

Add your prompt to the `prompts/` directory with a descriptive filename (e.g., `domain-specific.txt`). Include a header comment with metadata: purpose, target compliance, recommended temperature, and test results.

### Tests and Scenarios
Empirical validation is key. Contributions to testing ensure reliable benchmarks.

- **New Scenarios:** Expand `tests/test_cases/scenarios.json` with diverse inputs (short/long prompts, various complexities) to measure token reduction and compliance.
- **Test Scripts:** Enhance `test_token_reduction.py` or add scripts for multi-model evaluation (e.g., integrating Anthropic or Google APIs).
- **Benchmarking:** Run tests across temperatures, models, or prompt lengths, and submit results to compare variants.

This helps identify patterns that consistently achieve high token savings without sacrificing accuracy.

### Core Enhancements
For those interested in implementation details:

- **Parser Improvements:** Refine `vector_native/parser.py` to better handle symbol sequences or edge cases in vector-native syntax.
- **Tokenizer Utilities:** Update `vector_native/tokenizer.py` for more accurate token counting across providers.
- **LLM Integration:** Extend `vector_native/llm_integration.py` to support additional APIs or output parsing.

Focus on maintainability and include tests for changes.

### Documentation
Clear resources aid adoption and collaboration.

- **Guides and Examples:** Update docs like `how-to-read.md` or `examples.md` with new patterns or use cases.
- **FAQs and Tutorials:** Address common questions or add quickstarts for specific contributions (e.g., "Testing Your Prompt").

Ensure additions are concise and reference the language spec.

### Other Contributions
- **Conceptual Refinements:** Propose extensions to `LANGUAGE_SPEC.md`, such as new symbols or syntax rules, backed by tests.
- **Performance Analysis:** Analyze token impacts in real-world scenarios (e.g., agent chains) and share findings.

## General Guidelines

- **Empirical Focus:** Base contributions on measurable outcomes, such as token reduction percentages or compliance rates from tests.
- **Testing:** Run `python tests/test_token_reduction.py` before submitting. Aim for improvements in efficiency or robustness.
- **Documentation Standards:** Use Markdown consistently. For code, follow PEP 8; include docstrings explaining vector-native mappings.
- **Precision Over Speculation:** Highlight factual benefits (e.g., observed token savings) rather than untested assumptions.
- **Inclusivity:** Contributions should support broad applicability, including multi-language and domain variants.

## Submission Process

1. **Fork the Repository:** Create a fork on GitHub.
2. **Create a Branch:** Use a descriptive name (e.g., `add-domain-prompt` or `enhance-parser`).
3. **Make Changes:** Implement your contribution, test thoroughly, and update documentation.
4. **Commit and Push:** Commit with clear messages (e.g., "Add finance-domain system prompt with 85% compliance").
5. **Open a Pull Request:** Describe the changes, include test results, and reference any issues.
6. **Review and Iterate:** Respond to feedback to ensure alignment with project goals.

We review PRs promptly and appreciate detailed descriptions of your testing process.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct.html). By participating, you agree to uphold respectful and inclusive collaboration. Reports of violations can be directed to the project maintainers.

## Get Help or Discuss Ideas

- Join discussions on GitHub Issues or Discussions.
- For questions, open an Issue labeled "question" or "help wanted".

Your contributions make Vector-Native a more robust tool for efficient AI communication. We look forward to your involvement!
