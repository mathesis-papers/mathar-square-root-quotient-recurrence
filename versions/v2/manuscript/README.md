# Mathar's recurrence and Barker's Hankel formulas

Haobo Ma (ChronoAI Pte Ltd, Singapore), followed by Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore).

The note gives explicit proofs of consequences of Mathar's inverse-root theorem and Cigler's determinant theorems. A rational three-parameter identity for `(u+v*x)/sqrt(1+c*x^2)` specializes to Mathar's three-term conjecture in OEIS A128057 for every integer `n >= 2`. The identity `R(n)+R(n-1)=(5*n-9)*F(n)` also derives it directly from Mathar's earlier four-term recurrence. A block determinant and monic orthogonal polynomials evaluate the Hankel transform, proving Barker's empirical generating functions in A128056 and A128053 as explicit consequences of Cigler's determinant evaluation. No priority claim is made. The note includes unsigned, binomial and shifted-Hankel formulas and corrections to related OEIS statements.

## Build

Use Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
```

Alternatively, with a standard LaTeX installation:

```sh
pdflatex -halt-on-error note.tex
pdflatex -halt-on-error note.tex
```

The bibliography is included in `note.tex`. No figures, external TeX inputs or bibliography database are needed.

## Exact checks

Python 3.10 or later, standard library only:

```sh
python3 verify.py
```

The JSON output is also supplied as `verification.json`. Arithmetic is integral or rational, with no floating-point tolerance. The checks cover eight symbolic polynomial identities (four parity factors and four recurrence-bridge coefficients), an independent normalized root/inverse construction through degree 128, the original recurrence for `2 <= n <= 512`, ten rational parameter cases and coefficient identities through degree 64. Six families of Hankel determinants are evaluated directly for every `0 <= n <= 24` (150 determinants). Rational generating functions are compared through degree 64. `source-data.json` gives the OEIS revision numbers, source URLs and coefficient prefixes used for the comparisons; the output distinguishes compared lengths from available prefix lengths.

Explicit corrections concern the odd-parity sign in A128053, the odd-length abelian-square count in A128014, the identification of the unshifted Hankel transform of A128014 in an A128017 comment, and two interleaved-triangle indices. The unsigned integral is stated with its required Cauchy principal value at index zero. The reciprocal sums of A128054 and A128055 also have written proofs.

## Mathematical coverage

The parameterized recurrence, Hankel formulas and corollaries have complete written proofs in the note. The declaration `D5.S1.Recurrence.Algebraic.MatharA128057ThreeTermRecurrence.result` in the following source states existence and uniqueness of the normalized square root of `1+4*x^2`, its normalized two-sided inverse, and the original A128057 recurrence for every natural `n >= 2`:

https://github.com/the-omega-institute/trureturing/blob/2f8421f6b90d37b4815b887f6c60987553831b20/D5/S1/Recurrence/Algebraic/MatharA128057ThreeTermRecurrence.lean

That declaration does not cover the parameterized family, Hankel results or other transform consequences. The finite arithmetic checks supplement the universal written arguments. The coverage table distinguishes previously recorded relations, proved conjectures, corrected statements and items outside the note's scope. The posing locators are A128057 revision 11, FORMULA (Mathar, December 2, 2014), A128056 revision 5 and A128053 revision 5, FORMULA (Barker, June 27, 2013).

## License

CC BY 4.0 (`cc-by-4.0`). The scientific sources are identified with their contributor attributions. Their independent rights remain with their respective holders.
