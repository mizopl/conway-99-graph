import json
import time
import numpy as np
import numba as nb
from itertools import combinations, permutations, product
from collections import defaultdict


@nb.njit(inline="always")
def popcnt64(x):
    x = x - ((x >> 1) & np.uint64(0x5555555555555555))
    x = (x & np.uint64(0x3333333333333333)) + ((x >> 2) & np.uint64(0x3333333333333333))
    x = (x + (x >> 4)) & np.uint64(0x0F0F0F0F0F0F0F0F)
    return int((x * np.uint64(0x0101010101010101)) >> np.uint64(56))


@nb.njit(inline="always")
def check_kw(ik, kw_req):
    if kw_req == 1:
        return ik != 0 and (ik & (ik - np.uint64(1))) == 0
    elif kw_req == 2:
        t = ik & (ik - np.uint64(1))
        return t != 0 and (t & (t - np.uint64(1))) == 0
    elif kw_req == 0:
        return ik == 0
    else:
        return popcnt64(ik) == kw_req


@nb.njit(parallel=True)
def solve_orbit_parallel(lengths, all_cands, Gp, KW0, y0_mask, ALL59):
    offsets = np.zeros(10, dtype=np.int32)
    for i in range(1, 10):
        offsets[i] = offsets[i - 1] + lengths[i - 1]

    n0 = lengths[0]
    nodes_arr = np.zeros(n0, dtype=np.int64)
    sols_arr = np.zeros(n0, dtype=np.int64)

    for root_i in nb.prange(n0):
        arena = np.empty((10, 45000), dtype=np.int32)
        dom_v = np.empty((10, 10), dtype=np.int32)
        dom_start = np.empty((10, 10), dtype=np.int32)
        dom_cnt = np.empty((10, 10), dtype=np.int32)
        cur_choice = np.empty(10, dtype=np.int32)
        u1_stack = np.empty(10, dtype=np.uint64)
        u2_stack = np.empty(10, dtype=np.uint64)
        pu_stack = np.empty(10, dtype=np.uint64)

        local_nodes = 0
        local_sols = 0

        xm = all_cands[root_i, 0]
        pm = all_cands[root_i, 2]
        u1 = y0_mask | xm
        u2 = y0_mask & xm
        pu = pm

        ptr = 0
        avail1 = np.uint64(0)
        avail2 = np.uint64(0)
        ok = True
        for j in range(1, 10):
            v_nxt = j
            gp_req = Gp[0, v_nxt]
            kw_req = KW0[0, v_nxt]
            st = offsets[j]
            en = st + lengths[j]
            ns_start = ptr
            dom_or = np.uint64(0)
            if gp_req == 0:
                forb_x = u2 | xm
                for k in range(st, en):
                    rxm = all_cands[k, 0]
                    if (rxm & forb_x) != 0 or (all_cands[k, 2] & pu) != 0:
                        continue
                    if check_kw(xm & all_cands[k, 1], kw_req):
                        arena[0, ptr] = k
                        ptr += 1
                        dom_or |= rxm
            else:
                for k in range(st, en):
                    rxm = all_cands[k, 0]
                    if (rxm & u2) != 0:
                        continue
                    ix = xm & rxm
                    if ix == 0 or (ix & (ix - np.uint64(1))) != 0:
                        continue
                    if (all_cands[k, 2] & pu) != 0:
                        continue
                    if check_kw(xm & all_cands[k, 1], kw_req):
                        arena[0, ptr] = k
                        ptr += 1
                        dom_or |= rxm
            ns_cnt = ptr - ns_start
            if ns_cnt == 0:
                ok = False
                break
            avail2 |= avail1 & dom_or
            avail1 |= dom_or
            dom_v[0, j - 1] = v_nxt
            dom_start[0, j - 1] = ns_start
            dom_cnt[0, j - 1] = ns_cnt

        if not ok:
            continue
        if ((u2 | avail1) & ALL59) != ALL59 or ((u1 | avail2) & ALL59) != ALL59:
            continue

        best_j = 0
        best_c = dom_cnt[0, 0]
        for j in range(1, 9):
            if dom_cnt[0, j] < best_c:
                best_c = dom_cnt[0, j]
                best_j = j
        if best_j != 0:
            tv, ts, tc = dom_v[0, 0], dom_start[0, 0], dom_cnt[0, 0]
            dom_v[0, 0], dom_start[0, 0], dom_cnt[0, 0] = (
                dom_v[0, best_j],
                dom_start[0, best_j],
                dom_cnt[0, best_j],
            )
            dom_v[0, best_j], dom_start[0, best_j], dom_cnt[0, best_j] = tv, ts, tc

        depth = 0
        cur_choice[0] = 0
        u1_stack[0] = u1
        u2_stack[0] = u2
        pu_stack[0] = pu
        local_nodes += 1

        while depth >= 0:
            n_doms = 9 - depth
            c_idx = cur_choice[depth]
            if c_idx >= dom_cnt[depth, 0]:
                depth -= 1
                continue
            cur_choice[depth] = c_idx + 1
            cand_k = arena[depth, dom_start[depth, 0] + c_idx]
            cxm = all_cands[cand_k, 0]
            cpm = all_cands[cand_k, 2]
            nu2 = u2_stack[depth] | (u1_stack[depth] & cxm)
            nu1 = u1_stack[depth] | cxm
            npu = pu_stack[depth] | cpm

            if n_doms == 1:
                local_nodes += 1
                local_sols += 1
                continue

            v_cur = dom_v[depth, 0]
            nxt_d = depth + 1
            n_rest = n_doms - 1
            n_ptr = 0
            av1 = np.uint64(0)
            av2 = np.uint64(0)
            sub_ok = True

            for j in range(1, n_doms):
                v_nxt = dom_v[depth, j]
                gp_req = Gp[v_cur, v_nxt]
                kw_req = KW0[v_cur, v_nxt]
                st = dom_start[depth, j]
                en = st + dom_cnt[depth, j]
                ns_st = n_ptr
                d_or = np.uint64(0)
                if gp_req == 0:
                    forb_x = nu2 | cxm
                    for p_i in range(st, en):
                        rk = arena[depth, p_i]
                        rxm = all_cands[rk, 0]
                        if (rxm & forb_x) != 0 or (all_cands[rk, 2] & npu) != 0:
                            continue
                        if check_kw(cxm & all_cands[rk, 1], kw_req):
                            arena[nxt_d, n_ptr] = rk
                            n_ptr += 1
                            d_or |= rxm
                else:
                    for p_i in range(st, en):
                        rk = arena[depth, p_i]
                        rxm = all_cands[rk, 0]
                        if (rxm & nu2) != 0:
                            continue
                        ix = cxm & rxm
                        if ix == 0 or (ix & (ix - np.uint64(1))) != 0:
                            continue
                        if (all_cands[rk, 2] & npu) != 0:
                            continue
                        if check_kw(cxm & all_cands[rk, 1], kw_req):
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
                if ((nu2 | av1) & ALL59) != ALL59 or ((nu1 | av2) & ALL59) != ALL59:
                    continue
                bj = 0
                bc = dom_cnt[nxt_d, 0]
                for j in range(1, n_rest):
                    if dom_cnt[nxt_d, j] < bc:
                        bc = dom_cnt[nxt_d, j]
                        bj = j
                if bj != 0:
                    tv, ts, tc = dom_v[nxt_d, 0], dom_start[nxt_d, 0], dom_cnt[nxt_d, 0]
                    dom_v[nxt_d, 0], dom_start[nxt_d, 0], dom_cnt[nxt_d, 0] = (
                        dom_v[nxt_d, bj],
                        dom_start[nxt_d, bj],
                        dom_cnt[nxt_d, bj],
                    )
                    dom_v[nxt_d, bj], dom_start[nxt_d, bj], dom_cnt[nxt_d, bj] = tv, ts, tc
                u1_stack[nxt_d] = nu1
                u2_stack[nxt_d] = nu2
                pu_stack[nxt_d] = npu
                cur_choice[nxt_d] = 0
                local_nodes += 1
                depth = nxt_d

        nodes_arr[root_i] = local_nodes
        sols_arr[root_i] = local_sols

    return np.sum(nodes_arr), np.sum(sols_arr)


def main():
    t_start = time.time()
    F12 = np.zeros((12, 12), dtype=int)
    for b in range(6):
        F12[2 * b, 2 * b + 1] = F12[2 * b + 1, 2 * b] = 1
    I12 = np.eye(12, dtype=int)
    J12 = np.ones((12, 12), dtype=int)

    def get_matchings(verts):
        if not verts:
            return [()]
        u = verts[0]
        res = []
        for i in range(1, len(verts)):
            v = verts[i]
            if (u // 2) != (v // 2):
                rem = verts[1:i] + verts[i + 1 :]
                for m in get_matchings(rem):
                    res.append(((u, v),) + m)
        return res

    all_5blk_matchings = [F12.copy()]
    for k_cross in (2, 3, 4, 5):
        for idxs in combinations(range(1, 6), k_cross):
            rem_b = [b for b in range(1, 6) if b not in idxs]
            verts = [2 * b + s for b in idxs for s in (0, 1)]
            for m in get_matchings(verts):
                M = np.zeros((12, 12), dtype=int)
                M[0, 1] = M[1, 0] = 1
                for b in rem_b:
                    M[2 * b, 2 * b + 1] = M[2 * b + 1, 2 * b] = 1
                for u, v in m:
                    M[u, v] = M[v, u] = 1
                all_5blk_matchings.append(M)

    B5_perms = []
    for bp in permutations(range(1, 6)):
        for flips in product((0, 1), repeat=5):
            p = [0, 1]
            for b_new, flip in zip(bp, flips):
                p.extend([2 * b_new + flip, 2 * b_new + (1 - flip)])
            B5_perms.append(np.array(p, dtype=int))

    def mat_to_bits(A):
        b = 0
        for i in range(12):
            for j in range(i + 1, 12):
                if A[i, j]:
                    b |= 1 << (i * 12 + j)
        return b

    def count_block_comps(M, E):
        adj = F12 | M | E
        vis = set()
        comps = 0
        for u in range(12):
            if u not in vis:
                comps += 1
                q = [u]
                vis.add(u)
                while q:
                    cur = q.pop()
                    for nxt in range(12):
                        if adj[cur, nxt] and nxt not in vis:
                            vis.add(nxt)
                            q.append(nxt)
        return comps

    seen = set()
    null3_k1 = []
    for M in all_5blk_matchings:
        for E in all_5blk_matchings:
            if np.any(F12[2:, 2:] * M[2:, 2:] * E[2:, 2:]):
                continue
            if count_block_comps(M, E) != 2:
                continue
            KW0 = 2 * J12 - F12 - E - M @ E - E @ M
            if KW0.min() < 0:
                continue
            mb = mat_to_bits(M)
            eb = mat_to_bits(E)
            if (mb, eb) in seen:
                continue
            for p in B5_perms:
                seen.add((mat_to_bits(M[np.ix_(p, p)]), mat_to_bits(E[np.ix_(p, p)])))
            Gp = 9 * I12 + J12 - M
            null3_k1.append((M, E, Gp, KW0))

    print(f"Total nullity 3 k_type1=1 orbits: {len(null3_k1)}", flush=True)

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
    W_j = [[c for c, (j1, j2) in enumerate(cols_60) if j in (j1, j2)] for j in range(12)]
    edge_orbits = []
    for b1 in range(1, 6):
        for b2 in range(b1 + 1, 6):
            edge_orbits.append((col_idx[(2 * b1, 2 * b2)], col_idx[(2 * b1 + 1, 2 * b2 + 1)]))
            edge_orbits.append((col_idx[(2 * b1, 2 * b2 + 1)], col_idx[(2 * b1 + 1, 2 * b2)]))
    deg = [0] * 12
    all_H0 = []
    cur = []

    def bt(idx):
        if len(cur) + (20 - idx) < 10:
            return
        if idx == 20:
            if len(cur) == 10 and all(deg[v] == 2 for v in range(2, 12)):
                all_H0.append(tuple(sorted(cur)))
            return
        for c in edge_orbits[idx]:
            u, v = cols_60[c]
            if deg[u] < 2 and deg[v] < 2 and len(cur) < 10:
                deg[u] += 1
                deg[v] += 1
                cur.append(c)
                bt(idx + 1)
                cur.pop()
                deg[u] -= 1
                deg[v] -= 1
        bt(idx + 1)

    bt(0)
    h0 = all_H0[0]
    h0_set = set(h0) | {g_col[c] for c in h0}
    rem_orbits = [orb for orb in edge_orbits if orb[0] not in h0_set]
    for bits in product((0, 1), repeat=10):
        cand = [rem_orbits[k][bits[k]] for k in range(10)]
        d = [0] * 12
        for c in cand:
            u, v = cols_60[c]
            d[u] += 1
            d[v] += 1
        if all(d[v] == 2 for v in range(2, 12)):
            h1 = tuple(sorted(cand))
            break
    orbs_30 = [(c, g_col[c]) for c in range(60) if c < g_col[c]]
    forb = set()
    for fixed_row in (h0, h1):
        for j in range(12):
            p_fixed = [c for c in fixed_row if j in cols_60[c]]
            if len(p_fixed) == 2:
                gc1, gc2 = g_col[p_fixed[0]], g_col[p_fixed[1]]
                forb.add((min(gc1, gc2), max(gc1, gc2)))

    row_cache = {}

    def get_valid_rows_5blk(target_deg_tuple, diag_kw):
        key = (target_deg_tuple, diag_kw)
        if key in row_cache:
            return row_cache[key]
        target_deg = list(target_deg_tuple)
        ok_cols = [c for c in range(60) if target_deg[cols_60[c][0]] > 0 and target_deg[cols_60[c][1]] > 0]
        s_h0 = [c for c in h0 if c in ok_cols]
        s_h1 = [c for c in h1 if c in ok_cols]
        s_gh0 = [g_col[c] for c in h0 if g_col[c] in ok_cols]
        s_gh1 = [g_col[c] for c in h1 if g_col[c] in ok_cols]
        s_w0 = [c for c in W_j[0] if c in ok_cols]
        s_w1 = [c for c in W_j[1] if c in ok_cols]
        valid_gh0 = [p for p in combinations(s_gh0, 2) if (min(p), max(p)) not in forb]
        valid_gh1 = [p for p in combinations(s_gh1, 2) if (min(p), max(p)) not in forb]
        valid_w0 = list(combinations(s_w0, 2))
        valid_w1 = list(combinations(s_w1, 2))
        first_half = defaultdict(list)
        for c0 in s_h0:
            for c1 in s_h1:
                for p0 in valid_gh0:
                    cols4 = (c0, c1, p0[0], p0[1])
                    d = [0] * 12
                    ok = True
                    for c in cols4:
                        u, v = cols_60[c]
                        d[u] += 1
                        d[v] += 1
                        if d[u] > target_deg[u] or d[v] > target_deg[v]:
                            ok = False
                            break
                    if ok:
                        first_half[tuple(d[2:])].append(cols4)
        second_half = defaultdict(list)
        for p1 in valid_gh1:
            for pw0 in valid_w0:
                for pw1 in valid_w1:
                    cols6 = p1 + pw0 + pw1
                    d = [0] * 12
                    ok = True
                    for c in cols6:
                        u, v = cols_60[c]
                        d[u] += 1
                        d[v] += 1
                        if d[u] > target_deg[u] or d[v] > target_deg[v]:
                            ok = False
                            break
                    if ok:
                        need = tuple(target_deg[j] - d[j] for j in range(2, 12))
                        if need in first_half:
                            second_half[need].append(cols6)
        valid_rows = []
        req_pairs = diag_kw // 2
        for need, list6 in second_half.items():
            for cols4 in first_half[need]:
                for cols6 in list6:
                    r = cols4 + cols6
                    r_set = set(r)
                    npairs = sum(1 for c in r if c < g_col[c] and g_col[c] in r_set)
                    if npairs != req_pairs:
                        continue
                    xm = 0
                    gxm = 0
                    pm = 0
                    for c in r:
                        xm |= 1 << c
                        gxm |= 1 << g_col[c]
                    for idx_m, (c, gc) in enumerate(orbs_30):
                        if c in r_set and gc in r_set:
                            pm |= 1 << idx_m
                    valid_rows.append((xm, gxm, pm))
        arr = np.array(valid_rows, dtype=np.uint64)
        row_cache[key] = arr
        return arr

    y0_mask = np.uint64(sum(1 << c for c in list(h0) + list(h1)))
    ALL59 = np.uint64(((1 << 60) - 1) & ~1)

    total_unsat = 0
    total_nodes = 0
    per_orbit = []
    t_solve_start = time.time()
    for idx in range(len(null3_k1)):
        M, E, Gp, KW0 = null3_k1[idx]
        dz = int(np.sum(np.diag(KW0) == 0))
        Delta0 = 2 * J12 - I12 - F12 - M - E @ F12
        L = [
            get_valid_rows_5blk(tuple(int(Delta0[i, j]) for j in range(12)), int(KW0[i, i]))
            for i in range(2, 12)
        ]
        order = np.argsort([len(x) for x in L])
        L_sorted = [L[o] for o in order]
        rows_idx = [2 + o for o in order]
        Gp_sub = Gp[np.ix_(rows_idx, rows_idx)].astype(np.int32)
        KW0_sub = KW0[np.ix_(rows_idx, rows_idx)].astype(np.int32)
        lengths = np.array([len(x) for x in L_sorted], dtype=np.int32)
        all_cands = np.vstack(L_sorted)
        t_orb = time.time()
        nodes, sols = solve_orbit_parallel(lengths, all_cands, Gp_sub, KW0_sub, y0_mask, ALL59)
        dt = time.time() - t_orb
        total_nodes += int(nodes)
        if sols == 0:
            total_unsat += 1
        per_orbit.append(
            {
                "orbit": idx,
                "dz": dz,
                "min_L": int(lengths[0]),
                "max_L": int(lengths[-1]),
                "nodes": int(nodes),
                "sols": int(sols),
                "time_s": round(dt, 4),
            }
        )
        if (idx + 1) % 25 == 0 or idx == len(null3_k1) - 1:
            elapsed = time.time() - t_solve_start
            print(
                f"[{idx+1:3d}/299] unsat={total_unsat}/{idx+1}, last_nodes={nodes:8d}, "
                f"last_t={dt:.3f}s, elapsed={elapsed:.2f}s, cache={len(row_cache)}",
                flush=True,
            )

    total_wall = time.time() - t_start
    summary = {
        "orbits_total": len(null3_k1),
        "unsat_certified": total_unsat,
        "sat_found": len(null3_k1) - total_unsat,
        "total_search_nodes": total_nodes,
        "unique_row_pools_cached": len(row_cache),
        "total_wall_time_s": round(total_wall, 2),
        "solve_wall_time_s": round(time.time() - t_solve_start, 2),
        "max_single_orbit_time_s": max(x["time_s"] for x in per_orbit),
        "min_single_orbit_time_s": min(x["time_s"] for x in per_orbit),
        "max_single_orbit_nodes": max(x["nodes"] for x in per_orbit),
        "min_single_orbit_nodes": min(x["nodes"] for x in per_orbit),
        "per_orbit": per_orbit,
    }
    out_p = "null3_k1_299_summary.json"
    with open(out_p, "w") as f:
        json.dump(summary, f, indent=2)
    print(
        f"DONE: Certified {total_unsat}/{len(null3_k1)} UNSAT in {total_wall:.2f}s "
        f"(total_nodes={total_nodes}, cache={len(row_cache)})",
        flush=True,
    )


if __name__ == "__main__":
    main()
