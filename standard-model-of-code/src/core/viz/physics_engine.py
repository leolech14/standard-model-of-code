"""
Physics engine for force-directed graph layout.

Provides physics configuration for the 3D force graph visualization.
"""

from typing import Any, Dict

from .token_resolver import get_resolver


class PhysicsEngine:
    """Provides physics configuration for force-directed graph layout."""

    def __init__(self):
        """Initialize the physics engine."""
        self.resolver = get_resolver()

    def to_js_config(self) -> Dict[str, Any]:
        """
        Generate JavaScript-compatible physics configuration.

        Returns:
            Dictionary with physics settings for force-graph library
        """
        return {
            "forces": {
                "charge": {
                    "enabled": True,
                    "strength": self.resolver.appearance("physics.forces.charge.strength", -120),
                    "distanceMax": self.resolver.appearance("physics.forces.charge.distanceMax", 500),
                    "distanceMin": self.resolver.appearance("physics.forces.charge.distanceMin", 1)
                },
                "link": {
                    "enabled": True,
                    "distance": self.resolver.appearance("physics.forces.link.distance", 50),
                    "strength": self.resolver.appearance("physics.forces.link.strength", 0.3)
                },
                "center": {
                    "enabled": True,
                    "strength": self.resolver.appearance("physics.forces.center.strength", 0.05)
                },
                "collision": {
                    "enabled": False,
                    "radius": self.resolver.appearance("physics.forces.collision.radius", 5)
                }
            },
            "simulation": {
                "alphaMin": self.resolver.appearance("physics.simulation.alphaMin", 0.001),
                "alphaDecay": self.resolver.appearance("physics.simulation.alphaDecay", 0.0228),
                "velocityDecay": self.resolver.appearance("physics.simulation.velocityDecay", 0.4),
                "warmupTicks": 0,
                "cooldownTicks": self.resolver.appearance("physics.simulation.cooldownTicks", 200)
            },
            "constraints": {
                "fixY": False,
                "flattenZ": False
            }
        }
