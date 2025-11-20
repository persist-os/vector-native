# Examples

## Basic Syntax

```text
●operation|param1:value1|param2:value2
```

**Rules:**

1. Start with attention symbol (`●`, `◐`, `○`) – triggers focus directly
2. Operation name follows – specifies action
3. Parameters separated by `|` – combines properties
4. Key-value pairs use `:` – assigns values

**Token Savings Example:**  
English: "Focus on analyzing the dataset with revenue and profit metrics in JSON output" (~12 tokens)  
Vector-Native: `●analyze|dataset:Q4_sales|metrics:revenue,profit|output:json` (~6 tokens)  
**Savings: 50%**

## Simple Examples

**Analysis:**

```text
●analyze|dataset:Q4_sales|metrics:revenue,profit|output:json
```

**Task Creation (Agent-to-Agent):**

```text
●create_widget|userId:123|type:chart|priority:high
```

**Multi-Operation (Internal Tool Chain):**

```text
●analyze|dataset:sales|status:complete
●create_report|format:pdf|metrics:all
```

## Use Cases

### 1. Agent-to-Agent Communication

**Problem:** Agents waste tokens on verbose English handoffs.  
**Solution:** Direct operational cues reduce latency/cost.

```python
# Agent A → Agent B (A2A)
task = "●process|data:Q4|metrics:revenue,profit"
result = agent_b.execute(task)  # Triggers processing directly
```

**Benefit:** 88-95% completion token reduction (per README tests). Structured for instant parsing. Ideal for multi-agent systems.

### 2. System Prompts

**All system prompts should use Vector-Native.** Users never see them—every English token is waste.

**Before (English, ~20 tokens):**

```text
You are a helpful assistant. Always provide detailed responses.
Pay attention to the user's needs and format your output clearly.
```

**After (Vector-Native, ~8 tokens):**

```text
●assistant|mode:helpful|detail:high|attention:user_needs|format:clear
```

**Savings:** 60% per request. Scales to 93.6% at 1M tokens ($343 → $22).

### 3. Internal Tool Communication

**Non-human paths should use Vector-Native:**

- API requests between services (`●fetch|endpoint:/data|auth:token`)
- Database queries (`●query|table:users|filter:role:admin`)
- Log aggregation (`●log|level:error|message:timeout`)
- Internal messaging (`●notify|target:orchestrator|status:complete`)

**Example (Tool Call):**

```text
●api_call|method:POST|path:/process|body:{data:Q4}|headers:{auth:Bearer}
```
Triggers HTTP operation directly, no English parsing.

## Advanced Examples

**Conditional Processing:**

```text
[?→!]input_valid:●process|data:input|output:result|[∃→]error:●log|level:error
```

**Recursive Analysis:**

```text
●analyze⟲|dataset:sales|depth:3|stop_condition:convergence
```

**Probability-Weighted Output:**

```text
●generate|options:⟨summary,detail,brief⟩|weights:△,▽,≈
```

**Token Savings:** Complex English (~50 tokens) → Vector-Native (~15 tokens), 70% reduction.

## Reasoning Techniques

Vector-Native enables efficient implementation of advanced reasoning techniques by structuring prompts with symbols for step-by-step logic, branching, evaluation, and collaboration.

**Chain of Thought (CoT):**
Break down reasoning into sequential steps for better accuracy.

```text
●reason|step1:analyze_problem|step2:identify_assumptions|step3:evaluate_options|step4:conclude|output:⟦reasoning⟧
```

**English Equivalent (~25 tokens):** "Think step by step: first analyze the problem, then identify assumptions, evaluate options, and conclude. Output your reasoning."
**Savings: 60%** – Direct steps reduce verbosity while guiding the model.

**Tree of Thoughts (ToT):**
Explore multiple reasoning paths with branching and evaluation.

```text
[?→!]path1:●explore|branch:optionA|score:⟨high,low⟩|[∀→]path2:●explore|branch:optionB|evaluate:∥path1|select:best
●synthesize|paths:all|output:optimal_solution
```

**English Equivalent (~40 tokens):** "Explore multiple paths: consider option A and evaluate its viability. For option B, compare alignment with A. Synthesize the best solution."
**Savings: 75%** – Symbols like [?→!] for conditionals and ∥ for alignment enable compact tree structures.

**Multiple Outputs with Parsing and Checking:**
Generate variants, parse results, and verify consistency.

```text
●generate|variants:3|domains:reasoning,facts,logic|parse:each|check:≠inconsistencies|output:⟦verified⟧
```

**English Equivalent (~30 tokens):** "Generate three reasoning variants across domains. Parse each output and check for inconsistencies. Provide verified results."
**Savings: 65%** – ⟨⟩ for distributions and ≠ for checks streamline multi-output workflows.

**Multi-Model Collaboration:**
Agents/models pass structured reasoning via Vector-Native for joint problem-solving.

```text
# Model 1 → Model 2 (A2A)
●collaborate|task:complex_query|partial:reasoning_steps|handover:━model2|expect:refinement
```

**English Equivalent (~35 tokens):** "I've done initial reasoning steps on this query. Hand over to the next model for refinement and collaboration."
**Savings: 70%** – ━ for connections and A2A format enables seamless multi-model handoffs without natural language overhead.

**A2A Handoff:**
Direct task transfer between agents.

```text
# Agent A to Agent B
●handoff|task:analyze_data|context:⟦Q4_metrics⟧|target:agentB|priority:high
```

**English Equivalent (~28 tokens):** "Hand off the data analysis task with Q4 metrics context to Agent B as high priority."
**Savings: 65%** – Structured handover with ⟦⟧ blocks for context minimizes description.

**Group Broadcast:**
Announce to multiple agents simultaneously.

```text
●broadcast|message:status_update|recipients:agentA,agentB,agentC|data:⊕results|ack:required
```

**English Equivalent (~32 tokens):** "Broadcast this status update with combined results to Agents A, B, and C, requiring acknowledgments."
**Savings: 70%** – ⊕ for data merging and comma-separated recipients enable efficient group communication.

**Collaborative Reasoning Chain:**
Chain contributions across agents for joint output.

```text
# Agent 1: Initial step
●chain|step:1|reason:problem_analysis|link:━next
# Agent 2: Builds on chain
●chain|step:2|reason:option_evaluation|link:∥prev|output:⟦synthesis⟧
```

**English Equivalent (~45 tokens):** "Start the reasoning chain with problem analysis, then the next agent evaluates options aligned with the previous step and synthesizes the output."
**Savings: 75%** – ━ and ∥ link steps precisely, building chains without repetitive explanations.

**Task Delegation:**
Delegate subtasks with expectations.

```text
●delegate|subtask:validate_facts|to:agentC|params:dataset:sales|expect:⟨verified,flagged⟩|timeout:30s
```

**English Equivalent (~30 tokens):** "Delegate fact validation on the sales dataset to Agent C, expecting verified or flagged results within 30 seconds."
**Savings: 68%** – ⟨⟩ for expected outcomes and inline params streamline delegation.

These patterns support efficient multi-agent flows. Integrate with the parser for automatic routing and execution.

## Symbol Reference

### Attention (L0) – Triggers Focus

- `●` Full (weight=1.0) – Maximum attention
- `◐` Partial (weight=0.5) – Moderate focus
- `○` None (weight=0.0) – Background
- `━` Connection – Links operations

### Vectors (L1) – Embedding Operations

- `⊕` Add – Vector addition/combine
- `⊗` Multiply – Element-wise multiplication
- `⊖` Subtract – Vector difference
- `∠` Angle – Cosine similarity
- `∥` Parallel – Alignment check
- `⊥` Perpendicular – Orthogonality

### Probabilities (L2) – Prediction Cues

- `⟨⟩` Distribution – Weighted options
- `△` Increase – Boost probability
- `▽` Decrease – Reduce probability
- `≈` Optional – Approximate/nullable
- `≠` Not – Negation/difference

### Structures (L3) – Control Flow

- `[?→!]` Conditional – If-then
- `[∀→]` Universal – For all
- `[⟲]` Recursive – Loop/iteration
- `[T]×[V]` Transform – Type conversion
- `⟦...⟧` Block – Delimited output

See [`LANGUAGE_SPEC.md`](../LANGUAGE_SPEC.md) for full details and extensions.

**Pro Tip:** Test examples with `python tests/test_token_reduction.py` to verify savings (up to 95.7% in minimal variant).