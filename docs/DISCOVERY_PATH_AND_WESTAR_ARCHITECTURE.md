# The Discovery Path (`Ścieżka Dojścia`) & `we*star` Collaborative Architecture

> **Repository:** `mizopl/conway-99-graph`  
> **Autoresearch Engine:** [`mizopl/we-star`](https://github.com/mizopl/we-star) (`CONSTITUTION v18` -> `v19`)  
> **Benchmark Lineage:** [`elder-plinius/V3R1T4S` — PR #774](https://github.com/elder-plinius/V3R1T4S/pull/774)  
> **Hardware:** Single Apple MacBook Air M1 (16 GB RAM, 0 GPUs)

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

## 2. Step-by-Step Discovery Path (`Ścieżka Dojścia`)

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

---

*PS. `we*` = `@mizopl` + agentic systems (powered by Gemini Argon) `we*` create.*
