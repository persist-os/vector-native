"""
Prompt Loader - Loads and manages YAML prompt templates.

Provides centralized prompt management for VN quality evaluation.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    """Loads and manages prompt templates from YAML files."""
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize the prompt loader.
        
        Args:
            prompts_dir: Directory containing prompt YAML files.
                        Defaults to prompts/ folder relative to this file.
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent
        
        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def load_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """
        Load a prompt template from YAML file.
        
        Args:
            prompt_name: Name of the prompt file (without .yaml extension)
                        Can include subdirectory (e.g., 'evaluation/judge')
            
        Returns:
            Dict containing prompt template and configuration
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        # Check cache first
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        # Load from file
        prompt_path = self.prompts_dir / f"{prompt_name}.yaml"
        
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}\n"
                f"Available prompts: {self.list_available_prompts()}"
            )
        
        try:
            with open(prompt_path, 'r') as f:
                prompt_data = yaml.safe_load(f)
            
            # Validate required fields
            if 'system_context' not in prompt_data:
                logger.warning(f"Prompt {prompt_name} missing 'system_context' field")
            
            # Cache and return
            self._cache[prompt_name] = prompt_data
            return prompt_data
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in {prompt_path}: {e}")
    
    def list_available_prompts(self) -> list[str]:
        """
        List all available prompt files.
        
        Returns:
            List of prompt names (without .yaml extension)
        """
        prompts = []
        for p in self.prompts_dir.rglob("*.yaml"):
            # Get relative path without extension
            rel_path = p.relative_to(self.prompts_dir)
            prompts.append(str(rel_path.with_suffix('')))
        return prompts
    
    def build_prompt(
        self,
        prompt_name: str,
        template_key: str,
        **kwargs
    ) -> str:
        """
        Build a complete prompt from template with substitutions.
        
        Args:
            prompt_name: Name of prompt file (can include subdirectory)
            template_key: Key of the template to use (e.g., 'task_template')
            **kwargs: Variables to substitute in template
            
        Returns:
            Complete prompt string with substitutions applied
        """
        prompt_data = self.load_prompt(prompt_name)
        
        if template_key not in prompt_data:
            raise KeyError(
                f"Template key '{template_key}' not found in {prompt_name}.yaml\n"
                f"Available keys: {list(prompt_data.keys())}"
            )
        
        template = prompt_data[template_key]
        
        # Handle nested dict templates (e.g., examples)
        if isinstance(template, dict):
            template = str(template)
        
        # Perform substitutions
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise KeyError(
                f"Missing required variable {e} for template '{template_key}' "
                f"in {prompt_name}.yaml\nProvided: {list(kwargs.keys())}"
            )
    
    def get_config(self, prompt_name: str, config_key: str, default: Any = None) -> Any:
        """
        Get configuration value from prompt file.
        
        Args:
            prompt_name: Name of prompt file
            config_key: Configuration key (e.g., 'temperature', 'max_tokens')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        prompt_data = self.load_prompt(prompt_name)
        return prompt_data.get(config_key, default)
    
    def get_system_context(self, prompt_name: str) -> str:
        """
        Get system context message for a prompt.
        
        Args:
            prompt_name: Name of prompt file
            
        Returns:
            System context string
        """
        prompt_data = self.load_prompt(prompt_name)
        return prompt_data.get('system_context', '')
    
    def clear_cache(self):
        """Clear the prompt cache (useful for development/testing)."""
        self._cache = {}


# Global prompt loader instance
_loader = None


def get_prompt_loader() -> PromptLoader:
    """Get the global prompt loader instance."""
    global _loader
    if _loader is None:
        _loader = PromptLoader()
    return _loader

