# external Modules
import pytest

# internal Modules
from tbot223_core import Exception

@pytest.fixture(scope="module")
def tracker():
    """
    Fixture to create an ExceptionTracker instance for testing.
    """
    return Exception.ExceptionTracker()

@pytest.mark.usefixtures("tracker")
class TestExceptionTracker:
    def zero_division(self) -> None:
        """
        A method that raises a ZeroDivisionError for testing.
        """
        return 1 / 0
    
    def test_get_exception_location(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_location method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_location(error)
        assert result.success is True
        assert "line" in result.data
        assert "in" in result.data

    def test_get_exception_info(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_info method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_info(error, params=((), {}), mask_tuple=(False, False, False, False))
        assert result.success is True
        assert result.data["error"]["type"] == "ZeroDivisionError"

    def test_get_exception_return(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_return method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_return(error, params=((), {}), mask_tuple=(False, False, False, False))
        assert result.success is False
        assert result.data["error"]["type"] == "ZeroDivisionError"

    def test_system_info_initialization(self) -> None:
        """
        Test that the system info is initialized correctly in ExceptionTracker.
        """
        tracker = Exception.ExceptionTracker()
        assert isinstance(tracker._system_info, dict)
        assert "OS" in tracker._system_info
        assert "Python_Version" in tracker._system_info

    @Exception.ExceptionTrackerDecorator(mask_tuple=(False, False, False, False), tracker=Exception.ExceptionTracker())
    def dummy_method(self, x: int) -> float:
        """
        A dummy method to test the ExceptionTrackerDecorator.
        """
        return 10 / x

    def test_exception_tracker_decorator(self) -> None:
        """
        Test the ExceptionTrackerDecorator.
        """
        result = self.dummy_method(0)
        
        assert result.success is False
        assert "ZeroDivisionError" in result.error
    
    def test_get_exception_info_with_params(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test get_exception_info with user_input and params
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()
        
        error = exc_info.value
        result = tracker.get_exception_info(
            error, 
            user_input="test_input", 
            params=((1, 2), {"key": "value"}),
            mask_tuple=(False, False, False, False)
        )
        
        assert result.success is True
        assert result.data["input_context"]["user_input"] == "test_input"
        assert result.data["input_context"]["params"]["args"] == (1, 2)
        assert result.data["input_context"]["params"]["kwargs"] == {"key": "value"}
    
    def test_get_exception_return_with_params(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test get_exception_return with params
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()
        
        error = exc_info.value
        result = tracker.get_exception_return(
            error,
            params=((10,), {"divisor": 0})
        )
        
        assert result.success is False
        assert "ZeroDivisionError" in result.error
    
    @Exception.ExceptionTrackerDecorator(mask_tuple=(True, True, True, True), tracker=Exception.ExceptionTracker())
    def dummy_method_masked(self, x: int) -> float:
        """
        A dummy method to test the ExceptionTrackerDecorator with masking.
        """
        return 10 / x
    
    def test_exception_tracker_decorator_with_masking(self) -> None:
        """
        Test the ExceptionTrackerDecorator with masking enabled.
        """
        result = self.dummy_method_masked(0)
        
        assert result.success is False
        # When mask_tuple=(True, True, True, True), all fields in data dict are masked
        assert result.data["computer_info"] == "<Masked>"
        assert result.data["input_context"]["user_input"] == "<Masked>"
    
    @Exception.ExceptionTrackerDecorator(mask_tuple=(False, False, False, False), tracker=Exception.ExceptionTracker())
    def successful_method(self, x: int) -> int:
        """
        A method that succeeds for testing decorator.
        """
        return x * 2
    
    def test_exception_tracker_decorator_success(self) -> None:
        """
        Test that ExceptionTrackerDecorator returns normal value on success.
        """
        result = self.successful_method(5)
        
        assert result == 10  # Normal return value, not wrapped


@pytest.mark.usefixtures("tracker")
class TestExceptionEdgeCases:
    """Edge case tests for Exception module"""
    
    def test_exception_with_none_traceback(self, tracker: Exception.ExceptionTracker) -> None:
        """Test handling exception with no traceback"""
        error = ValueError("Test error without traceback")
        # Manually set traceback to None
        error.__traceback__ = None
        
        # Should handle gracefully - may return failure but should not crash
        result = tracker.get_exception_location(error)
        # The result should indicate failure since there's no traceback to extract
        assert result.success is False
    
    def test_exception_info_all_system_fields(self, tracker: Exception.ExceptionTracker) -> None:
        """Test that all system info fields are present"""
        expected_fields = [
            "OS", "OS_version", "Release", "Architecture", 
            "Processor", "Python_Version", "Python_Executable", 
            "Current_Working_Directory"
        ]
        
        for field in expected_fields:
            assert field in tracker._system_info, f"Missing field: {field}"
    
    def test_exception_info_timestamp_format(self, tracker: Exception.ExceptionTracker) -> None:
        """Test that timestamp is in correct format"""
        error = None
        try:
            1 / 0
        except ZeroDivisionError as e:
            error = e
        
        result = tracker.get_exception_info(error, params=((), {}), mask_tuple=(False, False, False, False))
        timestamp = result.data["timestamp"]
        # Should be in YYYY-MM-DD HH:MM:SS format
        assert len(timestamp) == 19
        assert timestamp[4] == "-" and timestamp[7] == "-"
        assert timestamp[10] == " "
        assert timestamp[13] == ":" and timestamp[16] == ":"


@pytest.mark.usefixtures("tracker")
class TestGetErrorCode:
    """Tests for get_error_code method"""
    
    def test_get_error_code_success(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_error_code with valid error_id_map"""
        error_id_map = {
            "ZeroDivisionError": 1001,
            "ValueError": 1002,
            "TypeError": 1003
        }
        
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_error_code(error_id_map, e)
            assert result.success is True
            assert result.data == 1001
    
    def test_get_error_code_value_error(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_error_code with ValueError"""
        error_id_map = {
            "ZeroDivisionError": 1001,
            "ValueError": 1002,
            "TypeError": 1003
        }
        
        try:
            int("not a number")
        except ValueError as e:
            result = tracker.get_error_code(error_id_map, e)
            assert result.success is True
            assert result.data == 1002
    
    def test_get_error_code_not_found(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_error_code when error type not in map"""
        error_id_map = {
            "ValueError": 1002,
            "TypeError": 1003
        }
        
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_error_code(error_id_map, e)
            assert result.success is False
            assert "not found" in result.error.lower() or "keyerror" in result.error.lower()
    
    def test_get_error_code_string_codes(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_error_code with string error codes"""
        error_id_map = {
            "ZeroDivisionError": "ERR_DIVISION",
            "ValueError": "ERR_VALUE"
        }
        
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_error_code(error_id_map, e)
            assert result.success is True
            assert result.data == "ERR_DIVISION"
    
    def test_get_error_code_empty_map(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_error_code with empty error_id_map"""
        error_id_map = {}
        
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_error_code(error_id_map, e)
            assert result.success is False


@pytest.mark.usefixtures("tracker")
class TestExceptionMasking:
    """Tests for masking functionality in Exception module"""
    
    def test_mask_user_input_only(self, tracker: Exception.ExceptionTracker) -> None:
        """Test masking only user_input"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(
                e, 
                user_input="sensitive_data", 
                params=((), {}),
                mask_tuple=(True, False, False, False)
            )
            assert result.success is True
            assert result.data["input_context"]["user_input"] == "<Masked>"
            assert result.data["computer_info"] != "<Masked>"
    
    def test_mask_params_only(self, tracker: Exception.ExceptionTracker) -> None:
        """Test masking only params"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(
                e, 
                user_input="visible_data", 
                params=((1, 2), {"key": "value"}),
                mask_tuple=(False, True, False, False)
            )
            assert result.success is True
            assert result.data["input_context"]["user_input"] == "visible_data"
            assert result.data["input_context"]["params"] == "<Masked>"
    
    def test_mask_traceback_only(self, tracker: Exception.ExceptionTracker) -> None:
        """Test masking only traceback"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(
                e, 
                user_input="data", 
                params=((), {}),
                mask_tuple=(False, False, True, False)
            )
            assert result.success is True
            assert result.data["traceback"] == "<Masked>"
    
    def test_mask_all_fields(self, tracker: Exception.ExceptionTracker) -> None:
        """Test masking all maskable fields"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(
                e, 
                user_input="data", 
                params=((1,), {"k": "v"}),
                mask_tuple=(True, True, True, True)
            )
            assert result.success is True
            assert result.data["input_context"]["user_input"] == "<Masked>"
            assert result.data["input_context"]["params"] == "<Masked>"
            assert result.data["traceback"] == "<Masked>"
            assert result.data["computer_info"] == "<Masked>"
    
    def test_invalid_mask_tuple_length(self, tracker: Exception.ExceptionTracker) -> None:
        """Test with invalid mask_tuple length"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(
                e, 
                user_input="data", 
                params=((), {}),
                mask_tuple=(True, False)  # Wrong length, should be 4
            )
            assert result.success is False
    
    def test_invalid_mask_tuple_types(self, tracker: Exception.ExceptionTracker) -> None:
        """Test with invalid mask_tuple types"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(
                e, 
                user_input="data", 
                params=((), {}),
                mask_tuple=(1, 0, 1, 0)  # integers instead of booleans
            )
            assert result.success is False


@pytest.mark.usefixtures("tracker")
class TestExceptionInfoStructure:
    """Tests for exception info data structure"""
    
    def test_exception_info_has_all_required_fields(self, tracker: Exception.ExceptionTracker) -> None:
        """Test that exception info contains all required fields"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(e, params=((), {}), mask_tuple=(False, False, False, False))
            data = result.data
            
            required_fields = ["success", "error", "location", "origin_location", 
                             "timestamp", "input_context", "traceback", "computer_info"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
    
    def test_exception_info_error_structure(self, tracker: Exception.ExceptionTracker) -> None:
        """Test error field structure"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(e, params=((), {}), mask_tuple=(False, False, False, False))
            error = result.data["error"]
            
            assert "type" in error
            assert "message" in error
            assert error["type"] == "ZeroDivisionError"
    
    def test_exception_info_location_structure(self, tracker: Exception.ExceptionTracker) -> None:
        """Test location field structure"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(e, params=((), {}), mask_tuple=(False, False, False, False))
            location = result.data["location"]
            
            assert "file" in location
            assert "line" in location
            assert "function" in location
            assert isinstance(location["line"], int)


@pytest.mark.usefixtures("tracker")
class TestExceptionParamsValidation:
    """Tests for improved params validation in get_exception_info"""

    def test_get_exception_info_none_params(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_exception_info rejects None params"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(e, params=None, mask_tuple=(False, False, False, False))
            assert result.success is False

    def test_get_exception_info_invalid_params_not_tuple(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_exception_info rejects non-tuple params"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(e, params=[(), {}], mask_tuple=(False, False, False, False))
            assert result.success is False

    def test_get_exception_info_invalid_params_wrong_length(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_exception_info rejects tuple with wrong length"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_info(e, params=((),), mask_tuple=(False, False, False, False))
            assert result.success is False

    def test_get_exception_return_none_params(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_exception_return with None params uses default empty params"""
        try:
            1 / 0
        except ZeroDivisionError as e:
            result = tracker.get_exception_return(e, params=None, mask_tuple=(False, False, False, False))
            # params=None is passed to get_exception_info which rejects it, 
            # so data will be a traceback string instead of error_info dict
            assert result.success is False
            assert isinstance(result.data, str), "data should be a traceback string when params validation fails in get_exception_info"


@pytest.mark.usefixtures("tracker")
class TestExceptionDecoratorMetadata:
    """Tests for ExceptionTrackerDecorator preserving function metadata via functools.wraps"""

    @Exception.ExceptionTrackerDecorator(mask_tuple=(False, False, False, False))
    def named_decorated_function(self, x: int) -> int:
        """Docstring for named function."""
        return x + 1

    def test_decorator_preserves_name(self) -> None:
        """Test ExceptionTrackerDecorator preserves __name__"""
        assert self.named_decorated_function.__name__ == "named_decorated_function"

    def test_decorator_preserves_docstring(self) -> None:
        """Test ExceptionTrackerDecorator preserves __doc__"""
        assert self.named_decorated_function.__doc__ == "Docstring for named function."


@pytest.mark.usefixtures("tracker")
class TestExceptionInfoNoneError:
    """Tests for get_exception_info when error argument is None"""

    def test_get_exception_info_none_error(self, tracker: Exception.ExceptionTracker) -> None:
        """Test get_exception_info rejects None as error"""
        result = tracker.get_exception_info(error=None, params=((), {}), mask_tuple=(False, False, False, False))
        assert result.success is False
        assert "ValueError" in result.error


if __name__ == "__main__":
    pytest.main([__file__])