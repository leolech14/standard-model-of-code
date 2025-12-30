"""
Semantic Lens
=============

Interrogates code atoms for meaning and certainty:
- R3: CLASSIFICATION - What kind is it?
- R7: SEMANTICS - What does it mean?
- R8: EPISTEMOLOGY - How certain are we?
"""

from typing import Dict, Any, List


class SemanticLens:
    """
    Reveals semantic properties of code atoms.

    Handles classification, meaning, and certainty questions.
    """

    # ==================== R3: CLASSIFICATION ====================

    def lens_r3_classification(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        R3: CLASSIFICATION - What kind is it?

        Reveals: Role, category, atom type
        """
        role = node.get("role", "Unknown")
        dimensions = node.get("dimensions", {})

        atom_type = dimensions.get("D1_WHAT", node.get("kind", "Unknown"))
        layer = dimensions.get("D2_LAYER", "Unknown")

        confidence = node.get("role_confidence", 0.0)
        discovery_method = node.get("discovery_method", "unknown")

        quality = "high" if confidence >= 80 else "medium" if confidence >= 50 else "low"

        return {
            "role": role,
            "atom_type": atom_type,
            "layer": layer,
            "confidence": confidence,
            "quality": quality,
            "discovery_method": discovery_method,
            "full_dimensions": dimensions,
        }

    # ==================== R7: SEMANTICS ====================

    def lens_r7_semantics(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        R7: SEMANTICS - What does it mean?

        Reveals: Purpose, intent, business meaning
        """
        docstring = node.get("docstring", "")
        name = node.get("name", "")
        role = node.get("role", "Unknown")
        dimensions = node.get("dimensions", {})

        layer = dimensions.get("D2_LAYER", "Unknown")
        lifecycle = dimensions.get("D7_LIFECYCLE", "Unknown")

        intent = self._extract_intent_from_name(name)
        purpose = self._extract_purpose_from_docstring(docstring)
        domain = self._infer_domain(node.get("file_path", ""))

        return {
            "purpose": purpose or f"Performs {intent} operation",
            "intent": intent,
            "business_domain": domain,
            "semantic_role": role,
            "lifecycle_phase": lifecycle,
            "layer_meaning": self._explain_layer(layer),
            "documented": len(docstring) > 0,
            "docstring": docstring[:200] if docstring else "",
        }

    def _extract_intent_from_name(self, name: str) -> str:
        """Extract semantic intent from function name."""
        name_lower = name.lower()

        if name_lower.startswith(("get", "fetch", "find", "load", "read", "query")):
            return "retrieval"
        elif name_lower.startswith(("set", "save", "store", "write", "update", "put")):
            return "persistence"
        elif name_lower.startswith(("create", "make", "build", "new", "init")):
            return "creation"
        elif name_lower.startswith(("delete", "remove", "destroy", "drop")):
            return "deletion"
        elif name_lower.startswith(("validate", "check", "verify", "ensure")):
            return "validation"
        elif name_lower.startswith(("calculate", "compute", "process")):
            return "computation"
        elif name_lower.startswith(("handle", "process", "on")):
            return "event_handling"
        else:
            return "transformation"

    def _extract_purpose_from_docstring(self, docstring: str) -> str:
        """Extract purpose from docstring."""
        if not docstring:
            return ""

        lines = docstring.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            return first_line.rstrip(".")

        return ""

    def _infer_domain(self, file_path: str) -> str:
        """Infer business domain from file path."""
        path_lower = file_path.lower()

        domains = {
            "user": ["user", "auth", "account", "profile"],
            "payment": ["payment", "billing", "invoice", "subscription"],
            "product": ["product", "inventory", "catalog"],
            "order": ["order", "cart", "checkout"],
            "analytics": ["analytics", "metrics", "stats", "report"],
            "notification": ["notification", "email", "sms", "alert"],
        }

        for domain, keywords in domains.items():
            if any(kw in path_lower for kw in keywords):
                return domain

        return "general"

    def _explain_layer(self, layer: str) -> str:
        """Explain what a layer means."""
        explanations = {
            "Core": "Business logic and domain rules",
            "Application": "Use cases and application workflows",
            "Infrastructure": "External integrations and data access",
            "Interface": "User-facing APIs and controllers",
            "Test": "Verification and validation",
        }
        return explanations.get(layer, "Unknown layer")

    # ==================== R8: EPISTEMOLOGY ====================

    def lens_r8_epistemology(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        R8: EPISTEMOLOGY - How certain are we?

        Reveals: Confidence, evidence, uncertainty
        """
        confidence = node.get("role_confidence", 0.0)
        discovery_method = node.get("discovery_method", "unknown")
        dimensions = node.get("dimensions", {})

        trust = dimensions.get("D8_TRUST", confidence)

        evidence = self._assess_evidence(node)
        uncertainties = self._identify_uncertainties(node, dimensions)
        quality = self._calculate_epistemic_quality(confidence, evidence)

        return {
            "confidence": confidence,
            "trust_score": trust,
            "discovery_method": discovery_method,
            "evidence": evidence,
            "uncertainties": uncertainties,
            "epistemic_quality": quality,
            "requires_review": confidence < 60,
            "high_confidence": confidence >= 80,
        }

    def _assess_evidence(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Assess what evidence we have for this classification."""
        evidence = {
            "has_docstring": len(node.get("docstring", "")) > 0,
            "has_type_hints": len(node.get("return_type", "")) > 0,
            "has_decorators": len(node.get("decorators", [])) > 0,
            "has_base_classes": len(node.get("base_classes", [])) > 0,
            "has_clear_name": len(node.get("name", "")) > 3,
        }

        evidence_count = sum(1 for v in evidence.values() if v)

        return {
            **evidence,
            "evidence_count": evidence_count,
            "evidence_strength": (
                "strong" if evidence_count >= 3
                else "medium" if evidence_count >= 2
                else "weak"
            )
        }

    def _identify_uncertainties(
        self,
        node: Dict[str, Any],
        dimensions: Dict[str, Any]
    ) -> List[str]:
        """Identify what we're uncertain about."""
        uncertainties = []

        if node.get("role", "Unknown") == "Unknown":
            uncertainties.append("Role is unknown")

        if node.get("role_confidence", 0) < 60:
            uncertainties.append("Low classification confidence")

        if dimensions.get("D2_LAYER") == "Unknown":
            uncertainties.append("Architectural layer unclear")

        if dimensions.get("D5_STATE") == "Unknown":
            uncertainties.append("Statefulness uncertain")

        if not node.get("docstring"):
            uncertainties.append("No documentation")

        return uncertainties

    def _calculate_epistemic_quality(
        self,
        confidence: float,
        evidence: Dict
    ) -> str:
        """Calculate overall epistemic quality."""
        evidence_strength = evidence.get("evidence_strength", "weak")

        if confidence >= 80 and evidence_strength == "strong":
            return "excellent"
        elif confidence >= 60 and evidence_strength in ["strong", "medium"]:
            return "good"
        elif confidence >= 40:
            return "fair"
        else:
            return "poor"

    # ==================== COMBINED ====================

    def interrogate(self, node: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Interrogate a node through all semantic lenses.

        Returns dict with R3, R7, R8 results.
        """
        return {
            "R3_CLASSIFICATION": self.lens_r3_classification(node),
            "R7_SEMANTICS": self.lens_r7_semantics(node),
            "R8_EPISTEMOLOGY": self.lens_r8_epistemology(node),
        }
