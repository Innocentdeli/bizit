import os
import yaml
from pathlib import Path
from typing import Optional, Any

class ConfigLoader:
    """Load and validate BIZIT configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
    
    def _resolve_config_path(self, path: Optional[str]) -> Path:
        """Find the config file across potential working directories."""
        env_path = os.getenv("CONFIG_PATH")
        if env_path:
            return Path(env_path)
        if path:
            return Path(path)
        
        # Check standard candidate locations
        project_root = Path(__file__).resolve().parent.parent.parent
        candidates = [
            project_root / "config.yaml",
            Path("config.yaml"),
            Path("../config.yaml"),
            project_root / "config.template.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return project_root / "config.yaml"
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file and overlay environment variables."""
        config = self._get_defaults()
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
                    if file_config and isinstance(file_config, dict):
                        config.update(file_config)
                        print(f"[CONFIG] Loaded configuration from {self.config_path}")
            except Exception as e:
                print(f"[CONFIG] Error loading config from {self.config_path}: {e}. Using defaults.")
        else:
            print(f"[CONFIG] No config file found at {self.config_path}. Using defaults.")

        # Environment variable overrides
        if os.getenv("RABBITMQ_HOST"):
            config.setdefault("rabbitmq", {})["host"] = os.getenv("RABBITMQ_HOST")
            config["rabbitmq"]["enabled"] = True
        if os.getenv("NEO4J_URI"):
            config.setdefault("neo4j", {})["uri"] = os.getenv("NEO4J_URI")
            config["neo4j"]["enabled"] = True
        if os.getenv("REDIS_HOST"):
            config.setdefault("redis", {})["host"] = os.getenv("REDIS_HOST")
            config["redis"]["enabled"] = True

        return config
    
    def _get_defaults(self) -> dict:
        """Return default configuration."""
        return {
            "shopify": {"enabled": False},
            "salesforce": {"enabled": False},
            "sap": {"enabled": False},
            "iot": {"enabled": True, "broker": "localhost"},
            "rabbitmq": {"enabled": False, "host": "localhost", "port": 5672},
            "neo4j": {"enabled": False, "uri": "bolt://localhost:7687"},
            "redis": {"enabled": False, "host": "localhost", "port": 6379},
            "embeddings": {"enabled": True, "model": "all-MiniLM-L6-v2"},
            "learning": {"enabled": True, "policy_update_frequency": 100}
        }
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value by dot-separated key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def is_enabled(self, service: str) -> bool:
        """Check if a service is enabled."""
        return bool(self.config.get(service, {}).get("enabled", False))
