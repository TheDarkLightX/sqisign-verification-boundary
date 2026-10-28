# SQIsign verification-boundary study

This repository is the public preprint and reproducibility artifact for a
bounded study of signature-length authority and representation canonicality in
[`SQISign/the-sqisign`](https://github.com/SQISign/the-sqisign) at revision
`dd133d7aca576c361a270c8e6434832535b42ecc`.

## Current status (28 October 2026)

SQIsign Round 3 is released as tag `nist-v3`, at commit
[`6d017708db403bf83977fa70770fc4f7f9e9ff21`](https://github.com/SQISign/the-sqisign/tree/6d017708db403bf83977fa70770fc4f7f9e9ff21).
Its public source contains the pre-decoding signature-length guards. The
SQIsign team had developed equivalent private corrections independently before
receiving the original report.

In [upstream issue #23](https://github.com/SQISign/the-sqisign/issues/23),
[yui9696 reported independent validation](https://github.com/SQISign/the-sqisign/issues/23#issuecomment-5506722786):
300/300 valid detached signatures and 300/300 valid signed messages accepted,
4,200 negative cases rejected, and no findings in a smaller AddressSanitizer
run. [trancee subsequently documented equivalent length protections and
regression tests in an independent safe-Rust port](https://github.com/SQISign/the-sqisign/issues/23#issuecomment-6468164363).
These are third-party reports, not new test runs by the original author.

The [Round 3 follow-up addendum, v0.2.0](addenda/round-3-validation-v0.2.0.md)
records the exact revisions, guard semantics, test scope, attribution, and
reproducibility sources. The original `v0.1.0` publication, evidence, and
[publication receipt](artifact/PUBLICATION_RECEIPT.json) retain the August
2026 observations and disclosure state; the receipt's planned-release wording
is historical.

## Original disclosure (12 August 2026)

The SQIsign team independently reproduced both reported boundary conditions,
said equivalent guards were already present in its private development tree,
confirmed that exact length is the intended detached-signature contract, and
authorized immediate public disclosure on 12 August 2026. The private tree was
not supplied or audited. Public `main` still resolved to the studied revision
when rechecked on 12 August 2026.

## Results at the studied revision

| Experiment | Pinned result | Candidate-repair result |
|---|---:|---:|
| Undersized calls across two APIs, levels 1/3/5, ref/Broadwell | 2,656/2,656 ASan findings | 2,656/2,656 clean rejections |
| Exact KAT signatures | 600/600 accepted | 600/600 accepted |
| Detached signatures with 1- or 16-byte declared suffixes | 1,200/1,200 accepted | 1,200/1,200 rejected |
| Field-encoding collision pairs | 0/2,400 paired accepts; 2,400/2,400 paired rejects | not applicable |

These are bounded implementation and representation findings. They are not a
signature forgery, key recovery, remote-code-execution result, named-deployment
exploit, flaw in the SQIsign security proof, SUF-CMA result, or proof that all
fixed-length encodings are noncanonical.

## Package map

- [`preprint/sqisign-verification-boundary-preprint-v0.1.0.pdf`](preprint/sqisign-verification-boundary-preprint-v0.1.0.pdf)
  is the ready-to-read preprint.
- `artifact/evidence/` contains aggregate validation, per-authority JSON,
  representative raw sanitizer output, the complete successful replay
  transcript, and frozen harness material.
- `artifact/patch/` contains the independently developed candidate guards.
- `artifact/lean/` contains the frozen generic Lean theorems and replay log.
- `CLAIMS.md` maps each original v0.1.0 headline claim to evidence and its
  nearest nonclaim.
- `BLOCKER_DISPOSITIONS.md` records the publication-gate decisions.

The versioned PDF and evidence archive are attached to the
[`v0.1.0` release](https://github.com/TheDarkLightX/sqisign-verification-boundary/releases/tag/v0.1.0).
Verify them with `SHA256SUMS`.

## Reproduction of v0.1.0

The evidence archive does not redistribute the SQIsign source. Obtain the
upstream repository, check out the exact 40-hex revision above, inspect the
commands in `artifact/evidence/command-transcript.log`, and use the preserved
harness bundle in `artifact/evidence/harness-material.tar`. The public package
is a reviewable record of the completed replay; it is not a one-command build
system for every platform.

## Licensing

Original material in this repository is provided under the MIT license. The
SQIsign source is referenced by immutable revision and remains under its
upstream license. No upstream source snapshot is bundled here.
