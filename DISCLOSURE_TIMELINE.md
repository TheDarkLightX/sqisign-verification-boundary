# Coordinated-disclosure timeline

- **11 August 2026:** Dana Edwards privately reported the two
  verification-boundary findings to the SQIsign team, identifying affected
  revision `dd133d7aca576c361a270c8e6434832535b42ecc`, the bounded matrix,
  candidate guards, and explicit cryptographic nonclaims.
- **11 August 2026:** A fresh clean-checkout replay established that public
  `main` resolved to the affected revision and reproduced the complete matrix.
- **12 August 2026:** Décio, responding for the SQIsign team, confirmed that
  equivalent fixes had been developed independently approximately one month
  earlier in their development tree.
- **12 August 2026:** The team reported reproducing the affected behavior by
  undoing its fix and clean behavior after restoring it; confirmed the exact
  detached-length contract; and authorized immediate publication.
- **12 August 2026:** A second public-remote check still resolved `main` to the
  affected revision. The public fixing commit was not yet available and is not
  claimed by this preprint.

The next version should replace the final item with the public fixing commit
and release identifier when they become available. Publication does not depend
on waiting for that update because the maintainers explicitly authorized
immediate disclosure.
