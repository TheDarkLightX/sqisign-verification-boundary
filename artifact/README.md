# Public artifact notes

This directory is the public minimum evidence package for the bounded claims
in the preprint.

- `evidence/results/` contains aggregate JSON for every tested authority and
  experiment variant.
- `evidence/raw/` contains representative raw ASan stderr from both public
  verification paths.
- `evidence/command-transcript.log` is the complete successful fresh-replay
  transcript.
- `evidence/harness-material.tar` contains the historical harness, candidate
  patch, and workflow material. It does not contain SQIsign source.
- `evidence/ARTIFACTS.sha256` is the frozen full-replay manifest. It names some
  private-record files that are not redistributed; it is included to preserve
  provenance, not to imply that every named file is in this public subset.
- `lean/` contains exact frozen formal sources, source hashes, and the
  successful recompile log.
- `patch/` contains the locally evaluated candidate guards.

The SQIsign source must be obtained from upstream and checked out at
`dd133d7aca576c361a270c8e6434832535b42ecc`. It remains under the upstream
license. The root `SHA256SUMS` authenticates the two versioned release assets.
