---
name: python-to-chtc
description: Convert Python scripts into production-ready Docker and Apptainer/Singularity containers with Pixi dependency management, automatic detection, multi-stage builds, and best practices. Supports GPU/CUDA configurations, multi-environment setups (CPU/GPU), HTCondor/SLURM integration, and .sif conversion for HPC. Use when users need to containerize Python applications, create Dockerfiles, generate Apptainer images, package Python code for deployment, need container configuration for Python projects, or want GPU-accelerated applications for HPC environments. Supports Pixi and pip workflows. Handles scripts, web apps, workers, services, and ML/data science workloads on Docker, Apptainer, and HPC systems.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Python to CHTC

Convert Python applications into production-ready Docker containers with Pixi dependency management, intelligent analysis, optimized multi-stage builds, GPU/CUDA support, and comprehensive configuration.

## When to Use
- Containerizing a Python script or application for HPC
- Creating Dockerfiles or Apptainer definitions for CHTC/HTCondor
- Packaging Python code with GPU/CUDA support
- Converting pip/conda projects to Pixi-managed containers

## When NOT to Use
- Non-Python applications — this is Python-specific
- Local Docker development without HPC — use standard Docker practices
- Kubernetes deployments — this targets HTCondor/SLURM

## Quick Start

For simple containerization requests (uses Pixi by default):

1. **Identify the Python file**: Locate the main script in uploaded files or working directory
2. **Run the dockerization script**:
   ```bash
   python /mnt/skills/user/python-to-chtc/scripts/dockerize_python.py <script.py> [output_dir]
   ```
3. **Review generated files**: The script creates Dockerfile, pixi.toml, .dockerignore, docker-compose.yml, and PIXI_INSTRUCTIONS.md
4. **Present to user**: Share the generated Docker configuration files

The script automatically:
- Detects external dependencies via AST parsing
- Generates optimized multi-stage Dockerfile with Pixi
- Creates pixi.toml with discovered packages
- Includes .dockerignore for efficient builds
- Provides docker-compose.yml for orchestration
- Generates PIXI_INSTRUCTIONS.md for local development

**For pip-based workflow**: Add `--no-pixi` flag to use traditional requirements.txt

## Workflow Decision Tree

```
User wants to containerize Python code
│
├─ Single script with clear entry point?
│  └─ Use dockerize_python.py script directly
│     └─ Present generated files to user
│
├─ Complex application (multiple files, custom setup)?
│  ├─ Read references/python_patterns.md for app type guidance
│  ├─ Read references/docker_best_practices.md for optimization
│  └─ Create custom Dockerfile based on patterns
│
├─ Existing Dockerfile needs improvement?
│  ├─ Read references/docker_best_practices.md
│  └─ Apply security and optimization recommendations
│
└─ Questions about Docker best practices?
   └─ Consult references/docker_best_practices.md
```

## Common Scenarios

### Scenario 1: Simple Script
User uploads `data_processor.py` and asks to containerize it.

**Actions:**
1. Run: `python dockerize_python.py data_processor.py ./docker_output`
2. Script analyzes imports, detects dependencies (e.g., pandas, requests)
3. Generates optimized multi-stage Dockerfile
4. Creates requirements.txt with detected packages
5. Present all generated files to user

### Scenario 2: Web Application
User has Flask/FastAPI app and needs production Docker setup.

**Actions:**
1. Read `references/python_patterns.md` for web app patterns
2. Run dockerize script as starting point
3. Enhance Dockerfile with:
   - EXPOSE directive for appropriate port
   - Production WSGI server (gunicorn/uvicorn)
   - Health checks
4. Update docker-compose.yml with port mappings
5. Present enhanced configuration

### Scenario 3: GPU/CUDA Application
User has PyTorch/TensorFlow model and needs GPU support.

**Actions:**
1. Read `references/cuda_gpu_support.md` for GPU patterns
2. Run: `python dockerize_python.py model.py ./gpu_output --cuda 12`
3. Script generates:
   - CUDA-enabled Dockerfile with GPU base images
   - pixi.toml with CUDA features and multi-environment support
   - PIXI_INSTRUCTIONS.md with GPU testing commands
4. Present files with instructions for GPU testing
5. Explain how to run with `docker run --gpus all`

### Scenario 4: Custom Requirements
User needs specific Python version, non-root user, or security hardening.

**Actions:**
1. Read `references/docker_best_practices.md` for security patterns
2. Generate base configuration with dockerize script
3. Apply customizations:
   - Adjust base image version
   - Add non-root user creation
   - Include security scanning recommendations
4. Present customized files with explanations

## Generated Files

### Dockerfile
Multi-stage build that:
- Uses builder stage for dependencies
- Copies only necessary artifacts to runtime stage
- Results in smaller final images (50-70% reduction)
- Optimizes layer caching

### requirements.txt
- Lists all detected external dependencies
- Excludes Python standard library modules
- Includes comment to add version pins
- Empty if no external dependencies found

### .dockerignore
Prevents unnecessary files from bloating image:
- Python cache directories
- Virtual environments
- IDE configurations
- Git metadata
- Documentation files

### docker-compose.yml
Orchestration file with:
- Build configuration
- Commented volume mounts
- Commented port mappings
- Commented environment variables
- Ready for customization

## Advanced Patterns

When the basic script isn't sufficient, consult the reference files:

### Complex Applications
Read `references/python_patterns.md` for:
- Different application types (scripts, services, workers)
- Common framework configurations
- Dependency management strategies
- Environment configuration patterns
- File system considerations
- Signal handling for graceful shutdown

### Production Optimization
Read `references/docker_best_practices.md` for:
- Image optimization techniques
- Security hardening (non-root users, secret management)
- Health checks and monitoring
- Resource limits
- Networking patterns
- Debugging and troubleshooting

## Script Capabilities

The `dockerize_python.py` script provides:

**Automatic Detection:**
- External package imports (excludes stdlib)
- CLI frameworks (argparse, click, typer, fire)
- Main execution patterns

**Smart Generation:**
- Multi-stage builds for dependency optimization
- Single-stage option for simpler cases
- Appropriate base image selection
- Efficient layer ordering

**Best Practices:**
- No-cache pip installs
- Proper working directory setup
- Optimized .dockerignore
- Ready-to-use docker-compose configuration

## Troubleshooting

**Dependency detection issues:**
- Script uses AST parsing, may miss dynamic imports
- Review and manually add missing packages to requirements.txt

**Large image sizes:**
- Ensure multi-stage build is used
- Check .dockerignore includes unnecessary files
- Consider using python:slim or python:alpine base

**Permission errors:**
- Add non-root user to Dockerfile (see references/docker_best_practices.md)
- Ensure volumes have correct permissions

**Module not found in container:**
- Verify requirements.txt is complete
- Check that pip install ran successfully
- Ensure Python version compatibility

## Next Steps After Generation

Always inform users of:
1. **Review requirements.txt**: Add version pins for production
2. **Test the build**: `docker build -t app-name .`
3. **Run the container**: `docker run app-name`
4. **Customize as needed**: Adjust ports, volumes, environment variables
5. **Consider**: Add health checks, resource limits, or security hardening

## Resources

### scripts/dockerize_python.py
Automated Python-to-Docker conversion tool. Analyzes Python scripts and generates complete Docker configuration with Pixi (default) or pip (--no-pixi flag). Supports GPU/CUDA with --cuda flag. Automatically generates Apptainer/Singularity conversion files.

### scripts/apptainerize.py
Standalone tool for converting Docker images to Apptainer .sif format, generating .def files, and creating conversion scripts. Three modes: convert, def, and script.

### references/apptainer_guide.md
Comprehensive guide for Apptainer/Singularity containers in HPC environments, covering Docker-to-.sif conversion, definition files, GPU support, SLURM/HTCondor integration, and best practices for scientific computing.

### references/cuda_gpu_support.md
Comprehensive guide for GPU-accelerated computing with CUDA, covering Pixi features, multi-environment setup (CPU/GPU), Docker integration, framework-specific configs (PyTorch, TensorFlow, JAX), and HTCondor/HPC deployment.

### references/pixi_guide.md
Comprehensive guide to Pixi package manager covering installation, commands, Docker integration, features, and migration from pip.

### references/docker_best_practices.md
Comprehensive guide covering image optimization, security, production considerations, networking, and troubleshooting.

### references/python_patterns.md
Python-specific Docker patterns for different application types, dependency management, configuration, and file system handling.
