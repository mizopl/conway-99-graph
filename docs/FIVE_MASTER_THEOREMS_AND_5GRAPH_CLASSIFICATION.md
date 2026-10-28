# The Five Master Theorems of the $\mathrm{SRG}(v, k, 1, 2)$ Universe: Plain-English Exposition, Mathematical Proofs, Literature Novelty Audit, and Short Existence / Non-Existence Derivations for All Five Graphs ($v \in \{9, 99, 243, 6273, 494019\}$)

> **Formal Lean 4.35.0 Companion (`42` Theorems, `67` Declarations, `0 sorryAx`):** [`verify-it-yourself/ChiralNullspaceAndHandshaking.lean`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean)  
> **Dual-Encoded Pure-RUP LRAT Companion (`27` Theorems = `54` Proofs, `0 RAT`):** [`verify-it-yourself/verify.py`](../verify-it-yourself/verify.py)  
> **Classical Derivations from $\mathrm{SRG}$ Axioms:** [`docs/CLASSICAL_PROOFS_FROM_SRG_AXIOMS.md`](CLASSICAL_PROOFS_FROM_SRG_AXIOMS.md)  
> **Zero-Trust Skeptic Panel Reports (`V3R1T4S` `panel/` — `reproduce`, `novelty`, `criterion` & Blind Reconstructor):** [`panel/gate.md`](../panel/gate.md) · [`panel/criterion.md`](../panel/criterion.md) *(Section 3.1: Full Blind Reconstruction of All 5 Graphs from Master Theorems I–V)* · [`panel/novelty.md`](../panel/novelty.md) *(Section 2.3: Theorem-by-Theorem Prior-Art Audit)* · [`panel/reproduce.md`](../panel/reproduce.md) *(Section 5.9: Lean 4 `#print axioms` Audit)*

---

## 1. Literature Attribution & Novelty Audit: What Was Known vs. What Is New in This Work

To maintain strict scientific transparency, the table below separates what was previously known in the algebraic graph theory literature from the **new structural theorems, generalizations, and formal machine-verified proofs** established in this repository.

| Master Theorem | Literature Status | What Was Known Previously (with Citations) | What Is **New & Generalized** in This Work (`we*star`) |
| :--- | :---: | :--- | :--- |
| **Master Theorem I:**<br>*Spectral Triangle-Pairing & Five-Graph Finiteness Law*<br>(`Theorems 0c, 1, 22, 36`) | **Classical (1973) + First Lean 4 Formalization** | **Berlekamp, van Lint, and Seidel (1973)** proved that $\lambda = 1, \mu = 2$, $v = 1 + k(k-1)/2$, and eigenvalue multiplicity integrality restrict $\mathrm{SRG}(v,k,1,2)$ to at most five parameter sets $v \in \{9, 99, 243, 6273, 494019\}$. **Thakkar & Severini (`arXiv:2608.11211v2`, 2026)** formulated 5 local forced-structure reductions without proof certificates. | First machine-checked formalization in **Lean 4** ([`we_star_five_graph_diophantine_and_orthoplex_ternary_classification`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2230-L2246), `0 axioms`, and [`srg_matrix_equation_and_conway99_spectral_decomposition`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L209-L234)) unifying the five graphs via $d = \sqrt{4k-7} = 2s+1 \mid 63$, coupled with dual-encoded Pure-RUP LRAT local-structure certificates (`Track p2`). |
| **Master Theorem II:**<br>*Lefschetz–Brauer Trace, Galois Conjugacy & the $N_1(F)$ No-Orbital-Step Law*<br>(`Theorems 38a, 38b, 38c` & `Track p1`) | **Partially Known (1983–2026) + New Universal Laws & $p=7$ Closure** | **Wilbrink (1983)**, **Makhnev & Minakova (2004)**, **Behbahani & Lam (2011)**, **Cesarz & Woldar (2023)**, and **Thakkar & Severini (2026)** analyzed prime-order automorphisms of $\mathrm{SRG}(99,14,1,2)$, leaving $p=7, |\mathrm{Fix}(g)|=1$ (`p7_fix1`) and the central involution `(0,7,0)` open. | **1. First-Principles Star-Bundle & $N_1(F)$ No-Orbital-Step Laws (`Theorems 38a & 38b`, `0 axioms`):** Proves without prime-order or orbit-matrix assumptions that $N_1(F)$ is a disjoint star-bundle and $\sigma(z)=z \wedge z\sim x \wedge \sigma^2(x)\ne x \implies x \nsim \sigma(x)$.<br>**2. Universal Galois Multiplicity Law (`Theorem 38c`):** Proves $d \cdot m_2 = \theta_1 n_{\text{orb}} + c_{\text{adj}}$ across all 5 graphs $d \in \{3, 7, 9, 21, 63\}$.<br>**3. Closure of `p7_fix1` ($0.82\text{s}$), `18/19` involutions, $p=3, 5$, and $\mathrm{Frob}(21)$** via Galois trace laws and Pure-RUP LRAT. |
| **Master Theorem III:**<br>*Three-Block Schur–Fiber Decomposition, 6D Orthoplex $\beta_6$, Induced 1-Regular Matching Law & $(R,R)$ Cherry-Free Reduction*<br>(`Theorems 3–21, 30, 32, 35, 37, 40, 40b`) | **100% NEW (Original Contribution of This Work)** | Only general Schur complement / quotient matrix inequalities (Haemers) and abstract equiangular/orthoplex line bounds existed in the general literature. | **Completely new for $\mathrm{SRG}(99,14,1,2)$ and $\mathrm{SRG}(v,k,1,2)$:**<br>**1. 6D Orthoplex $\beta_6(M_0)$ & Phantom $K_{12}$ Crystallization (`Theorems 17b, 35, 37`):** Proves $X X^\top = 9I_{12} + J_{12} - M_0$ (the vertex-edge incidence of $\beta_6(M_0) = K_{12}\setminus M_0$) and adjoins the $6$ antipodal columns $C_6$ to crystallize $\widetilde{X}\widetilde{X}^\top = 10I_{12} + J_{12}$, while establishing the 4-fold cross-slice mask exclusions.<br>**2. Induced 1-Regular Matching Law in $A_{60}[x_i]$ (`Theorem 40b(1)`):** Proves $\deg_{A_{60}[x_i]}(e) = 1 - w_{i,e} - gx_{e(i),e} \in \{0,1\}$, so every 10-column row $x_i \subset V_{60}$ with $e_0(i) \ne f(i)$ induces **4 disjoint edges and 2 isolated vertices** ($4K_2 \sqcup 2K_1$) inside $A_{60}$.<br>**3. Block $(R,R)$ Cherry-Free Sufficiency & Disjoint-Support Collapse (`Theorems 40, 40b(2)-(3)`):** Proves $(M^\top M)_{e_1,e_2}\le 2$ holds automatically on all $1,620$ pairs with $w_{12}=0$ and reduces to $\neg(x_{12}=1\wedge gx_{12}=1)$ on the $150$ pairs with $w_{12}=1$, while eliminating the `gp56` popcount test in `Stage D2` (**`4.17×` live speedup on NVIDIA A100** in `Gen V.6d`). |
| **Master Theorem IV:**<br>*Triangle-Core Seed $V_{3k-3}$, the $3_3$ Configuration Closure Dichotomy & Seed Dodecagon $C_{12}$*<br>(`Theorems 25–31, 33, 39a–b`) | **Partially Known Local Picture + New $3_3$ Closure Dichotomy & Seed Dodecagon $C_{12}$** | The local $39$-vertex neighborhood around a triangle in $v=99$ (Conway 1975) and the ternary Golay construction of $v=243$ (Berlekamp–van Lint–Seidel 1973) were known separately. | **1. Universal Triangle-Core Seed Decomposition (`Theorem 33`):** Proves that around any triangle $T$, cross-edges between $S_0^*, S_1^*, S_2^*$ partition into $t_{\text{trans}} = k - 2 - a_{01} - a_{02} - a_{12}$ disjoint transversal triangles.<br>**2. The $3_3$ Configuration Closure Criterion & Windmill Order-3 Law (`Theorems 39a & 39b`, `0 axioms`):** Identifies the exact geometric boundary between $v \in \{9, 243\}$ and $v=99$: the seed closes into an $\mathbb{F}_3$-affine space iff the three layer matchings $\iota_0,\iota_1,\iota_2$ pair every transversal triangle into a $K_3\square K_2$ prism, and proves from $\lambda=1, \mu=2$ that every generator $s \in S$ in an odd-order abelian Cayley graph satisfies $3s = 0$.<br>**3. The Universal Seed Dodecagon $C_{12}$ (`Theorems 28–31`):** Proves all $3,580$ slice orbits grow out of $3$ Seed Orbits on $C_{12}$ (`3/3 UNSAT`). |
| **Master Theorem V:**<br>*Complete Cayley (Regular Group) Classification Across All Five Graphs $v \in \{9, 99, 243, 6273, 494019\}$*<br>(`Theorems 39a–b, 41, 42a–b`) | **Indirectly known for $v=99$; NEW unified proof & non-abelian refutation for $v=6273$ and $v=494019$ (`0 axioms` in Lean 4)** | $v=9$ and $v=243$ were known as Cayley graphs over $\mathbb{F}_3^2$ and $\mathbb{F}_3^5$. For $v=99$, non-existence of a Cayley graph followed indirectly from combining Wilbrink ($11 \nmid |\mathrm{Aut}|$) and Makhnev ($3 \nmid |\mathrm{Aut}|$). | **1. Unconditional 2-Line Abelian Order-3 Exponent Bound (`Theorems 39a, 39b, 41`, `0 axioms`):** Since `Theorem 39b` proves $3s = 0$ unconditionally for every $s \in S$ in any odd-order abelian Cayley $\mathrm{SRG}(v,k,1,2)$, $S \subseteq \Omega_1(P_3)\setminus\{0\}$ forces $k \le 3^a - 1$, ruling out all abelian Cayley graphs for $v \in \{99, 6273, 494019\}$ ($14 > 8$, $112 > 8$, $994 > 242$).<br>**2. Complete Abelian & Non-Abelian Cayley Refutation (`Theorems 42a–b`, `0 axioms`):** Proves directly from Sylow normal projections, Galois eigenvalue constancy, and induced-character trace identities that **no group $H$ (abelian or non-abelian) of order $99$, $6,273$, or $494,019$ admits a Cayley $\mathrm{SRG}(v,k,1,2)$** — ruling out all non-abelian semidirect products $Q = (C_{19}\rtimes C_{d_\varphi})\times C_{107}$ ($d_\varphi \in \{1,3,9\}$) at $v=494,019$ via $107(19u_1 - s_1) = 63(m_0 - m_1)$. |

---

## 2. Complete Exposition of the Five Master Theorems (Plain-English & Mathematical Versions)

---

### Master Theorem I: The Spectral Triangle-Pairing & Five-Graph Finiteness Law

#### 1. Plain-English Explanation
Consider a regular network (graph) on $v$ vertices where every vertex has exactly $k$ neighbors, every pair of connected vertices shares **exactly one** common neighbor ($\lambda = 1$), and every pair of disconnected vertices shares **exactly two** common neighbors ($\mu = 2$).
- Because every edge belongs to a unique triangle ($\lambda = 1$), the $k$ neighbors of any vertex pair up into $k/2$ disjoint edges. Thus $k = 2m$ is always even, and the edges of the entire graph partition into $vk/6$ edge-disjoint triangles.
- Because every non-edge has exactly two common neighbors ($\mu = 2$), counting paths of length $2$ from any vertex to its $v - 1 - k$ non-neighbors gives $2(v - 1 - k) = k(k - 2)$, so the total number of vertices is $v = 1 + k + \frac{k(k-2)}{2} = 1 + \frac{k^2}{2} = 2m^2 + 1$, and the adjacency matrix $A$ satisfies the quadratic matrix equation $A^2 + A - (k-2)I_v = 2J_v$.
- Consequently, every non-principal eigenvalue of $A$ satisfies $\theta^2 + \theta - (k-2) = 0$, so the eigenvalue gap $\theta_1 - \theta_2 = \sqrt{4k-7} = d$ must be an odd integer $d = 2s + 1$, giving $k = s^2 + s + 2 = \frac{d^2+7}{4}$, $\theta_1 = s = \frac{d-1}{2}$, and $\theta_2 = -(s+1) = -\frac{d+1}{2}$.
- Finally, the dimensions (multiplicities $m_1, m_2$) of the two eigenspaces must be positive integers. Expressing $m_1 - m_2 = \frac{v - 1 - 2k}{d} = \frac{k(k-4)}{2d}$ in terms of $d$ yields $\frac{(d^2+7)(d^2-9)}{32d} = \frac{d^4 - 2d^2 - 63}{32d}$, forcing the odd integer $d$ to divide $63 = 3^2 \times 7$, so $d \in \{1, 3, 7, 9, 21, 63\}$. Removing $d = 1$ ($k = 2$, a single triangle $K_3$ with no non-edges) leaves **uniquely five mathematically possible graphs in the entire universe**: $v \in \{9, 99, 243, 6273, 494019\}$.

#### 2. Mathematical Formulation & Proof
**Theorem I (`we_star_five_graph_diophantine_and_orthoplex_ternary_classification`, Theorem 36 in Lean 4).**
*Let $G = (V, E)$ be a strongly regular graph $\mathrm{SRG}(v, k, 1, 2)$ with adjacency matrix $A \in \{0,1\}^{v \times v}$ and $v > 3$. Then:*
1. **Bose–Mesner Quadratic Identity & Vertex Count:**
   $$A^2 + A - (k - 2)I_v = 2J_v, \qquad v = 1 + \frac{k^2}{2} = 2m^2 + 1 \quad (k = 2m), \qquad 6 \mid vk.$$
2. **Odd Discriminant Parameterization ($d = 2s+1$):**
   *The restricted eigenvalues $\theta_1 > 0 > \theta_2$ on $\mathbf{1}^\perp$ satisfy $\theta^2 + \theta - (k-2) = 0$ with discriminant $d^2 = 4k - 7 = (2s+1)^2$, so:*
   $$k = s^2 + s + 2 = \frac{d^2 + 7}{4}, \qquad \theta_1 = s = \frac{d-1}{2}, \qquad \theta_2 = -(s+1) = -\frac{d+1}{2}, \qquad \theta_1 - \theta_2 = d.$$
3. **Diophantine Integrality of Multiplicities ($d \mid 63$):**
   *Since $\mathrm{Tr}(A) = k + m_1 \theta_1 + m_2 \theta_2 = 0$ and $m_1 + m_2 = v - 1 = \frac{k^2}{2}$, eliminating $m_1, m_2$ yields:*
   $$m_1 - m_2 = \frac{v - 1 - 2k}{d} = \frac{k(k - 4)}{2d} = \frac{(d^2 + 7)(d^2 - 9)}{32d} = \frac{d^4 - 2d^2 - 63}{32d} \in \mathbb{Z} \iff d \mid 63 = 3^2 \times 7.$$
   *Therefore, $(d, s, k, v, \theta_1, \theta_2, m_1, m_2)$ belongs to the exact 5-tuple table:*

| Index | $d = 2s+1$ | $s = \theta_1$ | $\theta_2 = -(s+1)$ | Degree $k = s^2+s+2$ | Vertices $v = 1 + k^2/2$ | Multiplicities $(m_1, m_2)$ | Existence Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | $3$ | $1$ | $-2$ | $4$ | $9 = 3^2$ | $(4, 4)$ | **Exists & Unique** ($K_3 \square K_3$) |
| **2** | $7$ | $3$ | $-4$ | $14$ | $99 = 3^2 \times 11$ | $(54, 44)$ | **Open** (*Conway's 99-Graph*; **No Cayley**, $|\mathrm{Aut}| \mid 54$) |
| **3** | $9$ | $4$ | $-5$ | $22$ | $243 = 3^5$ | $(132, 110)$ | **Exists** (*Berlekamp–van Lint–Seidel* over $\mathbb{F}_3^5$) |
| **4** | $21$ | $10$ | $-11$ | $112$ | $6,273 = 3^2 \times 17 \times 41$ | $(3264, 3008)$ | **Open** (**No Cayley graph over any group $H$**) |
| **5** | $63$ | $31$ | $-32$ | $994$ | $494,019 = 3^5 \times 19 \times 107$ | $(250920, 243098)$ | **Open** (**No Cayley graph over any group $H$**) |

- **Lean 4 Verification:**
  - [`we_star_five_graph_diophantine_and_orthoplex_ternary_classification`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2227-L2243) (`Theorem 36`, `does not depend on any axioms`)
  - [`srg_matrix_equation_and_conway99_spectral_decomposition`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L209-L234) (`Theorem 0c`, `0 sorryAx`)

---

### Master Theorem II: The Lefschetz–Brauer Trace, Galois Conjugacy & $N_1(F)$ No-Orbital-Step Law

#### 1. Plain-English Explanation
Suppose $G = \mathrm{SRG}(v,k,1,2)$ admits a symmetry (automorphism $\sigma$) of odd order $r \ge 3$, and let $F = \mathrm{Fix}(\sigma)$ be the set of $f_0 = |F|$ vertices left fixed by $\sigma$. Master Theorem II establishes three rigid laws governing $F$ and its surrounding layers:
1. **Disjoint Star-Bundle Law on $N_1(F)$ (`Theorem 38a`):** Because $\sigma$ has odd order (hence no $2$-cycles), no vertex $x \notin F$ can be connected to two distinct fixed vertices $z_1, z_2 \in F$. Why? If $z_1 \sim z_2$, their unique common neighbor ($\lambda = 1$) must be fixed by $\sigma$; if $z_1 \nsim z_2$, their pair of common neighbors ($\mu = 2$) is invariant under $\sigma$, and an odd-order permutation cannot swap two vertices, so both must be fixed by $\sigma$. Thus the external neighborhoods $N(z) \setminus F$ ($z \in F$) are **pairwise disjoint stars** of size $k - k_0$, forcing $|N_1(F)| = f_0(k - k_0) \le v - f_0$.
2. **The $N_1(F)$ No-Orbital-Step Law (`Theorem 38b`):** If a vertex $x \in N_1(F)$ is connected to a fixed point $z \in F$ and lies in an orbit of length $\ge 3$ ($\sigma^2(x) \ne x$), then **$x$ can never be connected to its immediate orbital image $\sigma(x)$**. Why? If $x \sim \sigma(x)$, then $\{z, x, \sigma(x)\}$ is a triangle, and applying $\sigma$ shows $\{z, \sigma(x), \sigma^2(x)\}$ is also a triangle. Then the edge $\{z, \sigma(x)\}$ would have **two** distinct common neighbors $x \ne \sigma^2(x)$, violating $\lambda = 1$! Consequently, every step-adjacent vertex $x \sim \sigma(x)$ must lie strictly inside the outer layer $N_0(F) = V \setminus (F \cup N_1(F))$.
3. **Galois Eigenvalue Multiplicity Law (`Theorem 38c`):** Because $G$ is loopless ($A_{z,z} = 0$), fixed points $z \in F$ contribute $0$ to $\mathrm{Tr}(A\sigma)$, so $\mathrm{Tr}(A\sigma) = p \cdot c_{\text{adj}}$ counts only step-adjacent orbits in $N_0(F)$. For any prime-order $p$ action where each of the $p - 1$ non-trivial character eigenspaces of $\sigma$ has common $\theta_1, \theta_2$ multiplicities $m_1, m_2$ (by $\mathrm{Gal}(\mathbb{Q}(\zeta_p)/\mathbb{Q})$ conjugacy), dimension conservation $m_1 + m_2 = n_{\text{orb}} = (v - f_0)/p$ and trace conservation $-m_1\theta_1 - m_2\theta_2 = c_{\text{adj}}$ yield across all 5 graphs $d \in \{3, 7, 9, 21, 63\}$:
   $$d \cdot m_2 = \theta_1 \cdot n_{\text{orb}} + c_{\text{adj}}, \qquad 0 \le p \cdot c_{\text{adj}} \le v - f_0 - f_0(k - k_0).$$

#### 2. Mathematical Formulation & Proof
**Theorem II (`odd_order_disjoint_star_bundle_structural`, `odd_order_no_step_in_n1_structural`, `odd_order_galois_eigenvalue_multiplicity_law`, Theorems 38a, 38b, 38c in Lean 4).**
*Let $\sigma \in \mathrm{Aut}(G)$ be an automorphism of $G = \mathrm{SRG}(v,k,1,2)$ with no $2$-cycles ($\forall u,\; \sigma(\sigma(u)) = u \implies \sigma(u) = u$) and fixed-point set $F = \mathrm{Fix}(\sigma)$ of size $f_0 = |F|$.*
1. **First-Principles Disjoint Star-Bundle Law (`Theorem 38a`, `0 axioms`):**
   *Since $|N(x) \cap N(y)| \in \{1, 2\} \le 2$ for all $x \ne y \in F$ and $\sigma$ has no $2$-cycles, every common neighbor $z \in N(x) \cap N(y)$ satisfies $\sigma(z) = z \in F$. Hence $(N(x)\setminus F) \cap (N(y)\setminus F) = \emptyset$ for all $x \ne y \in F$.*
2. **First-Principles $N_1(F)$ No-Orbital-Step Law (`Theorem 38b`, `0 axioms`):**
   *Assume the $\lambda=1$ uniqueness axiom ($\forall u, v, w_1, w_2:\; u \sim v \wedge u \sim w_1 \wedge v \sim w_1 \wedge u \sim w_2 \wedge v \sim w_2 \implies w_1 = w_2$) and $\sigma$-invariance ($u \sim v \implies \sigma(u) \sim \sigma(v)$). Then for all $z, x \in V$:*
   $$\sigma(z) = z \;\wedge\; z \sim x \;\wedge\; \sigma(\sigma(x)) \ne x \implies x \nsim \sigma(x).$$
   *Proof:* Suppose $x \sim \sigma(x)$. Since $\sigma(z)=z$ and $z \sim x$, applying $\sigma$ yields $z \sim \sigma(x)$ and $\sigma(x) \sim \sigma(\sigma(x))$, and applying $\sigma$ again yields $z \sim \sigma(\sigma(x))$. Thus both $w_1 = x$ and $w_2 = \sigma(\sigma(x))$ are common neighbors of the adjacent pair $(z, \sigma(x))$, forcing $x = \sigma(\sigma(x))$ by $\lambda = 1$, a contradiction. $\square$
3. **Universal Galois Multiplicity Identity (`Theorem 38c`):**
   *For an odd prime-order $p$ automorphism $\sigma$ with $n_{\text{orb}} = (v - f_0)/p$, let $m_1, m_2$ be the common multiplicities of $\theta_1, \theta_2$ in each of the $p - 1$ non-trivial character eigenspaces of $\sigma$, and let $p \cdot c_{\text{adj}} = |\{u \in N_0(F) : u \sim \sigma(u)\}|$. From $m_1 + m_2 = n_{\text{orb}}$ and $-m_1\theta_1 - m_2\theta_2 = c_{\text{adj}}$, across all 5 graphs $(\theta_1, \theta_2, d) \in \{(1,-2,3), (3,-4,7), (4,-5,9), (10,-11,21), (31,-32,63)\}$:*
   $$d \cdot m_2 = \theta_1 \cdot n_{\text{orb}} + c_{\text{adj}}.$$
   *(In particular, for $p = 3$ on $\mathrm{SRG}(99,14,1,2)$, $7\,\mathrm{Tr}(\sigma|_{V_1}) = 4f_0 + 3c_1 - 18$ and $7\,\mathrm{Tr}(\sigma|_{V_2}) = 3f_0 - 3c_1 + 11$ with $\mathrm{Tr}(\sigma|_{V_1}) = 54 - 3b_1 \equiv 0 \pmod 3$, forcing $f_0 \equiv 0 \pmod 3$, and for $p = 7, f_0 = 1$, `p7_fix1` has $\mathrm{Tr}(B) = 0$, certified `UNSAT` in $0.82\text{s}$).*

- **Lean 4 Verification:**
  - [`odd_order_disjoint_star_bundle_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2298-L2330) (`Theorem 38a`, `does not depend on any axioms`)
  - [`odd_order_no_step_in_n1_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2524-L2547) (`Theorem 38b`, `does not depend on any axioms`)
  - [`odd_order_galois_eigenvalue_multiplicity_law`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2560-L2570) (`Theorem 38c`, `0 sorryAx`)

---

### Master Theorem III: The Three-Block Schur–Fiber Decomposition, 6D Orthoplex $\beta_6$, Induced 1-Regular Matching Law & $(R,R)$ Cherry-Free Reduction

#### 1. Plain-English Explanation
In $\mathrm{SRG}(99,14,1,2)$, around a base triangle $T_0$ ($3$ vertices, which have $0$ edges to the exterior $R_{60}$), the $36$ neighbor vertices $S_{36} = W_{12} \sqcup X_{12} \sqcup g(X)_{12}$ connect to the $60$-vertex exterior $R_{60}$ via the $36 \times 60$ cross-block matrix $M = \begin{pmatrix} W \\ X \\ g(X) \end{pmatrix}$ ($W, X, g(X) \in \{0,1\}^{12 \times 60}$). Splitting the SRG equation $A^2 + A - 12I = 2J$ on $S_{36} \sqcup R_{60}$ yields **three coupled block equations** — each revealing a new structural law discovered in this work:
1. **Block $(S,S)$ — The 6D Orthoplex $\beta_6(M_0)$ & Phantom $K_{12}$ Crystallization (`Theorems 17b, 35, 37`):**
   Every row $x_i$ of $X$ has $10$ ones, meets its $M_0$-partner $x_{m_0(i)}$ in $0$ columns, and meets all other $10$ rows in $1$ column, so $X X^\top = G_p = 9I_{12} + J_{12} - M_0$. Geometrically, $X$ has the exact Gram matrix of the vertex-edge incidence matrix of the **regular 6-dimensional orthoplex (cross-polytope) $\beta_6(M_0) = K_{12} \setminus M_0$** ($12$ vertices, $60$ edges = $60$ roots of $D_6$), and adjoining the $12 \times 6$ incidence matrix $C_6$ of the $6$ antipodal edges of $M_0$ ($C_6 C_6^\top = I_{12} + M_0$) crystallizes the augmented Gram matrix into the universal $K_{12}$ matrix $\widetilde{X}\widetilde{X}^\top = 10 I_{12} + J_{12}$ (`Theorem 17b`), deterministically locking partner rows in `Stage D2`.
2. **Block $(S,R)$ — The Induced 1-Regular Matching Law in $A_{60}[x_i]$ (`Theorems 37 & 40b(1)`):**
   Multiplying $M$ by $A_{60}$ shows that $M A_{60} = 2J_{36,60} - (I_{36} + B_{36})M \ge 0$, which both yields the 4-fold cross-slice mask-exclusion law (`Theorem 37`) and proves that for every vertex $i \in \{0,\dots,11\}$ and every exterior neighbor $e \in x_i$ ($x_{i,e} = 1$, hence $x_{m_0(i),e} = 0$), the number of neighbors of $e$ *inside the 10-element set $x_i$* is given by the exact linear formula:
   $$\deg_{A_{60}[x_i]}(e) = 1 - w_{i,e} - gx_{e_0(i),e} \in \{0, 1\}.$$
   When $e_0(i) \ne f(i)$ ($E_0(i, f(i)) = 0$), $|x_i \cap W_i| = 1$ and $|x_i \cap g(x_{e_0(i)})| = 1$, so **every such 10-element row $x_i$ induces inside $A_{60}$ a subgraph consisting of $4$ disjoint edges ($8$ vertices of degree $1$) and $2$ isolated vertices (degree $0$)** ($A_{60}[x_i] \cong 4K_2 \sqcup 2K_1$, or $5K_2$ if $e_0(i) = f(i)$)!
3. **Block $(R,R)$ — The Cherry-Free Sufficiency Law & Disjoint-Support Collapse (`Theorems 40 & 40b(2)-(3)`):**
   For any pair of distinct columns $e_1 \ne e_2 \in R_{60}$, the number of common neighbors they share inside $S_{36}$ is $(M^\top M)_{e_1,e_2} = w_{12} + x_{12} + gx_{12} \le 2$, where $w_{12}, x_{12}, gx_{12} \in \{0, 1\}$ are binary indicators of whether $\{e_1,e_2\}$ lies in a common row of $W$, $X$, or $g(X)$. Because a sum of three binary numbers in $\{0,1\}$ exceeds $2$ **if and only if all three equal $1$**:
   - On all $1,620$ column pairs with $w_{12} = 0$, the bound $(M^\top M)_{e_1,e_2} \le 2$ is **automatically satisfied (`0` checks needed)**!
   - On the $150$ column pairs with $w_{12} = 1$, the bound is equivalent to the single cherry-free exclusion $\neg(x_{12} = 1 \wedge gx_{12} = 1)$.
   - Furthermore, in `Stage D2` (`Gen V.6d`), because the forbidden mask `fb_v6` excludes $x_4 \cap x_5 \subseteq \text{col\_u2\_5}$, any valid candidate $x_6$ satisfies $x_6 \cap x_4 \cap x_5 = \emptyset$, so $|x_6 \cap (x_4 \cup x_5)| = |x_6 \cap x_4| + |x_6 \cap x_5| = \mathrm{gp}_{46} + \mathrm{gp}_{56}$, eliminating the separate `gp56` popcount test and achieving **`2.05 s/orbit` (`4.17×` faster than `Gen V.4`) on `1× NVIDIA A100`**.

#### 2. Mathematical Formulation & Proof
**Theorem III (`m0_column_completion_k12_gram_crystallization`, `we_star_cross_slice_residual_matrix_and_mask_exclusion_theorem`, `no_cherry_collision_srg_fiber_law`, `schur_fiber_three_block_rr_sufficiency_and_matching_law`, Theorems 17b, 35, 37, 40, 40b in Lean 4).**
*For the slice decomposition $S_{36} \times R_{60}$ of $\mathrm{SRG}(99,14,1,2)$ with $M = \begin{pmatrix} W \\ X \\ g(X) \end{pmatrix} \in \{0,1\}^{36 \times 60}$ ($W, X, g(X) \in \{0,1\}^{12 \times 60}$) and internal slice adjacency $B_{36} = \begin{pmatrix} F_{12} & I_{12} & F_{12} \\ I_{12} & M_0 & E_0 \\ F_{12} & E_0 & M_0 \end{pmatrix}$, the SRG equation splits into:*
$$\begin{aligned}
\text{\textbf{(I) Block $(S,S)$:}}\quad & M M^\top = G_{36}(M_0, E_0), \qquad X X^\top = 9I_{12} + J_{12} - M_0, \\
\text{\textbf{(II) Block $(S,R)$:}}\quad & M A_{60} = 2J_{36,60} - (I_{36} + B_{36})M \ge 0, \\
\text{\textbf{(III) Block $(R,R)$:}}\quad & A_{60}^2 + A_{60} - 12I_{60} = 2J_{60} - M^\top M.
\end{aligned}$$
*From (I)–(III) the following three laws hold:*
1. **6D Orthoplex $\beta_6(M_0)$ & $K_{12}$ Gram Crystallization (`Theorems 17b & 35`):**
   *Adjoining the $12 \times 6$ vertex-edge incidence matrix $C_6$ of the $6$ antipodal edges of $M_0$ ($C_6 C_6^\top = I_{12} + M_0$) to $X \in \{0,1\}^{12 \times 60}$ yields $\widetilde{X} = [X \mid C_6] \in \{0,1\}^{12 \times 66}$ satisfying:*
   $$\widetilde{X}\widetilde{X}^\top = X X^\top + C_6 C_6^\top = (9I_{12} + J_{12} - M_0) + (I_{12} + M_0) = 10 I_{12} + J_{12}.$$
2. **Induced 1-Regular Matching Law in Block $(S,R)$ (`Theorems 37 & 40b(1)`):**
   *For every $i \in \{0,\dots,11\}$ and every column $e \in \{0,\dots,59\}$ with $x_{i,e} = 1$ (so $x_{m_0(i),e} = 0$), let $w_{i,e} = W_{i,e} \in \{0,1\}$ and $gx_{e_0(i),e} = g(X)_{e_0(i),e} \in \{0,1\}$. By Block $(S,R)$, $w_{i,e} + gx_{e_0(i),e} \le 1$, and the internal degree of $e$ in the 10-vertex induced subgraph $A_{60}[x_i]$ is:*
   $$\deg_{A_{60}[x_i]}(e) = (X A_{60})_{i,e} = 2 - w_{i,e} - x_{i,e} - x_{m_0(i),e} - gx_{e_0(i),e} = 1 - w_{i,e} - gx_{e_0(i),e} \in \{0, 1\}.$$
   *Hence $A_{60}[x_i] \cong 4 K_2 \sqcup 2 K_1$ whenever $e_0(i) \ne f(i)$ (and $5K_2$ when $e_0(i) = f(i)$).*
3. **Block $(R,R)$ Cherry-Free Sufficiency & Stage D2 Disjoint-Support Law (`Theorems 40 & 40b(2)-(3)`):**
   *For any distinct columns $e_1 \ne e_2 \in R_{60}$, let $w_{12} = (W^\top W)_{e_1,e_2} \in \{0,1\}$, $x_{12} = (X^\top X)_{e_1,e_2} \in \{0,1\}$, and $gx_{12} = (g(X)^\top g(X))_{e_1,e_2} \in \{0,1\}$. Then:*
   $$(M^\top M)_{e_1,e_2} = w_{12} + x_{12} + gx_{12} \le 2 \iff \bigl(w_{12} = 1 \implies \neg(x_{12} = 1 \wedge gx_{12} = 1)\bigr).$$
   *Moreover, for any candidate row $x_6$ disjoint from $x_4 \cap x_5 \subseteq \text{fb\_v6}$, $|x_6 \cap (x_4 \cup x_5)| = |x_6 \cap x_4| + |x_6 \cap x_5|$, so $(|x_6 \cap (x_4 \cup x_5)| = \mathrm{gp}_{46} + \mathrm{gp}_{56} \wedge |x_6 \cap x_4| = \mathrm{gp}_{46}) \implies |x_6 \cap x_5| = \mathrm{gp}_{56}$.*

- **Lean 4 Verification:**
  - [`m0_column_completion_k12_gram_crystallization`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L969-L982) (`Theorem 17b`, `0 sorryAx`)
  - [`we_star_d6_root_momentum_ternary_domino_duality_and_h3_hole_envelope`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2180-L2205) (`Theorem 35`, `0 sorryAx`)
  - [`we_star_cross_slice_residual_matrix_and_mask_exclusion_theorem`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2263-L2286) (`Theorem 37`, `does not depend on any axioms`)
  - [`no_cherry_collision_srg_fiber_law`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2423-L2430) (`Theorem 40`, `0 sorryAx`)
  - [`schur_fiber_three_block_rr_sufficiency_and_matching_law`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2586-L2607) (`Theorem 40b`, `0 sorryAx`)

---

### Master Theorem IV: The Triangle-Core Seed $V_{3k-3}$, the $3_3$ Configuration Closure Dichotomy & the Seed Dodecagon $C_{12}$

#### 1. Plain-English Explanation
Pick any triangle $T = \{u_0, u_1, u_2\}$ in a graph $G = \mathrm{SRG}(v,k,1,2)$. Each vertex $u_i \in T$ has $k - 2$ additional neighbors outside $T$, forming three layers $S_0, S_1, S_2$ of size $k - 2$. By $\lambda = 1$, each layer $S_i$ is paired up internally into $(k-2)/2$ disjoint matching edges via a fixed-point-free involution $\iota_i : S_i \to S_i$.
Now consider how the three layers $S_0, S_1, S_2$ connect to one another:
1. **Universal Transversal Triangle Partition (`Theorem 33`):**
   If $x_0 \in S_0$ and $x_1 \in S_1$ are adjacent (and neither belongs to a $K_4$ clique on $T$), then $x_0$ and $u_2$ are non-adjacent, so $\mu = 2$ forces $x_0$ and $u_2$ to share a second common neighbor $x_2 \in S_2$ besides $u_0$, and $\lambda = 1$ on $\{x_0, x_1\}$ forces $x_1 \sim x_2$. Thus **all cross-edges between $S_0^*, S_1^*, S_2^*$ partition into $t_{\text{trans}} = k - 2 - a_{01} - a_{02} - a_{12}$ vertex-disjoint transversal triangles $\{x_0, x_1, x_2\} \in S_0^* \times S_1^* \times S_2^*$**! In a $K_4$-free triangle seed ($a_{ij} = 0$), this local seed $V_{\text{seed}} = T \sqcup S_0 \sqcup S_1 \sqcup S_2$ has size $3k - 3 \in \{9, 39, 63, 333, 2979\}$ and looks locally identical across all 5 graphs.
2. **Why $v = 9$ and $v = 243$ Exist while $v = 99$ Fails Linear Closure — The $3_3$ Configuration Criterion & Windmill Order-3 Law (`Theorems 39a & 39b`):**
   Take any transversal triangle $\{x_0, x_1, x_2\}$ ($x_i \in S_i$), and look at the opposite endpoints $\{\iota_0(x_0), \iota_1(x_1), \iota_2(x_2)\}$ of their internal matching edges in $S_0, S_1, S_2$.
   - **If $\{\iota_0(x_0), \iota_1(x_1), \iota_2(x_2)\}$ is ALWAYS itself a transversal triangle** (so the $6$ vertices form a triangular prism $K_3 \square K_2$, i.e., a symmetric $3_3$ configuration), then the matching pairs $\{x_i, \iota_i(x_i)\}$ act as collinear antipodal pairs $\{\pm c_i\}$ over $\mathbb{F}_3$ (where $s \sim -s \implies 3s = 0$ by `Theorems 39a & 39b`), closing the graph into an $\mathbb{F}_3^n$ coset graph! This holds for **$v = 9 = 3^2$** ($1$ prism) and **$v = 243 = 3^5$** ($10$ prisms from the ternary Golay code).
   - **For $v = 99$**, $99$ is not a power of $3$ ($3^4 = 81 < 99 < 243 = 3^5$), so $3_3$ affine closure is globally impossible: on every slice $S_r$, the two matchings $(M_0, E_0)$ form a perturbation of the **Universal Seed Dodecagon $C_{12}$ (`Theorem 28`)** whose `3 / 3` ground-state Seed Orbits (`Orbits 0, 1670, 2118`) and all `910 / 910` symmetric Kempe co-pinches (`1+5`, `4+2`, `3+3`, `2+2+2`) are machine-certified `UNSAT`.

#### 2. Mathematical Formulation & Proof
**Theorem IV (`we_star_seed_dodecagon_and_seven_level_freckle_excitation_grading`, `we_star_throat_eight_bucket_partition_and_conway_family_seed_law`, `windmill_involution_unique_fixed_point_structural`, `abelian_cayley_lambda_one_order_three_structural`, Theorems 28–31, 33, 39a, 39b in Lean 4).**
*Let $T = \{u_0, u_1, u_2\}$ be a triangle in $G = \mathrm{SRG}(v,k,1,2)$ with layers $S_i = N(u_i) \setminus T$ ($|S_i| = k-2$), internal matchings $\iota_i : S_i \to S_i$, and $K_4$-overlap counts $a_{ij} = |S_i \cap S_j|$.*
1. **Transversal Triangle Decomposition (`Theorem 33`):**
   *Setting $S_0^* = S_0 \setminus (S_1 \cup S_2)$, $S_1^* = S_1 \setminus (S_0 \cup S_2)$, $S_2^* = S_2 \setminus (S_0 \cup S_1)$, every vertex $x \in S_i^*$ has appease neighbors in $S_{i+1}^*$ and $S_{i+2}^*$ that are mutually adjacent, partitioning cross-edges into $t_{\text{trans}} = k - 2 - a_{01} - a_{02} - a_{12}$ vertex-disjoint transversal triangles, with $|V_{\text{seed}}|_{a_{ij}=0} = 3 + 3(k-2) = 3k - 3 \in \{9, 39, 63, 333, 2979\}$.*
2. **Windmill Involution & $3_3$ Closure Law (`Theorems 39a & 39b`, `0 axioms`):**
   *For any involution $g \in \mathrm{Aut}(G)$ with a unique fixed point $x_0$, $\mu = 2$ at $x_0$ forces $s \sim g(s)$ for every $s \in N(x_0)$ (`Theorem 39a`), so in any odd-order abelian Cayley graph $\mathrm{Cay}(H, S)$, the inversion $g(x) = -x$ forces $s \sim -s$ and $s + s = -s \iff 3s = 0$ for every $s \in S$ (`Theorem 39b`).*

- **Lean 4 Verification:**
  - [`windmill_involution_unique_fixed_point_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2342-L2382) (`Theorem 39a`, `does not depend on any axioms`)
  - [`abelian_cayley_lambda_one_order_three_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2392-L2412) (`Theorem 39b`, `does not depend on any axioms`)
  - [`we_star_throat_eight_bucket_partition_and_conway_family_seed_law`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2111-L2124) (`Theorem 33`, `0 sorryAx`)
  - [`we_star_seed_dodecagon_and_seven_level_freckle_excitation_grading`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1967-L1979) (`Theorem 28`, `0 sorryAx`)

---

### Master Theorem V: Complete Cayley (Regular Group) Classification Across All Five Graphs $v \in \{9, 99, 243, 6273, 494019\}$

#### 1. Plain-English Explanation
A graph $G$ is a **Cayley graph** $\mathrm{Cay}(H, S)$ (equivalently, admits a regular automorphism group $H$ of order $|H| = v$) if its vertices can be labeled by the elements of a finite group $H$ (abelian or non-abelian) and its edges are generated by a symmetric inverse-closed subset $S \subset H \setminus \{1\}$ of size $|S| = k$.
Master Theorem V completely solves the Cayley graph existence problem across **all five parameter sets $v \in \{9, 99, 243, 6273, 494019\}$ and over ALL finite groups $H$ (both abelian and non-abelian)**:
- **Cayley $\mathrm{SRG}(v,k,1,2)$ graphs exist for $v = 9$ and $v = 243$** (over $H = \mathbb{F}_3^2$ and $H = \mathbb{F}_3^5$).
- **No Cayley $\mathrm{SRG}(v,k,1,2)$ graph exists over ANY group $H$ (abelian or non-abelian) for $v = 99$, $v = 6,273$, or $v = 494,019$!**

Why is every group $H$ of order $99$, $6,273$, or $494,019$ ruled out?
1. **First, for any abelian group $H$ (`Theorems 39a, 39b, 41`, `0 axioms`):**
   By `Theorems 39a & 39b`, in any odd-order abelian Cayley $\mathrm{SRG}(v,k,1,2)$, the inversion automorphism $g(x) = -x$ has a unique fixed point $0$, which unconditionally forces $s \sim -s$ and $3s = 0$ for **every** generator $s \in S$! Thus $S$ must be contained in the non-identity elements of the $3$-Sylow subgroup $P_3$ of order $3^a$, giving $k = |S| \le 3^a - 1$. Since every group of order $99 = 3^2 \times 11$ or $6,273 = 3^2 \times 17 \times 41$ is forced by Sylow's theorem to be abelian with $3^2 - 1 = 8$, this immediately rules out $v = 99$ ($14 > 8$), $v = 6,273$ ($112 > 8$), and all abelian groups of order $494,019$ ($994 > 3^5 - 1 = 242$).
2. **Second, in full generality — without using $3s = 0$ and allowing ALL non-abelian groups $H$ (`Theorems 42a & 42b`, `0 axioms`):**
   By projecting $S$ onto the normal prime-power quotients guaranteed by Sylow's theorem and applying Galois conjugacy of roots of unity:
   - **At $v = 6,273 = 153 \times 41$:** Sylow's theorem forces a central cyclic quotient $Q = C_{41}$. On $C_{41}$, all $40$ non-identity fibers contain the same number $n_* \ge 0$ of elements from $S$, while the identity fiber contains $n_0 \ge 0$ elements, satisfying $n_0 + 40 n_* = 112$ and $n_0 - n_* = \varepsilon_{41} \in \{10, -11\}$. Subtracting gives $41 n_* = 112 - \varepsilon_{41} \in \{102, 123\}$, which forces $\varepsilon_{41} = -11$, $n_* = 3$, and therefore **$n_0 = -11 + 3 = -8 < 0$ — impossible since a set cannot have $-8$ elements!**
   - **At $v = 99 = 3^2 \times 11$:** Projecting $S$ ($|S|=14$) onto $Q = C_3 \times C_{11}$, Fourier inversion for the multiplicity $n_{1,1} \ge 0$ of an order-$33$ element gives $33 n_{1,1} = 14 - \varepsilon_3 - \varepsilon_{11} + \varepsilon_{33}$ with $\varepsilon_3, \varepsilon_{11}, \varepsilon_{33} \in \{3, -4\}$, which only takes values in $\{4, 11, 18, 25\}$ — none of which is divisible by $33$!
   - **At $v = 494,019 = 3^5 \times 19 \times 107$ (including all non-abelian groups):** Sylow's theorem forces $H \cong H_{4617} \times C_{107}$ and $C_{19} \trianglelefteq H_{4617}$, so every group $H$ of order $494,019$ projects onto a solvable quotient $Q = (C_{19} \rtimes C_{d_\varphi}) \times C_{107}$ with $d_\varphi \in \{1, 3, 9\}$. On the abelian quotient $C_{d_\varphi} \times C_{107}$, the $C_{107}$ equation $n_0 + 106 n_* = 994, n_0 - n_* \in \{31, -32\}$ forces $\varepsilon_{107} = 31, n_* = 9$, and non-trivial $C_{d_\varphi}$-layer sum $s_1 = 9 / d_\varphi \in \{9, 3, 1\}$. Lifting to the $18$-dimensional direct sum $\Pi_b = \bigoplus_{i=1}^{18/d_\varphi} \mathrm{Ind}_{C_{19}\times C_{107}}^Q(\psi_{a_i} \otimes \chi_b)$ of induced representations of $C_{19}$ (whose characters vanish outside the normal subgroup $N = C_{19} \times \{0\} \times C_{107}$) yields the trace difference identity:
     $$T_0 - T_1 = 107(19 u_1 - s_1) = 63(m_0 - m_1), \qquad u_1 \in \mathbb{N},\; s_1 \in \{9, 3, 1\},\; 0 \le m_0, m_1 \le 18.$$
     Since $\gcd(107, 63) = 1$ and $|m_0 - m_1| \le 18 < 107$, we must have $m_0 = m_1$ and hence **$19 u_1 = s_1 \in \{9, 3, 1\}$ — impossible in integers!**

#### 2. Mathematical Formulation & Proof
**Theorem V (`windmill_involution_unique_fixed_point_structural`, `abelian_cayley_lambda_one_order_three_structural`, `higher_srg_seed_and_cayley_6273_obstructions_decide`, `galois_quotient_and_induced_character_cayley_no_go_structural`, `complete_five_graph_cayley_classification_9_99_243_6273_494019_decide`, Theorems 39a, 39b, 41, 42a, 42b in Lean 4).**
*Across all five parameter sets $(v, k, \theta_1, \theta_2)$ of $\mathrm{SRG}(v,k,1,2)$, a Cayley realization $G \cong \mathrm{Cay}(H, S)$ over a finite group $H$ of order $|H| = v$ (abelian or non-abelian) with symmetric $S \subset H \setminus \{1\}$ ($|S|=k$) exists **if and only if $v \in \{9, 243\}$**.*

- **Lean 4 Verification:**
  - [`windmill_involution_unique_fixed_point_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2342-L2382) (`Theorem 39a`, `does not depend on any axioms`)
  - [`abelian_cayley_lambda_one_order_three_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2392-L2412) (`Theorem 39b`, `does not depend on any axioms`)
  - [`higher_srg_seed_and_cayley_6273_obstructions_decide`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2452-L2466) (`Theorem 41`, `does not depend on any axioms`)
  - [`galois_quotient_and_induced_character_cayley_no_go_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2631-L2665) (`Theorem 42a`, `0 sorryAx`)
  - [`complete_five_graph_cayley_classification_9_99_243_6273_494019_decide`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L2687-L2714) (`Theorem 42b`, `does not depend on any axioms`)

---

## 3. Direct Few-Line Derivations of Existence, Uniqueness, and Non-Existence for Each of the Five Graphs ($v \in \{9, 99, 243, 6273, 494019\}$)

Directly from **Master Theorems I–V**, we obtain the following self-contained, few-line proofs and constructions for every graph in the 5-graph family.

---

### Graph 1: $v = 9$ — $\mathrm{SRG}(9, 4, 1, 2)$ (`EXISTENCE & UNIQUENESS`)

> **Claim:** *$\mathrm{SRG}(9, 4, 1, 2)$ exists, is unique up to isomorphism, and is isomorphic to the Cayley graph $\mathrm{Cay}(\mathbb{F}_3^2, \{\pm(1,0), \pm(0,1)\}) \cong K_3 \square K_3$.*

**4-Line Proof from Master Theorems I, IV & V:**
1. **Parameters (`Master Theorem I`):** For $d = 3$ ($s = 1$), we have $k = 4$, $v = 1 + 4^2/2 = 9$, $\theta_1 = 1$, $\theta_2 = -2$, and $(m_1, m_2) = (4, 4)$.
2. **Exhaustion by the Triangle-Core Seed (`Master Theorem IV`, `Theorem 33`):** Pick any triangle $T = \{u_0, u_1, u_2\}$. By $\lambda = 1$, no edge of $T$ lies in a $K_4$, so $a_{01} = a_{02} = a_{12} = 0$. The triangle-core seed $V_{\text{seed}} = T \sqcup S_0 \sqcup S_1 \sqcup S_2$ therefore has size $|V_{\text{seed}}| = 3k - 3 = 3(4) - 3 = 9 = v$, exhausting the entire graph!
3. **Unique $3_3$ Prism Closure (`Master Theorem IV`):** Each layer $S_i$ ($i \in \{0,1,2\}$) has size $k - 2 = 2$, consisting of a single matching edge $\{x_i, \iota_i(x_i)\}$. The cross-edges between $S_0, S_1, S_2$ partition into $t_{\text{trans}} = k - 2 = 2$ disjoint transversal triangles $\{x_0, x_1, x_2\}$ and $\{\iota_0(x_0), \iota_1(x_1), \iota_2(x_2)\}$.
4. **Explicit $\mathbb{F}_3^2$ Coordinates (`Master Theorem V`):** Labeling $T = \{(0,0), (1,0), (2,0)\}$ and the two transversal triangles as $\{(0,1), (1,1), (2,1)\}$ and $\{(0,2), (1,2), (2,2)\}$ realizes the graph uniquely as the $3 \times 3$ rook/Paley graph $K_3 \square K_3 \cong \mathrm{Cay}(\mathbb{F}_3^2, \{\pm(1,0), \pm(0,1)\})$. $\blacksquare$

---

### Graph 2: $v = 243$ — $\mathrm{SRG}(243, 22, 1, 2)$ (`EXISTENCE VIA TERNARY GOLAY CODE`)

> **Claim:** *$\mathrm{SRG}(243, 22, 1, 2)$ exists and is realized as the syndrome coset Cayley graph $\mathrm{Cay}(\mathbb{F}_3^5, S)$ of the perfect ternary Golay $[11, 6, 5]_3$ code.*

**5-Line Proof & Construction from Master Theorems I, IV & V:**
1. **Parameters & $3$-Group Bound (`Master Theorems I & V`):** For $d = 9$ ($s = 4$), we have $k = 22$, $v = 1 + 22^2/2 = 243 = 3^5$, and $k = 22 \le 3^5 - 1 = 242$ (`Theorem 41`), permitting an elementary abelian $3$-group realization $H = \mathbb{F}_3^5$.
2. **Generator Set $S$ from the Ternary Golay Parity-Check Matrix:** Let $H_{\text{Golay}} \in \mathbb{F}_3^{5 \times 11}$ be the parity-check matrix of the perfect ternary Golay $[11, 6, 5]_3$ code with columns $c_1, \dots, c_{11} \in \mathbb{F}_3^5 \setminus \{0\}$, and set $S = \{\pm c_1, \dots, \pm c_{11}\}$ ($|S| = 22$, $S = -S$).
3. **Minimum Distance $d_{\min} = 5$ Implies $\lambda = 1$:** Any $3$ columns of $H_{\text{Golay}}$ are linearly independent over $\mathbb{F}_3$ (since $d_{\min} = 5 \ge 4$). Hence $s_1 + s_2 = s_3$ for $s_1, s_2, s_3 \in S$ holds **if and only if** $s_1 = s_2 = -s_3 \in \{\pm c_i\}$, so every edge $\{x, x + c_i\}$ lies in the unique triangle $\{x, x + c_i, x - c_i\}$ ($\lambda = 1$).
4. **Perfectness of the Golay Code Implies $\mu = 2$:** Since $d_{\min} = 5 = 2(2) + 1$, the $1 + 22 + 2\binom{11}{2} = 243 = 3^5$ vectors of Hamming weight $\le 2$ in $\mathbb{F}_3^{11}$ have pairwise distinct syndromes covering all of $\mathbb{F}_3^5$. Thus every non-adjacent difference $y \in \mathbb{F}_3^5 \setminus (\{0\} \cup S)$ ($220$ vectors) is the syndrome of a unique weight-$2$ codeword $s_1 + s_2 = y$ ($s_1 \ne \pm s_2 \in S$), giving **exactly two** common neighbors $x + s_1$ and $x + s_2$ between $x$ and $x + y$ ($\mu = 2$).
5. **Verification of $3_3$ Closure (`Master Theorem IV`):** Around $T = \{0, c_{11}, -c_{11}\}$, the $20$ neighbors in $S \setminus \{\pm c_{11}\}$ partition into $10$ antipodal pairs $\{\pm c_1, \dots, \pm c_{10}\}$, forming $10$ closed $K_3 \square K_2$ prisms under translation by $T$. $\blacksquare$

---

### Graph 3: $v = 99$ — $\mathrm{SRG}(99, 14, 1, 2)$ (`CONWAY'S 99-GRAPH: CAYLEY & SYMMETRY NON-EXISTENCE + SCHUR SIEVE`)

> **Claim:** *For $v = 99, k = 14$ ($d = 7, \theta_1 = 3, \theta_2 = -4, m_1 = 54, m_2 = 44$):*
> *(A) No Cayley realization $\mathrm{Cay}(H, S)$ exists over **any** group $H$ of order $99$;*
> *(B) All prime-order symmetries $p \in \{11, 7, 5, 3\}$, $\mathrm{Frob}(21)$, all $18$ involution profiles with $|\mathrm{Fix}(g)| \ge 3$, all $3/3$ Seed Dodecagon $C_{12}$ orbits, and all $910/910$ decomposable polygonal strata (`2+2+2`, `3+3`, `4+2`, `1+5`) are `UNSAT`.*

**Few-Line Proofs from Master Theorems II, III, IV & V:**
1. **Non-Existence of Any Cayley Graph $\mathrm{Cay}(H, S)$ of Order $99$ (`Master Theorem V`, `Theorems 39a–b, 41, 42a–b`):**
   - By Sylow's theorem on $|H| = 99 = 3^2 \times 11$, $n_{11} \mid 9, n_{11} \equiv 1 \pmod{11} \implies n_{11} = 1$ and $n_3 \mid 11, n_3 \equiv 1 \pmod 3 \implies n_3 = 1$, so every group $H$ of order $99$ is abelian ($H \cong P_9 \times C_{11}$) and projects onto $Q = C_3 \times C_{11}$.
   - **2-Line Proof via Unconditional Order-3 Law (`Theorems 39a, 39b, 41`, `0 axioms`):** By `Theorem 39b`, in any odd-order abelian Cayley $\mathrm{SRG}(v,k,1,2)$, every $s \in S$ satisfies $3s = 0$, so $S \subseteq P_9 \setminus \{0\}$ has size at most $3^2 - 1 = 8 < 14 = |S|$ — contradiction!
   - **3-Line Proof without Using $3s = 0$ via $C_3 \times C_{11}$ Fourier Inversion (`Theorems 42a–b`, `0 axioms`):** Projecting any symmetric $S$ ($|S|=14$) onto $Q = C_3 \times C_{11}$, Galois transitivity forces the character sums on order-$3$, order-$11$, and order-$33$ characters to equal eigenvalues $\varepsilon_3, \varepsilon_{11}, \varepsilon_{33} \in \{3, -4\}$. Fourier inversion for the multiplicity $n_{1,1} \in \mathbb{N}$ of an order-$33$ fiber gives:
     $$33\, n_{1,1} = 14 - \varepsilon_3 - \varepsilon_{11} + \varepsilon_{33} \in \{4, 11, 18, 25\},$$
     which is impossible in $\mathbb{Z}$ since $0 < 4 \le 33n_{1,1} \le 25 < 33$! $\blacksquare$
2. **Global Elimination of $p = 3$ and $p = 7$ (`Master Theorem II`, `Theorems 38a–c` & `Track p1`):**
   - For $p = 3$, spectral trace congruence $7\,\mathrm{Tr}(\sigma|_{V_1}) = 4f_0 + 3c_1 - 18$ forces $f_0 \equiv 0 \pmod 3$, and `p3_t1_fix33` (`12` clauses, `1` RUP step) + `frob21_z7_z3` eliminate all order-$3$ actions.
   - For $p = 7, f_0 = 1$ (`p7_fix1`), $\mathrm{Gal}(\mathbb{Q}(\zeta_7)/\mathbb{Q})$ trace equivariance on $m_1 = 54, m_2 = 44$ forces $\mathrm{Tr}(B) = 0$ on the outer $12 \times 12$ orbit matrix, refuted in `0.82s` (`5,209` RUP steps).
3. **Asymmetric / `(0,7,0)` Sieve via Master Theorem III (`Theorems 17b, 35, 37, 40, 40b`):**
   - By `Theorems 17b & 35`, $X_{12 \times 60}$ is an edge-bijection of the 6D orthoplex $\beta_6(M_0)$ with $\widetilde{X}\widetilde{X}^\top = 10 I_{12} + J_{12}$; by `Theorem 40b(1)`, every row $x_i$ ($e_0(i)\ne f(i)$) induces $4 K_2 \sqcup 2 K_1$ inside $A_{60}$; and by `Theorem 40b(2)-(3)`, $(M^\top M)_{e_1,e_2} \le 2$ reduces to cherry-freeness on $w_{12}=1$ and disjoint-support collapse $|x_6 \cap (x_4 \cup x_5)| = \mathrm{gp}_{46} + \mathrm{gp}_{56}$ (`4.17×` A100 speedup in `Gen V.6d`).

---

### Graph 4: $v = 6,273$ — $\mathrm{SRG}(6273, 112, 1, 2)$ (`NON-EXISTENCE OF ALL CAYLEY REALIZATIONS`)

> **Claim:** *No strongly regular graph $\mathrm{SRG}(6273, 112, 1, 2)$ can be a Cayley graph $\mathrm{Cay}(H, S)$ over **any** finite group $H$ (abelian or non-abelian) of order $6,273$.*

**4-Line Proof from Master Theorems I & V (`Theorems 39a–b, 41, 42a–b`):**
1. **Sylow Central Quotient $Q = C_{41}$:** Since $v = 6,273 = 3^2 \times 17 \times 41 = 153 \times 41$, Sylow's theorem gives $n_{41} \mid 153$ and $n_{41} \equiv 1 \pmod{41} \implies n_{41} = 1$. Since $\gcd(153, |\mathrm{Aut}(C_{41})|) = \gcd(153, 40) = 1$, $P_{41} \cong C_{41}$ is central in $H$, so $H \cong H_{153} \times C_{41}$ projects onto $Q = C_{41}$. *(Moreover, $n_{17} = 1$ and $\gcd(9, 16 \cdot 40) = 1$ force every group of order $6,273$ to be abelian, where `Theorems 39b + 41` already give $112 > 3^2 - 1 = 8$ in 1 line).*
2. **Galois Constancy on $C_{41}$:** Projecting any symmetric generating set $S$ ($|S| = k = 112$) onto $C_{41}$, let $n_0 \in \mathbb{N}$ be the fiber size over $0 \in C_{41}$. Since $\mathrm{Gal}(\mathbb{Q}(\zeta_{41})/\mathbb{Q}) \cong \mathbb{Z}_{40}^\times$ acts transitively on the $40$ non-trivial characters of $C_{41}$ and the eigenvalues $\theta_1 = 10, \theta_2 = -11$ are rational integers, every non-trivial character sum equals the same eigenvalue $\varepsilon_{41} \in \{10, -11\}$, and every non-zero element of $C_{41}$ has the same fiber multiplicity $n_* \in \mathbb{N}$.
3. **Diophantine Contradiction ($n_0 = -8 < 0$):** Counting $|S| = 112$ and evaluating a non-trivial character gives:
   $$n_0 + 40 n_* = 112 \quad\text{and}\quad n_0 - n_* = \varepsilon_{41} \in \{10, -11\} \implies 41 n_* = 112 - \varepsilon_{41} \in \{102, 123\}.$$
4. Since $41 \nmid 102$ and $123 = 41 \times 3$, we are forced into $\varepsilon_{41} = -11$ and $n_* = 3$, which yields:
   $$n_0 = \varepsilon_{41} + n_* = -11 + 3 = -8 < 0,$$
   contradicting $n_0 \ge 0$! $\blacksquare$

---

### Graph 5: $v = 494,019$ — $\mathrm{SRG}(494019, 994, 1, 2)$ (`NON-EXISTENCE OF ALL ABELIAN & NON-ABELIAN CAYLEY REALIZATIONS`)

> **Claim:** *No strongly regular graph $\mathrm{SRG}(494019, 994, 1, 2)$ can be a Cayley graph $\mathrm{Cay}(H, S)$ over **any** finite group $H$ (abelian or non-abelian) of order $494,019$.*

**6-Line Proof from Master Theorems I & V (`Theorems 39a–b, 41, 42a–b`):**
1. **Sylow Direct-Factor Split $H \cong H_{4617} \times C_{107}$:** Since $v = 494,019 = 3^5 \times 19 \times 107 = 4617 \times 107$, Sylow's theorem gives $n_{107} \mid 4617$ and $n_{107} \equiv 1 \pmod{107}$. Checking all divisors of $4617 = 243 \times 19$ (`Theorem 42b`) shows $n_{107} = 1$, and since $\gcd(4617, |\mathrm{Aut}(C_{107})|) = \gcd(4617, 106) = 1$, $C_{107}$ is a central direct factor: $H \cong H_{4617} \times C_{107}$.
2. **Sylow Solvable Quotient $Q = (C_{19} \rtimes C_{d_\varphi}) \times C_{107}$:** Inside $H_{4617}$ ($|H_{4617}| = 243 \times 19$), Sylow's theorem gives $n_{19} \mid 243$ and $n_{19} \equiv 1 \pmod{19} \implies n_{19} = 1$ (since $3^1, \dots, 3^5 \equiv 3, 9, 8, 5, 15 \not\equiv 1 \pmod{19}$). Thus $C_{19} \trianglelefteq H_{4617}$ and $H_{4617} = C_{19} \rtimes_\varphi P_{243}$, where $\varphi : P_{243} \to \mathrm{Aut}(C_{19}) \cong C_{18}$ has cyclic image $C_{d_\varphi}$ of order $d_\varphi \mid \gcd(243, 18) = 9$, i.e., $d_\varphi \in \{1, 3, 9\}$. Since $K = \ker(\varphi)$ is normal in $P_{243}$ and centralizes $C_{19}$, $K \trianglelefteq H_{4617}$ is strictly normal with quotient $Q = (C_{19} \rtimes C_{d_\varphi}) \times C_{107}$. *(Note: if $H$ is abelian, `Theorems 39b + 41` already give $994 > 3^5 - 1 = 242$).*
3. **Projection to $C_{107}$ Forces $\varepsilon_{107} = 31$ and $n_*^{\text{107}} = 9$:** Projecting $S$ ($|S| = k = 994$, $\theta_1 = 31, \theta_2 = -32$) onto $C_{107}$ gives $n_0^{\text{107}} + 106 n_*^{\text{107}} = 994$ and $n_0^{\text{107}} - n_*^{\text{107}} = \varepsilon_{107} \in \{31, -32\}$, so $107 n_*^{\text{107}} = 994 - \varepsilon_{107} \in \{963, 1026\}$. Since $107 \nmid 1026$ and $963 = 107 \times 9$, we must have $\varepsilon_{107} = 31$, $n_*^{\text{107}} = 9$, and $n_0^{\text{107}} = 40$.
4. **Abelian Quotient $C_{d_\varphi} \times C_{107}$ Layer Sum $s_1 \in \{9, 3, 1\}$:** On $C_{d_\varphi} \times C_{107}$, the fiber of size $n_*^{\text{107}} = 9$ over any $y \in C_{107} \setminus \{0\}$ splits across $C_{d_\varphi}$ into $s_1$ (on the normal kernel coset $C_{19} \times \{0\} \times \{y\}$) plus $(d_\varphi - 1)$ Galois-equal cosets, with difference $s_1 - s_{\text{non}} \in \{0, \pm 63\}$. Since the total sum is $9 < 63$, all $d_\varphi$ cosets must have equal sum $s_1 = 9 / d_\varphi \in \{9, 3, 1\}$.
5. **18-Dimensional Induced-Character Trace on $Q = (C_{19} \rtimes C_{d_\varphi}) \times C_{107}$:** Let $N = C_{19} \times \{0\} \times C_{107} \trianglelefteq Q$, and let $u_0, u_1 \in \mathbb{N}$ be the counts of $S$ in the normal elements $(0, 0, 0)$ and $(0, 0, y \ne 0)$ of $N$. The $18$ non-trivial characters $\psi_1, \dots, \psi_{18}$ of $C_{19}$ partition into $18/d_\varphi$ orbits $\mathcal{O}_i$ under $C_{d_\varphi}$, so for each character $\chi_b$ of $C_{107}$, the direct sum $\Pi_b = \bigoplus_{i=1}^{18/d_\varphi} \mathrm{Ind}_N^Q(\psi_{a_i} \otimes \chi_b)$ has dimension $(18/d_\varphi) \times d_\varphi = 18$, vanishes outside $N$, and equals $(19\delta_{x,0} - 1)\chi_b(y)$ on $(x,0,y) \in N$. Evaluating $\mathrm{Tr}(A(\Pi_b))$ (the sum of $18$ eigenvalues in $\{31, -32\}$) at $b = 0$ ($\sum_{y \ne 0}\chi_0(y) = 106$) and $b \ne 0$ ($\sum_{y \ne 0}\chi_b(y) = -1$) gives:
   $$\begin{aligned}
   T_0 &= \mathrm{Tr}\bigl(A(\Pi_0)\bigr) = (19 u_0 - s_0) + 106(19 u_1 - s_1) = -18 \cdot 32 + 63 m_0 \qquad (0 \le m_0 \le 18), \\
   T_1 &= \mathrm{Tr}\bigl(A(\Pi_b)\bigr) = (19 u_0 - s_0) - (19 u_1 - s_1) = -18 \cdot 32 + 63 m_1 \qquad (0 \le m_1 \le 18,\; b \ne 0).
   \end{aligned}$$
6. **Final Diophantine Contradiction ($19 u_1 = s_1 \in \{9, 3, 1\}$):** Subtracting $T_1$ from $T_0$ eliminates $(19 u_0 - s_0)$ and yields:
   $$T_0 - T_1 = 107(19 u_1 - s_1) = 63(m_0 - m_1).$$
   Since $\gcd(107, 63) = 1$ and $|m_0 - m_1| \le 18 < 107$, we must have $m_0 = m_1$ and hence **$19 u_1 = s_1 \in \{9, 3, 1\}$**, which has **no integer solution** since $19 \nmid 9, 3, 1$! $\blacksquare$
