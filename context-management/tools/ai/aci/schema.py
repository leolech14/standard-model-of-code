import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class RefineryNode:
    """Atomic chunk with full metadata and logistics waybill."""
    content: str                    # The chunk text
    source_file: str                # Origin file path
    chunk_id: str                   # Unique ID (SHA256-based)
    chunk_type: str                 # Type: function, class, section, config_block, etc.
    relevance_score: float = 0.0    # 0.0-1.0 relevance score
    start_line: int = 0             # Line number in source (if applicable)
    end_line: int = 0               # End line number
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
    created_at: float = field(default_factory=time.time)
    embedding: List[float] = field(default_factory=list)  # Vector embedding (384-dim for MiniLM)

    # Fundamental Logistics ("The Mail")
    waybill: Dict[str, Any] = field(default_factory=dict) # Tracking info {parcel_id, parent_id, route}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return asdict(self)

    @property
    def token_estimate(self) -> int:
        """Rough token count estimate (chars / 4)."""
        return len(self.content) // 4

    def __repr__(self) -> str:
        return f"RefineryNode({self.chunk_type}:{self.chunk_id[:8]}... {self.token_estimate}tok)"
