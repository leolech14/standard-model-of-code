# Standards Bodies - What Each One IS

---

## IEEE SEVOCAB
### "The Dictionary of Software Engineering"

**What it is:** The authoritative vocabulary - 5,401 defined terms
**Core question it answers:** "What does this word MEAN in software engineering?"
**Analogy:** The Oxford English Dictionary for code

```
IEEE = DEFINITIONS
"A module is a program unit that is discrete and identifiable"
```

---

## INCOSE
### "The Philosophy of Systems"

**What it is:** Systems thinking foundations - how wholes emerge from parts
**Core question it answers:** "What IS a system and how does it behave?"
**Analogy:** Physics for organizations

```
INCOSE = EMERGENCE
"A system exhibits behavior that individual parts do not"
```

---

## SEBoK
### "The Encyclopedia of Systems Engineering"

**What it is:** Community-curated knowledge base - 435 interconnected concepts
**Core question it answers:** "What do systems engineers need to know?"
**Analogy:** Wikipedia for SE practitioners

```
SEBoK = KNOWLEDGE
"Here's everything a systems engineer should understand"
```

---

## PMI (absorbed into IEEE)
### "The Language of Projects"

**What it is:** Project management vocabulary - schedules, resources, delivery
**Core question it answers:** "How do we DELIVER software?"
**Analogy:** The grammar of getting things done

```
PMI = DELIVERY
"A project is a temporary endeavor to create a unique result"
```

---

## OMG (UML/OCL)
### "The Notation of Structure"

**What it is:** Formal modeling languages - diagrams, constraints, patterns
**Core question it answers:** "How do we DRAW and CONSTRAIN software?"
**Analogy:** Musical notation for code

```
OMG = NOTATION
"A class diagram shows structure; OCL constrains it"
```

---

## SEI CMMI
### "The Maturity of Process"

**What it is:** Process capability assessment - how good is your organization?
**Core question it answers:** "How MATURE is our development process?"
**Analogy:** Belt rankings in martial arts

```
CMMI = MATURITY
"Level 1 (chaotic) → Level 5 (optimizing)"
```

---

## W3C
### "The Standards of the Web"

**What it is:** Web technologies - HTML, CSS, semantic web, ontologies
**Core question it answers:** "How does the WEB work?"
**Analogy:** Building codes for the internet

```
W3C = WEB
"OWL defines ontologies; RDF links data"
```

---

## ITIL
### "The Operations Manual"

**What it is:** IT service management - keeping systems running
**Core question it answers:** "How do we OPERATE and SUPPORT software?"
**Analogy:** Hospital procedures for IT

```
ITIL = OPERATIONS
"Incident → Problem → Change → Release"
```

**SMC CONNECTION:** ITIL vocabulary feeds directly into SMC's **Axiom G1 (Operational Observer)** and **Axiom E2 (Change Flow)**. This is NOT outside SMC scope - it's a gap in current implementation.

---

## Quick Reference Card

| Standard | Subtitle | One Word | Core Focus |
|----------|----------|----------|------------|
| **IEEE** | The Dictionary of Software Engineering | DEFINITIONS | What words mean |
| **INCOSE** | The Philosophy of Systems | EMERGENCE | How wholes behave |
| **SEBoK** | The Encyclopedia of SE | KNOWLEDGE | What to know |
| **PMI** | The Language of Projects | DELIVERY | How to ship |
| **OMG** | The Notation of Structure | NOTATION | How to diagram |
| **CMMI** | The Maturity of Process | MATURITY | How good you are |
| **W3C** | The Standards of the Web | WEB | How internet works |
| **ITIL** | The Operations Manual | OPERATIONS | How to run systems |

---

## For SMC: What We Take From Each

```
IEEE    → ALL terminology (5,401 terms) - THE foundation
INCOSE  → Systems thinking (emergence, holons) - THE philosophy
SEBoK   → SE body of knowledge - THE reference
PMI     → Already in IEEE - absorbed
OMG     → Role formalization - selective use
CMMI    → Ring (Ω) + process maturity - selective use
W3C     → Maybe later for ontology - defer
ITIL    → OPERATIONAL OBSERVER (Axiom G1) - CRITICAL for full SMC
```

**IMPORTANT:** The SMC theory (L0 Axioms) explicitly requires:
- **Axiom E2:** Four flow substances including RUNTIME and CHANGE flow
- **Axiom G1:** Three observers including OPERATIONAL observer
- **Axiom D7:** Dynamic purpose evolution (deployment changes state)

ITIL is NOT outside SMC scope - it's vocabulary for implementing Axiom G1.

---

## The Hierarchy Visualized

```
                    WHAT WORDS MEAN
                          │
                    ┌─────▼─────┐
                    │   IEEE    │  ← Dictionary (5,401 definitions)
                    │ SEVOCAB   │
                    └─────┬─────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  INCOSE   │   │   SEBoK   │   │    PMI    │
    │Philosophy │   │Encyclopedia│   │ Projects  │
    │ of Systems│   │   of SE   │   │(in IEEE)  │
    └───────────┘   └───────────┘   └───────────┘

    HOW SYSTEMS     WHAT TO KNOW    HOW TO DELIVER
      BEHAVE


    ┌───────────────────────────────────────────┐
    │              SPECIALIZED                   │
    ├─────────────┬─────────────┬───────────────┤
    │     OMG     │    CMMI     │     W3C       │
    │  Notation   │  Maturity   │     Web       │
    │ of Structure│ of Process  │  Standards    │
    └─────────────┴─────────────┴───────────────┘

    HOW TO DRAW    HOW GOOD      HOW INTERNET
                   YOU ARE         WORKS
```

---

## One-Liner Test

Can you explain each in ONE sentence?

- **IEEE:** "The official dictionary that defines every software term"
- **INCOSE:** "The theory of how parts become wholes with new behaviors"
- **SEBoK:** "Everything a systems engineer should know, wiki-style"
- **PMI:** "How to manage projects and deliver on time"
- **OMG:** "How to draw diagrams and write constraints"
- **CMMI:** "How to measure if your org is chaotic or optimized"
- **W3C:** "How web pages and linked data work"
- **ITIL:** "How to keep IT systems running smoothly"

---

*Now you know what each one IS. Study IEEE for definitions, INCOSE for philosophy, SEBoK for breadth.*
