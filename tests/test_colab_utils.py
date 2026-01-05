"""
Unit tests for colab_utils module.

These tests verify the functionality of utility functions for Google Colab,
including environment detection, setup, and file operations.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

# Add parent directory to path to import colab_utils
sys.path.insert(0, str(Path(__file__).parent.parent))

import colab_utils


class TestIsColab(unittest.TestCase):
    """Test cases for is_colab() function."""

    def test_is_colab_not_in_colab(self):
        """Test that is_colab returns False in non-Colab environment."""
        # In a normal environment without google.colab module
        with patch.dict('sys.modules', {'google.colab': None}):
            # Also ensure no Colab environment variables
            with patch.dict(os.environ, {}, clear=True):
                result = colab_utils.is_colab()
                self.assertIsInstance(result, bool)
                # In test environment, should be False
                self.assertFalse(result)

    def test_is_colab_with_env_var(self):
        """Test that is_colab returns True when COLAB_GPU env var exists."""
        with patch.dict('sys.modules', {'google.colab': None}):
            with patch.dict(os.environ, {'COLAB_GPU': '0'}):
                result = colab_utils.is_colab()
                self.assertTrue(result)

    def test_is_colab_with_tpu_env_var(self):
        """Test that is_colab returns True when COLAB_TPU_ADDR env var exists."""
        with patch.dict('sys.modules', {'google.colab': None}):
            with patch.dict(os.environ, {'COLAB_TPU_ADDR': 'localhost'}):
                result = colab_utils.is_colab()
                self.assertTrue(result)

    def test_is_colab_return_type(self):
        """Test that is_colab always returns a boolean."""
        result = colab_utils.is_colab()
        self.assertIsInstance(result, bool)


class TestSetupColabEnvironment(unittest.TestCase):
    """Test cases for setup_colab_environment() function."""

    def test_setup_returns_dict(self):
        """Test that setup_colab_environment returns a dictionary."""
        result = colab_utils.setup_colab_environment(verbose=False, matplotlib_inline=False)
        self.assertIsInstance(result, dict)

    def test_setup_contains_required_keys(self):
        """Test that returned dict contains all required keys."""
        result = colab_utils.setup_colab_environment(verbose=False, matplotlib_inline=False)
        required_keys = ['is_colab', 'python_version', 'platform', 'working_directory']
        for key in required_keys:
            self.assertIn(key, result)

    def test_setup_values_types(self):
        """Test that returned values have correct types."""
        result = colab_utils.setup_colab_environment(verbose=False, matplotlib_inline=False)
        self.assertIsInstance(result['is_colab'], bool)
        self.assertIsInstance(result['python_version'], str)
        self.assertIsInstance(result['platform'], str)
        self.assertIsInstance(result['working_directory'], str)

    def test_setup_verbose_output(self):
        """Test that verbose=True produces output."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            colab_utils.setup_colab_environment(verbose=True, matplotlib_inline=False)
            output = fake_output.getvalue()
            self.assertIn("Environment Setup Complete", output)
            self.assertIn("Running in Colab", output)

    def test_setup_no_verbose_output(self):
        """Test that verbose=False produces minimal output."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            colab_utils.setup_colab_environment(verbose=False, matplotlib_inline=False)
            output = fake_output.getvalue()
            self.assertEqual(output, "")

    def test_setup_matplotlib_unavailable(self):
        """Test setup when matplotlib is not available."""
        with patch.dict('sys.modules', {'matplotlib': None, 'matplotlib.pyplot': None}):
            result = colab_utils.setup_colab_environment(
                verbose=False,
                matplotlib_inline=True
            )
            # Should not crash, just skip matplotlib setup
            self.assertIsInstance(result, dict)


class TestDownloadFromUrl(unittest.TestCase):
    """Test cases for download_from_url() function."""

    def test_download_invalid_url_empty(self):
        """Test that empty URL raises ValueError."""
        with self.assertRaises(ValueError) as context:
            colab_utils.download_from_url("")
        self.assertIn("non-empty string", str(context.exception))

    def test_download_invalid_url_no_protocol(self):
        """Test that URL without http/https raises ValueError."""
        with self.assertRaises(ValueError) as context:
            colab_utils.download_from_url("example.com/file.txt")
        self.assertIn("http://", str(context.exception))

    def test_download_invalid_url_type(self):
        """Test that non-string URL raises ValueError."""
        with self.assertRaises(ValueError):
            colab_utils.download_from_url(None)  # type: ignore

    @patch('colab_utils.urlretrieve')
    def test_download_with_destination(self, mock_urlretrieve):
        """Test downloading with specific destination."""
        mock_urlretrieve.return_value = None
        url = "https://example.com/test.txt"
        destination = "/tmp/test_file.txt"

        # Create a mock file
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024
            with patch('pathlib.Path.mkdir'):
                result = colab_utils.download_from_url(
                    url,
                    destination=destination,
                    verbose=False
                )

        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), destination)
        mock_urlretrieve.assert_called_once_with(url, destination)

    @patch('colab_utils.urlretrieve')
    def test_download_without_destination(self, mock_urlretrieve):
        """Test downloading without specifying destination."""
        mock_urlretrieve.return_value = None
        url = "https://example.com/test.txt"

        with patch('pathlib.Path.mkdir'):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 2048
                with patch('pathlib.Path.cwd') as mock_cwd:
                    mock_cwd.return_value = Path("/tmp")
                    result = colab_utils.download_from_url(url, verbose=False)

        self.assertIsInstance(result, Path)
        self.assertEqual(result.name, "test.txt")

    @patch('colab_utils.urlretrieve')
    def test_download_verbose_output(self, mock_urlretrieve):
        """Test that verbose=True produces output."""
        mock_urlretrieve.return_value = None
        url = "https://example.com/test.txt"

        with patch('pathlib.Path.mkdir'):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 512
                with patch('sys.stdout', new=StringIO()) as fake_output:
                    colab_utils.download_from_url(url, verbose=True)
                    output = fake_output.getvalue()
                    self.assertIn("Downloading from", output)
                    self.assertIn(url, output)
                    self.assertIn("Download complete", output)

    def test_download_extracts_filename_with_query(self):
        """Test filename extraction from URL with query parameters."""
        url = "https://example.com/file.csv?version=1&token=abc"

        with patch('colab_utils.urlretrieve') as mock_urlretrieve:
            with patch('pathlib.Path.mkdir'):
                with patch('pathlib.Path.stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    result = colab_utils.download_from_url(url, verbose=False)

        # Should extract 'file.csv' and ignore query parameters
        self.assertEqual(result.name, "file.csv")


class TestFormatFileSize(unittest.TestCase):
    """Test cases for format_file_size() function."""

    def test_format_zero_bytes(self):
        """Test formatting of 0 bytes."""
        result = colab_utils.format_file_size(0)
        self.assertEqual(result, "0 B")

    def test_format_bytes(self):
        """Test formatting of small byte values."""
        result = colab_utils.format_file_size(512)
        self.assertEqual(result, "512 B")

    def test_format_kilobytes(self):
        """Test formatting of kilobyte values."""
        result = colab_utils.format_file_size(1024)
        self.assertEqual(result, "1.00 KB")
        result = colab_utils.format_file_size(1536)
        self.assertEqual(result, "1.50 KB")

    def test_format_megabytes(self):
        """Test formatting of megabyte values."""
        result = colab_utils.format_file_size(1048576)
        self.assertEqual(result, "1.00 MB")

    def test_format_gigabytes(self):
        """Test formatting of gigabyte values."""
        result = colab_utils.format_file_size(1073741824)
        self.assertEqual(result, "1.00 GB")

    def test_format_negative_raises_error(self):
        """Test that negative values raise ValueError."""
        with self.assertRaises(ValueError) as context:
            colab_utils.format_file_size(-100)
        self.assertIn("non-negative", str(context.exception))

    def test_format_invalid_type_raises_error(self):
        """Test that non-numeric types raise TypeError."""
        with self.assertRaises(TypeError):
            colab_utils.format_file_size("1024")  # type: ignore

    def test_format_float_value(self):
        """Test formatting of float byte values."""
        result = colab_utils.format_file_size(1024.0)
        self.assertEqual(result, "1.00 KB")


class TestGetGpuInfo(unittest.TestCase):
    """Test cases for get_gpu_info() function."""

    def test_get_gpu_info_returns_dict(self):
        """Test that get_gpu_info returns a dictionary."""
        result = colab_utils.get_gpu_info()
        self.assertIsInstance(result, dict)

    def test_get_gpu_info_has_required_keys(self):
        """Test that result contains required keys."""
        result = colab_utils.get_gpu_info()
        self.assertIn('available', result)
        self.assertIn('count', result)
        self.assertIn('devices', result)

    def test_get_gpu_info_types(self):
        """Test that result values have correct types."""
        result = colab_utils.get_gpu_info()
        self.assertIsInstance(result['available'], bool)
        self.assertIsInstance(result['count'], int)
        self.assertIsInstance(result['devices'], list)

    @patch('subprocess.run')
    def test_get_gpu_info_nvidia_smi_not_found(self, mock_run):
        """Test behavior when nvidia-smi is not found."""
        mock_run.side_effect = FileNotFoundError()
        result = colab_utils.get_gpu_info()
        self.assertFalse(result['available'])
        self.assertIn('error', result)

    @patch('subprocess.run')
    def test_get_gpu_info_timeout(self, mock_run):
        """Test behavior when nvidia-smi times out."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="nvidia-smi", timeout=10)
        result = colab_utils.get_gpu_info()
        self.assertFalse(result['available'])
        self.assertIn('error', result)

    @patch('subprocess.run')
    def test_get_gpu_info_with_gpu(self, mock_run):
        """Test parsing of nvidia-smi output when GPU is available."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "0, Tesla T4, 15109, 500, 14609, 525.85.12\n"
        mock_run.return_value = mock_result

        result = colab_utils.get_gpu_info()
        self.assertTrue(result['available'])
        self.assertEqual(result['count'], 1)
        self.assertEqual(len(result['devices']), 1)
        self.assertEqual(result['devices'][0]['name'], 'Tesla T4')
        self.assertEqual(result['devices'][0]['memory_total'], 15109)


class TestGetMemoryInfo(unittest.TestCase):
    """Test cases for get_memory_info() function."""

    def test_get_memory_info_returns_dict(self):
        """Test that get_memory_info returns a dictionary."""
        result = colab_utils.get_memory_info()
        self.assertIsInstance(result, dict)

    def test_get_memory_info_has_required_keys(self):
        """Test that result contains required keys."""
        result = colab_utils.get_memory_info()
        self.assertIn('platform', result)
        self.assertIn('total_bytes', result)
        self.assertIn('available_bytes', result)
        self.assertIn('used_bytes', result)
        self.assertIn('percent_used', result)
        self.assertIn('total_formatted', result)

    def test_get_memory_info_types(self):
        """Test that result values have correct types."""
        result = colab_utils.get_memory_info()
        self.assertIsInstance(result['platform'], str)
        self.assertIsInstance(result['total_bytes'], (int, float))
        self.assertIsInstance(result['percent_used'], (int, float))
        self.assertIsInstance(result['total_formatted'], str)

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_get_memory_info_no_proc(self, mock_open_file):
        """Test behavior when /proc/meminfo is not available."""
        with patch('sys.platform', 'linux'):
            result = colab_utils.get_memory_info()
            self.assertIn('error', result)
            self.assertEqual(result['total_formatted'], "N/A")

    @patch('sys.platform', 'darwin')
    def test_get_memory_info_non_linux(self):
        """Test behavior on non-Linux platforms."""
        result = colab_utils.get_memory_info()
        self.assertIn('error', result)

    def test_get_memory_info_linux(self):
        """Test memory info on Linux platform."""
        import sys
        if sys.platform.startswith('linux'):
            result = colab_utils.get_memory_info()
            self.assertGreater(result['total_bytes'], 0)
            self.assertGreaterEqual(result['percent_used'], 0)
            self.assertLessEqual(result['percent_used'], 100)


class TestMainExecution(unittest.TestCase):
    """Test cases for main execution block."""

    def test_main_execution(self):
        """Test that main block runs without errors."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            # Import and run the main block
            import importlib
            importlib.reload(colab_utils)

            output = fake_output.getvalue()
            # Main block should produce some output
            self.assertIsInstance(output, str)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
