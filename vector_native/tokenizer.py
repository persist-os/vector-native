"""
Vector-Native Tokenizer: Count tokens to prove reduction.
"""

import re
from typing import Optional

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text.
    
    Uses tiktoken if available, otherwise simple word-based estimation.
    """
    if TIKTOKEN_AVAILABLE:
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback to simple estimation
            pass
    
    # Simple estimation: ~0.75 tokens per word + symbols count as 1 token
    # This is approximate but sufficient for MVP proof
    words = len(text.split())
    symbols = len(re.findall(r'[●◐○⊕⊗⊖∠∥⊥⟨⟩△▽≈≠]', text))
    structures = len(re.findall(r'\[[?∀∃⟲T]→[!V]\]|\[T\]×\[V\]', text))
    
    # Base word tokens + symbol tokens
    estimated = int(words * 0.75) + symbols + structures
    
    return max(1, estimated)  # At least 1 token


def calculate_reduction(english_text: str, vector_native_text: str, model: str = "gpt-4") -> dict:
    """
    Calculate token reduction percentage.
    
    Returns:
        {
            "before": int,
            "after": int,
            "reduction": float,  # Percentage
            "reduction_tokens": int
        }
    """
    before = count_tokens(english_text, model)
    after = count_tokens(vector_native_text, model)
    reduction_tokens = before - after
    reduction_pct = (reduction_tokens / before * 100) if before > 0 else 0.0
    
    return {
        "before": before,
        "after": after,
        "reduction": round(reduction_pct, 1),
        "reduction_tokens": reduction_tokens,
    }

