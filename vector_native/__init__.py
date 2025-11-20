"""
Vector-Native: Symbol-based language that maps to LLM computational operations.

Completion token reduction verified through testing (gpt-4o-mini):
- Strict variant: 88.8% average (75.0% - 94.2% range), 80% compliance
- Balanced variant: 95.4% average (successful tests), 40% compliance
- Minimal variant: 95.7% average (successful tests), 40% compliance
"""

from vector_native.llm_integration import (
    get_vector_native_system_prompt,
    list_prompt_variants,
    create_openai_client,
    create_gemini_client,
)
from vector_native.tokenizer import count_tokens, calculate_reduction
from vector_native.parser import (
    parse_vector_native,
    parse_vector_native_hybrid,
    validate_syntax,
    parse_with_fallback,
    ParsedOperation,
    ParseError,
    extract_operations,
    extract_prose,
    HybridContent,
)

__version__ = "0.1.0"
__all__ = [
    # Prompts
    "get_vector_native_system_prompt",
    "list_prompt_variants",
    # LLM Clients
    "create_openai_client",
    "create_gemini_client",
    # Tokenizer
    "count_tokens",
    "calculate_reduction",
    # Parser
    "parse_vector_native",
    "parse_vector_native_hybrid",
    "validate_syntax",
    "parse_with_fallback",
    "ParsedOperation",
    "ParseError",
    "extract_operations",
    "extract_prose",
    "HybridContent",
]
