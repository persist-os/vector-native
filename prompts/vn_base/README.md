# Vector Native Base Prompts

System prompts that instruct LLMs to output in Vector Native format.

## Variants

| Variant | Compliance | Token Savings | Use Case |
|---------|------------|---------------|----------|
| `minimal` | ~40% | ~95% | Maximum efficiency, testing |
| `standard` | ~80% | ~89% | Production, reliable output |

## Files

- `minimal.yaml` - Shortest prompt, highest token savings, lower compliance
- `standard.yaml` - Detailed prompt, best compliance, production-ready

## Usage

```python
import yaml

with open("prompts/vn_base/minimal.yaml") as f:
    prompt_data = yaml.safe_load(f)
    system_prompt = prompt_data["instructions"]
```

## Schema

```yaml
name: str           # Human-readable name
description: str    # One-line description  
compliance: str     # Expected compliance rate
savings: str        # Expected token savings
instructions: str   # The actual system prompt
```