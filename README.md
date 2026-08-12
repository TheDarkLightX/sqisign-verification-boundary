# SQIsign verification-boundary preprint and artifact

This standalone release accompanies Dana Edwards's preprint:

> **Length Authority and Representation Canonicality at an SQIsign
> Verification Boundary**

It studies the public SQIsign reference implementation at the exact revision

```text
SQISign/the-sqisign@dd133d7aca576c361a270c8e6434832535b42ecc
```

Across parameter levels 1, 3, and 5 under the reference and Broadwell x86
implementations, the bounded campaign recorded:

- AddressSanitizer findings for all 2,656 tested undersized calls before the
  tested boundary repair;
- acceptance of all 1,200 tested detached valid-signature-plus-suffix inputs;
- clean rejection of all tested undersized and suffix cases after the tested
  guards; and
- continued acceptance of all 600 exact KAT signatures after those guards.

The SQIsign team confirmed the intended API contracts, reported independently
developed equivalent checks in its development tree, reproduced the affected
behavior after removing those checks, reported clean behavior after restoring
them, and authorized immediate publication. The public fixing commit was not
available at this release's cutoff.

## Start here

- [`manuscript.pdf`](manuscript.pdf) — version 1.0 preprint.
- [`manuscript.tex`](manuscript.tex) and [`references.bib`](references.bib) —
  reproducible source.
- [`claims_evidence.json`](claims_evidence.json) — five headline claims with
  their nearest nonclaims.
- [`DISCLOSURE_TIMELINE.md`](DISCLOSURE_TIMELINE.md) and
  [`MAINTAINER_CONFIRMATION.md`](MAINTAINER_CONFIRMATION.md) — sanitized
  coordination record.
- [`PUBLIC_ISSUE_DRAFT.md`](PUBLIC_ISSUE_DRAFT.md) — concise public tracker
  report.
- [`research/h7_completion_2026_08_11/`](research/h7_completion_2026_08_11/) —
  full-matrix runner, complete case records, representative ASan logs, and
  exact Lean source/build receipts.

The nested replay packet preserves its original research-status README as
historical evidence. The present root README, disclosure record, and preprint
govern this public release.

## Validate the release

Required local tools are Python 3, `latexmk`, BibTeX, `pdfinfo`, and
`pdftotext`.

```text
python3 -B validate_packet.py
python3 -O -B validate_packet.py
sha256sum -c ARTIFACTS.sha256
```

The validator checks the complete manifest, claim boundaries, exact replay
receipt, deterministic PDF rebuild, PDF metadata, public-text privacy scan,
and maintainer-confirmation boundary.

## Reproduce the implementation matrix

Use a clean disposable checkout of the official SQIsign repository at the
pinned commit. The runner deliberately patches and builds that checkout.

```text
research/h7_completion_2026_08_11/run_full_matrix.sh \
  /path/to/clean/the-sqisign \
  /path/to/new/output
```

Do not point it at a checkout containing user work. The replay requires the
compiler, CMake, Git, Python, and the dependencies used by the official
SQIsign build.

## Scope

This is a bounded reference-implementation and representation-boundary study.
It does **not** demonstrate a signature forgery, key recovery, remote code
execution, deployment exploit, defect in the SQIsign security proof, or a
SUF-CMA break. The generic Lean theorems are not an end-to-end refinement of
production SQIsign serialization.

## Authorship and AI use

Dana Edwards is the sole author and takes responsibility for the work. OpenAI
Codex agents assisted with exploratory analysis, code and test generation,
evidence organization, and drafting. Their outputs were treated as untrusted
candidate material and checked against frozen source, replayable experiments,
and machine-checked proof artifacts. No AI system is an author.

## Publication

The public source and artifact repository is
[`TheDarkLightX/sqisign-verification-boundary`](https://github.com/TheDarkLightX/sqisign-verification-boundary).
`CITATION.cff` supplies citation metadata. No Zenodo DOI or IACR ePrint number
is inserted before the corresponding record exists.

The repository's original materials are MIT-licensed unless a file says
otherwise. Apache-2.0 applies to the identified SQIsign-derived patch material
and explicitly marked harnesses; see `LICENSES.md` and
`THIRD_PARTY_NOTICES.md`.
