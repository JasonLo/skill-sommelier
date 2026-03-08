#!/usr/bin/env python3
"""
Convert Docker images to Apptainer/Singularity .sif format.
Provides both direct conversion and .def file generation.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


def check_apptainer_installed() -> bool:
    """Check if Apptainer is installed."""
    try:
        subprocess.run(['apptainer', '--version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_docker_to_sif(docker_image: str, output_sif: str, 
                          force: bool = False) -> bool:
    """
    Convert a Docker image to Apptainer .sif format.
    
    Args:
        docker_image: Docker image name (e.g., 'my-app:latest')
        output_sif: Output .sif file path
        force: Overwrite existing file if True
    
    Returns:
        True if successful, False otherwise
    """
    # Add docker:// prefix if not present
    if not docker_image.startswith('docker://'):
        docker_image = f'docker://{docker_image}'
    
    # Check if output file exists
    if Path(output_sif).exists() and not force:
        print(f"Error: {output_sif} already exists. Use --force to overwrite.")
        return False
    
    print(f"🔨 Building Apptainer image from {docker_image}...")
    print(f"   Output: {output_sif}")
    
    try:
        cmd = ['apptainer', 'build']
        if force:
            cmd.append('--force')
        cmd.extend([output_sif, docker_image])
        
        subprocess.run(cmd, check=True)
        print(f"✅ Successfully created {output_sif}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building Apptainer image: {e}")
        return False


def generate_def_file(docker_image: str, script_name: str, 
                      output_def: str, cuda_enabled: bool = False) -> str:
    """
    Generate an Apptainer .def file for custom builds.
    
    Args:
        docker_image: Base Docker image
        script_name: Python script to run
        output_def: Output .def file path
        cuda_enabled: Whether to enable NVIDIA GPU support
    
    Returns:
        Path to generated .def file
    """
    # Determine bootstrap image
    if cuda_enabled:
        bootstrap_image = "nvidia/cuda:12.6.3-runtime-ubuntu22.04"
        post_section = """
    # Install Python and dependencies
    apt-get update
    apt-get install -y python3 python3-pip
    pip3 install --no-cache-dir torch torchvision
"""
    else:
        bootstrap_image = docker_image if not docker_image.startswith('docker://') else docker_image[9:]
        post_section = """
    # Additional setup if needed
    # apt-get update
    # apt-get install -y package-name
"""
    
    def_content = f"""Bootstrap: docker
From: {bootstrap_image}

%labels
    Author Your Name
    Version 1.0

%help
    This container runs {script_name}
    
    Usage:
        apptainer run image.sif
        apptainer exec image.sif python3 {script_name}

%post
{post_section}

%environment
    export LC_ALL=C
    export PATH=/usr/local/bin:$PATH

%runscript
    python3 {script_name} "$@"

%test
    python3 --version
    python3 -c "import sys; print(f'Python {{sys.version}}')"
"""
    
    with open(output_def, 'w') as f:
        f.write(def_content)
    
    print(f"✅ Generated {output_def}")
    return output_def


def generate_conversion_script(output_path: str = "apptainerize.sh") -> str:
    """Generate a standalone bash script for Docker to Apptainer conversion."""
    
    script_content = """#!/bin/bash
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
echo "  apptainer exec ${SIF_TARGET} python script.py"
echo "  apptainer shell ${SIF_TARGET}"
"""
    
    with open(output_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    Path(output_path).chmod(0o755)
    
    print(f"✅ Generated {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Convert Docker images to Apptainer/Singularity .sif format'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', 
                                          help='Convert Docker image to .sif')
    convert_parser.add_argument('docker_image', 
                               help='Docker image name (e.g., my-app:latest)')
    convert_parser.add_argument('output_sif', 
                               help='Output .sif file path')
    convert_parser.add_argument('--force', action='store_true',
                               help='Overwrite existing file')
    
    # Def file command
    def_parser = subparsers.add_parser('def', 
                                       help='Generate Apptainer .def file')
    def_parser.add_argument('docker_image', 
                           help='Base Docker image')
    def_parser.add_argument('script', 
                           help='Python script to run')
    def_parser.add_argument('--output', default='Apptainer.def',
                           help='Output .def file (default: Apptainer.def)')
    def_parser.add_argument('--cuda', action='store_true',
                           help='Enable CUDA/GPU support')
    
    # Script command
    script_parser = subparsers.add_parser('script',
                                         help='Generate conversion bash script')
    script_parser.add_argument('--output', default='apptainerize.sh',
                              help='Output script path (default: apptainerize.sh)')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        # Check Apptainer installation
        if not check_apptainer_installed():
            print("❌ Apptainer is not installed.")
            print("\nInstallation instructions:")
            print("  Ubuntu/Debian: sudo apt-get install -y apptainer")
            print("  CentOS/RHEL: sudo yum install -y apptainer")
            print("  From source: https://apptainer.org/docs/admin/main/installation.html")
            sys.exit(1)
        
        success = convert_docker_to_sif(args.docker_image, args.output_sif, args.force)
        sys.exit(0 if success else 1)
    
    elif args.command == 'def':
        generate_def_file(args.docker_image, args.script, args.output, args.cuda)
        print(f"\nTo build the image:")
        print(f"  sudo apptainer build myimage.sif {args.output}")
        sys.exit(0)
    
    elif args.command == 'script':
        generate_conversion_script(args.output)
        print(f"\nUsage:")
        print(f"  ./{args.output} my-app:latest myapp.sif")
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
