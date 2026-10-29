# Contributing GPU Compute & Certificates — Conway's 99-Graph Problem (`Class 6` Distributed Ledger)

Thank you for your interest in contributing to the open-science resolution of **John H. Conway's 99-Graph Problem** ($\Gamma = \mathrm{srg}(99, 14, 1, 2)$)!

All prime orders $p \in \{5, 7, 11, 13\}$, `p3_t1_fix33`, $\mathrm{Frob}(21)$, $18/19$ involution profiles, all `910 / 910` polygonally decomposable $(0,7,0)$ slice orbits (`1+5`, `4+2`, `3+3`, `2+2+2`), all `3 / 3` Seed Dodecagon $C_{12}$ ground-state orbits (`Orbits 0, 1670, 2118`), and **`270 / 2,670` (`10.11%`)** of the irreducible single-cycle `Class 6` orbits are already machine-certified `UNSAT`.

To close **100% of the symmetric universe ($|\mathrm{Aut}(\Gamma)| \ge 2$)** of Conway's 99-Graph Problem, **`2,400` `Class 6` orbits** remain, partitioned into **`164` Saddle-Free Super-Bundles (`IDs 20000..20170`)** across **`Shards 0..5`** (`~565 NVIDIA A100-hours` total with our **`Gen V.6g`** CUDA C++ solver).

We welcome external contributors with access to any modern CUDA GPU (**NVIDIA L4, RTX 3090 / 4090 / 5090, A100, H100, or B200**) to run one or more bundles (or partial batch slices) and submit the resulting certificates via a standard GitHub Pull Request. Every accepted certificate is permanently recorded in the repository and credited in the **Contributors & Compute Partners Ledger**.

---

## 1. How Our Zero-Trust Certificate Ledger Works (`Why Commits Are Conflict-Free`)

1. **Self-Contained Single-File Solver (`Gen V.6g`):**
   - [`verify-it-yourself/run_class6_trie_v6_solver.py`](verify-it-yourself/run_class6_trie_v6_solver.py) contains the complete C++/CUDA source code (`Gen V.6g`: `192 B` stack frame, `35,400 B` shared memory, `55,296` concurrent threads on A100, **`4.73×` faster than `Gen V.4`**) and the embedded `TRIE_B64` plan for all **`207` bundles (`2,670 / 2,670` `Class 6` orbits)**.
   - Requires only **Python 3.8+**, **`numpy`**, and the **NVIDIA CUDA compiler (`nvcc`)** (pre-installed on Google Colab, RunPod, Lambda, Vast.ai, and standard Linux GPU workstations).
2. **Atomic Per-Bundle Certificate Files (`Zero Merge Conflicts`):**
   - When a bundle finishes (`or checkpoints`), its result is stored in its own dedicated JSON file:
     ```text
     verify-it-yourself/class6_bundles/bundle_<BUNDLE_ID>.json
     ```
   - Because each bundle writes to its own `bundle_<BUNDLE_ID>.json` file, multiple contributors can submit Pull Requests for different bundles in parallel **without git merge conflicts**.
3. **Why Tree-Invariant Certificates (`reps, d4, d6, d8, sols=0`) Are Zero-Trust Verifiable:**
   - The solver is a **100% deterministic 4-level prefix-trie enumerator** (`0` heuristics, `0` random seeds, `0` floating-point branches) with a hard overflow guard (`Law M13`: `ovf_code != 0` aborts immediately).
   - For every batch of `252` canonical `L0` representatives, the solver counts the exact number of valid 4-vertex (`d4`), 6-vertex (`d6`), and 8-vertex (`d8`) prefix cones visited across the search tree.
   - Because `d4, d6, d8` are additive over all batches `1..N`, we can verify any submitted certificate in **~60 seconds on 1× A100** by running `1–2` deterministically chosen batches (`Spot-Check Protocol`) and confirming that `(d4, d6, d8_g7, sols=0)` match digit-for-digit.

---

## 2. Step-by-Step Guide: Running a Bundle & Submitting a Commit / PR

### Step 1: Pick an Available Bundle (or Shard)
Browse the master table in **[`docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md`](docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md)** (or inspect [`verify-it-yourself/class6_bundles_index.json`](verify-it-yourself/class6_bundles_index.json)):
- **Quick 15–30 minute test bundles (great for first PRs or single consumer GPUs / Colab L4):**
  Pick any `AVAILABLE` bundle in **Shard 5** (`e.g., Bundle 20165, 20166, 20167, 20168, 20169, 20170`, each `~0.14–0.35 A100-hours`).
- **Medium bundles (`~1–3 A100-hours`):**
  Pick any `AVAILABLE` bundle in **Shard 3, Shard 4, or Shard 5** (`IDs 20080..20164`).
- **Large high-multiplicity super-bundles (`~4–11 A100-hours`, `15–52` orbits at once):**
  Pick any `AVAILABLE` or `IN_PROGRESS` bundle in **Shard 0, Shard 1, or Shard 2** (`IDs 20000..20079`). Even if you only run **10–50 batches** (`MAX_BATCHES=20`) of a large bundle, you can commit the updated checkpoint!
- *(Optional)* Open a quick GitHub Issue or comment (e.g. `Claiming Bundle 20165..20170`) so others know you are running them.

### Step 2: Run the Solver on Your GPU (Local or Google Colab)
Clone your fork of the repository and run your chosen `BUNDLE_ID` (or `BUNDLE_LIST` / `SHARD_ID`):

```bash
# Example A: Certify a complete fast bundle (e.g. Bundle 20165)
BUNDLE_ID=20165 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee run_20165.log

# Example B: Certify multiple bundles in one run
BUNDLE_LIST=20165,20166,20167 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee run_batch.log

# Example C: Run 20 batches (~20 minutes on A100) of a large IN_PROGRESS bundle (e.g. Bundle 20008)
# The solver automatically resumes from the latest checkpoint in null2_k0_6_ckpts.json!
BUNDLE_ID=20008 MAX_BATCHES=20 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee run_20008_slice.log

# Example D: Run all remaining uncertified bundles in Shard 5 sequentially
SHARD_ID=5 python3 verify-it-yourself/run_class6_trie_v6_solver.py | tee shard_5.log
```

### Step 3: Ingest the Log & Update the Index
Run the indexer script on your log file:

```bash
python3 verify-it-yourself/index_class6_bundles.py --ingest run_20165.log
```

This command automatically:
1. Validates all `JSON_BATCH_CKPT:` and `JSON_BUNDLE_CERT:` records in `run_20165.log` (verifying `sols == 0` and monotonicity of checkpoints),
2. Creates/updates the atomic certificate file `verify-it-yourself/class6_bundles/bundle_20165.json`,
3. Updates `verify-it-yourself/null2_k0_6_partial.json` (for completed bundles) and `verify-it-yourself/null2_k0_6_ckpts.json` (for checkpoints),
4. Rebuilds [`verify-it-yourself/class6_bundles_index.json`](verify-it-yourself/class6_bundles_index.json) and [`docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md`](docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md).

### Step 4: Commit & Open a Pull Request
Commit the generated certificate and index files on a new branch and open a Pull Request:

```bash
git checkout -b cert/bundle-20165
git add verify-it-yourself/class6_bundles/ \
        verify-it-yourself/null2_k0_6_partial.json \
        verify-it-yourself/null2_k0_6_ckpts.json \
        verify-it-yourself/class6_bundles_index.json \
        docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md
git commit -m "cert(class6): certify bundle 20165 UNSAT via Gen V.6g"
git push origin cert/bundle-20165
```

In your Pull Request description, please include:
- **Bundle ID(s)** completed or checkpointed,
- **GPU model** used (e.g., `1× NVIDIA A100-SXM4-40GB`, `1× RTX 4090`, `Google Colab L4`),
- **How you would like to be credited** (GitHub handle, name/affiliation if desired) in the repository and completed paper/certificate.

---

## 3. Reviewer Verification Protocol (`How Maintainers Verify PRs`)

When a Pull Request is submitted, maintainers run two fast checks before merging:

1. **Deterministic Index & Invariant Audit (`< 2 seconds` on CPU):**
   ```bash
   python3 verify-it-yourself/index_class6_bundles.py
   sh verify-it-yourself/run_checks.sh
   ```
2. **Zero-Trust GPU Spot-Check (`~60 seconds` on GPU):**
   Generates 2 pseudo-random batch numbers seeded deterministically by the bundle's orbit list and verifies that the exact `(d4, d6, d8_g7, sols=0)` node counts match:
   ```bash
   python3 verify-it-yourself/index_class6_bundles.py --spot-check 20165
   ```
