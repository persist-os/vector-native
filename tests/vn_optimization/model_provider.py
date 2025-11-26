"""
Model Provider Abstraction

Abstracts model/provider, reuses Azure registry, supports multiple models
(gpt-4.1, grok-4-fast-reasoning, Llama-4-Scout-17B-16E-Instruct, OpenAI, Gemini).
"""

import os
from typing import Optional, Dict, Any, Protocol
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ChatCompletionClient(Protocol):
    """Protocol for chat completion clients (OpenAI-compatible interface)."""
    
    def chat(self):
        """Return chat interface."""
        ...
    
    class Chat:
        def completions(self):
            """Return completions interface."""
            ...
        
        class Completions:
            def create(self, **kwargs) -> Any:
                """Create chat completion."""
                ...


@dataclass
class ModelProviderConfig:
    """Configuration for model provider."""
    provider: str  # "openai", "azure", "gemini", "grok"
    model_id: str  # Model identifier (e.g., "gpt-4o-mini", "gpt-4.1-nano")
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    api_version: Optional[str] = None
    temperature: float = 0.0
    max_tokens: Optional[int] = None


class ModelProvider:
    """
    Model provider abstraction that supports multiple providers.
    
    Supports:
    - OpenAI (gpt-4o-mini, gpt-4o, etc.)
    - Azure (gpt-4.1-nano, gpt-4.1-mini, gpt-4.1, grok-4-fast-reasoning, etc.)
    - Gemini (via the-convergence adapters)
    """
    
    def __init__(self, config: ModelProviderConfig):
        """Initialize model provider."""
        self.config = config
        self._client: Optional[ChatCompletionClient] = None
    
    @property
    def client(self) -> ChatCompletionClient:
        """Get or create client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self) -> ChatCompletionClient:
        """Create client based on provider."""
        provider = self.config.provider.lower()
        
        if provider == "openai":
            return self._create_openai_client()
        elif provider in ("azure", "grok"):
            return self._create_azure_client()
        elif provider == "gemini":
            return self._create_gemini_client()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _create_openai_client(self) -> ChatCompletionClient:
        """Create OpenAI client."""
        from openai import OpenAI
        
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        return OpenAI(api_key=api_key)
    
    def _create_azure_client(self) -> ChatCompletionClient:
        """Create Azure client using Azure registry."""
        # Import Azure registry from backend
        import sys
        from pathlib import Path
        
        # Add backend to path if not already there
        backend_path = Path(__file__).parent.parent.parent.parent / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from app.agents.azure_registry import azure_registry
        from app.config import AZURE_API_KEY, AZURE_ENDPOINT
        from agno.models.azure.openai_chat import AzureOpenAI
        
        # Get model config from registry
        try:
            model_config = azure_registry.get_model_config(self.config.model_id)
        except ValueError:
            # If model not in registry, try direct deployment name
            deployment_name = self.config.model_id
            model_config = None
        else:
            deployment_name = model_config.deployment_name
        
        # Get API key and endpoint
        api_key = self.config.api_key or AZURE_API_KEY
        endpoint = self.config.endpoint or AZURE_ENDPOINT
        api_version = self.config.api_version or (model_config.api_version if model_config else "2024-06-01")
        
        if not api_key or not endpoint:
            raise ValueError("Azure requires api_key and endpoint")
        
        # Format endpoint with deployment
        if not endpoint.endswith("/"):
            endpoint = endpoint.rstrip("/")
        if deployment_name and f"/{deployment_name}" not in endpoint:
            endpoint = f"{endpoint}/{deployment_name}"
        
        return AzureOpenAI(
            id=deployment_name,
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens or (model_config.max_tokens if model_config else None),
        )
    
    def _create_gemini_client(self) -> ChatCompletionClient:
        """Create Gemini client."""
        # For now, use litellm for Gemini (the-convergence pattern)
        # This is a simplified version - full implementation would use the-convergence adapters
        try:
            import litellm
        except ImportError:
            raise ImportError("litellm required for Gemini support. Install with: pip install litellm")
        
        api_key = self.config.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        # Create a wrapper that provides OpenAI-compatible interface
        class GeminiClientWrapper:
            def __init__(self, model_id: str, api_key: str):
                self.model_id = model_id
                self.api_key = api_key
            
            class Chat:
                def __init__(self, parent):
                    self.parent = parent
                
                class Completions:
                    def __init__(self, parent):
                        self.parent = parent
                    
                    def create(self, **kwargs):
                        """Create completion using litellm."""
                        import litellm
                        
                        # Transform OpenAI format to litellm
                        messages = kwargs.get("messages", [])
                        model = kwargs.get("model", self.parent.parent.model_id)
                        temperature = kwargs.get("temperature", 0.0)
                        max_tokens = kwargs.get("max_tokens")
                        
                        response = litellm.completion(
                            model=f"gemini/{model}",
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            api_key=self.parent.parent.api_key,
                        )
                        
                        # Transform to OpenAI-compatible format
                        class Choice:
                            def __init__(self, message_content):
                                class Message:
                                    def __init__(self, content):
                                        self.content = content
                                self.message = Message(message_content)
                        
                        class Response:
                            def __init__(self, choices):
                                self.choices = choices
                        
                        return Response([Choice(response.choices[0].message.content)])
                
                def __init__(self, parent):
                    self.parent = parent
                    self.completions = self.Completions(self)
            
            def __init__(self, model_id: str, api_key: str):
                self.model_id = model_id
                self.api_key = api_key
                self.chat = self.Chat(self)
        
        return GeminiClientWrapper(self.config.model_id, api_key)
    
    def create_completion(self, messages: list, **kwargs) -> Any:
        """Create chat completion (unified interface)."""
        return self.client.chat.completions.create(
            model=self.config.model_id,
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            **{k: v for k, v in kwargs.items() if k not in ("model", "messages", "temperature", "max_tokens")}
        )


def create_model_provider(
    provider: str,
    model_id: str,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
) -> ModelProvider:
    """
    Factory function to create model provider.
    
    Args:
        provider: Provider name ("openai", "azure", "gemini", "grok")
        model_id: Model identifier
        api_key: Optional API key (uses env vars if not provided)
        endpoint: Optional endpoint (for Azure)
        temperature: Temperature setting
        max_tokens: Optional max tokens
    
    Returns:
        ModelProvider instance
    """
    config = ModelProviderConfig(
        provider=provider,
        model_id=model_id,
        api_key=api_key,
        endpoint=endpoint,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return ModelProvider(config)

