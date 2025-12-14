#!/usr/bin/env python3
"""
🔬 8D FLAT PARTICLE REGISTRY
All 8 dimensions as top-level fields (no grouping).
===================================================
"""
from dataclasses import dataclass, asdict
from typing import Optional, List
from enum import Enum
import json
from pathlib import Path


class Layer(Enum):
    INTERFACE = "interface"
    APP = "app"
    CORE = "core"
    INFRA = "infra"
    TESTS = "tests"
    UNKNOWN = "unknown"


class Role(Enum):
    ORCHESTRATOR = "orchestrator"
    DATA = "data"
    WORKER = "worker"
    UNKNOWN = "unknown"


class Boundary(Enum):
    INTERNAL = "internal"
    INPUT = "input"
    IO = "io"
    OUTPUT = "output"
    UNKNOWN = "unknown"


class State(Enum):
    STATEFUL = "stateful"
    STATELESS = "stateless"
    UNKNOWN = "unknown"


class Effect(Enum):
    READ = "read"
    WRITE = "write"
    READ_MODIFY = "read_modify"
    PURE = "pure"
    UNKNOWN = "unknown"


class Activation(Enum):
    EVENT = "event"
    TIME = "time"
    DIRECT = "direct"
    UNKNOWN = "unknown"


class Lifetime(Enum):
    TRANSIENT = "transient"
    SESSION = "session"
    GLOBAL = "global"
    UNKNOWN = "unknown"


@dataclass
class Particle8D:
    """A particle with 8 flat dimensions."""
    id: str
    name: str
    file: str
    line: int = 0
    
    # Dimension 1: WHAT (Material) - unique to our system
    material_continent: str = "Unknown"
    material_family: str = "Unknown"
    material_atom: str = "Unknown"
    
    # Dimension 2: Layer
    layer: str = "unknown"
    
    # Dimension 3: Role
    role: str = "unknown"
    
    # Dimension 4: Boundary
    boundary: str = "unknown"
    
    # Dimension 5: State
    state: str = "unknown"
    
    # Dimension 6: Effect
    effect: str = "unknown"
    
    # Dimension 7: Activation
    activation: str = "unknown"
    
    # Dimension 8: Lifetime
    lifetime: str = "unknown"
    
    # Bonus: Smells (not in 7D)
    smells: List[str] = None
    
    def __post_init__(self):
        if self.smells is None:
            self.smells = []
    
    def to_dict(self) -> dict:
        return asdict(self)


class ParticleRegistry8D:
    """Registry storing particles with 8D coordinates."""
    
    def __init__(self):
        self.particles: List[Particle8D] = []
    
    def add(self, particle: Particle8D):
        self.particles.append(particle)
    
    def export(self, output_path: str):
        """Export to JSON."""
        data = {
            "schema": "8D_FLAT",
            "dimensions": [
                "material", "layer", "role", "boundary",
                "state", "effect", "activation", "lifetime"
            ],
            "particle_count": len(self.particles),
            "particles": [p.to_dict() for p in self.particles],
            "stats": self._compute_stats()
        }
        Path(output_path).write_text(json.dumps(data, indent=2))
        return data
    
    def _compute_stats(self) -> dict:
        """Compute distribution stats per dimension."""
        stats = {
            "by_layer": {},
            "by_role": {},
            "by_boundary": {},
            "by_state": {},
            "by_effect": {},
            "by_activation": {},
            "by_lifetime": {},
            "by_material_continent": {},
        }
        for p in self.particles:
            stats["by_layer"][p.layer] = stats["by_layer"].get(p.layer, 0) + 1
            stats["by_role"][p.role] = stats["by_role"].get(p.role, 0) + 1
            stats["by_boundary"][p.boundary] = stats["by_boundary"].get(p.boundary, 0) + 1
            stats["by_state"][p.state] = stats["by_state"].get(p.state, 0) + 1
            stats["by_effect"][p.effect] = stats["by_effect"].get(p.effect, 0) + 1
            stats["by_activation"][p.activation] = stats["by_activation"].get(p.activation, 0) + 1
            stats["by_lifetime"][p.lifetime] = stats["by_lifetime"].get(p.lifetime, 0) + 1
            stats["by_material_continent"][p.material_continent] = stats["by_material_continent"].get(p.material_continent, 0) + 1
        return stats
