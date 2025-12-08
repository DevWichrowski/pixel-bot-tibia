"""
Windify Bot - User Configuration
Manages persistent user settings stored in JSON.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Tuple, Dict, Any


@dataclass
class RegionConfig:
    """Configuration for HP/Mana regions."""
    hp_region: Optional[Tuple[int, int, int, int]] = None    # (x, y, width, height)
    mana_region: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    
    def is_hp_configured(self) -> bool:
        return self.hp_region is not None
    
    def is_mana_configured(self) -> bool:
        return self.mana_region is not None
    
    def is_fully_configured(self) -> bool:
        return self.is_hp_configured() and self.is_mana_configured()


@dataclass
class HealerConfig:
    """Configuration for auto-healer."""
    heal_enabled: bool = True
    heal_threshold: int = 75
    heal_hotkey: str = "F1"
    
    critical_enabled: bool = True
    critical_threshold: int = 50
    critical_hotkey: str = "F2"
    
    mana_enabled: bool = True
    mana_threshold: int = 60
    mana_hotkey: str = "F4"


@dataclass
class EaterConfig:
    """Configuration for auto eater."""
    enabled: bool = False
    food_type: str = "fire_mushroom"
    hotkey: str = "]"


@dataclass
class HasteConfig:
    """Configuration for auto haste."""
    enabled: bool = False
    hotkey: str = "x"


@dataclass
class SkinnerConfig:
    """Configuration for auto skinner."""
    enabled: bool = False
    hotkey: str = "["


@dataclass
class UserConfig:
    """Complete user configuration."""
    regions: RegionConfig = field(default_factory=RegionConfig)
    healer: HealerConfig = field(default_factory=HealerConfig)
    eater: EaterConfig = field(default_factory=EaterConfig)
    haste: HasteConfig = field(default_factory=HasteConfig)
    skinner: SkinnerConfig = field(default_factory=SkinnerConfig)


class ConfigManager:
    """Manages loading and saving user configuration."""
    
    DEFAULT_CONFIG_PATH = Path(__file__).parent / "user_config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Optional[UserConfig] = None
    
    @property
    def config(self) -> UserConfig:
        """Get current config, loading from disk if needed."""
        if self._config is None:
            self.load()
        return self._config
    
    def load(self) -> UserConfig:
        """Load configuration from JSON file."""
        if not os.path.exists(self.config_path):
            self._config = UserConfig()
            return self._config

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            self._config = self._from_dict(data)
            print(f"✅ Config loaded from {self.config_path}")
        except Exception as e:
            print(f"⚠️ Failed to load config: {e}")
            self._config = UserConfig()
        
        return self._config
    
    def save(self) -> bool:
        """Save current configuration to JSON file."""
        try:
            data = self._to_dict(self._config)
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Config saved to {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = UserConfig()
        if self.config_path.exists():
            self.config_path.unlink()
        print("🔄 Config reset to defaults")
    
    def reset_regions(self) -> None:
        """Reset only region configuration."""
        self._config.regions.hp_region = None
        self._config.regions.mana_region = None
        self.save()
    
    def set_hp_region(self, region: Tuple[int, int, int, int]) -> None:
        """Set HP region and save."""
        self._config.regions.hp_region = region
        self.save()
    
    def set_mana_region(self, region: Tuple[int, int, int, int]) -> None:
        """Set Mana region and save."""
        self._config.regions.mana_region = region
        self.save()
    
    def is_configured(self) -> bool:
        """Check if regions are configured for bot to start."""
        return self.config.regions.is_fully_configured()
    
    def _to_dict(self, config: UserConfig) -> Dict[str, Any]:
        """Convert config to JSON-serializable dict."""
        return {
            "regions": {
                "hp_region": list(config.regions.hp_region) if config.regions.hp_region else None,
                "mana_region": list(config.regions.mana_region) if config.regions.mana_region else None,
            },
            "healer": asdict(config.healer),
            "eater": asdict(config.eater),
            "haste": asdict(config.haste),
            "skinner": asdict(config.skinner)
        }
    
    def _from_dict(self, data: Dict[str, Any]) -> UserConfig:
        """Create config from dict."""
        regions_data = data.get("regions", {})
        healer_data = data.get("healer", {})
        eater_data = data.get("eater", {})
        haste_data = data.get("haste", {})
        skinner_data = data.get("skinner", {})
        
        hp_region = regions_data.get("hp_region")
        mana_region = regions_data.get("mana_region")
        
        return UserConfig(
            regions=RegionConfig(
                hp_region=tuple(hp_region) if hp_region else None,
                mana_region=tuple(mana_region) if mana_region else None,
            ),
            healer=HealerConfig(**healer_data) if healer_data else HealerConfig(),
            eater=EaterConfig(**eater_data) if eater_data else EaterConfig(),
            haste=HasteConfig(**haste_data) if haste_data else HasteConfig(),
            skinner=SkinnerConfig(**skinner_data) if skinner_data else SkinnerConfig()
        )


# Global config manager instance
config_manager = ConfigManager()


# Test
if __name__ == "__main__":
    manager = ConfigManager()
    
    # Test save/load
    manager.set_hp_region((100, 200, 80, 20))
    manager.set_mana_region((100, 220, 80, 20))
    
    print(f"HP configured: {manager.config.regions.is_hp_configured()}")
    print(f"Mana configured: {manager.config.regions.is_mana_configured()}")
    print(f"Fully configured: {manager.is_configured()}")
    
    # Reload and verify
    manager2 = ConfigManager()
    manager2.load()
    print(f"Loaded HP region: {manager2.config.regions.hp_region}")
