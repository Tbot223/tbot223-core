# external Modules
from typing import Optional, Union, Any
from pathlib import Path
import logging

# internal Modules
from tbot223_core.Exception import ExceptionTracker
from tbot223_core.LogSys import SimpleSetting

class DefaultInit:
    """
    A class designed to provide a standardized way to initialize instances with logging and exception tracking capabilities.

    Use this class to easily add logging and exception tracking to any instance by simply calling it with the appropriate parameters.

    This class only provides the `run` method, which is a static method that can be called without creating an instance of `DefaultInit`.
    So, DO NOT create an instance of `DefaultInit` to use it. Instead, call the `run` method directly on the class, passing the target instance and the necessary parameters.

    Example:
        >>> # Correct usage
        >>> DefaultInit.run(target_instance=my_instance, 
                            is_logging_enabled=True, 
                            is_debug_enabled=False, 
                            base_dir="./logs", 
                            second_log_dir="./backup_logs", 
                            logger_name="my_logger", 
                            log_level=logging.INFO)
        >>> # This will initialize `my_instance` with logging enabled, using the specified directories and logger name, and set up exception tracking.
        >>> # Incorrect usage (DO NOT create an instance of DefaultInit)
        >>> default_init = DefaultInit()  # This is not necessary and not recommended
        >>> default_init.run(target_instance=my_instance,
                            is_logging_enabled=True, 
                            is_debug_enabled=False, 
                            base_dir="./logs", 
                            second_log_dir="./backup_logs", 
                            logger_name="my_logger", 
                            log_level=logging.INFO)
        >>> # This works, but is discouraged. Always call `run` directly on the class.
    """
    @staticmethod
    def run(target_instance: Any,
            is_logging_enabled: bool, is_debug_enabled: bool,
            base_dir: Optional[Union[str, Path]] = None, second_log_dir: Optional[str] = None, logger_name: Optional[str] = None, log_level: Union[int, str] = logging.INFO,
            
            ExceptionTracker=ExceptionTracker, SimpleSetting=SimpleSetting
            ) -> None:
        """
        A callable class that initializes a target instance with logging and exception tracking capabilities.
        When called, it sets up the target instance with an ExceptionTracker and logging utilities based on the provided parameters.

        - **(R) = Required argument**
        - **(O) = Optional argument (has a default value)**
        - **(D) = Dependency Injection (advanced usage)**

        Args:
            (R)`target_instance`: The instance to be initialized with logging and exception tracking.
            (R)`is_logging_enabled` (bool): Flag to enable or disable logging. 
            (R)`is_debug_enabled` (bool): Flag to enable or disable debug mode.
            (O)`base_dir` (str): Base directory for log files.
            (O)`second_log_dir` (str): Secondary directory for log files.
            (O)`logger_name` (str): Name of the logger to be used.
            (O)`log_level` (int): Logging level (e.g., `logging.INFO`, `logging.DEBUG`). When `is_debug_enabled=True`, `log_level` must allow DEBUG-level logging (i.e., DEBUG or more verbose).
                - If `log_level` is set to `"AUTO"`, it will automatically be set to `logging.DEBUG` if `is_debug_enabled` is True, otherwise it will be set to `logging.INFO`.

            (D)`ExceptionTracker`: The ExceptionTracker class to be used for tracking exceptions.
            (D)`SimpleSetting`: The SimpleSetting class to be used for configuring logging settings.

        Note:
            - if `is_logging_enabled` is set to True, base_dir, second_log_dir, logger_name, and log_level must be provided.
            - if `is_logging_enabled` is False, logging will be disabled regardless of the values of base_dir, second_log_dir, logger_name, and log_level.
            - if `is_debug_enabled` is set to True, logging must be enabled, and log_level must be set to logging.DEBUG or lower.
            - This class is designed to be flexible and can be used in various contexts where logging and exception tracking are needed. 

        Initialized Attributes on `target_instance`:
            target_instance will be initialized with the following attributes:
            - `_is_logging_enabled` (bool): Indicates whether logging is enabled.
            - `_is_debug_enabled` (bool): Indicates whether debug mode is enabled.
            - `_logger_manager` (LoggerManager or None): The LoggerManager instance if logging is enabled, otherwise None.
            - `log` (Log or None): The Log instance if logging is enabled, otherwise None.
            - `logger` (Logger or None): The Logger instance if logging is enabled, otherwise None.
            - `_log` (callable or None): A method for logging messages if logging is enabled, otherwise None.
        
        Example:
            >>> # Normal usage
            >>> DefaultInit.run(target_instance=my_instance, 
                            is_logging_enabled=True, 
                            is_debug_enabled=False, 
                            base_dir="./logs", 
                            second_log_dir="./backup_logs", 
                            logger_name="my_logger", 
                            log_level=logging.INFO)
            >>> # This will initialize `my_instance` with logging enabled, using the specified directories and logger name, and set up exception tracking.
        """
        # Validate parameters based on the logging and debug settings
        required_params = {
            "base_dir": base_dir,
            "second_log_dir": second_log_dir,
            "logger_name": logger_name
        }
        if is_logging_enabled or is_debug_enabled:
            missing_params = [name for name, value in required_params.items() if value is None]
            if missing_params:
                raise ValueError(f"base_dir, second_log_dir, and logger_name must be provided when logging or debug mode is enabled. Missing: {', '.join(missing_params)}")
        # Determine log level based on debug mode if set to AUTO
        if log_level == "AUTO":
            log_level = logging.DEBUG if is_debug_enabled else logging.INFO
        # Additional validation for debug mode
        if is_debug_enabled and not is_logging_enabled:
            raise ValueError("Debug mode cannot be enabled without logging enabled.")
        # Additional validation for log level when debug mode is enabled
        if is_debug_enabled and log_level > logging.DEBUG:
            raise ValueError("Log level must be set to DEBUG or lower when debug mode is enabled.")
        
        # Initialize the exception tracker for the target instance
        target_instance._exception_tracker = ExceptionTracker() 

        # Set logging and debug flags on the target instance
        target_instance._is_logging_enabled = is_logging_enabled
        target_instance._is_debug_enabled = is_debug_enabled

        # Initialize logging if enabled, otherwise set logging attributes to None
        tmp = SimpleSetting(base_dir, second_log_dir, logger_name, log_level).get_instance() if is_logging_enabled or is_debug_enabled else (None, None, None) 
        target_instance._logger_manager = tmp[0]
        target_instance.log = tmp[1]
        target_instance.logger = tmp[2]

        # Set the _log method on the target instance
        target_instance._log = lambda level, message: target_instance.log.log_message(level, message) if target_instance._is_logging_enabled else lambda *args, **kwargs: None