# Multi-LLM Consensus Annotation Guide

**Goal:** Generate high-quality ground truth using 3 LLMs voting in consensus

**Quality:** 90-95% (near-perfect with human review of conflicts)

---

## Setup

### Install Dependencies
```bash
pip install openai anthropic requests
```

### Get API Keys
```bash
# OpenAI (GPT-4)
export OPENAI_API_KEY="sk-..."

# Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-..."

# Ollama (local, free)
ollama pull llama3.2
```

---

## Usage

### Full Consensus (All 3 LLMs)
```bash
python scripts/annotate_consensus.py \
  --openai-key $OPENAI_API_KEY \
  --anthropic-key $ANTHROPIC_API_KEY
```

**Time:** ~60 minutes (500 samples × 3 LLMs)  
**Cost:** ~$4 (GPT-4 + Claude)  
**Quality:** 90-95%

---

### Budget Option (GPT-4 + Ollama)
```bash
python scripts/annotate_consensus.py \
  --openai-key $OPENAI_API_KEY \
  --no-anthropic
```

**Time:** ~40 minutes  
**Cost:** ~$2  
**Quality:** 85-90%

---

### Free Option (Ollama + Claude)
```bash
python scripts/annotate_consensus.py \
  --anthropic-key $ANTHROPIC_API_KEY \
  --no-openai
```

**Time:** ~40 minutes  
**Cost:** Free (Ollama) + Claude credits  
**Quality:** 80-85%

---

## Output

### Main Output: `data/mini_validation_consensus.csv`

**Columns:**
- `consensus_role` - Majority vote result
- `confidence` - HIGH/MEDIUM/CONFLICT
- `agreement_count` - How many LLMs agreed
- `gpt4_vote`, `claude_vote`, `ollama_vote` - Individual votes

**Example:**
```csv
name,consensus_role,confidence,agreement_count,gpt4_vote,claude_vote,ollama_vote
get_user,Query,HIGH,3,Query,Query,Query
save_data,Command,MEDIUM,2,Command,Command,Query
UserService,Service,CONFLICT,1,Service,Entity,Repository
```

---

### Conflict File: `data/conflicts_for_review.txt`

**Lists samples where LLMs disagreed:**
```
CONFLICTS REQUIRING HUMAN REVIEW
============================================================

#42: UserService
  Votes: {'gpt4': 'Service', 'claude': 'Entity', 'ollama': 'Repository'}
  Consensus: Service
  → Manual review needed

#128: process_data
  Votes: {'gpt4': 'Transformer', 'claude': 'Command', 'ollama': 'Utility'}
  Consensus: Transformer
  → Manual review needed
```

---

## Quality Levels

### HIGH Confidence (All Agree)
✅ **Use as-is**  
- All 3 LLMs voted the same
- ~70-80% of samples
- No review needed

### MEDIUM Confidence (2/3 Agree)
⚠️ **Probably correct**  
- Majority vote (2 out of 3)
- ~15-20% of samples
- Optional: Spot-check a few

### CONFLICT (All Disagree)
❌ **Human review required**  
- Each LLM voted differently
- ~5-10% of samples
- **MUST review these manually**

---

## Human Review Process

1. **Open** `data/conflicts_for_review.txt`
2. **For each conflict:**
   - Read the code element details
   - Consider each LLM's vote
   - Make your own judgment
   - Update `consensus_role` in CSV
3. **Update confidence** to `HUMAN_VERIFIED`

**Time:** ~1-2 hours for 50 conflicts

---

## Final Accuracy Estimate

| Configuration | High % | Medium % | Conflict % | Est. Accuracy |
|---------------|--------|----------|------------|---------------|
| **3 LLMs** | 75% | 20% | 5% | 90-95% |
| **2 LLMs** | 60% | 30% | 10% | 85-90% |
| **1 LLM** | 100% | 0% | 0% | 80-85% |

**After human review of conflicts:**
- **3 LLMs + review:** 95-99% accuracy ⭐
- **2 LLMs + review:** 90-95% accuracy
- **1 LLM:** 80-85% accuracy (no review)

---

## Recommended Workflow

### Phase 1: Consensus Annotation (60 min)
```bash
python scripts/annotate_consensus.py
```

### Phase 2: Review Conflicts (1-2 hours)
```bash
# Open conflicts_for_review.txt
# Review ~50 samples manually
# Update CSV with corrections
```

### Phase 3: Validation (2 min)
```bash
python scripts/validate_annotations.py \
  --input data/mini_validation_consensus.csv
```

**Total time:** 2-3 hours  
**Total cost:** ~$4  
**Quality:** 95-99%

---

## Troubleshooting

**"OpenAI API key invalid"**
```bash
export OPENAI_API_KEY="sk-..."
```

**"Ollama connection refused"**
```bash
ollama serve  # Start Ollama
ollama pull llama3.2  # Download model
```

**"Anthropic rate limit"**
- Add `time.sleep(1)` between requests
- Or use fewer LLMs

---

**This is the gold standard for ground truth generation.**
