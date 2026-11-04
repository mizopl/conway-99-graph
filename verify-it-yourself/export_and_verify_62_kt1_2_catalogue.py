#!/usr/bin/env python3
"""
Exports and verifies the machine-readable correspondence catalogue for all 62
canonical k_type1 = 2 slice classes (6 classes in 1+1+2+2 and 56 classes in 1+1+4),
including:
  1. Explicit ordered matching pairs (M8, E8) on the 8 non-Type-I vertices and (M12, E12),
  2. Derived slice matrices Gp8, KW8, D8 and exact per-row mask domain sizes
     (22,176 for Type-I rows Y0/Y2; 91,392 / 155,904 / 205,776 for 4-block rows X_r),
  3. Diagonal B4 stabilizer vs. full 8-row decoupled stabilizer Stab_{S8 x B4}(Gp8, KW8, D8)
     and the resulting orbit counts on the 289,536 ordered (144,768 unordered) compatible
     Type-I boundary pairs (y0, y1),
  4. Assignment of all 56 1+1+4 classes to the 45 4x8 sub-cones (with explicit 4-row
     subset q_rows, row permutation pr_4, and column permutation pc_8 in B4) and to the
     11 full-system 8-domain classes, plus a detailed worked example for Class 4.
"""
import json
import os
import sys
import time
from collections import defaultdict
from itertools import combinations, permutations, product
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_all_10_nullity3_k0_33_cpu import build_orbits, build_perm_luts, apply_lut


def edges_from_mat(M):
    n = M.shape[0]
    return [[int(u), int(v)] for u in range(n) for v in range(u + 1, n) if int(M[u, v]) == 1]


def main():
    t0 = time.time()
    F12, I12, J12, b6_perms, orbits_by_sig = build_orbits()

    b2_perms_4 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(2))
        for flips in product((0, 1), repeat=2)
    ]
    b4_perms_8 = [
        tuple(2 * b_new + fl if s == 0 else 2 * b_new + (1 - fl) for (b_new, fl) in zip(bp, flips) for s in (0, 1))
        for bp in permutations(range(4))
        for flips in product((0, 1), repeat=4)
    ]

    def canon_4block(M8, E8):
        return min(
            tuple(M8[np.ix_(p, p)].flatten()) + tuple(E8[np.ix_(p, p)].flatten())
            for p in b4_perms_8
        )

    # 1. Extract the 6 canonical 1+1+2+2 classes (on the 8 non-Type-I vertices)
    c22_classes = []
    seen_c22 = set()
    for M, E, Gp, KW0, Delta0, comps in orbits_by_sig["kt1=2_2+2+1+1"]:
        comps2 = [c for c in comps if len(c) == 4]
        comp8 = comps2[0] + comps2[1]
        M8, E8 = M[np.ix_(comp8, comp8)], E[np.ix_(comp8, comp8)]
        ck = canon_4block(M8, E8)
        if ck not in seen_c22:
            seen_c22.add(ck)
            c22_classes.append((M8, E8, M, E, comp8))

    # 2. Extract the 56 canonical 1+1+4 classes (on the 8-vertex 4-block component)
    c4_classes = []
    seen_c4 = set()
    for M, E, Gp, KW0, Delta0, comps in orbits_by_sig["kt1=2_4+1+1"]:
        comp4 = [c for c in comps if len(c) == 8][0]
        M8, E8 = M[np.ix_(comp4, comp4)], E[np.ix_(comp4, comp4)]
        ck4 = canon_4block(M8, E8)
        if ck4 not in seen_c4:
            seen_c4.add(ck4)
            c4_classes.append((M8, E8, M, E, comp4))

    assert len(c22_classes) == 6, f"Expected 6 1+1+2+2 classes, got {len(c22_classes)}"
    assert len(c4_classes) == 56, f"Expected 56 1+1+4 classes, got {len(c4_classes)}"

    # 3. Build 60-column indexing and verify exact Type-I (22,176) vs 4-block (91,392 / 155,904 / 205,776) pools
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
    O11_int = sum(1 << m for m, (c, gc) in enumerate(orbs_30) if cols_60[c][0] in I_B1 and cols_60[c][1] in I_B1)
    O12_int = sum(1 << m for m, (c, gc) in enumerate(orbs_30) if (cols_60[c][0] in I_B1) ^ (cols_60[c][1] in I_B1))
    col_orb_bit = [0] * 60
    for idx_m, (c, gc) in enumerate(orbs_30):
        col_orb_bit[c] = 1 << idx_m
        col_orb_bit[gc] = 1 << idx_m

    def gen_2block_rows(target_deg_4, diag_kw):
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
            adj_cols[min(u, v)].append((c, max(u, v), 1 << c, 1 << g_col[c], col_orb_bit[c]))
        rem_deg = list(target_deg_12)
        res = []

        def bt_v(v_idx, n_ch, xm, gxm, orb_u1, orb_u2):
            if v_idx == 12:
                if n_ch == 10 and (orb_u2 & O12_int) == 0 and orb_u2.bit_count() == req_pairs:
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
        return np.ascontiguousarray(np.array(res, dtype=np.uint64))

    Y0 = gen_2block_rows((0, 0, 2, 2), 0)
    assert len(Y0) == 22176, f"Expected 22,176 Type-I rows, got {len(Y0)}"
    by_orb0 = defaultdict(list)
    O12_y0 = 0
    for i in range(len(Y0)):
        O12_y0 |= int(Y0[i, 4])
        by_orb0[(int(Y0[i, 2]), int(Y0[i, 4]))].append(i)
    ordered_y0_pairs = []
    for i in range(len(Y0)):
        comp = (O11_int ^ int(Y0[i, 2]), O12_y0 ^ int(Y0[i, 4]))
        for j in by_orb0.get(comp, []):
            ordered_y0_pairs.append((int(Y0[i, 0]), int(Y0[j, 0])))
    assert len(ordered_y0_pairs) == 289536, f"Expected 289,536 ordered pairs, got {len(ordered_y0_pairs)}"

    # 4. Build the 45 canonical 4x8 sub-cones and record exact transport maps for every class
    F8 = F12[:8, :8]
    I8 = np.eye(8, dtype=int)
    J8 = np.ones((8, 8), dtype=int)

    def w4_mat(Gp8, KW8, u, v):
        return (4 if Gp8[u, v] == 0 else (1 if Gp8[u, v] == 1 else 0)) + (
            4 if KW8[u, v] == 0 else (1 if KW8[u, v] == 1 else 0)
        )

    perms4 = list(permutations(range(4)))
    cone_info = {}
    class_to_cone_transports = defaultdict(dict)

    for idx_d, (M8, E8, _, _, _) in enumerate(c4_classes):
        KW8 = 2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)
        D8 = 2 * J8 - I8 - F8 - M8 - (E8 @ F8)
        Gp8 = 7 * I8 + J8 - M8
        for q in combinations(range(8), 4):
            q = list(q)
            sm = sum(3 if 0 in D8[r] else (1 if KW8[r, r] == 0 else 0) for r in q)
            w_sum = sum(w4_mat(Gp8, KW8, q[a], q[b]) for a in range(4) for b in range(a + 1, 4))
            gp4, kw4, d48 = Gp8[np.ix_(q, q)], KW8[np.ix_(q, q)], D8[q, :]
            gp0 = tuple(gp4.flatten())
            kw0 = tuple(kw4.flatten())
            d0 = tuple(d48.flatten())
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
            best_pr = None
            best_pc = None
            for pr in cand_prs:
                d_pr = d48[list(pr), :]
                for pc in b4_perms_8:
                    dp = tuple(d_pr[:, pc].flatten())
                    if best_d is None or dp < best_d:
                        best_d = dp
                        best_pr = pr
                        best_pc = pc
            best_key = min_gk + best_d
            if best_key not in cone_info:
                cone_info[best_key] = {
                    "st": st,
                    "small": sm,
                    "w_sum": w_sum,
                    "classes": set(),
                    "example": (idx_d, q),
                }
            cone_info[best_key]["classes"].add(idx_d)
            if idx_d not in class_to_cone_transports[best_key]:
                class_to_cone_transports[best_key][idx_d] = {
                    "q_rows": q,
                    "canonical_row_perm_pr4": list(best_pr),
                    "canonical_col_perm_pc8": list(best_pc),
                }

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
                cone_info[k]["st"],
            ),
        )
        info = cone_info[best_k]
        new_c = sorted(info["classes"] & uncov)
        chosen_cones.append((best_k, new_c, sorted(info["classes"]), info))
        uncov -= info["classes"]

    rem11_set = {39, 41, 43, 5, 6, 34, 33, 52, 55, 16, 54}
    class_primary_cone = {}
    subcones_export = []
    for cone_id, (best_k, new_c, all_c, info) in enumerate(chosen_cones):
        ex_class, ex_q = info["example"]
        for c_id in new_c:
            class_primary_cone[c_id] = (cone_id, class_to_cone_transports[best_k][c_id])
        subcones_export.append(
            {
                "cone_id": cone_id,
                "example_class_id": ex_class,
                "example_q_rows": ex_q,
                "subcone_stab4_order": int(info["st"]),
                "newly_covered_classes": new_c,
                "all_matching_classes": all_c,
                "transports_by_class": {str(c_id): class_to_cone_transports[best_k][c_id] for c_id in all_c},
            }
        )

    # 5. Export all 56 1+1+4 classes and all 6 1+1+2+2 classes
    lego_summary_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "null_ktype1_ge1_unconditional_lego_summary.json",
    )
    all56_8dom_by_id = {}
    if os.path.exists(lego_summary_path):
        with open(lego_summary_path, "r") as f_lego:
            lego_data = json.load(f_lego)
        for rec in (
            lego_data.get("strata_certified", {})
            .get("kt1_2_partition_4_1_1", {})
            .get("all_56_classes_8dom", [])
        ):
            all56_8dom_by_id[int(rec["class_id"])] = rec

    classes_56_export = []
    for idx_c, (M8, E8, M12, E12, comp4) in enumerate(c4_classes):
        KW8 = (2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)).astype(int)
        D8 = (2 * J8 - I8 - F8 - M8 - (E8 @ F8)).astype(int)
        Gp8 = (7 * I8 + J8 - M8).astype(int)
        row_pool_sizes = [
            91392 if 0 in D8[r] else (155904 if KW8[r, r] == 0 else 205776)
            for r in range(8)
        ]
        diag_stab = [
            p for p in b4_perms_8 if (M8[np.ix_(p, p)] == M8).all() and (E8[np.ix_(p, p)] == E8).all()
        ]
        m_pairs = [
            (r, int(np.where(M8[r] == 1)[0][0]))
            for r in range(8)
            if r < int(np.where(M8[r] == 1)[0][0])
        ]
        decoupled_stab8 = []
        decoupled_cols = set()
        for bp in permutations(range(4)):
            for flips in product((0, 1), repeat=4):
                pr = [0] * 8
                for b_old, (b_new, fl) in enumerate(zip(bp, flips)):
                    u_old, v_old = m_pairs[b_old]
                    u_new, v_new = m_pairs[b_new]
                    pr[u_old] = u_new if fl == 0 else v_new
                    pr[v_old] = v_new if fl == 0 else u_new
                pr = tuple(pr)
                if any(row_pool_sizes[pr[a]] != row_pool_sizes[a] for a in range(8)):
                    continue
                if not (KW8 == KW8[np.ix_(pr, pr)]).all():
                    continue
                d_pr = D8[list(pr), :]
                for pc in b4_perms_8:
                    if (d_pr[:, pc] == D8).all():
                        decoupled_stab8.append((pr, pc))
                        decoupled_cols.add(pc)

        cone_id, tr = class_primary_cone[idx_c]
        q_rows = tr["q_rows"]
        gp4 = Gp8[np.ix_(q_rows, q_rows)]
        kw4 = KW8[np.ix_(q_rows, q_rows)]
        d48 = D8[q_rows, :]
        q_sizes = [row_pool_sizes[r] for r in q_rows]
        cols_sub_set = set()
        for pr in perms4:
            if any(q_sizes[pr[a]] != q_sizes[a] for a in range(4)):
                continue
            if not ((gp4[np.ix_(pr, pr)] == gp4).all() and (kw4[np.ix_(pr, pr)] == kw4).all()):
                continue
            d_pr = d48[list(pr), :]
            for pc in b4_perms_8:
                if (d_pr[:, pc] == d48).all():
                    cols_sub_set.add(pc)
        classes_56_export.append(
            {
                "class_id": idx_c,
                "M8_edges": edges_from_mat(M8),
                "E8_edges": edges_from_mat(E8),
                "M8_matrix": M8.tolist(),
                "E8_matrix": E8.tolist(),
                "Gp8_matrix": Gp8.tolist(),
                "KW8_matrix": KW8.tolist(),
                "D8_matrix": D8.tolist(),
                "B4_row_pool_sizes_exact": row_pool_sizes,
                "TypeI_row_pool_sizes_exact": [22176, 22176, 22176, 22176],
                "diagonal_Aut_B4_order": len(diag_stab),
                "diagonal_Aut_B6_order": len(diag_stab) * 8,
                "decoupled_Stab8_order": len(decoupled_stab8),
                "decoupled_Stab8_col_proj_order": len(decoupled_cols),
                "decoupled_Stab8x2_order": len(decoupled_stab8) * 32,
                "subcone_cols_sub_order": len(cols_sub_set),
                "cols_sub_is_subgroup_of_cols_full": cols_sub_set.issubset(decoupled_cols),
                "assigned_subcone_id": cone_id,
                "subcone_transport": tr,
                "in_secondary_11_full_system_run": idx_c in rem11_set,
                "full_stab8_8dom_verification": all56_8dom_by_id.get(idx_c),
            }
        )

    classes_6_export = []
    for idx_c, (M8, E8, M12, E12, comp8) in enumerate(c22_classes):
        KW8 = (2 * J8 - F8 - E8 - (M8 @ E8) - (E8 @ M8)).astype(int)
        D8 = (2 * J8 - I8 - F8 - M8 - (E8 @ F8)).astype(int)
        Gp8 = (7 * I8 + J8 - M8).astype(int)
        diag_stab = [
            p for p in b4_perms_8 if (M8[np.ix_(p, p)] == M8).all() and (E8[np.ix_(p, p)] == E8).all()
        ]
        classes_6_export.append(
            {
                "class_id": idx_c,
                "M8_edges": edges_from_mat(M8),
                "E8_edges": edges_from_mat(E8),
                "M8_matrix": M8.tolist(),
                "E8_matrix": E8.tolist(),
                "Gp8_matrix": Gp8.tolist(),
                "KW8_matrix": KW8.tolist(),
                "D8_matrix": D8.tolist(),
                "diagonal_Aut_B4_order": len(diag_stab),
            }
        )

    out_payload = {
        "schema": "conway99_kt1_2_62_class_correspondence_v1",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "domain_counts_explanation": {
            "TypeI_row_pool_Y0_Y2": {
                "mask_count": 22176,
                "ordered_compatible_pairs_y0_y1": 289536,
                "unordered_compatible_pairs_y0_lt_y1": 144768,
                "constraints": (
                    "Weight-10 subset of the 60 cross-block edges with vertex-degree vector "
                    "(2,2,2,2,2,2,2,2, 0,0,2,2) (or (2,2,2,2,2,2,2,2, 2,2,0,0)), 0 involution "
                    "dominoes (KW_diag = 0), AND 0 edges with both endpoints outside the 8-vertex "
                    "block I_B1 (enforced by M4 = E4 = F4 on the two Type-I blocks)."
                ),
            },
            "B4_4block_row_pools_Xr": {
                "mask_count_with_zero_in_D8_and_KW2": 91392,
                "mask_count_no_zero_in_D8_and_KW0": 155904,
                "mask_count_no_zero_in_D8_and_KW2": 205776,
                "note_on_previous_comment_terminology": (
                    "In our 2026-11-03 comment, 91,392 was inadvertently described as the Type-I "
                    "row pool; in fact, 22,176 is the Type-I row pool (gen_2block_rows((0,0,2,2), 0)), "
                    "matching @ibenarb's 22,176 count and 289,536 compatible boundary states exactly, "
                    "whereas 91,392 is the 4-block row pool X_r (gen_4block_rows) when row r in B_4 "
                    "has a single zero in D_8[r] (degree multiset (0,1,1,2,2,2,2,2, 2,2,2,2) and KW_diag = 2)."
                ),
            },
        },
        "classes_1_1_2_2_count": 6,
        "classes_1_1_2_2": classes_6_export,
        "classes_1_1_4_count": 56,
        "classes_1_1_4": classes_56_export,
        "subcones_4x8_count": 45,
        "subcones_4x8": subcones_export,
        "secondary_11_full_system_class_ids": sorted(rem11_set),
        "worked_example_class_4": {
            "class_id": 4,
            "M8_edges": [[0, 1], [2, 3], [4, 6], [5, 7]],
            "E8_edges": [[0, 4], [1, 5], [2, 6], [3, 7]],
            "B4_row_pool_sizes_exact": [91392, 91392, 91392, 91392, 205776, 205776, 205776, 205776],
            "TypeI_row_pool_sizes_exact": [22176, 22176, 22176, 22176],
            "ordered_compatible_TypeI_pairs_y0_y1": 289536,
            "boundary_orbits_under_order32_boundary_group": 9072,
            "assigned_subcone_id": 2,
            "subcone_q_rows": [0, 1, 2, 3],
            "subcone_4row_col_stabilizer_order": 8,
            "full_8row_col_stabilizer_order": 4,
            "full_8row_Stab8x2_verification": {
                "stab8x2_order": 128,
                "y0_reps": 2898,
                "b1_boundary_4tuples": 504090,
                "d6_prefixes": 180557100,
                "d8_prefixes": 1279698,
                "solutions": 0,
                "elapsed_s": 102.36,
            },
        },
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogue_62_kt1_2_correspondence.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_payload, f, indent=2)
    print(f"[PASS] Exported 6 + 56 class correspondence catalogue to {out_path} in {time.time()-t0:.2f}s.")


if __name__ == "__main__":
    main()
