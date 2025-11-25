# Vector-Native Prompts

This directory contains prompts for Vector Native across different use cases. The goal is to have a set of prompts that are easy to understand, use, and contribute to.

## 📁 File Structure

Each prompt consists of **two files**:

1. **`.md` file** - The actual prompt content (written in Vector Native Hybrid syntax)
2. **`.yaml` file** - Metadata about the prompt (name, tags, usage, etc.)

### Example Structure

```text
prompts/
  ├── a2a/
  │   ├── a2a_notes_hybrid.md      # Prompt content
  │   └── a2a_notes_hybrid.yaml    # Metadata
  └── translation/
      ├── hybrid_quotes_vn.md      # Prompt content
      └── hybrid_quotes_vn.yaml    # Metadata
```

## ✍️ Formatting Prompts

### The `.md` File (Prompt Content)

Write your prompt using **Vector Native Hybrid Syntax**:

- **Logic Layer**: Use symbols (`●`, `⊕`, `━`) for operations, routing, and structure
- **Content Layer**: Use exact quotes `"..."` for verbatim content, instructions, or data
- **Structure**: One operation per line, no conversational filler

**Example:**

```markdown
●system|role:translator|mode:hybrid
⊕constraint|preserve:quotes|forbid:filler
"Never summarize a great line. Quote it."
```

### The `.yaml` File (Metadata)

Include standard metadata fields:

```yaml
name: Your Prompt Name
id: unique-id-v1
version: 1.0.0
author: your-name
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
license: MIT
status: stable  # or: experimental, deprecated

tags:
  - vector-native
  - your-tag
  - another-tag

description: >
  A brief description of what this prompt does
  and when to use it.

usage:
  input_format: plain_text  # or: json, markdown, etc.
  output_format: vector_native_hybrid
  system_prompt_path: ./your_prompt.md
```

## 🚀 Contributing Prompts

**No code required!** Contributing prompts is simple:

1. **Create your prompt files**:
   - Create a new `.md` file with your prompt content (use Vector Native Hybrid syntax)
   - Create a matching `.yaml` file with metadata

2. **Choose a location**:
   - Put related prompts in the same subdirectory (e.g., `a2a/`, `translation/`)
   - Or create a new subdirectory if your prompt is for a new use case

3. **Follow naming conventions**:
   - Use lowercase with underscores: `my_prompt_name.md`
   - Keep the `.md` and `.yaml` filenames matching

4. **Test your prompt**:
   - Try it out with different inputs
   - Make sure the Vector Native syntax is correct
   - Verify examples work as expected

5. **Document clearly**:
   - Include examples in your `.md` file
   - Write a clear description in your `.yaml` file
   - Add relevant tags for discoverability

## 🧪 Experimentation Encouraged

**We welcome experimental prompts!** Don't worry about perfection:

- ✅ Try new use cases
- ✅ Experiment with different Vector Native patterns
- ✅ Test edge cases
- ✅ Share what works (and what doesn't)

Set `status: experimental` in your `.yaml` file if you're still iterating. We can refine together!

## 📚 Current Prompts

- **[a2a_notes_hybrid.md](a2a/a2a_notes_hybrid.md)** - Writing A2A notes in Vector Native Hybrid Syntax
- **[hybrid_quotes_vn.md](translation/hybrid_quotes_vn.md)** - Translating English prose into Vector Native Hybrid Syntax

## 💡 Tips

- **Start simple**: Begin with a basic prompt and iterate
- **Use examples**: Include 2-3 examples in your `.md` file showing input/output
- **Tag well**: Add descriptive tags so others can find your prompt
- **Document intent**: Explain what problem your prompt solves in the description