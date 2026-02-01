<!-- [MermaidChart: 1fc253e5-a686-4af3-a904-ce0c53d88c41] -->
<!-- [MermaidChart: 1fc253e5-a686-4af3-a904-ce0c53d88c41] -->
<!-- [MermaidChart: a47bb63c-d2f8-49cc-b8a1-601fc599e954] -->
<!-- [MermaidChart: 7b83b196-2f7f-4521-bb71-b2652aa088dc] -->
```mermaid
flowchart LR
    A[User runs collider full] --> B[src/core/output_generator.py]
    B --> C[tools/visualize_graph_webgl.py]
    C --> D[Load template.html]
    C --> E[Load styles.css]
    C --> F[Load app.js]
    C --> G[Engines and tokens to config]
    D --> H[Assemble HTML]
    E --> H
    F --> H
    G --> H
    H --> I[Output HTML]
    I --> J[Browser parses DOM]
    I --> K[Browser runs JS]
    J --> L[DOM elements exist only if in template.html]
    K --> M[JS getElementById uses expected IDs]
    M --> N{ID exists?}
    N -- yes --> O[Feature renders and works]
    N -- no --> P[Feature missing or inert]
```
