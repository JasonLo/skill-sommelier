# GPU and CUDA Support with Pixi

## Overview

Pixi provides excellent support for GPU-accelerated computing with CUDA. This guide covers how to configure your Python projects for GPU workloads using Pixi features and Docker.

## Key Concepts

### Pixi Features

Features in Pixi allow you to define optional dependency groups and system requirements. This is perfect for creating separate CPU and GPU environments.

### System Requirements

The `system-requirements` table tells Pixi what CUDA version is available on the system. This ensures proper dependency resolution for CUDA-enabled packages.

## Basic CUDA Configuration

### Simple CUDA Project

```toml
[project]
name = "gpu-app"
version = "0.1.0"
channels = ["conda-forge"]
platforms = ["linux-64"]

[dependencies]
python = "3.11.*"

[system-requirements]
cuda = "12"

[dependencies]
pytorch-gpu = "*"
```

### Multi-Environment Setup (CPU + GPU)

The recommended approach for maximum flexibility:

```toml
[project]
name = "gpu-app"
channels = ["conda-forge"]
platforms = ["linux-64"]

[dependencies]
python = "3.11.*"
# Shared dependencies
pandas = "*"
numpy = "*"

# CUDA Feature
[feature.cuda.system-requirements]
cuda = "12"

[feature.cuda.dependencies]
pytorch-gpu = "*"
# or: tensorflow-gpu = "*"
# or: jax with jaxlib cuda build

# CPU Feature  
[feature.cpu.dependencies]
pytorch-cpu = "*"

# Define Environments
[environments]
default = ["cuda"]  # GPU by default
gpu = ["cuda"]
cpu = ["cpu"]

[tasks]
train = "python train.py"
infer = "python infer.py"
```

## Running with Different Environments

```bash
# Use default (GPU) environment
pixi run train

# Explicitly use GPU environment
pixi run --environment gpu train

# Use CPU environment
pixi run --environment cpu train

# Check CUDA availability
pixi run python -c "import torch; print(torch.cuda.is_available())"
```

## Docker Integration with CUDA

### Dockerfile with CUDA Support

```dockerfile
# Use CUDA-enabled Pixi base image
FROM ghcr.io/prefix-dev/pixi:latest-cuda-12.6.3 AS builder

WORKDIR /app

# Copy Pixi configuration
COPY pixi.toml pixi.lock ./

# Install GPU environment
RUN pixi install --locked --environment gpu

# Runtime stage with NVIDIA CUDA base
FROM nvidia/cuda:12.6.3-runtime-ubuntu22.04 AS runtime

WORKDIR /app

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Pixi environment
COPY --from=builder /app/.pixi /app/.pixi

# Copy application
COPY app.py .

# Activate environment
ENV PATH="/app/.pixi/envs/default/bin:$PATH"

CMD ["python", "app.py"]
```

### Building and Running

```bash
# Build the image
docker build -t gpu-app .

# Run with GPU access
docker run --gpus all gpu-app

# Run interactively
docker run --gpus all -it gpu-app /bin/bash

# Check GPU inside container
docker run --gpus all gpu-app nvidia-smi
```

### Docker Compose with GPU

```yaml
version: '3.8'

services:
  gpu-app:
    build:
      context: .
      dockerfile: Dockerfile
    image: gpu-app:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - CUDA_VISIBLE_DEVICES=0
```

## Framework-Specific Configuration

### PyTorch

```toml
[feature.cuda.system-requirements]
cuda = "12"

[feature.cuda.dependencies]
pytorch-gpu = "*"
torchvision = "*"
torchaudio = "*"

[feature.cpu.dependencies]
pytorch-cpu = "*"
torchvision = "*"
torchaudio = "*"
```

Test CUDA:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0)}")
```

### TensorFlow

```toml
[feature.cuda.system-requirements]
cuda = "12"

[feature.cuda.dependencies]
tensorflow-gpu = "*"

[feature.cpu.dependencies]
tensorflow-cpu = "*"
```

Test CUDA:
```python
import tensorflow as tf
print(f"GPU devices: {tf.config.list_physical_devices('GPU')}")
```

### JAX

```toml
[feature.cuda.system-requirements]
cuda = "12"

[feature.cuda.dependencies]
jax = "*"
jaxlib = { version = "*", build = "cuda12" }

[feature.cpu.dependencies]
jax = "*"
jaxlib = "*"
```

Test CUDA:
```python
import jax
print(f"Devices: {jax.devices()}")
print(f"Default backend: {jax.default_backend()}")
```

## CUDA Version Management

### Specifying Exact CUDA Version

```toml
[feature.cuda.system-requirements]
cuda = "12.6"

[feature.cuda.dependencies]
cuda-version = "12.6.*"
pytorch-gpu = "*"
```

### Supporting Multiple CUDA Versions

Use separate features:

```toml
[feature.cuda12.system-requirements]
cuda = "12"

[feature.cuda12.dependencies]
pytorch-gpu = "*"

[feature.cuda11.system-requirements]
cuda = "11"

[feature.cuda11.dependencies]
pytorch-gpu = "*"

[environments]
cuda12 = ["cuda12"]
cuda11 = ["cuda11"]
```

## Available CUDA Base Images

Official Pixi CUDA images:
- `ghcr.io/prefix-dev/pixi:latest-cuda-12.6.3`
- `ghcr.io/prefix-dev/pixi:latest-cuda-12.4.1`
- `ghcr.io/prefix-dev/pixi:latest-cuda-11.8.0`

Check [Pixi Docker Registry](https://github.com/prefix-dev/pixi-docker/pkgs/container/pixi) for all available tags.

## HTCondor / HPC Integration

When deploying to HPC systems with job schedulers:

### HTCondor Submit File

```condor
# submit.sub
universe = docker
docker_image = gpu-app:latest

request_gpus = 1
request_cpus = 4
request_memory = 16GB

executable = run.sh
output = logs/job.$(Cluster).$(Process).out
error = logs/job.$(Cluster).$(Process).err
log = logs/job.$(Cluster).$(Process).log

queue 1
```

### SLURM

```bash
#!/bin/bash
#SBATCH --job-name=gpu-job
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

# Load required modules
module load singularity

# Run containerized app
singularity exec --nv docker://gpu-app:latest python app.py
```

## Testing GPU Access

### Quick GPU Test Script

```python
# test_gpu.py
import sys

def test_pytorch():
    try:
        import torch
        available = torch.cuda.is_available()
        device_count = torch.cuda.device_count()
        device_name = torch.cuda.get_device_name(0) if available else "N/A"
        print(f"PyTorch - CUDA: {available}, Devices: {device_count}, Name: {device_name}")
        return available
    except ImportError:
        print("PyTorch not installed")
        return False

def test_tensorflow():
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        print(f"TensorFlow - GPUs: {len(gpus)}, Devices: {gpus}")
        return len(gpus) > 0
    except ImportError:
        print("TensorFlow not installed")
        return False

def test_jax():
    try:
        import jax
        devices = jax.devices()
        backend = jax.default_backend()
        print(f"JAX - Backend: {backend}, Devices: {devices}")
        return backend == 'gpu'
    except ImportError:
        print("JAX not installed")
        return False

if __name__ == '__main__':
    print("=== GPU Detection Test ===")
    results = []
    results.append(test_pytorch())
    results.append(test_tensorflow())
    results.append(test_jax())
    
    if any(results):
        print("\n✅ GPU access confirmed")
        sys.exit(0)
    else:
        print("\n❌ No GPU access detected")
        sys.exit(1)
```

Run:
```bash
pixi run python test_gpu.py
docker run --gpus all gpu-app python test_gpu.py
```

## Troubleshooting

### CUDA Not Detected

**Problem**: `torch.cuda.is_available()` returns `False`

**Solutions**:
1. Verify NVIDIA drivers: `nvidia-smi`
2. Check Docker GPU support: `docker run --gpus all nvidia/cuda:12.6.3-base-ubuntu22.04 nvidia-smi`
3. Ensure `--gpus all` flag when running container
4. Verify system-requirements in pixi.toml
5. Check NVIDIA Container Toolkit is installed

### Wrong CUDA Version

**Problem**: Package expects different CUDA version

**Solutions**:
1. Match `system-requirements.cuda` with installed CUDA
2. Use `cuda-version` package to pin exact version
3. Check package compatibility with `pixi list`

### Memory Issues

**Problem**: Out of memory errors

**Solutions**:
1. Reduce batch size
2. Enable gradient checkpointing
3. Use mixed precision training
4. Limit CUDA memory: `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512`

### Build Issues

**Problem**: Docker build fails with CUDA packages

**Solutions**:
1. Use CUDA-enabled base image
2. Ensure `pixi.lock` is committed
3. Build on machine with GPU or use `CONDA_OVERRIDE_CUDA`

## Best Practices

1. **Always specify CUDA version** in system-requirements
2. **Use features** for CPU/GPU separation
3. **Test both environments** before deployment
4. **Pin cuda-version** for reproducibility
5. **Use official CUDA base images** in Docker
6. **Include GPU tests** in CI/CD (with CPU fallback)
7. **Document GPU requirements** in README
8. **Monitor GPU memory** usage in production

## Resources

- [Pixi CUDA Documentation](https://pixi.sh/latest/workspace/system_requirements/)
- [Pixi Docker Images](https://github.com/prefix-dev/pixi-docker)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)
- [PyTorch CUDA Guide](https://pytorch.org/get-started/locally/)
- [HTCondor GPU Jobs](https://htcondor.readthedocs.io/en/latest/users-manual/gpus.html)
