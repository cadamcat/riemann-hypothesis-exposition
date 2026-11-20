def qzTw (D : LData F Ω l) (e : ℤ) :
    Representation ℤ_[l] (GS Ω (D.S : Set (HeightOneSpectrum (𝓞 F)))) (QZ l) :=
  scalRep (QZ l) (D.chi ^ (-e))
