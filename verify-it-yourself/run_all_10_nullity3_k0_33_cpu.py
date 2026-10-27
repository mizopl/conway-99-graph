#!/usr/bin/env python3
"""
Standalone 8-Core CPU Verification of the 3+3 Stratum (55 B6-Orbits / 10 Isomorphism Classes C_0..C_9)
via Theorem 15 (Law M19: The Russian-Doll Hierarchical Point-Stabilizer Tower: D0: G_0 -> D1: Stab(x0) -> D2: Stab(x0,x1))
combined with Law M15 (6-Row Sub-Gram Rank-3 Elimination) and Law M16 (20-Column M0-Block Design).
Reduces the 3+3 search tree by 47.36x (298.73B -> 6.31B d3 nodes, ~89.3 min on 8-core Apple M1 CPU without GPU).
"""
import time
import numpy as np
from numba import njit, prange
from itertools import combinations, permutations, product

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

        # Active stabilizer S1(x0) in G_{0,1}:
        n_s1 = 0
        for g_i in range(n_g01):
            if apply_lut(x0, luts_g01[g_i]) == x0:
                s1_idx[n_s1] = g_i
                n_s1 += 1

        # Images of x0 under swap(0, 1) automorphisms:
        for sw_i in range(n_swap01):
            swap_x0_img[sw_i] = apply_lut(x0, luts_swap01[sw_i])

        n1_0 = 0
        for i in range(len(L1)):
            if c1_can[i] < min_can: continue
            if (o11_0 & L1[i, 2]) != z64 or (L1[i, 4] & u1_12_0) != z64 or (L1[i, 3] & u2_12_0) != z64 or (o2_0 & L1[i, 5]) != z64: continue
            if (L1[i, 7] & u1_22_0) != z64 or (L1[i, 6] & u2_22_0) != z64: continue
            x1_cand = L1[i, 0]
            if eq_bits(x0 & x1_cand, gp01) and eq_bits(x0 & L1[i, 1], kw01):
                # Quotient c1_0 by S1(x0): require x1_cand <= g(x1_cand) for all g in S1(x0)!
                ok_s1 = True
                for k_s in range(n_s1):
                    if apply_lut(x1_cand, luts_g01[s1_idx[k_s]]) < x1_cand:
                        ok_s1 = False
                        break
                if not ok_s1:
                    continue
                # Also if any g in swap(0,1) maps x1_cand -> x0, then g(x0) is the swapped partner in L1!
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
            if eq_bits(x0 & L2[i, 0], gp02) and eq_bits(x0 & L2[i, 1], kw02):
                c2_0[n2_0] = i; n2_0 += 1
        n3_0 = 0
        for i in range(len(L3)):
            if c3_can[i] < min_can: continue
            if (o11_0 & L3[i, 2]) != z64 or (L3[i, 4] & u1_12_0) != z64 or (L3[i, 3] & u2_12_0) != z64 or (o2_0 & L3[i, 5]) != z64: continue
            if (L3[i, 7] & u1_22_0) != z64 or (L3[i, 6] & u2_22_0) != z64: continue
            if eq_bits(x0 & L3[i, 0], gp03) and eq_bits(x0 & L3[i, 1], kw03):
                c3_0[n3_0] = i; n3_0 += 1
        n4_0 = 0
        for i in range(len(L4)):
            if c4_can[i] < min_can: continue
            if (o11_0 & L4[i, 2]) != z64 or (L4[i, 4] & u1_12_0) != z64 or (L4[i, 3] & u2_12_0) != z64 or (o2_0 & L4[i, 5]) != z64: continue
            if (L4[i, 7] & u1_22_0) != z64 or (L4[i, 6] & u2_22_0) != z64: continue
            if eq_bits(x0 & L4[i, 0], gp04) and eq_bits(x0 & L4[i, 1], kw04):
                c4_0[n4_0] = i; n4_0 += 1
        n5_0 = 0
        for i in range(len(L5)):
            if c5_can[i] < min_can: continue
            if (o11_0 & L5[i, 2]) != z64 or (L5[i, 4] & u1_12_0) != z64 or (L5[i, 3] & u2_12_0) != z64 or (o2_0 & L5[i, 5]) != z64: continue
            if (L5[i, 7] & u1_22_0) != z64 or (L5[i, 6] & u2_22_0) != z64: continue
            if eq_bits(x0 & L5[i, 0], gp05) and eq_bits(x0 & L5[i, 1], kw05):
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

            # Active joint stabilizer S2(x0, x1) in G_{0,1,2}:
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
                        if eq_bits(x1 & rx, gp12) and eq_bits(x1 & L2[ri, 1], kw12):
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
                        if eq_bits(x1 & rx, gp13) and eq_bits(x1 & L3[ri, 1], kw13):
                            c3_1[n3_1] = ri; n3_1 += 1
            if n3_1 == 0: continue

            n4_1 = 0
            for k in range(n4_0):
                ri = c4_0[k]; rx = L4[ri, 0]
                if (rx & col_u2_01) == z64 and (o11_01 & L4[ri, 2]) == z64 and (L4[ri, 4] & u1_12_01) == z64 and (L4[ri, 3] & u2_12_01) == z64 and (o2_01 & L4[ri, 5]) == z64:
                    if (L4[ri, 7] & u1_22_01) == z64 and (L4[ri, 6] & u2_22_01) == z64:
                        if eq_bits(x1 & rx, gp14) and eq_bits(x1 & L4[ri, 1], kw14):
                            c4_1[n4_1] = ri; n4_1 += 1
            if n4_1 == 0: continue

            cur_stamp += 1
            n5_1 = 0
            for k in range(n5_0):
                ri = c5_0[k]; rx = L5[ri, 0]
                if (rx & col_u2_01) == z64 and (o11_01 & L5[ri, 2]) == z64 and (L5[ri, 4] & u1_12_01) == z64 and (L5[ri, 3] & u2_12_01) == z64 and (o2_01 & L5[ri, 5]) == z64:
                    if (L5[ri, 7] & u1_22_01) == z64 and (L5[ri, 6] & u2_22_01) == z64:
                        if eq_bits(x1 & rx, gp15) and eq_bits(x1 & L5[ri, 1], kw15):
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
                            if eq_bits(x2 & rx, gp23) and eq_bits(x2 & L3[ri, 1], kw23):
                                c3_2[n3_2] = ri; n3_2 += 1
                if n3_2 == 0: continue

                n4_2 = 0
                for k in range(n4_1):
                    ri = c4_1[k]; rx = L4[ri, 0]
                    if (rx & col_u2_012) == z64 and (o11_012 & L4[ri, 2]) == z64 and (L4[ri, 4] & u1_12_012) == z64 and (L4[ri, 3] & u2_12_012) == z64 and (o2_012 & L4[ri, 5]) == z64:
                        if (L4[ri, 7] & u1_22_012) == z64 and (L4[ri, 6] & u2_22_012) == z64:
                            if eq_bits(x2 & rx, gp24) and eq_bits(x2 & L4[ri, 1], kw24):
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
                        if not (eq_bits(x3 & x4, gp34) and eq_bits(x3 & gx4, kw34)):
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
                                    if eq_bits(x2 & x5, gp25) and eq_bits(x3 & x5, gp35) and eq_bits(x4 & x5, gp45):
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
    F12, I12, J12, b6_perms, orbits_by_sig = build_orbits()
    orbits_33 = orbits_by_sig["kt1=0_3+3"]
    b3_perms_6 = []
    for bp in permutations(range(3)):
        for flips in product((0, 1), repeat=3):
            p = []
            for b_new, fl in zip(bp, flips):
                p.extend([2 * b_new + fl, 2 * b_new + (1 - fl)])
            b3_perms_6.append(tuple(p))

    def canon_3block(M6, E6):
        return min(tuple(M6[np.ix_(p, p)].flatten()) + tuple(E6[np.ix_(p, p)].flatten()) for p in b3_perms_6)

    c3_classes = []
    seen_c3 = set()
    for M, E, Gp, KW0, Delta0, comps in orbits_33:
        for comp in comps:
            M6 = M[np.ix_(comp, comp)]
            E6 = E[np.ix_(comp, comp)]
            ck = canon_3block(M6, E6)
            if ck not in seen_c3:
                seen_c3.add(ck)
                c3_classes.append((M6, E6))

    cols_60 = []; col_idx = {}
    for b1 in range(6):
        for b2 in range(b1 + 1, 6):
            for s1 in (0, 1):
                for s2 in (0, 1):
                    j1, j2 = 2 * b1 + s1, 2 * b2 + s2
                    c = len(cols_60); cols_60.append((j1, j2)); col_idx[(j1, j2)] = col_idx[(j2, j1)] = c
    g_col = [col_idx[(j1 ^ 1, j2 ^ 1)] for (j1, j2) in cols_60]
    orbs_30 = [(c, g_col[c]) for c in range(60) if c < g_col[c]]
    I_B1 = {0, 1, 2, 3, 4, 5}
    O11_orb_mask = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] in I_B1 and cols_60[c][1] in I_B1))
    O12_orb_mask = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if (cols_60[c][0] in I_B1) ^ (cols_60[c][1] in I_B1)))
    O22_orb_mask = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] not in I_B1 and cols_60[c][1] not in I_B1))
    C11_col_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in I_B1 and v in I_B1))
    C12_col_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in I_B1) ^ (v in I_B1)))
    C22_col_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u not in I_B1 and v not in I_B1))

    row_3block_cache = {}
    def gen_3block_rows_cached(target_deg_tuple, diag_kw):
        key = (target_deg_tuple, diag_kw)
        if key in row_3block_cache: return row_3block_cache[key]
        req_pairs = diag_kw // 2
        ok_cols = [c for c in range(60) if target_deg_tuple[cols_60[c][0]] > 0 and target_deg_tuple[cols_60[c][1]] > 0]
        adj_cols = [[] for _ in range(12)]
        for c in ok_cols:
            u, v = cols_60[c]; adj_cols[min(u, v)].append((c, max(u, v)))
        rem_deg = list(target_deg_tuple); chosen = []; res = []
        def bt_v(v_idx):
            if v_idx == 12:
                if len(chosen) == 10:
                    r_set = set(chosen); npairs = 0; ok_p = True
                    for c in chosen:
                        if c < g_col[c] and g_col[c] in r_set:
                            npairs += 1
                            if cols_60[c][0] in I_B1 and cols_60[c][1] in I_B1: ok_p = False; break
                    if ok_p and npairs == req_pairs:
                        xm = gxm = o11_1 = o12_1 = o12_2 = o2_all = o22_1 = o22_2 = 0
                        for c in chosen: xm |= 1 << c; gxm |= 1 << g_col[c]
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if s == 2: o2_all |= 1 << idx_m
                            if (int(O11_orb_mask) >> idx_m) & 1:
                                if s == 1: o11_1 |= 1 << idx_m
                            elif (int(O12_orb_mask) >> idx_m) & 1:
                                if s == 1: o12_1 |= 1 << idx_m
                                elif s == 2: o12_2 |= 1 << idx_m
                            else:
                                if s == 1: o22_1 |= 1 << idx_m
                                elif s == 2: o22_2 |= 1 << idx_m
                        res.append((xm, gxm, o11_1, o12_1, o12_2, o2_all, o22_1, o22_2))
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
        row_3block_cache[key] = arr
        return arr

    F6 = np.zeros((6, 6), dtype=int)
    for b_idx in range(3): F6[2 * b_idx, 2 * b_idx + 1] = F6[2 * b_idx + 1, 2 * b_idx] = 1
    I6 = np.eye(6, dtype=int); J6 = np.ones((6, 6), dtype=int)

    null3_ref = {
        0: (1883,   5900867589,   41.92),
        1: (1883,   9455757514,  118.09),
        2: (1883,   9651663607,  131.35),
        3: (1883,  17313046504,  124.03),
        4: (1883,    625280236,   16.69),
        5: (1883,   8073886820,   63.60),
        6: (1883,   9199567252,   83.77),
        7: (3366,  21554004006,  290.21),
        8: (2123,  72094506824,  689.27),
        9: (4459, 144858407154, 2898.76),
    }

    print("=" * 126, flush=True)
    print("ALL 10 CLASSES (C_0..C_9) — HIERARCHICAL STABILIZER QUOTIENT (D0 + D1 Stab(x0) + D2 Stab(x0,x1)) + Law M15 + M16", flush=True)
    print("=" * 126, flush=True)

    tot_est_d3 = 0
    tot_ref_d3 = 0
    tot_est_8core_s = 0.0
    tot_ref_a100_s = 0.0

    for idx_c in range(10):
        M6, E6 = c3_classes[idx_c]
        KW6 = (2 * J6 - F6 - E6 - (M6 @ E6) - (E6 @ M6)).astype(np.int32)
        Delta6 = 2 * J6 - I6 - F6 - M6 - (E6 @ F6)
        Gp6 = (9 * I6 + J6 - M6 - 2 * I6).astype(np.int32)
        L_raw = [gen_3block_rows_cached(tuple(int(Delta6[i, j]) for j in range(6)) + (2, 2, 2, 2, 2, 2), int(KW6[i, i])) for i in range(6)]
        lens = [len(x) for x in L_raw]

        stab_m16 = []
        for p_row in permutations(range(6)):
            if not (KW6 == KW6[np.ix_(p_row, p_row)]).all(): continue
            if not (Gp6 == Gp6[np.ix_(p_row, p_row)]).all(): continue
            for p_col1 in b3_perms_6:
                if (Delta6 == Delta6[np.ix_(p_row, p_col1)]).all():
                    stab_m16.append((p_row, p_col1))

        best_ord = None
        best_sc = None
        for p in permutations(range(6)):
            def w_pair(u, v):
                w = 0
                if Gp6[u, v] == 0: w += 4
                elif Gp6[u, v] == 1: w += 1
                if KW6[u, v] == 0: w += 4
                elif KW6[u, v] == 1: w += 1
                return w
            z2 = w_pair(p[0], p[1])
            z3 = z2 + sum(w_pair(p[a], p[2]) for a in range(2))
            z4 = z3 + sum(w_pair(p[a], p[3]) for a in range(3))
            max_z12 = Gp6[p[4], p[5]] + KW6[p[4], p[5]] + (KW6[p[4], p[4]] // 2) + (KW6[p[5], p[5]] // 2)
            stab_r0 = max(1, sum(1 for (pr, pc) in stab_m16 if pr[p[0]] == p[0]))
            est_reps = lens[p[0]] // stab_r0
            sc = (-est_reps, z4, z3, z2, -lens[p[1]], -max_z12, -sum(lens[p[a]] for a in range(4)))
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best_ord = list(p)

        L = [L_raw[r] for r in best_ord]
        Gp_ord = np.ascontiguousarray(Gp6[np.ix_(best_ord, best_ord)], dtype=np.int32)
        KW_ord = np.ascontiguousarray(KW6[np.ix_(best_ord, best_ord)], dtype=np.int32)

        stab_a_to_0 = [[] for _ in range(6)]
        g01_perms = []
        g012_flags = []
        swap01_perms = []

        for p_row, p_col1 in stab_m16:
            for p2 in b3_perms_6:
                g_p = list(p_col1) + [6 + x for x in p2]
                c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                for a_idx, orig_r in enumerate(best_ord):
                    if p_row[orig_r] == best_ord[0]:
                        stab_a_to_0[a_idx].append(c_map)
                if p_row[best_ord[0]] == best_ord[0] and p_row[best_ord[1]] == best_ord[1]:
                    g01_perms.append(c_map)
                    g012_flags.append(1 if p_row[best_ord[2]] == best_ord[2] else 0)
                if p_row[best_ord[0]] == best_ord[1] and p_row[best_ord[1]] == best_ord[0]:
                    swap01_perms.append(c_map)

        c_cans = []
        for a in range(6):
            luts_a = build_perm_luts(stab_a_to_0[a])
            c_cans.append(compute_canons_lut(L[a], luts_a))

        luts_g01 = build_perm_luts(g01_perms)
        is_g012_flag = np.ascontiguousarray(np.array(g012_flags, dtype=np.int32))
        luts_swap01 = build_perm_luts(swap01_perms)

        reps = np.ascontiguousarray([i for i in range(len(L[0])) if L[0][i, 0] == c_cans[0][i]], dtype=np.int32)
        rep_canons = np.ascontiguousarray([c_cans[0][i] for i in reps], dtype=np.uint64)

        # Warmup JIT on 0 reps on first iteration
        if idx_c == 0:
            _ = fast_hierarchical_30orbit_solver(
                0, reps[:1], rep_canons[:1],
                L[0], L[1], c_cans[1], L[2], c_cans[2], L[3], c_cans[3], L[4], c_cans[4], L[5], c_cans[5],
                Gp_ord, KW_ord,
                C11_col_mask, C12_col_mask, C22_col_mask, O11_orb_mask, O12_orb_mask, O22_orb_mask,
                luts_g01, is_g012_flag, luts_swap01
            )

        n_test = min(20, len(reps))
        sample_idx = np.linspace(0, len(reps) - 1, n_test, dtype=np.int32)
        s_reps = np.ascontiguousarray(reps[sample_idx], dtype=np.int32)
        s_cans = np.ascontiguousarray(rep_canons[sample_idx], dtype=np.uint64)

        t0 = time.time()
        d1, d2, d3, d4_hits, sols = fast_hierarchical_30orbit_solver(
            n_test, s_reps, s_cans,
            L[0], L[1], c_cans[1], L[2], c_cans[2], L[3], c_cans[3], L[4], c_cans[4], L[5], c_cans[5],
            Gp_ord, KW_ord,
            C11_col_mask, C12_col_mask, C22_col_mask, O11_orb_mask, O12_orb_mask, O22_orb_mask,
            luts_g01, is_g012_flag, luts_swap01
        )
        el = time.time() - t0
        scale = len(reps) / n_test
        est_d3 = int(d3 * scale)
        est_1core_s = el * scale
        est_8core_s = est_1core_s / 7.5
        ref_reps, ref_d3, ref_a100_s = null3_ref[idx_c]
        d3_red = ref_d3 / max(1, est_d3)

        tot_est_d3 += est_d3
        tot_ref_d3 += ref_d3
        tot_est_8core_s += est_8core_s
        tot_ref_a100_s += ref_a100_s

        print(
            f"C_{idx_c}: ord={best_ord} | G01={len(g01_perms):3d} | reps={len(reps):4d} | "
            f"20-unif d3={d3:8d} ({el:5.2f}s) | Est Total d3={est_d3:12,d} (null3:{ref_d3:15,d} -> {d3_red:5.1f}x less!) | "
            f"8-core M1={est_8core_s:5.1f}s (A100:{ref_a100_s:6.1f}s)",
            flush=True
        )

    print("=" * 126, flush=True)
    print(f"TOTAL 3+3 (C_0..C_9): Est d3 = {tot_est_d3:,} vs null3 d3 = {tot_ref_d3:,} ({tot_ref_d3 / max(1, tot_est_d3):.2f}x fewer nodes!)", flush=True)
    print(f"TOTAL TIME          : Est 8-core M1 = {tot_est_8core_s:.1f}s ({tot_est_8core_s/60:.1f} min) vs A100 = {tot_ref_a100_s:.1f}s ({tot_ref_a100_s/60:.1f} min)", flush=True)
    print("=" * 126, flush=True)

if __name__ == "__main__":
    main()
