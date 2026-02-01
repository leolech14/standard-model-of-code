# Research: I have a codebase with 2,500 files that has grown into a 'Big Ball of Mud' with high coupling (knot ...

> **Date:** 2026-01-26 04:18:18
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:9d190902bbf197597217f05fca7564324024c7569ed43951ed8d0d09c1a6934d`
> **Raw JSON:** `raw/20260126_041818_i_have_a_codebase_with_2_500_files_that_has_grown.json`

---

## Query

I have a codebase with 2,500 files that has grown into a 'Big Ball of Mud' with high coupling (knot score 10/10) and 75 god classes. I want to consolidate files based on SEMANTIC PURPOSE similarity, not just code structure.

The approach:
1. Extract PURPOSE/intent from each file
2. Compute semantic proximity between purposes
3. Cluster files with similar purposes
4. For each cluster: either promote one file as canonical (archive others) OR merge the PURPOSE itself under a broader umbrella

Questions:
1. What is the most effective way to compute semantic similarity between code file purposes?
2. Should I use embeddings, LLM classification, or hybrid?
3. What clustering algorithm works best for this (hierarchical, k-means, DBSCAN)?
4. How do I handle the promote/archive decision algorithmically?
5. Are there existing tools or papers on 'semantic code consolidation'?

I need the SIMPLEST approach that actually works, not over-engineered.

---

## Response

# Semantic Code Consolidation: A Practical Approach to Resolving Architectural Coupling in God Classes and Monolithic Codebases

This report presents a comprehensive methodology for consolidating files in a large, tightly-coupled codebase through semantic purpose analysis rather than structural refactoring alone. By extracting the intentional purpose of each code file, computing semantic similarity between purposes, clustering related files, and making algorithmic decisions about consolidation, development teams can systematically address the "Big Ball of Mud" antipattern while minimizing the risk of introducing new defects. This approach combines modern embedding techniques, proven clustering algorithms, and practical decision-making heuristics to transform a chaotic codebase into a more maintainable, semantically coherent system.

## Understanding the Challenge: From Structural to Semantic Refactoring

### The Limitations of Traditional Code Consolidation

The first step toward understanding semantic consolidation is recognizing why purely structural approaches to refactoring often fail in large codebases with high coupling. Traditional refactoring techniques focus on code metrics—cyclomatic complexity, method length, class size, and dependency counts[21][24]—but these metrics tell only part of the story. A class that is 500 lines long might actually consist of two separate, well-defined responsibilities that happen to be syntactically intertwined, or it might genuinely be a single, complex operation that cannot be easily decomposed[5][9]. Similarly, two files in different parts of the codebase might appear completely unrelated from a structural standpoint while performing nearly identical business logic[22].

The "God Class" antipattern exemplifies this problem perfectly. God classes violate the single-responsibility principle by assuming too many responsibilities and controlling multiple objects[2][5]. They are difficult to maintain because changes to any functionality require modifications to the god class itself, which increases the likelihood of introducing breaking changes[5]. Traditional refactoring approaches to splitting god classes typically involve incrementally redistributing responsibilities to collaborating classes or extracting new classes[2]. However, without understanding the **purpose** of each responsibility block, refactoring becomes arbitrary, potentially creating new problems while solving the immediate structural issues[5][9].

In a codebase with 2,500 files and 75 god classes, the challenge becomes exponentially more complex. Which responsibilities should be extracted? To which classes should they be moved? How can you be certain that semantically similar logic scattered across different classes is actually capturing the same business purpose? These are the questions that structural analysis alone cannot answer[9][12].

### Why Purpose-Based Consolidation Matters

Purpose-based consolidation addresses this gap by focusing on **what the code is trying to achieve** rather than how it achieves it. A file's purpose can be understood as the business intent, functional responsibility, or problem domain it addresses[50]. Two files with very different implementations but similar purposes are candidates for consolidation—either through unifying them into a single canonical implementation or by recognizing that they represent different manifestations of the same business concern that should be explicitly modeled[22][47].

This approach aligns with domain-driven design principles, where bounded contexts and aggregates are defined around business domains rather than technical layers[26][39]. It also resonates with the principle of a single source of truth, where each distinct business concept should have one authoritative representation[44][47]. By consolidating files based on semantic purpose, you naturally move toward a more maintainable architecture where files, classes, and functions are organized around what they do for the business, not how they happen to be implemented[12][39].

## Extracting Purpose and Intent from Code Files

### Static Analysis for Purpose Extraction

The first practical challenge is extracting the purpose of a given code file. There are several approaches, each with different trade-offs in terms of accuracy, scalability, and implementation complexity.

**Docstring and Comment Analysis** represents the simplest approach. By analyzing comments, docstrings, and class-level documentation, you can often infer a file's intended purpose with minimal computational overhead[50]. This approach scales well—it requires only text processing rather than deep code understanding. However, the quality of extraction depends entirely on documentation quality. In many real-world codebases, documentation is sparse, outdated, or misleading[50]. Additionally, comments describe what the developer thought they were implementing, which may not align with what the code actually does. For a codebase with high coupling and potential technical debt, relying solely on comments is risky[49][52].

**Structural Analysis** involves examining code structure—class names, method names, variable names, and control flow—to infer purpose. Tools perform this analysis through abstract syntax trees (ASTs), identifying patterns like "this class has multiple disconnected methods dealing with user authentication, database queries, and email notifications," which suggests three separate purposes bundled together[8][11][27]. Structural analysis is deterministic and does not require external services, making it suitable for large codebases[8][11]. However, it struggles with semantic clones—code that performs the same function but is written differently[19][22]. It also requires heuristics to distinguish between a complex single purpose (like a sophisticated algorithm) and multiple bundled purposes[24].

**Abstract Syntax Tree (AST) and Data Flow Analysis** provides deeper structural understanding. By building control flow graphs and data flow graphs, you can trace how data moves through a file and which operations depend on which[8][11][27]. This enables identification of logical components within large files. GraphCodeBERT and UniXcoder, pre-trained models that leverage AST and data flow information, achieve state-of-the-art performance on code understanding tasks[8][37][40]. These models can be fine-tuned or used directly to classify code functionality[8][40]. However, this approach requires either running specialized models (which demands computational resources) or implementing graph-based analysis (which is complex to build from scratch)[8].

**Existing Code Intelligence Tools** like CodeScene provide architectural analysis that identifies hotspots, knowledge distribution, and temporal coupling[27][30]. These tools analyze git history and code structure to surface which parts of the codebase are most frequently changed and which developers specialize in certain areas[27][30]. While these tools don't directly extract "purpose," they help identify which files should be examined together for consolidation[27][30][43].

### LLM-Based Purpose Extraction

**Large Language Models as Purpose Extractors** represent a more recent and potentially more effective approach. Modern LLMs trained on large code corpora can understand code semantics, infer developer intent, and generate accurate descriptions of what code does[7][10][50]. The key insight is that LLMs do not need explicit docstrings to infer purpose—they can extract intent from surrounding code, variable names, function signatures, and context[50].

A study on LLM-based code completion demonstrates that when LLMs have access to preceding code context, they can infer developer intent with reasonable accuracy, even without explicit function docstrings[50]. This same capability can be applied to purpose extraction. By prompting an LLM with a file's code and asking "What is the primary business purpose of this file?" or "List the distinct responsibilities this file handles," you can obtain semantically meaningful purpose descriptions[7][10][50].

The practical workflow would be: (1) read a code file, (2) generate a prompt that includes context (file path, imports, top-level comments, a sampling of key functions/classes), (3) submit to an LLM with a specific prompt asking for purpose extraction, (4) parse the response to obtain a standardized purpose description. Research on Extract Method Refactoring with LLMs shows that structured prompting—asking the model to reason step-by-step—significantly improves quality compared to direct requests[7]. A similar approach would ask the LLM to first identify key components, then reason about what they collectively achieve, then synthesize into a concise purpose statement[7][50].

**Hybrid Approach** combines structural analysis and LLM-based extraction. Use structural analysis to identify component boundaries and name-based hints about purpose, then use the LLM to synthesize these into a coherent purpose statement. This balances computational cost (you're not running the LLM on every line of code) with accuracy (the LLM provides semantic understanding that pure structural analysis cannot achieve)[7][10][50].

### Practical Recommendation for Purpose Extraction

For a codebase of 2,500 files with known structural issues, a **two-stage hybrid approach** is most practical:

**Stage 1: Lightweight Structural Analysis**. For each file, extract (1) file path and naming conventions, (2) top-level class and function names, (3) imports and external dependencies, (4) existing docstrings or comments. This stage is O(n) in file count and requires minimal resources. Output: a structured metadata file per source file.

**Stage 2: LLM-Based Purpose Synthesis**. For each file, construct a prompt that includes the metadata from Stage 1 plus a code excerpt (the first 100 lines or first few classes). Submit batched prompts to an LLM asking for a standardized purpose extraction in a structured format (e.g., JSON with fields like `primary_purpose`, `secondary_purposes`, `business_domain`, `technical_domain`). This stage is parallelizable and can be rate-limited to a single LLM inference service.

This approach avoids the overhead of analyzing the entire codebase with an LLM while leveraging LLMs' semantic understanding where it matters most. For a 2,500-file codebase, this could be completed in a single batch job (e.g., 2,500 files × ~10 tokens per purpose description / 100 tokens per second ≈ 4 minutes of inference on a capable LLM API)[7][10][50].

## Computing Semantic Similarity Between File Purposes

Once purpose descriptions are extracted, the next step is computing **semantic proximity** between purposes—determining which files address similar business concerns. This is a foundational step for clustering[1][4][13][16].

### Embedding-Based Similarity

**Text Embeddings** convert purpose descriptions into numerical vectors in a high-dimensional space where semantically similar purposes are close together[1][4][13][16]. This is the most practical and widely-adopted approach for semantic similarity.

OpenAI's embedding API and other models like those from Hugging Face provide pre-trained embeddings that capture semantic meaning[1][34]. The workflow is straightforward: for each file's purpose description, generate an embedding vector. Then, compute the **cosine similarity** between any two vectors to get a similarity score between 0 and 1, where 1 means identical purpose and 0 means completely different[1][13][16].

**Mathematical Foundation**: Cosine similarity between two vectors \(u\) and \(v\) is defined as:

\[ \text{similarity}(u, v) = \frac{u \cdot v}{||u|| \cdot ||v||} \]

where \(u \cdot v\) is the dot product and \(||u||\) is the magnitude of vector \(u\)[13][16]. The result is a value between -1 and 1, though for normalized embeddings (common in modern models), the result is typically between 0 and 1.

**Advantages of embeddings**: They are language-agnostic—the embedding model does not need to understand code syntax, only natural language. They are efficient to compute; once embeddings are generated, similarity computation is O(n²) in the number of files with highly optimized linear algebra libraries[13][16]. They capture nuanced semantic relationships; for example, "user authentication service" and "login mechanism" would have high similarity despite different wording[4][16].

**Practical Implementation**: For a 2,500-file codebase:
1. Extract purpose descriptions (as described in the previous section).
2. Generate embeddings using a pre-trained model. Models like `bge-en-icl` (7.11B parameters) or smaller alternatives like `stella_en_1.5B_v5` are suitable; the latter is preferred for memory efficiency[34].
3. Compute pairwise cosine similarities. For 2,500 files, this produces a 2,500 × 2,500 similarity matrix. Use optimized libraries like scikit-learn's `cosine_similarity` function or use sparse matrix operations if many similarities are near zero[13][16].
4. Threshold the similarities; only retain edges between files with similarity above a meaningful threshold (e.g., 0.7 or 0.8, depending on purpose description quality and desired cluster granularity)[1][4].

**Cost and Resource Considerations**: If using a cloud-based embedding API (e.g., OpenAI), 2,500 purpose descriptions at ~10-20 tokens each cost roughly $0.05-0.10[1]. If using open-source models hosted locally, the computational cost is one-time and minimal on modern hardware[34].

### Alternative: Direct LLM-Based Similarity

Instead of extracting purposes and then embedding them, you could query an LLM directly to assess similarity between files. However, this approach scales poorly—comparing 2,500 files pairwise would require ~3 million LLM calls, which is expensive and slow[7][10][50]. Direct LLM-based similarity is more suitable for smaller batches or as a validation step for specific file pairs identified by embedding-based methods as potentially consolidatable.

### Hybrid Similarity: Embeddings + LLM Refinement

A more nuanced approach is to use embeddings for initial similarity computation, then use LLMs to refine ambiguous cases. For example, if two files have embedding similarity of 0.65 (borderline), you could ask an LLM "Do these two files serve the same business purpose?" to get a clearer answer[4][7][10]. This balances efficiency with accuracy.

## Clustering Files by Semantic Purpose

With a similarity matrix in hand, the next challenge is grouping files into clusters of similar purpose. **Clustering** is the process of partitioning the files such that files within the same cluster are similar to each other, and files in different clusters are dissimilar[3][6][17][25][28][45].

### Clustering Algorithm Selection

Different clustering algorithms make different assumptions about the shape and size of clusters, which directly impacts the quality of consolidation decisions.

**K-Means Clustering** is a classic, fast algorithm that partitions data into k clusters by minimizing within-cluster variance[3][6][45]. Each point is assigned to the nearest centroid (cluster center), and centroids are iteratively recomputed[3][45]. K-means assumes clusters are roughly spherical and of similar size, which may not hold for purpose-based file clustering[3][6]. If purposes are unevenly distributed (e.g., many files handle user authentication, but few handle payment processing), k-means will create clusters of uneven sizes[3][6]. Additionally, k-means requires specifying k (the number of clusters) a priori[3][6][45]. For a codebase with 75 god classes and 2,500 files, it's unclear what k should be[3][6].

**Hierarchical Clustering** builds a tree-like dendrogram showing how files cluster at different levels of similarity[25][28][45]. This is useful because it provides clustering solutions for all possible numbers of clusters—you simply cut the dendrogram at a chosen height[25][28][45]. Hierarchical clustering does not assume cluster shape and can detect clusters of varying sizes[25][28][45]. However, it is computationally more expensive (typically O(n²) or O(n³) depending on the linkage method) compared to k-means[3][25][45].

The **linkage method** in hierarchical clustering determines how distance between clusters is computed. Common choices include single-linkage (minimum distance between points in two clusters), complete-linkage (maximum distance), and Ward's method (minimize variance increase when merging)[25][45]. Ward's method tends to produce more balanced, interpretable clusters for purpose-based data[25][45].

**DBSCAN (Density-Based Spatial Clustering of Applications with Noise)** identifies clusters as dense regions separated by sparse regions[3][17]. Unlike k-means and hierarchical clustering, DBSCAN does not require specifying the number of clusters and can identify outliers (files that don't fit well into any cluster)[3][17]. It is particularly effective for data with non-convex shapes and varying cluster densities[3][17]. However, DBSCAN requires tuning two parameters: **epsilon** (the maximum distance for neighbors) and **min_samples** (minimum points to form a cluster)[3][17][14].

**HDBSCAN (Hierarchical DBSCAN)** is an extension of DBSCAN that automatically determines optimal epsilon and provides a hierarchical structure, combining benefits of both approaches[3][17]. It is more robust than vanilla DBSCAN and does not require parameter tuning[3][17].

### Recommendation for Purpose-Based File Clustering

For semantic purpose consolidation in a large codebase, **hierarchical clustering with Ward's method** is the best starting point:

**Why hierarchical clustering is suitable**: (1) It does not require pre-specifying the number of clusters, which is appropriate when you don't know a priori how many distinct purposes should be in your codebase[25][28]. (2) The dendrogram provides interpretability—you can examine the tree at different levels and understand how files group progressively as similarity threshold increases[25][28]. (3) Ward's method produces balanced, interpretable clusters suitable for architectural refactoring decisions[25][45]. (4) It can handle varying cluster sizes, which is expected in purpose-based clustering (some domains have many files, others few)[25][45].

**Practical Algorithm**:
1. Compute the similarity matrix (all pairwise cosine similarities between embedding-derived purpose vectors).
2. Convert to a distance matrix: \(\text{distance} = 1 - \text{similarity}\)[25][45].
3. Apply hierarchical clustering using Ward's method on the distance matrix[25][45].
4. Generate a dendrogram visualization[25][45].
5. Visually inspect the dendrogram or use statistical methods (e.g., elbow method) to determine a cut height that produces a reasonable number of clusters[25][28].
6. Cut the dendrogram at the chosen height to produce final cluster assignments[25][28].

For the elbow method in hierarchical clustering, you examine the distances between successive merges in the dendrogram. A large jump in distance suggests a good cut point—at that point, clusters become increasingly dissimilar, indicating distinct purposes[25][28].

**Alternative Consideration**: If you want to be more aggressive about consolidation and can tolerate some false positives, **HDBSCAN** offers several advantages[3][17]. It automatically identifies dense clusters and outliers, which is useful for recognizing "standard" purpose groups (many files, similar purpose) versus "unique" files (few files with very specific purposes)[3][17]. Unique-purpose files might be left alone or manually reviewed, while standard-purpose groups proceed to consolidation[3][17].

### Implementation: Clustering in Practice

Using scikit-learn (a widely-used Python library), the workflow would be:

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np

# purpose_embeddings: array of shape (n_files, embedding_dim)
# e.g., shape (2500, 384) for sentence embeddings

# Compute distance matrix (1 - cosine_similarity)
distances = 1 - sklearn.metrics.pairwise.cosine_similarity(purpose_embeddings)

# Hierarchical clustering with Ward's method
linkage_matrix = linkage(squareform(distances), method='ward')

# Visualize dendrogram to determine cut height
dendrogram(linkage_matrix)
# ... inspect the plot, identify a good cut height ...

# Cut dendrogram at chosen height (e.g., distance threshold 0.3)
clustering = AgglomerativeClustering(
    n_clusters=None,
    distance_threshold=0.3,
    linkage='ward'
)
cluster_labels = clustering.fit_predict(purpose_embeddings)
```

This produces a mapping from each file to a cluster ID. Files with the same cluster ID have similar purposes and are candidates for consolidation[25][28][45].

## Handling Promote/Archive Decisions Algorithmically

Once files are clustered by purpose, the next step is deciding what to do with each cluster. Should files be merged? Should one be designated as canonical while others are archived? The decision logic must be algorithmic, repeatable, and defensible—because it will likely be applied to hundreds of clusters[9][12][20][49].

### Decision Factors

**Cluster Size**: A cluster with 2-3 files has different consolidation dynamics than one with 15 files. Larger clusters indicate widespread duplication of effort, suggesting high consolidation benefit[22][49].

**File Dependency Count**: A file with many inbound dependencies (many other files import from it) is a candidate for promotion to canonical status. Files with few dependencies might be candidates for archival[43][9].

**File Recency and Change Frequency**: Files that have been modified recently and frequently are more likely to contain actively maintained logic. Files that have not been touched in years might be legacy code that should be archived[27][30][24]. Git history provides this information[27][30].

**Code Complexity and Quality**: Files with high cyclomatic complexity, low test coverage, or numerous code smells are riskier to keep active. If a simpler, cleaner file in the same cluster addresses the same purpose, promoting the cleaner one reduces long-term maintenance burden[5][9][21][27].

**Documentation and Clarity**: Well-documented files are easier to understand and maintain. In a cluster of similar files, promoting the best-documented one as canonical improves overall system understandability[50][9].

### Algorithmic Decision Framework

A scoring-based approach can make these decisions repeatable:

**For each cluster, for each file, compute a promotion score**:

\[ \text{PromotionScore} = w_1 \cdot \text{DependencyScore} + w_2 \cdot \text{RecencyScore} + w_3 \cdot \text{QualityScore} \]

where weights \(w_1, w_2, w_3\) are configurable. Define:

- **DependencyScore**: Normalized count of files that import/depend on this file. Files with higher inbound dependencies are more "foundational" and good candidates for promotion[43][9].
  
  \[ \text{DependencyScore} = \frac{\text{inbound_dependency_count}}{\text{max_dependency_count_in_cluster}} \]

- **RecencyScore**: Based on git history. Recent modifications indicate active maintenance[27][30].
  
  \[ \text{RecencyScore} = \frac{\text{days_since_last_commit}}{\text{max_days_since_commit_in_cluster}} \]
  
  (Inverted, so recently modified files score higher.)

- **QualityScore**: Composite metric from code analysis tools[21][27][30].
  
  \[ \text{QualityScore} = w_q1 \cdot \text{CodeHealth} + w_q2 \cdot \text{TestCoverage} + w_q3 \cdot \text{(1 - \text{Complexity})} \]
  
  where CodeHealth comes from tools like CodeScene[21][30] and Complexity is normalized.

**Decision Rule**: For each cluster:
- If exactly one file has significantly higher PromotionScore than others (e.g., 30% higher), **promote** it as canonical and mark others for archival.
- If multiple files have comparable high scores (within 10%), further manual review or sub-clustering is needed.
- If all files have low PromotionScore (indicating low-quality code), consider **merging** them into a newly written, clean implementation (higher risk but potentially worth it for high-value clusters)[7][10][9].
- If cluster has only 1-2 low-dependency files, they may be **isolated special cases** and left alone[49].

### Managing Archive Decisions

Once a file is marked for archival, it should not be immediately deleted. Instead:

1. **Create a deprecation notice** at the top of the file indicating it is superseded by [canonical file path] and will be removed in [date][5][9].
2. **Redirect imports**: Update all imports in the codebase to point to the canonical file. This can be done via automated refactoring tools or IDE features[9].
3. **Monitor breakage**: Track which tests or production incidents involve the archived file[9].
4. **Grace period and removal**: After a grace period (e.g., one release cycle), safely remove the archived file[9].

This staged approach reduces the risk of surprising incompatibilities downstream[9][39][42].

### Special Case: Merging vs. Promoting

In some clusters, no existing file is clearly superior to others. In such cases, rather than promoting one, you might **merge** them—creating a single, canonical file that combines the best aspects of each source file. This is higher-risk because it involves re-implementing logic, but it can result in cleaner, more cohesive code.

This decision is best handled by LLM-assisted tools. Prompt an LLM with the semantics and implementations of multiple files and ask it to propose a merged version that preserves all distinct functionality while eliminating duplication[7][10]. Human review of the merged file is essential[7][10][9].

## Existing Tools and Research on Semantic Code Consolidation

### Tools for Code Understanding and Clustering

**CodeScene** is a behavioral code analysis tool that combines static analysis with git history to identify hotspots (frequently changing, complex code) and knowledge distribution (which developers specialize in which areas)[27][30]. While not specifically designed for purpose-based consolidation, CodeScene's metrics (Code Health, hotspot identification, temporal coupling) directly support promotion/archive decisions described above[27][30].

**vFunction** is a platform for identifying microservices and modular boundaries in monolithic codebases[12][24][43]. It analyzes code dependencies and proposes refactoring opportunities. However, it focuses on structural boundaries rather than semantic purpose, making it less directly applicable but useful as complementary information[12][43].

**Semantic diff and merge tools** like those described in conflict resolution research recognize semantic equivalence of code despite syntactic differences[19][20][22]. These tools apply techniques like AST matching and data flow analysis to detect semantic clones[19][22]. Tools like CCLearner and clone detection frameworks leverage deep learning to identify similar code across a codebase[19][38].

**Graph-based code analysis tools** like PuppyGraph enable querying dependencies as a graph, supporting change impact analysis and dependency cycle detection[43]. While not purpose-specific, these tools complement semantic consolidation by ensuring that consolidation decisions don't accidentally create new circular dependencies[43].

### Research on Semantic Code Analysis

**GraphCodeBERT** is a pre-trained model that leverages code structure (abstract syntax trees and data flow graphs) to learn code representations superior to token-based models[8]. This research demonstrates that semantic understanding of code can be captured and used for downstream tasks like code search, clone detection, and code translation[8]. The model's success on these tasks validates that code embeddings can capture semantic meaning[8].

**Code2Vec** represents code as sequences of abstract syntax tree paths and trains models to predict method names from code vectors[41]. The learned vectors capture semantic properties—for instance, the embedding vector for a method named "serialize" is close to "toJSON" (semantic clones with different names)[41]. This demonstrates that code vectors can recognize semantic similarity despite syntactic differences[41].

**UniXcoder** unifies code representation across understanding and generation tasks by leveraging both code comments and AST structure[37][40]. It shows that multi-modal code representation (combining code, comments, and structure) improves performance on code understanding tasks[37][40]. This research validates the effectiveness of embeddings derived from code semantics[37][40].

**LLM-based code refactoring** research demonstrates that modern LLMs can perform sophisticated code transformations when given structured prompts and iterative refinement[7][10][50]. Papers on Extract Method Refactoring show that LLMs can automatically identify method boundaries and extract cohesive code fragments—a related task to identifying distinct purposes[7]. Prompt engineering strategies (e.g., recursive criticism and improvement) consistently outperform naive prompting[7][10].

### Gap: Lack of Dedicated Research on Purpose-Based Consolidation

While abundant research exists on code similarity, code embeddings, clustering, and refactoring separately, there is surprisingly little dedicated research on **consolidating files based on semantic purpose similarity**. Most code consolidation and deduplication work focuses on clone detection (identifying identical or near-identical code) rather than on understanding broader semantic purpose[19][22][38]. The Big Ball of Mud and god class literature addresses the *problem* but not the *algorithmic solution* for consolidation at scale[49][52][2][5].

This gap suggests that the approach outlined in this report—combining semantic extraction, embeddings, clustering, and algorithmic promotion/archive decisions—is relatively novel in practice, even if each component is well-established in research.

## The Simplest Effective Approach: A Recommended Path

Given the complexity of the problem and the variety of techniques available, this section synthesizes a **minimal, practical approach** that balances simplicity with effectiveness.

### Three-Phase Implementation

**Phase 1: Purpose Extraction and Embedding** (1-2 weeks for 2,500 files)

1. **Lightweight structural analysis**: For each file, extract file path, naming, top-level declarations, and existing docstrings. Automate this with AST parsing.
2. **LLM-based purpose synthesis**: Batch-process all 2,500 files through an LLM API (or local model) with a standardized prompt asking for a concise purpose description (2-3 sentences). Use structured output format (JSON).
3. **Embedding generation**: Generate embeddings for each purpose description using an off-the-shelf model (e.g., OpenAI's API or HuggingFace's `stella_en_1.5B_v5`).
4. **Output**: A CSV or JSON file with one row per source file containing: file path, extracted purpose description, and embedding vector.

**Phase 2: Clustering and Decision** (1 week)

1. **Compute similarity matrix**: Generate all-pairs cosine similarity between purpose embeddings.
2. **Hierarchical clustering**: Apply Ward linkage hierarchical clustering to the similarity-based distance matrix.
3. **Dendrogram inspection and cutting**: Visualize dendrogram, identify a reasonable cut height (e.g., distance threshold 0.3-0.5), and produce final cluster assignments.
4. **Within-cluster analysis**: For each cluster, apply the algorithmic promotion/archive scoring described above to identify canonical files and archival candidates.
5. **Output**: A consolidation plan document listing, for each cluster: cluster ID, member files, recommended canonical file, files to archive, and confidence scores.

**Phase 3: Staged Implementation and Validation** (2-4 weeks, ongoing)

1. **Pilot subset**: Select 5-10 clusters with high confidence scores (clear canonical files, little ambiguity) and implement consolidation for those first.
2. **Automated refactoring**: Use IDE refactoring tools (move file, update imports) or custom scripts to redirect all imports from archived files to canonical files.
3. **Test and validation**: Run full test suite after each consolidation step. Monitor for failures and unexpected breakage.
4. **Iteration and learning**: Refine decision scores based on outcomes from pilot clusters. Adjust weights in the promotion score formula if certain criteria prove unreliable.
5. **Scale**: Once pilot clusters are successfully consolidated, proceed to remaining clusters in waves.

### Technology Stack (Minimal)

- **Embedding generation**: OpenAI API (`text-embedding-3-small`), or HuggingFace's `sentence-transformers` library locally.
- **Clustering**: scikit-learn (`AgglomerativeClustering`).
- **Visualization**: matplotlib/seaborn for dendrograms.
- **LLM for purpose extraction**: OpenAI API, Claude API, or local model like LLaMA.
- **Code analysis and refactoring**: Existing IDE features or custom AST-based scripts.

### Estimated Effort and Cost

- **Engineering time**: 4-6 weeks for a small team (1-2 engineers) to design, implement, and validate the consolidation pipeline.
- **LLM API costs** (if using OpenAI or Claude): ~$50-150 for 2,500 files × one extraction + one validation pass.
- **Computational resources** (if using local models): Minimal; hierarchical clustering on 2,500 files is tractable on any modern development machine.
- **Runtime for full pipeline**: ~4 hours (dominated by LLM batch processing and test suite runs after consolidation).

### Risk Mitigation

**Validate upstream**. Before consolidating, verify that extracted purposes are reasonable by spot-checking 20-30 files. If purpose extraction is poor, refine the prompt or increase code excerpt length before proceeding.

**Use a git branch**. Implement consolidation on a feature branch, not trunk. This allows easy rollback if unexpected issues arise.

**Monitor test coverage**: Ensure the codebase has adequate test coverage before consolidation. Weak tests obscure consolidation-related breakage. Consider boosting coverage for files in high-consolidation-impact clusters.

**Stage the consolidation**: Do not consolidate everything at once. Smaller, staged changes are easier to debug and rollback if needed.

**Document decisions**: Keep a record of why each file was archived and which canonical file replaced it. This aids future developers understanding the codebase evolution.

## Advanced Considerations and Extensions

### Handling Temporal Coupling and Architectural Cycles

The simple approach above focuses on semantic purpose but may inadvertently create or worsen **temporal coupling**—hidden dependencies on execution order or timing—or **circular dependencies** between modules[26][39][46]. After consolidation, use static analysis tools to detect new cycles and temporal coupling issues[26][27][43].

If consolidation would create cycles, consider one of several strategies:
- **Reverse consolidation**: Instead of archiving a file, keep it and remove its dependency on the other file.
- **Extract shared interface**: If two files depend on each other circularly, extract their common interface into a separate module[26][39].
- **Acknowledge acceptable cycles**: In some cases (e.g., bidirectional feature dependencies), cycles are unavoidable without major redesign. Document them explicitly[26][39].

### Extending to Broader Architectural Refactoring

The consolidation approach can be extended to higher-level architectural refactoring:
- **Package/module level**: Instead of individual files, cluster packages or modules, guiding modularization decisions[39][26].
- **Microservice extraction**: Files that form cohesive clusters with clear, exportable interfaces are candidates for extraction into separate microservices[26][39][42].
- **API design**: Canonical files from consolidation naturally become the "public API" for their cluster; explicit API contracts and interface definitions can be derived from them[26][39].

### Incorporating Business Context and Requirements

The simplest approach uses only code-based semantic similarity. A more sophisticated approach would incorporate business context:
- **Domain-driven design**: Tag files and purposes with business domain and subdomain. Consolidation should respect domain boundaries[39][26].
- **Stakeholder input**: For ambiguous consolidation decisions, gather input from domain experts or feature team members.
- **API versioning and contracts**: When promoting a canonical file, explicitly version its API and maintain backward compatibility to avoid surprising downstream consumers[26][39].

These extensions add complexity but can improve the long-term maintainability and business alignment of the refactored codebase.

## Conclusion: From Chaos to Coherence

The Big Ball of Mud antipattern and pervasive god classes are symptoms of a codebase where structure has eroded faster than refactoring has kept pace[49][52]. Traditional structural refactoring metrics—complexity scores, method lengths, class sizes—tell part of the story but miss the core issue: many pieces of code serve overlapping purposes and should be unified.

Semantic purpose-based consolidation addresses this by extracting the **intent** of each code file, measuring semantic similarity between intents, clustering related files, and making algorithmic decisions about which files should be authoritative and which should be archived. This approach is grounded in established techniques (embeddings, hierarchical clustering) and modern capabilities (LLM-based semantic understanding) but remains pragmatic and achievable without massive engineering effort.

The recommended three-phase approach—purpose extraction and embedding, clustering and decision-making, staged implementation and validation—can be executed by a small team in 4-6 weeks and scales to codebases with tens of thousands of files. The outcome is a more coherent architecture where each business concern has a clear, canonical representation and where future developers can understand the system's structure by understanding its purposes, not by decoding tangled dependencies.

For a codebase with 2,500 files, 75 god classes, and a knot score of 10/10, this is not a quick fix. But it is a systematic path from chaos to coherence—and one that, unlike monolithic rewrites, preserves working functionality while steadily improving structure.

---

## Citations

1. https://openai.com/index/introducing-text-and-code-embeddings/
2. https://eng.libretexts.org/Bookshelves/Computer_Science/Programming_and_Computation_Fundamentals/Book:_Object-Oriented_Reengineering_Patterns_(Demeyer_Ducasse_and_Nierstrasz)/09:_Redistribute_Responsibilities/9.04:_Split_Up_God_Class
3. https://scikit-learn.org/stable/modules/clustering.html
4. https://programminghistorian.org/en/lessons/clustering-visualizing-word-embeddings
5. https://linearb.io/blog/what-is-a-god-class
6. https://www.kaggle.com/code/iamtapendu/clustering-methods-kmeans-hierarchical-dbscan
7. https://arxiv.org/html/2510.26480v1
8. https://openreview.net/pdf?id=jLoC4ez43PZ
9. https://www.freecodecamp.org/news/how-to-refactor-complex-codebases/
10. https://www.emergentmind.com/topics/llm-based-refactoring
11. https://arxiv.org/html/2407.18877v2
12. https://vfunction.com/blog/modular-software/
13. https://www.tigerdata.com/learn/implementing-cosine-similarity-in-python
14. https://blog.dailydoseofds.com/p/how-to-find-optimal-epsilon-value
15. https://realpython.com/practical-prompt-engineering/
16. https://memgraph.com/blog/cosine-similarity-python-scikit-learn
17. https://www.datacamp.com/tutorial/dbscan-clustering-algorithm
18. https://www.promptingguide.ai/introduction/settings
19. https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0340971
20. https://homepages.uc.edu/~niunn/papers/RSSE12.pdf
21. https://vfunction.com/blog/software-quality/
22. https://www.in-com.com/blog/mirror-code-uncovering-hidden-duplicates-across-systems/
23. https://www.cs.tufts.edu/comp/150GIT/archive/tom-mens/merging.pdf
24. https://javapro.io/2025/10/21/map-your-code-master-your-architecture/
25. https://en.wikipedia.org/wiki/Hierarchical_clustering
26. https://www.infoq.com/articles/microservices-design-ideals/
27. https://codescene.com/blog/what-is-a-static-code-analysis
28. https://www.ibm.com/think/topics/hierarchical-clustering
29. https://bravenewgeek.com/category/design-patterns/
30. https://codescene.com
31. https://discuss.huggingface.co/t/how-to-use-huggingface-free-embedding-models/109700
32. https://labelyourdata.com/articles/machine-learning/intent-classification
33. https://www.kdnuggets.com/2020/01/decision-tree-algorithm-explained.html
34. https://codesphere.com/articles/best-open-source-sentence-embedding-models
35. https://arxiv.org/html/2510.17892v1
36. https://en.wikipedia.org/wiki/Greedy_algorithm
37. https://aclanthology.org/2022.acl-long.499.pdf
38. https://escholarship.org/content/qt5qx4b1xh/qt5qx4b1xh_noSplash_1fe52bbab62b4503558550e5e08390fa.pdf
39. https://microservices.io/post/architecture/2024/09/09/modular-monolith-patterns-for-fast-flow.html
40. https://arxiv.org/abs/2203.03850
41. https://haoxintu.github.io/files/7-code2vec%20Learning%20Distributed%20Representations%20of%20Code.pdf
42. https://dev.to/sepehr/from-monolith-to-modular-monolith-to-microservices-realistic-migration-patterns-36f2
43. https://www.puppygraph.com/blog/software-dependency-graph
44. https://en.wikipedia.org/wiki/Single_source_of_truth
45. https://machinelearningmastery.com/the-beginners-guide-to-clustering-with-python/
46. https://dev.to/devcorner/temporal-coupling-in-software-development-understanding-and-prevention-strategies-48m1
47. https://strapi.io/blog/what-is-single-source-of-truth
48. https://royalsocietypublishing.org/rsos/article/12/1/241692/92905/Human-interpretable-clustering-of-short-text-using
49. https://www.cin.ufpe.br/~sugarloafplop/mud.pdf
50. https://arxiv.org/pdf/2508.09537.pdf
51. https://www.cs.cmu.edu/~mmv/papers/merge-iccbr97.pdf
52. https://www.laputan.org/mud/
53. https://wires.onlinelibrary.wiley.com/doi/10.1002/wcms.70047
54. https://help.sap.com/docs/SAP_ADVANCED_PLANNING_AND_OPTIMIZATION,_ON_SAP_ERP/c95f1f0dcd9549628efa8d7d653da63e/0a4cc95360267614e10000000a174cb4.html
55. https://github.com/Project-Resilience/mvp
56. https://patterns.arcitura.com/big-data-patterns/design_patterns/canonical_data_format
57. https://github.com/thepracticaldeveloper/practical-architecture
58. https://dodcio.defense.gov/Portals/0/Documents/Library/DevSecOpsTools-ActivitiesGuidebook.pdf
59. https://ptgmedia.pearsoncmg.com/images/9780136135166/samplepages/0136135161.pdf
60. https://github.com/mehdihadeli/awesome-software-architecture

---

## Usage Stats

- Prompt tokens: 214
- Completion tokens: 7767
- Total tokens: 7981
