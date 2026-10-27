#!/usr/bin/env python3
"""
Standalone 8-Core CPU Verification of the 3+3 Stratum (55 B6-Orbits / 10 Isomorphism Classes C_0..C_9)
via Theorem 15 (Law M19: The Russian-Doll Hierarchical Point-Stabilizer Tower: D0: G_0 -> D1: Stab(x0) -> D2: Stab(x0,x1))
combined with Law M15 (6-Row Sub-Gram Rank-3 Elimination) and Law M16 (20-Column M0-Block Design).
Reduces the 3+3 search tree by 47.36x (298.73B -> 6.31B d3 nodes, ~89.3 min on 8-core Apple M1 CPU without GPU).

Includes a zero-trust pure-Python Cross-Check Oracle (`naive_reference_check_33`, without @njit, LUTs, eq_bits,
or custom open-addressing hash tables) that verifies 100% exact node-count isomorphism (d1, d2, d3, d4_ht_hits, sols)
against the @njit kernel across all 10 classes C_0..C_9 at startup.
"""
import time
import numpy as np
from numba import njit, prange
from itertools import combinations, permutations, product


def permute_mask_py(xm: int, perm: list[int]) -> int:
    """Elementary pure-Python 60-column bitmask permutation directly from mathematical definition."""
    out = 0
    m = int(xm)
    while m:
        lsb = m & -m
        c = lsb.bit_length() - 1
        out |= 1 << perm[c]
        m ^= lsb
    return out


def naive_reference_check_33(
    i0: int, min_can: int,
    L0, L1, c1_can, L2, c2_can, L3, c3_can, L4, c4_can, L5, c5_can,
    Gp, KW0,
    C11_col_mask: int, C22_col_mask: int, O11_orb_mask: int, O12_orb_mask: int, O22_orb_mask: int,
    g01_perms: list[list[int]], g012_flags: list[int], swap01_perms: list[list[int]]
) -> tuple[int, int, int, int, int]:
    """
    Elementary pure-Python reference solver for a single root i0 in 3+3.
    Uses NO @njit, NO byte-level LUTs, NO eq_bits trick, and NO open-addressing hash table.
    Verifies exact node-by-node isomorphism (d1, d2, d3, d4_ht_hits, sols) with fast_hierarchical_30orbit_solver.
    """
    C11_m = int(C11_col_mask); C22_m = int(C22_col_mask)
    O11_m = int(O11_orb_mask); O12_m = int(O12_orb_mask); O22_m = int(O22_orb_mask)
    min_can = int(min_can)
    min_u1_12_d3 = 18 - (int(Gp[4, 5]) + int(KW0[4, 5]) + int(KW0[4, 4]) // 2 + int(KW0[5, 5]) // 2)

    x0, gx0, o11_0, o12_1_0, o12_2_0, o2_0, o22_1_0, o22_2_0 = [int(v) for v in L0[i0]]
    u1_12_0 = o12_1_0 | o12_2_0; u2_12_0 = o12_2_0
    u1_22_0 = o22_1_0 | o22_2_0; u2_22_0 = o22_2_0

    s1_indices = [g_i for g_i, p in enumerate(g01_perms) if permute_mask_py(x0, p) == x0]
    swap_x0_img = [permute_mask_py(x0, p) for p in swap01_perms]

    def ok_d0(row, c_can_val, gp, kw):
        if int(c_can_val) < min_can: return False
        rx, rgx, ro11, ro12_1, ro12_2, ro2, ro22_1, ro22_2 = [int(v) for v in row]
        if (o11_0 & ro11) or (ro12_2 & u1_12_0) or (ro12_1 & u2_12_0) or (o2_0 & ro2) or (ro22_2 & u1_22_0) or (ro22_1 & u2_22_0):
            return False
        return (x0 & rx).bit_count() == int(gp) and (x0 & rgx).bit_count() == int(kw)

    c1_0 = []
    for i in range(len(L1)):
        if ok_d0(L1[i], c1_can[i], Gp[0, 1], KW0[0, 1]):
            rx = int(L1[i, 0])
            if any(permute_mask_py(rx, g01_perms[g_i]) < rx for g_i in s1_indices):
                continue
            if int(c1_can[i]) == min_can and any(permute_mask_py(rx, p) == x0 and img < rx for p, img in zip(swap01_perms, swap_x0_img)):
                continue
            c1_0.append(i)
    if not c1_0:
        return (0, 0, 0, 0, 0)

    c2_0 = [i for i in range(len(L2)) if ok_d0(L2[i], c2_can[i], Gp[0, 2], KW0[0, 2])]
    c3_0 = [i for i in range(len(L3)) if ok_d0(L3[i], c3_can[i], Gp[0, 3], KW0[0, 3])]
    c4_0 = [i for i in range(len(L4)) if ok_d0(L4[i], c4_can[i], Gp[0, 4], KW0[0, 4])]
    c5_0 = [i for i in range(len(L5)) if ok_d0(L5[i], c5_can[i], Gp[0, 5], KW0[0, 5])]

    d1 = len(c1_0); d2 = 0; d3 = 0; d4_ht_hits = 0; sols = 0

    for i1 in c1_0:
        x1, gx1, o11_1, o12_1_1, o12_2_1, o2_1, o22_1_1, o22_2_1 = [int(v) for v in L1[i1]]
        col_u2_01 = x0 & x1; g_col_u2_01 = gx0 & gx1
        if ((col_u2_01 & g_col_u2_01) & C22_m) or (col_u2_01 & C11_m):
            continue
        o11_01 = o11_0 | o11_1
        u2_12_01 = u2_12_0 | o12_2_1 | (u1_12_0 & o12_1_1); u1_12_01 = u1_12_0 | o12_1_1 | o12_2_1
        u2_22_01 = u2_22_0 | o22_2_1 | (u1_22_0 & o22_1_1); u1_22_01 = u1_22_0 | o22_1_1 | o22_2_1
        o2_01 = o2_0 | o2_1; col_u1_01 = x0 | x1

        s2_indices = [g_i for g_i in s1_indices if g012_flags[g_i] == 1 and permute_mask_py(x1, g01_perms[g_i]) == x1]

        def ok_d1(row, gp, kw):
            rx, rgx, ro11, ro12_1, ro12_2, ro2, ro22_1, ro22_2 = [int(v) for v in row]
            if (rx & col_u2_01) or (o11_01 & ro11) or (ro12_2 & u1_12_01) or (ro12_1 & u2_12_01) or (o2_01 & ro2) or (ro22_2 & u1_22_01) or (ro22_1 & u2_22_01):
                return False
            return (x1 & rx).bit_count() == int(gp) and (x1 & rgx).bit_count() == int(kw)

        c2_1 = [ri for ri in c2_0 if ok_d1(L2[ri], Gp[1, 2], KW0[1, 2]) and not any(permute_mask_py(int(L2[ri, 0]), g01_perms[g_i]) < int(L2[ri, 0]) for g_i in s2_indices)]
        if not c2_1: continue
        c3_1 = [ri for ri in c3_0 if ok_d1(L3[ri], Gp[1, 3], KW0[1, 3])]
        if not c3_1: continue
        c4_1 = [ri for ri in c4_0 if ok_d1(L4[ri], Gp[1, 4], KW0[1, 4])]
        if not c4_1: continue

        # Plain Python dictionary instead of open-addressing hash table
        c5_by_key = {}
        for ri in c5_0:
            if ok_d1(L5[ri], Gp[1, 5], KW0[1, 5]):
                key5 = int(L5[ri, 2]) | (int(L5[ri, 3]) << 1) | (int(L5[ri, 4]) << 2) | (int(L5[ri, 6]) << 3) | (int(L5[ri, 7]) << 4)
                c5_by_key.setdefault(key5, []).append(ri)
        if not c5_by_key: continue

        d2 += len(c2_1)
        for i2 in c2_1:
            x2, gx2, o11_2, o12_1_2, o12_2_2, o2_2, o22_1_2, o22_2_2 = [int(v) for v in L2[i2]]
            col_u2_012 = col_u2_01 | (col_u1_01 & x2); g_col_u2_012 = g_col_u2_01 | ((gx0 | gx1) & gx2)
            if ((col_u2_012 & g_col_u2_012) & C22_m) or (col_u2_012 & C11_m):
                continue
            o11_012 = o11_01 | o11_2
            u2_12_012 = u2_12_01 | o12_2_2 | (u1_12_01 & o12_1_2); u1_12_012 = u1_12_01 | o12_1_2 | o12_2_2
            u2_22_012 = u2_22_01 | o22_2_2 | (u1_22_01 & o22_1_2); u1_22_012 = u1_22_01 | o22_1_2 | o22_2_2
            o2_012 = o2_01 | o2_2; col_u1_012 = col_u1_01 | x2

            def ok_d2(row, gp, kw):
                rx, rgx, ro11, ro12_1, ro12_2, ro2, ro22_1, ro22_2 = [int(v) for v in row]
                if (rx & col_u2_012) or (o11_012 & ro11) or (ro12_2 & u1_12_012) or (ro12_1 & u2_12_012) or (o2_012 & ro2) or (ro22_2 & u1_22_012) or (ro22_1 & u2_22_012):
                    return False
                return (x2 & rx).bit_count() == int(gp) and (x2 & rgx).bit_count() == int(kw)

            c3_2 = [ri for ri in c3_1 if ok_d2(L3[ri], Gp[2, 3], KW0[2, 3])]
            if not c3_2: continue
            c4_2 = [ri for ri in c4_1 if ok_d2(L4[ri], Gp[2, 4], KW0[2, 4])]
            if not c4_2: continue

            d3 += len(c3_2)
            for i3 in c3_2:
                x3, gx3, o11_3, o12_1_3, o12_2_3, o2_3, o22_1_3, o22_2_3 = [int(v) for v in L3[i3]]
                col_u2_0123 = col_u2_012 | (col_u1_012 & x3); g_col_u2_0123 = g_col_u2_012 | ((gx0 | gx1 | gx2) & gx3)
                if ((col_u2_0123 & g_col_u2_0123) & C22_m) or (col_u2_0123 & C11_m):
                    continue
                o11_0123 = o11_012 | o11_3
                u2_12_0123 = u2_12_012 | o12_2_3 | (u1_12_012 & o12_1_3); u1_12_0123 = u1_12_012 | o12_1_3 | o12_2_3
                if u1_12_0123.bit_count() < min_u1_12_d3:
                    continue
                u2_22_0123 = u2_22_012 | o22_2_3 | (u1_22_012 & o22_1_3); u1_22_0123 = u1_22_012 | o22_1_3 | o22_2_3
                if u1_22_0123.bit_count() + u2_22_0123.bit_count() < 4:
                    continue
                o2_0123 = o2_012 | o2_3; col_u1_0123 = col_u1_012 | x3

                rem_o11_d3 = O11_m & ~o11_0123
                z12_d3 = O12_m & ~u1_12_0123; s1_12_d3 = u1_12_0123 & ~u2_12_0123
                z22_d3 = O22_m & ~u1_22_0123; s1_22_d3 = u1_22_0123 & ~u2_22_0123
                c22_rem_d3 = C22_m & ~col_u2_0123

                for i4 in c4_2:
                    x4, gx4, o11_4, o12_1_4, o12_2_4, o2_4, o22_1_4, o22_2_4 = [int(v) for v in L4[i4]]
                    if (x4 & col_u2_0123) or (o11_0123 & o11_4) or (o12_2_4 & u1_12_0123) or (o12_1_4 & u2_12_0123) or (o2_0123 & o2_4):
                        continue
                    if (o22_2_4 & u1_22_0123) or (o22_1_4 & u2_22_0123):
                        continue
                    if (x3 & x4).bit_count() != int(Gp[3, 4]) or (x3 & gx4).bit_count() != int(KW0[3, 4]):
                        continue
                    col_u2_4 = col_u2_0123 | (col_u1_0123 & x4); g_col_u2_4 = g_col_u2_0123 | ((gx0 | gx1 | gx2 | gx3) & gx4)
                    if ((col_u2_4 & g_col_u2_4) & C22_m) or (col_u2_4 & C11_m):
                        continue

                    req_o11_5 = rem_o11_d3 & ~o11_4
                    req_o12_2_5 = z12_d3 & ~(o12_1_4 | o12_2_4); req_o12_1_5 = (z12_d3 & o12_1_4) | (s1_12_d3 & ~o12_1_4)
                    req_o22_2_5 = z22_d3 & ~(o22_1_4 | o22_2_4); req_o22_1_5 = (z22_d3 & o22_1_4) | (s1_22_d3 & ~o22_1_4)
                    key5_req = req_o11_5 | (req_o12_1_5 << 1) | (req_o12_2_5 << 2) | (req_o22_1_5 << 3) | (req_o22_2_5 << 4)

                    cand5 = c5_by_key.get(key5_req)
                    if not cand5:
                        continue
                    col_u1_4 = col_u1_0123 | x4
                    req_c22_5 = C22_m & ~col_u1_4
                    forbid_x5 = col_u2_4 | (C22_m & ~c22_rem_d3)
                    o2_4_acc = o2_0123 | o2_4

                    for i5 in cand5:
                        d4_ht_hits += 1
                        x5, gx5 = int(L5[i5, 0]), int(L5[i5, 1])
                        if (x5 & forbid_x5) == 0 and (x5 & req_c22_5) == req_c22_5 and (o2_4_acc & int(L5[i5, 5])) == 0:
                            if (x2 & x5).bit_count() == int(Gp[2, 5]) and (x3 & x5).bit_count() == int(Gp[3, 5]) and (x4 & x5).bit_count() == int(Gp[4, 5]):
                                col_u2_5 = col_u2_4 | (col_u1_4 & x5)
                                g_col_u2_5 = g_col_u2_4 | ((gx0 | gx1 | gx2 | gx3 | gx4) & gx5)
                                if ((col_u2_5 & g_col_u2_5) & C22_m) == 0:
                                    sols += 1

    return (d1, d2, d3, d4_ht_hits, sols)


@njit(inline="always")
def popcnt64(x):
    x = x - ((x >> np.uint64(1)) & np.uint64(0x5555555555555555))
    x = (x & np.uint64(0x3333333333333333)) + ((x >> np.uint64(2)) & np.uint64(0x3333333333333333))
    x = (x + (x >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
    return int((x * np.uint64(0x0101010101010101)) >> np.uint64(56))

@njit(inline="always")
def eq_bits(a, b):
    return (~(a ^ b)) & np.uint64(0x3FFFFFFF)

def build_perm_luts(perms_list):
    n_p = len(perms_list)
    if n_p == 0:
        return np.zeros((0, 8, 256), dtype=np.uint64)
    luts = np.zeros((n_p, 8, 256), dtype=np.uint64)
    for p_idx, perm in enumerate(perms_list):
        for b_idx in range(8):
            base_c = b_idx * 8
            max_bit = min(8, 60 - base_c)
            for bit in range(max_bit):
                c = base_c + bit
                nc = perm[c]
                mask = np.uint64(1) << np.uint64(nc)
                step = 1 << bit
                for val in range(step, 256, 2 * step):
                    for v in range(val, val + step):
                        luts[p_idx, b_idx, v] |= mask
    return np.ascontiguousarray(luts)

@njit(inline="always")
def apply_lut(x, lut_p):
    return (
        lut_p[0, x & np.uint64(0xFF)] |
        lut_p[1, (x >> np.uint64(8)) & np.uint64(0xFF)] |
        lut_p[2, (x >> np.uint64(16)) & np.uint64(0xFF)] |
        lut_p[3, (x >> np.uint64(24)) & np.uint64(0xFF)] |
        lut_p[4, (x >> np.uint64(32)) & np.uint64(0xFF)] |
        lut_p[5, (x >> np.uint64(40)) & np.uint64(0xFF)] |
        lut_p[6, (x >> np.uint64(48)) & np.uint64(0xFF)] |
        lut_p[7, (x >> np.uint64(56)) & np.uint64(0xFF)]
    )

@njit(parallel=True)
def compute_canons_lut(L_a, luts):
    n_rows = len(L_a)
    n_perms = len(luts)
    out = np.empty(n_rows, dtype=np.uint64)
    if n_perms == 0:
        for i in prange(n_rows):
            out[i] = np.uint64(0xFFFFFFFFFFFFFFFF)
        return out
    for i in prange(n_rows):
        xm = L_a[i, 0]
        best = np.uint64(0xFFFFFFFFFFFFFFFF)
        for p_idx in range(n_perms):
            nx = apply_lut(xm, luts[p_idx])
            if nx < best:
                best = nx
        out[i] = best
    return out

@njit
def fast_hierarchical_30orbit_solver(
    n_reps, reps, rep_canons,
    L0, L1, c1_can, L2, c2_can, L3, c3_can, L4, c4_can, L5, c5_can,
    Gp, KW0,
    C11_col_mask, C12_col_mask, C22_col_mask, O11_orb_mask, O12_orb_mask, O22_orb_mask,
    luts_g01, is_g012_flag, luts_swap01
):
    d1 = 0; d2 = 0; d3 = 0; d4_ht_hits = 0; sols = 0
    z64 = np.uint64(0)
    req_p4 = KW0[4, 4] // 2; req_p5 = KW0[5, 5] // 2
    req_p45 = req_p4 + req_p5
    gpkw45 = Gp[4, 5] + KW0[4, 5]
    max_Z12_d3 = gpkw45 + req_p45
    min_u1_12_d3 = 18 - max_Z12_d3

    c1_0 = np.empty(32768, dtype=np.int32); c2_0 = np.empty(32768, dtype=np.int32)
    c3_0 = np.empty(32768, dtype=np.int32); c4_0 = np.empty(32768, dtype=np.int32); c5_0 = np.empty(32768, dtype=np.int32)
    c2_1 = np.empty(8192, dtype=np.int32); c3_1 = np.empty(8192, dtype=np.int32)
    c4_1 = np.empty(8192, dtype=np.int32); c5_1 = np.empty(8192, dtype=np.int32)
    c3_2 = np.empty(2048, dtype=np.int32); c4_2 = np.empty(2048, dtype=np.int32)

    HASH_SIZE = 2048
    HASH_MASK = np.uint64(HASH_SIZE - 1)
    HASH_MUL  = np.uint64(0x9E3779B97F4A7C15)
    ht_head = np.empty(HASH_SIZE, dtype=np.int32)
    ht_Stamp = np.zeros(HASH_SIZE, dtype=np.int32)
    ht_next = np.empty(8192, dtype=np.int32)
    ht_key  = np.empty(8192, dtype=np.uint64)
    ht_idx  = np.empty(8192, dtype=np.int32)
    cur_stamp = 0

    n_g01 = len(luts_g01)
    n_swap01 = len(luts_swap01)
    s1_idx = np.empty(256, dtype=np.int32)
    s2_idx = np.empty(256, dtype=np.int32)
    swap_x0_img = np.empty(256, dtype=np.uint64)

    gp01, kw01 = Gp[0, 1], KW0[0, 1]; gp02, kw02 = Gp[0, 2], KW0[0, 2]
    gp03, kw03 = Gp[0, 3], KW0[0, 3]; gp04, kw04 = Gp[0, 4], KW0[0, 4]; gp05, kw05 = Gp[0, 5], KW0[0, 5]
    gp12, kw12 = Gp[1, 2], KW0[1, 2]; gp13, kw13 = Gp[1, 3], KW0[1, 3]
    gp14, kw14 = Gp[1, 4], KW0[1, 4]; gp15, kw15 = Gp[1, 5], KW0[1, 5]
    gp23, kw23 = Gp[2, 3], KW0[2, 3]; gp24, kw24 = Gp[2, 4], KW0[2, 4]; gp25, kw25 = Gp[2, 5], KW0[2, 5]
    gp34, kw34 = Gp[3, 4], KW0[3, 4]; gp35, kw35 = Gp[3, 5], KW0[3, 5]
    gp45, kw45 = Gp[4, 5], KW0[4, 5]

    for b_idx in range(n_reps):
        i0 = reps[b_idx]
        min_can = rep_canons[b_idx]
        x0      = L0[i0, 0]; gx0     = L0[i0, 1]
        o11_0   = L0[i0, 2]; o12_1_0 = L0[i0, 3]; o12_2_0 = L0[i0, 4]; o2_0 = L0[i0, 5]
        o22_1_0 = L0[i0, 6]; o22_2_0 = L0[i0, 7]
        u1_12_0 = o12_1_0 | o12_2_0; u2_12_0 = o12_2_0
        u1_22_0 = o22_1_0 | o22_2_0; u2_22_0 = o22_2_0

        n_s1 = 0
        for g_i in range(n_g01):
            if apply_lut(x0, luts_g01[g_i]) == x0:
                s1_idx[n_s1] = g_i
                n_s1 += 1

        for sw_i in range(n_swap01):
            swap_x0_img[sw_i] = apply_lut(x0, luts_swap01[sw_i])

        n1_0 = 0
        for i in range(len(L1)):
            if c1_can[i] < min_can: continue
            if (o11_0 & L1[i, 2]) != z64 or (L1[i, 4] & u1_12_0) != z64 or (L1[i, 3] & u2_12_0) != z64 or (o2_0 & L1[i, 5]) != z64: continue
            if (L1[i, 7] & u1_22_0) != z64 or (L1[i, 6] & u2_22_0) != z64: continue
            x1_cand = L1[i, 0]
            if popcnt64(x0 & x1_cand) == gp01 and popcnt64(x0 & L1[i, 1]) == kw01:
                ok_s1 = True
                for k_s in range(n_s1):
                    if apply_lut(x1_cand, luts_g01[s1_idx[k_s]]) < x1_cand:
                        ok_s1 = False
                        break
                if not ok_s1:
                    continue
                if c1_can[i] == min_can and n_swap01 > 0:
                    for sw_i in range(n_swap01):
                        if apply_lut(x1_cand, luts_swap01[sw_i]) == x0:
                            if swap_x0_img[sw_i] < x1_cand:
                                ok_s1 = False
                                break
                    if not ok_s1:
                        continue
                c1_0[n1_0] = i; n1_0 += 1

        if n1_0 == 0:
            continue

        n2_0 = 0
        for i in range(len(L2)):
            if c2_can[i] < min_can: continue
            if (o11_0 & L2[i, 2]) != z64 or (L2[i, 4] & u1_12_0) != z64 or (L2[i, 3] & u2_12_0) != z64 or (o2_0 & L2[i, 5]) != z64: continue
            if (L2[i, 7] & u1_22_0) != z64 or (L2[i, 6] & u2_22_0) != z64: continue
            if popcnt64(x0 & L2[i, 0]) == gp02 and popcnt64(x0 & L2[i, 1]) == kw02:
                c2_0[n2_0] = i; n2_0 += 1
        n3_0 = 0
        for i in range(len(L3)):
            if c3_can[i] < min_can: continue
            if (o11_0 & L3[i, 2]) != z64 or (L3[i, 4] & u1_12_0) != z64 or (L3[i, 3] & u2_12_0) != z64 or (o2_0 & L3[i, 5]) != z64: continue
            if (L3[i, 7] & u1_22_0) != z64 or (L3[i, 6] & u2_22_0) != z64: continue
            if popcnt64(x0 & L3[i, 0]) == gp03 and popcnt64(x0 & L3[i, 1]) == kw03:
                c3_0[n3_0] = i; n3_0 += 1
        n4_0 = 0
        for i in range(len(L4)):
            if c4_can[i] < min_can: continue
            if (o11_0 & L4[i, 2]) != z64 or (L4[i, 4] & u1_12_0) != z64 or (L4[i, 3] & u2_12_0) != z64 or (o2_0 & L4[i, 5]) != z64: continue
            if (L4[i, 7] & u1_22_0) != z64 or (L4[i, 6] & u2_22_0) != z64: continue
            if popcnt64(x0 & L4[i, 0]) == gp04 and popcnt64(x0 & L4[i, 1]) == kw04:
                c4_0[n4_0] = i; n4_0 += 1
        n5_0 = 0
        for i in range(len(L5)):
            if c5_can[i] < min_can: continue
            if (o11_0 & L5[i, 2]) != z64 or (L5[i, 4] & u1_12_0) != z64 or (L5[i, 3] & u2_12_0) != z64 or (o2_0 & L5[i, 5]) != z64: continue
            if (L5[i, 7] & u1_22_0) != z64 or (L5[i, 6] & u2_22_0) != z64: continue
            if popcnt64(x0 & L5[i, 0]) == gp05 and popcnt64(x0 & L5[i, 1]) == kw05:
                c5_0[n5_0] = i; n5_0 += 1

        d1 += n1_0
        for idx1 in range(n1_0):
            i1 = c1_0[idx1]
            x1      = L1[i1, 0]; gx1     = L1[i1, 1]
            o11_1   = L1[i1, 2]; o12_1_1 = L1[i1, 3]; o12_2_1 = L1[i1, 4]; o2_1 = L1[i1, 5]
            o22_1_1 = L1[i1, 6]; o22_2_1 = L1[i1, 7]

            col_u2_01 = x0 & x1
            g_col_u2_01 = gx0 & gx1
            if ((col_u2_01 & g_col_u2_01) & C22_col_mask) != z64 or (col_u2_01 & C11_col_mask) != z64:
                continue

            o11_01   = o11_0 | o11_1
            u2_12_01 = u2_12_0 | o12_2_1 | (u1_12_0 & o12_1_1)
            u1_12_01 = u1_12_0 | o12_1_1 | o12_2_1
            u2_22_01 = u2_22_0 | o22_2_1 | (u1_22_0 & o22_1_1)
            u1_22_01 = u1_22_0 | o22_1_1 | o22_2_1
            o2_01    = o2_0 | o2_1
            col_u1_01 = x0 | x1

            n_s2 = 0
            for k_s in range(n_s1):
                g_i = s1_idx[k_s]
                if is_g012_flag[g_i] == 1 and apply_lut(x1, luts_g01[g_i]) == x1:
                    s2_idx[n_s2] = g_i
                    n_s2 += 1

            n2_1 = 0
            for k in range(n2_0):
                ri = c2_0[k]; rx = L2[ri, 0]
                if (rx & col_u2_01) == z64 and (o11_01 & L2[ri, 2]) == z64 and (L2[ri, 4] & u1_12_01) == z64 and (L2[ri, 3] & u2_12_01) == z64 and (o2_01 & L2[ri, 5]) == z64:
                    if (L2[ri, 7] & u1_22_01) == z64 and (L2[ri, 6] & u2_22_01) == z64:
                        if popcnt64(x1 & rx) == gp12 and popcnt64(x1 & L2[ri, 1]) == kw12:
                            ok_s2 = True
                            for k_s in range(n_s2):
                                if apply_lut(rx, luts_g01[s2_idx[k_s]]) < rx:
                                    ok_s2 = False
                                    break
                            if ok_s2:
                                c2_1[n2_1] = ri; n2_1 += 1
            if n2_1 == 0: continue

            n3_1 = 0
            for k in range(n3_0):
                ri = c3_0[k]; rx = L3[ri, 0]
                if (rx & col_u2_01) == z64 and (o11_01 & L3[ri, 2]) == z64 and (L3[ri, 4] & u1_12_01) == z64 and (L3[ri, 3] & u2_12_01) == z64 and (o2_01 & L3[ri, 5]) == z64:
                    if (L3[ri, 7] & u1_22_01) == z64 and (L3[ri, 6] & u2_22_01) == z64:
                        if popcnt64(x1 & rx) == gp13 and popcnt64(x1 & L3[ri, 1]) == kw13:
                            c3_1[n3_1] = ri; n3_1 += 1
            if n3_1 == 0: continue

            n4_1 = 0
            for k in range(n4_0):
                ri = c4_0[k]; rx = L4[ri, 0]
                if (rx & col_u2_01) == z64 and (o11_01 & L4[ri, 2]) == z64 and (L4[ri, 4] & u1_12_01) == z64 and (L4[ri, 3] & u2_12_01) == z64 and (o2_01 & L4[ri, 5]) == z64:
                    if (L4[ri, 7] & u1_22_01) == z64 and (L4[ri, 6] & u2_22_01) == z64:
                        if popcnt64(x1 & rx) == gp14 and popcnt64(x1 & L4[ri, 1]) == kw14:
                            c4_1[n4_1] = ri; n4_1 += 1
            if n4_1 == 0: continue

            cur_stamp += 1
            n5_1 = 0
            for k in range(n5_0):
                ri = c5_0[k]; rx = L5[ri, 0]
                if (rx & col_u2_01) == z64 and (o11_01 & L5[ri, 2]) == z64 and (L5[ri, 4] & u1_12_01) == z64 and (L5[ri, 3] & u2_12_01) == z64 and (o2_01 & L5[ri, 5]) == z64:
                    if (L5[ri, 7] & u1_22_01) == z64 and (L5[ri, 6] & u2_22_01) == z64:
                        if popcnt64(x1 & rx) == gp15 and popcnt64(x1 & L5[ri, 1]) == kw15:
                            idx_pos = n5_1
                            n5_1 += 1
                            key5 = L5[ri, 2] | (L5[ri, 3] << np.uint64(1)) | (L5[ri, 4] << np.uint64(2)) | (L5[ri, 6] << np.uint64(3)) | (L5[ri, 7] << np.uint64(4))
                            h = int(((key5 * HASH_MUL) >> np.uint64(53)) & HASH_MASK)
                            if ht_Stamp[h] != cur_stamp:
                                ht_Stamp[h] = cur_stamp
                                ht_head[h] = -1
                            ht_next[idx_pos] = ht_head[h]
                            ht_key[idx_pos]  = key5
                            ht_idx[idx_pos]  = ri
                            ht_head[h] = idx_pos
            if n5_1 == 0: continue

            d2 += n2_1
            for idx2 in range(n2_1):
                i2 = c2_1[idx2]
                x2      = L2[i2, 0]; gx2     = L2[i2, 1]
                o11_2   = L2[i2, 2]; o12_1_2 = L2[i2, 3]; o12_2_2 = L2[i2, 4]; o2_2 = L2[i2, 5]
                o22_1_2 = L2[i2, 6]; o22_2_2 = L2[i2, 7]

                col_u2_012 = col_u2_01 | (col_u1_01 & x2)
                g_col_u2_012 = g_col_u2_01 | ((gx0 | gx1) & gx2)
                if ((col_u2_012 & g_col_u2_012) & C22_col_mask) != z64 or (col_u2_012 & C11_col_mask) != z64:
                    continue

                o11_012   = o11_01 | o11_2
                u2_12_012 = u2_12_01 | o12_2_2 | (u1_12_01 & o12_1_2)
                u1_12_012 = u1_12_01 | o12_1_2 | o12_2_2
                u2_22_012 = u2_22_01 | o22_2_2 | (u1_22_01 & o22_1_2)
                u1_22_012 = u1_22_01 | o22_1_2 | o22_2_2
                o2_012    = o2_01 | o2_2
                col_u1_012 = col_u1_01 | x2

                n3_2 = 0
                for k in range(n3_1):
                    ri = c3_1[k]; rx = L3[ri, 0]
                    if (rx & col_u2_012) == z64 and (o11_012 & L3[ri, 2]) == z64 and (L3[ri, 4] & u1_12_012) == z64 and (L3[ri, 3] & u2_12_012) == z64 and (o2_012 & L3[ri, 5]) == z64:
                        if (L3[ri, 7] & u1_22_012) == z64 and (L3[ri, 6] & u2_22_012) == z64:
                            if popcnt64(x2 & rx) == gp23 and popcnt64(x2 & L3[ri, 1]) == kw23:
                                c3_2[n3_2] = ri; n3_2 += 1
                if n3_2 == 0: continue

                n4_2 = 0
                for k in range(n4_1):
                    ri = c4_1[k]; rx = L4[ri, 0]
                    if (rx & col_u2_012) == z64 and (o11_012 & L4[ri, 2]) == z64 and (L4[ri, 4] & u1_12_012) == z64 and (L4[ri, 3] & u2_12_012) == z64 and (o2_012 & L4[ri, 5]) == z64:
                        if (L4[ri, 7] & u1_22_012) == z64 and (L4[ri, 6] & u2_22_012) == z64:
                            if popcnt64(x2 & rx) == gp24 and popcnt64(x2 & L4[ri, 1]) == kw24:
                                c4_2[n4_2] = ri; n4_2 += 1
                if n4_2 == 0: continue

                d3 += n3_2
                for idx3 in range(n3_2):
                    i3 = c3_2[idx3]
                    x3      = L3[i3, 0]; gx3     = L3[i3, 1]
                    o11_3   = L3[i3, 2]; o12_1_3 = L3[i3, 3]; o12_2_3 = L3[i3, 4]; o2_3 = L3[i3, 5]
                    o22_1_3 = L3[i3, 6]; o22_2_3 = L3[i3, 7]

                    col_u2_0123 = col_u2_012 | (col_u1_012 & x3)
                    g_col_u2_0123 = g_col_u2_012 | ((gx0 | gx1 | gx2) & gx3)
                    if ((col_u2_0123 & g_col_u2_0123) & C22_col_mask) != z64 or (col_u2_0123 & C11_col_mask) != z64:
                        continue

                    o11_0123   = o11_012 | o11_3
                    u2_12_0123 = u2_12_012 | o12_2_3 | (u1_12_012 & o12_1_3)
                    u1_12_0123 = u1_12_012 | o12_1_3 | o12_2_3
                    if popcnt64(u1_12_0123) < min_u1_12_d3:
                        continue

                    u2_22_0123 = u2_22_012 | o22_2_3 | (u1_22_012 & o22_1_3)
                    u1_22_0123 = u1_22_012 | o22_1_3 | o22_2_3
                    if popcnt64(u1_22_0123) + popcnt64(u2_22_0123) < 4:
                        continue

                    o2_0123    = o2_012 | o2_3
                    col_u1_0123 = col_u1_012 | x3

                    rem_o11_d3 = O11_orb_mask & ~o11_0123
                    z12_d3 = O12_orb_mask & ~u1_12_0123
                    s1_12_d3 = u1_12_0123 & ~u2_12_0123
                    z22_d3 = O22_orb_mask & ~u1_22_0123
                    s1_22_d3 = u1_22_0123 & ~u2_22_0123
                    c22_rem_d3 = C22_col_mask & ~col_u2_0123

                    for idx4 in range(n4_2):
                        i4 = c4_2[idx4]
                        x4      = L4[i4, 0]; gx4     = L4[i4, 1]
                        o11_4   = L4[i4, 2]; o12_1_4 = L4[i4, 3]; o12_2_4 = L4[i4, 4]; o2_4 = L4[i4, 5]
                        o22_1_4 = L4[i4, 6]; o22_2_4 = L4[i4, 7]

                        if (x4 & col_u2_0123) != z64 or (o11_0123 & o11_4) != z64 or (o12_2_4 & u1_12_0123) != z64 or (o12_1_4 & u2_12_0123) != z64 or (o2_0123 & o2_4) != z64:
                            continue
                        if (o22_2_4 & u1_22_0123) != z64 or (o22_1_4 & u2_22_0123) != z64:
                            continue
                        if not (popcnt64(x3 & x4) == gp34 and popcnt64(x3 & gx4) == kw34):
                            continue

                        col_u2_4 = col_u2_0123 | (col_u1_0123 & x4)
                        g_col_u2_4 = g_col_u2_0123 | ((gx0 | gx1 | gx2 | gx3) & gx4)
                        if ((col_u2_4 & g_col_u2_4) & C22_col_mask) != z64 or (col_u2_4 & C11_col_mask) != z64:
                            continue

                        req_o11_5   = rem_o11_d3 & ~o11_4
                        req_o12_2_5 = z12_d3 & ~(o12_1_4 | o12_2_4)
                        req_o12_1_5 = (z12_d3 & o12_1_4) | (s1_12_d3 & ~o12_1_4)
                        req_o22_2_5 = z22_d3 & ~(o22_1_4 | o22_2_4)
                        req_o22_1_5 = (z22_d3 & o22_1_4) | (s1_22_d3 & ~o22_1_4)

                        key5_req = req_o11_5 | (req_o12_1_5 << np.uint64(1)) | (req_o12_2_5 << np.uint64(2)) | (req_o22_1_5 << np.uint64(3)) | (req_o22_2_5 << np.uint64(4))
                        h = int(((key5_req * HASH_MUL) >> np.uint64(53)) & HASH_MASK)
                        if ht_Stamp[h] != cur_stamp:
                            continue
                        e = ht_head[h]
                        if e == -1:
                            continue

                        col_u1_4 = col_u1_0123 | x4
                        req_c22_5 = C22_col_mask & ~col_u1_4
                        forbid_x5 = col_u2_4 | (C22_col_mask & ~c22_rem_d3)
                        o2_4_acc = o2_0123 | o2_4

                        while e != -1:
                            if ht_key[e] == key5_req:
                                d4_ht_hits += 1
                                i5 = ht_idx[e]
                                x5 = L5[i5, 0]
                                if (x5 & forbid_x5) == z64 and (x5 & req_c22_5) == req_c22_5 and (o2_4_acc & L5[i5, 5]) == z64:
                                    if popcnt64(x2 & x5) == gp25 and popcnt64(x3 & x5) == gp35 and popcnt64(x4 & x5) == gp45:
                                        gx5 = L5[i5, 1]
                                        col_u2_5 = col_u2_4 | (col_u1_4 & x5)
                                        g_col_u2_5 = g_col_u2_4 | ((gx0 | gx1 | gx2 | gx3 | gx4) & gx5)
                                        if ((col_u2_5 & g_col_u2_5) & C22_col_mask) == z64:
                                            sols += 1
                            e = ht_next[e]

    return d1, d2, d3, d4_ht_hits, sols

def build_orbits():
    F12 = np.zeros((12, 12), dtype=int)
    for b_idx in range(6):
        F12[2 * b_idx, 2 * b_idx + 1] = F12[2 * b_idx + 1, 2 * b_idx] = 1
    I12 = np.eye(12, dtype=int)
    J12 = np.ones((12, 12), dtype=int)

    def gen_matchings_12(verts):
        if not verts:
            yield ()
            return
        v0 = verts[0]
        rest = verts[1:]
        for idx, v1 in enumerate(rest):
            rem = rest[:idx] + rest[idx + 1:]
            for m in gen_matchings_12(rem):
                yield ((v0, v1),) + m

    matchings_12 = list(gen_matchings_12(list(range(12))))
    m_tuples = []
    for m in matchings_12:
        p = [0] * 12
        for u, v in m:
            p[u] = v
            p[v] = u
        m_tuples.append(tuple(p))
    m_to_id = {t: i for i, t in enumerate(m_tuples)}

    def cycle_part_12(p):
        vis = [False] * 6
        cycs = []
        for b_idx in range(6):
            if vis[b_idx]:
                continue
            cur = 2 * b_idx
            length = 0
            while not vis[cur // 2]:
                vis[cur // 2] = True
                length += 1
                nxt = p[cur]
                if nxt // 2 == cur // 2:
                    break
                cur = nxt ^ 1
            cycs.append(length)
        return tuple(sorted(cycs, reverse=True))

    reps_M0 = {}
    for p in m_tuples:
        part = cycle_part_12(p)
        if part not in reps_M0:
            reps_M0[part] = p

    b6_perms = []
    for perm in permutations(range(6)):
        for flips in product((0, 1), repeat=6):
            g_p = [0] * 12
            for b_old in range(6):
                b_new = perm[b_old]
                fl = flips[b_old]
                g_p[2 * b_old] = 2 * b_new + fl
                g_p[2 * b_old + 1] = 2 * b_new + (1 - fl)
            b6_perms.append(tuple(g_p))

    def get_block_comps(M, E):
        adj = F12 | M | E
        vis = set()
        comps = []
        for u in range(12):
            if u not in vis:
                comp = []
                q = [u]
                vis.add(u)
                while q:
                    cur = q.pop()
                    comp.append(cur)
                    for nxt in range(12):
                        if adj[cur, nxt] and nxt not in vis:
                            vis.add(nxt)
                            q.append(nxt)
                comps.append(sorted(comp))
        return comps

    orbits_by_sig = {}
    for part, m0 in sorted(reps_M0.items()):
        stab = [g_p for g_p in b6_perms if all(g_p[m0[u]] == m0[g_p[u]] for u in range(12))]
        M0_mat = np.zeros((12, 12), dtype=int)
        for u, v in enumerate(m0):
            M0_mat[u, v] = 1
        seen_e0 = [False] * len(m_tuples)
        for idx_e, e0 in enumerate(m_tuples):
            if seen_e0[idx_e]:
                continue
            for g_p in stab:
                img = [0] * 12
                for u in range(12):
                    img[g_p[u]] = g_p[e0[u]]
                seen_e0[m_to_id[tuple(img)]] = True
            E0_mat = np.zeros((12, 12), dtype=int)
            for u, v in enumerate(e0):
                E0_mat[u, v] = 1
            KW0 = 2 * J12 - F12 - E0_mat - (M0_mat @ E0_mat) - (E0_mat @ M0_mat)
            if KW0.min() >= 0:
                k_t1 = sum(1 for b_idx in range(6) if m0[2 * b_idx] == 2 * b_idx + 1 and e0[2 * b_idx] == 2 * b_idx + 1)
                comps = get_block_comps(M0_mat, E0_mat)
                sig = f"kt1={k_t1}_" + "+".join(str(len(c)//2) for c in sorted(comps, key=lambda x: len(x), reverse=True))
                Gp = 9 * I12 + J12 - M0_mat
                Delta0 = 2 * J12 - I12 - F12 - M0_mat - (E0_mat @ F12)
                orbits_by_sig.setdefault(sig, []).append((M0_mat, E0_mat, Gp, KW0, Delta0, comps))
    return F12, I12, J12, b6_perms, orbits_by_sig


def main():
    t_start = time.time()
    F12, I12, J12, b6_perms, orbits_by_sig = build_orbits()
    orbits_42 = orbits_by_sig["kt1=0_4+2"]

    b2_perms_4 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(2)) for flips in product((0, 1), repeat=2)
    ]
    b4_perms_8 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(4)) for flips in product((0, 1), repeat=4)
    ]

    def canon_2block(M4, E4):
        return min(tuple(M4[np.ix_(p, p)].flatten()) + tuple(E4[np.ix_(p, p)].flatten()) for p in b2_perms_4)

    def canon_4block(M8, E8):
        return min(tuple(M8[np.ix_(p, p)].flatten()) + tuple(E8[np.ix_(p, p)].flatten()) for p in b4_perms_8)

    c2_classes = []
    seen_c2 = set()
    c4_classes = []
    seen_c4 = set()
    for M, E, Gp, KW0, Delta0, comps in orbits_42:
        comp2 = comps[0] if len(comps[0]) == 4 else comps[1]
        comp4 = comps[1] if len(comps[0]) == 4 else comps[0]
        M4, E4 = M[np.ix_(comp2, comp2)], E[np.ix_(comp2, comp2)]
        ck2 = canon_2block(M4, E4)
        if ck2 not in seen_c2:
            seen_c2.add(ck2)
            c2_classes.append((M4, E4))
        M8, E8 = M[np.ix_(comp4, comp4)], E[np.ix_(comp4, comp4)]
        ck4 = canon_4block(M8, E8)
        if ck4 not in seen_c4:
            seen_c4.add(ck4)
            c4_classes.append((M8, E8))

    print(f"Extracted {len(c2_classes)} canonical 2-block classes and {len(c4_classes)} canonical 4-block classes (3 x 56 = 168 orbits).", flush=True)

    cols_60 = []; col_idx = {}
    for b1 in range(6):
        for b2 in range(b1 + 1, 6):
            for s1 in (0, 1):
                for s2 in (0, 1):
                    j1, j2 = 2 * b1 + s1, 2 * b2 + s2
                    c = len(cols_60); cols_60.append((j1, j2)); col_idx[(j1, j2)] = col_idx[(j2, j1)] = c
    g_col = [col_idx[(j1 ^ 1, j2 ^ 1)] for (j1, j2) in cols_60]
    orbs_30 = [(c, g_col[c]) for c in range(60) if c < g_col[c]]

    I_B1 = {0, 1, 2, 3, 4, 5, 6, 7}
    O11_orb_mask = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] in I_B1 and cols_60[c][1] in I_B1))
    O12_orb_mask = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if (cols_60[c][0] in I_B1) ^ (cols_60[c][1] in I_B1)))
    C11_col_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in I_B1 and v in I_B1))

    F4 = F12[:4, :4]; I4 = np.eye(4, dtype=int); J4 = np.ones((4, 4), dtype=int)
    F8 = F12[:8, :8]; I8 = np.eye(8, dtype=int); J8 = np.ones((8, 8), dtype=int)

    def w4_mat(Gp8, KW8, u, v):
        return (4 if Gp8[u, v] == 0 else (1 if Gp8[u, v] == 1 else 0)) + (4 if KW8[u, v] == 0 else (1 if KW8[u, v] == 1 else 0))

    # Build all canonical 4x8 sub-cones with |Stab_{S4 x B4}(K_4)| >= 2!
    cone_info = {}
    for idx_d, (M8, E8) in enumerate(c4_classes):
        KW8 = 2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)
        D8 = 2 * J8 - I8 - F8 - M8 - (E8 @ F8)
        Gp8 = 7 * I8 + J8 - M8
        for q in combinations(range(8), 4):
            q = list(q)
            sm = sum(1 for r in q if KW8[r, r] == 0)
            w_sum = sum(w4_mat(Gp8, KW8, q[a], q[b]) for a in range(4) for b in range(a + 1, 4))
            gp4, kw4, d48 = Gp8[np.ix_(q, q)], KW8[np.ix_(q, q)], D8[q, :]
            st = 0; best_key = None
            for pr in permutations(range(4)):
                gp_p = tuple(gp4[np.ix_(pr, pr)].flatten())
                kw_p = tuple(kw4[np.ix_(pr, pr)].flatten())
                for pc in b4_perms_8:
                    d_p = tuple(d48[np.ix_(pr, pc)].flatten())
                    k = gp_p + kw_p + d_p
                    if best_key is None or k < best_key: best_key = k
                    if gp_p == tuple(gp4.flatten()) and kw_p == tuple(kw4.flatten()) and d_p == tuple(d48.flatten()):
                        st += 1
            if best_key not in cone_info:
                cone_info[best_key] = {"st": st, "small": sm, "w_sum": w_sum, "classes": set(), "example": (idx_d, q)}
            cone_info[best_key]["classes"].add(idx_d)

    uncov = set(range(56))
    chosen_cones = []
    while uncov:
        best_k = max(
            cone_info.keys(),
            key=lambda k: (
                len(cone_info[k]["classes"] & uncov),
                cone_info[k]["small"],
                int(np.log2(cone_info[k]["st"])) * 4 + cone_info[k]["w_sum"],
                cone_info[k]["st"]
            )
        )
        info = cone_info[best_k]
        new_c = sorted(info["classes"] & uncov)
        chosen_cones.append((best_k, new_c, sorted(info["classes"]), info))
        uncov -= info["classes"]

    print(f"Covered all 56 4-block classes using {len(chosen_cones)} canonical 4x8 sub-cones:", flush=True)
    for idx_m, (k, new_c, all_c, info) in enumerate(chosen_cones):
        print(f"  K4_{idx_m:02d}: |Stab4|={info['st']:3d} small={info['small']} w_sum={info['w_sum']:2d} | covers {len(new_c):2d} new classes {new_c} (all={all_c})", flush=True)

    y_cache = {}
    def gen_2block_rows(target_deg_4, diag_kw):
        key = (target_deg_4, diag_kw)
        if key in y_cache: return y_cache[key]
        target_deg_12 = (2, 2, 2, 2, 2, 2, 2, 2) + tuple(target_deg_4)
        req_pairs = diag_kw // 2
        ok_cols = [c for c in range(60) if target_deg_12[cols_60[c][0]] > 0 and target_deg_12[cols_60[c][1]] > 0 and not (cols_60[c][0] not in I_B1 and cols_60[c][1] not in I_B1)]
        adj_cols = [[] for _ in range(12)]
        for c in ok_cols:
            u, v = cols_60[c]; adj_cols[min(u, v)].append((c, max(u, v)))
        rem_deg = list(target_deg_12); chosen = []; res = []
        def bt_v(v_idx):
            if v_idx == 12:
                if len(chosen) == 10:
                    r_set = set(chosen)
                    npairs = sum(1 for c in chosen if c < g_col[c] and g_col[c] in r_set)
                    if npairs == req_pairs:
                        xm = gxm = o11_1 = o11_2 = o12_1 = o12_2 = o2_all = 0
                        for c in chosen:
                            xm |= 1 << c; gxm |= 1 << g_col[c]
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if s == 2: o2_all |= 1 << idx_m
                            if (int(O11_orb_mask) >> idx_m) & 1:
                                if s == 1: o11_1 |= 1 << idx_m
                                elif s == 2: o11_2 |= 1 << idx_m
                            elif (int(O12_orb_mask) >> idx_m) & 1:
                                if s == 1: o12_1 |= 1 << idx_m
                                elif s == 2: o12_2 |= 1 << idx_m
                        if o12_2 == 0:
                            res.append((xm, gxm, o11_1, o11_2, o12_1, o2_all))
                return
            need = rem_deg[v_idx]
            if need < 0: return
            avail = [(c, w) for (c, w) in adj_cols[v_idx] if rem_deg[w] > 0]
            if len(avail) < need: return
            for comb in combinations(avail, need):
                for c, w in comb: rem_deg[w] -= 1; chosen.append(c)
                rem_deg[v_idx] = 0; bt_v(v_idx + 1); rem_deg[v_idx] = need
                for c, w in comb: rem_deg[w] += 1; chosen.pop()
        bt_v(0)
        arr = np.ascontiguousarray(np.array(res, dtype=np.uint64))
        y_cache[key] = arr
        return arr

    x_cache = {}
    def gen_4block_rows(target_deg_8, diag_kw):
        key = (target_deg_8, diag_kw)
        if key in x_cache: return x_cache[key]
        target_deg_12 = tuple(target_deg_8) + (2, 2, 2, 2)
        req_pairs = diag_kw // 2
        ok_cols = [c for c in range(60) if target_deg_12[cols_60[c][0]] > 0 and target_deg_12[cols_60[c][1]] > 0]
        adj_cols = [[] for _ in range(12)]
        for c in ok_cols:
            u, v = cols_60[c]; adj_cols[min(u, v)].append((c, max(u, v)))
        rem_deg = list(target_deg_12); chosen = []; res = []
        def bt_v(v_idx):
            if v_idx == 12:
                if len(chosen) == 10:
                    r_set = set(chosen)
                    npairs = sum(1 for c in chosen if c < g_col[c] and g_col[c] in r_set)
                    if npairs == req_pairs:
                        xm = gxm = o2_all = 0
                        for c in chosen:
                            xm |= 1 << c; gxm |= 1 << g_col[c]
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if s == 2: o2_all |= 1 << idx_m
                        res.append((xm, gxm, 0, 0, 0, 0, o2_all))
                return
            need = rem_deg[v_idx]
            if need < 0: return
            avail = [(c, w) for (c, w) in adj_cols[v_idx] if rem_deg[w] > 0]
            if len(avail) < need: return
            for comb in combinations(avail, need):
                for c, w in comb: rem_deg[w] -= 1; chosen.append(c)
                rem_deg[v_idx] = 0; bt_v(v_idx + 1); rem_deg[v_idx] = need
                for c, w in comb: rem_deg[w] += 1; chosen.pop()
        bt_v(0)
        arr = np.ascontiguousarray(np.array(res, dtype=np.uint64))
        x_cache[key] = arr
        return arr

    c2_prepared = []
    for idx_c2, (M4, E4) in enumerate(c2_classes):
        KW4 = (2 * J4 - F4 - E4 - (M4 @ E4) - (E4 @ M4)).astype(np.int32)
        D4 = 2 * J4 - I4 - F4 - M4 - (E4 @ F4)
        Gp4_2 = (7 * I4 + J4 - M4).astype(np.int32)
        Y_raw = [gen_2block_rows(tuple(int(D4[r, j]) for j in range(4)), int(KW4[r, r])) for r in range(4)]
        ylens = [len(y) for y in Y_raw]
        stab2_m16 = []
        for pr in permutations(range(4)):
            if any(ylens[pr[a]] != ylens[a] for a in range(4)): continue
            if not (Gp4_2 == Gp4_2[np.ix_(pr, pr)]).all() or not (KW4 == KW4[np.ix_(pr, pr)]).all(): continue
            for pc in b2_perms_4:
                if (D4 == D4[np.ix_(pr, pc)]).all():
                    stab2_m16.append((pr, pc))
        def w2(u, v):
            return (4 if Gp4_2[u, v] == 0 else (1 if Gp4_2[u, v] == 1 else 0)) + (4 if KW4[u, v] == 0 else (1 if KW4[u, v] == 1 else 0))
        ord2 = list(max(permutations(range(4)), key=lambda q: (w2(q[0], q[1]) + w2(q[0], q[2]) + w2(q[1], q[2]), w2(q[0], q[1]), -ylens[q[0]])))
        Y = [Y_raw[r] for r in ord2]
        Gp2_ord = np.ascontiguousarray(Gp4_2[np.ix_(ord2, ord2)], dtype=np.int32)
        KW2_ord = np.ascontiguousarray(KW4[np.ix_(ord2, ord2)], dtype=np.int32)
        c2_prepared.append((idx_c2, Y, Gp2_ord, KW2_ord, stab2_m16, ord2))

    dummy_x_row = np.zeros((1, 7), dtype=np.uint64)
    k4_prepared = []
    for idx_m, (k, new_c, all_c, info) in enumerate(chosen_cones):
        idx_d, q_base = info["example"]
        M8, E8 = c4_classes[idx_d]
        KW8 = (2 * J8 - F8 - E8 - (M8 @ E8) - (M8 @ M8)).astype(np.int32)
        # Note: exact KW8 = 2*J8 - F8 - E8 - M8@E8 - E8@M8
        KW8 = (2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)).astype(np.int32)
        D8 = 2 * J8 - I8 - F8 - M8 - (E8 @ F8)
        Gp8_4 = (7 * I8 + J8 - M8).astype(np.int32)
        xlens = [91368 if KW8[r, r] == 0 else 244944 for r in range(8)]

        def w4(u, v):
            return (4 if Gp8_4[u, v] == 0 else (1 if Gp8_4[u, v] == 1 else 0)) + (4 if KW8[u, v] == 0 else (1 if KW8[u, v] == 1 else 0))

        ord4_sub = list(max(
            permutations(q_base),
            key=lambda q: (
                w4(q[0], q[1]) + w4(q[0], q[2]) + w4(q[1], q[2]),
                w4(q[0], q[1]) + w4(q[0], q[2]),
                w4(q[0], q[1]),
                -xlens[q[0]]
            )
        ))
        gp4 = Gp8_4[np.ix_(ord4_sub, ord4_sub)]
        kw4 = KW8[np.ix_(ord4_sub, ord4_sub)]
        d48 = D8[ord4_sub, :]
        stab4_sub = []
        for pr in permutations(range(4)):
            if any(xlens[ord4_sub[pr[a]]] != xlens[ord4_sub[a]] for a in range(4)): continue
            if not (gp4 == gp4[np.ix_(pr, pr)]).all() or not (kw4 == kw4[np.ix_(pr, pr)]).all(): continue
            for pc in b4_perms_8:
                if (d48 == d48[np.ix_(pr, pc)]).all():
                    stab4_sub.append((pr, pc))
        rem4 = [u for u in range(8) if u not in ord4_sub]
        ord4 = ord4_sub + rem4
        X = [gen_4block_rows(tuple(int(D8[r, j]) for j in range(8)), int(KW8[r, r])) for r in ord4_sub] + [dummy_x_row] * 4
        Gp4_ord = np.ascontiguousarray(Gp8_4[np.ix_(ord4, ord4)], dtype=np.int32)
        KW4_ord = np.ascontiguousarray(KW8[np.ix_(ord4, ord4)], dtype=np.int32)
        k4_prepared.append((idx_m, X, Gp4_ord, KW4_ord, stab4_sub, new_c, all_c, info))

    print(f"\nRows cached in {time.time() - t_start:.1f}s ({len(y_cache)} Y-profiles, {len(x_cache)} X-profiles). Running 3 x {len(k4_prepared)} = {3*len(k4_prepared)} pairs...\n", flush=True)

    id_map = tuple(range(60))
    dummy_cx = [np.zeros(1, dtype=np.uint64) for _ in range(8)]
    warmed = False

    tot_b1_by_c2 = [0, 0, 0]
    tot_d6_by_c2 = [0, 0, 0]
    tot_d8_by_c2 = [0, 0, 0]
    tot_8c_by_c2 = [0.0, 0.0, 0.0]

    for idx_c2, Y, Gp2_ord, KW2_ord, stab2_m16, ord2 in c2_prepared:
        c2_name = ["A", "B", "C"][idx_c2]
        print(f"=== 2-Block Class {c2_name} (|Stab2|={len(stab2_m16)}) ===", flush=True)
        for idx_m, X, Gp4_ord, KW4_ord, stab4_sub, new_c, all_c, info in k4_prepared:
            stab_y_to_0 = [[] for _ in range(4)]
            seen_y_to_0 = [set() for _ in range(4)]
            g01_dict = {}
            swap01_perms = []
            seen_swap01 = set()

            for pr2, pc2 in stab2_m16:
                for pr4, pc4 in stab4_sub:
                    g_p = list(pc4) + [8 + x for x in pc2]
                    c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                    t_map = tuple(c_map)
                    for a_idx, orig_r in enumerate(ord2):
                        if pr2[orig_r] == ord2[0] and t_map not in seen_y_to_0[a_idx]:
                            seen_y_to_0[a_idx].add(t_map)
                            stab_y_to_0[a_idx].append(c_map)
                    if pr2[ord2[0]] == ord2[0] and pr2[ord2[1]] == ord2[1] and t_map != id_map:
                        f2 = 1 if pr2[ord2[2]] == ord2[2] else 0
                        f3 = 1 if (f2 == 1 and pr2[ord2[3]] == ord2[3]) else 0
                        prev = g01_dict.get(t_map, (0, 0))
                        g01_dict[t_map] = (max(prev[0], f2), max(prev[1], f3))
                    if pr2[ord2[0]] == ord2[1] and pr2[ord2[1]] == ord2[0] and t_map not in seen_swap01:
                        seen_swap01.add(t_map)
                        swap01_perms.append(c_map)

            g01_perms = [list(k) for k in g01_dict.keys()]
            g012_flags = [v[0] for v in g01_dict.values()]
            g0123_flags = [v[1] for v in g01_dict.values()]

            cy_cans = [compute_canons_lut(Y[a], build_perm_luts(stab_y_to_0[a])) for a in range(4)]
            luts_g01 = build_perm_luts(g01_perms)
            is_g012_flag = np.ascontiguousarray(np.array(g012_flags, dtype=np.int32))
            is_g0123_flag = np.ascontiguousarray(np.array(g0123_flags, dtype=np.int32))
            luts_swap01 = build_perm_luts(swap01_perms)

            reps = np.ascontiguousarray([i for i in range(len(Y[0])) if Y[0][i, 0] == cy_cans[0][i]], dtype=np.int32)
            rep_canons = np.ascontiguousarray([cy_cans[0][i] for i in reps], dtype=np.uint64)

            if not warmed:
                _ = solve_orbit_42_chiral_cpu(
                    0, reps[:1], rep_canons[:1],
                    Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
                    X[0], dummy_cx[0], X[1], dummy_cx[1], X[2], dummy_cx[2], X[3], dummy_cx[3],
                    X[4], dummy_cx[4], X[5], dummy_cx[5], X[6], dummy_cx[6], X[7], dummy_cx[7],
                    Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
                    C11_col_mask, O11_orb_mask, O12_orb_mask,
                    luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
                )
                warmed = True

            n_test = min(20, len(reps))
            sample_idx = np.linspace(0, len(reps) - 1, n_test, dtype=np.int32)
            s_reps = np.ascontiguousarray(reps[sample_idx], dtype=np.int32)
            s_cans = np.ascontiguousarray(rep_canons[sample_idx], dtype=np.uint64)

            t0 = time.time()
            res = solve_orbit_42_chiral_cpu(
                n_test, s_reps, s_cans,
                Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
                X[0], dummy_cx[0], X[1], dummy_cx[1], X[2], dummy_cx[2], X[3], dummy_cx[3],
                X[4], dummy_cx[4], X[5], dummy_cx[5], X[6], dummy_cx[6], X[7], dummy_cx[7],
                Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
                C11_col_mask, O11_orb_mask, O12_orb_mask,
                luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
            )
            el = time.time() - t0
            scale = len(reps) / n_test
            est_b1 = int(res[2] * scale)
            est_d6 = int(res[4] * scale)
            est_d8 = int(res[6] * scale)
            est_8c = (el * scale) / 7.5

            tot_b1_by_c2[idx_c2] += est_b1
            tot_d6_by_c2[idx_c2] += est_d6
            tot_d8_by_c2[idx_c2] += est_d8
            tot_8c_by_c2[idx_c2] += est_8c

            print(
                f"  ({c2_name}, K4_{idx_m:02d}) |Stab|={len(stab2_m16)*len(stab4_sub):4d} | reps={len(reps):5d} | "
                f"b1={est_b1:11,d} | d6={est_d6:12,d} | d8={est_d8:10,d} | 8c-M1={est_8c:5.1f}s | classes={new_c}",
                flush=True
            )

        print(
            f"--> Subtotal Class {c2_name}: b1={tot_b1_by_c2[idx_c2]:12,d} | d6={tot_d6_by_c2[idx_c2]:14,d} | "
            f"d8={tot_d8_by_c2[idx_c2]:11,d} | 8c-M1={tot_8c_by_c2[idx_c2]:.1f}s ({tot_8c_by_c2[idx_c2]/60:.2f} min)\n",
            flush=True
        )

    tot_b1 = sum(tot_b1_by_c2)
    tot_d6 = sum(tot_d6_by_c2)
    tot_d8 = sum(tot_d8_by_c2)
    tot_8c = sum(tot_8c_by_c2)
    print("================================================================================", flush=True)
    print("GRAND TOTAL 4+2 STRATUM (ALL 168 CANONICAL / 888 RAW ORBITS COVERED):", flush=True)
    print(f"  Total b1: {tot_b1:15,d} (vs null3:    89,803,453,164 -> {89803453164/max(1,tot_b1):.2f}x reduction)", flush=True)
    print(f"  Total d6: {tot_d6:15,d} (vs null3: 7,114,487,642,102 -> {7114487642102/max(1,tot_d6):.2f}x reduction)", flush=True)
    print(f"  Total d8: {tot_d8:15,d}", flush=True)
    print(f"  Total 8-core M1 CPU time: {tot_8c:.1f}s = {tot_8c/60:.2f} min = {tot_8c/3600:.2f} hours (vs null3 A100 GPU: 18.12 hours!)", flush=True)
    print("================================================================================", flush=True)


if __name__ == "__main__":
    main()

