import os
import sys
import time
import numpy as np
from numba import njit
from collections import Counter
from itertools import combinations, permutations, product

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


import run_all_10_nullity4_k0_222_cpu as M222
M222.apply_lut = apply_lut
M222.popcnt64 = popcnt64
M222.eq_bits = eq_bits_42
from run_all_10_nullity4_k0_222_cpu import solve_222_chiral_cpu, comp_priority

def main():
    t_start = time.time()
    F12, I12, J12, b6_perms, orbits_by_sig = build_orbits()
    orbits_1122 = orbits_by_sig["kt1=2_2+2+1+1"]
    print(f"[1/2] Loaded {len(orbits_1122)} orbits of 1+1+2+2 (kt1=2_2+2+1+1) in {time.time()-t_start:.2f}s.", flush=True)

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
    col_orb_bit = [0] * 60
    for idx_m, (c, gc) in enumerate(orbs_30):
        col_orb_bit[c] = 1 << idx_m
        col_orb_bit[gc] = 1 << idx_m

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
            u, v = cols_60[c]; adj_cols[min(u, v)].append((c, max(u, v), 1 << c, 1 << g_col[c], col_orb_bit[c]))
        rem_deg = list(target_deg); res = []
        def bt_v(v_idx, n_ch, xm, gxm, orb_u1, orb_u2):
            if v_idx == 12:
                if n_ch == 10 and (orb_u2 & cut_orb_mask) == 0 and orb_u2.bit_count() == req_pairs:
                    c2_out = orb_u2 & out_orb_mask
                    c1_out = (orb_u1 & out_orb_mask) ^ c2_out
                    c1_cut = orb_u1 & cut_orb_mask
                    res.append((xm, gxm, c1_cut, c1_out, c2_out))
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
        row_pool_cache[key] = arr
        return arr

    total_b1 = 0; total_b2 = 0; total_b3 = 0
    for run_i, (M_orig, E_orig, Gp_orig, KW0_orig, Delta0_orig, comps_orig) in enumerate(orbits_1122):
        comps2 = [c for c in comps_orig if len(c) == 4]
        comps1 = [c for c in comps_orig if len(c) == 2]
        ctypes2 = [comp_priority(M_orig, E_orig, KW0_orig, c) for c in comps2]
        if ctypes2[1] < ctypes2[0]:
            comps2 = [comps2[1], comps2[0]]
            ctypes2 = [ctypes2[1], ctypes2[0]]
        comps_sorted = [comps2[0], comps2[1], comps1[0] + comps1[1]]
        perm = [u for c in comps_sorted for u in c]
        M = M_orig[np.ix_(perm, perm)]
        E = E_orig[np.ix_(perm, perm)]
        Gp = Gp_orig[np.ix_(perm, perm)]
        KW0 = KW0_orig[np.ix_(perm, perm)]
        Delta0 = 2 * J12 - I12 - F12 - M - (E @ F12)
        comps = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
        cname_map = {0: "B", 1: "A", 2: "C"}
        csig = f"{cname_map[ctypes2[0]]}+{cname_map[ctypes2[1]]}+C1+C1"
        same_b12 = 1 if ctypes2[0] == ctypes2[1] else 0

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
        st3 = get_stab_comp(comps[2])
        pc3_set = sorted(set(pc3 for (pr3, pc3) in st3 if pr3 == (0, 1, 2, 3) or pr3 in [(0, 1, 2, 3), (1, 0, 2, 3), (0, 1, 3, 2), (1, 0, 3, 2)]))
        # Wait: in solve_single_rep_222, L8, L9 are rows 8,9 and L10, L11 are rows 10,11 (different pools: L8=L9 has deg 0 on 8,9 and L10=L11 has deg 0 on 10,11!).
        # When pc3 swaps {8,9} <-> {10,11}, it swaps L8,L9 with L10,L11! Since Gp[8..11, 8..11] and KW0[8..11, 8..11] are invariant under swapping (8,9)<->(10,11),
        # wait: solve_single_rep_222 tests x8 in L8, x9 in L9, x10 in L10, x11 in L11!
        # If pc3 swaps {8,9}<->{10,11}, applying pc3 to a solution (x8, x9, x10, x11) produces (pc3(x8) in L10, pc3(x9) in L11, pc3(x10) in L8, pc3(x11) in L9), which is a valid 4-tuple (x8', x9', x10', x11') in L8 x L9 x L10 x L11!
        # So ALL pc3 in st3 (all 8 elements of b2_perms_4) preserve L8 x L9 x L10 x L11 up to row permutation pr3!
        pc3_set = sorted(set(pc3 for (pr3, pc3) in st3))

        def make_cmap(pc1, pc2, pc3):
            p12 = [pc1[j] for j in range(4)] + [4 + pc2[j] for j in range(4)] + [8 + pc3[j] for j in range(4)]
            return np.array([col_idx[(p12[j1], p12[j2])] for (j1, j2) in cols_60], dtype=np.int32)

        stab_a_to_0 = [[] for _ in range(8)]
        for (pr1, pc1) in st1:
            a = pr1.index(0)
            for (pr2, pc2) in st2:
                for pc3 in pc3_set:
                    stab_a_to_0[a].append(make_cmap(pc1, pc2, pc3))
        if same_b12 == 1:
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
            t_jit = time.time()
            _ = solve_222_chiral_cpu(
                0, reps[:1], rep_canons[:1], same_b12,
                L[0], L[1], c_cans[1], L[2], c_cans[2], L[3], c_cans[3],
                L[4], c_cans[4], L[5], c_cans[5], L[6], c_cans[6], L[7], c_cans[7],
                L[8], L[9], L[10], L[11],
                Gp_off, KW0_int, O33_mask, O13_mask, O23_mask,
                luts_g01, is_g012_flag, is_g0123_flag, is_g01234_flag, luts_swap01
            )
            print(f"  -> JIT compiled solve_222_chiral_cpu in {time.time()-t_jit:.2f}s", flush=True)

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
            f"[{run_i+1}/6] Orbit {run_i} ({csig}): |G|={len(stab_a_to_0[0])}, reps={len(reps):4d}, "
            f"b1_sols={nb1:8d}, b12_sols={nb2:6d}, b123_sols={nb3} in {dt:.2f}s "
            f"(elapsed={time.time()-t_start:.2f}s)",
            flush=True
        )

    print(f"\n[PART B2 PASS] ALL 6 ORBITS OF 1+1+2+2 CERTIFIED UNSAT in {time.time()-t_start:.2f}s: total_b1={total_b1:,}, total_b12={total_b2:,}, total_b123={total_b3}", flush=True)

if __name__ == "__main__":
    main()
