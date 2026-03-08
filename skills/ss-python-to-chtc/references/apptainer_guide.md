# Apptainer/Singularity Integration

## Overview

Apptainer (formerly Singularity) is a container platform designed for HPC and scientific computing. It's the standard on many university clusters and supercomputers where Docker isn't available due to security constraints.

## Why Apptainer for HPC?

### Advantages over Docker on HPC
- **No root daemon**: Runs without privileged processes
- **User namespaces**: Better security model for shared systems
- **HPC-friendly**: Designed for batch schedulers (SLURM, HTCondor, PBS)
- **MPI support**: Native integration with HPC message passing
- **GPU support**: Simple --nv flag for NVIDIA GPUs
- **File system**: Direct access to host filesystems

### When to Use Apptainer
✅ University HPC clusters  
✅ National supercomputing centers  
✅ Shared computing resources  
✅ Systems without root access  
✅ SLURM/HTCondor environments  

## Docker to Apptainer Conversion

### Method 1: Using the apptainerize.py Script

**Quick Conversion:**
```bash
# Convert Docker image to .sif
python apptainerize.py convert my-app:latest myapp.sif

# With force overwrite
python apptainerize.py convert my-app:latest myapp.sif --force

# From remote registry
python apptainerize.py convert ghcr.io/user/app:tag app.sif
```

**Generate Bash Script:**
```bash
# Create standalone conversion script
python apptainerize.py script --output apptainerize.sh

# Then use it anywhere
./apptainerize.sh my-app:latest myapp.sif
```

**Generate Definition File:**
```bash
# Create .def file for custom builds
python apptainerize.py def ubuntu:22.04 app.py --output myapp.def

# With CUDA support
python apptainerize.py def ubuntu:22.04 train.py --cuda --output gpu-app.def
```

### Method 2: Direct Apptainer Commands

**From Docker Hub:**
```bash
apptainer build myapp.sif docker://my-app:latest
```

**From Docker daemon:**
```bash
apptainer build myapp.sif docker-daemon://my-app:latest
```

**From Docker archive:**
```bash
docker save my-app:latest -o myapp.tar
apptainer build myapp.sif docker-archive://myapp.tar
```

**From GitHub Container Registry:**
```bash
apptainer build myapp.sif docker://ghcr.io/username/repo:tag
```

## Apptainer Definition Files

### Basic .def File

```def
Bootstrap: docker
From: python:3.11-slim

%labels
    Author Your Name
    Version 1.0.0

%help
    This container runs a Python application.
    
    Usage:
        apptainer run app.sif
        apptainer exec app.sif python script.py

%files
    app.py /app/
    requirements.txt /app/

%post
    # Install dependencies
    cd /app
    pip install --no-cache-dir -r requirements.txt

%environment
    export LC_ALL=C
    export PATH=/app:$PATH

%runscript
    cd /app
    python app.py "$@"

%test
    python --version
    cd /app && python -c "import sys; print('Test passed')"
```

### CUDA-Enabled .def File

```def
Bootstrap: docker
From: nvidia/cuda:12.6.3-runtime-ubuntu22.04

%labels
    Author Your Name
    Version 1.0.0
    CUDA 12.6.3

%help
    GPU-accelerated Python application.
    
    Usage:
        apptainer run --nv app.sif
        apptainer exec --nv app.sif python train.py

%post
    # Install Python and ML libraries
    apt-get update
    apt-get install -y python3 python3-pip
    
    pip3 install --no-cache-dir \
        torch \
        torchvision \
        numpy \
        pandas

%environment
    export CUDA_VISIBLE_DEVICES=0
    export PATH=/usr/local/cuda/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

%runscript
    python3 train.py "$@"

%test
    python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Pixi-Based .def File

```def
Bootstrap: docker
From: ghcr.io/prefix-dev/pixi:latest

%files
    pixi.toml /app/
    pixi.lock /app/
    app.py /app/

%post
    cd /app
    pixi install --locked

%environment
    export PATH=/app/.pixi/envs/default/bin:$PATH

%runscript
    cd /app
    python app.py "$@"
```

## Building Apptainer Images

### On Systems with Root/Sudo

```bash
# Build from definition file
sudo apptainer build myapp.sif myapp.def

# Build from Docker
sudo apptainer build myapp.sif docker://my-app:latest

# Build with specific options
sudo apptainer build --force --sandbox myapp/ docker://my-app:latest
```

### On Systems without Root (Remote Build)

```bash
# Use Sylabs Cloud for building
apptainer build --remote myapp.sif myapp.def

# Or build locally in user namespace (if supported)
apptainer build --fakeroot myapp.sif myapp.def
```

## Running Apptainer Containers

### Basic Execution

```bash
# Run the container's runscript
apptainer run myapp.sif

# Execute specific command
apptainer exec myapp.sif python script.py

# Interactive shell
apptainer shell myapp.sif

# Run with arguments
apptainer run myapp.sif --arg1 value1 --arg2 value2
```

### With GPU Support

```bash
# Enable NVIDIA GPUs
apptainer run --nv myapp.sif

# Execute with GPU
apptainer exec --nv myapp.sif python train.py

# Check GPU access
apptainer exec --nv myapp.sif nvidia-smi
```

### Binding Directories

```bash
# Mount host directory
apptainer run --bind /data:/mnt/data myapp.sif

# Multiple binds
apptainer run \
    --bind /data:/data \
    --bind /scratch:/scratch \
    myapp.sif

# Short form
apptainer run -B /data:/data myapp.sif
```

## HPC Integration

### SLURM Example

```bash
#!/bin/bash
#SBATCH --job-name=ml-training
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=24:00:00

module load apptainer

# Run with GPU
apptainer exec --nv \
    --bind $SCRATCH:/scratch \
    myapp.sif \
    python train.py \
        --data /scratch/data \
        --output /scratch/results
```

### HTCondor Example

```condor
# submit.sub
universe = vanilla
executable = run_apptainer.sh

request_cpus = 4
request_memory = 16GB
request_gpus = 1

output = logs/job.$(Cluster).$(Process).out
error = logs/job.$(Cluster).$(Process).err
log = logs/job.$(Cluster).$(Process).log

queue 1
```

```bash
#!/bin/bash
# run_apptainer.sh
apptainer exec --nv myapp.sif python train.py
```

### PBS/Torque Example

```bash
#!/bin/bash
#PBS -N ml-training
#PBS -l nodes=1:ppn=8:gpus=1
#PBS -l walltime=24:00:00
#PBS -l mem=32gb

cd $PBS_O_WORKDIR

apptainer exec --nv \
    --bind /scratch:/scratch \
    myapp.sif \
    python train.py
```

## Complete Workflow Example

### 1. Create Application Locally with Docker

```bash
# Generate Docker config with our skill
python dockerize_python.py train.py ./app --cuda 12

# Build Docker image
cd app
docker build -t ml-training:v1 .

# Test locally
docker run --gpus all ml-training:v1
```

### 2. Convert to Apptainer

```bash
# Method A: Direct conversion
apptainer build ml-training.sif docker-daemon://ml-training:v1

# Method B: Push to registry, then pull
docker tag ml-training:v1 ghcr.io/user/ml-training:v1
docker push ghcr.io/user/ml-training:v1
apptainer build ml-training.sif docker://ghcr.io/user/ml-training:v1

# Method C: Use our script
python apptainerize.py convert ml-training:v1 ml-training.sif
```

### 3. Transfer to HPC

```bash
# Copy to cluster
scp ml-training.sif user@cluster.edu:/home/user/

# Or pull directly on cluster
ssh user@cluster.edu
apptainer build ml-training.sif docker://ghcr.io/user/ml-training:v1
```

### 4. Submit Job

```bash
# Create SLURM script
cat > submit.sh << 'EOF'
#!/bin/bash
#SBATCH --gres=gpu:1
apptainer exec --nv ml-training.sif python train.py
EOF

# Submit
sbatch submit.sh
```

## Advanced Features

### Overlay Filesystems

For read-write layers on top of read-only .sif:

```bash
# Create overlay
dd if=/dev/zero of=overlay.img bs=1M count=500
mkfs.ext3 overlay.img

# Use overlay
apptainer run --overlay overlay.img myapp.sif
```

### Instances (Persistent Containers)

```bash
# Start instance
apptainer instance start myapp.sif myapp-instance

# Execute in instance
apptainer exec instance://myapp-instance python script.py

# Stop instance
apptainer instance stop myapp-instance
```

### Environment Variables

```bash
# Set environment variables
apptainer exec --env VAR=value myapp.sif python script.py

# Pass all host environment
apptainer exec --cleanenv=false myapp.sif python script.py
```

## Pixi + Apptainer Workflow

### Generate Pixi-based Apptainer Image

```bash
# 1. Create Pixi project with our skill
python dockerize_python.py app.py ./pixi-app

# 2. Build Docker image with Pixi
cd pixi-app
docker build -t pixi-app:v1 .

# 3. Convert to Apptainer
apptainer build pixi-app.sif docker-daemon://pixi-app:v1

# 4. Run with all dependencies
apptainer run pixi-app.sif
```

### Direct .def File with Pixi

```def
Bootstrap: docker
From: ghcr.io/prefix-dev/pixi:latest

%files
    pixi.toml /app/
    app.py /app/

%post
    cd /app
    pixi install

%environment
    export PATH=/app/.pixi/envs/default/bin:$PATH

%runscript
    cd /app && pixi run start
```

## Troubleshooting

### Issue: Permission Denied

**Problem:** Can't write to mounted directories

**Solution:**
```bash
# Ensure directory permissions
chmod 755 /path/to/mount

# Or use --no-home to avoid home mounting issues
apptainer run --no-home myapp.sif
```

### Issue: GPU Not Detected

**Problem:** CUDA not available inside container

**Solution:**
```bash
# Check host GPU
nvidia-smi

# Use --nv flag
apptainer exec --nv myapp.sif nvidia-smi

# Check CUDA environment
apptainer exec --nv myapp.sif printenv | grep CUDA
```

### Issue: Module Not Found

**Problem:** Python can't find installed packages

**Solution:**
```bash
# Check Python path
apptainer exec myapp.sif python -c "import sys; print(sys.path)"

# Verify installation
apptainer exec myapp.sif pip list

# Rebuild if needed
sudo apptainer build --force myapp.sif myapp.def
```

### Issue: Cannot Build without Root

**Problem:** No sudo access on cluster

**Solution:**
```bash
# Use remote build (requires Sylabs account)
apptainer build --remote myapp.sif myapp.def

# Or use fakeroot (if available)
apptainer build --fakeroot myapp.sif myapp.def

# Or build locally and transfer
```

## Best Practices

1. **Build Images Locally**: Build and test on your laptop, then transfer
2. **Use Latest Apptainer**: Keep Apptainer updated for security and features
3. **Bind Mounts**: Use --bind for data, don't copy large files into image
4. **GPU Testing**: Always test GPU access before long jobs
5. **Documentation**: Include %help section in .def files
6. **Version Control**: Tag images with versions
7. **Size Optimization**: Use multi-stage Docker builds before converting
8. **Reproducibility**: Use Pixi + lock files for dependency management

## Comparison: Docker vs Apptainer

| Feature | Docker | Apptainer |
|---------|--------|-----------|
| Root required | Yes (daemon) | No |
| HPC friendly | Limited | Excellent |
| Security model | Namespace isolation | User namespace |
| GPU support | --gpus flag | --nv flag |
| MPI support | Complex | Native |
| File access | Volumes | Direct mount |
| Image format | layers | .sif (SquashFS) |
| Build location | Anywhere | May need root |

## Resources

- [Apptainer Documentation](https://apptainer.org/docs/)
- [Sylabs Cloud](https://cloud.sylabs.io/) - Remote building
- [Apptainer on NERSC](https://docs.nersc.gov/development/shifter/how-to-use/)
- [Apptainer GPU Guide](https://apptainer.org/docs/user/main/gpu.html)
- [Definition File Reference](https://apptainer.org/docs/user/main/definition_files.html)
