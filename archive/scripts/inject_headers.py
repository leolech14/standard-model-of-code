import json

def create_header_node(region_name, color_code, x, y, width):
    content = ""
    
    if region_name == "DATA":
        content = """# DATA / FOUNDATIONS
**The Atomic Nucleus**

> "Before there was logic, there was state."

This region represents the **Raw Material** of the universe.
*   **Physics Analogy:** Quantum Chromodynamics (Quarks & Gluons).
*   **Force:** Strong Nuclear Force (Binding Energy).
*   **Nature:** Passive, Atomic, Fundamental.

```mermaid
classDiagram
    class Bit {
        +0/1 state
        +spin
    }
    class Byte {
        +8 bits
        +addressable
    }
    class Primitive {
        +Integer
        +Float
        +String
    }
    Bit <|-- Byte : composes
    Byte <|-- Primitive : encodes
```

**Key Laws:**
1.  **Immutability:** Atoms do not change identity; they react.
2.  **Conservation of Info:**  Data is neither created nor destroyed, only transformed.
"""

    elif region_name == "LOGIC":
        content = """# LOGIC / FLOW
**Thermodynamics & Kinetics**

> "Energy allows the universe to change."

This region represents the **Work** being done.
*   **Physics Analogy:** Classical Mechanics & Thermodynamics.
*   **Force:** Electromagnetism (Transformation).
*   **Nature:** Active, Kinetic, Temporal.

```mermaid
graph LR
    Input((Input)) -->|Work| Logic[Logic Core]
    Logic -->|Result| Output((Output))
    Logic -.->|Heat| SideEffects(Side Effects)
    
    style Logic fill:#f33,stroke:#333,stroke-width:4px
    style SideEffects fill:#f99,stroke:#333,stroke-dasharray: 5 5
```

**Key Laws:**
1.  **2nd Law of Thermodynamics:** Entropy (complexity) always increases unless actively managed.
2.  **Action/Reaction:** Every Command has an Effect.
"""

    elif region_name == "ORG":
        content = """# ORGANIZATION / STRUCTURE
**Molecular Biology & Chemistry**

> "Life is order protecting itself from entropy."

This region represents the **Structure** that holds logic and data.
*   **Physics Analogy:** Condensed Matter Physics / Chemistry.
*   **Force:** Weak Nuclear Force (Decay & Transmutation).
*   **Nature:** Structural, Bounded, hierarchical.

```mermaid
mindmap
  root((Structure))
    Module
      Aggregate
        Entity
          ValueObject
    BoundedContext
      Domain
        Core
```

**Key Laws:**
1.  **Cellular Integrity:** A Bounded Context must protect its internal language.
2.  **Membrane Theory:** Ports & Adapters define what passes through the membrane.
"""

    elif region_name == "EXEC":
        content = """# EXECUTION / INFRA
**Cosmology & Astrophysics**

> "The spacetime where events occur."

This region represents the **Environment** where code runs.
*   **Physics Analogy:** General Relativity (Spacetime warping).
*   **Force:** Gravity (Lifecycle & Scope).
*   **Nature:** Environmental, Deployed, Massive.

```mermaid
sequenceDiagram
    participant Docker
    participant Kubernetes
    participant Lambda
    
    Docker->>Kubernetes: Deploy Image
    Kubernetes->>Lambda: Trigger Event
    Lambda-->>Docker: Log & Metric
```

**Key Laws:**
1.  **Speed of Light:** Latency is the absolute limit of distributed systems.
2.  **Event Horizon:** Beyond a certain scale, consistency is impossible (CAP Theorem).
"""

    return {
        "id": f"header_theory_{region_name.lower()}",
        "type": "text",
        "text": content,
        "x": x,
        "y": y - 1000, # Place 1000 units above
        "width": width,
        "height": 900,
        "color": color_code
    }

def inject_headers(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    nodes = data.get('nodes', [])
    new_nodes = []
    
    # Target Groups
    targets = {
        '1': 'LOGIC',
        '3': 'EXEC',
        '4': 'ORG',
        '5': 'DATA'
    }
    
    groups_found = {}
    
    # 1. Find group bounds
    for n in nodes:
        if n.get('type') == 'group':
            color = n.get('color')
            if color in targets:
                groups_found[targets[color]] = n
                
    # 2. Create Headers
    for region, group in groups_found.items():
        print(f"Injecting header for {region}...")
        header = create_header_node(
            region, 
            group['color'], 
            group['x'], 
            group['y'], 
            group['width']
        )
        new_nodes.append(header)
        
    # 3. Add to nodes
    filtered_nodes = [n for n in nodes if not n['id'].startswith('header_theory_')]
    filtered_nodes.extend(new_nodes)
    data['nodes'] = filtered_nodes
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Injected {len(new_nodes)} headers successfully.")

if __name__ == "__main__":
    inject_headers("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
