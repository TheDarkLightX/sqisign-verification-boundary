# Verification length authority at revision dd133d7

Affected revision:
`dd133d7aca576c361a270c8e6434832535b42ecc`

## Summary

I found two related length-authority issues in the public SQIsign reference
implementation revision above:

1. The signed-message open path and detached verifier could reach fixed-size
   signature decoding before the supplied length established that the complete
   signature was present.
2. Detached verification accepted tested buffers consisting of a valid
   fixed-size signature plus one or sixteen additional declared bytes, although
   exact equality is the intended detached contract.

Across levels 1, 3, and 5 in the reference and Broadwell x86 builds, all 2,656
tested undersized calls produced AddressSanitizer findings at the affected
revision. All 1,200 tested detached suffix cases were accepted. A boundary
repair converted every tested undersized case to clean rejection, rejected all
tested suffix cases, and preserved all 600 exact KAT signatures.

## Intended contracts

- The signed-message path should reject only when
  `smlen < SIGNATURE_BYTES`; bytes after the fixed-size signature are the
  message.
- Detached verification should require
  `siglen == SIGNATURE_BYTES`.

## Maintainer coordination

The SQIsign team confirmed these contracts and reported that equivalent fixes
had been developed independently in its development tree before my report.
Prompted by the report, the team reproduced the affected behavior after
temporarily undoing its fix and obtained clean rejections without ASan findings
after restoring it. The team authorized immediate public disclosure and plans
to ship the fix with the Round 3 release.

## Scope

This is a reference-implementation memory-safety and API-boundary report. It is
not a signature forgery, key-recovery result, remote-code-execution claim,
deployment exploit, defect in the mathematical security proof, or by itself a
SUF-CMA break.

The complete replay packet, bounded claims, candidate patch, and preprint are
available in the accompanying research repository. I will update this issue
with the public fixing commit when it is available.

Thank you to Décio and the SQIsign team for their prompt confirmation,
independent reproduction, and disclosure guidance.
