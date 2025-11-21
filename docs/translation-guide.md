# System Prompt Translation Guide

**Quick reference for translating English system prompts to Vector-Native.**

---

## Basic Structure

```
●role|property1:value1|property2:value2|property3:value3
```

**Rules:**
- Start with `●` (attention symbol)
- Follow with role: `assistant`, `system`, `api`, `agent`
- Properties separated by `|`
- Values use `:` between key and value
- Multi-word values use `_` (underscores): `user_needs` not "user needs"

---

## Common Role Types

```
●assistant    → General assistant
●api          → API/tool interactions
●agent        → Autonomous agent
●system       → System-level operations
●analyzer     → Analysis/processing
●generator    → Content generation
```

---

## Common Properties

### Behavior

```
mode:helpful           → Helpful behavior
mode:concise          → Brief responses
mode:detailed         → Detailed explanations
tone:professional     → Professional tone
tone:casual           → Casual tone
tone:technical        → Technical language
```

### Output Format

```
output:json           → JSON output
output:markdown       → Markdown output
output:plain_text     → Plain text only
format:snake_case     → Use snake_case
format:camelCase      → Use camelCase
strict:true           → Strict adherence
```

### Detail Level

```
detail:high           → Detailed responses
detail:medium         → Moderate detail
detail:low            → Minimal detail
verbosity:high        → Verbose
verbosity:low         → Concise
```

### Focus Areas

```
focus:user_needs      → Prioritize user needs
focus:accuracy        → Prioritize accuracy
focus:speed           → Prioritize speed
focus:clarity         → Prioritize clarity
```

### Constraints

```
max_length:500        → Max 500 words
include:examples      → Include examples
include:citations     → Include citations
exclude:jargon        → Avoid jargon
explanations:none     → No explanations
```

### Task-Specific

```
task:code_generation  → Code generation
task:analysis         → Data analysis
task:summarization    → Text summarization
task:translation      → Language translation
language:python       → Python language
language:javascript   → JavaScript language
style:pep8           → PEP 8 style
style:airbnb         → Airbnb style guide
```

---

## Translation Examples

### Example 1: Helpful Assistant

**English:**
```
You are a helpful assistant that provides detailed responses 
in a professional tone. Always pay attention to the user's needs.
```

**Vector-Native:**
```
●assistant|mode:helpful|detail:high|tone:professional|focus:user_needs
```

---

### Example 2: JSON API

**English:**
```
You are an API assistant. Always respond with valid JSON. 
Never include text outside the JSON structure. Use snake_case for keys.
```

**Vector-Native:**
```
●api|output:json|format:snake_case|strict:true|explanations:none
```

---

### Example 3: Code Generator

**English:**
```
You are a code generation assistant. Generate Python code following 
PEP 8 guidelines. Include type hints and detailed docstrings. 
Keep functions under 50 lines.
```

**Vector-Native:**
```
●generator|task:code_generation|language:python|style:pep8|include:type_hints,docstrings|max_length:50_lines
```

---

### Example 4: Data Analyzer

**English:**
```
You are a data analysis assistant. Analyze the provided data 
and return insights in markdown format. Focus on accuracy over speed. 
Include statistical evidence for all claims.
```

**Vector-Native:**
```
●analyzer|task:analysis|output:markdown|focus:accuracy|include:statistical_evidence
```

---

### Example 5: Concise Summarizer

**English:**
```
You are a summarization assistant. Provide brief, concise summaries. 
Keep summaries under 100 words. Avoid technical jargon.
```

**Vector-Native:**
```
●assistant|task:summarization|mode:concise|max_length:100_words|exclude:jargon
```

---

## Filler Words to Remove

**Don't include these in Vector-Native:**
- "always", "never", "please", "make sure"
- "you are", "you should", "try to"
- "it's important", "remember to"
- Articles: "a", "an", "the" (unless part of a proper name)

**Just state what you want directly:**
- ❌ "Please always make sure to include examples"
- ✅ `include:examples`

---

## Hybrid Approach (Mix English + Symbols)

You can combine both:

```
●assistant|mode:helpful|output:json

When generating JSON, ensure all strings are properly escaped.
Handle edge cases like null values and empty arrays gracefully.
```

**The AI dynamically chooses** which parts to compress. Start simple, test, iterate.

---

## Testing Your Translation

1. **Copy your Vector-Native prompt**
2. **Paste into ChatGPT/Claude** as system message
3. **Test with sample queries**
4. **Iterate based on results**

**Example test:**
- System: `●assistant|output:json|format:snake_case`
- User: "List 3 colors"
- Expected: `{"colors": ["red", "green", "blue"]}`

---

## Quick Checklist

- [ ] Started with `●role`
- [ ] Properties separated by `|`
- [ ] Key-value pairs use `:`
- [ ] Multi-word values use `_`
- [ ] Removed filler words
- [ ] Clear, explicit properties
- [ ] Tested with sample queries

---

## Common Mistakes

### ❌ Using spaces in values
```
●assistant|mode:very helpful    → WRONG
●assistant|mode:very_helpful    → CORRECT
```

### ❌ Including filler words
```
●assistant|please_be:helpful    → WRONG
●assistant|mode:helpful         → CORRECT
```

### ❌ Using quotes
```
●assistant|output:"json"        → WRONG
●assistant|output:json          → CORRECT
```

### ❌ Commas between properties
```
●assistant|mode:helpful, detail:high    → WRONG
●assistant|mode:helpful|detail:high     → CORRECT
```

---

## Need Help?

- **More examples:** See [`examples.md`](./examples.md)
- **Full quickstart:** See [`quickstart.md`](./quickstart.md)
- **Learn to read VN:** See [`how-to-read.md`](./how-to-read.md)
- **Questions:** Open an issue on GitHub

---

**Remember:** Vector-Native is an experiment. Results vary. Focus on **clarity** over compression.

