# Perplexity Research: Deterministic Archival Evaluation

> **Date:** 2026-01-22 15:55:00
> **Model:** sonar-deep-research
> **Source:** External MCP (manual-save, local MCP not yet active)
> **Raw JSON:** `raw/20260122_155500_deterministic_archival_evaluation.json`

---

## Query

We have built a local MCP (Model Context Protocol) server in Python that wraps the Perplexity API and implements a deterministic auto-save pipeline:

1. Query arrives via JSON-RPC over stdio
2. Call Perplexity API
3. Save TWO files automatically:
   - raw/{timestamp}_{slug}.json (COMPLETE API response)
   - docs/{timestamp}_{slug}.md (human-readable markdown)
4. Return response with save confirmation

Our goal is ZERO information loss from research queries.

Please evaluate this approach:
1. Is the dual-format save (JSON + Markdown) a good pattern for research archival?
2. Are there better alternatives for deterministic, lossless archival of API responses?
3. What metadata should we include beyond the raw API response?
4. Should we implement compression, indexing, or other features?
5. How do production systems handle similar research/knowledge archival requirements?

---

## Response

# Evaluating Deterministic Auto-Save Architectures for Research API Archival: A Comprehensive Assessment of Dual-Format Preservation in Model Context Protocol Implementations

## Executive Summary

Your dual-format auto-save pipeline represents a pragmatic approach to research query archival that balances accessibility with completeness, yet several established digital preservation patterns and production system implementations offer pathways to strengthen your architecture. This report evaluates your current design against validated archival methodologies from the digital preservation community, information management research, and production systems handling similar knowledge-intensive workflows. The analysis reveals that while your JSON-plus-Markdown pattern captures essential information, a more robust approach would integrate cryptographic fixity verification, structured metadata envelopes, content-addressed storage principles, and hierarchical retention policies aligned with research lifecycle requirements.

## Key Findings

### 1. Dual-Format Preservation Strengths

- **Complementary formats**: JSON preserves machine-actionable structure, Markdown provides human accessibility
- **Long-term durability**: Both formats are text-based, not tied to specific software
- **Basic discovery**: Timestamp + slug naming supports temporal ordering and semantic navigation

### 2. Critical Gap: No Fixity Verification

**Your current architecture lacks cryptographic integrity checking.** Without checksums (SHA-256), there is no mechanism to detect:
- Silent corruption during storage
- Bit-level failures over time
- Accidental or malicious modification

**Recommendation**: Implement checksum computation at save time, store in manifest, verify periodically.

### 3. Recommended Archival Standards

| Standard | Purpose | Implementation |
|----------|---------|----------------|
| **BagIt (RFC 8493)** | File packaging with manifests | Wrap each research session in a bag |
| **PREMIS** | Preservation metadata | Record events, agents, rights |
| **Content-Addressable Storage** | Immutable, deduplicated storage | Name files by SHA-256 hash |
| **FAIR Principles** | Findability, Accessibility, Interoperability, Reusability | Structured metadata, unique IDs |

### 4. Essential Metadata to Capture

Beyond raw API response, capture:
- **Request metadata**: Query text, model, parameters, user ID
- **Execution metadata**: Timestamp, latency, tokens used, confidence scores
- **Provenance**: Who initiated, why, under what context
- **Fixity**: SHA-256 checksums of all files
- **Relationships**: Links to related queries, external references

### 5. Production System Patterns

| Pattern | Description |
|---------|-------------|
| **Tiered Storage** | Hot (SSD) → Warm → Cold (tape) based on access patterns |
| **Event Sourcing** | Immutable event log of all interactions |
| **3-2-1 Backup** | 3 copies, 2 media types, 1 offsite |
| **Periodic Scrubbing** | Monthly checksum verification |

### 6. Compression Recommendation

**NOT recommended for your scale.** Perplexity responses are kilobytes. Compression adds:
- Software dependency (decompression required)
- Reduced immediate accessibility
- Negligible storage savings

Focus compression only at institutional scale (millions of queries).

### 7. Indexing Recommendation

**YES - Implement search indexing.** Without indexing, archived information becomes invisible over time. Recommended:
- SQLite database for smaller deployments
- Full-text search over query content
- Metadata filtering (date, model, user)

## Phased Implementation Roadmap

| Phase | Scope | Priority |
|-------|-------|----------|
| **Phase 1** | Add SHA-256 checksums + manifest | IMMEDIATE |
| **Phase 2** | Structured metadata capture | Week 1-2 |
| **Phase 3** | Automated replication (3-2-1) | Week 3-4 |
| **Phase 4** | BagIt-compatible packaging | Month 2 |
| **Phase 5** | Search indexing | Month 3 |
| **Phase 6** | Audit logging / event sourcing | Month 4 |

## Recommended Metadata Schema

```json
{
  "archival_metadata": {
    "package_id": "sha256-...",
    "created_timestamp": "ISO-8601",
    "retention_policy": "indefinite"
  },
  "request_metadata": {
    "query_text": "...",
    "model": "Sonar-Pro",
    "parameters": {"temperature": 0.7}
  },
  "response_metadata": {
    "latency_ms": 1234,
    "tokens_used": {"input": 100, "output": 150},
    "sources_consulted": ["url1", "url2"]
  },
  "fixity_information": {
    "raw_response_sha256": "...",
    "markdown_sha256": "...",
    "last_verified": "ISO-8601"
  }
}
```

## Conclusion

Your dual-format JSON + Markdown approach is **fundamentally sound** and demonstrates awareness that research archival serves multiple needs. To achieve **ZERO information loss**, prioritize:

1. **Fixity verification** (SHA-256 checksums) - most critical gap
2. **Structured metadata** capture
3. **Search indexing** for discovery
4. **Automated replication** for disaster recovery

The phased implementation approach allows incremental improvement without overwhelming complexity.

---

## Citations

1. https://modelcontextprotocol.io/specification/draft/basic/security_best_practices
2. https://apyhub.com/blog/converting-md-best-markdown-apis
3. https://www.dpconline.org/handbook/digital-preservation/preservation-issues
4. https://modelcontextprotocol.info/docs/best-practices/
5. https://docs.gitlab.com/development/documentation/restful_api_styleguide/
6. https://pmc.ncbi.nlm.nih.gov/articles/PMC12685206/
7. https://blogs.loc.gov/thesignal/2014/04/protect-your-data-file-fixity-and-data-integrity/
8. https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums
9. https://www.archondatastore.com/blog/storage-tiering-and-data-tiering/
10. https://docs.perplexity.ai/llms-full.txt
11. https://www.loc.gov/standards/premis/
12. https://www.digitalpreservation.gov/series/challenge/premis.html
13. https://pinata.cloud/blog/what-is-content-addressability/
14. https://microservices.io/patterns/data/event-sourcing.html
15. https://www.digitalpreservation.gov/documents/bagitspec.pdf
16. https://www.go-fair.org/fair-principles/
17. https://www.bizdata360.com/data-archival-strategy-guide-2025/
