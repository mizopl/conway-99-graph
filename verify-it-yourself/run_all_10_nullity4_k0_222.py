import json
import time
import numpy as np
import numba as nb
from itertools import combinations, permutations, product
import test_k2_components as tk2

cols_60 = []
col_idx = {}
for b1 in range(6):
    for b2 in range(b1 + 1, 6):
        for s1 in (0, 1):
            for s2 in (0, 1):
                j1 = 2 * b1 + s1
                j2 = 2 * b2 + s2
                c = len(cols_60)
                cols_60.append((j1, j2))
                col_idx[(j1, j2)] = c
                col_idx[(j2, j1)] = c
g_col = [col_idx[(j1 ^ 1, j2 ^ 1)] for (j1, j2) in cols_60]
orbs_30 = [(c, g_col[c]) for c in range(60) if c < g_col[c]]

def get_comp_orb_masks(I_B_set):
    cut_m = 0
    out_m = 0
    for idx_m, (c, gc) in enumerate(orbs_30):
        u, v = cols_60[c]
        cnt_in = (1 if u in I_B_set else 0) + (1 if v in I_B_set else 0)
        if cnt_in == 1:
            cut_m |= (1 << idx_m)
        elif cnt_in == 0:
            out_m |= (1 << idx_m)
    return cut_m, out_m

row_pool_cache = {}
def gen_2block_rows_cached(I_B_tuple, target_deg, diag_kw):
    key = (I_B_tuple, target_deg, diag_kw)
    if key in row_pool_cache:
        return row_pool_cache[key]
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
        u, v = cols_60[c]
        adj_cols[min(u, v)].append((c, max(u, v)))
    
    rem_deg = list(target_deg)
    chosen = []
    res = []
    
    def bt_v(v_idx):
        if v_idx == 12:
            if len(chosen) == 10:
                r_set = set(chosen)
                npairs = 0
                ok_p = True
                for c in chosen:
                    if c < g_col[c] and g_col[c] in r_set:
                        npairs += 1
                        if cols_60[c][0] in I_B_set or cols_60[c][1] in I_B_set:
                            ok_p = False
                            break
                if ok_p and npairs == req_pairs:
                    xm = 0
                    gxm = 0
                    c1_cut = 0
                    c1_out = 0
                    c2_out = 0
                    for c in chosen:
                        xm |= 1 << c
                        gxm |= 1 << g_col[c]
                    for idx_m, (c, gc) in enumerate(orbs_30):
                        s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                        if (cut_orb_mask >> idx_m) & 1:
                            if s == 1:
                                c1_cut |= 1 << idx_m
                        elif (out_orb_mask >> idx_m) & 1:
                            if s == 1:
                                c1_out |= 1 << idx_m
                            elif s == 2:
                                c2_out |= 1 << idx_m
                    res.append((xm, gxm, c1_cut, c1_out, c2_out))
            return
        need = rem_deg[v_idx]
        if need < 0:
            return
        avail = [(c, w) for (c, w) in adj_cols[v_idx] if rem_deg[w] > 0]
        if len(avail) < need:
            return
        for comb in combinations(avail, need):
            for c, w in comb:
                rem_deg[w] -= 1
                chosen.append(c)
            rem_deg[v_idx] = 0
            bt_v(v_idx + 1)
            rem_deg[v_idx] = need
            for c, w in comb:
                rem_deg[w] += 1
                chosen.pop()

    bt_v(0)
    arr = np.array(res, dtype=np.uint64)
    row_pool_cache[key] = arr
    return arr

@nb.njit(inline="always")
def popcnt64(x):
    x = x - ((x >> 1) & np.uint64(0x5555555555555555))
    x = (x & np.uint64(0x3333333333333333)) + ((x >> 2) & np.uint64(0x3333333333333333))
    x = (x + (x >> 4)) & np.uint64(0x0F0F0F0F0F0F0F0F)
    return int((x * np.uint64(0x0101010101010101)) >> np.uint64(56))

@nb.njit
def permute_mask(xm, c_map):
    out = np.uint64(0)
    for c in range(60):
        if (xm >> np.uint64(c)) & np.uint64(1):
            out |= np.uint64(1) << np.uint64(c_map[c])
    return out

@nb.njit
def compute_canonical_masks(La, col_perms):
    n = len(La)
    canon = np.empty(n, dtype=np.uint64)
    if len(col_perms) == 0:
        for i in range(n):
            canon[i] = np.uint64(0xFFFFFFFFFFFFFFFF)
        return canon
    for i in range(n):
        xm = La[i, 0]
        best = np.uint64(0xFFFFFFFFFFFFFFFF)
        for p_idx in range(len(col_perms)):
            pm = permute_mask(xm, col_perms[p_idx])
            if pm < best:
                best = pm
        canon[i] = best
    return canon

@nb.njit(parallel=True)
def solve_222_full_12row(
    reps, rep_canons,
    L0, L1, L2, L3, L4, L5, L6, L7, L8, L9, L10, L11,
    c1_can, c2_can, c3_can, c4_can, c5_can, c6_can, c7_can,
    Gp, KW0, O33_mask, O13_mask, O23_mask
):
    n_reps = len(reps)
    b1_sols_arr = np.zeros(n_reps, dtype=np.int64)
    b2_sols_arr = np.zeros(n_reps, dtype=np.int64)
    b3_sols_arr = np.zeros(n_reps, dtype=np.int64)
    
    for r_idx in nb.prange(n_reps):
        i0 = reps[r_idx]
        min_can = rep_canons[r_idx]
        x0, gx0, cut0, o1_0, o2_0 = L0[i0, 0], L0[i0, 1], L0[i0, 2], L0[i0, 3], L0[i0, 4]
        u1_0 = o1_0 | o2_0
        u2_0 = o2_0
        
        c1 = np.empty(135000, dtype=np.int32)
        n1 = 0
        for i in range(len(L1)):
            if c1_can[i] < min_can:
                continue
            if (cut0 & L1[i, 2]) == 0 and (L1[i, 4] & u1_0) == 0 and (L1[i, 3] & u2_0) == 0:
                if popcnt64(x0 & L1[i, 0]) == Gp[0, 1] and popcnt64(x0 & L1[i, 1]) == KW0[0, 1]:
                    c1[n1] = i
                    n1 += 1
                    
        c2 = np.empty(135000, dtype=np.int32)
        n2 = 0
        for i in range(len(L2)):
            if c2_can[i] < min_can:
                continue
            if (cut0 & L2[i, 2]) == 0 and (L2[i, 4] & u1_0) == 0 and (L2[i, 3] & u2_0) == 0:
                if popcnt64(x0 & L2[i, 0]) == Gp[0, 2] and popcnt64(x0 & L2[i, 1]) == KW0[0, 2]:
                    c2[n2] = i
                    n2 += 1
                    
        c3 = np.empty(135000, dtype=np.int32)
        n3 = 0
        for i in range(len(L3)):
            if c3_can[i] < min_can:
                continue
            if (cut0 & L3[i, 2]) == 0 and (L3[i, 4] & u1_0) == 0 and (L3[i, 3] & u2_0) == 0:
                if popcnt64(x0 & L3[i, 0]) == Gp[0, 3] and popcnt64(x0 & L3[i, 1]) == KW0[0, 3]:
                    c3[n3] = i
                    n3 += 1

        c4_0 = np.empty(40000, dtype=np.int32)
        n4_0 = 0
        for i in range(len(L4)):
            if c4_can[i] < min_can:
                continue
            if (o2_0 & L4[i, 4]) == 0 and popcnt64(x0 & L4[i, 0]) == 1 and popcnt64(x0 & L4[i, 1]) == 2:
                c4_0[n4_0] = i
                n4_0 += 1
        c5_0 = np.empty(40000, dtype=np.int32)
        n5_0 = 0
        for i in range(len(L5)):
            if c5_can[i] < min_can:
                continue
            if (o2_0 & L5[i, 4]) == 0 and popcnt64(x0 & L5[i, 0]) == 1 and popcnt64(x0 & L5[i, 1]) == 2:
                c5_0[n5_0] = i
                n5_0 += 1
        c6_0 = np.empty(40000, dtype=np.int32)
        n6_0 = 0
        for i in range(len(L6)):
            if c6_can[i] < min_can:
                continue
            if (o2_0 & L6[i, 4]) == 0 and popcnt64(x0 & L6[i, 0]) == 1 and popcnt64(x0 & L6[i, 1]) == 2:
                c6_0[n6_0] = i
                n6_0 += 1
        c7_0 = np.empty(40000, dtype=np.int32)
        n7_0 = 0
        for i in range(len(L7)):
            if c7_can[i] < min_can:
                continue
            if (o2_0 & L7[i, 4]) == 0 and popcnt64(x0 & L7[i, 0]) == 1 and popcnt64(x0 & L7[i, 1]) == 2:
                c7_0[n7_0] = i
                n7_0 += 1

        c8_0 = np.empty(40000, dtype=np.int32)
        n8_0 = 0
        for i in range(len(L8)):
            if (o2_0 & L8[i, 4]) == 0 and popcnt64(x0 & L8[i, 0]) == 1 and popcnt64(x0 & L8[i, 1]) == 2:
                c8_0[n8_0] = i
                n8_0 += 1
        c9_0 = np.empty(40000, dtype=np.int32)
        n9_0 = 0
        for i in range(len(L9)):
            if (o2_0 & L9[i, 4]) == 0 and popcnt64(x0 & L9[i, 0]) == 1 and popcnt64(x0 & L9[i, 1]) == 2:
                c9_0[n9_0] = i
                n9_0 += 1
        c10_0 = np.empty(40000, dtype=np.int32)
        n10_0 = 0
        for i in range(len(L10)):
            if (o2_0 & L10[i, 4]) == 0 and popcnt64(x0 & L10[i, 0]) == 1 and popcnt64(x0 & L10[i, 1]) == 2:
                c10_0[n10_0] = i
                n10_0 += 1
        c11_0 = np.empty(40000, dtype=np.int32)
        n11_0 = 0
        for i in range(len(L11)):
            if (o2_0 & L11[i, 4]) == 0 and popcnt64(x0 & L11[i, 0]) == 1 and popcnt64(x0 & L11[i, 1]) == 2:
                c11_0[n11_0] = i
                n11_0 += 1

        c2_1 = np.empty(8000, dtype=np.int32)
        c3_1 = np.empty(8000, dtype=np.int32)
        
        c4_1 = np.empty(8000, dtype=np.int32)
        c5_1 = np.empty(8000, dtype=np.int32)
        c6_1 = np.empty(8000, dtype=np.int32)
        c7_1 = np.empty(8000, dtype=np.int32)
        
        c4_2 = np.empty(2000, dtype=np.int32)
        c5_2 = np.empty(2000, dtype=np.int32)
        c6_2 = np.empty(2000, dtype=np.int32)
        c7_2 = np.empty(2000, dtype=np.int32)
        
        c4_3 = np.empty(500, dtype=np.int32)
        c5_3 = np.empty(500, dtype=np.int32)
        c6_3 = np.empty(500, dtype=np.int32)
        c7_3 = np.empty(500, dtype=np.int32)
        
        c8_7 = np.empty(300, dtype=np.int32)
        c9_7 = np.empty(300, dtype=np.int32)
        c10_7 = np.empty(300, dtype=np.int32)
        c11_7 = np.empty(300, dtype=np.int32)
        
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
            
            n2_1 = 0
            for idx2 in range(n2):
                i2 = c2[idx2]
                if (cut_01 & L2[i2, 2]) == 0 and (L2[i2, 4] & u1_01) == 0 and (L2[i2, 3] & u2_01) == 0:
                    if popcnt64(x1 & L2[i2, 0]) == Gp[1, 2] and popcnt64(x1 & L2[i2, 1]) == KW0[1, 2]:
                        c2_1[n2_1] = i2
                        n2_1 += 1
            if n2_1 == 0:
                continue
                
            n3_1 = 0
            for idx3 in range(n3):
                i3 = c3[idx3]
                if (cut_01 & L3[i3, 2]) == 0 and (L3[i3, 4] & u1_01) == 0 and (L3[i3, 3] & u2_01) == 0:
                    if popcnt64(x1 & L3[i3, 0]) == Gp[1, 3] and popcnt64(x1 & L3[i3, 1]) == KW0[1, 3]:
                        c3_1[n3_1] = i3
                        n3_1 += 1
            if n3_1 == 0:
                continue

            n4_1 = 0
            for k in range(n4_0):
                row_i = c4_0[k]
                rx = L4[row_i, 0]
                if (rx & col_u2_01) == 0 and (L4[row_i, 4] & o2_1) == 0:
                    if popcnt64(rx & x1) == 1 and popcnt64(rx & gx1) == 2:
                        c4_1[n4_1] = row_i
                        n4_1 += 1
            if n4_1 == 0:
                continue
            n5_1 = 0
            for k in range(n5_0):
                row_i = c5_0[k]
                rx = L5[row_i, 0]
                if (rx & col_u2_01) == 0 and (L5[row_i, 4] & o2_1) == 0:
                    if popcnt64(rx & x1) == 1 and popcnt64(rx & gx1) == 2:
                        c5_1[n5_1] = row_i
                        n5_1 += 1
            if n5_1 == 0:
                continue
            n6_1 = 0
            for k in range(n6_0):
                row_i = c6_0[k]
                rx = L6[row_i, 0]
                if (rx & col_u2_01) == 0 and (L6[row_i, 4] & o2_1) == 0:
                    if popcnt64(rx & x1) == 1 and popcnt64(rx & gx1) == 2:
                        c6_1[n6_1] = row_i
                        n6_1 += 1
            if n6_1 == 0:
                continue
            n7_1 = 0
            for k in range(n7_0):
                row_i = c7_0[k]
                rx = L7[row_i, 0]
                if (rx & col_u2_01) == 0 and (L7[row_i, 4] & o2_1) == 0:
                    if popcnt64(rx & x1) == 1 and popcnt64(rx & gx1) == 2:
                        c7_1[n7_1] = row_i
                        n7_1 += 1
            if n7_1 == 0:
                continue
                
            for idx2 in range(n2_1):
                i2 = c2_1[idx2]
                x2, gx2, cut2, o1_2, o2_2 = L2[i2, 0], L2[i2, 1], L2[i2, 2], L2[i2, 3], L2[i2, 4]
                cut_012 = cut_01 | cut2
                u2_012 = u2_01 | o2_2 | (u1_01 & o1_2)
                u1_012 = u1_01 | o1_2 | o2_2
                col_u2_012 = col_u2_01 | ((x0 | x1) & x2)
                
                has_i3 = False
                for idx3 in range(n3_1):
                    i3 = c3_1[idx3]
                    if (cut_012 & L3[i3, 2]) == 0 and (L3[i3, 4] & u1_012) == 0 and (L3[i3, 3] & u2_012) == 0:
                        if popcnt64(x2 & L3[i3, 0]) == Gp[2, 3] and popcnt64(x2 & L3[i3, 1]) == KW0[2, 3]:
                            has_i3 = True
                            break
                if not has_i3:
                    continue
                    
                n4_2 = 0
                for k in range(n4_1):
                    row_i = c4_1[k]
                    rx = L4[row_i, 0]
                    if (rx & col_u2_012) == 0 and (L4[row_i, 4] & o2_2) == 0:
                        if popcnt64(rx & x2) == 1 and popcnt64(rx & gx2) == 2:
                            c4_2[n4_2] = row_i
                            n4_2 += 1
                if n4_2 == 0:
                    continue
                n5_2 = 0
                for k in range(n5_1):
                    row_i = c5_1[k]
                    rx = L5[row_i, 0]
                    if (rx & col_u2_012) == 0 and (L5[row_i, 4] & o2_2) == 0:
                        if popcnt64(rx & x2) == 1 and popcnt64(rx & gx2) == 2:
                            c5_2[n5_2] = row_i
                            n5_2 += 1
                if n5_2 == 0:
                    continue
                n6_2 = 0
                for k in range(n6_1):
                    row_i = c6_1[k]
                    rx = L6[row_i, 0]
                    if (rx & col_u2_012) == 0 and (L6[row_i, 4] & o2_2) == 0:
                        if popcnt64(rx & x2) == 1 and popcnt64(rx & gx2) == 2:
                            c6_2[n6_2] = row_i
                            n6_2 += 1
                if n6_2 == 0:
                    continue
                n7_2 = 0
                for k in range(n7_1):
                    row_i = c7_1[k]
                    rx = L7[row_i, 0]
                    if (rx & col_u2_012) == 0 and (L7[row_i, 4] & o2_2) == 0:
                        if popcnt64(rx & x2) == 1 and popcnt64(rx & gx2) == 2:
                            c7_2[n7_2] = row_i
                            n7_2 += 1
                if n7_2 == 0:
                    continue
                
                for idx3 in range(n3_1):
                    i3 = c3_1[idx3]
                    if (cut_012 & L3[i3, 2]) != 0 or (L3[i3, 4] & u1_012) != 0 or (L3[i3, 3] & u2_012) != 0:
                        continue
                    x3, gx3, o2_3 = L3[i3, 0], L3[i3, 1], L3[i3, 4]
                    if popcnt64(x2 & x3) != Gp[2, 3] or popcnt64(x2 & gx3) != KW0[2, 3]:
                        continue
                        
                    local_b1 += 1
                    col_u1_B1 = x0 | x1 | x2 | x3
                    col_u2_B1 = col_u2_012 | ((x0 | x1 | x2) & x3)
                    g_col_u2_B1 = (gx0 & gx1) | (gx0 & gx2) | (gx0 & gx3) | (gx1 & gx2) | (gx1 & gx3) | (gx2 & gx3)
                    orb_p_B1 = orb_p_01 | o2_2 | o2_3
                    
                    req2_B2 = O33_mask & (~col_u1_B1)
                    req1_B2 = (O33_mask & (~col_u2_B1)) | (O13_mask & (~col_u1_B1)) | (O23_mask & g_col_u2_B1)
                    
                    n4_3 = 0
                    or4 = np.uint64(0)
                    for k in range(n4_2):
                        row_i = c4_2[k]
                        rx = L4[row_i, 0]
                        if (rx & col_u2_B1) == 0 and (L4[row_i, 4] & o2_3) == 0:
                            if popcnt64(rx & x3) == 1 and popcnt64(rx & gx3) == 2:
                                c4_3[n4_3] = row_i
                                n4_3 += 1
                                or4 |= rx
                    if n4_3 == 0:
                        continue
                        
                    n5_3 = 0
                    or5 = np.uint64(0)
                    for k in range(n5_2):
                        row_i = c5_2[k]
                        rx = L5[row_i, 0]
                        if (rx & col_u2_B1) == 0 and (L5[row_i, 4] & o2_3) == 0:
                            if popcnt64(rx & x3) == 1 and popcnt64(rx & gx3) == 2:
                                c5_3[n5_3] = row_i
                                n5_3 += 1
                                or5 |= rx
                    if n5_3 == 0:
                        continue
                        
                    n6_3 = 0
                    or6 = np.uint64(0)
                    for k in range(n6_2):
                        row_i = c6_2[k]
                        rx = L6[row_i, 0]
                        if (rx & col_u2_B1) == 0 and (L6[row_i, 4] & o2_3) == 0:
                            if popcnt64(rx & x3) == 1 and popcnt64(rx & gx3) == 2:
                                c6_3[n6_3] = row_i
                                n6_3 += 1
                                or6 |= rx
                    if n6_3 == 0:
                        continue
                        
                    n7_3 = 0
                    or7 = np.uint64(0)
                    for k in range(n7_2):
                        row_i = c7_2[k]
                        rx = L7[row_i, 0]
                        if (rx & col_u2_B1) == 0 and (L7[row_i, 4] & o2_3) == 0:
                            if popcnt64(rx & x3) == 1 and popcnt64(rx & gx3) == 2:
                                c7_3[n7_3] = row_i
                                n7_3 += 1
                                or7 |= rx
                    if n7_3 == 0:
                        continue
                        
                    all_or = or4 | or5 | or6 | or7
                    if (all_or & req1_B2) != req1_B2:
                        continue
                    pair_or = (or4 & or5) | (or4 & or6) | (or4 & or7) | (or5 & or6) | (or5 & or7) | (or6 & or7)
                    if (pair_or & req2_B2) != req2_B2:
                        continue
                        
                    for idx4 in range(n4_3):
                        i4 = c4_3[idx4]
                        x4, gx4, cut4, o1_4, o2_4 = L4[i4, 0], L4[i4, 1], L4[i4, 2], L4[i4, 3], L4[i4, 4]
                        b2_u1_4 = o1_4 | o2_4
                        b2_u2_4 = o2_4
                        col_u2_4 = col_u2_B1 | (col_u1_B1 & x4)
                        col_u1_4 = col_u1_B1 | x4
                        for idx5 in range(n5_3):
                            i5 = c5_3[idx5]
                            x5, gx5, cut5, o1_5, o2_5 = L5[i5, 0], L5[i5, 1], L5[i5, 2], L5[i5, 3], L5[i5, 4]
                            if (x5 & col_u2_4) != 0 or (cut4 & cut5) != 0 or (o2_5 & b2_u1_4) != 0 or (o1_5 & b2_u2_4) != 0:
                                continue
                            if popcnt64(x4 & x5) != Gp[4, 5] or popcnt64(x4 & gx5) != KW0[4, 5]:
                                continue
                            cut_45 = cut4 | cut5
                            b2_u2_45 = b2_u2_4 | o2_5 | (b2_u1_4 & o1_5)
                            b2_u1_45 = b2_u1_4 | o1_5 | o2_5
                            col_u2_45 = col_u2_4 | (col_u1_4 & x5)
                            col_u1_45 = col_u1_4 | x5
                            for idx6 in range(n6_3):
                                i6 = c6_3[idx6]
                                x6, gx6, cut6, o1_6, o2_6 = L6[i6, 0], L6[i6, 1], L6[i6, 2], L6[i6, 3], L6[i6, 4]
                                if (x6 & col_u2_45) != 0 or (cut_45 & cut6) != 0 or (o2_6 & b2_u1_45) != 0 or (o1_6 & b2_u2_45) != 0:
                                    continue
                                if popcnt64(x4 & x6) != Gp[4, 6] or popcnt64(x4 & gx6) != KW0[4, 6]:
                                    continue
                                if popcnt64(x5 & x6) != Gp[5, 6] or popcnt64(x5 & gx6) != KW0[5, 6]:
                                    continue
                                cut_456 = cut_45 | cut6
                                b2_u2_456 = b2_u2_45 | o2_6 | (b2_u1_45 & o1_6)
                                b2_u1_456 = b2_u1_45 | o1_6 | o2_6
                                col_u2_456 = col_u2_45 | (col_u1_45 & x6)
                                col_u1_456 = col_u1_45 | x6
                                for idx7 in range(n7_3):
                                    i7 = c7_3[idx7]
                                    x7, gx7, cut7, o1_7, o2_7 = L7[i7, 0], L7[i7, 1], L7[i7, 2], L7[i7, 3], L7[i7, 4]
                                    if (x7 & col_u2_456) != 0 or (cut_456 & cut7) != 0 or (o2_7 & b2_u1_456) != 0 or (o1_7 & b2_u2_456) != 0:
                                        continue
                                    if popcnt64(x4 & x7) != Gp[4, 7] or popcnt64(x4 & gx7) != KW0[4, 7]:
                                        continue
                                    if popcnt64(x5 & x7) != Gp[5, 7] or popcnt64(x5 & gx7) != KW0[5, 7]:
                                        continue
                                    if popcnt64(x6 & x7) != Gp[6, 7] or popcnt64(x6 & gx7) != KW0[6, 7]:
                                        continue
                                    
                                    local_b2 += 1
                                    col_u2_B12 = col_u2_456 | (col_u1_456 & x7)
                                    orb_p_B12 = orb_p_B1 | o2_4 | o2_5 | o2_6 | o2_7
                                    
                                    n8_7 = 0
                                    for k in range(n8_0):
                                        ri = c8_0[k]
                                        rx = L8[ri, 0]
                                        if (rx & col_u2_B12) != 0 or (L8[ri, 4] & orb_p_B12) != 0:
                                            continue
                                        if (popcnt64(rx & x1) == 1 and popcnt64(rx & x2) == 1 and popcnt64(rx & x3) == 1 and
                                            popcnt64(rx & x4) == 1 and popcnt64(rx & x5) == 1 and popcnt64(rx & x6) == 1 and popcnt64(rx & x7) == 1):
                                            if (popcnt64(rx & gx1) == 2 and popcnt64(rx & gx2) == 2 and popcnt64(rx & gx3) == 2 and
                                                popcnt64(rx & gx4) == 2 and popcnt64(rx & gx5) == 2 and popcnt64(rx & gx6) == 2 and popcnt64(rx & gx7) == 2):
                                                c8_7[n8_7] = ri
                                                n8_7 += 1
                                    if n8_7 == 0:
                                        continue
                                    n9_7 = 0
                                    for k in range(n9_0):
                                        ri = c9_0[k]
                                        rx = L9[ri, 0]
                                        if (rx & col_u2_B12) != 0 or (L9[ri, 4] & orb_p_B12) != 0:
                                            continue
                                        if (popcnt64(rx & x1) == 1 and popcnt64(rx & x2) == 1 and popcnt64(rx & x3) == 1 and
                                            popcnt64(rx & x4) == 1 and popcnt64(rx & x5) == 1 and popcnt64(rx & x6) == 1 and popcnt64(rx & x7) == 1):
                                            if (popcnt64(rx & gx1) == 2 and popcnt64(rx & gx2) == 2 and popcnt64(rx & gx3) == 2 and
                                                popcnt64(rx & gx4) == 2 and popcnt64(rx & gx5) == 2 and popcnt64(rx & gx6) == 2 and popcnt64(rx & gx7) == 2):
                                                c9_7[n9_7] = ri
                                                n9_7 += 1
                                    if n9_7 == 0:
                                        continue
                                    n10_7 = 0
                                    for k in range(n10_0):
                                        ri = c10_0[k]
                                        rx = L10[ri, 0]
                                        if (rx & col_u2_B12) != 0 or (L10[ri, 4] & orb_p_B12) != 0:
                                            continue
                                        if (popcnt64(rx & x1) == 1 and popcnt64(rx & x2) == 1 and popcnt64(rx & x3) == 1 and
                                            popcnt64(rx & x4) == 1 and popcnt64(rx & x5) == 1 and popcnt64(rx & x6) == 1 and popcnt64(rx & x7) == 1):
                                            if (popcnt64(rx & gx1) == 2 and popcnt64(rx & gx2) == 2 and popcnt64(rx & gx3) == 2 and
                                                popcnt64(rx & gx4) == 2 and popcnt64(rx & gx5) == 2 and popcnt64(rx & gx6) == 2 and popcnt64(rx & gx7) == 2):
                                                c10_7[n10_7] = ri
                                                n10_7 += 1
                                    if n10_7 == 0:
                                        continue
                                    n11_7 = 0
                                    for k in range(n11_0):
                                        ri = c11_0[k]
                                        rx = L11[ri, 0]
                                        if (rx & col_u2_B12) != 0 or (L11[ri, 4] & orb_p_B12) != 0:
                                            continue
                                        if (popcnt64(rx & x1) == 1 and popcnt64(rx & x2) == 1 and popcnt64(rx & x3) == 1 and
                                            popcnt64(rx & x4) == 1 and popcnt64(rx & x5) == 1 and popcnt64(rx & x6) == 1 and popcnt64(rx & x7) == 1):
                                            if (popcnt64(rx & gx1) == 2 and popcnt64(rx & gx2) == 2 and popcnt64(rx & gx3) == 2 and
                                                popcnt64(rx & gx4) == 2 and popcnt64(rx & gx5) == 2 and popcnt64(rx & gx6) == 2 and popcnt64(rx & gx7) == 2):
                                                c11_7[n11_7] = ri
                                                n11_7 += 1
                                    if n11_7 == 0:
                                        continue
                                    
                                    for idx8 in range(n8_7):
                                        i8 = c8_7[idx8]
                                        x8, gx8 = L8[i8, 0], L8[i8, 1]
                                        for idx9 in range(n9_7):
                                            i9 = c9_7[idx9]
                                            x9, gx9 = L9[i9, 0], L9[i9, 1]
                                            if popcnt64(x8 & x9) != Gp[8, 9] or popcnt64(x8 & gx9) != KW0[8, 9]:
                                                continue
                                            for idx10 in range(n10_7):
                                                i10 = c10_7[idx10]
                                                x10, gx10 = L10[i10, 0], L10[i10, 1]
                                                if popcnt64(x8 & x10) != Gp[8, 10] or popcnt64(x8 & gx10) != KW0[8, 10]:
                                                    continue
                                                if popcnt64(x9 & x10) != Gp[9, 10] or popcnt64(x9 & gx10) != KW0[9, 10]:
                                                    continue
                                                for idx11 in range(n11_7):
                                                    i11 = c11_7[idx11]
                                                    x11, gx11 = L11[i11, 0], L11[i11, 1]
                                                    if popcnt64(x8 & x11) != Gp[8, 11] or popcnt64(x8 & gx11) != KW0[8, 11]:
                                                        continue
                                                    if popcnt64(x9 & x11) != Gp[9, 11] or popcnt64(x9 & gx11) != KW0[9, 11]:
                                                        continue
                                                    if popcnt64(x10 & x11) != Gp[10, 11] or popcnt64(x10 & gx11) != KW0[10, 11]:
                                                        continue
                                                    if ((col_u2_B12 | (x8 & x9) | (x8 & x10) | (x8 & x11) | (x9 & x10) | (x9 & x11) | (x10 & x11)) == np.uint64((1 << 60) - 1)):
                                                        local_b3 += 1
        b1_sols_arr[r_idx] = local_b1
        b2_sols_arr[r_idx] = local_b2
        b3_sols_arr[r_idx] = local_b3
    return b1_sols_arr, b2_sols_arr, b3_sols_arr

def comp_priority(M, E, KW0, comp):
    # Priority: Class B (KW0[0,2]==2, diag=2) -> 0; Class A (KW0[0,2]==1, diag=2) -> 1; Class C (diag=0) -> 2
    sub_kw = KW0[np.ix_(comp, comp)]
    if sub_kw[0, 0] == 0:
        return 2
    # Check if off-diagonal of KW0 has 2s
    if np.sum(sub_kw == 2) == 8:
        return 0
    return 1

def main():
    t_start = time.time()
    # Order orbits by fastest expected first
    orbit_order = [6, 3, 7, 1, 4, 0, 2, 8, 5, 9]
    results = []
    total_unsat = 0
    
    for run_i, orb_idx in enumerate(orbit_order):
        M_orig, E_orig, Gp_orig, KW0_orig, comps_orig = tk2.orbits_222[orb_idx]
        # Reorder blocks so that comps are sorted by comp_priority (Class B < Class A < Class C)
        comps_sorted = sorted(comps_orig, key=lambda c: comp_priority(M_orig, E_orig, KW0_orig, c))
        perm = [u for c in comps_sorted for u in c]
        M = M_orig[np.ix_(perm, perm)]
        E = E_orig[np.ix_(perm, perm)]
        Gp = Gp_orig[np.ix_(perm, perm)]
        KW0 = KW0_orig[np.ix_(perm, perm)]
        comps = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
        ctypes = [comp_priority(M, E, KW0, c) for c in comps]
        cname_map = {0: "B", 1: "A", 2: "C"}
        csig = "+".join(cname_map[ct] for ct in ctypes)
        
        Delta0 = 2 * tk2.J12 - tk2.I12 - tk2.F12 - M - E @ tk2.F12
        L = []
        for c_idx, comp in enumerate(comps):
            I_B = tuple(comp)
            for i in comp:
                L.append(gen_2block_rows_cached(I_B, tuple(int(Delta0[i, j]) for j in range(12)), int(KW0[i, i])))
                
        B1_set = set(comps[0])
        B2_set = set(comps[1])
        B3_set = set(comps[2])
        O33_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in B3_set and v in B3_set))
        O13_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in B1_set and v in B3_set) or (u in B3_set and v in B1_set)))
        O23_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in B2_set and v in B3_set) or (u in B3_set and v in B2_set)))
        
        # Full Stab_B6(M, E) cosets mapping row a in {0..7} to row 0!
        # Wait: to be 100% sound for BOTH (B1, B2) and (B1, B2, B3), we use all g_p in Stab_B6(M, E)
        # that preserve B1 u B2 = {0..7} setwise (so B3 is also preserved setwise)!
        B12_set = B1_set | B2_set
        stab_a_to_0 = [[] for _ in range(8)]
        for g_p in tk2.b6_perms:
            ok = True
            for u in range(12):
                for v in range(12):
                    if M[u, v] != M[g_p[u], g_p[v]] or E[u, v] != E[g_p[u], g_p[v]]:
                        ok = False
                        break
                if not ok:
                    break
            if ok and set(g_p[u] for u in B12_set) == B12_set:
                for a in range(8):
                    if g_p[a] == 0:
                        c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                        stab_a_to_0[a].append(np.array(c_map, dtype=np.int32))
        stab_a_to_0 = [np.array(x, dtype=np.int32) if len(x) > 0 else np.empty((0, 60), dtype=np.int32) for x in stab_a_to_0]
        
        c_cans = [compute_canonical_masks(L[a], stab_a_to_0[a]) for a in range(8)]
        reps = np.array([i for i in range(len(L[0])) if L[0][i, 0] == c_cans[0][i]], dtype=np.int32)
        rep_canons = np.array([c_cans[0][i] for i in reps], dtype=np.uint64)
        
        Gp_off = (Gp - 2 * np.eye(12, dtype=int)).astype(np.int32)
        KW0_int = KW0.astype(np.int32)
        
        if run_i == 0:
            # JIT warmup
            solve_222_full_12row(
                reps[:1], rep_canons[:1],
                L[0], L[1], L[2], L[3], L[4], L[5], L[6], L[7], L[8], L[9], L[10], L[11],
                c_cans[1], c_cans[2], c_cans[3], c_cans[4], c_cans[5], c_cans[6], c_cans[7],
                Gp_off, KW0_int, O33_mask, O13_mask, O23_mask
            )
            
        t_orb = time.time()
        b1_s, b2_s, b3_s = solve_222_full_12row(
            reps, rep_canons,
            L[0], L[1], L[2], L[3], L[4], L[5], L[6], L[7], L[8], L[9], L[10], L[11],
            c_cans[1], c_cans[2], c_cans[3], c_cans[4], c_cans[5], c_cans[6], c_cans[7],
            Gp_off, KW0_int, O33_mask, O13_mask, O23_mask
        )
        dt = time.time() - t_orb
        nb1 = int(np.sum(b1_s))
        nb2 = int(np.sum(b2_s))
        nb3 = int(np.sum(b3_s))
        if nb3 == 0:
            total_unsat += 1
        rec = {
            "orbit_idx": orb_idx,
            "component_classes": csig,
            "r0_pool_size": len(L[0]),
            "r0_canonical_reps": len(reps),
            "b1_4row_sols": nb1,
            "b12_8row_sols": nb2,
            "b123_12row_sols": nb3,
            "time_s": round(dt, 4),
        }
        results.append(rec)
        print(
            f"[{run_i+1:2d}/10] Orbit {orb_idx} ({csig}): reps={len(reps):4d}, "
            f"b1_sols={nb1:8d}, b12_sols={nb2:6d}, b123_sols={nb3} in {dt:.2f}s "
            f"(elapsed={time.time()-t_start:.2f}s)",
            flush=True,
        )
        
    results_sorted = sorted(results, key=lambda x: x["orbit_idx"])
    summary = {
        "stratum": "dim ker(G_36) = 4, k_type1(S_0) = 0, component_signature = 2+2+2",
        "orbits_total": 10,
        "unsat_certified": total_unsat,
        "sat_found": 10 - total_unsat,
        "total_b1_4row_sols": sum(x["b1_4row_sols"] for x in results_sorted),
        "total_b12_8row_sols": sum(x["b12_8row_sols"] for x in results_sorted),
        "total_b123_12row_sols": sum(x["b123_12row_sols"] for x in results_sorted),
        "total_wall_time_s": round(time.time() - t_start, 2),
        "per_orbit": results_sorted,
    }
    out_p = "/Users/blister/.gemini/antigravity/brain/f9b47d7b-99a3-46e5-bb06-bc765b9911fb/scratch/null4_k0_222_10_summary.json"
    with open(out_p, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"DONE: Certified {total_unsat}/10 orbits of 2+2+2 UNSAT in {time.time()-t_start:.2f}s!", flush=True)

if __name__ == "__main__":
    main()
