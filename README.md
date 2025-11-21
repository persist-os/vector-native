# Vector-Native

**A protocol for structured AI-to-AI communication that turns instructions into reusable knowledge.**

Vector-Native eliminates ambiguity in machine communication through structured symbols with explicit parameters. By replacing verbose natural language with a standardized format, we enable instructions to become queryable, composable data—not ephemeral text blobs.

**This is for machine-to-machine communication**, not chatbots.

---

## Two Core Problems

**Problem 1: Ambiguity**

When you tell an agent "Please analyze the Q4 sales data and generate a report":
- Which Q4?
- What kind of report?
- What level of detail?

With Vector-Native: `●analyze|dataset:Q4_2024_sales|output:summary_report|detail:executive`

Every parameter is explicit. No room for misinterpretation.

**Problem 2: Instructions Disappear**

Natural language instructions are text blobs:
```
"Launching new B2B SaaS product targeting mid-market companies (100-500 employees). 
Competitive analysis shows crowded space but competitors focus on enterprise..."
```

You can't reuse parts of it, query it, template it, or compose it with other instructions. Once you use it, it's gone.

Vector-Native instructions are structured data:
```
●product_position|category:B2B_SaaS|target:midmarket:100-500_employees
⊕competitive_gap|competitors:enterprise_focus|our_differentiator:48hr_implementation
●campaign_architecture|channel:LinkedIn|theme:speed_to_value
●budget_allocation|total:$50K|period:3_months
●kpis|leads:500|demos:50|customers:10
```

Now you can:
- Reuse `●campaign_architecture` across products
- Query: "show all with `kpis|customers:>5`"
- Template `●budget_allocation` for different scales
- Compose multiple patterns together
- Store as database records
- Build libraries of proven workflows

---

## The Protocol

Vector-Native uses structured symbols that LLMs already understand:

- `●` — Core operation
- `|` — Parameter separator
- `:` — Key-value binding
- `⊕` — Addition/combination
  
The system prompt teaches the model when to use these associations. The result: precise, reusable communication.

**English**

"Please give this maximum attention and add these values" (10 words, ~20 tokens)

**Vector Native**

●⊕ (2 symbols, ~4 tokens)

Technical Concept: Symbols leverage pre-trained associations that already exist in the model:

●: Has learned associations with importance/attention concepts (from training data like Eisenhower Matrix, UI states)
⊕: Has learned associations with addition operations (from mathematical training data)

The system prompt teaches the model to use these associations. The result is higher signal-to-noise ratio—less ambiguity, clearer intent. Token reduction is a side effect of precision.

**This is just one interpretation.** We're collectively exploring what works best across different domains, models, and use cases. Your experiments help define the protocol.

---

## Examples

**Agent Task Delegation**
```
Before: "Can you create a presentation about our Q3 results? Include revenue charts, keep it concise."
After:  ●create|type:presentation|topic:Q3_results|include:revenue_charts|style:concise
```
Reusable component: `style:concise` can be applied to any creation task.

**System Instructions**
```
Before: "You are a helpful assistant. Always provide detailed responses. When analyzing data, be thorough."
After:  ●assistant|mode:helpful|detail:high|reasoning:explicit
```
Store and version this configuration. Reuse across agents.

**Document Updates**
```
Before: "Please update the deadline in the project timeline section from January 15th to January 20th."
After:  ●update|section:timeline|field:deadline|old:Jan_15|new:Jan_20
```
Queryable audit trail. Pattern reusable for any update operation.

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

---

## When to Use It

**✅ Good:**
- System prompts
- Agent-to-agent communication
- Workflows you'll reuse
- Internal APIs and tool calls
- Building knowledge libraries

**❌ Poor:**
- Chatbot conversations
- User-facing messages
- Creative writing

**Rule:** If a human reads it, use natural language. If you want precision and reusability, use Vector-Native.

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

Type any instruction. Watch it become structured, reusable data.

**Note:** This demonstrates one interpretation. The optimal translation depends on your use case. Try it with your own prompts and see what works.

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

## Join the Research

Vector-Native is an experiment, not a finished product. There's no single "correct" way to translate natural language to structured symbols—it depends heavily on your specific use case, the model you're using, and what you're trying to accomplish. This is a collaborative effort to discover what works.

**We need your perspective.** Every domain has unique patterns. Every use case reveals new possibilities. Your experiments, whether they succeed or fail, help us collectively define what this protocol should be.

### Ways to Contribute

**1. Share a translation example**

Take a verbose system prompt or agent instruction from your domain—something you actually use in production or testing. Show us how you'd translate it to Vector-Native. What did you decide to make explicit? What patterns emerged? What was ambiguous?

Open an issue with:
- The original natural language version
- Your VN translation
- Why you made the choices you did
- What you learned

Even if you're not sure it's "correct," share it. There is no correct. We're figuring this out together.

**2. Test it in your domain**

Try using Vector-Native for agent-to-agent communication, system prompts, or internal APIs in your specific use case. Run real experiments. See what breaks. See what works surprisingly well.

Share your results:
- What was your use case?
- What model did you test with?
- What system prompt did you use?
- What worked? What didn't?
- Did you discover reusable patterns?
- Where did the protocol fall short?

Negative results are just as valuable as positive ones. If VN doesn't work for your use case, we want to know why.

**3. Build a variant**

The system prompts we've provided are starting points, not gospel. Create your own interpretation of the Vector-Native protocol. Maybe you use different symbols. Maybe you structure operations differently. Maybe your domain needs specialized operations we haven't thought of.

Build it. Test it. Share:
- Your system prompt
- What makes your variant different
- What problem it solves
- Results from your testing

The best ideas often come from people solving real problems in specific domains.

### How to Contribute

**Simple path:** Open a GitHub issue. Title it with what you're sharing (e.g., "Translation example: Legal contract clauses" or "Testing results: Multi-agent customer service"). Share your experience. That's it.

**Code contributions:** See [`CONTRIBUTING.md`](CONTRIBUTING.md) for technical guidelines on submitting code, tests, or documentation improvements.

**Discussion:** Have questions? Want to discuss an idea before trying it? Open a discussion thread. We're here to explore this together.

### What We're Learning

This is an open research project. We're discovering:
- Which symbols work best for different operations
- How much structure is too much
- Where VN excels and where it fails
- How different models interpret the same symbols
- What makes instructions truly reusable
- How to balance precision with flexibility

Your contributions directly shape these answers. Every example, every test result, every variant teaches us something new about how machines can communicate more effectively.

**There's no formal review process. No credentials required.** Just experiment with Vector-Native in your domain and share what you learn. Whether you're a researcher, engineer, hobbyist, or just curious—if you're exploring structured AI communication, you're contributing to this research.

Let's figure this out together.

---

## Learn More

📖 [Language Spec](docs/language-spec.md) | 🎯 [Use Cases](docs/use-cases.md) | 📈 [Token Savings](docs/token-savings.md) | 🧠 [Why It Works](docs/why-it-works.md) | 💬 [FAQ](docs/faq.md)

---

**Core principle:** Structured symbols eliminate ambiguity and turn instructions into reusable knowledge.

Vector-Native is fully open-source. We're defining this protocol together.
