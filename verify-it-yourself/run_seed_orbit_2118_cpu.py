import time
import json
import numpy as np
from numba import njit, prange
from itertools import permutations, product

t_start = time.time()
with open("/Users/blister/.gemini/antigravity/brain/a032f282-8f89-4af4-b78c-396ebf6f53dc/scratch/build_we_star_ladder_plan.py") as f:
    bsrc = f.read()
exec(bsrc.split("def canonicalize_cone6_all20")[0])

MASK60 = np.uint64((1 << 60) - 1)

@njit
def popcnt64(x):
    x = x - ((x >> np.uint64(1)) & np.uint64(0x5555555555555555))
    x = (x & np.uint64(0x3333333333333333)) + ((x >> np.uint64(2)) & np.uint64(0x3333333333333333))
    x = (x + (x >> np.uint64(4))) & np.uint64(0x0f0f0f0f0f0f0f0f)
    return int((x * np.uint64(0x0101010101010101)) >> np.uint64(56))

@njit
def eq_bits(x, target):
    if target == 0:
        return x == np.uint64(0)
    elif target == 1:
        return x != np.uint64(0) and (x & (x - np.uint64(1))) == np.uint64(0)
    elif target == 2:
        if x == np.uint64(0):
            return False
        y = x & (x - np.uint64(1))
        return y != np.uint64(0) and (y & (y - np.uint64(1))) == np.uint64(0)
    return popcnt64(x) == target

@njit
def bt_numba(v_idx, chosen_len, rem_deg, chosen, adj_len, adj_c, adj_w, g_col, req_pairs, out, out_cnt):
    if v_idx == 12:
        if chosen_len == 10:
            xm = np.uint64(0)
            for i in range(10):
                xm |= (np.uint64(1) << np.uint64(chosen[i]))
            npairs = 0
            for i in range(10):
                c = chosen[i]
                gc = g_col[c]
                if c < gc and ((xm >> np.uint64(gc)) & np.uint64(1)):
                    npairs += 1
            if npairs == req_pairs:
                gxm = np.uint64(0)
                for i in range(10):
                    gxm |= (np.uint64(1) << np.uint64(g_col[chosen[i]]))
                idx = out_cnt[0]
                out[idx, 0] = xm
                out[idx, 1] = gxm
                out_cnt[0] = idx + 1
        return
    need = rem_deg[v_idx]
    if need < 0:
        return
    avail_c = np.empty(60, dtype=np.int32)
    avail_w = np.empty(60, dtype=np.int32)
    n_avail = 0
    for i in range(adj_len[v_idx]):
        c = adj_c[v_idx, i]
        w = adj_w[v_idx, i]
        if rem_deg[w] > 0:
            avail_c[n_avail] = c
            avail_w[n_avail] = w
            n_avail += 1
    if n_avail < need:
        return
    if need == 0:
        bt_numba(v_idx + 1, chosen_len, rem_deg, chosen, adj_len, adj_c, adj_w, g_col, req_pairs, out, out_cnt)
    elif need == 1:
        rem_deg[v_idx] = 0
        for i in range(n_avail):
            c = avail_c[i]
            w = avail_w[i]
            rem_deg[w] -= 1
            chosen[chosen_len] = c
            bt_numba(v_idx + 1, chosen_len + 1, rem_deg, chosen, adj_len, adj_c, adj_w, g_col, req_pairs, out, out_cnt)
            rem_deg[w] += 1
        rem_deg[v_idx] = 1
    elif need == 2:
        rem_deg[v_idx] = 0
        for i in range(n_avail):
            c1 = avail_c[i]
            w1 = avail_w[i]
            rem_deg[w1] -= 1
            chosen[chosen_len] = c1
            for j in range(i + 1, n_avail):
                c2 = avail_c[j]
                w2 = avail_w[j]
                if rem_deg[w2] > 0:
                    rem_deg[w2] -= 1
                    chosen[chosen_len + 1] = c2
                    bt_numba(v_idx + 1, chosen_len + 2, rem_deg, chosen, adj_len, adj_c, adj_w, g_col, req_pairs, out, out_cnt)
                    rem_deg[w2] += 1
            rem_deg[w1] += 1
        rem_deg[v_idx] = 2

@njit
def make_luts_numba(c_maps):
    n_p = len(c_maps)
    luts = np.zeros((n_p, 8, 256), dtype=np.uint64)
    for p_idx in range(n_p):
        for byte_idx in range(8):
            for val in range(256):
                mask = np.uint64(0)
                for bit in range(8):
                    c = byte_idx * 8 + bit
                    if c < 60 and ((val >> bit) & 1):
                        mask |= (np.uint64(1) << np.uint64(c_maps[p_idx, c]))
                luts[p_idx, byte_idx, val] = mask
    return luts

@njit(parallel=True)
def compute_canons_luts(L_pool, luts):
    n = len(L_pool)
    n_p = len(luts)
    out = np.empty(n, dtype=np.uint64)
    for i in prange(n):
        xm = L_pool[i, 0]
        best = xm
        b0 = xm & np.uint64(0xFF)
        b1 = (xm >> np.uint64(8)) & np.uint64(0xFF)
        b2 = (xm >> np.uint64(16)) & np.uint64(0xFF)
        b3 = (xm >> np.uint64(24)) & np.uint64(0xFF)
        b4 = (xm >> np.uint64(32)) & np.uint64(0xFF)
        b5 = (xm >> np.uint64(40)) & np.uint64(0xFF)
        b6 = (xm >> np.uint64(48)) & np.uint64(0xFF)
        b7 = (xm >> np.uint64(56)) & np.uint64(0xFF)
        for p in range(n_p):
            img = (luts[p, 0, b0] | luts[p, 1, b1] | luts[p, 2, b2] | luts[p, 3, b3] |
                   luts[p, 4, b4] | luts[p, 5, b5] | luts[p, 6, b6] | luts[p, 7, b7])
            if img < best:
                best = img
        out[i] = best
    return out

cols_60 = []
col_idx = {}
for b1 in range(6):
    for b2 in range(b1 + 1, 6):
        for s1 in (0, 1):
            for s2 in (0, 1):
                j1, j2 = 2 * b1 + s1, 2 * b2 + s2
                c = len(cols_60)
                cols_60.append((j1, j2))
                col_idx[(j1, j2)] = c
                col_idx[(j2, j1)] = c
g_col = np.array([col_idx[(j1 ^ 1, j2 ^ 1)] for (j1, j2) in cols_60], dtype=np.int32)
cols_u = np.array([u for u, v in cols_60], dtype=np.int32)
cols_v = np.array([v for u, v in cols_60], dtype=np.int32)

adj_len = np.zeros(12, dtype=np.int32)
adj_c = np.zeros((12, 60), dtype=np.int32)
adj_w = np.zeros((12, 60), dtype=np.int32)
for c in range(60):
    u, v = cols_u[c], cols_v[c]
    adj_c[u, adj_len[u]] = c; adj_w[u, adj_len[u]] = v; adj_len[u] += 1
    adj_c[v, adj_len[v]] = c; adj_w[v, adj_len[v]] = u; adj_len[v] += 1

pool_list = []
pool_key_to_id = {}
def get_pool_id(deg_tup):
    if deg_tup not in pool_key_to_id:
        pid = len(pool_list)
        pool_key_to_id[deg_tup] = pid
        t_deg = np.array(deg_tup, dtype=np.int32)
        out = np.empty((200000, 2), dtype=np.uint64)
        out_cnt = np.zeros(1, dtype=np.int32)
        bt_numba(0, 0, t_deg.copy(), np.zeros(12, dtype=np.int32), adj_len, adj_c, adj_w, g_col, 0, out, out_cnt)
        pool_list.append(out[:int(out_cnt[0])].copy())
    return pool_key_to_id[deg_tup]

M0, E0, Gp0, KW0 = orbits_6[2118]
D0 = 2 * J12 - I12 - F12 - M0 - (E0 @ F12)
Gp = Gp0 - 2 * I12
ro = [0, 2, 5, 8, 7, 10, 1, 4, 3, 6, 9, 11]
D_ro  = D0[ro, :]
KW_ro = KW0[np.ix_(ro, ro)]
Gp_ro = Gp[np.ix_(ro, ro)]
dom_blocks = [(0, 1), (2, 4), (3, 5)]

# Notice: If we use the 384-element group aut_384 that preserves ALL 12 ROWS of Seed Orbit 2118 simultaneously:
# wait — what if we also include the 8 row flips inside the 3 trunk dominoes (which just swap the corresponding
# tail rows inside the 3 tail dominoes!) and the 8 block swaps (which produce only 8 tail variants total!)?
#Wait: Look at why D_ro[6:, :] only had 8 r6 groups under the full 24,576 group:
# Because any row permutation pi_6 in Z_2^3 x S_3 (order 48) paired with the natural block permutation
# (b_swap = f_dom) preserves the FULL 12x12 matrices (D_ro, KW_ro, Gp_ro) up to permuting the 3 tail dominoes!
# Let us verify how many elements of Aut_dec(K_6) preserve the FULL 12x12 matrices up to permuting/flipping the 3 tail dominoes!
# Earlier we tested that and found 6 * 64 = 384 elements preserve the tail, giving 64 coset tails (8 r6 -> 16 r7 -> 64 members).
# And across all 64 coset tails, how many distinct tail row pools exist?!
aut_dec_full = []
for p_dom in permutations(range(3)):
    for f_dom in product((0, 1), repeat=3):
        pi_6 = [2 * p_dom[d] + (s ^ f_dom[d]) for d in range(3) for s in (0, 1)]
        for b_swap in product((0, 1), repeat=3):
            b_perm = [0]*6
            for d_i in range(3):
                sb0, sb1 = dom_blocks[d_i]
                db0, db1 = dom_blocks[p_dom[d_i]]
                b_perm[sb0], b_perm[sb1] = (db0, db1) if b_swap[d_i] == 0 else (db1, db0)
            for c_flips in product((0, 1), repeat=6):
                g_p = [2*b_perm[b] + (s ^ c_flips[b]) for b in range(6) for s in (0, 1)]
                aut_dec_full.append((pi_6, g_p))

stab_a_to_0 = [[] for _ in range(6)]
seen_c = [set() for _ in range(6)]
for pi_6, g_p in aut_dec_full:
    for a_idx in range(6):
        if pi_6[a_idx] == 0 and tuple(g_p) not in seen_c[a_idx]:
            seen_c[a_idx].add(tuple(g_p))
            stab_a_to_0[a_idx].append([col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60])

cone_pids = [get_pool_id(tuple(int(x) for x in D_ro[r])) for r in range(6)]
c0_can = compute_canons_luts(pool_list[cone_pids[0]], make_luts_numba(np.array(stab_a_to_0[0], dtype=np.int32)))
c2_can = compute_canons_luts(pool_list[cone_pids[2]], make_luts_numba(np.array(stab_a_to_0[2], dtype=np.int32)))
c4_can = compute_canons_luts(pool_list[cone_pids[4]], make_luts_numba(np.array(stab_a_to_0[4], dtype=np.int32)))
reps = np.array([i for i in range(len(pool_list[0])) if pool_list[0][i, 0] == c0_can[i]], dtype=np.int32)

coset_tails = {}
for p_dom in permutations(range(3)):
    for f_dom in product((0, 1), repeat=3):
        pi_6 = [2 * p_dom[d] + (s ^ f_dom[d]) for d in range(3) for s in (0, 1)]
        for b_swap in product((0, 1), repeat=3):
            b_perm = [0]*6
            for d_i in range(3):
                sb0, sb1 = dom_blocks[d_i]
                db0, db1 = dom_blocks[p_dom[d_i]]
                b_perm[sb0], b_perm[sb1] = (db0, db1) if b_swap[d_i] == 0 else (db1, db0)
            g_p = [2*b_perm[b//2] + (b%2) for b in range(12)]
            best_tail_key = None
            for p_t in permutations(range(3)):
                for f_t in product((0, 1), repeat=3):
                    pi_t = [6 + 2 * p_t[d] + (s ^ f_t[d]) for d in range(3) for s in (0, 1)]
                    pi_12 = pi_6 + pi_t
                    D_m  = D_ro[np.ix_(pi_12, g_p)]
                    KW_m = KW_ro[np.ix_(pi_12, pi_12)]
                    Gp_m = Gp_ro[np.ix_(pi_12, pi_12)]
                    tkey = (tuple(map(tuple, D_m.tolist())), tuple(map(tuple, KW_m.tolist())), tuple(map(tuple, Gp_m.tolist())))
                    if best_tail_key is None or tkey < best_tail_key:
                        best_tail_key = tkey
            coset_tails[best_tail_key] = True

# Build R0Spec table: every tail row is characterized at depth 0..3 by (pool_id, kw0..kw3) (since gp0..gp5 == 1 always!)
r3_specs = []
r3_key_to_id = {}
def get_r3_spec_id(pid, kw_0_3):
    k = (int(pid), tuple(int(x) for x in kw_0_3))
    if k not in r3_key_to_id:
        r3_key_to_id[k] = len(r3_specs)
        r3_specs.append((int(pid), int(kw_0_3[0]), int(kw_0_3[1]), int(kw_0_3[2]), int(kw_0_3[3])))
    return r3_key_to_id[k]

r6_map = {}
for D_m, KW_m, Gp_m in sorted(coset_tails.keys()):
    k6 = (D_m[6], KW_m[6][:6], Gp_m[6][:6])
    k7 = (D_m[7], KW_m[7][:7], Gp_m[7][:7])
    k_tail = (D_m[8:], tuple(KW_m[r][:12] for r in range(8, 12)), tuple(Gp_m[r][:12] for r in range(8, 12)))
    r6_map.setdefault(k6, {}).setdefault(k7, []).append(k_tail)

r6_s3_id = []
r6_kw45  = []
r6_g7_range = []

r7_s3_id = []
r7_kw46  = []
r7_mem_range = []

mem_s3_ids = []
mem_kw   = []
mem_gp   = []

for k6, g7_dict in r6_map.items():
    deg6, kw6, gp6 = k6
    pid6 = get_pool_id(deg6)
    r6_s3_id.append(get_r3_spec_id(pid6, kw6[:4]))
    r6_kw45.append((kw6[4], kw6[5]))
    g7_s = len(r7_s3_id)
    for k7, m_list in g7_dict.items():
        deg7, kw7, gp7 = k7
        pid7 = get_pool_id(deg7)
        r7_s3_id.append(get_r3_spec_id(pid7, kw7[:4]))
        r7_kw46.append((kw7[4], kw7[5], kw7[6]))
    r6_g7_range.append((g7_s, len(r7_s3_id)))

n_s67 = len(r3_specs)

for k6, g7_dict in r6_map.items():
    for k7, m_list in g7_dict.items():
        ms = len(mem_s3_ids)
        for degs_8_11, kws_8_11, gps_8_11 in m_list:
            s3s = [get_r3_spec_id(get_pool_id(degs_8_11[off]), kws_8_11[off][:4]) for off in range(4)]
            mem_s3_ids.append(s3s)
            mem_kw.append(kws_8_11)
            mem_gp.append(gps_8_11)
        r7_mem_range.append((ms, len(mem_s3_ids)))

print(f"Prepared {len(pool_list)} pools, {n_s67} r6/r7 specs ({len(r3_specs)} total R3-specs), {len(reps)} reps in {time.time()-t_start:.2f}s!", flush=True)

pool_offsets = np.zeros(len(pool_list) + 1, dtype=np.int32)
for idx, p in enumerate(pool_list):
    pool_offsets[idx + 1] = pool_offsets[idx] + len(p)
all_pools = np.vstack(pool_list)

r3_specs_arr = np.array(r3_specs, dtype=np.int32)
r6_s3_arr    = np.array(r6_s3_id, dtype=np.int32)
r6_kw45_arr  = np.array(r6_kw45, dtype=np.int32)
r6_g7_arr    = np.array(r6_g7_range, dtype=np.int32)

r7_s3_arr    = np.array(r7_s3_id, dtype=np.int32)
r7_kw46_arr  = np.array(r7_kw46, dtype=np.int32)
r7_mem_arr   = np.array(r7_mem_range, dtype=np.int32)

mem_s3_arr   = np.array(mem_s3_ids, dtype=np.int32)
mem_kw_arr   = np.array(mem_kw, dtype=np.int32)
mem_gp_arr   = np.array(mem_gp, dtype=np.int32)

@njit(parallel=True)
def solve_all_reps_2118_fast(
    reps, all_pools, pool_offsets,
    cone_pids, c0_can, c2_can, c4_can,
    r3_specs_arr, n_s67,
    r6_s3_arr, r6_kw45_arr, r6_g7_arr,
    r7_s3_arr, r7_kw46_arr, r7_mem_arr,
    mem_s3_arr, mem_kw_arr, mem_gp_arr
):
    n_reps = len(reps)
    d4_counts = np.zeros(n_reps, dtype=np.int64)
    d6_counts = np.zeros(n_reps, dtype=np.int64)
    d8_counts = np.zeros(n_reps, dtype=np.int64)
    d10_counts = np.zeros(n_reps, dtype=np.int64)
    d11_counts = np.zeros(n_reps, dtype=np.int64)
    sol_counts = np.zeros(n_reps, dtype=np.int64)

    p0_s, p0_e = pool_offsets[cone_pids[0]], pool_offsets[cone_pids[0] + 1]
    p2_s, p2_e = pool_offsets[cone_pids[2]], pool_offsets[cone_pids[2] + 1]
    p4_s, p4_e = pool_offsets[cone_pids[4]], pool_offsets[cone_pids[4] + 1]

    for r_i in prange(n_reps):
        i0 = reps[r_i]
        min_can = c0_can[i0]
        x0 = all_pools[p0_s + i0, 0]
        gx0 = all_pools[p0_s + i0, 1]

        X1 = np.empty((4096, 2), dtype=np.uint64); n1 = 0
        for i in range(p0_s, p0_e):
            if c0_can[i - p0_s] < min_can:
                continue
            rx = all_pools[i, 0]; rgx = all_pools[i, 1]
            if (x0 & rx) == np.uint64(0) and eq_bits(x0 & rgx, 1):
                X1[n1, 0] = rx; X1[n1, 1] = rgx; n1 += 1
        if n1 == 0:
            continue

        X2_0 = np.empty((16384, 3), dtype=np.uint64); n2_0 = 0
        for i in range(p2_s, p2_e):
            c2v = c2_can[i - p2_s]
            if c2v < min_can:
                continue
            rx = all_pools[i, 0]; rgx = all_pools[i, 1]
            if eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, 2):
                X2_0[n2_0, 0] = rx; X2_0[n2_0, 1] = rgx; X2_0[n2_0, 2] = c2v; n2_0 += 1
        if n2_0 == 0:
            continue

        X4_0 = np.empty((16384, 3), dtype=np.uint64); n4_0 = 0
        for i in range(p4_s, p4_e):
            c4v = c4_can[i - p4_s]
            if c4v < min_can:
                continue
            rx = all_pools[i, 0]; rgx = all_pools[i, 1]
            if eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, 2):
                X4_0[n4_0, 0] = rx; X4_0[n4_0, 1] = rgx; X4_0[n4_0, 2] = c4v; n4_0 += 1
        if n4_0 == 0:
            continue

        S_d0 = np.empty((n_s67, 16384, 2), dtype=np.uint64)
        n_d0 = np.zeros(n_s67, dtype=np.int32)
        for s_i in range(n_s67):
            pid = r3_specs_arr[s_i, 0]; kw0_t = r3_specs_arr[s_i, 1]
            ps, pe = pool_offsets[pid], pool_offsets[pid + 1]
            cnt_s = 0
            for i in range(ps, pe):
                rx = all_pools[i, 0]; rgx = all_pools[i, 1]
                if eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, kw0_t):
                    S_d0[s_i, cnt_s, 0] = rx; S_d0[s_i, cnt_s, 1] = rgx; cnt_s += 1
            n_d0[s_i] = cnt_s

        X2_1 = np.empty((4096, 3), dtype=np.uint64)
        X4_1 = np.empty((4096, 3), dtype=np.uint64)
        X3_2 = np.empty((1024, 2), dtype=np.uint64)
        X4_2 = np.empty((1024, 3), dtype=np.uint64)
        X4_3 = np.empty((512, 3), dtype=np.uint64)

        S_d1 = np.empty((n_s67, 2500, 2), dtype=np.uint64)
        n_d1 = np.zeros(n_s67, dtype=np.int32)
        S_d2 = np.empty((n_s67, 600, 2), dtype=np.uint64)
        n_d2 = np.zeros(n_s67, dtype=np.int32)
        S_d3 = np.empty((n_s67, 200, 2), dtype=np.uint64)
        n_d3 = np.zeros(n_s67, dtype=np.int32)
        S_d5 = np.empty((n_s67, 32, 2), dtype=np.uint64)
        S_d5_kw = np.empty((n_s67, 32, 2), dtype=np.int32)
        n_d5 = np.zeros(n_s67, dtype=np.int32)

        loc_d4 = np.int64(0)
        loc_d6 = np.int64(0)
        loc_d8 = np.int64(0)
        loc_d10 = np.int64(0)
        loc_d11 = np.int64(0)
        loc_sol = np.int64(0)

        for idx1 in range(n1):
            x1 = X1[idx1, 0]; gx1 = X1[idx1, 1]
            u1_1 = x0 | x1

            n2_1 = 0
            for i in range(n2_0):
                rx = X2_0[i, 0]; rgx = X2_0[i, 1]
                if eq_bits(x1 & rx, 1) and eq_bits(x1 & rgx, 2):
                    X2_1[n2_1, 0] = rx; X2_1[n2_1, 1] = rgx; X2_1[n2_1, 2] = X2_0[i, 2]; n2_1 += 1
            if n2_1 == 0:
                continue

            n4_1 = 0
            for i in range(n4_0):
                rx = X4_0[i, 0]; rgx = X4_0[i, 1]
                if eq_bits(x1 & rx, 1) and eq_bits(x1 & rgx, 2):
                    X4_1[n4_1, 0] = rx; X4_1[n4_1, 1] = rgx; X4_1[n4_1, 2] = X4_0[i, 2]; n4_1 += 1
            if n4_1 == 0:
                continue

            for s_i in range(n_s67):
                kw1_t = r3_specs_arr[s_i, 2]
                cnt_s = 0
                for i in range(n_d0[s_i]):
                    rx = S_d0[s_i, i, 0]; rgx = S_d0[s_i, i, 1]
                    if eq_bits(x1 & rx, 1) and eq_bits(x1 & rgx, kw1_t):
                        S_d1[s_i, cnt_s, 0] = rx; S_d1[s_i, cnt_s, 1] = rgx; cnt_s += 1
                n_d1[s_i] = cnt_s

            for idx2 in range(n2_1):
                x2 = X2_1[idx2, 0]; gx2 = X2_1[idx2, 1]; can2 = X2_1[idx2, 2]
                u2_2 = u1_1 & x2
                u1_2 = u1_1 | x2

                n3_2 = 0
                for i in range(n2_1):
                    c3v = X2_1[i, 2]
                    if c3v < can2 or (c3v == can2 and i <= idx2):
                        continue
                    rx = X2_1[i, 0]; rgx = X2_1[i, 1]
                    if (rx & u2_2) == np.uint64(0) and (x2 & rx) == np.uint64(0) and eq_bits(x2 & rgx, 1):
                        X3_2[n3_2, 0] = rx; X3_2[n3_2, 1] = rgx; n3_2 += 1
                if n3_2 == 0:
                    continue

                n4_2 = 0
                for i in range(n4_1):
                    c4v = X4_1[i, 2]
                    if c4v < can2:
                        continue
                    rx = X4_1[i, 0]; rgx = X4_1[i, 1]
                    if (rx & u2_2) == np.uint64(0) and eq_bits(x2 & rx, 1) and eq_bits(x2 & rgx, 2):
                        X4_2[n4_2, 0] = rx; X4_2[n4_2, 1] = rgx; X4_2[n4_2, 2] = c4v; n4_2 += 1
                if n4_2 < 2:
                    continue

                s2_ready = False

                for idx3 in range(n3_2):
                    x3 = X3_2[idx3, 0]; gx3 = X3_2[idx3, 1]
                    u2_3 = u2_2 | (u1_2 & x3)
                    u1_3 = u1_2 | x3
                    loc_d4 += 1

                    n4_3 = 0
                    for i in range(n4_2):
                        rx = X4_2[i, 0]; rgx = X4_2[i, 1]
                        if (rx & u2_3) == np.uint64(0) and eq_bits(x3 & rx, 1) and eq_bits(x3 & rgx, 2):
                            X4_3[n4_3, 0] = rx; X4_3[n4_3, 1] = rgx; X4_3[n4_3, 2] = X4_2[i, 2]; n4_3 += 1
                    if n4_3 < 2:
                        continue

                    s3_ready = False

                    for idx4 in range(n4_3):
                        x4 = X4_3[idx4, 0]; gx4 = X4_3[idx4, 1]; can4 = X4_3[idx4, 2]
                        u2_4 = u2_3 | (u1_3 & x4)
                        u1_4 = u1_3 | x4

                        for idx5 in range(n4_3):
                            c5v = X4_3[idx5, 2]
                            if c5v < can4 or (c5v == can4 and idx5 <= idx4):
                                continue
                            x5 = X4_3[idx5, 0]; gx5 = X4_3[idx5, 1]
                            if (x5 & u2_4) != np.uint64(0) or (x4 & x5) != np.uint64(0) or not eq_bits(x4 & gx5, 1):
                                continue
                            u2_5 = u2_4 | (u1_4 & x5)
                            u1_5 = u1_4 | x5
                            e12  = (~u1_5) & MASK60
                            loc_d6 += 1

                            if not s2_ready:
                                for s_i in range(n_s67):
                                    kw2_t = r3_specs_arr[s_i, 3]
                                    cnt_s = 0
                                    for i in range(n_d1[s_i]):
                                        rx = S_d1[s_i, i, 0]; rgx = S_d1[s_i, i, 1]
                                        if (rx & u2_2) == np.uint64(0) and eq_bits(x2 & rx, 1) and eq_bits(x2 & rgx, kw2_t):
                                            S_d2[s_i, cnt_s, 0] = rx; S_d2[s_i, cnt_s, 1] = rgx; cnt_s += 1
                                    n_d2[s_i] = cnt_s
                                s2_ready = True

                            if not s3_ready:
                                for s_i in range(n_s67):
                                    kw3_t = r3_specs_arr[s_i, 4]
                                    cnt_s = 0
                                    for i in range(n_d2[s_i]):
                                        rx = S_d2[s_i, i, 0]; rgx = S_d2[s_i, i, 1]
                                        if (rx & u2_3) == np.uint64(0) and eq_bits(x3 & rx, 1) and eq_bits(x3 & rgx, kw3_t):
                                            S_d3[s_i, cnt_s, 0] = rx; S_d3[s_i, cnt_s, 1] = rgx; cnt_s += 1
                                    n_d3[s_i] = cnt_s
                                s3_ready = True

                            for s_i in range(n_s67):
                                cnt_5 = 0
                                for i in range(n_d3[s_i]):
                                    rx = S_d3[s_i, i, 0]
                                    if (rx & u2_5) == np.uint64(0) and popcnt64(rx & e12) == 4:
                                        if eq_bits(x4 & rx, 1) and eq_bits(x5 & rx, 1):
                                            rgx = S_d3[s_i, i, 1]
                                            S_d5[s_i, cnt_5, 0] = rx
                                            S_d5[s_i, cnt_5, 1] = rgx
                                            S_d5_kw[s_i, cnt_5, 0] = popcnt64(x4 & rgx)
                                            S_d5_kw[s_i, cnt_5, 1] = popcnt64(x5 & rgx)
                                            cnt_5 += 1
                                n_d5[s_i] = cnt_5

                            for g6_i in range(len(r6_s3_arr)):
                                s3_6 = r6_s3_arr[g6_i]
                                if n_d5[s3_6] == 0:
                                    continue
                                kw4_6, kw5_6 = r6_kw45_arr[g6_i, 0], r6_kw45_arr[g6_i, 1]
                                X6 = np.empty((32, 2), dtype=np.uint64); n6 = 0
                                for i in range(n_d5[s3_6]):
                                    if S_d5_kw[s3_6, i, 0] == kw4_6 and S_d5_kw[s3_6, i, 1] == kw5_6:
                                        X6[n6, 0] = S_d5[s3_6, i, 0]; X6[n6, 1] = S_d5[s3_6, i, 1]; n6 += 1
                                if n6 == 0:
                                    continue

                                g7_s, g7_e = r6_g7_arr[g6_i, 0], r6_g7_arr[g6_i, 1]
                                for g7_i in range(g7_s, g7_e):
                                    s3_7 = r7_s3_arr[g7_i]
                                    if n_d5[s3_7] == 0:
                                        continue
                                    kw4_7, kw5_7, kw6_7 = r7_kw46_arr[g7_i, 0], r7_kw46_arr[g7_i, 1], r7_kw46_arr[g7_i, 2]
                                    X7 = np.empty((32, 2), dtype=np.uint64); n7 = 0
                                    for i in range(n_d5[s3_7]):
                                        if S_d5_kw[s3_7, i, 0] == kw4_7 and S_d5_kw[s3_7, i, 1] == kw5_7:
                                            X7[n7, 0] = S_d5[s3_7, i, 0]; X7[n7, 1] = S_d5[s3_7, i, 1]; n7 += 1
                                    if n7 == 0:
                                        continue

                                    for idx6 in range(n6):
                                        x6 = X6[idx6, 0]; gx6 = X6[idx6, 1]
                                        u2_6 = u2_5 | (u1_5 & x6)
                                        u1_6 = u1_5 | x6

                                        for idx7 in range(n7):
                                            x7 = X7[idx7, 0]; gx7 = X7[idx7, 1]
                                            if (x7 & u2_6) != np.uint64(0) or (x6 & x7) != np.uint64(0) or not eq_bits(x6 & gx7, kw6_7):
                                                continue
                                            u2_7 = u2_6 | (u1_6 & x7)
                                            u1_7 = u1_6 | x7
                                            h3_hole = (~u1_7) & MASK60
                                            loc_d8 += 1

                                            ms, me = r7_mem_arr[g7_i, 0], r7_mem_arr[g7_i, 1]
                                            for m_i in range(ms, me):
                                                s3_8 = mem_s3_arr[m_i, 0]
                                                pid8 = r3_specs_arr[s3_8, 0]
                                                gp8 = mem_gp_arr[m_i, 0]; kw8 = mem_kw_arr[m_i, 0]
                                                X8 = np.empty((32, 2), dtype=np.uint64); n8 = 0
                                                for i in range(pool_offsets[pid8], pool_offsets[pid8 + 1]):
                                                    rx = all_pools[i, 0]; rgx = all_pools[i, 1]
                                                    if (rx & u2_7) == np.uint64(0) and popcnt64(rx & h3_hole) == 2:
                                                        if (eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, kw8[0]) and
                                                            eq_bits(x1 & rx, 1) and eq_bits(x1 & rgx, kw8[1]) and
                                                            eq_bits(x2 & rx, 1) and eq_bits(x2 & rgx, kw8[2]) and
                                                            eq_bits(x3 & rx, 1) and eq_bits(x3 & rgx, kw8[3]) and
                                                            eq_bits(x4 & rx, gp8[4]) and eq_bits(x4 & rgx, kw8[4]) and
                                                            eq_bits(x5 & rx, gp8[5]) and eq_bits(x5 & rgx, kw8[5]) and
                                                            eq_bits(x6 & rx, gp8[6]) and eq_bits(x6 & rgx, kw8[6]) and
                                                            eq_bits(x7 & rx, gp8[7]) and eq_bits(x7 & rgx, kw8[7])):
                                                            X8[n8, 0] = rx; X8[n8, 1] = rgx; n8 += 1
                                                if n8 == 0:
                                                    continue

                                                s3_9 = mem_s3_arr[m_i, 1]
                                                pid9 = r3_specs_arr[s3_9, 0]
                                                gp9 = mem_gp_arr[m_i, 1]; kw9 = mem_kw_arr[m_i, 1]
                                                X9 = np.empty((32, 2), dtype=np.uint64); n9 = 0
                                                for i in range(pool_offsets[pid9], pool_offsets[pid9 + 1]):
                                                    rx = all_pools[i, 0]; rgx = all_pools[i, 1]
                                                    if (rx & u2_7) == np.uint64(0) and popcnt64(rx & h3_hole) == 2:
                                                        if (eq_bits(x0 & rx, 1) and eq_bits(x0 & rgx, kw9[0]) and
                                                            eq_bits(x1 & rx, 1) and eq_bits(x1 & rgx, kw9[1]) and
                                                            eq_bits(x2 & rx, 1) and eq_bits(x2 & rgx, kw9[2]) and
                                                            eq_bits(x3 & rx, 1) and eq_bits(x3 & rgx, kw9[3]) and
                                                            eq_bits(x4 & rx, gp9[4]) and eq_bits(x4 & rgx, kw9[4]) and
                                                            eq_bits(x5 & rx, gp9[5]) and eq_bits(x5 & rgx, kw9[5]) and
                                                            eq_bits(x6 & rx, gp9[6]) and eq_bits(x6 & rgx, kw9[6]) and
                                                            eq_bits(x7 & rx, gp9[7]) and eq_bits(x7 & rgx, kw9[7])):
                                                            X9[n9, 0] = rx; X9[n9, 1] = rgx; n9 += 1
                                                if n9 == 0:
                                                    continue

                                                for idx8 in range(n8):
                                                    x8 = X8[idx8, 0]; gx8 = X8[idx8, 1]
                                                    u2_8 = u2_7 | (u1_7 & x8)
                                                    u1_8 = u1_7 | x8
                                                    for idx9 in range(n9):
                                                        x9 = X9[idx9, 0]; gx9 = X9[idx9, 1]
                                                        if (x9 & u2_8) != np.uint64(0) or (x8 & x9) != np.uint64(0) or not eq_bits(x8 & gx9, kw9[8]):
                                                            continue
                                                        u2_9 = u2_8 | (u1_8 & x9)
                                                        u1_9 = u1_8 | x9
                                                        if u1_9 != MASK60:
                                                            continue
                                                        loc_d10 += 1
                                                        s3_10 = mem_s3_arr[m_i, 2]
                                                        pid10 = r3_specs_arr[s3_10, 0]
                                                        gp10 = mem_gp_arr[m_i, 2]; kw10 = mem_kw_arr[m_i, 2]
                                                        s3_11 = mem_s3_arr[m_i, 3]
                                                        pid11 = r3_specs_arr[s3_11, 0]
                                                        gp11 = mem_gp_arr[m_i, 3]; kw11 = mem_kw_arr[m_i, 3]
                                                        for i in range(pool_offsets[pid10], pool_offsets[pid10 + 1]):
                                                            x10 = all_pools[i, 0]; gx10 = all_pools[i, 1]
                                                            if (x10 & u2_9) == np.uint64(0):
                                                                if (eq_bits(x0 & x10, 1) and eq_bits(x0 & gx10, kw10[0]) and
                                                                    eq_bits(x1 & x10, 1) and eq_bits(x1 & gx10, kw10[1]) and
                                                                    eq_bits(x2 & x10, 1) and eq_bits(x2 & gx10, kw10[2]) and
                                                                    eq_bits(x3 & x10, 1) and eq_bits(x3 & gx10, kw10[3]) and
                                                                    eq_bits(x4 & x10, gp10[4]) and eq_bits(x4 & gx10, kw10[4]) and
                                                                    eq_bits(x5 & x10, gp10[5]) and eq_bits(x5 & gx10, kw10[5]) and
                                                                    eq_bits(x6 & x10, gp10[6]) and eq_bits(x6 & gx10, kw10[6]) and
                                                                    eq_bits(x7 & x10, gp10[7]) and eq_bits(x7 & gx10, kw10[7]) and
                                                                    eq_bits(x8 & x10, gp10[8]) and eq_bits(x8 & gx10, kw10[8]) and
                                                                    eq_bits(x9 & x10, gp10[9]) and eq_bits(x9 & gx10, kw10[9])):
                                                                    loc_d11 += 1
                                                                    x11_req = ((~u2_9) & MASK60) ^ x10
                                                                    for j11 in range(pool_offsets[pid11], pool_offsets[pid11 + 1]):
                                                                        x11 = all_pools[j11, 0]; gx11 = all_pools[j11, 1]
                                                                        if x11 == x11_req:
                                                                            if (eq_bits(x0 & x11, 1) and eq_bits(x0 & gx11, kw11[0]) and
                                                                                eq_bits(x1 & x11, 1) and eq_bits(x1 & gx11, kw11[1]) and
                                                                                eq_bits(x2 & x11, 1) and eq_bits(x2 & gx11, kw11[2]) and
                                                                                eq_bits(x3 & x11, 1) and eq_bits(x3 & gx11, kw11[3]) and
                                                                                eq_bits(x4 & x11, gp11[4]) and eq_bits(x4 & gx11, kw11[4]) and
                                                                                eq_bits(x5 & x11, gp11[5]) and eq_bits(x5 & gx11, kw11[5]) and
                                                                                eq_bits(x6 & x11, gp11[6]) and eq_bits(x6 & gx11, kw11[6]) and
                                                                                eq_bits(x7 & x11, gp11[7]) and eq_bits(x7 & gx11, kw11[7]) and
                                                                                eq_bits(x8 & x11, gp11[8]) and eq_bits(x8 & gx11, kw11[8]) and
                                                                                eq_bits(x9 & x11, gp11[9]) and eq_bits(x9 & gx11, kw11[9]) and
                                                                                eq_bits(x10 & gx11, kw11[10])):
                                                                                loc_sol += 1

        d4_counts[r_i] = loc_d4
        d6_counts[r_i] = loc_d6
        d8_counts[r_i] = loc_d8
        d10_counts[r_i] = loc_d10
        d11_counts[r_i] = loc_d11
        sol_counts[r_i] = loc_sol
    return d4_counts, d6_counts, d8_counts, d10_counts, d11_counts, sol_counts

t_solve = time.time()
tot_d4 = tot_d6 = tot_d8 = tot_d10 = tot_d11 = tot_sol = 0
B_SZ = 8
for b_start in range(0, len(reps), B_SZ):
    tb = time.time()
    b_reps = reps[b_start:b_start + B_SZ]
    d4_c, d6_c, d8_c, d10_c, d11_c, sol_c = solve_all_reps_2118_fast(
        b_reps, all_pools, pool_offsets,
        np.array(cone_pids, dtype=np.int32), c0_can, c2_can, c4_can,
        r3_specs_arr, int(n_s67),
        r6_s3_arr, r6_kw45_arr, r6_g7_arr,
        r7_s3_arr, r7_kw46_arr, r7_mem_arr,
        mem_s3_arr, mem_kw_arr, mem_gp_arr
    )
    tot_d4  += int(d4_c.sum())
    tot_d6  += int(d6_c.sum())
    tot_d8  += int(d8_c.sum())
    tot_d10 += int(d10_c.sum())
    tot_d11 += int(d11_c.sum())
    tot_sol += int(sol_c.sum())
    print(f"  [Batch {b_start+len(b_reps):3d}/{len(reps)}] +{time.time()-tb:.2f}s (cum {time.time()-t_solve:.2f}s) | d4={tot_d4:,}, d6={tot_d6:,}, d8={tot_d8:,}, d10={tot_d10:,}, sols={tot_sol}", flush=True)

el = time.time() - t_solve
print(f"[SEED ORBIT 2118 CERTIFIED UNSAT] Done in {el:.2f}s (total {time.time()-t_start:.2f}s)!", flush=True)
print(f"  reps = {len(reps)}, d4 = {tot_d4}, d6 = {tot_d6}, d8 = {tot_d8}, d10 = {tot_d10}, d11 = {tot_d11}, sols = {tot_sol}", flush=True)
cert_out = {
    "orbit_idx": 2118,
    "seed_name": "Seed III (Self-Chiral M0 = E0 on C12)",
    "aut_dec_order": 24576,
    "coset_members": 64,
    "reps": int(len(reps)),
    "d4": tot_d4,
    "d6": tot_d6,
    "d8": tot_d8,
    "d10": tot_d10,
    "d11": tot_d11,
    "sols": tot_sol,
    "elapsed_s": round(el, 3)
}
with open("/Users/blister/.gemini/antigravity/brain/a032f282-8f89-4af4-b78c-396ebf6f53dc/scratch/seed_orbit_2118_cert.json", "w") as f:
    json.dump(cert_out, f, indent=2)
