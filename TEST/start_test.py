# external Modules
import subprocess
import sys
from pathlib import Path

# internal Modules
from SRC import AppCore_test, Exception_test, LogSys_test, Utils_test, FileManager_test, Result_test
from tbot223_core import FileManager

# ============================================
# Constants
# ============================================
_SRC_DIR = Path(__file__).resolve().parent / "SRC"
_LOG_DIR = _SRC_DIR / "logs"

_MODULE_MAP = {
    "appcore":   AppCore_test,
    "exception": Exception_test,
    "logsys":    LogSys_test,
    "utils":     Utils_test,
    "filemanager": FileManager_test,
    "result":    Result_test,
}

# ============================================
# Helpers
# ============================================

def _prompt(msg: str, valid: list[str]) -> str:
    """Prompt the user until a valid response is given."""
    while True:
        resp = input(msg).strip().lower()
        if resp in valid:
            return resp
        print(f"  Invalid input. Choose one of: {', '.join(valid)}")


def _run_pytest(targets: list[str], *, include_performance: bool = False,
                duration: bool = False, coverage: bool = False,
                verbose: bool = True) -> int:
    """
    Build and execute a pytest command in a subprocess.
    Returns the process exit code.
    """
    args: list[str] = [sys.executable, "-m", "pytest"]
    args.extend(targets)

    if verbose:
        args.append("-v")
    if not include_performance:
        args.extend(["-m", "not performance"])
    if duration:
        args.extend(["--durations=10"])
    if coverage:
        args.extend(["--cov=tbot223_core", "--cov-report=term-missing"])

    result = subprocess.run(args, cwd=str(Path(__file__).resolve().parent.parent))
    return result.returncode


def _print_coverage_report() -> None:
    """No-op: coverage report is now printed inline by pytest-cov."""
    pass


def _clean_logs() -> None:
    """Delete all log directories under TEST/SRC/logs."""
    with FileManager(is_logging_enabled=False) as fm:
        if _LOG_DIR.exists() and _LOG_DIR.is_dir():
            count = 0
            for item in _LOG_DIR.iterdir():
                fm.delete_directory(item)
                count += 1
            print(f"  Deleted {count} log directories.")
        else:
            print(f"  No log directory found at: {_LOG_DIR}")


# ============================================
# Actions
# ============================================

def action_run_all(include_performance: bool, duration: bool, coverage: bool) -> None:
    """Run all pytest tests."""
    rc = _run_pytest(
        [str(_SRC_DIR)],
        include_performance=include_performance,
        duration=duration,
        coverage=coverage,
    )
    if coverage:
        _print_coverage_report()
    print(f"\n  All tests finished (exit code: {rc}).")


def action_run_module(module_name: str, include_performance: bool, duration: bool) -> None:
    """Run tests for a single module."""
    mod = _MODULE_MAP[module_name]
    _run_pytest(
        [mod.__file__],
        include_performance=include_performance,
        duration=duration,
    )


_MENU = """
==========================================
  tbot223-core  Test Runner
==========================================
  [1] Run ALL pytest tests
  [2] Run single module tests
  [3] Run ALL + coverage report
  [4] Clean log files
  [q] Quit
=========================================="""

_MODULE_MENU = """
  Select a module:
    appcore | exception | logsys
    utils   | filemanager | result
"""


def main() -> None:
    while True:
        print(_MENU)
        choice = _prompt("  > ", ["1", "2", "3", "4", "q"])

        if choice == "q":
            print("  Bye!")
            break

        # Common options for pytest runs
        perf = False
        dur = False
        if choice in ("1", "2", "3"):
            perf = _prompt("  Include performance tests? (y/n): ", ["y", "n"]) == "y"
            dur  = _prompt("  Show slowest durations? (y/n): ", ["y", "n"]) == "y"

        if choice == "1":
            action_run_all(include_performance=perf, duration=dur, coverage=False)

        elif choice == "2":
            print(_MODULE_MENU)
            mod = _prompt("  module > ", list(_MODULE_MAP.keys()))
            action_run_module(mod, include_performance=perf, duration=dur)

        elif choice == "3":
            action_run_all(include_performance=perf, duration=dur, coverage=True)

        elif choice == "4":
            confirm = _prompt("  ** All logs will be deleted. Continue? (y/n): ", ["y", "n"])
            if confirm == "y":
                _clean_logs()

        print()  # blank line between runs


if __name__ == "__main__":
    main()
