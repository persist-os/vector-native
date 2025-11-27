"""
Multi-provider LLM client for VN quality evaluation.

Uses direct provider SDKs (no Agno dependency).
Supports OpenAI, Anthropic (Claude), and Google (Gemini).
Includes automatic fallback if one provider fails.
"""

import os
import logging
from typing import Optional, List, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load Environment (Local .env takes precedence, if exists)
CURRENT_DIR = Path(__file__).parent.parent.resolve()
env_file = CURRENT_DIR / ".env"
if env_file.exists():
    try:
        load_dotenv(env_file, override=True)
    except Exception:
        pass  # .env loading optional

logger = logging.getLogger(__name__)

# Default fallback order: OpenAI → Gemini (Claude removed as default)
DEFAULT_FALLBACK_MODELS = [
    ("gpt-4o-mini", "OPENAI_API_KEY"),
    ("gemini-1.5-flash", "GOOGLE_API_KEY"),
    ("gpt-4o", "OPENAI_API_KEY"),
]


class LLMClient:
    """
    Multi-provider LLM client using direct SDK calls.
    
    Supports OpenAI, Anthropic (Claude), and Google (Gemini).
    Includes automatic fallback when a provider fails.
    No Agno dependency - uses provider SDKs directly.
    """
    
    def __init__(self, fallback_models: Optional[List[Tuple[str, str]]] = None):
        """
        Initialize client.
        
        Args:
            fallback_models: List of (model_name, env_var) tuples for fallback.
                           Defaults to OpenAI → Gemini.
        """
        self._openai_client = None
        self._anthropic_client = None
        self._google_configured = False
        self.fallback_models = fallback_models or DEFAULT_FALLBACK_MODELS
    
    def _has_api_key(self, env_var: str) -> bool:
        """Check if an API key is available."""
        return bool(os.getenv(env_var) or os.getenv(env_var.replace("_API_KEY", "_KEY")))
    
    def _get_openai_client(self):
        """Lazy initialize OpenAI client."""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI()
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._openai_client
    
    def _get_anthropic_client(self):
        """Lazy initialize Anthropic client."""
        if self._anthropic_client is None:
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic()
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
        return self._anthropic_client
    
    def _configure_google(self):
        """Configure Google Gemini."""
        if not self._google_configured:
            try:
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    self._google_configured = True
                else:
                    raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable required")
            except ImportError:
                raise ImportError("google-generativeai package required. Install with: pip install google-generativeai")
    
    def call(
        self, 
        prompt: str, 
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
        fallback: bool = True
    ) -> str:
        """
        Call an LLM using the appropriate provider SDK.
        
        Args:
            prompt: The user prompt
            model: Model identifier (e.g., "gpt-4o", "gemini-1.5-flash")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: Optional system prompt
            fallback: If True, try fallback models on failure (default: True)
            
        Returns:
            Generated text response
        """
        # Try primary model first
        try:
            return self._call_model(prompt, model, temperature, max_tokens, system)
        except Exception as primary_error:
            if not fallback:
                raise RuntimeError(f"LLM call failed for {model}: {primary_error}")
            
            logger.warning(f"Primary model {model} failed: {primary_error}. Trying fallbacks...")
            
            # Try fallback models
            errors = [(model, str(primary_error))]
            
            for fallback_model, env_var in self.fallback_models:
                # Skip if same as primary or no API key
                if fallback_model.lower() == model.lower():
                    continue
                if not self._has_api_key(env_var):
                    logger.debug(f"Skipping {fallback_model}: no {env_var}")
                    continue
                
                try:
                    logger.info(f"Trying fallback model: {fallback_model}")
                    result = self._call_model(prompt, fallback_model, temperature, max_tokens, system)
                    logger.info(f"Fallback {fallback_model} succeeded")
                    return result
                except Exception as fallback_error:
                    errors.append((fallback_model, str(fallback_error)))
                    logger.warning(f"Fallback {fallback_model} failed: {fallback_error}")
                    continue
            
            # All models failed
            error_summary = "; ".join([f"{m}: {e}" for m, e in errors])
            raise RuntimeError(f"All LLM models failed. Errors: {error_summary}")
    
    def _call_model(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system: Optional[str]
    ) -> str:
        """Call a specific model without fallback."""
        model_lower = model.lower()
        
        if "gemini" in model_lower:
            return self._call_gemini(prompt, model, temperature, max_tokens, system)
        elif "claude" in model_lower:
            return self._call_anthropic(prompt, model, temperature, max_tokens, system)
        elif "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
            return self._call_openai(prompt, model, temperature, max_tokens, system)
        else:
            # Default to OpenAI
            logger.warning(f"Unknown model '{model}', defaulting to OpenAI")
            return self._call_openai(prompt, model, temperature, max_tokens, system)
    
    def _call_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system: Optional[str]
    ) -> str:
        """Call OpenAI API."""
        client = self._get_openai_client()
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def _call_anthropic(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system: Optional[str]
    ) -> str:
        """Call Anthropic Claude API."""
        client = self._get_anthropic_client()
        
        # Map common model names to Anthropic format
        model_map = {
            "claude-sonnet-4": "claude-sonnet-4-20250514",
            "claude-sonnet-4.5": "claude-sonnet-4-20250514",
            "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-sonnet-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307",
        }
        
        model_id = model_map.get(model.lower(), model)
        
        kwargs = {
            "model": model_id,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system:
            kwargs["system"] = system
        
        # Temperature not supported for some Claude models, add with caution
        if temperature != 1.0:
            kwargs["temperature"] = temperature
        
        response = client.messages.create(**kwargs)
        
        return response.content[0].text
    
    def _call_gemini(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system: Optional[str]
    ) -> str:
        """Call Google Gemini API."""
        self._configure_google()
        
        import google.generativeai as genai
        
        # Map common model names to Gemini format
        model_map = {
            "gemini-2.0-flash": "gemini-2.0-flash-exp",
            "gemini-pro": "gemini-pro",
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-1.5-flash": "gemini-1.5-flash",
        }
        
        model_id = model_map.get(model.lower(), model)
        
        # Create model with configuration
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        gen_model = genai.GenerativeModel(
            model_name=model_id,
            generation_config=generation_config,
            system_instruction=system if system else None
        )
        
        response = gen_model.generate_content(prompt)
        
        return response.text
    
    def get_available_models(self) -> List[str]:
        """Return list of models that have API keys configured."""
        available = []
        
        if self._has_api_key("OPENAI_API_KEY"):
            available.extend(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"])
        
        if self._has_api_key("GOOGLE_API_KEY"):
            available.extend(["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"])
        
        if self._has_api_key("ANTHROPIC_API_KEY"):
            available.extend(["claude-sonnet-4", "claude-3.5-sonnet", "claude-3-haiku"])
        
        return available


# ==============================================================================
# TEST BLOCK
# ==============================================================================
if __name__ == "__main__":
    # Simple self-test
    logging.basicConfig(level=logging.INFO)
    client = LLMClient()
    
    print("Testing Multi-Provider LLM Client with Fallback...")
    print(f"Available models: {client.get_available_models()}")
    
    try:
        # This will automatically fallback if needed
        response = client.call(
            "What is 2+2? Reply with just the number.",
            model="gpt-4o-mini",
            max_tokens=10,
            fallback=True
        )
        print(f"\nResponse: {response.strip()}")
        print("✅ LLM call succeeded (with automatic fallback if needed)")
    except Exception as e:
        print(f"\n❌ All models failed: {e}")
