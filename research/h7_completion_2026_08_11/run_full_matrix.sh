#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REVISION=dd133d7aca576c361a270c8e6434832535b42ecc
PACKET_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RESEARCH_ROOT=$(cd "${PACKET_DIR}/../.." && pwd)

if [[ $# -ne 2 ]]; then
  echo "usage: $0 /clean/the-sqisign /output/directory" >&2
  exit 2
fi

SOURCE=$(cd "$1" && pwd)
OUTPUT=$2
mkdir -p "${OUTPUT}" "${OUTPUT}/raw"
OUTPUT=$(cd "${OUTPUT}" && pwd)

if [[ $(git -C "${SOURCE}" rev-parse HEAD) != "${EXPECTED_REVISION}" ]]; then
  echo "official checkout is not at ${EXPECTED_REVISION}" >&2
  exit 2
fi
if [[ -n $(git -C "${SOURCE}" status --porcelain) ]]; then
  echo "official checkout must be clean" >&2
  exit 2
fi

git -C "${SOURCE}" apply "${PACKET_DIR}/cmake-targets.patch"

{
  uname -a
  cc --version
  cmake --version
  python3 --version
  git -C "${SOURCE}" rev-parse HEAD
  git -C "${SOURCE}" remote -v
} > "${OUTPUT}/environment.txt"

git -C "${SOURCE}" ls-remote origin refs/heads/main \
  > "${OUTPUT}/upstream-main-ls-remote.txt"

declare -A SIGNATURE_BYTES=( [1]=148 [3]=224 [5]=292 )
declare -A KAT_SECRET_BYTES=( [1]=353 [3]=529 [5]=701 )

build_authority() {
  local implementation=$1
  local build_dir="${SOURCE}/build-${implementation}"
  cmake -S "${SOURCE}" -B "${build_dir}" \
    -DSQISIGN_BUILD_TYPE="${implementation}" \
    -DCMAKE_BUILD_TYPE=ASAN \
    -DENABLE_SIGN=OFF \
    -DENABLE_TESTS=OFF \
    -DH7_RESEARCH_ROOT="${RESEARCH_ROOT}" \
    > "${OUTPUT}/build-${implementation}.log" 2>&1
  cmake --build "${build_dir}" \
    --target h7_length_lvl1 h7_length_lvl3 h7_length_lvl5 \
             h7_detached_lvl1 h7_detached_lvl3 h7_detached_lvl5 \
    --parallel 2 >> "${OUTPUT}/build-${implementation}.log" 2>&1
}

capture_witness() {
  local implementation=$1
  local level=$2
  local state=$3
  local api=$4
  local length=$5
  local stem="${OUTPUT}/raw/${state}-lvl${level}-${implementation}-${api}-len${length}"
  set +e
  env ASAN_OPTIONS=detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86 \
    UBSAN_OPTIONS=halt_on_error=1:exitcode=87:print_stacktrace=1 \
    "${SOURCE}/build-${implementation}/h7_length_lvl${level}" \
    "${api}" "${length}" > "${stem}.stdout" 2> "${stem}.stderr"
  local status=$?
  set -e
  printf '%s\n' "${status}" > "${stem}.status"
}

run_state() {
  local state=$1
  for implementation in ref broadwell; do
    for level in 1 3 5; do
      local sig_bytes=${SIGNATURE_BYTES[${level}]}
      local kat_bytes=${KAT_SECRET_BYTES[${level}]}
      local build_dir="${SOURCE}/build-${implementation}"
      local prefix="${OUTPUT}/${state}-lvl${level}-${implementation}"

      python3 -B "${RESEARCH_ROOT}/tools/h7_official_length_matrix.py" \
        --harness "${build_dir}/h7_length_lvl${level}" \
        --signature-bytes "${sig_bytes}" \
        --parameter-level "${level}" \
        --implementation "${implementation}" \
        --authority-state "${state}" \
        --official-revision "${EXPECTED_REVISION}" \
        --out "${prefix}-length.json" \
        > "${prefix}-length.stdout"

      python3 -B "${RESEARCH_ROOT}/tools/h7_official_detached_trailing_kat.py" \
        --rsp "${SOURCE}/KAT/PQCsignKAT_${kat_bytes}_SQIsign_lvl${level}.rsp" \
        --verifier "${build_dir}/h7_detached_lvl${level}" \
        --signature-bytes "${sig_bytes}" \
        --parameter-level "${level}" \
        --implementation "${implementation}" \
        --authority-state "${state}" \
        --official-revision "${EXPECTED_REVISION}" \
        --extra-lengths 1 16 \
        --limit 100 \
        --out "${prefix}-trailing.json" \
        > "${prefix}-trailing.stdout"

      capture_witness "${implementation}" "${level}" "${state}" nist 0
      capture_witness "${implementation}" "${level}" "${state}" detached 0
      capture_witness "${implementation}" "${level}" "${state}" nist "$((sig_bytes - 1))"
      capture_witness "${implementation}" "${level}" "${state}" detached "$((sig_bytes - 1))"
    done
  done
}

build_authority ref
build_authority broadwell
run_state unpatched

git -C "${SOURCE}" apply "${RESEARCH_ROOT}/patches/sqisign-dd133d7-h7-length-guards.patch"
build_authority ref
build_authority broadwell
run_state repaired

python3 -B "${PACKET_DIR}/validate_results.py" "${OUTPUT}"
