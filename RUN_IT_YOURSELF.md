# Run It Yourself — `conway-99-graph` (`Gen V.6g` & Zero-Trust Verification Suite)

## 1. Quick Pure-Python Verification (`~18 Seconds`, Zero External Dependencies)

### Requirements
- Python 3.8+ (standard library only; zero external dependencies).

### One-Command Verification
From the repository root directory:

```sh
sh verify-it-yourself/run_checks.sh
```

Or directly via Python:

```sh
python3 -B verify-it-yourself/verify.py
```

### What `verify.py` Checks
1. **Positive Non-Vacuity Control (`srg(9, 4, 1, 2) = K_3 box K_3`):**
   Builds the unblocked forced-structure CNF on $\mathrm{srg}(9, 4, 1, 2)$ ($k = 4, M = 4$) under both Encoding A (Sinz 2005 Sequential Counter, $200$ clauses) and Encoding B (Bailleux & Boufkhad 2003 Binary Tree Totalizer, $146$ clauses), seeds the $6$ outer-edge variables with the unique outer $4$-cycle assignment of $K_3 \square K_3$, and verifies via deterministic unit propagation that every clause in both encodings is satisfied.
2. **Fresh CNF Re-Generation & Exact Core Clause Membership (54 Proofs across 27 Theorems):**
   Re-generates all $54$ full CNF clause sets from scratch (`5` Track `p2` propositions + `22` Track `p1` automorphism exclusions—including the open prime order $p = 7$ case `p7_fix1` and 18 of 19 involution profiles—across Encoding A and Encoding B) and checks that every clause in each `object/proofs/*_core.cnf` file is an exact member of the freshly generated CNF from its encoder.
3. **Pure-Python LRAT RUP Proof Verification (`92,259` RUP Lemmas, `0` RAT Lemmas):**
   Verifies all $54$ LRAT proofs in `object/proofs/*.lrat` (`55,589` RUP steps in Encoding A + `36,670` RUP steps in Encoding B = `92,259` RUP steps total) using a self-contained pure-Python LRAT Reverse Unit Propagation checker, confirming that `0` RAT lemmas are used and that every proof derives the empty clause `0`.
4. **Cryptographic Digest & Invariant Audit:**
   Verifies all SHA-256 digests (`142` proof files, each `< 750 KB`), variable/clause counts, and permutation cycle-structure invariants against `object/certificate.json`, terminating with `VERIFY: PASS`.

---

## 2. Seed Dodecagon $C_{12}$, Freckle Hierarchy & Decomposable Strata (`CPU Verifiers`)

```sh
# 1. Verify the Universal Seed Dodecagon C12 (Orbits 0, 1670, 2118) & 7-level freckle grading (~5.4s, pure Python/NumPy):
python3 verify-it-yourself/verify_seed_dodecagon_and_freckles.py

# 2. Verify zero-trust pure-Python cross-check oracles for strata 3+3 and 4+2:
python3 verify-it-yourself/test_naive_oracle_33_and_42.py

# 3. Run CPU refutation suites for decomposable strata (requires numpy + numba):
python3 verify-it-yourself/run_all_10_nullity4_k0_222_cpu.py   # 2+2+2 (10/10 orbits, ~11 min on M1 CPU)
python3 verify-it-yourself/run_all_10_nullity3_k0_33_cpu.py    # 3+3   (55/55 orbits, ~1.5 h on M1 CPU)
python3 verify-it-yourself/run_all_168_nullity3_k0_42_cpu.py   # 4+2   (168/168 orbits, ~6.3 h on M1 CPU)
python3 verify-it-yourself/run_all_299_nullity3_k1.py          # 1+5   (299/299 orbits, ~35 min on M1 CPU)
```

---

## 3. Running & Contributing `Class 6` GPU Bundles (`Gen V.6g` CUDA C++ Solver)

The irreducible single-cycle `Class 6` stratum (`2,670` canonical $B_6$-orbits) is partitioned into **`207` bundles** embedded inside [`verify-it-yourself/run_class6_trie_v6_solver.py`](verify-it-yourself/run_class6_trie_v6_solver.py):
- **`43` Certified `UNSAT` Bundles (`IDs 10000..10042`):** Covering **`270 / 2,670` (`10.11%`)** certified `Class 6` orbits (`verify-it-yourself/null2_k0_6_partial.json`).
- **`164` Remaining Saddle-Free Super-Bundles (`IDs 20000..20170` across `Shards 0..5`):** Covering the **`2,400` remaining `Class 6` orbits** (`~565 A100-hours` total with `Gen V.6g`).

Full bundle status tables and contributor instructions are in **[`docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md`](docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md)** and **[`CONTRIBUTING.md`](CONTRIBUTING.md)**.

```sh
# 1. Run a single bundle by ID on any CUDA GPU (requires Python 3, numpy, nvcc):
BUNDLE_ID=20165 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee run_20165.log

# 2. Run 10 batches (~10 minutes on A100) of an IN_PROGRESS bundle (auto-resumes from checkpoint):
BUNDLE_ID=20008 MAX_BATCHES=10 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee run_20008.log

# 3. Run all remaining uncertified bundles in a shard (SHARD_ID=0..5):
SHARD_ID=5 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee shard_5.log

# 4. Ingest a GPU run log and rebuild the bundle index & markdown ledger:
python3 verify-it-yourself/index_class6_bundles.py --ingest run_20165.log

# 5. Generate a deterministic 1-batch spot-check command for any bundle:
python3 verify-it-yourself/index_class6_bundles.py --spot-check 20008
```
