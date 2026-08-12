// SPDX-License-Identifier: Apache-2.0
/* Verify one detached SQIsign tuple with an explicit declared signature length. */

#include <api.h>
#include <sig.h>

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static unsigned char *
read_file(const char *path, size_t *length)
{
    FILE *file = fopen(path, "rb");
    unsigned char *buffer = NULL;
    long end;

    if (file == NULL || fseek(file, 0, SEEK_END) != 0) {
        if (file != NULL) fclose(file);
        return NULL;
    }
    end = ftell(file);
    if (end < 0 || fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return NULL;
    }
    buffer = malloc((size_t)end + 1);
    if (buffer == NULL) {
        fclose(file);
        return NULL;
    }
    if (end > 0 && fread(buffer, (size_t)end, 1, file) != 1) {
        free(buffer);
        fclose(file);
        return NULL;
    }
    fclose(file);
    *length = (size_t)end;
    return buffer;
}

static int
parse_length(const char *text, unsigned long long *value)
{
    char *end = NULL;
    unsigned long long parsed;

    errno = 0;
    parsed = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') return 0;
    *value = parsed;
    return 1;
}

int
main(int argc, char **argv)
{
    unsigned char *pk = NULL;
    unsigned char *sig = NULL;
    unsigned char *message = NULL;
    size_t pk_length = 0;
    size_t sig_file_length = 0;
    size_t message_length = 0;
    unsigned long long declared_siglen;
    int result;

    if (argc != 5 || !parse_length(argv[4], &declared_siglen)) {
        fprintf(stderr,
                "usage: %s public-key.bin signature.bin message.bin declared_siglen\n",
                argv[0]);
        return 2;
    }

    pk = read_file(argv[1], &pk_length);
    sig = read_file(argv[2], &sig_file_length);
    message = read_file(argv[3], &message_length);
    if (pk == NULL || sig == NULL || message == NULL ||
        pk_length != CRYPTO_PUBLICKEYBYTES ||
        declared_siglen > (unsigned long long)sig_file_length) {
        free(pk);
        free(sig);
        free(message);
        fprintf(stderr, "invalid harness input\n");
        return 2;
    }

    result = sqisign_verify(message,
                            (unsigned long long)message_length,
                            sig,
                            declared_siglen,
                            pk);
    printf("result=%d declared_siglen=%llu signature_file_length=%zu "
           "message_length=%zu accepted=%d\n",
           result,
           declared_siglen,
           sig_file_length,
           message_length,
           result == 0);

    free(pk);
    free(sig);
    free(message);
    return result == 0 ? 0 : 1;
}
