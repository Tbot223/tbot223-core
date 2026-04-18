<!-- markdownlint-disable-file MD041 -->

[한국어 (Korean)](../ko/Examples.md)

> This document is based on v4.0.0.

# Examples

All examples are **self-contained, runnable scripts**. Each prints `TEST COMPLETE` on success.

<details>
<summary>Table of Contents</summary>

- [Running Examples](#running-examples)
- [Result](#result)
- [AppCore](#appcore)
- [FileManager](#filemanager)
- [LogSys](#logsys)
- [ExceptionTracker](#exceptiontracker)
- [Utils](#utils)
- [GlobalVars](#globalvars)
- [DecoratorUtils](#decoratorutils)
</details>

## Running Examples

```bash
# Run any example directly
python examples/Result/unwrap.py
python examples/FileManager/atomic_write.py
```

Logs and temporary files are written to `examples/.OtherFiles/`.

## Result

The `Result` NamedTuple is the core return type for every public function. These examples show how to create, inspect, and extract values from it.

| File | What it demonstrates |
|------|----------------------|
| [Result.py](../examples/Result/Result.py) | Create `Result` objects manually and access each field — `success`, `error`, `context`, `data`. Shows `True`, `False`, and `None` (cancelled) states. |
| [unwrap.py](../examples/Result/unwrap.py) | `unwrap()` extracts `data` when `success=True`. When `success=False` or `None`, it raises `ResultUnwrapException` with the error message, context, and data. |
| [expect.py](../examples/Result/expect.py) | `expect(msg)` works like `unwrap()` but lets you provide a custom error message. Useful for adding context-specific failure descriptions. |
| [unwrap_or.py](../examples/Result/unwrap_or.py) | `unwrap_or(default)` returns `data` on success, or the provided default value on failure — never raises. Ideal for optional operations with fallback values. |

## AppCore

Application-level utilities: parallel execution, CLI input, localization, and process control.

| File | What it demonstrates |
|------|----------------------|
| [thread_pool_executor.py](../examples/AppCore/thread_pool_executor.py) | Run multiple functions concurrently with `ThreadPoolExecutor`. Shows `(function, kwargs_dict)` task format, `workers` limit, and collecting ordered per-task `Result` objects. |
| [process_pool_executor.py](../examples/AppCore/process_pool_executor.py) | Run CPU-bound tasks with `ProcessPoolExecutor` (spawn context). Shows `chunk_size` modes: `None` (single batch), `0` (auto), positive int (explicit), and ordered per-task `Result` objects. |
| [get_text_by_lang.py](../examples/AppCore/get_text_by_lang.py) | Load localized text from `Languages/{lang}.json` files. Results are cached internally and automatically reloaded on a cache miss. Unsupported languages fall back to `default_lang`. |
| [safe_CLI_input.py](../examples/AppCore/safe_CLI_input.py) | Prompt for validated user input with type conversion. Supports `str`, `int`, `float`, `bool`; bool accepts values such as `"true"/"false"`, `"yes"/"no"`, `"y"/"n"`, `"1"/"0"`, `"on"/"off"`, and `"enable"/"disable"`. Handles `EOFError` and `KeyboardInterrupt`. |
| [clear_console.py](../examples/AppCore/clear_console.py) | Clear the terminal screen. Uses `cls` on Windows, `clear` on Unix. |
| [exit_application.py](../examples/AppCore/exit_application.py) | Gracefully terminate the process with `sys.exit()`. Optional `pause=True` waits for user input before exiting. |
| [restart_application.py](../examples/AppCore/restart_application.py) | Restart the current Python process using `os.execv()`. Optional `pause=True` waits before restarting. |
| [ResultWrapper.py](../examples/AppCore/ResultWrapper/ResultWrapper.py) | `@ResultWrapper()` decorator that wraps any function's return in a `Result`. If the function already returns a `Result`, it passes through unchanged. Exceptions become `Result(False, ...)`. Preserves `__name__` and `__doc__`. |

## FileManager

Safe file-system operations with atomic writes, file locking, and JSON handling.

| File | What it demonstrates |
|------|----------------------|
| [atomic_write.py](../examples/FileManager/atomic_write.py) | Write data atomically — writes to a temp file first, then renames to the target path. If the write fails mid-way, the original file is left untouched. Parent directories are created automatically. |
| [read_file.py](../examples/FileManager/read_file.py) | Read file content in text mode (`str`) or binary mode (`bytes`) via `as_bytes=True`. Files larger than 10 MB are automatically locked during read. |
| [write_json.py](../examples/FileManager/write_json.py) | Serialize a Python object as JSON and write it to disk. Uses `atomic_write()` internally. Configurable `indent` (default 4 spaces). |
| [read_json.py](../examples/FileManager/read_json.py) | Read and parse a JSON file into a Python object. Returns the parsed object in `Result.data`. |
| [list_of_files.py](../examples/FileManager/list_of_files.py) | List files in a directory. Optional `extensions` filter (e.g. `[".json", ".txt"]`). Optional `only_name=True` returns file stems without extensions. |
| [exist.py](../examples/FileManager/exist.py) | Check whether a file or directory exists. Returns `Result(True, None, None, True/False)`. Note: `exist()` is a deprecated alias — use `exists()`. |
| [create_directory.py](../examples/FileManager/create_directory.py) | Create a directory including any missing parents (`parents=True`, `exist_ok=True`). |
| [delete_file.py](../examples/FileManager/delete_file.py) | Delete a single file. Uses `os.chmod()` to override read-only permissions before deletion. |
| [delete_directory.py](../examples/FileManager/delete_directory.py) | Recursively delete a directory and all its contents using `shutil.rmtree()`. |

## LogSys

Structured logging with automatic timestamped file organization.

| File | What it demonstrates |
|------|----------------------|
| [make_logger.py](../examples/LogSys/LoggerManager/make_logger.py) | Create a named logger with file and console handlers via `LoggerManager.make_logger()`. `make_logger()` returns a success message; use `get_logger()` to retrieve the actual logger instance. Log files are organized as `{resolved_base_dir}/{second_log_dir}/{timestamp}_log/{logger_name}.log`. |
| [get_logger.py](../examples/LogSys/LoggerManager/get_logger.py) | Retrieve an existing named logger instance with `LoggerManager.get_logger()`. Returns `Result(False, ...)` if the name doesn't exist. |
| [stop_stream_handlers.py](../examples/LogSys/LoggerManager/stop_stream_handlers.py) | Remove the console (stream) handler from a logger at runtime, so it only writes to its log file. |
| [log_message.py](../examples/LogSys/Log/log_message.py) | Send structured log messages via `Log.log_message(level, message)`. Level can be a string (`"INFO"`, `"DEBUG"`) or int (`10`, `20`). |
| [get_instance.py](../examples/LogSys/SimpleSetting/get_instance.py) | One-call setup with `SimpleSetting` — creates `LoggerManager`, `Log`, and `logging.Logger` together. Returns them as a tuple via `get_instance()`. |

## ExceptionTracker

Comprehensive exception tracking with system information, source location, and masking.

| File | What it demonstrates |
|------|----------------------|
| [get_exception_location.py](../examples/Exception/get_exception_location.py) | Extract the file, line number, and function name where an exception was raised. Returns a formatted string: `"'file.py', line 42, in function_name"`. |
| [get_exception_info.py](../examples/Exception/get_exception_info.py) | Build a detailed error payload dictionary including error type/message, source location, origin location, timestamp, traceback, input context, and system info. Supports `mask_tuple` for hiding sensitive fields. |
| [get_exception_return.py](../examples/Exception/get_exception_return.py) | Build a standardized `Result(False, error_message, location, error_info_dict)` from a caught exception. Internally calls `get_exception_info()`. |
| [get_error_code.py](../examples/Exception/get_error_code.py) | Map exception types to user-defined error codes. Pass a dict like `{ValueError: 1001, KeyError: 1002}` and get back the matching code for a caught exception. |
| [ExceptionTrackerDecorator.py](../examples/Exception/ExceptionTrackerDecorator.py) | `@ExceptionTrackerDecorator()` wraps a function so that exceptions are caught and returned as `Result(False, ...)`. Successful returns pass through unchanged. Supports `mask_tuple` for sensitive data. Preserves `__name__` and `__doc__`. |

## Utils

Utility functions for hashing, path operations, and data manipulation.

| File | What it demonstrates |
|------|----------------------|
| [hashing.py](../examples/Utils/Utils/hashing.py) | Hash a string with `md5`, `sha1`, `sha256` (default), or `sha512`. Returns the hex digest. Note: hashing is a one-way operation, not encryption. |
| [pbkdf2_hmac.py](../examples/Utils/Utils/pbkdf2_hmac.py) | Generate a PBKDF2-HMAC password hash with a random salt, then verify it. Shows `pbkdf2_hmac()` for generation and `verify_pbkdf2_hmac()` for verification. |
| [str_to_path.py](../examples/Utils/Utils/str_to_path.py) | Convert a string to a `pathlib.Path` object wrapped in a `Result`. |
| [insert_at_intervals.py](../examples/Utils/Utils/insert_at_intervals.py) | Insert an element into a list or string at regular intervals. `at_start=True` counts from the beginning, `False` from the end. |
| [find_keys_by_value.py](../examples/Utils/Utils/find_keys_by_value.py) | Search dictionary keys whose values satisfy a comparison (`eq`, `ne`, `gt`, `ge`, `lt`, `le`). Supports nested dict search with `nested=True` and configurable output format (`flat`, `forest`, `path`). |

## GlobalVars

Thread-safe global variable management with shared memory IPC support.

| File | What it demonstrates |
|------|----------------------|
| [basic_usage.py](../examples/Utils/GlobalVars/basic_usage.py) | Core operations: `set()`, `get()`, `delete()`, `clear()`, `exists()`, `list_vars()`. All return `Result` objects. `set()` raises `KeyError` if key exists unless `overwrite=True`. |
| [attribute_and_call.py](../examples/Utils/GlobalVars/attribute_and_call.py) | Alternative access syntax: `gv.name = "hello"` (attribute) and `gv("name", "hello")` (call). Both map to `set()`/`get()` internally. |
| [lock_and_context.py](../examples/Utils/GlobalVars/lock_and_context.py) | Thread-safe operations with the built-in `RLock` via `gv.lock()` or the context manager `with gv:`. |
| [shared_memory.py](../examples/Utils/GlobalVars/shared_memory.py) | Full shared memory IPC flow: `shm_gen()` creates a block with optional lock, `shm_sync()` writes variables to shared memory (JSON by default), `shm_update()` reads back, `shm_connect()` attaches from another process, `shm_close()` cleans up. Owner calls `shm_close(name)` to unlink; non-owners use `shm_close(name, close_only=True)`. |

## DecoratorUtils

| File | What it demonstrates |
|------|----------------------|
| [count_runtime.py](../examples/Utils/DecoratorUtils/count_runtime.py) | `@DecoratorUtils.count_runtime()` decorator prints how long a function takes to execute. Preserves `__name__` and `__doc__` via `functools.wraps`. |
