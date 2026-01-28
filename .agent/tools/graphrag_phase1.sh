#!/bin/bash
# GraphRAG Phase 1 - Automated Execution
# Run all pilot tasks in sequence

set -e  # Exit on error

VENV=".tools_venv/bin/python"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-elements2026}"

echo "════════════════════════════════════════════════════════"
echo "GRAPHRAG PHASE 1 - PILOT EXECUTION"
echo "════════════════════════════════════════════════════════"
echo ""

# Task 1.3: Import Academic Foundations
echo "[1/5] Importing Academic Foundations (9 papers)..."
$VENV .agent/tools/import_academic_foundations.py \
    --neo4j-password "$NEO4J_PASSWORD" \
    --test || echo "⚠️ Import failed - check password"

echo ""

# Task 1.4: Import Collider Graph
echo "[2/5] Importing Collider Graph (2,540 nodes)..."
# Update password in script first
sed -i '' "s/NEO4J_PASSWORD = .*/NEO4J_PASSWORD = \"$NEO4J_PASSWORD\"/" .agent/tools/collider_to_neo4j.py

latest_collider=$(ls -t .collider-full/output_llm*.json | head -1)
$VENV .agent/tools/collider_to_neo4j.py "$latest_collider" || echo "⚠️ Import failed"

echo ""

# Task 1.5: Verify Import
echo "[3/5] Verifying Data..."
cypher-shell -u neo4j -p "$NEO4J_PASSWORD" << 'CYPHER'
MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC;
CYPHER

echo ""

# Task 1.6: Install Dependencies
echo "[4/5] Installing Dependencies..."
$VENV -m pip install --quiet sentence-transformers networkx neo4j-graphrag

echo ""

# Task 1.7: Test Query
echo "[5/5] Testing GraphRAG Query..."
cypher-shell -u neo4j -p "$NEO4J_PASSWORD" << 'CYPHER'
// Test: What validates Purpose Field?
MATCH (c:SmocConcept)
WHERE c.name CONTAINS 'purpose'
MATCH (pc)-[:VALIDATES]->(c)
MATCH (p)-[:DEFINES]->(pc)
RETURN p.title as paper, p.author as author, c.name as concept
LIMIT 5;
CYPHER

echo ""
echo "════════════════════════════════════════════════════════"
echo "PHASE 1 COMPLETE ✓"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Next: Validate accuracy (Task 2.7) or proceed to full scale"
echo "Open Neo4j Browser: http://localhost:7474"
