structure IsLift {n d : ℕ} (B : Base (maximalRealSubfield E) E) (χX χW : Chr (maximalRealSubfield E) E)
    (mX mW : InfinitePlace (maximalRealSubfield E) → ℤ) (lam : InfinitePlace (maximalRealSubfield E) → DomWeight n)
    (U : Submodule ℂ (GlobalTheory.UnitaryBC.UA E n → ℂ)) (U' : Submodule ℂ (GlobalTheory.UnitaryBC.UA E d → ℂ)) : Prop where
  aut : GlobalTheory.UnitaryBC.IsAutRepU U'
  wt : ∀ w, ∃ lam' : DomWeight d, GlobalTheory.UnitaryBC.HasWeightAt U' (B.emb w).1 lam' ∧ IsLiftWt (lam w) (mX w) (mW w) lam'
  loc : ∀ (v : Pl (maximalRealSubfield E)) (t : E →ₐ[maximalRealSubfield E] Fv (maximalRealSubfield E) v) τ τ',
    CompAt U (splitPrime t) τ → CompAt U' (splitPrime t) τ' → LocPair t χX χW τ τ'
