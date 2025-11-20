"""
Vector-Native Language: Protocol Primitives (L0-L3)

Maps symbols to actual LLM computational operations.
"""

# L0: Attention Mechanisms
ATTENTION_SYMBOLS = {
    "●": {"name": "full", "weight": 1.0, "description": "Full attention"},
    "◐": {"name": "partial", "weight": 0.5, "description": "Partial attention"},
    "○": {"name": "none", "weight": 0.0, "description": "No attention"},
    "━": {"name": "connection", "weight": None, "description": "Connection marker"},
}

# L1: Vector Operations
VECTOR_SYMBOLS = {
    "⊕": {"name": "add", "operation": "vector_addition"},
    "⊗": {"name": "multiply", "operation": "matrix_multiplication"},
    "⊖": {"name": "subtract", "operation": "vector_subtraction"},
    "∠": {"name": "angle", "operation": "cosine_similarity"},
    "∥": {"name": "parallel", "operation": "parallel_check"},
    "⊥": {"name": "perpendicular", "operation": "perpendicular_check"},
}

# L2: Probability Distributions
PROBABILITY_SYMBOLS = {
    "⟨": {"name": "distribution_start", "operation": "probability_distribution"},
    "⟩": {"name": "distribution_end", "operation": "probability_distribution"},
    "△": {"name": "increase", "operation": "increase_probability"},
    "▽": {"name": "decrease", "operation": "decrease_probability"},
    "≈": {"name": "optional", "operation": "optional_marker"},
    "≠": {"name": "not", "operation": "negation"},
}

# L3: Structures
STRUCTURE_SYMBOLS = {
    "[?→!]": {"name": "conditional", "operation": "conditional_flow"},
    "[∀→]": {"name": "universal", "operation": "universal_quantifier"},
    "[∃→]": {"name": "existential", "operation": "existential_quantifier"},
    "[⟲]": {"name": "recursive", "operation": "recursive_pattern"},
    "[T]×[V]": {"name": "transform", "operation": "transform_operation"},
}

# Combined symbol registry
ALL_SYMBOLS = {
    **ATTENTION_SYMBOLS,
    **VECTOR_SYMBOLS,
    **PROBABILITY_SYMBOLS,
    **STRUCTURE_SYMBOLS,
}


def get_symbol_info(symbol: str) -> dict:
    """Get information about a symbol."""
    return ALL_SYMBOLS.get(symbol, {"name": "unknown", "description": "Unknown symbol"})


def is_valid_symbol(symbol: str) -> bool:
    """Check if symbol is valid vector-native symbol."""
    return symbol in ALL_SYMBOLS


def get_symbols_by_level(level: int) -> dict:
    """Get symbols for a specific level (0-3)."""
    levels = {
        0: ATTENTION_SYMBOLS,
        1: VECTOR_SYMBOLS,
        2: PROBABILITY_SYMBOLS,
        3: STRUCTURE_SYMBOLS,
    }
    return levels.get(level, {})

