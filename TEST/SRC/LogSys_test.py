# external Modules
import pytest
from pathlib import Path

# internal Modules
from tbot223_core.LogSys import LoggerManager, Log
from tbot223_core import LogSys

@pytest.fixture(scope="module")
def setup_module(tmp_path_factory):
    """
    Fixture to create a LoggerManager instance for testing.
    """
    tmp_path = tmp_path_factory.mktemp("test")
    return LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test_logs"), Log()

@pytest.mark.usefixtures("setup_module")
class TestLogSys:
    def test_make_logger(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "test_logger"
        log_level = "DEBUG"

        # Test creating a logger
        result = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert result.success, f"Logger creation failed: {result.error}"
        assert logger_name in logger_manager._loggers.keys(), "Logger not found in manager after creation."

        # Test creating the same logger again
        result_duplicate = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert not result_duplicate.success, "Duplicate logger creation should have failed."

    def test_get_logger(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "test_logger_get"
        log_level = "INFO"

        # Get logger ( already created )
        get_result = logger_manager.get_logger(logger_name=logger_name)
        assert not get_result.success, "Getting non-existent logger should have failed."

    def test_log_functionality(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "functional_logger"
        log_level = "INFO"

        # Create logger
        create_result = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert create_result.success, f"Logger creation failed: {create_result.error}"

        # Get logger
        get_result = logger_manager.get_logger(logger_name=logger_name)
        assert get_result.success, f"Getting logger failed: {get_result.error}"
        log.logger = get_result.data

        # Test logging
        try:
            log.log_message("INFO", "This is an info message.")
            log.log_message("WARNING", "This is a warning message.")
            log.log_message("ERROR", "This is an error message.")
        except Exception as e:
            pytest.fail(f"Logging functionality failed with exception: {e}")

@pytest.mark.usefixtures("setup_module")
class TestLogSysEdgeCases:
    def test_invalid_log_level(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "invalid_level_logger"
        invalid_log_level = "INVALID_LEVEL"

        # Test creating a logger with invalid log level
        result = logger_manager.make_logger(logger_name=logger_name, log_level=invalid_log_level)
        assert not result.success, "Logger creation with invalid log level should have failed."

    def test_log_without_logger(self, setup_module):
        """Test logging when logger is not initialized"""
        _, log = setup_module
        
        # Create a new Log instance without logger
        empty_log = Log(logger=None)
        result = empty_log.log_message("INFO", "Test message")
        assert not result.success, "Logging without logger should fail"
    
    def test_stop_stream_handlers(self, setup_module):
        """Test stopping stream handlers"""
        logger_manager, _ = setup_module
        
        logger_name = "stream_test_logger"
        logger_manager.make_logger(logger_name=logger_name, log_level="DEBUG")
        
        # Get the actual logger first
        logger = logger_manager.get_logger(logger_name).data
        
        # Stop stream handlers using the logger object
        result = logger_manager.stop_stream_handlers(logger)
        assert result.success, f"Stopping stream handlers failed: {result.error}"
    
    def test_stop_stream_handlers_nonexistent(self, setup_module):
        """Test stopping stream handlers for nonexistent logger"""
        logger_manager, _ = setup_module
        
        # Pass None which should fail
        result = logger_manager.stop_stream_handlers(None)
        assert not result.success, "Stopping handlers for None logger should fail"


@pytest.mark.usefixtures("setup_module")
class TestSimpleSetting:
    """Tests for SimpleSetting class"""
    
    def test_simple_setting_initialization(self, tmp_path):
        """Test SimpleSetting initialization"""
        setting = LogSys.SimpleSetting(
            base_dir=tmp_path / "logs",
            second_log_dir="test",
            logger_name="simple_logger"
        )
        
        logger_manager, log, logger = setting.get_instance()
        
        assert logger_manager is not None, "LoggerManager should be initialized"
        assert log is not None, "Log should be initialized"
        assert logger is not None, "Logger should be initialized"
    
    def test_simple_setting_logging(self, tmp_path):
        """Test logging with SimpleSetting"""
        setting = LogSys.SimpleSetting(
            base_dir=tmp_path / "logs",
            second_log_dir="test",
            logger_name="simple_log_test"
        )
        
        _, log, _ = setting.get_instance()
        
        result = log.log_message("INFO", "Test message from SimpleSetting")
        assert result.success, f"Logging with SimpleSetting failed: {result.error}"


class TestLogMessageEdgeCases:
    """Additional edge case tests for Log.log_message"""
    
    def test_log_message_with_integer_level(self, tmp_path):
        """Test logging with integer log level"""
        import logging
        logger_manager = LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test")
        logger_manager.make_logger("int_level_logger", log_level="DEBUG")
        logger = logger_manager.get_logger("int_level_logger").data
        log = Log(logger=logger)
        
        # Test with integer level
        result = log.log_message(logging.INFO, "Test with integer level")
        assert result.success, "Logging with integer level should succeed"
        
    def test_log_message_invalid_string_level_fallback(self, tmp_path):
        """Test that invalid string level falls back to INFO"""
        logger_manager = LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test")
        logger_manager.make_logger("fallback_logger", log_level="DEBUG")
        logger = logger_manager.get_logger("fallback_logger").data
        log = Log(logger=logger)
        
        # Invalid level should fallback to INFO
        result = log.log_message("INVALID_LEVEL", "Test with invalid level")
        assert result.success, "Logging with invalid level should succeed (fallback to INFO)"
        
    def test_log_message_lowercase_level(self, tmp_path):
        """Test logging with lowercase level string"""
        logger_manager = LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test")
        logger_manager.make_logger("lowercase_logger", log_level="DEBUG")
        logger = logger_manager.get_logger("lowercase_logger").data
        log = Log(logger=logger)
        
        # Test lowercase level
        result = log.log_message("info", "Test with lowercase level")
        assert result.success, "Logging with lowercase level should succeed"


class TestSimpleSettingEdgeCases:
    """Additional edge case tests for SimpleSetting"""
    
    def test_simple_setting_with_custom_log_level(self, tmp_path):
        """Test SimpleSetting with custom log level"""
        import logging
        setting = LogSys.SimpleSetting(
            base_dir=tmp_path / "logs",
            second_log_dir="test",
            logger_name="custom_level_logger",
            log_level=logging.DEBUG
        )
        
        logger_manager, log, logger = setting.get_instance()
        assert logger is not None, "Logger should be initialized with custom level"
        
    def test_simple_setting_path_as_string(self, tmp_path):
        """Test SimpleSetting with string paths"""
        setting = LogSys.SimpleSetting(
            base_dir=str(tmp_path / "logs"),
            second_log_dir="test",
            logger_name="string_path_logger"
        )
        
        logger_manager, log, logger = setting.get_instance()
        assert logger is not None, "Logger should be initialized with string paths"


class TestLoggerManagerEdgeCases:
    """Additional edge case tests for LoggerManager"""
    
    def test_make_logger_with_integer_level(self, tmp_path):
        """Test make_logger with integer log level"""
        import logging
        logger_manager = LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test")
        
        result = logger_manager.make_logger("int_level", log_level=logging.WARNING)
        assert result.success, "Creating logger with integer level should succeed"

    def test_make_logger_with_timestamp_keyword(self, tmp_path):
        """Test make_logger with explicit timestamp keyword."""
        import logging

        logger_manager = LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test")
        result = logger_manager.make_logger("timestamp_logger", log_level=logging.INFO, timestamp="custom_stamp")

        assert result.success, f"Creating logger with timestamp failed: {result.error}"

        logger = logger_manager.get_logger("timestamp_logger").data
        file_handler = next(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler))
        assert "custom_stamp_log" in str(file_handler.baseFilename)

    def test_make_logger_with_deprecated_time_alias(self, tmp_path):
        """Test make_logger still accepts deprecated time keyword alias."""
        import logging

        logger_manager = LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test")
        with pytest.deprecated_call():
            result = logger_manager.make_logger("legacy_time_logger", log_level=logging.INFO, time="legacy_stamp")

        assert result.success, f"Creating logger with deprecated time alias failed: {result.error}"

        logger = logger_manager.get_logger("legacy_time_logger").data
        file_handler = next(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler))
        assert "legacy_stamp_log" in str(file_handler.baseFilename)

    def test_make_logger_with_both_timestamp_and_time(self, tmp_path):
        """Test make_logger rejects both timestamp and deprecated time keyword."""
        import logging

        logger_manager = LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test")
        result = logger_manager.make_logger("both_args_logger", log_level=logging.INFO, timestamp="ts", time="legacy")
        assert not result.success, "Providing both timestamp and time should fail"
        assert "ValueError" in result.error

    def test_make_logger_with_unexpected_kwargs(self, tmp_path):
        """Test make_logger rejects unexpected keyword arguments."""
        import logging

        logger_manager = LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test")
        result = logger_manager.make_logger("unexpected_logger", log_level=logging.INFO, foo="bar")
        assert not result.success, "Unexpected kwargs should fail"
        assert "TypeError" in result.error


if __name__ == "__main__":
    pytest.main([__file__])
