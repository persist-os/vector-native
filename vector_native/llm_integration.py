"""
LLM Integration: Teach LLMs to speak vector-native.

KEY INSIGHT: The system prompt is written IN vector-native itself!
We teach LLMs by speaking the language to them.
"""

from pathlib import Path


def get_vector_native_system_prompt() -> str:
    """
    Get system prompt that teaches LLM to speak vector-native.
    
    The prompt itself is written IN vector-native - we teach by example!
    
    Returns:
        System prompt string written in vector-native
    """
    prompt_path = Path(__file__).parent / "system_prompt.txt"
    return prompt_path.read_text(encoding="utf-8").strip()
