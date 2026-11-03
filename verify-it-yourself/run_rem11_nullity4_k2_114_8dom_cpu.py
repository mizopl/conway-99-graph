import os
import sys
import time
import json
import numpy as np
from numba import njit, prange
from itertools import combinations, permutations, product
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_all_10_nullity3_k0_33_cpu import build_orbits, build_perm_luts, compute_canons_lut, popcnt64, apply_lut


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


@njit
def solve_8dom_after_y(
    col_u1_3, col_u2_3,
    X0_3, nx0_3, X1_3, nx1_3, X2_3, nx2_3, X3_3, nx3_3,
    X4_3, nx4_3, X5_3, nx5_3, X6_3, nx6_3, X7_3, nx7_3,
    Gp8, KW8, ALL60
):
    z64 = np.uint64(0)
    tot = nx0_3 + nx1_3 + nx2_3 + nx3_3 + nx4_3 + nx5_3 + nx6_3 + nx7_3
    cands = np.empty((tot, 3), dtype=np.uint64)
    arena = np.empty((8, tot), dtype=np.int32)
    dom_v = np.empty((8, 8), dtype=np.int32)
    dom_start = np.empty((8, 8), dtype=np.int32)
    dom_cnt = np.empty((8, 8), dtype=np.int32)

    ptr = 0
    av1 = z64
    av2 = z64

    for d_idx in range(8):
        ns_st = ptr
        d_or = z64
        if d_idx == 0:
            src, n_s = X0_3, nx0_3
        elif d_idx == 1:
            src, n_s = X1_3, nx1_3
        elif d_idx == 2:
            src, n_s = X2_3, nx2_3
        elif d_idx == 3:
            src, n_s = X3_3, nx3_3
        elif d_idx == 4:
            src, n_s = X4_3, nx4_3
        elif d_idx == 5:
            src, n_s = X5_3, nx5_3
        elif d_idx == 6:
            src, n_s = X6_3, nx6_3
        else:
            src, n_s = X7_3, nx7_3

        for k in range(n_s):
            rx = src[k, 0]
            cands[ptr, 0] = rx
            cands[ptr, 1] = src[k, 1]
            cands[ptr, 2] = src[k, 2]
            arena[0, ptr] = ptr
            ptr += 1
            d_or |= rx

        av2 |= av1 & d_or
        av1 |= d_or
        dom_v[0, d_idx] = d_idx
        dom_start[0, d_idx] = ns_st
        dom_cnt[0, d_idx] = n_s

    if ((col_u2_3 | (col_u1_3 & av1) | av2) & ALL60) != ALL60 or ((col_u1_3 | av1) & ALL60) != ALL60:
        return 0, 0

    bj = 0
    bc = dom_cnt[0, 0]
    for j in range(1, 8):
        if dom_cnt[0, j] < bc:
            bc = dom_cnt[0, j]
            bj = j
    if bj != 0:
        tv, ts, tc = dom_v[0, 0], dom_start[0, 0], dom_cnt[0, 0]
        dom_v[0, 0], dom_start[0, 0], dom_cnt[0, 0] = dom_v[0, bj], dom_start[0, bj], dom_cnt[0, bj]
        dom_v[0, bj], dom_start[0, bj], dom_cnt[0, bj] = tv, ts, tc

    cur_choice = np.empty(8, dtype=np.int32)
    u1_stack = np.empty(8, dtype=np.uint64)
    u2_stack = np.empty(8, dtype=np.uint64)
    pu_stack = np.empty(8, dtype=np.uint64)

    depth = 0
    cur_choice[0] = 0
    u1_stack[0] = col_u1_3
    u2_stack[0] = col_u2_3
    pu_stack[0] = z64
    nodes = 1
    sols = 0

    while depth >= 0:
        n_doms = 8 - depth
        c_idx = cur_choice[depth]
        if c_idx >= dom_cnt[depth, 0]:
            depth -= 1
            continue
        cur_choice[depth] = c_idx + 1
        cand_k = arena[depth, dom_start[depth, 0] + c_idx]
        cxm = cands[cand_k, 0]
        cpm = cands[cand_k, 2]
        nu2 = u2_stack[depth] | (u1_stack[depth] & cxm)
        nu1 = u1_stack[depth] | cxm
        npu = pu_stack[depth] | cpm

        if n_doms == 1:
            nodes += 1
            sols += 1
            continue

        v_cur = dom_v[depth, 0]
        nxt_d = depth + 1
        n_rest = n_doms - 1
        n_ptr = 0
        av1 = z64
        av2 = z64
        sub_ok = True

        for j in range(1, n_doms):
            v_nxt = dom_v[depth, j]
            gp_req = Gp8[v_cur, v_nxt]
            kw_req = KW8[v_cur, v_nxt]
            st = dom_start[depth, j]
            en = st + dom_cnt[depth, j]
            ns_st = n_ptr
            d_or = z64
            if gp_req == 0:
                forb_x = nu2 | cxm
                for p_i in range(st, en):
                    rk = arena[depth, p_i]
                    rxm = cands[rk, 0]
                    if (rxm & forb_x) != z64 or (cands[rk, 2] & npu) != z64:
                        continue
                    if eq_bits_42(cxm & cands[rk, 1], kw_req):
                        arena[nxt_d, n_ptr] = rk
                        n_ptr += 1
                        d_or |= rxm
            else:
                for p_i in range(st, en):
                    rk = arena[depth, p_i]
                    rxm = cands[rk, 0]
                    if (rxm & nu2) != z64 or (cands[rk, 2] & npu) != z64:
                        continue
                    if eq_bits_42(cxm & rxm, gp_req) and eq_bits_42(cxm & cands[rk, 1], kw_req):
                        arena[nxt_d, n_ptr] = rk
                        n_ptr += 1
                        d_or |= rxm
            ns_c = n_ptr - ns_st
            if ns_c == 0:
                sub_ok = False
                break
            av2 |= av1 & d_or
            av1 |= d_or
            dom_v[nxt_d, j - 1] = v_nxt
            dom_start[nxt_d, j - 1] = ns_st
            dom_cnt[nxt_d, j - 1] = ns_c

        if sub_ok:
            if ((nu2 | (nu1 & av1) | av2) & ALL60) != ALL60 or ((nu1 | av1) & ALL60) != ALL60:
                continue
            bj = 0
            bc = dom_cnt[nxt_d, 0]
            for j in range(1, n_rest):
                if dom_cnt[nxt_d, j] < bc:
                    bc = dom_cnt[nxt_d, j]
                    bj = j
            if bj != 0:
                tv, ts, tc = dom_v[nxt_d, 0], dom_start[nxt_d, 0], dom_cnt[nxt_d, 0]
                dom_v[nxt_d, 0], dom_start[nxt_d, 0], dom_cnt[nxt_d, 0] = dom_v[nxt_d, bj], dom_start[nxt_d, bj], dom_cnt[nxt_d, bj]
                dom_v[nxt_d, bj], dom_start[nxt_d, bj], dom_cnt[nxt_d, bj] = tv, ts, tc
            u1_stack[nxt_d] = nu1
            u2_stack[nxt_d] = nu2
            pu_stack[nxt_d] = npu
            cur_choice[nxt_d] = 0
            nodes += 1
            depth = nxt_d

    return nodes, sols


@njit
def solve_rep_114_8dom(
    i0, min_can,
    Y0, Y0_adj, Y0_deg, cy1_can,
    Y2, Y2_adj, Y2_deg, cy2_can,
    X0, X1, X2, X3, X4, X5, X6, X7,
    Gp8, KW8, ALL60,
    luts_g01, is_g012_flag, luts_swap01
):
    out = np.zeros(4, dtype=np.int64)
    z64 = np.uint64(0)
    n_g01 = len(luts_g01)
    n_swap01 = len(luts_swap01)
    y0 = Y0[i0, 0]; gy0 = Y0[i0, 1]

    stab0_idx = np.empty(n_g01 + 1, dtype=np.int32); n_stab0 = 0
    for p_idx in range(n_g01):
        if apply_lut(y0, luts_g01[p_idx]) == y0:
            stab0_idx[n_stab0] = p_idx; n_stab0 += 1

    c1_0 = np.empty(32, dtype=np.int32); n1_0 = 0
    for k1 in range(Y0_deg[i0]):
        j1 = Y0_adj[i0, k1]
        if j1 <= i0: continue
        if cy1_can[j1] >= min_can:
            ry = Y0[j1, 0]
            is_rep1 = True
            for s_i in range(n_stab0):
                if apply_lut(ry, luts_g01[stab0_idx[s_i]]) < ry:
                    is_rep1 = False; break
            if is_rep1 and n_swap01 > 0:
                for p_idx in range(n_swap01):
                    if apply_lut(ry, luts_swap01[p_idx]) == y0:
                        if apply_lut(y0, luts_swap01[p_idx]) < ry:
                            is_rep1 = False; break
            if is_rep1:
                c1_0[n1_0] = j1; n1_0 += 1
    if n1_0 == 0: return out

    c2_0 = np.empty(len(Y2), dtype=np.int32); n2_0 = 0
    for j2 in range(len(Y2)):
        if cy2_can[j2] >= min_can:
            ry = Y2[j2, 0]
            if eq_bits_42(y0 & ry, 1) and eq_bits_42(gy0 & ry, 2):
                c2_0[n2_0] = j2; n2_0 += 1
    if n2_0 == 0: return out

    X0_0 = np.empty((65536, 3), dtype=np.uint64); nx0_0 = -1
    X1_0 = np.empty((65536, 3), dtype=np.uint64); nx1_0 = 0
    X2_0 = np.empty((65536, 3), dtype=np.uint64); nx2_0 = 0
    X3_0 = np.empty((65536, 3), dtype=np.uint64); nx3_0 = 0
    X4_0 = np.empty((65536, 3), dtype=np.uint64); nx4_0 = 0
    X5_0 = np.empty((65536, 3), dtype=np.uint64); nx5_0 = 0
    X6_0 = np.empty((65536, 3), dtype=np.uint64); nx6_0 = 0
    X7_0 = np.empty((65536, 3), dtype=np.uint64); nx7_0 = 0

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

    c2_1 = np.empty(n2_0 + 1, dtype=np.int32)
    in_c2_1 = np.zeros(len(Y2), dtype=np.uint8)
    stab01_idx = np.empty(n_g01 + 1, dtype=np.int32)
    loc_b1 = 0; loc_nodes = 0; loc_sols = 0

    for idx1 in range(n1_0):
        i1 = c1_0[idx1]; y1 = Y0[i1, 0]; gy1 = Y0[i1, 1]
        col_u1_1 = y0 | y1
        n_stab01 = 0
        for s_i in range(n_stab0):
            p_idx = stab0_idx[s_i]
            if is_g012_flag[p_idx] == 1 and apply_lut(y1, luts_g01[p_idx]) == y1:
                stab01_idx[n_stab01] = p_idx; n_stab01 += 1
        n2_1 = 0
        for k2 in range(n2_0):
            i2 = c2_0[k2]; ry = Y2[i2, 0]
            if eq_bits_42(y1 & ry, 1) and eq_bits_42(gy1 & ry, 2):
                in_c2_1[i2] = 1; c2_1[n2_1] = i2; n2_1 += 1
        if n2_1 == 0: continue
        nx0_1 = -1
        for idx2 in range(n2_1):
            if nx0_1 == 0: break
            i2 = c2_1[idx2]; y2 = Y2[i2, 0]; gy2 = Y2[i2, 1]
            if n_stab01 > 0:
                is_rep2 = True
                for s_i in range(n_stab01):
                    if apply_lut(y2, luts_g01[stab01_idx[s_i]]) < y2:
                        is_rep2 = False; break
                if not is_rep2: continue
            nx0_2 = -1
            col_u2_2 = col_u1_1 & y2; col_u1_2 = col_u1_1 | y2
            for k3 in range(Y2_deg[i2]):
                i3 = Y2_adj[i2, k3]
                if in_c2_1[i3] == 0: continue
                ry3 = Y2[i3, 0]; rgy3 = Y2[i3, 1]
                if n_stab01 > 0:
                    is_rep3 = True
                    for s_i in range(n_stab01):
                        p_lut = luts_g01[stab01_idx[s_i]]
                        py3 = apply_lut(ry3, p_lut)
                        if py3 < y2: is_rep3 = False; break
                        py2 = apply_lut(y2, p_lut)
                        if py2 == y2 and py3 < ry3: is_rep3 = False; break
                        if py3 == y2 and py2 < ry3: is_rep3 = False; break
                    if not is_rep3: continue
                loc_b1 += 1
                if nx0_0 == -1:
                    nx0_0 = 0
                    for jx in range(len(X0)):
                        rx = X0[jx,0]; rgx = X0[jx,1]; rox = X0[jx,6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X0_0[nx0_0,0]=rx; X0_0[nx0_0,1]=rgx; X0_0[nx0_0,2]=rox; nx0_0+=1
                    for jx in range(len(X1)):
                        rx = X1[jx,0]; rgx = X1[jx,1]; rox = X1[jx,6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X1_0[nx1_0,0]=rx; X1_0[nx1_0,1]=rgx; X1_0[nx1_0,2]=rox; nx1_0+=1
                    for jx in range(len(X2)):
                        rx = X2[jx,0]; rgx = X2[jx,1]; rox = X2[jx,6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X2_0[nx2_0,0]=rx; X2_0[nx2_0,1]=rgx; X2_0[nx2_0,2]=rox; nx2_0+=1
                    for jx in range(len(X3)):
                        rx = X3[jx,0]; rgx = X3[jx,1]; rox = X3[jx,6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X3_0[nx3_0,0]=rx; X3_0[nx3_0,1]=rgx; X3_0[nx3_0,2]=rox; nx3_0+=1
                    for jx in range(len(X4)):
                        rx = X4[jx,0]; rgx = X4[jx,1]; rox = X4[jx,6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X4_0[nx4_0,0]=rx; X4_0[nx4_0,1]=rgx; X4_0[nx4_0,2]=rox; nx4_0+=1
                    for jx in range(len(X5)):
                        rx = X5[jx,0]; rgx = X5[jx,1]; rox = X5[jx,6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X5_0[nx5_0,0]=rx; X5_0[nx5_0,1]=rgx; X5_0[nx5_0,2]=rox; nx5_0+=1
                    for jx in range(len(X6)):
                        rx = X6[jx,0]; rgx = X6[jx,1]; rox = X6[jx,6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X6_0[nx6_0,0]=rx; X6_0[nx6_0,1]=rgx; X6_0[nx6_0,2]=rox; nx6_0+=1
                    for jx in range(len(X7)):
                        rx = X7[jx,0]; rgx = X7[jx,1]; rox = X7[jx,6]
                        if eq_bits_42(rx & y0, 1) and eq_bits_42(rgx & y0, 2):
                            X7_0[nx7_0,0]=rx; X7_0[nx7_0,1]=rgx; X7_0[nx7_0,2]=rox; nx7_0+=1
                if nx0_1 == -1:
                    nx0_1=0; nx1_1=0; nx2_1=0; nx3_1=0; nx4_1=0; nx5_1=0; nx6_1=0; nx7_1=0
                    for jx in range(nx0_0):
                        rx=X0_0[jx,0]; rgx=X0_0[jx,1]; rox=X0_0[jx,2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X0_1[nx0_1,0]=rx; X0_1[nx0_1,1]=rgx; X0_1[nx0_1,2]=rox; nx0_1+=1
                    for jx in range(nx1_0):
                        rx=X1_0[jx,0]; rgx=X1_0[jx,1]; rox=X1_0[jx,2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X1_1[nx1_1,0]=rx; X1_1[nx1_1,1]=rgx; X1_1[nx1_1,2]=rox; nx1_1+=1
                    for jx in range(nx2_0):
                        rx=X2_0[jx,0]; rgx=X2_0[jx,1]; rox=X2_0[jx,2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X2_1[nx2_1,0]=rx; X2_1[nx2_1,1]=rgx; X2_1[nx2_1,2]=rox; nx2_1+=1
                    for jx in range(nx3_0):
                        rx=X3_0[jx,0]; rgx=X3_0[jx,1]; rox=X3_0[jx,2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X3_1[nx3_1,0]=rx; X3_1[nx3_1,1]=rgx; X3_1[nx3_1,2]=rox; nx3_1+=1
                    for jx in range(nx4_0):
                        rx=X4_0[jx,0]; rgx=X4_0[jx,1]; rox=X4_0[jx,2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X4_1[nx4_1,0]=rx; X4_1[nx4_1,1]=rgx; X4_1[nx4_1,2]=rox; nx4_1+=1
                    for jx in range(nx5_0):
                        rx=X5_0[jx,0]; rgx=X5_0[jx,1]; rox=X5_0[jx,2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X5_1[nx5_1,0]=rx; X5_1[nx5_1,1]=rgx; X5_1[nx5_1,2]=rox; nx5_1+=1
                    for jx in range(nx6_0):
                        rx=X6_0[jx,0]; rgx=X6_0[jx,1]; rox=X6_0[jx,2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X6_1[nx6_1,0]=rx; X6_1[nx6_1,1]=rgx; X6_1[nx6_1,2]=rox; nx6_1+=1
                    for jx in range(nx7_0):
                        rx=X7_0[jx,0]; rgx=X7_0[jx,1]; rox=X7_0[jx,2]
                        if eq_bits_42(rx & y1, 1) and eq_bits_42(rgx & y1, 2):
                            X7_1[nx7_1,0]=rx; X7_1[nx7_1,1]=rgx; X7_1[nx7_1,2]=rox; nx7_1+=1
                if nx0_1==0 or nx1_1==0 or nx2_1==0 or nx3_1==0 or nx4_1==0 or nx5_1==0 or nx6_1==0 or nx7_1==0:
                    nx0_1 = 0; break
                if nx0_2 == -1:
                    nx0_2=0; nx1_2=0; nx2_2=0; nx3_2=0; nx4_2=0; nx5_2=0; nx6_2=0; nx7_2=0
                    for jx in range(nx0_1):
                        rx=X0_1[jx,0]; rgx=X0_1[jx,1]; rox=X0_1[jx,2]
                        if (rx & col_u2_2)==z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X0_2[nx0_2,0]=rx; X0_2[nx0_2,1]=rgx; X0_2[nx0_2,2]=rox; nx0_2+=1
                    for jx in range(nx1_1):
                        rx=X1_1[jx,0]; rgx=X1_1[jx,1]; rox=X1_1[jx,2]
                        if (rx & col_u2_2)==z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X1_2[nx1_2,0]=rx; X1_2[nx1_2,1]=rgx; X1_2[nx1_2,2]=rox; nx1_2+=1
                    for jx in range(nx2_1):
                        rx=X2_1[jx,0]; rgx=X2_1[jx,1]; rox=X2_1[jx,2]
                        if (rx & col_u2_2)==z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X2_2[nx2_2,0]=rx; X2_2[nx2_2,1]=rgx; X2_2[nx2_2,2]=rox; nx2_2+=1
                    for jx in range(nx3_1):
                        rx=X3_1[jx,0]; rgx=X3_1[jx,1]; rox=X3_1[jx,2]
                        if (rx & col_u2_2)==z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X3_2[nx3_2,0]=rx; X3_2[nx3_2,1]=rgx; X3_2[nx3_2,2]=rox; nx3_2+=1
                    for jx in range(nx4_1):
                        rx=X4_1[jx,0]; rgx=X4_1[jx,1]; rox=X4_1[jx,2]
                        if (rx & col_u2_2)==z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X4_2[nx4_2,0]=rx; X4_2[nx4_2,1]=rgx; X4_2[nx4_2,2]=rox; nx4_2+=1
                    for jx in range(nx5_1):
                        rx=X5_1[jx,0]; rgx=X5_1[jx,1]; rox=X5_1[jx,2]
                        if (rx & col_u2_2)==z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X5_2[nx5_2,0]=rx; X5_2[nx5_2,1]=rgx; X5_2[nx5_2,2]=rox; nx5_2+=1
                    for jx in range(nx6_1):
                        rx=X6_1[jx,0]; rgx=X6_1[jx,1]; rox=X6_1[jx,2]
                        if (rx & col_u2_2)==z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X6_2[nx6_2,0]=rx; X6_2[nx6_2,1]=rgx; X6_2[nx6_2,2]=rox; nx6_2+=1
                    for jx in range(nx7_1):
                        rx=X7_1[jx,0]; rgx=X7_1[jx,1]; rox=X7_1[jx,2]
                        if (rx & col_u2_2)==z64 and eq_bits_42(rx & y2, 1) and eq_bits_42(rgx & y2, 2):
                            X7_2[nx7_2,0]=rx; X7_2[nx7_2,1]=rgx; X7_2[nx7_2,2]=rox; nx7_2+=1
                if nx0_2==0 or nx1_2==0 or nx2_2==0 or nx3_2==0 or nx4_2==0 or nx5_2==0 or nx6_2==0 or nx7_2==0:
                    break
                col_u2_3 = col_u2_2 | (col_u1_1 & ry3)
                col_u1_3 = col_u1_2 | ry3
                nx0_3=0; nx1_3=0; nx2_3=0; nx3_3=0; nx4_3=0; nx5_3=0; nx6_3=0; nx7_3=0
                for jx in range(nx0_2):
                    rx=X0_2[jx,0]; rgx=X0_2[jx,1]; rox=X0_2[jx,2]
                    if (rx & col_u2_3)==z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X0_3[nx0_3,0]=rx; X0_3[nx0_3,1]=rgx; X0_3[nx0_3,2]=rox; nx0_3+=1
                if nx0_3==0: continue
                for jx in range(nx1_2):
                    rx=X1_2[jx,0]; rgx=X1_2[jx,1]; rox=X1_2[jx,2]
                    if (rx & col_u2_3)==z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X1_3[nx1_3,0]=rx; X1_3[nx1_3,1]=rgx; X1_3[nx1_3,2]=rox; nx1_3+=1
                if nx1_3==0: continue
                for jx in range(nx2_2):
                    rx=X2_2[jx,0]; rgx=X2_2[jx,1]; rox=X2_2[jx,2]
                    if (rx & col_u2_3)==z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X2_3[nx2_3,0]=rx; X2_3[nx2_3,1]=rgx; X2_3[nx2_3,2]=rox; nx2_3+=1
                if nx2_3==0: continue
                for jx in range(nx3_2):
                    rx=X3_2[jx,0]; rgx=X3_2[jx,1]; rox=X3_2[jx,2]
                    if (rx & col_u2_3)==z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X3_3[nx3_3,0]=rx; X3_3[nx3_3,1]=rgx; X3_3[nx3_3,2]=rox; nx3_3+=1
                if nx3_3==0: continue
                for jx in range(nx4_2):
                    rx=X4_2[jx,0]; rgx=X4_2[jx,1]; rox=X4_2[jx,2]
                    if (rx & col_u2_3)==z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X4_3[nx4_3,0]=rx; X4_3[nx4_3,1]=rgx; X4_3[nx4_3,2]=rox; nx4_3+=1
                if nx4_3==0: continue
                for jx in range(nx5_2):
                    rx=X5_2[jx,0]; rgx=X5_2[jx,1]; rox=X5_2[jx,2]
                    if (rx & col_u2_3)==z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X5_3[nx5_3,0]=rx; X5_3[nx5_3,1]=rgx; X5_3[nx5_3,2]=rox; nx5_3+=1
                if nx5_3==0: continue
                for jx in range(nx6_2):
                    rx=X6_2[jx,0]; rgx=X6_2[jx,1]; rox=X6_2[jx,2]
                    if (rx & col_u2_3)==z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X6_3[nx6_3,0]=rx; X6_3[nx6_3,1]=rgx; X6_3[nx6_3,2]=rox; nx6_3+=1
                if nx6_3==0: continue
                for jx in range(nx7_2):
                    rx=X7_2[jx,0]; rgx=X7_2[jx,1]; rox=X7_2[jx,2]
                    if (rx & col_u2_3)==z64 and eq_bits_42(rx & ry3, 1) and eq_bits_42(rgx & ry3, 2):
                        X7_3[nx7_3,0]=rx; X7_3[nx7_3,1]=rgx; X7_3[nx7_3,2]=rox; nx7_3+=1
                if nx7_3==0: continue

                nd, sl = solve_8dom_after_y(
                    col_u1_3, col_u2_3,
                    X0_3, nx0_3, X1_3, nx1_3, X2_3, nx2_3, X3_3, nx3_3,
                    X4_3, nx4_3, X5_3, nx5_3, X6_3, nx6_3, X7_3, nx7_3,
                    Gp8, KW8, ALL60
                )
                loc_nodes += nd
                loc_sols += sl
        for k2 in range(n2_1): in_c2_1[c2_1[k2]] = 0
    out[0] = loc_b1; out[1] = loc_nodes; out[2] = loc_sols
    return out


@njit(parallel=True)
def solve_class_114_parallel(
    n_test, reps, rep_canons,
    Y0, Y0_adj, Y0_deg, cy1_can,
    Y2, Y2_adj, Y2_deg, cy2_can,
    X0, X1, X2, X3, X4, X5, X6, X7,
    Gp8, KW8, ALL60,
    luts_g01, is_g012_flag, luts_swap01
):
    counts = np.zeros((n_test, 4), dtype=np.int64)
    for idx_rep in prange(n_test):
        counts[idx_rep] = solve_rep_114_8dom(
            reps[idx_rep], rep_canons[idx_rep],
            Y0, Y0_adj, Y0_deg, cy1_can,
            Y2, Y2_adj, Y2_deg, cy2_can,
            X0, X1, X2, X3, X4, X5, X6, X7,
            Gp8, KW8, ALL60,
            luts_g01, is_g012_flag, luts_swap01
        )
    return counts.sum(axis=0)


def main():
    t0 = time.time()
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
    O11_int = sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] in I_B1 and cols_60[c][1] in I_B1)
    O12_int = sum(1 << m for m, (c, gc) in enumerate(orbs_30) if (cols_60[c][0] in I_B1) ^ (cols_60[c][1] in I_B1))
    col_orb_bit = [0] * 60
    for idx_m, (c, gc) in enumerate(orbs_30):
        col_orb_bit[c] = 1 << idx_m; col_orb_bit[gc] = 1 << idx_m

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
                    rem_deg[w] -= 1; nxm |= cb; ngxm |= gcb; nu2 |= (nu1 & ob); nu1 |= ob
                rem_deg[v_idx] = 0
                bt_v(v_idx + 1, n_ch + need, nxm, ngxm, nu1, nu2)
                rem_deg[v_idx] = need
                for c, w, cb, gcb, ob in comb: rem_deg[w] += 1
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
                for c, w, cb, gcb, ob in comb:
                    rem_deg[w] -= 1; nxm |= cb; ngxm |= gcb; nu2 |= (nu1 & ob); nu1 |= ob
                if nu2.bit_count() <= req_pairs:
                    rem_deg[v_idx] = 0
                    bt_v(v_idx + 1, n_ch + need, nxm, ngxm, nu1, nu2)
                    rem_deg[v_idx] = need
                for c, w, cb, gcb, ob in comb: rem_deg[w] += 1
        bt_v(0, 0, 0, 0, 0, 0)
        arr = np.ascontiguousarray(np.array(res, dtype=np.uint64))
        x_cache[key] = arr
        return arr

    Y0_pool = gen_2block_rows((0, 0, 2, 2), 0)
    Y2_pool = gen_2block_rows((2, 2, 0, 0), 0)
    O12_y0_mask = 0
    for i in range(len(Y0_pool)): O12_y0_mask |= int(Y0_pool[i, 4])
    by_orb0 = defaultdict(list)
    for i in range(len(Y0_pool)): by_orb0[(int(Y0_pool[i, 2]), int(Y0_pool[i, 4]))].append(i)
    Y0_adj = np.zeros((len(Y0_pool), 32), dtype=np.int32)
    Y0_deg = np.zeros(len(Y0_pool), dtype=np.int32)
    for i in range(len(Y0_pool)):
        comp = (O11_int ^ int(Y0_pool[i, 2]), O12_y0_mask ^ int(Y0_pool[i, 4]))
        lst = [j for j in by_orb0.get(comp, []) if j > i]
        Y0_deg[i] = len(lst)
        for k, j in enumerate(lst): Y0_adj[i, k] = j

    O12_y2_mask = 0
    for i in range(len(Y2_pool)): O12_y2_mask |= int(Y2_pool[i, 4])
    by_orb2 = defaultdict(list)
    for i in range(len(Y2_pool)): by_orb2[(int(Y2_pool[i, 2]), int(Y2_pool[i, 4]))].append(i)
    Y2_adj = np.zeros((len(Y2_pool), 32), dtype=np.int32)
    Y2_deg = np.zeros(len(Y2_pool), dtype=np.int32)
    for i in range(len(Y2_pool)):
        comp = (O11_int ^ int(Y2_pool[i, 2]), O12_y2_mask ^ int(Y2_pool[i, 4]))
        lst = [j for j in by_orb2.get(comp, []) if j > i]
        Y2_deg[i] = len(lst)
        for k, j in enumerate(lst): Y2_adj[i, k] = j

    F4 = F12[:4, :4]; I4 = np.eye(4, dtype=int); J4 = np.ones((4, 4), dtype=int)
    F8 = F12[:8, :8]; I8 = np.eye(8, dtype=int); J8 = np.ones((8, 8), dtype=int)
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
    ALL60 = np.uint64((1 << 60) - 1)
    id_map = tuple(range(60))

    rem11 = [39, 41, 43, 5, 6, 34, 33, 52, 55, 16, 54]
    print(f"Prepared Y pools in {time.time()-t0:.2f}s. Solving 11 secondary 1+1+4 classes: {rem11}", flush=True)

    for idx_m, ex_c in enumerate(rem11):
        tc0 = time.time()
        M8, E8 = c4_classes[ex_c]
        KW8 = (2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)).astype(np.int32)
        D8 = 2 * J8 - I8 - F8 - M8 - (E8 @ F8)
        Gp8_4 = (7 * I8 + J8 - M8).astype(np.int32)
        X = [gen_4block_rows(tuple(int(D8[r, j]) for j in range(8)), int(KW8[r, r])) for r in range(8)]
        xlens = [len(x) for x in X]

        # Full 8-row decoupled stabilizer Stab_{S_8 x B_4}(Gp8_4, KW8, D8)
        m_pairs = [(r, int(np.where(M8[r] == 1)[0][0])) for r in range(8) if r < int(np.where(M8[r] == 1)[0][0])]
        stab8 = []
        for bp in permutations(range(4)):
            for flips in product((0, 1), repeat=4):
                pr = [0] * 8
                for b_old, (b_new, fl) in enumerate(zip(bp, flips)):
                    u_old, v_old = m_pairs[b_old]
                    u_new, v_new = m_pairs[b_new]
                    pr[u_old] = u_new if fl == 0 else v_new
                    pr[v_old] = v_new if fl == 0 else u_new
                pr = tuple(pr)
                if any(xlens[pr[a]] != xlens[a] for a in range(8)): continue
                if not (KW8 == KW8[np.ix_(pr, pr)]).all(): continue
                d_pr = D8[list(pr), :]
                for pc in b4_perms_8:
                    if (d_pr[:, pc] == D8).all():
                        stab8.append((pr, pc))

        stab_y_to_0 = [[] for _ in range(4)]
        seen_y_to_0 = [set() for _ in range(4)]
        g01_dict = {}
        swap01_perms = []
        seen_swap01 = set()

        for pr2, pc2 in stab2_m16:
            for pr4, pc4 in stab8:
                g_p = list(pc4) + [8 + x for x in pc2]
                c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                t_map = tuple(c_map)
                for a_idx, orig_r in enumerate(ord2):
                    if pr2[orig_r] == ord2[0] and t_map not in seen_y_to_0[a_idx]:
                        seen_y_to_0[a_idx].add(t_map)
                        stab_y_to_0[a_idx].append(c_map)
                if pr2[ord2[0]] == ord2[0] and pr2[ord2[1]] == ord2[1] and t_map != id_map:
                    f2 = 1 if pr2[ord2[2]] == ord2[2] else 0
                    prev = g01_dict.get(t_map, 0)
                    g01_dict[t_map] = max(prev, f2)
                if pr2[ord2[0]] == ord2[1] and pr2[ord2[1]] == ord2[0] and t_map not in seen_swap01:
                    seen_swap01.add(t_map)
                    swap01_perms.append(c_map)

        g01_perms = [list(k) for k in g01_dict.keys()]
        g012_flags = [v for v in g01_dict.values()]
        cy_cans = [compute_canons_lut(Y[a], build_perm_luts(stab_y_to_0[a])) for a in range(4)]
        luts_g01 = build_perm_luts(g01_perms)
        is_g012_flag = np.ascontiguousarray(np.array(g012_flags, dtype=np.int32))
        luts_swap01 = build_perm_luts(swap01_perms)

        reps = np.ascontiguousarray([i for i in range(len(Y[0])) if Y[0][i, 0] == cy_cans[0][i]], dtype=np.int32)
        rep_canons = np.ascontiguousarray([cy_cans[0][i] for i in reps], dtype=np.uint64)

        if idx_m == 0:
            _ = solve_class_114_parallel(
                1, reps[:1], rep_canons[:1],
                Y0_pool, Y0_adj, Y0_deg, cy_cans[1],
                Y2_pool, Y2_adj, Y2_deg, cy_cans[2],
                X[0], X[1], X[2], X[3], X[4], X[5], X[6], X[7],
                Gp8_4, KW8, ALL60,
                luts_g01, is_g012_flag, luts_swap01
            )

        res = solve_class_114_parallel(
            len(reps), reps, rep_canons,
            Y0_pool, Y0_adj, Y0_deg, cy_cans[1],
            Y2_pool, Y2_adj, Y2_deg, cy_cans[2],
            X[0], X[1], X[2], X[3], X[4], X[5], X[6], X[7],
            Gp8_4, KW8, ALL60,
            luts_g01, is_g012_flag, luts_swap01
        )
        if int(res[2]) != 0:
            raise RuntimeError(f"[1+1+4 Class {ex_c:2d} FAIL] Expected 0 solutions, got sols={int(res[2])}")
        print(f"[1+1+4 Class {ex_c:2d}] |Stab8x2|={len(stab8)*len(stab2_m16):4d} | reps={len(reps):4d} | b1={int(res[0]):7d} nodes={int(res[1]):8d} sols={int(res[2])} | {time.time()-tc0:.2f}s", flush=True)


if __name__ == "__main__":
    main()
