# Sanitized SQIsign maintainer confirmation

Received: 12 August 2026

Authority: written response from Décio on behalf of the SQIsign team, supplied
to the research project by Dana Edwards.

The team reported that:

1. approximately one month before Dana's report, a team member independently
   added a lower-bound check to the signed-message open path and an exact-length
   check to detached verification, both before signature decoding;
2. prompted by Dana's report, the team reproduced the affected behavior by
   undoing the development-tree fix;
3. after restoring the fix, the tested cases rejected cleanly without
   AddressSanitizer findings;
4. exact equality is the intended detached `siglen` contract;
5. the signed-message open path intentionally accepts
   `smlen >= SIGNATURE_BYTES`, because trailing bytes are the message;
6. comments and regression tests would be improved;
7. the fixes would ship in the Round 3 release; and
8. immediate publication, including a public GitHub issue, was authorized.

## Evidence boundary

This file is a sanitized summary, not the raw email. It omits private email
addresses and headers. The project did not receive the team's raw reproduction
logs or private development-tree commit. Accordingly, the paper describes this
as independent maintainer confirmation and reproduction, but not as a public
source-level verification of the fixing revision.

The correspondence also establishes that the team developed the fix before
the disclosure. The preprint therefore claims independent discovery and
artifact-backed characterization of the affected public revision, not priority
for the remediation.
