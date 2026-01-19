import json

def inject_unified(file_path):
    print(f"Injecting Unified Diagram into {file_path}...")
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    nodes = data.get('nodes', [])
    
    # Define the Unified Diagram Content
    unified_content = """# THE STANDARD MODEL OF CODE
**Grand Unified Theory (GUT)**

```mermaid
graph TD
    %% Global Styles
    classDef data fill:#0bb,stroke:#fff,stroke-width:2px,color:#fff;
    classDef logic fill:#f33,stroke:#fff,stroke-width:2px,color:#fff;
    classDef org fill:#4b4,stroke:#fff,stroke-width:2px,color:#fff;
    classDef exec fill:#ea2,stroke:#fff,stroke-width:2px,color:#fff;
    classDef void fill:#000,stroke:#f00,stroke-width:2px,stroke-dasharray: 5 5,color:#f00;

    subgraph UNIVERSE [The Code Universe]
        direction TB
        
        %% PHASE 1: MATTER
        subgraph P1 [Phase 1: DATA / MATTER]
            Bits(Bits & Bytes):::data
            Primitives(Primitives):::data
            State(State):::data
            
            Bits -->|Encodes| Primitives
            Primitives -->|Composes| State
        end
        
        %% CONNECTION 1: STRONG FORCE
        State ==>|Strong Force: Responsibility| LogicCore
        
        %% PHASE 2: ENERGY
        subgraph P2 [Phase 2: LOGIC / ENERGY]
            LogicCore(Logic Core):::logic
            Flow(Control Flow):::logic
            Work(Transformation):::logic
            
            LogicCore -->|Directs| Flow
            Flow -->|Performs| Work
        end
        
        %% CONNECTION 2: ELECTROMAGNETISM
        Work ==>|Electromagnetism: Purity| Structure
        
        %% PHASE 3: LIFE
        subgraph P3 [Phase 3: ORGANIZATION / LIFE]
            Structure(Structure):::org
            Module(Module):::org
            Context(Bounded Context):::org
            
            Structure -->|Organizes| Module
            Module -->|Protects| Context
        end
        
        %% CONNECTION 3: GRAVITY
        Context ==>|Gravity: Lifecycle| Runtime
        
        %% PHASE 4: REALITY
        subgraph P4 [Phase 4: EXECUTION / COSMOS]
            Runtime(Runtime):::exec
            Container(Container):::exec
            Cloud(The Cloud):::exec
            
            Runtime -->|Deploys to| Container
            Container -->|Runs in| Cloud
        end
    end
    
    %% ANTIMATTER WARNING
    subgraph VOID [The Void]
        Antimatter(Antimatter / Impossible):::void
        Antimatter -.->|Destabilizes| P2
        Antimatter -.->|Corrupts| P3
    end
```

**The 4 Fundamental Forces:**
1.  **Strong Force:** Binds Data into Logic.
2.  **Electromagnetism:** Transfers Energy (Work) into Structure.
3.  **Weak Force:** Defines the Boundaries of Organization.
4.  **Gravity:** Anchors the Abstraction to Reality (Execution).
"""

    # Create the Node
    unified_node = {
        "id": "unified_theory_diagram",
        "type": "text",
        "text": unified_content,
        "x": -200,      # Centered roughly
        "y": -6200,     # Top of the canvas ("The Big Bang")
        "width": 2000,
        "height": 1600,
        "color": "6"    # Purple/Theory color
    }
    
    # Remove existing if present to avoid dupes
    nodes = [n for n in nodes if n['id'] != 'unified_theory_diagram']
    nodes.append(unified_node)
    data['nodes'] = nodes
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
        
    print("Success: Injected 'unified_theory_diagram' at x=-200, y=-6200.")

if __name__ == "__main__":
    inject_unified("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
