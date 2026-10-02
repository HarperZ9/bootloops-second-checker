# bootloops-second-checker

An independent second checker for BootLoops RECEIPT v1.0 witnesses, a Lean 4
kernel check of the same identity over `ZMod p`, and a replay of one published
numerical check. MIT licensed.

One witness certifies one reduction-table row at one (kinematic point, prime):

```
sum_i lam[i] * R_i  ==  e_t  -  sum_m c[m] * e_m      (mod p)
```

This repository asks whether that contract can be checked by code that shares
nothing with BootLoops' `core.py`, and whether the two checkers agree.

## Run everything

```sh
sh scripts/run_all.sh OUT_DIR
```

It clones BootLoops at the pinned commit, builds the witness corpus, runs the
three checkers side by side, runs the controls and the spec-edge probe,
replays the sunrise check, runs the Lean legs, and writes `OUT_DIR/SUMMARY.json`
with `OUT_DIR/SHA256SUMS`. `SKIP_LEAN=1` skips the Lean legs, which download
Mathlib (several GB).

## What is here

| path | what it does |
|---|---|
| `src/second_checker/checker.py` | clean-room Python checker, written from `WITNESS_FORMAT.md` only |
| `js/check.mjs` | a second clean-room checker in JavaScript with BigInt arithmetic |
| `src/second_checker/synth.py` | an independent witness generator (Gauss-Jordan with a tracked transform) |
| `src/second_checker/lean_emit.py` | writes each identity as Lean 4 theorems over `ZMod p` |
| `scripts/gen_corpus.py` | builds the witness corpus with BootLoops' own emitters and the generator above |
| `scripts/compare.py` | row-by-row verdicts from both clean-room checkers and `core.py` |
| `scripts/controls.py` | seeded corruptions, the wrong-table class, shuffle controls, dummy checkers |
| `scripts/edge_cases.py` | inputs where the spec is silent or the two readings differ |
| `scripts/lean_run.py` | kernel check of a sample, Lean negative controls, scale limits |
| `scripts/sunrise_quadrature.py` | a 30-digit Feynman-parameter check of one sunrise value |
| `REPORT.md` | results, disagreements and limits |
| `.provenance.log` | when the spec, the docs and `core.py` were first opened |

## Limits

A mod-p witness certifies one row at one point and one prime. This repository
says nothing about rational reconstruction, the analytic result, or the
physics. See `REPORT.md`, section "What this does not prove".
