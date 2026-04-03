[English](API.md)

# API 레퍼런스

> tbot223-core v4.0.0 | Python 3.10 - 3.14

설치 및 빠른 시작 방법은 [README](../README.ko.md)를 참조하세요.
실행 가능한 예제 스크립트는 [예제 문서](Examples.ko.md)를 참조하세요.

<details>
<summary>목차</summary>

- [AppCore](#appcore)
- [ResultWrapper](#resultwrapper)
- [FileManager](#filemanager)
- [LogSys](#logsys) — [LoggerManager](#loggermanager) · [Log](#log) · [SimpleSetting](#simplesetting)
- [ExceptionTracker](#exceptiontracker)
- [ExceptionTrackerDecorator](#exceptiontrackerdecorator)
- [Result](#result-객체)
- [Utils](#utils)
- [GlobalVars](#globalvars)
- [DecoratorUtils](#decoratorutils)
- [에러 정보 구조](#에러-정보-구조)
- [공유 메모리 사용법](#공유-메모리-사용법)
</details>

## AppCore

병렬 실행, 다국어 지원, 콘솔 관리, CLI 입력을 위한 핵심 애플리케이션 유틸리티.

### 생성자

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

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `is_logging_enabled` | `bool` | `True` | 파일 내부 로깅 활성화 |
| `is_debug_enabled` | `bool` | `False` | 디버그 레벨 로그 출력 활성화 |
| `default_lang` | `str` | `"en"` | `get_text_by_lang()`의 기본 언어 코드 |
| `base_dir` | `Union[str, Path]` | `None` | 앱의 기본 디렉토리; `None`이면 현재 작업 디렉토리를 사용합니다. `Languages/`가 여기 생성되고 내부 로그는 `{base_dir}/logs/app_core/` 아래에 저장됩니다 |
| `logger_manager_instance` | `Optional[LoggerManager]` | `None` | 기존 LoggerManager 공유 |
| `logger` | `Optional[logging.Logger]` | `None` | 기존 logger 공유 |
| `log_instance` | `Optional[Log]` | `None` | 기존 Log 공유 |
| `filemanager` | `Optional[FileManager]` | `None` | 언어 파일 I/O를 위한 기존 FileManager 공유 |

### 메서드

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

`ThreadPoolExecutor`를 사용하여 작업 목록을 동시에 실행합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `data` | `List[Tuple[Callable, Dict]]` | — | `(함수, kwargs_dict)` 쌍의 리스트 |
| `workers` | `Optional[int]` | `None` | 최대 워커 스레드 수; `None`이면 `os.cpu_count()` 사용 |
| `override` | `bool` | `False` | `True`이면 `workers <= cpu_count` 제한 무시 |
| `timeout` | `float` | `None` | Future별 타임아웃 (초 단위) |

**반환값:** `Result(True, None, None, [task_result1, task_result2, ...])` — 입력 순서가 유지된 작업별 `Result` 객체 리스트입니다. 각 내부 `Result.data`에 실제 반환값이 들어 있습니다.

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

`spawn` 시작 방법을 사용하여 `ProcessPoolExecutor`로 작업을 동시에 실행합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `data` | `List[Tuple[Callable, Dict]]` | — | `(함수, kwargs_dict)` 쌍의 리스트 |
| `workers` | `Optional[int]` | `None` | 최대 워커 프로세스 수; `None`이면 `os.cpu_count()` 사용 |
| `override` | `bool` | `False` | `True`이면 `workers <= cpu_count` 제한 무시 |
| `timeout` | `float` | `None` | Future별 타임아웃 (초 단위) |
| `chunk_size` | `Optional[int]` | `None` | `None` = 모든 작업에 단일 executor, `0` = 자동 청크, 양의 정수 = 명시적 배치 크기 |

**반환값:** `Result(True, None, None, [task_result1, task_result2, ...])` — 입력 순서가 유지된 작업별 `Result` 객체 리스트입니다. 각 내부 `Result.data`에 실제 반환값이 들어 있습니다.

---

#### `get_text_by_lang(key, lang) -> Result`

```python
def get_text_by_lang(self, key: str, lang: str) -> Result
```

JSON 언어 파일에서 다국어 텍스트를 조회합니다. 언어 파일은 `Languages/` 디렉토리에 배치해야 합니다. 결과는 내부적으로 캐시되며, 캐시에 없으면 자동으로 다시 로드됩니다. 요청한 `lang`이 지원되지 않으면 `default_lang`으로 폴백합니다.

| 파라미터 | 타입 | 설명 |
|-----------|------|-------------|
| `key` | `str` | 언어 JSON에서 조회할 키 |
| `lang` | `str` | 언어 코드 (예: `"en"`, `"ko"`) — `Languages/{lang}.json`에 매핑됨 |

**반환값:** `Result(True, None, None, "translated text")` 또는 키나 파일을 찾을 수 없는 경우 `Result(False, ...)`.

> **경고**: 이 메서드를 호출하기 전에 `Languages/` 디렉토리 아래에 JSON 언어 파일을 생성해야 합니다. [get_text_by_lang.py](../examples/AppCore/get_text_by_lang.py)를 참조하세요.

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

유효성 검사, 타입 변환, 인터럽트 처리를 포함한 사용자 입력 프롬프트.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `prompt` | `str` | `""` | 사용자에게 표시되는 프롬프트 텍스트 |
| `input_type` | `type` | `str` | 예상 타입: `str`, `int`, `float`, 또는 `bool`. `other_type=True`이면 커스텀 변환기 타입도 허용됩니다 |
| `other_type` | `bool` | `False` | 기본 제공 타입 외의 커스텀 `input_type` 변환기를 허용하려면 `True`로 설정합니다 |
| `valid_options` | `List[str]` | `None` | 허용되는 값의 화이트리스트 |
| `case_sensitive` | `bool` | `False` | 유효성 검사 시 대소문자 구분 여부 |
| `allow_empty` | `bool` | `False` | 빈 입력 허용 여부 |
| `max_retries` | `int` | `10` | 실패 반환 전 최대 재시도 횟수 |

**Bool 타입**: `True`로는 `"true"`, `"t"`, `"yes"`, `"y"`, `"1"`, `"on"`, `"enable"`, `"enabled"`를, `False`로는 `"false"`, `"f"`, `"no"`, `"n"`, `"0"`, `"off"`, `"disable"`, `"disabled"`를 허용합니다 (대소문자 무관).

**반환값:** `Result(True, None, None, converted_value)` 또는 인터럽트/최대 재시도 시 `Result(False, ...)`.

---

#### `clear_console() -> Result`

```python
def clear_console(self) -> Result
```

터미널 화면을 지웁니다. Windows에서는 `cls`, Unix에서는 `clear`를 사용합니다.

---

#### `exit_application(code, pause) -> Result`

```python
def exit_application(self, code: int = 0, pause: bool = False) -> Result
```

현재 프로세스를 종료합니다. 성공하면 `sys.exit()`를 호출하므로 이 메서드는 반환되지 않습니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `code` | `int` | `0` | `sys.exit()`에 전달되는 종료 코드 |
| `pause` | `bool` | `False` | `True`이면 종료 전 사용자 입력 대기 |

---

#### `restart_application(pause) -> Result`

```python
def restart_application(self, pause: bool = False) -> Result
```

`os.execv()`를 사용하여 현재 Python 프로세스를 재시작합니다. 성공하면 현재 프로세스를 교체하므로 이 메서드는 반환되지 않습니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `pause` | `bool` | `False` | `True`이면 재시작 전 사용자 입력 대기 |

---

## ResultWrapper

함수의 반환값을 `Result`로 감싸는 데코레이터 클래스입니다. 함수가 이미 `Result`를 반환하는 경우 변경 없이 통과됩니다. 포착되지 않은 예외는 `ExceptionTracker.get_exception_return(...)`으로 변환되므로, 실패 시 `data`에 구조화된 예외 정보가 유지됩니다.

### 생성자

```python
ResultWrapper()
```

매개변수는 없습니다. 데코레이터로 사용하세요:

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

함수 메타데이터(`__name__`, `__doc__`)는 `functools.wraps`를 통해 보존됩니다.

---

## FileManager

원자적 쓰기, 파일 잠금, JSON 처리를 지원하는 안전하고 신뢰할 수 있는 파일 작업.

### 생성자

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

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `is_logging_enabled` | `bool` | `True` | 내부 로깅 활성화 |
| `is_debug_enabled` | `bool` | `False` | 디버그 레벨 출력 활성화 |
| `base_dir` | `Union[str, Path]` | `None` | 로그 파일의 기본 디렉토리; `None` = 현재 작업 디렉토리. **참고:** 이것은 로깅 디렉토리이며 I/O 기본 경로가 아닙니다 — 파일 작업 경로는 항상 절대 경로이거나 현재 작업 디렉토리 기준 상대 경로입니다 |
| `Utils_instance` | `Optional[Utils]` | `None` | 기존 Utils 인스턴스 공유 |

10 MB(`LOCK_FILE_SIZE_THRESHOLD`)보다 큰 파일에는 자동으로 파일 잠금이 적용됩니다. 크로스 플랫폼: Unix에서는 `fcntl`, Windows에서는 `msvcrt`를 사용합니다.

### 메서드

#### `atomic_write(file_path, data) -> Result`

```python
def atomic_write(self, file_path: Union[str, Path], data: Any) -> Result
```

파일에 데이터를 원자적으로 씁니다. 먼저 임시 파일에 쓴 다음 대상 경로로 이름을 변경합니다. 쓰기가 실패하면 원본 파일은 변경되지 않습니다.

부모 디렉토리가 존재하지 않으면 자동으로 생성됩니다.

---

#### `read_file(file_path, as_bytes) -> Result`

```python
def read_file(self, file_path: Union[str, Path], as_bytes: bool = False) -> Result
```

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `file_path` | `Union[str, Path]` | — | 파일 경로 |
| `as_bytes` | `bool` | `False` | `True` = 바이너리 모드(`"rb"`)로 읽기, `False` = 텍스트 모드(`"r"`, UTF-8) |

**반환값:** `Result(True, None, None, file_content_string_or_bytes)`

---

#### `write_json(file_path, data, indent) -> Result`

```python
def write_json(self, file_path: Union[str, Path], data: Any, indent: int = 4) -> Result
```

`data`를 JSON으로 직렬화하고 선택적 들여쓰기와 함께 디스크에 씁니다. 내부적으로 `atomic_write()`를 사용합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `file_path` | `Union[str, Path]` | — | 대상 파일 경로 |
| `data` | `Any` | — | JSON 직렬화 가능한 Python 객체 |
| `indent` | `int` | `4` | 정렬 출력을 위한 공백 수 |

---

#### `read_json(file_path) -> Result`

```python
def read_json(self, file_path: Union[str, Path]) -> Result
```

JSON 파일을 읽고 파싱합니다.

**반환값:** `Result(True, None, None, parsed_python_object)`

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

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `dir_path` | `Union[str, Path]` | — | 스캔할 디렉토리 |
| `extensions` | `List[str]` | `None` | 확장자 필터 (예: `[".json", ".txt"]`); `None` = 모든 파일 |
| `only_name` | `bool` | `False` | `True` = 확장자를 제외한 파일 stem만 반환, `False` = 전체 경로 반환 |

**반환값:** `Result(True, None, None, [path1, path2, ...])`

---

#### `exists(path) -> Result`

```python
def exists(self, path: Union[str, Path]) -> Result
```

파일 또는 디렉토리의 존재 여부를 확인합니다.

**반환값:** 존재하면 `Result(True, None, None, True)`, 존재하지 않으면 `Result(True, None, None, False)`.

> `exist()`는 더 이상 사용되지 않는 별칭입니다 — 대신 `exists()`를 사용하세요.

---

#### `delete_file(file_path) -> Result`

```python
def delete_file(self, file_path: Union[str, Path]) -> Result
```

단일 파일을 삭제합니다. 삭제 전 `os.chmod()`를 사용하여 읽기 전용 권한을 재설정합니다.

---

#### `delete_directory(dir_path) -> Result`

```python
def delete_directory(self, dir_path: Union[str, Path]) -> Result
```

`shutil.rmtree()`를 사용하여 디렉토리와 모든 내용을 재귀적으로 삭제합니다.

---

#### `create_directory(dir_path) -> Result`

```python
def create_directory(self, dir_path: Union[str, Path]) -> Result
```

누락된 부모 디렉토리를 포함하여 디렉토리를 생성합니다 (`parents=True`, `exist_ok=True`).

---

## LogSys

자동 파일 구성을 지원하는 구조화된 로깅 시스템.

### LoggerManager

파일 및 콘솔 핸들러를 가진 이름이 지정된 로거를 관리합니다.

#### 생성자

```python
LoggerManager(
    base_dir: Union[str, Path] = None,
    second_log_dir: Union[str, Path] = "default",
)
```

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `base_dir` | `Union[str, Path]` | `None` | 로그 저장 루트 디렉토리. `None`이면 `Path.cwd() / "logs"`를 사용합니다 |
| `second_log_dir` | `Union[str, Path]` | `"default"` | 해석된 `base_dir` 바로 아래에 생성될 하위 디렉토리 이름 |

로그 파일은 다음과 같이 구성됩니다: `{resolved_base_dir}/{second_log_dir}/{timestamp}_log/{logger_name}.log`

#### 메서드

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

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `logger_name` | `str` | — | 로거의 고유 이름 |
| `log_level` | `Union[int, str]` | `logging.INFO` | 최소 로그 레벨 (예: `logging.DEBUG`, `logging.WARNING`, 또는 `"DEBUG"`) |
| `timestamp` | `Any` | `None` | 로그 디렉토리 이름에 사용할 커스텀 타임스탬프; `None` = 현재 시간 |

> `time=...`은 `timestamp`의 더 이상 사용되지 않는 별칭으로 허용됩니다.

**반환값:** `Result(True, None, None, "Logger 'name' created successfully.")`

실제 `logging.Logger` 인스턴스가 필요하면 `get_logger(logger_name)`를 호출하세요.

##### `get_logger(logger_name) -> Result`

```python
def get_logger(self, logger_name: str) -> Result
```

기존 명명된 로거 인스턴스를 조회합니다.

**반환값:** `Result(True, None, None, logging.Logger)` 또는 찾을 수 없는 경우 `Result(False, ...)`.

##### `stop_stream_handlers(logger) -> Result`

```python
def stop_stream_handlers(self, logger: logging.Logger) -> Result
```

로거에서 콘솔(스트림) 핸들러를 제거합니다. 이 메서드를 호출하면 로거는 파일 핸들러에만 기록합니다.

> **경고**: `make_logger()`에 의해 생성된 스트림 핸들러가 두 번째 핸들러(인덱스 1)라고 가정합니다. 외부 핸들러 수정은 예기치 않은 동작을 유발할 수 있습니다.

---

### Log

구조화된 `log_message()` 호출을 위한 `logging.Logger` 래퍼.

#### 생성자

```python
Log(logger: logging.Logger = None)
```

#### 메서드

##### `log_message(level, message) -> Result`

```python
def log_message(self, level: Optional[Union[int, str]], message: str) -> Result
```

| 파라미터 | 타입 | 설명 |
|-----------|------|-------------|
| `level` | `Union[int, str]` | 로그 레벨 — 정수 (예: `10`, `20`) 또는 문자열 (예: `"INFO"`, `"DEBUG"`) |
| `message` | `str` | 로그에 기록할 메시지 |

---

### SimpleSetting

`LoggerManager`, `Log`, `logging.Logger`를 한 번에 생성하는 도우미 클래스입니다.

#### 생성자

```python
SimpleSetting(
    base_dir: Union[str, Path],
    second_log_dir: Union[str, Path],
    logger_name: str,
    log_level: Union[int, str] = logging.INFO,
)
```

#### 메서드

##### `get_instance() -> Tuple[LoggerManager, Log, logging.Logger]`

```python
def get_instance(self) -> Tuple[LoggerManager, Log, logging.Logger]
```

바로 사용할 수 있는 `(LoggerManager, Log, logging.Logger)` 튜플을 반환합니다.

```python
from tbot223_core import LoggerManager, Log
from tbot223_core.LogSys import SimpleSetting

setting = SimpleSetting(base_dir=".", second_log_dir="my_app", logger_name="AppLogger")
logger_manager, log, logger = setting.get_instance()
log.log_message("INFO", "Application started")
```

---

## ExceptionTracker

시스템 정보 캐시를 지원하는 종합적인 예외 추적 기능입니다.

시스템 정보(OS, 아키텍처, Python 버전 등)는 인스턴스 생성 시 한 번 캐시되며 이후 모든 호출에서 재사용됩니다.

### 생성자

```python
ExceptionTracker()
```

### 메서드

#### `get_exception_location(error) -> Result`

```python
def get_exception_location(self, error: Exception) -> Result
```

예외가 발생한 소스 위치를 추출합니다.

**반환값:** `Result(True, None, None, "'{file}', line {line}, in {function}")`

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

상세한 에러 페이로드 딕셔너리를 생성합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `error` | `Exception` | — | 포착된 예외 |
| `user_input` | `Any` | `None` | 에러를 유발한 사용자 입력 |
| `params` | `Tuple[Tuple, dict]` | `None` | 호출 함수의 `(args, kwargs)` |
| `mask_tuple` | `Tuple[bool, ...]` | `()` | 민감한 필드 마스킹. 순서: `(user_input, params, traceback, computer_info)` — `True` = 마스킹됨 |

**반환값:** `Result(True, None, None, error_info_dict)` — [에러 정보 구조](#에러-정보-구조)를 참조하세요.

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

예외로부터 표준화된 실패 `Result`를 생성합니다. 내부적으로 `get_exception_info()`를 호출합니다.

**반환값:** `Result(False, error_message, exception_location, error_info_dict)`

---

#### `get_error_code(error_id_map, error) -> Result`

```python
def get_error_code(self, error_id_map: dict, error: Exception) -> Result
```

예외 타입을 사용자 정의 에러 코드에 매핑합니다.

| 파라미터 | 타입 | 설명 |
|-----------|------|-------------|
| `error_id_map` | `dict` | `{ExceptionType: error_code}` 매핑 |
| `error` | `Exception` | 포착된 예외 |

```python
error_map = {ValueError: 1001, FileNotFoundError: 1002, KeyError: 1003}
result = tracker.get_error_code(error_map, caught_error)
print(result.data)  # 1001
```

**반환값:** `Result(True, None, None, error_code)` 또는 예외 타입이 맵에 없는 경우 `Result(False, ...)`.

---

## ExceptionTrackerDecorator

함수에 자동 예외 추적을 적용하는 데코레이터. 성공적인 반환값은 그대로 통과되며, 예외는 포착되어 `Result(False, ...)`로 반환됩니다.

### 생성자

```python
ExceptionTrackerDecorator(
    mask_tuple: Tuple[bool, bool, bool, bool] = (False, False, False, False),
    tracker: ExceptionTracker = None,
)
```

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `mask_tuple` | `Tuple[bool, bool, bool, bool]` | `(False, False, False, False)` | 마스킹 필드: `(user_input, params, traceback, computer_info)` |
| `tracker` | `ExceptionTracker` | `None` | 기존 tracker 공유; `None`이면 새로 생성 |

```python
from tbot223_core import ExceptionTrackerDecorator

@ExceptionTrackerDecorator(mask_tuple=(False, False, True, True))
def risky_operation(x):
    return 1 / x

result = risky_operation(0)
print(result.success)  # False
print(result.error)    # "ZeroDivisionError :division by zero"
```

함수 메타데이터(`__name__`, `__doc__`)는 `functools.wraps`를 통해 보존됩니다.

---

## Result 객체

모든 공개 함수는 `Result` NamedTuple을 반환합니다:

```python
from tbot223_core import Result

Result(
    success: Optional[bool],  # True = 성공, False = 실패, None = 취소됨
    error: Optional[str],     # 에러 메시지 (성공 시 None)
    context: Optional[str],   # 추가 컨텍스트 정보 (성공 시 None)
    data: Any,                # 반환된 데이터 또는 실패 상세 정보
)
```

성공 시 `data`에는 반환값이 들어갑니다. 실패 시에는 `None`, 메서드별 상세 정보, 또는 `ExceptionTracker`가 반환한 구조화된 `error_info` 딕셔너리가 들어갈 수 있습니다.

### 메서드

#### `unwrap() -> Any`

`success is True`이면 `data`를 반환합니다. `success is False` 또는 `None`이면 `ResultUnwrapException`을 발생시킵니다.

```python
data = fm.read_json("config.json").unwrap()  # 읽기 실패 시 예외 발생
```

#### `expect(msg="") -> Any`

`unwrap()`과 동일하지만, 커스텀 메시지와 함께 예외를 발생시킵니다. `msg`가 비어 있으면 원래 에러 메시지가 사용됩니다.

```python
data = fm.read_json("config.json").expect("Config file is required")
```

#### `unwrap_or(default) -> Any`

`success is True`이면 `data`를 반환하고, 그렇지 않으면 `default`를 반환합니다.

```python
data = fm.read_json("config.json").unwrap_or({"fallback": True})
```

### ResultUnwrapException

`unwrap()` 및 `expect()`에 의해 발생합니다. 속성:

| 속성 | 타입 | 설명 |
|-----------|------|-------------|
| `error` | `str` | 에러 메시지 |
| `context` | `str` | 추가 컨텍스트 |
| `data` | `Any` | 원래의 `Result.data` payload. 실패 시 상세 정보가 들어 있었다면 그 값도 그대로 포함 |

---

## Utils

해싱, 경로 작업, 데이터 조작을 위한 유틸리티 함수 모음.

### 생성자

```python
Utils(
    is_logging_enabled: bool = False,
    base_dir: Union[str, Path] = None,
    logger_manager_instance: Optional[LoggerManager] = None,
    logger: Optional[logging.Logger] = None,
    log_instance: Optional[Log] = None,
)
```

### 메서드

#### `str_to_path(path_str) -> Result`

```python
def str_to_path(self, path_str: str) -> Result
```

문자열을 `pathlib.Path` 객체로 변환합니다.

**반환값:** `Result(True, None, None, Path(...))`

---

#### `hashing(data, algorithm) -> Result`

```python
def hashing(self, data: str, algorithm: str = "sha256") -> Result
```

지정된 알고리즘을 사용하여 문자열을 해싱합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `data` | `str` | — | 해싱할 문자열 |
| `algorithm` | `str` | `"sha256"` | 다음 중 하나: `"md5"`, `"sha1"`, `"sha256"`, `"sha512"` |

**반환값:** `Result(True, None, None, "hex_digest_string")`

> **참고**: 해싱은 단방향 연산이며 암호화가 아닙니다.

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

랜덤 솔트를 사용하여 PBKDF2-HMAC 비밀번호 해시를 생성합니다.

| 파라미터 | 타입 | 설명 |
|-----------|------|-------------|
| `password` | `str` | 해싱할 비밀번호 |
| `algorithm` | `str` | 다음 중 하나: `"sha1"`, `"sha256"`, `"sha512"` |
| `iterations` | `int` | PBKDF2 반복 횟수 (예: `100000`) |
| `salt_size` | `int` | 솔트 크기 (바이트 단위, 예: `16`) |

**반환값:** `Result(True, None, None, {"salt_hex": "...", "hash_hex": "...", "iterations": 100000, "algorithm": "sha256"})`

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

기존 PBKDF2-HMAC 해시에 대해 비밀번호를 검증합니다.

**반환값:** 일치하면 `Result(True, None, None, True)`, 불일치하면 `Result(True, None, None, False)`.

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

리스트 또는 문자열에 일정 간격으로 요소를 삽입합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `data` | `Union[List, str]` | — | 수정할 리스트 또는 문자열 |
| `interval` | `int` | — | 삽입 간격 |
| `insert` | `Any` | — | 삽입할 요소 |
| `at_start` | `bool` | `True` | `True` = 시작부터 카운트, `False` = 끝부터 카운트 |

**반환값:** `Result(True, None, None, modified_data)`

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

비교 조건을 만족하는 딕셔너리 키를 검색합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `dict_obj` | `Dict` | — | 검색할 딕셔너리 |
| `threshold` | `Union[int, float, str, bool]` | — | 비교할 값 |
| `comparison` | `str` | `"eq"` | 연산자: `"eq"`, `"ne"`, `"gt"`, `"ge"`, `"lt"`, `"le"` |
| `nested` | `bool` | `False` | `True` = 중첩된 딕셔너리를 재귀적으로 검색 |
| `separator` | `str` | `"/"` | 중첩 결과의 키 경로 구분자입니다. `"tuple"`로 지정하면 최종 컬렉션을 리스트 대신 튜플로 반환합니다 |
| `return_mod` | `str` | `"flat"` | 반환 형식: `"flat"`, `"forest"`, `"path"` |

**반환값:** `Result(True, None, None, [matched_keys])` 또는 `Result(True, None, None, {nested_result})`

---

## GlobalVars

공유 메모리 IPC를 지원하는 스레드 안전 전역 변수 관리.

### 생성자

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

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `is_logging_enabled` | `bool` | `False` | 내부 로깅 활성화 |
| `base_dir` | `Union[str, Path]` | `None` | 로그 파일의 기본 디렉토리 |
| `shared_memory_cache_max_size` | `int` | `5` | 캐시된 공유 메모리 핸들의 최대 수 (LRU 제거) |

### 변수 작업

#### `set(key, value, overwrite) -> Result`

```python
def set(self, key: str, value: object, overwrite: bool = False) -> Result
```

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `key` | `str` | — | 변수 이름 (비어 있지 않은 문자열이어야 함) |
| `value` | `object` | — | 저장할 값 |
| `overwrite` | `bool` | `False` | `False` = 키가 이미 존재하면 `KeyError` 발생 |

#### `get(key) -> Result`

```python
def get(self, key: str) -> Result
```

**반환값:** `Result(True, None, None, stored_value)` 또는 키를 찾을 수 없는 경우 `Result(False, ...)`.

#### `delete(key) -> Result`

```python
def delete(self, key: str) -> Result
```

#### `clear() -> Result`

```python
def clear(self) -> Result
```

저장된 모든 변수를 삭제합니다.

#### `exists(key) -> Result`

```python
def exists(self, key: str) -> Result
```

**반환값:** 존재하면 `Result(True, None, None, True)`, 존재하지 않으면 `Result(True, None, None, False)`.

#### `list_vars() -> Result`

```python
def list_vars(self) -> Result
```

**반환값:** `Result(True, None, None, ["key1", "key2", ...])`

### 대체 접근 문법

```python
gv = GlobalVars()

# 속성 문법
gv.name = "hello"      # set("name", "hello")
print(gv.name)          # get("name").data

# 호출 문법
gv("name", "hello")     # set("name", "hello")
gv("name")              # get("name")
```

### 스레드 안전성

```python
# 내장 잠금 사용
with gv.lock():
    gv.set("counter", gv.get("counter").data + 1, overwrite=True)

# 또는 컨텍스트 매니저 사용
with gv:
    gv.set("counter", gv.get("counter").data + 1, overwrite=True)
```

### 공유 메모리 메서드

#### `shm_gen(name, size, create_lock) -> Result`

```python
def shm_gen(self, name: str = None, size: int = 1024, create_lock: bool = True) -> Result
```

POSIX 공유 메모리 블록을 생성하거나 연결합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `name` | `str` | `None` | 공유 메모리 이름. 비어 있지 않은 문자열이어야 하며 `None`이나 빈 문자열은 실패합니다 |
| `size` | `int` | `1024` | 블록 크기 (바이트 단위) |
| `create_lock` | `bool` | `True` | `True` = 프로세스 간 동기화를 위한 `multiprocessing.Lock` 생성 |

**반환값:** `create_lock=True`이면 `Result(True, None, None, lock)`, 아니면 `Result(True, None, None, "success to create shared memory object")`를 반환합니다.

**이름 충돌**: 이름이 이미 존재하면 기존 블록에 연결하고 `size >= 요청된 크기`를 검증합니다.

#### `shm_connect(name) -> Result`

```python
def shm_connect(self, name: str) -> Result
```

비소유자로서 기존 공유 메모리 블록에 연결합니다. 워커/자식 프로세스에서 사용하세요.

#### `shm_sync(name, serialize_format) -> Result`

```python
def shm_sync(self, name: str, serialize_format: str = "json") -> Result
```

현재 변수를 직렬화하여 공유 메모리에 씁니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `name` | `str` | — | 공유 메모리 이름 |
| `serialize_format` | `str` | `"json"` | `"json"` (안전한 기본값) 또는 `"pickle"` (신뢰할 수 있는 프로세스 전용) |

#### `shm_update(name, serialize_format) -> Result`

```python
def shm_update(self, name: str, serialize_format: str = "json") -> Result
```

공유 메모리에서 읽고 역직렬화된 데이터를 이 인스턴스의 변수에 병합합니다.

#### `shm_get(name) -> Result`

```python
def shm_get(self, name: str) -> Result
```

`name`에 대한 캐시된 `SharedMemory` 핸들을 반환하거나, 아직 캐시되지 않은 경우 연결합니다.

**반환값:** `Result(True, None, None, SharedMemory)`

#### `shm_close(name, close_only) -> Result`

```python
def shm_close(self, name: str, close_only: bool = False) -> Result
```

| 파라미터 | 타입 | 기본값 | 설명 |
|-----------|------|---------|-------------|
| `name` | `str` | — | 공유 메모리 이름 |
| `close_only` | `bool` | `False` | `True` = 핸들만 닫기 (비소유자 프로세스용), `False` = 닫고 해제 (소유자용) |

**소유권 규칙**: `shm_gen()`을 호출한 프로세스가 소유자이며, 블록을 해제하려면 `shm_close(name)` (`close_only=False`)을 호출해야 합니다. `shm_connect()`를 통해 연결된 자식 프로세스는 `shm_close(name, close_only=True)`를 사용해야 합니다.

> **보안**: JSON이 기본 직렬화 형식입니다. 신뢰할 수 없는 데이터의 `pickle` 역직렬화는 임의 코드를 실행할 수 있습니다. 통신하는 모든 프로세스가 신뢰할 수 있는 경우에만 `serialize_format="pickle"`을 사용하세요.

---

## DecoratorUtils

### `count_runtime()`

```python
@staticmethod
def count_runtime() -> Callable
```

함수의 실행 시간을 출력하는 데코레이터.

```python
from tbot223_core import DecoratorUtils

@DecoratorUtils.count_runtime()
def slow_function():
    time.sleep(1)

slow_function()
# Output: slow_function executed in 1.001s
```

함수 메타데이터는 `functools.wraps`를 통해 보존됩니다.

---

## 에러 정보 구조

`ExceptionTracker`를 통해 예외를 추적하면 `Result.data` 필드에 상세한 오류 정보 딕셔너리가 포함됩니다:

```python
{
    "success": False,
    "error": {
        "type": "ValueError",           # 예외 클래스 이름
        "message": "invalid literal..."  # 예외 메시지
    },
    "location": {
        "file": "app.py",               # 예외가 포착된 파일
        "line": 42,                      # 줄 번호
        "function": "process_data"       # 함수 이름
    },
    "origin_location": {
        "file": "parser.py",            # 예외가 발생한 파일
        "line": 15,                      # 줄 번호
        "function": "parse"             # 함수 이름
    },
    "timestamp": "2026-04-03 14:30:00",
    "input_context": {
        "user_input": "...",            # 에러를 유발한 사용자 입력 (마스킹 가능)
        "params": {                     # 함수 파라미터 (마스킹 가능)
            "args": (...),
            "kwargs": {...}
        }
    },
    "traceback": "Traceback (most recent call last):\n...",  # 전체 트레이스백 (마스킹 가능)
    "computer_info": {                  # 시스템 정보 — 인스턴스 생성 시 캐시됨 (마스킹 가능)
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

**마스킹**: `mask_tuple=(user_input, params, traceback, computer_info)`를 전달하여 민감한 필드를 숨길 수 있습니다. 예를 들어, `mask_tuple=(False, False, True, True)`는 트레이스백과 시스템 정보를 숨깁니다.

---

## 공유 메모리 사용법

프로세스 간 통신의 전체 작동 예제:

```python
from tbot223_core import GlobalVars
from multiprocessing import Process

# 워커 함수 (spawn 컨텍스트에서 모듈 레벨에 정의되어야 함)
def worker(shm_name, lock):
    gv_worker = GlobalVars()
    gv_worker.shm_connect(shm_name)          # 비소유자로 연결
    try:
        with lock:
            gv_worker.shm_update(shm_name)    # 공유 메모리에서 현재 상태 읽기
            current = gv_worker.get("counter").data
            gv_worker.set("counter", current + 1, overwrite=True)
            gv_worker.shm_sync(shm_name)      # 업데이트된 상태를 다시 쓰기
    finally:
        gv_worker.shm_close(shm_name, close_only=True)  # 비소유자: 닫기만

if __name__ == "__main__":
    gv = GlobalVars()

    # 1. 프로세스 간 잠금을 포함한 공유 메모리 (4 KB) 생성
    result = gv.shm_gen("my_shm", size=4096, create_lock=True)
    shm_lock = result.data  # multiprocessing.Lock

    # 2. 변수 초기화 및 공유 메모리에 쓰기
    gv.set("counter", 0, overwrite=True)
    gv.shm_sync("my_shm")

    # 3. 워커 프로세스 생성
    processes = [Process(target=worker, args=("my_shm", shm_lock)) for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    # 4. 최종 상태 읽기
    gv.shm_update("my_shm")
    print(f"Final counter: {gv.get('counter').data}")  # Output: 4

    # 5. 소유자 정리 — 닫고 해제
    gv.shm_close("my_shm")
```

### 핵심 사항

| 개념 | 상세 내용 |
|---------|--------|
| **직렬화** | 기본값은 JSON; pickle을 사용하려면 `serialize_format="pickle"` 전달 (신뢰할 수 있는 프로세스 전용) |
| **소유권** | `shm_gen()` = 소유자. `shm_connect()` = 비소유자. 소유자가 `shm_close(name)`을 호출하여 해제 |
| **잠금** | `create_lock=True`는 프로세스 간 동기화를 위한 `multiprocessing.Lock`을 반환 |
| **캐시** | 공유 메모리 핸들은 LRU 방식으로 캐시됩니다 (기본 최대 5개). 제거할 때는 `close()`만 호출하고 `unlink()`는 호출하지 않습니다 |
| **이름 충돌** | 이름이 존재하면 `shm_gen()`은 기존 블록에 연결하고 크기를 검증 |
