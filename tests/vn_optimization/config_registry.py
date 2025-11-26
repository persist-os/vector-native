"""
Configuration Registry

Store and compare VN configs, track best configs per model, enable systematic knowledge base.
"""

import json
import threading
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from .vn_config import VNConfig


@dataclass
class ConfigEntry:
    """Entry in configuration registry."""
    config_id: str
    model: str
    provider: str
    config: Dict[str, Any]  # VNConfig.to_searchable_dict()
    metrics: Dict[str, float]  # {"compliance": float, "token_reduction": float}
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


class ConfigRegistry:
    """
    Registry for storing and comparing VN configs.
    
    Stores configs with metadata: {model, config, metrics, timestamp}
    Supports persistence via JSON file storage.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize registry.
        
        Args:
            storage_path: Optional path to JSON storage file
                (defaults to test_results/vn_configs/registry.json)
        """
        if storage_path is None:
            # Default to test_results/vn_configs/registry.json
            base_path = Path(__file__).parent.parent.parent / "test_results" / "vn_configs"
            base_path.mkdir(parents=True, exist_ok=True)
            storage_path = base_path / "registry.json"
        
        self.storage_path = Path(storage_path)
        self._lock = threading.Lock()  # Thread-safe operations
        self._entries: Dict[str, ConfigEntry] = {}
        
        # Load existing entries
        self._load()
    
    def _load(self) -> None:
        """Load entries from storage."""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            for entry_data in data.get("entries", []):
                entry = ConfigEntry(**entry_data)
                self._entries[entry.config_id] = entry
        except Exception:
            # If loading fails, start with empty registry
            pass
    
    def _save(self) -> None:
        """Save entries to storage."""
        with self._lock:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert entries to dict
            data = {
                "entries": [asdict(entry) for entry in self._entries.values()],
                "updated_at": datetime.now().isoformat(),
            }
            
            # Write to file
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def store_config(
        self,
        model: str,
        provider: str,
        vn_config: VNConfig,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store VN config with metadata.
        
        Args:
            model: Model identifier
            provider: Provider name
            vn_config: VNConfig instance
            metrics: Metrics dict (compliance, token_reduction)
            metadata: Optional additional metadata
        
        Returns:
            Config ID (unique identifier)
        """
        import uuid
        import time
        
        config_id = f"{model}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        entry = ConfigEntry(
            config_id=config_id,
            model=model,
            provider=provider,
            config=vn_config.to_searchable_dict(),
            metrics=metrics,
            timestamp=time.time(),
            metadata=metadata or {},
        )
        
        with self._lock:
            self._entries[config_id] = entry
            self._save()
        
        return config_id
    
    def get_best_config(self, model: str) -> Optional[tuple[VNConfig, Dict[str, float]]]:
        """
        Get best config for a specific model.
        
        Args:
            model: Model identifier
        
        Returns:
            Tuple of (VNConfig, metrics) or None if no configs found
        """
        # Filter entries for this model
        model_entries = [
            entry for entry in self._entries.values()
            if entry.model == model
        ]
        
        if not model_entries:
            return None
        
        # Find best config (weighted score: compliance * 0.7 + token_reduction * 0.3)
        best_entry = max(
            model_entries,
            key=lambda e: e.metrics.get("compliance", 0.0) * 0.7 + e.metrics.get("token_reduction", 0.0) * 0.3
        )
        
        vn_config = VNConfig.from_dict(best_entry.config)
        return vn_config, best_entry.metrics
    
    def compare_configs(
        self,
        config_a_id: str,
        config_b_id: str,
        model: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two configs.
        
        Args:
            config_a_id: Config ID for first config
            config_b_id: Config ID for second config
            model: Optional model filter (both configs must be for this model)
        
        Returns:
            Comparison dict or None if configs not found
        """
        entry_a = self._entries.get(config_a_id)
        entry_b = self._entries.get(config_b_id)
        
        if not entry_a or not entry_b:
            return None
        
        # Filter by model if provided
        if model and (entry_a.model != model or entry_b.model != model):
            return None
        
        # Calculate comparison
        return {
            "config_a": {
                "id": config_a_id,
                "config": entry_a.config,
                "metrics": entry_a.metrics,
                "timestamp": entry_a.timestamp,
            },
            "config_b": {
                "id": config_b_id,
                "config": entry_b.config,
                "metrics": entry_b.metrics,
                "timestamp": entry_b.timestamp,
            },
            "comparison": {
                "compliance_delta": entry_b.metrics.get("compliance", 0.0) - entry_a.metrics.get("compliance", 0.0),
                "token_reduction_delta": entry_b.metrics.get("token_reduction", 0.0) - entry_a.metrics.get("token_reduction", 0.0),
            },
        }
    
    def list_configs(self, model: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all configs (optionally filtered by model).
        
        Args:
            model: Optional model filter
        
        Returns:
            List of config dicts
        """
        entries = list(self._entries.values())
        
        if model:
            entries = [e for e in entries if e.model == model]
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        return [
            {
                "config_id": entry.config_id,
                "model": entry.model,
                "provider": entry.provider,
                "config": entry.config,
                "metrics": entry.metrics,
                "timestamp": entry.timestamp,
                "metadata": entry.metadata,
            }
            for entry in entries
        ]
    
    def get_evolution(self, model: str) -> List[Dict[str, Any]]:
        """
        Get config evolution for a model (sorted by timestamp).
        
        Args:
            model: Model identifier
        
        Returns:
            List of config entries sorted by timestamp (oldest first)
        """
        model_entries = [
            entry for entry in self._entries.values()
            if entry.model == model
        ]
        
        # Sort by timestamp (oldest first)
        model_entries.sort(key=lambda e: e.timestamp)
        
        return [
            {
                "config_id": entry.config_id,
                "config": entry.config,
                "metrics": entry.metrics,
                "timestamp": entry.timestamp,
                "metadata": entry.metadata,
            }
            for entry in model_entries
        ]
    
    def get_improvements(self, model: str) -> List[Dict[str, Any]]:
        """
        Identify config improvements for a model.
        
        Args:
            model: Model identifier
        
        Returns:
            List of improvement records showing config evolution
        """
        evolution = self.get_evolution(model)
        
        if len(evolution) < 2:
            return []
        
        improvements = []
        
        for i in range(1, len(evolution)):
            prev = evolution[i - 1]
            curr = evolution[i]
            
            compliance_delta = curr["metrics"].get("compliance", 0.0) - prev["metrics"].get("compliance", 0.0)
            token_delta = curr["metrics"].get("token_reduction", 0.0) - prev["metrics"].get("token_reduction", 0.0)
            
            if compliance_delta > 0 or token_delta > 0:
                improvements.append({
                    "from_config": prev["config_id"],
                    "to_config": curr["config_id"],
                    "improvements": {
                        "compliance_delta": compliance_delta,
                        "token_reduction_delta": token_delta,
                    },
                    "timestamp": curr["timestamp"],
                })
        
        return improvements

