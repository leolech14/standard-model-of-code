%% Agent Initiation Process
%% This diagram captures the required initiation flow for this repo.
flowchart TD
    A[Start Session] --> B[Read AGENT_KERNEL.md]
    B --> C{Boot Sequence}
    C -->|Option A| D[Run ./tools/agent_boot.sh]
    C -->|Option B| E[Manual Boot]
    E --> F[Read docs/agent_school/INDEX.md]
    F --> G[Read docs/agent_school/REPO_FACTS.md]
    G --> H[Read docs/agent_school/WORKFLOWS.md]
    H --> I[Read docs/agent_school/DOD.md]
    D --> J[Complete Boot Checklist]
    I --> J
    J --> K[Identify Basics: repo root, branch, git status]
    J --> L[Find Commands: test/lint/format/build/run]
    J --> M[Acknowledge Policies]
    K --> N[Output INITIATION_REPORT JSON]
    L --> N
    M --> N
    N --> O[Begin Task: SCAN -> PLAN -> EXECUTE -> VALIDATE -> COMMIT]
