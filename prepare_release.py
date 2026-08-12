#!/usr/bin/env python3
"""Build the deterministic PDF and refresh the H7 receipt and manifest."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_DATE_EPOCH = 1786536000
CORE = [
    ".gitignore",
    "CITATION.cff",
    "DISCLOSURE_TIMELINE.md",
    "IACR_EPRINT_SUBMISSION.md",
    "LICENSE",
    "LICENSE-APACHE",
    "LICENSES.md",
    "MAINTAINER_CONFIRMATION.md",
    "PUBLIC_ISSUE_DRAFT.md",
    "PUBLIC_MAIN_2026_08_12.txt",
    "README.md",
    "RELEASE_CHECKLIST.md",
    "THIRD_PARTY_NOTICES.md",
    "ZENODO_DEPOSIT.md",
    "claims_evidence.json",
    "manuscript.pdf",
    "manuscript.tex",
    "prepare_release.py",
    "references.bib",
    "validate_packet.py",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    require(result.returncode == 0,
            f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")
    return result.stdout


def payload_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for directory, directories, names in os.walk(ROOT, followlinks=False):
        here = Path(directory)
        directories[:] = [name for name in directories if name != ".git"]
        for name in names:
            path = here / name
            relative = path.relative_to(ROOT).as_posix()
            if relative == "ARTIFACTS.sha256" or relative.startswith(".git/"):
                continue
            require(path.is_file() and not path.is_symlink(), f"invalid payload: {relative}")
            files[relative] = path
    return files


def main() -> int:
    for name in CORE:
        if name != "manuscript.pdf":
            require((ROOT / name).is_file(), f"missing core file: {name}")

    environment = os.environ.copy()
    environment.update({
        "SOURCE_DATE_EPOCH": str(SOURCE_DATE_EPOCH),
        "FORCE_SOURCE_DATE": "1",
        "TZ": "UTC",
    })
    with tempfile.TemporaryDirectory(prefix="h7-release-build-") as directory:
        target = Path(directory)
        shutil.copy2(ROOT / "manuscript.tex", target / "manuscript.tex")
        shutil.copy2(ROOT / "references.bib", target / "references.bib")
        run(["latexmk", "-pdf", "-bibtex", "-interaction=nonstopmode",
             "-halt-on-error", "manuscript.tex"], target, environment)
        log = (target / "manuscript.log").read_text(errors="replace")
        for forbidden in ("LaTeX Warning", "Overfull \\hbox", "Overfull \\vbox",
                          "undefined references", "undefined citations", "Fatal error"):
            require(forbidden not in log, f"build log contains: {forbidden}")
        atomic_write(ROOT / "manuscript.pdf", (target / "manuscript.pdf").read_bytes())

    info = run(["pdfinfo", "manuscript.pdf"], ROOT)
    page_match = re.search(r"^Pages:\s+(\d+)$", info, re.M)
    require(page_match is not None, "PDF page count unavailable")

    fresh_path = ROOT / "research/h7_completion_2026_08_11/generated/validation_receipt.json"
    lean_path = ROOT / "research/h7_completion_2026_08_11/lean/validation_receipt.json"
    fresh = json.loads(fresh_path.read_text())
    require(fresh["status"] == "PASS_FRESH_CURRENT_EXACT_REVISION_REPLAY",
            "fresh replay receipt")

    core_hashes = {name: sha256(ROOT / name) for name in CORE}
    receipt = {
        "schema": "isogeny-crypto/h7-public-preprint-receipt/v2",
        "status": "PASS_PUBLIC_PREPRINT_PACKET",
        "validated_on": "2026-08-12",
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "author": "Dana Edwards",
        "ai_is_author": False,
        "responsible_disclosure_completed": True,
        "publication_authorized": True,
        "public_fix_commit_available_at_cutoff": False,
        "public_main_revision_at_cutoff":
            "dd133d7aca576c361a270c8e6434832535b42ecc",
        "fresh_matrix_receipt_sha256": sha256(fresh_path),
        "original_fresh_matrix_receipt_sha256": sha256(
            ROOT / "research/h7_completion_2026_08_11/ORIGINAL_VALIDATION_RECEIPT.json"
        ),
        "lean_receipt_sha256": sha256(lean_path),
        "implementation_replay": {
            "unpatched_undersized_calls": 2656,
            "unpatched_asan_findings": 2656,
            "unpatched_overlong_acceptances": 1200,
            "repaired_safe_rejections": 2656,
            "repaired_overlong_rejections": 1200,
            "exact_kat_acceptances_before": 600,
            "exact_kat_acceptances_after": 600,
        },
        "maintainer_confirmation": {
            "independent_prior_fix_reported": True,
            "independent_reproduction_reported": True,
            "intended_contracts_confirmed": True,
            "immediate_publication_authorized": True,
            "raw_maintainer_logs_available": False,
            "raw_email_published": False,
        },
        "pdf_pages": int(page_match.group(1)),
        "pdf_sha256": sha256(ROOT / "manuscript.pdf"),
        "source_sha256": core_hashes,
        "limitations": [
            "not peer reviewed",
            "maintainer raw logs and private development-tree source were not supplied",
            "the public fixing commit was unavailable at the cutoff",
            "the generic Lean theorems are not a formal refinement of production SQIsign serialization",
            "no forgery, key recovery, remote code execution, deployment exploitability, or mathematical-security-proof defect is claimed",
        ],
    }
    atomic_write(
        ROOT / "validation_receipt.json",
        (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode(),
    )

    files = payload_files()
    lines = [f"{sha256(path)}  {name}" for name, path in sorted(files.items())]
    atomic_write(ROOT / "ARTIFACTS.sha256", ("\n".join(lines) + "\n").encode())

    print(json.dumps({
        "status": receipt["status"],
        "manifested_payload_files": len(files),
        "pdf_pages": receipt["pdf_pages"],
        "pdf_sha256": receipt["pdf_sha256"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
