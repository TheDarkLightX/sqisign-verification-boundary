# Zenodo deposit metadata

Use a manual Zenodo deposit for the first version. A GitHub integration is
optional, not required.

## Record

- **Upload type:** Publication
- **Publication type:** Preprint
- **Title:** Length Authority and Representation Canonicality at an SQIsign
  Verification Boundary
- **Creator:** Dana Edwards
- **Publication date:** 2026-08-12
- **Version:** 1.0.0
- **Language:** English
- **License:** MIT, matching the public repository's current license
- **Related identifier:**
  `https://github.com/TheDarkLightX/sqisign-verification-boundary`
  (relation: is supplemented by this software/artifact repository)

## Description

This preprint studies signature-length authority and representation
canonicality at the public SQIsign verification boundary, pinned to revision
`dd133d7aca576c361a270c8e6434832535b42ecc`. Across parameter levels 1, 3,
and 5 under the reference and Broadwell x86 implementations, all 2,656 tested
undersized calls produced AddressSanitizer findings before a tested boundary
repair, and all 1,200 tested detached valid-signature-plus-suffix inputs were
accepted. The tested guards converted all undersized and suffix cases to clean
rejections while preserving all 600 exact KAT signatures. The artifact also
contains generic Lean theorems clarifying accepted normalization and the
simultaneous-sign quotient of an ordered x-only observable. SQIsign
maintainers confirmed the intended contracts, reported an independently
developed development-tree fix and reproduction, and authorized immediate
publication. The work does not claim a signature forgery, key recovery,
remote code execution, deployment exploitability, a SUF-CMA break, or a defect
in the mathematical security proof.

## Keywords

`SQIsign`; `post-quantum cryptography`; `implementation security`; `parser
safety`; `signature representation`; `AddressSanitizer`; `formal
verification`; `Lean`

## Files

Upload both:

1. `manuscript.pdf`; and
2. the source archive generated from GitHub release `v1.0.0`.

After Zenodo reserves or mints the DOI, add it to `CITATION.cff`, the root
`README.md`, and the preferred citation in the manuscript. Do not invent a DOI
before the record exists.
