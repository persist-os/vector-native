# How It Works

Vector-Native streamlines AI-to-AI communication through simple integration. This guide walks through practical steps: from prompting an LLM to parsing outputs and testing efficiency. (For the science behind efficiency, see [why-it-works.md](./why-it-works.md).)

## Step 1: Setup and Prompting

### Install and Prepare
1. Clone/install as in [Quick Start](../README.md#quick-start).
2. Choose a variant: `strict` for production (80% compliance), `balanced`/`minimal` for testing (95%+ reduction).

### Load System Prompt
Use a pre-built variant or custom:

```python
from vector_native import get_vector_native_system_prompt

# Strict for reliable A2A
system_prompt = get_vector_native_system_prompt("strict")

# Custom: Load from file
with open("prompts/my_variant.txt", "r") as f:
    system_prompt = f.read()
```

### Generate with LLM
Integrate into your API call (OpenAI example):

```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Process Q4 sales data with revenue/profit metrics."}
    ],
    temperature=0.1,  # Low for compliance
    max_tokens=200
)

output = response.choices[0].message.content
# Expected: ●process|data:Q4|metrics:revenue,profit
```

**Tip:** For A2A, prepend user message with operational cues: "●task|input:sales_data".

## Step 2: Parsing Outputs

Vector-Native outputs are structured—parse for actions/values.

### Simple Parser Example
```python
def parse_vector_native(output: str):
    operations = []
    for line in output.split("\n"):
        if line.strip():
            parts = line.split("|", 1)
            attention_op = parts[0].strip()  # e.g., ●process
            params = {}
            if len(parts) > 1:
                for param in parts[1].split("|"):
                    if ":" in param:
                        key, value = param.split(":", 1)
                        params[key.strip()] = value.strip()
            operations.append({
                "attention_op": attention_op,
                "params": params
            })
    return operations

# Usage
result = parse_vector_native("●analyze|dataset:Q4|metrics:revenue\n●report|format:json")
# Output: [{'attention_op': '●analyze', 'params': {'dataset': 'Q4', 'metrics': 'revenue'}}, ...]
```

### Handle Variants
- **Strict:** High structure—parse reliably.
- **Balanced/Minimal:** May mix English/symbols—add fallback: if no `●`, treat as natural language.

**Edge Case:** Multi-line blocks—split on newlines, validate each starts with attention symbol.

## Step 3: Integration in Workflows

### Agent-to-Agent Example
```python
class VectorAgent:
    def __init__(self, llm_client):
        self.client = llm_client
        self.system_prompt = get_vector_native_system_prompt("strict")
    
    def send_task(self, target_agent, task_desc):
        # Generate Vector-Native instruction
        prompt = f"●task|description:{task_desc}|target:{target_agent}"
        response = self.client.chat(self.system_prompt, prompt)
        
        # Parse and forward
        ops = parse_vector_native(response)
        return target_agent.receive(ops)  # Target parses/executes

# Usage: agent1.send_task(agent2, "Analyze sales")
```

### Tool Communication
For internal APIs:
```python
# Send Vector-Native to tool endpoint
import requests
payload = {"instruction": "●fetch|endpoint:/api/sales|filters:quarter:Q4"}
response = requests.post("/internal-tool", json=payload)

# Tool side: Parse and act
ops = parse_vector_native(payload["instruction"])
if ops[0]["attention_op"] == "●fetch":
    data = fetch_data(ops[0]["params"]["endpoint"], ops[0]["params"]["filters"])
    return {"result": data}
```

**Best Practice:** Use low temperature (0.1) for 80%+ compliance in strict mode.

## Step 4: Testing and Validation

### Run Token Reduction Tests
```bash
python tests/test_token_reduction.py --variant strict --scenarios 10
```
- Outputs JSON with % reduction (expect 88.8% avg for strict).
- Compare English vs Vector-Native completions.

### Compliance Check
```python
def check_compliance(output: str):
    has_attention = "●" in output or "○" in output or "━" in output
    has_structure = "|" in output and ":" in output
    return has_attention and has_structure  # Simple validator

# Test batch
assert check_compliance("●process|data:Q4")  # True
assert not check_compliance("Just process data")  # False
```

### Measure Savings
Integrate tokenizer:
```python
from vector_native.tokenizer import count_tokens

english_tokens = count_tokens("Give attention and add values")
vn_tokens = count_tokens("●⊕")
savings = (1 - vn_tokens / english_tokens) * 100  # ~80%
```

**Workflow:** Prompt → Generate → Parse → Execute → Log savings. Iterate on variants for your use case.

## Common Patterns and Tips

- **A2A Handoffs:** List multi-ops sequentially: ●step1...●step2...
- **Error Handling:** If low compliance, fallback to English parsing.
- **Scaling:** Savings potential depends on task type and use case—see README for details on variability.
- **Customization:** Extend parser for domain symbols (e.g., `●db_query`).

This practical flow enables 88-95% token efficiency in production A2A systems. For variants, see `prompts/`. Test thoroughly—compliance varies by model/task.
