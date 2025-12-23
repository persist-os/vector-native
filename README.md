# Vector Native

**A symbolic structured protocol for AI-to-AI communication that transforms machine-processable information into reusable, queryable knowledge.**

**Core principle:** Structured symbols eliminate ambiguity and turn natural language into reusable knowledge.

Vector-Native (VN) is a pragmatic protocol for A2A communication that leverages high-frequency symbols from LLM training data. By utilizing symbols with consistent semantic associations (bullets, pipes, colons), VN activates existing representations rather than requiring new syntax learning. This approach eliminates ambiguity through structured formats, enabling complex information to become **queryable, composable data**.

**This is for machine-to-machine communication and knowledge modeling**, not chatbots.

-----

## Two Core Problems

### Problem 1: Ambiguity in Communication

When information is conveyed in natural language, whether it's an instruction or a rule, it's open to interpretation:

  * **Instruction:** "Please analyze the Q4 sales data and generate a report." (*Which Q4? What kind of report?*)
  * **Rule:** "Employees must report expenses by the end of the month." (*Which month? What format?*)

With Vector-Native, every parameter is **explicit and unambiguous**:

  * **Instruction:** `●analyze|dataset:Q4_2024_sales|output:summary_report|detail:executive`
  * **Rule:** `●policy|type:remote_work|eligibility:all_employees|approval:manager`

### Problem 2: Information Disappears

Natural language information is trapped in text blobs. Whether it's a project plan, a legal clause, or a strategic goal, you can't easily query it, reuse its parts, template it, or compose it with other information.

```
"Launching new B2B SaaS product targeting mid-market companies (100-500 employees). Competitive analysis shows crowded space..."
```

Vector-Native structures this information as data:

```
●product_position|category:B2B_SaaS|target:midmarket:100-500_employees
⊕competitive_gap|competitors:enterprise_focus|our_differentiator:48hr_implementation
●campaign_architecture|channel:LinkedIn|theme:speed_to_value
```

**Now you can turn this information into a Knowledge Asset:**

  * **Reuse:** Apply `●campaign_architecture` across different products.
  * **Query:** Search a database of structured notes: "show all `●finding` with `confidence:high`."
  * **Compose:** Combine a `●targeting_strategy` from one workflow with a `●budget_allocation` from another.
  * **Audit:** Maintain a queryable audit trail of document changes: `●update|section:timeline|field:deadline|new:Jan_20`

-----

## The Protocol: Design Principles

Vector-Native uses symbols selected from high-frequency patterns in LLM training data:

  * `●` — **Attention/Operation** (Signals instruction start)
  * `|` — **Parameter Delimiter** (Separates parameters)
  * `:` — **Key-Value Binding** (Binds keys to values)
  * `⊕` — **Merge/Addition** (Combination operations)

**Symbol Selection Criteria:**
- High frequency in training data (code, config files, technical documentation)
- Consistent semantic associations across contexts
- Visual distinctiveness for parsing landmarks

The bullet (●) signals instruction start. Pipes (|) delimit parameters. Colons (:) bind keys to values. These symbols leverage associations the model has already learned from exposure to millions of config files, code blocks, and data formats during training. VN utilizes the language of structured data the model already comprehends, activating existing representations rather than requiring new syntax learning.

| Natural Language | Vector Native |
| :--- | :--- |
| Text blob | Structured operations |
| One-time use | **Reusable components** |
| Can't query | **Database-ready** |
| Can't compose | **Mix and match** |
| Lost after use | **Knowledge asset** |

---

## The Protocol

### Four Core Symbols

- `●` — **Core Operation/Entity** (*Do this*, *This is an entity*, *This is a policy*)
- `|` — **Parameter Separator**
- `:` — **Key-value Binding**
- `⊕` — **Addition/Combination**

### Additional Symbols

- `→` — Sequential flow
- `○` — Background/secondary  
- `≠` — Block/reject

### How It Works

**Mechanism:**

Research on feature activation in large language models demonstrates that models develop distinct internal representations for different interaction formats. Features that activate for structured dialogue formats (such as "Human:/Assistant:" pairs used in finetuning) relate to dialogue mechanics, chatbot behavior, and assistant personas. When these features are suppressed, models shift from assistant-like responses toward more direct, human-like communication patterns.

VN's design leverages this phenomenon: by triggering training data associated with structured formats (configuration files, API calls, system logs), the protocol bypasses conversational overhead and activates task-oriented representations. The syntax requirement establishes this operational context immediately.

**Example:**

English: "Please give this maximum attention and add these values" (10 words, ~20 tokens)

Vector Native: `●⊕` (2 symbols, ~4 tokens)

The symbols leverage pre-trained associations:
- `●`: Importance/attention concepts (Eisenhower Matrix, UI states)
- `⊕`: Addition operations (mathematical training data)

The objective is precision and structure to eliminate the ambiguity of natural language. Token reduction is a side effect of this precision.

**This is a base protocol.** VN should be adapted to each use case. Most applications may require hybrid VN to preserve semantic meaning of certain phrases, while others may require minimal structural markup. This flexibility is essential for adaptability to the LLM's processing characteristics.

---

## Examples

### Basic Structure

```
●operation|param1:value1|param2:value2
```

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

### Practical Applications

**Agent Task Delegation**
```
Before: "Can you create a presentation about our Q3 results? Include revenue charts, keep it concise."
After:  ●create|type:presentation|topic:Q3_results|include:revenue_charts|style:concise
```

### System Instructions
```
Before: "You are a helpful assistant. Always provide detailed responses. When analyzing data, be thorough."
After:  ●assistant|mode:helpful|detail:high|reasoning:explicit
```

### Document Updates
```
Before: "Please update the deadline in the project timeline section from January 15th to January 20th."
After:  ●update|section:timeline|field:deadline|old:Jan_15|new:Jan_20
```

**Have a different approach?** We want to see it. Share your translation patterns and help us understand what works in your domain.

---

## What This Enables

**Workflow Libraries:** Store proven `●campaign_architecture` patterns. Reuse `●targeting_strategy` templates across campaigns.

**Intelligent Composition:** Combine components from different workflows. "This `●competitive_gap` pattern worked for SaaS—try it for fintech."

**Data-Driven Queries:** "Show all campaigns where `kpis|CAC_target:<$6000`" or "What `●budget_allocation` patterns led to best results?"

**Team Collaboration:** Marketing shares `●campaign_architecture` operations. Sales reuses `●targeting_strategy` for outreach.

**Surgical Modifications:** Template says `●budget_allocation|total:$50K`. Change to `total:$100K`. Everything else stays intact.

| Natural Language | Vector-Native |
|-----------------|---------------|
| Text blob | Structured operations |
| One-time use | Reusable components |
| Can't query | Database-ready |
| Can't compose | Mix and match |
| Lost after use | **Knowledge asset** |

**Testing in a different context?** Share what you learn. Your use case might reveal patterns we haven't considered.

---

## Applications

- **Multi-agent systems:** Precise coordination with reusable patterns
- **Knowledge management:** Queryable research notes and workflows
- **Business operations:** Template-driven project management
- **Domain-specific:** Machine-readable legal contracts, medical records
- **System integration:** Composable workflow definitions

📖 **Full catalog:** [`docs/use-cases.md`](docs/use-cases.md)

---

## Try It Now

**Live translator:** [Vector-Native Gem](https://gemini.google.com/gem/1gGEZtVRWGkXUGRCSQiRscVcxjnDTfdRI?usp=sharing)

Say anything in natural language. Watch it become structured, reusable data.

**Note:** The optimal translation depends on your use case. Experiment with your own prompts.

📖 **Implementation guides:** [`docs/quickstart.md`](docs/quickstart.md)

---

## Early Results

Testing on gpt-4o-mini (5 scenarios):

| Variant | Compliance | Token Reduction |
|---------|-----------|-----------------|
| STRICT | 80% | 88.8% |
| BALANCED | 40% | 95.4% |
| MINIMAL | 40% | 95.7% |

Reduction varies (10-95%) by task type. Primary value: **precision and reusability**.

**These are early results from limited testing.** We need more data across different models, domains, and use cases. Your testing helps us understand what's possible.

---

## What VN Is Not

VN differs from formal agent communication languages (KQML, FIPA-ACL) in that it lacks explicit semantics, speech act theory, or ontological commitments. Those languages define what messages mean; VN only defines how messages are structured.

VN differs from structured generation approaches (JSON-mode, function calling, grammar-constrained decoding) in that it targets input representation, not output formatting. The protocol does not constrain what the model produces; rather, it modifies how instructions are communicated to the model.

VN is best understood as a dialect optimized for LLM comprehension: a pragmatic protocol rather than a formal specification language. VN has no formal semantics. There is no compiler, no type system, no verification. It is designed for LLM comprehension, not machine parsing. This represents a deliberate design choice that allows flexibility while maintaining structure.

---

## Join the Research

Vector-Native is an experiment, not a finished product. There's no single "correct" way to translate natural language to structured symbols. It depends heavily on your specific use case, the model you're using, and what you're trying to accomplish. This is a collaborative effort to discover what works.

**We need your perspective.** Every domain has unique patterns. Your experiments help define what this protocol should be.

### Ways to Contribute

**1. Share Translation Examples**
- Take a verbose prompt from your domain
- Show your VN translation
- Explain your choices
- Share what you learned

**2. Test in Your Domain**
- Try VN for your specific use case
- Run experiments with different models
- Share results (positive or negative)
- Document what worked and what didn't

**3. Build Variants**
- Create your own interpretation
- Use different symbols or structures
- Test with your team/system
- Share your approach

### How to Contribute

**Simple:** Open a GitHub issue with your examples, results, or ideas.

**Code:** See [`CONTRIBUTING.md`](CONTRIBUTING.md) for technical guidelines.

**Discussion:** Questions? Open a discussion thread.

---

## What We're Learning

This is open research. We're discovering:
- Which symbols work best for different operations
- How much structure is optimal
- Where VN excels and where it falls short
- How different models interpret symbols
- What makes information truly reusable
- Domain-specific patterns and variations

**Your contributions directly shape these answers.**

---

## Frequently Asked Questions

### Is this just abbreviations?
No. VN leverages pre-trained symbol associations in LLMs. Symbols trigger statistical patterns from training data (math, programming, config files), not just shorter text.

### Why not just use JSON?
JSON is verbose and LLMs aren't trained to "think" in JSON. VN uses symbols with strong semantic associations, achieving both precision and token efficiency.

### Does this work with all LLMs?
Testing shows it works well with GPT-4, Claude, Gemini. Smaller models may need more explicit system prompts. Your testing helps us understand compatibility.

### When should I NOT use VN?
Casual conversations, creative writing, user-facing content, emotional support. VN is for precision and reusability, not warmth.

### Can I modify the symbols?
Yes! Build your own variant if your domain needs different symbols. Share your approach so others can learn.

📖 **More questions:** [`docs/faq.md`](docs/faq.md)

---

## Learn More

📖 [Language Spec](LANGUAGE_SPEC.md) — Complete symbol definitions  
🎯 [Use Cases](docs/use-cases.md) — Domain-specific applications  
📈 [Token Savings](docs/token-savings.md) — When efficiency matters  
🧠 [Why It Works](docs/why-it-works.md) — Training data mechanics  
💬 [FAQ](docs/faq.md) — Common questions  
🚀 [Quickstart](docs/quickstart.md) — Get started fast

---

## Community

- **GitHub Issues:** Bug reports, feature requests, examples
- **Discussions:** Ideas, questions, research
- **Discord:** [Coming soon]

---

## License

MIT License - see [`LICENSE`](LICENSE)

---

Vector Native is fully open source. We're defining this protocol together.

**Maintained by PersistOS**

