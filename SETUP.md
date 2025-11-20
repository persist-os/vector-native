# Vector-Native Setup Guide

Complete setup instructions for the Vector-Native project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/persist-os/vector-native
cd vector-native
```

### 2. Create Virtual Environment (Recommended)

**Why use a virtual environment?**
- Isolates dependencies from other Python projects
- Prevents version conflicts
- Makes it easier to manage dependencies

**Create and activate:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Verify activation:**
You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

**All dependencies (production + development):**
```bash
pip install -r requirements.txt
```

**Manual installation (if needed):**
```bash
pip install openai python-dotenv tiktoken
# Optional: For Gemini support
pip install google-generativeai
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Required for OpenAI tests
OPENAI_API_KEY=your-openai-api-key-here

# Optional: For Gemini support
GEMINI_API_KEY=your-gemini-api-key-here
```

**Security Note:** The `.env` file is already in `.gitignore` - never commit API keys!

### 5. Verify Installation

```bash
# Test imports
python -c "from vector_native import get_vector_native_system_prompt; print('✅ Installation successful!')"

# Run tests (requires OPENAI_API_KEY in .env)
python tests/test_token_reduction.py
```

## Troubleshooting

### Virtual Environment Issues

**Problem:** `python3 -m venv venv` fails
- **Solution:** Ensure Python 3.8+ is installed: `python3 --version`
- **Alternative:** Use `python -m venv venv` if `python3` isn't available

**Problem:** `source venv/bin/activate` doesn't work
- **Windows:** Use `venv\Scripts\activate` instead
- **PowerShell:** May need to run `Set-ExecutionPolicy RemoteSigned` first

### Dependency Issues

**Problem:** `pip install` fails with permission errors
- **Solution:** Use virtual environment (see above) or use `pip install --user`

**Problem:** `tiktoken` installation fails
- **Solution:** Ensure you have a C compiler installed (required for tiktoken)
- **macOS:** Install Xcode Command Line Tools: `xcode-select --install`
- **Linux:** Install build-essential: `sudo apt-get install build-essential`
- **Windows:** Install Visual Studio Build Tools

**Problem:** `openai` package not found
- **Solution:** Ensure virtual environment is activated and run `pip install -r requirements.txt`

### API Key Issues

**Problem:** Tests fail with "API key not found"
- **Solution:** Ensure `.env` file exists in project root with `OPENAI_API_KEY=your-key`
- **Verify:** Check `.env` file exists: `ls -la .env` (should show file)

**Problem:** API calls fail with authentication errors
- **Solution:** Verify API key is correct and has sufficient credits/quota

## Development Workflow

### Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
python tests/test_token_reduction.py
python tests/test_parser_hybrid.py

# Run with pytest (if installed)
pytest tests/
```

### Deactivating Virtual Environment

When done working:

```bash
deactivate
```

## Project Structure

```
vector-native/
├── requirements.txt          # All dependencies (production + development)
├── .env                      # Environment variables (create this)
├── venv/                     # Virtual environment (create this)
├── vector_native/            # Package code
├── tests/                    # Test files
└── prompts/                  # System prompt variants
```

## Next Steps

- Read [README.md](README.md) for usage examples
- Check [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) for protocol details
- Review [prompts/README.md](prompts/README.md) for prompt variants

