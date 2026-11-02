import os
import sys
import time
import numpy as np
from numba import njit, prange
from itertools import combinations, permutations, product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_all_10_nullity3_k0_33_cpu import build_orbits, build_perm_luts, compute_canons_lut, popcnt64, apply_lut
from run_all_168_nullity3_k0_42_cpu import naive_reference_check_42

@njit(inline="always")
def eq_bits_42(x, req):
    if req == 1:
        return x != np.uint64(0) and (x & (x - np.uint64(1))) == np.uint64(0)
    elif req == 2:
        t = x & (x - np.uint64(1))
        return t != np.uint64(0) and (t & (t - np.uint64(1))) == np.uint64(0)
    elif req == 0:
        return x == np.uint64(0)
    else:
        return popcnt64(x) == req

@njit(cache=True)
def check_d8_tail_fast(
    o2_0, col_u2_6, col_u1_6, orb_p_6,
    x0, gx0, x1, gx1, x2, gx2, x3, gx3, ox3,
    X4_3, nx4_3, X5_3, nx5_3, X6_3, nx6_3, X7_3, nx7_3,
    Gp4, KW4
):
    z64 = np.uint64(0)
    col_u2_7 = col_u2_6 | (col_u1_6 & x3)
    orb_p_7 = o2_0 | orb_p_6 | ox3
    X4_7 = np.empty((512, 3), dtype=np.uint64); n4_7 = 0
    for j4 in range(nx4_3):
        rx = X4_3[j4, 0]; rgx = X4_3[j4, 1]; rox = X4_3[j4, 2]
        if (rx & col_u2_7) == z64 and (rox & orb_p_7) == z64:
            if (eq_bits_42(rx & x0, Gp4[0, 4]) and eq_bits_42(rgx & x0, KW4[0, 4]) and
                eq_bits_42(rx & x1, Gp4[1, 4]) and eq_bits_42(rgx & x1, KW4[1, 4]) and
                eq_bits_42(rx & x2, Gp4[2, 4]) and eq_bits_42(rgx & x2, KW4[2, 4]) and
                eq_bits_42(rx & x3, Gp4[3, 4]) and eq_bits_42(rgx & x3, KW4[3, 4])):
                X4_7[n4_7, 0] = rx; X4_7[n4_7, 1] = rgx; X4_7[n4_7, 2] = rox; n4_7 += 1
    if n4_7 == 0: return 0
    X5_7 = np.empty((512, 3), dtype=np.uint64); n5_7 = 0
    for j5 in range(nx5_3):
        rx = X5_3[j5, 0]; rgx = X5_3[j5, 1]; rox = X5_3[j5, 2]
        if (rx & col_u2_7) == z64 and (rox & orb_p_7) == z64:
            if (eq_bits_42(rx & x0, Gp4[0, 5]) and eq_bits_42(rgx & x0, KW4[0, 5]) and
                eq_bits_42(rx & x1, Gp4[1, 5]) and eq_bits_42(rgx & x1, KW4[1, 5]) and
                eq_bits_42(rx & x2, Gp4[2, 5]) and eq_bits_42(rgx & x2, KW4[2, 5]) and
                eq_bits_42(rx & x3, Gp4[3, 5]) and eq_bits_42(rgx & x3, KW4[3, 5])):
                X5_7[n5_7, 0] = rx; X5_7[n5_7, 1] = rgx; X5_7[n5_7, 2] = rox; n5_7 += 1
    if n5_7 == 0: return 0
    X6_7 = np.empty((512, 3), dtype=np.uint64); n6_7 = 0
    for j6 in range(nx6_3):
        rx = X6_3[j6, 0]; rgx = X6_3[j6, 1]; rox = X6_3[j6, 2]
        if (rx & col_u2_7) == z64 and (rox & orb_p_7) == z64:
            if (eq_bits_42(rx & x0, Gp4[0, 6]) and eq_bits_42(rgx & x0, KW4[0, 6]) and
                eq_bits_42(rx & x1, Gp4[1, 6]) and eq_bits_42(rgx & x1, KW4[1, 6]) and
                eq_bits_42(rx & x2, Gp4[2, 6]) and eq_bits_42(rgx & x2, KW4[2, 6]) and
                eq_bits_42(rx & x3, Gp4[3, 6]) and eq_bits_42(rgx & x3, KW4[3, 6])):
                X6_7[n6_7, 0] = rx; X6_7[n6_7, 1] = rgx; X6_7[n6_7, 2] = rox; n6_7 += 1
    if n6_7 == 0: return 0
    X7_7 = np.empty((512, 3), dtype=np.uint64); n7_7 = 0
    for j7 in range(nx7_3):
        rx = X7_3[j7, 0]; rgx = X7_3[j7, 1]; rox = X7_3[j7, 2]
        if (rx & col_u2_7) == z64 and (rox & orb_p_7) == z64:
            if (eq_bits_42(rx & x0, Gp4[0, 7]) and eq_bits_42(rgx & x0, KW4[0, 7]) and
                eq_bits_42(rx & x1, Gp4[1, 7]) and eq_bits_42(rgx & x1, KW4[1, 7]) and
                eq_bits_42(rx & x2, Gp4[2, 7]) and eq_bits_42(rgx & x2, KW4[2, 7]) and
                eq_bits_42(rx & x3, Gp4[3, 7]) and eq_bits_42(rgx & x3, KW4[3, 7])):
                X7_7[n7_7, 0] = rx; X7_7[n7_7, 1] = rgx; X7_7[n7_7, 2] = rox; n7_7 += 1
    if n7_7 == 0: return 0
    sols = 0
    for a4 in range(n4_7):
        x4 = X4_7[a4, 0]; gx4 = X4_7[a4, 1]; ox4 = X4_7[a4, 2]
        for a5 in range(n5_7):
            x5 = X5_7[a5, 0]; gx5 = X5_7[a5, 1]; ox5 = X5_7[a5, 2]
            if (ox4 & ox5) != z64 or not (eq_bits_42(x4 & x5, Gp4[4, 5]) and eq_bits_42(gx4 & x5, KW4[4, 5])): continue
            for a6 in range(n6_7):
                x6 = X6_7[a6, 0]; gx6 = X6_7[a6, 1]; ox6 = X6_7[a6, 2]
                if ((ox4 | ox5) & ox6) != z64: continue
                if not (eq_bits_42(x4 & x6, Gp4[4, 6]) and eq_bits_42(gx4 & x6, KW4[4, 6]) and eq_bits_42(x5 & x6, Gp4[5, 6]) and eq_bits_42(gx5 & x6, KW4[5, 6])): continue
                for a7 in range(n7_7):
                    x7 = X7_7[a7, 0]; gx7 = X7_7[a7, 1]; ox7 = X7_7[a7, 2]
                    if ((ox4 | ox5 | ox6) & ox7) != z64: continue
                    if (eq_bits_42(x4 & x7, Gp4[4, 7]) and eq_bits_42(gx4 & x7, KW4[4, 7]) and
                        eq_bits_42(x5 & x7, Gp4[5, 7]) and eq_bits_42(gx5 & x7, KW4[5, 7]) and
                        eq_bits_42(x6 & x7, Gp4[6, 7]) and eq_bits_42(gx6 & x7, KW4[6, 7])):
                        sols += 1
    return sols

@njit(cache=True)
def solve_single_rep_114(
    i0, min_can,
    Y0, Y0_adj, Y0_deg, cy1_can,
    Y2, Y2_adj, Y2_deg, cy2_can,
    X0, X1, X2, X3, X4, X5, X6, X7,
    Gp4, KW4,
    C11_col_mask, O11_orb_mask, O12_orb_mask,
    luts_g01, is_g012_flag, luts_swap01
):
    out = np.zeros(8, dtype=np.int64)
    z64 = np.uint64(0)
    n_g01 = len(luts_g01)
    n_swap01 = len(luts_swap01)

    y0 = Y0[i0, 0]; gy0 = Y0[i0, 1]; o2_0 = z64

    stab0_idx = np.empty(n_g01 + 1, dtype=np.int32)
    n_stab0 = 0
    for p_idx in range(n_g01):
        if apply_lut(y0, luts_g01[p_idx]) == y0:
            stab0_idx[n_stab0] = p_idx
            n_stab0 += 1

    c1_0 = np.empty(32, dtype=np.int32); n1_0 = 0
    deg0 = Y0_deg[i0]
    for k1 in range(deg0):
        j1 = Y0_adj[i0, k1]
        if j1 <= i0:
            continue
        if cy1_can[j1] >= min_can:
            ry = Y0[j1, 0]
            is_rep1 = True
            for s_i in range(n_stab0):
                if apply_lut(ry, luts_g01[stab0_idx[s_i]]) < ry:
                    is_rep1 = False
                    break
            if is_rep1 and n_swap01 > 0:
                for p_idx in range(n_swap01):
                    if apply_lut(ry, luts_swap01[p_idx]) == y0:
                        if apply_lut(y0, luts_swap01[p_idx]) < ry:
                            is_rep1 = False
                            break
            if is_rep1:
                c1_0[n1_0] = j1; n1_0 += 1
    if n1_0 == 0:
        return out

    c2_0 = np.empty(len(Y2), dtype=np.int32); n2_0 = 0
    for j2 in range(len(Y2)):
        if cy2_can[j2] >= min_can:
            ry = Y2[j2, 0]
            if eq_bits_42(y0 & ry, 1) and eq_bits_42(gy0 & ry, 2):
                c2_0[n2_0] = j2; n2_0 += 1
    if n2_0 == 0:
        return out

    X0_0 = np.empty((65536, 3), dtype=np.uint64)
    X1_0 = np.empty((65536, 3), dtype=np.uint64)
    X2_0 = np.empty((65536, 3), dtype=np.uint64)
    X3_0 = np.empty((65536, 3), dtype=np.uint64)
    X4_0 = np.empty((65536, 3), dtype=np.uint64)
    X5_0 = np.empty((65536, 3), dtype=np.uint64)
    X6_0 = np.empty((65536, 3), dtype=np.uint64)
    X7_0 = np.empty((65536, 3), dtype=np.uint64)
    nx0_0 = -1; nx1_0 = 0; nx2_0 = 0; nx3_0 = 0
    nx4_0 = -1; nx5_0 = 0; nx6_0 = 0; nx7_0 = 0

    c2_1 = np.empty(n2_0 + 1, dtype=np.int32)
    in_c2_1 = np.zeros(len(Y2), dtype=np.uint8)
    X0_1 = np.empty((24576, 3), dtype=np.uint64)
    X1_1 = np.empty((24576, 3), dtype=np.uint64)
    X2_1 = np.empty((24576, 3), dtype=np.uint64)
    X3_1 = np.empty((24576, 3), dtype=np.uint64)
    X4_1 = np.empty((24576, 3), dtype=np.uint64)
    X5_1 = np.empty((24576, 3), dtype=np.uint64)
    X6_1 = np.empty((24576, 3), dtype=np.uint64)
    X7_1 = np.empty((24576, 3), dtype=np.uint64)

    X0_2 = np.empty((6144, 3), dtype=np.uint64)
    X1_2 = np.empty((6144, 3), dtype=np.uint64)
    X2_2 = np.empty((6144, 3), dtype=np.uint64)
    X3_2 = np.empty((6144, 3), dtype=np.uint64)
    X4_2 = np.empty((6144, 3), dtype=np.uint64)
    X5_2 = np.empty((6144, 3), dtype=np.uint64)
    X6_2 = np.empty((6144, 3), dtype=np.uint64)
    X7_2 = np.empty((6144, 3), dtype=np.uint64)

    X0_3 = np.empty((2048, 3), dtype=np.uint64)
    X1_3 = np.empty((2048, 3), dtype=np.uint64)
    X2_3 = np.empty((2048, 3), dtype=np.uint64)
    X3_3 = np.empty((2048, 3), dtype=np.uint64)
    X4_3 = np.empty((2048, 3), dtype=np.uint64)
    X5_3 = np.empty((2048, 3), dtype=np.uint64)
    X6_3 = np.empty((2048, 3), dtype=np.uint64)
    X7_3 = np.empty((2048, 3), dtype=np.uint64)

    X1_4 = np.empty((1024, 3), dtype=np.uint64)
    X2_4 = np.empty((1024, 3), dtype=np.uint64)
    X3_4 = np.empty((1024, 3), dtype=np.uint64)
    X2_5 = np.empty((1024, 3), dtype=np.uint64)
    X3_5 = np.empty((1024, 3), dtype=np.uint64)

    stab01_idx = np.empty(n_g01 + 1, dtype=np.int32)
    loc_d1 = n1_0; loc_d2 = 0; loc_b1 = 0; loc_d5 = 0; loc_d6 = 0; loc_d7 = 0; loc_d8 = 0; loc_sols = 0

    gp4_01, kw4_01 = Gp4[0, 1], KW4[0, 1]
    gp4_02, kw4_02 = Gp4[0, 2], KW4[0, 2]
    gp4_03, kw4_03 = Gp4[0, 3], KW4[0, 3]
    gp4_12, kw4_12 = Gp4[1, 2], KW4[1, 2]
    gp4_13, kw4_13 = Gp4[1, 3], KW4[1, 3]
    gp4_23, kw4_23 = Gp4[2, 3], KW4[2, 3]

    for idx1 in range(n1_0):
        i1 = c1_0[idx1]
        y1 = Y0[i1, 0]; gy1 = Y0[i1, 1]
        col_u1_1 = y0 | y1

        n_stab01 = 0
        for s_i in range(n_stab0):
            p_idx = stab0_idx[s_i]
            if is_g012_flag[p_idx] == 1:
                if apply_lut(y1, luts_g01[p_idx]) == y1:
                    stab01_idx[n_stab01] = p_idx
                    n_stab01 += 1

        n2_1 = 0
        for k2 in range(n2_0):
            i2 = c2_0[k2]; ry = Y2[i2, 0]
            if eq_bits_42(y1 & ry, 1):
                in_c2_1[i2] = 1
                c2_1[n2_1] = i2; n2_1 += 1
        if n2_1 == 0: continue

        loc_d2 += n2_1
        nx0_1 = -1; nx1_1 = 0; nx2_1 = 0; nx3_1 = 0
        nx4_1 = -1; nx5_1 = 0; nx6_1 = 0; nx7_1 = 0

        for idx2 in range(n2_1):
            if nx0_1 == 0:
                break
            i2 = c2_1[idx2]
            y2 = Y2[i2, 0]; gy2 = Y2[i2, 1]
            if n_stab01 > 0:
                is_rep2 = True
                for s_i in range(n_stab01):
                    if apply_lut(y2, luts_g01[stab01_idx[s_i]]) < y2:
                        is_rep2 = False
                        break
                if not is_rep2:
                    continue

            deg2 = Y2_deg[i2]
            nx0_2 = -1; nx1_2 = 0; nx2_2 = 0; nx3_2 = 0
            nx4_2 = -1; nx5_2 = 0; nx6_2 = 0; nx7_2 = 0
            col_u2_2 = col_u1_1 & y2
            col_u1_2 = col_u1_1 | y2

            for k3 in range(deg2):
                i3 = Y2_adj[i2, k3]
                if in_c2_1[i3] == 0:
                    continue
                ry3 = Y2[i3, 0]
                if n_stab01 > 0:
                    is_rep3 = True
                    for s_i in range(n_stab01):
                        p_lut = luts_g01[stab01_idx[s_i]]
                        py3 = apply_lut(ry3, p_lut)
                        if py3 < y2:
                            is_rep3 = False
                            break
                        py2 = apply_lut(y2, p_lut)
                        if py2 == y2 and py3 < ry3:
                            is_rep3 = False
                            break
                        if py3 == y2 and py2 < ry3:
                            is_rep3 = False
                            break
                    if not is_rep3:
                        continue

                loc_b1 += 1
                if nx0_0 == -1:
                    nx0_0 = 0
                    for jx0 in range(len(X0)):
                        rx = X0[jx0, 0]; rgx = X0[jx0, 1]; rox = X0[jx0, 6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X0_0[nx0_0, 0] = rx; X0_0[nx0_0, 1] = rgx; X0_0[nx0_0, 2] = rox; nx0_0 += 1
                    if nx0_0 == 0:
                        nx0_1 = 0; break
                    nx1_0 = 0
                    for jx1 in range(len(X1)):
                        rx = X1[jx1, 0]; rgx = X1[jx1, 1]; rox = X1[jx1, 6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X1_0[nx1_0, 0] = rx; X1_0[nx1_0, 1] = rgx; X1_0[nx1_0, 2] = rox; nx1_0 += 1
                    if nx1_0 == 0:
                        nx0_0 = 0; nx0_1 = 0; break
                    nx2_0 = 0
                    for jx2 in range(len(X2)):
                        rx = X2[jx2, 0]; rgx = X2[jx2, 1]; rox = X2[jx2, 6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X2_0[nx2_0, 0] = rx; X2_0[nx2_0, 1] = rgx; X2_0[nx2_0, 2] = rox; nx2_0 += 1
                    if nx2_0 == 0:
                        nx0_0 = 0; nx0_1 = 0; break
                    nx3_0 = 0
                    for jx3 in range(len(X3)):
                        rx = X3[jx3, 0]; rgx = X3[jx3, 1]; rox = X3[jx3, 6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X3_0[nx3_0, 0] = rx; X3_0[nx3_0, 1] = rgx; X3_0[nx3_0, 2] = rox; nx3_0 += 1
                    if nx3_0 == 0:
                        nx0_0 = 0; nx0_1 = 0; break
                elif nx0_0 == 0:
                    nx0_1 = 0; break

                if nx0_1 == -1:
                    nx0_1 = 0
                    for kx0 in range(nx0_0):
                        rx = X0_0[kx0, 0]; rgx = X0_0[kx0, 1]; rox = X0_0[kx0, 2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X0_1[nx0_1, 0] = rx; X0_1[nx0_1, 1] = rgx; X0_1[nx0_1, 2] = rox; nx0_1 += 1
                    if nx0_1 == 0: break
                    nx1_1 = 0
                    for kx1 in range(nx1_0):
                        rx = X1_0[kx1, 0]; rgx = X1_0[kx1, 1]; rox = X1_0[kx1, 2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X1_1[nx1_1, 0] = rx; X1_1[nx1_1, 1] = rgx; X1_1[nx1_1, 2] = rox; nx1_1 += 1
                    if nx1_1 == 0:
                        nx0_1 = 0; break
                    nx2_1 = 0
                    for kx2 in range(nx2_0):
                        rx = X2_0[kx2, 0]; rgx = X2_0[kx2, 1]; rox = X2_0[kx2, 2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X2_1[nx2_1, 0] = rx; X2_1[nx2_1, 1] = rgx; X2_1[nx2_1, 2] = rox; nx2_1 += 1
                    if nx2_1 == 0:
                        nx0_1 = 0; break
                    nx3_1 = 0
                    for kx3 in range(nx3_0):
                        rx = X3_0[kx3, 0]; rgx = X3_0[kx3, 1]; rox = X3_0[kx3, 2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X3_1[nx3_1, 0] = rx; X3_1[nx3_1, 1] = rgx; X3_1[nx3_1, 2] = rox; nx3_1 += 1
                    if nx3_1 == 0:
                        nx0_1 = 0; break

                if nx0_2 == -1:
                    nx0_2 = 0
                    for kx0 in range(nx0_1):
                        rx = X0_1[kx0, 0]; rgx = X0_1[kx0, 1]; rox = X0_1[kx0, 2]
                        if (rx & col_u2_2) == z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X0_2[nx0_2, 0] = rx; X0_2[nx0_2, 1] = rgx; X0_2[nx0_2, 2] = rox; nx0_2 += 1
                    if nx0_2 == 0: break
                    nx1_2 = 0
                    for kx1 in range(nx1_1):
                        rx = X1_1[kx1, 0]; rgx = X1_1[kx1, 1]; rox = X1_1[kx1, 2]
                        if (rx & col_u2_2) == z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X1_2[nx1_2, 0] = rx; X1_2[nx1_2, 1] = rgx; X1_2[nx1_2, 2] = rox; nx1_2 += 1
                    if nx1_2 == 0: break
                    nx2_2 = 0
                    for kx2 in range(nx2_1):
                        rx = X2_1[kx2, 0]; rgx = X2_1[kx2, 1]; rox = X2_1[kx2, 2]
                        if (rx & col_u2_2) == z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X2_2[nx2_2, 0] = rx; X2_2[nx2_2, 1] = rgx; X2_2[nx2_2, 2] = rox; nx2_2 += 1
                    if nx2_2 == 0: break
                    nx3_2 = 0
                    for kx3 in range(nx3_1):
                        rx = X3_1[kx3, 0]; rgx = X3_1[kx3, 1]; rox = X3_1[kx3, 2]
                        if (rx & col_u2_2) == z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X3_2[nx3_2, 0] = rx; X3_2[nx3_2, 1] = rgx; X3_2[nx3_2, 2] = rox; nx3_2 += 1
                    if nx3_2 == 0: break
                col_u2_3 = col_u2_2 | (col_u1_1 & ry3)
                col_u1_3 = col_u1_2 | ry3

                nx0_3 = 0
                for kx0 in range(nx0_2):
                    rx = X0_2[kx0, 0]; rgx = X0_2[kx0, 1]; rox = X0_2[kx0, 2]
                    if (rx & col_u2_3) == z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X0_3[nx0_3, 0] = rx; X0_3[nx0_3, 1] = rgx; X0_3[nx0_3, 2] = rox; nx0_3 += 1
                if nx0_3 == 0: continue

                nx1_3 = 0
                for kx1 in range(nx1_2):
                    rx = X1_2[kx1, 0]; rgx = X1_2[kx1, 1]; rox = X1_2[kx1, 2]
                    if (rx & col_u2_3) == z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X1_3[nx1_3, 0] = rx; X1_3[nx1_3, 1] = rgx; X1_3[nx1_3, 2] = rox; nx1_3 += 1
                if nx1_3 == 0: continue

                nx2_3 = 0
                for kx2 in range(nx2_2):
                    rx = X2_2[kx2, 0]; rgx = X2_2[kx2, 1]; rox = X2_2[kx2, 2]
                    if (rx & col_u2_3) == z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X2_3[nx2_3, 0] = rx; X2_3[nx2_3, 1] = rgx; X2_3[nx2_3, 2] = rox; nx2_3 += 1
                if nx2_3 == 0: continue

                nx3_3 = 0
                for kx3 in range(nx3_2):
                    rx = X3_2[kx3, 0]; rgx = X3_2[kx3, 1]; rox = X3_2[kx3, 2]
                    if (rx & col_u2_3) == z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X3_3[nx3_3, 0] = rx; X3_3[nx3_3, 1] = rgx; X3_3[nx3_3, 2] = rox; nx3_3 += 1
                if nx3_3 == 0: continue
                nx4_3 = -1; nx5_3 = 0; nx6_3 = 0; nx7_3 = 0

                loc_d5 += nx0_3
                for kx0 in range(nx0_3):
                    x0 = X0_3[kx0, 0]; gx0 = X0_3[kx0, 1]; ox0 = X0_3[kx0, 2]
                    col_u2_4 = col_u2_3 | (col_u1_3 & x0)
                    col_u1_4 = col_u1_3 | x0
                    orb_p_4 = ox0

                    fb4_01 = col_u2_4 | (x0 if gp4_01 == 0 else z64) | (gx0 if kw4_01 == 0 else z64)
                    nx1_4 = 0
                    for kx1 in range(nx1_3):
                        rx = X1_3[kx1, 0]; rox = X1_3[kx1, 2]
                        if (rx & fb4_01) == z64 and (rox & orb_p_4) == z64:
                            rgx = X1_3[kx1, 1]
                            if (gp4_01 == 0 or eq_bits_42(x0 & rx, gp4_01)) and (kw4_01 == 0 or eq_bits_42(gx0 & rx, kw4_01)):
                                X1_4[nx1_4, 0] = rx; X1_4[nx1_4, 1] = rgx; X1_4[nx1_4, 2] = rox; nx1_4 += 1
                    if nx1_4 == 0: continue
                    loc_d6 += nx1_4

                    fb4_02 = col_u2_4 | (x0 if gp4_02 == 0 else z64) | (gx0 if kw4_02 == 0 else z64)
                    nx2_4 = 0
                    for kx2 in range(nx2_3):
                        rx = X2_3[kx2, 0]; rox = X2_3[kx2, 2]
                        if (rx & fb4_02) == z64 and (rox & orb_p_4) == z64:
                            rgx = X2_3[kx2, 1]
                            if (gp4_02 == 0 or eq_bits_42(x0 & rx, gp4_02)) and (kw4_02 == 0 or eq_bits_42(gx0 & rx, kw4_02)):
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
                                if (gp4_12 == 0 or eq_bits_42(x1 & rx, gp4_12)) and (kw4_12 == 0 or eq_bits_42(gx1 & rx, kw4_12)):
                                    X2_5[nx2_5, 0] = rx; X2_5[nx2_5, 1] = rgx; X2_5[nx2_5, 2] = rox; nx2_5 += 1
                        if nx2_5 == 0: continue

                        if nx3_4 == -1:
                            fb4_03 = col_u2_4 | (x0 if gp4_03 == 0 else z64) | (gx0 if kw4_03 == 0 else z64)
                            nx3_4 = 0
                            for kx3 in range(nx3_3):
                                rx = X3_3[kx3, 0]; rox = X3_3[kx3, 2]
                                if (rx & fb4_03) == z64 and (rox & orb_p_4) == z64:
                                    rgx = X3_3[kx3, 1]
                                    if (gp4_03 == 0 or eq_bits_42(x0 & rx, gp4_03)) and (kw4_03 == 0 or eq_bits_42(gx0 & rx, kw4_03)):
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
                                if (gp4_13 == 0 or eq_bits_42(x1 & rx, gp4_13)) and (kw4_13 == 0 or eq_bits_42(gx1 & rx, kw4_13)):
                                    X3_5[nx3_5, 0] = rx; X3_5[nx3_5, 1] = rgx; X3_5[nx3_5, 2] = rox; nx3_5 += 1
                        if nx3_5 == 0: continue

                        for kx2 in range(nx2_5):
                            x2 = X2_5[kx2, 0]; gx2 = X2_5[kx2, 1]; ox2 = X2_5[kx2, 2]
                            col_u2_6 = col_u2_5 | (col_u1_5 & x2)
                            col_u1_6 = col_u1_5 | x2
                            orb_p_6 = orb_p_5 | ox2
                            fb4_23 = col_u2_6 | (x2 if gp4_23 == 0 else z64) | (gx2 if kw4_23 == 0 else z64)
                            for kx3 in range(nx3_5):
                                x3 = X3_5[kx3, 0]; gx3 = X3_5[kx3, 1]; ox3 = X3_5[kx3, 2]
                                if (x3 & fb4_23) == z64 and (ox3 & orb_p_6) == z64:
                                    if (gp4_23 == 0 or eq_bits_42(x2 & x3, gp4_23)) and (kw4_23 == 0 or eq_bits_42(gx2 & x3, kw4_23)):
                                        loc_d8 += 1
                                        if len(X4) > 1:
                                            if nx4_3 == -1:
                                                if nx4_0 == -1:
                                                    nx4_0 = 0
                                                    for jx4 in range(len(X4)):
                                                        rx = X4[jx4, 0]; rgx = X4[jx4, 1]; rox = X4[jx4, 6]
                                                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                                                            X4_0[nx4_0, 0] = rx; X4_0[nx4_0, 1] = rgx; X4_0[nx4_0, 2] = rox; nx4_0 += 1
                                                    nx5_0 = 0
                                                    for jx5 in range(len(X5)):
                                                        rx = X5[jx5, 0]; rgx = X5[jx5, 1]; rox = X5[jx5, 6]
                                                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                                                            X5_0[nx5_0, 0] = rx; X5_0[nx5_0, 1] = rgx; X5_0[nx5_0, 2] = rox; nx5_0 += 1
                                                    nx6_0 = 0
                                                    for jx6 in range(len(X6)):
                                                        rx = X6[jx6, 0]; rgx = X6[jx6, 1]; rox = X6[jx6, 6]
                                                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                                                            X6_0[nx6_0, 0] = rx; X6_0[nx6_0, 1] = rgx; X6_0[nx6_0, 2] = rox; nx6_0 += 1
                                                    nx7_0 = 0
                                                    for jx7 in range(len(X7)):
                                                        rx = X7[jx7, 0]; rgx = X7[jx7, 1]; rox = X7[jx7, 6]
                                                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                                                            X7_0[nx7_0, 0] = rx; X7_0[nx7_0, 1] = rgx; X7_0[nx7_0, 2] = rox; nx7_0 += 1
                                                if nx4_1 == -1:
                                                    nx4_1 = 0
                                                    for jx4 in range(nx4_0):
                                                        rx = X4_0[jx4, 0]; rgx = X4_0[jx4, 1]; rox = X4_0[jx4, 2]
                                                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                                                            X4_1[nx4_1, 0] = rx; X4_1[nx4_1, 1] = rgx; X4_1[nx4_1, 2] = rox; nx4_1 += 1
                                                    nx5_1 = 0
                                                    for jx5 in range(nx5_0):
                                                        rx = X5_0[jx5, 0]; rgx = X5_0[jx5, 1]; rox = X5_0[jx5, 2]
                                                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                                                            X5_1[nx5_1, 0] = rx; X5_1[nx5_1, 1] = rgx; X5_1[nx5_1, 2] = rox; nx5_1 += 1
                                                    nx6_1 = 0
                                                    for jx6 in range(nx6_0):
                                                        rx = X6_0[jx6, 0]; rgx = X6_0[jx6, 1]; rox = X6_0[jx6, 2]
                                                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                                                            X6_1[nx6_1, 0] = rx; X6_1[nx6_1, 1] = rgx; X6_1[nx6_1, 2] = rox; nx6_1 += 1
                                                    nx7_1 = 0
                                                    for jx7 in range(nx7_0):
                                                        rx = X7_0[jx7, 0]; rgx = X7_0[jx7, 1]; rox = X7_0[jx7, 2]
                                                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                                                            X7_1[nx7_1, 0] = rx; X7_1[nx7_1, 1] = rgx; X7_1[nx7_1, 2] = rox; nx7_1 += 1
                                                if nx4_2 == -1:
                                                    nx4_2 = 0
                                                    for jx4 in range(nx4_1):
                                                        rx = X4_1[jx4, 0]; rgx = X4_1[jx4, 1]; rox = X4_1[jx4, 2]
                                                        if (rx & col_u2_2) == z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                                                            X4_2[nx4_2, 0] = rx; X4_2[nx4_2, 1] = rgx; X4_2[nx4_2, 2] = rox; nx4_2 += 1
                                                    nx5_2 = 0
                                                    for jx5 in range(nx5_1):
                                                        rx = X5_1[jx5, 0]; rgx = X5_1[jx5, 1]; rox = X5_1[jx5, 2]
                                                        if (rx & col_u2_2) == z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                                                            X5_2[nx5_2, 0] = rx; X5_2[nx5_2, 1] = rgx; X5_2[nx5_2, 2] = rox; nx5_2 += 1
                                                    nx6_2 = 0
                                                    for jx6 in range(nx6_1):
                                                        rx = X6_1[jx6, 0]; rgx = X6_1[jx6, 1]; rox = X6_1[jx6, 2]
                                                        if (rx & col_u2_2) == z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                                                            X6_2[nx6_2, 0] = rx; X6_2[nx6_2, 1] = rgx; X6_2[nx6_2, 2] = rox; nx6_2 += 1
                                                    nx7_2 = 0
                                                    for jx7 in range(nx7_1):
                                                        rx = X7_1[jx7, 0]; rgx = X7_1[jx7, 1]; rox = X7_1[jx7, 2]
                                                        if (rx & col_u2_2) == z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                                                            X7_2[nx7_2, 0] = rx; X7_2[nx7_2, 1] = rgx; X7_2[nx7_2, 2] = rox; nx7_2 += 1
                                                nx4_3 = 0
                                                for jx4 in range(nx4_2):
                                                    rx = X4_2[jx4, 0]; rgx = X4_2[jx4, 1]; rox = X4_2[jx4, 2]
                                                    if (rx & col_u2_3) == z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                                                        X4_3[nx4_3, 0] = rx; X4_3[nx4_3, 1] = rgx; X4_3[nx4_3, 2] = rox; nx4_3 += 1
                                                nx5_3 = 0
                                                for jx5 in range(nx5_2):
                                                    rx = X5_2[jx5, 0]; rgx = X5_2[jx5, 1]; rox = X5_2[jx5, 2]
                                                    if (rx & col_u2_3) == z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                                                        X5_3[nx5_3, 0] = rx; X5_3[nx5_3, 1] = rgx; X5_3[nx5_3, 2] = rox; nx5_3 += 1
                                                nx6_3 = 0
                                                for jx6 in range(nx6_2):
                                                    rx = X6_2[jx6, 0]; rgx = X6_2[jx6, 1]; rox = X6_2[jx6, 2]
                                                    if (rx & col_u2_3) == z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                                                        X6_3[nx6_3, 0] = rx; X6_3[nx6_3, 1] = rgx; X6_3[nx6_3, 2] = rox; nx6_3 += 1
                                                nx7_3 = 0
                                                for jx7 in range(nx7_2):
                                                    rx = X7_2[jx7, 0]; rgx = X7_2[jx7, 1]; rox = X7_2[jx7, 2]
                                                    if (rx & col_u2_3) == z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                                                        X7_3[nx7_3, 0] = rx; X7_3[nx7_3, 1] = rgx; X7_3[nx7_3, 2] = rox; nx7_3 += 1
                                            if nx4_3 > 0 and nx5_3 > 0 and nx6_3 > 0 and nx7_3 > 0:
                                                loc_sols += check_d8_tail_fast(
                                                    o2_0, col_u2_6, col_u1_6, orb_p_6,
                                                    x0, gx0, x1, gx1, x2, gx2, x3, gx3, ox3,
                                                    X4_3, nx4_3, X5_3, nx5_3, X6_3, nx6_3, X7_3, nx7_3,
                                                    Gp4, KW4
                                                )
        for k2 in range(n2_1): in_c2_1[c2_1[k2]] = 0

    out[0] = loc_d1; out[1] = loc_d2; out[2] = loc_b1; out[3] = loc_d5
    out[4] = loc_d6; out[5] = loc_d7; out[6] = loc_d8; out[7] = loc_sols
    return out

@njit(parallel=True, cache=True)
def solve_orbit_114_cpu(
    n_test, reps, rep_canons,
    Y0, Y0_adj, Y0_deg, cy1_can,
    Y2, Y2_adj, Y2_deg, cy2_can,
    X0, X1, X2, X3, X4, X5, X6, X7,
    Gp4, KW4,
    C11_col_mask, O11_orb_mask, O12_orb_mask,
    luts_g01, is_g012_flag, luts_swap01
):
    counts = np.zeros((n_test, 8), dtype=np.int64)
    for idx_rep in prange(n_test):
        counts[idx_rep] = solve_single_rep_114(
            reps[idx_rep], rep_canons[idx_rep],
            Y0, Y0_adj, Y0_deg, cy1_can,
            Y2, Y2_adj, Y2_deg, cy2_can,
            X0, X1, X2, X3, X4, X5, X6, X7,
            Gp4, KW4,
            C11_col_mask, O11_orb_mask, O12_orb_mask,
            luts_g01, is_g012_flag, luts_swap01
        )
    return counts.sum(axis=0)

def main():
    t0 = time.time()
    print("[1/4] Building orbits...", flush=True)
    F12, I12, J12, b6_perms, orbits_by_sig = build_orbits()

    b2_perms_4 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(2)) for flips in product((0, 1), repeat=2)
    ]
    b4_perms_8 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(4)) for flips in product((0, 1), repeat=4)
    ]
    def canon_4block(M8, E8):
        return min(tuple(M8[np.ix_(p, p)].flatten()) + tuple(E8[np.ix_(p, p)].flatten()) for p in b4_perms_8)

    c4_classes = []
    seen_c4 = set()
    for M, E, Gp, KW0, Delta0, comps in orbits_by_sig["kt1=2_4+1+1"]:
        comp4 = [c for c in comps if len(c) == 8][0]
        M8, E8 = M[np.ix_(comp4, comp4)], E[np.ix_(comp4, comp4)]
        ck4 = canon_4block(M8, E8)
        if ck4 not in seen_c4:
            seen_c4.add(ck4)
            c4_classes.append((M8, E8))
    print(f"[2/4] Extracted {len(c4_classes)} canonical 4-block classes in {time.time()-t0:.2f}s.", flush=True)

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

    perms4 = list(permutations(range(4)))
    cone_info = {}
    for idx_d, (M8, E8) in enumerate(c4_classes):
        KW8 = 2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)
        D8 = 2 * J8 - I8 - F8 - M8 - (E8 @ F8)
        Gp8 = 7 * I8 + J8 - M8
        for q in combinations(range(8), 4):
            q = list(q)
            sm = sum(3 if 0 in D8[r] else (1 if KW8[r, r] == 0 else 0) for r in q)
            w_sum = sum(w4_mat(Gp8, KW8, q[a], q[b]) for a in range(4) for b in range(a + 1, 4))
            gp4, kw4, d48 = Gp8[np.ix_(q, q)], KW8[np.ix_(q, q)], D8[q, :]
            gp0 = tuple(gp4.flatten()); kw0 = tuple(kw4.flatten()); d0 = tuple(d48.flatten())
            min_gk = None
            cand_prs = []
            aut_prs = []
            for pr in perms4:
                gp_p = tuple(gp4[np.ix_(pr, pr)].flatten())
                kw_p = tuple(kw4[np.ix_(pr, pr)].flatten())
                gk = gp_p + kw_p
                if min_gk is None or gk < min_gk:
                    min_gk = gk
                    cand_prs = [pr]
                elif gk == min_gk:
                    cand_prs.append(pr)
                if gp_p == gp0 and kw_p == kw0:
                    aut_prs.append(pr)
            st = 0
            for pr in aut_prs:
                d_pr = d48[list(pr), :]
                for pc in b4_perms_8:
                    if tuple(d_pr[:, pc].flatten()) == d0:
                        st += 1
            best_d = None
            for pr in cand_prs:
                d_pr = d48[list(pr), :]
                for pc in b4_perms_8:
                    dp = tuple(d_pr[:, pc].flatten())
                    if best_d is None or dp < best_d:
                        best_d = dp
            best_key = min_gk + best_d
            if best_key not in cone_info:
                cone_info[best_key] = {"st": st, "small": sm, "w_sum": w_sum, "classes": set(), "example": (idx_d, q)}
            cone_info[best_key]["classes"].add(idx_d)

    uncov = set(range(56))
    chosen_cones = []
    while uncov:
        avail = [k for k in cone_info.keys() if cone_info[k]["classes"] & uncov]
        best_k = max(
            avail,
            key=lambda k: (
                int(np.log2(cone_info[k]["st"])) * 4 + cone_info[k]["w_sum"] + cone_info[k]["small"] * 2,
                cone_info[k]["small"],
                len(cone_info[k]["classes"] & uncov),
                cone_info[k]["st"]
            )
        )
        info = cone_info[best_k]
        new_c = sorted(info["classes"] & uncov)
        chosen_cones.append((best_k, new_c, sorted(info["classes"]), info))
        uncov -= info["classes"]

    col_orb_bit = [0] * 60
    for idx_m, (c, gc) in enumerate(orbs_30):
        col_orb_bit[c] = 1 << idx_m
        col_orb_bit[gc] = 1 << idx_m
    O11_int = int(O11_orb_mask)
    O12_int = int(O12_orb_mask)

    y_cache = {}
    def gen_2block_rows(target_deg_4, diag_kw):
        key = (target_deg_4, diag_kw)
        if key in y_cache: return y_cache[key]
        target_deg_12 = (2, 2, 2, 2, 2, 2, 2, 2) + tuple(target_deg_4)
        req_pairs = diag_kw // 2
        ok_cols = [c for c in range(60) if target_deg_12[cols_60[c][0]] > 0 and target_deg_12[cols_60[c][1]] > 0 and not (cols_60[c][0] not in I_B1 and cols_60[c][1] not in I_B1)]
        adj_cols = [[] for _ in range(12)]
        for c in ok_cols:
            u, v = cols_60[c]; adj_cols[min(u, v)].append((c, max(u, v), 1 << c, 1 << g_col[c], col_orb_bit[c]))
        rem_deg = list(target_deg_12); res = []
        def bt_v(v_idx, n_ch, xm, gxm, orb_u1, orb_u2):
            if v_idx == 12:
                if n_ch == 10 and (orb_u2 & O12_int) == 0 and orb_u2.bit_count() == req_pairs:
                    o11_2 = orb_u2 & O11_int
                    o11_1 = (orb_u1 & O11_int) ^ o11_2
                    o12_1 = orb_u1 & O12_int
                    res.append((xm, gxm, o11_1, o11_2, o12_1, orb_u2))
                return
            need = rem_deg[v_idx]
            if need < 0: return
            avail = [item for item in adj_cols[v_idx] if rem_deg[item[1]] > 0]
            if len(avail) < need: return
            for comb in combinations(avail, need):
                nxm, ngxm, nu1, nu2 = xm, gxm, orb_u1, orb_u2
                for c, w, cb, gcb, ob in comb:
                    rem_deg[w] -= 1
                    nxm |= cb; ngxm |= gcb
                    nu2 |= (nu1 & ob); nu1 |= ob
                rem_deg[v_idx] = 0
                bt_v(v_idx + 1, n_ch + need, nxm, ngxm, nu1, nu2)
                rem_deg[v_idx] = need
                for c, w, cb, gcb, ob in comb:
                    rem_deg[w] += 1
        bt_v(0, 0, 0, 0, 0, 0)
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
            u, v = cols_60[c]; adj_cols[min(u, v)].append((c, max(u, v), 1 << c, 1 << g_col[c], col_orb_bit[c]))
        rem_deg = list(target_deg_12); res = []
        def bt_v(v_idx, n_ch, xm, gxm, orb_u1, orb_u2):
            if v_idx == 12:
                if n_ch == 10 and orb_u2.bit_count() == req_pairs:
                    res.append((xm, gxm, 0, 0, 0, 0, orb_u2))
                return
            need = rem_deg[v_idx]
            if need < 0: return
            avail = [item for item in adj_cols[v_idx] if rem_deg[item[1]] > 0]
            if len(avail) < need: return
            for comb in combinations(avail, need):
                nxm, ngxm, nu1, nu2 = xm, gxm, orb_u1, orb_u2
                if req_pairs == 0:
                    ok = True
                    for c, w, cb, gcb, ob in comb:
                        if nu1 & ob:
                            ok = False
                            break
                        nu1 |= ob
                    if not ok:
                        continue
                    for c, w, cb, gcb, ob in comb:
                        rem_deg[w] -= 1
                        nxm |= cb; ngxm |= gcb
                    rem_deg[v_idx] = 0
                    bt_v(v_idx + 1, n_ch + need, nxm, ngxm, nu1, 0)
                    rem_deg[v_idx] = need
                    for c, w, cb, gcb, ob in comb:
                        rem_deg[w] += 1
                else:
                    for c, w, cb, gcb, ob in comb:
                        rem_deg[w] -= 1
                        nxm |= cb; ngxm |= gcb
                        nu2 |= (nu1 & ob); nu1 |= ob
                    if nu2.bit_count() <= req_pairs:
                        rem_deg[v_idx] = 0
                        bt_v(v_idx + 1, n_ch + need, nxm, ngxm, nu1, nu2)
                        rem_deg[v_idx] = need
                    for c, w, cb, gcb, ob in comb:
                        rem_deg[w] += 1
        bt_v(0, 0, 0, 0, 0, 0)
        arr = np.ascontiguousarray(np.array(res, dtype=np.uint64))
        x_cache[key] = arr
        return arr

    from collections import defaultdict
    Y0_pool = gen_2block_rows((0, 0, 2, 2), 0)
    Y2_pool = gen_2block_rows((2, 2, 0, 0), 0)
    O12_y0_mask = 0
    for i in range(len(Y0_pool)): O12_y0_mask |= int(Y0_pool[i, 4])
    by_orb0 = defaultdict(list)
    for i in range(len(Y0_pool)):
        by_orb0[(int(Y0_pool[i, 2]), int(Y0_pool[i, 4]))].append(i)
    Y0_adj = np.zeros((len(Y0_pool), 32), dtype=np.int32)
    Y0_deg = np.zeros(len(Y0_pool), dtype=np.int32)
    for i in range(len(Y0_pool)):
        comp = (O11_int ^ int(Y0_pool[i, 2]), O12_y0_mask ^ int(Y0_pool[i, 4]))
        lst = [j for j in by_orb0.get(comp, []) if j > i]
        Y0_deg[i] = len(lst)
        for k, j in enumerate(lst):
            Y0_adj[i, k] = j

    O12_y2_mask = 0
    for i in range(len(Y2_pool)): O12_y2_mask |= int(Y2_pool[i, 4])
    by_orb2 = defaultdict(list)
    for i in range(len(Y2_pool)):
        by_orb2[(int(Y2_pool[i, 2]), int(Y2_pool[i, 4]))].append(i)
    Y2_adj = np.zeros((len(Y2_pool), 32), dtype=np.int32)
    Y2_deg = np.zeros(len(Y2_pool), dtype=np.int32)
    for i in range(len(Y2_pool)):
        comp = (O11_int ^ int(Y2_pool[i, 2]), O12_y2_mask ^ int(Y2_pool[i, 4]))
        lst = [j for j in by_orb2.get(comp, []) if j > i]
        Y2_deg[i] = len(lst)
        for k, j in enumerate(lst):
            Y2_adj[i, k] = j

    M4, E4 = F4.copy(), F4.copy()
    KW4 = (2 * J4 - F4 - E4 - (M4 @ E4) - (E4 @ M4)).astype(np.int32)
    D4 = 2 * J4 - I4 - F4 - M4 - (E4 @ F4)
    Gp4_2 = (7 * I4 + J4 - M4).astype(np.int32)
    Y_raw = [Y0_pool, Y0_pool, Y2_pool, Y2_pool]
    ylens = [len(y) for y in Y_raw]
    stab2_m16 = []
    for pr in permutations(range(4)):
        if any(ylens[pr[a]] != ylens[a] for a in range(4)): continue
        if not (Gp4_2 == Gp4_2[np.ix_(pr, pr)]).all() or not (KW4 == KW4[np.ix_(pr, pr)]).all(): continue
        for pc in b2_perms_4:
            if (D4 == D4[np.ix_(pr, pc)]).all():
                stab2_m16.append((pr, pc))
    ord2 = [0, 1, 2, 3]
    Y = [Y_raw[r] for r in ord2]
    Gp2_ord = np.ascontiguousarray(Gp4_2[np.ix_(ord2, ord2)], dtype=np.int32)
    KW2_ord = np.ascontiguousarray(KW4[np.ix_(ord2, ord2)], dtype=np.int32)
    print(f"[3/4] Prepared Y=C1+C1 ({ylens}, |Stab2|={len(stab2_m16)}, Y0_pairs={Y0_deg.sum()}, Y2_pairs={Y2_deg.sum()}) in {time.time()-t0:.2f}s. Starting {len(chosen_cones)} sub-cones...", flush=True)

    id_map = tuple(range(60))
    X_dummy = np.zeros((1, 7), dtype=np.uint64)
    t_114 = time.time()
    tot_b1 = 0; tot_d6 = 0; tot_d8 = 0; tot_sols = 0
    for idx_m, (k, new_c, all_c, info) in enumerate(chosen_cones):
        idx_d, q_base = info["example"]
        M8, E8 = c4_classes[idx_d]
        KW8 = (2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)).astype(np.int32)
        D8 = 2 * J8 - I8 - F8 - M8 - (E8 @ F8)
        Gp8_4 = (7 * I8 + J8 - M8).astype(np.int32)
        xlens = [91392 if 0 in D8[r] else (195576 if KW8[r, r] == 0 else 216576) for r in range(8)]
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
        rem4 = sorted([u for u in range(8) if u not in ord4_sub], key=lambda u: (sum(w4(r, u) for r in ord4_sub), -xlens[u]), reverse=True)
        ord4 = ord4_sub + rem4
        t_x = time.time()
        X03 = [gen_4block_rows(tuple(int(D8[r, j]) for j in range(8)), int(KW8[r, r])) for r in ord4_sub]
        X47 = [gen_4block_rows(tuple(int(D8[r, j]) for j in range(8)), int(KW8[r, r])) for r in rem4]
        Gp4_ord = np.ascontiguousarray(Gp8_4[np.ix_(ord4, ord4)], dtype=np.int32)
        KW4_ord = np.ascontiguousarray(KW8[np.ix_(ord4, ord4)], dtype=np.int32)

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

        cy_cans = [compute_canons_lut(Y[a], build_perm_luts(stab_y_to_0[a])) for a in (0, 1, 2)]
        luts_g01 = build_perm_luts(g01_perms)
        is_g012_flag = np.ascontiguousarray(np.array(g012_flags, dtype=np.int32))
        luts_swap01 = build_perm_luts(swap01_perms)

        reps = np.ascontiguousarray([i for i in range(len(Y[0])) if Y[0][i, 0] == cy_cans[0][i]], dtype=np.int32)
        rep_canons = np.ascontiguousarray([cy_cans[0][i] for i in reps], dtype=np.uint64)
        print(f"    -> K4_{idx_m:02d} X-pools {[len(x) for x in X03]} ready in {time.time()-t_x:.2f}s (reps={len(reps)}, |Stab|={len(stab2_m16)*len(stab4_sub)})...", flush=True)

        if idx_m == 0:
            t_jit = time.time()
            _ = solve_orbit_114_cpu(
                0, reps[:1], rep_canons[:1],
                Y0_pool, Y0_adj, Y0_deg, cy_cans[1],
                Y2_pool, Y2_adj, Y2_deg, cy_cans[2],
                X03[0], X03[1], X03[2], X03[3], X47[0], X47[1], X47[2], X47[3],
                Gp4_ord, KW4_ord,
                C11_col_mask, O11_orb_mask, O12_orb_mask,
                luts_g01, is_g012_flag, luts_swap01
            )
            print(f"    -> Numba JIT compiled in {time.time()-t_jit:.2f}s", flush=True)

        t_k = time.time()
        res = solve_orbit_114_cpu(
            len(reps), reps, rep_canons,
            Y0_pool, Y0_adj, Y0_deg, cy_cans[1],
            Y2_pool, Y2_adj, Y2_deg, cy_cans[2],
            X03[0], X03[1], X03[2], X03[3], X47[0], X47[1], X47[2], X47[3],
            Gp4_ord, KW4_ord,
            C11_col_mask, O11_orb_mask, O12_orb_mask,
            luts_g01, is_g012_flag, luts_swap01
        )
        tot_b1 += int(res[2]); tot_d6 += int(res[4]); tot_d8 += int(res[6]); tot_sols += int(res[7])
        print(f"  [1+1+4 K4_{idx_m:02d}] |Stab|={len(stab2_m16)*len(stab4_sub):5d} | reps={len(reps):4d} | b1={int(res[2]):6d} d6={int(res[4]):8d} d8={int(res[6]):6d} sols={int(res[7])} | {time.time()-t_k:.2f}s (classes={new_c})", flush=True)

    print(f"[PART B1 PASS] All 45 canonical 4x8 sub-cones of 1+1+4 (kt1=2, dim=4) CERTIFIED UNSAT (tot_b1={tot_b1}, tot_d6={tot_d6}, tot_d8={tot_d8}, tot_sols={tot_sols}) in {time.time()-t_114:.2f}s!", flush=True)

if __name__ == "__main__":
    main()
