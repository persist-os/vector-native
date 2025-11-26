"""
VN Configuration Abstraction

Create VNConfig class, make symbols/prompts/variants searchable for the-convergence optimization.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from pathlib import Path
import sys

# Import vector-native functions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from vector_native import get_vector_native_system_prompt
from vector_native.language import ATTENTION_SYMBOLS, ALL_SYMBOLS


@dataclass
class VNConfig:
    """
    Vector-Native configuration that makes symbols, prompts, and variants searchable.
    
    Fields:
        symbols: Dictionary mapping symbol roles to symbol characters
            - "attention": Symbol for attention (default: "●")
            - "background": Symbol for background (default: "○")
            - "connection": Symbol for connection (default: "━")
            - Can include other symbols from ALL_SYMBOLS
        prompt_variant: Prompt variant name ("strict", "balanced", "minimal", or custom)
        custom_prompt: Optional custom prompt text (overrides prompt_variant if provided)
    """
    symbols: Dict[str, str] = field(default_factory=lambda: {
        "attention": "●",
        "background": "○",
        "connection": "━",
    })
    prompt_variant: str = "strict"
    custom_prompt: Optional[str] = None
    
    def to_searchable_dict(self) -> Dict[str, Any]:
        """
        Convert config to dictionary suitable for the-convergence search space.
        
        Returns:
            Dictionary with searchable fields for optimization
        """
        return {
            "symbols": self.symbols.copy(),
            "prompt_variant": self.prompt_variant,
            "custom_prompt": self.custom_prompt,
        }
    
    def generate_system_prompt(self) -> str:
        """
        Generate system prompt with symbol substitution.
        
        Uses get_vector_native_system_prompt with symbol substitution.
        If custom_prompt is provided, uses that instead.
        
        Returns:
            System prompt string with symbols substituted
        """
        if self.custom_prompt:
            prompt = self.custom_prompt
        else:
            prompt = get_vector_native_system_prompt(self.prompt_variant)
        
        # Substitute symbols in prompt
        # Replace default symbols with configured symbols
        # Default attention symbols: ●, ◐, ○
        # Default background: ○
        # Default connection: ━
        
        # Map common symbol substitutions
        symbol_map = {
            "●": self.symbols.get("attention", "●"),  # Full attention
            "◐": self.symbols.get("partial_attention", "◐"),  # Partial attention
            "○": self.symbols.get("background", "○"),  # Background/no attention
            "━": self.symbols.get("connection", "━"),  # Connection marker
        }
        
        # Apply substitutions
        for old_symbol, new_symbol in symbol_map.items():
            if old_symbol != new_symbol:
                prompt = prompt.replace(old_symbol, new_symbol)
        
        return prompt
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VNConfig":
        """
        Create VNConfig from dictionary.
        
        Args:
            data: Dictionary with symbols, prompt_variant, custom_prompt
        
        Returns:
            VNConfig instance
        """
        return cls(
            symbols=data.get("symbols", {}),
            prompt_variant=data.get("prompt_variant", "strict"),
            custom_prompt=data.get("custom_prompt"),
        )
    
    def mutate(
        self,
        symbol_mutations: Optional[Dict[str, str]] = None,
        prompt_variant: Optional[str] = None,
        custom_prompt: Optional[str] = None,
    ) -> "VNConfig":
        """
        Create mutated version of config for evolutionary search.
        
        Args:
            symbol_mutations: Dictionary of symbol role -> new symbol
            prompt_variant: New prompt variant (if provided)
            custom_prompt: New custom prompt (if provided)
        
        Returns:
            New VNConfig with mutations applied
        """
        new_symbols = self.symbols.copy()
        if symbol_mutations:
            new_symbols.update(symbol_mutations)
        
        return VNConfig(
            symbols=new_symbols,
            prompt_variant=prompt_variant if prompt_variant is not None else self.prompt_variant,
            custom_prompt=custom_prompt if custom_prompt is not None else self.custom_prompt,
        )
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate symbols are valid
        for role, symbol in self.symbols.items():
            if symbol not in ALL_SYMBOLS and symbol not in ["●", "○", "━", "*", "-", ".", "·"]:
                # Allow common alternatives for testing
                if symbol not in ["*", "-", ".", "·", "→", "←", "↑", "↓"]:
                    return False, f"Invalid symbol '{symbol}' for role '{role}'"
        
        # Validate prompt_variant exists (if not custom)
        if not self.custom_prompt:
            try:
                get_vector_native_system_prompt(self.prompt_variant)
            except FileNotFoundError:
                return False, f"Prompt variant '{self.prompt_variant}' not found"
        
        return True, None
    
    def __repr__(self) -> str:
        """String representation."""
        symbols_str = ", ".join(f"{k}:{v}" for k, v in self.symbols.items())
        return f"VNConfig(symbols={{{symbols_str}}}, variant={self.prompt_variant}, custom={self.custom_prompt is not None})"

