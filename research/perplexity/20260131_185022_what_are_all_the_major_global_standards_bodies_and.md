# Research: What are ALL the major global standards bodies and vocabularies for software engineering terminology...

> **Date:** 2026-01-31 18:50:22
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:0069c8e6a1556432aa0d4b75715634c28ec7a8ba08a404d66cb62e6f6384793a`
> **Raw JSON:** `raw/20260131_185022_what_are_all_the_major_global_standards_bodies_and.json`

---

## Query

What are ALL the major global standards bodies and vocabularies for software engineering terminology? Compare IEEE SEVOCAB vs ISO/IEC 24765 vs OMG (Object Management Group) vs W3C vs INCOSE vs PMI PMBOK vs SEI CMM/CMMI vocabulary. Which is THE authoritative source? Are there competing vocabularies? Who maintains the canonical software engineering dictionary?

---

## Response

# Global Standards Bodies and Vocabularies for Software Engineering Terminology: A Comprehensive Comparison

The landscape of software engineering terminology standardization is characterized by multiple authoritative bodies that have collectively developed overlapping yet distinct vocabularies to serve different aspects of the discipline. This report examines the major global standards organizations and their terminological frameworks, including IEEE SEVOCAB, ISO/IEC 24765, the Object Management Group (OMG), the World Wide Web Consortium (W3C), the International Council on Systems Engineering (INCOSE), the Project Management Institute (PMI), and the Software Engineering Institute (SEI). While no single canonical dictionary exists, a collaborative relationship between ISO/IEC and IEEE has created what is arguably the most comprehensive and widely recognized vocabulary source for systems and software engineering terminology, though this dominance is complemented by specialized vocabularies from other organizations serving distinct professional communities and domains.

## The ISO/IEC 24765 and IEEE SEVOCAB Ecosystem: The De Facto Standard Framework

### The Foundational Relationship and Joint Maintenance Structure

The most authoritative and comprehensive vocabulary for systems and software engineering is embodied in the ISO/IEC/IEEE 24765:2017 standard, titled "Systems and software engineering — Vocabulary."[2][4][5][21][38][50] This standard is maintained through a unique collaborative arrangement between ISO/IEC JTC 1/SC 7 (Software and systems engineering) and the IEEE Computer Society, with the practical maintenance of the vocabulary residing in the SEVOCAB (Software and Systems Engineering Vocabulary) database hosted by the IEEE Computer Society.[1][2][5][17][18][24][25] The relationship between these two entities is not competitive but rather complementary, where SEVOCAB serves as the living database that is periodically published as a formal ISO/IEC/IEEE standard, creating both an online resource for current practitioners and a formal standard for regulatory and contractual purposes.[1][5][17][24][41][47][55]

The scope of ISO/IEC 24765:2017 is remarkably comprehensive, covering terminology applicable to all systems and software engineering work falling within the scope of ISO/IEC JTC 1/SC 7.[5][21][25][38][47] The standard explicitly states that it was "prepared to collect and standardize terminology" with the purpose of identifying "terms currently in use in the field and standard definitions for these terms."[5][25][47] The definitions in this vocabulary are intentionally designed to be "rigorous, uncomplicated, and understandable by all concerned," representing an effort to create consensus around technical language that can transcend organizational, geographical, and sectoral boundaries.[5][14][25][41]

### Evolution and Current Status of ISO/IEC 24765

The current version, ISO/IEC 24765:2017 (second edition), represents a significant evolution from its predecessor, ISO/IEC 24765:2010 (first edition).[4][21][38][50] The 2017 edition superseded the earlier version and is currently confirmed as an active standard as of the latest review cycle.[38][50] This standard itself evolved from IEEE Std 610.12-1990, "IEEE Standard Glossary of Software Engineering Terminology," which served as the foundational model for the approach and lexical exactitude of the international standard.[5][20][25][27][44] The transition from IEEE 610.12 to ISO/IEC 24765 represented a significant expansion, increasing the number of defined terms from approximately 500 to over 1,300 terms, reflecting the continuous evolution of the field.[25][27][30]

The maintenance structure of ISO/IEC 24765 demonstrates a sophisticated approach to keeping terminology current without requiring formal standard revision for every change. The SEVOCAB database is "modified in a controlled fashion" and accessible to the public through the IEEE Computer Society website, allowing practitioners to access the most current terminology definitions while the formal standard serves as a periodic snapshot of this evolving resource.[1][5][17][24][41][49] This dual approach—maintaining both a dynamic online database and formal standard versions—addresses the tension between the need for rigorous, published standards and the reality of rapidly evolving technical language in software engineering.

### Inclusion of Other Vocabularies Within ISO/IEC 24765

An important characteristic of ISO/IEC 24765 is that it explicitly incorporates definitions from multiple sources, including those from the Project Management Institute (PMI) Glossary, creating a truly integrated reference work.[2][5][14][25][44] The standard states that "every effort has been made to use definitions from established systems and software engineering standards of ISO JTC 1/SC 7 and its liaison organizations IEEE Computer Society and the PMI."[5][25] When existing standards were found to be incomplete, unclear, or inconsistent with other entries in the vocabulary, "new, revised, or composite definitions have been developed."[5][25][49] This inclusive approach means that ISO/IEC 24765 functions as both a primary source and a meta-vocabulary that incorporates and harmonizes terminology from related standards organizations.

## Major Competing and Complementary Standards Bodies and Vocabularies

### The Object Management Group and Its Specialized Vocabularies

The Object Management Group (OMG) maintains several specialized vocabularies that serve specific purposes within software engineering and enterprise architecture, though these operate more as specialized domain languages rather than comprehensive engineering terminology references. The SBVR (Semantics of Business Vocabulary and Rules) specification, with version 1.3 published in May 2015, "defines the vocabulary and rules for documenting the semantics of business vocabularies and business rules for the exchange of business vocabularies and business rules among organizations and between software tools."[3] SBVR represents a more sophisticated approach to vocabulary standardization by addressing not just term definitions but the semantic relationships and business rules that govern them, making it particularly valuable for enterprises attempting to formalize their domain knowledge.

Similarly, the Object Constraint Language (OCL), with version 2.4 published in February 2014, represents OMG's approach to providing "a declarative language describing rules applying to Unified Modeling Language (UML) models."[35] OCL provides constraint and object query expressions on Meta-Object Facility (MOF) models and meta-models, offering a formally defined language for expressing complex relationships that purely definitional vocabularies like ISO/IEC 24765 cannot accommodate.[32][35] The Multiple Vocabulary Facility (MVF) specification further demonstrates OMG's recognition that organizations require the ability to "express any model element in a given model in terms of multiple natural languages and vocabularies."[6]

These OMG standards differ fundamentally from ISO/IEC 24765 in that they focus on formal semantic representation and constraint specification rather than simple term definitions, addressing a different need in the software engineering landscape. OMG maintains Category A liaison status with ISO/IEC JTC 1/SC 7, indicating formal collaborative relationships between these standards development organizations.[15][31]

### W3C Vocabularies and the Semantic Web Context

The World Wide Web Consortium (W3C) maintains vocabularies primarily focused on semantic web technologies and resource description, rather than software engineering terminology per se. The Profiles Vocabulary (PROF), for instance, is "an RDF vocabulary created to allow the machine-readable description of profiles of specifications for information resources."[7] While not a software engineering vocabulary in the traditional sense, it serves the broader IT community by providing standardized, structured, and machine-readable terminology for describing how standards and specifications relate to one another, their profiles, and the resources that constitute them.[7]

W3C's Web Ontology Language (OWL) and its semantic extensions provide formal mechanisms for defining and constraining vocabularies at a level of expressiveness exceeding what simple terminological glossaries can provide.[56][59] The OWL 2 RDF-Based Semantics specification defines not just vocabulary terms but their formal interpretations and entailment relationships, allowing automated reasoning systems to derive new knowledge from explicitly stated vocabulary relationships.[56] These approaches represent a more mathematically rigorous treatment of vocabulary than traditional glossaries, though they serve more specialized needs in semantic computing than general software engineering practice.

### INCOSE and Systems Engineering Definitions

The International Council on Systems Engineering (INCOSE) maintains definitional resources specifically tailored to the systems engineering discipline, which represents a related but distinct domain from general software engineering. INCOSE's foundational definition of systems engineering states it is "a transdisciplinary and integrative approach to enable the successful realization, use, and retirement of engineered systems, using systems principles and concepts, and scientific, technological, and management methods."[8][11][37] INCOSE operates as a Category A liaison organization to ISO/IEC JTC 1/SC 7, ensuring alignment between systems engineering and broader software engineering terminology standards.[15][31]

Beyond definitional standards, INCOSE publishes the Systems Engineering Competency Framework, which aligns terminology with competency definitions to ensure "using organizations have the ability to use systems and software engineering standards prepared by ISO and liaison organizations IEEE Computer Society and Project Management Institute" by maintaining alignment "in the areas of terminology and concepts."[29] This competency-based approach to terminology represents a different application of standardized vocabulary—focusing not just on what terms mean but on what competencies are required to use them effectively in professional practice.

The INCOSE SE Glossary provides specialized definitions for systems engineering terms, and INCOSE materials emphasize that a system is "a combination of interacting elements organized to achieve one or more stated purposes," a foundational definition also adopted in ISO/IEC standards.[11][37] INCOSE's approach demonstrates how domain-specific professional bodies can maintain specialized vocabularies while remaining aligned with broader international standards.

### PMI and Project Management Terminology

The Project Management Institute (PMI) maintains the "PMI Lexicon of Project Management Terms," offering "clear and concise definitions for more than 350 of the profession's frequently used terms."[9][12] The PMI Lexicon functions specifically within the project management domain, covering terminology related to project, program, and portfolio management that overlaps with but extends beyond pure software engineering. PMI's approach emphasizes practical utility for practicing project managers, with definitions that often include bracketed clarifications indicating whether a term refers to a process, output/input, technique, or other category within their project management framework.[9][12]

Significantly, PMI terminology has been incorporated wholesale into ISO/IEC 24765, with the standard explicitly stating that "PMI Glossary definitions have been included without alteration in accordance with the copyright agreement."[5][14][25] This integration demonstrates the recognition that software engineering terminology cannot be isolated from project management terminology, as the two disciplines are inherently intertwined in practice. PMI maintains Category A liaison status with ISO/IEC JTC 1/SC 7, ensuring formal coordination between these standards organizations.[15][31]

### SEI Capability Maturity Models and Process Terminology

The Software Engineering Institute (SEI) at Carnegie Mellon University maintains the Capability Maturity Model Integration (CMMI) and the People CMM, which include substantial glossaries and terminological frameworks focused on process capability and maturity assessment.[13][16][52] The CMMI glossary is "designed to document the meanings of words and terms that should have the widest use and understanding by users of CMMI products," explicitly recognizing that "words and terms can have different meanings in different contexts and environments."[13] The glossary in CMMI models references multiple standards including ISO/IEC 12207, IEEE standards, ITIL, and other frameworks, demonstrating the SEI's effort to create a coherent vocabular across multiple related standards.

The People CMM Version 2.0 includes a comprehensive Glossary of Terms (Appendix C) defining terminology specific to human capability aspects of software engineering, with definitions drawn from established standards, the Merriam-Webster dictionary, and source models including EIA 731, SW-CMM, and IPD-CMM.[16] This specialized vocabulary addresses the distinctive terminology needed for discussing workforce capability, competency development, and human factors in software engineering—areas that general vocabularies like ISO/IEC 24765 address less comprehensively.

## Comparative Analysis of Terminological Approaches and Coverage

| Standards Body | Primary Standard | Coverage Focus | Maintenance Structure | Formalism Level | Domain Scope |
|---|---|---|---|---|---|
| ISO/IEC & IEEE | ISO/IEC 24765:2017 | Comprehensive systems and software engineering | ISO/IEC JTC 1/SC 7 + IEEE SEVOCAB database | Textual definitions with cross-references | General software and systems engineering |
| OMG | SBVR 1.3, OCL 2.4 | Business vocabularies, UML/MOF constraints | OMG formal specification process | Formal semantics and constraint languages | UML/MOF-based systems, business rules |
| W3C | Profiles Vocab, OWL 2 | Semantic web and RDF vocabularies | W3C working groups | Formal ontology with description logic | Semantic web, linked data, distributed systems |
| INCOSE | SE Definitions, Competency Framework | Systems engineering practice | INCOSE working groups, aligned with ISO | Narrative with competency mapping | Systems engineering, engineered systems |
| PMI | Lexicon of PM Terms | Project and portfolio management | PMI volunteer committees | Contextual definitions with category labels | Project, program, portfolio management |
| SEI | CMMI Glossary, People CMM | Process capability and maturity | SEI development with standards references | Process-oriented with maturity levels | Process improvement, workforce capability |

## The Question of Canonical Authority and Standardization Hierarchy

### Why ISO/IEC 24765 Functions as the De Facto Standard

Despite the existence of these multiple vocabularies, ISO/IEC 24765:2017 functions as the de facto canonical reference for software engineering terminology for several compelling reasons. First, it represents the only explicitly collaborative effort between multiple major standards organizations, incorporating terminology from IEEE, PMI, and other bodies while maintaining organizational independence and rigor through the ISO/IEC formal standardization process.[2][5][38] Second, the scope of ISO/IEC 24765 is intentionally comprehensive, designed to cover "all systems and software engineering work falling within the scope of ISO/IEC JTC 1/SC 7," making it the broadest available reference.[5][38]

Third, the standard explicitly documents its sources for each definition, making it possible to trace terminology back to authoritative standards while understanding the genealogy of specific terms.[5][14][25] This transparency stands in contrast to some other vocabularies that may define terms without explicitly acknowledging their source standards or reasoning for particular definitions. Fourth, the dual maintenance structure—with SEVOCAB providing an up-to-date online database while formal standards provide authoritative snapshots—addresses the fundamental tension between the need for current terminology and the need for stable, formally endorsed definitions that can be referenced in contracts and regulatory contexts.[1][5][17][24][41]

Finally, ISO/IEC 24765 achieves wide adoption because compliance with ISO standards is often contractually required in regulated industries and government procurement, creating institutional incentives for its use. The standard is published by ISO, the "International Organization for Standardization," which carries weight and authority that perhaps no single professional body, however expert, could match independently.[38][50]

### Evidence of Competing and Complementary Vocabularies

Despite the prominence of ISO/IEC 24765, evidence clearly demonstrates that competing and complementary vocabularies persist. Research on vocabulary agreement in software issue descriptions reveals that "developers and other software stakeholders tend to use rather different vocabulary when describing the same problem," with duplicate bug reports sharing between 24.7% and 42.5% of their vocabulary depending on the source.[43] This empirical observation suggests that even when authoritative vocabularies exist, practitioners do not uniformly adopt them, instead developing domain-specific and organizational-specific terminology variants.

The literature also identifies what researchers term the "vocabulary mismatch problem," noting that "people choose the same words to refer to the same object with less than 20% probability,"[43] indicating that standardization efforts, while valuable, cannot completely eliminate the natural human tendency toward semantic variation. Some organizations and research groups have advocated for alternatives to absolute harmonization, with "standards blending" offered as a pragmatic approach that allows practitioners to integrate multiple vocabularies rather than adhering rigidly to a single canonical source.[60]

The existence of specialized vocabularies from OMG, W3C, INCOSE, SEI, and others indicates recognition that no single vocabulary can perfectly serve all contexts. OMG's development of the Multiple Vocabulary Facility explicitly acknowledges that "modeling tool vendors and users" need the ability to "express any model element in a given model in terms of multiple natural languages and vocabularies,"[6] suggesting that enforcing single-vocabulary compliance across diverse organizational and technical contexts is neither feasible nor desirable.

## Standards Harmonization Efforts and Current Initiatives

### The Challenge of Semantic Interoperability Across Standards

Recognizing that organizations frequently need to apply multiple standards in combination, significant research and standardization efforts have focused on standards harmonization and semantic interoperability. A comprehensive research effort in software engineering standards harmonization identified that "most of these standards are created independently, defining their own scope, structure and terminology, often not sharing the same semantics," which "frequently gives rise to inconsistencies and divergences between them, harming the combined application."[57] This analysis demonstrates that despite ISO/IEC 24765's broad scope and integrative approach, semantic alignment problems persist when practitioners attempt to combine ISO/IEC standards with other frameworks like CMMI, ITIL, or domain-specific standards.

The research produced the Software Engineering Ontology Network (SEON) and a semantic-oriented approach for standards harmonization called Harmony, which use formal ontologies to serve as an "interlingua" during harmonization efforts.[57] These initiatives acknowledge that achieving perfect harmonization is neither possible nor necessarily desirable, but that explicit semantic mapping and transformation tools can help organizations navigate the landscape of multiple vocabularies and standards more effectively.

### Joint Working Groups and Liaison Relationships

The formal structure of standards development organizations includes liaison relationships and joint working groups that create opportunities for terminological coordination. ISO/IEC JTC 1/SC 7 maintains Category A liaison relationships with IEEE, INCOSE, ISACA, itSMF, ITU, OMG, and PMI,[15][31] meaning these organizations have formal mechanisms for coordinating standards development and terminology. The existence of a "Joint Working Group ISO/IEC JTC1/SC 42 - ISO/IEC JTC1/SC 7 : Testing of AI-based systems" demonstrates how standards bodies actively coordinate across boundaries when new technologies create new terminological needs.[15][31]

Despite these coordination mechanisms, the research literature suggests that true semantic integration remains incomplete. Harmonization initiatives like Harmony operate at a meta-level, creating tools and ontological frameworks for translating between standards rather than fundamentally reconciling them. This approach implicitly accepts that different standards bodies will continue to maintain distinct vocabularies, but that mapping relationships and transformation tools can facilitate their combined application.

## Practical Implications for Software Engineering Practice

### How Practitioners Navigate the Vocabulary Landscape

Practitioners navigating software engineering terminology must understand that no single vocabulary, even ISO/IEC 24765, is universally applied across all organizational contexts. Software development has evolved with the understanding that "technical English vocabulary is important for understanding and writing code and communicating with colleagues and stakeholders," with clear, precise technical terms helping to "avoid misunderstandings and ensure that everyone is on the same page."[42][46] However, the diversity of vocabularies reflects genuine practical and domain-specific needs that cannot be resolved through standardization alone.

Organizations implementing systems engineering must often navigate "terminologies used in some diagrams and models [that are] confusing and non-intuitive," requiring training and education to ensure that "stakeholders [understand] a specific detailed technical language."[36] This reality explains why standards harmonization research has focused on tools and ontologies that allow navigation between standards rather than pushing for a single unified vocabulary. The TOGAF standard for enterprise architecture, the Zachman Framework, and the DoDAF approach each maintain distinct but related terminological frameworks,[51] reflecting the reality that different architectural perspectives and stakeholder communities have legitimate needs for specialized vocabulary.

### The Role of Organizational and Domain-Specific Vocabularies

Practical software engineering also requires recognition that organizational and domain-specific vocabularies complement rather than conflict with standardized terminology. Research on naming conventions in software development reveals that consistent organizational terminology—even when it differs from broader standards—contributes to code quality and team communication.[46] The principle that "consistency beats out clever every time" in naming and terminology use suggests that organizations may rationally choose to maintain consistent internal terminology even when it differs from external standards, as long as the organization explicitly acknowledges the mapping between internal and standardized terminology.[46]

Domain-specific vocabularies in areas such as healthcare software, financial systems, aerospace engineering, and automotive systems necessarily diverge from general software engineering terminology to accommodate domain requirements and regulatory needs. The existence of vocabulary variation is therefore not merely a problem to be solved but a reflection of legitimate diversity in how different professional communities conceptualize and discuss their work.

## Conclusion: Authority, Standardization, and Future Directions

The landscape of software engineering terminology is characterized by clear hierarchy with ISO/IEC 24765:2017 functioning as the authoritative comprehensive reference standard, jointly maintained by ISO/IEC JTC 1/SC 7 and the IEEE Computer Society through the SEVOCAB database.[2][5][38][50] This standard achieves its authority through broad scope, explicit documentation of sources, transparent maintenance processes, wide adoption in regulated industries, and formal integration of terminology from other major standards organizations including PMI, OMG, INCOSE, and others.[5][25][38] The decision to incorporate PMI terminology directly into ISO/IEC 24765 rather than maintaining competing vocabularies demonstrates a mature approach to standardization that acknowledges multiple legitimate sources of expertise while creating coherent, authoritative references.

However, the continued existence and active maintenance of specialized vocabularies from OMG, W3C, INCOSE, SEI, and others reflects both the incompleteness of any single vocabulary and the legitimate domain-specific needs of different professional communities.[3][6][7][16][29][35] Rather than viewing these as competing vocabularies, they are more accurately understood as complementary frameworks serving distinct purposes—from business rule specification (SBVR) to formal constraint languages (OCL) to semantic web representation (OWL) to systems engineering practice (INCOSE definitions) to project management (PMI) to process capability (CMMI).

The field has moved beyond seeking a single canonical source toward developing harmonization approaches, mapping tools, and ontological frameworks that allow practitioners to navigate multiple vocabularies effectively.[57][60] Organizations implementing software engineering standards increasingly recognize that effective terminology management requires explicit mapping between internal organizational terminology, domain-specific vocabulary, and multiple external standards, rather than perfect conformance to any single vocabulary source.

The maintenance of SEVOCAB as a living database that produces periodic formal standards represents perhaps the most innovative approach to addressing the tension between terminological stability and evolution.[1][5][17][24] As software engineering continues to evolve with emerging technologies including artificial intelligence, cloud computing, edge computing, and quantum computing—each introducing new terminology requiring standardization—this dual approach of maintaining an actively updated online vocabulary while publishing periodic formal standards provides a scalable mechanism for keeping terminology current while preserving the rigor of formally endorsed definitions. Future developments in software engineering terminology will likely continue to emphasize harmonization tools and cross-standard mapping frameworks rather than achieving complete terminological unification, acknowledging both the authority of ISO/IEC 24765 and the legitimate contribution of specialized vocabularies from domain-specific and community-specific standards bodies.

---

## Citations

1. https://pascal.computer.org
2. https://buildsoftwaresystems.com/terminologies/
3. https://www.omg.org/spec/SBVR/1.3/About-SBVR
4. https://www.iso.org/standard/50518.html
5. https://www.vde-verlag.de/iec-normen/preview-pdf/info_isoiecieee24765%7Bed2.0%7Den.pdf
6. https://www.omg.org/spec/MVF/1.0/About-MVF
7. https://www.w3.org/TR/dx-prof/
8. https://www.incose.org/docs/default-source/default-document-library/incose-se-definitions-tp-2020-002-06.pdf
9. https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf?rev=447328d841c249af985d14177ddd5f95
10. https://www.w3.org/2003/glossary/
11. https://www.incose.org/about-systems-engineering/system-and-se-definitions/se-glossary
12. https://www.pmi.org/pmbok-guide-standards/lexicon
13. https://www.wibas.com/cmmi/glossary
14. https://cse.msu.edu/~cse435/Handouts/Standards/IEEE24765.pdf
15. https://www.iso.org/committee/45086.html
16. https://www.sei.cmu.edu/documents/808/2009_005_001_15095.pdf
17. https://pascal.computer.org/sev_display/help.jsp
18. https://pascal.computer.org
19. https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-guides/glossary-computer-system-software-development-terminology-895
20. https://www.informatik.htw-dresden.de/~hauptman/SEI/IEEE_Standard_Glossary_of_Software_Engineering_Terminology%20.pdf
21. https://standards.ieee.org/ieee/24765/6800/
22. https://www.codingtemple.com/blog/50-terms-every-software-engineer-should-know/
23. https://ptacts.uspto.gov/ptacts/public-informations/petitions/1463490/download-documents?artifactId=Xj1d1g9A148LRXvAd3I_SD4U-7gKx16p8hTbNromWc0jTcanBtNsoyU
24. https://pascal.computer.org/sev_display/help.jsp
25. https://cse.msu.edu/~cse435/Handouts/Standards/IEEE24765.pdf
26. https://psg-inc.net/wp-content/uploads/2022/10/1d39s2ja3_776432.pdf
27. https://standards.ieee.org/ieee/610.12/855/
28. https://www.iso.org/obp/ui/fr/
29. https://www.incose.org/docs/default-source/professional-development-portal/isecf.pdf?sfvrsn=dad06bc7_4
30. https://www.informatik.htw-dresden.de/~hauptman/SEI/IEEE_Standard_Glossary_of_Software_Engineering_Terminology%20.pdf
31. https://www.iso.org/committee/45086.html
32. https://en.wikipedia.org/wiki/Object_Constraint_Language
33. https://www.incose.org/docs/default-source/default-document-library/systems-engineering-guidebook---isbn-9780692091807bb88028572db67488e78ff000036190a.pdf?sfvrsn=365365c7_0
34. https://www.omg.org/about/liaison.htm
35. https://www.omg.org/spec/OCL/2.4/About-OCL
36. https://www.incose.org/docs/default-source/working-groups/requirements-wg/gtwr/incose_rwg_gtwr_v4_040423_final_drafts.pdf?sfvrsn=5c877fc7_2
37. https://ops.fhwa.dot.gov/seits/sections/section2/2_1.html
38. https://www.iso.org/standard/71952.html
39. https://resources.axway.com/open-everything/ck-10-tech-buzzwords-you-should-know-in-2025-en
40. https://peer.asee.org/on-the-similarities-and-contrasts-between-systems-engineering-terminologies.pdf
41. https://cdn.standards.iteh.ai/samples/71952/6289cd982a154c1d8fa0b10b52e0f8a8/ISO-IEC-IEEE-24765-2017.pdf
42. https://www.immigo.io/blog/technical-english-essential-vocabulary-for-software-developers
43. https://ojcchar.github.io/files/6-icsme16.pdf
44. https://cse.msu.edu/~cse435/Handouts/Standards/IEEE24765.pdf
45. https://www.informatik.htw-dresden.de/~hauptman/SEI/IEEE_Standard_Glossary_of_Software_Engineering_Terminology%20.pdf
46. https://www.simplethread.com/taming-names-in-software-development/
47. https://cdn.standards.iteh.ai/samples/71952/6289cd982a154c1d8fa0b10b52e0f8a8/ISO-IEC-IEEE-24765-2017.pdf
48. https://www.iso.org/obp/ui/en/
49. https://cse.msu.edu/~cse435/Handouts/Standards/IEEE24765.pdf
50. https://www.iso.org/standard/71952.html
51. https://www.opengroup.org/architecture/0310wash/presents/Rolf_Siegers-REAP_Overview.pdf
52. https://www.gasq.org/files/content/gasq/downloads/certification/IQBBA/IQBBA_Standard_glossary_of_terms_used_in_Software_Engineering_1.0.pdf
53. https://www.computer.org/education/bodies-of-knowledge/software-engineering
54. https://www.opengroup.org/togaf
55. https://committee.iso.org/sites/jtc1sc7/home/projects/flagship-standards/isoiecieee-247652017.html
56. https://www.w3.org/TR/owl2-rdf-based-semantics/
57. https://nemo.inf.ufes.br/wp-content/papercite-data/pdf/software_engineering_standards_harmonization__an_ontology_based_approach_2017.pdf
58. https://cse.msu.edu/~cse435/Handouts/Standards/IEEE24765.pdf
59. https://en.wikipedia.org/wiki/Web_Ontology_Language
60. https://www.computer.org/csdl/magazine/co/2007/07/r7094/13rRUwjoNAv

---

## Usage Stats

- Prompt tokens: 82
- Completion tokens: 5026
- Total tokens: 5108
