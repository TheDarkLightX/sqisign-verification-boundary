# H7 fresh reproduction packet

This packet reproduces the SQIsign length-authority and detached-suffix matrix
from a clean official checkout.  It is private research evidence, not a public
advisory or disclosure authorization.

The official authority checked on 2026-08-11 is:

```text
SQISign/the-sqisign@dd133d7aca576c361a270c8e6434832535b42ecc
```

At the time of the replay, the remote `main` branch resolved to that same
commit.  The generated receipt records the live remote resolution separately
from the local checkout identity.

## Run

Use a clean, disposable checkout of the official repository:

```text
research/h7_completion_2026_08_11/run_full_matrix.sh \
  /path/to/the-sqisign \
  research/h7_completion_2026_08_11/generated
```

The runner:

1. verifies the exact official commit and a clean worktree;
2. adds six bounded local harness targets;
3. builds reference and Broadwell ASan authorities for levels 1, 3, and 5;
4. tests every undersized length through both public verification APIs;
5. tests 100 KAT signatures per authority at exact length and with 1- and
   16-byte declared suffixes;
6. applies the candidate length guards and repeats the complete matrix;
7. preserves representative raw sanitizer/safe-return logs, toolchain data,
   per-authority JSON, and a fail-closed aggregate receipt.

The v2 validator binds all 196 generated artifacts other than its own receipt,
including complete per-case JSON/stdout, build and environment logs, the live
remote-main record, and 144 representative raw files.  It also binds the
runner, validator, C harnesses, CMake target patch, and candidate repair.  The
normal and `python3 -O` validator executions produce the same receipt.

The `lean/` subdirectory preserves the exact generic H7 formal sources at the
frozen research ref.  Its separate receipt records the pinned Lean/Mathlib
recompile and axiom audit; these theorems are not a refinement of production
SQIsign serialization.

The runner intentionally leaves its disposable official checkout modified by
the local target patch and candidate repair.  Do not point it at a working
checkout containing user changes.

## Evidence boundary

The replay can establish the current exact-revision behavior and candidate
repair closure in this machine's tested matrix.  It cannot establish remote
code execution, deployment exploitability, a forgery, the intended normative
meaning of detached `siglen`, upstream acceptance of the patch, independent
third-party reproduction, or responsible disclosure.
