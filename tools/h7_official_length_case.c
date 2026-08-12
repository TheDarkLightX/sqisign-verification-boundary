// SPDX-License-Identifier: Apache-2.0
/*
 * Exercise one declared-length boundary at a public SQIsign verification API.
 *
 * The allocation extent matches the declared input length, except that a
 * one-byte allocation is used for declared length zero so a non-null pointer is
 * available. Under AddressSanitizer, an implementation which enters the
 * fixed-size signature decoder before validating the length should terminate
 * with a sanitizer finding. A repaired implementation should return clean
 * rejection without touching bytes outside the declared slice.
 *
 * This harness establishes only memory-safe rejection ordering. It does not
 * demonstrate signature acceptance, forgery, key recovery, or deployment-
 * specific exploitability.
 */

#include <api.h>
#include <sig.h>

#include <errno.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int
parse_length(const char *text, unsigned long long *value)
{
    char *end = NULL;
    unsigned long long parsed;

    errno = 0;
    parsed = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return 0;
    }
    if (parsed > (unsigned long long)SIZE_MAX - 1) {
        return 0;
    }
    *value = parsed;
    return 1;
}

int
main(int argc, char **argv)
{
    const char *api;
    unsigned long long declared_length;
    size_t allocation_length;
    unsigned char *pk = NULL;
    unsigned char *input = NULL;
    unsigned char *output = NULL;
    unsigned long long recovered_length = UINT64_C(0x5a5a5a5a5a5a5a5a);
    int result;
    int safe_rejection;

    if (argc != 3 || !parse_length(argv[2], &declared_length)) {
        fprintf(stderr, "usage: %s nist|detached declared_length\n", argv[0]);
        return 2;
    }
    api = argv[1];
    if (strcmp(api, "nist") != 0 && strcmp(api, "detached") != 0) {
        fprintf(stderr, "unknown API mode: %s\n", api);
        return 2;
    }

    allocation_length = declared_length == 0 ? 1 : (size_t)declared_length;
    pk = calloc(CRYPTO_PUBLICKEYBYTES, 1);
    input = calloc(allocation_length, 1);
    output = calloc(allocation_length + 1, 1);
    if (pk == NULL || input == NULL || output == NULL) {
        free(pk);
        free(input);
        free(output);
        return 2;
    }

    if (strcmp(api, "nist") == 0) {
        result = crypto_sign_open(output,
                                  &recovered_length,
                                  input,
                                  declared_length,
                                  pk);
        safe_rejection = result == 1 && recovered_length == 0;
        fprintf(stderr,
                "safe-return-check: api=nist declared_length=%llu "
                "result=%d recovered_length=%llu\n",
                declared_length,
                result,
                recovered_length);
    } else {
        result = sqisign_verify(output, 0, input, declared_length, pk);
        safe_rejection = result == 1;
        fprintf(stderr,
                "safe-return-check: api=detached declared_length=%llu result=%d\n",
                declared_length,
                result);
    }

    free(pk);
    free(input);
    free(output);
    return safe_rejection ? 0 : 3;
}
