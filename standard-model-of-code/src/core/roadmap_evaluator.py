
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Capability:
    name: str
    description: str
    patterns: List[str]
    min_confidence: float = 0.5
    status: str = "MISSING"  # MISSING, PRESENT, PARTIAL
    evidence: List[str] = field(default_factory=list)

@dataclass
class Roadmap:
    name: str
    description: str
    archetype: str
    required: List[Capability]
    optional: List[Capability]
    forbidden: List[Capability]
    maturity_stages: Dict[str, List[str]]

class RoadmapEvaluator:
    """Evaluates a codebase against a defined architectural roadmap."""

    def __init__(self, roadmap_path: str):
        self.roadmap = self._load_roadmap(roadmap_path)

    def _load_roadmap(self, path: str) -> Roadmap:
        with open(path, 'r') as f:
            data = json.load(f)
        
        return Roadmap(
            name=data['name'],
            description=data['description'],
            archetype=data['archetype'],
            required=[self._parse_cap(c) for c in data['capabilities']['required']],
            optional=[self._parse_cap(c) for c in data['capabilities'].get('optional', [])],
            forbidden=[self._parse_cap(c) for c in data['capabilities'].get('forbidden', [])],
            maturity_stages=data.get('maturity_stages', {})
        )

    def _parse_cap(self, data: Dict) -> Capability:
        return Capability(
            name=data['name'],
            description=data['description'],
            patterns=data['patterns'],
            min_confidence=data.get('min_confidence', 0.5)
        )

    def evaluate(self, file_paths: List[str], file_contents: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Evaluate the codebase against the roadmap.
        file_paths: List of absolute or relative file paths in the project.
        file_contents: Optional dict of {filepath: content} (for deep scan, unused for v1)
        """
        # 1. Evaluate Required Capabilities
        for cap in self.roadmap.required:
            self._check_capability(cap, file_paths)

        # 2. Evaluate Optional Capabilities
        for cap in self.roadmap.optional:
            self._check_capability(cap, file_paths)

        # 3. Evaluate Forbidden Capabilities
        for cap in self.roadmap.forbidden:
            self._check_capability(cap, file_paths, is_forbidden=True)
            
        return self._generate_report()

    def _check_capability(self, cap: Capability, file_paths: List[str], is_forbidden: bool = False):
        matches = []
        for pattern in cap.patterns:
            # Simple regex search in file path
            # In v2, this should search file CONTENT (e.g., imports, class names)
            regex = re.compile(pattern, re.IGNORECASE)
            for path in file_paths:
                if regex.search(path):
                    matches.append(path)
        
        if matches:
            cap.status = "PRESENT" if not is_forbidden else "VIOLATION"
            cap.evidence = matches[:5] # Limit evidence
        else:
            cap.status = "MISSING" if not is_forbidden else "CLEAN"

    def _generate_report(self) -> Dict[str, Any]:
        
        # Calculate Readiness
        total_req = len(self.roadmap.required)
        met_req = len([c for c in self.roadmap.required if c.status == "PRESENT"])
        readiness_score = (met_req / total_req * 100) if total_req > 0 else 100

        # Determine Maturity Stage
        current_stage = "v0_inception"
        for stage_name, reqs in self.roadmap.maturity_stages.items():
            # Check if all reqs for this stage are met
            if all(self._get_cap_status(r) == "PRESENT" for r in reqs):
                current_stage = stage_name
            else:
                break # Cannot reach higher stages if lower is missing

        return {
            "roadmap_name": self.roadmap.name,
            "readiness_score": readiness_score,
            "maturity_stage": current_stage,
            "gaps": [
                {"name": c.name, "desc": c.description} 
                for c in self.roadmap.required if c.status == "MISSING"
            ],
            "achieved": [
                {"name": c.name, "evidence": len(c.evidence)}
                for c in self.roadmap.required if c.status == "PRESENT"
            ],
             "violations": [
                {"name": c.name, "evidence": c.evidence}
                for c in self.roadmap.forbidden if c.status == "VIOLATION"
            ]
        }

    def _get_cap_status(self, cap_name: str) -> str:
        for c in self.roadmap.required + self.roadmap.optional:
            if c.name == cap_name:
                return c.status
        return "UNKNOWN"
