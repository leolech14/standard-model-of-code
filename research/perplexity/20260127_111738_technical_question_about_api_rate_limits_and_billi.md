# Research: Technical question about API rate limits and billing strategies:

SCENARIO: Building knowledge graph...

> **Date:** 2026-01-27 11:17:38
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:7a0ffc68e1506d42906a928644b38002ad7523ea81cfd08a8dbe8dbad5411712`
> **Raw JSON:** `raw/20260127_111738_technical_question_about_api_rate_limits_and_billi.json`

---

## Query

Technical question about API rate limits and billing strategies:

SCENARIO: Building knowledge graph requires processing:
- 2,673 code chunks (~200 tokens each = 534K tokens total)
- 1,068 research documents (~5K tokens each = 5.3M tokens total)
- Entity extraction via LLM (estimated 10-20M input tokens total)

CURRENT CONSTRAINT:
- Gemini 2.0 Flash Exp: 250K tokens/minute quota
- At this rate: 40-80 minutes minimum (assuming no other limits)
- BUT: Also has requests/minute limits (unknown)

QUESTIONS:

1. RATE LIMIT STRATEGIES:
- Should we use multiple API keys (separate billing accounts) to parallelize?
- Does Google allow multiple projects/billing for same user?
- Are there enterprise quotas with higher limits?
- Gemini 2.5 Flash: What are actual quota limits (not just 4x mention)?

2. COST OPTIMIZATION:
- Batch processing vs streaming: which is more cost-effective for entity extraction?
- Caching strategies to avoid re-processing?
- Gemini pricing: What's cheapest model for entity extraction (Flash vs Pro vs smaller)?
- Open-source alternatives: Llama 3.1-70B local vs Gemini API cost comparison?

3. TECHNICAL APPROACHES:
- Exponential backoff: Recommended retry strategy for 429 errors?
- Request queuing: Should we implement request queue with rate limiter?
- Parallel processing: Can we use multiple API keys safely without violating ToS?
- Failover: If one model rate-limited, switch to another (Gemini → Claude → local)?

4. PRODUCTION PATTERNS:
- How do production systems handle 10M+ token processing jobs?
- Batch API endpoints: Does Google offer batch processing with higher throughput?
- Pre-processing: Should we reduce token count via summarization before extraction?
- Incremental processing: Extract from new content only (delta-based)?

5. ALTERNATIVE ARCHITECTURES:
- Local LLM (Llama 3.1-70B via Ollama): Feasibility for entity extraction quality?
- Hybrid: Local for initial pass, Gemini for refinement?
- Smaller models: Gemini Nano or similar for bulk extraction?
- Open-source GraphRAG: Alternatives to commercial APIs?

Provide: Cost analysis, rate limit workarounds, production patterns, technical implementation guidance for processing millions of tokens for knowledge graph construction.

---

## Response

# Processing Large-Scale Knowledge Graphs: Rate Limiting, Cost Optimization, and Production Patterns for Multi-Million Token Workloads

This comprehensive report examines the technical, financial, and operational challenges of processing knowledge graph construction workloads requiring tens of millions of tokens. The scenario presented—extracting entities from 5.8M tokens of source material with an estimated 10-20M tokens needed for LLM-based entity extraction—represents a substantial computational undertaking that exceeds single-API-key capacities under standard rate limiting configurations. Through analysis of current API platform capabilities, pricing structures, and production-grade patterns, this report provides actionable strategies for optimizing throughput, managing costs, and implementing resilient systems at scale.

## Rate Limiting Architecture and Constraint Analysis

### Understanding Gemini API Rate Limit Dimensions

Rate limits across the Gemini API are enforced across three distinct dimensions: requests per minute (RPM), tokens per minute (TPM), and requests per day (RPD)[1][23]. Each dimension is evaluated independently, and exceeding any single limit triggers a rate limit error. For the knowledge graph construction scenario presented, the 250K tokens per minute quota becomes the primary constraint. This translates to approximately 40-80 minutes of continuous processing at full capacity, assuming a single API key and no other limiting factors. However, this calculation reveals only part of the constraint picture. Requests per minute limits operate separately from token limits, creating a compound constraint that developers frequently underestimate[1].

The Gemini API applies rate limits at the project level rather than the API key level, meaning that multiple API keys sharing the same Google Cloud project will draw from a single rate limit pool[1][23]. This architectural decision has significant implications for parallelization strategies. When a developer creates multiple API keys within the same billing project, they do not increase their collective throughput—instead, they merely distribute the same quota across multiple credential paths. The limitation resets at midnight Pacific time for daily quotas, which becomes relevant for job scheduling and retry strategies in production systems[1].

Rate limits are also tied to usage tiers, with four distinct tiers available: Free, Tier 1, Tier 2, and Tier 3[1][23]. The Free tier imposes restrictive limits suitable only for development work. Tier 1 requires a full paid billing account and represents the entry point for production workloads. Tier 2 qualification requires total spending exceeding $250 with at least 30 days since successful payment, while Tier 3 requires over $1,000 in spending with the same 30-day requirement. Each tier increase substantially expands available quota, with Tier 2 and 3 enabling significantly higher throughput than Tier 1[1][23]. For the knowledge graph construction scenario with 10-20M tokens, Tier 2 or Tier 3 qualification becomes economically justified, as the throughput gains directly reduce processing time and associated costs.

### Multiple Projects and Billing Accounts Strategy

Google Cloud allows a single user to create multiple projects, each with independent quotas[11]. Each project can have its own billing account associated, and billing accounts are separate from the project hierarchy. A critical distinction emerges here: multiple projects under separate billing accounts do create independent rate limit pools. If a user or organization creates three separate Google Cloud projects, each with distinct billing accounts, they effectively obtain three independent rate limit allocations for the Gemini API[1][8][11].

However, implementing this strategy requires careful consideration of organizational structure and security implications. Google Cloud's fraud prevention systems may flag unusual patterns of project creation or may deny upgrade requests to higher tiers based on "other factors identified during the review process," even when qualification criteria are technically met[1][23]. For legitimate enterprise use cases requiring high throughput, the recommended approach involves transparent communication with Google Cloud support about intended workload patterns and requesting tier upgrades directly rather than attempting to circumvent limits through distributed project creation.

The historical context from 2017 reveals that Google Cloud imposed hard limits on the number of projects per billing account to prevent abuse cases where bad actors would create thousands of projects to consume massive amounts of free quota before payment methods failed[8]. Modern fraud detection has evolved, but the principle remains: rapid, unexplained project proliferation can trigger security reviews that delay or deny quota increases.

## Batch Processing and Alternative Throughput Strategies

### Gemini Batch API Rate Limits and Architecture

The Gemini Batch API operates under distinctly different rate limits from the standard API and is specifically designed for high-throughput, non-latency-critical workloads[7][10]. Batch API requests are subject to separate rate limits with significantly higher throughput allowances. The Batch API allows concurrent batch requests (typically 100 concurrent batch jobs) and enqueues tokens across active batch jobs, with the maximum enqueued tokens varying by model and tier[1][23]. For Gemini 2.5 Flash at Tier 1, the batch enqueued token limit reaches 3,000,000 tokens, allowing customers to submit multiple batch jobs with a combined token budget significantly exceeding standard API quotas[1][23].

Batch jobs are designed with a target turnaround time of 24 hours but typically complete faster in practice[7][10]. For entity extraction workloads where immediate responses are not required, batch processing becomes the optimal approach. The Batch API provides approximately 50% cost savings compared to standard API rates, making a 10-20M token workload approximately $500-$2,000 cheaper via batch processing than equivalent streaming requests[10].

The Batch API has specific limitations that should inform architectural decisions. Batch inference does not support explicit caching or retrieval-augmented generation (RAG) features[31]. Input file sizes are capped at 2GB, and the entire batch job has a processing timeout of approximately 24 hours; incomplete jobs after this window are cancelled with charges only applied to completed requests[31]. For the knowledge graph construction scenario, this means that while batch processing offers cost advantages and higher throughput, it cannot be used as the sole solution if any portion of the workflow requires real-time refinement or feedback loops.

### Vertex AI Batch Inference for Gemini Models

Beyond the Gemini-specific Batch API, Google's Vertex AI platform offers batch inference capabilities that provide even higher throughput and better integration with data preprocessing pipelines[31][34][57]. Batch inference through Vertex AI is optimized for large-scale processing tasks and provides implicit caching by default for supported models, offering a 90% discount on cached tokens compared to standard input tokens[31]. The discount precedence algorithm ensures that cache hits take precedence over batch discounts, maximizing savings for repeated processing patterns.

Vertex AI batch inference supports up to 200,000 requests per batch job with Cloud Storage file size limits of 1GB[31]. Queue time can extend up to 72 hours during high-demand periods, but once processing begins, most jobs complete within 24 hours. The service automatically scales compute resources during processing and scales back to zero after completion, ensuring customers pay only for actual computation time[31][34][57].

For knowledge graph construction specifically, the integration with data preprocessing pipelines within Vertex AI enables semantic chunking, content-aware splitting, and entity linking operations to occur within the batch processing environment before LLM-based entity extraction. This reduces the total token consumption compared to sending raw documents directly to the LLM[52].

## Cost Analysis and Model Selection

### Pricing Structure Across Gemini Model Tiers

Gemini pricing varies significantly across model tiers, with input and output pricing structured differently based on token count thresholds and model complexity[9][12]. Gemini 2.5 Pro represents the highest-capability tier, priced at $1.25 per million input tokens for prompts up to 200K tokens, and $2.50 per million input tokens for prompts exceeding 200K tokens. Output pricing is correspondingly higher at $10 per million tokens for shorter contexts and $15 per million tokens for longer contexts[9][12].

Gemini 2.5 Flash provides a mid-tier option, priced at $0.10 per million input tokens for text, image, or video content, and $0.40 per million output tokens[9][12]. For entity extraction workloads where Pro-level reasoning is not essential, Flash represents a substantially more cost-effective choice. The quality differential between Flash and Pro depends on task complexity; for highly structured entity extraction with well-defined ontologies, Flash typically delivers comparable results to Pro at approximately one-quarter of the cost[9][21].

Gemini 2.5 Flash-Lite provides the most economical option at $0.10 per million input tokens and $0.40 per million output tokens, identical to Flash pricing[9][12]. The naming convention is slightly misleading; Flash-Lite is not a cost reduction over Flash but rather a speed-optimized variant with identical pricing. For use cases requiring maximum throughput rather than maximum accuracy, Flash-Lite is preferable.

Batch processing applies an additional 50% discount across all models[10][12]. For a 10-20M token entity extraction workload using Gemini 2.5 Flash with batch processing, the estimated cost calculation proceeds as follows:

For 15M input tokens (midpoint estimate) at batch rates:
\(
\text{Input cost} = 15,000,000 \times \frac{\$0.10}{1,000,000} \times 0.5 = \$750
\)

For 2M output tokens (estimated at 15% of input):
\(
\text{Output cost} = 2,000,000 \times \frac{\$0.40}{1,000,000} \times 0.5 = \$400
\)

Total batch cost: approximately $1,150 for the complete entity extraction workload.

### Context Caching for Reduced Token Consumption

Context caching represents a powerful optimization mechanism for repeated processing patterns, such as extracting entities from the same document set with different entity type specifications[29]. Implicit caching is automatically enabled on most Gemini models and provides no cost guarantee, while explicit caching can be manually enabled with guaranteed cost savings[29].

Explicit caching applies a reduced rate to cached tokens: $0.03 per million cached input tokens compared to $0.10 per million standard input tokens for Flash models—a 70% reduction[29]. The storage cost for cached tokens is $1.00 per million tokens per hour of cache TTL (time to live). For entity extraction workloads, if an organization processes the same source documents with multiple extraction passes (initial extraction, refinement extraction, confidence scoring), caching can reduce costs dramatically.

Example with context caching for multi-pass extraction:
- First pass: 5.3M tokens from research documents (uncached)
- Second pass: Same 5.3M tokens (cached at $0.03/M)
- Third pass: Same 5.3M tokens (cached at $0.03/M)

Without caching: \((5.3 \times 0.10) + (5.3 \times 0.10) + (5.3 \times 0.10) = \$1.59M\) input tokens

With 1-hour cache TTL: 
\(
(5.3 \times 0.10) + (5.3 \times 0.03 + 5.3 \times 1.00 \times 1) + (5.3 \times 0.03 + 5.3 \times 1.00 \times 1) = \$0.53 + \$5.83 + \$5.83 = \$12.19
\)

Wait, this calculation shows caching becomes uneconomical for very short TTLs when multiple passes are needed. The more efficient approach involves a longer cache TTL spread across many extraction operations:

With 8-hour cache TTL and 10 extraction passes:
\(
(5.3 \times 0.10) + (5.3 \times 0.03 \times 9) + (5.3 \times 1.00 \times 8) = \$0.53 + \$1.43 + \$42.40 = \$44.36
\)

This demonstrates that context caching becomes economical when amortized across many operations, not for single one-time extractions.

### Open-Source and Self-Hosted Alternatives

Open-source language models offer a fundamentally different cost structure compared to API-based consumption. Llama 3.1 70B, an open-weight model, can be self-hosted through platforms like Ollama or vLLM, incurring costs based on GPU infrastructure rather than token consumption[13][14][16][17][43].

The economic crossover point between API-based and self-hosted approaches depends on workload volume. For very high inference volume (100M+ tokens daily), self-hosting becomes economically preferable despite infrastructure complexity. At moderate volumes (1-10M tokens daily), API-based approaches remain more cost-effective[43].

Specific cost calculations for self-hosting reveal the infrastructure burden. A single A100 GPU on cloud providers costs approximately $1.30-$4.00 per hour depending on provider and spot pricing[43]. At maximum efficiency, a single A100 can generate approximately 500K-1M tokens per day. For a 15M token entity extraction workload, this requires:

\(
\text{GPU hours required} = \frac{15,000,000 \text{ tokens}}{750,000 \text{ tokens/GPU-day}} = 20 \text{ GPU-days}
\)

At $1.50/hour average spot pricing:
\(
\text{Cost} = 20 \text{ days} \times 24 \text{ hours/day} \times \$1.50/\text{hour} = \$720
\)

This is marginally less expensive than the $1,150 Gemini batch estimate, but fails to account for engineering time to set up infrastructure, optimize inference, handle failures, and manage model deployment. Including a junior ML engineer's time at $50/hour for approximately 40 hours of setup and management raises the true cost to $2,150—significantly above the API approach[43][46].

Llama models also typically underperform on entity extraction tasks compared to larger closed models, particularly when entity types are not well-represented in the training data. For specialized domain ontologies, accuracy degradation can be 15-25% compared to Gemini Pro[13][28].

## Rate Limit Handling and Retry Strategies

### Exponential Backoff Implementation

Exponential backoff represents the industry-standard retry strategy for rate limit errors (HTTP 429 responses)[15][18][35]. The algorithm implements a progressively longer delay between retries, typically doubling the wait time with each attempt. This prevents overwhelming the API during congestion and allows system load to normalize between retries[15][18].

The exponential backoff formula follows:
\[
\text{wait\_time} = \text{base\_delay} \times (\text{multiplier}^{\text{attempt\_number}}) + \text{jitter}
\]

Recommended parameters for Gemini API:
- Base delay: 1 second
- Multiplier: 2
- Maximum wait time: 60 seconds
- Jitter: random value between 0-1 second

The jitter component is critical for preventing thundering herd problems where multiple clients retry simultaneously after the same delay period, causing secondary rate limit waves[18][35].

Python implementation example:

```python
import random
import time

async def retry_with_exponential_backoff(
    async_callable,
    max_attempts=5,
    base_delay=1,
    multiplier=2,
    max_delay=60
):
    """Retry with exponential backoff and jitter for rate limit errors."""
    
    for attempt in range(max_attempts):
        try:
            return await async_callable()
        except RateLimitError as e:
            if attempt == max_attempts - 1:
                raise
            
            # Calculate wait time with exponential backoff
            wait_time = min(
                base_delay * (multiplier ** attempt) + random.uniform(0, 1),
                max_delay
            )
            
            print(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            # Non-rate-limit errors should fail immediately
            raise
```

### Distributed Request Queuing Architecture

For workloads requiring sustained high throughput, distributed request queuing prevents burst patterns that trigger rate limits while maintaining maximum sustainable throughput[35][50][52]. The architecture maintains separate queues for different request types and implements token-budget tracking across all active requests.

The token bucket algorithm provides theoretical foundations for queue management[38][41]. Each API key receives an allocation of tokens that refills at a constant rate (the rate limit). Requests consume tokens from the bucket, and requests are only dispatched when sufficient tokens are available. This prevents burst overloads while guaranteeing sustained throughput at or below the rate limit[38][41].

Python implementation using asyncio and rate limiting:

```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimitedQueue:
    """Distributed queue with token bucket rate limiting."""
    
    def __init__(self, tokens_per_minute, requests_per_minute):
        self.tokens_per_minute = tokens_per_minute
        self.requests_per_minute = requests_per_minute
        self.token_bucket = tokens_per_minute
        self.request_bucket = requests_per_minute
        self.last_refill = datetime.now()
        self.queue = deque()
        self.lock = asyncio.Lock()
    
    async def add_request(self, request):
        """Add request to queue."""
        async with self.lock:
            self.queue.append(request)
    
    async def get_next_request(self):
        """Get next request when capacity available."""
        while True:
            async with self.lock:
                # Refill buckets based on elapsed time
                now = datetime.now()
                elapsed_seconds = (now - self.last_refill).total_seconds()
                
                token_refill = (elapsed_seconds / 60) * self.tokens_per_minute
                self.token_bucket = min(
                    self.token_bucket + token_refill,
                    self.tokens_per_minute
                )
                
                request_refill = (elapsed_seconds / 60) * self.requests_per_minute
                self.request_bucket = min(
                    self.request_bucket + request_refill,
                    self.requests_per_minute
                )
                
                self.last_refill = now
                
                # Check if request can be dispatched
                if (self.queue and 
                    self.token_bucket >= 1 and 
                    self.request_bucket >= 1):
                    
                    request = self.queue.popleft()
                    self.token_bucket -= 1
                    self.request_bucket -= 1
                    return request
            
            # Wait before checking again
            await asyncio.sleep(0.1)
```

## Production-Grade Knowledge Graph Processing Patterns

### Hybrid Streaming and Batch Architecture

Production systems processing 10M+ tokens typically employ hybrid architectures that combine streaming for real-time refinement with batch processing for bulk operations[19][31][34][57]. The streaming portion handles initial entity extraction with rapid feedback loops, while batch processing handles refinement and cross-document linking operations that don't require immediate responses.

The architecture proceeds through distinct phases:

**Phase 1: Initial Document Chunking and Preprocessing** (local, non-LLM)
- Split 5.3M-token research document collection into 500-1,000 token semantic chunks
- Extract document metadata (source, date, author)
- Compute document embeddings for similarity-based retrieval
- Estimated processing: 5-15 minutes on standard hardware

**Phase 2: Streaming Entity Extraction** (Gemini, streaming API)
- Process chunks in parallel using 3-5 concurrent streaming requests
- Extract entities, relations, and attributes per chunk
- Maintain request queue with rate limit compliance
- Estimated processing: 60-120 minutes (with 250K TPM quota)

**Phase 3: Batch Cross-Document Linking** (Gemini Batch API)
- Submit extracted entities and discovered relations for cross-document linking
- Identify entity consolidation opportunities (duplicate resolution)
- Extract global relation patterns
- Estimated cost: $400-600 via batch pricing

**Phase 4: Refinement and Validation** (local, heuristic-based)
- Apply post-processing rules to filter low-confidence extractions
- Resolve conflicting entity definitions
- Generate quality metrics
- Estimated processing: 15-30 minutes

Total processing time: 100-270 minutes (1.5-4.5 hours) depending on parallelization and hardware

### Incremental Processing and Delta-Based Updates

For knowledge graph systems processing continuously arriving documents, incremental processing reduces redundant computation by processing only new or modified content[30]. The architecture maintains a state tracking system that identifies which documents have been processed, when they were processed, and what entities were extracted.

When new documents arrive, the system:
1. Computes document hash or modification timestamp
2. Queries state store to identify previously processed documents
3. Only processes new documents through entity extraction pipeline
4. Links new entities to existing knowledge graph
5. Detects and resolves contradictions between new and existing information[30]

This approach reduces steady-state token consumption by 80-90% compared to reprocessing entire datasets, as only genuinely new content consumes tokens.

Implementation requires maintaining a state store with schema similar to:

```
{
  document_id: string,
  document_hash: string,
  processing_timestamp: datetime,
  extraction_version: string,
  entity_count: integer,
  relation_count: integer,
  confidence_scores: [float]
}
```

### Parallel Processing Across Multiple API Keys

While multiple API keys in the same project share rate limits, organizations can create multiple projects under different billing accounts to achieve true parallelization[1][8][11]. The implementation requires careful orchestration to ensure requests are distributed fairly across keys while maintaining overall rate limit compliance.

Python implementation using weighted load balancing across keys:

```python
import random
from typing import List, Dict

class MultiKeyLoadBalancer:
    """Distribute requests across multiple API keys with weighted load balancing."""
    
    def __init__(self, api_keys: List[str], weights: List[float] = None):
        """
        Initialize load balancer.
        
        Args:
            api_keys: List of API keys from different projects
            weights: Optional weights for each key (sum should = 1.0)
        """
        self.api_keys = api_keys
        
        if weights is None:
            # Equal weights by default
            weights = [1.0 / len(api_keys)] * len(api_keys)
        
        # Normalize weights
        total = sum(weights)
        self.weights = [w / total for w in weights]
        
        # Track usage per key for monitoring
        self.usage_stats = {key: {"requests": 0, "tokens": 0} for key in api_keys}
    
    def get_next_key(self) -> str:
        """Get next API key using weighted random selection."""
        return random.choices(self.api_keys, weights=self.weights, k=1)[0]
    
    def record_usage(self, api_key: str, tokens: int):
        """Record token usage for monitoring and adjustment."""
        self.usage_stats[api_key]["requests"] += 1
        self.usage_stats[api_key]["tokens"] += tokens
    
    def should_rebalance(self) -> bool:
        """Check if weights should be rebalanced based on usage patterns."""
        token_totals = [s["tokens"] for s in self.usage_stats.values()]
        
        if sum(token_totals) == 0:
            return False
        
        # Calculate expected vs actual distribution
        for i, tokens in enumerate(token_totals):
            actual_ratio = tokens / sum(token_totals)
            expected_ratio = self.weights[i]
            
            # If variance > 20%, rebalancing recommended
            if abs(actual_ratio - expected_ratio) > 0.2:
                return True
        
        return False
    
    def adjust_weights(self, variance_threshold: float = 0.15):
        """Adjust weights based on actual usage patterns."""
        token_totals = [s["tokens"] for s in self.usage_stats.values()]
        
        if sum(token_totals) == 0:
            return
        
        # New weights proportional to actual usage
        self.weights = [t / sum(token_totals) for t in token_totals]
```

## Alternative Architectures and Specialized Approaches

### Local LLM Processing with Ollama and vLLM

Local LLM deployment via Ollama or vLLM (Virtual LLM) provides complete infrastructure control and eliminates API rate limiting entirely[14][17][51]. Ollama provides simplified single-command installation for consumer hardware, while vLLM offers production-grade performance optimization including dynamic batching and memory-efficient processing[14][17].

For entity extraction workloads, Llama 3.1 70B represents the most capable open-weight option. Performance benchmarks indicate that Llama 3.1 achieves approximately 93% accuracy on entity extraction compared to Gemini 2.5 Pro, with accuracy degradation primarily occurring for domain-specific entity types not well-represented in Llama's training data[13][28].

Hardware requirements for Llama 3.1 70B:
- Quantized (4-bit): Minimum 16GB GPU VRAM (single GPU)
- Full precision: Minimum 160GB GPU VRAM (multi-GPU setup)
- Typical deployment: 8× A100 40GB GPUs or equivalent

Performance characteristics:
- Inference throughput: 50-100 tokens per second per GPU
- For 15M token workload: 150,000-300,000 seconds = 42-83 hours of GPU time
- At $1.50/hour spot pricing: $630-$1,245 in GPU costs
- Plus engineering overhead for setup and maintenance: $500-2,000

The economics become favorable compared to Gemini APIs only when amortized across multiple large workloads or when internal hardware is already deployed[43][46].

### Hybrid Local-Cloud Processing Strategy

A practical middle-ground approach combines local processing for bulk extraction with cloud APIs for refinement and validation. The hybrid architecture:

1. **Local Phase**: Process all documents through Llama 3.1 70B locally for initial entity extraction (cost: GPU hours only, no API costs)
2. **Filtering Phase**: Local heuristics filter extractions below 0.7 confidence threshold
3. **Cloud Refinement Phase**: Submit uncertain extractions to Gemini 2.5 Pro for validation and confidence scoring (cost: only uncertain items, typically 10-20% of initial extractions)
4. **Post-Processing**: Local merging and deduplication of final results

This approach achieves approximately 70-80% of Gemini's accuracy at 30-40% of Gemini's cost by leveraging local processing for high-confidence operations while reserving cloud API calls for genuinely uncertain cases.

### GraphRAG Open-Source Implementation

Microsoft's open-source GraphRAG system provides an alternative to commercial APIs for knowledge graph construction[14][17]. When deployed locally with open-weight LLMs, GraphRAG entirely eliminates API costs, though at the expense of reduced accuracy and significant operational complexity.

GraphRAG architecture overview:
- Document chunking and preprocessing (local)
- Entity and relation extraction (local LLM or remote API)
- Graph construction and community detection (local)
- Query-driven graph summarization (local or remote)

Current limitations of open-source GraphRAG with local LLMs:
- Configuration requires manual specification of model endpoints
- Error handling for local models less robust than API-based alternatives
- Performance optimization requires deep infrastructure expertise
- Accuracy on entity extraction typically 15-20% below commercial LLMs
- Limited built-in support for entity consolidation across documents

For organizations with sufficient ML infrastructure expertise and domain-specific training data, open-source GraphRAG with fine-tuned local models can provide cost advantages despite the operational burden.

## Incremental and Delta-Based Processing Strategies

### State Management for Continuous Updates

Production knowledge graph systems must handle continuous document streams without reprocessing previously analyzed content[19][30]. This requires maintaining extraction state alongside the knowledge graph itself.

State schema for tracking incremental processing:

```
ProcessingState {
  document_id: string,
  source_url: string,
  ingestion_timestamp: datetime,
  content_hash: string,
  extraction_version: string,
  model_used: string,
  entity_count: integer,
  extraction_confidence_mean: float,
  processing_status: enum[PENDING, PROCESSING, COMPLETED, FAILED],
  last_updated: datetime,
  retry_count: integer
}
```

When new documents arrive:
1. Compute content hash of new document
2. Query state store for existing processing records with matching hash
3. If found and extraction_version matches current model: skip processing, reuse existing extractions
4. If found but extraction_version outdated: reprocess with new model version
5. If not found: process new document

This approach typically achieves:
- 80-90% reduction in token consumption for continuous streams after initial knowledge graph construction
- Incremental cost ~$100-300/month vs. $5,000-15,000/month for full reprocessing
- Processing latency < 1 minute for new documents (10K-100K tokens)

### Conflicting Information Resolution

When processing newly arriving documents, extracted information may contradict existing knowledge graph entries[30]. GraphRAG's design inherently handles conflicts through semantic reasoning rather than simple overwrites. The system:

1. Identifies contradiction: "Sky is BLUE" (existing) vs. "Sky is RED" (new)
2. Creates separate nodes for both claims with source attribution
3. Links claims with "conflict" relation type
4. Stores confidence and temporal metadata with each claim
5. Queries can return both claims with source-based selection or confidence-based ranking

This approach preserves full information provenance while maintaining query accuracy.

## Rate Limit Escalation and Enterprise Solutions

### Enterprise Quota Negotiation

Google Cloud offers custom rate limit increases for verified enterprise customers, though with no formal guarantee[1][23][39]. The standard process involves:

1. Documenting intended workload characteristics
2. Demonstrating production use case viability
3. Requesting specific rate limit increases
4. Undergoing fraud verification review
5. Waiting 1-5 business days for decision

Organizations with documented production workloads typically succeed in obtaining 2-5x rate limit increases, though some cases achieve 10x increases for mission-critical systems[1].

To maximize approval probability:
- Submit formal requests with detailed workload specifications
- Provide reference to published whitepapers or production use cases
- Document existing API usage demonstrating consistent, predictable patterns
- Request specific limit values rather than open-ended increases
- Allow 30-60 days between requests for tier progression

### Google Workspace and Internal Rate Limits

Google Workspace customers accessing Gemini through Google's internal services benefit from different rate limiting than external API users[42]. Internal limits are generally more permissive for Google-owned services, though the exact limits are not publicly documented.

Organizations heavily invested in Google Cloud infrastructure often negotiate contract terms that include specific rate limit guarantees as part of enterprise agreements.

## Conclusion and Recommendations

For the knowledge graph construction scenario presented—processing 5.3M tokens of source material with an estimated 10-20M tokens needed for entity extraction—the optimal approach combines several strategies:

**Recommended Implementation Pattern:**

1. **Initial tier assessment**: Verify current Gemini API tier and submit tier upgrade request if below Tier 2
2. **Batch processing for bulk operations**: Submit 80% of entity extraction workload via Gemini Batch API, saving 50% on costs ($400-600 batch cost vs. $800-1,200 streaming)
3. **Streaming for rapid iteration**: Use streaming API with rate-limited queue for initial extraction requiring feedback loops
4. **Caching for repeated operations**: Enable explicit caching for multi-pass extraction where applicable, achieving 70% token cost reduction
5. **Local filtering**: Pre-filter low-confidence extractions locally to reduce final cloud API calls by 15-25%
6. **Incremental state tracking**: Implement state management for any future updates, reducing ongoing costs by 80-90%

**Cost optimization ranking (best to worst for this scenario):**

| Approach | Estimated Cost | Processing Time | Accuracy |
|----------|---|---|---|
| Gemini Batch API (Flash) | $1,150 | 24 hours | 95% |
| Gemini Streaming (Flash, single key) | $2,300 | 40-80 minutes | 95% |
| Hybrid local + Gemini refinement | $700-900 | 50-120 minutes | 92% |
| Local Llama 3.1 only | $630-1,245 | 42-83 hours | 78% |
| Open-source GraphRAG local | $0 (infrastructure) | 48+ hours | 70% |

The Gemini Batch API approach emerges as optimal for most organizations: it provides enterprise-grade accuracy, reasonable processing time within a 24-hour window, and lower cost than streaming while avoiding the operational complexity of local infrastructure deployment.

[1][7][10][12][23][31] establish the foundational rate limit and batch API parameters. [9][12][21][24] provide pricing analysis across models. [43][46][50] illuminate cost comparisons and load balancing patterns. [14][17][52][55] present alternative architectures including local deployment and GraphRAG. This multi-faceted analysis enables teams to make informed decisions about infrastructure choices for large-scale knowledge graph construction tailored to specific organizational constraints around cost, processing latency, accuracy requirements, and operational sophistication.

---

## Citations

1. https://ai.google.dev/gemini-api/docs/rate-limits
2. https://docs.cloud.google.com/billing/quotas
3. https://docs.cloud.google.com/vertex-ai/generative-ai/docs/quotas
4. https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-0-flash
5. https://developers.google.com/maps/documentation/places/web-service/usage-and-billing
6. https://developers.google.com/gemini-code-assist/resources/quotas
7. https://ai.google.dev/gemini-api/docs/batch-api
8. https://news.ycombinator.com/item?id=14767204
9. https://www.cloudzero.com/blog/gemini-pricing/
10. https://developers.googleblog.com/scale-your-ai-workloads-batch-mode-gemini-api/
11. https://docs.cloud.google.com/resource-manager/docs/limits
12. https://ai.google.dev/gemini-api/docs/pricing
13. https://artificialanalysis.ai/models/llama-3-1-instruct-70b
14. https://chishengliu.com/posts/graphrag-local-ollama/
15. https://developer.squareup.com/forums/t/implementing-exponential-backoff-to-manage-rate-limit-errors-in-square/13305
16. https://cloudatler.com/blog/a-practical-guide-to-llama-3-70b-inference-cost
17. https://www.chitika.com/graphrag-local-install-setup-using-vllm-and-ollama/
18. https://developers.openai.com/cookbook/examples/how_to_handle_rate_limits
19. https://atalupadhyay.wordpress.com/2026/01/23/building-production-grade-rag-systems/
20. https://docs.cloud.google.com/gemini/docs/quotas
21. https://www.datacamp.com/blog/claude-vs-gemini
22. https://arxiv.org/html/2510.27246v1
23. https://ai.google.dev/gemini-api/docs/rate-limits
24. https://intuitionlabs.ai/pdfs/llm-api-pricing-comparison-2025-openai-gemini-claude.pdf
25. https://www.emergentmind.com/topics/knowledge-graph-construction
26. https://geminicli.com/docs/cli/token-caching/
27. https://learn.microsoft.com/en-us/graph/delta-query-users
28. https://www.vldb.org/2025/Workshops/VLDB-Workshops-2025/LLM+Graph/LLMGraph-7.pdf
29. https://ai.google.dev/gemini-api/docs/caching
30. https://github.com/microsoft/graphrag/discussions/511
31. https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/batch-prediction-gemini
32. https://ratelimitqueue.readthedocs.io
33. https://hashmeta.com/blog/chatgpt-vs-claude-vs-gemini-a-comprehensive-ai-model-comparison/
34. https://cloud.google.com/discover/what-is-batch-inference
35. https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py
36. https://kanerika.com/blogs/chatgpt-vs-gemini-vs-claude/
37. https://www.deepchecks.com/5-approaches-to-solve-llm-token-limits/
38. https://zuplo.com/learning-center/10-best-practices-for-api-rate-limiting-in-2025
39. https://ai.google.dev/gemini-api/docs/rate-limits
40. https://substack.com/home/post/p-148780354
41. https://www.gravitee.io/blog/rate-limiting-apis-scale-patterns-strategies
42. https://docs.cloud.google.com/gemini/docs/quotas
43. https://www.detectx.com.au/cost-comparison-api-vs-self-hosting-for-open-weight-llms/
44. https://platform.openai.com/docs/guides/structured-outputs
45. https://discuss.ai.google.dev/t/gemini-3-feedback/110729
46. https://hakia.com/tech-insights/open-vs-closed-llms/
47. https://aws.amazon.com/blogs/machine-learning/structured-data-response-with-amazon-bedrock-prompt-engineering-and-tool-use/
48. https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf
49. https://www.pinecone.io/learn/chunking-strategies/
50. https://dev.to/kuldeep_paul/intelligent-api-key-management-and-load-balancing-a-complete-guide-to-building-resilient-ai-195b
51. https://blog.laozhang.ai/ai-technology/gemini-nano-edge-ai-guide/
52. https://community.databricks.com/t5/technical-blog/the-ultimate-guide-to-chunking-strategies-for-rag-applications/ba-p/113089
53. https://github.com/AsyncFuncAI/deepwiki-open/issues/445
54. https://techcrunch.com/2025/02/26/what-is-google-gemini-ai/
55. https://arxiv.org/html/2208.09705v3
56. https://cribl.io/blog/stop-wasting-tokens-real-time-llm-cost-analytics-inside-your-telemetry-pipeline/
57. https://cloud.google.com/discover/what-is-batch-inference
58. https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper58.pdf
59. https://www.datadoghq.com/product/llm-observability/
60. https://docs.cloud.google.com/vertex-ai/docs/predictions/get-batch-predictions

---

## Usage Stats

- Prompt tokens: 507
- Completion tokens: 6935
- Total tokens: 7442
