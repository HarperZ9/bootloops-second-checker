<!-- writing-profile: research -->
# Verification report: an independent second checker for BootLoops RECEIPT v1.0

Run date 2026-10-02. Author: Zain Dana Harper, with Claude Code (Claude Opus 5.5)
writing and running the code. License: MIT for the code and this report, matching
BootLoops' contribution rules.

## Summary

- **Agreement.** A clean-room checker written from `WITNESS_FORMAT.md` alone, a
  second clean-room checker in JavaScript, and BootLoops' `core.py` returned the
  same verdict on **12,187 of 12,187** witnesses (23 corpora, two primes). Table
  mode also agreed on all 12,187. **Disagreements on the corpus: 0.**
- **Controls.** All **2,920 of 2,920** control cases scored as expected on every
  checker that applies: 2,653 corrupted or shuffled inputs rejected, and 267
  true-table positive controls passed. A dummy that accepts everything and a dummy
  that rejects everything both fail the same harness.
- **Spec-edge probe.** On 14 hand-built inputs, `sc-py` and `core.py` differ on
  10. Four findings are substantive for BootLoops. `core.py` accepts a
  non-integer coefficient by truncating it. It fails a correct table row when the
  witness carries an explicit zero coefficient. Its CLI exits 1, the FAIL code,
  on a valid witness whose file name starts with `c_`. And its CLI never checks a
  recorded system fingerprint. One more case is a genuine spec ambiguity.
- **Lean 4.** Each identity is stated over `ZMod p`, checked by the kernel and
  replayed with `leanchecker`. On a seeded sample of 46 corpus witnesses, **46 of
  46** passed in column form and **38 of 38** eligible rows passed in linear form.
  All 6 corrupted witnesses were rejected. Per-column `decide +kernel` passed at
  10,000 row terms (305 s) and timed out at 30,000. Every corpus witness has at
  most 6,372 terms.
- **Replay.** Schwartz's published sunrise evaluator reproduces the page's Checks
  table exactly: 111, 110 and 109 digits at t = -3, -9 and 12. This replays his
  check against his own stored reference values. A separate textbook quadrature
  agrees with the published t = -3 value to 32 digits.
- **Negative result on inputs.** BootLoops publishes **no witness files** and does
  not ship the banked wrong-table exhibit. Every witness checked here was emitted
  locally, by BootLoops' own emitters or by this repository's generator.

## 1. Inputs, pinned

| input | pin |
|---|---|
| BootLoops repository | `github.com/BootLoops-ai/bootloops` commit `66b680ce742e654cfe86da4f072a69061fe182b1` |
| `tools/trust/receipt/WITNESS_FORMAT.md` | sha256 `35acbf9671cb3a9103b230a6f4f7c448e474a4b090b120cdc6bfba719d83680a` |
| `tools/trust/receipt/core.py` | sha256 `901218fc4201113f8874075b491f96cefcad470062a720ac188a743737d78977`, byte-identical to `tools/winnow/ibplapper/receipt/core.py` |
| `tools/trust/receipt/receipt.py` | sha256 `15fcb3adf05d70ffbc1deb339f8958135ed7cfef6a960c62bfca6864b7ca62de` |
| `tools/trust/receipt/emitter.py` | sha256 `5724ab71d4f32a1b06a80bc4c9ae2787780ccc92cda891637922f31209e4bf3d` |
| `bootloops.ai/files/sunrise/sunrise-bundle.zip` | sha256 `609e7d82a4a01ac390d44a1f8ce9d2de695f1d84a40fd5f10233f3df00b86ee5`, fetched 2026-10-02; its own `MANIFEST.sha256` verified 19 of 19 files |
| `sunrise-evaluate.py` (also inside the bundle) | sha256 `149b83a3b73c8716c3abc84a33bc3156c2a1025565fd91a4f8fb65ad0442bb37` |
| Python | 3.12.10 with `mpmath 1.3.0`, `numpy 2.5.3`, `sympy 1.14.0`, `pytest 9.1.1` (`requirements.txt`) |
| Node.js | runs `js/check.mjs`, standard library only |
| Lean | v4.34.1 (commit `5045d005`), Mathlib tag `v4.34.1` at `d13f23b723b8a846827a245b89c10fc7d3f11612` (`lean/lake-manifest.json`) |
| Platform | Windows 11, x86_64. The CLI crash in section 4.3 was also reproduced on Ubuntu 24.04 (WSL, Python 3.12.3) |

Hashes of the inputs are in `inputs/`. The outputs of the reported run are in
`results/run-2026-10-02/`, hashed in its `SHA256SUMS`. Machine-local paths inside
error messages there were replaced with `<bootloops>`, `<repo>`, `<out>` or
`<path>` by `scripts/sanitize_results.py`, and the hashes cover the sanitized files.

**One command re-runs everything:**

```sh
sh scripts/run_all.sh OUT_DIR
```

It clones BootLoops at the pinned commit and stops on any hash mismatch.
`SKIP_LEAN=1` skips the Lean legs, which download Mathlib.

## 2. Independence of the second checker

`src/second_checker/checker.py` and `js/check.mjs` were written from
`WITNESS_FORMAT.md` only. One other source was read before they were finished:
the public page `bootloops.ai/tools/receipt.html`, for the system JSONL line
format, which the spec does not define ("one sparse row per line mapping an
integer column id to its value mod p").

Timeline, from `.provenance.log` and the git history:

| time (2026-10-02, PDT) | event |
|---|---|
| 01:02:13 | opened `WITNESS_FORMAT.md` |
| 01:04:22 | read the tool page for the JSONL row format |
| 01:09:51 | committed both clean-room checkers and their tests (`2b8d843`); `core.py` not yet opened |
| 01:09:57 | first opened `core.py`, `test_core.py` and `test_banked.py` |

Neither checker shares code with `core.py` or imports it. The harness in
`scripts/checkers.py` imports `core.py` only to call it as the comparison target.
One limit applies: both clean-room checkers were written in the same session by
the same model. They are not independent of each other the way two separate teams
would be. Section 4.3 shows they still differ from each other on three inputs.

## 3. Corpus and agreement

### 3.1 Why the corpus is emitted, not downloaded

The plan was to run the checker over every published witness. **None exist.**
A search of all seven public BootLoops repositories found witness code and
documentation, but no witness files and no published system snapshots. The search
covered file contents (`"receipt_version"`, `lambda-witness`) and file names
(`w_*.json`, `lam_*.npy`, `c_*.json`). The receipt, trust and winnow tool pages on
the site turned up none either. The archived exhibit store that `test_banked.py`
and Winnow's `test_sabotage.py` read (`RECEIPT_BANKED_ROOT`, `WINNOW_BANKED_ROOT`)
is marked "not shipped" in both files.

The corpus was therefore produced locally, by BootLoops' own code wherever it runs:

| producer | what it is | corpora | witnesses |
|---|---|---|---|
| `bl-receipt` | `tools/trust/receipt/emitter.py` (Wiedemann retrofit) | 5 | 859 |
| `bl-winnow-retrofit` | Winnow `eliminate(..., witnesses="retrofit")` | 6 | 3,776 |
| `bl-winnow-native` | Winnow `eliminate(..., witnesses="native")` | 6 | 3,776 |
| `sc-synth` | this repository's Gauss-Jordan generator | 6 | 3,776 |
| **total** | | **23** | **12,187** |

The systems are BootLoops' own three-row fixture from `test_core.py`, plus seeded
integer systems of 60, 400 and 1,500 integrals. Those have 8, 24 and 40 masters
and 15, 80 and 300 redundant rows, and each is reduced at p = 2147483647 and
p = 2147483629. The receipt emitter's direct path needs a square system (its
docstring says so), so it ran on variants without the redundant rows. Witnesses
carry 1 to 533 nonzero multipliers and 1 to 6,372 row terms. These are synthetic
systems, not IBP systems from a physics family. Section 7 states what that limits.
`results/run-2026-10-02/GEN_LOG.json` records every emitter status: all 12,187
targets came back `CERTIFIED`.

### 3.2 Results

| checker | PASS | FAIL | MALFORMED | crash |
|---|---|---|---|---|
| `core.py` (BootLoops) | 12,187 | 0 | 0 | 0 |
| `sc-py` (clean-room Python) | 12,187 | 0 | 0 | 0 |
| `sc-js` (clean-room JavaScript) | 12,187 | 0 | 0 | 0 |
| `core.py`, table mode, true tables | 12,187 | 0 | 0 | 0 |
| `sc-py`, table mode, true tables | 12,187 | 0 | 0 | 0 |

**Disagreements: 0 of 12,187.** Row-by-row verdicts are in
`results/run-2026-10-02/results/agreement.csv`.

**Timing.** Per-corpus medians with the witness files already in the OS cache:
0.06 to 0.24 ms per row for `sc-py`, 0.05 to 0.27 ms for `core.py`. Both exclude
loading the system file. The two Python checkers cost about the same per row, and
`sc-py` is about 10 percent slower on most corpora. The whole-run mean that
`agreement.json` reports for `sc-py` (5.1 ms) is an artifact: `compare.py` calls
`sc-py` first, so `sc-py` pays the cold first read of every witness file. The
JavaScript figure includes Node start-up for each batch of 200.

## 4. Controls

### 4.1 The banked wrong-table exhibit

**Not replayed, because it is not public.** Leg 3 of `test_banked.py` needs
`PAIR_RESULT.json`, `ORACLE_BLOCKS.json` and the staged `lbl3m2L_k2disp` Kira
system from the archive, and it skips when `RECEIPT_BANKED_ROOT` is unset. In its
place this report tests the exhibit's class as WITNESS_FORMAT.md defines it. A
witness that holds against the system is checked in table mode against a claimed
row that differs from the certified row. The wrong value carries the same integer
error at both primes, mirroring the exhibit's "2-prime CRT-consistent" property.
This rebuilds the class. It does not replay the banked bytes.

### 4.2 Seeded controls

Seed `20261002`, 12 witnesses sampled per corpus, fewer where a mutation does not
apply. A case scores correct when a mutant is rejected (FAIL or MALFORMED) or a
positive control passes.

| control | expected | cases | `core.py` | `sc-py` | `sc-js` |
|---|---|---|---|---|---|
| M1 one coefficient +1 mod p | reject | 267 | 267 | 267 | 267 |
| M2 one coefficient dropped | reject | 267 | 267 | 267 | 267 |
| M3 one extra coefficient | reject | 267 | 267 | 267 | 267 |
| M4 prime changed to the other prime | reject | 267 | 267 | 267 | 267 |
| M5 one lambda value +1 mod p | reject | 267 | 267 | 267 | 267 |
| M6 one lambda entry dropped | reject | 267 | 267 | 267 | 267 |
| M7 target column swapped | reject | 267 | 267 | 267 | 267 |
| M8 one value in a used system row altered | reject | 91 | 91 | 91 | 91 |
| N1 system rows shuffled, no used row left in place | reject | 267 | 267 | 267 | 267 |
| N2 lambda values permuted among indices | reject | 159 | 159 | 159 | 159 |
| X1 exhibit class: valid witness, wrong table row | reject | 267 | 267 | 267 | n/a |
| X0 exhibit control: valid witness, true table row | pass | 267 | 267 | 267 | n/a |
| **total** | | **2,920** | **2,920** | **2,920** | **2,386 of 2,386** |

The JavaScript checker has no table mode, so X0 and X1 do not apply to it.

**No-op control (N3).** Under the same scoring rule, a dummy that accepts
everything scores 267 of 2,920 and a dummy that rejects everything scores 2,653
of 2,920. The harness flags both as failing, so no checker can pass it by always
answering the same way.

### 4.3 Spec-edge probe, every disagreement

These inputs were built by hand on BootLoops' `test_core.py` fixture, target 202,
where the true row is `I_202 = 15 I_101 + 7 I_102`. None of them occurs in the
emitted corpus. They mark where the spec is silent, or where an implementation
departs from it.

| case | input | `sc-py` | `sc-js` | `core.py` | CLI rc | reading |
|---|---|---|---|---|---|---|
| E01 | `c` value `15.0` (JSON float) | MALFORMED | PASS | PASS | 0 | type strictness only; the value is right |
| E02 | `c` value `15.7` | MALFORMED | MALFORMED | **PASS** | 0 | **core truncates 15.7 to 15 and certifies a non-integer coefficient** |
| E03 | `c` value `true` | MALFORMED | MALFORMED | FAIL | 1 | both reject; core reads `true` as 1 |
| E04 | `receipt_version` as the number `1.0` | MALFORMED | MALFORMED | PASS | 0 | the schema shows a string; the field rules do not say |
| E05 | explicit zero `c` entry, table mode, true row | PASS | n/a | **FAIL** | 1 | **departs from rule 6**, which compares "after mod-p normalization and zero-dropping". Core keeps zeros in the witness `c`, drops them from the table row, and reports that "the TABLE is wrong" for a correct table |
| E06 | `c` entry equal to p, table mode, true row | PASS | n/a | **FAIL** | 1 | same cause as E05 |
| E07 | `c` contains the target column (`c[t]=5`), lambda scaled by 1-5 | PASS | PASS | FAIL | 1 | **spec ambiguity.** Rule 4 writes `{t: 1} + {m: -c[m]}`. Core overwrites the target entry; both clean-room checkers add. The witness is valid under the additive reading |
| E08 | keys `"101"` and `"0101"` in `c` | MALFORMED | PASS | PASS | 0 | core and sc-js keep the last value, so the verdict depends on key order |
| E09 | `lam.n_rows = -1`, empty lambda | MALFORMED | FAIL | FAIL | 1 | all reject |
| E10 | `lam.idx` entries as floats | MALFORMED | PASS | PASS | 0 | type strictness only |
| E11 | composite p = 15 | PASS | PASS | PASS | 0 | agree. No checker tests primality; the spec asks only for p > 1 |
| E12 | `p` as a string | PASS | PASS | PASS | 0 | agree |
| E13 | `system.fingerprint` replaced by 64 zeros | PASS | PASS | PASS | **0** | agree, but see below: **core's CLI never computes a fingerprint**, so a tampered fingerprint passes |
| E14 | valid v1 witness saved as `c_x.json` | PASS | PASS | PASS (library) | **1** | **the CLI sends any `c_*` file to the legacy reader.** On Linux it raises `KeyError: 'd0'`; on Windows it fails importing the Unix-only `resource` module. Either way an uncaught exception exits 1, the FAIL code, where the rc discipline calls for 2 |

`sc-py` and `core.py` differ on 10 of the 14 inputs (E01 to E10). Two of those
differ only in class, since both checkers reject (E03, E09). Four are type
strictness on inputs whose value is correct (E01, E04, E08, E10). The substantive
ones are E02, E05 and E06, plus the E07 ambiguity. The CLI-level findings E13 and
E14 do not show up as library-verdict disagreements. The two clean-room checkers
also differ from each other on E01, E08 and E10. JavaScript's JSON parser cannot
tell `15.0` from `15`, and the JavaScript checker does not reject duplicate key
aliases. Those differences are kept as found. The JavaScript checker was not
changed after `core.py` was read.

**Fingerprint.** Rule 2 makes the fingerprint check conditional ("when the
verifier computed its own"), and `receipt.py verify` calls `verify_many` without
one. The spec describes the fingerprint ("row order as given, columns sorted per
row, `p` prefixed") without fixing its bytes, so a clean-room implementation cannot
compute a matching value from the spec. `core.system_fingerprint` hashes the line
`p={p}`, then for each row the prefix `{i}:`, one `{col}={val % p};` per column in
sorted order, and a newline. Writing that layout into WITNESS_FORMAT.md would let a
second implementation enforce rule 2.

**Severity.** No witness written by BootLoops' own emitters is affected:
`write_witness` drops zeros, writes integers and names files `w_*`. The findings
matter for the format's stated purpose, a contract that any solver can write to.

## 5. Lean 4 kernel check

### 5.1 Statements

`src/second_checker/lean_emit.py` writes each witness in two forms over `ZMod p`:

- **Column form.** One equation per column in the union of the supports of
  `lam_i * R_i` and `e_t - sum c_m e_m`: `(sum_i lam_i * R_i[k] : ZMod p) = expect_k`.
  Each column is a lemma proved by `decide +kernel`, and the full conjunction is
  assembled from those lemmas. Trust boundary: the emitter enumerates the columns.
  A column outside that union is zero on both sides by construction, and the
  Python checkers confirm independently that the residual has no other columns.
- **Linear form.** `forall x : N -> ZMod p, sum_i lam_i * (sum_k R_i[k] * x k) = x t - sum_m c_m * x m`,
  proved by `ring_nf; reduce_mod_char` applied twice. This states the identity
  itself, with no column enumeration to trust.

No proof uses `sorry`, `native_decide` or `implemented_by`. Every module that
builds is replayed by `leanchecker` in a fresh process. Its `#print axioms`
output is checked against `{propext, Classical.choice, Quot.sound}`.

### 5.2 Corpus sample

Seed `20261002`, 2 witnesses per corpus, 46 witnesses in all. They range from 3
to 6,136 row terms (median 24), and 4 exceed 1,000 terms.

| leg | rows | result | axioms | `leanchecker` |
|---|---|---|---|---|
| column form, `decide +kernel` | 46 | **46 of 46 kernel-checked** | `propext`, `Quot.sound` | rc 0 on all 8 modules |
| linear form, rows of 100 terms or fewer | 38 | **38 of 38 kernel-checked** | `propext`, `Classical.choice`, `Quot.sound` | rc 0 on all 7 modules |
| negative: one coefficient flipped, column form | 3 | 3 of 3 rejected (`decide` proves the proposition false) | | |
| negative: one coefficient flipped, linear form | 3 | 3 of 3 rejected (unsolved goals) | | |

Time: the column form took 370 s of wall time over 8 modules of up to 6 rows, or
about 297 s after subtracting the 9.1 s Mathlib import per module. That is
**about 6.5 s per row on average**, dominated by the four rows above 1,000 terms;
the module holding the heaviest rows took 182 s. The linear form took about
**0.3 s per row** after the import. At these sizes, checking all 12,187 rows is
a matter of compute time, not of what the kernel can carry. This run checked the
sample only.

### 5.3 How far the kernel scales

Artificial valid witnesses with T row terms (10 columns per row, T/10 rows), one
module per (T, tactic), a 900 s limit, and 9.1 s for the Mathlib import alone.

| tactic and form | 10 | 100 | 300 | 1,000 | 3,000 | 10,000 | 30,000 |
|---|---|---|---|---|---|---|---|
| `decide +kernel`, one lemma per column | 9.1 s | 9.9 s | 10.9 s | 17.5 s | 48.3 s | 304.9 s | timeout |
| `decide`, one lemma per column | 19.7 s | 13.3 s | 14.5 s | 21.7 s | 55.4 s | 295.9 s | timeout |
| `norm_num <;> reduce_mod_char`, per column | 34.3 s | 10.4 s | 12.9 s | 19.2 s | 52.1 s | not run | not run |
| `decide +kernel`, one monolithic conjunction | 9.2 s | 9.7 s | 13.1 s | **fails** | | | |
| `norm_num` alone, per column | **fails** | | | | | | |
| linear form, `ring_nf; reduce_mod_char` | 11.0 s | 15.2 s | **timeout** | | | | |

Wall times include the import. The first build in a series can include file-cache
warm-up, which is why some 10-term figures exceed the 100-term ones.

Where each approach stops:

- **Monolithic `decide`** fails at 1,000 terms (199 conjuncts). Lean cannot
  synthesize the `Decidable` instance for a conjunction that large under default
  settings. One lemma per column removes this limit.
- **`norm_num` alone** fails on every row. It multiplies the numerals as integers
  and leaves goals such as `2441368740449552418 = 1` in `ZMod p`, because it does
  not reduce modulo the characteristic. Adding `reduce_mod_char` fixes it.
- **Per-column `decide +kernel` and `decide`** pass at 10,000 terms in about
  300 s and time out at 30,000. Time grows faster than linearly: about 6x from
  3,000 to 10,000 terms. Every corpus witness has at most 6,372 terms (median 18,
  90th percentile 5,869), so all of them fall below the largest size that passed.
- **The linear form** passes at 100 terms and times out at 300. It is the more
  faithful statement and the least scalable one.

`leanchecker` replay passed (rc 0) on every module that built. Each replay took
33 to 130 s, mostly spent loading the environment.

## 6. Replay of the published numerical check

The post says anyone can check a final answer "by running two scripts", but it
does not name them. The equal-mass sunrise page
(`bootloops.ai/diagrams/sunrise-equal-mass.html`) links an evaluator and a bundle,
and the bundle's index lists the evaluator and `sunrise-B34.py` as that page's
commands. This report replays that one result. **It is a replay of Schwartz's
check, not an independent derivation.** The oracle values are literals inside his
script, and the replay shows the script recomputes the closed form and matches
them, as the page states.

| command, run inside the bundle | result | page states |
|---|---|---|
| `sha256sum -c MANIFEST.sha256` | 19 of 19 OK | |
| `sunrise-evaluate.py --point -3 --point -9 --point 12` | 111, 110 and 109 digits of agreement with the stored oracle; every raising gate PASS; 2 min 5 s wall | 111, 110, 109 |
| `sunrise-B34.py --dps 60` | closed-form controls B0 to B2 at 74 to 75 digits; held-out gates B1 to B4 PASS (75 to 76 digits, capped at 60); precision-doubling gate PASS | |

Both scripts were read before they ran. They import only `mpmath`, `argparse` and
`time`, and make no network or subprocess calls.

**One outside sanity check.** `scripts/sunrise_quadrature.py` integrates the
standard two-dimensional Feynman-parameter form of the equal-mass sunrise,
`J = -integral over the simplex of 1/F` with `F = (x1x2 + x2x3 + x3x1) - t x1x2x3`
on `x1+x2+x3 = 1`, using `mpmath.quad` at 30 digits. At t = -3 it agrees with
the published value to **32.5 digits** (46.7 at 45-digit working precision),
which is the limit set by working precision. This is a textbook parametrization
at modest precision, not research-scale computation. It says nothing about
t = -9, t = 12 or higher orders in epsilon.

## 7. What this does NOT prove

- **A mod-p witness certifies one point and one prime.** A PASS says the claimed
  row lies in the row span of the given system at that (kinematic point, prime).
  It says nothing about other points, other primes, rational reconstruction, the
  symbolic table, the analytic result or the physics. The spec states this scope
  itself, and neither the checkers nor Lean widen it.
- **A witness does not certify the system.** If the system rows are wrong or
  incomplete, a valid witness still passes. That is the job of the `detect` layer,
  which this report does not test.
- **The corpus is synthetic.** No published witness or system exists, so every
  witness here was emitted locally over BootLoops' test fixture and seeded integer
  systems. Agreement on these 12,187 witnesses does not show agreement on a real
  IBP table, whose rows are larger and structured differently.
- **The banked exhibit was not replayed.** Only its class was rebuilt.
- **Lean covers a sample of 46 witnesses**, not the corpus. The column form trusts
  the emitter's column enumeration. The linear form does not, and it scales only to
  about 100 terms.
- **The replay re-runs Schwartz's own check against his own stored oracle** and
  inherits that check's assumptions. The quadrature agrees at one point to 32
  digits and is not a derivation.
- **The operator does no research-scale exact computation.** No multi-precision
  re-derivation of any BootLoops integral was attempted. BootLoops' exact,
  research-scale layer lies outside what this work tests.
- **Both clean-room checkers come from one author and one model.** They share no
  code with `core.py`, but they are not independent of each other.

## 8. Re-running a single leg

```sh
python scripts/gen_corpus.py BOOTLOOPS_ROOT OUT/corpus
python scripts/compare.py    BOOTLOOPS_ROOT OUT/corpus OUT/results
python scripts/controls.py   BOOTLOOPS_ROOT OUT/corpus OUT/results 20261002
python scripts/edge_cases.py BOOTLOOPS_ROOT OUT/corpus OUT/edge
python scripts/lean_run.py   OUT/corpus OUT/lean --per-corpus 2 --rows-per-module 6 --linear-max-terms 100
python scripts/lean_run.py   OUT/corpus OUT/lean_scale --only-scale
python scripts/summarize.py  OUT
```
