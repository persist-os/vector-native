"""
Vector-Native: Native vector-space language for LLMs.

30-80% token reduction through symbol-based syntax.
The system prompt teaches LLMs by speaking vector-native to them.
"""

from vector_native.llm_integration import get_vector_native_system_prompt
from vector_native.tokenizer import count_tokens

__version__ = "0.1.0"
__all__ = [
    "get_vector_native_system_prompt",
    "parse_vector_native",
    "validate_syntax",
    "count_tokens",
]

