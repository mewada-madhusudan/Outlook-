"""
Configuration management for the Outlook Automation Tool
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class AuthConfig:
    """Authentication configuration"""
    client_id: str = ""
    tenant_id: str = "common"
    scopes: list = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = [
                "Mail.ReadWrite",
                "Mail.Send", 
                "MailboxSettings.Read",
                "Calendars.ReadWrite",
                "offline_access"
            ]

@dataclass
class ZoomConfig:
    """Zoom API configuration"""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8080/callback"
    scopes: list = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = ["meeting:write", "recording:read"]

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///outlook_automation.db"
    echo: bool = False
    pool_size: int = 5

class Config:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_dir = Path.home() / ".outlook_automation"
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = config_file or (self.config_dir / "settings.json")
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "auth": asdict(AuthConfig()),
            "zoom": asdict(ZoomConfig()),
            "database": asdict(DatabaseConfig()),
            "ui": {
                "theme": "light",
                "window_geometry": None,
                "sidebar_width": 250
            },
            "features": {
                "zoom_integration": True,
                "rsvp_tracking": True,
                "attachment_rules": True,
                "webhooks": False
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._merge_config(default_config, loaded_config)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        self.config = default_config
        self.save_config()
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]):
        """Recursively merge loaded config with defaults"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    @property
    def auth_config(self) -> AuthConfig:
        """Get authentication configuration"""
        return AuthConfig(**self.config["auth"])
    
    @property
    def zoom_config(self) -> ZoomConfig:
        """Get Zoom configuration"""
        return ZoomConfig(**self.config["zoom"])
    
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return self.config["database"]["url"]
    
    @property
    def ui_theme(self) -> str:
        """Get UI theme"""
        return self.config["ui"]["theme"]
    
    def set_theme(self, theme: str):
        """Set UI theme"""
        self.config["ui"]["theme"] = theme
        self.save_config()
    
    def get_feature_flag(self, feature: str) -> bool:
        """Get feature flag status"""
        return self.config["features"].get(feature, False)
    
    def set_feature_flag(self, feature: str, enabled: bool):
        """Set feature flag status"""
        self.config["features"][feature] = enabled
        self.save_config()