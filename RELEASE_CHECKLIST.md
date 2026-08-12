# Public preprint release checklist

## Before tagging

- [ ] Review the final PDF as Dana Edwards.
- [ ] Run `python3 -B validate_packet.py`.
- [ ] Run `python3 -O -B validate_packet.py`.
- [ ] Run `sha256sum -c ARTIFACTS.sha256`.
- [ ] Confirm the public Git commit contains no private email, machine path,
      credential, cache, or build-only file.
- [ ] Confirm the public SQIsign issue text still matches the paper and
      maintainer authorization.

## Publish version 1.0.0

- [ ] Merge the reviewed publication pull request.
- [ ] Create annotated tag and GitHub release `v1.0.0`.
- [ ] Attach `manuscript.pdf`; retain GitHub's source archive.
- [ ] Deposit `manuscript.pdf` and the release source archive on Zenodo as a
      Publication / Preprint record.
- [ ] Add the minted Zenodo DOI to `CITATION.cff` and `README.md` in a metadata
      follow-up commit.
- [ ] Submit the PDF to IACR Cryptology ePrint under Implementation.
- [ ] Add the assigned ePrint number in a metadata follow-up commit.
- [ ] Open the prepared issue in `SQISign/the-sqisign` and link the public
      preprint and artifact.

The maintainer response authorizes immediate publication. Waiting for the
future public fixing commit is not a release prerequisite; add it later as a
versioned factual update.
