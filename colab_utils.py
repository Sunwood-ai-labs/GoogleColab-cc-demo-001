"""
Utility functions for Google Colab environment.

This module provides helper functions for working in Google Colab notebooks,
including environment detection, setup, and file operations.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any
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

    print("\n" + "-" * 50)
    print("All utility functions are ready to use!")
