"""
Utility functions for Google Colab environment.

This module provides helper functions for working in Google Colab notebooks,
including environment detection, setup, and file operations.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any, Union
from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError


def is_colab() -> bool:
    """
    Check if the current environment is Google Colab.

    This function detects whether the code is running in a Google Colab
    environment by checking for Colab-specific modules and environment variables.

    Returns:
        bool: True if running in Google Colab, False otherwise.

    Examples:
        >>> if is_colab():
        ...     print("Running in Google Colab")
        ... else:
        ...     print("Running locally")

    Notes:
        This function checks for the presence of 'google.colab' module
        and COLAB_GPU environment variable to determine the environment.
    """
    try:
        import google.colab  # type: ignore
        return True
    except ImportError:
        pass

    # Additional check for COLAB environment variables
    if 'COLAB_GPU' in os.environ or 'COLAB_TPU_ADDR' in os.environ:
        return True

    return False


def setup_colab_environment(
    verbose: bool = True,
    matplotlib_inline: bool = True
) -> Dict[str, Any]:
    """
    Set up basic configurations for Google Colab environment.

    This function performs common setup tasks for Colab notebooks, including
    matplotlib configuration and environment information gathering.

    Args:
        verbose: If True, print setup information. Defaults to True.
        matplotlib_inline: If True, configure matplotlib for inline display.
            Defaults to True.

    Returns:
        Dict[str, Any]: A dictionary containing environment information with keys:
            - 'is_colab': Whether running in Colab
            - 'python_version': Python version string
            - 'platform': Platform information
            - 'working_directory': Current working directory

    Raises:
        RuntimeError: If matplotlib configuration fails when matplotlib_inline is True
            and matplotlib is not available.

    Examples:
        >>> env_info = setup_colab_environment(verbose=True)
        >>> print(f"Python version: {env_info['python_version']}")

    Notes:
        This function is safe to call in non-Colab environments; it will
        simply skip Colab-specific configurations.
    """
    env_info: Dict[str, Any] = {
        'is_colab': is_colab(),
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': str(Path.cwd())
    }

    # Configure matplotlib for inline display if requested
    if matplotlib_inline:
        try:
            import matplotlib.pyplot as plt
            if env_info['is_colab']:
                # In Colab, inline is usually default, but ensure it's set
                try:
                    from IPython import get_ipython
                    ipython = get_ipython()
                    if ipython is not None:
                        ipython.run_line_magic('matplotlib', 'inline')
                except Exception:
                    pass  # IPython not available or magic failed
            env_info['matplotlib_backend'] = plt.get_backend()
        except ImportError:
            if verbose:
                print("Warning: matplotlib not available")
            env_info['matplotlib_backend'] = None

    if verbose:
        print("=" * 50)
        print("Environment Setup Complete")
        print("=" * 50)
        print(f"Running in Colab: {env_info['is_colab']}")
        print(f"Python Version: {env_info['python_version'].split()[0]}")
        print(f"Platform: {env_info['platform']}")
        print(f"Working Directory: {env_info['working_directory']}")
        if matplotlib_inline:
            print(f"Matplotlib Backend: {env_info.get('matplotlib_backend', 'N/A')}")
        print("=" * 50)

    return env_info


def download_from_url(
    url: str,
    destination: Optional[str] = None,
    verbose: bool = True
) -> Path:
    """
    Download a file from a URL to a local destination.

    This function downloads a file from the specified URL and saves it to
    the destination path. If no destination is provided, the filename from
    the URL is used in the current directory.

    Args:
        url: The URL of the file to download. Must be a valid HTTP/HTTPS URL.
        destination: Optional path where the file should be saved. If None,
            uses the filename from the URL in the current directory.
        verbose: If True, print download progress information. Defaults to True.

    Returns:
        Path: Path object pointing to the downloaded file.

    Raises:
        ValueError: If the URL is empty or invalid.
        HTTPError: If the HTTP request fails (e.g., 404, 403).
        URLError: If there's a network-related error.
        IOError: If there's an error writing the file to disk.

    Examples:
        >>> # Download a file to current directory
        >>> path = download_from_url("https://example.com/data.csv")
        >>> print(f"Downloaded to: {path}")

        >>> # Download to specific location
        >>> path = download_from_url(
        ...     "https://example.com/data.csv",
        ...     destination="/tmp/my_data.csv"
        ... )

    Notes:
        - Large files may take time to download
        - Ensure you have write permissions for the destination directory
        - The function will overwrite existing files without warning
    """
    # Validate URL
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")

    # Determine destination path
    if destination is None:
        # Extract filename from URL
        filename = url.split('/')[-1].split('?')[0]  # Remove query parameters
        if not filename:
            filename = 'downloaded_file'
        destination_path = Path.cwd() / filename
    else:
        destination_path = Path(destination)

    # Create parent directories if they don't exist
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Downloading from: {url}")
        print(f"Saving to: {destination_path}")

    try:
        # Download the file
        urlretrieve(url, str(destination_path))

        if verbose:
            file_size = destination_path.stat().st_size
            print(f"Download complete! File size: {file_size:,} bytes")

        return destination_path

    except HTTPError as e:
        raise HTTPError(
            url=e.url,
            code=e.code,
            msg=f"HTTP Error {e.code}: {e.msg}",
            hdrs=e.hdrs,
            fp=e.fp
        )
    except URLError as e:
        raise URLError(f"Failed to download from {url}: {e.reason}")
    except IOError as e:
        raise IOError(f"Failed to save file to {destination_path}: {e}")


def format_file_size(size_bytes: Union[int, float]) -> str:
    """
    Convert file size in bytes to human-readable format.

    This function converts a numeric file size to a human-readable string
    with appropriate unit suffix (B, KB, MB, GB, TB).

    Args:
        size_bytes: The file size in bytes. Must be a non-negative number.

    Returns:
        str: Human-readable file size string (e.g., "1.50 MB", "2.30 GB").

    Raises:
        ValueError: If size_bytes is negative.
        TypeError: If size_bytes is not a number.

    Examples:
        >>> format_file_size(1024)
        '1.00 KB'
        >>> format_file_size(1536)
        '1.50 KB'
        >>> format_file_size(1048576)
        '1.00 MB'
        >>> format_file_size(0)
        '0 B'

    Notes:
        - Uses binary units (1 KB = 1024 bytes)
        - Returns up to 2 decimal places for sizes >= 1 KB
        - Returns integer format for bytes (< 1 KB)
    """
    if not isinstance(size_bytes, (int, float)):
        raise TypeError(f"size_bytes must be a number, got {type(size_bytes).__name__}")

    if size_bytes < 0:
        raise ValueError("size_bytes must be non-negative")

    if size_bytes == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} B"
    return f"{size:.2f} {units[unit_index]}"


def get_gpu_info() -> Dict[str, Any]:
    """
    Get GPU information for the current environment.

    This function retrieves GPU information using nvidia-smi command.
    Useful for checking GPU availability and specifications in Colab.

    Returns:
        Dict[str, Any]: A dictionary containing GPU information with keys:
            - 'available': Whether GPU is available (bool)
            - 'count': Number of GPUs (int)
            - 'devices': List of device information dicts, each containing:
                - 'index': GPU index
                - 'name': GPU model name
                - 'memory_total': Total memory in MB
                - 'memory_used': Used memory in MB (if available)
                - 'memory_free': Free memory in MB (if available)
            - 'driver_version': NVIDIA driver version (if available)
            - 'error': Error message if GPU detection failed (only present on error)

    Examples:
        >>> gpu_info = get_gpu_info()
        >>> if gpu_info['available']:
        ...     print(f"GPU: {gpu_info['devices'][0]['name']}")
        ...     print(f"Memory: {gpu_info['devices'][0]['memory_total']} MB")
        ... else:
        ...     print("No GPU available")

    Notes:
        - Requires nvidia-smi to be installed and accessible
        - Safe to call in environments without GPU (returns available=False)
        - In Colab, use this to verify GPU runtime is enabled
    """
    result: Dict[str, Any] = {
        'available': False,
        'count': 0,
        'devices': [],
    }

    try:
        # Check if nvidia-smi is available
        nvidia_smi_output = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,memory.free,driver_version',
             '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if nvidia_smi_output.returncode != 0:
            result['error'] = "nvidia-smi command failed"
            return result

        lines = nvidia_smi_output.stdout.strip().split('\n')
        devices = []

        for line in lines:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 6:
                device = {
                    'index': int(parts[0]),
                    'name': parts[1],
                    'memory_total': int(float(parts[2])),
                    'memory_used': int(float(parts[3])),
                    'memory_free': int(float(parts[4])),
                }
                devices.append(device)
                # Driver version is same for all GPUs, take from first
                if 'driver_version' not in result:
                    result['driver_version'] = parts[5]

        if devices:
            result['available'] = True
            result['count'] = len(devices)
            result['devices'] = devices

    except FileNotFoundError:
        result['error'] = "nvidia-smi not found (no NVIDIA GPU or drivers not installed)"
    except subprocess.TimeoutExpired:
        result['error'] = "nvidia-smi command timed out"
    except Exception as e:
        result['error'] = f"Failed to get GPU info: {str(e)}"

    return result


def get_memory_info() -> Dict[str, Any]:
    """
    Get system memory information.

    This function retrieves RAM usage information from /proc/meminfo on Linux
    or uses alternative methods for other platforms.

    Returns:
        Dict[str, Any]: A dictionary containing memory information with keys:
            - 'total_bytes': Total RAM in bytes
            - 'available_bytes': Available RAM in bytes
            - 'used_bytes': Used RAM in bytes
            - 'percent_used': Memory usage percentage (0-100)
            - 'total_formatted': Human-readable total memory
            - 'available_formatted': Human-readable available memory
            - 'used_formatted': Human-readable used memory
            - 'platform': Platform identifier
            - 'error': Error message (only present if detection failed)

    Examples:
        >>> mem_info = get_memory_info()
        >>> print(f"Memory Usage: {mem_info['percent_used']:.1f}%")
        >>> print(f"Available: {mem_info['available_formatted']}")

    Notes:
        - On Linux (including Colab), reads from /proc/meminfo
        - Falls back to basic info on unsupported platforms
        - Useful for monitoring memory in long-running Colab notebooks
    """
    result: Dict[str, Any] = {
        'platform': sys.platform,
    }

    try:
        if sys.platform.startswith('linux'):
            # Read from /proc/meminfo on Linux
            meminfo: Dict[str, int] = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0].rstrip(':')
                        # Values in /proc/meminfo are in kB
                        value = int(parts[1]) * 1024  # Convert to bytes
                        meminfo[key] = value

            total = meminfo.get('MemTotal', 0)
            available = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
            used = total - available

            result['total_bytes'] = total
            result['available_bytes'] = available
            result['used_bytes'] = used
            result['percent_used'] = (used / total * 100) if total > 0 else 0
            result['total_formatted'] = format_file_size(total)
            result['available_formatted'] = format_file_size(available)
            result['used_formatted'] = format_file_size(used)

        else:
            # Fallback for non-Linux platforms
            result['error'] = f"Memory info not fully supported on {sys.platform}"
            result['total_bytes'] = 0
            result['available_bytes'] = 0
            result['used_bytes'] = 0
            result['percent_used'] = 0
            result['total_formatted'] = "N/A"
            result['available_formatted'] = "N/A"
            result['used_formatted'] = "N/A"

    except FileNotFoundError:
        result['error'] = "/proc/meminfo not found"
        result['total_bytes'] = 0
        result['available_bytes'] = 0
        result['used_bytes'] = 0
        result['percent_used'] = 0
        result['total_formatted'] = "N/A"
        result['available_formatted'] = "N/A"
        result['used_formatted'] = "N/A"
    except Exception as e:
        result['error'] = f"Failed to get memory info: {str(e)}"
        result['total_bytes'] = 0
        result['available_bytes'] = 0
        result['used_bytes'] = 0
        result['percent_used'] = 0
        result['total_formatted'] = "N/A"
        result['available_formatted'] = "N/A"
        result['used_formatted'] = "N/A"

    return result


if __name__ == "__main__":
    # Simple demonstration
    print("Colab Utils Demonstration")
    print("-" * 50)

    # Check environment
    print(f"\n1. Environment Check:")
    print(f"   Is Colab: {is_colab()}")

    # Setup environment
    print(f"\n2. Setup Environment:")
    env_info = setup_colab_environment(verbose=False)
    for key, value in env_info.items():
        print(f"   {key}: {value}")

    # File size formatting
    print(f"\n3. File Size Formatting:")
    test_sizes = [0, 512, 1024, 1536, 1048576, 1073741824]
    for size in test_sizes:
        print(f"   {size} bytes -> {format_file_size(size)}")

    # GPU info
    print(f"\n4. GPU Information:")
    gpu_info = get_gpu_info()
    print(f"   Available: {gpu_info['available']}")
    if gpu_info['available']:
        for device in gpu_info['devices']:
            print(f"   GPU {device['index']}: {device['name']}")
            print(f"   Memory: {device['memory_total']} MB")
    elif 'error' in gpu_info:
        print(f"   Note: {gpu_info['error']}")

    # Memory info
    print(f"\n5. Memory Information:")
    mem_info = get_memory_info()
    print(f"   Total: {mem_info['total_formatted']}")
    print(f"   Available: {mem_info['available_formatted']}")
    print(f"   Used: {mem_info['used_formatted']} ({mem_info['percent_used']:.1f}%)")

    print("\n" + "-" * 50)
    print("All utility functions are ready to use!")
