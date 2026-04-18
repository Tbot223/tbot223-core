<!-- markdownlint-disable-file MD041 -->

[English](../en/Examples.md)

> 이 문서는 v4.0.0 기준입니다.

# 예제

모든 예제는 **독립 실행 가능한 스크립트**입니다. 성공 시 `TEST COMPLETE`를 출력합니다.

<details>
<summary>목차</summary>

- [예제 실행](#예제-실행)
- [Result](#result)
- [AppCore](#appcore)
- [FileManager](#filemanager)
- [LogSys](#logsys)
- [ExceptionTracker](#exceptiontracker)
- [Utils](#utils)
- [GlobalVars](#globalvars)
- [DecoratorUtils](#decoratorutils)
</details>

## 예제 실행

```bash
# 예제 직접 실행
python examples/Result/unwrap.py
python examples/FileManager/atomic_write.py
```

로그 및 임시 파일은 `examples/.OtherFiles/`에 저장됩니다.

## Result

`Result` NamedTuple은 모든 공개 함수의 핵심 반환 타입입니다. 이 예제들은 Result를 생성, 검사, 값 추출하는 방법을 보여줍니다.

| 파일 | 설명 |
|------|------|
| [Result.py](../examples/Result/Result.py) | `Result` 객체를 직접 생성하고 각 필드(`success`, `error`, `context`, `data`)에 접근하는 방법을 보여줍니다. `True`, `False`, `None`(취소) 상태를 모두 시연합니다. |
| [unwrap.py](../examples/Result/unwrap.py) | `unwrap()`은 `success=True`일 때 `data`를 추출합니다. `False`나 `None`이면 오류 메시지, 컨텍스트, 데이터와 함께 `ResultUnwrapException`을 발생시킵니다. |
| [expect.py](../examples/Result/expect.py) | `expect(msg)`는 `unwrap()`과 비슷하지만 커스텀 오류 메시지를 지정할 수 있습니다. 상황별 실패 설명을 덧붙일 때 유용합니다. |
| [unwrap_or.py](../examples/Result/unwrap_or.py) | `unwrap_or(default)`는 성공 시 `data`를 반환하고, 실패 시 제공한 기본값을 반환합니다. 예외를 일으키지 않으므로 폴백이 필요한 작업에 적합합니다. |

## AppCore

애플리케이션 수준 유틸리티: 병렬 실행, CLI 입력, 다국어, 프로세스 제어.

| 파일 | 설명 |
|------|------|
| [thread_pool_executor.py](../examples/AppCore/thread_pool_executor.py) | `ThreadPoolExecutor`로 여러 함수를 동시에 실행합니다. `(function, kwargs_dict)` 태스크 형식, `workers` 제한, 입력 순서가 유지된 작업별 `Result` 수집을 보여줍니다. |
| [process_pool_executor.py](../examples/AppCore/process_pool_executor.py) | `ProcessPoolExecutor`(spawn 컨텍스트)로 CPU 바운드 태스크를 실행합니다. `chunk_size` 모드: `None`(단일 배치), `0`(자동), 양수(명시적)와 입력 순서가 유지된 작업별 `Result`를 시연합니다. |
| [get_text_by_lang.py](../examples/AppCore/get_text_by_lang.py) | `Languages/{lang}.json` 파일에서 다국어 텍스트를 불러옵니다. 내부에 캐시되며, 캐시에 없으면 자동으로 다시 로드됩니다. 지원되지 않는 언어 코드는 `default_lang`으로 폴백합니다. |
| [safe_CLI_input.py](../examples/AppCore/safe_CLI_input.py) | 타입 변환을 포함한 검증된 사용자 입력입니다. `str`, `int`, `float`, `bool`를 지원하며, bool은 `"true"/"false"`, `"yes"/"no"`, `"y"/"n"`, `"1"/"0"`, `"on"/"off"`, `"enable"/"disable"` 같은 값을 허용합니다. `EOFError`, `KeyboardInterrupt`도 처리합니다. |
| [clear_console.py](../examples/AppCore/clear_console.py) | 터미널 화면 지우기. Windows에서 `cls`, Unix에서 `clear` 사용. |
| [exit_application.py](../examples/AppCore/exit_application.py) | `sys.exit()`으로 프로세스 정상 종료. `pause=True`로 종료 전 사용자 입력 대기. |
| [restart_application.py](../examples/AppCore/restart_application.py) | `os.execv()`로 현재 Python 프로세스 재시작. `pause=True`로 재시작 전 대기. |
| [ResultWrapper.py](../examples/AppCore/ResultWrapper/ResultWrapper.py) | `@ResultWrapper()` 데코레이터 — 함수의 반환값을 `Result`로 래핑. 이미 `Result`를 반환하면 그대로 통과. 예외는 `Result(False, ...)`로 변환. `__name__`, `__doc__` 보존. |

## FileManager

안전한 파일 시스템 작업 — 원자적 쓰기, 파일 잠금, JSON 처리.

| 파일 | 설명 |
|------|------|
| [atomic_write.py](../examples/FileManager/atomic_write.py) | 원자적 쓰기 — 임시 파일에 먼저 쓴 후 대상 경로로 rename. 중간에 실패해도 원본 파일 보존. 부모 디렉토리 자동 생성. |
| [read_file.py](../examples/FileManager/read_file.py) | 텍스트 모드(`str`) 또는 바이너리 모드(`bytes`, `as_bytes=True`)로 파일 읽기. 10 MB 초과 파일은 자동으로 잠금 처리. |
| [write_json.py](../examples/FileManager/write_json.py) | Python 객체를 JSON으로 직렬화하여 디스크에 저장. 내부적으로 `atomic_write()` 사용. `indent` 설정 가능(기본 4칸). |
| [read_json.py](../examples/FileManager/read_json.py) | JSON 파일을 읽어 Python 객체로 파싱. `Result.data`에 파싱된 객체 반환. |
| [list_of_files.py](../examples/FileManager/list_of_files.py) | 디렉토리 내 파일 목록을 조회합니다. `extensions` 필터(예: `[".json", ".txt"]`)를 지원하며, `only_name=True`이면 확장자를 제외한 파일 stem만 반환합니다. |
| [exist.py](../examples/FileManager/exist.py) | 파일이나 디렉토리의 존재 여부를 확인합니다. `Result(True, None, None, True/False)`를 반환합니다. 참고로 `exist()`는 더 이상 권장되지 않는 별칭이므로 `exists()` 사용을 권장합니다. |
| [create_directory.py](../examples/FileManager/create_directory.py) | 부모 디렉토리 포함 디렉토리 생성 (`parents=True`, `exist_ok=True`). |
| [delete_file.py](../examples/FileManager/delete_file.py) | 파일 삭제. 읽기 전용 권한은 `os.chmod()`로 해제 후 삭제. |
| [delete_directory.py](../examples/FileManager/delete_directory.py) | `shutil.rmtree()`로 디렉토리와 모든 내용물 재귀 삭제. |

## LogSys

타임스탬프 기반 자동 파일 구성의 구조화된 로깅.

| 파일 | 설명 |
|------|------|
| [make_logger.py](../examples/LogSys/LoggerManager/make_logger.py) | `LoggerManager.make_logger()`로 파일 핸들러와 콘솔 핸들러를 가진 이름 지정 로거를 생성합니다. `make_logger()` 자체는 성공 메시지를 반환하고, 실제 로거 인스턴스는 `get_logger()`로 가져옵니다. 로그 파일 경로는 `{resolved_base_dir}/{second_log_dir}/{timestamp}_log/{logger_name}.log` 형식입니다. |
| [get_logger.py](../examples/LogSys/LoggerManager/get_logger.py) | `LoggerManager.get_logger()`로 이름으로 기존 로거 조회. 존재하지 않으면 `Result(False, ...)` 반환. |
| [stop_stream_handlers.py](../examples/LogSys/LoggerManager/stop_stream_handlers.py) | 런타임에 로거의 콘솔(스트림) 핸들러 제거 — 이후 파일에만 기록. |
| [log_message.py](../examples/LogSys/Log/log_message.py) | `Log.log_message(level, message)`로 구조화된 로그 전송. level은 문자열(`"INFO"`, `"DEBUG"`) 또는 정수(`10`, `20`). |
| [get_instance.py](../examples/LogSys/SimpleSetting/get_instance.py) | `SimpleSetting`으로 `LoggerManager`, `Log`, `logging.Logger`를 한 번에 설정합니다. `get_instance()`로 튜플을 반환합니다. |

## ExceptionTracker

시스템 정보, 소스 위치, 마스킹을 포함한 종합 예외 추적.

| 파일 | 설명 |
|------|------|
| [get_exception_location.py](../examples/Exception/get_exception_location.py) | 예외가 발생한 파일, 줄 번호, 함수명 추출. `"'file.py', line 42, in function_name"` 형식 문자열 반환. |
| [get_exception_info.py](../examples/Exception/get_exception_info.py) | 오류 타입/메시지, 소스 위치, 원본 위치, 타임스탬프, 트레이스백, 입력 컨텍스트, 시스템 정보를 포함한 상세한 오류 정보 딕셔너리를 생성합니다. `mask_tuple`로 민감한 필드를 숨길 수 있습니다. |
| [get_exception_return.py](../examples/Exception/get_exception_return.py) | 잡힌 예외에서 표준화된 `Result(False, error_message, location, error_info_dict)` 생성. 내부적으로 `get_exception_info()` 호출. |
| [get_error_code.py](../examples/Exception/get_error_code.py) | 예외 타입을 사용자 정의 에러 코드로 매핑. `{ValueError: 1001, KeyError: 1002}` 같은 dict를 전달하면 매칭 코드 반환. |
| [ExceptionTrackerDecorator.py](../examples/Exception/ExceptionTrackerDecorator.py) | `@ExceptionTrackerDecorator()` — 함수의 예외를 잡아 `Result(False, ...)`로 반환. 성공 시 반환값 그대로 통과. `mask_tuple` 지원, `__name__`/`__doc__` 보존. |

## Utils

해싱, 경로 작업, 데이터 조작을 위한 유틸리티 함수.

| 파일 | 설명 |
|------|------|
| [hashing.py](../examples/Utils/Utils/hashing.py) | `md5`, `sha1`, `sha256`(기본), `sha512`로 문자열 해싱. hex digest 반환. 참고: 해싱은 단방향 연산이며 암호화가 아님. |
| [pbkdf2_hmac.py](../examples/Utils/Utils/pbkdf2_hmac.py) | 랜덤 salt로 PBKDF2-HMAC 패스워드 해시 생성 후 검증. `pbkdf2_hmac()` (생성)과 `verify_pbkdf2_hmac()` (검증) 시연. |
| [str_to_path.py](../examples/Utils/Utils/str_to_path.py) | 문자열을 `pathlib.Path` 객체로 변환하여 `Result`에 래핑. |
| [insert_at_intervals.py](../examples/Utils/Utils/insert_at_intervals.py) | 리스트나 문자열에 일정 간격으로 요소 삽입. `at_start=True`는 시작부터, `False`는 끝부터 카운트. |
| [find_keys_by_value.py](../examples/Utils/Utils/find_keys_by_value.py) | 비교 조건(`eq`, `ne`, `gt`, `ge`, `lt`, `le`)을 만족하는 딕셔너리 키 검색. `nested=True`로 중첩 dict 탐색, 출력 형식(`flat`, `forest`, `path`) 설정 가능. |

## GlobalVars

공유 메모리 IPC를 지원하는 스레드 안전 전역 변수 관리.

| 파일 | 설명 |
|------|------|
| [basic_usage.py](../examples/Utils/GlobalVars/basic_usage.py) | 핵심 작업: `set()`, `get()`, `delete()`, `clear()`, `exists()`, `list_vars()`. 모두 `Result` 반환. `set()`은 키 존재 시 `overwrite=True` 없으면 `KeyError`. |
| [attribute_and_call.py](../examples/Utils/GlobalVars/attribute_and_call.py) | 대체 접근 문법: `gv.name = "hello"` (속성)과 `gv("name", "hello")` (호출). 내부적으로 `set()`/`get()` 매핑. |
| [lock_and_context.py](../examples/Utils/GlobalVars/lock_and_context.py) | 내장 `RLock`(`gv.lock()`) 또는 컨텍스트 매니저(`with gv:`)를 이용한 스레드 안전 작업. |
| [shared_memory.py](../examples/Utils/GlobalVars/shared_memory.py) | 공유 메모리 IPC의 전체 흐름을 보여줍니다. `shm_gen()`으로 블록을 만들고(선택적으로 잠금 객체 포함), `shm_sync()`로 변수를 공유 메모리에 기록한 뒤(기본 JSON), `shm_update()`로 다시 읽고, `shm_connect()`로 다른 프로세스에서 연결하며, `shm_close()`로 정리합니다. 공유 메모리를 생성한 프로세스는 `shm_close(name)`으로 블록을 해제하고, 비소유자는 `shm_close(name, close_only=True)`로 핸들만 닫습니다. |

## DecoratorUtils

| 파일 | 설명 |
|------|------|
| [count_runtime.py](../examples/Utils/DecoratorUtils/count_runtime.py) | `@DecoratorUtils.count_runtime()` 데코레이터로 함수 실행 시간을 측정해 출력합니다. `functools.wraps`를 사용해 `__name__`과 `__doc__`를 보존합니다. |
