"""
Context Refinery Module
========================
RAG + Long Context hybrid system that maps, refines, atomizes,
and recompiles context on demand.

Components:
  - corpus_inventory: Scan and categorize all files
  - boundary_mapper: Map analysis_sets.yaml to boundary nodes
  - delta_detector: Detect changes since last run
  - atom_generator: Create RefineryNode entries
  - state_synthesizer: Produce global state/live.yaml

Philosophy: "We apply Collider logic to context: break the repository into
semantic units and reaggregate them as distilled matter for reasoning."
"""

__version__ = "0.1.0"
