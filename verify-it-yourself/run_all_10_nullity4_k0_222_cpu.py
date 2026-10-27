import time
import json
import numpy as np
from numba import njit, prange
from itertools import combinations, permutations, product


@njit
def solve_single_rep_222(
    i0, min_can, same_b12,
    L0, L1, c1_can, L2, c2_can, L3, c3_can,
    L4, c4_can, L5, c5_can, L6, c6_can, L7, c7_can,
    L8, L9, L10, L11,
    Gp, KW0, O33_mask, O13_mask, O23_mask,
    luts_g01, is_g012_flag, is_g0123_flag, is_g01234_flag, luts_swap01
):
    out = np.zeros(3, dtype=np.int64)
    z64 = np.uint64(0)
    n_g01 = len(luts_g01)
    n_swap01 = len(luts_swap01)

    x0, gx0, cut0, o1_0, o2_0 = L0[i0, 0], L0[i0, 1], L0[i0, 2], L0[i0, 3], L0[i0, 4]
    u1_0 = o1_0 | o2_0
    u2_0 = o2_0

    stab0_idx = np.empty(n_g01 + 1, dtype=np.int32)
    n_stab0 = 0
    for p_idx in range(n_g01):
        if apply_lut(x0, luts_g01[p_idx]) == x0:
            stab0_idx[n_stab0] = p_idx
            n_stab0 += 1

    c1 = np.empty(len(L1), dtype=np.int32); n1 = 0
    for i in range(len(L1)):
        if c1_can[i] < min_can: continue
        rx = L1[i, 0]
        if (cut0 & L1[i, 2]) == z64 and (L1[i, 4] & u1_0) == z64 and (L1[i, 3] & u2_0) == z64:
            if eq_bits(x0 & rx, Gp[0, 1]) and eq_bits(x0 & L1[i, 1], KW0[0, 1]):
                is_rep1 = True
                for s_i in range(n_stab0):
                    if apply_lut(rx, luts_g01[stab0_idx[s_i]]) < rx:
                        is_rep1 = False
                        break
                if is_rep1 and n_swap01 > 0:
                    for p_idx in range(n_swap01):
                        if apply_lut(x0, luts_swap01[p_idx]) == rx:
                            if apply_lut(rx, luts_swap01[p_idx]) < x0:
                                is_rep1 = False
                                break
                if is_rep1:
                    c1[n1] = i; n1 += 1
    if n1 == 0: return out

    c2 = np.empty(len(L2), dtype=np.int32); n2 = 0
    for i in range(len(L2)):
        if c2_can[i] < min_can: continue
        if (cut0 & L2[i, 2]) == z64 and (L2[i, 4] & u1_0) == z64 and (L2[i, 3] & u2_0) == z64:
            if eq_bits(x0 & L2[i, 0], Gp[0, 2]) and eq_bits(x0 & L2[i, 1], KW0[0, 2]):
                c2[n2] = i; n2 += 1
    if n2 == 0: return out

    c3 = np.empty(len(L3), dtype=np.int32); n3 = 0
    for i in range(len(L3)):
        if c3_can[i] < min_can: continue
        if (cut0 & L3[i, 2]) == z64 and (L3[i, 4] & u1_0) == z64 and (L3[i, 3] & u2_0) == z64:
            if eq_bits(x0 & L3[i, 0], Gp[0, 3]) and eq_bits(x0 & L3[i, 1], KW0[0, 3]):
                c3[n3] = i; n3 += 1
    if n3 == 0: return out

    # Pack surviving L4..L7 at depth 0 into contiguous L2 arrays (xm, gxm, cutm, o1m, o2m)
    X4_0 = np.empty((20000, 5), dtype=np.uint64); n4_0 = 0
    for i in range(len(L4)):
        if same_b12 == 1 and c4_can[i] < min_can: continue
        rx = L4[i, 0]; rgx = L4[i, 1]; ro2 = L4[i, 4]
        if (o2_0 & ro2) == z64 and eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, 2):
            X4_0[n4_0, 0] = rx; X4_0[n4_0, 1] = rgx; X4_0[n4_0, 2] = L4[i, 2]; X4_0[n4_0, 3] = L4[i, 3]; X4_0[n4_0, 4] = ro2
            n4_0 += 1
    if n4_0 == 0: return out

    X5_0 = np.empty((20000, 5), dtype=np.uint64); n5_0 = 0
    for i in range(len(L5)):
        if same_b12 == 1 and c5_can[i] < min_can: continue
        rx = L5[i, 0]; rgx = L5[i, 1]; ro2 = L5[i, 4]
        if (o2_0 & ro2) == z64 and eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, 2):
            X5_0[n5_0, 0] = rx; X5_0[n5_0, 1] = rgx; X5_0[n5_0, 2] = L5[i, 2]; X5_0[n5_0, 3] = L5[i, 3]; X5_0[n5_0, 4] = ro2
            n5_0 += 1
    if n5_0 == 0: return out

    X6_0 = np.empty((20000, 5), dtype=np.uint64); n6_0 = 0
    for i in range(len(L6)):
        if same_b12 == 1 and c6_can[i] < min_can: continue
        rx = L6[i, 0]; rgx = L6[i, 1]; ro2 = L6[i, 4]
        if (o2_0 & ro2) == z64 and eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, 2):
            X6_0[n6_0, 0] = rx; X6_0[n6_0, 1] = rgx; X6_0[n6_0, 2] = L6[i, 2]; X6_0[n6_0, 3] = L6[i, 3]; X6_0[n6_0, 4] = ro2
            n6_0 += 1
    if n6_0 == 0: return out

    X7_0 = np.empty((20000, 5), dtype=np.uint64); n7_0 = 0
    for i in range(len(L7)):
        if same_b12 == 1 and c7_can[i] < min_can: continue
        rx = L7[i, 0]; rgx = L7[i, 1]; ro2 = L7[i, 4]
        if (o2_0 & ro2) == z64 and eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, 2):
            X7_0[n7_0, 0] = rx; X7_0[n7_0, 1] = rgx; X7_0[n7_0, 2] = L7[i, 2]; X7_0[n7_0, 3] = L7[i, 3]; X7_0[n7_0, 4] = ro2
            n7_0 += 1
    if n7_0 == 0: return out

    c8_0 = np.empty(20000, dtype=np.int32); n8_0 = 0
    for i in range(len(L8)):
        if (o2_0 & L8[i, 4]) == z64 and eq_bits(x0 & L8[i, 0], 1) and eq_bits(x0 & L8[i, 1], 2):
            c8_0[n8_0] = i; n8_0 += 1
    c9_0 = np.empty(20000, dtype=np.int32); n9_0 = 0
    for i in range(len(L9)):
        if (o2_0 & L9[i, 4]) == z64 and eq_bits(x0 & L9[i, 0], 1) and eq_bits(x0 & L9[i, 1], 2):
            c9_0[n9_0] = i; n9_0 += 1
    c10_0 = np.empty(20000, dtype=np.int32); n10_0 = 0
    for i in range(len(L10)):
        if (o2_0 & L10[i, 4]) == z64 and eq_bits(x0 & L10[i, 0], 1) and eq_bits(x0 & L10[i, 1], 2):
            c10_0[n10_0] = i; n10_0 += 1
    c11_0 = np.empty(20000, dtype=np.int32); n11_0 = 0
    for i in range(len(L11)):
        if (o2_0 & L11[i, 4]) == z64 and eq_bits(x0 & L11[i, 0], 1) and eq_bits(x0 & L11[i, 1], 2):
            c11_0[n11_0] = i; n11_0 += 1

    c2_1 = np.empty(4096, dtype=np.int32)
    c3_1 = np.empty(4096, dtype=np.int32)
    X4_1 = np.empty((4096, 5), dtype=np.uint64)
    X5_1 = np.empty((4096, 5), dtype=np.uint64)
    X6_1 = np.empty((4096, 5), dtype=np.uint64)
    X7_1 = np.empty((4096, 5), dtype=np.uint64)
    X4_2 = np.empty((1024, 5), dtype=np.uint64)
    X5_2 = np.empty((1024, 5), dtype=np.uint64)
    X6_2 = np.empty((1024, 5), dtype=np.uint64)
    X7_2 = np.empty((1024, 5), dtype=np.uint64)
    X4_3 = np.empty((256, 5), dtype=np.uint64)
    X5_3 = np.empty((256, 5), dtype=np.uint64)
    X6_3 = np.empty((256, 5), dtype=np.uint64)
    X7_3 = np.empty((256, 5), dtype=np.uint64)
    c8_7 = np.empty(256, dtype=np.int32)
    c9_7 = np.empty(256, dtype=np.int32)
    c10_7 = np.empty(256, dtype=np.int32)
    c11_7 = np.empty(256, dtype=np.int32)

    stab01_idx = np.empty(n_g01 + 1, dtype=np.int32)
    stab012_idx = np.empty(n_g01 + 1, dtype=np.int32)
    stab0123_idx = np.empty(n_g01 + 1, dtype=np.int32)

    local_b1 = 0
    local_b2 = 0
    local_b3 = 0

    for idx1 in range(n1):
        i1 = c1[idx1]
        x1, gx1, cut1, o1_1, o2_1 = L1[i1, 0], L1[i1, 1], L1[i1, 2], L1[i1, 3], L1[i1, 4]
        cut_01 = cut0 | cut1
        u2_01 = u2_0 | o2_1 | (u1_0 & o1_1)
        u1_01 = u1_0 | o1_1 | o2_1
        col_u2_01 = x0 & x1
        orb_p_01 = o2_0 | o2_1

        n_stab01 = 0
        for s_i in range(n_stab0):
            p_idx = stab0_idx[s_i]
            if is_g012_flag[p_idx] == 1:
                if apply_lut(x1, luts_g01[p_idx]) == x1:
                    stab01_idx[n_stab01] = p_idx
                    n_stab01 += 1

        n2_1 = 0
        for idx2 in range(n2):
            i2 = c2[idx2]; rx = L2[i2, 0]
            if (cut_01 & L2[i2, 2]) == z64 and (L2[i2, 4] & u1_01) == z64 and (L2[i2, 3] & u2_01) == z64:
                if eq_bits(x1 & rx, Gp[1, 2]) and eq_bits(x1 & L2[i2, 1], KW0[1, 2]):
                    if n_stab01 > 0:
                        is_rep2 = True
                        for s_i in range(n_stab01):
                            if apply_lut(rx, luts_g01[stab01_idx[s_i]]) < rx:
                                is_rep2 = False
                                break
                        if not is_rep2: continue
                    c2_1[n2_1] = i2; n2_1 += 1
        if n2_1 == 0: continue

        n3_1 = 0
        for idx3 in range(n3):
            i3 = c3[idx3]; rx = L3[i3, 0]
            if (cut_01 & L3[i3, 2]) == z64 and (L3[i3, 4] & u1_01) == z64 and (L3[i3, 3] & u2_01) == z64:
                if eq_bits(x1 & rx, Gp[1, 3]) and eq_bits(x1 & L3[i3, 1], KW0[1, 3]):
                    c3_1[n3_1] = i3; n3_1 += 1
        if n3_1 == 0: continue

        n4_1 = 0
        for k in range(n4_0):
            rx = X4_0[k, 0]; rgx = X4_0[k, 1]; ro2 = X4_0[k, 4]
            if (rx & col_u2_01) == z64 and (ro2 & o2_1) == z64 and eq_bits(rx & x1, 1) and eq_bits(rx & gx1, 2):
                X4_1[n4_1, 0] = rx; X4_1[n4_1, 1] = rgx; X4_1[n4_1, 2] = X4_0[k, 2]; X4_1[n4_1, 3] = X4_0[k, 3]; X4_1[n4_1, 4] = ro2
                n4_1 += 1
        if n4_1 == 0: continue

        n5_1 = 0
        for k in range(n5_0):
            rx = X5_0[k, 0]; rgx = X5_0[k, 1]; ro2 = X5_0[k, 4]
            if (rx & col_u2_01) == z64 and (ro2 & o2_1) == z64 and eq_bits(rx & x1, 1) and eq_bits(rx & gx1, 2):
                X5_1[n5_1, 0] = rx; X5_1[n5_1, 1] = rgx; X5_1[n5_1, 2] = X5_0[k, 2]; X5_1[n5_1, 3] = X5_0[k, 3]; X5_1[n5_1, 4] = ro2
                n5_1 += 1
        if n5_1 == 0: continue

        n6_1 = 0
        for k in range(n6_0):
            rx = X6_0[k, 0]; rgx = X6_0[k, 1]; ro2 = X6_0[k, 4]
            if (rx & col_u2_01) == z64 and (ro2 & o2_1) == z64 and eq_bits(rx & x1, 1) and eq_bits(rx & gx1, 2):
                X6_1[n6_1, 0] = rx; X6_1[n6_1, 1] = rgx; X6_1[n6_1, 2] = X6_0[k, 2]; X6_1[n6_1, 3] = X6_0[k, 3]; X6_1[n6_1, 4] = ro2
                n6_1 += 1
        if n6_1 == 0: continue

        n7_1 = 0
        for k in range(n7_0):
            rx = X7_0[k, 0]; rgx = X7_0[k, 1]; ro2 = X7_0[k, 4]
            if (rx & col_u2_01) == z64 and (ro2 & o2_1) == z64 and eq_bits(rx & x1, 1) and eq_bits(rx & gx1, 2):
                X7_1[n7_1, 0] = rx; X7_1[n7_1, 1] = rgx; X7_1[n7_1, 2] = X7_0[k, 2]; X7_1[n7_1, 3] = X7_0[k, 3]; X7_1[n7_1, 4] = ro2
                n7_1 += 1
        if n7_1 == 0: continue

        for idx2 in range(n2_1):
            i2 = c2_1[idx2]
            x2, gx2, cut2, o1_2, o2_2 = L2[i2, 0], L2[i2, 1], L2[i2, 2], L2[i2, 3], L2[i2, 4]
            cut_012 = cut_01 | cut2
            u2_012 = u2_01 | o2_2 | (u1_01 & o1_2)
            u1_012 = u1_01 | o1_2 | o2_2
            col_u2_012 = col_u2_01 | ((x0 | x1) & x2)

            n_stab012 = 0
            for s_i in range(n_stab01):
                p_idx = stab01_idx[s_i]
                if is_g0123_flag[p_idx] == 1:
                    if apply_lut(x2, luts_g01[p_idx]) == x2:
                        stab012_idx[n_stab012] = p_idx
                        n_stab012 += 1

            has_i3 = False
            for idx3 in range(n3_1):
                i3 = c3_1[idx3]
                if (cut_012 & L3[i3, 2]) == z64 and (L3[i3, 4] & u1_012) == z64 and (L3[i3, 3] & u2_012) == z64:
                    if eq_bits(x2 & L3[i3, 0], Gp[2, 3]) and eq_bits(x2 & L3[i3, 1], KW0[2, 3]):
                        has_i3 = True
                        break
            if not has_i3: continue

            n4_2 = 0
            for k in range(n4_1):
                rx = X4_1[k, 0]; rgx = X4_1[k, 1]; ro2 = X4_1[k, 4]
                if (rx & col_u2_012) == z64 and (ro2 & o2_2) == z64 and eq_bits(rx & x2, 1) and eq_bits(rx & gx2, 2):
                    X4_2[n4_2, 0] = rx; X4_2[n4_2, 1] = rgx; X4_2[n4_2, 2] = X4_1[k, 2]; X4_2[n4_2, 3] = X4_1[k, 3]; X4_2[n4_2, 4] = ro2
                    n4_2 += 1
            if n4_2 == 0: continue

            n5_2 = 0
            for k in range(n5_1):
                rx = X5_1[k, 0]; rgx = X5_1[k, 1]; ro2 = X5_1[k, 4]
                if (rx & col_u2_012) == z64 and (ro2 & o2_2) == z64 and eq_bits(rx & x2, 1) and eq_bits(rx & gx2, 2):
                    X5_2[n5_2, 0] = rx; X5_2[n5_2, 1] = rgx; X5_2[n5_2, 2] = X5_1[k, 2]; X5_2[n5_2, 3] = X5_1[k, 3]; X5_2[n5_2, 4] = ro2
                    n5_2 += 1
            if n5_2 == 0: continue

            n6_2 = 0
            for k in range(n6_1):
                rx = X6_1[k, 0]; rgx = X6_1[k, 1]; ro2 = X6_1[k, 4]
                if (rx & col_u2_012) == z64 and (ro2 & o2_2) == z64 and eq_bits(rx & x2, 1) and eq_bits(rx & gx2, 2):
                    X6_2[n6_2, 0] = rx; X6_2[n6_2, 1] = rgx; X6_2[n6_2, 2] = X6_1[k, 2]; X6_2[n6_2, 3] = X6_1[k, 3]; X6_2[n6_2, 4] = ro2
                    n6_2 += 1
            if n6_2 == 0: continue

            n7_2 = 0
            for k in range(n7_1):
                rx = X7_1[k, 0]; rgx = X7_1[k, 1]; ro2 = X7_1[k, 4]
                if (rx & col_u2_012) == z64 and (ro2 & o2_2) == z64 and eq_bits(rx & x2, 1) and eq_bits(rx & gx2, 2):
                    X7_2[n7_2, 0] = rx; X7_2[n7_2, 1] = rgx; X7_2[n7_2, 2] = X7_1[k, 2]; X7_2[n7_2, 3] = X7_1[k, 3]; X7_2[n7_2, 4] = ro2
                    n7_2 += 1
            if n7_2 == 0: continue

            for idx3 in range(n3_1):
                i3 = c3_1[idx3]
                if (cut_012 & L3[i3, 2]) != z64 or (L3[i3, 4] & u1_012) != z64 or (L3[i3, 3] & u2_012) != z64:
                    continue
                x3, gx3, o2_3 = L3[i3, 0], L3[i3, 1], L3[i3, 4]
                if not (eq_bits(x2 & x3, Gp[2, 3]) and eq_bits(x2 & gx3, KW0[2, 3])):
                    continue

                if n_stab012 > 0:
                    is_rep3 = True
                    for s_i in range(n_stab012):
                        if apply_lut(x3, luts_g01[stab012_idx[s_i]]) < x3:
                            is_rep3 = False
                            break
                    if not is_rep3: continue

                n_stab0123 = 0
                for s_i in range(n_stab012):
                    p_idx = stab012_idx[s_i]
                    if is_g01234_flag[p_idx] == 1:
                        if apply_lut(x3, luts_g01[p_idx]) == x3:
                            stab0123_idx[n_stab0123] = p_idx
                            n_stab0123 += 1

                local_b1 += 1
                col_u1_B1 = x0 | x1 | x2 | x3
                col_u2_B1 = col_u2_012 | ((x0 | x1 | x2) & x3)
                g_col_u2_B1 = (gx0 & gx1) | (gx0 & gx2) | (gx0 & gx3) | (gx1 & gx2) | (gx1 & gx3) | (gx2 & gx3)
                orb_p_B1 = orb_p_01 | o2_2 | o2_3

                req2_B2 = O33_mask & (~col_u1_B1)
                req1_B2 = (O33_mask & (~col_u2_B1)) | (O13_mask & (~col_u1_B1)) | (O23_mask & g_col_u2_B1)

                n4_3 = 0; or4 = z64
                for k in range(n4_2):
                    rx = X4_2[k, 0]; rgx = X4_2[k, 1]; ro2 = X4_2[k, 4]
                    if (rx & col_u2_B1) == z64 and (ro2 & o2_3) == z64 and eq_bits(rx & x3, 1) and eq_bits(rx & gx3, 2):
                        if n_stab0123 > 0:
                            is_rep4 = True
                            for s_i in range(n_stab0123):
                                if apply_lut(rx, luts_g01[stab0123_idx[s_i]]) < rx:
                                    is_rep4 = False
                                    break
                            if not is_rep4: continue
                        X4_3[n4_3, 0] = rx; X4_3[n4_3, 1] = rgx; X4_3[n4_3, 2] = X4_2[k, 2]; X4_3[n4_3, 3] = X4_2[k, 3]; X4_3[n4_3, 4] = ro2
                        n4_3 += 1
                        or4 |= rx
                if n4_3 == 0: continue

                n5_3 = 0; or5 = z64
                for k in range(n5_2):
                    rx = X5_2[k, 0]; rgx = X5_2[k, 1]; ro2 = X5_2[k, 4]
                    if (rx & col_u2_B1) == z64 and (ro2 & o2_3) == z64 and eq_bits(rx & x3, 1) and eq_bits(rx & gx3, 2):
                        X5_3[n5_3, 0] = rx; X5_3[n5_3, 1] = rgx; X5_3[n5_3, 2] = X5_2[k, 2]; X5_3[n5_3, 3] = X5_2[k, 3]; X5_3[n5_3, 4] = ro2
                        n5_3 += 1
                        or5 |= rx
                if n5_3 == 0: continue

                n6_3 = 0; or6 = z64
                for k in range(n6_2):
                    rx = X6_2[k, 0]; rgx = X6_2[k, 1]; ro2 = X6_2[k, 4]
                    if (rx & col_u2_B1) == z64 and (ro2 & o2_3) == z64 and eq_bits(rx & x3, 1) and eq_bits(rx & gx3, 2):
                        X6_3[n6_3, 0] = rx; X6_3[n6_3, 1] = rgx; X6_3[n6_3, 2] = X6_2[k, 2]; X6_3[n6_3, 3] = X6_2[k, 3]; X6_3[n6_3, 4] = ro2
                        n6_3 += 1
                        or6 |= rx
                if n6_3 == 0: continue

                n7_3 = 0; or7 = z64
                for k in range(n7_2):
                    rx = X7_2[k, 0]; rgx = X7_2[k, 1]; ro2 = X7_2[k, 4]
                    if (rx & col_u2_B1) == z64 and (ro2 & o2_3) == z64 and eq_bits(rx & x3, 1) and eq_bits(rx & gx3, 2):
                        X7_3[n7_3, 0] = rx; X7_3[n7_3, 1] = rgx; X7_3[n7_3, 2] = X7_2[k, 2]; X7_3[n7_3, 3] = X7_2[k, 3]; X7_3[n7_3, 4] = ro2
                        n7_3 += 1
                        or7 |= rx
                if n7_3 == 0: continue

                all_or = or4 | or5 | or6 | or7
                if (all_or & req1_B2) != req1_B2: continue
                pair_or = (or4 & or5) | (or4 & or6) | (or4 & or7) | (or5 & or6) | (or5 & or7) | (or6 & or7)
                if (pair_or & req2_B2) != req2_B2: continue

                for idx4 in range(n4_3):
                    x4, gx4, cut4, o1_4, o2_4 = X4_3[idx4, 0], X4_3[idx4, 1], X4_3[idx4, 2], X4_3[idx4, 3], X4_3[idx4, 4]
                    b2_u1_4 = o1_4 | o2_4
                    b2_u2_4 = o2_4
                    col_u2_4 = col_u2_B1 | (col_u1_B1 & x4)
                    col_u1_4 = col_u1_B1 | x4
                    for idx5 in range(n5_3):
                        x5, gx5, cut5, o1_5, o2_5 = X5_3[idx5, 0], X5_3[idx5, 1], X5_3[idx5, 2], X5_3[idx5, 3], X5_3[idx5, 4]
                        if (x5 & col_u2_4) != z64 or (cut4 & cut5) != z64 or (o2_5 & b2_u1_4) != z64 or (o1_5 & b2_u2_4) != z64:
                            continue
                        if not (eq_bits(x4 & x5, Gp[4, 5]) and eq_bits(x4 & gx5, KW0[4, 5])):
                            continue
                        cut_45 = cut4 | cut5
                        b2_u2_45 = b2_u2_4 | o2_5 | (b2_u1_4 & o1_5)
                        b2_u1_45 = b2_u1_4 | o1_5 | o2_5
                        col_u2_45 = col_u2_4 | (col_u1_4 & x5)
                        col_u1_45 = col_u1_4 | x5
                        for idx6 in range(n6_3):
                            x6, gx6, cut6, o1_6, o2_6 = X6_3[idx6, 0], X6_3[idx6, 1], X6_3[idx6, 2], X6_3[idx6, 3], X6_3[idx6, 4]
                            if (x6 & col_u2_45) != z64 or (cut_45 & cut6) != z64 or (o2_6 & b2_u1_45) != z64 or (o1_6 & b2_u2_45) != z64:
                                continue
                            if not (eq_bits(x4 & x6, Gp[4, 6]) and eq_bits(x4 & gx6, KW0[4, 6])):
                                continue
                            if not (eq_bits(x5 & x6, Gp[5, 6]) and eq_bits(x5 & gx6, KW0[5, 6])):
                                continue
                            cut_456 = cut_45 | cut6
                            b2_u2_456 = b2_u2_45 | o2_6 | (b2_u1_45 & o1_6)
                            b2_u1_456 = b2_u1_45 | o1_6 | o2_6
                            col_u2_456 = col_u2_45 | (col_u1_45 & x6)
                            col_u1_456 = col_u1_45 | x6
                            for idx7 in range(n7_3):
                                x7, gx7, cut7, o1_7, o2_7 = X7_3[idx7, 0], X7_3[idx7, 1], X7_3[idx7, 2], X7_3[idx7, 3], X7_3[idx7, 4]
                                if (x7 & col_u2_456) != z64 or (cut_456 & cut7) != z64 or (o2_7 & b2_u1_456) != z64 or (o1_7 & b2_u2_456) != z64:
                                    continue
                                if not (eq_bits(x4 & x7, Gp[4, 7]) and eq_bits(x4 & gx7, KW0[4, 7])):
                                    continue
                                if not (eq_bits(x5 & x7, Gp[5, 7]) and eq_bits(x5 & gx7, KW0[5, 7])):
                                    continue
                                if not (eq_bits(x6 & x7, Gp[6, 7]) and eq_bits(x6 & gx7, KW0[6, 7])):
                                    continue

                                local_b2 += 1
                                col_u2_B12 = col_u2_456 | (col_u1_456 & x7)
                                orb_p_B12 = orb_p_B1 | o2_4 | o2_5 | o2_6 | o2_7

                                n8_7 = 0
                                for k in range(n8_0):
                                    ri = c8_0[k]; rx = L8[ri, 0]
                                    if (rx & col_u2_B12) != z64 or (L8[ri, 4] & orb_p_B12) != z64: continue
                                    if (eq_bits(rx & x1, 1) and eq_bits(rx & x2, 1) and eq_bits(rx & x3, 1) and
                                        eq_bits(rx & x4, 1) and eq_bits(rx & x5, 1) and eq_bits(rx & x6, 1) and eq_bits(rx & x7, 1)):
                                        if (eq_bits(rx & gx1, 2) and eq_bits(rx & gx2, 2) and eq_bits(rx & gx3, 2) and
                                            eq_bits(rx & gx4, 2) and eq_bits(rx & gx5, 2) and eq_bits(rx & gx6, 2) and eq_bits(rx & gx7, 2)):
                                            c8_7[n8_7] = ri; n8_7 += 1
                                if n8_7 == 0: continue

                                n9_7 = 0
                                for k in range(n9_0):
                                    ri = c9_0[k]; rx = L9[ri, 0]
                                    if (rx & col_u2_B12) != z64 or (L9[ri, 4] & orb_p_B12) != z64: continue
                                    if (eq_bits(rx & x1, 1) and eq_bits(rx & x2, 1) and eq_bits(rx & x3, 1) and
                                        eq_bits(rx & x4, 1) and eq_bits(rx & x5, 1) and eq_bits(rx & x6, 1) and eq_bits(rx & x7, 1)):
                                        if (eq_bits(rx & gx1, 2) and eq_bits(rx & gx2, 2) and eq_bits(rx & gx3, 2) and
                                            eq_bits(rx & gx4, 2) and eq_bits(rx & gx5, 2) and eq_bits(rx & gx6, 2) and eq_bits(rx & gx7, 2)):
                                            c9_7[n9_7] = ri; n9_7 += 1
                                if n9_7 == 0: continue

                                n10_7 = 0
                                for k in range(n10_0):
                                    ri = c10_0[k]; rx = L10[ri, 0]
                                    if (rx & col_u2_B12) != z64 or (L10[ri, 4] & orb_p_B12) != z64: continue
                                    if (eq_bits(rx & x1, 1) and eq_bits(rx & x2, 1) and eq_bits(rx & x3, 1) and
                                        eq_bits(rx & x4, 1) and eq_bits(rx & x5, 1) and eq_bits(rx & x6, 1) and eq_bits(rx & x7, 1)):
                                        if (eq_bits(rx & gx1, 2) and eq_bits(rx & gx2, 2) and eq_bits(rx & gx3, 2) and
                                            eq_bits(rx & gx4, 2) and eq_bits(rx & gx5, 2) and eq_bits(rx & gx6, 2) and eq_bits(rx & gx7, 2)):
                                            c10_7[n10_7] = ri; n10_7 += 1
                                if n10_7 == 0: continue

                                n11_7 = 0
                                for k in range(n11_0):
                                    ri = c11_0[k]; rx = L11[ri, 0]
                                    if (rx & col_u2_B12) != z64 or (L11[ri, 4] & orb_p_B12) != z64: continue
                                    if (eq_bits(rx & x1, 1) and eq_bits(rx & x2, 1) and eq_bits(rx & x3, 1) and
                                        eq_bits(rx & x4, 1) and eq_bits(rx & x5, 1) and eq_bits(rx & x6, 1) and eq_bits(rx & x7, 1)):
                                        if (eq_bits(rx & gx1, 2) and eq_bits(rx & gx2, 2) and eq_bits(rx & gx3, 2) and
                                            eq_bits(rx & gx4, 2) and eq_bits(rx & gx5, 2) and eq_bits(rx & gx6, 2) and eq_bits(rx & gx7, 2)):
                                            c11_7[n11_7] = ri; n11_7 += 1
                                if n11_7 == 0: continue

                                for idx8 in range(n8_7):
                                    i8 = c8_7[idx8]; x8, gx8 = L8[i8, 0], L8[i8, 1]
                                    for idx9 in range(n9_7):
                                        i9 = c9_7[idx9]; x9, gx9 = L9[i9, 0], L9[i9, 1]
                                        if not (eq_bits(x8 & x9, Gp[8, 9]) and eq_bits(x8 & gx9, KW0[8, 9])): continue
                                        for idx10 in range(n10_7):
                                            i10 = c10_7[idx10]; x10, gx10 = L10[i10, 0], L10[i10, 1]
                                            if not (eq_bits(x8 & x10, Gp[8, 10]) and eq_bits(x8 & gx10, KW0[8, 10])): continue
                                            if not (eq_bits(x9 & x10, Gp[9, 10]) and eq_bits(x9 & gx10, KW0[9, 10])): continue
                                            for idx11 in range(n11_7):
                                                i11 = c11_7[idx11]; x11, gx11 = L11[i11, 0], L11[i11, 1]
                                                if not (eq_bits(x8 & x11, Gp[8, 11]) and eq_bits(x8 & gx11, KW0[8, 11])): continue
                                                if not (eq_bits(x9 & x11, Gp[9, 11]) and eq_bits(x9 & gx11, KW0[9, 11])): continue
                                                if not (eq_bits(x10 & x11, Gp[10, 11]) and eq_bits(x10 & gx11, KW0[10, 11])): continue
                                                if ((col_u2_B12 | (x8 & x9) | (x8 & x10) | (x8 & x11) | (x9 & x10) | (x9 & x11) | (x10 & x11)) == np.uint64((1 << 60) - 1)):
                                                    local_b3 += 1

    out[0] = local_b1
    out[1] = local_b2
    out[2] = local_b3
    return out

@njit(parallel=True)
def solve_222_chiral_cpu(
    n_test, reps, rep_canons, same_b12,
    L0, L1, c1_can, L2, c2_can, L3, c3_can,
    L4, c4_can, L5, c5_can, L6, c6_can, L7, c7_can,
    L8, L9, L10, L11,
    Gp, KW0, O33_mask, O13_mask, O23_mask,
    luts_g01, is_g012_flag, is_g0123_flag, is_g01234_flag, luts_swap01
):
    counts = np.zeros((n_test, 3), dtype=np.int64)
    for idx_rep in prange(n_test):
        counts[idx_rep] = solve_single_rep_222(
            reps[idx_rep], rep_canons[idx_rep], same_b12,
            L0, L1, c1_can, L2, c2_can, L3, c3_can,
            L4, c4_can, L5, c5_can, L6, c6_can, L7, c7_can,
            L8, L9, L10, L11,
            Gp, KW0, O33_mask, O13_mask, O23_mask,
            luts_g01, is_g012_flag, is_g0123_flag, is_g01234_flag, luts_swap01
        )
    return counts.sum(axis=0)

def comp_priority(M, E, KW0, comp):
    sub_kw = KW0[np.ix_(comp, comp)]
    if sub_kw[0, 0] == 0:
        return 2
    if np.sum(sub_kw == 2) == 8:
        return 0
    return 1

def main():
    t_start = time.time()
    F12, I12, J12, b6_perms, orbits_by_sig = build_orbits()
    orbits_222 = orbits_by_sig["kt1=0_2+2+2"]

    b2_perms_4 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(2)) for flips in product((0, 1), repeat=2)
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

    def get_comp_orb_masks(I_B_set):
        cut_m = 0; out_m = 0
        for idx_m, (c, gc) in enumerate(orbs_30):
            u, v = cols_60[c]
            cnt_in = (1 if u in I_B_set else 0) + (1 if v in I_B_set else 0)
            if cnt_in == 1: cut_m |= (1 << idx_m)
            elif cnt_in == 0: out_m |= (1 << idx_m)
        return cut_m, out_m

    row_pool_cache = {}
    def gen_2block_rows_cached(I_B_tuple, target_deg, diag_kw):
        key = (I_B_tuple, target_deg, diag_kw)
        if key in row_pool_cache: return row_pool_cache[key]
        I_B_set = set(I_B_tuple)
        cut_orb_mask, out_orb_mask = get_comp_orb_masks(I_B_set)
        req_pairs = diag_kw // 2
        ok_cols = [
            c for c in range(60)
            if not (cols_60[c][0] in I_B_set and cols_60[c][1] in I_B_set)
            and target_deg[cols_60[c][0]] > 0
            and target_deg[cols_60[c][1]] > 0
        ]
        adj_cols = [[] for _ in range(12)]
        for c in ok_cols:
            u, v = cols_60[c]; adj_cols[min(u, v)].append((c, max(u, v)))
        rem_deg = list(target_deg); chosen = []; res = []
        def bt_v(v_idx):
            if v_idx == 12:
                if len(chosen) == 10:
                    r_set = set(chosen)
                    npairs = 0; ok_p = True
                    for c in chosen:
                        if c < g_col[c] and g_col[c] in r_set:
                            npairs += 1
                            if cols_60[c][0] in I_B_set or cols_60[c][1] in I_B_set:
                                ok_p = False; break
                    if ok_p and npairs == req_pairs:
                        xm = gxm = c1_cut = c1_out = c2_out = 0
                        for c in chosen:
                            xm |= 1 << c; gxm |= 1 << g_col[c]
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if (cut_orb_mask >> idx_m) & 1:
                                if s == 1: c1_cut |= 1 << idx_m
                            elif (out_orb_mask >> idx_m) & 1:
                                if s == 1: c1_out |= 1 << idx_m
                                elif s == 2: c2_out |= 1 << idx_m
                        res.append((xm, gxm, c1_cut, c1_out, c2_out))
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
        row_pool_cache[key] = arr
        return arr

    orbit_order = [6, 3, 7, 1, 4, 0, 2, 8, 5, 9]
    total_b1 = 0; total_b2 = 0; total_b3 = 0

    for run_i, orb_idx in enumerate(orbit_order):
        M_orig, E_orig, Gp_orig, KW0_orig, Delta0_orig, comps_orig = orbits_222[orb_idx]
        # Order components: put duplicate B or A first as (B1, B2), but NEVER put C before B or A!
        ctypes_orig = [comp_priority(M_orig, E_orig, KW0_orig, c) for c in comps_orig]
        from collections import Counter
        cnt = Counter(ctypes_orig)
        comps_idx = sorted(range(3), key=lambda k: (1 if ctypes_orig[k] == 2 else 0, -1 if cnt[ctypes_orig[k]] >= 2 else 0, ctypes_orig[k]))
        comps_sorted = [comps_orig[k] for k in comps_idx]
        perm = [u for c in comps_sorted for u in c]
        M = M_orig[np.ix_(perm, perm)]
        E = E_orig[np.ix_(perm, perm)]
        Gp = Gp_orig[np.ix_(perm, perm)]
        KW0 = KW0_orig[np.ix_(perm, perm)]
        Delta0 = 2 * J12 - I12 - F12 - M - (E @ F12)
        comps = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
        ctypes = [comp_priority(M, E, KW0, c) for c in comps]
        cname_map = {0: "B", 1: "A", 2: "C"}
        csig = "+".join(cname_map[ct] for ct in comps_idx and ctypes)
        same_b12 = 1 if ctypes[0] == ctypes[1] else 0

        # Within each 4-row component, order rows for tightest constraints first
        Gp_off = (Gp - 2 * I12).astype(np.int32)
        KW0_int = KW0.astype(np.int32)

        L = []
        for c_idx, comp in enumerate(comps):
            I_B = tuple(comp)
            for i in comp:
                L.append(gen_2block_rows_cached(I_B, tuple(int(Delta0[i, j]) for j in range(12)), int(KW0[i, i])))

        B1_set = set(comps[0]); B2_set = set(comps[1]); B3_set = set(comps[2])
        O33_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in B3_set and v in B3_set))
        O13_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in B1_set and v in B3_set) or (u in B3_set and v in B1_set)))
        O23_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in B2_set and v in B3_set) or (u in B3_set and v in B2_set)))

        # Build decoupled stabilizer G = Stab_{S4 x B2}(B1) x Stab_{S4 x B2}(B2) x Stab_{B2}^{col}(B3)
        def get_stab_comp(comp):
            gp_c = Gp_off[np.ix_(comp, comp)]
            kw_c = KW0_int[np.ix_(comp, comp)]
            d_c = Delta0[np.ix_(comp, comp)]
            lens_c = [len(L[u]) for u in comp]
            st = []
            for pr in permutations(range(4)):
                if any(lens_c[pr[a]] != lens_c[a] for a in range(4)): continue
                if not (gp_c == gp_c[np.ix_(pr, pr)]).all() or not (kw_c == kw_c[np.ix_(pr, pr)]).all(): continue
                for pc in b2_perms_4:
                    if (d_c == d_c[np.ix_(pr, pc)]).all():
                        st.append((pr, pc))
            return st

        st1 = get_stab_comp(comps[0])
        st2 = get_stab_comp(comps[1])
        # For B3, column permutations pc3 in B2(B3) that preserve Delta0[B3, B3] up to a row permutation pr3 of B3!
        # Wait: if (pr3, pc3) in get_stab_comp(comps[2]), then applying pc3 to columns of B3 permutes rows L8..L11 by pr3,
        # which preserves the existence of a valid 4-tuple (x8, x9, x10, x11) in L8 x L9 x L10 x L11!
        st3 = get_stab_comp(comps[2])
        pc3_set = sorted(set(pc3 for (pr3, pc3) in st3))

        def make_cmap(pc1, pc2, pc3):
            p12 = [pc1[j] for j in range(4)] + [4 + pc2[j] for j in range(4)] + [8 + pc3[j] for j in range(4)]
            return np.array([col_idx[(p12[j1], p12[j2])] for (j1, j2) in cols_60], dtype=np.int32)

        # For single-row canonical masks of B1 (L0..L3) and B2 (L4..L7):
        stab_a_to_0 = [[] for _ in range(8)]
        for (pr1, pc1) in st1:
            a = pr1.index(0)
            for (pr2, pc2) in st2:
                for pc3 in pc3_set:
                    stab_a_to_0[a].append(make_cmap(pc1, pc2, pc3))
        if same_b12 == 1:
            # Also include swapping B1 <-> B2!
            for (pr1, pc1) in st1:
                for (pr2, pc2) in st2:
                    a = 4 + pr2.index(0)
                    for pc3 in pc3_set:
                        p12 = [4 + pc1[j] for j in range(4)] + [pc2[j] for j in range(4)] + [8 + pc3[j] for j in range(4)]
                        cmap = np.array([col_idx[(p12[j1], p12[j2])] for (j1, j2) in cols_60], dtype=np.int32)
                        stab_a_to_0[a].append(cmap)

        luts_a = [build_perm_luts(x) for x in stab_a_to_0]
        c_cans = [compute_canons_lut(L[a], luts_a[a]) if len(stab_a_to_0[a]) > 0 else np.full(len(L[a]), np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64) for a in range(8)]
        reps = np.array([i for i in range(len(L[0])) if L[0][i, 0] == c_cans[0][i]], dtype=np.int32)
        rep_canons = np.array([c_cans[0][i] for i in reps], dtype=np.uint64)

        # Build g01 tower (pr1[0]==0, pr1[1]==1) and swap01 (pr1[0]==1, pr1[1]==0)
        seen_g01 = {}
        for (pr1, pc1) in st1:
            if pr1[0] == 0 and pr1[1] == 1:
                f2 = 1 if pr1[2] == 2 else 0
                f3 = 1 if (pr1[2] == 2 and pr1[3] == 3) else 0
                for (pr2, pc2) in st2:
                    f4 = 1 if (f3 == 1 and pr2[0] == 0) else 0
                    for pc3 in pc3_set:
                        cm = make_cmap(pc1, pc2, pc3)
                        k = tuple(cm.tolist())
                        if k not in seen_g01:
                            seen_g01[k] = [cm, f2, f3, f4]
                        else:
                            if f2 > seen_g01[k][1]: seen_g01[k][1] = f2
                            if f3 > seen_g01[k][2]: seen_g01[k][2] = f3
                            if f4 > seen_g01[k][3]: seen_g01[k][3] = f4

        g01_items = sorted(seen_g01.values(), key=lambda x: (-x[3], -x[2], -x[1]))
        id_tuple = tuple(range(60))
        g01_non_id = [it for it in g01_items if tuple(it[0].tolist()) != id_tuple]
        g01_perms = [it[0] for it in g01_non_id]
        is_g012_flag = np.array([it[1] for it in g01_non_id], dtype=np.int32)
        is_g0123_flag = np.array([it[2] for it in g01_non_id], dtype=np.int32)
        is_g01234_flag = np.array([it[3] for it in g01_non_id], dtype=np.int32)

        seen_sw = {}
        for (pr1, pc1) in st1:
            if pr1[0] == 1 and pr1[1] == 0:
                for (pr2, pc2) in st2:
                    for pc3 in pc3_set:
                        cm = make_cmap(pc1, pc2, pc3)
                        k = tuple(cm.tolist())
                        if k not in seen_sw: seen_sw[k] = cm
        swap01_perms = list(seen_sw.values())

        luts_g01 = build_perm_luts(g01_perms)
        luts_swap01 = build_perm_luts(swap01_perms)

        if run_i == 0:
            _ = solve_222_chiral_cpu(
                min(2, len(reps)), reps, rep_canons, same_b12,
                L[0], L[1], c_cans[1], L[2], c_cans[2], L[3], c_cans[3],
                L[4], c_cans[4], L[5], c_cans[5], L[6], c_cans[6], L[7], c_cans[7],
                L[8], L[9], L[10], L[11],
                Gp_off, KW0_int, O33_mask, O13_mask, O23_mask,
                luts_g01, is_g012_flag, is_g0123_flag, is_g01234_flag, luts_swap01
            )

        t_orb = time.time()
        res = solve_222_chiral_cpu(
            len(reps), reps, rep_canons, same_b12,
            L[0], L[1], c_cans[1], L[2], c_cans[2], L[3], c_cans[3],
            L[4], c_cans[4], L[5], c_cans[5], L[6], c_cans[6], L[7], c_cans[7],
            L[8], L[9], L[10], L[11],
            Gp_off, KW0_int, O33_mask, O13_mask, O23_mask,
            luts_g01, is_g012_flag, is_g0123_flag, is_g01234_flag, luts_swap01
        )
        dt = time.time() - t_orb
        nb1, nb2, nb3 = int(res[0]), int(res[1]), int(res[2])
        total_b1 += nb1; total_b2 += nb2; total_b3 += nb3
        print(
            f"[{run_i+1:2d}/10] Orbit {orb_idx} ({csig}): |G|={len(stab_a_to_0[0])}, reps={len(reps):4d}, "
            f"b1_sols={nb1:8d}, b12_sols={nb2:6d}, b123_sols={nb3} in {dt:.2f}s "
            f"(elapsed={time.time()-t_start:.2f}s)",
            flush=True
        )

    print(f"\nALL 10 ORBITS OF 2+2+2 COMPLETE in {time.time()-t_start:.2f}s: total_b1={total_b1:,}, total_b12={total_b2:,}, total_b123={total_b3}", flush=True)

if __name__ == "__main__":
    main()
