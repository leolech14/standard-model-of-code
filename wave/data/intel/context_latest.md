# Context: wave/tools/ai

## wave/tools/ai/.pytest_cache/README.md
**Purpose:** Describes the purpose of the pytest cache directory

This README file explains that the directory contains data from pytest's cache plugin and should not be committed to version control. It provides a link to the official pytest documentation for more information.

**Concepts:** pytest, cache plugin, version control

## wave/tools/ai/.research/ARCHITECTURE_MAP.md
**Purpose:** Unified Architecture Map for the AI toolkit at wave/tools/ai/

The AI toolkit is a context intelligence platform organized into 6 subsystems: Cerebras Tools, ACI System, Decision Deck, Support Tools, Config Layer, and Refinery. The toolkit provides a comprehensive architecture for AI-related tasks, including fast inference, query routing, and context optimization. The architecture map outlines the relationships between these subsystems and their components.

**Concepts:** Context Intelligence Platform, Subsystem Architecture, Cerebras Tools, ACI System, Decision Deck

## wave/tools/ai/.research/chunks/01_CEREBRAS_TOOLS.md
**Purpose:** Analyzes the Cerebras toolkit, a suite of Python scripts leveraging the Cerebras inference API for codebase intelligence operations.

The Cerebras toolkit consists of 8 standalone Python scripts that share a common structural pattern, utilizing the Cerebras inference API for fast codebase intelligence operations. Each script implements its own Cerebras client, rate limiter, and API key retrieval, with an acknowledged architectural debt. The toolkit provides various functionalities, including full-codebase intelligence sweeps, multi-pass iterative refinement, batch dimension classification, and semantic enrichment.

**Concepts:** Cerebras inference API, Codebase intelligence operations, Standalone Python scripts, Architectural debt, Semantic enrichment

## wave/tools/ai/.research/chunks/02_ACI_SYSTEM.md
**Purpose:** Describes the architecture and components of the Adaptive Context Intelligence (ACI) system

The ACI system is a complex architecture that powers the Elements AI analysis tool, responsible for query routing, context optimization, and multi-tier execution. It consists of multiple components, including intent parsing, tier orchestration, semantic finding, and context building. The system is designed to bridge the gap between human questions and the right AI model+context combination.

**Concepts:** Adaptive Context Intelligence (ACI), Query routing, Context optimization, Multi-tier execution, Intent parsing

## wave/tools/ai/.research/chunks/03_DECISION_DECK.md
**Purpose:** Decision Deck System: a governance layer for AI agents with a curated library of certified moves

The Decision Deck System is a governance layer that constrains AI agent actions to a curated library of certified moves, improving task success rates by 40-60%. It consists of a Dealer, Router, Player, and Meters, and uses a card game metaphor. The system has been analyzed based on 4 Python modules, 26 YAML cards, and 1 external consumer.

**Concepts:** Certified moves, Constrained action space, Card game metaphor, Dealer, Router, Player, Meters

## wave/tools/ai/.research/chunks/04_SUPPORT_TOOLS.md
**Purpose:** Support and utility tools for AI systems

This file documents various support and utility tools for AI systems, including intel.py, insights_generator.py, boundary_analyzer.py, context_filters.py, token_estimator.py, perplexity_research.py, and gemini_status.py. These tools provide functionality such as unified AI subsystem query interfaces, collider AI insights wrappers, internal organization validators, intelligent file filtering, token budget management, external research tools, and Gemini API status and diagnostics. The tools are designed to support the development and deployment of AI systems, and are used by various higher-level systems such as analyze.py, Decision Deck, and ACI.

**Concepts:** AI subsystem query interfaces, Collider AI insights wrappers, Internal organization validation, Intelligent file filtering, Token budget management, External research tools, Gemini API status and diagnostics

## wave/tools/ai/.research/chunks/05_CONFIG_DATA.md
**Purpose:** Maps configuration files and data directories for the Wave AI toolkit

This file provides a detailed map of configuration files and data directories used by the Wave AI toolkit, including their purpose, consumers, and key sections. It covers various aspects such as prompt templates, analysis sets, adaptive context intelligence, and research schemas. The file serves as a reference for understanding the dependencies and interactions between different components of the toolkit.

**Concepts:** Configuration files, Data directories, Adaptive Context Intelligence (ACI), Research schemas, Prompt templates

## wave/tools/ai/.research/chunks/06_REFINERY.md
**Purpose:** This file provides a deep dive into the Refinery, a context atomization and knowledge refinement engine within the PROJECT_elements system.

The Refinery breaks down large raw data into atomic, searchable, scorable chunks called RefineryNodes and integrates them into a broader pipeline of query routing, semantic matching, caching, and multi-tier AI execution. It is a core module within the Adaptive Context Intelligence (ACI) subsystem, which prepares optimal context for AI models before they answer questions. The Refinery is evolving from an L6 Package to an L7 System and potentially an L8 Platform.

**Concepts:** RefineryNode, Context Intelligence, Adaptive Context Intelligence (ACI), Semantic Matching, Knowledge Refinement

## wave/tools/ai/.research/chunks/07_CROSS_PROJECT.md
**Purpose:** Documents connections between the AI toolkit in PROJECT_elements and other projects in ~/PROJECTS_all/

This file provides a detailed overview of how the AI toolkit in PROJECT_elements connects to other projects, including PROJECT_openclaw, PROJECT_atman, PROJECT_sentinel, and PROJECT_central-mcp. It describes the data flows, code-level analysis, and planned integrations between these projects. The AI toolkit is deeply integrated with PROJECT_elements and has connections to other projects via data exchange, CLI invocation, or config references.

**Concepts:** Cross-project connections, AI toolkit integration, Data flows, Code-level analysis, Planned integrations

## wave/tools/ai/CEREBRAS_TOOLS.md
**Purpose:** Provides tools for fast semantic enrichment using Cerebras inference

The Cerebras Integration Tools offer a suite of scripts for repository mapping, semantic enrichment, and batch dimension tagging, leveraging Cerebras inference for fast and accurate results. These tools integrate with the Collider output to add a semantic layer, providing insights into code purpose, complexity, and quality. The tools also support various models and have been validated for accuracy.

**Concepts:** Semantic Enrichment, Cerebras Inference, Repository Mapping, Batch Dimension Tagging, Model Selection

## wave/tools/ai/README.md
**Purpose:** Serves as the documentation index for OpenClaw, providing a map to various documents and resources.

This README file acts as a central hub for navigating the OpenClaw documentation, covering topics such as getting started, usage, architecture, and troubleshooting. It also includes an archive of historical documents and design decisions. The file is designed to be a living document, with guidelines for maintenance and updates.

**Concepts:** Documentation index, OpenClaw, Getting started, Architecture, Troubleshooting

## wave/tools/ai/TRIAD_FLOWS_AND_MERMAIDS_files/libs/bootstrap/bootstrap.min.js
**Purpose:** Bootstrap JavaScript library

This file is part of the Bootstrap JavaScript library, providing various utility functions and classes for working with DOM elements, events, and data attributes. It includes classes for managing component configuration and data, as well as functions for handling events, setting and getting data attributes, and more. The library is designed to be used in web applications to provide a set of reusable UI components and functionality.

**Concepts:** Bootstrap, JavaScript library, DOM manipulation, Event handling, Data attributes

## wave/tools/ai/TRIAD_FLOWS_AND_MERMAIDS_files/libs/clipboard/clipboard.min.js
**Purpose:** Clipboard.js library for copying and cutting text

This file contains the Clipboard.js library, which provides a simple way to copy and cut text in the browser. It uses the `execCommand` API to perform the copy and cut operations. The library also provides a way to customize the behavior of the copy and cut operations, such as specifying a custom container element and target element.

**Concepts:** Clipboard.js, execCommand API, copy and cut operations, custom container element, target element

## wave/tools/ai/TRIAD_FLOWS_AND_MERMAIDS_files/libs/quarto-html/anchor.min.js
**Purpose:** AnchorJS library for adding anchor links to HTML elements

This JavaScript file provides the AnchorJS library, which allows users to add anchor links to HTML elements. It supports various options for customization, such as icon, placement, and visibility. The library also includes methods for adding, removing, and removing all anchor links.

**Concepts:** Anchor links, HTML elements, Customization options, JavaScript library, DOM manipulation

## wave/tools/ai/TRIAD_FLOWS_AND_MERMAIDS_files/libs/quarto-html/axe/axe-check.js
**Purpose:** Provides accessibility checking functionality using axe-core

This file contains classes for reporting accessibility violations in a Quarto HTML document. It uses axe-core to run accessibility checks and provides different reporting options, including JSON, console, and document-based reporting. The QuartoAxeChecker class initializes the accessibility check and generates a report based on the provided options.

**Concepts:** Accessibility checking, Axe-core integration, Reporting options (JSON, console, document), Class-based architecture, Async initialization

## wave/tools/ai/TRIAD_FLOWS_AND_MERMAIDS_files/libs/quarto-html/popper.min.js
**Purpose:** The Popper.js library for managing popovers and tooltips

This is a JavaScript library that provides a simple way to create and manage popovers and tooltips. It offers a range of features, including automatic positioning, boundary detection, and support for various modifiers. The library is designed to be flexible and customizable, allowing developers to easily integrate it into their applications.

**Concepts:** Popover management, Tooltip management, Automatic positioning, Boundary detection, Modifiers

## wave/tools/ai/TRIAD_FLOWS_AND_MERMAIDS_files/libs/quarto-html/quarto.js
**Purpose:** Handles layout and event handling for Quarto HTML documents

This script manages the layout of margin elements, tracks scrolling and marks TOC links as active, and dispatches events for HTML widgets and Shiny. It also handles category links and URL offsetting. The script uses various event listeners and observers to respond to changes in the document and window.

**Concepts:** CustomEvent, ResizeObserver, event listeners, DOM manipulation, URL offsetting

## wave/tools/ai/TRIAD_FLOWS_AND_MERMAIDS_files/libs/quarto-html/tabsets/tabsets.js
**Purpose:** Manages grouped tabsets with persistent state across page loads

This JavaScript file initializes and manages grouped tabsets, allowing users to switch between tabs and persisting the state across page loads. It uses local storage to store the tab settings and updates the tab state accordingly. The file also sets up event listeners for tab clicks to update the state and toggle the active tabs.

**Concepts:** Local storage, Event listeners, Tab management, Persistent state, DOM manipulation

## wave/tools/ai/TRIAD_FLOWS_AND_MERMAIDS_files/libs/quarto-html/tippy.umd.min.js
**Purpose:** Tippy.js library for creating tooltips and popovers

This file is a minified version of the Tippy.js library, which provides a way to create tooltips and popovers for HTML elements. It includes various features such as animation, interactive elements, and accessibility options. The library uses the Popper.js library for positioning and layout.

**Concepts:** Tooltips, Popovers, Animation, Interactive elements, Accessibility

## wave/tools/ai/aci/GEMINI.md
**Purpose:** Describes the AI Context Intelligence (ACI) component, the 'Brain' of the Standard Model

The ACI component processes raw code into refined, logistics-aware context through a refinement engine, synthesis, and deep analysis logic. It consists of multiple files, including refinery.py, context_builder.py, and research_orchestrator.py, each playing a specific role. The component is logistics-aware and maintains W3C PROV compliance.

**Concepts:** Refinement Engine, Synthesis, Logistics-Aware, W3C PROV compliance, Chain of Custody

## wave/tools/ai/aci/__init__.py
**Purpose:** Adaptive Context Intelligence (ACI) System for selecting the right context tier for every query

The ACI System analyzes queries based on intent, complexity, and scope to determine the optimal context tier. It provides a range of tools and functions for query analysis, tier routing, context optimization, and semantic matching. The system is designed to be modular and extensible, with a focus on flexibility and customization.

**Concepts:** Adaptive Context Intelligence, Query Analysis, Tier Routing, Context Optimization, Semantic Matching

## wave/tools/ai/aci/context_builder.py
**Purpose:** Builds optimized context for AI queries

This module is responsible for optimizing the context for AI queries by injecting agent context, positioning critical files, managing context budgets, and integrating truths for instant queries. It provides functions to estimate token counts, load repository truths, and answer queries using cached truths. The module is part of the ACI subsystem and uses configuration from aci_config.yaml.

**Concepts:** Context optimization, Agent context injection, Token budget management, Truths integration, Positional strategy

## wave/tools/ai/aci/context_cache.py
**Purpose:** Manages the lifecycle of cached contexts for the FLASH_DEEP tier

This Python module provides a cache registry for tracking Gemini context caches, enabling the 'expensive per snapshot, cheap per question' pattern. It allows for registering, retrieving, and invalidating cache entries, as well as cleaning up expired entries and providing registry statistics. The cache registry is persisted to a JSON file on disk.

**Concepts:** Cache registry, Gemini context caches, FLASH_DEEP tier, Time-to-live (TTL) caching, Data persistence

## wave/tools/ai/aci/feedback_store.py
**Purpose:** Manages feedback collection and storage for ACI queries

This module provides a feedback loop for ACI queries, storing query profiles, routing decisions, and execution results. It enables learning from query patterns and provides statistics and recommendations for routing improvements. The feedback data is stored in a YAML file and can be accessed through various methods.

**Concepts:** Feedback Loop, ACI Queries, Query Profiles, Routing Decisions, YAML Storage

## wave/tools/ai/aci/intent_parser.py
**Purpose:** Parses incoming queries to determine intent, complexity, scope, and agent context

This file contains classes and functions for parsing queries and determining their intent, complexity, and scope. It uses configuration loaded from aci_config.yaml and merges it with default values. The intent parser detects the type of question being asked, estimates the complexity of the query, and determines whether the query targets the internal codebase or external knowledge.

**Concepts:** Intent detection, Query complexity estimation, Scope determination, Agent context detection, Configuration loading and merging

## wave/tools/ai/aci/refinery.py
**Purpose:** Breaks large context into atomic chunks with metadata using semantic chunking strategies

The refinery.py file is a Context Atomization Engine that integrates with CacheRegistry for persistence and TierRouter for relevance scoring. It uses semantic chunking strategies to break large files into atomic chunks with metadata. The file supports various input formats, including Python, Markdown, and YAML, and provides a Refinery class for processing files and exporting chunks to JSON.

**Concepts:** Semantic chunking, Embedding engine, Cache registry, Tier router, Relevance scoring

## wave/tools/ai/aci/refinery/publishers/neo4j_publisher.py
**Purpose:** Publishes Refinery Atoms to a Neo4j Graph Store

This Python module provides a Neo4jPublisher class that connects to a Neo4j database and publishes Refinery Atoms (RefineryNodes) to it. The class implements the 'Unification' stage of the Waybill Architecture and handles tasks such as initializing the connection, verifying connectivity, and publishing atoms and telemetry data. The module uses the neo4j library to interact with the Neo4j database and provides methods for creating audit nodes, ingesting atoms, and publishing telemetry events.

**Concepts:** Neo4j Graph Database, Refinery Atoms (RefineryNodes), Waybill Architecture, Unification stage, Cypher queries

## wave/tools/ai/aci/repopack.py
**Purpose:** Generates a deterministic repository context snapshot for caching purposes

This script creates a structured, cacheable context snapshot for a given repository, including information such as repository ID, file tree, and recently modified files. The snapshot is designed to be identical for the same repository state, allowing for efficient caching. The script also generates a deterministic cache key based on the repository state.

**Concepts:** Repository context snapshot, Deterministic caching, Git repository analysis, File tree generation, Cache key generation

## wave/tools/ai/aci/research_orchestrator.py
**Purpose:** Orchestrates multi-configuration query execution using predefined research schemas for AI agents.

The Research Orchestrator provides a 'joystick interface' for AI agents to control research by executing multiple ACI queries with different parameters, synthesizing results using various strategies, and producing validated, multi-perspective answers. It supports predefined and custom research schemas, with features like schema validation, output format selection, and result synthesis. The orchestrator is part of the S3 (ACI subsystem) and targets AI agents as its primary audience.

**Concepts:** Research schemas, Multi-configuration query execution, Result synthesis, Schema validation, Joystick interface for AI agents

## wave/tools/ai/aci/schema.py
**Purpose:** Defines a data class for representing refinery nodes with metadata and logistics information

This file defines a data class called RefineryNode, which represents an atomic chunk of text with associated metadata and logistics information. The class includes attributes such as content, source file, chunk ID, and relevance score, as well as methods for converting to a dictionary and estimating token count. The RefineryNode class is designed to be used in a larger system for processing and analyzing text data.

**Concepts:** Dataclasses, Metadata, Logistics, Text analysis, Vector embeddings

## wave/tools/ai/aci/semantic_finder.py
**Purpose:** Finds semantically related code using the Standard Model relationship graph

This file implements a semantic finder that uses a relationship graph to find semantically related code. It loads a semantic index from a JSON file and uses it to calculate semantic distances and traverse the graph. The finder can be used to select optimal context based on semantic understanding of a query's relationship to the codebase graph.

**Concepts:** Semantic graph, Relationship graph, Standard Model, Purpose field hierarchy, Dimension semantics

## wave/tools/ai/aci/temporal_resolver.py
**Purpose:** Resolve canonical source conflicts using git history, file timestamps, and code analysis

This script resolves conflicts between files claiming to be canonical for a specific concept by analyzing git history, file timestamps, and code analysis. It provides a recommendation on which file is the most authoritative source. The script uses a scoring heuristic to rank files based on their git history and file system metadata.

**Concepts:** Canonical source resolution, Git history analysis, File system metadata analysis, Code analysis, Scoring heuristic

## wave/tools/ai/aci/tier_orchestrator.py
**Purpose:** Orchestrates routing queries to the appropriate execution tier based on query intent, complexity, and scope

This file implements a tier orchestrator that routes queries to different execution tiers based on their intent, complexity, and scope. It integrates with SemanticFinder for graph-based context selection and uses a decision matrix to determine the most suitable tier for each query. The orchestrator supports various tiers, including INSTANT, RAG, LONG_CONTEXT, PERPLEXITY, FLASH_DEEP, and HYBRID, each with its own characteristics and use cases.

**Concepts:** Tiered query execution, Query intent analysis, Semantic graph-based context selection, Decision matrix-based routing, Integration with external services (e.g., Gemini API)

## wave/tools/ai/analyze.py
**Purpose:** Local Codebase Analysis Tool that reads files directly from the local filesystem with proper secret exclusions and line-numbered output

This script is a headless AI tool that provides various features such as Adaptive Context Intelligence, token budget awareness, and file search. It can be used in different modes, including ACI mode, one-shot mode, interactive mode, and file search mode. The script also supports various commands, including indexing files, querying with file search, listing existing stores, and deleting stores.

**Concepts:** Adaptive Context Intelligence (ACI), Token budget awareness, File search, Interactive mode, Context filters

## wave/tools/ai/analyze/__init__.py
**Purpose:** Provides main entry points for the modular AI analysis tool

This file serves as the main entry point for the analyze package, exporting key classes and functions for configuration, output, and execution. It follows the Standard Model of Code principles, separating responsibilities into distinct modules and tiers. The package structure is designed to facilitate modular and extensible AI analysis.

**Concepts:** Modular architecture, Standard Model of Code principles, Separation of concerns, Tiers and execution channels, Explicit output contracts

## wave/tools/ai/analyze/clients.py
**Purpose:** ```json
{
    "purpose": "Create API clients for interacting with Google Vertex AI and AI Studio",
    "summary": "This module provides functions to create clients for Google Vertex AI and AI Studio,

## wave/tools/ai/analyze/config.py
**Purpose:** Loads and manages configuration for the analysis system

This module provides a centralized configuration management system for the analysis tool. It loads configuration from YAML files, detects the environment, and assembles the configuration into a single coherent structure. The module uses dataclasses to represent the configuration and provides functions to load and resolve the configuration.

**Concepts:** Configuration management, YAML file loading, Dataclasses, Environment detection, Recursive set resolution

## wave/tools/ai/analyze/context.py
**Purpose:** Builds context from files for AI model input

This module provides functions to list, filter, and read files from the local filesystem, and then build a context string from the file contents. It includes security-sensitive exclusions and supports strategic positioning of critical files. The module is designed to be used during analysis and provides a stateless, impure interface.

**Concepts:** Filesystem traversal, Pattern matching, Security-sensitive exclusions, Context building, Positional strategies

## wave/tools/ai/analyze/modes/__init__.py
**Purpose:** Defines analysis modes for codebase analysis with their respective metadata and behaviors

This module provides a set of analysis modes, each with its own configuration and behavior, to modify how analysis is performed on a codebase. The modes are defined in the MODE_METADATA dictionary and can be accessed through various functions. The module also provides functions to retrieve mode information, list available modes, and check if a mode requires line numbers.

**Concepts:** Analysis modes, Mode metadata, Codebase analysis, Configuration-based behavior modification, Deterministic mode lookup

## wave/tools/ai/analyze/output.py
**Purpose:** Defines the output schema for the Stone Tool contract, including dataclasses for ContextManifest and AnalyzeResult

This module provides a standardized output format for analysis results, following principles of information theory and including metadata for provenance tracking. It defines two main dataclasses: ContextManifest and AnalyzeResult, which capture the context of the analysis and the results, respectively. The module also includes utility functions for computing bundle hashes, estimating costs, and generating unique run IDs.

**Concepts:** Dataclasses, Information Theory, Provenance Tracking, Context Manifest, Analyze Result

## wave/tools/ai/analyze/search/__init__.py
**Purpose:** Implements a Retrieval Augmented Generation (RAG) pipeline for file search using the Gemini File Search API

This package provides a self-contained RAG pipeline for indexing and searching files using semantic search. It integrates with the Gemini File Search API and stores indexed files for reuse. The package is designed to function independently of other analysis modes and provides a complete store lifecycle.

**Concepts:** Retrieval Augmented Generation (RAG), Semantic search, Indexing and storing files, Gemini File Search API integration, Store lifecycle management

## wave/tools/ai/analyze/session.py
**Purpose:** Manages and logs conversation sessions for later analysis and debugging

This module provides functionality for logging conversation turns, saving session logs to files, and retrieving session statistics. It implements the AUDIT TRAIL concept, recording all interactions for later analysis and debugging. The module uses a stateful approach, accumulating session turns and metadata, and provides methods for clearing the session state and setting the model for the current session.

**Concepts:** Session management, Logging, AUDIT TRAIL, Stateful design, File I/O

## wave/tools/ai/analyze/tiers/__init__.py
**Purpose:** Defines the ACI Execution Tier System for routing queries to appropriate tiers based on analysis requirements

This package provides a coordination layer for the ACI Execution Tier System, which includes six tiers with different trade-offs between latency, cost, depth, and scope. The package defines an enum for the tiers, a function to convert string to tier enum, and a dictionary of tier characteristics for routing decisions. The tiers are designed to handle various analysis requirements, from instant answers to comprehensive analysis with external research.

**Concepts:** ACI Execution Tier System, Tier enum, Tier characteristics, Routing decisions, Adaptive Context Intelligence

## wave/tools/ai/analyze/tiers/base.py
**Purpose:** Defines the contract that all tier executors must implement for polymorphic tier selection

This file provides an abstract base class for tier executors, defining the interface for execution, handling, and metadata retrieval. It also includes data classes for tier requests and responses, as well as a function for standardized error handling. The design enables flexible and modular tier selection and execution.

**Concepts:** Abstract Base Class (ABC), Polymorphism, Tier Execution, Data Classes, Error Handling

## wave/tools/ai/analyze/tiers/long_context.py
**Purpose:** Executes long context analysis using full codebase context and Gemini API

The LongContextExecutor class is a tier implementation that sends all context to the model and asks it to reason over the full picture. It is best suited for architecture questions, code understanding, pattern analysis, and comprehensive reviews. The class handles API client initialization, query execution, and result processing.

**Concepts:** Long context analysis, Gemini API, API client initialization, Query execution, Result processing

## wave/tools/ai/boundary_analyzer.py
**Purpose:** Validates PROJECT_elements internal organization against declared boundaries

This script analyzes the directory structure of a project and checks if it matches the declared boundaries, including realms and concordances. It provides a report on the alignment score, issues, and recommendations for improvement. The script can be run in different modes, including full analysis, quick check, and continuous monitoring.

**Concepts:** Boundary analysis, Realms, Concordances, Codome, Contextome

## wave/tools/ai/cerebras_doc_validator.py
**Purpose:** Validates documentation for overclaiming language using the Cerebras API

This script validates documentation files for overclaiming language by sending the content to the Cerebras API and parsing the response. It supports validating single files or directories and generates a report with the results. The report includes the number of MUST_FIX issues found in each file and a summary of the total issues found.

**Concepts:** Cerebras API, Documentation validation, Overclaiming language detection, JSON parsing, Rate limiting

## wave/tools/ai/cerebras_enricher.py
**Purpose:** ```json
{
    "purpose": "Enriches Collider output with semantic meaning using Cerebras API",
    "summary": "This script enriches the output of the Collider tool with semantic meaning by utilizing th

## wave/tools/ai/cerebras_hire.py
**Purpose:** Exclusive access control for Cerebras API using a global lock file

This script provides a mechanism for multiple agents to access the Cerebras API without hitting rate limits. It uses a global lock file to grant exclusive access to one agent at a time, with automatic expiration after a specified duration. The script can be used as a command-line tool or imported as a Python module to manage Cerebras access.

**Concepts:** Exclusive access control, Global lock file, Automatic expiration, Context manager, Command-line interface

## wave/tools/ai/cerebras_queue.py
**Purpose:** Manages a centralized queue for Cerebras API requests to prevent rate limit chaos from multiple agents.

This script implements a file-based queue with locking to manage Cerebras API requests. It provides functionality to submit requests, process the queue, and check queue status. The queue is designed to handle rate limiting and automatic backoff on 429 errors. The script uses a context manager for queue locking and provides a worker function to process pending requests in the queue.

**Concepts:** Rate limiting, Queue management, Locking mechanism, Cerebras API, Error handling

## wave/tools/ai/cerebras_rapid_intel.py
**Purpose:** Cerebras Rapid Intelligence System for code analysis and gap detection

This script is designed to analyze a codebase, detect gaps such as missing documentation, broken links, and incomplete implementations, and generate comprehensive reports. It utilizes the Cerebras API for natural language processing and can process multiple files in parallel. The system consists of a scanner, analyzer, reporter, and filler, and stores intelligence data in a database.

**Concepts:** Code analysis, Gap detection, Natural language processing, Cerebras API, Parallel processing

## wave/tools/ai/cerebras_spiral_intel.py
**Purpose:** Cerebras Spiral Intelligence System for multi-pass iterative refinement of codebase understanding

This system performs a series of passes to analyze and understand a codebase, with each pass building on the previous one to increase confidence in the results. The system tracks confidence, gaps, and errors, and provides outputs such as file intelligence, spiral state, and lap history. The system can be run in parallel with multiple workers to improve performance.

**Concepts:** Multi-pass iterative refinement, Confidence tracking, Gap analysis, Parallel processing, Codebase understanding

## wave/tools/ai/cerebras_tagger.py
**Purpose:** Cerebras Batch Tagger for fast D1-D8 classification of code files

This script uses the Cerebras API for bulk file classification and validates the results with Claude for accuracy. It provides a command-line interface for tagging files, validating results, and running the full pipeline. The script handles rate limiting, error handling, and JSON parsing for the Cerebras API responses.

**Concepts:** Cerebras API, Rate limiting, JSON parsing, Command-line interface, Error handling

## wave/tools/ai/cerebras_zoo_compare.py
**Purpose:** Compare external knowledge to CODE_ZOO taxonomy using Cerebras AI

This script compares external text to CODE_ZOO concepts, identifying matches, gaps, enhancements, and conflicts. It utilizes the Cerebras AI API to rapidly process documents and provides output in structured JSON and human-readable YAML formats. The script supports various modes, including comparing SWEBOK to CODE_ZOO, comparing any text file, and interactive mode.

**Concepts:** CODE_ZOO taxonomy, Cerebras AI API, Text chunking, Rate limiting, YAML parsing

## wave/tools/ai/context_filters.py
**Purpose:** Applies intelligent file filtering to prevent token quota disasters.

This module provides a set of functions to filter files based on various criteria such as exclude patterns, maximum age, maximum file size, and sorting. It also includes a function to estimate the number of tokens in a list of files. The apply_filters function applies all configured filters to a list of files and returns the filtered and sorted list.

**Concepts:** File filtering, Exclude patterns, Maximum age, Maximum file size, Sorting

## wave/tools/ai/debug_models.py
**Purpose:** Lists models in the Google Cloud AI Platform Model Garden, specifically searching for Gemini models

This script initializes the Google Cloud AI Platform client, lists models in the Model Garden using the low-level API, and searches for models containing 'gemini' in their name. It handles exceptions and prints the results or error messages. The script is designed to test access to the Model Garden endpoint and find specific models.

**Concepts:** Google Cloud AI Platform, Model Garden, Low-level API, Exception handling, Model listing and filtering

## wave/tools/ai/deck/CARD-ANA-001.yaml
**Purpose:** Run full Collider analysis pipeline on a codebase

This YAML file defines a workflow for executing a Collider analysis on a codebase, generating various output files, and handling success and failure outcomes. The workflow consists of multiple steps, including running the analysis pipeline, reviewing output files, and verifying visualization. The file also specifies preconditions, phase gates, and cost estimates for the workflow.

**Concepts:** Collider analysis, Workflow definition, Pipeline execution, Output file generation, Error handling

## wave/tools/ai/deck/CARD-AUD-001.yaml
**Purpose:** Defines a skeptical audit card to identify dead code, integration failures, and validation issues after creating new code or schemas

This YAML file describes a card that triggers a systematic self-criticism process to identify potential issues after creating new code or schemas. The card has preconditions, steps, and outcomes that guide the audit process. It also provides context injection, cost estimation, and tags for categorization. The card is designed to be played after sessions that create new artifacts, such as feature implementation or schema creation.

**Concepts:** Skeptical audit, Systematic self-criticism, Dead code detection, Integration failure identification, Validation theater

## wave/tools/ai/deck/CARD-DOC-001.yaml
**Purpose:** Defines a specification document creation process

This YAML file outlines a step-by-step process for creating or updating a formal specification document, including preconditions, steps, outcomes, and rollback procedures. The process is designed to ensure that a concept is validated and scoped before a specification document is created. The document is part of a larger workflow, with specific outcomes and state changes that occur upon success or failure.

**Concepts:** Specification document creation, Workflow management, Preconditions and checkpoints, Outcome-based process design, Rollback procedures

## wave/tools/ai/deck/CARD-GIT-001.yaml
**Purpose:** Defines a git commit checkpoint process to save progress and maintain an audit trail

This YAML file outlines a step-by-step process for creating a git commit to checkpoint current progress. It includes preconditions, steps, outcomes, and rollback procedures to ensure a consistent and reliable commit process. The process is designed to be used frequently to avoid losing work and maintain an audit trail.

**Concepts:** Git commit, Checkpoint, Audit trail, Preconditions, Rollback procedures

## wave/tools/ai/deck/CARD-OPP-059.yaml
**Purpose:** Defines a task for Sprawl Consolidation Infrastructure improvements

This YAML file describes a task for managing repository sprawl, including infrastructure improvements and cleanup. The task has been partially completed, with several steps already taken, and outlines remaining work and outcomes. The file is auto-generated with a high confidence level.

**Concepts:** Task definition, Repository management, Infrastructure improvements, Auto-generated content,  Confidence scoring

## wave/tools/ai/deck/CARD-OPP-060.yaml
**Purpose:** Defines the Autonomous Enrichment Pipeline (AEP) MVP task

This YAML file describes the implementation of the Autonomous Enrichment Pipeline, which automates research loops, fills knowledge gaps, and computes confidence scores. The pipeline runs on GCP and auto-promotes tasks when a certain confidence threshold is met. The file outlines the scope, preconditions, cost, and outcomes of the task.

**Concepts:** Autonomous Enrichment Pipeline (AEP), Research loops, Confidence scores, Auto-promotion, GCP infrastructure

## wave/tools/ai/deck/CARD-OPP-061.yaml
**Purpose:** Defines a task to fix HSL Daemon Locally with associated preconditions, cost, and outcomes

This YAML file represents a task named 'Fix HSL Daemon Locally' with a unique identifier 'CARD-OPP-061'. It includes details such as preconditions, cost estimation, and possible outcomes. The task seems to be related to infrastructure and has been auto-generated from an inbox item 'OPP-061'.

**Concepts:** Task definition, Preconditions, Cost estimation, Outcomes, Auto-generation

## wave/tools/ai/deck/CARD-OPP-062.yaml
**Purpose:** Defines a task for BARE Phase 2 - CrossValidator Implementation

This YAML file represents a task named CARD-OPP-062, which is part of the BARE Phase 2 - CrossValidator Implementation. It outlines the task's preconditions, cost, and possible outcomes. The task is auto-generated from inbox:OPP-062 with a confidence level of 35.

**Concepts:** Task definition, Preconditions, Cost estimation, Outcome management, Auto-generation

## wave/tools/ai/deck/CARD-OPP-063.yaml
**Purpose:** Defines a task for verifying GCS Mirror Post-Triage

This YAML file represents a task named 'Verify GCS Mirror Post-Triage' with a specific set of preconditions, cost, and outcomes. It appears to be auto-generated from an inbox item OPP-063. The task is related to infrastructure and has a medium risk level.

**Concepts:** Task definition, Preconditions, Cost estimation, Outcomes, Auto-generation

## wave/tools/ai/deck/CARD-OPP-064.yaml
**Purpose:** Defines a task for implementing a hierarchical tree layout for file view

This YAML file represents a task named CARD-OPP-064, which aims to implement a hierarchical tree layout for file view. The task has preconditions, cost estimates, and defined outcomes for success and failure. The file is auto-generated with a confidence level of 85%.

**Concepts:** Task definition, Hierarchical tree layout, File view visualization, Preconditions and outcomes, Cost estimation

## wave/tools/ai/deck/CARD-OPP-065.yaml
**Purpose:** Defines a task for an Always-Green Continuous Refinement Pipeline

This YAML file represents a task named Always-Green Continuous Refinement Pipeline, which is auto-generated from inbox:OPP-065. It outlines the task's properties, including preconditions, cost, and outcomes. The task appears to be related to infrastructure and has a medium risk level.

**Concepts:** Task definition, Auto-generation, Preconditions, Cost estimation, Outcome tracking

## wave/tools/ai/deck/CARD-OPP-066.yaml
**Purpose:** Defines a task to handle Gemini API rate limiting (429) in a project management system

This YAML file represents a task to handle Gemini API rate limiting, with a confidence level of 95%. It includes preconditions, cost estimates, and possible outcomes. The task is auto-generated from an inbox item OPP-066 and has a medium risk level.

**Concepts:** Task management, API rate limiting, Project planning, Risk assessment, Auto-generated tasks

## wave/tools/ai/deck/CARD-OPP-067.yaml
**Purpose:** Defines a task for implementing a consolidated Health Model

This YAML file represents a task, CARD-OPP-067, which aims to implement a consolidated Health Model. The task has preconditions, estimated costs, and defined outcomes for success and failure. The file was auto-generated from an inbox item with a confidence level of 70%.

**Concepts:** Task definition, Health Model implementation, Preconditions and outcomes, Cost estimation, Auto-generation from inbox items

## wave/tools/ai/deck/CARD-OPP-071.yaml
**Purpose:** Defines a task to fix MISALIGNMENT reporting issues

This YAML file describes a task to resolve a specific issue (OPP-071) related to MISALIGNMENT reporting, with details on preconditions, cost, and potential outcomes. The task is auto-generated with a confidence level of 70%. The file provides a structured format for tracking and managing the task.

**Concepts:** Task definition, Issue tracking, Auto-generation, Confidence scoring, Workflow management

## wave/tools/ai/deck/CARD-OPP-076.yaml
**Purpose:** Defines a task for implementing a collider Mcafee CLI command

This YAML file represents a task with a specific id, title, and description. It outlines the preconditions, cost, and potential outcomes of the task, including success and failure scenarios. The task is auto-generated with a confidence level of 70%.

**Concepts:** Task definition, CLI command implementation, Preconditions and cost estimation, Outcome tracking, Auto-generation with confidence level

## wave/tools/ai/deck/CARD-OPP-077.yaml
**Purpose:** Defines a task for refining orphan detection entry point patterns

This YAML file represents a task named CARD-OPP-077, which aims to refine orphan detection entry point patterns. The task has preconditions, estimated costs, and defined outcomes for success and failure. It was auto-generated from an inbox item with a confidence level of 70%.

**Concepts:** Task definition, Orphan detection, Entry point patterns, Auto-generation, Confidence scoring

## wave/tools/ai/deck/CARD-OPP-082.yaml
**Purpose:** Defines a task for creating a pathogen impact inventory

This YAML file describes a task with an ID of CARD-OPP-082, which involves creating a pathogen impact inventory. The task has preconditions, cost estimates, and outcomes defined. It was auto-generated from an inbox item with a confidence level of 70%. The task is related to the DESIGNING and IMPLEMENTING phases.

**Concepts:** Task definition, Pathogen impact inventory, Preconditions, Cost estimation, Outcome definition

## wave/tools/ai/deck/CARD-OPP-083.yaml
**Purpose:** Defines a task for selecting and validating golden repositories for regression testing

This YAML file represents a task named CARD-OPP-083, which involves selecting and validating golden repositories for regression testing. The task has preconditions, cost estimates, and defined outcomes for success and failure. The file was auto-generated from an inbox item with a confidence level of 70%.

**Concepts:** Task definition, Regression testing, Golden repositories, Preconditions, Outcome-based planning

## wave/tools/ai/deck/CARD-OPP-084.yaml
**Purpose:** Defines a task to add Goodharts Law protection mechanism

This YAML file represents a task to implement a protection mechanism based on Goodharts Law, with preconditions, cost estimates, and possible outcomes. The task is auto-generated from an inbox item OPP-084 with a confidence level of 70%. The file provides details about the task, including its description, preconditions, cost, and expected outcomes.

**Concepts:** Goodharts Law, Task definition, Preconditions, Cost estimation, Outcome tracking

## wave/tools/ai/deck/CARD-RES-001.yaml
**Purpose:** Defines a research card for conducting deep research using Perplexity AI

This YAML file outlines a research workflow that utilizes Perplexity AI to conduct deep research on a given topic. The workflow includes preconditions, steps, and outcomes, ensuring a structured approach to research. The file provides a clear framework for researchers to follow, including the use of specific models and the review of output files.

**Concepts:** Perplexity AI, Research workflow, Preconditions, State changes, Outcome-based design

## wave/tools/ai/deck/CARD-RES-002.yaml
**Purpose:** Defines a research card for conducting analysis using Gemini models

This YAML file outlines a research card that utilizes Gemini models for deep analysis. It specifies preconditions, steps, and outcomes for the research process, including running Gemini analysis, reviewing responses, and saving significant findings. The card also tracks state changes, unlocks other cards, and updates meters for discovery and focus.

**Concepts:** Gemini models, Research card, Analysis workflow, State machine, Dependency injection

## wave/tools/ai/deck/CARD-SES-001.yaml
**Purpose:** Initialize a new agent session by loading project context, checking for active sprint, scanning inbox for opportunities, and displaying the decision deck state.

This YAML file defines a card in a decision deck that initializes a new agent session. It loads critical context, checks for active sprints and inbox opportunities, and displays the decision deck state. The card has preconditions, steps, outcomes, and rollback procedures. It also provides context injection, cost estimates, and tags for categorization.

**Concepts:** Decision Deck, Session Initialization, Context Loading, Sprint Management, Inbox Scanning

## wave/tools/ai/deck/CARD-SYS-001.yaml
**Purpose:** Defines a system configuration audit and cleanup process to identify and rectify inconsistencies, redundancies, and deprecations.

This YAML file outlines a step-by-step procedure for auditing and cleaning up system configurations, ensuring consistency and adherence to project standards. It includes preconditions, steps, outcomes, and rollback procedures to maintain system stability. The process aims to remove duplicates, deprecated entries, and misconfigurations, and validate system integrity through tests and health checks.

**Concepts:** System configuration audit, Canonical sources, Deduplication, Technical debt reduction, System validation

## wave/tools/ai/deck/CARD-WLD-000.yaml
**Purpose:** Defines a wildcard action card for executing actions outside the deck

This YAML file describes a wildcard action card that allows for the execution of actions not covered by any other card in the deck. It requires explicit justification and is intended for use when no suitable card exists. The card logs its usage for pattern detection and potential new card creation.

**Concepts:** Wildcard action, Justification, Pattern detection, Deck expansion, State changes

## wave/tools/ai/deck/deck_context.py
**Purpose:** Generates context summaries about the Decision Deck for injection into AI queries

This file provides functions to generate context summaries about the Decision Deck, including current meter values, recent card plays, and available cards. It allows AI to be aware of the current state of the deck and make informed decisions. The file includes functions to get specific components, such as meters, recent plays, and available cards, as well as a function to generate a complete deck state summary.

**Concepts:** Decision Deck, Context Summaries, AI Queries, Meter Values, Card Plays

## wave/tools/ai/deck/deck_router.py
**Purpose:** Decision Deck Router for AI Agents with Constrained Action Space

This module implements the 'Game Master' layer from the Decision Deck architecture, loading certified moves from YAML definitions, evaluating preconditions, routing natural language intents to cards, and providing structured action execution. The Deck constrains AI agents to certified moves rather than free-form improvisation. Each card has preconditions, steps, expected outcomes, and rollback procedures.

**Concepts:** Decision Deck Architecture, Certified Moves, Natural Language Intent Routing, Constrained Action Space, Precondition Evaluation

## wave/tools/ai/deck/fabric_bridge.py
**Purpose:** Bridges the gap between system-level Communication Fabric metrics and agent-level decision making.

This module provides fabric-aware precondition checks, risk assessment based on current fabric state, context injection with fabric awareness, and card filtering based on system health. It translates system-level metrics into agent-actionable signals, enabling agents to make informed decisions. The module uses caching to optimize performance and provides a simplified state object for agent decisions.

**Concepts:** Communication Fabric, Agent-level decision making, Risk assessment, Context injection, Caching

## wave/tools/ai/deck/play_card.py
**Purpose:** Execute a certified move from the Decision Deck

This script loads a card by ID, verifies preconditions, executes steps with checkpoints, validates outcomes, updates meters, and handles rollback if needed. It provides a command-line interface to play cards and supports dry runs and auto mode. The script uses YAML files to store card definitions, meters, and play logs.

**Concepts:** Decision Deck, Card execution, Precondition checking, Step execution, Meter updates

## wave/tools/ai/gemini_cache_demo.py
**Purpose:** Demonstrates how to use Google Gemini 2.0 Flash to analyze a mirrored codebase directly from Google Cloud Storage without downloading it.

This script uses the Google Gemini 2.0 Flash model to analyze a set of files stored in Google Cloud Storage, providing a summary of the purpose of the 'Repository Mirror' feature, an explanation of how the 'archive.py' script handles file discovery, and a suggested improvement for the archive tool. The script authenticates with Google Cloud using the gcloud CLI and initializes a client with explicit credentials to interact with the Vertex AI API.

**Concepts:** Google Gemini 2.0 Flash, Google Cloud Storage, Vertex AI API, gcloud CLI, Authentication with access token

## wave/tools/ai/gemini_genai_test.py
**Purpose:** Test the google-genai package with Vertex AI backend for generating content

This script tests the google-genai package by using the Vertex AI backend to generate content from a specified model. It creates a client instance with the Vertex AI backend and uses it to generate content based on a given prompt. The response from the model is then printed to the console.

**Concepts:** Vertex AI backend, google-genai package, Content generation, Client instance, Model specification

## wave/tools/ai/gemini_status.py
**Purpose:** Gemini API Status & Diagnostics Tool for real-time observability and error diagnosis

This script provides a command-line interface to monitor and diagnose Gemini API usage, quotas, and errors. It analyzes session data, checks quota limits, and recommends optimal models based on current usage. The tool also includes error patterns and diagnoses to help resolve common issues.

**Concepts:** Gemini API, Quota limits, Error diagnosis, Session analysis, Model recommendation

## wave/tools/ai/gemini_test_simple.py
**Purpose:** Simple test script for Google's Gemini AI model using Vertex AI SDK

This script initializes a Vertex AI project, loads the Gemini 2.0 model, and generates a response to a simple math question. It uses the Vertex AI SDK to interact with the model and prints the response text. The script is a basic example of using the Gemini model for text generation.

**Concepts:** Vertex AI SDK, GenerativeModel, Google AI SDK, Gemini AI model, Text generation

## wave/tools/ai/graph_engine.py
**Purpose:** Converts natural language queries to Cypher queries for Neo4j graph database

The GraphEngine class connects to a Neo4j database and uses a language model to generate Cypher queries from natural language input. It provides methods to close the database connection, generate schema summaries, and execute queries. The class relies on environment variables for database credentials and API keys.

**Concepts:** Natural Language Processing (NLP), Cypher query language, Neo4j graph database, Language models, API integration

## wave/tools/ai/hf_space.py
**Purpose:** HuggingFace CLI for chat, image generation, and space access

This script provides a command-line interface to interact with HuggingFace models and spaces, allowing users to chat with language models, generate images, and access various endpoints. It supports multiple commands, including chat, image, models, info, and call, each with its own set of options and arguments. The script uses the HuggingFace Inference API and Gradio Client to interact with models and spaces.

**Concepts:** HuggingFace Inference API, Gradio Client, Language models, Image generation, Command-line interface

## wave/tools/ai/hf_spaces.py
**Purpose:** HuggingFace Spaces API Tool for generating images and transcribing audio

This script provides a command-line interface to access HuggingFace Spaces, allowing users to generate images using various models and transcribe audio using Whisper. It uses the gradio_client library to interact with the HuggingFace Spaces API. The script supports multiple models, including FLUX and Stable Diffusion, and allows users to customize the generation process with parameters such as prompt, model, width, height, and seed.

**Concepts:** HuggingFace Spaces, gradio_client, image generation, audio transcription, Whisper

## wave/tools/ai/industrial_ui.py
**Purpose:** Provides a consistent ANSI-styled terminal output for AI tools

This Python module defines a set of classes for generating industrial-style terminal output, with support for different tools and customizable colors. It includes classes for Gemini and Perplexity UI, each with its own primary color and accent color. The module provides methods for printing headers, sections, items, progress bars, and other elements. The classes are designed to be extensible, allowing for easy addition of new tools and customization of the output.

**Concepts:** ANSI escape codes, Terminal output styling, Object-Oriented Programming (OOP), Inheritance, Polymorphism

## wave/tools/ai/insights_generator.py
**Purpose:** Generates AI insights from Collider output using Vertex AI Gemini

This script reads Collider's unified_analysis.json, extracts key metrics, sends them to Vertex AI Gemini for pattern analysis, and outputs structured ai_insights.json. It uses the gcloud CLI, Vertex AI API, and GCS mirror. The script provides a command-line interface for specifying input, output, and model options.

**Concepts:** Collider output analysis, Vertex AI Gemini integration, GCS mirror configuration, Command-line interface, Subprocess execution

## wave/tools/ai/intel.py
**Purpose:** Unified AI Subsystem Query Interface for providing context to AI agents

This file provides a unified interface for querying AI context, supporting various context sets, custom components, and output formats. It loads data from state files, computes health status and alerts, and formats the context for output. The interface can be accessed via CLI, import, or file reads.

**Concepts:** Context Sets, Data Loaders, Formatters, Custom Components, CLI Interface

## wave/tools/ai/laboratory_bridge.py
**Purpose:** ```json
{
    "purpose": "Acts as a bridge between the Wave agent and the Particle scientist, invoking the Laboratory facade and returning parsed results.",
    "summary": "This module provides a stab

## wave/tools/ai/list_models.py
**Purpose:** Analysis failed

## wave/tools/ai/loop.py
**Purpose:** Executes the research validation loop using Gemini and Perplexity

This script provides a convenience wrapper for executing the research validation loop, which involves formulating a research question, performing external research using Perplexity, and synthesizing the results with local context using Gemini. The script supports various modes, including direct Perplexity queries, Gemini synthesis, and a full loop that combines both. It uses command-line arguments to customize the workflow and provides a clear output of the research findings and recommended actions.

**Concepts:** Research validation loop, Gemini, Perplexity, Command-line arguments, Subprocess execution

## wave/tools/ai/observe_session.py
**Purpose:** Real-time observer for analyze.py interactive sessions

This script streams interactive chat session logs in real-time using a file tail pattern. It can watch a specific session by PID, the most recent session, or start analyze.py and watch it. The observer reads from a session log file and displays turns in real-time.

**Concepts:** Real-time session observation, File tail pattern, Interactive chat session logs, PID-based session tracking, PTY-based process interaction

## wave/tools/ai/openclaw-implementation/FRESH_START_CHECKLIST.md
**Purpose:** Provides a checklist for a fresh start of the OpenClaw implementation, including what to delete and what to keep.

This file serves as a guide for reimplementing OpenClaw from scratch, outlining the steps to safely delete regenerable data and preserve irreplaceable information such as identity, sessions, and custom scripts. It provides a clear procedure for backing up critical data before wiping the system and restoring it after a fresh install.

**Concepts:** OpenClaw implementation, Fresh start, Data preservation, Backup and restore, Docker and system management

## wave/tools/ai/openclaw-implementation/VPS_INVENTORY_20260204.md
**Purpose:** Documents the complete system state of a VPS, including hardware, software, and network configurations.

This file provides a detailed inventory of a VPS, including its hardware and software components, network configurations, and installed services. It also identifies potential problems and provides recommendations for solutions. The VPS is running Ubuntu 24.04.3 LTS and has various services installed, including Docker, Ollama, Tailscale, and Node.js.

**Concepts:** VPS inventory, System documentation, Hardware and software configurations, Network configurations, Troubleshooting and problem-solving

## wave/tools/ai/openclaw-implementation/openclaw.json
**Purpose:** Configuration file for OpenCLAW implementation

This JSON file provides configuration settings for the OpenCLAW implementation, including general settings, module configurations, agent defaults, channel settings, and filesystem paths. It appears to be used for setting up and customizing the behavior of the OpenCLAW system. The configuration includes settings for timezone, admin access, module enablement, model selection, and channel permissions.

**Concepts:** Configuration file, JSON format, Modular design, Agent-based architecture, Channel management

## wave/tools/ai/perplexity_research.py
**Purpose:** Perplexity Research Tool for executing research queries using Perplexity API

This script provides a command-line interface for executing research queries using Perplexity API. It supports various models, auto-saves research output, and provides options for customizing the output. The script integrates with Doppler for secrets management and Industrial UI for styled output.

**Concepts:** Perplexity API, Doppler secrets management, Industrial UI, Command-line interface, Auto-save research output

## wave/tools/ai/research/__init__.py
**Purpose:** Provides research tools for external knowledge acquisition using AI services

This module offers precision context fetching capabilities to fill knowledge gaps identified by the Codome Completeness Index (CCI) using external AI services like Perplexity SONAR-PRO. It includes various classes and functions for fetching guidance and research results. The module exports several key classes and functions for use in other parts of the application.

**Concepts:** External knowledge acquisition, AI services, Precision context fetching, Codome Completeness Index (CCI), Perplexity SONAR-PRO

## wave/tools/ai/research/precision_fetcher.py
**Purpose:** Fetches precision context from Perplexity SONAR-PRO to provide actionable guidance for fixing gaps in code analysis tools

The precision_fetcher module is designed to fetch external knowledge from Perplexity SONAR-PRO when the CCI attribution reveals OUR_FAULT gaps. It provides a structured approach to acquiring actionable guidance for fixing these gaps, using a combination of data models, configuration management, rate limiting, and budget control. The module uses a PrecisionContextFetcher class to interact with the Perplexity API and retrieve guidance in the form of JSON data.

**Concepts:** Precision Context Fetcher, Perplexity SONAR-PRO, CCI attribution, OUR_FAULT gaps, Actionable guidance

## wave/tools/ai/setup_agent_builder.sh
**Purpose:** Guides the user through setting up a Vertex AI Agent Builder for a 'Chat with Codebase' app

This script provides a step-by-step guide for setting up a Vertex AI Agent Builder using the Google Cloud Console. It retrieves the current project ID and provides a target source path, then prompts the user to follow manual steps in their browser to complete the setup. The script finally opens the Google Cloud Console page for the user to access the Data Stores page.

**Concepts:** Vertex AI Agent Builder, Google Cloud Console, Cloud Storage, Data Stores, Bash scripting

## wave/tools/ai/setup_rag.py
**Purpose:** RAG setup and data consolidation tool for Vertex AI Agent Builder

This script provides a set of commands to automate the setup of Vertex AI Agent Builder, including initializing the RAG, bundling documentation, and checking the health of necessary APIs. It uses the Google Cloud SDK and provides guidance for the user to complete the setup process. The script is designed to simplify the process of setting up the knowledge infrastructure for the Agent Builder.

**Concepts:** Vertex AI Agent Builder, RAG setup, Google Cloud SDK, API health check, Data consolidation

## wave/tools/ai/test_vertex_sdk.py
**Purpose:** Tests the Vertex AI SDK with specific generative models

This script initializes the Vertex AI SDK, tests a list of generative models by attempting to generate content, and reports the success or failure of each model. The script stops and returns as soon as it finds a working model. It requires a project ID and location to be set, and uses the vertexai library to interact with the Vertex AI API.

**Concepts:** Vertex AI SDK, Generative models, Error handling, API initialization, Content generation

## wave/tools/ai/token_estimator.py
**Purpose:** Estimate token count of files with varying accuracy levels

This module provides functions to estimate the token count of files using different methods, including fast, medium, and accurate estimations. It also includes a function to check if the estimated token count is within a specified budget. The module uses the tiktoken library for accurate token counting and provides a fallback to medium accuracy if tiktoken is not available.

**Concepts:** Token estimation, Tiktoken library, File size estimation, Character-based estimation, Budget checking
