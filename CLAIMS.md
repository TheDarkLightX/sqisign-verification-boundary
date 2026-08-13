# Claim and evidence map

Authority: `SQISign/the-sqisign` revision
`dd133d7aca576c361a270c8e6434832535b42ecc`; x86 reference and Broadwell
implementations; parameter levels 1, 3, and 5.

| ID | Bounded claim | Public evidence | Nearest nonclaim |
|---|---|---|---|
| H7-LEN-001 | All 2,656 tested undersized calls produced ASan findings before clean pre-decode rejection. | `artifact/evidence/results/*length*-unpatched.json`, representative raw stderr, replay transcript, validation | No RCE, deployment exploitability, confidentiality loss, forgery, or key recovery is established. |
| H7-TRAIL-001 | All 1,200 tested detached suffix aliases were accepted at the pinned revision. | `artifact/evidence/results/*trailing*-unpatched.json`, validation | An API representation alias is not automatically a second signature in a fixed-length formal signature domain or a SUF-CMA break. |
| H7-REPAIR-001 | Candidate guards converted all 2,656 undersized cases to clean rejection, rejected all 1,200 suffix aliases, and preserved all 600 exact KAT signatures. | `artifact/evidence/results/*-repaired.json`, candidate patch, validation | The patch is not asserted to be source-identical to the private upstream fix or to eliminate every parser defect. |
| H7-FIELD-CANON-NEG-001 | All 2,400 tested field-encoding collision pairs were paired rejections. | `artifact/evidence/results/*canonicality*.json`, validation | This negative campaign is not a universal proof of canonical fixed-length serialization. |
| H7-CANON-STRUCTURAL-001 | Under the stated section law, accepted-fiber injectivity is equivalent to accepted bytes being normalization fixed points. | `artifact/lean/CanonicalNormalization.lean`, exact-source replay log | No production SQIsign decoder, verifier, or byte domain is instantiated. |
| H7-XONLY-QUOTIENT-001 | The ordered x-only observable has simultaneous-negation orbits as fibers under the formal theorem's assumptions. | `artifact/lean/XCoordinateFiber.lean`, `artifact/lean/XOnlyQuotient.lean`, exact-source replay log | The classical quotient theorem is not a production serialization-refinement or security theorem. |

The aggregate values are machine-readable in
`artifact/evidence/validation.json`. The root `SHA256SUMS` authenticates the
published release assets.
