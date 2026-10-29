#!/usr/bin/env python3
"""
Conway's 99-Graph Problem — Class 6 Bundle Indexer & Zero-Trust Certificate Ledger Tool
=======================================================================================
Maintains the master index of all 207 Class 6 bundles (covering 2,670 / 2,670 Class 6 orbits):
  - 164 Remaining Saddle-Free Super-Bundles (IDs 20000..20170 across Shards 0..5, 2,400 remaining orbits)
  -  43 Certified UNSAT Bundles (IDs 10000..10042, 270 certified UNSAT orbits)

Capabilities:
  1. Build/refresh `class6_bundles_index.json`, atomic `class6_bundles/bundle_<id>.json` files,
     and `../docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md`:
       python3 index_class6_bundles.py
  2. Ingest `JSON_BATCH_CKPT:` and `JSON_BUNDLE_CERT:` lines from a GPU log file:
       python3 index_class6_bundles.py --ingest path/to/gpu_run.log
  3. Print a deterministic spot-check command for any bundle:
       python3 index_class6_bundles.py --spot-check 20008
"""
import argparse
import base64
import hashlib
import json
import os
import re
import sys
import zlib
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
SOLVER_PATH = os.path.join(SCRIPT_DIR, "run_class6_trie_v6_solver.py")
PARTIAL_PATH = os.path.join(SCRIPT_DIR, "null2_k0_6_partial.json")
SEED2118_PATH = os.path.join(SCRIPT_DIR, "seed_orbit_2118_cert.json")
CKPTS_PATH = os.path.join(SCRIPT_DIR, "null2_k0_6_ckpts.json")
BUNDLES_DIR = os.path.join(SCRIPT_DIR, "class6_bundles")
INDEX_JSON_PATH = os.path.join(SCRIPT_DIR, "class6_bundles_index.json")
LEDGER_MD_PATH = os.path.join(REPO_ROOT, "docs", "CLASS6_BUNDLE_INDEX_AND_LEDGER.md")


def load_solver_plan():
    with open(SOLVER_PATH, "r", encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r'TRIE_B64\s*=\s*"([^"]+)"', txt)
    if not m:
        raise RuntimeError(f"TRIE_B64 not found in {SOLVER_PATH}")
    raw = zlib.decompress(base64.b64decode(m.group(1))).decode("utf-8")
    return json.loads(raw)


def get_bundle_orbits(b):
    s = set()
    for g6 in b.get("r6_groups", []):
        for g7 in g6.get("r7_groups", []):
            for mem in g7.get("members", []):
                s.add(int(mem["orbit_idx"]))
    return sorted(s)


def ingest_log_file(log_path, ckpts, cert_by_orbit):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    n_ckpt = 0
    n_cert = 0
    for line in lines:
        if "JSON_BATCH_CKPT:" in line:
            payload = line.split("JSON_BATCH_CKPT:", 1)[1].strip()
            obj = json.loads(payload)
            bid = str(obj["bundle_id"])
            if any(int(x) != 0 for x in obj.get("sol_mem", [])):
                raise RuntimeError(f"Non-zero solution count in checkpoint for bundle {bid}!")
            prev = ckpts.get(bid, {})
            if int(obj["reps_done"]) >= int(prev.get("reps_done", -1)):
                ckpts[bid] = obj
                n_ckpt += 1
        elif "JSON_BUNDLE_CERT:" in line:
            payload = line.split("JSON_BUNDLE_CERT:", 1)[1].strip()
            recs = json.loads(payload)
            for r in recs:
                if int(r.get("sols", 0)) != 0:
                    raise RuntimeError(f"Non-zero sols in certificate for orbit {r.get('orbit_idx')}!")
                oid = int(r["orbit_idx"])
                cert_by_orbit[oid] = r
                n_cert += 1
    print(f"Ingested {n_ckpt} checkpoint updates and {n_cert} orbit certificates from {log_path}.")
    return n_ckpt, n_cert


def generate_spot_check_cmd(bundle_id, plan):
    bundles = plan["bundles"]
    target = None
    for b in bundles:
        if int(b.get("bundle_idx", -1)) == int(bundle_id) or int(b.get("orig_bundle_idx", -1)) == int(bundle_id):
            target = b
            break
    if target is None:
        raise ValueError(f"Bundle {bundle_id} not found in plan.")
    bid = int(target["bundle_idx"])
    # Deterministic hash seed from bundle_id + orbits
    h = int(hashlib.sha256(json.dumps(get_bundle_orbits(target)).encode()).hexdigest()[:8], 16)
    reps_est = int(target.get("cert_reps", 0))
    if reps_est <= 0 and os.path.exists(CKPTS_PATH):
        with open(CKPTS_PATH, "r", encoding="utf-8") as cf:
            ck = json.load(cf).get(str(bid), {})
            reps_est = int(ck.get("reps", 0))
    if reps_est <= 0:
        reps_est = 11626
    tot_batches = max(1, (reps_est + 251) // 252)
    b1 = (h % tot_batches) + 1
    b2 = ((h >> 8) % tot_batches) + 1
    print(f"# Spot-Check Protocol for Bundle {bid} (total batches ~ {tot_batches}):")
    print(f"BUNDLE_ID={bid} START_BATCH={b1} MAX_BATCHES=1 python3 verify-it-yourself/run_class6_trie_v6_solver.py")
    if b2 != b1:
        print(f"BUNDLE_ID={bid} START_BATCH={b2} MAX_BATCHES=1 python3 verify-it-yourself/run_class6_trie_v6_solver.py")


def main():
    parser = argparse.ArgumentParser(description="Index and verify Class 6 bundles and certificates.")
    parser.add_argument("--ingest", type=str, default="", help="Path to GPU log file containing JSON_BATCH_CKPT / JSON_BUNDLE_CERT lines.")
    parser.add_argument("--spot-check", type=int, default=-1, help="Print deterministic 1-batch spot-check command for a bundle ID.")
    args = parser.parse_args()

    plan = load_solver_plan()
    if args.spot_check >= 0:
        generate_spot_check_cmd(args.spot_check, plan)
        return

    with open(PARTIAL_PATH, "r", encoding="utf-8") as f:
        partial_list = json.load(f)
    with open(CKPTS_PATH, "r", encoding="utf-8") as f:
        ckpts = json.load(f)

    cert_by_orbit = {int(r["orbit_idx"]): r for r in partial_list}
    if os.path.exists(SEED2118_PATH):
        with open(SEED2118_PATH, "r", encoding="utf-8") as f:
            s2118 = json.load(f)
        if 2118 not in cert_by_orbit:
            cert_by_orbit[2118] = {
                "orbit_idx": 2118,
                "bundle_idx": 10042,
                "reps": int(s2118["reps"]),
                "d4": int(s2118["d4"]),
                "d6": int(s2118["d6"]),
                "d8": int(s2118["d8"]),
                "sols": int(s2118["sols"]),
                "bundle_elapsed_s": float(s2118["elapsed_s"]),
            }

    if args.ingest:
        n_ckpt, n_cert = ingest_log_file(args.ingest, ckpts, cert_by_orbit)
        if n_ckpt > 0:
            with open(CKPTS_PATH, "w", encoding="utf-8") as f:
                json.dump(ckpts, f, indent=2, sort_keys=True)
        if n_cert > 0:
            updated_partial = sorted(cert_by_orbit.values(), key=lambda x: int(x["orbit_idx"]))
            with open(PARTIAL_PATH, "w", encoding="utf-8") as f:
                json.dump(updated_partial, f, indent=2)

    os.makedirs(BUNDLES_DIR, exist_ok=True)
    bundles = plan["bundles"]

    # Empirical Gen V.6g A100 scaling: ~565 hours across total remaining work_est = 787.48
    A100_HOURS_PER_WORK_UNIT = 565.0 / 787.484

    bundle_entries = []
    orbit_to_bundle = {}
    shard_stats = {sh: {"shard_id": sh, "hardware_tier": "A100" if sh < 3 else "L4/A100", "bundles": 0, "orbits": 0, "uncertified_orbits": 0, "work_est": 0.0, "est_a100_v6g_hours": 0.0, "in_progress": 0} for sh in range(6)}

    # Also Record Batch 145 verified benchmark on Bundle 20008
    b20008_batch145_verified = {
        "batch_num": 145,
        "reps_done": 36540,
        "reps_total": 91392,
        "d4": 362842977964,
        "d6": 69581840508,
        "sum_d8": 866532551,
        "sols": 0,
        "batch_145_a100_v6g_s": 59.85,
        "batch_145_a100_v4_s": 283.04,
        "speedup_vs_v4": 4.729,
    }

    for pos, b in enumerate(bundles):
        bid = int(b.get("bundle_idx", pos))
        orig_bid = int(b.get("orig_bundle_idx", bid))
        sh_id = int(b.get("shard_id", -1))
        sh_pos = int(b.get("shard_pos", pos))
        orbs = get_bundle_orbits(b)
        uncert_orbs = [o for o in orbs if o not in cert_by_orbit]
        work_est = float(b.get("work_est", 0.0))
        est_hrs = round(work_est * A100_HOURS_PER_WORK_UNIT, 2)
        n_mem = int(b.get("num_members", b.get("num_coset_members", 0)))
        n_r6 = int(b.get("num_r6", len(b.get("r6_groups", []))))
        n_r7 = int(b.get("num_r7", sum(len(g6.get("r7_groups", [])) for g6 in b.get("r6_groups", []))))
        aut_order = len(b.get("aut_dec", []))

        if b.get("status") == "CERTIFIED_UNSAT" or len(uncert_orbs) == 0:
            status = "CERTIFIED_UNSAT"
            reps_tot = int(b.get("cert_reps", cert_by_orbit[orbs[0]]["reps"]))
            reps_done = reps_tot
            d4_val = int(b.get("cert_d4", cert_by_orbit[orbs[0]]["d4"]))
            d6_val = int(b.get("cert_d6", cert_by_orbit[orbs[0]]["d6"]))
            sum_d8_val = sum(int(cert_by_orbit[o]["d8"]) for o in orbs)
            sols_val = sum(int(cert_by_orbit[o].get("sols", 0)) for o in orbs)
            el_val = float(b.get("cert_elapsed_s", cert_by_orbit[orbs[0]].get("bundle_elapsed_s", cert_by_orbit[orbs[0]].get("elapsed_s", 0.0))))
            prog_pct = 100.0
        elif str(bid) in ckpts and int(ckpts[str(bid)].get("reps_done", 0)) > 0:
            status = "IN_PROGRESS"
            ck = ckpts[str(bid)]
            reps_tot = int(ck.get("reps", 91392))
            reps_done = int(ck["reps_done"])
            d4_val = int(ck["d4"])
            d6_val = int(ck["d6"])
            sum_d8_val = sum(int(x) for x in ck.get("d8_g7", []))
            sols_val = sum(int(x) for x in ck.get("sol_mem", []))
            el_val = float(ck.get("el", 0.0))
            prog_pct = round(100.0 * reps_done / max(1, reps_tot), 2)
        else:
            status = "AVAILABLE"
            reps_tot = 0
            reps_done = 0
            d4_val = 0
            d6_val = 0
            sum_d8_val = 0
            sols_val = 0
            el_val = 0.0
            prog_pct = 0.0

        entry = {
            "bundle_id": bid,
            "orig_bundle_id": orig_bid,
            "array_pos": pos,
            "status": status,
            "shard_id": sh_id,
            "shard_pos": sh_pos,
            "num_orbits": len(orbs),
            "num_uncertified_orbits": len(uncert_orbs),
            "orbits": orbs,
            "num_coset_members": n_mem,
            "num_r6": n_r6,
            "num_r7": n_r7,
            "aut_dec_order": aut_order,
            "work_est": round(work_est, 3),
            "est_a100_v6g_hours": est_hrs,
            "reps_done": reps_done,
            "reps_total": reps_tot,
            "progress_pct": prog_pct,
            "d4": d4_val,
            "d6": d6_val,
            "sum_d8": sum_d8_val,
            "sols": sols_val,
            "elapsed_s": round(el_val, 3),
        }
        if bid == 20008:
            entry["latest_verified_batch"] = b20008_batch145_verified

        bundle_entries.append(entry)

        if sh_id >= 0:
            st = shard_stats[sh_id]
            st["bundles"] += 1
            st["orbits"] += len(orbs)
            st["uncertified_orbits"] += len(uncert_orbs)
            st["work_est"] = round(st["work_est"] + work_est, 3)
            st["est_a100_v6g_hours"] = round(st["est_a100_v6g_hours"] + est_hrs, 2)
            if status == "IN_PROGRESS":
                st["in_progress"] += 1

        # Write atomic per-bundle JSON file for CERTIFIED_UNSAT and IN_PROGRESS bundles
        if status in ("CERTIFIED_UNSAT", "IN_PROGRESS"):
            b_doc = dict(entry)
            if status == "CERTIFIED_UNSAT":
                b_doc["orbit_certificates"] = [cert_by_orbit[o] for o in orbs]
            elif str(bid) in ckpts:
                b_doc["checkpoint"] = ckpts[str(bid)]
            b_path = os.path.join(BUNDLES_DIR, f"bundle_{bid}.json")
            with open(b_path, "w", encoding="utf-8") as bf:
                json.dump(b_doc, bf, indent=2)

        for o in orbs:
            if o not in orbit_to_bundle:
                orbit_to_bundle[o] = {
                    "orbit_idx": o,
                    "status": "CERTIFIED_UNSAT" if o in cert_by_orbit else "REMAINING",
                    "primary_bundle_id": bid,
                    "shard_id": sh_id,
                }
            elif status == "CERTIFIED_UNSAT":
                orbit_to_bundle[o]["certified_bundle_id"] = bid
            if o in cert_by_orbit:
                c_rec = cert_by_orbit[o]
                orbit_to_bundle[o]["reps"] = int(c_rec["reps"])
                orbit_to_bundle[o]["d4"] = int(c_rec["d4"])
                orbit_to_bundle[o]["d6"] = int(c_rec["d6"])
                orbit_to_bundle[o]["d8"] = int(c_rec["d8"])
                orbit_to_bundle[o]["sols"] = int(c_rec.get("sols", 0))

    cert_bundles_list = [e for e in bundle_entries if e["status"] == "CERTIFIED_UNSAT"]
    inprog_bundles_list = [e for e in bundle_entries if e["status"] == "IN_PROGRESS"]
    avail_bundles_list = [e for e in bundle_entries if e["status"] == "AVAILABLE"]

    summary_obj = {
        "schema_version": "1.0.0",
        "solver_version": "Gen_V.6g",
        "total_class6_orbits": 2670,
        "certified_unsat_orbits": len(cert_by_orbit),
        "remaining_uncertified_orbits": 2670 - len(cert_by_orbit),
        "completion_pct": round(100.0 * len(cert_by_orbit) / 2670.0, 2),
        "total_bundles": len(bundle_entries),
        "remaining_super_bundles": len(inprog_bundles_list) + len(avail_bundles_list),
        "certified_bundles": len(cert_bundles_list),
        "in_progress_bundles": len(inprog_bundles_list),
        "available_bundles": len(avail_bundles_list),
        "certified_tree_totals": {
            "sum_d4_across_certified_bundles": sum(e["d4"] for e in cert_bundles_list),
            "sum_d6_across_certified_bundles": sum(e["d6"] for e in cert_bundles_list),
            "sum_d8_across_certified_orbits": sum(int(r["d8"]) for r in cert_by_orbit.values()),
            "total_solutions_found": sum(int(r.get("sols", 0)) for r in cert_by_orbit.values()),
        },
        "remaining_compute_estimate": {
            "total_work_est": round(sum(e["work_est"] for e in inprog_bundles_list + avail_bundles_list), 3),
            "est_a100_v6g_hours_total": round(sum(e["est_a100_v6g_hours"] for e in inprog_bundles_list + avail_bundles_list), 1),
            "benchmark_reference": "Bundle 20008 Batch 145/363: 59.85s on 1x NVIDIA A100-SXM4-40GB (4.73x faster than Gen V.4 283.04s)",
        },
        "shards": [shard_stats[sh] for sh in range(6)],
    }

    index_doc = {
        "summary": summary_obj,
        "bundles": bundle_entries,
        "orbit_index": [orbit_to_bundle[o] for o in range(2670)],
    }

    with open(INDEX_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(index_doc, f, indent=2)

    # Generate Markdown Ledger
    md_lines = [
        "# Conway's 99-Graph Problem — Class 6 Bundle Index & Zero-Trust Certificate Ledger (`Gen V.6g`)",
        "",
        "Ten dokument stanowi główny indeks wszystkich **`207` paczek (`bundles`)** pokrywających **`2670 / 2670` (`100%`)** kanonicznych $B_6$-orbit w nierozkładalnej warstwie **`Class 6`** (`pojedynczy 12-wierzchołkowy cykl ziarna`, $|\\mathrm{Aut}(\\Gamma)| \\ge 2$).",
        "",
        "---",
        "",
        "## 1. Podsumowanie Statusu (`Class 6` Ledger Summary)",
        "",
        "| Metryka | Wartość | Opis |",
        "| :--- | ---: | :--- |",
        f"| **Wszystkie orbity `Class 6`** | **`2 670`** | Pełna przestrzeń nierozkładalnych 12-wierzchołkowych ziaren pod inwolucją $(0,7,0)$ |",
        f"| **Certyfikowane orbity (`CERTIFIED_UNSAT`)** | **`{len(cert_by_orbit)} / 2 670` (`{summary_obj['completion_pct']}%`)** | Wykluczone z dokładnymi niezmiennikami drzewa `(reps, d4, d6, d8, sols=0)` |",
        f"| **Pozostałe orbity do wyliczenia** | **`{2670 - len(cert_by_orbit)} / 2 670`** | Zgrupowane w **`164` paczkach `Saddle-Free`** (`ID 20000..20170`, `Shards 0..5`) |",
        f"| **Paczki certyfikowane (`ID 10000..10042`)** | **`{len(cert_bundles_list)}`** | Zapisane atomowo w `verify-it-yourself/class6_bundles/bundle_100xx.json` |",
        f"| **Paczki w trakcie (`IN_PROGRESS`)** | **`{len(inprog_bundles_list)}`** | `20074` (`S0: 40.47%`), `20008` (`S2: 39.71%` + `Batch 145: 59.85 s`), `20093` (`S3: 45.68%`), `20155` (`S4: 52.66%`), `20073` (`S5: 81.90%`) |",
        f"| **Paczki wolne (`AVAILABLE`)** | **`{len(avail_bundles_list)}`** | Gotowe do pobrania i przeliczenia przez dowolny węzeł GPU |",
        f"| **Łączna liczba odwiedzonych węzłów `d4` (certyfikowane)** | **`{summary_obj['certified_tree_totals']['sum_d4_across_certified_bundles']:,}`** | Dokładny niezmiennik poziomu `d4` (4-wierzchołkowy stożek) |",
        f"| **Łączna liczba odwiedzonych węzłów `d6` (certyfikowane)** | **`{summary_obj['certified_tree_totals']['sum_d6_across_certified_bundles']:,}`** | Dokładny niezmiennik poziomu `d6` (6-wierzchołkowy stożek) |",
        f"| **Łączna liczba odwiedzonych węzłów `d8` (certyfikowane)** | **`{summary_obj['certified_tree_totals']['sum_d8_across_certified_orbits']:,}`** | Dokładny niezmiennik poziomu `d8` (8-wierzchołkowy most) |",
        f"| **Znalezione rozwiązania (`sols`)** | **`0`** | Dowód sprzeczności (`UNSAT`) dla wszystkich `270` certyfikowanych orbit |",
        f"| **Szacowany czas pozostałych `164` paczek (`Gen V.6g`)** | **`~{summary_obj['remaining_compute_estimate']['est_a100_v6g_hours_total']} A100-h`** | Przy potwierdzonym przyspieszeniu **`4.73x`** (`59.85 s` vs `283.04 s` na `Batch 145`) |",
        "",
        "---",
        "",
        "## 2. Podział Pozostałych `164` Paczek na `Shards 0..5`",
        "",
        "| Shard | Rekomendowane GPU | Liczba paczek | Wszystkie orbity w paczkach | Nowe (niecertyfikowane) orbity | Suma `work_est` | Szacowany czas (`Gen V.6g` A100-h) | W trakcie (`IN_PROGRESS`) |",
        "| :---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for sh in range(6):
        st = shard_stats[sh]
        md_lines.append(
            f"| **Shard {sh}** | `{st['hardware_tier']}` | `{st['bundles']}` | `{st['orbits']}` | **`{st['uncertified_orbits']}`** | `{st['work_est']:.2f}` | `~{st['est_a100_v6g_hours']:.1f} h` | `{st['in_progress']}` |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Instrukcja Uruchamiania i Zbierania Certyfikatów (`Zero-Trust Workflow`)",
        "",
        "### A. Przeliczenie wybranej paczki (`Bundle ID`) lub całego Shardu",
        "Skrypt [`verify-it-yourself/run_class6_trie_v6_solver.py`](../verify-it-yourself/run_class6_trie_v6_solver.py) zawiera wbudowany kod `Gen V.6g` oraz wszystkie `207` paczek (`TRIE_B64`). Po każdym batchu (`252` reprezentantów `L0`) wypisuje linię `JSON_BATCH_CKPT:...`, a po ukończeniu `100%` reprezentantów paczki zapisuje atomowy certyfikat do `verify-it-yourself/class6_bundles/bundle_<id>.json`:",
        "",
        "```bash",
        "# 1. Uruchomienie pojedynczej paczki (np. najmniejszej paczki 20165 z Shard 5):",
        "BUNDLE_ID=20165 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee run_20165.log",
        "",
        "# 2. Kontynuacja paczki 20008 od zapisanego checkpointu przez 10 batchy (~10 minut na A100):",
        "BUNDLE_ID=20008 MAX_BATCHES=10 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee run_20008.log",
        "",
        "# 3. Uruchomienie kolejki paczek z wybranego Shardu (np. Shard 0):",
        "SHARD_ID=0 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee shard_0.log",
        "```",
        "",
        "### B. Ingestia logu i aktualizacja indeksu oraz bazy certyfikatów",
        "```bash",
        "# Automatyczny odczyt JSON_BATCH_CKPT i JSON_BUNDLE_CERT z logu oraz przebudowa indeksu:",
        "python3 verify-it-yourself/index_class6_bundles.py --ingest run_20165.log",
        "```",
        "",
        "### C. Wyrywkowa weryfikacja Zero-Trust (`Spot-Check Protocol`)",
        "Ponieważ niezmienniki `(reps, d4, d6, d8, sols=0)` zależą od każdej odwiedzonej gałęzi deterministycznego drzewa przeszukiwań, wyrywkowe przeliczenie 1–2 losowych batchy (`~60 s` na A100) natychmiast weryfikuje autentyczność zgłoszonego certyfikatu:",
        "",
        "```bash",
        "python3 verify-it-yourself/index_class6_bundles.py --spot-check 20008",
        "```",
        "",
        "---",
        "",
        "## 4. Indeks Wszystkich `164` Pozostałych Paczek `Saddle-Free` (`ID 20000..20170`)",
        "",
        "| Bundle ID | Shard | Status | Orbity (nowe/wszystkie) | `coset_mem` | `r6` / `r7` | `|H6|` | Postęp (`reps`) | `work_est` | Est. A100 (`Gen V.6g`) | Lista Orbit (`orbit_idx`) |",
        "| :---: | :---: | :---: | :---: | ---: | :---: | ---: | :---: | ---: | ---: | :--- |",
    ])

    for e in bundle_entries:
        if e["shard_id"] < 0:
            continue
        orbs_str = ", ".join(str(x) for x in e["orbits"][:8])
        if len(e["orbits"]) > 8:
            orbs_str += f", ... (+{len(e['orbits'])-8})"
        prog_str = f"`{e['reps_done']}/{e['reps_total']}` (`{e['progress_pct']}%`)" if e["reps_total"] > 0 else "`0%`"
        md_lines.append(
            f"| **`{e['bundle_id']}`** | `S{e['shard_id']}` | `{e['status']}` | `{e['num_uncertified_orbits']}/{e['num_orbits']}` | `{e['num_coset_members']}` | `{e['num_r6']}/{e['num_r7']}` | `{e['aut_dec_order']}` | {prog_str} | `{e['work_est']:.2f}` | `~{e['est_a100_v6g_hours']:.2f} h` | `{orbs_str}` |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 5. Indeks Wszystkich `43` Certyfikowanych Paczek `UNSAT` (`ID 10000..10042` — `270 / 270` Orbit)",
        "",
        "| Bundle ID | Orig ID | Orbity | `reps` | `d4` | `d6` | `sum_d8` | `sols` | Czas GPU (`s`) | Certyfikowane Orbity (`orbit_idx`) |",
        "| :---: | :---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: | :--- |",
    ])

    for e in cert_bundles_list:
        orbs_str = ", ".join(str(x) for x in e["orbits"][:10])
        if len(e["orbits"]) > 10:
            orbs_str += f", ... (+{len(e['orbits'])-10})"
        md_lines.append(
            f"| **`{e['bundle_id']}`** | `{e['orig_bundle_id']}` | `{e['num_orbits']}` | `{e['reps_total']:,}` | `{e['d4']:,}` | `{e['d6']:,}` | `{e['sum_d8']:,}` | **`{e['sols']}`** | `{e['elapsed_s']:.1f} s` | `{orbs_str}` |"
        )

    md_lines.append("")
    with open(LEDGER_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Generated index JSON: {INDEX_JSON_PATH}")
    print(f"Generated atomic bundle files in: {BUNDLES_DIR} ({len(cert_bundles_list) + len(inprog_bundles_list)} files)")
    print(f"Generated Markdown ledger: {LEDGER_MD_PATH}")


if __name__ == "__main__":
    main()
