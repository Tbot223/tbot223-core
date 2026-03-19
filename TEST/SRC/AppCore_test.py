# external Modules
import pytest
import random
from typing import Callable, Dict, List, Tuple, Any, Union, Optional
import subprocess
from pathlib import Path
import numpy as np

# internal Modules
from tbot223_core import AppCore
from tbot223_core.AppCore import ResultWrapper

@pytest.fixture(scope="module")
def test_appcore_initialization():
    """
    Fixture to initialize AppCore instance for testing.
    """
    test_base_dir = Path(__file__).resolve().parent
    app_core = AppCore(base_dir=test_base_dir)
    return app_core

@pytest.fixture(scope="module")
def helper_methods():
    """
    Fixture to provide helper methods for testing.
    """
    return HelperMethods()

class HelperMethods:
    @staticmethod
    def metrix_task(n: int, m: int) -> bool:
        """
        A sample task that generates an n x m matrix filled with random floats.
        Implemented with numpy for performance.
        """
        np.random.rand(n, m)
        return True
    
    def verify_results(self, results: List[Any], expected_count: int = 500) -> None:
        """
        Verify that the results list contains the expected number of successful results.
        """
        assert len(results) == expected_count
        for res in results:
            assert res.success is True
            assert res.data is True

    def dummy_task(self, x) -> str:
        """
        A simple dummy task that returns a formatted string.
        """
        return f"dummy, {x}"
    
@pytest.mark.usefixtures("test_appcore_initialization", "helper_methods")
class TestAppCore:
    def test_initialization(self, test_appcore_initialization: AppCore) -> None:
        """
        Test the initialization of the AppCore class.
        """
        assert test_appcore_initialization is not None
        assert isinstance(test_appcore_initialization, AppCore)

    def test_HelperMethods_initialization(self, helper_methods: HelperMethods) -> None:
        """
        Test the initialization of the HelperMethods class.
        """
        assert helper_methods is not None
        assert isinstance(helper_methods, HelperMethods)

    # Test Methods
    def test_thread_pool_executor(self, test_appcore_initialization: AppCore, helper_methods: HelperMethods) -> None:
        """
        Test the thread pool executor with 500 tasks.

        Each task runs the _metrix_task function with increasing n and m values.
        The results are verified to ensure all tasks completed successfully.
        """
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(50)]
        results = test_appcore_initialization.thread_pool_executor(tasks, workers=4, override=False, timeout=1)
        helper_methods.verify_results(results.data, expected_count=50)
    
    def test_process_pool_executor(self, test_appcore_initialization: AppCore, helper_methods: HelperMethods) -> None:
        """
        Test the process pool executor with 500 tasks.

        Each task runs the _metrix_task function with increasing n and m values.
        The results are verified to ensure all tasks completed successfully.
        """
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(50)]
        results = test_appcore_initialization.process_pool_executor(tasks, workers=4, override=False, timeout=5, chunk_size=10)
        helper_methods.verify_results(results.data, expected_count=50)

    def test_get_text_by_lang(self, test_appcore_initialization: AppCore) -> None:
        """
        Test the get_text_by_lang method for retrieving text based on language code.
        """
        not_supported_lang = test_appcore_initialization.get_text_by_lang("Test Key", "fr")
        assert not_supported_lang.data == "Test Value" # Default to 'en' text

        test_appcore_initialization._default_lang = "ko"
        not_supported_lang_ko = test_appcore_initialization.get_text_by_lang("Test Key", "ja")
        assert not_supported_lang_ko.data == "테스트 값" # Default to 'ko' text

        supported_lang = test_appcore_initialization.get_text_by_lang("Test Key", "en")
        assert supported_lang.data == "Test Value" # Supported 'en' text
    
    def test_ResultWrapper(self, test_appcore_initialization: AppCore, helper_methods: HelperMethods) -> None:
        """
        Test the ResultWrapper decorator for both successful and failing tasks.
        
        ResultWrapper is used to wrap functions to automatically handle exceptions
        and return a standardized result object.
        """
        @ResultWrapper()
        def successful_task(x) -> str:
            return f"successful, {x}"
        
        @ResultWrapper()
        def failing_task(x) -> str:
            raise ValueError("Intentional Failure")
        
        success_result = successful_task(10)
        assert success_result.success is True
        assert success_result.data == "successful, 10"

        fail_result = failing_task(20)
        assert fail_result.success is False

@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization", "helper_methods")
class TestAppCoreXfail:
    def _dummy_task(self, x) -> str:
        return f"dummy, {x}"
    
    def test_thread_pool_executor(self, test_appcore_initialization: AppCore):
        """
        Test various failure scenarios for the thread pool executor.
        """
        empty_tasks_result = test_appcore_initialization.thread_pool_executor([], workers=4, override=False, timeout=1)
        assert empty_tasks_result.success is False
        assert "Data must be a non-empty list" in empty_tasks_result.error

        wrong_tasks_result_func = test_appcore_initialization.thread_pool_executor([("not_a_function", {"x" : 1})], workers=4, override=True, timeout=1)
        wrong_tasks_result_kwargs = test_appcore_initialization.thread_pool_executor([(self._dummy_task, "not_a_dict")], workers=4, override=True, timeout=1)
        wrong_tasks_result_both = test_appcore_initialization.thread_pool_executor([("not_a_function", "not_a_dict")], workers=4, override=True, timeout=1)
        wrong_tasks_result_not_tuple = test_appcore_initialization.thread_pool_executor([[self._dummy_task, {"x" : 1}]], workers=4, override=True, timeout=1)
        wrong_tasks_result_one_tuple = test_appcore_initialization.thread_pool_executor([(self._dummy_task)], workers=4, override=True, timeout=1)
        for result in [wrong_tasks_result_func, wrong_tasks_result_kwargs, wrong_tasks_result_both, wrong_tasks_result_not_tuple, wrong_tasks_result_one_tuple]:
            assert result.success is False
            assert "Each item in data must be a tuple of (function, kwargs_dict)" in result.error

        wrong_workers_result = test_appcore_initialization.thread_pool_executor([(self._dummy_task, {"x" : 1})], workers=0, override=False, timeout=1)
        assert wrong_workers_result.success is False
        assert "workers must be a positive integer" in wrong_workers_result.error
        override_workers_result = test_appcore_initialization.thread_pool_executor([(self._dummy_task, {"x" : 1})]*2, workers=5, override=False, timeout=1)
        assert override_workers_result.success is False
        assert "workers 5 exceeds number of tasks 2" in override_workers_result.error

        wrong_timeout_result = test_appcore_initialization.thread_pool_executor([(self._dummy_task, {"x" : 1})], workers=4, override=True, timeout=0)
        assert wrong_timeout_result.success is False
        assert "timeout must be a positive number" in wrong_timeout_result.error

    def test_process_pool_executor(self, test_appcore_initialization: AppCore):
        """
        Test various failure scenarios for the process pool executor.
        """
        empty_tasks_result = test_appcore_initialization.process_pool_executor([], workers=4, override=False, timeout=1)
        assert empty_tasks_result.success is False
        assert "Data must be a non-empty list" in empty_tasks_result.error

        wrong_tasks_result_func = test_appcore_initialization.process_pool_executor([("not_a_function", {"x" : 1})], workers=4, override=True, timeout=1)
        wrong_tasks_result_kwargs = test_appcore_initialization.process_pool_executor([(self._dummy_task, "not_a_dict")], workers=4, override=True, timeout=1)
        wrong_tasks_result_both = test_appcore_initialization.process_pool_executor([("not_a_function", "not_a_dict")], workers=4, override=True, timeout=1)
        wrong_tasks_result_not_tuple = test_appcore_initialization.process_pool_executor([[self._dummy_task, {"x" : 1}]], workers=4, override=True, timeout=1)
        wrong_tasks_result_one_tuple = test_appcore_initialization.process_pool_executor([(self._dummy_task)], workers=4, override=True, timeout=1)
        for result in [wrong_tasks_result_func, wrong_tasks_result_kwargs, wrong_tasks_result_both, wrong_tasks_result_not_tuple, wrong_tasks_result_one_tuple]:
            assert result.success is False
            assert "Each item in data must be a tuple of (function, kwargs_dict)" in result.error

        wrong_workers_result = test_appcore_initialization.process_pool_executor([(self._dummy_task, {"x" : 1})], workers=0, override=False, timeout=1)
        assert wrong_workers_result.success is False
        assert "workers must be a positive integer" in wrong_workers_result.error
        override_workers_result = test_appcore_initialization.process_pool_executor([(self._dummy_task, {"x" : 1})]*2, workers=5, override=False, timeout=1)
        assert override_workers_result.success is False
        assert "workers 5 exceeds number of tasks 2" in override_workers_result.error

        wrong_timeout_result = test_appcore_initialization.process_pool_executor([(self._dummy_task, {"x" : 1})], workers=4, override=True, timeout=0)
        assert wrong_timeout_result.success is False
        assert "timeout must be a positive number" in wrong_timeout_result.error

        wrong_chunk_size_result = test_appcore_initialization.process_pool_executor([(self._dummy_task, {"x" : 1})], workers=4, override=True, timeout=1, chunk_size=0)
        assert wrong_chunk_size_result.success is False
        assert "chunk_size must be a positive integer" in wrong_chunk_size_result.error

@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization", "helper_methods")
class TestAppCoreEdgeCases:
    def test_process_pool_executor_no_chunk(self, test_appcore_initialization: AppCore, helper_methods: HelperMethods) -> None:
        """
        Test the process pool executor without specifying chunk size.

        Each task runs the _metrix_task function with increasing n and m values.
        The results are verified to ensure all tasks completed successfully.
        22 tasks are used to test edge case with small number of tasks.
        """
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(25)]
        results = test_appcore_initialization.process_pool_executor(tasks, workers=4, override=False, timeout=5)
        helper_methods.verify_results(results.data, expected_count=25)

    def test_get_text_by_lang_unsupported_lang(self, test_appcore_initialization: AppCore) -> None:
        """Test get_text_by_lang with unsupported language falls back to default"""
        result = test_appcore_initialization.get_text_by_lang("Test Key", "unsupported_lang")
        assert result.success, f"get_text_by_lang failed: {result.error}"
        # Should fallback to default language
    
    def test_get_text_by_lang_nonexistent_key(self, test_appcore_initialization: AppCore) -> None:
        """Test get_text_by_lang with non-existent key"""
        result = test_appcore_initialization.get_text_by_lang("NonExistentKey12345", "en")
        assert not result.success, "Non-existent key should fail"
        assert "KeyError" in result.error or "not found" in result.error, "Error should mention KeyError or not found"
    
    def test_thread_pool_with_exception_task(self, test_appcore_initialization: AppCore) -> None:
        """Test thread pool executor with task that raises exception"""
        def failing_task(x):
            raise ValueError(f"Intentional failure with {x}")
        
        tasks = [(failing_task, {"x": i}) for i in range(3)]
        results = test_appcore_initialization.thread_pool_executor(tasks, workers=2, override=True, timeout=5)
        
        assert results.success, "thread_pool_executor should succeed even with failing tasks"
        for res in results.data:
            assert not res.success, "Individual failing task should have success=False"
    
    def test_process_pool_with_exception_task(self, test_appcore_initialization: AppCore) -> None:
        """Test process pool executor with task that raises exception"""
        def failing_task(x):
            raise ValueError(f"Intentional failure with {x}")
        
        tasks = [(failing_task, {"x": i}) for i in range(3)]
        results = test_appcore_initialization.process_pool_executor(tasks, workers=2, override=True, timeout=5)
        
        assert results.success, "process_pool_executor should succeed even with failing tasks"
        for res in results.data:
            assert not res.success, "Individual failing task should have success=False"
    
    def test_thread_pool_with_override(self, test_appcore_initialization: AppCore, helper_methods: HelperMethods) -> None:
        """Test thread pool executor with override=True"""
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(5)]
        # workers > tasks but override=True so it should work
        results = test_appcore_initialization.thread_pool_executor(tasks, workers=10, override=True, timeout=5)
        assert results.success, f"thread_pool_executor with override failed: {results.error}"

    # I WILL ADD MORE EDGE CASE TESTS HERE IN THE FUTURE

@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization")
class TestCLIMethods:
    def test_clear_console(self, test_appcore_initialization: AppCore) -> None:
        """
        Test the clear_console method to ensure it executes without errors.
        """
        try:
            test_appcore_initialization.clear_console()
        except Exception as e:
            pytest.fail(f"clear_console raised an exception: {e}")

    def test_exit_application(self, test_appcore_initialization: AppCore) -> None:
        """
        Test the exit_application method to ensure it executes without errors.
        """
        with pytest.raises(SystemExit) as exc_info:
            test_appcore_initialization.exit_application(code=0)
        assert exc_info.value.code == 0

    def test_restart_application(self, test_appcore_initialization: AppCore) -> None:
        """
        Test the restart_application method to ensure it executes without errors.
        """
        test_base_dir = Path(__file__).resolve().parent
        cmd = f"from tbot223_core import AppCore; app = AppCore(is_logging_enabled=False, base_dir={str(test_base_dir)}); app.restart_application()"
        proc = subprocess.run(["python", "-c", cmd], capture_output=True)
        assert proc.returncode in [0, 1, 2]  # Environment dependent, it may return different codes

@pytest.mark.usefixtures("tmp_path", "test_appcore_initialization", "helper_methods")
class TestAppCorePerformance:
    """
    Performance tests for AppCore executor methods.
    
    WARNING: These tests involve large-scale parallel operations (2000+ tasks).
    Results may vary significantly depending on system hardware (CPU cores, memory, etc.).
    Timeouts and failures may occur on lower-spec machines or under heavy system load.
    
    These tests are excluded by default. Use `-m performance` to include them.
    """
    
    @pytest.mark.performance
    def test_thread_pool_executor_performance(self, test_appcore_initialization: AppCore, helper_methods: HelperMethods) -> None:
        """
        Performance test for the thread pool executor with 2000 tasks.
        
        Note: May timeout on systems with limited CPU/memory resources.
        """
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(2000)]
        results = test_appcore_initialization.thread_pool_executor(tasks, workers=8, override=False, timeout=5)
        helper_methods.verify_results(results.data, expected_count=2000)
    
    @pytest.mark.performance
    def test_process_pool_executor_performance(self, test_appcore_initialization: AppCore, helper_methods: HelperMethods) -> None:
        """
        Performance test for the process pool executor with 2000 tasks.
        
        Note: May timeout on systems with limited CPU/memory resources.
        Process pool has higher overhead than thread pool.
        """
        tasks = [(helper_methods.metrix_task, {"n": i+1, "m": i+1}) for i in range(2000)]
        results = test_appcore_initialization.process_pool_executor(tasks, workers=8, override=False, timeout=5, chunk_size=64)
        helper_methods.verify_results(results.data, expected_count=2000)

    @pytest.mark.performance
    def test_get_text_by_lang_performance(self, test_appcore_initialization: AppCore) -> None:
        """
        Performance test for the get_text_by_lang method with multiple language requests.
        
        Note: Executes 2000 iterations. May take longer on slower I/O systems.
        """
        for _ in range(2000):
            result = test_appcore_initialization.get_text_by_lang("Test Key", random.choice(["en", "ko", "de", "fr", "es"]))
            assert result.success is True


@pytest.mark.usefixtures("test_appcore_initialization")
class TestResultClass:
    """Tests for Result NamedTuple class"""
    
    def test_result_creation(self, test_appcore_initialization: AppCore) -> None:
        """Test basic Result creation"""
        from tbot223_core.Result import Result
        
        # Success result
        success_result = Result(True, None, None, "test_data")
        assert success_result.success is True
        assert success_result.error is None
        assert success_result.context is None
        assert success_result.data == "test_data"
    
    def test_result_failure(self, test_appcore_initialization: AppCore) -> None:
        """Test Result with failure state"""
        from tbot223_core.Result import Result
        
        # Failure result
        fail_result = Result(False, "Error message", "Error context", None)
        assert fail_result.success is False
        assert fail_result.error == "Error message"
        assert fail_result.context == "Error context"
        assert fail_result.data is None
    
    def test_result_immutability(self, test_appcore_initialization: AppCore) -> None:
        """Test Result immutability (NamedTuple)"""
        from tbot223_core.Result import Result
        
        result = Result(True, None, None, "data")
        
        # Attempt to modify should raise AttributeError
        with pytest.raises(AttributeError):
            result.success = False
    
    def test_result_unpacking(self, test_appcore_initialization: AppCore) -> None:
        """Test Result unpacking"""
        from tbot223_core.Result import Result
        
        result = Result(True, "err", "ctx", [1, 2, 3])
        success, error, context, data = result
        
        assert success is True
        assert error == "err"
        assert context == "ctx"
        assert data == [1, 2, 3]
    
    def test_result_with_complex_data(self, test_appcore_initialization: AppCore) -> None:
        """Test Result with complex data types"""
        from tbot223_core.Result import Result
        
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2),
            "none": None
        }
        result = Result(True, None, None, complex_data)
        
        assert result.data["list"] == [1, 2, 3]
        assert result.data["dict"]["nested"] == "value"


@pytest.mark.usefixtures("test_appcore_initialization")
class TestResultWrapper:
    """Tests for ResultWrapper decorator class"""
    
    def test_result_wrapper_success(self, test_appcore_initialization: AppCore) -> None:
        """Test ResultWrapper with successful function"""
        @ResultWrapper()
        def add_numbers(a, b):
            return a + b
        
        result = add_numbers(5, 10)
        assert result.success is True
        assert result.data == 15
    
    def test_result_wrapper_exception(self, test_appcore_initialization: AppCore) -> None:
        """Test ResultWrapper with function that raises exception"""
        @ResultWrapper()
        def divide(a, b):
            return a / b
        
        result = divide(10, 0)
        assert result.success is False
        assert "ZeroDivisionError" in result.data["error"]["type"]
    
    def test_result_wrapper_returns_result(self, test_appcore_initialization: AppCore) -> None:
        """Test ResultWrapper with function that already returns Result"""
        from tbot223_core.Result import Result
        
        @ResultWrapper()
        def returns_result():
            return Result(True, None, "context", "already_result")
        
        result = returns_result()
        assert result.success is True
        assert result.data == "already_result"
        assert result.context == "context"
    
    def test_result_wrapper_with_kwargs(self, test_appcore_initialization: AppCore) -> None:
        """Test ResultWrapper with kwargs"""
        @ResultWrapper()
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        result = greet("World", greeting="Hi")
        assert result.success is True
        assert result.data == "Hi, World!"


class TestSafeCLIInput:
    """Test cases for safe_CLI_input method"""
    
    def test_safe_cli_input_basic_string(self, test_appcore_initialization: AppCore) -> None:
        """Test basic string input"""
        from unittest.mock import patch
        
        with patch('builtins.input', return_value='hello'):
            result = test_appcore_initialization.safe_CLI_input(prompt="Enter text: ")
            assert result.success is True
            assert result.data == 'hello'
    
    def test_safe_cli_input_integer_conversion(self, test_appcore_initialization: AppCore) -> None:
        """Test input with integer type conversion"""
        from unittest.mock import patch
        
        with patch('builtins.input', return_value='42'):
            result = test_appcore_initialization.safe_CLI_input(prompt="Enter number: ", input_type=int)
            assert result.success is True
            assert result.data == 42
            assert isinstance(result.data, int)
    
    def test_safe_cli_input_float_conversion(self, test_appcore_initialization: AppCore) -> None:
        """Test input with float type conversion"""
        from unittest.mock import patch
        
        with patch('builtins.input', return_value='3.14'):
            result = test_appcore_initialization.safe_CLI_input(prompt="Enter float: ", input_type=float)
            assert result.success is True
            assert abs(result.data - 3.14) < 0.001
    
    def test_safe_cli_input_valid_options(self, test_appcore_initialization: AppCore) -> None:
        """Test input with valid options validation"""
        from unittest.mock import patch
        
        with patch('builtins.input', return_value='yes'):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter choice: ",
                valid_options=['yes', 'no']
            )
            assert result.success is True
            assert result.data == 'yes'
    
    def test_safe_cli_input_valid_options_case_insensitive(self, test_appcore_initialization: AppCore) -> None:
        """Test input with valid options - case insensitive"""
        from unittest.mock import patch
        
        with patch('builtins.input', return_value='YES'):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter choice: ",
                valid_options=['yes', 'no'],
                case_sensitive=False
            )
            assert result.success is True
            assert result.data == 'YES'
    
    def test_safe_cli_input_valid_options_case_sensitive(self, test_appcore_initialization: AppCore) -> None:
        """Test input with valid options - case sensitive rejection then valid"""
        from unittest.mock import patch
        
        # First input is 'YES' (wrong case), second is 'yes' (correct)
        with patch('builtins.input', side_effect=['YES', 'yes']):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter choice: ",
                valid_options=['yes', 'no'],
                case_sensitive=True
            )
            assert result.success is True
            assert result.data == 'yes'
    
    def test_safe_cli_input_invalid_type_conversion_retry(self, test_appcore_initialization: AppCore) -> None:
        """Test retry on invalid type conversion"""
        from unittest.mock import patch
        
        # First input fails conversion, second succeeds
        with patch('builtins.input', side_effect=['not_a_number', '123']):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter number: ",
                input_type=int
            )
            assert result.success is True
            assert result.data == 123
    
    def test_safe_cli_input_max_retries_exceeded(self, test_appcore_initialization: AppCore) -> None:
        """Test max retries exceeded returns failure"""
        from unittest.mock import patch
        
        with patch('builtins.input', return_value='invalid'):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter choice: ",
                valid_options=['yes', 'no'],
                max_retries=3
            )
            assert result.success is False
            assert "Maximum retry attempts" in result.error
    
    def test_safe_cli_input_empty_not_allowed(self, test_appcore_initialization: AppCore) -> None:
        """Test empty input rejected when not allowed"""
        from unittest.mock import patch
        
        with patch('builtins.input', side_effect=['', 'valid']):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter text: ",
                allow_empty=False
            )
            assert result.success is True
            assert result.data == 'valid'
    
    def test_safe_cli_input_empty_allowed(self, test_appcore_initialization: AppCore) -> None:
        """Test empty input accepted when allowed"""
        from unittest.mock import patch
        
        with patch('builtins.input', return_value=''):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter text: ",
                allow_empty=True
            )
            assert result.success is True
            assert result.data == ''
    
    def test_safe_cli_input_invalid_max_retries(self, test_appcore_initialization: AppCore) -> None:
        """Test invalid max_retries parameter raises error"""
        result = test_appcore_initialization.safe_CLI_input(
            prompt="Enter text: ",
            max_retries=0
        )
        assert result.success is False
        assert "max_retries must be a positive integer" in str(result.data)
    
    def test_safe_cli_input_invalid_max_retries_negative(self, test_appcore_initialization: AppCore) -> None:
        """Test negative max_retries parameter raises error"""
        result = test_appcore_initialization.safe_CLI_input(
            prompt="Enter text: ",
            max_retries=-5
        )
        assert result.success is False
        assert "max_retries must be a positive integer" in str(result.data)
    
    def test_safe_cli_input_unsupported_type_without_other_type(self, test_appcore_initialization: AppCore) -> None:
        """Test unsupported input_type without other_type flag"""
        result = test_appcore_initialization.safe_CLI_input(
            prompt="Enter text: ",
            input_type=list,
            other_type=False
        )
        assert result.success is False
        assert "input_type must be one of" in str(result.data)
    
    def test_safe_cli_input_custom_type_with_other_type(self, test_appcore_initialization: AppCore) -> None:
        """Test custom input_type with other_type flag enabled"""
        from unittest.mock import patch
        
        # Using a custom callable that converts string to list of chars
        def to_char_list(s):
            return list(s)
        
        with patch('builtins.input', return_value='abc'):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter text: ",
                input_type=to_char_list,
                other_type=True
            )
            assert result.success is True
            assert result.data == ['a', 'b', 'c']
    
    def test_safe_cli_input_bool_conversion(self, test_appcore_initialization: AppCore) -> None:
        """Test bool type conversion (note: bool('False') is True in Python)"""
        from unittest.mock import patch
        
        with patch('builtins.input', return_value='True'):
            result = test_appcore_initialization.safe_CLI_input(
                prompt="Enter bool: ",
                input_type=bool
            )
            assert result.success is True
            # Python's bool('True') is True, bool('') is False
            assert result.data is True


@pytest.mark.usefixtures("test_appcore_initialization")
class TestResultWrapperMetadata:
    """Tests for ResultWrapper preserving function metadata via functools.wraps"""

    def test_result_wrapper_preserves_name(self, test_appcore_initialization: AppCore) -> None:
        """Test ResultWrapper preserves __name__"""
        @ResultWrapper()
        def my_special_function(x):
            return x * 2

        assert my_special_function.__name__ == "my_special_function"

    def test_result_wrapper_preserves_docstring(self, test_appcore_initialization: AppCore) -> None:
        """Test ResultWrapper preserves __doc__"""
        @ResultWrapper()
        def documented_function(x):
            """This is the docstring."""
            return x

        assert documented_function.__doc__ == "This is the docstring."


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m not performance"])