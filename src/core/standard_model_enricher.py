"""
Standard Model Enricher
Applies the full Standard Model theory to particles:
- 58 Canonical Types from canonical_types.json
- RPBL Scores (Responsibility, Purity, Boundary, Lifecycle)
- Atom Mapping (DAT.BYT.A, LOG.FNC.M, etc.)
- Type Alias Resolution (Helper→Utility, Schema→DTO)
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class StandardModelEnricher:
    """Enriches particles with full Standard Model theory."""
    
    def __init__(self):
        self.canonical_types = {}       # type_id -> {description, rpbl, layer, aliases}
        self.type_aliases = {}          # alias -> canonical_type
        self.rpbl_scores = {}           # type_id -> {R, P, B, L}
        self.type_to_layer = {}         # type_id -> layer
        self.atoms = {}                 # atom_id -> {name, layer, description}
        self.atom_mappings = {}         # language -> {symbol_kind -> atom_id}
        
        self._load_canonical_types()
        self._load_atoms()
    
    def _load_canonical_types(self):
        """Load all 58 canonical types from canonical_types.json"""
        patterns_dir = Path(__file__).parent.parent / "patterns"
        types_file = patterns_dir / "canonical_types.json"
        
        if not types_file.exists():
            print(f"⚠️  canonical_types.json not found at {types_file}")
            return
        
        with open(types_file) as f:
            data = json.load(f)
        
        # Parse layers and types
        for layer_name, layer_data in data.get('layers', {}).items():
            for type_def in layer_data.get('types', []):
                type_id = type_def.get('id')
                if not type_id:
                    continue
                
                self.canonical_types[type_id] = {
                    'description': type_def.get('description', ''),
                    'layer': layer_name,
                    'aliases': type_def.get('aliases', []),
                    'rpbl': type_def.get('rpbl', {})
                }
                
                # Store RPBL scores
                self.rpbl_scores[type_id] = type_def.get('rpbl', {})
                
                # Store layer mapping
                self.type_to_layer[type_id] = layer_name
                
                # Register aliases
                for alias in type_def.get('aliases', []):
                    self.type_aliases[alias] = type_id
                    self.type_aliases[alias.lower()] = type_id
                
                # Also register lowercase
                self.type_aliases[type_id.lower()] = type_id
        
        print(f"   ✓ Loaded {len(self.canonical_types)} canonical types")
    
    def _load_atoms(self):
        """Load atoms from atoms.json"""
        patterns_dir = Path(__file__).parent.parent / "patterns"
        atoms_file = patterns_dir / "atoms.json"
        
        if not atoms_file.exists():
            print(f"⚠️  atoms.json not found at {atoms_file}")
            return
        
        with open(atoms_file) as f:
            data = json.load(f)
        
        self.atoms = data.get('atoms', {})
        self.atom_mappings = data.get('mappings', {})
        print(f"   ✓ Loaded {len(self.atoms)} atoms")
    
    def resolve_canonical_type(self, type_name: str) -> str:
        """Resolve a type name to its canonical form."""
        if not type_name:
            return "Unknown"
        
        # Direct match
        if type_name in self.canonical_types:
            return type_name
        
        # Alias match
        if type_name in self.type_aliases:
            return self.type_aliases[type_name]
        
        # Case-insensitive match
        lower = type_name.lower()
        if lower in self.type_aliases:
            return self.type_aliases[lower]
        
        # Suffix matching for common patterns
        suffix_map = {
            'helper': 'Utility',
            'utils': 'Utility',
            'util': 'Utility',
            'schema': 'DTO',
            'request': 'DTO',
            'response': 'DTO',
            'model': 'Entity',
            'aggregate': 'Entity',
            'vo': 'ValueObject',
            'config': 'Configuration',
            'settings': 'Configuration',
            'handler': 'CommandHandler',
            'spec': 'Specification',
            'rule': 'Specification',
        }
        
        for suffix, canonical in suffix_map.items():
            if lower.endswith(suffix) or lower == suffix:
                return canonical
        
        return type_name  # Return as-is if no match
    
    def get_rpbl_scores(self, type_name: str) -> Dict[str, int]:
        """Get RPBL scores for a type."""
        canonical = self.resolve_canonical_type(type_name)
        return self.rpbl_scores.get(canonical, {
            'responsibility': 5,
            'purity': 5,
            'boundary': 5,
            'lifecycle': 5
        })
    
    def get_layer(self, type_name: str) -> Optional[str]:
        """Get the architectural layer for a type."""
        canonical = self.resolve_canonical_type(type_name)
        return self.type_to_layer.get(canonical)
    
    def get_atom(self, symbol_kind: str, language: str = 'python') -> str:
        """Get the Atom ID for a symbol kind."""
        lang_map = self.atom_mappings.get(language, self.atom_mappings.get('python', {}))
        
        # Direct mapping
        atom_id = lang_map.get(symbol_kind)
        if atom_id:
            return atom_id
        
        # Fallback mappings
        fallbacks = {
            'class': 'ORG.AGG.M',
            'function': 'LOG.FNC.M',
            'method': 'LOG.FNC.M',
            'module': 'ORG.MOD.O',
            'variable': 'DAT.VAR.A',
            'constant': 'DAT.PRM.A',
            'interface': 'ORG.AGG.M',
            'enum': 'DAT.PRM.A',
        }
        return fallbacks.get(symbol_kind, 'ORG.AGG.M')
    
    def enrich_particle(self, particle: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single particle with full Standard Model data."""
        
        # Resolve canonical type
        current_type = particle.get('type') or particle.get('role') or 'Unknown'
        canonical_type = self.resolve_canonical_type(current_type)
        
        # Update type/role to canonical
        particle['type'] = canonical_type
        particle['role'] = canonical_type
        
        # Add RPBL scores
        rpbl = self.get_rpbl_scores(canonical_type)
        particle['rpbl'] = rpbl
        
        # Add to dimensions if dimensions dict exists
        if 'dimensions' in particle:
            particle['dimensions']['responsibility'] = rpbl.get('responsibility', 5)
            particle['dimensions']['purity'] = rpbl.get('purity', 5)
            particle['dimensions']['boundary'] = rpbl.get('boundary', 5)
            particle['dimensions']['lifecycle'] = rpbl.get('lifecycle', 5)
        
        # Add layer from type definition
        layer = self.get_layer(canonical_type)
        if layer and not particle.get('layer'):
            particle['layer'] = layer
        
        # Add Atom mapping
        symbol_kind = particle.get('symbol_kind') or particle.get('kind') or 'unknown'
        particle['atom'] = self.get_atom(symbol_kind)
        
        return particle
    
    def enrich_all(self, particles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich all particles with Standard Model data."""
        for particle in particles:
            self.enrich_particle(particle)
        return particles


# Singleton instance
_enricher = None

def get_standard_model_enricher() -> StandardModelEnricher:
    """Get or create the singleton enricher instance."""
    global _enricher
    if _enricher is None:
        _enricher = StandardModelEnricher()
    return _enricher


def enrich_with_standard_model(particles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to enrich particles with Standard Model."""
    enricher = get_standard_model_enricher()
    return enricher.enrich_all(particles)


if __name__ == "__main__":
    # Test the enricher
    enricher = StandardModelEnricher()
    
    test_particles = [
        {'name': 'UserRepository', 'type': 'Internal', 'symbol_kind': 'class'},
        {'name': 'CreateUserCommand', 'type': 'Command', 'symbol_kind': 'class'},
        {'name': 'helper_function', 'type': 'Utility', 'symbol_kind': 'function'},
        {'name': 'UserSchema', 'type': 'DTO', 'symbol_kind': 'class'},
    ]
    
    print("\nTest enrichment:")
    for p in test_particles:
        enricher.enrich_particle(p)
        print(f"  {p['name']}: type={p['type']}, rpbl={p.get('rpbl')}, atom={p.get('atom')}")
