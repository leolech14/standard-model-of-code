# Research: What are the requirements for publishing a novel theoretical framework in software engineering acade...

> **Date:** 2026-02-01 02:49:37
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:6da0e055b839ef65b8c6946e6761ac7979dd74da8de1b91e62305a55dac5a778`
> **Raw JSON:** `raw/20260201_024937_what_are_the_requirements_for_publishing_a_novel_t.json`

---

## Query

What are the requirements for publishing a novel theoretical framework in software engineering academic venues (ICSE, FSE, TSE, TOSEM)? Specifically:

1. What distinguishes a 'theory paper' from a 'tool paper' in SE research?
2. What level of formalization is required (category theory, type theory, formal proofs)?
3. What empirical validation is expected for theoretical contributions?
4. How do successful SE theory papers cite and position against existing work?
5. What are common rejection reasons for theory papers that are 'almost there'?

I have a framework called 'Standard Model of Code' that:
- Has formal axioms (15+) organized in layers
- Defines 167 'atom' types for code classification
- Uses 8-dimensional classification
- Has a 16-level holarchy (like physics scales)
- Includes mathematical notation for coordinates
- Has working implementation (static analyzer)

What specific gaps would prevent this from being publishable at top venues?

---

## Response

# Publishing Requirements for Theoretical Frameworks in Software Engineering: A Comprehensive Analysis of ICSE, FSE, TSE, and TOSEM Standards

This report provides an exhaustive examination of the publication requirements for novel theoretical frameworks in premier software engineering academic venues, with specific attention to the distinctions between theory and tool contributions, formalization expectations, empirical validation norms, and structural positioning strategies that distinguish publishable work from submissions that face rejection despite significant effort. Based on current conference and journal guidelines, community feedback on review practices, and analysis of successful theoretical contributions in the field, this analysis identifies critical gaps that could prevent publication and provides concrete recommendations for frameworks such as the "Standard Model of Code" that seeks to establish formal abstractions for code classification and analysis.

## Understanding the Landscape of Theory Contributions in Software Engineering Venues

### The Distinction Between Theory Papers and Tool Papers in Contemporary SE Research

Software engineering research has traditionally operated with a somewhat blurred boundary between theoretical contributions and tool-based contributions, a distinction that has become increasingly important as major venues attempt to clarify their evaluation criteria. The International Conference on Software Engineering (ICSE), the Foundations of Software Engineering (FSE) conference, and the associated journals IEEE Transactions on Software Engineering (TSE), and ACM Transactions on Software Engineering and Methodology (TOSEM) each maintain specific expectations about what constitutes a valid theoretical contribution versus a tool contribution, though these distinctions are not always explicitly formalized in submission guidelines[1][13][19].

A theory paper in the contemporary software engineering context is fundamentally distinguished by its focus on establishing generalizable abstractions, principles, or formal models that explain relationships among software engineering phenomena[3]. Theory papers typically introduce new concepts, define formal relationships between existing concepts, establish axioms that govern software engineering activities, or present mathematical models that enable prediction or verification of software properties. The defining characteristic of a theory paper is that the primary contribution is intellectual and mathematical rather than technological, though the paper may describe implementation or validation of the theoretical ideas[3]. A theory paper might establish a formal semantics for a class of programs, define a hierarchy of code abstractions, propose axioms for software quality, or introduce mathematical frameworks for reasoning about software evolution.

In sharp contrast, a tool paper is primarily focused on the implementation and demonstration of a software artifact that embodies or applies theoretical ideas[26]. Tool papers emphasize the engineering aspects of translating theory into working systems, demonstrating how the artifact functions in practice, and validating that the tool produces useful results for practitioners or researchers. While tool papers may include theoretical elements, their primary value proposition lies in the artifact itself rather than in novel theoretical abstractions[26]. The evaluation of tool papers centers on whether the tool is usable, whether it addresses genuine problems, and whether practitioners can effectively employ it[26].

This distinction has profound implications for what kinds of evidence and validation are required. A theory paper must demonstrate that its formal framework is rigorous, internally consistent, and applicable to a meaningful class of problems, but it is not required to implement a production-grade tool[9]. Indeed, many successful theory papers in top venues present their ideas through mathematical formalism, illustrative examples, and conceptual descriptions without necessarily providing a complete software implementation. Conversely, a tool paper that makes only incremental improvements to existing tools or lacks clear theoretical novelty will face criticism even if the tool is well-engineered[26].

The user's "Standard Model of Code" framework appears to straddle this boundary in potentially problematic ways. It includes 15+ formal axioms, mathematical notation including 8-dimensional coordinates, a 16-level holarchy analogous to physics' organizational scales, and 167 atom types for code classification. These elements suggest a theoretical framework of considerable ambition. However, the presence of "working implementation (static analyzer)" indicates that the contribution has been operationalized as a tool. This dual nature requires careful positioning to avoid the risk of being evaluated simultaneously against both standards—which could result in rejection if the work is deemed insufficiently rigorous as pure theory or insufficiently novel as a tool contribution.

### Historical Evolution of Theory Publication at Major Venues

The publication landscape for theoretical work in software engineering has shifted considerably over the past two decades[12][44]. Earlier eras of the field saw more acceptance of theoretical papers that were primarily conceptual with limited empirical validation, reflecting the immaturity of software engineering as a discipline. However, as the field has developed and venues have accumulated thousands of submissions annually, there has been a documented shift toward what some community members characterize as an over-emphasis on novelty and empirical rigor at the expense of theoretical depth[12][44][55].

Recent community surveys and discussions have revealed significant tensions in how venues evaluate theoretical contributions. While venues officially value novelty and theoretical contribution, there is substantial evidence that reviewers and program committees struggle to balance the theoretical merit of novel frameworks against the practical and empirical validation that contemporary venues increasingly expect[12][44][55]. This creates a particular challenge for frameworks that are theoretically comprehensive but for which extensive empirical validation remains incomplete or ongoing. Some community members have characterized this dynamic as a "novelty-vicious cycle" where new theoretical ideas face resistance because they lack the extensive empirical validation that established approaches have accumulated, yet the empirical validation itself requires resources and time that may not be available during the initial development phase[12][44].

## Formalization Requirements and Mathematical Frameworks in Contemporary SE Theory

### What Constitutes Adequate Formalization for Publication

The question of how formally rigorous a theoretical framework must be to meet publication standards at premier venues does not have a single, uniformly applied answer across ICSE, FSE, TSE, and TOSEM. However, analysis of review guidelines and published theory papers reveals several levels of formalization that are considered acceptable, each with different associated challenges and advantages[3][15][18].

At the highest level of formalization, theory papers employ complete formal specification languages with accompanying proof systems and verification infrastructure[3][15][18]. These approaches, exemplified by axiomatic semantics and formal methods research in programming language semantics, provide the strongest possible guarantee of internal consistency and logical soundness[15][18]. Papers using this level of formalization typically employ mathematical logic, predicate calculus, or specialized proof systems. The advantage of this approach is that claims about the framework can be proven rigorously. The disadvantage is the steep learning curve required for both authors and reviewers, the time required to develop complete formal specifications, and the risk that overly formal presentations may obscure insights that could be understood through less formal exposition[3][15].

At an intermediate level, theory papers employ structured mathematical notation without necessarily providing complete formal proofs or employing specialized logic systems. This approach, common in contemporary software engineering theory papers, involves clearly defining the domain of discourse, establishing mathematical notation for key concepts, specifying relationships through equations or formal definitions, and reasoning about properties through rigorous mathematical argumentation even without formal proof systems[3][15]. This level of formalization allows authors to make precise claims while remaining accessible to a broader audience of software engineers who may not have specialized training in formal methods[3][15].

At a more informal level, theory papers establish conceptual frameworks through well-organized definitions, examples, and logical reasoning without explicit mathematical notation throughout[3]. These papers establish clear taxonomies, define concepts carefully, describe relationships, and reason about implications. The advantage is greater accessibility; the disadvantage is increased risk of imprecision or unstated assumptions[3].

For a framework like the "Standard Model of Code," the formalization level matters significantly. The presence of 15+ formal axioms and 8-dimensional coordinates suggests an attempt at the intermediate level—establishing mathematical structure without necessarily providing complete formal proofs[3]. This is reasonable for ICSE, FSE, TSE, and TOSEM, where not all theory papers employ the highest level of formalization. However, the specificity required by these venues means that if axioms are proposed, they must be mathematically sound and internally consistent[3]. Each of the 15+ axioms should be clearly stated using consistent notation, and the relationships between axioms should be explicit. The 8-dimensional classification and 167 atom types require clear, formal definitions that allow readers to understand exactly what constitutes each dimension and each atom type, and how these categories are exhaustively defined and mutually exclusive[3].

### Recent Work on Formalizing Software Engineering Concepts

A particularly relevant recent paper in the search results directly addresses the question of formalizing software engineering itself[3]. This work proposes developing a comprehensive theory of software engineering using object-oriented modeling and formal methods, with the goal of creating an ontology of core concepts including project, milestone, code module, test, and other fundamental abstractions[3]. The paper acknowledges that while SWEBOK (the Software Engineering Body of Knowledge) has documented much known understanding, it remains primarily descriptive rather than formal, and lacks the kind of mathematical rigor that would enable systematic verification[3].

The authors of this recent formalization work argue that a theory of software engineering should follow principles including: (1) descriptive rather than prescriptive focus—describing what software engineering concepts are rather than how they should be used; (2) focus on isolating and describing key abstractions; (3) use of formal logical properties enabling verification by program provers; and (4) incremental development taking advantage of reuse[3]. These principles are directly applicable to evaluating the "Standard Model of Code." The framework should clarify whether it is primarily descriptive (defining what code structure is and what classifications are valid) or prescriptive (recommending how code should be organized). It should isolate what it considers the key abstractions of code structure. It should employ formal logical properties in its axioms that could potentially be verified by automated tools.

The formalization paper also emphasizes that the field currently lacks widely-accepted formal frameworks for software engineering concepts, and that developing such frameworks requires community effort and builds on existing work like SEMAT (Semantic Execution Model and Terminology)[3]. This context is important because it means that a comprehensive formal framework for code classification would be addressing a genuine gap in the field, but it also means that such a framework faces the challenge of not having established standards or conventions for how such formalizations are typically structured and presented.

### Mathematical Approaches: Category Theory, Type Theory, and Axiomatic Methods

The search results provide exposure to several mathematical approaches that could be employed for formalizing software engineering concepts[3][14][17][38]. Understanding which approaches are appropriate for which kinds of frameworks is essential for positioning theoretical contributions effectively.

**Category Theory**: Several of the search results discuss category theory as a potential mathematical foundation for software engineering[3][14][17]. Category theory is described as "a general theory of algebraic structures and systems of structures" that "has come to occupy a central position in contemporary mathematics and theoretical computer science"[17]. The potential application of category theory to software engineering stems from its ability to reveal how different types of structures are related to one another and to provide structure-preserving maps (morphisms) between concepts[14][17]. For software engineering specifically, category theory could be employed to reason about how different code structures relate to one another, how abstractions at different levels of a hierarchy correspond, and how transformations preserve structural properties[14][17].

However, the search results also emphasize a critical limitation: "application of the theory requires specific and advanced mathematical skills, typically not possessed by engineers," and "to date, category theory has provided little impact on engineering practice"[17]. This suggests that while category theory might provide elegant mathematical foundations for a code classification framework, it carries significant risk of making the framework inaccessible to both reviewers and potential users in the software engineering community. The use of category theory in a framework should be justified by necessity rather than mathematical elegance—that is, the framework should employ category theory because other mathematical approaches cannot express the needed concepts, not simply because category theory is more rigorous or mathematically sophisticated.

**Type Theory and Formal Semantics**: The search results discuss type theory as a foundation for programming language semantics[15][18][27][49]. Type theory provides mechanisms for classifying programs and program expressions into categories (types) and establishing rules about which operations are valid on which types[18][27]. This approach is particularly relevant for code classification frameworks because code can be understood as having different types of structures (functions, classes, modules, etc.) with different properties and relationships[49].

The formalization of programming language semantics using axiomatic semantics involves defining the meaning of programs through logical assertions about their behavior[15][18]. Axiomatic semantics uses a precondition-postcondition framework where the meaning of a code fragment is captured by establishing what must be true before executing the code and what must be true after executing it[15][18][49]. This approach has proven effective for reasoning about program correctness and could potentially be adapted for reasoning about code structure and classification.

**Axiomatic Methods**: The "Standard Model of Code" framework explicitly employs axioms, which aligns it with axiomatic approaches to formalization[3][15]. In mathematical axiomatic systems, axioms are foundational propositions taken to be true, from which theorems can be derived through logical inference[3][15]. The quality and appropriateness of an axiomatic framework depends critically on several factors: (1) the axioms should be independent—no axiom should be derivable from the others; (2) the axioms should be consistent—they should not contradict one another; (3) the axioms should be complete enough to characterize the domain—important properties of the domain should be expressible using the axioms; and (4) the axioms should be parsimonious—there should not be unnecessary axioms[3].

For a framework proposing 15+ axioms organizing code classification, peer reviewers will examine whether the axioms meet these criteria. A particular risk is that reviewers might find that some proposed axioms are redundant (derivable from other axioms), which would suggest either that the framework is not as comprehensive as claimed or that it includes unnecessary complexity. Alternatively, reviewers might find that important properties of code classification are not captured by the proposed axioms, suggesting the framework is incomplete.

## Empirical Validation Expectations for Theoretical Frameworks

### What Venues Expect in Terms of Empirical Validation

A critical question for any theoretical framework seeking publication at premier venues is what empirical validation is required[10][25][28]. The answer depends on what the framework claims and how novelty is positioned, but analysis of ICSE and FSE review guidelines reveals important patterns[25][28].

According to ICSE 2023 and 2022 review guidelines, soundness is evaluated "relative to claimed research contributions"[25][28]. This principle is crucial: if a paper claims only to introduce a formal framework with illustrative examples, the empirical validation bar is lower than if the paper claims that the framework predicts software quality or that following the framework's recommendations improves code maintainability[25][28]. The guidelines explicitly state that "a novel idea with great potential can make a very valuable paper even with only preliminary evaluation, whereas an incremental idea might need more support"[25][28].

This creates an important strategic consideration for theoretical frameworks: they should clearly distinguish between what the framework claims and what remains for future work[25][28]. If the "Standard Model of Code" claims only to establish a formal taxonomy and ontology of code structures, empirical validation might consist primarily of demonstrating that the taxonomy can be applied consistently to real code and that it captures important distinctions that practitioners recognize. If, however, the framework claims to enable better software quality analysis, predict defects, or improve developer productivity, the empirical validation requirements increase substantially[25][28].

The ACM SIGSOFT Empirical Standards provide detailed guidance on empirical validation for software engineering research[10]. These standards specify different criteria for different research methodologies—the standards recognize that qualitative case studies, quantitative experiments, and design studies have different empirical requirements[10]. Importantly, the standards explicitly reject certain "invalid criticisms," including criticizing a case study for having "small N" (small number of participants) when case studies by definition study phenomena in depth rather than breadth[10].

For a theoretical framework accompanied by a working implementation (static analyzer), the empirical validation might take several forms. One approach would be a design study demonstrating that the static analyzer implementing the framework can detect certain classes of issues in real code[37][40]. Another would be a case study showing how practitioners use the framework to understand or improve code structure. A third would be a comparative study showing that the framework-based analysis identifies issues that other approaches miss or that the framework's classifications align with classifications that experienced developers make[10].

However, the search results reveal important cautions about over-emphasizing empirical validation at the expense of theoretical novelty[12][44][55]. Recent community discussion has noted that "the excessive focus on rigor and big samples seems to have made it harder to connect with real practitioners"[55] and that reviewers sometimes focus more on evaluation methodology than on the novelty and significance of the theoretical contribution[12][44][55].

### Validation Through Implementation and Case Studies

The presence of a working implementation (static analyzer) for the "Standard Model of Code" framework provides both advantages and challenges for publication[26]. The advantage is that implementation provides concrete evidence that the framework is not merely theoretical but can be operationalized—implementability serves as a form of validation that the framework is well-defined enough to code[26][38]. The challenge is that the paper must then be evaluated partly as a tool paper, and tool papers face particular standards around usability, effectiveness, and comparison to existing approaches[26].

If the framework paper includes the static analyzer implementation, reviewers will ask: Does the analyzer work correctly? Has it been validated against known defects or real-world code? How does its performance compare to existing static analyzers[37][40]? These are tool evaluation questions, not pure theory questions. If the paper positions primarily as a theoretical contribution and minimizes discussion of the implementation, reviewers may question why implementation was necessary or feel that the paper is incomplete. If the paper positions as both theory and tool, it must meet standards for both, which is more challenging[26].

One effective strategy employed by successful papers in this domain is to carefully separate layers of contribution: a primary contribution focused on the theoretical framework, with secondary contributions focused on implementation and validation[26]. The primary contribution paper establishes the framework, demonstrates its coherence and completeness through examples and logical arguments, and positions it within the existing literature. Implementation and validation details are then secondary, supporting the theoretical contribution but not required to be comprehensive in the initial paper[26].

### The Role of Formal Proofs and Verification

For a theoretical framework in software engineering, reviewers will assess whether and how the framework enables verification[3][38][41]. This does not necessarily mean that the paper must include formal proofs—though it might. Rather, it means assessing whether the framework is sufficiently precise and rigorous that verification through automated or manual means is possible in principle[3][38][41].

Formal methods research demonstrates that complete formal proofs of properties are valuable but not always necessary for publication[3][41]. Many prominent formal methods papers present verification techniques or specifications without providing proofs of correctness in the paper itself; rather, they explain how correctness could be established and potentially cite accompanying mechanized proofs in supplementary materials[3][41]. The key is demonstrating that the framework could, in principle, be verified and that approaches to verification are clear[3].

For the "Standard Model of Code," the question would be: what properties of the framework could be verified, and how? Could an automated tool verify that a given code structure satisfies the framework's classification? Could the axioms be checked for consistency? Could theorems about code structure be proven from the axioms[3]? If the answer to these questions is affirmative and the paper explains the verification approach, this strengthens the framework's positioning as formal and rigorous[3].

## Positioning Against Existing Work and Scholarly Context

### Relating Theory to Prior Theoretical Frameworks

One of the most common reasons that papers face rejection despite significant intellectual content is failure to adequately position the work within existing scholarship[9][25][28][39]. For a theoretical framework in software engineering, this positioning must address several distinct bodies of prior work.

First, the framework should relate to existing formal models of software. The search results reference several prior efforts to formalize software engineering concepts, including SWEBOK, SEMAT, and the recent arXiv paper on formalizing software engineering itself[3]. A paper proposing the "Standard Model of Code" should explicitly address what these prior efforts accomplished, where they fell short, and how the new framework advances beyond them. For example, does SWEBOK establish any axioms for code structure? If so, how do the proposed axioms differ or improve? Does SEMAT provide any classification of code elements? If so, how is the new taxonomy different or more comprehensive[3]?

Second, the framework should relate to existing taxonomies and classification schemes in software engineering. The search results include examples of taxonomies for feature location, software tools, and other domains[20][23]. The paper should discuss whether any existing taxonomies cover similar ground and explain what makes the new classification more rigorous, comprehensive, or useful. The presence of 167 atom types for code classification is substantial—are there existing classification schemes with similar numbers of categories? If so, what advances does this framework offer? If not, is that because existing approaches found 167 categories to be excessive or unnecessarily fine-grained[23]?

Third, the framework should relate to existing work in formal methods, programming language semantics, and mathematical frameworks for computing[3][14][15][18][27]. If the framework employs category theory, type theory, or axiomatic methods, the paper should demonstrate familiarity with how these approaches have been applied in prior work and explain what new insights the application to code classification yields. This is particularly important because category theory and type theory have already been employed in computer science for decades—reviewers will expect the paper to explain what is novel about this particular application[14][17].

### Common Positioning Errors and How to Avoid Them

The search results on paper review in software engineering identify several positioning errors that lead to rejection[9]. One common error is failing to distinguish the contribution from existing work, leading reviewers to conclude that the work has been done before even if it actually advances beyond prior approaches[9]. Another error is over-claiming novelty—proposing that the work addresses a gap that does not actually exist or claiming to be first when similar ideas have been explored[9].

For a framework positioning as the "Standard Model of Code," a particular risk is comparing itself to physics' "Standard Model" in ways that overstate the analogy. Physics' Standard Model was developed over decades by thousands of researchers and has extraordinary predictive power about physical phenomena. Software engineering is vastly more complex and less well-understood theoretically than physics. Positioning a classification framework as the "standard model" of code carries risk of seeming to overstate its significance or scope unless the framework's claims are explicitly bounded and carefully situated[9].

Another positioning error is failing to acknowledge limitations and scope[9][25][28]. Excellent papers typically include explicit discussion of what the framework does and does not address, what kinds of code or software phenomena it applies to, and what assumptions it makes[9][25][28]. For the "Standard Model of Code," this would mean clearly specifying: Does the framework apply to all programming languages or specific ones? Does it address all aspects of code structure or focus on particular dimensions like function-level or class-level structure? Does it address dynamic behavior or only static structure? What assumptions does the framework make about how code is organized[9][25][28]?

## Common Rejection Patterns for Theory Papers "Almost There"

### The Nature of Incompleteness in Theory Papers

The search results include detailed discussion of why papers that are "almost there" still face rejection[9][12][44][55]. Community feedback and review guidelines reveal several patterns. One fundamental issue is that incompleteness in a theoretical framework can manifest in different ways, each of which presents problems[9][12][44][55].

A framework might be incomplete in its formal specification, meaning that while it proposes axioms and structures, these are not fully formalized or some key definitions are left informal[3][9]. Reviewers will judge whether this incompleteness is acceptable (because formalization would be excessive or obscure key insights) or problematic (because the informality prevents verification or makes claims ambiguous). A framework might be incomplete in its scope, meaning it addresses some important phenomena but not others, leaving significant gaps. This is often acceptable if the scope limitations are clearly stated; it becomes problematic when reviewers perceive that the framework claims broader scope than it actually achieves.

A framework might be incomplete in its validation, meaning that while it is theoretically sound, it has not been validated against sufficient real-world examples or has not been tested in practice. This incompleteness is increasingly problematic at contemporary venues, where empirical grounding is increasingly valued. However, the search results reveal tension on this point—some community members argue that requiring extensive validation before publication delays the dissemination of novel theoretical ideas[12][44][55].

A framework might be incomplete in its positioning and presentation, meaning that while the core ideas are sound, the paper does not adequately explain how the framework relates to existing work, does not clarify what the framework claims, or does not present the ideas with sufficient clarity that reviewers and readers can fully understand them[9][25][39].

### Why "Sufficiently Novel" Is Harder to Demonstrate Than It Seems

The search results reveal that demonstrating sufficient novelty for publication at premium venues has become increasingly challenging[12][44][55]. Community feedback indicates that reviewers struggle with assessing whether an incremental advance on existing work is sufficiently novel or whether the work merely extends prior work in minor ways. The guidelines attempt to clarify this by noting that papers should not be rejected "because the novel idea is simple" and that many research advances are necessarily incremental since "most research is, necessarily, advancing previous work"[9][25][28].

However, the practical implementation of this guidance appears inconsistent. Recent community discussion reveals that papers proposing theoretically novel frameworks often face resistance with claims that the ideas are "too simple," "already proposed in some form," or "extending prior work solely with additional details"[12][44][55]. This is particularly problematic for theoretical frameworks because frameworks by their nature build on and organize existing concepts—perfect novelty would be rare. The challenge is distinguishing between a framework that usefully organizes and formalizes existing concepts (valuable) and a framework that merely relabels existing concepts without adding new understanding (not valuable)[12][44][55].

For the "Standard Model of Code" framework, reviewers will ask: Are the 167 atom types for code classification truly novel, or are these existing distinctions already recognized in the literature? Are the 8 dimensions and the 16-level holarchy providing new insight into code structure, or are these pre-existing organizational schemes repackaged? The paper must demonstrate that the formal framework enables understanding or capabilities that existing informal classifications do not provide. It is not enough to say "here is a taxonomy of code structures"—successful theory papers explain why formalizing these structures matters and what becomes possible once they are formalized[12][44][55].

### Specific Rejection Reasons That Apply to Comprehensive Frameworks

The search results provide a list of bad reasons for rejecting papers that help clarify what are legitimate concerns[9]. Several of these explicitly apply to comprehensive theoretical frameworks:

One legitimate concern is "The work is technically correct but pointless—basically a rephrasing of the above. The claims (presuming they are substantiated) wouldn't significantly advance the subject"[9]. A comprehensive code classification framework runs this risk if reviewers perceive that classifying code into 167 categories and 8 dimensions, while possibly correct, does not enable answers to important questions or does not advance practice or theory in meaningful ways. The framework must establish not just that the classification is correct but why practitioners and researchers should care about it[9].

Another legitimate concern is "The motivation isn't explained—it doesn't clearly explain why anyone should care"[9]. If a paper proposes the "Standard Model of Code" without establishing why such a standard model is needed, what problems it solves, or what becomes possible with it, reviewers will reject it regardless of its technical merit[9]. The paper must open by establishing that software engineering faces challenges that require a formal, universally-applicable framework for understanding code structure, and it must explain specifically what those challenges are[9].

A third legitimate concern is "The claims are misleading: the work is over-sold and the authors aren't clear about the limitations, or about the relationship to previous work"[9]. For an ambitious framework proposing to be the "standard" model, there is high risk of overselling. The paper must carefully distinguish between what the framework accomplishes (a formal, comprehensive classification of code structures) and what it does not accomplish (predicting code quality, proving correctness, recommending design patterns, etc.). It must be explicit about what types of code, programming paradigms, or software phenomena the framework does and does not address[9].

## Specific Assessment: The "Standard Model of Code" Framework

### Strengths That Support Publishability

The "Standard Model of Code" framework as described possesses several features that align well with what premier venues seek in theoretical contributions. First, the framework appears to attempt genuine formalization with 15+ formal axioms, which signals serious engagement with mathematical rigor[3]. This addresses a documented gap in the field—the lack of widely-adopted formal frameworks for software engineering concepts[3]. If the axioms are sound, internally consistent, and appropriately scoped, this provides a foundation for peer evaluation and builds on recognized approaches like axiomatic semantics in programming language theory[3][15].

Second, the framework proposes a substantial classification system with 167 atom types organized in 8 dimensions across a 16-level holarchy. If these classifications are rigorously defined, exhaustive (covering all possible code structures), and mutually exclusive (with no ambiguity about which category a given code element belongs to), this could provide genuine value as a comprehensive ontology of code structure. This would address the need for formal, universally-applicable classification systems identified in prior work on taxonomies and formal software engineering frameworks[3][20][23].

Third, the framework includes working implementation as a static analyzer, which provides concrete evidence that the formalism can be operationalized and enables empirical validation. Implementation serves as a kind of proof-of-concept—if the axioms were fundamentally flawed or the classification incoherent, implementing them would likely reveal those problems. The existence of a working implementation suggests the framework is coherent enough to realize in code[26][38].

Fourth, the use of mathematical notation for coordinates and the 16-level holarchy organized analogously to physics' hierarchical organization of scales suggests sophisticated thinking about the structure of the framework. The attempt to capture multiple levels of abstraction and their relationships reflects understanding of complexity theory and systems thinking[32][34][35].

### Critical Gaps and Vulnerabilities

However, the framework as currently described appears to have several significant gaps that would likely lead to rejection at ICSE, FSE, TSE, or TOSEM without substantial additional work:

**Insufficient Justification of Scope and Motivation**: The search results emphasize repeatedly that papers must establish motivation—why anyone should care[9]. The description provided does not establish why a "Standard Model of Code" is needed. What problems does it solve? What current approaches are inadequate? What would become possible with this framework that is not possible now? Without this foundational justification, reviewers will struggle to understand the contribution's significance[9][25].

**Unclear Relationship to Existing Formalizations**: The framework should explicitly address prior work in formalizing software engineering concepts, including SWEBOK, SEMAT, and recent work on formalizing software engineering itself[3]. It is unclear from the description whether the framework builds on these efforts, supersedes them, or addresses a different problem entirely. This positioning is crucial; without it, reviewers may conclude that the framework reinvents existing wheels or fails to acknowledge prior work[9][25].

**Absence of Clear Formalization Details**: While the description mentions "15+ axioms" and "8-dimensional classification," no actual axioms, formal definitions, or dimensional specifications are provided. For a framework emphasizing formalization, this is a critical gap. Peer reviewers need to examine the actual axioms to assess whether they are consistent, complete, and appropriate. Without seeing these details, it is impossible to evaluate the framework's rigor[3][15]. Each axiom should be stated in clear mathematical notation, should be labeled and indexed, and should have accompanying explanation of what it means and why it is necessary[3].

**Undefined Categories and Atom Types**: The 167 "atom types for code classification" require clear, formal definitions. What exactly is an "atom" in this system? How are the boundaries between different atom types defined? The framework must provide either explicit definitions for all 167 types or a clear algorithmic or mathematical procedure for determining what atom types exist and how code elements are classified[3][15]. Without this, the framework cannot be evaluated for completeness, consistency, or utility.

**Unclear Relationship Between Dimensions, Holarchy, and Atom Types**: The description mentions "8-dimensional classification," "16-level holarchy," and "167 atom types," but the relationships between these three organizational schemes are not explained. Does the 8-dimensional space define the atom types? Does the 16-level holarchy create 167 categories at various levels? Is there overlap between how dimensions and holarchy levels organize code structure? Reviewers will need to understand how these three organizational schemes interrelate[3][34][35].

**Inadequate Explanation of Physical Analogy**: The comparison of the framework to physics' Standard Model and hierarchical organization of scales is intriguing but risks being merely metaphorical unless the analogy is rigorously developed. In what specific ways does the framework's organization parallel physics? Does this parallel provide mathematical insights or is it primarily mnemonic? What assumptions about code structure are imported from physics, and are they valid[32][34][35]?

**Missing Empirical Grounding**: While the static analyzer implementation exists, the description provides no information about validation. Can the analyzer correctly classify code according to the framework? Has it been tested on real-world code from diverse domains, programming paradigms, and languages? Do practitioners find the classifications useful? Do the classifications correlate with software quality metrics, developer productivity, or defect rates? Without some empirical grounding—even preliminary—reviewers will question whether the framework addresses real needs or remains purely theoretical[10][25][28][37][40].

**Unclear Scope Limitations**: The framework must clearly specify what it does and does not address. Does it apply to all programming languages or specific ones? Does it classify all aspects of code structure or focus on particular levels (function, class, module, etc.)? Does it apply to object-oriented code, functional code, procedural code, or all paradigms? What about legacy code, generated code, or other special forms? Without clear scope, reviewers will perceive ambiguity or over-claiming[9][25][28].

**Inadequate Discussion of Limitations and Alternatives**: The paper should explicitly acknowledge what the framework does not accomplish. It does not predict code quality, recommend designs, automatically refactor code, or solve any particular software engineering problem directly—it provides a classification system. This is not a weakness if clearly acknowledged, but it becomes a weakness if the paper implies or suggests broader applicability[9][25][28].

## Requirements for Publication: Detailed Recommendations

### Paper Structure and Organization

To address the gaps identified above and present the "Standard Model of Code" framework for publication at premier venues, the paper should employ a clear structure that guides readers through the framework systematically:

**Introduction and Motivation** (15-20% of paper): This section must establish compelling motivation. It should identify specific problems that software engineering faces that require a formal, universally-applicable framework for code classification. It might discuss limitations of existing informal classifications, explain why practitioners and tool builders need a standard framework, describe specific software engineering tasks that require formal code classification (such as static analysis, software architecture evaluation, or code search), or establish that the diversity of code classification schemes across tools creates interoperability problems. The introduction should make a clear case that the investment in learning and using this framework is worthwhile[9][25][39].

**Related Work and Positioning** (15-20% of paper): This section must systematically address prior work in formal software engineering frameworks (SWEBOK, SEMAT, and recent formalization efforts), existing taxonomies and classification schemes, formal methods and mathematical approaches to computing, and programming language semantics[3][9][25]. For each category of related work, the paper should explain what it accomplishes, where it falls short relative to the current framework, and how the new framework advances beyond it. This section is not a literature review in the traditional sense but rather a systematic positioning of the new work within the landscape of existing scholarship.

**Framework Definition** (30-40% of paper): This is the core section establishing the formal framework. It should include:

- Clear definition of what constitutes a "code element" and what the framework applies to (which languages, paradigms, scope of analysis)
- Formal statement of each of the 15+ axioms, numbered and in clear mathematical notation, with accompanying explanation
- Formal definition of the 8 dimensions, including what each dimension represents, how it is measured or determined, and what the range of values is for each dimension
- Explanation of the 16-level holarchy, perhaps with diagram showing relationships between levels
- Clear definition of each of the 167 atom types (or a procedure for deriving them), probably organized by dimension or holarchy level
- Mathematical notation and formalism for coordinates in the 8-dimensional space
- Proof or rigorous argument that the framework is complete (all possible code structures fit within it), consistent (no contradictions between axioms or classifications), and sound (the classifications reflect meaningful distinctions in code structure)
- Examples showing how specific code elements are classified according to the framework
- Comparison showing how existing, informal code classifications (e.g., as used in popular static analyzers) map to the formal framework[3][15]

**Implementation and Validation** (20-30% of paper): This section should describe the static analyzer that implements the framework, present results showing that the analyzer correctly classifies code according to the framework definition, and provide empirical grounding through application to real code. Examples might include:

- Validation that the analyzer produces consistent results across repeated classification of the same code elements
- Application of the analyzer to a corpus of real-world code (e.g., from GitHub repositories, open-source projects, or industry systems) and reporting statistics about how code is distributed across the framework's categories
- Comparison of the framework's classifications against ground truth (either expert human classification or existing tool classifications)
- Case studies showing specific examples where the framework's formal classification enables useful capabilities (e.g., identifying missing abstractions, finding unexpected code patterns, or analyzing architectural structure)
- Evidence that practitioners find the framework's classifications meaningful and useful[10][25][26][37][40]

**Discussion and Limitations** (10-15% of paper): This section should clearly articulate what the framework does and does not accomplish, what scope limitations apply, what assumptions it makes, and what remains for future work. It should not oversell the contribution or imply broader applicability than the framework actually achieves. Specific limitations might include: applicability to specific programming languages or paradigms, inability to classify dynamic or generated code, focus on static structure rather than runtime behavior, or assumptions about code organization that may not hold in all contexts[9][25][28].

**Conclusion** (5% of paper): Concise summary of the contribution and its significance[39].

### Formalization Standards to Meet Reviewers' Expectations

For the 15+ axioms, each should be stated using clear mathematical notation. For example, if one axiom concerns the relationship between code elements at different levels of the holarchy, it might be expressed formally rather than just informally described:

\[
\forall e \in \text{Elements}, \forall L_i, L_j \in \text{Levels} \mid i < j : \text{Contains}(L_j, e) \implies \exists e' \in \text{Elements} : (e' \in L_i \land \text{ComponentOf}(e, e'))
\]

Each axiom should be accompanied by explanation in natural language of what the axiom means, why it is necessary, and what properties of code structure it constrains[3][15].

The 8-dimensional classification should include:
- Name and formal definition of each dimension
- Range of values for each dimension (continuous, discrete, finite, etc.)
- Method for determining the value of each dimension for a given code element
- Justification for why these specific 8 dimensions are chosen—why not 7 or 9? What is special about these 8?

The 167 atom types should be formally defined, ideally with a decision procedure that determines which atom type applies to a given code element. If this is not feasible for all 167 types (perhaps some are defined by combinations of dimension values and holarchy level rather than explicit categories), this should be explained clearly[3][15].

### Addressing Likely Reviewer Concerns Proactively

Anticipate the most likely reviewer concerns and address them directly in the paper:

**Concern: "This seems to just classify code in a complex way. Why should I care?"**
Address: Establish specifically how this formal classification enables capabilities that existing informal classifications do not. Perhaps the framework enables automated checking that code is organized according to good architectural principles, or enables automated discovery of patterns or anti-patterns, or enables better communication about code structure, or enables more precise specification of software quality metrics. The paper must demonstrate concrete value, not just the existence of a classification[9][25].

**Concern: "Haven't existing formalizations already addressed this?"**
Address: Systematically show where prior formalizations fall short. Perhaps they lack the comprehensiveness of the new framework, or lack the connection to practical implementation, or address different aspects of code structure. Be specific in comparing against SWEBOK, SEMAT, and category-theoretic approaches to program semantics. This positioning is crucial[3][9][25].

**Concern: "How do you know 167 atom types is the right number? This seems arbitrary."**
Address: Justify the choice of 167 types by arguing that they emerge naturally from the framework's mathematical structure (perhaps as combinations of values along the 8 dimensions and 16 holarchy levels), or by demonstrating that this level of granularity captures important distinctions that coarser classifications miss, or by showing that code in the wild naturally clusters into these categories. Use empirical evidence if possible[10][25][37].

**Concern: "The holarchy analogy to physics seems forced. What does physics have to do with code?"**
Address: Either develop the analogy rigorously (showing that specific mathematical structures from physics apply to code) or remove the analogy and focus on the mathematical structure of the holarchy on its own merits. If the physics analogy is merely mnemonic, acknowledge this and do not overstate its significance[32][35].

**Concern: "You have a static analyzer implementation. Why isn't this positioned as a tool paper?"**
Address: Clearly position the framework as the primary contribution and the static analyzer as a secondary artifact demonstrating feasibility. Make clear that the theoretical framework is the innovation; the analyzer is merely a proof-of-concept. Alternatively, if the paper is submitted to a track that accepts tool papers, position as a tool paper and use the theoretical framework as supporting material explaining why the tool is designed as it is[26].

### Strategic Considerations for Choosing a Target Venue

The choice of venue (ICSE, FSE, TSE, or TOSEM) should be strategic based on how the framework is positioned[1][13][19]:

**ICSE** (International Conference on Software Engineering) accepts journal-first papers and maintains research paper tracks[1]. ICSE's journal-first program accepts papers that have been published in IEEE TSE, ACM TOSEM, or Empirical Software Engineering (EMSE) within a specific time window[1][13][19]. This suggests a possible strategy: develop the framework paper in full for submission to one of these journals, and if accepted, then present it as a journal-first paper at ICSE. The journal publication provides formal peer review and credibility, and ICSE presentation provides visibility to the community[1].

**TSE** (IEEE Transactions on Software Engineering) is a prestigious journal that publishes theoretical and empirical software engineering research. TSE has long publication cycles but reaches a broad audience and has rigorous peer review[25][28][39].

**TOSEM** (ACM Transactions on Software Engineering and Methodology) similarly publishes theoretical contributions and maintains high standards for formal, rigorous work.

**EMSE** (Empirical Software Engineering) emphasizes empirical studies but also accepts theoretical work with clear empirical grounding.

For a primarily theoretical framework, starting with submission to TSE or TOSEM makes sense, as these journals specialize in methodological and theoretical contributions and have the time for thorough peer review that such work deserves[25][28].

## Broader Context: The State of Theory Publication in Software Engineering

### Current Tensions in How Theory Is Valued

The search results reveal significant current tensions in software engineering academia regarding how theoretical contributions are valued and evaluated. On one hand, venues officially value theoretical novelty and contribution. On the other hand, recent community surveys suggest that the practical implementation of peer review may not sufficiently value theoretical work, particularly theory that is novel but not yet heavily validated empirically[12][44][55].

Some community members argue that the emphasis on empirical validation, while important, has created a "novelty-vicious cycle" where genuinely novel theoretical ideas face resistance because they lack the extensive empirical validation that established approaches have accumulated, yet the empirical validation itself requires resources and time[12][44][55]. Others argue that recent decades of emphasis on empirical software engineering research, while productive, have come at the expense of theoretical work that provides conceptual foundations[12][44][55].

### Implications for the Standard Model of Code

These broader tensions have direct implications for publishing the "Standard Model of Code" framework. The paper will face reviewers with varying perspectives on how much empirical validation is necessary. Some reviewers will focus primarily on whether the formal framework is rigorous and novel, giving relatively less weight to empirical validation. Others will emphasize that without substantial empirical grounding, the framework remains disconnected from practice[12][44][55].

The paper should acknowledge these tensions directly. It might note that the framework is proposed as a formal foundation that can support future empirical research on code structure, software quality, and software evolution. It should acknowledge what empirical work remains for the future while providing sufficient preliminary empirical grounding to demonstrate feasibility[12][44][55].

## Conclusion: Pathways to Publication

The "Standard Model of Code" framework addresses a recognized gap in software engineering—the lack of comprehensive, formal frameworks for code classification and structure. It possesses significant theoretical ambition and has been operationalized in a working static analyzer. However, to meet publication standards at ICSE, FSE, TSE, or TOSEM, the framework requires substantial additional development and presentation work across multiple dimensions.

**Critical Additions Required**:

1. **Motivational Framing**: Establish compelling reasons why practitioners and researchers need this formal framework. What specific problems does it solve? How does it advance software engineering practice or theory[9][25]?

2. **Complete Formal Specification**: Provide rigorous mathematical definitions of all 15+ axioms, the 8 dimensions, the 16-level holarchy, and the 167 atom types. Make the framework completely formal enough that verification is feasible in principle[3][15][18].

3. **Systematic Positioning**: Relate the framework explicitly to prior formalizations (SWEBOK, SEMAT, recent formalization efforts) and explain where the new framework advances beyond existing work[3][25].

4. **Empirical Grounding**: Provide evidence that the framework can be applied consistently to real code, that the classifications are meaningful, and that practitioners find the framework useful[10][25][26][37][40].

5. **Clear Scope and Limitations**: Explicitly state what the framework does and does not address, what programming languages and paradigms it applies to, and what assumptions it makes[9][25][28].

6. **Strategic Presentation**: Organize the paper to lead readers through motivation, related work, formal specification, implementation/validation, and discussion of limitations in a logical flow that guides understanding[9][25][39].

**Recommended Path**:

Submit first to a prestigious journal (TSE or TOSEM) rather than initially to a conference. Journal publication provides time for thorough peer review of complex theoretical work and produces a publication venue with high visibility and credibility. Once published in the journal, the work can be presented at ICSE through the journal-first program, providing access to the conference community[1].

**Timeline and Effort**: Developing the framework paper to publication standard requires substantial effort—likely 2-4 months of intensive work to fully formalize the framework, develop the empirical validation, write the paper systematically, and revise based on feedback. This timeline assumes the core framework is already well-developed; if significant refinement of the framework itself is still needed, the timeline extends accordingly.

**Probability of Success**: If the framework paper is developed following the recommendations above—with clear motivation, rigorous formalization, systematic positioning, adequate empirical grounding, and careful acknowledgment of scope and limitations—publication at a premier venue is achievable. The framework appears to address genuine gaps in formal software engineering foundations. However, if significant gaps remain in motivation, formalization, or empirical grounding, rejection becomes likely even with substantial intellectual content, because peer review at premier venues applies consistent standards across all submissions[9][25][28].

The field would benefit from a comprehensive, formal framework for code classification that could serve as a foundation for future research on software quality, evolution, architecture, and analysis. The "Standard Model of Code" has the potential to provide such a framework, provided the additional work necessary to meet publication standards is undertaken with the rigor and care that theoretical contributions of this ambition require.

---

## Citations

1. https://conf.researchr.org/track/icse-2025/icse-2025-journal-first-papers
2. https://www.software.ac.uk/blog/scientific-coding-and-software-engineering-whats-difference
3. https://arxiv.org/pdf/2502.17170.pdf
4. http://www.icse-conferences.org/organization/ICSE-Operating-Rules-and-Guidelines-2023.pdf
5. https://pmc.ncbi.nlm.nih.gov/articles/PMC8743026/
6. https://dl.acm.org/doi/pdf/10.1145/3442389
7. https://www.ehealthinformation.ca/web/default/files/wp-files/isern-95-03.pdf
8. https://www.sei.cmu.edu/documents/1099/1993_005_001_16232.pdf
9. https://blog.sigplan.org/2021/12/07/bad-reasons-to-reject-good-papers-and-vice-versa/
10. https://www2.sigsoft.org/EmpiricalStandards/
11. https://dl.acm.org/doi/10.1145/3643664.3648206
12. https://www.arxiv.org/pdf/2601.18566.pdf
13. https://conf.researchr.org/track/icse-2025/icse-2025-journal-first-papers
14. https://www.cs.toronto.edu/~sme/presentations/cat101.pdf
15. https://homepage.cs.uiowa.edu/~slonnegr/plf/Book/Chapter11.pdf
16. http://www.icse-conferences.org/organization/ICSE-Operating-Rules-and-Guidelines-2023.pdf
17. https://www.omg.org/maths/September-2024-Mathsig-Presentation-to-the-AI-PTF.pdf
18. https://en.wikipedia.org/wiki/Axiomatic_semantics
19. https://conf.researchr.org/track/icse-2025/icse-2025-journal-first-papers
20. https://www.sei.cmu.edu/documents/902/1987_005_001_15512.pdf
21. https://pubmed.ncbi.nlm.nih.gov/41486571/
22. https://2024.esec-fse.org/track/fse-2024-research-papers
23. https://www.cs.wm.edu/~denys/pubs/JSME-FL-SurveyCRCV1.pdf
24. https://onlinelibrary.wiley.com/doi/10.1111/1556-4029.70253
25. https://conf.researchr.org/getImage/icse-2022/orig/ICSE+2022+Review+Process+and+Guidelines-2.pdf
26. https://conf.researchr.org/track/icse-2025/icse-2025-demonstrations
27. https://en.wikipedia.org/wiki/Semantics_(programming_languages)
28. https://conf.researchr.org/getImage/icse-2023/orig/ICSE+2023+Review+Process+and+Guidelines.pdf
29. https://dl.acm.org/doi/pdf/10.1109/ICSE-C.2017.50
30. http://lambda-the-ultimate.org/node/5305
31. https://ligechina.github.io/My%20Papers/2023%20-%20ICPC%20-%20Implant%20Global%20and%20Local%20Hierarchy%20Information%20to%20Sequence%20based%20Code%20Representation%20Models.pdf
32. https://ntrs.nasa.gov/api/citations/20030063129/downloads/20030063129.pdf
33. https://www.datacamp.com/blog/curse-of-dimensionality-machine-learning
34. https://www.emergentmind.com/topics/hierarchical-feature-representation
35. https://tholonia.github.io/posts/the-holarchy/
36. https://en.wikipedia.org/wiki/Dimensional_models_of_personality_disorders
37. https://machiry.github.io/files/emsast.pdf
38. https://en.wikipedia.org/wiki/Formal_methods
39. https://arxiv.org/html/2506.21634
40. https://dl.acm.org/doi/10.1145/3650212.3680313
41. https://users.ece.cmu.edu/~koopman/des_s99/formal_methods/
42. https://dl.acm.org/doi/10.1145/234426.234431
43. https://libguides.brown.edu/organize/litreview
44. https://www.arxiv.org/pdf/2601.18566.pdf
45. https://homepages.cwi.nl/~jurgenv/theses/TimPrijn.pdf
46. https://researchguides.elac.edu/Citation/litreviews
47. https://dl.acm.org/doi/proceedings/10.1145/3696630?id=121
48. https://pmc.ncbi.nlm.nih.gov/articles/PMC10028510/
49. https://people.cs.nott.ac.uk/pszgmh/123.pdf
50. https://help.klocwork.com/2024/en-us/concepts/abstractsyntaxtreeast.htm
51. https://codescene.com/product/code-health
52. https://cs.lmu.edu/~ray/notes/semantics/
53. https://dev.to/balapriya/abstract-syntax-tree-ast-explained-in-plain-english-1h38
54. https://docs.qlty.sh/cloud/maintainability/metrics
55. https://www.arxiv.org/pdf/2601.18566.pdf
56. https://pmc.ncbi.nlm.nih.gov/articles/PMC6318722/
57. https://www.coherentsolutions.com/insights/proof-of-concept-prototype-and-mvp-product-validation-stages-explained
58. https://pmc.ncbi.nlm.nih.gov/articles/PMC10220166/
59. https://lumivero.com/resources/blog/an-overview-of-grounded-theory-qualitative-research/
60. https://www.nrc.gov/docs/ML0421/ML042170285.pdf

---

## Usage Stats

- Prompt tokens: 198
- Completion tokens: 10412
- Total tokens: 10610
