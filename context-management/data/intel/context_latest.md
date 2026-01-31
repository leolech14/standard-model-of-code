# Context: context-management/tools/refinery

## context-management/tools/refinery/GEMINI.md
**Purpose:** Describes the Data Logistics Subsystem for managing data flow from ingestion to refined intelligence

The Data Logistics Subsystem implements the Logistics Hyper-Layer, tracking data objects with Waybills for provenance. It consists of tools like pipeline.py, corpus_inventory.py, and refinery.py, which work together to process data from ingestion to refinement. The subsystem uses concepts like Copresence to track relationships between data objects.

**Concepts:** Logistics Hyper-Layer, Waybill, Copresence, Batch ID, Provenance tracking

## context-management/tools/refinery/__init__.py
**Purpose:** Initializes the Context Refinery Module

The Context Refinery Module is a hybrid system that maps, refines, atomizes, and recompiles context on demand. It consists of several components, including corpus inventory, boundary mapping, delta detection, atom generation, and state synthesis. The module follows a philosophy of breaking down the repository into semantic units and reaggregating them for reasoning.

**Concepts:** Context Refinery, Hybrid System, Semantic Units, Collider Logic

## context-management/tools/refinery/atom_generator.py
**Purpose:** Creates RefineryNode entries from source files based on the 'Atomization' principle

This script generates atoms from files by creating a RefineryNode entry for each file, including its metadata, dimensions, and relationships. It can process all files, a specific boundary, a single file, or only changed files. The script uses various functions to infer the layer and role of each file based on its path and name.

**Concepts:** Atomization, RefineryNode, File metadata extraction, Layer and role inference, Batch processing

## context-management/tools/refinery/boundary_mapper.py
**Purpose:** Maps analysis_sets.yaml to BoundaryNode entries in the RefineryNode format

This script maps boundaries defined in analysis_sets.yaml to BoundaryNode entries, creating a semantic map of all defined boundaries. It uses configuration files and command-line arguments to determine which boundaries to map and where to output the results. The script provides a summary of the mapping process, including the number of boundaries and files mapped.

**Concepts:** Boundary mapping, RefineryNode format, analysis_sets.yaml, Semantic mapping, Command-line arguments

## context-management/tools/refinery/context-management/intelligence/chunks/courier_demo.json
**Purpose:** Stores a collection of chunks extracted from a Markdown document, containing information about Category Theory and its potential integration with a Standard Model.

This JSON file contains a list of chunks, each representing a section of a Markdown document, with metadata such as source file, chunk type, relevance score, and waybill information. The chunks cover topics related to Category Theory, including its key concepts, and how it can be integrated with a Standard Model. The file also includes information about the processing history of each chunk, including checkout, work start, work complete, and checkin events.

**Concepts:** Category Theory, Chunking, Waybill, Relevance Score, Standard Model

## context-management/tools/refinery/context-management/intelligence/chunks/logistics_demo.json
**Purpose:** Stores data logistics subsystem information in JSON format

This JSON file contains information about the data logistics subsystem, including node counts, total tokens, and node details such as content, source files, and relevance scores. The data appears to be related to a context management system, with nodes representing different sections of a Markdown file. The file also includes information about the processing of the data, including the creation of waybills and the tracking of parcels.

**Concepts:** Data logistics subsystem, Context management, Node counting, Tokenization, Waybills, Parcel tracking

## context-management/tools/refinery/corpus_inventory.py
**Purpose:** Scans the repository and produces a complete inventory of all files, categorized by type, language, and size.

This script scans a repository, categorizes files by language and purpose, and generates a JSON inventory report. It can be run in full or quick mode, and supports custom output paths. The report includes file metadata, language and category summaries, and a list of files with their corresponding hashes and sizes.

**Concepts:** File system scanning, Language detection, Categorization, Hashing, Inventory reporting

## context-management/tools/refinery/delta_detector.py
**Purpose:** Detects changes in the corpus inventory by comparing the current state to the previous state.

The delta detector script compares the current corpus inventory to the previous inventory and detects changes, including added, modified, and deleted files. It implements the 'Delta-First' principle, only reprocessing what has changed. The script outputs a delta report in JSON format, which includes a summary of the changes and detailed information about the added, modified, and deleted files.

**Concepts:** Delta detection, Corpus inventory, State management, JSON reporting, Command-line arguments

## context-management/tools/refinery/docs_audit.py
**Purpose:** Audits active documentation for broken internal links, unresolved placeholders, and validated_* file integrity

This script scans markdown files in the context-management/docs directory, checks for broken links, unresolved placeholders, and validated_* file integrity, and generates a report with the findings. The report includes the number of files scanned, the number of active files, and the results of the checks. The script also provides suggestions for fixing the issues found.

**Concepts:** Markdown file scanning, Regular expression pattern matching, Dataclass-based report generation, Git SHA retrieval, Path manipulation

## context-management/tools/refinery/pipeline.py
**Purpose:** Orchestrates the flow of data parcels from Ingestion to Chunking in the Logistics Pipeline

The Logistics Pipeline is a data processing pipeline that ingests files, refines them, and exports the results. It consists of two phases: Ingestion and Refinement. The pipeline uses a configuration file and command-line arguments to control its behavior. It also uses a semantic matching mechanism to drive the attention mechanism gate.

**Concepts:** Data pipeline, Ingestion, Refinement, Semantic matching, Configuration management

## context-management/tools/refinery/query_chunks.py
**Purpose:** Search consolidated knowledge chunks by text match with relevance ranking

This script provides a simple text search interface over refinery chunks, allowing users to query chunks by search term and retrieve relevant results. The search results are ranked by relevance and can be limited in number. The script also provides options to show full chunk content and output results as JSON.

**Concepts:** Text search, Relevance ranking, Chunk processing, JSON output, Command-line interface

## context-management/tools/refinery/reference_analyzer.py
**Purpose:** Analyzes and processes the reference library for academic purposes

The ReferenceAnalyzer class systematically processes the reference library by analyzing remaining references, building a full-text search index, optimizing caption extraction, and extracting holon hierarchies. It integrates with the Refinery subsystem architecture and provides methods for getting text content, scanning pending analyses, prioritizing references, building a full-text index, and filtering image artifacts. The class also generates batch analysis requests for multiple references.

**Concepts:** Reference analysis, Full-text search index, Caption extraction, Holon hierarchies, Batch processing

## context-management/tools/refinery/refinery_report.py
**Purpose:** Generates a refinery report, providing an activity summary and knowledge library view

This script provides a comprehensive report on the refinery's activity, including a summary of its current state, recent changes, and a library view of consolidated knowledge. It can be run in various modes, including a full report, summary, library view, and recent changes. The report includes information on chunk generation, watcher activity, and health metrics for the knowledge base.

**Concepts:** Refinery report, Activity summary, Knowledge library view, Chunk generation, Watcher activity

## context-management/tools/refinery/state_synthesizer.py
**Purpose:** Produces the global state/live.yaml map from all refinery outputs

This script synthesizes the global state of a corpus by aggregating data from various refinery outputs, including corpus inventory, boundaries, delta reports, and atom files. It generates a comprehensive state representation, including metadata, corpus summary, boundaries summary, delta status, and health indicators. The output can be customized to either YAML or JSON format.

**Concepts:** State synthesis, Corpus management, Refinery outputs, Data aggregation, Health indicators

## context-management/tools/refinery/subsystem_registry.py
**Purpose:** Manages the registry of Refinery subsystems, providing a catalog of their responsibilities, health, and access methods.

This module serves as a central registry for all Refinery subsystems, allowing for the dynamic loading of subsystem modules and providing a comprehensive overview of their status, dependencies, and health. It offers various functions for listing, filtering, and analyzing subsystems, as well as a command-line interface for printing the registry and dependency graph.

**Concepts:** Subsystem registry, Dynamic module loading, Subsystem status and health tracking, Dependency graph analysis, Command-line interface
