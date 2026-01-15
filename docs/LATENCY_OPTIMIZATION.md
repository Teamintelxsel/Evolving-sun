# Latency Optimization Guide

## Overview

This guide covers comprehensive latency optimization techniques for achieving sub-50ms response times with 99.9% stability.

## Industry Benchmarks

### Model Size vs. Expected Latency

| Model Size | Typical Latency | Optimized Latency | Target CV |
|------------|----------------|-------------------|-----------|
| Small (<1B) | 20-50ms | 10-20ms | <0.1% |
| Medium (1-7B) | 50-200ms | 30-100ms | <0.1% |
| Large (7-70B) | 200-1000ms | 100-500ms | <0.1% |
| XL (70B+) | 1000-5000ms | 500-2000ms | <0.1% |

## Optimization Techniques

### 1. Quantization

**INT8 Quantization**
- Expected gain: 2-3x speedup
- Memory reduction: 4x
- Accuracy impact: <1%

```python
# Example with PyTorch
import torch
model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
```

**INT4 Quantization**
- Expected gain: 4-6x speedup
- Memory reduction: 8x
- Accuracy impact: 1-3%

### 2. Flash Attention 2

- Expected gain: 2-3x speedup for attention layers
- Memory reduction: 5-20x
- No accuracy impact

```python
# Install: pip install flash-attn
from flash_attn import flash_attn_func
```

### 3. Speculative Decoding

- Expected gain: 2-3x speedup for generation
- Requires draft model (10% of main model size)
- Best for autoregressive tasks

### 4. Continuous Batching

- Expected gain: 2-10x throughput improvement
- Dynamic batching of requests
- Optimal batch size: 8-32 for most models

### 5. KV Cache Optimization

- PagedAttention for memory efficiency
- Expected memory reduction: 2-4x
- Enables larger batch sizes

```python
# Example configuration
kv_cache_config = {
    "block_size": 16,
    "max_blocks": 1024,
    "swap_space": "8GB"
}
```

### 6. Tensor Parallelism

- Split model across GPUs
- Expected speedup: 0.7-0.9x per GPU (communication overhead)
- Best for very large models

### 7. Pipeline Parallelism

- Different layers on different GPUs
- Expected speedup: 0.8-0.95x per GPU
- Better for sequential models

### 8. Prompt Caching

- Cache common prompt prefixes
- Expected gain: 10-100x for repeated prefixes
- Implement with LRU cache

### 9. Torch 2.0 Compilation

```python
import torch
model = torch.compile(model, mode="reduce-overhead")
# Expected gain: 1.2-2x speedup
```

### 10. ONNX Runtime

- Expected gain: 1.5-3x speedup
- Good cross-platform support
- Requires model conversion

## Hardware Tuning

### CPU Pinning

```bash
# Pin process to specific cores
taskset -c 0-7 python benchmark.py
```

### Kernel Parameters

```bash
# Disable CPU frequency scaling
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Increase file descriptors
ulimit -n 65536
```

### GPU Optimization

```bash
# Set maximum performance mode
nvidia-smi -pm 1
nvidia-smi -pl 300  # Set power limit

# Set clock speeds
nvidia-smi -lgc 1410  # Graphics clock
```

## Batching Strategies

### Static Batching
```python
batch_sizes = [1, 2, 4, 8, 16, 32, 64]
optimal_batch = find_optimal_batch(model, batch_sizes)
```

### Dynamic Batching
```python
# Adaptive batch size based on queue length
def get_batch_size(queue_length):
    if queue_length < 10:
        return 1
    elif queue_length < 50:
        return 8
    else:
        return 32
```

## Before/After Comparison

### Measurement Methodology

1. **Baseline Measurement**
   - Run 1000 iterations
   - Measure p50, p95, p99
   - Calculate coefficient of variation

2. **Apply Optimization**
   - Apply single optimization
   - Re-run 1000 iterations
   - Compare metrics

3. **Validation**
   - Verify accuracy maintained
   - Check for regressions
   - Test edge cases

### Example Results

```
Baseline:
- p50: 150ms
- p95: 220ms
- p99: 280ms
- CV: 0.15%

After INT8 Quantization + Flash Attention:
- p50: 55ms (2.7x faster)
- p95: 82ms (2.7x faster)
- p99: 105ms (2.7x faster)
- CV: 0.08%
```

## Verification Checklist

- [ ] Latency reduced by expected amount
- [ ] Coefficient of variation < 0.1%
- [ ] Accuracy degradation < 1%
- [ ] No crashes or errors during stress test
- [ ] Results reproducible across 3+ runs
- [ ] All percentiles improved (p50, p95, p99)
- [ ] Throughput maintained or improved
- [ ] Memory usage within limits

## Tools

### Profiling
- PyTorch Profiler
- NVIDIA Nsight Systems
- cProfile for Python

### Monitoring
- `nvidia-smi` for GPU monitoring
- `htop` for CPU monitoring
- Custom dashboard (see DASHBOARD_SETUP.md)

## Common Pitfalls

1. **Measuring cold start latency**: Always warm up model
2. **Small sample sizes**: Use at least 1000 iterations
3. **Not controlling for variance**: Lock CPU frequencies
4. **Ignoring accuracy**: Always validate outputs
5. **Over-optimization**: Stop when targets are met

## References

- [FlashAttention Paper](https://arxiv.org/abs/2205.14135)
- [Speculative Decoding](https://arxiv.org/abs/2211.17192)
- [PagedAttention](https://arxiv.org/abs/2309.06180)
