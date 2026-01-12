# Distributed Execution Guide

## Overview

This guide covers setting up and running distributed benchmark execution across multiple GPUs to reduce 500-iteration runtime from ~8 hours to ~50 minutes.

## Hardware Requirements

### Minimum Configuration
- 4 GPUs (NVIDIA recommended)
- 32GB RAM
- 8+ CPU cores
- 100GB free disk space

### Optimal Configuration
- 10 GPUs (one per worker)
- 128GB RAM
- 32+ CPU cores
- 500GB SSD storage

## Software Requirements

```bash
# Core dependencies
pip install ray[default]>=2.5.0
pip install gputil>=1.4.0

# Optional monitoring
pip install prometheus-client
pip install grafana-api
```

## Architecture

### Worker Distribution

```
Master Node
├── Coordinator Process
│   ├── Task Distribution
│   ├── Result Aggregation
│   └── Progress Tracking
└── Worker Pool (10 workers)
    ├── Worker 0: GPU 0, CPU Cores 0-2
    ├── Worker 1: GPU 1, CPU Cores 3-5
    ├── Worker 2: GPU 2, CPU Cores 6-8
    ├── ...
    └── Worker 9: GPU 9, CPU Cores 27-29
```

### Task Scheduling

- **Total iterations**: 500
- **Workers**: 10
- **Batch size**: 10 iterations per batch
- **Total batches**: 50
- **Expected time**: ~50 minutes (1 min per batch)

## Ray Setup

### Single Machine (Multiple GPUs)

```python
import ray

# Initialize Ray
ray.init(
    num_gpus=10,
    num_cpus=30,
    object_store_memory=10 * 1024 * 1024 * 1024  # 10GB
)

# Define remote worker
@ray.remote(num_gpus=1, num_cpus=3)
class BenchmarkWorker:
    def run_iteration(self, iteration):
        # Run benchmark iteration
        pass

# Create workers
workers = [BenchmarkWorker.remote() for _ in range(10)]

# Distribute work
futures = []
for i, worker in enumerate(workers):
    for batch in range(50):
        iteration = batch * 10 + i + 1
        futures.append(worker.run_iteration.remote(iteration))

# Collect results
results = ray.get(futures)
```

### Multi-Machine Cluster

```bash
# On head node
ray start --head --port=6379

# On worker nodes
ray start --address='<head-node-ip>:6379'
```

## Configuration

### Ray Configuration (`config/ray_config.yaml`)

```yaml
cluster:
  head_node: localhost
  port: 6379
  
resources:
  gpus_per_worker: 1
  cpus_per_worker: 3
  memory_per_worker: 8GB
  
scheduling:
  batch_size: 10
  max_retries: 3
  timeout_minutes: 5
  
monitoring:
  dashboard_port: 8265
  prometheus_port: 8080
```

## Running Distributed Benchmarks

### Basic Usage

```bash
# Start Ray cluster
ray start --head

# Run distributed benchmark
python scripts/distributed_executor.py \
    --iterations 500 \
    --workers 10 \
    --batch-size 10

# Monitor progress
ray dashboard  # Open http://localhost:8265
```

### Advanced Options

```bash
# With specific GPU allocation
CUDA_VISIBLE_DEVICES=0,1,2,3 python scripts/distributed_executor.py \
    --workers 4

# With fault tolerance
python scripts/distributed_executor.py \
    --retry-failed \
    --max-retries 3

# Resume from checkpoint
python scripts/distributed_executor.py \
    --resume checkpoints/distributed_iter_250.json
```

## Monitoring

### Ray Dashboard

Access at `http://localhost:8265`:
- Task progress
- Resource utilization
- Worker status
- Error logs

### Custom Monitoring

```python
# Track worker progress
def monitor_progress(futures):
    completed = 0
    total = len(futures)
    
    while completed < total:
        ready, not_ready = ray.wait(futures, num_returns=1, timeout=1.0)
        completed += len(ready)
        
        print(f"Progress: {completed}/{total} ({completed/total*100:.1f}%)")
```

### GPU Monitoring

```bash
# Watch GPU utilization
watch -n 1 nvidia-smi

# Log to file
nvidia-smi dmon -s um -o TD -f gpu_usage.log
```

## Fault Tolerance

### Automatic Retry

```python
@ray.remote(max_retries=3, retry_exceptions=True)
class RobustWorker:
    def run_iteration(self, iteration):
        try:
            return benchmark_iteration(iteration)
        except Exception as e:
            logger.error(f"Iteration {iteration} failed: {e}")
            raise
```

### Checkpoint Strategy

- Save checkpoint every 50 iterations
- Include worker states
- Enable resume from any checkpoint

### Error Handling

1. **Worker Failure**: Restart worker, retry failed tasks
2. **GPU OOM**: Reduce batch size, retry
3. **Network Error**: Reconnect, resume from checkpoint
4. **Timeout**: Mark as failed, continue with other tasks

## Performance Optimization

### Minimize Communication Overhead

```python
# Bad: Frequent small transfers
for i in range(1000):
    result = worker.run.remote(i)  # 1000 remote calls

# Good: Batch transfers
results = worker.run_batch.remote(range(1000))  # 1 remote call
```

### GPU Memory Management

```python
# Clear cache between iterations
torch.cuda.empty_cache()

# Use gradient checkpointing for large models
model.gradient_checkpointing_enable()
```

### CPU Affinity

```bash
# Pin workers to specific CPU cores
numactl --cpunodebind=0 --membind=0 python worker.py
```

## Scaling Guidelines

### Horizontal Scaling (More Machines)

| Machines | GPUs | Expected Time | Communication Overhead |
|----------|------|---------------|----------------------|
| 1 | 10 | 50 min | 0% |
| 2 | 20 | 25 min | 5-10% |
| 4 | 40 | 12.5 min | 10-15% |
| 10 | 100 | 5 min | 15-20% |

### Vertical Scaling (More GPUs per Machine)

| GPUs/Machine | Optimal Workers | Memory/Worker |
|--------------|----------------|---------------|
| 2-4 | 2-4 | 16GB |
| 4-8 | 4-8 | 12GB |
| 8-16 | 8-16 | 8GB |

## Troubleshooting

### Common Issues

**Issue**: Workers not utilizing GPUs
```bash
# Check GPU visibility
echo $CUDA_VISIBLE_DEVICES

# Set explicitly
export CUDA_VISIBLE_DEVICES=0,1,2,3
```

**Issue**: Ray cluster connection failed
```bash
# Check Ray status
ray status

# Restart cluster
ray stop
ray start --head
```

**Issue**: Out of memory errors
```bash
# Reduce batch size
--batch-size 5

# Increase object store memory
ray start --head --object-store-memory 20000000000
```

## Best Practices

1. **Start Small**: Test with 2 workers before scaling to 10
2. **Monitor Resources**: Watch CPU, GPU, and memory usage
3. **Use Checkpoints**: Save progress frequently
4. **Profile First**: Identify bottlenecks before optimizing
5. **Test Locally**: Verify single-GPU performance first

## Example: Full Distributed Run

```bash
#!/bin/bash
# distributed_run.sh

# 1. Start Ray cluster
ray start --head --num-gpus=10 --num-cpus=30

# 2. Run distributed benchmark
python scripts/distributed_executor.py \
    --iterations 500 \
    --workers 10 \
    --batch-size 10 \
    --checkpoint-interval 50 \
    --output results/distributed_500.json

# 3. Verify results
python scripts/verify_benchmarks.py results/distributed_500.json

# 4. Shutdown Ray
ray stop
```

## Resource Estimation

### Time Estimates

```
Serial (1 GPU):
  500 iterations × 1 min = 500 min = 8.3 hours

Parallel (10 GPUs):
  50 batches × 1 min = 50 min

Parallel (20 GPUs):
  25 batches × 1 min = 25 min
```

### Cost Estimates (Cloud)

```
AWS p3.2xlarge (1 V100):
  $3.06/hour × 8.3 hours = $25.40

AWS p3.16xlarge (8 V100s):
  $24.48/hour × 1 hour = $24.48

Savings: Minimal cost increase for 8x speedup
```

## References

- [Ray Documentation](https://docs.ray.io/)
- [NVIDIA Multi-GPU Best Practices](https://docs.nvidia.com/deeplearning/)
- [Distributed PyTorch](https://pytorch.org/tutorials/beginner/dist_overview.html)
