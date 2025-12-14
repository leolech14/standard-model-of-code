# 🌌 Standard Model for Computer Language (Spectrometer v12)

> **"We are code particle physicists. We map the fundamental sub-atomic pieces of modern software."**

Spectrometer is not just a linter. It is a **Particle Accelerator for your Codebase**. It smashes your repository against a wall of static analysis and LLM inference to reveal the hidden structure of your software—the "Standard Model" of your system.

---

## 🗺️ What We Have Mapped So Far

We currently detect **22 Fundamental Particles** of software architecture. These are the building blocks of the digital universe.

```mermaid
graph LR
    %% Palette: Scientific & Professional
    classDef domain fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b;
    classDef app fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#00695c;
    classDef interface fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#4a148c;
    classDef infra fill:#eceff1,stroke:#37474f,stroke-width:2px,color:#37474f;
    classDef root fill:#263238,stroke:#000,stroke-width:4px,color:#fff;

    Root((STANDARD<br/>MODEL)):::root

    %% Domain Layer
    subgraph Domain ["Domain Core (The 'Nucleus')"]
        direction TB
        Entity:::domain
        ValueObject:::domain
        AggregateRoot:::domain
        DomainService:::domain
        Policy:::domain
        Specification:::domain
        Factory:::domain
    end

    %% Application Layer
    subgraph App ["Application (The 'Electrons')"]
        direction TB
        UseCase:::app
        Service:::app
        AppService[ApplicationService]:::app
        Command:::app
        Query:::app
        EventHandler:::app
    end

    %% Interface Layer
    subgraph Interface ["Interface (The 'Fields')"]
        direction TB
        Controller:::interface
        DTO:::interface
        Mediator:::interface
        Observer:::interface
    end

    %% Infrastructure Layer
    subgraph Infra ["Infrastructure (The 'Gravitons')"]
        direction TB
        Repository:::infra
        RepoImpl[RepositoryImpl]:::infra
        Projection:::infra
        ReadModel:::infra
    end

    %% Connections
    Root --- Domain
    Root --- App
    Root --- Interface
    Root --- Infra
```

We map these particles, measure their "Mass" (Lines of Code), "Charge" (Dependencies), and "Spin" (Complexity), and generate a 3D model of your codebase.

---

## ⚡ The "One Button" Philosophy

You don't need a PhD in Physics to use this. You press one button, and we do the rest.

### 1. Analyze Everything

The **Analyze** command runs our complete hybrid pipeline:
1.  **Static Extraction**: Deterministically finds classes and functions.
2.  **Semantic Inference**: Uses LLMs (if enabled) to classify particles ensuring < 0.1% hallucination rate.
3.  **God Class Detection**: Scans for "Antimatter" (oversized, dangerous components).

```bash
python3 cli.py analyze /path/to/your/repo
```

*That's it.*

### 2. Check System Health

Verify that the particle accelerator is calibrated and ready to fire.

```bash
python3 cli.py health
```

### 3. Full Audit

Prove the entire pipeline works end-to-end on your code.

```bash
python3 cli.py audit /path/to/your/repo
```

---

## 🏗️ Technical Architecture

Our "Standard Model" is built on a **Hybrid Static+LLM Pipeline**:

1.  **Structural Truth (The "What")**:
    *   We use **Tree-Sitter** and **Regex** to build an immutable Graph of Truth. If a file exists, we know it. If a class is defined, we map it.
    *   *Zero Hallucinations allowed here.*

2.  **Semantic Role (The "Why")**:
    *   We overlay semantic meaning. Is this class a `Repository`? Is that function a `UseCase`?
    *   We use heuristic patterns first.
    *   If unsure (Confidence < 55%), we escalate to a **Local LLM** (Ollama/Qwen) to examine the code and make a determination.

3.  **Antimatter Detection**:
    *   We scan for **God Classes**—components with too much mass and responsibility. These are the black holes of your system.

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

*(Optional) For Hybrid Mode semantic inference, ensure [Ollama](https://ollama.ai) is running.*

---

*Probing the deep structure of code.*
