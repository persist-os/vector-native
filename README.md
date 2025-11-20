# Vector-Native

**Native vector-space language for LLMs - 30-80% token reduction**

Vector-native is a symbol-based language that maps directly to LLM computational operations. Agents understand it natively - no translation needed.

## The Core Innovation

**The system prompt teaches LLMs vector-native by speaking it to them.**

The system prompt (`vector_native/system_prompt.txt`) is written **IN vector-native itself**. LLMs learn the language by reading it. This is the unlock.

## The Difference

**Without vector-native (verbose, unstructured):**
```
Hello! I see the time is early in San Francisco. How can I help you this morning?

That's a big question! As of today, November 20, 2025, the global news is focused on several major, complex issues. Here are the top headlines and ongoing developments across the world:

🌍 Major Global News
Ukraine Peace Plan Discussions: There is significant international activity around potential peace plans...
[continues for hundreds of tokens]
```

**With vector-native (concise, structured):**
```
●acknowledged|status:complete
●current_global_events|
●conflict_update|russia_ukraine:active|middle_east:volatile|sudan:escalating
●economy_update|markets:volatile|nvidia:strong_earnings|uk_manufacturing:declining
●politics_social_update|us_politics:trump_diplomacy|tech_regulation:india_dpdp|health:who_toilet_warning
●next_action|detail_topic:geopolitical,economic,or_social
```

**Result:** 80%+ token reduction, structured output, native understanding.

## Quick Start

```python
from vector_native.llm_integration import get_vector_native_system_prompt

# Get the system prompt (written in vector-native)
system_prompt = get_vector_native_system_prompt()

# Use it with any LLM
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Analyze sales data"}
    ]
)
# LLM responds in vector-native: "●analyze|dataset:sales|status:complete"
```

## How It Works

**Symbols map to actual LLM operations:**
- `●` = Full attention (1.0)
- `◐` = Partial attention (0.5)
- `○` = No attention (0.0)
- `⊕` = Vector addition
- `⊗` = Matrix multiplication

**Syntax:** `●operation|param:value|param2:value`

**Example:**
```
●analyze|dataset:Q4_sales|metrics:revenue,profit|output:json
```

## Installation

```bash
pip install vector-native
```

## API

```python
from vector_native import get_vector_native_system_prompt, parse_vector_native, count_tokens

# Get system prompt
prompt = get_vector_native_system_prompt()

# Parse vector-native
parsed = parse_vector_native("●create_widget|userId:123")
# {"operation": "create_widget", "params": {"userId": "123"}}

# Count tokens
tokens = count_tokens("●analyze|dataset:sales")
```

## Why This Matters

**Token reduction enables scale:**
- 30-80% reduction (scales with prompt length)
- More tokens = more LLM calls = more collaboration
- Enables artificial civilization at scale

**Native operations enable precision:**
- Direct mapping to LLM computations
- No translation overhead
- Agents understand natively

## License

MIT License
