role: novelty
context: fresh research subagent invoked via invoke_subagent
problem_id: conway-99-graph
claim_targeted: p1 + p2

# Skeptic 2 (`novelty`) Audit — `conway-99-graph` (`p1 + p2`)

## 1. Scope & Files Inspected

This audit inspected only the permitted target, scout, and claim files:
- `target.md`
- `scout.md`
- `claim/artifact.md`
- `claim/certificate.json`

## 2. Prior-Art Baseline vs. Claimed Contributions

### 2.1 Track `p2`: Forced-Structure Reduction of `arXiv:2608.11211`

- **Prior-Art Baseline:**
  Aalok Thakkar & Simone Severini (`arXiv:2608.11211v2`, 18 Sep 2026, Section 2.3) introduced the forced-structure reduction around a fixed root vertex $x \in V(\Gamma)$ for $\Gamma = \mathrm{srg}(99, 14, 1, 2)$, showing analytically and via CP-SAT/backtracking models that:
  1. $\Gamma_1(x)$ is forced to be $1$-regular (a perfect matching $M_x$ of $k/2 = 7$ edges),
  2. $\Gamma_2(x)$ ($84$ vertices) stands in canonical bijection with the $M = \binom{k}{2} - k/2 = 84$ non-matched pairs $P_u \in \binom{\Gamma_1(x)}{2} \setminus M_x$,
  3. Every $u \in \Gamma_2(x)$ and $a \in \Gamma_1(x)$ satisfies the inner-outer coordinate balance $\mathbf{1}_{m(a) \in P_u} + \deg_{N(a)}(u) = 2$,
  4. Every distinct pair $u, v \in \Gamma_2(x)$ with $s = |P_u \cap P_v| \in \{0, 1\}$ satisfies $E(u, v) + \mathrm{cn}_{\Gamma_2(x)}(u, v) = 2 - s$,
  5. The reduced system is exact and uniquely satisfied on the smaller parameter-family member $\mathrm{srg}(9, 4, 1, 2) \cong K_3 \square K_3$.
  However, `arXiv:2608.11211v2` did not publish SAT CNF encodings or machine-checkable DRAT/LRAT proof certificates for these reduction steps.

- **Novelty of the Present Claim on Track `p2`:**
  The artifact provides the first standalone, dual-encoded pure-RUP LRAT (`0 RAT lemmas`) machine-checked re-derivation of all $5$ forced-structure reduction propositions (`p2_1_inner_matching_k14`, `p2_2_outer_bijection_k14`, `p2_3_inner_outer_balance_k14`, `p2_4_outer_pair_cn_k14`, and `p2_5_srg9_uniqueness`), together with positive SAT non-vacuity verification on $\mathrm{srg}(9, 4, 1, 2) \cong K_3 \square K_3$. Every proposition is independently encoded and certified across two structurally distinct SAT cardinality encodings:
  - **Encoding A (`Sinz_2005_Sequential_Counter`):** $4 + 13 + 2,487 + 345 + 13 = 2,862$ trimmed core clauses and $1 + 3 + 836 + 142 + 1 = 983$ pure-RUP LRAT steps (`0 RAT lemmas`).
  - **Encoding B (`Bailleux_Boufkhad_2003_Binary_Tree_Totalizer`):** $4 + 12 + 2,483 + 342 + 7 = 2,848$ trimmed core clauses and $1 + 3 + 780 + 111 + 1 = 896$ pure-RUP LRAT steps (`0 RAT lemmas`).

### 2.2 Track `p1`: Resolution of Open Prime Order $p = 7$ (`p7_fix1`) and 21 Additional Automorphism Exclusions

- **Prior-Art Baseline:**
  - Makhnev & Minakova (2004) and Behbahani & Lam (2011) restricted prime divisors of $|\mathrm{Aut}(\Gamma)|$ for $\Gamma = \mathrm{srg}(99, 14, 1, 2)$.
  - Patrick G. Cesarz & Andrew J. Woldar (`arXiv:2308.02978`, 2023) excluded prime orders $p \in \{11, 13\}$ and the order-$21$ Frobenius subgroup $\mathrm{Frob}(21) = \mathbb{Z}_7 \rtimes \mathbb{Z}_3$, while leaving standalone prime order $p = 7$ ($|\mathrm{Fix}(g)| = 1$, $14$ cycles of length $7$) open.
  - Aalok Thakkar & Simone Severini (`arXiv:2608.11211v2`, 18 Sep 2026) ran 14-core CP-SAT searches on prime orders $p \in \{2, 3, 5, 7, 11\}$ and resolved $p \in \{3, 5, 11\}$, **leaving standalone prime order $p = 7$ (`p7_fix1`) as the sole remaining open prime-order automorphism case after timing out at $> 48\text{ hours}$**, and did not emit DRAT/LRAT proof certificates for any case.

- **Novelty of the Present Claim on Track `p1`:**
  By proving the **Galois-Spectral Trace Theorem** ($\mathrm{Tr}(B) = 0$ on the $12$ outer $7$-cycle orbits of `p7_fix1`), the **Involution Spectral Trace & Flipped-Edge Window Theorem** ($\mathrm{Tr}(B) = 8a + 3b + 4k_2 - 7m_3(-1)$), the **Global Flipped-Edge Triangle Bijection Theorem** ($\mathrm{Tr}(B) = \sum_{z \in \mathrm{Fix}(g) \setminus \{x_0\}} b_z$), and projecting onto orbit-valency matrices anchored at root vertex $x = 0$, the artifact resolves the open prime order $p = 7$ (`p7_fix1`) and produces dual-encoded pure-RUP LRAT (`0 RAT lemmas`) UNSAT certificates for $22$ distinct prime-order and Frobenius automorphism actions ($44$ proofs):
  1. `p7_fix1`: **Resolves the last open prime order $p = 7$** ($1$ fixed vertex, $14 \times 7$-cycles) in $1.14\text{s}$ (Enc A: $36,342$ core clauses, $10,590$ RUP steps) and $0.82\text{s}$ (Enc B: $17,392$ core clauses, $5,209$ RUP steps).
  2. `p5_t1_fix9`: Prime order $p = 5$ fixing $9$ vertices ($1 + 4 + 4$) with $18$ cycles of length $5$ ($31,141$ / $21,073$ core clauses, $2,461$ / $2,050$ RUP steps).
  3. `p3_t1_fix33`: Prime order $p = 3$ fixing $33$ vertices ($1 + 8 + 24$) with $22$ cycles of length $3$ ($166$ / $251$ core clauses, $23$ / $35$ RUP steps).
  4. `frob21_z7_z3`: Order-$21$ Frobenius subgroup $\mathrm{Frob}(21) = \mathbb{Z}_7 \rtimes \mathbb{Z}_3$ ($13,758$ / $8,104$ core clauses, $3,253$ / $3,016$ RUP steps).
  5. **18 of the 19 prime-order $p = 2$ involutions (`p2_*`):** `(0,1,6)`, `(0,2,5)`, `(0,3,4)`, `(0,4,3)`, `(0,5,2)`, `(0,6,1)`, `(1,0,5)`, `(1,1,4)`, `(1,2,3)`, `(1,3,2)`, `(1,4,1)`, `(1,5,0)`, `(2,0,3)`, `(2,1,2)`, `(2,2,1)`, `(2,3,0)`, `(3,0,1)`, `(3,1,0)`.
  6. **Asymmetric Algebraic, Spectral & 7-Triangle Triality Rigidity (`verify_lens3_asymmetric.py`):** Establishes the $6$-dimensional Hyperoctahedral $B_7 = \mathbb{Z}_2^7 \rtimes S_7$ Bose-Mesner scheme on $\Gamma_2(x_0)$, the Triangle-Complement Spectral Duality Theorem and Exact Triangle Conservation Law $T(R_{60}) + T(S_{36}) = 32$, the coupled $42 \times 42$ matrix system $(B, D)$ and Global 7-Triangle Triality Coupling for the 19th involution profile `(0, 7, 0)` ($g = -I_7 \in Z(B_7)$), the Mod-2 Triple-Block Parity Obstruction Theorem ($k_{\text{type1}}(S_r) \le 2, \Delta(G_{\text{type1}}) \le 2$), the Generalized Cycle-Orbit Exclusion Theorem ($\dim \ker(G_{36}) = 1 + c(M_0^+, E_0)$ across all $3,294$ surviving $B_6$-orbits), the Universal $[F_{12}, D_{S_0, S_0}]$ Commutator Cancellation Law ($Z_D - Z_D^T = [D_{S_0, S_0}, X P_g X^T - K_{W_0}^{\text{true}}]$), the multi-pair $k_{\text{type1}}(S_0) = 2$ closure (`620/620 UNSAT` in `290.69s`), and the 2-Block Component $g$-Orbit Partition Law ($(2, 16, 12)$) and 60-bit Bitmask Hash-Join certifying `30/30 UNSAT` across all $\dim \ker(G_{36}) = 4$ orbits of $k_{\text{type1}}(S_0) = 1$ (`31.47s`), `80/80 UNSAT` across all uncanonicalized 2-block connected components (`67.86s`), and `9/9 UNSAT` across all two-component extensions for the $10 = \binom{3+3-1}{3}$ $\dim \ker(G_{36}) = 4$ orbits of $k_{\text{type1}}(S_0) = 0$ (`2.86s`).

## 3. Conclusion

Across both tracks (`5` forced-structure reduction propositions in Track `p2` and `22` prime-order / Frobenius subgroup automorphism exclusions in Track `p1`, including the open prime order $p = 7$), the artifact delivers $54$ independent pure-RUP LRAT UNSAT certificates ($92,259$ total RUP steps, $0$ RAT lemmas) across two structurally distinct SAT cardinality encodings, complemented by the machine-verified asymmetric/triality suite (`verify_lens3_asymmetric.py`). The claim genuinely advances beyond the existing literature on Conway's 99-graph problem.

pass: true
