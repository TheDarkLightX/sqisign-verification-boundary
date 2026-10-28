# SQIsign verification-boundary study: Round 3 follow-up

Document version: **v0.2.0 (addendum)**. Date: **28 October 2026**.
Supplements the [v0.1.0 publication of 12 August 2026][original-release].

SQIsign Round 3, tag [`nist-v3`][round3-tag], at commit
[`6d017708db403bf83977fa70770fc4f7f9e9ff21`][round3-tree], contains the required
pre-decoding signature-length guards. This addendum records the public source
and subsequent independent reports. It adds no runtime measurements by the
original author and leaves the original publication and evidence unchanged.

## Original observations and correction attribution

The August study by Dana Edwards (`TheDarkLightX`) documented two implementation
boundary problems at [`dd133d7aca576c361a270c8e6434832535b42ecc`][original-source]:
undersized inputs reached fixed-size signature decoding through the detached
and signed-message APIs, and overlong detached signatures were accepted despite
the intended exact-length contract. Its measurements and locally evaluated
candidate repair remain in [v0.1.0][original-release].

As recorded in [official issue #23][issue] and the [original publication
receipt][original-receipt], the SQIsign team independently reproduced the
conditions and had already developed equivalent guards in its private tree
**before receiving the report**. The team authorized disclosure on 12 August
2026. That private source was not supplied or audited; equivalence describes
guard behavior, not source identity. The later public release does not change
that attribution or imply that the report originated the team's corrections.

## Released C guards

At the pinned Round 3 revision, [`src/sqisign.c`][round3-source] implements:

| Entry point | Check before decoding | Failure behavior |
|---|---|---|
| `sqisign_verify` | `siglen != SIGNATURE_BYTES` | Return `-1` for either a short or an overlong detached signature. |
| `sqisign_open` | `smlen < SIGNATURE_BYTES` | Set `*mlen = 0` and return `-1` for an undersized signed message. |

Both guards precede `public_key_from_bytes` and `signature_from_bytes`; the
`open` guard also precedes subtracting `SIGNATURE_BYTES` from `smlen`. The
[NIST API wrappers][round3-api] delegate to these functions. `open` permits
`smlen >= SIGNATURE_BYTES`: bytes after the signature are the message. Appending
bytes changes that message and requires a valid signature for the changed
message; it is not a detached-signature suffix alias.

## Independent C validation reported by yui9696

[yui9696's report][c-report] identifies `6d01770` / `nist-v3`, macOS 26.1 on
Apple Silicon, `SQISIGN_BUILD_TYPE=ref`, and `CMAKE_BUILD_TYPE=Release`.
It exercises `crypto_sign_verify` and `crypto_sign_open` with 100 shipped KAT
vectors per parameter set, across all three sets. The following are the
tester's reported results, not tests executed for this addendum:

| Case | Reported outcome |
|---|---:|
| Valid detached KAT signatures | 300/300 accepted |
| Valid signed messages | 300/300 accepted |
| Detached buffers and declared lengths shortened by 1, 2, 16, or 64 bytes | 1,200/1,200 rejected |
| Detached declared lengths increased by 1 or 16 bytes beyond the buffer | 600/600 rejected |
| Detached buffers and declared lengths both extended by 1 or 16 bytes | 600/600 rejected |
| Undersized signed-message inputs, using deficits of 1, 2, 16, or 64 bytes | 1,200/1,200 rejected |
| Signed messages extended by 1 or 16 bytes, changing the message | 600/600 rejected |

The five negative categories total **4,200 rejections**. The last row concerns
altered messages; it does not establish an exact-length requirement for `open`.

The tester also reports **zero AddressSanitizer findings** for the same case
set over 10 vectors per parameter set with `CMAKE_BUILD_TYPE=ASAN` and precisely
sized heap buffers. In a control build with only the `sqisign_verify` guard
disabled, a signature 16 bytes short triggered an ASan heap-buffer-overflow
during `signature_from_bytes` (a 16-byte read, `p324_3`). This control supports
the guard's causal role for that tested case. The smaller ASan campaign is
separate from the Release-build counts above.

## Independent safe-Rust implementation

[trancee's follow-up][rust-report] documents an independently developed
safe-Rust port at commit
[`c52ab76c7d4e336572f8364d3e1d672c4a04f5c6`][rust-tree]. Its
[`Signature::decode` and `PublicKey::decode`][rust-encode] return `None` unless
the input slice has exactly the corresponding encoded size, before parsing
fields. Its [`open`][rust-open] uses a checked split at the signature size and
verifies the remaining bytes as the message.

The [`wrong_lengths_are_rejected` regression test][rust-tests] covers every
shorter signature length, one- and sixteen-byte signature extensions, key
lengths of zero / one byte short / one byte long, successful opening of a valid
signed message, and rejection below the signature-size boundary. The suite is
instantiated for `p324_3`, `p500_27`, and `p664_17` (levels 1, 3, and 5).
This is separate implementation evidence; its tests were inspected, not run
for this addendum. The port's [README][rust-readme] describes it as work in
progress awaiting review.

## Reproducibility sources and limits

- **Original study:** the [v0.1.0 release][original-release], frozen
  [command transcript][original-transcript], [harness bundle][original-harness],
  and [SHA256SUMS][original-sums] preserve the August replay and asset hashes.
  Those results apply to `dd133d7` and its candidate repair.
- **Round 3 C:** use the pinned [source tree][round3-tree], [build
  instructions][round3-build], [KAT inputs][round3-kats], and [tester's
  report][c-report]. The comment supplies the setup, counts, ASan summary, and
  control excerpt, but no standalone harness or complete raw run log. This
  addendum checks source and reference consistency; it does not claim an
  independent replay of those measurements. When adapting the historical
  harness, note the Round 3 `crypto_sign_verify` order
  `(sig, siglen, m, mlen, pk)` in the [wrapper][round3-api]; the tester reports
  that it changed from `(m, mlen, sig, siglen, pk)`.
- **Rust:** the pinned [test source][rust-tests] and [build/test
  instructions][rust-readme] provide the independently maintained regression
  material. Its results must not be pooled with the C campaign's counts.

These are bounded implementation/API length findings and corrections. Neither
the original report nor this follow-up establishes a mathematical weakness in
SQIsign, a signature forgery, key recovery, a SUF-CMA break, or universal parser
safety. The C tester's adjacent field-decoding observation is outside this
length-guard addendum and is not promoted to a new finding here.

[original-release]: https://github.com/TheDarkLightX/sqisign-verification-boundary/releases/tag/v0.1.0
[original-source]: https://github.com/SQISign/the-sqisign/blob/dd133d7aca576c361a270c8e6434832535b42ecc/src/sqisign.c
[original-receipt]: https://github.com/TheDarkLightX/sqisign-verification-boundary/blob/v0.1.0/artifact/PUBLICATION_RECEIPT.json
[original-transcript]: https://github.com/TheDarkLightX/sqisign-verification-boundary/blob/v0.1.0/artifact/evidence/command-transcript.log
[original-harness]: https://github.com/TheDarkLightX/sqisign-verification-boundary/blob/v0.1.0/artifact/evidence/harness-material.tar
[original-sums]: https://github.com/TheDarkLightX/sqisign-verification-boundary/blob/v0.1.0/SHA256SUMS
[issue]: https://github.com/SQISign/the-sqisign/issues/23
[round3-tag]: https://github.com/SQISign/the-sqisign/tree/nist-v3
[round3-tree]: https://github.com/SQISign/the-sqisign/tree/6d017708db403bf83977fa70770fc4f7f9e9ff21
[round3-source]: https://github.com/SQISign/the-sqisign/blob/6d017708db403bf83977fa70770fc4f7f9e9ff21/src/sqisign.c#L80-L133
[round3-api]: https://github.com/SQISign/the-sqisign/blob/6d017708db403bf83977fa70770fc4f7f9e9ff21/src/nistapi/api.c#L45-L65
[round3-build]: https://github.com/SQISign/the-sqisign/blob/6d017708db403bf83977fa70770fc4f7f9e9ff21/README.md#build
[round3-kats]: https://github.com/SQISign/the-sqisign/tree/6d017708db403bf83977fa70770fc4f7f9e9ff21/KAT
[c-report]: https://github.com/SQISign/the-sqisign/issues/23#issuecomment-5506722786
[rust-report]: https://github.com/SQISign/the-sqisign/issues/23#issuecomment-6468164363
[rust-tree]: https://github.com/trancee/the-sqisign/tree/c52ab76c7d4e336572f8364d3e1d672c4a04f5c6
[rust-encode]: https://github.com/trancee/the-sqisign/blob/c52ab76c7d4e336572f8364d3e1d672c4a04f5c6/rust/crates/sqisign/src/verify/encode.rs#L43-L93
[rust-open]: https://github.com/trancee/the-sqisign/blob/c52ab76c7d4e336572f8364d3e1d672c4a04f5c6/rust/crates/sqisign/src/verify/mod.rs#L76-L88
[rust-tests]: https://github.com/trancee/the-sqisign/blob/c52ab76c7d4e336572f8364d3e1d672c4a04f5c6/rust/crates/sqisign/tests/verify_reject.rs#L88-L118
[rust-readme]: https://github.com/trancee/the-sqisign/blob/c52ab76c7d4e336572f8364d3e1d672c4a04f5c6/rust/README.md#build-and-test
