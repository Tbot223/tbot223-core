<!-- markdownlint-disable-file MD041 -->

[한국어 (Korean)](../ko/API.md)

> This document is based on tbot223-core v4.0.0.

# API Reference

> Python 3.10 - 3.14

For installation and quick start, see the [README](README.md).
For runnable example scripts, see the [Examples](Examples.md).

<details>
<summary>Table of Contents</summary>

- [AppCore](#appcore)
- [ResultWrapper](#resultwrapper)
- [FileManager](#filemanager)
- [LogSys](#logsys) — [LoggerManager](#loggermanager) · [Log](#log) · [SimpleSetting](#simplesetting)
- [ExceptionTracker](#exceptiontracker)
- [ExceptionTrackerDecorator](#exceptiontrackerdecorator)
- [Result](#result-object)
- [Utils](#utils)
- [GlobalVars](#globalvars)
- [DecoratorUtils](#decoratorutils)
- [Error Information Structure](#error-information-structure)
- [Shared Memory Usage](#shared-memory-usage)

</details>

## AppCore

Core application utilities for parallel execution, localization, console management, and CLI input.

### Constructor

```python
AppCore(
    is_logging_enabled: bool = True,
    is_debug_enabled: bool = False,
    default_lang: str = "en",
    base_dir: Union[str, Path] = None,
    logger_manager_instance: Optional[LoggerManager] = None,
    logger: Optional[logging.Logger] = None,
    log_instance: Optional[Log] = None,
    filemanager: Optional[FileManager] = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_logging_enabled` | `bool` | `True` | Enable internal logging to file |
| `is_debug_enabled` | `bool` | `False` | Enable debug-level log output |
| `default_lang` | `str` | `"en"` | Default language code for `get_text_by_lang()` |
| `base_dir` | `Union[str, Path]` | `None` | Base directory for the app; `None` uses CWD. `Languages/` is created here and internal logs go under `{base_dir}/logs/app_core/` |
| `logger_manager_instance` | `Optional[LoggerManager]` | `None` | Share an existing LoggerManager |
| `logger` | `Optional[logging.Logger]` | `None` | Share an existing logger |
| `log_instance` | `Optional[Log]` | `None` | Share an existing Log |
| `filemanager` | `Optional[FileManager]` | `None` | Share an existing FileManager for language file I/O |

### Methods

#### `thread_pool_executor(data, workers, override, timeout) -> Result`

```python
def thread_pool_executor(
    self,
    data: List[Tuple[Callable[..., Any], Dict]],
    workers: Optional[int] = None,
    override: bool = False,
    timeout: float = None,
) -> Result
```

Execute a list of tasks concurrently using `ThreadPoolExecutor`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `List[Tuple[Callable, Dict]]` | — | List of `(function, kwargs_dict)` pairs |
| `workers` | `Optional[int]` | `None` | Max worker threads; `None` defaults to `os.cpu_count()` |
| `override` | `bool` | `False` | If `True`, skip the `workers <= cpu_count` limit |
| `timeout` | `float` | `None` | Per-future timeout in seconds |

**Returns:** `Result(True, None, None, [task_result1, task_result2, ...])` — an ordered list of per-task `Result` objects. Each inner `Result.data` contains that task's return value.

---

#### `process_pool_executor(data, workers, override, timeout, chunk_size) -> Result`

```python
def process_pool_executor(
    self,
    data: List[Tuple[Callable[..., Any], Dict]],
    workers: Optional[int] = None,
    override: bool = False,
    timeout: float = None,
    chunk_size: Optional[int] = None,
) -> Result
```

Execute tasks concurrently using `ProcessPoolExecutor` with `spawn` start method.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `List[Tuple[Callable, Dict]]` | — | List of `(function, kwargs_dict)` pairs |
| `workers` | `Optional[int]` | `None` | Max worker processes; `None` defaults to `os.cpu_count()` |
| `override` | `bool` | `False` | If `True`, skip the `workers <= cpu_count` limit |
| `timeout` | `float` | `None` | Per-future timeout in seconds |
| `chunk_size` | `Optional[int]` | `None` | `None` = single executor for all tasks, `0` = auto chunk, positive int = explicit batch size |

**Returns:** `Result(True, None, None, [task_result1, task_result2, ...])` — an ordered list of per-task `Result` objects. Each inner `Result.data` contains that task's return value.

---

#### `get_text_by_lang(key, lang) -> Result`

```python
def get_text_by_lang(self, key: str, lang: str) -> Result
```

Retrieve localized text from a JSON language file. Language files must be placed in a `Languages/` directory. Results are cached internally and automatically reloaded on a cache miss. If `lang` is not supported, AppCore falls back to `default_lang`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `str` | The key to look up in the language JSON |
| `lang` | `str` | Language code (e.g. `"en"`, `"ko"`) — maps to `Languages/{lang}.json` |

**Returns:** `Result(True, None, None, "translated text")` or `Result(False, ...)` if key or file not found.

> **WARNING**: You must create JSON language files under a `Languages/` directory before calling this method. See [get_text_by_lang.py](../examples/AppCore/get_text_by_lang.py).

---

#### `safe_CLI_input(prompt, input_type, ...) -> Result`

```python
def safe_CLI_input(
    self,
    prompt: str = "",
    input_type: type = str,
    other_type: bool = False,
    valid_options: List[str] = None,
    case_sensitive: bool = False,
    allow_empty: bool = False,
    max_retries: int = 10,
) -> Result
```

Prompt the user for input with validation, type conversion, and interrupt handling.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | `""` | The prompt text shown to the user |
| `input_type` | `type` | `str` | Expected type: `str`, `int`, `float`, or `bool`. With `other_type=True`, custom conversion callables are also allowed |
| `other_type` | `bool` | `False` | Set to `True` to allow custom `input_type` converters beyond the built-in supported types |
| `valid_options` | `List[str]` | `None` | Whitelist of accepted values |
| `case_sensitive` | `bool` | `False` | Whether validation is case-sensitive |
| `allow_empty` | `bool` | `False` | Whether empty input is accepted |
| `max_retries` | `int` | `10` | Max retry attempts before returning failure |

**Bool type**: accepts `"true"`, `"t"`, `"yes"`, `"y"`, `"1"`, `"on"`, `"enable"`, `"enabled"` for `True`, and `"false"`, `"f"`, `"no"`, `"n"`, `"0"`, `"off"`, `"disable"`, `"disabled"` for `False` (case-insensitive).

**Returns:** `Result(True, None, None, converted_value)` or `Result(False, ...)` on interrupt / max retries.

---

#### `clear_console() -> Result`

```python
def clear_console(self) -> Result
```

Clear the terminal screen. Uses `cls` on Windows, `clear` on Unix.

---

#### `exit_application(code, pause) -> Result`

```python
def exit_application(self, code: int = 0, pause: bool = False) -> Result
```

Terminate the current process. On success, this method does not return because it calls `sys.exit()`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | `int` | `0` | Exit code passed to `sys.exit()` |
| `pause` | `bool` | `False` | If `True`, waits for user input before exiting |

---

#### `restart_application(pause) -> Result`

```python
def restart_application(self, pause: bool = False) -> Result
```

Restart the current Python process using `os.execv()`. On success, this method does not return because it replaces the current process.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pause` | `bool` | `False` | If `True`, waits for user input before restarting |

---

## ResultWrapper

A decorator class that wraps any function's return value in a `Result`. If the function already returns a `Result`, it passes through unchanged. Uncaught exceptions are caught and converted with `ExceptionTracker.get_exception_return(...)`, so failures keep structured exception details in `data`.

### Constructor

```python
ResultWrapper()
```

No parameters. Use as a decorator:

```python
from tbot223_core import ResultWrapper

@ResultWrapper()
def divide(a, b):
    return a / b

result = divide(10, 2)
print(result.success, result.data)  # True, 5.0

result = divide(10, 0)
print(result.success, result.error)  # False, "ZeroDivisionError :division by zero"
```

Function metadata (`__name__`, `__doc__`) is preserved via `functools.wraps`.

---

## FileManager

Safe and reliable file operations with atomic writes, file locking, and JSON handling.

### Constructor

```python
FileManager(
    is_logging_enabled: bool = True,
    is_debug_enabled: bool = False,
    base_dir: Union[str, Path] = None,
    logger_manager_instance: Optional[LoggerManager] = None,
    logger: Optional[logging.Logger] = None,
    log_instance: Optional[Log] = None,
    Utils_instance: Optional[Utils] = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_logging_enabled` | `bool` | `True` | Enable internal logging |
| `is_debug_enabled` | `bool` | `False` | Enable debug-level output |
| `base_dir` | `Union[str, Path]` | `None` | Base directory for log files; `None` = CWD. **Note:** this is the logging directory, not the I/O base — file operation paths are always absolute or relative to CWD |
| `Utils_instance` | `Optional[Utils]` | `None` | Share an existing Utils instance |

File locking is applied automatically for files larger than 10 MB (`LOCK_FILE_SIZE_THRESHOLD`). Cross-platform: uses `fcntl` on Unix, `msvcrt` on Windows.

### Methods

#### `atomic_write(file_path, data) -> Result`

```python
def atomic_write(self, file_path: Union[str, Path], data: Any) -> Result
```

Write data to a file atomically. Writes to a temporary file first, then renames it to the target path. If the write fails, the original file is left untouched.

Parent directories are created automatically if they don't exist.

---

#### `read_file(file_path, as_bytes) -> Result`

```python
def read_file(self, file_path: Union[str, Path], as_bytes: bool = False) -> Result
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `Union[str, Path]` | — | Path to the file |
| `as_bytes` | `bool` | `False` | `True` = read in binary mode (`"rb"`), `False` = text mode (`"r"`, UTF-8) |

**Returns:** `Result(True, None, None, file_content_string_or_bytes)`

---

#### `write_json(file_path, data, indent) -> Result`

```python
def write_json(self, file_path: Union[str, Path], data: Any, indent: int = 4) -> Result
```

Serialize `data` as JSON and write it to disk with optional indentation. Uses `atomic_write()` internally.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `Union[str, Path]` | — | Target file path |
| `data` | `Any` | — | JSON-serializable Python object |
| `indent` | `int` | `4` | Number of spaces for pretty-printing |

---

#### `read_json(file_path) -> Result`

```python
def read_json(self, file_path: Union[str, Path]) -> Result
```

Read and parse a JSON file.

**Returns:** `Result(True, None, None, parsed_python_object)`

---

#### `list_of_files(dir_path, extensions, only_name) -> Result`

```python
def list_of_files(
    self,
    dir_path: Union[str, Path],
    extensions: List[str] = None,
    only_name: bool = False,
) -> Result
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dir_path` | `Union[str, Path]` | — | Directory to scan |
| `extensions` | `List[str]` | `None` | Filter by extensions (e.g. `[".json", ".txt"]`); `None` = all files |
| `only_name` | `bool` | `False` | `True` = return file stems only (no extension), `False` = return full paths |

**Returns:** `Result(True, None, None, [path1, path2, ...])`

---

#### `exists(path) -> Result`

```python
def exists(self, path: Union[str, Path]) -> Result
```

Check whether a file or directory exists.

**Returns:** `Result(True, None, None, True)` if exists, `Result(True, None, None, False)` if not.

> `exist()` is a deprecated alias — use `exists()` instead.

---

#### `delete_file(file_path) -> Result`

```python
def delete_file(self, file_path: Union[str, Path]) -> Result
```

Delete a single file. Uses `os.chmod()` to override read-only permissions before deletion.

---

#### `delete_directory(dir_path) -> Result`

```python
def delete_directory(self, dir_path: Union[str, Path]) -> Result
```

Recursively delete a directory and all its contents using `shutil.rmtree()`.

---

#### `create_directory(dir_path) -> Result`

```python
def create_directory(self, dir_path: Union[str, Path]) -> Result
```

Create a directory, including any missing parent directories (`parents=True`, `exist_ok=True`).

---

## LogSys

Structured logging system with automatic file organization.

### LoggerManager

Manages named loggers with file and console handlers.

#### Constructor

```python
LoggerManager(
    base_dir: Union[str, Path] = None,
    second_log_dir: Union[str, Path] = "default",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_dir` | `Union[str, Path]` | `None` | Root directory for log storage. If `None`, uses `Path.cwd() / "logs"` |
| `second_log_dir` | `Union[str, Path]` | `"default"` | Subdirectory name directly under the resolved `base_dir` |

Log files are organized as: `{resolved_base_dir}/{second_log_dir}/{timestamp}_log/{logger_name}.log`

#### Methods

##### `make_logger(logger_name, log_level, timestamp, **kwargs) -> Result`

```python
def make_logger(
    self,
    logger_name: str,
    log_level: Union[int, str] = logging.INFO,
    timestamp: Any = None,
    **kwargs,
) -> Result
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `logger_name` | `str` | — | Unique name for the logger |
| `log_level` | `Union[int, str]` | `logging.INFO` | Minimum log level (e.g. `logging.DEBUG`, `logging.WARNING`, or `"DEBUG"`) |
| `timestamp` | `Any` | `None` | Custom timestamp for the log directory name; `None` = current time |

> `time=...` is accepted as a deprecated alias for `timestamp`.

**Returns:** `Result(True, None, None, "Logger 'name' created successfully.")`

Retrieve the actual `logging.Logger` instance with `get_logger(logger_name)`.

##### `get_logger(logger_name) -> Result`

```python
def get_logger(self, logger_name: str) -> Result
```

Retrieve an existing named logger instance.

**Returns:** `Result(True, None, None, logging.Logger)` or `Result(False, ...)` if not found.

##### `stop_stream_handlers(logger) -> Result`

```python
def stop_stream_handlers(self, logger: logging.Logger) -> Result
```

Remove the console (stream) handler from a logger. After calling this, the logger only writes to its file handler.

> **WARNING**: assumes the stream handler is the second handler (index 1) as created by `make_logger()`. External handler modifications may cause unexpected behavior.

---

### Log

Wrapper around `logging.Logger` for structured `log_message()` calls.

#### Constructor

```python
Log(logger: logging.Logger = None)
```

#### Methods

##### `log_message(level, message) -> Result`

```python
def log_message(self, level: Optional[Union[int, str]], message: str) -> Result
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | `Union[int, str]` | Log level — integer (e.g. `10`, `20`) or string (e.g. `"INFO"`, `"DEBUG"`) |
| `message` | `str` | The message to log |

---

### SimpleSetting

One-call helper that creates `LoggerManager`, `Log`, and `logging.Logger` together.

#### Constructor

```python
SimpleSetting(
    base_dir: Union[str, Path],
    second_log_dir: Union[str, Path],
    logger_name: str,
    log_level: Union[int, str] = logging.INFO,
)
```

#### Methods

##### `get_instance() -> Tuple[LoggerManager, Log, logging.Logger]`

```python
def get_instance(self) -> Tuple[LoggerManager, Log, logging.Logger]
```

Returns a tuple of `(LoggerManager, Log, logging.Logger)` ready to use.

```python
from tbot223_core import LoggerManager, Log
from tbot223_core.LogSys import SimpleSetting

setting = SimpleSetting(base_dir=".", second_log_dir="my_app", logger_name="AppLogger")
logger_manager, log, logger = setting.get_instance()
log.log_message("INFO", "Application started")
```

---

## ExceptionTracker

Comprehensive error tracking with system information caching.

System information (OS, architecture, Python version, etc.) is cached once at instantiation and reused for all subsequent calls.

### Constructor

```python
ExceptionTracker()
```

### Methods

#### `get_exception_location(error) -> Result`

```python
def get_exception_location(self, error: Exception) -> Result
```

Extract the source location where the exception was raised.

**Returns:** `Result(True, None, None, "'{file}', line {line}, in {function}")`

---

#### `get_exception_info(error, user_input, params, mask_tuple) -> Result`

```python
def get_exception_info(
    self,
    error: Exception,
    user_input: Any = None,
    params: Tuple[Tuple, dict] = None,
    mask_tuple: Tuple[bool, ...] = (),
) -> Result
```

Build a detailed error payload dictionary.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `error` | `Exception` | — | The caught exception |
| `user_input` | `Any` | `None` | User input that triggered the error |
| `params` | `Tuple[Tuple, dict]` | `None` | `(args, kwargs)` of the calling function |
| `mask_tuple` | `Tuple[bool, ...]` | `()` | Mask sensitive fields. Order: `(user_input, params, traceback, computer_info)` — `True` = masked |

**Returns:** `Result(True, None, None, error_info_dict)` — see [Error Information Structure](#error-information-structure).

---

#### `get_exception_return(error, user_input, params, mask_tuple) -> Result`

```python
def get_exception_return(
    self,
    error: Exception,
    user_input: Any = None,
    params: Tuple[Tuple, dict] = ((), {}),
    mask_tuple: Tuple[bool, ...] = (),
) -> Result
```

Build a standardized failure `Result` from an exception. Internally calls `get_exception_info()`.

**Returns:** `Result(False, error_message, exception_location, error_info_dict)`

---

#### `get_error_code(error_id_map, error) -> Result`

```python
def get_error_code(self, error_id_map: dict, error: Exception) -> Result
```

Map an exception type to a user-defined error code.

| Parameter | Type | Description |
|-----------|------|-------------|
| `error_id_map` | `dict` | Mapping of `{ExceptionType: error_code}` |
| `error` | `Exception` | The caught exception |

```python
error_map = {ValueError: 1001, FileNotFoundError: 1002, KeyError: 1003}
result = tracker.get_error_code(error_map, caught_error)
print(result.data)  # 1001
```

**Returns:** `Result(True, None, None, error_code)` or `Result(False, ...)` if the exception type is not in the map.

---

## ExceptionTrackerDecorator

Decorator that wraps a function with automatic exception tracking. Successful returns pass through; exceptions are caught and returned as `Result(False, ...)`.

### Constructor

```python
ExceptionTrackerDecorator(
    mask_tuple: Tuple[bool, bool, bool, bool] = (False, False, False, False),
    tracker: ExceptionTracker = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mask_tuple` | `Tuple[bool, bool, bool, bool]` | `(False, False, False, False)` | Mask fields: `(user_input, params, traceback, computer_info)` |
| `tracker` | `ExceptionTracker` | `None` | Share an existing tracker; `None` creates a new one |

```python
from tbot223_core import ExceptionTrackerDecorator

@ExceptionTrackerDecorator(mask_tuple=(False, False, True, True))
def risky_operation(x):
    return 1 / x

result = risky_operation(0)
print(result.success)  # False
print(result.error)    # "ZeroDivisionError :division by zero"
```

Function metadata (`__name__`, `__doc__`) is preserved via `functools.wraps`.

---

## Result Object

All public functions return a `Result` NamedTuple:

```python
from tbot223_core import Result

Result(
    success: Optional[bool],  # True = success, False = failure, None = cancelled
    error: Optional[str],     # Error message (None on success)
    context: Optional[str],   # Additional context info (None on success)
    data: Any,                # The returned data, or failure details
)
```

On success, `data` contains the returned value. On failure, it may contain `None`, method-specific detail data, or a structured `error_info` dictionary returned by `ExceptionTracker`.

### Methods

#### `unwrap() -> Any`

Returns `data` if `success is True`. Raises `ResultUnwrapException` if `success is False` or `None`.

```python
data = fm.read_json("config.json").unwrap()  # raises if read fails
```

#### `expect(msg="") -> Any`

Like `unwrap()`, but raises with a custom message. If `msg` is empty, the original error message is used.

```python
data = fm.read_json("config.json").expect("Config file is required")
```

#### `unwrap_or(default) -> Any`

Returns `data` if `success is True`, otherwise returns `default`.

```python
data = fm.read_json("config.json").unwrap_or({"fallback": True})
```

### ResultUnwrapException

Raised by `unwrap()` and `expect()`. Attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `error` | `str` | The error message |
| `context` | `str` | Additional context |
| `data` | `Any` | The original `Result.data` payload, including failure detail data when present |

---

## Utils

Collection of utility functions for hashing, path operations, and data manipulation.

### Constructor

```python
Utils(
    is_logging_enabled: bool = False,
    base_dir: Union[str, Path] = None,
    logger_manager_instance: Optional[LoggerManager] = None,
    logger: Optional[logging.Logger] = None,
    log_instance: Optional[Log] = None,
)
```

### Methods

#### `str_to_path(path_str) -> Result`

```python
def str_to_path(self, path_str: str) -> Result
```

Convert a string to a `pathlib.Path` object.

**Returns:** `Result(True, None, None, Path(...))`

---

#### `hashing(data, algorithm) -> Result`

```python
def hashing(self, data: str, algorithm: str = "sha256") -> Result
```

Hash a string using the specified algorithm.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `str` | — | The string to hash |
| `algorithm` | `str` | `"sha256"` | One of: `"md5"`, `"sha1"`, `"sha256"`, `"sha512"` |

**Returns:** `Result(True, None, None, "hex_digest_string")`

> **Note**: Hashing is a one-way operation and is not encryption.

---

#### `pbkdf2_hmac(password, algorithm, iterations, salt_size) -> Result`

```python
def pbkdf2_hmac(
    self,
    password: str,
    algorithm: str,
    iterations: int,
    salt_size: int,
) -> Result
```

Generate a PBKDF2-HMAC password hash with a random salt.

| Parameter | Type | Description |
|-----------|------|-------------|
| `password` | `str` | The password to hash |
| `algorithm` | `str` | One of: `"sha1"`, `"sha256"`, `"sha512"` |
| `iterations` | `int` | Number of PBKDF2 iterations (e.g. `100000`) |
| `salt_size` | `int` | Salt size in bytes (e.g. `16`) |

**Returns:** `Result(True, None, None, {"salt_hex": "...", "hash_hex": "...", "iterations": 100000, "algorithm": "sha256"})`

---

#### `verify_pbkdf2_hmac(password, salt_hex, hash_hex, iterations, algorithm) -> Result`

```python
def verify_pbkdf2_hmac(
    self,
    password: str,
    salt_hex: str,
    hash_hex: str,
    iterations: int,
    algorithm: str,
) -> Result
```

Verify a password against an existing PBKDF2-HMAC hash.

**Returns:** `Result(True, None, None, True)` if matched, `Result(True, None, None, False)` if not.

---

#### `insert_at_intervals(data, interval, insert, at_start) -> Result`

```python
def insert_at_intervals(
    self,
    data: Union[List, str],
    interval: int,
    insert: Any,
    at_start: bool = True,
) -> Result
```

Insert an element into a list or string at regular intervals.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `Union[List, str]` | — | The list or string to modify |
| `interval` | `int` | — | Insertion interval |
| `insert` | `Any` | — | Element to insert |
| `at_start` | `bool` | `True` | `True` = count from start, `False` = count from end |

**Returns:** `Result(True, None, None, modified_data)`

---

#### `find_keys_by_value(dict_obj, threshold, comparison, nested, separator, return_mod) -> Result`

```python
def find_keys_by_value(
    self,
    dict_obj: Dict,
    threshold: Union[int, float, str, bool],
    comparison: str = "eq",
    nested: bool = False,
    separator: str = "/",
    return_mod: str = "flat",
) -> Result
```

Find dictionary keys whose values satisfy a comparison.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dict_obj` | `Dict` | — | The dictionary to search |
| `threshold` | `Union[int, float, str, bool]` | — | Value to compare against |
| `comparison` | `str` | `"eq"` | Operator: `"eq"`, `"ne"`, `"gt"`, `"ge"`, `"lt"`, `"le"` |
| `nested` | `bool` | `False` | `True` = search nested dictionaries recursively |
| `separator` | `str` | `"/"` | Key path separator for nested results. If set to `"tuple"`, the final collection is returned as a tuple instead of a list |
| `return_mod` | `str` | `"flat"` | Return format: `"flat"`, `"forest"`, `"path"` |

**Returns:** `Result(True, None, None, [matched_keys])` or `Result(True, None, None, {nested_result})`

---

## GlobalVars

Thread-safe global variable management with shared memory IPC support.

### Constructor

```python
GlobalVars(
    is_logging_enabled: bool = False,
    base_dir: Union[str, Path] = None,
    shared_memory_cache_max_size: int = 5,
    logger_manager_instance: Optional[LoggerManager] = None,
    logger: Optional[logging.Logger] = None,
    log_instance: Optional[Log] = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_logging_enabled` | `bool` | `False` | Enable internal logging |
| `base_dir` | `Union[str, Path]` | `None` | Base directory for log files |
| `shared_memory_cache_max_size` | `int` | `5` | Max number of cached shared memory handles (LRU eviction) |

### Variable Operations

#### `set(key, value, overwrite) -> Result`

```python
def set(self, key: str, value: object, overwrite: bool = False) -> Result
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | `str` | — | Variable name (must be non-empty string) |
| `value` | `object` | — | Value to store |
| `overwrite` | `bool` | `False` | `False` = raise `KeyError` if key already exists |

#### `get(key) -> Result`

```python
def get(self, key: str) -> Result
```

**Returns:** `Result(True, None, None, stored_value)` or `Result(False, ...)` if key not found.

#### `delete(key) -> Result`

```python
def delete(self, key: str) -> Result
```

#### `clear() -> Result`

```python
def clear(self) -> Result
```

Delete all stored variables.

#### `exists(key) -> Result`

```python
def exists(self, key: str) -> Result
```

**Returns:** `Result(True, None, None, True)` if exists, `Result(True, None, None, False)` if not.

#### `list_vars() -> Result`

```python
def list_vars(self) -> Result
```

**Returns:** `Result(True, None, None, ["key1", "key2", ...])`

### Alternate Access Syntax

```python
gv = GlobalVars()

# Attribute syntax
gv.name = "hello"      # set("name", "hello")
print(gv.name)          # get("name").data

# Call syntax
gv("name", "hello")     # set("name", "hello")
gv("name")              # get("name")
```

### Thread Safety

```python
# Use the built-in lock
with gv.lock():
    gv.set("counter", gv.get("counter").data + 1, overwrite=True)

# Or use the context manager
with gv:
    gv.set("counter", gv.get("counter").data + 1, overwrite=True)
```

### Shared Memory Methods

#### `shm_gen(name, size, create_lock) -> Result`

```python
def shm_gen(self, name: str = None, size: int = 1024, create_lock: bool = True) -> Result
```

Create or attach to a POSIX shared memory block.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `None` | Shared memory name. Must be a non-empty string; `None` or empty values fail validation |
| `size` | `int` | `1024` | Block size in bytes |
| `create_lock` | `bool` | `True` | `True` = create a `multiprocessing.Lock` for inter-process sync |

**Returns:** `Result(True, None, None, lock)` if `create_lock=True`, otherwise `Result(True, None, None, "success to create shared memory object")`.

**Name collision**: if the name already exists, connects to the existing block and validates `size >= requested`.

#### `shm_connect(name) -> Result`

```python
def shm_connect(self, name: str) -> Result
```

Attach to an existing shared memory block as a non-owner. Use this in worker/child processes.

#### `shm_sync(name, serialize_format) -> Result`

```python
def shm_sync(self, name: str, serialize_format: str = "json") -> Result
```

Serialize current variables and write them into shared memory.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Shared memory name |
| `serialize_format` | `str` | `"json"` | `"json"` (safe default) or `"pickle"` (trusted processes only) |

#### `shm_update(name, serialize_format) -> Result`

```python
def shm_update(self, name: str, serialize_format: str = "json") -> Result
```

Read from shared memory and merge the deserialized data into this instance's variables.

#### `shm_get(name) -> Result`

```python
def shm_get(self, name: str) -> Result
```

Return the cached `SharedMemory` handle for `name`, or attach if not yet cached.

**Returns:** `Result(True, None, None, SharedMemory)`

#### `shm_close(name, close_only) -> Result`

```python
def shm_close(self, name: str, close_only: bool = False) -> Result
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Shared memory name |
| `close_only` | `bool` | `False` | `True` = close handle only (for non-owner processes), `False` = close and unlink (for owner) |

**Ownership rule**: the process that called `shm_gen()` is the owner and should call `shm_close(name)` (with `close_only=False`) to unlink the block. Child processes that attached via `shm_connect()` should use `shm_close(name, close_only=True)`.

> **Security**: JSON is the default serialization format. Pickle deserialization of untrusted data can execute arbitrary code. Use `serialize_format="pickle"` only when all communicating processes are trusted.

---

## DecoratorUtils

### `count_runtime()`

```python
@staticmethod
def count_runtime() -> Callable
```

Decorator that prints the execution time of a function.

```python
from tbot223_core import DecoratorUtils

@DecoratorUtils.count_runtime()
def slow_function():
    time.sleep(1)

slow_function()
# Output: slow_function executed in 1.001s
```

Function metadata is preserved via `functools.wraps`.

---

## Error Information Structure

When an exception is tracked via `ExceptionTracker`, the `Result.data` field contains a detailed error payload:

```python
{
    "success": False,
    "error": {
        "type": "ValueError",           # Exception class name
        "message": "invalid literal..."  # Exception message
    },
    "location": {
        "file": "app.py",               # File where the exception was caught
        "line": 42,                      # Line number
        "function": "process_data"       # Function name
    },
    "origin_location": {
        "file": "parser.py",            # File where the exception originated
        "line": 15,                      # Line number
        "function": "parse"             # Function name
    },
    "timestamp": "2026-04-03 14:30:00",
    "input_context": {
        "user_input": "...",            # User input that triggered the error (maskable)
        "params": {                     # Function parameters (maskable)
            "args": (...),
            "kwargs": {...}
        }
    },
    "traceback": "Traceback (most recent call last):\n...",  # Full traceback (maskable)
    "computer_info": {                  # System info — cached at instantiation (maskable)
        "OS": "Darwin",
        "OS_version": "Darwin Kernel Version 25.3.0",
        "Release": "25.3.0",
        "Architecture": "arm64",
        "Processor": "arm",
        "Python_Version": "3.12.0",
        "Python_Executable": "/usr/local/bin/python3",
        "Current_Working_Directory": "/home/user/project"
    }
}
```

**Masking**: pass `mask_tuple=(user_input, params, traceback, computer_info)` to hide sensitive fields. For example, `mask_tuple=(False, False, True, True)` hides the traceback and system info.

---

## Shared Memory Usage

Full working example with inter-process communication:

```python
from tbot223_core import GlobalVars
from multiprocessing import Process

# Worker function (must be defined at module level for spawn context)
def worker(shm_name, lock):
    gv_worker = GlobalVars()
    gv_worker.shm_connect(shm_name)          # attach as non-owner
    try:
        with lock:
            gv_worker.shm_update(shm_name)    # read current state from shared memory
            current = gv_worker.get("counter").data
            gv_worker.set("counter", current + 1, overwrite=True)
            gv_worker.shm_sync(shm_name)      # write updated state back
    finally:
        gv_worker.shm_close(shm_name, close_only=True)  # non-owner: close only

if __name__ == "__main__":
    gv = GlobalVars()

    # 1. Create shared memory (4 KB) with an inter-process lock
    result = gv.shm_gen("my_shm", size=4096, create_lock=True)
    shm_lock = result.data  # multiprocessing.Lock

    # 2. Initialize variables and write to shared memory
    gv.set("counter", 0, overwrite=True)
    gv.shm_sync("my_shm")

    # 3. Spawn worker processes
    processes = [Process(target=worker, args=("my_shm", shm_lock)) for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    # 4. Read final state
    gv.shm_update("my_shm")
    print(f"Final counter: {gv.get('counter').data}")  # Output: 4

    # 5. Owner cleanup — close and unlink
    gv.shm_close("my_shm")
```

### Key Points

| Concept | Detail |
|---------|--------|
| **Serialization** | JSON by default; pass `serialize_format="pickle"` for pickle (trusted processes only) |
| **Ownership** | `shm_gen()` = owner. `shm_connect()` = non-owner. Owner calls `shm_close(name)` to unlink |
| **Locking** | `create_lock=True` returns a `multiprocessing.Lock` for cross-process synchronization |
| **Cache** | Shared memory handles are LRU-cached (default max 5). Eviction calls `close()` but not `unlink()` |
| **Name collision** | If the name exists, `shm_gen()` attaches to the existing block and validates size |
