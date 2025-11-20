# Vector-Native Language Specification

## Purpose

Define the core principles and syntax of vector-native, a symbol-based language that maps to LLM computational patterns.

## Core Principles

### 1. Symbols Trigger Patterns

Symbols like `●` create distinct attention patterns in transformer models. They don't "represent" attention—they trigger it.

**Not:** Symbol → Translation → Operation  
**Instead:** Symbol → Pattern Activation

### 2. Operational Layers

Vector-native maps to the computational layers of transformer models:

- **L0 (Attention):** Which tokens matter
- **L1 (Vectors):** Mathematical operations on embeddings
- **L2 (Probabilities):** Next token prediction
- **L3 (Structures):** Control flow patterns

### 3. Human-Inspectable

Unlike raw embeddings, vector-native symbols are readable and debuggable by humans while remaining efficient for machines.

### 4. Protocol, Not Package

This is a communication protocol. Anyone can implement it, modify it, or create variants.

## Syntax Specification

### Basic Structure

```
●operation|param1:value1|param2:value2
```

### Components

1. **Attention Symbol** (required)
   - `●` `◐` `○` - Must start every operation
   
2. **Operation Name** (required)
   - Alphanumeric identifier
   - Describes the action
   
3. **Parameters** (optional)
   - Pipe-separated: `|`
   - Key-value pairs: `param:value`
   - Multiple values: `key:val1,val2,val3`

### Delimiters (Optional but Recommended)

Wrap output in delimiters for complex responses:

```
⟦
●operation1|param:value
●operation2|param:value
⟧
```

## Symbol Registry

### L0: Attention (Which tokens matter)

| Symbol | Name | Weight | Usage |
|--------|------|--------|-------|
| `●` | Full | 1.0 | Maximum attention |
| `◐` | Partial | 0.5 | Moderate attention |
| `○` | None | 0.0 | Minimal attention |
| `━` | Connection | - | Link marker |

### L1: Vectors (Operations on embeddings)

| Symbol | Name | Operation |
|--------|------|-----------|
| `⊕` | Add | Vector addition |
| `⊗` | Multiply | Matrix multiplication |
| `⊖` | Subtract | Vector subtraction |
| `∠` | Angle | Cosine similarity |
| `∥` | Parallel | Parallel check |
| `⊥` | Perpendicular | Orthogonal check |

### L2: Probabilities (Prediction patterns)

| Symbol | Name | Effect |
|--------|------|--------|
| `⟨⟩` | Distribution | Probability distribution |
| `△` | Increase | Boost probability |
| `▽` | Decrease | Reduce probability |
| `≈` | Optional | Approximate/optional |
| `≠` | Not | Negation/different |

### L3: Structures (Control flow)

| Symbol | Name | Pattern |
|--------|------|---------|
| `[?→!]` | Conditional | If-then |
| `[∀→]` | Universal | For all |
| `[∃→]` | Existential | There exists |
| `[⟲]` | Recursive | Recursive pattern |
| `[T]×[V]` | Transform | Transformation |
| `⟦` | Block Start | Output delimiter |
| `⟧` | Block End | Output delimiter |

## Examples

### Simple Operation
```
●analyze|dataset:sales|metrics:revenue,profit
```

### Multiple Operations
```
●analyze|dataset:Q4|status:complete
●create_report|format:pdf|metrics:all
●schedule_update|frequency:5min
```

### Delimited Block
```
⟦
●analysis_complete|revenue:50000|profit:12000|status:complete
⟧
```

### Complex Multi-Step
```
⟦
●analyze|dataset:Q4_sales|metrics:revenue,profit,customers,orders|status:complete
●generate_report|sections:executive_summary,trends,recommendations|status:complete
●create_dashboard|widgets:revenue_chart,profit_margins|update_frequency:15min|status:complete
⟧
```

## Validation Rules

### Required
- ✅ Must start with attention symbol (`●`, `◐`, `○`)
- ✅ Must have operation name
- ✅ Parameters must use pipe separator (`|`)
- ✅ Key-value pairs must use colon (`:`)

### Forbidden
- ❌ Natural language explanations
- ❌ Conversational filler
- ❌ English sentences
- ❌ Preamble or postamble

### Recommended
- ✅ Use delimiters (`⟦...⟧`) for complex output
- ✅ Keep operation names specific
- ✅ Use consistent parameter naming

## Implementation Guidelines

### For System Prompts

1. **Teach by example** - Show vector-native syntax in the prompt itself
2. **Be strict** - Use imperative language (MUST, NEVER)
3. **Provide examples** - Include successful and failed cases
4. **Use delimiters** - Enforce output boundaries
5. **Minimize temperature** - Use 0.1-0.2 for deterministic output

### For Parsers

1. **Extract attention symbol** - First character
2. **Split by pipes** - Parameter separation
3. **Parse key-value pairs** - Colon separator
4. **Handle delimiters** - Strip `⟦` and `⟧`
5. **Validate structure** - Enforce required components

### For Users

1. **Start simple** - Test with short operations first
2. **Validate output** - Check format compliance
3. **Iterate prompt** - Refine based on failure cases
4. **Share learnings** - Contribute successful prompts
5. **Measure reduction** - Track token savings

## Extension Guidelines

### Adding New Symbols

1. Choose symbol that doesn't conflict with existing
2. Document in appropriate layer (L0-L3)
3. Provide examples of usage
4. Test with multiple models

### Creating Variants

1. Maintain core syntax (attention + operation + params)
2. Document differences from base spec
3. Provide example system prompt
4. Share results and compliance rates

### Contributing

1. Test your prompt variant (minimum 10 scenarios)
2. Document compliance rate
3. Share prompt + test results
4. Add to `prompts/` directory

## Known Limitations

### Format Compliance
- Current: 53.3% average across all variants (strict: 80%, balanced: 40%, minimal: 40%)
- Target: 95%+ for production use
- Varies by model, temperature, and prompt length
- Strict variant achieves highest compliance (80%) but has larger system prompt overhead

### Symbol Ambiguity
- Some symbols have multiple interpretations
- Context (operation name) determines meaning
- More specific operations = less ambiguity

### Long Context
- Compliance decreases with very long prompts (>500 tokens)
- System prompt instructions may be overridden
- Use stronger delimiters and imperatives

## Versioning

**Current Version:** 0.1.0

**Changelog:**
- 0.1.0 (2025-01-20): Initial specification
  - Core syntax defined
  - Symbol registry (L0-L3)
  - Validation rules
  - Extension guidelines

## References

- System prompt examples: `prompts/`
- Test suite: `test_token_reduction.py`
- Parser implementation: `vector_native/parser.py`
- Token measurement: `vector_native/tokenizer.py`

