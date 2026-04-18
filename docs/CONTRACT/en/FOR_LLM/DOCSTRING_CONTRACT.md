[한국어 (Korean)](../../ko/FOR_LLM/DOCSTRING_CONTRACT.md)

> Contract revision: 2026-04-19.

# Docstring Contract for LLM

> 이 문서는 사람이 읽는 계약서가 아니라, LLM이 docstring 생성 작업을 수행할 때 직접 따라야 하는 실행 지시서다.

## 먼저 할 일

이 문서를 읽기 전에 반드시 [../FOR_HUMAN/DOCSTRING_CONTRACT.md](../FOR_HUMAN/DOCSTRING_CONTRACT.md)를 먼저 읽는다.

- `FOR_HUMAN` 문서는 규약의 정본이다.
- 이 문서는 정본을 요약 대체하지 않는다.
- 이 문서의 역할은 정본을 읽은 뒤, 실제 생성 작업에서 무엇을 우선 적용해야 하는지 보조하는 것이다.

## 목표

- 현재 코드의 런타임 동작을 우선으로 docstring을 작성한다.
- 형식과 섹션 구조는 사람용 계약서 [../FOR_HUMAN/DOCSTRING_CONTRACT.md](../FOR_HUMAN/DOCSTRING_CONTRACT.md)를 따른다.
- `Constraint`는 코드의 검증 로직에서만 추출한다.
- `Example`은 실제로 실행 가능한 최소 예제로 작성한다.

## 읽기 절차

1. 먼저 [../FOR_HUMAN/DOCSTRING_CONTRACT.md](../FOR_HUMAN/DOCSTRING_CONTRACT.md)를 끝까지 읽는다.
2. 섹션 구조, 표현 규칙, 예시 형식을 이해한다.
3. 그 다음 이 문서를 읽고, 실제 코드에서 무엇을 추출해야 하는지 확인한다.
4. 작성 중 충돌이 생기면 사람용 정본이 우선이다.

## 우선순위

1. 코드의 실제 동작.
2. 현재 함수 시그니처와 반환 방식.
3. 사람용 정본 계약서의 섹션 구조와 표현 규칙.
4. 이 문서의 추출 규칙과 체크리스트.
5. 문체의 완성도와 장식.

형식보다 런타임 진실이 우선이다. 코드가 아직 5.0.0 개발 단계라면, 섹션을 억지로 채우는 것보다 실제 동작만 정확히 적는 편이 낫다.

## 작업 절차

1. 함수 시그니처를 읽는다.
2. 함수 본문에서 입력 검증, 가드 절, 실패 반환, 예외 발생 지점을 찾는다.
3. 해당 근거를 바탕으로 `Arguments`, `Callable Signature`, `Enum`, `Constraint`, `Returns`, `Note`, `Warning`, `Example`을 필요한 만큼만 작성한다.
4. 근거가 없는 섹션은 생략한다. 단, `Arguments`와 `Returns`는 항상 넣는다.
5. `Example`은 실제 import, 실제 함수명, 실제 인자 형태를 사용한다.

## Constraint 추출 규칙

### 핵심 원칙

- `Constraint`는 코드에 있는 검증 로직만 반영한다.
- 주석, 의도, 미래 계획, TODO는 `Constraint` 근거가 아니다.
- fallback이나 자동 보정은 거절 조건이 아니므로 보통 `Note`로 간다.
- 여러 조건이 결합돼 있으면 정형 패턴으로 쪼개거나, 조건 관계가 중요하면 그대로 유지한다.
- `raise`뿐 아니라 `return Result(False, ...)` 같은 실패 경로도 제약 근거로 본다.

### 근거로 인정할 코드 패턴

- `if not isinstance(...)`
- `if value is None`
- `if len(data) == 0`
- `if workers > len(data) and not override`
- `if chunk_size is not None and chunk_size < 0`
- `raise ValueError(...)`, `raise TypeError(...)`, `raise KeyError(...)`
- `return Result(False, ...)` 또는 이에 준하는 실패 반환

### 정형 패턴 매핑 예시

| 코드 형태 | docstring 패턴 |
| --- | --- |
| `if not isinstance(data, list) or len(data) == 0:` | `data` MUST be a non-empty `list`. |
| `if workers > len(data) and not override:` | `workers` MUST be `<= len(data)` unless `override` is `True`. |
| `if chunk_size is not None and chunk_size < 0:` | If `chunk_size` is not `None`, `chunk_size` MUST be `>= 0`. |
| `if code < 0 or code > 255:` | `code` MUST be `>= 0` and `<= 255`. |

### 금지 사항

- 코드에 없는 제약을 상식으로 보충하지 않는다.
- 미래에 필요해 보이는 제약을 미리 적지 않는다.
- 하나의 if 문을 보고 타입, 범위, 의미 제약을 동시에 과장해서 쓰지 않는다.
- 내부 구현이 자동 보정하는 동작을 실패 제약처럼 쓰지 않는다.

## Example 작성 규칙

- 실제 import 경로와 실제 클래스명을 사용한다.
- 예제 안의 함수나 데이터는 코드 블록 안에서 직접 정의해서 바로 실행 가능해야 한다.
- `func1`, `val1` 같은 미정의 placeholder는 금지한다.
- 부작용이 큰 함수는 최소 호출 예제만 보여주고, 위험성은 `Warning`에 적는다.
- 내부 helper라도 실행 가능한 최소 맥락을 만들 수 있으면 그렇게 한다.

## 섹션별 체크리스트

### Arguments

- 시그니처에 있는 인자만 적는다.
- 기본값이 있으면 ``Default: `value`.`` 형태를 유지한다.

### Callable Signature

- 콜러블이 핵심 인자일 때만 넣는다.
- `Callable[..., Any]`처럼 뭉개지지 말고 실제 호출 형태를 설명할 수 있으면 더 구체적으로 쓴다.

### Enum

- 선택지가 실제로 제한될 때만 넣는다.
- 단순 `Optional[int]` 같은 타입 표기만으로 Enum을 만들지 않는다.

### Constraint

- 코드 근거가 있는 검증만 적는다.
- 머신 파싱 가능한 정형 문장으로 쓴다.
- 코드에 없는 검증은 한 줄도 추가하지 않는다.

### Returns

- 현재 함수의 실제 반환 타입을 적는다.
- `Result`를 반환하면 `data`에 무엇이 담기는지도 현재 코드 기준으로 적는다.

### Note

- fallback, 자동 계산, lazy loading, 캐시 동작 같은 보충 정보를 적는다.
- 입력 거절 조건을 `Note`에 숨기지 않는다.

### Warning

- 비정상 종료, 프로세스 교체, 보안 리스크, pickling 제약, side effect가 있을 때만 적는다.

### Example

- 바로 실행 가능한지 다시 본다.
- import가 빠졌는지, 예제 내 함수 정의가 빠졌는지, 존재하지 않는 인자를 쓰지 않았는지 점검한다.

## 출력 전에 확인할 것

- 사람이 준 코드와 시그니처를 바꾸지 않았는가.
- `Constraint`가 실제 if 문, raise, 실패 반환에서만 나왔는가.
- `Example`이 placeholder 없이 실행 가능한가.
- `Returns`가 현재 구현과 맞는가.
- 형식이 부족하더라도 허구의 내용을 채우지 않았는가.

## 붙여넣기용 프롬프트

```text
먼저 docs/CONTRACT/en/FOR_HUMAN/DOCSTRING_CONTRACT.md를 읽고 규약을 익힌 뒤,
docs/CONTRACT/en/FOR_LLM/DOCSTRING_CONTRACT.md를 작업 지시서로 사용해서 방금 준 코드의 docstring을 작성해줘.
특히 Constraint는 코드의 if문, raise, 실패 반환 로직을 분석해서 정형 패턴으로 누락 없이 작성하고,
코드에 없는 제약은 절대 추가하지 마.
Example은 실제 import와 실제 함수명을 사용해서 바로 실행 가능한 형태로 작성해.
```
