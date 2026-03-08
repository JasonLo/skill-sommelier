#!/usr/bin/env python3
"""
Generate HTCondor submit files optimized for CHTC and OSPool.
"""

import argparse
from pathlib import Path
from typing import Optional, List


class HTCondorSubmitGenerator:
    """Generates HTCondor submit files for various scenarios."""
    
    def __init__(self, 
                 script_name: str,
                 container_image: str,
                 job_name: str = "python_job",
                 use_gpu: bool = False,
                 use_oras: bool = False):
        self.script_name = script_name
        self.container_image = container_image
        self.job_name = job_name
        self.use_gpu = use_gpu
        self.use_oras = use_oras
        
    def generate_submit_file(self, 
                            cpus: int = 1,
                            memory: str = "4GB",
                            disk: str = "10GB",
                            input_files: Optional[List[str]] = None,
                            output_files: Optional[str] = None,
                            arguments: Optional[str] = None,
                            queue_from: Optional[str] = None) -> str:
        """Generate complete HTCondor submit file."""
        
        # Determine container format
        if self.use_oras:
            container_line = f"container_image         = oras://{self.container_image}"
        else:
            container_line = f"container_image         = docker://{self.container_image}"
        
        # Build input files list
        if input_files is None:
            input_files = [self.script_name]
        input_files_str = ", ".join(input_files)
        
        # Output files
        output_files_str = output_files if output_files else '""'
        
        # Arguments handling
        args_line = ""
        if arguments:
            args_line = f"arguments               = {arguments}"
        elif queue_from:
            args_line = f"arguments               = $(item)"
        
        # GPU settings
        gpu_section = ""
        if self.use_gpu:
            gpu_section = """
# GPU settings
request_gpus            = 1
require_gpus            = GlobalMemoryMb >= 8000
+WantGPULab             = true
+GPUJobLength           = "short"
Requirements            = (Target.CUDADriverVersion >= 12.0)
"""
        
        # Queue directive
        if queue_from:
            queue_line = f"queue item from {queue_from}"
        else:
            queue_line = "queue 1"
        
        submit_file = f"""# HTCondor Submit File for CHTC
# Generated for: {self.script_name}

JobBatchName            = "{self.job_name}"

# Container
{container_line}

# Executable and arguments
executable              = run.sh
{args_line}

# File transfer
transfer_input_files    = {input_files_str}
transfer_output_files   = {output_files_str}

# Logging
stream_output           = true
output                  = condor_log/output.$(Cluster)-$(Process).txt
error                   = condor_log/error.$(Cluster)-$(Process).txt
log                     = condor_log/log.$(Cluster)-$(Process).txt

# Compute resources
request_cpus            = {cpus}
request_memory          = {memory}
request_disk            = {disk}
{gpu_section}
# CHTC and OSPool settings
+WantFlocking           = true
+is_resumable           = true
+want_campus_pools      = true
+want_ospool            = true
+WantGlidein            = true

# Queue jobs
{queue_line}
"""
        return submit_file
    
    def generate_run_script(self, has_args: bool = False) -> str:
        """Generate wrapper run.sh script with HTCondor workarounds."""
        
        if has_args:
            run_script = f"""#!/bin/bash
# run.sh - Wrapper script for HTCondor job
set -euo pipefail

# Arguments passed from submit file
ARGS="$@"

echo "=== Job Start ==="
echo "Arguments: $ARGS"
echo "Hostname: $(hostname)"
echo "Date: $(date)"

# HTCondor workarounds for container environments
export HOME=$_CONDOR_SCRATCH_DIR
export XDG_CACHE_HOME=$_CONDOR_SCRATCH_DIR/.cache

# Pixi environment path workaround for .sif permission issues
export PATH="/workspace/.pixi/envs/default/bin:$PATH"

# Verify Python executable
echo "Python executable: $(which python)"

# Detect and display hardware
echo ""
echo "=== Hardware Detection ==="
lscpu | head -15
echo "Number of CPUs: $(nproc)"

# Check for GPU availability
if nvidia-smi &> /dev/null; then
    echo ""
    echo "=== GPU Information ==="
    nvidia-smi --query-gpu=name --format=csv,noheader | sort | uniq -c
    nvidia-smi | grep "CUDA Version"
else
    echo ""
    echo "No GPU detected or nvidia-smi unavailable"
fi

# Load environment variables from .env if present
if [ -f ".env" ]; then
    echo ""
    echo "=== Loading Environment Variables ==="
    echo "Found .env file - loading environment variables"
    set -a  # Automatically export all variables
    source .env
    set +a
    echo "Environment variables loaded successfully"
else
    echo ""
    echo "No .env file found - continuing without additional environment variables"
fi

echo ""
echo "=== Running Application ==="

# Run the Python script with arguments and measure execution time
time python {self.script_name} $ARGS

echo ""
echo "=== Job Complete ==="
echo "Date: $(date)"
"""
        else:
            run_script = f"""#!/bin/bash
# run.sh - Wrapper script for HTCondor job
set -euo pipefail

echo "=== Job Start ==="
echo "Hostname: $(hostname)"
echo "Date: $(date)"

# HTCondor workarounds for container environments
export HOME=$_CONDOR_SCRATCH_DIR
export XDG_CACHE_HOME=$_CONDOR_SCRATCH_DIR/.cache

# Pixi environment path workaround for .sif permission issues
export PATH="/workspace/.pixi/envs/default/bin:$PATH"

# Verify Python executable
echo "Python executable: $(which python)"

# Detect and display hardware
echo ""
echo "=== Hardware Detection ==="
lscpu | head -15
echo "Number of CPUs: $(nproc)"

# Check for GPU availability
if nvidia-smi &> /dev/null; then
    echo ""
    echo "=== GPU Information ==="
    nvidia-smi --query-gpu=name --format=csv,noheader | sort | uniq -c
    nvidia-smi | grep "CUDA Version"
else
    echo ""
    echo "No GPU detected or nvidia-smi unavailable"
fi

# Load environment variables from .env if present
if [ -f ".env" ]; then
    echo ""
    echo "=== Loading Environment Variables ==="
    echo "Found .env file - loading environment variables"
    set -a  # Automatically export all variables
    source .env
    set +a
    echo "Environment variables loaded successfully"
else
    echo ""
    echo "No .env file found - continuing without additional environment variables"
fi

echo ""
echo "=== Running Application ==="

# Run the Python script and measure execution time
time python {self.script_name}

echo ""
echo "=== Job Complete ==="
echo "Date: $(date)"
"""
        return run_script


def generate_list_file(items: List[str], output_path: str = "job_list.txt") -> str:
    """Generate a list file for queue from."""
    content = "\n".join(items)
    with open(output_path, 'w') as f:
        f.write(content)
    return output_path


def generate_readme() -> str:
    """Generate README for HTCondor submission."""
    return """# HTCondor Job Submission Guide

## Files Generated

1. **submit.sub** - HTCondor submit file
2. **run.sh** - Wrapper script (executable)
3. **job_list.txt** - Input parameter list (if using queue from)

## Environment Variables with .env

The generated `run.sh` script automatically checks for a `.env` file in the job directory and loads environment variables from it if present. This is useful for:

- API keys and credentials
- Configuration parameters
- S3 storage credentials
- Database connection strings
- Application-specific settings

### Using .env Files

1. Create a `.env` file in your job directory:
```bash
# .env
API_KEY=your-api-key-here
S3_BUCKET=my-bucket
DATABASE_URL=postgresql://user:pass@host/db
```

2. Add it to your submit file's input files:
```condor
transfer_input_files = script.py, .env, data.csv
```

3. The `run.sh` script will automatically load these variables before running your Python script

**Security Note**: Be careful with sensitive credentials in .env files. Consider using HTCondor's encrypted input files feature for production secrets.

## Quick Start

### Single Job

```bash
# Create log directory
mkdir -p condor_log

# Submit job
condor_submit submit.sub

# Check status
condor_q

# Check output
tail -f condor_log/output.*.txt
```

### Multiple Jobs with Parameters

```bash
# Create parameter list
cat > job_list.txt << EOF
param1
param2
param3
EOF

# Submit array jobs
condor_submit submit.sub

# Monitor
condor_q -nobatch
```

## CHTC-Specific Features

### GPU Jobs

This submit file is configured for GPU jobs on CHTC:
- Requests 1 GPU with >= 8GB memory
- Requires CUDA 12.0+ driver
- Uses short GPU queue
- Enables WantGPULab for priority

### Flocking and OSPool

The submit file enables:
- `+WantFlocking` - Can run on other HTCondor pools
- `+want_ospool` - Can use OSPool resources
- `+want_campus_pools` - Can use campus resources
- `+WantGlidein` - Can use grid resources

### Resumable Jobs

- `+is_resumable = true` - Jobs can checkpoint and resume

## Container Images

### Using Docker Images

```
container_image = docker://my-image:tag
```

### Using ORAS (GitHub Container Registry)

```
container_image = oras://ghcr.io/user/repo:tag
```

### Using Apptainer .sif Files

Upload .sif to staging:
```bash
# Transfer .sif to staging
scp myapp.sif user@submit.chtc.wisc.edu:/staging/user/

# Update submit file
transfer_input_files = myapp.sif, script.py
```

## Resource Requests

### CPU Jobs
```
request_cpus   = 1-8    # Typical range
request_memory = 4-16GB
request_disk   = 10-100GB
```

### GPU Jobs
```
request_cpus   = 4-8     # More CPUs with GPU
request_memory = 8-32GB  # More memory for GPU work
request_disk   = 50GB+   # Larger datasets
request_gpus   = 1       # 1-4 GPUs
```

## File Transfer

### Input Files
- Listed in `transfer_input_files`
- Automatically transferred to execute node
- Can use http:// or staging:// URLs

### Output Files
- Listed in `transfer_output_files`
- Empty string ("") means all generated files
- Automatically transferred back

### Large Files
For files > 100MB, use:
- CHTC staging area
- HTTP server
- Squid cache

## Monitoring Jobs

```bash
# View queue
condor_q

# View detailed status
condor_q -better-analyze <job_id>

# View completed jobs
condor_history <username>

# Job statistics
condor_q -analyze <job_id>

# Hold reasons
condor_q -hold
```

## Common Issues

### Job Held

Check hold reason:
```bash
condor_q -hold
condor_q -analyze <job_id>
```

Common fixes:
- Increase memory/disk request
- Fix file permissions (chmod +x run.sh)
- Check container image access

### Job Idle

Reasons:
- Waiting for resources
- Requirements not met
- Flocking disabled

Check:
```bash
condor_q -better-analyze <job_id>
```

### File Transfer Errors

- Verify file paths
- Check file sizes (use staging for large files)
- Ensure executable permissions

## Best Practices

1. **Test locally first**
   ```bash
   docker run my-image:tag python script.py
   ```

2. **Start small**
   - Submit 1-2 test jobs
   - Verify output
   - Then scale up

3. **Use job arrays**
   - More efficient than individual jobs
   - Better resource utilization

4. **Monitor resources**
   - Check memory/disk usage
   - Adjust requests as needed

5. **Clean up**
   ```bash
   # Remove old logs
   rm condor_log/*.txt

   # Remove held jobs
   condor_rm -constraint 'JobStatus==5'
   ```

## Resources

- [CHTC Documentation](https://chtc.cs.wisc.edu/)
- [HTCondor Manual](https://htcondor.readthedocs.io/)
- [OSPool Guide](https://osg-htc.org/services/open_science_pool.html)
- [GPU Jobs Guide](https://chtc.cs.wisc.edu/uw-research-computing/gpu-jobs.html)

## Support

- CHTC Help: chtc@cs.wisc.edu
- Office Hours: Check CHTC website
- Slack: UW-Madison research computing
"""


def main():
    parser = argparse.ArgumentParser(
        description='Generate HTCondor submit files for CHTC'
    )
    
    parser.add_argument('script', help='Python script to run')
    parser.add_argument('--image', required=True, 
                       help='Container image (e.g., my-app:latest or ghcr.io/user/repo:tag)')
    parser.add_argument('--job-name', default='python_job',
                       help='Job batch name')
    parser.add_argument('--oras', action='store_true',
                       help='Use ORAS format (GitHub Container Registry)')
    parser.add_argument('--gpu', action='store_true',
                       help='Request GPU resources')
    parser.add_argument('--cpus', type=int, default=1,
                       help='Number of CPUs')
    parser.add_argument('--memory', default='4GB',
                       help='Memory request (e.g., 4GB, 16GB)')
    parser.add_argument('--disk', default='10GB',
                       help='Disk space request')
    parser.add_argument('--input-files', nargs='+',
                       help='Additional input files to transfer')
    parser.add_argument('--output-files', 
                       help='Output files to transfer back')
    parser.add_argument('--arguments',
                       help='Arguments to pass to script')
    parser.add_argument('--queue-from',
                       help='File with list of parameters for job array')
    parser.add_argument('--output-dir', default='.',
                       help='Output directory for generated files')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    generator = HTCondorSubmitGenerator(
        script_name=args.script,
        container_image=args.image,
        job_name=args.job_name,
        use_gpu=args.gpu,
        use_oras=args.oras
    )
    
    # Generate submit file
    submit_content = generator.generate_submit_file(
        cpus=args.cpus,
        memory=args.memory,
        disk=args.disk,
        input_files=args.input_files,
        output_files=args.output_files,
        arguments=args.arguments,
        queue_from=args.queue_from
    )
    
    with open(output_dir / 'submit.sub', 'w') as f:
        f.write(submit_content)
    print(f"✅ Generated submit.sub")
    
    # Generate run script
    run_script = generator.generate_run_script(
        has_args=bool(args.arguments or args.queue_from)
    )
    
    run_script_path = output_dir / 'run.sh'
    with open(run_script_path, 'w') as f:
        f.write(run_script)
    run_script_path.chmod(0o755)
    print(f"✅ Generated run.sh (executable)")
    
    # Generate README
    readme_content = generate_readme()
    with open(output_dir / 'HTCONDOR_README.md', 'w') as f:
        f.write(readme_content)
    print(f"✅ Generated HTCONDOR_README.md")
    
    print(f"\n📝 Next steps:")
    print(f"   1. Review submit.sub and adjust resources if needed")
    print(f"   2. Create log directory: mkdir -p condor_log")
    print(f"   3. Submit job: condor_submit submit.sub")
    print(f"   4. Monitor: condor_q")
    print(f"\n   See HTCONDOR_README.md for detailed instructions")


if __name__ == '__main__':
    main()
