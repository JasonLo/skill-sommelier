#!/usr/bin/env python3
"""
Analyzes Python scripts and generates complete Docker containerization setup with Pixi.
Handles dependency detection, multi-stage builds, and production best practices.
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Set, Dict, Optional


class PythonAnalyzer:
    """Analyzes Python code to detect dependencies and requirements."""
    
    STDLIB_MODULES = {
        'abc', 'argparse', 'array', 'ast', 'asyncio', 'base64', 'bisect', 'calendar',
        'collections', 'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'email',
        'enum', 'functools', 'glob', 'gzip', 'hashlib', 'heapq', 'html', 'http',
        'inspect', 'io', 'itertools', 'json', 'logging', 'math', 'multiprocessing',
        'operator', 'os', 'pathlib', 'pickle', 're', 'random', 'shutil', 'socket',
        'sqlite3', 'statistics', 'string', 'struct', 'subprocess', 'sys', 'tempfile',
        'threading', 'time', 'typing', 'unittest', 'urllib', 'uuid', 'warnings',
        'weakref', 'xml', 'zipfile', '__future__'
    }
    
    def __init__(self, script_path: Path):
        self.script_path = script_path
        self.imports: Set[str] = set()
        self.has_main = False
        self.uses_cli = False
        
    def analyze(self) -> Dict:
        """Analyze the Python script and return findings."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
            self._extract_imports(tree)
            self._check_main(tree)
            self._check_cli(tree)
        except SyntaxError as e:
            print(f"Warning: Could not parse {self.script_path}: {e}", file=sys.stderr)
            
        # Filter out stdlib modules
        external_deps = {imp for imp in self.imports if imp.split('.')[0] not in self.STDLIB_MODULES}
        
        return {
            'dependencies': sorted(external_deps),
            'has_main': self.has_main,
            'uses_cli': self.uses_cli,
            'script_name': self.script_path.name
        }
    
    def _extract_imports(self, tree: ast.AST):
        """Extract all import statements."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.add(node.module)
    
    def _check_main(self, tree: ast.AST):
        """Check if script has if __name__ == '__main__' pattern."""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Compare):
                    if (isinstance(node.test.left, ast.Name) and 
                        node.test.left.id == '__name__'):
                        self.has_main = True
                        return
    
    def _check_cli(self, tree: ast.AST):
        """Check if script uses CLI argument parsing."""
        cli_modules = {'argparse', 'click', 'typer', 'fire'}
        if self.imports & cli_modules:
            self.uses_cli = True


class DockerGenerator:
    """Generates Docker configuration files with Pixi support."""
    
    def __init__(self, analysis: Dict, python_version: str = "3.11", use_pixi: bool = True, 
                 cuda_version: Optional[str] = None):
        self.analysis = analysis
        self.python_version = python_version
        self.use_pixi = use_pixi
        self.cuda_version = cuda_version
        
    def generate_dockerfile(self) -> str:
        """Generate optimized Dockerfile with Pixi."""
        if self.use_pixi:
            return self._pixi_dockerfile()
        return self._pip_dockerfile()
    
    def _pixi_dockerfile(self) -> str:
        """Generate Dockerfile using Pixi for dependency management."""
        script = self.analysis['script_name']
        
        # Select appropriate base image
        if self.cuda_version:
            # Use CUDA-enabled Pixi base image
            base_image = f"ghcr.io/prefix-dev/pixi:latest-cuda-{self.cuda_version}"
            runtime_base = "nvidia/cuda:12.6.3-runtime-ubuntu22.04"
        else:
            base_image = "ghcr.io/prefix-dev/pixi:latest"
            runtime_base = "ubuntu:22.04"
        
        dockerfile = f"""# Build stage with Pixi
FROM {base_image} AS builder

WORKDIR /app

# Copy Pixi configuration
COPY pixi.toml pixi.lock* ./

# Install dependencies in the environment
# Use --environment flag to select GPU or CPU environment
RUN pixi install --locked

# Runtime stage
FROM {runtime_base} AS runtime

WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/*

# Copy the Pixi environment from builder
COPY --from=builder /app/.pixi /app/.pixi

# Copy application code
COPY {script} .

# Activate Pixi environment and run
ENV PATH="/app/.pixi/envs/default/bin:$PATH"
CMD ["python", "{script}"]
"""
        return dockerfile
    
    def _pip_dockerfile(self) -> str:
        """Generate traditional pip-based Dockerfile (fallback)."""
        deps = self.analysis['dependencies']
        script = self.analysis['script_name']
        
        dockerfile = f"""# Build stage
FROM python:{self.python_version}-slim as builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:{self.python_version}-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY {script} .

# Run the script
CMD ["python", "{script}"]
"""
        return dockerfile
    
    def generate_pixi_toml(self) -> str:
        """Generate pixi.toml configuration file."""
        deps = self.analysis['dependencies']
        script = self.analysis['script_name']
        
        # Detect if PyTorch, TensorFlow, or other GPU libraries are present
        gpu_libs = {'torch', 'pytorch', 'tensorflow', 'jax', 'jaxlib'}
        has_gpu_deps = bool(set(deps) & gpu_libs)
        
        # Build dependencies section
        deps_section = ""
        if deps:
            deps_section = "\n".join([f'{dep} = "*"' for dep in deps])
        else:
            deps_section = "# No external dependencies detected"
        
        toml = f"""[project]
name = "app"
version = "0.1.0"
description = "Containerized Python application"
channels = ["conda-forge"]
platforms = ["linux-64"]

[dependencies]
python = "{self.python_version}.*"
{deps_section}
"""
        
        # Add CUDA feature if requested or GPU libraries detected
        if self.cuda_version or has_gpu_deps:
            cuda_ver = self.cuda_version or "12"
            toml += f"""
[feature.cuda.system-requirements]
cuda = "{cuda_ver}"

[feature.cuda.dependencies]
# Add GPU-specific dependencies here
# For example: pytorch-gpu = "*" or tensorflow-gpu = "*"

[feature.cpu.dependencies]
# Add CPU-specific dependencies here  
# For example: pytorch-cpu = "*"

[environments]
# Default environment includes CUDA support
default = ["cuda"]
cpu = ["cpu"]
"""
        
        toml += f"""
[tasks]
start = "python {script}"
"""
        return toml
    
    def generate_requirements(self) -> str:
        """Generate requirements.txt content (for pip fallback)."""
        deps = self.analysis['dependencies']
        if not deps:
            return "# No external dependencies detected\n"
        
        content = "# Auto-generated requirements\n"
        content += "# Specify versions for production use\n\n"
        content += "\n".join(deps)
        return content
    
    def generate_dockerignore(self) -> str:
        """Generate .dockerignore file."""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Pixi
.pixi/
pixi.lock

# Distribution / packaging
dist/
build/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Documentation
*.md
docs/

# Docker
Dockerfile
.dockerignore
docker-compose.yml
"""
    
    def generate_compose(self, service_name: str = "app") -> str:
        """Generate docker-compose.yml for easy orchestration."""
        script = self.analysis['script_name']
        
        return f"""version: '3.8'

services:
  {service_name}:
    build:
      context: .
      dockerfile: Dockerfile
    image: {service_name}:latest
    container_name: {service_name}
    restart: unless-stopped
    # Uncomment to mount volumes
    # volumes:
    #   - ./data:/app/data
    # Uncomment to expose ports
    # ports:
    #   - "8000:8000"
    # Uncomment to set environment variables
    # environment:
    #   - ENV_VAR=value
"""

    def generate_apptainerize_script(self) -> str:
        """Generate bash script for converting Docker image to Apptainer .sif."""
        script = self.analysis['script_name']
        
        return """#!/bin/bash
# apptainerize.sh - Build an Apptainer/Singularity image from a Docker image
#
# Usage:
#   ./apptainerize.sh <docker-image> <output-sif-file>
#
# Arguments:
#   docker-image     - Docker image name (e.g., my-app:latest or ghcr.io/owner/repo:tag)
#                      The docker:// prefix is optional and will be added automatically
#   output-sif-file  - Path to the output .sif file (e.g., myimage.sif)
#
# Example:
#   ./apptainerize.sh my-app:latest myapp.sif
#   ./apptainerize.sh ghcr.io/owner/repo:tag repo.sif
#
# Requirements:
#   - Apptainer must be installed
#
set -e

DOCKER_SOURCE=$1
SIF_TARGET=$2

# Validate arguments
if [ -z "$DOCKER_SOURCE" ] || [ -z "$SIF_TARGET" ]; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 <docker-image> <output-sif-file>"
    echo "Example: $0 my-app:latest myapp.sif"
    exit 1
fi

# Add docker:// prefix if not present
if [[ ! "$DOCKER_SOURCE" =~ ^docker:// ]]; then
    DOCKER_SOURCE="docker://${DOCKER_SOURCE}"
fi

# Ensure Apptainer is installed
if ! command -v apptainer &> /dev/null; then
    echo "Apptainer is not installed. Please install it first."
    echo ""
    echo "Installation instructions:"
    echo "  Ubuntu/Debian: sudo apt-get install -y apptainer"
    echo "  CentOS/RHEL: sudo yum install -y apptainer"
    echo "  From source: https://apptainer.org/docs/admin/main/installation.html"
    exit 1
fi

# Build the Apptainer image from Docker image
echo "Building Apptainer image from ${DOCKER_SOURCE}..."
apptainer build "${SIF_TARGET}" "${DOCKER_SOURCE}"

echo ""
echo "✅ Apptainer image ${SIF_TARGET} built successfully!"
echo ""
echo "Usage:"
echo "  apptainer run ${SIF_TARGET}"
echo "  apptainer exec ${SIF_TARGET} python """ + script + """"
echo "  apptainer shell ${SIF_TARGET}"
"""

    def generate_apptainer_def(self) -> str:
        """Generate Apptainer definition file."""
        script = self.analysis['script_name']
        deps = self.analysis['dependencies']
        
        if self.cuda_version:
            base_image = "nvidia/cuda:12.6.3-runtime-ubuntu22.04"
            gpu_section = f"""
%labels
    CUDA {self.cuda_version}

%post
    # Install Python and GPU libraries
    apt-get update
    apt-get install -y python3 python3-pip
    
    # Install dependencies
    pip3 install --no-cache-dir {' '.join(deps) if deps else 'numpy pandas'}

%environment
    export CUDA_VISIBLE_DEVICES=0
    export PATH=/usr/local/cuda/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
"""
            help_text = f"""
    GPU-accelerated application.
    
    Usage:
        apptainer run --nv app.sif
        apptainer exec --nv app.sif python {script}
"""
        else:
            base_image = "python:3.11-slim"
            gpu_section = f"""
%post
    # Install dependencies
    pip install --no-cache-dir {' '.join(deps) if deps else 'numpy pandas'}
"""
            help_text = f"""
    Python application.
    
    Usage:
        apptainer run app.sif
        apptainer exec app.sif python {script}
"""
        
        return f"""Bootstrap: docker
From: {base_image}

%labels
    Author Your Name
    Version 1.0.0

%help{help_text}

%files
    {script} /app/

{gpu_section}

%runscript
    cd /app
    python {script} "$@"

%test
    python --version
    cd /app && python -c "import sys; print('Test passed')"
"""

    def generate_htcondor_submit(self) -> str:
        """Generate HTCondor submit file for CHTC."""
        script = self.analysis['script_name']
        
        # Determine container image format
        # Users should update this with their actual image name
        container_line = "# TODO: Update with your actual container image\n"
        container_line += "# For GitHub Container Registry (ORAS):\n"
        container_line += "# container_image = oras://ghcr.io/username/repo:tag\n"
        container_line += "# For Docker Hub:\n"
        container_line += "# container_image = docker://username/repo:tag\n"
        container_line += "container_image         = docker://my-app:latest"
        
        # GPU settings
        gpu_section = ""
        if self.cuda_version:
            gpu_section = """
# GPU settings
request_gpus            = 1
require_gpus            = GlobalMemoryMb >= 8000
+WantGPULab             = true
+GPUJobLength           = "short"
Requirements            = (Target.CUDADriverVersion >= 12.0)
"""
        
        # Important tips section
        tips_section = """
# ============================================================================
# IMPORTANT TIPS FOR CHTC USERS
# ============================================================================
#
# 1. JOB LENGTH & CHECKPOINTING:
#    - "short" GPU jobs have ~12 hour limit
#    - If your script runs longer, implement checkpointing/resume mechanism
#    - Without checkpointing, jobs may be killed and lose all progress
#    - See: https://chtc.cs.wisc.edu/uw-research-computing/hpc/guides.html
#
# 2. CREDENTIALS & SECRETS:
#    - NEVER put credentials in your script!
#    - Use .env file: transfer_input_files = script.py, .env
#    - Add .env to .gitignore
#    - Load in script: from dotenv import load_dotenv; load_dotenv()
#
# 3. MORE RESOURCES:
#    - CHTC Guides: https://chtc.cs.wisc.edu/uw-research-computing/hpc/guides.html
#    - GPU Jobs: https://chtc.cs.wisc.edu/uw-research-computing/gpu-jobs.html
#    - Get help: chtc@cs.wisc.edu
#
# ============================================================================

"""
        
        return f"""{tips_section}# HTCondor Submit File for CHTC
# Generated for: {script}

JobBatchName            = "python_job_batch"

# Container
{container_line}

# Executable and arguments  
executable              = run.sh
arguments               = $(item)

# File transfer
transfer_input_files    = {script}
# If using .env for credentials, add: {script}, .env
transfer_output_files   = ""

# Logging
stream_output           = true
output                  = condor_log/output.$(Cluster)-$(Process).txt
error                   = condor_log/error.$(Cluster)-$(Process).txt
log                     = condor_log/log.$(Cluster)-$(Process).txt

# Compute resources
request_cpus            = {4 if self.cuda_version else 1}
request_memory          = {16 if self.cuda_version else 4}GB
request_disk            = {50 if self.cuda_version else 10}GB
{gpu_section}
# CHTC and OSPool settings
+WantFlocking           = true
+is_resumable           = true
+want_campus_pools      = true
+want_ospool            = true
+WantGlidein            = true

# Queue jobs
# Option 1: Single job
queue 1

# Option 2: Job array from file (uncomment and create job_list.txt)
# queue item from job_list.txt
"""
    
    def generate_htcondor_run_script(self) -> str:
        """Generate run.sh wrapper for HTCondor."""
        script = self.analysis['script_name']
        
        return f"""#!/bin/bash
# run.sh - Wrapper script for HTCondor job

set -e

echo "=== Job Start ==="
echo "Job ID: ${{CLUSTER}}.${{PROCESS}}"
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo "Arguments: $@"

# Check GPU if available
if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "=== GPU Info ==="
    nvidia-smi
fi

echo ""
echo "=== Python Environment ==="
python --version
python -c "import sys; print(f'Python: {{sys.executable}}')"

echo ""
echo "=== Running Application ==="

# Run the Python script with arguments
python {script} "$@"

EXIT_CODE=$?

echo ""
echo "=== Job Complete ==="
echo "Exit code: $EXIT_CODE"
echo "Date: $(date)"

exit $EXIT_CODE
"""
    
    def generate_htcondor_readme(self) -> str:
        """Generate README for HTCondor submission."""
        return """# HTCondor Submission Guide

## ⚠️ IMPORTANT TIPS

### 1. Job Length & Checkpointing
- **"short" GPU jobs are limited to ~12 hours**
- If your script doesn't have a resume mechanism, jobs may lose all progress if killed
- **RECOMMENDED**: Implement checkpointing to save progress periodically
- Example: Save model checkpoints every N epochs, save processed data incrementally
- For longer jobs, change +GPUJobLength to "medium" or "long" in submit.sub

### 2. Credentials & Secrets
- **NEVER put credentials directly in your script!**
- Use a separate `.env` file for secrets
- Add to transfer_input_files: `script.py, .env`
- Add `.env` to your `.gitignore`
- Load in script: `from dotenv import load_dotenv; load_dotenv()`

### 3. More Resources
- CHTC Guides: https://chtc.cs.wisc.edu/uw-research-computing/hpc/guides.html
- GPU Jobs: https://chtc.cs.wisc.edu/uw-research-computing/gpu-jobs.html
- Support: chtc@cs.wisc.edu

## Quick Start

1. **Update container image** in `submit.sub`
2. **Review tips above** (especially checkpointing!)
3. **Create log directory**: `mkdir -p condor_log`
4. **Submit job**: `condor_submit submit.sub`
5. **Monitor**: `condor_q`
"""
    
    def generate_env_example(self) -> str:
        """Generate .env.example file for credentials."""
        return """# Environment Variables for CHTC Jobs
# Copy this file to .env and fill in your actual credentials
# DO NOT commit .env to git!

# API Keys
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Database Credentials
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password

# Cloud Storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET=your_s3_bucket_name

# Other Credentials
# Add any other secrets your application needs
"""
    
    def generate_gitignore(self) -> str:
        """Generate .gitignore for the project."""
        return """# Environment variables (IMPORTANT!)
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Pixi
.pixi/
pixi.lock

# HTCondor logs
condor_log/
*.out
*.err
*.log

# Docker
*.tar
*.tar.gz

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Output files
output/
results/
checkpoints/
*.pkl
*.pth
*.h5
"""
    
    def generate_pixi_instructions(self) -> str:
        script = self.analysis['script_name']
        has_cuda = bool(self.cuda_version)
        
        cuda_section = ""
        if has_cuda:
            cuda_section = f"""
## GPU/CUDA Support

This project includes CUDA {self.cuda_version} support for GPU acceleration.

### Running with GPU
```bash
# Use default environment (includes CUDA)
pixi run start

# Or explicitly specify CUDA environment
pixi run --environment default start

# Check CUDA availability
pixi run python -c "import torch; print(torch.cuda.is_available())"
```

### Running on CPU
```bash
# Use CPU-only environment
pixi run --environment cpu start
```

### Docker with GPU
```bash
# Build with CUDA support
docker build -t my-app .

# Run with GPU access
docker run --gpus all my-app

# Test GPU inside container
docker run --gpus all my-app python -c "import torch; print(torch.cuda.is_available())"
```
"""
        
        return f"""# Pixi Development Instructions

## Local Development (without Docker)

### Install Pixi
```bash
# macOS/Linux
curl -fsSL https://pixi.sh/install.sh | bash

# Windows
iwr -useb https://pixi.sh/install.ps1 | iex
```

### Setup and Run
```bash
# Install dependencies
pixi install

# Run the application
pixi run start

# Or activate the environment
pixi shell
python {script}
```
{cuda_section}
## Docker Development

### Build and Run
```bash
# Build the image
docker build -t my-app .

# Run the container
docker run my-app

# Or use docker-compose
docker-compose up
```

## Benefits of Pixi

✅ **Reproducible**: Lock file ensures exact same dependencies everywhere
✅ **Fast**: Uses conda-forge packages (pre-compiled binaries)
✅ **Cross-platform**: Works on Linux, macOS, Windows
✅ **No virtual env management**: Pixi handles everything
✅ **Task runner**: Built-in task definitions in pixi.toml
✅ **Multi-environment**: Separate CPU and GPU environments

## Adding Dependencies

```bash
# Add a new package
pixi add numpy

# Add with specific version
pixi add "pandas>=2.0"

# Add from PyPI
pixi add --pypi requests

# Add to specific environment
pixi add --feature cuda pytorch-gpu
pixi add --feature cpu pytorch-cpu
```

## Updating Dependencies

```bash
# Update all packages
pixi update

# Update specific package
pixi update numpy
```

## Working with Features

This project uses Pixi features to support multiple environments:

```bash
# List available environments
pixi info

# Install specific environment
pixi install --environment cpu

# Run task in specific environment  
pixi run --environment cpu start
```
"""


def main():
    """Main entry point for the dockerization tool."""
    if len(sys.argv) < 2:
        print("Usage: python dockerize_python.py <script.py> [output_dir] [--no-pixi] [--cuda VERSION]")
        sys.exit(1)
    
    script_path = Path(sys.argv[1])
    
    # Parse arguments
    output_dir = Path.cwd()
    use_pixi = True
    cuda_version = None
    
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == '--no-pixi':
            use_pixi = False
        elif arg == '--cuda' and i + 1 < len(sys.argv):
            cuda_version = sys.argv[i + 1]
        elif not arg.startswith('--') and output_dir == Path.cwd():
            output_dir = Path(arg)
    
    if not script_path.exists():
        print(f"Error: {script_path} not found")
        sys.exit(1)
    
    print(f"🐳 Analyzing {script_path.name}...")
    analyzer = PythonAnalyzer(script_path)
    analysis = analyzer.analyze()
    
    print(f"📦 Found {len(analysis['dependencies'])} external dependencies")
    if analysis['dependencies']:
        print(f"   Dependencies: {', '.join(analysis['dependencies'])}")
    
    dependency_manager = "Pixi" if use_pixi else "pip"
    cuda_info = f" with CUDA {cuda_version}" if cuda_version else ""
    print(f"🔨 Generating Docker configuration with {dependency_manager}{cuda_info}...")
    generator = DockerGenerator(analysis, use_pixi=use_pixi, cuda_version=cuda_version)
    
    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate files
    files = {
        'Dockerfile': generator.generate_dockerfile(),
        '.dockerignore': generator.generate_dockerignore(),
        '.gitignore': generator.generate_gitignore(),
        'docker-compose.yml': generator.generate_compose(),
        'apptainerize.sh': generator.generate_apptainerize_script(),
        'Apptainer.def': generator.generate_apptainer_def(),
        'submit.sub': generator.generate_htcondor_submit(),
        'run.sh': generator.generate_htcondor_run_script(),
        '.env.example': generator.generate_env_example(),
        'HTCONDOR_QUICK_START.txt': generator.generate_htcondor_readme()
    }
    
    if use_pixi:
        files['pixi.toml'] = generator.generate_pixi_toml()
        files['PIXI_INSTRUCTIONS.md'] = generator.generate_pixi_instructions()
    else:
        files['requirements.txt'] = generator.generate_requirements()
    
    for filename, content in files.items():
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make scripts executable
        if filename in ['apptainerize.sh', 'run.sh']:
            filepath.chmod(0o755)
        
        print(f"   ✅ Created {filename}")
    
    print(f"\n✨ Docker configuration created successfully!")
    
    if use_pixi:
        print(f"\n📝 Next steps with Pixi:")
        print(f"   1. Copy {script_path.name} to {output_dir}")
        print(f"   2. Install Pixi: curl -fsSL https://pixi.sh/install.sh | bash")
        print(f"   3. Run locally: pixi run start")
        if cuda_version:
            print(f"   4. Build Docker: docker build -t my-app .")
            print(f"   5. Run with GPU: docker run --gpus all my-app")
            print(f"   6. Convert to Apptainer: ./apptainerize.sh my-app:latest myapp.sif")
            print(f"   7. Run on HPC: apptainer exec --nv myapp.sif python {script_path.name}")
        else:
            print(f"   4. Or build Docker: docker build -t my-app .")
            print(f"   5. Run container: docker run my-app")
            print(f"   6. Convert to Apptainer: ./apptainerize.sh my-app:latest myapp.sif")
        print(f"\n   See PIXI_INSTRUCTIONS.md for detailed guide!")
    else:
        print(f"\n📝 Next steps with pip:")
        print(f"   1. Review and adjust requirements.txt versions")
        print(f"   2. Copy {script_path.name} to {output_dir}")
        print(f"   3. Build: docker build -t my-app .")
        print(f"   4. Run: docker run my-app")
        print(f"   5. Convert to Apptainer: ./apptainerize.sh my-app:latest myapp.sif")


if __name__ == '__main__':
    main()
