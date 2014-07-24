#!/usr/bin/python3

from math import sin
import sys
import struct


class md5 :
    
    words = None
    (A, B, C, D) =  (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)
    T = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501, 
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 
        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821, 
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8, 
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 
        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a, 
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70, 
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 
        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665, 
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 
        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1, 
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
    ]


    def F(self, X, Y, Z) : 
        return (X & Y) | ((~X) & Z)

    def G(self, X, Y, Z) :
        return (X & Z) | (Y & (~Z))

    def H(self, X, Y, Z) :
        return X ^ Y ^ Z

    def I(self, X, Y, Z) :
        return Y ^ (X | (~Z))

    def __init__(self, message):
        self.words = self.makechunks(message)
        self.dothefollowing()

    def makechunks(self, seq):
        #convert to bytearray
        words = bytearray(seq, "utf8")
        #keep size for later
        s = len(words)
        #add the byte 10000000b = 0x80 = 128 at the very end
        words.append(0x80)
        """error class : test it to see if that works with (k*512 + 511)b messages"""
        #slice into 512b (64B) chunks
        words = [words[l:l+64] for l in range(0, len(words), 64)]
        #pad last word with 0s so that there is 448b (62B)
        words[-1] = words[-1].ljust(56, b'\x00')
        #add the length to the end of the message
        #byte -> bit conversion shortcut
        words[-1].extend(struct.pack('<I', (s << 3)))
        words[-1].extend(struct.pack('<I', (s >> 29)))

        return words

    def leftcircularshift(self, base, offset) :
        return (base << offset) | (base >> (32 - offset))

    def round1(self, a, b, c, d, k, s, i, X):
        return ((self.leftcircularshift(((a + self.F(b, c, d) + X[k] + self.T[i]) % (1 << 32)), s) % (1 << 32)) + b) % (1 << 32)

    def round2(self, a, b, c, d, k, s, i, X):
        return ((self.leftcircularshift(((a + self.G(b, c, d) + X[k] + self.T[i]) % (1 << 32)), s) % (1 << 32)) + b) % (1 << 32)

    def round3(self, a, b, c, d, k, s, i, X):
        return ((self.leftcircularshift(((a + self.H(b, c, d) + X[k] + self.T[i]) % (1 << 32)), s) % (1 << 32)) + b) % (1 << 32)

    def round4(self, a, b, c, d, k, s, i, X):
        return ((self.leftcircularshift(((a + self.I(b, c, d) + X[k] + self.T[i]) % (1 << 32)), s) % (1 << 32)) + b) % (1 << 32)

    def dothefollowing(self):
        """ ref. rfc1321 page 4 """
        for word in self.words :
            X = [struct.unpack("<L", word[j*4:j*4+4])[0] for j in range(16)]
            AA = self.A
            BB = self.B
            CC = self.C
            DD = self.D
            #round 1
            AA = self.round1(AA, BB, CC, DD, 0, 7, 0, X)
            DD = self.round1(DD, AA, BB, CC, 1,12, 1, X)
            CC = self.round1(CC, DD, AA, BB, 2,17, 2, X)
            BB = self.round1(BB, CC, DD, AA, 3,22, 3, X)
            AA = self.round1(AA, BB, CC, DD, 4, 7, 4, X)
            DD = self.round1(DD, AA, BB, CC, 5,12, 5, X)
            CC = self.round1(CC, DD, AA, BB, 6,17, 6, X)
            BB = self.round1(BB, CC, DD, AA, 7,22, 7, X)
            AA = self.round1(AA, BB, CC, DD, 8, 7, 8, X)
            DD = self.round1(DD, AA, BB, CC, 9,12, 9, X)
            CC = self.round1(CC, DD, AA, BB,10,17,10, X)
            BB = self.round1(BB, CC, DD, AA,11,22,11, X)
            AA = self.round1(AA, BB, CC, DD,12, 7,12, X)
            DD = self.round1(DD, AA, BB, CC,13,12,13, X)
            CC = self.round1(CC, DD, AA, BB,14,17,14, X)
            BB = self.round1(BB, CC, DD, AA,15,22,15, X)
            #round 2
            AA = self.round2(AA, BB, CC, DD, 1, 5,16, X)
            DD = self.round2(DD, AA, BB, CC, 6, 9,17, X)
            CC = self.round2(CC, DD, AA, BB,11,14,18, X)
            BB = self.round2(BB, CC, DD, AA, 0,20,19, X)
            AA = self.round2(AA, BB, CC, DD, 5, 5,20, X)
            DD = self.round2(DD, AA, BB, CC,10, 9,21, X)
            CC = self.round2(CC, DD, AA, BB,15,14,22, X)
            BB = self.round2(BB, CC, DD, AA, 4,20,23, X)
            AA = self.round2(AA, BB, CC, DD, 9, 5,24, X)
            DD = self.round2(DD, AA, BB, CC,14, 9,25, X)
            CC = self.round2(CC, DD, AA, BB, 3,14,26, X)
            BB = self.round2(BB, CC, DD, AA, 8,20,27, X)
            AA = self.round2(AA, BB, CC, DD,13, 5,28, X)
            DD = self.round2(DD, AA, BB, CC, 2, 9,29, X)
            CC = self.round2(CC, DD, AA, BB, 7,14,30, X)
            BB = self.round2(BB, CC, DD, AA,12,20,31, X)
            #round 3
            AA = self.round3(AA, BB, CC, DD, 5, 4,32, X)
            DD = self.round3(DD, AA, BB, CC, 8,11,33, X)
            CC = self.round3(CC, DD, AA, BB,11,16,34, X)
            BB = self.round3(BB, CC, DD, AA,14,23,35, X)
            AA = self.round3(AA, BB, CC, DD, 1, 4,36, X)
            DD = self.round3(DD, AA, BB, CC, 4,11,37, X)
            CC = self.round3(CC, DD, AA, BB, 7,16,38, X)
            BB = self.round3(BB, CC, DD, AA,10,23,39, X)
            AA = self.round3(AA, BB, CC, DD,13, 4,40, X)
            DD = self.round3(DD, AA, BB, CC, 0,11,41, X)
            CC = self.round3(CC, DD, AA, BB, 3,16,42, X)
            BB = self.round3(BB, CC, DD, AA, 6,23,43, X)
            AA = self.round3(AA, BB, CC, DD, 9, 4,44, X)
            DD = self.round3(DD, AA, BB, CC,12,11,45, X)
            CC = self.round3(CC, DD, AA, BB,15,16,46, X)
            BB = self.round3(BB, CC, DD, AA, 2,23,47, X)
            #round 4
            AA = self.round4(AA, BB, CC, DD, 0, 6,48, X)
            DD = self.round4(DD, AA, BB, CC, 7,10,49, X)
            CC = self.round4(CC, DD, AA, BB,14,15,50, X)
            BB = self.round4(BB, CC, DD, AA, 5,21,51, X)
            AA = self.round4(AA, BB, CC, DD,12, 6,52, X)
            DD = self.round4(DD, AA, BB, CC, 3,10,53, X)
            CC = self.round4(CC, DD, AA, BB,10,15,54, X)
            BB = self.round4(BB, CC, DD, AA, 1,21,55, X)
            AA = self.round4(AA, BB, CC, DD, 8, 6,56, X)
            DD = self.round4(DD, AA, BB, CC,15,10,57, X)
            CC = self.round4(CC, DD, AA, BB, 6,15,58, X)
            BB = self.round4(BB, CC, DD, AA,13,21,59, X)
            AA = self.round4(AA, BB, CC, DD, 4, 6,60, X)
            DD = self.round4(DD, AA, BB, CC,11,10,61, X)
            CC = self.round4(CC, DD, AA, BB, 2,15,62, X)
            BB = self.round4(BB, CC, DD, AA, 9,21,63, X)

            #addition
            self.A = (self.A + AA) % (1 << 32)
            self.B = (self.B + BB) % (1 << 32)
            self.C = (self.C + CC) % (1 << 32)
            self.D = (self.D + DD) % (1 << 32)

    def printdigest(self):
        mauvaisbe = ''.join([hex(self.A),hex(self.B),hex(self.C),hex(self.D)]).replace("0x","")
        bonbe = ""
        for x in range(0, 4):
            b = x*8
            bonbe += mauvaisbe[b+6:b+8]
            bonbe += mauvaisbe[b+4:b+6]
            bonbe += mauvaisbe[b+2:b+4]
            bonbe += mauvaisbe[b+0:b+2]
        print(bonbe)






if len(sys.argv) < 2:
    print("usage : " + sys.argv[0] + " file")
    sys.exit(1)

toHash = ''.join(open(sys.argv[1], 'r').readlines())
x = md5(toHash)
x.printdigest()
