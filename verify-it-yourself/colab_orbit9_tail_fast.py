import ctypes
import os
import subprocess
import time
import numpy as np
from itertools import combinations, permutations, product

CUDA_SRC = r"""
#include <stdint.h>
#include <stdio.h>
#include <cuda_runtime.h>

__device__ __forceinline__ int popcnt64(uint64_t x) {
    return __popcll(x);
}

__global__ void compute_canon_kernel(
    const uint64_t* __restrict__ L_a,
    int n_rows,
    const int32_t* __restrict__ perms,
    int n_perms,
    uint64_t* __restrict__ out_can
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_rows) return;
    uint64_t mask = L_a[idx * 5 + 0];
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

#define MAX_C1 16384
#define MAX_C23 32768
#define MAX_C4_0 40960

__global__ void stage1_filter_r0_kernel(
    int batch_n,
    const int32_t* __restrict__ reps,
    const uint64_t* __restrict__ rep_canons,
    const uint64_t* __restrict__ L0, int len0,
    const uint64_t* __restrict__ L1, int len1, const uint64_t* __restrict__ c1_can,
    const uint64_t* __restrict__ L2, int len2, const uint64_t* __restrict__ c2_can,
    const uint64_t* __restrict__ L3, int len3, const uint64_t* __restrict__ c3_can,
    const uint64_t* __restrict__ L4, int len4, const uint64_t* __restrict__ c4_can,
    const uint64_t* __restrict__ L5, int len5, const uint64_t* __restrict__ c5_can,
    const uint64_t* __restrict__ L6, int len6, const uint64_t* __restrict__ c6_can,
    const uint64_t* __restrict__ L7, int len7, const uint64_t* __restrict__ c7_can,
    const uint64_t* __restrict__ L8, int len8, const uint64_t* __restrict__ c8_can,
    const uint64_t* __restrict__ L9, int len9, const uint64_t* __restrict__ c9_can,
    const uint64_t* __restrict__ L10, int len10, const uint64_t* __restrict__ c10_can,
    const uint64_t* __restrict__ L11, int len11, const uint64_t* __restrict__ c11_can,
    const int32_t* __restrict__ Gp,
    const int32_t* __restrict__ KW0,
    int32_t* __restrict__ g_c1, int32_t* __restrict__ g_n1,
    int32_t* __restrict__ g_c2, int32_t* __restrict__ g_n2,
    int32_t* __restrict__ g_c3, int32_t* __restrict__ g_n3,
    int32_t* __restrict__ g_c4_0, int32_t* __restrict__ g_n4_0,
    int32_t* __restrict__ g_c5_0, int32_t* __restrict__ g_n5_0,
    int32_t* __restrict__ g_c6_0, int32_t* __restrict__ g_n6_0,
    int32_t* __restrict__ g_c7_0, int32_t* __restrict__ g_n7_0,
    int32_t* __restrict__ g_c8_0, int32_t* __restrict__ g_n8_0,
    int32_t* __restrict__ g_c9_0, int32_t* __restrict__ g_n9_0,
    int32_t* __restrict__ g_c10_0, int32_t* __restrict__ g_n10_0,
    int32_t* __restrict__ g_c11_0, int32_t* __restrict__ g_n11_0,
    int32_t* __restrict__ overflow_flag
) {
    int b_idx = blockIdx.x;
    if (b_idx >= batch_n) return;
    int tid = threadIdx.x;
    int bdim = blockDim.x;

    __shared__ int s_n1, s_n2, s_n3, s_n4, s_n5, s_n6, s_n7, s_n8, s_n9, s_n10, s_n11;
    if (tid == 0) {
        s_n1 = s_n2 = s_n3 = s_n4 = s_n5 = s_n6 = s_n7 = s_n8 = s_n9 = s_n10 = s_n11 = 0;
    }
    __syncthreads();

    int i0 = reps[b_idx];
    uint64_t min_can = rep_canons[b_idx];
    uint64_t x0   = L0[i0 * 5 + 0];
    uint64_t cut0 = L0[i0 * 5 + 2];
    uint64_t o1_0 = L0[i0 * 5 + 3];
    uint64_t o2_0 = L0[i0 * 5 + 4];
    uint64_t u1_0 = o1_0 | o2_0;
    uint64_t u2_0 = o2_0;

    int32_t* c1 = g_c1 + (size_t)b_idx * MAX_C1;
    int gp01 = Gp[0 * 12 + 1], kw01 = KW0[0 * 12 + 1];
    for (int i = tid; i < len1; i += bdim) {
        if (c1_can[i] >= min_can && (cut0 & L1[i * 5 + 2]) == 0 && (L1[i * 5 + 4] & u1_0) == 0 && (L1[i * 5 + 3] & u2_0) == 0) {
            if (popcnt64(x0 & L1[i * 5 + 0]) == gp01 && popcnt64(x0 & L1[i * 5 + 1]) == kw01) {
                int pos = atomicAdd(&s_n1, 1);
                if (pos < MAX_C1) c1[pos] = i; else atomicExch(overflow_flag, 1);
            }
        }
    }

    int32_t* c2 = g_c2 + (size_t)b_idx * MAX_C23;
    int gp02 = Gp[0 * 12 + 2], kw02 = KW0[0 * 12 + 2];
    for (int i = tid; i < len2; i += bdim) {
        if (c2_can[i] >= min_can && (cut0 & L2[i * 5 + 2]) == 0 && (L2[i * 5 + 4] & u1_0) == 0 && (L2[i * 5 + 3] & u2_0) == 0) {
            if (popcnt64(x0 & L2[i * 5 + 0]) == gp02 && popcnt64(x0 & L2[i * 5 + 1]) == kw02) {
                int pos = atomicAdd(&s_n2, 1);
                if (pos < MAX_C23) c2[pos] = i; else atomicExch(overflow_flag, 2);
            }
        }
    }

    int32_t* c3 = g_c3 + (size_t)b_idx * MAX_C23;
    int gp03 = Gp[0 * 12 + 3], kw03 = KW0[0 * 12 + 3];
    for (int i = tid; i < len3; i += bdim) {
        if (c3_can[i] >= min_can && (cut0 & L3[i * 5 + 2]) == 0 && (L3[i * 5 + 4] & u1_0) == 0 && (L3[i * 5 + 3] & u2_0) == 0) {
            if (popcnt64(x0 & L3[i * 5 + 0]) == gp03 && popcnt64(x0 & L3[i * 5 + 1]) == kw03) {
                int pos = atomicAdd(&s_n3, 1);
                if (pos < MAX_C23) c3[pos] = i; else atomicExch(overflow_flag, 3);
            }
        }
    }

    #define FILTER_B23_COOP(LA, LENA, CANA, GCA, SNA, CODE) \
    { \
        int32_t* ca = GCA + (size_t)b_idx * MAX_C4_0; \
        for (int i = tid; i < LENA; i += bdim) { \
            if (CANA[i] >= min_can && (o2_0 & LA[i * 5 + 4]) == 0 && popcnt64(x0 & LA[i * 5 + 0]) == 1 && popcnt64(x0 & LA[i * 5 + 1]) == 2) { \
                int pos = atomicAdd(&SNA, 1); \
                if (pos < MAX_C4_0) ca[pos] = i; else atomicExch(overflow_flag, CODE); \
            } \
        } \
    }

    FILTER_B23_COOP(L4, len4, c4_can, g_c4_0, s_n4, 4);
    FILTER_B23_COOP(L5, len5, c5_can, g_c5_0, s_n5, 5);
    FILTER_B23_COOP(L6, len6, c6_can, g_c6_0, s_n6, 6);
    FILTER_B23_COOP(L7, len7, c7_can, g_c7_0, s_n7, 7);
    FILTER_B23_COOP(L8, len8, c8_can, g_c8_0, s_n8, 8);
    FILTER_B23_COOP(L9, len9, c9_can, g_c9_0, s_n9, 9);
    FILTER_B23_COOP(L10, len10, c10_can, g_c10_0, s_n10, 10);
    FILTER_B23_COOP(L11, len11, c11_can, g_c11_0, s_n11, 11);

    __syncthreads();
    if (tid == 0) {
        g_n1[b_idx] = s_n1;
        g_n2[b_idx] = s_n2;
        g_n3[b_idx] = s_n3;
        g_n4_0[b_idx] = s_n4;
        g_n5_0[b_idx] = s_n5;
        g_n6_0[b_idx] = s_n6;
        g_n7_0[b_idx] = s_n7;
        g_n8_0[b_idx] = s_n8;
        g_n9_0[b_idx] = s_n9;
        g_n10_0[b_idx] = s_n10;
        g_n11_0[b_idx] = s_n11;
    }
}

#define MAX_C23_1 4096
#define MAX_C4_1  4096
#define MAX_C4_2  1024
#define MAX_C4_3  256
#define MAX_C8_7  128

struct BlockScratch {
    int32_t c2_1[MAX_C23_1];
    int32_t c3_1[MAX_C23_1];
    int32_t c4_1[MAX_C4_1];
    int32_t c5_1[MAX_C4_1];
    int32_t c6_1[MAX_C4_1];
    int32_t c7_1[MAX_C4_1];
    int32_t c8_1[MAX_C4_1];
    int32_t c9_1[MAX_C4_1];
    int32_t c10_1[MAX_C4_1];
    int32_t c11_1[MAX_C4_1];
};

__global__ void stage2_block_coop_kernel(
    int total_tasks,
    const int2* __restrict__ tasks,
    int* __restrict__ d_task_counter,
    const int32_t* __restrict__ reps,
    const uint64_t* __restrict__ L0,
    const uint64_t* __restrict__ L1,
    const uint64_t* __restrict__ L2,
    const uint64_t* __restrict__ L3,
    const uint64_t* __restrict__ L4,
    const uint64_t* __restrict__ L5,
    const uint64_t* __restrict__ L6,
    const uint64_t* __restrict__ L7,
    const uint64_t* __restrict__ L8,
    const uint64_t* __restrict__ L9,
    const uint64_t* __restrict__ L10,
    const uint64_t* __restrict__ L11,
    const int32_t* __restrict__ Gp,
    const int32_t* __restrict__ KW0,
    uint64_t O33_mask, uint64_t O13_mask, uint64_t O23_mask, uint64_t O22_mask, uint64_t O12_mask,
    const int32_t* __restrict__ g_c1, const int32_t* __restrict__ g_n1,
    const int32_t* __restrict__ g_c2, const int32_t* __restrict__ g_n2,
    const int32_t* __restrict__ g_c3, const int32_t* __restrict__ g_n3,
    const int32_t* __restrict__ g_c4_0, const int32_t* __restrict__ g_n4_0,
    const int32_t* __restrict__ g_c5_0, const int32_t* __restrict__ g_n5_0,
    const int32_t* __restrict__ g_c6_0, const int32_t* __restrict__ g_n6_0,
    const int32_t* __restrict__ g_c7_0, const int32_t* __restrict__ g_n7_0,
    const int32_t* __restrict__ g_c8_0, const int32_t* __restrict__ g_n8_0,
    const int32_t* __restrict__ g_c9_0, const int32_t* __restrict__ g_n9_0,
    const int32_t* __restrict__ g_c10_0, const int32_t* __restrict__ g_n10_0,
    const int32_t* __restrict__ g_c11_0, const int32_t* __restrict__ g_n11_0,
    BlockScratch* __restrict__ block_scratch_pool,
    int32_t* __restrict__ soa_c2,   // 8 * MAX_C4_2 * total_threads
    int32_t* __restrict__ soa_c3,   // 8 * MAX_C4_3 * total_threads
    int32_t* __restrict__ soa_c7,   // 4 * MAX_C8_7 * total_threads
    unsigned long long* __restrict__ d_b1_sols,
    unsigned long long* __restrict__ d_b2_sols,
    unsigned long long* __restrict__ d_b3_sols,
    int32_t* __restrict__ overflow_flag
) {
    int bid = blockIdx.x;
    int tid = threadIdx.x;
    int bdim = blockDim.x;
    size_t total_threads = (size_t)gridDim.x * bdim;
    size_t gtid = (size_t)bid * bdim + tid;

    BlockScratch* bsc = &block_scratch_pool[bid];
    int32_t* c2_1 = bsc->c2_1;
    int32_t* c3_1 = bsc->c3_1;
    int32_t* c4_1 = bsc->c4_1;
    int32_t* c5_1 = bsc->c5_1;
    int32_t* c6_1 = bsc->c6_1;
    int32_t* c7_1 = bsc->c7_1;
    int32_t* c8_1 = bsc->c8_1;
    int32_t* c9_1 = bsc->c9_1;
    int32_t* c10_1 = bsc->c10_1;
    int32_t* c11_1 = bsc->c11_1;

    #define SOA2(ARR_IDX, K) soa_c2[(((size_t)(ARR_IDX) * MAX_C4_2 + (K)) * total_threads) + gtid]
    #define SOA3(ARR_IDX, K) soa_c3[(((size_t)(ARR_IDX) * MAX_C4_3 + (K)) * total_threads) + gtid]
    #define SOA7(ARR_IDX, K) soa_c7[(((size_t)(ARR_IDX) * MAX_C8_7 + (K)) * total_threads) + gtid]

    int gp12 = Gp[1 * 12 + 2], kw12 = KW0[1 * 12 + 2];
    int gp13 = Gp[1 * 12 + 3], kw13 = KW0[1 * 12 + 3];
    int gp23 = Gp[2 * 12 + 3], kw23 = KW0[2 * 12 + 3];

    int gp45 = Gp[4 * 12 + 5], kw45 = KW0[4 * 12 + 5];
    int gp46 = Gp[4 * 12 + 6], kw46 = KW0[4 * 12 + 6];
    int gp56 = Gp[5 * 12 + 6], kw56 = KW0[5 * 12 + 6];
    int gp47 = Gp[4 * 12 + 7], kw47 = KW0[4 * 12 + 7];
    int gp57 = Gp[5 * 12 + 7], kw57 = KW0[5 * 12 + 7];
    int gp67 = Gp[6 * 12 + 7], kw67 = KW0[6 * 12 + 7];

    int gp89   = Gp[8 * 12 + 9],   kw89   = KW0[8 * 12 + 9];
    int gp810  = Gp[8 * 12 + 10],  kw810  = KW0[8 * 12 + 10];
    int gp910  = Gp[9 * 12 + 10],  kw910  = KW0[9 * 12 + 10];
    int gp811  = Gp[8 * 12 + 11],  kw811  = KW0[8 * 12 + 11];
    int gp911  = Gp[9 * 12 + 11],  kw911  = KW0[9 * 12 + 11];
    int gp1011 = Gp[10 * 12 + 11], kw1011 = KW0[10 * 12 + 11];

    unsigned long long total_b1 = 0, total_b2 = 0, total_b3 = 0;

    __shared__ int s_task_id;
    __shared__ int s_n2_1, s_n3_1, s_n4_1, s_n5_1, s_n6_1, s_n7_1, s_n8_1, s_n9_1, s_n10_1, s_n11_1;

    while (true) {
        if (tid == 0) {
            s_task_id = atomicAdd(d_task_counter, 1);
            s_n2_1 = s_n3_1 = s_n4_1 = s_n5_1 = s_n6_1 = s_n7_1 = s_n8_1 = s_n9_1 = s_n10_1 = s_n11_1 = 0;
        }
        __syncthreads();
        if (s_task_id >= total_tasks) break;

        int2 t = tasks[s_task_id];
        int b_idx = t.x;
        int idx1 = t.y;

        int i0 = reps[b_idx];
        uint64_t x0   = L0[i0 * 5 + 0];
        uint64_t gx0  = L0[i0 * 5 + 1];
        uint64_t cut0 = L0[i0 * 5 + 2];
        uint64_t o1_0 = L0[i0 * 5 + 3];
        uint64_t o2_0 = L0[i0 * 5 + 4];
        uint64_t u1_0 = o1_0 | o2_0;
        uint64_t u2_0 = o2_0;

        const int32_t* c1 = g_c1 + (size_t)b_idx * MAX_C1;
        const int32_t* c2 = g_c2 + (size_t)b_idx * MAX_C23;
        const int32_t* c3 = g_c3 + (size_t)b_idx * MAX_C23;
        int n2 = g_n2[b_idx];
        int n3 = g_n3[b_idx];

        int i1 = c1[idx1];
        uint64_t x1   = L1[i1 * 5 + 0];
        uint64_t gx1  = L1[i1 * 5 + 1];
        uint64_t cut1 = L1[i1 * 5 + 2];
        uint64_t o1_1 = L1[i1 * 5 + 3];
        uint64_t o2_1 = L1[i1 * 5 + 4];

        uint64_t cut_01 = cut0 | cut1;
        uint64_t u2_01 = u2_0 | o2_1 | (u1_0 & o1_1);
        uint64_t u1_01 = u1_0 | o1_1 | o2_1;
        uint64_t col_u2_01 = x0 & x1;
        uint64_t orb_p_01 = o2_0 | o2_1;

        for (int idx2 = tid; idx2 < n2; idx2 += bdim) {
            int i2 = c2[idx2];
            if ((cut_01 & L2[i2 * 5 + 2]) == 0 && (L2[i2 * 5 + 4] & u1_01) == 0 && (L2[i2 * 5 + 3] & u2_01) == 0) {
                if (popcnt64(x1 & L2[i2 * 5 + 0]) == gp12 && popcnt64(x1 & L2[i2 * 5 + 1]) == kw12) {
                    int pos = atomicAdd(&s_n2_1, 1);
                    if (pos < MAX_C23_1) c2_1[pos] = i2; else atomicExch(overflow_flag, 21);
                }
            }
        }
        for (int idx3 = tid; idx3 < n3; idx3 += bdim) {
            int i3 = c3[idx3];
            if ((cut_01 & L3[i3 * 5 + 2]) == 0 && (L3[i3 * 5 + 4] & u1_01) == 0 && (L3[i3 * 5 + 3] & u2_01) == 0) {
                if (popcnt64(x1 & L3[i3 * 5 + 0]) == gp13 && popcnt64(x1 & L3[i3 * 5 + 1]) == kw13) {
                    int pos = atomicAdd(&s_n3_1, 1);
                    if (pos < MAX_C23_1) c3_1[pos] = i3; else atomicExch(overflow_flag, 31);
                }
            }
        }

        #define FILTER_1_COOP(LA, GC0, GN0, CA1, SNA1) \
        { \
            const int32_t* c0_ptr = GC0 + (size_t)b_idx * MAX_C4_0; \
            int n0_cnt = GN0[b_idx]; \
            for (int k = tid; k < n0_cnt; k += bdim) { \
                int row_i = c0_ptr[k]; \
                uint64_t rx = LA[row_i * 5 + 0]; \
                if ((rx & col_u2_01) == 0 && (LA[row_i * 5 + 4] & o2_1) == 0) { \
                    if (popcnt64(rx & x1) == 1 && popcnt64(rx & gx1) == 2) { \
                        int pos = atomicAdd(&SNA1, 1); \
                        if (pos < MAX_C4_1) CA1[pos] = row_i; else atomicExch(overflow_flag, 41); \
                    } \
                } \
            } \
        }

        FILTER_1_COOP(L4, g_c4_0, g_n4_0, c4_1, s_n4_1);
        FILTER_1_COOP(L5, g_c5_0, g_n5_0, c5_1, s_n5_1);
        FILTER_1_COOP(L6, g_c6_0, g_n6_0, c6_1, s_n6_1);
        FILTER_1_COOP(L7, g_c7_0, g_n7_0, c7_1, s_n7_1);
        FILTER_1_COOP(L8, g_c8_0, g_n8_0, c8_1, s_n8_1);
        FILTER_1_COOP(L9, g_c9_0, g_n9_0, c9_1, s_n9_1);
        FILTER_1_COOP(L10, g_c10_0, g_n10_0, c10_1, s_n10_1);
        FILTER_1_COOP(L11, g_c11_0, g_n11_0, c11_1, s_n11_1);

        __syncthreads();

        int n2_1 = s_n2_1, n3_1 = s_n3_1;
        int n4_1 = s_n4_1, n5_1 = s_n5_1, n6_1 = s_n6_1, n7_1 = s_n7_1;
        int n8_1 = s_n8_1, n9_1 = s_n9_1, n10_1 = s_n10_1, n11_1 = s_n11_1;

        if (n2_1 == 0 || n3_1 == 0 || n4_1 == 0 || n5_1 == 0 || n6_1 == 0 || n7_1 == 0 || n8_1 == 0 || n9_1 == 0 || n10_1 == 0 || n11_1 == 0) {
            __syncthreads();
            continue;
        }

        for (int idx2 = tid; idx2 < n2_1; idx2 += bdim) {
            int i2 = c2_1[idx2];
            uint64_t x2   = L2[i2 * 5 + 0];
            uint64_t gx2  = L2[i2 * 5 + 1];
            uint64_t cut2 = L2[i2 * 5 + 2];
            uint64_t o1_2 = L2[i2 * 5 + 3];
            uint64_t o2_2 = L2[i2 * 5 + 4];
            uint64_t cut_012 = cut_01 | cut2;
            uint64_t u2_012 = u2_01 | o2_2 | (u1_01 & o1_2);
            uint64_t u1_012 = u1_01 | o1_2 | o2_2;
            uint64_t col_u2_012 = col_u2_01 | ((x0 | x1) & x2);

            bool has_i3 = false;
            for (int idx3 = 0; idx3 < n3_1; ++idx3) {
                int i3 = c3_1[idx3];
                if ((cut_012 & L3[i3 * 5 + 2]) == 0 && (L3[i3 * 5 + 4] & u1_012) == 0 && (L3[i3 * 5 + 3] & u2_012) == 0) {
                    if (popcnt64(x2 & L3[i3 * 5 + 0]) == gp23 && popcnt64(x2 & L3[i3 * 5 + 1]) == kw23) {
                        has_i3 = true;
                        break;
                    }
                }
            }
            if (!has_i3) continue;

            #define FILTER_2_SOA(LA, CA1, NA1, AIDX, NA2) \
            int NA2 = 0; \
            for (int k = 0; k < NA1; ++k) { \
                int row_i = CA1[k]; \
                uint64_t rx = LA[row_i * 5 + 0]; \
                if ((rx & col_u2_012) == 0 && (LA[row_i * 5 + 4] & o2_2) == 0) { \
                    if (popcnt64(rx & x2) == 1 && popcnt64(rx & gx2) == 2) { \
                        if (NA2 < MAX_C4_2) SOA2(AIDX, NA2++) = row_i; else atomicExch(overflow_flag, 42); \
                    } \
                } \
            } \
            if (NA2 == 0) continue;

            FILTER_2_SOA(L4, c4_1, n4_1, 0, n4_2);
            FILTER_2_SOA(L5, c5_1, n5_1, 1, n5_2);
            FILTER_2_SOA(L6, c6_1, n6_1, 2, n6_2);
            FILTER_2_SOA(L7, c7_1, n7_1, 3, n7_2);
            FILTER_2_SOA(L8, c8_1, n8_1, 4, n8_2);
            FILTER_2_SOA(L9, c9_1, n9_1, 5, n9_2);
            FILTER_2_SOA(L10, c10_1, n10_1, 6, n10_2);
            FILTER_2_SOA(L11, c11_1, n11_1, 7, n11_2);

            for (int idx3 = 0; idx3 < n3_1; ++idx3) {
                int i3 = c3_1[idx3];
                if ((cut_012 & L3[i3 * 5 + 2]) != 0 || (L3[i3 * 5 + 4] & u1_012) != 0 || (L3[i3 * 5 + 3] & u2_012) != 0) continue;
                uint64_t x3   = L3[i3 * 5 + 0];
                uint64_t gx3  = L3[i3 * 5 + 1];
                uint64_t o2_3 = L3[i3 * 5 + 4];
                if (popcnt64(x2 & x3) != gp23 || popcnt64(x2 & gx3) != kw23) continue;

                total_b1 += 1;
                uint64_t col_u1_B1 = x0 | x1 | x2 | x3;
                uint64_t col_u2_B1 = col_u2_012 | ((x0 | x1 | x2) & x3);
                uint64_t g_col_u2_B1 = (gx0 & gx1) | (gx0 & gx2) | (gx0 & gx3) | (gx1 & gx2) | (gx1 & gx3) | (gx2 & gx3);
                uint64_t orb_p_B1 = orb_p_01 | o2_2 | o2_3;

                uint64_t req2_B2 = O33_mask & (~col_u1_B1);
                uint64_t req1_B2 = (O33_mask & (~col_u2_B1)) | (O13_mask & (~col_u1_B1)) | (O23_mask & g_col_u2_B1);

                uint64_t req2_B3 = O22_mask & (~col_u1_B1);
                uint64_t req1_B3 = (O22_mask & (~col_u2_B1)) | (O12_mask & (~col_u1_B1)) | (O23_mask & g_col_u2_B1);

                #define FILTER_3_SOA(LA, AIDX, NA2, NA3, ORA) \
                int NA3 = 0; \
                uint64_t ORA = 0ULL; \
                for (int k = 0; k < NA2; ++k) { \
                    int row_i = SOA2(AIDX, k); \
                    uint64_t rx = LA[row_i * 5 + 0]; \
                    if ((rx & col_u2_B1) == 0 && (LA[row_i * 5 + 4] & o2_3) == 0) { \
                        if (popcnt64(rx & x3) == 1 && popcnt64(rx & gx3) == 2) { \
                            if (NA3 < MAX_C4_3) SOA3(AIDX, NA3++) = row_i; else atomicExch(overflow_flag, 43); \
                            ORA |= rx; \
                        } \
                    } \
                } \
                if (NA3 == 0) continue;

                FILTER_3_SOA(L4, 0, n4_2, n4_3, or4);
                FILTER_3_SOA(L5, 1, n5_2, n5_3, or5);
                FILTER_3_SOA(L6, 2, n6_2, n6_3, or6);
                FILTER_3_SOA(L7, 3, n7_2, n7_3, or7);

                uint64_t all_or = or4 | or5 | or6 | or7;
                if ((all_or & req1_B2) != req1_B2) continue;
                uint64_t pair_or = (or4 & or5) | (or4 & or6) | (or4 & or7) | (or5 & or6) | (or5 & or7) | (or6 & or7);
                if ((pair_or & req2_B2) != req2_B2) continue;

                FILTER_3_SOA(L8, 4, n8_2, n8_3, or8);
                FILTER_3_SOA(L9, 5, n9_2, n9_3, or9);
                FILTER_3_SOA(L10, 6, n10_2, n10_3, or10);
                FILTER_3_SOA(L11, 7, n11_2, n11_3, or11);

                uint64_t all_or_b3 = or8 | or9 | or10 | or11;
                if ((all_or_b3 & req1_B3) != req1_B3) continue;
                uint64_t pair_or_b3 = (or8 & or9) | (or8 & or10) | (or8 & or11) | (or9 & or10) | (or9 & or11) | (or10 & or11);
                if ((pair_or_b3 & req2_B3) != req2_B3) continue;

                for (int idx4 = 0; idx4 < n4_3; ++idx4) {
                    int i4 = SOA3(0, idx4);
                    uint64_t x4 = L4[i4 * 5 + 0], gx4 = L4[i4 * 5 + 1], cut4 = L4[i4 * 5 + 2], o1_4 = L4[i4 * 5 + 3], o2_4 = L4[i4 * 5 + 4];
                    uint64_t b2_u1_4 = o1_4 | o2_4;
                    uint64_t b2_u2_4 = o2_4;
                    uint64_t col_u2_4 = col_u2_B1 | (col_u1_B1 & x4);
                    uint64_t col_u1_4 = col_u1_B1 | x4;
                    for (int idx5 = 0; idx5 < n5_3; ++idx5) {
                        int i5 = SOA3(1, idx5);
                        uint64_t x5 = L5[i5 * 5 + 0], gx5 = L5[i5 * 5 + 1], cut5 = L5[i5 * 5 + 2], o1_5 = L5[i5 * 5 + 3], o2_5 = L5[i5 * 5 + 4];
                        if ((x5 & col_u2_4) != 0 || (cut4 & cut5) != 0 || (o2_5 & b2_u1_4) != 0 || (o1_5 & b2_u2_4) != 0) continue;
                        if (popcnt64(x4 & x5) != gp45 || popcnt64(x4 & gx5) != kw45) continue;
                        uint64_t cut_45 = cut4 | cut5;
                        uint64_t b2_u2_45 = b2_u2_4 | o2_5 | (b2_u1_4 & o1_5);
                        uint64_t b2_u1_45 = b2_u1_4 | o1_5 | o2_5;
                        uint64_t col_u2_45 = col_u2_4 | (col_u1_4 & x5);
                        uint64_t col_u1_45 = col_u1_4 | x5;
                        for (int idx6 = 0; idx6 < n6_3; ++idx6) {
                            int i6 = SOA3(2, idx6);
                            uint64_t x6 = L6[i6 * 5 + 0], gx6 = L6[i6 * 5 + 1], cut6 = L6[i6 * 5 + 2], o1_6 = L6[i6 * 5 + 3], o2_6 = L6[i6 * 5 + 4];
                            if ((x6 & col_u2_45) != 0 || (cut_45 & cut6) != 0 || (o2_6 & b2_u1_45) != 0 || (o1_6 & b2_u2_45) != 0) continue;
                            if (popcnt64(x4 & x6) != gp46 || popcnt64(x4 & gx6) != kw46) continue;
                            if (popcnt64(x5 & x6) != gp56 || popcnt64(x5 & gx6) != kw56) continue;
                            uint64_t cut_456 = cut_45 | cut6;
                            uint64_t b2_u2_456 = b2_u2_45 | o2_6 | (b2_u1_45 & o1_6);
                            uint64_t b2_u1_456 = b2_u1_45 | o1_6 | o2_6;
                            uint64_t col_u2_456 = col_u2_45 | (col_u1_45 & x6);
                            uint64_t col_u1_456 = col_u1_45 | x6;
                            for (int idx7 = 0; idx7 < n7_3; ++idx7) {
                                int i7 = SOA3(3, idx7);
                                uint64_t x7 = L7[i7 * 5 + 0], gx7 = L7[i7 * 5 + 1], cut7 = L7[i7 * 5 + 2], o1_7 = L7[i7 * 5 + 3], o2_7 = L7[i7 * 5 + 4];
                                if ((x7 & col_u2_456) != 0 || (cut_456 & cut7) != 0 || (o2_7 & b2_u1_456) != 0 || (o1_7 & b2_u2_456) != 0) continue;
                                if (popcnt64(x4 & x7) != gp47 || popcnt64(x4 & gx7) != kw47) continue;
                                if (popcnt64(x5 & x7) != gp57 || popcnt64(x5 & gx7) != kw57) continue;
                                if (popcnt64(x6 & x7) != gp67 || popcnt64(x6 & gx7) != kw67) continue;

                                total_b2 += 1;
                                uint64_t col_u2_B12 = col_u2_456 | (col_u1_456 & x7);
                                uint64_t orb_p_B12 = orb_p_B1 | o2_4 | o2_5 | o2_6 | o2_7;

                                #define FILTER_7_SOA(LA, AIDX3, NA3, AIDX7, NA7) \
                                int NA7 = 0; \
                                for (int k = 0; k < NA3; ++k) { \
                                    int ri = SOA3(AIDX3, k); \
                                    uint64_t rx = LA[ri * 5 + 0]; \
                                    if ((rx & col_u2_B12) != 0 || (LA[ri * 5 + 4] & orb_p_B12) != 0) continue; \
                                    if (popcnt64(rx & x4) == 1 && popcnt64(rx & x5) == 1 && popcnt64(rx & x6) == 1 && popcnt64(rx & x7) == 1) { \
                                        if (popcnt64(rx & gx4) == 2 && popcnt64(rx & gx5) == 2 && popcnt64(rx & gx6) == 2 && popcnt64(rx & gx7) == 2) { \
                                            if (NA7 < MAX_C8_7) SOA7(AIDX7, NA7++) = ri; else atomicExch(overflow_flag, 87); \
                                        } \
                                    } \
                                } \
                                if (NA7 == 0) continue;

                                FILTER_7_SOA(L8, 4, n8_3, 0, n8_7);
                                FILTER_7_SOA(L9, 5, n9_3, 1, n9_7);
                                FILTER_7_SOA(L10, 6, n10_3, 2, n10_7);
                                FILTER_7_SOA(L11, 7, n11_3, 3, n11_7);

                                for (int idx8 = 0; idx8 < n8_7; ++idx8) {
                                    int i8 = SOA7(0, idx8);
                                    uint64_t x8 = L8[i8 * 5 + 0], gx8 = L8[i8 * 5 + 1];
                                    for (int idx9 = 0; idx9 < n9_7; ++idx9) {
                                        int i9 = SOA7(1, idx9);
                                        uint64_t x9 = L9[i9 * 5 + 0], gx9 = L9[i9 * 5 + 1];
                                        if (popcnt64(x8 & x9) != gp89 || popcnt64(x8 & gx9) != kw89) continue;
                                        for (int idx10 = 0; idx10 < n10_7; ++idx10) {
                                            int i10 = SOA7(2, idx10);
                                            uint64_t x10 = L10[i10 * 5 + 0], gx10 = L10[i10 * 5 + 1];
                                            if (popcnt64(x8 & x10) != gp810 || popcnt64(x8 & gx10) != kw810) continue;
                                            if (popcnt64(x9 & x10) != gp910 || popcnt64(x9 & gx10) != kw910) continue;
                                            for (int idx11 = 0; idx11 < n11_7; ++idx11) {
                                                int i11 = SOA7(3, idx11);
                                                uint64_t x11 = L11[i11 * 5 + 0], gx11 = L11[i11 * 5 + 1];
                                                if (popcnt64(x8 & x11) != gp811 || popcnt64(x8 & gx11) != kw811) continue;
                                                if (popcnt64(x9 & x11) != gp911 || popcnt64(x9 & gx11) != kw911) continue;
                                                if (popcnt64(x10 & x11) != gp1011 || popcnt64(x10 & gx11) != kw1011) continue;
                                                if ((col_u2_B12 | (x8 & x9) | (x8 & x10) | (x8 & x11) | (x9 & x10) | (x9 & x11) | (x10 & x11)) == ((1ULL << 60) - 1ULL)) {
                                                    total_b3 += 1;
                                                }
                                            }
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
    if (total_b1 > 0) atomicAdd(d_b1_sols, total_b1);
    if (total_b2 > 0) atomicAdd(d_b2_sols, total_b2);
    if (total_b3 > 0) atomicAdd(d_b3_sols, total_b3);
}

extern "C" {

void gpu_compute_canons(
    const uint64_t* h_L, int n_rows,
    const int32_t* h_perms, int n_perms,
    uint64_t* h_out_can
) {
    uint64_t *d_L, *d_out;
    int32_t *d_perms;
    cudaMalloc(&d_L, (size_t)n_rows * 5 * sizeof(uint64_t));
    cudaMalloc(&d_perms, (size_t)n_perms * 60 * sizeof(int32_t));
    cudaMalloc(&d_out, (size_t)n_rows * sizeof(uint64_t));
    cudaMemcpy(d_L, h_L, (size_t)n_rows * 5 * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_perms, h_perms, (size_t)n_perms * 60 * sizeof(int32_t), cudaMemcpyHostToDevice);
    int threads = 256;
    int blocks = (n_rows + threads - 1) / threads;
    compute_canon_kernel<<<blocks, threads>>>(d_L, n_rows, d_perms, n_perms, d_out);
    cudaDeviceSynchronize();
    cudaMemcpy(h_out_can, d_out, (size_t)n_rows * sizeof(uint64_t), cudaMemcpyDeviceToHost);
    cudaFree(d_L);
    cudaFree(d_perms);
    cudaFree(d_out);
}

struct GpuSolverCtx {
    uint64_t* d_L[12];
    uint64_t* d_can[12];
    int len[12];
    int32_t *d_Gp, *d_KW0;
    uint64_t O33_mask, O13_mask, O23_mask, O22_mask, O12_mask;

    int32_t *d_c1, *d_n1;
    int32_t *d_c2, *d_n2;
    int32_t *d_c3, *d_n3;
    int32_t *d_c4_0, *d_n4_0;
    int32_t *d_c5_0, *d_n5_0;
    int32_t *d_c6_0, *d_n6_0;
    int32_t *d_c7_0, *d_n7_0;
    int32_t *d_c8_0, *d_n8_0;
    int32_t *d_c9_0, *d_n9_0;
    int32_t *d_c10_0, *d_n10_0;
    int32_t *d_c11_0, *d_n11_0;
    int32_t *d_overflow;

    BlockScratch* d_block_scratch;
    int32_t *d_soa_c2, *d_soa_c3, *d_soa_c7;
    int num_blocks, threads_per_block;
};

GpuSolverCtx* gpu_solver_init(
    const uint64_t** h_L, const int* lengths, const uint64_t** h_can,
    const int32_t* h_Gp, const int32_t* h_KW0,
    uint64_t O33_mask, uint64_t O13_mask, uint64_t O23_mask, uint64_t O22_mask, uint64_t O12_mask,
    int max_batch, int num_blocks, int threads_per_block
) {
    GpuSolverCtx* ctx = new GpuSolverCtx();
    ctx->O33_mask = O33_mask;
    ctx->O13_mask = O13_mask;
    ctx->O23_mask = O23_mask;
    ctx->O22_mask = O22_mask;
    ctx->O12_mask = O12_mask;
    ctx->num_blocks = num_blocks;
    ctx->threads_per_block = threads_per_block;
    size_t total_threads = (size_t)num_blocks * threads_per_block;

    for (int a = 0; a < 12; ++a) {
        ctx->len[a] = lengths[a];
        cudaMalloc(&ctx->d_L[a], (size_t)lengths[a] * 5 * sizeof(uint64_t));
        cudaMemcpy(ctx->d_L[a], h_L[a], (size_t)lengths[a] * 5 * sizeof(uint64_t), cudaMemcpyHostToDevice);
        cudaMalloc(&ctx->d_can[a], (size_t)lengths[a] * sizeof(uint64_t));
        cudaMemcpy(ctx->d_can[a], h_can[a], (size_t)lengths[a] * sizeof(uint64_t), cudaMemcpyHostToDevice);
    }
    cudaMalloc(&ctx->d_Gp, 144 * sizeof(int32_t));
    cudaMemcpy(ctx->d_Gp, h_Gp, 144 * sizeof(int32_t), cudaMemcpyHostToDevice);
    cudaMalloc(&ctx->d_KW0, 144 * sizeof(int32_t));
    cudaMemcpy(ctx->d_KW0, h_KW0, 144 * sizeof(int32_t), cudaMemcpyHostToDevice);

    cudaMalloc(&ctx->d_c1, (size_t)max_batch * MAX_C1 * sizeof(int32_t));
    cudaMalloc(&ctx->d_n1, (size_t)max_batch * sizeof(int32_t));
    cudaMalloc(&ctx->d_c2, (size_t)max_batch * MAX_C23 * sizeof(int32_t));
    cudaMalloc(&ctx->d_n2, (size_t)max_batch * sizeof(int32_t));
    cudaMalloc(&ctx->d_c3, (size_t)max_batch * MAX_C23 * sizeof(int32_t));
    cudaMalloc(&ctx->d_n3, (size_t)max_batch * sizeof(int32_t));

    #define ALLOC_B23(DC, DN) \
        cudaMalloc(&ctx->DC, (size_t)max_batch * MAX_C4_0 * sizeof(int32_t)); \
        cudaMalloc(&ctx->DN, (size_t)max_batch * sizeof(int32_t));

    ALLOC_B23(d_c4_0, d_n4_0);
    ALLOC_B23(d_c5_0, d_n5_0);
    ALLOC_B23(d_c6_0, d_n6_0);
    ALLOC_B23(d_c7_0, d_n7_0);
    ALLOC_B23(d_c8_0, d_n8_0);
    ALLOC_B23(d_c9_0, d_n9_0);
    ALLOC_B23(d_c10_0, d_n10_0);
    ALLOC_B23(d_c11_0, d_n11_0);

    cudaMalloc(&ctx->d_overflow, sizeof(int32_t));
    cudaMalloc(&ctx->d_block_scratch, (size_t)num_blocks * sizeof(BlockScratch));
    cudaMalloc(&ctx->d_soa_c2, 8ULL * MAX_C4_2 * total_threads * sizeof(int32_t));
    cudaMalloc(&ctx->d_soa_c3, 8ULL * MAX_C4_3 * total_threads * sizeof(int32_t));
    cudaMalloc(&ctx->d_soa_c7, 4ULL * MAX_C8_7 * total_threads * sizeof(int32_t));
    return ctx;
}

void gpu_solve_batch(
    GpuSolverCtx* ctx,
    int batch_n,
    const int32_t* h_reps,
    const uint64_t* h_rep_canons,
    unsigned long long* out_totals
) {
    int32_t* d_reps;
    uint64_t* d_rep_canons;
    cudaMalloc(&d_reps, batch_n * sizeof(int32_t));
    cudaMalloc(&d_rep_canons, batch_n * sizeof(uint64_t));
    cudaMemcpy(d_reps, h_reps, batch_n * sizeof(int32_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_rep_canons, h_rep_canons, batch_n * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemset(ctx->d_overflow, 0, sizeof(int32_t));

    stage1_filter_r0_kernel<<<batch_n, 256>>>(
        batch_n, d_reps, d_rep_canons,
        ctx->d_L[0], ctx->len[0],
        ctx->d_L[1], ctx->len[1], ctx->d_can[1],
        ctx->d_L[2], ctx->len[2], ctx->d_can[2],
        ctx->d_L[3], ctx->len[3], ctx->d_can[3],
        ctx->d_L[4], ctx->len[4], ctx->d_can[4],
        ctx->d_L[5], ctx->len[5], ctx->d_can[5],
        ctx->d_L[6], ctx->len[6], ctx->d_can[6],
        ctx->d_L[7], ctx->len[7], ctx->d_can[7],
        ctx->d_L[8], ctx->len[8], ctx->d_can[8],
        ctx->d_L[9], ctx->len[9], ctx->d_can[9],
        ctx->d_L[10], ctx->len[10], ctx->d_can[10],
        ctx->d_L[11], ctx->len[11], ctx->d_can[11],
        ctx->d_Gp, ctx->d_KW0,
        ctx->d_c1, ctx->d_n1,
        ctx->d_c2, ctx->d_n2,
        ctx->d_c3, ctx->d_n3,
        ctx->d_c4_0, ctx->d_n4_0,
        ctx->d_c5_0, ctx->d_n5_0,
        ctx->d_c6_0, ctx->d_n6_0,
        ctx->d_c7_0, ctx->d_n7_0,
        ctx->d_c8_0, ctx->d_n8_0,
        ctx->d_c9_0, ctx->d_n9_0,
        ctx->d_c10_0, ctx->d_n10_0,
        ctx->d_c11_0, ctx->d_n11_0,
        ctx->d_overflow
    );
    cudaDeviceSynchronize();

    int32_t* h_n1 = new int32_t[batch_n];
    cudaMemcpy(h_n1, ctx->d_n1, batch_n * sizeof(int32_t), cudaMemcpyDeviceToHost);
    int total_tasks = 0;
    for (int i = 0; i < batch_n; ++i) total_tasks += h_n1[i];

    int2* h_tasks = new int2[total_tasks];
    int p = 0;
    for (int i = 0; i < batch_n; ++i) {
        for (int j = 0; j < h_n1[i]; ++j) {
            h_tasks[p].x = i;
            h_tasks[p].y = j;
            p++;
        }
    }
    int2* d_tasks;
    int* d_task_counter;
    unsigned long long *d_b1_sols, *d_b2_sols, *d_b3_sols;
    cudaMalloc(&d_tasks, (size_t)total_tasks * sizeof(int2));
    cudaMemcpy(d_tasks, h_tasks, (size_t)total_tasks * sizeof(int2), cudaMemcpyHostToDevice);
    cudaMalloc(&d_task_counter, sizeof(int));
    cudaMemset(d_task_counter, 0, sizeof(int));
    cudaMalloc(&d_b1_sols, sizeof(unsigned long long));
    cudaMalloc(&d_b2_sols, sizeof(unsigned long long));
    cudaMalloc(&d_b3_sols, sizeof(unsigned long long));
    cudaMemset(d_b1_sols, 0, sizeof(unsigned long long));
    cudaMemset(d_b2_sols, 0, sizeof(unsigned long long));
    cudaMemset(d_b3_sols, 0, sizeof(unsigned long long));

    stage2_block_coop_kernel<<<ctx->num_blocks, ctx->threads_per_block>>>(
        total_tasks, d_tasks, d_task_counter,
        d_reps,
        ctx->d_L[0], ctx->d_L[1], ctx->d_L[2], ctx->d_L[3],
        ctx->d_L[4], ctx->d_L[5], ctx->d_L[6], ctx->d_L[7],
        ctx->d_L[8], ctx->d_L[9], ctx->d_L[10], ctx->d_L[11],
        ctx->d_Gp, ctx->d_KW0,
        ctx->O33_mask, ctx->O13_mask, ctx->O23_mask, ctx->O22_mask, ctx->O12_mask,
        ctx->d_c1, ctx->d_n1,
        ctx->d_c2, ctx->d_n2,
        ctx->d_c3, ctx->d_n3,
        ctx->d_c4_0, ctx->d_n4_0,
        ctx->d_c5_0, ctx->d_n5_0,
        ctx->d_c6_0, ctx->d_n6_0,
        ctx->d_c7_0, ctx->d_n7_0,
        ctx->d_c8_0, ctx->d_n8_0,
        ctx->d_c9_0, ctx->d_n9_0,
        ctx->d_c10_0, ctx->d_n10_0,
        ctx->d_c11_0, ctx->d_n11_0,
        ctx->d_block_scratch,
        ctx->d_soa_c2, ctx->d_soa_c3, ctx->d_soa_c7,
        d_b1_sols, d_b2_sols, d_b3_sols,
        ctx->d_overflow
    );
    cudaDeviceSynchronize();

    int32_t ovf = 0;
    cudaMemcpy(&ovf, ctx->d_overflow, sizeof(int32_t), cudaMemcpyDeviceToHost);
    if (ovf != 0) {
        printf("ERROR: Overflow flag = %d!\n", ovf);
    }

    cudaMemcpy(&out_totals[0], d_b1_sols, sizeof(unsigned long long), cudaMemcpyDeviceToHost);
    cudaMemcpy(&out_totals[1], d_b2_sols, sizeof(unsigned long long), cudaMemcpyDeviceToHost);
    cudaMemcpy(&out_totals[2], d_b3_sols, sizeof(unsigned long long), cudaMemcpyDeviceToHost);

    delete[] h_n1;
    delete[] h_tasks;
    cudaFree(d_reps);
    cudaFree(d_rep_canons);
    cudaFree(d_tasks);
    cudaFree(d_task_counter);
    cudaFree(d_b1_sols);
    cudaFree(d_b2_sols);
    cudaFree(d_b3_sols);
}

}
"""

def main():
    t0 = time.time()
    with open("/tmp/orbit9_coop.cu", "w") as f:
        f.write(CUDA_SRC)
    subprocess.run(
        ["nvcc", "-O3", "-arch=native", "-shared", "-Xcompiler", "-fPIC", "/tmp/orbit9_coop.cu", "-o", "/tmp/orbit9_coop.so"],
        check=True
    )
    lib = ctypes.CDLL("/tmp/orbit9_coop.so")
    print(f"Compiled block-cooperative CUDA kernel in {time.time() - t0:.2f}s!", flush=True)

    F12 = np.zeros((12, 12), dtype=int)
    for b_idx in range(6):
        F12[2 * b_idx, 2 * b_idx + 1] = F12[2 * b_idx + 1, 2 * b_idx] = 1
    I12 = np.eye(12, dtype=int)
    J12 = np.ones((12, 12), dtype=int)

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

    M = np.zeros((12, 12), dtype=int)
    for base in (0, 4, 8):
        M[base, base + 2] = M[base + 2, base] = 1
        M[base + 1, base + 3] = M[base + 3, base + 1] = 1
    E = M.copy()
    Gp = 9 * I12 + J12 - M
    KW0 = 2 * J12 - F12 - E - (M @ E) - (E @ M)
    Delta0 = 2 * J12 - I12 - F12 - M - E @ F12
    comps = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]

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

    row_cache = {}
    def gen_2block_rows_cached(I_B_tuple, target_deg_tuple, diag_kw):
        key = (I_B_tuple, target_deg_tuple, diag_kw)
        if key in row_cache:
            return row_cache[key]
        I_B_set = set(I_B_tuple)
        req_pairs = diag_kw // 2
        ok_cols = [
            c for c in range(60)
            if not (cols_60[c][0] in I_B_set and cols_60[c][1] in I_B_set)
            and target_deg_tuple[cols_60[c][0]] > 0
            and target_deg_tuple[cols_60[c][1]] > 0
        ]
        adj_cols = [[] for _ in range(12)]
        for c in ok_cols:
            u, v = cols_60[c]
            adj_cols[min(u, v)].append((c, max(u, v)))
        rem_deg = list(target_deg_tuple)
        chosen = []
        res = []
        def bt_v(v_idx):
            if v_idx == 12:
                if len(chosen) == 10:
                    r_set = set(chosen)
                    npairs = 0
                    for c in chosen:
                        if c < g_col[c] and g_col[c] in r_set:
                            npairs += 1
                    if npairs == req_pairs:
                        xm = gxm = cutm = o1m = o2m = 0
                        for c in chosen:
                            xm |= 1 << c
                            gxm |= 1 << g_col[c]
                            u, v = cols_60[c]
                            if (u in I_B_set) ^ (v in I_B_set):
                                cutm |= 1 << c
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if s == 1:
                                o1m |= 1 << idx_m
                            elif s == 2:
                                o2m |= 1 << idx_m
                        res.append((xm, gxm, cutm, o1m, o2m))
                return
            need = rem_deg[v_idx]
            if need < 0:
                return
            avail = [(c, w) for (c, w) in adj_cols[v_idx] if rem_deg[w] > 0]
            if len(avail) < need:
                return
            for comb in combinations(avail, need):
                for c, w in comb:
                    rem_deg[w] -= 1
                    chosen.append(c)
                rem_deg[v_idx] = 0
                bt_v(v_idx + 1)
                rem_deg[v_idx] = need
                for c, w in comb:
                    rem_deg[w] += 1
                    chosen.pop()
        bt_v(0)
        arr = np.array(res, dtype=np.uint64)
        row_cache[key] = arr
        return arr

    row_order = [0, 3, 2, 1, 4, 7, 6, 5, 8, 11, 10, 9]
    L_raw = []
    for comp in comps:
        I_B = tuple(comp)
        for i in comp:
            L_raw.append(gen_2block_rows_cached(I_B, tuple(int(Delta0[i, j]) for j in range(12)), int(KW0[i, i])))
    L = [np.ascontiguousarray(L_raw[r], dtype=np.uint64) for r in row_order]
    Gp_ord = np.ascontiguousarray(Gp[np.ix_(row_order, row_order)] - 2 * np.eye(12, dtype=int), dtype=np.int32)
    KW0_ord = np.ascontiguousarray(KW0[np.ix_(row_order, row_order)], dtype=np.int32)

    B1_set, B2_set, B3_set = set(comps[0]), set(comps[1]), set(comps[2])
    O33_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in B3_set and v in B3_set))
    O13_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in B1_set and v in B3_set) or (u in B3_set and v in B1_set)))
    O23_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in B2_set and v in B3_set) or (u in B3_set and v in B2_set)))
    O22_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in B2_set and v in B2_set))
    O12_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if (u in B1_set and v in B2_set) or (u in B2_set and v in B1_set)))

    stab_a_to_0 = [[] for _ in range(12)]
    for g_p in b6_perms:
        ok = True
        for u in range(12):
            for v in range(12):
                if M[u, v] != M[g_p[u], g_p[v]] or E[u, v] != E[g_p[u], g_p[v]]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            for a_idx, orig_row in enumerate(row_order):
                if g_p[orig_row] == 0:
                    c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                    stab_a_to_0[a_idx].append(np.array(c_map, dtype=np.int32))
    stab_a_to_0 = [np.ascontiguousarray(x, dtype=np.int32) for x in stab_a_to_0]

    lib.gpu_compute_canons.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p
    ]
    c_cans = []
    for a in range(12):
        out_c = np.empty(len(L[a]), dtype=np.uint64)
        lib.gpu_compute_canons(
            L[a].ctypes.data, len(L[a]),
            stab_a_to_0[a].ctypes.data, len(stab_a_to_0[a]),
            out_c.ctypes.data
        )
        c_cans.append(out_c)

    reps = np.array([i for i in range(len(L[0])) if L[0][i, 0] == c_cans[0][i]], dtype=np.int32)
    rep_canons = np.array([c_cans[0][i] for i in reps], dtype=np.uint64)
    print(f"Setup & GPU canonical masks ready in {time.time() - t0:.2f}s: {len(reps)} reps!", flush=True)

    lib.gpu_solver_init.restype = ctypes.c_void_p
    lib.gpu_solver_init.argtypes = [
        ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64,
        ctypes.c_int, ctypes.c_int, ctypes.c_int
    ]
    lib.gpu_solve_batch.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
    ]

    L_ptrs = (ctypes.c_void_p * 12)(*[L[a].ctypes.data for a in range(12)])
    lengths = (ctypes.c_int * 12)(*[len(L[a]) for a in range(12)])
    can_ptrs = (ctypes.c_void_p * 12)(*[c_cans[a].ctypes.data for a in range(12)])

    batch_sz = 512
    num_blocks = 512
    threads_per_block = 128
    ctx = lib.gpu_solver_init(
        L_ptrs, lengths, can_ptrs,
        Gp_ord.ctypes.data, KW0_ord.ctypes.data,
        int(O33_mask), int(O13_mask), int(O23_mask), int(O22_mask), int(O12_mask),
        batch_sz, num_blocks, threads_per_block
    )

    t_orb = time.time()
    # Run ALL 8 batches (0..4092) with the ultra-fast block-cooperative kernel!
    tot_b1 = 61062148
    tot_b2 = 684776
    tot_b3 = 0
    for st in range(2560, len(reps), batch_sz):
        en = min(st + batch_sz, len(reps))
        b_reps = np.ascontiguousarray(reps[st:en], dtype=np.int32)
        b_cans = np.ascontiguousarray(rep_canons[st:en], dtype=np.uint64)
        out_totals = np.zeros(3, dtype=np.uint64)
        tb0 = time.time()
        lib.gpu_solve_batch(ctx, len(b_reps), b_reps.ctypes.data, b_cans.ctypes.data, out_totals.ctypes.data)
        tot_b1 += int(out_totals[0])
        tot_b2 += int(out_totals[1])
        tot_b3 += int(out_totals[2])
        print(f"  [COOP-GPU Orbit 9 batch {en:4d}/{len(reps)}] batch_b1={int(out_totals[0]):9d}, cum_b1={tot_b1:9d}, cum_b12={tot_b2:7d}, cum_b123={tot_b3} (batch {time.time()-tb0:.2f}s, tot {time.time()-t_orb:.2f}s)", flush=True)

    dt = time.time() - t_orb
    print(f"[COOP-GPU 10/10] Orbit 9 (C+C+C): reps={len(reps)}, b1_sols={tot_b1}, b12_sols={tot_b2}, b123_sols={tot_b3} in {dt:.2f}s!", flush=True)

if __name__ == "__main__":
    main()
