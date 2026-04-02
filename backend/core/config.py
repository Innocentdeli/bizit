import yaml
from pathlib import Path

class ConfigLoader:
    """Load and validate BIZIT configuration."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            print(f"[CONFIG] No config file found at {self.config_path}. Using defaults.")
            return self._get_defaults()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                print(f"[CONFIG] Loaded configuration from {self.config_path}")
                return config
        except Exception as e:
            print(f"[CONFIG] Error loading config: {e}. Using defaults.")
            return self._get_defaults()
    
    def _get_defaults(self) -> dict:
        """Return default configuration."""
        return {
            "shopify": {"enabled": False},
            "salesforce": {"enabled": False},
            "sap": {"enabled": False},
            "iot": {"enabled": True, "broker": "localhost"},
            "rabbitmq": {"enabled": False, "host": "localhost", "port": 5672},
            "neo4j": {"enabled": False, "uri": "bolt://localhost:7687"},
            "embeddings": {"enabled": True, "model": "all-MiniLM-L6-v2"},
            "learning": {"enabled": True, "policy_update_frequency": 100}
        }
    
    def get(self, key: str, default=None):
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
            if not isinstance(value, dict):
                return value
        return default if value == {} else value
    
    def is_enabled(self, service: str) -> bool:
        """Check if a service is enabled."""
        return self.config.get(service, {}).get("enabled", False)
