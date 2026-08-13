# SQIsign verification-boundary study

This repository is the public preprint and reproducibility artifact for a
bounded study of signature-length authority and representation canonicality in
[`SQISign/the-sqisign`](https://github.com/SQISign/the-sqisign) at revision
`dd133d7aca576c361a270c8e6434832535b42ecc`.

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
- `CLAIMS.md` maps each headline claim to evidence and its nearest nonclaim.
- `BLOCKER_DISPOSITIONS.md` records the publication-gate decisions.

The versioned PDF and evidence archive are attached to the
[`v0.1.0` release](https://github.com/TheDarkLightX/sqisign-verification-boundary/releases/tag/v0.1.0).
Verify them with `SHA256SUMS`.

## Reproduction

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
