"""
LLM Integration: Load vector-native system prompts and create LLM clients.

Multiple prompt variants available in prompts/ directory.
Supports OpenAI and Google Gemini APIs.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


def get_vector_native_system_prompt(variant: str = "strict") -> str:
    """
    Get system prompt for vector-native communication.
    
    Args:
        variant: Prompt variant to load. Options:
            - "strict" (default): High compliance, production-ready
            - "balanced": Moderate enforcement, good default
            - "minimal": Compact, experimental
            - Or filename without extension (e.g., "custom")
    
    Returns:
        System prompt string written in vector-native
    
    Raises:
        FileNotFoundError: If variant doesn't exist
    
    Examples:
        >>> prompt = get_vector_native_system_prompt("strict")
        >>> prompt = get_vector_native_system_prompt("balanced")
        >>> prompt = get_vector_native_system_prompt("minimal")
    """
    # Get project root (parent of vector_native package)
    package_dir = Path(__file__).parent
    project_root = package_dir.parent
    prompts_dir = project_root / "prompts"
    
    # Load prompt file
    prompt_file = prompts_dir / f"{variant}.txt"
    
    if not prompt_file.exists():
        available = [f.stem for f in prompts_dir.glob("*.txt")]
        raise FileNotFoundError(
            f"Prompt variant '{variant}' not found. "
            f"Available: {', '.join(available)}"
        )
    
    return prompt_file.read_text(encoding="utf-8").strip()


def list_prompt_variants() -> list[str]:
    """
    List all available prompt variants.
    
    Returns:
        List of variant names (without .txt extension)
    
    Example:
        >>> variants = list_prompt_variants()
        >>> print(variants)
        ['strict', 'balanced', 'minimal']
    """
    package_dir = Path(__file__).parent
    project_root = package_dir.parent
    prompts_dir = project_root / "prompts"
    
    if not prompts_dir.exists():
        return []
    
    return [f.stem for f in prompts_dir.glob("*.txt")]


def create_openai_client(api_key: Optional[str] = None) -> OpenAI:
    """
    Create OpenAI client.
    
    Args:
        api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
    
    Returns:
        OpenAI client instance
    
    Raises:
        ImportError: If openai package not installed
        ValueError: If API key not found
    """
    if not OPENAI_AVAILABLE:
        raise ImportError(
            "OpenAI package not installed. Install with: pip install openai"
        )
    
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Set OPENAI_API_KEY env var or pass api_key parameter."
        )
    
    return OpenAI(api_key=api_key)


def create_gemini_client(api_key: Optional[str] = None):
    """
    Create Gemini client (configured, ready to use).
    
    Args:
        api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
    
    Returns:
        Configured genai module (call genai.GenerativeModel() to create models)
    
    Raises:
        ImportError: If google-generativeai package not installed
        ValueError: If API key not found
    
    Example:
        >>> genai = create_gemini_client()
        >>> model = genai.GenerativeModel("gemini-1.5-flash")
    """
    if not GEMINI_AVAILABLE:
        raise ImportError(
            "Gemini package not installed. Install with: pip install google-generativeai"
        )
    
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Set GEMINI_API_KEY env var or pass api_key parameter."
        )
    
    genai.configure(api_key=api_key)
    return genai
