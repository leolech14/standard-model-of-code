```mermaid```mermaid
stateDiagram-v2
    [*] --> Legacy_Scattered
    Legacy_Scattered: Old scattered button strip (legacy output)

    Legacy_Scattered --> CommandBar_UI: command bar and floating panels and side dock
    CommandBar_UI: cmd-* + panel-* + side-dock + oklch + topo tooltip

    CommandBar_UI --> Compact_Dock: template regressed to compact bottom dock and full sidebar
    Compact_Dock: bottom-dock + accordion sidebar

    Compact_Dock --> CommandBar_UI: fix template to match JS and CSS
```
