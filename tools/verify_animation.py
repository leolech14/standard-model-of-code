
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.viz.appearance_engine import AppearanceEngine

def verify_animation_config():
    engine = AppearanceEngine()
    config = engine.get_animation_config()
    
    print("Checking Animation Config...")
    print(f"Config keys: {list(config.keys())}")
    
    # Verify core keys
    assert "hue" in config, "Missing hue config"
    assert "ripple" in config, "Missing ripple config"
    
    # Verify specific values (defaults from app.js backup / new tokens)
    ripple_speed = config["ripple"]["speed"]
    print(f"Ripple Speed: {ripple_speed}")
    assert ripple_speed == 0.035, f"Expected ripple speed 0.035, got {ripple_speed}"
    
    hue_damping = config["hue"]["damping"]
    print(f"Hue Damping: {hue_damping}")
    assert hue_damping == 0.9995, f"Expected hue damping 0.9995, got {hue_damping}"
    
    print("\n✅ VERIFICATION PASSED: AppearanceEngine is correctly loading animation tokens.")

if __name__ == "__main__":
    verify_animation_config()
