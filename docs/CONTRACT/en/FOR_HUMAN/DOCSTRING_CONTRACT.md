[한국어 (Korean)](../../ko/FOR_HUMAN/DOCSTRING_CONTRACT.md)

> This document is based on v4.0.0.

# Docstring Contract

> tbot223-core 프로젝트의 Markdown 기반 docstring 양식 계약.
> 모든 public/internal 메서드에 동일하게 적용한다.

---

## 1. 전체 구조

모든 docstring은 **한 줄 요약**으로 시작하며, 이후 섹션은 `###` 헤더를 사용한다.

```
"""
한 줄 요약.

### Arguments
...
### Returns
...
### Example
...
"""
```

---

## 2. 섹션 목록과 적용 조건

| 섹션 | 필수 여부 | 적용 조건 |
|------|-----------|-----------|
| **한 줄 요약** | **항상** | 모든 docstring의 첫 줄. |
| **Arguments** | **항상** | 인자가 없으면 `None`으로 표기. |
| **Callable Signature** | 조건부 | 콜러블 / 콜백 / 함수 리스트 / 프로토콜이 핵심 인자일 때. |
| **Enum** | 조건부 | 선택지가 중요한 인자가 있을 때 (`str` 리터럴, `type` 집합 등). |
| **Constraint** | 조건부 | 인자 간 상호조건, 수식, 범위 제약이 코드에 존재할 때. 없는 제약을 만들지 않는다. |
| **Returns** | **항상** | 반환 타입 + 설명. |
| **Note** | 선택 | 보충 설명이 필요할 때. |
| **Warning** | 선택 | 주의 사항이 필요할 때. |
| **Example** | **가능하면 항상** | 최소 1개, `>>>` 형식. |

---

## 3. 섹션 순서

### 기본형 (단순 메서드)

```
Arguments → Returns → Example
```

### 확장형 (복잡한 메서드)

```
Arguments → Callable Signature → Enum → Constraint → Returns → Note → Warning → Example
```

### 확장형 — 위험성 강조 변형

Warning을 먼저 읽어야 하는 경우 Note와 Warning의 순서를 바꾼다.

```
Arguments → Callable Signature → Enum → Constraint → Returns → Warning → Note → Example
```

---

## 4. 표현 표준 (Expression Standard)

모든 섹션에서 아래 표현 규칙을 통일한다.

### 4.0.1 문장 종결

- 모든 Description, Note, Warning 문장은 **마침표(`.`)** 로 끝낸다.
- 한 줄 요약도 마침표로 끝낸다.

### 4.0.2 기본값 표기

```
Default: `value`.
```

- `Default is ...` 가 아니라 `Default: \`value\`.` 로 통일한다.
- `None`, `True`, `False`, 숫자, 문자열 모두 백틱으로 감싼다.

### 4.0.3 타입 표기

- 모든 Type 칼럼은 `typing` 모듈 표기를 따른다: `Optional[int]`, `Union[str, Path]`, `List[str]`.
- 제네릭 내부 파라미터까지 명시한다: `List[Tuple[Callable[..., Any], Dict[str, Any]]]`.
- 단일 타입도 백틱으로 감싼다: `str`, `int`, `bool`.

### 4.0.4 인자 참조

- docstring 내에서 인자를 참조할 때 항상 백틱으로 감싼다: `workers`, `timeout`.
- 클래스/함수 참조도 백틱: `ThreadPoolExecutor`, `Result`.

### 4.0.5 값 참조

- 리터럴 값은 항상 백틱: `True`, `False`, `None`, `0`, `'thread'`.
- 문자열 리터럴은 작은따옴표를 백틱 안에 포함: `'thread'`, `'process'`.

### 4.0.6 연산자/조건 표기

- 수학 연산자는 백틱으로 감싼다: `> 0`, `>= 0`, `<= 255`.
- "이상/이하" 같은 자연어 대신 연산자를 사용한다.

---

## 5. 각 섹션의 양식

### 5.1 한 줄 요약

```python
"""
Execute tasks concurrently with `ThreadPoolExecutor`.
```

- 영어, 동사 원형으로 시작, 간결하게, 마침표로 끝낸다.
- 주요 클래스/함수를 백틱으로 감싼다.
- 두 번째 줄은 빈 줄로 분리한다.

### 5.2 Tag 범례

클래스 `__init__`의 docstring 상단에만 한 번 기재한다.

```
- **(R)** = Required argument
- **(O)** = Optional argument (has a default value)
- **(D)** = Dependency Injection (advanced usage)
```

### 5.3 Arguments

MD 테이블 형식으로 작성한다.

```markdown
### Arguments
| Tag | Name | Type | Description |
|-----|------|------|-------------|
| **(R)** | `name` | `str` | User name. |
| **(O)** | `count` | `int` | Number of items. Default: `10`. |
| **(D)** | `manager` | `Optional[Manager]` | Manager instance. Default: built-in `Manager`. |
```

**Tag 의미:**

- **(R)** — Required. 기본값이 없는 필수 인자.
- **(O)** — Optional. 기본값이 있는 선택 인자. Description 끝에 `Default: \`value\`.`을 명시한다.
- **(D)** — Dependency Injection. 테스트 / 확장을 위한 주입 인자.

**인자가 없을 때:**

```markdown
### Arguments
None
```

### 5.4 Callable Signature

콜러블 인자의 정확한 시그니처를 blockquote로 기술한다.

```markdown
### Callable Signature
> `param_name` element: `Tuple[Callable[..., Any], Dict[str, Any]]`
> - `Callable[..., Any]` — Any function accepting keyword arguments.
> - `Dict[str, Any]` — Keyword arguments passed via `func(**kwargs)`.
```

**적용 조건:** `Callable`, 함수 리스트, 콜백, 프로토콜이 인자의 핵심일 때만.

**표현 규칙:**

- 첫 줄에 파라미터명과 전체 타입을 명시한다.
- 하위 bullet에서 각 타입 요소를 em dash (`—`)로 설명한다.
- 중첩 Callable은 `(param1: Type, param2: Type) -> ReturnType` 형식으로 풀어 쓴다.

### 5.5 Enum

선택지가 제한된 인자를 blockquote + 테이블로 명시한다.
**반드시 값의 타입을 `type:` 행으로 선언한다.**

```markdown
### Enum
> `param_name` — type: `str`
> | Value | Description |
> |-------|-------------|
> | `'thread'` | Uses `ThreadPoolExecutor`. |
> | `'process'` | Uses `ProcessPoolExecutor`. |
```

**복수 인자의 Enum:**

```markdown
### Enum
> `param_a` — type: `str`
> | Value | Description |
> |-------|-------------|
> | `'x'` | Description. |
> | `'y'` | Description. |
>
> `param_b` — type: `int`
> | Value | Description |
> |-------|-------------|
> | `0` | Auto mode. |
> | `1` | Manual mode. |
```

**type 집합 Enum (`type` 자체가 값인 경우):**

```markdown
### Enum
> `input_type` — type: `type`
> | Value | Description |
> |-------|-------------|
> | `str` | String input (no conversion). |
> | `int` | Integer conversion via `int()`. |
> | `float` | Float conversion via `float()`. |
> | `bool` | Boolean conversion (see **Note**). |
```

**적용 조건:** `str` 리터럴 집합, `type` 집합, 정수 모드 플래그, `None`/값 분기 등 선택지가 중요한 인자.

### 5.6 Constraint

인자의 유효성 제약을 blockquote + bullet list로 기술한다.
**문장은 머신 파싱이 가능한 정형 패턴을 따른다.**

#### 정형 패턴 (Machine-Parseable Patterns)

| Pattern | Template | Example |
|---------|----------|---------|
| **TYPE** | `` `{param}` MUST be `{type}`. `` | `` `data` MUST be `list`. `` |
| **RANGE** | `` `{param}` MUST be `{op} {value}`. `` | `` `timeout` MUST be `> 0.1`. `` |
| **NON-EMPTY** | `` `{param}` MUST be a non-empty `{type}`. `` | `` `data` MUST be a non-empty `list`. `` |
| **ELEMENT** | `` Each element of `{param}` MUST be `{shape}`. `` | `` Each element of `data` MUST be `Tuple[Callable, Dict]`. `` |
| **CONDITION** | `` `{paramA}` MUST be `{op} {paramB}` unless `{guard}` is `{value}`. `` | `` `workers` MUST be `<= len(data)` unless `override` is `True`. `` |
| **IF-THEN** | `` If `{param}` is `{value}`, `{target}` MUST be `{constraint}`. `` | `` If `chunk_size` is not `None`, `chunk_size` MUST be `>= 0`. `` |
| **MUTUAL** | `` `{paramA}` and `{paramB}` MUST NOT both be `{value}`. `` | `` `a` and `b` MUST NOT both be `None`. `` |

```markdown
### Constraint
> - `data` MUST be a non-empty `list`.
> - Each element of `data` MUST be `Tuple[Callable, Dict]`.
> - `workers` MUST be `> 0`.
> - `workers` MUST be `<= len(data)` unless `override` is `True`.
> - `timeout` MUST be `> 0.1`.
> - If `chunk_size` is not `None`, `chunk_size` MUST be `>= 0`.
```

**적용 조건:** 코드에 실제 유효성 검증이 존재할 때만. 없는 제약을 만들지 않는다.
**핵심:** `MUST be`, `MUST NOT be` 동사 구문으로 통일한다. `should`, `can`, `may` 사용 금지.

### 5.7 Returns

```markdown
### Returns
`Result` — Contains the validated value in `data`.
```

- 타입을 백틱으로 감싼다.
- em dash (`—`) 뒤에 간결한 설명을 붙인다.
- 복합 반환: `` `Tuple[bool, Optional[str]]` — `(is_valid, error_message)`. ``

### 5.8 Note

보충 설명을 blockquote로 작성한다.

```markdown
### Note
> Worker count defaults to `os.cpu_count()` when `workers` is `None`.
```

### 5.9 Warning

주의 사항을 blockquote로 작성한다.

```markdown
### Warning
> This method does **not** return under normal circumstances.
```

보안 관련 주의 사항이 있을 때는 Warning 안에서 `⚠️ **Security:**` 블록으로 시각 구분한다.

```markdown
### Warning
> ⚠️ **Security:**
> - Input is not sanitized. Do not pass untrusted user input directly.
> - Pickle deserialization can execute arbitrary code.
>
> General warnings here.
```

- Security 블록은 Warning 내부 **최상단**에 배치한다.
- 일반 Warning과 빈 줄(`>`)로 구분한다.
- 보안 이슈가 없으면 Security 블록을 생략한다.

### 5.10 Example

`>>>` 형식의 코드 블록을 사용한다.

```markdown
### Example
>>> result = app_core.thread_pool_executor(data, workers=4, timeout=10)
>>> for res in result.data:
>>>     print(res.success, res.data)
```

- 최소 1개의 예시를 포함한다.
- 실제 사용 패턴을 반영한다.
- 성공 / 실패 양 경로를 보여주면 좋다.

---

## 6. 규칙 요약

1. **한 줄 요약, Arguments, Returns**는 항상 포함한다.
2. **Example**은 가능하면 항상 포함한다.
3. **Callable Signature, Enum, Constraint**는 해당 조건을 만족할 때만 추가한다.
4. **Note, Warning**은 선택이다.
5. 섹션 순서를 지킨다. 위험성이 강한 경우에만 Warning ↔ Note 순서를 바꾼다.
6. Tag 범례는 클래스 `__init__`에만 한 번 기재한다.
7. 기존 설명 내용을 변경하지 않고 양식만 적용한다.
8. 기본값은 `Default: \`value\`.` 형식으로 통일한다.
9. Constraint 문장은 `MUST be` / `MUST NOT be` 패턴으로 통일한다.
10. Enum 선언 시 `type:` 행으로 값 타입을 반드시 명시한다.

---

## 7. 전체 예시 Docstring

### 7.1 기본형 예시

```python
def clear_console(self) -> Result:
    """
    Clear the current console screen.

    ### Arguments
    None

    ### Returns
    `Result` — Indicates whether the console-clear command succeeded.

    ### Example
    >>> result = app_core.clear_console()
    >>> print(result.success)  # True
    """
```

### 7.2 확장형 예시

```python
def process_pool_executor(
    self,
    data: List[Tuple[Callable[..., Any], Dict]],
    workers: Optional[int] = None,
    override: bool = False,
    timeout: float = None,
    chunk_size: Optional[int] = None,
) -> Result:
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
    > When `chunk_size` is `0`, the chunk size is auto-computed as `ceil(len(data) / workers)`.
    > When `chunk_size` is `None`, the full task list is submitted to a single executor.

    ### Warning
    > Functions passed to the process pool MUST be picklable. Lambda functions and closures will fail.

    ### Example
    >>> def add(a, b): return a + b
    >>> data = [(add, {'a': 1, 'b': 2}), (add, {'a': 3, 'b': 4})]
    >>> result = app_core.process_pool_executor(data, workers=2, timeout=10)
    >>> if result.success:
    >>>     for res in result.data:
    >>>         print(res.data)  # 3, 7
    """
```

### 7.3 위험성 강조 변형 예시

```python
def exit_application(self, code: int = 0, pause: bool = False) -> Result:
    """
    Terminate the current process with the specified exit code.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(O)** | `code` | `int` | Exit code for the OS. Default: `0`. |
    | **(O)** | `pause` | `bool` | Wait for user input before exiting. Default: `False`. |

    ### Constraint
    > - `code` MUST be `>= 0` and `<= 255`.

    ### Returns
    `Result` — Returned only if the exit attempt fails.

    ### Warning
    > This method does **not** return under normal circumstances.
    > Any code after this call will not execute.

    ### Note
    > Calls `sys.exit(code)` internally. A `SystemExit` exception will be raised.

    ### Example
    >>> app_core.exit_application(0)
    """
```

### 7.4 Callable Signature 독립 예시

```python
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

    ### Warning
    > Intended for `get_text_by_lang()` only. Do not apply to other methods.

    ### Example
    >>> @AppCore.__lang_cache_management__
    >>> def get_text_by_lang(self, key: str, lang: str) -> Result:
    >>>     ...
    """
```
