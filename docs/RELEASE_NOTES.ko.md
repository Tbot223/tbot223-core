# 릴리스 노트

[English](RELEASE_NOTES.md)

<details>
<summary>목차</summary>

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

### 주요 변경

- **GlobalVars**: `gv.some_key` 같은 없는 속성 접근이 더 이상 `"Key does not exist."` 문자열을 반환하지 않고 `AttributeError`를 발생시킵니다. 기존에 이 문자열 비교에 의존하던 코드는 `get()`, `exists()`, 또는 `try/except AttributeError`로 바꿔야 합니다.
- **GlobalVars**: 호출 문법에서 `None`이 이제 실제 값으로 취급됩니다. `gv("key", None)`은 조회가 아니라 `None`을 저장합니다. 조회는 `gv("key")`를 사용해야 합니다.
- **GlobalVars**: 공유 메모리 소유권 규칙이 명시적으로 적용됩니다. `shm_close(name)`은 현재 프로세스가 생성한 블록만 unlink하고, 비소유자는 `shm_close(name, close_only=True)`를 사용해야 합니다. 또한 `shm_gen()`은 기존 블록에 연결할 때 요청한 크기보다 작은 블록이면 실패합니다.
- **AppCore**: `process_pool_executor(chunk_size=None)`는 더 이상 자동 청킹이 아닙니다. 이제 전체 작업 목록을 단일 executor에 제출합니다. 자동 청킹이 필요하면 `chunk_size=0`, 명시적 배치가 필요하면 양의 정수를 전달해야 합니다.

### 추가

- **FileManager**: 존재 여부 확인용 권장 API로 `exists()`를 추가했고, `exist()`는 deprecated alias로 유지합니다.
- **Result**: `Result.expect(msg="")`가 선택적 커스텀 실패 메시지를 지원합니다. 실패 payload 자체는 그대로 유지됩니다.
- **LogSys**: `LoggerManager.make_logger()`의 권장 키워드로 `timestamp=`를 추가했습니다. 기존 `time=`은 deprecated alias로 계속 지원됩니다.
- **타이핑/패키징**: `tbot223_core/py.typed`를 패키지에 포함하고 `setup.py`를 통해 함께 배포하도록 정리해, 외부 타입 체커가 배포된 타입 정보를 인식할 수 있게 했습니다.
- **예제**: `safe_CLI_input`, `get_error_code`, `exist`, `unwrap`, `expect`, `unwrap_or`, 그리고 `Utils` / `GlobalVars` 계열의 실행 가능한 예제를 추가했습니다.
- **문서**: API 레퍼런스, 예제 문서, 마이그레이션 가이드, 릴리스 노트를 `docs/` 아래에서 영어/한국어 파일로 분리해 제공합니다.

### 변경

- **문서 구조**: 장문 문서를 `docs/` 중심으로 재배치하고, 루트에는 `README.md`와 `README.ko.md`만 남겼습니다.
- **문서 정합성**: README/API/Examples 문서를 현재 런타임 동작에 맞게 다시 썼습니다. executor 반환 형태, `Result` 실패 payload, 로그 경로 의미, 다국어 폴백, bool 파싱, PBKDF2 반환 구조, 공유 메모리 소유권/정리 규칙이 모두 현재 코드 기준으로 설명됩니다.
- **AppCore**: `workers` 기본값을 import 시점이 아니라 호출 시점에 해석하도록 정리해, 현재 CPU 수를 반영하고 오래된 기본값 문제를 줄였습니다.
- **테스트/도구**: 레거시 루트 `test.py` 흐름을 정리하고, 유지되는 테스트 진입점을 `TEST/SRC/` pytest 스위트 중심으로 맞췄습니다.
- **예제**: LogSys와 ResultWrapper 예제가 실제 반환값과 현재 로그 디렉토리 레이아웃을 반영하도록 갱신되었습니다.

### 수정

- **AppCore**: executor 검증, chunking 설명, 샘플 사용법을 현재 구현과 일치하도록 바로잡았습니다.
- **FileManager**: 존재 여부 확인 관련 문서와 예제 범위를 실제 `exists()` / `exist()` API 상태에 맞게 수정했습니다.
- **Utils**: PBKDF2와 중첩 딕셔너리 탐색 관련 문서/예제가 실제 반환 payload와 `separator="tuple"` 동작을 반영하도록 수정되었습니다.
- **Exception/Result**: unwrap/expect 예시와 실패 payload 설명을 구조화된 `error_info` 처리 방식과 맞췄습니다.
- **LogSys**: `make_logger()`는 성공 메시지를 반환하고, 실제 `logging.Logger`는 `get_logger()`로 가져와야 한다는 점을 문서와 예제에 맞게 반영했습니다.

### 문서

- **이중 언어 문서**: 영어와 한국어 문서를 각각 독립 파일로 분리하고 상호 링크를 모두 갱신했습니다.
- **한국어 문서 품질**: 한국어 릴리스 노트, 마이그레이션 가이드, API, 예제 문서를 요약판이 아니라 단독으로 읽을 수 있는 문서로 다시 다듬었습니다.
- **리포지토리 링크**: 내부 링크를 모두 새 `docs/` 구조에 맞게 업데이트했고, 더 이상 쓰지 않는 루트 문서 경로는 제거했습니다.

### 테스트

- **Pytest**: 현재 트리 기준으로 `TEST/SRC/AppCore_test.py`, `TEST/SRC/LogSys_test.py`, `TEST/SRC/Utils_test.py`, `TEST/SRC/Exception_test.py`를 검증했고 `163 passed`였습니다.
- **예제 실행**: 총 41개의 예제 스크립트를 확인했습니다. 40개는 배치 실행으로 검증했고, `examples/AppCore/restart_application.py`는 프로세스를 교체하는 특성 때문에 대화형으로 추가 검증했습니다.

<a id="v3-1-1"></a>
## [3.1.1] - 2026-03-28

### 수정

- **Utils**: `tbot223_core/Utils/` 서브패키지에 누락된 `__init__.py` 추가 — 이 파일 없이는 `find_packages()`가 `Utils/`를 인식하지 못해 `DecoratorUtils`, `Utils`, `GlobalVars`가 PyPI 배포에서 완전히 빠짐

---

<a id="v3-1-0"></a>
## [3.1.0] - 2026-03-27

### 보안

- **GlobalVars**: `shm_sync()`와 `shm_update()`의 기본 직렬화 형식을 `"pickle"`에서 `"json"`으로 변경 — 신뢰할 수 없는 데이터의 `pickle` 역직렬화는 임의 코드를 실행할 수 있음. 기존에 `pickle` 기본값에 의존하던 코드는 `serialize_format="pickle"`을 명시해야 함.

### 수정

- **FileManager**: `atomic_write()`의 잠재적 `NameError` 수정 — `temp_path`를 `try` 블록 전에 `None`으로 초기화
- **FileManager**: `delete_directory()`의 광범위한 `except:`를 `except TypeError:`로 좁힘
- **GlobalVars**: `__getattr__` 예외 처리 강화 — `KeyError`를 별도 처리, 예기치 않은 오류는 `_exception_tracker`로 라우팅
- **LogSys**: `LoggerManager`와 `Log`가 매 예외마다 새 `ExceptionTracker()`를 생성하는 대신 영속 인스턴스 유지
- **AppCore**: `_generic_executor()`의 executor shutdown 오류를 `_exception_tracker`로 추적
- **Utils**: `find_keys_by_value()`에서 `isinstance(...) is False`를 `not isinstance(...)`로 변경 (PEP 8)
- **Exception**: `get_exception_return()`의 `params` 기본값을 `None`에서 `((), {})`로 변경
- **Exception**: `get_error_code()` 반환 타입 힌트를 `None`에서 `Result`로 수정

### 변경

- **전체 모듈**: 반복되는 `if self.__is_logging_enabled__: self.log.log_message(...)`를 `_log(level, message)` 보조 메서드로 추출
- **GlobalVars**: `shm_update()` 역직렬화 오류 메시지가 실제 `serialize_format`을 반영하도록 수정
- **문서**: docstring Args 형식을 전체 모듈에서 백틱 스타일로 통일
- **AppCore**: `ProcessPoolExecutor`에 `mp_context=multiprocessing.get_context("spawn")` 전달 — 안전한 크로스 플랫폼 프로세스 생성
- **AppCore**: `safe_CLI_input()`에 `EOFError` 처리, `KeyboardInterrupt` 처리, bool 타입 변환 지원 추가

---

<a id="v3-0-1"></a>
## [3.0.1] - 2026-03-20

### 수정

- **ResultWrapper**: 예외마다 새 `ExceptionTracker` 생성 대신 단일 인스턴스 재사용
- **Exception**: `get_exception_info()` / `get_exception_return()` params 검증 개선
- **Utils**: `find_keys_by_value()`에서 `type(value) != type(threshold)`를 `type(value) is not type(threshold)`로 변경

### 변경

- **데코레이터**: `functools.wraps` 추가로 함수 메타데이터 보존 (`ResultWrapper`, `ExceptionTrackerDecorator`, `DecoratorUtils.count_runtime()`)
- **타입 힌트**: 데코레이터 반환 타입 어노테이션 개선
- **패키지**: `setup.py`의 description과 keywords 업데이트

---

<a id="v3-0-0"></a>
## [3.0.0] - 2026-02-07

### 주요 변경 (Breaking Changes)

- **임포트 시스템 전면 개편**: 클래스를 직접 임포트하여 사용 가능
  - 이전: `from tbot223_core import FileManager` → `FileManager.FileManager()`
  - 이후: `from tbot223_core import FileManager` → `FileManager()`
- **Utils 모듈 분리**: `Utils.py`가 서브패키지 `Utils/`로 분리
- **Exception API 변경**: `mask_tuple` 파라미터 추가, `get_error_code()` 메서드 추가
- **Result 객체 변경**: `success` 필드 타입 `bool` → `Optional[bool]` (`None` = 취소/미실행)

### 추가

- **Result 메서드**: `unwrap()`, `expect(msg="")`, `unwrap_or(default)`
- **ResultUnwrapException**: unwrap 실패 시 전용 예외 클래스
- **Exception 메서드**: `get_error_code()` — 사용자 정의 에러 코드 반환
- **테스트**: `Result_test.py` 추가

### 변경

- **기본 Workers**: `thread_pool_executor`와 `process_pool_executor`의 기본값이 `os.cpu_count()`로 변경
- **타임아웃 처리**: executor의 `as_completed` 타임아웃 스케일링 개선

---

<a id="v2-1-3"></a>
## [2.1.3] - 2026-01-27

### 추가

- **예제**: 모든 핵심 모듈의 종합 예제 스크립트 추가 (40개 이상)
- **LogSys**: `stop_stream_handlers()` 메서드 추가, `SimpleSetting` 로그 레벨 설정 지원
- **테스트**: 커버리지 확장 (72% → 81%)
- **Utils**: `find_keys_by_value()`에 `separator`, `return_mod` 파라미터 추가

### 수정

- **Utils**: `_lookup_dict()`에서 `extend()` 대신 `append()` 사용하여 중첩 결과 평탄화 방지
- **FileManager**: `shutil.rmtree()` 호환성 폴백 추가 (`onexc` → `onerror`)
- **AppCore**: `ResultWrapper`가 `params` 파라미터를 통해 함수 인자를 `ExceptionTracker.get_exception_return()`에 전달

---

<a id="v2-1-2"></a>
## [2.1.2] - 2026-01-19

### 수정

- **치명적**: `safe_CLI_input()`의 무한 루프 수정 — `max_retries` 파라미터 추가 (기본: 10)
- **치명적**: `insert_at_intervals()`의 인덱스 오프셋 버그 수정
- **치명적**: 하드코딩된 파일 크기 임계값을 `LOCK_FILE_SIZE_THRESHOLD` 상수로 교체 (10MB)

### 추가

- 공유 메모리 IPC용 JSON 직렬화 지원, `serialize_format` 파라미터
- 언어 캐시 관리 (`__lang_cache_management__` 데코레이터)
- `safe_CLI_input()`의 `SUPPORTED_TYPES` 및 `other_type` 파라미터
- `DecoratorUtils.make_decorator()` 메서드

### 보안

- 신뢰할 수 없는 프로세스 간 통신을 위한 JSON 직렬화 옵션 추가

---

<a id="v2-1-1"></a>
## [2.1.1] - 2026-01-18

### 추가

- `shm_connect()` 메서드 (자식 프로세스용)
- 헤더 기반 직렬화

### 변경

- `is_logging_enabled` → `__is_logging_enabled__` (비공개 속성)
- `shm_close()`에 `close_only` 파라미터 추가

---

<a id="v2-1-0"></a>
## [2.1.0] - 2026-01-16

### 추가

- GlobalVars 공유 메모리 IPC 지원: `shm_gen()`, `shm_sync()`, `shm_update()`, `shm_get()`, `shm_close()`
- GlobalVars 컨텍스트 매니저 지원 (`with gv:`)

### 변경

- `ExceptionTracker.get_exception_info()` params 타입: `dict` → `Tuple[Tuple, dict]`
