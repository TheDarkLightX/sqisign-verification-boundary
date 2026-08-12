#!/usr/bin/env python3
"""Classify every declared signature length below the fixed-size boundary.

The controller invokes one ASan-instrumented harness process per public API and
undersized length. For an unpatched authority, a case may trigger
AddressSanitizer or return clean rejection; the boundary is observed rather
than assumed. For a candidate repaired authority, every undersized case must
return clean rejection without a sanitizer finding.

Full-length behavior is tested with valid published KAT objects in the companion
trailing-byte experiment. Zero-filled full-length objects are intentionally not
used as a length oracle because unrelated algebraic assertions or rejection
paths can dominate after the parser has safely consumed the complete slice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


ASAN_PATTERN = re.compile(
    r"AddressSanitizer|heap-buffer-overflow|stack-buffer-overflow|"
    r"global-buffer-overflow|use-after-free|SEGV"
)
SAFE_MARKER = "safe-return-check:"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def classify(completed: subprocess.CompletedProcess[str]) -> str:
    combined = completed.stdout + "\n" + completed.stderr
    if ASAN_PATTERN.search(combined):
        return "asan_finding"
    if completed.returncode == 0 and SAFE_MARKER in combined:
        return "safe_rejection"
    return "unexpected"


def contiguous_ranges(values: list[int]) -> list[list[int]]:
    if not values:
        return []
    ordered = sorted(set(values))
    ranges: list[list[int]] = []
    start = previous = ordered[0]
    for value in ordered[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append([start, previous])
        start = previous = value
    ranges.append([start, previous])
    return ranges


def run_case(
    harness: Path,
    api: str,
    declared_length: int,
    timeout_seconds: int,
    environment: dict[str, str],
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [str(harness), api, str(declared_length)],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=environment,
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return {
            "api": api,
            "declared_length": declared_length,
            "classification": "timeout",
            "returncode": None,
            "stdout_sha256": sha256_bytes(stdout.encode()),
            "stderr_sha256": sha256_bytes(stderr.encode()),
            "stdout": stdout[-4000:],
            "stderr": stderr[-12000:],
        }

    classification = classify(completed)
    return {
        "api": api,
        "declared_length": declared_length,
        "classification": classification,
        "returncode": completed.returncode,
        "stdout_sha256": sha256_bytes(completed.stdout.encode()),
        "stderr_sha256": sha256_bytes(completed.stderr.encode()),
        "stdout": completed.stdout[-4000:] if classification == "unexpected" else "",
        "stderr": completed.stderr[-12000:] if classification == "unexpected" else "",
    }


def representative_logs(cases: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    representatives: dict[str, dict[str, Any]] = {}
    for api in ("nist", "detached"):
        findings = [
            case
            for case in cases
            if case["api"] == api and case["classification"] == "asan_finding"
        ]
        if not findings:
            continue
        first = min(findings, key=lambda case: case["declared_length"])
        last = max(findings, key=lambda case: case["declared_length"])
        representatives[api] = {
            "first_length": first["declared_length"],
            "first_stderr_sha256": first["stderr_sha256"],
            "last_length": last["declared_length"],
            "last_stderr_sha256": last["stderr_sha256"],
        }
    return representatives


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--signature-bytes", type=int, required=True)
    parser.add_argument("--parameter-level", type=int, choices=(1, 3, 5), required=True)
    parser.add_argument(
        "--implementation",
        choices=("ref", "broadwell", "arm64crypto"),
        required=True,
    )
    parser.add_argument("--authority-state", choices=("unpatched", "repaired"), required=True)
    parser.add_argument("--official-revision", required=True)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.signature_bytes <= 0:
        raise SystemExit("signature size must be positive")

    environment = dict(os.environ)
    environment["ASAN_OPTIONS"] = (
        "detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86:"
        "allocator_may_return_null=1"
    )
    environment["UBSAN_OPTIONS"] = "halt_on_error=1:exitcode=87:print_stacktrace=1"

    lengths = list(range(args.signature_bytes))
    cases: list[dict[str, Any]] = []
    for api in ("nist", "detached"):
        for declared_length in lengths:
            cases.append(
                run_case(
                    args.harness,
                    api,
                    declared_length,
                    args.timeout,
                    environment,
                )
            )

    counts: dict[str, dict[str, int]] = {}
    asan_ranges: dict[str, list[list[int]]] = {}
    last_undersized_results: dict[str, str] = {}
    unexpected_cases: list[dict[str, Any]] = []
    repaired_failures: list[dict[str, Any]] = []

    for api in ("nist", "detached"):
        api_cases = [case for case in cases if case["api"] == api]
        api_counts: dict[str, int] = {}
        for case in api_cases:
            classification = str(case["classification"])
            api_counts[classification] = api_counts.get(classification, 0) + 1
            if classification in ("unexpected", "timeout"):
                unexpected_cases.append(case)
            if args.authority_state == "repaired" and classification != "safe_rejection":
                repaired_failures.append(case)
        counts[api] = dict(sorted(api_counts.items()))
        asan_ranges[api] = contiguous_ranges(
            [
                int(case["declared_length"])
                for case in api_cases
                if case["classification"] == "asan_finding"
            ]
        )
        last_undersized_results[api] = next(
            str(case["classification"])
            for case in api_cases
            if case["declared_length"] == args.signature_bytes - 1
        )

    unsafe_under_lengths = {
        api: [
            int(case["declared_length"])
            for case in cases
            if case["api"] == api and case["classification"] == "asan_finding"
        ]
        for api in ("nist", "detached")
    }
    safe_under_lengths = {
        api: [
            int(case["declared_length"])
            for case in cases
            if case["api"] == api and case["classification"] == "safe_rejection"
        ]
        for api in ("nist", "detached")
    }

    summary = {
        "schema": "isogeny-crypto/h7-official-length-matrix/v2",
        "official_repository": "SQISign/the-sqisign",
        "official_revision": args.official_revision,
        "parameter_level": args.parameter_level,
        "implementation": args.implementation,
        "authority_state": args.authority_state,
        "signature_bytes": args.signature_bytes,
        "tested_declared_length_range": [0, args.signature_bytes - 1],
        "tested_cases": len(cases),
        "counts": counts,
        "asan_ranges": asan_ranges,
        "last_undersized_results": last_undersized_results,
        "unsafe_undersized_length_count": {
            api: len(values) for api, values in unsafe_under_lengths.items()
        },
        "safe_undersized_length_count": {
            api: len(values) for api, values in safe_under_lengths.items()
        },
        "unsafe_undersized_ranges": {
            api: contiguous_ranges(values) for api, values in unsafe_under_lengths.items()
        },
        "safe_undersized_ranges": {
            api: contiguous_ranges(values) for api, values in safe_under_lengths.items()
        },
        "representative_asan_logs": representative_logs(cases),
        "unexpected_case_count": len(unexpected_cases),
        "unexpected_cases": unexpected_cases,
        "repaired_failure_count": len(repaired_failures),
        "repaired_failures": repaired_failures,
        "harness_sha256": sha256_bytes(args.harness.read_bytes()),
        "claim_boundary": (
            "The matrix classifies memory-safe rejection ordering for every "
            "declared length strictly below the fixed signature boundary."
        ),
        "full_length_companion": (
            "Valid exact and overlong detached signatures are tested separately "
            "by h7_official_detached_trailing_kat.py."
        ),
        "nonclaims": [
            "A sanitizer finding does not establish signature acceptance or forgery.",
            "The matrix does not establish deployment-specific exploitability.",
            "A repaired matrix proves only the tested boundary family at the pinned authority.",
        ],
        "cases": cases,
    }
    args.out.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "parameter_level": args.parameter_level,
                "implementation": args.implementation,
                "authority_state": args.authority_state,
                "signature_bytes": args.signature_bytes,
                "tested_cases": len(cases),
                "counts": counts,
                "asan_ranges": asan_ranges,
                "last_undersized_results": last_undersized_results,
                "unexpected_case_count": len(unexpected_cases),
                "repaired_failure_count": len(repaired_failures),
            },
            indent=2,
            sort_keys=True,
        )
    )

    if unexpected_cases or repaired_failures:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
