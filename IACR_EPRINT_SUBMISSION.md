# IACR Cryptology ePrint submission metadata

- **Category:** Implementation
- **Title:** Length Authority and Representation Canonicality at an SQIsign
  Verification Boundary
- **Author:** Dana Edwards
- **Contact author:** Dana Edwards
- **Keywords:** SQIsign, post-quantum cryptography, implementation security,
  parser safety, signature representation, AddressSanitizer, Lean

## Abstract

We study signature-length authority and representation canonicality at the
public verification boundary of the SQIsign reference implementation at
revision `dd133d7aca576c361a270c8e6434832535b42ecc`. A fresh same-machine
replay covers parameter levels 1, 3, and 5 under the reference and Broadwell
x86 implementations. Across both public verification paths, all 2,656 tested
undersized inputs produced AddressSanitizer findings before a tested boundary
repair; the repair converted all tested cases to clean pre-decode rejections.
The detached verifier also accepted all 1,200 tested representations formed by
appending one or sixteen declared bytes to 600 valid fixed-size KAT
signatures. An exact-length guard rejected all such tested suffix aliases while
preserving all 600 exact KAT signatures. Generic Lean theorems identify the
structural canonicality boundary. Following private disclosure, SQIsign
maintainers confirmed the intended contracts, reported an independently
developed development-tree fix and reproduction, and authorized immediate
publication. These are bounded implementation and representation findings,
not a forgery, key recovery, remote-code-execution result, deployment exploit,
SUF-CMA break, or defect in the mathematical security proof.

## Submission notes

- Upload `manuscript.pdf` as the paper.
- Give the public GitHub repository as the implementation/artifact URL.
- Add the assigned ePrint number to `CITATION.cff` and `README.md` only after
  IACR assigns it.
