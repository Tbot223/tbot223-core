# Contract Docs

> docstring 계약 문서를 사람용 기준서와 LLM용 작업 지시서로 분리한 문서 트리다.

## 구조

- [FOR_HUMAN/DOCSTRING_CONTRACT.md](FOR_HUMAN/DOCSTRING_CONTRACT.md): 사람이 읽는 기준서다. 규약의 의도, 섹션 구성, 표현 규칙, 예시를 담는다.
- [FOR_LLM/DOCSTRING_CONTRACT.md](FOR_LLM/DOCSTRING_CONTRACT.md): LLM이 바로 작업 지시로 읽을 수 있게 압축한 실행 문서다. 특히 `Constraint` 추출과 실행 가능한 `Example` 작성 규칙을 직접 다룬다.

## 권장 사용 방식

- 사람이 기준을 확인할 때는 `FOR_HUMAN` 문서를 본다.
- AI에게 docstring 작업을 맡길 때는 먼저 `FOR_HUMAN` 문서를 읽게 하고, 그 다음 `FOR_LLM` 문서를 작업 지시서로 준다.
- 사람이 AI 결과를 검토할 때는 `FOR_HUMAN` 문서를 기준으로 보고, AI가 과잉 추론하지 않았는지는 `FOR_LLM`의 추출 규칙으로 역검증한다.

## 경로 정책

- 기존 경로 [../DOCSTRING_CONTRACT.md](../DOCSTRING_CONTRACT.md)는 호환성용 안내 문서로 유지한다.
- 실제 정본은 [FOR_HUMAN/DOCSTRING_CONTRACT.md](FOR_HUMAN/DOCSTRING_CONTRACT.md)다.
- AI용 동반 문서는 [FOR_LLM/DOCSTRING_CONTRACT.md](FOR_LLM/DOCSTRING_CONTRACT.md)다.
