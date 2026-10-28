import os
os.environ.setdefault("BUNDLE_LIST", "")
os.environ.setdefault("MAX_BATCHES", "0")
import base64
import ctypes
import json
import subprocess
import sys
import time
import zlib
import numpy as np
from itertools import combinations, permutations, product

TRIE_B64 = "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"

CUDA_SRC = r"""
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <cuda_runtime.h>

__device__ __host__ __forceinline__ int popcnt64(uint64_t x) {
#ifdef __CUDA_ARCH__
    return __popcll(x);
#else
    return __builtin_popcountll(x);
#endif
}

struct RowGen6Ctx {
    int cols_u[60];
    int cols_v[60];
    int g_col[60];
    int orbs_c[30];
    int orbs_gc[30];
    int rem_deg[12];
    int adj_len[12];
    int adj_c[12][60];
    int adj_w[12][60];
    int chosen[12];
    int chosen_len;
    int req_pairs;
    uint64_t* out_buf;
    int out_count;
    int max_rows;
};

static void bt_v_6(RowGen6Ctx* ctx, int v_idx) {
    if (v_idx == 12) {
        if (ctx->chosen_len == 10) {
            uint64_t xm = 0ULL;
            for (int i = 0; i < 10; ++i) {
                xm |= (1ULL << ctx->chosen[i]);
            }
            int npairs = 0;
            for (int i = 0; i < 10; ++i) {
                int c = ctx->chosen[i];
                int gc = ctx->g_col[c];
                if (c < gc && ((xm >> gc) & 1ULL)) {
                    npairs++;
                }
            }
            if (npairs == ctx->req_pairs) {
                uint64_t gxm = 0ULL;
                for (int i = 0; i < 10; ++i) {
                    gxm |= (1ULL << ctx->g_col[ctx->chosen[i]]);
                }
                uint64_t o2 = 0ULL;
                for (int m = 0; m < 30; ++m) {
                    int c = ctx->orbs_c[m];
                    int gc = ctx->orbs_gc[m];
                    if (((xm >> c) & 1ULL) && ((xm >> gc) & 1ULL)) {
                        o2 |= (1ULL << m);
                    }
                }
                if (ctx->out_count < ctx->max_rows) {
                    size_t base = (size_t)ctx->out_count * 3;
                    ctx->out_buf[base + 0] = xm;
                    ctx->out_buf[base + 1] = gxm;
                    ctx->out_buf[base + 2] = o2;
                }
                ctx->out_count++;
            }
        }
        return;
    }
    int need = ctx->rem_deg[v_idx];
    if (need < 0) return;
    int avail_c[60], avail_w[60];
    int n_avail = 0;
    for (int i = 0; i < ctx->adj_len[v_idx]; ++i) {
        int c = ctx->adj_c[v_idx][i];
        int w = ctx->adj_w[v_idx][i];
        if (ctx->rem_deg[w] > 0) {
            avail_c[n_avail] = c;
            avail_w[n_avail] = w;
            n_avail++;
        }
    }
    if (n_avail < need) return;
    if (need == 0) {
        ctx->rem_deg[v_idx] = 0;
        bt_v_6(ctx, v_idx + 1);
        ctx->rem_deg[v_idx] = 0;
    } else if (need == 1) {
        ctx->rem_deg[v_idx] = 0;
        for (int i = 0; i < n_avail; ++i) {
            int c = avail_c[i], w = avail_w[i];
            ctx->rem_deg[w]--;
            ctx->chosen[ctx->chosen_len++] = c;
            bt_v_6(ctx, v_idx + 1);
            ctx->chosen_len--;
            ctx->rem_deg[w]++;
        }
        ctx->rem_deg[v_idx] = 1;
    } else if (need == 2) {
        ctx->rem_deg[v_idx] = 0;
        for (int i = 0; i < n_avail; ++i) {
            for (int j = i + 1; j < n_avail; ++j) {
                int c1 = avail_c[i], w1 = avail_w[i];
                int c2 = avail_c[j], w2 = avail_w[j];
                ctx->rem_deg[w1]--;
                ctx->rem_deg[w2]--;
                ctx->chosen[ctx->chosen_len++] = c1;
                ctx->chosen[ctx->chosen_len++] = c2;
                bt_v_6(ctx, v_idx + 1);
                ctx->chosen_len -= 2;
                ctx->rem_deg[w1]++;
                ctx->rem_deg[w2]++;
            }
        }
        ctx->rem_deg[v_idx] = 2;
    }
}

extern "C" int c_gen_6block_rows(
    const int* cols_u, const int* cols_v, const int* g_col,
    const int* orbs_c, const int* orbs_gc,
    const int* target_deg, int diag_kw,
    uint64_t* out_buf, int max_rows
) {
    RowGen6Ctx ctx;
    memcpy(ctx.cols_u, cols_u, 60 * sizeof(int));
    memcpy(ctx.cols_v, cols_v, 60 * sizeof(int));
    memcpy(ctx.g_col, g_col, 60 * sizeof(int));
    memcpy(ctx.orbs_c, orbs_c, 30 * sizeof(int));
    memcpy(ctx.orbs_gc, orbs_gc, 30 * sizeof(int));
    memcpy(ctx.rem_deg, target_deg, 12 * sizeof(int));
    memset(ctx.adj_len, 0, sizeof(ctx.adj_len));
    ctx.chosen_len = 0;
    ctx.req_pairs = diag_kw / 2;
    for (int c = 0; c < 60; ++c) {
        int u = cols_u[c], v = cols_v[c];
        if (target_deg[u] > 0 && target_deg[v] > 0) {
            int mn = u < v ? u : v;
            int mx = u < v ? v : u;
            int idx = ctx.adj_len[mn]++;
            ctx.adj_c[mn][idx] = c;
            ctx.adj_w[mn][idx] = mx;
        }
    }
    ctx.out_buf = out_buf;
    ctx.out_count = 0;
    ctx.max_rows = max_rows;
    bt_v_6(&ctx, 0);
    return ctx.out_count;
}

__global__ void compute_canon3_kernel(
    const uint64_t* __restrict__ L_a,
    int n_rows,
    const int32_t* __restrict__ perms,
    int n_perms,
    uint64_t* __restrict__ out_can
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_rows) return;
    uint64_t mask = L_a[(size_t)idx * 3 + 0];
    uint64_t best = ~0ULL;
    for (int p = 0; p < n_perms; ++p) {
        const int32_t* perm = perms + p * 60;
        uint64_t nm = 0ULL;
        for (int c = 0; c < 60; ++c) {
            if ((mask >> c) & 1ULL) {
                nm |= (1ULL << perm[c]);
            }
        }
        if (nm < best) best = nm;
    }
    out_can[idx] = best;
}

#define MAX_C0 65536
#define MAX_C1 16384
#define MAX_C1_67 8192
#define MAX_VALID_I2 4096
#define MAX_B1_PAIRS 65536
#define MAX_R0_SPECS 256
#define MAX_R6_GROUPS 64
#define MAX_R7_GROUPS 104
#define MAX_BUNDLE_MEMBERS 200

struct R0Spec {
    int32_t pool_idx;
    int32_t can_idx; // -1 if no canon filter (~0ULL)
    int32_t gp0a;
    int32_t kw0a;
};

struct R6GroupSpec {
    int32_t r0_id;
    int32_t gp[6]; // gp[1..5]
    int32_t kw[6]; // kw[1..5]
    int32_t g7_start;
    int32_t g7_end;
};

struct R7GroupSpec {
    int32_t r0_id;
    int32_t gp[7]; // gp[1..6]
    int32_t kw[7]; // kw[1..6]
    int32_t mem_start;
    int32_t mem_end;
    int8_t  ub_e8[8]; // Theorem 35 Law II: max_{m in g7} (KW0[r,7] + ub_h3[r]) for r in 0..6
    int8_t  ub_h3[8]; // Theorem 35 Law II: max_{m in g7} min(KW0[r,8]+KW0[r,9], KW0[r,10]+KW0[r,11]) for r in 0..7
};

struct MemberSpec {
    int32_t r0_id[4]; // for rows 8, 9, 10, 11
    int8_t  gp[4][12]; // gp[a-8][0..11]
    int8_t  kw[4][12]; // kw[a-8][0..11]
    int8_t  ub_h3[8];  // Theorem 35 Law II: min(KW0[r,8]+KW0[r,9], KW0[r,10]+KW0[r,11]) for r in 0..7
};

__constant__ int32_t c_cone6_Gp[36];
__constant__ int32_t c_cone6_KW0[36];
__constant__ int32_t c_cone6_r0_id[6];
__constant__ R0Spec c_r0_specs[MAX_R0_SPECS];
__constant__ R6GroupSpec c_r6_specs[MAX_R6_GROUPS];
__constant__ R7GroupSpec c_r7_specs[MAX_R7_GROUPS];

__device__ __forceinline__ uint64_t get_gx(uint64_t rx) {
    return ((rx & 0x1111111111111111ULL) << 3)
         | ((rx & 0x2222222222222222ULL) << 1)
         | ((rx & 0x4444444444444444ULL) >> 1)
         | ((rx & 0x8888888888888888ULL) >> 3);
}

__device__ __forceinline__ bool match_sandwich(uint64_t rx, uint64_t w_inter, uint64_t w_union, int t) {
    if (t == 0) return (rx & w_inter) == 0ULL;
    uint64_t m_u = rx & w_union;
    if (m_u == 0ULL) return false;
    if (t == 2 && (m_u & (m_u - 1ULL)) == 0ULL) return false;
    uint64_t m_i = rx & w_inter;
    if (t == 1) return (m_i & (m_i - 1ULL)) == 0ULL;
    if (t == 2) {
        uint64_t m_i1 = m_i & (m_i - 1ULL);
        return (m_i1 & (m_i1 - 1ULL)) == 0ULL;
    }
    return true;
}

__device__ __forceinline__ uint64_t eval_q_mask(
    uint64_t rx, uint64_t rgx, uint64_t col_u1_012,
    uint64_t active_q, int gp3a, int kw3a,
    const unsigned long long* s_col_q,
    const uint64_t* s_x3_q
) {
    if (active_q == 0ULL) return 0ULL;
    if (popcnt64(active_q) <= 16 || gp3a > 2 || kw3a > 2) {
        uint64_t fb3 = (rx & col_u1_012) | (gp3a == 0 ? rx : 0ULL) | (kw3a == 0 ? rgx : 0ULL);
        uint64_t m = 0ULL, aq = active_q;
        while (aq != 0ULL) {
            int q = __ffsll(aq) - 1;
            aq &= (aq - 1ULL);
            uint64_t x3 = s_x3_q[q];
            if ((x3 & fb3) == 0ULL && (gp3a == 0 || popcnt64(x3 & rx) == gp3a) && (kw3a == 0 || popcnt64(x3 & rgx) == kw3a)) {
                m |= (1ULL << q);
            }
        }
        return m;
    }
    uint64_t forbid_q = ~active_q;
    uint64_t fb_cols = (rx & col_u1_012) | (gp3a == 0 ? rx : 0ULL) | (kw3a == 0 ? rgx : 0ULL);
    while (fb_cols != 0ULL) {
        int c = __ffsll(fb_cols) - 1;
        fb_cols &= (fb_cols - 1ULL);
        forbid_q |= s_col_q[c];
    }
    uint64_t valid_q = ~forbid_q;
    if (valid_q == 0ULL) return 0ULL;

    if (gp3a > 0) {
        uint64_t rem = rx & ~col_u1_012;
        if (gp3a == 1) {
            uint64_t b0 = 0ULL, ovf = ~valid_q;
            while (rem != 0ULL) {
                int c = __ffsll(rem) - 1;
                rem &= (rem - 1ULL);
                uint64_t w = s_col_q[c];
                ovf |= (b0 & w);
                b0  |= w;
            }
            valid_q = b0 & ~ovf;
        } else {
            uint64_t b0 = 0ULL, b1 = 0ULL, ovf = ~valid_q;
            while (rem != 0ULL) {
                int c = __ffsll(rem) - 1;
                rem &= (rem - 1ULL);
                uint64_t w = s_col_q[c];
                ovf |= (b1 & b0 & w);
                b1  ^= (b0 & w);
                b0  ^= w;
            }
            valid_q = b1 & ~b0 & ~ovf;
        }
        if (valid_q == 0ULL) return 0ULL;
    }

    if (kw3a > 0) {
        uint64_t rem = rgx;
        if (kw3a == 1) {
            uint64_t b0 = 0ULL, ovf = ~valid_q;
            while (rem != 0ULL) {
                int c = __ffsll(rem) - 1;
                rem &= (rem - 1ULL);
                uint64_t w = s_col_q[c];
                ovf |= (b0 & w);
                b0  |= w;
            }
            valid_q = b0 & ~ovf;
        } else {
            uint64_t b0 = 0ULL, b1 = 0ULL, ovf = ~valid_q;
            while (rem != 0ULL) {
                int c = __ffsll(rem) - 1;
                rem &= (rem - 1ULL);
                uint64_t w = s_col_q[c];
                ovf |= (b1 & b0 & w);
                b1  ^= (b0 & w);
                b0  ^= w;
            }
            valid_q = b1 & ~b0 & ~ovf;
        }
    }
    return valid_q;
}

// Grid: (batch_n, num_r0_specs), Block: 256
__global__ void stage1_filter_r0_trie_kernel(
    int batch_n,
    int num_r0_specs,
    const int32_t* __restrict__ reps,
    const uint64_t* __restrict__ rep_canons,
    const uint64_t* __restrict__ L0,
    const uint64_t* const* __restrict__ d_pool_ptrs,
    const int32_t* __restrict__ d_pool_lens,
    const uint64_t* const* __restrict__ d_can_ptrs,
    uint64_t* __restrict__ g_c_r0,
    int32_t* __restrict__ g_n_r0,
    int32_t* __restrict__ overflow_flag
) {
    int b_idx = blockIdx.x;
    int s_idx = blockIdx.y;
    if (b_idx >= batch_n || s_idx >= num_r0_specs) return;

    __shared__ int s_cnt;
    int tid = threadIdx.x;
    int bdim = blockDim.x;
    if (tid == 0) s_cnt = 0;
    __syncthreads();

    int i0 = reps[b_idx];
    uint64_t min_can = rep_canons[b_idx];
    uint64_t x0      = L0[(size_t)i0 * 3 + 0];
    uint64_t gx0     = get_gx(x0);

    R0Spec spec = c_r0_specs[s_idx];
    const uint64_t* LA = d_pool_ptrs[spec.pool_idx];
    int len_a = d_pool_lens[spec.pool_idx];
    const uint64_t* CANA = (spec.can_idx >= 0) ? d_can_ptrs[spec.can_idx] : NULL;
    int gp0a = spec.gp0a;
    int kw0a = spec.kw0a;
    uint64_t forbid0 = (gp0a == 0 ? x0 : 0ULL) | (kw0a == 0 ? gx0 : 0ULL);

    uint64_t* ca = g_c_r0 + ((size_t)s_idx * batch_n + b_idx) * MAX_C0;
    for (int i = tid; i < len_a; i += bdim) {
        if (CANA == NULL || CANA[i] >= min_can) {
            uint64_t rx = LA[(size_t)i * 3 + 0];
            if ((rx & forbid0) == 0ULL) {
                if ((gp0a == 0 || popcnt64(x0 & rx) == gp0a) && (kw0a == 0 || popcnt64(gx0 & rx) == kw0a)) {
                    int pos = atomicAdd(&s_cnt, 1);
                    if (pos < MAX_C0) ca[pos] = rx;
                    else atomicExch(overflow_flag, 100 + s_idx);
                }
            }
        }
    }
    __syncthreads();
    if (tid == 0) {
        g_n_r0[s_idx * batch_n + b_idx] = (s_cnt <= MAX_C0) ? s_cnt : MAX_C0;
    }
}

struct BlockScratchTrie {
    uint64_t x2_1[MAX_C1];
    uint64_t x3_1[MAX_C1];
    uint64_t x4_1[MAX_C1];
    uint64_t x5_1[MAX_C1];
    uint64_t x6_1[MAX_R6_GROUPS][MAX_C1_67];
    uint64_t x7_1[MAX_R7_GROUPS][MAX_C1_67];
    uint64_t x3_q_ext[MAX_C1];
    uint64_t x4_r2[2048];
    uint64_t x5_r2[2048];
    uint64_t x4_2_ext[2048];
    uint64_t m4_ext[2048];
    uint64_t x5_2_ext[2048];
    uint64_t m5_ext[2048];
    uint64_t x6_2_ext[2048];
    uint64_t m6_ext[2048];
    uint64_t x7_2_ext[2048];
    uint64_t m7_ext[2048];
    uint32_t v345_ext[4096];
    uint64_t col_u2_5_ext[4096];
    uint32_t d7_ext[2048];
};

__global__ void stage2_6_trie_kernel(
    int batch_n,
    int total_tasks,
    int num_r6,
    int num_r7,
    int num_members,
    const int2* __restrict__ tasks,
    int* __restrict__ d_task_counter,
    const int32_t* __restrict__ reps,
    const uint64_t* __restrict__ L0,
    const uint64_t* __restrict__ g_c_r0,
    const int32_t* __restrict__ g_n_r0,
    const MemberSpec* __restrict__ d_mem_specs,
    BlockScratchTrie* __restrict__ scratch_pool,
    unsigned long long* __restrict__ d_d4_cnt,
    unsigned long long* __restrict__ d_d6_cnt,
    unsigned long long* __restrict__ d_d8_per_g7,
    unsigned long long* __restrict__ d_sol_per_mem,
    int32_t* __restrict__ overflow_flag
) {
    __shared__ int s_task_idx;
    __shared__ int s_n2_1, s_n3_1, s_ni3;
    __shared__ int s_n4_1, s_n5_1;
    __shared__ int s_n6_1[MAX_R6_GROUPS];
    __shared__ int s_n7_1[MAX_R7_GROUPS];
    __shared__ int s_n4_2, s_n5_2, s_n6_2, s_n7_2, s_n_v345, s_n_d7, s_tmp_cnt;
    __shared__ int s_n4_r2, s_n5_r2;
    __shared__ unsigned long long s_active_q_mask;
    __shared__ unsigned long long s_d7_q_mask;
    __shared__ unsigned long long s_cu2_3_inter, s_x3_inter, s_x3_union, s_gx3_inter, s_gx3_union;
    __shared__ unsigned long long s_active_q4_mask, s_x4_2_inter, s_x4_2_union, s_gx4_2_inter, s_gx4_2_union;
    __shared__ unsigned long long s_cu2_5_inter, s_x4_inter, s_gx4_inter, s_x5_inter, s_gx5_inter;
    __shared__ unsigned long long s_x4_union, s_gx4_union, s_x5_union, s_gx5_union, s_v3_inter, s_v3_union, s_vg3_inter, s_vg3_union;
    __shared__ unsigned long long s_d7_cu2_6_inter, s_d7_x4_inter, s_d7_gx4_inter, s_d7_x5_inter, s_d7_gx5_inter, s_d7_x6_inter, s_d7_gx6_inter;
    __shared__ unsigned long long s_d7_x4_union, s_d7_gx4_union, s_d7_x5_union, s_d7_gx5_union, s_d7_x6_union, s_d7_gx6_union;
    __shared__ unsigned long long s_cu2_q_inter[64];
    __shared__ unsigned long long s_d7_cu2_q_inter[64];
    __shared__ unsigned long long s_d7_x6_q_inter[64];
    __shared__ unsigned long long s_d7_gx6_q_inter[64];
    __shared__ unsigned long long s_q_u_mask[64][8];
    __shared__ uint64_t s_x3_q[64];
    __shared__ uint64_t s_gx3_q[64];
    __shared__ uint64_t s_x456_2[2048];
    __shared__ uint64_t s_m45[1024];
    __shared__ uint64_t s_col_u2_5[1024];
    __shared__ uint32_t s_v345[1024];
    __shared__ uint32_t s_d7[512];

    uint64_t* s_x4_2 = &s_x456_2[0];
    uint64_t* s_x5_2 = &s_x456_2[512];
    uint64_t* s_x6_2 = &s_x456_2[1024];
    unsigned long long (*s_col_i5_mask)[8] = (unsigned long long (*)[8])(&s_x456_2[1024]);
    uint64_t* s_m4 = &s_m45[0];
    uint64_t* s_m5 = &s_m45[512];
    uint64_t* s_m6 = &s_m45[0];

    int tid = threadIdx.x;
    int bdim = blockDim.x;
    BlockScratchTrie* my_scratch = scratch_pool + blockIdx.x;

    unsigned long long my_d4 = 0ULL;
    unsigned long long my_d6 = 0ULL;
    const uint64_t MASK60 = (1ULL << 60) - 1ULL;

    int gp12 = c_cone6_Gp[1 * 6 + 2], kw12 = c_cone6_KW0[1 * 6 + 2];
    int gp13 = c_cone6_Gp[1 * 6 + 3], kw13 = c_cone6_KW0[1 * 6 + 3];
    int gp14 = c_cone6_Gp[1 * 6 + 4], kw14 = c_cone6_KW0[1 * 6 + 4];
    int gp15 = c_cone6_Gp[1 * 6 + 5], kw15 = c_cone6_KW0[1 * 6 + 5];

    int gp23 = c_cone6_Gp[2 * 6 + 3], kw23 = c_cone6_KW0[2 * 6 + 3];
    int gp24 = c_cone6_Gp[2 * 6 + 4], kw24 = c_cone6_KW0[2 * 6 + 4];
    int gp25 = c_cone6_Gp[2 * 6 + 5], kw25 = c_cone6_KW0[2 * 6 + 5];

    int gp34 = c_cone6_Gp[3 * 6 + 4], kw34 = c_cone6_KW0[3 * 6 + 4];
    int gp35 = c_cone6_Gp[3 * 6 + 5], kw35 = c_cone6_KW0[3 * 6 + 5];
    int gp45 = c_cone6_Gp[4 * 6 + 5], kw45 = c_cone6_KW0[4 * 6 + 5];

    int r0_id1 = c_cone6_r0_id[1];
    int r0_id2 = c_cone6_r0_id[2];
    int r0_id3 = c_cone6_r0_id[3];
    int r0_id4 = c_cone6_r0_id[4];
    int r0_id5 = c_cone6_r0_id[5];

    while (true) {
        if (tid == 0) {
            s_task_idx = atomicAdd(d_task_counter, 1);
            s_n2_1 = s_n3_1 = 0;
            s_n4_1 = s_n5_1 = 0;
        }
        for (int g = tid; g < num_r6; g += bdim) s_n6_1[g] = -1;
        for (int g = tid; g < num_r7; g += bdim) s_n7_1[g] = -1;
        __syncthreads();

        int t_idx = s_task_idx;
        if (t_idx >= total_tasks) break;

        int2 task = tasks[t_idx];
        int b_idx = task.x;
        int idx1  = task.y;

        int i0 = reps[b_idx];
        uint64_t x0   = L0[(size_t)i0 * 3 + 0];
        uint64_t gx0  = get_gx(x0);
        uint64_t x1   = g_c_r0[((size_t)r0_id1 * batch_n + b_idx) * MAX_C0 + idx1];
        uint64_t gx1  = get_gx(x1);
        uint64_t col_u2_01 = x0 & x1;

        #define FILTER_R1_CONE(SPEC_ID, X1A, SN1A, GP1A, KW1A, CODE) \
        { \
            const uint64_t* c0_ptr = g_c_r0 + ((size_t)(SPEC_ID) * batch_n + b_idx) * MAX_C0; \
            int n0_cnt = g_n_r0[(SPEC_ID) * batch_n + b_idx]; \
            uint64_t fb1 = col_u2_01 | ((GP1A) == 0 ? x1 : 0ULL) | ((KW1A) == 0 ? gx1 : 0ULL); \
            for (int k = tid; k < n0_cnt; k += bdim) { \
                uint64_t rx = c0_ptr[k]; \
                if ((rx & fb1) == 0ULL) { \
                    if (((GP1A) == 0 || popcnt64(x1 & rx) == (GP1A)) && ((KW1A) == 0 || popcnt64(gx1 & rx) == (KW1A))) { \
                        int pos = atomicAdd(&SN1A, 1); \
                        if (pos < MAX_C1) my_scratch->X1A[pos] = rx; else atomicExch(overflow_flag, (CODE)); \
                    } \
                } \
            } \
        }

        bool same45 = (r0_id4 == r0_id5 && gp14 == gp15 && kw14 == kw15 && gp24 == gp25 && kw24 == kw25 && gp34 == gp35 && kw34 == kw35);

        FILTER_R1_CONE(r0_id2, x2_1, s_n2_1, gp12, kw12, 12);
        FILTER_R1_CONE(r0_id3, x3_1, s_n3_1, gp13, kw13, 13);
        FILTER_R1_CONE(r0_id4, x4_1, s_n4_1, gp14, kw14, 14);
        if (!same45) {
            FILTER_R1_CONE(r0_id5, x5_1, s_n5_1, gp15, kw15, 15);
        }
        __syncthreads();

        int n2_1 = s_n2_1, n3_1 = s_n3_1, n4_1 = s_n4_1, n5_1 = same45 ? s_n4_1 : s_n5_1;
        if (n2_1 > MAX_C1) n2_1 = MAX_C1;
        if (n3_1 > MAX_C1) n3_1 = MAX_C1;
        if (n4_1 > MAX_C1) n4_1 = MAX_C1;
        if (n5_1 > MAX_C1) n5_1 = MAX_C1;
        if (n2_1 == 0 || n3_1 == 0) continue;

        for (int idx2 = 0; idx2 < n2_1; ++idx2) {
            if (tid == 0) s_ni3 = 0;
            __syncthreads();

            uint64_t x2   = my_scratch->x2_1[idx2];
            uint64_t gx2  = get_gx(x2);
            uint64_t col_u1_012 = x0 | x1 | x2;
            uint64_t col_u2_012 = col_u2_01 | ((x0 | x1) & x2);
            uint64_t fb23 = col_u2_012 | (gp23 == 0 ? x2 : 0ULL) | (kw23 == 0 ? gx2 : 0ULL);

            for (int k = tid; k < n3_1; k += bdim) {
                uint64_t rx3 = my_scratch->x3_1[k];
                if ((rx3 & fb23) == 0ULL) {
                    if ((gp23 == 0 || popcnt64(x2 & rx3) == gp23) && (kw23 == 0 || popcnt64(gx2 & rx3) == kw23)) {
                        int pos = atomicAdd(&s_ni3, 1);
                        if (pos < 64) s_x3_q[pos] = rx3;
                        else if (pos < MAX_C1) my_scratch->x3_q_ext[pos] = rx3;
                    }
                }
            }
            __syncthreads();

            int ni3 = s_ni3;
            if (ni3 > MAX_C1) ni3 = MAX_C1;
            if (ni3 == 0) continue;
            if (tid == 0) my_d4 += (unsigned long long)ni3;
            if (n4_1 == 0 || n5_1 == 0) continue;

            uint64_t fb24 = col_u2_012 | (gp24 == 0 ? x2 : 0ULL) | (kw24 == 0 ? gx2 : 0ULL);
            uint64_t fb25 = col_u2_012 | (gp25 == 0 ? x2 : 0ULL) | (kw25 == 0 ? gx2 : 0ULL);
            if (tid == 0) { s_n4_r2 = 0; s_n5_r2 = 0; }
            __syncthreads();

            if (same45 || n4_1 <= n5_1) {
                for (int k = tid; k < n4_1; k += bdim) {
                    uint64_t rx = my_scratch->x4_1[k];
                    if ((rx & fb24) == 0ULL && (gp24 == 0 || popcnt64(x2 & rx) == gp24) && (kw24 == 0 || popcnt64(gx2 & rx) == kw24)) {
                        int pos = atomicAdd(&s_n4_r2, 1);
                        if (pos < 2048) my_scratch->x4_r2[pos] = rx;
                        else atomicExch(overflow_flag, 24);
                    }
                }
                __syncthreads();
                if (s_n4_r2 == 0) continue;
                if (!same45) {
                    for (int k = tid; k < n5_1; k += bdim) {
                        uint64_t rx = my_scratch->x5_1[k];
                        if ((rx & fb25) == 0ULL && (gp25 == 0 || popcnt64(x2 & rx) == gp25) && (kw25 == 0 || popcnt64(gx2 & rx) == kw25)) {
                            int pos = atomicAdd(&s_n5_r2, 1);
                            if (pos < 2048) my_scratch->x5_r2[pos] = rx;
                            else atomicExch(overflow_flag, 25);
                        }
                    }
                    __syncthreads();
                    if (s_n5_r2 == 0) continue;
                }
            } else {
                for (int k = tid; k < n5_1; k += bdim) {
                    uint64_t rx = my_scratch->x5_1[k];
                    if ((rx & fb25) == 0ULL && (gp25 == 0 || popcnt64(x2 & rx) == gp25) && (kw25 == 0 || popcnt64(gx2 & rx) == kw25)) {
                        int pos = atomicAdd(&s_n5_r2, 1);
                        if (pos < 2048) my_scratch->x5_r2[pos] = rx;
                        else atomicExch(overflow_flag, 25);
                    }
                }
                __syncthreads();
                if (s_n5_r2 == 0) continue;
                for (int k = tid; k < n4_1; k += bdim) {
                    uint64_t rx = my_scratch->x4_1[k];
                    if ((rx & fb24) == 0ULL && (gp24 == 0 || popcnt64(x2 & rx) == gp24) && (kw24 == 0 || popcnt64(gx2 & rx) == kw24)) {
                        int pos = atomicAdd(&s_n4_r2, 1);
                        if (pos < 2048) my_scratch->x4_r2[pos] = rx;
                        else atomicExch(overflow_flag, 24);
                    }
                }
                __syncthreads();
                if (s_n4_r2 == 0) continue;
            }
            int n4_r2 = (s_n4_r2 <= 2048) ? s_n4_r2 : 2048;
            int n5_r2 = same45 ? n4_r2 : ((s_n5_r2 <= 2048) ? s_n5_r2 : 2048);

            // Process q in chunks of 64 (99.9% of idx2 have ni3 <= 64, so 1 single iteration!)
            for (int q_base = 0; q_base < ni3; q_base += 64) {
                __syncthreads();
                int nq = (ni3 - q_base <= 64) ? (ni3 - q_base) : 64;
                if (q_base >= 64) {
                    for (int _q = tid; _q < nq; _q += bdim) {
                        s_x3_q[_q] = my_scratch->x3_q_ext[q_base + _q];
                    }
                }
                if (tid == 0) {
                    s_n4_2 = s_n5_2 = s_n_v345 = 0;
                    s_active_q_mask = s_active_q4_mask = 0ULL;
                    s_cu2_3_inter = s_x3_inter = s_gx3_inter = ~0ULL;
                    s_x3_union = s_gx3_union = 0ULL;
                    s_x4_2_inter = s_gx4_2_inter = ~0ULL;
                    s_x4_2_union = s_gx4_2_union = 0ULL;
                    s_cu2_5_inter = s_x4_inter = s_gx4_inter = s_x5_inter = s_gx5_inter = ~0ULL;
                    s_x4_union = s_gx4_union = s_x5_union = s_gx5_union = 0ULL;
                }
                for (int _q = tid; _q < 64; _q += bdim) {
                    s_cu2_q_inter[_q] = ~0ULL;
                }
                __syncthreads();

                for (int _q = tid; _q < nq; _q += bdim) {
                    uint64_t x3 = s_x3_q[_q];
                    uint64_t gx3 = get_gx(x3);
                    s_gx3_q[_q] = gx3;
                    atomicAnd(&s_cu2_3_inter, (unsigned long long)(col_u2_012 | (col_u1_012 & x3)));
                    atomicAnd(&s_x3_inter, (unsigned long long)x3);
                    atomicOr(&s_x3_union, (unsigned long long)x3);
                    atomicAnd(&s_gx3_inter, (unsigned long long)gx3);
                    atomicOr(&s_gx3_union, (unsigned long long)gx3);
                }
                __syncthreads();

                unsigned long long my_aq4 = 0ULL, my_x4i = ~0ULL, my_x4u = 0ULL, my_gx4i = ~0ULL, my_gx4u = 0ULL;
                for (int k = tid; k < n4_r2; k += bdim) {
                    uint64_t rx = my_scratch->x4_r2[k];
                    if ((rx & s_cu2_3_inter) != 0ULL) continue;
                    if (!match_sandwich(rx, s_x3_inter, s_x3_union, gp34)) continue;
                    uint64_t rgx = get_gx(rx);
                    if (!match_sandwich(rgx, s_x3_inter, s_x3_union, kw34)) continue;
                    uint64_t fb34 = (rx & col_u1_012) | (gp34 == 0 ? rx : 0ULL) | (kw34 == 0 ? rgx : 0ULL);
                    uint64_t m4 = 0ULL;
                    for (int q = 0; q < nq; ++q) {
                        uint64_t x3 = s_x3_q[q];
                        if ((x3 & fb34) == 0ULL && (gp34 == 0 || popcnt64(x3 & rx) == gp34) && (kw34 == 0 || popcnt64(x3 & rgx) == kw34)) {
                            m4 |= (1ULL << q);
                        }
                    }
                    if (m4 != 0ULL) {
                        int pos = atomicAdd(&s_n4_2, 1);
                        if (pos < 512) { s_x4_2[pos] = rx; s_m4[pos] = m4; }
                        else if (pos < 2048) { my_scratch->x4_2_ext[pos] = rx; my_scratch->m4_ext[pos] = m4; }
                        else atomicExch(overflow_flag, 24);
                        my_aq4 |= m4;
                        my_x4i &= rx; my_x4u |= rx;
                        my_gx4i &= rgx; my_gx4u |= rgx;
                    }
                }
                if (my_aq4 != 0ULL) {
                    atomicOr(&s_active_q4_mask, my_aq4);
                    atomicAnd(&s_x4_2_inter, my_x4i); atomicOr(&s_x4_2_union, my_x4u);
                    atomicAnd(&s_gx4_2_inter, my_gx4i); atomicOr(&s_gx4_2_union, my_gx4u);
                }
                for (int i = tid; i < nq * 8; i += bdim) {
                    (&s_q_u_mask[0][0])[i] = 0ULL;
                }
                for (int idx_c = tid; idx_c < 60 * 8; idx_c += bdim) {
                    (&s_col_i5_mask[0][0])[idx_c] = 0ULL;
                }
                __syncthreads();
                int n4_2 = (s_n4_2 <= 2048) ? s_n4_2 : 2048;
                if (n4_2 == 0) continue;

                uint64_t active_q4 = s_active_q4_mask;
                uint64_t fb_x4 = (gp45 == 0 ? s_x4_2_inter : 0ULL) | (kw45 == 0 ? s_gx4_2_inter : 0ULL);
                for (int k = tid; k < n5_r2; k += bdim) {
                    uint64_t rx = same45 ? my_scratch->x4_r2[k] : my_scratch->x5_r2[k];
                    if ((rx & (s_cu2_3_inter | fb_x4)) != 0ULL) continue;
                    if (!match_sandwich(rx, s_x3_inter, s_x3_union, gp35)) continue;
                    if (!match_sandwich(rx, s_x4_2_inter, s_x4_2_union, gp45)) continue;
                    if (!match_sandwich(rx, s_gx4_2_inter, s_gx4_2_union, kw45)) continue;
                    uint64_t rgx = get_gx(rx);
                    if (!match_sandwich(rgx, s_x3_inter, s_x3_union, kw35)) continue;
                    uint64_t fb35 = (rx & col_u1_012) | (gp35 == 0 ? rx : 0ULL) | (kw35 == 0 ? rgx : 0ULL);
                    uint64_t m5 = 0ULL;
                    uint64_t aq = active_q4;
                    while (aq != 0ULL) {
                        int q = __ffsll(aq) - 1;
                        aq &= (aq - 1ULL);
                        uint64_t x3 = s_x3_q[q];
                        if ((x3 & fb35) == 0ULL && (gp35 == 0 || popcnt64(x3 & rx) == gp35) && (kw35 == 0 || popcnt64(x3 & rgx) == kw35)) {
                            m5 |= (1ULL << q);
                        }
                    }
                    if (m5 != 0ULL) {
                        int pos = atomicAdd(&s_n5_2, 1);
                        if (pos < 512) { s_x5_2[pos] = rx; s_m5[pos] = m5; }
                        else if (pos < 2048) { my_scratch->x5_2_ext[pos] = rx; my_scratch->m5_ext[pos] = m5; }
                        else atomicExch(overflow_flag, 25);
                        if (pos < 512) {
                            int w = pos >> 6;
                            unsigned long long bit5 = 1ULL << (pos & 63);
                            uint64_t tm = m5;
                            while (tm != 0ULL) {
                                int qb = __ffsll(tm) - 1;
                                tm &= (tm - 1ULL);
                                atomicOr(&s_q_u_mask[qb][w], bit5);
                            }
                            uint64_t tr5 = rx;
                            while (tr5 != 0ULL) {
                                int c5 = __ffsll(tr5) - 1;
                                tr5 &= (tr5 - 1ULL);
                                atomicOr(&s_col_i5_mask[c5][w], bit5);
                            }
                        }
                    }
                }
                __syncthreads();
                int n5_2 = (s_n5_2 <= 2048) ? s_n5_2 : 2048;
                if (n5_2 == 0) continue;

                // Stage C: 64-lane Bitmask Join (s_q_u_mask) with ZERO integer divisions!
                unsigned long long my_q_mask = 0ULL;
                unsigned long long my_cu2_inter = ~0ULL, my_x4_inter = ~0ULL, my_gx4_inter = ~0ULL, my_x5_inter = ~0ULL, my_gx5_inter = ~0ULL;
                unsigned long long my_x4_union = 0ULL, my_gx4_union = 0ULL, my_x5_union = 0ULL, my_gx5_union = 0ULL;
                int n5_2_fast = (n5_2 <= 512) ? n5_2 : 512;
                int n_w5 = (n5_2_fast + 63) >> 6;
                for (int i4 = tid; i4 < n4_2; i4 += bdim) {
                    uint64_t m4_val = (i4 < 512) ? s_m4[i4] : my_scratch->m4_ext[i4];
                    uint64_t x4 = (i4 < 512) ? s_x4_2[i4] : my_scratch->x4_2_ext[i4];
                    uint64_t gx4 = get_gx(x4);
                    bool i4_added = false;

                    for (int w = 0; w <= n_w5; ++w) {
                        uint64_t mask5 = 0ULL;
                        if (w < n_w5) {
                            uint64_t tm4 = m4_val;
                            while (tm4 != 0ULL) {
                                int qb = __ffsll(tm4) - 1;
                                tm4 &= (tm4 - 1ULL);
                                mask5 |= s_q_u_mask[qb][w];
                            }
                            if (mask5 == 0ULL) continue;
                            // Step 1: 100% forbid occupied columns (x4 & col_u1_012), plus x4 if gp45==0, plus gx4 if kw45==0
                            uint64_t f4 = ((gp45 == 0) ? x4 : (x4 & col_u1_012)) | ((kw45 == 0) ? gx4 : 0ULL);
                            while (f4 != 0ULL) {
                                int c = __ffsll(f4) - 1;
                                f4 &= (f4 - 1ULL);
                                mask5 &= ~s_col_i5_mask[c][w];
                            }
                            if (mask5 == 0ULL) continue;
                            // Step 2: Monotone Threshold Ladder on hole cone H0_012 = x4 & ~col_u1_012 for gp45 in {1, 2}
                            if (gp45 == 1) {
                                uint64_t ge1 = 0ULL, ge2 = 0ULL;
                                uint64_t h4 = x4 & ~col_u1_012;
                                while (h4 != 0ULL) {
                                    int c = __ffsll(h4) - 1;
                                    h4 &= (h4 - 1ULL);
                                    uint64_t mc = s_col_i5_mask[c][w];
                                    ge2 |= (ge1 & mc);
                                    ge1 |= mc;
                                }
                                mask5 &= (ge1 & ~ge2);
                                if (mask5 == 0ULL) continue;
                            } else if (gp45 == 2) {
                                uint64_t ge1 = 0ULL, ge2 = 0ULL, ge3 = 0ULL;
                                uint64_t h4 = x4 & ~col_u1_012;
                                while (h4 != 0ULL) {
                                    int c = __ffsll(h4) - 1;
                                    h4 &= (h4 - 1ULL);
                                    uint64_t mc = s_col_i5_mask[c][w];
                                    ge3 |= (ge2 & mc);
                                    ge2 |= (ge1 & mc);
                                    ge1 |= mc;
                                }
                                mask5 &= (ge2 & ~ge3);
                                if (mask5 == 0ULL) continue;
                            }
                            // Step 3: Monotone Threshold Ladder on chiral/imaginary cone gx4 for kw45 in {1, 2}
                            if (kw45 == 1) {
                                uint64_t k1 = 0ULL, k2 = 0ULL;
                                uint64_t g4 = gx4;
                                while (g4 != 0ULL) {
                                    int c = __ffsll(g4) - 1;
                                    g4 &= (g4 - 1ULL);
                                    uint64_t mc = s_col_i5_mask[c][w];
                                    k2 |= (k1 & mc);
                                    k1 |= mc;
                                }
                                mask5 &= (k1 & ~k2);
                                if (mask5 == 0ULL) continue;
                            } else if (kw45 == 2) {
                                uint64_t k1 = 0ULL, k2 = 0ULL, k3 = 0ULL;
                                uint64_t g4 = gx4;
                                while (g4 != 0ULL) {
                                    int c = __ffsll(g4) - 1;
                                    g4 &= (g4 - 1ULL);
                                    uint64_t mc = s_col_i5_mask[c][w];
                                    k3 |= (k2 & mc);
                                    k2 |= (k1 & mc);
                                    k1 |= mc;
                                }
                                mask5 &= (k2 & ~k3);
                                if (mask5 == 0ULL) continue;
                            }
                        }
                        int i5_fallback = 512;
                        while (w < n_w5 ? (mask5 != 0ULL) : (i5_fallback < n5_2)) {
                            int i5;
                            if (w < n_w5) {
                                int b = __ffsll(mask5) - 1;
                                mask5 &= (mask5 - 1ULL);
                                i5 = (w << 6) + b;
                            } else {
                                i5 = i5_fallback++;
                            }
                            if (same45 && gp45 == 0 && i4 == i5) continue;
                            uint64_t m5_val = (i5 < 512) ? s_m5[i5] : my_scratch->m5_ext[i5];
                            uint64_t common_q = m4_val & m5_val;
                            if (common_q == 0ULL) continue;
                            uint64_t x5 = (i5 < 512) ? s_x5_2[i5] : my_scratch->x5_2_ext[i5];
                            if (w >= n_w5) {
                                if (gp45 == 0 ? ((x4 & x5) != 0ULL) : (popcnt64(x4 & x5) != gp45 || (col_u1_012 & x4 & x5) != 0ULL)) continue;
                                if (kw45 == 0 ? ((gx4 & x5) != 0ULL) : (popcnt64(gx4 & x5) != kw45)) continue;
                            }
                            uint64_t gx5 = get_gx(x5);

                            uint64_t col_u1_01245 = col_u1_012 | x4 | x5;
                            uint64_t col_u2_01245 = col_u2_012 | (col_u1_012 & (x4 | x5)) | (x4 & x5);
                            bool pair_added = false;
                            while (common_q != 0ULL) {
                                int q_bit = __ffsll(common_q) - 1;
                                common_q &= (common_q - 1ULL);
                                uint64_t x3 = s_x3_q[q_bit];
                                if (gp45 != 0 && (x3 & x4 & x5) != 0ULL) continue;
                                my_q_mask |= (1ULL << q_bit);
                                uint64_t cu2_5 = col_u2_01245 | (col_u1_01245 & x3);
                                my_cu2_inter &= cu2_5;
                                atomicAnd(&s_cu2_q_inter[q_bit], (unsigned long long)cu2_5);
                                my_x4_inter &= (x4 & ~cu2_5); my_x4_union |= (x4 & ~cu2_5);
                                my_gx4_inter &= (gx4 & ~cu2_5); my_gx4_union |= (gx4 & ~cu2_5);
                                my_x5_inter &= (x5 & ~cu2_5); my_x5_union |= (x5 & ~cu2_5);
                                my_gx5_inter &= (gx5 & ~cu2_5); my_gx5_union |= (gx5 & ~cu2_5);
                                pair_added = true;
                                uint32_t pk = ((uint32_t)q_bit << 22) | ((uint32_t)i4 << 11) | (uint32_t)i5;
                                int vpos = atomicAdd(&s_n_v345, 1);
                                if (vpos < 1024) {
                                    s_v345[vpos] = pk;
                                    s_col_u2_5[vpos] = cu2_5;
                                } else if (vpos < 4096) {
                                    my_scratch->v345_ext[vpos] = pk;
                                    my_scratch->col_u2_5_ext[vpos] = cu2_5;
                                } else {
                                    atomicExch(overflow_flag, 345);
                                }
                            }
                        }
                    }
                }
                if (my_q_mask != 0ULL) {
                    atomicOr(&s_active_q_mask, my_q_mask);
                    atomicAnd(&s_cu2_5_inter, my_cu2_inter);
                    atomicAnd(&s_x4_inter, my_x4_inter);
                    atomicAnd(&s_gx4_inter, my_gx4_inter);
                    atomicAnd(&s_x5_inter, my_x5_inter);
                    atomicAnd(&s_gx5_inter, my_gx5_inter);
                    atomicOr(&s_x4_union, my_x4_union);
                    atomicOr(&s_gx4_union, my_gx4_union);
                    atomicOr(&s_x5_union, my_x5_union);
                    atomicOr(&s_gx5_union, my_gx5_union);
                }
                __syncthreads();

                int n_v345 = s_n_v345;
                if (n_v345 == 0) continue;
                if (tid == 0) {
                    my_d6 += (unsigned long long)n_v345;
                }
                if (n_v345 > 4096) n_v345 = 4096;
                uint64_t active_q = s_active_q_mask;
                if (tid == 0) {
                    uint64_t tq = active_q, v3i = ~0ULL, v3u = 0ULL, vg3i = ~0ULL, vg3u = 0ULL;
                    while (tq != 0ULL) {
                        int qb = __ffsll(tq) - 1; tq &= (tq - 1ULL);
                        uint64_t cu2q = s_cu2_q_inter[qb];
                        uint64_t x3q = s_x3_q[qb] & ~cu2q;
                        uint64_t gx3q = s_gx3_q[qb] & ~cu2q;
                        v3i &= x3q; v3u |= x3q; vg3i &= gx3q; vg3u |= gx3q;
                    }
                    s_v3_inter = v3i; s_v3_union = v3u; s_vg3_inter = vg3i; s_vg3_union = vg3u;
                }
                __syncthreads();

                // Evaluate all r6_groups of the bundle on this surviving D6 set!
                for (int g6_idx = 0; g6_idx < num_r6; ++g6_idx) {
                    __syncthreads();
                    R6GroupSpec r6s = c_r6_specs[g6_idx];
                    int gp26 = r6s.gp[2], kw26 = r6s.kw[2];
                    int gp36 = r6s.gp[3], kw36 = r6s.kw[3];
                    int gp46 = r6s.gp[4], kw46 = r6s.kw[4];
                    int gp56 = r6s.gp[5], kw56 = r6s.kw[5];

                    bool same_d3 = false;
                    if (g6_idx > 0) {
                        R6GroupSpec prev6 = c_r6_specs[g6_idx - 1];
                        if (r6s.r0_id == prev6.r0_id && r6s.gp[1] == prev6.gp[1] && r6s.kw[1] == prev6.kw[1]
                            && gp26 == prev6.gp[2] && kw26 == prev6.kw[2] && gp36 == prev6.gp[3] && kw36 == prev6.kw[3]
                            && gp46 == prev6.gp[4] && kw46 == prev6.kw[4]
                            && gp56 == prev6.gp[5] && kw56 == prev6.kw[5]) {
                            same_d3 = true;
                        }
                    }

                    if (!same_d3) {
                        if (s_n6_1[g6_idx] < 0) {
                            int reuse_g6 = -1;
                            for (int pg = 0; pg < g6_idx; ++pg) {
                                R6GroupSpec pr = c_r6_specs[pg];
                                if (r6s.r0_id == pr.r0_id && r6s.gp[1] == pr.gp[1] && r6s.kw[1] == pr.kw[1] && s_n6_1[pg] >= 0) {
                                    reuse_g6 = pg;
                                    break;
                                }
                            }
                            if (reuse_g6 >= 0) {
                                int cnt_r = s_n6_1[reuse_g6];
                                const uint64_t* src_r = my_scratch->x6_1[reuse_g6];
                                uint64_t* dst6 = my_scratch->x6_1[g6_idx];
                                for (int k = tid; k < cnt_r; k += bdim) dst6[k] = src_r[k];
                                if (tid == 0) s_n6_1[g6_idx] = cnt_r;
                                __syncthreads();
                            } else {
                                if (tid == 0) s_tmp_cnt = 0;
                                __syncthreads();
                                const uint64_t* c0_ptr = g_c_r0 + ((size_t)r6s.r0_id * batch_n + b_idx) * MAX_C0;
                                int n0_cnt = g_n_r0[r6s.r0_id * batch_n + b_idx];
                                int gp16 = r6s.gp[1], kw16 = r6s.kw[1];
                                uint64_t fb16 = col_u2_01 | (gp16 == 0 ? x1 : 0ULL) | (kw16 == 0 ? gx1 : 0ULL);
                                uint64_t* dst6 = my_scratch->x6_1[g6_idx];
                                for (int k = tid; k < n0_cnt; k += bdim) {
                                    uint64_t rx = c0_ptr[k];
                                    if ((rx & fb16) == 0ULL) {
                                        if ((gp16 == 0 || popcnt64(x1 & rx) == gp16) && (kw16 == 0 || popcnt64(gx1 & rx) == kw16)) {
                                            int pos = atomicAdd(&s_tmp_cnt, 1);
                                            if (pos < MAX_C1_67) dst6[pos] = rx; else atomicExch(overflow_flag, 16);
                                        }
                                    }
                                }
                                __syncthreads();
                                if (tid == 0) s_n6_1[g6_idx] = (s_tmp_cnt <= MAX_C1_67) ? s_tmp_cnt : MAX_C1_67;
                                __syncthreads();
                            }
                        }
                        int n6_1 = s_n6_1[g6_idx];
                        if (n6_1 == 0) {
                            if (tid == 0) s_n6_2 = 0;
                            __syncthreads();
                            continue;
                        }

                        if (tid == 0) {
                            s_n6_2 = 0;
                        }
                        for (int i = tid; i < 64 * 8; i += bdim) {
                            (&s_q_u_mask[0][0])[i] = 0ULL;
                        }
                        __syncthreads();

                        uint64_t fb26 = s_cu2_5_inter
                            | (gp26 == 0 ? x2 : 0ULL) | (kw26 == 0 ? gx2 : 0ULL)
                            | (gp46 == 0 ? s_x4_inter : 0ULL) | (kw46 == 0 ? s_gx4_inter : 0ULL)
                            | (gp56 == 0 ? s_x5_inter : 0ULL) | (kw56 == 0 ? s_gx5_inter : 0ULL);
                        const uint64_t* src6 = my_scratch->x6_1[g6_idx];
                        for (int k = tid; k < n6_1; k += bdim) {
                            uint64_t rx = src6[k];
                            if ((rx & fb26) != 0ULL) continue;
                            if (!match_sandwich(rx, s_v3_inter, s_v3_union, gp36)) continue;
                            if (!match_sandwich(rx, s_x4_inter, s_x4_union, gp46)) continue;
                            if (!match_sandwich(rx, s_x5_inter, s_x5_union, gp56)) continue;
                            if ((gp26 == 0 || popcnt64(x2 & rx) == gp26) && (kw26 == 0 || popcnt64(gx2 & rx) == kw26)) {
                                if (!match_sandwich(rx, s_vg3_inter, s_vg3_union, kw36)) continue;
                                if (!match_sandwich(rx, s_gx4_inter, s_gx4_union, kw46)) continue;
                                if (!match_sandwich(rx, s_gx5_inter, s_gx5_union, kw56)) continue;
                                uint64_t m6 = 0ULL;
                                uint64_t aq = active_q;
                                while (aq != 0ULL) {
                                    int q_bit = __ffsll(aq) - 1;
                                    aq &= (aq - 1ULL);
                                    if ((rx & s_cu2_q_inter[q_bit]) != 0ULL) continue;
                                    uint64_t x3 = s_x3_q[q_bit];
                                    if (gp36 == 0 ? ((x3 & rx) == 0ULL) : (popcnt64(x3 & rx) == gp36)) {
                                        uint64_t gx3 = s_gx3_q[q_bit];
                                        if (kw36 == 0 ? ((gx3 & rx) == 0ULL) : (popcnt64(gx3 & rx) == kw36)) {
                                            m6 |= (1ULL << q_bit);
                                        }
                                    }
                                }
                                if (m6 != 0ULL) {
                                    int pos = atomicAdd(&s_n6_2, 1);
                                    if (pos < 1024) { s_x6_2[pos] = rx; s_m6[pos] = m6; }
                                    else if (pos < 2048) { my_scratch->x6_2_ext[pos] = rx; my_scratch->m6_ext[pos] = m6; }
                                    else atomicExch(overflow_flag, 26);
                                    if (pos < 512) {
                                        int w = pos >> 6;
                                        unsigned long long bit_u = 1ULL << (pos & 63);
                                        uint64_t tm = m6;
                                        while (tm != 0ULL) {
                                            int qb = __ffsll(tm) - 1;
                                            tm &= (tm - 1ULL);
                                            atomicOr(&s_q_u_mask[qb][w], bit_u);
                                        }
                                    }
                                }
                            }
                        }
                        __syncthreads();
                    }

                    int n6_2 = s_n6_2;
                    if (n6_2 > 2048) n6_2 = 2048;
                    if (n6_2 == 0) continue;

                    if (tid == 0) {
                        s_n_d7 = 0;
                        s_d7_q_mask = 0ULL;
                        s_d7_cu2_6_inter = s_d7_x4_inter = s_d7_gx4_inter = s_d7_x5_inter = s_d7_gx5_inter = s_d7_x6_inter = s_d7_gx6_inter = ~0ULL;
                        s_d7_x4_union = s_d7_gx4_union = s_d7_x5_union = s_d7_gx5_union = s_d7_x6_union = s_d7_gx6_union = 0ULL;
                    }
                    for (int _q = tid; _q < 64; _q += bdim) {
                        s_d7_cu2_q_inter[_q] = ~0ULL;
                        s_d7_x6_q_inter[_q]  = ~0ULL;
                        s_d7_gx6_q_inter[_q] = ~0ULL;
                    }
                    __syncthreads();

                    unsigned long long my_d7_q = 0ULL;
                    unsigned long long my_d7_cu2_6_inter = ~0ULL, my_d7_x4_inter = ~0ULL, my_d7_gx4_inter = ~0ULL, my_d7_x5_inter = ~0ULL, my_d7_gx5_inter = ~0ULL, my_d7_x6_inter = ~0ULL, my_d7_gx6_inter = ~0ULL;
                    unsigned long long my_d7_x4_union = 0ULL, my_d7_gx4_union = 0ULL, my_d7_x5_union = 0ULL, my_d7_gx5_union = 0ULL, my_d7_x6_union = 0ULL, my_d7_gx6_union = 0ULL;

                    int n6_2_fast = (n6_2 <= 512) ? n6_2 : 512;
                    int n_u6_words = (n6_2_fast + 63) >> 6;
                    for (int v_i = tid; v_i < n_v345; v_i += bdim) {
                        uint32_t pk = (v_i < 1024) ? s_v345[v_i] : my_scratch->v345_ext[v_i];
                        int q_bit = (int)(pk >> 22);
                        int i4 = (int)((pk >> 11) & 0x7FFU);
                        int i5 = (int)(pk & 0x7FFU);
                        uint64_t x3 = s_x3_q[q_bit];
                        uint64_t x4 = (i4 < 512) ? s_x4_2[i4] : my_scratch->x4_2_ext[i4];
                        uint64_t x5 = (i5 < 512) ? s_x5_2[i5] : my_scratch->x5_2_ext[i5];
                        uint64_t gx4 = get_gx(x4), gx5 = get_gx(x5);
                        uint64_t col_u1_5 = col_u1_012 | x3 | x4 | x5;
                        uint64_t col_u2_5 = (v_i < 1024) ? s_col_u2_5[v_i] : my_scratch->col_u2_5_ext[v_i];

                        for (int w = 0; w < n_u6_words; ++w) {
                            uint64_t umask = s_q_u_mask[q_bit][w];
                            while (umask != 0ULL) {
                                int b = __ffsll(umask) - 1;
                                umask &= (umask - 1ULL);
                                int u = (w << 6) + b;
                                uint64_t x6 = s_x6_2[u];
                                if ((x6 & col_u2_5) != 0ULL) continue;
                                if (gp46 == 0 ? ((x4 & x6) != 0ULL) : ((x4 & x6) == 0ULL || popcnt64(x4 & x6) != gp46)) continue;
                                if (gp56 == 0 ? ((x5 & x6) != 0ULL) : ((x5 & x6) == 0ULL || popcnt64(x5 & x6) != gp56)) continue;
                                if (kw46 == 0 ? ((gx4 & x6) != 0ULL) : ((gx4 & x6) == 0ULL || popcnt64(gx4 & x6) != kw46)) continue;
                                if (kw56 == 0 ? ((gx5 & x6) != 0ULL) : ((gx5 & x6) == 0ULL || popcnt64(gx5 & x6) != kw56)) continue;
                                uint64_t gx6 = get_gx(x6);

                                my_d7_q |= (1ULL << q_bit);
                                uint64_t cu2_6 = col_u2_5 | (col_u1_5 & x6);
                                my_d7_cu2_6_inter &= cu2_6;
                                my_d7_x4_inter &= (x4 & ~cu2_6); my_d7_x4_union |= (x4 & ~cu2_6);
                                my_d7_gx4_inter &= (gx4 & ~cu2_6); my_d7_gx4_union |= (gx4 & ~cu2_6);
                                my_d7_x5_inter &= (x5 & ~cu2_6); my_d7_x5_union |= (x5 & ~cu2_6);
                                my_d7_gx5_inter &= (gx5 & ~cu2_6); my_d7_gx5_union |= (gx5 & ~cu2_6);
                                my_d7_x6_inter &= (x6 & ~cu2_6); my_d7_x6_union |= (x6 & ~cu2_6);
                                my_d7_gx6_inter &= (gx6 & ~cu2_6); my_d7_gx6_union |= (gx6 & ~cu2_6);
                                atomicAnd(&s_d7_cu2_q_inter[q_bit], (unsigned long long)cu2_6);
                                atomicAnd(&s_d7_x6_q_inter[q_bit], (unsigned long long)x6);
                                atomicAnd(&s_d7_gx6_q_inter[q_bit], (unsigned long long)gx6);

                                int d7_pos = atomicAdd(&s_n_d7, 1);
                                if (d7_pos < 512) {
                                    s_d7[d7_pos] = ((uint32_t)v_i << 16) | (uint32_t)u;
                                } else if (d7_pos < 2048) {
                                    my_scratch->d7_ext[d7_pos] = ((uint32_t)v_i << 16) | (uint32_t)u;
                                } else {
                                    atomicExch(overflow_flag, 46);
                                }
                            }
                        }
                        for (int u = 512; u < n6_2; ++u) {
                            uint64_t m6_val = (u < 1024) ? s_m6[u] : my_scratch->m6_ext[u];
                            if (((m6_val >> q_bit) & 1ULL) == 0ULL) continue;
                            uint64_t x6 = (u < 1024) ? s_x6_2[u] : my_scratch->x6_2_ext[u];
                            if ((x6 & col_u2_5) != 0ULL) continue;
                            if (gp46 == 0 ? ((x4 & x6) != 0ULL) : ((x4 & x6) == 0ULL || popcnt64(x4 & x6) != gp46)) continue;
                            if (gp56 == 0 ? ((x5 & x6) != 0ULL) : ((x5 & x6) == 0ULL || popcnt64(x5 & x6) != gp56)) continue;
                            uint64_t gx6 = get_gx(x6);
                            if (kw46 == 0 ? ((x4 & gx6) != 0ULL) : ((x4 & gx6) == 0ULL || popcnt64(x4 & gx6) != kw46)) continue;
                            if (kw56 == 0 ? ((x5 & gx6) != 0ULL) : ((x5 & gx6) == 0ULL || popcnt64(x5 & gx6) != kw56)) continue;

                            my_d7_q |= (1ULL << q_bit);
                            uint64_t cu2_6 = col_u2_5 | (col_u1_5 & x6);
                            my_d7_cu2_6_inter &= cu2_6;
                            my_d7_x4_inter &= (x4 & ~cu2_6); my_d7_x4_union |= (x4 & ~cu2_6);
                            my_d7_gx4_inter &= (gx4 & ~cu2_6); my_d7_gx4_union |= (gx4 & ~cu2_6);
                            my_d7_x5_inter &= (x5 & ~cu2_6); my_d7_x5_union |= (x5 & ~cu2_6);
                            my_d7_gx5_inter &= (gx5 & ~cu2_6); my_d7_gx5_union |= (gx5 & ~cu2_6);
                            my_d7_x6_inter &= (x6 & ~cu2_6); my_d7_x6_union |= (x6 & ~cu2_6);
                            my_d7_gx6_inter &= (gx6 & ~cu2_6); my_d7_gx6_union |= (gx6 & ~cu2_6);
                            atomicAnd(&s_d7_cu2_q_inter[q_bit], (unsigned long long)cu2_6);
                            atomicAnd(&s_d7_x6_q_inter[q_bit], (unsigned long long)x6);
                            atomicAnd(&s_d7_gx6_q_inter[q_bit], (unsigned long long)gx6);

                            int d7_pos = atomicAdd(&s_n_d7, 1);
                            if (d7_pos < 512) {
                                s_d7[d7_pos] = ((uint32_t)v_i << 16) | (uint32_t)u;
                            } else if (d7_pos < 2048) {
                                my_scratch->d7_ext[d7_pos] = ((uint32_t)v_i << 16) | (uint32_t)u;
                            } else {
                                atomicExch(overflow_flag, 46);
                            }
                        }
                    }
                    if (my_d7_q != 0ULL) {
                        atomicOr(&s_d7_q_mask, my_d7_q);
                        atomicAnd(&s_d7_cu2_6_inter, my_d7_cu2_6_inter);
                        atomicAnd(&s_d7_x4_inter, my_d7_x4_inter); atomicOr(&s_d7_x4_union, my_d7_x4_union);
                        atomicAnd(&s_d7_gx4_inter, my_d7_gx4_inter); atomicOr(&s_d7_gx4_union, my_d7_gx4_union);
                        atomicAnd(&s_d7_x5_inter, my_d7_x5_inter); atomicOr(&s_d7_x5_union, my_d7_x5_union);
                        atomicAnd(&s_d7_gx5_inter, my_d7_gx5_inter); atomicOr(&s_d7_gx5_union, my_d7_gx5_union);
                        atomicAnd(&s_d7_x6_inter, my_d7_x6_inter); atomicOr(&s_d7_x6_union, my_d7_x6_union);
                        atomicAnd(&s_d7_gx6_inter, my_d7_gx6_inter); atomicOr(&s_d7_gx6_union, my_d7_gx6_union);
                    }
                    __syncthreads();

                    int n_d7 = s_n_d7;
                    if (n_d7 == 0) continue;
                    if (n_d7 > 2048) n_d7 = 2048;
                    uint64_t d7_q_mask = s_d7_q_mask;

                    // Only on the 1.2% of cases where n_d7 > 0, evaluate r7_groups!
                    for (int g7_idx = r6s.g7_start; g7_idx < r6s.g7_end; ++g7_idx) {
                        __syncthreads();
                        R7GroupSpec r7s = c_r7_specs[g7_idx];
                        if (s_n7_1[g7_idx] < 0) {
                            int reuse_g7 = -1;
                            for (int pg = 0; pg < g7_idx; ++pg) {
                                R7GroupSpec pr7 = c_r7_specs[pg];
                                if (r7s.r0_id == pr7.r0_id && r7s.gp[1] == pr7.gp[1] && r7s.kw[1] == pr7.kw[1] && s_n7_1[pg] >= 0) {
                                    reuse_g7 = pg;
                                    break;
                                }
                            }
                            if (reuse_g7 >= 0) {
                                int cnt_r = s_n7_1[reuse_g7];
                                const uint64_t* src_r = my_scratch->x7_1[reuse_g7];
                                uint64_t* dst7 = my_scratch->x7_1[g7_idx];
                                for (int k = tid; k < cnt_r; k += bdim) dst7[k] = src_r[k];
                                if (tid == 0) s_n7_1[g7_idx] = cnt_r;
                                __syncthreads();
                            } else {
                                if (tid == 0) s_tmp_cnt = 0;
                                __syncthreads();
                                const uint64_t* c0_ptr = g_c_r0 + ((size_t)r7s.r0_id * batch_n + b_idx) * MAX_C0;
                                int n0_cnt = g_n_r0[r7s.r0_id * batch_n + b_idx];
                                int gp17 = r7s.gp[1], kw17 = r7s.kw[1];
                                uint64_t fb17 = col_u2_01 | (gp17 == 0 ? x1 : 0ULL) | (kw17 == 0 ? gx1 : 0ULL);
                                uint64_t* dst7 = my_scratch->x7_1[g7_idx];
                                for (int k = tid; k < n0_cnt; k += bdim) {
                                    uint64_t rx = c0_ptr[k];
                                    if ((rx & fb17) == 0ULL) {
                                        if ((gp17 == 0 || popcnt64(x1 & rx) == gp17) && (kw17 == 0 || popcnt64(gx1 & rx) == kw17)) {
                                            int pos = atomicAdd(&s_tmp_cnt, 1);
                                            if (pos < MAX_C1_67) dst7[pos] = rx; else atomicExch(overflow_flag, 17);
                                        }
                                    }
                                }
                                __syncthreads();
                                if (tid == 0) s_n7_1[g7_idx] = (s_tmp_cnt <= MAX_C1_67) ? s_tmp_cnt : MAX_C1_67;
                                __syncthreads();
                            }
                        }
                        int n7_1 = s_n7_1[g7_idx];
                        if (n7_1 == 0) continue;

                        if (tid == 0) s_n7_2 = 0;
                        for (int i = tid; i < 64 * 8; i += bdim) {
                            (&s_q_u_mask[0][0])[i] = 0ULL;
                        }
                        __syncthreads();

                        int gp27 = r7s.gp[2], kw27 = r7s.kw[2];
                        int gp37 = r7s.gp[3], kw37 = r7s.kw[3];
                        int gp47 = r7s.gp[4], kw47 = r7s.kw[4];
                        int gp57 = r7s.gp[5], kw57 = r7s.kw[5];
                        int gp67 = r7s.gp[6], kw67 = r7s.kw[6];
                        int sum_gp36 = gp37 + gp47 + gp57 + gp67;
                        uint64_t fb27 = s_d7_cu2_6_inter
                            | (gp27 == 0 ? x2 : 0ULL) | (kw27 == 0 ? gx2 : 0ULL)
                            | (gp47 == 0 ? s_d7_x4_inter : 0ULL) | (kw47 == 0 ? s_d7_gx4_inter : 0ULL)
                            | (gp57 == 0 ? s_d7_x5_inter : 0ULL) | (kw57 == 0 ? s_d7_gx5_inter : 0ULL)
                            | (gp67 == 0 ? s_d7_x6_inter : 0ULL) | (kw67 == 0 ? s_d7_gx6_inter : 0ULL);
                        const uint64_t* src7 = my_scratch->x7_1[g7_idx];

                        // Theorems 22a + 23 + 27: Sandwich + Domino-Disjointness x7_2 + m7 compaction!
                        for (int k = tid; k < n7_1; k += bdim) {
                            uint64_t rx = src7[k];
                            if ((rx & fb27) != 0ULL) continue;
                            if (!match_sandwich(rx, s_d7_x4_inter, s_d7_x4_union, gp47)) continue;
                            if (!match_sandwich(rx, s_d7_x5_inter, s_d7_x5_union, gp57)) continue;
                            if (!match_sandwich(rx, s_d7_x6_inter, s_d7_x6_union, gp67)) continue;
                            if (!match_sandwich(rx, s_d7_gx4_inter, s_d7_gx4_union, kw47)) continue;
                            if (!match_sandwich(rx, s_d7_gx5_inter, s_d7_gx5_union, kw57)) continue;
                            if (!match_sandwich(rx, s_d7_gx6_inter, s_d7_gx6_union, kw67)) continue;
                            if ((gp27 == 0 || popcnt64(x2 & rx) == gp27) && (kw27 == 0 || popcnt64(gx2 & rx) == kw27)) {
                                uint64_t m7 = 0ULL;
                                uint64_t dq = d7_q_mask;
                                while (dq != 0ULL) {
                                    int q_bit = __ffsll(dq) - 1;
                                    dq &= (dq - 1ULL);
                                    uint64_t fb_q7 = s_d7_cu2_q_inter[q_bit]
                                        | (gp67 == 0 ? s_d7_x6_q_inter[q_bit] : 0ULL)
                                        | (kw67 == 0 ? s_d7_gx6_q_inter[q_bit] : 0ULL);
                                    if ((rx & fb_q7) != 0ULL) continue;
                                    uint64_t x3 = s_x3_q[q_bit];
                                    if (gp37 == 0 ? ((x3 & rx) == 0ULL) : (popcnt64(x3 & rx) == gp37)) {
                                        uint64_t gx3 = s_gx3_q[q_bit];
                                        if (kw37 == 0 ? ((gx3 & rx) == 0ULL) : (popcnt64(gx3 & rx) == kw37)) {
                                            m7 |= (1ULL << q_bit);
                                        }
                                    }
                                }
                                if (m7 != 0ULL) {
                                    int pos = atomicAdd(&s_n7_2, 1);
                                    if (pos < 2048) {
                                        my_scratch->x7_2_ext[pos] = rx;
                                        my_scratch->m7_ext[pos]   = m7;
                                    } else {
                                        atomicExch(overflow_flag, 27);
                                    }
                                    if (pos < 512) {
                                        int w = pos >> 6;
                                        unsigned long long bit_v = 1ULL << (pos & 63);
                                        uint64_t tm = m7;
                                        while (tm != 0ULL) {
                                            int qb = __ffsll(tm) - 1;
                                            tm &= (tm - 1ULL);
                                            atomicOr(&s_q_u_mask[qb][w], bit_v);
                                        }
                                    }
                                }
                            }
                        }
                        __syncthreads();

                        int n7_2 = s_n7_2;
                        if (n7_2 > 2048) n7_2 = 2048;
                        if (n7_2 == 0) continue;

                        uint64_t l_x8[128], l_x9[128], l_x10[128], l_x11[128];
                        int n7_2_fast = (n7_2 <= 512) ? n7_2 : 512;
                        int n_u7_words = (n7_2_fast + 63) >> 6;
                        for (int d7_i = tid; d7_i < n_d7; d7_i += bdim) {
                            uint32_t d7_pk = (d7_i < 512) ? s_d7[d7_i] : my_scratch->d7_ext[d7_i];
                            int v_i = (int)(d7_pk >> 16);
                            int u   = (int)(d7_pk & 0xFFFFU);
                            uint32_t pk = (v_i < 1024) ? s_v345[v_i] : my_scratch->v345_ext[v_i];
                            int q_bit = (int)(pk >> 22);
                            int i4 = (int)((pk >> 11) & 0x7FFU);
                            int i5 = (int)(pk & 0x7FFU);

                            uint64_t x3 = s_x3_q[q_bit], gx3 = s_gx3_q[q_bit];
                            uint64_t x4 = (i4 < 512) ? s_x4_2[i4] : my_scratch->x4_2_ext[i4];
                            uint64_t x5 = (i5 < 512) ? s_x5_2[i5] : my_scratch->x5_2_ext[i5];
                            uint64_t x6 = (u < 1024) ? s_x6_2[u] : my_scratch->x6_2_ext[u];

                            uint64_t col_u1_36 = x3 | x4 | x5 | x6;
                            uint64_t col_u1_5  = col_u1_012 | x3 | x4 | x5;
                            uint64_t col_u2_5  = (v_i < 1024) ? s_col_u2_5[v_i] : my_scratch->col_u2_5_ext[v_i];
                            uint64_t col_u2_6  = col_u2_5 | (col_u1_5 & x6);
                            uint64_t col_u1_6  = col_u1_5 | x6;
                            uint64_t gx4 = get_gx(x4), gx5 = get_gx(x5), gx6 = get_gx(x6);

                            // Theorem 35 Law II & III: Pre-x7 E_8 Cut + Mandatory req_x7 Mask + Boundary-Saturation Forbidden Mask!
                            uint64_t E_8 = MASK60 & ~col_u1_6;
                            uint64_t gx_arr[8] = {gx0, gx1, gx2, gx3, gx4, gx5, gx6, 0ULL};
                            uint64_t req_x7 = 0ULL;
                            uint64_t fb_d7 = col_u2_6
                                | (gp47 == 0 ? x4 : 0ULL) | (kw47 == 0 ? gx4 : 0ULL)
                                | (gp57 == 0 ? x5 : 0ULL) | (kw57 == 0 ? gx5 : 0ULL)
                                | (gp67 == 0 ? x6 : 0ULL) | (kw67 == 0 ? gx6 : 0ULL);
                            bool d7_ok = true;
                            for (int r = 0; r < 7; ++r) {
                                uint64_t e8_g = E_8 & gx_arr[r];
                                int cnt_e8 = popcnt64(e8_g);
                                if (cnt_e8 > (int)r7s.ub_e8[r]) { d7_ok = false; break; }
                                if (r7s.ub_h3[r] == 0) req_x7 |= e8_g;
                                if (cnt_e8 == (int)r7s.ub_e8[r]) fb_d7 |= (gx_arr[r] & col_u1_6);
                            }
                            if (!d7_ok || popcnt64(req_x7) > 4) continue;

                            for (int w = 0; w <= n_u7_words; ++w) {
                                uint64_t vmask = (w < n_u7_words) ? s_q_u_mask[q_bit][w] : 0ULL;
                                int v_fallback = 512;
                                while (w < n_u7_words ? (vmask != 0ULL) : (v_fallback < n7_2)) {
                                    int v;
                                    if (w < n_u7_words) {
                                        int b = __ffsll(vmask) - 1;
                                        vmask &= (vmask - 1ULL);
                                        v = (w << 6) + b;
                                    } else {
                                        v = v_fallback++;
                                        if (((my_scratch->m7_ext[v] >> q_bit) & 1ULL) == 0ULL) continue;
                                    }
                                    uint64_t x7 = my_scratch->x7_2_ext[v];
                                    if ((x7 & fb_d7) != 0ULL || (x7 & req_x7) != req_x7) continue;
                                    if (gp47 == 1 && gp57 == 1 && gp67 == 0) {
                                        if ((x4 & x7) == 0ULL || (x5 & x7) == 0ULL) continue;
                                        uint64_t m45 = (x4 | x5) & x7;
                                        uint64_t m45_1 = m45 & (m45 - 1ULL);
                                        if ((m45_1 & (m45_1 - 1ULL)) != 0ULL) continue;
                                    } else {
                                        if (popcnt64(x7 & col_u1_36) != sum_gp36) continue;
                                        if (popcnt64(x4 & x7) != gp47 || popcnt64(x5 & x7) != gp57 || popcnt64(x6 & x7) != gp67) continue;
                                    }
                                    if (popcnt64(gx4 & x7) != kw47 || popcnt64(gx5 & x7) != kw57 || popcnt64(gx6 & x7) != kw67) continue;

                                    uint64_t gx7 = get_gx(x7);
                                    gx_arr[7] = gx7;
                                    uint64_t col_u1_7 = col_u1_6 | x7;
                                    uint64_t E_dead0 = MASK60 & ~col_u1_7;

                                    // Theorem 35 Law II: Post-x7 H_3 Chiral Envelope Cut!
                                    int h3_cnt[8];
                                    bool h3_ok = true;
                                    for (int r = 0; r < 8; ++r) {
                                        int c_h3 = popcnt64(E_dead0 & gx_arr[r]);
                                        if (c_h3 > (int)r7s.ub_h3[r]) { h3_ok = false; break; }
                                        h3_cnt[r] = c_h3;
                                    }
                                    if (!h3_ok) continue;

                                    atomicAdd(&d_d8_per_g7[g7_idx], 1ULL);
                                    uint64_t col_u2_7 = col_u2_6 | (col_u1_6 & x7);
                                    uint64_t col_u1_17 = x1 | x2 | col_u1_36 | x7;
                                    uint64_t U1_4 = col_u1_7 & ~col_u2_7;

                                    int prev_r8_r0 = -1;
                                    uint64_t prev_r8_fb = 0ULL;
                                    int prev_n8_7 = -1;
                                    uint64_t prev_u8 = 0ULL, prev_inter8 = ~0ULL, prev_g_inter8 = ~0ULL;

                                    for (int m_idx = r7s.mem_start; m_idx < r7s.mem_end; ++m_idx) {
                                        MemberSpec ms = d_mem_specs[m_idx];
                                        // Theorem 35 O(1) Member Envelope Gate + Domino Boundary Saturation!
                                        bool mem_ok = true;
                                        uint64_t fb_s4 = 0ULL, fb_s5 = 0ULL, req_s4 = E_dead0;
                                        for (int r = 0; r < 8; ++r) {
                                            int hc = h3_cnt[r];
                                            if (hc > (int)ms.ub_h3[r]) { mem_ok = false; break; }
                                            int A_r = (int)ms.kw[0][r] + (int)ms.kw[1][r];
                                            int B_r = (int)ms.kw[2][r] + (int)ms.kw[3][r];
                                            if (hc == A_r) fb_s4 |= (gx_arr[r] & ~E_dead0);
                                            if (hc == B_r) {
                                                fb_s5 |= (gx_arr[r] & ~E_dead0);
                                                req_s4 |= (gx_arr[r] & U1_4);
                                            }
                                        }
                                        if (!mem_ok || (req_s4 & fb_s4) != 0ULL) continue;

                                        #define LAZY_MEM_R8_11_V6(ROW_OFFSET, LXA, NLCA, UA, INTERA, GINTERA, EXTRA_FB, REQ_MASK, CODE) \
                                        int NLCA = 0; \
                                        uint64_t UA = 0ULL, INTERA = ~0ULL, GINTERA = ~0ULL; \
                                        { \
                                            int r0_id_a = ms.r0_id[ROW_OFFSET]; \
                                            const uint64_t* c0a_ptr = g_c_r0 + ((size_t)r0_id_a * batch_n + b_idx) * MAX_C0; \
                                            int n0a_cnt = g_n_r0[r0_id_a * batch_n + b_idx]; \
                                            int gp1a = ms.gp[ROW_OFFSET][1], kw1a = ms.kw[ROW_OFFSET][1]; \
                                            int gp2a = ms.gp[ROW_OFFSET][2], kw2a = ms.kw[ROW_OFFSET][2]; \
                                            int gp3a = ms.gp[ROW_OFFSET][3], kw3a = ms.kw[ROW_OFFSET][3]; \
                                            int gp4a = ms.gp[ROW_OFFSET][4], kw4a = ms.kw[ROW_OFFSET][4]; \
                                            int gp5a = ms.gp[ROW_OFFSET][5], kw5a = ms.kw[ROW_OFFSET][5]; \
                                            int gp6a = ms.gp[ROW_OFFSET][6], kw6a = ms.kw[ROW_OFFSET][6]; \
                                            int gp7a = ms.gp[ROW_OFFSET][7], kw7a = ms.kw[ROW_OFFSET][7]; \
                                            int sum_gp17 = gp1a + gp2a + gp3a + gp4a + gp5a + gp6a + gp7a; \
                                            uint64_t fba = col_u2_7 | (EXTRA_FB) \
                                                | (gp1a == 0 ? x1 : 0ULL) | (kw1a == 0 ? gx1 : 0ULL) \
                                                | (gp2a == 0 ? x2 : 0ULL) | (kw2a == 0 ? gx2 : 0ULL) \
                                                | (gp3a == 0 ? x3 : 0ULL) | (kw3a == 0 ? gx3 : 0ULL) \
                                                | (gp4a == 0 ? x4 : 0ULL) | (kw4a == 0 ? gx4 : 0ULL) \
                                                | (gp5a == 0 ? x5 : 0ULL) | (kw5a == 0 ? gx5 : 0ULL) \
                                                | (gp6a == 0 ? x6 : 0ULL) | (kw6a == 0 ? gx6 : 0ULL) \
                                                | (gp7a == 0 ? x7 : 0ULL) | (kw7a == 0 ? gx7 : 0ULL); \
                                            if (sum_gp17 == 7) { \
                                                for (int k = 0; k < n0a_cnt; ++k) { \
                                                    uint64_t rx = c0a_ptr[k]; \
                                                    uint64_t mh = rx & E_dead0; \
                                                    if ((mh & (mh - 1ULL)) != 0ULL && (rx & fba) == 0ULL && (rx & (REQ_MASK)) == (REQ_MASK)) { \
                                                        if ((x1 & rx) && (x2 & rx) && (x3 & rx) && (x4 & rx) && (x5 & rx) && (x6 & rx) && (x7 & rx)) { \
                                                            if (popcnt64(gx1 & rx) == kw1a && popcnt64(gx2 & rx) == kw2a && popcnt64(gx3 & rx) == kw3a && popcnt64(gx4 & rx) == kw4a && popcnt64(gx5 & rx) == kw5a && popcnt64(gx6 & rx) == kw6a && popcnt64(gx7 & rx) == kw7a) { \
                                                                if (NLCA < 128) { LXA[NLCA++] = rx; UA |= rx; INTERA &= rx; GINTERA &= get_gx(rx); } else atomicExch(overflow_flag, (CODE)); \
                                                            } \
                                                        } \
                                                    } \
                                                } \
                                            } else { \
                                                for (int k = 0; k < n0a_cnt; ++k) { \
                                                    uint64_t rx = c0a_ptr[k]; \
                                                    if ((rx & fba) == 0ULL && (rx & (REQ_MASK)) == (REQ_MASK) && popcnt64(rx & col_u1_17) == sum_gp17) { \
                                                        if (popcnt64(x1 & rx) == gp1a && popcnt64(gx1 & rx) == kw1a && popcnt64(x2 & rx) == gp2a && popcnt64(gx2 & rx) == kw2a && popcnt64(x3 & rx) == gp3a && popcnt64(gx3 & rx) == kw3a) { \
                                                            if (popcnt64(x4 & rx) == gp4a && popcnt64(gx4 & rx) == kw4a && popcnt64(x5 & rx) == gp5a && popcnt64(gx5 & rx) == kw5a && popcnt64(x6 & rx) == gp6a && popcnt64(gx6 & rx) == kw6a && popcnt64(x7 & rx) == gp7a && popcnt64(gx7 & rx) == kw7a) { \
                                                                if (NLCA < 128) { LXA[NLCA++] = rx; UA |= rx; INTERA &= rx; GINTERA &= get_gx(rx); } else atomicExch(overflow_flag, (CODE)); \
                                                            } \
                                                        } \
                                                    } \
                                                } \
                                            } \
                                        }

                                        int gp89   = ms.gp[1][8],  kw89   = ms.kw[1][8];
                                        int gp1011 = ms.gp[3][10], kw1011 = ms.kw[3][10];
                                        bool same_r8 = false;
                                        if (m_idx > r7s.mem_start && ms.r0_id[0] == prev_r8_r0 && fb_s4 == prev_r8_fb) {
                                            MemberSpec pms = d_mem_specs[m_idx - 1];
                                            if (ms.kw[0][1] == pms.kw[0][1] && ms.kw[0][2] == pms.kw[0][2] && ms.kw[0][3] == pms.kw[0][3] &&
                                                ms.kw[0][4] == pms.kw[0][4] && ms.kw[0][5] == pms.kw[0][5] && ms.kw[0][6] == pms.kw[0][6] && ms.kw[0][7] == pms.kw[0][7]) {
                                                same_r8 = true;
                                            }
                                        }
                                        int n8_7; uint64_t u8, inter8, g_inter8;
                                        if (same_r8) {
                                            n8_7 = prev_n8_7; u8 = prev_u8; inter8 = prev_inter8; g_inter8 = prev_g_inter8;
                                        } else {
                                            LAZY_MEM_R8_11_V6(0, l_x8, n8_tmp, u8_tmp, inter8_tmp, g_inter8_tmp, fb_s4, 0ULL, 78);
                                            n8_7 = n8_tmp; u8 = u8_tmp; inter8 = inter8_tmp; g_inter8 = g_inter8_tmp;
                                            prev_r8_r0 = ms.r0_id[0]; prev_r8_fb = fb_s4;
                                            prev_n8_7 = n8_7; prev_u8 = u8; prev_inter8 = inter8; prev_g_inter8 = g_inter8;
                                        }
                                        if (n8_7 == 0) continue;
                                        // Theorem 35 Complementary Hole & Intersection Propagation into l_x9!
                                        uint64_t req_9 = req_s4 & ~u8;
                                        uint64_t fb_9  = fb_s4 | inter8 | (kw89 == 0 ? g_inter8 : 0ULL);
                                        LAZY_MEM_R8_11_V6(1, l_x9, n9_7, u9, inter9, g_inter9, fb_9, req_9, 79);
                                        if (n9_7 == 0) continue;
                                        if (((u8 | u9) & req_s4) != req_s4) continue;

                                        int gp810 = ms.gp[2][8],  kw810 = ms.kw[2][8];
                                        int gp910 = ms.gp[2][9],  kw910 = ms.kw[2][9];
                                        int gp811 = ms.gp[3][8],  kw811 = ms.kw[3][8];
                                        int gp911 = ms.gp[3][9],  kw911 = ms.kw[3][9];

                                        bool init_10_11 = false;
                                        int n10_7 = 0, n11_7 = 0;
                                        uint64_t u10 = 0ULL, u11 = 0ULL, u10_u11 = 0ULL;

                                        for (int idx8 = 0; idx8 < n8_7; ++idx8) {
                                            uint64_t x8 = l_x8[idx8], gx8 = get_gx(x8);
                                            uint64_t col_u2_8 = col_u2_7 | (col_u1_7 & x8);
                                            uint64_t col_u1_8 = col_u1_7 | x8;
                                            uint64_t req_9_for_8 = req_s4 & ~x8;
                                            uint64_t fb_9_for_8  = col_u2_8 | (gp89 == 0 ? x8 : 0ULL) | (kw89 == 0 ? gx8 : 0ULL);
                                            for (int idx9 = 0; idx9 < n9_7; ++idx9) {
                                                uint64_t x9 = l_x9[idx9];
                                                if ((x9 & fb_9_for_8) != 0ULL || (x9 & req_9_for_8) != req_9_for_8) continue;
                                                if ((gp89 != 0 && popcnt64(x8 & x9) != gp89) || (kw89 != 0 && popcnt64(gx8 & x9) != kw89)) continue;
                                                uint64_t gx9 = get_gx(x9);
                                                if (!init_10_11) {
                                                    init_10_11 = true;
                                                    LAZY_MEM_R8_11_V6(2, l_x10, n10_tmp, u10_tmp, inter10, g_inter10, fb_s5, 0ULL, 80);
                                                    n10_7 = n10_tmp; u10 = u10_tmp;
                                                    if (n10_7 > 0 && (((u8 | u9 | u10) & E_dead0) == E_dead0)) {
                                                        uint64_t req_11 = E_dead0 & ~u10;
                                                        uint64_t fb_11  = fb_s5 | inter10 | (kw1011 == 0 ? g_inter10 : 0ULL);
                                                        LAZY_MEM_R8_11_V6(3, l_x11, n11_tmp, u11_tmp, inter11, g_inter11, fb_11, req_11, 81);
                                                        n11_7 = n11_tmp; u11 = u11_tmp;
                                                        if (n11_7 > 0 && (((u10 | u11) & E_dead0) == E_dead0) && (((u8 | u9 | u10 | u11) | col_u2_7) == MASK60)) {
                                                            u10_u11 = u10 & u11;
                                                        } else {
                                                            n10_7 = 0;
                                                        }
                                                    } else {
                                                        n10_7 = 0;
                                                    }
                                                }
                                                if (n10_7 == 0) break;
                                                uint64_t col_u1_9 = col_u1_8 | x9;
                                                uint64_t col_u2_9 = col_u2_8 | (col_u1_8 & x9);
                                                // Theorem 35 Law I: S_5 = x10 | x11 = MASK60 & ~col_u2_9!
                                                uint64_t S_5 = MASK60 & ~col_u2_9;
                                                if ((S_5 & (u10 | u11)) != S_5) continue;
                                                for (int idx10 = 0; idx10 < n10_7; ++idx10) {
                                                    uint64_t x10 = l_x10[idx10];
                                                    if ((x10 & col_u2_9) != 0ULL) continue;
                                                    uint64_t req_x11 = S_5 ^ x10;
                                                    if ((req_x11 & u11) != req_x11) continue;
                                                    uint64_t gx10 = get_gx(x10);
                                                    if (popcnt64(x8 & x10) != gp810 || popcnt64(gx8 & x10) != kw810) continue;
                                                    if (popcnt64(x9 & x10) != gp910 || popcnt64(gx9 & x10) != kw910) continue;
                                                    for (int idx11 = 0; idx11 < n11_7; ++idx11) {
                                                        uint64_t x11 = l_x11[idx11];
                                                        if (x11 != req_x11) continue;
                                                        if (popcnt64(x8 & x11) != gp811 || popcnt64(gx8 & x11) != kw811) continue;
                                                        if (popcnt64(x9 & x11) != gp911 || popcnt64(gx9 & x11) != kw911) continue;
                                                        if (popcnt64(x10 & x11) != gp1011 || popcnt64(gx10 & x11) != kw1011) continue;
                                                        atomicAdd(&d_sol_per_mem[m_idx], 1ULL);
                                                        printf("SAT WITNESS FOUND IN MEMBER %d!\n", m_idx);
                                                    }
                                                }
                                            }
                                            if (init_10_11 && n10_7 == 0) break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        __syncthreads();
    }

    if (my_d4 > 0ULL) atomicAdd(d_d4_cnt, my_d4);
    if (my_d6 > 0ULL) atomicAdd(d_d6_cnt, my_d6);
}

#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA Error at line %d: %s\n", __LINE__, cudaGetErrorString(err)); \
        exit(1); \
    } \
} while(0)

extern "C" void gpu_compute_canons3(
    const uint64_t* h_L_a, int n_rows,
    const int32_t* h_perms, int n_perms,
    uint64_t* h_out_can
) {
    uint64_t *d_L_a = NULL, *d_out = NULL;
    int32_t *d_perms = NULL;
    CUDA_CHECK(cudaMalloc(&d_L_a, (size_t)n_rows * 3 * sizeof(uint64_t)));
    CUDA_CHECK(cudaMalloc(&d_perms, (size_t)n_perms * 60 * sizeof(int32_t)));
    CUDA_CHECK(cudaMalloc(&d_out, (size_t)n_rows * sizeof(uint64_t)));

    CUDA_CHECK(cudaMemcpy(d_L_a, h_L_a, (size_t)n_rows * 3 * sizeof(uint64_t), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_perms, h_perms, (size_t)n_perms * 60 * sizeof(int32_t), cudaMemcpyHostToDevice));

    int bsize = 256;
    int gsize = (n_rows + bsize - 1) / bsize;
    compute_canon3_kernel<<<gsize, bsize>>>(d_L_a, n_rows, d_perms, n_perms, d_out);
    CUDA_CHECK(cudaDeviceSynchronize());

    CUDA_CHECK(cudaMemcpy(h_out_can, d_out, (size_t)n_rows * sizeof(uint64_t), cudaMemcpyDeviceToHost));
    cudaFree(d_L_a);
    cudaFree(d_perms);
    cudaFree(d_out);
}

#define MAX_R0_SLOTS 16384
#define MAX_POOLS_PER_BUNDLE 256
#define MAX_CANS_PER_BUNDLE 16

struct SolverTrieCtx {
    uint64_t* d_pools[MAX_POOLS_PER_BUNDLE];
    int32_t   h_pool_lens[MAX_POOLS_PER_BUNDLE];
    int       num_pools;
    uint64_t** d_pool_ptrs_dev;
    int32_t*   d_pool_lens_dev;

    uint64_t* d_cans[MAX_CANS_PER_BUNDLE];
    int       num_cans;
    uint64_t** d_can_ptrs_dev;

    MemberSpec* d_mem_specs;

    uint64_t* g_c_r0;
    int32_t*  g_n_r0;
    int32_t*  h_n1;
    int2*     h_tasks;
    int2*     d_tasks;
    int       max_tasks;
    int*      d_task_counter;
    BlockScratchTrie* d_scratch;
    int32_t*  d_reps;
    uint64_t* d_rep_canons;
    unsigned long long *d_d4_cnt, *d_d6_cnt;
    unsigned long long *d_d8_per_g7, *d_sol_per_mem;
    int32_t*  d_overflow;
    int       num_blocks;
    int       block_threads;
    int       num_r0_specs;
    int       num_r6;
    int       num_r7;
    int       num_members;
    int       r0_id1;
};

extern "C" void* gpu_trie_init(int num_blocks, int block_threads) {
    SolverTrieCtx* ctx = new SolverTrieCtx();
    ctx->num_blocks = num_blocks;
    ctx->block_threads = block_threads;
    ctx->num_pools = 0;
    ctx->num_cans = 0;
    for (int i = 0; i < MAX_POOLS_PER_BUNDLE; ++i) ctx->d_pools[i] = NULL;
    for (int i = 0; i < MAX_CANS_PER_BUNDLE; ++i) ctx->d_cans[i] = NULL;

    CUDA_CHECK(cudaMalloc(&ctx->d_pool_ptrs_dev, MAX_POOLS_PER_BUNDLE * sizeof(uint64_t*)));
    CUDA_CHECK(cudaMalloc(&ctx->d_pool_lens_dev, MAX_POOLS_PER_BUNDLE * sizeof(int32_t)));
    CUDA_CHECK(cudaMalloc(&ctx->d_can_ptrs_dev,  MAX_CANS_PER_BUNDLE * sizeof(uint64_t*)));
    CUDA_CHECK(cudaMalloc(&ctx->d_mem_specs,     MAX_BUNDLE_MEMBERS * sizeof(MemberSpec)));

    CUDA_CHECK(cudaMalloc(&ctx->g_c_r0, (size_t)MAX_R0_SLOTS * MAX_C0 * sizeof(uint64_t)));
    CUDA_CHECK(cudaMalloc(&ctx->g_n_r0, (size_t)MAX_R0_SLOTS * sizeof(int32_t)));

    ctx->h_n1 = new int32_t[512];
    ctx->max_tasks = 512 * MAX_C0;
    ctx->h_tasks = new int2[ctx->max_tasks];
    CUDA_CHECK(cudaMalloc(&ctx->d_tasks, (size_t)ctx->max_tasks * sizeof(int2)));
    CUDA_CHECK(cudaMalloc(&ctx->d_task_counter, sizeof(int)));
    CUDA_CHECK(cudaMalloc(&ctx->d_scratch, (size_t)num_blocks * sizeof(BlockScratchTrie)));

    CUDA_CHECK(cudaMalloc(&ctx->d_reps, 512 * sizeof(int32_t)));
    CUDA_CHECK(cudaMalloc(&ctx->d_rep_canons, 512 * sizeof(uint64_t)));
    CUDA_CHECK(cudaMalloc(&ctx->d_d4_cnt, sizeof(unsigned long long)));
    CUDA_CHECK(cudaMalloc(&ctx->d_d6_cnt, sizeof(unsigned long long)));
    CUDA_CHECK(cudaMalloc(&ctx->d_d8_per_g7, MAX_R7_GROUPS * sizeof(unsigned long long)));
    CUDA_CHECK(cudaMalloc(&ctx->d_sol_per_mem, MAX_BUNDLE_MEMBERS * sizeof(unsigned long long)));
    CUDA_CHECK(cudaMalloc(&ctx->d_overflow, sizeof(int32_t)));
    return ctx;
}

extern "C" void gpu_trie_set_bundle(
    void* vctx,
    int num_pools, const uint64_t** h_pool_ptrs, const int32_t* h_pool_lens,
    int num_cans, const uint64_t** h_can_ptrs, const int32_t* h_can_lens,
    const int32_t* h_cone6_Gp, const int32_t* h_cone6_KW0, const int32_t* h_cone6_r0_id,
    int num_r0_specs, const void* h_r0_specs,
    int num_r6, const void* h_r6_specs,
    int num_r7, const void* h_r7_specs,
    int num_members, const void* h_mem_specs
) {
    SolverTrieCtx* ctx = (SolverTrieCtx*)vctx;
    for (int i = 0; i < ctx->num_pools; ++i) {
        if (ctx->d_pools[i]) { cudaFree(ctx->d_pools[i]); ctx->d_pools[i] = NULL; }
    }
    ctx->num_pools = num_pools;
    for (int i = 0; i < num_pools; ++i) {
        ctx->h_pool_lens[i] = h_pool_lens[i];
        CUDA_CHECK(cudaMalloc(&ctx->d_pools[i], (size_t)h_pool_lens[i] * 3 * sizeof(uint64_t)));
        CUDA_CHECK(cudaMemcpy(ctx->d_pools[i], h_pool_ptrs[i], (size_t)h_pool_lens[i] * 3 * sizeof(uint64_t), cudaMemcpyHostToDevice));
    }
    CUDA_CHECK(cudaMemcpy(ctx->d_pool_ptrs_dev, ctx->d_pools, num_pools * sizeof(uint64_t*), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(ctx->d_pool_lens_dev, ctx->h_pool_lens, num_pools * sizeof(int32_t), cudaMemcpyHostToDevice));

    for (int i = 0; i < ctx->num_cans; ++i) {
        if (ctx->d_cans[i]) { cudaFree(ctx->d_cans[i]); ctx->d_cans[i] = NULL; }
    }
    ctx->num_cans = num_cans;
    for (int i = 0; i < num_cans; ++i) {
        CUDA_CHECK(cudaMalloc(&ctx->d_cans[i], (size_t)h_can_lens[i] * sizeof(uint64_t)));
        CUDA_CHECK(cudaMemcpy(ctx->d_cans[i], h_can_ptrs[i], (size_t)h_can_lens[i] * sizeof(uint64_t), cudaMemcpyHostToDevice));
    }
    if (num_cans > 0) {
        CUDA_CHECK(cudaMemcpy(ctx->d_can_ptrs_dev, ctx->d_cans, num_cans * sizeof(uint64_t*), cudaMemcpyHostToDevice));
    }

    CUDA_CHECK(cudaMemcpyToSymbol(c_cone6_Gp, h_cone6_Gp, 36 * sizeof(int32_t)));
    CUDA_CHECK(cudaMemcpyToSymbol(c_cone6_KW0, h_cone6_KW0, 36 * sizeof(int32_t)));
    CUDA_CHECK(cudaMemcpyToSymbol(c_cone6_r0_id, h_cone6_r0_id, 6 * sizeof(int32_t)));
    CUDA_CHECK(cudaMemcpyToSymbol(c_r0_specs, h_r0_specs, num_r0_specs * sizeof(R0Spec)));
    CUDA_CHECK(cudaMemcpyToSymbol(c_r6_specs, h_r6_specs, num_r6 * sizeof(R6GroupSpec)));
    CUDA_CHECK(cudaMemcpyToSymbol(c_r7_specs, h_r7_specs, num_r7 * sizeof(R7GroupSpec)));
    CUDA_CHECK(cudaMemcpy(ctx->d_mem_specs, h_mem_specs, num_members * sizeof(MemberSpec), cudaMemcpyHostToDevice));

    ctx->num_r0_specs = num_r0_specs;
    ctx->num_r6 = num_r6;
    ctx->num_r7 = num_r7;
    ctx->num_members = num_members;
    ctx->r0_id1 = h_cone6_r0_id[1];
}

extern "C" int gpu_trie_solve_batch(
    void* vctx, int batch_n,
    const int32_t* h_reps, const uint64_t* h_rep_canons,
    uint64_t* out_d4_d6,
    uint64_t* out_d8_per_g7,
    uint64_t* out_sol_per_mem
) {
    SolverTrieCtx* ctx = (SolverTrieCtx*)vctx;
    CUDA_CHECK(cudaMemcpy(ctx->d_reps, h_reps, (size_t)batch_n * sizeof(int32_t), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(ctx->d_rep_canons, h_rep_canons, (size_t)batch_n * sizeof(uint64_t), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemset(ctx->d_d4_cnt, 0, sizeof(unsigned long long)));
    CUDA_CHECK(cudaMemset(ctx->d_d6_cnt, 0, sizeof(unsigned long long)));
    CUDA_CHECK(cudaMemset(ctx->d_d8_per_g7, 0, ctx->num_r7 * sizeof(unsigned long long)));
    CUDA_CHECK(cudaMemset(ctx->d_sol_per_mem, 0, ctx->num_members * sizeof(unsigned long long)));
    CUDA_CHECK(cudaMemset(ctx->d_overflow, 0, sizeof(int32_t)));

    dim3 grid1(batch_n, ctx->num_r0_specs);
    stage1_filter_r0_trie_kernel<<<grid1, 256>>>(
        batch_n, ctx->num_r0_specs,
        ctx->d_reps, ctx->d_rep_canons,
        ctx->d_pools[0],
        ctx->d_pool_ptrs_dev, ctx->d_pool_lens_dev,
        ctx->d_can_ptrs_dev,
        ctx->g_c_r0, ctx->g_n_r0,
        ctx->d_overflow
    );
    CUDA_CHECK(cudaDeviceSynchronize());

    CUDA_CHECK(cudaMemcpy(ctx->h_n1, ctx->g_n_r0 + ctx->r0_id1 * batch_n, (size_t)batch_n * sizeof(int32_t), cudaMemcpyDeviceToHost));
    int total_tasks = 0;
    for (int b = 0; b < batch_n; ++b) {
        int n1 = ctx->h_n1[b];
        for (int idx1 = 0; idx1 < n1; ++idx1) {
            ctx->h_tasks[total_tasks].x = b;
            ctx->h_tasks[total_tasks].y = idx1;
            total_tasks++;
        }
    }

    if (total_tasks > 0) {
        CUDA_CHECK(cudaMemcpy(ctx->d_tasks, ctx->h_tasks, (size_t)total_tasks * sizeof(int2), cudaMemcpyHostToDevice));
        CUDA_CHECK(cudaMemset(ctx->d_task_counter, 0, sizeof(int)));
        stage2_6_trie_kernel<<<ctx->num_blocks, ctx->block_threads>>>(
            batch_n, total_tasks,
            ctx->num_r6, ctx->num_r7, ctx->num_members,
            ctx->d_tasks, ctx->d_task_counter,
            ctx->d_reps, ctx->d_pools[0],
            ctx->g_c_r0, ctx->g_n_r0,
            ctx->d_mem_specs,
            ctx->d_scratch,
            ctx->d_d4_cnt, ctx->d_d6_cnt,
            ctx->d_d8_per_g7, ctx->d_sol_per_mem,
            ctx->d_overflow
        );
        CUDA_CHECK(cudaDeviceSynchronize());
    }

    int32_t h_ovf = 0;
    CUDA_CHECK(cudaMemcpy(&h_ovf, ctx->d_overflow, sizeof(int32_t), cudaMemcpyDeviceToHost));
    if (h_ovf != 0) {
        return (int)h_ovf;
    }

    unsigned long long h_d4 = 0, h_d6 = 0;
    CUDA_CHECK(cudaMemcpy(&h_d4, ctx->d_d4_cnt, sizeof(unsigned long long), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(&h_d6, ctx->d_d6_cnt, sizeof(unsigned long long), cudaMemcpyDeviceToHost));
    out_d4_d6[0] = (uint64_t)h_d4;
    out_d4_d6[1] = (uint64_t)h_d6;
    CUDA_CHECK(cudaMemcpy(out_d8_per_g7, ctx->d_d8_per_g7, ctx->num_r7 * sizeof(uint64_t), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(out_sol_per_mem, ctx->d_sol_per_mem, ctx->num_members * sizeof(uint64_t), cudaMemcpyDeviceToHost));
    return 0;
}
"""

class R0SpecC(ctypes.Structure):
    _fields_ = [
        ("pool_idx", ctypes.c_int32),
        ("can_idx",  ctypes.c_int32),
        ("gp0a",     ctypes.c_int32),
        ("kw0a",     ctypes.c_int32),
    ]

class R6GroupSpecC(ctypes.Structure):
    _fields_ = [
        ("r0_id",    ctypes.c_int32),
        ("gp",       ctypes.c_int32 * 6),
        ("kw",       ctypes.c_int32 * 6),
        ("g7_start", ctypes.c_int32),
        ("g7_end",   ctypes.c_int32),
    ]

class R7GroupSpecC(ctypes.Structure):
    _fields_ = [
        ("r0_id",     ctypes.c_int32),
        ("gp",        ctypes.c_int32 * 7),
        ("kw",        ctypes.c_int32 * 7),
        ("mem_start", ctypes.c_int32),
        ("mem_end",   ctypes.c_int32),
        ("ub_e8",     ctypes.c_int8 * 8),
        ("ub_h3",     ctypes.c_int8 * 8),
    ]

class MemberSpecC(ctypes.Structure):
    _fields_ = [
        ("r0_id", ctypes.c_int32 * 4),
        ("gp",    (ctypes.c_int8 * 12) * 4),
        ("kw",    (ctypes.c_int8 * 12) * 4),
        ("ub_h3", ctypes.c_int8 * 8),
    ]


def main():
    t0 = time.time()
    cu_path = "/tmp/class6_trie.cu"
    so_path = "/tmp/class6_trie.so"
    with open(cu_path, "w") as f:
        f.write(CUDA_SRC)
    subprocess.check_call([
        "nvcc", "-O3", "-arch=native", "--shared", "-Xcompiler", "-fPIC",
        cu_path, "-o", so_path
    ])
    print(f"Compiled Class 6 Multi-Orbit 4-Level Trie v2 CUDA kernel in {time.time() - t0:.2f}s!", flush=True)

    lib = ctypes.CDLL(so_path)
    lib.c_gen_6block_rows.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_int, ctypes.c_void_p, ctypes.c_int
    ]
    lib.c_gen_6block_rows.restype = ctypes.c_int
    lib.gpu_compute_canons3.argtypes = [
        ctypes.c_void_p, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_int,
        ctypes.c_void_p
    ]
    lib.gpu_trie_init.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.gpu_trie_init.restype = ctypes.c_void_p
    lib.gpu_trie_set_bundle.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_int, ctypes.c_void_p,
        ctypes.c_int, ctypes.c_void_p,
        ctypes.c_int, ctypes.c_void_p,
        ctypes.c_int, ctypes.c_void_p
    ]
    lib.gpu_trie_solve_batch.argtypes = [
        ctypes.c_void_p, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
    ]
    lib.gpu_trie_solve_batch.restype = ctypes.c_int

    F12 = np.zeros((12, 12), dtype=int)
    for b_idx in range(6):
        F12[2 * b_idx, 2 * b_idx + 1] = F12[2 * b_idx + 1, 2 * b_idx] = 1
    I12 = np.eye(12, dtype=int)
    J12 = np.ones((12, 12), dtype=int)

    def gen_matchings_12(verts):
        if not verts:
            yield ()
            return
        v0 = verts[0]
        rest = verts[1:]
        for idx, v1 in enumerate(rest):
            rem = rest[:idx] + rest[idx + 1:]
            for m in gen_matchings_12(rem):
                yield ((v0, v1),) + m

    matchings_12 = list(gen_matchings_12(list(range(12))))
    m_tuples = []
    for m in matchings_12:
        p = [0] * 12
        for u, v in m:
            p[u] = v
            p[v] = u
        m_tuples.append(tuple(p))
    m_to_id = {t: i for i, t in enumerate(m_tuples)}

    def cycle_part_12(p):
        vis = [False] * 6
        cycs = []
        for b_idx in range(6):
            if vis[b_idx]:
                continue
            cur = 2 * b_idx
            length = 0
            while not vis[cur // 2]:
                vis[cur // 2] = True
                length += 1
                nxt = p[cur]
                if nxt // 2 == cur // 2:
                    break
                cur = nxt ^ 1
            cycs.append(length)
        return tuple(sorted(cycs, reverse=True))

    reps_M0 = {}
    for p in m_tuples:
        part = cycle_part_12(p)
        if part not in reps_M0:
            reps_M0[part] = p

    b6_perms = []
    for perm in permutations(range(6)):
        for flips in product((0, 1), repeat=6):
            g_p = [0] * 12
            for b_old in range(6):
                b_new = perm[b_old]
                fl = flips[b_old]
                g_p[2 * b_old] = 2 * b_new + fl
                g_p[2 * b_old + 1] = 2 * b_new + (1 - fl)
            b6_perms.append(tuple(g_p))

    def get_block_comps(M, E):
        adj = F12 | M | E
        vis = set()
        comps = []
        for u in range(12):
            if u not in vis:
                comp = []
                q = [u]
                vis.add(u)
                while q:
                    cur = q.pop()
                    comp.append(cur)
                    for nxt in range(12):
                        if adj[cur, nxt] and nxt not in vis:
                            vis.add(nxt)
                            q.append(nxt)
                comps.append(sorted(comp))
        return comps

    orbits_6 = []
    for part, m0 in sorted(reps_M0.items()):
        stab = [g_p for g_p in b6_perms if all(g_p[m0[u]] == m0[g_p[u]] for u in range(12))]
        M0_mat = np.zeros((12, 12), dtype=int)
        for u, v in enumerate(m0):
            M0_mat[u, v] = 1
        seen_e0 = [False] * len(m_tuples)
        for idx_e, e0 in enumerate(m_tuples):
            if seen_e0[idx_e]:
                continue
            for g_p in stab:
                img = [0] * 12
                for u in range(12):
                    img[g_p[u]] = g_p[e0[u]]
                seen_e0[m_to_id[tuple(img)]] = True
            E0_mat = np.zeros((12, 12), dtype=int)
            for u, v in enumerate(e0):
                E0_mat[u, v] = 1
            KW0 = 2 * J12 - F12 - E0_mat - (M0_mat @ E0_mat) - (E0_mat @ M0_mat)
            if KW0.min() >= 0:
                k_t1 = sum(1 for b_idx in range(6) if m0[2 * b_idx] == 2 * b_idx + 1 and e0[2 * b_idx] == 2 * b_idx + 1)
                if k_t1 == 0:
                    comps = get_block_comps(M0_mat, E0_mat)
                    sig = "+".join(str(len(c)//2) for c in sorted(comps, key=lambda x: len(x), reverse=True))
                    if sig == "6":
                        Gp = 9 * I12 + J12 - M0_mat
                        orbits_6.append((M0_mat, E0_mat, Gp, KW0))

    trie_plan = json.loads(zlib.decompress(base64.b64decode(TRIE_B64)).decode("utf-8"))
    bundles = trie_plan["bundles"]
    print(f"Loaded {len(orbits_6)} Class 6 orbits and {len(bundles)} Trie v2 bundles.", flush=True)

    cols_60 = []
    col_idx = {}
    for b1 in range(6):
        for b2 in range(b1 + 1, 6):
            for s1 in (0, 1):
                for s2 in (0, 1):
                    j1 = 2 * b1 + s1
                    j2 = 2 * b2 + s2
                    c = len(cols_60)
                    cols_60.append((j1, j2))
                    col_idx[(j1, j2)] = c
                    col_idx[(j2, j1)] = c
    g_col = [col_idx[(j1 ^ 1, j2 ^ 1)] for (j1, j2) in cols_60]
    orbs_30 = [(c, g_col[c]) for c in range(60) if c < g_col[c]]

    arr_cols_u = np.ascontiguousarray([u for u, v in cols_60], dtype=np.int32)
    arr_cols_v = np.ascontiguousarray([v for u, v in cols_60], dtype=np.int32)
    arr_g_col  = np.ascontiguousarray(g_col, dtype=np.int32)
    arr_orbs_c = np.ascontiguousarray([c for c, gc in orbs_30], dtype=np.int32)
    arr_orbs_gc = np.ascontiguousarray([gc for c, gc in orbs_30], dtype=np.int32)

    row_cache = {}
    scratch_buf = np.empty((250000, 3), dtype=np.uint64)

    def gen_6block_rows_fast(target_deg_tuple, diag_kw):
        key = (target_deg_tuple, int(diag_kw))
        if key in row_cache:
            return row_cache[key]
        t_deg = np.ascontiguousarray(target_deg_tuple, dtype=np.int32)
        cnt = lib.c_gen_6block_rows(
            arr_cols_u.ctypes.data_as(ctypes.c_void_p),
            arr_cols_v.ctypes.data_as(ctypes.c_void_p),
            arr_g_col.ctypes.data_as(ctypes.c_void_p),
            arr_orbs_c.ctypes.data_as(ctypes.c_void_p),
            arr_orbs_gc.ctypes.data_as(ctypes.c_void_p),
            t_deg.ctypes.data_as(ctypes.c_void_p),
            int(diag_kw),
            scratch_buf.ctypes.data_as(ctypes.c_void_p),
            250000
        )
        assert cnt <= 250000, f"Row buffer overflow: {cnt}"
        res = np.ascontiguousarray(scratch_buf[:cnt].copy())
        row_cache[key] = res
        return res

    ctx = lib.gpu_trie_init(512, 128)

    b_start = int(os.environ.get("BUNDLE_START", "0"))
    b_end   = int(os.environ.get("BUNDLE_END", str(len(bundles))))
    b_list_env = os.environ.get("BUNDLE_LIST", "")
    max_batches = int(os.environ.get("MAX_BATCHES", "0"))
    if b_list_env:
        target_bundles = [int(x) for x in b_list_env.split(",") if x.strip()]
    else:
        target_bundles = list(range(b_start, b_end))

    print(f"Running Multi-Orbit 4-Level Trie v2 Class 6 on {len(target_bundles)} bundles...", flush=True)
    summary = []

    for b_pos, b_idx in enumerate(target_bundles):
        t_b = time.time()
        bundle = bundles[b_idx]
        all_members = []
        for g6 in bundle["r6_groups"]:
            for g7 in g6["r7_groups"]:
                for m in g7["members"]:
                    all_members.append(m)

        m0 = all_members[0]
        M_0, E_0, Gp_0, KW0_0 = orbits_6[m0["orbit_idx"]]
        gi0 = m0["g_inv"]
        ro0 = m0["row_order"]
        Mc0 = M_0[np.ix_(gi0, gi0)]
        Ec0 = E_0[np.ix_(gi0, gi0)]
        Gpc0 = Gp_0[np.ix_(gi0, gi0)] - 2 * I12
        KW0c0 = KW0_0[np.ix_(gi0, gi0)]
        Delta0c0 = 2 * J12 - I12 - F12 - Mc0 - (Ec0 @ F12)

        cone6_rows = ro0[:6]
        cone6_Gp = np.ascontiguousarray(Gpc0[np.ix_(cone6_rows, cone6_rows)], dtype=np.int32)
        cone6_KW0 = np.ascontiguousarray(KW0c0[np.ix_(cone6_rows, cone6_rows)], dtype=np.int32)

        pool_key_to_id = {}
        pool_list = []

        def get_pool_id(deg_tuple, kw_diag):
            k = (tuple(int(x) for x in deg_tuple), int(kw_diag))
            if k not in pool_key_to_id:
                pid = len(pool_list)
                pool_key_to_id[k] = pid
                pool_list.append(gen_6block_rows_fast(k[0], k[1]))
            return pool_key_to_id[k]

        cone_pool_ids = [
            get_pool_id(tuple(int(Delta0c0[r, j]) for j in range(12)), int(KW0c0[r, r]))
            for r in cone6_rows
        ]
        assert cone_pool_ids[0] == 0

        # Law M16: Decoupled 6-Cone automorphism group Aut_dec(C6*) from class6_trie_plan_v3.json!
        aut_dec = bundle["aut_dec"]

        stab_a_to_0 = [[] for _ in range(6)]
        seen_c_map = [set() for _ in range(6)]
        for pi_6, g_p in aut_dec:
            for a_idx in range(6):
                if pi_6[a_idx] == 0 and tuple(g_p) not in seen_c_map[a_idx]:
                    seen_c_map[a_idx].add(tuple(g_p))
                    c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                    stab_a_to_0[a_idx].append(np.array(c_map, dtype=np.int32))

        c_cans = []
        can_idx_for_cone = [-1] * 6
        for a_idx in range(6):
            L_a = pool_list[cone_pool_ids[a_idx]]
            n_rows = len(L_a)
            n_perms = len(stab_a_to_0[a_idx])
            if a_idx == 0:
                out_can = np.empty(n_rows, dtype=np.uint64)
                perms_arr = np.ascontiguousarray(np.array(stab_a_to_0[0], dtype=np.int32))
                lib.gpu_compute_canons3(
                    L_a.ctypes.data_as(ctypes.c_void_p), n_rows,
                    perms_arr.ctypes.data_as(ctypes.c_void_p), n_perms,
                    out_can.ctypes.data_as(ctypes.c_void_p)
                )
                c0_can = out_can
            else:
                if n_perms > 0:
                    out_can = np.empty(n_rows, dtype=np.uint64)
                    perms_arr = np.ascontiguousarray(np.array(stab_a_to_0[a_idx], dtype=np.int32))
                    lib.gpu_compute_canons3(
                        L_a.ctypes.data_as(ctypes.c_void_p), n_rows,
                        perms_arr.ctypes.data_as(ctypes.c_void_p), n_perms,
                        out_can.ctypes.data_as(ctypes.c_void_p)
                    )
                    can_idx_for_cone[a_idx] = len(c_cans)
                    c_cans.append(out_can)

        L0_pool = pool_list[0]
        reps = np.ascontiguousarray([i for i in range(len(L0_pool)) if L0_pool[i, 0] == c0_can[i]], dtype=np.int32)
        rep_canons = np.ascontiguousarray([c0_can[i] for i in reps], dtype=np.uint64)

        r0_spec_list = []
        r0_key_to_id = {}

        def get_r0_id(pool_idx, can_idx, gp0a, kw0a):
            k = (int(pool_idx), int(can_idx), int(gp0a), int(kw0a))
            if k not in r0_key_to_id:
                rid = len(r0_spec_list)
                r0_key_to_id[k] = rid
                r0_spec_list.append(R0SpecC(k[0], k[1], k[2], k[3]))
            return r0_key_to_id[k]

        cone6_r0_id = np.zeros(6, dtype=np.int32)
        for a_idx in range(1, 6):
            cone6_r0_id[a_idx] = get_r0_id(
                cone_pool_ids[a_idx], can_idx_for_cone[a_idx],
                int(cone6_Gp[0, a_idx]), int(cone6_KW0[0, a_idx])
            )

        r6_c_list = []
        r7_c_list = []
        mem_c_list = []
        mem_meta = []

        for g6 in bundle["r6_groups"]:
            pid6 = get_pool_id(g6["deg6"], g6["kw66"])
            gp6 = g6["gp_05_6"]
            kw6 = g6["kw_05_6"]
            r0_id6 = get_r0_id(pid6, -1, gp6[0], kw6[0])
            g7_start = len(r7_c_list)

            for g7 in g6["r7_groups"]:
                pid7 = get_pool_id(g7["deg7"], g7["kw77"])
                gp7 = g7["gp_06_7"]
                kw7 = g7["kw_06_7"]
                r0_id7 = get_r0_id(pid7, -1, gp7[0], kw7[0])
                mem_start = len(mem_c_list)

                mem_ub_e8_g7 = []
                mem_ub_h3_g7 = []
                for m in g7["members"]:
                    idx_o = m["orbit_idx"]
                    gi = m["g_inv"]
                    ro = m["row_order"]
                    Mm, Em, Gpm, KW0m = orbits_6[idx_o]
                    Mcm = Mm[np.ix_(gi, gi)]
                    Ecm = Em[np.ix_(gi, gi)]
                    Gp_ord = (Gpm[np.ix_(gi, gi)] - 2 * I12)[np.ix_(ro, ro)]
                    KW0_ord = KW0m[np.ix_(gi, gi)][np.ix_(ro, ro)]
                    Delta0_ord = (2 * J12 - I12 - F12 - Mcm - (Ecm @ F12))[ro, :]

                    ms = MemberSpecC()
                    for off in range(4):
                        a_idx = 8 + off
                        pid_a = get_pool_id(tuple(int(Delta0_ord[a_idx, j]) for j in range(12)), int(KW0_ord[a_idx, a_idx]))
                        ms.r0_id[off] = get_r0_id(pid_a, -1, int(Gp_ord[0, a_idx]), int(KW0_ord[0, a_idx]))
                        for j in range(12):
                            ms.gp[off][j] = int(Gp_ord[a_idx, j])
                            ms.kw[off][j] = int(KW0_ord[a_idx, j])
                    ub_h3 = [min(int(KW0_ord[r, 8] + KW0_ord[r, 9]), int(KW0_ord[r, 10] + KW0_ord[r, 11])) for r in range(8)]
                    ub_e8 = [int(KW0_ord[r, 7]) + ub_h3[r] for r in range(7)] + [0]
                    for r in range(8):
                        ms.ub_h3[r] = ub_h3[r]
                    mem_ub_e8_g7.append(ub_e8)
                    mem_ub_h3_g7.append(ub_h3)
                    mem_c_list.append(ms)
                    mem_meta.append((idx_o, len(r7_c_list)))

                mem_end = len(mem_c_list)
                r7_spec = R7GroupSpecC()
                r7_spec.r0_id = r0_id7
                for j in range(7):
                    r7_spec.gp[j] = int(gp7[j])
                    r7_spec.kw[j] = int(kw7[j])
                r7_spec.mem_start = mem_start
                r7_spec.mem_end = mem_end
                for r in range(8):
                    r7_spec.ub_e8[r] = max(u[r] for u in mem_ub_e8_g7)
                    r7_spec.ub_h3[r] = max(u[r] for u in mem_ub_h3_g7)
                r7_c_list.append(r7_spec)

            g7_end = len(r7_c_list)
            r6_spec = R6GroupSpecC()
            r6_spec.r0_id = r0_id6
            for j in range(6):
                r6_spec.gp[j] = int(gp6[j])
                r6_spec.kw[j] = int(kw6[j])
            r6_spec.g7_start = g7_start
            r6_spec.g7_end = g7_end
            r6_c_list.append(r6_spec)

        num_pools = len(pool_list)
        num_cans  = len(c_cans)
        num_r0    = len(r0_spec_list)
        num_r6    = len(r6_c_list)
        num_r7    = len(r7_c_list)
        num_mem   = len(mem_c_list)

        h_pool_ptrs = (ctypes.c_void_p * num_pools)(*[p.ctypes.data_as(ctypes.c_void_p) for p in pool_list])
        h_pool_lens = (ctypes.c_int32 * num_pools)(*[len(p) for p in pool_list])
        h_can_ptrs  = (ctypes.c_void_p * max(1, num_cans))(*([c.ctypes.data_as(ctypes.c_void_p) for c in c_cans] if num_cans > 0 else [0]))
        h_can_lens  = (ctypes.c_int32 * max(1, num_cans))(*([len(c) for c in c_cans] if num_cans > 0 else [0]))

        arr_r0  = (R0SpecC * num_r0)(*r0_spec_list)
        arr_r6  = (R6GroupSpecC * num_r6)(*r6_c_list)
        arr_r7  = (R7GroupSpecC * num_r7)(*r7_c_list)
        arr_mem = (MemberSpecC * num_mem)(*mem_c_list)

        lib.gpu_trie_set_bundle(
            ctx,
            num_pools, h_pool_ptrs, h_pool_lens,
            num_cans, h_can_ptrs, h_can_lens,
            cone6_Gp.ctypes.data_as(ctypes.c_void_p),
            cone6_KW0.ctypes.data_as(ctypes.c_void_p),
            cone6_r0_id.ctypes.data_as(ctypes.c_void_p),
            num_r0, ctypes.byref(arr_r0),
            num_r6, ctypes.byref(arr_r6),
            num_r7, ctypes.byref(arr_r7),
            num_mem, ctypes.byref(arr_mem)
        )

        batch_size = min(512, 16384 // num_r0)
        resume_map = trie_plan.get("resume_state", {})
        orig_b_id = str(bundle.get("bundle_idx", b_idx))
        res_info = resume_map.get(orig_b_id, {})
        start_rep = int(res_info.get("reps_done", 0))
        cum_d4 = int(res_info.get("d4", 0))
        cum_d6 = int(res_info.get("d6", 0))
        cum_d8_g7 = np.array(res_info.get("d8_g7", [0] * num_r7), dtype=np.uint64)
        cum_sol_mem = np.array(res_info.get("sol_mem", [0] * num_mem), dtype=np.uint64)
        el_prev = float(res_info.get("el", 0.0))

        limit_reps = len(reps) if max_batches <= 0 else min(len(reps), max_batches * batch_size)
        n_unique_orbits = bundle["num_orbits"]
        print(f"Bundle {b_idx} (id={orig_b_id}, {b_pos+1}/{len(target_bundles)}): orbits={n_unique_orbits} (coset_mem={num_mem}), r6={num_r6}, r7={num_r7}, r0_specs={num_r0}, pools={num_pools}, |H6|={len(aut_dec)}, reps={len(reps)} (start={start_rep}), batch_sz={batch_size}", flush=True)

        for start in range(start_rep, limit_reps, batch_size):
            end = min(start + batch_size, limit_reps)
            b_reps = np.ascontiguousarray(reps[start:end], dtype=np.int32)
            b_cans = np.ascontiguousarray(rep_canons[start:end], dtype=np.uint64)
            out_d4_d6 = np.zeros(2, dtype=np.uint64)
            out_d8    = np.zeros(num_r7, dtype=np.uint64)
            out_sol   = np.zeros(num_mem, dtype=np.uint64)
            ovf_code = lib.gpu_trie_solve_batch(
                ctx, len(b_reps),
                b_reps.ctypes.data_as(ctypes.c_void_p),
                b_cans.ctypes.data_as(ctypes.c_void_p),
                out_d4_d6.ctypes.data_as(ctypes.c_void_p),
                out_d8.ctypes.data_as(ctypes.c_void_p),
                out_sol.ctypes.data_as(ctypes.c_void_p)
            )
            if ovf_code != 0:
                print(f"OVERFLOW DETECTED in Bundle {b_idx} batch {(start // batch_size) + 1}: code {ovf_code}", flush=True)
                raise RuntimeError(f"OVERFLOW DETECTED: code {ovf_code}")
            cum_d4 += int(out_d4_d6[0])
            cum_d6 += int(out_d4_d6[1])
            cum_d8_g7 += out_d8
            cum_sol_mem += out_sol
            b_num = (start // batch_size) + 1
            tot_b = (limit_reps + batch_size - 1) // batch_size
            cur_el = el_prev + (time.time() - t_b)
            if b_num == 1 or b_num % 2 == 0 or end == limit_reps:
                print(f"  [Bundle {b_idx} batch {b_num}/{tot_b}] reps={end}/{limit_reps} el={cur_el:.1f}s d4={cum_d4} d6={cum_d6}", flush=True)
            if b_num % 2 == 0 and end < limit_reps:
                ckpt_obj = {
                    "bundle_id": orig_b_id,
                    "reps_done": int(end),
                    "reps": int(len(reps)),
                    "el": round(cur_el, 2),
                    "d4": cum_d4,
                    "d6": cum_d6,
                    "d8_g7": [int(x) for x in cum_d8_g7],
                    "sol_mem": [int(x) for x in cum_sol_mem],
                }
                print("JSON_BATCH_CKPT:" + json.dumps(ckpt_obj), flush=True)

        el = el_prev + (time.time() - t_b)
        orbit_d8 = {}
        orbit_sol = {}
        for m_i, (idx_o, g7_i) in enumerate(mem_meta):
            orbit_d8[idx_o] = orbit_d8.get(idx_o, 0) + int(cum_d8_g7[g7_i])
            orbit_sol[idx_o] = orbit_sol.get(idx_o, 0) + int(cum_sol_mem[m_i])

        total_d8_b = sum(orbit_d8.values())
        total_sol_b = sum(orbit_sol.values())
        print(f"[Bundle {b_idx}] Certified {n_unique_orbits} orbits in {el:.2f}s ({el/n_unique_orbits:.2f}s/orbit)! d4={cum_d4}, d6={cum_d6}, sum_d8={total_d8_b}, sols={total_sol_b}", flush=True)

        b_cert = []
        for idx_o in sorted(orbit_d8.keys()):
            rec = {
                "orbit_idx": idx_o,
                "bundle_idx": b_idx,
                "reps": int(len(reps)),
                "d4": cum_d4,
                "d6": cum_d6,
                "d8": orbit_d8[idx_o],
                "sols": orbit_sol[idx_o],
                "bundle_elapsed_s": round(el, 3)
            }
            summary.append(rec)
            b_cert.append(rec)
        print("JSON_BUNDLE_CERT:" + json.dumps(b_cert), flush=True)

    print(f"JSON_TRIE_SUMMARY:" + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
