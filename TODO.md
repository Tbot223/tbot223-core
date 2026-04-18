# Roadmap

## 5.0.0a1 — AppCore 분해

- [ ] Executor 모듈 분리 (`_check_executable`, `_resolve_worker_count`, `_generic_executor`, `_chunk_list`, `thread_pool_executor`, `process_pool_executor`)
- [ ] i18n 모듈 분리 (`__lang_cache_management__`, `get_text_by_lang`)
- [ ] CLI 모듈 분리 (`clear_console`, `safe_CLI_input`)
- [ ] Lifecycle 모듈 분리 (`exit_application`, `restart_application`)
- [ ] `ResultWrapper` 배치 결정 (독립 유틸 이동 또는 현위치 유지)

## 5.0.0a2 — GlobalVars 분리

- [ ] Config 계층 분리 (`_BASE_DIR`, `__is_logging_enabled__`, `__shm_cache_max_size__`, `SERIALIZERS`)
- [ ] State 계층 분리 (`__vars__`, `__lock__`, `__shm_name__`, `__shm_owner__`, `__shm_cache__`)
- [ ] SHM 관련 로직 그룹핑 (`shm_gen`, `shm_connect`, `shm_get`, `shm_sync`, `shm_update`, `shm_close`, `shm_cache_management`)

## 5.0.0a3 — 싱글톤 재조립

- [ ] 모듈-레벨 인스턴스 + 팩토리 패턴 적용
- [ ] 기존 `AppCore()` / `GlobalVars()` API 하위호환 유지

## 5.0.0a4 — 초기화 통일

- [ ] `DefaultInit.run()` 기반으로 전 모듈 초기화 통일 (로깅, 예외 추적, masking, `_log` 바인딩)
- [ ] 각 분해 모듈이 `DefaultInit`을 통해 초기화되도록 교체

## 5.0.0 — Core Decomposition (정식)

- [ ] 신규/변경 모듈 독스트링 계약(`docs/CONTRACT/ko/FOR_HUMAN/DOCSTRING_CONTRACT.md`) 적용
- [ ] LookupDict stub 유지 확인
- [ ] 알파 단계 잔여 이슈 정리

## 5.0.1 — Stabilization

- [ ] 분해/초기화 교체 과정에서 발생한 회귀 수정
- [ ] 독스트링 계약 검수 후 누락분 패치
- [ ] 최소 테스트 보정 (기존 테스트가 새 구조에서 통과하도록)

## 5.1.0 — LookupDict

- [ ] `Utils._lookup_dict` 기반 개선판 구현 (재귀 검색, return_mod, 비교 연산 확장)
- [ ] async 하위 패키지 기반 최소 도입 (필요 시)
- [ ] 해당 기능 테스트 작성

## 5.2.0 — Pythonic Subpackage

- [ ] 기존 API를 따르되 예외를 직접 raise하는 파이썬 철학 기반 모듈
- [ ] 별도 패키지 분리 여부 최종 결정
- [ ] 해당 기능 테스트 작성

## 5.2.1 — Test Overhaul

- [ ] 레거시 테스트 정리 및 커버리지 보강
- [ ] 전체 테스트 스위트 구조 재정비
