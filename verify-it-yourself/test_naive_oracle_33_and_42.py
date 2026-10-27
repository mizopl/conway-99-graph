import time
import numpy as np
from itertools import permutations, product
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_all_10_nullity3_k0_33_cpu import (
    build_orbits, build_perm_luts, compute_canons_lut,
    naive_reference_check_33, fast_hierarchical_30orbit_solver
)
from run_all_168_nullity3_k0_42_cpu import naive_reference_check_42, solve_orbit_42_chiral_cpu

def main():
    t_start = time.time()
    F12, I12, J12, b6_perms, orbits_by_sig = build_orbits()

    cols_60 = []; col_idx = {}
    for b1 in range(6):
        for b2 in range(b1 + 1, 6):
            for s1 in (0, 1):
                for s2 in (0, 1):
                    j1, j2 = 2 * b1 + s1, 2 * b2 + s2
                    c = len(cols_60); cols_60.append((j1, j2)); col_idx[(j1, j2)] = col_idx[(j2, j1)] = c
    g_col = [col_idx[(j1 ^ 1, j2 ^ 1)] for (j1, j2) in cols_60]
    orbs_30 = [(c, g_col[c]) for c in range(60) if c < g_col[c]]

    print("=" * 100, flush=True)
    print("PART 1: 3+3 STRATUM CROSS-CHECK ORACLE (PURE PYTHON vs @njit KERNEL ACROSS ALL 10 CLASSES C_0..C_9)", flush=True)
    print("=" * 100, flush=True)

    orbits_33 = orbits_by_sig["kt1=0_3+3"]
    b3_perms_6 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(3)) for flips in product((0, 1), repeat=3)
    ]
    def canon_3block(M6, E6):
        return min(tuple(M6[np.ix_(p, p)].flatten()) + tuple(E6[np.ix_(p, p)].flatten()) for p in b3_perms_6)

    c3_classes = []; seen_c3 = set()
    for M, E, Gp, KW0, Delta0, comps in orbits_33:
        for comp in comps:
            M6, E6 = M[np.ix_(comp, comp)], E[np.ix_(comp, comp)]
            ck = canon_3block(M6, E6)
            if ck not in seen_c3:
                seen_c3.add(ck); c3_classes.append((M6, E6))

    I_B1_33 = {0, 1, 2, 3, 4, 5}
    O11_33 = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] in I_B1_33 and cols_60[c][1] in I_B1_33))
    O12_33 = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if (cols_60[c][0] in I_B1_33) ^ (cols_60[c][1] in I_B1_33)))
    O22_33 = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] not in I_B1_33 and cols_60[c][1] not in I_B1_33))
    C11_33 = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in I_B1_33 and v in I_B1_33))
    C12_33 = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in I_B1_33) ^ (v in I_B1_33)))
    C22_33 = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u not in I_B1_33 and v not in I_B1_33))

    from itertools import combinations
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
                            if cols_60[c][0] in I_B1_33 and cols_60[c][1] in I_B1_33: ok_p = False; break
                    if ok_p and npairs == req_pairs:
                        xm = gxm = o11_1 = o12_1 = o12_2 = o2_all = o22_1 = o22_2 = 0
                        for c in chosen: xm |= 1 << c; gxm |= 1 << g_col[c]
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if s == 2: o2_all |= 1 << idx_m
                            if (int(O11_33) >> idx_m) & 1:
                                if s == 1: o11_1 |= 1 << idx_m
                            elif (int(O12_33) >> idx_m) & 1:
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

    F6 = F12[:6, :6]; I6 = np.eye(6, dtype=int); J6 = np.ones((6, 6), dtype=int)

    for idx_c in range(10):
        M6, E6 = c3_classes[idx_c]
        KW6 = (2 * J6 - F6 - E6 - (M6 @ E6) - (E6 @ M6)).astype(np.int32)
        Delta6 = 2 * J6 - I6 - F6 - M6 - (E6 @ F6)
        Gp6 = (9 * I6 + J6 - M6 - 2 * I6).astype(np.int32)
        L_raw = [gen_3block_rows_cached(tuple(int(Delta6[i, j]) for j in range(6)) + (2, 2, 2, 2, 2, 2), int(KW6[i, i])) for i in range(6)]
        lens = [len(x) for x in L_raw]
        stab_m16 = [
            (pr, pc) for pr in permutations(range(6))
            if (KW6 == KW6[np.ix_(pr, pr)]).all() and (Gp6 == Gp6[np.ix_(pr, pr)]).all()
            for pc in b3_perms_6 if (Delta6 == Delta6[np.ix_(pr, pc)]).all()
        ]
        def w_pair(u, v):
            return (4 if Gp6[u, v] == 0 else (1 if Gp6[u, v] == 1 else 0)) + (4 if KW6[u, v] == 0 else (1 if KW6[u, v] == 1 else 0))
        best_ord = list(max(
            permutations(range(6)),
            key=lambda p: (
                -(lens[p[0]] // max(1, sum(1 for (pr, pc) in stab_m16 if pr[p[0]] == p[0]))),
                sum(w_pair(p[a], p[b]) for a in range(4) for b in range(a + 1, 4)),
                sum(w_pair(p[a], p[b]) for a in range(3) for b in range(a + 1, 3)),
                w_pair(p[0], p[1]),
                -lens[p[1]],
                -(Gp6[p[4], p[5]] + KW6[p[4], p[5]] + (KW6[p[4], p[4]] // 2) + (KW6[p[5], p[5]] // 2)),
                -sum(lens[p[a]] for a in range(4))
            )
        ))
        L = [L_raw[r] for r in best_ord]
        Gp_ord = np.ascontiguousarray(Gp6[np.ix_(best_ord, best_ord)], dtype=np.int32)
        KW_ord = np.ascontiguousarray(KW6[np.ix_(best_ord, best_ord)], dtype=np.int32)
        stab_a_to_0 = [[] for _ in range(6)]; seen_a_to_0 = [set() for _ in range(6)]
        g01_dict = {}; swap01_perms = []; seen_swap01 = set(); id_map = tuple(range(60))
        for p_row, p_col1 in stab_m16:
            for p2 in b3_perms_6:
                g_p = list(p_col1) + [6 + x for x in p2]
                c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                t_map = tuple(c_map)
                for a_idx, orig_r in enumerate(best_ord):
                    if p_row[orig_r] == best_ord[0] and t_map not in seen_a_to_0[a_idx]:
                        seen_a_to_0[a_idx].add(t_map); stab_a_to_0[a_idx].append(c_map)
                if p_row[best_ord[0]] == best_ord[0] and p_row[best_ord[1]] == best_ord[1] and t_map != id_map:
                    f2 = 1 if p_row[best_ord[2]] == best_ord[2] else 0
                    g01_dict[t_map] = max(g01_dict.get(t_map, 0), f2)
                if p_row[best_ord[0]] == best_ord[1] and p_row[best_ord[1]] == best_ord[0] and t_map not in seen_swap01:
                    seen_swap01.add(t_map); swap01_perms.append(c_map)
        g01_perms = [list(k) for k in g01_dict.keys()]
        g012_flags = [v for v in g01_dict.values()]
        c_cans = [compute_canons_lut(L[a], build_perm_luts(stab_a_to_0[a])) for a in range(6)]
        luts_g01 = build_perm_luts(g01_perms)
        is_g012_flag = np.ascontiguousarray(np.array(g012_flags, dtype=np.int32))
        luts_swap01 = build_perm_luts(swap01_perms)
        reps = np.ascontiguousarray([i for i in range(len(L[0])) if L[0][i, 0] == c_cans[0][i]], dtype=np.int32)
        rep_canons = np.ascontiguousarray([c_cans[0][i] for i in reps], dtype=np.uint64)

        t0 = time.time()
        or_idx = 0
        best_cost = 10**18
        for cand_idx in range(min(400, len(reps))):
            chk = fast_hierarchical_30orbit_solver(
                1, reps[cand_idx:cand_idx+1], rep_canons[cand_idx:cand_idx+1],
                L[0], L[1], c_cans[1], L[2], c_cans[2], L[3], c_cans[3], L[4], c_cans[4], L[5], c_cans[5],
                Gp_ord, KW_ord,
                C11_33, C12_33, C22_33, O11_33, O12_33, O22_33,
                luts_g01, is_g012_flag, luts_swap01
            )
            cost = int(chk[1]) + 40 * int(chk[2])
            if chk[2] > 0 and cost < best_cost:
                best_cost = cost
                or_idx = cand_idx
                if best_cost <= 15000:
                    break
        naive_c = naive_reference_check_33(
            int(reps[or_idx]), int(rep_canons[or_idx]),
            L[0], L[1], c_cans[1], L[2], c_cans[2], L[3], c_cans[3], L[4], c_cans[4], L[5], c_cans[5],
            Gp_ord, KW_ord,
            int(C11_33), int(C22_33), int(O11_33), int(O12_33), int(O22_33),
            g01_perms, g012_flags, swap01_perms
        )
        numba_c = tuple(int(v) for v in fast_hierarchical_30orbit_solver(
            1, reps[or_idx:or_idx+1], rep_canons[or_idx:or_idx+1],
            L[0], L[1], c_cans[1], L[2], c_cans[2], L[3], c_cans[3], L[4], c_cans[4], L[5], c_cans[5],
            Gp_ord, KW_ord,
            C11_33, C12_33, C22_33, O11_33, O12_33, O22_33,
            luts_g01, is_g012_flag, luts_swap01
        ))
        assert naive_c == numba_c, f"Mismatch on C_{idx_c}: {naive_c} != {numba_c}"
        print(f"  [3+3 C_{idx_c} rep_idx={or_idx:4d}] PASS: naive={naive_c} == numba={numba_c} ({time.time()-t0:.2f}s)", flush=True)

    print("\n" + "=" * 100, flush=True)
    print("PART 2: 4+2 STRATUM CROSS-CHECK ORACLE (PURE PYTHON vs @njit KERNEL ON ORBIT 0 & HARDEST ORBIT 162)", flush=True)
    print("=" * 100, flush=True)

    orbits_42 = orbits_by_sig["kt1=0_4+2"]
    b2_perms_4 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(2)) for flips in product((0, 1), repeat=2)
    ]
    b4_perms_8 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(4)) for flips in product((0, 1), repeat=4)
    ]
    I_B1_42 = {0, 1, 2, 3, 4, 5, 6, 7}
    O11_42 = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] in I_B1_42 and cols_60[c][1] in I_B1_42))
    O12_42 = np.uint64(sum(1 << m for m, (c, gc) in enumerate(orbs_30) if (cols_60[c][0] in I_B1_42) ^ (cols_60[c][1] in I_B1_42)))
    C11_42 = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in I_B1_42 and v in I_B1_42))

    y_cache = {}
    def gen_2block_rows(target_deg_4, diag_kw):
        key = (target_deg_4, diag_kw)
        if key in y_cache: return y_cache[key]
        target_deg_12 = (2, 2, 2, 2, 2, 2, 2, 2) + tuple(target_deg_4)
        req_pairs = diag_kw // 2
        ok_cols = [c for c in range(60) if target_deg_12[cols_60[c][0]] > 0 and target_deg_12[cols_60[c][1]] > 0 and not (cols_60[c][0] not in I_B1_42 and cols_60[c][1] not in I_B1_42)]
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
                        for c in chosen: xm |= 1 << c; gxm |= 1 << g_col[c]
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if s == 2: o2_all |= 1 << idx_m
                            if (int(O11_42) >> idx_m) & 1:
                                if s == 1: o11_1 |= 1 << idx_m
                                elif s == 2: o11_2 |= 1 << idx_m
                            elif (int(O12_42) >> idx_m) & 1:
                                if s == 1: o12_1 |= 1 << idx_m
                                elif s == 2: o12_2 |= 1 << idx_m
                        if o12_2 == 0: res.append((xm, gxm, o11_1, o11_2, o12_1, o2_all))
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
                        for c in chosen: xm |= 1 << c; gxm |= 1 << g_col[c]
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if s == 2: o2_all |= 1 << idx_m
                            if (int(O11_42) >> idx_m) & 1:
                                if s == 1: o11_1 |= 1 << idx_m
                                elif s == 2: o11_2 |= 1 << idx_m
                            elif (int(O12_42) >> idx_m) & 1:
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
    id_map = tuple(range(60))

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

        stab2_m16 = [
            (pr, pc) for pr in permutations(range(4))
            if all(ylens[pr[a]] == ylens[a] for a in range(4)) and (Gp4_2 == Gp4_2[np.ix_(pr, pr)]).all() and (KW4 == KW4[np.ix_(pr, pr)]).all()
            for pc in b2_perms_4 if (D4 == D4[np.ix_(pr, pc)]).all()
        ]
        def w2(u, v):
            return (4 if Gp4_2[u, v] == 0 else (1 if Gp4_2[u, v] == 1 else 0)) + (4 if KW4[u, v] == 0 else (1 if KW4[u, v] == 1 else 0))
        ord2 = list(max(permutations(range(4)), key=lambda q: (w2(q[0], q[1]) + w2(q[0], q[2]) + w2(q[1], q[2]), w2(q[0], q[1]), -ylens[q[0]])))

        def w4(u, v):
            return (4 if Gp8_4[u, v] == 0 else (1 if Gp8_4[u, v] == 1 else 0)) + (4 if KW8[u, v] == 0 else (1 if KW8[u, v] == 1 else 0))
        def get_stab4_sub(q):
            q = list(q); gp4 = Gp8_4[np.ix_(q, q)]; kw4 = KW8[np.ix_(q, q)]; d48 = D8[q, :]
            return [
                (pr, pc) for pr in permutations(range(4))
                if all(xlens[q[pr[a]]] == xlens[q[a]] for a in range(4)) and (gp4 == gp4[np.ix_(pr, pr)]).all() and (kw4 == kw4[np.ix_(pr, pr)]).all()
                for pc in b4_perms_8 if (d48 == d48[np.ix_(pr, pc)]).all()
            ]
        best_4 = max(
            combinations(range(8), 4),
            key=lambda q: (
                sum(1 for r in q if xlens[r] < 200000),
                int(np.log2(max(1, len(get_stab4_sub(q))))) * 4 + sum(w4(q[a], q[b]) for a in range(4) for b in range(a + 1, 4)),
                len(get_stab4_sub(q))
            )
        )
        stab4_sub = get_stab4_sub(best_4)
        ord4_sub = max(permutations(best_4), key=lambda q: (w4(q[0], q[1]) + w4(q[0], q[2]) + w4(q[1], q[2]), w4(q[0], q[1]), -xlens[q[0]], -xlens[q[1]]))
        rem_4 = [r for r in range(8) if r not in ord4_sub]
        ord4 = list(ord4_sub) + rem_4
        idx_map_4 = [list(best_4).index(r) for r in ord4_sub]
        stab4_m16 = [(tuple(idx_map_4[pr[idx_map_4.index(a)]] for a in range(4)), pc) for (pr, pc) in stab4_sub]

        Y = [Y_raw[r] for r in ord2]; X = [X_raw[r] for r in ord4]
        Gp2_ord = np.ascontiguousarray(Gp4_2[np.ix_(ord2, ord2)], dtype=np.int32)
        KW2_ord = np.ascontiguousarray(KW4[np.ix_(ord2, ord2)], dtype=np.int32)
        Gp4_ord = np.ascontiguousarray(Gp8_4[np.ix_(ord4, ord4)], dtype=np.int32)
        KW4_ord = np.ascontiguousarray(KW8[np.ix_(ord4, ord4)], dtype=np.int32)

        stab_y_to_0 = [[] for _ in range(4)]; seen_y_to_0 = [set() for _ in range(4)]
        g01_dict = {}; swap01_perms = []; seen_swap01 = set()
        for pr2, pc2 in stab2_m16:
            for pr4, pc4 in stab4_m16:
                g_p = list(pc4) + [8 + x for x in pc2]
                c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                t_map = tuple(c_map)
                for a_idx, orig_r in enumerate(ord2):
                    if pr2[orig_r] == ord2[0] and t_map not in seen_y_to_0[a_idx]:
                        seen_y_to_0[a_idx].add(t_map); stab_y_to_0[a_idx].append(c_map)
                if pr2[ord2[0]] == ord2[0] and pr2[ord2[1]] == ord2[1] and t_map != id_map:
                    f2 = 1 if pr2[ord2[2]] == ord2[2] else 0
                    f3 = 1 if (f2 == 1 and pr2[ord2[3]] == ord2[3]) else 0
                    prev = g01_dict.get(t_map, (0, 0))
                    g01_dict[t_map] = (max(prev[0], f2), max(prev[1], f3))
                if pr2[ord2[0]] == ord2[1] and pr2[ord2[1]] == ord2[0] and t_map not in seen_swap01:
                    seen_swap01.add(t_map); swap01_perms.append(c_map)

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

        tail_idx = 0
        for cand_idx in range(len(reps)):
            chk = solve_orbit_42_chiral_cpu(
                1, reps[cand_idx:cand_idx+1], rep_canons[cand_idx:cand_idx+1],
                Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
                X[0], cx_cans[0], X[1], cx_cans[1], X[2], cx_cans[2], X[3], cx_cans[3],
                X[4], cx_cans[4], X[5], cx_cans[5], X[6], cx_cans[6], X[7], cx_cans[7],
                Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
                C11_42, O11_42, O12_42,
                luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
            )
            if chk[6] > 0:
                tail_idx = cand_idx
                break

        for r_test_idx in [tail_idx, len(reps) // 2]:
            t0 = time.time()
            naive_c = naive_reference_check_42(
                int(reps[r_test_idx]), int(rep_canons[r_test_idx]),
                Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
                X[0], X[1], X[2], X[3],
                Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
                int(C11_42), int(O11_42), int(O12_42),
                g01_perms, g012_flags, g0123_flags, swap01_perms
            )
            numba_c = tuple(int(v) for v in solve_orbit_42_chiral_cpu(
                1, reps[r_test_idx:r_test_idx+1], rep_canons[r_test_idx:r_test_idx+1],
                Y[0], Y[1], cy_cans[1], Y[2], cy_cans[2], Y[3], cy_cans[3],
                X[0], cx_cans[0], X[1], cx_cans[1], X[2], cx_cans[2], X[3], cx_cans[3],
                X[4], cx_cans[4], X[5], cx_cans[5], X[6], cx_cans[6], X[7], cx_cans[7],
                Gp2_ord, KW2_ord, Gp4_ord, KW4_ord,
                C11_42, O11_42, O12_42,
                luts_g01, is_g012_flag, is_g0123_flag, luts_swap01
            ))
            assert naive_c == numba_c, f"Mismatch on Orbit {orb_idx} rep_idx={r_test_idx}: {naive_c} != {numba_c}"
            print(f"  [4+2 Orbit {orb_idx:3d} rep_idx={r_test_idx:3d}] PASS: naive={naive_c} == numba={numba_c} ({time.time()-t0:.2f}s)", flush=True)

    print("\nALL 14 CROSS-CHECK ORACLE TESTS (10 IN 3+3 + 4 IN 4+2) PASSED WITH 100% EXACT NODE-COUNT ISOMORPHISM!", flush=True)

if __name__ == "__main__":
    main()
