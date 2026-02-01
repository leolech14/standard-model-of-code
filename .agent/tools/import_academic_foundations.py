#!/usr/bin/env python3
"""
Import Academic Foundations to Neo4j
=====================================

Imports the 9 analyzed academic papers from reference library.
These provide theoretical grounding for SMoC concepts.

Source: wave/archive/references/metadata/*.json
Output: Neo4j nodes (AcademicPaper, Concept, Theory)

Usage:
    python import_academic_foundations.py --neo4j-password <password>
"""

import json
import sys
from pathlib import Path
from neo4j import GraphDatabase

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
METADATA_DIR = REPO_ROOT / "wave" / "archive" / "references" / "metadata"

# Neo4j config
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"


class AcademicFoundationsImporter:
    """Import academic papers to Neo4j."""

    def __init__(self, password):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, password))
        self.stats = {"papers": 0, "concepts": 0, "validations": 0}

    def close(self):
        self.driver.close()

    def import_paper(self, ref_id, metadata):
        """Import single paper with its concepts and validations."""

        with self.driver.session() as session:
            # Create paper node
            session.run("""
                CREATE (p:AcademicPaper {
                    id: $id,
                    title: $title,
                    author: $author,
                    year: $year,
                    summary: $summary,
                    smoc_relevance: $relevance,
                    priority: $priority
                })
            """, {
                "id": ref_id,
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "year": metadata.get("year", ""),
                "summary": metadata.get("summary", ""),
                "relevance": metadata.get("smoc_relevance_summary", ""),
                "priority": metadata.get("priority", 5)
            })

            self.stats["papers"] += 1

            # Create concept nodes from key_smoc_concepts
            for concept_map in metadata.get("key_smoc_concepts", []):
                smoc_concept = concept_map.get("smoc_concept")
                paper_concept = concept_map.get("paper_concept")
                mapping = concept_map.get("mapping", "")

                # Create or merge SMoC concept
                session.run("""
                    MERGE (c:SmocConcept {name: $name})
                    ON CREATE SET c.first_seen = timestamp()
                """, {"name": smoc_concept})

                # Create paper concept
                session.run("""
                    CREATE (pc:PaperConcept {
                        name: $name,
                        paper_id: $paper_id
                    })
                """, {
                    "name": paper_concept,
                    "paper_id": ref_id
                })

                # Link paper to paper concept
                session.run("""
                    MATCH (p:AcademicPaper {id: $paper_id})
                    MATCH (pc:PaperConcept {name: $concept, paper_id: $paper_id})
                    CREATE (p)-[:DEFINES]->(pc)
                """, {
                    "paper_id": ref_id,
                    "concept": paper_concept
                })

                # Link paper concept to SMoC concept (VALIDATES relationship)
                session.run("""
                    MATCH (pc:PaperConcept {name: $paper_concept, paper_id: $paper_id})
                    MATCH (sc:SmocConcept {name: $smoc_concept})
                    CREATE (pc)-[:VALIDATES {
                        mapping: $mapping,
                        strength: $strength
                    }]->(sc)
                """, {
                    "paper_concept": paper_concept,
                    "paper_id": ref_id,
                    "smoc_concept": smoc_concept,
                    "mapping": mapping,
                    "strength": concept_map.get("strength", "medium")
                })

                self.stats["concepts"] += 1
                self.stats["validations"] += 1

            print(f"  ✓ Imported {ref_id}: {metadata.get('title', 'Unknown')[:50]}...")

    def import_all(self):
        """Import all analyzed papers from metadata directory."""

        if not METADATA_DIR.exists():
            print(f"Error: Metadata directory not found: {METADATA_DIR}")
            return

        # Find all *_analysis.json files
        metadata_files = list(METADATA_DIR.glob("*_analysis.json"))
        print(f"Found {len(metadata_files)} analyzed papers")
        print()

        for metadata_file in sorted(metadata_files):
            ref_id = metadata_file.stem.replace("_analysis", "")

            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)

                # Skip if just a stub
                if "[TO BE GENERATED" in metadata.get("summary", ""):
                    continue

                self.import_paper(ref_id, metadata)

            except Exception as e:
                print(f"  ✗ Error importing {ref_id}: {e}")

        print()
        print("=" * 60)
        print("IMPORT COMPLETE")
        print("=" * 60)
        print(f"Papers imported: {self.stats['papers']}")
        print(f"Concepts extracted: {self.stats['concepts']}")
        print(f"Validations created: {self.stats['validations']}")
        print("=" * 60)

    def test_query(self):
        """Test query to verify import worked."""
        print("\nTesting query: What validates Purpose Field?")

        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:SmocConcept {name: 'purpose_field_dynamics'})
                MATCH (pc:PaperConcept)-[:VALIDATES]->(c)
                MATCH (p:AcademicPaper)-[:DEFINES]->(pc)
                RETURN p.title as paper, pc.name as concept
            """)

            for record in result:
                print(f"  {record['paper']} validates via {record['concept']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Import Academic Foundations to Neo4j")
    parser.add_argument("--neo4j-password", required=True, help="Neo4j password")
    parser.add_argument("--test", action="store_true", help="Run test query after import")

    args = parser.parse_args()

    importer = AcademicFoundationsImporter(args.neo4j_password)

    try:
        importer.import_all()

        if args.test:
            importer.test_query()

    finally:
        importer.close()


if __name__ == "__main__":
    main()
