/* Count raw CD sectors (2352 B, MODE1) whose stored EDC does not match their data.

     gcc -O2 -o build/edcscan.exe tools/disc/edcscan.c
     build/edcscan.exe image.bin

   A clean pressing has none; SafeDisc 2 discs carry a run of deliberately bad sectors
   (its "weak sectors" signature), which a raw .bin dump keeps. EDC = CRC-32, reflected
   polynomial 0xD8018001, over bytes 0..0x80F of a mode-1 sector, stored little-endian at
   0x810. Mode-2 sectors are skipped (counted). */
#include <stdint.h>
#include <stdio.h>

int main(int argc, char **argv) {
	static uint32_t t[256];
	for (uint32_t i = 0; i < 256; i++) {
		uint32_t e = i;
		for (int k = 0; k < 8; k++)
			e = (e >> 1) ^ (e & 1 ? 0xD8018001u : 0);
		t[i] = e;
	}
	FILE *f = argc > 1 ? fopen(argv[1], "rb") : NULL;
	if (!f) {
		fprintf(stderr, "usage: edcscan image.bin\n");
		return 1;
	}
	unsigned char s[2352];
	long n = 0, bad = 0, mode2 = 0, runs = 0, first = -1, last = -1;
	while (fread(s, 1, sizeof s, f) == sizeof s) {
		if (s[15] != 1) {
			mode2++;
		} else {
			uint32_t e = 0;
			for (int i = 0; i < 0x810; i++)
				e = (e >> 8) ^ t[(e ^ s[i]) & 0xff];
			uint32_t stored = s[0x810] | s[0x811] << 8 | s[0x812] << 16 | (uint32_t)s[0x813] << 24;
			if (e != stored) {
				if (last != n - 1)
					runs++;
				if (first < 0)
					first = n;
				bad++;
				last = n;
			}
		}
		n++;
	}
	printf("sectors %ld mode2 %ld bad-edc %ld runs %ld first %ld last %ld\n", n, mode2, bad, runs, first, last);
	return 0;
}
