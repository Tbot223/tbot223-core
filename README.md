# tbot223-core

[![PyPI](https://img.shields.io/pypi/v/tbot223-core)](https://pypi.org/project/tbot223-core/)
[![Python](https://img.shields.io/pypi/pyversions/tbot223-core)](https://pypi.org/project/tbot223-core/)
[![License](https://img.shields.io/pypi/l/tbot223-core)](LICENSE)

<details>
<summary>Table of Contents</summary>

- [Who This Is For](#who-this-is-for)
- [Not For Everyone](#not-for-everyone)
- [Why tbot223-core?](#why-tbot223-core)
- [Design Tradeoffs](#design-tradeoffs)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Imports](#imports)
- [Core Modules](#core-modules)
- [The Result Pattern](#the-result-pattern)
- [Examples](#examples)
- [Version Policy](#version-policy)
- [Documentation](#documentation)
- [License](#license)
- [Links](#links)
</details>

A zero-dependency Python toolkit for file operations, logging, exception tracking, and parallel execution, built around a Result pattern for predictable error handling.

[한국어 (Korean)](README.ko.md)

## Who This Is For

- Scripts, automation, and internal tools that benefit from predictable success/failure handling
- Codebases that prefer checking return values over catching exceptions at every call site
- Teams that want file operations, logging, exception tracking, and execution helpers to follow one consistent return shape

## Not For Everyone

- If you want a fully exception-first, idiomatic Python API surface
- If you prefer very small, single-purpose libraries over a bundled toolkit
- If you want failures to interrupt control flow by default instead of being handled as values

## Why tbot223-core?

Every public function returns a `Result` object instead of raising exceptions.
This gives you a consistent, predictable shape for every operation — success or failure.
No more wrapping every call in `try/except`; just check `result.success` or call `.unwrap()`.

The core `Result` type was designed independently; the convenience methods `unwrap()`, `expect()`, and `unwrap_or()` were later inspired by Rust's `Result<T, E>`.

This package is a good fit if you:

- Prefer explicit success/failure flows over catching exceptions everywhere
- Want a ready-to-use toolkit for tools, scripts, and internal utilities
- Prefer a consistent return shape over unexpected runtime tracebacks

This library follows an explicit success/failure pattern rather than Python's traditional exception-driven style.

## Design Tradeoffs

- Public APIs favor a consistent `Result` shape over Python's usual raise-on-failure style
- Callers write a little more branching code up front, but error handling becomes more predictable and easier to standardize
- The library intentionally groups several utilities under one package so internal tools can share the same patterns across file I/O, logging, exception tracking, and parallel work

## Features

- **Consistent Result Objects** — All functions return a standardized `Result` NamedTuple with `success`, `error`, `context`, and `data` fields
- **Robust File Management** — Atomic writes (temp file + rename), JSON I/O, file locking for large files, directory operations
- **Advanced Logging System** — Named loggers with automatic timestamped file organization, configurable levels, and a single-step `SimpleSetting` helper
- **Exception Tracking** — Source location extraction, full traceback capture, system info caching, sensitive data masking
- **Parallel Execution** — `ThreadPoolExecutor` and `ProcessPoolExecutor` wrappers with support for timeouts, chunking, and worker limits
- **Localization Support** — JSON-based localization with internal caching and automatic reloads
- **Shared Memory IPC** — Process-safe global variables with JSON/pickle serialization, LRU-cached handles, and ownership tracking

## Installation

```bash
pip install tbot223-core
```

Requires Python 3.10 - 3.14. Zero external dependencies.

## Quick Start

### 1. File operations with Result pattern

```python
from tbot223_core import FileManager

fm = FileManager()

# Every operation returns a Result — no exceptions to catch
result = fm.write_json("config.json", {"key": "value"})

if result.success:
    print("Saved successfully")
else:
    print(f"Failed: {result.error}")

# unwrap() — returns data on success, raises ResultUnwrapException on failure
data = fm.read_json("config.json").unwrap()

# expect() — like unwrap(), but with a custom error message
data = fm.read_json("config.json").expect("Config file is required")

# unwrap_or() — returns data on success, or the default value on failure
data = fm.read_json("missing.json").unwrap_or({"default": True})
```

### 2. Auto-wrap any function with ResultWrapper

```python
from tbot223_core import ResultWrapper

@ResultWrapper()
def divide(a, b):
    return a / b

result = divide(10, 2)
print(result.success)  # True
print(result.data)     # 5.0

result = divide(10, 0)
print(result.success)  # False
print(result.error)    # "ZeroDivisionError :division by zero"
```

### 3. Structured logging

```python
from tbot223_core.LogSys import SimpleSetting

setting = SimpleSetting(
    base_dir=".",
    second_log_dir="my_app",
    logger_name="AppLogger",
)
logger_manager, log, logger = setting.get_instance()

log.log_message("INFO", "Application started")
log.log_message("ERROR", "Something went wrong")
# Log file: ./my_app/{timestamp}_log/AppLogger.log
```

### 4. Parallel execution

```python
from tbot223_core import AppCore
import time

app = AppCore()

def slow_task(n):
    time.sleep(0.1)
    return n * 2

tasks = [(slow_task, {"n": i}) for i in range(10)]
result = app.thread_pool_executor(tasks, workers=4, timeout=5.0)
print([task_result.data for task_result in result.data])  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

## Imports

All core classes are available directly from `tbot223_core`:

```python
from tbot223_core import (
    AppCore,                    # Parallel execution, CLI input, localization
    ResultWrapper,              # Decorator: wraps returns in Result
    FileManager,                # File I/O, JSON, atomic writes
    LoggerManager, Log,         # Structured logging
    ExceptionTracker,           # Exception info extraction
    ExceptionTrackerDecorator,  # Decorator: auto exception-to-Result
    Utils,                      # Hashing, path conversion, data manipulation
    GlobalVars,                 # Thread-safe global variables + shared memory
    DecoratorUtils,             # Runtime measurement
    Result,                     # The Result NamedTuple itself
)

# For Result-related exceptions:
from tbot223_core.Result import ResultUnwrapException

# For SimpleSetting (not re-exported at top level):
from tbot223_core.LogSys import SimpleSetting
```

## Core Modules

| Module | Purpose | Key Methods |
|--------|---------|-------------|
| `AppCore` | Parallel execution, console, CLI input, localization | `thread_pool_executor()`, `process_pool_executor()`, `safe_CLI_input()`, `get_text_by_lang()` |
| `ResultWrapper` | Decorator: wraps any function's return in a `Result` | `@ResultWrapper()` |
| `FileManager` | Atomic writes, file/JSON I/O, directory operations | `atomic_write()`, `read_file()`, `write_json()`, `read_json()`, `exists()` |
| `LogSys` | Structured logging with auto file management | `make_logger()`, `get_logger()`, `log_message()`, `SimpleSetting` |
| `ExceptionTracker` | Exception location/info tracking, error code mapping | `get_exception_info()`, `get_exception_return()`, `get_error_code()` |
| `Utils` | Hashing, path conversion, PBKDF2, data manipulation | `hashing()`, `pbkdf2_hmac()`, `find_keys_by_value()`, `insert_at_intervals()` |
| `GlobalVars` | Thread-safe global variables with shared memory IPC | `set()`, `get()`, `shm_gen()`, `shm_sync()`, `shm_update()`, `shm_close()` |
| `DecoratorUtils` | Runtime measurement | `@DecoratorUtils.count_runtime()` |

See [API Reference](docs/API.md) for full method signatures, parameters, and return values.

## The Result Pattern

All public functions return a `Result` NamedTuple:

```python
Result(
    success: Optional[bool],  # True = success, False = failure, None = cancelled
    error: Optional[str],     # Error message (None on success)
    context: Optional[str],   # Additional context (None on success)
    data: Any,                # Returned data, or failure details
)
```

On success, `data` contains the returned value. On failure, it may contain `None`, method-specific detail data, or a structured `error_info` dictionary produced by `ExceptionTracker`.

### Methods

| Method | Behavior on success | Behavior on failure |
|--------|-------------------|-------------------|
| `unwrap()` | Returns `data` | Raises `ResultUnwrapException` |
| `expect(msg)` | Returns `data` | Raises `ResultUnwrapException` with custom `msg` |
| `unwrap_or(default)` | Returns `data` | Returns `default` |

When `unwrap()` or `expect()` raises on a failed result, the exception keeps the original `Result.data` payload in `ResultUnwrapException.data`.

## Examples

The [examples/](examples/) directory contains 40+ runnable scripts organized by module.
Each script is self-contained and prints `TEST COMPLETE` on success.

| Module | Examples |
|--------|----------|
| Result | Basic usage, `unwrap()`, `expect()`, `unwrap_or()` |
| AppCore | Thread/process pool executors, CLI input, multi-language, ResultWrapper |
| FileManager | Atomic write, JSON I/O, file listing, directory operations |
| LogSys | Logger creation, log messages, SimpleSetting single-step setup |
| ExceptionTracker | Exception info, location tracking, error codes, decorator |
| Utils | Hashing, PBKDF2, path conversion, interval insertion, dict search |
| GlobalVars | Basic CRUD, attribute/call syntax, thread locking, shared memory IPC |
| DecoratorUtils | Runtime measurement |

See [Examples.md](docs/Examples.md) for a full listing with descriptions.

## Version Policy

- The `4.x` line aims to keep public behavior stable unless a change clearly fixes broken or misleading behavior
- Breaking changes are called out explicitly in the [Release Notes](docs/RELEASE_NOTES.md) and [Migration Guide](docs/MIGRATION_GUIDE.md)
- Deprecation aliases may remain for compatibility, but new code should follow the current documented names and semantics

## Documentation

- [API Reference](docs/API.md) — Full method signatures, parameters, return values, and usage examples
- [Migration Guide](docs/MIGRATION_GUIDE.md) — Upgrade paths from 2.x or 3.x to 4.x
- [Release Notes](docs/RELEASE_NOTES.md) — Changelog and version history
- [Examples](docs/Examples.md) — 40+ runnable example scripts with descriptions
- [한국어 문서 (Korean)](README.ko.md)

## License

[Apache License 2.0](LICENSE)

## Links

- [GitHub](https://github.com/Tbot223/tbot223-core)
- [PyPI](https://pypi.org/project/tbot223-core/)
- Author: tbot223 (tbotxyz@gmail.com)
