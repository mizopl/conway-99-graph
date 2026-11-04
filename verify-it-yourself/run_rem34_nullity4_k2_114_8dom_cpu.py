import os
import sys
import time
import json
import argparse
import numpy as np
import numba
from numba import njit, prange
from itertools import combinations, permutations, product
from collections import defaultdict

# Ensure Numba uses all available vCPU threads on the remote Colab VM
N_CPU = os.cpu_count() or 8
try:
    numba.set_num_threads(N_CPU)
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_all_10_nullity3_k0_33_cpu import (
    build_orbits,
    build_perm_luts,
    compute_canons_lut,
    popcnt64,
    apply_lut,
)
from run_rem11_nullity4_k2_114_8dom_cpu import (
    solve_class_114_parallel,
)


REM34_CLASSES = [
    1, 2, 7, 8, 9, 11, 13, 14, 15, 17, 18, 20, 21, 22, 24, 25, 26,
    27, 30, 31, 32, 35, 37, 38, 40, 44, 45, 46, 47, 48, 49, 50, 51, 53
]


def main():
    parser = argparse.ArgumentParser(
        description="Verify the remaining 34 1+1+4 classes under exact full 8-row stabilizer Stab8 (cols_full)."
    )
    parser.add_argument(
        "--classes",
        type=str,
        default="",
        help="Comma-separated list of class IDs to run (default: all 34 in REM34_CLASSES).",
    )
    parser.add_argument(
        "--shard",
        type=str,
        default="",
        help="Optional shard index k/N (0-indexed, e.g. 0/4, 1/4, 2/4, 3/4) for round-robin load-balanced splitting.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="rem34_nullity4_k2_114_8dom_results.json",
        help="Path to write incremental JSON checkpoint.",
    )
    args = parser.parse_args()

    if args.classes.strip():
        target_classes = [int(x.strip()) for x in args.classes.split(",") if x.strip()]
    else:
        target_classes = list(REM34_CLASSES)

    if args.shard.strip():
        k_str, n_str = args.shard.strip().split("/")
        k_shard, n_shards = int(k_str), int(n_str)
        target_classes = target_classes[k_shard::n_shards]

    t0 = time.time()
    n_threads = numba.get_num_threads()
    print(
        f"[INIT] Numba vCPU threads={n_threads} (os.cpu_count()={os.cpu_count()}) | Target classes ({len(target_classes)}): {target_classes}",
        flush=True,
    )

    F12, I12, J12, b6_perms, orbits_by_sig = build_orbits()
    b2_perms_4 = [
        tuple(
            2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl)
            for (b_new, fl) in zip(bp, flips)
            for s in (0, 1)
        )
        for bp in permutations(range(2))
        for flips in product((0, 1), repeat=2)
    ]
    b4_perms_8 = [
        tuple(
            2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl)
            for (b_new, fl) in zip(bp, flips)
            for s in (0, 1)
        )
        for bp in permutations(range(4))
        for flips in product((0, 1), repeat=4)
    ]

    def canon_4block(M8, E8):
        return min(
            tuple(M8[np.ix_(p, p)].flatten()) + tuple(E8[np.ix_(p, p)].flatten())
            for p in b4_perms_8
        )

    c4_classes = []
    seen_c4 = set()
    for M, E, Gp, KW0, Delta0, comps in orbits_by_sig["kt1=2_4+1+1"]:
        comp4 = [c for c in comps if len(c) == 8][0]
        M8, E8 = M[np.ix_(comp4, comp4)], E[np.ix_(comp4, comp4)]
        ck4 = canon_4block(M8, E8)
        if ck4 not in seen_c4:
            seen_c4.add(ck4)
            c4_classes.append((M8, E8))

    cols_60 = []
    col_idx = {}
    for b1 in range(6):
        for b2 in range(b1 + 1, 6):
            for s1 in (0, 1):
                for s2 in (0, 1):
                    j1, j2 = 2 * b1 + s1, 2 * b2 + s2
                    c = len(cols_60)
                    cols_60.append((j1, j2))
                    col_idx[(j1, j2)] = col_idx[(j2, j1)] = c
    g_col = [col_idx[(j1 ^ 1, j2 ^ 1)] for (j1, j2) in cols_60]
    orbs_30 = [(c, g_col[c]) for c in range(60) if c < g_col[c]]
    I_B1 = {0, 1, 2, 3, 4, 5, 6, 7}
    O11_int = sum(
        1 << m
        for m, (c, gc) in enumerate(orbs_30)
        if cols_60[c][0] in I_B1 and cols_60[c][1] in I_B1
    )
    O12_int = sum(
        1 << m
        for m, (c, gc) in enumerate(orbs_30)
        if (cols_60[c][0] in I_B1) ^ (cols_60[c][1] in I_B1)
    )
    col_orb_bit = [0] * 60
    for idx_m, (c, gc) in enumerate(orbs_30):
        col_orb_bit[c] = 1 << idx_m
        col_orb_bit[gc] = 1 << idx_m

    y_cache = {}

    def gen_2block_rows(target_deg_4, diag_kw):
        key = (target_deg_4, diag_kw)
        if key in y_cache:
            return y_cache[key]
        target_deg_12 = (2, 2, 2, 2, 2, 2, 2, 2) + tuple(target_deg_4)
        req_pairs = diag_kw // 2
        ok_cols = [
            c
            for c in range(60)
            if target_deg_12[cols_60[c][0]] > 0
            and target_deg_12[cols_60[c][1]] > 0
            and not (cols_60[c][0] not in I_B1 and cols_60[c][1] not in I_B1)
        ]
        adj_cols = [[] for _ in range(12)]
        for c in ok_cols:
            u, v = cols_60[c]
            adj_cols[min(u, v)].append(
                (c, max(u, v), 1 << c, 1 << g_col[c], col_orb_bit[c])
            )
        rem_deg = list(target_deg_12)
        res = []

        def bt_v(v_idx, n_ch, xm, gxm, orb_u1, orb_u2):
            if v_idx == 12:
                if (
                    n_ch == 10
                    and (orb_u2 & O12_int) == 0
                    and orb_u2.bit_count() == req_pairs
                ):
                    o11_2 = orb_u2 & O11_int
                    o11_1 = (orb_u1 & O11_int) ^ o11_2
                    o12_1 = orb_u1 & O12_int
                    res.append((xm, gxm, o11_1, o11_2, o12_1, orb_u2))
                return
            need = rem_deg[v_idx]
            if need < 0:
                return
            avail = [item for item in adj_cols[v_idx] if rem_deg[item[1]] > 0]
            if len(avail) < need:
                return
            for comb in combinations(avail, need):
                nxm, ngxm, nu1, nu2 = xm, gxm, orb_u1, orb_u2
                for c, w, cb, gcb, ob in comb:
                    rem_deg[w] -= 1
                    nxm |= cb
                    ngxm |= gcb
                    nu2 |= nu1 & ob
                    nu1 |= ob
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
        if key in x_cache:
            return x_cache[key]
        target_deg_12 = tuple(target_deg_8) + (2, 2, 2, 2)
        req_pairs = diag_kw // 2
        ok_cols = [
            c
            for c in range(60)
            if target_deg_12[cols_60[c][0]] > 0 and target_deg_12[cols_60[c][1]] > 0
        ]
        adj_cols = [[] for _ in range(12)]
        for c in ok_cols:
            u, v = cols_60[c]
            adj_cols[min(u, v)].append(
                (c, max(u, v), 1 << c, 1 << g_col[c], col_orb_bit[c])
            )
        rem_deg = list(target_deg_12)
        res = []

        def bt_v(v_idx, n_ch, xm, gxm, orb_u1, orb_u2):
            if v_idx == 12:
                if n_ch == 10 and orb_u2.bit_count() == req_pairs:
                    res.append((xm, gxm, 0, 0, 0, 0, orb_u2))
                return
            need = rem_deg[v_idx]
            if need < 0:
                return
            avail = [item for item in adj_cols[v_idx] if rem_deg[item[1]] > 0]
            if len(avail) < need:
                return
            for comb in combinations(avail, need):
                nxm, ngxm, nu1, nu2 = xm, gxm, orb_u1, orb_u2
                for c, w, cb, gcb, ob in comb:
                    rem_deg[w] -= 1
                    nxm |= cb
                    ngxm |= gcb
                    nu2 |= nu1 & ob
                    nu1 |= ob
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

    Y0_pool = gen_2block_rows((0, 0, 2, 2), 0)
    Y2_pool = gen_2block_rows((2, 2, 0, 0), 0)
    O12_y0_mask = 0
    for i in range(len(Y0_pool)):
        O12_y0_mask |= int(Y0_pool[i, 4])
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
    for i in range(len(Y2_pool)):
        O12_y2_mask |= int(Y2_pool[i, 4])
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

    F4 = F12[:4, :4]
    I4 = np.eye(4, dtype=int)
    J4 = np.ones((4, 4), dtype=int)
    F8 = F12[:8, :8]
    I8 = np.eye(8, dtype=int)
    J8 = np.ones((8, 8), dtype=int)
    M4, E4 = F4.copy(), F4.copy()
    KW4 = (2 * J4 - F4 - E4 - (M4 @ E4) - (E4 @ M4)).astype(np.int32)
    D4 = 2 * J4 - I4 - F4 - M4 - (E4 @ F4)
    Gp4_2 = (7 * I4 + J4 - M4).astype(np.int32)
    Y_raw = [Y0_pool, Y0_pool, Y2_pool, Y2_pool]
    ylens = [len(y) for y in Y_raw]
    stab2_m16 = []
    for pr in permutations(range(4)):
        if any(ylens[pr[a]] != ylens[a] for a in range(4)):
            continue
        if (
            not (Gp4_2 == Gp4_2[np.ix_(pr, pr)]).all()
            or not (KW4 == KW4[np.ix_(pr, pr)]).all()
        ):
            continue
        for pc in b2_perms_4:
            if (D4 == D4[np.ix_(pr, pc)]).all():
                stab2_m16.append((pr, pc))
    ord2 = [0, 1, 2, 3]
    Y = [Y_raw[r] for r in ord2]
    ALL60 = np.uint64((1 << 60) - 1)
    id_map = tuple(range(60))

    print(
        f"Prepared Y pools in {time.time()-t0:.2f}s. Solving {len(target_classes)} 1+1+4 classes: {target_classes}",
        flush=True,
    )

    results = []
    for idx_m, ex_c in enumerate(target_classes):
        tc0 = time.time()
        M8, E8 = c4_classes[ex_c]
        KW8 = (2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)).astype(np.int32)
        D8 = 2 * J8 - I8 - F8 - M8 - (E8 @ F8)
        Gp8_4 = (7 * I8 + J8 - M8).astype(np.int32)
        X = [
            gen_4block_rows(tuple(int(D8[r, j]) for j in range(8)), int(KW8[r, r]))
            for r in range(8)
        ]
        xlens = [len(x) for x in X]

        # Exact full 8-row decoupled stabilizer Stab_{S_8 x B_4}(Gp8_4, KW8, D8)
        m_pairs = [
            (r, int(np.where(M8[r] == 1)[0][0]))
            for r in range(8)
            if r < int(np.where(M8[r] == 1)[0][0])
        ]
        stab8 = []
        cols_full_set = set()
        for bp in permutations(range(4)):
            for flips in product((0, 1), repeat=4):
                pr = [0] * 8
                for b_old, (b_new, fl) in enumerate(zip(bp, flips)):
                    u_old, v_old = m_pairs[b_old]
                    u_new, v_new = m_pairs[b_new]
                    pr[u_old] = u_new if fl == 0 else v_new
                    pr[v_old] = v_new if fl == 0 else u_new
                pr = tuple(pr)
                if any(xlens[pr[a]] != xlens[a] for a in range(8)):
                    continue
                if not (KW8 == KW8[np.ix_(pr, pr)]).all():
                    continue
                d_pr = D8[list(pr), :]
                for pc in b4_perms_8:
                    if (d_pr[:, pc] == D8).all():
                        stab8.append((pr, pc))
                        cols_full_set.add(pc)

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
                if (
                    pr2[ord2[0]] == ord2[0]
                    and pr2[ord2[1]] == ord2[1]
                    and t_map != id_map
                ):
                    f2 = 1 if pr2[ord2[2]] == ord2[2] else 0
                    prev = g01_dict.get(t_map, 0)
                    g01_dict[t_map] = max(prev, f2)
                if (
                    pr2[ord2[0]] == ord2[1]
                    and pr2[ord2[1]] == ord2[0]
                    and t_map not in seen_swap01
                ):
                    seen_swap01.add(t_map)
                    swap01_perms.append(c_map)

        g01_perms = [list(k) for k in g01_dict.keys()]
        g012_flags = [v for v in g01_dict.values()]
        cy_cans = [
            compute_canons_lut(Y[a], build_perm_luts(stab_y_to_0[a])) for a in range(4)
        ]
        luts_g01 = build_perm_luts(g01_perms)
        is_g012_flag = np.ascontiguousarray(np.array(g012_flags, dtype=np.int32))
        luts_swap01 = build_perm_luts(swap01_perms)

        raw_reps = [i for i in range(len(Y[0])) if Y[0][i, 0] == cy_cans[0][i]]
        # Stripe-interleave representatives across n_threads * 4 buckets so static prange
        # distributes heavy low-i0 boundary pairs evenly across all vCPU threads.
        n_stripe = max(1, n_threads * 4)
        striped_reps = [
            raw_reps[idx]
            for s in range(n_stripe)
            for idx in range(s, len(raw_reps), n_stripe)
        ]
        reps = np.ascontiguousarray(striped_reps, dtype=np.int32)
        rep_canons = np.ascontiguousarray(
            [cy_cans[0][i] for i in striped_reps], dtype=np.uint64
        )

        if idx_m == 0:
            _ = solve_class_114_parallel(
                1,
                reps[:1],
                rep_canons[:1],
                Y0_pool,
                Y0_adj,
                Y0_deg,
                cy_cans[1],
                Y2_pool,
                Y2_adj,
                Y2_deg,
                cy_cans[2],
                X[0],
                X[1],
                X[2],
                X[3],
                X[4],
                X[5],
                X[6],
                X[7],
                Gp8_4,
                KW8,
                ALL60,
                luts_g01,
                is_g012_flag,
                luts_swap01,
            )

        res = solve_class_114_parallel(
            len(reps),
            reps,
            rep_canons,
            Y0_pool,
            Y0_adj,
            Y0_deg,
            cy_cans[1],
            Y2_pool,
            Y2_adj,
            Y2_deg,
            cy_cans[2],
            X[0],
            X[1],
            X[2],
            X[3],
            X[4],
            X[5],
            X[6],
            X[7],
            Gp8_4,
            KW8,
            ALL60,
            luts_g01,
            is_g012_flag,
            luts_swap01,
        )
        el = round(time.time() - tc0, 2)
        if int(res[2]) != 0:
            raise RuntimeError(
                f"[1+1+4 Class {ex_c:2d} FAIL] Expected 0 solutions, got sols={int(res[2])}"
            )
        rec = {
            "class_id": int(ex_c),
            "stab8x2_order": int(len(stab8) * len(stab2_m16)),
            "cols_full_order": int(len(cols_full_set)),
            "reps": int(len(reps)),
            "b1": int(res[0]),
            "nodes": int(res[1]),
            "sols": int(res[2]),
            "elapsed_s": el,
        }
        results.append(rec)
        with open(args.out, "w") as f:
            json.dump(
                {
                    "threads": n_threads,
                    "completed_count": len(results),
                    "total_target_count": len(target_classes),
                    "results": results,
                },
                f,
                indent=2,
            )
        print(
            f"[{len(results):2d}/{len(target_classes):2d}] [1+1+4 Class {ex_c:2d}] |Stab8x2|={rec['stab8x2_order']:4d} (|cols_full|={rec['cols_full_order']:2d}) | reps={rec['reps']:4d} | b1={rec['b1']:7d} nodes={rec['nodes']:9d} sols={rec['sols']} | {el:.2f}s",
            flush=True,
        )

    print(
        f"[DONE] Verified {len(results)}/{len(target_classes)} classes in {time.time()-t0:.2f}s -> {args.out}",
        flush=True,
    )


if __name__ == "__main__":
    main()
