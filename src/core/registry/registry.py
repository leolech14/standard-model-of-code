"""
Atom Registry
=============

The canonical registry of all known atoms.
This grows over time as we discover new patterns.
"""

from typing import Dict, Optional
from datetime import datetime

from .models import AtomDefinition
from .definitions import ALL_DEFINITIONS


class AtomRegistry:
    """
    The canonical registry of all known atoms.

    This grows over time as we discover new patterns.
    """

    def __init__(self):
        self.atoms: Dict[int, AtomDefinition] = {}
        self.ast_type_map: Dict[str, int] = {}  # node_type -> atom_id
        self.next_id: int = 97  # Original 96 + new discoveries
        self._init_from_definitions()

    def _init_from_definitions(self):
        """Initialize registry from definitions data."""
        for defn in ALL_DEFINITIONS:
            id_, name, ast_types, continent, fundamental, level, desc, rule = defn
            self._add(id_, name, ast_types, continent, fundamental, level, desc, rule)

    def _add(
        self,
        id: int,
        name: str,
        ast_types: list,
        continent: str,
        fundamental: str,
        level: str,
        description: str,
        detection_rule: str
    ):
        """Add an atom to the registry."""
        atom = AtomDefinition(
            id=id,
            name=name,
            ast_types=ast_types,
            continent=continent,
            fundamental=fundamental,
            level=level,
            description=description,
            detection_rule=detection_rule,
            source="original"
        )
        self.atoms[id] = atom

        # Map AST types to this atom
        for ast_type in ast_types:
            self.ast_type_map[ast_type] = id

    def add_discovery(
        self,
        name: str,
        ast_types: list,
        continent: str,
        fundamental: str,
        level: str,
        description: str,
        detection_rule: str,
        source_repo: str
    ) -> int:
        """Add a newly discovered atom to the registry."""
        atom = AtomDefinition(
            id=self.next_id,
            name=name,
            ast_types=ast_types,
            continent=continent,
            fundamental=fundamental,
            level=level,
            description=description,
            detection_rule=detection_rule,
            source=source_repo,
            discovered_at=datetime.now().isoformat()
        )
        self.atoms[self.next_id] = atom

        for ast_type in ast_types:
            self.ast_type_map[ast_type] = self.next_id

        self.next_id += 1
        return atom.id

    def get_by_id(self, id: int) -> Optional[AtomDefinition]:
        """Get atom definition by ID."""
        return self.atoms.get(id)

    def get_by_name(self, name: str) -> Optional[AtomDefinition]:
        """Get atom definition by name."""
        for atom in self.atoms.values():
            if atom.name == name:
                return atom
        return None

    def get_by_ast_type(self, ast_type: str) -> Optional[AtomDefinition]:
        """Get atom definition by AST node type."""
        if ast_type in self.ast_type_map:
            return self.atoms[self.ast_type_map[ast_type]]
        return None

    def get_all(self) -> list:
        """Get all atom definitions."""
        return list(self.atoms.values())

    def get_by_continent(self, continent: str) -> list:
        """Get all atoms in a continent."""
        return [a for a in self.atoms.values() if a.continent == continent]

    def get_by_level(self, level: str) -> list:
        """Get all atoms at a level (atom, molecule, organelle)."""
        return [a for a in self.atoms.values() if a.level == level]
