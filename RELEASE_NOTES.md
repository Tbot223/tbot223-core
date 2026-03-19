# Release Notes

## [3.0.1] - 2026-03-20

### Fixed

- **ResultWrapper**: Reuse single `ExceptionTracker` instance instead of creating a new one per exception
- **Exception**: Improved `get_exception_info()` / `get_exception_return()` params validation — now properly rejects `None`, non-tuple, and wrong-length params with a clearer error message
- **Utils**: Changed `type(value) != type(threshold)` to `type(value) is not type(threshold)` for PEP 8 compliance in `find_keys_by_value()`

### Changed

- **Decorators**: Added `functools.wraps` to preserve function metadata (`__name__`, `__doc__`) in:
  - `ResultWrapper`
  - `ExceptionTrackerDecorator`
  - `DecoratorUtils.count_runtime()`
- **Type Hints**: Improved type annotations for decorator return types in `ResultWrapper`, `ExceptionTrackerDecorator`, and `DecoratorUtils.count_runtime()`
- **Package**: Updated description and keywords in `setup.py` for better discoverability

### Tests

- **Added**: `TestResultWrapperMetadata` — verifies `functools.wraps` preserves `__name__` and `__doc__` in `ResultWrapper`
- **Added**: `TestExceptionDecoratorMetadata` — verifies `functools.wraps` preserves `__name__` and `__doc__` in `ExceptionTrackerDecorator`
- **Added**: `TestExceptionParamsValidation` — tests for `None`, non-tuple, and wrong-length params rejection in `get_exception_info()` / `get_exception_return()`
- **Added**: `test_count_runtime_preserves_function_metadata` — verifies `functools.wraps` in `count_runtime()`
- **Fixed**: `test_shm_memory_overflow` — use PID-unique shared memory name and larger payload to avoid OS page-alignment false positives

### Known Issues

- **AppCore_test.py**: Cannot run due to broken `numpy` native library dependency (`libgfortran.5.dylib` not found). This is an environment-specific issue, not a code bug.

---

## [3.0.0] - 2026-02-07

### Breaking Changes

- **Import System Overhaul**: Classes can now be imported and used directly
  - Before: `from tbot223_core import FileManager` → `FileManager.FileManager()`
  - After: `from tbot223_core import FileManager` → `FileManager()`
- **Utils Module Split**: `Utils.py` split into subpackage `Utils/`
  - `Utils/Utils.py` - Utility functions
  - `Utils/GlobalVars.py` - Global variable management
  - `Utils/DecoratorUtils.py` - Decorator utilities
- **Exception API Changes**:
  - Added `mask_tuple` parameter to `get_exception_info()` and `get_exception_return()`
  - Added `get_error_code()` method
  - `ExceptionTrackerDecorator` now uses `mask_tuple` for masking
- **Result Object Changes**:
  - `success` field type changed from `bool` to `Optional[bool]` (None = cancelled/not executed)

### Added

- **Result Methods**: New methods for Result object
  - `unwrap()` - Returns data if successful, raises `ResultUnwrapException` if failed or cancelled
  - `expect()` - Returns data if successful, raises `ResultUnwrapException` if not successful
  - `unwrap_or(default)` - Returns data if successful, otherwise returns default value
- **ResultUnwrapException**: New exception class for unwrap failures
- **Exception Methods**: `get_error_code()` function for returning unique identifiers
- **Tests**: Added `Result_test.py` with comprehensive Result object tests

### Changed

- **Default Workers**: `thread_pool_executor` and `process_pool_executor` now default to `os.cpu_count()`
- **Timeout Handling**: Improved `as_completed` timeout scaling in executors
- **Examples Updated**: All example files updated to reflect new import system
- **Tests Refactored**: Removed duplicate/overlapping tests for cleaner test suite

### Removed

- **Examples.md**: Removed from repository (examples still available in `examples/` directory)

---

## [2.1.3] - 2026-01-27

### Added

- **Examples**: Comprehensive example scripts for all core modules
  - `AppCore`: `thread_pool_executor`, `process_pool_executor`, `get_text_by_lang`, `clear_console`, `exit_application`, `restart_application`, `ResultWrapper`
  - `Exception`: `get_exception_info`, `get_exception_location`, `get_exception_return`, `ExceptionTrackerDecorator`
  - `FileManager`: `atomic_write`, `read_file`, `read_json`, `write_json`, `list_of_files`, `create_directory`, `delete_file`, `delete_directory`
  - `LogSys`: `make_logger`, `get_logger`, `stop_stream_handlers`, `log_message`, `SimpleSetting.get_instance`
  - `Result`: Basic usage of Result NamedTuple
- **LogSys**: `stop_stream_handlers()` method added to `LoggerManager`
- **LogSys**: `SimpleSetting` now supports log level configuration
- **Tests**: Comprehensive test coverage expansion (72% → 81%)
  - `TestSafeCLIInput`: 15 new tests for `safe_CLI_input()` method with mocked input
  - `TestSharedMemory`: 10 tests for SHM generation, sync, update, and cache management
  - `TestSharedMemoryFailures`: 6 tests for SHM failure scenarios
  - `TestUtilsMethods`: 5 tests for `insert_at_intervals()` method
  - `TestDecoratorUtilsMethods`: 2 tests for `make_decorator()` method
  - `TestResultClass`: 5 tests for Result NamedTuple behavior
  - `TestResultWrapper`: 4 tests for ResultWrapper decorator
  - Additional edge case tests for FileManager, LogSys, Exception modules
- **Utils**: Enhanced `find_keys_by_value()` with new parameters
  - `separator` parameter: Custom separator for nested key paths (supports "list"/"tuple" for output type)
  - `return_mod` parameter: Control return format ("flat", "forest", "path")

### Fixed

- **Utils**: Fixed `_lookup_dict()` using `extend()` instead of `append()` for nested results, preventing unintended list flattening
- **FileManager**: Added fallback for `shutil.rmtree()` compatibility (`onexc` → `onerror` for older Python versions)
- **AppCore**: `ResultWrapper` now passes function arguments to `ExceptionTracker.get_exception_return()` via `params` parameter

### Changed

- **Documentation**: Improved docstrings for `thread_pool_executor`, `process_pool_executor`, application lifecycle methods
- **Documentation**: Enhanced `ExceptionTrackerDecorator` docstring with detailed usage examples
- **Documentation**: Improved `Result` class docstring explaining NamedTuple immutability benefits
- **Documentation**: Clarified `FileManager.base_dir` attribute description (logging directory, not I/O base)
- **Documentation**: Enhanced `FileManager._lock_file()` docstring with mode parameter details for Unix/Windows
- **Documentation**: Updated README with usage warnings and clarifications
- **Utils**: Improved `_lookup_dict()` type hints and internal logic for better nested dictionary handling

---

## [2.1.2] - 2026-01-19

### Fixed

- **Critical**: Fixed infinite loop in `safe_CLI_input()` by adding `max_retries` parameter (default: 10)
- **Critical**: Fixed index offset bug in `insert_at_intervals()` by using reverse insertion
- **Critical**: Replaced hardcoded file size threshold with `LOCK_FILE_SIZE_THRESHOLD` constant (10MB)
- Improved traceback formatting in `ExceptionTracker` using `traceback.format_exception()`

### Added

- JSON serialization support for shared memory IPC (safer alternative to pickle)
  - `GlobalVars.SERIALIZERS` dictionary with pickle and json serialization lambdas
  - `serialize_format` parameter in `shm_sync()` and `shm_update()` methods
- Language cache management with automatic reload on KeyError via `__lang_cache_management__` decorator
- Type validation for `safe_CLI_input()` with `SUPPORTED_TYPES` and `other_type` parameter
- `DecoratorUtils.make_decorator()` method for converting functions to decorator form
- Comprehensive security warnings in all shared memory method docstrings

### Changed

- Improved process pool chunk calculation with `math.ceil()` and `max(1, ...)` to prevent zero chunk size
- Enhanced `_check_executable()` return type hint to `Tuple[bool, Optional[str]]`
- Optimized conditional logging checks throughout codebase
- Updated all shared memory security documentation to explain pickle vs JSON trade-offs

### Security

- **Important**: Added JSON serialization option for untrusted inter-process communication
- **Important**: All shared memory methods now document pickle security risks and JSON alternatives
- Pickle serialization retained as default for performance, JSON available via `serialize_format="json"`

---

## [2.1.1] - 2026-01-18

### Added

- `shm_connect()` method for connecting to existing shared memory objects (for child processes)
- Header-based serialization for robust shared memory data transfer

### Changed

- `is_logging_enabled` → `__is_logging_enabled__` (private attribute) in AppCore, FileManager, Utils
- `shm_close()` now accepts `close_only` parameter to close without unlinking shared memory
- GlobalVars internal logic refactored: direct key checks instead of `exists()` for thread safety and performance
- Conditional logging added to reduce overhead when logging is disabled

---

## [2.1.0] - 2026-01-16

### Added

- Shared Memory IPC support for GlobalVars
  - `shm_gen()`, `shm_sync()`, `shm_update()`, `shm_get()`, `shm_close()`
  - Optional `multiprocessing.Lock` for inter-process synchronization
  - LRU cache for shared memory objects (`shm_cache_management()`)
- Context manager support for GlobalVars (`with gv:`)

### Changed

- `ExceptionTracker.get_exception_info()` params type: `dict` → `Tuple[Tuple, dict]`
