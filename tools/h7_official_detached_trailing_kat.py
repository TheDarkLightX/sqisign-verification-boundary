#!/usr/bin/env python3
"""Test whether detached SQIsign verification honors the declared siglen.

Each valid KAT signature is checked at its exact fixed length and with one or
more deterministic trailing-byte extensions. If an overlong declared signature
is accepted, the detached API has accepted a distinct length-delimited byte
string with the same fixed signature prefix. The result is an API-level
encoding alias; it is not by itself a new signature forgery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_rsp(path: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    required = {"mlen", "msg", "pk", "smlen", "sm"}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            if current.get("count") is not None and required <= current.keys():
                records.append(current)
                current = {}
            continue
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        current[key.strip()] = value.strip()
    if current.get("count") is not None and required <= current.keys():
        records.append(current)
    return records


def invoke(
    verifier: Path,
    pk_path: Path,
    sig_path: Path,
    message_path: Path,
    declared_siglen: int,
    timeout_seconds: int,
    environment: dict[str, str],
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [
                str(verifier),
                str(pk_path),
                str(sig_path),
                str(message_path),
                str(declared_siglen),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=environment,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "classification": "timeout",
            "returncode": None,
            "stdout": str(error.stdout or "")[-4000:],
            "stderr": str(error.stderr or "")[-12000:],
        }

    if completed.returncode == 0:
        classification = "accepted"
    elif completed.returncode == 1:
        classification = "rejected"
    else:
        classification = "abnormal"
    return {
        "classification": classification,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def deterministic_tail(count: int, length: int) -> bytes:
    return bytes(((count * 131 + index * 17 + 1) & 0xFF) for index in range(length))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rsp", type=Path, required=True)
    parser.add_argument("--verifier", type=Path, required=True)
    parser.add_argument("--signature-bytes", type=int, required=True)
    parser.add_argument("--parameter-level", type=int, choices=(1, 3, 5), required=True)
    parser.add_argument(
        "--implementation",
        choices=("ref", "broadwell", "arm64crypto"),
        required=True,
    )
    parser.add_argument("--authority-state", choices=("unpatched", "repaired"), required=True)
    parser.add_argument("--official-revision", required=True)
    parser.add_argument("--extra-lengths", type=int, nargs="+", default=[1, 16])
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.signature_bytes <= 0 or any(length <= 0 for length in args.extra_lengths):
        raise SystemExit("signature and extra lengths must be positive")
    extra_lengths = sorted(set(args.extra_lengths))
    max_extra = max(extra_lengths)

    records = parse_rsp(args.rsp)[: args.limit]
    if not records:
        raise SystemExit("no KAT records parsed")

    environment = dict(os.environ)
    environment["ASAN_OPTIONS"] = (
        "detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86"
    )
    environment["UBSAN_OPTIONS"] = "halt_on_error=1:exitcode=87:print_stacktrace=1"

    outcomes: list[dict[str, Any]] = []
    malformed_records: list[dict[str, Any]] = []
    baseline_failures: list[dict[str, Any]] = []
    abnormal_results: list[dict[str, Any]] = []
    repaired_failures: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="h7-detached-trailing-") as temporary:
        work = Path(temporary)
        for record in records:
            count = int(record["count"])
            message_length = int(record["mlen"])
            signed_message_length = int(record["smlen"])
            message = bytes.fromhex(record["msg"])
            pk = bytes.fromhex(record["pk"])
            signed_message = bytes.fromhex(record["sm"])
            problems: list[str] = []
            if len(message) != message_length:
                problems.append("message length mismatch")
            if len(signed_message) != signed_message_length:
                problems.append("signed-message length mismatch")
            if signed_message_length - message_length != args.signature_bytes:
                problems.append("signature length mismatch")
            if message_length > len(signed_message) or signed_message[-message_length:] != message:
                problems.append("signed-message tail mismatch")
            if problems:
                malformed_records.append({"count": count, "problems": problems})
                continue

            signature = signed_message[: args.signature_bytes]
            extended_signature = signature + deterministic_tail(count, max_extra)
            pk_path = work / f"{count}.pk"
            sig_path = work / f"{count}.sig"
            message_path = work / f"{count}.msg"
            pk_path.write_bytes(pk)
            sig_path.write_bytes(extended_signature)
            message_path.write_bytes(message)

            exact = invoke(
                args.verifier,
                pk_path,
                sig_path,
                message_path,
                args.signature_bytes,
                args.timeout,
                environment,
            )
            if exact["classification"] != "accepted":
                baseline_failures.append({"count": count, "result": exact})

            extras: list[dict[str, Any]] = []
            for extra_length in extra_lengths:
                declared_length = args.signature_bytes + extra_length
                result = invoke(
                    args.verifier,
                    pk_path,
                    sig_path,
                    message_path,
                    declared_length,
                    args.timeout,
                    environment,
                )
                item = {
                    "extra_length": extra_length,
                    "declared_signature_length": declared_length,
                    "classification": result["classification"],
                    "returncode": result["returncode"],
                    "tail_sha256": sha256_bytes(extended_signature[args.signature_bytes:declared_length]),
                }
                extras.append(item)
                if result["classification"] in ("abnormal", "timeout"):
                    abnormal_results.append({"count": count, **item, "detail": result})
                if args.authority_state == "repaired" and result["classification"] != "rejected":
                    repaired_failures.append({"count": count, **item, "detail": result})

            outcomes.append(
                {
                    "count": count,
                    "signature_sha256": sha256_bytes(signature),
                    "exact_result": exact["classification"],
                    "extensions": extras,
                }
            )

    accepted_extensions = [
        {"count": outcome["count"], **extension}
        for outcome in outcomes
        for extension in outcome["extensions"]
        if extension["classification"] == "accepted"
    ]
    rejected_extensions = [
        {"count": outcome["count"], **extension}
        for outcome in outcomes
        for extension in outcome["extensions"]
        if extension["classification"] == "rejected"
    ]
    per_extra_length: dict[str, dict[str, int]] = {}
    for extra_length in extra_lengths:
        classifications = [
            extension["classification"]
            for outcome in outcomes
            for extension in outcome["extensions"]
            if extension["extra_length"] == extra_length
        ]
        per_extra_length[str(extra_length)] = {
            classification: classifications.count(classification)
            for classification in sorted(set(classifications))
        }

    summary = {
        "schema": "isogeny-crypto/h7-detached-trailing-kat/v1",
        "official_repository": "SQISign/the-sqisign",
        "official_revision": args.official_revision,
        "parameter_level": args.parameter_level,
        "implementation": args.implementation,
        "authority_state": args.authority_state,
        "api": "sqisign_verify",
        "signature_bytes": args.signature_bytes,
        "extra_lengths": extra_lengths,
        "record_count": len(records),
        "malformed_record_count": len(malformed_records),
        "malformed_records": malformed_records,
        "exact_baseline_accepted_count": sum(
            outcome["exact_result"] == "accepted" for outcome in outcomes
        ),
        "baseline_failure_count": len(baseline_failures),
        "baseline_failures": baseline_failures,
        "overlong_case_count": sum(len(outcome["extensions"]) for outcome in outcomes),
        "accepted_overlong_count": len(accepted_extensions),
        "rejected_overlong_count": len(rejected_extensions),
        "per_extra_length": per_extra_length,
        "accepted_extensions": accepted_extensions,
        "abnormal_result_count": len(abnormal_results),
        "abnormal_results": abnormal_results,
        "repaired_failure_count": len(repaired_failures),
        "repaired_failures": repaired_failures,
        "kat_sha256": sha256_bytes(args.rsp.read_bytes()),
        "experiment_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "verifier_sha256": sha256_bytes(args.verifier.read_bytes()),
        "interpretation": (
            "An accepted overlong case is a distinct declared byte string with a valid "
            "fixed signature prefix and trailing bytes. It demonstrates an API-level "
            "accepted encoding alias when siglen is ignored; it is not a new-message forgery."
        ),
        "nonclaims": [
            "An accepted trailing-byte alias does not create a signature for a new message.",
            "The experiment does not by itself establish strong-unforgeability consequences.",
            "The repaired result applies only to the tested patch, corpus, and authorities.",
        ],
        "outcomes": outcomes,
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
                "record_count": len(records),
                "exact_baseline_accepted_count": summary["exact_baseline_accepted_count"],
                "overlong_case_count": summary["overlong_case_count"],
                "accepted_overlong_count": len(accepted_extensions),
                "rejected_overlong_count": len(rejected_extensions),
                "per_extra_length": per_extra_length,
                "abnormal_result_count": len(abnormal_results),
                "repaired_failure_count": len(repaired_failures),
            },
            indent=2,
            sort_keys=True,
        )
    )

    if malformed_records or baseline_failures or abnormal_results or repaired_failures:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
