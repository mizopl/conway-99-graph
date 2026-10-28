# Meta-Level Research Notes & Open Directions (`Work in Progress`): The 6D Orthoplex $\beta_6$, `1-3 / 3-1` Ternary Domino Duality, 5-Graph Diophantine Classification ($d \mid 63$), and Cross-Slice Coupling

> **Status (`2026-10-28`, Meta-Research / Work in Progress):** These notes document our ongoing architectural exploration beyond single-slice row-by-row enumeration, developed within the **[`we*star`](https://github.com/mizopl/we-star)** human–AI autoresearch loop on a single 16 GB Apple M1 laptop. Rather than a finished academic paper, this document serves as an open laboratory notebook mapping the higher-dimensional geometry of the problem (`Theorems 33–37`, machine-checked in Core Lean 4.35.0 with `0 sorryAx` in [`verify-it-yourself/ChiralNullspaceAndHandshaking.lean`](../verify-it-yourself/ChiralNullspaceAndHandshaking.lean)) and outlining the next structural directions ($\mathcal{T}_1$ & $\mathcal{T}_3$).

---

## 1. Where the Proof Stands Today (`What Is 100% Closed vs What Remains Open`)

Across the automorphism and local-slice hierarchy of John H. Conway's 99-graph problem ($\Gamma = \mathrm{srg}(99, 14, 1, 2)$, $\lambda = 1$, $\mu = 2$):

1. **Global Automorphism Group $\mathrm{Aut}(\Gamma)$ Reduced to $|\mathrm{Aut}(\Gamma)| \mid 54 = 2 \cdot 3^3$ (`100% Certified`):**
   - The last open prime divisor $p = 7$ (`p7_fix1`, $|\mathrm{Fix}(g)| = 1$, $14 \times 7$-cycles) is unconditionally refuted in **$0.82\text{s}$** via the **Galois-Spectral Trace Theorem** ($\mathrm{Tr}(B) = 0$) and dual Pure-RUP LRAT certificates (`0 RAT lemmas`).
   - **18 of the 19 involution profiles ($p = 2$)** (every profile with $|\mathrm{Fix}(g)| \ge 3$) are unconditionally refuted by the **Global Flipped-Edge Triangle Bijection Theorem** ($E_{\text{flip}}(g) = 4\dim V_{-1}(g) - 7M_3(-1)$), isolating the single central involution `(0, 7, 0)` ($g = -I_7 \in Z(B_7)$, $|\mathrm{Fix}(g)| = 1$).
   - Thus any non-trivial symmetry group of $\Gamma$ must satisfy $|\mathrm{Aut}(\Gamma)| \mid 54 = 2 \cdot 3^3$ (and if $2 \mid |\mathrm{Aut}(\Gamma)|$, then $\mathrm{Aut}(\Gamma) \cong P_3 \rtimes \mathbb{Z}_2$ with $|\mathrm{Aut}(\Gamma)| \in \{2, 6, 18, 54\}$).

2. **All Symmetric, Polygonally Decomposable, and Seed Dodecagonal $C_{12}$ Strata under `(0, 7, 0)` (`913 / 913 = 100% Certified UNSAT` on a Single M1 Laptop):**
   - Every orbit with $\ge 1$ Type-I block ($k_{\text{type1}}(S_r) \ge 1$: `391 / 391 UNSAT`), every multi-component polygonal cleavage of the dodecagon (`4+2`: `168 / 168 UNSAT`, `3+3`: `55 / 55` canonical = `178 / 178 UNSAT`, `2+2+2`: `10 / 10` canonical = `265 / 265 UNSAT`), and all **`3 / 3` Seed Dodecagon $C_{12}$ orbits at ground state $h = 0$ (`Orbit 0`, `Orbit 1670`, `Orbit 2118`)** are `100% CERTIFIED UNSAT` (`sols = 0`).

3. **The Irreducible Freckled Stratum (`Class 6`, $h = 1..6$): `270 / 2,670` (`10.11%`) Certified `UNSAT` (`1,180 / 3,580 = 32.96%` Total Orbits):**
   - Within the remaining single-component `Class 6` stratum (`2,670` canonical orbits across freckle excitation rings $h = 1..6$), **`270` orbits** (`269` in [`verify-it-yourself/null2_k0_6_partial.json`](../verify-it-yourself/null2_k0_6_partial.json) + `Orbit 2118`, with `41` active mid-bundle checkpoints saved in [`verify-it-yourself/null2_k0_6_ckpts.json`](../verify-it-yourself/null2_k0_6_ckpts.json)) are certified `UNSAT` (`sols = 0`).

---

## 2. Meta-Level Geometric Synthesis (`Theorems 33–37`, Core Lean 4.35.0, `0 sorryAx`)

### 2.1. `Theorem 33` & `Theorem 34`: The 8-Bucket Throat Partition & Future-Hole Overlap Cone (`Sieve-Cone`)
At the half-crystal horizon `d6` ($6$ rows = $3$ $M_0$-dominoes), the $60$ columns split into $36$ saturated (`u2 = 1`), $12$ active (`u1 = 1`), and $12$ empty (`E12`) columns.
- **`Theorem 33` (`we_star_throat_eight_bucket_partition_and_conway_family_seed_law`):** Any remaining row $x_r$ ($r \in \{6, \dots, 11\}$) satisfies $\langle x_r, U_2^{(3)} \rangle + \langle x_r, U_1^{(3)} \rangle + \langle x_r, E_{12} \rangle = 10$ with exact `(0, 6, 4)` split, partitioning the $12$ active columns into $8$ chiral buckets under $g$ and forcing the 4-bit hole $H_3 = E_{12} \setminus (x_6 \mid x_7)$ to lie inside $\binom{12}{4} = 495 < 2^9$ states.
- **`Theorem 34` (`we_star_future_hole_overlap_partition_and_monotone_threshold_ladder`):** Before generating `d6`, for any 4-row prefix $(x_0, x_1, x_2, x_3)$ and any future row $r \ge 6$:
  $$\langle x_4, x_r \rangle + \langle x_5, x_r \rangle = 2 - M_0(4, r) - M_0(5, r) = 2 \quad \Longrightarrow \quad \big|(x_4 \oplus x_5) \cap \mathrm{Valid}_r(E_{24})\big| = 6 - \big|x_r \cap E_{12}\big| = 2,$$
  and similarly for $g(x_r)$ against $\mathrm{KW}_0[4, r] + \mathrm{KW}_0[5, r]$. Precomputing the 60 column-wise 512-bit masks `s_col_i5_mask[60][8]` at `d4` and propagating two monotone threshold ladders (`ge1, ge2, ge3` for $E_{12}$ and `k1, k2, k3` for $g(E_{12})$) cuts the `Stage C` (`d4 -> d6`) candidate loop by **`~1.75x` end-to-end wall-clock speedup**.

---

### 2.2. `Theorem 35`: Why a Regular Dodecagon $C_{12}$ Appears in 6 Dimensions ($\beta_6 \subset \mathbb{R}^6$, $D_6$ Roots & `1-3 / 3-1` Ternary Domino Duality)
Why does a slice of Conway's 99-graph have **12 vertices**, **60 columns**, and a ground state equal to the **Regular Dodecagon $C_{12}$**?
- **The 6-Dimensional Cross-Polytope (Orthoplex) $\beta_6 \subset \mathbb{R}^6$:**
  The 12 slice vertices are the 12 poles $\{\pm e_0, \dots, \pm e_5\} \subset \mathbb{R}^6$ of the **6-dimensional orthoplex $\beta_6 \cong K_{2,2,2,2,2,2}$** ($F_{12}(u) = -u$). Its 60 edges are in canonical bijection with the **60 roots of the $D_6$ root lattice**:
  $$\Phi(D_6) = \{\pm e_a \pm e_b : 0 \le a < b \le 5\} \subset \mathbb{R}^6, \qquad r_{g(c)} = -r_c.$$
  Under orthogonal projection of $\beta_6 \subset \mathbb{R}^6$ onto the 2-dimensional **$B_6$ Coxeter plane** (Coxeter number $h(B_6) = 12$), the **Petrie polygon of the 6-orthoplex $\beta_6$ is the Regular Dodecagon $C_{12}$**!
- **Law I (`6D Root-Momentum Conservation`):**
  Let $L \in \{-1, 0, +1\}^{6 \times 12}$ map vertex $2b \mapsto +e_b$ and $2b+1 \mapsto -e_b$. Since $F_{12} L^T = -L^T$ and $J_{12} L^T = 0$, the block-degree matrix $\Delta_0 = 2J_{12} - I_{12} - F_{12} - M_0 - E_0 F_{12}$ satisfies:
  $$\Delta_0 L^T = (E_0 - M_0) L^T \quad \Longrightarrow \quad \vec{P}_i = \sum_{c \in x_i} r_c = \ell(e_0(i)) - \ell(m_0(i)) \in \mathbb{Z}^6,$$
  forcing $\vec{P}_i = \vec{0}$ whenever $m_0(i) = e_0(i)$ and $\sum_{i \in C} \vec{P}_i = \vec{0}$ around every cycle $C$ of $M_0 \cup E_0$.
- **Law II (`The 1-3 / 3-1 Ternary Domino Duality & Mod-3 Blindness`):**
  Contracting $\mathrm{KW}_0$ and $\Delta_0$ along the 6 dominoes $U_{M_0} \in \{0, 1\}^{6 \times 12}$ of $M_0$ ($U_{M_0} M_0 = U_{M_0}$) yields (`0` errors across all `2,670` `Class 6` orbits):
  $$\mathrm{KW}_{\text{dom}} = U_{M_0} \mathrm{KW}_0 U_{M_0}^T = 8 J_6 - \mathbf{1}\cdot F_{M_0} - \mathbf{3}\cdot E_{M_0} - 4 I_6 \equiv 2 J_6 - F_{M_0} - I_6 \pmod 3,$$
  $$\Delta_{\text{dom}} = U_{M_0} \Delta_0 U_{F_{12}}^T = 8 J_6 - \mathbf{3}\cdot B_{FM} - \mathbf{1}\cdot T_{ME} \equiv 2 J_6 - T_{ME} \pmod 3,$$
  where $F_{M_0} = U_{M_0} F_{12} U_{M_0}^T$, $E_{M_0} = U_{M_0} E_0 U_{M_0}^T$, $B_{FM} = U_{M_0} U_{F_{12}}^T$, and $T_{ME} = U_{M_0} E_0 U_{F_{12}}^T$. Modulo $3$, $\mathrm{KW}_{\text{dom}}$ is completely blind to $E_0$, while $\Delta_{\text{dom}}$ is completely blind to $F_{12}$!
- **Law III (`Domino-Hole Chiral Envelope` $H_3 \subset S_4 \cap S_5$):**
  Since $S_4 + S_5 = 2 H_3 + U_1^{(4)}$ with $S_4, S_5 \in \{0, 1\}^{60}$, the 4-bit hole $H_3 = E_{12} \setminus (x_6 \mid x_7)$ satisfies $H_3 \subset S_4 \cap S_5$, forcing for every row $r \in \{0, \dots, 7\}$:
  $$\mathrm{popcnt64}\big(H_3 \ \& \ g(x_r)\big) \le \min\big(\mathrm{KW}_0[r, 8] + \mathrm{KW}_0[r, 9], \;\; \mathrm{KW}_0[r, 10] + \mathrm{KW}_0[r, 11]\big).$$

---

### 2.3. `Theorem 36`: Universal 5-Graph Diophantine & Orthoplex-Ternary Classification ($d \mid 63 = 3^2 \times 7$)
In any strongly regular graph $\mathrm{srg}(n, k, 1, 2)$, setting $k = 2m$, $n = 2m^2 + 1$, and $\Delta = 8m - 7 = d^2$ ($d = 2u - 1$) yields:
$$128 m(mu - 1) = d\big(16 u d^2 + 8 d + 90\big) - 126 \quad \Longrightarrow \quad d \;\big|\; 63 = 3^2 \times 7,$$
$$m - 2 = \frac{(d - 3)(d + 3)}{8}, \qquad 32 n = d^4 + 14 d^2 + 81.$$
Thus the entire family $\mathrm{srg}(2m^2 + 1, 2m, 1, 2)$ contains **uniquely 5 arithmetically feasible parameter sets**, split into two branches by the prime $7$:

| $d = 2u-1$ | Graph $\mathrm{srg}(n, k, 1, 2)$ | Orthoplex & Petrie Polygon | $m - 2 \pmod 9$ & Domino Weights | Chiral Parity $(m - 3) \bmod 2$ | Automorphisms $|\mathrm{Aut}(\Gamma)|$ & Structural Fate |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **$3 = 3^1$** | **`SRG(9, 4, 1, 2)`**<br>$n = 3^2$ | $\beta_1 \subset \mathbb{R}^1$, **$C_4$**<br>($R = 0$ roots) | $m - 2 = 0 \equiv 0 \pmod 9$<br>`row = 0, dom = 0` | — ($R = 0$) | **$|\mathrm{Aut}| = 72 = 3^2 \cdot 8$** (`SAT = 1`, unique). Affine $\mathbb{F}_3^2$; outer orbit killed in 1 line by reflection $M_0 E_0 = F_4$. |
| **$7 = 7 \cdot 1$** | **`SRG(99, 14, 1, 2)`**<br>$n = 3^2 \cdot 11$ | $\beta_6 \subset \mathbb{R}^6$, **$C_{12}$**<br>($R = 60$ roots of $D_6$) | **$m - 2 = 5 \not\equiv 0 \pmod 3$**<br>`row = 10 ≡ 1, dom = 20 ≡ 2 (mod 3)` | $4 \equiv 0 \pmod 2$<br>(`colSum = 2`) | **$|\mathrm{Aut}| \mid 54 = 2 \cdot 3^3$**. **Unique graph where $3 \nmid d$**, breaking $\mathbb{F}_3$ divisibility; `18/19` involutions & all `913/913` symmetric + $C_{12}$ seed orbits `UNSAT`. |
| **$9 = 3^2$** | **`SRG(243, 22, 1, 2)`**<br>$n = 3^5$ | $\beta_{10} \subset \mathbb{R}^{10}$, **$C_{20}$**<br>($R = 180$ roots of $D_{10}$) | **$m - 2 = 9 \equiv 0 \pmod 9$**<br>`row = 18, dom = 36 ≡ 0 (mod 9)` | $8 \equiv 0 \pmod 2$<br>(`colSum = 4`) | **$|\mathrm{Aut}| = 3,849,120 = 3^5 \cdot 2 \cdot |M_{11}|$** (`SAT`). Affine $\mathbb{F}_3^5$ (Golay code $\mathcal{G}_{12}$); every slice maximally symmetric $M_0 = E_0 = F_{20}$. |
| **$21 = 7 \cdot 3$** | **`SRG(6273, 112, 1, 2)`**<br>$n = 3^2 \cdot 17 \cdot 41$ | $\beta_{55} \subset \mathbb{R}^{55}$, **$C_{110}$**<br>($R = 5,940$ roots of $D_{55}$) | $m - 2 = 54 \equiv 0 \pmod 9$<br>`row = 108, dom = 216` | **$53 \equiv 1 \pmod 2$**<br>(`(m-3)/2 = 26.5 ∉ ℤ`) | **Central involution $g = -I_{56}$ IMPOSSIBLE (`Theorem 2`)!** Multiplying $7 \times 3$ restores $\pmod 9$ but forces $m = 56$ even, killing $\mathbb{Z}_2$ chiral parity. |
| **$63 = 7 \cdot 9$** | **`SRG(494019, 994, 1, 2)`**<br>$n = 3^5 \cdot 19 \cdot 107$ | $\beta_{496} \subset \mathbb{R}^{496}$, **$C_{992}$**<br>($R = 491,040$ roots of $D_{496}$) | $m - 2 = 495 \equiv 0 \pmod 9$<br>`row = 990, dom = 1980` | $494 \equiv 0 \pmod 2$<br>(`(m-3)/2 = 247`) | **No $\mathbb{F}_3$ affine translation group** ($n = 243 \cdot 2033$ not a prime power); Mod-2 Triple-Block Parity ($k_{\text{type1}} \le 2$) blocks $M_0 = E_0 = F_{992}$. |

---

### 2.4. `Theorem 37`: Cross-Slice Residual Matrix Identity & Four-Fold Mask-Exclusion Laws (`Laws T1-A, T1-B, T1-C1, T1-C2`)
In a single-slice solver (`Lens 3`), enforcing $M_{36 \times 60} M_{36 \times 60}^T = G_{36}(M_0, E_0)$ on the stacked $36 \times 60$ incidence matrix $M_{36 \times 60} = (W^T, X^T, g(X)^T)^T$ checks only row inner products, ignoring the **entrywise non-negativity of the cross-slice walk equation** $(A_{99}^2 + A_{99})_{S_{36}, R_{60}} = 2 J_{36 \times 60}$:
$$M_{36 \times 60} \, A_{60} \;=\; 2 J_{36 \times 60} \;-\; (I_{36} + B_{36}) \, M_{36 \times 60} \;\in\; \{0, 1, 2\}^{36 \times 60}, \qquad B_{36} = \begin{pmatrix} F_{12} & I_{12} & F_{12} \\ I_{12} & M_0 & E_0 \\ F_{12} & E_0 & M_0 \end{pmatrix}.$$
Since $B_{36}$ is 3-regular and $x_k \cap x_{m(k)} = \emptyset$, the 36-row non-negativity condition $M_{36 \times 60} A_{60} \ge 0$ (`Theorem 37`, `we_star_cross_slice_residual_matrix_and_mask_exclusion_theorem`) is **strictly equivalent** to the **Four-Fold Cross-Slice Mask-Exclusion Law** for every row pair $(i, i') \in \{0, \dots, 11\}^2$:
$$\big(x_i \ \& \ g(x_{i'}) \ \& \ \mathrm{Forb}_{M_0, E_0}[i, i']\big) \;=\; 0,$$
where:
$$\mathrm{Forb}_{M_0, E_0}[i, i'] \;=\; \underbrace{F_{12}[i, i']\,(W_j[i] \cup W_j[f(i)])}_{\text{Law T1-A (Domino)}}\;\cup\;\underbrace{E_0[i, i']\,(W_j[i] \cup W_j[f(i')])}_{\text{Law T1-B ($E_0$-edge)}}\;\cup\;\underbrace{(M_0 E_0)[i, i']\,W_j[m(i)]}_{\text{Law T1-C1 ($M_0 E_0$-walk)}}\;\cup\;\underbrace{(E_0 M_0)[i, i']\,W_j[f(e(i))]}_{\text{Law T1-C2 ($E_0 M_0$-walk)}}.$$
- **Zero-Overhead Bitwise Filtering on Local M1 CPU (`bench_t1_d8.py`):** Because `x_a & gx_b` is already computed in registers when checking `popcnt64(x_a & gx_b) == kw[a, b]`, adding `((x_a & gx_b) & fb[a, b]) == 0ULL` costs a single bitwise `AND` and prunes up to **`-21.3%` at `d4`**, **`-29.0%` at `d6`**, and **`-20.9%` at `d7/d8`** across multi-active `Class 6` bundles (`Bundle 6: d4 78.7%, d6 71.0%, d7 79.1%`; `Bundle 7: d6 77.2%, d7 79.8%, d8 79.2%`; `Bundle 3: d6 86.5%, d7 85.1%`; `Bundle 0: d6 91.9%, d7 84.0%`).

---

## 3. Next Open Architectural Directions (`Work in Progress` on Local M1 CPU)

Rather than brute-forcing the remaining `Class 6` orbits one isolated slice $S_0$ at a time on paid cloud GPUs, we are actively pursuing two structural reductions on a single Apple M1 laptop:

### Direction $\mathcal{T}_1$: Global 7-Slice Triality Coupling on the $42 \times 42$ Orbit Space
Evaluating a single slice $S_0$ in isolation ignores the other **6 slices $S_1, \dots, S_6$** around $x_0$. In the full 99-vertex graph under $g = -I_7$:
- All **7 slices $S_0, \dots, S_6$** intersect pairwise across the $\binom{7}{2} = 21$ four-vertex cells $Q_{\{r, t\}} = S_r \cap S_t$ ($42$ involution orbits) and must **simultaneously** avoid all `913` certified `UNSAT` symmetric/decomposable/seed orbits and all `270` certified `UNSAT` `Class 6` orbits.
- Since $k_{\text{type1}}(S_r) = 0$ for all $r \in \{0, \dots, 6\}$, in the global $42 \times 42$ equation $B = 2P_\pi + |D|$ ($B^2 + B - 12I_{42} = M_{21}^{\text{true}} \otimes J_2$), no involution partner $\pi(u)$ can lie in the same cell $Q_{\{r, t\}}$, so $\pi(u)$ cannot lie in $S_r \cap S_t$. Consequently, for every orbit $u \in Q_{\{r, t\}}$, **at most one** of the two slices $S_r, S_t$ can have a diagonal freckle $\mathrm{KW}(u, u) = 0$ ($M^+(u) = E(u)$), while any diagonal freckle in $S_r$ rigidly pins the $\Lambda$-hinge $\{c, g(c)\}$ in the dual slices.

### Direction $\mathcal{T}_3$: Orthoplex-to-Orthoplex Edge Bijection ($X = U_{M_0}\Pi$)
Because every column $c \in \{0, \dots, 59\}$ of $X \in \{0, 1\}^{12 \times 60}$ has exact column sum $\mathrm{colSum}(c) = 2$ and $(X X^T)_{i, j} = 1 - M_0(i, j) \in \{0, 1\}$ ($i \ne j$), **the 60 columns of $X$ are always a permutation $\Pi \in S_{60}$ of the 60 fixed edges of the $M_0$-orthoplex $\beta_6(M_0)$**:
$$E(\beta_6(M_0)) = \big\{\{i, j\} \subset \{0, \dots, 11\} : i < j, \; j \ne m_0(i)\big\}, \qquad \mathrm{KW}_0 = \sum_{r=0}^{29} \big(\mathbf{1}_{e_r}\mathbf{1}_{e_r'}^T + \mathbf{1}_{e_r'}\mathbf{1}_{e_r}^T\big).$$
Each of the 6 column-blocks $b \in \{0, \dots, 5\}$ is therefore a 10-edge subgraph $H_b \subset \beta_6(M_0)$ with maximum degree $\Delta_0(i, 2b) \le 2$ (a disjoint union of cycles and paths!), partitioning $E(\beta_6(M_0)) = H_0 \sqcup \dots \sqcup H_5$.

---

## 4. Open Invitation: Compute Partners & Collaborative Completion

All theoretical reductions, formal Lean 4 proofs (`37` theorems, `57` declarations, `0 sorryAx`), CPU solvers (`913 / 913` symmetric, decomposable, and $C_{12}$ seed orbits verifiable on a single 16 GB M1 laptop), and the first **`10.11%` (`270 / 2,670` orbits, `1,180 / 3,580 = 32.96%` of the full `(0, 7, 0)` space)** of the asymmetric `Class 6` sweep were developed by an independent human–AI research team (`we*`) on a single laptop supplemented by modest cloud GPU runs.

While we pursue the pure cross-slice theoretical collapse ($\mathcal{T}_1 + \mathcal{T}_3$) locally, **our deterministic CUDA C++ solver (`Gen V.4` + `Theorems 34, 35 & 37`, with per-batch JSON checkpointing in [`verify-it-yourself/null2_k0_6_ckpts.json`](../verify-it-yourself/null2_k0_6_ckpts.json) and zero-trust SHA-256 verification) is ready to run out-of-the-box on any modern multi-GPU cluster (`NVIDIA A100 / H100`)**.

> **If you have access to a larger GPU cluster and would enjoy contributing compute cycles to help finish the remaining checkpointed `Class 6` bundles — or collaborating on the final verification — we warmly invite you to reach out (via GitHub Issues/Discussions on [`mizopl/conway-99-graph`](https://github.com/mizopl/conway-99-graph)) for full co-authorship / joint credit on the completed certificate.**
