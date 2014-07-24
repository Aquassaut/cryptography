#define _BSD_SOURCE

#include <string.h>
#include <endian.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

#define BUFFSIZE 64

typedef unsigned char byte;

/*
    See the standard
*/
uint32_t k(int t) {
    if (t < 20) {
        return 0x5A827999;
    } else if (t < 40) {
        return 0x6ED9EBA1;
    } else if (t < 60) {
        return 0x8F1BBCDC;
    } else if (t < 80) {
        return 0xCA62C1D6;
    }
    fprintf(stderr, "wrong value for t while calculating K");
    exit(EXIT_FAILURE);
    return -1;
}

/*
    See the standard
*/
uint32_t f(uint32_t B, uint32_t C, uint32_t D, int t) {
    if (t < 20) {
        return (B & C) | ((~B) & D);
    } else if (t < 40) {
        return B ^ C ^ D;
    } else if (t < 60) {
        return (B & C) | (B & D) | (C & D);
    } else if (t < 80) {
        return B ^ C ^ D;
    }
    fprintf(stderr, "Wrong value for t while calculating f");
    exit(EXIT_FAILURE);
    return -1;
}

/*
    Left rotate, see http://tools.ietf.org/html/rfc3174
*/
uint32_t s(int shift, uint32_t x) {
    return (x << shift) | (x >> (32 - shift));
}

/*
    See the standard
*/
void hash(byte* m, int size, uint32_t* h) {
    int i, t;
    uint32_t w[80];
    uint32_t A, B, C, D, E, T;
    h[0] = 0x67452301, h[1] = 0xEFCDAB89, h[2] = 0x98BADCFE,
        h[3] = 0x10325476, h[4] = 0xC3D2E1F0;

    A = h[0], B = h[1], C = h[2], D = h[3], E = h[4];
    for (i = 0; i < (size / BUFFSIZE); i += 1) {
        for (t = 0; t < 16; t += 1) {
            w[t] = htobe32(((uint32_t*) m)[(16 * i) + t]);
        }
        for (t = 16; t < 80; t += 1) {
            w[t] = s(1, w[t-3] ^ w[t-8] ^ w[t-14] ^ w[t-16]);
        }
        A = h[0], B = h[1], C = h[2], D = h[3], E = h[4];
        for (t = 0; t < 80; t += 1) {
            T = s(5, A) + f(B, C, D, t) + E + w[t] + k(t);
            E = D;
            D = C;
            C = s(30, B);
            B = A;
            A = T;            
        }
        h[0] += A, h[1] += B, h[2] += C, h[3] += D, h[4] += E;
    }
}

int inflate(byte** word, int size) {
    int addedsize, newsize;
    int64_t besize;
    addedsize = BUFFSIZE - (size % BUFFSIZE);
    newsize = size + addedsize; /* skipping the -8B part,
                                   we'll use the extra anyway */
    if (NULL == (*word = realloc(*word, newsize))) {
        perror("realloc");
        exit(EXIT_FAILURE);
    }
    memset(*word + size, 0, addedsize); /* size will be rewritten afterwards */
    
    (*word)[size] = 0x80; /* Next byte should be 1000000 per standard */

    besize = htobe64(size * 8); /* 64b BE int to avoid manual conversion */
    memcpy(*word + newsize - 8, &besize, 8);
    return newsize;
}

int get_content_of_file(byte** buffer, FILE* file) {
    int pos, read;
    pos = 0;
    *buffer = malloc(BUFFSIZE);
    /* We need to make sure we don't overallocate if file is completely read */
    while ( BUFFSIZE == (read = fread(*buffer + pos, 1, BUFFSIZE, file)) ) {
        pos += read;
        if (NULL == (*buffer = realloc(*buffer, pos + BUFFSIZE))) {
            perror("realloc");
            exit(EXIT_FAILURE);
        }
    }
    pos += read;
    return pos;
}

int main(int argc, char* argv[]) {
    FILE* file = NULL;
    byte* word = NULL;
    int wordsize = 0, i = 0;
    uint32_t sum[5];
    /* Argument checks */
    if (argc != 2) {
        fprintf(stderr, "usage : %s file\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    file = fopen(argv[1], "r");
    if (NULL == file) {
        perror("fopen");
        exit(EXIT_FAILURE);
    }
    wordsize = get_content_of_file(&word, file);
    fclose(file); /* We won't use the file anymore */
    
    wordsize = inflate(&word, wordsize);
    hash(word, wordsize, sum);
    /* Let's not leak memory */
    free(word);
    /* Let's display hash in hex */
    for (i = 0; i < 5; i += 1) {
        printf("%.8x", sum[i]);
    }
    printf("\n");
    return EXIT_SUCCESS;
}