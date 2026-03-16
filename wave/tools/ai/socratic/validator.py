"""SocraticValidator — antimatter pattern detection (the Critic Agent)."""

import json
from typing import Any, Dict

import sys
from pathlib import Path
_AI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_DIR))

from _shared import retry_with_backoff, HAS_GENAI
if HAS_GENAI:
    from google import genai


class SocraticValidator:
    """Detect AI liabilities (Antimatter Patterns) via Socratic critique."""

    def __init__(self, semantic_config: dict):
        self.laws = semantic_config.get("antimatter", [])

    def validate(
        self, client, model: str, code_context: str, concept_role: str
    ) -> Dict[str, Any]:
        """Run antimatter audit on code context.

        Returns dict with {compliant, violations, critique_summary}
        or {status: "SKIPPED"/"ERROR", reason/error}.
        """
        if not self.laws:
            return {"status": "SKIPPED", "reason": "No Antimatter Patterns defined"}

        prompt = f"""
        ACT AS: Socratic Supervisor (Senior Architect Auditor).
        TASK: Audit the following code candidate (Role: {concept_role}) for 'Antimatter' violations.

        CODE CONTEXT:
        {code_context[:30000]}

        ANTIMATTER LAWS (Violations to detect):
        """
        for law in self.laws:
            prompt += (
                f"- [{law['id']}] {law['name']}: {law['description']}\n"
                f"  Check: {law['detection_prompt']}\n"
            )

        prompt += """

        OUTPUT FORMAT (JSON):
        {
          "compliant": boolean,
          "violations": [
            {"law_id": "AMxxx", "severity": "HIGH/MEDIUM/LOW", "reasoning": "..."}
          ],
          "critique_summary": "One sentence summary of the audit."
        }
        """

        try:
            def make_request():
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )

            response = retry_with_backoff(make_request)
            return json.loads(response.text)
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
