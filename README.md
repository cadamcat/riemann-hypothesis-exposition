# How the alpo.ge Lean source states a proof of the Riemann hypothesis

An annotated map of the architecture of the Lean 4 source tree, published with L. Alpöge's note of 20 November 2026, that contains a theorem `riemannHypothesis : RiemannHypothesis` (Mathlib's proposition).

[Read the article (PDF)](https://github.com/cadamcat/riemann-hypothesis-exposition/releases/latest/download/riemann-hypothesis-exposition-article.pdf) · [Watch the film (4K, 8 min)](https://github.com/cadamcat/riemann-hypothesis-exposition/releases/download/v1.1.0/riemann-hypothesis-exposition-film-4k.mp4)

- Author: Yao Xu.
- Version: v1.1.0 (article and narrated film).
- Date: 21 November 2026.
- Readers: graduate students and research mathematicians. §1 is written for a general reader.

## What the article covers

1. What `Main.lean` exports, and the short classical reductions that bring all five exported theorems (RH, GRH for Dirichlet L-functions in three forms) down to one proposition: no Dirichlet L-function vanishes on Re s > 1/2 (except at s = 1 for principal characters).
2. How the fields of the "literature" structure at the top are supplied: the final construction fills them with declarations of the tree itself.
3. The analytic half. A weighted prime sum built from Σ Λ(n)(x/n − 1) − x log x + (1+γ)x, its explicit formula, and a Landau-type criterion that turns a one-sided square-root bound on sparse windows of scales into a zero-free half-plane.
4. The window bound. Length estimates for Ш¹ of the Tate twists Q_ℓ/Z_ℓ(−e) over fields cut out of cyclotomic fields.
5. The automorphic half. The source supplies declarations and proof bodies for three deep inputs:
   - statements on Galois representations attached to polarized regular algebraic cuspidal representations over CM fields;
   - a form of the local Langlands correspondence for GL_n;
   - global theta lifts between unitary groups in a stable range.

   For each input, the article says which published theorems it resembles.
6. How the two halves connect, with a dependency figure.
7. The twenty items of the author's note, set against the source.
8. Verification status.

## Status of each part

Every mathematical claim in the article carries one of four labels:

- **classical**: a published theorem or standard fact, with a citation.
- **Lean (file:line)**: identifies a location in the Lean source. Where the article discusses a proof body, the label refers to the body as written. Section 10 reports the kernel replay of the compiled modules.
- **remark**: the author's own description in the note.
- **interpretation**: our reading of a Lean statement, or of which published result it corresponds to. Declaration names are suggestive, but they are not evidence.

**Verification status (Section 10).** An independent verification record by A. Sutherland (MIT; https://math.mit.edu/~drew/grh/, as of 21 November 2026, 09:30 UTC) reports the following:
- all 175,187 modules compile;
- the five headline theorems use only `propext`, `Classical.choice` and `Quot.sound`;
- Lean's kernel replays every compiled module;
- the independent kernels nanoda and con-leche accept the full exported proof.

Some runs were still going at that time. So `riemannHypothesis : RiemannHypothesis` (Mathlib's definition) has been machine-checked by several independent checkers, as that record reports.

Two things remain for expert reading: the mathematical argument itself, and the agreement of Mathlib's definitions with the classical ones. The article does not call the proof refereed.

## The film

A narrated film of about 8 minutes follows the article's outline: primes and zeros, what the source states, the analytic half, the two halves of the proof, the author's idea, and where the check stands. It is attached to the release in 4K with burned-in subtitles. The subtitles and the narration text are in `film/`. The narration voice is synthesized with an OpenAI speech model.

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

The article text, figures, LaTeX source, film, subtitles and narration text are licensed under CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`). The scripts in `tools/` are licensed under Apache-2.0 (`LICENSE-APACHE-2.0.txt`). The files in `article/quotes/` are short excerpts of the Lean source, quoted for commentary; they are not covered by these licences. The source archive itself is not redistributed here.
