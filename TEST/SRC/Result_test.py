# external Modules
import pytest

# internal Modules
from tbot223_core import Result
from tbot223_core.Result import ResultUnwrapException


class TestResult:
    """Test class for Result NamedTuple and its methods."""

    def test_result_creation_success(self):
        """Test creating a successful Result."""
        result = Result(success=True, error=None, context="TestContext", data={"key": "value"})
        assert result.success is True
        assert result.error is None
        assert result.context == "TestContext"
        assert result.data == {"key": "value"}

    def test_result_creation_failure(self):
        """Test creating a failed Result."""
        result = Result(success=False, error="Some error", context="FailContext", data=None)
        assert result.success is False
        assert result.error == "Some error"
        assert result.context == "FailContext"
        assert result.data is None

    def test_result_creation_cancelled(self):
        """Test creating a cancelled/not executed Result (success=None)."""
        result = Result(success=None, error=None, context="CancelledContext", data=None)
        assert result.success is None
        assert result.error is None
        assert result.context == "CancelledContext"

    # unwrap() tests
    def test_unwrap_success(self):
        """Test unwrap returns data on success."""
        result = Result(success=True, error=None, context="TestContext", data={"key": "value"})
        data = result.unwrap()
        assert data == {"key": "value"}

    def test_unwrap_failure_raises(self):
        """Test unwrap raises ResultUnwrapException on failure."""
        result = Result(success=False, error="Test error", context="FailContext", data={"error_details": "info"})
        with pytest.raises(ResultUnwrapException) as exc_info:
            result.unwrap()
        assert exc_info.value.error == "Test error"
        assert exc_info.value.context == "FailContext"
        assert exc_info.value.data == {"error_details": "info"}

    def test_unwrap_cancelled_raises(self):
        """Test unwrap raises ResultUnwrapException when cancelled (success=None)."""
        result = Result(success=None, error=None, context="CancelledContext", data=None)
        with pytest.raises(ResultUnwrapException) as exc_info:
            result.unwrap()
        assert "cancelled" in str(exc_info.value).lower() or "not executed" in str(exc_info.value).lower()

    # expect() tests
    def test_expect_success(self):
        """Test expect returns data on success."""
        result = Result(success=True, error=None, context="TestContext", data=[1, 2, 3])
        data = result.expect()
        assert data == [1, 2, 3]

    def test_expect_failure_raises(self):
        """Test expect raises ResultUnwrapException on failure."""
        result = Result(success=False, error="Expect error", context="ExpectContext", data=None)
        with pytest.raises(ResultUnwrapException) as exc_info:
            result.expect()
        assert exc_info.value.error == "Expect error"

    def test_expect_cancelled_raises(self):
        """Test expect raises ResultUnwrapException when cancelled."""
        result = Result(success=None, error=None, context="CancelledContext", data=None)
        with pytest.raises(ResultUnwrapException) as exc_info:
            result.expect()
        assert "cancelled" in str(exc_info.value).lower() or "not executed" in str(exc_info.value).lower()

    def test_expect_custom_message_overrides_error(self):
        """Test expect uses custom message when provided."""
        result = Result(success=False, error="Original error", context="ExpectContext", data=None)
        with pytest.raises(ResultUnwrapException) as exc_info:
            result.expect("Custom failure message")
        assert exc_info.value.error == "Custom failure message"

    # unwrap_or() tests
    def test_unwrap_or_success(self):
        """Test unwrap_or returns data on success."""
        result = Result(success=True, error=None, context="TestContext", data="success_data")
        data = result.unwrap_or("default")
        assert data == "success_data"

    def test_unwrap_or_failure_returns_default(self):
        """Test unwrap_or returns default on failure."""
        result = Result(success=False, error="Some error", context="FailContext", data=None)
        data = result.unwrap_or("default_value")
        assert data == "default_value"

    def test_unwrap_or_cancelled_returns_default(self):
        """Test unwrap_or returns default when cancelled (success=None)."""
        result = Result(success=None, error=None, context="CancelledContext", data=None)
        data = result.unwrap_or({"fallback": True})
        assert data == {"fallback": True}

    # ResultUnwrapException tests
    def test_result_unwrap_exception_message(self):
        """Test ResultUnwrapException formats message correctly."""
        exc = ResultUnwrapException("Test Error", "TestContext", {"data": "value"})
        assert "Test Error" in str(exc)
        assert "TestContext" in str(exc)
        assert str({"data": "value"}) in str(exc)

    def test_result_unwrap_exception_attributes(self):
        """Test ResultUnwrapException stores attributes correctly."""
        exc = ResultUnwrapException("Error msg", "Context msg", [1, 2, 3])
        assert exc.error == "Error msg"
        assert exc.context == "Context msg"
        assert exc.data == [1, 2, 3]

    # Edge cases
    def test_unwrap_with_none_data_success(self):
        """Test unwrap returns None when data is None but success is True."""
        result = Result(success=True, error=None, context="NoneDataContext", data=None)
        data = result.unwrap()
        assert data is None

    def test_unwrap_or_with_none_default(self):
        """Test unwrap_or with None as default value."""
        result = Result(success=False, error="Error", context="Context", data="ignored")
        data = result.unwrap_or(None)
        assert data is None

    def test_result_immutability(self):
        """Test that Result is immutable (NamedTuple)."""
        result = Result(success=True, error=None, context="Immutable", data="data")
        with pytest.raises(AttributeError):
            result.success = False

    def test_result_as_tuple(self):
        """Test Result can be unpacked like a tuple."""
        result = Result(success=True, error="err", context="ctx", data="val")
        success, error, context, data = result
        assert success is True
        assert error == "err"
        assert context == "ctx"
        assert data == "val"
