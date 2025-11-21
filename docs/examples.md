# Examples

## Basic Syntax

```text
●operation|param1:value1|param2:value2
```

**Rules:**

1. Start with attention symbol (`●`, `○`, `━`) – leverages pre-trained importance/attention associations
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
result = agent_b.execute(task)  # Leverages pre-trained associations for efficient processing
```

**Benefit:** Variable compression (10-95% depending on task type) + clearer intent. The format is structured for programmatic parsing, making it useful for multi-agent systems where precision matters.

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
Leverages pre-trained associations for structured operation, eliminating English parsing overhead.

## Advanced Examples

**Universal Quantifier:**

```text
●process∀|items:all|status:active
```

**Existential Check:**

```text
●find∃|condition:match|result:found
```

**Optional Parameter:**

```text
●create≈|name:widget|optional:true
```

**Token Savings:** Complex English (~50 tokens) → Vector-Native (~15 tokens), 70% reduction.

## Reasoning Techniques

Vector-Native enables efficient implementation of advanced reasoning techniques by structuring prompts with symbols for step-by-step logic, branching, evaluation, and collaboration.

**Chain of Thought (CoT):**
Break down reasoning into sequential steps for better accuracy.

```text
●reason|step1:analyze_problem|step2:identify_assumptions|step3:evaluate_options|step4:conclude|output:reasoning
```

**English Equivalent (~25 tokens):** "Think step by step: first analyze the problem, then identify assumptions, evaluate options, and conclude. Output your reasoning."
**Savings: 60%** – Direct steps reduce verbosity while guiding the model.

**Tree of Thoughts (ToT):**
Explore multiple reasoning paths with branching and evaluation.

```text
●explore∥|branch1:optionA|branch2:optionB|evaluate:similarity∠|select:best
●synthesize|paths:all|output:optimal_solution
```

**English Equivalent (~40 tokens):** "Explore multiple paths: consider option A and option B. Evaluate similarity between them. Synthesize the best solution."
**Savings: 75%** – Symbols like ∥ for parallel paths and ∠ for similarity enable compact tree structures.

**Multiple Outputs with Parsing and Checking:**
Generate variants, parse results, and verify consistency.

```text
●generate|variants:3|domains:reasoning,facts,logic|parse:each|check≠inconsistencies|output:verified
```

**English Equivalent (~30 tokens):** "Generate three reasoning variants across domains. Parse each output and check for inconsistencies. Provide verified results."
**Savings: 65%** – ≠ for negation checks streamline multi-output workflows.

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
●handoff|task:analyze_data|context:Q4_metrics|target:agentB|priority:high
```

**English Equivalent (~28 tokens):** "Hand off the data analysis task with Q4 metrics context to Agent B as high priority."
**Savings: 65%** – Structured handover minimizes description.

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
●chain|step:2|reason:option_evaluation|link:∥prev|output:synthesis
```

**English Equivalent (~45 tokens):** "Start the reasoning chain with problem analysis, then the next agent evaluates options aligned with the previous step and synthesizes the output."
**Savings: 75%** – ━ and ∥ link steps precisely, building chains without repetitive explanations.

**Task Delegation:**
Delegate subtasks with expectations.

```text
●delegate|subtask:validate_facts|to:agentC|params:dataset:sales|expect:verified,flagged|timeout:30s
```

**English Equivalent (~30 tokens):** "Delegate fact validation on the sales dataset to Agent C, expecting verified or flagged results within 30 seconds."
**Savings: 68%** – Inline params streamline delegation.

These patterns support efficient multi-agent flows. Integrate with the parser for automatic routing and execution.

## Symbol Reference

**How Symbols Work:** Symbols leverage pre-trained associations that already exist in the model. The system prompt guides the model to use these associations, eliminating filler words and ambiguity. The core value is **precision** (clearer intent), not just compression. Token reduction varies widely (10-95%) based on task type.

### Attention (L0) – Pre-Trained Associations

- `●` Full – Pre-trained: importance/selected (Eisenhower Matrix, UI states)
- `○` None – Pre-trained: empty/inactive (UI states)
- `━` Connection – Pre-trained: linking/connection (em dash usage)

### Vectors (L1) – Pre-Trained Associations

- `⊕` Add – Pre-trained: addition (mathematical operations)
- `⊗` Multiply – Pre-trained: tensor product (mathematical operations)
- `∠` Angle – Pre-trained: angle symbol (geometry/trigonometry)
- `∥` Parallel – Pre-trained: parallel lines (geometry)
- `⊥` Perpendicular – Pre-trained: perpendicular symbol (geometry)

### Probabilities (L2) – Pre-Trained Associations

- `≈` Optional – Pre-trained: approximately equal (mathematics)
- `≠` Not – Pre-trained: not equal (mathematics/programming)

### Structures (L3) – Pre-Trained Associations

- `∀` Universal – Pre-trained: for all (mathematical logic)
- `∃` Existential – Pre-trained: there exists (mathematical logic)

See [`LANGUAGE_SPEC.md`](../LANGUAGE_SPEC.md) for full details and extensions.

**Pro Tip:** Test examples with `python tests/test_token_reduction.py` to verify savings (up to 95.7% in minimal variant).