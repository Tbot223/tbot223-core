#external Modules
import os
import subprocess
import sys
from typing import Any, Callable, List, Dict, Tuple, Union, Optional, Generator, Type, cast
import math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing
from functools import wraps

#internal Modules
from tbot223_core.Result import Result
from tbot223_core.Exception import ExceptionTracker
from tbot223_core.FileManager import FileManager
from tbot223_core._default_init import DefaultInit

class AppCore:
    """
    Core application utilities for parallel execution, localization, console
    control, and interactive CLI input.
    """
    _log: Callable[[str, str], None]
    _exception_tracker: ExceptionTracker
    _file_manager: FileManager

    def __init__(self, is_logging_enabled: bool=True, is_debug_enabled: bool=False,
                 default_lang: str="en",
                 base_dir: Optional[Union[str, Path]]=None,

                 DefaultInit: Optional[Type[DefaultInit]]=DefaultInit,
                 FileManager: Optional[Type[FileManager]]=FileManager):
        """
        Initialize the `AppCore` instance with logging, exception tracking, and language support.

        - **(R)** = Required argument
        - **(O)** = Optional argument (has a default value)
        - **(D)** = Dependency Injection (advanced usage)

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(O)** | `is_logging_enabled` | `bool` | Enable or disable logging. Default: `True`. |
        | **(O)** | `is_debug_enabled` | `bool` | Enable or disable debug mode. Default: `False`. |
        | **(O)** | `default_lang` | `str` | Default language code. Default: `"en"`. |
        | **(O)** | `base_dir` | `Union[str, Path]` | Base directory for the application. Default: `None`. |
        | **(D)** | `DefaultInit` | `Optional[Type[DefaultInit]]` | Custom `DefaultInit` class for dependency injection. Default: built-in `DefaultInit`. |
        | **(D)** | `FileManager` | `Optional[Type[FileManager]]` | Custom `FileManager` class for dependency injection. Default: built-in `FileManager`. |

        ### Returns
        `None`

        ### Note
        > **Dependency Injection:**
        > - **DefaultInit** — The `DefaultInit` class is responsible for setting up logging and exception tracking. By allowing it to be injected, you can customize the initialization process or replace it with a mock during testing.
        > - **FileManager** — The `FileManager` class handles file operations, including reading language files. By allowing it to be injected, you can use a custom file manager or mock it for testing purposes.

        ### Warning
        > The `AppCore` class is designed to be a central utility for various application needs. Be cautious when modifying its internal methods, as they are used by multiple external methods and rely on consistent behavior.

        ### Example
        >>> from tbot223_core import AppCore
        >>> app_core = AppCore()
        >>> app_core_custom = AppCore(is_logging_enabled=False, default_lang="ko"ppCore(is_logging_enabled=False, default_lang="ko")
        """

        # Initialize paths
        self._PARENT_DIR = Path(base_dir) if base_dir is not None else Path.cwd()
        self._LANG_DIR = self._PARENT_DIR / "Languages"
        Path.mkdir(self._LANG_DIR, exist_ok=True)

        # Initialize logging and exception tracking using DefaultInit
        if DefaultInit is None:
            raise ValueError("DefaultInit dependency cannot be None")
        if FileManager is None:
            raise ValueError("FileManager dependency cannot be None")
        DefaultInit._validate_dependency((DefaultInit, FileManager))

        DefaultInit.run(self,
                        is_logging_enabled=is_logging_enabled,
                        is_debug_enabled=is_debug_enabled,
                        base_dir=self._PARENT_DIR / "logs", second_log_dir="app_core", logger_name="AppCoreLogger", log_level="AUTO")
        self._file_manager = FileManager(is_logging_enabled=False, base_dir=self._PARENT_DIR)

        # Initialize internal variables
        self._lang_cache = {}
        self._default_lang = default_lang
        self._supported_langs_getter = lambda self: self._file_manager.list_of_files(self._LANG_DIR, extensions=['.json'], only_name=True).data
        self._supported_langs = self._supported_langs_getter(self)
        if self._supported_langs is None or len(self._supported_langs) == 0:
            self._log("WARNING", "No language files found in Languages directory.")

        self._log("INFO", f"AppCore initialized. Supported languages: {self._supported_langs}")

    # internal Methods
    @staticmethod
    def _check_executable(data: List[Tuple[Callable[..., Any], Dict[str, Any]]], workers: int, override: bool, timeout: Optional[float], chunk_size: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate parameters for the executor methods.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `data` | `List[Tuple[Callable[..., Any], Dict[str, Any]]]` | A list of `(callable, kwargs_dict)` tuples. |
        | **(R)** | `workers` | `int` | Number of worker threads/processes. |
        | **(R)** | `override` | `bool` | If `True`, allows `workers` to exceed the number of tasks. |
        | **(R)** | `timeout` | `float` | Maximum time to wait for each function to complete. |
        | **(O)** | `chunk_size` | `Optional[int]` | Size of chunks for processing. Default: `None`. |

        ### Callable Signature
        > `data` element: `Tuple[Callable[..., Any], Dict[str, Any]]`
        > - `Callable[..., Any]` — Any function accepting keyword arguments.
        > - `Dict[str, Any]` — Keyword arguments passed via `func(**kwargs)`.

        ### Constraint
        > - `data` MUST be a non-empty `list`.
        > - Each element of `data` MUST be `Tuple[Callable, Dict]`.
        > - `workers` MUST be `> 0`.
        > - `workers` MUST be `<= len(data)` unless `override` is `True`.
        > - `timeout` MUST be `> 0.1`.
        > - If `chunk_size` is not `None`, `chunk_size` MUST be `>= 0`.

        ### Returns
        `Tuple[bool, Optional[str]]` — `(is_valid, error_message)`..

        ### Note
        > This is an internal validation helper used by `thread_pool_executor` and `process_pool_executor`.

        ### Warning
        > Do not call this method directly unless you are extending the executor logic.

        ### Example
        >>> is_valid, err = AppCore._check_executable(data, workers=4, override=False, timeout=10)
        >>> if not is_valid:
        >>>     print(err)
        """
        if not isinstance(data, list) or len(data) == 0:
            return False, "Data must be a non-empty list"
        for item in data:
            if not (isinstance(item, tuple) and len(item) == 2 and callable(item[0]) and isinstance(item[1], dict)):
                return False, "Each item in data must be a tuple of (function, kwargs_dict)"
        if workers is None or not isinstance(workers, int) or workers <= 0:
            return False, "workers must be a positive integer"
        if workers > len(data) and not override:
            return False, f"workers {workers} exceeds number of tasks {len(data)}"
        if timeout is None or not isinstance(timeout, (int, float)) or timeout <= 0.1:
            return False, "timeout must be a positive number"
        if chunk_size is not None and (not isinstance(chunk_size, int) or chunk_size < 0):
            return False, "chunk_size must be 0 or a positive integer"
        return True, None

    @staticmethod
    def _resolve_worker_count(workers: Optional[int], data_length: int, override: bool) -> int:
        """
        Resolve worker count at call time.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `workers` | `Optional[int]` | Requested worker count. If `None`, defaults to CPU count. |
        | **(R)** | `data_length` | `int` | Number of tasks in the data list. |
        | **(R)** | `override` | `bool` | If `False`, cap workers to the number of tasks. |

        ### Constraint
        > - `data_length` MUST be `>= 0`.
        > - Return value is always `>= 1`.

        ### Returns
        `int` — Resolved worker count.

        ### Note
        > If `workers` is `None`, uses `os.cpu_count()`. When `override` is `False`, the count is capped to `data_length` for small task lists.

        ### Warning
        > This is an internal helper. The resolved count may differ from the requested value.

        ### Example
        >>> count = AppCore._resolve_worker_count(None, data_length=3, override=False)
        >>> print(count)  # min(cpu_count, 3)
        """
        cpu_count = os.cpu_count() or 1
        if workers is None:
            return cpu_count if override else min(cpu_count, max(data_length, 1))
        return min(workers, cpu_count) if override else workers

    def _generic_executor(self, data: List[Tuple[Callable[..., Any], Dict[str, Any]]], workers: int, timeout: float, type: str) -> List[Result]:
        """
        Shared executor implementation used by the thread and process pools.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `data` | `List[Tuple[Callable[..., Any], Dict[str, Any]]]` | List of `(callable, kwargs_dict)` tuples. |
        | **(R)** | `workers` | `int` | Number of worker threads/processes. |
        | **(R)** | `timeout` | `float` | Per-task timeout in seconds. Total timeout is `timeout * len(data)`. |
        | **(R)** | `type` | `str` | Executor type. See **Enum**. |

        ### Callable Signature
        > `data` element: `Tuple[Callable[..., Any], Dict[str, Any]]`
        > - `Callable[..., Any]` — Any function accepting keyword arguments.
        > - `Dict[str, Any]` — Keyword arguments passed via `func(**kwargs)`.

        ### Enum
        > `type` — type: `str`
        > | Value | Description |
        > |-------|-------------|
        > | `'thread'` | Uses `ThreadPoolExecutor`. |
        > | `'process'` | Uses `ProcessPoolExecutor`. |

        ### Constraint
        > - `data` MUST be a non-empty `list`.
        > - `workers` MUST be `> 0`.
        > - `timeout` MUST be `> 0.1`.

        ### Returns
        `List[Result]` — Indexed list of `Result` objects corresponding to each function execution.

        ### Note
        > This is an internal helper; typically not called directly. Use `thread_pool_executor` or `process_pool_executor` instead.

        ### Warning
        > Failed tasks are logged and wrapped in a failure `Result` via `_exception_tracker`.

        ### Example
        >>> data = [(func1, {'arg1': val1}), (func2, {'arg2': val2})]
        >>> results = app_core._generic_executor(data, workers=4, timeout=10, type='thread')
        >>> for res in results:
        >>>     print(res.success, res.data)
        """
        results: List[Optional[Result]] = [None] * len(data)

        executor_class = ThreadPoolExecutor if type == 'thread' else ProcessPoolExecutor
        executor_kwargs: Dict[str, Any] = {"max_workers": workers}
        if type == 'process':
            executor_kwargs["mp_context"] = multiprocessing.get_context("spawn")
        with executor_class(**executor_kwargs) as executor:
            future_to_task = {executor.submit(func, **params): idx for idx, (func, params) in enumerate(data)}

            for future in as_completed(future_to_task, timeout=timeout * len(future_to_task)):
                idx = future_to_task[future]
                try:
                    result = future.result(timeout=timeout)
                    results[idx] = Result(True, None, None, result)
                except Exception as e:
                    self._log("ERROR", f"Error executing task at index {idx}: {str(e)}")
                    results[idx] = self._exception_tracker.get_exception_return(e, params=((), data[idx][1]))
        return cast(List[Result], results)

    def _chunk_list(self, data_list: List, chunk_size: int) -> Generator[List, None, None]:
        """
        Yield successive chunks from a list.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `data_list` | `List` | The list to be chunked. |
        | **(R)** | `chunk_size` | `int` | The size of each chunk. |

        ### Constraint
        > - `chunk_size` MUST be `> 0`.
        > - `data_list` MUST be a non-empty `list`.

        ### Returns
        `Generator[List, None, None]` — Yields sublists of the given chunk size.

        ### Note
        > This is an internal helper used by `process_pool_executor` when `chunk_size` is specified.

        ### Warning
        > The last chunk may be smaller than `chunk_size` if the list length is not evenly divisible.

        ### Example
        >>> my_list = [1, 2, 3, 4, 5, 6, 7]
        >>> chunks = list(app_core._chunk_list(my_list, chunk_size=3))
        >>> print(chunks)  # 3], [4, 5, 6], [7]]
        """
        for i in range(0, len(data_list), chunk_size):
            yield data_list[i:i + chunk_size]

    @staticmethod
    def __lang_cache_management__(func):
        """
        Decorator that reloads a language file when a cached key lookup fails.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `func` | `Callable[[AppCore, str, str], Result]` | The `get_text_by_lang` method to decorate. |

        ### Callable Signature
        > `func`: `(self: AppCore, key: str, lang: str) -> Result`

        ### Returns
        `Callable[[AppCore, str, str], Result]` — Wrapped function with cache-reload logic.

        ### Note
        > When a `KeyError` occurs, the decorator reloads the language JSON file and retries. If the key is still missing after reload, it returns a failure `Result`.

        ### Warning
        > Intended for `get_text_by_lang()` only. Do not apply to other methods.

        ### Example
        >>> @AppCore.__lang_cache_management__
        >>> def get_text_by_lang(self, key: str, lang: str) -> Result:
        >>>     ...
        """
        def wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            if not res.success:
                if isinstance(res.data, dict) and res.data.get("error", {}).get("type") == "KeyError":
                    lang = args[1] if len(args) > 1 else kwargs.get("lang", self._default_lang)
                    key = args[0] if len(args) > 0 else kwargs.get("key", "")
                    lang_file = self._file_manager.read_json(self._LANG_DIR / f"{lang}.json")
                    if lang_file.success:
                        lang_file = lang_file.data
                    else:
                        return res
                    if key in lang_file:
                        self._log("INFO", f"Reloaded language file for '{lang}' after KeyError.")
                        self._lang_cache[lang] = lang_file
                        return func(self, *args, **kwargs)
                    else:
                        self._log("ERROR", f"Key '{key}' still not found in language '{lang}'. it may have been removed.")
                        return Result(False, res.error, "Does not exist key even after reloading lang file", res.data)
            return res
        return wrapper


    # external Methods
    def thread_pool_executor(self, data: List[Tuple[Callable[..., Any], Dict[str, Any]]], workers: Optional[int] = None, override: bool = False, timeout: float = 0.1) -> Result:
        """
        Execute tasks concurrently with `ThreadPoolExecutor`.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `data` | `List[Tuple[Callable[..., Any], Dict[str, Any]]]` | A list of `(callable, kwargs_dict)` tuples. |
        | **(O)** | `workers` | `Optional[int]` | Number of worker threads. Default: `None` (CPU count). |
        | **(O)** | `override` | `bool` | Allow workers to exceed task count. Default: `False`. |
        | **(O)** | `timeout` | `float` | Max wait time per task in seconds. Default: `0.1`. |

        ### Callable Signature
        > `data` element: `Tuple[Callable[..., Any], Dict[str, Any]]`
        > - `Callable[..., Any]` — Any function accepting keyword arguments.
        > - `Dict[str, Any]` — Keyword arguments passed via `func(**kwargs)`.

        ### Constraint
        > - `data` MUST be a non-empty `list`.
        > - Each element of `data` MUST be `Tuple[Callable, Dict]`.
        > - `workers` MUST be `> 0`.
        > - `workers` MUST be `<= len(data)` unless `override` is `True`.
        > - `timeout` MUST be `> 0.1`.

        ### Returns
        `Result` — `data` field contains an indexed `List[Result]` of task results.

        ### Note
        > Worker count defaults to `os.cpu_count()` when `workers` is `None`. If `override` is `False`, the count is capped to the number of tasks.

        ### Warning
        > Each element of `data` MUST be `Tuple[Callable, Dict]`. Passing invalid data will result in a validation failure.

        ### Example
        >>> def add(a, b): return a + b
        >>> data = [(add, {'a': 1, 'b': 2}), (add, {'a': 3, 'b': 4})]
        >>> result = app_core.thread_pool_executor(data, workers=2, timeout=10)
        >>> if result.success:
        >>>     for res in result.data:
        >>>         print(res.data)  # 3, 7 (add, {'a': 3, 'b': 4})]
        >>> result = app_core.thread_pool_executor(data, workers=2, timeout=10)
        >>> if result.success:
        >>>     for res in result.data:
        >>>         print(res.data)  # 3, 7
        """
        try:
            resolved_workers = self._resolve_worker_count(workers, len(data) if isinstance(data, list) else 0, override)
            is_valid, error_message = self._check_executable(data, resolved_workers, override, timeout)
            if not is_valid:
                self._log("ERROR", f"Thread pool executor validation failed: {error_message}")
                return Result(False, error_message, None, None)
            results = self._generic_executor(data, resolved_workers, timeout, type='thread')

            self._log("INFO", f"Thread pool executor completed with {len(results)} tasks.")
            return Result(True, None, None, results)
        except Exception as e:
            self._log("ERROR", f"Error in thread pool executor: {str(e)}")
            return self._exception_tracker.get_exception_return(e)

    def process_pool_executor(self, data: List[Tuple[Callable[..., Any], Dict[str, Any]]], workers: Optional[int] = None, override: bool = False, timeout: Optional[float] = None, chunk_size: Optional[int] = None) -> Result:
        """
        Execute tasks concurrently with `ProcessPoolExecutor`.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `data` | `List[Tuple[Callable[..., Any], Dict[str, Any]]]` | A list of `(callable, kwargs_dict)` tuples. |
        | **(O)** | `workers` | `Optional[int]` | Number of worker processes. Default: `None` (CPU count). |
        | **(O)** | `override` | `bool` | Allow workers to exceed task count. Default: `False`. |
        | **(O)** | `timeout` | `float` | Max wait time per task in seconds. Default: `None`. |
        | **(O)** | `chunk_size` | `Optional[int]` | Chunking mode. See **Enum**. Default: `None`. |

        ### Callable Signature
        > `data` element: `Tuple[Callable[..., Any], Dict[str, Any]]`
        > - `Callable[..., Any]` — Any **picklable** function accepting keyword arguments.
        > - `Dict[str, Any]` — Keyword arguments passed via `func(**kwargs)`.

        ### Enum
        > `chunk_size` — type: `Optional[int]`
        > | Value | Description |
        > |-------|-------------|
        > | `None` | Submit the full task list to a single executor. |
        > | `0` | Auto-compute as `ceil(len(data) / workers)`. |
        > | positive `int` | Submit tasks in fixed-size batches. |

        ### Constraint
        > - `data` MUST be a non-empty `list`.
        > - Each element of `data` MUST be `Tuple[Callable, Dict]`.
        > - `workers` MUST be `> 0`.
        > - `workers` MUST be `<= len(data)` unless `override` is `True`.
        > - `timeout` MUST be `> 0.1`.
        > - If `chunk_size` is not `None`, `chunk_size` MUST be `>= 0`.
        > - Each `Callable` in `data` MUST be picklable (no lambdas, closures).

        ### Returns
        `Result` — `data` field contains an indexed `List[Result]` of task results.

        ### Note
        > When `chunk_size` is `0`, the chunk size is auto-computed as `ceil(len(data) / workers)`. When `chunk_size` is `None`, the full task list is submitted to a single executor.

        ### Warning
        > Each `Callable` in `data` MUST be picklable. Lambda functions and closures will fail.

        ### Example
        >>> def add(a, b): return a + b
        >>> data = [(add, {'a': 1, 'b': 2}), (add, {'a': 3, 'b': 4})]
        >>> result = app_core.process_pool_executor(data, workers=2, timeout=10)
        >>> if result.success:
        >>>     for res in result.data:
        >>>         print(res.data)  # 3, 7
        """
        try:
            resolved_workers = self._resolve_worker_count(workers, len(data) if isinstance(data, list) else 0, override)
            is_valid, error_message = self._check_executable(data, resolved_workers, override, timeout, chunk_size)
            if not is_valid:
                self._log("ERROR", f"Process pool executor validation failed: {error_message}")
                return Result(False, error_message, None, None)
            effective_timeout = timeout if timeout is not None else 0.1
            if chunk_size is None:
                results = self._generic_executor(data, resolved_workers, effective_timeout, type='process')
            else:
                computed_chunk = chunk_size if chunk_size > 0 else max(1, int(math.ceil(len(data) / resolved_workers)))
                chunks = list(self._chunk_list(data, computed_chunk))
                results = []
                for chunk in chunks:
                    chunk_results = self._generic_executor(chunk, resolved_workers, effective_timeout, type='process')
                    results.extend(chunk_results)

            self._log("INFO", f"Process pool executor completed with {len(results)} tasks.")
            return Result(True, None, None, results)
        except Exception as e:
            self._log("ERROR", f"Error in process pool executor: {str(e)}")
            return self._exception_tracker.get_exception_return(e)

    @__lang_cache_management__
    def get_text_by_lang(self, key: str, lang: str) -> Result:
        """
        Retrieve localized text for the given key and language.

        ### ArgumentsLanguage code (e.g., `'en'`, `'ko'`). |

        ### Returns
        `Result` — Contains the localized text in `data`.

        ### Note
        > If `lang` is not in the supported languages list, it falls back to `_default_lang`. Language files are cached after the first load.

        ### Warning
        > If `key` does not exist in the language file, a `KeyError` is raised internally and returned as a failure `Result`. The `__lang_cache_management__` decorator will attempt one reload before giving up.

        ### Example
        >>> result = app_core.get_text_by_lang('greeting', 'en')
        >>> if result.success:
        >>>     print(result.data)  #
        ### Example
        >>> result = app_core.get_text_by_lang('greeting', 'en')
        >>> if result.success:
        >>>     print(result.data)  # "Hello"
        >>> else:
        >>>     print(result.error)
        """

        try:
            if lang not in self._supported_langs:
                lang = self._default_lang

            if lang not in self._lang_cache:
                self._log("INFO", f"Loading language file for '{lang}'.")
                lang_file_path = self._LANG_DIR / f"{lang}.json"
                read_result = self._file_manager.read_json(lang_file_path)
                if not read_result.success:
                    self._log("ERROR", f"Failed to read language file for '{lang}': {read_result.error}")
                    return read_result
                self._lang_cache[lang] = read_result.data

            if key not in self._lang_cache[lang]:
                self._log("ERROR", f"Key '{key}' not found in language '{lang}'.")
                raise KeyError(f"Key '{key}' not found in language '{lang}'.")

            self._log("INFO", f"Retrieved text for key '{key}' in language '{lang}'.")
            return Result(True, None, None, self._lang_cache[lang][key])
        except Exception as e:
            self._log("ERROR", f"Error in get_text_by_lang: {str(e)}")
            return self._exception_tracker.get_exception_return(e)

    def clear_console(self) -> Result:
        """
        Clear the current console screen.

        ### Arguments
        None

        ### Returns
        `Result` — Indicates whether the console-clear command succeeded.

        ### Note
        > Uses `cls` on Windows (`os.name == 'nt'`) and `clear` on other platforms.

        ### Warning
        >>> print(result.success)  # True
        > Runs a subprocess command. May fail if the system command is unavailable.

        ### Example
        >>> result = app_core.clear_console()
        >>> print(result.success)  # True
        """
        try:
            command = ["cmd", "/c", "cls"] if os.name == 'nt' else ["clear"]
            subprocess.run(command, shell=False, check=True)

            self._log("INFO", "Console cleared successfully.")
            return Result(True, None, None, "Console cleared successfully.")
        except Exception as e:
            self._log("ERROR", f"Error in clear_console: {str(e)}")
            return self._exception_tracker.get_exception_return(e)

    def exit_application(self, code: int=0, pause: bool=False) -> Result:
        """
        Terminate the current process with the for the OS. Default: `0`. |
        | **(O)** | `pause` | `bool` | Wait for user input before exiting. Default: `False`. |

        ### Constraint
        > - `code` MUST be `>= 0` and `<= 255`.

        ### Returns
        `Result` — Returned only if the exit attempt fails.

        ### Warning
        > This method does **not** return under normal circumstances. Any code after this call will not execute.

        ### Note
        > Calls `sys.exit(code)` internally. A `SystemExit` exception will be raised.

        ### Example
        >>> app_core.exit_application(0)
        ### Note
        > Calls `sys.exit(code)` internally. A `SystemExit` exception will be raised.

        ### Example
        >>> app_core.exit_application(0)
        """
        try:
            self._log("INFO", f"Exiting application with code {code}.")
            if pause:
                input("Press Enter to exit...")
            sys.exit(code)
        except Exception as e:
            self._log("ERROR", f"Error in exit_application: {str(e)}")
            return self._exception_tracker.get_exception_return(e)

    def restart_application(self, pause: bool=False) -> Result:
        """
        Restart the current Python procWait for user input before restarting. Default: `False`. |

        ### Returns
        `Result` — Returned only if the restart attempt fails.

        ### Warning
        > This method does **not** return under normal circumstances. The current process is replaced entirely.

        ### Note
        > Uses `os.execl()` to replace the current process with a new Python interpreter instance using the same arguments.

        ### Example
        >>> app_core.restart_application()
        ### Note
        > Uses `os.execl()` to replace the current process with a new Python interpreter instance using the same arguments.

        ### Example
        >>> app_core.restart_application()
        """
        try:
            python = sys.executable
            self._log("INFO", "Restarting application.")
            if pause:
                input("Press Enter to restart...")
            os.execl(python, python, * sys.argv)
        except Exception as e:
            self._log("ERROR", f"Error in restart_application: {str(e)}")
            return self._exception_tracker.get_exception_return(e)

    def safe_CLI_input(self, prompt: str="", input_type: type=str, other_type: bool=False, valid_options: Optional[List[str]]=None, case_sensitive: bool=False, allow_empty: bool=False, max_retries: int=10) -> Result:
        """
        Prompt for CLI input with validation and optional type conversion.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(O)** | `prompt` | `str` | Prompt message to display. Default: `""`. |
        | **(O)** | `input_type` | `type` | Target type for conversion. See **Enum**. Default: `str`. |
        | **(O)** | `other_type` | `bool` | Allow custom types beyond built-ins. Default: `False`. |
        | **(O)** | `valid_options` | `List[str]` | Accepted values whitelist. Default: `None`. |
        | **(O)** | `case_sensitive` | `bool` | Validate `valid_options` case-exactly. Default: `False`. |
        | **(O)** | `allow_empty` | `bool` | Allow empty input string. Default: `False`. |
        | **(O)** | `max_retries` | `int` | Max invalid attempts before failure. Default: `10`. |

        ### Enum
        > `input_type` — type: `type` (when `other_type` is `False`)
        > | Value | Description |
        > |-------|-------------|
        > | `str` | String input (no conversion). |
        > | `int` | Integer conversion via `int()`. |
        > | `float` | Float conversion via `float()`. |
        > | `bool` | Boolean conversion (see **Note** for accepted values). |

        ### Constraint
        > - `max_retries` MUST be `> 0`.
        > - `input_type` MUST be one of `{str, int, float, bool}` unless `other_type` is `True`.
        > - If `input_type` is `bool` and `valid_options` is set, options MUST be from the supported true/false value sets.

        ### Returns
        `Result` — Contains the validated and converted value, or a failure if `max_retries` is exceeded.

        ### Note
        > When `input_type` is `bool`, common true/false values are accepted:
        > - **True** values: `"true"`, `"t"`, `"yes"`, `"y"`, `"1"`, `"on"`, `"enable"`, `"enabled"`.
        > - **False** values: `"false"`, `"f"`, `"no"`, `"n"`, `"0"`, `"off"`, `"disable"`, `"disabled"`.
        >
        > If `input_type` is `bool`, `valid_options` MUST use values from those sets. `["y", "n"]` works, but `["ok", "cancel"]` will validate then fail during boolean conversion.

        ### Warning
        > The prompt repeats until valid input is received or `max_retries` is exceeded. A `KeyboardInterrupt` will immediately return a failure `Result`.

        ### Example
        >>> result = app_core.safe_CLI_input(
        >>>     prompt="Enter your choice: ",
        >>>     valid_options=["yes", "no"],
        >>>     max_retries=3
        >>> )
        >>> if result.success:
        >>>     print(result.data)  # "yes" or "no"
        >>> else:
        >>>     print(result.error)
        """
        SUPPORTED_TYPES = {str, int, float, bool}
        try:
            if not isinstance(max_retries, int) or max_retries <= 0:
                raise ValueError("max_retries must be a positive integer")
            if not other_type and input_type not in SUPPORTED_TYPES:
                raise ValueError(f"input_type must be one of {SUPPORTED_TYPES} or other_type must be True")

            def validate_input(user_input: str) -> bool:
                if not allow_empty and user_input == "":
                    return False
                if valid_options:
                    comparison_input = user_input if case_sensitive else user_input.lower()
                    comparison_options = valid_options if case_sensitive else map(str.lower, valid_options)
                    return comparison_input in comparison_options
                return True

            retry_count = 0
            while retry_count < max_retries:
                try:
                    user_input = input(prompt)
                except EOFError:
                    user_input = ""
                except KeyboardInterrupt:
                    self._log("WARNING", "User interrupted input with KeyboardInterrupt.")
                    print("\nInput interrupted by user.")
                    return Result(False, "Input interrupted by user", None, None)
                if validate_input(user_input):
                    try:
                        if input_type is bool:
                            true_values = {"true", "t", "yes", "y", "1", "on", "enable", "enabled"}
                            false_values = {"false", "f", "no", "n", "0", "off", "disable", "disabled"}
                            if user_input.lower() in true_values:
                                converted_input = True
                            elif user_input.lower() in false_values:
                                converted_input = False
                            else:
                                raise ValueError(f"Invalid boolean input: {user_input}")
                        else:
                            converted_input = input_type(user_input)
                        self._log("INFO", f"User input received and validated: {converted_input}")
                        return Result(True, None, None, converted_input)
                    except ValueError:
                        self._log("WARNING", f"Input conversion to {input_type} failed for input: {user_input}")
                        print(f"Invalid input type. Please enter a value of type {input_type.__name__}.")
                else:
                    self._log("WARNING", f"User input validation failed: {user_input}")
                    if valid_options:
                        print(f"Invalid option. Please choose from: {', '.join(valid_options)}")
                    else:
                        print("Invalid input. Please try again.")

                retry_count += 1

            error_msg = f"Maximum retry attempts ({max_retries}) exceeded for user input."
            self._log("ERROR", error_msg)
            return Result(False, error_msg, None, None)
        except Exception as e:
            self._log("ERROR", f"Error in safe_CLI_input: {str(e)}")
            return self._exception_tracker.get_exception_return(e)

class ResultWrapper:
    """
    A class decorator that wraps function returns in `Result` objects.

    ### Arguments
    None (class decorator — instantiate with `@ResultWrapper()`).

    ### Callable Signature
    > Wrapped function: `Callable[..., Any]` → `Callable[..., Result]`
    > - Input: Any function with arbitrary arguments.
    > - Output: Same function, but always returns `Result`.

    ### Returns
    `Callable[..., Result]` — A wrapped function that always returns a `Result` object.

    ### Note
    > - If the wrapped function already returns a `Result`, it is passed through unchanged.
    > - If an exception is raised, the decorator converts it into a failure `Result`.
    > - Best suited for non-critical helper functions where a consistent return shape is more important than preserving raw exceptions.

    ### Warning
    > Do not combine with `ExceptionTrackerDecorator`, because `ResultWrapper` already handles exceptions internally.

    ### Example
    >>> @ResultWrapper()
    >>> def my_function(x, y):
    >>>     return x + y
    >>> result = my_function(5, 10)
    >>> print(result.success)  # True
    >>> print(result.data)     # 15
    """
    def __init__(self):
        self._exception_tracker = ExceptionTracker()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Result]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Result:
            try:
                result = func(*args, **kwargs)
                if isinstance(result, Result):
                    return result

                return Result(True, None, None, result)
            except Exception as e:
                return self._exception_tracker.get_exception_return(e, params=(args, kwargs))
        return wrapper
