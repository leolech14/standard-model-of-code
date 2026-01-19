
from typing import List, Dict, Any, Tuple
from collections import defaultdict, deque
import statistics

class TopologyClassifier:
    """
    Analyzes the 'visual' shape of a software graph to help LLMs 'see' the architecture.
    Classifies into patterns like:
    - DISCONNECTED_ISLANDS: Many separate clusters
    - BIG_BALL_OF_MUD: High density, high tangles, no hierarchy
    - STAR_HUB: One massive central node (god object)
    - STRICT_LAYERS: Clear directional flow, low cycles
    - MESH: High connectivity but balanced
    """

    def classify(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        if not nodes:
            return {"shape": "EMPTY", "description": "No nodes found"}

        # 1. Component Analysis (Islands)
        components = self._find_components(nodes, edges)
        num_components = len(components)
        largest_component_size = max(len(c) for c in components) if components else 0
        percent_in_largest = (largest_component_size / len(nodes)) * 100

        # 2. Centrality Analysis (Hubs)
        in_degrees = defaultdict(int)
        out_degrees = defaultdict(int)
        for edge in edges:
            in_degrees[edge.get('target', '')] += 1
            out_degrees[edge.get('source', '')] += 1
        
        degrees = [in_degrees[n['id']] + out_degrees[n['id']] for n in nodes]
        max_degree = max(degrees) if degrees else 0
        avg_degree = statistics.mean(degrees) if degrees else 0
        # Centralization: How much is the graph dominated by one node?
        # (Simplified Freeman centralization)
        centralization = sum(max_degree - d for d in degrees) / ((len(nodes) - 1) * (len(nodes) - 2)) if len(nodes) > 2 else 0

        # 3. Hierarchy Analysis (Layers vs Cycles)
        # We can reuse Knot Score from existing analysis, but calculate a hierarchy score
        # Simple proxy: Ratio of feedback edges (cycles) to feedforward edges
        
        # 4. Classification Logic
        shape = "UNKNOWN"
        description = "Undefined structure"
        
        if num_components > 5 and percent_in_largest < 50:
            shape = "DISCONNECTED_ISLANDS"
            description = f"Fragmented into {num_components} separate clusters."
        
        elif centralization > 0.4: # Arbitrary threshold, tune based on experience
            top_hub_id = max(nodes, key=lambda n: in_degrees[n['id']] + out_degrees[n['id']])['id']
            hub_name = top_hub_id.split(':')[-1]
            shape = "STAR_HUB"
            description = f"Dominated by central hub '{hub_name}' (Star Topology)."
            
        elif avg_degree > 10: # Very dense
            shape = "DENSE_MESH"
            description = "Highly interconnected mesh."
            
        else:
            # Check for Mud vs Layers
            # We need knot score input for this ideally, but let's approximate
            # Here we default to "Generic Network"
            shape = "BALANCED_NETWORK"
            description = "Connected network with distributed responsibility."

        return {
            "shape": shape,
            "description": description,
            "visual_metrics": {
                "components": num_components,
                "largest_cluster_percent": round(percent_in_largest, 1),
                "centralization_score": round(centralization, 2),
                "density_score": round(avg_degree, 2)
            }
        }

    def _find_components(self, nodes: List[Dict], edges: List[Dict]) -> List[List[str]]:
        # Undirected component finding
        adj = defaultdict(set)
        for edge in edges:
            s, t = edge.get('source'), edge.get('target')
            if s and t:
                adj[s].add(t)
                adj[t].add(s)
        
        visited = set()
        components = []
        
        node_ids = set(n['id'] for n in nodes)
        
        for node in node_ids:
            if node not in visited:
                component = []
                queue = deque([node])
                visited.add(node)
                while queue:
                    curr = queue.popleft()
                    component.append(curr)
                    for neighbor in adj[curr]:
                        if neighbor in node_ids and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(component)
        
        return components
