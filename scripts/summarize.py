"""Collect every leg's output into OUT/SUMMARY.json and hash the verdict files.

    python scripts/summarize.py OUT_DIR
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys


def _load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lean_summary(rep):
    if rep is None:
        return None
    l1 = rep.get("L1", [])
    out = {
        "baseline_import_only_s": rep.get("baseline_import_only", {}).get("wall_s"),
        "sample_rows": len(rep.get("sample", [])),
        "L1_modules": [{k: m.get(k) for k in ("module", "form", "n_rows", "ok", "wall_s",
                                               "cumulative_ms", "axioms", "axioms_ok",
                                               "leanchecker_rc", "leanchecker_s")} for m in l1],
        "L1_rows_checked": {f: sum(m["n_rows"] for m in l1 if m["form"] == f and m["ok"]
                                   and m.get("leanchecker_rc") == 0 and m["axioms_ok"])
                            for f in {m["form"] for m in l1}},
        "L2_negative": [{k: m.get(k) for k in ("module", "form", "ok")} for m in rep.get("L2", [])],
        "L2_all_rejected": all(not m["ok"] for m in rep.get("L2", [])) if rep.get("L2") else None,
        "L3_scale": [{k: m.get(k) for k in ("tactic", "terms", "lam_nnz", "n_cols", "ok", "timeout",
                                             "wall_s", "cumulative_ms", "axioms_ok", "leanchecker_rc",
                                             "errors")} for m in rep.get("L3", [])],
    }
    return out


def main(out):
    s = {}
    agr = _load(os.path.join(out, "results", "agreement.json"))
    if agr:
        s["agreement"] = {k: v for k, v in agr.items() if k != "disagreements"}
        s["agreement"]["disagreements"] = agr["disagreements"]
    ctl = _load(os.path.join(out, "results", "controls.json"))
    if ctl:
        s["controls"] = {k: v for k, v in ctl.items() if k != "records"}
    s["edge_cases"] = _load(os.path.join(out, "edge", "edge_cases.json"))
    s["lean"] = lean_summary(_load(os.path.join(out, "lean", "lean.json")))
    s["lean_scale"] = lean_summary(_load(os.path.join(out, "lean_scale", "lean.json")))
    rep = os.path.join(out, "replay", "evaluate.out")
    if os.path.exists(rep):
        with open(rep, encoding="utf-8", errors="replace") as fh:
            txt = fh.read()
        s["replay_sunrise_digits"] = [int(x) for x in re.findall(r"oracle \(recomputed\) = (\d+) digits", txt)]
    files = []
    for sub in ("results", "edge", "lean", "lean_scale"):
        d = os.path.join(out, sub)
        if os.path.isdir(d):
            for name in sorted(os.listdir(d)):
                q = os.path.join(d, name)
                if os.path.isfile(q) and name.endswith((".json", ".csv")):
                    files.append(q)
    with open(os.path.join(out, "SHA256SUMS"), "w", encoding="utf-8", newline="\n") as fh:
        for q in files:
            fh.write(f"{_sha(q)}  {os.path.relpath(q, out).replace(os.sep, '/')}\n")
    with open(os.path.join(out, "SUMMARY.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(s, fh, indent=1, sort_keys=True)
    print(json.dumps({k: (v if k not in ("edge_cases",) else len(v or [])) for k, v in s.items()
                      if k not in ("lean", "lean_scale")}, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main(sys.argv[1])
