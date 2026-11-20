# How the alpo.ge Lean source states a proof of the Riemann hypothesis

An annotated map of the architecture of the Lean 4 source tree, published with L. Alpöge's note of 20 November 2026, that contains a theorem `riemannHypothesis : RiemannHypothesis` (Mathlib's proposition).

[Read the article (PDF)](https://github.com/cadamcat/riemann-hypothesis-exposition/releases/latest/download/riemann-hypothesis-exposition-article.pdf)

- Author: Yao Xu.
- Version: v1.0.0.
- Date: 20 November 2026.
- Readers: graduate students and research mathematicians. §1 is written for a general reader.

## What the article covers

1. What `Main.lean` exports, and the short classical reductions that bring all five exported theorems (RH, GRH for Dirichlet L-functions in three forms) down to one proposition: no Dirichlet L-function vanishes on Re s > 1/2.
2. The layer of "literature" statements at the top. The tree proves these statements itself; it does not assume them.
3. The analytic half. A weighted prime sum built from Σ Λ(n)(x/n − 1) − x log x + (1+γ)x, its explicit formula, and a Landau-type criterion that turns a one-sided square-root bound on sparse windows of scales into a zero-free half-plane.
4. The window bound. Length estimates for Ш¹ of the Tate twists Q_ℓ/Z_ℓ(−e) over fields cut out of cyclotomic fields.
5. The automorphic half. The tree states and proves three deep inputs:
   - Galois representations attached to polarized regular algebraic cuspidal representations over CM fields;
   - the local Langlands correspondence for GL_n;
   - global theta lifts between unitary groups in a stable range.

   For each input, the article says which published theorems it resembles.
6. How the two halves connect, with a dependency figure.
7. The twenty items of the author's note, set against the source.
8. Verification status.

## Status of each part

Every mathematical claim in the article carries one of four labels:

- **classical**: a published theorem or standard fact, with a citation.
- **Lean (file:line)**: the source contains a theorem or definition with this statement at this location. For theorems this means *stated and proved in the source, as written*. The kernel check of the tree had not finished when this version was written (see below).
- **remark**: the author's own description in the note.
- **interpretation**: our reading of a Lean statement, or of which published result it corresponds to. Declaration names are suggestive, but they are not evidence.

**This article does not assert that the Riemann hypothesis is proved.** It describes what the Lean source states and how the pieces fit together. Whether the source proves `RiemannHypothesis` from Lean's standard axioms is decided by a full build, an axiom audit and a kernel replay. Section 10 records what had been checked when this version was written. A later version will add those results.

## Quotations are generated, not typed

Every framed Lean statement in the article is extracted from the source by `tools/leanquotes.py`. The same script checks the article and fails, by name, when:

- a quotation differs from the source;
- a declaration name in the text does not exist;
- a cited `file:line` does not start a declaration;
- a citation key is undefined.

To reproduce:

1. Download the archive announced in the note and check it. Its parts are `lean.tar.gz.part01` to `part14`; the concatenated archive has SHA-256 `9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc`.
2. Unpack it so that the source is at `lean/src/` in this repository, or set `RH_SRC` to its location.
3. Run:

```bash
cd tools
python3 -I index.py ../lean/src out        # declaration index, a few seconds
python3 -I leanquotes.py check             # 0 failures expected
python3 -I edges.py build && python3 -I edges.py cone riemannHypothesis   # optional: cone estimate (Appendix A)
```

Nothing from the tree is compiled or run by these scripts; they read it as text.

Build the PDF with `cd article && latexmk -lualatex main.tex`.

## Sources and contributions

The mathematics and the Lean source are due to their authors: the note and the Lean archive by L. Alpöge, Mathlib by its contributors, and the classical results by the authors cited in the article.

This exposition is our own work and has not been peer reviewed. We contribute:
- the explanation;
- the map of the proof from `Main.lean` down six to seven levels;
- the status labels;
- the script-generated quotations and their check;
- the comparison of the note's twenty items with the source.

No new mathematics is claimed.

Prepared with the assistance of AI.

## Licence

The article text, figures and LaTeX source are licensed under CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`). The scripts in `tools/` are licensed under Apache-2.0 (`LICENSE-APACHE-2.0.txt`). The files in `article/quotes/` are short excerpts of the Lean source, quoted for commentary; they are not covered by these licences. The source archive itself is not redistributed here.
