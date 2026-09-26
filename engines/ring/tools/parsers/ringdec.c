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

/* Mono sound DPCM (RING_DVD.EXE 0x47bc20, called with vbits 10 from 0x47bbf0): 3 bits
 * skipped, then nsamples codes: 0 + vbits: delta d (d > 0x1ff: 0x200 - d), times 64;
 * 1: the previous delta again. Each code adds the delta to the running sample. state[0]
 * is the sample, state[1] the delta; both carry over between chunks. */
__declspec(dllexport) int ring_dpcm(const uint8_t *buf, size_t len, uint32_t pos, int vbits,
                                    int nsamples, int16_t *out, int16_t *state,
                                    uint32_t *endpos)
{
	int16_t sample = state[0], delta = state[1];
	pos += 3;
	for (int n = 0; n < nsamples; n++) {
		uint32_t w = window(buf, len, pos);
		int sh = 31 - (int)(pos & 7);
		if (!((w >> sh) & 1)) {
			int16_t d = (int16_t)((w << (32 - sh)) >> (32 - vbits));
			if (d > 0x1ff)
				d = (int16_t)(0x200 - d);
			delta = (int16_t)(d * 0x40);
			pos += vbits + 1;
		} else {
			pos += 1;
		}
		sample = (int16_t)(sample + delta);
		out[n] = sample;
	}
	state[0] = sample;
	state[1] = delta;
	*endpos = pos;
	return nsamples;
}

/* HBR video stream (RING_DVD.EXE 0x42ce30), one call per 'T' or 'S' chunk. Codes of 11 or
 * 12 bits are packed in nibbles; a 128-slot ring remembers recent codes (write position
 * restarts at 0 every call, contents persist: ring[] is in/out). A code <= ntiles is one
 * tile (4 pixels) of the chunk's tile table; ntiles < code < 0x780 is the (code-ntiles)th
 * run in the run list (u8 byte count, then u16 tile indices); code >= 0x780 is a segment
 * of the back buffer (segment k = code - 0x780, lengths in tiles). Every emitted code's
 * output is remembered (memo) so a ring reference repeats it.
 * Returns pixels written, or a negative error: -1 output overflow, -2 tile index out of
 * range, -3 run list overrun, -4 ring reference to an unset code, -5 segment out of range. */
typedef struct { int32_t kind, start, len; } memo_t; /* kind 0 unset, 1 tiles, 2 out, 3 back */

static int emit_copy(const memo_t *m, const uint16_t *tiles, const uint16_t *out_base,
                     const uint16_t *back, uint16_t *out, size_t n, size_t cap)
{
	const uint16_t *src = m->kind == 1 ? tiles : m->kind == 2 ? out_base : back;
	if (!m->kind)
		return -4;
	if (n + (size_t)m->len > cap)
		return -1;
	for (int i = 0; i < m->len; i++)
		out[n + i] = src[m->start + i];
	return m->len;
}

__declspec(dllexport) int ring_hbr(const uint8_t *buf, size_t buflen, uint32_t pos,
                                   uint32_t end, const uint8_t *runs, size_t runslen,
                                   const uint16_t *tiles, int ntiles, uint32_t *ring,
                                   const uint16_t *back, const uint16_t *segs, int nsegs,
                                   uint16_t *out, size_t cap)
{
	static memo_t memo[0x800];
	size_t n = 0;
	int half = 0, rp = 0;
	for (int i = 0; i < 0x800; i++)
		memo[i].kind = 0;
	for (int k = 0, c = 0; k < nsegs && 0x780 + k < 0x800; c += segs[k] * 4, k++) {
		memo[0x780 + k].kind = 3;
		memo[0x780 + k].start = c;
		memo[0x780 + k].len = segs[k] * 4;
	}
	while (pos < end) {
		uint8_t b = buf[pos], nx = pos + 1 < buflen ? buf[pos + 1] : 0;
		uint32_t code;
		int is_new;
		if (half) {
			uint8_t lo = b & 15;
			is_new = lo < 8;
			code = is_new ? lo * 256u + nx : ring[lo * 16 + (nx >> 4) - 0x80];
			pos += is_new ? 2 : 1;
			half = !is_new;
		} else {
			is_new = b < 0x80;
			code = is_new ? b * 16u + (nx >> 4) : ring[b - 0x80];
			pos += 1;
			half = is_new;
		}
		int r;
		if (!is_new) {
			if (code >= 0x800)
				return -4;
			r = emit_copy(&memo[code], tiles, out, back, out, n, cap);
		} else {
			ring[rp] = code;
			rp = (rp + 1) & 127;
			if ((int)code > ntiles && code < 0x780) {
				size_t p = 0;
				for (uint32_t k = 0; k + 1 < code - ntiles; k++) {
					if (p >= runslen)
						return -3;
					p += runs[p] + 1u;
				}
				if (p >= runslen || p + 1 + runs[p] > runslen)
					return -3;
				int cnt = runs[p] >> 1;
				if (n + cnt * 4u > cap)
					return -1;
				memo[code].kind = 2;
				memo[code].start = (int32_t)n;
				memo[code].len = cnt * 4;
				for (int k = 0; k < cnt; k++) {
					int t = runs[p + 1 + 2 * k] | runs[p + 2 + 2 * k] << 8;
					if (t >= ntiles)
						return -2;
					for (int q = 0; q < 4; q++)
						out[n + 4 * k + q] = tiles[t * 4 + q];
				}
				r = cnt * 4;
			} else if (code >= 0x780) {
				if ((int)code - 0x780 >= nsegs)
					return -5;
				r = emit_copy(&memo[code], tiles, out, back, out, n, cap);
			} else if (memo[code].kind) {
				r = emit_copy(&memo[code], tiles, out, back, out, n, cap);
			} else {
				if ((int)code >= ntiles)
					return -2;
				memo[code].kind = 1;
				memo[code].start = (int32_t)code * 4;
				memo[code].len = 4;
				r = emit_copy(&memo[code], tiles, out, back, out, n, cap);
			}
		}
		if (r < 0)
			return r;
		n += (size_t)r;
	}
	return (int)n;
}
