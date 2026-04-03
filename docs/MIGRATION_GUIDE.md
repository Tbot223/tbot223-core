# Migration Guide

[한국어 (Korean)](MIGRATION_GUIDE.ko.md)

This guide now covers the upgrade path to 4.x for both older 2.x codebases and 3.x codebases. If you are upgrading from 3.x, start with the `3.1.1 -> 4.0.0` section below. If you are upgrading from 2.x, read that section and the earlier `2.x -> 3.0.0` major-upgrade section further down.

<details>
<summary>Table of Contents</summary>

- [3.1.1 to 4.0.0](#upgrade-3-1-1-to-4-0-0)
- [Quick Checklist](#current-quick-checklist)
- [1. `GlobalVars` missing attribute access](#gv-missing-attr)
- [2. `GlobalVars` call syntax and `None`](#gv-none-call)
- [3. Shared-memory ownership and size validation](#shared-memory-size)
- [4. `process_pool_executor(chunk_size=None)` semantics](#process-pool-semantics)
- [5. `FileManager.exist()` -> `exists()`](#filemanager-exists)
- [6. `LoggerManager.make_logger(time=...)` -> `timestamp=`](#logger-timestamp)
- [7. `Result.expect(msg)`](#result-expect)
- [8. Documentation and path layout](#docs-layout)
- [Earlier Major Upgrade: 2.x to 3.0.0](#legacy-2x-to-3-0-0)
- [Import System Changes](#import-system-changes)
- [Exception API Changes](#exception-api-changes)
- [Result Object Changes](#result-object-changes)
- [2.x to 3.0.0 Checklist](#legacy-checklist)
- [Compatibility Notes](#compatibility-notes)
</details>

<a id="upgrade-3-1-1-to-4-0-0"></a>
## Migrating from 3.1.1 to 4.0.0

Version 4.0.0 collects the behavior and documentation changes that accumulated after 3.1.1. Most code will continue to work, but a few `GlobalVars` behaviors and `process_pool_executor()` semantics changed in ways that can break existing callers.

<a id="current-quick-checklist"></a>
### Quick Checklist

- Replace sentinel-string checks for missing `GlobalVars` attributes
- Replace `gv("key", None)` reads with `gv("key")`
- Review shared-memory cleanup code for owner vs non-owner processes
- If you relied on implicit process-pool batching, pass `chunk_size=0` or a positive integer
- Rename `exist()` to `exists()` in maintained code
- Rename `make_logger(time=...)` to `make_logger(timestamp=...)`
- Update bookmarks and doc links to the `docs/` paths

<a id="gv-missing-attr"></a>
### 1. `GlobalVars` missing attribute access

**Before (3.1.1):**
```python
gv = GlobalVars()
value = gv.missing_key
print(value)  # "Key does not exist."
```

**After (4.0.0):**
```python
gv = GlobalVars()
try:
    value = gv.missing_key
except AttributeError:
    value = None
```

**Action required:**

- If your code compared against the string `"Key does not exist."`, replace that check.
- Prefer `gv.get("missing_key")` or `gv.exists("missing_key")` when missing keys are expected.
- Use `try/except AttributeError` only when attribute-style access is intentional.

<a id="gv-none-call"></a>
### 2. `GlobalVars` call syntax and `None`

**Before (3.1.1):**

`None` was treated like an omitted value, so `gv("key", None)` could accidentally behave like a read.

```python
result = gv("key", None)  # could behave like gv("key")
```

**After (4.0.0):**

`None` is now treated as a real value and stored.

```python
gv("key", None, overwrite=True)  # stores None
result = gv("key")               # reads the value
```

**Action required:**

- Use `gv("key")` for reads.
- Only pass `None` when you intend to store `None`.
- Audit helper wrappers that forward optional values into `gv(...)`.

<a id="shared-memory-size"></a>
### 3. Shared-memory ownership and size validation

**Before (3.1.1):**

- `shm_close(name)` could unlink more aggressively, regardless of whether the current process originally created the block.
- `shm_gen(name, size)` could attach to an existing block without checking whether the existing size matched your new request.

**After (4.0.0):**

- Only the owner process unlinks the shared-memory block.
- Non-owner processes should usually call `shm_close(name, close_only=True)`.
- `shm_gen(name, size)` now fails if an existing block is smaller than the requested size.

**Action required:**

- Update parent/child cleanup code so workers use `close_only=True`.
- If you reuse stable shared-memory names across runs, make sure the requested `size` is compatible with the existing block.
- Treat `shm_gen()` attachment failures as configuration or lifecycle problems, not silent success.

<a id="process-pool-semantics"></a>
### 4. `process_pool_executor(chunk_size=None)` semantics

**Before (3.1.1):**

`chunk_size=None` triggered automatic chunk calculation based on task count and worker count.

```python
result = app.process_pool_executor(tasks, workers=4, timeout=5, chunk_size=None)
```

**After (4.0.0):**

`chunk_size=None` submits the full task list in one executor. Automatic chunking moved to `chunk_size=0`.

```python
result = app.process_pool_executor(tasks, workers=4, timeout=5, chunk_size=0)   # auto
result = app.process_pool_executor(tasks, workers=4, timeout=5, chunk_size=64)  # explicit
```

**Action required:**

- If you relied on the old implicit batching, pass `chunk_size=0` or a positive integer explicitly.
- Keep `chunk_size=None` only when you intentionally want a single full-list executor.

<a id="filemanager-exists"></a>
### 5. `FileManager.exist()` -> `exists()`

**Before (3.1.1):**
```python
result = fm.exist("config.json")
```

**After (4.0.0):**
```python
result = fm.exists("config.json")
```

`exist()` still works, but it is now a deprecated alias that forwards to `exists()`.

**Action required:**

- Update new and maintained code to use `exists()`.
- Treat `exist()` as compatibility-only and plan to remove it from downstream code.

<a id="logger-timestamp"></a>
### 6. `LoggerManager.make_logger(time=...)` -> `timestamp=`

**Before (3.1.1):**
```python
logger_manager.make_logger("app", time="custom_stamp")
```

**After (4.0.0):**
```python
logger_manager.make_logger("app", timestamp="custom_stamp")
```

`time=` still works, but it is now a deprecated alias.

**Action required:**

- Rename keyword arguments to `timestamp=`.
- Do not pass both `time=` and `timestamp=` in the same call.

<a id="result-expect"></a>
### 7. `Result.expect(msg)`

**Before (3.1.1):**
```python
value = result.expect()
```

**After (4.0.0):**
```python
value = result.expect("configuration is required")
```

The no-argument form still works. This is an additive change, not a breaking one.

**Action required:**

- No mandatory code changes.
- Prefer the new message argument when the caller needs a clearer failure reason at the unwrap site.

<a id="docs-layout"></a>
### 8. Documentation and path layout

**Before (3.1.1):**

- `MIGRATION_GUIDE.md`
- `RELEASE_NOTES.md`
- `examples/Examples.md`

**After (4.0.0):**

- `docs/MIGRATION_GUIDE.md`
- `docs/RELEASE_NOTES.md`
- `docs/Examples.md`

Root-level `README.md` and `README.ko.md` remain in place.

**Action required:**

- Update bookmarks, links, package docs references, and onboarding docs to the `docs/` paths.
- If you linked directly to the old root files from CI, badges, or external docs, update those URLs now.

<a id="legacy-2x-to-3-0-0"></a>
## Earlier Major Upgrade: 2.x to 3.0.0

Version 3.0.0 introduced significant changes to the import system and module structure. These notes are kept here for 2.x codebases that still need to cross 3.0.0 on the way to 4.x.

---

<a id="import-system-changes"></a>
### Import System Changes

#### Direct Class Imports

The most significant change is how you import and instantiate classes.

**Before (2.x):**
```python
from tbot223_core import AppCore, FileManager, LogSys
from tbot223_core.Utils import GlobalVars

# Double reference required
app = AppCore.AppCore()
fm = FileManager.FileManager()
logger_manager = LogSys.LoggerManager()
log = LogSys.Log()
gv = GlobalVars.GlobalVars()
```

**After (3.0.0):**
```python
from tbot223_core import AppCore, FileManager, LoggerManager, Log, GlobalVars

# Direct instantiation
app = AppCore()
fm = FileManager()
logger_manager = LoggerManager()
log = Log()
gv = GlobalVars()
```

#### Utils Subpackage

The `Utils.py` module has been split into a subpackage with separate files.

**Before (2.x):**
```python
from tbot223_core.Utils import GlobalVars, DecoratorUtils, Utils
```

**After (3.0.0):**
```python
# Option 1: Import from main package (recommended)
from tbot223_core import GlobalVars, DecoratorUtils, Utils

# Option 2: Import from subpackage
from tbot223_core.Utils.GlobalVars import GlobalVars
from tbot223_core.Utils.DecoratorUtils import DecoratorUtils
from tbot223_core.Utils.Utils import Utils
```

---

<a id="exception-api-changes"></a>
### Exception API Changes

#### `mask_tuple` Parameter

The `get_exception_info()` and `get_exception_return()` methods now use `mask_tuple` for masking sensitive information.

**Before (2.x):**
```python
tracker = ExceptionTracker()
info = tracker.get_exception_info(error, user_input=data, params=(args, kwargs))
```

**After (3.0.0):**
```python
tracker = ExceptionTracker()
# mask_tuple order: (user_input, params, traceback, computer_info)
info = tracker.get_exception_info(
    error,
    user_input=data,
    params=(args, kwargs),
    mask_tuple=(True, False, True, False)  # Masks user_input and traceback
)
```

---

<a id="result-object-changes"></a>
### Result Object Changes

#### `success` Field Type

The `success` field type changed from `bool` to `Optional[bool]`.

| Value | Meaning |
|-------|---------|
| `True` | Operation succeeded |
| `False` | Operation failed |
| `None` | Operation cancelled or not executed |

#### New Methods

Result objects now have convenience methods for unwrapping values:

```python
from tbot223_core import FileManager
from tbot223_core.Result import ResultUnwrapException

fm = FileManager()

# unwrap() - Raises exception if not successful
try:
    content = fm.read_file("example.txt").unwrap()
except ResultUnwrapException as e:
    print(f"Failed: {e.error}")

# expect() - Similar to unwrap(), but supports a custom failure message
content = fm.read_file("example.txt").expect("config file is required")

# unwrap_or() - Returns default if not successful
content = fm.read_file("missing.txt").unwrap_or("default content")
```

---

<a id="legacy-checklist"></a>
### 2.x to 3.0.0 Checklist

- [ ] Update all class imports to use direct instantiation
- [ ] Replace `LogSys.LoggerManager` with `LoggerManager`
- [ ] Replace `LogSys.Log` with `Log`
- [ ] Update `Utils` imports to use the new subpackage structure
- [ ] Add `mask_tuple` parameter if using exception masking
- [ ] Handle `None` value for `Result.success` if using async operations
- [ ] Consider using new `unwrap()`, `expect()`, `unwrap_or()` methods

---

<a id="compatibility-notes"></a>
### Compatibility Notes

- Python 3.10 - 3.14 supported
- All existing functionality is preserved
- Old import style `from tbot223_core.Utils.GlobalVars import GlobalVars` still works
