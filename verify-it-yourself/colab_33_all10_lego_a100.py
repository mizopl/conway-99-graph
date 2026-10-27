import ctypes
import json
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
    uint64_t mask = L_a[idx * 6 + 0];
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

#define MAX_C0 32768
#define MAX_C1 8192
#define MAX_C2 2048
#define MAX_C3 512

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
    const int32_t* __restrict__ Gp,
    const int32_t* __restrict__ KW0,
    int32_t* __restrict__ g_c1, int32_t* __restrict__ g_n1,
    int32_t* __restrict__ g_c2, int32_t* __restrict__ g_n2,
    int32_t* __restrict__ g_c3, int32_t* __restrict__ g_n3,
    int32_t* __restrict__ g_c4, int32_t* __restrict__ g_n4,
    int32_t* __restrict__ g_c5, int32_t* __restrict__ g_n5,
    int32_t* __restrict__ overflow_flag
) {
    int b_idx = blockIdx.x;
    if (b_idx >= batch_n) return;
    int tid = threadIdx.x;
    int bdim = blockDim.x;

    __shared__ int s_n1, s_n2, s_n3, s_n4, s_n5;
    if (tid == 0) {
        s_n1 = s_n2 = s_n3 = s_n4 = s_n5 = 0;
    }
    __syncthreads();

    int i0 = reps[b_idx];
    uint64_t min_can  = rep_canons[b_idx];
    uint64_t x0       = L0[i0 * 6 + 0];
    uint64_t o11_0    = L0[i0 * 6 + 2];
    uint64_t o12_1_0  = L0[i0 * 6 + 3];
    uint64_t o12_2_0  = L0[i0 * 6 + 4];
    uint64_t o2_0     = L0[i0 * 6 + 5];
    uint64_t u1_12_0  = o12_1_0 | o12_2_0;
    uint64_t u2_12_0  = o12_2_0;

    #define FILTER_R0(LA, LENA, CANA, GCA, SNA, A_IDX) \
    { \
        int32_t* ca = GCA + (size_t)b_idx * MAX_C0; \
        int gp0a = Gp[0 * 6 + (A_IDX)], kw0a = KW0[0 * 6 + (A_IDX)]; \
        for (int i = tid; i < (LENA); i += bdim) { \
            if (CANA[i] >= min_can && (o11_0 & LA[i * 6 + 2]) == 0 && (LA[i * 6 + 4] & u1_12_0) == 0 && (LA[i * 6 + 3] & u2_12_0) == 0 && (o2_0 & LA[i * 6 + 5]) == 0) { \
                if (popcnt64(x0 & LA[i * 6 + 0]) == gp0a && popcnt64(x0 & LA[i * 6 + 1]) == kw0a) { \
                    int pos = atomicAdd(&SNA, 1); \
                    if (pos < MAX_C0) ca[pos] = i; else atomicExch(overflow_flag, (A_IDX)); \
                } \
            } \
        } \
    }

    FILTER_R0(L1, len1, c1_can, g_c1, s_n1, 1);
    FILTER_R0(L2, len2, c2_can, g_c2, s_n2, 2);
    FILTER_R0(L3, len3, c3_can, g_c3, s_n3, 3);
    FILTER_R0(L4, len4, c4_can, g_c4, s_n4, 4);
    FILTER_R0(L5, len5, c5_can, g_c5, s_n5, 5);

    __syncthreads();
    if (tid == 0) {
        g_n1[b_idx] = s_n1;
        g_n2[b_idx] = s_n2;
        g_n3[b_idx] = s_n3;
        g_n4[b_idx] = s_n4;
        g_n5[b_idx] = s_n5;
    }
}

struct BlockScratch6 {
    int32_t c2_1[MAX_C1];
    int32_t c3_1[MAX_C1];
    int32_t c4_1[MAX_C1];
    int32_t c5_1[MAX_C1];
};

__global__ void stage2_6row_coop_kernel(
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
    const int32_t* __restrict__ Gp,
    const int32_t* __restrict__ KW0,
    uint64_t C11_col_mask,
    uint64_t C22_col_mask,
    const int32_t* __restrict__ g_c1, const int32_t* __restrict__ g_n1,
    const int32_t* __restrict__ g_c2, const int32_t* __restrict__ g_n2,
    const int32_t* __restrict__ g_c3, const int32_t* __restrict__ g_n3,
    const int32_t* __restrict__ g_c4, const int32_t* __restrict__ g_n4,
    const int32_t* __restrict__ g_c5, const int32_t* __restrict__ g_n5,
    BlockScratch6* __restrict__ block_scratch_pool,
    int32_t* __restrict__ soa_c2,   // 3 * MAX_C2 * total_threads
    int32_t* __restrict__ soa_c3,   // 2 * MAX_C3 * total_threads
    unsigned long long* __restrict__ d_d3_cnt,
    unsigned long long* __restrict__ d_sol_cnt,
    int32_t* __restrict__ overflow_flag
) {
    int bid = blockIdx.x;
    int tid = threadIdx.x;
    int bdim = blockDim.x;
    size_t total_threads = (size_t)gridDim.x * bdim;
    size_t gtid = (size_t)bid * bdim + tid;

    BlockScratch6* bsc = &block_scratch_pool[bid];
    int32_t* c2_1 = bsc->c2_1;
    int32_t* c3_1 = bsc->c3_1;
    int32_t* c4_1 = bsc->c4_1;
    int32_t* c5_1 = bsc->c5_1;

    #define SOA2(ARR_IDX, K) soa_c2[(((size_t)(ARR_IDX) * MAX_C2 + (K)) * total_threads) + gtid]
    #define SOA3(ARR_IDX, K) soa_c3[(((size_t)(ARR_IDX) * MAX_C3 + (K)) * total_threads) + gtid]

    int gp12 = Gp[1 * 6 + 2], kw12 = KW0[1 * 6 + 2];
    int gp13 = Gp[1 * 6 + 3], kw13 = KW0[1 * 6 + 3];
    int gp14 = Gp[1 * 6 + 4], kw14 = KW0[1 * 6 + 4];
    int gp15 = Gp[1 * 6 + 5], kw15 = KW0[1 * 6 + 5];

    int gp23 = Gp[2 * 6 + 3], kw23 = KW0[2 * 6 + 3];
    int gp24 = Gp[2 * 6 + 4], kw24 = KW0[2 * 6 + 4];
    int gp25 = Gp[2 * 6 + 5], kw25 = KW0[2 * 6 + 5];

    int gp34 = Gp[3 * 6 + 4], kw34 = KW0[3 * 6 + 4];
    int gp35 = Gp[3 * 6 + 5], kw35 = KW0[3 * 6 + 5];

    int gp45 = Gp[4 * 6 + 5], kw45 = KW0[4 * 6 + 5];

    unsigned long long loc_d3 = 0, loc_sols = 0;

    __shared__ int s_task_id;
    __shared__ int s_n2_1, s_n3_1, s_n4_1, s_n5_1;
    __shared__ int s_skip;

    while (true) {
        if (tid == 0) {
            s_task_id = atomicAdd(d_task_counter, 1);
            s_n2_1 = s_n3_1 = s_n4_1 = s_n5_1 = 0;
            s_skip = 0;
        }
        __syncthreads();
        if (s_task_id >= total_tasks) break;

        int2 t = tasks[s_task_id];
        int b_idx = t.x;
        int idx1 = t.y;

        int i0 = reps[b_idx];
        uint64_t x0       = L0[i0 * 6 + 0];
        uint64_t gx0      = L0[i0 * 6 + 1];
        uint64_t o11_0    = L0[i0 * 6 + 2];
        uint64_t o12_1_0  = L0[i0 * 6 + 3];
        uint64_t o12_2_0  = L0[i0 * 6 + 4];
        uint64_t o2_0     = L0[i0 * 6 + 5];
        uint64_t u1_12_0  = o12_1_0 | o12_2_0;
        uint64_t u2_12_0  = o12_2_0;

        const int32_t* c1 = g_c1 + (size_t)b_idx * MAX_C0;
        int i1 = c1[idx1];
        uint64_t x1       = L1[i1 * 6 + 0];
        uint64_t gx1      = L1[i1 * 6 + 1];
        uint64_t o11_1    = L1[i1 * 6 + 2];
        uint64_t o12_1_1  = L1[i1 * 6 + 3];
        uint64_t o12_2_1  = L1[i1 * 6 + 4];
        uint64_t o2_1     = L1[i1 * 6 + 5];

        uint64_t col_u2_01 = x0 & x1;
        uint64_t g_col_u2_01 = gx0 & gx1;
        if (((col_u2_01 & g_col_u2_01) & C22_col_mask) != 0ULL || (col_u2_01 & C11_col_mask) != 0ULL) {
            __syncthreads();
            continue;
        }

        uint64_t o11_01   = o11_0 | o11_1;
        uint64_t u2_12_01 = u2_12_0 | o12_2_1 | (u1_12_0 & o12_1_1);
        uint64_t u1_12_01 = u1_12_0 | o12_1_1 | o12_2_1;
        uint64_t o2_01    = o2_0 | o2_1;
        uint64_t col_u1_01 = x0 | x1;

        #define FILTER_R1_COOP(LA, GC0, GN0, CA1, SNA1, GP1A, KW1A, CODE) \
        { \
            const int32_t* c0_ptr = GC0 + (size_t)b_idx * MAX_C0; \
            int n0_cnt = GN0[b_idx]; \
            for (int k = tid; k < n0_cnt; k += bdim) { \
                int ri = c0_ptr[k]; \
                uint64_t rx = LA[ri * 6 + 0]; \
                if ((rx & col_u2_01) == 0ULL && (o11_01 & LA[ri * 6 + 2]) == 0ULL && (LA[ri * 6 + 4] & u1_12_01) == 0ULL && (LA[ri * 6 + 3] & u2_12_01) == 0ULL && (o2_01 & LA[ri * 6 + 5]) == 0ULL) { \
                    if (popcnt64(x1 & rx) == (GP1A) && popcnt64(x1 & LA[ri * 6 + 1]) == (KW1A)) { \
                        int pos = atomicAdd(&SNA1, 1); \
                        if (pos < MAX_C1) CA1[pos] = ri; else atomicExch(overflow_flag, (CODE)); \
                    } \
                } \
            } \
        }

        FILTER_R1_COOP(L2, g_c2, g_n2, c2_1, s_n2_1, gp12, kw12, 21);
        FILTER_R1_COOP(L3, g_c3, g_n3, c3_1, s_n3_1, gp13, kw13, 31);
        FILTER_R1_COOP(L4, g_c4, g_n4, c4_1, s_n4_1, gp14, kw14, 41);
        FILTER_R1_COOP(L5, g_c5, g_n5, c5_1, s_n5_1, gp15, kw15, 51);

        __syncthreads();
        int n2_1 = s_n2_1, n3_1 = s_n3_1, n4_1 = s_n4_1, n5_1 = s_n5_1;
        if (n2_1 == 0 || n3_1 == 0 || n4_1 == 0 || n5_1 == 0) {
            __syncthreads();
            continue;
        }

        for (int idx2 = tid; idx2 < n2_1; idx2 += bdim) {
            int i2 = c2_1[idx2];
            uint64_t x2       = L2[i2 * 6 + 0];
            uint64_t gx2      = L2[i2 * 6 + 1];
            uint64_t o11_2    = L2[i2 * 6 + 2];
            uint64_t o12_1_2  = L2[i2 * 6 + 3];
            uint64_t o12_2_2  = L2[i2 * 6 + 4];
            uint64_t o2_2     = L2[i2 * 6 + 5];

            uint64_t col_u2_012 = col_u2_01 | (col_u1_01 & x2);
            uint64_t g_col_u2_012 = g_col_u2_01 | ((gx0 | gx1) & gx2);
            if (((col_u2_012 & g_col_u2_012) & C22_col_mask) != 0ULL) continue;

            uint64_t o11_012   = o11_01 | o11_2;
            uint64_t u2_12_012 = u2_12_01 | o12_2_2 | (u1_12_01 & o12_1_2);
            uint64_t u1_12_012 = u1_12_01 | o12_1_2 | o12_2_2;
            uint64_t o2_012    = o2_01 | o2_2;
            uint64_t col_u1_012 = col_u1_01 | x2;

            #define FILTER_R2_SOA(LA, CA1, NA1, AIDX, NA2, GP2A, KW2A, CODE) \
            int NA2 = 0; \
            for (int k = 0; k < (NA1); ++k) { \
                int ri = CA1[k]; \
                uint64_t rx = LA[ri * 6 + 0]; \
                if ((rx & col_u2_012) == 0ULL && (o11_012 & LA[ri * 6 + 2]) == 0ULL && (LA[ri * 6 + 4] & u1_12_012) == 0ULL && (LA[ri * 6 + 3] & u2_12_012) == 0ULL && (o2_012 & LA[ri * 6 + 5]) == 0ULL) { \
                    if (popcnt64(x2 & rx) == (GP2A) && popcnt64(x2 & LA[ri * 6 + 1]) == (KW2A)) { \
                        if (NA2 < MAX_C2) SOA2(AIDX, NA2++) = ri; else atomicExch(overflow_flag, (CODE)); \
                    } \
                } \
            } \
            if (NA2 == 0) continue;

            FILTER_R2_SOA(L3, c3_1, n3_1, 0, n3_2, gp23, kw23, 32);
            FILTER_R2_SOA(L4, c4_1, n4_1, 1, n4_2, gp24, kw24, 42);
            FILTER_R2_SOA(L5, c5_1, n5_1, 2, n5_2, gp25, kw25, 52);

            for (int idx3 = 0; idx3 < n3_2; ++idx3) {
                int i3 = SOA2(0, idx3);
                uint64_t x3       = L3[i3 * 6 + 0];
                uint64_t gx3      = L3[i3 * 6 + 1];
                uint64_t o11_3    = L3[i3 * 6 + 2];
                uint64_t o12_1_3  = L3[i3 * 6 + 3];
                uint64_t o12_2_3  = L3[i3 * 6 + 4];
                uint64_t o2_3     = L3[i3 * 6 + 5];

                uint64_t col_u2_0123 = col_u2_012 | (col_u1_012 & x3);
                uint64_t g_col_u2_0123 = g_col_u2_012 | ((gx0 | gx1 | gx2) & gx3);
                if (((col_u2_0123 & g_col_u2_0123) & C22_col_mask) != 0ULL) continue;
                loc_d3 += 1ULL;

                uint64_t o11_0123   = o11_012 | o11_3;
                uint64_t u2_12_0123 = u2_12_012 | o12_2_3 | (u1_12_012 & o12_1_3);
                uint64_t u1_12_0123 = u1_12_012 | o12_1_3 | o12_2_3;
                uint64_t o2_0123    = o2_012 | o2_3;
                uint64_t col_u1_0123 = col_u1_012 | x3;

                #define FILTER_R3_SOA(LA, AIDX2, NA2, AIDX3, NA3, GP3A, KW3A, CODE) \
                int NA3 = 0; \
                for (int k = 0; k < (NA2); ++k) { \
                    int ri = SOA2(AIDX2, k); \
                    uint64_t rx = LA[ri * 6 + 0]; \
                    if ((rx & col_u2_0123) == 0ULL && (o11_0123 & LA[ri * 6 + 2]) == 0ULL && (LA[ri * 6 + 4] & u1_12_0123) == 0ULL && (LA[ri * 6 + 3] & u2_12_0123) == 0ULL && (o2_0123 & LA[ri * 6 + 5]) == 0ULL) { \
                        if (popcnt64(x3 & rx) == (GP3A) && popcnt64(x3 & LA[ri * 6 + 1]) == (KW3A)) { \
                            if (NA3 < MAX_C3) SOA3(AIDX3, NA3++) = ri; else atomicExch(overflow_flag, (CODE)); \
                        } \
                    } \
                } \
                if (NA3 == 0) continue;

                FILTER_R3_SOA(L4, 1, n4_2, 0, n4_3, gp34, kw34, 43);
                FILTER_R3_SOA(L5, 2, n5_2, 1, n5_3, gp35, kw35, 53);

                for (int idx4 = 0; idx4 < n4_3; ++idx4) {
                    int i4 = SOA3(0, idx4);
                    uint64_t x4       = L4[i4 * 6 + 0];
                    uint64_t gx4      = L4[i4 * 6 + 1];
                    uint64_t o11_4    = L4[i4 * 6 + 2];
                    uint64_t o12_1_4  = L4[i4 * 6 + 3];
                    uint64_t o12_2_4  = L4[i4 * 6 + 4];
                    uint64_t o2_4     = L4[i4 * 6 + 5];

                    uint64_t col_u2_4 = col_u2_0123 | (col_u1_0123 & x4);
                    uint64_t g_col_u2_4 = g_col_u2_0123 | ((gx0 | gx1 | gx2 | gx3) & gx4);
                    if (((col_u2_4 & g_col_u2_4) & C22_col_mask) != 0ULL) continue;

                    uint64_t o11_4_acc = o11_0123 | o11_4;
                    uint64_t u2_12_4   = u2_12_0123 | o12_2_4 | (u1_12_0123 & o12_1_4);
                    uint64_t u1_12_4   = u1_12_0123 | o12_1_4 | o12_2_4;
                    uint64_t o2_4_acc  = o2_0123 | o2_4;
                    uint64_t col_u1_4  = col_u1_0123 | x4;

                    for (int idx5 = 0; idx5 < n5_3; ++idx5) {
                        int i5 = SOA3(1, idx5);
                        uint64_t x5       = L5[i5 * 6 + 0];
                        uint64_t gx5      = L5[i5 * 6 + 1];
                        uint64_t o11_5    = L5[i5 * 6 + 2];
                        uint64_t o12_1_5  = L5[i5 * 6 + 3];
                        uint64_t o12_2_5  = L5[i5 * 6 + 4];
                        uint64_t o2_5     = L5[i5 * 6 + 5];

                        if ((x5 & col_u2_4) != 0ULL || (o11_4_acc & o11_5) != 0ULL || (o12_2_5 & u1_12_4) != 0ULL || (o12_1_5 & u2_12_4) != 0ULL || (o2_4_acc & o2_5) != 0ULL) continue;
                        if (popcnt64(x4 & x5) != gp45 || popcnt64(x4 & gx5) != kw45) continue;

                        uint64_t col_u2_5 = col_u2_4 | (col_u1_4 & x5);
                        uint64_t g_col_u2_5 = g_col_u2_4 | ((gx0 | gx1 | gx2 | gx3 | gx4) & gx5);
                        if (((col_u2_5 & g_col_u2_5) & C22_col_mask) != 0ULL) continue;

                        uint64_t col_u1_5 = col_u1_4 | x5;
                        if ((col_u1_5 & C22_col_mask) == C22_col_mask && popcnt64(col_u2_5 & C22_col_mask) == 6) {
                            loc_sols += 1ULL;
                        }
                    }
                }
            }
        }
        __syncthreads();
    }
    if (loc_d3 > 0) atomicAdd(d_d3_cnt, loc_d3);
    if (loc_sols > 0) atomicAdd(d_sol_cnt, loc_sols);
}

extern "C" {

void gpu_compute_canons6(
    const uint64_t* h_L, int n_rows,
    const int32_t* h_perms, int n_perms,
    uint64_t* h_out_can
) {
    uint64_t *d_L, *d_out;
    int32_t *d_perms;
    cudaMalloc(&d_L, (size_t)n_rows * 6 * sizeof(uint64_t));
    cudaMalloc(&d_perms, (size_t)n_perms * 60 * sizeof(int32_t));
    cudaMalloc(&d_out, (size_t)n_rows * sizeof(uint64_t));
    cudaMemcpy(d_L, h_L, (size_t)n_rows * 6 * sizeof(uint64_t), cudaMemcpyHostToDevice);
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

struct GpuSolver6Ctx {
    uint64_t* d_L[6];
    uint64_t* d_can[6];
    int len[6];
    int32_t *d_Gp, *d_KW0;
    uint64_t C11_col_mask, C22_col_mask;

    int32_t *d_c1, *d_n1;
    int32_t *d_c2, *d_n2;
    int32_t *d_c3, *d_n3;
    int32_t *d_c4, *d_n4;
    int32_t *d_c5, *d_n5;
    int32_t *d_overflow;

    BlockScratch6* d_block_scratch;
    int32_t *d_soa_c2, *d_soa_c3;
    int num_blocks, threads_per_block;
};

GpuSolver6Ctx* gpu_solver6_init(
    const uint64_t** h_L, const int* lengths, const uint64_t** h_can,
    const int32_t* h_Gp, const int32_t* h_KW0,
    uint64_t C11_col_mask, uint64_t C22_col_mask,
    int max_batch, int num_blocks, int threads_per_block
) {
    GpuSolver6Ctx* ctx = new GpuSolver6Ctx();
    ctx->C11_col_mask = C11_col_mask;
    ctx->C22_col_mask = C22_col_mask;
    ctx->num_blocks = num_blocks;
    ctx->threads_per_block = threads_per_block;
    size_t total_threads = (size_t)num_blocks * threads_per_block;

    for (int a = 0; a < 6; ++a) {
        ctx->len[a] = lengths[a];
        cudaMalloc(&ctx->d_L[a], (size_t)lengths[a] * 6 * sizeof(uint64_t));
        cudaMemcpy(ctx->d_L[a], h_L[a], (size_t)lengths[a] * 6 * sizeof(uint64_t), cudaMemcpyHostToDevice);
        cudaMalloc(&ctx->d_can[a], (size_t)lengths[a] * sizeof(uint64_t));
        cudaMemcpy(ctx->d_can[a], h_can[a], (size_t)lengths[a] * sizeof(uint64_t), cudaMemcpyHostToDevice);
    }
    cudaMalloc(&ctx->d_Gp, 36 * sizeof(int32_t));
    cudaMemcpy(ctx->d_Gp, h_Gp, 36 * sizeof(int32_t), cudaMemcpyHostToDevice);
    cudaMalloc(&ctx->d_KW0, 36 * sizeof(int32_t));
    cudaMemcpy(ctx->d_KW0, h_KW0, 36 * sizeof(int32_t), cudaMemcpyHostToDevice);

    cudaMalloc(&ctx->d_c1, (size_t)max_batch * MAX_C0 * sizeof(int32_t));
    cudaMalloc(&ctx->d_n1, (size_t)max_batch * sizeof(int32_t));
    cudaMalloc(&ctx->d_c2, (size_t)max_batch * MAX_C0 * sizeof(int32_t));
    cudaMalloc(&ctx->d_n2, (size_t)max_batch * sizeof(int32_t));
    cudaMalloc(&ctx->d_c3, (size_t)max_batch * MAX_C0 * sizeof(int32_t));
    cudaMalloc(&ctx->d_n3, (size_t)max_batch * sizeof(int32_t));
    cudaMalloc(&ctx->d_c4, (size_t)max_batch * MAX_C0 * sizeof(int32_t));
    cudaMalloc(&ctx->d_n4, (size_t)max_batch * sizeof(int32_t));
    cudaMalloc(&ctx->d_c5, (size_t)max_batch * MAX_C0 * sizeof(int32_t));
    cudaMalloc(&ctx->d_n5, (size_t)max_batch * sizeof(int32_t));

    cudaMalloc(&ctx->d_overflow, sizeof(int32_t));
    cudaMalloc(&ctx->d_block_scratch, (size_t)num_blocks * sizeof(BlockScratch6));
    cudaMalloc(&ctx->d_soa_c2, 3ULL * MAX_C2 * total_threads * sizeof(int32_t));
    cudaMalloc(&ctx->d_soa_c3, 2ULL * MAX_C3 * total_threads * sizeof(int32_t));
    return ctx;
}

void gpu_solver6_free(GpuSolver6Ctx* ctx) {
    for (int a = 0; a < 6; ++a) {
        cudaFree(ctx->d_L[a]);
        cudaFree(ctx->d_can[a]);
    }
    cudaFree(ctx->d_Gp);
    cudaFree(ctx->d_KW0);
    cudaFree(ctx->d_c1); cudaFree(ctx->d_n1);
    cudaFree(ctx->d_c2); cudaFree(ctx->d_n2);
    cudaFree(ctx->d_c3); cudaFree(ctx->d_n3);
    cudaFree(ctx->d_c4); cudaFree(ctx->d_n4);
    cudaFree(ctx->d_c5); cudaFree(ctx->d_n5);
    cudaFree(ctx->d_overflow);
    cudaFree(ctx->d_block_scratch);
    cudaFree(ctx->d_soa_c2);
    cudaFree(ctx->d_soa_c3);
    delete ctx;
}

void gpu_solve6_batch(
    GpuSolver6Ctx* ctx,
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
        ctx->d_Gp, ctx->d_KW0,
        ctx->d_c1, ctx->d_n1,
        ctx->d_c2, ctx->d_n2,
        ctx->d_c3, ctx->d_n3,
        ctx->d_c4, ctx->d_n4,
        ctx->d_c5, ctx->d_n5,
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
    unsigned long long *d_d3_cnt, *d_sol_cnt;
    cudaMalloc(&d_tasks, (size_t)(total_tasks > 0 ? total_tasks : 1) * sizeof(int2));
    if (total_tasks > 0) {
        cudaMemcpy(d_tasks, h_tasks, (size_t)total_tasks * sizeof(int2), cudaMemcpyHostToDevice);
    }
    cudaMalloc(&d_task_counter, sizeof(int));
    cudaMemset(d_task_counter, 0, sizeof(int));
    cudaMalloc(&d_d3_cnt, sizeof(unsigned long long));
    cudaMalloc(&d_sol_cnt, sizeof(unsigned long long));
    cudaMemset(d_d3_cnt, 0, sizeof(unsigned long long));
    cudaMemset(d_sol_cnt, 0, sizeof(unsigned long long));

    if (total_tasks > 0) {
        stage2_6row_coop_kernel<<<ctx->num_blocks, ctx->threads_per_block>>>(
            total_tasks, d_tasks, d_task_counter,
            d_reps,
            ctx->d_L[0], ctx->d_L[1], ctx->d_L[2], ctx->d_L[3], ctx->d_L[4], ctx->d_L[5],
            ctx->d_Gp, ctx->d_KW0,
            ctx->C11_col_mask, ctx->C22_col_mask,
            ctx->d_c1, ctx->d_n1,
            ctx->d_c2, ctx->d_n2,
            ctx->d_c3, ctx->d_n3,
            ctx->d_c4, ctx->d_n4,
            ctx->d_c5, ctx->d_n5,
            ctx->d_block_scratch,
            ctx->d_soa_c2, ctx->d_soa_c3,
            d_d3_cnt, d_sol_cnt,
            ctx->d_overflow
        );
        cudaDeviceSynchronize();
    }

    int32_t ovf = 0;
    cudaMemcpy(&ovf, ctx->d_overflow, sizeof(int32_t), cudaMemcpyDeviceToHost);
    if (ovf != 0) {
        printf("ERROR: Overflow flag = %d!\n", ovf);
    }

    cudaMemcpy(&out_totals[0], d_d3_cnt, sizeof(unsigned long long), cudaMemcpyDeviceToHost);
    cudaMemcpy(&out_totals[1], d_sol_cnt, sizeof(unsigned long long), cudaMemcpyDeviceToHost);

    delete[] h_n1;
    delete[] h_tasks;
    cudaFree(d_reps);
    cudaFree(d_rep_canons);
    cudaFree(d_tasks);
    cudaFree(d_task_counter);
    cudaFree(d_d3_cnt);
    cudaFree(d_sol_cnt);
}

}
"""


def main():
    t0 = time.time()
    with open("/tmp/lego33_coop.cu", "w") as f:
        f.write(CUDA_SRC)
    subprocess.run(
        ["nvcc", "-O3", "-arch=native", "-shared", "-Xcompiler", "-fPIC", "/tmp/lego33_coop.cu", "-o", "/tmp/lego33_coop.so"],
        check=True
    )
    lib = ctypes.CDLL("/tmp/lego33_coop.so")
    print(f"Compiled LEGO 3+3 CUDA kernel in {time.time() - t0:.2f}s!", flush=True)

    lib.gpu_compute_canons6.argtypes = [
        ctypes.c_void_p, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_int,
        ctypes.c_void_p
    ]
    lib.gpu_solver6_init.argtypes = [
        ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_uint64, ctypes.c_uint64,
        ctypes.c_int, ctypes.c_int, ctypes.c_int
    ]
    lib.gpu_solver6_init.restype = ctypes.c_void_p
    lib.gpu_solver6_free.argtypes = [ctypes.c_void_p]
    lib.gpu_solve6_batch.argtypes = [
        ctypes.c_void_p, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p
    ]

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

    orbits_33 = []
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
                    if sig == "3+3":
                        orbits_33.append((M0_mat, E0_mat, comps))

    b3_perms_6 = []
    for bp in permutations(range(3)):
        for flips in product((0, 1), repeat=3):
            p = []
            for b_new, fl in zip(bp, flips):
                p.extend([2 * b_new + fl, 2 * b_new + (1 - fl)])
            b3_perms_6.append(tuple(p))

    def canon_3block(M6, E6):
        best = None
        for p in b3_perms_6:
            Mp = M6[np.ix_(p, p)]
            Ep = E6[np.ix_(p, p)]
            k = tuple(Mp.flatten()) + tuple(Ep.flatten())
            if best is None or k < best:
                best = k
        return best

    c3_classes = []
    seen_c3 = set()
    for M, E, comps in orbits_33:
        for comp in comps:
            M6 = M[np.ix_(comp, comp)]
            E6 = E[np.ix_(comp, comp)]
            ck = canon_3block(M6, E6)
            if ck not in seen_c3:
                seen_c3.add(ck)
                c3_classes.append((M6, E6))

    print(f"Extracted {len(c3_classes)} canonical 3-block classes from {len(orbits_33)} 3+3 orbits.", flush=True)

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

    I_B1 = {0, 1, 2, 3, 4, 5}
    O11_orb_mask = np.uint64(0)
    O12_orb_mask = np.uint64(0)
    for idx_m, (c, gc) in enumerate(orbs_30):
        u, v = cols_60[c]
        cnt_in = (1 if u in I_B1 else 0) + (1 if v in I_B1 else 0)
        if cnt_in == 2:
            O11_orb_mask |= np.uint64(1 << idx_m)
        elif cnt_in == 1:
            O12_orb_mask |= np.uint64(1 << idx_m)

    C11_col_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u in I_B1 and v in I_B1))
    C22_col_mask = np.uint64(sum(1 << c for c, (u, v) in enumerate(cols_60) if u not in I_B1 and v not in I_B1))

    row_3block_cache = {}
    def gen_3block_rows_cached(target_deg_tuple, diag_kw):
        key = (target_deg_tuple, diag_kw)
        if key in row_3block_cache:
            return row_3block_cache[key]
        req_pairs = diag_kw // 2
        ok_cols = [
            c for c in range(60)
            if target_deg_tuple[cols_60[c][0]] > 0
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
                    ok_p = True
                    for c in chosen:
                        if c < g_col[c] and g_col[c] in r_set:
                            npairs += 1
                            if cols_60[c][0] in I_B1 and cols_60[c][1] in I_B1:
                                ok_p = False
                                break
                    if ok_p and npairs == req_pairs:
                        xm = gxm = o11_1 = o12_1 = o12_2 = o2_all = 0
                        for c in chosen:
                            xm |= 1 << c
                            gxm |= 1 << g_col[c]
                        for idx_m, (c, gc) in enumerate(orbs_30):
                            s = (1 if c in r_set else 0) + (1 if gc in r_set else 0)
                            if s == 2:
                                o2_all |= 1 << idx_m
                            if (int(O11_orb_mask) >> idx_m) & 1:
                                if s == 1:
                                    o11_1 |= 1 << idx_m
                            elif (int(O12_orb_mask) >> idx_m) & 1:
                                if s == 1:
                                    o12_1 |= 1 << idx_m
                                elif s == 2:
                                    o12_2 |= 1 << idx_m
                        res.append((xm, gxm, o11_1, o12_1, o12_2, o2_all))
                return
            need = rem_deg[v_idx]
            if need < 0: return
            avail = [(c, w) for (c, w) in adj_cols[v_idx] if rem_deg[w] > 0]
            if len(avail) < need: return
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
        arr = np.ascontiguousarray(np.array(res, dtype=np.uint64))
        row_3block_cache[key] = arr
        return arr

    F6 = np.zeros((6, 6), dtype=int)
    for b_idx in range(3):
        F6[2 * b_idx, 2 * b_idx + 1] = F6[2 * b_idx + 1, 2 * b_idx] = 1
    I6 = np.eye(6, dtype=int)
    J6 = np.ones((6, 6), dtype=int)

    summary = []
    for idx_c, (M6, E6) in enumerate(c3_classes):
        t_c = time.time()
        KW6 = (2 * J6 - F6 - E6 - (M6 @ E6) - (E6 @ M6)).astype(np.int32)
        Delta6 = 2 * J6 - I6 - F6 - M6 - (E6 @ F6)
        Gp6 = (9 * I6 + J6 - M6 - 2 * I6).astype(np.int32)

        used = set()
        order = []
        for u in range(6):
            if u in used: continue
            best_v = None
            for v in range(u + 1, 6):
                if v not in used and KW6[u, v] == 2:
                    best_v = v; break
            if best_v is not None:
                order.extend([u, best_v])
                used.add(u); used.add(best_v)
        for u in range(6):
            if u not in used:
                order.append(u); used.add(u)

        L_raw = [gen_3block_rows_cached(tuple(int(Delta6[i, j]) for j in range(6)) + (2, 2, 2, 2, 2, 2), int(KW6[i, i])) for i in range(6)]
        L = [L_raw[r] for r in order]
        Gp_ord = np.ascontiguousarray(Gp6[np.ix_(order, order)], dtype=np.int32)
        KW_ord = np.ascontiguousarray(KW6[np.ix_(order, order)], dtype=np.int32)

        stab_b1 = [p for p in b3_perms_6 if (M6 == M6[np.ix_(p, p)]).all() and (E6 == E6[np.ix_(p, p)]).all()]
        stab_a_to_0 = [[] for _ in range(6)]
        for p1 in stab_b1:
            for p2 in b3_perms_6:
                g_p = list(p1) + [6 + x for x in p2]
                for a_idx, orig_r in enumerate(order):
                    if g_p[orig_r] == order[0]:
                        c_map = [col_idx[(g_p[j1], g_p[j2])] for (j1, j2) in cols_60]
                        stab_a_to_0[a_idx].append(np.array(c_map, dtype=np.int32))
        stab_a_to_0 = [np.ascontiguousarray(np.array(x, dtype=np.int32)) if len(x) > 0 else np.zeros((0, 60), dtype=np.int32) for x in stab_a_to_0]

        c_cans = []
        for a in range(6):
            n_rows = len(L[a])
            n_perms = len(stab_a_to_0[a])
            out_can = np.empty(n_rows, dtype=np.uint64)
            if n_perms > 0:
                lib.gpu_compute_canons6(
                    L[a].ctypes.data_as(ctypes.c_void_p), n_rows,
                    stab_a_to_0[a].ctypes.data_as(ctypes.c_void_p), n_perms,
                    out_can.ctypes.data_as(ctypes.c_void_p)
                )
            else:
                out_can.fill(np.uint64(0xFFFFFFFFFFFFFFFF))
            c_cans.append(out_can)

        reps = np.ascontiguousarray([i for i in range(len(L[0])) if L[0][i, 0] == c_cans[0][i]], dtype=np.int32)
        rep_canons = np.ascontiguousarray([c_cans[0][i] for i in reps], dtype=np.uint64)

        h_L_ptrs = (ctypes.c_void_p * 6)(*[L[a].ctypes.data_as(ctypes.c_void_p) for a in range(6)])
        lengths_arr = (ctypes.c_int * 6)(*[len(L[a]) for a in range(6)])
        h_can_ptrs = (ctypes.c_void_p * 6)(*[c_cans[a].ctypes.data_as(ctypes.c_void_p) for a in range(6)])

        batch_size = 512
        ctx = lib.gpu_solver6_init(
            h_L_ptrs, lengths_arr, h_can_ptrs,
            Gp_ord.ctypes.data_as(ctypes.c_void_p),
            KW_ord.ctypes.data_as(ctypes.c_void_p),
            ctypes.c_uint64(int(C11_col_mask)),
            ctypes.c_uint64(int(C22_col_mask)),
            batch_size, 512, 128
        )

        # Quick cross-check on Class C_0 first 200 reps!
        if idx_c == 0 and len(reps) >= 200:
            out_chk = np.zeros(2, dtype=np.uint64)
            lib.gpu_solve6_batch(
                ctx, 200,
                reps[:200].ctypes.data_as(ctypes.c_void_p),
                rep_canons[:200].ctypes.data_as(ctypes.c_void_p),
                out_chk.ctypes.data_as(ctypes.c_void_p)
            )
            print(f"  [CPU-GPU CHECK Class C_0 first 200 reps]: d3={int(out_chk[0])} (expected 72398778), sols={int(out_chk[1])}", flush=True)

        cum_d3 = 0
        cum_sols = 0
        for start in range(0, len(reps), batch_size):
            end = min(start + batch_size, len(reps))
            b_reps = np.ascontiguousarray(reps[start:end], dtype=np.int32)
            b_cans = np.ascontiguousarray(rep_canons[start:end], dtype=np.uint64)
            out_totals = np.zeros(2, dtype=np.uint64)
            lib.gpu_solve6_batch(
                ctx, len(b_reps),
                b_reps.ctypes.data_as(ctypes.c_void_p),
                b_cans.ctypes.data_as(ctypes.c_void_p),
                out_totals.ctypes.data_as(ctypes.c_void_p)
            )
            cum_d3 += int(out_totals[0])
            cum_sols += int(out_totals[1])

        lib.gpu_solver6_free(ctx)
        el = time.time() - t_c
        print(f"[LEGO-3B {idx_c+1}/10] Class C_{idx_c}: order={order}, stab={len(stab_b1)}x48, reps={len(reps)}, d3={cum_d3}, sols={cum_sols} in {el:.2f}s!", flush=True)
        summary.append({
            "class_idx": idx_c,
            "order": order,
            "stab_b1": len(stab_b1),
            "reps": int(len(reps)),
            "d3": cum_d3,
            "sols": cum_sols,
            "elapsed_s": round(el, 3)
        })

    print("JSON_33_SUMMARY:" + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
