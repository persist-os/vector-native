# Quick Start: Try Vector-Native in 5 Minutes

**No code required.** Just translate your system prompt and test it.

---

## Step 1: Understand the Concept

**System prompts** are instructions you give to AI that users never see. Examples:
- "You are a helpful assistant that provides detailed responses..."
- "Always format your output as JSON..."
- "Pay attention to the user's needs and respond professionally..."

**Key insight:** Since users never see these prompts, they don't need to be in natural language. Structured symbols can be clearer and more efficient.

---

## Step 2: See Examples (Before → After)

### Example 1: Basic Assistant

**Before (English):**
```
You are a helpful assistant. Always provide detailed responses 
in a professional tone. Pay attention to the user's needs.
```

**After (Vector-Native):**
```
●assistant|mode:helpful|detail:high|tone:professional|focus:user_needs
```

**Why it works:** Same meaning, less filler, clearer structure.

---

### Example 2: JSON Output Requirement

**Before (English):**
```
You are an API assistant. Always output valid JSON. Never include 
explanations outside the JSON. Use snake_case for keys.
```

**After (Vector-Native):**
```
●assistant|output:json|format:snake_case|strict:true|explanations:none
```

---

### Example 3: Code Generator

**Before (English):**
```
You are a code generation assistant. Generate Python code that follows 
PEP 8 style guidelines. Include type hints and docstrings.
```

**After (Vector-Native):**
```
●assistant|task:code_generation|language:python|style:pep8|include:type_hints,docstrings
```

---

## Step 3: Learn the Translation Pattern

### Basic Structure
```
●role|property1:value1|property2:value2
```

### Translation Rules

1. **Start with role:** `●assistant`, `●system`, `●api`, etc.
2. **Properties are key:value pairs** separated by `|`
3. **No filler words:** "always", "please", "make sure" → just state what you want
4. **Be explicit:** "detailed responses" → `detail:high`
5. **Use underscores** for multi-word values: `user_needs` not "user needs"

### Common Translations

| English | Vector-Native |
|---------|---------------|
| "helpful assistant" | `mode:helpful` |
| "detailed responses" | `detail:high` |
| "professional tone" | `tone:professional` |
| "output as JSON" | `output:json` |
| "follow PEP 8" | `style:pep8` |
| "include examples" | `include:examples` |
| "no explanations" | `explanations:none` |

---

## Step 4: Test It (No Code!)

### Option A: ChatGPT/Claude

1. Copy your Vector-Native prompt
2. Paste it into ChatGPT or Claude as the system message
3. Test if the AI follows the instructions

**Example test:**
- System: `●assistant|output:json|format:snake_case`
- User: "List 3 colors"
- Expected: `{"colors": ["red", "green", "blue"]}`

### Option B: API Playground

1. Go to OpenAI Playground or Anthropic Console
2. Paste Vector-Native prompt in "System" field
3. Test with sample queries

**Pro tip:** The AI might not understand Vector-Native perfectly on first try. That's okay! The goal is testing if structured prompts work better than natural language for YOUR use case.

---

## Step 5: Iterate

Vector-Native is **hybrid**. You can mix English and symbols:

```
●assistant|mode:helpful|detail:high

Provide detailed explanations for complex topics. 
Keep responses under 500 words unless asked for more detail.
```

**The LLM dynamically chooses** which parts to compress based on the task. Start simple, test, iterate.

---

## Common Questions

### Q: Do I need to teach the AI Vector-Native?

**No.** The symbols leverage pre-trained associations (from training data). Just use them. The AI will recognize patterns like `●` (importance), `|` (properties), `:` (key-value).

### Q: What if the AI doesn't understand?

**Try simpler structure first:**
- Start: `●assistant|mode:helpful`
- Then add: `●assistant|mode:helpful|detail:high`
- Keep testing until you find what works

### Q: Can I use this for user-facing messages?

**No.** Vector-Native is for **system prompts** and **agent-to-agent communication** only. Users should always see natural language.

### Q: How much reduction should I expect?

**It varies wildly.** Programmatic tasks (APIs, configs) compress more. Creative tasks compress less. Focus on **clarity**, not compression.

---

## For Developers: Code Setup (Optional)

If you want to run automated tests or build tools:

### Installation

```bash
git clone https://github.com/persist-os/vector-native
cd vector-native
pip install -r requirements.txt
```

### Use in Code

```python
from vector_native import get_vector_native_system_prompt

# Load a pre-made system prompt
prompt = get_vector_native_system_prompt("strict")

# Use with OpenAI
import openai
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Your query here"}
    ]
)
```

### Run Tests

```bash
python tests/test_token_reduction.py
```

Generates JSON reports in `tests/test_results/` showing token reduction across different scenarios.

---

## What's Next?

1. **Try it:** Translate one of your system prompts
2. **Test it:** Use ChatGPT or API playground
3. **Share results:** Open an issue on GitHub with your findings
4. **Contribute:** Create new prompt variants for your domain

**Remember:** This is an experiment. Results vary. The goal is exploring whether structured symbols improve precision in machine-to-machine communication.

---

## Quick Links

- **[Examples](./examples.md)** - More before/after examples
- **[How to Read](./how-to-read.md)** - Learn to read Vector-Native fluently
- **[Use Cases](./use-cases.md)** - 30+ potential applications
- **[Why It Works](./why-it-works.md)** - Technical explanation
- **[FAQ](./faq.md)** - Common questions
