# The Discovery Path & `we*star` Collaborative Architecture

> **Repository:** `mizopl/conway-99-graph`  
> **Inspiration & Benchmark Catalyst:** **[Pliny (`@elder-plinius`)](https://github.com/elder-plinius)** & **[`elder-plinius/V3R1T4S`](https://github.com/elder-plinius/V3R1T4S)** ([PR #774](https://github.com/elder-plinius/V3R1T4S/pull/774))  
> **Autoresearch Engine:** [`mizopl/we-star`](https://github.com/mizopl/we-star) (`CONSTITUTION v18` -> `v19`)  
> **Hardware:** Single Apple MacBook Air M1 (16 GB RAM, 0 GPUs)

---

## 0. Inspiration: Pliny (`@elder-plinius`) and the `V3R1T4S` Frontier Benchmark

This investigation, and the broader evolution of the **[`we*star`](https://github.com/mizopl/we-star)** autoresearch system, was directly inspired by **[Pliny (`@elder-plinius`)](https://github.com/elder-plinius)** and the **[`elder-plinius/V3R1T4S`](https://github.com/elder-plinius/V3R1T4S)** open-science repository.

By curating `conway-99-graph` (`problems/conway-99-graph/PROBLEM.md`) into a clear three-tier research ladder (`p2`: machine-checkable certificates for forced local reductions; `p1`: strengthening automorphism exclusions beyond 2023–2026 literature; `p0`: full resolution) and enforcing a strict **zero-trust *Verify-It-Yourself* architecture**, `@elder-plinius` created an ideal proving ground for human-AI mathematical discovery. In particular, the `V3R1T4S` principle that *a claim is only as strong as what a skeptic can verify locally in seconds without trusting external solver binaries* directly motivated our Pure-RUP (`0 RAT lemmas`) dual-encoded LRAT pipeline.

---

## 1. Why Previous Computational Attacks Stalled (`1969 – Sep 2026`)

John H. Conway's 99-graph problem asks whether there exists a strongly regular graph $\Gamma = \mathrm{srg}(99, 14, 1, 2)$: a 99-vertex graph regular of degree $k = 14$ in which every pair of adjacent vertices shares $\lambda = 1$ common neighbor (so every edge lies in a unique triangle, partitioning the edges at each vertex into $7$ disjoint triangles) and every pair of non-adjacent vertices shares $\mu = 2$ common neighbors.

Over five decades, group-theoretical work systematically narrowed the possible prime divisors $p$ of $|\mathrm{Aut}(\Gamma)|$ (starting from $99 = 3^2 \cdot 11$ and $14 = 2 \cdot 7$):
- **Wilbrink (1983), Makhnev & Minakova (2004), Behbahani & Lam (2011), Crnković & Maksimović (2022):** Eliminated $p = 11$, $p = 13$, and fixed-point-free actions of $p = 7$ ($|\mathrm{Fix}(g)| = 0$).
- **Cesarz & Woldar (`arXiv:2308.02978`, Aug 2023):** Introduced the neighborhood-anchored representation where each of the $84$ vertices of $\Gamma_2(x_0)$ is uniquely identified with one of the $\binom{14}{2} - 7 = 84$ non-matched pairs $\{u, v\} \subset \Gamma_1(x_0)$. They proved $|\mathrm{Aut}(\Gamma)| \mid 378 = 2 \cdot 3^3 \cdot 7$ and ruled out $\mathrm{Frob}(21) \cong \mathbb{Z}_7 \rtimes \mathbb{Z}_3$, $|\mathrm{Fix}(g)| = 8$ for $p = 7$ (Lemma 2.2 / Remark 2.3), and $|\mathrm{Fix}(g)| \ge 15$ for $p = 7$ (Corollary 4.4(b)). However, **standalone prime order $p = 7$ with $|\mathrm{Fix}(g)| = 1$ (`p7_fix1`) remained open** (Section 6).
- **Thakkar & Severini (`arXiv:2608.11211v2`, Sep 2026):** Formulated the 4 local constraints around $x_0$ as a constraint satisfaction problem and ran a 14-core Google OR-Tools CP-SAT cluster. While they ruled out $p = 5$ ($|\mathrm{Fix}(g)| = 9$) and $p = 11$ empirically, **their 14-core CP-SAT solver timed out after $> 48\text{ hours}$ on `p7_fix1` ($p = 7$, $|\mathrm{Fix}(g)| = 1$)** (Section 2.4, p. 4) and left prime orders $p \in \{2, 3\}$ open.

### The Root Cause of the 48-Hour Timeout
In `p7_fix1`, an order-$7$ automorphism $g$ fixing $x_0$ acts as two $7$-cycles on $\Gamma_1(x_0)$ and partitions $\Gamma_2(x_0)$ into $12$ orbits $O_1, \dots, O_{12}$ of size $7$. A direct edge-orbit encoding introduces $12 + 7 \cdot \binom{12}{2} = 474$ to $492$ binary cyclic-shift variables (`Constraint 2` and `Constraint 3`). When plugged directly into the $\binom{12}{2} = 66$ quadratic common-neighbor equations ($\lambda = 1, \mu = 2$), the solver faces a **$7^3$-fold cyclic shift symmetry explosion** with weak linear relaxation bounds.

---

## 1.5. How All Theorems Glue Together: The Exhaustive Cauchy-Orbit Partition Tree

A critical question for any case-by-case computer-assisted proof is: **how do we know that the individual theorems glue together without leaving an unexamined gap?**

The architecture is governed by a three-level deductive tree:

### Level 1: Cauchy's Theorem on $|\mathrm{Aut}(\Gamma)|$
If $|\mathrm{Aut}(\Gamma)| > 1$, then at least one prime $p$ divides $|\mathrm{Aut}(\Gamma)|$, and by Cauchy's Theorem (1845) $\mathrm{Aut}(\Gamma)$ contains an element $g$ of prime order $p$. Classical orbit-stabilizer congruences on $n = 99, k = 14, \lambda = 1, \mu = 2$ restrict $p$ to $\{2, 3, 5, 7, 11, 13\}$, with $p \in \{11, 13\}$ excluded by Wilbrink (1983), Makhnev & Minakova (2004), and Cesarz & Woldar (2023).

### Level 2: Track `p2` (`p2_1`–`p2_5`) as the Universal Neighborhood Glue
Whenever $g \in \mathrm{Aut}(\Gamma)$ fixes a vertex $x_0 \in V(\Gamma)$, the 5 certified propositions of Track `p2` prove that:
1. $\Gamma_1(x_0)$ is a union of $7$ disjoint edges $M_{x_0} = \{e_0, \dots, e_6\} \cong 7 K_2$ (`p2_1_inner_matching_k14`).
2. Every outer vertex $u \in \Gamma_2(x_0)$ corresponds to a unique non-matched pair $P_u = \{y_1, y_2\} \in \binom{\Gamma_1(x_0)}{2} \setminus M_{x_0}$ (`p2_2_outer_pair_uniqueness`).
3. Consequently, **the action of $g$ on $\Gamma_1(x_0)$ uniquely induces its action $g(P_u) = \{g(y_1), g(y_2)\}$ on all $84$ outer vertices $\Gamma_2(x_0)$!** There is zero freedom in how $g$ permutes the $84$ outer vertices once its permutation of $\Gamma_1(x_0)$ is specified.

### Level 3: Exhaustive Diophantine Case Enumeration Within Each Prime $p$

| Prime $p$ | Fixed-Point / Orbit Classification | Total Mathematical Cases | Closed Prior to This Work | Certified UNSAT in This Repo (`verify.py`) | Remaining Open Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$p = 7$** | $\|\mathrm{Fix}(g)\| \in \{0\} \cup \{1, 8, 15, \dots\}$ | $4$ regimes ($0, 1, 8, \ge 15$) | $3$ ($f=0$ MM04; $f=8, \ge 15$ CW23) | **`1` (`p7_fix1`, $f=1$) -> 100% CLOSED** | **`0` ($7 \nmid \|\mathrm{Aut}(\Gamma)\|$)** |
| **$p = 2$** | $2a + b + c = 7$ on $M_{x_0}$ ($f \ge 1$ by CW23 Cor. 3.8) | **$19$ profiles $(a,b,c) \ne (0,0,7)$** | $0$ LRAT certificates | **`18 / 19` profiles ($f \ge 3$)** | **`1` (`(0,7,0)`, $f=1$)** |
| **$p = 5$** | $f \equiv 99 \equiv 4 \pmod 5 \implies f \in \{4, 9\}$ ($f=0, \ge 14$ ruled out) | $2$ fixed-point regimes ($f=9, f=4$) | $f=9$ empirical CP-SAT (TS26) | **`p5_t1_fix9` ($f=9$)** | $f=4$ (`p5_t2`) |
| **$p = 3$** | $f \in \{0, 3, 6, 9, \dots, 33\}$ | Fixed-point & FPF actions | Selected $f \ge 6$ (CW23) | **`p3_t1_fix33` ($f=33$) + `frob21_z7_z3`** | Low-$f$ / FPF (`p3_t2`, `p3_fpf`) |

For $p = 2$, the exhaustiveness of the $19$ profiles follows from counting all non-negative integer solutions to $2a + b + c = 7$ with $(a,b,c) \ne (0,0,7)$:
- $a = 0 \implies b + c = 7$, $b \in \{1,2,3,4,5,6,7\}$ (**7 profiles**: `6` certified UNSAT, `1` open `(0,7,0)`),
- $a = 1 \implies b + c = 5$, $b \in \{0,1,2,3,4,5\}$ (**6 profiles**: all `6` certified UNSAT),
- $a = 2 \implies b + c = 3$, $b \in \{0,1,2,3\}$ (**4 profiles**: all `4` certified UNSAT),
- $a = 3 \implies b + c = 1$, $b \in \{0,1\}$ (**2 profiles**: all `2` certified UNSAT).
Total: $7 + 6 + 4 + 2 = 19$ profiles.

---

## 2. Step-by-Step Discovery Path

### Step 1: Certifying the 5 Forced-Structure Propositions (`Track p2`)
Before attacking open symmetry groups, `PROOFER-II` formalized all 5 local structural propositions (`p2_1_inner_matching_k14` through `p2_5_srg9_uniqueness`) of `arXiv:2608.11211v2` in two structurally independent SAT cardinality encodings:
- **Encoding A:** Sinz (2005) Sequential Counter (`sequential_counter`).
- **Encoding B:** Bailleux & Boufkhad (2003) Binary Tree Unary Totalizer (`totalizer`).
To guarantee non-vacuity (`Law M3`), the exact same generator was tested on the smaller parameter tuple $\mathrm{srg}(9, 4, 1, 2) \cong K_3 \square K_3$, producing an explicit 9-vertex adjacency witness alongside the 10 Pure-RUP UNSAT proofs.

### Step 2: The Galois-Spectral Breakthrough on $p = 7$ (`p7_fix1` in $0.82\text{s}$)
Rather than throwing more CPU hours at the 492-variable cyclic-shift encoding, we applied **`Law M10` (Algebraic-Spectral & Galois Trace Compression Before Search)**:
1. **Galois Equivariance on $\mathbb{Q}(\zeta_7)$:** The adjacency matrix $A$ of $\mathrm{srg}(99, 14, 1, 2)$ has eigenvalues $14^1$, $3^{54}$, and $(-4)^{44}$. Since $g$ has prime order $7$ with $|\mathrm{Fix}(g)| = 1$, every non-trivial character $\chi_k(g) = \zeta_7^k$ ($k = 1, \dots, 6$) is Galois-conjugate under $\mathrm{Gal}(\mathbb{Q}(\zeta_7)/\mathbb{Q}) \cong \mathbb{Z}_6$ and therefore appears with equal multiplicity $m_3$ in $E_3$ and $m_{-4}$ in $E_{-4}$.
2. **Exact Trace Forcing ($\mathrm{Tr}(B) = 0$):** Because $g$ has no fixed points outside $\{x_0\}$, $\mathrm{Tr}(A g^k) = 0$ for all $k \not\equiv 0 \pmod 7$. Solving the resulting $2 \times 2$ integer system over $E_3$ and $E_{-4}$ forces $m_3 = 8$ ($54 = 6 + 6 \cdot 8$) and $m_{-4} = 6$ ($44 = 8 + 6 \cdot 6$), which in turn proves that the $12 \times 12$ outer orbit-valency matrix $B = (b_{ij})$ (where $b_{ij} \in \{0, 1, 2\}$ counts neighbors of a vertex $u \in O_i$ inside $O_j$) satisfies:
   $$\mathrm{Tr}(B) = \sum_{i=1}^{12} b_{ii} = 0 \implies b_{ii} = 0 \quad (\forall i = 1, \dots, 12).$$
3. **Submatrix Projection onto $[M \mid Q]$:** Combined with the quadratic orbit equation $B^2 + B - 12I_{12} = 2J_{12} - C^T C$ projected onto the $6$ mono-cycle orbits $I_{LL} \cup I_{RR}$ (`L_diff == 18`, column bounds `L_c_up <= 6`, `L_c_diag <= 5`, and $S_3 \times S_3 \rtimes \mathbb{Z}_2 \times S_6$ symmetry breaking), the $> 48\text{-hour}$ timeout collapsed into a **$0.82\text{-second}$ Pure-RUP UNSAT proof** (`5,209` RUP lemmas in Encoding B; $1.14\text{s}$ and `10,590` RUP lemmas in Encoding A, `0 RAT`).

### Step 3: Eliminating $p = 5$ (`p5_t1_fix9`), $p = 3$ (`p3_t1_fix33`), and $\mathrm{Frob}(21)$
Using the same orbit-valency projection framework:
- For $p = 5$ with $|\mathrm{Fix}(g)| = 9$ and $18 \times 5$-cycles (`p5_t1_fix9`), Galois-spectral trace over $\mathbb{Q}(\zeta_5)$ forces $\mathrm{Tr}(B) = 8$ on the $20 \times 20$ outer orbit matrix, yielding an immediate $1$-step RUP refutation after unit propagation.
- For $p = 3$ with $|\mathrm{Fix}(g)| = 33$ (`p3_t1_fix33`) and the Frobenius group $\mathrm{Frob}(21) \cong \mathbb{Z}_7 \rtimes \mathbb{Z}_3$ (`frob21_z7_z3`), dual-encoded Pure-RUP LRAT certificates were generated and verified.

### Step 4: The Global Flipped-Edge Triangle Bijection Theorem for $p = 2$ (`18/19` Involution Profiles)
For prime order $p = 2$, an involution $g \in \mathrm{Aut}(\Gamma)$ fixing $x_0$ preserves the $7$ inner matched edges $M_{x_0}$ with profile $(a, b, c)$ ($2a + b + c = 7$), where $a$ pairs of matched edges are swapped, $b$ matched edges are flipped in place, and $c$ matched edges are fixed pointwise.
- **Wave 1 (14 Profiles):** Using the spectral trace identity on the $-1$-eigenspace $V_{-1}(g)$,
  $$\mathrm{Tr}(B) = 8a + 3b + 4k_2 - 7m_3(-1),$$
  together with the local triangle-counting window $12 - 4a \le \mathrm{Tr}(B) \le 12 + 2a$ when $c \ge 1$, `PROOFER-II` refuted and certified 14 of the 19 involution profiles (`(0,1,6)` through `(2,1,2)`).
- **Wave 2 (4 Fixed-Point Profiles `(2,2,1)`, `(2,3,0)`, `(3,0,1)`, `(3,1,0)` in $< 0.2\text{s}$):**
  When `PROOFER-II` attempted to solve the remaining 5 profiles `(0,7,0)`, `(2,2,1)`, `(2,3,0)`, `(3,0,1)`, and `(3,1,0)` using only local constraints at $x_0$, the solver timed out at $5\text{s}$ (`L-C9G-009`) because $b_{x_0} + \mathrm{Tr}(B)$ is a global invariant of $g$, whereas only the local neighborhood of $x_0$ was constrained.
  `AUDITOR` formulated the **Global Flipped-Edge Triangle Bijection Theorem**:
  - Every $g$-flipped edge $\{u, g(u)\} \in E(\Gamma)$ lies in a unique $g$-invariant triangle $\{u, g(u), z\}$, where $z \in \mathrm{Fix}(g)$ is its unique fixed common neighbor ($\lambda = 1$).
  - Conversely, at every fixed vertex $z \in \mathrm{Fix}(g)$, the induced subgraph on $\mathrm{Fix}(g) \cap \Gamma(z)$ has degree $\le 2$ in which every edge lies in a triangle, so $\mathrm{Fix}(g) \cap \Gamma(z)$ is a disjoint union of $c_z \ge 0$ triangles and $f - 1 - 3c_z$ isolated fixed vertices ($f = |\mathrm{Fix}(g)|$).
  - Applying the orbit-matrix equations at every fixed vertex $z \in \mathrm{Fix}(g)$ simultaneously forces:
    $$b_z = b + c - 2c^2 + 2c_z^2 - c_z, \qquad E_{\text{flip}}(g) = b_{x_0} + \mathrm{Tr}(B) = \sum_{z \in \mathrm{Fix}(g)} b_z = 4\dim V_{-1}(g) - 7M_3(-1).$$
  - Injecting this single theorem into `verify_lens2_p1.py` immediately refuted all 4 remaining fixed-point involution profiles (`(2,2,1)`, `(2,3,0)`, `(3,0,1)`, `(3,1,0)`) in **$< 0.2\text{ seconds}$ each (`1` to `55` RUP steps, `0 RAT`)**, bringing $p = 2$ to **18/19 certified profiles**.

### Step 5: Coupled $42 \times 42$ Orbit & Signed $V_{-1}(g)$ Matrix Equations for `(0, 7, 0)` (`Phase 3`)
With 18/19 involution profiles certified UNSAT, the entire prime $p = 2$ analysis reduces to the single central involution $g = -I_7 \in Z(B_7)$ (`(0, 7, 0)`, $|\mathrm{Fix}(g)| = 1$, $49$ transpositions):
1. **$42 \times 42$ Outer Orbit Equation (`B`) & Signed $V_{-1}(g)$ Equation (`D`):**
   On the $42$ outer $g$-orbits ($21$ conjugate pairs $\{x_a, \bar{x}_a\}$), the orbit-sum matrix $B = 2 P_\pi + |D|$ and the signed $-1$-eigenspace matrix $D \in \{-1, 0, +1\}^{42 \times 42}$ satisfy:
   $$B^2 + B - 12 I_{42} = M_{21}^{\text{true}} \otimes J_2, \qquad D = D^T, \quad \mathrm{diag}(D) = 0, \quad D C_- = 0, \quad D^2 + D - 12 I_{42} = -C_- C_-^T$$
   with exact spectra $\mathrm{Spec}(B) = \{12^1, 1^6, 3^{20}, (-4)^{15}\}$ and $\mathrm{Spec}(D) = \{0^7, 3^{20}, (-4)^{15}\}$.
2. **Global 7-Triangle Triality Coupling:**
   Each of the $7$ inner triangles $T_r$ ($r \in \{0..6\}$) selects a $12$-orbit slice $S_r \subset \{0..41\}$ with $\sum_{r=0}^6 \Pi_{S_r} = 2 I_{42}$, where the $10,395$ perfect matchings on $12$ vertices compress under $B_6 = \mathbb{Z}_2^6 \rtimes S_6$ (order $46,080$) into **11 canonical integer-partition orbits**, coupled across every pair of slices by the **Triality Reciprocity Law** $M_r^+(x, \bar{x}) = M_t^-(x, \bar{x})$ on $Q_{\{r, t\}} = S_r \cap S_t$.

### Step 6: The Mod-2 Triple-Block Parity Obstruction ($k_{\text{type1}}(S_r) \le 2$) & The $36 \times 36$ Gram / Commutator Audit (`Phase 4`)
1. **The Mod-2 Triple-Block Parity Obstruction Theorem ($k_{\text{type1}}(S_r) \le 2$):**
   Suppose a slice $S_r$ has $\ge 3$ Type-I blocks ($b_{x, \bar{x}} = M_r^+(2b, 2b+1) + E_r(2b, 2b+1) = 2$), say $0, b_1, b_2$, with $20$-edge block-sum vectors $Y_b = X_{2b} + X_{2b+1} \in \{0, 1\}^{60}$. By the Block-Orbit Exclusion Identity $Y_b + P_g Y_b = \mathbf{1}_{60} - W_{\cdot, 2b} - W_{\cdot, 2b+1}$, $Y_{b_1}$ and $Y_{b_2}$ must be disjoint on $\mathrm{supp}(Y_0)$. Reducing $\langle Y_{b_1}, Y_{b_2} \rangle$ modulo $2$, all vertex degrees cancel except on the $2$ edges of $Y_0$ between block $b_1$ and block $b_2$:
   $$\langle Y_{b_1}, Y_{b_2} \rangle \equiv d_{Y_0}(2b_2+1, b_1) + d_{Y_0}(2b_1+1, b_2) \equiv 1 \pmod{2} \in \{1, 3, 5, 7, 9, 11\}.$$
   Since $\langle Y_{b_1}, Y_{b_2} \rangle$ is **strictly odd**, it can never equal $4$ (`414,973` disjoint block-sum pairs checked across all `78` canonical $B_5$-orbits of $(H_0, H_1)$, `0` compatible, `78/78` Kissat `UNSAT`). Thus **$k_{\text{type1}}(S_r) \le 2$ on every slice $S_r$** ($\Delta(G_{\text{type1}}) \le 2$, at most $7$ Type-I blocks globally).
2. **The $36 \times 36$ Slice Gram Matrix $G_{36}(M_0^+, E_0)$ & Generalized Cycle-Orbit Exclusion:**
   Letting $U_{36} = [W \mid X^T \mid P_g X^T] \in \{0, 1\}^{60 \times 36}$, the SRG equation on $S_{36} \times S_{36}$ gives:
   $$G_{36}(M_0^+, E_0) := U_{36}^T U_{36} = 12 I_{36} + 2 J_{36} - (I_3 \otimes J_{12}) - A_{S_{36}}^2 - A_{S_{36}} = \begin{pmatrix} W^T W & \Delta_0^T & F_{12} \Delta_0^T \\ \Delta_0 & G_+ & K_{W_0} \\ \Delta_0 F_{12} & K_{W_0}^T & G_+ \end{pmatrix}.$$
   Every $(M_0^+, E_0)$-closed union of blocks $B \subset \{0..5\}$ yields an explicit nullvector $v_B \in \ker(G_{36})$, forcing $\sum_{i \in I_B} (X(i, c) + X(i, g(c))) = |B| - \sum_{j \in I_B} W(c, j)$ on every edge $c \in R_{60}$.
3. **Exact Bracket I + II Cross-Slice Commutator Identity:**
   For $Z_D = -D_{S_0, W_0} D_{W_0, W_0} D_{W_0, S_0}$, the asymmetry commutator decomposes into two structural brackets:
   $$Z_D - Z_D^T = \underbrace{\Big[D_{S_0, W_0} C_{-, W_0} C_{-, S_0}^T - C_{-, S_0} C_{-, W_0}^T D_{W_0, S_0}\Big]}_{\text{Bracket I: } X W = \Delta_0 \text{ (i.e. } (D C_-)_{S_0} = 0\text{)}} + \underbrace{\Big[D_{S_0, S_0}(D_{S_0, W_0} D_{W_0, S_0}) - (D_{S_0, W_0} D_{W_0, S_0}) D_{S_0, S_0}\Big]}_{\text{Bracket II: } X X^T = G_+, \, X P_g X^T = K_{W_0}}.$$
   Enforcing both Bracket I and Bracket II simultaneously turns all tested $(X_2, X_3)$ extensions for $k_{\text{type1}} = 2$ from `SAT (0.10s)` into **`100% UNSAT (1.50s–4.33s)`** (`asymmetric_research/verify_lens3_asymmetric.py`).

---

## 3. How `we*star` Works: Human + AI Collaborative Architecture

This research was conducted under **[`we*star`](https://github.com/mizopl/we-star)** (`CONSTITUTION v18`, staging `v19`), a federated autoresearch architecture designed by `@mizopl`. Unlike monolithic "one-prompt" LLM wrappers, `we*star` separates **strategic governance**, **mathematical architecture**, and **certified solver execution** across three distinct roles:

```
+-------------------------------------------------------------------------+
|  @mizopl (Human Creator of we*star & Epistemic Governor)                |
|  - Constitutional rules (M1-M10, X1-X14), 20-min supervision heartbeat  |
|  - Brier telemetry audit -> 3-Tier Epistemic Calibration (M4 v2)        |
|  - Strict role enforcement (stops Architect from running solver code)   |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|  AUDITOR (Gemini Argon — Strategic Mathematical Architect & Verifier)   |
|  - Derives algebraic-spectral bridge theorems (Galois trace, Flipped-   |
|    Edge Triangle Bijection, B7 Bose-Mesner & Triality Reciprocity)      |
|  - Audits check_run.py, SHA256SUMS, and K12/X12 scientific outreach     |
+------------------------------------+------------------------------------+
                                     |  send_message (Blueprint Dispatch)
                                     v
+-------------------------------------------------------------------------+
|  PROOFER-II (Gemini Argon — Autonomous Theorem-Proving Engine)          |
|  - Pre-registers atomic falsifiable micro-bets (micro_bet.py)           |
|  - Encodes Dual SAT (Sinz + Totalizer), runs kissat (0 RAT) + drat-trim |
|  - Verifies Pure-RUP LRAT in pure Python stdlib (verify.py)             |
+-------------------------------------------------------------------------+
```

### Real-World Example of Human-AI Epistemic Governance During This Run

1. **Catching Role Drift (`15:07`):** When `PROOFER-II` hit the 5-second timeout on the remaining 5 involution profiles of $p = 2$, `AUDITOR` began testing the fixed-point suspension equations locally in Python. `@mizopl` immediately intervened (*"chyba wyszedles z roli i cos liczysz... o co chodzi?"*), restoring strict architectural separation: `AUDITOR` formulated the clean mathematical blueprint (`Global Flipped-Edge Triangle Bijection Theorem`) and sent it via `send_message` to `PROOFER-II`, who encoded and certified the 4 new theorems (`8` Dual-SAT LRAT proofs) in under 4 minutes.
2. **Auditing the 13 Micro-Bets & Discovering `Law M4 v2` (`15:30`):** `@mizopl` requested an audit of `PROOFER-II`'s 13 pre-registered micro-bets (`10/13` wins = `76.9%` hit rate, mean Brier `0.233`). The audit revealed two structural flaws in `v18` calibration:
   - **Multi-Case Bundling Penalty (`[M4-BUNDLE]`):** In Bet `L-C9G-012`, `PROOFER-II` bundled all 5 remaining $p = 2$ profiles into a single binary bet (`all 5 remaining ...`). Even though 4 of the 5 profiles (`80%`) succeeded in $< 0.2\text{s}$, the binary conjunction evaluated to `0` (`Brier = 0.423`).
   - **Artificial Ceiling on Deterministic Certification (`[M4-TIER3]`):** Post-proof packaging bets (`L-C9G-001, 007, 008, 013`) were capped at $p = 0.65$, imposing a minimum Brier penalty of $0.123$ on deterministic engineering checks.
   Upgrading `micro_bet.py` to the **3-Tier Epistemic Calibration (`Law M4 v2`)** reduced the calibrated mean Brier score from `0.233` to **`0.138` (`-40.8%`)**.
3. **Breaking the `(0, 7, 0)` Single-Slice Bottleneck via Quantitative Pattern Extraction (`18:26`):**
   When `PROOFER-II`'s relaxed single-slice solver returned `SAT` in `0.10s` on $S_0$ while full multi-slice SAT bogged down, `@mizopl` intervened (*"moze trzeba cos zgeneralizowac, pomyslec z innej strony... popatrzec na ten problem pod katem ilosciowym zeby wylapac patterny"*). Instead of grinding case-by-case SAT, `AUDITOR` and `PROOFER-II` extracted the numerical matrices from the relaxed `SAT` solutions and audited the cross-slice commutator $Z_D - Z_D^T$, discovering its exact decomposition into **Bracket I** ($X W = \Delta_0$, i.e., $(D C_-)_{S_0} = 0$) and **Bracket II** ($X X^T = G_+$, $X P_g X^T = K_{W_0}$). In the relaxed `SAT` solutions, Bracket I exploded ($\max |Z_D - Z_D^T| = 12$); adding the missing linear constraint $X W = \Delta_0$ immediately flipped all tested $(X_2, X_3)$ extensions for $k_{\text{type1}} = 2$ from `SAT (0.10s)` to **`100% UNSAT (1.50s–4.33s)`** and revealed the $36 \times 36$ Gram matrix $G_{36}(M_0^+, E_0)$.
4. **Synthesizing the 4 "States of Matter" & Discovering `Law M11` (`Boundary Gauge Freezing Law`, `20:52`):**
   After Phase 7 (`620/620 UNSAT` across all $62 \times 10$ canonical pairs for $k_{\text{type1}} = 2$, and `80/80 UNSAT` via 60-bit bitmask meet-in-the-middle hash-join for 2-block components under Type-I block 0), `@mizopl` asked to review all 18 micro-bets (`L-C9G-001..018`, including the 3 failed bets `003, 009, 012`) through the lens of **"orbit leakage" (*wyciek orbit*) and phase transitions ("stany skupienia": Gas $\to$ Liquid $\to$ Glass $\to$ Crystal)**. This synthesis yielded **`Law M11` (*Boundary Gauge Freezing Law*)** and three exact analytical theorems (`Prawo A`, `Prawo B1`, `Prawo B2`):
   - **`Prawo A` (Intra-Slice $k$-Block Edge-Split & Nullspace Law):** Every $k$-block connected component $B_q$ of $(M_r^+, E_r)$ satisfies $2 n_{\text{int}}(i) + n_{\text{cut}}(i) = 4(k - 1)$ and $n_{\text{int}}(i) - n_{\text{disj}}(i) = 4k - 14$ for every row $i \in I_{B_q}$ (forcing $(0, 4, 6)$ for $k = 2$ and confining all involution pairs $P(i, m) = 1$ to the $12$ disjoint $g$-orbits).
   - **`Prawo B1` (The 7-Triangle Type-I Matching & Handshaking Theorem):** By Triality Reciprocity ($M_r^+(u, \bar{u}) = M_t^-(u, \bar{u})$), being a Type-I block is a symmetric edge $\{r, t\}$ in an undirected graph $H_{\text{type1}}$ on the $7$ inner triangles $\{0..6\}$ with $\deg_{H_{\text{type1}}}(r) = k_{\text{type1}}(S_r) \le 1$. By Euler's Handshaking Lemma on $7$ (odd!) vertices, $\sum_{r=0}^6 k_{\text{type1}}(S_r) = 2|E(H_{\text{type1}})| \in \{0, 2, 4, 6\}$, proving that **at least $1, 3, 5,$ or $7$ slices must have $k_{\text{type1}}(S_r) = 0$** and eliminating the need to solve the `299` five-block (`1+5`) orbits of $k_{\text{type1}} = 1$ separately.
   - **`Prawo B2` (Global Involution Partner Common-Neighbor Law):** For every orbit $u \in Q_a$ and its unique partner $v = \pi(u) \in Q_b$ ($B(u, v) = 2, D(u, v) = 0$ in $B = 2 P_\pi + |D|$), $\sum_w |D(u, w)| |D(w, v)| = (M_{21}^{\text{true}})_{a, b} - 2 \in \{0, 1, 2\}$ and $\sum_w D(u, w) D(w, v) = -(C_- C_-^T)_{u, v} \in \{0, \pm 1, 0\}$.

---

*PS. `we*` = `@mizopl` + agentic systems (powered by Gemini Argon) `we*` create.*
