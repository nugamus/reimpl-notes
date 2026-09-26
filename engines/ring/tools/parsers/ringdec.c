/* Bit decoder shared by the Ring engine's packed images, panoramas and sound
 * (engines/ring/docs/formats/README.md, "Packed bit stream"; RING_DVD.EXE 0x4308e0).
 * Built into build/ringdec.dll by bitstream.py and called through ctypes: the Python
 * version of the same loop is too slow for the whole corpus. Keep the two in step;
 * bitstream.py --selftest compares them.
 *
 * Stream: bits MSB first. 0 + vbits: literal, stored in the replacement slot.
 * 10 + ibits: value of cache slot i, slot stamped. 11: repeat the last value, the last
 * slot stamped. The replacement slot is the least recently stamped of 64 (lowest index
 * on ties), recomputed whenever it is the one just used.
 */
#include <stdint.h>
#include <stddef.h>

static uint32_t window(const uint8_t *buf, size_t len, uint32_t pos)
{
	size_t o = pos >> 3;
	uint32_t w = 0;
	for (int i = 0; i < 4; i++)
		w = (w << 8) | (o + i < len ? buf[o + i] : 0);
	return w;
}

static uint8_t oldest(const int32_t *stamp)
{
	uint8_t best = 0;
	int32_t t = stamp[0];
	for (int i = 1; i < 64; i++)
		if (stamp[i] < t) {
			t = stamp[i];
			best = (uint8_t)i;
		}
	return best;
}

__declspec(dllexport) int ring_decode(const uint8_t *buf, size_t len, int vbits, int ibits,
                                      uint32_t pos, uint32_t end, uint16_t *out,
                                      size_t maxcodes, uint32_t *endpos)
{
	uint16_t value[64] = {0};
	int32_t stamp[64] = {0};
	uint8_t repl = 0, last = 0;
	size_t n = 0;
	while (pos < end && n < maxcodes) {
		uint32_t w = window(buf, len, pos);
		int sh = 31 - (int)(pos & 7);
		if (!((w >> sh) & 1)) {
			uint16_t v = (uint16_t)((w << (32 - sh)) >> (32 - vbits));
			out[n++] = v;
			last = repl;
			value[repl] = v;
			pos += vbits + 1;
		} else if (!((w >> (sh - 1)) & 1)) {
			uint8_t i = (uint8_t)((w << (33 - sh)) >> (32 - ibits));
			last = i;
			out[n++] = value[i];
			pos += ibits + 2;
			stamp[i] = (int32_t)pos;
			if (i == repl)
				repl = oldest(stamp);
		} else {
			pos += 2;
			out[n] = n ? out[n - 1] : 0;
			n++;
			stamp[last] = (int32_t)pos;
			if (repl == last)
				repl = oldest(stamp);
		}
	}
	*endpos = pos;
	return (int)n;
}
