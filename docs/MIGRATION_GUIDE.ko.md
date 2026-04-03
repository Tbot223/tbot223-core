# 마이그레이션 가이드

[English](MIGRATION_GUIDE.md)

이 가이드는 이제 2.x 계열과 3.x 계열 모두에서 4.x로 올라가는 경로를 함께 다룹니다. 3.x에서 업그레이드한다면 아래 `3.1.1 -> 4.0.0` 섹션부터 보면 되고, 2.x에서 올라간다면 그 섹션과 아래쪽의 `2.x -> 3.0.0` 메이저 업그레이드 섹션을 함께 확인하는 편이 좋습니다.

<details>
<summary>목차</summary>

- [3.1.1에서 4.0.0으로 마이그레이션](#upgrade-3-1-1-to-4-0-0)
- [빠른 체크리스트](#current-quick-checklist)
- [1. `GlobalVars`의 없는 속성 접근](#gv-missing-attr)
- [2. `GlobalVars` 호출 문법과 `None`](#gv-none-call)
- [3. 공유 메모리 소유권과 크기 검증](#shared-memory-size)
- [4. `process_pool_executor(chunk_size=None)` 의미 변경](#process-pool-semantics)
- [5. `FileManager.exist()`에서 `exists()`로](#filemanager-exists)
- [6. `LoggerManager.make_logger(time=...)`에서 `timestamp=`로](#logger-timestamp)
- [7. `Result.expect(msg)`](#result-expect)
- [8. 문서 경로와 구조](#docs-layout)
- [이전 메이저 업그레이드: 2.x에서 3.0.0으로 마이그레이션](#legacy-2x-to-3-0-0)
- [임포트 시스템 변경](#import-system-changes)
- [Exception API 변경](#exception-api-changes)
- [Result 객체 변경](#result-object-changes)
- [2.x에서 3.0.0으로 가는 체크리스트](#legacy-checklist)
- [호환성 참고사항](#compatibility-notes)
</details>

<a id="upgrade-3-1-1-to-4-0-0"></a>
## 3.1.1에서 4.0.0으로 마이그레이션

버전 4.0.0은 3.1.1 이후 누적된 동작 변경과 문서 구조 변경을 한 번에 정리한 릴리스입니다. 대부분의 코드는 그대로 동작하지만, `GlobalVars` 일부 동작과 `process_pool_executor()`의 청킹 의미는 기존 호출자를 깨뜨릴 수 있으므로 먼저 점검하는 편이 좋습니다.

<a id="current-quick-checklist"></a>
### 빠른 체크리스트

- 없는 `GlobalVars` 속성 접근을 문자열로 비교하던 코드가 있는지 확인
- `gv("key", None)`를 조회 용도로 쓰던 코드를 `gv("key")`로 교체
- 공유 메모리 정리 코드에서 owner / non-owner 역할을 다시 확인
- 암묵적인 프로세스 풀 청킹에 의존했다면 `chunk_size=0` 또는 양의 정수를 명시
- 유지보수 중인 코드에서는 `exist()` 대신 `exists()` 사용
- `make_logger(time=...)`를 `make_logger(timestamp=...)`로 변경
- 문서 북마크와 내부 링크를 `docs/` 경로로 업데이트

<a id="gv-missing-attr"></a>
### 1. `GlobalVars`의 없는 속성 접근

**이전 (3.1.1):**
```python
gv = GlobalVars()
value = gv.missing_key
print(value)  # "Key does not exist."
```

**이후 (4.0.0):**
```python
gv = GlobalVars()
try:
    value = gv.missing_key
except AttributeError:
    value = None
```

**필요한 조치:**

- `"Key does not exist."` 문자열 비교에 의존하던 코드를 제거하세요.
- 없는 키가 정상 흐름의 일부라면 `gv.get("missing_key")` 또는 `gv.exists("missing_key")`를 사용하는 편이 안전합니다.
- 속성 문법을 유지해야 한다면 `try/except AttributeError`로 처리하세요.

<a id="gv-none-call"></a>
### 2. `GlobalVars` 호출 문법과 `None`

**이전 (3.1.1):**

`None`이 “값이 생략됨”처럼 취급되어, `gv("key", None)`이 의도치 않게 조회처럼 동작할 수 있었습니다.

```python
result = gv("key", None)  # gv("key")처럼 동작할 수 있었음
```

**이후 (4.0.0):**

이제 `None`은 실제 값으로 취급되어 그대로 저장됩니다.

```python
gv("key", None, overwrite=True)  # None 저장
result = gv("key")               # 조회
```

**필요한 조치:**

- 조회는 `gv("key")`를 사용하세요.
- `None`을 넘길 때는 정말 `None`을 저장하려는 의도인지 확인하세요.
- optional 값을 그대로 `gv(...)`에 전달하는 래퍼 함수나 헬퍼를 점검하세요.

<a id="shared-memory-size"></a>
### 3. 공유 메모리 소유권과 크기 검증

**이전 (3.1.1):**

- `shm_close(name)`가 현재 프로세스가 블록을 만든 주체인지와 관계없이 더 공격적으로 unlink할 수 있었습니다.
- `shm_gen(name, size)`가 기존 블록에 연결할 때, 그 블록의 크기가 새 요청과 맞는지 검증하지 않을 수 있었습니다.

**이후 (4.0.0):**

- owner 프로세스만 공유 메모리 블록을 unlink합니다.
- non-owner 프로세스는 보통 `shm_close(name, close_only=True)`를 사용해야 합니다.
- `shm_gen(name, size)`는 기존 블록이 요청한 크기보다 작으면 실패합니다.

**필요한 조치:**

- 부모/자식 프로세스 정리 코드를 다시 보고, worker 쪽은 `close_only=True`를 쓰도록 정리하세요.
- 실행 사이에 같은 공유 메모리 이름을 재사용한다면, 요청하는 `size`가 기존 블록과 호환되는지 확인하세요.
- `shm_gen()` attach 실패를 조용히 성공으로 넘기지 말고 설정/생명주기 문제로 처리하세요.

<a id="process-pool-semantics"></a>
### 4. `process_pool_executor(chunk_size=None)` 의미 변경

**이전 (3.1.1):**

`chunk_size=None`이면 태스크 수와 worker 수를 기준으로 자동 청킹이 수행되었습니다.

```python
result = app.process_pool_executor(tasks, workers=4, timeout=5, chunk_size=None)
```

**이후 (4.0.0):**

`chunk_size=None`은 전체 작업 목록을 하나의 executor에 그대로 제출합니다. 자동 청킹은 `chunk_size=0`으로 이동했습니다.

```python
result = app.process_pool_executor(tasks, workers=4, timeout=5, chunk_size=0)   # 자동 청킹
result = app.process_pool_executor(tasks, workers=4, timeout=5, chunk_size=64)  # 명시적 청킹
```

**필요한 조치:**

- 이전의 암묵적 배치 처리에 의존했다면 `chunk_size=0` 또는 양의 정수를 명시하세요.
- 전체 목록을 한 번에 처리하려는 경우에만 `chunk_size=None`을 유지하세요.

<a id="filemanager-exists"></a>
### 5. `FileManager.exist()`에서 `exists()`로

**이전 (3.1.1):**
```python
result = fm.exist("config.json")
```

**이후 (4.0.0):**
```python
result = fm.exists("config.json")
```

`exist()`는 여전히 동작하지만, 이제 `exists()`로 전달하는 deprecated alias입니다.

**필요한 조치:**

- 새 코드와 유지보수 중인 코드에서는 `exists()`를 사용하세요.
- `exist()`는 호환성 용도로만 생각하고, 다운스트림 코드에서는 점진적으로 제거하는 편이 좋습니다.

<a id="logger-timestamp"></a>
### 6. `LoggerManager.make_logger(time=...)`에서 `timestamp=`로

**이전 (3.1.1):**
```python
logger_manager.make_logger("app", time="custom_stamp")
```

**이후 (4.0.0):**
```python
logger_manager.make_logger("app", timestamp="custom_stamp")
```

`time=`은 여전히 동작하지만 deprecated alias입니다.

**필요한 조치:**

- 키워드 인자를 `timestamp=`로 바꾸세요.
- 같은 호출에서 `time=`과 `timestamp=`를 함께 넘기지 마세요.

<a id="result-expect"></a>
### 7. `Result.expect(msg)`

**이전 (3.1.1):**
```python
value = result.expect()
```

**이후 (4.0.0):**
```python
value = result.expect("configuration is required")
```

기존 무인자 호출도 계속 동작합니다. 이 항목은 breaking change가 아니라 확장입니다.

**필요한 조치:**

- 필수 변경은 없습니다.
- unwrap 시점에 더 명확한 실패 이유가 필요하다면 새 메시지 인자를 활용하세요.

<a id="docs-layout"></a>
### 8. 문서 경로와 구조

**이전 (3.1.1):**

- `MIGRATION_GUIDE.md`
- `RELEASE_NOTES.md`
- `examples/Examples.md`

**이후 (4.0.0):**

- `docs/MIGRATION_GUIDE.md`
- `docs/RELEASE_NOTES.md`
- `docs/Examples.md`

루트에는 `README.md`와 `README.ko.md`만 그대로 남습니다.

**필요한 조치:**

- 북마크, 내부 링크, 패키지 문서 링크, 온보딩 문서를 `docs/` 경로 기준으로 업데이트하세요.
- CI, 배지, 외부 문서에서 예전 루트 경로를 직접 링크하고 있다면 지금 함께 바꾸는 편이 안전합니다.

<a id="legacy-2x-to-3-0-0"></a>
## 이전 메이저 업그레이드: 2.x에서 3.0.0으로 마이그레이션

버전 3.0.0에서는 임포트 시스템과 모듈 구조에 중요한 변경사항이 도입되었습니다. 아래 메모는 2.x 코드베이스가 4.x로 올라가는 과정에서 3.0.0 구간도 함께 통과해야 할 때 참고할 수 있도록 남겨둔 내용입니다.

---

<a id="import-system-changes"></a>
### 임포트 시스템 변경

#### 클래스를 직접 임포트하기

가장 큰 변경점은 클래스를 임포트한 뒤 인스턴스화하는 방식입니다.

**이전 (2.x):**
```python
from tbot223_core import AppCore, FileManager, LogSys
from tbot223_core.Utils import GlobalVars

# 이중 참조 필요
app = AppCore.AppCore()
fm = FileManager.FileManager()
logger_manager = LogSys.LoggerManager()
log = LogSys.Log()
gv = GlobalVars.GlobalVars()
```

**이후 (3.0.0):**
```python
from tbot223_core import AppCore, FileManager, LoggerManager, Log, GlobalVars

# 직접 인스턴스화
app = AppCore()
fm = FileManager()
logger_manager = LoggerManager()
log = Log()
gv = GlobalVars()
```

#### Utils 서브패키지

`Utils.py` 모듈이 별도의 파일을 가진 서브패키지로 분리되었습니다.

**이전 (2.x):**
```python
from tbot223_core.Utils import GlobalVars, DecoratorUtils, Utils
```

**이후 (3.0.0):**
```python
# 옵션 1: 메인 패키지에서 import (권장)
from tbot223_core import GlobalVars, DecoratorUtils, Utils

# 옵션 2: 서브패키지에서 import
from tbot223_core.Utils.GlobalVars import GlobalVars
from tbot223_core.Utils.DecoratorUtils import DecoratorUtils
from tbot223_core.Utils.Utils import Utils
```

---

<a id="exception-api-changes"></a>
### Exception API 변경

#### `mask_tuple` 파라미터

`get_exception_info()`와 `get_exception_return()` 메서드는 이제 민감한 정보를 마스킹하기 위해 `mask_tuple`을 사용합니다.

**이전 (2.x):**
```python
tracker = ExceptionTracker()
info = tracker.get_exception_info(error, user_input=data, params=(args, kwargs))
```

**이후 (3.0.0):**
```python
tracker = ExceptionTracker()
# mask_tuple 순서: (user_input, params, traceback, computer_info)
info = tracker.get_exception_info(
    error,
    user_input=data,
    params=(args, kwargs),
    mask_tuple=(True, False, True, False)  # `user_input`과 `traceback` 마스킹
)
```

---

<a id="result-object-changes"></a>
### Result 객체 변경

#### `success` 필드 타입

`success` 필드 타입이 `bool`에서 `Optional[bool]`로 변경되었습니다.

| 값 | 의미 |
|-------|---------|
| `True` | 작업 성공 |
| `False` | 작업 실패 |
| `None` | 작업 취소됨 또는 실행되지 않음 |

#### 새로운 메서드

Result 객체에 값을 추출하기 위한 편의 메서드가 추가되었습니다:

```python
from tbot223_core import FileManager
from tbot223_core.Result import ResultUnwrapException

fm = FileManager()

# unwrap() - 성공이 아니면 예외 발생
try:
    content = fm.read_file("example.txt").unwrap()
except ResultUnwrapException as e:
    print(f"실패: {e.error}")

# expect() - unwrap()과 비슷하지만 커스텀 실패 메시지 사용 가능
content = fm.read_file("example.txt").expect("config file is required")

# unwrap_or() - 성공이 아니면 기본값 반환
content = fm.read_file("missing.txt").unwrap_or("기본 내용")
```

---

<a id="legacy-checklist"></a>
### 2.x에서 3.0.0으로 가는 체크리스트

- [ ] 모든 클래스 import를 직접 인스턴스화 방식으로 업데이트
- [ ] `LogSys.LoggerManager`를 `LoggerManager`로 교체
- [ ] `LogSys.Log`를 `Log`로 교체
- [ ] `Utils` import를 새로운 서브패키지 구조로 업데이트
- [ ] 예외 마스킹 사용 시 `mask_tuple` 파라미터 추가
- [ ] 비동기 작업 사용 시 `Result.success`의 `None` 값 처리
- [ ] 새로운 `unwrap()`, `expect()`, `unwrap_or()` 메서드 사용 고려

---

<a id="compatibility-notes"></a>
### 호환성 참고사항

- Python 3.10 - 3.14 지원
- 모든 기존 기능 유지
- 이전 import 스타일 `from tbot223_core.Utils.GlobalVars import GlobalVars`도 계속 작동
