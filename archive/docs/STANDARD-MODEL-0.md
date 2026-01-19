# THE STANDARD MODEL OF CODE
**Grand Unified Theory (GUT) - Entity Relationship Model**

```mermaid
erDiagram
  UNIVERSE ||--|{ PHASE : manifests
  PHASE ||--|| REGION : correlates_to
  REGION ||--|{ HADRON : classifies
  HADRON ||--o{ SUBHADRON : instantiated_as
  QUARK ||--|{ HADRON : composes
  FORCE ||--|{ PHASE : governs
  LAW ||--o{ IMPOSSIBLE : defines
  HADRON ||--o{ IMPOSSIBLE : participates_in

  UNIVERSE {
    string name "The Code Universe"
    int dimensions "4"
    string origin "Big Bang"
  }

  PHASE {
    int sequence
    string name "Matter|Energy|Life|Reality"
    string analogy "Physics|Thermodynamics|Biology|Cosmology"
  }

  REGION {
    string code "DATA|LOGIC|ORG|EXEC"
    string color "Blue|Red|Green|Yellow"
    string focus "State|Flow|Structure|Runtime"
  }

  HADRON {
    string name "Integer|LoopFor|Class|Container..."
    string type "Particle"
    string stability "Stable"
    int mass
  }

  SUBHADRON {
    uuid id
    string specific_name
    string file_location
    int line_number
    string content_snippet
  }

  QUARK {
    string flavor "Up|Down|Charm|Strange|Top|Bottom"
    string charge
    string spin
  }

  FORCE {
    string name "Strong|Electromagnetism|Weak|Gravity"
    string carrier "Gluon|Photon|W_Boson|Graviton"
    string effect "Binding|Transformation|Boundary|Anchoring"
  }

  LAW {
    int id
    string name "Law of Conservation|Law of Entropy..."
    string description
    bool is_immutable
  }

  IMPOSSIBLE {
    string name "Antimatter"
    string description "Forbidden Combinations"
    string severity "Catastrophic"
  }
```

## Entity Dictionaries

### **PHASE**
The four fundamental states of code existence, parallel to physical phases of matter.
- **Matter (Data):** Static information.
- **Energy (Logic):** Kinetic transformation.
- **Life (Organization):** Negentropic structure.
- **Reality (Execution):** The observable universe.

### **REGION**
The spatial domains where Hadrons reside.
- **DATA:** Bits, Primitives, State.
- **LOGIC:** Control Flow, Operations, Algorithms.
- **ORG:** Classes, Modules, files, directories.
- **EXEC:** Containers, Threads, Processes.

### **HADRON**
The 96 stable composite particles that make up all software.
Examples: `Integer`, `String`, `LoopFor`, `IfBranch`, `Class`, `Service`, `DockerContainer`.

### **FORCE**
The interactions that bind the universe together.
1.  **Strong Force:** Binds Data into Logic (Responsibility).
2.  **Electromagnetism:** COMPOSES Logic into Organization (Purity/Design).
3.  **Weak Force:** BOUNDARIES between contexts (Encapsulation).
4.  **Gravity:** ANCHORS Organization to Execution (Deployment).
