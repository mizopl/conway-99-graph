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
- **Execution result:** Completed in $\sim 6.5$ seconds with exit code `0` and output `[PASS] Phase 2, Phase 3, Phase 4 & Phase 5 Algebraic, Spectral & Triality Verification Suite`.
- **Verified invariants (`lens3_output.json`):**
  1. Canonical $14 + 70$ decomposition $\mathbb{R}^{84} = \mathrm{col}(C^T) \oplus \ker(C)$ with $\mathrm{Spec}(A_{84}) = \{12^1, (-2)^6, 0^7\} \cup \{3^{40}, (-4)^{30}\}$.
  2. $6$-dimensional Hyperoctahedral $B_7 = \mathbb{Z}_2^7 \rtimes S_7$ Bose-Mesner association scheme on $\Gamma_2(x_0)$ with valencies $(1, 2, 1, 20, 20, 40)$ and irreducible decomposition $(1 \oplus 6 \oplus 7) \oplus (14 \oplus 35 \oplus 21)$.
  3. Triangle-Complement Spectral Duality Theorem and Exact Triangle Conservation Law $T(R_{60}) + T(S_{36}) = 32$.
  4. Coupled $42 \times 42$ matrix system $(B, D)$ for the 19th involution profile `(0, 7, 0)` ($g = -I_7 \in Z(B_7)$), $15$ canonical $B_5$-orbits of $H_{u_0}$ on $K_{2,2,2,2,2}$, Block-Orbit Exclusion Identity, and Global 7-Triangle Triality Coupling across $T_0, \dots, T_6$.
  5. Exact $3,580 \to 3,308 \to 3,294$ $B_6$-orbit sieve of matching pairs $(M_0^+, E_0)$ on $S_0$, $78$ canonical $B_5$-orbits of Type I block pairs $(H_0, H_1)$, and the Mod-2 Triple-Block Parity Obstruction Theorem ($k_{\text{type1}}(S_r) \le 2$ and $\Delta(G_{\text{type1}}) \le 2$).
  6. Full $3,294$-orbit $G_{36}(M_0^+, E_0) \succeq 0$ and $S_{12}^D(M_0^+, E_0) \succeq 0$ spectral & nullspace sieve ($\dim \ker(G_{36}) = 1 + c(M_0^+, E_0) \in \{2,3,4,5\}$, $\dim \ker(S_{12}^D) = 1$), Generalized Cycle-Orbit Exclusion Theorem, and Universal $[F_{12}, D_{S_0, S_0}]$ Commutator Cancellation Law ($Z_D - Z_D^T = [D_{S_0, S_0}, X P_g X^T - K_{W_0}^{\text{true}}]$) verified on the explicit binary solution $X_{\text{sym}} \in \{0, 1\}^{12 \times 60}$.

pass: true
