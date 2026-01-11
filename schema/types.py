"""
Standard Model of Code - Python Types

Auto-generated dataclass definitions for the Standard Model particle schema.

Version: 1.0.0
See: https://standardmodelofcode.org/schemas/
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Enums
# ============================================================================

class Level(str, Enum):
    """Holarchy levels from L-3 (Bit) to L12 (Universe)"""
    L_3 = "L-3"
    L_2 = "L-2"
    L_1 = "L-1"
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"  # The Atom - Function/Method
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"
    L7 = "L7"
    L8 = "L8"
    L9 = "L9"
    L10 = "L10"
    L11 = "L11"
    L12 = "L12"


class Plane(str, Enum):
    """Popper's Three Worlds"""
    PHYSICAL = "Physical"
    VIRTUAL = "Virtual"
    SEMANTIC = "Semantic"


class Layer(str, Enum):
    """Clean Architecture layers"""
    INTERFACE = "Interface"
    APPLICATION = "Application"
    CORE = "Core"
    INFRASTRUCTURE = "Infrastructure"
    TEST = "Test"
    UNKNOWN = "Unknown"


class Boundary(str, Enum):
    """Information flow boundary"""
    INTERNAL = "Internal"
    INPUT = "Input"
    OUTPUT = "Output"
    I_O = "I-O"


class State(str, Enum):
    """State management characteristic"""
    STATEFUL = "Stateful"
    STATELESS = "Stateless"


class Effect(str, Enum):
    """Side effect classification"""
    PURE = "Pure"
    READ = "Read"
    WRITE = "Write"
    READ_WRITE = "ReadWrite"


class Lifecycle(str, Enum):
    """Object lifecycle phase"""
    CREATE = "Create"
    USE = "Use"
    DESTROY = "Destroy"


class Intent(str, Enum):
    """Popper World 2 - Intent clarity (NEW from foundational theories)"""
    DOCUMENTED = "Documented"    # Clear docstring/comments explaining intent
    IMPLICIT = "Implicit"        # Intent inferred from naming/patterns
    AMBIGUOUS = "Ambiguous"      # Intent unclear
    CONTRADICTORY = "Contradictory"  # Code behavior contradicts documentation


class Role(str, Enum):
    """DDD tactical roles (33 roles)"""
    QUERY = "Query"
    FINDER = "Finder"
    LOADER = "Loader"
    GETTER = "Getter"
    COMMAND = "Command"
    CREATOR = "Creator"
    MUTATOR = "Mutator"
    DESTROYER = "Destroyer"
    FACTORY = "Factory"
    BUILDER = "Builder"
    REPOSITORY = "Repository"
    STORE = "Store"
    CACHE = "Cache"
    SERVICE = "Service"
    CONTROLLER = "Controller"
    MANAGER = "Manager"
    VALIDATOR = "Validator"
    GUARD = "Guard"
    ASSERTER = "Asserter"
    TRANSFORMER = "Transformer"
    MAPPER = "Mapper"
    SERIALIZER = "Serializer"
    HANDLER = "Handler"
    LISTENER = "Listener"
    SUBSCRIBER = "Subscriber"
    UTILITY = "Utility"
    FORMATTER = "Formatter"
    HELPER = "Helper"
    INTERNAL = "Internal"
    LIFECYCLE = "Lifecycle"
    UNKNOWN = "Unknown"


class EdgeType(str, Enum):
    """Edge types for relationships"""
    CALLS = "calls"
    IMPORTS = "imports"
    USES = "uses"
    REFERENCES = "references"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    MIXES_IN = "mixes_in"
    CONTAINS = "contains"
    IS_PART_OF = "is_part_of"
    RETURNS = "returns"
    RECEIVES = "receives"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    TRIGGERS = "triggers"
    DISPOSES = "disposes"
    DELEGATES_TO = "delegates_to"
    DECORATES = "decorates"
    WRAPS = "wraps"


class EdgeFamily(str, Enum):
    """Edge family groups"""
    STRUCTURAL = "Structural"
    DEPENDENCY = "Dependency"
    INHERITANCE = "Inheritance"
    SEMANTIC = "Semantic"
    TEMPORAL = "Temporal"


class AntimatterLawId(str, Enum):
    """Antimatter law IDs (architectural anti-patterns)"""
    AM001 = "AM001"  # Layer Skip Violation
    AM002 = "AM002"  # Reverse Layer Dependency
    AM003 = "AM003"  # God Class
    AM004 = "AM004"  # Anemic Model
    AM005 = "AM005"  # Bounded Context Violation


class ViolationSeverity(str, Enum):
    """Violation severity levels"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


# ============================================================================
# Core Dataclasses
# ============================================================================

@dataclass
class Dimensions:
    """10-dimensional semantic classification (8 core + 2 contextual)"""
    D1_WHAT: str  # Atom type
    D2_LAYER: Optional[Layer] = None
    D3_ROLE: Optional[Role] = None
    D4_BOUNDARY: Optional[Boundary] = None
    D5_STATE: Optional[State] = None
    D6_EFFECT: Optional[Effect] = None
    D7_LIFECYCLE: Optional[Lifecycle] = None
    D8_TRUST: Optional[float] = None
    # NEW dimensions from foundational theories:
    D9_INTENT: Optional[Intent] = None  # Popper World 2
    D10_LANGUAGE: Optional[str] = None  # Ranganathan Matter facet


@dataclass
class Location:
    """Source code location"""
    file: str
    line_start: int
    line_end: int
    col_start: Optional[int] = None
    col_end: Optional[int] = None


@dataclass
class EdgeLocation:
    """Location where edge is established"""
    file: str
    line: int


@dataclass
class Edge:
    """Relationship between particles"""
    target: str
    type: EdgeType
    family: EdgeFamily
    weight: Optional[float] = None
    confidence: Optional[float] = None
    location: Optional[EdgeLocation] = None


@dataclass
class ParticleMetadata:
    """Additional metadata about the particle"""
    signature: Optional[str] = None
    docstring: Optional[str] = None
    decorators: Optional[List[str]] = None
    parameters: Optional[List[str]] = None
    return_type: Optional[str] = None
    complexity: Optional[float] = None
    lines_of_code: Optional[int] = None
    language: Optional[str] = None


@dataclass
class Particle:
    """A single classified code entity"""
    id: str  # file_path::qualified_name
    atom: str  # From 200-atom periodic table
    dimensions: Dimensions
    level: Level
    plane: Plane
    location: Location
    tau: Optional[str] = None
    name: Optional[str] = None
    qualified_name: Optional[str] = None
    metadata: Optional[ParticleMetadata] = None
    edges_out: List[Edge] = field(default_factory=list)


# ============================================================================
# Metrics and DDD (From Foundational Theories)
# ============================================================================

@dataclass
class ComplexityMetrics:
    """Complexity metrics (Shannon-inspired)"""
    cyclomatic: Optional[float] = None
    cognitive: Optional[float] = None
    halstead_volume: Optional[float] = None
    entropy: Optional[float] = None  # Shannon entropy


@dataclass
class CouplingMetrics:
    """Coupling metrics (Koestler tension dynamics)"""
    afferent: Optional[int] = None   # Incoming dependencies (Ca)
    efferent: Optional[int] = None   # Outgoing dependencies (Ce)
    instability: Optional[float] = None  # Ce / (Ca + Ce)
    tension: Optional[float] = None  # Balance between autonomy and integration


@dataclass
class CohesionMetrics:
    """Cohesion metrics"""
    lcom: Optional[float] = None  # Lack of Cohesion of Methods


@dataclass
class Metrics:
    """Combined metrics (Shannon + Koestler inspired)"""
    complexity: Optional[ComplexityMetrics] = None
    coupling: Optional[CouplingMetrics] = None
    cohesion: Optional[CohesionMetrics] = None


@dataclass
class DDDProperties:
    """Domain-Driven Design tactical properties (Evans)"""
    is_aggregate_root: Optional[bool] = None
    aggregate_id: Optional[str] = None
    bounded_context: Optional[str] = None
    invariants: Optional[List[str]] = None
    domain_events: Optional[List[str]] = None


@dataclass
class Violation:
    """Antimatter law violation (Clean Arch + Dijkstra + Koestler)"""
    law_id: AntimatterLawId
    severity: ViolationSeverity
    message: str
    law_name: Optional[str] = None
    source_theory: Optional[str] = None  # "Clean Architecture", "Dijkstra", "Koestler", "DDD"


@dataclass
class ParticleExtended(Particle):
    """Extended particle with metrics, DDD, and violations from foundational theories"""
    metrics: Optional[Metrics] = None
    ddd: Optional[DDDProperties] = None
    violations: List[Violation] = field(default_factory=list)


# ============================================================================
# Graph Types
# ============================================================================

@dataclass
class Repository:
    """Repository information"""
    name: str
    root: str
    languages: Optional[List[str]] = None
    commit: Optional[str] = None
    branch: Optional[str] = None


@dataclass
class ConfidenceStats:
    """Confidence statistics"""
    mean: float
    median: float
    min: float
    max: float


@dataclass
class GraphStatistics:
    """Aggregate statistics"""
    total_particles: Optional[int] = None
    total_edges: Optional[int] = None
    total_files: Optional[int] = None
    total_lines: Optional[int] = None
    by_level: Optional[Dict[str, int]] = None
    by_layer: Optional[Dict[str, int]] = None
    by_phase: Optional[Dict[str, int]] = None
    by_role: Optional[Dict[str, int]] = None
    by_edge_family: Optional[Dict[str, int]] = None
    by_language: Optional[Dict[str, int]] = None
    confidence: Optional[ConfidenceStats] = None


@dataclass
class Generator:
    """Generator tool info"""
    name: str
    version: str


@dataclass
class Graph:
    """Complete codebase graph"""
    version: str
    generated_at: str  # ISO 8601
    repository: Repository
    particles: List[Particle]
    generator: Optional[Generator] = None
    statistics: Optional[GraphStatistics] = None


# ============================================================================
# Utility Functions
# ============================================================================

def build_tau(d: Dimensions) -> str:
    """Construct τ notation string from dimensions"""
    parts = [
        d.D1_WHAT or "Unknown",
        d.D3_ROLE.value if d.D3_ROLE else "Unknown",
        d.D2_LAYER.value if d.D2_LAYER else "Unknown",
        d.D4_BOUNDARY.value[0] if d.D4_BOUNDARY else "-",
        d.D5_STATE.value[0] if d.D5_STATE else "-",
        d.D6_EFFECT.value[0] if d.D6_EFFECT else "-",
        d.D7_LIFECYCLE.value[0] if d.D7_LIFECYCLE else "-",
        str(int(d.D8_TRUST)) if d.D8_TRUST is not None else "-"
    ]
    return f"τ({':'.join(parts)})"


def parse_particle_id(id: str) -> tuple[str, str]:
    """Parse particle ID into (file, name) components"""
    parts = id.split("::")
    if len(parts) == 2:
        return parts[0], parts[1]
    return id, ""


def is_boundary_crossing(particle: Particle) -> bool:
    """Check if particle crosses I/O boundary"""
    return particle.dimensions.D4_BOUNDARY in (
        Boundary.I_O, 
        Boundary.INPUT, 
        Boundary.OUTPUT
    )


def create_particle_id(file_path: str, qualified_name: str) -> str:
    """Create a standard particle ID"""
    return f"{file_path}::{qualified_name}"


# ============================================================================
# Serialization Helpers
# ============================================================================

def particle_to_dict(p: Particle) -> Dict[str, Any]:
    """Convert Particle to dictionary for JSON serialization"""
    result = {
        "id": p.id,
        "atom": p.atom,
        "dimensions": {
            "D1_WHAT": p.dimensions.D1_WHAT,
        },
        "level": p.level.value,
        "plane": p.plane.value,
        "location": {
            "file": p.location.file,
            "line_start": p.location.line_start,
            "line_end": p.location.line_end,
        }
    }
    
    # Add optional dimension fields
    if p.dimensions.D2_LAYER:
        result["dimensions"]["D2_LAYER"] = p.dimensions.D2_LAYER.value
    if p.dimensions.D3_ROLE:
        result["dimensions"]["D3_ROLE"] = p.dimensions.D3_ROLE.value
    if p.dimensions.D4_BOUNDARY:
        result["dimensions"]["D4_BOUNDARY"] = p.dimensions.D4_BOUNDARY.value
    if p.dimensions.D5_STATE:
        result["dimensions"]["D5_STATE"] = p.dimensions.D5_STATE.value
    if p.dimensions.D6_EFFECT:
        result["dimensions"]["D6_EFFECT"] = p.dimensions.D6_EFFECT.value
    if p.dimensions.D7_LIFECYCLE:
        result["dimensions"]["D7_LIFECYCLE"] = p.dimensions.D7_LIFECYCLE.value
    if p.dimensions.D8_TRUST is not None:
        result["dimensions"]["D8_TRUST"] = p.dimensions.D8_TRUST
    
    # Add tau
    if p.tau:
        result["tau"] = p.tau
    else:
        result["tau"] = build_tau(p.dimensions)
    
    return result
