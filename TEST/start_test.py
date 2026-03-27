# external Modules
import pytest
from pathlib import Path
import subprocess
import sys

# internal Modules
from SRC import AppCore_test, Exception_test, LogSys_test, Utils_test, FileManager_test, Result_test
from tbot223_core import FileManager

class Test_CoreV2:
    def a_test_AppCore(self):
        pytest.main([AppCore_test.__file__, "-m not performance"])

    def a_test_Exception(self):
        pytest.main([Exception_test.__file__])

    def a_test_LogSys(self):
        pytest.main([LogSys_test.__file__])

    def a_test_Utils(self):
        pytest.main([Utils_test.__file__])

    def a_test_FileManager(self):
        pytest.main([FileManager_test.__file__])
    
    def a_test_Result(self):
        pytest.main([Result_test.__file__])

    def run_all_tests(self, include_performance=False, duration=False):
        test_path = str(Path(__file__).resolve().parent / "SRC")
        args = [sys.executable, "-m", "pytest", test_path, "-v"] # avoid pytest invocation issues on some systems
        if not include_performance:
            args.extend(["-m", "not performance"])
        if duration:
            args.extend(["--durations=10"])
        subprocess.run(args)

if __name__ == "__main__":
    def verify_input(prompt, valid_responses):
        while True:
            response = input(prompt).strip().lower()
            if response in valid_responses:
                return response
            print(f"Invalid input. Please enter one of the following: {', '.join(valid_responses)}")

    performance_test = verify_input("Do you want to run performance tests? (y/n): ", ['y', 'n'])
    show_run_duration = verify_input("Do you want to see the test run duration? (y/n): ", ['y', 'n'])
    log_del = verify_input("Do you want to delete the log files after running the test? (**Caution** All existing logs will be deleted) (y/n): ", ['y', 'n'])
    duration = show_run_duration == 'y'
    include_performance = performance_test == 'y'
    tester = Test_CoreV2()
    tester.run_all_tests(include_performance=include_performance, duration=duration)
    if log_del == 'y':
        log_dir = Path(__file__).resolve().parent / "SRC" / "logs"
        with FileManager(is_logging_enabled=False) as FM:
            if log_dir.exists() and log_dir.is_dir():
                for item in log_dir.iterdir():
                    FM.delete_directory(item)
            else:
                print(f"No log directory found at: {log_dir}")
