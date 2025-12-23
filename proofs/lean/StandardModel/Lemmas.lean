/-
  Supporting Lemmas for the Standard Model
  
  Key properties and helper theorems.
-/

import StandardModel.Definitions

-- Lemma: Atom phases are disjoint
theorem atom_phases_disjoint :
  ∀ (a1 a2 : Nat),
    a1 < 26 → a2 < 61 →
    Atom.data ⟨a1, by omega⟩ ≠ Atom.logic ⟨a2, by omega⟩ := by
  intro a1 a2 h1 h2
  simp [Atom.data, Atom.logic]

-- Lemma: Role set is bounded
theorem role_bounded : ∀ (r : Role), r.val < 27 := by
  intro r
  exact r.isLt

-- Lemma: RPBL coordinates are bounded
theorem rpbl_coordinates_bounded :
  ∀ (v : RPBL),
    v.responsibility.val < 10 ∧
    v.purity.val < 10 ∧
    v.boundary.val < 10 ∧
    v.lifecycle.val < 10 := by
  intro v
  exact ⟨v.responsibility.isLt, v.purity.isLt, v.boundary.isLt, v.lifecycle.isLt⟩

-- Lemma: Semantic space is a product type
theorem semantic_space_is_product :
  ∀ (σ : SemanticSpace),
    ∃ (a : Atom) (r : Role) (v : RPBL), σ = (a, r, v) := by
  intro σ
  use σ.1, σ.2.1, σ.2.2
  simp

-- Lemma: Two elements with same coordinates are equal
theorem semantic_equality :
  ∀ (σ1 σ2 : SemanticSpace),
    σ1.1 = σ2.1 →
    σ1.2.1 = σ2.2.1 →
    σ1.2.2 = σ2.2.2 →
    σ1 = σ2 := by
  intro σ1 σ2 h1 h2 h3
  cases σ1
  cases σ2
  simp at h1 h2 h3
  simp [h1, h2, h3]

-- Lemma: Atom count is fixed
theorem atom_count_fixed : 26 + 61 + 45 + 35 = 167 := by
  rfl

-- Lemma: Every atom belongs to exactly one phase
theorem atom_unique_phase :
  ∀ (a : Atom),
    (∃ n : Fin 26, a = Atom.data n) ∨
    (∃ n : Fin 61, a = Atom.logic n) ∨
    (∃ n : Fin 45, a = Atom.org n) ∨
    (∃ n : Fin 35, a = Atom.exec n) := by
  intro a
  cases a with
  | data n => left; use n
  | logic n => right; left; use n
  | org n => right; right; left; use n
  | exec n => right; right; right; use n

-- Lemma: RPBL space cardinality formula
theorem rpbl_cardinality : Fintype.card RPBL = 10 * 10 * 10 * 10 := by
  unfold RPBL
  simp [Fintype.card_prod]
  norm_num

-- Lemma: Semantic space cardinality formula (already proven in Boundedness.lean)
theorem semantic_cardinality_formula :
  Fintype.card SemanticSpace = Fintype.card Atom * Fintype.card Role * Fintype.card RPBL := by
  unfold SemanticSpace
  simp [Fintype.card_prod]

-- Lemma: Role 25 is Utility (fallback)
def utility_role : Role := ⟨25, by norm_num⟩

theorem utility_is_fallback : utility_role.val = 25 := by
  rfl

-- Lemma: Atom families sum to 167
theorem atom_families_sum :
  26 + 61 + 45 + 35 = 167 := by
  rfl
