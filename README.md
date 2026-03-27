# tbot223-core

A comprehensive utility package providing core functionalities for Python applications, including file management, logging, error tracking, and various utility functions.

## Note

This library returns all external APIs using the `Result` object. It is designed with safety as the top priority.
This may not align with traditional Python values. While we have strived for ease of use, this library is not recommended for beginners.

## Features

- **Consistent Result Objects**: All functions return a standardized `Result` object for predictable error handling
- **Robust File Management**: Atomic file operations, JSON handling, and safe file I/O
- **Advanced Logging System**: Structured logging with automatic log file management
- **Exception Tracking**: Detailed error tracking with system information and context
- **Utility Functions**: Hashing, path handling, parallel execution, and more
- **Multi-language Support**: Built-in localization support
- **Shared Memory IPC**: Inter-process communication via shared memory with process-safe locking

## Installation

```bash
pip install tbot223-core
```

## Python Version

Python 3.10 - 3.12

## Core Modules

### AppCore
Provides core application functionalities:
- Parallel execution with `ThreadPoolExecutor` / `ProcessPoolExecutor` (spawn context for process pool)
- Console management (`clear_console()`)
- Application lifecycle control (`restart_application()`, `exit_application()`) — optional `pause` parameter waits for user input before proceeding
- Multi-language text retrieval (`get_text_by_lang()`)
    <details>
    <summary style="color:#FF7F7F">WARNING</summary>
    You must configure language files before using this feature. Place JSON language files in the Languages directory. Examples can be found in `examples`.
    </details>
- Safe CLI input with validation, type conversion, and interrupt handling (`safe_CLI_input()`)
    - Supports `str`, `int`, `float`, `bool` types; bool accepts common true/false strings (`"yes"`, `"no"`, `"1"`, `"0"`, `"on"`, `"off"`, etc.)
    - Handles `EOFError` (non-interactive terminals) and `KeyboardInterrupt` gracefully

### ResultWrapper
A decorator class that wraps any function's return value in a `Result` object. If the function already returns a `Result`, it is passed through unchanged. Exceptions are caught and returned as a `Result(False, ...)`.

```python
from tbot223_core import ResultWrapper

@ResultWrapper()
def my_function(x, y):
    return x + y

result = my_function(5, 10)
print(result.success, result.data)  # True, 15
```

### FileManager
Safe and reliable file operations:
- Atomic file writing (`atomic_write()`)
- File read operations (`read_file()`) with text/binary modes
- JSON read/write operations (`read_json()`, `write_json()`)
- File/directory listing with extension filtering (`list_of_files()`)
- File/directory existence checking (`exist()`)
- Safe file/directory deletion (`delete_file()`, `delete_directory()`)
- Directory creation with parent support (`create_directory()`)

### LogSys
Structured logging system:
- Logger management with automatic file organization (`LoggerManager`)
  - `make_logger()` — create a named logger with file + console handlers
  - `get_logger()` — retrieve a named logger instance
  - `stop_stream_handlers()` — remove console (stream) handler from a logger at runtime
- Time-stamped log files
- Configurable log levels
- Centralized log instances (`Log`) — wraps a `logging.Logger` for structured `log_message(level, message)` calls
- Simple one-call setup helper (`SimpleSetting(base_dir, second_log_dir, logger_name)`) — creates `LoggerManager`, `Log`, and `logging.Logger` in one step; retrieve them via `get_instance()`

### Utils (Utils/Utils.py)
Collection of utility functions:
- Path conversions (`str_to_path()`)
- Hashing (`hashing()`) - md5, sha1, sha256, sha512
- PBKDF2 HMAC hash generation and verification (`pbkdf2_hmac()`, `verify_pbkdf2_hmac()`)
- List/string manipulation (`insert_at_intervals()`)
- Dictionary operations (`find_keys_by_value()`) with comparison operators
- Unique ID generation (`get_unique_id()`)

#### GlobalVars (Utils/GlobalVars.py)
Thread-safe global variable management with shared memory support:
- Variable operations (`set()`, `get()`, `delete()`, `clear()`)
- Variable existence checking (`exists()`, `list_vars()`)
- Attribute access syntax support (`gv.key = value`)
- Call syntax for get/set operations (`gv("key", value)`)
- Shared memory creation (`shm_gen()`) with optional `multiprocessing.Lock`
- Shared memory connection for child processes (`shm_connect()`)
- Shared memory synchronization (`shm_sync()`, `shm_update()`) — **JSON serialization by default** (pass `serialize_format="pickle"` to use pickle)
- Shared memory access with LRU cache (`shm_get()`, `shm_cache_management()`)
- Shared memory cleanup (`shm_close()`) with optional `close_only` mode
- Context manager support (`with gv:`) for thread-safe operations
- Internal thread lock access (`lock()`)
- **Security**: JSON is the default serialization format — pickle deserialization of untrusted data can execute arbitrary code. Use `serialize_format="pickle"` only when all communicating processes are trusted.

#### DecoratorUtils (Utils/DecoratorUtils.py)
Utility decorators:
- Runtime measurement decorator (`count_runtime()`)

### ExceptionTracker
Comprehensive error tracking:
- Exception location tracking (`get_exception_location()`)
- Detailed exception info with system context (`get_exception_info()`)
- Standardized exception return (`get_exception_return()`)
- Predefined error code lookup (`get_error_code(error_id_map, error)`) — maps exception types to user-defined codes
- System information caching (OS, architecture, Python version)
- Information masking support with `mask_tuple` parameter for sensitive data
- Decorator for automatic exception handling (`ExceptionTrackerDecorator`)

## Result Object

All functions (except internal ones) return a `Result` NamedTuple for consistent error handling:

```python
Result(
    success: Optional[bool], # True=success, False=failure, None=cancelled
    error: Optional[str],    # Error message if failed
    context: Optional[str],  # Additional context information
    data: Any               # Returned data
)
```

### Result Methods

- `unwrap()` - Returns data if successful, raises `ResultUnwrapException` if failed or cancelled
- `expect()` - Returns data if successful, raises `ResultUnwrapException` if not successful
- `unwrap_or(default)` - Returns data if successful, otherwise returns the default value

### Usage Example

```python
from tbot223_core import FileManager
from tbot223_core.Result import ResultUnwrapException

fm = FileManager()
result = fm.read_file("example.txt")

if result.success:
    print(f"File content: {result.data}")
else:
    print(f"Error: {result.error}")

# Using unwrap methods
try:
    content = fm.read_file("example.txt").unwrap()
except ResultUnwrapException as e:
    print(f"Failed: {e}")

# Using unwrap_or for default value
content = fm.read_file("missing.txt").unwrap_or("default content")
```

## Error Information

System information is cached when library classes are instantiated. Access detailed error information via `Result.data`:

```python
{
    "success": bool,
    "error": {
        "type": "ExceptionType",
        "message": "Exception message"
    },
    "location": {
        "file": "filename",
        "line": 123,
        "function": "function_name"
    },
    "origin_location": {
        "file": "filename",
        "line": 123,
        "function": "function_name"
    },
    "timestamp": "YYYY-MM-DD HH:MM:SS",
    "input_context": {
        "user_input": "...",
        "params": {...}
    },
    "traceback": "Full traceback...",
    "computer_info": {
        "OS": "OS name",
        "OS_version": "OS version",
        "Release": "OS release",
        "Architecture": "Machine architecture",
        "Processor": "Processor information",
        "Python_Version": "Python version",
        "Python_Executable": "Path to Python executable",
        "Current_Working_Directory": "Current working directory"
    }
}
```

## Quick Start

```python
from tbot223_core import AppCore, FileManager

app = AppCore(
    is_logging_enabled=True,
    is_debug_enabled=False,
    default_lang="en"
)

filemanager = FileManager(
    is_logging_enabled=True,
    is_debug_enabled=False,
    # Empty space (set as CWD) or custom path
    base_dir=""
)

# Use FileManager for safe file operations
result = filemanager.write_json("config.json", {"key": "value"})

# Execute functions in parallel
tasks = [
    (somefunc, {"some_arg1": val1}),
    (anotherfunc, {"some_arg1": val1, "some_arg2": val2})
]
result = app.thread_pool_executor(tasks, workers=4)
```

## Shared Memory Usage

`shm_sync()` and `shm_update()` use **JSON serialization by default**. To use pickle (trusted processes only), pass `serialize_format="pickle"`.

```python
from tbot223_core import GlobalVars
from multiprocessing import Process

# Worker function (must be defined at module level)
def worker(shm_name, lock):
    gv_worker = GlobalVars()
    with lock:
        gv_worker.shm_update(shm_name)  # reads from shared memory (JSON by default)
        current = gv_worker.get("counter").data
        gv_worker.set("counter", current + 1, overwrite=True)
        gv_worker.shm_sync(shm_name)    # writes to shared memory (JSON by default)

if __name__ == "__main__":
    # Main process - all setup must be inside __main__ guard
    gv = GlobalVars()
    result = gv.shm_gen("my_shm", size=4096, create_lock=True)
    shm_lock = result.data  # Get the lock for inter-process sync

    gv.set("counter", 0, overwrite=True)
    gv.shm_sync("my_shm")

    # Start processes (lock must be passed before fork/spawn)
    processes = [Process(target=worker, args=("my_shm", shm_lock)) for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    # Check result
    gv.shm_update("my_shm")
    print(f"Final counter: {gv.get('counter').data}")  # Output: 4

    # Cleanup
    gv.shm_close("my_shm")
```

## License

Apache License 2.0

## Links

- GitHub: https://github.com/Tbot223/tbot223-core
- Author: tbot223 (tbotxyz@gmail.com)

---

# 한국어 (Korean)

파이썬 애플리케이션을 위한 핵심 기능을 제공하는 종합 유틸리티 패키지입니다. 파일 관리, 로깅, 에러 추적 및 다양한 유틸리티 함수를 포함합니다.

## 참고사항

이 라이브러리의 모든 외부 API는 `Result` 객체를 사용하여 반환합니다. 안전성을 최우선으로 두고 설계되었습니다.
파이썬의 전통적인 가치와는 맞지 않을 수 있습니다. 사용 편의성을 위해 노력했지만, 초보자에게는 권장하지 않습니다.

## 주요 기능

- **일관된 Result 객체**: 모든 함수가 표준화된 `Result` 객체를 반환하여 예측 가능한 에러 처리 제공
- **안정적인 파일 관리**: 원자적 파일 작업, JSON 처리, 안전한 파일 I/O
- **고급 로깅 시스템**: 자동 로그 파일 관리를 통한 구조화된 로깅
- **예외 추적**: 시스템 정보와 컨텍스트를 포함한 상세한 에러 추적
- **유틸리티 함수**: 해싱, 경로 처리, 병렬 실행 등
- **다국어 지원**: 내장 지역화 지원
- **공유 메모리 IPC**: 프로세스 안전 잠금을 통한 공유 메모리 프로세스 간 통신

## 설치

```bash
pip install tbot223-core
```

## 파이썬 버전

Python 3.10 - 3.12

## 핵심 모듈

### AppCore
핵심 애플리케이션 기능 제공:
- `ThreadPoolExecutor` / `ProcessPoolExecutor`를 통한 병렬 실행 (프로세스 풀은 spawn 컨텍스트 사용)
- 콘솔 관리 (`clear_console()`)
- 애플리케이션 생명주기 제어 (`restart_application()`, `exit_application()`) — `pause` 파라미터로 실행 전 사용자 입력 대기 가능
- 다국어 텍스트 조회 (`get_text_by_lang()`)
- 검증, 타입 변환, 인터럽트 처리를 포함한 안전한 CLI 입력 (`safe_CLI_input()`)
    - `str`, `int`, `float`, `bool` 타입 지원; bool은 일반적인 true/false 문자열(`"yes"`, `"no"`, `"1"`, `"0"`, `"on"`, `"off"` 등) 허용
    - `EOFError`(비대화형 터미널)와 `KeyboardInterrupt` 안전하게 처리

### ResultWrapper
함수의 반환값을 `Result` 객체로 감싸는 데코레이터 클래스. 함수가 이미 `Result`를 반환하면 그대로 통과. 예외 발생 시 `Result(False, ...)`로 반환.

```python
from tbot223_core import ResultWrapper

@ResultWrapper()
def my_function(x, y):
    return x + y

result = my_function(5, 10)
print(result.success, result.data)  # True, 15
```

### FileManager
안전하고 신뢰할 수 있는 파일 작업:
- 원자적 파일 쓰기 (`atomic_write()`)
- 텍스트/바이너리 모드 파일 읽기 (`read_file()`)
- JSON 읽기/쓰기 (`read_json()`, `write_json()`)
- 확장자 필터링을 포함한 파일/디렉토리 목록 (`list_of_files()`)
- 파일/디렉토리 존재 확인 (`exist()`)
- 안전한 파일/디렉토리 삭제 (`delete_file()`, `delete_directory()`)
- 상위 디렉토리 지원 디렉토리 생성 (`create_directory()`)

### LogSys
구조화된 로깅 시스템:
- 자동 파일 구성을 통한 로거 관리 (`LoggerManager`)
  - `make_logger()` — 파일 + 콘솔 핸들러를 가진 named 로거 생성
  - `get_logger()` — named 로거 인스턴스 조회
  - `stop_stream_handlers()` — 런타임에 콘솔(스트림) 핸들러 제거
- 타임스탬프 로그 파일
- 설정 가능한 로그 레벨
- 중앙화된 로그 인스턴스 (`Log`) — `log_message(level, message)` 호출용 `logging.Logger` 래퍼
- 원스텝 설정 헬퍼 (`SimpleSetting(base_dir, second_log_dir, logger_name)`) — `LoggerManager`, `Log`, `logging.Logger`를 한 번에 생성; `get_instance()`로 반환

### Utils (Utils/Utils.py)
유틸리티 함수 모음:
- 경로 변환 (`str_to_path()`)
- 해싱 (`hashing()`) - md5, sha1, sha256, sha512
- PBKDF2 HMAC 해시 생성 및 검증 (`pbkdf2_hmac()`, `verify_pbkdf2_hmac()`)
- 리스트/문자열 조작 (`insert_at_intervals()`)
- 딕셔너리 작업 (`find_keys_by_value()`)
- 고유 ID 생성 (`get_unique_id()`)

#### GlobalVars (Utils/GlobalVars.py)
공유 메모리를 지원하는 스레드 안전 전역 변수 관리:
- 변수 작업 (`set()`, `get()`, `delete()`, `clear()`)
- 공유 메모리 생성 (`shm_gen()`), 연결 (`shm_connect()`)
- 공유 메모리 동기화 (`shm_sync()`, `shm_update()`) — **기본값은 JSON 직렬화** (`serialize_format="pickle"`으로 pickle 사용 가능)
- 컨텍스트 관리자 지원 (`with gv:`)
- **보안**: JSON이 기본 직렬화 형식 — 신뢰할 수 없는 데이터의 pickle 역직렬화는 임의 코드를 실행할 수 있음. 모든 통신 프로세스가 신뢰되는 경우에만 `serialize_format="pickle"` 사용.

#### DecoratorUtils (Utils/DecoratorUtils.py)
유틸리티 데코레이터:
- 실행 시간 측정 데코레이터 (`count_runtime()`)

### ExceptionTracker
종합적인 에러 추적:
- 예외 위치 추적 (`get_exception_location()`)
- 시스템 컨텍스트를 포함한 상세 예외 정보 (`get_exception_info()`)
- 표준화된 예외 반환 (`get_exception_return()`)
- 사용자 정의 에러 코드 조회 (`get_error_code(error_id_map, error)`) — 예외 타입을 정의된 코드로 매핑
- 민감한 데이터를 위한 `mask_tuple` 파라미터 마스킹 지원
- 자동 예외 처리를 위한 데코레이터 (`ExceptionTrackerDecorator`)

## Result 객체

모든 함수(내부 함수 제외)는 일관된 에러 처리를 위해 `Result` NamedTuple을 반환합니다:

```python
Result(
    success: Optional[bool], # True=성공, False=실패, None=취소됨
    error: Optional[str],    # 실패 시 에러 메시지
    context: Optional[str],  # 추가 컨텍스트 정보
    data: Any               # 반환 데이터
)
```

### Result 메서드

- `unwrap()` - 성공 시 데이터 반환, 실패 또는 취소 시 `ResultUnwrapException` 발생
- `expect()` - 성공 시 데이터 반환, 성공이 아닌 경우 `ResultUnwrapException` 발생
- `unwrap_or(default)` - 성공 시 데이터 반환, 그렇지 않으면 기본값 반환

### 사용 예시

```python
from tbot223_core import FileManager
from tbot223_core.Result import ResultUnwrapException

fm = FileManager()
result = fm.read_file("example.txt")

if result.success:
    print(f"파일 내용: {result.data}")
else:
    print(f"에러: {result.error}")

# unwrap 메서드 사용
try:
    content = fm.read_file("example.txt").unwrap()
except ResultUnwrapException as e:
    print(f"실패: {e}")

# 기본값을 위한 unwrap_or 사용
content = fm.read_file("missing.txt").unwrap_or("기본 내용")
```

## 빠른 시작

```python
from tbot223_core import AppCore, FileManager

app = AppCore(
    is_logging_enabled=True,
    is_debug_enabled=False,
    default_lang="ko"
)

filemanager = FileManager(
    is_logging_enabled=True,
    is_debug_enabled=False,
    base_dir=""  # 빈 문자열(CWD) 또는 커스텀 경로
)

# FileManager로 안전한 파일 작업
result = filemanager.write_json("config.json", {"key": "value"})

# 병렬로 함수 실행
tasks = [
    (somefunc, {"arg1": val1}),
    (anotherfunc, {"arg1": val1, "arg2": val2})
]
result = app.thread_pool_executor(tasks, workers=4)
```

## 라이선스

Apache License 2.0