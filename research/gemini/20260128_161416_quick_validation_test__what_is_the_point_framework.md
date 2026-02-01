# Research: Quick validation test: What is the POINT framework for defining APIs?

> **Date:** 2026-01-28 16:14:16
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:4aaa8b8652f86ef1fb1c9639323f4e0d3920b9376b191103314752e1a1e0096b`
> **Raw JSON:** `raw/20260128_161416_quick_validation_test__what_is_the_point_framework.json`

---

## Query

Quick validation test: What is the POINT framework for defining APIs?

---

## Response

Based on **Layer 1: Definitions** of the Standard Model of Code (specifically section 9.1), the **POINT framework** is a set of five criteria used to distinguish a true **API** from a standard function call or module interface.

It stands for:

*   **P — Purposeful**: Formal documentation exists.
*   **O — Oriented**: Follows an architectural style (REST, gRPC, GraphQL).
*   **I — Isolated**: Decoupled from implementation details.
*   **N — Negotiated**: Crosses a meaningful boundary (Team, Repo, Network, Deployment).
*   **T — Versioned**: Makes backward compatibility commitments.

**Formal Definition:**
`API(interface) = true ⟺ P ∧ O ∧ I ∧ N ∧ T`

This definition helps determine scale emergence: a function call (L3) is not an API, but a System interaction (L7) almost always is.

---

## Citations

_No citations provided_
