#!/usr/bin/env python3
"""Fail-closed, read-only validator for the standalone H7 release."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
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
REQUIRED_ROOT = set(CORE + ["ARTIFACTS.sha256", "validation_receipt.json"])
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache"}
FORBIDDEN_TOP_LEVEL_SUFFIXES = {
    ".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".log", ".out",
    ".pyc", ".pyo", ".synctex.gz",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    require(
        result.returncode == 0,
        f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}",
    )
    return result.stdout


def payload_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for directory, directories, names in os.walk(ROOT, followlinks=False):
        here = Path(directory)
        directories[:] = [name for name in directories if name != ".git"]
        for name in directories:
            require(not (here / name).is_symlink(), f"symlink directory: {here / name}")
        for name in names:
            path = here / name
            relative = path.relative_to(ROOT).as_posix()
            if relative == "ARTIFACTS.sha256" or relative.startswith(".git/"):
                continue
            require(path.is_file() and not path.is_symlink(), f"invalid payload: {relative}")
            require(not (set(path.parts) & FORBIDDEN_PARTS), f"cache path: {relative}")
            if "/" not in relative:
                require(not any(relative.endswith(suffix)
                                for suffix in FORBIDDEN_TOP_LEVEL_SUFFIXES),
                        f"build/cache artifact: {relative}")
            files[relative] = path
    return files


def manifest_entries(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text().splitlines():
        fields = line.split("  ", 1)
        require(len(fields) == 2, f"malformed manifest line: {line}")
        digest, name = fields
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
                f"malformed digest: {digest}")
        require(name not in entries, f"duplicate manifest entry: {name}")
        require(not name.startswith("/") and ".." not in Path(name).parts,
                f"unsafe manifest path: {name}")
        entries[name] = digest
    return entries


def scan_public_text(files: dict[str, Path]) -> None:
    forbidden = {
        "/home/" + "trevormoc": "private workstation path",
        "trevormoc-" + "system-product-name": "private hostname",
        "dana" + "@": "private author email",
        "contact" + "@sqisign": "private disclosure address",
        "github" + "_pat_": "GitHub token",
        "gh" + "p_": "GitHub token",
        "sk-" + "proj-": "API key",
    }
    for name, path in files.items():
        if path.suffix.lower() == ".pdf":
            continue
        data = path.read_bytes()
        if b"\x00" in data:
            continue
        lowered = data.decode("utf-8", errors="replace").lower()
        for needle, label in forbidden.items():
            require(needle not in lowered, f"{label} in {name}")


def main() -> int:
    root_names = {path.name for path in ROOT.iterdir() if path.name != ".git"}
    require(REQUIRED_ROOT <= root_names,
            f"missing root files: {sorted(REQUIRED_ROOT - root_names)}")

    files = payload_files()
    manifest = manifest_entries(ROOT / "ARTIFACTS.sha256")
    require(set(manifest) == set(files),
            f"manifest inventory mismatch: {sorted(set(manifest) ^ set(files))}")
    for name, expected in manifest.items():
        require(sha256(files[name]) == expected, f"manifest mismatch: {name}")

    scan_public_text(files)

    claims = json.loads((ROOT / "claims_evidence.json").read_text())
    require(claims["status"] == "PUBLIC_PREPRINT_DISCLOSURE_AUTHORIZED",
            "claims status")
    require(claims["author"] == "Dana Edwards", "author")
    require(claims["ai_authorship"] is False, "AI authorship")
    authority = claims["audited_authority"]
    require(authority["revision"] ==
            "dd133d7aca576c361a270c8e6434832535b42ecc", "authority revision")
    require(authority["public_main_revision_at_cutoff"] == authority["revision"],
            "public-main cutoff")
    confirmation = claims["maintainer_confirmation"]
    for field in (
        "independent_prior_fix_reported",
        "affected_behavior_reproduced_by_maintainers",
        "patched_behavior_retested_clean_by_maintainers",
        "detached_exact_length_contract_confirmed",
        "signed_message_lower_bound_contract_confirmed",
        "immediate_publication_authorized",
    ):
        require(confirmation[field] is True, f"maintainer confirmation: {field}")
    require(confirmation["public_fix_commit_available_at_cutoff"] is False,
            "public fixing-commit boundary")
    claim_ids = {claim["id"] for claim in claims["claims"]}
    require(claim_ids == {
        "H7-LEN-001",
        "H7-TRAIL-001",
        "H7-REPAIR-001",
        "H7-CANON-STRUCTURAL-001",
        "H7-XONLY-QUOTIENT-001",
    }, "headline claim set")

    main_record = (ROOT / "PUBLIC_MAIN_2026_08_12.txt").read_text().strip()
    require(main_record.startswith(authority["revision"]), "public main record")
    require(main_record.endswith("refs/heads/main"), "public main ref")

    packet = ROOT / "research/h7_completion_2026_08_11"
    fresh_path = packet / "generated/validation_receipt.json"
    original_path = packet / "ORIGINAL_VALIDATION_RECEIPT.json"
    lean_path = packet / "lean/validation_receipt.json"
    normalization_path = packet / "PUBLIC_TRANSCRIPT_NORMALIZATION.md"
    fresh = json.loads(fresh_path.read_text())
    lean = json.loads(lean_path.read_text())
    replay = claims["fresh_replay"]
    require(sha256(fresh_path) == replay["receipt_sha256"], "fresh receipt binding")
    require(sha256(original_path) == replay["original_pre_normalization_receipt_sha256"],
            "original receipt binding")
    require(normalization_path.relative_to(ROOT).as_posix() ==
            replay["public_transcript_normalization"], "normalization path binding")
    require(replay["complete_generated_artifacts_excluding_receipt"] == 196,
            "fresh artifact count claim")
    require(fresh["status"] == "PASS_FRESH_CURRENT_EXACT_REVISION_REPLAY",
            "fresh replay")
    require(fresh["complete_generated_artifact_count"] == 196,
            "fresh artifact count")
    require(fresh["aggregates"]["unpatched_asan_findings"] == 2656,
            "ASan aggregate")
    require(fresh["aggregates"]["unpatched_overlong_acceptances"] == 1200,
            "suffix aggregate")
    require(fresh["aggregates"]["repaired_safe_rejections"] == 2656,
            "repair aggregate")
    require(fresh["aggregates"]["repaired_exact_kat_acceptances"] == 600,
            "KAT aggregate")
    for name, expected in fresh["packet_files_sha256"].items():
        bound = ROOT / name
        require(bound.is_file(), f"missing fresh bound input: {name}")
        require(sha256(bound) == expected, f"fresh bound input mismatch: {name}")
    require(lean["status"] == "PASS_EXACT_SOURCE_RECOMPILE", "Lean replay")
    require(lean["placeholder_scan_matches"] == 0, "Lean placeholders")

    tex = (ROOT / "manuscript.tex").read_text()
    issue = (ROOT / "PUBLIC_ISSUE_DRAFT.md").read_text()
    citation = (ROOT / "CITATION.cff").read_text()
    require("\\author{Dana Edwards}" in tex, "TeX author")
    require("PREPRINT --- NOT PEER REVIEWED" in tex, "preprint marker")
    require("No AI system is an author" in tex, "AI disclosure")
    require("INTERNAL DRAFT" not in tex and "NOT FOR SUBMISSION" not in tex,
            "stale internal marker")
    require("authorized immediate" in tex.lower(), "publication authorization")
    require("developed independently" in tex.lower(), "fix chronology")
    require("2,400" not in tex and "canonical-zero" not in tex,
            "unpackaged historical field experiment")
    require("not a signature forgery" in issue.lower(), "issue nonclaim")
    require("cff-version: 1.2.0" in citation, "CFF version")
    require("family-names: Edwards" in citation and "given-names: Dana" in citation,
            "CFF author")
    require("https://github.com/TheDarkLightX/sqisign-verification-boundary" in citation,
            "CFF repository")

    receipt = json.loads((ROOT / "validation_receipt.json").read_text())
    require(receipt["status"] == "PASS_PUBLIC_PREPRINT_PACKET", "receipt status")
    require(receipt["responsible_disclosure_completed"] is True, "disclosure flag")
    require(receipt["publication_authorized"] is True, "publication flag")
    require(receipt["fresh_matrix_receipt_sha256"] == sha256(fresh_path),
            "receipt fresh replay hash")
    require(receipt["lean_receipt_sha256"] == sha256(lean_path),
            "receipt Lean hash")
    core_hashes = {name: sha256(ROOT / name) for name in CORE}
    require(receipt["source_sha256"] == core_hashes, "receipt core hashes")
    require(receipt["pdf_sha256"] == sha256(ROOT / "manuscript.pdf"),
            "receipt PDF hash")

    environment = os.environ.copy()
    environment.update({
        "SOURCE_DATE_EPOCH": str(receipt["source_date_epoch"]),
        "FORCE_SOURCE_DATE": "1",
        "TZ": "UTC",
    })
    with tempfile.TemporaryDirectory(prefix="h7-public-preprint-") as directory:
        target = Path(directory)
        shutil.copy2(ROOT / "manuscript.tex", target / "manuscript.tex")
        shutil.copy2(ROOT / "references.bib", target / "references.bib")
        run(["latexmk", "-pdf", "-bibtex", "-interaction=nonstopmode",
             "-halt-on-error", "manuscript.tex"], target, environment)
        log = (target / "manuscript.log").read_text(errors="replace")
        for forbidden in ("LaTeX Warning", "Overfull \\hbox", "Overfull \\vbox",
                          "undefined references", "undefined citations", "Fatal error"):
            require(forbidden not in log, f"build log contains: {forbidden}")
        require(sha256(target / "manuscript.pdf") == sha256(ROOT / "manuscript.pdf"),
                "isolated PDF is not byte-identical")

    info = run(["pdfinfo", "manuscript.pdf"], ROOT)
    require("Author:          Dana Edwards" in info, "PDF author")
    page_match = re.search(r"^Pages:\s+(\d+)$", info, re.M)
    require(page_match is not None, "PDF page count")
    require(int(page_match.group(1)) == receipt["pdf_pages"], "receipt page count")
    pdf_text = run(["pdftotext", "manuscript.pdf", "-"], ROOT)
    for phrase in ("PREPRINT", "Dana Edwards", "maintainers", "No AI system is an author"):
        require(phrase in pdf_text, f"PDF text missing: {phrase}")

    output = {
        "schema": "isogeny-crypto/h7-public-preprint-validation/v2",
        "status": "PASS_PUBLIC_PREPRINT_PACKET",
        "author": "Dana Edwards",
        "claims_checked": len(claims["claims"]),
        "manifested_payload_files": len(files),
        "responsible_disclosure_completed": True,
        "publication_authorized": True,
        "fresh_matrix_replayed": True,
        "lean_exact_source_recompiled": True,
        "privacy_scan_passed": True,
        "isolated_pdf_byte_identical": True,
        "pdf_pages": int(page_match.group(1)),
        "pdf_sha256": sha256(ROOT / "manuscript.pdf"),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
