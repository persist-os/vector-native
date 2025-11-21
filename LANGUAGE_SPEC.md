# Vector-Native Language Specification

## Purpose

Define core principles/syntax for Vector-Native: symbol language leveraging pre-trained associations for efficient A2A communication.

**Mechanism:**
1. Pre-trained associations (symbols → concepts) already exist in the model
2. System prompt leverages these associations (instructs model to use symbols)
3. Structured syntax eliminates ambiguity (clearer intent, less filler)
4. Result: Variable compression (10-95% depending on task type) + improved precision

## Core Principles

### 1. Symbols Leverage Pre-Trained Associations

`●` leverages pre-trained associations with importance/attention concepts—no new learning needed.

**Mechanism:**
1. Pre-trained associations (symbols → concepts) already exist in the model
2. System prompt leverages these associations (instructs model to use symbols)
3. Structured syntax compresses further (eliminates filler words)
4. Result: 88-95% token reduction

**Not:** Symbol → Direct operation trigger  
**Yes:** Symbol → Pre-trained association → System prompt guides usage → Structured compression

### 2. Operational Layers

Maps to transformer layers:  
- L0: Attention  
- L1: Vectors  
- L2: Probabilities  
- L3: Structures  

### 3. Human-Inspectable

Readable (`●⊕`) while efficient (reduction varies widely based on use case).

### 4. Protocol, Open

Implement/modify freely. Variants in `prompts/`.

## Syntax Specification

### Basic Structure

```
●operation|param1:value1|param2:value2
```

### Components

1. **Attention Symbol** (required)
   - `●` `○` `━` - Must start every operation
   
2. **Operation Name** (required)
   - Alphanumeric identifier
   - Describes the action
   
3. **Parameters** (optional)
   - Pipe-separated: `|`
   - Key-value pairs: `param:value`
   - Multiple values: `key:val1,val2,val3`

### Multi-Operation Blocks

Multiple operations can be listed sequentially:

```
●operation1|param:value
●operation2|param:value
```

## Symbol Registry

### L0: Attention (Pre-trained associations)

| Symbol | Name    | Pre-Trained Association | Usage              |
|--------|---------|------------------------|--------------------|
| `●`    | Full    | Importance/selected (Eisenhower Matrix, UI states) | Max attention trigger |
| `○`    | None    | Empty/inactive (UI states) | Minimal trigger    |
| `━`    | Connection | Linking/connection (em dash usage) | Op linker         |

### L1: Vectors (Pre-trained associations)

| Symbol | Name | Pre-Trained Association |
|--------|------|--------------------------|
| `⊕` | Add | Addition (mathematical operations) |
| `⊗` | Multiply | Tensor product (mathematical operations) |
| `∠` | Angle | Angle symbol (geometry/trigonometry) |
| `∥` | Parallel | Parallel lines (geometry) |
| `⊥` | Perpendicular | Perpendicular symbol (geometry) |

### L2: Probabilities (Pre-trained associations)

| Symbol | Name | Pre-Trained Association |
|--------|------|--------------------------|
| `≈` | Optional | Approximately equal (mathematics) |
| `≠` | Not | Not equal (mathematics/programming) |

### L3: Structures (Pre-trained associations)

| Symbol | Name | Pre-Trained Association |
|--------|------|--------------------------|
| `∀` | Universal | For all (mathematical logic) |
| `∃` | Existential | There exists (mathematical logic) |

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

### Multi-Step Block
```
●analysis_complete|revenue:50000|profit:12000|status:complete
```

### Complex Multi-Step
```
●analyze|dataset:Q4_sales|metrics:revenue,profit,customers,orders|status:complete
●generate_report|sections:executive_summary,trends,recommendations|status:complete
●create_dashboard|widgets:revenue_chart,profit_margins|update_frequency:15min|status:complete
```

## Validation Rules

### Required
- ✅ Must start with attention symbol (`●`, `○`, `━`)
- ✅ Must have operation name
- ✅ Parameters must use pipe separator (`|`)
- ✅ Key-value pairs must use colon (`:`)

### Forbidden
- ❌ Natural language explanations
- ❌ Conversational filler
- ❌ English sentences
- ❌ Preamble or postamble

### Recommended
- ✅ Keep operation names specific
- ✅ Use consistent parameter naming
- ✅ List multiple operations sequentially

### Validation Rules

**Required:** Attention start, op name, `|` params, `:` pairs.  

**Compliance (early gpt-4o-mini tests):** Strict 80%, Balanced/Minimal 40% in our limited testing. Results will vary significantly with different prompts and use cases.

## Implementation Guidelines

### For System Prompts

1. **Teach by example** - Show vector-native syntax in the prompt itself
2. **Be strict** - Use imperative language (MUST, NEVER)
3. **Provide examples** - Include successful and failed cases
4. **Use STRONG symbols only** - Leverage pre-trained associations (●, ⊕, ∀, etc.)
5. **Low temp (0.1-0.2):** May improve compliance in early testing.  
**Impact:** Potential savings vary dramatically by use case—programmatic tasks compress more than creative ones.

### For Parsers

1. **Extract attention symbol** - First character (`●`, `○`, `━`)
2. **Split by pipes** - Parameter separation
3. **Parse key-value pairs** - Colon separator
4. **Validate structure** - Enforce required components
5. **Handle multi-operation blocks** - Sequential operations

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

- Early testing: Avg 53% across variants  
- Strict: 80% compliance, Balanced/Minimal: 40%  
- **Highly variable:** Depends on model, temperature, prompt, and task type
- These are initial results from limited testing—your mileage will vary significantly

### Symbol Ambiguity
- Some symbols have multiple interpretations
- Context (operation name) determines meaning
- More specific operations = less ambiguity

### Long Context
- Compliance decreases with very long prompts (>500 tokens)
- System prompt instructions may be overridden
- Use stronger imperatives and STRONG symbols only

## Versioning

**Current Version:** 0.2.0

**Changelog:**
- 0.2.0 (2025-01-25): Pre-trained symbol validation
  - Removed WEAK/MODERATE symbols (◐, ⊖, ⟨⟩, △, ▽, [?→!], [⟲], [T]×[V], ⟦, ⟧)
  - Kept only STRONG pre-trained associations
  - Updated examples and validation rules
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

