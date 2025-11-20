# Quick Start

## Installation

```bash
# Clone this repo
git clone https://github.com/persist-os/vector-native
cd vector-native

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your-key" > .env
# Optional: For Gemini support
# echo "GEMINI_API_KEY=your-key" >> .env
```

**Note:** Virtual env recommended. See [`SETUP.md`](../SETUP.md) for details.

## Use a System Prompt

```python
# Option 1: Load from file
from pathlib import Path
prompt = Path("prompts/strict.txt").read_text()

# Option 2: Use helper
from vector_native import get_vector_native_system_prompt
prompt = get_vector_native_system_prompt("strict")  # or "balanced", "minimal"
```

## Available System Prompts

**Tested with OpenAI gpt-4o-mini (5 scenarios, README results):**

1. **`strict.txt`** - Production-ready (experimental)
   - 80% compliance, 88.8% avg reduction  
   - Imperative (MUST/NEVER), strict delimiters (`⟦...⟧`)  
   - Best for: A2A communication, cost-critical systems  
   - Cost savings: 93.6% at scale (1M tokens: $343 → $22)

2. **`balanced.txt`** - General use  
   - 40% compliance, 95.4% avg reduction  
   - Moderate guidance, flexible  
   - Best for: Experimentation, agent tools

3. **`minimal.txt`** - Learning/testing  
   - 40% compliance, 95.7% avg reduction  
   - Ultra-compact (4 lines)  
   - Best for: Quick tests, prompt development

## Run Tests

```bash
python tests/test_token_reduction.py
```

**Output:**  
- `tests/test_results/*.json` – Raw data  
- Terminal: Summary stats (aligns with README table)

## Try the Live Demo

**Interact with Vector-Native AI:** [Gemini Gem Demo](https://gemini.google.com/gem/1uvnWkhWpFj58qCF-McVBu0Zc36HYc1p6?usp=sharing)  

**Usage:** Prompt "Translate [request] to Vector-Native" to see efficient A2A format. Expect `●` symbols—designed for machines, not human chat.

**Note:** Demo shows operational triggers in action; results match 88-95% reductions.

**Pro Tip:** Vector-Native for internal/A2A only—not user messages (keep natural language for humans).