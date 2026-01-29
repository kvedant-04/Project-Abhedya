"""
Configuration management system.

Manages system configuration with fail-safe defaults and validation.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from abhedya.core.constants import (
    DEFAULT_ACTION,
    DEFAULT_THREAT_LEVEL,
    MANDATORY_HUMAN_APPROVAL,
    SYSTEM_MODE_MONITORING
)


class ConfigManager:
    """
    Configuration manager with fail-safe defaults.
    
    Ensures all configuration values are safe and ethical.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config: Dict[str, Any] = {}
        self.config_file = config_file
        
        # Load defaults
        self._load_defaults()
        
        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)
        
        # Validate configuration
        self._validate_config()
    
    def _load_defaults(self):
        """Load fail-safe default configuration."""
        self.config = {
            "system": {
                "mode": SYSTEM_MODE_MONITORING,
                "human_operator_required": True,
                "mandatory_human_approval": MANDATORY_HUMAN_APPROVAL
            },
            "sensors": {
                "default_range_meters": 100000.0,
                "default_update_rate_hz": 1.0,
                "default_detection_threshold": 0.5
            },
            "assessment": {
                "protected_zone_radius": 50000.0,
                "critical_zone_radius": 20000.0,
                "hostile_speed_threshold": 300.0
            },
            "advisory": {
                "min_confidence": 0.5,
                "enable_probabilistic_reasoning": True
            },
            "safety": {
                "max_tracks_per_update": 1000,
                "max_recommendations_queue": 100,
                "system_timeout_seconds": 30.0,
                "fail_safe_action": DEFAULT_ACTION
            },
            "audit": {
                "enabled": True,
                "retention_days": 365,
                "explainability_required": True
            }
        }
    
    def load_from_file(self, config_file: str):
        """
        Load configuration from YAML file.
        
        Args:
            config_file: Path to configuration file
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            file_config = yaml.safe_load(f)
        
        # Merge with defaults (file config overrides defaults)
        self._merge_config(self.config, file_config)
    
    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _validate_config(self):
        """Validate configuration values and enforce safety constraints."""
        # Ensure mandatory human approval cannot be disabled
        if not self.config.get("system", {}).get("mandatory_human_approval", True):
            raise ValueError(
                "CRITICAL: Mandatory human approval cannot be disabled"
            )
        
        # Ensure human operator is required
        if not self.config.get("system", {}).get("human_operator_required", True):
            raise ValueError(
                "CRITICAL: Human operator requirement cannot be disabled"
            )
        
        # Validate numeric ranges
        if "sensors" in self.config:
            sensors_config = self.config["sensors"]
            if sensors_config.get("default_detection_threshold", 0.5) < 0.0:
                raise ValueError("Detection threshold must be >= 0.0")
            if sensors_config.get("default_detection_threshold", 0.5) > 1.0:
                raise ValueError("Detection threshold must be <= 1.0")
        
        if "advisory" in self.config:
            advisory_config = self.config["advisory"]
            if advisory_config.get("min_confidence", 0.5) < 0.0:
                raise ValueError("Advisory confidence must be >= 0.0")
            if advisory_config.get("min_confidence", 0.5) > 1.0:
                raise ValueError("Advisory confidence must be <= 1.0")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path (e.g., "system.mode")
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split(".")
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path
            value: Value to set
        """
        keys = key_path.split(".")
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        
        # Re-validate after setting
        self._validate_config()
    
    def save_to_file(self, config_file: Optional[str] = None):
        """
        Save configuration to YAML file.
        
        Args:
            config_file: Output file path (uses instance config_file if None)
        """
        output_file = config_file or self.config_file
        if not output_file:
            raise ValueError("No configuration file path specified")
        
        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

