# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-05

### Added

#### New Utility Functions

- **`format_file_size()`**: Human-readable file size formatting utility
  - Converts bytes to KB, MB, GB, TB, PB with 2 decimal precision
  - Input validation for negative values and non-numeric types
  - Uses binary units (1 KB = 1024 bytes)
  - Useful for displaying download sizes and file information
  - Full type hints and comprehensive docstring

- **`get_gpu_info()`**: GPU information retrieval function
  - Detects NVIDIA GPU availability using nvidia-smi
  - Returns device name, memory (total/used/free), driver version
  - Supports multi-GPU environments
  - Safe to call in environments without GPU
  - Essential for verifying Colab GPU runtime is enabled
  - Full type hints and comprehensive docstring

- **`get_memory_info()`**: System memory information function
  - Retrieves RAM usage from /proc/meminfo on Linux
  - Returns total, available, used memory with formatted strings
  - Calculates memory usage percentage
  - Cross-platform fallback for non-Linux systems
  - Useful for monitoring memory in long-running notebooks
  - Full type hints and comprehensive docstring

#### Testing
- Added 20 new tests for the three new functions (38 total)
  - 8 tests for `format_file_size()`: zero, bytes, KB, MB, GB, negative, invalid type, float
  - 6 tests for `get_gpu_info()`: return type, keys, nvidia-smi not found, timeout, GPU parsing
  - 6 tests for `get_memory_info()`: return type, keys, /proc/meminfo unavailable, non-Linux

#### Documentation
- Updated README.md with:
  - New function descriptions and usage examples
  - Updated test count (38 tests)
  - Enhanced Colab usage examples including GPU and memory checks
- Updated demonstration in `__main__` block

### Changed
- Import statement updated to include `subprocess` module
- Type hints enhanced with `Union[int, float]` for `format_file_size`

### Technical Details
- All new functions use only Python standard library
- Consistent error handling patterns with existing code
- Test patterns match existing unittest/pytest style
- No breaking changes to existing API

### Files Changed
- `colab_utils.py` (UPDATED): Added 3 new functions (+260 lines)
- `tests/test_colab_utils.py` (UPDATED): Added 20 new tests (+152 lines)
- `README.md` (UPDATED): Added documentation for new functions (+75 lines)
- `CHANGELOG.md` (UPDATED): Added v0.2.0 release notes

### Commit Information
- Commit: fa41841
- Tag: v0.2.0
- Date: 2026-01-05

---

## Release Notes for GitHub Release (v0.2.0)

### 🚀 v0.2.0 - System Monitoring Utilities

New utility functions for GPU and memory monitoring in Google Colab environments.

**New Features:**
- 📏 `format_file_size()` - Convert bytes to human-readable format
- 🎮 `get_gpu_info()` - Check GPU availability and specifications
- 💾 `get_memory_info()` - Monitor system RAM usage

**Highlights:**
- ✅ 38 comprehensive tests (20 new, all passing)
- 📝 Full type hints and docstrings
- 🛡️ Robust error handling for edge cases
- 🚀 Standard library only (no new dependencies)

**Quick Start:**
```python
from colab_utils import format_file_size, get_gpu_info, get_memory_info

# Check GPU
gpu = get_gpu_info()
if gpu['available']:
    print(f"GPU: {gpu['devices'][0]['name']}")

# Check memory
mem = get_memory_info()
print(f"Available: {mem['available_formatted']}")

# Format sizes
print(format_file_size(1073741824))  # "1.00 GB"
```

**Test Command:**
```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

See [README.md](README.md) for detailed usage instructions.

---

**Generated with** [Claude Code](https://claude.com/claude-code)

---

## [0.1.0] - 2026-01-04

### Added

#### Core Functionality
- **`is_colab()`**: Environment detection function to identify Google Colab runtime
  - Checks for `google.colab` module presence
  - Validates Colab-specific environment variables (`COLAB_GPU`, `COLAB_TPU_ADDR`)
  - Returns boolean indicating Colab environment status
  - Full type hints and comprehensive docstring

- **`setup_colab_environment()`**: Environment configuration function for Colab notebooks
  - Gathers system information (Python version, platform, working directory)
  - Configures matplotlib for inline display (optional)
  - Supports verbose mode for detailed setup information
  - Returns dictionary with environment details
  - Safe to call in non-Colab environments
  - Full type hints and comprehensive docstring

- **`download_from_url()`**: URL-based file download utility
  - Downloads files from HTTP/HTTPS URLs
  - Automatic filename extraction from URLs
  - Custom destination path support
  - Query parameter handling in URLs
  - Comprehensive error handling (HTTPError, URLError, IOError)
  - Input validation for URL format
  - Progress reporting (optional verbose mode)
  - Full type hints and comprehensive docstring

#### Testing Infrastructure
- Comprehensive test suite with pytest (18 tests, 100% passing)
  - 4 tests for `is_colab()` covering:
    - Non-Colab environment detection
    - Environment variable-based detection
    - Return type validation
  - 6 tests for `setup_colab_environment()` covering:
    - Return value structure and types
    - Verbose/silent output modes
    - Matplotlib configuration handling
    - Missing dependency scenarios
  - 7 tests for `download_from_url()` covering:
    - URL validation (empty, invalid format, incorrect type)
    - Download with/without destination
    - Filename extraction from URLs with query parameters
    - Verbose output verification
  - 1 test for main execution block
- Test dependencies: pytest >= 7.4.0, pytest-cov >= 4.1.0

#### Documentation
- Comprehensive README.md with:
  - Feature overview and descriptions
  - Usage examples for all three functions
  - Installation instructions
  - Google Colab-specific usage guide
  - Test execution instructions
  - Dependency information
- Function-level documentation:
  - Complete docstrings with Args, Returns, Raises, Examples, and Notes sections
  - Type hints for all parameters and return values
- requirements.txt for development dependencies

#### Project Infrastructure
- `.gitignore` configured for Python projects
  - Python bytecode and cache files
  - Testing artifacts
  - IDE-specific files
  - Environment files
  - OS-specific files

### Technical Details

#### Dependencies
- **Runtime**: Python 3.7+ with standard library only
- **Testing**: pytest, pytest-cov
- **Optional**: matplotlib, IPython (typically pre-installed in Colab)

#### Design Principles
- Minimal external dependencies
- Standard library-first approach
- Comprehensive error handling
- Input validation at all entry points
- Type safety with full type hints
- Extensive documentation
- Test-driven development

#### Code Quality
- All functions include type hints
- Comprehensive docstrings following Google style
- Input validation and error handling
- Pure function approach where possible for testability
- No breaking changes (initial release)

### Files Changed
- `colab_utils.py` (NEW): Main utility module (280+ lines)
- `tests/test_colab_utils.py` (NEW): Comprehensive test suite (200+ lines)
- `tests/__init__.py` (NEW): Test package initialization
- `requirements.txt` (NEW): Development dependencies
- `.gitignore` (NEW): Version control ignore rules
- `README.md` (UPDATED): Comprehensive documentation (140+ lines)

### Commit Information
- Commit: 143dfe2
- Tag: v0.1.0
- Date: 2026-01-04

---

## Release Notes for GitHub Release

### 🎉 v0.1.0 - Initial Release

First release of GoogleColab-cc-demo-001, providing utility functions for Google Colab environments.

**Features:**
- 🔍 Environment detection (`is_colab()`)
- ⚙️ Environment setup (`setup_colab_environment()`)
- 📥 File download utility (`download_from_url()`)

**Highlights:**
- ✅ 18 comprehensive tests (100% passing)
- 📝 Full type hints and docstrings
- 🛡️ Robust error handling and input validation
- 📚 Extensive documentation with examples
- 🚀 Minimal dependencies (standard library only for runtime)

**Test Command:**
```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

**Quick Start:**
```python
from colab_utils import is_colab, setup_colab_environment, download_from_url

# Check environment
if is_colab():
    env_info = setup_colab_environment()
    download_from_url("https://example.com/data.csv")
```

See [README.md](README.md) for detailed usage instructions.

---

**Generated with** [Claude Code](https://claude.com/claude-code)
