# Release Notes

[한국어 (Korean)](RELEASE_NOTES.ko.md)

<details>
<summary>Table of Contents</summary>

- [4.0.0](#v4-0-0)
- [3.1.1](#v3-1-1)
- [3.1.0](#v3-1-0)
- [3.0.1](#v3-0-1)
- [3.0.0](#v3-0-0)
- [2.1.3](#v2-1-3)
- [2.1.2](#v2-1-2)
- [2.1.1](#v2-1-1)
- [2.1.0](#v2-1-0)
</details>

<a id="v4-0-0"></a>
## [4.0.0] - 2026-04-03

### Breaking Changes

- **GlobalVars**: Missing attribute reads such as `gv.some_key` now raise `AttributeError` instead of returning the sentinel string `"Key does not exist."`. Code that relied on string comparison must switch to `get()`, `exists()`, or `try/except AttributeError`.
- **GlobalVars**: Call-style access now treats `None` as a real value. `gv("key", None)` stores `None`; it no longer behaves like a read. Use `gv("key")` for lookups.
- **GlobalVars**: Shared-memory ownership rules are now enforced explicitly. `shm_close(name)` only unlinks blocks owned by the current process, non-owners should use `shm_close(name, close_only=True)`, and `shm_gen()` now fails if an existing block is smaller than the requested size.
- **AppCore**: `process_pool_executor(chunk_size=None)` no longer means auto chunking. It now submits the full task list to a single executor. Pass `chunk_size=0` for automatic chunking or a positive integer for explicit batching.

### Added

- **FileManager**: Added `exists()` as the preferred existence-check API while keeping `exist()` as a deprecated alias.
- **Result**: `Result.expect(msg="")` now accepts an optional custom failure message without changing the stored failure payload.
- **LogSys**: Added `timestamp=` as the preferred keyword for `LoggerManager.make_logger()`. The legacy `time=` keyword is still accepted as a deprecated alias.
- **Typing/Packaging**: Added `tbot223_core/py.typed` to the package and shipped it via `setup.py` so external type checkers can consume distributed type information.
- **Examples**: Added new runnable examples for `safe_CLI_input`, `get_error_code`, `exist`, `unwrap`, `expect`, `unwrap_or`, and the `Utils` / `GlobalVars` example sets.
- **Documentation**: Added split English/Korean docs under `docs/` for API reference, examples, migration guidance, and release history.

### Changed

- **Documentation layout**: Moved long-form documentation into `docs/` and kept only `README.md` and `README.ko.md` at the repository root.
- **Documentation fidelity**: Rewrote README/API/Examples content to match the current runtime behavior, including executor result shapes, `Result` failure payloads, logging path semantics, localization fallback, bool parsing, PBKDF2 payload shape, and shared-memory ownership/cleanup behavior.
- **AppCore**: Worker defaults are now resolved at call time instead of import time, so omitted `workers` values track the current CPU count and avoid stale defaults.
- **Tests/Tooling**: Retired the legacy root-level `test.py` flow and centered the maintained test workflow on the `TEST/SRC/` pytest suite.
- **Examples**: Updated LogSys and ResultWrapper examples to reflect real return values and the current log directory layout.

### Fixed

- **AppCore**: Brought executor validation, chunking docs, and sample usage into agreement with the current implementation.
- **FileManager**: Corrected existence-check docs and example coverage to match the actual `exists()` / `exist()` API split.
- **Utils**: Corrected PBKDF2 and nested-dictionary search docs/examples to match the actual return payloads and `separator="tuple"` behavior.
- **Exception/Result**: Corrected unwrap/expect examples and failure payload descriptions to match structured `error_info` handling.
- **LogSys**: Corrected logger creation docs/examples so they reflect that `make_logger()` returns a success message and `get_logger()` retrieves the actual `logging.Logger`.

### Documentation

- **Bilingual docs**: Fully split English and Korean documentation into separate files with updated cross-links.
- **Korean docs**: Rewrote the Korean release, migration, API, and examples docs to stand on their own instead of being summary-only translations.
- **Repo links**: Updated internal links to follow the new `docs/` layout and removed obsolete root-level doc paths.

### Tests

- **Pytest**: Verified `TEST/SRC/AppCore_test.py`, `TEST/SRC/LogSys_test.py`, `TEST/SRC/Utils_test.py`, and `TEST/SRC/Exception_test.py` against the current tree — `163 passed`.
- **Examples**: Verified all 41 example scripts. 40 ran in batch mode, and `examples/AppCore/restart_application.py` was additionally validated interactively because it replaces the running process.

<a id="v3-1-1"></a>
## [3.1.1] - 2026-03-28

### Fixed

- **Utils**: Added missing `__init__.py` to `tbot223_core/Utils/` subpackage — `find_packages()` did not recognize `Utils/` as a Python package without it, causing `DecoratorUtils`, `Utils`, and `GlobalVars` to be entirely absent from the PyPI distribution

---

<a id="v3-1-0"></a>
## [3.1.0] - 2026-03-27

### Security

- **GlobalVars**: Changed default serialization format for `shm_sync()` and `shm_update()` from `"pickle"` to `"json"` — pickle deserialization of untrusted data can execute arbitrary code. Existing code relying on the pickle default must now pass `serialize_format="pickle"` explicitly.

### Fixed

- **FileManager**: Fixed potential `NameError` in `atomic_write()` — `temp_path` is now initialized to `None` before the `try` block, preventing a reference error if the temp file is never created
- **FileManager**: Narrowed bare `except:` to `except TypeError:` in `delete_directory()` fallback path (`onexc` → `onerror`) to avoid suppressing unrelated exceptions
- **GlobalVars**: Hardened `__getattr__` exception handling — `KeyError` (key not found) is now caught separately from unexpected errors, which are routed through `_exception_tracker` instead of being silently swallowed
- **LogSys**: `LoggerManager` and `Log` now hold a persistent `_exception_tracker` instance instead of creating a new `ExceptionTracker()` on every exception
- **AppCore**: Executor shutdown errors in `_generic_executor()` are now tracked via `_exception_tracker`
- **Utils**: Changed `isinstance(...) is False` to `not isinstance(...)` in `find_keys_by_value()` for PEP 8 compliance
- **Exception**: `get_exception_return()` `params` default changed from `None` to `((), {})` — the previous default caused the params validation in `get_exception_info()` to always reject it, making parameterless calls fail
- **Exception**: `get_error_code()` return type annotation corrected from `None` to `Result`

### Changed

- **All modules**: Extracted repeated `if self.__is_logging_enabled__: self.log.log_message(...)` into a `_log(level, message)` helper method on each class — reduces boilerplate and centralizes the logging guard
- **GlobalVars**: `shm_update()` deserialization error message now reflects the actual `serialize_format` in use instead of hardcoding `"pickle"`
- **Documentation**: Unified docstring Args format to backtick style (`` `param` : description ``) across all modules
- **README**: Corrected `encrypt()` → `hashing()` (wrong method name); removed `_lock()` from public API listing; documented `exists()` for FileManager and kept `exist()` as a deprecated alias; added `stop_stream_handlers()` to LogSys; added `get_error_code()` to ExceptionTracker; added `ResultWrapper` class with usage example; expanded `LogSys` section with per-method descriptions and `SimpleSetting` usage; updated `AppCore` section with spawn context note and `pause` parameter; updated GlobalVars serialization description to reflect JSON-as-default
- **AppCore**: `ProcessPoolExecutor` now passes `mp_context=multiprocessing.get_context("spawn")` — enforces spawn start method for safer cross-platform process creation and avoids fork-related issues on macOS/Windows
- **AppCore**: `safe_CLI_input()` enhanced with `EOFError` handling (sets empty string for non-interactive terminals), `KeyboardInterrupt` handling (returns `Result(False, ...)` immediately), and full bool type conversion support — accepts common true/false strings (`"yes"`, `"no"`, `"1"`, `"0"`, `"on"`, `"off"`, etc.) and converts them to `bool`

---

<a id="v3-0-1"></a>
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

<a id="v3-0-0"></a>
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
  - `expect(msg="")` - Returns data if successful, raises `ResultUnwrapException` with an optional custom message if not successful
  - `unwrap_or(default)` - Returns data if successful, otherwise returns default value
- **ResultUnwrapException**: New exception class for unwrap failures
- **Exception Methods**: `get_error_code()` function for returning user-defined error codes
- **Tests**: Added `Result_test.py` with comprehensive Result object tests

### Changed

- **Default Workers**: `thread_pool_executor` and `process_pool_executor` now default to `os.cpu_count()`
- **Timeout Handling**: Improved `as_completed` timeout scaling in executors
- **Examples Updated**: All example files updated to reflect new import system
- **Tests Refactored**: Removed duplicate/overlapping tests for cleaner test suite

### Removed

- **Examples.md**: Removed from repository (examples still available in `examples/` directory)

---

<a id="v2-1-3"></a>
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

<a id="v2-1-2"></a>
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

<a id="v2-1-1"></a>
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

<a id="v2-1-0"></a>
## [2.1.0] - 2026-01-16

### Added

- Shared Memory IPC support for GlobalVars
  - `shm_gen()`, `shm_sync()`, `shm_update()`, `shm_get()`, `shm_close()`
  - Optional `multiprocessing.Lock` for inter-process synchronization
  - LRU cache for shared memory objects (`shm_cache_management()`)
- Context manager support for GlobalVars (`with gv:`)

### Changed

- `ExceptionTracker.get_exception_info()` params type: `dict` → `Tuple[Tuple, dict]`
