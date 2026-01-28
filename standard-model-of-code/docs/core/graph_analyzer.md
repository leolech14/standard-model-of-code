# Graph Analyzer

> **Mirror**: [`graph_analyzer.py`](../../../src/core/graph_analyzer.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture
### Classes
- **`NodeStats`**: No docstring
- **`GraphAnalysisResult`**: No docstring

### Functions
- **`get_filtered_degree`**: Calculate degree counting only edges of specified types.
- **`load_graph`**: Load graph.json into a NetworkX DiGraph.
- **`find_bottlenecks`**: Find bottleneck nodes using betweenness centrality.
- **`find_pagerank`**: Rank nodes by PageRank (importance based on incoming links).
- **`find_communities_leiden`**: Detect communities using the Leiden algorithm (preferred).
- **`find_communities_louvain`**: Detect communities using Louvain algorithm (fallback).
- **`find_communities`**: Detect communities using the best available algorithm.
- **`find_bridges`**: Find bridge edges whose removal would disconnect the graph.
- **`shortest_path`**: Find shortest path between two nodes.
- **`shortest_path.resolve`**: No docstring
- **`suggest_refactoring_cuts`**: Suggest edges to remove that would best decouple the graph.
- **`analyze_full`**: Run full analysis on a graph.
- **`generate_report`**: Generate markdown report from analysis results.
