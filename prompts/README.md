# Vector-Native System Prompts

This directory contains example system prompts for vector-native. Each variant has different strictness levels and compliance characteristics.

## Available Prompts

### 1. `strict.txt` (Recommended for Production)

**Characteristics:**
- Imperative language (MUST, NEVER)
- Strict attention symbols (operations must start with `●`, `○`, or `━`)
- No acknowledgements or preamble allowed
- Multiple examples (short, medium, long)

**Best for:**
- Agent-to-agent communication
- Production systems requiring high reliability
- Cost-critical applications

**Compliance target:** 80% (4/5 tests successful) with temperature 0.1-0.2

**Usage:**
```python
from pathlib import Path

prompt = Path("prompts/strict.txt").read_text()
# Use with LLM API
```

---

### 2. `balanced.txt` (Good Default)

**Characteristics:**
- Moderate enforcement (preferred vs required)
- Recommended delimiters
- Flexible compliance
- Shorter than strict variant

**Best for:**
- General use cases
- Experimentation
- Less critical applications

**Compliance target:** 40% (2/5 tests successful) with temperature 0.3-0.5

**Usage:**
```python
from pathlib import Path

prompt = Path("prompts/balanced.txt").read_text()
# Use with LLM API
```

---

### 3. `minimal.txt` (Experimental)

**Characteristics:**
- Minimal instructions
- Compact (4 lines)
- Basic symbol definitions
- Simple examples

**Best for:**
- Testing
- Understanding core concepts
- Custom extensions

**Compliance target:** 40% (2/5 tests successful) - not recommended for production

**Usage:**
```python
from pathlib import Path

prompt = Path("prompts/minimal.txt").read_text()
# Use with LLM API
```

---

## Testing Your Prompt

Use the test suite to measure compliance:

```bash
# Modify test_token_reduction.py to load your prompt
python test_token_reduction.py
```

**Key metrics:**
- Format compliance rate (target: >75%)
- Token reduction percentage
- Success across different prompt lengths

## Contributing Your Own

### Guidelines

1. **Test thoroughly** - Minimum 10 diverse scenarios
2. **Document compliance** - Report success rate
3. **Name descriptively** - e.g., `strict.txt`, `balanced.txt`, `creative.txt`
4. **Include metadata** - Add comment header with:
   - Purpose
   - Target compliance rate
   - Recommended temperature
   - Best use cases

### Metadata Format

Add this header to your prompt file:

```
# Vector-Native System Prompt: [NAME]
# Purpose: [DESCRIPTION]
# Target Compliance: [X%]
# Recommended Temperature: [0.X]
# Best For: [USE CASES]
# Tested With: [MODEL NAMES]
```

### Submission

1. Add your prompt to `prompts/your_name.txt`
2. Test with at least 10 scenarios
3. Document results in comment header
4. Submit PR with test results

## Temperature Recommendations

| Prompt Type | Temperature | Use Case |
|-------------|-------------|----------|
| Strict | 0.1 - 0.2 | Production, high reliability |
| Balanced | 0.3 - 0.5 | General use, experimentation |
| Minimal | 0.5 - 0.7 | Testing, creative applications |

**Lower temperature = Higher format compliance**

## Model Compatibility

Tested with:
- ✅ OpenAI (gpt-4o-mini, gpt-4)
- ⏳ Anthropic (Claude) - pending tests
- ⏳ Google (Gemini) - pending tests
- ⏳ Meta (Llama) - pending tests

Different models may require prompt adjustments. Contribute your findings!

## Performance Tips

### Improve Compliance

1. **Use strict prompt** - More imperatives = higher compliance
2. **Lower temperature** - Reduce randomness
3. **Add few-shot examples** - Include successful long-form examples
4. **Strengthen delimiters** - Make output boundaries explicit
5. **Test iteratively** - Refine based on failure cases

### Optimize for Speed

1. **Use minimal prompt** - Shorter system prompt = faster
2. **Increase temperature** - Faster sampling (trade-off: lower compliance)
3. **Limit examples** - Fewer examples = shorter prompt

### Balance Both

1. **Use balanced prompt** - Middle ground
2. **Temperature 0.3-0.5** - Reasonable compliance + speed
3. **Test with your use case** - Measure what matters

## Common Issues

### Low Compliance (<60%)

**Try:**
- Switch to `strict.txt`
- Lower temperature to 0.1
- Add more explicit delimiters
- Include long-form examples in prompt

### Slow Responses

**Try:**
- Switch to `minimal.txt`
- Increase temperature to 0.5
- Remove examples from prompt
- Reduce symbol explanations

### Symbol Confusion

**Try:**
- Use more specific operation names
- Avoid ambiguous symbols
- Add context in parameters
- Document symbol meanings in prompt

## Future Variants

Ideas for community contributions:

- **Domain-specific** - Optimized for finance, healthcare, etc.
- **Creative** - Allow more flexibility for generative tasks
- **Multilingual** - Support non-English text in parameters
- **Compact** - Optimize for shortest possible prompt
- **Verbose** - Extensive examples and explanations

## Resources

- Language spec: `../LANGUAGE_SPEC.md`
- Test suite: `../test_token_reduction.py`
- Parser: `../vector_native/parser.py`
- Main docs: `../README.md`

