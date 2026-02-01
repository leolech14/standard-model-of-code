# IEEE Core Vocabulary for SMC

> **Status:** DEFINITIVE PRE-EXISTING MAP
> **Source:** IEEE SEVOCAB (ISO/IEC/IEEE 24765)
> **Purpose:** Foundation for ALL SMC terminology

---

## SYSTEM

> "combination of interacting elements organized to achieve one or more stated purposes"
> — ISO/IEC 25000:2014

Alternative definitions:
- "something of interest as a whole or as comprised of parts"
- "interacting combination of elements to accomplish a defined objective"
- "arrangement of parts or elements that together exhibit a stated behavior or meaning that the individual constituents do not"
- "set of interrelated elements considered in a defined context as a whole and separated from their environment"

**SMC Connection:** Foundation for PROJECTOME, CODOME, CONTEXTOME partitions.

---

## MODULE

> "program unit that is discrete and identifiable with respect to compiling, combining with other units, and loading"

Alternative definitions:
- "logically separable part of a program"
- "independent information unit"

**SMC Connection:** Foundation for Atom concept.

---

## COMPONENT

> "entity with discrete structure, such as an assembly or software module, within a system considered at a particular level of analysis"
> — ISO/IEC 25019:2023

Alternative definitions:
- "one part that makes up a system"
- "object that encapsulates its own template"
- "product used as a constituent in an assembled product, system or plant"

**SMC Connection:** Maps to SMC Element and structural decomposition.

---

## SERVICE

> "performance of activities, work, or duties"
> — ISO/IEC/IEEE 12207:2026

Alternative definitions:
- "means of delivering value for the user by facilitating results the user wants to achieve"
- "behavior, triggered by an interaction, which adds value for the service users"
- "output of an organization with at least one activity necessarily performed between the organization and the customer"

**SMC Connection:** Role:Service is IEEE-aligned.

---

## ARCHITECTURE

> "fundamental concepts or properties of an entity in its environment and governing principles for the realization and evolution of this entity and its related life cycle processes"
> — ISO/IEC/IEEE 12207:2026

Alternative definitions:
- "set of rules to define the structure of a system and the interrelationships between its parts"
- "fundamental concepts or properties of a system in its environment and governing principles for the realization and evolution of this system"

**SMC Connection:** LOCUS is an architectural coordinate system. Architecture is the frame.

---

## LAYER

> "partition resulting from the functional division of a software system, where layers are organized in a hierarchy; there is only one layer at each level in the hierarchy; there is a superior/subordinate hierarchical dependency between the functional services provided by software in any two layers"

**SMC Connection:** Extended to Ring (Ω) with formal R0-R4 scale.

---

## LEVEL

> "designation of the coverage and detail of a view"
> — ISO/IEC/IEEE 24765n:2025

**SMC Connection:** Extended to Level (λ) with L-3 to L12 scale.

---

## TIER

> "grouping of process definitions"

**SMC Connection:** Extended to Tier (τ) as abstraction layer.

---

## INTERFACE

> "point at which two or more logical, physical, or both, system elements or software system elements meet and act on or communicate with each other"
> — ISO/IEC/IEEE 12207:2026

**SMC Connection:** Boundary dimension in RPBL metrics.

---

## FUNCTION

> "a task, action, or activity that must be accomplished to achieve a desired outcome"

Alternative definitions:
- "defined objective or characteristic action of a system or component"
- "software module that performs a specific action, is invoked by the appearance of its name in an expression, receives input values, and returns a single value"
- "transformation of inputs to outputs"
- "single-valued mapping"

**SMC Connection:** Foundation for Query role (returns value).

---

## CLASS

> "abstraction of the knowledge and behavior of a set of similar things"

Alternative definitions:
- "static programming entity in an object-oriented program that contains a combination of functionality and data"
- "the set of all Xs satisfying a type"

**SMC Connection:** Foundation for Entity role.

---

## OBJECT

> "encapsulation of data and services that manipulate that data"

Alternative definitions:
- "model of an entity"
- "encapsulation of content units"

**SMC Connection:** Foundation for object-oriented roles.

---

## METHOD

> "code that is executed to perform a service"

Alternative definitions:
- "means for achieving an outcome, output, result, or project deliverable"

**SMC Connection:** Unit of analysis within classes.

---

## ATTRIBUTE

> "inherent property or characteristic of an entity that can be distinguished quantitatively or qualitatively by human or automated means"
> — ISO/IEC 25000:2014

Alternative definitions:
- "observable characteristic or property of the system or system element"
- "unique item of information about an entity"

**SMC Connection:** Foundation for Getter role (property accessor).

---

## PROPERTY

> "responsibility that is an inherent or distinctive characteristic or trait that manifests some aspect of an object's knowledge or behavior"

Alternative definitions:
- "attribute of things"

**SMC Connection:** RPBL metrics assess properties.

---

## BEHAVIOR

> "observable activity of a system, measurable in terms of quantifiable effects on the environment whether arising from internal or external stimulus"

Alternative definitions:
- "of an object, a collection of actions with a set of constraints on when they may occur"
- "peculiar reaction of a thing under given circumstances"
- "observable sequence of inputs and outputs for a system"

**SMC Connection:** Distinguishes PARTICLE (exhibits behavior) from WAVE (exhibits meaning).

---

## STATE

> "at a given instant in time, the condition of an object that determines the set of all sequences of actions (or traces) in which the object can participate"

Alternative definitions:
- "condition that characterizes the behavior of a function at a point in time"
- "unique value that represents the stage of progress of software in its execution"
- "condition that characterizes a system, system element, function, or other entity at a point in time"

**SMC Connection:** Foundation for Symmetry states (SYMMETRIC, ORPHAN, PHANTOM, DRIFT).

---

## PROCESS

> "set of interrelated or interacting activities which transforms inputs into outputs"
> — ISO/IEC/IEEE 12207:2026

Alternative definitions:
- "predetermined course of events defined by its purpose or by its effect"
- "collection of steps taking place in a prescribed manner"
- "system of activities, which use resources to transform inputs into outputs"

**SMC Connection:** Lifecycle dimension tracks process phases.

---

## REQUIREMENT

> "statement that translates or expresses a need and its associated constraints and conditions"
> — ISO/IEC/IEEE 12207:2026

Alternative definitions:
- "condition or capability that is necessary to be present in a product, service, or result to satisfy a business need"
- "need or expectation that is stated, generally implied, or obligatory"
- "provision that conveys criteria to be fulfilled"

**SMC Connection:** Purpose Field formalizes requirements as vector field.

---

## VALIDATION

> "confirmation, through the provision of objective evidence, that the requirements for a specific intended use or application have been fulfilled"
> — ISO/IEC 25000:2014

Alternative definitions:
- "process of providing evidence that the system, software, or hardware and its associated products satisfy requirements allocated to it"
- "assurance that a product, service, or system meets the needs of the customer and other identified stakeholders"

**SMC Connection:** Source for Validator role. "Are we building the RIGHT thing?"

---

## VERIFICATION

> "confirmation, through the provision of objective evidence, that specified requirements have been fulfilled"
> — ISO/IEC 25000:2014

Alternative definitions:
- "evaluation of whether or not a product, service, or system complies with a regulation, requirement, specification, or imposed condition"

**SMC Connection:** Source for Asserter role. "Are we building the thing RIGHT?"

---

## TEST

> "activity in which a system or component is executed under specified conditions, the results are observed or recorded, and an evaluation is made of some aspect of the system or component"
> — ISO/IEC 25051:2014

**SMC Connection:** Symmetry verification requires testing.

---

## ABSTRACTION

> "view of an object that focuses on the information relevant to a particular purpose and ignores the remainder of the information"

Alternative definitions:
- "process of suppressing irrelevant detail to establish a simplified model"

**SMC Connection:** Tier (τ) measures abstraction level.

---

## ENCAPSULATION

> "software development technique that consists of isolating a system function or a set of data and operations on those data within a module and providing precise specifications for the module"

Alternative definitions:
- "concept that access to the names, meanings, and values of the responsibilities of a class is entirely separated from access to their realization"
- "idea that a module has an outside that is distinct from its inside, that it has an external interface and an internal implementation"

**SMC Connection:** Boundary dimension in RPBL.

---

## COUPLING

> "manner and degree of interdependence between software modules"

Alternative definitions:
- "strength of the relationships between modules"
- "measure of how closely connected two routines or modules are"

**SMC Connection:** Ring (Ω) measures dependency coupling.

---

## COHESION

> "manner and degree to which the tasks performed by a single software module are related to one another"

Alternative definitions:
- "measure of the strength of association of the elements within a module"

**SMC Connection:** Responsibility dimension in RPBL measures cohesion.

---

## DESIGN

> "specification of system elements and their relationships, that is sufficiently complete to support a compliant implementation of the architecture"
> — ISO/IEC/IEEE 12207:2026

**SMC Connection:** Design is the WAVE realm (planning). Implementation is PARTICLE realm.

---

## The Pattern

Every IEEE definition above represents **decades of consensus**. SMC doesn't replace these - it:

1. **USES** them where exact match (service, repository, validation)
2. **EXTENDS** them where formalization needed (layer → Ring, level → Level)
3. **ADDS** where IEEE lacks (LOCUS, CODOME, Purpose Field)

---

*This is Layer 0. Everything SMC does builds on this.*
