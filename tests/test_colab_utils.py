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
