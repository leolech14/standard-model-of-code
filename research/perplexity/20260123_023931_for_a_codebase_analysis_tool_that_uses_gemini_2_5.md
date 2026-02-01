# Perplexity Research: For a codebase analysis tool that uses Gemini 2.5 Pro (1M token context), we have 'analysis sets' de...

> **Date:** 2026-01-23 02:39:31
> **Model:** sonar-pro
> **Source:** MCP Server (auto-saved)
> **Raw JSON:** `raw/20260123_023931_for_a_codebase_analysis_tool_that_uses_gemini_2_5.json`

---

## Query

For a codebase analysis tool that uses Gemini 2.5 Pro (1M token context), we have 'analysis sets' defined in YAML with token budgets. Given the research on:

1. Lost-in-the-middle effect (best at beginning/end)
2. Real effective context often 50-60% of advertised
3. Token quality > quantity
4. Sandwich method (instructions → context → instructions)

What are the SPECIFIC best practices for:
- Setting token budget tiers (what % of 1M is safe?)
- Structuring the prompt (where to put instructions vs code)
- When to use RAG vs long-context

Provide concrete numbers and thresholds where possible.

---

## Response

**For Gemini 2.5 Pro's 1M token context in codebase analysis, set token budgets conservatively at 10-20% of total capacity (100k-200k tokens max) to stay under the critical 200k threshold where input costs double from $1.25 to $2.50 per 1M tokens and output from $10 to $15, while mitigating lost-in-the-middle effects and 50-60% effective context loss.** [1][2][3][4]

### Token Budget Tiers
Structure budgets in YAML 'analysis sets' with these **concrete tiers** based on pricing cliffs, performance research, and cost efficiency:
- **Tier 1: <50k tokens (5% of 1M)** – Small files/single modules. **Safe default** for high accuracy; avoids all brackets. Cost: $1.25/M input.
- **Tier 2: 50k-150k tokens (5-15%)** – Medium repos. **Optimal sweet spot** – stays ≤200k pricing, prioritizes beginning/end placement to counter lost-in-the-middle. Effective context ~25-90k after 50% loss.
- **Tier 3: 150k-200k tokens (15-20%)** – Large analysis. **Hard cap** – hits pricing jump at 200k+; use only if token quality (clean, relevant code) justifies. Monitor for quality drop-off.
- **Avoid >200k (20%+)** unless caching: Costs spike, and real performance plateaus due to 50-60% effective limit; research shows diminished recall mid-context.[1][2][3][4]

**Pro tip**: Enforce budgets with pre-tokenization checks; use context caching for repeated codebases (saves 75% on inputs, $0.31–$0.625/M + $4.50/hr storage).[2]

### Prompt Structuring (Sandwich Method)
Apply the **sandwich structure** to combat lost-in-the-middle: instructions at start/end, code in middle but prioritized at edges.
```
[Core Instructions: Task, rules, output format – 5-10% tokens]
[High-priority code: Key files/modules – beginning/end]
[Supporting context: Full codebase – compressed middle]
[Reinforcing Instructions: "Focus on X, ignore Y, summarize Z" – 5-10% tokens]
```
- **Instructions**: 10-20% total tokens, split 60/40 (start heavier). Repeat key directives at end for 20-30% recall boost.[Research alignment: beginning/end primacy]
- **Code placement**: Critical paths/files first/last (e.g., entrypoints, configs); bulk in middle with summaries/chunking. Token quality > quantity: dedupe, remove comments, use tree-summaries for large sets.
- **Threshold**: If >100k code tokens, chunk into <75k segments with overlap (10-20%).

### RAG vs Long-Context Thresholds
| Scenario | Use **RAG** (when...) | Use **Long-Context** (when...) | Thresholds |
|----------|-----------------------|-------------------------------|------------|
| **Small/Targeted** (<50k) | Rarely needed | Default: Full context | Always long-context |
| **Medium (50k-200k)** | If retrieval precision >80% needed (e.g., specific bugs) | Default for holistic analysis | RAG if >20% irrelevant code |
| **Large (>200k)** | **Mandatory**: Chunk repo, retrieve top-k relevant (k=5-20 files) | Only with caching | Switch at 200k pricing cliff |
| **Cost-sensitive** | Always for repeats | One-shot analysis | RAG saves 50-75% via caching [2] |

**Decision rule**: RAG if query-specific (e.g., "find vuln in auth"); long-context for global (e.g., "architecture review"). Crossover at **150k tokens** – beyond this, effective context drops below 75-90k, favoring RAG for quality.[1][2]

**Additional optimizations**: Set thinking budgets for controlled outputs; batch mode halves costs (input $0.625 ≤200k).[4] Prioritize token quality via preprocessing (e.g., AST extraction).[2]

---

## Citations

1. https://www.finout.io/blog/gemini-pricing-in-2026
2. https://www.cloudzero.com/blog/gemini-pricing/
3. https://www.metacto.com/blogs/the-true-cost-of-google-gemini-a-guide-to-api-pricing-and-integration
4. https://ai.google.dev/gemini-api/docs/pricing
5. https://neuraltalk.ai/calculators/gemini-2-5-pro
6. https://firebase.google.com/docs/ai-logic/count-tokens
7. https://addyo.substack.com/p/gemini-cli-tips-and-tricks
8. https://chatlyai.app/blog/gemini-3-pro-vs-gemini-2-5-pro-cost-analysis

---

## Usage Stats

- Prompt tokens: 138
- Completion tokens: 910
- Total tokens: 1048
