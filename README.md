# Vector-Native

**A collaborative protocol for defining the optimal, low-token communication language between AI agents.**

Vector-Native is an open-source research initiative focused on drastically reducing Large Language Model (LLM) token usage and improving the precision of AI-to-AI communication. We achieve this by replacing verbose natural language with compact, structured symbols.

---

## The Evidence: Massive Token Reduction

Empirical testing demonstrates that Vector-Native provides substantial savings across diverse scenarios, models, and compliance levels.

**Real results from OpenAI API testing (gpt-4o-mini, 5 scenarios):**

| Variant | Compliance | Avg Token Reduction | Use Case |
|---------|-----------|---------------------|----------|
| **STRICT** | 80% | **88.8%** | Production systems |
| **BALANCED** | 40% | **95.4%** | General use |
| **MINIMAL** | 40% | **95.7%** | Testing/learning |

**Cost impact at scale (1M Output Tokens):**
- English: ~$343
- Vector-Native: **~$22**
- **Savings: 93.6%**

*Based on current gpt-4o-mini pricing.*

---

## Why It Works: Precision for Machines

Vector-Native uses a hybrid syntax that intelligently minimizes the "filler" tokens required by English, achieving maximum precision and efficiency.

**The principle:** We replace long, ambiguous natural language instructions with high-signal, single-token symbols that strongly cue the LLM's internal computational patterns.

| English (Low Signal) | Vector-Native (High Signal) |
| :--- | :--- |
| "Please give this maximum attention and add these values" (10 words, ~20 tokens) | `●⊕` (2 symbols, ~4 tokens) |

**Technical Concept:** The symbols do not bypass the transformer architecture, but they are designed to activate existing learned patterns.
* **`●`:** Strongly cues the model's learned weights to assign maximum **attention** to the subsequent tokens.
* **`⊕`:** Cues a **vector processing pattern** equivalent to a vector addition operation.

This optimization eliminates the need for the LLM to translate verbose human language into an internal, actionable format, resulting in lower costs and greater consistency.

---

## Primary Use Case: AI-to-AI Communication

Vector-Native is optimized for interactions where efficiency and precision are paramount.

-   ✅ **System Prompts:** Optimize token usage where humans do not see the instructions.
-   ✅ **Agent-to-Agent Communication:** Ensure fast, precise, and low-cost interaction between AI services.
-   ✅ **Internal Tooling/APIs:** Standardize and reduce the cost of calls between microservices.
-   ❌ **Direct User-Facing Messages:** Natural language remains necessary for human consumption.

---

## Join the Research: Contribute a Prompt Variant

The key to Vector-Native's success is collaborative, empirical testing. We do not believe a single "master prompt" exists. Optimal performance is highly dependent on the model, task, and desired compliance level.

**Your easiest entry point is creating a System Prompt Variant.**

You can develop a prompt (like our `strict`, `balanced`, or `minimal` examples) that teaches the LLM your own interpretation of the Vector-Native protocol, then test and share your results. This is how we collectively define the most efficient language for machine intelligence.

We welcome contributions across all areas:
* **Prompt Variants:** Define new domain-specific or language-specific prompts.
* **Test Cases:** Expand the scenario suite for more rigorous benchmarking.
* **Core Code:** Improve the parser, tokenizer, and LLM integration utilities.

📖 **Detailed Contribution Guidelines:** See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Get Started

```bash
# Clone and install
git clone [https://github.com/persist-os/vector-native](https://github.com/persist-os/vector-native)
cd vector-native
# ... installation steps ...

# Use a system prompt variant
from vector_native import get_vector_native_system_prompt
prompt = get_vector_native_system_prompt("strict") # or "balanced", "minimal"

# Test your own prompt variant
python tests/test_token_reduction.py

```

## Learn More

📖 Language Spec - Complete protocol specification.

📈 Token Savings - Detailed test results and analysis.

🧠 Why It Works - Full technical explanation of the cueing mechanism.

⚙️ Setup Guide - Detailed installation instructions.

💬 - Common questions and answers.

Vector-Native is a fully open-source research demonstration. We encourage collaboration to define the future of AI communication.