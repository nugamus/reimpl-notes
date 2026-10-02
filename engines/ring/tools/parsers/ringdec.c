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

/* UNR video (README "UNR video codec", E-0350..E-0357): v1 in the Ring ISO EXE
 * (RING_ISO.EXE 0x42c680 tiles, 0x436440 picture), bits MSB first; v2 in Prophet's
 * (LEGEND.EXE 0x424240 tiles, 0x423630 picture), bits LSB first. Pictures are u32 per
 * pixel (B, G, R, 0), rows bottom-up, w*h, kept by the caller between frames.
 * Errors: -1 bits past the buffer, -2 a tile the data does not hold (limit = ntiles) or
 * a v2 entry above 0xfff, -3 a copy from before the picture or map, -4 a vector the first
 * row cannot use, -5 an unsupported layout. */
typedef struct { const uint8_t *buf; size_t len; uint32_t pos; int over; } bits_t;

static uint32_t msb(bits_t *b, int n)
{
	uint32_t v = 0;
	while (n--) {
		size_t o = b->pos >> 3;
		if (o >= b->len)
			b->over = 1;
		v = v << 1 | (o < b->len ? b->buf[o] >> (7 - (b->pos & 7)) & 1 : 0);
		b->pos++;
	}
	return v;
}

static uint32_t lsb(bits_t *b, int n)
{
	uint32_t v = 0;
	for (int i = 0; i < n; i++) {
		size_t o = b->pos >> 3;
		if (o >= b->len)
			b->over = 1;
		v |= (uint32_t)(o < b->len ? b->buf[o] >> (b->pos & 7) & 1 : 0) << i;
		b->pos++;
	}
	return v;
}

/* Tile table: 4096 tiles of 4 pixels x 4 bytes. ntiles counts tile 0, 16 raw bytes, and
 * tiles 1..ntiles-1, each the previous tile plus deltas. The original decodes one tile
 * more from the bytes after the data (zeros here); no index reaches it. *endbit is the
 * position after tile ntiles-1. v1: per tile 3 bits n, then 16 deltas of n+1 bits
 * (a sign bit after each non-zero one, 1 = minus). v2: per byte lane (0..3) 3 bits n;
 * n = 7: four raw bytes; else four deltas of n bits with the same sign rule. Doubled
 * (the header's interlace byte): tiles 0..ntiles-1 shifted left one bit as dwords. */
__declspec(dllexport) int ring_unr_tiles(int version, const uint8_t *buf, size_t len,
                                         int ntiles, int doubled, uint8_t *tiles,
                                         uint32_t *endbit)
{
	bits_t b = {buf, len, 16 * 8, 0};
	if (len < 16 || ntiles < 1 || ntiles > 4095)
		return -5;
	for (int i = 0; i < 16; i++)
		tiles[i] = buf[i];
	for (int t = 1; t <= ntiles; t++) {
		if (t == ntiles)
			*endbit = b.pos;
		uint8_t *d = tiles + 16 * t, *s = d - 16;
		for (int i = 0; i < 16; i++)
			d[i] = s[i];
		if (version == 1) {
			int n = (int)msb(&b, 3) + 1;
			for (int i = 0; i < 16; i++) {
				uint8_t v = (uint8_t)msb(&b, n);
				if (v)
					d[i] = (uint8_t)(msb(&b, 1) ? d[i] - v : d[i] + v);
			}
		} else {
			for (int c = 0; c < 4; c++) {
				int n = (int)lsb(&b, 3);
				for (int p = 0; p < 4; p++) {
					if (n == 7) {
						d[4 * p + c] = (uint8_t)lsb(&b, 8);
						continue;
					}
					uint8_t v = (uint8_t)lsb(&b, n);
					if (v)
						d[4 * p + c] = (uint8_t)(lsb(&b, 1) ? d[4 * p + c] - v : d[4 * p + c] + v);
				}
			}
		}
	}
	if (doubled)
		for (int i = 0; i < 4 * ntiles; i++) {
			uint32_t *w = (uint32_t *)tiles + i;
			*w <<= 1;
		}
	return 0;
}

/* v1 picture, interlaced 4-pixel tiles (every Ring ISO video). Tile rows are written to
 * picture rows 0, 2, 4, ..; between two written rows the row is the average of its
 * neighbours (p >> 1) + (q >> 1) per u32; an even height ends with a last tile row on
 * row h-1. Per tile: 0 + index (10/11/12 bits for ntiles < 0x400/0x800/0x1000), or
 * 1 + a vector: 1 = up; 01 + 2 bits; 00 + 4 bits (vec[] below, in tiles and tile rows);
 * the in-between row takes the up copy as is. */
static const int8_t vec2[4][2] = {{-1, 0}, {-1, -1}, {1, -1}, {0, -2}};
static const int8_t vec4[16][2] = {{-2, -3}, {2, -3}, {-1, -4}, {1, -4}, {-1, -2}, {1, -2},
                                   {0, -3}, {0, -4}, {-2, 0}, {-2, -1}, {2, -1}, {-2, -2},
                                   {2, -2}, {-1, -3}, {1, -3}, {0, -5}};

__declspec(dllexport) int ring_unr1_frame(const uint8_t *buf, size_t len, int ntiles,
                                          int limit, const uint8_t *tiles, uint32_t *out,
                                          int w, int h, uint32_t *endbit)
{
	bits_t b = {buf, len, 0, 0};
	const uint32_t *tt = (const uint32_t *)tiles;
	int nb = ntiles < 0x400 ? 10 : ntiles < 0x800 ? 11 : 12;
	int tw = w / 4, rows = (h >> 1) + 1, par = 1 - (h & 1);
	int mid = rows - par - 1;
	if (ntiles > 4095 || w % 4 || mid < 1)
		return -5;
	for (int r = 0; r < rows; r++) {
		/* row 0: plain; then mid rows two picture rows apart with an averaged row
		 * between; then (even height) the last one, plain, one picture row lower. */
		int kind = r == 0 ? 0 : r <= mid ? 1 : 2;
		int y = kind == 2 ? h - 1 : 2 * r;
		for (int c = 0; c < tw; c++) {
			int p = y * w + 4 * c, src, avg = 1;
			if (!msb(&b, 1)) {
				uint32_t idx = msb(&b, nb);
				if ((int)idx >= limit)
					return -2;
				for (int i = 0; i < 4; i++) {
					uint32_t v = tt[4 * idx + i];
					out[p + i] = v;
					if (kind == 1)
						out[p + i - w] = (v >> 1) + (out[p + i - 2 * w] >> 1);
				}
				continue;
			}
			int dx, dy;
			if (msb(&b, 1)) {
				dx = 0, dy = -1, avg = 0;
			} else if (msb(&b, 1)) {
				uint32_t k = msb(&b, 2);
				dx = vec2[k][0], dy = vec2[k][1];
			} else {
				uint32_t k = msb(&b, 4);
				dx = vec4[k][0], dy = vec4[k][1];
			}
			if (kind == 0 && dy)
				return -4;
			/* a tile row is two picture rows; the last row is one below the previous */
			src = p + 4 * dx + dy * 2 * w + (kind == 2 && dy ? w : 0);
			if (src < 0)
				return -3;
			for (int i = 0; i < 4; i++) {
				uint32_t v = out[src + i];
				out[p + i] = v;
				if (kind == 1)
					out[p + i - w] = avg ? (v >> 1) + (out[p + i - 2 * w] >> 1) : v;
			}
		}
	}
	*endbit = b.pos;
	return b.over ? -1 : 0;
}

/* v2 picture. First a map of u16 tile numbers (4-pixel tiles, w/4 per row, h rows, or
 * h/2+1 when interlaced), in groups of 8: 1 = the 8 entries above; 0 = 8 single entries,
 * each one of (bits in read order)
 *   1            the entry above
 *   000 + n      a new index of n = bit length of ntiles bits
 *   001 + d + s  above + d + 1 (s = 0) or above - d - 1 (s = 1), d 4 bits
 *   010          one of the left, up-left, up-right and up-up entries that differ from
 *                the one above, each value once (0, 1 or 2 bits for 1, 2 or 3-4 of them)
 *   011 + k      slot k + 1 (k 4 bits) of the above entry's history
 * Each entry except 1 and 011 is pushed on the history of the entry above it (16 slots,
 * cyclic, cleared per picture). The map ends after `rows` row ends, counted as the
 * original does: a group crosses at most one (col += 8, then col -= tw once), a single
 * entry ends a row when col reaches tw. Then every non-zero entry draws its tile; 0 leaves
 * the picture as it was. Interlaced: map rows go to picture rows 0, 2, ..; the row in
 * between becomes (below + new) >> 1 over each pixel pair as one 64-bit value, and an
 * even height ends with a plain row on h-1.
 * list: u16[4] kept between calls (the original's neighbour list buffer); *stale counts
 * choices past the candidates, which read what an earlier entry left there. */
__declspec(dllexport) int ring_unr2_frame(const uint8_t *buf, size_t len, int ntiles,
                                          int limit, const uint8_t *tiles, uint32_t *out,
                                          int w, int h,
                                          int interlaced, uint16_t *map, uint16_t *list,
                                          uint32_t *endbit, int *stale)
{
	static uint16_t hist[4096][17]; /* [0] = last slot written x 2, slots 1..16 */
	static int32_t mark[4096];
	bits_t b = {buf, len, 0, 0};
	const uint32_t *tt = (const uint32_t *)tiles;
	int nb = 0, tw = w / 4, rows = interlaced ? (h >> 1) + 1 : h;
	int mid = interlaced ? rows - (1 - (h & 1)) - 1 : 0;
	int t = 0, col = 0, left = tw * rows, total = tw * rows, over = -1;
	if (w % 4 || tw < 1 || rows < 1)
		return -5;
	for (int v = ntiles; v; v >>= 1)
		nb++;
	for (int i = 0; i < 4096; i++) {
		mark[i] = -1;
		for (int k = 0; k <= 16; k++)
			hist[i][k] = 0;
	}
	*stale = 0;
	while (left) {
		if (lsb(&b, 1)) {
			if (t < tw)
				return -3;
			for (int k = 0; k < 8; k++)
				map[t + k] = map[t + k - tw];
			t += 8, col += 8;
			if (t >= total && over < 0)
				*endbit = b.pos, over = b.over;
			if (col >= tw) {
				col -= tw;
				left -= tw;
			}
			continue;
		}
		for (int g = 0; g < 8 && left; g++) {
			int push = 1, v;
			uint16_t up = t >= tw ? map[t - tw] : 0;
			if (lsb(&b, 1)) {
				if (t < tw)
					return -3;
				v = up;
				push = 0;
			} else {
				int code = (int)lsb(&b, 2);
				if (code == 1) {
					/* the neighbours that differ from the one above, each once */
					int n = 0;
					int have[4] = {t >= 1 && col >= 1, t >= tw + 1 && col >= 1,
					               t >= tw - 1 && col <= tw - 2, t >= 2 * tw};
					int at[4] = {t - 1, t - tw - 1, t - tw + 1, t - 2 * tw};
					if (t >= tw)
						mark[up] = t;
					for (int k = 0; k < 4; k++)
						if (have[k] && mark[map[at[k]]] != t) {
							mark[map[at[k]]] = t;
							list[n++] = map[at[k]];
						}
					int pick = n == 1 ? 0 : n <= 2 ? (int)lsb(&b, 1) : (int)lsb(&b, 2);
					if (pick >= n)
						(*stale)++; /* the original reads a left-over list entry */
					v = list[pick];
				} else if (code == 3) {
					if (t < tw)
						return -3;
					v = hist[up][lsb(&b, 4) + 1];
					push = 0;
				} else if (code == 2) {
					if (t < tw)
						return -3;
					int d = (int)lsb(&b, 4);
					v = (uint16_t)(lsb(&b, 1) ? up - d - 1 : up + d + 1);
				} else {
					v = (int)lsb(&b, nb);
				}
			}
			if (v > 0xfff)
				return -2;
			map[t] = (uint16_t)v;
			if (push && t >= tw) {
				uint16_t *hh = hist[up];
				hh[0] = hh[0] + 2 == 0x20 ? 0 : hh[0] + 2;
				hh[hh[0] ? hh[0] / 2 : 16] = (uint16_t)v;
			}
			if (++t >= total && over < 0)
				*endbit = b.pos, over = b.over;
			if (++col >= tw) { /* below 8 tiles a row, a group's col can pass tw */
				col = 0;
				left -= tw;
			}
		}
	}
	/* Under 8 tiles a row the count runs past the map (entries never drawn), reading
	 * past the data; only the bits of the drawn entries must be there. */
	if (over)
		return -1;
	for (int r = 0, m = 0; r < rows; r++) {
		int kind = r == 0 || !interlaced ? 0 : r <= mid ? 1 : 2;
		int y = !interlaced ? r : kind == 2 ? h - 1 : 2 * r;
		for (int c = 0; c < tw; c++, m++) {
			uint16_t i = map[m];
			if (!i)
				continue;
			if (i >= limit)
				return -2;
			int p = y * w + 4 * c;
			for (int k = 0; k < 4; k++)
				out[p + k] = tt[4 * i + k];
			if (kind == 1)
				for (int k = 0; k < 4; k += 2) {
					/* (above + new) per dword, then the pair shifted right as a qword */
					uint32_t s0 = out[p + k] + out[p + k - 2 * w];
					uint32_t s1 = out[p + k + 1] + out[p + k + 1 - 2 * w];
					out[p + k - w] = s0 >> 1 | s1 << 31;
					out[p + k + 1 - w] = s1 >> 1;
				}
		}
	}
	return 0;
}
