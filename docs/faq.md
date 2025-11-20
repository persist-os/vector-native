# FAQ

## Which variant should I start with?

**Easiest entry point:** `minimal` - Maximum token reduction (95.7%) with minimum system prompt overhead (4 lines).

**Observed results (gpt-4o-mini, 5 scenarios):**

| Variant | Compliance | Token Reduction | System Prompt Size |
|---------|-----------|-----------------|-------------------|
| **minimal** | 40% | 95.7% | Smallest (~4 lines) |
| **balanced** | 40% | 95.4% | Medium |
| **strict** | 80% | 88.8% | Largest |

**Open questions:**

- Does higher compliance justify larger prompt overhead?
- How does compliance vary across models and tasks?
- What's the optimal balance between prompt size and compliance?

**Reference:** [README.md](../README.md#the-evidence-massive-token-reduction) for test results.

---

## What happens if compliance is low?

**Observed symptom:** Model outputs English instead of Vector-Native symbols.

**Questions to explore:**

- Does strict variant consistently achieve higher compliance across models?
- How does temperature affect compliance for each variant?
- Can fallback parsing handle low-compliance scenarios gracefully?

**Potential approaches:**

- Try different variants (strict shows 80% compliance in limited tests)
- Experiment with temperature (lower may increase compliance, but needs validation)
- Add fallback parsing (detect English output, parse as natural language)
- Strengthen delimiters (`⟦...⟧` boundaries)
- Include examples in system prompt

**What have you observed?** Share your findings to help build collective knowledge.

**Reference:** [prompts/README.md](../prompts/README.md#common-issues) for troubleshooting ideas.

---

## What temperature should I use?

**Observed patterns (limited testing):**

| Variant | Temperature Range Tested | Compliance Observed |
|---------|------------------------|---------------------|
| strict | 0.1 - 0.2 | 80% |
| balanced | 0.3 - 0.5 | 40% |
| minimal | 0.5 - 0.7 | 40% |

**Open questions:**

- Does lower temperature always increase compliance?
- How does temperature interact with different models?
- What's the optimal temperature for your specific use case?

**Research direction:** Test temperature ranges systematically and share results.

**Reference:** [prompts/README.md](../prompts/README.md#temperature-recommendations) for initial observations.

---

## Can I mix Vector-Native with English?

**Unanswered questions:**

- Does hybrid usage reduce efficiency? (Needs measurement)
- How does mixing affect compliance rates?
- Can delimited blocks (`⟦●operation|param:value⟧`) isolate Vector-Native from English?

**Potential research:**

- Test hybrid prompts with delimited Vector-Native blocks
- Measure token reduction vs pure Vector-Native
- Compare compliance rates

**What's your use case?** Understanding real-world needs helps guide research priorities.

**Reference:** [README.md](../README.md#primary-use-case-ai-to-ai-communication) for use case context.

---

## How do I handle errors or malformed output?

**Research questions:**

- What validation strategies work best?
- How reliable is fallback parsing?
- Can we detect and recover from format errors automatically?

**Example fallback approach:**

```python
def parse_with_fallback(output: str):
    if "●" in output and "|" in output:
        return parse_vector_native(output)  # Vector-Native
    else:
        return parse_natural_language(output)  # Fallback
```

**Validation ideas:**

- Check for `●` symbol, pipe separators, colon pairs
- Retry with different variant if parsing fails
- Log failures to track compliance patterns

**What error patterns have you seen?** Share observations to improve robustness.

**Reference:** [how-it-works.md](./how-it-works.md#step-2-parsing-outputs) for parsing examples.

---

## Is there a parser library?

**Yes.** Use `vector_native.parser` for parsing outputs.

**Basic usage:**

```python
from vector_native.parser import parse_vector_native

output = "●analyze|dataset:Q4|metrics:revenue"
operations = parse_vector_native(output)
```

**For custom parsing:** See [how-it-works.md](./how-it-works.md#step-2-parsing-outputs) for implementation examples.

**Reference:** [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md#for-parsers) for parser guidelines.

---

## How do I measure token reduction in my own system?

### Method 1: Use test suite

```bash
python tests/test_token_reduction.py --variant minimal --scenarios 10
```

### Method 2: Manual measurement

```python
from vector_native.tokenizer import count_tokens

english_tokens = count_tokens("Give attention and add values")
vn_tokens = count_tokens("●⊕")
reduction = (1 - vn_tokens / english_tokens) * 100
```

### Method 3: API comparison

- Generate same task in English vs Vector-Native
- Compare completion token counts from API response
- Calculate percentage reduction

**What reduction rates are you seeing?** Share results to expand the dataset.

**Reference:** [token-savings.md](./token-savings.md) for observed results (88-95% reduction in limited tests).

---

## Can I use this for multi-turn conversations?

**Research questions:**

- How does compliance change across multiple turns?
- Does context accumulation degrade performance?
- What state management patterns work best?

**Example pattern:**

```text
Turn 1: ●task|description:analyze_sales|context:Q4
Turn 2: ●result|status:complete|data:revenue:50000
Turn 3: ●next|action:generate_report|format:pdf
```

**Potential challenges:**

- Context accumulation (each turn adds tokens)
- Compliance drift (later turns may degrade)
- State management (track conversation state in parameters)

**What patterns have you tested?** Multi-turn usage needs more research.

**Reference:** [how-it-works.md](./how-it-works.md#step-3-integration-in-workflows) for A2A examples.

---

## Can I use this with my existing system prompts?

**Research approach:**
1. Identify verbose sections in your prompts
2. Convert to Vector-Native equivalents
3. Test compliance with your model/temperature
4. Measure token reduction
5. Compare results

**Example conversion:**

- English: "You are helpful. Provide details. Focus on needs."
- Vector-Native: `●assistant|mode:helpful|detail:high|attention:needs`

**Open questions:**
- How much can you convert before compliance drops?
- Does hybrid (English + Vector-Native) work better than pure conversion?
- What conversion patterns work best?

**What have you tried?** Migration strategies need real-world testing.

**Reference:** [how-it-works.md](./how-it-works.md#step-1-setup-and-prompting) for integration steps.

---

## What if the model outputs English instead of Vector-Native?

**This indicates low compliance.** See ["What happens if compliance is low?"](#what-happens-if-compliance-is-low) for research directions.

**Questions to investigate:**
- Why does compliance vary?
- Can we predict when English output will occur?
- What recovery strategies work best?

**Potential approaches:**
- Try different variants (strict shows higher compliance in limited tests)
- Experiment with temperature
- Add fallback parsing

**What patterns have you observed?** Understanding failure modes helps improve the system.

---

## How do I contribute a prompt variant?

**Research contribution steps:**

1. Create `prompts/your_variant.txt` with system prompt
2. Test with `python tests/test_token_reduction.py`
3. Document compliance rate, temperature, model, scenarios tested
4. Submit PR with test results and observations

**What to include:**
- Minimum 10 test scenarios
- Compliance rate observed
- Token reduction measured
- Model and temperature used
- Any patterns or anomalies noticed

**Reference:** [CONTRIBUTING.md](../CONTRIBUTING.md) and [prompts/README.md](../prompts/README.md) for guidelines.
