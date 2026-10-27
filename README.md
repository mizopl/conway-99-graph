# Conway's 99-Graph Problem (`srg(99, 14, 1, 2)`): Galois-Spectral & Pure-RUP LRAT Certificates

[![Engine: we*star](https://img.shields.io/badge/Autoresearch_Engine-we*star-blue)](https://github.com/mizopl/we-star)
[![Benchmark: V3R1T4S PR #774](https://img.shields.io/badge/V3R1T4S-PR_%23774-success)](https://github.com/elder-plinius/V3R1T4S/pull/774)
[![Proofs: 54 Pure-RUP LRAT (0 RAT)](https://img.shields.io/badge/LRAT_Proofs-54_Pure--RUP_(0_RAT)-brightgreen)](#quick-verification-18-seconds-zero-dependencies)

This repository contains the standalone code, algebraic-spectral reductions, trimmed CNF cores, and **54 dual-encoded Pure-RUP LRAT (`0 RAT lemmas`) UNSAT certificates** across **27 theorems** on John H. Conway's 99-graph problem ($\Gamma = \mathrm{srg}(99, 14, 1, 2)$, $\lambda = 1$, $\mu = 2$), developed using the **[`we*star`](https://github.com/mizopl/we-star)** human-AI autoresearch architecture (`CONSTITUTION v18/v19`) on a single 16 GB M1 laptop.

> **Inspiration & Catalyst (`@elder-plinius` / `V3R1T4S`):** This work was directly inspired by **[Pliny (`@elder-plinius`)](https://github.com/elder-plinius)** and the **[`elder-plinius/V3R1T4S`](https://github.com/elder-plinius/V3R1T4S)** open-science benchmark, which formulated the structured `p2 -> p1 -> p0` challenge ladder for Conway's 99-graph (`problems/conway-99-graph/PROBLEM.md`) and established the zero-trust *Verify-It-Yourself* standard requiring self-contained, fast, dependency-free verification ([PR #774](https://github.com/elder-plinius/V3R1T4S/pull/774)).

All **54 LRAT certificates (`92,259` Reverse Unit Propagation steps, `0` RAT lemmas)** are verified from freshly generated CNF clauses in **$\sim 18$ seconds** using only the Python 3 standard library (`verify-it-yourself/verify.py`).

---

## Highlights & Key Mathematical Results

1. **Resolving the Last Open Prime Order $p = 7$ (`p7_fix1`, $|\mathrm{Fix}(g)| = 1$, $14 \times 7$-cycles) in $0.82\text{s}$:**
   - In both **Patrick G. Cesarz & Andrew J. Woldar (`arXiv:2308.02978`, Aug 2023)** and **Aalok Thakkar & Simone Severini (`arXiv:2608.11211v2`, Sep 2026)**, a prime-order $p = 7$ automorphism fixing a single vertex ($|\mathrm{Fix}(g)| = 1$, $14$ cycles of length $7$) remained the **sole unresolved prime order** of $\mathrm{Aut}(\Gamma)$ (where a 14-core CP-SAT search timed out after $> 48\text{ hours}$ in `arXiv:2608.11211v2`, Section 2.4, p. 4).
   - By proving the **Galois-Spectral Trace Theorem** ($\mathrm{Gal}(\mathbb{Q}(\zeta_7)/\mathbb{Q}) \cong \mathbb{Z}_6$ equivariance on the eigenspaces $E_3$ of dimension $54$ and $E_{-4}$ of dimension $44$ forces the outer $12 \times 12$ orbit-valency matrix $B$ to have trace $\mathrm{Tr}(B) = 0$) and projecting the quadratic SRG equation $B^2 + B - 12I_{12} = 2J_{12} - C^T C$ onto the top $6 \times 12$ submatrix $[M \mid Q]$ over $I_{LL} \cup I_{RR}$, `p7_fix1` is refuted and certified UNSAT in **$1.14\text{s}$** (Encoding A: `36,342` core clauses, `10,590` RUP steps) and **$0.82\text{s}$** (Encoding B: `17,392` core clauses, `5,209` RUP steps) with `0 RAT lemmas`.
   - Combined with Cesarz & Woldar (2023) ($|\mathrm{Fix}(g)| = 8$ via Lemma 2.2 / Remark 2.3 and $|\mathrm{Fix}(g)| \ge 15$ via Corollary 4.4(b)) and Makhnev & Minakova (2004) ($|\mathrm{Fix}(g)| = 0$), this **unconditionally eliminates $p = 7$ as a prime divisor of $|\mathrm{Aut}(\Gamma)|$**, reducing the open automorphism divisor bound from $|\mathrm{Aut}(\Gamma)| \mid 378$ to **$|\mathrm{Aut}(\Gamma)| \mid 54 = 2 \cdot 3^3$**.

2. **Global Flipped-Edge Triangle Bijection Theorem & 18/19 Involution Profiles of $p = 2$:**
   - Every involution $g \in \mathrm{Aut}(\Gamma)$ ($p = 2$) fixing $x_0$ induces an inner matching profile $(a, b, c)$ ($2a + b + c = 7$) on the $7$ matched edges $M_{x_0}$ of $\Gamma_1(x_0)$.
   - By proving that every $g$-flipped edge $\{u, g(u)\} \in E(\Gamma)$ has a unique fixed common neighbor $z \in \mathrm{Fix}(g)$ and suspending $\Gamma$ at every $z \in \mathrm{Fix}(g)$, we establish the **Global Flipped-Edge Triangle Bijection Theorem**:
     $$E_{\text{flip}}(g) = b_{x_0} + \mathrm{Tr}(B) = \sum_{z \in \mathrm{Fix}(g)} b_z = 4\dim V_{-1}(g) - 7M_3(-1), \qquad b_z = b + c - 2c^2 + 2c_z^2 - c_z.$$
   - Coupled with the spectral trace identity $\mathrm{Tr}(B) = 8a + 3b + 4k_2 - 7m_3(-1)$, this refutes and certifies **18 of the 19 involution profiles** of $p = 2$ (all 18 profiles with $|\mathrm{Fix}(g)| \ge 3$), isolating the single central fixed-point-free outer involution `(0,7,0)` ($g = -I_7 \in Z(B_7)$, $|\mathrm{Fix}(g)| = 1$).

3. **Forced Local Structure (`Track p2`, 5 Theorems = 10 Proofs) & Odd-Order Reductions ($p = 5, 3, \mathrm{Frob}(21)$):**
   - Machine-checked Pure-RUP LRAT certificates for all 5 forced-structure propositions (`p2_1` through `p2_5`) of Thakkar & Severini (`arXiv:2608.11211v2`), including positive SAT non-vacuity on the paley-9 / $3 \times 3$ rook graph $\mathrm{srg}(9, 4, 1, 2) \cong K_3 \square K_3$.
   - Machine-checked Pure-RUP LRAT refutations for **`p5_t1_fix9`** ($p = 5$, $9$ fixed vertices, $18 \times 5$-cycles via $\mathrm{Tr}(B) = 8$), **`p3_t1_fix33`** ($p = 3$, $33$ fixed vertices, $22 \times 3$-cycles), and **`frob21_z7_z3`** ($\mathrm{Frob}(21) \cong \mathbb{Z}_7 \rtimes \mathbb{Z}_3$).

4. **Central Involution `(0, 7, 0)` ($g = -I_7 \in Z(B_7)$) & Asymmetric ($|\mathrm{Aut}(\Gamma)| = 1$) Algebraic-Spectral Framework (`asymmetric_research/`):**
   - **Universal $14 \oplus 70$ Decomposition & $B_7$ Bose-Mesner Scheme (`Phase 2`):** Even when $|\mathrm{Aut}(\Gamma)| = 1$, the neighborhood projection $C: \mathbb{R}^{84} \to \mathbb{R}^{14}$ canonically splits $\mathbb{R}^{84} = \mathrm{col}(C^T) \oplus \ker(C)$ ($14 \oplus 70$) with universal spectrum $\mathrm{spec}(A_{84}|_{\mathrm{col}(C^T)}) = \{12^1, (-2)^6, 0^7\}$ and $\mathrm{spec}(A_{84}|_{\ker(C)}) = \{3^{40}, (-4)^{30}\}$, governed by the 6-dimensional hyperoctahedral $B_7 = \mathbb{Z}_2^7 \rtimes S_7$ Bose-Mesner algebra and the triangle-complement conservation law $T(R_{60}) + T(S_{36}) = 32$.
   - **Coupled $42 \times 42$ Orbit & Signed $V_{-1}(g)$ Matrix Equations (`Phase 3`):** For the remaining central involution profile `(0, 7, 0)` ($|\mathrm{Fix}(g)| = 1$, $49$ transpositions), the $42 \times 42$ outer orbit matrix $B = 2 P_\pi + |D|$ and the signed $-1$-eigenspace matrix $D \in \{-1, 0, +1\}^{42 \times 42}$ satisfy:
     $$B^2 + B - 12 I_{42} = M_{21}^{\text{true}} \otimes J_2, \qquad D = D^T, \quad \mathrm{diag}(D) = 0, \quad D C_- = 0, \quad D^2 + D - 12 I_{42} = -C_- C_-^T$$
     with $\mathrm{Spec}(B) = \{12^1, 1^6, 3^{20}, (-4)^{15}\}$ and $\mathrm{Spec}(D) = \{0^7, 3^{20}, (-4)^{15}\}$, coupled across all $7$ triangle slices $S_0, \dots, S_6$ by the **Global 7-Triangle Triality Reciprocity Law** $M_r^+(x, \bar{x}) = M_t^-(x, \bar{x})$ on $Q_{\{r, t\}} = S_r \cap S_t$.
   - **The Mod-2 Triple-Block Parity Obstruction Theorem ($k_{\text{type1}}(S_r) \le 2$) & $36 \times 36$ Slice Gram Matrix (`Phase 4`):**
     - Across all $10,395 \times 10,395 = 108,056,025$ ordered matching pairs $(M_0^+, E_0)$ on a slice $S_r$ (`3,580` $B_6$-orbits, `3,308` with $K_{W_0} \ge 0$), any three Type-I blocks $(0, b_1, b_2)$ force an **odd** bit-overlap modulo $2$:
       $$\langle Y_{b_1}, Y_{b_2} \rangle \equiv d_{Y_0}(2b_2+1, b_1) + d_{Y_0}(2b_1+1, b_2) \equiv 1 \pmod{2} \in \{1, 3, 5, 7, 9, 11\},$$
       contradicting $\langle Y_{b_1}, Y_{b_2} \rangle = 4$ (`414,973` disjoint block-sum pairs and `78/78` $B_5$-orbits verified UNSAT). Thus every slice $S_r$ satisfies **$k_{\text{type1}}(S_r) \le 2$** ($\le 7$ Type-I blocks globally).
     - Combining the fixed $60 \times 12$ edge-incidence matrix $W$ of $K_{2,2,2,2,2,2}$ with $[X^T \mid P_g X^T]$ yields the full $36 \times 36$ slice Gram matrix $G_{36}(M_0^+, E_0) = U_{36}^T U_{36}$ (with exact nullspace dimension $\dim \ker(G_{36}) = 1 + c(M_0^+, E_0) \in \{2, 3, 4, 5\}$) and the **Bracket I + II Cross-Slice Commutator Identity** (`verify-it-yourself/verify_lens3_asymmetric.py`).
   - **Generalized Chiral Nullspace Theory for $\mathrm{srg}(2m^2+1, 2m, 1, 2)$, Lean 4 Formal Proofs, and Hybrid M1 + NVIDIA A100 Bitmask Sieve (`Phases 5–10`):**
     - **Unconditional Closure of ALL $k_{\text{type1}}(S_r) \ge 1$ Orbits (`391 / 391 UNSAT`) AND ALL $\dim \ker(G_{36}) \ge 4$ Orbits (`102 / 102 UNSAT`):** Refutes all `62` canonical $B_4$-orbits of $k_{\text{type1}}=2$ $\times$ `10` $(X_2, X_3)$ pairs (`620/620 UNSAT` in `290.69s`), all `30` canonical $B_5$-orbits of $k_{\text{type1}}=1, \dim=4$ (`1+2+3`, `30/30 UNSAT` in `67.86s`), all `299` canonical $B_5$-orbits of $k_{\text{type1}}=1, \dim=3$ (`1+5`, `299/299 UNSAT` in `2,077.56s`, `686,048,000` nodes, [`verify-it-yourself/null3_k1_299_summary.json`](verify-it-yourself/null3_k1_299_summary.json)), and all `10` canonical $B_6$-orbits of $k_{\text{type1}}=0, \dim=4$ (`2+2+2`, `10/10 UNSAT`, `160,968,902` $B_1$ bricks and `1,933,691` $(B_1,B_2)$ pairs explored, [`verify-it-yourself/null4_k0_222_10_summary.json`](verify-it-yourself/null4_k0_222_10_summary.json), with `Orbit 9: C+C+C` cross-verified digit-for-digit between Apple M1 CPU and Google Colab NVIDIA A100 CUDA C++ `__popcll`). Moreover, all `55` canonical $B_6$-orbits (`309,760` raw seed pairs) of $k_{\text{type1}}=0, \dim \ker(G_{36})=3$ with component partition `3+3` (`10 / 10` canonical 3-block LEGO bricks $C_0, \dots, C_9$) are certified `UNSAT` (`23,129` symmetry-reduced leader rows and `298,726,987,506` depth-3 nodes evaluated on NVIDIA A100 GPUs with `0` valid 6-row solutions even for an isolated 3-block component, [`verify-it-yourself/null2_k0_33_55_summary.json`](verify-it-yourself/null2_k0_33_55_summary.json)). Every surviving slice is forced into partition `4+2` (`168` orbits) or irreducible `6` (`2,670` orbits).
     - **14 Theorems Formally Proved in Lean 4.35.0 (`0 sorryAx`, [`verify-it-yourself/ChiralNullspaceAndHandshaking.lean`](verify-it-yourself/ChiralNullspaceAndHandshaking.lean)):**
       1. *`Law M11-A` ($k$-Block Edge-Split Law):* $2 n_{\text{int}}(i) + n_{\text{cut}}(i) = 4(k - 1)$ and $n_{\text{int}}(i) - n_{\text{disj}}(i) = 4k - 2m$ (forcing $(0, 4, 6)$ for $m=7, k=2$).
       2. *Even-$m$ Central Involution No-Go & Exact Column-Sum $= 2$ Law:* $\ker_+(G_{3n_S})$ and $\ker_-(G_{3n_S})$ force $2 \cdot \text{colSum}(c) = m - 3$, proving that no $\mathrm{srg}(2m^2+1, 2m, 1, 2)$ with even $m \ge 4$ admits $g = -I_m$, and forcing $\sum_{i=0}^{11} X(i, c) = 2$ for every column $c \in R_{60}$ at $m = 7$.
       3. *`Law M11-A2` (Unified Chiral Component Imbalance Law):* $\sum_e \delta_{B_q}(e)^2 = 4k(m - 1 - k)$ and $\sum_e \delta_{B_p}(e)\delta_{B_q}(e) = -4k_p k_q$, forcing $(d_2 = 4, d_0 = 8)$ on the $12$ disjoint $g$-orbits of any $k=2$ component and $(c_2 = 6, c_0 = 12)$ on the $18$ cut $g$-orbits of any $k=3$ component at $m = 7$.
       4. *`Law M11-B1` (7-Triangle Type-I Handshaking Theorem):* $\sum_{r=0}^6 k_{\text{type1}}(S_r) = 2|E(H_{\text{type1}})| \in \{0, 2, 4, 6\}$, forcing $7 - 2|E(H_{\text{type1}})| \in \{1, 3, 5, 7\}$ slices to have $k_{\text{type1}}(S_r) = 0$.
       5. *`Law M11-B2` (Global Involution Partner Law):* $(B^2)_{u, \pi(u)} = 2 - |a \cap b| \in \{0, 1, 2\}$ and $(D^2)_{u, \pi(u)} = -(C_- C_-^T)_{u, \pi(u)} \in \{0, \pm 1, 0\}$.
       6. *Universal $k$-Block Column-Sum Distribution & Particle-Hole Duality ($k \leftrightarrow (m - 1) - k$):* $n_2(m, k) = 2k(k - 1)$, $n_1(m, k) = 4k(m - 1 - k)$, $n_0(m, k) = 2(m - 1 - k)(m - 2 - k)$ with $n_2(m, m-1-k) = n_0(m, k)$ and $n_1(m, m-1-k) = n_1(m, k)$.
       7. *`Law M11.5` ("The Standardized LEGO Plug Theorem" — Cross-Component Universal Interface & Cut-Orbit Partition):* For any two vertices $i \in I_{B_p}, j \in I_{B_q}$ in distinct connected components ($p \ne q$), all sparse matrices vanish off-diagonal so $(\Delta_r(i,j), G_+(i,j), K_{W_r}(i,j)) = (2, 1, 2)$ universally, and the 4 rows of any $k=2$ component partition its $16$ cut $g$-orbits into $4$ pairwise disjoint 4-tuples.
       8. *The Asymmetric Diagonal Inversion Law:* $K_{W_r}(i, i) = 2 - 2\cdot\mathbf{1}_{[M_r^+(i)=E_r(i)]} \in \{0, 2\}$, proving that absence of local edge repetition ($M_r^+(i) \ne E_r(i)$) forces $K_{W_r}(i, i) = 2$ (requiring an involution pair $\{c, g(c)\}$ in row $X_i$, which holds on all 12 rows for `1,679 / 2,670` and on $\ge 8$ rows for `2,624 / 2,670` (`98.3%`) of the irreducible `6`-block orbits).
     - **Custom Native ARM64 `@numba.njit(parallel=True)` + CUDA C++ (`__popcll`) 64-Bit Bitmask Solvers ([`verify-it-yourself/run_all_299_nullity3_k1.py`](verify-it-yourself/run_all_299_nullity3_k1.py)):** Combines a 2-bit saturating column-sum half-adder (`nu2 = u2 | (u1 & cxm); nu1 = u1 | cxm`), bitwise power-of-two chiral intersection checks, and `Law M11.5` universal LEGO component coupling to certify all `299 / 299` canonical orbits of $\dim \ker(G_{36}) = 3, k_{\text{type1}} = 1$ (`1+5`) and all `10 / 10` canonical orbits of $\dim \ker(G_{36}) = 4, k_{\text{type1}} = 0$ (`2+2+2`) `UNSAT`.

---

## Quick Verification (~18 Seconds, Zero Dependencies)

Run the standalone standard-library verifier from the root of this repository:

```sh
sh verify-it-yourself/run_checks.sh
```

Using **only the Python 3 standard library** (`collections`, `hashlib`, `itertools`, `json`, `os`, `sys`), `verify.py`:
1. Re-generates all **54 CNF formulas** from scratch across **Encoding A** (Sinz 2005 Sequential Counter) and **Encoding B** (Bailleux & Boufkhad 2003 Binary Tree Totalizer).
2. Verifies the positive satisfiability control on $\mathrm{srg}(9, 4, 1, 2) \cong K_3 \square K_3$.
3. Checks exact clause membership of all 54 trimmed `*_core.cnf` files against the freshly generated CNFs and verifies all SHA-256 digests against `object/certificate.json` and `SHA256SUMS`.
4. Executes a step-by-step Reverse Unit Propagation (`RUP`) check across all **92,259 steps (`0 RAT lemmas`)** of the 54 LRAT certificates to the empty clause `0`.

---

## How All 27 Theorems Glue Together: The Exhaustive Cauchy-Orbit Partition Tree

How do we know that these individual SAT/LRAT theorems fit together without missing any hidden intermediate cases? The glue is purely algebraic and rests on three exact exhaustiveness principles (detailed in [`docs/DISCOVERY_PATH_AND_WESTAR_ARCHITECTURE.md`](docs/DISCOVERY_PATH_AND_WESTAR_ARCHITECTURE.md#2-how-all-theorems-glue-together-the-exhaustive-cauchy-orbit-partition-tree)):

1. **Cauchy's Theorem (Prime-Order Reduction):** Every non-trivial finite group $\mathrm{Aut}(\Gamma)$ ($|\mathrm{Aut}(\Gamma)| > 1$) contains an element $g$ of prime order $p \mid |\mathrm{Aut}(\Gamma)|$. By classic orbit-stabilizer congruences on $99$ vertices and valency $14$ (Wilbrink 1983; Cesarz & Woldar 2023), the only primes that can divide $|\mathrm{Aut}(\Gamma)|$ are $p \in \{2, 3, 5, 7, 11, 13\}$, with $p \in \{11, 13\}$ already eliminated in the literature.
2. **Track `p2` as the Universal Local Glue (`p2_1` through `p2_5`):** Around any fixed vertex $x_0 \in \mathrm{Fix}(g)$, Track `p2` machine-certifies that $\Gamma_1(x_0)$ is rigidly a perfect matching $M_{x_0}$ of $7$ disjoint edges ($7 K_2$, $\lambda = 1$) and that the $84$ vertices of $\Gamma_2(x_0)$ are in canonical bijection with the $\binom{14}{2} - 7 = 84$ non-matched pairs of $\Gamma_1(x_0)$ ($\mu = 2$). Therefore, **any automorphism $g$ fixing $x_0$ is completely determined on $\Gamma_1(x_0) \cup \Gamma_2(x_0)$ by how it permutes the $7$ matched edges of $M_{x_0}$**.
3. **Exhaustive Diophantine Partition Within Each Prime $p$:**
   - **Prime $p = 7$ (100% Exhausted -> $7 \nmid |\mathrm{Aut}(\Gamma)|$):** Since $99 \equiv 1 \pmod 7$ and $g^7 = 1$, $|\mathrm{Fix}(g)| \equiv 1 \pmod 7$ whenever $\mathrm{Fix}(g) \ne \emptyset$.
     - $|\mathrm{Fix}(g)| = 0$: Ruled out by Makhnev & Minakova (2004).
     - $|\mathrm{Fix}(g)| = 8$: Ruled out by Cesarz & Woldar (2023, Lemma 2.2 / Remark 2.3).
     - $|\mathrm{Fix}(g)| \ge 15$: Ruled out by Cesarz & Woldar (2023, Corollary 4.4(b)).
     - **$|\mathrm{Fix}(g)| = 1$ (`p7_fix1`):** Since $7$ is prime, $g$ cannot fix any of the $7$ inner triangles without fixing its vertices, so $g$ must cycle all $7$ edges of $M_{x_0}$ as a single $7$-cycle ($14$ cycles of length $7$ on $V(\Gamma) \setminus \{x_0\}$). Our `p7_fix1` certificate closes this **unique remaining case**, unconditionally proving $7 \nmid |\mathrm{Aut}(\Gamma)|$.
   - **Prime $p = 2$ (19 Exact Cases from $2a + b + c = 7$, 18/19 Certified UNSAT):** By Cesarz & Woldar (2023, Corollary 3.8), every involution $g$ ($g^2 = 1$) fixes at least one vertex $x_0$. On the $7$ edges of $M_{x_0}$, an involution can only: (i) swap $a$ pairs of edges ($2a$ edges), (ii) flip $b$ edges in place, and (iii) fix $c$ edges pointwise. The Diophantine equation:
     $$2a + b + c = 7 \quad (a, b, c \in \mathbb{Z}_{\ge 0}, \ (a,b,c) \ne (0,0,7))$$
     has **exact $7 + 6 + 4 + 2 = 19$ solutions** (`verify.py` enumerates all 19 tuples programmatically). **18 of these 19 tuples** (every tuple with $|\mathrm{Fix}(g)| \ge 3$) are certified UNSAT in Track `p1`, leaving only the single tuple `(0, 7, 0)` ($|\mathrm{Fix}(g)| = 1$).

---

## Summary Table of Certified Theorems (`27` Theorems = `54` Proofs)

| Track | Theorem ID | Group / Structural Case | Encoding A (Sinz 2005) Core / RUP | Encoding B (Totalizer) Core / RUP | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `p2` | `p2_1_inner_matching_k14` | $\Gamma_1(x) \not\cong 7 K_2$ ($\lambda=1$) | `55` cls / `9` RUP | `55` cls / `9` RUP | Certified UNSAT |
| `p2` | `p2_2_outer_pair_uniqueness` | $\Gamma_2(x)$ pair bijection ($\mu=2$) | `29` cls / `2` RUP | `30` cls / `2` RUP | Certified UNSAT |
| `p2` | `p2_3_triangle_forbiddance` | Triangle-free outer neighborhood | `7` cls / `2` RUP | `7` cls / `2` RUP | Certified UNSAT |
| `p2` | `p2_4_outer_degree_balance` | Outer degree balance ($k_2 = 12$) | `45` cls / `4` RUP | `48` cls / `5` RUP | Certified UNSAT |
| `p2` | `p2_5_srg9_uniqueness` | Unique local $\mathrm{srg}(9,4,1,2) \cong K_3 \square K_3$ | `348` cls / `241` RUP | `348` cls / `241` RUP | Certified UNSAT + SAT witness |
| **`p1`** | **`p7_fix1`** | **$p=7$, $\|\mathrm{Fix}(g)\|=1$ ($14 \times 7$-cycles)** | **`36,342` cls / `10,590` RUP** | **`17,392` cls / `5,209` RUP** | **Certified UNSAT ($0.82\text{s}$)** |
| `p1` | `p5_t1_fix9` | $p=5$, $\|\mathrm{Fix}(g)\|=9$ ($18 \times 5$-cycles) | `91` cls / `1` RUP | `11` cls / `1` RUP | Certified UNSAT |
| `p1` | `p3_t1_fix33` | $p=3$, $\|\mathrm{Fix}(g)\|=33$ ($22 \times 3$-cycles) | `12` cls / `1` RUP | `12` cls / `1` RUP | Certified UNSAT |
| `p1` | `frob21_z7_z3` | $\mathrm{Frob}(21) \cong \mathbb{Z}_7 \rtimes \mathbb{Z}_3$ | `36,214` cls / `10,331` RUP | `17,843` cls / `5,293` RUP | Certified UNSAT |
| `p1` | `p2_a0_b1_c6_fix29` .. `p2_a2_b1_c2_fix13` | 14 Involution profiles ($p=2$, Wave 1) | `120,034` cls / `34,321` RUP | `72,000` cls / `25,872` RUP | Certified UNSAT |
| `p1` | `p2_a2_b2_c1_fix7` | $p=2$, profile `(2,2,1)`, $\|\mathrm{Fix}(g)\|=7$ | `743` cls / `17` RUP | `91` cls / `8` RUP | Certified UNSAT ($0.12\text{s}$) |
| `p1` | `p2_a2_b3_c0_fix5` | $p=2$, profile `(2,3,0)`, $\|\mathrm{Fix}(g)\|=5$ | `906` cls / `14` RUP | `91` cls / `8` RUP | Certified UNSAT ($0.13\text{s}$) |
| `p1` | `p2_a3_b0_c1_fix9` | $p=2$, profile `(3,0,1)`, $\|\mathrm{Fix}(g)\|=9$ | `1,583` cls / `1` RUP | `74` cls / `1` RUP | Certified UNSAT ($0.12\text{s}$) |
| `p1` | `p2_a3_b1_c0_fix7` | $p=2$, profile `(3,1,0)`, $\|\mathrm{Fix}(g)\|=7$ | `1,024` cls / `55` RUP | `180` cls / `18` RUP | Certified UNSAT ($0.14\text{s}$) |

---

## The Discovery Path & `we*star` Architecture

A complete chronicle of how these results were discovered and verified is documented in **[`docs/DISCOVERY_PATH_AND_WESTAR_ARCHITECTURE.md`](docs/DISCOVERY_PATH_AND_WESTAR_ARCHITECTURE.md)**.

### How `we*star` Collaborated on This Problem

This project was engineered using **[`we*star`](https://github.com/mizopl/we-star)** (`CONSTITUTION v18/v19`), an open-source framework for zero-trust human-AI mathematical discovery. A central principle of `we*star` is strict **Epistemic Role Separation** coupled with **Algebraic-Before-Search (`Law M10`)**:

1. **`@mizopl` (Human Systems Architect & Epistemic Governor):**
   - Designed and evolved the [`we*star`](https://github.com/mizopl/we-star) autoresearch harness, constitutional laws (`M1-M10`), and dead-end guards (`X1-X14`).
   - Enforced strict role separation during live execution (preventing the strategic architect thread from drifting into ad-hoc solver execution and ensuring every mathematical lemma was dispatched cleanly to the proving engine).
   - Audited the system's pre-registered epistemic micro-bets (`Brier Score` telemetry), identifying the *all-or-nothing conjunction trap* on multi-profile bets and establishing the **3-Tier Epistemic Calibration (`Law M4 v2`)** in `micro_bet.py`.
   - Directed the **Quantitative Pattern Extraction Pivot (`Law M2`)** on `(0, 7, 0)`: when relaxed single-slice `SAT` models stalled full multi-slice search, `@mizopl` redirected the team to extract numerical matrices from the relaxed `SAT` solutions to uncover hidden structural invariants — immediately revealing the **Bracket I + II Cross-Slice Commutator Decomposition** ($X W = \Delta_0$ vs. $X X^T = G_+$) and the $36 \times 36$ Gram matrix $G_{36}(M_0^+, E_0)$.
2. **`AUDITOR` (Gemini Argon — Strategic Mathematical Architect & Zero-Trust Auditor):**
   - Formulated the algebraic-spectral bridge lemmas that replaced exponential search with compact linear invariants: the **Galois-Spectral Trace Theorem** for $p = 7$ ($\mathrm{Tr}(B) = 0$), the **Global Flipped-Edge Triangle Bijection Theorem** for $p = 2$ ($E_{\text{flip}}(g) = \sum_{z \in \mathrm{Fix}(g)} b_z$), and the **$B_7$ Bose-Mesner / Inner-Triangle Triality Reciprocity** framework.
   - Audited all code, hashes, and external communications under `Dead-End Guard X12` (`K12`) and `check_run.py`.
3. **`PROOFER-II` (Gemini Argon — Autonomous Theorem-Proving & Certification Engine):**
   - Implemented the orbit-valency projections (`how-we-built-it/verify_lens2_p1.py`), generated dual SAT encodings (Sinz 2005 + Bailleux-Boufkhad 2003), ran `kissat` in pure-deduction mode (`0 RAT`) + `drat-trim -L`, compressed backward cones, and built the standalone pure-Python verifier (`verify-it-yourself/verify.py`).

---

## Repository Structure

- [`verify-it-yourself/`](verify-it-yourself/) — Standalone zero-dependency pure-Python LRAT RUP verifier (`verify.py`, `run_checks.sh`).
- [`object/`](object/) — Machine-verified `certificate.json` and all 54 trimmed CNF cores (`*_core.cnf`) and Pure-RUP LRAT proof files (`*.lrat`).
- [`how-we-built-it/`](how-we-built-it/) — Proof generation scripts (`verify_lens1_p2.py`, `verify_lens2_p1.py`).
- [`asymmetric_research/`](asymmetric_research/) — Algebraic-spectral verification of the $14 \oplus 70$ neighborhood decomposition, $B_7 = \mathbb{Z}_2^7 \rtimes S_7$ Bose-Mesner algebra, and Inner-Triangle Triality Reciprocity for the asymmetric $|\mathrm{Aut}(\Gamma)| = 1$ regime (`verify_lens3_asymmetric.py`).
- [`docs/DISCOVERY_PATH_AND_WESTAR_ARCHITECTURE.md`](docs/DISCOVERY_PATH_AND_WESTAR_ARCHITECTURE.md) — Full step-by-step discovery narrative, mathematical proofs of the bridge theorems, Brier telemetry audit, and `we*star` architecture guide.
- [`panel/`](panel/) — 3-skeptic zero-trust review panel reports (`gate.md`, `criterion.md`, `novelty.md`, `reproduce.md`).

---

## Inspiration, Links & Lineage

- **Inspiration & Benchmark Catalyst (`@elder-plinius`):** Directly inspired by **[Pliny (`@elder-plinius`)](https://github.com/elder-plinius)** and the **[`elder-plinius/V3R1T4S`](https://github.com/elder-plinius/V3R1T4S)** open-science initiative. Putting `conway-99-graph` on the `V3R1T4S` frontier list, and demanding zero-trust, dependency-free *Verify-It-Yourself* artifacts, was the direct catalyst that drove both these mathematical results and the evolution of the `we*star` engine ([Pull Request #774 on `elder-plinius/V3R1T4S`](https://github.com/elder-plinius/V3R1T4S/pull/774)).
- **Autoresearch Engine & Constitution (`we*star`):** [https://github.com/mizopl/we-star](https://github.com/mizopl/we-star)
- **Prior Literature Referenced:**
  - P. G. Cesarz & A. J. Woldar, *"On symmetries of Conway's 99-graph"*, `arXiv:2308.02978` (2023).
  - A. Thakkar & S. Severini, *"Computational Restrictions on Networking Conway's 99-Graph"*, `arXiv:2608.11211v2` (Sep 2026).
  - A. A. Makhnev & I. M. Minakova, *"On automorphisms of the Conway graph on 99 vertices"* (2004).
  - H. A. Wilbrink, *"On the Conway graph"* (1983) & M. Behbahani & C. Lam (2011).

*PS. `we*` = `@mizopl` + agentic systems (powered by Gemini Argon) `we*` create.*
