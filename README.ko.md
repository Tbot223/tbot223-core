[English](README.md)

> 이 문서는 v4.0.0 기준입니다.

# tbot223-core

[![PyPI](https://img.shields.io/pypi/v/tbot223-core)](https://pypi.org/project/tbot223-core/)
[![Python](https://img.shields.io/pypi/pyversions/tbot223-core)](https://pypi.org/project/tbot223-core/)
[![License](https://img.shields.io/pypi/l/tbot223-core)](LICENSE)

<details>
<summary>목차</summary>

- [왜 tbot223-core인가?](#왜-tbot223-core인가)
- [주요 기능](#주요-기능)
- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [Import 가이드](#import-가이드)
- [핵심 모듈](#핵심-모듈)
- [Result 객체](#result-객체)
- [예제](#예제)
- [문서](#문서)
- [라이선스](#라이선스)
- [링크](#링크)
</details>

파이썬 애플리케이션을 위한 의존성 없는 핵심 유틸리티 패키지입니다.
Result 패턴을 바탕으로 파일 관리, 로깅, 예외 추적, 병렬 실행 기능을 제공합니다.

## 왜 tbot223-core인가?

모든 공개 함수가 예외를 발생시키는 대신 `Result` 객체를 반환합니다.
성공이든 실패이든 모든 작업에 일관되고 예측 가능한 반환 형식을 제공합니다.
매번 `try/except`로 감쌀 필요 없이, `result.success`를 확인하거나 `.unwrap()`을 호출하면 됩니다.

핵심 `Result` 타입은 독자적으로 설계했고, `unwrap()`, `expect()`, `unwrap_or()` 세 가지 편의 메서드는 이후 Rust의 `Result<T, E>`에서 영감을 얻었습니다.

이런 경우에 특히 잘 맞습니다:

- 예외를 여기저기서 잡기보다 성공/실패 흐름이 명시적으로 보이는 걸 좋아하는 분
- 작은 도구, 자동화 스크립트, 내부 유틸리티에 바로 쓸 공통 기반 툴킷이 필요한 분
- 런타임에서 예상치 못한 트레이스백보다 일관된 반환 형식이 더 편한 분

파이썬의 전통적인 예외 중심 방식보다, 명시적인 성공/실패 패턴을 택한 라이브러리입니다.

## 주요 기능

- **일관된 Result 객체** — 모든 함수가 `success`, `error`, `context`, `data` 필드를 가진 표준화된 `Result` NamedTuple을 반환
- **안정적인 파일 관리** — 원자적 쓰기(임시 파일 + rename), JSON I/O, 대용량 파일 잠금, 디렉토리 작업
- **고급 로깅 시스템** — 타임스탬프 기반 자동 파일 구성, 설정 가능한 레벨, `SimpleSetting`으로 한 번에 설정할 수 있는 도우미
- **예외 추적** — 소스 위치 추출, 전체 트레이스백 캡처, 시스템 정보 캐시, 민감 데이터 마스킹
- **병렬 실행** — `ThreadPoolExecutor` / `ProcessPoolExecutor` 래퍼 (타임아웃, 청킹, 워커 제한 지원)
- **다국어 지원** — JSON 기반 로컬라이제이션, 내부 캐시, 필요 시 자동 다시 로드
- **공유 메모리 IPC** — 프로세스 안전 전역 변수, JSON/pickle 직렬화, LRU 캐시 핸들, 소유권 추적

## 설치

```bash
pip install tbot223-core
```

Python 3.10 - 3.14. 외부 의존성 없음.

## 빠른 시작

### 1. Result 패턴을 활용한 파일 작업

```python
from tbot223_core import FileManager

fm = FileManager()

# 모든 작업은 Result를 반환 — 예외를 잡을 필요 없음
result = fm.write_json("config.json", {"key": "value"})

if result.success:
    print("저장 성공")
else:
    print(f"실패: {result.error}")

# unwrap() — 성공 시 data를 반환하고, 실패 시 ResultUnwrapException을 발생시킴
data = fm.read_json("config.json").unwrap()

# expect() — unwrap()과 동일하나 커스텀 에러 메시지 지정 가능
data = fm.read_json("config.json").expect("설정 파일이 필요합니다")

# unwrap_or() — 성공 시 data, 실패 시 기본값 반환
data = fm.read_json("missing.json").unwrap_or({"default": True})
```

### 2. ResultWrapper로 함수 자동 래핑

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

### 3. 구조화된 로깅

```python
from tbot223_core.LogSys import SimpleSetting

setting = SimpleSetting(
    base_dir=".",
    second_log_dir="my_app",
    logger_name="AppLogger",
)
logger_manager, log, logger = setting.get_instance()

log.log_message("INFO", "애플리케이션 시작")
log.log_message("ERROR", "문제가 발생했습니다")
# 로그 파일: ./my_app/{타임스탬프}_log/AppLogger.log
```

### 4. 병렬 실행

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

## Import 가이드

모든 핵심 클래스는 `tbot223_core`에서 직접 import할 수 있습니다:

```python
from tbot223_core import (
    AppCore,                    # 병렬 실행, CLI 입력, 다국어
    ResultWrapper,              # 데코레이터: 반환값을 Result로 래핑
    FileManager,                # 파일 I/O, JSON, 원자적 쓰기
    LoggerManager, Log,         # 구조화된 로깅
    ExceptionTracker,           # 예외 정보 추출
    ExceptionTrackerDecorator,  # 데코레이터: 자동 예외→Result 변환
    Utils,                      # 해싱, 경로 변환, 데이터 조작
    GlobalVars,                 # 스레드 안전 전역 변수 + 공유 메모리
    DecoratorUtils,             # 실행 시간 측정
    Result,                     # Result NamedTuple
)

# Result 관련 예외:
from tbot223_core.Result import ResultUnwrapException

# SimpleSetting (최상위에서 re-export되지 않음):
from tbot223_core.LogSys import SimpleSetting
```

## 핵심 모듈

| 모듈 | 설명 | 주요 메서드 |
|------|------|------------|
| `AppCore` | 병렬 실행, 콘솔 관리, CLI 입력, 다국어 | `thread_pool_executor()`, `process_pool_executor()`, `safe_CLI_input()`, `get_text_by_lang()` |
| `ResultWrapper` | 데코레이터: 함수의 반환값을 `Result`로 래핑 | `@ResultWrapper()` |
| `FileManager` | 원자적 쓰기, 파일/JSON I/O, 디렉토리 작업 | `atomic_write()`, `read_file()`, `write_json()`, `read_json()`, `exists()` |
| `LogSys` | 자동 파일 관리 구조화된 로깅 | `make_logger()`, `get_logger()`, `log_message()`, `SimpleSetting` |
| `ExceptionTracker` | 예외 위치/정보 추적, 에러 코드 매핑 | `get_exception_info()`, `get_exception_return()`, `get_error_code()` |
| `Utils` | 해싱, 경로 변환, PBKDF2, 데이터 조작 | `hashing()`, `pbkdf2_hmac()`, `find_keys_by_value()`, `insert_at_intervals()` |
| `GlobalVars` | 공유 메모리 IPC를 지원하는 스레드 안전 전역 변수 | `set()`, `get()`, `shm_gen()`, `shm_sync()`, `shm_update()`, `shm_close()` |
| `DecoratorUtils` | 실행 시간 측정 | `@DecoratorUtils.count_runtime()` |

전체 메서드 시그니처, 파라미터, 반환값은 [API 레퍼런스](docs/API.ko.md)를 참고하세요.

## Result 객체

모든 공개 함수는 `Result` NamedTuple을 반환합니다:

```python
Result(
    success: Optional[bool],  # True = 성공, False = 실패, None = 취소됨
    error: Optional[str],     # 에러 메시지 (성공 시 None)
    context: Optional[str],   # 추가 컨텍스트 (성공 시 None)
    data: Any,                # 반환 데이터 또는 실패 상세 정보
)
```

성공 시 `data`에는 반환값이 들어갑니다. 실패 시에는 `None`이 들어갈 수도 있고, 메서드별 상세 정보나 `ExceptionTracker`가 만든 구조화된 `error_info` 딕셔너리가 들어갈 수도 있습니다.

### 메서드

| 메서드 | 성공 시 | 실패 시 |
|--------|---------|---------|
| `unwrap()` | `data` 반환 | `ResultUnwrapException` 발생 |
| `expect(msg)` | `data` 반환 | 커스텀 `msg`와 함께 `ResultUnwrapException` 발생 |
| `unwrap_or(default)` | `data` 반환 | `default` 반환 |

실패한 `Result`에 대해 `unwrap()`이나 `expect()`가 예외를 발생시키면, 원래의 `Result.data` payload는 `ResultUnwrapException.data`에 그대로 보존됩니다.

## 예제

[examples/](examples/) 디렉토리에 모듈별로 정리된 40개 이상의 실행 가능한 스크립트가 있습니다.
각 스크립트는 독립 실행 가능하며 성공 시 `TEST COMPLETE`를 출력합니다.

| 모듈 | 예제 |
|------|------|
| Result | 기본 사용법, `unwrap()`, `expect()`, `unwrap_or()` |
| AppCore | 스레드/프로세스 풀, CLI 입력, 다국어, ResultWrapper |
| FileManager | 원자적 쓰기, JSON I/O, 파일 목록, 디렉토리 작업 |
| LogSys | 로거 생성, 로그 메시지, SimpleSetting 한 번에 설정 |
| ExceptionTracker | 예외 정보, 위치 추적, 에러 코드, 데코레이터 |
| Utils | 해싱, PBKDF2, 경로 변환, 인터벌 삽입, 딕셔너리 검색 |
| GlobalVars | 기본 CRUD, 속성/호출 문법, 스레드 잠금, 공유 메모리 IPC |
| DecoratorUtils | 실행 시간 측정 |

전체 목록과 설명은 [예제 문서](docs/Examples.ko.md)를 참고하세요.

## 문서

- [API 레퍼런스](docs/API.ko.md) — 전체 메서드 시그니처, 파라미터, 반환값, 사용 예제
- [마이그레이션 가이드](docs/MIGRATION_GUIDE.ko.md) — 2.x 또는 3.x에서 4.x로 업그레이드하는 경로 안내
- [릴리스 노트](docs/RELEASE_NOTES.ko.md) — 변경 이력 및 버전 히스토리
- [예제 문서](docs/Examples.ko.md) — 40개 이상의 실행 가능한 예제 스크립트 (설명 포함)

## 라이선스

[Apache License 2.0](LICENSE)

## 링크

- [GitHub](https://github.com/Tbot223/tbot223-core)
- [PyPI](https://pypi.org/project/tbot223-core/)
- Author: tbot223 (tbotxyz@gmail.com)
