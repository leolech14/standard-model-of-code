# Research: Specific GraphRAG implementation question:

OUR SETUP:
- Neo4j local: 5,284 nodes (code + chunks + p...

> **Date:** 2026-01-27 19:13:47
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:82fa7a466227b338a5879120b38ddfee4b85284f6df233b174fcd0383b688370`
> **Raw JSON:** `raw/20260127_191347_specific_graphrag_implementation_question___our_se.json`

---

## Query

Specific GraphRAG implementation question:

OUR SETUP:
- Neo4j local: 5,284 nodes (code + chunks + papers)
- Embeddings: all-MiniLM-L6-v2 (384-dim) available but not in Neo4j yet
- Query interface: Basic Cypher pattern matching
- ACI tiers: INSTANT, RAG, LONG_CONTEXT, PERPLEXITY (4 existing)

WANT TO ADD:
1. Vector index to Neo4j for hybrid retrieval
2. Leiden community detection (not Louvain)
3. GraphRAG as ACI Tier 5
4. Query-driven subgraph extraction (2-4 hops)
5. Incremental updates from delta detection

SPECIFIC TECHNICAL QUESTIONS:

1. Neo4j vector index setup:
   - Command to create vector index on node property?
   - How to store 384-dim embeddings in Neo4j?
   - Query syntax for hybrid (Cypher + vector similarity)?
   - Performance: Can Neo4j handle 5K nodes with 384-dim vectors?

2. Leiden vs Louvain in NetworkX/Neo4j:
   - Which Python library has best Leiden implementation?
   - Can Neo4j GDS run Leiden (or only Louvain)?
   - Parameters to tune for 5K node graph?
   - How to use communities in GraphRAG queries?

3. Query-driven subgraph extraction:
   - Algorithm: Start from seed entities → expand N hops?
   - How to limit explosion (100 neighbors per node)?
   - Shortest-path-only pruning implementation?
   - Convert subgraph → LLM-readable format?

4. Integration patterns:
   - How to add GraphRAG tier to existing RAG system?
   - When to route to graph vs vector-only RAG?
   - Fallback strategy if graph query returns nothing?

Provide: Code examples (Python + Cypher), specific commands, library versions, parameter tuning guidance, integration architecture for adding GraphRAG to existing RAG tiers.

---

## Response

# Implementing GraphRAG with Neo4j: Vector Indexing, Leiden Community Detection, and Hybrid Retrieval Architecture

This comprehensive technical report provides a complete implementation guide for integrating Graph-based Retrieval-Augmented Generation (GraphRAG) into an existing Neo4j knowledge graph with vector search capabilities, Leiden community detection, and sophisticated query routing. Based on your existing infrastructure of 5,284 nodes with 384-dimensional embeddings and multiple ACI tiers, this report details the architectural decisions, code implementations, parameter tuning strategies, and integration patterns necessary for production deployment of GraphRAG as a fifth ACI tier alongside your existing INSTANT, RAG, LONG_CONTEXT, and PERPLEXITY tiers.

## Understanding the GraphRAG Architecture and Your Integration Requirements

GraphRAG represents a significant evolution beyond traditional vector-based retrieval-augmented generation systems[19][43]. While standard RAG systems rely primarily on semantic similarity search through vector embeddings to retrieve contextually relevant documents, GraphRAG integrates structured knowledge graphs with language models to enable more sophisticated reasoning over interconnected entities and relationships[28][31]. The distinction is particularly important for your use case: vector-only RAG struggles with multi-hop reasoning queries that require understanding how entities connect through multiple intermediate steps, whereas GraphRAG excels precisely in scenarios requiring relational reasoning and complex entity traversal[16][28].

Your current system architecture, with five ACI (Analysis Capability Interface) tiers, positions you well to implement GraphRAG as an additional tier that operates alongside rather than replacing existing capabilities. The INSTANT tier likely handles simple keyword matching, RAG provides vector-based semantic search, LONG_CONTEXT manages extended document contexts, PERPLEXITY handles uncertainty quantification, and the new GraphRAG tier would handle graph-structured reasoning requiring entity relationships and multi-hop traversal[10][61]. This multi-tier approach enables intelligent routing where query classification determines which tier best serves each query type.

Your existing 384-dimensional embeddings from the all-MiniLM-L6-v2 model create an important compatibility consideration. This model produces significantly smaller embeddings than OpenAI's text-embedding-3-large (1536 dimensions) or GPT-3's text-embedding-ada-002 (also 1536 dimensions), which affects both storage efficiency and retrieval performance[1]. The smaller dimensionality reduces memory requirements and query latency, though it may have different precision characteristics for similarity matching compared to larger embedding models. The 5,284 nodes with 384-dimensional embeddings represent a relatively modest dataset by enterprise standards—well within Neo4j's capabilities for both vector and graph operations[4][35].

## Neo4j Vector Index Implementation and Configuration

Creating a vector index in Neo4j requires careful consideration of several dimensions: the CREATE VECTOR INDEX syntax, dimension specification, similarity function selection, and query patterns for hybrid retrieval. The modern Neo4j vector indexing system (version 5.3+) provides native support for approximate nearest neighbor (ANN) search with multiple similarity functions optimized for different data types and retrieval patterns[50].

The fundamental command to create your vector index on node embeddings follows this structure:

```cypher
CREATE VECTOR INDEX questions IF NOT EXISTS
FOR (n:Chunk)
ON n.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}}
```

This command creates an index named "questions" on the Chunk node label's embedding property, specifying 384 dimensions to match your all-MiniLM-L6-v2 embeddings and using cosine similarity as the matching function[50]. The cosine similarity metric typically performs best for text embeddings because it measures angular distance between vectors in high-dimensional space, making it robust to vector magnitude variations. For your 5,284-node dataset with 384-dimensional embeddings, this index will have minimal memory overhead—approximately 7-10 MB depending on Neo4j's internal indexing structures.

However, your query noted that embeddings are "available but not in Neo4j yet," indicating a data ingestion phase precedes index creation. The process requires three sequential steps: embedding generation, node property storage, and index creation. Using Python with the Neo4j driver and sentence-transformers library:

```python
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

model = SentenceTransformer('all-MiniLM-L6-v2')
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def embed_and_store_chunks(driver, batch_size=100):
    """
    Retrieve chunks from Neo4j, generate embeddings,
    and store back in the database
    """
    with driver.session() as session:
        # First, count total chunks to process
        count_result = session.run(
            "MATCH (c:Chunk) RETURN count(c) as total"
        )
        total = count_result.single()["total"]

        # Process in batches to avoid memory overload
        for offset in range(0, total, batch_size):
            result = session.run(
                """
                MATCH (c:Chunk)
                WHERE c.embedding IS NULL
                RETURN c.id, c.text
                SKIP $offset LIMIT $batch_size
                """,
                offset=offset,
                batch_size=batch_size
            )

            chunks = result.data()
            if not chunks:
                break

            # Generate embeddings for this batch
            texts = [c['text'] for c in chunks]
            embeddings = model.encode(texts, convert_to_tensor=False)

            # Store embeddings back in Neo4j
            for chunk, embedding in zip(chunks, embeddings):
                session.run(
                    """
                    MATCH (c:Chunk {id: $chunk_id})
                    SET c.embedding = $embedding
                    """,
                    chunk_id=chunk['id'],
                    embedding=embedding.tolist()
                )

            print(f"Processed {offset + len(chunks)} of {total} chunks")

# Execute embedding pipeline
embed_and_store_chunks(driver)
driver.close()
```

After embedding ingestion, create the vector index and verify its status[50]:

```cypher
CREATE VECTOR INDEX chunk_embedding IF NOT EXISTS
FOR (c:Chunk)
ON c.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}}

// Monitor index population
SHOW INDEXES WHERE type = "VECTOR"
```

The SHOW INDEXES query returns critical metadata including populationPercent (the proportion of nodes indexed) and state (ONLINE when ready for queries). With 5,284 nodes and 384-dimensional vectors, index population typically completes within seconds to a few minutes depending on your Neo4j hardware configuration[50].

For your hybrid retrieval requirement combining vector similarity with graph structure, Neo4j provides the db.index.vector.queryNodes procedure that executes approximate nearest neighbor search:

```cypher
// Hybrid query: Vector similarity + graph traversal
CALL db.index.vector.queryNodes('chunk_embedding', $k, $query_embedding)
YIELD node, score
WHERE score > $similarity_threshold

// Optional: Traverse to related entities
OPTIONAL MATCH (node)<-[:MENTIONS]-(e:Entity)
OPTIONAL MATCH (e)-[:RELATED_TO]-(related:Entity)

// Apply property-based filtering
WHERE node.source IN $allowed_sources

// Return rich context for LLM
RETURN
  node.text AS text,
  score AS similarity_score,
  collect(DISTINCT e.name) AS mentioned_entities,
  collect(DISTINCT related.name) AS related_entities
ORDER BY score DESC
LIMIT $k
```

This query pattern forms the foundation of your hybrid retrieval strategy[15][39]. The initial vector search retrieves semantically similar chunks, then optional graph traversal enriches results with entity relationships and context information. The WHERE clause enables property-based filtering (source documents, access control, content types) without requiring post-retrieval pruning that could eliminate relevant results from consideration[42].

Performance optimization for your 5,284-node dataset requires attention to Neo4j's memory configuration and query planning. The vector index itself consumes relatively modest memory—approximately 8-12 MB for 5,284 384-dimensional vectors—but optimal retrieval performance requires sufficient buffer pool allocation. For desktop/workstation deployments with high-performance hardware, Neo4j's recommended memory configuration allocates 25-50% of available RAM to the database[35][38]. A typical configuration on a machine with 32GB RAM would allocate 8-16GB to Neo4j:

```
# neo4j.conf configuration
dbms.memory.heap.initial_size=8g
dbms.memory.heap.max_size=16g
dbms.memory.pagecache.size=4g
```

These settings establish adequate memory for your dataset scale while leaving room for OS operations and other processes.

## Leiden Community Detection: Library Selection and Implementation

Your requirement to use Leiden rather than Louvain community detection reflects an important algorithmic choice. The Leiden algorithm represents an improvement over its predecessor by guaranteeing well-connected communities and achieving faster convergence to optimal partitions[36][60]. Unlike Louvain, which can produce arbitrarily badly connected communities, Leiden ensures that all subsets of communities remain locally optimally assigned, providing more stable and interpretable community structure for GraphRAG's hierarchical reasoning[3][36].

Three primary options exist for running Leiden on your graph: NetworkX with the leidenalg backend, Neo4j Graph Data Science (GDS) library, and standalone leidenalg Python package[3][7][33][36]. Each presents different trade-offs regarding ease of use, performance, and integration with Neo4j.

The leidenalg Python package provides the most flexible and widely-used implementation, built as C++ bindings wrapped for Python[33][36]. Installation requires careful attention to dependencies:

```bash
# Install leidenalg with its igraph dependency
pip install leidenalg igraph

# Verify installation
python -c "import leidenalg; import igraph; print('Leiden available')"
```

The leidenalg package (currently version 0.10.2+) implements six different partition quality functions: modularity (default), Reichardt and Bornholdt's model, Constant Potts Model (CPM), Significance, and Surprise[33][36]. For GraphRAG hierarchical community detection, modularity provides the best default behavior—it balances community compactness against global graph structure, producing communities at natural granularity levels suited for hierarchical traversal[36].

Converting your Neo4j graph to igraph format for Leiden processing requires extracting nodes and relationships, then converting to an igraph Graph object[36][47]:

```python
import igraph as ig
import leidenalg as la
from neo4j import GraphDatabase

def extract_graph_and_detect_communities(driver, resolution=1.0, seed=42):
    """
    Extract graph from Neo4j, run Leiden community detection,
    and store results back in database
    """
    with driver.session() as session:
        # Extract nodes with their properties
        nodes_result = session.run(
            """
            MATCH (n:Entity)
            RETURN n.id AS id, n.name AS name
            ORDER BY n.id
            """
        )
        nodes = {node['id']: i for i, node in enumerate(nodes_result)}

        # Extract relationships
        rels_result = session.run(
            """
            MATCH (a:Entity)-[r:RELATED_TO]-(b:Entity)
            RETURN a.id AS source, b.id AS target
            """
        )
        relationships = []
        for rel in rels_result:
            src_idx = nodes.get(rel['source'])
            tgt_idx = nodes.get(rel['target'])
            if src_idx is not None and tgt_idx is not None:
                relationships.append((src_idx, tgt_idx))

    # Create igraph from extracted data
    g = ig.Graph()
    g.add_vertices(len(nodes))
    g.add_edges(relationships)

    # Add node attributes
    node_id_map = {v: k for k, v in nodes.items()}
    g.vs["neo4j_id"] = [node_id_map[i] for i in range(len(nodes))]

    # Run Leiden algorithm with specified parameters
    # Use ModularityVertexPartition for quality function
    partition = la.find_partition(
        g,
        la.ModularityVertexPartition,
        seed=seed,
        n_iterations=2,  # Default: 2 iterations
        resolution_parameter=resolution  # Tune for community granularity
    )

    # Extract community assignments
    community_assignments = {
        node_id_map[idx]: partition.membership[idx]
        for idx in range(len(nodes))
    }

    # Store results back in Neo4j
    with driver.session() as session:
        # Create hierarchical community structure
        for entity_id, community_id in community_assignments.items():
            session.run(
                """
                MATCH (e:Entity {id: $entity_id})
                SET e.community_id = $community_id,
                    e.leiden_iteration = $iteration
                """,
                entity_id=entity_id,
                community_id=community_id,
                iteration=1
            )

        # Create Community nodes and relationships
        session.run(
            """
            MATCH (e:Entity)
            WHERE e.community_id IS NOT NULL
            WITH e.community_id AS comm_id, collect(e) AS entities
            MERGE (c:Community {id: $community_id})
            SET c.size = size(entities),
                c.leiden_level = 1
            WITH c, entities
            UNWIND entities AS entity
            MERGE (entity)-[:MEMBER_OF]->(c)
            """,
            community_id="community"
        )

    return len(partition), partition.modularity

# Run community detection
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
num_communities, modularity = extract_graph_and_detect_communities(
    driver,
    resolution=1.0,
    seed=42
)
print(f"Detected {num_communities} communities with modularity {modularity:.4f}")
driver.close()
```

The Leiden algorithm's parameters merit careful tuning for your 5,284-node graph[11][57]. The resolution parameter controls the granularity of detected communities—values less than 1.0 favor larger communities, while values greater than 1.0 favor smaller communities[3][11]. For GraphRAG hierarchical reasoning, a resolution around 0.5-1.0 typically produces 10-50 communities from a 5,000-node graph, providing useful intermediate abstraction levels without excessive fragmentation[10]. The seed parameter ensures deterministic results across multiple runs, critical for consistent entity resolution and production reproducibility[57].

Regarding Neo4j GDS (Graph Data Science) library capabilities: Neo4j GDS includes Leiden community detection, but requires a commercial license for unlocking concurrency beyond 4 threads[4]. For your dataset size, even the community edition's 4-thread limitation completes in reasonable time, but the Python leidenalg package provides more flexibility, better parameter control, and no licensing constraints[4][33].

## Hierarchical Community Detection for GraphRAG Indexing

GraphRAG's power derives from creating hierarchical communities—detecting communities at multiple levels of abstraction[10][13][58]. The most effective approach applies Leiden detection iteratively: first detecting top-level communities, then recursively detecting communities within each community to create a hierarchy. This enables the global search queries that GraphRAG uses for dataset-wide reasoning[10][58].

```python
def create_hierarchical_communities(driver, max_levels=3):
    """
    Create multi-level hierarchical community structure
    for GraphRAG global search
    """
    current_level = 0
    max_level_reached = False

    with driver.session() as session:
        while current_level < max_levels and not max_level_reached:
            if current_level == 0:
                # Initial level: detect communities from all entities
                query = """
                MATCH (e:Entity)
                RETURN e.id AS id, e.name AS name
                """
            else:
                # Subsequent levels: communities within each parent community
                query = """
                MATCH (parent:Community {level: $level})
                MATCH (e:Entity)-[:MEMBER_OF]->(:Community)-[:SUB_COMMUNITY_OF*]->
                      (:Community {level: $level})
                RETURN e.id AS id, e.name AS name
                """

            # Extract nodes for this level
            nodes_result = session.run(query, level=current_level)
            nodes = {node['id']: i for i, node in enumerate(nodes_result)}

            if len(nodes) < 3:  # Stop if communities too small
                max_level_reached = True
                break

            # Extract relationships within this community set
            edges_result = session.run(
                """
                MATCH (a:Entity)-[r:RELATED_TO]-(b:Entity)
                WHERE a.id IN $node_ids AND b.id IN $node_ids
                RETURN a.id AS source, b.id AS target
                """,
                node_ids=list(nodes.keys())
            )

            relationships = []
            for edge in edges_result:
                src = nodes.get(edge['source'])
                tgt = nodes.get(edge['target'])
                if src is not None and tgt is not None:
                    relationships.append((src, tgt))

            if not relationships:  # Stop if no edges at this level
                max_level_reached = True
                break

            # Run Leiden on this subgraph
            g = ig.Graph()
            g.add_vertices(len(nodes))
            g.add_edges(relationships)

            partition = la.find_partition(
                g,
                la.ModularityVertexPartition,
                seed=42,
                n_iterations=2,
                resolution_parameter=1.0
            )

            # Store communities at this level
            for entity_id, comm_id in zip(nodes.keys(),
                                          partition.membership):
                community_node_id = f"community_L{current_level}_C{comm_id}"
                session.run(
                    """
                    MATCH (e:Entity {id: $entity_id})
                    MERGE (c:Community {id: $community_id})
                    SET c.level = $level, c.modularity = $modularity
                    MERGE (e)-[:MEMBER_OF]->(c)
                    """,
                    entity_id=entity_id,
                    community_id=community_node_id,
                    level=current_level,
                    modularity=partition.modularity
                )

            # Link hierarchical relationships
            if current_level > 0:
                session.run(
                    """
                    MATCH (child:Community {level: $level})
                    MATCH (child)<-[:MEMBER_OF]-(e:Entity)
                    MATCH (e)-[:MEMBER_OF]->(parent:Community {level: $parent_level})
                    MERGE (child)-[:SUB_COMMUNITY_OF]->(parent)
                    """
                )

            current_level += 1

    return current_level

# Create hierarchical structure
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
levels = create_hierarchical_communities(driver, max_levels=3)
print(f"Created {levels} levels of hierarchical communities")
driver.close()
```

This hierarchical structure enables GraphRAG's global search methodology[10][58]. Higher levels provide abstracted, summarized views of the dataset, while lower levels preserve detailed entity information. The dynamic community selection approach (as implemented in Microsoft's GraphRAG) traverses this hierarchy intelligently, rating community relevance to queries and pruning irrelevant branches—reducing token costs by 77% compared to static level selection while maintaining answer quality[10].

## Query-Driven Subgraph Extraction and Context Assembly

Subgraph extraction forms the critical bridge between graph structure and language model reasoning[9][43]. GraphRAG's effectiveness depends on retrieving focused subgraphs that contain sufficient context for LLM reasoning without overwhelming the model with irrelevant data. The extraction strategy must balance three competing objectives: breadth (including diverse information sources), depth (enabling multi-hop reasoning), and focus (excluding irrelevant nodes).

Your requirement for query-driven subgraph extraction with 2-4 hops and neighbor limiting (100 neighbors per node) reflects real production constraints. Unrestricted graph traversal on knowledge graphs readily explodes to millions of nodes, making such pragmatic limits essential[9][27]. The recommended algorithm combines several techniques:

```python
def extract_query_subgraph(driver, query_embedding, k_initial=5, max_hops=4,
                           max_neighbors_per_hop=100, max_total_nodes=500):
    """
    Extract a focused subgraph starting from query-relevant entities,
    with controlled expansion to prevent neighbor explosion
    """
    with driver.session() as session:
        # Step 1: Vector similarity to find initial seed entities
        seed_result = session.run(
            """
            CALL db.index.vector.queryNodes('chunk_embedding', $k, $query_embedding)
            YIELD node, score
            WHERE score > 0.3

            // Traverse to mentioned entities
            OPTIONAL MATCH (node)<-[:MENTIONED_IN]-(e:Entity)
            RETURN DISTINCT e.id AS entity_id, e.name AS entity_name,
                   score AS initial_score
            LIMIT $k_initial
            """,
            query_embedding=query_embedding,
            k=k_initial,
            k_initial=k_initial
        )

        seed_entities = {row['entity_id']: row for row in seed_result}

        # Step 2: Multi-hop expansion with controlled neighbor growth
        visited_nodes = set(seed_entities.keys())
        current_frontier = list(seed_entities.keys())
        current_hop = 0
        subgraph_nodes = seed_entities.copy()

        while current_hop < max_hops and current_frontier and \
              len(subgraph_nodes) < max_total_nodes:

            next_frontier = []

            # For each node at current frontier, find connected neighbors
            for node_id in current_frontier:
                # Query for related entities, ordered by relationship strength
                neighbors = session.run(
                    """
                    MATCH (e:Entity {id: $entity_id})
                    -[r:RELATED_TO|:MENTIONS|:AUTHORED_BY]-(neighbor:Entity)
                    WHERE NOT neighbor.id IN $visited
                    RETURN DISTINCT
                        neighbor.id AS neighbor_id,
                        neighbor.name AS neighbor_name,
                        type(r) AS relationship_type,
                        CASE
                            WHEN type(r) = 'RELATED_TO' THEN 2
                            WHEN type(r) = 'MENTIONS' THEN 1.5
                            WHEN type(r) = 'AUTHORED_BY' THEN 1.0
                            ELSE 0.5
                        END AS relationship_weight
                    ORDER BY relationship_weight DESC
                    LIMIT $limit
                    """,
                    entity_id=node_id,
                    visited=list(visited_nodes),
                    limit=max_neighbors_per_hop
                ).data()

                # Add neighbors to next frontier (if space available)
                for neighbor in neighbors:
                    if len(subgraph_nodes) < max_total_nodes:
                        neighbor_id = neighbor['neighbor_id']
                        visited_nodes.add(neighbor_id)
                        subgraph_nodes[neighbor_id] = neighbor
                        next_frontier.append(neighbor_id)

            current_frontier = next_frontier
            current_hop += 1
            print(f"Hop {current_hop}: Added {len(next_frontier)} nodes, "
                  f"total: {len(subgraph_nodes)}")

        # Step 3: Enrich subgraph with relationships and context
        subgraph_result = session.run(
            """
            MATCH (e:Entity)
            WHERE e.id IN $entity_ids

            // Get entity properties
            WITH e, collect(e) AS all_entities

            // Get relationships between extracted entities
            OPTIONAL MATCH (e)-[r:RELATED_TO|:MENTIONS|:AUTHORED_BY]
                            ->(related:Entity)
            WHERE related.id IN $entity_ids

            // Get supporting text chunks
            OPTIONAL MATCH (e)<-[:MENTIONED_IN]-(chunk:Chunk)

            RETURN DISTINCT
                e.id AS entity_id,
                e.name AS entity_name,
                collect(DISTINCT {
                    type: type(r),
                    target: related.id,
                    weight: properties(r).weight
                }) AS relationships,
                collect(DISTINCT {
                    id: chunk.id,
                    text: chunk.text,
                    source: chunk.source
                }) AS supporting_chunks
            """,
            entity_ids=list(subgraph_nodes.keys())
        )

        return subgraph_result.data()

# Example: Extract subgraph for a specific query
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query = "What are the security implications of distributed systems?"
query_embedding = model.encode(query, convert_to_tensor=False).tolist()

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
subgraph = extract_query_subgraph(
    driver,
    query_embedding,
    k_initial=5,
    max_hops=3,
    max_neighbors_per_hop=50,
    max_total_nodes=300
)

print(f"Extracted subgraph with {len(subgraph)} entities")
driver.close()
```

The neighbor limiting strategy operates at two levels: per-node filtering (max_neighbors_per_hop) and global limiting (max_total_nodes). Relationship weighting prioritizes different connection types—direct entity relationships carry highest weight, mention relationships moderate weight, authorship relationships lower weight—ensuring the most semantically relevant neighbors get traversed first. This prevents exhausting the expansion budget on weakly-connected peripheral nodes[9][27].

Converting the extracted subgraph to LLM-readable format requires careful structuring. Different LLMs benefit from different formats, but a structured text representation combining entities, relationships, and supporting evidence typically yields good results:

```python
def convert_subgraph_to_context(subgraph_data):
    """
    Convert extracted subgraph to readable context for LLM
    """
    lines = []
    lines.append("=== KNOWLEDGE GRAPH CONTEXT ===\n")

    # Entity listing
    lines.append("ENTITIES:")
    entity_map = {}
    for idx, entity in enumerate(subgraph_data):
        entity_id = entity['entity_id']
        entity_map[entity_id] = idx + 1
        lines.append(f"{idx + 1}. {entity['entity_name']}")

    lines.append("\nRELATIONSHIPS:")
    # Relationship listing
    rel_count = 1
    for entity in subgraph_data:
        for rel in entity.get('relationships', []):
            target_id = rel.get('target')
            if target_id in entity_map:
                lines.append(
                    f"{rel_count}. Entity {entity_map[entity['entity_id']]} "
                    f"({entity['entity_name']}) --[{rel['type']}]--> "
                    f"Entity {entity_map[target_id]}"
                )
                rel_count += 1

    lines.append("\nSUPPORTING EVIDENCE:")
    # Supporting chunks
    for entity in subgraph_data:
        for chunk in entity.get('supporting_chunks', []):
            lines.append(
                f"\nFrom '{chunk['source']}':\n"
                f"  {chunk['text'][:200]}..."
            )

    return "\n".join(lines)

# Generate LLM context
context_text = convert_subgraph_to_context(subgraph)
print(context_text)
```

## GraphRAG Query Execution and Community Summary Generation

GraphRAG queries operate in two modalities: global search for dataset-wide reasoning and local search for targeted queries[10][58][61]. Global search traverses hierarchical communities, retrieving and summarizing information at multiple abstraction levels. Local search starts from query-relevant entities and expands contextually significant subgraphs.

Global search implementation requires pre-computed community summaries—LLM-generated summaries of each community's content, relationships, and significance[10][13][58]:

```python
def generate_community_summaries(driver, llm_model=None):
    """
    Generate LLM summaries for each community to support global search
    Requires an LLM API (OpenAI, Anthropic, etc.)
    """
    import json
    from datetime import datetime

    # Default: use a summarization function from transformers
    if llm_model is None:
        from transformers import pipeline
        llm_model = pipeline("summarization", model="facebook/bart-large-cnn")

    with driver.session() as session:
        # Get all communities with their member entities
        communities = session.run(
            """
            MATCH (c:Community)
            WHERE NOT (c)-[:SUB_COMMUNITY_OF]->()
            WITH c, collect(c.id) AS top_level_communities
            OPTIONAL MATCH (c)<-[:MEMBER_OF]-(e:Entity)
            OPTIONAL MATCH (e)<-[:MENTIONED_IN]-(chunk:Chunk)
            RETURN
                c.id AS community_id,
                c.level AS level,
                collect(DISTINCT e.name) AS member_entities,
                collect(DISTINCT chunk.text) AS supporting_text
            LIMIT 50  // Process first 50 communities
            """
        )

        for community in communities:
            community_id = community['community_id']
            member_entities = community['member_entities']
            supporting_text = community['supporting_text']

            # Create summary prompt
            context_text = f"""
            This community contains these entities: {', '.join(member_entities[:20])}

            Supporting information:
            {' '.join(supporting_text[:5])}
            """

            # Generate summary using LLM
            summary = llm_model(context_text, max_length=150, min_length=50)[0]
            summary_text = summary['summary_text']

            # Store summary in Neo4j
            session.run(
                """
                MATCH (c:Community {id: $community_id})
                SET c.summary = $summary,
                    c.summary_generated_at = $timestamp
                """,
                community_id=community_id,
                summary=summary_text,
                timestamp=datetime.now().isoformat()
            )

            print(f"Generated summary for {community_id}")

# Generate summaries (requires LLM setup)
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
generate_community_summaries(driver)
driver.close()
```

With community summaries in place, global search queries use a map-reduce pattern[10][58]:

```cypher
// Global Search: Answer dataset-wide question using community summaries
WITH $user_question AS question

// MAP phase: Generate intermediate responses from community summaries
MATCH (c:Community {level: 1})
WHERE c.summary IS NOT NULL

WITH question, c, c.summary AS context
CALL apoc.openai.query(
  {
    message: "Given this context about a dataset community: " + context +
            "\n\nHow does this relate to: " + question,
    systemPrompt: "You are a research analyst summarizing dataset insights."
  }
)
YIELD value AS intermediate_response
WITH question, collect({
  community: c.id,
  response: intermediate_response
}) AS all_responses

// REDUCE phase: Aggregate responses into final answer
CALL apoc.openai.query(
  {
    message: "Synthesize these community insights: " + all_responses +
            "\n\nOriginal question: " + question,
    systemPrompt: "Synthesize multiple perspectives into a cohesive answer."
  }
)
YIELD value AS final_response

RETURN final_response AS answer
```

Local search provides targeted retrieval for entity-specific queries[9][61]:

```python
def local_search(driver, query, llm_model=None):
    """
    Execute local search: start from query-relevant entities,
    expand with contextual relationships, return focused answer
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query, convert_to_tensor=False).tolist()

    with driver.session() as session:
        # Step 1: Find initial entities matching query
        seed_entities = session.run(
            """
            CALL db.index.vector.queryNodes('chunk_embedding', 10, $query_embedding)
            YIELD node, score
            MATCH (node)<-[:MENTIONED_IN]-(e:Entity)
            RETURN DISTINCT e.id, e.name, score
            LIMIT 5
            """,
            query_embedding=query_embedding
        )

        # Step 2: Extract focused subgraph
        entity_ids = [row['id'] for row in seed_entities]
        subgraph = extract_query_subgraph(
            driver,
            query_embedding,
            k_initial=5,
            max_hops=2,
            max_neighbors_per_hop=50,
            max_total_nodes=200
        )

        # Step 3: Convert to context
        context = convert_subgraph_to_context(subgraph)

        # Step 4: Generate answer with LLM
        if llm_model is None:
            # Use a simple retrieval augmentation pattern
            answer = f"Based on the connected entities: {context}"
        else:
            answer = llm_model(f"Question: {query}\n\nContext: {context}")

        return {
            "question": query,
            "subgraph_size": len(subgraph),
            "context": context,
            "answer": answer
        }

# Execute local search
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
result = local_search(driver, "What are the key security considerations?")
print(json.dumps(result, indent=2))
driver.close()
```

## Integration Architecture: Adding GraphRAG as ACI Tier 5

Integrating GraphRAG as a fifth ACI tier requires careful architectural consideration of routing logic, fallback mechanisms, response formatting, and performance monitoring. Your existing four tiers (INSTANT, RAG, LONG_CONTEXT, PERPLEXITY) each serve distinct purposes; GraphRAG should complement rather than duplicate their functionality.

The routing strategy determines when each tier handles queries[40][59]. INSTANT tier handles simple factual lookups with high-confidence keyword matches. RAG tier performs vector similarity search for semantic matching. LONG_CONTEXT tier manages queries requiring extended document contexts. PERPLEXITY tier quantifies uncertainty in answers. GraphRAG tier handles complex relational reasoning requiring multi-hop entity traversal.

```python
class ACIRouter:
    """
    Route queries to appropriate ACI tier based on
    query characteristics and intent classification
    """
    def __init__(self, driver):
        self.driver = driver
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def classify_query_intent(self, query):
        """
        Classify query intent to determine routing tier
        Returns: (tier, confidence, reasoning)
        """
        query_lower = query.lower()

        # Define keywords for each tier
        instant_keywords = ['what is', 'who is', 'when was', 'where is',
                          'simple', 'basic', 'definition']
        graphrag_keywords = ['how does', 'relationship', 'connect', 'relate',
                           'through', 'chain', 'path', 'network', 'multi-hop',
                           'across', 'between']
        long_context_keywords = ['comprehensive', 'detailed', 'full analysis',
                               'complete', 'extensively', 'thoroughly']
        perplexity_keywords = ['certain', 'confident', 'reliability', 'confidence',
                             'uncertainty', 'likely', 'probably']

        scores = {
            'INSTANT': sum(1 for kw in instant_keywords if kw in query_lower),
            'GRAPHRAG': sum(1 for kw in graphrag_keywords if kw in query_lower),
            'LONG_CONTEXT': sum(1 for kw in long_context_keywords if kw in query_lower),
            'PERPLEXITY': sum(1 for kw in perplexity_keywords if kw in query_lower),
            'RAG': 0  # Default tier
        }

        max_tier = max(scores, key=scores.get)
        max_score = scores[max_tier]
        total_keywords = sum(scores.values())

        if max_score == 0:
            # No strong intent signals, default to RAG
            return 'RAG', 0.5, 'No strong intent indicators'

        confidence = max_score / (total_keywords + 1)
        reasoning = f"{max_score} keywords matched for {max_tier}"

        return max_tier, confidence, reasoning

    def should_use_graphrag(self, query, classification_result):
        """
        Determine if GraphRAG tier is appropriate
        """
        tier, confidence, reasoning = classification_result

        # Use GraphRAG if explicitly classified or if query
        # shows relational complexity
        if tier == 'GRAPHRAG' and confidence > 0.3:
            return True, 'Explicit relational query detected'

        # Check for entity density (multiple entities mentioned)
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity)
                WHERE $query CONTAINS e.name
                RETURN count(e) AS entity_count
                """,
                query=query
            )
            entity_count = result.single()['entity_count']

        if entity_count >= 2:
            return True, f'Query mentions {entity_count} entities'

        return False, 'No relational indicators'

    def route_query(self, query):
        """
        Route query to appropriate ACI tier
        """
        classification = self.classify_query_intent(query)
        use_graphrag, reason = self.should_use_graphrag(query, classification)

        if use_graphrag:
            return {
                'tier': 'GRAPHRAG',
                'reason': reason,
                'confidence': classification[1],
                'parameters': {
                    'max_hops': 3,
                    'max_neighbors_per_hop': 100,
                    'max_total_nodes': 500
                }
            }
        else:
            return {
                'tier': classification[0],
                'reason': classification[2],
                'confidence': classification[1],
                'parameters': {}
            }

# Usage
router = ACIRouter(driver)
routing_decision = router.route_query(
    "How do distributed consensus algorithms relate to blockchain?"
)
print(f"Route to: {routing_decision['tier']} - {routing_decision['reason']}")
```

Fallback mechanisms ensure graceful degradation when GraphRAG queries fail or return empty results[40]. A well-designed fallback chain prevents user-facing errors:

```python
def execute_with_fallback(driver, query, llm_model=None):
    """
    Execute query with fallback chain:
    1. Try GraphRAG local search
    2. Fall back to graph traversal only
    3. Fall back to RAG (vector search)
    4. Provide error message
    """

    results = {
        'query': query,
        'primary_result': None,
        'fallback_tier_used': None,
        'status': 'failed'
    }

    # Tier 1: GraphRAG local search
    try:
        result = local_search(driver, query, llm_model)
        if result and result.get('subgraph_size', 0) > 0:
            results['primary_result'] = result
            results['fallback_tier_used'] = 'GRAPHRAG'
            results['status'] = 'success'
            return results
    except Exception as e:
        print(f"GraphRAG search failed: {e}")

    # Tier 2: Pure graph traversal (no LLM summarization)
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(query, convert_to_tensor=False).tolist()

        subgraph = extract_query_subgraph(driver, query_embedding)
        if len(subgraph) > 0:
            context = convert_subgraph_to_context(subgraph)
            results['primary_result'] = {
                'answer': f"Graph entities: {context}",
                'subgraph_size': len(subgraph),
                'method': 'graph_traversal_only'
            }
            results['fallback_tier_used'] = 'GRAPH_TRAVERSAL'
            results['status'] = 'success'
            return results
    except Exception as e:
        print(f"Graph traversal failed: {e}")

    # Tier 3: Fall back to vector-only RAG
    try:
        with driver.session() as session:
            result = session.run(
                """
                CALL db.index.vector.queryNodes('chunk_embedding', 5, $query_embedding)
                YIELD node, score
                RETURN node.text AS text, score
                LIMIT 3
                """,
                query_embedding=model.encode(query, convert_to_tensor=False).tolist()
            )

            texts = [row['text'] for row in result]
            if texts:
                results['primary_result'] = {
                    'answer': f"Retrieved documents: {texts}",
                    'method': 'vector_search_only'
                }
                results['fallback_tier_used'] = 'RAG'
                results['status'] = 'success'
                return results
    except Exception as e:
        print(f"Vector search failed: {e}")

    # All tiers failed
    results['primary_result'] = {
        'answer': 'Unable to find relevant information',
        'error': 'All retrieval tiers exhausted'
    }
    results['fallback_tier_used'] = 'ERROR'
    results['status'] = 'failed'
    return results

# Execute with fallback
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
result = execute_with_fallback(driver, "Query that might fail", llm_model=None)
print(json.dumps(result, indent=2))
driver.close()
```

## Incremental Update and Delta Detection

Your fifth requirement—incremental updates from delta detection—ensures that the knowledge graph evolves with source documents without requiring full reprocessing. The delta detection system monitors source changes and propagates updates through entity extraction, embedding generation, and community recomputation:

```python
def detect_document_deltas(driver, document_source_path):
    """
    Monitor source documents for changes and identify deltas
    """
    import os
    import hashlib
    from datetime import datetime

    current_files = {}
    for filename in os.listdir(document_source_path):
        if filename.endswith(('.txt', '.pdf', '.md')):
            filepath = os.path.join(document_source_path, filename)
            with open(filepath, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            current_files[filename] = {
                'hash': file_hash,
                'modified_time': os.path.getmtime(filepath)
            }

    with driver.session() as session:
        # Check for new, modified, or deleted documents
        deltas = {'new': [], 'modified': [], 'deleted': []}

        # Find new and modified documents
        for filename, current_info in current_files.items():
            result = session.run(
                """
                MATCH (d:Document {source: $source})
                RETURN d.file_hash AS hash
                """,
                source=filename
            )

            db_record = result.single()

            if db_record is None:
                deltas['new'].append(filename)
            elif db_record['hash'] != current_info['hash']:
                deltas['modified'].append(filename)

        # Find deleted documents
        stored_docs = session.run(
            "MATCH (d:Document) RETURN d.source AS source"
        )
        stored_filenames = {row['source'] for row in stored_docs}

        for filename in stored_filenames:
            if filename not in current_files:
                deltas['deleted'].append(filename)

        return deltas

def process_document_deltas(driver, deltas, embedder):
    """
    Process detected document changes:
    1. Ingest new documents
    2. Update modified documents
    3. Remove deleted documents and related entities
    4. Recompute affected communities
    """

    with driver.session() as session:
        # Handle deleted documents
        for deleted_doc in deltas['deleted']:
            session.run(
                """
                MATCH (d:Document {source: $source})
                DETACH DELETE d
                """,
                source=deleted_doc
            )
            print(f"Deleted document: {deleted_doc}")

        # Handle modified documents (treat as delete + re-add)
        for modified_doc in deltas['modified']:
            session.run(
                """
                MATCH (d:Document {source: $source})
                DETACH DELETE d
                """,
                source=modified_doc
            )
            deltas['new'].append(modified_doc)

        # Handle new documents
        for new_doc in deltas['new']:
            # Extract text, chunk, embed, and store
            # (Implementation depends on document format)
            chunks = extract_document_chunks(new_doc)

            for idx, chunk_text in enumerate(chunks):
                embedding = embedder.encode(
                    chunk_text,
                    convert_to_tensor=False
                ).tolist()

                session.run(
                    """
                    MERGE (d:Document {source: $source})
                    WITH d
                    CREATE (c:Chunk {
                        id: $chunk_id,
                        text: $text,
                        embedding: $embedding,
                        chunk_index: $chunk_index
                    })
                    CREATE (c)-[:PART_OF]->(d)
                    """,
                    source=new_doc,
                    chunk_id=f"{new_doc}_chunk_{idx}",
                    text=chunk_text,
                    embedding=embedding,
                    chunk_index=idx
                )

            print(f"Ingested new document: {new_doc} with {len(chunks)} chunks")

        # Recompute affected communities
        if deltas['new'] or deltas['modified'] or deltas['deleted']:
            print("Recomputing affected communities...")
            # Trigger hierarchical community recomputation
            # (Can be run as async job for large updates)
            create_hierarchical_communities(driver, max_levels=2)

# Monitor and process deltas
def incremental_update_loop(driver, source_path, check_interval_seconds=300):
    """
    Periodically check for document changes and update graph
    """
    import time
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    while True:
        try:
            deltas = detect_document_deltas(driver, source_path)

            if any(deltas.values()):
                print(f"Found deltas: {deltas}")
                process_document_deltas(driver, deltas, embedder)

            time.sleep(check_interval_seconds)
        except Exception as e:
            print(f"Error in incremental update loop: {e}")
            time.sleep(check_interval_seconds)

# Start incremental update monitor
# In production, run this as a background service
# incremental_update_loop(driver, '/path/to/documents', check_interval_seconds=300)
```

## Performance Monitoring and Production Deployment Recommendations

Successful production deployment of GraphRAG requires comprehensive performance monitoring covering query latency, cache hit rates, memory utilization, and answer quality metrics. The following monitoring strategy captures essential operational signals:

```python
class GraphRAGMonitor:
    """
    Monitor GraphRAG performance metrics and operational health
    """
    def __init__(self, driver):
        self.driver = driver
        self.metrics = {
            'query_latencies': [],
            'subgraph_sizes': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': []
        }

    def record_query_latency(self, query_id, latency_ms, tier):
        """Record query execution time"""
        self.metrics['query_latencies'].append({
            'query_id': query_id,
            'latency_ms': latency_ms,
            'tier': tier,
            'timestamp': datetime.now()
        })

    def record_subgraph_size(self, query_id, node_count, edge_count):
        """Record subgraph extraction metrics"""
        self.metrics['subgraph_sizes'].append({
            'query_id': query_id,
            'nodes': node_count,
            'edges': edge_count,
            'timestamp': datetime.now()
        })

    def get_performance_summary(self, hours=1):
        """Generate performance summary for operational dashboards"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_latencies = [
            m for m in self.metrics['query_latencies']
            if m['timestamp'] > cutoff_time
        ]

        if not recent_latencies:
            return {'status': 'no_queries', 'hours': hours}

        latencies = [m['latency_ms'] for m in recent_latencies]

        return {
            'hours': hours,
            'queries': len(recent_latencies),
            'avg_latency_ms': sum(latencies) / len(latencies),
            'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)],
            'p99_latency_ms': sorted(latencies)[int(len(latencies) * 0.99)],
            'by_tier': self._summarize_by_tier(recent_latencies)
        }

    def _summarize_by_tier(self, latencies):
        """Break down metrics by ACI tier"""
        by_tier = {}
        for metric in latencies:
            tier = metric['tier']
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(metric['latency_ms'])

        return {
            tier: {
                'avg_ms': sum(ms) / len(ms),
                'queries': len(ms)
            }
            for tier, ms in by_tier.items()
        }

# Production deployment checklist
DEPLOYMENT_CHECKLIST = """
GRAPHRAG PRODUCTION DEPLOYMENT CHECKLIST

1. DATA PREPARATION
   ✓ Verify all 5,284 nodes have 384-dimensional embeddings
   ✓ Validate embedding consistency and no NaN values
   ✓ Test vector index creation on full dataset
   ✓ Verify vector search performance (p99 latency < 100ms)

2. COMMUNITY DETECTION
   ✓ Run Leiden with seed=42 for reproducibility
   ✓ Verify community quality (modularity > 0.4)
   ✓ Generate hierarchical communities (2-3 levels)
   ✓ Test community summary generation with LLM

3. QUERY ROUTING
   ✓ Configure intent classification thresholds
   ✓ Test routing on 100+ sample queries
   ✓ Verify fallback chains function correctly
   ✓ Monitor routing distribution for anomalies

4. PERFORMANCE BASELINE
   ✓ Measure vector search latency (p95 < 100ms)
   ✓ Measure subgraph extraction latency (p95 < 500ms)
   ✓ Measure LLM response generation time
   ✓ Establish total query latency baseline

5. PRODUCTION SAFEGUARDS
   ✓ Implement query timeout (60 seconds)
   ✓ Implement subgraph size limits (500 max nodes)
   ✓ Implement LLM API rate limiting
   ✓ Configure monitoring and alerting
   ✓ Set up incident response procedures

6. DEPLOYMENT
   ✓ Deploy GraphRAG as background service
   ✓ Configure incremental update monitoring
   ✓ Configure database backup strategy
   ✓ Set up performance dashboards
   ✓ Document SLAs and escalation procedures
"""
```

GraphRAG integration into your existing system represents a significant capability enhancement for complex relational queries. The layered architecture—combining vector retrieval for semantic matching, graph traversal for relationship reasoning, and community detection for abstracted knowledge—creates a system capable of answering sophisticated multi-hop questions that defeat pure vector-based approaches. By implementing the code patterns and architectural guidance in this report, you can productionize GraphRAG while maintaining the stable, predictable behavior of your existing INSTANT, RAG, LONG_CONTEXT, and PERPLEXITY tiers. The 77% token cost reduction through dynamic community selection and the demonstrated improvements in multi-hop reasoning accuracy establish GraphRAG as a critical addition to your AI system's reasoning capabilities.

---

## Citations

1. https://github.com/run-llama/llama_index/issues/12266
2. https://github.com/langchain4j/langchain4j/issues/1306
3. https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.leiden.leiden_communities.html
4. https://github.com/neo4j/neo4j/issues/13368
5. https://community.neo4j.com/t/vector-indexing-across-multiple-node-labels/69864
6. https://hackernoon.com/building-a-hybrid-rag-agent-with-neo4j-graphs-and-milvus-vector-search
7. https://networkx.org/documentation/stable/reference/algorithms/community.html
8. https://community.neo4j.com/t/circular-hierarchy-from-leiden-clustering/69385
9. https://igor-polyakov.com/2025/11/26/graphrag-part-2-cross-doc-sub-graph-extraction-multi-vector-entity-representation/
10. https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/
11. https://graphacademy.neo4j.com/courses/gds-fundamentals/3-working-with-algorithms/5-configuring-algorithms/
12. https://arxiv.org/abs/2601.14662
13. https://graphrag.com/reference/graphrag/global-community-summary-retriever/
14. https://community.neo4j.com/t/how-to-ensure-results-consistency-in-community-detection-algorithms/61111
15. https://docs.langchain.com/oss/python/integrations/vectorstores/neo4jvector
16. https://foojay.io/today/navigating-the-nuances-of-graphrag-vs-rag/
17. https://community.neo4j.com/t/vector-search-index-pre-filtered-query/64465
18. https://github.com/neo4j-partners/neo4j-databricks-demo/blob/main/VECTOR.md
19. https://graphrag.com/concepts/intro-to-graphrag/
20. https://www.youtube.com/watch?v=keatNq2Coo4
21. https://community.neo4j.com/t/nearest-neighbor-to-a-node-from-a-set-of-nodes-of-specific-type/4862
22. https://reference.langchain.com/v0.3/python/community/vectorstores/langchain_community.vectorstores.neo4j_vector.Neo4jVector.html
23. https://community.neo4j.com/t/whats-the-best-way-to-incrementally-add-content-to-neo4j-database/16897
24. https://community.neo4j.com/t/subgraph-extraction-in-a-single-instance-of-a-multi-tenant-graph/12177
25. https://github.com/neo4j/neo4j/issues/13654
26. https://pub.towardsai.net/building-a-self-updating-knowledge-graph-from-meeting-notes-with-llm-extraction-and-neo4j-b02d3d62a251
27. https://arxiv.org/html/2505.14394v1
28. https://www.meilisearch.com/blog/graph-rag-vs-vector-rag
29. https://github.com/satijalab/seurat/discussions/6754
30. https://quantiphi.com/blog/bridging-code-and-context-a-knowledge-graph-based-repository-level-code-generation
31. https://www.instaclustr.com/education/retrieval-augmented-generation/graph-rag-vs-vector-rag-3-differences-pros-and-cons-and-how-to-choose/
32. https://memgraph.com/blog/graph-clustering-algorithms-usage-comparison
33. https://pypi.org/project/leidenalg/
34. https://www.instaclustr.com/education/retrieval-augmented-generation/graph-rag-vs-vector-rag-3-differences-pros-and-cons-and-how-to-choose/
35. http://oreateai.com/blog/performance-tuning-and-best-practices-for-neo4j-database/ec3d04d90cf23535d66072fd4900efdf
36. https://leidenalg.readthedocs.io/en/stable/intro.html
37. https://www.chitika.com/graph-rag-vs-vector-rag/
38. https://community.neo4j.com/t/optimizing-graph-database-performance-on-high-performance-pc-desktops/71732
39. https://docs.langchain.com/oss/python/integrations/vectorstores/neo4jvector
40. https://gradientflow.substack.com/p/graphrag-design-patterns-challenges
41. https://dev.to/exploredataaiml/building-an-intelligent-rag-system-with-query-routing-validation-and-self-correction-2e4k
42. https://community.neo4j.com/t/vector-search-index-pre-filtered-query/64465
43. https://arxiv.org/html/2501.00309v2
44. https://github.com/mia-platform/ai-rag-template
45. https://memgraph.com/docs/querying/vector-search
46. https://trustgraph.ai/news/context-graph-manifesto/
47. https://leidenalg.readthedocs.io/en/latest/reference.html
48. https://atalupadhyay.wordpress.com/2026/01/24/the-complete-guide-to-context-graphs/
49. https://leidenalg.readthedocs.io/en/latest/advanced.html
50. https://graphacademy.neo4j.com/courses/llm-vectors-unstructured/2-vector-indexes/3-create-vector-index/
51. https://cocoindex.io/examples/meeting_notes_graph
52. https://www.geeksforgeeks.org/python/python-program-for-breadth-first-search-or-bfs-for-a-graph/
53. https://www.blog.langchain.com/neo4j-x-langchain-new-vector-index/
54. https://towardsai.net/p/machine-learning/building-a-self-updating-knowledge-graph-from-meeting-notes-with-llm-extraction-and-neo4j
55. https://www.datacamp.com/tutorial/depth-first-search-in-python
56. https://dev.to/exploredataaiml/building-an-intelligent-rag-system-with-query-routing-validation-and-self-correction-2e4k
57. https://community.neo4j.com/t/how-to-ensure-results-consistency-in-community-detection-algorithms/61111
58. https://microsoft.github.io/graphrag/query/global_search/
59. https://www.vellum.ai/blog/how-to-build-intent-detection-for-your-chatbot
60. https://leidenalg.readthedocs.io/en/latest/reference.html
61. https://www.microsoft.com/en-us/research/blog/introducing-drift-search-combining-global-and-local-search-methods-to-improve-quality-and-efficiency/

---

## Usage Stats

- Prompt tokens: 419
- Completion tokens: 10892
- Total tokens: 11311
