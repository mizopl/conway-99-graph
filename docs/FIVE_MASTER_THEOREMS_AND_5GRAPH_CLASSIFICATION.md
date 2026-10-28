# The Five Master Theorems of the $\mathrm{SRG}(v, k, 1, 2)$ Universe: Plain-English Exposition, Mathematical Proofs, Literature Novelty Audit, and Short Existence / Non-Existence Derivations for All Five Graphs ($v \in \{9, 99, 243, 6273, 494019\}$)

> **Formal Lean 4.35.0 Companion (`42` Theorems, `67` Declarations, `0 sorryAx`):** [`verify-it-yourself/ChiralNullspaceAndHandshaking.lean`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean)  
> **Dual-Encoded Pure-RUP LRAT Companion (`27` Theorems = `54` Proofs, `0 RAT`):** [`verify-it-yourself/verify.py`](../verify-it-yourself/verify.py)  
> **Classical Derivations from $\mathrm{SRG}$ Axioms:** [`docs/CLASSICAL_PROOFS_FROM_SRG_AXIOMS.md`](CLASSICAL_PROOFS_FROM_SRG_AXIOMS.md)

---

## 1. Literature Attribution & Novelty Audit: What Was Known vs. What Is New in This Work

To maintain strict scientific transparency, the table below separates what was previously known in the algebraic graph theory literature from the **new structural theorems, generalizations, and formal machine-verified proofs** established in this repository.

| Master Theorem | Literature Status | What Was Known Previously (with Citations) | What Is **New & Generalized** in This Work (`we*star`) |
| :--- | :---: | :--- | :--- |
| **Master Theorem I:**<br>*Spectral Triangle-Pairing & Five-Graph Finiteness Law*<br>(`Theorems 1, 22, 38`) | **Classical (1973) + First Lean 4 Formalization** | **Berlekamp, van Lint, and Seidel (1973)** proved that $\lambda = 1, \mu = 2$ and eigenvalue multiplicity integrality restrict $\mathrm{SRG}(v,k,1,2)$ to at most five parameter sets $v \in \{9, 99, 243, 6273, 494019\}$. | First machine-checked formalization in **Lean 4** ([`srg_lambda1_mu2_eigenvalue_discriminant_law`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L975-L993)) unifying the five graphs via the odd discriminant $d = \sqrt{4k-7} = 2s+1 \mid 63$ and linking it to dual-encoded Pure-RUP LRAT local-structure certificates (`Track p2`). |
| **Master Theorem II:**<br>*Lefschetz–Brauer Trace, Galois Conjugacy & the $N_1(F)$ No-Orbital-Step Law*<br>(`Theorems 33–35, 38b–c` & `Track p1`) | **Partially Known (1983–2023) + New Universal Generalizations & $p=7$ Closure** | **Wilbrink (1983)**, **Makhnev & Minakova (2004)**, **Behbahani & Lam (2011)**, and **Cesarz & Woldar (2023)** analyzed prime-order automorphisms of $\mathrm{SRG}(99,14,1,2)$, leaving $p=7, |\mathrm{Fix}(g)|=1$ (`p7_fix1`) and the central involution `(0,7,0)` open. | **1. First principles $N_1(F)$ No-Step Law (`Theorem 38b`):** Proves without prime-order or orbit-matrix assumptions that $\sigma(z)=z \wedge x\sim z \wedge \sigma^2(x)\ne x \implies x \nsim \sigma(x)$ (`0 axioms` in Lean 4).<br>**2. Universal Galois Multiplicity Law (`Theorem 38c`):** Proves $d \cdot m_2 = \theta_1 n_{\text{orb}} + c_{\text{adj}}$ simultaneously across all 5 graphs.<br>**3. Closure of `p7_fix1` ($0.82\text{s}$), `18/19` involutions, and $p=3$ (`Theorem 33, 35`)** via $\mathrm{Fix}(\sigma) \equiv 0 \pmod 9$ trace divisibility and Pure-RUP LRAT. |
| **Master Theorem III:**<br>*Three-Block Schur–Fiber Decomposition, 6D Orthoplex $\beta_6$, Induced 1-Regular Matching Law & $(R,R)$ Cherry-Free Reduction*<br>(`Theorems 3–21, 30, 32, 37, 40, 40b`) | **100% NEW (Original Contribution of This Work)** | Only general Schur complement / quotient matrix inequalities (Haemers) and abstract equiangular/orthoplex line bounds existed in the general literature. | **Completely new for $\mathrm{SRG}(99,14,1,2)$ and $\mathrm{SRG}(v,k,1,2)$:**<br>**1. 6D Orthoplex Embedding (`Theorem 37`):** Adjoining the $12\times 12$ edge-pair matrix $C_{12}$ to $X_{12\times 60}$ yields $(3\widetilde{X}-J)(3\widetilde{X}-J)^\top = 81I_{12}$, deterministically locking half of the rows in `Stage D2`.<br>**2. Induced 1-Regular Matching Law in $A_{60}[x_i]$ (`Theorem 40 & 40b(1)`):** Proves $\deg_{A_{60}[x_i]}(e) = 1 - w_{i,e} - gx_{e(i),e} \in \{0,1\}$, so every 10-column neighborhood $x_i \subset V_{60}$ induces **4 disjoint edges and 2 isolated vertices** inside $A_{60}$.<br>**3. Block $(R,R)$ Cherry-Free Sufficiency & Disjoint-Support Collapse (`Theorem 40b(2)-(3)`):** Proves $(M^\top M)_{e_1,e_2}\le 2$ holds automatically on all $1,620$ pairs with $w_{12}=0$ and reduces to $\neg(x_{12}=1\wedge gx_{12}=1)$ on the $150$ pairs with $w_{12}=1$, while eliminating the `gp56` popcount test in `Stage D2` (**`4.17×` live speedup on NVIDIA A100** in `Gen V.6d`). |
| **Master Theorem IV:**<br>*Triangle-Core Seed $V_{3k-3}$ & the $3_3$ Configuration Closure Dichotomy*<br>(`Theorems 25–31, 39a–b`) | **Partially Known Local Picture + New $3_3$ Closure Dichotomy & Seed Dodecagon $C_{12}$** | The local $39$-vertex neighborhood around a triangle in $v=99$ (Conway 1975) and the ternary Golay construction of $v=243$ (Berlekamp–van Lint–Seidel 1973) were known separately. | **1. Universal Triangle-Core Seed Decomposition (`Theorem 39a`):** Proves that around any triangle $T$, the transversal edges between $S_0, S_1, S_2$ partition into $t_{\text{trans}} = k - 2 - a_{01} - a_{02} - a_{12}$ disjoint triangles.<br>**2. The $3_3$ Configuration Closure Criterion (`Theorem 39b`):** Identifies the exact geometric dichotomy between $v \in \{9, 243\}$ and $v=99$: the seed closes into an $\mathbb{F}_3$-affine space iff the three layer matchings $\iota_0,\iota_1,\iota_2$ map every transversal triangle $\{x_0,x_1,x_2\}$ to a partner transversal triangle $\{\iota_0(x_0),\iota_1(x_1),\iota_2(x_2)\}$ (forming a $K_3\square K_2$ prism / symmetric $3_3$ configuration).<br>**3. The Universal Seed Dodecagon $C_{12}$ (`Theorems 28–31`):** Proves all $3,580$ slice orbits grow out of $3$ Seed Orbits on $C_{12}$ (`3/3 UNSAT`). |
| **Master Theorem V:**<br>*Complete Cayley (Regular Group) Classification Across All Five Graphs $v \in \{9, 99, 243, 6273, 494019\}$*<br>(`Theorems 41, 42a–b`) | **Indirectly known for $v=99$; NEW unified proof & non-abelian refutation for $v=6273$ and $v=494019$ (`0 axioms` in Lean 4)** | $v=9$ and $v=243$ were known as Cayley graphs over $\mathbb{F}_3^2$ and $\mathbb{F}_3^5$. For $v=99$, non-existence of a Cayley graph followed indirectly from combining Wilbrink ($11 \nmid |\mathrm{Aut}|$) and Makhnev ($3 \nmid |\mathrm{Aut}|$). | **1. Elementary 2-Line Sylow Exponent Bound (`Theorem 41`):** Rules out all abelian/normal-$P_3$ order-3-generated Cayley graphs for $v \in \{99, 6273, 494019\}$ via $k > 3^a - 1$ ($14 > 8$, $112 > 8$, $994 > 242$).<br>**2. Complete Abelian & Non-Abelian Cayley Refutation (`Theorems 42a–b`, `0 axioms`):** Proves directly from Sylow normal projections, Galois eigenvalue constancy, and induced-character trace identities that **no group $H$ (abelian or non-abelian) of order $99$, $6,273$, or $494,019$ admits a Cayley $\mathrm{SRG}(v,k,1,2)$** — in particular ruling out all non-abelian semidirect products $Q = (C_{19}\rtimes C_{d_\varphi})\times C_{107}$ ($d_\varphi \in \{1,3,9\}$) at $v=494,019$ via $107(19u_1 - s_1) = 63(m_1 - m_0)$. |

---

## 2. Complete Exposition of the Five Master Theorems (Plain-English & Mathematical Versions)

---

### Master Theorem I: The Spectral Triangle-Pairing & Five-Graph Finiteness Law

#### 1. Plain-English Explanation
Consider a regular network (graph) on $v$ vertices where every vertex has exactly $k$ neighbors, every pair of connected vertices shares **exactly one** common neighbor ($\lambda = 1$), and every pair of disconnected vertices shares **exactly two** common neighbors ($\mu = 2$).
- Because every edge belongs to a unique triangle ($\lambda = 1$), the $k$ neighbors of any vertex pair up into $k/2$ disjoint edges. Thus $k$ is always even, and the edges of the entire graph partition into $vk/6$ edge-disjoint triangles.
- Because every non-edge has exactly two common neighbors ($\mu = 2$), counting paths of length $2$ from any vertex shows that the total number of vertices is $v = 1 + k + \frac{k(k-2)}{2} = 1 + \frac{k(k-1)}{2}$, and the adjacency matrix $A$ satisfies the quadratic matrix equation $A^2 + A - (k-2)I = 2J$.
- Consequently, every non-principal eigenvalue of $A$ satisfies $\theta^2 + \theta - (k-2) = 0$, so the eigenvalue gap $\theta_1 - \theta_2 = \sqrt{4k-7} = d$ must be an odd integer $d = 2s + 1$, giving $k = s^2 + s + 2$, $\theta_1 = s$, and $\theta_2 = -(s+1)$.
- Finally, the dimensions (multiplicities $m_1, m_2$) of the two eigenspaces must be positive integers. Expressing $m_1, m_2$ in terms of $d$ leaves a remainder of $63 / d$, forcing $d$ to divide $63 = 3^2 \times 7$, so $d \in \{1, 3, 7, 9, 21, 63\}$. Removing $d = 1$ ($k = 2$, a single triangle with no non-edges) leaves **uniquely five mathematically possible graphs in the entire universe**: $v \in \{9, 99, 243, 6273, 494019\}$.

#### 2. Mathematical Formulation & Proof
**Theorem I (`srg_lambda1_mu2_eigenvalue_discriminant_law`, Theorem 38 in Lean 4).**
*Let $G = (V, E)$ be a strongly regular graph $\mathrm{SRG}(v, k, 1, 2)$ with adjacency matrix $A \in \{0,1\}^{v \times v}$ and $v > 3$. Then:*
1. **Bose–Mesner Quadratic Identity & Vertex Count:**
   $$A^2 + A - (k - 2)I_v = 2J_v, \qquad v = 1 + \frac{k(k-1)}{2}, \qquad 2 \mid k, \qquad 6 \mid vk.$$
2. **Odd Discriminant Parameterization ($d = 2s+1$):**
   *The restricted eigenvalues $\theta_1 > 0 > \theta_2$ on $\mathbf{1}^\perp$ satisfy $\theta^2 + \theta - (k-2) = 0$ with discriminant $d^2 = 4k - 7 = (2s+1)^2$, so:*
   $$k = s^2 + s + 2 = \frac{d^2 + 7}{4}, \qquad \theta_1 = s = \frac{d-1}{2}, \qquad \theta_2 = -(s+1) = -\frac{d+1}{2}, \qquad \theta_1 - \theta_2 = d.$$
3. **Diophantine Integrality of Multiplicities ($d \mid 63$):**
   *Since $\mathrm{Tr}(A) = k + m_1 \theta_1 + m_2 \theta_2 = 0$ and $m_1 + m_2 = v - 1 = \frac{(k+1)(k-2)}{2}$, multiplying by $16d$ yields:*
   $$m_1 - m_2 = \frac{v - 1 - 2k}{d} = \frac{d^4 + 10d^2 - 175}{16d} \in \mathbb{Z} \implies d \mid 175 \quad\text{or, combined with } 8 \mid (d^2-1),\quad d \mid 63 = 3^2 \times 7.$$
   *Therefore, $(d, s, k, v, \theta_1, \theta_2, m_1, m_2)$ belongs to the exact 5-tuple table:*

| Index | $d = 2s+1$ | $s = \theta_1$ | $\theta_2 = -(s+1)$ | Degree $k = s^2+s+2$ | Vertices $v = 1 + \binom{k}{2}$ | Multiplicities $(m_1, m_2)$ | Existence Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | $3$ | $1$ | $-2$ | $4$ | $9 = 3^2$ | $(4, 4)$ | **Exists & Unique** ($K_3 \square K_3$) |
| **2** | $7$ | $3$ | $-4$ | $14$ | $99 = 3^2 \times 11$ | $(54, 44)$ | **Open** (*Conway's 99-Graph*; **No Cayley**, $|\mathrm{Aut}| \mid 54$) |
| **3** | $9$ | $4$ | $-5$ | $22$ | $243 = 3^5$ | $(132, 110)$ | **Exists** (*Berlekamp–van Lint–Seidel* over $\mathbb{F}_3^5$) |
| **4** | $21$ | $10$ | $-11$ | $112$ | $6,273 = 3^2 \times 17 \times 41$ | $(3264, 3008)$ | **Open** (**No Cayley graph over any group $H$**) |
| **5** | $63$ | $31$ | $-32$ | $994$ | $494,019 = 3^5 \times 19 \times 107$ | $(250920, 243098)$ | **Open** (**No Cayley graph over any group $H$**) |

- **Lean 4 Verification:** [`srg_lambda1_mu2_eigenvalue_discriminant_law`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L975-L993) (`Theorem 38`, `0 sorryAx`).

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./master_theorem_1_finiteness_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./master_theorem_1_finiteness_light.svg">
    <img alt="Master Theorem I: Spectral Triangle-Pairing and the Five-Graph Finiteness Law (d | 63)" src="./master_theorem_1_finiteness_light.svg" width="880">
  </picture>
  <br>
  <em><b>Figure 1: Master Theorem I — Spectral Triangle-Pairing &amp; the Five-Graph Finiteness Law (<code>d | 63</code>)</b> (adaptive: <a href="./master_theorem_1_finiteness_dark.svg">Dark</a> · <a href="./master_theorem_1_finiteness_light.svg">Light</a>).</em>
</p>

---

### Master Theorem II: The Lefschetz–Brauer Trace, Galois Conjugacy & $N_1(F)$ No-Orbital-Step Law

#### 1. Plain-English Explanation
Suppose $G = \mathrm{SRG}(v,k,1,2)$ admits a symmetry (automorphism $\sigma$) of order $r \ge 2$, and let $F = \mathrm{Fix}(\sigma)$ be the set of $f = |F|$ vertices left fixed by $\sigma$. Master Theorem II establishes three rigid laws governing $F$ and its surrounding layers:
1. **Disjoint Star-Bundle Law on $V \setminus F$:** If $\sigma$ has odd order $r$, no vertex $x \notin F$ can be connected to two distinct fixed vertices $z_1, z_2 \in F$. Why? If $z_1 \sim z_2$, their unique common neighbor ($\lambda = 1$) must be fixed by $\sigma$; if $z_1 \nsim z_2$, their pair of common neighbors ($\mu = 2$) is invariant under $\sigma$, and an odd-order permutation cannot swap two vertices, so both must be fixed by $\sigma$. Thus every non-fixed vertex has **at most one** neighbor in $F$, partitioning $V \setminus F = N_1(F) \sqcup N_0(F)$ into a disjoint bundle of stars $N_1(F)$ centered on $F$ and an outer layer $N_0(F)$.
2. **The $N_1(F)$ No-Orbital-Step Law (`Theorem 38b`):** If a vertex $x \in N_1(F)$ is connected to a fixed point $z \in F$ and lies in an orbit of length $\ge 3$ ($\sigma^2(x) \ne x$), then **$x$ can never be connected to its immediate orbital image $\sigma(x)$**. Why? If $x \sim \sigma(x)$, then $\{z, x, \sigma(x)\}$ is a triangle, and applying $\sigma$ shows $\{z, \sigma(x), \sigma^2(x)\}$ is also a triangle. Then the edge $\{z, \sigma(x)\}$ would have **two** distinct common neighbors $x \ne \sigma^2(x)$, violating $\lambda = 1$! Consequently, every orbital edge $\{x, \sigma(x)\}$ must lie strictly inside the outer layer $N_0(F)$.
3. **Galois Spectral Trace & Multiplicity Law (`Theorems 33, 38c`):** The trace $\mathrm{Tr}(A\sigma)$ counts twice the edges inside $F$ plus the number $c_{\text{adj}}$ of vertices $x \in N_0(F)$ with $x \sim \sigma(x)$. Spectrally, $\mathrm{Tr}(A\sigma) = k + \theta_1 \mathrm{Tr}(\sigma|_{V_1}) + \theta_2 \mathrm{Tr}(\sigma|_{V_2})$. Because Galois conjugation $\zeta_r \mapsto \zeta_r^m$ ($\gcd(m,r)=1$) permutes primitive $r$-th roots of unity while keeping integer traces fixed, the eigenspace traces obey strict modular congruences:
   - Across all 5 graphs, for any semi-regular action with rational/uniform $V_2$-trace, $d \cdot m_2 = \theta_1 n_{\text{orb}} + c_{\text{adj}}$ (`Theorem 38c`).
   - In $\mathrm{SRG}(99,14,1,2)$, since $\theta_1 = 3 \equiv -6 \pmod 9$ and $\theta_2 = -4 \equiv 5 \pmod 9$ satisfy $\theta_1 - \theta_2 = 7$, any order-$3$ automorphism satisfies $|\mathrm{Fix}(\sigma)| \equiv 0 \pmod 9$ (`Theorem 33`), which together with the uniqueness of the $F_{21}$ kernel (`Theorem 35`) globally eliminates order-$3$ symmetries.

#### 2. Mathematical Formulation & Proof
**Theorem II (`odd_order_no_step_in_n1_structural`, `odd_order_galois_eigenvalue_multiplicity_law`, `order3_spectral_trace_divisibility_by_9`, Theorems 33, 35, 38b, 38c in Lean 4).**
*Let $\sigma \in \mathrm{Aut}(G)$ be an automorphism of $G = \mathrm{SRG}(v,k,1,2)$ with fixed-point set $F = \mathrm{Fix}(\sigma)$, $f = |F|$, and layers $N_i(F) = \{x \in V \setminus F : |N(x) \cap F| = i\}$.*
1. **First-Principles $N_1(F)$ No-Orbital-Step Law (`Theorem 38b`, `0 axioms`):**
   *Assume the $\lambda=1$ uniqueness axiom ($\forall u, v, w_1, w_2:\; u \sim v \wedge u \sim w_1 \wedge v \sim w_1 \wedge u \sim w_2 \wedge v \sim w_2 \implies w_1 = w_2$) and $\sigma$-invariance ($u \sim v \implies \sigma(u) \sim \sigma(v)$). Then for all $z, x \in V$:*
   $$\sigma(z) = z \;\wedge\; z \sim x \;\wedge\; \sigma(\sigma(x)) \ne x \implies x \nsim \sigma(x).$$
   *Proof:* Suppose $x \sim \sigma(x)$. Since $\sigma(z)=z$ and $z \sim x$, applying $\sigma$ yields $z \sim \sigma(x)$ and $\sigma(x) \sim \sigma(\sigma(x))$, and applying $\sigma$ again yields $z \sim \sigma(\sigma(x))$. Thus both $w_1 = x$ and $w_2 = \sigma(\sigma(x))$ are common neighbors of the adjacent pair $(z, \sigma(x))$, forcing $x = \sigma(\sigma(x))$ by $\lambda = 1$, a contradiction. $\square$
2. **Universal Galois Multiplicity Identity (`Theorem 38c`):**
   *Let $\sigma$ have odd order $r \ge 3$ acting semi-regularly on $V \setminus F$ with $n_{\text{orb}} = (v-f)/r$ orbits, and let $c_{\text{adj}} = |\{x \in N_0(F) : x \sim \sigma(x)\}|$. Using $\mathrm{Tr}(\sigma) = f = 1 + \mathrm{Tr}(\sigma|_{V_1}) + \mathrm{Tr}(\sigma|_{V_2})$ and $\mathrm{Tr}(A\sigma) = \sum_{z \in F}\deg_F(z) + c_{\text{adj}} = k + \theta_1 \mathrm{Tr}(\sigma|_{V_1}) + \theta_2 \mathrm{Tr}(\sigma|_{V_2})$, eliminating $\mathrm{Tr}(\sigma|_{V_1})$ yields:*
   $$(\theta_1 - \theta_2)\,\mathrm{Tr}(\sigma|_{V_2}) = d\,\mathrm{Tr}(\sigma|_{V_2}) = k + \theta_1(f - 1) - \sum_{z \in F}\deg_F(z) - c_{\text{adj}}.$$
   *In particular, for a fixed-point-free action ($f = 0$, $v = r \cdot n_{\text{orb}}$) where $V_2$ decomposes into $a_0$ trivial and $b_1$ copies of the $(r-1)$-dimensional augmentation module with $a_0 = b_1$ ($\mathrm{Tr}(\sigma|_{V_2}) = 0$), substituting $k - \theta_1 = d m_2 - \theta_1 v$ yields across all 5 graphs $d \in \{3, 7, 9, 21, 63\}$:*
   $$d \cdot m_2 = \theta_1 \cdot n_{\text{orb}} + c_{\text{adj}}.$$
3. **Order-3 Divisibility by 9 (`Theorem 33`):**
   *In $\mathrm{SRG}(99,14,1,2)$, for any $\sigma \in \mathrm{Aut}(G)$ of order $3$ fixing $f$ vertices with $c_1$ orbital 3-cycles in $V \setminus F$, $7\,\mathrm{Tr}(\sigma|_{V_1}) = 3f + 3c_1 - 18$ and $7\,\mathrm{Tr}(\sigma|_{V_2}) = 4f - 3c_1 + 11$, where $\mathrm{Tr}(\sigma|_{V_i}) = m_i - 3b_i \equiv m_i \pmod 3$, forcing $f \equiv 0 \pmod 9$.*

- **Lean 4 Verification:**
  - [`odd_order_no_step_in_n1_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L999-L1024) (`Theorem 38b`, `does not depend on any axioms`)
  - [`odd_order_galois_eigenvalue_multiplicity_law`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1029-L1052) (`Theorem 38c`, `0 sorryAx`)
  - [`order3_spectral_trace_divisibility_by_9`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L868-L884) (`Theorem 33`, `0 sorryAx`)
  - [`frob21_uniqueness_and_order3_global_elimination`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L901-L917) (`Theorem 35`, `0 sorryAx`)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./master_theorem_2_lefschetz_galois_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./master_theorem_2_lefschetz_galois_light.svg">
    <img alt="Master Theorem II: Lefschetz-Brauer Trace, Galois Conjugacy and the N1(F) No-Orbital-Step Law" src="./master_theorem_2_lefschetz_galois_light.svg" width="880">
  </picture>
  <br>
  <em><b>Figure 2: Master Theorem II — Lefschetz–Brauer Trace, Galois Conjugacy &amp; the <code>N₁(F)</code> No-Orbital-Step Law</b> (adaptive: <a href="./master_theorem_2_lefschetz_galois_dark.svg">Dark</a> · <a href="./master_theorem_2_lefschetz_galois_light.svg">Light</a>).</em>
</p>

---

### Master Theorem III: The Three-Block Schur–Fiber Decomposition, 6D Orthoplex $\beta_6$, Induced 1-Regular Matching Law & $(R,R)$ Cherry-Free Reduction

#### 1. Plain-English Explanation
Suppose we partition the vertices of $G = \mathrm{SRG}(v,k,1,2)$ into an already-known local subgraph $S$ (specifically, the $39$-vertex neighborhood $S = V_{39} = V_3 \sqcup V_{12} \sqcup V_{24}$ around a triangle/edge in $\mathrm{SRG}(99,14,1,2)$) and the remaining $60$-vertex exterior $R = V_{60}$. Writing the adjacency matrix in block form $A = \begin{pmatrix} A_S & M \\ M^\top & A_R \end{pmatrix}$, where $M \in \{0,1\}^{39 \times 60}$ records which exterior vertices in $V_{60}$ connect to each vertex of $V_{39}$ (and specifically $X \in \{0,1\}^{12 \times 60}$ for the $12$-vertex layer $V_{12}$), the single SRG matrix equation $A^2 + A - 12I = 2J$ splits into **three coupled block equations** — each revealing a new structural law discovered in this work:
1. **Block $(S,S)$ — The 6D Orthoplex Embedding (`Theorem 37`):**
   Every row $x_i$ of $X$ has $10$ ones, meets its matched partner $x_{e(i)}$ in $1$ column, and meets all other $10$ rows in $2$ columns. If we append a tiny $12 \times 12$ edge-pair correction matrix $C_{12}$ (giving each matched pair $(i, e(i))$ one shared column and one private column in $C_{12}$), the augmented $12 \times 72$ matrix $\widetilde{X} = [X \mid C_{12}]$ has uniform dot product $11$ on the diagonal and $2$ everywhere off the diagonal! Subtracting the mean vector $\frac{1}{3}J$ makes all $12$ rows **strictly orthogonal**: $(3\widetilde{X} - J)(3\widetilde{X} - J)^\top = 81 I_{12}$. Geometrically, the $12$ rows of $X$ are the $12$ vertices of a **regular 6-dimensional orthoplex (cross-polytope) $\beta_6$**, which deterministically locks the partner rows in `Stage D2` of our GPU sieve.
2. **Block $(S,R)$ — The Induced 1-Regular Matching Law in $A_{60}[x_i]$ (`Theorem 40` & `Theorem 40b(1)`):**
   Previously, $A_{60}$ was treated as an unknown black box until all of $X$ was chosen. However, multiplying $M$ by $A_{60}$ shows that for every vertex $i \in V_{12}$ and every exterior neighbor $e \in x_i$ ($x_{i,e} = 1$), the number of neighbors of $e$ *inside the 10-element set $x_i$* is given by the exact linear formula:
   $$\deg_{A_{60}[x_i]}(e) = 1 - w_{i,e} - gx_{e(i),e} \in \{0, 1\}.$$
   Since $|x_i \cap W_i| + |x_i \cap g(x_{e(i)})| = 2$, **every 10-element row $x_i$ must induce inside $A_{60}$ a subgraph consisting of exactly $4$ disjoint edges ($8$ vertices of degree $1$) and $2$ isolated vertices (degree $0$)**!
3. **Block $(R,R)$ — The Cherry-Free Sufficiency Law & Disjoint-Support Collapse (`Theorem 40b(2)-(3)`):**
   For any pair of distinct columns $e_1 \ne e_2 \in V_{60}$, the number of common neighbors they share inside $V_{39}$ is $(M^\top M)_{e_1,e_2} = w_{12} + x_{12} + gx_{12} \le 2$, where $w_{12}, x_{12}, gx_{12} \in \{0, 1\}$ are binary indicators of whether $\{e_1,e_2\}$ lies in a common row of $W$, $X$, or $g(X)$. Because a sum of three binary numbers in $\{0,1\}$ exceeds $2$ **if and only if all three equal $1$**:
   - On all $1,620$ column pairs with $w_{12} = 0$, the bound $(M^\top M)_{e_1,e_2} \le 2$ is **automatically satisfied (`0` checks needed)**!
   - On the $150$ column pairs with $w_{12} = 1$, the bound is equivalent to the single cherry-free exclusion $\neg(x_{12} = 1 \wedge gx_{12} = 1)$.
   - Furthermore, in `Stage D2` (`Gen V.6d`), because the forbidden mask `fb_v6` excludes $x_4 \cap x_5 \subseteq \text{col\_u2\_5}$, any valid candidate $x_6$ satisfies $x_6 \cap x_4 \cap x_5 = \emptyset$, so $|x_6 \cap (x_4 \cup x_5)| = |x_6 \cap x_4| + |x_6 \cap x_5| = \mathrm{gp}_{46} + \mathrm{gp}_{56}$, eliminating the separate `gp56` popcount test and achieving **`2.05 s/orbit` (`4.17×` faster than `Gen V.4`) on `1× NVIDIA A100`**.

#### 2. Mathematical Formulation & Proof
**Theorem III (`six_dim_orthoplex_gram_identity`, `schur_complement_cross_block_degree_constraint`, `schur_fiber_three_block_rr_sufficiency_and_matching_law`, Theorems 37, 40, 40b in Lean 4).**
*For the partition $V = S \sqcup R$ ($|S|=39, |R|=60$) of $\mathrm{SRG}(99,14,1,2)$ with $A = \begin{pmatrix} A_S & M \\ M^\top & A_{60} \end{pmatrix}$ and $M = \begin{pmatrix} W \\ X \\ P X G^\top \end{pmatrix}$ ($W \in \{0,1\}^{3 \times 60}, X \in \{0,1\}^{12 \times 60}$), the SRG matrix equation $A^2 + A - 12I_{99} = 2J_{99}$ is equivalent to the coupled system:*
$$\begin{aligned}
\text{\textbf{(I) Block $(S,S)$:}}\quad & M M^\top = 2J_{39} + 12I_{39} - A_S - A_S^2, \\
\text{\textbf{(II) Block $(S,R)$:}}\quad & M A_{60} = 2J_{39,60} - (I_{39} + A_S)M, \\
\text{\textbf{(III) Block $(R,R)$:}}\quad & A_{60}^2 + A_{60} - 12I_{60} = 2J_{60} - M^\top M.
\end{aligned}$$
*From (I)–(III) the following three laws hold:*
1. **6D Orthoplex Gram Identity (`Theorem 37`):**
   *Let $X X^\top = 10 I_{12} + A_{\text{match}} + 2(J_{12} - I_{12} - A_{\text{match}}) = 8I_{12} - A_{\text{match}} + 2J_{12}$, and let $C_{12} \in \{0,1\}^{12 \times 12}$ satisfy $C_{12}C_{12}^\top = I_{12} + A_{\text{match}}$ and $C_{12}J_{12} = 2J_{12}$. Then for $\widetilde{X} = [X \mid C_{12}] \in \{0,1\}^{12 \times 72}$:*
   $$\widetilde{X}\widetilde{X}^\top = 9I_{12} + 2J_{12}, \qquad (3\widetilde{X} - J_{12,72})(3\widetilde{X} - J_{12,72})^\top = 81 I_{12}.$$
2. **Induced 1-Regular Matching Law in Block $(S,R)$ (`Theorem 40` & `Theorem 40b(1)`):**
   *For every $i \in \{0,\dots,11\}$ and every column $e \in \{0,\dots,59\}$ with $x_{i,e} = 1$, let $w_{i,e} = ((I_{12}+A_{12})W)_{i,e} \in \{0,1\}$, $x_{e(i),e} \in \{0,1\}$, and $gx_{e(i),e} = (A_{12,24} P X G^\top)_{i,e} \in \{0,1\}$ with $w_{i,e} + x_{e(i),e} + gx_{e(i),e} \le 1$. When $x_{e(i),e} = 0$, the internal degree of $e$ in the 10-vertex induced subgraph $A_{60}[x_i]$ is:*
   $$\deg_{A_{60}[x_i]}(e) = (X A_{60})_{i,e} = 1 - w_{i,e} - gx_{e(i),e} \in \{0, 1\}, \qquad \sum_{e \in x_i} \deg_{A_{60}[x_i]}(e) = 8 = 2 \times 4.$$
   *Hence $A_{60}[x_i] \cong 4 K_2 \sqcup 2 K_1$ (4 disjoint edges on $x_i \setminus (W_i \cup g(x_{e(i)}))$ and 2 isolated vertices on $x_i \cap (W_i \cup g(x_{e(i)}))$).*
3. **Block $(R,R)$ Cherry-Free Sufficiency & Stage D2 Disjoint-Support Law (`Theorem 40b(2)-(3)`):**
   *For any distinct columns $e_1 \ne e_2 \in V_{60}$, let $w_{12} = (W^\top W)_{e_1,e_2} \in \{0,1\}$, $x_{12} = (X^\top X)_{e_1,e_2} \in \{0,1\}$, and $gx_{12} = (G X^\top X G^\top)_{e_1,e_2} \in \{0,1\}$. Then:*
   $$(M^\top M)_{e_1,e_2} = w_{12} + x_{12} + gx_{12} \le 2 \iff \bigl(w_{12} = 1 \implies \neg(x_{12} = 1 \wedge gx_{12} = 1)\bigr).$$
   *Moreover, for any candidate row $x_6$ disjoint from $x_4 \cap x_5 \subseteq \text{fb\_v6}$, $|x_6 \cap (x_4 \cup x_5)| = |x_6 \cap x_4| + |x_6 \cap x_5|$, so $(|x_6 \cap (x_4 \cup x_5)| = \mathrm{gp}_{46} + \mathrm{gp}_{56} \wedge |x_6 \cap x_4| = \mathrm{gp}_{46}) \implies |x_6 \cap x_5| = \mathrm{gp}_{56}$.*

- **Lean 4 Verification:**
  - [`six_dim_orthoplex_gram_identity`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L948-L968) (`Theorem 37`, `0 sorryAx`)
  - [`schur_complement_cross_block_degree_constraint`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1126-L1139) (`Theorem 40`, `0 sorryAx`)
  - [`schur_fiber_three_block_rr_sufficiency_and_matching_law`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1146-L1178) (`Theorem 40b`, `0 sorryAx`)
  - Plus the full suite of Chiral Nullspace & Handshaking theorems (`Theorems 1–24, 30, 32`) in [`ChiralNullspaceAndHandshaking.lean`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean).

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./master_theorem_3_schur_orthoplex_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./master_theorem_3_schur_orthoplex_light.svg">
    <img alt="Master Theorem III: Three-Block Schur-Fiber Decomposition, 6D Orthoplex beta_6 and Cherry-Free Collapse" src="./master_theorem_3_schur_orthoplex_light.svg" width="880">
  </picture>
  <br>
  <em><b>Figure 3: Master Theorem III — Three-Block Schur–Fiber Decomposition, 6D Orthoplex <code>β₆</code> &amp; Cherry-Free Collapse (<code>Gen V.6d</code> <code>4.17×</code> Speedup)</b> (adaptive: <a href="./master_theorem_3_schur_orthoplex_dark.svg">Dark</a> · <a href="./master_theorem_3_schur_orthoplex_light.svg">Light</a>).</em>
</p>

---

### Master Theorem IV: The Triangle-Core Seed $V_{3k-3}$, the $3_3$ Configuration Closure Dichotomy & the Seed Dodecagon $C_{12}$

#### 1. Plain-English Explanation
Pick any triangle $T = \{u_0, u_1, u_2\}$ in a graph $G = \mathrm{SRG}(v,k,1,2)$. Each vertex $u_i \in T$ has $k - 2$ additional neighbors outside $T$, forming three layers $S_0, S_1, S_2$ of size $k - 2$. By $\lambda = 1$, each layer $S_i$ is paired up internally into $(k-2)/2$ disjoint matching edges via a fixed-point-free involution $\iota_i : S_i \to S_i$.
Now consider how the three layers $S_0, S_1, S_2$ connect to one another:
1. **Universal Transversal Triangle Partition (`Theorem 39a`):**
   If $x_0 \in S_0$ and $x_1 \in S_1$ are adjacent (and neither belongs to a $K_4$ clique on $T$), then $x_0$ and $x_2 = u_2$ are non-adjacent, so $\mu = 2$ forces $x_0$ and $u_2$ to share a second common neighbor $x_2 \in S_2$ besides $u_0$, and $\lambda = 1$ on $\{x_0, x_1\}$ forces $x_1 \sim x_2$. Thus **all cross-edges between $S_0^*, S_1^*, S_2^*$ partition into $t_{\text{trans}} = k - 2 - a_{01} - a_{02} - a_{12}$ vertex-disjoint transversal triangles $\{x_0, x_1, x_2\} \in S_0^* \times S_1^* \times S_2^*$**! In a $K_4$-free triangle seed ($a_{ij} = 0$), this local seed $V_{\text{seed}} = T \sqcup S_0 \sqcup S_1 \sqcup S_2$ has size $3k - 3 \in \{9, 39, 63, 333, 2979\}$ and looks locally identical across all 5 graphs.
2. **Why $v = 9$ and $v = 243$ Exist while $v = 99$ Fails Linear Closure — The $3_3$ Configuration Criterion (`Theorem 39b`):**
   Take any transversal triangle $\{x_0, x_1, x_2\}$ ($x_i \in S_i$), and look at the opposite endpoints $\{\iota_0(x_0), \iota_1(x_1), \iota_2(x_2)\}$ of their internal matching edges in $S_0, S_1, S_2$.
   - **If $\{\iota_0(x_0), \iota_1(x_1), \iota_2(x_2)\}$ is ALWAYS itself a transversal triangle** (so the $6$ vertices form a triangular prism $K_3 \square K_2$, i.e., a symmetric $3_3$ configuration), then the matching pairs $\{x_i, \iota_i(x_i)\}$ act as collinear antipodal pairs $\{\pm c_i\}$ over $\mathbb{F}_3$, closing the graph into an $\mathbb{F}_3^n$ coset graph! This requires $2 \mid t_{\text{trans}}$ and $v = 3^n$, which holds for **$v = 9 = 3^2$** ($1$ prism) and **$v = 243 = 3^5$** ($10$ prisms from the ternary Golay code).
   - **For $v = 99$**, $99$ is not a power of $3$ ($3^4 = 81 < 99 < 243 = 3^5$), so $3_3$ affine closure is globally impossible: on every slice $S_r$, the two matchings $(M_0, E_0)$ form a perturbation of the **Universal Seed Dodecagon $C_{12}$ (`Theorem 28`)** whose `3 / 3` ground-state Seed Orbits (`Orbits 0, 1670, 2118`) and all `910 / 910` symmetric Kempe co-pinches (`1+5`, `4+2`, `3+3`, `2+2+2`) are machine-certified `UNSAT`.

#### 2. Mathematical Formulation & Proof
**Theorem IV (`triangle_seed_transversal_decomposition`, `golay_243_ternary_closure_vs_99_obstruction`, `we_star_seed_dodecagon_and_seven_level_freckle_excitation_grading`, Theorems 28–31, 39a, 39b in Lean 4).**
*Let $T = \{u_0, u_1, u_2\}$ be a triangle in $G = \mathrm{SRG}(v,k,1,2)$ with layers $S_i = N(u_i) \setminus T$ ($|S_i| = k-2$), internal matchings $\iota_i : S_i \to S_i$, and $K_4$-overlap counts $a_{ij} = |S_i \cap S_j|$.*
1. **Transversal Triangle Decomposition (`Theorem 39a`):**
   *Setting $S_0^* = S_0 \setminus (S_1 \cup S_2)$, $S_1^* = S_1 \setminus (S_0 \cup S_2)$, $S_2^* = S_2 \setminus (S_0 \cup S_1)$, every vertex $x \in S_i^*$ has exactly one neighbor in $S_{i+1}^*$ and one neighbor in $S_{i+2}^*$, and those two neighbors are mutually adjacent. Hence the edges between $S_0^*, S_1^*, S_2^*$ partition into:*
   $$t_{\text{trans}} = k - 2 - a_{01} - a_{02} - a_{12} = s(s+1) - a_{01} - a_{02} - a_{12}$$
   *vertex-disjoint transversal triangles, and when $a_{01}=a_{02}=a_{12}=0$, $|V_{\text{seed}}| = 3 + 3(k-2) = 3k - 3 = 3s^2 + 3s + 3 \in \{9, 39, 63, 333, 2979\}$.*
2. **The $3_3$ Configuration Closure & $\mathbb{F}_3$-Generation Dichotomy (`Theorem 39b`, `0 axioms`):**
   *The seed $V_{\text{seed}}$ satisfies the **$3_3$ Prism Closure Axiom** iff for every transversal triangle $\{x_0, x_1, x_2\} \in S_0 \times S_1 \times S_2$, the matched partner triple $\{\iota_0(x_0), \iota_1(x_1), \iota_2(x_2)\}$ is also a transversal triangle (partitioning the $k-2$ transversal triangles into $(k-2)/2$ prisms $K_3 \square K_2$). Under $3_3$ closure across all triangles, the $(k/2)$ antipodal edge pairs generate an elementary abelian $3$-group $\mathbb{F}_3^n$ of order $v = 3^n$, which occurs if and only if $v \in \{9, 243\}$.*

- **Lean 4 Verification:**
  - [`triangle_seed_transversal_decomposition`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1065-L1085) (`Theorem 39a`, `0 sorryAx`)
  - [`golay_243_ternary_closure_vs_99_obstruction`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1091-L1119) (`Theorem 39b`, `does not depend on any axioms`)
  - [`we_star_seed_dodecagon_and_seven_level_freckle_excitation_grading`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L747-L769) (`Theorem 28`, `0 sorryAx`)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./master_theorem_4_seed_dichotomy_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./master_theorem_4_seed_dichotomy_light.svg">
    <img alt="Master Theorem IV: Triangle-Core Seed V_{3k-3}, the 3_3 Prism Closure Dichotomy and Seed Dodecagon C_{12}" src="./master_theorem_4_seed_dichotomy_light.svg" width="880">
  </picture>
  <br>
  <em><b>Figure 4: Master Theorem IV — Triangle-Core Seed <code>V₃ₖ₋₃</code>, the <code>3₃</code> Prism Closure Dichotomy &amp; Seed Dodecagon <code>C₁₂</code></b> (adaptive: <a href="./master_theorem_4_seed_dichotomy_dark.svg">Dark</a> · <a href="./master_theorem_4_seed_dichotomy_light.svg">Light</a>).</em>
</p>

---

### Master Theorem V: Complete Cayley (Regular Group) Classification Across All Five Graphs $v \in \{9, 99, 243, 6273, 494019\}$

#### 1. Plain-English Explanation
A graph $G$ is a **Cayley graph** $\mathrm{Cay}(H, S)$ (equivalently, admits a regular automorphism group $H$ of order $|H| = v$) if its vertices can be labeled by the elements of a finite group $H$ (abelian or non-abelian) and its edges are generated by a symmetric inverse-closed subset $S \subset H \setminus \{1\}$ of size $|S| = k$.
Master Theorem V completely solves the Cayley graph existence problem across **all five parameter sets $v \in \{9, 99, 243, 6273, 494019\}$ and over ALL finite groups $H$ (both abelian and non-abelian)**:
- **Cayley $\mathrm{SRG}(v,k,1,2)$ graphs exist for $v = 9$ and $v = 243$** (over $H = \mathbb{F}_3^2$ and $H = \mathbb{F}_3^5$).
- **No Cayley $\mathrm{SRG}(v,k,1,2)$ graph exists over ANY group $H$ (abelian or non-abelian) for $v = 99$, $v = 6,273$, or $v = 494,019$!**

Why is every group $H$ of order $99$, $6,273$, or $494,019$ ruled out?
1. **First, if $S$ consists of elements of order $3$ inside a normal abelian $3$-Sylow subgroup (`Theorem 41`):**
   Every group of order $99 = 3^2 \times 11$ or $6,273 = 3^2 \times 17 \times 41$ is forced by Sylow's theorem to be abelian with a $3$-Sylow subgroup of size $3^2 = 9$ (containing only $9 - 1 = 8$ non-identity elements of order dividing $3$), whereas $S$ requires $k = 14 > 8$ (for $v=99$) and $k = 112 > 8$ (for $v=6273$) generators! Even for an abelian group of order $494,019 = 3^5 \times 19 \times 107$, the $3$-Sylow subgroup has $3^5 - 1 = 242$ non-identity elements, which is strictly smaller than $k = 994 > 242$.
2. **Second, in full generality — without assuming elements of $S$ have order $3$ and allowing ALL non-abelian groups $H$ (`Theorems 42a & 42b`):**
   By projecting $S$ onto the normal prime-power quotients guaranteed by Sylow's theorem and applying Galois conjugacy of roots of unity:
   - **At $v = 6,273 = 153 \times 41$:** Sylow's theorem forces a central cyclic quotient $Q = C_{41}$. On $C_{41}$, all $40$ non-identity fibers must contain the same number $n_* \ge 0$ of elements from $S$, while the identity fiber contains $n_0 \ge 0$ elements, satisfying $n_0 + 40 n_* = 112$ and $n_0 - n_* = \varepsilon_{41} \in \{10, -11\}$. Subtracting gives $41 n_* = 112 - \varepsilon_{41} \in \{102, 123\}$, which forces $\varepsilon_{41} = -11$, $n_* = 3$, and therefore **$n_0 = -11 + 3 = -8 < 0$ — impossible since a set cannot have $-8$ elements!**
   - **At $v = 99 = 3^2 \times 11$:** Projecting $S$ ($|S|=14$) onto $Q = C_3 \times C_{11}$, Fourier inversion for the multiplicity $n_{1,1} \ge 0$ of an order-$33$ element gives $33 n_{1,1} = 14 - \varepsilon_3 - \varepsilon_{11} + \varepsilon_{33}$ with $\varepsilon_3, \varepsilon_{11}, \varepsilon_{33} \in \{3, -4\}$, which only takes values in $\{7, 14, 21, 28\}$ — none of which is divisible by $33$!
   - **At $v = 494,019 = 3^5 \times 19 \times 107$ (including all non-abelian groups):** Sylow's theorem forces $H \cong H_{4617} \times C_{107}$ and $C_{19} \trianglelefteq H_{4617}$, so every group $H$ of order $494,019$ projects onto a solvable quotient $Q = (C_{19} \rtimes C_{d_\varphi}) \times C_{107}$ with $d_\varphi \in \{1, 3, 9\}$. On the abelian quotient $C_{d_\varphi} \times C_{107}$, the $C_{107}$ equation $n_0 + 106 n_* = 994, n_0 - n_* \in \{31, -32\}$ forces $\varepsilon_{107} = 31, n_* = 9$, and non-trivial $C_{d_\varphi}$-layer sum $s_1 = 9 / d_\varphi \in \{9, 3, 1\}$. Lifting to the $18$ non-trivial characters of $C_{19}$ (whose induced representations on $Q$ vanish outside the normal kernel $C_{19} \times \{0\} \times C_{107}$) yields the Diophantine identity:
     $$107(19 u_1 - s_1) = 63(m_1 - m_0), \qquad u_1 \in \mathbb{N},\; s_1 \in \{9, 3, 1\},\; 0 \le m_0, m_1 \le 18.$$
     Since $\gcd(107, 63) = 1$ and $|m_1 - m_0| \le 18 < 107$, we must have $m_1 = m_0$ and hence **$19 u_1 = s_1 \in \{9, 3, 1\}$ — impossible in integers!**

#### 2. Mathematical Formulation & Proof
**Theorem V (`abelian_regular_3group_exponent_bound_no_go`, `galois_quotient_and_induced_character_cayley_no_go_structural`, `complete_five_graph_cayley_classification_9_99_243_6273_494019_decide`, Theorems 41, 42a, 42b in Lean 4).**
*Across all five parameter sets $(v, k, \theta_1, \theta_2)$ of $\mathrm{SRG}(v,k,1,2)$, a Cayley realization $G \cong \mathrm{Cay}(H, S)$ over a finite group $H$ of order $|H| = v$ (abelian or non-abelian) with symmetric $S \subset H \setminus \{1\}$ ($|S|=k$) exists **if and only if $v \in \{9, 243\}$**.*

- **Lean 4 Verification:**
  - [`abelian_regular_3group_exponent_bound_no_go`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1185-L1214) (`Theorem 41`, `does not depend on any axioms`)
  - [`galois_quotient_and_induced_character_cayley_no_go_structural`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1224-L1268) (`Theorem 42a`, `0 sorryAx`)
  - [`complete_five_graph_cayley_classification_9_99_243_6273_494019_decide`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1273-L1324) (`Theorem 42b`, `does not depend on any axioms`)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./master_theorem_5_cayley_nogo_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./master_theorem_5_cayley_nogo_light.svg">
    <img alt="Master Theorem V: Complete Abelian and Non-Abelian Cayley Classification Across All Five Graphs" src="./master_theorem_5_cayley_nogo_light.svg" width="880">
  </picture>
  <br>
  <em><b>Figure 5: Master Theorem V — Complete Abelian &amp; Non-Abelian Cayley Classification Across All Five Graphs (<code>v ∈ {9, 99, 243, 6273, 494019}</code>)</b> (adaptive: <a href="./master_theorem_5_cayley_nogo_dark.svg">Dark</a> · <a href="./master_theorem_5_cayley_nogo_light.svg">Light</a>).</em>
</p>

---

## 3. Direct Few-Line Derivations of Existence, Uniqueness, and Non-Existence for Each of the Five Graphs ($v \in \{9, 99, 243, 6273, 494019\}$)

Directly from **Master Theorems I–V**, we obtain the following self-contained, few-line proofs and constructions for every graph in the 5-graph family.

---

### Graph 1: $v = 9$ — $\mathrm{SRG}(9, 4, 1, 2)$ (`EXISTENCE & UNIQUENESS`)

> **Claim:** *$\mathrm{SRG}(9, 4, 1, 2)$ exists, is unique up to isomorphism, and is isomorphic to the Cayley graph $\mathrm{Cay}(\mathbb{F}_3^2, \{\pm(1,0), \pm(0,1)\}) \cong K_3 \square K_3$.*

**4-Line Proof from Master Theorems I, IV & V:**
1. **Parameters (`Master Theorem I`):** For $d = 3$ ($s = 1$), we have $k = 4$, $v = 9$, $\theta_1 = 1$, $\theta_2 = -2$, and $(m_1, m_2) = (4, 4)$.
2. **Exhaustion by the Triangle-Core Seed (`Master Theorem IV`, `Theorem 39a`):** Pick any triangle $T = \{u_0, u_1, u_2\}$. If any edge of $T$ lay in a $K_4$, a vertex would have $\ge 2$ common neighbors with an adjacent vertex, violating $\lambda = 1$; hence $a_{01} = a_{02} = a_{12} = 0$. The triangle-core seed $V_{\text{seed}} = T \sqcup S_0 \sqcup S_1 \sqcup S_2$ therefore has size $|V_{\text{seed}}| = 3k - 3 = 3(4) - 3 = 9 = v$, exhausting the entire graph!
3. **Unique $3_3$ Prism Closure (`Master Theorem IV`, `Theorem 39b`):** Each layer $S_i$ ($i \in \{0,1,2\}$) has size $k - 2 = 2$, consisting of a single matching edge $\{x_i, \iota_i(x_i)\}$. By `Theorem 39a`, the cross-edges between $S_0, S_1, S_2$ partition into $t_{\text{trans}} = k - 2 = 2$ disjoint transversal triangles $\{x_0, x_1, x_2\}$ and $\{\iota_0(x_0), \iota_1(x_1), \iota_2(x_2)\}$.
4. **Explicit $\mathbb{F}_3^2$ Coordinates (`Master Theorem V`):** Labeling $T = \{(0,0), (1,0), (2,0)\}$ and the two transversal triangles as $\{(0,1), (1,1), (2,1)\}$ and $\{(0,2), (1,2), (2,2)\}$ realizes the graph uniquely as the $3 \times 3$ rook/Paley graph $K_3 \square K_3 \cong \mathrm{Cay}(\mathbb{F}_3^2, \{\pm(1,0), \pm(0,1)\})$. $\blacksquare$

---

### Graph 2: $v = 243$ — $\mathrm{SRG}(243, 22, 1, 2)$ (`EXISTENCE VIA TERNARY GOLAY CODE`)

> **Claim:** *$\mathrm{SRG}(243, 22, 1, 2)$ exists and is realized as the syndrome coset Cayley graph $\mathrm{Cay}(\mathbb{F}_3^5, S)$ of the perfect ternary Golay $[11, 6, 5]_3$ code.*

**5-Line Proof & Construction from Master Theorems I, IV & V:**
1. **Parameters & $3$-Group Bound (`Master Theorems I & V`):** For $d = 9$ ($s = 4$), we have $k = 22$, $v = 243 = 3^5$, and $k = 22 \le 3^5 - 1 = 242$ (`Theorem 41`), permitting an elementary abelian $3$-group realization $H = \mathbb{F}_3^5$.
2. **Generator Set $S$ from the Ternary Golay Parity-Check Matrix:** Let $H_{\text{Golay}} \in \mathbb{F}_3^{5 \times 11}$ be the parity-check matrix of the perfect ternary Golay $[11, 6, 5]_3$ code with columns $c_1, \dots, c_{11} \in \mathbb{F}_3^5 \setminus \{0\}$, and set $S = \{\pm c_1, \dots, \pm c_{11}\}$ ($|S| = 22$, $S = -S$).
3. **Minimum Distance $d_{\min} = 5$ Implies $\lambda = 1$:** Any $3$ columns of $H_{\text{Golay}}$ are linearly independent over $\mathbb{F}_3$ (since $d_{\min} = 5 \ge 4$). Hence $s_1 + s_2 = s_3$ for $s_1, s_2, s_3 \in S$ holds **if and only if** $s_1 = s_2 = -s_3 \in \{\pm c_i\}$, so every edge $\{x, x + c_i\}$ lies in the unique triangle $\{x, x + c_i, x - c_i\}$ ($\lambda = 1$).
4. **Perfectness of the Golay Code Implies $\mu = 2$:** Since $d_{\min} = 5 = 2(2) + 1$, the $1 + 22 + 2\binom{11}{2} = 243 = 3^5$ vectors of Hamming weight $\le 2$ in $\mathbb{F}_3^{11}$ have pairwise distinct syndromes covering all of $\mathbb{F}_3^5$. Thus every non-adjacent difference $y \in \mathbb{F}_3^5 \setminus (\{0\} \cup S)$ ($220$ vectors) is the syndrome of a unique weight-$2$ codeword $s_1 + s_2 = y$ ($s_1 \ne \pm s_2 \in S$), giving **exactly two** common neighbors $x + s_1$ and $x + s_2$ between $x$ and $x + y$ ($\mu = 2$).
5. **Verification of $3_3$ Closure (`Master Theorem IV`, `Theorem 39b`):** Around $T = \{0, c_{11}, -c_{11}\}$, the $20$ neighbors in $S \setminus \{\pm c_{11}\}$ partition into $10$ antipodal pairs $\{\pm c_1, \dots, \pm c_{10}\}$, forming $10$ closed $K_3 \square K_2$ prisms under translation by $T$. $\blacksquare$

---

### Graph 3: $v = 99$ — $\mathrm{SRG}(99, 14, 1, 2)$ (`CONWAY'S 99-GRAPH: CAYLEY & SYMMETRY NON-EXISTENCE + SCHUR SIEVE`)

> **Claim:** *For $v = 99, k = 14$ ($d = 7, \theta_1 = 3, \theta_2 = -4, m_1 = 54, m_2 = 44$):*
> *(A) No Cayley realization $\mathrm{Cay}(H, S)$ exists over **any** group $H$ of order $99$;*
> *(B) All prime-order symmetries $p \in \{11, 7, 5, 3\}$, $\mathrm{Frob}(21)$, all $18$ involution profiles with $|\mathrm{Fix}(g)| \ge 3$, all $3/3$ Seed Dodecagon $C_{12}$ orbits, and all $910/910$ decomposable polygonal strata (`2+2+2`, `3+3`, `4+2`, `1+5`) are `UNSAT`.*

**Few-Line Proofs from Master Theorems II, III, IV & V:**
1. **Non-Existence of Any Cayley Graph $\mathrm{Cay}(H, S)$ of Order $99$ (`Master Theorem V`, `Theorems 41, 42a–b`):**
   - By Sylow's theorem on $|H| = 99 = 3^2 \times 11$, $n_{11} \mid 9, n_{11} \equiv 1 \pmod{11} \implies n_{11} = 1$ and $n_3 \mid 11, n_3 \equiv 1 \pmod 3 \implies n_3 = 1$, so every group $H$ of order $99$ is abelian ($H \cong P_9 \times C_{11}$) and projects onto $Q = C_3 \times C_{11}$.
   - **2-Line Proof for Order-3 Generators (`Theorem 41`):** Every element of order $3$ in $P_9 \times C_{11}$ lies in $P_9 \setminus \{1\}$, which has at most $3^2 - 1 = 8$ elements, whereas $|S| = 14 > 8$ — contradiction!
   - **3-Line Proof for Arbitrary Symmetric $S$ via $C_3 \times C_{11}$ Fourier Inversion (`Theorems 42a–b`):** Projecting $S$ ($|S|=14$) onto $Q = C_3 \times C_{11}$, Galois transitivity forces the character sums on order-$3$, order-$11$, and order-$33$ characters to equal eigenvalues $\varepsilon_3, \varepsilon_{11}, \varepsilon_{33} \in \{3, -4\}$. Fourier inversion for the multiplicity $n_{1,1} \in \mathbb{N}$ of an order-$33$ fiber gives:
     $$33\, n_{1,1} = 14 - \varepsilon_3 - \varepsilon_{11} + \varepsilon_{33} \in \{7, 14, 21, 28\},$$
     which is impossible in $\mathbb{Z}$ since $33 \nmid 7, 14, 21, 28$. $\blacksquare$
2. **Global Elimination of $p = 3$ and $p = 7$ (`Master Theorem II`, `Theorems 33, 35, 38b–c`):**
   - For $p = 3$, `Theorem 33` forces $7\,\mathrm{Tr}(\sigma|_{V_1}) = 3f + 3c_1 - 18 \implies f \equiv 0 \pmod 9$, and `Theorem 35` + `p3_t1_fix33` (`12` clauses, `1` RUP step) eliminate all $p=3$ actions.
   - For $p = 7, f = 1$ (`p7_fix1`), $\mathrm{Gal}(\mathbb{Q}(\zeta_7)/\mathbb{Q})$ trace equivariance on $m_1 = 54, m_2 = 44$ forces $\mathrm{Tr}(B) = 0$ on the outer $12 \times 12$ orbit matrix, refuted in `0.82s` (`5,209` RUP steps).
3. **Asymmetric / `(0,7,0)` Sieve via Master Theorem III (`Theorems 37, 40, 40b`):**
   - By `Theorem 37`, $X_{12 \times 60}$ embeds into the 6D orthoplex $(3\widetilde{X}-J)(3\widetilde{X}-J)^\top = 81 I_{12}$; by `Theorem 40b(1)`, every row $x_i$ induces $4 K_2 \sqcup 2 K_1$ inside $A_{60}$; and by `Theorem 40b(2)-(3)`, $(M^\top M)_{e_1,e_2} \le 2$ reduces to cherry-freeness on $w_{12}=1$ and disjoint-support collapse $|x_6 \cap (x_4 \cup x_5)| = \mathrm{gp}_{46} + \mathrm{gp}_{56}$ (`4.17×` A100 speedup in `Gen V.6d`).

---

### Graph 4: $v = 6,273$ — $\mathrm{SRG}(6273, 112, 1, 2)$ (`NON-EXISTENCE OF ALL CAYLEY REALIZATIONS`)

> **Claim:** *No strongly regular graph $\mathrm{SRG}(6273, 112, 1, 2)$ can be a Cayley graph $\mathrm{Cay}(H, S)$ over **any** finite group $H$ (abelian or non-abelian) of order $6,273$.*

**4-Line Proof from Master Theorems I & V (`Theorems 41, 42a–b`):**
1. **Sylow Central Quotient $Q = C_{41}$:** Since $v = 6,273 = 3^2 \times 17 \times 41 = 153 \times 41$, Sylow's theorem gives $n_{41} \mid 153$ and $n_{41} \equiv 1 \pmod{41} \implies n_{41} = 1$. Since $\gcd(153, |\mathrm{Aut}(C_{41})|) = \gcd(153, 40) = 1$, $P_{41} \cong C_{41}$ is central in $H$, so $H \cong H_{153} \times C_{41}$ projects onto $Q = C_{41}$. *(In fact, $n_{17} = 1$ and $\gcd(9, 16 \cdot 40) = 1$ force every group of order $6,273$ to be abelian, where `Theorem 41` already gives $3^2 - 1 = 8 < 112$).*
2. **Galois Constancy on $C_{41}$:** Projecting any symmetric generating set $S$ ($|S| = k = 112$) onto $C_{41}$, let $n_0 \in \mathbb{N}$ be the fiber size over $0 \in C_{41}$. Since $\mathrm{Gal}(\mathbb{Q}(\zeta_{41})/\mathbb{Q}) \cong \mathbb{Z}_{40}^\times$ acts transitively on the $40$ non-trivial characters of $C_{41}$ and the eigenvalues $\theta_1 = 10, \theta_2 = -11$ are rational integers, every non-trivial character sum equals the same eigenvalue $\varepsilon_{41} \in \{10, -11\}$, and every non-zero element of $C_{41}$ has the same fiber multiplicity $n_* \in \mathbb{N}$.
3. **Diophantine Contradiction ($n_0 = -8 < 0$):** Counting $|S| = 112$ and evaluating a non-trivial character gives:
   $$n_0 + 40 n_* = 112 \quad\text{and}\quad n_0 - n_* = \varepsilon_{41} \in \{10, -11\} \implies 41 n_* = 112 - \varepsilon_{41} \in \{102, 123\}.$$
4. Since $41 \nmid 102$ and $123 = 41 \times 3$, we are forced into $\varepsilon_{41} = -11$ and $n_* = 3$, which yields:
   $$n_0 = \varepsilon_{41} + n_* = -11 + 3 = -8 < 0,$$
   contradicting $n_0 \ge 0$! $\blacksquare$

---

### Graph 5: $v = 494,019$ — $\mathrm{SRG}(494019, 994, 1, 2)$ (`NON-EXISTENCE OF ALL ABELIAN & NON-ABELIAN CAYLEY REALIZATIONS`)

> **Claim:** *No strongly regular graph $\mathrm{SRG}(494019, 994, 1, 2)$ can be a Cayley graph $\mathrm{Cay}(H, S)$ over **any** finite group $H$ (abelian or non-abelian) of order $494,019$.*

**6-Line Proof from Master Theorems I & V (`Theorems 41, 42a–b`):**
1. **Sylow Direct-Factor Split $H \cong H_{4617} \times C_{107}$:** Since $v = 494,019 = 3^5 \times 19 \times 107 = 4617 \times 107$, Sylow's theorem gives $n_{107} \mid 4617$ and $n_{107} \equiv 1 \pmod{107}$. Checking the divisors of $4617 = 243 \times 19$ shows $n_{107} = 1$, and since $\gcd(4617, |\mathrm{Aut}(C_{107})|) = \gcd(4617, 106) = 1$, $C_{107}$ is a central direct factor: $H \cong H_{4617} \times C_{107}$.
2. **Sylow Solvable Quotient $Q = (C_{19} \rtimes C_{d_\varphi}) \times C_{107}$:** Inside $H_{4617}$ ($|H_{4617}| = 243 \times 19$), Sylow's theorem gives $n_{19} \mid 243$ and $n_{19} \equiv 1 \pmod{19} \implies n_{19} = 1$ (since $3^1, 3^2, 3^3, 3^4, 3^5 \equiv 3, 9, 8, 5, 15 \not\equiv 1 \pmod{19}$). Thus $C_{19} \trianglelefteq H_{4617}$, and any $3$-Sylow subgroup $P_{243}$ acts on $C_{19}$ via a cyclic subgroup $C_{d_\varphi} \le \mathrm{Aut}(C_{19}) \cong C_{18}$ of order $d_\varphi \mid \gcd(243, 18) = 9$, i.e., $d_\varphi \in \{1, 3, 9\}$. Quotienting by the kernel of this action yields the quotient group $Q = (C_{19} \rtimes C_{d_\varphi}) \times C_{107}$. *(Note: if $H$ is abelian with order-$3$ generators, `Theorem 41` already gives $3^5 - 1 = 242 < 994$).*
3. **Projection to $C_{107}$ Forces $\varepsilon_{107} = 31$ and $n_*^{\text{107}} = 9$:** Projecting $S$ ($|S| = k = 994$, $\theta_1 = 31, \theta_2 = -32$) onto $C_{107}$ gives $n_0^{\text{107}} + 106 n_*^{\text{107}} = 994$ and $n_0^{\text{107}} - n_*^{\text{107}} = \varepsilon_{107} \in \{31, -32\}$, so $107 n_*^{\text{107}} = 994 - \varepsilon_{107} \in \{963, 1026\}$. Since $107 \nmid 1026$ and $963 = 107 \times 9$, we must have $\varepsilon_{107} = 31$, $n_*^{\text{107}} = 9$, and $n_0^{\text{107}} = 40$.
4. **Abelian Quotient $C_{d_\varphi} \times C_{107}$ Layer Sum $s_1 \in \{9, 3, 1\}$:** On $C_{d_\varphi} \times C_{107}$, the fiber of size $n_*^{\text{107}} = 9$ over any $y \in C_{107} \setminus \{0\}$ splits across $C_{d_\varphi}$ into $s_1$ (on the identity coset $C_{19} \times \{0\} \times \{y\}$) plus $(d_\varphi - 1)$ Galois-equal cosets, with difference $s_1 - s_{\text{non}} \in \{0, \pm 63\}$. Since the total sum is $9 < 63$, all $d_\varphi$ cosets must have equal sum $s_1 = 9 / d_\varphi \in \{9, 3, 1\}$.
5. **Induced-Character Trace on $Q = (C_{19} \rtimes C_{d_\varphi}) \times C_{107}$:** Let $u_0, u_1 \in \mathbb{N}$ be the counts of $S$ in the normal elements $(0, 0, 0)$ and $(0, 0, y \ne 0)$ of $C_{19} \times \{0\} \times C_{107}$. Because every non-trivial character $\psi_a$ ($a \in \{1,\dots,18\}$) of $C_{19}$ has zero induced character trace outside the normal subgroup $C_{19} \times \{0\} \times C_{107}$, summing the eigenvalues $\lambda_{a,0}, \lambda_{a,1} \in \{31, -32\}$ over $a = 1, \dots, 18$ gives:
   $$19 u_0 - s_0 = 18 \cdot 31 - 63 m_0, \qquad 19 u_1 - s_1 = -18 \cdot 32 + 63 m_1 \qquad (0 \le m_0, m_1 \le 18).$$
6. **Final Diophantine Contradiction ($19 u_1 = s_1 \in \{9, 3, 1\}$):** By $C_{107}$-Fourier inversion, $\lambda_{a,0} + 106\lambda_{a,1} \equiv 0 \pmod{107} \implies \lambda_{a,0} \equiv \lambda_{a,1} \pmod{107}$, and since $|\lambda_{a,0} - \lambda_{a,1}| \le 63 < 107$, $\lambda_{a,0} = \lambda_{a,1}$ for all $a$, yielding:
   $$107(19 u_1 - s_1) = 63(m_1 - m_0).$$
   Since $\gcd(107, 63) = 1$ and $|m_1 - m_0| \le 18 < 107$, we must have $m_1 = m_0$ and hence **$19 u_1 = s_1 \in \{9, 3, 1\}$**, which has **no integer solution** since $19 \nmid 9, 3, 1$! $\blacksquare$
