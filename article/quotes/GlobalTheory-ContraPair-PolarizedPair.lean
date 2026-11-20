structure PolarizedPair (π : CuspSub L a) (χ : HChar (maximalRealSubfield L)) : Prop where
  sign : ∀ v : InfinitePlace (maximalRealSubfield L), χ.locInf v (-1) = (-1) ^ a
  dual : DualIsConjBy π (GlobalTheory.GalOfCusp.compNorm L χ)
