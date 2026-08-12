#!/usr/bin/env python3
"""Aggregate and fail closed over a fresh H7 full-matrix replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


EXPECTED_REVISION = "dd133d7aca576c361a270c8e6434832535b42ecc"
SIGNATURE_BYTES = {1: 148, 3: 224, 5: 292}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_results.py generated-directory")
    output = Path(sys.argv[1]).resolve()
    require(output.is_dir(), "generated directory does not exist")
    packet = Path(__file__).resolve().parent
    research_root = packet.parent.parent

    files: dict[str, str] = {}
    aggregates = {
        "unpatched_undersized_calls": 0,
        "unpatched_asan_findings": 0,
        "repaired_undersized_calls": 0,
        "repaired_safe_rejections": 0,
        "unpatched_exact_kat_acceptances": 0,
        "unpatched_overlong_acceptances": 0,
        "repaired_exact_kat_acceptances": 0,
        "repaired_overlong_rejections": 0,
    }

    for state in ("unpatched", "repaired"):
        for level, signature_bytes in SIGNATURE_BYTES.items():
            for implementation in ("ref", "broadwell"):
                prefix = output / f"{state}-lvl{level}-{implementation}"
                length_path = Path(f"{prefix}-length.json")
                trailing_path = Path(f"{prefix}-trailing.json")
                length = json.loads(length_path.read_text())
                trailing = json.loads(trailing_path.read_text())
                files[length_path.name] = sha256(length_path)
                files[trailing_path.name] = sha256(trailing_path)

                require(length["official_revision"] == EXPECTED_REVISION, "length revision")
                require(trailing["official_revision"] == EXPECTED_REVISION, "trailing revision")
                require(length["tested_cases"] == 2 * signature_bytes, "length case count")
                require(length["unexpected_case_count"] == 0, "unexpected length case")
                require(trailing["record_count"] == 100, "KAT record count")
                require(trailing["baseline_failure_count"] == 0, "KAT baseline failure")
                require(trailing["abnormal_result_count"] == 0, "abnormal trailing case")

                if state == "unpatched":
                    asan = sum(
                        length["counts"][api].get("asan_finding", 0)
                        for api in ("nist", "detached")
                    )
                    require(asan == 2 * signature_bytes, "unpatched ASan coverage")
                    require(trailing["accepted_overlong_count"] == 200, "suffix acceptance")
                    aggregates["unpatched_undersized_calls"] += length["tested_cases"]
                    aggregates["unpatched_asan_findings"] += asan
                    aggregates["unpatched_exact_kat_acceptances"] += trailing[
                        "exact_baseline_accepted_count"
                    ]
                    aggregates["unpatched_overlong_acceptances"] += trailing[
                        "accepted_overlong_count"
                    ]
                else:
                    safe = sum(
                        length["counts"][api].get("safe_rejection", 0)
                        for api in ("nist", "detached")
                    )
                    require(length["repaired_failure_count"] == 0, "repair length failure")
                    require(safe == 2 * signature_bytes, "repaired safe coverage")
                    require(trailing["accepted_overlong_count"] == 0, "repair suffix acceptance")
                    require(trailing["rejected_overlong_count"] == 200, "repair suffix rejection")
                    aggregates["repaired_undersized_calls"] += length["tested_cases"]
                    aggregates["repaired_safe_rejections"] += safe
                    aggregates["repaired_exact_kat_acceptances"] += trailing[
                        "exact_baseline_accepted_count"
                    ]
                    aggregates["repaired_overlong_rejections"] += trailing[
                        "rejected_overlong_count"
                    ]

    require(aggregates["unpatched_undersized_calls"] == 2656, "aggregate undersized calls")
    require(aggregates["unpatched_asan_findings"] == 2656, "aggregate ASan findings")
    require(aggregates["repaired_safe_rejections"] == 2656, "aggregate repair rejections")
    require(aggregates["unpatched_exact_kat_acceptances"] == 600, "aggregate exact KAT")
    require(aggregates["unpatched_overlong_acceptances"] == 1200, "aggregate suffix acceptance")
    require(aggregates["repaired_exact_kat_acceptances"] == 600, "aggregate repaired KAT")
    require(aggregates["repaired_overlong_rejections"] == 1200, "aggregate suffix rejection")

    remote_line = (output / "upstream-main-ls-remote.txt").read_text().strip().split()
    require(len(remote_line) == 2, "remote main receipt")
    require(remote_line[0] == EXPECTED_REVISION, "remote main differs from audited revision")

    environment = (output / "environment.txt").read_text()
    require(EXPECTED_REVISION in environment.splitlines(), "local checkout revision receipt")

    raw_files = sorted((output / "raw").glob("*"))
    require(len(raw_files) == 144, "representative raw artifact inventory")
    for state in ("unpatched", "repaired"):
        for level, signature_bytes in SIGNATURE_BYTES.items():
            for implementation in ("ref", "broadwell"):
                for api in ("nist", "detached"):
                    for length in (0, signature_bytes - 1):
                        stem = output / "raw" / (
                            f"{state}-lvl{level}-{implementation}-{api}-len{length}"
                        )
                        status = (stem.with_suffix(".status")).read_text().strip()
                        stderr = (stem.with_suffix(".stderr")).read_text()
                        if state == "unpatched":
                            require(status == "86", "unpatched witness exit status")
                            require(
                                "ERROR: AddressSanitizer:" in stderr,
                                "unpatched witness lacks ASan report",
                            )
                        else:
                            require(status == "0", "repaired witness exit status")
                            require(
                                "safe-return-check:" in stderr,
                                "repaired witness lacks safe-return receipt",
                            )

    output_files = sorted(
        path for path in output.rglob("*")
        if path.is_file() and path.name != "validation_receipt.json"
    )
    require(len(output_files) == 196, "complete generated artifact inventory")
    for path in output_files:
        files[str(path.relative_to(output))] = sha256(path)

    packet_bindings = [
        packet / "README.md",
        packet / "cmake-targets.patch",
        packet / "run_full_matrix.sh",
        packet / "validate_results.py",
        research_root / "patches" / "sqisign-dd133d7-h7-length-guards.patch",
        research_root / "tools" / "h7_official_length_case.c",
        research_root / "tools" / "h7_official_length_matrix.py",
        research_root / "tools" / "h7_official_detached_kat_verify.c",
        research_root / "tools" / "h7_official_detached_trailing_kat.py",
    ]
    for path in packet_bindings:
        require(path.is_file(), f"missing packet input: {path}")
    packet_files = {
        str(path.relative_to(research_root)): sha256(path)
        for path in packet_bindings
    }

    receipt = {
        "schema": "isogeny-crypto/h7-fresh-full-matrix/v2",
        "status": "PASS_FRESH_CURRENT_EXACT_REVISION_REPLAY",
        "official_repository": "SQISign/the-sqisign",
        "official_revision": EXPECTED_REVISION,
        "remote_main_revision_at_replay": remote_line[0],
        "current_main_equals_audited_revision": True,
        "authorities": {
            "levels": [1, 3, 5],
            "implementations": ["ref", "broadwell"],
            "apis": ["crypto_sign_open", "sqisign_verify"],
        },
        "aggregates": aggregates,
        "representative_raw_artifact_count": len(raw_files),
        "complete_generated_artifact_count": len(output_files),
        "files_sha256": dict(sorted(files.items())),
        "packet_files_sha256": dict(sorted(packet_files.items())),
        "nonclaims": [
            "No signature forgery, key recovery, or remote-code-execution result is claimed.",
            "No deployment-specific exploitability is established.",
            "The detached siglen contract still requires maintainer confirmation.",
            "The candidate repair is not upstream-approved.",
            "This same-machine replay is not an independent third-party reproduction.",
            "No responsible disclosure or publication action is authorized by this receipt.",
        ],
    }
    receipt_path = output / "validation_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], **aggregates}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
