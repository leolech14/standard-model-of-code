# Codex Submission: 3-Step Collider Insights Pipeline

## Architecture Map

```text
OUT-OF-BAND (Collider run)
Repository semantic/topological analysis
  -> emits collider_insights.json

IN-MCP (get_collider_insights)
1) Extraction
   _find_insights_json(db_dir):
   a) db_dir/collider_insights.json
   b) cwd/.collider/collider_insights.json
   c) newest /tmp/**/collider_insights.json
   Then JSON load, attach _source, add stale-data warning if age > 7 days.

2) Processing
   _format_insights_markdown(insights):
   - Build digest: grade, health score, Q-score, nodes/edges, health components
   - Sort findings by severity: critical -> high -> medium -> low -> info
   - Map severity to GitHub alerts:
     critical=CAUTION, high=WARNING, medium=IMPORTANT, low=TIP, info=NOTE
   - Emit structured action fields:
     What it is / Evidence / Action to Take / Why
   - Add navigation priorities from navigation.start_here

3) Delivery
   Return final Markdown digest string to the caller LLM.
   If missing/unreadable JSON: return structured JSON error message.
```

## Why This Design Is Superior

- The model receives a curated digest, not raw JSON noise.
- Prioritization is deterministic in code, so risk ordering is consistent.
- Output schema is stable (alerts + action fields), improving agent reliability.
- Token usage drops because extraction and synthesis happen inside the MCP tool.
