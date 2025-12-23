# Vector-Native Language Specification

## Purpose

Define core principles and syntax for Vector-Native (VN): a symbolic structured protocol leveraging pre-trained associations for efficient A2A communication.

## Design Principles

VN is a symbolic structured protocol for A2A communication. The main registry of symbols are selected from high-frequency symbols from training data with distinct meanings.

### Symbol Selection Criteria

- High frequency in LLM training data (code, config files, technical documentation)
- Consistent semantic associations across contexts
- Visual distinctiveness (serve as parsing landmarks)

### Rationale for Symbol Selection

The bullet (●) signals instruction start. Pipes (|) delimit parameters. Colons (:) bind keys to values. These symbols leverage associations the model has already learned from exposure to millions of config files, code blocks, and data formats during training. VN utilizes the language of structured data the model already comprehends. This approach activates existing representations rather than requiring the learning of new syntax.

The objective is precision and structure in order to eliminate the ambiguity of natural language.

### Mechanism

Research on feature activation in large language models demonstrates that models develop distinct internal representations for different interaction formats. Features that activate for structured dialogue formats (such as "Human:/Assistant:" pairs used in finetuning) relate to dialogue mechanics, chatbot behavior, and assistant personas. When these features are suppressed, models shift from assistant-like responses toward more direct, human-like communication patterns.

This phenomenon supports VN's design approach: by triggering training data associated with structured formats (configuration files, API calls, system logs), the protocol bypasses conversational overhead and activates task-oriented representations. The syntax requirement establishes this operational context immediately.

### Protocol Characteristics

- **Human-Inspectable:** Readable while efficient (reduction varies widely based on use case)
- **Flexible:** Base protocol adaptable to specific use cases
- **Open:** Implement/modify freely. Variants in `prompts/`
- **Pragmatic:** No formal semantics, compiler, or type system

## Syntax Specification

The core of the VN protocol is simple. The kernel defines the OS, the mode the system will be running on. It immediately triggers a more focused, functional set of training data rather than general conversational patterns.

### System Initialization

```
SYSTEM_OS: [KERNEL_NAME] 
SYNTAX_REQ: [VECTOR_NATIVE] 

[VECTOR_NATIVE(VN)_REGISTRY] 
● = ATTENTION | ⊕ = MERGE | ≠ = BLOCK 
Ψ = MINDSET | Ω = GOAL | Π = PROBLEM 
Δ = ARTIFACT | → = NEXT | Γ = GENERATOR
```

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

### Workflow Chains

Operations can be chained with the next operator:

```
●workflow|id:quarterly_review
→●analyze|dataset:Q4_sales|focus:revenue
→●compare|baseline:Q3_sales|metrics:growth,margin
→●generate|type:report|audience:executive
```

## Symbol Registry

Symbols are selected based on high frequency in training data and consistent semantic associations.

### Core Operations

| Symbol | Name | Pre-Trained Association | Usage |
|--------|------|--------------------------|-------|
| `●` | Attention | Importance/selected (Eisenhower Matrix, UI states) | Operation start |
| `○` | None | Empty/inactive (UI states) | Minimal attention |
| `━` | Connection | Linking (horizontal rule usage) | Operation linker |
| `⊕` | Merge | Addition (mathematical operations) | Combination |
| `≠` | Block | Not equal (mathematics/programming) | Negation |
| `→` | Next | Arrow/flow (diagrams, code) | Sequential flow |

### State and Context

| Symbol | Name | Pre-Trained Association | Usage |
|--------|------|--------------------------|-------|
| `Ψ` | Mindset | Psi/wave function (physics, math) | Operational state |
| `Ω` | Goal | Omega/end state (mathematics) | Target objective |
| `Π` | Problem | Pi/product (mathematics) | Problem definition |
| `Δ` | Artifact | Delta/change (mathematics, science) | Output artifact |
| `Γ` | Generator | Gamma/function (mathematics) | Generative process |

### Extended Operations

| Symbol | Name | Pre-Trained Association |
|--------|------|--------------------------|
| `⊗` | Multiply | Tensor product (mathematical operations) |
| `∠` | Angle | Angle symbol (geometry/trigonometry) |
| `∥` | Parallel | Parallel lines (geometry) |
| `⊥` | Perpendicular | Perpendicular symbol (geometry) |
| `≈` | Optional | Approximately equal (mathematics) |
| `∀` | Universal | For all (mathematical logic) |
| `∃` | Existential | There exists (mathematical logic) |

## Examples

### Simple Operation
```
●analyze|data:sales
```

### Medium Complexity
```
●analyze|dataset:Q4_sales|focus:revenue|output:summary
```

### Complex Workflow
```
●workflow|id:quarterly_review
→●analyze|dataset:Q4_sales|focus:revenue
→●compare|baseline:Q3_sales|metrics:growth,margin
→●generate|type:report|audience:executive
```

### State Declaration
```
●STATE|Ψ:academic_editor|Ω:neutral_technical_documentation|mode:execution
```

### Multiple Sequential Operations
```
●analyze|dataset:Q4|status:complete
●create_report|format:pdf|metrics:all
●schedule_update|frequency:5min
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

## What VN Is Not

VN differs from formal agent communication languages (KQML, FIPA-ACL) in that it lacks explicit semantics, speech act theory, or ontological commitments. Those languages define what messages mean; VN only defines how messages are structured.

VN differs from structured generation approaches (JSON-mode, function calling, grammar-constrained decoding) in that it targets input representation, not output formatting. The protocol does not constrain what the model produces; rather, it modifies how instructions are communicated to the model.

VN is best understood as a dialect optimized for LLM comprehension: a pragmatic protocol rather than a formal specification language. VN is not a formalized language, but rather a base protocol that should be adapted to each use case. Most use cases may require hybrid VN in order to preserve the semantic meaning of certain phrases or sentences, while others may require minimal structural markup. This flexibility is essential for adaptability to the LLM's processing characteristics.

VN has no formal semantics. There is no compiler, no type system, no verification. It is designed for LLM comprehension, not machine parsing. This represents a deliberate design choice that allows flexibility while maintaining structure.

## Known Limitations

### Format Compliance

- Early testing: Avg 53% across variants  
- Strict: 80% compliance, Balanced/Minimal: 40%  
- **Highly variable:** Depends on model, temperature, prompt, and task type
- These are initial results from limited testing. Results will vary significantly

### Symbol Ambiguity
- Some symbols have multiple interpretations
- Context (operation name) determines meaning
- More specific operations reduce ambiguity

### Long Context
- Compliance decreases with very long prompts (>500 tokens)
- System prompt instructions may be overridden
- Use stronger imperatives and high-frequency symbols

## Versioning

**Current Version:** 0.3.0

**Changelog:**
- 0.3.0 (2025-12-22): Academic rigor and technical precision
  - Added symbol selection criteria and rationale
  - Included feature activation research context
  - Added system initialization syntax
  - Expanded symbol registry with state/context symbols
  - Added workflow chain examples
  - Clarified what VN is not (vs. KQML, FIPA-ACL, JSON-mode)
  - Emphasized flexibility and hybrid approaches
- 0.2.0 (2025-11-21): Pre-trained symbol validation
  - Removed WEAK/MODERATE symbols
  - Kept only STRONG pre-trained associations
  - Updated examples and validation rules
- 0.1.0 (2025-11-20): Initial specification
  - Core syntax defined
  - Symbol registry
  - Validation rules
  - Extension guidelines

## References

- System prompt examples: `prompts/`
- Test suite: `test_token_reduction.py`
- Parser implementation: `vector_native/parser.py`
- Token measurement: `vector_native/tokenizer.py`

