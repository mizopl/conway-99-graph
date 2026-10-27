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


def naive_reference_check_42(
    i0: int, min_can: int,
    Y0, Y1, cy1_can, Y2, cy2_can, Y3, cy3_can,
    X0, X1, X2, X3,
    Gp2, KW2, Gp4, KW4,
    C11_col_mask: int, O11_orb_mask: int, O12_orb_mask: int,
    g01_perms: list[list[int]], g012_flags: list[int], g0123_flags: list[int], swap01_perms: list[list[int]]
) -> tuple[int, int, int, int, int, int, int]:
    """
    Elementary pure-Python reference solver for a single root i0 in 4+2.
    Uses NO @njit, NO byte-level LUTs, NO eq_bits trick, and NO manual L1/L2 cache buffers (X0_0..X3_5).
    Verifies exact node-by-node isomorphism (d1, d2, b1, d5, d6, d7, d8) with solve_single_rep_orbit42.
    """
    C11_m = int(C11_col_mask); O11_m = int(O11_orb_mask); O12_m = int(O12_orb_mask)
    min_can = int(min_can)
    y0, gy0, o11_1_0, o11_2_0, o12_1_0, o2_0 = [int(v) for v in Y0[i0]]
    u1_11_0 = o11_1_0 | o11_2_0; u2_11_0 = o11_2_0

    stab0_indices = [p_i for p_i, p in enumerate(g01_perms) if permute_mask_py(y0, p) == y0]

    def ok_y_d0(row, c_can_val, gp, kw):
        if int(c_can_val) < min_can: return False
        ry, rgy, ro11_1, ro11_2, ro12_1, ro2 = [int(v) for v in row]
        if (ro12_1 & o12_1_0) or (ro11_2 & u1_11_0) or (ro11_1 & u2_11_0): return False
        if (y0 & ry).bit_count() != int(gp) or (gy0 & ry).bit_count() != int(kw): return False
        return ((y0 & ry) & C11_m).bit_count() <= 4

    c1_0 = []
    for j1 in range(len(Y1)):
        if ok_y_d0(Y1[j1], cy1_can[j1], Gp2[0, 1], KW2[0, 1]):
            ry = int(Y1[j1, 0])
            if any(permute_mask_py(ry, g01_perms[p_i]) < ry for p_i in stab0_indices):
                continue
            if any(permute_mask_py(y0, p) == ry and permute_mask_py(ry, p) < y0 for p in swap01_perms):
                continue
            c1_0.append(j1)
    c2_0 = [j2 for j2 in range(len(Y2)) if ok_y_d0(Y2[j2], cy2_can[j2], Gp2[0, 2], KW2[0, 2])]
    c3_0 = [j3 for j3 in range(len(Y3)) if ok_y_d0(Y3[j3], cy3_can[j3], Gp2[0, 3], KW2[0, 3])]

    def filter_x_d0(X_pool):
        return [
            (int(row[0]), int(row[1]), int(row[6]))
            for row in X_pool
            if (int(row[6]) & o2_0) == 0 and (int(row[0]) & y0).bit_count() == 1 and (int(row[1]) & y0).bit_count() == 2
        ]

    x0_0 = filter_x_d0(X0); x1_0 = filter_x_d0(X1); x2_0 = filter_x_d0(X2); x3_0 = filter_x_d0(X3)

    d1 = len(c1_0); d2 = 0; b1 = 0; d5 = 0; d6 = 0; d7 = 0; d8 = 0
    gp4_01, kw4_01 = int(Gp4[0, 1]), int(KW4[0, 1])
    gp4_02, kw4_02 = int(Gp4[0, 2]), int(KW4[0, 2])
    gp4_03, kw4_03 = int(Gp4[0, 3]), int(KW4[0, 3])
    gp4_12, kw4_12 = int(Gp4[1, 2]), int(KW4[1, 2])
    gp4_13, kw4_13 = int(Gp4[1, 3]), int(KW4[1, 3])
    gp4_23, kw4_23 = int(Gp4[2, 3]), int(KW4[2, 3])

    for i1 in c1_0:
        y1, gy1, o11_1_1, o11_2_1, o12_1_1, o2_1 = [int(v) for v in Y1[i1]]
        col_u1_1 = y0 | y1; col_u2_1 = y0 & y1
        d2_1 = (col_u2_1 & C11_m).bit_count()
        if d2_1 > 4: continue
        u2_11_1 = u2_11_0 | o11_2_1 | (u1_11_0 & o11_1_1)
        if u2_11_1.bit_count() - d2_1 > 8: continue
        u1_11_1 = u1_11_0 | o11_1_1 | o11_2_1
        u1_12_1 = o12_1_0 | o12_1_1; orb_p_1 = o2_0 | o2_1

        stab01_indices = [p_i for p_i in stab0_indices if g012_flags[p_i] == 1 and permute_mask_py(y1, g01_perms[p_i]) == y1]

        def ok_y_d1(row, gp, kw):
            ry, rgy, ro11_1, ro11_2, ro12_1, ro2 = [int(v) for v in row]
            if (ro12_1 & u1_12_1) or (ry & col_u2_1) or (ro11_2 & u1_11_1) or (ro11_1 & u2_11_1): return False
            if (y1 & ry).bit_count() != int(gp) or (gy1 & ry).bit_count() != int(kw): return False
            return ((col_u2_1 | (col_u1_1 & ry)) & C11_m).bit_count() <= 4

        c2_1 = [
            i2 for i2 in c2_0
            if ok_y_d1(Y2[i2], Gp2[1, 2], KW2[1, 2])
            and not any(permute_mask_py(int(Y2[i2, 0]), g01_perms[p_i]) < int(Y2[i2, 0]) for p_i in stab01_indices)
        ]
        if not c2_1: continue
        c3_1 = [i3 for i3 in c3_0 if ok_y_d1(Y3[i3], Gp2[1, 3], KW2[1, 3])]
        if not c3_1: continue

        def filter_x_d1(x_list):
            return [(rx, rgx, rox) for (rx, rgx, rox) in x_list if (rx & col_u2_1) == 0 and (rox & orb_p_1) == 0 and (rx & y1).bit_count() == 1 and (rgx & y1).bit_count() == 2]

        x0_1 = filter_x_d1(x0_0)
        if not x0_1: continue
        x1_1 = filter_x_d1(x1_0)
        if not x1_1: continue
        x2_1 = filter_x_d1(x2_0)
        if not x2_1: continue
        x3_1 = filter_x_d1(x3_0)
        if not x3_1: continue

        d2 += len(c2_1)
        for i2 in c2_1:
            y2, gy2, o11_1_2, o11_2_2, o12_1_2, o2_2 = [int(v) for v in Y2[i2]]
            col_u2_2 = col_u2_1 | (col_u1_1 & y2); col_u1_2 = col_u1_1 | y2
            d2_2 = (col_u2_2 & C11_m).bit_count()
            if d2_2 > 4 or (col_u1_2 & C11_m).bit_count() < 14: continue
            u2_11_2 = u2_11_1 | o11_2_2 | (u1_11_1 & o11_1_2)
            if u2_11_2.bit_count() - d2_2 > 8: continue
            u1_11_2 = u1_11_1 | o11_1_2 | o11_2_2
            u1_12_2 = u1_12_1 | o12_1_2; orb_p_2 = orb_p_1 | o2_2

            stab012_indices = [p_i for p_i in stab01_indices if g0123_flags[p_i] == 1 and permute_mask_py(y2, g01_perms[p_i]) == y2]
            req_o11_2 = O11_m & (~u1_11_2); req_o11_1 = u1_11_2 & (~u2_11_2); req_o12_1 = O12_m & (~u1_12_2)

            x0_2 = None
            for i3 in c3_1:
                ry3, gy3, ro11_1_3, ro11_2_3, ro12_1_3, o2_3 = [int(v) for v in Y3[i3]]
                if ro12_1_3 == req_o12_1 and ro11_1_3 == req_o11_1 and ro11_2_3 == req_o11_2 and (ry3 & col_u2_2) == 0:
                    if (y2 & ry3).bit_count() == int(Gp2[2, 3]) and (gy2 & ry3).bit_count() == int(KW2[2, 3]):
                        col_u2_3 = col_u2_2 | (col_u1_2 & ry3); col_u1_3 = col_u1_2 | ry3
                        if (col_u2_3 & C11_m).bit_count() == 4 and (col_u1_3 & C11_m).bit_count() == 20:
                            if any(permute_mask_py(ry3, g01_perms[p_i]) < ry3 for p_i in stab012_indices):
                                continue
                            if x0_2 is None:
                                def filter_x_d2(x_list):
                                    return [(rx, rgx, rox) for (rx, rgx, rox) in x_list if (rx & col_u2_2) == 0 and (rox & orb_p_2) == 0 and (rx & y2).bit_count() == 1 and (rgx & y2).bit_count() == 2]
                                x0_2 = filter_x_d2(x0_1)
                                if not x0_2: break
                                x1_2 = filter_x_d2(x1_1)
                                if not x1_2: break
                                x2_2 = filter_x_d2(x2_1)
                                if not x2_2: break
                                x3_2 = filter_x_d2(x3_1)
                                if not x3_2: break

                            b1 += 1
                            orb_p_3 = orb_p_2 | o2_3
                            def filter_x_d3(x_list):
                                return [(rx, rgx, rox) for (rx, rgx, rox) in x_list if (rx & col_u2_3) == 0 and (rox & orb_p_3) == 0 and (rx & ry3).bit_count() == 1 and (rgx & ry3).bit_count() == 2]
                            x0_3 = filter_x_d3(x0_2)
                            if not x0_3: continue
                            x1_3 = filter_x_d3(x1_2)
                            if not x1_3: continue
                            x2_3 = filter_x_d3(x2_2)
                            if not x2_3: continue
                            x3_3 = filter_x_d3(x3_2)
                            if not x3_3: continue

                            d5 += len(x0_3)
                            for (x0, gx0, ox0) in x0_3:
                                col_u2_4 = col_u2_3 | (col_u1_3 & x0); col_u1_4 = col_u1_3 | x0; orb_p_4 = orb_p_3 | ox0
                                x1_4 = [(rx, rgx, rox) for (rx, rgx, rox) in x1_3 if (rx & col_u2_4) == 0 and (rox & orb_p_4) == 0 and (x0 & rx).bit_count() == gp4_01 and (gx0 & rx).bit_count() == kw4_01]
                                if not x1_4: continue
                                d6 += len(x1_4)
                                x2_4 = [(rx, rgx, rox) for (rx, rgx, rox) in x2_3 if (rx & col_u2_4) == 0 and (rox & orb_p_4) == 0 and (x0 & rx).bit_count() == gp4_02 and (gx0 & rx).bit_count() == kw4_02]
                                if not x2_4: continue
                                x3_4 = None
                                for (x1, gx1, ox1) in x1_4:
                                    col_u2_5 = col_u2_4 | (col_u1_4 & x1); col_u1_5 = col_u1_4 | x1; orb_p_5 = orb_p_4 | ox1
                                    x2_5 = [(rx, rgx, rox) for (rx, rgx, rox) in x2_4 if (rx & col_u2_5) == 0 and (rox & orb_p_5) == 0 and (x1 & rx).bit_count() == gp4_12 and (gx1 & rx).bit_count() == kw4_12]
                                    if not x2_5: continue
                                    if x3_4 is None:
                                        x3_4 = [(rx, rgx, rox) for (rx, rgx, rox) in x3_3 if (rx & col_u2_4) == 0 and (rox & orb_p_4) == 0 and (x0 & rx).bit_count() == gp4_03 and (gx0 & rx).bit_count() == kw4_03]
                                    if not x3_4:
                                        d7 += len(x2_5)
                                        continue
                                    d7 += len(x2_5)
                                    x3_5 = [(rx, rgx, rox) for (rx, rgx, rox) in x3_4 if (rx & col_u2_5) == 0 and (rox & orb_p_5) == 0 and (x1 & rx).bit_count() == gp4_13 and (gx1 & rx).bit_count() == kw4_13]
                                    if not x3_5: continue
                                    for (x2, gx2, ox2) in x2_5:
                                        col_u2_6 = col_u2_5 | (col_u1_5 & x2); orb_p_6 = orb_p_5 | ox2
                                        for (x3, gx3, ox3) in x3_5:
                                            if (x3 & col_u2_6) == 0 and (ox3 & orb_p_6) == 0 and (x2 & x3).bit_count() == gp4_23 and (gx2 & x3).bit_count() == kw4_23:
                                                d8 += 1

    return (d1, d2, b1, d5, d6, d7, d8)

@njit
def solve_single_rep_orbit42(
    i0, min_can,
    Y0, Y1, cy1_can, Y2, cy2_can, Y3, cy3_can,
    X0, cx0_can, X1, cx1_can, X2, cx2_can, X3, cx3_can,
    X4, cx4_can, X5, cx5_can, X6, cx6_can, X7, cx7_can,
    Gp2, KW2, Gp4, KW4,
    C11_col_mask, O11_orb_mask, O12_orb_mask,
    luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
):
    out = np.zeros(7, dtype=np.int64)
    z64 = np.uint64(0)
    n_g01 = len(luts_g01)
    n_swap01 = len(luts_swap01)

    gp2_01, kw2_01 = Gp2[0, 1], KW2[0, 1]
    gp2_02, kw2_02 = Gp2[0, 2], KW2[0, 2]
    gp2_03, kw2_03 = Gp2[0, 3], KW2[0, 3]
    gp2_12, kw2_12 = Gp2[1, 2], KW2[1, 2]
    gp2_13, kw2_13 = Gp2[1, 3], KW2[1, 3]
    gp2_23, kw2_23 = Gp2[2, 3], KW2[2, 3]

    if True:
        y0 = Y0[i0, 0]
        gy0 = Y0[i0, 1]
        o11_1_0 = Y0[i0, 2]
        o11_2_0 = Y0[i0, 3]
        o12_1_0 = Y0[i0, 4]
        o2_0 = Y0[i0, 5]

        u1_11_0 = o11_1_0 | o11_2_0
        u2_11_0 = o11_2_0

        stab0_idx = np.empty(6144, dtype=np.int32)
        n_stab0 = 0
        for p_idx in range(n_g01):
            if apply_lut(y0, luts_g01[p_idx]) == y0:
                stab0_idx[n_stab0] = p_idx
                n_stab0 += 1

        # Filter Y1, Y2, Y3 at depth 0
        c1_0 = np.empty(len(Y1), dtype=np.int32); n1_0 = 0
        fb01 = (y0 if gp2_01 == 0 else z64) | (gy0 if kw2_01 == 0 else z64)
        for j1 in range(len(Y1)):
            if cy1_can[j1] >= min_can:
                ry = Y1[j1, 0]
                if (Y1[j1, 4] & o12_1_0) == z64 and (ry & fb01) == z64 and (Y1[j1, 3] & u1_11_0) == z64 and (Y1[j1, 2] & u2_11_0) == z64:
                    if (gp2_01 == 0 or eq_bits(y0 & ry, gp2_01)) and (kw2_01 == 0 or eq_bits(gy0 & ry, kw2_01)):
                        if popcnt64((y0 & ry) & C11_col_mask) <= 4:
                            is_rep1 = True
                            for s_i in range(n_stab0):
                                if apply_lut(ry, luts_g01[stab0_idx[s_i]]) < ry:
                                    is_rep1 = False
                                    break
                            if is_rep1 and n_swap01 > 0:
                                for p_idx in range(n_swap01):
                                    if apply_lut(y0, luts_swap01[p_idx]) == ry:
                                        if apply_lut(ry, luts_swap01[p_idx]) < y0:
                                            is_rep1 = False
                                            break
                            if is_rep1:
                                c1_0[n1_0] = j1; n1_0 += 1

        c2_0 = np.empty(len(Y2), dtype=np.int32); n2_0 = 0
        fb02 = (y0 if gp2_02 == 0 else z64) | (gy0 if kw2_02 == 0 else z64)
        for j2 in range(len(Y2)):
            if cy2_can[j2] >= min_can:
                ry = Y2[j2, 0]
                if (Y2[j2, 4] & o12_1_0) == z64 and (ry & fb02) == z64 and (Y2[j2, 3] & u1_11_0) == z64 and (Y2[j2, 2] & u2_11_0) == z64:
                    if (gp2_02 == 0 or eq_bits(y0 & ry, gp2_02)) and (kw2_02 == 0 or eq_bits(gy0 & ry, kw2_02)):
                        if popcnt64((y0 & ry) & C11_col_mask) <= 4:
                            c2_0[n2_0] = j2; n2_0 += 1

        c3_0 = np.empty(len(Y3), dtype=np.int32); n3_0 = 0
        fb03 = (y0 if gp2_03 == 0 else z64) | (gy0 if kw2_03 == 0 else z64)
        for j3 in range(len(Y3)):
            if cy3_can[j3] >= min_can:
                ry = Y3[j3, 0]
                if (Y3[j3, 4] & o12_1_0) == z64 and (ry & fb03) == z64 and (Y3[j3, 3] & u1_11_0) == z64 and (Y3[j3, 2] & u2_11_0) == z64:
                    if (gp2_03 == 0 or eq_bits(y0 & ry, gp2_03)) and (kw2_03 == 0 or eq_bits(gy0 & ry, kw2_03)):
                        if popcnt64((y0 & ry) & C11_col_mask) <= 4:
                            c3_0[n3_0] = j3; n3_0 += 1

        # Also filter X0..X3 against y0 and pack (rx, rgx, rox) into contiguous L2-cache arrays!
        X0_0 = np.empty((32768, 3), dtype=np.uint64); nx0_0 = 0
        for jx0 in range(len(X0)):
            rx = X0[jx0, 0]; rgx = X0[jx0, 1]; rox = X0[jx0, 6]
            if (rox & o2_0) == z64 and eq_bits(rx & y0, 1) and eq_bits(rgx & y0, 2):
                X0_0[nx0_0, 0] = rx; X0_0[nx0_0, 1] = rgx; X0_0[nx0_0, 2] = rox; nx0_0 += 1

        X1_0 = np.empty((32768, 3), dtype=np.uint64); nx1_0 = 0
        for jx1 in range(len(X1)):
            rx = X1[jx1, 0]; rgx = X1[jx1, 1]; rox = X1[jx1, 6]
            if (rox & o2_0) == z64 and eq_bits(rx & y0, 1) and eq_bits(rgx & y0, 2):
                X1_0[nx1_0, 0] = rx; X1_0[nx1_0, 1] = rgx; X1_0[nx1_0, 2] = rox; nx1_0 += 1

        X2_0 = np.empty((32768, 3), dtype=np.uint64); nx2_0 = 0
        for jx2 in range(len(X2)):
            rx = X2[jx2, 0]; rgx = X2[jx2, 1]; rox = X2[jx2, 6]
            if (rox & o2_0) == z64 and eq_bits(rx & y0, 1) and eq_bits(rgx & y0, 2):
                X2_0[nx2_0, 0] = rx; X2_0[nx2_0, 1] = rgx; X2_0[nx2_0, 2] = rox; nx2_0 += 1

        X3_0 = np.empty((32768, 3), dtype=np.uint64); nx3_0 = 0
        for jx3 in range(len(X3)):
            rx = X3[jx3, 0]; rgx = X3[jx3, 1]; rox = X3[jx3, 6]
            if (rox & o2_0) == z64 and eq_bits(rx & y0, 1) and eq_bits(rgx & y0, 2):
                X3_0[nx3_0, 0] = rx; X3_0[nx3_0, 1] = rgx; X3_0[nx3_0, 2] = rox; nx3_0 += 1

        c2_1 = np.empty(n2_0 + 1, dtype=np.int32)
        c3_1 = np.empty(n3_0 + 1, dtype=np.int32)
        X0_1 = np.empty((4096, 3), dtype=np.uint64)
        X1_1 = np.empty((4096, 3), dtype=np.uint64)
        X2_1 = np.empty((4096, 3), dtype=np.uint64)
        X3_1 = np.empty((4096, 3), dtype=np.uint64)

        X0_2 = np.empty((1024, 3), dtype=np.uint64)
        X1_2 = np.empty((1024, 3), dtype=np.uint64)
        X2_2 = np.empty((1024, 3), dtype=np.uint64)
        X3_2 = np.empty((1024, 3), dtype=np.uint64)

        X0_3 = np.empty((256, 3), dtype=np.uint64)
        X1_3 = np.empty((256, 3), dtype=np.uint64)
        X2_3 = np.empty((256, 3), dtype=np.uint64)
        X3_3 = np.empty((256, 3), dtype=np.uint64)

        X1_4 = np.empty((256, 3), dtype=np.uint64)
        X2_4 = np.empty((256, 3), dtype=np.uint64)
        X3_4 = np.empty((256, 3), dtype=np.uint64)
        X2_5 = np.empty((256, 3), dtype=np.uint64)
        X3_5 = np.empty((256, 3), dtype=np.uint64)

        stab01_idx = np.empty(6144, dtype=np.int32)
        stab012_idx = np.empty(6144, dtype=np.int32)

        loc_d1 = n1_0
        loc_d2 = 0
        loc_b1 = 0
        loc_d5 = 0
        loc_d6 = 0
        loc_d7 = 0
        loc_d8 = 0

        for idx1 in range(n1_0):
            i1 = c1_0[idx1]
            y1 = Y1[i1, 0]; gy1 = Y1[i1, 1]
            o11_1_1 = Y1[i1, 2]; o11_2_1 = Y1[i1, 3]; o12_1_1 = Y1[i1, 4]; o2_1 = Y1[i1, 5]

            col_u1_1 = y0 | y1
            col_u2_1 = y0 & y1
            d2_1 = popcnt64(col_u2_1 & C11_col_mask)
            if d2_1 > 4: continue
            u2_11_1 = u2_11_0 | o11_2_1 | (u1_11_0 & o11_1_1)
            if popcnt64(u2_11_1) - d2_1 > 8: continue
            u1_11_1 = u1_11_0 | o11_1_1 | o11_2_1
            u1_12_1 = o12_1_0 | o12_1_1
            orb_p_1 = o2_0 | o2_1

            n_stab01 = 0
            for s_i in range(n_stab0):
                p_idx = stab0_idx[s_i]
                if is_g012_flag[p_idx] == 1:
                    if apply_lut(y1, luts_g01[p_idx]) == y1:
                        stab01_idx[n_stab01] = p_idx
                        n_stab01 += 1

            n2_1 = 0
            fb12 = col_u2_1 | (y1 if gp2_12 == 0 else z64) | (gy1 if kw2_12 == 0 else z64)
            for k2 in range(n2_0):
                i2 = c2_0[k2]; ry = Y2[i2, 0]
                if (Y2[i2, 4] & u1_12_1) == z64 and (ry & fb12) == z64 and (Y2[i2, 3] & u1_11_1) == z64 and (Y2[i2, 2] & u2_11_1) == z64:
                    if (gp2_12 == 0 or eq_bits(y1 & ry, gp2_12)) and (kw2_12 == 0 or eq_bits(gy1 & ry, kw2_12)):
                        d2_tmp = popcnt64((col_u2_1 | (col_u1_1 & ry)) & C11_col_mask)
                        if d2_tmp <= 4:
                            if n_stab01 > 0:
                                is_rep2 = True
                                for s_i in range(n_stab01):
                                    if apply_lut(ry, luts_g01[stab01_idx[s_i]]) < ry:
                                        is_rep2 = False
                                        break
                                if not is_rep2:
                                    continue
                            c2_1[n2_1] = i2; n2_1 += 1
            if n2_1 == 0: continue

            n3_1 = 0
            fb13 = col_u2_1 | (y1 if gp2_13 == 0 else z64) | (gy1 if kw2_13 == 0 else z64)
            for k3 in range(n3_0):
                i3 = c3_0[k3]; ry = Y3[i3, 0]
                if (Y3[i3, 4] & u1_12_1) == z64 and (ry & fb13) == z64 and (Y3[i3, 3] & u1_11_1) == z64 and (Y3[i3, 2] & u2_11_1) == z64:
                    if (gp2_13 == 0 or eq_bits(y1 & ry, gp2_13)) and (kw2_13 == 0 or eq_bits(gy1 & ry, kw2_13)):
                        if popcnt64((col_u2_1 | (col_u1_1 & ry)) & C11_col_mask) <= 4:
                            c3_1[n3_1] = i3; n3_1 += 1
            if n3_1 == 0: continue

            # Filter X0_0..X3_0 at depth 1 into contiguous L2 arrays X0_1..X3_1
            nx0_1 = 0
            for kx0 in range(nx0_0):
                rx = X0_0[kx0, 0]; rgx = X0_0[kx0, 1]; rox = X0_0[kx0, 2]
                if (rx & col_u2_1) == z64 and (rox & orb_p_1) == z64 and eq_bits(rx & y1, 1) and eq_bits(rgx & y1, 2):
                    X0_1[nx0_1, 0] = rx; X0_1[nx0_1, 1] = rgx; X0_1[nx0_1, 2] = rox; nx0_1 += 1
            if nx0_1 == 0: continue

            nx1_1 = 0
            for kx1 in range(nx1_0):
                rx = X1_0[kx1, 0]; rgx = X1_0[kx1, 1]; rox = X1_0[kx1, 2]
                if (rx & col_u2_1) == z64 and (rox & orb_p_1) == z64 and eq_bits(rx & y1, 1) and eq_bits(rgx & y1, 2):
                    X1_1[nx1_1, 0] = rx; X1_1[nx1_1, 1] = rgx; X1_1[nx1_1, 2] = rox; nx1_1 += 1
            if nx1_1 == 0: continue

            nx2_1 = 0
            for kx2 in range(nx2_0):
                rx = X2_0[kx2, 0]; rgx = X2_0[kx2, 1]; rox = X2_0[kx2, 2]
                if (rx & col_u2_1) == z64 and (rox & orb_p_1) == z64 and eq_bits(rx & y1, 1) and eq_bits(rgx & y1, 2):
                    X2_1[nx2_1, 0] = rx; X2_1[nx2_1, 1] = rgx; X2_1[nx2_1, 2] = rox; nx2_1 += 1
            if nx2_1 == 0: continue

            nx3_1 = 0
            for kx3 in range(nx3_0):
                rx = X3_0[kx3, 0]; rgx = X3_0[kx3, 1]; rox = X3_0[kx3, 2]
                if (rx & col_u2_1) == z64 and (rox & orb_p_1) == z64 and eq_bits(rx & y1, 1) and eq_bits(rgx & y1, 2):
                    X3_1[nx3_1, 0] = rx; X3_1[nx3_1, 1] = rgx; X3_1[nx3_1, 2] = rox; nx3_1 += 1
            if nx3_1 == 0: continue

            loc_d2 += n2_1

            for idx2 in range(n2_1):
                i2 = c2_1[idx2]
                y2 = Y2[i2, 0]; gy2 = Y2[i2, 1]
                o11_1_2 = Y2[i2, 2]; o11_2_2 = Y2[i2, 3]; o12_1_2 = Y2[i2, 4]; o2_2 = Y2[i2, 5]

                col_u2_2 = col_u2_1 | (col_u1_1 & y2)
                col_u1_2 = col_u1_1 | y2
                d2_2 = popcnt64(col_u2_2 & C11_col_mask)
                if d2_2 > 4 or popcnt64(col_u1_2 & C11_col_mask) < 14: continue
                u2_11_2 = u2_11_1 | o11_2_2 | (u1_11_1 & o11_1_2)
                if popcnt64(u2_11_2) - d2_2 > 8: continue
                u1_11_2 = u1_11_1 | o11_1_2 | o11_2_2
                u1_12_2 = u1_12_1 | o12_1_2
                orb_p_2 = orb_p_1 | o2_2

                n_stab012 = 0
                for s_i in range(n_stab01):
                    p_idx = stab01_idx[s_i]
                    if is_g0123_flag[p_idx] == 1:
                        if apply_lut(y2, luts_g01[p_idx]) == y2:
                            stab012_idx[n_stab012] = p_idx
                            n_stab012 += 1

                req_o11_2 = O11_orb_mask & (~u1_11_2)
                req_o11_1 = u1_11_2 & (~u2_11_2)
                req_o12_1 = O12_orb_mask & (~u1_12_2)
                fb23 = col_u2_2 | (y2 if gp2_23 == 0 else z64) | (gy2 if kw2_23 == 0 else z64)

                # Filter X0..X3 at depth 2 lazily only if at least one y3 survives!
                nx0_2 = -1

                for idx3 in range(n3_1):
                    i3 = c3_1[idx3]; ry3 = Y3[i3, 0]
                    if Y3[i3, 4] == req_o12_1 and Y3[i3, 2] == req_o11_1 and Y3[i3, 3] == req_o11_2 and (ry3 & fb23) == z64:
                        if (gp2_23 == 0 or eq_bits(y2 & ry3, gp2_23)) and (kw2_23 == 0 or eq_bits(gy2 & ry3, kw2_23)):
                            col_u2_3 = col_u2_2 | (col_u1_2 & ry3)
                            col_u1_3 = col_u1_2 | ry3
                            if popcnt64(col_u2_3 & C11_col_mask) == 4 and popcnt64(col_u1_3 & C11_col_mask) == 20:
                                if n_stab012 > 0:
                                    is_rep3 = True
                                    for s_i in range(n_stab012):
                                        if apply_lut(ry3, luts_g01[stab012_idx[s_i]]) < ry3:
                                            is_rep3 = False
                                            break
                                    if not is_rep3:
                                        continue

                                if nx0_2 == -1:
                                    nx0_2 = 0
                                    for kx0 in range(nx0_1):
                                        rx = X0_1[kx0, 0]; rgx = X0_1[kx0, 1]; rox = X0_1[kx0, 2]
                                        if (rx & col_u2_2) == z64 and (rox & orb_p_2) == z64 and eq_bits(rx & y2, 1) and eq_bits(rgx & y2, 2):
                                            X0_2[nx0_2, 0] = rx; X0_2[nx0_2, 1] = rgx; X0_2[nx0_2, 2] = rox; nx0_2 += 1
                                    if nx0_2 == 0:
                                        break
                                    nx1_2 = 0
                                    for kx1 in range(nx1_1):
                                        rx = X1_1[kx1, 0]; rgx = X1_1[kx1, 1]; rox = X1_1[kx1, 2]
                                        if (rx & col_u2_2) == z64 and (rox & orb_p_2) == z64 and eq_bits(rx & y2, 1) and eq_bits(rgx & y2, 2):
                                            X1_2[nx1_2, 0] = rx; X1_2[nx1_2, 1] = rgx; X1_2[nx1_2, 2] = rox; nx1_2 += 1
                                    if nx1_2 == 0:
                                        break
                                    nx2_2 = 0
                                    for kx2 in range(nx2_1):
                                        rx = X2_1[kx2, 0]; rgx = X2_1[kx2, 1]; rox = X2_1[kx2, 2]
                                        if (rx & col_u2_2) == z64 and (rox & orb_p_2) == z64 and eq_bits(rx & y2, 1) and eq_bits(rgx & y2, 2):
                                            X2_2[nx2_2, 0] = rx; X2_2[nx2_2, 1] = rgx; X2_2[nx2_2, 2] = rox; nx2_2 += 1
                                    if nx2_2 == 0:
                                        break
                                    nx3_2 = 0
                                    for kx3 in range(nx3_1):
                                        rx = X3_1[kx3, 0]; rgx = X3_1[kx3, 1]; rox = X3_1[kx3, 2]
                                        if (rx & col_u2_2) == z64 and (rox & orb_p_2) == z64 and eq_bits(rx & y2, 1) and eq_bits(rgx & y2, 2):
                                            X3_2[nx3_2, 0] = rx; X3_2[nx3_2, 1] = rgx; X3_2[nx3_2, 2] = rox; nx3_2 += 1
                                    if nx3_2 == 0:
                                        break

                                loc_b1 += 1
                                gy3 = Y3[i3, 1]; o2_3 = Y3[i3, 5]
                                orb_p_3 = orb_p_2 | o2_3

                                # Filter X0_2..X3_2 at depth 3 into L1-cache arrays X0_3..X3_3
                                nx0_3 = 0
                                for kx0 in range(nx0_2):
                                    rx = X0_2[kx0, 0]; rgx = X0_2[kx0, 1]; rox = X0_2[kx0, 2]
                                    if (rx & col_u2_3) == z64 and (rox & orb_p_3) == z64 and eq_bits(rx & ry3, 1) and eq_bits(rgx & ry3, 2):
                                        X0_3[nx0_3, 0] = rx; X0_3[nx0_3, 1] = rgx; X0_3[nx0_3, 2] = rox; nx0_3 += 1
                                if nx0_3 == 0: continue

                                nx1_3 = 0
                                for kx1 in range(nx1_2):
                                    rx = X1_2[kx1, 0]; rgx = X1_2[kx1, 1]; rox = X1_2[kx1, 2]
                                    if (rx & col_u2_3) == z64 and (rox & orb_p_3) == z64 and eq_bits(rx & ry3, 1) and eq_bits(rgx & ry3, 2):
                                        X1_3[nx1_3, 0] = rx; X1_3[nx1_3, 1] = rgx; X1_3[nx1_3, 2] = rox; nx1_3 += 1
                                if nx1_3 == 0: continue

                                nx2_3 = 0
                                for kx2 in range(nx2_2):
                                    rx = X2_2[kx2, 0]; rgx = X2_2[kx2, 1]; rox = X2_2[kx2, 2]
                                    if (rx & col_u2_3) == z64 and (rox & orb_p_3) == z64 and eq_bits(rx & ry3, 1) and eq_bits(rgx & ry3, 2):
                                        X2_3[nx2_3, 0] = rx; X2_3[nx2_3, 1] = rgx; X2_3[nx2_3, 2] = rox; nx2_3 += 1
                                if nx2_3 == 0: continue

                                nx3_3 = 0
                                for kx3 in range(nx3_2):
                                    rx = X3_2[kx3, 0]; rgx = X3_2[kx3, 1]; rox = X3_2[kx3, 2]
                                    if (rx & col_u2_3) == z64 and (rox & orb_p_3) == z64 and eq_bits(rx & ry3, 1) and eq_bits(rgx & ry3, 2):
                                        X3_3[nx3_3, 0] = rx; X3_3[nx3_3, 1] = rgx; X3_3[nx3_3, 2] = rox; nx3_3 += 1
                                if nx3_3 == 0: continue

                                loc_d5 += nx0_3
                                gp4_01, kw4_01 = Gp4[0, 1], KW4[0, 1]
                                gp4_02, kw4_02 = Gp4[0, 2], KW4[0, 2]
                                gp4_03, kw4_03 = Gp4[0, 3], KW4[0, 3]
                                gp4_12, kw4_12 = Gp4[1, 2], KW4[1, 2]
                                gp4_13, kw4_13 = Gp4[1, 3], KW4[1, 3]
                                gp4_23, kw4_23 = Gp4[2, 3], KW4[2, 3]

                                for kx0 in range(nx0_3):
                                    x0 = X0_3[kx0, 0]; gx0 = X0_3[kx0, 1]; ox0 = X0_3[kx0, 2]
                                    col_u2_4 = col_u2_3 | (col_u1_3 & x0)
                                    col_u1_4 = col_u1_3 | x0
                                    orb_p_4 = orb_p_3 | ox0

                                    fb4_01 = col_u2_4 | (x0 if gp4_01 == 0 else z64) | (gx0 if kw4_01 == 0 else z64)
                                    nx1_4 = 0
                                    for kx1 in range(nx1_3):
                                        rx = X1_3[kx1, 0]; rox = X1_3[kx1, 2]
                                        if (rx & fb4_01) == z64 and (rox & orb_p_4) == z64:
                                            rgx = X1_3[kx1, 1]
                                            if (gp4_01 == 0 or eq_bits(x0 & rx, gp4_01)) and (kw4_01 == 0 or eq_bits(gx0 & rx, kw4_01)):
                                                X1_4[nx1_4, 0] = rx; X1_4[nx1_4, 1] = rgx; X1_4[nx1_4, 2] = rox; nx1_4 += 1
                                    if nx1_4 == 0: continue
                                    loc_d6 += nx1_4

                                    fb4_02 = col_u2_4 | (x0 if gp4_02 == 0 else z64) | (gx0 if kw4_02 == 0 else z64)
                                    nx2_4 = 0
                                    for kx2 in range(nx2_3):
                                        rx = X2_3[kx2, 0]; rox = X2_3[kx2, 2]
                                        if (rx & fb4_02) == z64 and (rox & orb_p_4) == z64:
                                            rgx = X2_3[kx2, 1]
                                            if (gp4_02 == 0 or eq_bits(x0 & rx, gp4_02)) and (kw4_02 == 0 or eq_bits(gx0 & rx, kw4_02)):
                                                X2_4[nx2_4, 0] = rx; X2_4[nx2_4, 1] = rgx; X2_4[nx2_4, 2] = rox; nx2_4 += 1
                                    if nx2_4 == 0: continue

                                    nx3_4 = -1

                                    for kx1 in range(nx1_4):
                                        x1 = X1_4[kx1, 0]; gx1 = X1_4[kx1, 1]; ox1 = X1_4[kx1, 2]
                                        col_u2_5 = col_u2_4 | (col_u1_4 & x1)
                                        col_u1_5 = col_u1_4 | x1
                                        orb_p_5 = orb_p_4 | ox1

                                        fb4_12 = col_u2_5 | (x1 if gp4_12 == 0 else z64) | (gx1 if kw4_12 == 0 else z64)
                                        nx2_5 = 0
                                        for kx2 in range(nx2_4):
                                            rx = X2_4[kx2, 0]; rox = X2_4[kx2, 2]
                                            if (rx & fb4_12) == z64 and (rox & orb_p_5) == z64:
                                                rgx = X2_4[kx2, 1]
                                                if (gp4_12 == 0 or eq_bits(x1 & rx, gp4_12)) and (kw4_12 == 0 or eq_bits(gx1 & rx, kw4_12)):
                                                    X2_5[nx2_5, 0] = rx; X2_5[nx2_5, 1] = rgx; X2_5[nx2_5, 2] = rox; nx2_5 += 1
                                        if nx2_5 == 0: continue

                                        if nx3_4 == -1:
                                            fb4_03 = col_u2_4 | (x0 if gp4_03 == 0 else z64) | (gx0 if kw4_03 == 0 else z64)
                                            nx3_4 = 0
                                            for kx3 in range(nx3_3):
                                                rx = X3_3[kx3, 0]; rox = X3_3[kx3, 2]
                                                if (rx & fb4_03) == z64 and (rox & orb_p_4) == z64:
                                                    rgx = X3_3[kx3, 1]
                                                    if (gp4_03 == 0 or eq_bits(x0 & rx, gp4_03)) and (kw4_03 == 0 or eq_bits(gx0 & rx, kw4_03)):
                                                        X3_4[nx3_4, 0] = rx; X3_4[nx3_4, 1] = rgx; X3_4[nx3_4, 2] = rox; nx3_4 += 1
                                        if nx3_4 == 0:
                                            loc_d7 += nx2_5
                                            continue

                                        loc_d7 += nx2_5

                                        fb4_13 = col_u2_5 | (x1 if gp4_13 == 0 else z64) | (gx1 if kw4_13 == 0 else z64)
                                        nx3_5 = 0
                                        for kx3 in range(nx3_4):
                                            rx = X3_4[kx3, 0]; rox = X3_4[kx3, 2]
                                            if (rx & fb4_13) == z64 and (rox & orb_p_5) == z64:
                                                rgx = X3_4[kx3, 1]
                                                if (gp4_13 == 0 or eq_bits(x1 & rx, gp4_13)) and (kw4_13 == 0 or eq_bits(gx1 & rx, kw4_13)):
                                                    X3_5[nx3_5, 0] = rx; X3_5[nx3_5, 1] = rgx; X3_5[nx3_5, 2] = rox; nx3_5 += 1
                                        if nx3_5 == 0: continue

                                        for kx2 in range(nx2_5):
                                            x2 = X2_5[kx2, 0]; gx2 = X2_5[kx2, 1]; ox2 = X2_5[kx2, 2]
                                            col_u2_6 = col_u2_5 | (col_u1_5 & x2)
                                            orb_p_6 = orb_p_5 | ox2
                                            fb4_23 = col_u2_6 | (x2 if gp4_23 == 0 else z64) | (gx2 if kw4_23 == 0 else z64)

                                            for kx3 in range(nx3_5):
                                                x3 = X3_5[kx3, 0]
                                                if (x3 & fb4_23) == z64 and (X3_5[kx3, 2] & orb_p_6) == z64:
                                                    if (gp4_23 == 0 or eq_bits(x2 & x3, gp4_23)) and (kw4_23 == 0 or eq_bits(gx2 & x3, kw4_23)):
                                                        loc_d8 += 1

        out[0] = loc_d1
        out[1] = loc_d2
        out[2] = loc_b1
        out[3] = loc_d5
        out[4] = loc_d6
        out[5] = loc_d7
        out[6] = loc_d8

    return out

@njit(parallel=True)
def solve_orbit_42_chiral_cpu(
    n_test, reps, rep_canons,
    Y0, Y1, cy1_can, Y2, cy2_can, Y3, cy3_can,
    X0, cx0_can, X1, cx1_can, X2, cx2_can, X3, cx3_can,
    X4, cx4_can, X5, cx5_can, X6, cx6_can, X7, cx7_can,
    Gp2, KW2, Gp4, KW4,
    C11_col_mask, O11_orb_mask, O12_orb_mask,
    luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
):
    counts = np.zeros((n_test, 7), dtype=np.int64)
    for idx_rep in prange(n_test):
        counts[idx_rep] = solve_single_rep_orbit42(
            reps[idx_rep], rep_canons[idx_rep],
            Y0, Y1, cy1_can, Y2, cy2_can, Y3, cy3_can,
            X0, cx0_can, X1, cx1_can, X2, cx2_can, X3, cx3_can,
            X4, cx4_can, X5, cx5_can, X6, cx6_can, X7, cx7_can,
            Gp2, KW2, Gp4, KW4,
            C11_col_mask, O11_orb_mask, O12_orb_mask,
            luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
        )
    return counts.sum(axis=0)

def main():
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

    cols_60 = []; col_idx = {}
    for b1 in range(6):
        for b2 in range(b1 + 1, 6):
            for s1 in (0, 1):
                for s2 in (0, 1):
                    j1, j2 = 2 * b1 + s1, 2 * b2 + s2
                    c = len(cols_60); cols_60.append((j1, j2)); col_idx[(j1, j2)] = col_idx[(j2, j1)] = c
    g_col = [col_idx[(j1 ^ 1, j2 ^ 1)] for (j1, j2) in cols_60]
    orbs_30 = [(c, g_col[c]) for c in range(60) if c < g_col[c]]

    # Place C4 on {0..7} and C2 on {8..11}
    I_B1 = {0, 1, 2, 3, 4, 5, 6, 7}
    O11_orb_mask = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] in I_B1 and cols_60[c][1] in I_B1))
    O12_orb_mask = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if (cols_60[c][0] in I_B1) ^ (cols_60[c][1] in I_B1)))
    C11_col_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in I_B1 and v in I_B1))

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
                        res.append((xm, gxm, o11_1, o11_2, o12_1, o12_2, o2_all))
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

    F4 = F12[:4, :4]; I4 = np.eye(4, dtype=int); J4 = np.ones((4, 4), dtype=int)
    F8 = F12[:8, :8]; I8 = np.eye(8, dtype=int); J8 = np.ones((8, 8), dtype=int)

    for orb_idx in [0, 162]:
        M, E, Gp, KW0, Delta0, comps = orbits_42[orb_idx]
        comp2 = comps[0] if len(comps[0]) == 4 else comps[1]
        comp4 = comps[1] if len(comps[0]) == 4 else comps[0]

        M4, E4 = M[np.ix_(comp2, comp2)], E[np.ix_(comp2, comp2)]
        KW4 = (2 * J4 - F4 - E4 - (M4 @ E4) - (E4 @ M4)).astype(np.int32)
        D4 = 2 * J4 - I4 - F4 - M4 - (E4 @ F4)
        Gp4_2 = (7 * I4 + J4 - M4).astype(np.int32)
        Y_raw = [gen_2block_rows(tuple(int(D4[r, j]) for j in range(4)), int(KW4[r, r])) for r in range(4)]
        ylens = [len(y) for y in Y_raw]

        M8, E8 = M[np.ix_(comp4, comp4)], E[np.ix_(comp4, comp4)]
        KW8 = (2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)).astype(np.int32)
        D8 = 2 * J8 - I8 - F8 - M8 - (E8 @ F8)
        Gp8_4 = (7 * I8 + J8 - M8).astype(np.int32)
        X_raw = [gen_4block_rows(tuple(int(D8[r, j]) for j in range(8)), int(KW8[r, r])) for r in range(8)]
        xlens = [len(x) for x in X_raw]

        # Decoupled stabilizers Stab_M16(C2) and Stab_M16(C4)
        stab2_m16 = []
        for pr in permutations(range(4)):
            if any(ylens[pr[a]] != ylens[a] for a in range(4)): continue
            if not (Gp4_2 == Gp4_2[np.ix_(pr, pr)]).all() or not (KW4 == KW4[np.ix_(pr, pr)]).all(): continue
            for pc in b2_perms_4:
                if (D4 == D4[np.ix_(pr, pc)]).all():
                    stab2_m16.append((pr, pc))

        def w2(u, v):
            w = 0
            if Gp4_2[u, v] == 0: w += 4
            elif Gp4_2[u, v] == 1: w += 1
            if KW4[u, v] == 0: w += 4
            elif KW4[u, v] == 1: w += 1
            return w

        ord2 = list(max(permutations(range(4)), key=lambda q: (w2(q[0], q[1]) + w2(q[0], q[2]) + w2(q[1], q[2]), w2(q[0], q[1]), -ylens[q[0]])))

        def w4(u, v):
            w = 0
            if Gp8_4[u, v] == 0: w += 4
            elif Gp8_4[u, v] == 1: w += 1
            if KW8[u, v] == 0: w += 4
            elif KW8[u, v] == 1: w += 1
            return w

        def get_stab4_sub(q):
            q = list(q)
            gp4 = Gp8_4[np.ix_(q, q)]
            kw4 = KW8[np.ix_(q, q)]
            d48 = D8[q, :]
            st = []
            for pr in permutations(range(4)):
                if any(xlens[q[pr[a]]] != xlens[q[a]] for a in range(4)): continue
                if not (gp4 == gp4[np.ix_(pr, pr)]).all() or not (kw4 == kw4[np.ix_(pr, pr)]).all(): continue
                for pc in b4_perms_8:
                    if (d48 == d48[np.ix_(pr, pc)]).all():
                        st.append((pr, pc))
            return st

        stab_cache = {q_set: get_stab4_sub(q_set) for q_set in combinations(range(8), 4)}

        # Prioritize smallest pools (diag_kw == 0) + balanced zero-links & 4x8 sub-cone stabilizer |Stab4_sub|!
        ord4 = list(max(
            permutations(range(8), 4),
            key=lambda q: (
                sum(1 for a in range(4) if xlens[q[a]] < 150000),
                sum(w4(q[a], q[b]) for a in range(4) for b in range(a + 1, 4)) + 2 * int(np.log2(len(stab_cache[tuple(sorted(q))]))),
                len(stab_cache[tuple(sorted(q))]),
                w4(q[0], q[1]) + w4(q[0], q[2]) + w4(q[1], q[2]),
                w4(q[0], q[1]) + w4(q[0], q[2]),
                w4(q[0], q[1]),
                -sum(xlens[q[a]] for a in range(4))
            )
        ))
        stab4_m16 = get_stab4_sub(ord4)
        rem4 = [u for u in range(8) if u not in ord4]
        ord4 = ord4 + rem4

        Y = [Y_raw[r] for r in ord2]
        Gp2_ord = np.ascontiguousarray(Gp4_2[np.ix_(ord2, ord2)], dtype=np.int32)
        KW2_ord = np.ascontiguousarray(KW4[np.ix_(ord2, ord2)], dtype=np.int32)

        X = [X_raw[r] for r in ord4]
        Gp4_ord = np.ascontiguousarray(Gp8_4[np.ix_(ord4, ord4)], dtype=np.int32)
        KW4_ord = np.ascontiguousarray(KW8[np.ix_(ord4, ord4)], dtype=np.int32)

        stab_y_to_0 = [[] for _ in range(4)]
        seen_y_to_0 = [set() for _ in range(4)]
        g01_dict = {}
        swap01_perms = []
        seen_swap01 = set()
        id_map = tuple(range(60))

        for pr2, pc2 in stab2_m16:
            for pr4, pc4 in stab4_m16:
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
        cx_cans = [np.zeros(len(X[a]), dtype=np.uint64) for a in range(8)]

        luts_g01 = build_perm_luts(g01_perms)
        is_g012_flag = np.ascontiguousarray(np.array(g012_flags, dtype=np.int32))
        is_g0123_flag = np.ascontiguousarray(np.array(g0123_flags, dtype=np.int32))
        luts_swap01 = build_perm_luts(swap01_perms)

        reps = np.ascontiguousarray([i for i in range(len(Y[0])) if Y[0][i, 0] == cy_cans[0][i]], dtype=np.int32)
        rep_canons = np.ascontiguousarray([cy_cans[0][i] for i in reps], dtype=np.uint64)

        if orb_idx == 0:
            _ = solve_orbit_42_chiral_cpu(
                0, reps[:1], rep_canons[:1],
                Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
                X[0], cx_cans[0], X[1], cx_cans[1], X[2], cx_cans[2], X[3], cx_cans[3],
                X[4], cx_cans[4], X[5], cx_cans[5], X[6], cx_cans[6], X[7], cx_cans[7],
                Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
                C11_col_mask, O11_orb_mask, O12_orb_mask,
                luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
            )

        # Zero-Trust Cross-Check Oracle on a non-trivial root (d8 > 0) of Orbit {orb_idx}:
        t_or = time.time()
        or_idx = 0
        for cand_idx in range(len(reps)):
            chk = solve_orbit_42_chiral_cpu(
                1, reps[cand_idx:cand_idx+1], rep_canons[cand_idx:cand_idx+1],
                Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
                X[0], cx_cans[0], X[1], cx_cans[1], X[2], cx_cans[2], X[3], cx_cans[3],
                X[4], cx_cans[4], X[5], cx_cans[5], X[6], cx_cans[6], X[7], cx_cans[7],
                Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
                C11_col_mask, O11_orb_mask, O12_orb_mask,
                luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
            )
            if chk[6] > 0:
                or_idx = cand_idx
                break
        naive_counts = naive_reference_check_42(
            int(reps[or_idx]), int(rep_canons[or_idx]),
            Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
            X[0], X[1], X[2], X[3],
            Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
            int(C11_col_mask), int(O11_orb_mask), int(O12_orb_mask),
            g01_perms, g012_flags, g0123_flags, swap01_perms
        )
        numba_counts = tuple(int(v) for v in solve_orbit_42_chiral_cpu(
            1, reps[or_idx:or_idx+1], rep_canons[or_idx:or_idx+1],
            Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
            X[0], cx_cans[0], X[1], cx_cans[1], X[2], cx_cans[2], X[3], cx_cans[3],
            X[4], cx_cans[4], X[5], cx_cans[5], X[6], cx_cans[6], X[7], cx_cans[7],
            Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
            C11_col_mask, O11_orb_mask, O12_orb_mask,
            luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
        ))
        assert naive_counts == numba_counts, f"Oracle mismatch on Orbit {orb_idx}: naive={naive_counts} != numba={numba_counts}"
        print(f"  [ORACLE Orbit {orb_idx:3d} rep_idx={or_idx:4d}] EXACT MATCH naive == numba == {naive_counts} in {time.time()-t_or:.2f}s", flush=True)

        n_test = min(50, len(reps))
        sample_idx = np.linspace(0, len(reps) - 1, n_test, dtype=np.int32)
        s_reps = np.ascontiguousarray(reps[sample_idx], dtype=np.int32)
        s_cans = np.ascontiguousarray(rep_canons[sample_idx], dtype=np.uint64)

        t0 = time.time()
        res = solve_orbit_42_chiral_cpu(
            n_test, s_reps, s_cans,
            Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
            X[0], cx_cans[0], X[1], cx_cans[1], X[2], cx_cans[2], X[3], cx_cans[3],
            X[4], cx_cans[4], X[5], cx_cans[5], X[6], cx_cans[6], X[7], cx_cans[7],
            Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
            C11_col_mask, O11_orb_mask, O12_orb_mask,
            luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
        )
        el = time.time() - t0
        scale = len(reps) / n_test
        print(
            f"Orbit {orb_idx:3d}: |Stab2|={len(stab2_m16)} |Stab4|={len(stab4_m16)} (tot={len(stab2_m16)*len(stab4_m16)}) | "
            f"reps={len(reps):5d} | Est b1={int(res[2]*scale):10,d} | Est d6={int(res[4]*scale):11,d} | Est d8={int(res[6]*scale):9,d} | 50-rep={el:.2f}s | Est 8c-M1={(el*scale)/7.5:.1f}s",
            flush=True
        )

if __name__ == "__main__":
    main()
