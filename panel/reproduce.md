role: reproduce
context: fresh research subagent invoked via invoke_subagent
target_id: conway-99-graph
claim_targeted: p1 + p2

# Skeptic 1 (`reproduce`) Audit Report: `conway-99-graph` (Tracks `p2` and `p1`)

## 1. Execution & Standard-Library-Only Verification

- **Command executed:** `python3 -B verify.py` inside the `claim/` directory.
- **Standard library compliance:** Inspected `verify.py` imports (`collections`, `hashlib`, `itertools`, `json`, `os`, `sys`). No third-party packages, external SAT solvers, or external C binaries are imported or invoked during verification.
- **Execution result:** Completed in $\sim 18$ seconds with exit code `0` and final line `VERIFY: PASS`.

```text
[PASS] Positive non-vacuity control on srg(9, 4, 1, 2) = K_3 box K_3 (Encoding A & Encoding B)
[PASS] Track p2 p2_1_inner_matching_k14: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p2 p2_2_outer_bijection_k14: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p2 p2_3_inner_outer_balance_k14: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p2 p2_4_outer_pair_cn_k14: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p2 p2_5_srg9_uniqueness: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p7_fix1: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p5_t1_fix9: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p3_t1_fix33: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 frob21_z7_z3: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a0_b1_c6_fix73: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a0_b2_c5_fix51: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a0_b3_c4_fix33: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a0_b4_c3_fix19: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a0_b5_c2_fix9: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a0_b6_c1_fix3: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a1_b0_c5_fix53: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a1_b1_c4_fix35: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a1_b2_c3_fix21: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a1_b3_c2_fix11: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a1_b4_c1_fix5: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a1_b5_c0_fix3: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a2_b0_c3_fix23: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a2_b1_c2_fix13: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a2_b2_c1_fix7: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a2_b3_c0_fix5: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a3_b0_c1_fix9: Enc A & Enc B CNF membership + LRAT RUP verified
[PASS] Track p1 p2_a3_b1_c0_fix7: Enc A & Enc B CNF membership + LRAT RUP verified
All 54 UNSAT proofs (27 theorems x 2 encodings, 92259 RUP lemmas, 0 RAT lemmas) verified.
VERIFY: PASS
```

## 2. Independent CNF Re-Generation & Core Clause Membership Audit

- **Dual Cardinality Encoders:**
  - **Encoding A (`add_exact_sinz`):** Implements the Sinz (2005) linear sequential counter using $n \cdot k$ register variables $s_{i,j}$ with bidirectional implications enforcing $\sum_{i=1}^n L_i = k$.
  - **Encoding B (`add_exact_totalizer`):** Implements the Bailleux & Boufkhad (2003) binary tree unary totalizer recursively splitting $L$ into balanced subtrees and enforcing both upward at-most-$k$/sum propagation and downward sum-witness propagation.
- **54 Formulas Re-Generated From Scratch:**
  - `verify.py` constructs all $5$ Track `p2` propositions (`p2_1_inner_matching_k14`, `p2_2_outer_bijection_k14`, `p2_3_inner_outer_balance_k14`, `p2_4_outer_pair_cn_k14`, `p2_5_srg9_uniqueness`) and all $22$ Track `p1` automorphism exclusion cases (`p7_fix1`, `p5_t1_fix9`, `p3_t1_fix33`, `frob21_z7_z3`, and 18 involution profiles `p2_*`) under both Encoding A and Encoding B ($27 \times 2 = 54$ full CNFs).
- **Exact Clause Set Membership:**
  - For each of the $54$ proof objects, `verify.py` parses `*_core.cnf` via `parse_dimacs_clauses` and checks `cl in full_clause_set` against the freshly generated CNF from its corresponding encoder. All $150,439$ core clauses in Encoding A and $90,023$ core clauses in Encoding B are verified to be exact subsets of the freshly generated formulas.

## 3. Positive Non-Vacuity Control (`srg(9, 4, 1, 2)`)

- `verify_positive_control_srg9` builds the unblocked $\mathrm{srg}(9, 4, 1, 2) \cong K_3 \square K_3$ formulas (`add_blocking_clause=False`) for both Encoding A ($66$ variables, $200$ clauses) and Encoding B ($42$ variables, $146$ clauses), seeds the $6$ outer-edge variables with the explicit $4$-cycle truth assignment (`{1: True, 2: True, 3: False, 4: False, 5: True, 6: True}`), runs deterministic unit propagation across all auxiliary cardinality and conjunction variables, and confirms that every clause in both formulas is satisfied.

## 4. Pure-Python LRAT RUP Proof Checker & Hash Integrity Audit

- **Pure-Python LRAT RUP Checker (`verify_lrat_python`):**
  - Loads the $1$-indexed clauses of `*_core.cnf`, processes clause deletions (`d`) and RUP additions across single and multi-part `.lrat` files, explicitly rejects any negative hint (`any(h < 0 for h in hints)` $\implies$ error, enforcing $0$ RAT lemmas), verifies that every hint chain reaches a unit-propagation conflict from the negated lemma literals using only active clauses, and confirms that the empty clause `0` (`len(lemma_lits) == 0`) is derived in all $54$ proofs ($55,589$ RUP lemmas in Encoding A $+ 36,670$ RUP lemmas in Encoding B $= 92,259$ RUP lemmas total, $0$ RAT lemmas).
- **Hash & Artifact Cross-Check:**
  - All $54$ `core_cnf_sha256` and $88$ `core_lrat_sha256s` digests (`142` proof files total, each strictly $< 750\text{ KB}$) in `certificate.json` match the files on disk and are mutually distinct between Encoding A and Encoding B.
  - Every variable count, full clause count, core clause count, RUP lemma count, and cycle-structure statistic in `artifact.md` matches `certificate.json` and `verify.py` with zero discrepancies.

## 5. Asymmetric Algebraic, Spectral & 7-Triangle Triality Suite (`verify_lens3_asymmetric.py`)

- **Command executed:** `/opt/homebrew/bin/python3 attempts/lens3_asymmetric_algebraic_spectral/verify_lens3_asymmetric.py`.
- **Execution result:** Completed in $\sim 4.6$ seconds with exit code `0` and output `[PASS] Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7 & Phase 8 Algebraic, Spectral & Triality Verification Suite`.
- **Verified invariants (`lens3_output.json`):**
  1. Canonical $14 + 70$ decomposition $\mathbb{R}^{84} = \mathrm{col}(C^T) \oplus \ker(C)$ with $\mathrm{Spec}(A_{84}) = \{12^1, (-2)^6, 0^7\} \cup \{3^{40}, (-4)^{30}\}$.
  2. $6$-dimensional Hyperoctahedral $B_7 = \mathbb{Z}_2^7 \rtimes S_7$ Bose-Mesner association scheme on $\Gamma_2(x_0)$ with valencies $(1, 2, 1, 20, 20, 40)$ and irreducible decomposition $(1 \oplus 6 \oplus 7) \oplus (14 \oplus 35 \oplus 21)$.
  3. Triangle-Complement Spectral Duality Theorem and Exact Triangle Conservation Law $T(R_{60}) + T(S_{36}) = 32$.
  4. Coupled $42 \times 42$ matrix system $(B, D)$ for the 19th involution profile `(0, 7, 0)` ($g = -I_7 \in Z(B_7)$), $15$ canonical $B_5$-orbits of $H_{u_0}$ on $K_{2,2,2,2,2}$, Block-Orbit Exclusion Identity, and Global 7-Triangle Triality Coupling across $T_0, \dots, T_6$.
  5. Exact $3,580 \to 3,308 \to 3,294$ $B_6$-orbit sieve of matching pairs $(M_0^+, E_0)$ on $S_0$, $78$ canonical $B_5$-orbits of Type I block pairs $(H_0, H_1)$, and the Mod-2 Triple-Block Parity Obstruction Theorem ($k_{\text{type1}}(S_r) \le 2$ and $\Delta(G_{\text{type1}}) \le 2$).
  6. Full $3,294$-orbit $G_{36}(M_0^+, E_0) \succeq 0$ and $S_{12}^D(M_0^+, E_0) \succeq 0$ spectral & nullspace sieve ($\dim \ker(G_{36}) = 1 + c(M_0^+, E_0) \in \{2,3,4,5\}$, $\dim \ker(S_{12}^D) = 1$), Generalized Cycle-Orbit Exclusion Theorem, Universal $[F_{12}, D_{S_0, S_0}]$ Commutator Cancellation Law ($Z_D - Z_D^T = [D_{S_0, S_0}, X P_g X^T - K_{W_0}^{\text{true}}]$) verified on the explicit binary solution $X_{\text{sym}} \in \{0, 1\}^{12 \times 60}$, and complete fixed-$(M_0^+, E_0)$ full-$K_{W_0}$ sieve across all $62$ canonical $B_4$-orbits of $k_{\text{type1}}(S_0) = 2$ (`62/62 UNSAT` in `27.12s`).
  7. Complete $(k_{\text{type1}}(S_0), \dim \ker(G_{36}))$ classification of all $3,294$ surviving orbits (`k_type1=2: {5: 6, 4: 56}`, `k_type1=1: {4: 30, 3: 299}`, `k_type1=0: {4: 10, 3: 223, 2: 2670}`), multi-pair $k_{\text{type1}}(S_0) = 2$ closure across all $62 \times 10 = 620$ instances (`620/620 UNSAT` in `290.69s`), 2-Block Component $g$-Orbit Partition Law ($(2, 16, 12)$), 6-Way Disjoint Column Partition $R_{60} = h_0 \sqcup g(h_0) \sqcup h_1 \sqcup g(h_1) \sqcup W_0 \sqcup W_1$, and 4-row 60-bit Bitmask Hash-Join certifying `30/30 UNSAT` across all $\dim \ker(G_{36}) = 4$ orbits of $k_{\text{type1}}(S_0) = 1$ (`31.47s`), `80/80 UNSAT` across all $\binom{5}{2} \times 8 = 80$ uncanonicalized 2-block connected components (`67.86s`), and `9/9 UNSAT` across all two-component extensions for the $10 = \binom{3+3-1}{3}$ $\dim \ker(G_{36}) = 4$ orbits of $k_{\text{type1}}(S_0) = 0$ (`2.86s`).
  8. 7-Triangle Type-I Handshaking Law (`Law M11-B1`, forcing $7 - 2|E(H_{\text{type1}})| \in \{1, 3, 5, 7\}$ slices with $k_{\text{type1}}(S_r) = 0$), Global Involution Partner Classification (`Law M11-B2`: Type I / II / III), Connected Component Factorization Theorem ($(N_1, N_2, N_3, N_4, N_5, N_6) = (1, 3, 10, 56, 299, 2670)$), Unified Chiral Nullspace & Component Imbalance Law (`Law M11-A2`: $\sum_{i=0}^{11} X(i, c) = 2$, $\sum_{m=1}^{30} \delta_{B_q}(m)^2 = 4k(6-k)$, $\sum_{m=1}^{30} \delta_{B_p}(m)\delta_{B_q}(m) = -4k_p k_q$, verified across all $4,644$ connected components of all $3,294$ orbits), and native ARM64 `@numba.njit(parallel=True)` Bitmask Forward-Checking Backtracker certifying `30/30 UNSAT` on `Orbits 0..29` (`70.11s`) and `20/20 UNSAT` across all non-trivial `diag_zeros` strata (`dz = 12`: `1/1`, `dz = 8`: `5/5`, `dz = 6`: `5`, `dz = 4`: `9`, in `63.91s`; `42` distinct canonical $B_5$-orbits of $\dim \ker(G_{36}) = 3, k_{\text{type1}}(S_0) = 1$ certified `UNSAT`).
  9. **Five Master Theorems & 5-Graph Cayley Classification (`verify-it-yourself/ChiralNullspaceAndHandshaking.lean`, `verify-it-yourself/run_checks.sh`):**
     - **Command executed:** `lean verify-it-yourself/ChiralNullspaceAndHandshaking.lean && sh verify-it-yourself/run_checks.sh`.
     - **Execution result:** Compiles 2,734 lines (`67` theorem declarations across `Theorems 1–42b`) with `0 warnings`, `0 errors`, and `0 sorryAx`, and passes `28/28` checks in `verify-it-yourself/run_checks.sh`.
     - **Axiom & Kernel Audit of New Master Theorem Declarations (`#print axioms`):**
       - `odd_order_disjoint_star_bundle_structural` (`Theorem 34`): `does not depend on any axioms` (`0 axioms`).
       - `windmill_involution_unique_fixed_point_structural` (`Theorem 35a`): `does not depend on any axioms` (`0 axioms`).
       - `abelian_cayley_lambda_one_order_three_structural` (`Theorem 35b`): `does not depend on any axioms` (`0 axioms`).
       - `no_cherry_collision_srg_fiber_law` (`Theorem 36`): `[propext, Classical.choice, Quot.sound]`.
       - `higher_srg_seed_and_cayley_6273_obstructions_decide` (`Theorem 37`): `does not depend on any axioms` (`0 axioms`).
       - `odd_order_no_step_in_n1_structural` (`Theorem 38a`): `does not depend on any axioms` (`0 axioms`).
       - `odd_order_galois_eigenvalue_multiplicity_law` (`Theorem 38c`): `[propext, Quot.sound]`.
       - `schur_fiber_three_block_rr_sufficiency_and_matching_law` (`Theorem 41b`): `[propext, Classical.choice, Quot.sound]`.
       - `galois_quotient_and_induced_character_cayley_no_go_structural` (`Theorem 42a`): `[propext, Classical.choice, Quot.sound]`.
       - `complete_five_graph_cayley_classification_9_99_243_6273_494019_decide` (`Theorem 42b`): `does not depend on any axioms` (`0 axioms`).

pass: true
