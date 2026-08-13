# Suggested title

Verification length checks occur after fixed-size decoding at `dd133d7`

# Issue body

We privately reported two verification-boundary findings affecting public
revision `dd133d7aca576c361a270c8e6434832535b42ecc`. Thank you to Décio and the
SQIsign team for the prompt response, independent reproduction, contract
clarification, and permission to publish this issue.

The team told us that equivalent checks had already been added independently
to its private development tree before our report, and that the fix is planned
for the Round 3 release. We did not audit that private source; “equivalent”
refers to the reported guard semantics, not source identity.

## Bounded results

1. Across parameter levels 1, 3, and 5, reference and Broadwell builds, and
   both `crypto_sign_open` and `sqisign_verify`, all 2,656 tested undersized
   calls reached fixed-size decoding and produced AddressSanitizer findings.
   Candidate pre-decode guards converted all 2,656 cases to clean rejections.
2. `sqisign_verify` accepted all 1,200 tested representations made by appending
   one or sixteen declared bytes to 600 valid fixed-size KAT signatures. An
   exact-length guard rejected all 1,200 while preserving all 600 exact KAT
   signatures. The team confirmed exact length is the intended detached API
   contract; larger `smlen` in `crypto_sign_open` is valid because the trailing
   bytes are the message.

Preprint and reproducibility artifact:
https://github.com/TheDarkLightX/sqisign-verification-boundary/releases/tag/v0.1.0

This is a bounded implementation/API representation report. It does not claim
a forgery, key recovery, remote code execution, a named deployment exploit, a
defect in SQIsign's mathematical security proof, or a SUF-CMA break.
