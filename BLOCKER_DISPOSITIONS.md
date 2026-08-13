# Publication blocker dispositions

Decision date: 12 August 2026. Publication target: a versioned research
artifact, public preprint, and upstream GitHub issue. This is not a claim of
peer review or venue acceptance.

## External disclosure

- **Author approval - resolved.** Dana Edwards explicitly approved publication
  and authorized this agent to publish on her behalf.
- **Maintainer process - resolved.** The report was sent privately. Décio Luiz
  Gazzoni Filho replied for the SQIsign team that the project has no separate
  disclosure policy and explicitly authorized immediate publication, including
  a public issue in the official repository.
- **Embargo and timing - resolved.** The team authorized immediate publication
  and said its private fix would ship in the Round 3 release.
- **Standards-body notification - not required for this release.** The claims
  concern the studied reference implementation and its C API boundary. No
  standards-body claim or contact is made.

## Scientific evidence

- **Exact-source reproduction and raw evidence - resolved.** A fresh isolated
  replay used the pinned revision, preserved the successful transcript,
  per-authority JSON, representative ASan stderr, harness material, validation,
  and hashes.
- **Twelve original workflow archives - resolved in the private research
  record.** They were reacquired and reauthenticated. They are not needed for
  the public minimum artifact, which includes the fresh replay outputs and
  frozen full-manifest record.
- **Independent reproduction - resolved.** The SQIsign team reported that it
  reproduced the findings by removing its independently developed checks and
  obtained clean rejections after restoring them. Its raw logs were not
  supplied, which is stated as a limitation.
- **Current upstream - resolved.** Public `main` was rechecked on 12 August 2026
  and still resolved to the pinned revision. The preprint makes no later-state
  claim.
- **Detached-length contract - resolved.** The team confirmed that exact
  signature length is the intended detached contract; longer `smlen` in the
  signed-message API carries the message after the fixed-size signature.
- **Other C boundaries - scoped out.** Null pointers, oversized containers,
  integer overflow, output buffers, and public-key lengths are not generalized
  from this experiment. The preprint claims closure only over the tested
  matrix.
- **Backend scope - resolved by claim boundary.** Results are limited to x86
  reference and Broadwell implementations at levels 1, 3, and 5.
- **Guard behavior - resolved for publication scope.** The maintainers confirmed
  the contract and independently tested equivalent guard semantics. Their
  private source was not audited, and the local patch is labeled a candidate.

## Formal, mathematical, and venue matters

- **Frozen Lean sources - resolved.** Exact frozen sources were recompiled with
  Lean 4.19.0 and the recorded Mathlib revision; the log and source hashes are
  public.
- **Statement review - resolved for bounded use.** Exceptional points, ordered
  roles, partial decoding, and simultaneous sign are reflected in the theorem
  statements; no production refinement is claimed.
- **Production verification claim - excluded.** The release does not say
  production SQIsign serialization is formally verified.
- **Prior art and novelty - resolved by framing.** The x-line quotient geometry
  is described as classical and cited; novelty is not claimed for it.
- **Venue adaptation - not applicable.** This is a public preprint and artifact,
  not a venue submission. Venue-specific class, anonymity, AI, artifact, and
  ethics checks remain future work before any submission.
- **Bibliography and AI disclosure - resolved for this artifact.** Primary
  implementation/specification/paper and sanitizer references are included,
  and the preprint gives an accurate AI-assistance statement.
- **Internal banner - resolved.** Dana's explicit publication authorization and
  the maintainer's immediate-disclosure authorization satisfy the removal gate.

The excluded claims in `README.md`, `CLAIMS.md`, and the preprint remain in
force.
